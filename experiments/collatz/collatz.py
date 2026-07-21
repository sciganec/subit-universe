"""
SUBIT-COLLATZ: Collatz Conjecture Explorer
Version 1.0 · 2026

A SUBIT-TOPOS instantiation for exploring the generalized Collatz space:
ρₐ,₀(n) = n/2 if n even, else a*n + b

Builds phase diagrams, detects cycles, and finds chaotic candidates.
"""

from typing import List, Tuple, Dict, Optional, Set
import random
import hashlib
import sys
from collections import defaultdict
from dataclasses import dataclass, field
import time

# ============================================================================
# 1. CORE: SUBIT-TOPOS for Collatz
# ============================================================================

State = int  # n (up to 2^max_bits - 1)
RuleID = int
ExtendedState = Tuple[State, RuleID]


class CollatzRule:
    """Generalized Collatz rule: ρ(n) = n/2 if even, else a*n + b."""

    def __init__(self, a: int = 3, b: int = 1, max_bits: int = 16, max_steps: int = 1000):
        self.a = a
        self.b = b
        self.max_bits = max_bits
        self.limit = (1 << max_bits) - 1
        self.max_steps = max_steps

        # Statistics (reset per trajectory)
        self.steps = 0
        self.max_reached = 0
        self.overflow = False
        self.cycle_detected = False
        self.cycle_start = -1
        self.cycle_length = 0

    def reset_stats(self):
        self.steps = 0
        self.max_reached = 0
        self.overflow = False
        self.cycle_detected = False
        self.cycle_start = -1
        self.cycle_length = 0

    def apply(self, n: State) -> State:
        """Apply one step of the Collatz map."""
        self.steps += 1
        if n > self.max_reached:
            self.max_reached = n

        if n == 1:
            return 1  # Stable attractor

        if n % 2 == 0:
            return n // 2
        else:
            val = self.a * n + self.b
            if val > self.limit:
                self.overflow = True
                return val % self.limit  # Wrap around for finite simulation
            return val

    def trajectory(self, n: State) -> Tuple[str, List[State]]:
        """
        Run trajectory until:
        - reaches 1 (STABLE)
        - detects a cycle (CYCLIC)
        - exceeds max_steps (CHAOTIC candidate)
        """
        self.reset_stats()
        seen: Dict[State, int] = {}
        traj: List[State] = []
        current = n
        step = 0

        while True:
            if current in seen:
                self.cycle_detected = True
                self.cycle_start = seen[current]
                self.cycle_length = step - seen[current]
                return "CYCLIC", traj

            traj.append(current)
            seen[current] = step

            if current == 1:
                return "STABLE", traj

            if step >= self.max_steps:
                return "CHAOTIC", traj

            current = self.apply(current)
            step += 1


# ============================================================================
# 2. SUBIT SYSTEM WRAPPER
# ============================================================================

class SUBITCollatzSystem:
    """SUBIT system for Collatz exploration."""

    def __init__(self, num_rules: int = 256, max_bits: int = 16, max_steps: int = 1000):
        self.num_rules = num_rules
        self.max_bits = max_bits
        self.max_steps = max_steps
        self.limit = (1 << max_bits) - 1

        # Generate rules: various (a,b) pairs
        self.rules: List[CollatzRule] = []
        param_pairs = self._generate_param_pairs(num_rules)
        for a, b in param_pairs:
            self.rules.append(CollatzRule(a, b, max_bits, max_steps))

    def _generate_param_pairs(self, n: int) -> List[Tuple[int, int]]:
        """Generate n distinct (a,b) pairs, focusing on interesting regions."""
        pairs = []
        # Always include the classic (3,1)
        pairs.append((3, 1))

        # Systematic grid: a in 1..7, b in 1..7
        for a in range(1, 8):
            for b in range(1, 8):
                if (a, b) not in pairs:
                    pairs.append((a, b))

        # Random extras to fill
        rng = random.Random(42)
        while len(pairs) < n:
            a = rng.randint(1, 10)
            b = rng.randint(1, 10)
            if (a, b) not in pairs:
                pairs.append((a, b))

        return pairs[:n]

    def f(self, rid: RuleID, s: State) -> State:
        """Apply active rule to state."""
        return self.rules[rid].apply(s)

    def g(self, rid: RuleID, s: State) -> RuleID:
        """Meta-evolution: switch to a different rule based on state."""
        key = (rid * 1000003 + s * 1000033) & 0xFFFFFFFF
        hash_val = hashlib.md5(str(key).encode()).hexdigest()
        return int(hash_val[:8], 16) % self.num_rules

    def step(self, es: ExtendedState) -> ExtendedState:
        """Full evolution F: (s, rho) -> (rho(s), g(rho, s))."""
        s, rid = es
        new_s = self.f(rid, s)
        new_rid = self.g(rid, new_s)
        return (new_s, new_rid)


