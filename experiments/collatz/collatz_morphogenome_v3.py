"""
collatz_morphogenome_v3.py — SUBIT-COLLATZ v3.0
Morphodynamic Genome + Attractor Topology Map
Version 3.0 · 2026
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Try to import umap, fallback to PCA if not available
try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False
    print("UMAP not installed. Using PCA instead. Install with: pip install umap-learn")


# ============================================================================
# 0. PATH UTILITIES
# ============================================================================

def get_data_path(filename):
    """Return absolute path to data file in the script's directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)


# ============================================================================
# 1. LOAD DATA
# ============================================================================

def load_data(results_file='generalized_collatz_results_v2.1.csv',
              catalog_file='attractor_catalog.csv'):
    """Load results and catalog from the script's directory."""
    results_path = get_data_path(results_file)
    catalog_path = get_data_path(catalog_file)
    
    if not os.path.exists(results_path):
        raise FileNotFoundError(f"Results file not found: {results_path}")
    if not os.path.exists(catalog_path):
        raise FileNotFoundError(f"Catalog file not found: {catalog_path}")
    
    results = pd.read_csv(results_path)
    catalog = pd.read_csv(catalog_path)
    return results, catalog


# ============================================================================
# 2. GENOME FEATURES
# ============================================================================

def compute_genome_features(results, catalog, k, c):
    """Compute 10-dimensional genome vector for a rule (k,c)."""
    row = results[(results['k'] == k) & (results['c'] == c)].iloc[0]
    cycles = catalog[(catalog['k'] == k) & (catalog['c'] == c)]
    
    cycle_lengths = cycles['length'].tolist() if not cycles.empty else []
    num_attractors = len(cycle_lengths)
    mean_cycle_len = np.mean(cycle_lengths) if cycle_lengths else 0
    max_cycle_len = max(cycle_lengths) if cycle_lengths else 0
    
    # Compute cycle diversity: number of distinct cycle lengths
    cycle_diversity = len(set(cycle_lengths)) if cycle_lengths else 0
    
    # Compute basin entropy (if not already present)
    basin_entropy = row.get('basin_entropy', 0)
    if basin_entropy == 0 and cycle_lengths:
        # Approximate basin entropy from cycle length distribution
        # For now, just use the number of attractors as a proxy
        basin_entropy = np.log(num_attractors + 1)
    
    return {
        'k': k,
        'c': c,
        'omega': row['omega'],
        'stable_fraction': row['stable_count'] / 100,
        'escape_fraction': row['chaotic_count'] / 100,
        'cyclic_fraction': row['cyclic_count'] / 100,
        'num_attractors': num_attractors,
        'mean_cycle_len': mean_cycle_len,
        'max_cycle_len': max_cycle_len,
        'basin_entropy': basin_entropy,
        'cycle_diversity': cycle_diversity,
    }


def build_genome_matrix(results, catalog):
    """Build genome matrix for all rules."""
    genomes = []
    for _, row in results.iterrows():
        k, c = int(row['k']), int(row['c'])
        g = compute_genome_features(results, catalog, k, c)
        genomes.append(g)
    return pd.DataFrame(genomes)


# ============================================================================
# 3. MORPHOLOGICAL SPACE PROJECTION
# ============================================================================

def project_morphospace(genome_df, method='umap', n_components=2):
    """Project genome vectors into 2D morphospace."""
    feature_cols = ['stable_fraction', 'escape_fraction', 'cyclic_fraction',
                    'num_attractors', 'mean_cycle_len', 'max_cycle_len',
                    'basin_entropy', 'cycle_diversity']
    X = genome_df[feature_cols].values
    
    # Handle NaN or inf values
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    if method == 'umap' and HAS_UMAP:
        reducer = umap.UMAP(n_components=n_components, random_state=42)
        embedding = reducer.fit_transform(X_scaled)
    else:
        if method == 'umap' and not HAS_UMAP:
            print("UMAP not available, falling back to PCA.")
        reducer = PCA(n_components=n_components)
        embedding = reducer.fit_transform(X_scaled)
        explained = reducer.explained_variance_ratio_.sum()
        print(f"PCA explained variance: {explained:.3f}")
    
    genome_df['x'] = embedding[:, 0]
    genome_df['y'] = embedding[:, 1] if n_components > 1 else 0
    return genome_df


# ============================================================================
# 4. CLUSTERING IN MORPHOSPACE
# ============================================================================

def cluster_morphospace(genome_df, n_clusters=4):
    """Cluster rules in morphospace."""
    X = genome_df[['x', 'y']].values
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    genome_df['morphocluster'] = kmeans.fit_predict(X)
    return genome_df


# ============================================================================
# 5. VISUALIZATION
# ============================================================================

