"""SHAP: o que o Random Forest usa para classificar, e se isso é doença ou projeto.

A. Como no artigo: RF das 4 classes com todos os projetos juntos; |SHAP| médio por classe.
   Para cada gênero do topo, quanto da variação dele é explicada pelo projeto (eta² em postos)
   e quanto da abundância vem de um único projeto.
B. RF que prevê o PROJETO (não a classe): os gêneros que mais pesam para o projeto
   coincidem com os que mais pesam para a classe?
C. Leave-one-project-out: SHAP calculado no projeto deixado de fora. O ranking dos gêneros
   se mantém quando o modelo não pode usar o projeto?
D. Dentro de cada projeto (câncer, HSIL, LSIL contra controle; >= 8 por classe): top 10 por
   |SHAP| e a direção (gênero mais abundante empurra para caso ou para controle).
   Um gênero conta como sinal se aparecer no top 10 de >= 2 projetos com a mesma direção.
E. Figura: top 15 do câncer no modelo global, com a parte da variação explicada pelo projeto.

Gêneros presentes em >= 5% das amostras, abundância relativa, RF com 500 árvores
(o mesmo do 03_ml_vies.py), shap.TreeExplainer.
"""
import numpy as np
import pandas as pd
import shap
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestClassifier

from common import CLASSES, OUT_DIR, ativas, genero, meta, relativa

CONTRASTES = {"cancer vs control": "cancer", "HSIL vs control": "lesion high", "LSIL vs control": "lesion low"}
MINIMO = 8
TOP = 20


def rf(seed=42, **kw):
    return RandomForestClassifier(n_estimators=500, n_jobs=-1, random_state=seed, **kw)


def shap_valores(modelo, X):
    """Devolve array amostras x gêneros x classes (formato muda entre versões do shap)."""
    v = shap.TreeExplainer(modelo).shap_values(X, check_additivity=False)
    if isinstance(v, list):
        v = np.stack(v, axis=-1)
    if v.ndim == 2:
        v = v[:, :, None]
    return v


def eta2(v, f):
    r = v.rank()
    tot = ((r - r.mean()) ** 2).sum()
    if tot == 0:
        return np.nan
    return r.groupby(f).apply(lambda s: len(s) * (s.mean() - r.mean()) ** 2).sum() / tot


def direcao(x, s):
    """Sinal da correlação entre abundância e SHAP: + = mais abundante empurra para a classe."""
    if np.std(x) == 0 or np.std(s) == 0:
        return 0.0
    return spearmanr(x, s).correlation


