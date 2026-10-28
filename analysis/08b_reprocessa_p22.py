"""Monta a tabela de gêneros do P22 reprocessado no ramo V3-V4.

Processamento feito fora do QIIME 2, com as mesmas ferramentas e parâmetros do
ramo V3-V4 do pipeline (ver analysis/p22_v3v4.sh):
  1. FASTQ das 119 runs baixados do espelho público do SRA na AWS (fasterq-dump)
  2. cutadapt -g CCTAYGGGRBGCASCAG --discard-untrimmed (341F), só R1
  3. filtro de qualidade com os padrões do q2-quality-filter (Q4, janela 3, 75% do comprimento, sem N)
  4. deblur 1.1.1 workflow, --trim-length 220, min-reads 10, min-size 2 (demais parâmetros iguais ao denoise-16S)

Por que 220 e não 250 como no resto do ramo V3-V4: no P22, todas as 65 amostras de
câncer têm leituras de ~222 nt depois do primer e os 54 controles, ~274 nt. Câncer e
controle foram sequenciados em corridas diferentes. Com corte de 250, o deblur descarta
todas as amostras de câncer. O corte de 220 é o maior que mantém as duas classes.

Classificação: o classificador SILVA V3-V4 retreinado não está acessível desta
sessão. Cada ASV recebe (a) a taxonomia de consenso das ASVs V3-V4 já classificadas no
pipeline (P1, P6, P14, P19) que têm os mesmos primeiros 220 nt, ou, se não houver, (b) a de um Naive Bayes de k-mers
(k=7, como o q2-feature-classifier) treinado nessas ASVs classificadas, truncada no
nível em que a confiança fica abaixo de 0,7. A classificação final deve ser refeita
com o classificador SILVA V3-V4 no QIIME 2.

Entrada: P22_DEBLUR_DIR com reference-hit.biom e reference-hit.seqs.fa do deblur.
"""
import os

TRIM = int(os.environ.get("P22_TRIM", "220"))

import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB

from common import OUT_DIR, fasta, path, unzip_qza

deb = os.environ.get("P22_DEBLUR_DIR")
f = h5py.File(os.path.join(deb, "reference-hit.biom"), "r")
obs = [x.decode() for x in f["observation/ids"][:]]
smp = [x.decode() for x in f["sample/ids"][:]]
mat = sp.csr_matrix((f["observation/matrix/data"][:], f["observation/matrix/indices"][:],
                     f["observation/matrix/indptr"][:]), shape=(len(obs), len(smp)))
tab = pd.DataFrame(mat.T.toarray(), index=smp, columns=obs)  # deblur usa a sequência como ID
tab.index = [s.split(".")[0] for s in tab.index]
print(f"P22 reprocessado: {tab.shape[0]} amostras, {tab.shape[1]} ASVs, leituras por amostra (mediana) {int(tab.sum(axis=1).median())}")

ref_seq = fasta(os.path.join(unzip_qza(path("tassi", "V3V4_repseqs.qza")), "dna-sequences.fasta"))
ref_tax = pd.read_csv(os.path.join(unzip_qza(path("tassi", "V3V4_taxonomy.qza")), "taxonomy.tsv"), sep="\t", index_col=0)["Taxon"]
ref = pd.DataFrame({"seq": pd.Series(ref_seq), "tax": ref_tax}).dropna()
ref["seq"] = ref.seq.str.upper().str[:TRIM]


def consenso(taxas):
    niveis = [t.split("; ") for t in taxas]
    out = []
    for nivel in zip(*niveis):
        if len(set(nivel)) != 1:
            break
        out.append(nivel[0])
    return "; ".join(out) if out else "Unassigned"


por_seq = ref.groupby("seq").tax.agg(lambda t: consenso(list(t)))

asv = pd.Series(tab.columns, index=tab.columns).str.upper()
exata = asv.map(por_seq)
print(f"correspondência exata de {TRIM} nt: {exata.notna().sum()}/{len(asv)} ASVs, "
      f"{100 * tab.loc[:, exata.notna().values].values.sum() / tab.values.sum():.1f}% das leituras")

# Naive Bayes de k-mers para as ASVs sem correspondência exata
vec = HashingVectorizer(analyzer="char", ngram_range=(7, 7), n_features=8192, alternate_sign=False, norm="l1")
ref_nb = ref.drop_duplicates("seq").assign(tax=lambda d: d.seq.map(por_seq))
nb = MultinomialNB(alpha=0.001, fit_prior=False).fit(vec.transform(ref_nb.seq), ref_nb.tax.values)


def consenso_confianca(probs, classes, limite=0.7):
    top = classes[probs.argmax()].split("; ")
    out = []
    for nivel in range(1, len(top) + 1):
        prefixo = "; ".join(top[:nivel])
        conf = probs[[c == prefixo or c.startswith(prefixo + ";") for c in classes]].sum()
        if conf < limite:
            break
        out.append(top[nivel - 1])
    return "; ".join(out) if out else "Unassigned"


faltam = exata.index[exata.isna()]
if len(faltam):
    P = nb.predict_proba(vec.transform(asv[faltam]))
    exata.loc[faltam] = [consenso_confianca(p, nb.classes_) for p in P]


def formata(t):
    r = [x.strip() for x in t.split(";")]
    r = (r + ["__"] * 6)[:6]
    return ";".join(x if x and not x.endswith("__") else "__" for x in r)


col = [formata(t) for t in exata.loc[tab.columns]]
g = tab.T.groupby(col).sum().T
g = g[[c for c in g.columns if not any(x in c.lower() for x in ["mitochondria", "chloroplast", "archaea"])]]
g.to_pickle(f"{OUT_DIR}/p22_v3v4_genero.pkl")
pd.DataFrame({"asv": tab.columns, "taxonomia": exata.loc[tab.columns].values,
              "origem": np.where(asv.map(por_seq).notna(), "exata", "naive_bayes")}).to_csv(
    f"{OUT_DIR}/08b_p22_taxonomia_asvs.csv", index=False)
top = (g.div(g.sum(axis=1), axis=0).mean() * 100).sort_values(ascending=False).head(10)
print({k.split(";")[-1] if k.split(";")[-1] != "__" else k: round(v, 1) for k, v in top.items()})
print("sem gênero (% médio):", round((g.div(g.sum(axis=1), axis=0)[[c for c in g.columns if c.endswith("__")]].sum(axis=1).mean()) * 100, 1))
