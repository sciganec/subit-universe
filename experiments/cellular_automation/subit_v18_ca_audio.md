 # SUBIT v18 Application Specification

## 1. General Information

| Parameter | Value |
|-----------|-------|
| **Name** | SUBIT v18: Active Rule Ecology + Audio |
| **Version** | 18 |
| **Type** | Interactive web-based cellular automaton simulator with evolutionary rule dynamics |
| **Interface Language** | Ukrainian |
| **Technologies** | HTML5, CSS3, Vanilla JavaScript, Web Audio API, Canvas API |
| **Author** | Not specified (open-source style) |

---

## 2. System Architecture

### 2.1 Components

```
┌─────────────────────────────────────────────────────────────┐
│                         SUBIT v18                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Core       │  │ Visualization│  │  Audio System    │  │
│  │  Simulation  │  │   (Canvas)   │  │  (Web Audio API) │  │
│  │              │  │              │  │                  │  │
│  │ • Cellular   │  │ • 6 canvas   │  │ • FM/AM/Additive │  │
│  │   automaton  │  │   elements   │  │ • Chorus         │  │
│  │ • Rule       │  │ • Phase      │  │ • Reverb         │  │
│  │   evolution  │  │   space      │  │ • Visualizer     │  │
│  │ • Metrics    │  │ • Heatmaps   │  │ • 3 data         │  │
│  │              │  │              │  │   mappings       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Control    │  │   Audio      │  │   Statistics     │  │
│  │   Panel      │  │   Panel      │  │   & Metrics      │  │
│  │              │  │              │  │                  │  │
│  │ • Sliders    │  │ • Synthesis  │  │ • Top-5 rules    │  │
│  │ • Checkboxes │  │ • Mapping    │  │ • Fitness func.  │  │
│  │ • Buttons    │  │ • Volume     │  │ • Entropy        │  │
│  │ • Hotkeys    │  │ • Frequency  │  │ • Phase Ω        │  │
│  │              │  │ • Reverb     │  │ • Trajectories   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
User → Parameters → Core Simulation → Cell States (states[])
                                    ↓
                              Rules (rules[])
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              Metrics         Visualization      Audio Synthesis
           (H_rule, Δrule)   (6 canvases)       (Web Audio)
                    ↓               ↓               ↓
              Phase Ω          DOM Updates       Analyser
           (STABLE/CYCLIC/    (tables,          (visualizer)
            CHAOTIC/META)     graphs)
```

---

## 3. Simulation Core

### 3.1 Cellular Automaton Model

| Parameter | Value |
|-----------|-------|
| **Topology** | Toroidal grid (cyclic boundaries) |
| **Grid Size** | 40–120 cells (configurable, default 80×80) |
| **Neighborhood** | Moore (8 neighbors: N, NE, E, SE, S, SW, W, NW) |
| **Cell States** | Binary: 0 (dead), 1 (alive) |
| **Rules** | 8-bit (0–255), each cell has its own rule |

### 3.2 Transition Rule (B3/S23-like)

```
For each cell (x, y):
  1. Count live neighbors (liveNeighbors ∈ [0, 8])
  2. New state = (rule[cell] >> liveNeighbors) & 1
     • Bit 0 → dead
     • Bit 1 → alive
  3. Determine dominant rule among live neighbors (voting)
  4. Update cell rule depending on state and mutations
```

### 3.3 Rule Evolution

| Mechanism | Description | Probability |
|-----------|-------------|-------------|
| **Live adaptation** | Inherit dominant neighbor rule with mutation | Always |
| **Live mutation** | Random deviation from dominant rule | `±liveMutRange` |
| **Dead adaptation** | Dead cells copy neighbor rule | `deadAdaptRate` (0–100%) |
| **Global mutation** | Completely random new rule | `mutationRate` (0–5%) |

---

## 4. Metrics & Analytics

### 4.1 Core Metrics

| Metric | Formula | Range | Description |
|--------|---------|-------|-------------|
| **Population** | `Σ states[i]` | [0, SIZE²] | Number of live cells |
| **Rule Entropy (H_rule)** | `-Σ p(r) × log₂(p(r))` | [0, 8] | Diversity of rules in population |
| **Average Rule Change (Δrule)** | `Σ |newRule - oldRule| / pop` | [0, 255] | Speed of rule evolution |
| **Unique Rules** | `|{r : freq(r) > 0}|` | [0, 256] | Count of active rules |
| **Density** | `pop / SIZE² × 100%` | [0%, 100%] | Percentage of live cells |
| **Rule Fitness** | `children / parents` | [0, ∞) | Reproductive success |

### 4.2 Phase Classification (Ω)

