"""Os gêneros que o artigo diz aumentar/diminuir com a doença mudam na mesma direção dentro de cada projeto?

Teste de Mann-Whitney em abundância relativa, para todas as amostras juntas (como no artigo)
e separadamente em cada projeto que tem as duas classes comparadas.
"""
import pandas as pd
from scipy.stats import mannwhitneyu

from common import OUT_DIR, TABELAS, genero, meta, relativa

GENEROS = ["Lactobacillus", "Gardnerella", "Prevotella", "Fusobacterium", "Porphyromonas", "Bacteroides",
           "Peptostreptococcus", "Streptococcus", "Sneathia", "Atopobium", "Pseudomonas",
           "Burkholderia-Caballeronia-Paraburkholderia", "Enterococcus", "Megasphaera", "Dialister",
           "Anaerococcus", "Peptoniphilus", "Campylobacter"]
COMPARACOES = {"cancer vs control": ("cancer", "control"),
               "HSIL vs control": ("lesion high", "control"),
               "LSIL vs control": ("lesion low", "control")}

m = meta()
linhas = []
for nome in ["PAOLA", "TASSI_FIX"]:
    rel = relativa(genero(TABELAS[nome]())) * 100
    mm = m.loc[rel.index]
    for comp, (a, b) in COMPARACOES.items():
        for pj in ["todos"] + sorted(mm.Project.unique()):
            s = mm if pj == "todos" else mm[mm.Project == pj]
            ia, ib = s.index[s.tipo_amostra == a], s.index[s.tipo_amostra == b]
            if len(ia) < 4 or len(ib) < 4:
                continue
            for g in GENEROS:
                if g not in rel:
                    continue
                xa, xb = rel.loc[ia, g], rel.loc[ib, g]
                p = mannwhitneyu(xa, xb).pvalue if (xa.sum() + xb.sum()) > 0 else 1.0
                linhas.append(dict(tabela=nome, comparacao=comp, projeto=pj, genero=g, n_a=len(ia), n_b=len(ib),
                                   media_a=xa.mean(), media_b=xb.mean(),
                                   direcao="sobe" if xa.mean() > xb.mean() else "desce", p=p))

R = pd.DataFrame(linhas)
R.to_csv(f"{OUT_DIR}/05_abundancia_dentro_do_projeto.csv", index=False)
for (nome, comp), s in R.groupby(["tabela", "comparacao"]):
    s = s.assign(celula=s.apply(lambda r: ("↑" if r.direcao == "sobe" else "↓") + ("*" if r.p < 0.05 else "") + ("*" if r.p < 0.001 else ""), axis=1))
    print(f"\n== {nome} | {comp}  (* p<0,05  ** p<0,001)")
    print(s.pivot(index="genero", columns="projeto", values="celula").reindex(GENEROS).fillna("").to_string())
