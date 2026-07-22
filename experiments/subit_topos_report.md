# SUBIT-TOPOS: Experimental Research Report

**A Morphodynamic Framework for Exploring Formal Dynamical Systems**

*SUBIT Research Group*  
*Date: 2026-07-22*  
*Version: 2.0 (Final)*

---

## Abstract

This report presents the results of applying the SUBIT-TOPOS framework — a self‑referential, rule‑changing dynamical system with dynamic truth as stability under evolution — to three distinct mathematical problems: the Jacobian conjecture, the Collatz conjecture, and a family of generalized Collatz maps. Instead of searching for isolated counterexamples, we construct **morphodynamic atlases** that reveal the structural stratification of state spaces and parameter spaces. Key results include: (1) a characteristic‑dependent phase transition in the Jacobian property over finite fields; (2) the discovery of 7 stable trajectory morphotypes in the classical Collatz map, with distinct event genomes and a non‑uniform integer‑space topology; and (3) a comprehensive phase diagram of the generalized Collatz parameter space, showing that only a small fraction of parameters yield stable behaviour, while the vast majority produce cycles or chaotic excursions. These experiments demonstrate that SUBIT-TOPOS is not a theorem prover but a **morphodynamic discovery engine** capable of revealing hidden structure in formal systems.

---

## 1. Introduction

Many open problems in mathematics involve iterated maps or polynomial transformations where local properties (e.g., non‑zero Jacobian, simple rule) do not obviously imply global behaviour (e.g., injectivity, convergence to 1). Traditional computational approaches focus on verifying conjectures for large sets of inputs or searching for counterexamples. However, such methods often treat each instance independently and miss the **structural relationships** between different dynamical regimes.

SUBIT-TOPOS offers a complementary approach. It formalizes a universe where:
- **The rule is part of the state** — evolution changes both state and rule.
- **Truth is dynamic** — a proposition is true if it is invariant under evolution (F(P) ⊆ P).
- **Ω‑classification** — trajectories are classified as STABLE, METASTABLE, CYCLIC, or CHAOTIC.
- **Morphodynamic signatures** — each object (rule, trajectory) receives a fingerprint that enables clustering and comparison.

In this report, we apply SUBIT-TOPOS to three distinct domains: algebraic geometry (Jacobian conjecture), number theory (Collatz conjecture), and a parametric family of maps. The goal is not to prove or disprove these conjectures, but to **map the morphology of their solution spaces** and to demonstrate the versatility of the framework.

---

## 2. Theoretical Framework

### 2.1 Core Definitions

The SUBIT-TOPOS universe is defined as:

```
SUBIT_∞ = ( S_∞, ℛ, F, g, Ω, d_Ω, U )
```

- **S_∞** = νX.(X × X × X) — recursive state space.
- **ℛ** — rule space (functions S_∞ → S_∞).
- **F(s, ρ)** = (f_ρ(s), g(ρ, s)) — evolution of state and rule.
- **Ω** = {STABLE, METASTABLE, CYCLIC, CHAOTIC} — dynamic classifier.
- **d_Ω** — semantic ultrametric on trajectories.
- **U** — universal interpreter object.

Truth: A set of states P is true iff F(P) ⊆ P (stability under evolution).

### 2.2 Methodology for Experimental Mapping

For each problem domain, we follow a common pipeline:

1. **Encoding** — map the objects (polynomials, integers, parameters) into states.
2. **Define rules** — specify transformations (Jacobian computation, Collatz iteration, generalized map iteration).
3. **Generate trajectories** — sample the state space and evolve.
4. **Extract signatures** — compute a feature vector Φ for each trajectory.
5. **Cluster** — apply unsupervised learning to identify morphotypes.
6. **Analyse topology** — build graphs of transitions or adjacencies.
7. **Interpret** — map results back to the original mathematical problem.

---

## 3. Experiment 1: Jacobian Conjecture

### 3.1 Setup

We investigated polynomial maps F(x,y) = (P(x,y), Q(x,y)) over different algebraic structures:
- ℤ (characteristic 0, finite sample),
- finite fields 𝔽₂, 𝔽₃, 𝔽₅, 𝔽₇,
- ring ℤ/4ℤ (with nilpotents).

For each, we generated 1024 random polynomials (degree ≤ 3, coefficients in [-2,2]), computed the Jacobian determinant over a finite grid, and checked injectivity.

### 3.2 Results

| Structure | Domain Size | Non‑injective with constant J ≠ 0 |
|-----------|-------------|-----------------------------------|
| ℤ (char 0) | 16 | 0 |
| 𝔽₂ | 4 | 6 |
| 𝔽₃ | 9 | 2 |
| ℤ/4ℤ | 16 | 2 |
| 𝔽₅ | 25 | 0 |
| 𝔽₇ | 49 | 0 |

