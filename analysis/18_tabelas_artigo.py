"""Tabelas prontas para o artigo.

1. Tabela 1 corrigida: por BioProject e classe, o que o artigo declara, o que foi
   catalogado, o que está na tabela da Paola com >= 1.000 leituras e o que está na
   tabela da Tassiane (P22 reprocessado), com notas de exclusão.
2. Tabela de validação: AUC por classe nos três esquemas (CV aleatória, só projeto,
   leave-one-project-out) para as duas tabelas, a partir de 03_ml_*.json.
Saídas: results/18_tabela1.csv, results/18_tabela_validacao.csv e um Markdown com as duas.
"""
import json
import os

import pandas as pd

from common import OUT_DIR, TABELAS, meta

BIOPROJECT = {"P1": "PRJNA687644", "P2": "PRJNA518153", "P6": "PRJNA687331", "P9": "PRJNA431248",
              "P10": "PRJEB51893", "P14": "PRJNA933917", "P16": "PRJNA1029035", "P19": "PRJNA914231",
              "P21": "PRJEB83336", "P22": "PRJNA725946"}
PAIS = {"P1": "China", "P2": "USA", "P6": "China", "P9": "USA", "P10": "USA", "P14": "Brazil", "P16": "USA",
        "P19": "Nigeria", "P21": "Spain", "P22": "China"}
REGIAO = {"P1": "V3-V4", "P2": "V4", "P6": "V3-V4", "P9": "V4", "P10": "V4", "P14": "V3-V4", "P16": "V4",
          "P19": "V3-V4", "P21": "V3-V4", "P22": "V3-V4"}
# Tabela 1 do manuscrito (CC, HSIL, LSIL, Control)
ARTIGO = {"P1": (68, 0, 0, 4), "P2": (10, 27, 11, 29), "P6": (26, 0, 0, 0), "P9": (58, 0, 0, 0),
          "P10": (1, 59, 43, 214), "P14": (0, 22, 0, 21), "P16": (26, 0, 0, 0), "P19": (31, 60, 58, 19),
          "P21": (0, 2, 0, 100), "P22": (65, 0, 0, 54)}
NOTAS = {
    "P14": "21 runs (10 controls, 11 HSIL) are not 16S amplicons (human DNA) and were excluded.",
    "P16": "55 runs listed: 26 low-depth runs with BioSample (counted in Table 1) and 29 runs without BioSample, "
           "~55% of whose reads lack the 16S primer; only the 29 are in the analysed table.",
    "P22": "Cancer and control samples were sequenced in runs with different read lengths (~222 vs ~274 nt).",
    "P21": "Primer sequence not published; included in the article table, excluded from the reprocessed table.",
    "P19": "Primer corrected empirically.",
}
CLASSES = ["cancer", "lesion high", "lesion low", "control"]

m = meta()


def contagem(ids):
    s = m.loc[ids].groupby(["Project", "tipo_amostra"]).size().unstack(fill_value=0)
    return s.reindex(columns=CLASSES, fill_value=0)


cat = contagem(m.index)
P = TABELAS["PAOLA"]()
pao = contagem(P.index[P.sum(axis=1) >= 1000])
tas = contagem(TABELAS["TASSI_V2"]().index)

linhas = []
for pj in sorted(BIOPROJECT, key=lambda p: int(p[1:])):
    def fmt(t):
        if pj not in t.index:
            return "0/0/0/0"
        r = t.loc[pj]
        return "/".join(str(int(r[c])) for c in CLASSES)
    linhas.append({"Project": pj, "BioProject": BIOPROJECT[pj], "Country": PAIS[pj], "16S region": REGIAO[pj],
                   "Article (CC/HSIL/LSIL/Ctrl)": "/".join(map(str, ARTIGO[pj])),
                   "Catalogued": fmt(cat), "Paola table, >=1,000 reads": fmt(pao),
                   "Reprocessed table": fmt(tas), "Note": NOTAS.get(pj, "")})
T1 = pd.DataFrame(linhas)
tot = lambda t: "/".join(str(int(t[c].sum())) for c in CLASSES)
T1.loc[len(T1)] = {"Project": "Total", "BioProject": "", "Country": "", "16S region": "",
                   "Article (CC/HSIL/LSIL/Ctrl)": "/".join(str(sum(v[i] for v in ARTIGO.values())) for i in range(4)),
                   "Catalogued": tot(cat), "Paola table, >=1,000 reads": tot(pao), "Reprocessed table": tot(tas), "Note": ""}
T1.to_csv(f"{OUT_DIR}/18_tabela1.csv", index=False)

val = []
for nome, rotulo in [("PAOLA", "Paola table"), ("TASSI_V2", "Reprocessed table")]:
    R = json.load(open(os.path.join(OUT_DIR, f"03_ml_{nome}.json")))
    for chave, esquema in [("treino_no_treino", "Evaluated on training samples"),
                           ("cv_aleatoria", "Random 10-fold cross-validation"),
                           ("so_projeto", "Study identifier only (no microbiome)"),
                           ("lopo", "Leave-one-project-out")]:
        val.append({"Table": rotulo, "Validation": esquema,
                    **{c: round(R[chave][c], 3) for c in ["cancer", "control", "lesion high", "lesion low"]}})
    val.append({"Table": rotulo, "Validation": "Predicting the study of origin (accuracy)",
                "cancer": round(R["acuracia_prever_projeto"], 3), "control": None, "lesion high": None, "lesion low": None})
V = pd.DataFrame(val)
V.to_csv(f"{OUT_DIR}/18_tabela_validacao.csv", index=False)

with open(f"{OUT_DIR}/18_tabelas_artigo.md", "w") as f:
    f.write("# Table 1 (corrected)\n\nCounts as CC/HSIL/LSIL/Control.\n\n")
    f.write(T1.to_markdown(index=False))
    f.write("\n\n# Table X. Random Forest AUC by validation scheme\n\n")
    f.write(V.to_markdown(index=False))
    f.write("\n")
print(T1.to_string(index=False))
print(V.to_string(index=False))
