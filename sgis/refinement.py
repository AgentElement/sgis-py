import networkx as nx
from collections import defaultdict
from heapq import merge
from enum import Enum

from networkx.algorithms.connectivity import build_auxiliary_node_connectivity
from networkx.algorithms.flow import build_residual_network

REFINEMENT_TRUNCATION = 10000


class Heuristic(Enum):
    UNION = 0
    LEVEL = 1


def partition_dict_by_keys(G, d):
    partition = defaultdict(list)
    for k, v in d.items():
        if v == float("inf"):
            continue
        partition[int(v)].append(G.degree(k))
    for lst in partition.values():
        lst.sort(reverse=True)
    return partition


def level_dominates(target_level, pattern_level, trunc=None):
    i = 0
    for lt, lp in zip(target_level, pattern_level):
        if trunc is not None and i > trunc:
            break
        i += 1
        if not multiset_dominates(target_level[lt], pattern_level[lp]):
            return False
    return True


def union_level_dominates(target_level, pattern_level, trunc=None):
    i = 0
    target_union = []
    pattern_union = []
    for lt, lp in zip(target_level, pattern_level):
        if trunc is not None and i > trunc:
            break
        i += 1
        target_union = merge(target_union, target_level[lt], reverse=True)
        pattern_union = merge(pattern_union, pattern_level[lp], reverse=True)
        if not multiset_dominates(target_union, pattern_union):
            return False
    return True


def multiset_dominates(a, b):
    for i, j in zip(a, b):
        if j > i:
            return False
    return True


# Degrees
def degree_bfs(G, v):
    visited = defaultdict(int)
    levels = defaultdict(list)
    levels[0] = [G.degree(v)]
    queue = [v]
    while len(queue) != 0:
        vtx = queue[0]
        del queue[0]
        for n in G.neighbors(vtx):
            if n in visited:
                continue
            queue.append(n)
            depth = visited[vtx] + 1
            visited[n] = depth
            degree = G.degree(n)
            levels[depth].append(degree)
    for lv in levels.values():
        lv.sort(reverse=True)
    return levels


# Outdegrees
def outdegree_bfs(G, v):
    visited = defaultdict(int)
    levels = defaultdict(list)
    levels[0] = [G.degree(v)]
    queue = [v]
    while len(queue) != 0:
        vtx = queue[0]
        del queue[0]
        for n in G.neighbors(vtx):
            if n in visited:
                continue
            queue.append(n)
            depth = visited[vtx] + 1
            visited[n] = depth
            outdegree = len(list(filter(lambda x: x not in visited, G.neighbors(n))))
            # see counterexample case in main()
            if outdegree != 0:
                levels[depth].append(outdegree)
    for lv in levels.values():
        lv.sort(reverse=True)
    return levels


# Outdegree + # of disjoint paths
def path_bfs(G, v):
    visited = defaultdict(int)
    levels = defaultdict(list)
    levels[0] = [G.degree(v)]
    queue = [v]
    H = build_auxiliary_node_connectivity(G)
    R = build_residual_network(H, "capacity")
    while len(queue) != 0:
        vtx = queue[0]
        del queue[0]
        for n in G.neighbors(vtx):
            if n in visited:
                continue
            queue.append(n)
            depth = visited[vtx] + 1
            visited[n] = depth
            outdegree = len(list(filter(lambda x: x not in visited, G.neighbors(n))))
            n_disjoint_paths = len(
                list(nx.node_disjoint_paths(G, v, n, auxiliary=H, residual=R))
            )
            # see counterexample case in main()
            if outdegree != 0:
                levels[depth].append(outdegree + n_disjoint_paths)
    for lv in levels.values():
        lv.sort(reverse=True)
    return levels


class Refinement:
    def __init__(self, target, pattern, heuristic=Heuristic.UNION):
        self.target = target
        self.pattern = pattern
        self.refinement = defaultdict(dict)
        match heuristic:
            case Heuristic.UNION:
                self.union_refinement()
            case Heuristic.LEVEL:
                self.level_refinement()

    def query(self, target_node, pattern_node):
        return self.refinement[target_node][pattern_node]

    def union_refinement(self):
        for t in self.target.nodes():
            t_part = degree_bfs(self.target, t)
            for p in self.pattern.nodes():
                p_part = outdegree_bfs(self.pattern, p)
                self.refinement[t][p] = union_level_dominates(
                    t_part, p_part, REFINEMENT_TRUNCATION
                )

    def level_refinement(self):
        for t in self.target.nodes():
            t_part = degree_bfs(self.target, t)
            for p in self.pattern.nodes():
                p_part = outdegree_bfs(self.pattern, p)
                self.refinement[t][p] = level_dominates(
                    t_part, p_part, REFINEMENT_TRUNCATION
                )

    def distance_refinement(self):
        apsp_t = nx.floyd_warshall(self.target)
        apsp_p = nx.floyd_warshall(self.pattern)
        for t, t_dists in apsp_t.items():
            t_part = partition_dict_by_keys(self.target, t_dists)
            for p, p_dists in apsp_p.items():
                p_part = partition_dict_by_keys(self.pattern, p_dists)
                self.refinement[t][p] = level_dominates(
                    t_part, p_part, REFINEMENT_TRUNCATION
                )

    def print_refinement(self):
        for t, td in self.refinement.items():
            for p, b in td.items():
                print(f"({t} {p}): {b}", end="\t")
            print()
