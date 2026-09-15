import React, { useState, useRef } from "react";
import {
  Copy,
  Check,
  Download,
  Scissors,
  Dna,
  Tag,
  BarChart3,
  Brain,
  ClipboardCheck,
  ListChecks,
  BookOpen,
  GraduationCap,
  Sliders,
  Layers,
  Repeat,
  FolderTree,
  Eye,
  FlaskConical,
  Filter,
  GitBranch,
  Sprout,
} from "lucide-react";

/**
 * Documento de acompanhamento do próprio projeto de pesquisa: validação por
 * projeto em meta-análises de microbioma cervicovaginal / câncer cervical.
 * Artigo próprio: "Validação por projeto em meta-análises de microbioma: um
 * estudo de caso em câncer cervical" (LATINOWARE / Latin.Science, 2026).
 * Visual: artigo acadêmico (estilo LaTeX). Voz: estudante explicando, casual.
 */

type SectionId = "s1" | "s2" | "s3" | "s4" | "s4b" | "s5" | "refs";

const TERMS: Record<string, string> = {
  microbiotaCervicovaginal:
    "O conjunto de micro-organismos (principalmente bactérias) que vive na vagina e no colo do útero. Um perfil dominado por Lactobacillus costuma indicar um ambiente mais protegido; a perda dessa dominância (disbiose) está associada a maior risco de infecções e de persistência viral.",
  disbiose:
    "Um desequilíbrio da comunidade microbiana normal de um lugar do corpo, aqui a perda da dominância de Lactobacillus na vagina, substituída por uma mistura mais diversa de outras bactérias.",
  hpv: "Papilomavírus humano: a infecção persistente por certos tipos de alto risco é a causa necessária (mas não suficiente) do câncer cervical, já que a maioria das mulheres infectadas elimina o vírus sozinha.",
  hsil: "Lesão intraepitelial escamosa de alto grau: uma alteração das células do colo do útero mais avançada que a de baixo grau, com maior chance de evoluir para câncer se não tratada.",
  lsil: "Lesão intraepitelial escamosa de baixo grau: uma alteração inicial e discreta das células do colo do útero, associada à infecção por HPV, que na maioria das vezes regride sozinha.",
  bioproject:
    "Um \"projeto guarda-chuva\" dentro de um banco de dados público (NCBI/SRA ou ENA), onde os cientistas depositam os dados brutos de sequenciamento de uma pesquisa.",
  ena: "European Nucleotide Archive: o repositório público europeu de sequências brutas de DNA, equivalente ao SRA americano.",
  amplicon16s:
    "Um pedacinho específico do DNA que toda bactéria tem (o gene 16S rRNA). Sequenciar só essa parte é a forma mais barata de identificar quais bactérias estão presentes numa amostra, sem sequenciar o genoma inteiro.",
  regiaoV3V4:
    "Uma das sub-regiões variáveis do gene 16S rRNA mais usadas em estudos de microbioma. Estudos diferentes às vezes sequenciam regiões diferentes (V3-V4 ou só V4), o que dificulta comparar diretamente os resultados.",
  deblur:
    "Um dos programas (plugin do QIIME 2) que transforma as leituras brutas de sequenciamento em ASVs, corrigindo erros de leitura e removendo sequências espúrias, de forma parecida com o que o DADA2 faz.",
  asv: "Uma sequência de DNA específica encontrada na amostra, tratada como uma bactéria (ou linhagem) diferente das outras, a unidade básica de contagem em estudos de microbioma modernos.",
  silva:
    "Um grande banco de dados online com sequências de bactérias já identificadas, usado como \"dicionário\" pra dar nome (taxonomia) a cada ASV encontrada.",
  efeitoDeLote:
    "Quando diferenças técnicas entre estudos (equipamento, protocolo de extração, região do gene sequenciada, centro que processou a amostra) se misturam com a diferença biológica de interesse, a ponto de ficar impossível saber qual das duas está sendo medida.",
  confundimento:
    "Quando duas variáveis explicativas (por exemplo, \"projeto de origem\" e \"condição clínica\") variam juntas de um jeito que não dá pra separar o efeito de uma da outra estatisticamente.",
  permanova:
    "Um teste estatístico (PERMANOVA) que verifica se grupos de amostras têm comunidades bacterianas realmente diferentes, sem exigir que os dados sigam uma distribuição específica; funciona bem com dados de microbioma, que costumam ser bem \"tortos\".",
  brayCurtis:
    "Uma forma de medir o quão parecidas (ou diferentes) duas amostras são, olhando pra quais bactérias elas têm em comum e em que proporção. Quanto mais perto de 1, mais diferentes as amostras são.",
  gllvm:
    "Modelo linear generalizado de variáveis latentes: uma alternativa às ordenações baseadas em distância (como NMDS) que modela diretamente a contagem de cada bactéria, e permite incluir covariáveis (como o projeto de origem) dentro do próprio modelo, em vez de só olhar depois.",
  ordenacao:
    "Uma técnica que resume a comunidade bacteriana de cada amostra em um número pequeno de \"eixos\" (geralmente 2), pra dar pra visualizar num gráfico quais amostras são parecidas entre si.",
  aliasing:
    "Quando duas variáveis carregam exatamente a mesma informação estatística (aqui, \"localidade\" e \"projeto de origem\", já que cada projeto vem de um único país), de modo que incluir as duas no modelo não acrescenta nada além de incluir uma só.",
  variancia:
    "O quanto de toda a diferença entre as amostras pode ser \"atribuída\" a um fator específico (condição clínica, localidade, projeto). Mesmo uma porcentagem pequena pode ser estatisticamente significativa, porque o resto da variação vem de todas as outras diferenças naturais entre amostras.",
  pseudoF:
    "O número que o teste PERMANOVA calcula pra medir o quanto os grupos se separam: quanto maior, mais forte é a diferença entre eles. Sozinho não diz muita coisa; o que importa é o p-valor que vem junto.",
  looPo:
    "Leave-one-project-out: um jeito de validar o modelo em que, em vez de misturar tudo aleatoriamente, cada rodada de teste deixa de fora um projeto/estudo inteiro, pra ver se o modelo aprendeu algo que generaliza além do estudo específico onde foi treinado.",
  controleNegativo:
    "Um classificador treinado de propósito para prever algo que NÃO deveria ser aprendível a partir do sinal biológico de interesse (aqui, prever de qual projeto veio a amostra usando só a composição bacteriana). Se ele acerta muito, é sinal de que existe uma assinatura técnica forte nos dados.",
  randomForest:
    "Um tipo de modelo de aprendizado de máquina que combina várias \"árvores de decisão\" simples, tipo uma votação entre várias opiniões, pra chegar numa previsão mais robusta do que uma árvore sozinha.",
  aucMetric:
    "Resume o quão bem um classificador separa dois grupos em todos os limiares de decisão possíveis, não só num ponto de corte fixo. Varia de 0,5 (chute aleatório) a 1,0 (separação perfeita).",
  identificabilidade:
    "Se existe informação suficiente nos dados pra estimar um efeito específico sem ambiguidade. Um contraste clínico só é \"identificável\" dentro de um projeto se esse projeto contiver amostras de mais de uma classe clínica.",
  qiimeView:
    "Um site (view.qiime2.org) que abre os arquivos gerados pelo QIIME 2 (.qza e .qzv) direto no navegador, sem precisar instalar nada nem enviar os dados pra nenhum servidor.",
};

