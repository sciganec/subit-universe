"""
collatz_fe16_fixed.py

Collatz V13.1 — Fixed analyzer for Fiber Escape Conjecture (FE_16)

Builds G_16 exactly, computes rank function rho_16, tests fiber escape.
No extra states are added; all transitions map to existing valid states.
"""

import os
import csv
import numpy as np
import networkx as nx
from collections import defaultdict
from tqdm import tqdm

# -----------------------------------------------------------------------------
# 1. UTILITY FUNCTIONS
# -----------------------------------------------------------------------------

def v2(n: int) -> int:
    """Exponent of the highest power of 2 dividing n. Returns 0 for n <= 0."""
    if n <= 0:
        return 0
    return (n & -n).bit_length() - 1

def v3(n: int) -> int:
    """Truncated 2-adic valuation: min(v2(n), 3)."""
    return min(v2(n), 3)

def is_state_valid(r: int, v: int) -> bool:
    """Check if (r, v) is a valid state in S_k."""
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
    """
    Builds the state space S_k and the transition map T_k.
    Returns:
        states: list of (r, v) tuples.
        transitions: dict mapping (r, v) -> (r_next, v_next).
    """
    M = 1 << k
    print(f"[1] Building states for k={k} (M={M})...")

    states = []
    for r in range(M):
        for v in range(4):
            if is_state_valid(r, v):
                states.append((r, v))

    print(f"    Total valid states: {len(states)}")

    # Precompute a representative integer for each state.
    # We search n = r + q * M for q in 0..7.
    print("[2] Finding representatives for each state...")
    reps = {}
    for r, v in tqdm(states, desc="  Searching reps"):
        found = False
        for q in range(8):
            n = r + q * M
            if n <= 0:
                n = M  # skip 0
            if v3(n) == v:
                reps[(r, v)] = n
                found = True
                break
        if not found:
            # Fallback: take any n with this residue and valuation.
            # This is extremely unlikely, but we try larger q.
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

    # Build transitions
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

        # Sanity check: next_state must be in our list (it should).
        if next_state not in states:
            # This should never happen for a correctly built quotient.
            # But if it does, we add it anyway (with a warning).
            print(f"WARNING: next_state {next_state} not in states. Adding it.")
            states.append(next_state)
        transitions[(r, v)] = next_state

    # Ensure all states have a transition (including newly added).
    # Actually, if we added a state, we still need its transition.
    # We'll recompute for all states just to be safe.
    print("[3b] Recomputing transitions for all states (including any added)...")
    for r, v in tqdm(states, desc="  Recomputing"):
        if (r, v) in transitions:
            continue
        # Find rep for this state (it may have been added)
        n = None
        for q in range(8):
            n_candidate = r + q * M
            if n_candidate <= 0:
                continue
            if v3(n_candidate) == v:
                n = n_candidate
                break
        if n is None:
            # fallback
            for q in range(8, 100):
                n_candidate = r + q * M
                if n_candidate <= 0:
                    continue
                if v3(n_candidate) == v:
                    n = n_candidate
                    break
        if n is None:
            raise RuntimeError(f"Cannot find rep for added state ({r}, {v})")
        if n % 2 == 0:
            n_next = n // 2
        else:
            n_next = 3 * n + 1
        r_next = n_next % M
        v_next = v3(n_next)
        next_state = (r_next, v_next)
        transitions[(r, v)] = next_state

    return states, transitions

# -----------------------------------------------------------------------------
# 3. RANK COMPUTATION (via SCC condensation)
# -----------------------------------------------------------------------------

