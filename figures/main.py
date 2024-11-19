import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def expansion_plot(ifname, xlabel, ylabel, ax):
    df = pd.read_csv(ifname)
    raw = df.to_numpy()
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.errorbar(df["ntarget"], df["vf2mean"], yerr=df["vf2std"], label="\\verb|vf2|", linewidth=0.8)
    ax.errorbar(df["ntarget"], df["refmean"], yerr=df["refstd"], label="Our solver", linewidth=0.8)
    ax.legend()


def time_plot(ifname, xlabel, ylabel, ax):
    df = pd.read_csv(ifname)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.plot(df["ntarget"], df["vf2time"], label="\\verb|vf2|", linewidth=0.8)
    ax.plot(df["ntarget"], df["reftime"], label="Our solver", linewidth=0.8)
    ax.legend()


def error_plot(ifname, xlabel, ylabel, ax):
    df = pd.read_csv(ifname)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.plot(df["ntarget"], df["vf2mean"], label="\\verb|vf2|", linewidth=0.8)
    ax.plot(df["ntarget"], df["refmean"], label="Outdegree levels", linewidth=0.8)
    eax = ax.twinx()
    eax.plot(df["ntarget"], df["accuracy"], label="accuracy", color="red")
    eax.set_ylim(ymin=0)
    ax.legend()
    eax.legend()


def rollout_cost_plot(ifname, xlabel, ylabel, ax):
    df = pd.read_csv(ifname)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.plot(df["ntarget"], df["hcost"], label="Greedy Cost", linewidth=0.8)
    ax.plot(df["ntarget"], df["bcost"], label="Optimal Cost", linewidth=0.8)
    ax.plot(df["ntarget"], df["rcost"], label="Rollout Cost", linewidth=0.8)
    ax.legend()


def rollout_time_plot(ifname, xlabel, ylabel, ax):
    df = pd.read_csv(ifname)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_yscale("log", base=10)
    ax.errorbar(df["ntarget"], df["htime"], df["htstd"], label="Greedy Time", linewidth=0.8)
    ax.errorbar(df["ntarget"], df["btime"], df["btstd"], label="Optimal Time", linewidth=0.8)
    ax.errorbar(df["ntarget"], df["rtime"], df["rtstd"], label="Rollout Time", linewidth=0.8)
    ax.legend()


def p002_r75_tINF_LP():
    plt.rcParams.update({"text.usetex": True, "font.family": "Times New Roman"})
    fig, axs = plt.subplots(1, 1, sharex=True)
    error_plot(
        "data/out_p002_r75_tINF_LP.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.02$",
        "Vertex pairs expanded by search\n\\small{Geometric mean of $k = 100$ graphs}",
        axs,
    )
    plt.savefig("data/figures/f_p002_r75_tINF_LP.png", dpi=192)


def p010_r75_tINF_LP():
    pass

def p002_r75_tINF_UP():
    plt.rcParams.update({"text.usetex": True, "font.family": "Times New Roman"})
    fig, axs = plt.subplots(2, 1, sharex=True)
    expansion_plot(
        "data/out_p002_r75_tINF_UP.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.02$",
        "Vertex pairs expanded by search\n\\small{Geometric mean of $k = 100$ graphs)", 
        axs[0]
    )
    time_plot(
        "data/out_p002_r75_tINF_UP.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.02$",
        "Wall clock time (ns)\n\\small{Geometric mean of $k = 100$ graphs}",
        axs[1],
    )
    plt.savefig("data/figures/f_p002_r75_tINF_UP.png", dpi=192)

def p010_r75_tINF_UP():
    plt.rcParams.update({"text.usetex": True, "font.family": "Times New Roman"})
    fig, axs = plt.subplots(2, 1, sharex=True)
    expansion_plot(
        "data/out_p010_r75_tINF_UP.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.10$",
        "Vertex pairs expanded by search\n\\small{Geometric mean of $k = 100$ graphs)", 
        axs[0]
    )
    time_plot(
        "data/out_p010_r75_tINF_UP.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.10$",
        "Wall clock time (ns)\n\\small{Geometric mean of $k = 100$ graphs}",
        axs[1],
    )
    plt.savefig("data/figures/f_p010_r75_tINF_UP.png", dpi=192)

def p002_r75_tINF_CP():
    plt.rcParams.update({"text.usetex": True, "font.family": "Times New Roman"})
    fig, axs = plt.subplots(2, 1, sharex=True)
    expansion_plot(
        "data/out_p002_r75_tINF_CP.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.02$",
        "Vertex pairs expanded by both searches\n\\small{Geometric mean of $k = 100$ graphs)", 
        axs[0]
    )
    time_plot(
        "data/out_p002_r75_tINF_CP.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.02$",
        "Wall clock time (ns)\n\\small{Geometric mean of $k = 100$ graphs}",
        axs[1],
    )
    plt.savefig("data/figures/f_p002_r75_tINF_CP.png", dpi=192)

def rollout():
    plt.rcParams.update({"text.usetex": True, "font.family": "Times New Roman"})
    fig, axs = plt.subplots(2, 1, sharex=True)
    rollout_cost_plot(
        "data/rollout_largetargets.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.10$",
        "Normalized isomorphism weight\n\\small{Geometric mean of $k=20$ graphs}",
        axs[0]
    )
    rollout_time_plot(
        "data/rollout_largetargets.csv",
        "Number of vertices in random $G(n, p)$, $n$ varying and $p = 0.10$",
        "Wall clock time (ns)\n\\small{Geometric mean of $k = 20$ graphs}",
        axs[1]
    )
    plt.savefig("data/figures/rollout_smalltargets.png", dpi=192)

if __name__ == "__main__":
    p002_r75_tINF_LP()
    p002_r75_tINF_UP()
    p010_r75_tINF_UP()
    p002_r75_tINF_CP()
    rollout()
