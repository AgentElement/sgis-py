import networkx as nx
from sgis.refinement import Refinement
from sgis.treematcher import TreeMatcher 
from sgis.util import harmonic_mean
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

    vf2_means = []
    tree_means = []

    for i in range(30, 105, 5):

        NBENCH_ITER = 100
        N_NODES = i
        P_EDGE = 0.02
        R_RATIO = 0.75

        t_bench = 0
        n_bench = 0

        vf2_expansions = []
        tree_expansions = []

        for i in range(NBENCH_ITER):
            G, H = generate_benchmark_pair(N_NODES, P_EDGE, R_RATIO)
            logger.info(f"TEST {i}")
            logger.info(f"\tTarget nodes: {G.number_of_nodes()}")
            logger.info(f"\tTarget edges: {G.number_of_edges()}")
            logger.info(f"\tPattern nodes: {H.number_of_nodes()}")
            logger.info(f"\tPattern edges: {H.number_of_edges()}")

            GM = GraphMatcher(G, H)
            result, delta = bench(GM.subgraph_is_isomorphic)
            t_bench += delta
            vf2_expansion = GM.n_expanded_nodes()
            vf2_expansions.append(vf2_expansion + 1)
            logger.info(f"\t VF2 Expansions: {vf2_expansion}")
            
            TM = TreeMatcher(G, H)
            result, delta = bench(TM.subgraph_is_isomorphic)
            t_bench += delta
            tree_expansion = TM.n_expanded_nodes()
            tree_expansions.append(tree_expansion + 1)
            logger.info(f"\t Refinement Expansions: {tree_expansion}")

        vf2_means.append(harmonic_mean(vf2_expansions))
        tree_means.append(harmonic_mean(tree_expansions))

    print(",".join([f"{i}" for i in range(30, 105, 5)]))
    print("vf2", ",".join([f"{i}" for i in vf2_means]))
    print("tree_means", ",".join([f"{i}" for i in tree_means]))


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

    R = Refinement(target, pattern)
    R.print_refinement()


if __name__ == '__main__':
    main()

