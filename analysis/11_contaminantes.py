"""Contaminantes de reagente e de laboratório: quanto pesam e se mudam os resultados.

Sem controles negativos de extração nos BioProjects, não dá para rodar o decontam.
A alternativa é uma lista de gêneros reconhecidos como contaminantes de kit em
amostras de baixa biomassa (Salter et al., 2014, BMC Biol 12:87; Eisenhofer et al.,
2019, Trends Microbiol 27:105), mais Wolbachia (endossimbionte de inseto) e
cloroplasto. Gêneros que também são habitantes plausíveis do trato genital
(Streptococcus, Corynebacterium, Pseudomonas, Escherichia, Staphylococcus) ficam de
fora da lista para não remover sinal biológico.

Saídas: fração de leituras contaminantes por projeto e classe, e sensibilidade
(CV aleatória, LOPO e previsão do projeto com e sem esses gêneros).
"""
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from common import CLASSES, OUT_DIR, TABELAS, ativas, genero, meta, relativa

CONTAMINANTES = [
    "Burkholderia-Caballeronia-Paraburkholderia", "Ralstonia", "Cupriavidus", "Bradyrhizobium",
    "Methylobacterium-Methylorubrum", "Sphingomonas", "Delftia", "Brevundimonas", "Caulobacter",
    "Mesorhizobium", "Allorhizobium-Neorhizobium-Pararhizobium-Rhizobium", "Novosphingobium",
    "Acidovorax", "Herbaspirillum", "Massilia", "Pelomonas", "Variovorax", "Stenotrophomonas",
    "Halomonas", "Shewanella", "Bacillus", "Brochothrix", "Paenibacillus", "Thermus", "Aeribacillus",
    "Geobacillus", "Anoxybacillus", "Wolbachia", "Chloroplast", "Rhodococcus", "Flavobacterium",
    "Chryseobacterium", "Pedobacter", "Deinococcus", "Microbacterium", "Achromobacter",
    "Ochrobactrum", "Phyllobacterium", "Afipia", "Bosea", "Aquabacterium", "Comamonas",
    "Janthinobacterium", "Duganella", "Undibacterium", "Tepidimonas", "Dickeya", "Nocardia",
]


def rf():
    return RandomForestClassifier(n_estimators=500, n_jobs=-1, random_state=42)


def avalia(X, y, g):
    """AUC por classe em CV aleatória e LOPO, e acurácia ao prever o projeto."""
    out = {}
    for esquema in ["cv", "lopo"]:
        P = np.zeros((len(y), len(CLASSES)))
        splits = (StratifiedKFold(10, shuffle=True, random_state=42).split(X, y) if esquema == "cv"
                  else [(np.where(g != p)[0], np.where(g == p)[0]) for p in np.unique(g)])
        for tr, te in splits:
            c = rf().fit(X[tr], y[tr])
            P[np.ix_(te, [CLASSES.index(k) for k in c.classes_])] = c.predict_proba(X[te])
        out[esquema] = {c: roc_auc_score((y == c).astype(int), P[:, i]) for i, c in enumerate(CLASSES)}
    pp = np.empty(len(g), dtype=object)
    for tr, te in StratifiedKFold(10, shuffle=True, random_state=42).split(X, g):
        pp[te] = rf().fit(X[tr], g[tr]).predict(X[te])
    out["acuracia_projeto"] = float((pp == g).mean())
    return out


m = meta()
resultado = {}
for nome, carregar in ativas():
    G = genero(carregar())
    rel = relativa(G)
    mm = m.loc[G.index]
    presentes = [c for c in CONTAMINANTES if c in G.columns]
    frac = rel[presentes].sum(axis=1) * 100
    tab = frac.groupby([mm.Project, mm.tipo_amostra]).median().unstack().round(2)
    tab.to_csv(f"{OUT_DIR}/11_contaminantes_por_projeto_{nome}.csv")
    top = (rel[presentes].mean() * 100).sort_values(ascending=False).head(10).round(3)
    print(f"\n== {nome}: {len(presentes)} gêneros contaminantes presentes; mediana {frac.median():.2f}% das leituras")
    print("mediana (%) por projeto x classe:\n", tab)
    print("mais abundantes (média %):", top.to_dict())

    y, g = mm.tipo_amostra.values, mm.Project.values
    com = avalia(rel.values, y, g)
    sem_df = G.drop(columns=presentes)
    sem = avalia(relativa(sem_df).values, y, g)
    resultado[nome] = {"generos_contaminantes": presentes, "mediana_pct_leituras": float(frac.median()),
                       "com_contaminantes": com, "sem_contaminantes": sem}
    for k in ["cv", "lopo"]:
        print(f"  {k}: com {[round(v, 3) for v in com[k].values()]}  sem {[round(v, 3) for v in sem[k].values()]}")
    print(f"  acurácia ao prever projeto: com {com['acuracia_projeto']:.3f}  sem {sem['acuracia_projeto']:.3f}")

json.dump(resultado, open(f"{OUT_DIR}/11_contaminantes.json", "w"), indent=1, default=float)
