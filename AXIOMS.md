# SUBIT — Axiomatic System

**Reference companion to SPECIFICATION.md**

---

## 1. Base Structure Axioms

### A1. Recursion
```
S_∞ = νX.(X × X × X)
```
The state space is the greatest coalgebraic fixed point of the triple product functor. Every state is a triple (w, x, y) where each component is itself a state, down to primitive leaves A = {a₁, …, aₖ}.

### A2. Internal Rule
Every extended state contains its active rule:
```
ŝ = (s, ρ) ∈ S_∞ × ℛ
```
The rule is not external to the state; it is part of the state's internal structure.

### A3. Evolution
```
F(s, ρ) = ( f_ρ(s), g(ρ, s) )
```
where f_ρ: S_∞ → S_∞ applies rule ρ to state s, and g: ℛ × S_∞ → ℛ evolves the rule itself.

### A4. Totality
F is a total function: defined for all (s, ρ) ∈ S_∞ × ℛ.

---

## 2. Categorical Structure Axioms

### A5. Category SUBIT
Objects are systems X = (S_X, ℛ_X, F_X, g_X). Morphisms φ = (φ_S, φ_ℛ) satisfy dynamic compatibility:
```
φ_S ∘ π_S ∘ F_X = π_S ∘ F_Y ∘ (φ_S × φ_ℛ)
```

### A6. Identity
For every object X, there exists id_X = (id_{S_X}, id_{ℛ_X}).

### A7. Associativity
Composition of morphisms is associative: (χ ∘ ψ) ∘ φ = χ ∘ (ψ ∘ φ).

### A8. Terminal Object
There exists 1 ∈ SUBIT with S_1 = {*}, ℛ_1 = {id}, and for every X exactly one morphism X → 1.

### A9. Finite Products
For any X, Y ∈ SUBIT, their product X × Y exists with componentwise structure.

### A10. Exponentials
For any X, Y ∈ SUBIT, the exponential Y^X exists, making SUBIT a cartesian closed category (CCC).

---

## 3. Dynamic Classifier Axioms

### A11. Ω-Set
```
Ω = {stable, metastable, cyclic, chaotic}
```

### A12. Stable
```
P is stable ⟺ F(P) ⊆ P and F⁻¹(P) ⊆ P
```
Full invariance: forward and backward.

### A13. Metastable
```
P is metastable ⟺ F(P) ⊆ P and F⁻¹(P) ⊄ P
```
Forward invariant only.

### A14. Cyclic
```
P is cyclic ⟺ ∃k > 0: Fᵏ(P) = P
```
Orbital stability, neither stable nor metastable.

### A15. Chaotic
```
P is chaotic ⟺ ∄k: Fᵏ(P) ⊆ P
```
No stability reachable.

### A16. Ω-Order
```
chaotic < cyclic < metastable < stable
```
Partial order by increasing stability.

---

## 4. Truth Axioms

### A17. Dynamic Truth
```
P is true ⟺ F(P) ⊆ P
```
Truth is stability under evolution. Not static correspondence.

### A18. Ω-Heyting Algebra
Ω with operations ∧, ∨, ¬ (as defined in SPECIFICATION.md §3.4) forms a Heyting algebra. The law of excluded middle fails for metastable propositions.

---

## 5. Metric Axioms

### A19. Semantic Metric
```
d_Ω(ŝ, t̂) = Σ_{n=0}^{∞} 2^{-n} · δ(Fⁿ(ŝ), Fⁿ(t̂))
```
where δ = 0 if same Ω-class, 1 otherwise.

### A20. Ultrametric
d_Ω is an ultrametric satisfying:
- d_Ω(ŝ, t̂) = 0 ⟺ ŝ = t̂ (bisimilarity)
- Symmetry
- Strong triangle inequality: d_Ω(ŝ, û) ≤ max(d_Ω(ŝ, t̂), d_Ω(t̂, û))

---

## 6. Universality Axioms

### A21. Universal Object
```
∃U ∈ SUBIT: ∀X ∈ SUBIT ∃φ: U → X
```
and U can simulate its own operator F from within (self-reference).

---

## 7. Type-Theoretic Axioms

### A22. Type as Stability Class
Every type A is an F-invariant class of trajectories:
```
A = { ŝ ∈ S_∞ × ℛ | stability_class(ŝ) = mode_A }
```

### A23. Type Evolution
```
Γ ⊢ t : A @ τ  and  F(A) ⊆ B @ τ
─────────────────────────────────
Γ ⊢ F(t) : B @ (τ+1)
```

