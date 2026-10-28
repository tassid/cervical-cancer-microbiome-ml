"""Diversidade alfa (riqueza observada e Shannon) com e sem ajuste por projeto.

O artigo compara as classes juntando todos os projetos. Aqui repetimos isso e,
em seguida, (a) ajustamos um modelo linear com projeto como efeito fixo e
(b) comparamos câncer x controle dentro de cada projeto que tem as duas classes.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import kruskal, mannwhitneyu

from common import OUT_DIR, TABELAS, ativas, meta

RAREFACAO = 5000
rng = np.random.default_rng(42)


def rarefaz(df, d):
    df = df[df.sum(axis=1) >= d]
    X = df.values.astype(int)
    out = np.zeros_like(X)
    for i, row in enumerate(X):
        sorteio = rng.choice(np.repeat(np.arange(len(row)), row), d, replace=False)
        out[i] = np.bincount(sorteio, minlength=len(row))
    return pd.DataFrame(out, index=df.index, columns=df.columns)


def alfa(df):
    p = df.div(df.sum(axis=1), axis=0).values
    with np.errstate(divide="ignore", invalid="ignore"):
        sh = -np.nansum(np.where(p > 0, p * np.log(p), 0), axis=1)
    return pd.DataFrame({"obs": (df > 0).sum(axis=1), "shannon": sh}, index=df.index)


m = meta()
linhas = []
for nome, carregar in ativas():
    a = alfa(rarefaz(carregar(), RAREFACAO)).join(m[["tipo_amostra", "Project"]])
    a.to_csv(f"{OUT_DIR}/02_alfa_{nome}.csv")
    multi = a.groupby("Project").tipo_amostra.nunique()
    aa = a[a.Project.isin(multi[multi > 1].index)].copy()
    for met in ["obs", "shannon"]:
        aa["y"] = np.log1p(aa[met]) if met == "obs" else aa[met]
        p_kw = kruskal(*[g[met] for _, g in a.groupby("tipo_amostra")]).pvalue
        f0 = smf.ols('y ~ C(tipo_amostra, Treatment("control"))', aa).fit()
        f1 = smf.ols('y ~ C(tipo_amostra, Treatment("control")) + C(Project)', aa).fit()
        for c in ["cancer", "lesion high", "lesion low"]:
            k = f'C(tipo_amostra, Treatment("control"))[T.{c}]'
            linhas.append(dict(tabela=nome, metrica=met, comparacao=f"{c} vs control", escopo="todos (Kruskal global p)",
                               efeito=np.nan, p=p_kw))
            linhas.append(dict(tabela=nome, metrica=met, comparacao=f"{c} vs control", escopo="modelo SEM projeto",
                               efeito=f0.params[k], p=f0.pvalues[k]))
            linhas.append(dict(tabela=nome, metrica=met, comparacao=f"{c} vs control", escopo="modelo COM projeto",
                               efeito=f1.params[k], p=f1.pvalues[k]))
        for pj in ["P1", "P2", "P19", "P22"]:
            s = a[a.Project == pj]
            c1, c0 = s[s.tipo_amostra == "cancer"][met], s[s.tipo_amostra == "control"][met]
            if len(c1) >= 3 and len(c0) >= 3:
                linhas.append(dict(tabela=nome, metrica=met, comparacao="cancer vs control", escopo=f"dentro de {pj} (n={len(c1)}/{len(c0)})",
                                   efeito=c1.median() - c0.median(), p=mannwhitneyu(c1, c0).pvalue))

res = pd.DataFrame(linhas).drop_duplicates()
res.to_csv(f"{OUT_DIR}/02_alfa_efeitos.csv", index=False)
with pd.option_context("display.width", 200, "display.max_rows", 500):
    print(res[res.comparacao.str.startswith("cancer")].to_string(index=False, float_format=lambda v: f"{v:.3g}"))
