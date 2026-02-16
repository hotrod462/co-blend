# Finding the One — Detailed Animation Script (v4)

> A 105-second black-and-white Heider-Simmel-inspired animation about a small square journeying through a world of triangles, searching for its perfect match.

---

## Global Parameters

| Parameter           | Value                          |
|---------------------|--------------------------------|
| **Duration**        | 105 seconds (1:45)             |
| **FPS**             | 30                             |
| **Total Frames**    | 3150                           |
| **Resolution**      | 1920 × 1080                    |
| **Color Palette**   | Black, white, and grays only   |
| **Render Engine**   | EEVEE (flat/unlit shading)     |
| **Camera**          | Top-down orthographic, tracking protagonist |

---

## Stage Design — Scrolling World

The animation uses a **fixed-frame scrolling** approach. The Seeker stays roughly centered in frame while the world scrolls past from right to left. The wide 1920×1080 format becomes a road stretching into the future.

```
Frame view (camera fixed on Seeker):

     ← world scrolls this way ←

  △        △                        △
       △        ■ (Seeker)     △
  △                       △            △
           △                    △

  (past)     (protagonist)      (future)
  shapes     stays centered     new shapes
  exit       in frame           appear
  left                          from right
```

### World Specs
- **World space**: The Seeker travels from X≈0 to X≈100+ over 105 seconds
- **Visible frame**: ~20 units wide × ~11 units tall (orthographic scale ~20)
- **No walls, no room, no door** — open black void
- **Floor**: Pure black (background)

### Camera Behavior
- **Type**: Orthographic, top-down
- **Tracking**: Camera X = Seeker X. Camera Y = 0 (fixed).
- **Orthographic scale**: Base ~20, with subtle emotional shifts (18–22)
- **Result**: Seeker centered horizontally, drifts vertically within frame.

### Characters

| Character                | Shape              | Size                  | Fill Color     | Emission | Notes |
|--------------------------|--------------------|-----------------------|----------------|----------|-------|
| **Parent Triangle A**    | Right-angle tri    | ~1.0 leg              | White (0.9)    | 2.0      | Intro only. Large, eye-catching. |
| **Parent Triangle B**    | Right-angle tri    | ~1.0 leg              | White (0.9)    | 2.0      | Intro only. Mirror of Parent A. |
| **Seeker**               | Square             | 0.6 side              | White (1.0)    | 2.0      | Protagonist. Bright. Centered in frame. |
| **Right-Angle Triangle** | Right-angle tri    | ~0.7 leg              | Gray (0.45)    | 0.8      | Mismatch 1. Erratic. Flat side teases. |
| **Isosceles Triangle**   | Isosceles tri      | ~0.7 base, ~0.9 tall  | Gray (0.4)     | 0.8      | Mismatch 2. Rigid. Wide base teases. |
| **The One**              | Square             | 0.6 side              | White (1.0)    | 2.0      | Perfect match. Identical to Seeker. |
| **Background Triangles** | Mixed              | 0.3–0.5               | Dark gray (0.2–0.3) | 0.4 | 6–8 ambient. Fade over time. |

### Visual Hierarchy
- **Seeker & The One**: Emission 2.0, white. Pop against everything.
- **Encounter triangles**: Emission 0.8, mid-gray. Visible but secondary.
- **Background triangles**: Emission 0.4, dark gray. Scenery.
- **Seeker emission fluctuates** with emotional state (see curve below).

---

## Visual Systems

### Corner Trail Lines
The **two left corners** of the Seeker square leave trailing glow lines. Length scales with scroll speed:

| Scroll Speed | Trail Length | Brightness | Feel |
|--------------|-------------|------------|------|
| Near-stop (0.005 u/f) | Dots, ~0.1u | 0.2 | Barely moving |
| Slow (0.015 u/f) | ~0.5u | 0.4 | Contemplative |
| Normal (0.03 u/f) | ~1.0u | 0.6 | Steady journey |
| Fast (0.06 u/f) | ~2.5u | 1.0 | Purposeful |
| Racing (0.10 u/f) | ~4.0u streaks | 1.5 | Exhilarating |

