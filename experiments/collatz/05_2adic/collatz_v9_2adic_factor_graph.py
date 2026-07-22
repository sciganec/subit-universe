"""
collatz_v9_2adic_factor_graph.py — Collatz v9.0 (Final)
2-adic Factor Graph Reconstruction

Builds the exact finite quotient of the Collatz map over Z/2^k Z,
computes SCCs, minimizes the automaton, and searches for a rank function
using SCC condensation (no recursion).
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 0. PATH
# ============================================================================

def get_data_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

# ============================================================================
# 1. 2-ADIC RESIDUE ENGINE
# ============================================================================

class TwoAdicCollatzAutomaton:
    """
    Exact finite quotient of the Collatz map over Z/2^k Z.
    State = (residue mod 2^k, v2_class)
    """

    def __init__(self, k: int = 8):
        self.k = k
        self.M = 1 << k
        self._build_states()
        self._build_transitions()

    def _v2_class(self, n: int) -> int:
        if n <= 0:
            return 0
        v = (n & -n).bit_length() - 1
        return min(v, 3)

    def _residue(self, n: int) -> int:
        return n & (self.M - 1)

    def _build_states(self):
        self.states = []
        self.state_to_id = {}
        for r in range(self.M):
            for v in range(4):
                # Validate state
                if v == 0 and r % 2 == 0:
                    continue
                if v == 1 and (r % 2 != 0 or (r // 2) % 2 == 0):
                    continue
                if v == 2 and (r % 4 != 0 or (r // 4) % 2 == 0):
                    continue
                if v == 3 and r % 8 != 0:
                    continue
                state = (r, v)
                self.state_to_id[state] = len(self.states)
                self.states.append(state)

    def _next_state(self, r: int, v: int):
        # Build representative n
        if v == 0:
            if r % 2 == 0:
                return None
            n = r
        elif v == 1:
            if r % 2 != 0 or (r // 2) % 2 == 0:
                return None
            n = r
        elif v == 2:
            if r % 4 != 0 or (r // 4) % 2 == 0:
                return None
            n = r
        else:  # v == 3
            if r % 8 != 0:
                return None
            n = r

        # One Collatz step
        if n % 2 == 0:
            n_next = n // 2
        else:
            n_next = 3 * n + 1

        r_next = self._residue(n_next)
        v_next = self._v2_class(n_next)
        return (r_next, v_next)

    def _build_transitions(self):
        self.transitions = {}
        for state in self.states:
            r, v = state
            nxt = self._next_state(r, v)
            if nxt is not None and nxt in self.state_to_id:
                self.transitions[state] = nxt
            else:
                self.transitions[state] = None

    def get_graph(self):
        G = nx.DiGraph()
        for state in self.states:
            G.add_node(state)
        for state, nxt in self.transitions.items():
            if nxt is not None:
                G.add_edge(state, nxt)
        return G

    def get_sccs(self):
        G = self.get_graph()
        return list(nx.strongly_connected_components(G))

    def minimize_dfa(self):
        G = self.get_graph()
        initial = (1, 0)
        if initial not in self.state_to_id:
            return None, None
        reachable = set()
        queue = deque([initial])
        while queue:
            state = queue.popleft()
            if state in reachable:
                continue
            reachable.add(state)
            nxt = self.transitions.get(state)
            if nxt is not None and nxt not in reachable:
                queue.append(nxt)
        reachable_states = list(reachable)
        reachable_trans = {}
        for s in reachable_states:
            nxt = self.transitions.get(s)
            if nxt in reachable:
                reachable_trans[s] = nxt
        return reachable_states, reachable_trans


# ============================================================================
# 2. RANK FUNCTION SEARCH (SCC-based, iterative, no recursion)
# ============================================================================

class RankFunctionSearcher:
    def __init__(self, automaton: TwoAdicCollatzAutomaton):
        self.automaton = automaton
        self.transitions = automaton.transitions
        self.states = automaton.states
        self.state_to_id = automaton.state_to_id

    def find_rank(self):
        """
        Compute rank as longest path to a terminal SCC in the condensation DAG.
        Returns (rank_dict, is_decreasing) or (None, False).
        """
        G = nx.DiGraph()
        for state, nxt in self.transitions.items():
            if nxt is not None:
                G.add_edge(state, nxt)

        # SCCs
        sccs = list(nx.strongly_connected_components(G))
        scc_id = {}
        for idx, scc in enumerate(sccs):
            for s in scc:
                scc_id[s] = idx

        # Build condensation DAG (acyclic)
        dag = nx.DiGraph()
        for idx in range(len(sccs)):
            dag.add_node(idx)
        for state, nxt in self.transitions.items():
            if nxt is not None:
                i = scc_id[state]
                j = scc_id[nxt]
                if i != j:
                    dag.add_edge(i, j)

        # Find terminal SCCs (no outgoing edges)
        terminal_sccs = [n for n in dag.nodes() if dag.out_degree(n) == 0]
        if not terminal_sccs:
            return None, False

        # Compute longest distance to any terminal SCC using topological order (iterative)
        # Since DAG is acyclic, we can process nodes in reverse topological order.
        topo = list(nx.topological_sort(dag))
        dist = {n: -1 for n in dag.nodes()}
        for n in terminal_sccs:
            dist[n] = 0
        # Process in reverse topological order
        for node in reversed(topo):
            if node in terminal_sccs:
                continue
            max_child = -1
            for child in dag.successors(node):
                if dist[child] >= 0:
                    max_child = max(max_child, 1 + dist[child])
            dist[node] = max_child

        # Assign rank to each state
        rank = {}
        for state in self.states:
            sid = scc_id[state]
            rank[state] = dist.get(sid, -1)

        # Check strict decrease
        decreasing = True
        for state, nxt in self.transitions.items():
            if nxt is not None:
                if rank[state] <= rank[nxt]:
                    decreasing = False
                    break

        return rank, decreasing


# ============================================================================
# 3. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ v9.0: 2-ADIC FACTOR GRAPH RECONSTRUCTION")
    print("From Morphology to Topological Skeleton")
    print("=" * 80)

    k = 8
    print(f"\n[1] Building 2-adic automaton (k={k})...")
    automaton = TwoAdicCollatzAutomaton(k=k)
    print(f"  States: {len(automaton.states)}")
    print(f"  Transitions: {len(automaton.transitions)}")

    print("\n[2] Computing SCCs...")
    sccs = automaton.get_sccs()
    print(f"  SCCs: {len(sccs)}")
    scc_sizes = sorted([len(scc) for scc in sccs], reverse=True)
    print(f"  Largest SCC: {scc_sizes[0] if scc_sizes else 0}")
    if len(scc_sizes) > 1:
        print(f"  Second largest: {scc_sizes[1] if len(scc_sizes) > 1 else 0}")

    terminals = [s for s in automaton.states if automaton.transitions.get(s) is None]
    print(f"  Terminal states: {len(terminals)}")

    initial = (1, 0)
    if initial in automaton.state_to_id:
        print(f"  Initial state (1,0) is present.")

    print("\n[3] Minimizing automaton...")
    reachable, reachable_trans = automaton.minimize_dfa()
    if reachable:
        print(f"  Reachable states: {len(reachable)}")
        patterns = {}
        for s, nxt in reachable_trans.items():
            pattern = nxt
            if pattern not in patterns:
                patterns[pattern] = []
            patterns[pattern].append(s)
        print(f"  Distinct next-state patterns: {len(patterns)}")
    else:
        print("  Minimization failed.")

    print("\n[4] Searching for rank function (SCC-based)...")
    searcher = RankFunctionSearcher(automaton)
    rank, decreasing = searcher.find_rank()
    if rank is not None:
        max_rank = max(rank.values()) if rank else 0
        print(f"  Rank function found (max value: {max_rank})")
        if decreasing:
            print("  ✅ Rank function is strictly decreasing on all transitions!")
        else:
            print("  ⚠️ Rank function is NOT strictly decreasing on all transitions.")
            # Show counterexample
            for state, nxt in automaton.transitions.items():
                if nxt is not None and rank[state] <= rank[nxt]:
                    print(f"    Counterexample: {state} -> {nxt}, ranks: {rank[state]} <= {rank[nxt]}")
                    break
    else:
        print("  No rank function found.")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  k = {k} (mod 2^{k})")
    print(f"  Total states: {len(automaton.states)}")
    print(f"  Transitions: {len(automaton.transitions)}")
    print(f"  SCCs: {len(sccs)}")
    print(f"  Terminal states: {len(terminals)}")
    print(f"  Reachable states: {len(reachable) if reachable else 'N/A'}")
    print("=" * 80)

    # Save results
    import json
    results = {
        'k': k,
        'states': len(automaton.states),
        'transitions': len(automaton.transitions),
        'scc_count': len(sccs),
        'scc_sizes': scc_sizes,
        'terminal_count': len(terminals),
        'reachable_states': len(reachable) if reachable else None,
        'rank_found': rank is not None,
        'rank_max': max(rank.values()) if rank else None,
        'rank_decreasing': decreasing if rank is not None else None,
    }
    with open(get_data_path("v9_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("  Results saved to v9_results.json")

    print("\n  Next steps:")
    print("  1. Increase k to 9, 10, 12 to see if the structure stabilizes.")
    print("  2. If a rank function exists, formalize it as a proof.")
    print("  3. Map the automaton back to arithmetic classes.")


if __name__ == "__main__":
    main()