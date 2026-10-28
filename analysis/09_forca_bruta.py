"""Busca exaustiva de classificadores (sugestão do Pedro / abordagem do trabalho do Berry).

Tarefa binária câncer x controle. Para cada combinação de pré-processamento
(abundância relativa, CLR, presença/ausência; gêneros em >=10% das amostras),
classificador e SMOTE, compara CV aleatória (5 folds) com leave-one-project-out.
No LOPO também reporta o AUC dentro de cada projeto que tem as duas classes.
"""
import sys
import warnings

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

from common import OUT_DIR, TABELAS, ativas, meta

warnings.filterwarnings("ignore")

MODELOS = {
    "RF": lambda: RandomForestClassifier(500, n_jobs=-1, random_state=0, class_weight="balanced"),
    "ExtraTrees": lambda: ExtraTreesClassifier(500, n_jobs=-1, random_state=0, class_weight="balanced"),
    "XGBoost": lambda: XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.1, n_jobs=-1, verbosity=0),
    "HistGB": lambda: HistGradientBoostingClassifier(random_state=0),
    "LogReg": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000, class_weight="balanced")),
    "SVM": lambda: make_pipeline(StandardScaler(), SVC(C=1, probability=True, class_weight="balanced")),
    "kNN": lambda: make_pipeline(StandardScaler(), KNeighborsClassifier(15)),
    "NaiveBayes": lambda: GaussianNB(),
}


def prepara(tipo, X):
    if tipo == "rel":
        return X / X.sum(1, keepdims=True)
    if tipo == "clr":
        log = np.log(X + 0.5)
        return log - log.mean(1, keepdims=True)
    return (X > 0).astype(float)


def avalia(X, y, g, modelo, esquema, smote):
    p = np.full(len(y), np.nan)
    if esquema == "aleatoria":
        splits = StratifiedKFold(5, shuffle=True, random_state=0).split(X, y)
    else:
        splits = [(np.where(g != pj)[0], np.where(g == pj)[0]) for pj in np.unique(g)]
    for tr, te in splits:
        Xtr, ytr = X[tr], y[tr]
        if len(set(ytr)) < 2:
            continue
        if smote:
            Xtr, ytr = SMOTE(random_state=0).fit_resample(Xtr, ytr)
        p[te] = MODELOS[modelo]().fit(Xtr, ytr).predict_proba(X[te])[:, 1]
    ok = ~np.isnan(p)
    r = {"AUC": roc_auc_score(y[ok], p[ok])}
    if esquema == "lopo":
        for pj in ["P1", "P2", "P19", "P22"]:
            i = (g == pj) & ok
            if len(set(y[i])) == 2:
                r[pj] = roc_auc_score(y[i], p[i])
    return r


def roda(nome):
    df = TABELAS[nome]()
    m = meta().loc[df.index]
    sel = m.tipo_amostra.isin(["cancer", "control"]).values
    X0 = df.values[sel].astype(float)
    y = (m.tipo_amostra.values[sel] == "cancer").astype(int)
    g = m.Project.values[sel]
    X0 = X0[:, (X0 > 0).mean(0) >= 0.10]
    linhas = []
    for tipo in ["rel", "clr", "pa"]:
        X = prepara(tipo, X0)
        for modelo in MODELOS:
            for esquema in ["aleatoria", "lopo"]:
                for smote in ([False, True] if modelo in ("RF", "LogReg") else [False]):
                    r = avalia(X, y, g, modelo, esquema, smote)
                    r.update(tabela=nome, prep=tipo, modelo=modelo, esquema=esquema, smote=smote)
                    linhas.append(r)
                    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    pd.DataFrame(linhas).to_csv(f"{OUT_DIR}/09_forca_bruta_{nome}.csv", index=False)


if __name__ == "__main__":
    for nome in (sys.argv[1:] or [n for n, _ in ativas()]):
        roda(nome)
