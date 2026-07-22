# SUBIT-COLLATZ: A Morphodynamic Genome Atlas of the Generalized Collatz Family

**Authors:** SUBIT Research Group  
**Affiliation:** SUBIT-TOPOS Project  
**Date:** 2026-07-22  
**Status:** Preprint

---

## Abstract

We present a systematic morphodynamic analysis of the generalized Collatz family, defined by the map \( T(n) = n/2 \) if \( n \) is even, and \( T(n) = k n + c \) otherwise, where \( k \) and \( c \) are integer parameters. Using the SUBIT-TOPOS framework, we explore the parameter space \( k \in [2,7] \), \( c \in [1,9] \) (54 combinations) by sampling 100 trajectories per combination and extracting a 10‑dimensional genome vector for each rule. The genome captures the rule's dynamical behavior, including stability fraction, escape fraction, attractor counts, cycle length statistics, and basin entropy. We then project the genome vectors into a 2D morphospace using UMAP, revealing four distinct morphological clusters. We find that only 4 out of 54 rules are empirically stable (including the classic Collatz map \( (k,c)=(3,1) \)), while the majority exhibit cycles or unbounded growth. The classic Collatz map is not isolated but belongs to a cluster containing other stable and cyclic rules. Our results demonstrate that the generalized Collatz parameter space is morphologically stratified and that the SUBIT-TOPOS framework provides a novel perspective on discrete dynamical systems by treating rules as dynamical objects with measurable genomic signatures.

**Keywords:** Collatz conjecture, generalized Collatz maps, dynamical systems, morphodynamic analysis, SUBIT-TOPOS, attractor topology, parameter space exploration.

---

## 1. Introduction

The Collatz conjecture (also known as the \( 3n+1 \) problem) is a longstanding open problem in number theory. It states that iterating the map \( T(n) = n/2 \) if \( n \) is even, \( T(n) = 3n+1 \) otherwise, eventually reaches the cycle \( 1 \to 4 \to 2 \to 1 \) for every positive integer \( n \). Despite extensive computational verification for \( n \) up to enormous bounds, a proof remains elusive.

Traditional approaches have focused on individual trajectories, analyzing stopping times, maximum excursions, and statistical distributions. However, these methods treat each trajectory in isolation and miss the structural relationships between different dynamical behaviours. In this work, we adopt a different perspective: instead of asking whether every trajectory reaches 1, we ask what is the morphological structure of the space of trajectories and, more generally, of the parameter space of a family of related maps.

We study the **generalized Collatz family**:

\[
T_{k,c}(n) =
\begin{cases}
n/2 & \text{if } n \text{ is even},\\
k n + c & \text{if } n \text{ is odd},
\end{cases}
\]

where \( k \) and \( c \) are positive integers. The classic Collatz map corresponds to \( (k,c) = (3,1) \). By varying \( k \) and \( c \), we explore a broader class of maps and ask: how does the dynamical behaviour of these maps change across the parameter space? Are there structural regions of stability, cyclic behaviour, or unbounded growth?

To answer these questions, we employ the **SUBIT-TOPOS** framework, a general-purpose morphodynamic analysis system that treats rules as dynamical objects and computes genomic signatures of their behaviour.

### 1.1 Contributions

1. We introduce a **10‑dimensional genome vector** for each rule, capturing its stability, attractor count, cycle length distribution, and basin entropy.
2. We construct a **morphodynamic atlas** of 54 rules by projecting their genome vectors into a 2D space using UMAP, revealing four distinct morphological clusters.
3. We identify a **morphological family** containing the classic Collatz map along with other stable and cyclic rules.
4. We demonstrate that the SUBIT-TOPOS framework can systematically map the morphology of a parameterized family of discrete dynamical systems.

---

## 2. Methods

### 2.1 Generalized Collatz Map

We define the map:

\[
T_{k,c}(n) =
\begin{cases}
n/2, & n \equiv 0 \pmod{2},\\
k n + c, & n \equiv 1 \pmod{2}.
\end{cases}
\]

We fix the divisor to be 2 (the classic case) and vary \( k \in [2,7] \) and \( c \in [1,9] \), resulting in 54 parameter combinations. For each combination, we sample 100 random starting numbers from the interval \( [1,2000] \). Each trajectory is simulated for up to 5,000 steps, with a maximum value cutoff of \( 10^{12} \). Trajectories that exceed this limit are classified as **CHAOTIC** (unresolved). Trajectories that enter a cycle not containing 1 are classified as **CYCLIC**. Trajectories that reach 1 are classified as **STABLE**. If a combination exhibits a mixture of behaviours (e.g., some stable, some cyclic), it is classified as **MIXED**.

### 2.2 Genome Vector for a Rule

For each rule \( (k,c) \), we compute the following 10‑dimensional genome vector:

\[
G(k,c) = \left[
\begin{array}{l}
\text{stable\_fraction},\\
\text{escape\_fraction},\\
\text{cyclic\_fraction},\\
\text{num\_attractors},\\
\text{mean\_cycle\_len},\\
\text{max\_cycle\_len},\\
\text{basin\_entropy},\\
\text{cycle\_diversity}
\end{array}
\right]
\]

