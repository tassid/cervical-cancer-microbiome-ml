"""Curva de aprendizado de câncer x controle sem o P22 (lote confundido com a classe).

Estudos mistos: P1, P2 e P19. Para cada um deixado de fora, treina com frações dos outros
mistos (mais N pareado) ou com os mistos completos mais frações dos estudos de uma classe
(mais N não pareado), e mede o AUC no estudo deixado de fora. O P22 não entra nem no treino
nem no teste.
"""
import numpy as np
import pandas as pd

from common import OUT_DIR, ativas, genero, meta
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

MISTOS = ["P1", "P2", "P19"]
REPS = 10


def ajustar(mod, X, y):
    if mod == "RF":
        return RandomForestClassifier(500, n_jobs=-1, random_state=0, class_weight="balanced_subsample",
                                      min_samples_leaf=2).fit(X, y)
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.1, class_weight="balanced", max_iter=5000)).fit(X, y)


def subamostra(idx, estratos, frac, rng):
    out = []
    for _, g in pd.Series(idx).groupby(estratos[idx]):
        out.extend(rng.choice(g.values, max(1, int(round(frac * len(g)))), replace=False))
    return np.array(sorted(out))


m = meta()
res = []
for nome, carregar in ativas():
    G = genero(carregar())
    G = G.loc[:, (G > 0).mean() >= 0.05]
    mm = m.loc[G.index]
    pj, cl = mm.Project.values, mm.tipo_amostra.values
    lg = np.log(G + 0.5)
    Xs = {"RF": G.div(G.sum(axis=1), axis=0).values, "LogReg": lg.sub(lg.mean(axis=1), axis=0).values}
    y = (cl == "cancer").astype(int)
    estr = np.array([f"{a}|{b}" for a, b in zip(pj, cl)])
    base = np.isin(cl, ["cancer", "control"]) & ~((pj == "P10") & (cl == "cancer")) & (pj != "P22")
    im = np.where(base & np.isin(pj, MISTOS))[0]
    iu = np.where(base & ~np.isin(pj, MISTOS))[0]
    for T in MISTOS:
        te = im[pj[im] == T]
        trA = im[pj[im] != T]
        for mod in ["RF", "LogReg"]:
            for fonte, fr in [("estudos mistos (pareados)", [0.25, 0.5, 0.75, 1.0]),
                              ("+ estudos de uma classe", [0.25, 0.5, 1.0])]:
                for f in fr:
                    for r in range(REPS if f < 1 else 1):
                        rng = np.random.default_rng(10 * r + int(100 * f))
                        if fonte.startswith("estudos"):
                            tr = subamostra(trA, estr, f, rng) if f < 1 else trA
                        else:
                            tr = np.concatenate([trA, subamostra(iu, estr, f, rng) if f < 1 else iu])
                        if len(np.unique(y[tr])) < 2:
                            continue
                        p = ajustar(mod, Xs[mod][tr], y[tr]).predict_proba(Xs[mod][te])[:, 1]
                        res.append(dict(tabela=nome, modelo=mod, estudo_teste=T, fonte=fonte, fracao=f,
                                        n_treino=len(tr), auc=roc_auc_score(y[te], p)))
    R = pd.DataFrame([r for r in res if r["tabela"] == nome])
    print(f"\n== {nome}")
    print(R.groupby(["modelo", "fonte", "fracao"]).agg(n=("n_treino", "mean"), auc=("auc", "mean")).round(3).to_string())
    print("   por estudo de teste (N máximo de cada fonte):")
    mx = R[R.fracao == 1.0]
    print(mx.pivot_table(index=["modelo", "estudo_teste"], columns="fonte", values="auc").round(2).to_string())

pd.DataFrame(res).to_csv(f"{OUT_DIR}/22c_curva_sem_P22.csv", index=False)