m = meta()
resumo = []
for nome, carregar in ativas():
    R = relativa(genero(carregar()))
    R = R.loc[:, (R > 0).mean() >= 0.05]
    mm = m.loc[R.index]
    y, proj = mm.tipo_amostra.values, mm.Project.values
    X = R.values
    gen = np.array(R.columns)
    print(f"\n== {nome}: {X.shape[0]} amostras, {X.shape[1]} gêneros")

    # A. modelo global (desenho do artigo)
    mod = rf().fit(X, y)
    S = shap_valores(mod, X)
    cls = list(mod.classes_)
    A = pd.DataFrame({"genero": gen})
    for c in CLASSES:
        k = cls.index(c)
        A[f"shap_{c}"] = np.abs(S[:, :, k]).mean(axis=0)
        A[f"dir_{c}"] = [direcao(X[:, j], S[:, j, k]) for j in range(len(gen))]
    A["shap_total"] = A[[f"shap_{c}" for c in CLASSES]].sum(axis=1)
    medias = R.groupby(proj).mean()
    A["projeto_dominante"] = medias.idxmax().values
    A["fracao_no_projeto_dominante"] = (medias.max() / medias.sum()).values
    A["eta2_projeto"] = [eta2(R[g], proj) for g in gen]
    A["eta2_classe"] = [eta2(R[g], y) for g in gen]

    # B. modelo que prevê o projeto
    modp = rf().fit(X, proj)
    Sp = shap_valores(modp, X)
    A["shap_projeto"] = np.abs(Sp).mean(axis=0).sum(axis=1)
    A = A.sort_values("shap_total", ascending=False)

    rho_cp = spearmanr(A.shap_total, A.shap_projeto).correlation
    top_c = set(A.nlargest(TOP, "shap_total").genero)
    top_p = set(A.nlargest(TOP, "shap_projeto").genero)
    print(f"   A/B. top {TOP} classe x top {TOP} projeto: {len(top_c & top_p)} em comum; "
          f"Spearman |SHAP| classe x projeto = {rho_cp:.2f}")
    for c in CLASSES:
        t = A.nlargest(10, f"shap_{c}")
        dom = (t.fracao_no_projeto_dominante >= 0.8).sum()
        mais = (t.eta2_projeto > t.eta2_classe).sum()
        print(f"   top 10 {c}: {dom}/10 com >= 80% da abundância em 1 projeto; "
              f"{mais}/10 explicados mais por projeto que por classe")
        print("      " + ", ".join(f"{g} ({p}, {100 * f:.0f}%)" for g, p, f in
                                    zip(t.genero, t.projeto_dominante, t.fracao_no_projeto_dominante)))

    # C. LOPO: SHAP no projeto deixado de fora
    lopo = {}
    for p in np.unique(proj):
        te = proj == p
        if len(np.unique(y[~te])) < 2:
            continue
        mo = rf().fit(X[~te], y[~te])
        Sl = shap_valores(mo, X[te])
        lopo[p] = pd.Series(np.abs(Sl).mean(axis=0).sum(axis=1), index=gen)
    L = pd.DataFrame(lopo)
    glob_rank = A.set_index("genero").shap_total.reindex(gen)
    estab = []
    for p in L:
        tp = set(L[p].nlargest(TOP).index)
        estab.append(dict(projeto_fora=p, n=int((proj == p).sum()),
                          spearman_com_global=spearmanr(L[p], glob_rank).correlation,
                          top20_em_comum_com_global=len(tp & top_c)))
    E = pd.DataFrame(estab)
    pares = [spearmanr(L[a], L[b]).correlation for i, a in enumerate(L) for b in list(L)[i + 1:]]
    print(f"   C. LOPO: top {TOP} do projeto deixado de fora tem em média "
          f"{E.top20_em_comum_com_global.mean():.1f}/{TOP} em comum com o global; "
          f"Spearman médio entre folds {np.mean(pares):.2f}")
    print(E.to_string(index=False, float_format="%.2f"))

    # D. dentro de cada projeto
    linhas = []
    for comp, classe in CONTRASTES.items():
        for p, s in mm.groupby("Project"):
            vc = s.tipo_amostra.value_counts()
            if vc.get(classe, 0) < MINIMO or vc.get("control", 0) < MINIMO:
                continue
            ids = s.index[s.tipo_amostra.isin([classe, "control"])]
            Xp = R.loc[ids]
            Xp = Xp.loc[:, (Xp > 0).mean() >= 0.05]
            yp = (mm.loc[ids, "tipo_amostra"] == classe).astype(int).values
            mo = rf(class_weight="balanced").fit(Xp.values, yp)
            Sd = shap_valores(mo, Xp.values)[:, :, -1]  # classe 1 = caso
            imp = np.abs(Sd).mean(axis=0)
            for j in np.argsort(imp)[::-1][:10]:
                d = direcao(Xp.values[:, j], Sd[:, j])
                linhas.append(dict(contraste=comp, projeto=p, n_caso=int(yp.sum()), n_controle=int((yp == 0).sum()),
                                   genero=Xp.columns[j], shap_medio=imp[j], rho_abund_shap=d,
                                   direcao="caso" if d > 0 else "controle"))
    D = pd.DataFrame(linhas)
    rep = (D.groupby(["contraste", "genero", "direcao"]).projeto.agg(lambda x: ",".join(sorted(x))).reset_index()
           .assign(n_projetos=lambda d: d.projeto.str.count(",") + 1))
    rep["projetos_testados"] = rep.contraste.map(D.groupby("contraste").projeto.nunique())
    rep = rep[rep.n_projetos >= 2].sort_values(["contraste", "n_projetos"], ascending=[True, False])
    print("   D. no top 10 de >= 2 projetos, mesma direção:")
    print(rep.to_string(index=False) if len(rep) else "   nenhum")
    for p, s in D[D.contraste == "cancer vs control"].groupby("projeto"):
        print(f"      câncer em {p}: " + ", ".join(f"{g} ({'+' if r > 0 else '-'})" for g, r in zip(s.genero, s.rho_abund_shap)))

    A.to_csv(f"{OUT_DIR}/20_shap_global_{nome}.csv", index=False)
    L.to_csv(f"{OUT_DIR}/20_shap_lopo_{nome}.csv")
    E.to_csv(f"{OUT_DIR}/20_shap_lopo_estabilidade_{nome}.csv", index=False)
    D.to_csv(f"{OUT_DIR}/20_shap_por_projeto_{nome}.csv", index=False)
    rep.to_csv(f"{OUT_DIR}/20_shap_repetidos_{nome}.csv", index=False)
    resumo.append(dict(tabela=nome, top20_classe_e_projeto=len(top_c & top_p), spearman_classe_projeto=rho_cp,
                       lopo_top20_em_comum=E.top20_em_comum_com_global.mean(), lopo_spearman_entre_folds=np.mean(pares),
                       repetidos_dentro_projetos=len(rep)))

    # E. figura
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = A.nlargest(15, "shap_cancer").iloc[::-1]
    frac = t.eta2_projeto / (t.eta2_projeto + t.eta2_classe)
    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.barh(t.genero, t.shap_cancer, color=plt.cm.RdBu_r(0.15 + 0.7 * frac.values))
    for i, (v, p, f) in enumerate(zip(t.shap_cancer, t.projeto_dominante, t.fracao_no_projeto_dominante)):
        ax.text(v, i, f"  {p} {100 * f:.0f}%", va="center", fontsize=8)
    ax.set_xlabel("mean |SHAP| (cancer class)")
    ax.set_title(f"{nome}: top 15 genera for cancer (pooled model)\n"
                 "red = variance explained more by study than by class; label = study with most of the abundance",
                 fontsize=9)
    ax.set_xlim(0, t.shap_cancer.max() * 1.35)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/20_shap_cancer_{nome}.png", dpi=150)

    sh = shap.Explanation(S[:, :, cls.index("cancer")], data=X, feature_names=list(gen))
    plt.figure()
    shap.plots.beeswarm(sh, max_display=15, show=False)
    plt.title(f"{nome}: SHAP, cancer class (pooled model)", fontsize=9)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/20_shap_beeswarm_cancer_{nome}.png", dpi=150)
    plt.close("all")

pd.DataFrame(resumo).to_csv(f"{OUT_DIR}/20_shap_resumo.csv", index=False)
print(pd.DataFrame(resumo).to_string(index=False, float_format="%.2f"))
