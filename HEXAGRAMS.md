# SUBIT-64 — Hexagram Correspondence

Complete mapping between 6-bit SUBIT states and I-Ching hexagrams.

---

## Encoding Scheme

```
State = b₁b₂b₃b₄b₅b₆ ∈ {0,1}⁶

WHO   = b₁b₂  ∈ {10, 11, 01, 00} = {ME, WE, YOU, THEY}
WHERE = b₃b₄  ∈ {10, 11, 01, 00} = {EAST, SOUTH, WEST, NORTH}
WHEN  = b₅b₆  ∈ {10, 11, 01, 00} = {SPRING, SUMMER, AUTUMN, WINTER}
```

```
Lower Trigram = b₁b₂b₃  →  WHO + first bit of WHERE
Upper Trigram = b₄b₅b₆  →  second bit of WHERE + WHEN
```

---

## Bit-to-Value Mapping

| Bits | WHO | WHERE | WHEN |
|:--:|:---|:---|:---|
| 10 | ME | EAST | SPRING |
| 11 | WE | SOUTH | SUMMER |
| 01 | YOU | WEST | AUTUMN |
| 00 | THEY | NORTH | WINTER |

---

## Trigram Mapping

| Bits | Trigram | Symbol | Direction | Element |
|:--:|:---|:---:|:---|:---|
| 111 | ☰ Heaven | 乾 | North-East | — |
| 110 | ☱ Lake | 兌 | East-East | — |
| 101 | ☲ Fire | 離 | South-East | — |
| 100 | ☳ Thunder | 震 | South-South | — |
| 011 | ☴ Wind | 巽 | South-West | — |
| 010 | ☵ Water | 坎 | West-West | — |
| 001 | ☶ Mountain | 艮 | North-West | — |
| 000 | ☷ Earth | 坤 | North-North | — |

---

## Complete Hexagram Table

