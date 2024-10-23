import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def expansion_plot(ifname, xlabel, ylabel, ax):
    df = pd.read_csv(ifname)
    raw = df.to_numpy()
    print(df)
    clean = raw[:, 0:]
    cols = np.array(df.columns)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.errorbar(cols, clean[0], yerr=clean[2], label='vf2')
    ax.errorbar(cols, clean[1], yerr=clean[3], label='ours')
    ax.legend()


def time_plot(ifname, xlabel, ylabel, ax):
    df = pd.read_csv(ifname)
    raw = df.to_numpy()
    clean = raw[:, 0:]
    cols = np.array(df.columns)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.plot(cols, clean[4], label='vf2')
    ax.plot(cols, clean[5], label='ours')
    ax.legend()


def main():
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'Times New Roman'
    })
    # timeseries("data/out10.csv", "# of vertices", "Harmonic mean of expanded nodes")
    # plt.savefig("data/figures/fig10.png")

    fig, axs = plt.subplots(2, 1, sharex=True)
    time_plot("data/out10.csv", "", "Wall clock time (ns)\n(geometric mean)", axs[0])
    expansion_plot(
        "data/out10.csv", "Number of vertices", "Vertex pairs expanded\n(geometric mean)", axs[1]
    )
    plt.savefig("data/figures/fig10.", dpi=192)


if __name__ == "__main__":
    main()
