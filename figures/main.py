import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def expansion_plot(ifname, xlabel, ylabel):
    df = pd.read_csv(ifname)
    raw = df.to_numpy()
    print(df)
    clean = raw[:, 0:]
    cols = np.array(df.columns)
    fig, ax = plt.subplots()
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.errorbar(cols, clean[0], yerr=clean[2])
    ax.errorbar(cols, clean[1], yerr=clean[3])


def time_plot(ifname, xlabel, ylabel):
    df = pd.read_csv(ifname)
    raw = df.to_numpy()
    print(df)
    clean = raw[:, 0:]
    cols = np.array(df.columns)
    fig, ax = plt.subplots()
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.plot(cols, clean[4])
    ax.plot(cols, clean[5])

def main():
    # timeseries("data/out10.csv", "# of vertices", "Harmonic mean of expanded nodes")
    # plt.savefig("data/figures/fig10.png")
    
    time_plot("data/out02.csv", "# of vertices", "Mean wall clock time")
    plt.savefig("data/figures/fig10.png")

if __name__ == "__main__":
    main()