| # | Glyph | Binary | Lower | Upper | WHO | WHERE | WHEN |
|:--:|:---:|:---:|:---:|:---:|:---|:---|:---|
| 01 | ䷀ | 111111 | ☰ Heaven | ☰ Heaven | WE | SOUTH | SUMMER |
| 02 | ䷁ | 000000 | ☷ Earth | ☷ Earth | THEY | NORTH | WINTER |
| 03 | ䷂ | 100010 | ☳ Thunder | ☵ Water | ME | EAST | WINTER |
| 04 | ䷃ | 010001 | ☵ Water | ☶ Mountain | YOU | WEST | AUTUMN |
| 05 | ䷄ | 111010 | ☰ Heaven | ☵ Water | WE | SOUTH | WINTER |
| 06 | ䷅ | 010111 | ☵ Water | ☰ Heaven | YOU | WEST | SUMMER |
| 07 | ䷆ | 010000 | ☵ Water | ☷ Earth | YOU | WEST | WINTER |
| 08 | ䷇ | 000010 | ☷ Earth | ☵ Water | THEY | NORTH | WINTER |
| 09 | ䷈ | 111011 | ☰ Heaven | ☴ Wind | WE | SOUTH | AUTUMN |
| 10 | ䷉ | 110111 | ☱ Lake | ☰ Heaven | WE | EAST | SUMMER |
| 11 | ䷊ | 111000 | ☰ Heaven | ☷ Earth | WE | SOUTH | WINTER |
| 12 | ䷋ | 000111 | ☷ Earth | ☰ Heaven | THEY | NORTH | SUMMER |
| 13 | ䷌ | 101111 | ☲ Fire | ☰ Heaven | ME | SOUTH | SUMMER |
| 14 | ䷍ | 111101 | ☰ Heaven | ☲ Fire | WE | SOUTH | AUTUMN |
| 15 | ䷎ | 001000 | ☶ Mountain | ☷ Earth | YOU | NORTH | WINTER |
| 16 | ䷏ | 000100 | ☷ Earth | ☳ Thunder | THEY | NORTH | SPRING |
| 17 | ䷐ | 100110 | ☳ Thunder | ☱ Lake | ME | EAST | SUMMER |
| 18 | ䷑ | 011001 | ☴ Wind | ☶ Mountain | YOU | EAST | AUTUMN |
| 19 | ䷒ | 110000 | ☱ Lake | ☷ Earth | WE | EAST | WINTER |
| 20 | ䷓ | 000011 | ☷ Earth | ☴ Wind | THEY | NORTH | AUTUMN |
| 21 | ䷔ | 100101 | ☳ Thunder | ☲ Fire | ME | EAST | AUTUMN |
| 22 | ䷕ | 101001 | ☲ Fire | ☶ Mountain | ME | WEST | AUTUMN |
| 23 | ䷖ | 000001 | ☷ Earth | ☶ Mountain | THEY | NORTH | AUTUMN |
| 24 | ䷗ | 100000 | ☳ Thunder | ☷ Earth | ME | EAST | WINTER |
| 25 | ䷘ | 100111 | ☳ Thunder | ☰ Heaven | ME | EAST | SUMMER |
| 26 | ䷙ | 111001 | ☰ Heaven | ☶ Mountain | WE | SOUTH | AUTUMN |
| 27 | ䷚ | 100001 | ☳ Thunder | ☶ Mountain | ME | EAST | AUTUMN |
| 28 | ䷛ | 011110 | ☴ Wind | ☱ Lake | YOU | EAST | SUMMER |
| 29 | ䷜ | 010010 | ☵ Water | ☵ Water | YOU | WEST | WINTER |
| 30 | ䷝ | 101101 | ☲ Fire | ☲ Fire | ME | SOUTH | AUTUMN |
| 31 | ䷞ | 001110 | ☶ Mountain | ☱ Lake | YOU | NORTH | SUMMER |
| 32 | ䷟ | 011100 | ☴ Wind | ☳ Thunder | YOU | EAST | SPRING |
| 33 | ䷠ | 001111 | ☶ Mountain | ☰ Heaven | YOU | NORTH | SUMMER |
| 34 | ䷡ | 111100 | ☰ Heaven | ☳ Thunder | WE | SOUTH | SPRING |
| 35 | ䷢ | 000101 | ☷ Earth | ☲ Fire | THEY | NORTH | AUTUMN |
| 36 | ䷣ | 101000 | ☲ Fire | ☷ Earth | ME | SOUTH | WINTER |
| 37 | ䷤ | 101011 | ☲ Fire | ☴ Wind | ME | SOUTH | AUTUMN |
| 38 | ䷥ | 110101 | ☱ Lake | ☲ Fire | WE | EAST | AUTUMN |
| 39 | ䷦ | 001010 | ☶ Mountain | ☵ Water | YOU | NORTH | WINTER |
| 40 | ䷧ | 010100 | ☵ Water | ☳ Thunder | YOU | WEST | SPRING |
| 41 | ䷨ | 110001 | ☱ Lake | ☶ Mountain | WE | EAST | AUTUMN |
| 42 | ䷩ | 100011 | ☳ Thunder | ☴ Wind | ME | EAST | AUTUMN |
| 43 | ䷪ | 111110 | ☰ Heaven | ☱ Lake | WE | SOUTH | SUMMER |
| 44 | ䷫ | 011111 | ☴ Wind | ☰ Heaven | YOU | EAST | SUMMER |
| 45 | ䷬ | 000110 | ☷ Earth | ☱ Lake | THEY | NORTH | SUMMER |
| 46 | ䷭ | 011000 | ☴ Wind | ☷ Earth | YOU | EAST | WINTER |
| 47 | ䷮ | 010110 | ☵ Water | ☱ Lake | YOU | WEST | SUMMER |
| 48 | ䷯ | 011010 | ☴ Wind | ☵ Water | YOU | EAST | WINTER |
| 49 | ䷰ | 101110 | ☲ Fire | ☱ Lake | ME | SOUTH | SUMMER |
| 50 | ䷱ | 011101 | ☴ Wind | ☲ Fire | YOU | EAST | AUTUMN |
| 51 | ䷲ | 100100 | ☳ Thunder | ☳ Thunder | ME | EAST | SPRING |
| 52 | ䷳ | 001001 | ☶ Mountain | ☶ Mountain | YOU | NORTH | AUTUMN |
| 53 | ䷴ | 001011 | ☶ Mountain | ☴ Wind | YOU | NORTH | AUTUMN |
| 54 | ䷵ | 110100 | ☱ Lake | ☳ Thunder | WE | EAST | SPRING |
| 55 | ䷶ | 101100 | ☲ Fire | ☳ Thunder | ME | SOUTH | SPRING |
| 56 | ䷷ | 001101 | ☶ Mountain | ☲ Fire | YOU | NORTH | AUTUMN |
| 57 | ䷸ | 011011 | ☴ Wind | ☴ Wind | YOU | EAST | AUTUMN |
| 58 | ䷹ | 110110 | ☱ Lake | ☱ Lake | WE | EAST | SUMMER |
| 59 | ䷺ | 010011 | ☵ Water | ☴ Wind | YOU | WEST | AUTUMN |
| 60 | ䷻ | 110010 | ☱ Lake | ☵ Water | WE | EAST | WINTER |
| 61 | ䷼ | 110011 | ☱ Lake | ☴ Wind | WE | EAST | AUTUMN |
| 62 | ䷽ | 001100 | ☶ Mountain | ☳ Thunder | YOU | NORTH | SPRING |
| 63 | ䷾ | 101010 | ☲ Fire | ☵ Water | ME | SOUTH | WINTER |
| 64 | ䷿ | 010101 | ☵ Water | ☲ Fire | YOU | WEST | AUTUMN |

---

## Lookup by Binary

