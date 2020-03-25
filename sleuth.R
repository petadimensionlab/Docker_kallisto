rm( list=ls(all=TRUE) ) # clean up R workspace
library("sleuth")

setwd("/tmp/wk")

base_dir <- "/tmp/wk/k_results"

sample_id <- dir(file.path(base_dir))
kal_dirs <- file.path(base_dir, sample_id)

s2c <- read.table(file.path("/tmp/wk/sample_table.txt"), header = TRUE, stringsAsFactors=FALSE)
s2c <- dplyr::mutate(s2c, path = kal_dirs)

so <- sleuth_prep(s2c, extra_bootstrap_summary = TRUE)

so <- sleuth_fit(so, ~condition, 'full')

so <- sleuth_fit(so, ~1, 'reduced')

so <- sleuth_lrt(so, 'reduced', 'full')

models(so)


sleuth_table <- sleuth_results(so, 'reduced:full', 'lrt', show_all = FALSE)
sleuth_significant <- dplyr::filter(sleuth_table, qval <= 0.05)
#head(sleuth_significant, 20)

out.name <- paste('sleuth_significant.txt',sep="")
write.table(sleuth_significant,out.name,row.names=F,col.names=,sep="\t",quote=F)


gene <- "ENST00000344120"

target_id <- sleuth_significant[grep(gene,sleuth_significant$target_id), 1]
target_id

out.pdfname <- paste("test_", gene,".pdf", sep = "")
pdf(out.pdfname,width = 6, height = 5)
plot_bootstrap(so, target_id[1], units = "est_counts", color_by = "condition")
de