def plot_morphospace(genome_df, save_path='rule_morphospace.png'):
    """Plot morphospace with clusters and labels."""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Color by Ω-class
    omega_colors = {'STABLE': '#2ecc71', 'CYCLIC': '#e74c3c', 
                    'CHAOTIC': '#34495e', 'MIXED': '#f1c40f'}
    colors = [omega_colors.get(omega, 'gray') for omega in genome_df['omega']]
    
    scatter = ax.scatter(genome_df['x'], genome_df['y'], 
                         c=colors, s=120, alpha=0.8, edgecolors='black', linewidth=0.5)
    
    # Annotate
    for _, row in genome_df.iterrows():
        label = f"({int(row['k'])},{int(row['c'])})"
        ax.annotate(label, (row['x'], row['y']), fontsize=9, alpha=0.8, 
                   xytext=(3, 3), textcoords='offset points')
    
    ax.set_title("Morphological Space of Generalized Collatz Rules", fontsize=14)
    ax.set_xlabel("UMAP1" if HAS_UMAP else "PC1", fontsize=12)
    ax.set_ylabel("UMAP2" if HAS_UMAP else "PC2", fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', label='STABLE'),
        Patch(facecolor='#e74c3c', label='CYCLIC'),
        Patch(facecolor='#34495e', label='CHAOTIC'),
        Patch(facecolor='#f1c40f', label='MIXED')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    full_path = get_data_path(save_path)
    plt.savefig(full_path, dpi=150)
    plt.show()
    print(f"Morphospace saved to {full_path}")


def plot_genome_heatmap(genome_df, save_path='genome_heatmap.png'):
    """Heatmap of genome features across rules."""
    feature_cols = ['stable_fraction', 'escape_fraction', 'cyclic_fraction',
                    'num_attractors', 'mean_cycle_len', 'max_cycle_len',
                    'basin_entropy', 'cycle_diversity']
    labels = [f"({int(row['k'])},{int(row['c'])})" for _, row in genome_df.iterrows()]
    X = genome_df[feature_cols].values
    
    # Normalize for better visualization
    X = np.nan_to_num(X, nan=0.0)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(X, annot=True, fmt='.2f', cmap='viridis',
                xticklabels=feature_cols, yticklabels=labels, ax=ax)
    ax.set_title("Genome Features per Rule", fontsize=14)
    plt.tight_layout()
    full_path = get_data_path(save_path)
    plt.savefig(full_path, dpi=150)
    plt.show()
    print(f"Genome heatmap saved to {full_path}")


def plot_cluster_summary(genome_df, save_path='cluster_summary.png'):
    """Plot summary of morphological clusters."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    ax = axes[0, 0]
    cluster_counts = genome_df['morphocluster'].value_counts().sort_index()
    ax.bar(cluster_counts.index, cluster_counts.values, color='steelblue')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Number of rules')
    ax.set_title('Cluster Sizes')
    
    ax = axes[0, 1]
    # Stable fraction by cluster
    stable_by_cluster = genome_df.groupby('morphocluster')['stable_fraction'].mean()
    ax.bar(stable_by_cluster.index, stable_by_cluster.values, color='#2ecc71')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Mean Stable Fraction')
    ax.set_title('Stability by Cluster')
    
    ax = axes[1, 0]
    # Cycle count by cluster
    cycles_by_cluster = genome_df.groupby('morphocluster')['num_attractors'].mean()
    ax.bar(cycles_by_cluster.index, cycles_by_cluster.values, color='#e74c3c')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Mean Number of Attractors')
    ax.set_title('Attractor Count by Cluster')
    
    ax = axes[1, 1]
    # Max cycle length by cluster
    max_cycle_by_cluster = genome_df.groupby('morphocluster')['max_cycle_len'].mean()
    ax.bar(max_cycle_by_cluster.index, max_cycle_by_cluster.values, color='#f39c12')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Mean Max Cycle Length')
    ax.set_title('Maximum Cycle Length by Cluster')
    
    plt.tight_layout()
    full_path = get_data_path(save_path)
    plt.savefig(full_path, dpi=150)
    plt.show()
    print(f"Cluster summary saved to {full_path}")


# ============================================================================
# 6. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("SUBIT-COLLATZ v3.0: Morphodynamic Genome + Attractor Topology")
    print("=" * 80)
    
    # Load data
    try:
        results, catalog = load_data()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure the data files are in the same directory as this script.")
        print("Expected files: generalized_collatz_results_v2.1.csv and attractor_catalog.csv")
        return
    
    print(f"Loaded {len(results)} rules, {len(catalog)} attractors")
    
    # Build genome matrix
    genome_df = build_genome_matrix(results, catalog)
    print(f"Built genome matrix: {len(genome_df)} rules x {len(genome_df.columns)-3} features")
    
    # Project into morphospace
    genome_df = project_morphospace(genome_df, method='umap' if HAS_UMAP else 'pca')
    print("Projected into 2D morphospace")
    
    # Cluster
    genome_df = cluster_morphospace(genome_df, n_clusters=4)
    print("Clustered into 4 morphological families")
    
    # Visualize
    plot_morphospace(genome_df)
    plot_genome_heatmap(genome_df)
    plot_cluster_summary(genome_df)
    
    # Print cluster summary
    print("\n" + "=" * 80)
    print("MORPHOLOGICAL FAMILIES")
    print("=" * 80)
    for cluster in sorted(genome_df['morphocluster'].unique()):
        rules = genome_df[genome_df['morphocluster'] == cluster]
        omegas = rules['omega'].value_counts()
        print(f"\n  Cluster {cluster} ({len(rules)} rules):")
        for omega, count in omegas.items():
            print(f"    {omega}: {count} ({count/len(rules)*100:.1f}%)")
        rule_list = [f"({int(r.k)},{int(r.c)})" for _, r in rules.iterrows()]
        print(f"    Rules: {rule_list}")
    
    # Highlight classic Collatz
    classic = genome_df[(genome_df['k'] == 3) & (genome_df['c'] == 1)]
    if not classic.empty:
        row = classic.iloc[0]
        print(f"\n  Classic Collatz (3,1) is in cluster {int(row['morphocluster'])}")
    
    print("\n" + "=" * 80)
    print("SUBIT-COLLATZ v3.0 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()