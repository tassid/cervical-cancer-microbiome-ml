# O que cada figura mostra

As figuras saem de `analysis/21_figuras.py`. Cada uma tem PNG e PDF nesta pasta. Os rótulos estão
em inglês porque o artigo é em inglês; este texto explica cada figura em português.

**Convenções usadas em todas as figuras:**
- **Azul** é a tabela da Paola (a do artigo, 997 amostras).
- **Laranja** é a tabela da Tassiane com o P22 reprocessado (889 amostras).
- As classes clínicas têm cor fixa: câncer vermelho, HSIL violeta, LSIL amarelo e controle verde-água.
- **AUC:** 1 é classificação perfeita e 0,5 é acaso (linha tracejada). Abaixo de 0,5, o modelo erra mais do que acerta.
- **LOPO** (*leave-one-study-out*, ou projeto fora do treino): o modelo é treinado sem um projeto e testado só nele. Isso simula usar o modelo em um hospital novo.

---

## Validação dos modelos

### f01. AUC conforme o tipo de validação

**O que mostra.** O AUC do Random Forest das 4 classes (câncer, HSIL, LSIL e controle) em quatro situações:
1. avaliado nas mesmas amostras usadas no treino;
2. com validação cruzada aleatória de 10 partes;
3. com um modelo que recebe só o código do projeto, sem nenhuma bactéria;
4. com o projeto fora do treino.

**Como ler.** Cada painel é uma classe e cada ponto é uma tabela. As linhas ligam os quatro esquemas da esquerda para a direita.

**O que significa.**
- O AUC ≈ 1 do artigo só aparece no primeiro esquema, que não é validação.
- Na validação cruzada aleatória, o AUC cai para 0,97 (câncer), 0,85 (controle), 0,76 (HSIL) e 0,74 (LSIL). Mesmo assim é otimista, porque amostras do mesmo projeto aparecem no treino e no teste.
- O terceiro ponto é quase igual ao segundo: saber de qual projeto a amostra veio já dá o mesmo desempenho que o microbioma inteiro.
- Com o projeto fora do treino, câncer fica em 0,64–0,70 e as outras classes ficam no nível do acaso ou abaixo (LSIL 0,34). O modelo do artigo não funcionaria em um estudo novo.

### f02. Os 30 modelos da busca exaustiva

**O que mostra.** Câncer × controle com as 30 combinações testadas:
- 9 classificadores (Random Forest, regressão logística, SVM, XGBoost, kNN, Naive Bayes, ExtraTrees e outros);
- 3 formas de preparar os dados (abundância relativa, CLR e presença/ausência);
- com e sem SMOTE.

**Como ler.** Cada linha é um modelo. O ponto cinza é o AUC na validação cruzada aleatória e o ponto colorido é o AUC com o projeto fora do treino. Os modelos estão ordenados pelo AUC com projeto fora. No topo aparecem as medianas.

**O que significa.**
- Todos os modelos ficam entre 0,83 e 0,97 na validação aleatória e caem para 0,41–0,79 com o projeto fora do treino (mediana 0,70 na tabela da Paola e 0,64 na sua).
- Nenhuma combinação de modelo, normalização ou SMOTE resolve o problema. Ele não está no algoritmo, está na estrutura dos dados.
- Os melhores com projeto fora são regressões logísticas (0,79 com presença/ausência na tabela da Paola; 0,75 com CLR na sua).
- A busca exaustiva que o orientador sugeriu responde à pergunta "existe algum modelo melhor?": não existe.

### f03. AUC em cada projeto deixado de fora

**O que mostra.** Para os 4 projetos que têm câncer e controle (P1, P2, P19 e P22), o AUC de câncer × controle quando aquele projeto ficou fora do treino, para cada um dos 30 modelos.

**Como ler.** Cada ponto é um modelo e o traço preto é a mediana.

