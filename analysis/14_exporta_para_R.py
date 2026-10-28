"""Exporta uma tabela no formato que os scripts R originais da Tassiane leem.

Cria, em R_DIR, export/genus_table_final/feature-table.tsv (formato do `biom convert`)
e metadata_final_889.tsv (mesmas colunas do original, só com as amostras da tabela),
para rodar permanova.R, permanova_pares.R, gllvm_fit.R e random_forest.R sem mudar
nenhuma linha deles.

Uso: TABELA=TASSI_V2 R_DIR=/caminho python 14_exporta_para_R.py
"""
import os

from common import TABELAS, meta

nome = os.environ.get("TABELA", "TASSI_V2")
dest = os.environ["R_DIR"]
os.makedirs(os.path.join(dest, "export", "genus_table_final"), exist_ok=True)
t = TABELAS[nome]().T
t.index.name = "#OTU ID"
with open(os.path.join(dest, "export", "genus_table_final", "feature-table.tsv"), "w") as f:
    f.write("# Constructed from biom file\n")
    t.to_csv(f, sep="\t")
m = meta().loc[t.columns]
m.index.name = "sampleid"
m = m.reset_index()
m.to_csv(os.path.join(dest, "metadata_final_889.tsv"), sep="\t", index=False)
print(f"{nome}: {t.shape[1]} amostras, {t.shape[0]} gêneros -> {dest}")
print(m.groupby(["Project", "tipo_amostra"]).size().unstack(fill_value=0))
