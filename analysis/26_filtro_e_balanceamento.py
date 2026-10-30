"""Sugestões do Pedro na reunião de 23/10/2026 que ainda faltavam testar.

Tarefa binária câncer x controle, mesmos dados e mesma lógica do 09_forca_bruta.py,
comparando CV aleatória (5 folds) com leave-one-project-out (LOPO).

Parte A, filtro de colunas
  Pedro: excluir colunas com mais de 25% de valores nulos e colunas pouco expressivas ou
  idênticas. Em microbioma o "nulo" é zero (ausência), então a regra vira um filtro de
  prevalência. Testa vários limiares de fração máxima de zeros por gênero:
    sem filtro, 90% (= prevalência >= 10%, o usado hoje), 75%, 50% e 25% (regra do Pedro),
  sempre removendo também colunas constantes e colunas duplicadas.
  O filtro é calculado só nas amostras de treino de cada fold, para o projeto de teste não
  influenciar quais gêneros entram (vazamento).

Parte B, balanceamento
  Pedro: oversampling, undersampling e variações do SMOTE. Testa nenhum, class_weight,
  RandomUnderSampler, SMOTE, BorderlineSMOTE, ADASYN e SMOTETomek, em dois modos:
    global       : reamostra o treino inteiro, como no 09
    por_projeto  : reamostra dentro de cada projeto de treino que tem as duas classes;
                   projetos de uma classe só entram como estão
  O modo por_projeto responde à pergunta da pauta: balancear dentro dos projetos
  multiclasse muda alguma coisa, ou o atalho do projeto continua?

Saídas: results/26_filtro_{TABELA}.csv, results/26_balanceamento_{TABELA}.csv e um resumo
impresso. Uso: DATA_DIR=... python 26_filtro_e_balanceamento.py [TABELA ...]
"""
import sys
import warnings

import numpy as np
import pandas as pd
from imblearn.combine import SMOTETomek
from imblearn.over_sampling import ADASYN, SMOTE, BorderlineSMOTE
from imblearn.under_sampling import RandomUnderSampler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

PROJETOS_PAREADOS = ["P1", "P2", "P19", "P22"]


def modelo(nome, pesos):
    cw = "balanced" if pesos else None
    if nome == "RF":
        return RandomForestClassifier(500, n_jobs=-1, random_state=0, class_weight=cw)
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000, class_weight=cw))


def clr(X):
    log = np.log(X + 0.5)
    return log - log.mean(1, keepdims=True)


def relativa(X):
    s = X.sum(1, keepdims=True)
    s[s == 0] = 1
    return X / s


def prepara(X, prep):
    return clr(X) if prep == "clr" else relativa(X)


def seleciona_colunas(Xtr, max_zeros):
    """Índices das colunas mantidas, calculados só no treino."""
    ok = np.ones(Xtr.shape[1], bool)
    if max_zeros is not None:
        ok &= (Xtr == 0).mean(0) <= max_zeros
    ok &= Xtr.std(0) > 0                         # constantes
    idx = np.where(ok)[0]
    _, unicas = np.unique(Xtr[:, idx].round(12), axis=1, return_index=True)  # duplicadas
    return idx[np.sort(unicas)]


AMOSTRADORES = {
    "nenhum": None,
    "class_weight": None,
    "RandomUnder": lambda k: RandomUnderSampler(random_state=0),
    "SMOTE": lambda k: SMOTE(random_state=0, k_neighbors=k),
    "BorderlineSMOTE": lambda k: BorderlineSMOTE(random_state=0, k_neighbors=k),
    "ADASYN": lambda k: ADASYN(random_state=0, n_neighbors=k),
    "SMOTETomek": lambda k: SMOTETomek(random_state=0, smote=SMOTE(random_state=0, k_neighbors=k)),
}


def reamostra(X, y, g, metodo, modo):
    if AMOSTRADORES.get(metodo) is None:
        return X, y
    if modo == "global":
        k = max(1, min(5, np.bincount(y).min() - 1))
        try:
            return AMOSTRADORES[metodo](k).fit_resample(X, y)
        except (ValueError, RuntimeError):       # já balanceado ou sem vizinhos válidos
            return X, y
    Xs, ys = [], []
    for pj in np.unique(g):
        i = g == pj
        yi = y[i]
        cont = np.bincount(yi, minlength=2)
        if cont.min() >= 2:
            k = max(1, min(5, cont.min() - 1))
            try:
                xr, yr = AMOSTRADORES[metodo](k).fit_resample(X[i], yi)
            except (ValueError, RuntimeError):   # ADASYN/Borderline podem não achar vizinhos
                xr, yr = X[i], yi
        else:
            xr, yr = X[i], yi
        Xs.append(xr)
        ys.append(yr)
    return np.vstack(Xs), np.concatenate(ys)