| Binary | # | Glyph | Binary | # | Glyph |
|:---:|:--:|:---:|:---:|:--:|:---:|
| 000000 | 02 | ䷁ | 100000 | 24 | ䷗ |
| 000001 | 23 | ䷖ | 100001 | 27 | ䷚ |
| 000010 | 08 | ䷇ | 100010 | 03 | ䷂ |
| 000011 | 20 | ䷓ | 100011 | 42 | ䷩ |
| 000100 | 16 | ䷏ | 100100 | 51 | ䷲ |
| 000101 | 35 | ䷢ | 100101 | 21 | ䷔ |
| 000110 | 45 | ䷬ | 100110 | 17 | ䷐ |
| 000111 | 12 | ䷋ | 100111 | 25 | ䷘ |
| 001000 | 15 | ䷎ | 101000 | 36 | ䷣ |
| 001001 | 52 | ䷳ | 101001 | 22 | ䷕ |
| 001010 | 39 | ䷦ | 101010 | 63 | ䷾ |
| 001011 | 53 | ䷴ | 101011 | 37 | ䷤ |
| 001100 | 62 | ䷽ | 101100 | 55 | ䷶ |
| 001101 | 56 | ䷷ | 101101 | 30 | ䷝ |
| 001110 | 31 | ䷞ | 101110 | 49 | ䷰ |
| 001111 | 33 | ䷠ | 101111 | 13 | ䷌ |
| 010000 | 07 | ䷆ | 110000 | 19 | ䷒ |
| 010001 | 04 | ䷃ | 110001 | 41 | ䷨ |
| 010010 | 29 | ䷜ | 110010 | 60 | ䷻ |
| 010011 | 59 | ䷺ | 110011 | 61 | ䷼ |
| 010100 | 40 | ䷧ | 110100 | 54 | ䷵ |
| 010101 | 64 | ䷿ | 110101 | 38 | ䷥ |
| 010110 | 47 | ䷮ | 110110 | 58 | ䷹ |
| 010111 | 06 | ䷅ | 110111 | 10 | ䷉ |
| 011000 | 46 | ䷭ | 111000 | 11 | ䷊ |
| 011001 | 18 | ䷑ | 111001 | 26 | ䷙ |
| 011010 | 48 | ䷯ | 111010 | 05 | ䷄ |
| 011011 | 57 | ䷸ | 111011 | 09 | ䷈ |
| 011100 | 32 | ䷟ | 111100 | 34 | ䷡ |
| 011101 | 50 | ䷱ | 111101 | 14 | ䷍ |
| 011110 | 28 | ䷛ | 111110 | 43 | ䷪ |
| 011111 | 44 | ䷫ | 111111 | 01 | ䷀ |

---

## Structural Observations

### Symmetry Pairs
| Pair | Binary Relation | Meaning |
|:---|:---|:---|
| 01 ↔ 02 | 111111 ↔ 000000 | Heaven ↔ Earth (perfect opposition) |
| 11 ↔ 12 | 111000 ↔ 000111 | Peace ↔ Stagnation |
| 29 ↔ 30 | 010010 ↔ 101101 | Water ↔ Fire (elemental opposition) |
| 51 ↔ 52 | 100100 ↔ 001001 | Thunder ↔ Mountain |
| 57 ↔ 58 | 011011 ↔ 110110 | Wind ↔ Lake |

### Self-Symmetric (Palindromic Binary)
None in standard ordering; all hexagrams have distinct bit-reversals.

### Pure Trigram Doubles
| # | Glyph | Binary | Trigram | Element |
|:--:|:---:|:---:|:---:|:---|
| 01 | ䷀ | 111111 | ☰☰ Heaven·Heaven | — |
| 02 | ䷁ | 000000 | ☷☷ Earth·Earth | — |
| 29 | ䷜ | 010010 | ☵☵ Water·Water | — |
| 30 | ䷝ | 101101 | ☲☲ Fire·Fire | — |
| 51 | ䷲ | 100100 | ☳☳ Thunder·Thunder | — |
| 52 | ䷳ | 001001 | ☶☶ Mountain·Mountain | — |
| 57 | ䷸ | 011011 | ☴☴ Wind·Wind | — |
| 58 | ䷹ | 110110 | ☱☱ Lake·Lake | — |

---

## Alternative Encodings

### By Color (Trigram Palette)
| Trigram | Color |
|:---:|:---|
| 111 ☰ | Blue |
| 110 ☱ | Green |
| 101 ☲ | Lime |
| 100 ☳ | Yellow |
| 011 ☴ | Orange |
| 010 ☵ | Red |
| 001 ☶ | Burgundy |
| 000 ☷ | Purple |

### By Direction (Double)
| Lower | Upper | Composite Direction |
|:---:|:---:|:---|
| 111 NE | 111 NE | North-East → North-East |
| 110 EE | 110 EE | East-East → East-East |
| ... | ... | ... |

---

## Validation

```python
def validate_hexagram_table():
    """Verify all 64 entries are unique and cover full space"""
    seen = set()
    for entry in HEXAGRAM_TABLE:
        bits = entry['binary']
        assert len(bits) == 6
        assert all(b in '01' for b in bits)
        assert bits not in seen
        seen.add(bits)
    assert len(seen) == 64
    print("Valid: 64 unique 6-bit states")
```

---
