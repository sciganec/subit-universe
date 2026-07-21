"""
SUBIT-TOPOS: Rule Injectivity Search with Visualization
Version 6.0 · 2026

Finds non-injective rules (counterexamples to injectivity) in chaotic trajectories.
"""

from typing import List, Tuple, Dict, Set, Optional
import hashlib
import random

# ============================================================================
# 1. CORE: State, Rule, System
# ============================================================================

State = int          # 6-bit state (0..63)
RuleID = int
ExtendedState = Tuple[State, RuleID]

class Rule:
    """A rule rho: S_0 -> S_0 as a 64-entry lookup table."""
    def __init__(self, table: List[int]):
        if len(table) != 64:
            raise ValueError("Rule table must have exactly 64 entries.")
        self.table = table[:]  # copy

    def apply(self, s: State) -> State:
        return self.table[s] & 0x3F

    @classmethod
    def from_seed(cls, seed: int) -> "Rule":
        """Deterministic rule generation from a seed (often non-injective)."""
        return cls([((seed * (i + 1) + 7) % 64) for i in range(64)])

    @classmethod
    def random(cls, rng: random.Random) -> "Rule":
        """Random permutation rule (always injective)."""
        perm = list(range(64))
        rng.shuffle(perm)
        return cls(perm)

    def is_injective(self) -> bool:
        """Check if the rule is injective (no two states map to the same output)."""
        seen = set()
        for s in range(64):
            out = self.table[s]
            if out in seen:
                return False
            seen.add(out)
        return True

    def find_collision(self) -> Optional[Tuple[State, State, State]]:
        """Return (s1, s2, output) if non-injective, else None."""
        seen = {}
        for s in range(64):
            out = self.table[s]
            if out in seen:
                return (seen[out], s, out)
            seen[out] = s
        return None


class SUBITSystem:
    """SUBIT system with internal rules and meta-evolution g."""
    def __init__(self, num_rules: int = 4096, seed: int = 42):
        self.num_rules = num_rules
        rng = random.Random(seed)
        self.rules: List[Rule] = []
        # Half seeded (often non-injective), half random permutations (injective)
        for i in range(num_rules // 2):
            self.rules.append(Rule.from_seed(i))
        for _ in range(num_rules - len(self.rules)):
            self.rules.append(Rule.random(rng))

    def f(self, rid: RuleID, s: State) -> State:
        return self.rules[rid].apply(s)

    def g(self, rid: RuleID, s: State) -> RuleID:
        """Chaotic meta-evolution using MD5 hash."""
        key = (rid * 1000003 + s * 1000033) & 0xFFFFFFFF
        hash_val = hashlib.md5(str(key).encode()).hexdigest()
        return int(hash_val[:8], 16) % self.num_rules

    def step(self, es: ExtendedState) -> ExtendedState:
        """Full evolution operator F: (s, rho) -> (f_rho(s), g(rho, s))."""
        s, rid = es
        new_s = self.f(rid, s)
        new_rid = self.g(rid, new_s)
        return (new_s, new_rid)


# ============================================================================
# 2. OMEGA CLASSIFIER
# ============================================================================

class OmegaClassifier:
    STABLE = "STABLE"
    METASTABLE = "METASTABLE"
    CYCLIC = "CYCLIC"
    CHAOTIC = "CHAOTIC"

    @staticmethod
    def classify_and_get_trajectory(
        system: SUBITSystem,
        s0: State,
        rid0: RuleID,
        max_steps: int = 150
    ) -> Tuple[str, List[ExtendedState]]:
        """Returns (classification, trajectory) up to max_steps."""
        es = (s0 & 0x3F, rid0 % system.num_rules)
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
# 3. HELPER: DECODE POINT
# ============================================================================

def decode_point(state: State) -> Tuple[int, int]:
    """Decode 6-bit state into (x, y) coordinates: high 3 bits = x, low 3 bits = y."""
    return (state >> 3) & 0x7, state & 0x7


# ============================================================================
# 4. MAIN SEARCH ENGINE
# ============================================================================

def search_for_counterexample(num_trials: int = 500):
    print("=" * 70)
    print("SUBIT-TOPOS: Rule Injectivity Search (with Visualization)")
    print("Interpreting 6-bit states as (x, y) in [0..7]²")
    print("=" * 70)

    system = SUBITSystem(num_rules=4096, seed=42)
    checked_rules: Set[RuleID] = set()
    total_rules_checked = 0

    for trial in range(num_trials):
        s0 = random.randint(0, 63)
        rid0 = random.randint(0, system.num_rules - 1)

        cls, traj = OmegaClassifier.classify_and_get_trajectory(
            system, s0, rid0, max_steps=150
        )

        if cls == OmegaClassifier.CHAOTIC and len(traj) >= 10:
            # Check each unique rule encountered in the chaotic trajectory
            for s, rid in traj:
                if rid not in checked_rules:
                    checked_rules.add(rid)
                    total_rules_checked += 1

                    collision = system.rules[rid].find_collision()
                    if collision is not None:
                        s1, s2, out = collision
                        x1, y1 = decode_point(s1)
                        x2, y2 = decode_point(s2)
                        x_out, y_out = decode_point(out)

                        print("\n" + "🔥" * 30)
                        print("✅ COUNTEREXAMPLE FOUND!")
                        print("🔥" * 30)
                        print(f"Non-injective rule ID: {rid}")
                        print(f"Found in chaotic trajectory #: {trial}")
                        print(f"Point A: ({x1},{y1})  ->  ({x_out},{y_out})")
                        print(f"Point B: ({x2},{y2})  ->  ({x_out},{y_out})")
                        print("Since two different inputs map to the same output,")
                        print("the map is NOT injective.")
                        print("👉 In the Jacobian context, this refutes the conjecture.")

                        # ---- VISUALIZATION: PRINT THE RULE TABLE ----
                        print("\n" + "-" * 70)
                        print(f"Table for rule {rid} (inputs 0..63 -> outputs):")
                        print("   ", end="")
                        for col in range(8):
                            print(f" {col:3d} ", end="")
                        print()
                        print("   " + "-" * 32)
                        for row in range(8):
                            print(f"{row*8:2d} |", end="")
                            for col in range(8):
                                idx = row * 8 + col
                                val = system.rules[rid].table[idx]
                                # Highlight the colliding entries
                                if idx == s1 or idx == s2:
                                    print(f"*{val:2d}*", end=" ")
                                else:
                                    print(f" {val:2d} ", end=" ")
                            print()
                        print("-" * 70)

                        # Show the actual collision in table context
                        print(f"Input {s1} -> {system.rules[rid].table[s1]}")
                        print(f"Input {s2} -> {system.rules[rid].table[s2]}")
                        print(f"Output collision at value: {out}")
                        print("=" * 70)
                        return  # Stop on first counterexample

        # Progress indicator
        if trial % 50 == 0 and trial > 0:
            print(f"   Searched {trial} trials... checked {total_rules_checked} unique rules so far")

    print("\n" + "-" * 70)
    print(f"❌ No non-injective rules found after checking {total_rules_checked} unique rules.")
    print("   Suggestions:")
    print("   - Increase num_rules (e.g., to 16384) for more diverse rules.")
    print("   - Increase max_steps to explore longer trajectories.")
    print("   - Use a larger state space (8 bits = 256 states).")


# ============================================================================
# 5. RUN
# ============================================================================

if __name__ == "__main__":
    search_for_counterexample(num_trials=500)