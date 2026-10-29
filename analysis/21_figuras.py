"""Figuras para o artigo: validação dos modelos, viés de projeto, SHAP e diferenças
entre a tabela da Paola e a tabela reprocessada da Tassiane.

Lê os resultados de results/ (rode antes os scripts 01-20). As figuras de composição
(f13, f14, f10) também leem as tabelas, então precisam de DATA_DIR.
Saída: figuras/fNN_nome.png (200 dpi) e .pdf.

Cores: Paola = azul, Tassiane = laranja; classes clínicas com cor fixa
(câncer vermelho, HSIL violeta, LSIL amarelo, controle verde-água), sempre com rótulo.
Paleta validada com o validador de daltonismo (scripts/validate_palette.js da skill de dataviz).
"""
import json
import os
import traceback

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from common import OUT_DIR, TABELAS, genero, meta, relativa

FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figuras")
os.makedirs(FIG, exist_ok=True)
R = OUT_DIR

INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#ffffff"
TAB = {"PAOLA": "#2a78d6", "TASSI_V2": "#eb6834"}
TABLAB = {"PAOLA": "Paola table", "TASSI_V2": "Reprocessed table (Tassiane)"}
CLS = ["cancer", "lesion high", "lesion low", "control"]
CLSLAB = {"cancer": "Cancer", "lesion high": "HSIL", "lesion low": "LSIL", "control": "Control"}
CLSCOR = {"cancer": "#e34948", "lesion high": "#6250d6", "lesion low": "#eda100", "control": "#1baf7a"}
PALETA8 = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DIVERG = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f2f1ee", "#e34948"])
BIOPROJ = {"P1": "PRJNA687644", "P2": "PRJNA518153", "P6": "PRJNA687331", "P9": "PRJNA431248",
           "P10": "PRJEB51893", "P14": "PRJNA933917", "P16": "PRJNA1029035", "P19": "PRJNA914231",
           "P21": "PRJEB83336", "P22": "PRJNA725946"}
ORDEM_PJ = ["P1", "P2", "P6", "P9", "P10", "P14", "P16", "P19", "P21", "P22"]

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.labelcolor": INK2, "axes.edgecolor": MUTED, "axes.linewidth": 0.8,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "legend.fontsize": 8, "figure.facecolor": SURF, "axes.facecolor": SURF,
    "savefig.bbox": "tight", "savefig.facecolor": SURF, "pdf.fonttype": 42,
})


def grade(ax, eixo="x"):
    ax.grid(axis=eixo, color=GRID, lw=0.7)
    ax.set_axisbelow(True)


def salvar(fig, nome, titulo, nota=None):
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            fig.tight_layout()
        except Exception:
            pass
    H = fig.get_figheight()
    fig.text(0.01, 1 + 0.12 / H, titulo, ha="left", va="bottom", fontsize=11, fontweight="bold", color=INK)
    if nota:
        fig.text(0.01, -0.12 / H, nota, ha="left", va="top", fontsize=7.5, color=INK2, wrap=True)
    fig.savefig(f"{FIG}/{nome}.png", dpi=200)
    fig.savefig(f"{FIG}/{nome}.pdf")
    plt.close(fig)
    print("ok", nome)


def legenda_tabelas(ax, loc="lower left", **kw):
    h = [plt.Line2D([], [], marker="o", ls="", color=TAB[t], ms=6, label=TABLAB[t]) for t in TAB]
    ax.legend(handles=h, loc=loc, **kw)


def ml(t):
    return json.load(open(f"{R}/03_ml_{t}.json"))


# ---------------------------------------------------------------- validação
def f01():
    esquemas = [("treino_no_treino", "Training\nset"), ("cv_aleatoria", "Random\n10-fold CV"),
                ("so_projeto", "Study ID\nonly"), ("lopo", "Leave-one-\nstudy-out")]
    fig, axs = plt.subplots(1, 4, figsize=(11, 3.4), sharey=True)
    for ax, c in zip(axs, CLS):
        for k, t in enumerate(TAB):
            d = ml(t)
            v = [d[e][c] for e, _ in esquemas]
            x = np.arange(4) + (k - 0.5) * 0.18
            ax.plot(x, v, color=TAB[t], lw=1.5, alpha=0.6)
            ax.plot(x, v, "o", color=TAB[t], ms=7, mec=SURF, mew=1.5)
            ax.text(x[-1] + 0.12 * (1 if k else -1), v[-1], f"{v[-1]:.2f}", fontsize=7.5, color=INK2,
                    ha="left" if k else "right", va="center")
        ax.axhline(0.5, color=MUTED, lw=0.8, ls="--")
        ax.set_xticks(range(4), [l for _, l in esquemas], fontsize=7.5)
        ax.set_title(CLSLAB[c])
        ax.set_ylim(0.25, 1.04)
        grade(ax, "y")
    axs[0].set_ylabel("AUC (one-vs-rest)")
    axs[0].text(3.35, 0.51, "chance", fontsize=7, color=MUTED, ha="right", va="bottom")
    legenda_tabelas(axs[0])
    salvar(fig, "f01_auc_por_validacao", "AUC depends on how the model is validated",
           "Random Forest, 4 classes. A model given only the study identifier matches the full microbiome under random CV; "
           "holding out each study drops AUC to near or below chance.")


def f02():
    fig, axs = plt.subplots(1, 2, figsize=(12, 7.4), sharex=True, gridspec_kw={"wspace": 0.55})
    for ax, t in zip(axs, TAB):
        d = pd.read_csv(f"{R}/09_forca_bruta_{t}.csv")
        d["nome"] = d.modelo + " · " + d.prep.map({"rel": "relative", "clr": "CLR", "pa": "pres/abs"}) + \
            np.where(d.smote, " · SMOTE", "")
        w = d.pivot_table(index="nome", columns="esquema", values="AUC").sort_values("lopo")
        y = np.arange(len(w))
        ax.hlines(y, w.lopo, w.aleatoria, color=GRID, lw=2.5)
        ax.plot(w.aleatoria, y, "o", color=MUTED, ms=6, label="Random 5-fold CV")
        ax.plot(w.lopo, y, "o", color=TAB[t], ms=6, mec=SURF, mew=1, label="Leave-one-study-out")
        ax.set_yticks(y, w.index, fontsize=7)
        ax.axvline(0.5, color=MUTED, lw=0.8, ls="--")
        ax.set_title(f"{TABLAB[t]}: {len(w)} models")
        ax.set_xlabel("AUC, cancer vs control")
        grade(ax)
        ax.text(w.aleatoria.median(), len(w) - 0.2, f"median {w.aleatoria.median():.2f}", fontsize=7.5,
                color=INK2, ha="center", va="bottom")
        ax.text(w.lopo.median(), len(w) - 0.2, f"median {w.lopo.median():.2f}", fontsize=7.5, color=INK2,
                ha="center", va="bottom")
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2)
        ax.set_ylim(-1, len(w) + 0.8)
    salvar(fig, "f02_forca_bruta_30_modelos", "No classifier survives a new study",
           "Exhaustive search: 9 classifiers x 3 preprocessings (relative abundance, CLR, presence/absence), with and without SMOTE. "
           "Every combination reaches 0.83-0.97 under random CV and falls to 0.41-0.79 when the test study is unseen.")


