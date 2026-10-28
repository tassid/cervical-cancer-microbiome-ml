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
