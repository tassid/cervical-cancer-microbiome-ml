"""Abundância diferencial com projeto no modelo (no espírito do MaAsLin2).

Para cada gênero presente em >= 10% das amostras: transformação CLR (pseudocontagem
0,5) e regressão linear clr ~ classe (referência: controle). Dois modelos:
  - sem projeto (o que o artigo faz, implicitamente)
  - com projeto como efeito fixo (só contrastes dentro do projeto informam a classe)
Correção de Benjamini-Hochberg por contraste. Usa só projetos com mais de uma classe
no modelo com projeto, porque projetos de uma classe só não informam o contraste.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from common import OUT_DIR, ativas, genero, meta

m = meta()
for nome, carregar in ativas():
    G = genero(carregar())
    G = G.loc[:, (G > 0).mean() >= 0.10]
    log = np.log(G + 0.5)
    clr = log.sub(log.mean(axis=1), axis=0)
    mm = m.loc[G.index, ["tipo_amostra", "Project"]].copy()
    multi = mm.groupby("Project").tipo_amostra.nunique()
    linhas = []
    for gname in clr.columns:
        d = mm.assign(y=clr[gname].values)
        dm = d[d.Project.isin(multi[multi > 1].index)]
        f0 = smf.ols('y ~ C(tipo_amostra, Treatment("control"))', d).fit()
        f1 = smf.ols('y ~ C(tipo_amostra, Treatment("control")) + C(Project)', dm).fit()
        for c in ["cancer", "lesion high", "lesion low"]:
            k = f'C(tipo_amostra, Treatment("control"))[T.{c}]'
            linhas.append(dict(genero=gname, contraste=f"{c} vs control",
                               coef_sem_projeto=f0.params[k], p_sem_projeto=f0.pvalues[k],
                               coef_com_projeto=f1.params.get(k, np.nan), p_com_projeto=f1.pvalues.get(k, np.nan)))
    R = pd.DataFrame(linhas)
    for col in ["sem_projeto", "com_projeto"]:
        R[f"q_{col}"] = np.nan
        for c, s in R.groupby("contraste"):
            ok = s[f"p_{col}"].notna()
            R.loc[s.index[ok], f"q_{col}"] = multipletests(s.loc[ok, f"p_{col}"], method="fdr_bh")[1]
    R.to_csv(f"{OUT_DIR}/12_abundancia_com_projeto_{nome}.csv", index=False)
    print(f"\n== {nome}: {G.shape[1]} gêneros testados")
    for c, s in R.groupby("contraste"):
        n0 = (s.q_sem_projeto < 0.05).sum()
        n1 = (s.q_com_projeto < 0.05).sum()
        print(f"{c}: significativos (q<0,05) sem projeto {n0}, com projeto {n1}")
        sig = s[s.q_com_projeto < 0.05].sort_values("coef_com_projeto")
        if len(sig):
            print("   com projeto:", ", ".join(f"{r.genero} ({r.coef_com_projeto:+.2f})" for r in sig.itertuples()))
