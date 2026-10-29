"""Estudos novos do SRA (com caso e controle no mesmo estudo): tabelas, CSTs e meta-análise.

Entrada: a saída do deblur de 25_novos_estudos.sh (NOVOS_DIR/<estudo>/deb) e os metadados por
amostra de 24d_metadados_por_amostra.py (results/24d_metadados_por_amostra.csv). O PRJNA1085021
não precisa do 24d: o grupo está no nome da amostra (CC, HS, He).

Taxonomia:
  - V3-V4 (250 nt) e V4 (220 nt): mesma região e comprimento das ASVs do pipeline da Tassiane.
    Cada ASV recebe a taxonomia SILVA da ASV idêntica já classificada (consenso, se houver mais
    de uma) ou, sem correspondência exata, a de um Naive Bayes de k-mers (k = 7) treinado nessas
    ASVs, truncada onde a confiança cai abaixo de 0,7 (o mesmo método do 08b para o P22).
  - V1-V3 (PRJEB40437): não há ASVs dessa região no pipeline; o gênero vem do melhor acerto
    (vsearch, identidade >= 97%) nas referências V1-V3 do vSpeciateDB (taxonomia GTDB; Fannyhessea
    renomeado para Atopobium, como no SILVA). Gêneros fora do banco vaginal ficam sem gênero.
  - Espécies de Lactobacillus, Gardnerella, Atopobium e Sneathia e CSTs: como no 23_cst_valencia.py.

Análises: (1) g de Hedges em CLR e Shannon, por estudo, juntando os estudos novos aos efeitos
da tabela reprocessada (13_meta_por_projeto_TASSI_V2.csv) numa nova meta-análise; (2) odds
ratio de CST IV, I e III por estudo, juntando aos do 23_cst_por_estudo.csv. As duas com e sem o
P22 (lote confundido com a classe).

Variáveis: NOVOS_DIR, DATA_DIR, SPECIATEIT_DIR, VALENCIA_DIR e ENV_BIN (pasta com o vsearch).
"""
import os
import subprocess
import tempfile

import edlib
import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.stats import fisher_exact, norm
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB

from common import OUT_DIR, fasta, genero, path, unzip_qza

NOVOS = os.environ["NOVOS_DIR"]
SPEC = os.environ["SPECIATEIT_DIR"]
VAL = os.environ["VALENCIA_DIR"]
VSEARCH = os.path.join(os.environ.get("ENV_BIN", ""), "vsearch")
ESTUDOS = {"PRJNA1085021": ("V3V4", 250), "PRJNA308947": ("V3V4", 250),
           "PRJNA622998": ("V4", 220), "PRJEB40437": ("V1V3", 250)}
GENEROS = ["Lactobacillus", "Gardnerella", "Prevotella", "Fusobacterium", "Porphyromonas", "Bacteroides",
           "Peptostreptococcus", "Streptococcus", "Sneathia", "Atopobium", "Megasphaera", "Dialister",
           "Anaerococcus", "Peptoniphilus", "Campylobacter", "Pseudomonas", "Ureaplasma", "Finegoldia"]
COMPARACOES = {"cancer vs control": "cancer", "HSIL vs control": "lesion high", "LSIL vs control": "lesion low"}
MIN_LEITURAS = 1000


# ------------------------------------------------------------------ grupos clínicos
def grupos():
    ri = pd.read_csv(f"{OUT_DIR}/24b_runinfo.csv")
    g = {}
    s = ri[ri.bioproject == "PRJNA1085021"]
    for run, nome in zip(s.Run, s.SampleName.astype(str)):
        g[run] = {"CC": "cancer", "HS": "lesion high", "He": "control"}.get(nome[:2])
    arq = f"{OUT_DIR}/24d_metadados_por_amostra.csv"
    if not os.path.exists(arq):
        print("Sem 24d_metadados_por_amostra.csv: só o PRJNA1085021 terá grupos.")
        return g
    M = pd.read_csv(arq, dtype=str)
    col = lambda d, *nomes: next((d[c] for c in nomes if c in d), pd.Series(index=d.index, dtype=str))
    for pj, d in M.groupby("bioproject"):
        if pj == "PRJNA308947":
            h = col(d, "health_state").str.lower()
            v = np.select([h.str.startswith("cc"), h.str.contains("lsil"), h.str.startswith("healthy")],
                          ["cancer", "lesion low", "control"], default=None)
        elif pj == "PRJNA622998":
            c = col(d, "Cytology").str.upper()
            desc = col(d, "description").str.lower()
            v = np.select([c.str.contains("LGSIL"), c.str.contains("HGSIL"),
                           c.str.contains("NOT APPLICABLE") & desc.str.contains("vaginal swab")],
                          ["lesion low", "lesion high", "control"], default=None)
        elif pj == "PRJEB40437":
            c = col(d, "gynecological disorder", "gynecological_disorder").str.upper()
            # NIC antes da excisão (tratamento indicado para NIC 2+) x mulheres sem lesão; o pós-excisão fica fora
            v = np.select([c.eq("PRE"), c.eq("NORMAL")], ["lesion high", "control"], default=None)
        else:
            continue
        g.update(dict(zip(d.Run, v)))
    return g


