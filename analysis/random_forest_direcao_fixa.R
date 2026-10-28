# Cópia de random_forest.R (Drive da Tassiane) com uma única mudança: direction = "<" no pROC::roc().
# Sem isso o pROC escolhe a direção automaticamente e nunca devolve AUC < 0,5,
# o que esconde classificadores piores que o acaso (ex.: LSIL no leave-one-project-out).

library(ranger)
library(pROC)

set.seed(42)

tabela <- read.delim("export/genus_table_final/feature-table.tsv",
                      skip = 1, header = TRUE, row.names = 1, check.names = FALSE)
tabela_t <- t(tabela)
tabela_rel <- as.matrix(tabela_t / rowSums(tabela_t))

metadata <- read.delim("metadata_final_889.tsv", header = TRUE, stringsAsFactors = FALSE)
rownames(metadata) <- metadata$sampleid
metadata <- metadata[rownames(tabela_rel), ]
metadata$tipo_amostra <- factor(metadata$tipo_amostra)
metadata$Project <- factor(metadata$Project)

n <- nrow(tabela_rel)
classes <- levels(metadata$tipo_amostra)

fazer_folds <- function(y, k) {
  folds <- integer(length(y))
  for (nivel in levels(y)) {
    idx <- which(y == nivel)
    idx <- sample(idx)
    grupos <- rep(1:k, length.out = length(idx))
    folds[idx] <- grupos
  }
  folds
}

## ESQUEMA 1: CV estratificada aleatoria (10 folds), prevendo tipo_amostra
folds_random <- fazer_folds(metadata$tipo_amostra, 10)
prob_random <- matrix(NA, n, length(classes), dimnames = list(NULL, classes))

for (k in 1:10) {
  idx_treino <- folds_random != k
  idx_teste  <- folds_random == k
  rf <- ranger(x = tabela_rel[idx_treino, ], y = metadata$tipo_amostra[idx_treino],
               probability = TRUE, num.trees = 500)
  pred <- predict(rf, tabela_rel[idx_teste, ])$predictions
  prob_random[idx_teste, colnames(pred)] <- pred
}

auc_random <- sapply(classes, function(c) {
  y_bin <- as.numeric(metadata$tipo_amostra == c)
  as.numeric(auc(roc(y_bin, prob_random[, c], quiet = TRUE, direction = "<")))
})
cat("=== ESQUEMA 1: CV aleatoria estratificada ===\n")
print(round(auc_random, 3))
cat("Macro-AUC:", round(mean(auc_random), 3), "\n\n")

## ESQUEMA 2: leave-one-project-out, prevendo tipo_amostra
projetos <- levels(metadata$Project)
prob_lopo <- matrix(NA, n, length(classes), dimnames = list(NULL, classes))

for (p in projetos) {
  idx_treino <- metadata$Project != p
  idx_teste  <- metadata$Project == p
  rf <- ranger(x = tabela_rel[idx_treino, ], y = metadata$tipo_amostra[idx_treino],
               probability = TRUE, num.trees = 500)
  pred <- predict(rf, tabela_rel[idx_teste, ])$predictions
  prob_lopo[idx_teste, colnames(pred)] <- pred
}

auc_lopo <- sapply(classes, function(c) {
  y_bin <- as.numeric(metadata$tipo_amostra == c)
  tryCatch(as.numeric(auc(roc(y_bin, prob_lopo[, c], quiet = TRUE, direction = "<"))), error = function(e) NA)
})
cat("=== ESQUEMA 2: leave-one-project-out ===\n")
print(round(auc_lopo, 3))
cat("Macro-AUC:", round(mean(auc_lopo, na.rm = TRUE), 3), "\n\n")

## CONTROLE NEGATIVO: prever o projeto de origem a partir da composicao
folds_proj <- fazer_folds(metadata$Project, 10)
pred_projeto <- factor(rep(NA, n), levels = levels(metadata$Project))

for (k in 1:10)





{
  idx_treino <- folds_proj != k
  idx_teste  <- folds_proj == k
  rf <- ranger(x = tabela_rel[idx_treino, ], y = metadata$Project[idx_treino], num.trees = 500)
  pred_projeto[idx_teste] <- predict(rf, tabela_rel[idx_teste, ])$predictions
}

acc_projeto <- mean(pred_projeto == metadata$Project)
cat("=== CONTROLE NEGATIVO: prever projeto a partir da composicao ===\n")
cat("Acuracia:", round(acc_projeto, 4), "\n")

resultado <- list(auc_random = auc_random, auc_lopo = auc_lopo, acc_projeto = acc_projeto)
saveRDS(resultado, "rf_resultado_direcao_fixa.rds")
