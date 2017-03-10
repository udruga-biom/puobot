setwd("C:/Users/cotoj/Documents/PUO informacije o zahvatu PDF/")
# ID <- 1

for (url in tablica2$V5) {
  ime <- sub("^.*doc/(.*)$", "\\1", url) 
  download.file(url, destfile=paste0(ime, ".pdf"), mode = "wb")}
  # ID <- ID + 1
