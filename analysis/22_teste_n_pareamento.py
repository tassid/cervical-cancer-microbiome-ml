"""Os estudos de uma classe só ajudam ou atrapalham? (dúvida da Paola sobre N e pareamento)

Argumento a testar: tirar o efeito do projeto diminui o N, e artigos de biomarcador de câncer
precisam de N grande e de casos e controles pareados; por isso entram estudos só de câncer
(P6, P9, P16) ou só de controle (P21).

Comparação câncer x controle. Estudos "mistos" têm os dois grupos (P1, P2, P19, P22).
Estudos "de uma classe" têm só um dos lados para esta comparação:
  câncer sem controle: P6, P9, P16 (e o único câncer do P10 é descartado)
  controle sem câncer: P10, P14, P21 (só os controles; lesões ficam fora desta comparação)

1. N efetivo: quantas amostras vêm de estudos em que a comparação existe.
2. Cenários de treino, sempre testando num estudo misto deixado de fora:
     A. só mistos;
     B. mistos + estudos de uma classe (o desenho do artigo);
     C. só estudos de uma classe ("pareamento entre estudos": câncer de um laboratório,
        controle de outro);
     D. como B, mas subamostrado para o mesmo N de A (separa o efeito do N do efeito da composição).
3. Curva de aprendizado: o AUC no estudo novo sobe com o N? Adiciona N de duas fontes:
   mais amostras de estudos mistos (frações de A) ou mais estudos de uma classe (frações de B - A).
   Também para HSIL x controle (mistos: P10, P14, P19, P2).
4. Embaralhamento dentro do estudo: troca aleatoriamente os rótulos dentro de cada estudo
   (estudos de uma classe ficam iguais) e repete a CV aleatória do artigo. Se o AUC continuar
   alto, ele vem de qual estudo a amostra é, não da doença.

Modelos: Random Forest (abundância relativa) e regressão logística (CLR), os dois melhores
da busca exaustiva (09). Gêneros em >= 5% das amostras.
"""
import json
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from common import CLASSES, OUT_DIR, ativas, genero, meta

warnings.filterwarnings("ignore")
MISTOS = {"cancer": ["P1", "P2", "P19", "P22"], "lesion high": ["P10", "P14", "P19", "P2"]}
REPS = 10
N_PERM = 10


def modelos():
    return {
        "RF": lambda: RandomForestClassifier(500, n_jobs=-1, random_state=0, class_weight="balanced_subsample",
                                             min_samples_leaf=2),
        "LogReg": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.1, class_weight="balanced",
                                                                             max_iter=5000)),
    }


def preparar(G):
    G = G.loc[:, (G > 0).mean() >= 0.05]
    rel = G.div(G.sum(axis=1), axis=0)
    lg = np.log(G + 0.5)
    clr = lg.sub(lg.mean(axis=1), axis=0)
    return {"RF": rel.values, "LogReg": clr.values}


def auc_teste(nome_mod, Xs, tr, te, y):
    if len(np.unique(y[tr])) < 2 or len(np.unique(y[te])) < 2:
        return np.nan
    mod = modelos()[nome_mod]().fit(Xs[nome_mod][tr], y[tr])
    return roc_auc_score(y[te], mod.predict_proba(Xs[nome_mod][te])[:, 1])


def subamostra(idx, estratos, frac, rng):
    """Subamostra estratificada (por estudo x classe) de uma lista de índices."""
    out = []
    for _, g in pd.Series(idx).groupby(estratos[idx]):
        k = max(1, int(round(frac * len(g))))
        out.extend(rng.choice(g.values, k, replace=False))
    return np.array(sorted(out))