**O que significa.**
- **P19 (Nigéria):** é o mais estável (mediana 0,71). É o projeto em que câncer, lesões e controles foram sequenciados juntos.
- **P1 e P2:** variam muito de modelo para modelo (0,4 a 0,9). O resultado depende de detalhes da escolha do modelo.
- **P22:** fica abaixo de 0,5 em todos os modelos (mediana 0,39). O que os outros projetos ensinam como "câncer" aparece invertido no P22, porque lá câncer e controle foram sequenciados em corridas diferentes e a diferença entre eles é de corrida, não de doença.

### f04. Matrizes de confusão

**O que mostra.** Quantas amostras de cada classe verdadeira (linhas) o modelo classificou em cada classe (colunas). A coluna da esquerda é a validação cruzada aleatória e a da direita, o projeto fora do treino. A linha de cima é a tabela da Paola e a de baixo, a sua.

**Como ler.** Cada célula tem o número de amostras e o percentual da linha. Quanto mais escura, maior o percentual. Um bom modelo tem a diagonal escura.

**O que significa.**
- Mesmo na validação aleatória, HSIL e LSIL quase nunca são reconhecidas: 61–72% delas são chamadas de controle.
- Com o projeto fora do treino:
  - nenhuma LSIL é acertada;
  - só 7–14% das HSIL são acertadas;
  - 29–42% dos controles viram câncer.
- O AUC alto para HSIL e LSIL no artigo não corresponde a classificar essas amostras corretamente.

### f05. O microbioma identifica o projeto

**O que mostra.** A acurácia de um Random Forest que, com os mesmos gêneros, tenta adivinhar de qual projeto veio a amostra.

**Como ler.** A barra é a acurácia e o traço preto é o acaso (chutar sempre o maior projeto).

**O que significa.** O modelo acerta o projeto em 88% (Paola) e 86% (Tassiane) das amostras, contra 32–35% do acaso. O perfil bacteriano carrega uma "assinatura" forte de cada estudo (país, região do 16S, kit, laboratório e sequenciador). Como cada projeto tem uma mistura própria de classes, essa assinatura vira um atalho para o classificador.

### f06. Dentro de cada projeto

**O que mostra.**
- **Painel A:** o AUC de modelos treinados e testados dentro de um mesmo projeto, onde o projeto não pode ajudar. Cada cor é uma classe; o círculo é a tabela da Paola e o losango, a sua.
- **Painel B:** o AUC usando só o número de leituras por amostra.

**O que significa.**
- **P19:** o único projeto em que o câncer se separa bem (≈ 0,80) sem confusão com o projeto.
- **P22:** chega a 0,98, mas o painel B mostra que a profundidade de leitura sozinha já dá 0,97. Ali o modelo está separando corridas de sequenciamento, não câncer de controle (efeito de lote).
- **Lesões (P2, P10, P14, P19):** ficam entre 0,42 e 0,68, ou seja, pouco ou nenhum sinal.

### f25. Direção da curva ROC nos scripts R

**O que mostra.** O AUC com o projeto fora do treino calculado pelo `random_forest.R` da Tassiane de duas formas: com `direction = "auto"` (padrão do pROC, círculo cinza) e com a direção fixada (laranja).

**Como ler.** A seta vai do valor com "auto" para o valor correto.

**O que significa.**
- Com "auto", o pROC escolhe a direção que dá o maior AUC, então nunca devolve nada abaixo de 0,5. Um AUC de 0,34 vira 0,66.
- Com a direção fixa, controle, HSIL e LSIL ficam abaixo do acaso, e a média cai de 0,596 para 0,457.
- Essa correção precisa entrar em qualquer AUC calculado com o pROC no trabalho.

---

## Viés de projeto

### f07. PERMANOVA

**O que mostra.** Quanto da variação na composição (Bray-Curtis) é explicado:
- pela classe clínica sozinha;
- pelo projeto sozinho;
- pela classe depois de descontar o projeto (permutações dentro de cada projeto).

