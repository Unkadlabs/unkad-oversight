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
every judge model, because decoding ability improves with capability. Current
status on our three local judges:

```
PASS  ollama/qwen2.5:7b     worst overlap 0.00
PASS  ollama/llama3.1:8b    worst overlap 0.00
PASS  ollama/gemma2:9b      worst overlap 0.00
```

## Running it

Everything runs locally on quantised models through [Ollama](https://ollama.com).
No API keys, no rented compute.

```bash
ollama pull qwen2.5:7b llama3.1:8b gemma2:9b

python -m venv .venv && ./.venv/bin/pip install -e .

# Validate the blinding first. Never skip this.
./.venv/bin/python -m oversight.validate

# Run 1: positive control, judge sighted
./.venv/bin/inspect eval oversight/task.py@direct_full --model ollama/qwen2.5:7b
./.venv/bin/inspect eval oversight/task.py@consultancy_full --model ollama/qwen2.5:7b
./.venv/bin/inspect eval oversight/task.py@debate_full --model ollama/qwen2.5:7b

# Run 2: judge cannot verify quotations
./.venv/bin/inspect eval oversight/task.py@debate_obscured --model ollama/qwen2.5:7b
```

Task data is BoolQ: a passage, a yes/no question, and ground truth.

## The experimental plan

**Run 1, positive control.** With the judge sighted, does debate beat direct
judging, as the literature says it should? If not, the rig is broken and nothing
downstream means anything. This is the first thing to run and the cheapest way to
discover a problem.

**Run 2, the hypothesis test.** Six cells: three protocols, judge sighted and
blinded. The metric is not absolute accuracy, which will fall in both conditions,
but whether **debate's advantage over direct judging survives blinding**.

- If it survives, our hypothesis is wrong and the result is better than the one we
  set out to find: debate is robust to the judge losing object-level access.
- If it collapses, verifiable access is a precondition for debate, which is a real
  constraint on the protocol.

**Run 3, the fabrication test.** Under blinding, one debater is assigned the
incorrect position. How often does it misrepresent the source, and does
misrepresentation win? This tests debate's foundational assumption directly.

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
