# Pre-registration: does debate survive the judge losing verifiable access?

**Written before the confirmatory run, after a pilot. Timestamped by the commit
that introduces this file.**

Unkad Labs. Contact: research@unkad.com

---

## Why this document exists

We are a new lab with no track record. Pre-registering costs an afternoon and
makes it harder for us to tell ourselves a convenient story after the fact. The
pilot results below are attractive, which is precisely the reason to fix the
analysis plan before running at scale.

## Background and the specific gap

Scalable oversight studies how a weak judge can supervise stronger models. The
standard protocols are direct judging, consultancy, and debate, as characterised
in Kenton et al., [On scalable oversight with weak LLMs judging strong LLMs](https://arxiv.org/abs/2407.04622)
(NeurIPS 2024).

That literature makes judges weak in two ways: a smaller model, or withheld
information. In both cases the judge remains inside the same representational
medium as the debaters and can, in principle, verify a quotation against a source.

We introduce a third condition. The judge is shown a source it **cannot read**,
while debaters read plaintext. The judge can see that a source exists and can see
debaters quoting from it, but cannot check any quotation. This is the situation of
an automated overseer applied to a language it does not handle, and a cheap proxy
for oversight where the object level is not inspectable.

## Pilot results that motivated this

n = 60 per cell, BoolQ validation, judge qwen2.5:7b, debaters llama3.1:8b.

| Judge access | Direct | Consultancy | Debate |
|---|---|---|---|
| FULL | 0.783 | 0.817 | 0.783 |
| NONE | 0.633 | 0.600 | 0.750 |
| OBSCURED | 0.500 | not run | 0.617 |

**No comparison in this pilot is statistically significant.** All differences of
interest sit between roughly 1.3 and 1.5 standard errors. These numbers are the
reason for the confirmatory run, not evidence for any claim.

Two patterns motivate the hypotheses below. Debate lifted accuracy by about 12
points in both NONE and OBSCURED. And OBSCURED direct judging fell to chance,
below the NONE baseline, suggesting an unreadable source may be worse than no
source.

## Hypotheses

**H1 (replication).** Under NONE, debate outperforms direct judging.
*Directional. This is the positive control; failure invalidates the rig.*

**H2 (replication).** Under NONE, debate outperforms consultancy.
*Directional.*

**H3 (primary, novel).** Under OBSCURED, direct judging is **worse** than under
NONE. An unreadable source degrades the judge relative to having no source.
*Directional.*

**H4 (primary, novel).** Debate's advantage over direct judging is preserved
under OBSCURED, meaning the lift is not significantly smaller than under NONE.
*This is a test of equivalence in direction; we predict the lift persists.*

**H5 (control).** Under FULL, debate does **not** outperform direct judging,
because a judge that can read the source has nothing to gain.
*Directional. Confirmed in the pilot and re-tested here.*

## Design

**Dataset.** BoolQ validation, passages of at most 180 words, sampled with a
fixed seed. Ground truth is BoolQ's yes/no label.

**Conditions.** 3 protocols (direct, consultancy, debate) × 3 access levels
(FULL, NONE, OBSCURED) = 9 cells.

**Sample size.** n = 300 per cell. Chosen so that a 12-point difference between
proportions near 0.5 to 0.75 is detectable at approximately 80 percent power,
which the pilot at n = 60 could not do.

**Models.** Primary judge qwen2.5:7b, debaters llama3.1:8b. A secondary weaker
judge, qwen2.5:3b, runs the same matrix as a robustness check, because our
primary judge sits close to ceiling under FULL and a weaker judge gives the
protocols more headroom.

**Obscuring mechanism.** ROT13 substitution, which preserves length, word
boundaries, and punctuation so the judge sees something of the right shape that
it cannot read.

## Validation gate

The obscured condition is meaningless if the judge can decode the cipher. Before
the confirmatory run, every judge model is probed with explicit decode requests,
naive reads, and quote requests, scored by word overlap against plaintext. A model
exceeding 0.5 overlap is disqualified.

Pilot status: qwen2.5:7b, llama3.1:8b, and gemma2:9b all scored 0.00. qwen2.5:3b
will be checked before use.

## Primary metric and analysis

**Metric.** Judge accuracy against BoolQ ground truth, per cell.

**Primary comparisons**, each a two-proportion test at α = 0.05:
1. debate_none vs direct_none (H1)
2. debate_none vs consultancy_none (H2)
3. direct_obscured vs direct_none (H3)
4. (debate − direct) under OBSCURED vs the same difference under NONE (H4)
5. debate_full vs direct_full (H5)

**Multiple comparisons.** Five primary tests. We report both uncorrected p-values
and Holm-corrected values, and we treat only the corrected results as
confirmatory.

**Unparsed responses.** Judge outputs from which no YES or NO can be read are
scored incorrect and reported separately as a rate per cell. If any cell exceeds
10 percent unparsed, we report it prominently, since a protocol that confuses the
judge into silence is a finding rather than a nuisance.

## Stopping rule

The full matrix runs to completion. No interim analysis, no early stopping, no
addition of samples after seeing results.

## What would falsify the interesting claim

If direct judging under OBSCURED is statistically indistinguishable from NONE, H3
fails and our headline pilot observation was noise. We will report that.

If debate's lift disappears under OBSCURED, H4 fails and the honest conclusion is
that verifiable access is required for debate to function, which is a different
paper and one we will also write.

## Known limitations, stated in advance

BoolQ questions are frequently answerable from world knowledge alone, which is why
direct judging under NONE lands well above chance. This compresses the range in
which protocols can demonstrate value, and it means our results speak to a task
with a strong prior rather than one requiring the source.

Single dataset, single debater model, English only. The linguistic case that
motivates this work is not tested here; that is deliberate, because establishing
the effect under controlled conditions should precede spending annotation budget
on Somali.

ROT13 is a specific obscuring mechanism. A different transform might produce
different judge behaviour, and we have not tested that.

## Commitments

All transcripts, judge decisions, and per-sample scores released with results.
Prompt formulations reported, including variants tried and discarded. Negative
and null results published on the same terms as positive ones.
