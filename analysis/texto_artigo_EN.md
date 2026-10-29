# Suggested additions to the manuscript (draft)

Textos prontos para colar no artigo. As tabelas correspondentes estão em
`results/18_tabelas_artigo.md` (Tabela 1 corrigida e tabela de validação).

## Methods: sample selection (replaces the last paragraph of "Data Acquisition and Preprocessing")

Of the 1,042 runs listed in the ten BioProjects, several required exclusion or special
handling after inspection of the raw reads. In PRJNA933917 (Brazil), 21 of the 43 runs
(10 controls and 11 HSIL) did not contain 16S rRNA amplicons: no read carried the forward
primer or the start of the V3 region, and the most frequent sequences were human repetitive
elements (Alu and satellite DNA). These runs were excluded. PRJNA1029035 (USA) lists 55
cancer runs that form two groups: 26 runs with BioSample accessions and ~1,600 reads per
sample, and 29 runs without BioSample accessions, deposited one week later, in which only
~45% of the reads carried the 16S primer; reads without primer were discarded. In
PRJNA725946 (China), cancer and control samples were sequenced in runs with different read
lengths (~222 and ~274 nt after primer removal); all reads were therefore truncated to
220 nt, and the cancer-versus-control contrast within this study cannot be separated from
the sequencing run. Samples with fewer than 1,000 reads after denoising were removed. The
final numbers of samples per study and clinical group are given in Table 1.

## Table 1: footnotes

- PRJNA933917: 21 runs (10 controls, 11 HSIL) are not 16S amplicons (human DNA) and were excluded.
- PRJNA1029035: 55 runs are listed; 26 low-depth runs have BioSample accessions and 29 runs
  (without BioSample) were analysed. The BioProject assignment of the 29 runs should be
  confirmed in the SRA Run Selector.
- PRJNA725946: cancer and control samples were sequenced in separate runs (different read lengths).
- PRJEB83336: primer sequence not published.

## Results: validation (new paragraph, with Table X)

Because clinical status and study of origin were strongly associated (four studies contained
only cancer samples and one contained only controls), we compared three validation schemes
(Table X). With randomly split 10-fold cross-validation, the Random Forest reached AUCs of
0.97 for cancer, 0.85 for control, 0.76 for HSIL and 0.74 for LSIL. A model that received only
the study identifier, without any microbial feature, reached almost the same values (0.95,
0.85, 0.77 and 0.79). When each study was held out in turn (leave-one-project-out), AUCs fell
to 0.70, 0.51, 0.46 and 0.34; no LSIL sample and only 11 of 161 HSIL samples were correctly
classified. The microbial profile predicted the study of origin with 88% accuracy (chance:
32%). The same pattern was obtained after independent reprocessing of all raw data (AUCs
0.96/0.82/0.74/0.71 with random cross-validation and 0.64/0.44/0.48/0.35 with
leave-one-project-out) and after removing genera recognised as reagent contaminants.

## Results: biomarker selection (replaces the Boruta and LEfSe paragraphs)

Feature selection was repeated within each study that contained both groups being
compared (at least eight samples per group), so that study of origin could not contribute to
the result, and a genus was retained as a candidate biomarker only when it was selected in at
least two studies with the same direction of change. With all studies pooled, Boruta
confirmed 50 genera and LEfSe identified 104 genera discriminating cancer from controls.
Within studies, no genus was confirmed by Boruta in two studies, and only *Gemella*
(enriched in cancer in PRJNA518153 and PRJNA725946) was selected by LEfSe in two studies;
for HSIL and LSIL, LEfSe selected *Megasphaera* (PRJNA933917 and PRJNA518153) and
*Escherichia-Shigella* (PRJEB51893 and PRJNA914231), respectively. In PRJNA725946, where
cancer and control samples were sequenced in different runs, most genera selected within the
study were reagent-associated taxa (*Brevundimonas*, *Rhizobium*, *Ralstonia*,
*Delftia*), consistent with a batch effect. In PRJNA914231, the only study with cancer,
lesion and control samples sequenced together, cancer was characterised by enrichment of
anaerobes (*Anaerococcus*, *Peptoniphilus*, *Porphyromonas*). The genera that
remained consistent across studies were therefore those identified by the random-effects
meta-analysis (*Fusobacterium* and *Sneathia* in cancer; *Sneathia*,
*Megasphaera* and *Atopobium* in HSIL), each with modest effect sizes.

## Results: SHAP (replaces the pooled SHAP paragraph)

SHAP values from the pooled Random Forest mainly reflected study of origin. For each of the four
classes, all ten genera with the highest mean |SHAP| varied more between studies than between
clinical groups (rank-based η²), and several were concentrated in a single study (*Halomonas*,
97% of its abundance in PRJNA431248; *Rhodococcus*, 95% in PRJNA687644;
*Burkholderia-Caballeronia-Paraburkholderia*, 96% in PRJEB83336). The importance of each genus for
predicting clinical group was strongly correlated with its importance in a model trained to predict
the study (Spearman ρ = 0.81). When each study was held out, the SHAP ranking changed little (on
average 16 of the top 20 genera were retained), although AUCs fell to 0.34–0.70, indicating that a
stable SHAP ranking does not imply transferable biomarkers. Within studies, the genera most often
among the ten highest-ranked by SHAP were *Atopobium* (enriched in HSIL in three of four studies),
*Sneathia* (HSIL, two studies), and *Lactobacillus* (depleted) and *Corynebacterium* (enriched) in
cancer (PRJNA914231 and PRJNA518153), in agreement with the meta-analysis.

