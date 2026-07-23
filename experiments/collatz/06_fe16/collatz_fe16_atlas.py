"""
collatz_fe16_atlas.py

Collatz V13.1 — FE16 Morphodynamic Atlas.
Builds the full graph, computes ranks, computes escape efficiency E(s),
and saves the complete atlas for all 65,536 states.
"""

import os
import csv
import numpy as np
import networkx as nx
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. UTILITY FUNCTIONS
# -----------------------------------------------------------------------------

def v2(n: int) -> int:
    if n <= 0:
        return 0
    return (n & -n).bit_length() - 1

def v3(n: int) -> int:
    return min(v2(n), 3)

def is_state_valid(r: int, v: int) -> bool:
    if v == 0:
        return r % 2 == 1
    elif v == 1:
        return r % 2 == 0 and (r // 2) % 2 == 1
    elif v == 2:
        return r % 4 == 0 and (r // 4) % 2 == 1
    elif v == 3:
        return r % 8 == 0
    return False

# -----------------------------------------------------------------------------
# 2. QUOTIENT GRAPH BUILDER (k=16)
# -----------------------------------------------------------------------------

def build_quotient(k: int = 16):
    M = 1 << k
    print(f"[1] Building states for k={k} (M={M})...")
    states = []
    for r in range(M):
        for v in range(4):
            if is_state_valid(r, v):
                states.append((r, v))
    print(f"    Total valid states: {len(states)}")

    print("[2] Finding representatives...")
    reps = {}
    for r, v in tqdm(states, desc="  Searching reps"):
        found = False
        for q in range(8):
            n = r + q * M
            if n <= 0:
                n = M
            if v3(n) == v:
                reps[(r, v)] = n
                found = True
                break
        if not found:
            for q in range(8, 100):
                n = r + q * M
                if n <= 0:
                    continue
                if v3(n) == v:
                    reps[(r, v)] = n
                    found = True
                    break
        if not found:
            raise RuntimeError(f"Could not find representative for state ({r}, {v})")

    print("[3] Building transitions...")
    transitions = {}
    for r, v in tqdm(states, desc="  Computing T"):
        n = reps[(r, v)]
        if n % 2 == 0:
            n_next = n // 2
        else:
            n_next = 3 * n + 1
        r_next = n_next % M
        v_next = v3(n_next)
        next_state = (r_next, v_next)
        if next_state not in states:
            # This should not happen for k=16, but we handle it gracefully.
            states.append(next_state)
        transitions[(r, v)] = next_state

    # Recompute transitions for any added states (should be zero).
    for r, v in states:
        if (r, v) not in transitions:
            # Find rep for this state
            n = None
            for q in range(8):
                n_candidate = r + q * M
                if n_candidate <= 0:
                    continue
                if v3(n_candidate) == v:
                    n = n_candidate
                    break
            if n is None:
                for q in range(8, 100):
                    n_candidate = r + q * M
                    if n_candidate <= 0:
                        continue
                    if v3(n_candidate) == v:
                        n = n_candidate
                        break
            if n is None:
                raise RuntimeError(f"Cannot find rep for state ({r}, {v})")
            if n % 2 == 0:
                n_next = n // 2
            else:
                n_next = 3 * n + 1
            r_next = n_next % M
            v_next = v3(n_next)
            transitions[(r, v)] = (r_next, v_next)

    return states, transitions

# -----------------------------------------------------------------------------
# 3. RANK COMPUTATION
# -----------------------------------------------------------------------------

def compute_ranks(states, transitions):
    print("[4] Building NetworkX graph...")
    G = nx.DiGraph()
    G.add_nodes_from(states)
    for src, dst in transitions.items():
        G.add_edge(src, dst)

    print("[5] Computing SCCs...")
    sccs = list(nx.strongly_connected_components(G))
    print(f"    Found {len(sccs)} SCCs.")

    terminal_scc = None
    for scc in sccs:
        if (1, 0) in scc:
            terminal_scc = scc
            break
    if terminal_scc is None:
        raise RuntimeError("Terminal SCC not found!")
    print(f"    Terminal SCC size: {len(terminal_scc)}")

    scc_id = {}
    for idx, scc in enumerate(sccs):
        for s in scc:
            scc_id[s] = idx

    dag = nx.DiGraph()
    for idx in range(len(sccs)):
        dag.add_node(idx)
    for src, dst in transitions.items():
        i = scc_id[src]
        j = scc_id[dst]
        if i != j:
            dag.add_edge(i, j)

    term_id = scc_id[(1, 0)]
    try:
        topo = list(nx.topological_sort(dag))
    except nx.NetworkXUnfeasible:
        print("ERROR: Condensation is not a DAG!")
        return None, None

    rank_scc = {node: -1 for node in dag.nodes()}
    rank_scc[term_id] = 0
    for node in reversed(topo):
        if node == term_id:
            continue
        max_child = -1
        for child in dag.successors(node):
            if rank_scc[child] >= 0:
                max_child = max(max_child, rank_scc[child])
        if max_child >= 0:
            rank_scc[node] = max_child + 1

    rank = {}
    for state, sid in scc_id.items():
        rank[state] = rank_scc[sid]

    # Verify strict decrease
    ok = True
    for src, dst in transitions.items():
        if src in terminal_scc:
            continue
        if rank[src] <= rank[dst]:
            print(f"WARNING: {src} -> {dst}, rank {rank[src]} <= {rank[dst]}")
            ok = False
    if ok:
        print("    Rank strictly decreases on all edges outside terminal SCC.")
    else:
        print("    Rank violation detected!")
    return rank, terminal_scc

# -----------------------------------------------------------------------------
# 4. ATLAS BUILDER
# -----------------------------------------------------------------------------

def build_atlas(states, transitions, rank, terminal_scc):
    print("[6] Building FE16 Morphodynamic Atlas...")
    atlas = []
    max_rank = max(rank.values())
    
    for s in tqdm(states, desc="  Computing atlas entries"):
        R = rank.get(s, -1)
        if s in terminal_scc:
            tau = 0
            efficiency = 0
            R_next = R
        else:
            next_s = transitions[s]
            R_next = rank.get(next_s, -1)
            # Since rank strictly decreases, tau = 1.
            tau = 1
            efficiency = R - R_next  # How much rank drops in one step
        
        r, v = s
        atlas.append({
            'r': r,
            'v': v,
            'rank': R,
            'rank_next': R_next,
            'tau': tau,
            'efficiency': efficiency,
            'next_r': next_s[0] if s not in terminal_scc else -1,
            'next_v': next_s[1] if s not in terminal_scc else -1,
        })
    
    return atlas

# -----------------------------------------------------------------------------
# 5. ANALYSIS & VISUALIZATION
# -----------------------------------------------------------------------------

def analyze_atlas(atlas, states):
    ranks = [entry['rank'] for entry in atlas]
    efficiencies = [entry['efficiency'] for entry in atlas if entry['tau'] > 0]
    taus = [entry['tau'] for entry in atlas]
    
    print("\n" + "=" * 60)
    print("FE16 ATLAS STATISTICS")
    print("=" * 60)
    print(f"Total states: {len(states)}")
    print(f"Max rank: {max(ranks)}")
    print(f"Mean rank: {np.mean(ranks):.2f}")
    print(f"Median rank: {np.median(ranks):.2f}")
    print(f"States with tau=1: {sum(1 for t in taus if t == 1)}")
    print(f"States with tau=0 (terminal): {sum(1 for t in taus if t == 0)}")
    print(f"Max efficiency (rank drop in 1 step): {max(efficiencies) if efficiencies else 0}")
    print(f"Mean efficiency: {np.mean(efficiencies):.2f}")
    print(f"Median efficiency: {np.median(efficiencies):.2f}")
    
    # Distribution of efficiency
    plt.figure(figsize=(10, 6))
    plt.hist(efficiencies, bins=range(1, max(efficiencies)+2), align='left', rwidth=0.8, log=True)
    plt.xlabel("Efficiency E(s) = Rank drop in one step")
    plt.ylabel("Frequency (log scale)")
    plt.title("FE16 Atlas: Distribution of Escape Efficiency")
    plt.grid(True, alpha=0.3)
    plt.savefig("fe16_efficiency_distribution.png", dpi=150)
    plt.show()
    
    # Rank distribution
    plt.figure(figsize=(10, 6))
    plt.hist(ranks, bins=50, log=True)
    plt.xlabel("Rank L(s)")
    plt.ylabel("Frequency (log scale)")
    plt.title("FE16 Atlas: Distribution of Ranks")
    plt.grid(True, alpha=0.3)
    plt.savefig("fe16_rank_distribution.png", dpi=150)
    plt.show()
    
    # Find states with max efficiency
    max_eff = max(efficiencies) if efficiencies else 0
    max_eff_states = [e for e in atlas if e['efficiency'] == max_eff]
    print(f"\nStates with max efficiency ({max_eff}):")
    for e in max_eff_states[:5]:
        print(f"  State ({e['r']}, {e['v']}) rank={e['rank']} -> next_rank={e['rank_next']}")
    
    # Find states with efficiency 1 (slow descent)
    slow_states = [e for e in atlas if e['efficiency'] == 1 and e['tau'] > 0]
    print(f"\nNumber of 'slow' states (efficiency=1): {len(slow_states)}")
    if slow_states:
        print("  Example slow state:", slow_states[0])
    
    return ranks, efficiencies

# -----------------------------------------------------------------------------
# 6. SAVE ATLAS
# -----------------------------------------------------------------------------

def save_atlas(atlas, filename="fe16_atlas_full.csv"):
    print(f"\n[7] Saving atlas to {filename}...")
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['r', 'v', 'rank', 'rank_next', 'tau', 'efficiency', 'next_r', 'next_v'])
        writer.writeheader()
        for entry in atlas:
            writer.writerow(entry)
    print("    Atlas saved.")

# -----------------------------------------------------------------------------
# 7. MAIN
# -----------------------------------------------------------------------------

def main():
    print("=" * 80)
    print("COLLATZ FE16 — MORPHODYNAMIC ATLAS BUILDER")
    print("=" * 80)
    
    # Build graph
    states, transitions = build_quotient(16)
    
    # Compute ranks
    rank, terminal_scc = compute_ranks(states, transitions)
    if rank is None:
        return
    
    # Build atlas
    atlas = build_atlas(states, transitions, rank, terminal_scc)
    
    # Analyze
    ranks, efficiencies = analyze_atlas(atlas, states)
    
    # Save
    save_atlas(atlas)
    
    print("\n" + "=" * 80)
    print("ATLAS BUILD COMPLETE.")
    print(f"Files generated: fe16_atlas_full.csv, fe16_efficiency_distribution.png, fe16_rank_distribution.png")
    print("=" * 80)

if __name__ == "__main__":
    main()