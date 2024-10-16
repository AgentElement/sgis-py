import networkx as nx
from collections import defaultdict
from heapq import merge

REFINEMENT_TRUNCATION = 5


def partition_dict_by_keys(G, d):
    partition = defaultdict(list)
    for k, v in d.items():
        if v == float('inf'):
            continue
        partition[int(v)].append(G.degree(k))
    for lst in partition.values():
        lst.sort(reverse=True)
    return partition


def level_dominates(target_level, pattern_level, k):
    i = 0
    target_agg_level = []
    pattern_agg_level = []
    for lt, lp in zip(target_level, pattern_level):
        if i > k:
            break
        i += 1
        # target_agg_level = list(merge(target_agg_level, target_level[lt], reverse=True))
        # pattern_agg_level = list(merge(pattern_agg_level, pattern_level[lp], reverse=True))
        # if not multiset_dominates(target_agg_level, pattern_agg_level):
        #     return False
        if not multiset_dominates(target_level[lt], pattern_level[lp]):
            return False
    return True


def multiset_dominates(a, b):
    # if len(b) > len(a):
    #     return False
    for (i, j) in zip(a, b):
        if j > i:
            return False
    return True


class Refinement:
    def __init__(self, target, pattern):
        self.target = target
        self.pattern = pattern
        self.refinement = defaultdict(dict)
        self.level_refinement()

    
    def query(self, target_node, pattern_node):
        return self.refinement[target_node][pattern_node]

    def level_refinement(self):
        apsp_t = nx.floyd_warshall(self.target)
        apsp_p = nx.floyd_warshall(self.pattern)
        for t, t_dists in apsp_t.items():
            t_part = partition_dict_by_keys(self.target, t_dists)
            for p, p_dists in apsp_p.items():
                p_part = partition_dict_by_keys(self.pattern, p_dists)
                self.refinement[t][p] = level_dominates(t_part, p_part, REFINEMENT_TRUNCATION)
    

    def iterative_refinement(self):
        pass

    
    def iterative_level_refinement(self):
        pass


    def print_refinement(self):
        for t, td in self.refinement.items():
            for p, b in td.items():
                print(f"({t} {p}): {b}", end="\t")
            print()
