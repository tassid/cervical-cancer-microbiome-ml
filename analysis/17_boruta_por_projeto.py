"""Boruta como no artigo (todos os projetos juntos) e dentro de cada projeto.

1. Global: as 4 classes, todos os projetos juntos (o desenho do artigo).
2. Por projeto: cada contraste (câncer, HSIL, LSIL contra controle) dentro de cada
   projeto que tem pelo menos 8 amostras em cada classe. Aqui o projeto não pode
   explicar nada, porque é constante dentro da análise.
Um gênero só é reportado como biomarcador se for confirmado em pelo menos dois
projetos, com a mesma direção (mais abundante no caso ou no controle).

Gêneros presentes em >= 5% das amostras, abundância relativa, Random Forest com
classes balanceadas, BorutaPy com 100 iterações e alfa de 0,05.
"""
import numpy as np
import pandas as pd
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier

from common import OUT_DIR, ativas, genero, meta, relativa

CONTRASTES = {"cancer vs control": "cancer", "HSIL vs control": "lesion high", "LSIL vs control": "lesion low"}
MINIMO = 8


def boruta(X, y, seed=42):
    rf = RandomForestClassifier(n_jobs=-1, class_weight="balanced", max_depth=5, random_state=seed)
    b = BorutaPy(rf, n_estimators="auto", max_iter=100, alpha=0.05, random_state=seed, verbose=0)
    b.fit(np.asarray(X, dtype=float), np.asarray(y).astype(str))
    return b.support_, b.support_weak_, b.ranking_


m = meta()
for nome, carregar in ativas():
    G = genero(carregar())
    R = relativa(G)
    R = R.loc[:, (R > 0).mean() >= 0.05]
    mm = m.loc[R.index]
    gen = np.array(R.columns)

    sup, fraco, rank = boruta(R.values, mm.tipo_amostra.values)
    imp = RandomForestClassifier(500, n_jobs=-1, random_state=0, class_weight="balanced").fit(
        R.values, mm.tipo_amostra.values).feature_importances_
    glob_df = pd.DataFrame({"genero": gen, "confirmado": sup, "tentativo": fraco, "ranking": rank, "importancia_rf": imp})
    glob_df = glob_df.sort_values(["confirmado", "importancia_rf"], ascending=[False, False])
    glob_df.to_csv(f"{OUT_DIR}/17_boruta_global_{nome}.csv", index=False)
    print(f"\n== {nome}: Boruta global (4 classes, todos os projetos): {sup.sum()} confirmados de {len(gen)}")
    print("   top 15 por importância:", ", ".join(glob_df[glob_df.confirmado].genero.head(15)))

    linhas = []
    for comp, classe in CONTRASTES.items():
        for pj, s in mm.groupby("Project"):
            vc = s.tipo_amostra.value_counts()
            if vc.get(classe, 0) < MINIMO or vc.get("control", 0) < MINIMO:
                continue
            ids = s.index[s.tipo_amostra.isin([classe, "control"])]
            X = R.loc[ids]
            X = X.loc[:, (X > 0).mean() >= 0.05]
            y = (m.loc[ids, "tipo_amostra"] == classe).astype(int).values
            sp, wk, _ = boruta(X.values, y)
            for g, ok, w in zip(X.columns, sp, wk):
                if ok or w:
                    caso, ctrl = X.loc[y == 1, g].mean(), X.loc[y == 0, g].mean()
                    linhas.append(dict(contraste=comp, projeto=pj, n_caso=int(y.sum()), n_controle=int((y == 0).sum()),
                                       genero=g, status="confirmado" if ok else "tentativo",
                                       direcao="caso" if caso > ctrl else "controle",
                                       media_caso_pct=100 * caso, media_controle_pct=100 * ctrl))
            print(f"   {comp} em {pj} (n={int(y.sum())}/{int((y == 0).sum())}): {int(sp.sum())} confirmados")
    P = pd.DataFrame(linhas)
    P.to_csv(f"{OUT_DIR}/17_boruta_por_projeto_{nome}.csv", index=False)

    conf = P[P.status == "confirmado"]
    rep = (conf.groupby(["contraste", "genero", "direcao"]).projeto.agg(lambda x: ",".join(sorted(x)))
           .reset_index().assign(n_projetos=lambda d: d.projeto.str.count(",") + 1))
    n_testados = P.groupby("contraste").projeto.nunique()
    rep["projetos_testados"] = rep.contraste.map(n_testados)
    rep = rep[rep.n_projetos >= 2].sort_values(["contraste", "n_projetos"], ascending=[True, False])
    rep.to_csv(f"{OUT_DIR}/17_boruta_repetidos_{nome}.csv", index=False)
    print(f"   confirmados em >= 2 projetos, mesma direção:")
    print(rep.to_string(index=False) if len(rep) else "   nenhum")
    glob_top = set(glob_df[glob_df.confirmado].genero.head(25))
    print(f"   dos 25 primeiros do Boruta global, {len(glob_top & set(rep.genero))} se repetem dentro de projetos")
