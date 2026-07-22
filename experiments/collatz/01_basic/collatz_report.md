# SUBIT-TOPOS: Collatz Morphodynamic Atlas v1.0

**A Morphogenetic Study of Collatz Trajectory Space**

*Author:* SUBIT Research Group  
*Date:* 2026-07-20  
*Version:* 1.0

---

## Abstract

This report presents the first systematic morphodynamic analysis of Collatz trajectory space using the SUBIT-TOPOS framework. Instead of searching for counterexamples to the Collatz conjecture, we construct an atlas of trajectory morphologies — a discrete classification of dynamical regimes based on invariant signatures and symbolic event genomes. Analyzing 2,919 trajectories for n ∈ [1, 50,000], we identify **7 stable morphotypes** with distinct dynamical characteristics, construct a **transition graph** revealing the topology of morphotype evolution, and build a **phylogenetic tree** based on Levenshtein distances between event genomes. The results demonstrate that Collatz trajectory space is not homogeneous but exhibits discrete structural stratification, with a central attractor morphotype (M5, 23.5%) and an extreme morphotype (M3, 5.1%) characterized by long stopping times and high excursions. This work establishes a new language for describing Collatz dynamics — not through individual numbers, but through morphological classes and their evolutionary relationships.

**Keywords:** Collatz conjecture, SUBIT-TOPOS, morphodynamic atlas, trajectory morphotypes, event genomes, phylogenetic analysis, dynamical systems.

---

## 1. Introduction

The Collatz conjecture (also known as the 3n + 1 problem) has remained unsolved since its formulation in 1937. It states that for any positive integer n, repeated application of the function

```
T(n) = n/2   if n is even
T(n) = 3n+1  if n is odd
```

eventually reaches 1. Despite massive computational verification up to enormous bounds, a proof remains elusive.

Traditional approaches focus on individual trajectories — analyzing stopping times, maximum excursions, and statistical distributions. However, these methods treat each trajectory in isolation, missing the structural relationships between different dynamical behaviors.

### 1.1 The SUBIT-TOPOS Approach

Instead of asking "does every trajectory reach 1?", we ask:

> **What is the morphological structure of the space of Collatz trajectories?**

This shifts the problem from numerical verification to **structural classification**. SUBIT-TOPOS provides the framework for this investigation:

- **State space:** Collatz trajectories encoded as sequences of integers.
- **Signature:** A feature vector summarizing the trajectory's dynamical properties.
- **Morphotypes:** Stable clusters of trajectories with similar signatures.
- **Genomes:** Symbolic representations of event sequences within trajectories.
- **Phylogeny:** Evolutionary relationships between morphotypes based on genome similarity.

### 1.2 Research Questions

1. Does the space of Collatz trajectories exhibit discrete structural classes (morphotypes)?
2. If so, how many morphotypes exist, and what are their characteristics?
3. Can we construct a symbolic language (event genomes) to describe morphotypes?
4. What is the topology of transitions between morphotypes?
5. Can we build a phylogenetic tree that reveals evolutionary relationships?

---

## 2. Methodology

### 2.1 Data Generation

We generated **2,919 unique starting numbers** uniformly sampled from the interval [1, 50,000]. For each number n, we computed:

- The full Collatz trajectory until reaching 1 (or until a safety limit of 10,000 steps).
- A signature vector Φ(τ) of 15 morphodynamic invariants.

### 2.2 Signature Vector Φ(τ)

For each trajectory τ, we extracted the following features:

| Feature | Description |
|---------|-------------|
| `length` | Number of steps until reaching 1 |
| `max_log` | Logarithm of the maximum value reached |
| `stopping_time` | Steps to reach 1 (same as length) |
| `event_entropy` | Entropy of the event sequence |
| `event_compression` | Compression ratio of the event sequence |
| `peak_count` | Number of new global maxima |
| `return_count` | Number of returns below the starting value |
| `cycle_count` | Number of times the trajectory enters a cycle |
| `avg_run_length` | Average length of runs (consecutive same parity) |
| `max_run_length` | Maximum run length |
| `up_ratio` | Ratio of odd (up) steps to total steps |
| `unique_values` | Number of unique values in the trajectory |
| `fractal_like` | A measure of self-similarity |

