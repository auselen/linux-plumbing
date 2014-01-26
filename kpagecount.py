#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import subprocess

ANDROID = False

WIDE = 512
kpagecount_prev = None
plotted = False
while True:
    if ANDROID:
        subprocess.call(["adb", "pull", "/proc/kpagecount", "."])
    else:
        subprocess.call(["cp", "/proc/kpagecount", "."])
    f = open("kpagecount", "r")
    kpagecount = np.fromfile(f, dtype=np.int64)
    f.close()

    if ANDROID:
        subprocess.call(["adb", "pull", "/proc/kpageflags", "."])
    else:
        subprocess.call(["cp", "/proc/kpageflags", "."])
    f = open("kpagecount", "r")
    kpageflags = np.fromfile(f, dtype=np.uint64)
    f.close()

#    kpagecount = np.clip(kpagecount, 0, np.iinfo(np.int64).max)
    kpagecount = kpagecount.astype(np.float32)
#    kpagecount /= np.max(kpagecount)
    kpagecount = np.append(kpagecount, np.zeros((WIDE - kpagecount.size % WIDE,), dtype=np.float32))
    kpagecount = np.reshape(kpagecount, (-1, WIDE))
    kpc_norm = colors.Normalize(vmin=0, clip=True)

#    kpageflags_colors = np.empty_like(cm.rainbow)
#    kpageflags_colors = np.recarray([(0, cm.rainbow(0))])
#    kpageflags_uniq = np.unique(kpageflags)
#    for i in kpageflags_uniq:
#        kpageflags_colors[i] = cm.rainbow(1.*i/64)

    kpageflags = np.append(kpageflags, np.zeros((WIDE - kpageflags.size % WIDE,), dtype=np.float32))
    kpageflags = np.reshape(kpageflags, (-1, WIDE))

    if kpagecount_prev is None:
        kpagecount_prev = kpagecount
    kpagecount_update = kpagecount - kpagecount_prev
    kpagecount_prev = np.copy(kpagecount)

    if plotted == False:
        plt.subplot(1, 3, 1)
        plt.title("kpageflags")
        p_flags = plt.imshow(kpageflags, cm.prism)
        plt.colorbar(p_flags)
        plt.subplot(1, 3, 2)
        plt.title("kpagecount")
        p_count = plt.imshow(kpagecount, cm.spectral, norm=kpc_norm)
        plt.colorbar(p_count)
        plt.subplot(1, 3, 3)
        plt.title("update")
        p_update = plt.imshow(kpagecount_update, cm.flag, norm=kpc_norm)
        plt.colorbar(p_update)
        plt.gcf()
        #plt.clim()   # clamp the color limits
        plotted = True
    else:
        plt.gcf()
        p_count.set_data(kpagecount)
        p_update.set_data(kpagecount_update)
        p_flags.set_data(kpageflags)
    plt.pause(1)