| Phase | Condition | Color | Description |
|-------|-----------|-------|-------------|
| **STABLE** | `Δrule < 0.5` AND `H_rule > 0.8` | 🟢 Green | Stable ecosystem, few changes, high diversity |
| **CYCLIC** | `Δrule < 2.0` AND `H_rule > 0.4` | 🟡 Yellow | Cyclic dynamics, moderate change |
| **CHAOTIC** | `Δrule > 5.0` | 🔴 Red | Chaotic evolution, rapid rule changes |
| **META** | Everything else | 🔵 Purple | Transitional/metastable phase |

---

## 5. Visualization

### 5.1 Canvas Elements

| ID | Size | Purpose | Update Rate |
|----|------|---------|-------------|
| `mainCanvas` | 400×400 | Physical space: colored live cells | Every 3 generations |
| `ruleCanvas` | 200×200 | Rule space: rule map (R, 255-R, 3R) | Every 3 generations |
| `deltaCanvas` | 200×200 | Change map: intensity = Δrule × 8 | Every 3 generations |
| `transCanvas` | 256×256 | Transition graph: rule → new rule (heatmap) | Every 3 generations |
| `omegaPlot` | 500×150 | Trajectory: H_rule (green) & Δrule (red) | Every 3 generations |
| `phaseCanvas` | 200×200 | Phase space: Δrule (X) vs H_rule (Y) | Every 3 generations |
| `audioCanvas` | 500×80 | Audio visualizer (frequency spectrum) | Every frame |

### 5.2 Color Scheme

- **Live cells**: HSL hue depending on rule (`hue = rule × 360 / 256`)
- **Background**: `#0a0a0a` (dark)
- **Panels**: `#141414` with 8px radius
- **Accent**: `#2a5` (green) / `#f0a` (pink for audio)

---

## 6. Audio System

### 6.1 Sound Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Oscillators │────→│  Gain/Pan   │────→│ Master Gain │
│  (FM/AM/    │     │  (stereo)   │     │  (volume)   │
│  Additive)  │     │             │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐     ┌──────┴──────┐
                    │   Reverb    │←────│  Analyser   │
                    │ (Convolver) │     │  (FFT 256)  │
                    └─────────────┘     └─────────────┘
                                               │
                                          ┌────┴────┐
                                          │ Output  │
                                          │(speakers)│
                                          └─────────┘
```

### 6.2 Synthesis Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| **Volume** | 0–100% | 30% | Overall volume |
| **Base Frequency** | 55–880 Hz | 110 Hz | Fundamental tone (A2) |
| **Frequency Scale** | 0.1–3.0× | 1.0× | Base frequency multiplier |
| **Chorus Size** | 1–8 | 3 | Number of voices |
| **Synthesis Type** | FM / AM / Additive / Drone | FM | Generation algorithm |
| **Reverb** | On/Off | On | Spatial effect (2s impulse) |

### 6.3 Synthesis Types

| Type | Algorithm | Timbre |
|------|-----------|--------|
| **FM** | Sine + frequency modulator (0.5× base) | Rich, bell-like |
| **AM** | Sawtooth | Sharp, aggressive |
| **Additive** | Sine/Triangle alternate | Organ-like |
| **Drone** | Pure Sine | Sustained, meditative |

### 6.4 Data → Music Mapping

| Mapping | Data Source | Musical Parameter |
|---------|-------------|-------------------|
| **Entropy** | H_rule → number of voices | Number of oscillators |
| | Δrule × 10 → detune | Pitch deviation |
| **Population** | Population/SIZE² → volume | Master gain amplitude |
| | Rules → pentatonic/minor | Chord structure |
| **Phase** | Phase Ω → scale (pentatonic/minor/chaotic) | Scale |
| | Δrule × 20 → note shift | Pitch modulation |

### 6.5 Musical Scales

| Phase | Scale | Intervals (semitones) |
|-------|-------|----------------------|
| STABLE | Major Pentatonic | 0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24 |
| CYCLIC | Minor | 0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24 |
| CHAOTIC | Chaotic | 0, 1, 3, 4, 6, 7, 9, 10, 12 |
| META | Pentatonic | Same as STABLE |

---

## 7. User Interface

### 7.1 Control Elements

#### Main Panel (Buttons)
| Button | Hotkey | Action |
|--------|--------|--------|
| ⏸ Pause/▶ Start | `Space` | Pause/resume simulation |
| ↺ New Universe | `R` | Generate new initial configuration |
| ⏭ Step | `→` | Single simulation step |
| 🔊 Audio ON/OFF | `A` | Toggle sound on/off |

#### Evolution Parameters (Sliders)
| Parameter | Range | Default | Unit |
|-----------|-------|---------|------|
| Initial Density | 1–100% | 20% | % |
| Mutation Rate | 0–50 | 1 | ‰ (0.1%) |
| Dead Adaptation | 0–100% | 5% | % |
| Live Mutation Strength | 0–10 | 1 | ±1 |
| Grid Size | 40–120 | 80 | cells (step 10) |
| Simulation Speed | 1–10 | 1 | × (steps/frame) |

#### Audio Parameters (Sliders + Selectors)
| Parameter | Range | Default |
|-----------|-------|---------|
| Volume | 0–100% | 30% |
| Base Frequency | 55–880 Hz | 110 Hz (step 5) |
| Frequency Scale | 0.1–3.0× | 1.0× (step 0.1) |
| Chorus Size | 1–8 | 3 |
| Synthesis Type | FM/AM/Additive/Drone | FM |
| Data Mapping | Entropy/Population/Phase | Entropy |

#### Checkboxes
| Parameter | Default | Description |
|-----------|---------|-------------|
| Trail on Phase Space | ✓ | Show full trajectory history |
| Auto-scale Phase Space | ✓ | Dynamic axis scaling |
| Reverb | ✓ | Spatial effect |

### 7.2 Top-5 Rules Table

| Column | Description |
|--------|-------------|
| ID | Rule number (0–255) |
| % | Share in population |
| Fitness | Children/parents ratio (color: green >1, red <1) |
| Children/Parents | Absolute numbers |

---

## 8. Technical Details

### 8.1 Data Structures

```javascript
// Core arrays (TypedArrays for performance)
states:      Uint8Array  // SIZE × SIZE, 0/1
rules:       Uint8Array  // SIZE × SIZE, 0–255
prevRules:   Uint8Array  // Previous rules
deltaRules:  Uint8Array  // |newRule - oldRule|
nextStates:  Uint8Array  // Buffer for next state
nextRules:   Uint8Array  // Buffer for next rule
totalTransition: Uint32Array  // 256 × 256, transition graph

