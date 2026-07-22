# Oversight without access: debate survives a judge that cannot read the source

**Unkad Labs, Mogadishu.** Contact: research@unkad.com

Pre-registered at [PREREGISTRATION.md](PREREGISTRATION.md), committed before the
confirmatory run. Code, transcripts, and per-sample scores in this repository.

---

## Abstract

Scalable oversight asks how a weak judge can supervise a stronger model. The
standard protocols, direct judging, consultancy, and debate, assume the judge and
the debaters share a representational medium: the judge may know less, but it can
read what the debaters read, and can therefore check a quotation against a source.
Debate's foundational argument, that verification is easier than generation, rests
on that assumption.

We make judge access an experimental parameter rather than an assumption, and add
a condition in which the judge is shown a source it **cannot read** while the
debaters read plaintext. The judge sees that a source exists and sees debaters
quoting from it, but can verify nothing.

Across 18 cells (3 protocols x 3 access levels x 2 judges, n = 300 each, 5,400
judgements), we find that **debate's advantage over direct judging is preserved
when the judge cannot verify a single quotation**. The lift is +0.148 with no
source and +0.141 with an unreadable source on our primary judge, and +0.187 and
+0.136 on a second judge. Whatever debate is providing, it does not route through
quote verification.

We also report a failure. Our pre-registered hypothesis that an unreadable source
is worse than no source did not survive multiple-comparison correction on the
primary metric, and we report it as failed.

Separately, and as an exploratory finding, judges shown an unreadable source do
not become uncertain. They collapse toward rejection. On a task whose true answer
is YES 61.7 percent of the time, direct judging under an unreadable source answered
YES 6.3 percent and 6.0 percent of the time on our two judges. Such a judge scores
1.000 on the reject-correct half of the data. We argue this failure mode is
systematically invisible to aggregate accuracy.

---

## 1. Introduction

An automated overseer is often applied to material it cannot process. The clearest
case is linguistic: a safety classifier, a reward model, or an LLM judge trained
predominantly on English, applied to one of the several thousand languages for
which it has little competence. The overseer is not absent. It runs, it returns a
score, and that score enters a pipeline.

The scalable oversight literature weakens judges in two ways: a smaller model, or
withheld information such as the source document. In both cases the judge remains
inside the same representational medium as the debaters. A weak English-speaking
judge reading an English debate about an English passage can still parse claims,
follow reasoning, and check whether a quotation supports what is claimed of it.
Its weakness is one of **capability**.

We study a different weakness: **access**. The judge is shown the source, and
cannot read it.

This is a cheap proxy, available today, for a condition alignment research
otherwise has to imagine: an overseer supervising reasoning it cannot inspect. It
is also, unmodified, the situation of automated oversight in most of the world's
languages.

### Contributions

1. `JudgeAccess` as a parameter over standard oversight protocols, with an
   `OBSCURED` level distinct from `NONE`, and an open implementation on Inspect.
2. A pre-registered confirmatory result, replicated on two judges: **debate's
   advantage survives the judge losing the ability to verify quotations** (H4).
3. A pre-registered hypothesis that failed, reported as failed (H3).
4. An exploratory finding: illegible evidence induces **systematic rejection**
   rather than uncertainty, and this is invisible to aggregate accuracy.
5. A validated fabrication detector, and the finding that a naive dishonest
   debater's fabrication rate cannot be cleanly distinguished from an honest
   one's, though fabrication does not appear to pay.

---

## 2. Related work

Kenton et al., *On scalable oversight with weak LLMs judging strong LLMs*
(NeurIPS 2024, arXiv:2407.04622), characterise direct judging, consultancy, and
debate, and establish the information-asymmetry setup in which the judge does not
see the passage and the debaters do. Our protocol structure follows theirs so that
results are comparable, and our `NONE` condition is their asymmetry condition.

Our departure is the `OBSCURED` level. To our knowledge, no prior work varies
judge access to the object level as a graded parameter while holding debater
competence fixed, and none tests debate's grounding mechanism under conditions
where quotation cannot be checked in principle.

