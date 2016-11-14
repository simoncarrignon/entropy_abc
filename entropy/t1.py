import abcpmc
import numpy as np

##Copy of abcpmc test scripts

#create "observed" data set
size = 5000
sigma = np.eye(4) * 0.25
means = np.array([1.1, 1.5, 1.1, 1.5])
data = np.random.multivariate_normal(means, sigma, size)
print (data)
#-------

#distance function: sum of abs mean differences
def dist(x, y):
    return np.sum(np.abs(np.mean(x, axis=0) - np.mean(y, axis=0)))

#our "model", a gaussian with varying means
def postfn(theta):
    return np.random.multivariate_normal(theta, sigma, size)

eps = abcpmc.LinearEps(10, 5, 0.75)
prior = abcpmc.GaussianPrior(means*1.1, sigma*2) #our best guess

sampler = abcpmc.Sampler(N=10, Y=data, postfn=postfn, dist=dist)

for pool in sampler.sample(prior, eps):
    print("T: {0}, eps: {1:>.4f}, ratio: {2:>.4f}".format(pool.t, pool.eps, pool.ratio))
    for i, (mean, std) in enumerate(zip(np.mean(pool.thetas, axis=0), np.std(pool.thetas, axis=0))):
        print(u"    theta[{0}]: {1:>.4f} \u00B1 {2:>.4f}".format(i, mean,std))