Each component is defined as follows:

- **stable_fraction**: fraction of sampled trajectories that reach 1.
- **escape_fraction**: fraction of sampled trajectories that exceed the value limit.
- **cyclic_fraction**: fraction of sampled trajectories that enter a non‑trivial cycle.
- **num_attractors**: number of distinct cycles found for this rule.
- **mean_cycle_len**: average length of the cycles.
- **max_cycle_len**: length of the longest cycle.
- **basin_entropy**: entropy of the distribution of trajectories across attractors (approximated as \( \log(\text{num\_attractors}+1) \) when not directly available).
- **cycle_diversity**: number of distinct cycle lengths observed.

### 2.3 Morphospace Projection (UMAP)

We apply UMAP (Uniform Manifold Approximation and Projection) to the normalized genome vectors to project them into a 2D space. The UMAP parameters are set to \( n\_neighbors=15 \), \( min\_dist=0.1 \), and \( random\_state=42 \) for reproducibility. The resulting coordinates \( (x,y) \) define the **morphospace** of the rules.

### 2.4 Clustering in Morphospace

We apply K‑means clustering to the projected coordinates to identify distinct morphological families. The number of clusters is set to \( K=4 \) based on the elbow method.

---

## 3. Results

### 3.1 Ω‑class Distribution

Across the 54 parameter combinations, the classification is:

| Ω‑class | Count | Percentage |
|---------|-------|------------|
| CHAOTIC | 33 | 61.1% |
| CYCLIC | 14 | 25.9% |
| STABLE | 4 | 7.4% |
| MIXED | 3 | 5.6% |

**Only 4 out of 54 rules are empirically stable.** The stable rules are:

- \( (k,c) = (2,2) \)
- \( (k,c) = (3,1) \) *(classic Collatz)*
- \( (k,c) = (4,4) \)
- \( (k,c) = (6,2) \)

All other rules produce either cycles (25.9%) or unresolved trajectories (61.1%), with a few mixed cases.

### 3.2 Morphological Clusters

The UMAP projection reveals four distinct clusters:

| Cluster | Size | Composition | Key Rules |
|---------|------|-------------|-----------|
| **0** | 12 | 8 CYCLIC (66.7%), 4 STABLE (33.3%) | (2,2), (3,1) classic, (4,4), (6,2), plus cyclic (2,6), (3,5), (5,9) |
| **1** | 13 | 100% CHAOTIC | (2,1), (2,5), (2,9), (3,4), (4,3), (4,5), (4,6), (5,8), (6,4), (6,7), (6,9), (7,1), (7,3) |
| **2** | 20 | 100% CHAOTIC | (2,3), (2,7), (3,2), (3,6), (3,8), (4,1), (4,2), (4,7), (4,9), (5,2), (5,4), (5,6), (6,1), (6,3), (6,5), (6,8), (7,2), (7,4), (7,6), (7,8) |
| **3** | 9 | 6 CYCLIC (66.7%), 3 MIXED (33.3%) | (2,4), (2,8), (3,3), (3,9), (4,8), (5,1), (6,6), (7,7), (7,9) |

**Key observation:** The classic Collatz map (3,1) belongs to Cluster 0, which includes other stable rules as well as cyclic rules. This indicates that the classic map is not an isolated stable point but part of a broader morphological region.

### 3.3 Attractor Catalog

A total of **38 unique cycles** were identified across the parameter space. Cycle lengths range from 3 to 90, with a mean of 14.3 and a median of 10. The most complex attractor landscape was found for \( (k,c) = (5,9) \), which exhibits cycles of lengths 4, 7, 10, 30, and 90. This suggests a hierarchical structure of attractors within a single parameter combination, where trajectories can settle into different cycles depending on the starting point.

---

## 4. Discussion

### 4.1 Stability is Rare but Structured

Our results show that empirical stability is rare in the explored parameter space (7.4%). However, the stable rules are not scattered randomly; they form a distinct sub‑group within Cluster 0. This suggests that stability is a special case of a broader class of behaviours that include both stable and cyclic dynamics. The classic Collatz map (3,1) is a member of this group.

### 4.2 The CHAOTIC Regime is Divided into Two Clusters

The 33 CHAOTIC rules are split between Cluster 1 (13 rules) and Cluster 2 (20 rules). This indicates that there are at least two qualitatively different types of "escape" behaviour: one that may correspond to rapid divergence and another that may correspond to very long transients or rare large cycles. This distinction is not captured by a simple binary classification and highlights the value of the morphodynamic approach.

### 4.3 Attractor Hierarchies

The discovery of multiple cycles for a single parameter combination, especially for (5,9), suggests that the attractor landscape can be complex even for relatively simple rules. The presence of cycle lengths forming a hierarchical pattern (4, 7, 10, 30, 90) hints at possible structural relationships between cycles, which could be investigated further.

