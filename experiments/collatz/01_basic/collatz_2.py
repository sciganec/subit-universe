"""
SUBIT-COLLATZ v2: Deep Explorer
Version 2.0 · 2026

Expands the atlas to larger grids, automatically verifies CHAOTIC candidates
without bit truncation, and prints detailed cycles for CYCLIC rules.
"""

from typing import List, Tuple, Dict, Optional, Set
import random
import hashlib
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field

# ============================================================================
# 1. CORE: Collatz Rule (with overflow tracking)
# ============================================================================

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
        self.overflow_value = 0
        self.cycle_detected = False
        self.cycle_start = -1
        self.cycle_length = 0
        self.trajectory_cache = []

    def reset_stats(self):
        self.steps = 0
        self.max_reached = 0
        self.overflow = False
        self.overflow_value = 0
        self.cycle_detected = False
        self.cycle_start = -1
        self.cycle_length = 0
        self.trajectory_cache = []

    def apply(self, n: int) -> int:
        """Apply one step of the Collatz map."""
        self.steps += 1
        if n > self.max_reached:
            self.max_reached = n

        if n == 1:
            return 1

        if n % 2 == 0:
            return n // 2
        else:
            val = self.a * n + self.b
            if val > self.limit:
                self.overflow = True
                self.overflow_value = val
                return val % self.limit  # Wrap around for finite simulation
            return val

    def trajectory(self, n: int) -> Tuple[str, List[int]]:
        """
        Run trajectory until:
        - reaches 1 (STABLE)
        - detects a cycle (CYCLIC)
        - exceeds max_steps (CHAOTIC candidate)
        """
        self.reset_stats()
        seen: Dict[int, int] = {}
        traj: List[int] = []
        current = n
        step = 0

        while True:
            if current in seen:
                self.cycle_detected = True
                self.cycle_start = seen[current]
                self.cycle_length = step - seen[current]
                self.trajectory_cache = traj
                return "CYCLIC", traj

            traj.append(current)
            seen[current] = step

            if current == 1:
                self.trajectory_cache = traj
                return "STABLE", traj

            if step >= self.max_steps:
                self.trajectory_cache = traj
                return "CHAOTIC", traj

            current = self.apply(current)
            step += 1


# ============================================================================
# 2. DEEP VERIFICATION (without bit truncation)
# ============================================================================

def deep_verify(start: int, a: int, b: int,
                max_steps: int = 500000,
                max_value: int = 10**100) -> Tuple[str, int, Optional[int]]:
    """
    Run Collatz WITHOUT bit truncation (Python big ints).
    Returns: (status, steps, value_or_cycle)
    - status: "STABLE", "CYCLIC", "ESCAPE_CANDIDATE", or "UNKNOWN"
    """
    seen: Dict[int, int] = {}
    current = start
    step = 0

    while current not in seen:
        if current > max_value:
            return "ESCAPE_CANDIDATE", step, current

        seen[current] = step

        if current == 1:
            return "STABLE", step, 1

        if step > max_steps:
            return "UNKNOWN", step, current

        if current % 2 == 0:
            current //= 2
        else:
            current = a * current + b
        step += 1

    # Cycle detected
    cycle_start = seen[current]
    cycle = [k for k in seen if seen[k] >= cycle_start]
    return "CYCLIC", step, cycle


# ============================================================================
# 3. SUBIT SYSTEM WRAPPER
# ============================================================================