m = meta()
res_cen, res_curva, res_perm, res_n = [], [], [], []
for nome, carregar in ativas():
    G = genero(carregar())
    mm = m.loc[G.index]
    pj, cl = mm.Project.values, mm.tipo_amostra.values
    Xs = preparar(G)
    estr = np.array([f"{a}|{b}" for a, b in zip(pj, cl)])
    print(f"\n==================== {nome}: {len(G)} amostras")

    # ---------------------------------------------------------------- 1. N efetivo
    caso, mistos = "cancer", MISTOS["cancer"]
    no_contraste = np.isin(cl, ["cancer", "control"]) & ~((pj == "P10") & (cl == "cancer"))
    em_misto = np.isin(pj, mistos)
    for c in ["cancer", "control"]:
        tot = int(((cl == c) & no_contraste).sum())
        ef = int(((cl == c) & no_contraste & em_misto).sum())
        res_n.append(dict(tabela=nome, classe=c, total=tot, em_estudos_mistos=ef, de_estudos_de_uma_classe=tot - ef,
                          pct_uma_classe=100 * (tot - ef) / tot))
    print(pd.DataFrame([r for r in res_n if r["tabela"] == nome]).to_string(index=False))

    # ---------------------------------------------------------------- 2. cenários (câncer)
    y = (cl == "cancer").astype(int)
    idx_m = np.where(no_contraste & em_misto)[0]
    idx_u = np.where(no_contraste & ~em_misto)[0]
    rng = np.random.default_rng(1)
    for T in mistos:
        te = idx_m[pj[idx_m] == T]
        trA = idx_m[pj[idx_m] != T]
        trB = np.concatenate([trA, idx_u])
        for mod in modelos():
            linha = dict(tabela=nome, modelo=mod, estudo_teste=T, n_teste=len(te),
                         n_A=len(trA), n_B=len(trB), n_C=len(idx_u))
            linha["A_so_mistos"] = auc_teste(mod, Xs, trA, te, y)
            linha["B_mistos_mais_uma_classe"] = auc_teste(mod, Xs, trB, te, y)
            linha["C_so_uma_classe"] = auc_teste(mod, Xs, idx_u, te, y)
            d = []
            for r in range(REPS):
                # mesma proporção de casos que em B, mesmo N de A
                k1 = int(round(len(trA) * y[trB].mean()))
                pos, neg = trB[y[trB] == 1], trB[y[trB] == 0]
                trD = np.concatenate([rng.choice(pos, min(k1, len(pos)), replace=False),
                                      rng.choice(neg, min(len(trA) - k1, len(neg)), replace=False)])
                d.append(auc_teste(mod, Xs, trD, te, y))
            linha["D_B_com_N_de_A"] = np.nanmean(d)
            res_cen.append(linha)
            print(f"   teste {T:>3} {mod:6}: A={linha['A_so_mistos']:.2f}  B={linha['B_mistos_mais_uma_classe']:.2f}  "
                  f"C={linha['C_so_uma_classe']:.2f}  D={linha['D_B_com_N_de_A']:.2f}   (N treino A={len(trA)}, B={len(trB)})")

    # ---------------------------------------------------------------- 3. curva de aprendizado
    for caso, mistos in MISTOS.items():
        yy = (cl == caso).astype(int)
        base = np.isin(cl, [caso, "control"]) & ~((pj == "P10") & (cl == "cancer"))
        im = np.where(base & np.isin(pj, mistos))[0]
        iu = np.where(base & ~np.isin(pj, mistos))[0]
        for T in mistos:
            te = im[pj[im] == T]
            if len(np.unique(yy[te])) < 2:
                continue
            trA = im[pj[im] != T]
            for mod in modelos():
                # (a) mais N vindo de estudos mistos
                for f in [0.25, 0.5, 0.75, 1.0]:
                    for r in range(REPS if f < 1 else 1):
                        tr = subamostra(trA, estr, f, np.random.default_rng(100 + r)) if f < 1 else trA
                        res_curva.append(dict(tabela=nome, contraste=caso, modelo=mod, estudo_teste=T, fonte="estudos mistos",
                                              n_treino=len(tr), auc=auc_teste(mod, Xs, tr, te, yy)))
                # (b) mistos completos + N extra vindo de estudos de uma classe
                if caso == "cancer":
                    for f in [0.25, 0.5, 0.75, 1.0]:
                        for r in range(REPS if f < 1 else 1):
                            extra = subamostra(iu, estr, f, np.random.default_rng(200 + r)) if f < 1 else iu
                            tr = np.concatenate([trA, extra])
                            res_curva.append(dict(tabela=nome, contraste=caso, modelo=mod, estudo_teste=T,
                                                  fonte="+ estudos de uma classe", n_treino=len(tr),
                                                  auc=auc_teste(mod, Xs, tr, te, yy)))
        C = pd.DataFrame([r for r in res_curva if r["tabela"] == nome and r["contraste"] == caso])
        resumo = C.groupby(["modelo", "fonte"]).apply(
            lambda s: s.groupby("n_treino").auc.mean().round(3).to_dict() if len(s) else {})
        print(f"   curva {caso}:")
        for k, v in C.groupby(["modelo", "fonte"]):
            g = v.groupby(pd.cut(v.n_treino, 4)).agg(n=("n_treino", "mean"), auc=("auc", "mean"))
            print(f"      {k[0]:6} {k[1]:24} " + "  ".join(f"N≈{int(a)}: {b:.2f}" for a, b in zip(g.n, g.auc) if a == a))

    # ---------------------------------------------------------------- 4. embaralhar dentro do estudo
    X = Xs["RF"]

    def cv_auc(rotulos, seed=0):
        P = np.zeros((len(rotulos), 4))
        for tr, te in StratifiedKFold(10, shuffle=True, random_state=seed).split(X, rotulos):
            c = RandomForestClassifier(500, n_jobs=-1, random_state=42).fit(X[tr], rotulos[tr])
            P[np.ix_(te, [CLASSES.index(k) for k in c.classes_])] = c.predict_proba(X[te])
        return {c: roc_auc_score(rotulos == c, P[:, i]) for i, c in enumerate(CLASSES)}

    real = cv_auc(cl)
    res_perm.append(dict(tabela=nome, rotulos="reais", rep=0, **real))
    for r in range(N_PERM):
        rr = np.random.default_rng(300 + r)
        emb = cl.copy()
        for p in np.unique(pj):
            ii = np.where(pj == p)[0]
            emb[ii] = rr.permutation(cl[ii])
        res_perm.append(dict(tabela=nome, rotulos="embaralhados dentro do estudo", rep=r, **cv_auc(emb, seed=r)))
    Pm = pd.DataFrame([x for x in res_perm if x["tabela"] == nome])
    print("   CV aleatória, rótulos reais x embaralhados dentro de cada estudo (média de", N_PERM, "):")
    print(Pm.groupby("rotulos")[CLASSES].mean().round(3).to_string())

pd.DataFrame(res_n).to_csv(f"{OUT_DIR}/22_n_efetivo.csv", index=False)
pd.DataFrame(res_cen).to_csv(f"{OUT_DIR}/22_cenarios_treino.csv", index=False)
pd.DataFrame(res_curva).to_csv(f"{OUT_DIR}/22_curva_aprendizado.csv", index=False)
pd.DataFrame(res_perm).to_csv(f"{OUT_DIR}/22_embaralhado_dentro_estudo.csv", index=False)

S = pd.DataFrame(res_cen)
print("\n==================== resumo dos cenários (média nos estudos de teste)")
cols = ["A_so_mistos", "B_mistos_mais_uma_classe", "C_so_uma_classe", "D_B_com_N_de_A"]
print(S.groupby(["tabela", "modelo"])[cols].mean().round(3).to_string())
print("   sem P22 como teste:")
print(S[S.estudo_teste != "P22"].groupby(["tabela", "modelo"])[cols].mean().round(3).to_string())
