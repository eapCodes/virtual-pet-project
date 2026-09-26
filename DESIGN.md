# Wizardling — Design Doc (v2)

A virtual pet / tamagotchi-style companion that doubles as a light, fully
procedural dungeon crawler. Built to be approachable for casual "just take
care of it" players, with an optional deeper layer for players who want to
train and battle.

Inspired by classic Tamagotchi/Digimon virtual pets — the time-gated
evolution stages of Digimon World and the Pendulum devices, and the
Digimon x Godzilla Color device's G-Cell Activation Value system (a
hidden stat that quietly steers which evolution you get).

Educational/portfolio project — the goal is clean separation between game
logic and presentation, so the same core can be reused across a CLI,
a GUI (Phase 2, in progress), and an Arduino port (Phase 3).

---

## 1. Core Pet Loop (Caretaker Layer)

**Status: built and working**, in `core/pet.py`, both a CLI (`cli/cli.py`)
and a pygame GUI (`cli/game.py`).

This layer must be complete and satisfying on its own — a player should
never be forced into the dungeon to enjoy the game.

### Stats (0–100 unless noted)
- **Hunger** — 100 = full, decays down
- **Energy** — rest fills, actions drain
- **Happiness** — play/attention fills, decays down; hit hard when Hunger
  or Energy is at 0. Also drives the passive Restoration/Dark drift (§3)
- **Knowledge** — does not decay; raised by Study
- **Health** — derived, not directly acted on; drops when Hunger or
  Energy has been at 0 for a while; 0 = Fading state

### Decay (per real hour, recalculated lazily from elapsed time on load)
- Hunger: −4/hr
- Energy: −3/hr (faster if Happiness is already low — "stressed")
- Happiness: −2/hr, extra −5 flat per tick where Hunger or Energy is 0
- Health: no passive decay; −10/hr while Hunger=0 or Energy=0

### Actions (each with a cooldown to prevent spam)
In-code method names stay as-is; on-screen labels are reskinned for the
wizard theme.

| Method (code) | Menu label | Effect | Cooldown |
|---|---|---|---|
| `feed()` | Nourish | Hunger +30, Energy +5 | 15 min |
| `play()` | Recreation | Happiness +25, Energy −10 | 15 min |
| `rest()` | Meditate | Energy +40, Hunger −5 | 30 min |
| `teach()` | Study | Knowledge +15, Energy −15, Happiness −5 | 20 min |

### Mood / State (priority order, first match wins)
1. Health ≤ 0 → **Fading**
2. Hunger ≤ 15 → **Hungry**
3. Energy ≤ 15 → **Tired**
4. Happiness ≤ 20 → **Sad**
5. All stats ≥ 70 → **Happy**
6. Otherwise → **Neutral**

---

## 2. GUI (Phase 2, in progress)

Built in `cli/game.py` with pygame. Placeholder rectangles stand in for
sprites until art is ready — swapping them in later is a small, isolated
change, not a rebuild.

- Window, game loop, event handling
- 4-item scrollable menu (Nourish / Recreation / Meditate / Study),
  highlighted box shows current selection
- Left / Right arrows move the highlight; Enter selects and calls the
  matching `Pet` method
- Still to add: Cancel/back button, on-screen status display (stats +
  mood), Cast Spell / Brew Potion menu items, an "under construction"
  placeholder screen for the dungeon

---

## 3. Evolution System

Evolution is **time-gated, not action-gated** — a pet evolves on schedule
whether or not the player is actively engaged, matching classic
Tamagotchi/Digimon behavior. Care quality and active choices don't
change *whether* a pet evolves, only *what it becomes*.

### Stages

| Stage | Name | Duration to next stage | Notes |
|---|---|---|---|
| 1 | Puddle | ~1–2 hours | No distinguishing look — every pet identical |
| 2 | Elemental Ball | ~4–6 hours | Birth-weather lean becomes visible; Cast Spell / Brew Potion unlock |
| 3 | Appendages | ~2–3 days | **Branch point** — identity locks in; dungeon (shallow layers) and minigames unlock |
| 4 | Clothes | ~4–5 days | Same identity as Stage 3, stronger/more detailed appearance |
| 5 | Mature | — | Final form, same identity as Stage 3, fully realized |

Stages 4 and 5 do not re-branch — they grow whichever identity was
locked in at Stage 3.

### Birth Conditions (set once, at creation)

Two independent axes, both read once via a real-world weather/time
lookup at the moment `Pet.__init__()` runs. Small starting nudges, not
locks — ongoing care and active choices can reinforce or override them.

**Weather → elemental flavor lean:**
- Sunny → Elemental (fire)
- Thunderstorm → Elemental (electric)
- Hail → Elemental (ice, special/rare variant)
- Snow → Illusion
- Rain → Restoration / Nature

**Time of day → light/dark lean:**
- Born at night → small Dark lean
- Born during the day → small Restoration lean (mirrors Rain, for
  symmetry)

