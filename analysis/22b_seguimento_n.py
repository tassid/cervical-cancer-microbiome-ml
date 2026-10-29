"""Seguimento do 22: por que os estudos de uma classe ajudam no P19?

1. Cenários sem o P22 no treino. O P22 tem câncer e controle em corridas diferentes, então
   ensina um sinal invertido; ele pode estar derrubando o cenário "só mistos".
2. O que os estudos de uma classe ensinam: AUC de um único gênero (Lactobacillus, mais
   baixo no câncer) e de um índice simples de disbiose dentro de cada estudo misto, comparado
   com o modelo treinado só em estudos de uma classe. Se Lactobacillus sozinho chega perto,
   o que se ganha com esses estudos é a regra "menos Lactobacillus = câncer", conhecida e sem
   necessidade de machine learning.
3. Importância dos gêneros no modelo treinado só com estudos de uma classe.
4. Poder: N pareado por grupo para detectar efeitos do tamanho dos que a meta-análise achou
   (g de Hedges 0,2 a 0,5), comparado com o N pareado disponível hoje.
"""
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from common import OUT_DIR, ativas, genero, meta

MISTOS = ["P1", "P2", "P19", "P22"]


def preparar(G):
    G = G.loc[:, (G > 0).mean() >= 0.05]
    rel = G.div(G.sum(axis=1), axis=0)
    lg = np.log(G + 0.5)
    return rel, lg.sub(lg.mean(axis=1), axis=0)


def ajustar(mod, X, tr, y):
    if mod == "RF":
        return RandomForestClassifier(500, n_jobs=-1, random_state=0, class_weight="balanced_subsample",
                                      min_samples_leaf=2).fit(X[tr], y[tr])
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.1, class_weight="balanced", max_iter=5000)).fit(X[tr], y[tr])


m = meta()
linhas, simples, imp = [], [], []
for nome, carregar in ativas():
    G = genero(carregar())
    mm = m.loc[G.index]
    pj, cl = mm.Project.values, mm.tipo_amostra.values
    rel, clr = preparar(G)
    Xs = {"RF": rel.values, "LogReg": clr.values}
    y = (cl == "cancer").astype(int)
    base = np.isin(cl, ["cancer", "control"]) & ~((pj == "P10") & (cl == "cancer"))
    im = np.where(base & np.isin(pj, MISTOS))[0]
    iu = np.where(base & ~np.isin(pj, MISTOS))[0]
    print(f"\n== {nome}")

    # 1. sem P22 no treino
    for T in ["P1", "P2", "P19"]:
        te = im[pj[im] == T]
        A = im[(pj[im] != T) & (pj[im] != "P22")]
        cen = {"A_so_mistos_sem_P22": A, "B_mistos_sem_P22_mais_uma_classe": np.concatenate([A, iu]),
               "C_so_uma_classe": iu}
        for mod in ["RF", "LogReg"]:
            r = dict(tabela=nome, modelo=mod, estudo_teste=T, n_controles_teste=int((y[te] == 0).sum()))
            for k, tr in cen.items():
                c = ajustar(mod, Xs[mod], tr, y)
                r[k] = roc_auc_score(y[te], c.predict_proba(Xs[mod][te])[:, 1])
                r["n_" + k[0]] = len(tr)
            linhas.append(r)
            print(f"   teste {T:>3} {mod:6}: A(sem P22)={r['A_so_mistos_sem_P22']:.2f} (N={r['n_A']})  "
                  f"B(sem P22)={r['B_mistos_sem_P22_mais_uma_classe']:.2f}  C={r['C_so_uma_classe']:.2f}")

    # 2. regras simples dentro de cada estudo misto
    lacto = rel["Lactobacillus"].values if "Lactobacillus" in rel else np.zeros(len(rel))
    shannon = -(rel.values * np.log(np.where(rel.values > 0, rel.values, 1))).sum(axis=1)
    for T in MISTOS:
        te = im[pj[im] == T]
        simples.append(dict(tabela=nome, estudo=T, n_cancer=int(y[te].sum()), n_controle=int((y[te] == 0).sum()),
                            auc_menos_lactobacillus=roc_auc_score(y[te], -lacto[te]),
                            auc_shannon=roc_auc_score(y[te], shannon[te])))
    S = pd.DataFrame([s for s in simples if s["tabela"] == nome])
    print("   regras simples dentro de cada estudo misto:")
    print(S.round(2).to_string(index=False))

    # 3. o que o modelo só-uma-classe usa
    rf = ajustar("RF", Xs["RF"], iu, y)
    top = pd.Series(rf.feature_importances_, index=rel.columns).nlargest(10)
    for g, v in top.items():
        imp.append(dict(tabela=nome, genero=g, importancia=v,
                        media_cancer_uma_classe=100 * rel.iloc[iu][y[iu] == 1][g].mean(),
                        media_controle_uma_classe=100 * rel.iloc[iu][y[iu] == 0][g].mean()))
    print("   gêneros mais importantes no modelo treinado só com estudos de uma classe:")
    print(pd.DataFrame([i for i in imp if i["tabela"] == nome]).round(3).to_string(index=False))

# 4. poder (teste t de duas amostras, alfa 0,05 bilateral, poder 80%)
za, zb = norm.ppf(0.975), norm.ppf(0.8)
pod = pd.DataFrame([dict(g=g, n_por_grupo_80pct=int(np.ceil(2 * (za + zb) ** 2 / g ** 2))) for g in [0.2, 0.3, 0.35, 0.5]])
print("\n   N por grupo (pareado, mesmo estudo) para 80% de poder:")
print(pod.to_string(index=False))

pd.DataFrame(linhas).to_csv(f"{OUT_DIR}/22b_cenarios_sem_P22.csv", index=False)
pd.DataFrame(simples).to_csv(f"{OUT_DIR}/22b_regras_simples.csv", index=False)
pd.DataFrame(imp).to_csv(f"{OUT_DIR}/22b_importancia_so_uma_classe.csv", index=False)
pod.to_csv(f"{OUT_DIR}/22b_poder.csv", index=False)