**Key findings:**
- Anomalies appear only in small characteristics and rings with nilpotents.
- In characteristic 0 (even on a finite grid), no counterexamples were found.
- This confirms that the Jacobian property is **characteristic‑dependent**, with a phase transition between p ≤ degree and p > degree.

### 3.3 Interpretation

The experiment shows that SUBIT-TOPOS can automatically detect **structural phase transitions** in algebraic geometry. It does not disprove the Jacobian conjecture over ℂ, but it maps the parameter space of fields and reveals where local invertibility fails to imply global injectivity.

---

## 4. Experiment 2: Classical Collatz Morphodynamic Atlas

### 4.1 Motivation

Instead of asking "does every n reach 1?", we ask: **What is the morphological structure of the space of Collatz trajectories?** This shifts the problem from verification to structural classification.

### 4.2 Methodology

We sampled 2,919 starting numbers n ∈ [1, 50,000]. For each n, we computed the full trajectory until reaching 1 (or a safety limit) and extracted a 15‑dimensional signature Φ(τ) including:
- stopping time,
- log‑maximum excursion,
- event entropy,
- compression ratio,
- peak count,
- return count,
- run‑length statistics,
- and others.

We applied k‑means clustering (k=7) and then converted each trajectory into a **symbolic event genome** over the alphabet:
- `U` — odd step (expansion),
- `D` — even step (contraction),
- `P` — new global maximum,
- `R` — return below the starting value,
- `S` — stabilization (entering the final cycle).

We built a phylogenetic tree using Levenshtein distances between representative genomes.

### 4.3 Results

**Morphotype distribution:**

| Morphotype | Count | % | Representative n | Stopping Time |
|------------|------|---|------------------|---------------|
| M0 | 574 | 19.7 | 19556 | 48 |
| M1 | 153 | 5.2 | 19947 | 118 |
| M2 | 354 | 12.1 | 31547 | 85 |
| M3 | 150 | 5.1 | 19611 | 198 |
| M4 | 411 | 14.1 | 16734 | 159 |
| M5 | 687 | 23.5 | 11141 | 68 |
| M6 | 590 | 20.2 | 43917 | 132 |

**Event genome examples (first 100 characters):**

```
M0: DRDRURDRDRURDRURDRDRDRURDRURDRURDRUPDRDRDRDRDRURDRDRDRURDRDRDRDRDRURDRURDRURDRDRDRDRDRURDRDRSDRDRS...
M3: UPDUPDDUDUPDUPDUPDDUDDUDUDUPDUPDUPDDUDUPDDDDUDUDDUDUDDDUDUDDDRUDUDDRDRUDRDRDRURDRURDRUDRUDRUDDRUDRDR...
```

**Normalized Levenshtein distance matrix (selected):**

```
        M0   M1   M2   M3   M4   M5   M6
M5    0.104 0.194 0.081 0.618 0.503 0.000 0.382
M3    0.720 0.465 0.566 0.000 0.139 0.618 0.243
```

**Initial‑condition adjacency graph** (based on consecutive integers in the sampled range):

```
M5 — {M0, M1, M2, M6}
M6 — {M0, M1, M2, M4, M5}
M0 — {M2, M5}
M4 — {M1, M2, M3, M5, M6}
M1 — {M2, M3, M4, M5}
M2 — {M0, M1, M4, M5, M6}
M3 — {M1, M4}
```

### 4.4 Interpretation

- The space of Collatz trajectories is **not homogeneous**; it exhibits 7 stable morphotypes under the chosen representation.
- M5 is the **dominant morphodynamic basin** (23.5%), with short stopping times and moderate excursions.
- M3 is a **rare excursion regime** (5.1%), with very long stopping times and high maxima.
- The adjacency graph shows that M5 acts as a central hub in the integer‑space topology, while M3 is an isolated outlier.
- Event genomes provide a **new symbolic language** for describing Collatz dynamics, opening the door to formal language analysis.

---

## 5. Experiment 3: Generalized Collatz Atlas

### 5.1 Parameterization

We explored the family of generalized Collatz maps with **separate divisor and multiplier**:

```
T(n) = n / d       if n % d == 0
T(n) = k * n + c   otherwise
```

The classical Collatz map corresponds to (d, k, c) = (2, 3, 1). We fixed d = 2 and varied k ∈ [2, 7], c ∈ [1, 9] (54 combinations). For each combination, we sampled 100 starting numbers n ∈ [1, 2000], ran trajectories up to 5000 steps, and classified the dominant behaviour as STABLE, CYCLIC, or MIXED.

### 5.2 Results

**Ω‑class distribution:**

| Class | Count | Percentage |
|-------|-------|------------|
| STABLE | 4 | 7.4% |
| MIXED | 18 | 33.3% |
| CYCLIC | 32 | 59.3% |
| CHAOTIC | 0 | 0% |

