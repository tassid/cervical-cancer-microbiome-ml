"""Reclassifica o P22 (PRJNA725946), que entrou no pipeline V4 mas é V3-V4.

Diagnóstico: as ASVs do P22 começam por TAGGGAATCTTCCACAATGG..., início da região V3
logo após o primer 341F, e não por TACG... (início de V4 após o 515F). Com o
classificador treinado só em V4, 79% das leituras do P22 ficaram sem gênero
(43% paradas em "c__Bacilli") e apareceram gêneros espúrios (Dickeya, Nocardia).

Correção feita aqui, sem precisar rodar o QIIME de novo: os outros projetos V3-V4
(P1, P6, P14, P19) usam o mesmo início de leitura, então cada ASV do P22 (220 nt)
recebe a taxonomia das ASVs V3-V4 cujo prefixo de 220 nt é idêntico (consenso se
houver várias). Cobre ~93% das leituras do P22.

A correção definitiva é reprocessar o P22 no ramo V3-V4 do pipeline (deblur +
classificador V3-V4). Este script serve para não travar as análises até lá.
"""
import os
from collections import defaultdict

import pandas as pd

from common import OUT_DIR, biom, fasta, meta, path, unzip_qza

m = meta()
v4 = biom(path("tassi", "V4_table.qza"))
seq_v4 = fasta(os.path.join(unzip_qza(path("tassi", "V4_repseqs.qza")), "dna-sequences.fasta"))
seq_v34 = fasta(os.path.join(unzip_qza(path("tassi", "V3V4_repseqs.qza")), "dna-sequences.fasta"))
tax_v34 = pd.read_csv(os.path.join(unzip_qza(path("tassi", "V3V4_taxonomy.qza")), "taxonomy.tsv"), sep="\t", index_col=0)["Taxon"]

ids = v4.index.intersection(m.index[m.Project == "P22"])
p22 = v4.loc[ids]
p22 = p22.loc[:, p22.sum() > 0]

prefixos = defaultdict(list)
for k, s in seq_v34.items():
    prefixos[s[:220]].append(tax_v34.get(k))


def consenso(taxas):
    niveis = [t.split("; ") for t in taxas if isinstance(t, str)]
    out = []
    for nivel in zip(*niveis):
        if len(set(nivel)) != 1:
            break
        out.append(nivel[0])
    return "; ".join(out) if out else "Unassigned"


def formata(t):
    r = [x.strip() for x in t.split(";")]
    r = (r + ["__"] * 6)[:6]
    return ";".join(x if x and not x.endswith("__") else "__" for x in r)


nova, leituras_ok = {}, 0
for f in p22.columns:
    s = seq_v4[f][:220]
    if s in prefixos:
        nova[f] = consenso(prefixos[s])
        leituras_ok += p22[f].sum()
print(f"P22: {len(ids)} amostras, {p22.shape[1]} ASVs; com correspondência exata em V3-V4: "
      f"{len(nova)} ASVs, {100 * leituras_ok / p22.values.sum():.1f}% das leituras")

col = [formata(nova[f]) if f in nova else "Unassigned;__;__;__;__;__" for f in p22.columns]
g = p22.T.groupby(col).sum().T
g = g[[c for c in g.columns if not any(x in c.lower() for x in ["mitochondria", "chloroplast", "archaea"])]]
g.to_pickle(f"{OUT_DIR}/p22_genero_corrigido.pkl")
top = (g.div(g.sum(axis=1), axis=0).mean() * 100).sort_values(ascending=False).head(8)
print({k.split(";")[-1]: round(v, 1) for k, v in top.items()})