**O que significa.**
- O projeto explica 14–16% da variação e a classe, 7%.
- Depois de descontar o projeto, a classe explica só 0,4% e deixa de ser significativa (p = 0,08).
- Quase toda a diferença entre classes que aparece com os dados juntos vem de as classes estarem em projetos diferentes.

### f08. GLLVM

**O que mostra.** Quanto de cada eixo latente do modelo GLLVM (o `gllvm_fit.R` da Tassiane) é explicado pelo projeto (cinza) e pela classe clínica (violeta), antes e depois de reprocessar o P22.

**O que significa.**
- Na tabela original, os dois eixos são ~57% projeto e só 8–11% classe.
- Com o P22 reprocessado, o peso do projeto cai para 30% e 16%, porque parte do "efeito de projeto" era o erro de processamento do P22.
- O projeto continua sendo o que mais explica os eixos.

### f09. Diversidade de Shannon: efeito do câncer

**O que mostra.** A diferença de diversidade de Shannon entre câncer e controle:
- com todos os projetos juntos;
- com o projeto no modelo;
- dentro de cada projeto que tem os dois grupos.

**Como ler.** O ponto à direita do zero indica câncer mais diverso; à esquerda, menos diverso. O valor de p está à direita.

**O que significa.**
- Com tudo junto, o câncer parece muito mais diverso (+1,0, p ≈ 10⁻²⁴).
- Com o projeto no modelo, a diferença cai para +0,1 e deixa de ser significativa.
- Dentro dos projetos, o efeito muda de sinal: maior no P1 e no P19, sem diferença no P2 e **menor** no P22.
- "Câncer tem mais diversidade" não pode ser afirmado com estes dados.

### f10. Shannon por projeto e classe

**O que mostra.** As caixas (boxplots) de Shannon por classe em cada um dos 10 projetos (tabela da Paola). O número embaixo de cada rótulo é o número de amostras.

**O que significa.**
- Quatro projetos só têm câncer (P6, P9, P16 e, quase, P1) e o P21 é quase só controle.
- Os projetos só de câncer têm diversidade alta por características próprias (região, kit, população), e isso "contamina" a comparação feita com todos os dados juntos.
- Esta figura explica a f09.

### f15. De onde vêm os biomarcadores do artigo

**O que mostra.** Para cada gênero citado no artigo (Boruta, LEfSe e heatmap), a fração de toda a abundância dele que está concentrada em um único projeto. À direita, o projeto que concentra.

**Como ler.** Pontos à direita da linha vermelha (80%) indicam um gênero que existe praticamente em um só estudo.

**O que significa.**
- Na tabela da Paola, 8 dos 27 gêneros têm ≥ 80% da abundância em um projeto:
  - *Brochothrix* (P22), *Aeribacillus* (P9) e *Wolbachia* (P1), com ~100%;
  - *Burkholderia* (96% no P21, que é quase só controle);
  - *Halomonas* (P9) e *Rhodococcus* (P1).
- Esses "biomarcadores" marcam um estudo, não uma doença. *Wolbachia*, por exemplo, é uma bactéria de insetos, típica de contaminação.
- Na sua tabela, *Burkholderia* cai para 32% porque o P21 não está nela.

### f26. Contaminantes de reagente

**O que mostra.** A porcentagem das leituras de cada projeto e classe que pertence a gêneros conhecidos como contaminantes de kit e laboratório (lista de Salter et al.). O traço indica que o projeto não tem aquela classe.

**O que significa.**
- A contaminação está concentrada no câncer do P1 (6–8%) e do P9 (2–3%) e nas HSIL do P21.
- Esses projetos têm pouca biomassa ou foram processados de forma diferente.
- Remover esses gêneros **não** muda os resultados (o LOPO fica em 0,63 e o projeto continua previsível em 83–85%). O viés de projeto não se explica só por contaminação.