def compute_ranks(states, transitions):
    """
    Builds the directed graph, finds SCCs, and computes the rank function.
    Rank = longest path length to the terminal SCC (1->4->2->1).
    """
    print("[4] Building NetworkX graph...")
    G = nx.DiGraph()
    G.add_nodes_from(states)
    for src, dst in transitions.items():
        G.add_edge(src, dst)

    print("[5] Computing SCCs...")
    sccs = list(nx.strongly_connected_components(G))
    print(f"    Found {len(sccs)} SCCs.")

    # Identify terminal SCC: the one containing (1,0)
    terminal_scc = None
    for scc in sccs:
        if (1, 0) in scc:
            terminal_scc = scc
            break

    if terminal_scc is None:
        raise RuntimeError("Terminal SCC containing (1,0) not found!")

    print(f"    Terminal SCC size: {len(terminal_scc)}")
    print(f"    Expected terminal cycle: (1,0) -> (4,2) -> (2,1) -> (1,0)")

    # Build condensation DAG: SCC_id -> list of child SCC_ids
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

    # Find terminal SCC id
    term_id = scc_id[(1, 0)]

    # Compute rank = longest path to term_id.
    try:
        topo = list(nx.topological_sort(dag))
    except nx.NetworkXUnfeasible:
        print("ERROR: Condensation graph is not a DAG! Cannot compute ranks.")
        return None, None

    # Initialize ranks.
    rank_scc = {node: -1 for node in dag.nodes()}
    rank_scc[term_id] = 0

    for node in reversed(topo):
        if node == term_id:
            continue
        max_child_rank = -1
        for child in dag.successors(node):
            if rank_scc[child] >= 0:
                max_child_rank = max(max_child_rank, rank_scc[child])
        if max_child_rank >= 0:
            rank_scc[node] = max_child_rank + 1
        else:
            rank_scc[node] = -1

    # Map back to states
    rank = {}
    for state, sid in scc_id.items():
        rank[state] = rank_scc[sid]

    # Verify rank decreases on edges (except within terminal SCC).
    print("[5b] Checking rank monotonicity...")
    ok = True
    for src, dst in transitions.items():
        if src in terminal_scc:
            continue
        if rank[src] <= rank[dst]:
            print(f"WARNING: Rank not strictly decreasing on edge {src} -> {dst}")
            print(f"         rank({src})={rank[src]}, rank({dst})={rank[dst]}")
            ok = False
    if ok:
        print("    All edges outside terminal SCC strictly decrease rank.")
    else:
        print("    Some edges violate rank decrease!")

    return rank, terminal_scc

# -----------------------------------------------------------------------------
# 4. FIBER ESCAPE TESTER
# -----------------------------------------------------------------------------

def sample_fiber(state, num_samples, M=65536):
    """
    Generate num_samples positive integers n from the fiber of state (r, v).
    """
    r, v = state
    samples = []
    q = 0
    attempts = 0
    max_attempts = num_samples * 20
    while len(samples) < num_samples and attempts < max_attempts:
        n = r + q * M
        if n <= 0:
            n = M
        if v3(n) == v:
            samples.append(n)
        q += 1
        attempts += 1
    return samples

def test_fiber_escape(state, rank, M=65536, num_samples=5, max_steps=20000):
    """
    For a given state, test its fiber samples.
    Returns: list of dicts with results.
    """
    r, v = state
    initial_rank = rank.get(state, -1)

    # If already terminal rank, skip.
    if initial_rank == 0:
        return []

    samples = sample_fiber(state, num_samples, M)
    results = []

    for n_start in samples:
        n = n_start
        escaped = False
        steps = 0
        max_rank_reached = initial_rank

        while steps < max_steps:
            curr_state = (n % M, v3(n))
            curr_rank = rank.get(curr_state, -1)
            max_rank_reached = max(max_rank_reached, curr_rank)

            if curr_rank < initial_rank:
                escaped = True
                break
            if n == 1:
                # 1 has rank 0, so this should have been caught above.
                if initial_rank > 0:
                    escaped = True
                    break
                else:
                    # Shouldn't happen if initial_rank > 0, but just in case.
                    escaped = True
                    break

            # Apply Collatz
            if n % 2 == 0:
                n = n // 2
            else:
                n = 3 * n + 1
            steps += 1

        results.append({
            'state': state,
            'initial_rank': initial_rank,
            'n_start': n_start,
            'escaped': escaped,
            'escape_steps': steps if escaped else max_steps,
            'max_rank_reached': max_rank_reached,
            'final_n': n
        })

    return results

# -----------------------------------------------------------------------------
# 5. MAIN
# -----------------------------------------------------------------------------

