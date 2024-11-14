import networkx as nx
import scipy

from sgis.rolloutmatcher import GraphMatcher
from sgis.util import geometric_mean

import time
import random
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="compare.log", level=logging.INFO)


def bench(fn, *args, **kwargs):
    init_time = time.time_ns()
    result = fn(*args, **kwargs)
    final_time = time.time_ns()
    delta = final_time - init_time
    logger.info(f"Benchmark for {str(fn)}: {delta} ns")
    return result, delta


def generate_weighted_benchmark_pair(
    target_size, target_density, target_pattern_ratio_cap
):
    target = nx.binomial_graph(target_size, target_density)
    for u, v in target.edges:
        target[u][v]["weight"] = random.random()
        #  d['weight'] = random.random()
    n = len(target)
    s = set(random.choices(range(n), k=int(n * target_pattern_ratio_cap)))
    sub = target.subgraph(s)
    largest_cc = max(nx.connected_components(sub), key=len)
    pattern = target.subgraph(largest_cc)

    return target, pattern


# Stuff put in the document before the serious graphs (see below)
def old_results():
    # C_5 is isompophic to the subgraph induced by the 'outer' vertices of the
    # Petersen graph
    random.seed(3141592)
    for i in range(4):
        print(f"ITERATION {i}")
        N = 100
        P = 0.02
        R = 0.7
        G, H = generate_weighted_benchmark_pair(N, P, R)
        print(G.number_of_nodes())
        print(G.number_of_edges())
        print(H.number_of_nodes())
        print(H.number_of_edges())

        GM = GraphMatcher(G, H)
        (hcost, _), htime = bench(GM.heuristic_isomorphism)
        (bcost, _), btime = bench(GM.best_isomorphism)
        (rcost, _), rtime = bench(GM.rollout_isomorphism)
        print(hcost, bcost, rcost)
        print(htime, btime, rtime)


# About as horrible as it gets, really.
def main():
    random.seed(314159)
    # target sizes,
    # times (in ns), time standard deviations
    # cost, cost standard deviation
    print(
        "ntarget,htime,btime,rtime,htstd,btstd,rtstd,hcost,bcost,rcost,hcstd,bcstd,rcstd"
    )
    NBENCH_ITER = 100
    P_EDGE = 0.10
    R_RATIO = 0.75

    for i in range(30, 130, 5):
        N_NODES = i

        hcosts = []
        bcosts = []
        rcosts = []
        htimes = []
        btimes = []
        rtimes = []

        for j in range(NBENCH_ITER):
            G, H = generate_weighted_benchmark_pair(N_NODES, P_EDGE, R_RATIO)
            GM = GraphMatcher(G, H)
            logger.info(f"TEST {i}")
            logger.info(f"\tTarget nodes: {G.number_of_nodes()}")
            logger.info(f"\tTarget edges: {G.number_of_edges()}")
            logger.info(f"\tPattern nodes: {H.number_of_nodes()}")
            logger.info(f"\tPattern edges: {H.number_of_edges()}")

            (hcost, _), htime = bench(GM.heuristic_isomorphism)
            (bcost, _), btime = bench(GM.best_isomorphism)
            (rcost, _), rtime = bench(GM.rollout_isomorphism)

            hcosts.append(hcost)
            bcosts.append(bcost)
            rcosts.append(rcost)

            htimes.append(htime)
            btimes.append(btime)
            rtimes.append(rtime)

        htime = geometric_mean(htimes)
        btime = geometric_mean(btimes)
        rtime = geometric_mean(rtimes)

        htstd = scipy.stats.gstd(htimes)
        btstd = scipy.stats.gstd(btimes)
        rtstd = scipy.stats.gstd(rtimes)

        hcost = geometric_mean(hcosts)
        bcost = geometric_mean(bcosts)
        rcost = geometric_mean(rcosts)

        hcstd = scipy.stats.gstd(hcosts)
        bcstd = scipy.stats.gstd(bcosts)
        rcstd = scipy.stats.gstd(rcosts)

        print(
            f"{i},{htime},{btime},{rtime},{htstd},{btstd},{rtstd},{hcost},{bcost},{rcost},{hcstd},{bcstd},{rcstd}"
        )


if __name__ == "__main__":
    main()
