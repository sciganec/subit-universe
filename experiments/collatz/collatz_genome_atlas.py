"""
collatz_genome_atlas.py — Morphogenetic Genome Atlas of Collatz Trajectories
Version 2.0 · 2026

Transforms trajectories into event genomes, builds signatures of trajectories,
and constructs a morphodynamic atlas of trajectory families.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Dict, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, field
import random
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. TRAJECTORY COMPUTATION
# ============================================================================

def compute_trajectory(n: int, max_steps: int = 10000, max_value: int = 10**12) -> List[int]:
    """Compute the full Collatz trajectory."""
    traj = []
    current = n
    step = 0
    seen = {}
    
    while current not in seen:
        traj.append(current)
        seen[current] = step
        if current == 1:
            break
        if step > max_steps:
            break
        if current > max_value:
            break
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1
        step += 1
    
    return traj


# ============================================================================
# 2. EVENT GENOME — Symbolic Encoding of Trajectory
# ============================================================================

def encode_events(traj: List[int]) -> List[str]:
    """
    Convert trajectory to a sequence of local events.
    Events:
    - U: up (odd step -> 3n+1)
    - D: down (even step -> n/2)
    - P: new global peak
    - R: return below starting value
    - C: entry into a previously visited value (cycle detection)
    """
    if len(traj) < 2:
        return []
    
    events = []
    start = traj[0]
    current_max = traj[0]
    seen = set()
    
    for i in range(1, len(traj)):
        prev = traj[i-1]
        curr = traj[i]
        
        # Direction
        if curr > prev:
            events.append('U')
        else:
            events.append('D')
        
        # Peak
        if curr > current_max:
            events.append('P')
            current_max = curr
        
        # Return below start
        if curr < start:
            events.append('R')
        
        # Cycle detection (if we see a value we've seen before)
        if curr in seen:
            events.append('C')
        seen.add(curr)
    
    return events


def compress_events(events: List[str]) -> List[str]:
    """
    Compress the event sequence by merging consecutive identical events.
    Example: U U U D D -> U3 D2 (or UUU DD)
    """
    if not events:
        return []
    
    compressed = []
    current = events[0]
    count = 1
    
    for e in events[1:]:
        if e == current:
            count += 1
        else:
            if count == 1:
                compressed.append(current)
            else:
                compressed.append(f"{current}{count}")
            current = e
            count = 1
    
    if count == 1:
        compressed.append(current)
    else:
        compressed.append(f"{current}{count}")
    
    return compressed


def event_signature(events: List[str]) -> Dict[str, float]:
    """Extract statistical features from the event sequence."""
    if not events:
        return {}
    
    # Count events
    event_counts = Counter(events)
    total = len(events)
    
    # Compute transition probabilities
    transitions = Counter()
    for i in range(len(events)-1):
        transitions[events[i] + events[i+1]] += 1
    
    # Entropy of events
    probs = [count / total for count in event_counts.values()]
    entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probs)
    
    # Compressibility ratio
    compressed = compress_events(events)
    compression_ratio = len(compressed) / len(events) if events else 1.0
    
    # Run length statistics
    run_lengths = []
    current = events[0]
    length = 1
    for e in events[1:]:
        if e == current:
            length += 1
        else:
            run_lengths.append(length)
            current = e
            length = 1
    run_lengths.append(length)
    
    return {
        'total_events': total,
        'event_types': len(event_counts),
        'entropy': entropy,
        'compression_ratio': compression_ratio,
        'p_U': event_counts.get('U', 0) / total,
        'p_D': event_counts.get('D', 0) / total,
        'p_P': event_counts.get('P', 0) / total,
        'p_R': event_counts.get('R', 0) / total,
        'p_C': event_counts.get('C', 0) / total,
        'avg_run_length': np.mean(run_lengths) if run_lengths else 0,
        'max_run_length': max(run_lengths) if run_lengths else 0,
        'num_peaks': event_counts.get('P', 0),
        'num_returns': event_counts.get('R', 0),
        'transitions': len(transitions),
    }


# ============================================================================
# 3. TRAJECTORY SIGNATURE — Φ(τ)
# ============================================================================

@dataclass
class TrajectorySignature:
    """Φ(τ) — signature of the trajectory itself."""
    n: int
    trajectory: List[int] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    compressed: List[str] = field(default_factory=list)
    
    # Structural features
    length: int = 0
    max_value: int = 0
    max_log: float = 0.0
    stopping_time: int = 0
    
    # Event-based features
    event_entropy: float = 0.0
    event_compression: float = 0.0
    peak_count: int = 0
    return_count: int = 0
    cycle_count: int = 0
    avg_run_length: float = 0.0
    max_run_length: int = 0
    up_ratio: float = 0.0
    down_ratio: float = 0.0
    
    # Complexity metrics
    unique_values: int = 0
    fractal_like: float = 0.0  # rough measure of complexity
    
    def to_vector(self) -> np.ndarray:
        """Convert to feature vector for clustering."""
        return np.array([
            self.length,
            self.max_log,
            self.stopping_time,
            self.event_entropy,
            self.event_compression,
            self.peak_count,
            self.return_count,
            self.cycle_count,
            self.avg_run_length,
            self.max_run_length,
            self.up_ratio,
            self.unique_values,
            self.fractal_like,
        ])
    
    @classmethod
    def from_trajectory(cls, n: int) -> 'TrajectorySignature':
        """Build signature from a trajectory."""
        traj = compute_trajectory(n)
        events = encode_events(traj)
        compressed = compress_events(events)
        event_stats = event_signature(events)
        
        # Compute additional metrics
        unique_vals = len(set(traj))
        max_val = max(traj) if traj else 0
        
        # Fractal-like complexity: ratio of unique values to total length
        fractal_like = unique_vals / len(traj) if traj else 0
        
        return cls(
            n=n,
            trajectory=traj,
            events=events,
            compressed=compressed,
            length=len(traj),
            max_value=max_val,
            max_log=np.log10(max_val + 1) if max_val > 0 else 0,
            stopping_time=len(traj) - 1 if traj else 0,
            event_entropy=event_stats.get('entropy', 0),
            event_compression=event_stats.get('compression_ratio', 1.0),
            peak_count=event_stats.get('num_peaks', 0),
            return_count=event_stats.get('num_returns', 0),
            cycle_count=event_stats.get('p_C', 0) * len(events) if events else 0,
            avg_run_length=event_stats.get('avg_run_length', 0),
            max_run_length=event_stats.get('max_run_length', 0),
            up_ratio=event_stats.get('p_U', 0),
            down_ratio=event_stats.get('p_D', 0),
            unique_values=unique_vals,
            fractal_like=fractal_like,
        )


# ============================================================================
# 4. MORPHODYNAMIC ATLAS
# ============================================================================

class MorphodynamicAtlas:
    """Atlas of trajectory morphotypes."""
    
    def __init__(self):
        self.signatures: List[TrajectorySignature] = []
        self.vectors: np.ndarray = None
        self.labels: np.ndarray = None
        self.projection: np.ndarray = None
        self.morphotypes: Dict[int, List[int]] = {}  # cluster -> list of n
        self.transition_graph: Dict[int, Set[int]] = {}  # cluster -> set of next clusters
    
    def add_trajectories(self, numbers: List[int], progress: bool = True):
        """Add trajectories for a list of numbers."""
        for i, n in enumerate(numbers):
            if progress and i % 1000 == 0:
                print(f"  Processing {i}/{len(numbers)}...")
            sig = TrajectorySignature.from_trajectory(n)
            self.signatures.append(sig)
    
    def build_matrix(self):
        """Build feature matrix from signatures."""
        self.vectors = np.array([sig.to_vector() for sig in self.signatures])
        return self.vectors
    
    def cluster(self, n_clusters: int = 7):
        """Cluster trajectories by their signatures."""
        if self.vectors is None:
            self.build_matrix()
        
        # Normalize
        scaler = StandardScaler()
        scaled = scaler.fit_transform(self.vectors)
        
        # Cluster
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.labels = kmeans.fit_predict(scaled)
        
        # Build morphotype map
        self.morphotypes = defaultdict(list)
        for i, label in enumerate(self.labels):
            self.morphotypes[label].append(self.signatures[i].n)
        
        return self.labels
    
    def project(self, method: str = 'pca', n_components: int = 2):
        """Project signatures to 2D for visualization."""
        if self.vectors is None:
            self.build_matrix()
        
        if method == 'pca':
            pca = PCA(n_components=n_components)
            self.projection = pca.fit_transform(self.vectors)
        elif method == 'tsne':
            tsne = TSNE(n_components=n_components, random_state=42, perplexity=30)
            self.projection = tsne.fit_transform(self.vectors)
        
        return self.projection
    
    def build_transition_graph(self, max_steps: int = 10):
        """Build transition graph between morphotypes."""
        self.transition_graph = defaultdict(set)
        
        for sig in self.signatures:
            n = sig.n
            label = self.labels[self.signatures.index(sig)]
            # Look ahead in trajectory to see which morphotypes it visits
            # (simplified: just track the first few steps)
            current = n
            for _ in range(max_steps):
                if current == 1:
                    break
                if current % 2 == 0:
                    current //= 2
                else:
                    current = 3 * current + 1
                # Find which cluster this new number belongs to
                for other_sig in self.signatures:
                    if other_sig.n == current:
                        other_label = self.labels[self.signatures.index(other_sig)]
                        if other_label != label:
                            self.transition_graph[label].add(other_label)
                        break
        
        return self.transition_graph


# ============================================================================
# 5. VISUALIZATION
# ============================================================================

def plot_morphodynamic_atlas(atlas: MorphodynamicAtlas, title: str = "Morphodynamic Atlas of Collatz Trajectories"):
    """Visualize the atlas with clusters and trajectories."""
    if atlas.projection is None:
        atlas.project()
    
    if atlas.labels is None:
        atlas.cluster()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Clusters
    scatter1 = axes[0].scatter(
        atlas.projection[:, 0], atlas.projection[:, 1],
        c=atlas.labels, cmap='tab10', alpha=0.6, s=20
    )
    axes[0].set_title(f"Morphotypes (k={len(set(atlas.labels))})")
    axes[0].set_xlabel("Projection 1")
    axes[0].set_ylabel("Projection 2")
    plt.colorbar(scatter1, ax=axes[0])
    
    # Plot 2: Color by stopping time
    stopping_times = [sig.stopping_time for sig in atlas.signatures]
    scatter2 = axes[1].scatter(
        atlas.projection[:, 0], atlas.projection[:, 1],
        c=stopping_times, cmap='viridis', alpha=0.6, s=20
    )
    axes[1].set_title("Stopping Time")
    axes[1].set_xlabel("Projection 1")
    axes[1].set_ylabel("Projection 2")
    plt.colorbar(scatter2, ax=axes[1], label="Steps to 1")
    
    plt.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.savefig("morphodynamic_atlas.png", dpi=150)
    plt.show()
    print("  Saved to morphodynamic_atlas.png")


def plot_morphotype_examples(atlas: MorphodynamicAtlas, samples_per_morphotype: int = 2):
    """Plot example trajectories for each morphotype."""
    if atlas.labels is None:
        atlas.cluster()
    
    n_clusters = len(set(atlas.labels))
    fig, axes = plt.subplots(n_clusters, samples_per_morphotype, 
                             figsize=(4*samples_per_morphotype, 3*n_clusters))
    
    if n_clusters == 1:
        axes = axes.reshape(1, -1)
    
    for c in range(n_clusters):
        # Get indices of this cluster
        idx = np.where(atlas.labels == c)[0]
        if len(idx) == 0:
            continue
        # Pick random samples
        sample_idx = np.random.choice(idx, min(samples_per_morphotype, len(idx)), replace=False)
        
        for j, s in enumerate(sample_idx):
            sig = atlas.signatures[s]
            traj = sig.trajectory
            ax = axes[c, j]
            ax.plot(traj, linewidth=0.8)
            ax.set_title(f"Morphotype {c}: n={sig.n}\nsteps={sig.stopping_time}")
            ax.set_xlabel("Step")
            ax.set_ylabel("Value")
            ax.set_yscale('log')
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("morphotype_examples.png", dpi=150)
    plt.show()
    print("  Saved to morphotype_examples.png")


# ============================================================================
# 6. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ MORPHODYNAMIC GENOME ATLAS")
    print("Building atlas of trajectory morphotypes")
    print("=" * 80)
    
    # Configuration
    N_SAMPLES = 3000
    RANGE_START = 1
    RANGE_END = 50000
    N_CLUSTERS = 7
    
    # Generate numbers
    print(f"\n[Phase 1] Generating {N_SAMPLES} numbers from {RANGE_START} to {RANGE_END}...")
    rng = random.Random(42)
    numbers = [rng.randint(RANGE_START, RANGE_END) for _ in range(N_SAMPLES)]
    # Add known interesting numbers
    special = [27, 703, 6171, 837799, 9780657631]
    for n in special:
        if n <= RANGE_END:
            numbers.append(n)
    numbers = list(set(numbers))
    print(f"  Generated {len(numbers)} unique numbers.")
    
    # Build atlas
    print("\n[Phase 2] Building trajectory signatures Φ(τ)...")
    atlas = MorphodynamicAtlas()
    import time
    start = time.time()
    atlas.add_trajectories(numbers, progress=True)
    elapsed = time.time() - start
    print(f"  Computed {len(atlas.signatures)} signatures in {elapsed:.1f}s.")
    
    # Cluster
    print(f"\n[Phase 3] Clustering trajectories into {N_CLUSTERS} morphotypes...")
    atlas.cluster(n_clusters=N_CLUSTERS)
    cluster_counts = [len(atlas.morphotypes[i]) for i in range(N_CLUSTERS)]
    print(f"  Cluster sizes: {cluster_counts}")
    
    # Project
    print("\n[Phase 4] Projecting to 2D (PCA)...")
    atlas.project(method='pca')
    
    # Build transition graph
    print("\n[Phase 5] Building morphotype transition graph...")
    atlas.build_transition_graph(max_steps=20)
    print(f"  Transitions: {dict(atlas.transition_graph)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("ATLAS SUMMARY")
    print("=" * 80)
    print(f"  Total trajectories: {len(atlas.signatures)}")
    print(f"  Morphotypes: {N_CLUSTERS}")
    print(f"  Cluster sizes: {cluster_counts}")
    
    # Find longest trajectory in each morphotype
    print("\n  Representative trajectories (longest in each morphotype):")
    for c in range(N_CLUSTERS):
        idx = np.where(atlas.labels == c)[0]
        if len(idx) > 0:
            best = max(idx, key=lambda i: atlas.signatures[i].stopping_time)
            sig = atlas.signatures[best]
            print(f"    Morphotype {c}: n={sig.n}, steps={sig.stopping_time}, peak=10^{sig.max_log:.1f}")
    
    # Visualize
    print("\n[Phase 6] Visualizing atlas...")
    plot_morphodynamic_atlas(atlas)
    plot_morphotype_examples(atlas, samples_per_morphotype=2)
    
    # Save data
    print("\n[Phase 7] Saving results...")
    import csv
    with open("morphotype_signatures.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "cluster", "length", "max_log", "stopping_time", 
                        "event_entropy", "event_compression", "peak_count", 
                        "return_count", "cycle_count", "avg_run_length", "max_run_length",
                        "up_ratio", "unique_values", "fractal_like"])
        for i, sig in enumerate(atlas.signatures):
            writer.writerow([
                sig.n, atlas.labels[i], sig.length, sig.max_log, sig.stopping_time,
                sig.event_entropy, sig.event_compression, sig.peak_count,
                sig.return_count, sig.cycle_count, sig.avg_run_length, sig.max_run_length,
                sig.up_ratio, sig.unique_values, sig.fractal_like
            ])
    print("  Data saved to morphotype_signatures.csv")
    
    print("\n" + "=" * 80)
    print("MORPHODYNAMIC GENOME ATLAS COMPLETE")
    print("=" * 80)
    print("  Key insight: Trajectories can be classified by their event genomes.")
    print("  This provides a new language for describing Collatz dynamics.")
    print("  Use the transition graph to study how morphotypes evolve.")


if __name__ == "__main__":
    main()