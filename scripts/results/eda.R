
library(ggplot2)

myData <- read.csv('fooabc.csv', sep=";", header=T)
best100 <- myData[1:100,]

# alpha-beta

svg('alpha-beta.svg')
ggplot(best100, aes(x=alpha, y=beta, col=weight)) + geom_point()
dev.off()

# harbour
svg('density_harbour.svg')    
ggplot(best100, aes(x=harbourBonus, col=weight)) + geom_density() 
dev.off()

# prom-farming
svg('intrinsic.svg')    
ggplot(best100, aes(x=weight, fill=weight)) + geom_histogram()
dev.off()  
