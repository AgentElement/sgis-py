import networkx as nx
from copy import deepcopy
from sgis.util import PriorityQueue


class GraphMatcher:
    def __init__(self, target, pattern):
        self.target = target
        self.pattern = pattern

        self.target_nodes = set(target.nodes())
        self.pattern_nodes = set(pattern.nodes())

        self.pattern_node_order = {n: i for i, n in enumerate(pattern)}

        self.root_node = TreeNode(self)

    def subgraph_is_isomorphic(self):
        return self.match()

    def match(self):
        search_queue = PriorityQueue()
        search_queue.push(self.root_node, -self.root_node.depth)
        while not search_queue.empty():
            node = search_queue.pop()
            node.debug_print()
            if node.is_isomorphism():
                return True
            child_nodes = node.generate_children()
            for child in child_nodes:
                search_queue.push(child, -child.depth)
        return False

    def isomorphism_search_tree(self):
        partial_isomorphism_tree = nx.DiGraph()
        isomorphisms = []
        search_queue = PriorityQueue()
        search_queue.push(self.root_node, -self.root_node.depth)
        while not search_queue.empty():
            node = search_queue.pop()
            if node.is_isomorphism():
                isomorphisms.append(node)
                continue
            child_nodes = node.generate_children()
            for child in child_nodes:
                search_queue.push(child, -child.depth)
                partial_isomorphism_tree.add_edge(
                    child.parent.get_hashable_state(),
                    child.get_hashable_state(),
                    weight=child.cost)
        return isomorphisms, partial_isomorphism_tree

    # Naive method
    def best_isomorphism(self):
        isomorphisms = []
        search_queue = PriorityQueue()
        search_queue.push(self.root_node, -self.root_node.depth)

        while not search_queue.empty():
            node = search_queue.pop()
            if node.is_isomorphism():
                isomorphisms.append(node)
                continue
            child_nodes = node.generate_children()
            for child in child_nodes:
                search_queue.push(child, -child.depth)

        if not isomorphisms:
            return None
        best = min(isomorphisms, key=lambda x: x.cost)
        return best.cost, best.target_to_pattern_map

    # Greedy search
    def heuristic_isomorphism(self):
        search_queue = PriorityQueue()
        search_queue.push(
            self.root_node, (-self.root_node.depth, self.root_node.cost))

        while not search_queue.empty():
            node = search_queue.pop()
            if node.is_isomorphism():
                return node.cost, node.target_to_pattern_map
            child_nodes = node.generate_children()
            for child in child_nodes:
                search_queue.push(child, (-child.depth, child.cost))
        return None

    # Ours!
    def rollout_isomorphism(self):
        search_queue = PriorityQueue()
        search_queue.push(
            self.root_node, (-self.root_node.depth, self.root_node.cost))

        while not search_queue.empty():
            node = search_queue.pop()
            if node.is_isomorphism():
                return node.cost, node.target_to_pattern_map
            child_nodes = node.generate_children()
            for child in child_nodes:
                search_queue.push(child, (-child.depth, child.rollout()))
        return None


