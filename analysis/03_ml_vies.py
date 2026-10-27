"""Random Forest: o desempenho vem do microbioma ou do projeto de origem?

Esquemas avaliados (4 classes, abundância relativa por gênero):
  1. avaliação no próprio treino (o que reproduz AUC ~1 do artigo)
  2. CV estratificada aleatória de 10 folds (o padrão de meta-análise)
  3. linha de base "só projeto": RF que recebe apenas o ID do projeto, sem nenhuma bactéria
  4. leave-one-project-out (LOPO): treina sem o projeto, testa nele
  5. controle negativo: prever o projeto a partir da composição
  6. CV dentro de cada projeto multiclasse (o único teste sem confusão projeto x classe)
  7. AUC usando só a profundidade de leitura, dentro de cada projeto (detecta lote dentro do projeto)
"""
import json
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

from common import CLASSES, OUT_DIR, TABELAS, meta, relativa


def rf():
    return RandomForestClassifier(n_estimators=500, n_jobs=-1, random_state=42)


def auc_por_classe(y, P, classes=CLASSES):
    out = {}
    for i, c in enumerate(classes):
        yb = (y == c).astype(int)
        out[c] = roc_auc_score(yb, P[:, i]) if 0 < yb.sum() < len(yb) else None
    return out


def cv_proba(X, y, splits, classes=CLASSES):
    P = np.zeros((len(y), len(classes)))
    for tr, te in splits:
        c = rf().fit(X[tr], y[tr])
        P[np.ix_(te, [classes.index(k) for k in c.classes_])] = c.predict_proba(X[te])
    return P


def roda(nome):
    df = TABELAS[nome]()
    m = meta().loc[df.index]
    X = relativa(df).values
    y, g = m.tipo_amostra.values, m.Project.values
    skf = list(StratifiedKFold(10, shuffle=True, random_state=42).split(X, y))
    R = {"tabela": nome, "n": len(y)}

    R["treino_no_treino"] = auc_por_classe(y, rf().fit(X, y).predict_proba(X))

    P = cv_proba(X, y, skf)
    R["cv_aleatoria"] = auc_por_classe(y, P)
    R["cv_aleatoria_acc_balanceada"] = balanced_accuracy_score(y, np.array(CLASSES)[P.argmax(1)])

    G = pd.get_dummies(g).values.astype(float)
    R["so_projeto"] = auc_por_classe(y, cv_proba(G, y, skf))

    lopo = [(np.where(g != p)[0], np.where(g == p)[0]) for p in np.unique(g)]
    P3 = cv_proba(X, y, lopo)
    R["lopo"] = auc_por_classe(y, P3)
    R["lopo_acc_balanceada"] = balanced_accuracy_score(y, np.array(CLASSES)[P3.argmax(1)])

    pp = np.empty(len(g), dtype=object)
    for tr, te in StratifiedKFold(10, shuffle=True, random_state=42).split(X, g):
        pp[te] = rf().fit(X[tr], g[tr]).predict(X[te])
    R["acuracia_prever_projeto"] = float((pp == g).mean())
    R["acuracia_prever_projeto_acaso"] = float(pd.Series(g).value_counts(normalize=True).max())

    R["dentro_do_projeto"] = {}
    R["so_profundidade_dentro_do_projeto"] = {}
    prof = df.sum(axis=1).values
    for pj in np.unique(g):
        idx = np.where(g == pj)[0]
        vc = pd.Series(y[idx]).value_counts()
        ok = sorted(vc[vc >= 5].index)
        if len(ok) < 2:
            continue
        sel = idx[np.isin(y[idx], ok)]
        k = int(min(5, vc[ok].min()))
        Pp = cv_proba(X[sel], y[sel], list(StratifiedKFold(k, shuffle=True, random_state=42).split(X[sel], y[sel])), ok)
        R["dentro_do_projeto"][pj] = {**auc_por_classe(y[sel], Pp, ok), "n": {c: int(vc[c]) for c in ok}}
        if "control" in ok:
            R["so_profundidade_dentro_do_projeto"][pj] = {
                f"{c} vs control": roc_auc_score((y[sel][np.isin(y[sel], [c, "control"])] == c).astype(int),
                                                 prof[sel][np.isin(y[sel], [c, "control"])])
                for c in ok if c != "control"}

    json.dump(R, open(f"{OUT_DIR}/03_ml_{nome}.json", "w"), indent=1, default=float)
    print(json.dumps(R, indent=1, default=lambda v: round(float(v), 3)))


if __name__ == "__main__":
    for nome in (sys.argv[1:] or ["PAOLA", "TASSI_FIX"]):
        roda(nome)
