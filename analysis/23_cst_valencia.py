"""Tipos de comunidade vaginal (CSTs) com o VALENCIA, e comparação dentro de cada estudo.

CSTs (France et al. 2020, Microbiome): I = L. crispatus, II = L. gasseri, III = L. iners,
V = L. jensenii, IV = baixa abundância de Lactobacillus (IV-A/IV-B com Gardnerella e
Atopobium; IV-C com Prevotella, Streptococcus, Enterococcus, Bifidobacterium ou Staphylococcus).

O VALENCIA precisa de espécie para Lactobacillus, Gardnerella, Atopobium e Sneathia. O SILVA
138 não separa L. crispatus nem L. gasseri nas nossas ASVs, então:
  - as ASVs desses gêneros são alinhadas (edlib, alinhamento da ASV dentro da referência)
    às sequências de referência do speciateIT/vSpeciateDB (Holm et al. 2024), V3-V4 ou V4
    conforme a região; recebe a espécie se a identidade for >= 97% e o melhor acerto for de
    uma única espécie vaginal (empates com espécies não vaginais quase idênticas no trecho,
    como L. acidophilus/helveticus para L. crispatus, ficam com a espécie vaginal);
  - Prevotella é somada em g_Prevotella, na amostra e nos centróides (como o README do
    VALENCIA recomenda quando a nomenclatura de Prevotella não bate).
Só a tabela reprocessada (TASSI_V2) tem as sequências das ASVs; a da Paola só tem nomes.

Comparação: proporção de CST IV (sem dominância de Lactobacillus) e de CST III (L. iners)
em casos x controles dentro de cada estudo que tem os dois grupos; odds ratio com correção
de 0,5 e meta-análise de efeitos aleatórios (DerSimonian-Laird).

Variáveis: DATA_DIR (tabelas da Tassiane), P22_DEBLUR_DIR (saída do deblur do P22),
SPECIATEIT_DIR e VALENCIA_DIR (clones de github.com/ravel-lab/speciateIT e /VALENCIA).
"""
import os

import edlib
import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.stats import fisher_exact, norm

from common import OUT_DIR, biom, fasta, meta, path, tassi_v2, unzip_qza

SPEC = os.environ["SPECIATEIT_DIR"]
VAL = os.environ["VALENCIA_DIR"]
DEB = os.environ["P22_DEBLUR_DIR"]
GENEROS_ESPECIE = {"Lactobacillus", "Gardnerella", "Atopobium", "Fannyhessea", "Sneathia"}
VAGINAIS = {"Lactobacillus crispatus": "Lactobacillus_crispatus", "Lactobacillus iners": "Lactobacillus_iners",
            "Lactobacillus gasseri": "Lactobacillus_gasseri", "Lactobacillus paragasseri": "Lactobacillus_gasseri",
            "Lactobacillus jensenii": "Lactobacillus_jensenii", "Lactobacillus mulieris": "Lactobacillus_jensenii",
            "Fannyhessea vaginae": "Atopobium_vaginae", "Sneathia sanguinegens": "Sneathia_sanguinegens",
            "Sneathia vaginalis": "Sneathia_amnii", "Sneathia amnii": "Sneathia_amnii"}
CONTRASTES = {"cancer vs control": "cancer", "HSIL vs control": "lesion high", "LSIL vs control": "lesion low"}


def referencias(regiao):
    seqs, nomes = [], []
    arq = f"{SPEC}/training_data/vSpeciateIT_{'V3V4' if regiao == 'V3V4' else 'V4V4'}.fasta"
    nome = None
    for l in open(arq):
        if l.startswith(">"):
            nome = l.split("s__")[1].split(" [")[0] if "s__" in l else None
        elif nome:
            g = nome.split()[0]
            if g in GENEROS_ESPECIE or g.startswith("Gardnerella"):
                seqs.append(l.strip().upper())
                nomes.append(nome)
    return seqs, nomes


def especie(asv, refs):
    seqs, nomes = refs
    melhor, quem = 10 ** 9, set()
    for s, n in zip(seqs, nomes):
        d = edlib.align(asv, s, mode="HW", task="distance", k=min(melhor, int(0.03 * len(asv))))["editDistance"]
        if d == -1:
            continue
        if d < melhor:
            melhor, quem = d, {n}
        elif d == melhor:
            quem.add(n)
    if not quem:
        return None, None
    ident = 1 - melhor / len(asv)
    mapa = {("Gardnerella_vaginalis" if n.startswith("Gardnerella") else VAGINAIS.get(n)) for n in quem}
    vag = {x for x in mapa if x}
    if len(vag) == 1:
        return vag.pop(), ident
    return None, ident


def taxonomia_qza(nome):
    t = pd.read_csv(os.path.join(unzip_qza(path("tassi", nome)), "taxonomy.tsv"), sep="\t", index_col=0)
    return t.Taxon


def genero_de(tax):
    for parte in tax.split(";"):
        parte = parte.strip()
        if parte.startswith("g__") and len(parte) > 3:
            return parte[3:]
    return None