class TreeNode:
    def __init__(self, GM):
        self.target = GM.target
        self.pattern = GM.pattern

        self.GM = GM

        self.target_to_pattern_map = {}
        self.pattern_to_target_map = {}

        self.inout_target = {}
        self.inout_pattern = {}

        self.target_node = None
        self.pattern_node = None

        self.depth = 0
        self.cost = 0

        self.parent = None

    def get_hashable_state(self):
        if self.parent is None:
            return "{}"
        #  return str(frozenset(self.target_to_pattern_map.items()))[10:-1]

        s = ""
        for key, val in self.target_to_pattern_map.items():
            s += f"({key}, {val})\n"
        return s

    def debug_print(self):
        print("Node")
        print(self.target_node, self.pattern_node)
        print(self.target_to_pattern_map, self.pattern_to_target_map)
        print(self.inout_target, self.inout_pattern)
        print(self.cost)
        print()

    def is_isomorphism(self):
        return len(self.target_to_pattern_map) == len(self.pattern)

    def syntactic_feasibility(self, target_node, pattern_node):
        return self.conglomerate_rule(target_node, pattern_node)

    def heuristic_syntactic_feasibility(self, target_node, pattern_node):
        return self.conglomerate_rule(target_node, pattern_node)
        

    def generate_cost(self, target_node, pattern_node):
        target_cost = 0
        for neighbor in self.target[target_node]:
            if neighbor in self.target_to_pattern_map:
                target_cost += self.target[target_node][neighbor]['weight']
        return target_cost

    def conglomerate_rule(self, target_node, pattern_node):
        assigned_target_count = 0
        target_count = 0

        pattern, target = self.pattern, self.target

        for neighbor in target[target_node]:
            neighbor_assigned = neighbor in self.target_to_pattern_map
            if neighbor_assigned:
                neighbor_in_pattern = self.target_to_pattern_map[neighbor]
                if neighbor_in_pattern not in pattern[pattern_node]:
                    return False
                elif target.number_of_edges(neighbor, target_node) \
                        != pattern.number_of_edges(neighbor_in_pattern,
                                                   pattern_node):
                    return False

            if neighbor in self.inout_target:
                if neighbor_assigned:
                    assigned_target_count += 1
            else:
                target_count += 1

        assigned_pattern_count = 0
        pattern_count = 0

        for neighbor in pattern[pattern_node]:
            neighbor_assigned = neighbor in self.pattern_to_target_map
            if neighbor_assigned:
                neighbor_in_target = self.pattern_to_target_map[neighbor]
                if neighbor_in_target not in target[target_node]:
                    return False
                elif pattern.number_of_edges(neighbor, pattern_node) \
                        != target.number_of_edges(neighbor_in_target,
                                                  target_node):
                    return False

            if neighbor in self.inout_pattern:
                if neighbor_assigned:
                    assigned_pattern_count += 1
            else:
                pattern_count += 1

        return (assigned_pattern_count >= assigned_target_count) \
            and (target_count >= pattern_count)

    def add_node_assignment(self, target_node, pattern_node):
        self.target_to_pattern_map[target_node] = pattern_node
        self.pattern_to_target_map[pattern_node] = target_node

        self.target_node = target_node
        self.pattern_node = pattern_node

        self.depth += 1
        self.cost += self.generate_cost(target_node, pattern_node)

        if target_node not in self.inout_target:
            self.inout_target[target_node] = self.depth

        if pattern_node not in self.inout_pattern:
            self.inout_pattern[pattern_node] = self.depth

        new_nodes = set()
        for node in self.target_to_pattern_map:
            new_nodes.update(
                [neighbor for neighbor in self.target[node]
                 if neighbor not in self.target_to_pattern_map
                 ]
            )

        for node in new_nodes:
            if node not in self.inout_target:
                self.inout_target[node] = self.depth

        new_nodes = set()
        for node in self.pattern_to_target_map:
            new_nodes.update(
                [neighbor for neighbor in self.pattern[node]
                 if neighbor not in self.pattern_to_target_map
                 ]
            )

        for node in new_nodes:
            if node not in self.inout_pattern:
                self.inout_pattern[node] = self.depth

    def generate_candidate_pairs(self):
        min_key = self.GM.pattern_node_order.__getitem__

        t_target_inout = [node for node in self.inout_target
                          if node not in self.target_to_pattern_map]
        t_pattern_inout = [node for node in self.inout_pattern
                           if node not in self.pattern_to_target_map]

        if t_target_inout and t_pattern_inout:
            pattern_node = min(t_pattern_inout, key=min_key)
            for target_node in t_target_inout:
                yield target_node, pattern_node

        else:
            pattern_node = min(self.GM.pattern_nodes
                               - set(self.pattern_to_target_map),
                               key=min_key)
            for target_node in self.target:
                if target_node not in self.target_to_pattern_map:
                    yield target_node, pattern_node

    def generate_children(self):
        for target_node, pattern_node in self.generate_candidate_pairs():
            if self.syntactic_feasibility(target_node, pattern_node):
                child = deepcopy(self)
                child.add_node_assignment(target_node, pattern_node)
                child.parent = self
                yield child

    def rollout(self):
        search_queue = PriorityQueue()
        search_queue.push(self, (-self.depth, self.cost))

        while not search_queue.empty():
            node = search_queue.pop()
            if node.is_isomorphism():
                return node.cost
            child_nodes = node.generate_children()
            for child in child_nodes:
                search_queue.push(child, (-child.depth, child.cost))
        return float('+inf')


def main():
    import networkx as nx
    import random
    import math

    random.seed(314159)
    G = nx.Graph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=2)
    G.add_edge('C', 'D', weight=3)
    G.add_edge('D', 'E', weight=4)
    G.add_edge('E', 'A', weight=5)
    G.add_edge('A', 'C', weight=6)
    G.add_edge('B', 'D', weight=7)
    H = nx.cycle_graph(3)

    nx.drawing.nx_pydot.write_dot(G, 'graphs/target.dot')
    nx.drawing.nx_pydot.write_dot(H, 'graphs/pattern.dot')

    GM = GraphMatcher(G, H)
    isomorphisms, iso_tree = GM.isomorphism_search_tree()

    for u, v in iso_tree.edges:
        iso_tree[u][v]['label'] = iso_tree[u][v]['weight']

    nx.drawing.nx_pydot.write_dot(iso_tree, 'graphs/isomorphism_search.dot')

    for iso in isomorphisms:
        iso.debug_print()

    #  print(GM.subgraph_is_isomorphic())


if __name__ == '__main__':
    main()
