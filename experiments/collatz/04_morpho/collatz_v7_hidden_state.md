# Collatz Morphological Automaton v7.0 — Hidden State / ε‑Machine Reconstruction — Results and Interpretation

**Experiment Date:** 2026-07-22  
**Data:** 3,000 morphotype sequences (M0–M6)  
**Method:** Predictive state (ε‑machine) reconstruction using suffix histories of length up to 5

---

## 1. Summary of Results

| Metric | Value |
|--------|-------|
| Number of causal states | **441** |
| Conditional entropy H(next | state) | **1.696 bits** |
| Original order‑1 H_cond | **1.091 bits** |
| “Reduction” (increase) | **+0.605 bits** |

---

## 2. What This Means

### 2.1. The Number of Causal States (441)

From the set of all possible histories (morphotype sequences of length up to 5), the ε‑machine algorithm merged those that had **identical future distributions** into **441 distinct causal states**.

- Possible histories of length 5: \(7^5 = 16,807\).
- Observed distinct histories: 486 (from the output).
- After merging, 441 causal states.

**Interpretation:** The dynamics is **not purely deterministic** — many histories with different pasts still lead to the same future behaviour, but there is still a large number of distinct predictive states. The number 441 is much smaller than 16,807, indicating significant structure, but still far larger than the 7 morphotypes or the 22 pair states from v4.0.

### 2.2. Conditional Entropy – The Surprising Increase

The ε‑machine predicts the next morphotype given the causal state. The conditional entropy **increased** from 1.091 bits (order‑1) to **1.696 bits**.

This is counterintuitive: adding more information (the entire history) should reduce uncertainty. Why did it increase?

**Possible explanations:**

1. **Sparsity and finite‑sample bias:**  
   The ε‑machine states are defined by the empirical distribution of futures. With only 3,000 training sequences, many states have very few observations. The entropy estimate may be inflated because the model is over‑fitting to noise – it assigns probability mass to many possible next morphotypes, even if the true underlying distribution is more peaked. The order‑1 model has 7 states, each with many samples, so its entropy estimate is more reliable.

2. **The predictive states are not yet minimal:**  
   The construction used histories of length ≤5. If the true causal state requires longer memory, the model is incomplete. The high entropy suggests that the future is still uncertain even after conditioning on 5 steps of history – meaning the process has **longer‑range structure** than 5 steps.

3. **The dynamics is intrinsically stochastic:**  
   Even with perfect knowledge of the past, the next morphotype may not be fully determined. The remaining entropy (~1.7 bits) might be irreducible – it reflects the inherent randomness of the Collatz map at the morphological level.

**Key conclusion:** The ε‑machine reconstruction did **not** find a simpler, lower‑entropy representation of the dynamics than the first‑order model. This suggests that **the morphological dynamics is not well‑approximated by a finite‑state Markov chain of any low order** – or that our method of state construction is insufficient.

---

## 3. Comparison with Previous Versions

| Version | Method | States | H_cond (bits) |
|---------|--------|--------|---------------|
| v3.3 | 7 morphotypes (order 1) | 7 | 1.091 |
| v4.0 | Pair states (order 2) | 22 | 0.926 |
| v6.2 | Triples (order 3) | 53 | 0.936 |
| v7.0 | ε‑machine (histories ≤5) | 441 | **1.696** |

The entropy **increased** for the ε‑machine, meaning the predictive power actually **decreased** relative to simpler models. This strongly suggests that:

- The ε‑machine construction overfitted the data.
- The true causal states are not captured by simple suffix merging.
- A different representation – perhaps using **arithmetic features** (residues, popcount) in addition to morphotypes – is needed to reduce uncertainty.

---

## 4. What This Tells Us About Collatz

The morphological dynamics of Collatz is **not** a simple finite‑state Markov process, even when using histories of length 5. The remaining uncertainty is high, and the number of causal states is large.

This aligns with the idea that the Collatz map has **complex, long‑range correlations** that cannot be captured by a small number of discrete states based only on past morphotypes. The system’s “memory” is not just in the sequence of morphological labels – it is encoded in the **arithmetic structure** of the numbers themselves.

**Implication:** To make progress, we need to combine morphological information with arithmetic features (residues, parity patterns, binary structure) into a joint state space. The ε‑machine on morphotypes alone is insufficient.

---

## 5. Next Steps (v7.1)

1. **Re‑run the ε‑machine with longer histories** (up to 10) to see if the number of states and entropy converge. If the entropy continues to grow, it suggests the process has infinite memory – i.e., the morphological projection is not a finite‑state process.

2. **Incorporate arithmetic features into the state definition.** For example, define a state as a pair: `(current morphotype, n mod 2^k)`. Then build a Markov model and check the entropy. If this reduces H_cond significantly, we have found the right coordinates.

3. **Apply the ε‑machine algorithm to the augmented state space** (with arithmetic features). This may yield a much smaller number of causal states and a lower conditional entropy.

4. **Perform cross‑validation** – split data into training and test sets to compute log‑likelihood and avoid overfitting. The current entropy estimates may be biased due to data sparsity.

---

## 6. Corrected Interpretation of v7.0 Results

The ε‑machine experiment **did not** produce a better predictive model than the simple first‑order Markov chain. The conditional entropy increased, indicating that the causal states derived from morphotype histories are not a good representation of the underlying dynamics.

This is a **negative but valuable result**: it tells us that **morphotypes alone are insufficient** to capture the state of the system. The memory effect observed in v6.2 (order 3) was real, but it does not lead to a compact, predictive model when taken to its logical extreme.

**The next step is to combine morphology with arithmetic – to build a joint state space that includes both the current morphological regime and the arithmetic “coordinates” (residues, parity) of the number.**

---

## 7. Conclusion

The Collatz morphological automaton is not a simple finite‑state Markov chain. The ε‑machine reconstruction revealed that histories of length up to 5 still leave ~1.7 bits of uncertainty, and the resulting 441 causal states are too numerous and not predictive.

This reinforces the idea that the true “state” of the system is a combination of the current morphological regime and the arithmetic properties of the number. Future work should focus on building such a joint representation.

---

*This analysis is part of the SUBIT-TOPOS research program and may be cited as:*

> SUBIT Research Group (2026). "Collatz Morphological Automaton v7.0: Hidden State Reconstruction." SUBIT Technical Report.