---

## Diferenças entre a tabela da Paola e a da Tassiane

### f11. Concordância entre os pipelines

**O que mostra.**
- **Painel A:** para as mesmas amostras, a distância Bray-Curtis mediana entre o perfil de gêneros na tabela da Paola e na sua (0 = idêntico).
- **Painel B:** quantas leituras por amostra a sua tabela manteve em relação à da Paola.

**O que significa.**
- Em 8 dos 9 projetos as tabelas são praticamente iguais (Bray-Curtis ≤ 0,09).
- **P16:** a exceção (0,49). Na tabela da Paola, 39% das leituras são "Unassigned" ou de eucariotos (DNA humano); filtrando essas leituras, a distância cai para 0,09.
- **Profundidade (painel B):**
  - P19: a sua tabela mantém 2,3 vezes mais leituras;
  - P14, P16 e P1: mantém menos.

  Essas diferenças vêm dos filtros de qualidade e do corte dos primers, não mudam a composição e explicam por que alguns números de amostras diferem.

### f12. Onde as amostras se perderam

**O que mostra.** Por projeto, o número de runs catalogadas (cinza), as amostras que ficaram na tabela da Paola (azul) e as que ficaram na sua (laranja), considerando ≥ 1.000 leituras.

**O que significa.**
- **P14:** perde metade das runs nas duas tabelas, porque 21 das 43 runs são DNA humano, não 16S.
- **P16:** tem dois grupos de runs; a Paola ficou com 29 e você com 47.
- **P21:** só está na tabela da Paola.
- **Totais:** 1.042 catalogadas, 997 na tabela da Paola e 889 na sua.
- A Tabela 1 do artigo precisa refletir essas perdas.

### f13. Composição média por projeto

**O que mostra.** A abundância relativa média dos 7 gêneros mais comuns em cada projeto. As duas barras de cada projeto são as duas tabelas (P = Paola, T = Tassiane); o cinza é o resto.

**O que significa.**
- As duas barras de cada projeto são quase iguais: os dois pipelines enxergam a mesma comunidade. A única diferença visível é o P16.
- **Diferenças entre projetos:**
  - P2, P10 e P14 são dominados por *Lactobacillus*;
  - P1, P6 e P9 (só câncer) têm pouco *Lactobacillus* e muitos outros gêneros (o cinza);
  - P19 tem *Pseudomonas*.
- Estas diferenças são o que o modelo aprende quando o projeto e a classe estão misturados.

### f14. Gênero a gênero, nas mesmas amostras

**O que mostra.** Para cada projeto, cada ponto é um gênero: no eixo x, a abundância média na tabela da Paola; no eixo y, na sua (escala log). O ρ (Spearman) mede a concordância.

**Como ler.** Pontos sobre a linha tracejada indicam que as duas tabelas dão o mesmo valor. Os rótulos vermelhos marcam as maiores discordâncias entre gêneros acima de 1%.

**O que significa.**
- A concordância é alta em todos os projetos (ρ entre 0,77 e 0,98).
- As discordâncias se concentram em gêneros raros (canto inferior esquerdo) e em leituras sem gênero (diferença de banco de dados e de filtro).
- Os gêneros principais batem. A escolha entre as duas tabelas não muda as conclusões.

---

## Biomarcadores

### f16. Abundância diferencial com e sem projeto

**O que mostra.** Quantos gêneros são significativos (q < 0,05, modelo linear em CLR com correção de Benjamini-Hochberg) em cada comparação, sem o projeto no modelo (cinza) e com o projeto (colorido).

**O que significa.**

| Comparação | Sem projeto | Com projeto |
|---|---|---|
| Câncer | 60–72 gêneros | 18 |
| HSIL | 14–15 | 0–3 |
| LSIL | 8 | 0–2 |