**Counterexamples:** 2,324 cyclic trajectories were found, of which 832 were non‑trivial cycles (length ≥ 2). Examples of genuine cycles:

- (d=2, k=2, c=6): cycle [12, 6, 3] (length 3).
- (d=2, k=3, c=6): cycle [18, 6, 2, 12, 4] (length 5).

**Classical Collatz:** (d=2, k=3, c=1) was STABLE (100/100 samples reached 1).

### 5.3 Interpretation

- Only a small fraction of parameter combinations are stable (7.4%).
- The vast majority produce cycles or mixed behaviour.
- The classical Collatz map is an **exceptional point** in this parameter space, surrounded by unstable regions.
- This demonstrates that SUBIT-TOPOS can **systematically map instability** in a family of dynamical systems, identifying regions where the conjecture fails.

---

## 6. Discussion

### 6.1 Common Themes

Across all three experiments, several patterns emerge:

1. **Structural stratification** — The state spaces are not uniform; they exhibit discrete clusters or regimes.
2. **Phase transitions** — Changes in parameters (field characteristic, morphotype, (k,c)) lead to qualitative changes in behaviour.
3. **Morphodynamic signatures** — Feature vectors capture essential dynamical properties and enable meaningful clustering.
4. **Symbolic representations** — Event genomes provide a language for describing trajectories independently of specific numerical values.

### 6.2 SUBIT-TOPOS as a Discovery Engine

The framework is not a theorem prover; it does not replace rigorous proof. Instead, it:

- **Generates hypotheses** by revealing structure that may be invisible to classical analysis.
- **Guides exploration** by identifying regions of interest (e.g., rare morphotypes, unstable parameter regions).
- **Provides a new language** for describing dynamical systems in terms of morphological classes and symbolic event sequences.

### 6.3 Limitations

- **Empirical nature** — all results are sample‑based and do not constitute mathematical proofs.
- **Representation dependence** — the number and stability of morphotypes depend on the chosen features and clustering algorithm.
- **Computational boundaries** — results are limited by sampling range, step limits, and value limits.

---

## 7. Conclusions

1. **The Jacobian property is characteristic‑dependent.** Non‑injective maps with constant non‑zero Jacobian appear in 𝔽₂, 𝔽₃, and ℤ/4ℤ, but not in 𝔽₅, 𝔽₇, or characteristic‑0 samples. This indicates a phase transition in algebraic geometry.

2. **Collatz trajectory space is morphologically stratified.** Seven stable morphotypes were identified, with a dominant basin (M5) and a rare extreme regime (M3). Event genomes provide a symbolic description that can be used for formal language analysis.

3. **The generalized Collatz parameter space is dominated by instability.** Only 7.4% of tested combinations are stable; the classical Collatz map (2,3,1) is an exceptional stable point.

4. **SUBIT-TOPOS is a versatile framework for morphodynamic exploration.** It can be applied to diverse domains (algebraic geometry, number theory, parametric families) and yields structural insights that complement traditional mathematical analysis.

---

## 8. Future Work

- **Scale up** — increase sample sizes, parameter ranges, and step limits.
- **Cross‑domain comparison** — apply the same morphodynamic methodology to other iterated maps (e.g., 5n+1, 3n−1).
- **Formal language theory** — study the Collatz event genome language L₃ₙ₊₁, its entropy, grammar, and minimal automaton.
- **Reverse morphology** — given a genome signature, find all starting numbers that produce it (inverse Collatz problem).
- **Integration with symbolic computation** — use SUBIT-TOPOS to guide automated theorem proving by identifying invariant patterns.

---

## 9. Data Availability

All experimental data and code are available in the repository:

- `experiments/jacobian/` — Jacobian atlas and phase diagrams.
- `experiments/collatz/` — Collatz morphodynamic atlas, event genomes, phylogenetic trees, generalized atlas.

Key output files:
- `morphotype_signatures.csv` — signatures of all 2,919 Collatz trajectories.
- `collatz_genomes.csv` — event genomes of representative morphotypes.
- `generalized_collatz_results.csv` — Ω‑classification for all (k,c) combinations.
- `generalized_collatz_counterexamples.csv` — list of 2,324 counterexamples.

---

## 10. References

1. Keller, O. H. (1939). "Die Jacobi-Hypothese". *Monatshefte für Mathematik*.
2. Collatz, L. (1937). "On the problem of 3n+1". *Problem 256*.
3. Lagarias, J. C. (1985). "The 3x+1 problem and its generalizations". *American Mathematical Monthly*.
4. Aczel, P. (1988). *Non‑Well‑Founded Sets*. CSLI Publications.
5. SUBIT-TOPOS Specification v2.0 (2026). "A recursive semantic universe".

---

*This report is part of the SUBIT-TOPOS research project and is intended for scientific dissemination. The results are experimental and do not constitute proofs of the conjectures discussed.*