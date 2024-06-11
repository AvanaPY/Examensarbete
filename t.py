import numpy as np
import matplotlib.pyplot as plt


ac1 = 0.95
ac2 = 0.09167
ac3 = 250

cg1 = 50
cg2 = 50

for u in range(25, 250, 25):
    results = []
    for _ in range(12*6):
        d_cg1 = -ac1 * cg1 + u
        d_cg2 = ac1 * cg1 - ac2 * cg2
        gg = ac3 * ac2 * cg2
        
        cg1 += d_cg1
        cg2 += d_cg2
        results.append((cg1, cg2, d_cg1, d_cg2, gg))
        u = 0
    
    y = [result[-1] for result in results]
    y = np.cumsum(y)

    x = range(len(y))
    plt.plot(x, y)
    
plt.tight_layout()
plt.show()