def nome_valencia(g):
    if g is None:
        return "d_NA"
    if g.startswith("Prevotella"):
        return "g_Prevotella"
    return "g_" + g.replace("-", ".").replace(" ", "_")


# ------------------------------------------------------------------ ASVs da tabela reprocessada
m = meta()
amostras = tassi_v2().index
blocos = []
for reg, tab, seqs_qza, tax_qza in [("V3V4", "V3V4_table.qza", "V3V4_repseqs.qza", "V3V4_taxonomy.qza"),
                                     ("V4", "V4_table.qza", "V4_repseqs.qza", "V4_taxonomy.qza")]:
    T = biom(path("tassi", tab))
    T = T.loc[T.index.intersection(amostras)]
    T = T.drop(index=T.index.intersection(m.index[m.Project == "P22"]))
    sq = fasta(os.path.join(unzip_qza(path("tassi", seqs_qza)), "dna-sequences.fasta"))
    tx = taxonomia_qza(tax_qza)
    blocos.append((reg, T, {k: sq[k] for k in T.columns}, {k: tx.get(k, "") for k in T.columns}))

f = h5py.File(os.path.join(DEB, "reference-hit.biom"), "r")
obs = [x.decode() for x in f["observation/ids"][:]]
smp = [x.decode() for x in f["sample/ids"][:]]
M = sp.csr_matrix((f["observation/matrix/data"][:], f["observation/matrix/indices"][:],
                   f["observation/matrix/indptr"][:]), shape=(len(obs), len(smp)))
P22 = pd.DataFrame(M.T.toarray(), index=smp, columns=obs)
P22 = P22.loc[P22.index.intersection(amostras)]
p22tax = pd.read_csv(f"{OUT_DIR}/08b_p22_taxonomia_asvs.csv").set_index("asv").taxonomia
p22seq = dict(zip(obs, [o.upper() for o in obs])) if all(set(o.upper()) <= set("ACGTN") for o in obs[:20]) else \
    fasta(os.path.join(DEB, "reference-hit.seqs.fa"))
blocos.append(("V3V4", P22, {k: p22seq[k] for k in P22.columns}, {k: p22tax.get(p22seq[k], "") for k in P22.columns}))

refs = {"V3V4": referencias("V3V4"), "V4": referencias("V4")}
linhas_tab, cont = [], []
for reg, T, sq, tx in blocos:
    nomes = {}
    for k in T.columns:
        g = genero_de(tx[k])
        if g in GENEROS_ESPECIE or (g or "").startswith("Gardnerella"):
            esp, ident = especie(sq[k], refs[reg])
            if esp is None and g.startswith("Gardnerella"):
                esp = "Gardnerella_vaginalis"  # o VALENCIA usa G. vaginalis para o gênero todo (no GTDB ele foi dividido)
            nomes[k] = esp or nome_valencia(g)
            cont.append(dict(regiao=reg, genero=g, especie=esp, identidade=ident, leituras=int(T[k].sum())))
        else:
            nomes[k] = nome_valencia(g)
    linhas_tab.append(T.T.groupby(pd.Series(nomes)).sum().T)
X = pd.concat(linhas_tab).fillna(0)
X = X.loc[:, X.sum() > 0]
C = pd.DataFrame(cont)
lido = C.groupby(["genero", C.especie.fillna("sem espécie")]).leituras.sum().sort_values(ascending=False)
print("Leituras por espécie atribuída (gêneros-chave):")
print(lido.head(20).to_string())
lac = C[C.genero == "Lactobacillus"]
print(f"Lactobacillus: {100 * lac[lac.especie.notna()].leituras.sum() / lac.leituras.sum():.1f}% das leituras com espécie")

# ------------------------------------------------------------------ VALENCIA
ref = pd.read_csv(f"{VAL}/CST_centroids_012920.csv")
prev = [c for c in ref.columns if c.startswith("Prevotella_") or c == "g_Prevotella"]
ref["g_Prevotella"] = ref[prev].sum(axis=1)
ref = ref.drop(columns=[c for c in prev if c != "g_Prevotella"])
if "g_Corynebacterium_1" in ref:
    ref["g_Corynebacterium"] = ref.get("g_Corynebacterium", 0) + ref["g_Corynebacterium_1"]
    ref = ref.drop(columns="g_Corynebacterium_1")
# Similaridade de Yue-Clayton (theta) de cada amostra a cada centróide, como no Valencia.py
# (reimplementado em forma vetorial porque o script original não roda com pandas >= 2).
cent = ref.set_index("sub_CST")
cols = sorted(set(cent.columns) | set(X.columns))
Q = cent.reindex(columns=cols, fill_value=0).fillna(0).values
P = X.reindex(columns=cols, fill_value=0).div(X.sum(axis=1), axis=0).values
prod = P @ Q.T
dif = (P ** 2).sum(axis=1)[:, None] + (Q ** 2).sum(axis=1)[None, :] - 2 * prod
sim = prod / (dif + prod)
out = pd.DataFrame({"subCST": cent.index[sim.argmax(axis=1)], "score": sim.max(axis=1)}, index=X.index)
out["CST"] = out.subCST.replace({"I-A": "I", "I-B": "I", "III-A": "III", "III-B": "III", "IV-C0": "IV-C",
                                 "IV-C1": "IV-C", "IV-C2": "IV-C", "IV-C3": "IV-C", "IV-C4": "IV-C"})
