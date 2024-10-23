import networkx as nx
from networkx.generators import geometric
import numpy as np
import scipy

from sgis.refinement import Refinement, t_bfs, bfs, level_dominates
from sgis.treematcher import TreeMatcher
from sgis.util import geometric_mean, harmonic_mean
from sgis.vf2 import GraphMatcher

import time
import random
import math
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
    random.seed(314159)
    print("ntarget, vf2mean, vf2std, vf2time, refmean, refstd, reftime")
    NBENCH_ITER = 100
    P_EDGE = 0.1
    R_RATIO = 0.75

    for i in range(30, 70, 5):
        N_NODES = i
        vf2_expansions = []
        tree_expansions = []

        vf2_time = []
        tree_time = []

        for j in range(NBENCH_ITER):
            G, H = generate_benchmark_pair(N_NODES, P_EDGE, R_RATIO)
            logger.info(f"TEST {i}")
            logger.info(f"\tTarget nodes: {G.number_of_nodes()}")
            logger.info(f"\tTarget edges: {G.number_of_edges()}")
            logger.info(f"\tPattern nodes: {H.number_of_nodes()}")
            logger.info(f"\tPattern edges: {H.number_of_edges()}")

            GM = GraphMatcher(G, H)
            gm_result, delta = bench(GM.subgraph_is_isomorphic)
            vf2_time.append(delta)
            vf2_expansion = GM.n_expanded_nodes()
            vf2_expansions.append(vf2_expansion + 1)
            logger.info(f"\t VF2 Expansions: {vf2_expansion}")

            TM = TreeMatcher(G, H)
            tm_result, delta = bench(TM.subgraph_is_isomorphic)
            tree_time.append(delta)
            tree_expansion = TM.n_expanded_nodes()
            tree_expansions.append(tree_expansion + 1)
            logger.info(f"\t Refinement Expansions: {tree_expansion}")

            if tm_result != gm_result:
                print(f"BAD BATCH {i} {j}")

        gm_vf2 = geometric_mean(vf2_expansions)
        std_vf2 = scipy.stats.gstd(vf2_expansions)
        time_vf2 = geometric_mean(vf2_time)

        gm_tree = geometric_mean(tree_expansions)
        std_tree = scipy.stats.gstd(tree_expansions)
        time_tree = geometric_mean(tree_time)

        print(
            f"{i}, {gm_vf2}, {std_vf2}, {time_vf2}, {gm_tree}, {std_tree}, {time_tree}"
        )


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


# Counterexample no more
def counterexample():
    P = nx.path_graph(7)
    T = nx.path_graph(7)
    T.add_node("*")
    T.add_edge(0, "*")
    T.add_edge(3, "*")
    GM = GraphMatcher(T, P)
    TM = TreeMatcher(T, P)
    print(GM.subgraph_is_isomorphic())
    print(TM.subgraph_is_isomorphic())
    lva = bfs(P, 4)
    lvb = bfs(T, 3)
    print(lva, lvb, level_dominates(lvb, lva))
    print(P, T)


# Also counterexample no more, from the union bound
def cycle_counterexample():
    P = nx.path_graph(5)
    P.add_node("*")
    P.add_edge(1, "*")

    T = nx.cycle_graph(6)
    T.add_node("*")
    T.add_edge(0, "*")

    GM = GraphMatcher(T, P)
    TM = TreeMatcher(T, P)
    print(GM.subgraph_is_isomorphic())
    print(TM.subgraph_is_isomorphic())
    lva = bfs(P, 4)
    lvb = bfs(T, 3)
    print(lva, lvb, level_dominates(lvb, lva))
    print(P, T)


def test_refinement():
    random.seed(3141592)
    pattern = nx.drawing.nx_pydot.read_dot("graphs/zds_pattern.dot")
    target = nx.drawing.nx_pydot.read_dot("graphs/zds_target.dot")

    print(level_dominates(bfs(target, "0"), bfs(pattern, "0")))
    R = Refinement(target, pattern)


def random_refinement_test(target_size, target_density, target_pattern_ratio_cap):
    target = nx.binomial_graph(target_size, target_density)
    n = len(target)
    s = set(random.choices(range(n), k=int(n * target_pattern_ratio_cap)))
    sub = target.subgraph(s)
    largest_cc = max(nx.connected_components(sub), key=len)
    pattern = target.subgraph(largest_cc)

    nx.draw(target, pos=nx.spring_layout(target), with_labels=True)
    nx.draw(pattern, pos=nx.spring_layout(pattern), with_labels=True)


if __name__ == "__main__":
    # random_refinement_test(30, 0.1, 0.75)
    main()
