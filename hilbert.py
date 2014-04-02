#!/usr/bin/env python

import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def hilbert_curve(a, N=None, offset=0, t=None, t_offset=[0, 0]):
    p = a.size / (N*N)
    if N is None:
        N = np.sqrt(a.size).astype(int)
    if t is None:
        t = np.empty([N*p, N], a.dtype)
    for i in range(N*N):
        x, y = d2xy(N, i)
        for j in range(p):
            t[y + j*N, x] = a[i + j*N*N]
    return t

#from wikipedia
def d2xy(n, d):
    x = y = 0
    s = 1
    while (s < n):
        rx = 1 & (d / 2)
        ry = 1 & (d ^ rx)
        # rotate
        if ry == 0:
            if rx == 1:
                x = s - 1 - x
                y = s - 1 - y
            x, y = y, x
        x += s * rx
        y += s * ry
        d /= 4
        s *= 2
    return x, y

#kpageflags = np.fromfile("kpageflags", dtype=np.int64)
#kf_uniq = np.unique(kpageflags)
#j = 0
#for i in kf_uniq:
#    kpageflags[kpageflags == i] = j
#    j = j + 1
#kpageflags = hilbert_curve(kpageflags, N=256)
#im = plt.imshow(kpageflags, interpolation='nearest', cmap=cm.gist_rainbow)
#plt.colorbar(im)
#plt.show()

#a = np.arange(int(sys.argv[1]))
#c = hilbert_curve(a)
#print c

