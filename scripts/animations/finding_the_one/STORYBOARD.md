# Finding the One — Detailed Animation Script

> A 60-second black-and-white Heider-Simmel-inspired animation about a small circle searching for its perfect match.

---

## Global Parameters

| Parameter           | Value                          |
|---------------------|--------------------------------|
| **Duration**        | 60 seconds                     |
| **FPS**             | 30                             |
| **Total Frames**    | 1800                           |
| **Resolution**      | 1920 × 1080                    |
| **Color Palette**   | Black, white, and grays only   |
| **Render Engine**   | EEVEE (flat/unlit shading)     |
| **Camera**          | Top-down orthographic          |

---

## Stage Design

The scene is viewed from directly above (bird's-eye / top-down orthographic camera). The "room" is a simple rectangular space defined by faint gray boundary lines on a black background.

```
┌─────────────────────────────────────────────────┐
│                                                 │
│                                                 │
│                                                 │
│                  (room interior)                │
│                                                 │
│                                                 │
│                                                 │
│          ┌──┐                                   │
└──────────┘  └───────────────────────────────────┘
           door
```

### Room Specs
- **Room bounds**: roughly -8 to +8 on X, -4.5 to +4.5 on Y
- **Wall**: faint gray lines (material: emission gray ~0.25), thickness ~0.05
- **Door opening**: bottom-left wall, ~2 units wide gap
- **Floor**: pure black (background)

### Characters

| Character         | Shape     | Size (radius/half-width) | Fill Color  | Notes |
|-------------------|-----------|--------------------------|-------------|-------|
| **Seeker**        | Circle    | 0.35                     | White (1.0) | The protagonist. Soft glow. |
| **Square**        | Square    | 0.6 side                 | Gray (0.5)  | Jittery, erratic energy. |
| **Rectangle**     | Rectangle | 0.8 × 0.4               | Gray (0.4)  | Stiff, mechanical movement. |
| **The One**       | Circle    | 0.35                     | White (1.0) | Identical to Seeker. Soft glow. |

All characters are flat 2D shapes (thin 3D meshes viewed from above), with soft emission materials to give a subtle glow against the black background.

---

## Act I — Searching (Frames 1–450, 0s–15s)

### Beat 1.1: Entrance (Frames 1–90, 0s–3s)

**Action**: The Seeker circle enters hesitantly through the door from offscreen-left.

| Frame Range | Seeker Position (X, Y) | Movement Quality | Notes |
|-------------|------------------------|------------------|-------|
| 1–30        | (-10, -3) → (-6, -3)  | Slow drift rightward | Entering through door opening |
| 30–45       | (-6, -3) → (-5, -2)   | Pause, slight upward drift | Looking around — "hesitation" |
| 45–60       | (-5, -2)               | Hold position, gentle pulse (scale 1.0 → 1.05 → 1.0) | Breathing / awareness |
| 60–90       | (-5, -2) → (-1, 0)    | Ease-in-out drift to center | Moving into the room |

**Pulse animation**: Throughout the entire animation, the Seeker has a subtle continuous "heartbeat" pulse — scaling between 1.0 and 1.03 on a ~1.5 second cycle (45 frames). This is gentle enough to be subconscious.

### Beat 1.2: Wandering (Frames 90–180, 3s–6s)

**Action**: The Seeker slowly wanders the center of the room, looking "lost."

| Frame Range | Movement | Notes |
|-------------|----------|-------|
| 90–120      | Drift from (-1, 0) → (1, 1) | Slow, meandering path |
| 120–150     | Drift from (1, 1) → (0.5, -0.5) | Change direction, still aimless |
| 150–180     | Drift from (0.5, -0.5) → (0, 0) | Settle near center |

**Path quality**: Use perlin-noise-like wandering — not a straight line but a wobbly, uncertain path. Speed should be slow (~0.03 units/frame).

### Beat 1.3: Square Encounter (Frames 180–360, 6s–12s)

**Action**: The Square bounces in from the right side, interacts clumsily with the Seeker.

| Frame Range | Square Action | Seeker Reaction | Notes |
|-------------|---------------|-----------------|-------|
| 180–210     | Square enters from (10, 2), bouncing erratically toward center | Seeker holds at (0, 0) | Square moves in sharp zigzags — 2–3 direction changes, fast |
| 210–240     | Square reaches (1.5, 0.5), circles Seeker abruptly at tight radius (~1.0) | Seeker stays still, slight recoil (shift -0.3 away from Square) | Square orbits too fast — 1 full circle in 30 frames (180°/15fr) |
| 240–270     | Square nudges into Seeker (approaches to 0.3 gap, bounces off) | Seeker recoils: quick jump to (-1.5, -0.5) | The "nudge" — Square moves to (0.3, 0), Seeker flinches away |
| 270–310     | Square follows erratically, overshoots past Seeker | Seeker backs away further to (-2.5, -1) | Mismatch energy — Square is too aggressive |
| 310–340     | Square pauses confused at (-0.5, 0), then exits right: (-0.5, 0) → (10, 1) | Seeker watches from (-2.5, -1) | Square gives up, leaves |
| 340–360     | (Square offscreen) | Seeker "sighs": scale 1.0 → 0.92 → 1.0 over 20 frames | Deflation = sadness |

**Square movement style**:
- Sharp direction changes (not smooth easing — use linear or ease-out-bounce)
- Speed: 0.15–0.25 units/frame (much faster than Seeker)
- Rotation: Square should rotate jerkily as it moves (±15° random wobble per 5 frames)

**Mismatch indicators**:
- Speed differential (Square 4× faster than Seeker)
- Distance mismatch (Square gets too close too fast)
- Rhythm mismatch (Square's pulse, if any, is 2× the frequency of Seeker's)

### Beat 1.4: Recovery (Frames 360–450, 12s–15s)

**Action**: Seeker sighs and resumes wandering.

| Frame Range | Seeker Action | Notes |
|-------------|---------------|-------|
| 360–390     | Stay at (-2.5, -1), slow pulse continues | Processing the encounter |
| 390–420     | Drift back toward center: (-2.5, -1) → (-1, 0.5) | Reluctant re-engagement |
| 420–450     | Gentle wander: (-1, 0.5) → (0.5, 0) | Back to searching |

---

## Act II — False Hopes (Frames 450–900, 15s–30s)

### Beat 2.1: Rectangle Entrance (Frames 450–540, 15s–18s)

**Action**: The Rectangle glides in smoothly but stiffly from the top of the room.

| Frame Range | Rectangle Position | Movement Quality | Notes |
|-------------|-------------------|------------------|-------|
| 450–480     | (3, 6) → (3, 3)  | Perfectly straight downward glide, constant speed | Mechanical precision |
| 480–510     | (3, 3) → (2, 1.5) | 90° turn, then straight horizontal+diagonal | Rigid, no curves |
| 510–540     | (2, 1.5) → (1.2, 0.5) | Approaches Seeker's area, slows | Never decelerates smoothly — steps down in speed |

**Rectangle movement style**:
- Always in straight lines with sharp corner turns
- No rotation (or perfectly aligned rotation — turns exactly 90° when changing direction)
- Speed: constant 0.1 units/frame, steps down to 0.05 when "approaching"
- No pulse animation (it doesn't "breathe")

### Beat 2.2: Stiff Orbit (Frames 540–690, 18s–23s)

**Action**: Rectangle attempts to orbit the Seeker, but rigidly. Seeker tries to match.

| Frame Range | Rectangle Action | Seeker Reaction | Notes |
|-------------|------------------|-----------------|-------|
| 540–600     | Begins orbiting Seeker at radius 1.5, but in a square-shaped orbit path (straight segments with 90° corners) | Seeker tries to rotate to "face" Rectangle, speeding up to track it | Rectangle orbit: 4 straight segments, 90° turn each |
| 600–630     | Orbit shifts closer to radius 1.0, still square-shaped path | Seeker speeds up, overshoots, doubles back | Out-of-sync — Seeker arrives at where Rectangle WAS |
| 630–660     | Rectangle and Seeker collide softly (gap shrinks to 0.1, bump) | Both shift apart — Rectangle barely reacts, Seeker wobbles | The "clumsy bump" |
| 660–690     | Rectangle resumes rigid orbit, unchanged | Seeker slows down, drifts away from orbit path to (-1, -1) | Seeker gives up trying to match |

**Mismatch indicators**:
- Rectangle's path is angular; Seeker's natural movement is curved
- Rectangle maintains constant speed regardless of Seeker's position
- No synchronization of "breathing" — Rectangle has no pulse
- The bump causes no change in Rectangle's behavior (it doesn't care)

### Beat 2.3: Sad Separation (Frames 690–810, 23s–27s)

**Action**: Seeker drifts away sadly. Rectangle lingers but doesn't pursue.

| Frame Range | Rectangle Action | Seeker Action | Notes |
|-------------|------------------|---------------|-------|
| 690–720     | Continues orbiting at reduced speed, doesn't follow Seeker | Seeker drifts to (-2, -1.5), pulse slows slightly | Emotional distance |
| 720–750     | Rectangle stops orbiting, holds position at (1.5, 0) | Seeker at (-2.5, -2), minimal movement | Stillness = loneliness |
| 750–780     | Rectangle begins exit: (1.5, 0) → (3, 2) (straight line) | Seeker watches (no movement) | Rectangle leaves without looking back |
| 780–810     | Rectangle exits: (3, 2) → (3, 6) → offscreen | Seeker alone | No pursuit = it wasn't meant to be |

### Beat 2.4: Alone Again (Frames 810–900, 27s–30s)

| Frame Range | Seeker Action | Notes |
|-------------|---------------|-------|
| 810–840     | Hold at (-2.5, -2), slow pulse, slight "sigh" deflation (scale 0.94) | Deeper sadness than after Square |
| 840–870     | Very slow drift toward door area: (-2.5, -2) → (-3, -2.5) | Considering leaving? |
| 870–900     | Stops near (-3, -2), turns slightly back toward center | One more look... |

---

## Act III — Discovery (Frames 900–1350, 30s–45s)

### Beat 3.1: The One Enters (Frames 900–990, 30s–33s)

**Action**: A second small circle enters softly through the door, mirroring the Seeker's original entrance path.

| Frame Range | The One Position | Seeker Position | Notes |
|-------------|------------------|-----------------|-------|
| 900–930     | (-10, -3) → (-6, -3) | (-3, -2) holds still | SAME entrance path as Seeker used in Beat 1.1 |
| 930–950     | (-6, -3) → (-5, -2) | (-3, -2) holds, pulse quickens slightly | Same hesitation pattern! |
| 950–970     | (-5, -2) → (-4, -1.5) | (-3, -2) → (-3.2, -1.8) slight drift toward The One | Noticing each other |
| 970–990     | (-4, -1.5) — holds | (-3.2, -1.8) — holds | THE PAUSE. Both stop. "Seeing" each other. |

**Critical detail**: The One's entrance MIRRORS the Seeker's Act I entrance (same path, same hesitation timing). Audience should subconsciously recognize the parallel.

**The One's pulse**: Same frequency and amplitude as the Seeker's — 1.0 → 1.03 on a 45-frame cycle. They should already be roughly in sync from the start.

### Beat 3.2: Mutual Recognition (Frames 990–1050, 33s–35s)

**Action**: The moment of recognition. Both pause, "face" each other, then begin tentative approach.

| Frame Range | The One | Seeker | Notes |
|-------------|---------|--------|-------|
| 990–1010    | Hold at (-4, -1.5) | Hold at (-3.2, -1.8) | Frozen pause — no movement at all for 20 frames |
| 1010–1020   | Very slight drift: (-4, -1.5) → (-3.8, -1.6) | Very slight drift: (-3.2, -1.8) → (-3.4, -1.7) | Tentative approach — 0.02 units/frame |
| 1020–1035   | (-3.8, -1.6) → (-3.5, -1.5) | (-3.4, -1.7) → (-3.5, -1.5) | Coming together — meeting at midpoint |
| 1035–1050   | Hold at (-3.5, -1.5), gap = 0.8 units | Hold at (-3.5, -1.5), gap = 0.8  | Close but not touching. Gentle pulse in sync. |

**Pulse synchronization**: By frame 1020, both circles should be pulsing in PERFECT sync — same phase, same amplitude. This is the first major visual marker of compatibility.

### Beat 3.3: First Orbit (Frames 1050–1200, 35s–40s)

**Action**: Slow, synchronized orbiting — starts gentle, builds to joyful spins.

| Frame Range | Movement | Speed | Orbit Radius | Notes |
|-------------|----------|-------|--------------|-------|
| 1050–1110   | Begin slow circular orbit around their shared center point | 0.5 RPM (1 revolution per 120 frames) | 0.8 units | Gentle, testing |
| 1110–1140   | Speed increases | 1.0 RPM (1 rev per 60 frames) | 0.7 units | Growing comfort, tightening orbit |
| 1140–1170   | Speed increases more | 2.0 RPM (1 rev per 30 frames) | 0.5 units | Joyful — spinning faster |
| 1170–1200   | Rapid, joyful spinning | 3.0 RPM (1 rev per 20 frames) | 0.4 units | Exuberant! |

**Orbit quality**:
- SMOOTH circular path (contrast with Square's zigzags and Rectangle's angular orbit)
- Both circles always equidistant from center — perfect symmetry
- Both pulsing in sync throughout
- Orbit is centered, gradually drifting toward room center as they spin

### Beat 3.4: Nose-to-Nose (Frames 1200–1350, 40s–45s)

**Action**: They slow down and come to a stop, perfectly aligned, "nose to nose."

| Frame Range | Movement | Notes |
|-------------|----------|-------|
| 1200–1230   | Decelerate from 3.0 RPM to 1.0 RPM, radius shrinks 0.4 → 0.3 | Winding down from joy |
| 1230–1260   | Decelerate to 0.3 RPM, radius 0.3 → 0.15 | Almost still |
| 1260–1290   | Final quarter-turn to perfect horizontal alignment | Side by side |
| 1290–1320   | Hold position, gap = 0.1 units | "Nose to nose" — closest they've been |
| 1320–1350   | Synchronized pulse intensifies: 1.0 → 1.06 → 1.0 | Shared heartbeat growing stronger |

---

## Act IV — Union (Frames 1350–1800, 45s–60s)

### Beat 4.1: Huddle (Frames 1350–1500, 45s–50s)

**Action**: The pair huddles closely, pulsing in unison, swaying gently.

| Frame Range | Movement | Notes |
|-------------|----------|-------|
| 1350–1380   | Gap closes from 0.1 to 0.05 | Almost touching |
| 1380–1440   | Gentle shared sway: both drift left 0.3, right 0.3, left 0.3 units in sync | Rocking together |
| 1440–1500   | Sway continues, pair slowly drifts toward door: center → (-2, -1) | Beginning to leave together |

**Pulse**: Now a strong shared heartbeat — 1.0 → 1.08 → 1.0 on a 40-frame cycle. Both EXACTLY in sync.

**Glow**: Both circles subtly brighten — emission strength increases from 1.0 to 1.5 over this section.

### Beat 4.2: Exit Together (Frames 1500–1650, 50s–55s)

**Action**: The pair glides toward the door and exits together, side by side.

| Frame Range | Pair Position (center) | Movement | Notes |
|-------------|----------------------|----------|-------|
| 1500–1530   | (-2, -1) → (-3.5, -1.5) | Smooth drift toward door | Still pulsing together |
| 1530–1560   | (-3.5, -1.5) → (-5, -2.5) | Approaching door opening | Side by side, gap = 0.05 |
| 1560–1590   | (-5, -2.5) → (-7, -3) | Through the door | Exiting! |
| 1590–1650   | (-7, -3) → (-12, -3) | Offscreen left | Gone together |

**Trail effect**: As they exit (frames 1530+), leave a faint trail behind them — ghosted positions every 10 frames that fade out over 30 frames. The trail of two parallel lines should subtly curve to suggest a **heart shape** as they approach and pass through the door. This is achieved by having the pair wobble slightly left then right then converge as they exit, so the trail forms the two bumps of a heart.

### Beat 4.3: Lingering Glow (Frames 1650–1800, 55s–60s)

**Action**: The room is empty. A faint warm glow remains where they were.

| Frame Range | Visual | Notes |
|-------------|--------|-------|
| 1650–1700   | Empty room. Faint glow at center where they orbited. | Glow = small emission plane, low opacity |
| 1700–1750   | Glow fades. Room slightly "warmer" than beginning (walls go from gray 0.25 to gray 0.3). | Subtle — the room changed |
| 1750–1800   | Fade to full black. | End. |

---

## Animation Principles Reference

### Speed & Proximity as Emotion

| State           | Speed (units/frame) | Gap to Other | Pulse Rate | Meaning |
|-----------------|---------------------|--------------|------------|---------|
| Neutral         | 0.03–0.05           | N/A          | 45 frames  | Calm wandering |
| Interest        | 0.02 (slower)       | Closing      | 40 frames  | Curiosity |
| Discomfort      | 0.08–0.12 (recoil)  | Increasing   | 50 frames  | Avoidance |
| Sadness         | 0.01–0.02           | N/A          | 55 frames  | Deflation |
| Joy             | 0.15+ (spinning)    | Decreasing   | 35 frames  | Excitement |
| Love            | 0.02 (gentle sway)  | Minimal      | 40 frames, synchronized | Bond |

### Contrast Table

| Property          | Square (Mismatch 1) | Rectangle (Mismatch 2) | The One (Match) |
|-------------------|---------------------|------------------------|-----------------|
| Speed             | 4× Seeker           | Same as Seeker         | Same as Seeker  |
| Movement Quality  | Erratic, zigzag     | Rigid, straight lines  | Smooth, curved  |
| Approach Style    | Aggressive           | Indifferent            | Tentative, mutual |
| Response to Seeker| Ignores recoil      | Ignores bump           | Mirrors perfectly |
| Pulse             | 2× frequency        | None                   | Same frequency, same phase |
| Exit behavior     | Leaves alone         | Leaves without pursuit | Leaves together |
| Shape             | Angular              | Angular                | Circular (matches) |

---

## Technical Notes

### Camera
- **Type**: Orthographic
- **Position**: (0, 0, 10) looking straight down (-Z)
- **Orthographic scale**: ~20 (to capture the full room)
- **No camera movement** — static throughout

### Materials
- All materials are **Emission** shaders (no lighting needed)
- Black background = world color (0, 0, 0)
- Characters: emission white/gray at various strengths
- The glow effect at the end: a plane with emission material, animated opacity

### Easing
- Seeker movement: ease-in-out-cubic for most movements
- Square movement: linear or ease-out-bounce (jarring)
- Rectangle movement: linear (mechanical, no easing)
- The One: ease-in-out-cubic (same as Seeker — they match)
- Orbiting: sinusoidal position (cos/sin with changing angular velocity)

### Trail Effect (Act IV)
- Implemented by spawning small, fading circles along the exit path
- Each trail dot: scale 0.15, opacity starts at 0.4, fades to 0 over 30 frames
- Spawn rate: 1 trail dot every 10 frames during exit
- Arrange trail dots so the two parallel trails form a subtle heart curve
