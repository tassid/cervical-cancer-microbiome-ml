"""PERMANOVA (Bray-Curtis) separando o quanto é classe clínica e o quanto é projeto.

  - R² da classe sozinha (o que o artigo reporta)
  - R² do projeto sozinho
  - R² da classe ALÉM do projeto, com permutações restritas dentro de cada projeto
"""
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform

from common import OUT_DIR, TABELAS, ativas, meta, relativa

N_PERM = 499
rng = np.random.default_rng(1)


def gower(D):
    A = -0.5 * D ** 2
    n = len(A)
    J = np.eye(n) - np.ones((n, n)) / n
    return J @ A @ J


def hat(X):
    return X @ np.linalg.pinv(X.T @ X) @ X.T


def desenho(*fatores):
    cols = [np.ones((len(fatores[0]), 1))]
    cols += [pd.get_dummies(f, drop_first=True).values.astype(float) for f in fatores]
    return np.hstack(cols)


def marginal(G, completo, reduzido, permuta):
    Hf, Hr = hat(completo), hat(reduzido)
    total = np.trace(G)
    ss_f, ss_r = np.trace(Hf @ G), np.trace(Hr @ G)
    r2 = (ss_f - ss_r) / total
    F = (ss_f - ss_r) / (total - ss_f)
    maiores = 0
    for _ in range(N_PERM):
        p = permuta()
        Gp = G[np.ix_(p, p)]
        sf, sr = np.trace(Hf @ Gp), np.trace(Hr @ Gp)
        maiores += (sf - sr) / (np.trace(Gp) - sf) >= F
    return r2, (maiores + 1) / (N_PERM + 1)


m = meta()
linhas = []
for nome, carregar in ativas():
    df = carregar()
    mm = m.loc[df.index]
    G = gower(squareform(pdist(relativa(df).values, "braycurtis")))
    y, pj = mm.tipo_amostra.values, mm.Project.values
    n = len(y)

    def livre():
        return rng.permutation(n)

    def dentro_do_projeto():
        p = np.arange(n)
        for g in np.unique(pj):
            i = np.where(pj == g)[0]
            p[i] = rng.permutation(i)
        return p

    r2c, pc = marginal(G, desenho(y), desenho(y)[:, :1], livre)
    r2p, pp = marginal(G, desenho(pj), desenho(pj)[:, :1], livre)
    r2cp, pcp = marginal(G, desenho(pj, y), desenho(pj), dentro_do_projeto)
    linhas.append(dict(tabela=nome, n=n, R2_classe=r2c, p_classe=pc, R2_projeto=r2p, p_projeto=pp,
                       R2_classe_alem_do_projeto=r2cp, p_classe_alem_do_projeto=pcp))
    print(linhas[-1])

pd.DataFrame(linhas).to_csv(f"{OUT_DIR}/06_permanova.csv", index=False)