def f03():
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    pjs = ["P1", "P2", "P19", "P22"]
    rng = np.random.default_rng(1)
    for k, t in enumerate(TAB):
        d = pd.read_csv(f"{R}/09_forca_bruta_{t}.csv")
        d = d[d.esquema == "lopo"]
        for i, p in enumerate(pjs):
            v = d[p].dropna().values
            x = i + (k - 0.5) * 0.3 + rng.uniform(-0.07, 0.07, len(v))
            ax.plot(x, v, "o", color=TAB[t], ms=4, alpha=0.55)
            ax.hlines(np.median(v), i + (k - 0.5) * 0.3 - 0.12, i + (k - 0.5) * 0.3 + 0.12, color=INK, lw=2)
    ax.axhline(0.5, color=MUTED, lw=0.8, ls="--")
    ax.set_xticks(range(4), [f"{p}\n{BIOPROJ[p]}" for p in pjs])
    ax.set_ylabel("AUC in the held-out study")
    grade(ax, "y")
    legenda_tabelas(ax, loc="upper right")
    salvar(fig, "f03_forca_bruta_por_projeto", "Cancer vs control in each held-out study, all 30 models",
           "Each dot is one model trained without that study. Black bar: median. P22 stays below chance for every model "
           "(cancer and controls were sequenced in different runs).")


def f04():
    fig, axs = plt.subplots(2, 2, figsize=(8.5, 7.6))
    for i, t in enumerate(TAB):
        d = ml(t)
        for j, (k, lab) in enumerate([("matriz_confusao_cv_aleatoria", "Random CV"),
                                      ("matriz_confusao_lopo", "Leave-one-study-out")]):
            M = np.array([[d[k][p][v] for p in CLS] for v in CLS], float)  # linhas = verdade
            P = M / M.sum(axis=1, keepdims=True)
            ax = axs[i, j]
            ax.imshow(P, cmap=LinearSegmentedColormap.from_list("s", ["#f7f6f3", TAB[t]]), vmin=0, vmax=1)
            for a in range(4):
                for b in range(4):
                    ax.text(b, a, f"{int(M[a, b])}\n{100 * P[a, b]:.0f}%", ha="center", va="center", fontsize=7.5,
                            color=SURF if P[a, b] > 0.55 else INK)
            ax.set_xticks(range(4), [CLSLAB[c] for c in CLS])
            ax.set_yticks(range(4), [CLSLAB[c] for c in CLS])
            ax.set_xlabel("Predicted")
            if j == 0:
                ax.set_ylabel(f"{TABLAB[t]}\nTrue")
            ax.set_title(lab)
            for s in ax.spines.values():
                s.set_visible(False)
    salvar(fig, "f04_matrizes_confusao", "Confusion matrices: random CV vs unseen study",
           "Rows are true classes (percent of the row). Under leave-one-study-out no LSIL sample is recognised "
           "and most HSIL samples are called control.")


def f05():
    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    linhas = []
    for t in TAB:
        d = ml(t)
        linhas.append((TABLAB[t], d["acuracia_prever_projeto"], d["acuracia_prever_projeto_acaso"], TAB[t]))
    y = np.arange(len(linhas))
    for i, (lab, a, c, cor) in enumerate(linhas):
        ax.barh(i, a, color=cor, height=0.5)
        ax.plot([c, c], [i - 0.32, i + 0.32], color=INK, lw=2)
        ax.text(a + 0.01, i, f"{100 * a:.0f}%", va="center", fontsize=8, color=INK)
        ax.text(c + 0.01, i + 0.3, f"chance {100 * c:.0f}%", va="bottom", fontsize=7, color=INK2)
    ax.set_yticks(y, [l[0] for l in linhas])
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Accuracy predicting the study of origin from the microbiome")
    grade(ax)
    salvar(fig, "f05_prever_projeto", "The microbiome identifies the study of origin",
           "Random Forest with the same genera, target = BioProject. Chance = always predicting the largest study.")


def f06():
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1.4, 1]})
    ax = axs[0]
    pjs = ["P2", "P10", "P14", "P19", "P22"]
    for k, t in enumerate(TAB):
        d = ml(t)["dentro_do_projeto"]
        for i, p in enumerate(pjs):
            for c in CLS:
                if p in d and c in d[p]:
                    x = i + (CLS.index(c) - 1.5) * 0.17
                    ax.plot(x, d[p][c], "o" if k == 0 else "D", color=CLSCOR[c], ms=6, mec=SURF, mew=1, alpha=0.9)
    ax.axhline(0.5, color=MUTED, lw=0.8, ls="--")
    ax.set_xticks(range(len(pjs)), pjs)
    ax.set_ylabel("AUC, CV within the study")
    ax.set_title("A. Microbiome model trained and tested inside each study")
    h = [plt.Line2D([], [], marker="s", ls="", color=CLSCOR[c], label=CLSLAB[c]) for c in CLS]
    h += [plt.Line2D([], [], marker="o", ls="", color=MUTED, label=TABLAB["PAOLA"]),
          plt.Line2D([], [], marker="D", ls="", color=MUTED, label=TABLAB["TASSI_V2"])]
    ax.legend(handles=h, loc="lower left", ncol=2, fontsize=7)
    ax.set_ylim(0.2, 1.02)
    grade(ax, "y")
    ax = axs[1]
    d = ml("PAOLA")["so_profundidade_dentro_do_projeto"]
    rows = [(f"{p} · {c.replace('lesion high', 'HSIL').replace('lesion low', 'LSIL')}", v) for p in d for c, v in d[p].items()]
    rows.sort(key=lambda r: r[1])
    y = np.arange(len(rows))
    ax.hlines(y, 0.5, [v for _, v in rows], color=GRID, lw=2)
    ax.scatter([v for _, v in rows], y, s=45, c=[("#e34948" if v > 0.8 else MUTED) for _, v in rows], zorder=3)
    ax.set_yticks(y, [r for r, _ in rows], fontsize=7.5)
    ax.axvline(0.5, color=MUTED, lw=0.8, ls="--")
    ax.set_xlabel("AUC using only read depth")
    ax.set_title("B. Read depth alone")
    ax.text(rows[-1][1], len(rows) - 1, "  batch effect", va="center", fontsize=7.5, color="#e34948")
    grade(ax)
    salvar(fig, "f06_dentro_do_projeto", "Inside studies, the signal is weak except where batch and class coincide",
           "A: only P19 (Nigeria) separates cancer (AUC ~0.80) without study confounding. P22 reaches 0.98, "
           "but B shows that sequencing depth alone gives 0.97 there.")


