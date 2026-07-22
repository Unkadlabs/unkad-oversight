"""Regenerate every table and test statistic in PAPER.md from the transcripts.

The paper should not be the only place its numbers exist. This reads the eval
logs directly, recomputes the full matrix, the hypothesis tests, and the
exploratory analyses, and prints them as markdown. If a number here disagrees
with the paper, the paper is wrong.

    python -m oversight.analyse                    # reads transcripts/
    python -m oversight.analyse --logs logs/       # or any directory of .eval

Cells are identified by the judge model and task recorded inside each log, not
by filename. Only logs with the full n=300 are used.
"""

from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log

JUDGES = ["ollama/qwen2.5:7b", "ollama/qwen2.5:3b"]
PROTOCOLS = ["direct", "consultancy", "debate"]
ACCESS = ["full", "none", "obscured"]
N_EXPECTED = 300
ALPHA = 0.05


def normal_p(z: float) -> float:
    """Two-sided p-value for a z statistic."""
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


class Cell:
    """One judge x protocol x access condition."""

    def __init__(self, samples):
        self.n = len(samples)
        self.correct_by_label = {"YES": [0, 0], "NO": [0, 0]}
        self.yes = 0
        self.unparsed = 0
        for s in samples:
            truth = s.target if isinstance(s.target, str) else s.target[0]
            score = next(iter((s.scores or {}).values()), None)
            answer = getattr(score, "answer", None)
            if answer == "YES":
                self.yes += 1
            elif answer != "NO":
                self.unparsed += 1
            bucket = self.correct_by_label[truth]
            bucket[1] += 1
            bucket[0] += answer == truth

    @property
    def acc_yes(self) -> float:
        c, n = self.correct_by_label["YES"]
        return c / n if n else 0.0

    @property
    def acc_no(self) -> float:
        c, n = self.correct_by_label["NO"]
        return c / n if n else 0.0

    @property
    def raw(self) -> float:
        return sum(b[0] for b in self.correct_by_label.values()) / self.n

    @property
    def raw_se(self) -> float:
        p = self.raw
        return math.sqrt(p * (1 - p) / self.n)

    @property
    def balanced(self) -> float:
        """Mean of per-label accuracies.

        Our BoolQ draw is 61.7 percent YES, so raw accuracy rewards a judge that
        leans NO regardless of whether it is discriminating. Balanced accuracy
        does not. Reported alongside raw throughout, never in place of it.
        """
        return (self.acc_yes + self.acc_no) / 2

    @property
    def balanced_se(self) -> float:
        out = 0.0
        for acc, (_, n) in ((self.acc_yes, self.correct_by_label["YES"]),
                            (self.acc_no, self.correct_by_label["NO"])):
            if n:
                out += acc * (1 - acc) / n
        return 0.5 * math.sqrt(out)

    @property
    def yes_rate(self) -> float:
        return self.yes / self.n


def load(directory: Path) -> dict:
    cells: dict = {}
    skipped = []
    for path in sorted(directory.glob("*.eval")):
        try:
            log = read_eval_log(str(path))
        except Exception as exc:  # a corrupt log should be visible, not silent
            skipped.append((path.name, f"unreadable: {exc}"))
            continue
        samples = log.samples or []
        if len(samples) != N_EXPECTED:
            skipped.append((path.name, f"n={len(samples)}, expected {N_EXPECTED}"))
            continue
        key = (log.eval.model, log.eval.task.split("/")[-1])
        if key in cells:
            # Two logs claiming the same cell is exactly how a pre-confirmatory
            # run silently replaces a reported number. Refuse to guess.
            raise SystemExit(
                f"Duplicate logs for {key[0]} {key[1]}.\n"
                f"  already loaded: {cells[key][1]}\n"
                f"  also found:     {path.name}\n"
                "Point --logs at a directory holding exactly one log per cell "
                "(transcripts/ is curated for this)."
            )
        cells[key] = (Cell(samples), path.name)
    if skipped:
        print(f"<!-- skipped {len(skipped)} log(s): "
              + "; ".join(f"{n} ({why})" for n, why in skipped) + " -->\n")
    return {k: v[0] for k, v in cells.items()}


def matrix(cells: dict, judge: str, attr: str) -> str:
    lines = ["| access | " + " | ".join(PROTOCOLS) + " |",
             "|---|" + "---|" * len(PROTOCOLS)]
    for access in ACCESS:
        row = []
        for protocol in PROTOCOLS:
            cell = cells.get((judge, f"{protocol}_{access}"))
            row.append(f"{getattr(cell, attr):.3f}" if cell else "n/a")
        lines.append(f"| {access.upper()} | " + " | ".join(row) + " |")
    return "\n".join(lines)


def compare(a: Cell, b: Cell, balanced: bool = False):
    """Difference between two cells, with a z statistic and p-value."""
    if balanced:
        diff = a.balanced - b.balanced
        se = math.sqrt(a.balanced_se ** 2 + b.balanced_se ** 2)
    else:
        diff = a.raw - b.raw
        se = math.sqrt(a.raw_se ** 2 + b.raw_se ** 2)
    z = diff / se if se else 0.0
    return diff, se, z, normal_p(z)


