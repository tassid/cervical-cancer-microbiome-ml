# Réplica: microbioma cervicovaginal e câncer cervical

Documento de acompanhamento técnico da replicação da análise descrita em:

> "Validação por projeto em meta-análises de microbioma: um estudo de caso em câncer cervical", LATINOWARE / Latin.Science, 2026.

Segue o mesmo formato do repositório de replicação do Hagen et al. (2024) sobre microbioma do solo e estresse hídrico: um site em React/Vite que documenta o pipeline passo a passo, com glossário interativo e comandos prontos pra copiar.

## Contexto

Etapa preparatória da dissertação de mestrado da autora no PPGTCA/UTFPR, cujo objeto é a classificação de sanidade em soja a partir do microbioma, com validação leave-one-project-out entre múltiplos projetos de origem. O paper-base investiga exatamente esse problema — confundimento entre projeto de origem e condição clínica em dados agregados de microbioma — num dataset de câncer cervical (997 amostras, 10 BioProjects).

## O que o site documenta

- O dataset agregado (Tabela I do paper: 10 BioProjects, 5 países, 4 classes clínicas)
- Um glossário interativo dos conceitos envolvidos (PERMANOVA, GLLVM, efeito de lote, leave-one-project-out, controle negativo, etc.)
- Todos os comandos planejados do pipeline, na ordem em que entram, com botão de copiar
- O status atual da replicação (ainda não iniciada) e os valores publicados no paper, usados como alvo de comparação
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
  App.tsx        — todo o conteúdo e a lógica do documento
  main.tsx       — ponto de entrada React
  index.css      — reset mínimo de estilos
```

## Status

Documento vivo — a seção 4 (comandos) e a seção 5 (status) devem ser atualizadas conforme a replicação avançar de fato.

**Concluído:** confirmação dos primers de amplificação 16S para 8 dos 10 BioProjects, por cruzamento manual do artigo-fonte de cada projeto (Tabela 1b, seção 4). Os outros 2 (P2, P21) foram verificados exaustivamente — artigo principal e material suplementar de ambos — e a sequência do primer nunca foi publicada, pois o sequenciamento foi terceirizado a fornecedores comerciais (Second Genome Inc. e Novogene) que tratam o protocolo como proprietário. Essa ausência está documentada com DOI e citação exata, não é uma lacuna de busca.

**Pendente:** accessions/metadados clínicos por BioProject, download dos FASTQ, corte de primers nos 8 projetos confirmados (comandos prontos na seção 4), decisão sobre incluir ou excluir P2/P21 do dataset agregado, processamento QIIME2 (deblur por região, taxonomia SILVA), PERMANOVA, GLLVM, e por fim a avaliação empírica do protocolo leave-one-project-out com Random Forest. Lista detalhada em "O que falta até o final" na seção 5 do site.
