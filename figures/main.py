import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def timeseries(ifname, xlabel, ylabel):
    df = pd.read_csv(ifname)
    raw = df.to_numpy()
    print(df)
    clean = raw[:, 0:]
    cols = np.array(df.columns)
    fig, ax = plt.subplots()
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    for i in range(clean.shape[0]):
        ax.plot(cols, clean[i])

def main():
    timeseries("data/out10.csv", "# of vertices", "Harmonic mean of expanded nodes")
    plt.savefig("data/figures/fig10.png")
    
    timeseries("data/out02.csv", "# of vertices", "Harmonic mean of expanded nodes")
    plt.savefig("data/figures/fig2.png")

if __name__ == "__main__":
    main()
