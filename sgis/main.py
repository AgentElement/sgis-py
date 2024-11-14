import networkx as nx
from networkx.generators import geometric
import numpy as np
import scipy

from sgis.refinement import Heuristic, Refinement, level_dominates, outdegree_bfs
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


def test_graphmatcher(G, H):
    GM = GraphMatcher(G, H)
    result, delta = bench(GM.subgraph_is_isomorphic)
    expansions = GM.n_expanded_nodes()
    logger.info(f"\t VF2 Expansions: {expansions}")
    return result, expansions, delta


def test_union_treematcher(G, H):
    TM = TreeMatcher(G, H, heuristic=Heuristic.UNION)
    result, delta = bench(TM.subgraph_is_isomorphic)
    expansions = TM.n_expanded_nodes()
    logger.info(f"\t Refinement (union) Expansions: {expansions}")
    return result, expansions, delta


def test_levels_treematcher(G, H):
    TM = TreeMatcher(G, H, heuristic=Heuristic.LEVEL)
    result, delta = bench(TM.subgraph_is_isomorphic)
    expansions = TM.n_expanded_nodes()
    logger.info(f"\t Refinement (levels) Expansions: {expansions}")
    return result, expansions, delta


def test_combined_treematcher(G, H):
    TM = TreeMatcher(G, H, heuristic=Heuristic.LEVEL)
    result, delta = bench(TM.subgraph_is_isomorphic)
    expansions = TM.n_expanded_nodes()
    logger.info(f"\t Refinement (levels) Expansions: {expansions}")
    
    if not result:
        TM = TreeMatcher(G, H, heuristic=Heuristic.UNION)
        result, delta = bench(TM.subgraph_is_isomorphic)
        expansions += TM.n_expanded_nodes()
        logger.info(f"\t Refinement (union) Expansions: {expansions}")
    return result, expansions, delta


def main():
    random.seed(314159)
    print("ntarget,vf2mean,vf2std,vf2time,refmean,refstd,reftime,accuracy")
    NBENCH_ITER = 100
    P_EDGE = 0.10
    R_RATIO = 0.75

    for i in range(30, 130, 5):
        N_NODES = i
        vf2_expansions = []
        tree_expansions = []

        vf2_times = []
        tree_times = []

        n_correct = NBENCH_ITER

        for j in range(NBENCH_ITER):
            G, H = generate_benchmark_pair(N_NODES, P_EDGE, R_RATIO)
            logger.info(f"TEST {i}")
            logger.info(f"\tTarget nodes: {G.number_of_nodes()}")
            logger.info(f"\tTarget edges: {G.number_of_edges()}")
            logger.info(f"\tPattern nodes: {H.number_of_nodes()}")
            logger.info(f"\tPattern edges: {H.number_of_edges()}")

            gm_result, gm_expansion, gm_time = test_graphmatcher(G, H)
            tm_result, tm_expansion, tm_time = test_combined_treematcher(G, H)

            vf2_expansions.append(gm_expansion)
            tree_expansions.append(tm_expansion)

            vf2_times.append(gm_time)
            tree_times.append(tm_time)

            if tm_result != gm_result:
                n_correct -= 1

        gm_vf2 = geometric_mean(vf2_expansions)
        std_vf2 = scipy.stats.gstd(vf2_expansions)
        time_vf2 = geometric_mean(vf2_times)

        gm_tree = geometric_mean(tree_expansions)
        std_tree = scipy.stats.gstd(tree_expansions)
        time_tree = geometric_mean(tree_times)

        accuracy = n_correct / NBENCH_ITER

        print(
            f"{i},{gm_vf2},{std_vf2},{time_vf2},{gm_tree},{std_tree},{time_tree},{accuracy}"
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
    lva = outdegree_bfs(P, 4)
    lvb = outdegree_bfs(T, 3)
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
    lva = outdegree_bfs(P, 4)
    lvb = outdegree_bfs(T, 3)
    print(lva, lvb, level_dominates(lvb, lva))
    print(P, T)


def test_refinement():
    random.seed(3141592)
    pattern = nx.drawing.nx_pydot.read_dot("graphs/zds_pattern.dot")
    target = nx.drawing.nx_pydot.read_dot("graphs/zds_target.dot")

    print(level_dominates(outdegree_bfs(target, "0"), outdegree_bfs(pattern, "0")))
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
