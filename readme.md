# SUBIT Universe

**A recursive semantic universe where the rule belongs to the state.**

```
SUBIT_∞ = ( S_∞, ℛ, F, g, Ω, d_Ω, U )

S_∞ = νX.(X × X × X)              — state = (WHO, WHERE, WHEN), recursive
F(s,ρ) = (f_ρ(s), g(ρ,s))         — evolution of state AND rule
Ω = {stable, metastable, cyclic, chaotic}  — dynamic truth: P is true ⟺ F(P) ⊆ P
d_Ω — ultrametric on trajectories
U — universal interpreter (internal simulation)
```

**Core thesis:** Truth is not static — it is defined as stability under evolution.

## Documents

| File | Contents |
|------|----------|
| [`SPECIFICATION.md`](SPECIFICATION.md) | Full formal specification: base definitions, dynamics, Ω-stability, metric, category, topos, type theory, universal object |
| [`AXIOMS.md`](AXIOMS.md) | Axiomatic system, definitions, theorems, symbol table |
| [`IMPLEMENTATION.md`](IMPLEMENTATION.md) | Algorithms for Ω-class computation, semantic distance, pseudocode, open problems |

## License

MIT