def f07():
    d = pd.read_csv(f"{R}/06_permanova.csv").set_index("tabela")
    met = [("R2_classe", "Clinical group alone"), ("R2_projeto", "Study alone"),
           ("R2_classe_alem_do_projeto", "Clinical group\nbeyond study")]
    fig, ax = plt.subplots(figsize=(7, 3))
    for k, t in enumerate(TAB):
        v = [100 * d.loc[t, m] for m, _ in met]
        y = np.arange(3) + (k - 0.5) * 0.36
        ax.barh(y, v, height=0.34, color=TAB[t], label=TABLAB[t])
        for yy, vv in zip(y, v):
            ax.text(vv + 0.2, yy, f"{vv:.1f}%", va="center", fontsize=7.5, color=INK)
    ax.set_yticks(range(3), [l for _, l in met])
    ax.invert_yaxis()
    ax.set_xlabel("Variance explained (R², Bray-Curtis PERMANOVA)")
    grade(ax)
    ax.legend(loc="lower right")
    salvar(fig, "f07_permanova", "Study explains twice as much variance as clinical group",
           "Beyond study (permutations restricted within study) clinical group explains 0.4% (p = 0.08).")


def f08():
    linhas = [("Original table", "LV1", 56.7, 11.1), ("Original table", "LV2", 58.2, 7.9),
              ("P22 reprocessed", "LV1", 30.3, 15.0), ("P22 reprocessed", "LV2", 15.9, 4.1)]
    fig, axs = plt.subplots(1, 2, figsize=(8, 2.8), sharey=True)
    for ax, tab in zip(axs, ["Original table", "P22 reprocessed"]):
        s = [l for l in linhas if l[0] == tab]
        y = np.arange(len(s))
        ax.barh(y - 0.18, [l[2] for l in s], height=0.34, color=INK2, label="Study")
        ax.barh(y + 0.18, [l[3] for l in s], height=0.34, color="#6250d6", label="Clinical group")
        for yy, l in zip(y, s):
            ax.text(l[2] + 1, yy - 0.18, f"{l[2]:.1f}", va="center", fontsize=7.5)
            ax.text(l[3] + 1, yy + 0.18, f"{l[3]:.1f}", va="center", fontsize=7.5)
        ax.set_yticks(y, [f"Latent axis {l[1][-1]}" for l in s])
        ax.set_title(tab)
        ax.set_xlim(0, 70)
        ax.set_xlabel("η² of the GLLVM latent axis (%)")
        grade(ax)
    axs[0].invert_yaxis()
    axs[1].legend(loc="lower right")
    salvar(fig, "f08_gllvm", "GLLVM: the latent axes track study, less so after fixing P22",
           "Tassiane's gllvm_fit.R rerun. Reprocessing P22 in the V3-V4 branch halves the share of the axes explained by study.")


def f09():
    d = pd.read_csv(f"{R}/02_alfa_efeitos.csv")
    d = d[(d.metrica == "shannon") & (d.comparacao == "cancer vs control") & d.efeito.notna()]

    def rot(e):
        if "SEM" in e:
            return "All studies pooled"
        if "COM" in e:
            return "Adjusted for study"
        return e.replace("dentro de ", "Within ")

    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    for k, t in enumerate(TAB):
        s = d[d.tabela == t].reset_index(drop=True)
        y = np.arange(len(s)) + (k - 0.5) * 0.25
        ax.hlines(y, 0, s.efeito, color=TAB[t], lw=1.2, alpha=0.5)
        ax.plot(s.efeito, y, "o", color=TAB[t], ms=7, mec=SURF, mew=1.2, label=TABLAB[t])
        if k == 1:
            ax.set_yticks(np.arange(len(s)), [rot(e) for e in s.escopo])
            for yy, p in zip(np.arange(len(s)), s.p):
                ax.text(2.25, yy, f"p = {p:.2g}", fontsize=7.5, color=INK2, va="center")
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlim(-0.8, 2.6)
    ax.invert_yaxis()
    ax.set_xlabel("Difference in Shannon diversity, cancer minus control")
    grade(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    salvar(fig, "f09_shannon_efeito", "Higher diversity in cancer disappears after adjusting for study",
           "p values shown for the reprocessed table. The within-study effect changes sign between studies (P22 negative).")


def f10():
    m = meta()
    fig, axs = plt.subplots(2, 5, figsize=(12, 5), sharey=True)
    for ax, p in zip(axs.flat, ORDEM_PJ):
        d = pd.read_csv(f"{R}/02_alfa_PAOLA.csv", index_col=0)
        s = d[d.Project == p]
        cl = [c for c in CLS if (s.tipo_amostra == c).any()]
        bp = ax.boxplot([s.shannon[s.tipo_amostra == c] for c in cl], widths=0.55, patch_artist=True,
                        medianprops=dict(color=INK, lw=1.5), flierprops=dict(ms=2, mec=MUTED),
                        whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED))
        for b, c in zip(bp["boxes"], cl):
            b.set(facecolor=CLSCOR[c], alpha=0.75, edgecolor=SURF)
        ax.set_xticks(range(1, len(cl) + 1), [f"{CLSLAB[c]}\n{(s.tipo_amostra == c).sum()}" for c in cl], fontsize=7)
        ax.set_title(f"{p} · {BIOPROJ[p]}", fontsize=8.5)
        grade(ax, "y")
    for ax in axs[:, 0]:
        ax.set_ylabel("Shannon")
    salvar(fig, "f10_shannon_por_projeto", "Shannon diversity by study and clinical group (Paola table)",
           "Number under each label = samples. Four studies have only cancer samples and one has almost only controls, "
           "so pooled comparisons mix study with class.")


