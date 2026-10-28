"""Meta-análise por projeto: o efeito de cada gênero calculado dentro de cada estudo e depois combinado.

Para cada contraste e cada projeto que tem as duas classes (mínimo de 4 amostras em
cada), calcula o g de Hedges na abundância CLR do gênero e no índice de Shannon. Os
efeitos por projeto são combinados com modelo de efeitos aleatórios
(DerSimonian-Laird), que reporta também a heterogeneidade entre estudos (I²).
Esse é o desenho padrão quando os estudos têm protocolos diferentes.
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

from common import OUT_DIR, ativas, genero, meta

GENEROS = ["Lactobacillus", "Gardnerella", "Prevotella", "Fusobacterium", "Porphyromonas", "Bacteroides",
           "Peptostreptococcus", "Streptococcus", "Sneathia", "Atopobium", "Megasphaera", "Dialister",
           "Anaerococcus", "Peptoniphilus", "Campylobacter", "Pseudomonas", "Ureaplasma", "Finegoldia"]
COMPARACOES = {"cancer vs control": "cancer", "HSIL vs control": "lesion high", "LSIL vs control": "lesion low"}


def hedges_g(a, b):
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1)) / (n1 + n2 - 2))
    if sp == 0:
        return np.nan, np.nan
    d = (a.mean() - b.mean()) / sp
    J = 1 - 3 / (4 * (n1 + n2) - 9)
    g = J * d
    v = (n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2))
    return g, v


def dersimonian_laird(g, v):
    w = 1 / v
    gf = np.sum(w * g) / np.sum(w)
    Q = np.sum(w * (g - gf) ** 2)
    k = len(g)
    C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0, (Q - (k - 1)) / C) if k > 1 else 0
    wr = 1 / (v + tau2)
    gr = np.sum(wr * g) / np.sum(wr)
    se = np.sqrt(1 / np.sum(wr))
    I2 = max(0, (Q - (k - 1)) / Q) * 100 if Q > 0 else 0
    return gr, gr - 1.96 * se, gr + 1.96 * se, 2 * (1 - norm.cdf(abs(gr / se))), I2


m = meta()
for nome, carregar in ativas():
    G = genero(carregar())
    log = np.log(G + 0.5)
    clr = log.sub(log.mean(axis=1), axis=0)
    rel = G.div(G.sum(axis=1), axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        shannon = -(rel * np.log(rel.where(rel > 0, 1))).sum(axis=1)
    feats = {g: clr[g] for g in GENEROS if g in clr.columns}
    feats["Shannon"] = shannon
    mm = m.loc[G.index]
    por_projeto, combinado = [], []
    for comp, classe in COMPARACOES.items():
        for f, x in feats.items():
            gs, vs, pjs = [], [], []
            for pj, s in mm.groupby("Project"):
                a = x[s.index[s.tipo_amostra == classe]]
                b = x[s.index[s.tipo_amostra == "control"]]
                if len(a) >= 4 and len(b) >= 4:
                    g, v = hedges_g(a, b)
                    if not np.isnan(g):
                        gs.append(g); vs.append(v); pjs.append(pj)
                        por_projeto.append(dict(contraste=comp, variavel=f, projeto=pj, n_caso=len(a), n_controle=len(b), g=g, var=v))
            if len(gs) >= 2:
                gr, lo, hi, p, I2 = dersimonian_laird(np.array(gs), np.array(vs))
                mesma_direcao = int(max((np.array(gs) > 0).sum(), (np.array(gs) < 0).sum()))
                combinado.append(dict(contraste=comp, variavel=f, k_projetos=len(gs), projetos=",".join(pjs),
                                      g_combinado=gr, ic95_inf=lo, ic95_sup=hi, p=p, I2=I2,
                                      mesma_direcao=f"{mesma_direcao}/{len(gs)}"))
    pd.DataFrame(por_projeto).to_csv(f"{OUT_DIR}/13_meta_por_projeto_{nome}.csv", index=False)
    C = pd.DataFrame(combinado)
    C.to_csv(f"{OUT_DIR}/13_meta_combinado_{nome}.csv", index=False)
    print(f"\n== {nome}")
    with pd.option_context("display.width", 220):
        for comp, s in C.groupby("contraste"):
            print(f"-- {comp}")
            print(s.drop(columns="contraste").sort_values("p").to_string(index=False, float_format=lambda v: f"{v:.3g}"))
