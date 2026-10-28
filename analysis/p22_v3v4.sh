#!/bin/sh
# Reprocessamento do P22 (PRJNA725946) no ramo V3-V4, fora do QIIME 2.
# Requer: sra-tools, cutadapt 5.x, deblur 1.1.1 (bioconda) e python3.
# Uso: sh p22_v3v4.sh ids_p22.txt pasta_de_trabalho
set -e
IDS=$1
W=$2
mkdir -p "$W/sra" "$W/fq" "$W/trim" "$W/qf"
DIR=$(cd "$(dirname "$0")" && pwd)

# 1. download do espelho público do SRA na AWS
while read id; do
  [ -s "$W/fq/${id}_1.fastq" ] && continue
  curl -s --retry 4 -o "$W/sra/$id.sra" "https://sra-pub-run-odp.s3.amazonaws.com/sra/$id/$id"
  fasterq-dump --split-files -e 2 -O "$W/fq" "$W/sra/$id.sra" && rm -f "$W/sra/$id.sra"
done < "$IDS"

# 2. corte do primer 341F (descarta leituras sem primer) e 3. filtro de qualidade
while read id; do
  cutadapt -g CCTAYGGGRBGCASCAG --discard-untrimmed -e 0.1 -o "$W/trim/$id.fastq" "$W/fq/${id}_1.fastq" > "$W/trim/$id.log"
  python3 "$DIR/qfilter_q2.py" "$W/trim/$id.fastq" "$W/qf/$id.fastq"
done < "$IDS"

# 4. deblur; corte de 220 porque as amostras de câncer do P22 têm leituras de ~222 nt (ver 08b)
deblur workflow --seqs-fp "$W/qf" --output-dir "$W/deb" --trim-length 220 \
  --min-reads 10 --min-size 2 --mean-error 0.005 --indel-prob 0.01 --indel-max 3 -O 4 -w

echo "Depois: P22_DEBLUR_DIR=$W/deb python 08b_reprocessa_p22.py"
