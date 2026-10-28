import React, { useState, useRef } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";
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

type SectionId = "s1" | "s2" | "s3" | "s4" | "s4b" | "s4c" | "s5" | "refs";

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
  { id: "s4c", number: "6", label: "Auditoria de viés", icon: <BarChart3 size={14} /> },
  { id: "s5", number: "7", label: "Por que isso importa pra tese", icon: <GraduationCap size={14} /> },
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
  {
    codigo: "P10",
    regiao: "V4",
    fwd: "GTGCCAGCMGCCGCGGTAA",
    rev: "GGACTACHVGGGTWTCTAAT",
    fonte:
      "TOSADO-RODRÍGUEZ, E. L. et al. mSystems, 2023 (coorte hispânica de Porto Rico, centro UCSDMI, identificado via metadata-conferida.md): par original de Caporaso (2011/2012), sem o Y degenerado da versão atualizada usada em P9/P16. Achado adicional na execução real (Etapa 4): o BioProject mistura dois sublotes, uma parte com o primer de fato presente nas leituras brutas e outra, cerca de 165 amostras (faixas de accession ERR9391105-ERR9391228 e ERR9409855-ERR9409922), já sem primer na origem, tratada separadamente como P10b, igual ao caso de P9/P14/P2.",
    status: "done",
    statusLabel: "confirmado (misto)",
  },
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
  {
    codigo: "P19",
    regiao: "V3-V4",
    fwd: "CCTACGGGNGGCWGCAG",
    rev: "GACTACHVGGGTATCTAATCC",
    fonte:
      "MUSA, J. et al. BMC Cancer 23(1):683, 2023 cita 357wF/806R, mas a execução real do cutadapt reteve só 55% das leituras com esse par; testando 341F/805R a retenção subiu para 83,7%. Primer corrigido empiricamente, não pela fonte original.",
    status: "done",
    statusLabel: "corrigido empiricamente",
  },
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

const DATASET_COMPOSITION = [
  { codigo: "P1", CC: 68, HSIL: 0, LSIL: 0, Ctrl: 4 },
  { codigo: "P2", CC: 10, HSIL: 27, LSIL: 11, Ctrl: 29 },
  { codigo: "P6", CC: 26, HSIL: 0, LSIL: 0, Ctrl: 0 },
  { codigo: "P9", CC: 58, HSIL: 0, LSIL: 0, Ctrl: 0 },
  { codigo: "P10", CC: 1, HSIL: 59, LSIL: 43, Ctrl: 216 },
  { codigo: "P14", CC: 0, HSIL: 22, LSIL: 0, Ctrl: 21 },
  { codigo: "P16", CC: 55, HSIL: 0, LSIL: 0, Ctrl: 0 },
  { codigo: "P19", CC: 31, HSIL: 60, LSIL: 58, Ctrl: 19 },
  { codigo: "P21", CC: 0, HSIL: 2, LSIL: 0, Ctrl: 103 },
  { codigo: "P22", CC: 65, HSIL: 0, LSIL: 0, Ctrl: 54 },
];

const CLASS_COLORS: Record<string, string> = {
  CC: "#8b3a3a",
  HSIL: "#c07830",
  LSIL: "#a8944f",
  Ctrl: "#5b7a5b",
};

function DatasetCompositionChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 340, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={DATASET_COMPOSITION} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis dataKey="codigo" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} label={{ value: "amostras", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip contentStyle={{ fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="CC" stackId="a" fill={CLASS_COLORS.CC} name="Câncer">
            <LabelList dataKey="CC" position="inside" fontSize={10} fill="#fff" formatter={(v: any) => (v > 0 ? v : "")} />
          </Bar>
          <Bar dataKey="HSIL" stackId="a" fill={CLASS_COLORS.HSIL} name="HSIL">
            <LabelList dataKey="HSIL" position="inside" fontSize={10} fill="#fff" formatter={(v: any) => (v > 0 ? v : "")} />
          </Bar>
          <Bar dataKey="LSIL" stackId="a" fill={CLASS_COLORS.LSIL} name="LSIL">
            <LabelList dataKey="LSIL" position="inside" fontSize={10} fill="#fff" formatter={(v: any) => (v > 0 ? v : "")} />
          </Bar>
          <Bar dataKey="Ctrl" stackId="a" fill={CLASS_COLORS.Ctrl} name="Controle">
            <LabelList dataKey="Ctrl" position="inside" fontSize={10} fill="#fff" formatter={(v: any) => (v > 0 ? v : "")} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. A. Composição de classe por projeto (Tabela I), números dentro
        de cada segmento. P6, P9 e P16 são monoclasse (só câncer); P1 e P21
        são quase monoclasse. Essa distribuição desigual é a raiz do
        problema: quando quase todo projeto tem uma classe clínica
        dominante, projeto de origem e condição clínica ficam
        estatisticamente quase impossíveis de separar num modelo agregado.
      </div>
    </div>
  );
}

const AUC_COMPARISON = [
  { classe: "cancer", aleatoria: 0.967, lopo: 0.69 },
  { classe: "control", aleatoria: 0.862, lopo: 0.497 },
  { classe: "HSIL", aleatoria: 0.779, lopo: 0.46 },
  { classe: "LSIL", aleatoria: 0.746, lopo: 0.297 },
];

function AucComparisonChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 320, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={AUC_COMPARISON} margin={{ top: 20, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis dataKey="classe" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} label={{ value: "AUC", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip contentStyle={{ fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="aleatoria" fill="#5b7a9e" name="CV aleatória">
            <LabelList dataKey="aleatoria" position="top" fontSize={11} formatter={(v: any) => v.toFixed(2)} />
          </Bar>
          <Bar dataKey="lopo" fill="#a85b5b" name="Leave-one-project-out">
            <LabelList dataKey="lopo" position="top" fontSize={11} formatter={(v: any) => v.toFixed(2)} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. B. AUC por classe clínica, CV aleatória vs. leave-one-project-out
        (preview exploratório sobre o dado da Paola, Tabela 2c). A linha de
        0,5 é o nível de acaso. A queda de desempenho de uma coluna azul
        alta para uma coluna vermelha baixa, em toda classe, é o sinal
        visual do confundimento: o modelo aprende a reconhecer o projeto
        de origem, não a condição clínica, e falha quando é testado num
        projeto que nunca viu.
      </div>
    </div>
  );
}

const REAL_AUC_COMPARISON = [
  { classe: "cancer", aleatoria: 0.959, lopo: 0.717, lopoFix: 0.606 },
  { classe: "control", aleatoria: 0.815, lopo: 0.512, lopoFix: 0.419 },
  { classe: "lesion high", aleatoria: 0.76, lopo: 0.51, lopoFix: 0.467 },
  { classe: "lesion low", aleatoria: 0.71, lopo: 0.662, lopoFix: 0.337 },
];

function RealAucComparisonChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 320, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={REAL_AUC_COMPARISON} margin={{ top: 20, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis dataKey="classe" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} label={{ value: "AUC", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip contentStyle={{ fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="aleatoria" fill="#5b7a9e" name="CV aleatória">
            <LabelList dataKey="aleatoria" position="top" fontSize={11} formatter={(v: any) => v.toFixed(2)} />
          </Bar>
          <Bar dataKey="lopo" fill="#a85b5b" name="Leave-one-project-out">
            <LabelList dataKey="lopo" position="top" fontSize={11} formatter={(v: any) => v.toFixed(2)} />
          </Bar>
          <Bar dataKey="lopoFix" fill="#6f4a3a" name="LOPO, P22 reprocessado, direção da ROC fixa">
            <LabelList dataKey="lopoFix" position="top" fontSize={11} formatter={(v: any) => v.toFixed(2)} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. F. AUC real por classe clínica, CV aleatória vs.
        leave-one-project-out, execução própria sobre as 889 amostras
        finais. Macro-AUC cai de 0,811 para 0,6. A queda é maior justamente
        na classe câncer (0,959 para 0,717), a mais desbalanceada entre
        projetos (Fig. A). A linha de 0,5 é o nível de acaso: controle e
        lesão alta ficam bem perto dela sob leave-one-project-out, ou seja,
        quase não melhor que chutar. A terceira barra é o mesmo script
        depois de reprocessar o P22 (que tinha entrado no ramo V4 sendo
        V3-V4) e de fixar a direção da curva ROC no pROC: com a direção
        automática, o pacote inverte curvas abaixo de 0,5, e por isso a
        lesão baixa aparecia com 0,66. Com a direção fixa, o macro-AUC no
        LOPO cai para 0,457, abaixo do acaso (ver seção 6).
      </div>
    </div>
  );
}

const PERMANOVA_R2 = [
  { fator: "Condição clínica", r2: 3.32 },
  { fator: "Localidade", r2: 5.09 },
  { fator: "Projeto", r2: 12.08 },
];

function PermanovaChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 260, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={PERMANOVA_R2} layout="vertical" margin={{ top: 8, right: 40, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis type="number" domain={[0, 14]} tick={{ fontSize: 12 }} unit="%" />
          <YAxis type="category" dataKey="fator" tick={{ fontSize: 12 }} width={110} />
          <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v) => `${v}%`} />
          <Bar dataKey="r2" name="R² aproximado" radius={[0, 4, 4, 0]}>
            {PERMANOVA_R2.map((entry, i) => (
              <Cell key={entry.fator} fill={i === 2 ? "#a85b5b" : "#8a8370"} />
            ))}
            <LabelList dataKey="r2" position="right" fontSize={11} formatter={(v: any) => `${v}%`} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. C. Variação composicional explicada por fator, modelos
        marginais (preview exploratório, Tabela 2c). Projeto sozinho já
        explica quase tanto quanto o modelo completo publicado (13,5%), o
        indício inicial de que projeto de origem, e não condição clínica,
        é o que mais move a composição microbiana nesse dataset agregado.
      </div>
    </div>
  );
}

const REAL_PERMANOVA_R2 = [
  { fator: "Condição clínica", r2: 0.59 },
  { fator: "Localidade", r2: 0.0 },
  { fator: "Projeto", r2: 9.19 },
];

function RealPermanovaChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 260, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={REAL_PERMANOVA_R2} layout="vertical" margin={{ top: 8, right: 40, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis type="number" domain={[0, 10]} tick={{ fontSize: 12 }} unit="%" />
          <YAxis type="category" dataKey="fator" tick={{ fontSize: 12 }} width={110} />
          <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v) => `${v}%`} />
          <Bar dataKey="r2" name="R² marginal" radius={[0, 4, 4, 0]}>
            {REAL_PERMANOVA_R2.map((entry, i) => (
              <Cell key={entry.fator} fill={i === 2 ? "#a85b5b" : "#8a8370"} />
            ))}
            <LabelList dataKey="r2" position="right" fontSize={11} formatter={(v: any) => `${v}%`} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. E. PERMANOVA real, pipeline próprio, 889 amostras finais.
        Localidade sai com R² zero por colinearidade completa com projeto de
        origem, o R descarta o termo redundante porque cada projeto vem de
        um único país. Projeto explica quase 16 vezes mais variação que
        condição clínica, confirmando o padrão qualitativo do artigo sobre
        um dado processado do zero, de forma independente.
      </div>
    </div>
  );
}

const REAL_GLLVM_ETA2 = [
  { eixo: "LV1", projeto: 56.7, tipoAmostra: 11.1 },
  { eixo: "LV2", projeto: 58.2, tipoAmostra: 7.9 },
];

function RealGllvmChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 280, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={REAL_GLLVM_ETA2} margin={{ top: 20, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis dataKey="eixo" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 70]} tick={{ fontSize: 12 }} unit="%" label={{ value: "η²", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v) => `${v}%`} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="projeto" fill="#a85b5b" name="Projeto de origem">
            <LabelList dataKey="projeto" position="top" fontSize={11} formatter={(v: any) => `${v}%`} />
          </Bar>
          <Bar dataKey="tipoAmostra" fill="#5b7a9e" name="Condição clínica">
            <LabelList dataKey="tipoAmostra" position="top" fontSize={11} formatter={(v: any) => `${v}%`} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. G. Variância de cada eixo latente do GLLVM (sem covariáveis)
        explicada por projeto de origem vs. condição clínica, execução
        própria sobre as 889 amostras finais e os 98 gêneros mais
        prevalentes. Os dois eixos, que juntos resumem a maior parte da
        estrutura de composição do dataset, são dominados por projeto de
        origem por uma margem de mais de 5 vezes, terceira confirmação
        independente do mesmo achado do PERMANOVA (Fig. E).
      </div>
    </div>
  );
}

const RETENTION_DATA = [
  { regiao: "V3-V4", importadas: 309, retidas: 289 },
  { regiao: "V4", importadas: 628, retidas: 627 },
];

function RetentionChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 280, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={RETENTION_DATA} margin={{ top: 20, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis dataKey="regiao" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} label={{ value: "amostras", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip contentStyle={{ fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="importadas" fill="#8a8370" name="Importadas para o deblur">
            <LabelList dataKey="importadas" position="top" fontSize={11} />
          </Bar>
          <Bar dataKey="retidas" fill="#5b7a5b" name="Retidas pelo deblur">
            <LabelList dataKey="retidas" position="top" fontSize={11} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. D. Retenção do deblur por região, execução real do pipeline
        próprio. V3-V4 fechado em 93,5% (--p-trim-length 250). V4 fechado em
        99,8% (--p-trim-length 220), depois de corrigir o manifest
        duplicado do P10 explicado no texto. As duas barras quase do mesmo
        tamanho mostram que a perda de amostras nessa etapa foi pequena,
        a maior parte da diferença entre 889 e 997 amostras finais vem de
        outro lugar, a exclusão do P21 (Etapa 6).
      </div>
    </div>
  );
}

const SAMPLE_FUNNEL = [
  { etapa: "Catalogadas", amostras: 1042 },
  { etapa: "Teto sem P21", amostras: 937 },
  { etapa: "Pré-corte de profundidade", amostras: 916 },
  { etapa: "Final (corte 1000)", amostras: 889 },
];

function SampleFunnelChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 300, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={SAMPLE_FUNNEL} layout="vertical" margin={{ top: 8, right: 48, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis type="number" domain={[0, 1100]} tick={{ fontSize: 12 }} />
          <YAxis type="category" dataKey="etapa" tick={{ fontSize: 12 }} width={170} />
          <Tooltip contentStyle={{ fontSize: 12 }} />
          <Bar dataKey="amostras" name="Amostras" radius={[0, 4, 4, 0]}>
            {SAMPLE_FUNNEL.map((entry) => (
              <Cell key={entry.etapa} fill={entry.etapa === "Final (corte 1000)" ? "#5b7a5b" : "#8a8370"} />
            ))}
            <LabelList dataKey="amostras" position="right" fontSize={12} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. H. Funil de amostras do pipeline próprio, do total catalogado
        até o dataset final. A maior perda (105 amostras) é a exclusão do
        P21 por falta de primer confirmado, não a bioinformática em si: do
        teto de 937 amostras alcançável sem o P21, o pipeline chega a 889
        depois do deblur e do corte de profundidade, uma perda adicional
        de só 5,1%.
      </div>
    </div>
  );
}

const PAIRWISE_CONTRASTS = [
  { par: "Ctrl vs. câncer", publicado: 5.0, proprio: 6.52 },
  { par: "HSIL vs. câncer", publicado: 3.6, proprio: 5.75 },
  { par: "LSIL vs. câncer", publicado: 2.2, proprio: 4.44 },
  { par: "HSIL vs. LSIL", publicado: 0, proprio: 0.61 },
];

function PairwiseContrastsChart() {
  return (
    <div className="fig-block" style={{ width: "100%", height: 300, margin: "40px 0" }}>
      <ResponsiveContainer>
        <BarChart data={PAIRWISE_CONTRASTS} margin={{ top: 20, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis dataKey="par" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 12 }} unit="%" label={{ value: "R²", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v) => `${v}%`} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="publicado" fill="#8a8370" name="Valor publicado (artigo)">
            <LabelList dataKey="publicado" position="top" fontSize={11} formatter={(v: any) => (v > 0 ? `${v}%` : "n.s.")} />
          </Bar>
          <Bar dataKey="proprio" fill="#5b7a5b" name="Pipeline próprio">
            <LabelList dataKey="proprio" position="top" fontSize={11} formatter={(v: any) => `${v}%`} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. I. Contrastes par a par entre condições clínicas, PERMANOVA
        restrito a 2 classes por vez, valor publicado no artigo contra o
        pipeline próprio. As magnitudes do pipeline próprio ficam sempre
        um pouco acima das publicadas, mas na mesma ordem de grandeza e na
        mesma direção, e o par HSIL vs. LSIL (a barra de 0,61%,
        rotulada "n.s." no valor publicado) é o único não significativo
        nos dois casos, a réplica mais próxima do artigo obtida até aqui.
      </div>
    </div>
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
    title: "Importar, cortar primers e preparar para o deblur",
    note: (
      <>
        <p style={{ marginTop: 0 }}>
          Importar cada projeto no QIIME 2 (<code>import_all.sh</code>,
          detecção automática pareado/single-end por amostra), cortar os{" "}
          <em>primers</em> com o plugin cutadapt e preparar as sequências
          para o deblur (mesclar pares e filtrar por qualidade). Nem todos
          os projetos precisam do mesmo tratamento: isso só ficou claro na
          execução real, checando a taxa de retenção do cutadapt projeto a
          projeto.
        </p>
        <p>
          <strong>Achados da execução real:</strong> P9, P14 e P2 tiveram
          retenção ~0% ao tentar cortar o primer esperado. Inspecionando as
          leituras brutas, ficou claro que esses três projetos já vieram{" "}
          <strong>sem o primer</strong>, removido na origem antes do
          depósito no repositório. Para esses, o cutadapt é pulado (copia-se
          o artefato importado direto como "trimmed"). P19 teve retenção de
          só 55% com o par documentado (357wF/806R); testando 341F/805R a
          retenção subiu para 83,7%, então o primer real desse projeto foi{" "}
          <strong>corrigido empiricamente</strong>, e a Tabela 1b foi
          atualizada. P10 e P22 se confirmaram <strong>single-end de
          verdade</strong> (a leitura cobre quase todo o amplicon V4
          sozinha), apesar do campo <code>library_layout</code> do
          ENA/SRA dizer <code>PAIRED</code> para algumas dessas runs, uma
          inconsistência de metadado documentada, não um erro de download.
          Uma investigação mais profunda, já durante a fusão das regiões
          na Etapa 4, revelou ainda que o próprio P10 é um caso misto:
          parte das amostras tem o primer 515F(Caporaso) de fato presente,
          e outra parte (cerca de 165 de 319) já veio sem primer, como
          P9/P14/P2, exigindo separação em dois lotes de processamento.
        </p>
        <table className="formal">
          <caption>
            <span className="cap-label">Tabela 1c.</span> Resultado real do
            corte de primer, por projeto (retenção via <code>cutadapt --p-discard-untrimmed</code>).
          </caption>
          <thead>
            <tr><th>Projeto</th><th>Ação</th><th>Retenção</th><th>Observação</th></tr>
          </thead>
          <tbody>
            <tr><td>P1</td><td>cutadapt 338F/806R</td><td>~98%</td><td>ok</td></tr>
            <tr><td>P6</td><td>cutadapt 338F/806R</td><td>~99,8%</td><td>ok</td></tr>
            <tr><td>P10</td><td>cutadapt 515F(Caporaso), single</td><td>~99,7% no sublote com primer; ~0,008% no sublote sem primer</td><td>BioProject misto (ver Etapa 4): par diferente de P9/P16, confirmado no artigo-fonte; ~165 das 319 amostras precisaram de tratamento à parte (P10b), resolvido, deblur da V4 fechado em 99,8%</td></tr>
            <tr><td>P16</td><td>cutadapt 515F(Parada)/806R</td><td>~98,8%</td><td>ok</td></tr>
            <tr><td>P22</td><td>cutadapt 341F, single</td><td>~97,8%</td><td>4 runs com R2 vazia migradas para single-end</td></tr>
            <tr><td>P19</td><td>cutadapt 341F/805R</td><td>83,7%</td><td>corrigido: fonte antiga apontava 357wF/806R (55% de retenção)</td></tr>
            <tr><td>P9</td><td>sem corte (cópia direta)</td><td>0% com primer esperado</td><td>primer já removido na origem</td></tr>
            <tr><td>P14</td><td>sem corte (cópia direta)</td><td>0,05% com primer esperado</td><td>primer já removido na origem</td></tr>
            <tr><td>P2</td><td>sem corte (cópia direta)</td><td>0,0006% com primer esperado</td><td>primer já removido na origem; a suposição do par EMP ficou sem efeito prático</td></tr>
            <tr><td>P21</td><td>SKIP</td><td>N/D</td><td>sem primer confirmado nem suposição plausível</td></tr>
          </tbody>
        </table>
        <PrimerTable />
      </>
    ),
    commands: [
      {
        code: `# Import (todos os 10 projetos de uma vez, detecta pareado/single por amostra)
python3 generate_manifests.py --raw-dir raw --out-dir manifests
conda activate rachis-qiime2-2026.7
./import_all.sh`,
        caption:
          "Gera qiime/{projeto}_paired.qza e/ou qiime/{projeto}_single.qza, com log em qiime/import_log.tsv.",
      },
      {
        code: `# Grupo 338F/806R (V3-V4): P1, P6
qiime cutadapt trim-paired \\
  --i-demultiplexed-sequences qiime/P1_paired.qza \\
  --p-front-f ACTCCTACGGGAGGCAGCA \\
  --p-front-r GGACTACHVGGGTWTCTAAT \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences qiime/P1_trimmed.qza \\
  --o-stats qiime/P1_cutadapt_stats.qza`,
        caption: "Repetir para P6 trocando o projeto. --o-stats é obrigatório nesta versão do plugin.",
      },
      `# 515F(Parada)/806R(Apprill), V4: P16
qiime cutadapt trim-paired \\
  --i-demultiplexed-sequences qiime/P16_paired.qza \\
  --p-front-f GTGYCAGCMGCCGCGGTAA \\
  --p-front-r GGACTACNVGGGTWTCTAAT \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences qiime/P16_trimmed.qza \\
  --o-stats qiime/P16_cutadapt_stats.qza`,
      {
        code: `# P10: 515F(Caporaso original, sem Y), V4, single-end
qiime cutadapt trim-single \\
  --i-demultiplexed-sequences qiime/P10_single.qza \\
  --p-front GTGCCAGCMGCCGCGGTAA \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences qiime/P10_trimmed.qza \\
  --o-stats qiime/P10_cutadapt_stats.qza`,
        caption: "Par diferente de P9/P16 mesmo sendo a mesma região nominal, confirmado no artigo-fonte (Tosado-Rodríguez et al. 2023).",
      },
      `# P19: 341F/805R (corrigido; a fonte antiga indicava 357wF/806R)
qiime cutadapt trim-paired \\
  --i-demultiplexed-sequences qiime/P19_paired.qza \\
  --p-front-f CCTACGGGNGGCWGCAG \\
  --p-front-r GACTACHVGGGTATCTAATCC \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences qiime/P19_trimmed.qza \\
  --o-stats qiime/P19_cutadapt_stats.qza`,
      `# P22: 341F, single-end (dado real; parte das runs tem R2 vazia)
qiime cutadapt trim-single \\
  --i-demultiplexed-sequences qiime/P22_single.qza \\
  --p-front CCTAYGGGRBGCASCAG \\
  --p-discard-untrimmed \\
  --o-trimmed-sequences qiime/P22_trimmed.qza \\
  --o-stats qiime/P22_cutadapt_stats.qza`,
      {
        code: `# P9, P14, P2: primer ja removido na origem, sem corte, so copia o artefato
cp qiime/P9_paired.qza qiime/P9_trimmed.qza
cp qiime/P14_paired.qza qiime/P14_trimmed.qza
cp qiime/P2_paired.qza qiime/P2_trimmed.qza`,
        caption:
          "Confirmado por retenção ~0% com o primer esperado, e pela leitura bruta não começar com nenhuma sequência de primer conhecida.",
      },
      {
        code: `# P21: sem primer confirmado nem suposicao plausivel, SKIP
echo "P21 excluido: sequencia proprietaria (Novogene), sem par de referencia plausivel" \\
  >> primers_skip.log`,
        caption:
          "Decisão em aberto: excluir P21 do dataset agregado, ou manter e documentar a limitação no texto final.",
      },
      {
        code: `# Mesclar pares (forward+reverse) nos projetos ainda pareados
for p in P1 P6 P9 P14 P16 P19 P2; do
  qiime vsearch merge-pairs \\
    --i-demultiplexed-seqs qiime/\${p}_trimmed.qza \\
    --o-merged-sequences qiime/\${p}_joined.qza \\
    --o-unmerged-sequences qiime/\${p}_unmerged.qza
done`,
        caption: "P10 e P22 já são single-end, não passam por este passo.",
      },
      `# Filtro de qualidade (Q-score), todos os 9 projetos usaveis
for p in P1 P6 P9 P14 P16 P19 P2; do
  qiime quality-filter q-score \\
    --i-demux qiime/\${p}_joined.qza \\
    --o-filtered-sequences qiime/\${p}_filtered.qza \\
    --o-filter-stats qiime/\${p}_filter_stats.qza
done
for p in P10 P22; do
  qiime quality-filter q-score \\
    --i-demux qiime/\${p}_trimmed.qza \\
    --o-filtered-sequences qiime/\${p}_filtered.qza \\
    --o-filter-stats qiime/\${p}_filter_stats.qza
done`,
    ],
  },
  {
    n: 4,
    title: "Denoising com deblur (por região)",
    note: (
      <>
        <p style={{ marginTop: 0 }}>
          O paper original usa o plugin <Term id="deblur">q2-deblur</Term> do
          QIIME 2 2023.2 pra gerar as <Term id="asv">ASVs</Term>. Cada região
          (V3-V4 e V4) precisa de um lote de deblur separado, com seu próprio
          comprimento de corte, porque não dá pra comparar ASVs de regiões
          diferentes diretamente. Antes disso, os artefatos{" "}
          <code>*_filtered.qza</code> de cada grupo de região (V3-V4: P1, P6,
          P14, P19; V4: P2, P9, P10, P16, P22) precisam virar um único
          artefato por região.
        </p>
        <p>
          <strong>Primeira tentativa errada:</strong> <code>qiime
          feature-table merge-seqs</code> parecia o comando óbvio, mas ele
          exige <code>FeatureData[Sequence]</code> (saída pós-deblur), não{" "}
          <code>SampleData[...]</code> (a entrada, ainda pré-deblur). O
          comando falhou com um erro de tipo incompatível nos dois grupos.
          A solução real foi outra: exportar cada artefato{" "}
          <code>_filtered.qza</code> pra FASTQ bruto, montar um manifest
          combinado por região com um script Python (glob nas pastas
          exportadas), e reimportar tudo como um único artefato{" "}
          <code>SampleData[SequencesWithQuality]</code> por região.
        </p>
        <p>
          Nessa reimportação, o disco chegou a ficar crítico duas vezes
          (98% cheio, 12&nbsp;GB livres), interrompendo o import com{" "}
          <code>OSError: [Errno 28] No space left on device</code>. Resolvido
          apagando os artefatos intermediários já superados (
          <code>*_paired.qza</code>, <code>*_single.qza</code>,{" "}
          <code>*_trimmed*.qza</code>, <code>*_joined.qza</code>), o que
          liberou a pasta <code>qiime/</code> de 43&nbsp;GB pra 7,4&nbsp;GB.
        </p>
        <p>
          <strong>Resultado real do deblur:</strong> a região V3-V4 (
          <code>--p-trim-length 250</code>) fechou com 289 de 309 amostras
          retidas (93,5%), compatível com o esperado. A região V4 na
          primeira tentativa, também com corte em 250, reteve só 243 de 624
          (38,9%), uma perda enorme. Um histograma de comprimento de leitura
          mostrou grandes grupos de amostras com leituras entre 221 e 232
          pb, abaixo do corte de 250 pb, o que descartava a amostra inteira.
          Refazendo com <code>--p-trim-length 220</code>, a retenção subiu
          pra 469 de 624 (75,2%), ainda abaixo da taxa de ~93% obtida na
          V3-V4.
        </p>
        <p>
          <strong>Isolando o restante da perda em V4:</strong> cruzando os
          IDs de amostra retidos contra os manifests de cada projeto, P2,
          P9, P16 e P22 bateram 100% de retenção, mas o P10 sozinho ficou em
          apenas 160 de 319 (50%). Investigando manualmente (contagem de
          leituras por amostra, estatísticas do cutadapt por amostra via{" "}
          <code>qiime metadata tabulate</code>, inspeção dos prefixos das
          leituras brutas), ficou claro que o próprio P10 mistura dois
          sublotes: cerca de 154 amostras com o primer 515F(Caporaso) de
          fato presente (retenção do cutadapt ~99,7%), e cerca de 165
          amostras (faixas de accession ERR9391105-ERR9391228 e
          ERR9409855-ERR9409922) já sem primer na origem (retenção do
          cutadapt ~0,008%, leituras brutas começando direto na sequência
          16S pós-primer). É o mesmo padrão de P9/P14/P2, só que como um
          sublote dentro de um único projeto, não o projeto inteiro, um
          achado novo e mais complexo que exigiu tratamento separado. Essas
          165 amostras quase vazias pós-cutadapt explicam a maior parte da
          perda: sem leitura real, o deblur simplesmente as descartava.
        </p>
        <p>
          A correção extraiu as 165 IDs do sublote sem primer via um filtro
          nas estatísticas do cutadapt, montou um manifest só pra elas
          apontando pro FASTQ bruto (sem corte), reimportou diretamente como{" "}
          <code>SampleData[SequencesWithQuality]</code> e rodou o filtro de
          qualidade, produzindo <code>P10_sem_primer_filtered.qza</code>{" "}
          ("P10b"), com os dados reais dessas 165 amostras. A primeira
          tentativa de juntar P10b ao restante da região V4 falhou com{" "}
          <code>Metadata IDs must be unique</code>, porque{" "}
          <code>P10_filtered.qza</code> ("P10a") ainda continha essas mesmas
          165 IDs, só que com leituras quase vazias. Corrigindo o script de
          manifest combinado pra excluir essas 165 IDs da exportação do
          P10a antes de juntar com o P10b, o import passou a fechar sem
          duplicata (628 amostras únicas, conferido com{" "}
          <code>sort | uniq -d</code>), e o deblur da região V4 refeito
          sobre esse manifest corrigido reteve 627 de 628 amostras (99,8%),
          essencialmente fechado, no mesmo patamar da V3-V4.
        </p>
        <RetentionChart />
      </>
    ),
    commands: [
      {
        code: `mkdir -p export/V3V4 export/V4

for p in P1 P6 P14 P19; do
  qiime tools export --input-path qiime/\${p}_filtered.qza --output-path export/V3V4/\${p}
done

for p in P2 P9 P10 P16 P22; do
  qiime tools export --input-path qiime/\${p}_filtered.qza --output-path export/V4/\${p}
done`,
        caption:
          "Exporta cada projeto de volta para FASTQ bruto, contornando o feature-table merge-seqs (que exige FeatureData[Sequence], não SampleData[...]).",
      },
      {
        code: `python3 << 'PYEOF'
import glob, os, csv

for regiao, projetos in [("V3V4", ["P1","P6","P14","P19"]), ("V4", ["P2","P9","P10","P16","P22"])]:
    rows = []
    for p in projetos:
        for fp in sorted(glob.glob(f"export/{regiao}/{p}/*.fastq.gz")):
            sample_id = os.path.basename(fp).split(".")[0].split("_")[0]
            rows.append((sample_id, os.path.abspath(fp)))
    out = f"manifests/{regiao}_combined_manifest.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f, delimiter="\\t", lineterminator="\\n")
        w.writerow(["sample-id", "absolute-filepath"])
        w.writerows(rows)
    print(f"{out}: {len(rows)} amostras")
PYEOF`,
        caption:
          "Primeira rodada: manifests/V3V4_combined_manifest.csv: 309 amostras. manifests/V4_combined_manifest.csv: 624 amostras (antes de incluir o P10b, ver correção abaixo).",
      },
      {
        code: `qiime tools import \\
  --type 'SampleData[SequencesWithQuality]' \\
  --input-path manifests/V3V4_combined_manifest.csv \\
  --input-format SingleEndFastqManifestPhred33V2 \\
  --output-path qiime/V3V4_filtered_merged.qza

qiime tools import \\
  --type 'SampleData[SequencesWithQuality]' \\
  --input-path manifests/V4_combined_manifest.csv \\
  --input-format SingleEndFastqManifestPhred33V2 \\
  --output-path qiime/V4_filtered_merged.qza`,
        caption:
          "Falhou uma vez por falta de espaço em disco (OSError Errno 28), refeito com sucesso após liberar qiime/ de 43 GB para 7,4 GB.",
      },
      {
        code: `qiime deblur denoise-16S \\
  --i-demultiplexed-seqs qiime/V3V4_filtered_merged.qza \\
  --p-trim-length 250 \\
  --p-sample-stats \\
  --o-representative-sequences qiime/V3V4_repseqs.qza \\
  --o-table qiime/V3V4_table.qza \\
  --o-stats qiime/V3V4_stats.qza`,
        caption: "Resultado real: 289 de 309 amostras retidas (93,5%). Fechado.",
      },
      {
        code: `qiime deblur denoise-16S \\
  --i-demultiplexed-seqs qiime/V4_filtered_merged.qza \\
  --p-trim-length 220 \\
  --p-sample-stats \\
  --o-representative-sequences qiime/V4_repseqs.qza \\
  --o-table qiime/V4_table.qza \\
  --o-stats qiime/V4_stats.qza`,
        caption:
          "Primeira rodada com esse manifest (antes da correção do P10; a tentativa anterior com --p-trim-length 250 reteve só 243/624, 38,9%): 469 de 624 amostras retidas (75,2%), abaixo do alvo por causa do sublote sem primer do P10.",
      },
      {
        code: `awk -F'\\t' 'NR>2 && $3<10 {print $1}' /tmp/p10_cutadapt_stats/metadata.tsv > /tmp/p10_sem_primer.txt
# NR>2 pula o cabecalho e a linha de tipo (#q2:types)
# $3 = percent-reads-after; <10% identifica o sublote sem primer`,
        caption:
          "Isola as 165 IDs do sublote sem primer a partir das estatísticas do cutadapt por amostra, exportadas via qiime metadata tabulate.",
      },
      {
        code: `qiime tools import \\
  --type 'SampleData[SequencesWithQuality]' \\
  --input-path manifests/P10_sem_primer_manifest.csv \\
  --input-format SingleEndFastqManifestPhred33V2 \\
  --output-path qiime/P10_sem_primer.qza

qiime quality-filter q-score \\
  --i-demux qiime/P10_sem_primer.qza \\
  --o-filtered-sequences qiime/P10_sem_primer_filtered.qza \\
  --o-filter-stats qiime/P10_sem_primer_filter_stats.qza`,
        caption:
          "Manifest construído com os.path.abspath() (paths relativos causam ValueError). Pula o cutadapt: o primer já não existe nessas leituras. Produz P10_sem_primer_filtered.qza (\"P10b\").",
      },
      {
        code: `# Correcao: excluir as 165 IDs do sublote sem primer ao exportar P10a
# (qiime/P10_filtered.qza) antes de gerar o manifest combinado da V4,
# para nao duplicar essas IDs com as vindas de P10b.

qiime tools import \\
  --type 'SampleData[SequencesWithQuality]' \\
  --input-path manifests/V4_combined_manifest.csv \\
  --input-format SingleEndFastqManifestPhred33V2 \\
  --output-path qiime/V4_filtered_merged.qza

qiime deblur denoise-16S \\
  --i-demultiplexed-seqs qiime/V4_filtered_merged.qza \\
  --p-trim-length 220 \\
  --p-sample-stats \\
  --o-representative-sequences qiime/V4_repseqs.qza \\
  --o-table qiime/V4_table.qza \\
  --o-stats qiime/V4_stats.qza`,
        caption:
          "Manifest corrigido: 628 linhas de dados, 0 IDs duplicadas (sort | uniq -d). Deblur refeito sobre esse manifest reteve 627/628 amostras (99,8%). Região V4 fechada.",
      },
    ],
  },
  {
    n: 5,
    title: "Atribuição taxonômica (SILVA)",
    note: (
      <>
        <p style={{ marginTop: 0 }}>
          Classificar as sequências representativas contra o banco{" "}
          <Term id="silva">SILVA</Term>, pra dar nome (taxonomia) a cada
          ASV. É essa taxonomia, não o ASV bruto, que depois permite unir as
          tabelas das duas regiões num único conjunto agregado.
        </p>
        <p>
          <strong>Problema real encontrado:</strong> o classificador
          pré-treinado oficial (<code>silva-138-99-nb-classifier.qza</code>,
          baixado dos data resources do QIIME 2) foi treinado com
          scikit-learn 0.24.1, e o ambiente usado aqui roda scikit-learn
          1.7.1. O <code>classify-sklearn</code> recusou o artefato com{" "}
          <code>ValueError: The scikit-learn version ... does not match</code>
          , pra evitar corrupção silenciosa dos resultados.
        </p>
        <p>
          <strong>Solução aplicada:</strong> em vez do classificador pronto,
          baixadas as referências brutas do SILVA (sequências e taxonomia,
          93&nbsp;MB e 6,5&nbsp;MB), extraída a região amplificada de cada
          par de primer confirmado com <code>extract-reads</code> (reduz o
          tamanho da referência antes de treinar), e treinado um
          classificador Naive Bayes por região com{" "}
          <code>fit-classifier-naive-bayes</code>, usando a versão de
          scikit-learn já instalada no ambiente. Essa etapa é a mais pesada
          de todo o pipeline: o treino de cada classificador levou entre
          1&nbsp;e 5&nbsp;horas num MacBook Air, mesmo restringindo a
          referência à região amplificada.
        </p>
        <p>
          Os dois classificadores treinados classificaram as sequências
          representativas das duas regiões sem erro:{" "}
          <code>V3V4_taxonomy.qza</code> e <code>V4_taxonomy.qza</code>{" "}
          gerados com sucesso. Etapa fechada nas duas regiões.
        </p>
      </>
    ),
    commands: [
      {
        code: `curl -sSL -o silva-138-99-seqs.qza \\
  "https://data.qiime2.org/2024.2/common/silva-138-99-seqs.qza"
curl -sSL -o silva-138-99-tax.qza \\
  "https://data.qiime2.org/2024.2/common/silva-138-99-tax.qza"`,
        caption:
          "O classificador pronto (silva-138-99-nb-classifier.qza) foi baixado primeiro e descartado por incompatibilidade de versão do scikit-learn (0.24.1 vs. 1.7.1 instalado).",
      },
      {
        code: `qiime feature-classifier extract-reads \\
  --i-sequences silva-138-99-seqs.qza \\
  --p-f-primer ACTCCTACGGGAGGCAGCA \\
  --p-r-primer GGACTACHVGGGTWTCTAAT \\
  --p-n-jobs 4 \\
  --o-reads silva-138-99-V3V4-seqs.qza \\
  --o-read-extraction-stats silva-138-99-V3V4-extraction-stats.qza

qiime feature-classifier extract-reads \\
  --i-sequences silva-138-99-seqs.qza \\
  --p-f-primer GTGYCAGCMGCCGCGGTAA \\
  --p-r-primer GGACTACNVGGGTWTCTAAT \\
  --p-n-jobs 4 \\
  --o-reads silva-138-99-V4-seqs.qza \\
  --o-read-extraction-stats silva-138-99-V4-extraction-stats.qza`,
        caption:
          "extract-reads exige --o-read-extraction-stats (obrigatório) e --p-n-jobs >= 1 (não aceita 0 como classify-sklearn).",
      },
      {
        code: `qiime feature-classifier fit-classifier-naive-bayes \\
  --i-reference-reads silva-138-99-V3V4-seqs.qza \\
  --i-reference-taxonomy silva-138-99-tax.qza \\
  --o-classifier silva-138-99-V3V4-classifier.qza

qiime feature-classifier fit-classifier-naive-bayes \\
  --i-reference-reads silva-138-99-V4-seqs.qza \\
  --i-reference-taxonomy silva-138-99-tax.qza \\
  --o-classifier silva-138-99-V4-classifier.qza`,
        caption:
          "Comando mais pesado do pipeline inteiro, single-thread, sem --p-n-jobs. Rodar um de cada vez, não em paralelo.",
      },
      {
        code: `qiime feature-classifier classify-sklearn \\
  --i-classifier silva-138-99-V3V4-classifier.qza \\
  --i-reads qiime/V3V4_repseqs.qza \\
  --p-n-jobs 4 \\
  --o-classification qiime/V3V4_taxonomy.qza

qiime feature-classifier classify-sklearn \\
  --i-classifier silva-138-99-V4-classifier.qza \\
  --i-reads qiime/V4_repseqs.qza \\
  --p-n-jobs 4 \\
  --o-classification qiime/V4_taxonomy.qza`,
        caption: "As duas fecharam sem erro. Etapa 5 concluída.",
      },
    ],
  },
  {
    n: 6,
    title: "Filtragem",
    note: (
      <>
        <p style={{ marginTop: 0 }}>
          Remover cloroplasto, mitocôndria, arqueia e singletons, depois
          filtrar amostras com profundidade insuficiente. A meta é bater com
          as <strong>997 amostras finais</strong> reportadas no artigo (de
          1.042 catalogadas na Tabela I).
        </p>
        <p>
          <strong>Correção de abordagem:</strong> V3-V4 e V4 sequenciam
          pedaços diferentes do gene 16S, então as ASVs de uma região não
          são diretamente comparáveis às da outra, mesmo vindo da mesma
          bactéria. Juntar as duas tabelas de ASV brutas numa só não faz
          sentido biológico. A correção foi colapsar cada tabela num nível
          taxonômico comum (gênero, nível 6 do SILVA) antes de mesclar as
          duas regiões, usando a taxonomia da Etapa 5 como ponte entre
          elas.
        </p>
        <p>
          <strong>Resultado real:</strong> 289 (V3-V4) + 627 (V4) = 916
          amostras entraram na mesclagem por gênero. Com o filtro de
          profundidade mínima em 1.000 leituras por amostra, sobraram{" "}
          <strong>889 amostras</strong> no dataset final agregado. O teto
          alcançável por este pipeline não são as 1.042 catalogadas, e sim
          1.042 − 105 (P21, excluído desde a Etapa 3 por falta de primer
          confirmado) = 937. Então 889/937 = 94,9% de retenção sobre o que
          era alcançável, e 889/997 = 89,2% do número publicado no artigo.
          Testado também um corte mais permissivo (500 leituras), que
          recupera só 16 amostras a mais (905 no total), então o corte de
          1.000 foi mantido como final, por ser o critério mais defensável
          tecnicamente, mesmo não fechando o número publicado. A diferença
          restante fica documentada como limitação, não como erro do
          pipeline: vem majoritariamente da exclusão do P21.
        </p>
      </>
    ),
    commands: [
      {
        code: `qiime taxa filter-table \\
  --i-table qiime/V3V4_table.qza \\
  --i-taxonomy qiime/V3V4_taxonomy.qza \\
  --p-exclude mitochondria,chloroplast,archaea \\
  --o-filtered-table qiime/V3V4_table_clean.qza

qiime taxa filter-table \\
  --i-table qiime/V4_table.qza \\
  --i-taxonomy qiime/V4_taxonomy.qza \\
  --p-exclude mitochondria,chloroplast,archaea \\
  --o-filtered-table qiime/V4_table_clean.qza`,
        caption: "Remove cloroplasto, mitocôndria e arqueia de cada região separadamente.",
      },
      {
        code: `qiime feature-table filter-features \\
  --i-table qiime/V3V4_table_clean.qza \\
  --p-min-frequency 2 \\
  --o-filtered-table qiime/V3V4_table_nosingle.qza

qiime feature-table filter-features \\
  --i-table qiime/V4_table_clean.qza \\
  --p-min-frequency 2 \\
  --o-filtered-table qiime/V4_table_nosingle.qza`,
        caption: "Remove singletons (features com frequência total menor que 2).",
      },
      {
        code: `qiime taxa collapse \\
  --i-table qiime/V3V4_table_nosingle.qza \\
  --i-taxonomy qiime/V3V4_taxonomy.qza \\
  --p-level 6 \\
  --o-collapsed-table qiime/V3V4_genus.qza

qiime taxa collapse \\
  --i-table qiime/V4_table_nosingle.qza \\
  --i-taxonomy qiime/V4_taxonomy.qza \\
  --p-level 6 \\
  --o-collapsed-table qiime/V4_genus.qza`,
        caption:
          "Colapsa cada tabela em gênero (nível 6), tornando as duas regiões comparáveis pela taxonomia, não pela sequência.",
      },
      {
        code: `qiime feature-table merge \\
  --i-tables qiime/V3V4_genus.qza qiime/V4_genus.qza \\
  --p-overlap-method sum \\
  --o-merged-table qiime/genus_table_merged.qza`,
        caption: "916 amostras únicas mescladas (289 + 627, sem sobreposição entre regiões).",
      },
      {
        code: `qiime feature-table filter-samples \\
  --i-table qiime/genus_table_merged.qza \\
  --p-min-frequency 1000 \\
  --o-filtered-table qiime/genus_table_final.qza`,
        caption:
          "889 amostras finais (testado também --p-min-frequency 500: 905 amostras, ganho marginal de 16; mantido 1000 como corte final).",
      },
    ],
  },
  {
    n: 7,
    title: "Partição de variância (PERMANOVA)",
    note: (
      <>
        Rodar <Term id="permanova">PERMANOVA</Term> sobre dissimilaridade de{" "}
        <Term id="brayCurtis">Bray-Curtis</Term>, com condição clínica,
        localidade e projeto como termos, sobre as 889 amostras finais do
        pipeline próprio. O metadado clínico usado veio de
        `metadata/metadata_master.tsv`, arquivo já presente na pasta do
        projeto desde a preparação inicial (colunas `sampleid`,
        `sample_accession`, `tipo_amostra`, `HPV`, `Center`, `Location`,
        `Project`), cruzado pelo `sampleid` contra as 889 amostras da
        tabela de gênero final, com correspondência perfeita nas 889
        linhas.
      </>
    ),
    commands: [
      `library(vegan)

tabela <- read.delim("export/genus_table_final/feature-table.tsv",
                      skip = 1, header = TRUE, row.names = 1,
                      check.names = FALSE)
tabela_t <- t(tabela)

metadata <- read.delim("metadata_final_889.tsv", header = TRUE,
                        stringsAsFactors = FALSE)
rownames(metadata) <- metadata$sampleid
metadata <- metadata[rownames(tabela_t), ]

dist_bc <- vegdist(tabela_t, method = "bray")
resultado <- adonis2(dist_bc ~ tipo_amostra + Location + Project,
                      data = metadata, permutations = 999, by = "margin")
print(resultado)`,
      {
        code: `              Df SumOfSqs      R2       F Pr(>F)
tipo_amostra   3     2.14 0.00593  2.2311  0.002 **
Location       0     0.00 0.00000     Inf
Project        5    33.18 0.09193 20.7474  0.001 ***
Residual     877   280.52 0.77715
Total        888   360.97 1.00000`,
        caption:
          "Resultado real, execução própria (889 amostras). Localidade saiu com 0 graus de liberdade porque é colinear com projeto de origem, cada projeto vem de um único país, e o R descarta o termo redundante. Condição clínica explicou 0,59% da variação (F = 2,23; p = 0,002) e projeto de origem explicou 9,19% (F = 20,75; p = 0,001), cerca de 15,5 vezes mais. Alvo de comparação, valores publicados no artigo: condição + localidade + projeto ≈ 13,5% da variação (F ≈ 12,8; p = 0,001); controle vs. câncer ≈ 5,0%. A distância na magnitude absoluta é esperada, dado que o pipeline próprio parte de 889 das 997 amostras e de uma reconstrução independente de todo o processamento bioinformático desde os FASTQ brutos, mas o padrão qualitativo central do artigo se confirma: o projeto de origem domina a variação composicional muito mais do que a condição clínica.",
      },
      {
        code: `pares <- list(c("control", "cancer"), c("lesion high", "cancer"),
              c("lesion low", "cancer"), c("lesion high", "lesion low"))

for (p in pares) {
  idx <- metadata$tipo_amostra %in% p
  sub_dist <- as.dist(dist_bc_matriz[idx, idx])
  sub_meta <- metadata[idx, ]
  sub_meta$tipo_amostra <- factor(sub_meta$tipo_amostra, levels = p)
  print(adonis2(sub_dist ~ tipo_amostra, data = sub_meta, permutations = 999))
}`,
        caption:
          "Resultado real, contraste par a par restrito a 2 classes por vez, removendo o confundimento com as outras condições clínicas: controle vs. câncer 6,52% (F = 43,36; p = 0,001; n = 624), HSIL vs. câncer 5,75% (F = 27,56; p = 0,001; n = 454), LSIL vs. câncer 4,44% (F = 18,93; p = 0,001; n = 409), HSIL vs. LSIL não significativo (F = 1,60; p = 0,107; n = 265). Os quatro contrastes ficam bem próximos das magnitudes publicadas no artigo (5,0%; 3,6%; 2,2%; não significativo com p = 0,067), inclusive reproduzindo qual par não é significativo, resultado mais próximo do publicado do que o modelo combinado de 3 termos, porque aqui o confundimento entre condição e projeto de origem é parcialmente controlado ao restringir a comparação a 2 classes por vez.",
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
        origem, sobre as 889 amostras finais do pipeline próprio. Dos 1.597
        gêneros da tabela final, filtrados para os 98 presentes em pelo
        menos 10% das amostras, faixa em que o ajuste multivariado do GLLVM
        se mantém tratável.
      </>
    ),
    commands: [
      `library(gllvm)

tabela <- read.delim("export/genus_table_final/feature-table.tsv",
                      skip = 1, header = TRUE, row.names = 1, check.names = FALSE)
tabela_t <- t(tabela)

metadata <- read.delim("metadata_final_889.tsv", header = TRUE, stringsAsFactors = FALSE)
rownames(metadata) <- metadata$sampleid
metadata <- metadata[rownames(tabela_t), ]

prevalencia <- colSums(tabela_t > 0) / nrow(tabela_t)
tabela_filtrada <- as.matrix(tabela_t[, prevalencia >= 0.10])
metadata$Project <- factor(metadata$Project)

modelo_sem <- gllvm(y = tabela_filtrada, family = "negative.binomial", num.lv = 2)
modelo_com <- gllvm(y = tabela_filtrada, X = metadata[, "Project", drop = FALSE],
                     formula = ~ Project, family = "negative.binomial", num.lv = 2)

escores <- getLV(modelo_sem)
d <- data.frame(LV1 = escores[, 1], LV2 = escores[, 2],
                tipo_amostra = factor(metadata$tipo_amostra),
                Project = metadata$Project)
summary(aov(LV1 ~ Project, data = d))
summary(aov(LV1 ~ tipo_amostra, data = d))
summary(aov(LV2 ~ Project, data = d))
summary(aov(LV2 ~ tipo_amostra, data = d))`,
      {
        code: `AIC (sem covariaveis): 313373
AIC (com projeto):     300307.4

LV1 ~ Project:       SumSq 499.6 de 880.8   (eta2 = 56,7%)  p < 2e-16
LV1 ~ tipo_amostra:  SumSq  97.6 de 880.8   (eta2 = 11,1%)  p < 2e-16
LV2 ~ Project:       SumSq 513.8 de 882.2   (eta2 = 58,2%)  p < 2e-16
LV2 ~ tipo_amostra:  SumSq  69.6 de 882.3   ( eta2 = 7,9%)  p = 1,1e-15`,
        caption:
          "Resultado real, execução própria (889 amostras, 98 gêneros filtrados por prevalência). O AIC cai bastante ao incluir projeto como efeito fixo, e os dois eixos latentes do modelo sem covariáveis são explicados majoritariamente por projeto de origem (56,7% e 58,2% da variância de cada eixo) e só marginalmente por condição clínica (11,1% e 7,9%), terceira confirmação independente do mesmo padrão central do artigo, depois do PERMANOVA na Etapa 7.",
      },
    ],
  },
  {
    n: 9,
    title: "Protocolo de validação (Random Forest)",
    note: (
      <>
        A etapa central declarada como trabalho em curso no artigo: comparar
        CV estratificada aleatória contra{" "}
        <Term id="looPo">leave-one-project-out</Term> com Random Forest, mais
        um <Term id="controleNegativo">controle negativo</Term> prevendo o
        projeto de origem a partir da composição, sobre as 889 amostras
        finais do pipeline próprio (abundância relativa por gênero, toda a
        tabela de 1.597 gêneros, sem filtro de prevalência).
      </>
    ),
    commands: [
      `library(ranger)
library(pROC)

tabela_rel <- tabela_t / rowSums(tabela_t)   # abundancia relativa por amostra
classes <- levels(metadata$tipo_amostra)
fazer_folds <- function(y, k) { ... }        # k folds estratificados por classe

# Esquema 1: CV estratificada aleatoria (10 folds)
folds_random <- fazer_folds(metadata$tipo_amostra, 10)
for (k in 1:10) {
  rf <- ranger(x = tabela_rel[folds_random != k, ],
               y = metadata$tipo_amostra[folds_random != k], probability = TRUE)
  # guarda predict(rf, tabela_rel[folds_random == k, ])$predictions
}

# Esquema 2: leave-one-project-out
for (p in levels(metadata$Project)) {
  rf <- ranger(x = tabela_rel[metadata$Project != p, ],
               y = metadata$tipo_amostra[metadata$Project != p], probability = TRUE)
  # guarda predict(rf, tabela_rel[metadata$Project == p, ])$predictions
}

# Controle negativo: prever o projeto a partir da composicao (10 folds)
for (k in 1:10) {
  rf <- ranger(x = tabela_rel[folds_proj != k, ], y = metadata$Project[folds_proj != k])
  # guarda predict(rf, tabela_rel[folds_proj == k, ])$predictions
}`,
      {
        code: `=== ESQUEMA 1: CV aleatoria estratificada ===
     cancer     control lesion high  lesion low
      0.959       0.815       0.760       0.710
Macro-AUC: 0.811

=== ESQUEMA 2: leave-one-project-out ===
     cancer     control lesion high  lesion low
      0.717       0.512       0.510       0.662
Macro-AUC: 0.6

=== CONTROLE NEGATIVO: prever projeto a partir da composicao ===
Acuracia: 0.8279`,
        caption:
          "Resultado real, execução própria (889 amostras, ranger com interface x/y, necessária porque os nomes de gênero da linhagem SILVA quebram a interface de fórmula do R). O macro-AUC cai de 0,811 na CV aleatória para 0,6 na validação leave-one-project-out, queda mais acentuada na classe câncer (0,959 para 0,717) e quase ao nível do acaso em controle e lesão alta (0,815 para 0,512; 0,760 para 0,510). O controle negativo prevê o projeto de origem com 82,79% de acurácia, bem acima do acaso para 9 classes (cerca de 11%), confirmando que a composição carrega assinatura de projeto de origem muito mais forte que assinatura clínica, mesmo padrão do preview exploratório da Tabela 2c (macro-AUC 0,838 na CV aleatória, 0,486 no LOPO, 90,4% de acurácia no controle negativo), agora obtido de forma independente sobre dado próprio.",
      },
    ],
  },
];

const AUDIT_AUC = [
  { classe: "câncer", treino: 1.0, cv: 0.966, projeto: 0.95, lopo: 0.701 },
  { classe: "controle", treino: 1.0, cv: 0.849, projeto: 0.846, lopo: 0.51 },
  { classe: "HSIL", treino: 1.0, cv: 0.763, projeto: 0.77, lopo: 0.458 },
  { classe: "LSIL", treino: 1.0, cv: 0.737, projeto: 0.787, lopo: 0.338 },
];

function AuditAucChart() {
  const fmt = (v: any) => Number(v).toFixed(2);
  return (
    <div className="fig-block" style={{ width: "100%", height: 340, margin: "32px 0" }}>
      <ResponsiveContainer>
        <BarChart data={AUDIT_AUC} margin={{ top: 20, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
          <XAxis dataKey="classe" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} label={{ value: "AUC", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip contentStyle={{ fontSize: 12 }} formatter={fmt} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="treino" fill="#c9b98a" name="Avaliado no treino" />
          <Bar dataKey="cv" fill="#5b7a9e" name="CV aleatória">
            <LabelList dataKey="cv" position="top" fontSize={10} formatter={fmt} />
          </Bar>
          <Bar dataKey="projeto" fill="#8a8370" name="Só o projeto, sem microbioma">
            <LabelList dataKey="projeto" position="top" fontSize={10} formatter={fmt} />
          </Bar>
          <Bar dataKey="lopo" fill="#a85b5b" name="Projeto novo (LOPO)">
            <LabelList dataKey="lopo" position="top" fontSize={10} formatter={fmt} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, textAlign: "center", color: "var(--ink-soft)", marginTop: 6, lineHeight: 1.5 }}>
        Fig. J. Mesmo Random Forest do artigo (500 árvores, 4 classes,
        abundância relativa por gênero) sobre a tabela da Paola (997
        amostras), mudando só a forma de validar. O AUC ≈ 1 do artigo só
        aparece avaliando no próprio treino. Um modelo que recebe só o
        código do projeto empata com o microbioma inteiro.
      </div>
    </div>
  );
}

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

        .fig-block { padding: 20px 16px 8px; background: var(--paper-soft, #faf7f0); border: 1px solid var(--rule-light); border-radius: 6px; }
        .recharts-responsive-container {
          display: block;
          width: 100%;
        }
        .recharts-legend-wrapper {
          position: relative !important;
          margin-top: 10px;
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
            <DatasetCompositionChart />
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

            <h3 style={{ fontSize: 15.5, marginBottom: 6 }}>Por que os primers importam numa meta-análise</h3>
            <p>
              Um <em>primer</em> (ou oligonucleotídeo iniciador) é uma
              sequência curta de DNA sintético usada na reação em cadeia da
              polimerase (PCR) pra selecionar e amplificar uma região
              específica do genoma dos micro-organismos presentes numa
              amostra{" "}
              <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7991656/" target="_blank" rel="noreferrer">[1]</a>
              <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7023036/" target="_blank" rel="noreferrer">[2]</a>
              . Na maioria dos estudos de microbioma baseados no gene 16S
              rRNA, os pesquisadores não sequenciam o genoma inteiro, mas
              sim uma região assinatura dentro dele. O gene 16S tem nove
              regiões hipervariáveis (V1 a V9), e a escolha do par de
              primers define qual delas será lida: pra ler a região V4, por
              exemplo, usa-se habitualmente o par 515F/806R; pra ler V3-V4,
              outro par, como os confirmados na Tabela 1b (seção 4){" "}
              <a href="https://www.mdpi.com/2076-2607/8/1/131" target="_blank" rel="noreferrer">[3]</a>
              <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7991656/" target="_blank" rel="noreferrer">[4]</a>
              <a href="https://onlinelibrary.wiley.com/doi/10.1111/1755-0998.13215" target="_blank" rel="noreferrer">[5]</a>
              .
            </p>
            <p>
              Quando uma meta-análise combina dados de estudos
              independentes, o primer usado em cada um vira uma fonte
              direta de <Term id="efeitoDeLote">efeito de lote</Term>, por
              três motivos principais{" "}
              <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC6708278/" target="_blank" rel="noreferrer">[6]</a>
              <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10989904/" target="_blank" rel="noreferrer">[7]</a>
              <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC12309989/" target="_blank" rel="noreferrer">[8]</a>
              :
            </p>
            <ol style={{ fontSize: 14, lineHeight: 1.7, paddingLeft: 20, marginBottom: 16 }}>
              <li>
                <strong>Abundância diferencial artificial:</strong> pares de
                primers diferentes têm afinidades diferentes por certos
                grupos de bactérias. Um par pode amplificar melhor
                Firmicutes, outro pode amplificar melhor Bacteroidetes na
                mesma amostra exata, distorcendo a proporção real da
                comunidade se os dados forem juntados sem correção.
              </li>
              <li>
                <strong>Pontos cegos taxonômicos:</strong> alguns primers
                universais falham em se ligar ao DNA de gêneros específicos
                (como Bifidobacterium), omitindo completamente a presença
                deles nos estudos que usaram esse par.
              </li>
              <li>
                <strong>Resolução de espécies:</strong> um primer voltado à
                V4 dá uma boa visão geral da comunidade, mas pode não
                diferenciar espécies tão bem quanto um primer voltado à
                V1-V3.
              </li>
            </ol>
            <p>
              As estratégias usuais pra lidar com isso incluem restringir a
              meta-análise a estudos que usaram exatamente o mesmo par de
              primer, aplicar correções bioinformáticas que tentam remover
              matematicamente o efeito de lote (pacotes como MMUPHin ou
              Melody), ou recorrer a sequenciamento shotgun, que evita esse
              viés específico por não depender de amplificação por primer{" "}
              <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7023036/" target="_blank" rel="noreferrer">[9]</a>
              <a href="https://link.springer.com/article/10.1186/s13059-025-03721-4" target="_blank" rel="noreferrer">[10]</a>
              <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC11334437/" target="_blank" rel="noreferrer">[11]</a>
              . O artigo aqui acompanhado não segue nenhuma dessas três
              saídas: ele mantém os primers diferentes entre projetos e usa
              o próprio efeito de lote resultante como objeto de estudo, daí
              a importância de documentar exatamente qual par cada
              BioProject usou (Tabela 1b) antes de qualquer análise
              estatística.
            </p>

            <h3 style={{ fontSize: 15.5, marginTop: 28, marginBottom: 6 }}>Glossário</h3>
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
              Duas etapas do pipeline próprio já estão concluídas: a
              confirmação dos primers por BioProject (Tabela 1b, seção 4) e o
              levantamento de accessions e metadados clínicos (Tabela 2b
              abaixo), este último a partir de <code>metadata.txt</code>,
              compartilhado pela coautora Paola Gyuliane Gonçalves, cuja
              contagem por projeto e por classe bate célula a célula com a
              Tabela I do artigo.
            </p>
            <p>
              O pipeline próprio já avançou de fato pela execução real no
              terminal, não só planejamento, e chegou a um dataset final
              agregado: os FASTQ brutos dos 10 BioProjects foram baixados,
              importados no QIIME 2, tiveram os primers cortados via
              cutadapt (Tabela 1c), passaram por denoising via deblur
              (V3-V4 com 93,5% de retenção, V4 com 99,8%), tiveram taxonomia
              atribuída via SILVA (com retreino local do classificador, ver
              Etapa 5) e foram filtrados e mesclados por gênero taxonômico
              (Etapa 6), resultando em <strong>889 amostras finais</strong>{" "}
              de um teto alcançável de 937 (89,2% das 997 publicadas no
              artigo, diferença explicada pela exclusão do P21). Sobre esse
              dataset final já foram rodados o PERMANOVA (Etapa 7), com
              condição clínica explicando 0,59% da variação e projeto de
              origem explicando 9,19%, cerca de 15,5 vezes mais, o GLLVM
              (Etapa 8), cujos dois eixos latentes também são dominados por
              projeto de origem (η² de 56,7% e 58,2%) e só marginalmente
              por condição clínica (11,1% e 7,9%), e o Random Forest
              (Etapa 9), cujo macro-AUC cai de 0,811 na CV aleatória para
              0,6 na validação leave-one-project-out, com o controle
              negativo prevendo o projeto de origem com 82,79% de acurácia.
              As três técnicas confirmam, de forma independente e sobre
              dado próprio, o mesmo padrão qualitativo do artigo: o pipeline
              próprio está com as quatro etapas estatísticas planejadas
              concluídas. Um{" "}
              <code>feature-table.txt</code> já processado também existe na
              mesma pasta do Drive, mas é o processamento da Paola, útil
              como dado de referência e para orientação exploratória
              (Tabela 2c), e não substitui o resultado do pipeline próprio.
            </p>
            <p style={{ fontSize: 13.5, borderLeft: "3px solid #a85b5b", paddingLeft: 12 }}>
              <strong>Correção (out/2026).</strong> O P22 (PRJNA725946) é
              V3-V4 (341F/806R, Tabela 1b), mas entrou no lote de deblur e
              no classificador da V4. As leituras começam em{" "}
              <code>TAGGGAATCTTCCACAATGG</code>, início de V3, e o
              classificador V4 deixou 79% delas sem gênero, com gêneros
              espúrios (<em>Dickeya</em> 9,6%, <em>Nocardia</em> 5,6%). O P22
              foi reprocessado a partir do SRA (<code>analysis/p22_v3v4.sh</code>):
              o deblur reproduziu exatamente as mesmas ASVs, então o único
              erro era o classificador. No caminho apareceu outro problema:
              no P22, as 65 amostras de câncer têm leituras de ~222 nt e os
              54 controles, ~274 nt, ou seja, foram sequenciados em corridas
              diferentes (por isso o corte de 220 nt, e por isso a
              profundidade sozinha separa as classes dentro do P22). Com o
              P22 reprocessado, o <code>permanova.R</code> dá condição 0,47%
              e projeto 6,36%. O <code>random_forest.R</code> também tinha um
              problema: o <code>pROC::roc()</code> usa direção automática e
              nunca devolve AUC abaixo de 0,5; com a direção fixa, o
              macro-AUC no LOPO é 0,457, não 0,6. O GLLVM ainda precisa ser
              refeito.
            </p>
            <table className="formal">
              <caption><span className="cap-label">Tabela 2.</span> Etapas do pipeline próprio e status atual.</caption>
              <thead><tr><th>Etapa</th><th>Status</th></tr></thead>
              <tbody>
                <tr><td>1. Accessions e metadados clínicos</td><td><span className="status-badge done">concluído</span></td></tr>
                <tr><td>2. Download dos FASTQ (10 BioProjects)</td><td><span className="status-badge done">concluído</span></td></tr>
                <tr><td>3a. Confirmação de primers por BioProject</td><td><span className="status-badge done">concluído (8/10; nota do P10 misto)</span></td></tr>
                <tr><td>3b. Import e corte de primers (cutadapt, 10 projetos)</td><td><span className="status-badge done">concluído</span></td></tr>
                <tr><td>4a. Deblur região V3-V4 (P1, P6, P14, P19)</td><td><span className="status-badge done">concluído (289/309, 93,5%)</span></td></tr>
                <tr><td>4b. Deblur região V4 (P2, P9, P10, P16, P22)</td><td><span className="status-badge partial">P22 reprocessado no ramo V3-V4 (corte 220); falta o classificador SILVA V3-V4</span></td></tr>
                <tr><td>5. Taxonomia SILVA (V3-V4 e V4)</td><td><span className="status-badge done">concluído (classificador retreinado localmente)</span></td></tr>
                <tr><td>6. Filtragem e fusão por gênero</td><td><span className="status-badge done">concluído (889 amostras finais de um teto de 937)</span></td></tr>
                <tr><td>7. PERMANOVA</td><td><span className="status-badge done">concluído (condição 0,59%, projeto 9,19%; com P22 reprocessado: 0,47% e 6,36%)</span></td></tr>
                <tr><td>8. GLLVM</td><td><span className="status-badge partial">refazer com P22 corrigido (antes: eixos dominados por projeto, η² 56,7% e 58,2%)</span></td></tr>
                <tr><td>9. Random Forest (CV aleatória vs. LOPO)</td><td><span className="status-badge done">refeito: com P22 reprocessado e direção da ROC fixa, macro-AUC 0,808 para 0,457; controle negativo 83,0%</span></td></tr>
                <tr><td>10. Auditoria de viés e comparação com a tabela da Paola</td><td><span className="status-badge done">concluído (seção 6; scripts em analysis/)</span></td></tr>
              </tbody>
            </table>
            <SampleFunnelChart />

            <h3 style={{ fontSize: 15, marginTop: 28 }}>
              Passo a passo real: do início ao Random Forest
            </h3>
            <p style={{ fontSize: 13.5 }}>
              Resumo cronológico de toda a execução real no terminal, do
              levantamento dos metadados clínicos até o fechamento das
              quatro etapas estatísticas finais, todos os números vindos
              do próprio pipeline, não do dado da Paola.
            </p>
            <ol style={{ fontSize: 13.5, lineHeight: 1.8, paddingLeft: 20 }}>
              <li>
                <strong>Accessions e metadados clínicos.</strong> O arquivo{" "}
                <code>metadata_master.tsv</code> (1.042 linhas, delimitado
                por tabulação) trouxe a contagem clínica por projeto: 314
                câncer, 170 HSIL, 112 LSIL e 446 controle, batendo célula a
                célula com a Tabela I do artigo. Essa é a base sobre a qual
                todo o restante do pipeline foi construído.
              </li>
              <li>
                <strong>Download e import dos FASTQ.</strong> Os FASTQ
                brutos dos 10 BioProjects foram baixados e importados no
                QIIME 2 via manifest (<code>SingleEndFastqManifestPhred33V2</code>,
                tabulado a despeito do nome ".csv"), separadamente por
                projeto, antes de qualquer corte de primer.
              </li>
              <li>
                <strong>Confirmação de primers e corte com cutadapt.</strong>{" "}
                8 dos 10 primers foram confirmados por cruzamento com o
                artigo-fonte de cada BioProject (Tabela 1b). No caminho,
                descobriu-se que P9, P14 e P2 já chegavam sem primer na
                origem, que o P19 precisou de correção empírica do par
                usado, e que o P10 usa o par original de Caporaso,
                diferente do par mais novo de P9/P16. P2 e P21 ficaram sem
                confirmação publicada, tratados nas notas metodológicas
                acima.
              </li>
              <li>
                <strong>O problema do P10.</strong> Ao montar o manifest
                combinado da região V4 (P2, P9, P10, P16, P22), o
                BioProject P10 se revelou misto: cerca de 154 amostras
                chegaram com o primer de fato presente nas leituras brutas
                e cerca de 165, faixas de accession
                ERR9391105-ERR9391228 e ERR9409855-ERR9409922, já sem
                primer na origem, igual ao caso de P9/P14/P2. As duas
                partes precisaram de corte de primer diferente e foram
                processadas separadamente como P10a e P10b antes de voltar
                a fazer parte da mesma tabela.
              </li>
              <li>
                <strong>O erro de ID duplicado.</strong> A primeira
                tentativa de juntar P10a e P10b no mesmo manifest falhou em{" "}
                <code>qiime tools import</code> com{" "}
                <code>Metadata IDs must be unique</code>, listando as
                mesmas 165 accessions duplicadas: P10a ainda continha
                leituras quase vazias pra essas IDs, e P10b continha as
                leituras reais das mesmas amostras. A correção foi excluir
                essas 165 IDs da exportação do P10a antes de montar o
                manifest combinado, deixando cada amostra aparecer uma
                única vez, na versão certa.
              </li>
              <li>
                <strong>Deblur da V4 fechado.</strong> Com o manifest
                corrigido (628 linhas de dados, 0 IDs duplicadas
                confirmado via <code>sort | uniq -d</code>), o{" "}
                <code>qiime deblur denoise-16S</code> rodou sem erro e
                reteve 627 das 628 amostras (99,8%), retenção equivalente à
                da região V3-V4 (289/309, 93,5%). Ver Fig. D.
              </li>
              <li>
                <strong>Taxonomia via SILVA.</strong> O classificador
                pré-treinado oficial não pôde ser usado por incompatibilidade
                de versão do scikit-learn entre o artefato (0.24.1) e o
                ambiente instalado (1.7.1). A correção foi baixar as
                referências brutas do SILVA 138, extrair as regiões
                amplificadas por par de primer (<code>extract-reads</code>)
                e retreinar um classificador Naive Bayes local por região
                (<code>fit-classifier-naive-bayes</code>), evitando o
                artefato incompatível.
              </li>
              <li>
                <strong>Filtragem, colapso e fusão.</strong> As ASVs de
                V3-V4 e V4 não são diretamente comparáveis entre si, então
                as duas tabelas foram limpas (organela e singleton
                removidos), colapsadas em gênero taxonômico e mescladas
                (<code>feature-table merge --p-overlap-method sum</code>).
                Com corte de profundidade em 1.000 leituras por amostra
                (testado também 500, rejeitado por só ganhar 16 amostras à
                custa de um corte menos defensável), o resultado final foi
                889 amostras, de um teto alcançável de 937.
              </li>
              <li>
                <strong>Cruzamento com o metadado clínico.</strong> As 889
                amostras da tabela final foram cruzadas pelo identificador
                de amostra contra <code>metadata/metadata_master.tsv</code>
                {" "}(1.042 linhas, colunas <code>sampleid</code>,{" "}
                <code>sample_accession</code>, <code>tipo_amostra</code>,{" "}
                <code>HPV</code>, <code>Center</code>, <code>Location</code>,{" "}
                <code>Project</code>), com correspondência perfeita nas 889
                linhas. As 4 classes clínicas reais: câncer (299), controle
                (325), lesão alta/HSIL (155) e lesão baixa/LSIL (110).
              </li>
              <li>
                <strong>PERMANOVA.</strong> Sobre Bray-Curtis, condição
                clínica explicou 0,59% da variação (F = 2,23; p = 0,002) e
                projeto de origem explicou 9,19% (F = 20,75; p = 0,001),
                cerca de 15,5 vezes mais; localidade saiu colinear com
                projeto, 0 graus de liberdade. Ver Fig. E.
              </li>
              <li>
                <strong>Contrastes par a par.</strong> Restringindo o
                PERMANOVA a 2 classes clínicas por vez, controle vs. câncer
                deu 6,52% (n = 624), HSIL vs. câncer 5,75% (n = 454), LSIL
                vs. câncer 4,44% (n = 409) e HSIL vs. LSIL não significativo
                (p = 0,107; n = 265), valores próximos aos publicados no
                artigo (5,0%; 3,6%; 2,2%; não significativo). Ver Fig. I.
              </li>
              <li>
                <strong>GLLVM.</strong> Sobre os 98 gêneros presentes em
                pelo menos 10% das amostras, o AIC caiu de 313.373 (sem
                covariáveis) para 300.307,4 (com projeto como efeito fixo).
                Os dois eixos latentes do modelo sem covariáveis são
                explicados majoritariamente por projeto de origem (η² de
                56,7% e 58,2%) e só marginalmente por condição clínica
                (11,1% e 7,9%). Ver Fig. G.
              </li>
              <li>
                <strong>Random Forest.</strong> Macro-AUC de 0,811 na CV
                estratificada aleatória cai para 0,6 na validação
                leave-one-project-out, queda mais acentuada na classe
                câncer (0,959 para 0,717). O controle negativo, prever o
                projeto de origem a partir da composição, acertou 82,79%
                das amostras, bem acima do acaso para 9 classes. Ver
                Fig. F.
              </li>
            </ol>
            <p style={{ fontSize: 13, fontStyle: "italic", marginTop: 8 }}>
              Um preview exploratório das Etapas 7 e 9 foi rodado sobre o{" "}
              <code>feature-table.txt</code> da Paola (Python: scikit-bio,
              scikit-learn, sem rarefação prévia), só para orientação,
              resultado na Tabela 2c. Não substitui a execução sobre dados
              processados pelo pipeline próprio, que é o que de fato conta
              para o trabalho.
            </p>

            <table className="formal">
              <caption><span className="cap-label">Tabela 2c.</span> Preview exploratório (dado da Paola, sem rarefação, não é resultado final).</caption>
              <thead><tr><th>Etapa</th><th>Métrica</th><th>Valor</th></tr></thead>
              <tbody>
                <tr><td rowSpan={3}>PERMANOVA marginal</td><td>Condição clínica (R²)</td><td>3,32%</td></tr>
                <tr><td>Localidade (R²)</td><td>5,09%</td></tr>
                <tr><td>Projeto (R²)</td><td>12,08%</td></tr>
                <tr><td rowSpan={2}>Random Forest, CV aleatória</td><td>Macro-AUC</td><td>0,838</td></tr>
                <tr><td>Por classe (cancer/control/HSIL/LSIL)</td><td>0,97 / 0,86 / 0,78 / 0,75</td></tr>
                <tr><td rowSpan={2}>Random Forest, leave-one-project-out</td><td>Macro-AUC</td><td>0,486 (≈ acaso)</td></tr>
                <tr><td>Por classe (cancer/control/HSIL/LSIL)</td><td>0,69 / 0,50 / 0,46 / 0,30</td></tr>
                <tr><td>Controle negativo</td><td>Acurácia ao prever projeto</td><td>90,4%</td></tr>
              </tbody>
            </table>
            <PermanovaChart />
            <AucComparisonChart />
            <p style={{ fontSize: 13.5, marginTop: 8 }}>
              O PERMANOVA foi refeito sobre o dado real do pipeline próprio
              (889 amostras finais, Etapa 6), com o metadado clínico da
              coautora Paola Gyuliane Gonçalves (`metadata_master.tsv`)
              cruzado pelo identificador de amostra, correspondência
              perfeita nas 889 linhas. Resultado na Fig. E.
            </p>
            <RealPermanovaChart />
            <p style={{ fontSize: 13.5, marginTop: 8 }}>
              O GLLVM (Etapa 8) também foi ajustado sobre o dado real do
              pipeline próprio, 98 gêneros presentes em pelo menos 10% das
              889 amostras. Resultado na Fig. G.
            </p>
            <RealGllvmChart />
            <p style={{ fontSize: 13.5, marginTop: 8 }}>
              O Random Forest (Etapa 9) também foi refeito sobre o dado real
              do pipeline próprio (889 amostras), abundância relativa por
              gênero, interface x/y do <code>ranger</code> pra evitar a
              quebra da fórmula do R com os nomes de linhagem do SILVA.
              Resultado na Fig. F.
            </p>
            <RealAucComparisonChart />
            <p style={{ fontSize: 13, fontStyle: "italic" }}>
              O padrão (projeto domina sobre condição clínica; desempenho
              despenca sob LOPO; projeto é previsível a partir da composição)
              confirma a hipótese do artigo, mas os números não são finais:
              vieram de dado de terceiros sem rarefação, não do pipeline
              próprio da autora.
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

            <h3 style={{ fontSize: 15, marginTop: 24 }}>
              Notas metodológicas para a redação
            </h3>
            <p style={{ fontSize: 13.5 }}>
              Dois pontos levantados durante a execução do pipeline próprio
              merecem registro explícito na seção de metodologia da
              dissertação, prontos para adaptação direta.
            </p>
            <p style={{ fontSize: 13.5 }}>
              <strong>Sobre a proveniência do primer de P2 e P21.</strong>{" "}
              Dos 10 BioProjects agregados, 8 tiveram o par de primer de
              amplificação 16S confirmado por cruzamento direto com o
              artigo-fonte ou seu material suplementar (Tabela 1b). Para P2
              e P21, essa confirmação não foi possível: os dois artigos
              informam apenas a região amplificada, V4 para P2 e V3-V4 para
              P21, e o fornecedor comercial responsável pelo sequenciamento
              (Second Genome Inc. para P2, Novogene para P21), mas nenhum
              dos dois publica a sequência de nucleotídeos do par de
              primer usado, tratado como protocolo proprietário pelo
              fornecedor. Na execução real, essa lacuna se resolveu por si
              só para P2, cujas leituras já chegaram sem primer na origem,
              o mesmo padrão de P9 e P14, então nenhuma suposição precisou
              ser adotada. P21 segue fora do pipeline agregado por falta de
              primer confirmado ou de uma suposição defensável, e é o
              principal responsável pela diferença entre as 889 amostras
              do pipeline próprio e as 997 publicadas no artigo (teto
              alcançável de 937 amostras sem o P21).
            </p>
            <p style={{ fontSize: 13.5 }}>
              <strong>Sobre a divergência do P16 entre trabalhos.</strong>{" "}
              O metadado clínico usado neste trabalho (compartilhado pela
              coautora Paola Gyuliane Gonçalves) registra 55 amostras de
              câncer para o BioProject P16, enquanto uma versão anterior do
              mesmo agregado, o TCC de M. T. S. Figueiredo (2025, referência
              [16] do artigo), registra 26. A contagem usada neste trabalho
              bate célula a célula com a Tabela I do artigo LATINOWARE, o
              que indica que a divergência não é um erro de transcrição
              deste pipeline, e sim uma atualização do BioProject de
              origem, ou um novo levantamento de amostras, entre a
              elaboração do TCC e a submissão do artigo. Vale registrar essa
              diferença como nota metodológica na dissertação, caso
              apareça alguma discrepância downstream ao comparar resultados
              com o TCC.
            </p>

            <h3 style={{ fontSize: 15, marginTop: 24 }}>O que falta até o final</h3>
            <ol style={{ fontSize: 13.5, lineHeight: 1.7, paddingLeft: 20 }}>
              <li>
                <strong>Classificar o P22 com o SILVA V3-V4</strong>: o P22 já
                foi reprocessado (<code>analysis/p22_v3v4.sh</code>), mas a
                taxonomia veio das ASVs V3-V4 já classificadas no pipeline;
                falta rodar o classificador no QIIME 2.
              </li>
              <li>
                <strong>Registrar o P14 nos Métodos</strong>: 21 das 43 runs
                (10 controles, 11 HSIL) não são 16S. Nos FASTQ do SRA nenhuma
                leitura tem o primer ou o início de V3, e as sequências mais
                comuns são humanas (Alu, satélite). A exclusão pelo cutadapt
                é correta; a tabela da Paola também não as tem.
              </li>
              <li>
                <strong>Refazer o GLLVM</strong> com a tabela corrigida.
              </li>
              <li>
                <strong>Alinhar com a Paola</strong> as incongruências da
                seção 6: P21 dentro ou fora, filtro de 1.000 leituras, DNA não
                bacteriano no P16 e a contagem total (997 na tabela, 1.008 no
                artigo).
              </li>
              <li>
                <strong>Etapa 4 fechada</strong>: o deblur das duas regiões
                está concluído, V3-V4 com 93,5% e V4 com 99,8% de retenção,
                depois de corrigir o manifest combinado da V4 pra excluir as
                165 IDs duplicadas do sublote sem primer do P10 antes de
                juntar com os dados reais dessas mesmas amostras (P10b).
              </li>
              <li>
                <strong>P2 tratado, P21 excluído</strong>: P2 acabou não
                precisando da suposição documentada (par EMP), porque na
                execução real ficou confirmado que o primer já vinha
                removido na origem, igual P9/P14, então todas as suas
                amostras entraram no pipeline normalmente. P21 segue fora,
                por falta de primer confirmado ou suposição plausível.
              </li>
              <li>
                <strong>Etapas 5 e 6 fechadas</strong>: taxonomia via SILVA
                (com retreino local do classificador, necessário por
                incompatibilidade de versão do scikit-learn) e filtragem
                com fusão por gênero taxonômico entre as duas regiões,
                resultando em 889 amostras finais, 89,2% das 997 publicadas,
                diferença majoritariamente explicada pela exclusão do P21
                (detalhes na Etapa 6).
              </li>
              <li>
                <strong>Etapa 7 fechada</strong>: PERMANOVA sobre Bray-Curtis
                a partir dos dados do pipeline próprio (889 amostras).
                Condição clínica explicou 0,59% da variação, projeto de
                origem explicou 9,19%, cerca de 15,5 vezes mais, e
                localidade saiu colinear com projeto (0 graus de liberdade).
                O padrão qualitativo do artigo se confirma sobre um dado
                independente, mesmo com magnitudes absolutas diferentes das
                publicadas.
              </li>
              <li>
                <strong>Etapa 8 fechada</strong>: GLLVM sobre os 98 gêneros
                mais prevalentes das 889 amostras. Os dois eixos latentes
                são explicados majoritariamente por projeto de origem
                (η² de 56,7% e 58,2%) e só marginalmente por condição
                clínica (11,1% e 7,9%), terceira confirmação independente do
                mesmo padrão central do artigo.
              </li>
              <li>
                <strong>Etapa 9 fechada</strong>: protocolo de validação
                Random Forest sobre as 889 amostras do pipeline próprio.
                Macro-AUC cai de 0,811 na CV estratificada aleatória para
                0,6 na validação leave-one-project-out, e o controle
                negativo prevê o projeto de origem a partir da composição
                com 82,79% de acurácia. Esta era a contribuição central
                declarada como "em andamento" no artigo, e o padrão se
                confirma sobre dado processado do zero pelo pipeline
                próprio, no mesmo sentido do preview exploratório
                (Tabela 2c) rodado sobre o dado da Paola.
              </li>
              <li>
                <strong>Contrastes par a par fechados</strong>: PERMANOVA
                restrito a 2 classes por vez reproduz de perto as
                magnitudes publicadas (controle vs. câncer 6,52% contra
                5,0%; HSIL vs. câncer 5,75% contra 3,6%; LSIL vs. câncer
                4,44% contra 2,2%; HSIL vs. LSIL não significativo nos
                dois), inclusive acertando qual par não chega a ser
                significativo.
              </li>
              <li>
                <strong>Fechamento</strong>: todas as quatro etapas
                estatísticas planejadas (PERMANOVA, GLLVM, Random Forest e
                os contrastes par a par) estão concluídas sobre as 889
                amostras do pipeline próprio, e as duas notas metodológicas
                pendentes (proveniência do primer de P2/P21 e divergência
                do P16 entre o TCC de 2025 e o artigo LATINOWARE) já estão
                redigidas, prontas para adaptação direta na seção de
                metodologia da dissertação. Com a auditoria de out/2026,
                entram também os três itens do início desta lista.
              </li>
            </ol>
            <PairwiseContrastsChart />

            <table className="formal">
              <caption><span className="cap-label">Tabela 3.</span> Valores publicados no paper, usados como alvo de comparação, e o obtido pelo pipeline próprio até aqui.</caption>
              <thead><tr><th>Métrica</th><th>Valor publicado</th><th>Pipeline próprio</th></tr></thead>
              <tbody>
                <tr><td>Amostras finais (de 1.042 catalogadas)</td><td>997</td><td>889 (89,2% do publicado; teto alcançável de 937 sem o P21)</td></tr>
                <tr><td>Variância explicada por condição clínica (R² marginal)</td><td>13,5% combinado (condição + localidade + projeto), F ≈ 12,8; p = 0,001</td><td>0,59% (F = 2,23; p = 0,002), só condição clínica</td></tr>
                <tr><td>Variância explicada por projeto de origem (R² marginal)</td><td>não isolado no artigo (modelo combinado)</td><td>9,19% (F = 20,75; p = 0,001), cerca de 15,5x a condição clínica</td></tr>
                <tr><td>Localidade</td><td>incluída no modelo combinado publicado</td><td>colinear com projeto, 0 graus de liberdade</td></tr>
                <tr><td>Eixos de ordenação (GLLVM), variância por fator</td><td>não reportado em η² no artigo</td><td>LV1 e LV2 dominados por projeto (η² 56,7% e 58,2%), condição clínica marginal (11,1% e 7,9%)</td></tr>
                <tr><td>Contraste controle vs. câncer</td><td>5,0% (F = 38,257; p = 0,001)</td><td>6,52% (F = 43,36; p = 0,001; n = 624)</td></tr>
                <tr><td>Contraste HSIL vs. câncer</td><td>3,6%</td><td>5,75% (F = 27,56; p = 0,001; n = 454)</td></tr>
                <tr><td>Contraste LSIL vs. câncer</td><td>2,2%</td><td>4,44% (F = 18,93; p = 0,001; n = 409)</td></tr>
                <tr><td>Contraste HSIL vs. LSIL</td><td>não significativo (p = 0,067)</td><td>não significativo (F = 1,60; p = 0,107; n = 265)</td></tr>
                <tr><td>Amostras com contraste de 4 classes identificável</td><td>245 (23,5%), só P2 e P19</td><td>6 projetos com mais de uma classe (P1, P2, P10, P14, P19, P22), de um total de 889 amostras</td></tr>
                <tr><td>Random Forest, macro-AUC CV aleatória vs. LOPO</td><td>não reportado nesse formato no artigo</td><td>0,811 (CV aleatória) para 0,6 (LOPO)</td></tr>
                <tr><td>Controle negativo, acurácia ao prever projeto</td><td>não reportado no artigo</td><td>82,79%</td></tr>
              </tbody>
            </table>
          </section>

          {/* 6 */}
          <section id="s4c" ref={(el) => { refs.current["s4c"] = el; }}>
            <h2 className="sec"><span className="sec-num">6.</span>Auditoria de viés e comparação com a Paola</h2>
            <p>
              Em out/2026 a tabela do pipeline próprio foi comparada com a
              tabela usada no artigo da coautora Paola Gyuliane Gonçalves
              (<code>feature-table.txt</code>, 997 amostras), e as
              conclusões do manuscrito foram testadas contra o viés de
              projeto de origem. Scripts e resultados em{" "}
              <code>analysis/</code>; relatório completo em{" "}
              <code>analysis/relatorio_vies.html</code>.
            </p>
            <AuditAucChart />
            <table className="formal">
              <caption><span className="cap-label">Tabela 5.</span> Mesmas análises nas duas tabelas (pipeline próprio com P22 reprocessado).</caption>
              <thead><tr><th>Análise</th><th>Paola</th><th>Pipeline próprio</th></tr></thead>
              <tbody>
                <tr><td>RF, CV aleatória (câncer / controle / HSIL / LSIL)</td><td>0,97 / 0,85 / 0,76 / 0,74</td><td>0,96 / 0,82 / 0,74 / 0,71</td></tr>
                <tr><td>RF, só o projeto como preditor</td><td>0,95 / 0,85 / 0,77 / 0,79</td><td>0,94 / 0,81 / 0,75 / 0,76</td></tr>
                <tr><td>RF, leave-one-project-out</td><td>0,70 / 0,51 / 0,46 / 0,34</td><td>0,64 / 0,44 / 0,48 / 0,35</td></tr>
                <tr><td>Acurácia ao prever o projeto (acaso)</td><td>88,1% (31,8%)</td><td>86,3% (35,2%)</td></tr>
                <tr><td>PERMANOVA: classe / projeto / classe além do projeto</td><td>7,1% / 16,4% / 0,4%</td><td>6,6% / 14,5% / 0,4%</td></tr>
                <tr><td>Shannon câncer − controle: sem / com ajuste por projeto</td><td>+0,97 (p &lt; 10⁻²⁶) / +0,09 (p = 0,43)</td><td>+1,00 / +0,14 (p = 0,23)</td></tr>
                <tr><td>30 combinações de classificador, câncer × controle (mediana)</td><td>CV 0,96; LOPO 0,70</td><td>CV 0,95; LOPO 0,64</td></tr>
                <tr><td>Meta-análise por projeto: gêneros que sobem em todos os estudos</td><td colSpan={2}>câncer: <em>Fusobacterium</em>, <em>Sneathia</em> (g ≈ 0,33, I² = 0%); HSIL: <em>Sneathia</em>, <em>Megasphaera</em>, <em>Atopobium</em>; LSIL: nenhum; <em>Lactobacillus</em> heterogêneo (I² = 86%)</td></tr>
                <tr><td>Remover 48 gêneros contaminantes de kit</td><td colSpan={2}>não muda o LOPO (câncer 0,63) nem a previsão do projeto (83–85%)</td></tr>
              </tbody>
            </table>
            <p style={{ fontSize: 13.5 }}>
              Os principais biomarcadores do artigo vêm, cada um, de
              praticamente um único projeto:{" "}
              <em>Burkholderia-Caballeronia-Paraburkholderia</em> (96% no
              P21, só controles), <em>Wolbachia</em> (100% no P1),{" "}
              <em>Aeribacillus</em> (100% no P9), <em>Halomonas</em> (95% no
              P9). Dentro dos projetos com câncer e controle, o que se
              repete é perda de <em>Lactobacillus</em> e ganho de{" "}
              <em>Fusobacterium</em> e <em>Prevotella</em>; o único projeto
              em que o sinal de câncer se transfere é o P19 (Nigéria, AUC ≈
              0,7–0,8). No P22, a profundidade de leitura sozinha separa
              câncer de controle (AUC 0,97), sinal de lote dentro do projeto.
            </p>
            <table className="formal">
              <caption><span className="cap-label">Tabela 6.</span> Incongruências entre a tabela da Paola e a do pipeline próprio.</caption>
              <thead><tr><th>Ponto</th><th>Paola (artigo)</th><th>Pipeline próprio</th><th>Corrigir</th></tr></thead>
              <tbody>
                <tr><td>P22</td><td>classificado corretamente</td><td>processado como V4; 79% sem gênero (Bray-Curtis 0,99 contra a Paola; 0,02 após reprocessar). Câncer e controle vêm de corridas diferentes (~222 vs. ~274 nt)</td><td><span className="status-badge partial">reprocessado; falta SILVA</span></td></tr>
                <tr><td>P21 (Espanha)</td><td>incluído: 103 controles + 2 HSIL</td><td>excluído (primer não publicado)</td><td><span className="status-badge partial">decisão conjunta</span></td></tr>
                <tr><td>Amostras com menos de 1.000 leituras</td><td>26 mantidas (mínimo de 2 leituras) em P19, P10, P9 e P14</td><td>filtradas</td><td><span className="status-badge notfound">Paola</span></td></tr>
                <tr><td>P16</td><td>29 amostras; mediana de 48% Unassigned + Eukaryota (provável DNA humano)</td><td>47 amostras; Bray-Curtis 0,49 nas 29 em comum. Metadados: 55; artigo: 26</td><td><span className="status-badge notfound">Paola</span></td></tr>
                <tr><td>P14, 21 runs que não são 16S (DNA humano)</td><td>5 com 2–4 leituras, 16 ausentes</td><td>descartadas pelo cutadapt</td><td><span className="status-badge done">exclusão correta; registrar</span></td></tr>
                <tr><td>Profundidade da mesma amostra</td><td>referência</td><td>P19 2,3×, P14 0,59×, P1 0,72× (demais 0,99–1,04×)</td><td><span className="status-badge partial">conferir</span></td></tr>
                <tr><td>P14 (Brasil)</td><td>13 HSIL / 14 controles</td><td>11 / 11 (artigo: 22 / 21)</td><td><span className="status-badge partial">as duas</span></td></tr>
                <tr><td>Total e cloroplasto</td><td>997 na tabela, 1.008 no artigo; "Chloroplast" no Boruta, ausente da tabela</td><td>889</td><td><span className="status-badge notfound">Paola</span></td></tr>
                <tr><td>Método</td><td>DADA2 no texto (pasta tem Deblur), SILVA completo, espécie, sem filtro de profundidade</td><td>Deblur por região, classificador por região, gênero, filtro de 1.000 leituras</td><td><span className="status-badge done">escolha de método</span></td></tr>
              </tbody>
            </table>
            <p style={{ fontSize: 13.5 }}>
              Com o mesmo esquema de validação, as duas tabelas ficam a
              0,01–0,03 de AUC uma da outra, e a correlação entre elas nos
              gêneros principais vai de 0,97 a 1,00. As diferenças de método
              mudam pouco; o que muda as conclusões é quais amostras e
              projetos entram (P21, P16 e amostras de baixa profundidade).
            </p>
          </section>

          <section id="s5" ref={(el) => { refs.current["s5"] = el; }}>
            <h2 className="sec"><span className="sec-num">7.</span>Por que isso importa pra tese</h2>
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
              <li>
                Fontes consultadas para a explicação sobre o papel dos
                primers em meta-análises de microbioma (seção 3):{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7991656/" target="_blank" rel="noreferrer">pmc.ncbi.nlm.nih.gov/articles/PMC7991656</a>
                ,{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7023036/" target="_blank" rel="noreferrer">PMC7023036</a>
                ,{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10989904/" target="_blank" rel="noreferrer">PMC10989904</a>
                ,{" "}
                <a href="https://journals.plos.org/plosone/article/file?id=10.1371/journal.pcbi.1000667&type=printable" target="_blank" rel="noreferrer">PLOS Comp. Biol. 10.1371/journal.pcbi.1000667</a>
                ,{" "}
                <a href="https://onlinelibrary.wiley.com/doi/10.1111/1755-0998.13215" target="_blank" rel="noreferrer">Mol. Ecol. Resour. 10.1111/1755-0998.13215</a>
                ,{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC9415448/" target="_blank" rel="noreferrer">PMC9415448</a>
                ,{" "}
                <a href="https://www.mdpi.com/2076-2607/8/1/131" target="_blank" rel="noreferrer">Microorganisms 8(1):131</a>
                ,{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC6708278/" target="_blank" rel="noreferrer">PMC6708278</a>
                ,{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC12309989/" target="_blank" rel="noreferrer">PMC12309989</a>
                ,{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10569954/" target="_blank" rel="noreferrer">PMC10569954</a>
                ,{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC12081361/" target="_blank" rel="noreferrer">PMC12081361</a>
                ,{" "}
                <a href="https://link.springer.com/article/10.1186/s13059-025-03721-4" target="_blank" rel="noreferrer">Genome Biology 10.1186/s13059-025-03721-4</a>{" "}
                (pacote Melody) e{" "}
                <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC11334437/" target="_blank" rel="noreferrer">PMC11334437</a>
                .
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
