"""
collatz_reverse_tree_grammar_v4.2.py — SUBIT-COLLATZ v4.2
Reverse Tree + Morphogenetic Grammar (depth 20, leaf fix)
Version 4.2 · 2026
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, Counter
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 0. PATH
# ============================================================================

def get_data_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

# ============================================================================
# 1. REVERSE TREE (DEPTH 20, BETTER SCALING)
# ============================================================================

def preimages(n):
    """Return all positive integer preimages of n under Collatz."""
    pre = [2 * n]
    if n % 3 == 1 and n > 1:
        m = (n - 1) // 3
        if m % 2 == 1 and m > 0:
            pre.append(m)
    return pre

def build_reverse_tree(root=1, max_depth=20, max_nodes=100000):
    """
    Build reverse Collatz tree up to max_depth.
    Returns DiGraph where edge child → parent.
    """
    G = nx.DiGraph()
    G.add_node(root, depth=0)
    current_level = {root}
    depth = 0

    with tqdm(total=max_nodes, desc="Building reverse tree") as pbar:
        while current_level and depth < max_depth and G.number_of_nodes() < max_nodes:
            next_level = set()
            for node in current_level:
                for pre in preimages(node):
                    if pre not in G:
                        G.add_node(pre, depth=depth+1)
                        G.add_edge(pre, node)
                        next_level.add(pre)
                        pbar.update(1)
                        if G.number_of_nodes() >= max_nodes:
                            break
                if G.number_of_nodes() >= max_nodes:
                    break
            current_level = next_level
            depth += 1

    return G

# ============================================================================
# 2. CLASSIFIER (REAL OR SIMULATED)
# ============================================================================

def load_classifier():
    """Try to load real morphotype classifier; fallback to simulated."""
    try:
        df = pd.read_csv(get_data_path("morphotype_signatures.csv"))
        # We would need to build a real classifier; for now, we just use a simple rule.
        # Since the file exists, we could use KNN or centroids, but for simplicity we keep simulation.
        print("Loaded morphotype_signatures.csv (but using simulated classifier for speed).")
    except FileNotFoundError:
        print("morphotype_signatures.csv not found. Using simulated morphotypes (n % 7).")
    # Simulated classifier: return n % 7
    return lambda n: n % 7

# ============================================================================
# 3. PATH GENOMES
# ============================================================================

def extract_path_genomes(G, max_depth):
    """Extract event genomes from nodes at max_depth to root."""
    # Find nodes at max_depth (leaves in our truncated tree)
    leaves = [n for n, data in G.nodes(data=True) if data.get('depth', 0) == max_depth]
    print(f"Found {len(leaves)} nodes at depth {max_depth}.")

    if not leaves:
        print("No nodes at max_depth. Try increasing max_depth.")
        return []

    # Sample if too many
    if len(leaves) > 1000:
        import random
        leaves = random.sample(leaves, 1000)

    path_genomes = []
    for leaf in tqdm(leaves, desc="Extracting paths"):
        try:
            path = nx.shortest_path(G, source=leaf, target=1)
        except nx.NetworkXNoPath:
            continue
        events = []
        for i in range(len(path)-1):
            curr = path[i]
            if curr % 2 == 1:
                events.append('U')
            else:
                events.append('D')
        path_genomes.append(''.join(events))
    return path_genomes

# ============================================================================
# 4. FREQUENT MOTIFS (GRAMMAR INDUCTION)
# ============================================================================

def find_frequent_motifs(genomes, min_support=3, max_len=10):
    motifs = defaultdict(int)
    for g in genomes:
        for L in range(2, min(max_len, len(g))+1):
            for i in range(len(g)-L+1):
                motif = g[i:i+L]
                motifs[motif] += 1
    return {m: c for m, c in motifs.items() if c >= min_support}

# ============================================================================
# 5. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("SUBIT-COLLATZ v4.2: Reverse Tree (depth 20) + Grammar")
    print("=" * 80)

    # Build tree
    print("\n[1] Building reverse Collatz tree (depth=20)...")
    G = build_reverse_tree(root=1, max_depth=20, max_nodes=100000)
    print(f"Tree: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Assign morphotypes (simulated)
    print("\n[2] Assigning morphotypes (simulated mod 7)...")
    classifier = load_classifier()
    morphotypes = {n: classifier(n) for n in G.nodes()}

    # Distribution
    dist = Counter(morphotypes.values())
    print("Morphotype distribution:")
    for mt, cnt in sorted(dist.items()):
        print(f"  M{mt}: {cnt}")

    # Extract path genomes from depth=20 nodes
    print("\n[3] Extracting path genomes from depth-20 nodes to root...")
    path_genomes = extract_path_genomes(G, max_depth=20)
    print(f"Extracted {len(path_genomes)} genomes.")

    if path_genomes:
        print("\nSample genomes (first 5):")
        for g in path_genomes[:5]:
            print(f"  {g[:80]}..." if len(g)>80 else f"  {g}")

        # Motifs
        print("\n[4] Finding frequent motifs (support ≥ 3)...")
        motifs = find_frequent_motifs(path_genomes, min_support=3)
        print(f"Found {len(motifs)} motifs.")
        sorted_motifs = sorted(motifs.items(), key=lambda x: -x[1])
        for motif, count in sorted_motifs[:15]:
            print(f"  '{motif}': {count}")
    else:
        print("No genomes extracted. Try increasing max_depth further.")

    # Save
    with open(get_data_path("reverse_tree_morphotypes.csv"), "w") as f:
        f.write("node,morphotype\n")
        for n, mt in morphotypes.items():
            f.write(f"{n},{mt}\n")
    with open(get_data_path("path_genomes.txt"), "w") as f:
        for g in path_genomes:
            f.write(g + "\n")
    print("\nSaved: reverse_tree_morphotypes.csv, path_genomes.txt")

    # Visualize (only if tree not too large)
    if G.number_of_nodes() <= 2000:
        print("\n[5] Visualizing tree (colored by morphotype)...")
        pos = nx.spring_layout(G, seed=42, k=2)
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f',
                  '#9b59b6', '#e67e22', '#1abc9c', '#95a5a6']
        node_colors = [colors[morphotypes.get(n, 7) % len(colors)] for n in G.nodes()]
        plt.figure(figsize=(14, 10))
        nx.draw(G, pos, node_color=node_colors, with_labels=False,
                node_size=50, edge_color='gray', alpha=0.6)
        plt.title("Reverse Collatz Tree (depth 20) – colored by morphotype")
        plt.savefig(get_data_path("reverse_tree.png"), dpi=150)
        plt.show()
        print("  Saved to reverse_tree.png")
    else:
        print("\n[5] Tree too large for visualization (>2000 nodes). Skipping plot.")

    print("\n" + "=" * 80)
    print("SUBIT-COLLATZ v4.2 COMPLETE")
    print("=" * 80)
    print(f"  • Tree nodes: {G.number_of_nodes()}")
    print(f"  • Path genomes: {len(path_genomes)}")
    print(f"  • Frequent motifs: {len(motifs) if path_genomes else 0}")
    print("\n  Next: Increase depth to 25 or use real morphotype classifier.")


if __name__ == "__main__":
    main()