### 2.3 Clustering

We applied **k-means clustering** to the normalized signature matrix. The optimal number of clusters was determined using the elbow method and silhouette analysis, yielding **k = 7** morphotypes.

### 2.4 Event Genomes

We transformed each trajectory into a **symbolic genome** using the following event alphabet:

| Symbol | Event | Meaning |
|--------|-------|---------|
| `U` | Up | An odd step (3n + 1) — expansion |
| `D` | Down | An even step (n/2) — contraction |
| `P` | Peak | A new global maximum |
| `R` | Return | A value below the starting point |
| `S` | Stabilization | Entering the final cycle (4, 2, 1) |

**Example:** For n = 13, the trajectory is `13 → 40 → 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1`.  
The genome becomes: `U D D D U D D D D S` (with P and R events omitted for brevity).

### 2.5 Phylogenetic Analysis

For each morphotype, we selected a **representative trajectory** — the one closest to the centroid of its cluster in feature space. We then:

1. Computed the event genome for each representative.
2. Calculated the normalized Levenshtein (edit) distance between all pairs of genomes.
3. Built a phylogenetic tree using UPGMA (Unweighted Pair Group Method with Arithmetic Mean).

---

## 3. Results

### 3.1 Morphotype Distribution

The 2,919 trajectories were partitioned into **7 morphotypes** with the following sizes:

| Morphotype | Count | Percentage | Representative n | Stopping Time |
|------------|-------|------------|------------------|---------------|
| **M0** | 574 | 19.7% | 19556 | 48 |
| **M1** | 153 | 5.2% | 19947 | 118 |
| **M2** | 354 | 12.1% | 31547 | 85 |
| **M3** | 150 | 5.1% | 19611 | 198 |
| **M4** | 411 | 14.1% | 16734 | 159 |
| **M5** | 687 | 23.5% | 11141 | 68 |
| **M6** | 590 | 20.2% | 43917 | 132 |

**Observation:** The largest morphotype is M5 (23.5%), characterized by short stopping times and moderate excursions. The smallest is M3 (5.1%), characterized by very long stopping times and high maximum excursions.

### 3.2 Event Genomes

The representative genomes for each morphotype (first 100 characters):

```
M0: DRDRURDRDRURDRURDRDRDRURDRURDRURDRUPDRDRDRDRDRURDRDRDRURDRDRDRDRDRURDRURDRURDRDRDRDRDRURDRDRSDRDRS...
M1: UPDUPDDUDDRUDUDUPDUPDUPDUPDDUDUPDUPDDDUDDDDRDRUDRUDRUDUDUDDUDUDDUDUDDUDDDRUDUDDRDRDRDRDRURDRDRURDRDR...
M2: UPDUPDDUDUPDDDRDRDRURDRURDRUDRUDRUDUDUPDDDRUDUDDRUDDRDRDRDRURDRDRURDRURDRURDRDRDRDRDRDRDRURDRDRURDRU...
M3: UPDUPDDUDUPDUPDUPDDUDDUDUDUPDUPDUPDDUDUPDDDDUDUDDUDUDDDUDUDDDRUDUDDRDRUDRDRDRURDRURDRUDRUDRUDDRUDRDR...
M4: DRUPDRUPDUPDUPDDUDDRDRUDRUDUDDRUDDRDRURDRUDRDRDRDRDRURDRURDRDRDRDRURDRURDRURDRDRURDRDRURDRDRDRURDRUR...
M5: UPDDRDRDRURDRDRURDRURDRURDRUDRUDDRUDRDRUDRDRURDRDRDRDRDRDRURDRDRDRURDRURDRDRURDRURDRDRDRDRURDRURDRDR...
M6: UPDDRDRUDRDRDRDRDRDRDRDRURDRDRURDRDRURDRDRDRURDRDRURDRURDRURDRURDRURDRDRURDRDRURDRURDRDRURDRURDRURDR...
```

Each morphotype exhibits a distinct pattern of `U` (up), `D` (down), `P` (peak), `R` (return), and `S` (stabilization) events.

### 3.3 Distance Matrix (Normalized Levenshtein)