# ============================================================================
# 3. Ω-CLASSIFIER
# ============================================================================

class OmegaClassifier:
    STABLE = "STABLE"
    METASTABLE = "METASTABLE"
    CYCLIC = "CYCLIC"
    CHAOTIC = "CHAOTIC"

    @staticmethod
    def classify_rule(rule: CollatzRule, s0: State) -> Tuple[str, List[State]]:
        """Classify a single trajectory using the rule directly."""
        return rule.trajectory(s0)

    @staticmethod
    def classify_system(system: SUBITCollatzSystem, s0: State, rid: RuleID,
                         max_steps: int = 500) -> Tuple[str, List[ExtendedState]]:
        """Classify trajectory in the full SUBIT system."""
        es = (s0 & system.limit, rid % system.num_rules)
        visited: Dict[ExtendedState, int] = {}
        trajectory: List[ExtendedState] = []
        step = 0

        while es not in visited:
            visited[es] = step
            trajectory.append(es)
            es = system.step(es)
            step += 1
            if step > max_steps:
                return OmegaClassifier.CHAOTIC, trajectory

        cycle_start = visited[es]
        cycle_len = step - cycle_start

        if cycle_start == 0 and cycle_len == 1:
            return OmegaClassifier.STABLE, trajectory
        elif cycle_start > 0 and cycle_len == 1:
            return OmegaClassifier.METASTABLE, trajectory
        elif cycle_len > 1:
            return OmegaClassifier.CYCLIC, trajectory
        return OmegaClassifier.CHAOTIC, trajectory


# ============================================================================
# 4. SIGNATURE COMPUTATION
# ============================================================================

@dataclass
class CollatzSignature:
    """Morphodynamic signature Φ(ρ) for a Collatz rule."""

    a: int
    b: int
    omega: str          # Ω-class
    stable_ratio: float # fraction of samples that reach 1
    avg_steps: float    # average steps to 1
    avg_max: float      # average maximum value reached
    overflow_ratio: float # fraction of samples that overflowed
    cycle_count: int    # number of distinct cycles found
    cycle_lengths: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'a': self.a,
            'b': self.b,
            'omega': self.omega,
            'stable_ratio': self.stable_ratio,
            'avg_steps': self.avg_steps,
            'avg_max': self.avg_max,
            'overflow_ratio': self.overflow_ratio,
            'cycle_count': self.cycle_count,
            'cycle_lengths': self.cycle_lengths,
        }