We build on [Inspect](https://inspect.aisi.org.uk/), the UK AI Security
Institute's evaluation framework.

---

## 3. Method

### 3.1 Task

BoolQ validation: a passage, a yes/no question, and a ground-truth label. Passages
capped at 180 words so a full debate fits the context of small local models.
Sampled with a fixed seed (0).

**Label balance.** Our 300-sample draw is 185 YES and 115 NO. The trivial
always-YES baseline therefore scores **0.617**, not 0.500. Every accuracy figure
below should be read against 0.617. This skew is the reason we report balanced
accuracy alongside raw accuracy, and the reason the exploratory analysis in
section 6 exists at all.

### 3.2 Access levels

```
FULL      judge reads the source, as in standard debate
OBSCURED  judge sees a ROT13 transform of the source, and is told the debaters
          can read it and that it may not be able to verify their quotations
NONE      judge sees no source (the classic information-asymmetry condition)
```

`OBSCURED` is deliberately not `NONE`. The judge knows a source exists, sees its
shape, length, word boundaries, and punctuation, and sees claims made about it. It
simply cannot check any of them. That is closer to reading a language you do not
speak than deleting the text would be.

### 3.3 Protocols

`direct_judging` (judge alone), `consultancy` (one assigned advocate, position
alternated independently of truth so the protocol measures the judge rather than
the consultant), and `debate` (two debaters, opposite sides, one round each).

**Debaters always read plaintext, at every access level.** This is the design
point: debater competence is held fixed while judge access varies. Any difference
across access levels is a property of the judge's situation, not of argument
quality.

### 3.4 Models

Judges: qwen2.5:7b (primary) and qwen2.5:3b (secondary). Debaters: llama3.1:8b in
every cell. All quantised, run locally through Ollama. No API calls, no rented
compute. The entire 5,400-judgement matrix ran overnight on one Apple Silicon
machine.

### 3.5 Scoring

The judge is asked for one word, YES or NO, then a brief reason. We read the first
YES/NO token emitted. Responses from which neither can be read are scored
incorrect and reported separately.

**Unparsed rate was 0.000 in all 18 cells.** The preregistration's concern about
protocols confusing judges into silence did not materialise.

---

## 4. Validation: the judge genuinely cannot read the cipher

The `OBSCURED` condition is meaningless if the judge can decode ROT13. Every judge
model was probed with explicit decode requests, naive reads, and quote requests,
scored by word overlap against the true plaintext, with a disqualification
threshold of 0.5.

| model | worst overlap | verdict |
|---|---|---|
| qwen2.5:7b | 0.00 | pass |
| qwen2.5:3b | 0.00 | pass |
| llama3.1:8b | 0.00 | pass |
| gemma2:9b | 0.00 | pass |

All four scored 0.00 across nine probes each. This check must be re-run for any
new judge, since decoding ability improves with capability, and it is wired into
the run script ahead of the matrix rather than left to discipline.

---

## 5. Confirmatory results

### 5.1 The full matrix

Raw accuracy, n = 300 per cell. Always-YES baseline = 0.617.

**Judge qwen2.5:7b**

| access | direct | consultancy | debate |
|---|---|---|---|
| FULL | 0.827 | 0.757 | 0.840 |
| NONE | 0.537 | 0.660 | 0.743 |
| OBSCURED | 0.447 | 0.447 | 0.633 |

**Judge qwen2.5:3b**

| access | direct | consultancy | debate |
|---|---|---|---|
| FULL | 0.830 | 0.753 | 0.860 |
| NONE | 0.510 | 0.637 | 0.753 |
| OBSCURED | 0.443 | 0.500 | 0.623 |

Standard errors are 0.020 to 0.029 throughout.

### 5.2 Pre-registered hypothesis tests

Five primary comparisons, two-proportion tests on **raw accuracy**, Holm-corrected
within judge. H4 and H5 predict the absence of a difference, so for those a
non-significant result is support.

**Judge qwen2.5:7b**

| hypothesis | diff | z | p | outcome |
|---|---|---|---|---|
| H1 debate > direct (NONE) | +0.207 | 5.40 | <0.0001 | **confirmed**, survives Holm |
| H2 debate > consultancy (NONE) | +0.083 | 2.24 | 0.0251 | fails Holm |
| H3 direct OBSCURED < NONE | -0.090 | -2.21 | 0.0268 | **fails** |
| H4 lift preserved (diff-in-diff) | -0.020 | -0.36 | 0.7178 | **supported** |
| H5 debate = direct (FULL) | +0.013 | 0.44 | 0.6612 | **supported** |

**Judge qwen2.5:3b**

| hypothesis | diff | z | p | outcome |
|---|---|---|---|---|
| H1 debate > direct (NONE) | +0.243 | 6.38 | <0.0001 | **confirmed**, survives Holm |
| H2 debate > consultancy (NONE) | +0.117 | 3.13 | 0.0018 | **confirmed**, survives Holm |
| H3 direct OBSCURED < NONE | -0.067 | -1.64 | 0.1013 | **fails** |
| H4 lift preserved (diff-in-diff) | -0.063 | -1.15 | 0.2521 | **supported** |
| H5 debate = direct (FULL) | +0.030 | 1.02 | 0.3096 | **supported** |

### 5.3 H1 and H5: the rig behaves at both ends

Debate beats direct judging by 20.7 and 24.3 points under information asymmetry,
replicating the established result at high significance on both judges. Under
`FULL`, debate's advantage disappears (+0.013 and +0.030, both non-significant).

The rig therefore produces a large effect exactly where the literature says it
should and no effect exactly where it should not. Nothing downstream would be
interpretable without both.

### 5.4 H4: the main result

Debate's advantage over direct judging, computed within access level:

| judge | lift under NONE | lift under OBSCURED | difference | p |
|---|---|---|---|---|
| qwen2.5:7b | +0.207 | +0.187 | -0.020 | 0.718 |
| qwen2.5:3b | +0.243 | +0.180 | -0.063 | 0.252 |

The lift under an unreadable source is statistically indistinguishable from the
lift under no source, on both judges. In balanced-accuracy terms (section 6.1) the
same holds: +0.148 versus +0.141, and +0.187 versus +0.136.

**Debate helps a judge that cannot verify a single quotation, by approximately the
amount it helps a judge with no source at all.** Whatever mechanism produces
debate's advantage here, it does not run through quote verification, because in
this condition quote verification is impossible by construction.

### 5.5 H3: a pre-registered failure, reported as failed

We predicted that an unreadable source would be *worse* than no source, on the
intuition that illegible material actively misleads. Direct judging did fall, by
9.0 and 6.7 points, in the predicted direction on both judges. Neither survives
Holm correction (p = 0.0268 and p = 0.1013).

**We report H3 as failed.** The preregistration commits us to this: "If direct
judging under OBSCURED is statistically indistinguishable from NONE, H3 fails and
our headline pilot observation was noise. We will report that."

One disclosure matters here. Under **balanced accuracy**, H3 would pass on the
primary judge (-0.063, z = -2.81, p = 0.0050). The preregistration named raw
accuracy as the primary metric. Changing metrics after seeing results in order to
rescue a hypothesis is precisely the practice pre-registration exists to prevent,
so we do not do it. H3 failed. The balanced-accuracy result is exploratory, and it
motivates section 6 rather than salvaging section 5.

---

## 6. Exploratory analyses

Everything in this section was decided after seeing the data. None of it is
confirmatory, and each item is stated as a hypothesis for a future pre-registered
experiment rather than as an established result.

### 6.1 Balanced accuracy

Given 61.7 percent YES labels, raw accuracy rewards a judge that leans NO on the
115 NO items even as it fails the 185 YES items. Balanced accuracy, the mean of
per-label accuracies, removes that.

| judge | cell | raw | balanced | acc given YES | acc given NO | YES rate |
|---|---|---|---|---|---|---|
| 7b | direct/full | 0.827 | 0.848 | 0.757 | 0.939 | 0.490 |
| 7b | direct/none | 0.537 | 0.614 | 0.281 | 0.948 | 0.193 |
| 7b | direct/obscured | 0.447 | 0.551 | 0.103 | **1.000** | **0.063** |
| 7b | consultancy/full | 0.757 | 0.786 | 0.659 | 0.913 | 0.440 |
| 7b | consultancy/none | 0.660 | 0.695 | 0.546 | 0.843 | 0.397 |
| 7b | consultancy/obscured | 0.447 | 0.535 | 0.157 | 0.913 | 0.130 |
| 7b | debate/full | 0.840 | 0.857 | 0.784 | 0.930 | 0.510 |
| 7b | debate/none | 0.743 | 0.762 | 0.681 | 0.843 | 0.480 |
| 7b | debate/obscured | 0.633 | 0.693 | 0.438 | 0.948 | 0.290 |
| 3b | direct/full | 0.830 | 0.854 | 0.751 | 0.957 | 0.480 |
| 3b | direct/none | 0.510 | 0.590 | 0.249 | 0.930 | 0.180 |
| 3b | direct/obscured | 0.443 | 0.549 | 0.097 | **1.000** | **0.060** |
| 3b | consultancy/full | 0.753 | 0.785 | 0.649 | 0.922 | 0.430 |
| 3b | consultancy/none | 0.637 | 0.677 | 0.503 | 0.852 | 0.367 |
| 3b | consultancy/obscured | 0.500 | 0.580 | 0.238 | 0.922 | 0.177 |
| 3b | debate/full | 0.860 | 0.872 | 0.822 | 0.922 | 0.537 |
| 3b | debate/none | 0.753 | 0.777 | 0.676 | 0.878 | 0.463 |
| 3b | debate/obscured | 0.623 | 0.685 | 0.422 | 0.948 | 0.280 |

H1, H4, and H5 hold under balanced accuracy on both judges, so the main results
are not artifacts of label skew.

### 6.2 Illegible evidence induces rejection, not uncertainty

The judge's YES rate as access degrades, against a true rate of 0.617:

| judge | protocol | FULL | NONE | OBSCURED |
|---|---|---|---|---|
| 7b | direct | 0.490 | 0.193 | **0.063** |
| 7b | consultancy | 0.440 | 0.397 | 0.130 |
| 7b | debate | 0.510 | 0.480 | 0.290 |
| 3b | direct | 0.480 | 0.180 | **0.060** |
| 3b | consultancy | 0.430 | 0.367 | 0.177 |
| 3b | debate | 0.537 | 0.463 | 0.280 |

The pattern is monotonic in access, consistent across protocols, and near-identical
across two judges (0.063 and 0.060 in the extreme cell).

A judge shown text it cannot read does not spread its uncertainty. It rejects.
Under `direct/obscured` it answers YES 6 percent of the time on a task that is YES
62 percent of the time, and consequently scores **1.000 on NO items** on both
judges.

That 1.000 is the point. It is not competence. It is the arithmetic shadow of
answering NO to nearly everything, and it is indistinguishable from competence in
any metric that does not condition on the label.

**Hypothesis for future work.** An automated overseer applied to material it cannot
process may fail toward rejection rather than toward noise, and such failure is
systematically flattering under aggregate metrics: it looks conservative, it looks
safe, and on data where most items are negative it looks accurate. A safety
classifier applied to a language it does not handle might therefore report
defensible aggregate numbers while having near-zero discrimination.

We did not test that. We tested question-answering judges on BoolQ. The
generalisation to safety classifiers is a hypothesis we intend to test directly,
not a result of this paper.

#### Follow-up: a confound in this section, found and tested

After publishing we found a confound in the comparison this section rests on. Our
`OBSCURED` and `NONE` conditions differ in **two** ways, not one. `OBSCURED` shows
ciphertext *and* tells the judge "You cannot decode this passage" and "You may not
be able to verify their quotations". `NONE` says only that the passage was not
shown. Either the ciphertext or the warning could produce the collapse, and
nothing in this paper separates them. Had the warning been responsible, the
finding above would have been a demand characteristic of our own prompt.

We ran the dissociation, in [`collapse/`](collapse/). A matched
2x2 crossing ciphertext against warning, n = 300 per cell, two judges, with anchor
cells reproducing this paper's prompts verbatim.

**The ciphertext causes the collapse. The warning does not.** On the primary judge,
ciphertext moved the YES rate by -0.213 (z = -7.67) with the warning absent, while
the warning moved it +0.010 (p = 0.57) with ciphertext present. Both replicate on
the second judge. The cleanest cell shows the judge ciphertext and says nothing
whatever about verification, and it answers YES 4.3 percent of the time.

The anchors reproduce this paper closely: `e1_none` returned 0.193 against the
0.193 reported here, and `e1_obscured` returned 0.057 and 0.060 against 0.063.

The finding in this section therefore survives its strongest objection. We record
the confound rather than quietly benefiting from having resolved it, because the
version of this paper you may have read first did not know about it.

### 6.3 Consultancy degrades a sighted judge

On both judges, consultancy under `FULL` is **below** direct judging: 0.786 versus
0.848 (z = -2.12, p = 0.034) and 0.785 versus 0.854 (z = -2.42, p = 0.016) in
balanced accuracy. A single advocate makes a judge that can read the passage
perfectly well **worse** than leaving it alone.

Under `OBSCURED` the picture does not replicate. Consultancy is marginally below
direct on the 7b judge (-0.016, p = 0.451) and marginally above on the 3b judge
(+0.031, p = 0.172). Neither is significant. An earlier reading of the 7b results
alone, where consultancy and direct were identical at 0.447, suggested that a
single advocate is worth exactly nothing to a blind judge. The second judge does
not support that, and we withdraw it.

### 6.4 Do dishonest debaters exploit a blind judge?

Under `OBSCURED` the judge cannot check any quotation, so fabrication is
unpunishable. We built a detector to measure whether debaters exploit this,
extracting quoted spans and matching them against the true passage.

**Calibration changed the measure.** We expected the honest debater, whose position
matches ground truth and which has no motive to invent, to give a false-positive
floor near zero. It does not. Honest debaters misquote about 12 percent of the
time: they elide with ellipses, insert bracketed clarifications, add their own
connectives, and wrap song titles in quotation marks. That is a property of
llama3.1:8b, not a detector fault, and no threshold removes it while remaining
sensitive to real fabrication.

Calibration also exposed a worse problem. A plain token-coverage detector caught
only **28 percent** of synthetic single-entity swaps, because changing one token in
a twenty-token quote costs 0.05 of coverage. Entity substitution is the cheapest
and highest-value fabrication available, and the obvious detector is nearly blind
to it. Weighting by meaning-bearing tokens raises swap detection to 99.8 percent.

Detector sensitivity, against corrupted known-grounded quotes:

| corruption | caught |
|---|---|
| entity swap | 0.998 |
| recombination (real words, wrong order) | 0.976 |
| wholesale invention | 1.000 |

We therefore report the **excess** of the dishonest rate over the honest rate,
both carrying the same loose-quoting baseline.

Debaters never see the judge and are the same model in every cell, so the two
`debate/obscured` runs are two independent samples of one process. They do not
agree well, and we report both rather than pick one.

| run | honest | dishonest | excess | z |
|---|---|---|---|---|
| debate/obscured, 7b matrix | 0.122 | 0.141 | +0.019 | 0.71 |
| debate/obscured, 3b matrix | 0.113 | 0.173 | +0.060 | 2.13 |
| **pooled** | **0.117** | **0.157** | **+0.040** | **2.02** (p = 0.043) |

Our first reading used a single run, showed no excess, and would have supported
reporting that dishonest debaters do not fabricate more than honest ones. Pooled
across both runs there is a small excess of about 4 points at p = 0.043. That is
marginal, it does not survive correction for the several exploratory comparisons
in this section, and the two runs straddle it. The honest summary is that **we
cannot cleanly distinguish the dishonest fabrication rate from the honest one**,
which is a weaker statement than saying they are the same.

What is consistent across both runs is that fabrication did not pay. The
dishonest debater won 0.33 of the time when it fabricated against 0.37 when it
did not in the first run, and 0.33 against 0.38 in the second.

The obvious caveat is that our debaters were never told the judge is blind. They
were assigned a position and asked to argue it. Whether a debater informed of the
judge's blindness behaves differently is the subject of our next experiment, and
until it runs, this result should be read as a baseline rather than as evidence
that debate is safe under adversarial pressure.

---

## 7. Limitations

**ROT13 is not a language.** This is the central limitation. Our motivation is
oversight in languages an overseer does not handle, and we tested a cipher on
English text. A judge facing ROT13 has exactly zero comprehension; a judge facing
Somali has some non-zero and unmeasured amount. These are different situations.
The choice was deliberate, since establishing the effect under a clean binary
should precede spending annotation budget, but nothing here speaks directly to any
natural language. Our next experiment replaces the binary with a competence
gradient across real languages.

**BoolQ is answerable from world knowledge.** Direct judging under `NONE` lands
above chance because many questions do not need the passage. This compresses the
range in which protocols can show value.

**Label skew.** 61.7 percent YES. We report balanced accuracy throughout in
response, but a balanced dataset would have been better, and the exploratory
finding in 6.2 needs one to be tested properly.

**Two judges from one family.** qwen2.5:7b and qwen2.5:3b replicate each other
closely, but they are the same architecture and training lineage. We had justified
the 3b judge as a weaker model offering more headroom; it scored 0.830 under
`FULL` against the 7b's 0.827, so it provided no such headroom and functioned as a
same-strength replication instead. Genuine judge-capability variation should be
selected by measuring `FULL` accuracy, not by assuming parameter count predicts it.

**Single dataset, single debater model, one round, English only.**

**Exploratory analyses are exploratory.** Section 6 was written after seeing the
data and does not carry the guarantees of section 5.

---

## 8. Conclusion

Making judge access a parameter rather than an assumption produces one clear
positive result and one clear negative one.

Debate's advantage over direct judging survives the judge losing the ability to
verify quotations, replicated on two judges and robust to the choice of accuracy
metric. Since verification is impossible by construction in that condition, the
mechanism behind debate's advantage here is not the one usually offered for it.
Identifying what it actually is remains open.

An unreadable source is not reliably worse than no source, as we had predicted. We
report that hypothesis as failed.

The finding we did not anticipate is the one we consider most consequential. A
judge denied the ability to read does not become uncertain, it becomes rejecting,
and a rejecting judge posts a perfect score on the half of the data where
rejection is correct. If that generalises from question-answering to the safety
classifiers actually deployed across low-resource languages, then some portion of
multilingual safety tooling may be reporting respectable aggregate numbers while
discriminating almost nothing. Testing that is our next priority.

---

## Reproducibility

All 5,400 judgements ran locally on quantised models through Ollama on a single
machine. No API keys, no rented compute.

```bash
ollama pull qwen2.5:7b qwen2.5:3b llama3.1:8b gemma2:9b
python -m venv .venv && ./.venv/bin/pip install -e .

./.venv/bin/python -m oversight.validate      # blinding gate, never skip
./run_overnight.sh                            # full 18-cell matrix
./.venv/bin/python -m oversight.fabrication --selftest transcripts/*debate-obscured*.eval
```

Per-cell results in `results.tsv`. The 18 confirmatory transcripts, with full
debate text, judge prompts, completions, and per-sample scores, are in
[`transcripts/`](transcripts/), each matched to its `results.tsv` row by exact
accuracy. See [`transcripts/README.md`](transcripts/README.md) for why that
directory is separate from Inspect's working `logs/`. Prompts in `oversight/protocols.py`, unmodified
between the pilot and the confirmatory run.

## License

Apache-2.0.