# ------------------------------------------------------------------ tabela de ASVs do deblur
def deblur(estudo):
    f = h5py.File(os.path.join(NOVOS, estudo, "deb", "reference-hit.biom"), "r")
    obs = [x.decode().upper() for x in f["observation/ids"][:]]
    smp = [x.decode().split(".")[0] for x in f["sample/ids"][:]]
    M = sp.csr_matrix((f["observation/matrix/data"][:], f["observation/matrix/indices"][:],
                       f["observation/matrix/indptr"][:]), shape=(len(obs), len(smp)))
    return pd.DataFrame(M.T.toarray(), index=smp, columns=obs)


# ------------------------------------------------------------------ taxonomia
def consenso(taxas):
    out = []
    for nivel in zip(*[t.split("; ") for t in taxas]):
        if len(set(nivel)) != 1:
            break
        out.append(nivel[0])
    return "; ".join(out) if out else "Unassigned"


def consenso_confianca(probs, classes, limite=0.7):
    top = classes[probs.argmax()].split("; ")
    out = []
    for nivel in range(1, len(top) + 1):
        pref = "; ".join(top[:nivel])
        if probs[[c == pref or c.startswith(pref + ";") for c in classes]].sum() < limite:
            break
        out.append(top[nivel - 1])
    return "; ".join(out) if out else "Unassigned"


_ref = {}


def classificador(regiao, trim):
    if (regiao, trim) not in _ref:
        nome = "V3V4" if regiao == "V3V4" else "V4"
        sq = fasta(os.path.join(unzip_qza(path("tassi", f"{nome}_repseqs.qza")), "dna-sequences.fasta"))
        tx = pd.read_csv(os.path.join(unzip_qza(path("tassi", f"{nome}_taxonomy.qza")), "taxonomy.tsv"),
                         sep="\t", index_col=0)["Taxon"]
        ref = pd.DataFrame({"seq": pd.Series(sq), "tax": tx}).dropna()
        ref["seq"] = ref.seq.str.upper().str[:trim]
        por_seq = ref.groupby("seq").tax.agg(lambda t: consenso(list(t)))
        vec = HashingVectorizer(analyzer="char", ngram_range=(7, 7), n_features=8192, alternate_sign=False, norm="l1")
        nb = MultinomialNB(alpha=0.001, fit_prior=False).fit(vec.transform(por_seq.index), por_seq.values)
        _ref[(regiao, trim)] = (por_seq, vec, nb)
    return _ref[(regiao, trim)]


def taxonomia(asvs, regiao, trim):
    asvs = pd.Series(asvs, index=asvs)
    if regiao == "V1V3":
        with tempfile.TemporaryDirectory() as d:
            with open(f"{d}/q.fa", "w") as fh:
                for i, s in enumerate(asvs):
                    fh.write(f">a{i}\n{s}\n")
            refs, lin = [], {}
            nome = None
            for l in open(f"{SPEC}/training_data/vSpeciateIT_V1V3.fasta"):
                if l.startswith(">"):
                    k = l[1:].split()[0]
                    lin[k] = l.split(" ", 1)[1].split(" [")[0] if " " in l else ""
                    nome = k
            subprocess.run([VSEARCH, "--usearch_global", f"{d}/q.fa", "--db", f"{SPEC}/training_data/vSpeciateIT_V1V3.fasta",
                            "--id", "0.97", "--blast6out", f"{d}/hits.tsv", "--maxaccepts", "1", "--threads", "4",
                            "--quiet"], check=True)
            hits = pd.read_csv(f"{d}/hits.tsv", sep="\t", header=None) if os.path.getsize(f"{d}/hits.tsv") else pd.DataFrame()
        tax = pd.Series("Unassigned", index=asvs.index)
        for _, h in hits.iterrows():
            l = lin.get(h[1], "").replace("g__Fannyhessea", "g__Atopobium")
            partes = [p.strip() for p in l.split(";")][:6]
            tax.iloc[int(h[0][1:])] = "; ".join(partes)
        return tax, pd.Series(np.where(tax != "Unassigned", "vSpeciateDB", "sem acerto"), index=asvs.index)
    por_seq, vec, nb = classificador(regiao, trim)
    tax = asvs.map(por_seq)
    origem = pd.Series(np.where(tax.notna(), "exata", "naive_bayes"), index=asvs.index)
    faltam = tax.index[tax.isna()]
    if len(faltam):
        P = nb.predict_proba(vec.transform(asvs[faltam]))
        tax.loc[faltam] = [consenso_confianca(p, nb.classes_) for p in P]
    return tax, origem