function Term({ id, children }: { id: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const def = TERMS[id];
  return (
    <span className="term-wrap">
      <button
        type="button"
        className="term-trigger"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        {children}
      </button>
      {open && def && (
        <span className="term-pop">
          <span className="term-pop-text">{def}</span>
          <button
            type="button"
            className="term-pop-close"
            onClick={() => setOpen(false)}
            aria-label="fechar"
          >
            ×
          </button>
        </span>
      )}
    </span>
  );
}

interface TocEntry {
  id: SectionId;
  number: string;
  label: string;
  icon: React.ReactNode;
}

const TOC: TocEntry[] = [
  { id: "s1", number: "1", label: "Do que se trata", icon: <Sprout size={14} /> },
  { id: "s2", number: "2", label: "O dataset", icon: <FlaskConical size={14} /> },
  { id: "s3", number: "3", label: "Conceitos que precisam ficar claros", icon: <BookOpen size={14} /> },
  { id: "s4", number: "4", label: "Comandos do pipeline", icon: <ListChecks size={14} /> },
  { id: "s4b", number: "5", label: "Status do projeto", icon: <BarChart3 size={14} /> },
  { id: "s5", number: "6", label: "Por que isso importa pra tese", icon: <GraduationCap size={14} /> },
  { id: "refs", number: "", label: "Referências", icon: <BookOpen size={14} /> },
];

const STEP_ICONS: Record<number, React.ReactNode> = {
  1: <ClipboardCheck size={17} />,
  2: <Download size={17} />,
  3: <Scissors size={17} />,
  4: <Dna size={17} />,
  5: <Tag size={17} />,
  6: <Filter size={17} />,
  7: <BarChart3 size={17} />,
  8: <Eye size={17} />,
  9: <Brain size={17} />,
  10: <GitBranch size={17} />,
};

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const el = document.createElement("textarea");
      el.value = text;
      el.style.position = "fixed";
      el.style.opacity = "0";
      document.body.appendChild(el);
      el.select();
      try {
        document.execCommand("copy");
      } catch {
        /* no-op */
      }
      document.body.removeChild(el);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  return (
    <button className={`copy-btn ${copied ? "copied" : ""}`} onClick={handleCopy}>
      {copied ? <Check size={12} /> : <Copy size={12} />}
      {copied ? "copiado" : "copiar"}
    </button>
  );
}

function Listing({ command }: { command: string }) {
  return (
    <div className="listing-wrap">
      <pre className="listing">
        <code>{command}</code>
      </pre>
      <CopyButton text={command} />
    </div>
  );
}

interface PrimerRow {
  codigo: string;
  regiao: string;
  fwd: string;
  rev: string;
  fonte: string;
  status: "done" | "partial" | "notfound";
  statusLabel: string;
  assumido?: { fwd: string; rev: string; nota: React.ReactNode };
}

const PRIMERS: PrimerRow[] = [
  { codigo: "P1", regiao: "V3-V4", fwd: "ACTCCTACGGGAGGCAGCA", rev: "GGACTACHVGGGTWTCTAAT", fonte: "338F/806R", status: "done", statusLabel: "confirmado" },
  {
    codigo: "P2",
    regiao: "V4",
    fwd: "N/D",
    rev: "N/D",
    fonte:
      "ŁANIEWSKI, P. et al. Sci. Rep. 8:7593, 2018 (artigo + suplementar): sequenciamento terceirizado à Second Genome Inc., \"fusion primers\" sem par nomeado nem sequência publicada",
    status: "notfound",
    statusLabel: "não publicado",
    assumido: {
      fwd: "GTGYCAGCMGCCGCGGTAA",
      rev: "GGACTACNVGGGTWTCTAAT",
      nota: (
        <>
          Suposição documentada, <strong>não confirmada</strong>: par EMP
          515F (Parada, 2016) / 806R (Apprill, 2015), o padrão da comunidade
          já vigente em 2018, mesmo par confirmado para P9/P10/P16 nesta
          tabela. Fonte do protocolo:{" "}
          <a href="https://earthmicrobiome.ucsd.edu/protocols-and-standards/16s/" target="_blank" rel="noreferrer">
            Earth Microbiome Project, 16S Illumina Amplicon Protocol
          </a>
          . O EMP também documenta um par anterior (Caporaso 2011/2012:
          FWD GTGCCAGCMGCCGCGGTAA / REV GGACTACHVGGGTWTCTAAT) que a Second
          Genome pode ter usado em vez do atualizado. Nenhum dos dois é
          citado no artigo do Łaniewski, então a adoção do par EMP
          atualizado é uma convenção de análise, não uma citação do método
          original.
        </>
      ),
    },
  },
  { codigo: "P6", regiao: "V3-V4", fwd: "ACTCCTACGGGAGGCAGCA", rev: "GGACTACHVGGGTWTCTAAT", fonte: "WANG, Z. et al. Microb. Ecol. 84:302-313, 2022, 338F/806R", status: "done", statusLabel: "confirmado" },
  { codigo: "P9", regiao: "V4", fwd: "GTGYCAGCMGCCGCGGTAA", rev: "GGACTACNVGGGTWTCTAAT", fonte: "515F/806R", status: "done", statusLabel: "confirmado" },
  { codigo: "P10", regiao: "V4", fwd: "GTGYCAGCMGCCGCGGTAA", rev: "GGACTACNVGGGTWTCTAAT", fonte: "515F/806R", status: "done", statusLabel: "confirmado" },
  {
    codigo: "P14",
    regiao: "V3-V4",
    fwd: "CCTACGGGNGGCWGCAG",
    rev: "GACTACHVGGGTATCTAATCC",
    fonte: "BRITTO, A. M. A. et al. Front. Immunol., 2023, doi:10.3389/fimmu.2023.1147950, kit \"16S Metagenomic Sequencing Library Preparation\" (Illumina) nomeado explicitamente (341F/805R)",
    status: "done",
    statusLabel: "confirmado",
  },
  { codigo: "P16", regiao: "V4", fwd: "GTGYCAGCMGCCGCGGTAA", rev: "GGACTACNVGGGTWTCTAAT", fonte: "TORTELLI, B. A. et al. JCI Insight 10(6):e176839, 2025, 515F/806R", status: "done", statusLabel: "confirmado" },
  { codigo: "P19", regiao: "V3-V4", fwd: "N/D", rev: "N/D", fonte: "357wF/806R", status: "done", statusLabel: "confirmado" },
  {
    codigo: "P21",
    regiao: "V3-V4",
    fwd: "N/D",
    rev: "N/D",
    fonte:
      "ROSAS CANCIO-SUÁREZ, M. et al. Front. Med. 12:1615571, 2025 (texto completo): sequenciamento terceirizado à Novogene, região confirmada, par de primers não nomeado nem publicado",
    status: "notfound",
    statusLabel: "não publicado",
  },
  {
    codigo: "P22",
    regiao: "V3-V4",
    fwd: "CCTAYGGGRBGCASCAG",
    rev: "GGACTACNNGGGTATCTAAT",
    fonte: "FAN, Q. et al. Cell Death Dis. 12(12):1094, 2021, doi:10.1038/s41419-021-04388-y, 341F/806R, BioProject citado explicitamente",
    status: "done",
    statusLabel: "confirmado",
  },
];

function PrimerTable() {
  return (
    <table className="formal">
      <caption>
        <span className="cap-label">Tabela 1b.</span> Confirmação de primers por
        BioProject (8 de 10 confirmados com sequência exata; 2 documentados como
        não publicados após verificação exaustiva de artigo principal e material
        suplementar).
      </caption>
      <thead>
        <tr>
          <th>Cód.</th>
          <th>Região</th>
          <th>Forward</th>
          <th>Reverse</th>
          <th>Fonte / observação</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {PRIMERS.map((p) => (
          <React.Fragment key={p.codigo}>
            <tr>
              <td>{p.codigo}</td>
              <td>{p.regiao}</td>
              <td style={{ fontFamily: "var(--mono-font, monospace)", fontSize: 12 }}>{p.fwd}</td>
              <td style={{ fontFamily: "var(--mono-font, monospace)", fontSize: 12 }}>{p.rev}</td>
              <td style={{ fontSize: 12.5 }}>{p.fonte}</td>
              <td>
                <span className={`status-badge ${p.status}`}>{p.statusLabel}</span>
              </td>
            </tr>
            {p.assumido && (
              <tr style={{ background: "rgba(0,0,0,0.02)" }}>
                <td colSpan={2} style={{ fontSize: 11.5, fontStyle: "italic", color: "var(--ink-soft)" }}>
                  ↳ se assumido
                </td>
                <td style={{ fontFamily: "var(--mono-font, monospace)", fontSize: 12 }}>{p.assumido.fwd}</td>
                <td style={{ fontFamily: "var(--mono-font, monospace)", fontSize: 12 }}>{p.assumido.rev}</td>
                <td colSpan={2} style={{ fontSize: 12, fontStyle: "italic" }}>
                  {p.assumido.nota}
                </td>
              </tr>
            )}
          </React.Fragment>
        ))}
      </tbody>
    </table>
  );
}

type CommandEntry = string | { code: string; caption: React.ReactNode };

interface Step {
  n: number;
  title: string;
  note: React.ReactNode;
  commands: CommandEntry[];
}

