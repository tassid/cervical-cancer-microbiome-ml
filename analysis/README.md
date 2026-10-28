# Comparação Paola × Tassiane e auditoria de viés

Scripts que comparam a tabela usada no artigo da Paola ("Cervicovaginal microbiome as a
predictive biomarker for cervical cancer", 2026) com a tabela do pipeline próprio da
Tassiane, e testam se as conclusões do artigo sobrevivem quando o projeto de origem é
levado em conta.

## Dados

Os dados ficam no Google Drive (não versionados aqui). Monte uma pasta com a estrutura
descrita em `common.py` e aponte `DATA_DIR` para ela.

| Tabela | Origem | Amostras | Nível |
|---|---|---|---|
| `PAOLA` | `Results/feature-table.txt` (Drive da Paola) | 997 | espécie, colapsada para gênero |
| `TASSI` | `qiime/genus_table_final.qza` (Drive da Tassiane) | 889 | gênero |
| `TASSI_FIX` | `TASSI` com o P22 reclassificado (`08_corrige_p22.py`) | 889 | gênero |

## Ordem de execução

```bash
pip install -r requirements.txt
export DATA_DIR=/caminho/dos/dados OUT_DIR=$PWD/results
python 08_corrige_p22.py                # cria a tabela TASSI_FIX
python 01_auditoria.py                  # classe x projeto x região x profundidade
python 02_diversidade_alfa.py           # alfa com e sem ajuste por projeto
python 03_ml_vies.py                    # RF: treino-no-treino, CV, só-projeto, LOPO, controle negativo
python 04_biomarcadores_por_projeto.py  # de que projeto vem cada "biomarcador"
python 05_abundancia_dentro_do_projeto.py
python 06_permanova.py                  # R² classe, projeto e classe além do projeto
python 07_compara_pipelines.py          # mesma amostra nos dois pipelines
python 09_forca_bruta.py                # 30 combinações de modelo/pré-processamento (demora ~1 h)
python 10_contabilidade_amostras.py     # onde cada uma das 1.042 amostras se perdeu (precisa de V3V4_stats.qza, V4_stats.qza, P14_cutadapt_stats.qza)
```

Os resultados já calculados estão em `results/`.

## Principais resultados (resumo)

- **O AUC ≈ 1 do artigo só é reproduzido avaliando o modelo nas próprias amostras de
  treino.** Com validação cruzada de 10 folds o mesmo Random Forest dá AUC 0,97 (câncer),
  0,85 (controle), 0,76 (HSIL) e 0,74 (LSIL); acurácia balanceada 0,50.
- **Saber só o projeto de origem dá praticamente o mesmo AUC** (0,95 / 0,85 / 0,77 / 0,79)
  que o microbioma inteiro.
- **Leave-one-project-out derruba o desempenho**: câncer 0,70, controle 0,51, HSIL 0,46,
  LSIL 0,34 (Paola); 0,62 / 0,43 / 0,47 / 0,35 (Tassiane corrigida).
- **A composição prevê o projeto com 86–88% de acerto** (acaso: 32–35%).
- **PERMANOVA**: classe sozinha R² ≈ 7%, projeto sozinho 15–16%, classe além do projeto 0,4%.
- **Diversidade alfa maior no câncer desaparece ao ajustar por projeto** (Shannon:
  +0,99 → +0,09 a +0,14, p > 0,2) e muda de sinal entre projetos (P19 ↑, P22 ↓, P2 n.s.).
- **Biomarcadores do Boruta/LEfSe concentrados em um único projeto**:
  Burkholderia-Caballeronia-Paraburkholderia 96% no P21 (Espanha, quase só controles),
  Wolbachia 100% no P1, Aeribacillus 100% e Halomonas 95% no P9, Rhodococcus 92% no P1.
- **Dentro de cada projeto**, o único sinal de câncer que se repete é no P19 (Nigéria,
  AUC ≈ 0,80). No P22 a profundidade de leitura sozinha separa câncer de controle (AUC 0,97),
  sinal de lote dentro do próprio projeto. Nas lesões (P10, P14, P2, P19) o AUC fica entre 0,42 e 0,68.
- **Pipeline da Tassiane**: o P22 foi processado no ramo V4, mas é V3-V4 (leituras começam em
  `TAGGGAATCTTCCACAATGG`, início de V3). Com isso 79% das leituras ficaram sem gênero. Depois
  da correção, as duas tabelas concordam (Spearman 0,97–1,00 nos gêneros principais;
  Bray-Curtis mediano por amostra ≤ 0,09 em todos os projetos exceto P16).
- **P14 tem dois sublotes**: 21 amostras (10 controles, 11 HSIL) já vêm sem primer; no pipeline da Tassiane o cutadapt as descarta (sobram 0,02% das leituras) e na tabela da Paola elas também faltam (16 ausentes, 5 com 2–4 leituras). Metade do único projeto brasileiro está fora das duas tabelas.
- **P16 na tabela da Paola**: 39% "Unassigned" e 2,5% Eukaryota, provável DNA do hospedeiro
  não filtrado; 29 amostras contra 47 na da Tassiane e 26 no artigo.
