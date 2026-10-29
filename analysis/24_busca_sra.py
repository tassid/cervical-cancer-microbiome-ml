"""Levantamento de BioProjects candidatos no NCBI: estudos 16S cervicovaginais com caso E controle.

Objetivo: aumentar o N pareado (ver 22_teste_n_pareamento.py). Para cada busca, lista os
BioProjects, baixa o runinfo do SRA e os atributos das BioSamples, e marca:
  - se é amplicon 16S (LibraryStrategy AMPLICON e menção a 16S);
  - quantas amostras parecem caso (câncer, CIN/NIC, HSIL, LSIL, SIL) e quantas parecem controle
    (controle, normal, saudável, NILM, HPV-negativo), pelos atributos e títulos das BioSamples;
  - se já está entre os 10 projetos usados.
As contagens por palavra-chave são uma triagem: cada candidato precisa ser conferido no artigo.

Requer acesso a eutils.ncbi.nlm.nih.gov. Uso: python 24_busca_sra.py
Opcional: NCBI_API_KEY (aumenta o limite de 3 para 10 requisições por segundo).
"""
import io
import os
import re
import time
import xml.etree.ElementTree as ET

import pandas as pd
import requests

from common import OUT_DIR

EU = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
KEY = os.environ.get("NCBI_API_KEY")
JA_USADOS = {"PRJNA687644", "PRJNA518153", "PRJNA687331", "PRJNA431248", "PRJEB51893", "PRJNA933917",
             "PRJNA1029035", "PRJNA914231", "PRJEB83336", "PRJNA725946"}
BUSCAS = [
    '(cervical cancer[All Fields] OR cervical carcinoma[All Fields]) AND (16S[All Fields] OR microbiome[All Fields] OR microbiota[All Fields])',
    '(cervical intraepithelial neoplasia[All Fields] OR CIN[Title] OR squamous intraepithelial lesion[All Fields]) AND (16S[All Fields] OR microbiota[All Fields] OR microbiome[All Fields])',
    '(HPV[All Fields] OR papillomavirus[All Fields]) AND (cervicovaginal[All Fields] OR cervical[All Fields] OR vaginal[All Fields]) AND (16S[All Fields] OR microbiota[All Fields])',
    'cervicovaginal microbiota[All Fields] AND (neoplasia[All Fields] OR lesion[All Fields] OR cancer[All Fields])',
]
CASO = re.compile(r"cancer|carcinoma|tumou?r|malignan|\bcin ?[123]|\bcin\b|hsil|lsil|\bsil\b|neoplasi|lesion|dysplas", re.I)
CONTROLE = re.compile(r"control|normal|healthy|nilm|negative for intraepithelial|hpv[- ]?neg|non[- ]?cancer|benign", re.I)


def get(endpoint, **params):
    if KEY:
        params["api_key"] = KEY
    for t in range(4):
        r = requests.get(f"{EU}/{endpoint}.fcgi", params=params, timeout=60)
        if r.status_code == 200:
            time.sleep(0.12 if KEY else 0.4)
            return r.text
        time.sleep(2 ** t)
    r.raise_for_status()


def bioprojects(termo):
    x = ET.fromstring(get("esearch", db="bioproject", term=termo, retmax=500))
    return [e.text for e in x.iter("Id")]


def resumo_projetos(uids):
    out = {}
    for i in range(0, len(uids), 100):
        x = ET.fromstring(get("esummary", db="bioproject", id=",".join(uids[i:i + 100])))
        for d in x.iter("DocumentSummary"):
            acc = d.findtext("Project_Acc")
            out[acc] = dict(uid=d.get("uid"), titulo=d.findtext("Project_Title"),
                            organismo=d.findtext("Organism_Name"), data=d.findtext("Registration_Date"),
                            descricao=(d.findtext("Project_Description") or "")[:300])
    return out


def runinfo(acc):
    x = ET.fromstring(get("esearch", db="sra", term=f"{acc}[BioProject]", retmax=5000))
    ids = [e.text for e in x.iter("Id")]
    if not ids:
        return pd.DataFrame()
    partes = []
    for i in range(0, len(ids), 300):
        txt = get("efetch", db="sra", id=",".join(ids[i:i + 300]), rettype="runinfo", retmode="text")
        if txt.strip():
            partes.append(pd.read_csv(io.StringIO(txt)))
    return pd.concat(partes) if partes else pd.DataFrame()


def biosamples(accs):
    txts = []
    accs = [a for a in accs if isinstance(a, str)]
    for i in range(0, len(accs), 200):
        x = ET.fromstring(get("esearch", db="biosample", term=" OR ".join(accs[i:i + 200]), retmax=500))
        ids = [e.text for e in x.iter("Id")]
        if not ids:
            continue
        xml = ET.fromstring(get("efetch", db="biosample", id=",".join(ids), retmode="xml"))
        for b in xml.iter("BioSample"):
            campos = [b.findtext("Description/Title") or ""]
            campos += [f"{a.get('attribute_name')}={a.text}" for a in b.iter("Attribute")]
            txts.append(" | ".join(campos))
    return txts


linhas = []
vistos = {}
for termo in BUSCAS:
    uids = bioprojects(termo)
    print(f"{len(uids):4d} BioProjects para: {termo[:90]}")
    vistos.update(resumo_projetos([u for u in uids if u not in {v['uid'] for v in vistos.values()}]))
print(f"{len(vistos)} BioProjects únicos")

for acc, info in vistos.items():
    try:
        ri = runinfo(acc)
    except Exception as e:  # noqa: BLE001 - um projeto com erro não deve parar o levantamento
        print("erro", acc, e)
        continue
    if ri.empty:
        continue
    amplicon = ri.LibraryStrategy.astype(str).str.upper().eq("AMPLICON").mean() if "LibraryStrategy" in ri else 0
    humano = ri.ScientificName.astype(str).str.contains("vaginal|human|Homo|metagenome", case=False).mean() \
        if "ScientificName" in ri else 0
    bs = biosamples(list(ri.BioSample.dropna().unique())) if "BioSample" in ri else []
    n_caso = sum(bool(CASO.search(t)) for t in bs)
    n_ctrl = sum(bool(CONTROLE.search(t)) for t in bs)
    texto = f"{info['titulo']} {info['descricao']}"
    linhas.append(dict(bioproject=acc, ja_usado=acc in JA_USADOS, titulo=info["titulo"], data=info["data"],
                       runs=len(ri), biosamples=len(bs), fracao_amplicon=round(amplicon, 2),
                       menciona_16S=bool(re.search(r"16S", texto, re.I)), amostras_caso=n_caso,
                       amostras_controle=n_ctrl, tem_caso_e_controle=n_caso >= 5 and n_ctrl >= 5,
                       plataforma=", ".join(ri.Platform.dropna().astype(str).unique()[:2]) if "Platform" in ri else "",
                       descricao=info["descricao"]))
    print(f"  {acc}: {len(ri)} runs, caso~{n_caso}, controle~{n_ctrl}  {info['titulo'][:70]}")

R = pd.DataFrame(linhas).sort_values(["tem_caso_e_controle", "ja_usado", "runs"], ascending=[False, True, False])
R.to_csv(f"{OUT_DIR}/24_candidatos_sra.csv", index=False)
cand = R[R.tem_caso_e_controle & ~R.ja_usado & (R.fracao_amplicon > 0.5)]
print(f"\n{len(cand)} candidatos novos com caso e controle (amplicon):")
print(cand[["bioproject", "runs", "amostras_caso", "amostras_controle", "titulo"]].to_string(index=False))
