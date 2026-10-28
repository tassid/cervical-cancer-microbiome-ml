"""Por que o P16 aparece com 55, 29 e 26 amostras em lugares diferentes.

O metadado lista 55 runs de câncer para o P16 (PRJNA1029035). Elas formam dois grupos:
  - SRR26410xxx: 26 runs com BioSample (SAMN37857xxx), carregadas no SRA em 17/10/2023,
    com ~1.600 leituras brutas por amostra. É o número da Tabela 1 do artigo e do TCC.
  - SRR26495xxx: 29 runs sem BioSample no metadado, carregadas em 24/10/2023, com
    ~120 mil leituras, das quais só ~45% têm o primer 16S. São as 29 da tabela da Paola.
O BioProject das 29 runs precisa ser confirmado no SRA Run Selector (NCBI inacessível
na sessão da auditoria).
"""
import os

import pandas as pd

from common import OUT_DIR, meta, paola, path, tassi, unzip_qza

m = meta()
P, T = paola(), tassi()
stats = pd.read_csv(os.path.join(unzip_qza(path("tassi", "V4_stats.qza")), "stats.csv"), index_col=0)
ids = m.index[m.Project == "P16"]
d = pd.DataFrame(index=ids)
d["grupo"] = [i[:8] + "xxx" for i in ids]
d["biosample"] = m.loc[ids, "sample_accession"]
d["leituras_brutas"] = stats["reads-raw"].reindex(ids)
d["na_tabela_paola"] = [i in P.index for i in ids]
d["na_tabela_tassiane"] = [i in T.index for i in ids]
d.to_csv(f"{OUT_DIR}/16_p16_runs.csv")
resumo = d.groupby("grupo").agg(runs=("biosample", "size"), com_biosample=("biosample", lambda x: x.notna().sum()),
                                leituras_brutas_mediana=("leituras_brutas", "median"),
                                na_paola=("na_tabela_paola", "sum"), na_tassiane=("na_tabela_tassiane", "sum"))
resumo.to_csv(f"{OUT_DIR}/16_p16_resumo.csv")
print(resumo)
