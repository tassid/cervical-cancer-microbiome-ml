"""Auditoria do desenho: quanto a classe clínica está misturada com projeto, região e profundidade."""
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, kruskal

from common import OUT_DIR, REGIAO, TABELAS, ativas, meta


def cramer(ct):
    chi = chi2_contingency(ct)[0]
    return np.sqrt(chi / (ct.values.sum() * (min(ct.shape) - 1)))


m = meta()
linhas = []
for nome, carregar in ativas():
    df = carregar()
    mm = m.loc[df.index].copy()
    mm["regiao"] = mm.Project.map(REGIAO)
    mm["leituras"] = df.sum(axis=1)
    cancer = mm[mm.tipo_amostra == "cancer"]
    linhas.append({
        "tabela": nome, "amostras": len(df), "features": df.shape[1],
        "cramer_classe_projeto": cramer(pd.crosstab(mm.tipo_amostra, mm.Project)),
        "cramer_classe_pais": cramer(pd.crosstab(mm.tipo_amostra, mm.Location)),
        "cramer_classe_regiao": cramer(pd.crosstab(mm.tipo_amostra, mm.regiao)),
        "cancer_de_projetos_so_cancer": f"{cancer.Project.isin(['P1', 'P6', 'P9', 'P16']).sum()}/{len(cancer)}",
        "p_kruskal_leituras_por_classe": kruskal(*[g.leituras for _, g in mm.groupby("tipo_amostra")]).pvalue,
        **{f"leituras_mediana_{c}": mm[mm.tipo_amostra == c].leituras.median() for c in sorted(mm.tipo_amostra.unique())},
    })
    print(f"\n== {nome}")
    print(pd.crosstab(mm.Project, mm.tipo_amostra, margins=True))

res = pd.DataFrame(linhas)
print(res.T)
res.to_csv(f"{OUT_DIR}/01_auditoria.csv", index=False)
