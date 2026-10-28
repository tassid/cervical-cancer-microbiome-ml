"""Mesma amostra, dois pipelines: a tabela da Paola e a da Tassiane dão o mesmo perfil?

Para cada amostra em comum, calcula a dissimilaridade de Bray-Curtis entre o perfil
de gêneros da Paola e o da Tassiane (0 = idêntico, 1 = nada em comum).
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import OUT_DIR, TABELAS, ativas, genero, meta, relativa

m = meta()
P = genero(TABELAS["PAOLA"]())
for nome in [n for n, _ in ativas() if n.startswith("TASSI")]:
    T = genero(TABELAS[nome]())
    comum = P.index.intersection(T.index)
    gl = P.columns.union(T.columns)
    A = relativa(P.loc[comum]).reindex(columns=gl, fill_value=0)
    B = relativa(T.loc[comum]).reindex(columns=gl, fill_value=0)
    mm = m.loc[comum].copy()
    mm["bray_curtis_entre_pipelines"] = 1 - np.minimum(A.values, B.values).sum(1)
    mm["razao_leituras_tassi_paola"] = (T.loc[comum].sum(axis=1) / P.loc[comum].sum(axis=1)).values
    resumo = mm.groupby("Project")[["bray_curtis_entre_pipelines", "razao_leituras_tassi_paola"]].median()
    resumo["n"] = mm.groupby("Project").size()
    print(f"\n== Paola x {nome}: {len(comum)} amostras em comum")
    print(resumo.round(3))
    resumo.to_csv(f"{OUT_DIR}/07_paola_vs_{nome}_por_projeto.csv")
    for g in ["Lactobacillus", "Gardnerella", "Prevotella", "Fusobacterium", "Sneathia", "Streptococcus", "Pseudomonas"]:
        print(f"  {g:14s} Spearman={spearmanr(A[g], B[g])[0]:.2f}  média Paola={A[g].mean()*100:.1f}%  {nome}={B[g].mean()*100:.1f}%")
