from dataclasses import dataclass
import sys

from sgis.refinement import Heuristic, Refinement


class TreeMatcher:
    def __init__(self, target, pattern, heuristic=Heuristic.UNION):
        self.target = target
        self.pattern = pattern

        self.target_nodes = set(target.nodes())
        self.pattern_nodes = set(pattern.nodes())

        self.pattern_node_order = {
            n: i for i, n in enumerate(pattern)}

        self.root_node = TreeNode(self)
        self.refinement = Refinement(target, pattern, heuristic=heuristic)

        expected_max_recursion_level = len(target)
        sys.setrecursionlimit(max(
            sys.getrecursionlimit(),
            int(1.5 * expected_max_recursion_level)
        ))



    def subgraph_is_isomorphic(self):
        try:
            next(self.root_node.match())
            return True
        except StopIteration:
            return False

    def n_expanded_nodes(self):
        return self.root_node.expansions


@dataclass(order=True)
class TreeNode:
    priority: int

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
        self.expansions = 0

    def debug_print(self):
        print("Node")
        print(self.target_node, self.pattern_node)
        print(self.target_to_pattern_map, self.pattern_to_target_map)
        print(self.inout_target, self.inout_pattern)
        print()

    def is_isomorphism(self):
        return len(self.target_to_pattern_map) == len(self.pattern)

    def syntactic_feasibility(self, target_node, pattern_node):
        return \
            self.rule_refinement(target_node, pattern_node) \
            and self.rule_pred_succ(target_node, pattern_node) \
            and self.rule_cardinality(target_node, pattern_node) \
            and self.rule_new(target_node, pattern_node)

    def rule_pred_succ(self, target_node, pattern_node):
        for neighbor in self.target[target_node]:
            if neighbor in self.target_to_pattern_map:
                neighbor_in_pattern = self.target_to_pattern_map[neighbor]
                if neighbor_in_pattern not in self.pattern[pattern_node]:
                    return False
                elif self.target.number_of_edges(neighbor, target_node) \
                        != self.pattern.number_of_edges(neighbor_in_pattern, pattern_node):
                    return False

        for neighbor in self.pattern[pattern_node]:
            if neighbor in self.pattern_to_target_map:
                neighbor_in_target = self.pattern_to_target_map[neighbor]
                if neighbor_in_target not in self.target[target_node]:
                    return False
                elif self.pattern.number_of_edges(neighbor, pattern_node) \
                        != self.target.number_of_edges(neighbor_in_target, target_node):
                    return False

        return True

    def rule_cardinality(self, target_node, pattern_node):
        card_target = 0
        for neighbor in self.target[target_node]:
            if (neighbor in self.inout_target) \
                    and (neighbor not in self.target_to_pattern_map):
                card_target += 1

        card_pattern = 0
        for neighbor in self.pattern[pattern_node]:
            if (neighbor in self.inout_pattern) \
                    and (neighbor not in self.pattern_to_target_map):
                card_pattern += 1

        return card_target >= card_pattern

    def rule_new(self, target_node, pattern_node):
        card_target = 0
        for neighbor in self.target[target_node]:
            if neighbor not in self.inout_target:
                card_target += 1

        card_pattern = 0
        for neighbor in self.pattern[pattern_node]:
            if neighbor not in self.inout_pattern:
                card_pattern += 1

        return card_target >= card_pattern

    def rule_refinement(self, target_node, pattern_node):
        return self.GM.refinement.query(target_node, pattern_node)

    def add_node_assignment(self, target_node, pattern_node):
        self.target_to_pattern_map[target_node] = pattern_node
        self.pattern_to_target_map[pattern_node] = target_node

        self.target_node = target_node
        self.pattern_node = pattern_node

        self.depth += 1
        self.priority = -self.depth

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

    def restore(self, target_node, pattern_node):
        del self.target_to_pattern_map[target_node]
        del self.pattern_to_target_map[pattern_node]

        for vector in (self.inout_target, self.inout_pattern):
            for node in list(vector.keys()):
                if vector[node] == self.depth:
                    del vector[node]

        self.depth -= 1
        self.priority += self.depth

    def match(self):
        if self.is_isomorphism():
            yield self.target_to_pattern_map
        for target_node, pattern_node in self.generate_candidate_pairs():
            if self.syntactic_feasibility(target_node, pattern_node):
                self.expansions += 1
                self.add_node_assignment(target_node, pattern_node)
                yield from self.match()
                self.restore(target_node, pattern_node)

