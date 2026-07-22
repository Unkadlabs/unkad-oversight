"""Regenerate every number in RESULTS.md from the transcripts.

The transcripts are the authority. results.tsv is a convenience file written by
the run script, and in this experiment that script's YES-rate extractor silently
recorded nothing for the whole run, so a reader trusting it alone would have read
accuracy as the YES rate. This module exists so that never decides anything.

    python -m collapse.analyse                 # reads logs/
    python -m collapse.analyse --logs dir/

Cells are identified by the judge model and task recorded inside each log, not by
filename, and a duplicate cell is a hard error rather than a silent choice.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from inspect_ai.log import read_eval_log

JUDGES = ["ollama/qwen2.5:7b", "ollama/qwen2.5:3b"]
FACTORIAL = ["cipher_neutral", "cipher_warned", "absent_neutral", "absent_warned"]
ANCHORS = ["e1_obscured", "e1_none"]
N_EXPECTED = 300

# Experiment 1's published YES rates, for the anchor comparison.
E1_PUBLISHED = {"e1_obscured": 0.063, "e1_none": 0.193}


def normal_p(z: float) -> float:
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


class Cell:
    def __init__(self, samples):
        self.n = len(samples)
        self.yes = 0
        self.unparsed = 0
        self.correct = 0
        self.by_label = {"YES": [0, 0], "NO": [0, 0]}
        for s in samples:
            truth = s.target if isinstance(s.target, str) else s.target[0]
            answer = getattr(next(iter((s.scores or {}).values()), None), "answer", None)
            if answer == "YES":
                self.yes += 1
            elif answer != "NO":
                self.unparsed += 1
            self.correct += answer == truth
            bucket = self.by_label[truth]
            bucket[1] += 1
            bucket[0] += answer == truth

    @property
    def yes_rate(self) -> float:
        return self.yes / self.n

    @property
    def yes_se(self) -> float:
        p = self.yes_rate
        return math.sqrt(p * (1 - p) / self.n)

    @property
    def accuracy(self) -> float:
        return self.correct / self.n

    @property
    def balanced(self) -> float:
        return sum(c / n for c, n in self.by_label.values() if n) / 2

    @property
    def unparsed_rate(self) -> float:
        return self.unparsed / self.n

    @property
    def true_yes_rate(self) -> float:
        return self.by_label["YES"][1] / self.n


def load(directory: Path) -> dict:
    cells: dict = {}
    for path in sorted(directory.glob("*.eval")):
        try:
            log = read_eval_log(str(path))
        except Exception as exc:
            raise SystemExit(f"unreadable log {path.name}: {exc}")
        samples = log.samples or []
        if len(samples) != N_EXPECTED:
            # A partial log is what a killed or interrupted run leaves behind.
            # Refusing rather than filtering means nobody analyses a half cell
            # by accident.
            raise SystemExit(
                f"{path.name} has n={len(samples)}, expected {N_EXPECTED}. "
                "Remove partial logs before analysing."
            )
        key = (log.eval.model, log.eval.task.split("/")[-1])
        if key in cells:
            raise SystemExit(
                f"Duplicate logs for {key[0]} {key[1]}. Exactly one log per cell."
            )
        cells[key] = Cell(samples)
    return cells


def compare(a: Cell, b: Cell):
    diff = a.yes_rate - b.yes_rate
    se = math.sqrt(a.yes_se ** 2 + b.yes_se ** 2)
    z = diff / se if se else 0.0
    return diff, z, normal_p(z)


def holm(pvalues: list[float], alpha: float = 0.05) -> list[bool]:
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    out = [False] * len(pvalues)
    broken = False
    for rank, i in enumerate(order):
        threshold = alpha / (len(pvalues) - rank)
        passes = (not broken) and pvalues[i] < threshold
        if not passes:
            broken = True
        out[i] = passes
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs", default="logs", help="directory of .eval logs")
    ap.add_argument("--carryover", action="store_true",
                    help="analyse the framing carry-over cells instead of the 2x2")
    args = ap.parse_args()

    if args.carryover:
        carryover(Path(args.logs))
        return

    directory = Path(args.logs)
    if not directory.is_dir():
        raise SystemExit(f"No such directory: {directory}")
    cells = load(directory)
    if not cells:
        raise SystemExit(f"No logs found in {directory}")

    base = next(iter(cells.values())).true_yes_rate
    print(f"# Regenerated from {len(cells)} cells in {directory}/\n")
    print(f"True YES rate on this draw: **{base:.3f}**. "
          "The primary metric is the judge's YES rate, read against that.\n")

    judges = [j for j in JUDGES if any(k[0] == j for k in cells)]
    for judge in judges:
        get = lambda c: cells[(judge, c)]
        print(f"\n## Judge {judge}\n")
        print("### YES rate\n")
        print("| source | NEUTRAL | WARNED |")
        print("|---|---|---|")
        for src in ("cipher", "absent"):
            print(f"| {src} | {get(src + '_neutral').yes_rate:.3f} "
                  f"| {get(src + '_warned').yes_rate:.3f} |")

        print("\n### Anchors against experiment 1\n")
        print("| cell | this run | experiment 1 | difference |")
        print("|---|---|---|---|")
        for a in ANCHORS:
            if (judge, a) not in cells:
                continue
            got = get(a).yes_rate
            pub = E1_PUBLISHED[a]
            print(f"| {a} | {got:.3f} | {pub:.3f} | {got - pub:+.3f} |")

        print("\n### Effects on YES rate\n")
        tests = [
            ("ciphertext, NEUTRAL row", "cipher_neutral", "absent_neutral"),
            ("ciphertext, WARNED row", "cipher_warned", "absent_warned"),
            ("warning, CIPHER row", "cipher_warned", "cipher_neutral"),
            ("warning, ABSENT row", "absent_warned", "absent_neutral"),
        ]
        results = [(label,) + compare(get(a), get(b)) for label, a, b in tests]
        survives = holm([r[3] for r in results])
        print("| effect | difference | z | p | survives Holm |")
        print("|---|---|---|---|---|")
        for (label, diff, z, p), ok in zip(results, survives):
            print(f"| {label} | {diff:+.3f} | {z:.2f} | {p:.3g} | {'yes' if ok else 'no'} |")

        print("\n### Secondary and diagnostics\n")
        print("| cell | YES rate | accuracy | balanced | unparsed |")
        print("|---|---|---|---|---|")
        for c in FACTORIAL + ANCHORS:
            if (judge, c) not in cells:
                continue
            cell = get(c)
            print(f"| {c} | {cell.yes_rate:.3f} | {cell.accuracy:.3f} "
                  f"| {cell.balanced:.3f} | {cell.unparsed_rate:.3f} |")




# ---- Framing carry-over beyond direct judging ------------------------------

CARRYOVER = [
    ("consultancy", "consultancy_cipher_neutral", "consultancy_cipher_warned"),
    ("debate", "debate_cipher_neutral", "debate_cipher_warned"),
]

# Experiment 1's OBSCURED YES rates for the same protocols, for the within-run
# reproduction check.
E1_OBSCURED_YES = {"consultancy": 0.130, "debate": 0.290}


def carryover(directory: Path) -> None:
    """Does the 2x2 framing result hold for consultancy and debate?

    Experiment 2 tested direct judging only. Without this, the claim that
    framing does not matter for the other protocols is an argument from the
    judge prompt being built identically, not a measurement.
    """
    cells = load(directory)
    by_task = {task: cell for (_model, task), cell in cells.items()}
    print(f"\n# Framing carry-over, from {len(cells)} cells in {directory}/\n")
    print("| protocol | neutral | warned | effect | z | p |")
    print("|---|---|---|---|---|---|")
    for name, neutral, warned in CARRYOVER:
        if neutral not in by_task or warned not in by_task:
            continue
        diff, z, p = compare(by_task[neutral], by_task[warned])
        print(f"| {name} | {by_task[neutral].yes_rate:.3f} "
              f"| {by_task[warned].yes_rate:.3f} | {diff:+.3f} | {z:.2f} | {p:.3f} |")

    print("\nWithin-run reproduction of experiment 1's OBSCURED cells:\n")
    print("| protocol | this run | experiment 1 | difference |")
    print("|---|---|---|---|")
    for name, _neutral, warned in CARRYOVER:
        if warned not in by_task:
            continue
        got = by_task[warned].yes_rate
        pub = E1_OBSCURED_YES[name]
        print(f"| {name} | {got:.3f} | {pub:.3f} | {got - pub:+.3f} |")


if __name__ == "__main__":
    main()
