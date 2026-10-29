"""Baixa os metadados completos dos candidatos da triagem (results/24_triagem_candidatos.csv).

Para cada BioProject: estratégia, plataforma e comprimento médio das leituras (runinfo do SRA)
e a contagem de cada valor de cada atributo das BioSamples (por exemplo, disease=cervical
cancer: 48). Serve para conferir se o estudo tem caso e controle de verdade, quantos de cada,
e qual região do 16S foi sequenciada.

Requer acesso a eutils.ncbi.nlm.nih.gov. Uso: python 24b_atributos_candidatos.py
Saída: results/24b_atributos.csv (projeto, atributo, valor, n) e results/24b_runinfo.csv.
"""
import importlib.util
import os
from collections import Counter

import pandas as pd

from common import OUT_DIR

spec = importlib.util.spec_from_file_location(
    "busca", os.path.join(os.path.dirname(os.path.abspath(__file__)), "24_busca_sra.py"))
busca = importlib.util.module_from_spec(spec)
spec.loader.exec_module(busca)  # só define as funções; a busca roda apenas com python 24_busca_sra.py
get, runinfo = busca.get, busca.runinfo

import xml.etree.ElementTree as ET  # noqa: E402

tri = pd.read_csv(f"{OUT_DIR}/24_triagem_candidatos.csv")
attrs, runs = [], []
for acc in tri.bioproject:
    ri = runinfo(acc)
    if ri.empty:
        print(acc, "sem runs")
        continue
    cols = [c for c in ["Run", "LibraryStrategy", "LibrarySource", "LibraryLayout", "Platform", "Model", "avgLength",
                        "spots", "BioSample", "SampleName"] if c in ri]
    r = ri[cols].copy()
    r.insert(0, "bioproject", acc)
    runs.append(r)
    bs = [b for b in ri.BioSample.dropna().unique() if isinstance(b, str)]
    cont = Counter()
    for i in range(0, len(bs), 200):
        x = ET.fromstring(get("esearch", db="biosample", term=" OR ".join(bs[i:i + 200]), retmax=500))
        ids = [e.text for e in x.iter("Id")]
        if not ids:
            continue
        xml = ET.fromstring(get("efetch", db="biosample", id=",".join(ids), retmode="xml"))
        for b in xml.iter("BioSample"):
            cont[("title", (b.findtext("Description/Title") or "")[:80])] += 1
            for a in b.iter("Attribute"):
                cont[(a.get("attribute_name"), (a.text or "")[:80])] += 1
    for (k, v), n in cont.items():
        attrs.append(dict(bioproject=acc, atributo=k, valor=v, n=n))
    estr = ", ".join(f"{k}:{v}" for k, v in r.LibraryStrategy.value_counts().items()) if "LibraryStrategy" in r else ""
    print(f"\n== {acc}: {len(r)} runs | {estr} | comprimento médio {r.avgLength.median() if 'avgLength' in r else '?'}")
    A = pd.DataFrame([a for a in attrs if a["bioproject"] == acc])
    # atributos com poucos valores distintos costumam ser os grupos (doença, HPV, citologia)
    for k, g in A.groupby("atributo"):
        if 1 < len(g) <= 12:
            print(f"   {k}: " + "; ".join(f"{v} ({n})" for v, n in g.sort_values("n", ascending=False)[["valor", "n"]].values))

pd.DataFrame(attrs).to_csv(f"{OUT_DIR}/24b_atributos.csv", index=False)
pd.concat(runs).to_csv(f"{OUT_DIR}/24b_runinfo.csv", index=False)
print("\nSalvo em results/24b_atributos.csv e results/24b_runinfo.csv")
