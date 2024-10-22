import networkx as nx
from collections import defaultdict
from heapq import merge

from pandas.core.groupby.categorical import recode_for_groupby

REFINEMENT_TRUNCATION = 10


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

def pomultiset_dominates(a, b, poset):
    for (i, j) in zip(a, b):
        if (j, i) in poset:
            return False
    return True


def bfs(G, v):
    visited = defaultdict(int)
    levels = defaultdict(list)
    levels[v] = [G.degree(v)]
    queue = [v]
    while(len(queue) != 0):
        vtx = queue[0]
        del(queue[0])
        for n in G.neighbors(vtx):
            if n in visited:
                continue
            queue.append(n)
            depth = visited[vtx] + 1
            visited[n] = depth
            levels[depth].append(len(list(filter(lambda x: x not in visited, G.neighbors(n)))))
    for lv in levels.values():
        lv.sort(reverse=True)
    return levels


class Refinement:
    def __init__(self, target, pattern):
        self.target = target
        self.pattern = pattern
        self.refinement = defaultdict(dict)
        self.bfs_refinement()
    
    def query(self, target_node, pattern_node):
        return self.refinement[target_node][pattern_node]

    def bfs_refinement(self):
        for t in self.target.nodes():
            t_part = bfs(self.target, t)
            for p in self.pattern.nodes():
                p_part = bfs(self.pattern, p)
                self.refinement[t][p] = level_dominates(t_part, p_part, REFINEMENT_TRUNCATION)

    def level_refinement(self):
        apsp_t = nx.floyd_warshall(self.target)
        apsp_p = nx.floyd_warshall(self.pattern)
        for t, t_dists in apsp_t.items():
            t_part = partition_dict_by_keys(self.target, t_dists)
            for p, p_dists in apsp_p.items():
                p_part = partition_dict_by_keys(self.pattern, p_dists)
                self.refinement[t][p] = level_dominates(t_part, p_part, REFINEMENT_TRUNCATION)
    

    def iterative_refinement(self):
        refinement_map = {}
        label_map = {}
        i = 0
        for v in self.target:
            neighbors = [self.target.degree(n) for n in self.target.neighbors(v)]
            neighbors.sort(reverse=True)
            m = (self.target.degree(v), tuple(neighbors))
            if m not in refinement_map:
                refinement_map[m] = f"m{i}"
                i += 1
            label_map[f"t{v}"] = refinement_map[m]
        
        for v in self.pattern:
            neighbors = [self.pattern.degree(n) for n in self.pattern.neighbors(v)]
            neighbors.sort(reverse=True)
            m = (self.pattern.degree(v), tuple(neighbors))
            if m not in refinement_map:
                refinement_map[m] = f"m{i}"
                i += 1
            label_map[f"p{v}"] = refinement_map[m]
        
        print("refinement", refinement_map)
        print("label", label_map)

        poset = set()
        for dom, vd in refinement_map.items():
            for sub, vs in refinement_map.items():
                if dom[0] > sub[0] and multiset_dominates(dom[1], sub[1]):
                    poset |= {(vd, vs)}
        
        for v in self.target:
            neighbors = [self.target.degree(n) for n in self.target.neighbors(v)]
            neighbors.sort(reverse=True)
            m = (self.target.degree(v), tuple(neighbors))
            if m not in refinement_map:
                refinement_map[m] = f"m{i}"
                i += 1
        
        for v in self.pattern:
            neighbors = [self.pattern.degree(n) for n in self.pattern.neighbors(v)]
            neighbors.sort(reverse=True)
            m = (self.pattern.degree(v), tuple(neighbors))
            if m not in refinement_map:
                refinement_map[m] = f"m{i}"
                i += 1
        print(refinement_map)

        print(poset)
        changed = True
        while changed:
            new_poset = set()
            for dom in refinement_map.values():
                for sub in refinement_map.values():
                    if (dom[0], sub[0]) in poset and multiset_dominates(dom[1], sub[1]):
                        new_poset |= {(dom, sub),}
            changed = False
            print(new_poset)


    # implement ZDS refinement with trees if there is time for it
    def iterative_level_refinement(self):
        pass


    def print_refinement(self):
        for t, td in self.refinement.items():
            for p, b in td.items():
                print(f"({t} {p}): {b}", end="\t")
            print()
