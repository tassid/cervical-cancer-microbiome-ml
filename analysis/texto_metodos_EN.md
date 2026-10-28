# Suggested Methods text (draft)

Texto sugerido para a seção de Métodos do artigo. Os trechos entre colchetes precisam ser
conferidos com o processamento final.

## Sample selection and exclusions

Of the 1,042 runs catalogued from the ten BioProjects, runs that did not contain 16S rRNA
amplicons were excluded after inspection of the raw reads: 21 runs from PRJNA933917 (Brazil;
10 controls and 11 HSIL) contained no forward primer and no V3 start motif, and their most
frequent sequences were human repetitive elements (Alu, satellite DNA). In PRJNA1029035
(USA), only ~45% of the reads of the main sequencing batch carried the 16S primer; reads
without primer were discarded. Samples with fewer than 1,000 reads after denoising were
removed. PRJEB83336 (Spain) [was included / was excluded because the primer sequence was not
published]. The final dataset comprised [N] samples ([n] cancer, [n] HSIL, [n] LSIL and [n]
controls) from [k] BioProjects (Table 1).

## Sequence processing

Primers were removed with cutadapt, discarding reads without primer. Reads were quality
filtered (q2-quality-filter defaults) and denoised with Deblur. Because the studies amplified
different regions (V4 or V3-V4) with different read lengths, each region was processed
separately (trim length 250 nt for V3-V4 and 220 nt for V4; 220 nt for PRJNA725946, whose
cancer and control samples were sequenced in runs with different read lengths, ~222 nt and
~274 nt after primer removal). Taxonomy was assigned with a naive Bayes classifier trained on
SILVA 138 (99%) reference sequences extracted with the primer pair of each region (confidence
0.7). Sequences assigned to mitochondria, chloroplasts or archaea and singletons were removed,
and tables were collapsed at genus level before merging the two regions.

## Accounting for study of origin

Because clinical status was strongly associated with study of origin (Cramér's V = 0.55-0.57;
four studies contained only cancer samples and one contained only controls), all analyses
were performed with and without adjustment for study. Alpha diversity was compared with
linear models including study as a fixed effect. Beta diversity was partitioned with
PERMANOVA (Bray-Curtis), reporting the variance explained by clinical status alone, by study
alone, and by clinical status conditional on study with permutations restricted within
studies. Differential abundance was tested on centred log-ratio transformed genus abundances
with linear models including study as a fixed effect (Benjamini-Hochberg correction). In
addition, effect sizes (Hedges' g) were estimated within each study that contained both
groups being compared and pooled with a DerSimonian-Laird random-effects model, reporting I²
as a measure of between-study heterogeneity.

## Machine learning and validation

Random Forest classifiers (500 trees, relative abundance at genus level) were evaluated with
three schemes: (i) stratified 10-fold cross-validation with random splits; (ii) a baseline
model that received only the study identifier, without microbial features; and (iii)
leave-one-project-out validation, in which each study was held out in turn. As a negative
control, the same features were used to predict the study of origin. Performance was
reported as the area under the ROC curve per class, computed on held-out predictions only.
An exhaustive comparison of eight classifiers, three transformations (relative abundance,
CLR, presence/absence) and SMOTE oversampling was performed for the cancer versus control
task under the same validation schemes. Sensitivity analyses repeated the models after
removing genera recognised as reagent or laboratory contaminants.

## Data and code availability

All sequencing data are public (BioProject accessions in Table 1). Processing scripts and
analysis code are available at https://github.com/tassid/cervical-cancer-microbiome-ml.