def hypotheses(cells: dict, judge: str, balanced: bool = False):
    """The five pre-registered comparisons, in the order they were registered."""
    def c(protocol, access):
        return cells[(judge, f"{protocol}_{access}")]

    out = []
    out.append(("H1 debate > direct (NONE)",) + compare(c("debate", "none"), c("direct", "none"), balanced))
    out.append(("H2 debate > consultancy (NONE)",) + compare(c("debate", "none"), c("consultancy", "none"), balanced))
    out.append(("H3 direct OBSCURED < NONE",) + compare(c("direct", "obscured"), c("direct", "none"), balanced))

    # H4 is a difference of differences: is debate's lift the same under an
    # unreadable source as under no source at all?
    key = "balanced" if balanced else "raw"
    se_key = "balanced_se" if balanced else "raw_se"
    lift_obscured = getattr(c("debate", "obscured"), key) - getattr(c("direct", "obscured"), key)
    lift_none = getattr(c("debate", "none"), key) - getattr(c("direct", "none"), key)
    se = math.sqrt(sum(
        getattr(c(p, a), se_key) ** 2
        for p, a in [("debate", "obscured"), ("direct", "obscured"),
                     ("debate", "none"), ("direct", "none")]
    ))
    did = lift_obscured - lift_none
    z = did / se if se else 0.0
    out.append(("H4 lift preserved (diff-in-diff)", did, se, z, normal_p(z)))

    out.append(("H5 debate = direct (FULL)",) + compare(c("debate", "full"), c("direct", "full"), balanced))
    return out, lift_none, lift_obscured


def holm(tests) -> dict:
    """Holm-Bonferroni. Sequential: once one test fails, every later one fails.

    H4 and H5 predict the absence of a difference, so a non-significant result
    supports them. Holm is only meaningful for the directional tests, and the
    caller is expected to know that. We mark it rather than hide it.
    """
    order = sorted(range(len(tests)), key=lambda i: tests[i][4])
    verdict = {}
    broken = False
    for rank, i in enumerate(order):
        threshold = ALPHA / (len(tests) - rank)
        passes = (not broken) and tests[i][4] < threshold
        if not passes:
            broken = True
        verdict[i] = passes
    return verdict


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs", default="transcripts", help="directory of .eval logs")
    args = ap.parse_args()

    directory = Path(args.logs)
    if not directory.is_dir():
        raise SystemExit(f"No such directory: {directory}")
    cells = load(directory)
    if not cells:
        raise SystemExit(f"No complete (n={N_EXPECTED}) logs found in {directory}")

    judges = [j for j in JUDGES if any(k[0] == j for k in cells)]
    print(f"# Regenerated from {len(cells)} cells in {directory}/\n")

    base = None
    for judge in judges:
        any_cell = next(c for k, c in cells.items() if k[0] == judge)
        base = any_cell.correct_by_label["YES"][1] / any_cell.n
    print(f"Label balance: always-YES baseline = **{base:.3f}**. "
          "Read every accuracy against this, not 0.500.\n")

    for judge in judges:
        print(f"\n## Judge {judge}\n")
        print("### Raw accuracy\n")
        print(matrix(cells, judge, "raw"))
        print("\n### Balanced accuracy\n")
        print(matrix(cells, judge, "balanced"))
        print("\n### YES rate (true rate %.3f)\n" % base)
        print(matrix(cells, judge, "yes_rate"))

        print("\n### Per-cell detail\n")
        print("| cell | raw | balanced | acc given YES | acc given NO | YES rate | unparsed |")
        print("|---|---|---|---|---|---|---|")
        for protocol in PROTOCOLS:
            for access in ACCESS:
                c = cells.get((judge, f"{protocol}_{access}"))
                if not c:
                    continue
                print(f"| {protocol}/{access} | {c.raw:.3f} | {c.balanced:.3f} | "
                      f"{c.acc_yes:.3f} | {c.acc_no:.3f} | {c.yes_rate:.3f} | "
                      f"{c.unparsed / c.n:.3f} |")

        try:
            tests, lift_none, lift_obscured = hypotheses(cells, judge)
        except KeyError as exc:
            print(f"\n(incomplete matrix for {judge}, skipping tests: missing {exc})")
            continue
        verdict = holm(tests)
        print("\n### Pre-registered tests (raw accuracy, primary metric)\n")
        print("| hypothesis | diff | z | p | survives Holm |")
        print("|---|---|---|---|---|")
        for i, (name, diff, _se, z, p) in enumerate(tests):
            mark = "yes" if verdict[i] else "no"
            if name.startswith(("H4", "H5")):
                mark += " (predicts no difference; non-significant = supported)"
            print(f"| {name} | {diff:+.3f} | {z:.2f} | {p:.4f} | {mark} |")
        print(f"\nDebate's lift: **{lift_none:+.3f}** under NONE, "
              f"**{lift_obscured:+.3f}** under OBSCURED.\n")

        btests, blift_none, blift_obscured = hypotheses(cells, judge, balanced=True)
        print("### Same tests on balanced accuracy (exploratory)\n")
        print("The pre-registration named raw accuracy as primary. These are "
              "reported for transparency, not to relabel any outcome.\n")
        print("| hypothesis | diff | z | p |")
        print("|---|---|---|---|")
        for name, diff, _se, z, p in btests:
            print(f"| {name} | {diff:+.3f} | {z:.2f} | {p:.4f} |")
        print(f"\nBalanced lift: **{blift_none:+.3f}** under NONE, "
              f"**{blift_obscured:+.3f}** under OBSCURED.")


if __name__ == "__main__":
    main()
