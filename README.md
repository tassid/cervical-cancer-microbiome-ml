# Validação por projeto: microbioma cervicovaginal e câncer cervical

Documento de acompanhamento técnico do projeto de pesquisa da autora, descrito em:

> "Validação por projeto em meta-análises de microbioma: um estudo de caso em câncer cervical", LATINOWARE / Latin.Science, 2026 (autoria própria).

Segue o mesmo formato do repositório de réplica do Hagen et al. (2024) sobre microbioma do solo e estresse hídrico, esse sim um exercício de replicação de terceiros, mas aqui o objeto é o andamento do próprio artigo: um site em React/Vite que documenta o pipeline passo a passo, com glossário interativo e comandos prontos pra copiar.

## Contexto

Etapa preparatória da dissertação de mestrado da autora no PPGTCA/UTFPR, cujo objeto é a classificação de sanidade em soja a partir do microbioma, com validação leave-one-project-out entre múltiplos projetos de origem. O artigo aqui acompanhado investiga exatamente esse problema, confundimento entre projeto de origem e condição clínica em dados agregados de microbioma, num dataset de câncer cervical (997 amostras, 10 BioProjects), e foi submetido como trabalho em andamento: a avaliação empírica do protocolo de validação proposto ficou para uma etapa seguinte, que é o que este caderno documenta.

## O que o site documenta

- O dataset agregado (Tabela I do artigo: 10 BioProjects, 5 países, 4 classes clínicas)
- Um glossário interativo dos conceitos envolvidos (PERMANOVA, GLLVM, efeito de lote, leave-one-project-out, controle negativo, etc.)
- Todos os comandos planejados do pipeline, na ordem em que entram, com botão de copiar
- O status atual do projeto e os valores publicados no artigo, usados como alvo de comparação
- A relação entre este trabalho e os objetivos da dissertação

## Stack técnica