// Metrics
ruleFreq:    Uint32Array  // 256, rule frequency
parentCount: Uint32Array  // 256, parent count
childCount:  Uint32Array  // 256, offspring count
fitnessArr:  Float64Array // 256, fitness
HUE_TABLE:   Float64Array // 256, precomputed hues

// History
omegaHistory: Array<{hRule, avgDeltaRule, omega, omegaClass}>
```

### 8.2 Performance

| Aspect | Implementation |
|--------|----------------|
| **Rendering** | `createImageData` + direct pixel manipulation |
| **Simulation** | Optimized nested loops without function calls |
| **Memory** | Array reuse (double-buffering scheme) |
| **Updates** | Separate: simulation every frame, visualization every 3 generations |
| **FPS Counter** | Update once per second |

### 8.3 Limitations

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| Max Ω History | 200 points | Fixed buffer for graph |
| Max Rules | 256 | 8-bit addressing |
| Max Neighbors | 8 | Moore neighborhood |
| Audio Context | Requires interaction | Browser autoplay policy |

---

## 9. CSS Variables (Design Tokens)

```css
:root {
  --bg: #0a0a0a;        /* Page background */
  --panel: #141414;      /* Panel background */
  --panel2: #1a1a1a;     /* Secondary background */
  --border: #2a2a2a;     /* Borders */
  --text: #e0e0e0;       /* Primary text */
  --muted: #888;          /* Secondary text */
  --accent: #2a5;         /* Primary accent (green) */
  --accent-hov: #3b7;     /* Accent hover */
  --danger: #a33;         /* Danger/reset */
  --danger-hov: #c44;     /* Danger hover */
  --stable: #5f5;         /* STABLE phase */
  --cyclic: #ff5;         /* CYCLIC phase */
  --chaotic: #f55;        /* CHAOTIC phase */
  --meta: #aaf;           /* META phase */
  --audio: #f0a;          /* Audio accent (pink) */
  --font: 'Segoe UI', system-ui, sans-serif;
  --radius: 8px;
  --shadow: 0 2px 8px rgba(0,0,0,0.4);
}
```

---

## 10. Possible Extensions

| Feature | Description | Complexity |
|---------|-------------|------------|
| **Export/Import State** | Save/load configuration | Low |
| **Audio Recording** | Record synthesized sound to file | Medium |
| **3D Visualization** | WebGL rendering of physical space | High |
| **Distributed Simulation** | Web Workers for large grids | Medium |
| **Genetic Algorithm** | Automatic parameter optimization | Medium |
| **Plugin API** | Custom transition rules | Medium |
| **Mobile App** | React Native / PWA | High |

---

This specification describes the complete functionality of the SUBIT v18 application, including architecture, mathematical models, audio system, and user interface.