# Confirmatory transcripts

The 18 Inspect log files backing every number in [PAPER.md](../PAPER.md). Each
contains the full debate transcript, the judge's prompt and completion, and the
per-sample score for all 300 samples in that cell.

`MANIFEST.tsv` maps each file to its judge, cell, and reported accuracy. Every
file here was matched to its row in `results.tsv` by exact accuracy before being
copied, so the mapping is verified rather than assumed.

## Why this directory exists separately from `logs/`

`logs/` is the working directory Inspect writes to, and it is gitignored. It
accumulates pilot runs, the invalid n=60 first attempt, and reruns, so it is not
a clean record of what the paper reports.

One example of why that matters. `logs/` contains a `direct_none` run for
qwen2.5:7b at n=300 scoring 0.507, from a pre-confirmatory run started before the
official matrix. The paper reports 0.537, from the confirmatory run. Both are
n=300 and both look authoritative from the filename alone. Anyone reanalysing the
raw `logs/` directory would silently get a different number for that cell.

Only the confirmatory 18 are here. The 0.507 orphan is deliberately excluded, and
is named here so the exclusion is on the record rather than invisible.

## Reading a log

```python
from inspect_ai.log import read_eval_log
log = read_eval_log("transcripts/<file>.eval")
for s in log.samples:
    s.metadata["passage"]     # true plaintext
    s.metadata["transcript"]  # debater arguments as the judge saw them
    s.target                  # BoolQ ground truth
    s.scores                  # judge verdict, parsed answer, raw completion
```
