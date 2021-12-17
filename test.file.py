import numpy as np
from numpy.core.fromnumeric import sort

# taken with corrections in https://pubmed.ncbi.nlm.nih.gov/19695002/

standard_error = (np.log(3.48)-np.log(1.75))/1.96
median = np.exp(np.log(1.75)-(0.5*standard_error*standard_error))

def generate2():
    return np.random.lognormal(np.log(median), np.log(standard_error))
vals2 = [generate2() for i in range(100000)]

import matplotlib.pyplot as plt

plt.hist(vals2, bins = 1000)
plt.show()

np.mean(vals2)

vals2.sort()


plt.hist(x, bins = 1000)
plt.show()