A maior parte das diferenças "significativas" vem do projeto. Ajustar por projeto é obrigatório em qualquer teste de abundância.

### f17. Meta-análise: câncer × controle

**O que mostra.** O tamanho do efeito (g de Hedges) de três gêneros dentro de cada projeto que tem câncer e controle (n câncer/controle entre parênteses), com intervalo de 95%. Embaixo, o losango é o efeito combinado (efeitos aleatórios).

**Como ler.** À direita do zero, o gênero é mais abundante no câncer. "pooled p" é o valor de p do efeito combinado e I² mede o quanto os projetos discordam (0% = concordam).

**O que significa.**
- ***Fusobacterium* e *Sneathia*:** sobem no câncer nos 4 projetos, sem discordância (I² = 0%) e com efeito combinado significativo (g ≈ 0,33, p ≈ 0,01–0,02). É um sinal que se repete entre estudos, mas é pequeno.
- ***Lactobacillus*:** cai no câncer no P19 e no P2, mas **sobe** no P22 (de novo o efeito de corrida). Por isso o combinado não é significativo e a discordância é alta (I² = 85%).

### f18. Meta-análise: HSIL × controle

**O que mostra.** O mesmo da f17, para HSIL nos 4 projetos que têm HSIL e controle (P10, P14, P19 e P2).

**O que significa.**
- *Sneathia* (p ≈ 0,006), *Megasphaera* (p ≈ 0,02–0,05) e *Atopobium* (p ≈ 0,04) são mais abundantes na HSIL, com a mesma direção nos 4 estudos.
- São os candidatos a biomarcador de HSIL que este conjunto de dados sustenta. Os efeitos são pequenos (g ≈ 0,2–0,5) e não servem sozinhos para classificar pacientes.

### f19. Seleção de gêneros: todos juntos × dentro dos projetos

**O que mostra.** Quantos gêneros cada método escolhe com todos os projetos juntos (como no artigo) e quantos aparecem em pelo menos dois projetos quando o método é rodado dentro de cada projeto.

**O que significa.**

| Método | Todos os projetos juntos | Dentro dos projetos (≥ 2) |
|---|---|---|
| Boruta | 50 (Paola) / 37 (Tassiane) | 0 |
| LEfSe | 104 | 1 (*Gemella*) |
| SHAP top 10 | 10 | 4 |

- As listas grandes do artigo vêm, em sua maior parte, da diferença entre projetos.
- O SHAP sempre devolve 10 gêneros, por isso a barra da esquerda é fixa. Não é um teste estatístico.

---

## SHAP

O SHAP mede quanto cada gênero empurra a previsão de cada amostra para uma classe. Ele explica **o que o
modelo usa**, não se aquilo é biologia.

### f20. SHAP do modelo global para câncer

**O que mostra.** Os gêneros mais importantes para o modelo reconhecer câncer (|SHAP| médio), nas duas tabelas. O rótulo indica o projeto que concentra a abundância do gênero e quanto.

**O que significa.**
- **Topo da lista:** leituras sem gênero (concentradas no P16 ou no P22), *Lactobacillus*, *Enterococcus* e *Streptococcus* (P6).
- **Mais abaixo:** vários gêneros de um projeto só, como *Halomonas* (97% no P9), *Rhodococcus* (95% no P1) e *Burkholderia* (96% no P21).
- **Diferenças entre as tabelas:**
  - *Burkholderia* só pesa na da Paola, porque o P21 só existe nela;
  - *Shuttleworthia* pesa mais na sua.
- O modelo usa o que diferencia projetos. É a figura de SHAP que o artigo mostraria hoje, e ela não deve ser lida como biomarcador.

### f21. Importância para a classe × importância para o projeto

**O que mostra.** Cada ponto é um gênero. No eixo x, a importância (SHAP) num modelo que prevê o **projeto**; no eixo y, num modelo que prevê a **classe clínica**.

