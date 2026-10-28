"""η² dos eixos latentes do GLLVM (gllvm_escores.csv do gllvm_fit.R original).

Para cada variável latente, η² = SQ entre grupos / SQ total de uma ANOVA de um
fator, separadamente para projeto de origem e para tipo de amostra. É a mesma
medida citada no README (LV1 e LV2: 56,7% e 58,2% por projeto; 11,1% e 7,9% por
condição clínica, na tabela original).

Uso: python 15_gllvm_eta2.py caminho/gllvm_escores.csv [rótulo]
"""
import sys

import pandas as pd


def eta2(y, g):
    media = y.mean()
    entre = y.groupby(g).apply(lambda s: len(s) * (s.mean() - media) ** 2).sum()
    return entre / ((y - media) ** 2).sum()


arq = sys.argv[1]
rotulo = sys.argv[2] if len(sys.argv) > 2 else arq
d = pd.read_csv(arq)
linhas = []
for lv in ["LV1", "LV2"]:
    linhas.append(dict(tabela=rotulo, eixo=lv,
                       eta2_projeto=round(100 * eta2(d[lv], d.Project), 1),
                       eta2_tipo_amostra=round(100 * eta2(d[lv], d.tipo_amostra), 1)))
print(pd.DataFrame(linhas).to_string(index=False))
