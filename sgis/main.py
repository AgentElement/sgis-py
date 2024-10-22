import networkx as nx
import numpy as np
import scipy

from sgis.refinement import Refinement, bfs
from sgis.treematcher import TreeMatcher 
from sgis.util import geometric_mean, harmonic_mean
from sgis.vf2 import GraphMatcher

import time
import random
import math
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='compare.log', level=logging.INFO)

def bench(fn, *args, **kwargs):
    init_time = time.time_ns()
    result = fn(*args, **kwargs)
    final_time = time.time_ns()
    delta = final_time - init_time
    logger.info(f"Benchmark for {str(fn)}: {delta} ns")
    return result, delta


def generate_benchmark_pair(target_size, target_density, target_pattern_ratio_cap):
    target = nx.binomial_graph(target_size, target_density)
    n = len(target)
    s = set(random.choices(range(n), k=int(n * target_pattern_ratio_cap)))
    sub = target.subgraph(s)
    largest_cc = max(nx.connected_components(sub), key=len)
    pattern = target.subgraph(largest_cc)

    return target, pattern


def validate():
    random.seed(3141592)

    N_NODES = 100
    P_EDGE = 0.02
    R_RATIO = 0.7

    G, H = generate_benchmark_pair(N_NODES, P_EDGE, R_RATIO)

    GM = GraphMatcher(G, H)
    print(GM.subgraph_is_isomorphic())


def main():
    random.seed(3141592)

    vf2_standard_dev = []
    vf2_means = []
    vf2_times = []

    tree_means = []
    tree_standard_dev = []
    tree_times = []

    for i in range(30, 105, 5):

        NBENCH_ITER = 100
        N_NODES = i
        P_EDGE = 0.02
        R_RATIO = 0.75

        vf2_expansions = []
        tree_expansions = []

        vf2_time = []
        tree_time = []

        for i in range(NBENCH_ITER):
            G, H = generate_benchmark_pair(N_NODES, P_EDGE, R_RATIO)
            logger.info(f"TEST {i}")
            logger.info(f"\tTarget nodes: {G.number_of_nodes()}")
            logger.info(f"\tTarget edges: {G.number_of_edges()}")
            logger.info(f"\tPattern nodes: {H.number_of_nodes()}")
            logger.info(f"\tPattern edges: {H.number_of_edges()}")

            GM = GraphMatcher(G, H)
            result, delta = bench(GM.subgraph_is_isomorphic)
            vf2_time.append(delta)
            vf2_expansion = GM.n_expanded_nodes()
            vf2_expansions.append(vf2_expansion + 1)
            logger.info(f"\t VF2 Expansions: {vf2_expansion}")
            
            TM = TreeMatcher(G, H)
            result, delta = bench(TM.subgraph_is_isomorphic)
            tree_time.append(delta)
            tree_expansion = TM.n_expanded_nodes()
            tree_expansions.append(tree_expansion + 1)
            logger.info(f"\t Refinement Expansions: {tree_expansion}")

        vf2_means.append(geometric_mean(vf2_expansions))
        vf2_standard_dev.append(scipy.stats.gstd(vf2_expansions))
        vf2_times.append(geometric_mean(vf2_time))

        tree_means.append(geometric_mean(tree_expansions))
        tree_standard_dev.append(scipy.stats.gstd(tree_expansions))
        tree_times.append(geometric_mean(tree_time))

    print(",".join([f"{i}" for i in range(30, 105, 5)]))
    print(",".join([f"{i}" for i in vf2_means]))
    print(",".join([f"{i}" for i in tree_means]))
    print(",".join([f"{i}" for i in vf2_standard_dev]))
    print(",".join([f"{i}" for i in tree_standard_dev]))
    print(",".join([f"{i}" for i in vf2_times]))
    print(",".join([f"{i}" for i in tree_times]))


def test_treematching():
    G = nx.cycle_graph(5)
    H = nx.path_graph(4)
    print(f"\tTarget nodes: {G.number_of_nodes()}")
    print(f"\tTarget edges: {G.number_of_edges()}")
    print(f"\tPattern nodes: {H.number_of_nodes()}")
    print(f"\tPattern edges: {H.number_of_edges()}")

    GM = GraphMatcher(G, H)
    result, delta = bench(GM.subgraph_is_isomorphic)
    print(result)
    print(f"\t VF2 Expansions: {GM.n_expanded_nodes()}")
    
    GM = TreeMatcher(G, H)
    result, delta = bench(GM.subgraph_is_isomorphic)
    print(result)
    print(f"\t Refinement Expansions: {GM.n_expanded_nodes()}")

def test_refinement():
    random.seed(3141592)
    pattern = nx.drawing.nx_pydot.read_dot('graphs/zds_pattern.dot')
    target = nx.drawing.nx_pydot.read_dot('graphs/zds_target.dot')
    
    test = nx.drawing.nx_pydot.read_dot('graphs/octagon_subdivided.dot')
    print(test)

    print(bfs(test, '0'))
    R = Refinement(target, pattern)


if __name__ == '__main__':
    main()