out = out.join(m[["Project", "tipo_amostra"]])
out["IV"] = out.CST.str.startswith("IV")
out.to_csv(f"{OUT_DIR}/23_cst_por_amostra.csv")
print(f"\n{len(out)} amostras; similaridade mediana {out.score.median():.2f} "
      f"({(out.score < 0.5).mean() * 100:.0f}% abaixo de 0,5)")

tab = pd.crosstab([out.Project, out.tipo_amostra], out.CST)
tab.to_csv(f"{OUT_DIR}/23_cst_por_projeto_classe.csv")
print(tab.to_string())


# ------------------------------------------------------------------ comparações dentro do estudo
def log_or(a, b, c, d):
    a, b, c, d = a + .5, b + .5, c + .5, d + .5
    return np.log(a * d / (b * c)), 1 / a + 1 / b + 1 / c + 1 / d


def dl(y, v):
    y, v = np.array(y), np.array(v)
    w = 1 / v
    mu = (w * y).sum() / w.sum()
    q = (w * (y - mu) ** 2).sum()
    k = len(y)
    t2 = max(0, (q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0
    ws = 1 / (v + t2)
    mu = (ws * y).sum() / ws.sum()
    se = np.sqrt(1 / ws.sum())
    i2 = max(0, (q - (k - 1)) / q) * 100 if q > 0 else 0
    return mu, se, 2 * norm.sf(abs(mu / se)), i2


linhas, comb = [], []
for desfecho, col in [("CST IV (sem dominância de Lactobacillus)", "IV"), ("CST III (L. iners)", "III"),
                      ("CST I (L. crispatus)", "I")]:
    o = out.copy()
    o["y"] = o.IV if col == "IV" else (o.CST == col)
    for comp, classe in CONTRASTES.items():
        ys, vs = [], []
        for pj, s in o.groupby("Project"):
            ca, co = s[s.tipo_amostra == classe], s[s.tipo_amostra == "control"]
            if len(ca) < 5 or len(co) < 5:  # o P1 tem 4 controles: com uma célula zero, a correção de 0,5 inverte o sinal
                continue
            a, b = int(ca.y.sum()), len(ca) - int(ca.y.sum())
            c, d = int(co.y.sum()), len(co) - int(co.y.sum())
            lo, v = log_or(a, b, c, d)
            linhas.append(dict(desfecho=desfecho, contraste=comp, projeto=pj, n_caso=len(ca), n_controle=len(co),
                               pct_caso=100 * a / len(ca), pct_controle=100 * c / len(co), log_or=lo, var=v,
                               p_fisher=fisher_exact([[a, b], [c, d]])[1]))
            ys.append(lo)
            vs.append(v)
        if ys:
            pjs_ok = [l["projeto"] for l in linhas if l["desfecho"] == desfecho and l["contraste"] == comp]
            sem22 = [(y_, v_) for y_, v_, q in zip(ys, vs, pjs_ok) if q != "P22"]
            mu2, se2, p2, _ = dl([x[0] for x in sem22], [x[1] for x in sem22]) if len(sem22) < len(ys) else (np.nan,) * 4
            mu, se, p, i2 = dl(ys, vs)
            o2 = o[o.tipo_amostra.isin([classe, "control"])]
            comb.append(dict(desfecho=desfecho, contraste=comp, k=len(ys), OR=np.exp(mu), ic_inf=np.exp(mu - 1.96 * se),
                             ic_sup=np.exp(mu + 1.96 * se), p=p, I2=i2,
                             mesma_direcao=f"{sum(np.sign(ys) == np.sign(mu))}/{len(ys)}",
                             OR_sem_P22=np.exp(mu2), ic_inf_sem_P22=np.exp(mu2 - 1.96 * se2),
                             ic_sup_sem_P22=np.exp(mu2 + 1.96 * se2), p_sem_P22=p2,
                             OR_ingenuo_todos_juntos=np.exp(log_or(
                                 int(o2[o2.tipo_amostra == classe].y.sum()), int((~o2[o2.tipo_amostra == classe].y).sum()),
                                 int(o2[o2.tipo_amostra == "control"].y.sum()), int((~o2[o2.tipo_amostra == "control"].y).sum()))[0])))
L, K = pd.DataFrame(linhas), pd.DataFrame(comb)
L.to_csv(f"{OUT_DIR}/23_cst_por_estudo.csv", index=False)
K.to_csv(f"{OUT_DIR}/23_cst_meta.csv", index=False)
C.to_csv(f"{OUT_DIR}/23_especies_asvs.csv", index=False)
print("\nDentro de cada estudo:")
print(L.round(2).to_string(index=False))
print("\nMeta-análise (OR > 1 = mais frequente no caso):")
print(K.round(3).to_string(index=False))