const STEPS: Step[] = [
  {
    n: 1,
    title: "Levantar accessions e metadados clínicos",
    note: (
      <>
        <p style={{ marginTop: 0 }}>
          <strong>Concluído.</strong> O mapeamento entre cada Run/Sample e a
          classe clínica (câncer, <Term id="hsil">HSIL</Term>,{" "}
          <Term id="lsil">LSIL</Term> ou controle) para as 1.042 amostras
          catalogadas já existe: o arquivo <code>metadata.txt</code>,
          compartilhado pela coautora Paola Gyuliane Gonçalves (pasta{" "}
          <em>Cancer Cervical</em> no Google Drive do grupo). O arquivo traz,
          por Run: accession de amostra, classe clínica (
          <code>tipo_amostra</code>), status de HPV, centro de origem, país e
          código do projeto (P1–P22).
        </p>
        <p>
          A contagem por projeto e por classe extraída desse arquivo bate,
          célula a célula, com a Tabela I do artigo, incluindo o total de
          1.042 amostras (314 CC + 170 HSIL + 112 LSIL + 446 Ctrl). Isso
          confirma que <code>metadata.txt</code> é de fato a fonte usada para
          montar a Tabela I, não uma reconstrução aproximada.
        </p>
        <p style={{ fontSize: 13.5 }}>
          Nota: o P16 registra 55 amostras de câncer neste arquivo, contra 26
          numa versão anterior do mesmo agregado (TCC de M. T. S. Figueiredo,
          2025, referência [16] do artigo), provavelmente uma atualização do
          BioProject entre os dois trabalhos. Vale documentar essa diferença
          como nota metodológica caso apareça alguma discrepância downstream.
        </p>
        <p style={{ fontSize: 13.5 }}>
          Também foi localizado, na mesma pasta, um <code>feature-table.txt</code>{" "}
          com contagens de ASV/OTU já anotadas por taxonomia, a confirmar se
          corresponde à tabela final pós-filtragem (997 amostras) ou a uma
          etapa intermediária, o que pode adiantar as Etapas 3–6 abaixo.
        </p>
      </>
    ),
    commands: [
      {
        code: `# metadata.txt, colunas: #NAME (run);sample_accession;tipo_amostra;HPV;Center;Location;Project
# 1042 linhas (1041 amostras + cabecalho), delimitador ";"
# Contagem por projeto e classe clinica, conferida nesta sessao:
#   P1  : cancer=68 control=4
#   P2  : cancer=10 lesion_high=27 lesion_low=11 control=29
#   P6  : cancer=26
#   P9  : cancer=58
#   P10 : cancer=1 lesion_high=59 lesion_low=43 control=216
#   P14 : lesion_high=22 control=21
#   P16 : cancer=55
#   P19 : cancer=31 lesion_high=60 lesion_low=58 control=19
#   P21 : lesion_high=2 control=103
#   P22 : cancer=65 control=54
#   TOTAL: cancer=314 lesion_high=170 lesion_low=112 control=446 (1042)`,
        caption:
          "Bate exatamente com a Tabela I do artigo, a Etapa 1 está fechada para os 10 projetos.",
      },
      `# Próximo passo real: confirmar se feature-table.txt já corresponde
# a uma etapa processada (deblur + taxonomia) reaproveitável, ou se
# é preciso reprocessar do FASTQ bruto com os primers da Tabela 1b.`,
    ],
  },
  {
    n: 2,
    title: "Baixar os FASTQ brutos",
    note: (
      <>
        Um projeto por vez, usando o SRA Toolkit, organizando o resultado por
        código de projeto (P1..P22) pra manter rastreável de onde cada
        amostra veio, importante porque a região do gene sequenciada (
        <Term id="regiaoV3V4">V3-V4</Term> ou V4) muda de um projeto pro
        outro, e isso condiciona toda a etapa seguinte.
      </>
    ),
    commands: [
      `mkdir -p raw/P1 && cd raw/P1
prefetch --option-file ../../accessions/P1_runs.txt
fasterq-dump --split-files --threads 4 SRR*/*.sra
gzip *.fastq
cd ../..`,
    ],
  },
  {
    n: 3,
    title: "Importar e remover primers",
    note: (
      <>
        <p style={{ marginTop: 0 }}>
          Importar cada projeto no QIIME 2 e cortar os <em>primers</em> com o
          plugin cutadapt, separando os lotes por região amplificada (V3-V4 /
          V4) e, dentro de cada região, pelo par de primer exato usado no
          estudo original, que não é o mesmo em todos os projetos, mesmo
          quando a região nominal é a mesma.
        </p>
        <p>
          <strong>Atualização:</strong> os primers de 8 dos 10 BioProjects
          foram confirmados por sequência exata, cruzando cada artigo-fonte
          individualmente (ver Tabela 1b). Dos 2 restantes, o <strong>P2</strong>{" "}
          tem uma suposição documentada (par EMP 515F/806R, não confirmada,
          ver nota na Tabela 1b) que pode ser usada opcionalmente com o
          artefato marcado como tal; o <strong>P21</strong> segue sem
          nenhuma suposição plausível e entra como <code>SKIP</code>{" "}
          documentado. Em ambos os casos o sequenciamento foi terceirizado a
          fornecedores comerciais (Second Genome Inc. e Novogene) que não
          publicam a sequência do primer nem no artigo principal nem no
          material suplementar, verificado exaustivamente nos dois casos.
        </p>
        <PrimerTable />
      </>
    ),
    commands: [
      `qiime tools import \\
  --type 'SampleData[PairedEndSequencesWithQuality]' \\
  --input-path manifest_P1.csv \\
  --input-format PairedEndFastqManifestPhred33V2 \\
  --output-path P1_demux.qza`,
      {
        code: `# Grupo 338F/806R (V3-V4): P1, P6
qiime cutadapt trim-paired \\
  --i-demultiplexed-sequences P1_demux.qza \\
  --p-front-f ACTCCTACGGGAGGCAGCA \\
  --p-front-r GGACTACHVGGGTWTCTAAT \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences P1_trimmed.qza`,
        caption: "Repetir para P6 trocando apenas o artefato de entrada/saída.",
      },
      {
        code: `# Grupo 515F/806R (V4): P9, P10, P16
qiime cutadapt trim-paired \\
  --i-demultiplexed-sequences P9_demux.qza \\
  --p-front-f GTGYCAGCMGCCGCGGTAA \\
  --p-front-r GGACTACNVGGGTWTCTAAT \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences P9_trimmed.qza`,
        caption: "Repetir para P10 e P16.",
      },
      `# 341F/805R (V3-V4), via kit Illumina, P14
qiime cutadapt trim-paired \\
  --i-demultiplexed-sequences P14_demux.qza \\
  --p-front-f CCTACGGGNGGCWGCAG \\
  --p-front-r GACTACHVGGGTATCTAATCC \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences P14_trimmed.qza`,
      `# 357wF/806R (V3-V4), P19
qiime cutadapt trim-single \\
  --i-demultiplexed-sequences P19_demux.qza \\
  --p-front CTCCTACGGGAGGCAGCAG \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences P19_trimmed.qza`,
      `# 341F/806R (V3-V4), sequência específica do estudo, P22
qiime cutadapt trim-paired \\
  --i-demultiplexed-sequences P22_demux.qza \\
  --p-front-f CCTAYGGGRBGCASCAG \\
  --p-front-r GGACTACNNGGGTATCTAAT \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences P22_trimmed.qza`,
      {
        code: `# P2 (V4): sem primer publicado. Se optar por rodar com a suposição
# documentada (par EMP 515F Parada / 806R Apprill, NAO confirmado):
qiime cutadapt trim-paired \\
  --i-demultiplexed-sequences P2_demux.qza \\
  --p-front-f GTGYCAGCMGCCGCGGTAA \\
  --p-front-r GGACTACNVGGGTWTCTAAT \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences P2_trimmed_ASSUMIDO.qza`,
        caption:
          "Marcar o artefato de saída como resultado de suposição (sufixo _ASSUMIDO), não como dado confirmado, ver Tabela 1b.",
      },
      {
        code: `# P21: nenhuma suposição documentada até agora, SKIP
echo "P21 excluido do corte de primer: sequencia proprietaria (Novogene), sem par de referencia plausivel identificado" \\
  >> primers_skip.log`,
        caption:
          "Decisão em aberto: excluir P21 do dataset agregado, ou manter e documentar a limitação no texto final.",
      },
    ],
  },
  {
    n: 4,
    title: "Denoising com deblur (por região)",
    note: (
      <>
        O paper original usa o plugin <Term id="deblur">q2-deblur</Term> do
        QIIME 2 2023.2 pra gerar as <Term id="asv">ASVs</Term>. Cada região
        (V3-V4 e V4) precisa de um lote de deblur separado, com seu próprio
        comprimento de corte, porque não dá pra comparar ASVs de regiões
        diferentes diretamente.
      </>
    ),
    commands: [
      `qiime deblur denoise-16S \\
  --i-demultiplexed-seqs V3V4_trimmed_merged.qza \\
  --p-trim-length 250 \\
  --p-sample-stats \\
  --o-representative-sequences V3V4_repseqs.qza \\
  --o-table V3V4_table.qza \\
  --o-stats V3V4_stats.qza`,
    ],
  },
  {
    n: 5,
    title: "Atribuição taxonômica (SILVA)",
    note: (
      <>
        Classificar as sequências representativas contra o banco{" "}
        <Term id="silva">SILVA</Term>, pra dar nome (taxonomia) a cada ASV.
        É essa taxonomia, não o ASV bruto, que depois permite unir as
        tabelas das duas regiões num único conjunto agregado.
      </>
    ),
    commands: [
      `qiime feature-classifier classify-sklearn \\
  --i-classifier silva-138-99-nb-classifier.qza \\
  --i-reads V3V4_repseqs.qza \\
  --o-classification V3V4_taxonomy.qza`,
    ],
  },
  {
    n: 6,
    title: "Filtragem",
    note: (
      <>
        Remover cloroplasto, mitocôndria, arqueia e singletons, depois
        filtrar amostras com profundidade insuficiente. A meta é bater com
        as <strong>997 amostras finais</strong> reportadas no paper (de 1.042
        catalogadas na Tabela I). É o número que valida se a filtragem ficou
        equivalente à do estudo original.
      </>
    ),
    commands: [
      `qiime taxa filter-table \\
  --i-table table.qza \\
  --i-taxonomy taxonomy.qza \\
  --p-exclude mitochondria,chloroplast,archaea \\
  --o-filtered-table table_filtered.qza`,
      `qiime feature-table filter-features \\
  --i-table table_filtered.qza \\
  --p-min-frequency 2 \\
  --o-filtered-table table_no_singletons.qza`,
      `qiime feature-table filter-samples \\
  --i-table table_no_singletons.qza \\
  --p-min-frequency 1000 \\
  --o-filtered-table table_final.qza`,
    ],
  },
  {
    n: 7,
    title: "Partição de variância (PERMANOVA)",
    note: (
      <>
        Rodar <Term id="permanova">PERMANOVA</Term> sobre dissimilaridade de{" "}
        <Term id="brayCurtis">Bray-Curtis</Term>, com condição clínica,
        localidade e projeto como termos, e depois os contrastes par a par
        entre condições clínicas isoladamente.
      </>
    ),
    commands: [
      `library(vegan)

bc_dist <- vegdist(otu_table, method = "bray")
modelo <- adonis2(bc_dist ~ condicao + localidade + projeto,
                   data = metadata, permutations = 999)
print(modelo)`,
      {
        code: `pares <- combn(levels(metadata$condicao), 2, simplify = FALSE)
for (p in pares) {
  sub_idx <- metadata$condicao %in% p
  sub_dist <- as.dist(as.matrix(bc_dist)[sub_idx, sub_idx])
  print(adonis2(sub_dist ~ condicao, data = metadata[sub_idx, ], permutations = 999))
}`,
        caption:
          "Alvo de comparação (valores publicados): condição+localidade+projeto ≈ 13,5% da variação (F ≈ 12,8; p = 0,001); controle vs. câncer ≈ 5,0%.",
      },
    ],
  },
  {
    n: 8,
    title: "Ordenação por variáveis latentes (GLLVM)",
    note: (
      <>
        Ajustar um modelo <Term id="gllvm">GLLVM</Term> em duas configurações,
        sem covariáveis e com o projeto como efeito fixo, pra comparar se
        o eixo dominante de variação separa condição clínica ou projeto de
        origem.
      </>
    ),
    commands: [
      `library(gllvm)

modelo_gllvm_0 <- gllvm(otu_table, family = "negative.binomial", num.lv = 2)

modelo_gllvm_1 <- gllvm(otu_table, X = metadata["projeto"],
                         formula = ~ projeto,
                         family = "negative.binomial", num.lv = 2)

ordiplot(modelo_gllvm_0, biplot = FALSE)`,
    ],
  },
  {
    n: 9,
    title: "Protocolo de validação (Random Forest)",
    note: (
      <>
        A parte que o paper ainda deixa como trabalho em curso: comparar CV
        estratificada aleatória contra <Term id="looPo">leave-one-project-out</Term>{" "}
        com Random Forest, mais um <Term id="controleNegativo">controle negativo</Term>{" "}
        prevendo o projeto de origem a partir da composição.
      </>
    ),
    commands: [
      {
        code: `library(ranger)
library(caret)

# Esquema 1: CV estratificada aleatória
folds_random <- createFolds(metadata$condicao, k = 10)

# Esquema 2: leave-one-project-out
projetos <- unique(metadata$projeto)
auc_lopo <- sapply(projetos, function(p) {
  treino <- metadata$projeto != p
  teste  <- metadata$projeto == p
  if (length(unique(metadata$condicao[teste])) < 2) return(NA)
  rf <- ranger(condicao ~ ., data = otu_table[treino, ], probability = TRUE)
  predict(rf, otu_table[teste, ])$predictions
})

# Controle negativo: prever o projeto a partir da composição
rf_projeto <- ranger(projeto ~ ., data = otu_table, probability = TRUE)`,
        caption:
          "Restringir o contraste de 4 classes aos projetos com poder real (P2 e P19); P6, P9 e P16 são monoclasse e ficam de fora dessa parte.",
      },
    ],
  },
];

