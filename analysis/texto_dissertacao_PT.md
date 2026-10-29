# Seções para a dissertação (rascunho)

Textos em português para adaptar ao capítulo de Métodos, Resultados e Discussão. Os números vêm
de `results/22*`, `results/23*` e das figuras f27, f28 e f29. A versão em inglês, mais curta,
está em `texto_artigo_EN.md`.

---

## Métodos

### Tipos de comunidade vaginal (CSTs)

As amostras foram classificadas em tipos de comunidade vaginal (*community state types*, CSTs)
com o VALENCIA (France et al., 2020). O VALENCIA atribui cada amostra ao mais parecido de 13
perfis de referência (subtipos de CST), definidos a partir de mais de 13 mil amostras vaginais,
usando a similaridade de Yue-Clayton. Os tipos são:
- **CST I:** dominado por *Lactobacillus crispatus*;
- **CST II:** por *L. gasseri*;
- **CST III:** por *L. iners*;
- **CST V:** por *L. jensenii*;
- **CST IV:** pouca abundância de *Lactobacillus*. Divide-se em IV-A e IV-B, com *Gardnerella* e *Atopobium*, e IV-C, com outros anaeróbios, *Streptococcus*, *Enterococcus*, *Bifidobacterium* ou *Staphylococcus*.

O VALENCIA precisa da espécie para *Lactobacillus*, *Gardnerella*, *Atopobium* e *Sneathia*. O
SILVA 138 não distinguiu *L. crispatus* nem *L. gasseri* nas ASVs deste trabalho, então:
- as ASVs desses gêneros foram alinhadas às sequências de referência do vSpeciateDB (Holm et al., 2024), usando a referência da mesma região do 16S (V3-V4 ou V4);
- a ASV recebeu a espécie quando a identidade foi de pelo menos 97% e o melhor alinhamento correspondeu a uma única espécie vaginal;
- todas as ASVs de *Gardnerella* foram tratadas como *G. vaginalis*, como no VALENCIA;
- *Prevotella* foi agrupada no nível de gênero, nas amostras e nos perfis de referência.

Com isso, 85% das leituras de *Lactobacillus* receberam espécie. A classificação foi feita nas
889 amostras da tabela reprocessada, a única que tem as sequências das ASVs.

Para cada comparação (câncer, HSIL ou LSIL contra controle), a proporção de amostras em CST IV,
CST I e CST III foi comparada dentro de cada estudo que tinha pelo menos cinco amostras em cada
grupo. O efeito em cada estudo foi medido pelo odds ratio, com correção de 0,5 nas caselas.
Os estudos foram combinados por meta-análise de efeitos aleatórios (DerSimonian-Laird), com e
sem o PRJNA725946 (P22), cujo caso e controle foram sequenciados em corridas diferentes. O P1
(PRJNA687644) ficou de fora dessas comparações porque tem apenas quatro controles: com uma casela
zerada, a correção de 0,5 chega a inverter o sinal do efeito.

### Delineamento dentro dos estudos e tamanho amostral

Quatro estudos tinham apenas amostras de câncer e um tinha quase só controles. Para verificar se
esses estudos de uma classe só acrescentam informação à comparação entre caso e controle, foram
feitas quatro análises:

1. **N efetivo.** Contagem das amostras de cada grupo que vêm de estudos com caso e controle.
2. **Embaralhamento dentro do estudo.** Os rótulos clínicos foram embaralhados dentro de cada estudo, o que apaga a informação de doença mas mantém a origem de cada amostra. Em seguida, a validação cruzada aleatória de 10 partes foi repetida (10 permutações).
3. **Curva de aprendizado.** Na comparação câncer × controle, modelos de Random Forest e regressão logística foram treinados de duas formas: só com estudos que têm os dois grupos (com frações crescentes das amostras) ou com esses estudos mais os estudos de uma classe. Os modelos foram avaliados no estudo deixado de fora. O P22 foi excluído dessas análises.
4. **Poder.** Cálculo do número de amostras por grupo necessário para detectar uma diferença padronizada de 0,3 com 80% de poder (α = 0,05, bilateral).

---

## Resultados

### Tipos de comunidade vaginal

| CST | Amostras | % |
|---|---|---|
| IV-C | 318 | 36 |
| III | 213 | 24 |
| IV-B | 211 | 24 |
| I | 121 | 14 |
| II e V | 26 | 3 |

**Câncer.** Dentro dos estudos, o CST IV foi mais frequente no câncer do que nos controles no
P19 (PRJNA914231; 83% contra 50%, teste exato de Fisher p = 0,04) e no P2 (PRJNA518153; 70%
contra 31%, p = 0,06). No P22 foi menos frequente (45% contra 57%), o que é compatível com o
efeito de corrida desse estudo.

| CST IV no câncer | OR | IC 95% | p |
|---|---|---|---|
| Sem o P22 | 4,5 | 1,7–12,2 | 0,003 |
| Com o P22 | 2,1 | 0,5–9,7 | 0,34 (I² = 81%) |
| Todas as amostras juntas, sem considerar o estudo | 6,0 | — | — |

Juntar as amostras sem considerar o estudo superestima o efeito. O CST I (*L. crispatus*) foi
menos frequente no câncer nos três estudos comparáveis, mas sem significância (OR 0,58; IC
0,25–1,36).