def compute_signature(rule: CollatzRule, num_samples: int = 200) -> CollatzSignature:
    """
    Compute signature Φ(ρ) by sampling random starting states.
    """
    stable_count = 0
    overflow_count = 0
    total_steps = 0
    total_max = 0
    cycles_found: List[int] = []
    cycle_lengths: List[int] = []

    for _ in range(num_samples):
        s0 = random.randint(2, rule.limit // 4)  # start above 1
        omega, traj = rule.trajectory(s0)

        if omega == "STABLE":
            stable_count += 1
            total_steps += rule.steps
            total_max += rule.max_reached

        elif omega == "CYCLIC":
            cycles_found.append(rule.cycle_start)
            cycle_lengths.append(rule.cycle_length)
            total_steps += rule.steps
            total_max += rule.max_reached

        elif omega == "CHAOTIC":
            overflow_count += 1
            total_steps += rule.steps
            total_max += rule.max_reached

    # Determine dominant Ω-class
    total = num_samples
    if stable_count / total > 0.8:
        omega_dom = OmegaClassifier.STABLE
    elif overflow_count / total > 0.3:
        omega_dom = OmegaClassifier.CHAOTIC
    elif len(cycles_found) > 0:
        omega_dom = OmegaClassifier.CYCLIC
    else:
        omega_dom = OmegaClassifier.METASTABLE

    return CollatzSignature(
        a=rule.a,
        b=rule.b,
        omega=omega_dom,
        stable_ratio=stable_count / total,
        avg_steps=total_steps / total if total > 0 else 0,
        avg_max=total_max / total if total > 0 else 0,
        overflow_ratio=overflow_count / total,
        cycle_count=len(cycles_found),
        cycle_lengths=cycle_lengths,
    )


# ============================================================================
# 5. ATLAS BUILDER
# ============================================================================

def build_collatz_atlas(param_grid: List[Tuple[int, int]],
                         num_samples: int = 100,
                         max_bits: int = 16,
                         max_steps: int = 1000) -> List[CollatzSignature]:
    """
    Build atlas for a grid of (a,b) parameters.
    """
    signatures = []
    total = len(param_grid)

    for idx, (a, b) in enumerate(param_grid):
        print(f"  [{idx+1}/{total}] Computing signature for (a={a}, b={b})...")
        rule = CollatzRule(a, b, max_bits, max_steps)
        sig = compute_signature(rule, num_samples)
        signatures.append(sig)

    return signatures


def print_atlas_table(signatures: List[CollatzSignature]):
    """Print a human-readable atlas table."""
    print("\n" + "=" * 80)
    print("SUBIT-COLLATZ ATLAS")
    print("=" * 80)
    print(f"{'a':<4} {'b':<4} {'Ω':<12} {'Stable%':<10} {'Overflow%':<12} {'Cycles':<8} {'Avg Steps':<12}")
    print("-" * 80)

    # Sort by a then b
    for sig in sorted(signatures, key=lambda x: (x.a, x.b)):
        print(f"{sig.a:<4} {sig.b:<4} {sig.omega:<12} "
              f"{sig.stable_ratio*100:<10.1f} "
              f"{sig.overflow_ratio*100:<12.1f} "
              f"{sig.cycle_count:<8} "
              f"{sig.avg_steps:<12.1f}")

    print("=" * 80)


def print_heatmap(signatures: List[CollatzSignature]):
    """
    Print a simple ASCII heatmap of Ω-classes.
    """
    # Build a map: (a,b) -> omega
    omega_map = {}
    for sig in signatures:
        omega_map[(sig.a, sig.b)] = sig.omega

    # Determine range
    a_values = sorted(set(sig.a for sig in signatures))
    b_values = sorted(set(sig.b for sig in signatures))

    # Color mapping
    color = {
        OmegaClassifier.STABLE: "🟢",
        OmegaClassifier.METASTABLE: "🟡",
        OmegaClassifier.CYCLIC: "🔴",
        OmegaClassifier.CHAOTIC: "⚫",
    }

    print("\n" + "-" * 80)
    print("SUBIT-COLLATZ PHASE DIAGRAM")
    print("-" * 80)
    print("Legend: 🟢=STABLE  🟡=METASTABLE  🔴=CYCLIC  ⚫=CHAOTIC")
    print("-" * 80)

    # Header: a values
    print("a\\b", end="")
    for a in a_values:
        print(f"  {a:2d} ", end="")
    print()

    for b in b_values:
        print(f"{b:2d}  ", end="")
        for a in a_values:
            omega = omega_map.get((a, b), "?")
            print(f" {color.get(omega, '?')} ", end="")
        print()

    print("-" * 80)


# ============================================================================
# 6. DEEP SEARCH FOR CHAOTIC CANDIDATES
# ============================================================================

def deep_search(system: SUBITCollatzSystem,
                 candidate_rules: List[int],
                 num_starts: int = 1000,
                 max_steps: int = 10000) -> Dict[int, List[State]]:
    """
    Deep search for chaotic numbers using specific rules.
    """
    results: Dict[int, List[State]] = {}

    for rid in candidate_rules:
        rule = system.rules[rid]
        chaotic_candidates = []

        for _ in range(num_starts):
            s0 = random.randint(2, system.limit // 2)
            omega, traj = rule.trajectory(s0)

            if omega == "CHAOTIC":
                chaotic_candidates.append(s0)

                # If we have enough, we can stop early
                if len(chaotic_candidates) >= 10:
                    break

        results[rid] = chaotic_candidates
        print(f"Rule {rid} (a={rule.a}, b={rule.b}): found {len(chaotic_candidates)} candidates")

    return results


# ============================================================================
# 7. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("SUBIT-COLLATZ: Generalized Collatz Explorer")
    print("Using SUBIT-TOPOS Core v0.1")
    print("=" * 80)

    # Configuration
    MAX_BITS = 16
    MAX_STEPS = 1000
    NUM_SAMPLES = 50
    NUM_RULES = 256

    # Phase 1: Build the atlas for (a,b) grid
    print(f"\n[Phase 1] Building atlas (max_bits={MAX_BITS}, samples={NUM_SAMPLES})")

    # Define parameter grid: a in 1..7, b in 1..7
    param_grid = []
    for a in range(1, 8):
        for b in range(1, 8):
            param_grid.append((a, b))

    start_time = time.time()
    signatures = build_collatz_atlas(param_grid, num_samples=NUM_SAMPLES,
                                      max_bits=MAX_BITS, max_steps=MAX_STEPS)
    elapsed = time.time() - start_time
    print(f"Atlas built in {elapsed:.1f} seconds")

    # Print results
    print_atlas_table(signatures)
    print_heatmap(signatures)

    # Phase 2: Find rules with CHAOTIC or CYCLIC behavior
    print("\n" + "=" * 80)
    print("[Phase 2] Identifying interesting rules")

    interesting_rules = []
    for sig in signatures:
        if sig.omega in (OmegaClassifier.CHAOTIC, OmegaClassifier.CYCLIC):
            interesting_rules.append(sig)
            print(f"  Interesting: (a={sig.a}, b={sig.b}) -> {sig.omega} "
                  f"(overflow={sig.overflow_ratio*100:.1f}%, cycles={sig.cycle_count})")

    if interesting_rules:
        print(f"\nFound {len(interesting_rules)} interesting rules!")
    else:
        print("\nNo interesting rules found in this grid. Try expanding a,b range.")

    # Phase 3: Deep search on interesting rules
    if interesting_rules:
        print("\n" + "=" * 80)
        print("[Phase 3] Deep search for chaotic candidates")

        # Create a system with just the interesting rules
        system = SUBITCollatzSystem(num_rules=len(interesting_rules) + 10,
                                     max_bits=MAX_BITS + 4,  # Increase bits for deeper search
                                     max_steps=MAX_STEPS * 10)

        # Map interesting rules to rule IDs in the system
        # For simplicity, we'll just use the first few
        for idx, sig in enumerate(interesting_rules[:5]):
            # Find a rule with matching (a,b) in the system
            for rid, rule in enumerate(system.rules):
                if rule.a == sig.a and rule.b == sig.b:
                    print(f"\nDeep search for (a={sig.a}, b={sig.b})")
                    candidates = deep_search(system, [rid], num_starts=200, max_steps=5000)
                    for rid, cands in candidates.items():
                        if cands:
                            print(f"  Found {len(cands)} chaotic candidates:")
                            for c in cands[:5]:
                                print(f"    {c}")
                        else:
                            print("  No chaotic candidates found in this run.")
                    break

    print("\n" + "=" * 80)
    print("SUBIT-COLLATZ exploration complete.")
    print(f"Total signatures computed: {len(signatures)}")
    print("=" * 80)


if __name__ == "__main__":
    main()