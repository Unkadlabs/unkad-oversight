# Oversight without access to the object level

**Scalable oversight protocols with the judge's access to the source as a
parameter rather than an assumption.**

Built on [Inspect](https://inspect.aisi.org.uk/), the evaluation framework from
the UK AI Security Institute. By [Unkad Labs](https://unkad.com), a non-profit AI
research laboratory in Mogadishu.

> **Results are in.** The full pre-registered matrix has run: 3 protocols x 3
> access levels x 2 judges, n = 300 per cell, 5,400 judgements. Read
> **[PAPER.md](PAPER.md)**. The analysis plan was fixed in
> [PREREGISTRATION.md](PREREGISTRATION.md) before the confirmatory run.
>
> Headline: **debate's advantage over direct judging survives the judge losing the
> ability to verify quotations.** One pre-registered hypothesis failed and is
> reported as failed. Separately, judges shown a source they cannot read collapse
> toward rejection rather than uncertainty, answering YES 6 percent of the time on
> a task that is YES 62 percent of the time, and so scoring 1.000 on the
> reject-correct half of the data.

## The question

The scalable oversight literature makes judges weak in two ways: give them a
smaller model, or withhold information such as the source document. In both cases
the judge stays inside the same representational medium as the debaters. A weak
English-speaking judge reading an English debate about an English passage can
still parse claims, follow reasoning, and check whether a quotation supports what
is claimed of it. Its weakness is one of **capability**.

We are interested in a different weakness: **access**. What happens when the judge
cannot read the object level at all?

That condition is not hypothetical. It is the situation of any automated overseer
applied to a language it does not handle, which today means most of the world's
languages. It is also a cheap present-day proxy for the harder case alignment
worries about, where a system's reasoning is not inspectable in principle.

Debate's foundational claim is that verification is easier than generation, which
is what makes honesty the winning strategy. **That claim assumes the judge can
verify.** This repository is built to test what happens when it cannot.

## What is here

### `JudgeAccess`, the parameter

```python
FULL      # judge reads the source, as in standard debate
OBSCURED  # judge sees a transformed source it cannot read, but can see
          # debaters quoting from it. Quotations are unverifiable.
NONE      # judge sees no source (the classic information-asymmetry condition)
```

`OBSCURED` is the condition of interest, and it is deliberately not the same as
`NONE`. The judge knows a source exists, can see its shape, and can see claims
made about it. It simply cannot check any of them. That is closer to reading a
language you do not speak than deleting the text would be.

### Protocols

`direct_judging`, `consultancy`, and `debate`, following the structure in
Kenton et al., [On scalable oversight with weak LLMs judging strong LLMs](https://arxiv.org/abs/2407.04622)
(NeurIPS 2024), so results are comparable to the existing literature. Each takes
a `JudgeAccess` value. Debaters always see the full source, which is the point:
**debater competence is held fixed while judge access varies.**

### Validation

The obscured condition is only meaningful if the judge genuinely cannot read the
transformed passage. `oversight/validate.py` probes each judge model with explicit
decode requests, naive reads, and quote requests, and measures word overlap
against the true plaintext.

This must pass before any result is interpretable, and it must be re-run for
every judge model, because decoding ability improves with capability. Status on
all four local models we have used:

```
PASS  ollama/qwen2.5:7b     worst overlap 0.00
PASS  ollama/qwen2.5:3b     worst overlap 0.00
PASS  ollama/llama3.1:8b    worst overlap 0.00
PASS  ollama/gemma2:9b      worst overlap 0.00
```

## Reproducing the results

Everything runs locally on quantised models through [Ollama](https://ollama.com).
No API keys, no rented compute. The full matrix took about eight hours on one
Apple Silicon machine.

### Check our numbers without running anything

The 18 confirmatory logs are in [`transcripts/`](transcripts/), so every table and
test statistic in the paper can be regenerated in about a minute, without a GPU
and without Ollama installed.

```bash
python -m venv .venv && ./.venv/bin/pip install -e .
./.venv/bin/python -m oversight.analyse
```

That prints the full matrix, balanced accuracy, YES rates, per-cell unparsed
rates, and all five pre-registered tests with Holm correction, as markdown. If
anything it prints disagrees with [PAPER.md](PAPER.md), the paper is wrong.

### Rerun the experiment from scratch

```bash
# One model per command; ollama pull takes a single argument.
ollama pull qwen2.5:7b
ollama pull qwen2.5:3b
ollama pull llama3.1:8b
ollama pull gemma2:9b

python -m venv .venv && ./.venv/bin/pip install -e .

# Validate the blinding first. Never skip this: the obscured condition is void
# if a judge can read the cipher, and this is the only thing standing between
# you and a meaningless result.
./.venv/bin/python -m oversight.validate

# The full 18-cell matrix at n=300. Writes results.tsv incrementally, in
# hypothesis-priority order, so an interrupted run is still usable.
./run_overnight.sh

# Analyse whatever you just produced.
./.venv/bin/python -m oversight.analyse --logs logs/
```

Single cells, if you want to poke at one condition:

```bash
./.venv/bin/inspect eval oversight/task.py@debate_obscured \
    --model ollama/qwen2.5:7b -T n=300
```

Task names are `{direct,consultancy,debate}_{full,none,obscured}`. Note `-T n=300`
rather than `--limit`: `--limit` truncates Inspect's own sample loading and will
silently give you a smaller run than you asked for. We lost a full overnight run
to that mistake, and `results-INVALID-n60.tsv` and `overnight-INVALID-n60.log`
are kept in the repository as the record of it. Nothing in the paper draws on
them. The giveaway was standard errors around 0.05 where n = 300 should have
produced roughly 0.025.

### Expected runtime per cell

Debate cells generate three completions per sample and dominate everything else.

| protocol | approximate wall clock at n=300 |
|---|---|
| direct | 5 to 9 minutes |
| consultancy | 23 to 33 minutes |
| debate | 47 to 49 minutes |

Swapping in a smaller judge barely helps, because the debaters are the same model
in every cell and do most of the generation.

## What we ran, and what came of it

**Positive control.** Under `FULL`, debate does not beat direct judging (+0.013 and
+0.030, both non-significant). Under `NONE` it beats it decisively (+0.207 and
+0.243). Large effect where the literature says there should be one, none where
there should not be.

**The hypothesis test.** Debate's lift is statistically indistinguishable between
`NONE` and `OBSCURED` on both judges. Debate helps a judge that cannot verify a
single quotation. See [PAPER.md](PAPER.md) section 5.4.

**The fabrication test.** `oversight/fabrication.py` measures whether debaters
quote things the passage does not contain. Naive dishonest debaters do not
fabricate more than honest ones. Whether a debater *told* the judge is blind
behaves differently is the subject of our next experiment.

## Commitments

Small lab, no track record, so the practices matter more than usual.

- **Pre-registration** of run 2's conditions, primary metric, and analysis plan
  before it executes.
- **Transcripts released** with every result. The obvious objection is that the
  debates were incoherent, and that should be inspectable rather than asserted.
- **Prompt sensitivity reported.** A result that survives only one prompt
  formulation is a result about that prompt.
- **Sample sizes stated plainly.** These runs are small and the confidence
  intervals will be wide.

## Related work this builds on

Kenton et al., [On scalable oversight with weak LLMs judging strong LLMs](https://arxiv.org/abs/2407.04622),
NeurIPS 2024, for the protocol structure. [Inspect](https://inspect.aisi.org.uk/)
for the evaluation framework.

Our own related work: [SomaliBench](https://huggingface.co/spaces/unkadlabs/somalibench),
measuring English versus Somali refusal gaps, and
[the Somali token tax](https://github.com/unkadlabs/somali-token-tax).

## License

Apache-2.0.