## Methods: community state types (new subsection)

Vaginal community state types (CSTs) were assigned with VALENCIA (France et al., 2020), a
nearest-centroid classifier based on Yue-Clayton similarity to 13 reference sub-CSTs. Because
SILVA 138 did not resolve *Lactobacillus crispatus* or *L. gasseri* in our amplicons, amplicon
sequence variants of *Lactobacillus*, *Gardnerella*, *Atopobium* and *Sneathia* were assigned to
species by alignment to the region-matched (V3-V4 or V4) vSpeciateDB reference sequences
(Holm et al., 2024), requiring at least 97% identity and a single best-matching vaginal species;
all *Gardnerella* variants were treated as *G. vaginalis*, and *Prevotella* was collapsed to genus
in both samples and centroids. CSTs were assigned to the 889 samples of the reprocessed table.
For each contrast (cancer, HSIL or LSIL vs control), the proportion of samples in CST IV (low
*Lactobacillus*), CST I (*L. crispatus*) and CST III (*L. iners*) was compared within each study
with at least five samples per group, and log odds ratios (0.5 continuity correction) were pooled
with a DerSimonian-Laird random-effects model, with and without PRJNA725946.

## Methods: within-study design and sample size (new subsection)

Because four studies contained only cancer samples and one contained almost only controls,
we tested whether these single-class studies contributed information on the case-control
contrast. (i) We counted the samples that came from studies containing both groups. (ii) We
shuffled clinical labels within each study, which removes the case-control information while
preserving study membership, and repeated the random 10-fold cross-validation (10 permutations).
(iii) For cancer vs control, we trained Random Forest and logistic regression models on studies
with both groups, with increasing fractions of their samples or with the single-class studies
added, and evaluated them on the held-out study (PRJNA725946 was excluded from these analyses
because its cases and controls were sequenced in different runs). (iv) We estimated the number of
samples per group needed to detect a standardised difference of 0.3 with 80% power (two-sided
α = 0.05).

## Results: community state types (new paragraph)

Most samples were assigned to CST IV-C (36%), CST III (24%), CST IV-B (24%) or CST I (14%). Within
studies, CST IV was more frequent in cancer than in controls in PRJNA914231 (83% vs 50%, Fisher
p = 0.04) and PRJNA518153 (70% vs 31%, p = 0.06), and less frequent in PRJNA725946 (45% vs 57%),
the study in which cases and controls were sequenced in different runs. Excluding this study,
the pooled odds ratio for CST IV in cancer was 4.5 (95% CI 1.7–12.2, p = 0.003); including it,
2.1 (0.5–9.7, p = 0.34, I² = 81%). Pooling all samples without regard to study gave an odds ratio
of 6.0, overstating the within-study effect. CST I (*L. crispatus*) was less frequent in cancer in
all three comparable studies (pooled OR 0.58, 0.25–1.36). For lesions, effects pointed in the same
direction but were smaller: CST IV in LSIL, OR 1.6 (0.95–2.7, p = 0.08); CST III (*L. iners*) in
LSIL, OR 0.57 (0.32–1.01, p = 0.06); CST IV in HSIL, OR 1.3 (0.75–2.2, p = 0.36).

## Results: single-class studies and sample size (new paragraph)

In the original table, 113 of 287 cancer samples (39%) came from studies without controls and
331 of 436 controls (76%) from studies without cancer (42% and 68% in the reprocessed table).
Shuffling the clinical labels within each study left most of the random cross-validation
performance intact (cancer AUC 0.96 to 0.92; control 0.84 to 0.81), indicating that pooled
performance derives largely from study membership. With about 105 training samples from studies
with both groups, the Random Forest reached an AUC of 0.74–0.75 in the held-out study; adding
the 350–450 samples from single-class studies did not improve it (0.76 in the original table)
or reduced it (0.67 in the reprocessed table). What single-class studies added was mainly the
contrast between *Lactobacillus*-dominated controls and *Lactobacillus*-depleted cancers, together
with study-specific artefacts; within PRJNA914231, Shannon diversity alone separated cancer from
controls with an AUC of 0.80, as did the models. Detecting a standardised difference of 0.3 with
80% power requires about 175 samples per group from the same studies, more than the paired samples
currently available.

## Discussion: limitations and future studies (new paragraph)

This meta-analysis has several limitations. Clinical group and study of origin were strongly
confounded: four studies contributed only cancer samples and one almost only controls, so a
large part of the pooled sample cannot inform the case-control comparison, and the within-study
estimates rest on few studies (two for the CST IV association with cancer). In PRJNA725946, cases
and controls were sequenced in different runs, which makes the within-study contrast inseparable
from a batch effect. Inspection of raw reads showed that half of the runs of the only Brazilian
study (PRJNA933917) contained human DNA rather than 16S amplicons, and that the 55 runs listed for
PRJNA1029035 comprise two sets with different depth and metadata. Studies used different regions
of the 16S rRNA gene (V3-V4 or V4), primers, kits and platforms, which limits species-level
resolution and comparability; CST similarity scores were low for 45% of samples, as expected for
populations outside the North American reference and for cancer. Information on HPV status, age,
menopausal status, histological type and stage was not available for all studies and could not
be adjusted for. Future studies should sequence cases and controls from the same population in
the same runs, record these clinical covariates, and aim for at least 175 samples per group. For
meta-analyses, additional studies with both cases and controls (identified, for example, with the
SRA search provided in our repository) and leave-one-study-out validation should be the standard.