- [Vite](https://vite.dev/) + [React](https://react.dev/) + TypeScript
- [lucide-react](https://lucide.dev/) para os ícones

## Rodando localmente

```bash
npm install
npm run dev
```

## Build de produção

```bash
npm run build
```

Os arquivos finais são gerados em `dist/`.

## Estrutura

```
src/
  App.tsx       , todo o conteúdo e a lógica do documento
  main.tsx      , ponto de entrada React
  index.css     , reset mínimo de estilos
```

## Status

Documento vivo, a seção 4 (comandos) e a seção 5 (status) são atualizadas conforme o trabalho avança de fato. O pipeline próprio já está em execução real no terminal, não apenas planejado.

**Concluído:**
- Confirmação dos primers de amplificação 16S para 8 dos 10 BioProjects, por cruzamento manual do artigo-fonte de cada projeto (Tabela 1b, seção 4). P2 e P21 foram verificados exaustivamente, artigo principal e material suplementar de ambos, e a sequência do primer nunca foi publicada, pois o sequenciamento foi terceirizado a fornecedores comerciais (Second Genome Inc. e Novogene) que tratam o protocolo como proprietário.
- Accessions e metadados clínicos (Run/Sample → classe clínica) para as 1.042 amostras catalogadas, via `metadata.txt` compartilhado pela coautora Paola Gyuliane Gonçalves, bate célula a célula com a Tabela I do artigo.
- Download dos FASTQ brutos dos 10 BioProjects, import no QIIME 2 e corte de primers via cutadapt (Tabela 1c), incluindo a descoberta de que P9, P14 e P2 já vinham sem primer na origem, a correção empírica do primer do P19 e a confirmação de que P10 usa o par original de Caporaso, diferente de P9/P16.
- Denoising via deblur na região V3-V4 (P1, P6, P14, P19): 289 de 309 amostras retidas (93,5%), fechado.
- Denoising via deblur na região V4 (P2, P9, P10, P16, P22): 627 de 628 amostras retidas (99,8%), fechado. No caminho, descoberto que o BioProject P10 mistura dois sublotes, cerca de 154 amostras com o primer presente e cerca de 165 já sem primer na origem, exigindo processamento separado (P10a/P10b). A primeira tentativa de juntar os dois sublotes travou com um erro de ID duplicado (`Metadata IDs must be unique`), corrigido excluindo as 165 IDs do sublote sem primer da exportação do P10a antes de montar o manifest combinado. **Correção (out/2026):** o P22 (PRJNA725946) é V3-V4, não V4 (as leituras começam em `TAGGGAATCTTCCACAATGG`, início de V3 após o 341F). Processado no ramo V4, 79% das leituras ficaram sem gênero e surgiram gêneros espúrios (*Dickeya*, *Nocardia*). Correção provisória por correspondência de sequência em `analysis/08_corrige_p22.py`; falta reprocessar o P22 no ramo V3-V4.
- Taxonomia via SILVA nas duas regiões. O classificador pré-treinado oficial não pôde ser usado por incompatibilidade de versão do scikit-learn (0.24.1 do artefato vs. 1.7.1 instalado); contornado retreinando localmente um classificador Naive Bayes por região a partir das referências brutas do SILVA 138, extraídas para a região amplificada de cada par de primer antes do treino.
- Filtragem e fusão das duas regiões: cloroplasto/mitocôndria/arqueia e singletons removidos, tabelas colapsadas em gênero taxonômico (as ASVs de V3-V4 e V4 não são diretamente comparáveis) e mescladas, resultando em 889 amostras finais, de um teto alcançável de 937 (1.042 catalogadas menos o P21, excluído por falta de primer confirmado). 889/997 = 89,2% do número publicado no artigo, diferença majoritariamente explicada pela exclusão do P21.
- PERMANOVA sobre dissimilaridade de Bray-Curtis, com o metadado clínico da coautora Paola Gyuliane Gonçalves (`metadata/metadata_master.tsv`) cruzado pelo identificador de amostra contra as 889 amostras finais, correspondência perfeita nas 889 linhas. Condição clínica explicou 0,59% da variação (F = 2,23; p = 0,002) e projeto de origem explicou 9,19% (F = 20,75; p = 0,001), cerca de 15,5 vezes mais; localidade saiu colinear com projeto (0 graus de liberdade), já que cada projeto vem de um único país. Refeito com o P22 corrigido (`analysis/06_permanova.py`, permutações dentro do projeto): classe sozinha 6,6%, projeto sozinho 14,5%, classe além do projeto 0,4% (p = 0,10). **Com o P22 reprocessado no ramo V3-V4 (`analysis/p22_v3v4.sh`), o mesmo `permanova.R` dá condição clínica 0,47% (F = 1,60; p = 0,032) e projeto 6,36% (F = 13,08; p = 0,001)**: parte do efeito de projeto vinha do P22 mal classificado, mas projeto ainda explica ~14 vezes mais que condição.
- GLLVM com e sem projeto de origem como efeito fixo, sobre os 98 gêneros presentes em pelo menos 10% das 889 amostras finais (dos 1.597 gêneros totais da tabela). O AIC caiu de 313.373 para 300.307,4 ao incluir projeto, e os dois eixos latentes do modelo sem covariáveis são explicados majoritariamente por projeto de origem (η² de 56,7% e 58,2%) e só marginalmente por condição clínica (η² de 11,1% e 7,9%). Este ajuste usou a tabela com o P22 mal classificado e precisa ser refeito (o pacote `gllvm` não pôde ser instalado no ambiente da auditoria).
- Protocolo de validação Random Forest sobre as 889 amostras finais, abundância relativa por gênero, com a interface x/y do `ranger` (necessária porque os nomes de linhagem taxonômica do SILVA quebram a interface de fórmula do R). Macro-AUC de 0,811 na CV estratificada aleatória cai para 0,6 na validação leave-one-project-out, queda mais acentuada na classe câncer (0,959 para 0,717), e o controle negativo prevê o projeto de origem a partir da composição com 82,79% de acurácia, bem acima do acaso para 9 classes. Essa era a contribuição central declarada como trabalho em andamento no artigo. Refeito com o P22 corrigido (`analysis/03_ml_vies.py`, scikit-learn): câncer cai de 0,964 na CV aleatória para 0,622 no leave-one-project-out (controle 0,821 → 0,427; HSIL 0,733 → 0,465; LSIL 0,708 → 0,354), e o controle negativo prevê o projeto com 86,4% de acurácia (acaso: 35,2%). Um modelo que recebe só o ID do projeto, sem microbioma, atinge 0,943 em câncer. **Correção (out/2026):** o `pROC::roc()` usa `direction = "auto"` por padrão e inverte curvas abaixo de 0,5, então nunca reporta AUC < 0,5. Com `direction = "<"` (`analysis/random_forest_direcao_fixa.R`) e o P22 reprocessado, o mesmo script dá macro-AUC 0,808 na CV aleatória e **0,457 no LOPO** (câncer 0,606; controle 0,419; HSIL 0,467; LSIL 0,337), ou seja, abaixo do acaso fora do projeto de origem; controle negativo 83,0%.

- Contrastes par a par entre condições clínicas, PERMANOVA restrito a 2 classes por vez: controle vs. câncer 6,52% (F = 43,36; p = 0,001; n = 624), HSIL vs. câncer 5,75% (F = 27,56; p = 0,001; n = 454), LSIL vs. câncer 4,44% (F = 18,93; p = 0,001; n = 409), HSIL vs. LSIL não significativo (F = 1,60; p = 0,107; n = 265). Valores próximos aos publicados no artigo (5,0%; 3,6%; 2,2%; não significativo com p = 0,067), inclusive acertando qual par não chega a ser significativo. Com o P22 reprocessado: controle vs. câncer 6,00% (F = 39,73), HSIL vs. câncer 3,35% (F = 15,65), LSIL vs. câncer 2,52% (F = 10,52), todos p = 0,001, ainda mais perto do artigo.

PERMANOVA, GLLVM e Random Forest confirmam, de forma independente e sobre dado processado do zero pelo pipeline próprio, o mesmo padrão qualitativo do artigo: projeto de origem domina a variação composicional muito mais do que condição clínica, e a composição carrega assinatura de projeto de origem forte o suficiente para ser prevista diretamente. As quatro etapas estatísticas planejadas estão concluídas.

## Auditoria de viés e comparação com a tabela da Paola (out/2026)

A pasta [`analysis/`](analysis/) compara a tabela usada no artigo da Paola com a do pipeline próprio e testa as conclusões do manuscrito contra o viés de projeto. Resumo em [`analysis/README.md`](analysis/README.md) e relatório em `analysis/relatorio_vies.html`. Pontos principais:

- O AUC ≈ 1 do artigo só é reproduzido avaliando o modelo no próprio treino; CV aleatória dá 0,97/0,85/0,76/0,74 e leave-one-project-out 0,70/0,51/0,46/0,34.
- Um modelo que recebe só o ID do projeto atinge o mesmo AUC que o microbioma inteiro.
- O P22 foi processado no ramo V4, mas é V3-V4; 79% das leituras ficaram sem gênero. **Reprocessado a partir do SRA** (`analysis/p22_v3v4.sh`, `analysis/08b_reprocessa_p22.py`): o deblur reproduziu exatamente as ASVs originais, então o erro era só o classificador. Depois disso as duas tabelas concordam (Spearman 0,97–1,00).
- **No P22, câncer e controle foram sequenciados em corridas diferentes**: depois do primer, as 65 amostras de câncer têm leituras de ~222 nt e os 54 controles, ~274 nt. Com o corte de 250 nt do ramo V3-V4 todo o câncer seria descartado, por isso o P22 usa 220 nt. Dentro do P22 a profundidade sozinha separa as classes (AUC 0,97).
- Meta-análise por projeto (efeitos aleatórios): *Fusobacterium* e *Sneathia* sobem no câncer em 4 de 4 estudos (g ≈ 0,33, I² = 0%); *Sneathia*, *Megasphaera* e *Atopobium* sobem na HSIL em 4 de 4; nada consistente em LSIL; *Lactobacillus* é heterogêneo (I² = 86%).
- Contaminantes de kit (48 gêneros) pesam até 7,7% no P1 e 2,8% no P9, mas removê-los não muda os resultados.

### Incongruências entre a tabela da Paola e a do pipeline próprio

| # | Ponto | Paola (artigo) | Pipeline próprio |
|---|---|---|---|
| 1 | P22 | classificado corretamente | processado como V4; 79% das leituras sem gênero (Bray-Curtis 0,99 contra a Paola; 0,02 após correção) |
| 2 | P21 (Espanha) | incluído: 103 controles + 2 HSIL | excluído (primer não publicado) |
| 3 | Amostras com < 1.000 leituras | 26 mantidas (mínimo de 2 leituras), em P19, P10, P9 e P14 | filtradas |
| 4 | P16 | 29 amostras; mediana de 48% Unassigned + Eukaryota por amostra (provável DNA humano) | 47 amostras; Bray-Curtis 0,49 nas 29 em comum. Metadados: 55; artigo: 26 |
| 5 | Profundidade da mesma amostra | referência | P19 2,3×, P14 0,59×, P1 0,72× (demais 0,99–1,04×) |
| 6 | P14 (Brasil) | 13 HSIL / 14 controles | 11 / 11 (artigo: 22 / 21; 16 amostras em nenhuma tabela) |
| 7 | Total de amostras | 997 na tabela, 1.008 no artigo; "Chloroplast" no Boruta mas ausente da tabela | 889 |
| 8 | P14, 21 runs que não são 16S | 5 com 2–4 leituras, 16 ausentes | todas descartadas pelo cutadapt (correto) |
| 9 | Método | DADA2 no texto (pasta tem Deblur), SILVA completo, nível de espécie, sem filtro de profundidade | Deblur por região, classificador por região, gênero, filtro de 1.000 leituras, P10 em dois sublotes |

**21 das 43 runs do P14 não são 16S.** FASTQ baixados do SRA: no sublote bom, 95% das leituras começam com o primer 341F; nas outras 21 (10 controles e 11 HSIL), nenhuma tem primer ou início de V3 e as sequências mais comuns são humanas (Alu, satélite). A exclusão nas duas tabelas é correta, mas precisa constar nos Métodos e a Tabela 1 do artigo (22 HSIL / 21 controles) conta essas runs. **P16:** no sublote principal só ~45% das leituras têm primer; o resto não é 16S e explica os 48% de Unassigned + Eukaryota na tabela da Paola. O sublote de baixa profundidade (26 runs, ~2.000 leituras) é 16S de verdade. Contabilidade completa das 1.042 amostras em `analysis/10_contabilidade_amostras.py`.

Com o mesmo esquema de validação, os resultados das duas tabelas ficam a 0,01–0,03 de AUC um do outro. As diferenças de método mudam pouco; o que muda as conclusões é quais amostras e projetos entram (P21, P16 e amostras de baixa profundidade).

**Pendente:** rodar o classificador SILVA V3-V4 no QIIME 2 sobre as ASVs do P22 reprocessado (a taxonomia atual vem das ASVs V3-V4 já classificadas); registrar que 21 runs do P14 não são 16S (ver abaixo); refazer o GLLVM; decidir a nota metodológica sobre P2/P21 (primer não publicado) e sobre a divergência do P16 entre o TCC de M. T. S. Figueiredo (2025) e o artigo LATINOWARE (26 vs. 55 amostras de câncer); e redigir a seção de metodologia da dissertação com base em todo o processamento realizado. Lista detalhada em "O que falta até o final" na seção 5 do site.
