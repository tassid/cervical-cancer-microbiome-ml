"""Leitura das tabelas usadas na comparação Paola x Tassiane.

Os dados não ficam no repositório. Aponte DATA_DIR para uma pasta com:

  paola/feature-table.txt        (Drive da Paola: Results/feature-table.txt)
  paola/metadata.txt             (Drive da Paola: Results/metadata.txt)
  tassi/metadata_master.tsv      (Drive da Tassiane: metadata/metadata_master.tsv)
  tassi/genus_table_final.qza    (Drive da Tassiane: qiime/genus_table_final.qza)
  tassi/V4_table.qza, V4_repseqs.qza                (para a correção do P22)
  tassi/V3V4_repseqs.qza, V3V4_taxonomy.qza         (para a correção do P22)

Uso: DATA_DIR=/caminho/dos/dados python 01_auditoria.py
"""
import glob
import os
import zipfile

import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
OUT_DIR = os.environ.get("OUT_DIR", os.path.join(os.path.dirname(__file__), "results"))
os.makedirs(OUT_DIR, exist_ok=True)

CLASSES = ["cancer", "control", "lesion high", "lesion low"]
REGIAO = {"P1": "V3V4", "P6": "V3V4", "P14": "V3V4", "P19": "V3V4", "P21": "V3V4", "P22": "V3V4",
          "P2": "V4", "P9": "V4", "P10": "V4", "P16": "V4"}


def path(*p):
    return os.path.join(DATA_DIR, *p)


def unzip_qza(qza):
    """Extrai um .qza (zip) ao lado do arquivo e devolve a pasta data/ interna."""
    dest = qza[:-4]
    if not os.path.isdir(dest):
        zipfile.ZipFile(qza).extractall(dest)
    return glob.glob(os.path.join(dest, "*", "data"))[0]


def biom(qza):
    """Lê o feature-table.biom (HDF5) de dentro de um .qza. Retorna amostras x features."""
    f = h5py.File(os.path.join(unzip_qza(qza), "feature-table.biom"), "r")
    obs = [x.decode() for x in f["observation/ids"][:]]
    smp = [x.decode() for x in f["sample/ids"][:]]
    m = sp.csr_matrix((f["observation/matrix/data"][:], f["observation/matrix/indices"][:],
                       f["observation/matrix/indptr"][:]), shape=(len(obs), len(smp)))
    return pd.DataFrame(m.T.toarray(), index=smp, columns=obs)


def fasta(p):
    seqs, k = {}, None
    for line in open(p):
        line = line.strip()
        if line.startswith(">"):
            k = line[1:]
        elif k:
            seqs[k] = seqs.get(k, "") + line
    return seqs


def meta():
    m = pd.read_csv(path("tassi", "metadata_master.tsv"), sep="\t")
    m["tipo_amostra"] = m.tipo_amostra.str.strip()  # P16 tem "cancer " com espaço
    return m.set_index("sampleid")


def paola():
    """Tabela da Paola (nível de espécie, 7 níveis SILVA). Amostras x táxons."""
    ft = pd.read_csv(path("paola", "feature-table.txt"), sep=";", index_col=0, encoding="utf-8-sig")
    return ft.drop(columns=["taxonomy"], errors="ignore").T


def paola_genus():
    df = paola()
    g = [";".join(c.split(";")[:6]) for c in df.columns]
    return df.T.groupby(g).sum().T


def tassi():
    """Tabela final da Tassiane (gênero, 889 amostras), como está no Drive."""
    return biom(path("tassi", "genus_table_final.qza"))


def tassi_fix():
    """Tabela da Tassiane com o P22 reclassificado (ver 08_corrige_p22.py)."""
    fixed = os.path.join(OUT_DIR, "p22_genero_corrigido.pkl")
    if not os.path.exists(fixed):
        raise SystemExit("Rode 08_corrige_p22.py antes.")
    g = pd.read_pickle(fixed)
    g = g[g.sum(axis=1) >= 1000]
    t = tassi()
    m = meta()
    t = t.drop(index=t.index.intersection(m.index[m.Project == "P22"]))
    out = pd.concat([t, g]).fillna(0)
    return out.loc[:, out.sum() >= 2]


def paola_limpa():
    """Tabela da Paola sem P21, sem P16 (DNA não bacteriano) e sem amostras < 1.000 leituras."""
    df = paola_genus()
    m = meta().loc[df.index]
    ok = ~m.Project.isin(["P21", "P16"]) & (df.sum(axis=1) >= 1000)
    return df[ok.values]


def tassi_v2():
    """Tabela da Tassiane com o P22 reprocessado no ramo V3-V4 (ver 08b_reprocessa_p22.py)."""
    novo = os.path.join(OUT_DIR, "p22_v3v4_genero.pkl")
    if not os.path.exists(novo):
        raise SystemExit("Rode 08b_reprocessa_p22.py antes.")
    g = pd.read_pickle(novo)
    g = g[g.sum(axis=1) >= 1000]
    t = tassi()
    m = meta()
    t = t.drop(index=t.index.intersection(m.index[m.Project == "P22"]))
    out = pd.concat([t, g]).fillna(0)
    return out.loc[:, out.sum() >= 2]


TABELAS = {"PAOLA": paola_genus, "TASSI": tassi, "TASSI_FIX": tassi_fix,
           "PAOLA_LIMPA": paola_limpa, "TASSI_V2": tassi_v2}


def genero(df):
    """Renomeia colunas para só o nome do gênero (somando duplicatas)."""
    nomes = []
    for c in df.columns:
        r = c.split(";")
        g = r[5].replace("g__", "") if len(r) > 5 else "__"
        if "Chloroplast" in c:
            g = "Chloroplast"
        if g in ("__", ""):
            g = "sem_genero"
        nomes.append(g)
    return df.T.groupby(nomes).sum().T


def relativa(df):
    return df.div(df.sum(axis=1), axis=0)


def ativas():
    """Tabelas a analisar. Padrão: Paola e Tassiane com P22 reprocessado.
    Troque com TABELAS=PAOLA,TASSI_FIX,PAOLA_LIMPA python ..."""
    nomes = os.environ.get("TABELAS", "PAOLA,TASSI_V2").split(",")
    return [(n, TABELAS[n]) for n in nomes]
