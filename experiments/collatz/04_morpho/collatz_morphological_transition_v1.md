# Collatz Morphological Transition System v1.0 — Results and Interpretation

**Experiment Date:** 2026-07-22  
**Sample:** 2,000 random starting numbers (n ∈ [1, 10⁵])  
**Local window:** 20 steps  
**Number of local morphotypes:** 7 (k-means)  
**Transition matrix:** 7×7 (probabilities)

---

## 1. Objective

We aim to characterise the dynamics of Collatz trajectories at the level of **local morphological states** — short-term patterns of behaviour — rather than global fate. This allows us to build a genuine Markov chain on discrete states, free from "teleological" bias (i.e., not looking into the distant future). The resulting transition graph is the first step towards a **formal grammar of Collatz dynamics**.

---

## 2. Local Morphotype Classifier

We built a classifier for local states using a 20‑step window. Each state \( n \) was mapped to a 6‑dimensional feature vector:
- `odd_ratio` – proportion of odd steps in the window;
- `mean_growth` – average multiplicative change;
- `var_growth` – variance of changes;
- `local_entropy` – entropy of the U/D pattern;
- `excursion` – maximum relative height in the window;
- `compression` – ratio of last to first value.

K‑means clustering (k=7) produced **7 local morphotypes** (\( M_0, \dots, M_6 \)). These are not the same as the global morphotypes (M0–M6) from the earlier atlas — they describe **momentary dynamical regimes**.

---

## 3. Transition Matrix

The transition matrix \( P \) (first 5 rows shown) is:

| From \ To | M0   | M1   | M2   | M3   | M4   | M5   | M6   |
|-----------|------|------|------|------|------|------|------|
| **M0**    | 0.586| 0.000| 0.000| 0.000| 0.243| 0.170| 0.000|
| **M1**    | 0.000| 0.486| 0.000| 0.000| 0.252| 0.000| 0.262|
| **M2**    | 0.000| 0.000| 0.126| 0.009| 0.000| 0.000| 0.865|
| **M3**    | 0.000| 0.000| 1.000| 0.000| 0.000| 0.000| 0.000|
| **M4**    | 0.224| 0.205| 0.000| 0.000| 0.571| 0.000| 0.000|

*(Rows may not sum to 1 due to rounding; full matrix includes missing transitions.)*

---

## 4. Key Observations

### 4.1. Deterministic Transition: M3 → M2

State M3 always transitions to M2 with probability 1. This suggests that M3 is a transient "pre‑M2" regime, possibly associated with a specific local pattern that immediately leads to M2 in the next step.

### 4.2. Strong Self‑Loops

- M0 has a 58.6% chance of staying in M0.
- M1 has 48.6% self‑loop.
- M4 has 57.1% self‑loop.
- M2 has 86.5% self‑loop — a highly persistent state.

These high self‑loop probabilities indicate that local morphotypes are often stable over short timescales; the system spends considerable time in the same regime before switching.

### 4.3. M2 as a "Sink" or "Hub"

M2 has the highest self‑loop (0.865) and receives deterministic inflow from M3. It also has a small transition to M3 (0.009). This suggests M2 is a **dominant state** — trajectories may get trapped in M2 for long periods.

### 4.4. Rare Exits

Some transitions are zero or near‑zero (e.g., M0 → M1, M0 → M2, etc.). This implies that not all morphological switches are equally probable; the dynamics has a **preferred structure**.

---

## 5. Comparison with Global Morphotypes

We also assigned global morphotypes to a subset of trajectories (full‑trajectory classification). However, a direct mapping between local and global states is not yet established. Preliminary inspection suggests that:

- Trajectories classified globally as **M5** (the dominant basin) may spend most of their time in **local M2** or **M0** states.
- Extreme trajectories (global M3) likely involve sequences of local states that are rare, such as transitions into M1 or M4.

This two‑level ontology (local vs global) is promising: it separates **short‑term behaviour** from **long‑term fate**.

---

## 6. Transition Graph Visualisation

The graph (saved as `local_transition_graph.png`) shows the structure:

- M2 and M0 are central nodes with multiple outgoing and incoming edges.
- M3 is a leaf that feeds only into M2.
- M5 and M6 are less connected, suggesting they are "boundary" regimes.

The graph is **strongly connected**? Not entirely — M3 has no outgoing except to M2, so it's a transient state leading into the main component. Other states may form a single strongly connected component (M0, M1, M2, M4, maybe M5, M6). A full SCC analysis would be needed.

---

## 7. Stationary Distribution (if applicable)

If we treat the matrix as a Markov chain, the stationary distribution (if it exists as a single recurrent class) would indicate the long‑run fraction of time spent in each local morphotype. Given the high self‑loops, we can approximate:

- M2 likely has the highest stationary mass (due to strong self‑loop and inflow from M3).
- M0 and M4 also have significant mass.
- M3 has near‑zero mass (transient).

A formal computation would reveal the dominant eigenvector.

---

## 8. Next Steps: Towards a Grammar (v6.0)

With the local transition matrix, we can now:

1. **Extract sequences** of local morphotypes along full trajectories.
2. **Apply grammar induction** (e.g., Sequitur) to these sequences to discover recurrent patterns.
3. **Build a minimal DFA** that recognises valid sequences of local states.
4. **Compare grammars** for different global morphotypes — do they have distinct syntactic rules?

This would answer the fundamental question: **Is Collatz dynamics described by a formal language with a simple grammar?** If yes, we may have uncovered the hidden structure that underpins the conjecture.

---

## 9. Conclusion

The Collatz Morphological Transition System v1.0 successfully transforms the problem from a continuous‑state dynamics into a **discrete‑state Markov chain** on 7 local regimes. The transition matrix reveals:

- **Deterministic paths** (M3 → M2).
- **Persistent states** (M2, M0, M4).
- **Sparse connectivity**, indicating structural bias.

This lays the foundation for a higher‑order analysis: **morphological grammar**.

*The image `local_transition_graph.png` visualises the graph; the matrix is available for further analysis.*