**Lesões.** Os efeitos foram na mesma direção, mas menores e sem significância:

| Comparação | OR | IC 95% | p |
|---|---|---|---|
| CST IV na LSIL | 1,6 | 0,95–2,7 | 0,08 |
| CST III (*L. iners*) na LSIL | 0,57 | 0,32–1,01 | 0,06 |
| CST IV na HSIL | 1,3 | 0,75–2,2 | 0,36 |

Esses resultados indicam que a perda da dominância de *Lactobacillus* é o padrão de composição
mais consistente associado ao câncer cervical neste conjunto de dados. Nas lesões, o sinal é
fraco.

### Estudos de uma classe e tamanho amostral

**Uma grande parte do N não informa a comparação.** Na tabela original:
- 113 dos 287 cânceres (39%) vêm de estudos sem nenhum controle;
- 331 dos 436 controles (76%) vêm de estudos sem nenhum câncer.

Na tabela reprocessada, essas proporções são 42% e 68%.

**O desempenho com todos os dados juntos vem principalmente do estudo de origem.** Com os rótulos
embaralhados dentro de cada estudo, a validação cruzada aleatória quase não perdeu desempenho:

| Classe | AUC com rótulos reais | AUC com rótulos embaralhados |
|---|---|---|
| Câncer | 0,96 | 0,92 |
| Controle | 0,84 | 0,81 |

**Mais N só ajuda se for pareado.** Com cerca de 105 amostras de estudos com caso e controle, o
Random Forest alcançou AUC de 0,74–0,75 no estudo deixado de fora. Acrescentar as 350–450 amostras
dos estudos de uma classe:
- não melhorou o resultado na tabela original (0,76);
- piorou o resultado na tabela reprocessada (0,67).

O que esses estudos acrescentam é sobretudo o contraste entre controles dominados por
*Lactobacillus* e cânceres com pouco *Lactobacillus*, junto com artefatos próprios de cada
estudo: leituras sem gênero vindas de DNA humano no P16 e contaminantes de reagente no P9. Dentro
do P19, a diversidade de Shannon sozinha separou câncer de controle com AUC de 0,80, o mesmo valor
dos modelos.

**O N pareado disponível ainda é insuficiente.** Para detectar uma diferença padronizada de 0,3
com 80% de poder, seriam necessárias cerca de 175 amostras por grupo dentro dos mesmos estudos,
mais do que o disponível hoje.

---

## Discussão: limitações e estudos futuros

### Limitações

**1. Classe clínica confundida com estudo de origem.**
- Quatro estudos contribuíram só com amostras de câncer e um quase só com controles.
- Grande parte da amostra total não informa a comparação entre caso e controle.
- As estimativas dentro dos estudos se apoiam em poucos estudos: a associação do CST IV com o câncer depende de dois.
- Juntar todas as amostras infla tanto o desempenho dos classificadores quanto o tamanho dos efeitos.

**2. Problemas nos dados depositados.**
- **P22:** caso e controle foram sequenciados em corridas diferentes, com leituras de comprimentos diferentes. A comparação dentro desse estudo não se separa do efeito de lote.
- **P14:** metade das corridas do único estudo brasileiro contém DNA humano, e não amplicons de 16S.
- **P16:** as 55 corridas listadas formam dois grupos com profundidade e metadados diferentes, e a qual BioProject pertence o segundo grupo ainda precisa ser confirmado.

**3. Heterogeneidade técnica.**
- Os estudos usaram regiões diferentes do 16S (V3-V4 ou V4), além de primers, kits e plataformas diferentes.
- Isso limita a resolução no nível de espécie e a comparabilidade entre estudos.
- 45% das amostras tiveram similaridade baixa (menor que 0,5) com o CST atribuído. Isso é esperado em populações fora da América do Norte, onde as referências do VALENCIA foram definidas, e em amostras de câncer.

**4. Ausência de variáveis clínicas.** Status de HPV, idade, menopausa, tipo histológico e
estadiamento não estavam disponíveis para todos os estudos e não puderam ser ajustados. O HPV,
em particular, é um fator de confusão importante para a relação entre microbiota e lesões.

**5. Taxonomia do P22.** A classificação taxonômica do P22 reprocessado ainda precisa ser refeita
com o classificador SILVA V3-V4 no QIIME 2.

### Estudos futuros

1. **Coleta e sequenciamento pareados.** Sequenciar casos e controles da mesma população nas mesmas corridas, registrando HPV, idade, menopausa e dados do tumor, e com pelo menos 175 amostras por grupo.
2. **Meta-análise com mais estudos pareados.** Incluir mais estudos com caso e controle. O script `24_busca_sra.py` faz esse levantamento no SRA, e os autores dos estudos só de câncer podem ser contatados sobre controles não depositados.
3. **Validação com o estudo fora do treino.** Usar o leave-one-study-out e o ajuste por estudo como padrão, em vez da validação cruzada aleatória.
4. **Maior resolução taxonômica.** Sequenciamento shotgun ou do gene 16S completo, para distinguir espécies e linhagens de *Lactobacillus* e de *Gardnerella* com segurança.