# ---------------------------------------------------------------- Paola x Tassiane
def f11():
    d = pd.read_csv(f"{R}/07_paola_vs_TASSI_V2_por_projeto.csv").set_index("Project").reindex(
        [p for p in ORDEM_PJ if p != "P21"])
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
    y = np.arange(len(d))
    ax = axs[0]
    cor = ["#e34948" if v > 0.3 else INK2 for v in d.bray_curtis_entre_pipelines]
    ax.barh(y, d.bray_curtis_entre_pipelines, color=cor, height=0.6)
    for yy, v in zip(y, d.bray_curtis_entre_pipelines):
        ax.text(v + 0.008, yy, f"{v:.3f}", va="center", fontsize=7.5)
    ax.set_yticks(y, [f"{p} · {BIOPROJ[p]}" for p in d.index])
    ax.invert_yaxis()
    ax.set_xlabel("Median Bray-Curtis between tables, same sample")
    ax.set_title("A. Genus profiles")
    grade(ax)
    ax = axs[1]
    ax.axvline(1, color=MUTED, lw=0.8, ls="--")
    ax.hlines(y, 1, d.razao_leituras_tassi_paola, color=GRID, lw=2)
    ax.plot(d.razao_leituras_tassi_paola, y, "o", color=TAB["TASSI_V2"], ms=7)
    ax.set_xscale("log")
    ax.set_xticks([0.5, 1, 2], ["0.5x", "1x", "2x"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("Reads per sample, Tassiane / Paola (median)")
    ax.set_title("B. Sequencing depth kept")
    grade(ax)
    salvar(fig, "f11_concordancia_pipelines", "The two pipelines agree on everything but P16",
           "Bray-Curtis 0 = identical. P16: 39% of reads in the Paola table are 'Unassigned' or eukaryotic (host DNA); "
           "filtering them lowers the distance to 0.09. P21 is absent from Tassiane's table.")


def f12():
    d = pd.read_csv(f"{R}/10_contabilidade_por_projeto.csv").set_index("projeto").reindex(ORDEM_PJ)
    fig, ax = plt.subplots(figsize=(9, 3.6))
    x = np.arange(len(d))
    ax.bar(x - 0.27, d.catalogadas, 0.26, color=GRID, edgecolor=MUTED, lw=0.6, label="Runs catalogued")
    ax.bar(x, d.paola_ok, 0.26, color=TAB["PAOLA"], label=TABLAB["PAOLA"])
    ax.bar(x + 0.27, d.tassi_ok, 0.26, color=TAB["TASSI_V2"], label=TABLAB["TASSI_V2"])
    notas = {"P14": "21 runs are\nhuman DNA", "P16": "two sets\nof runs", "P21": "not in\nTassiane"}
    for i, p in enumerate(d.index):
        if p in notas:
            ax.text(i, d.loc[p, "catalogadas"] + 8, notas[p], ha="center", fontsize=7, color=INK2)
    ax.set_xticks(x, [f"{p}\n{BIOPROJ[p]}" for p in d.index], fontsize=7)
    ax.set_ylabel("Samples")
    grade(ax, "y")
    ax.legend(loc="upper left")
    salvar(fig, "f12_contabilidade_amostras", "Where samples were lost in each table",
           "Samples with at least 1,000 reads after denoising. Totals: 1,042 catalogued, 997 Paola, 889 Tassiane.")


_tabs = {}


def tabela(t):
    if t not in _tabs:
        _tabs[t] = relativa(genero(TABELAS[t]()))
    return _tabs[t]


def f13():
    m = meta()
    P, T = tabela("PAOLA"), tabela("TASSI_V2")
    pjs = [p for p in ORDEM_PJ if p != "P21"]
    top = (P.mean() + T.reindex(columns=P.columns, fill_value=0).mean()).drop("sem_genero", errors="ignore").nlargest(7).index
    cores = dict(zip(top, PALETA8))
    fig, ax = plt.subplots(figsize=(11, 4.2))
    x = 0
    ticks, labs = [], []
    for p in pjs:
        for t, D in (("PAOLA", P), ("TASSI_V2", T)):
            ids = D.index[m.loc[D.index, "Project"] == p]
            mu = D.loc[ids].mean()
            base = 0
            for g in top:
                v = 100 * mu.get(g, 0)
                ax.bar(x, v, bottom=base, color=cores[g], width=0.8, edgecolor=SURF, lw=0.6)
                base += v
            ax.bar(x, 100 - base, bottom=base, color=GRID, width=0.8, edgecolor=SURF, lw=0.6)
            ax.text(x, 101, "P" if t == "PAOLA" else "T", ha="center", fontsize=7, color=INK2)
            x += 1
        ticks.append(x - 1.5)
        labs.append(p)
        x += 0.6
    ax.set_xticks(ticks, labs)
    ax.set_ylabel("Mean relative abundance (%)")
    ax.set_ylim(0, 106)
    h = [plt.Rectangle((0, 0), 1, 1, color=cores[g], label=g) for g in top]
    h.append(plt.Rectangle((0, 0), 1, 1, color=GRID, label="Other"))
    ax.legend(handles=h, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    salvar(fig, "f13_composicao_por_projeto", "Same studies, two pipelines: mean composition side by side",
           "P = Paola table, T = Tassiane reprocessed table. Seven most abundant genera overall; the rest grouped as Other.")


def f14():
    m = meta()
    P, T = tabela("PAOLA"), tabela("TASSI_V2")
    pjs = [p for p in ORDEM_PJ if p != "P21"]
    fig, axs = plt.subplots(2, 5, figsize=(12, 5.2))
    for ax, p in zip(axs.flat, pjs):
        ids = P.index[m.loc[P.index, "Project"] == p].intersection(T.index)
        a = P.loc[ids].mean() * 100
        b = T.loc[ids].mean().reindex(a.index.union(T.columns), fill_value=0) * 100
        a = a.reindex(b.index, fill_value=0)
        ok = (a > 0.01) | (b > 0.01)
        a, b = a[ok].clip(lower=0.01), b[ok].clip(lower=0.01)
        ax.plot([0.01, 100], [0.01, 100], color=MUTED, lw=0.8, ls="--")
        ax.plot(a, b, "o", ms=3.5, color=INK2, alpha=0.6)
        dif = (np.log10(b) - np.log10(a)).abs()
        for g in dif[(a > 1) | (b > 1)].nlargest(2).index:
            if dif[g] > 0.3:
                ax.annotate(g[:18], (a[g], b[g]), fontsize=6.5, color="#e34948", xytext=(3, -8), textcoords="offset points")
        ax.set_xscale("log")
        ax.set_yscale("log")
        rho = pd.Series(a).corr(pd.Series(b), method="spearman")
        ax.set_title(f"{p} (n={len(ids)})  ρ={rho:.2f}", fontsize=8.5)
        ax.set_xticks([0.01, 1, 100], ["0.01", "1", "100"])
        ax.set_yticks([0.01, 1, 100], ["0.01", "1", "100"])
    axs[-1, -1].axis("off")
    for ax in axs[:, 0]:
        ax.set_ylabel("Tassiane (%)")
    for ax in axs[-1, :]:
        ax.set_xlabel("Paola (%)")
    salvar(fig, "f14_generos_pareados", "Genus by genus, the same samples in the two tables",
           "Each dot is a genus: mean relative abundance over the samples present in both tables (log scale). "
           "Dashed line: identical. Red labels: largest disagreements among genera above 1%.")


# ---------------------------------------------------------------- biomarcadores
def f15():
    fig, ax = plt.subplots(figsize=(8, 7))
    d = {t: pd.read_csv(f"{R}/04_origem_biomarcadores_{t}.csv").set_index("genero") for t in TAB}
    gen = d["PAOLA"].sort_values("fracao_no_projeto_dominante").index
    y = np.arange(len(gen))
    for k, t in enumerate(TAB):
        s = d[t].reindex(gen)
        ax.plot(100 * s.fracao_no_projeto_dominante, y + (k - 0.5) * 0.25, "o", color=TAB[t], ms=6, label=TABLAB[t])
    s = d["PAOLA"].reindex(gen)
    for yy, (f, gr) in enumerate(zip(s.fracao_no_projeto_dominante, s.grupo_mais_abundante)):
        ax.text(107, yy, gr.split("|")[0], va="center", fontsize=7, color=INK2)
    ax.axvline(80, color="#e34948", lw=0.8, ls="--")
    ax.set_yticks(y, gen, fontsize=7.5)
    ax.set_xlim(0, 114)
    ax.set_xticks(range(0, 101, 20))
    ax.set_xlabel("Share of the genus' total abundance held by one study (%)")
    grade(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2)
    salvar(fig, "f15_origem_biomarcadores", "Many 'biomarkers' in the manuscript come from a single study",
           "Genera cited in the Boruta, LEfSe and heatmap figures. Right column: study holding most of the abundance (Paola table). "
           "Dashed line: 80%.")


def f16():
    fig, ax = plt.subplots(figsize=(7.5, 3))
    rows = []
    for t in TAB:
        d = pd.read_csv(f"{R}/12_abundancia_com_projeto_{t}.csv")
        for c, s in d.groupby("contraste"):
            rows.append((t, c, (s.q_sem_projeto < 0.05).sum(), (s.q_com_projeto < 0.05).sum()))
    rows = pd.DataFrame(rows, columns=["t", "c", "sem_pj", "com_pj"])
    cs = ["cancer vs control", "lesion high vs control", "lesion low vs control"]
    for k, t in enumerate(TAB):
        s = rows[rows.t == t].set_index("c").reindex(cs)
        y = np.arange(3) + (k - 0.5) * 0.3
        ax.hlines(y, s.com_pj, s.sem_pj, color=GRID, lw=3)
        ax.plot(s.sem_pj, y, "o", color=MUTED, ms=7)
        ax.plot(s.com_pj, y, "o", color=TAB[t], ms=7, mec=SURF, mew=1)
        for yy, a, b in zip(y, s.sem_pj, s.com_pj):
            ax.text(a + 1.5, yy, f"{a} → {b}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(range(3), ["Cancer vs control", "HSIL vs control", "LSIL vs control"])
    ax.invert_yaxis()
    ax.set_xlabel("Genera with q < 0.05 (CLR linear model, BH)")
    h = [plt.Line2D([], [], marker="o", ls="", color=MUTED, label="Without study term")] + \
        [plt.Line2D([], [], marker="o", ls="", color=TAB[t], label=f"With study term, {TABLAB[t]}") for t in TAB]
    ax.legend(handles=h, loc="lower right", fontsize=7)
    grade(ax)
    salvar(fig, "f16_abundancia_diferencial", "Differential abundance shrinks when study enters the model")


def forest(contraste, generos, nome, titulo, nota):
    pp = {t: pd.read_csv(f"{R}/13_meta_por_projeto_{t}.csv") for t in TAB}
    cc = {t: pd.read_csv(f"{R}/13_meta_combinado_{t}.csv") for t in TAB}
    fig, axs = plt.subplots(1, len(generos), figsize=(3.6 * len(generos), 3.4))
    for ax, g in zip(axs, generos):
        base = pp["PAOLA"]
        pjs = list(base[(base.contraste == contraste) & (base.variavel == g)].projeto)
        rot = []
        for i, pj in enumerate(pjs):
            for k, t in enumerate(TAB):
                r = pp[t][(pp[t].contraste == contraste) & (pp[t].variavel == g) & (pp[t].projeto == pj)]
                if not len(r):
                    continue
                r = r.iloc[0]
                e = 1.96 * np.sqrt(r["var"])
                y = i + (k - 0.5) * 0.3
                ax.hlines(y, r["g"] - e, r["g"] + e, color=TAB[t], lw=1.2)
                ax.plot(r["g"], y, "s", color=TAB[t], ms=5)
                if k == 0:
                    rot.append(f"{pj} ({int(r.n_caso)}/{int(r.n_controle)})")
        yp = len(pjs) + 0.3
        for k, t in enumerate(TAB):
            c = cc[t][(cc[t].contraste == contraste) & (cc[t].variavel == g)].iloc[0]
            y = yp + (k - 0.5) * 0.35
            ax.fill([c.ic95_inf, c.g_combinado, c.ic95_sup, c.g_combinado], [y, y + 0.14, y, y - 0.14], color=TAB[t])
            if k == 1:
                ax.text(1.0, 1.02, f"pooled p = {c.p:.2g} · I² = {c.I2:.0f}%", transform=ax.transAxes,
                        ha="right", va="bottom", fontsize=7, color=INK2)
        ax.set_yticks(list(range(len(pjs))) + [yp], rot + ["Pooled"], fontsize=7.5)
        ax.invert_yaxis()
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_title(g, style="italic")
        ax.set_xlabel("Hedges' g (case − control)")
        grade(ax)
    legenda_tabelas(axs[1], loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=7.5)
    salvar(fig, nome, titulo, nota)


def f17():
    forest("cancer vs control", ["Fusobacterium", "Sneathia", "Lactobacillus"], "f17_meta_cancer",
           "Meta-analysis by study: cancer vs control",
           "Effect of each genus inside each study with its own controls (n cancer/control), pooled by DerSimonian-Laird random effects. "
           "Fusobacterium and Sneathia rise in all four studies; Lactobacillus is heterogeneous.")


def f18():
    forest("HSIL vs control", ["Sneathia", "Megasphaera", "Atopobium"], "f18_meta_hsil",
           "Meta-analysis by study: HSIL vs control",
           "Same direction in all four studies with HSIL and controls; effects are small.")


def f19():
    rows = []
    for t in TAB:
        b = pd.read_csv(f"{R}/17_boruta_global_{t}.csv")
        br = pd.read_csv(f"{R}/17_boruta_repetidos_{t}.csv")
        lg = pd.read_csv(f"{R}/19_lefse_global_{t}.csv")
        lr = pd.read_csv(f"{R}/19_lefse_repetidos_{t}.csv")
        sr = pd.read_csv(f"{R}/20_shap_repetidos_{t}.csv")
        rows += [(t, "Boruta", int(b.confirmado.sum()), len(br)),
                 (t, "LEfSe (cancer vs control)", int((lg.analise == "global cancer vs control").sum()),
                  int((lr.contraste == "cancer vs control").sum()) if len(lr) else 0),
                 (t, "SHAP top 10 (cancer vs control)", 10, int((sr.contraste == "cancer vs control").sum()))]
    d = pd.DataFrame(rows, columns=["t", "metodo", "global", "rep"])
    fig, axs = plt.subplots(1, 3, figsize=(10, 2.9), sharey=False)
    for ax, (mt, s) in zip(axs, d.groupby("metodo", sort=False)):
        x = np.arange(2)
        for k, t in enumerate(TAB):
            r = s[s.t == t].iloc[0]
            ax.bar(x[0] + (k - 0.5) * 0.36, r["global"], 0.34, color=TAB[t])
            ax.bar(x[1] + (k - 0.5) * 0.36, r["rep"], 0.34, color=TAB[t])
            ax.text(x[0] + (k - 0.5) * 0.36, r["global"], f"{r['global']}", ha="center", va="bottom", fontsize=7.5)
            ax.text(x[1] + (k - 0.5) * 0.36, r["rep"], f"{r['rep']}", ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(x, ["All studies\npooled", "Within studies,\nin ≥ 2 studies"])
        ax.set_title(mt, fontsize=9)
        grade(ax, "y")
    axs[0].set_ylabel("Genera selected")
    legenda_tabelas(axs[0], loc="upper right", fontsize=7)
    salvar(fig, "f19_selecao_global_vs_por_projeto", "Feature selection collapses when study cannot contribute",
           "A genus counts within studies only if selected in at least two studies with the same direction. "
           "SHAP top 10 always returns ten genera, so its pooled bar is fixed at 10.")


# ---------------------------------------------------------------- SHAP
def f20():
    d = {t: pd.read_csv(f"{R}/20_shap_global_{t}.csv").set_index("genero") for t in TAB}
    top = (d["PAOLA"].shap_cancer.add(d["TASSI_V2"].shap_cancer, fill_value=0)).nlargest(18).index[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    y = np.arange(len(top))
    va = d["PAOLA"].shap_cancer.reindex(top).fillna(0)
    vb = d["TASSI_V2"].shap_cancer.reindex(top).fillna(0)
    ax.hlines(y, va, vb, color=GRID, lw=3)
    ax.plot(va, y, "o", color=TAB["PAOLA"], ms=7, label=TABLAB["PAOLA"])
    ax.plot(vb, y, "o", color=TAB["TASSI_V2"], ms=7, label=TABLAB["TASSI_V2"])
    dom = d["PAOLA"].reindex(top)
    for yy, g in enumerate(top):
        r = d["PAOLA"].loc[g] if g in d["PAOLA"].index else d["TASSI_V2"].loc[g]
        ax.text(max(va[g], vb[g]) + 0.0015, yy, f"{r.projeto_dominante} {100 * r.fracao_no_projeto_dominante:.0f}%",
                va="center", fontsize=7, color=INK2)
    ax.set_yticks(y, [g.replace("sem_genero", "unassigned genus") for g in top])
    ax.set_xlabel("Mean |SHAP|, cancer class (pooled Random Forest)")
    ax.set_xlim(0, max(va.max(), vb.max()) * 1.25)
    grade(ax)
    ax.legend(loc="lower right")
    salvar(fig, "f20_shap_global_comparado", "SHAP, pooled model: what the classifier uses for cancer",
           "Label: study holding most of the genus abundance. The top features differ between tables "
           "(unassigned reads concentrated in P16 in the Paola table and in P22 in the reprocessed table) and several sit in one study.")


def f21():
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.3), sharex=True, sharey=True)
    for ax, t in zip(axs, TAB):
        d = pd.read_csv(f"{R}/20_shap_global_{t}.csv")
        ax.plot(d.shap_projeto, d.shap_total, "o", ms=4, color=TAB[t], alpha=0.55)
        for _, r in d.nlargest(5, "shap_total").iterrows():
            ax.annotate(r.genero.replace("sem_genero", "unassigned")[:16], (r.shap_projeto, r.shap_total),
                        fontsize=6.5, color=INK2, xytext=(3, 2), textcoords="offset points")
        ax.set_xscale("log")
        ax.set_yscale("log")
        rho = d.shap_projeto.corr(d.shap_total, method="spearman")
        ax.set_title(f"{TABLAB[t]}  (Spearman ρ = {rho:.2f})", fontsize=9)
        ax.set_xlabel("Mean |SHAP| predicting the STUDY")
        grade(ax, "both")
    axs[0].set_ylabel("Mean |SHAP| predicting the CLINICAL GROUP")
    salvar(fig, "f21_shap_classe_vs_projeto", "Genera that predict the clinical group also predict the study",
           "Each dot is a genus. Two Random Forests on the same data: one predicting clinical group, one predicting BioProject.")


def f22():
    d = {t: pd.read_csv(f"{R}/20_shap_global_{t}.csv") for t in TAB}
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
    for ax, t in zip(axs, TAB):
        s = d[t].nlargest(30, "shap_total")
        ax.plot([0, 1], [0, 1], color=MUTED, lw=0.8, ls="--")
        ax.plot(s.eta2_classe, s.eta2_projeto, "o", color=TAB[t], ms=6, alpha=0.8)
        for _, r in s.head(8).iterrows():
            ax.annotate(r.genero.replace("sem_genero", "unassigned")[:16], (r.eta2_classe, r.eta2_projeto),
                        fontsize=6.5, color=INK2, xytext=(3, 2), textcoords="offset points")
        acima = (s.eta2_projeto > s.eta2_classe).sum()
        ax.set_title(f"{TABLAB[t]}: {acima}/30 above the line", fontsize=9)
        ax.set_xlabel("η² clinical group")
        ax.set_xlim(0, 0.75)
        ax.set_ylim(0, 0.75)
        grade(ax, "both")
    axs[0].set_ylabel("η² study")
    axs[0].text(0.5, 0.55, "explained more\nby study", fontsize=7.5, color=MUTED, rotation=0)
    salvar(fig, "f22_shap_eta2", "The 30 most important SHAP genera vary more between studies than between groups",
           "Rank-based η² of each genus' relative abundance. Above the dashed line = more variation between studies.")


def f23():
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, t in zip(axs, TAB):
        e = pd.read_csv(f"{R}/20_shap_lopo_estabilidade_{t}.csv").set_index("projeto_fora").reindex(
            [p for p in ORDEM_PJ if p != "P21" or t == "PAOLA"]).dropna()
        x = np.arange(len(e))
        ax.bar(x, e.top20_em_comum_com_global, color=TAB[t], width=0.6)
        for xx, v in zip(x, e.top20_em_comum_com_global):
            ax.text(xx, v + 0.3, f"{int(v)}", ha="center", fontsize=7.5)
        ax.set_xticks(x, e.index)
        ax.set_ylim(0, 21)
        ax.set_title(TABLAB[t], fontsize=9)
        ax.set_xlabel("Study held out")
        grade(ax, "y")
    axs[0].set_ylabel("Top-20 SHAP genera shared\nwith the pooled model")
    salvar(fig, "f23_shap_lopo", "SHAP ranking barely changes when a study is held out",
           "The model keeps using the same genera (about 16 of 20), yet leave-one-study-out AUC drops to 0.34-0.70: "
           "a stable SHAP ranking does not make the genera transferable biomarkers.")


def f24():
    fig, axs = plt.subplots(1, 2, figsize=(12, 6.5), gridspec_kw={"wspace": 0.6})
    for ax, t in zip(axs, TAB):
        d = pd.read_csv(f"{R}/20_shap_por_projeto_{t}.csv")
        d = d[d.contraste != "LSIL vs control"]
        d["col"] = d.contraste.str.replace(" vs control", "").str.replace("cancer", "Cancer") + "\n" + d.projeto
        d["v"] = d.shap_medio * np.sign(d.rho_abund_shap)
        M = d.pivot_table(index="genero", columns="col", values="v")
        M = M.loc[M.notna().sum(axis=1).sort_values(ascending=False).index[:24]]
        M = M.rename(index=lambda g: g.replace("sem_genero", "unassigned")[:22])
        lim = np.nanmax(np.abs(M.values))
        ax.imshow(M.values, cmap=DIVERG, vmin=-lim, vmax=lim, aspect="auto")
        for (i, j), v in np.ndenumerate(M.values):
            if np.isnan(v):
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color="#fafaf8"))
        ax.set_xticks(range(M.shape[1]), M.columns, fontsize=7)
        ax.set_yticks(range(M.shape[0]), M.index, fontsize=7, style="italic")
        ax.set_title(TABLAB[t], fontsize=9)
        for s in ax.spines.values():
            s.set_visible(False)
    sm = plt.cm.ScalarMappable(cmap=DIVERG, norm=plt.Normalize(-1, 1))
    cb = fig.colorbar(sm, ax=axs, shrink=0.5, ticks=[-1, 0, 1], pad=0.02)
    cb.ax.set_yticklabels(["control", "0", "case"], fontsize=7.5)
    cb.set_label("signed mean |SHAP| (higher abundance pushes to …)", fontsize=7.5)
    salvar(fig, "f24_shap_dentro_projetos", "SHAP inside each study: genera in the top 10",
           "Random Forest per study and contrast. Red: more abundant in the case; blue: in controls. Blank: not in the top 10. "
           "Atopobium (HSIL) and Lactobacillus/Corynebacterium (cancer) repeat across studies; P22 is driven by reagent genera.")


def f25():
    auto = {"cancer": 0.606, "control": 0.581, "lesion high": 0.533, "lesion low": 0.663}
    fixa = {"cancer": 0.606, "control": 0.419, "lesion high": 0.467, "lesion low": 0.337}
    fig, ax = plt.subplots(figsize=(7, 2.9))
    y = np.arange(4)
    for i, c in enumerate(CLS):
        ax.annotate("", xy=(fixa[c], i), xytext=(auto[c], i),
                    arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.2) if auto[c] != fixa[c] else None)
        ax.plot(auto[c], i, "o", color=GRID, mec=INK2, ms=8)
        ax.plot(fixa[c], i, "o", color=TAB["TASSI_V2"], ms=8)
    ax.axvline(0.5, color=MUTED, lw=0.8, ls="--")
    ax.set_yticks(y, [CLSLAB[c] for c in CLS])
    ax.invert_yaxis()
    ax.set_xlabel("Leave-one-study-out AUC (Tassiane's random_forest.R)")
    h = [plt.Line2D([], [], marker="o", ls="", mfc=GRID, mec=INK2, label='pROC direction = "auto" (macro 0.596)'),
         plt.Line2D([], [], marker="o", ls="", color=TAB["TASSI_V2"], label='direction fixed (macro 0.457)')]
    ax.legend(handles=h, loc="lower right", fontsize=7.5)
    grade(ax)
    salvar(fig, "f25_proc_direcao", "pROC's automatic direction hides below-chance AUCs",
           'With direction = "auto", pROC flips any AUC below 0.5 to 1 - AUC. Fixing the direction shows control, HSIL '
           "and LSIL below chance in unseen studies.")


def f26():
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.2))
    for ax, t in zip(axs, TAB):
        d = pd.read_csv(f"{R}/11_contaminantes_por_projeto_{t}.csv").set_index("Project").reindex(ORDEM_PJ)
        d = d[CLS].dropna(how="all")
        M = d.values.astype(float)
        cm = LinearSegmentedColormap.from_list("s", ["#f7f6f3", "#e34948"])
        ax.imshow(np.nan_to_num(M, nan=0), cmap=cm, vmin=0, vmax=8, aspect="auto")
        for (i, j), v in np.ndenumerate(M):
            ax.text(j, i, "–" if np.isnan(v) else f"{v:.1f}", ha="center", va="center", fontsize=7.5,
                    color=SURF if (not np.isnan(v) and v > 5) else INK)
        ax.set_xticks(range(4), [CLSLAB[c] for c in CLS])
        ax.set_yticks(range(len(d)), d.index)
        ax.set_title(TABLAB[t], fontsize=9)
        for s in ax.spines.values():
            s.set_visible(False)
    salvar(fig, "f26_contaminantes", "Reagent-associated genera: % of reads by study and group",
           "Genera recognised as kit/laboratory contaminants (Salter et al. list). Removing them does not change "
           "leave-one-study-out AUC (0.63) or study prediction (83-85%).")