class SUBITCollatzSystem:
    def __init__(self, num_rules: int = 256, max_bits: int = 16, max_steps: int = 1000):
        self.num_rules = num_rules
        self.max_bits = max_bits
        self.max_steps = max_steps
        self.limit = (1 << max_bits) - 1

        self.rules: List[CollatzRule] = []
        param_pairs = self._generate_param_pairs(num_rules)
        for a, b in param_pairs:
            self.rules.append(CollatzRule(a, b, max_bits, max_steps))

    def _generate_param_pairs(self, n: int) -> List[Tuple[int, int]]:
        pairs = []
        pairs.append((3, 1))  # classic

        # Systematic grid: a in 1..15, b in 1..15 (if n is large)
        grid_range = min(15, n // 4 + 1)
        for a in range(1, grid_range + 1):
            for b in range(1, grid_range + 1):
                if (a, b) not in pairs:
                    pairs.append((a, b))

        rng = random.Random(42)
        while len(pairs) < n:
            a = rng.randint(1, 15)
            b = rng.randint(1, 15)
            if (a, b) not in pairs:
                pairs.append((a, b))

        return pairs[:n]

    def f(self, rid: int, s: int) -> int:
        return self.rules[rid].apply(s)

    def g(self, rid: int, s: int) -> int:
        key = (rid * 1000003 + s * 1000033) & 0xFFFFFFFF
        hash_val = hashlib.md5(str(key).encode()).hexdigest()
        return int(hash_val[:8], 16) % self.num_rules

    def step(self, es: Tuple[int, int]) -> Tuple[int, int]:
        s, rid = es
        new_s = self.f(rid, s)
        new_rid = self.g(rid, new_s)
        return (new_s, new_rid)


# ============================================================================
# 4. OMEGA CLASSIFIER
# ============================================================================

class OmegaClassifier:
    STABLE = "STABLE"
    METASTABLE = "METASTABLE"
    CYCLIC = "CYCLIC"
    CHAOTIC = "CHAOTIC"

    @staticmethod
    def classify_rule(rule: CollatzRule, s0: int) -> Tuple[str, List[int]]:
        return rule.trajectory(s0)


# ============================================================================
# 5. SIGNATURE COMPUTATION
# ============================================================================

@dataclass
class CollatzSignature:
    a: int
    b: int
    omega: str
    stable_ratio: float
    avg_steps: float
    avg_max: float
    overflow_ratio: float
    cycle_count: int
    cycle_lengths: List[int] = field(default_factory=list)
    chaotic_samples: List[int] = field(default_factory=list)  # starting numbers that overflowed


def compute_signature(rule: CollatzRule, num_samples: int = 100) -> CollatzSignature:
    stable_count = 0
    overflow_count = 0
    total_steps = 0
    total_max = 0
    cycles_found: List[int] = []
    cycle_lengths: List[int] = []
    chaotic_samples: List[int] = []

    for _ in range(num_samples):
        s0 = random.randint(2, rule.limit // 4)
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
            chaotic_samples.append(s0)
            total_steps += rule.steps
            total_max += rule.max_reached

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
        chaotic_samples=chaotic_samples,
    )


# ============================================================================
# 6. ATLAS BUILDER
# ============================================================================

def build_collatz_atlas(param_grid: List[Tuple[int, int]],
                         num_samples: int = 100,
                         max_bits: int = 16,
                         max_steps: int = 1000) -> List[CollatzSignature]:
    signatures = []
    total = len(param_grid)
    for idx, (a, b) in enumerate(param_grid):
        print(f"  [{idx+1}/{total}] Computing signature for (a={a}, b={b})...")
        rule = CollatzRule(a, b, max_bits, max_steps)
        sig = compute_signature(rule, num_samples)
        signatures.append(sig)
    return signatures


def print_atlas_table(signatures: List[CollatzSignature]):
    print("\n" + "=" * 90)
    print("SUBIT-COLLATZ ATLAS")
    print("=" * 90)
    print(f"{'a':<4} {'b':<4} {'Ω':<12} {'Stable%':<10} {'Overflow%':<12} {'Cycles':<8} {'Avg Steps':<12}")
    print("-" * 90)
    for sig in sorted(signatures, key=lambda x: (x.a, x.b)):
        print(f"{sig.a:<4} {sig.b:<4} {sig.omega:<12} "
              f"{sig.stable_ratio*100:<10.1f} "
              f"{sig.overflow_ratio*100:<12.1f} "
              f"{sig.cycle_count:<8} "
              f"{sig.avg_steps:<12.1f}")
    print("=" * 90)


def print_heatmap(signatures: List[CollatzSignature]):
    omega_map = {(sig.a, sig.b): sig.omega for sig in signatures}
    a_values = sorted(set(sig.a for sig in signatures))
    b_values = sorted(set(sig.b for sig in signatures))

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
# 7. ANOMALY INVESTIGATORS
# ============================================================================

def investigate_cycles(rule: CollatzRule, max_starts: int = 200):
    """Find and print up to 5 distinct cycles for a given rule."""
    print(f"\n  Investigating cycles for (a={rule.a}, b={rule.b})...")
    cycles_found = []
    seen_starts = set()

    for _ in range(max_starts):
        s0 = random.randint(2, rule.limit // 4)
        if s0 in seen_starts:
            continue
        seen_starts.add(s0)

        omega, traj = rule.trajectory(s0)
        if omega == "CYCLIC":
            cycle = traj[rule.cycle_start:]
            # Normalize cycle representation (start with smallest element)
            min_idx = min(range(len(cycle)), key=lambda i: cycle[i])
            norm_cycle = cycle[min_idx:] + cycle[:min_idx]
            if norm_cycle not in cycles_found:
                cycles_found.append(norm_cycle)
                print(f"    Cycle #{len(cycles_found)} (len={len(norm_cycle)}): "
                      f"{norm_cycle[:8]}... (first 8 elements)")
                if len(cycles_found) >= 5:
                    break

    if not cycles_found:
        print("    No cycles found in this sample.")
    return cycles_found


def investigate_chaotic_candidates(signatures: List[CollatzSignature],
                                   max_to_check: int = 5,
                                   deep_max_steps: int = 500000):
    """Deep verify CHAOTIC candidates from the atlas."""
    print("\n" + "=" * 90)
    print("DEEP VERIFICATION OF CHAOTIC CANDIDATES (no bit truncation)")
    print("=" * 90)

    # Collect all CHAOTIC signatures with samples
    chaotic_sigs = [sig for sig in signatures if sig.omega == OmegaClassifier.CHAOTIC and sig.chaotic_samples]

    if not chaotic_sigs:
        print("No CHAOTIC candidates to verify.")
        return

    results = []

    for sig in chaotic_sigs[:max_to_check]:
        print(f"\n▶ Verifying rule (a={sig.a}, b={sig.b})")
        print(f"  Found {len(sig.chaotic_samples)} candidate starting numbers.")

        # Take the first few samples
        for start_n in sig.chaotic_samples[:3]:
            status, steps, data = deep_verify(start_n, sig.a, sig.b,
                                               max_steps=deep_max_steps,
                                               max_value=10**100)

            if status == "ESCAPE_CANDIDATE":
                print(f"    🚀 ESCAPE CANDIDATE! n={start_n} grew beyond 10^100 "
                      f"after {steps} steps. Last value: {data:.2e}")
                results.append((sig.a, sig.b, start_n, status, steps))
            elif status == "STABLE":
                print(f"    ✅ STABLE: n={start_n} reached 1 after {steps} steps "
                      f"(long transient, but stable).")
            elif status == "CYCLIC":
                print(f"    🔄 CYCLIC: n={start_n} entered a cycle of length "
                      f"{len(data)} after {steps} steps.")
            else:
                print(f"    ❓ UNKNOWN: n={start_n} ran for {steps} steps without conclusion.")

    return results


# ============================================================================
# 8. MAIN
# ============================================================================

def main():
    print("=" * 90)
    print("SUBIT-COLLATZ v2: Deep Explorer")
    print("Using SUBIT-TOPOS Core v0.1")
    print("=" * 90)

    # ---- Configuration ----
    MAX_BITS = 16
    MAX_STEPS = 2000          # For atlas exploration
    NUM_SAMPLES = 80          # Per rule signature
    GRID_A = range(1, 8)      # 1..7
    GRID_B = range(1, 8)      # 1..7
    DEEP_MAX_STEPS = 200000   # For deep verification

    # Build parameter grid
    param_grid = [(a, b) for a in GRID_A for b in GRID_B]
    print(f"\n[Phase 1] Building atlas: {len(param_grid)} rules "
          f"(max_bits={MAX_BITS}, samples={NUM_SAMPLES})")

    start_time = time.time()
    signatures = build_collatz_atlas(param_grid, num_samples=NUM_SAMPLES,
                                      max_bits=MAX_BITS, max_steps=MAX_STEPS)
    elapsed = time.time() - start_time
    print(f"Atlas built in {elapsed:.1f} seconds")

    # Print atlas
    print_atlas_table(signatures)
    print_heatmap(signatures)

    # ---- Phase 2: Investigate interesting rules ----
    print("\n" + "=" * 90)
    print("[Phase 2] Investigating Anomalies")
    print("=" * 90)

    # Find CHAOTIC and CYCLIC signatures
    chaotic_sigs = [sig for sig in signatures if sig.omega == OmegaClassifier.CHAOTIC]
    cyclic_sigs = [sig for sig in signatures if sig.omega == OmegaClassifier.CYCLIC]

    print(f"\nFound {len(chaotic_sigs)} CHAOTIC rules, {len(cyclic_sigs)} CYCLIC rules.")

    # Investigate first few CYCLIC rules
    if cyclic_sigs:
        print("\n--- CYCLIC RULES (cycle search) ---")
        for sig in cyclic_sigs[:5]:
            rule = CollatzRule(sig.a, sig.b, max_bits=MAX_BITS, max_steps=MAX_STEPS)
            investigate_cycles(rule, max_starts=100)

    # Deep verify CHAOTIC candidates
    if chaotic_sigs:
        print("\n--- CHAOTIC RULES (deep verification) ---")
        results = investigate_chaotic_candidates(chaotic_sigs,
                                                  max_to_check=5,
                                                  deep_max_steps=DEEP_MAX_STEPS)

        # Summary
        if results:
            print("\n" + "=" * 90)
            print("SUMMARY OF ESCAPE CANDIDATES")
            print("=" * 90)
            for a, b, n, status, steps in results:
                print(f"  (a={a}, b={b}): n={n} -> {status} after {steps} steps")
            print("\n⚠️  Note: 'ESCAPE_CANDIDATE' means the value exceeded 10^100.")
            print("   This is a strong candidate but NOT a proof.")
            print("   To prove divergence, one must show it never returns to 1.")
        else:
            print("\nNo escape candidates found. The CHAOTIC samples likely just had long transients.")

    print("\n" + "=" * 90)
    print("SUBIT-COLLATZ v2 exploration complete.")
    print(f"Total signatures computed: {len(signatures)}")
    print("=" * 90)


if __name__ == "__main__":
    main()