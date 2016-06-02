
library(gridExtra)
library(ggplot2)
library(plyr)  

showData <- function()
{
    data <- read.csv('output.csv', sep=";", header=T)


    lastStep <- subset(data, step==max(data$step))
    maxRow <- lastStep[lastStep$size==max(lastStep$size),]

    g1 <- ggplot(data, aes(x=step, y=size, group=site)) + geom_line()
    g2 <- ggplot(lastStep, aes(x=size)) + geom_density()
    g3 <- ggplot(lastStep, aes(x=site, y=size)) + geom_point()

    grid.arrange(g1,g2,g3)
    return(maxRow)
}

print(showData())