def f27():
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1, 1.2]})
    ax = axs[0]
    d = pd.read_csv(f"{R}/22_embaralhado_dentro_estudo.csv")
    for k, t in enumerate(TAB):
        s = d[d.tabela == t]
        real = s[s.rotulos == "reais"][CLS].iloc[0]
        emb = s[s.rotulos != "reais"][CLS].mean()
        for i, c in enumerate(CLS):
            y = i + (k - 0.5) * 0.3
            ax.hlines(y, emb[c], real[c], color=GRID, lw=3)
            ax.plot(real[c], y, "o", color=TAB[t], ms=7)
            ax.plot(emb[c], y, "o", mfc=SURF, mec=TAB[t], mew=1.6, ms=7)
    ax.set_yticks(range(4), [CLSLAB[c] for c in CLS])
    ax.invert_yaxis()
    ax.axvline(0.5, color=MUTED, lw=0.8, ls="--")
    ax.set_xlim(0.45, 1.0)
    ax.set_xlabel("AUC, random 10-fold CV")
    ax.set_title("A. Labels shuffled within each study")
    h = [plt.Line2D([], [], marker="o", ls="", color=INK2, label="true labels"),
         plt.Line2D([], [], marker="o", ls="", mfc=SURF, mec=INK2, label="shuffled within study (mean of 10)")]
    ax.legend(handles=h, loc="lower left", fontsize=7)
    grade(ax)
    ax = axs[1]
    c = pd.read_csv(f"{R}/22c_curva_sem_P22.csv")
    c = c[c.modelo == "RF"]
    for t in TAB:
        for fonte, ls, mk in [("estudos mistos (pareados)", "-", "o"), ("+ estudos de uma classe", "--", "s")]:
            s = c[(c.tabela == t) & (c.fonte == fonte)].groupby("fracao").agg(n=("n_treino", "mean"), auc=("auc", "mean"))
            if fonte.startswith("+"):
                base = c[(c.tabela == t) & (c.fonte.str.startswith("estudos")) & (c.fracao == 1.0)].agg(
                    n=("n_treino", "mean"), auc=("auc", "mean"))
                s = pd.concat([pd.DataFrame({"n": [base.loc["n", "n_treino"]], "auc": [base.loc["auc", "auc"]]}), s])
            ax.plot(s.n, s.auc, ls=ls, marker=mk, color=TAB[t], ms=5, lw=1.5)
    ax.axhline(0.5, color=MUTED, lw=0.8, ls="--")
    ax.set_xlabel("Training samples, cancer vs control")
    ax.set_ylabel("AUC in the held-out study (P1, P2, P19)")
    ax.set_ylim(0.45, 0.9)
    ax.set_title("B. More samples: paired vs single-class studies")
    h = [plt.Line2D([], [], ls="-", marker="o", color=INK2, label="from studies with both groups (paired)"),
         plt.Line2D([], [], ls="--", marker="s", color=INK2, label="adding single-class studies")]
    h += [plt.Line2D([], [], marker="o", ls="", color=TAB[t], label=TABLAB[t]) for t in TAB]
    ax.legend(handles=h, loc="lower right", fontsize=7)
    grade(ax, "y")
    salvar(fig, "f27_n_e_pareamento", "Does a larger N from single-class studies help?",
           "A: shuffling the clinical labels inside each study keeps about 95% of the random-CV AUC, so the pooled AUC "
           "comes from which study a sample belongs to. B: Random Forest, P22 excluded (batch confounded). About 100 paired "
           "samples give the same AUC on an unseen study as adding 350-450 samples from cancer-only and control-only studies.")


