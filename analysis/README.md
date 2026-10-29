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
python 11_contaminantes.py              # gêneros de kit/laboratório: peso por projeto e sensibilidade do ML
python 12_abundancia_com_projeto.py     # abundância diferencial em CLR com e sem projeto no modelo
python 13_meta_analise.py               # efeito por projeto (g de Hedges) + efeitos aleatórios (DerSimonian-Laird)
python 14_exporta_para_R.py             # exporta TABELA=... para os scripts R originais (R_DIR=...)
python 15_gllvm_eta2.py results/R_tassi_v2/gllvm_escores.csv   # η² dos eixos do GLLVM
python 16_p16_sublotes.py               # os dois grupos de runs do P16 (26 com BioSample, 29 sem)
python 17_boruta_por_projeto.py         # Boruta global e dentro de cada projeto (pip install Boruta)
LEFSE_BIN=... python 19_lefse_por_projeto.py   # LEfSe global e por projeto (lefse 1.1.2, python 3.9, rpy2 < 3.5)
python 18_tabelas_artigo.py             # Tabela 1 corrigida e tabela de validação (depois do 03)
python 20_shap.py                       # SHAP global, do modelo que prevê o projeto, LOPO e dentro de cada projeto (~15 min)
python 22_teste_n_pareamento.py        # estudos de uma classe ajudam? (N efetivo, cenários de treino, embaralhamento)
python 22b_seguimento_n.py              # cenários sem P22, regras simples, poder
python 22c_curva_sem_p22.py             # curva de aprendizado: N pareado x N de estudos de uma classe
SPECIATEIT_DIR=... VALENCIA_DIR=... P22_DEBLUR_DIR=... python 23_cst_valencia.py   # CSTs (VALENCIA) e comparação dentro dos estudos
python 24_busca_sra.py                  # candidatos no SRA com caso e controle (precisa de acesso a eutils.ncbi.nlm.nih.gov)
python 24b_atributos_candidatos.py      # metadados completos dos candidatos da triagem (results/24_triagem_candidatos.csv)
python 24d_metadados_por_amostra.py     # grupo clínico de cada amostra dos estudos novos (precisa de acesso ao NCBI)
bash 25_novos_estudos.sh ESTUDO runs.txt PASTA PRIMER TRIM   # baixa e processa um estudo novo (ver cabeçalho)
NOVOS_DIR=... python 25_novos_estudos.py   # tabelas, CSTs e meta-análise com os estudos novos
python 21_figuras.py                    # 26 figuras do artigo em figuras/ (PNG e PDF); explicação de cada uma em figuras/EXPLICACOES.md
```

Textos para o artigo: `texto_metodos_EN.md` (Métodos) e `texto_artigo_EN.md` (exclusões, CSTs, N e pareamento, limitações, notas da
Tabela 1, validação e biomarcadores). Versão em português para a dissertação: `texto_dissertacao_PT.md`. A tabela `PAOLA_FILTRADA` é a da Paola sem leituras
"Unassigned" e de Eukaryota (corrige o P16).

As tabelas analisadas vêm da variável `TABELAS` (padrão: `PAOLA,TASSI_V2`). Opções: `PAOLA`,
`PAOLA_LIMPA` (sem P21, sem P16 e sem amostras < 1.000 leituras), `TASSI` (como está no Drive),
`TASSI_FIX` (P22 corrigido por prefixo) e `TASSI_V2` (P22 reprocessado no ramo V3-V4).

### Reprocessamento do P22

`p22_v3v4.sh` baixa as 119 runs do espelho do SRA na AWS, corta o primer 341F com cutadapt,
aplica o filtro de qualidade padrão do QIIME 2 (`qfilter_q2.py`) e roda o deblur 1.1.1 com
corte de 220 nt. Depois, `08b_reprocessa_p22.py` monta a tabela de gêneros (`TASSI_V2`).
A taxonomia vem das ASVs V3-V4 já classificadas no pipeline; a classificação final deve ser
refeita com o classificador SILVA V3-V4 no QIIME 2.


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
- **21 das 43 runs do P14 não são 16S** (DNA humano: Alu e satélite, nenhuma leitura com primer ou início de V3, conferido nos FASTQ do SRA). A exclusão nas duas tabelas é correta. No P16, ~55% das leituras do sublote principal também não são 16S, o que explica o Unassigned da tabela da Paola. Metade do único projeto brasileiro está fora das duas tabelas.
- **P22 reprocessado** (`TASSI_V2`): mesmas ASVs do pipeline original; câncer e controle do P22 vêm de
  corridas com leituras de ~222 e ~274 nt (por isso corte de 220 nt). Com essa tabela: LOPO 0,64 / 0,44 /
  0,48 / 0,35; projeto previsto com 86% de acerto; PERMANOVA classe 6,6%, projeto 14,5%, classe além do
  projeto 0,4% (p = 0,08).
- **Scripts R originais rodados de novo** (`results/R_tassi_v2/`): PERMANOVA condição 0,47% e projeto 6,36%;
  o `random_forest.R` usa `pROC::roc()` com direção automática, que nunca devolve AUC < 0,5. Com
  `direction = "<"` (`random_forest_direcao_fixa.R`) o LOPO cai de 0,596 para 0,457 de macro-AUC.
  O `gllvm_fit.R` reproduz a tabela original (AIC 313.373 → 300.307,4; η² por projeto 56,7% e 58,2%)
  e, com o P22 reprocessado, o η² por projeto cai para 30,3% e 15,9% (condição: 15,0% e 4,1%).
  η² calculado com `15_gllvm_eta2.py` sobre `gllvm_escores.csv`.
- **Meta-análise por projeto** (`13_meta_analise.py`): *Fusobacterium* e *Sneathia* ↑ no câncer em 4/4
  estudos (g ≈ 0,33, I² = 0%); *Sneathia*, *Megasphaera* e *Atopobium* ↑ na HSIL em 4/4; LSIL sem sinal;
  *Lactobacillus* heterogêneo (I² = 86%).
- **Abundância diferencial com projeto** (`12_abundancia_com_projeto.py`): câncer cai de 72 para 18 gêneros
  significativos; HSIL e LSIL caem para 0.
- **Contaminantes** (`11_contaminantes.py`): até 7,7% das leituras no P1 e 2,8% no P9; removê-los não muda
  o LOPO (0,63) nem a previsão do projeto (83–85%).
- **SHAP** (`20_shap.py`): no modelo com todos os projetos juntos, os 10 gêneros de maior |SHAP| de cada
  classe variam mais entre projetos do que entre classes (10/10, nas duas tabelas); a importância para a
  classe e para o projeto tem Spearman 0,81. Com o projeto fora do treino o ranking quase não muda (16 dos
  20 primeiros), mas o AUC cai: estabilidade do SHAP não valida biomarcador. Dentro dos projetos, o top 10
  repete *Atopobium* ↑ (HSIL, 3 de 4 projetos), *Sneathia* ↑ (HSIL), *Lactobacillus* ↓ e *Corynebacterium* ↑
  (câncer, P19 e P2), em linha com a meta-análise. Figuras: `results/20_shap_cancer_*.png` e
  `results/20_shap_beeswarm_cancer_*.png`.
- **N e pareamento** (`22*_*.py`): 39–42% dos cânceres e 68–76% dos controles vêm de estudos sem a outra
  classe. Embaralhar os rótulos dentro de cada estudo mantém ~95% do AUC da CV aleatória (câncer 0,96 → 0,92).
  Sem o P22, ~100 amostras pareadas dão o mesmo AUC num estudo novo (0,74–0,75) que somar 350–450 amostras de
  estudos de uma classe (0,67–0,76). Para g ≈ 0,3 com 80% de poder seriam ~175 por grupo pareado.
- **CSTs (VALENCIA)** (`23_cst_valencia.py`): espécies de Lactobacillus por alinhamento ao vSpeciateDB (85% das
  leituras). CST IV (pouco Lactobacillus) mais frequente no câncer no P19 e no P2: OR 4,5 (1,7–12,2; p = 0,003) sem o
  P22, contra 6,0 com tudo junto (P1 fora: 4 controles). L. crispatus (CST I) menos frequente no câncer nos 3 estudos (n.s.). Lesões: mesma
  direção, sem significância.
- **Estudos novos** (`25_novos_estudos.*`): PRJNA1085021, PRJEB40437, PRJNA622998 e PRJNA308947, processados com o mesmo
  pipeline. Replicam os achados: CST IV no câncer 67% × 35% (meta sem P22: OR 4,0, 2,1–7,5, I² = 0); Lactobacillus ↓ no câncer
  em 5/5 estudos (g −0,88); Dialister, Megasphaera e Sneathia ↑ na HSIL em 6–7/7 estudos; na LSIL, CST IV ↑ (OR 1,8) e
  L. iners ↓ (OR 0,52).
- **P16 na tabela da Paola**: 39% "Unassigned" e 2,5% Eukaryota, provável DNA do hospedeiro
  não filtrado; 29 amostras contra 47 na da Tassiane e 26 no artigo.
