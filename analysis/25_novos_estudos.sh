#!/bin/sh
# Processa um estudo novo do SRA com o mesmo pipeline do P22 (ver p22_v3v4.sh), só a leitura R1.
# Uso: sh 25_novos_estudos.sh ESTUDO LISTA_DE_RUNS PASTA PRIMER_5 TRIM
#   PRIMER_5: sequência a cortar no início da R1 (cutadapt -g, descarta leituras sem ela),
#             ou "nenhum" quando as leituras já começam na região (primer removido no depósito).
#   TRIM:     comprimento do deblur (250 para V3-V4 e 220 para V4, como no pipeline da Tassiane).
# Requer sra-tools, cutadapt e deblur 1.1.1 no PATH (variáveis ENV_BIN e DEBLUR_BIN).
#
# Primers encontrados nas leituras (ver 25_novos_estudos.py):
#   PRJNA1085021  341F CCTAYGGGRBGCASCAG + 806R (V3-V4)      -> PRIMER_5=CCTAYGGGRBGCASCAG TRIM=220 (leituras de 227 nt após o primer)
#   PRJNA308947   454, leituras começam em GGAGGCAGCAG (fim do 338F/341F) -> PRIMER_5=GGAGGCAGCAG TRIM=250
#   PRJNA622998   leituras já começam no V4 (TACG...)        -> PRIMER_5=nenhum TRIM=220
#   PRJEB40437    27F (V1-V3), processado à parte             -> PRIMER_5=GAGTTTGATCMTGGCTCAG TRIM=250
#   PRJEB43410    kit Ion 16S com várias regiões misturadas  -> não processado
set -e
EST=$1; IDS=$2; W=$3; PRIMER=$4; TRIM=$5
DIR=$(cd "$(dirname "$0")" && pwd)
PATH="$ENV_BIN:$PATH"
mkdir -p "$W/$EST/sra" "$W/$EST/qf" "$W/$EST/log"

um() {
  id=$1
  [ -s "$W/$EST/qf/$id.fastq" ] && return 0
  t="$W/$EST/sra/$id"
  mkdir -p "$t"
  curl -s --retry 4 -o "$t/$id.sra" "https://sra-pub-run-odp.s3.amazonaws.com/sra/$id/$id" || { echo "$id download falhou" >> "$W/$EST/log/erros.txt"; return 0; }
  fasterq-dump --split-files -e 1 -O "$t" "$t/$id.sra" > /dev/null 2>&1 || fasterq-dump -e 1 -O "$t" "$t/$id.sra" > /dev/null 2>&1
  r1=$(ls "$t"/*_1.fastq 2>/dev/null || ls "$t"/*.fastq | head -1)
  if [ "$PRIMER" = "nenhum" ]; then
    cp "$r1" "$t/trim.fastq"
  else
    cutadapt -g "$PRIMER" --discard-untrimmed -e 0.15 -O 10 -o "$t/trim.fastq" "$r1" > "$W/$EST/log/$id.cutadapt.txt"
    # Algumas runs foram depositadas já sem o primer (no PRJEB40437, 134 de 245 começam logo
    # depois do 27F). Se menos de 10% das leituras têm o primer, usa a leitura como está.
    n_in=$(($(wc -l < "$r1") / 4)); n_out=$(($(wc -l < "$t/trim.fastq") / 4))
    if [ "$n_in" -gt 0 ] && [ $((n_out * 10)) -lt "$n_in" ]; then
      cp "$r1" "$t/trim.fastq"
      echo "$id sem primer: usada sem corte" >> "$W/$EST/log/sem_primer.txt"
    fi
  fi
  python3 "$DIR/qfilter_q2.py" "$t/trim.fastq" "$W/$EST/qf/$id.fastq"
  rm -rf "$t"
}

export -f um 2>/dev/null || true
while read id; do
  um "$id" &
  # até 3 runs ao mesmo tempo
  while [ "$(jobs -r | wc -l)" -ge 3 ]; do sleep 1; done
done < "$IDS"
wait

PATH="$DEBLUR_BIN:$PATH" deblur workflow --seqs-fp "$W/$EST/qf" --output-dir "$W/$EST/deb" --trim-length "$TRIM" \
  --min-reads 10 --min-size 2 --mean-error 0.005 --indel-prob 0.01 --indel-max 3 -O 4 -w
echo "pronto: $W/$EST/deb"