CSTCOR = {"I": "#2a78d6", "II": "#1baf7a", "III": "#6250d6", "V": "#008300", "IV-B": "#eda100", "IV-C": "#e34948"}
CSTLAB = {"I": "I · L. crispatus", "II": "II · L. gasseri", "III": "III · L. iners", "V": "V · L. jensenii",
          "IV-B": "IV-B · Gardnerella/Atopobium", "IV-C": "IV-C · other anaerobes, Streptococcus…"}


def f28():
    d = pd.read_csv(f"{R}/23_cst_por_amostra.csv")
    grupos = [(p, c) for p in ORDEM_PJ for c in CLS if ((d.Project == p) & (d.tipo_amostra == c)).sum() >= 4]
    fig, ax = plt.subplots(figsize=(12, 4.4))
    x, ticks, labs, xp = 0, [], [], {}
    ultimo = None
    for p, c in grupos:
        if ultimo and p != ultimo:
            x += 0.7
        s = d[(d.Project == p) & (d.tipo_amostra == c)]
        base = 0
        for k in CSTCOR:
            v = 100 * (s.CST == k).mean()
            ax.bar(x, v, bottom=base, color=CSTCOR[k], width=0.82, edgecolor=SURF, lw=0.8)
            base += v
        ax.text(x, 101.5, f"{len(s)}", ha="center", fontsize=6.5, color=INK2)
        ticks.append(x)
        labs.append(CLSLAB[c])
        xp.setdefault(p, []).append(x)
        ultimo = p
        x += 1
    ax.set_xticks(ticks, labs, rotation=90, fontsize=7)
    for p, xs in xp.items():
        ax.text(np.mean(xs), -36, p, ha="center", fontsize=8.5, fontweight="bold", color=INK)
    ax.set_ylabel("Samples (%)")
    ax.set_ylim(0, 106)
    h = [plt.Rectangle((0, 0), 1, 1, color=CSTCOR[k], label=CSTLAB[k]) for k in CSTCOR]
    ax.legend(handles=h, loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=7.5)
    salvar(fig, "f28_cst_por_projeto", "Vaginal community state types (VALENCIA) by study and clinical group",
           "Reprocessed table; Lactobacillus species assigned by alignment to vSpeciateDB references. Number above each bar = samples "
           "(groups with at least 4). CST IV = low Lactobacillus.")


