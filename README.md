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

**Em andamento / bloqueado:**
- Denoising via deblur na região V4 (P2, P9, P10, P16, P22): 469 de 624 amostras retidas (75,2%) até agora. Descoberto que o BioProject P10 mistura dois sublotes, cerca de 154-160 amostras com o primer presente e cerca de 165 já sem primer na origem, exigindo processamento separado (P10a/P10b). A junção final desses dois sublotes no manifest combinado da região está travada por um erro de ID duplicado (`Metadata IDs must be unique`), porque o P10a ainda contém as 165 IDs do sublote sem primer com leituras quase vazias. A correção pendente é excluir essas IDs do P10a antes de combinar com o P10b.

**Pendente:** destravar o P10 e fechar o deblur da região V4; decidir a nota metodológica sobre P2/P21 (primer não publicado) e sobre a divergência do P16 entre o TCC de M. T. S. Figueiredo (2025) e o artigo LATINOWARE (26 vs. 55 amostras de câncer); rodar taxonomia SILVA e filtragem sobre as duas regiões; e, principalmente, as três etapas estatísticas finais, PERMANOVA, GLLVM e a avaliação empírica do protocolo leave-one-project-out com Random Forest, que é a contribuição central declarada como trabalho em andamento no artigo, sobre os dados do próprio pipeline (hoje só há um preview exploratório rodado sobre o `feature-table.txt` da Paola, marcado como não final). Lista detalhada em "O que falta até o final" na seção 5 do site.