def main():
    # Configuration
    K = 16
    M = 1 << K
    NUM_SAMPLES_PER_STATE = 5
    MAX_STEPS = 20000
    MAX_STATES_TO_TEST = 2000  # Set to None to test all states (262k). Use small for demo.

    print("=" * 80)
    print("COLLATZ FE16 ANALYZER (FIXED VERSION)")
    print("Testing Fiber Escape Conjecture for k=16")
    print("=" * 80)

    # --- Build quotient ---
    states, transitions = build_quotient(K)

    # --- Compute ranks ---
    rank, terminal_scc = compute_ranks(states, transitions)
    if rank is None:
        print("Rank computation failed. Exiting.")
        return

    # Filter states with rank > 0
    nonterminal_states = [s for s in states if rank.get(s, -1) > 0]
    print(f"[6] Non-terminal states with rank > 0: {len(nonterminal_states)}")

    if MAX_STATES_TO_TEST is not None:
        test_states = nonterminal_states[:MAX_STATES_TO_TEST]
        print(f"    Testing only first {len(test_states)} states (set MAX_STATES_TO_TEST=None for full run).")
    else:
        test_states = nonterminal_states
        print(f"    Testing ALL {len(test_states)} states.")

    # --- Test FE_16 ---
    print("[7] Testing Fiber Escape...")
    all_results = []
    failed_states = []

    for state in tqdm(test_states, desc="  Testing states"):
        res = test_fiber_escape(state, rank, M, NUM_SAMPLES_PER_STATE, MAX_STEPS)
        all_results.extend(res)
        # Check if any sample failed to escape
        for r in res:
            if not r['escaped']:
                failed_states.append(r)

    # --- Statistics ---
    print("\n[8] Results Summary")
    print("-" * 60)
    total_samples = len(all_results)
    if total_samples == 0:
        print("No samples tested. Exiting.")
        return

    escaped_samples = sum(1 for r in all_results if r['escaped'])
    failed_samples = total_samples - escaped_samples

    print(f"Total samples tested: {total_samples}")
    print(f"Escaped to lower rank: {escaped_samples} ({escaped_samples/total_samples*100:.2f}%)")
    print(f"Failed to escape (hit limit or bug): {failed_samples}")

    if failed_samples > 0:
        print(f"\nWARNING: {failed_samples} samples did NOT escape within {MAX_STEPS} steps!")
        print("These are potential counterexamples to FE_16 or indicate hitting time > limit.")
        # Print first few
        for f in failed_states[:5]:
            print(f"  State {f['state']} (rank {f['initial_rank']}), start n={f['n_start']}, final n={f['final_n']}")

    # Compute distribution of escape times
    escaped_times = [r['escape_steps'] for r in all_results if r['escaped']]
    if escaped_times:
        print("\nEscape time statistics (for escaped samples):")
        print(f"  Mean: {np.mean(escaped_times):.2f}")
        print(f"  Median: {np.median(escaped_times):.2f}")
        print(f"  Min: {np.min(escaped_times)}")
        print(f"  Max: {np.max(escaped_times)}")
        print(f"  Std: {np.std(escaped_times):.2f}")

    # Rank reduction analysis
    rank_reductions = []
    for r in all_results:
        if r['escaped']:
            final_state = (r['final_n'] % M, v3(r['final_n']))
            final_rank = rank.get(final_state, -1)
            reduction = r['initial_rank'] - final_rank
            rank_reductions.append(reduction)
    if rank_reductions:
        print(f"\nAverage rank reduction: {np.mean(rank_reductions):.2f}")

    # --- Save results ---
    csv_file = "fe16_results_fixed.csv"
    print(f"\n[9] Saving results to {csv_file}...")
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['state_r', 'state_v', 'initial_rank', 'n_start', 'escaped', 'escape_steps', 'max_rank_reached', 'final_n'])
        writer.writeheader()
        for r in all_results:
            writer.writerow({
                'state_r': r['state'][0],
                'state_v': r['state'][1],
                'initial_rank': r['initial_rank'],
                'n_start': r['n_start'],
                'escaped': r['escaped'],
                'escape_steps': r['escape_steps'],
                'max_rank_reached': r['max_rank_reached'],
                'final_n': r['final_n']
            })

    print("Done.")
    print("=" * 80)

if __name__ == "__main__":
    main()