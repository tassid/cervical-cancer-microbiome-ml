"""De onde vêm os "biomarcadores" do artigo?

Para cada gênero citado (Boruta, LEfSe, heatmap), mostra a abundância média por
projeto|classe e quanto da variação é explicada por projeto vs. classe (eta² em postos).
Também compara a importância de cada gênero num RF que prevê a classe com a
importância num RF que prevê o projeto.
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestClassifier

from common import OUT_DIR, TABELAS, genero, meta, relativa

CITADOS = ["Burkholderia-Caballeronia-Paraburkholderia", "Lactobacillus", "Pseudomonas", "Enterococcus",
           "Brochothrix", "Chloroplast", "Peptostreptococcus", "Rhodococcus", "Ralstonia", "Cupriavidus",
           "Corynebacterium", "Finegoldia", "Fusobacterium", "Porphyromonas", "Staphylococcus", "Bacillus",
           "Halomonas", "Streptococcus", "Wolbachia", "Aeribacillus", "Thermus", "Bacteroides", "Prevotella",
           "Gardnerella", "Sneathia", "Atopobium", "Megasphaera", "Campylobacter"]


def eta2(v, f):
    r = v.rank()
    return r.groupby(f).apply(lambda s: len(s) * (s.mean() - r.mean()) ** 2).sum() / ((r - r.mean()) ** 2).sum()


m = meta()
for nome in ["PAOLA", "TASSI_FIX"]:
    rel = relativa(genero(TABELAS[nome]())) * 100
    mm = m.loc[rel.index]
    chave = mm.Project + "|" + mm.tipo_amostra.str.replace("lesion ", "L")
    presentes = [t for t in CITADOS if t in rel.columns]
    tab = rel[presentes].groupby(chave).mean().T
    tab.round(3).to_csv(f"{OUT_DIR}/04_media_por_projeto_{nome}.csv")

    linhas = []
    for t in presentes:
        top = tab.loc[t].sort_values(ascending=False)
        linhas.append(dict(genero=t, media_geral=rel[t].mean(),
                           grupo_mais_abundante=top.index[0], media_no_grupo=top.iloc[0],
                           fracao_no_projeto_dominante=(rel[t].groupby(mm.Project).sum().max() / rel[t].sum()) if rel[t].sum() else np.nan,
                           eta2_projeto=eta2(rel[t], mm.Project), eta2_classe=eta2(rel[t], mm.tipo_amostra)))
    res = pd.DataFrame(linhas)
    res.to_csv(f"{OUT_DIR}/04_origem_biomarcadores_{nome}.csv", index=False)
    print(f"\n== {nome}\n", res.to_string(index=False, float_format=lambda v: f"{v:.2f}"))

    # importância para classe x importância para projeto (gêneros em >=5% das amostras)
    X = rel.loc[:, (rel > 0).mean() >= 0.05]
    ic = pd.Series(RandomForestClassifier(500, n_jobs=-1, random_state=0).fit(X, mm.tipo_amostra).feature_importances_, X.columns)
    ip = pd.Series(RandomForestClassifier(500, n_jobs=-1, random_state=0).fit(X, mm.Project).feature_importances_, X.columns)
    top20 = ic.sort_values(ascending=False).head(20).index
    imp = pd.DataFrame({"importancia_classe": ic[top20], "importancia_projeto": ip[top20],
                        "eta2_projeto": [eta2(X[g], mm.Project) for g in top20],
                        "eta2_classe": [eta2(X[g], mm.tipo_amostra) for g in top20]})
    imp.to_csv(f"{OUT_DIR}/04_importancia_classe_vs_projeto_{nome}.csv")
    print(f"Spearman importância classe x projeto ({X.shape[1]} gêneros): {spearmanr(ic, ip)[0]:.2f}")
    print(f"Top-20 da classe em que projeto explica mais que classe: {(imp.eta2_projeto > imp.eta2_classe).sum()}/20")