def formata(t):
    r = [x.strip() for x in t.split(";")]
    r = (r + ["__"] * 6)[:6]
    return ";".join(x if x and not x.endswith("__") else "__" for x in r)


# ------------------------------------------------------------------ espécies e CSTs (como no 23)
VAGINAIS = {"Lactobacillus crispatus": "Lactobacillus_crispatus", "Lactobacillus iners": "Lactobacillus_iners",
            "Lactobacillus gasseri": "Lactobacillus_gasseri", "Lactobacillus paragasseri": "Lactobacillus_gasseri",
            "Lactobacillus jensenii": "Lactobacillus_jensenii", "Lactobacillus mulieris": "Lactobacillus_jensenii",
            "Fannyhessea vaginae": "Atopobium_vaginae", "Sneathia sanguinegens": "Sneathia_sanguinegens",
            "Sneathia vaginalis": "Sneathia_amnii", "Sneathia amnii": "Sneathia_amnii"}
CHAVE = {"Lactobacillus", "Gardnerella", "Atopobium", "Fannyhessea", "Sneathia"}


def refs_especie(regiao):
    arq = {"V3V4": "V3V4", "V4": "V4V4", "V1V3": "V1V3"}[regiao]
    seqs, nomes, nome = [], [], None
    for l in open(f"{SPEC}/training_data/vSpeciateIT_{arq}.fasta"):
        if l.startswith(">"):
            nome = l.split("s__")[1].split(" [")[0] if "s__" in l else None
        elif nome and (nome.split()[0] in CHAVE or nome.startswith("Gardnerella")):
            seqs.append(l.strip().upper())
            nomes.append(nome)
    return seqs, nomes


def especie(asv, refs):
    melhor, quem = 10 ** 9, set()
    for s, n in zip(*refs):
        d = edlib.align(asv, s, mode="HW", task="distance", k=min(melhor, int(0.03 * len(asv))))["editDistance"]
        if d == -1:
            continue
        if d < melhor:
            melhor, quem = d, {n}
        elif d == melhor:
            quem.add(n)
    vag = {("Gardnerella_vaginalis" if n.startswith("Gardnerella") else VAGINAIS.get(n)) for n in quem} - {None}
    return vag.pop() if len(vag) == 1 else None


def tabela_valencia(T, tax, regiao):
    refs = refs_especie(regiao)
    nomes = {}
    for a in T.columns:
        g = next((p.strip()[3:] for p in tax[a].split(";") if p.strip().startswith("g__") and len(p.strip()) > 3), None)
        if g in CHAVE or (g or "").startswith("Gardnerella"):
            e = especie(a, refs) or ("Gardnerella_vaginalis" if (g or "").startswith("Gardnerella") else None)
            nomes[a] = e or f"g_{'Atopobium' if g == 'Fannyhessea' else g}"
        elif g is None:
            nomes[a] = "d_NA"
        else:
            nomes[a] = "g_Prevotella" if g.startswith("Prevotella") else "g_" + g.replace("-", ".").replace(" ", "_")
    return T.T.groupby(pd.Series(nomes)).sum().T


def valencia(X):
    ref = pd.read_csv(f"{VAL}/CST_centroids_012920.csv")
    prev = [c for c in ref.columns if c.startswith("Prevotella_") or c == "g_Prevotella"]
    ref["g_Prevotella"] = ref[prev].sum(axis=1)
    ref = ref.drop(columns=[c for c in prev if c != "g_Prevotella"])
    if "g_Corynebacterium_1" in ref:
        ref["g_Corynebacterium"] = ref.get("g_Corynebacterium", 0) + ref["g_Corynebacterium_1"]
        ref = ref.drop(columns="g_Corynebacterium_1")
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
    return out