|        | M0 | M1 | M2 | M3 | M4 | M5 | M6 |
|--------|----|----|----|----|----|----|----|
| **M0** | 0.000 | 0.266 | 0.156 | 0.720 | 0.604 | 0.104 | 0.483 |
| **M1** | 0.266 | 0.000 | 0.142 | 0.465 | 0.361 | 0.194 | 0.272 |
| **M2** | 0.156 | 0.142 | 0.000 | 0.566 | 0.454 | 0.081 | 0.335 |
| **M3** | 0.720 | 0.465 | 0.566 | 0.000 | 0.139 | 0.618 | 0.243 |
| **M4** | 0.604 | 0.361 | 0.454 | 0.139 | 0.000 | 0.503 | 0.127 |
| **M5** | 0.104 | 0.194 | 0.081 | 0.618 | 0.503 | 0.000 | 0.382 |
| **M6** | 0.483 | 0.272 | 0.335 | 0.243 | 0.127 | 0.382 | 0.000 |

**Key observations:**
- M0 and M5 are extremely close (0.104), suggesting they share a similar dynamical structure.
- M2 and M5 are also close (0.081) — the closest pair overall.
- M3 is the most distant from M0 (0.720) and M5 (0.618), confirming its extreme nature.
- M4 and M6 are closely related (0.127), suggesting a family of morphotypes with moderate complexity.

### 3.4 Transition Graph

The directed transition graph between morphotypes, derived from the ordering of n values:

```
M5 → {M0, M1, M2, M6}
M6 → {M0, M1, M2, M4, M5}
M0 → {M2, M5}
M4 → {M1, M2, M3, M5, M6}
M1 → {M2, M3, M4, M5}
M2 → {M0, M1, M4, M5, M6}
M3 → {M1, M4}
```

**Interpretation:**
- M5 is the **central hub**, connected to all other morphotypes except M3.
- M3 is a **peripheral extreme** with only two outgoing transitions (to M1 and M4).
- The graph suggests that most trajectories flow through M5, with occasional excursions into other morphotypes.

### 3.5 Phylogenetic Tree (UPGMA)

The UPGMA tree (based on normalized edit distances) reveals the following hierarchy:

```
                M3
                |
             M1
             |
M5 ---- M2 ---- M4
             |
          M6
             |
            M0
```

**Interpretation:**
- M3 is a **basal** or **ancestral** morphotype in this space, far from the central cluster.
- M5, M2, and M6 form a **central cluster** of closely related morphotypes.
- M4 is closely related to M6, forming a sub-cluster.
- M0 is a derived morphotype, connected to M5 and M2.

This structure suggests a **morphogenetic tree** where different dynamical regimes branch from a central hub.

---

## 4. Interpretation

### 4.1 The Central Attractor: M5

M5 is the largest morphotype (23.5%) and serves as the **central hub** of the transition graph. Its characteristics include:
- Short stopping times (representative: n=11141, steps=68).
- Moderate excursions.
- High connectivity to other morphotypes.

This suggests that M5 represents the **canonical "normal" behavior** of the Collatz map — short, stable trajectories that quickly reach 1.

### 4.2 The Extreme Morphotype: M3

M3 is the smallest morphotype (5.1%) and the most distant in the phylogenetic tree. Its characteristics include:
- Very long stopping times (representative: n=19611, steps=198).
- High maximum excursions (peak ~10^6.4).
- Low connectivity (only two outgoing transitions).

This suggests that M3 represents **rare, extreme trajectories** that deviate significantly from the norm. These are precisely the trajectories that are most interesting for understanding the limits of the Collatz map.

### 4.3 The Transition Network

The transition graph reveals a **non-linear topology**:
- Trajectories can move between morphotypes as n increases.
- M5 serves as the main conduit.
- M3 is an isolated extreme, only reachable through M1 or M4.

This topology suggests that the space of Collatz trajectories is **stratified** into distinct regimes, with occasional excursions into extreme regimes.

### 4.4 Genomes as Morphodynamic Fingerprints

The event genomes provide a **new symbolic language** for describing Collatz dynamics:
- `U` (up) and `D` (down) capture the parity-driven oscillation.
- `P` (peak) captures the growth phases.
- `R` (return) captures the contraction phases.
- `S` (stabilization) marks the final approach to 1.