**O que significa.**
- Os pontos sobem juntos (Spearman 0,81 nas duas tabelas): os gêneros que ajudam a dizer a classe são os mesmos que ajudam a dizer o projeto.
- Se o sinal fosse de doença, a correlação seria fraca.

### f22. Os gêneros do SHAP variam mais entre projetos

**O que mostra.** Para os 30 gêneros com maior SHAP, quanto da variação de cada um é explicado pela classe (eixo x) e pelo projeto (eixo y), medido pelo η².

**Como ler.** Acima da linha tracejada, o gênero varia mais entre projetos do que entre classes.

**O que significa.** Os 30 de 30 estão acima da linha nas duas tabelas. Nenhum dos gêneros que o modelo considera importantes é, antes de tudo, um marcador de classe clínica.

### f23. O SHAP com o projeto fora do treino

**O que mostra.** Para cada projeto deixado fora do treino, quantos dos 20 gêneros mais importantes continuam entre os 20 do modelo com todos os dados.

**O que significa.**
- O ranking quase não muda (12 a 18 de 20, média 16), mas o AUC cai para 0,34–0,70 nesses mesmos testes.
- Um ranking de SHAP estável não prova que o biomarcador funciona: o modelo usa sempre os mesmos gêneros, e eles não servem para um estudo novo.
- Este argumento responde a quem disser "o SHAP é estável, então os biomarcadores são robustos".

### f24. SHAP dentro de cada projeto

**O que mostra.** Um Random Forest treinado dentro de cada projeto e comparação (câncer ou HSIL contra controle). As colunas são projeto × comparação e as linhas são gêneros que entraram no top 10 de algum deles.

**Como ler.**
- Vermelho: o gênero mais abundante empurra para o caso (câncer ou HSIL).
- Azul: empurra para controle.
- Branco: o gênero não entrou no top 10.
- Quanto mais forte a cor, maior o SHAP.

**O que significa.**
- **HSIL:** *Atopobium* aparece em vermelho em 3 de 4 projetos.
- **Câncer:** *Lactobacillus* aparece em azul (mais alto nos controles) e *Corynebacterium* em vermelho no P19 e no P2.
- **P22:** é dominado por gêneros de reagente em azul (*Ralstonia*, *Brevundimonas*, *Rhizobium*), mais um sinal de efeito de corrida.
- Dentro dos projetos, o SHAP concorda com a meta-análise. É esta a versão do SHAP que faz sentido levar para o artigo.

---

## N e pareamento

### f27. Os estudos de uma classe ajudam?

**O que mostra.** Responde à dúvida de que ajustar pelo projeto diminuiria o N.
- **Painel A:** o AUC da validação cruzada aleatória com os rótulos reais (ponto cheio) e com os rótulos embaralhados dentro de cada estudo (ponto vazio, média de 10 vezes). Embaralhar dentro do estudo apaga a informação de doença, mas mantém de qual estudo cada amostra veio.
- **Painel B:** o AUC num estudo novo (P1, P2 ou P19, sem o P22) conforme aumenta o N de treino. Na linha cheia, o N vem de estudos com câncer e controle (pareados); na tracejada, somam-se os estudos só de câncer (P6, P9, P16) e só de controle (P10, P14, P21).

**O que significa.**
- **Painel A:** o AUC quase não cai (câncer 0,96 → 0,92). O desempenho do modelo com todos os dados juntos vem de reconhecer o estudo, não a doença.
- **Painel B:** com ~100 amostras pareadas o AUC já é 0,74–0,75. Somar 350–450 amostras de estudos de uma classe não melhora (Paola, 0,76) ou piora (Tassiane, 0,67).
- O N que ajuda é o pareado. Para efeitos do tamanho achado na meta-análise (g ≈ 0,3), seriam necessárias ~175 amostras por grupo dentro dos mesmos estudos. O caminho é buscar mais estudos com caso e controle, não somar estudos de uma classe.