When paired (Act IV), **four** trailing corners (both squares' left edges = rectangle left side).

### Seeker Emission Curve (Emotional Barometer)

```
Emission: 2.0 ── 2.0 ─╲ 1.7 ╱ 1.9 ─╲ 1.4 ── 1.2 ╲ 1.0 ╱ 2.0 ╱ 3.0 → 5.0
                       ↑          ↑              ↑       ↑         ↑
                  1st reject   recover      2nd reject  lowest   The One
```

### Background Triangle Density Curve

```
Density: 0 ╱ 7-8 ╲ 8-10  ╲ 6-7 ╲ 4-5 ╲ 2-3 ╲ 0-1 ╱ 1-2 ╲ 0
        intro  exploring  crowded normal thinning bare  pair  gone
                          ↑                  ↑        ↑
                     after 1st          after 2nd   "gave up"
```

Background triangles don't disappear — they **fade out** (emission 0.4 → 0 over 60–90 frames each). Stars going out, one by one.

### Post-Rejection Y-Drift Range

| Phase | Y Range | Quality |
|-------|---------|---------|
| Pre-encounters | ±2.0 | Wide, curious exploration |
| After 1st rejection | ±1.5 | Slightly guarded |
| After 2nd rejection | ±0.8 | Withdrawing |
| "Almost gave up" | ±0.2 | Flatlined — no curiosity |
| The One appears | ±0.5 → ±1.0 | Reopening |
| Paired | ±0.3 | Gentle, chosen sway (warm, not defeated) |

### Scroll Speed as Emotion

| Speed | Meaning |
|-------|---------|
| 0.03 u/f (normal) | Calm journey |
| 0.01–0.02 u/f | Encounter — world slows |
| 0.005 u/f | Critical moment — time stops |
| 0.04–0.10 u/f | Paired momentum — world flies past |

### Orthographic Scale Shifts

| Moment | Scale | Effect |
|--------|-------|--------|
| Normal | 20 | Standard view |
| During encounters | 18 | Slightly zoomed in — focused |
| "Almost gave up" | 22 | Zoomed out — Seeker feels small |
| The Click | 16 | Tight zoom — intimate |
| Final acceleration | 24 | Wide — world expanding |

---

## ⚠️ Continuity Rules

> **CRITICAL**: Every shape's position must be continuous. No teleporting.
> All world-space positions must account for camera scroll.

---

## Prologue — The Birth (Frames 1–330, 0s–11s)

### Purpose
**The hook.** Two large, bright right-angle triangles are spinning from frame 1 — immediate motion to stop social media scrolling. They spiral together, their hypotenuses align to form a square, and from that union the Seeker is born.

### Geometric Poetry
- **Opening**: △ + △ = ■ (birth)
- **Ending**: ■ + ■ = ▬ (union)

### Beat P.1: Immediate Motion (Frames 1–30, 0s–1s)

Two large right-angle triangles are ALREADY orbiting when the animation begins. No fade-in, no title card. Motion from frame 1.

| Frame Range | Action | Notes |
|-------------|--------|-------|
| 1–30 | Two right-angle triangles orbiting each other at radius ~2.0, center of screen | Large (~1.0 leg), bright white, emission 2.0+. Against pure black, pops on any feed. |

Speed: ~1 revolution per 60 frames (moderate). Large, visible, hypnotic.

### Beat P.2: Spiral Inward (Frames 30–90, 1s–3s)

| Frame Range | Action | Notes |
|-------------|--------|-------|
| 30–60 | Orbit tightens: radius 2.0 → 1.0. Speed increases. | Gravitational pull feeling |
| 60–90 | Radius 1.0 → 0.5. Faster spin. | "What happens when they meet?" |

### Beat P.3: The Alignment (Frames 90–130, 3s–4.3s)

| Frame Range | Action | Notes |
|-------------|--------|-------|
| 90–110 | Spin slows. Triangles rotate so hypotenuses face each other. | Deliberate alignment |
| 110–125 | Gap shrinks: 0.5 → 0.2 → 0.05. Slide together. | Building tension |
| 125–130 | Hypotenuses meet flush. **CLICK.** They form a perfect rectangle. | Satisfying snap. The audience learns: shapes can combine. |

### Beat P.4: The Birth (Frames 130–200, 4.3s–6.7s)

| Frame Range | Action | Notes |
|-------------|--------|-------|
| 130–160 | Combined shape pulses: emission 2.0 → 4.0 → 2.0. Whole screen breathes. | Life force |
| 160–185 | A smaller square separates from the center. Parent dims (2.0 → 0.8), child brightens (0 → 2.0). | Cell-dividing visual. The Seeker is BORN. |
| 185–200 | Seeker fully separated, ~60% parent size. Parent holds. | Two distinct shapes now. |

### Beat P.5: Departure (Frames 200–330, 6.7s–11s)

| Frame Range | Action | Notes |
|-------------|--------|-------|
| 200–240 | Parent rectangle drifts left and off-screen (into the past). | Establishes scroll direction. |
| 240–270 | Seeker alone in frame. Holds still. Its pulse begins — the heartbeat. | The journey hasn't started yet. |
| 270–300 | First background triangles appear dimly from the right. | The world exists. |
| 300–330 | World scroll begins (0 → 0.03 u/f). Seeker centered. Journey starts. | Transition into Act I. |

---

## Act I — The Journey Begins (Frames 330–990, 11s–33s)

### Beat 1.1: First Steps (Frames 330–450, 11s–15s)

| Frame Range | Seeker (screen-relative) | Scroll | Notes |
|-------------|--------------------------|--------|-------|
| 330–370 | Y: 0 → 0.5, gentle upward drift | 0.03 u/f (settling) | Looking around. Background triangles flowing past. |
| 370–420 | Y: 0.5 → -0.3 → 0.2 (wander) | 0.03 u/f | Establishing the rhythm. Corner trails visible — medium length (~1.0u). |
| 420–450 | Y: 0.2 → 0 (centers) | 0.03 u/f | Settled into the journey. |

Pulse: 45-frame cycle, amplitude 0.03. Steady heartbeat.

### Beat 1.2: Wandering the Landscape (Frames 450–630, 15s–21s)

Wide Y-drift (±2.0) showing curiosity and exploration. Background triangles at full density (7–8 visible).

| Frame Range | Y Movement | Notes |
|-------------|------------|-------|
| 450–500 | Y: 0 → 1.5 | Drifting upward, exploring |
| 500–540 | Y: 1.5 → -0.5 | Direction change, aimless |
| 540–570 | Y: -0.5 → -1.5 | Passes near a background triangle — no interaction |
| 570–600 | Y: -1.5 → 0.5 | Wandering through the landscape |
| 600–630 | Y: 0.5 → 0 | Settling toward center |

**Background Pairing #1** (frames ~480–570): Two small dim equilateral triangles (~Y: 2.5, mid-ground) approach each other, do a brief awkward orbit (~80 frames), bonk, drift apart. The Seeker passes by. Audience sees: "everyone is trying to connect. It's hard."

### Beat 1.3: Right-Angle Triangle Encounter (Frames 630–870, 21s–29s)

A right-angle triangle enters from the right — brighter and larger than background shapes. Erratic, fast. Its flat leg side briefly teases compatibility.

**Scroll slows during encounters** (0.03 → 0.01 u/f). Corner trails shorten.

| Frame Range | Triangle (screen-rel) | Seeker Y | Scroll | Notes |
|-------------|----------------------|----------|--------|-------|
| 630–680 | Enters from (+12, 1.5), zigzags toward center | Y≈0, interest (pulse quickens) | → 0.02 | 3–4 direction changes. Clearly brighter than background. |
| 680–720 | Reaches (~2, 0.5), tight chaotic orbit around Seeker | Y≈0, watching | 0.01 | Too fast, too tight |
| 720–750 | Flat leg faces Seeker's side — approaches to 0.2 gap | Seeker leans right (+0.2) | 0.01 | **THE TEASE** — hold ~10 frames. Ortho scale → 18. |
| 750–780 | Hypotenuse rotates into contact — BONK. Bounces, spins. | Recoils: Y → 1.0 | 0.01 | Geometry fails. |
| 780–820 | Follows erratically, overshoots | Y → 1.5 | 0.015 | Too aggressive |
| 820–850 | Stops keeping up. Falls behind in frame (scroll carries it left). | Y≈1.5, watching | → 0.02 | The Seeker moves on; triangle left behind in the past. |
| 850–870 | Off-screen left | Sigh: scale 1.0 → 0.92 → 1.0 | → 0.03 | Deflation. Ortho scale → 20. |

**Seeker emission**: 2.0 → dips to 1.7 after encounter.
**Y-drift range contracts**: ±2.0 → ±1.5

### Beat 1.4: Recovery (Frames 870–990, 29s–33s)

| Frame Range | Seeker Y | Scroll | Notes |
|-------------|----------|--------|-------|
| 870–910 | Y: 1.5 → 1.2 | 0.03 | Processing. Emission recovering: 1.7 → 1.9 |
| 910–950 | Y: 1.2 → 0.5 | 0.03 | Drifting back toward center |
| 950–990 | Y: 0.5 → 0 | 0.03 | Re-centered. Searching again. |

**🔮 Foreshadowing Near-Miss** (frames ~900–990): A bright square (emission 2.0, same as Seeker) drifts through the TOP-RIGHT corner of frame (Y ≈ 3.5–4.0), ~3–4 seconds visible. The Seeker is at Y ≈ 1.0, drifting downward — processing rejection, not looking up. They pass each other. On rewatch: "The One was RIGHT THERE."

---

## Act II — False Hopes (Frames 990–1650, 33s–55s)

### Beat 2.1: Isosceles Triangle Entrance (Frames 990–1110, 33s–37s)

Isosceles enters from upper-right. Rigid, mechanical. Wide base is almost the width of the Seeker's side — audience curiosity: "maybe THIS one fits?"

| Frame Range | Triangle (screen-rel) | Scroll | Notes |
|-------------|----------------------|--------|-------|
| 990–1030 | Enters (+12, 3), straight downward glide to (+6, 1.5) | → 0.02 | Mechanical precision. Brighter than background. |
| 1030–1070 | (+6, 1.5) → (+3, 0.5), 90° turn | 0.015 | Rigid. No curves. |
| 1070–1110 | (+3, 0.5) → (+1.5, 0.2), speed steps down | 0.01 | Approaches. Ortho scale → 18. |

### Beat 2.2: Stiff Interaction (Frames 1110–1350, 37s–45s)

**Background Pairing #2** (frames ~1140–1230): In the far background (Y ≈ -3), scalene + equilateral triangles circle briefly and fail. Doubles the sense of "connection is hard."

| Frame Range | Triangle Action | Seeker Y | Notes |
|-------------|-----------------|----------|-------|
| 1110–1170 | Angular orbit at radius 1.5, straight segments + 90° turns | Tries to track, speeding up | Angular — not smooth |
| 1170–1210 | Orbit tightens to 1.0, still angular | Overshoots, doubles back | Out-of-sync |
| 1210–1260 | Wide base faces Seeker's side — 0.15 gap | Y holds still, pulse quickens | **THE STRONGER TEASE** — 50 frames! Almost matches! |
| 1260–1290 | Rotation reveals taper — flush breaks. Soft bump. | Wobbles, recoils | Close but wrong. Taper ruins it. |
| 1290–1320 | Resumes rigid orbit, unchanged | Drifts: Y → -1 | Doesn't care. |
| 1320–1350 | Continues mechanical orbit | Y ≈ -1, deflating | Giving up. |

**Scroll**: Nearly stopped (0.005 u/f) during interaction. Corner trails: dots.

### Beat 2.3: Sad Separation (Frames 1350–1500, 45s–50s)

The Seeker resumes forward movement. Triangle doesn't pursue — left behind.

| Frame Range | Triangle | Seeker | Scroll | Notes |
|-------------|----------|--------|--------|-------|
| 1350–1390 | Falls behind in frame (scroll carries it left) | Y ≈ -1, pulse slows | → 0.015 | Moving on. |
| 1390–1430 | Drifts to left edge | Y: -1 → -1.5 | 0.02 | Being left in the past. |
| 1430–1470 | Exits left | Y ≈ -1.5 | 0.025 | Gone. |
| 1470–1500 | Off-screen | Y ≈ -1.5, lonely | 0.025 | Just background shapes again. |

**Seeker emission**: drops to 1.4.
**Y-drift range contracts**: ±1.5 → ±0.8
**Background triangles**: starting to thin — 4–5 visible, some fading out.

### Beat 2.4: Alone Again (Frames 1500–1650, 50s–55s)

| Frame Range | Seeker Y | Scroll | Notes |
|-------------|----------|--------|-------|
| 1500–1540 | Y: -1.5, sigh (scale 0.92) | 0.025 | Deeper sadness. Emission → 1.2. |
| 1540–1580 | Y: -1.5 → -2.0 (sinking) | 0.02 | Losing momentum. BG triangles: 2–3, dimming. |
| 1580–1620 | Y: -2.0 → -1.5 (slight recovery) | 0.02 | Still going, barely. |
| 1620–1650 | Y: -1.5 → -0.5 | 0.02 | One more try... scroll still slow. |

Background triangles sparser — fewer spawning. World feels emptier.

---

## The Valley — "Almost Gave Up" (Frames 1650–1800, 55s–60s)

**The emotional hinge.** 5 seconds of genuine darkness before the turn.

### Frames 1650–1690 (first 1.3s)
- Y-drift flatlined: ±0.2
- Scroll: 0.012 u/f, decelerating
- Emission: 1.2, still dimming
- Background: 1 triangle visible, fading
- Pulse: period 60, amplitude 0.02 (weak)
- Corner trails: barely visible dots

### Frames 1690–1740 (middle)
- Scroll: 0.008 u/f — crawling
- Emission: **1.0** — almost as dim as an encounter triangle
- Background: last triangle faded. **Pure black void.**
- Pulse: period 70, amplitude 0.015 — heartbeat dying?
- Corner trails: gone
- **Ortho scale: 22** — Seeker feels tiny in the void
- The screen is almost pure black with one dim square in the center.

### Frame 1740 — THE TURN
- Extreme right edge: a tiny, faint glow. Almost imperceptible.
- Just a few pixels of light. Could be nothing.

### Frames 1740–1770
- Glow gets slightly brighter, closer. Definitely there.
- Seeker's pulse **skips** — tiny extra beat (amplitude briefly 0.04). Something registered.
- Emission: 1.0 → 1.1. Barely.
- Scroll: 0.008 → 0.010.

### Frames 1770–1800
- The glow is clearly a shape. A **SQUARE** shape. Bright. White. Emission 2.0.
- Seeker emission: 1.1 → 1.5 → 1.8
- Scroll: 0.010 → 0.015 → 0.020
- Pulse quickens: period 70 → 50 → 45
- Corner trails reappear — short but growing
- **Transition into Act III**

---

## Act III — Discovery (Frames 1800–2460, 60s–82s)

### Beat 3.1: The One Appears Ahead (Frames 1800–1950, 60s–65s)

A second square, directly ahead on the Seeker's path. Bright white. Not a triangle. The thematic payoff of the scrolling format: The One was always out there ahead. The Seeker just had to keep going.

| Frame Range | The One (screen-rel) | Seeker | Scroll | Notes |
|-------------|---------------------|--------|--------|-------|
| 1800–1850 | (+8, 0.5), closing | Y: -0.5 → 0, pulse quickens | 0.025 | A bright square! Not a triangle! |
| 1850–1880 | (+5, 0.3) | Y: 0 → 0.3 | 0.025 | Noticing each other. |
| 1880–1910 | (+3, 0.2) | Y: 0.3 → 0.2, aligning | 0.02 | Approaching cautiously. |
| 1910–1950 | (+1.5, 0.1) | Y: 0.1, nearly aligned | 0.01 | **THE PAUSE.** Both nearly still. |

Seeker emission: 1.8 → 2.0 (back to full brightness).
The One's pulse: same frequency, same amplitude — already in sync.

### Beat 3.2: Mutual Recognition (Frames 1950–2040, 65s–68s)

| Frame Range | The One (screen-rel) | Seeker | Scroll | Notes |
|-------------|---------------------|--------|--------|-------|
| 1950–1980 | (+1.2, 0.1) holds | Y: 0.1 holds | 0.005 | Frozen. 30 frames stillness. World holds breath. |
| 1980–1995 | (+1.0, 0.05) | Y: 0.1 → 0.05 | 0.005 | Tentative approach |
| 1995–2020 | (+0.6, 0) | Y: 0 | 0.005 | Meeting at midpoint |
| 2020–2040 | (+0.4, 0), gap=0.6 | Y: 0 | 0.005 | Close, not touching. Pulse in perfect sync. |

**Ortho scale → 16** (tight, intimate zoom).

### Beat 3.3: First Orbit (Frames 2040–2250, 68s–75s)

Scroll near-stopped. Smooth circular orbiting — direct contrast with triangles' angular orbits.

| Frame Range | Speed | Radius | Notes |
|-------------|-------|--------|-------|
| 2040–2110 | 0.4 RPM | 0.8 | Gentle, testing. SMOOTH circle. |
| 2110–2160 | 0.8 RPM | 0.7 | Growing comfort |
| 2160–2200 | 1.5 RPM | 0.5 | Joyful! |
| 2200–2250 | 2.5 RPM | 0.4 | Exuberant! |

Both pulsing in sync. Orbit center slowly drifts toward screen center.

### Beat 3.4: Side Alignment — "The Click" (Frames 2250–2460, 75s–82s)

The payoff. Flat sides align flush. Two squares become one rectangle.

| Frame Range | Movement | Notes |
|-------------|----------|-------|
| 2250–2300 | Decelerate to 0.8 RPM, radius 0.4 → 0.3 | Winding down |
| 2300–2350 | 0.3 RPM, radius 0.3 → 0.15 | Almost still |
| 2350–2390 | Final quarter-turn — flat sides face each other | Aligning. Ortho scale → 16. |
| 2390–2420 | Slide together, gap 0.3 → 0.02 | **THE CLICK.** Flush. No gaps. No bonking. |
| 2420–2440 | Hold. Perfectly flush. Combined rectangle. | Let the audience feel it. One slow rotation echoing the intro. |
| 2440–2460 | Pulse intensifies: 1.0 → 1.06 → 1.0 | Shared heartbeat. |

```
Attempt 1 — Right-Angle Triangle:
  ┌──┐ ◁       Flat leg teases → hypotenuse bonks → gap
  │  │  \
  └──┘   \
         ──

Attempt 2 — Isosceles Triangle:
  ┌──┐  △      Wide base teases → taper breaks → gap
  │  │ / \
  └──┘/   \
     ──────

The One — Square:
  ┌──┐┌──┐     Flat side meets flat side.
  │  ││  │     Perfect flush → Rectangle.
  └──┘└──┘     CLICK. ❤️
```

**Echo of the intro**: The combined rectangle briefly does one slow rotation (frames 2420–2440), recalling the parent shapes from the prologue. The audience subconsciously recognizes the structural mirror.

---

## Act IV — Union (Frames 2460–3150, 82s–105s)

### Beat 4.1: Huddle (Frames 2460–2670, 82s–89s)

| Frame Range | Movement | Scroll | Notes |
|-------------|----------|--------|-------|
| 2460–2500 | Flush contact (0.0 gap). One shape. | 0.02 (resuming) | Combined rectangle. |
| 2500–2580 | Gentle sway: Y ±0.3 in sync | 0.025 | Rocking together. Moving as one. |
| 2580–2670 | Sway continues, scroll accelerates | 0.03 | Traveling together. Not alone anymore. |

Pulse: 1.0 → 1.08, period 40. Exactly synced.
Emission: 2.0 → 3.0. Brightest things in the world.
Corner trails: now **four** lines (both squares' left corners). Growing.

### Beat 4.2: Accelerating Together (Frames 2670–2940, 89s–98s)

| Frame Range | Scroll Speed | Notes |
|-------------|--------------|-------|
| 2670–2760 | 0.04 u/f | Faster than Seeker ever traveled alone |
| 2760–2850 | 0.06 u/f | Background triangles streaming past |
| 2850–2900 | 0.08 u/f | World is a blur |
| 2900–2940 | 0.10 u/f | Racing forward together. Four long trail streaks. |

**Trail effect**: Faint trail squares spawn behind every 10 frames, fading over 40 frames. Two parallel trails curve to suggest a heart shape.
**Ortho scale → 24** (wide, world expanding).

### Beat 4.3: Into the Light (Frames 2940–3150, 98s–105s)

| Frame Range | Visual | Scroll | Notes |
|-------------|--------|--------|-------|
| 2940–3010 | Pair's glow expands: emission 3.0 → 5.0 | 0.10 | Glow bleeds beyond shapes |
| 3010–3060 | Glow fills ~30% screen. BG triangles fading to 0. | 0.08 | World dissolving |
| 3060–3100 | Glow fills ~60%. Background gone. | 0.05 | Just the pair and light |
| 3100–3130 | White fills screen | 0.03 | Pure white |
| 3130–3150 | White fades to black | 0 | End. |

---

## Animation Principles Reference

### Contrast Table

| Property | Right-Angle Tri | Isosceles Tri | The One |
|----------|-----------------|---------------|---------|
| Shape | Right-angle triangle | Isosceles triangle | Square (matches Seeker) |
| Entry | From right (ahead) | From upper-right | From right (the future) |
| Speed | 5× Seeker | Same as Seeker | Same as Seeker |
| Movement | Erratic, zigzag | Rigid, straight lines | Smooth, curved |
| Approach | Aggressive | Indifferent | Tentative, mutual |
| Response | Ignores recoil | Ignores bump | Mirrors perfectly |
| Pulse | 2× frequency | None | Same freq, same phase |
| "Fit" | Flat leg → hypotenuse bonks | Wide base → taper fails | Flat → flat → **flush** |
| Tension | Low (wrong energy) | High (almost fits!) | Resolution (it fits!) |
| Exit | Left behind by scroll | Left behind, doesn't pursue | Leaves together, accelerating |
| Emission | 0.8 | 0.8 | 2.0 (matches Seeker) |

---

## Technical Notes

### Camera
- **Type**: Orthographic, top-down
- **Position**: (Seeker.world_X, 0, 10)
- **Ortho scale**: Animated 16–24 for emotional moments
- **Implementation**: Animate camera X to match Seeker X each frame

### World Coordinate System
- Seeker starts at world X≈0, moves rightward
- ~100 units traversed over 105 seconds
- Background triangles pre-placed along path (~50 scattered)
- Anything outside Seeker.X ± 10 is off-screen

### Background Triangle Implementation
- Pre-place ~50 triangles across the world path
- Each gets slow drift + rotation
- Fade-out: animate emission strength to 0 based on density curve schedule
- Only ~6–8 visible at any moment

### Materials
- All **Emission** shaders (no lighting)
- Seeker emission animated for emotional barometer
- Trail lines: thin planes with emission, length scaled per frame

### Easing
- Seeker: ease-in-out-cubic (deliberate)
- Right-angle tri: linear / ease-out-bounce (jarring)
- Isosceles tri: linear (mechanical)
- The One: ease-in-out-cubic (matches Seeker)
- Scroll speed changes: ease-in-out (smooth)
- Background: linear (ambient)

### Corner Trail Implementation
- Two thin glowing planes anchored to Seeker's left corners
- Scale X = trail length (proportional to scroll speed)
- Gradient material: bright at anchor, transparent at tail
- When paired: four planes (rectangle's four left-edge corners)
