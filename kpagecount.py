#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import subprocess

WIDE = 1024
kpagecount_prev = None
plotted = False
while True:
    subprocess.call(["cp", "/proc/kpagecount", "."])
    f = open("kpagecount", "r")
    kpagecount = np.fromfile(f, dtype=np.int64)
    f.close()

    kpagecount = np.clip(kpagecount, 0, np.iinfo(np.int64).max)
    kpagecount = kpagecount.astype(np.float32)
    kpagecount /= np.max(kpagecount)
    kpagecount = np.append(kpagecount, np.zeros((WIDE - kpagecount.size % WIDE,), dtype=np.float32))
    kpagecount = np.reshape(kpagecount, (-1, WIDE))

    if kpagecount_prev is None:
        kpagecount_prev = kpagecount
    kpagecount_diff = kpagecount - kpagecount_prev
    kpagecount_prev = np.copy(kpagecount)

    if plotted == False:
        plt.subplot(211)
        plt.title("kpagecount")
        p = plt.imshow(kpagecount, cm.gist_stern)
        plt.subplot(212)
        plt.title("update")
        p2 = plt.imshow(kpagecount_diff, cm.binary)
        fig = plt.gcf()
        plt.clim()   # clamp the color limits
        plotted = False
    else:
        p.set_data(kpagecount)
        p2.set_data(kpagecount_diff)
    plt.pause(1)