### The 5 Magic Schools

- **Elemental** — fire/ice/lightning, offense-leaning
- **Restoration** — healing/wards, ties into potion-making
- **Illusion/Mind** — utility, debuffs
- **Dark/Necromancy** — high power, has a built-in Happiness/Health cost
- **Nature/Alchemy** — buffs/summons, ties into potion-making

Each has its own counter, no decay: `{elemental, restoration, illusion,
dark, nature}`, all starting at 0 (plus any birth-weather nudge). Active
investment happens through Cast Spell (Elemental / Illusion / Dark) and
Brew Potion (Restoration / Nature), once those unlock at Stage 2.

### Restoration vs. Dark: the Care-Quality Axis

Separate from active-use growth, Restoration and Dark also drift
**passively**, driven by Happiness, checked during `tick()`:
- Happiness ≥ 70 → small Restoration nudge
- Happiness ≤ 20 → small Dark nudge
- Otherwise → no passive drift

This passive drift is **strongest during Stage 1, tapering toward zero
by Stage 3** — early care matters most.

**Balance bonus (Twilight):** if the Restoration-vs-Dark gap stays
within 5–10 points at the Stage 1→2 checkpoint *and* is sustained
through the Stage 2→3 checkpoint, the pet qualifies for the rare
**Twilight** trait. Balance achieved only at the Stage 2 checkpoint
(not Stage 1) grants a lesser/partial version. Drifting out of balance
after an early success grants nothing extra — the final Stage 2→3
snapshot is what decides the outcome, care quality determines which
direction (Restoration or Dark) any leftover imbalance leans.

Twilight is an independent qualifier, not its own school — it can stack
onto any tier below (a Twilight-Pure Elemental, a Twilight-Hybrid, etc.),
representing sustained equilibrium alongside whatever else the pet
specialized in.

### Branch Tiers (decided once, at the Stage 3 checkpoint)

At Stage 3, the game checks how many of the 5 schools are meaningfully
invested in, relative to each other. Full combinatorics (choosing *k*
schools out of 5):

| Tier | Schools involved | Count | Twilight variant also possible? |
|---|---|---|---|
| Pure | 1 | 5 | Yes → Twilight-Pure (5) |
| Hybrid | 2 | 10 | Yes → Twilight-Hybrid (10) |
| Tri-class | 3 | 10 | Yes, in principle |
| Quad-class | 4 | 5 | Yes, in principle |
| Archmage | 5 (all) | 1 | N/A — already includes everything |

