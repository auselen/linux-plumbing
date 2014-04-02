#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import subprocess
import os
import argparse
from hilbert import hilbert_curve

WIDTH = 256
WAIT = 1000

arg_parser = argparse.ArgumentParser(description="Visualizes /proc/kpagecount")
arg_parser.add_argument("-a", "--android", action='store_true',
                        help="use adb to retrieve information")
arg_parser.add_argument("-w", "--width", type=int,
                        help="set bar width, default is " + str(WIDTH), default=WIDTH)
arg_parser.add_argument("-d", "--delay", type=int,
                        help="milliseconds between updates, default is " + str(WAIT)
                        + " and no delay on Android", default=-1)
arg_parser.add_argument("-f", "--flags", metavar='flag', type=int, nargs='*',
                        help="filter for kpageflags")
arg_parser.add_argument("-v", "--verbose", action='store_true',
                        help="be verbose")
args = arg_parser.parse_args()

WIDTH = args.width
if args.delay > -1:
    WAIT = args.delay
elif args.android == True:
    WAIT = 1

if args.android == False and os.getuid() != 0:
    arg_parser.print_help()
    print("\nNeeds root permission to access vm information on PC and 'adb root' on Android!\n")
    raise SystemExit

kpagecount_prev = None
plotted = False
while True:
    if args.android:
        if args.verbose:
            print "Getting data via 'adb pull'"
        subprocess.call(["adb", "pull", "/proc/kpagecount", "."], stderr=open(os.devnull, 'wb'))
        kpagecount = np.fromfile("kpagecount", dtype=np.int64)
    else:
        if args.verbose:
            print "Reading from '/proc'"
        subprocess.call(["cp", "/proc/kpagecount", "."], stderr=open(os.devnull, 'wb'))
        kpagecount = np.fromfile("kpagecount", dtype=np.int64)

    if args.android:
        subprocess.call(["adb", "pull", "/proc/kpageflags", "."], stderr=open(os.devnull, 'wb'))
        kpageflags = np.fromfile("kpageflags", dtype=np.uint64)
    else:
        subprocess.call(["cp", "/proc/kpageflags", "."], stderr=open(os.devnull, 'wb'))
        kpageflags = np.fromfile("kpageflags", dtype=np.uint64)

    if args.verbose:
        print " done."

    # filter kpageflags
    if args.flags:
        mask = 0
        for f in args.flags:
            mask |= 1 << f
        kpageflags = np.bitwise_and(kpageflags, mask)

    # reshape so it can be a rectangle
    kpagecount_data = np.append(kpagecount, np.zeros((WIDTH - kpagecount.size % WIDTH,), dtype=np.int64))
    kpagecount = np.reshape(kpagecount_data, (-1, WIDTH))
    hilbert_curve(kpagecount_data, t=kpagecount, N=256)
    kpageflags_data = np.append(kpageflags, np.zeros((WIDTH - kpageflags.size % WIDTH,), dtype=np.uint64))
    kpageflags = np.reshape(kpageflags_data, (-1, WIDTH))
    hilbert_curve(kpageflags_data, t=kpageflags, N=256)
    #hilbert_curve(kpageflags_data, t=kpageflags, N=256, offset=65536, t_offset=[0, 256])

    kpageflags_bounds = np.unique(kpageflags)
    kpageflags_bounds = np.append(kpageflags_bounds, kpageflags_bounds[-1] + np.uint64(1))
    kpageflags_colors = ['black']
    cm = plt.get_cmap('gist_rainbow')
    for i in range(kpageflags_bounds.size):
        color = cm(1. * i / (kpageflags_bounds.size))
        kpageflags_colors.append(color)
#    np.random.shuffle(kpageflags_colors)
    kpageflags_cm = colors.ListedColormap(kpageflags_colors)
    kpageflags_norm = colors.BoundaryNorm(kpageflags_bounds, kpageflags_bounds.size)
    kpageflags_str = []
    for b in np.nditer(kpageflags_bounds):
        s = ""
        for i in range(64):
            if b & np.uint64(1 << i):
                s += "LERUDlASWIBMasbHTGuXnxtrmdPpOhcIPAE______________________________"[i]
        kpageflags_str.append(s)

    kpagecount_bounds = np.unique(kpagecount)
    kpagecount_bounds = np.append(kpagecount_bounds, kpagecount_bounds[-1] + 1)
    kpagecount_colors = ['white', 'black', 'yellow']
    cm = plt.get_cmap('gist_rainbow')
    for i in range(kpagecount_bounds.size):
        color = cm(1. * i / kpagecount_bounds.size)
        kpagecount_colors.append(color)
    kpagecount_cm = colors.ListedColormap(kpagecount_colors)
    kpagecount_norm = colors.BoundaryNorm(kpagecount_bounds, kpagecount_bounds.size)

    if kpagecount_prev is None:
        kpagecount_prev = np.zeros_like(kpagecount)
    kpagecount_update = kpagecount - kpagecount_prev
    kpagecount_prev = np.copy(kpagecount)

    kpageupdate_bounds = np.unique(kpagecount_update)
    kpageupdate_bounds = np.append(kpageupdate_bounds, kpageupdate_bounds[-1] + 1)
    kpageupdate_colors = ['black']
    cm = plt.get_cmap('gist_rainbow')
    for i in range(kpageupdate_bounds.size):
        color = cm(1. * i / kpageupdate_bounds.size)
        kpageupdate_colors.append(color)
    kpageupdate_cm = colors.ListedColormap(kpageupdate_colors)
    kpageupdate_norm = colors.BoundaryNorm(kpageupdate_bounds, kpageupdate_bounds.size)

    plt.clf()
    plt.subplot(1, 3, 1)
    plt.title("kpageflags")
    p_flags = plt.imshow(kpageflags, kpageflags_cm,
                         norm=kpageflags_norm, interpolation='nearest')
    cbar = plt.colorbar(p_flags)
    cbar.set_ticks(kpageflags_bounds)
    cbar.set_ticklabels(kpageflags_str)

    plt.subplot(1, 3, 2)
    plt.title("kpagecount")
    p_count = plt.imshow(kpagecount, kpagecount_cm,
                         norm=kpagecount_norm, interpolation='nearest')
    plt.colorbar(p_count)

    plt.subplot(1, 3, 3)
    plt.title("update")
    p_update = plt.imshow(kpagecount_update, kpageupdate_cm,
                          norm=kpageupdate_norm, interpolation='nearest')
    plt.colorbar(p_update)

    plt.gcf()

    if args.verbose:
        print "Waiting for " + str(WAIT/1000.) + " seconds"
    plt.pause(WAIT/1000.)