### 4.4 SUBIT-TOPOS as a Morphodynamic Discovery Engine

This study demonstrates the value of the SUBIT-TOPOS approach. Instead of asking "does every trajectory reach 1?" for a single rule, we map the behaviour of a family of rules and identify structural patterns in their dynamics. The genome vector, morphospace projection, and clustering pipeline provide a systematic way to compare and classify dynamical systems.

---

## 5. Conclusions

We have conducted a systematic morphodynamic analysis of the generalized Collatz family using the SUBIT-TOPOS framework. Our main findings are:

1. **Stability is rare and structured:** Only 4 out of 54 rules are empirically stable, and they form a distinct sub‑group within a larger morphological cluster that also contains many cyclic rules.

2. **CHAOTIC behaviour is dominant and divided into two types:** 61% of the rules produce unresolved trajectories, and they split into two distinct morphological clusters.

3. **Attractor landscapes can be complex:** Some rules, like (5,9), exhibit multiple cycles with a hierarchical length structure, suggesting that the attractor topology can be rich.

4. **The classic Collatz map is not an isolated case:** It belongs to a broader region of the parameter space containing both stable and cyclic rules, supporting the view that the Collatz conjecture is a special instance of a larger phenomenon.

Our work shows that the SUBIT-TOPOS framework provides a new perspective on discrete dynamical systems by focusing on morphological classification and structural relationships rather than individual trajectories.

---

## 6. Future Work

- Expand the parameter space to larger \( k \) and \( c \) ranges and include other divisors \( d \).
- Compute additional genome features, such as Lyapunov exponents, parity entropy, and fractal dimensions of basins.
- Build a graph of attractor relationships to study hierarchical structures.
- Use the morphospace projection to guide the meta‑evolution of rules in the SUBIT-TOPOS framework.

---

## 7. Data Availability

All data and code are available in the SUBIT-TOPOS repository:

- `generalized_collatz_results_v2.1.csv`: detailed results per rule.
- `attractor_catalog.csv`: list of unique cycles with metadata.
- `rule_morphospace.png`, `genome_heatmap.png`, `cluster_summary.png`: visualizations.
- `collatz_morphogenome_v3.py`: code for reproducing the analysis.

---

## 8. References

1. Collatz, L. (1937). "On the problem of 3n+1". *Problem 256*.
2. Lagarias, J. C. (1985). "The 3x+1 problem and its generalizations". *American Mathematical Monthly*.
3. Aczel, P. (1988). *Non‑Well‑Founded Sets*. CSLI Publications.
4. SUBIT-TOPOS Specification v2.0 (2026). "A recursive semantic universe".

---

## Appendix A: Cycle Catalog

The full list of 38 unique cycles with lengths and min/max values is provided in `attractor_catalog.csv`. A summary is given in Table 1.

**Table 1: Selected cycles by parameter.**

| (k,c) | Cycle Length | Cycle (first elements) |
|-------|--------------|------------------------|
| (2,6) | 3 | [3, 12, 6] |
| (3,5) | 3 | [5, 20, 10] |
| (3,5) | 8 | [19, 62, 31, 98, 49, 152, 76, 38] |
| (3,5) | 44 | [187, 566, 283, 854, 427, ...] |
| (5,9) | 4 | [3, 24, 12, 6] |
| (5,9) | 7 | [9, 54, 27, 144, 72, 36, 18] |
| (5,9) | 10 | [117, 594, 297, ...] |
| (5,9) | 30 | [89, 454, 227, ...] |
| (5,9) | 90 | [29, 154, 77, 394, ...] |
| (7,5) | 42 | [27, 194, 97, ...] |

---

## Appendix B: Genome Features by Cluster

The average genome features for each cluster are given in Table 2.

**Table 2: Mean genome features by cluster.**

| Cluster | stable_fraction | escape_fraction | cyclic_fraction | num_attractors | mean_cycle_len | max_cycle_len | basin_entropy | cycle_diversity |
|---------|-----------------|-----------------|-----------------|----------------|----------------|---------------|---------------|-----------------|
| 0 | 0.38 | 0.18 | 0.44 | 1.8 | 12.3 | 27.5 | 0.65 | 1.6 |
| 1 | 0.01 | 0.99 | 0.00 | 0.0 | 0.0 | 0.0 | 0.00 | 0.0 |
| 2 | 0.02 | 0.98 | 0.00 | 0.0 | 0.0 | 0.0 | 0.00 | 0.0 |
| 3 | 0.06 | 0.33 | 0.61 | 1.1 | 5.4 | 10.8 | 0.38 | 1.0 |

Cluster 0 has the highest stability fraction and the most complex attractor landscape (highest num_attractors, mean_cycle_len, max_cycle_len). Clusters 1 and 2 are almost purely CHAOTIC. Cluster 3 is a mixture of cyclic and mixed behaviour.

---

*This manuscript was prepared using the SUBIT-TOPOS framework and is intended for submission to a peer‑reviewed journal.*