def f29():
    L = pd.read_csv(f"{R}/23_cst_por_estudo.csv")
    K = pd.read_csv(f"{R}/23_cst_meta.csv")
    desf = [("CST IV (sem dominância de Lactobacillus)", "CST IV (low Lactobacillus)"),
            ("CST I (L. crispatus)", "CST I (L. crispatus)"), ("CST III (L. iners)", "CST III (L. iners)")]
    comps = [("cancer vs control", "Cancer"), ("HSIL vs control", "HSIL"), ("LSIL vs control", "LSIL")]
    fig, axs = plt.subplots(1, 3, figsize=(12, 5.2), sharey=True)
    for ax, (dk, dl_) in zip(axs, desf):
        y, rot = 0, []
        for ck, cl_ in comps:
            s = L[(L.desfecho == dk) & (L.contraste == ck)]
            for _, r in s.iterrows():
                e = 1.96 * np.sqrt(r["var"])
                lo = np.clip([r.log_or - e, r.log_or, r.log_or + e], -4, 4)
                cor = MUTED if r.projeto == "P22" else INK2
                ax.hlines(y, lo[0], lo[2], color=cor, lw=1.2)
                ax.plot(lo[1], y, "s", color=cor, ms=5, mfc=SURF if r.projeto == "P22" else cor)
                rot.append(f"{cl_} · {r.projeto} ({int(r.n_caso)}/{int(r.n_controle)})")
                y += 1
            k = K[(K.desfecho == dk) & (K.contraste == ck)].iloc[0]
            for j, (orv, a, b, p, lab, cor) in enumerate([
                    (k.OR, k.ic_inf, k.ic_sup, k.p, "pooled", CLSCOR["cancer" if ck.startswith("cancer") else
                                                                     "lesion high" if ck.startswith("HSIL") else "lesion low"]),
                    (k.OR_sem_P22, k.ic_inf_sem_P22, k.ic_sup_sem_P22, k.p_sem_P22, "pooled without P22", INK)]):
                if not np.isfinite(orv):
                    continue
                lm, la, lb = np.log(orv), np.log(a), np.log(b)
                ax.fill([la, lm, lb, lm], [y, y + 0.28, y, y - 0.28], color=cor)
                ax.text(4.1, y, f"p = {p:.2g}", fontsize=6.5, color=INK2, va="center")
                rot.append(f"{cl_} · {lab}")
                y += 1
            y += 0.6
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_xlim(-4, 5)
        ax.set_xticks(np.log([0.05, 0.2, 1, 5, 20]), ["0.05", "0.2", "1", "5", "20"])
        ax.set_xlabel("Odds ratio, case vs control (log scale)")
        ax.set_title(dl_)
        grade(ax)
        ax.invert_yaxis()
    ys, labs = [], []
    yy = 0
    for ck, cl_ in comps:
        s = L[(L.desfecho == desf[0][0]) & (L.contraste == ck)]
        for _, r in s.iterrows():
            ys.append(yy); labs.append(f"{cl_} · {r.projeto} ({int(r.n_caso)}/{int(r.n_controle)})"); yy += 1
        k = K[(K.desfecho == desf[0][0]) & (K.contraste == ck)].iloc[0]
        ys.append(yy); labs.append(f"{cl_} · pooled"); yy += 1
        if np.isfinite(k.OR_sem_P22):
            ys.append(yy); labs.append(f"{cl_} · pooled without P22"); yy += 1
        yy += 0.6
    axs[0].set_yticks(ys, labs, fontsize=7.5)
    salvar(fig, "f29_cst_meta", "Community state types inside each study",
           "Squares: odds ratio inside each study (n case/control), 95% CI; hollow grey = P22 (case and control in different runs). "
           "Diamonds: random-effects pooled estimate, with and without P22. Right of 1 = more frequent in the case group.")


if __name__ == "__main__":
    import sys
    so = sys.argv[1:]
    for nome, f in sorted((k, v) for k, v in globals().items() if k[:1] == "f" and k[1:].isdigit()):
        if so and nome not in so:
            continue
        try:
            f()
        except Exception:
            print("ERRO", nome)
            traceback.print_exc()
