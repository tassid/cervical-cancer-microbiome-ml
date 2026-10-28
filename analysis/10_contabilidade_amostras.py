"""Onde cada uma das 1.042 amostras catalogadas se perdeu, em cada tabela.

Para o pipeline da Tassiane usa as estatísticas do deblur (V3V4_stats, V4_stats) e as
tabelas por região antes do filtro de 1.000 leituras. Para a Paola só há a tabela
final, então a ausência é registrada sem etapa.

Também separa os sublotes do P14: amostras em que o deblur descartou >90% das
leituras na derreplicação (corte de 250 nt) e cujo primer já vinha removido na origem
(cutadapt encontrou o primer em ~1-2% das leituras, contra ~99% no outro sublote).
"""
import glob
import os

import pandas as pd

from common import OUT_DIR, biom, meta, paola, path, tassi, unzip_qza

m = meta()
P, T = paola(), tassi()
pre = pd.concat([biom(path("tassi", "V4_table.qza")).sum(axis=1),
                 biom(path("tassi", "V3V4_table.qza")).sum(axis=1)])
stats = pd.concat([pd.read_csv(os.path.join(unzip_qza(path("tassi", f"{r}_stats.qza")), "stats.csv"), index_col=0)
                   for r in ["V3V4", "V4"]])
stats["fracao_apos_derep"] = stats["reads-derep"] / stats["reads-raw"]

linhas = []
for s in m.index:
    proj = m.loc[s, "Project"]
    if s in T.index:
        tassi_motivo = "presente"
    elif proj == "P21":
        tassi_motivo = "P21 excluído (primer não publicado)"
    elif s in stats.index and stats.loc[s, "fracao_apos_derep"] < 0.1:
        tassi_motivo = "perdida no deblur (corte de 250/220 nt)"
    elif s in pre.index:
        tassi_motivo = "filtro de 1.000 leituras"
    else:
        tassi_motivo = "não chegou ao deblur"
    paola_leituras = int(P.loc[s].sum()) if s in P.index else None
    if paola_leituras is None:
        paola_motivo = "ausente da tabela"
    elif paola_leituras < 1000:
        paola_motivo = "presente com < 1.000 leituras"
    else:
        paola_motivo = "presente"
    linhas.append(dict(sampleid=s, projeto=proj, classe=m.loc[s, "tipo_amostra"],
                       paola=paola_motivo, paola_leituras=paola_leituras,
                       tassi=tassi_motivo, tassi_leituras=int(T.loc[s].sum()) if s in T.index else None,
                       deblur_leituras_brutas=stats["reads-raw"].get(s), deblur_fracao_apos_derep=stats["fracao_apos_derep"].get(s)))

R = pd.DataFrame(linhas)
R.to_csv(f"{OUT_DIR}/10_contabilidade_amostras.csv", index=False)

utilizavel = lambda col: R[col].eq("presente")
resumo = R.groupby("projeto").agg(catalogadas=("sampleid", "size"),
                                  paola_ok=("paola", lambda x: (x == "presente").sum()),
                                  tassi_ok=("tassi", lambda x: (x == "presente").sum()))
resumo["perdidas_nas_duas"] = R[~utilizavel("paola") & ~utilizavel("tassi")].groupby("projeto").size().reindex(resumo.index, fill_value=0)
resumo.to_csv(f"{OUT_DIR}/10_contabilidade_por_projeto.csv")
print(resumo)
print("\nMotivos (Tassiane):\n", pd.crosstab(R.projeto, R.tassi))
print("\nMotivos (Paola):\n", pd.crosstab(R.projeto, R.paola))

# P14: os dois sublotes
cut = pd.read_csv(os.path.join(unzip_qza(path("tassi", "P14_cutadapt_stats.qza")), "metadata.tsv"), sep="\t", skiprows=[1], index_col=0)
cut["sublote_sem_primer"] = stats["fracao_apos_derep"].reindex(cut.index) < 0.1
cut["bases_por_par"] = cut["bases-before"] / cut["reads-before"]
print("\nP14 por sublote:\n", cut.groupby("sublote_sem_primer")[
    ["reads-before", "bases_por_par", "percent-r1-with-adapter", "percent-reads-after"]].median().round(2).T)
print(m.loc[cut.index[cut.sublote_sem_primer]].tipo_amostra.value_counts().to_dict())