Full mathematical space: **31 school-combinations**, up to **62** if every
one gets a Twilight variant. Note: the Restoration+Dark hybrid slot
overlaps conceptually with Twilight itself (both are "Restoration and
Dark roughly equal") — worth deciding whether to treat it as its own
hybrid or fold it into the Twilight system when this is implemented.

**Scope decision — hand-crafted vs. procedural vs. effect overlay:**
- **Pure (5) + Hybrid (10) + Archmage (1)** = 16 forms get real names
  and dedicated base art — these are what an ordinary player will
  actually reach.
- **Twilight is not a separate sprite.** It's a single reusable
  glow/particle overlay effect, drawn on top of whichever base form the
  pet has, tinted using that form's own school color(s) — red for a
  Fire Pure, green for Restoration, a blended tint for a two-school
  Hybrid, etc. One effect asset, one small color-lookup, reused across
  every base form it can apply to. Dark's Twilight tint should lean
  into a light/dark split rather than a flat color, since that's
  already Dark's whole theme.
- **Tri-class, Quad-class (15 combinations)** get a **procedurally
  generated name** (e.g. "Elemental-Illusion-Dark Wizard," assembled
  from whichever schools qualify) and a shared/recolored visual
  treatment rather than bespoke sprites — reaching these is rare enough
  that hand-crafted art isn't justified yet.

A school must be the highest (or tied for top-*k*) **and** clear a
minimum share of total points (e.g. ≥40% for the dominant one) to
qualify — stops a generalist from accidentally locking into a school
they barely touched.

### Sprite Checklist (current scope)

- 1 — Stage 1 (universal Puddle)
- 5 — Stage 2 (weather-lean looks)
- 16 — Stage 3 hand-crafted (5 Pure + 10 Hybrid + 1 Archmage)
- 16 — Stage 4 (same 16 identities, evolved look)
- 16 — Stage 5 (same 16 identities, final look)
- **54 base sprites total**, plus **1 reusable Twilight overlay effect**
  (tinted per school at render time — not a separate sprite per form),
  plus Tri-class/Quad-class handled procedurally (no dedicated art
  required initially)

In practice, Stage 4/5 art can often be palette-swaps or added detail on
the Stage 3 base rather than fully separate drawings.

---

## 4. Dungeon Layer (opt-in, fully procedural)

Unlocks at Stage 3. No hand-authored levels — only weighted tables the
game assembles at random each run.

- Each run is a seeded random walk: generate rooms one at a time, each
  drawn from a room-type pool (monster encounter / trap / treasure /
  empty)
- Monster/trap/loot specifics also drawn from pools, so content variety
  comes from table size, not level design
- **Difficulty scales off the pet's current stat total at the moment of
  entry, not off depth alone** — this is the key anti-trivialization
  lever. A heavily trained pet just meets tougher monsters at the same
  depth, so the dungeon stays tense at any power level
- Depth still controls loot rarity/variety, giving a reason to go deeper
  beyond raw difficulty
- Each room costs Energy (and a little Hunger), so a run is bounded and
  ties back into the core caretaker loop
- A loss (Health hits 0 mid-run) ends the run early and hits Health/
  Happiness hard on return

---

## 5. Minigames (train affinity, don't trivialize the dungeon)

Unlock at Stage 2 alongside Cast Spell / Brew Potion.

- **Spellcasting** (rhythm-timing or Simon-style sequence memory) →
  raises Elemental / Illusion / Dark depending on which spell is cast
- **Potion-making** (ingredient matching or mix-ratio meter) → raises
  Restoration / Nature

### Keeping minigames from being an "infinite grind" exploit
1. **Mana gates spellcasting.** Capped resource, regenerates slowly
   (like Energy).
2. **Ingredients gate potion-making.** Mostly come from dungeon loot,
   only a slow trickle otherwise.
3. **Diminishing returns on repeating the same spell.** Shrinking
   affinity gains on repeat casts, resetting after a Rest or a day
   passing.
4. **Dungeon difficulty scales to the pet's current power** (see §4).

---

## 6. Weather & Time-of-Day Visuals (deferred, end of roadmap)

Separate from the one-time birth-weather lookup (§3), a *continuous*
weather effect (e.g. rain falling on screen) and time-of-day background
tinting are planned as later polish, alongside minigames/dungeon — both
require either a live weather API or reusable particle-effect code, not
yet built.

---

## 7. Architecture

Keep game logic and presentation completely separate so the CLI, GUI,
and a future Arduino port can all share the same core.

- **`Pet`** — pure state: stat dict, affinity dict, birth conditions,
  stage, last-updated/last-action timestamps. Methods: `tick()`,
  `feed()`, `play()`, `rest()`, `teach()`, `mood()`, `save()`,
  `load()` (classmethod). No I/O beyond save/load's own file access.
- **`Dungeon`** — room/monster/loot tables, `generate_room(depth, seed)`,
  encounter resolution. Not yet built.
- **Minigames** — standard interface, e.g. `run_minigame() -> score`.
  Not yet built.
- **Save/load** — JSON, datetimes stored via `.isoformat()` /
  `datetime.fromisoformat()`. Decay is recalculated from elapsed real
  time on load via `tick()`, not stored per-tick. Built and working;
  will need the affinity dict and birth conditions added once those
  exist.
- **Frontend shells** — `cli/cli.py` (done); `cli/game.py` (pygame GUI,
  in progress); Arduino C++ or MicroPython port (Phase 3) reusing the
  same state machine.

---

## 8. Roadmap (in order)

**Shell-building (small/medium):**
- [ ] Left-arrow key (menu navigate backward)
- [ ] On-screen status display
- [ ] Magic school affinity dict added to `Pet`
- [ ] Dark affinity's Happiness/Health cost
- [ ] Cast Spell / Brew Potion menu items (placeholder logic)
- [ ] Enter Dungeon menu item ("under construction" placeholder)
- [ ] Cancel/Back button
- [ ] Save/load updated to include affinity + birth conditions

**Sprites (once shell is stable):**
- [ ] Idle sprite replacing placeholder rectangle
- [ ] Mood-based sprite variations
- [ ] Menu icons replacing text labels

**Major standalone builds (own future phases):**
- [ ] Spellcasting minigame
- [ ] Potion-making minigame
- [ ] Dungeon layer
- [ ] Full evolution branch logic (tier detection, name assembly for
  procedural tiers)
- [ ] Live weather integration + time-of-day visuals

**Hardware (Phase 3/4):**
- [ ] Pico/breadboard prototype (MicroPython)
- [ ] Custom PCB design
- [ ] 3D-printed enclosure

---

## 9. Open Questions
- Final flavor names for the 30 hand-crafted Stage 3–5 identities
  (placeholders used in early sketches: Pyromancer, Cleric, Illusionist,
  Necromancer, Druid, and their Twilight/Hybrid counterparts)
- Whether Restoration+Dark Hybrid folds into Twilight or stays separate
- Exact Mana pool size/regen rate and ingredient drop rates
- Combat resolution formula (pet ATK/DEF derived from stats + stage vs.
  monster stats, plus minigame-driven bonuses)
- Monster/trap/loot tables for the dungeon generator