### A24. Stable Type
```
Γ ⊢ t : A @ τ  and  F(A) ⊆ A
─────────────────────────────────
Γ ⊢ t : □A @ τ
```

### A25. Attractor Equality
```
s ~_F t ⟺ ∃k: Fᵏ(s) = Fᵏ(t)
```
Equality is attractor equivalence, not identity.

---

## 8. Modal Logic Axioms

| Axiom | Formula | Meaning |
|-------|---------|---------|
| M1 | □A → A | Stable implies actual |
| M2 | □A → □□A | Stability of stability |
| M3 | □(A → B) → (□A → □B) | Distributivity of □ |
| M4 | ◇A ↔ ¬□¬A | ◇ defined via □ |
| M5 | ◯A → ◇A | Cycle implies potential |
| M6 | □A → ◯A | Stable implies cyclic (trivially) |
| M7 | ◯◯A ↔ ◯A | Idempotence of cycle |
| M8 | □A ∧ □B → □(A ∧ B) | Stability of conjunction |

**Non-theorems (intuitionistic character):**
- ◇A ∨ ◇¬A — not every trajectory stabilizes
- □A ∨ □¬A — excluded middle fails

---

## 9. Correspondence Axioms (SUBIT-64)

### A26. Finite Embedding
SUBIT-64 embeds into S_∞ as depth-1 leaves:
```
S_64 = { (w, x, y) | w, x, y ∈ A } ⊂ S_∞
```
where |A| = 4, hence |S_64| = 64.

### A27. Hexagram Encoding
Each state s ∈ S_64 corresponds to a unique I-Ching hexagram via 6-bit encoding:
```
s = b₁b₂b₃ | b₄b₅b₆  =  Lower Trigram | Upper Trigram
```

---

## 10. Meta-Theoretic Properties

### Consistency
SUBIT-TOPOS is consistent because:
- S₀ is finite (|S₀| = 64)
- ℛ is finite (under finite system assumption)
- F is total on finite set
- All axioms are satisfiable in finite model

### Incompleteness
If ℛ is sufficiently rich (contains self-description rules), then by Gödel-type argument: there exist true propositions (in the sense F(P) ⊆ P) that are not provable in the system.

### Expressive Power Hierarchy
```
SUBIT-64 ⊂ SUBIT⁺ ⊂ SUBIT-TOPOS
```
- SUBIT-64: classification without dynamics
- SUBIT⁺: dynamics with internal rules
- SUBIT-TOPOS: full categorical structure with Ω, U, internal language

---

## Symbol Table

| Symbol | Definition |
|--------|------------|
| S_∞ | Recursive state space νX.(X × X × X) |
| ℛ | Rule space (functions S_∞ → S_∞) |
| ŝ | Extended state (s, ρ) |
| F | Full evolution operator |
| f_ρ | Local state evolution under rule ρ |
| g | Meta-evolution operator (rule change) |
| τ(ŝ) | Trajectory starting at ŝ |
| Fix(F) | Attractor set {ŝ | F(ŝ) = ŝ} |
| φ | Morphism in category SUBIT |
| id_X | Identity morphism of X |
| 1 | Terminal object |
| Y^X | Exponential (space of morphisms X → Y) |
| U | Universal object / internal interpreter |
| Ω | Dynamic classifier {stable, metastable, cyclic, chaotic} |
| χ_A | Characteristic function of subobject A ↪ X |
| □A | Stable (necessary) truth: F(A) ⊆ A |
| ◇A | Potential stabilization: ∃k: Fᵏ(s) ∈ A |
| ◯A | Cyclic return: ∃k: Fᵏ(A) = A |
| ~_F | Attractor equivalence: ∃k: Fᵏ(s) = Fᵏ(t) |
| Γ ⊢ t : A @ τ | Type judgment: t has type A at phase τ |
| 𝔸 | Base set {T, F, B, N} (Belnap bilattice) |
| S₀ | SUBIT-64 state space = 𝔸³, \|S₀\| = 64 |
| b₁…b₆ | Bit coordinates of state in {0,1}⁶ |
| WHO, WHERE, WHEN | Semantic coordinates of SUBIT |
| α, β, γ | Values of coordinates WHO, WHERE, WHEN |
| ρ | Active evolution rule (part of extended state ŝ) |

---

## Reference Map

| This file | SPECIFICATION.md |
|-----------|------------------|
| A1–A4 | §I, §II |
| A5–A10, A21 | §V |
| A11–A18 | §III, §VII.3 |
| A19–A20 | §IV |
| A22–A25 | §B.4 |
| M1–M8 | §B.4 |
| A26–A27 | §Appendix A, §B.2–B.3 |

---