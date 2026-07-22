# Regenerated from 12 cells in logs/

True YES rate on this draw: **0.617**. The primary metric is the judge's YES rate, read against that.


## Judge ollama/qwen2.5:7b

### YES rate

| source | NEUTRAL | WARNED |
|---|---|---|
| cipher | 0.043 | 0.053 |
| absent | 0.257 | 0.213 |

### Anchors against experiment 1

| cell | this run | experiment 1 | difference |
|---|---|---|---|
| e1_obscured | 0.057 | 0.063 | -0.006 |
| e1_none | 0.193 | 0.193 | +0.000 |

### Effects on YES rate

| effect | difference | z | p | survives Holm |
|---|---|---|---|---|
| ciphertext, NEUTRAL row | -0.213 | -7.67 | 1.75e-14 | yes |
| ciphertext, WARNED row | -0.160 | -5.93 | 3.01e-09 | yes |
| warning, CIPHER row | +0.010 | 0.57 | 0.568 | no |
| warning, ABSENT row | -0.043 | -1.25 | 0.21 | no |

### Secondary and diagnostics

| cell | YES rate | accuracy | balanced | unparsed |
|---|---|---|---|---|
| cipher_neutral | 0.043 | 0.427 | 0.535 | 0.000 |
| cipher_warned | 0.053 | 0.430 | 0.536 | 0.000 |
| absent_neutral | 0.257 | 0.580 | 0.645 | 0.000 |
| absent_warned | 0.213 | 0.550 | 0.624 | 0.000 |
| e1_obscured | 0.057 | 0.433 | 0.539 | 0.000 |
| e1_none | 0.193 | 0.510 | 0.586 | 0.000 |

## Judge ollama/qwen2.5:3b

### YES rate

| source | NEUTRAL | WARNED |
|---|---|---|
| cipher | 0.043 | 0.060 |
| absent | 0.273 | 0.193 |

### Anchors against experiment 1

| cell | this run | experiment 1 | difference |
|---|---|---|---|
| e1_obscured | 0.060 | 0.063 | -0.003 |
| e1_none | 0.220 | 0.193 | +0.027 |

### Effects on YES rate

| effect | difference | z | p | survives Holm |
|---|---|---|---|---|
| ciphertext, NEUTRAL row | -0.230 | -8.13 | 4.44e-16 | yes |
| ciphertext, WARNED row | -0.133 | -5.01 | 5.4e-07 | yes |
| warning, CIPHER row | +0.017 | 0.92 | 0.356 | no |
| warning, ABSENT row | -0.080 | -2.33 | 0.02 | yes |

### Secondary and diagnostics

| cell | YES rate | accuracy | balanced | unparsed |
|---|---|---|---|---|
| cipher_neutral | 0.043 | 0.420 | 0.528 | 0.000 |
| cipher_warned | 0.060 | 0.437 | 0.542 | 0.000 |
| absent_neutral | 0.273 | 0.583 | 0.644 | 0.000 |
| absent_warned | 0.193 | 0.543 | 0.622 | 0.000 |
| e1_obscured | 0.060 | 0.443 | 0.549 | 0.000 |
| e1_none | 0.220 | 0.543 | 0.615 | 0.000 |
