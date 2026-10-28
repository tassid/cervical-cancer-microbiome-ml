"""LEfSe como no artigo (todos os projetos juntos) e dentro de cada projeto.

Usa o LEfSe oficial (bioconda: lefse_format_input.py e lefse_run.py, parâmetros
padrão: Kruskal-Wallis alfa 0,05, Wilcoxon alfa 0,05, LDA >= 2,0), em abundância
relativa por gênero (normalizada para 1e6, como no Galaxy/LEfSe).
  1. Global: câncer x controle e as 4 classes, todos os projetos juntos.
  2. Por projeto: cada contraste dentro de cada projeto com >= 8 amostras por classe.
Um gênero entra como biomarcador só se aparecer, com a mesma classe enriquecida, em
pelo menos dois projetos.

Requer LEFSE_BIN apontando para a pasta bin de um ambiente com lefse 1.1.2, python 3.9 e rpy2 < 3.5
(com Python mais novo o lefse_run.py falha no rpy2).
"""
import os
import subprocess
import tempfile

import pandas as pd

from common import OUT_DIR, ativas, genero, meta, relativa

LEFSE = os.environ.get("LEFSE_BIN", "")
ENV = {**os.environ, "PATH": LEFSE + ":" + os.environ.get("PATH", "")}
CONTRASTES = {"cancer vs control": "cancer", "HSIL vs control": "lesion high", "LSIL vs control": "lesion low"}
MINIMO = 8


def lefse(R, classes):
    """Roda o LEfSe e devolve (gênero, classe enriquecida, LDA, p) dos significativos."""
    R = R.loc[:, (R > 0).any()]
    with tempfile.TemporaryDirectory() as d:
        tab = pd.DataFrame(R.T.values, index=[c.replace(" ", "_") for c in R.columns], columns=R.index)
        cab = pd.DataFrame([list(classes), list(R.index)], index=["class", "subject_id"], columns=R.index)
        pd.concat([cab, tab]).to_csv(f"{d}/in.txt", sep="\t", header=False)
        subprocess.run([f"{LEFSE}/lefse_format_input.py", f"{d}/in.txt", f"{d}/in.lefse", "-c", "1", "-u", "2",
                        "-o", "1000000"],
                       check=True, capture_output=True, env=ENV)
        subprocess.run([f"{LEFSE}/lefse_run.py", f"{d}/in.lefse", f"{d}/res.txt"], check=True, capture_output=True, env=ENV)
        res = pd.read_csv(f"{d}/res.txt", sep="\t", header=None, names=["genero", "log_max", "classe", "LDA", "p"])
    res = res[res.classe.notna() & (res.classe.astype(str) != "") & (res.classe.astype(str) != "nan")]
    return res[["genero", "classe", "LDA", "p"]]


m = meta()
for nome, carregar in ativas():
    R = relativa(genero(carregar()))
    R = R.loc[:, (R > 0).mean() >= 0.05]
    mm = m.loc[R.index]

    glob = []
    cc = mm.index[mm.tipo_amostra.isin(["cancer", "control"])]
    r = lefse(R.loc[cc], mm.loc[cc, "tipo_amostra"]); r["analise"] = "global cancer vs control"; glob.append(r)
    r = lefse(R, mm.tipo_amostra.str.replace(" ", "_")); r["analise"] = "global 4 classes"; glob.append(r)
    G = pd.concat(glob).sort_values(["analise", "LDA"], ascending=[True, False])
    G.to_csv(f"{OUT_DIR}/19_lefse_global_{nome}.csv", index=False)
    print(f"\n== {nome}: LEfSe global câncer x controle: {(G.analise == 'global cancer vs control').sum()} gêneros; "
          f"4 classes: {(G.analise == 'global 4 classes').sum()}")

    linhas = []
    for comp, classe in CONTRASTES.items():
        for pj, s in mm.groupby("Project"):
            vc = s.tipo_amostra.value_counts()
            if vc.get(classe, 0) < MINIMO or vc.get("control", 0) < MINIMO:
                continue
            ids = s.index[s.tipo_amostra.isin([classe, "control"])]
            y = mm.loc[ids, "tipo_amostra"].str.replace(" ", "_")
            r = lefse(R.loc[ids], y)
            r["contraste"], r["projeto"] = comp, pj
            linhas.append(r)
            print(f"   {comp} em {pj}: {len(r)} gêneros")
    P = pd.concat(linhas)
    P.to_csv(f"{OUT_DIR}/19_lefse_por_projeto_{nome}.csv", index=False)
    rep = (P.groupby(["contraste", "genero", "classe"]).projeto.agg(lambda x: ",".join(sorted(x))).reset_index()
           .assign(n_projetos=lambda d: d.projeto.str.count(",") + 1))
    rep["projetos_testados"] = rep.contraste.map(P.groupby("contraste").projeto.nunique())
    rep = rep[rep.n_projetos >= 2].sort_values(["contraste", "n_projetos"], ascending=[True, False])
    rep.to_csv(f"{OUT_DIR}/19_lefse_repetidos_{nome}.csv", index=False)
    print("   em >= 2 projetos, mesma classe enriquecida:")
    print(rep.to_string(index=False) if len(rep) else "   nenhum")
    gcc = set(G[G.analise == "global cancer vs control"].genero)
    rcc = set(rep[rep.contraste == "cancer vs control"].genero)
    print(f"   do LEfSe global câncer x controle ({len(gcc)} gêneros), {len(gcc & rcc)} se repetem dentro de projetos")