# ------------------------------------------------------------------ estatística (como no 13 e no 23)
def hedges_g(a, b):
    n1, n2 = len(a), len(b)
    s = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1)) / (n1 + n2 - 2))
    if s == 0:
        return np.nan, np.nan
    g = (1 - 3 / (4 * (n1 + n2) - 9)) * (a.mean() - b.mean()) / s
    return g, (n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2))


def dl(y, v):
    y, v = np.asarray(y, float), np.asarray(v, float)
    w = 1 / v
    mu = (w * y).sum() / w.sum()
    q = (w * (y - mu) ** 2).sum()
    k = len(y)
    t2 = max(0, (q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0
    ws = 1 / (v + t2)
    mu = (ws * y).sum() / ws.sum()
    se = np.sqrt(1 / ws.sum())
    return mu, mu - 1.96 * se, mu + 1.96 * se, 2 * norm.sf(abs(mu / se)), (max(0, (q - (k - 1)) / q) * 100 if q > 0 else 0)


def log_or(a, b, c, d):
    a, b, c, d = a + .5, b + .5, c + .5, d + .5
    return np.log(a * d / (b * c)), 1 / a + 1 / b + 1 / c + 1 / d


# ------------------------------------------------------------------ execução
G = grupos()
generos, csts, contagem = {}, [], []
for est, (reg, trim) in ESTUDOS.items():
    if not os.path.exists(os.path.join(NOVOS, est, "deb", "reference-hit.biom")):
        print(f"{est}: deblur ainda não terminou")
        continue
    T = deblur(est)
    T = T[T.sum(axis=1) >= MIN_LEITURAS]
    tax, origem = taxonomia(list(T.columns), reg, trim)
    pct_exata = 100 * T.loc[:, origem.reindex(T.columns).eq("exata").values].values.sum() / T.values.sum() \
        if reg != "V1V3" else np.nan
    gtab = T.T.groupby([formata(t) for t in tax.loc[T.columns]]).sum().T
    gtab = gtab[[c for c in gtab.columns if not any(x in c.lower() for x in ["mitochondria", "chloroplast", "archaea"])]]
    gen = genero(gtab)
    gen.to_pickle(f"{OUT_DIR}/25_genero_{est}.pkl")
    grp = pd.Series({r: G.get(r) for r in gen.index})
    generos[est] = (gen, grp)
    cst = valencia(tabela_valencia(T, tax, reg)).assign(Project=est, tipo_amostra=grp.reindex(T.index).values)
    csts.append(cst)
    rel = gen.div(gen.sum(axis=1), axis=0)
    contagem.append(dict(estudo=est, regiao=reg, amostras=len(T), com_grupo=int(grp.notna().sum()),
                         **{f"n_{k}": int((grp == k).sum()) for k in ["cancer", "lesion high", "lesion low", "control"]},
                         leituras_mediana=int(T.sum(axis=1).median()), asvs=T.shape[1],
                         pct_leituras_asv_identica=round(pct_exata, 1) if pct_exata == pct_exata else None,
                         pct_sem_genero=round(100 * rel["sem_genero"].mean(), 1) if "sem_genero" in rel else 0,
                         lactobacillus_pct=round(100 * rel.get("Lactobacillus", pd.Series(0, index=rel.index)).mean(), 1)))
    print(contagem[-1])

pd.DataFrame(contagem).to_csv(f"{OUT_DIR}/25_resumo_estudos_novos.csv", index=False)
C = pd.concat(csts) if csts else pd.DataFrame()
C.to_csv(f"{OUT_DIR}/25_cst_por_amostra_novos.csv")

# (1) meta-análise de gêneros e Shannon
antigos = pd.read_csv(f"{OUT_DIR}/13_meta_por_projeto_TASSI_V2.csv").assign(origem="tabela reprocessada")
novos = []
for est, (gen, grp) in generos.items():
    lg = np.log(gen + 0.5)
    clr = lg.sub(lg.mean(axis=1), axis=0)
    rel = gen.div(gen.sum(axis=1), axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        sh = -(rel * np.log(rel.where(rel > 0, 1))).sum(axis=1)
    feats = {g: clr[g] for g in GENEROS if g in clr}
    feats["Shannon"] = sh
    for comp, classe in COMPARACOES.items():
        a_ids, b_ids = grp.index[grp == classe], grp.index[grp == "control"]
        if len(a_ids) < 4 or len(b_ids) < 4:
            continue
        for f, x in feats.items():
            g, v = hedges_g(x[a_ids], x[b_ids])
            if g == g:
                novos.append(dict(contraste=comp, variavel=f, projeto=est, n_caso=len(a_ids), n_controle=len(b_ids),
                                  g=g, var=v, origem="estudo novo"))
P = pd.concat([antigos, pd.DataFrame(novos)], ignore_index=True)
P.to_csv(f"{OUT_DIR}/25_meta_por_projeto_com_novos.csv", index=False)
comb = []
for (comp, var), s in P.groupby(["contraste", "variavel"]):
    for rot, ss in [("todos", s), ("sem P22", s[s.projeto != "P22"]), ("só estudos novos", s[s.origem == "estudo novo"])]:
        if len(ss) >= 2:
            mu, lo, hi, p, i2 = dl(ss.g, ss["var"])
            comb.append(dict(contraste=comp, variavel=var, conjunto=rot, k=len(ss), projetos=",".join(ss.projeto),
                             g=mu, ic_inf=lo, ic_sup=hi, p=p, I2=i2,
                             mesma_direcao=f"{int(max((ss.g > 0).sum(), (ss.g < 0).sum()))}/{len(ss)}"))
K = pd.DataFrame(comb)
K.to_csv(f"{OUT_DIR}/25_meta_combinado_com_novos.csv", index=False)
print("\nMeta-análise com os estudos novos (sem P22), p < 0,1:")
print(K[(K.conjunto == "sem P22") & (K.p < 0.1)].sort_values(["contraste", "p"]).round(3).to_string(index=False))

# (2) CSTs
if len(C):
    linhas = []
    for desf, cond in [("CST IV", lambda d: d.CST.str.startswith("IV")), ("CST I", lambda d: d.CST == "I"),
                       ("CST III", lambda d: d.CST == "III")]:
        for comp, classe in COMPARACOES.items():
            for est, s in C.groupby("Project"):
                ca, co = s[s.tipo_amostra == classe], s[s.tipo_amostra == "control"]
                if len(ca) < 5 or len(co) < 5:
                    continue
                a, c = int(cond(ca).sum()), int(cond(co).sum())
                lo, v = log_or(a, len(ca) - a, c, len(co) - c)
                linhas.append(dict(desfecho=desf, contraste=comp, projeto=est, n_caso=len(ca), n_controle=len(co),
                                   pct_caso=100 * a / len(ca), pct_controle=100 * c / len(co), log_or=lo, var=v,
                                   p_fisher=fisher_exact([[a, len(ca) - a], [c, len(co) - c]])[1], origem="estudo novo"))
    N = pd.DataFrame(linhas)
    ant = pd.read_csv(f"{OUT_DIR}/23_cst_por_estudo.csv")
    ant["desfecho"] = ant.desfecho.str.extract(r"^(CST \w+)")[0]
    ant["origem"] = "tabela reprocessada"
    L = pd.concat([ant, N], ignore_index=True)
    L.to_csv(f"{OUT_DIR}/25_cst_por_estudo_com_novos.csv", index=False)
    comb = []
    for (desf, comp), s in L.groupby(["desfecho", "contraste"]):
        for rot, ss in [("todos", s), ("sem P22", s[s.projeto != "P22"]), ("só estudos novos", s[s.origem == "estudo novo"])]:
            if len(ss) >= 2:
                mu, lo, hi, p, i2 = dl(ss.log_or, ss["var"])
                comb.append(dict(desfecho=desf, contraste=comp, conjunto=rot, k=len(ss), projetos=",".join(ss.projeto),
                                 OR=np.exp(mu), ic_inf=np.exp(lo), ic_sup=np.exp(hi), p=p, I2=i2))
    KC = pd.DataFrame(comb)
    KC.to_csv(f"{OUT_DIR}/25_cst_meta_com_novos.csv", index=False)
    print("\nCSTs por estudo novo:")
    print(N.round(2).to_string(index=False))
    print("\nCSTs, meta-análise com os estudos novos:")
    print(KC.round(3).to_string(index=False))
