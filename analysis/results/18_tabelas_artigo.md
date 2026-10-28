# Table 1 (corrected)

Counts as CC/HSIL/LSIL/Control.

| Project   | BioProject   | Country   | 16S region   | Article (CC/HSIL/LSIL/Ctrl)   | Catalogued      | Paola table, >=1,000 reads   | Reprocessed table   | Note                                                                                                                                                                                 |
|:----------|:-------------|:----------|:-------------|:------------------------------|:----------------|:-----------------------------|:--------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| P1        | PRJNA687644  | China     | V3-V4        | 68/0/0/4                      | 68/0/0/4        | 68/0/0/4                     | 68/0/0/4            |                                                                                                                                                                                      |
| P2        | PRJNA518153  | USA       | V4           | 10/27/11/29                   | 10/27/11/29     | 10/27/11/29                  | 10/27/11/29         |                                                                                                                                                                                      |
| P6        | PRJNA687331  | China     | V3-V4        | 26/0/0/0                      | 26/0/0/0        | 26/0/0/0                     | 26/0/0/0            |                                                                                                                                                                                      |
| P9        | PRJNA431248  | USA       | V4           | 58/0/0/0                      | 58/0/0/0        | 53/0/0/0                     | 53/0/0/0            |                                                                                                                                                                                      |
| P10       | PRJEB51893   | USA       | V4           | 1/59/43/214                   | 1/59/43/216     | 1/58/43/210                  | 1/58/43/211         |                                                                                                                                                                                      |
| P14       | PRJNA933917  | Brazil    | V3-V4        | 0/22/0/21                     | 0/22/0/21       | 0/11/0/11                    | 0/11/0/11           | 21 runs (10 controls, 11 HSIL) are not 16S amplicons (human DNA) and were excluded.                                                                                                  |
| P16       | PRJNA1029035 | USA       | V4           | 26/0/0/0                      | 55/0/0/0        | 29/0/0/0                     | 47/0/0/0            | 55 runs listed: 26 low-depth runs with BioSample (counted in Table 1) and 29 runs without BioSample, ~55% of whose reads lack the 16S primer; only the 29 are in the analysed table. |
| P19       | PRJNA914231  | Nigeria   | V3-V4        | 31/60/58/19                   | 31/60/58/19     | 29/56/55/16                  | 29/59/56/16         | Primer corrected empirically.                                                                                                                                                        |
| P21       | PRJEB83336   | Spain     | V3-V4        | 0/2/0/100                     | 0/2/0/103       | 0/2/0/103                    | 0/0/0/0             | Primer sequence not published; included in the article table, excluded from the reprocessed table.                                                                                   |
| P22       | PRJNA725946  | China     | V3-V4        | 65/0/0/54                     | 65/0/0/54       | 65/0/0/54                    | 65/0/0/54           | Cancer and control samples were sequenced in runs with different read lengths (~222 vs ~274 nt).                                                                                     |
| Total     |              |           |              | 285/170/112/441               | 314/170/112/446 | 281/154/109/427              | 299/155/110/325     |                                                                                                                                                                                      |

# Table X. Random Forest AUC by validation scheme

| Table             | Validation                                |   cancer |   control |   lesion high |   lesion low |
|:------------------|:------------------------------------------|---------:|----------:|--------------:|-------------:|
| Paola table       | Evaluated on training samples             |    1     |     1     |         1     |        1     |
| Paola table       | Random 10-fold cross-validation           |    0.966 |     0.849 |         0.763 |        0.737 |
| Paola table       | Study identifier only (no microbiome)     |    0.95  |     0.846 |         0.77  |        0.787 |
| Paola table       | Leave-one-project-out                     |    0.701 |     0.51  |         0.458 |        0.338 |
| Paola table       | Predicting the study of origin (accuracy) |    0.881 |   nan     |       nan     |      nan     |
| Reprocessed table | Evaluated on training samples             |    1     |     1     |         1     |        1     |
| Reprocessed table | Random 10-fold cross-validation           |    0.963 |     0.821 |         0.737 |        0.708 |
| Reprocessed table | Study identifier only (no microbiome)     |    0.942 |     0.809 |         0.754 |        0.763 |
| Reprocessed table | Leave-one-project-out                     |    0.636 |     0.442 |         0.479 |        0.354 |
| Reprocessed table | Predicting the study of origin (accuracy) |    0.863 |   nan     |       nan     |      nan     |
