"""Metadados amostra por amostra dos estudos novos (o 24b só guardava contagens por atributo).

Para cada run: BioSample, nome da amostra, título e todos os atributos da BioSample em colunas
(por exemplo, "gynecological disorder" = PRE/POST/Normal no PRJEB40437, "Cytology" no PRJNA622998).
É o que permite saber o grupo clínico de cada run baixada pelo 25_novos_estudos.sh.

Requer acesso a eutils.ncbi.nlm.nih.gov (rodar no computador local).
Uso: python 24d_metadados_por_amostra.py
Saída: results/24d_metadados_por_amostra.csv
"""
import importlib.util
import os
import xml.etree.ElementTree as ET

import pandas as pd

from common import OUT_DIR

ESTUDOS = ["PRJNA1085021", "PRJNA308947", "PRJNA622998", "PRJEB40437", "PRJEB43410",
           "PRJNA1479850", "PRJNA1433670", "PRJNA1532026"]

spec = importlib.util.spec_from_file_location(
    "busca", os.path.join(os.path.dirname(os.path.abspath(__file__)), "24_busca_sra.py"))
busca = importlib.util.module_from_spec(spec)
spec.loader.exec_module(busca)

linhas = []
for acc in ESTUDOS:
    ri = busca.runinfo(acc)
    if ri.empty:
        print(acc, "sem runs")
        continue
    ri = ri[ri.BioProject.astype(str) == acc] if "BioProject" in ri else ri
    bs = [b for b in ri.BioSample.dropna().unique() if isinstance(b, str)]
    attrs = {}
    for i in range(0, len(bs), 150):
        x = ET.fromstring(busca.get("esearch", db="biosample", term=" OR ".join(f"{b}[accn]" for b in bs[i:i + 150]),
                                    retmax=500))
        ids = [e.text for e in x.iter("Id")]
        if not ids:
            continue
        xml = ET.fromstring(busca.get("efetch", db="biosample", id=",".join(ids), retmode="xml"))
        for b in xml.iter("BioSample"):
            acc_bs = b.get("accession")
            d = {"titulo_biosample": b.findtext("Description/Title") or ""}
            for a in b.iter("Attribute"):
                d[a.get("attribute_name")] = a.text
            for i_ in b.iter("Id"):
                if i_.get("db") == "SRA" or i_.get("db_label") == "Sample name":
                    d["id_" + (i_.get("db") or i_.get("db_label"))] = i_.text
            attrs[acc_bs] = d
    for _, r in ri.iterrows():
        linha = {"bioproject": acc, "Run": r.Run, "BioSample": r.BioSample, "SampleName": r.get("SampleName", "")}
        linha.update(attrs.get(r.BioSample, {}))
        linhas.append(linha)
    print(f"{acc}: {len(ri)} runs, {len(attrs)} BioSamples com atributos")

D = pd.DataFrame(linhas)
D.to_csv(f"{OUT_DIR}/24d_metadados_por_amostra.csv", index=False)
print(f"\nSalvo em results/24d_metadados_por_amostra.csv ({len(D)} runs, {D.shape[1]} colunas)")