def splits(y, g, esquema):
    if esquema == "aleatoria":
        return list(StratifiedKFold(5, shuffle=True, random_state=0).split(np.zeros(len(y)), y))
    return [(np.where(g != pj)[0], np.where(g == pj)[0]) for pj in np.unique(g)]


def avalia(X0, y, g, esquema, nome_modelo, prep="clr", max_zeros=0.90, metodo="nenhum", modo="global"):
    p = np.full(len(y), np.nan)
    ncols = []
    for tr, te in splits(y, g, esquema):
        if len(set(y[tr])) < 2:
            continue
        cols = seleciona_colunas(X0[tr], max_zeros)
        ncols.append(len(cols))
        if len(cols) < 2:            # filtro estrito demais: não sobra gênero para modelar
            continue
        Xtr, Xte = prepara(X0[tr][:, cols], prep), prepara(X0[te][:, cols], prep)
        Xtr, ytr = reamostra(Xtr, y[tr], g[tr], metodo, modo)
        m = modelo(nome_modelo, pesos=(metodo == "class_weight"))
        p[te] = m.fit(Xtr, ytr).predict_proba(Xte)[:, 1]
    ok = ~np.isnan(p)
    n = int(np.median(ncols)) if ncols else 0
    if len(set(y[ok])) < 2:
        return {"AUC": np.nan, "n_generos": n}
    r = {"AUC": roc_auc_score(y[ok], p[ok]), "n_generos": n}
    if esquema == "lopo":
        for pj in PROJETOS_PAREADOS:
            i = (g == pj) & ok
            if len(set(y[i])) == 2:
                r[pj] = roc_auc_score(y[i], p[i])
    return r


def dados(nome):
    from common import TABELAS, meta
    df = TABELAS[nome]()
    m = meta().loc[df.index]
    sel = m.tipo_amostra.isin(["cancer", "control"]).values
    X0 = df.values[sel].astype(float)
    y = (m.tipo_amostra.values[sel] == "cancer").astype(int)
    g = m.Project.values[sel]
    return X0, y, g


def mostra(r):
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)


def parte_a(X0, y, g, nome):
    linhas = []
    for max_zeros, rotulo in [(None, "sem filtro"), (0.90, "prev>=10%"), (0.75, "prev>=25%"),
                              (0.50, "prev>=50%"), (0.25, "<=25% zeros (Pedro)")]:
        for prep in ["clr", "rel"]:
            for mod in ["RF", "LogReg"]:
                for esquema in ["aleatoria", "lopo"]:
                    r = avalia(X0, y, g, esquema, mod, prep=prep, max_zeros=max_zeros)
                    r.update(tabela=nome, filtro=rotulo, prep=prep, modelo=mod, esquema=esquema)
                    linhas.append(r)
                    mostra(r)
    return pd.DataFrame(linhas)


def parte_b(X0, y, g, nome):
    linhas = []
    for metodo in AMOSTRADORES:
        for modo in (["global"] if metodo in ("nenhum", "class_weight") else ["global", "por_projeto"]):
            for mod in ["RF", "LogReg"]:
                for esquema in ["aleatoria", "lopo"]:
                    r = avalia(X0, y, g, esquema, mod, metodo=metodo, modo=modo)
                    r.update(tabela=nome, balanceamento=metodo, modo=modo, modelo=mod, esquema=esquema)
                    linhas.append(r)
                    mostra(r)
    return pd.DataFrame(linhas)


def resumo(a, b):
    print("\n== Parte A: filtro de colunas (mediana de AUC entre RF/LogReg e CLR/relativa) ==")
    print(a.groupby(["filtro", "esquema"]).agg(AUC=("AUC", "median"), generos=("n_generos", "median"))
          .unstack("esquema").round(3).to_string())
    print("\n== Parte B: balanceamento (mediana de AUC entre RF/LogReg) ==")
    print(b.groupby(["balanceamento", "modo", "esquema"]).AUC.median().unstack("esquema").round(3).to_string())


def roda(nome):
    from common import OUT_DIR
    X0, y, g = dados(nome)
    a, b = parte_a(X0, y, g, nome), parte_b(X0, y, g, nome)
    a.to_csv(f"{OUT_DIR}/26_filtro_{nome}.csv", index=False)
    b.to_csv(f"{OUT_DIR}/26_balanceamento_{nome}.csv", index=False)
    resumo(a, b)


if __name__ == "__main__":
    from common import ativas
    for nome in (sys.argv[1:] or [n for n, _ in ativas()]):
        roda(nome)