export default function App() {
  const [, setActive] = useState<SectionId>("s1");
  const refs = useRef<Partial<Record<SectionId, HTMLElement | null>>>({});

  const scrollTo = (id: SectionId) => {
    setActive(id);
    refs.current[id]?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="doc">
      <style>{`
        :root {
          --paper: #fbfaf7;
          --ink: #1a1a1a;
          --ink-soft: #55534a;
          --rule: #1a1a1a;
          --rule-light: #cdc7b6;
          --mono-bg: #14130f;
          --mono-text: #d9e9c8;
          --font-serif: "Latin Modern Roman", "CMU Serif", "STIX Two Text", "Georgia", "Times New Roman", serif;
          --font-mono: "Latin Modern Mono", "CMU Typewriter Text", "Courier New", monospace;
        }
        * { box-sizing: border-box; }
        .doc {
          background: var(--paper);
          color: var(--ink);
          font-family: var(--font-serif);
          min-height: 100vh;
        }
        .grid {
          display: grid;
          grid-template-columns: 220px minmax(0, 1fr);
          max-width: 1060px;
          margin: 0 auto;
        }
        @media (max-width: 820px) {
          .grid { grid-template-columns: 1fr; }
          .toc { position: static !important; border-right: none !important; border-bottom: 1px solid var(--rule-light); }
        }

        .toc {
          position: sticky;
          top: 0;
          align-self: start;
          height: 100vh;
          overflow-y: auto;
          border-right: 1px solid var(--rule-light);
          padding: 60px 22px 24px;
        }
        .toc-heading {
          font-variant: small-caps;
          letter-spacing: 0.04em;
          font-size: 12px;
          color: var(--ink-soft);
          margin-bottom: 12px;
          border-bottom: 1px solid var(--rule-light);
          padding-bottom: 8px;
        }
        .toc-item {
          display: flex;
          align-items: center;
          gap: 7px;
          width: 100%;
          text-align: left;
          background: none;
          border: none;
          font-family: var(--font-serif);
          color: var(--ink);
          font-size: 13px;
          padding: 5px 0;
          cursor: pointer;
        }
        .toc-item:hover { text-decoration: underline; }
        .toc-item svg { flex-shrink: 0; opacity: 0.7; }
        .toc-num { display: inline-block; width: 18px; color: var(--ink-soft); }

        .paper { padding: 60px 68px 130px; }
        @media (max-width: 820px) { .paper { padding: 44px 24px 100px; } }

        .masthead {
          text-align: center;
          border-bottom: 1px double var(--rule);
          padding-bottom: 26px;
          margin-bottom: 40px;
        }
        .doc-title { font-size: 24px; font-weight: 700; line-height: 1.35; margin: 0 0 12px; }
        .doc-authors { font-size: 14.5px; margin-bottom: 4px; }
        .doc-affil { font-size: 12.5px; color: var(--ink-soft); font-style: italic; }
        .doc-note { font-size: 12px; color: var(--ink-soft); margin-top: 10px; }
        .quick-links { margin-top: 14px; display: flex; gap: 14px; justify-content: center; }
        .quick-link {
          font-size: 12.5px;
          color: var(--ink);
          border: 1px solid var(--rule-light);
          padding: 4px 12px;
          border-radius: 3px;
          text-decoration: none;
        }
        .quick-link:hover { background: var(--rule-light); }

        .abstract {
          background: #f3f1ea;
          border: 1px solid var(--rule-light);
          padding: 20px 24px;
          margin-bottom: 44px;
          font-size: 14px;
          line-height: 1.65;
        }
        .abstract-heading {
          font-variant: small-caps;
          font-weight: 700;
          margin-bottom: 8px;
          font-size: 13px;
        }

        p { line-height: 1.75; font-size: 15px; margin: 0 0 16px; }
        section { margin-bottom: 46px; }
        .sec { font-size: 18px; border-bottom: 1px solid var(--rule-light); padding-bottom: 8px; margin-bottom: 18px; }
        .sec-num { margin-right: 8px; color: var(--ink-soft); }
        em { font-style: italic; }
        strong { font-weight: 700; }

        .term-wrap { position: relative; display: inline; }
        .term-trigger {
          background: none;
          border: none;
          padding: 0;
          font: inherit;
          color: inherit;
          border-bottom: 1px dotted var(--ink-soft);
          cursor: pointer;
        }
        .term-name { font-weight: 700; }
        .term-pop {
          position: absolute;
          left: 0;
          top: 100%;
          margin-top: 6px;
          z-index: 20;
          background: #fff;
          border: 1px solid var(--rule);
          box-shadow: 3px 3px 0 var(--rule-light);
          padding: 12px 32px 12px 14px;
          width: min(320px, 80vw);
          font-size: 13px;
          line-height: 1.55;
          color: var(--ink);
        }
        .term-pop-close {
          position: absolute;
          top: 6px;
          right: 8px;
          background: none;
          border: none;
          font-size: 16px;
          line-height: 1;
          cursor: pointer;
          color: var(--ink-soft);
        }

        table.formal { width: 100%; border-collapse: collapse; margin: 18px 0 4px; font-size: 13.5px; }
        table.formal caption { text-align: left; font-size: 13px; margin-bottom: 8px; }
        .cap-label { font-weight: 700; margin-right: 4px; }
        table.formal th, table.formal td { padding: 6px 10px; border-bottom: 1px solid var(--rule-light); text-align: left; }
        table.formal thead th { border-top: 1.5px solid var(--rule); border-bottom: 1.5px solid var(--rule); font-variant: small-caps; }
        table.formal tbody tr:last-child td { border-bottom: 1.5px solid var(--rule); }
        .table-caption-below { font-size: 11.5px; color: var(--ink-soft); margin-bottom: 24px; }

        .term-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
        .term-list li { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; line-height: 1.6; }
        .concept-icon { color: var(--ink-soft); margin-top: 2px; flex-shrink: 0; }
        .concept-text { flex: 1; }

        .flow-diagram {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 4px;
          margin: 18px 0 26px;
          padding: 14px;
          background: #f3f1ea;
          border: 1px solid var(--rule-light);
        }
        .flow-node { display: flex; flex-direction: column; align-items: center; gap: 2px; color: var(--ink-soft); }
        .flow-n { font-size: 10px; }
        .flow-arrow { color: var(--rule-light); font-size: 13px; }

        .task-row { margin-bottom: 30px; }
        .task-head { margin-bottom: 6px; }
        .task-title { font-size: 15.5px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
        .step-icon { color: var(--ink-soft); display: inline-flex; }
        .task-note { font-size: 14px; }
        .cmd-caption { font-size: 12.5px; color: var(--ink-soft); margin-top: -8px; margin-bottom: 18px; }

        .listing-wrap { position: relative; margin-bottom: 10px; }
        .listing {
          background: var(--mono-bg);
          color: var(--mono-text);
          font-family: var(--font-mono);
          font-size: 12.5px;
          line-height: 1.55;
          padding: 14px 16px;
          border-radius: 4px;
          overflow-x: auto;
          margin: 0;
          white-space: pre;
        }
        .copy-btn {
          position: absolute;
          top: 8px;
          right: 8px;
          display: flex;
          align-items: center;
          gap: 4px;
          background: rgba(255,255,255,0.08);
          color: var(--mono-text);
          border: 1px solid rgba(255,255,255,0.2);
          border-radius: 3px;
          font-size: 11px;
          padding: 3px 8px;
          cursor: pointer;
        }
        .copy-btn:hover { background: rgba(255,255,255,0.16); }
        .copy-btn.copied { background: rgba(120,200,120,0.25); }

        .status-badge {
          display: inline-block;
          font-size: 11px;
          font-variant: small-caps;
          padding: 2px 8px;
          border-radius: 3px;
          border: 1px solid var(--rule-light);
          color: var(--ink-soft);
        }
        .status-badge.pending { background: #f3f1ea; }
        .status-badge.blocked { background: #f0e3d8; }
        .status-badge.done { background: #e1ead8; }
        .status-badge.partial { background: #ece0c8; }
        .status-badge.notfound { background: #ecdcdc; }

        .refs { padding-left: 20px; font-size: 13.5px; line-height: 1.7; }
        .refs li { margin-bottom: 10px; }

        .footnote { font-size: 12px; color: var(--ink-soft); border-top: 1px solid var(--rule-light); padding-top: 16px; margin-top: 40px; }
        .pagefoot { text-align: center; font-size: 11.5px; color: var(--ink-soft); padding: 20px; }
      `}</style>

      <div className="grid">
        <nav className="toc">
          <div className="toc-heading">Sumário</div>
          {TOC.map((t) => (
            <button key={t.id} className="toc-item" onClick={() => scrollTo(t.id)}>
              {t.icon}
              <span className="toc-num">{t.number}</span>
              {t.label}
            </button>
          ))}
        </nav>

        <main className="paper">
          <div className="masthead">
            <div className="doc-title">
              Validação por projeto em meta-análises de microbioma
              cervicovaginal e câncer cervical
            </div>
            <div className="doc-authors">Tassiane Anzolin</div>
            <div className="doc-affil">
              PPGTCA, Universidade Tecnológica Federal do Paraná
            </div>
            <div className="doc-note">caderno de acompanhamento do próprio projeto de pesquisa, atualizado conforme o trabalho avança</div>
          </div>

          <div className="abstract">
            <div className="abstract-heading">Resumo</div>
            <p style={{ marginBottom: 0 }}>
              Este caderno acompanha o andamento do próprio artigo,
              "Validação por projeto em meta-análises de microbioma: um
              estudo de caso em câncer cervical", que reanalisa 997 amostras
              cervicovaginais agregadas de dez BioProjects públicos e mostra
              que o efeito de projeto/lote domina a variação composicional,
              mascarando o sinal clínico. O artigo, apresentado como trabalho
              em andamento, deixou em aberto a avaliação empírica do
              protocolo de validação leave-one-project-out proposto. É essa
              etapa que este caderno documenta a partir daqui. O mesmo
              problema de confundimento entre projeto de origem e condição
              biológica é o cerne da dissertação, aplicado à soja.
            </p>
          </div>

          {/* 1 */}
          <section id="s1" ref={(el) => { refs.current["s1"] = el; }}>
            <h2 className="sec"><span className="sec-num">1.</span>Do que se trata</h2>
            <p>
              A pergunta de fundo é conhecida: a{" "}
              <Term id="microbiotaCervicovaginal">microbiota cervicovaginal</Term>{" "}
              muda conforme a progressão do câncer do colo do útero? A
              dominância por Lactobacillus protege, e sua perda (
              <Term id="disbiose">disbiose</Term>) está ligada a maior
              suscetibilidade à persistência do{" "}
              <Term id="hpv">HPV</Term>. Verificar isso exige um tamanho
              amostral que raramente existe num único estudo, o que torna
              atraente agregar dados de repositórios públicos.
            </p>
            <p>
              O artigo, publicado no LATINOWARE/Latin.Science, não tenta
              maximizar acurácia de classificação, ele investiga um problema
              anterior: quando se agregam dez estudos diferentes, cada um com
              seu próprio protocolo, região de sequenciamento e composição de
              classes, o efeito técnico entre estudos (<Term id="efeitoDeLote">efeito de lote</Term>)
              pode ficar indistinguível do sinal biológico de interesse. A
              conclusão central: o eixo dominante de variação nesse conjunto
              agregado separa <em>estudos</em>, não condições clínicas, e por
              isso o artigo propõe um protocolo de validação por{" "}
              <Term id="looPo">exclusão de um projeto por vez</Term> pra
              classificadores treinados sobre esse tipo de dado.
            </p>
            <p>
              O artigo foi submetido como trabalho em andamento, com a
              avaliação empírica desse protocolo declarada como próxima
              etapa. É essa etapa, treinar Random Forest sob os dois
              esquemas de validação e medir a diferença, que este caderno
              acompanha agora. O motivo de documentar isso passo a passo é o
              mesmo que levou a autora a montar um caderno equivalente pro
              exercício de réplica do Hagen et al. (solo e seca): a
              dissertação vai lidar com exatamente esse mesmo problema:
              combinar múltiplos projetos de soja, então faz sentido deixar
              o pipeline e o diagnóstico de confundimento bem documentados
              num projeto próprio antes de aplicar o mesmo raciocínio a
              um dado que ninguém nunca processou.
            </p>
          </section>

          {/* 2 */}
          <section id="s2" ref={(el) => { refs.current["s2"] = el; }}>
            <h2 className="sec"><span className="sec-num">2.</span>O dataset</h2>
            <p>
              Dez <Term id="bioproject">BioProjects</Term> públicos (NCBI e{" "}
              <Term id="ena">ENA</Term>), cinco países, cobrindo controles
              saudáveis, <Term id="lsil">LSIL</Term>, <Term id="hsil">HSIL</Term>{" "}
              e câncer cervical (CC). Todos processados a partir de{" "}
              <Term id="amplicon16s">amplicon 16S</Term> em plataforma
              Illumina.
            </p>
            <table className="formal">
              <caption><span className="cap-label">Tabela 1.</span> Composição do conjunto de dados agregado (Tabela I do artigo).</caption>
              <thead>
                <tr><th>Cód.</th><th>BioProject</th><th>País</th><th>Região</th><th>CC</th><th>HSIL</th><th>LSIL</th><th>Ctrl</th><th>Total</th></tr>
              </thead>
              <tbody>
                <tr><td>P1</td><td>PRJNA687644</td><td>China</td><td>V3-V4</td><td>68</td><td>0</td><td>0</td><td>4</td><td>72</td></tr>
                <tr><td>P2</td><td>PRJNA518153</td><td>EUA</td><td>V4</td><td>10</td><td>27</td><td>11</td><td>29</td><td>77</td></tr>
                <tr><td>P6</td><td>PRJNA687331</td><td>China</td><td>V3-V4</td><td>26</td><td>0</td><td>0</td><td>0</td><td>26</td></tr>
                <tr><td>P9</td><td>PRJNA431248</td><td>EUA</td><td>V4</td><td>58</td><td>0</td><td>0</td><td>0</td><td>58</td></tr>
                <tr><td>P10</td><td>PRJEB51893</td><td>EUA</td><td>V4</td><td>1</td><td>59</td><td>43</td><td>216</td><td>319</td></tr>
                <tr><td>P14</td><td>PRJNA933917</td><td>Brasil</td><td>V3-V4</td><td>0</td><td>22</td><td>0</td><td>21</td><td>43</td></tr>
                <tr><td>P16</td><td>PRJNA1029035</td><td>EUA</td><td>V4</td><td>55</td><td>0</td><td>0</td><td>0</td><td>55</td></tr>
                <tr><td>P19</td><td>PRJNA914231</td><td>Nigéria</td><td>V3-V4</td><td>31</td><td>60</td><td>58</td><td>19</td><td>168</td></tr>
                <tr><td>P21</td><td>PRJEB83336</td><td>Espanha</td><td>V3-V4</td><td>0</td><td>2</td><td>0</td><td>103</td><td>105</td></tr>
                <tr><td>P22</td><td>PRJNA725946</td><td>China</td><td>V3-V4</td><td>65</td><td>0</td><td>0</td><td>54</td><td>119</td></tr>
                <tr><td><strong>Total</strong></td><td /><td /><td /><td><strong>314</strong></td><td><strong>170</strong></td><td><strong>112</strong></td><td><strong>446</strong></td><td><strong>1042</strong></td></tr>
              </tbody>
            </table>
            <div className="table-caption-below">
              CC: câncer cervical · HSIL: lesão de alto grau · LSIL: lesão de baixo grau · Ctrl: controle.
              Contagens antes da filtragem de qualidade (após: 997 amostras).
            </div>
            <p>
              Três características desta tabela condicionam o pipeline
              inteiro: a região sequenciada alterna entre{" "}
              <Term id="regiaoV3V4">V3-V4</Term> e V4 (não dá pra rodar um
              denoising único pra tudo); a distribuição de classes é
              fortemente desbalanceada dentro de cada projeto (P6, P9 e P16
              são monoclasse, só câncer); e cada estudo vem de um único
              centro e de um único país, o que faz a <em>localidade</em>{" "}
              ficar totalmente <Term id="aliasing">aliasada</Term> ao{" "}
              <em>projeto</em>.
            </p>
          </section>

          {/* 3 */}
          <section id="s3" ref={(el) => { refs.current["s3"] = el; }}>
            <h2 className="sec"><span className="sec-num">3.</span>Conceitos que precisam ficar claros</h2>
            <p>
              Clique em cada termo abaixo pra ver a explicação em linguagem
              simples.
            </p>
            <ul className="term-list">
              <li>
                <span className="concept-icon"><Dna size={16} /></span>
                <span className="concept-text">
                  <Term id="asv"><span className="term-name">ASV</span></Term>{": "}
                  variante de sequência que representa uma bactéria
                  específica encontrada na amostra.
                </span>
              </li>
              <li>
                <span className="concept-icon"><Sliders size={16} /></span>
                <span className="concept-text">
                  <Term id="deblur"><span className="term-name">deblur</span></Term>{": "}
                  o plugin do QIIME 2 usado neste paper (em vez do DADA2) pra
                  gerar as ASVs a partir das leituras brutas.
                </span>
              </li>
              <li>
                <span className="concept-icon"><Layers size={16} /></span>
                <span className="concept-text">
                  <Term id="efeitoDeLote"><span className="term-name">Efeito de lote</span></Term>{" "}
                  e{" "}
                  <Term id="confundimento"><span className="term-name">confundimento</span></Term>{": "}
                  quando diferença técnica entre estudos se mistura com a
                  diferença biológica de interesse.
                </span>
              </li>
              <li>
                <span className="concept-icon"><BarChart3 size={16} /></span>
                <span className="concept-text">
                  <Term id="permanova"><span className="term-name">PERMANOVA</span></Term>{" "}
                  sobre{" "}
                  <Term id="brayCurtis"><span className="term-name">Bray-Curtis</span></Term>{": "}
                  o teste usado pra particionar quanto da variação vem de
                  cada fator (condição, localidade, projeto).
                </span>
              </li>
              <li>
                <span className="concept-icon"><FolderTree size={16} /></span>
                <span className="concept-text">
                  <Term id="gllvm"><span className="term-name">GLLVM</span></Term>{": "}
                  a ordenação baseada em modelo usada como alternativa à
                  ordenação baseada em distância, permitindo incluir o
                  projeto como covariável.
                </span>
              </li>
              <li>
                <span className="concept-icon"><Repeat size={16} /></span>
                <span className="concept-text">
                  <Term id="looPo"><span className="term-name">Leave-one-project-out</span></Term>{": "}
                  a validação que deixa um projeto inteiro de fora do teste
                  por vez, o protocolo que o paper propõe e que a
                  dissertação também pretende usar.
                </span>
              </li>
              <li>
                <span className="concept-icon"><Brain size={16} /></span>
                <span className="concept-text">
                  <Term id="controleNegativo"><span className="term-name">Controle negativo</span></Term>{": "}
                  treinar um classificador pra prever o projeto de origem a
                  partir da composição bacteriana, como diagnóstico de
                  assinatura técnica.
                </span>
              </li>
              <li>
                <span className="concept-icon"><Tag size={16} /></span>
                <span className="concept-text">
                  <Term id="silva"><span className="term-name">SILVA</span></Term>{": "}
                  o banco de dados usado como dicionário pra dar taxonomia a
                  cada ASV.
                </span>
              </li>
              <li>
                <span className="concept-icon"><Eye size={16} /></span>
                <span className="concept-text">
                  <Term id="identificabilidade"><span className="term-name">Identificabilidade</span></Term>{": "}
                  se um contraste clínico é de fato estimável dentro de um
                  projeto, ou se fica preso ao confundimento com o efeito de
                  projeto.
                </span>
              </li>
            </ul>
          </section>

          {/* 4 */}
          <section id="s4" ref={(el) => { refs.current["s4"] = el; }}>
            <h2 className="sec"><span className="sec-num">4.</span>Comandos do pipeline</h2>
            <div className="flow-diagram">
              {STEPS.map((step, i) => (
                <React.Fragment key={step.n}>
                  <div className="flow-node">
                    <div className="flow-icon">{STEP_ICONS[step.n]}</div>
                    <div className="flow-n">{step.n}</div>
                  </div>
                  {i < STEPS.length - 1 && <div className="flow-arrow">→</div>}
                </React.Fragment>
              ))}
            </div>
            <p>
              Cada etapa abaixo explica o que acontece e por quê, seguida
              do(s) comando(s) planejado(s), pra que qualquer pessoa entenda
              o processo e consiga reproduzi-lo assim que a execução real
              começar.
            </p>
            {STEPS.map((step) => (
              <div className="task-row" key={step.n}>
                <div className="task-head">
                  <div className="task-title">
                    <span className="step-icon">{STEP_ICONS[step.n]}</span>
                    <span className="n">{step.n}.</span>
                    {step.title}
                  </div>
                </div>
                <p className="task-note">{step.note}</p>
                {step.commands.map((cmd, i) => {
                  const code = typeof cmd === "string" ? cmd : cmd.code;
                  const caption = typeof cmd === "string" ? null : cmd.caption;
                  return (
                    <div key={i}>
                      <Listing command={code} />
                      {caption && <p className="cmd-caption">{caption}</p>}
                    </div>
                  );
                })}
              </div>
            ))}
          </section>

          {/* 5 - STATUS */}
          <section id="s4b" ref={(el) => { refs.current["s4b"] = el; }}>
            <h2 className="sec"><span className="sec-num">5.</span>Status do projeto</h2>
            <p>
              Duas etapas já estão concluídas: a confirmação dos primers por
              BioProject (Tabela 1b, seção 4) e o levantamento de accessions
              e metadados clínicos (Tabela 2b abaixo). O mapeamento
              Run/Sample → classe clínica veio de <code>metadata.txt</code>,
              compartilhado pela coautora Paola Gyuliane Gonçalves, e bate
              célula a célula com a Tabela I do artigo. O restante do
              pipeline segue a partir daqui.
            </p>
            <table className="formal">
              <caption><span className="cap-label">Tabela 2.</span> Etapas do pipeline e status atual.</caption>
              <thead><tr><th>Etapa</th><th>Status</th></tr></thead>
              <tbody>
                <tr><td>1. Accessions e metadados clínicos</td><td><span className="status-badge done">concluído</span></td></tr>
                <tr><td>2. Download dos FASTQ (10 BioProjects)</td><td><span className="status-badge done">concluído (evidenciado por feature-table.txt)</span></td></tr>
                <tr><td>3a. Confirmação de primers por BioProject</td><td><span className="status-badge done">concluído (8/10)</span></td></tr>
                <tr><td>3b–4. Import, corte de primers, deblur (V3-V4 / V4)</td><td><span className="status-badge done">concluído (evidenciado por feature-table.txt)</span></td></tr>
                <tr><td>5–6. Taxonomia SILVA e filtragem</td><td><span className="status-badge done">concluído, 997/1042 amostras retidas, batendo com o artigo</span></td></tr>
                <tr><td>7. PERMANOVA</td><td><span className="status-badge pending">pendente, dados prontos, falta rodar</span></td></tr>
                <tr><td>8. GLLVM</td><td><span className="status-badge pending">pendente, dados prontos, falta rodar</span></td></tr>
                <tr><td>9. Random Forest (CV aleatória vs. LOPO)</td><td><span className="status-badge pending">pendente, dados prontos, falta rodar</span></td></tr>
              </tbody>
            </table>
            <p style={{ fontSize: 13, fontStyle: "italic", marginTop: 8 }}>
              Etapas 2–6 inferidas como concluídas a partir de{" "}
              <code>feature-table.txt</code> (997 amostras, taxonomia
              atribuída, cruzado amostra a amostra com{" "}
              <code>metadata.txt</code>), não a partir de artefatos QIIME 2
              (.qza/.qzv) inspecionados diretamente. Vale confirmar a
              proveniência exata (parâmetros de deblur, versão do
              classificador SILVA) antes de tratar o dado como
              definitivamente fechado.
            </p>

            <table className="formal">
              <caption><span className="cap-label">Tabela 2b.</span> Resumo da confirmação de primers.</caption>
              <thead><tr><th>Situação</th><th>Projetos</th><th>Qtde.</th></tr></thead>
              <tbody>
                <tr><td><span className="status-badge done">confirmado</span></td><td>P1, P6, P9, P10, P14, P16, P19, P22</td><td>8</td></tr>
                <tr><td><span className="status-badge partial">não publicado, suposição documentada</span></td><td>P2</td><td>1</td></tr>
                <tr><td><span className="status-badge notfound">não publicado, sem suposição</span></td><td>P21</td><td>1</td></tr>
              </tbody>
            </table>
            <p style={{ fontSize: 13.5 }}>
              P2 e P21 foram verificados de forma exaustiva: artigo principal
              e material suplementar de ambos confirmam apenas a região
              amplificada (V4 e V3-V4, respectivamente) e o fornecedor
              comercial responsável pelo sequenciamento (Second Genome Inc. e
              Novogene), mas nenhum dos dois documentos nomeia o par de
              primer nem publica sua sequência de nucleotídeos, protocolo
              tratado como proprietário pelo fornecedor. Ver Tabela 1b
              (seção 4) e Referências para os DOIs exatos consultados.
            </p>

            <h3 style={{ fontSize: 15, marginTop: 24 }}>O que falta até o final</h3>
            <ol style={{ fontSize: 13.5, lineHeight: 1.7, paddingLeft: 20 }}>
              <li>
                <strong>Confirmar a proveniência do <code>feature-table.txt</code></strong>{" "}
                antes de tratar os dados como definitivamente fechados:
                parâmetros exatos do deblur, versão do classificador SILVA, e
                se corresponde à execução da Maria Thalillian, da Paola, ou a
                uma rodada nova. Os números batem, 997/1042 amostras, com o
                artigo, mas os parâmetros de processamento ainda não foram
                conferidos linha a linha.
              </li>
              <li>
                <strong>Decidir o tratamento de P2 e P21</strong>: os dois já
                estão presentes no <code>feature-table.txt</code> (77 e 105
                amostras mantidas, respectivamente, nenhuma filtrada). A
                decisão agora é se a limitação de proveniência do primer
                (Tabela 1b) precisa de nota metodológica no texto, já que os
                dados em si não foram excluídos do processamento.
              </li>
              <li>
                <strong>Etapa 7</strong>: PERMANOVA sobre Bray-Curtis a partir
                de <code>feature-table.txt</code> + <code>metadata.txt</code>,
                comparando com os valores-alvo da Tabela 3 (13,5% de variância
                explicada por condição+localidade+projeto).
              </li>
              <li>
                <strong>Etapa 8</strong>: GLLVM com e sem projeto como
                covariável, pra ver se o eixo dominante separa condição
                clínica ou projeto de origem.
              </li>
              <li>
                <strong>Etapa 9</strong>: protocolo de validação Random
                Forest, CV estratificada aleatória vs. leave-one-project-out,
                mais o controle negativo prevendo projeto a partir da
                composição. Esta é a etapa central declarada como "em
                andamento" no artigo.
              </li>
              <li>
                <strong>Fechamento</strong>: redigir a seção de metodologia
                da dissertação com base no que foi replicado, incluindo a
                nota sobre P16 (55 vs. 26 amostras de câncer entre o
                TCC de 2025 e o artigo LATINOWARE) e a proveniência do
                primer de P2/P21 como notas metodológicas.
              </li>
            </ol>

            <table className="formal">
              <caption><span className="cap-label">Tabela 3.</span> Valores publicados no paper, usados como alvo de comparação.</caption>
              <thead><tr><th>Métrica</th><th>Valor publicado</th></tr></thead>
              <tbody>
                <tr><td>Amostras finais (de 1.042 catalogadas)</td><td>997</td></tr>
                <tr><td>Variância explicada (condição + localidade + projeto)</td><td>13,5% (F = 12,821; p = 0,001)</td></tr>
                <tr><td>Contraste controle vs. câncer</td><td>5,0% (F = 38,257; p = 0,001)</td></tr>
                <tr><td>Contraste HSIL vs. câncer</td><td>3,6%</td></tr>
                <tr><td>Contraste LSIL vs. câncer</td><td>2,2%</td></tr>
                <tr><td>Contraste HSIL vs. LSIL</td><td>não significativo (p = 0,067)</td></tr>
                <tr><td>Amostras com contraste de 4 classes identificável</td><td>245 (23,5%), só P2 e P19</td></tr>
              </tbody>
            </table>
          </section>

          {/* 6 */}
          <section id="s5" ref={(el) => { refs.current["s5"] = el; }}>
            <h2 className="sec"><span className="sec-num">6.</span>Por que isso importa pra tese</h2>
            <p>
              A dissertação enfrenta exatamente esse mesmo problema
              metodológico, só que com <strong>microbioma de soja</strong>:
              combinar dados de vários projetos de origem diferentes pra
              classificar sanidade, sem deixar que o modelo aprenda a
              reconhecer o projeto em vez da condição biológica.
            </p>
            <table className="formal">
              <caption><span className="cap-label">Tabela 4.</span> O que se repete entre este estudo e a dissertação.</caption>
              <thead><tr><th>Neste estudo (câncer cervical)</th><th>Na dissertação (soja)</th></tr></thead>
              <tbody>
                <tr><td>Dez BioProjects agregados</td><td>Múltiplos projetos de soja combinados</td></tr>
                <tr><td>Câncer / HSIL / LSIL / controle</td><td>Sadio vs. doente (ou múltiplos estágios)</td></tr>
                <tr><td>PERMANOVA + GLLVM pra diagnosticar confundimento</td><td>Mesmo diagnóstico, aplicado ao dado de soja</td></tr>
                <tr><td>Leave-one-project-out proposto (não avaliado ainda)</td><td>Leave-one-project-out como validação central</td></tr>
              </tbody>
            </table>
            <p>
              Concluir esse diagnóstico de confundimento, e ir além dele,
              avaliando de fato o protocolo de validação com Random Forest,
              é uma forma direta de já chegar aos dados de soja sabendo
              reconhecer esse problema, em vez de descobri-lo tarde demais.
            </p>
          </section>

          {/* REFERÊNCIAS */}
          <section id="refs" ref={(el) => { refs.current["refs"] = el; }}>
            <h2 className="sec">Referências</h2>
            <ol className="refs">
              <li>
                Artigo próprio acompanhado neste caderno: "Validação por
                projeto em meta-análises de microbioma: um estudo de caso em
                câncer cervical", 23º Congresso Latino-americano de Software
                Livre e Tecnologias Abertas (LATINOWARE) / Latin.Science,
                2026 (nomes e afiliações omitidos para avaliação cega no
                original).
              </li>
              <li>
                BOLYEN, E. et al. Reproducible, interactive, scalable and
                extensible microbiome data science using QIIME 2.{" "}
                <em>Nature Biotechnology</em>, v.&nbsp;37, n.&nbsp;8, p.&nbsp;852-857, 2019.
              </li>
              <li>
                NIKU, J.; HUI, W.; TASKINEN, S.; WARTON, D.&nbsp;I. gllvm: Fast
                analysis of multivariate abundance data with generalized
                linear latent variable models in R.{" "}
                <em>Methods in Ecology and Evolution</em>, v.&nbsp;10, n.&nbsp;12,
                p.&nbsp;2173-2182, 2019.
              </li>
              <li>
                ANDERSON, M.&nbsp;J. A new method for non-parametric
                multivariate analysis of variance.{" "}
                <em>Austral Ecology</em>, v.&nbsp;26, n.&nbsp;1, p.&nbsp;32-46, 2001.
              </li>
              <li>
                QUAST, C. et al. The SILVA ribosomal RNA gene database
                project: improved data processing and web-based tools.{" "}
                <em>Nucleic Acids Research</em>, v.&nbsp;41, p.&nbsp;D590-D596, 2013.
              </li>
              <li>
                Artigos-fonte consultados para confirmação de primers
                (Tabela 1b):
                <ol style={{ marginTop: 8 }}>
                  <li>
                    WANG, Z. et al. The diversity of vaginal microbiota
                    predicts neoadjuvant chemotherapy responsiveness in
                    locally advanced cervical cancer.{" "}
                    <em>Microbial Ecology</em>, v.&nbsp;84, p.&nbsp;302-313,
                    2022. doi:10.1007/s00248-021-01800-0. (P1, P6)
                  </li>
                  <li>
                    TORTELLI, B.&nbsp;A. et al. Characterization of the
                    vaginal microbiome of postmenopausal patients receiving
                    chemoradiation for locally advanced cervical cancer.{" "}
                    <em>JCI Insight</em>, v.&nbsp;10, n.&nbsp;6, e176839,
                    2025. doi:10.1172/jci.insight.176839. (P9, P10, P16)
                  </li>
                  <li>
                    BRITTO, A.&nbsp;M.&nbsp;A. et al. Microbiome analysis of
                    Brazilian women cervix reveals specific bacterial
                    abundance correlation to RIG-like receptor gene
                    expression. <em>Frontiers in Immunology</em>, 2023.
                    doi:10.3389/fimmu.2023.1147950. (P14)
                  </li>
                  <li>
                    FAN, Q. et al. Lactobacillus spp. create a protective
                    micro-ecological environment through regulating the core
                    fucosylation of vaginal epithelial cells against cervical
                    cancer. <em>Cell Death &amp; Disease</em>, v.&nbsp;12,
                    n.&nbsp;12, 1094, 2021. doi:10.1038/s41419-021-04388-y.
                    (P22)
                  </li>
                  <li>
                    ŁANIEWSKI, P. et al. Linking cervicovaginal immune
                    signatures, HPV and microbiota composition in cervical
                    carcinogenesis in non-Hispanic and Hispanic women.{" "}
                    <em>Scientific Reports</em>, v.&nbsp;8, 7593, 2018.
                    doi:10.1038/s41598-018-25879-7. Primer não publicado
                    (artigo e material suplementar verificados); ver nota de
                    suposição documentada na Tabela 1b. (P2)
                  </li>
                  <li>
                    EARTH MICROBIOME PROJECT. 16S Illumina Amplicon
                    Protocol.{" "}
                    <a href="https://earthmicrobiome.ucsd.edu/protocols-and-standards/16s/" target="_blank" rel="noreferrer">
                      earthmicrobiome.ucsd.edu/protocols-and-standards/16s
                    </a>
                    . Fonte dos pares 515F/806R (Parada 2016 / Apprill 2015,
                    e Caporaso 2011/2012) usados na suposição documentada
                    para o P2, não confirma qual par a Second Genome Inc.
                    de fato usou.
                  </li>
                  <li>
                    ROSAS CANCIO-SUÁREZ, M. et al. Cervical microbiota
                    diversity and functional shifts in the development of
                    cervical high-grade squamous intraepithelial lesions.{" "}
                    <em>Frontiers in Medicine</em>, v.&nbsp;12, 1615571,
                    2025. doi:10.3389/fmed.2025.1615571. Primer não
                    publicado (texto completo verificado). (P21)
                  </li>
                </ol>
              </li>
            </ol>
          </section>

          <div className="footnote">
            Isto é um caderno de acompanhamento, não um relatório final: as
            seções 4 e 5 vão mudando conforme o trabalho avança de verdade.
          </div>
        </main>
      </div>

      <footer className="pagefoot">caderno vivo · PPGTCA / UTFPR</footer>
    </div>
  );
}