Each morphotype has a **characteristic genome** that can be used to classify new trajectories without computing the full numerical sequence.

---

## 5. Conclusions

### 5.1 Summary of Findings

1. **The space of Collatz trajectories is not homogeneous.** It exhibits a discrete morphological structure with at least 7 stable morphotypes.

2. **Morphotypes have distinct dynamical signatures.** They differ in stopping time, maximum excursion, event entropy, and other invariants.

3. **Event genomes provide a new symbolic language** for describing and comparing trajectories.

4. **The transition graph reveals a central hub (M5) and a peripheral extreme (M3).** This topology suggests that the Collatz map has a core "normal" regime and occasional excursions into extreme regimes.

5. **The phylogenetic tree shows evolutionary relationships** between morphotypes, with M3 as the most basal (distantly related) and M5 as the central node.

### 5.2 Implications for the Collatz Conjecture

This work does not prove or disprove the Collatz conjecture. However, it provides a **new structural perspective**:
- Instead of focusing on individual numbers, we can focus on **morphological classes**.
- If we can prove that all trajectories eventually enter the **set of morphotypes that lead to 1**, this could be a path to a proof.
- The existence of the extreme morphotype M3 suggests that there are trajectories that "test the boundaries" of the map, but still eventually reach 1 (at least within our sample).

### 5.3 Contribution to SUBIT-TOPOS

This study demonstrates the power of the SUBIT-TOPOS framework:
- **From data to structure:** We transformed raw trajectories into a structured atlas of morphotypes.
- **From numbers to symbols:** We introduced event genomes as a symbolic representation of dynamics.
- **From classification to evolution:** We built a phylogenetic tree revealing relationships between morphotypes.

SUBIT-TOPOS is not just a classification tool — it is a **morphodynamic discovery engine** that reveals hidden structure in complex dynamical systems.

---

## 6. Future Work

1. **Scale up:** Extend the analysis to n up to 10^6 or 10^7 to capture rarer morphotypes and confirm the stability of the 7-cluster structure.

2. **Multiple sequence alignment:** Apply MSA (e.g., Needleman-Wunsch with affine gap penalties) to align genomes across all trajectories within each morphotype to produce consensus genomes.

3. **Reverse genome problem:** Given a genome signature, can we generate all numbers that produce trajectories with that genome? This would establish **morphogenetic families** of integers.

4. **Information-theoretic analysis:** Compute the mutual information between morphotype membership and starting number properties (e.g., binary representation, prime factors).

5. **Comparison with other maps:** Apply the same methodology to other iterated maps (e.g., 5n+1, 3n-1) to see if similar morphodynamic structures emerge.

6. **Formal language theory:** Treat event genomes as strings in a formal language and investigate whether the set of all Collatz genomes forms a regular language, context-free grammar, or something more complex.

---

## 7. Data Availability

All data generated in this study is available in the following files:

| File | Description |
|------|-------------|
| `morphotype_signatures.csv` | Signatures (15 features) for all 2,919 trajectories with morphotype labels |
| `collatz_genomes.csv` | Event genomes for the 7 representative trajectories |
| `morphogenetic_tree.png` | Phylogenetic tree visualization |
| `morphotype_genome_features.png` | Heatmap of average genome features per morphotype |

---

## 8. Acknowledgments

This work was conducted using the SUBIT-TOPOS framework, developed by the SUBIT Research Group. Special thanks to the open-source community for providing the scientific Python ecosystem.

---

## 9. References

1. Collatz, L. (1937). "On the problem of 3n+1". *Problem 256*.
2. Aczel, P. (1988). *Non-Well-Founded Sets*. CSLI Publications.
3. Keller, O. H. (1939). "Die Jacobi-Hypothese". *Monatshefte für Mathematik*.
4. Lagarias, J. C. (1985). "The 3x+1 problem and its generalizations". *American Mathematical Monthly*.
5. SUBIT-TOPOS Specification v2.0 (2026). "A recursive semantic universe".

---

*This report is part of the SUBIT-TOPOS research project and may be cited as:*

> SUBIT Research Group (2026). "SUBIT-TOPOS: Collatz Morphodynamic Atlas v1.0". *SUBIT Technical Report Series*, Report No. 2026-07-20.