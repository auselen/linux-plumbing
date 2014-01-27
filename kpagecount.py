#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import subprocess
import os
import argparse

WIDTH = 256
WAIT = 1000

arg_parser = argparse.ArgumentParser(description="Visualizes /proc/kpagecount")
arg_parser.add_argument("-a", "--android", action='store_true',
                        help="use adb to retrieve information")
arg_parser.add_argument("-w", "--width", type=int,
                        help="set bar width, default is " + str(WIDTH), default=WIDTH)
arg_parser.add_argument("-d", "--delay", type=int,
                        help="milliseconds between updates, default is " + str(WAIT), default=WAIT)
args = arg_parser.parse_args()

WIDTH = args.width

if args.android == False and os.getuid() != 0:
    arg_parser.print_help()
    print("\nNeeds root permission to access vm information!\n")
    raise SystemExit

kpagecount_prev = None
plotted = False
while True:
    if args.android:
        subprocess.call(["adb", "pull", "/proc/kpagecount", "."], stderr=open(os.devnull, 'wb'))
    else:
        subprocess.call(["cp", "/proc/kpagecount", "."])
    f = open("kpagecount", "r")
    kpagecount = np.fromfile(f, dtype=np.int64)
    f.close()

    if args.android:
        subprocess.call(["adb", "pull", "/proc/kpageflags", "."], stderr=open(os.devnull, 'wb'))
    else:
        subprocess.call(["cp", "/proc/kpageflags", "."])
    f = open("kpagecount", "r")
    kpageflags = np.fromfile(f, dtype=np.uint64)
    f.close()

#    kpagecount = np.clip(kpagecount, 0, np.iinfo(np.int64).max)
    kpagecount = kpagecount.astype(np.float32)
#    kpagecount /= np.max(kpagecount)
    kpagecount = np.append(kpagecount, np.zeros((WIDTH - kpagecount.size % WIDTH,), dtype=np.float32))
    kpagecount = np.reshape(kpagecount, (-1, WIDTH))
    kpc_norm = colors.Normalize(vmin=0, clip=True)

#    kpageflags_colors = np.empty_like(cm.rainbow)
#    kpageflags_colors = np.recarray([(0, cm.rainbow(0))])
#    kpageflags_uniq = np.unique(kpageflags)
#    for i in kpageflags_uniq:
#        kpageflags_colors[i] = cm.rainbow(1.*i/64)

    kpageflags = np.append(kpageflags, np.zeros((WIDTH - kpageflags.size % WIDTH,), dtype=np.float32))
    kpageflags = np.reshape(kpageflags, (-1, WIDTH))

    kpagediff_colors = np.empty_like(cm.rainbow)
    kpagediff_colors = np.append(kpagediff_colors, cm.rainbow(0))
    for i in range(16):
        kpagediff_colors = np.append(kpagediff_colors, cm.rainbow(0)[0]+i*10)
    kpagediff_cm = colors.ListedColormap(
        ('black', 'gray', 'brown', 'blue', 'red', 'green', 'yellow', 'purple', 'white'), 
                                         name='kpagediff_cm')
    kpd_norm = colors.Normalize(vmin=0, vmax=9, clip=True)

    if kpagecount_prev is None:
        kpagecount_prev = kpagecount
    kpagecount_update = kpagecount - kpagecount_prev
    kpagecount_update = kpagecount_update.astype(np.int32)
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
        p_update = plt.imshow(kpagecount_update, kpagediff_cm, norm=kpd_norm)
        plt.colorbar(p_update)
        plt.gcf()
        #plt.clim()   # clamp the color limits
        plotted = True
    else:
        plt.gcf()
        p_count.set_data(kpagecount)
        p_update.set_data(kpagecount_update)
        p_flags.set_data(kpageflags)
    plt.pause(args.delay/1000.)
