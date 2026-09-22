# Wizardling — Design Doc

A virtual pet / tamagotchi-style companion that doubles as a light, fully
procedural dungeon crawler. Built to be approachable for casual "just take
care of it" players, with an optional deeper layer for players who want to
train and battle.

Inspired by classic Tamagotchi/Digimon virtual pets, especially the
Digimon x Godzilla Color device's G-Cell Activation Value system (an
extra hidden stat that quietly steers which evolution you get).

Educational/portfolio project — the goal is clean separation between game
logic and presentation, so the same core can be reused across a CLI,
a GUI (Phase 2), and an Arduino port (Phase 3).

---

## 1. Core Pet Loop (Caretaker Layer)

This layer must be complete and satisfying on its own — a player should
never be forced into the dungeon to enjoy the game.

### Stats (0–100 unless noted)
- **Hunger** — 100 = full, decays down
- **Energy** — rest fills, actions drain
- **Happiness** — play/attention fills, decays down; hit hard when Hunger
  or Energy is at 0
- **Knowledge** — does not decay; raised by Teach/Study and (later)
  spellcasting minigames
- **Health** — derived, not directly acted on; drops when Hunger or
  Energy has been at 0 for a while; 0 = Fading state

### Decay (per real hour, recalculated lazily from elapsed time on load)
- Hunger: −4/hr
- Energy: −3/hr (faster if Happiness is already low — "stressed")
- Happiness: −2/hr, extra −5 flat per tick where Hunger or Energy is 0
- Health: no passive decay; −10/hr while Hunger=0 or Energy=0

### Actions (each with a cooldown to prevent spam)
| Action | Effect | Cooldown |
|---|---|---|
| Feed | Hunger +30, Energy +5 | 15 min |
| Play | Happiness +25, Energy −10 | 15 min |
| Rest | Energy +40, Hunger −5 | 30 min |
| Teach/Study | Knowledge +15, Energy −15, Happiness −5 | 20 min |

### Mood / State (priority order, first match wins)
1. Health ≤ 0 → **Fading**
2. Hunger ≤ 15 → **Hungry**
3. Energy ≤ 15 → **Tired**
4. Happiness ≤ 20 → **Sad**
5. Knowledge crosses an evolution threshold → **Evolving** (one-tick
   transition state)
6. All stats ≥ 70 → **Happy**
7. Otherwise → **Neutral/Content**

---

## 2. Magic School Affinity (drives evolution)

Instead of a single Knowledge ladder, evolution branches based on which
magic school the player has leaned into. This replaces an earlier "taint"
meter idea — dark magic is just one school among several, not a
punishment track.

### Schools
- **Elemental** — fire/ice/lightning, offense-leaning
- **Restoration** — healing/wards, ties into potion-making
- **Illusion/Mind** — utility, debuffs
- **Dark/Necromancy** — high power, has a built-in cost (see below)
- **Nature/Alchemy** — buffs/summons, ties into potion-making

### How affinity builds
Each school has its own counter, no decay, similar to Knowledge:
`{elemental: 0, restoration: 0, illusion: 0, dark: 0, nature: 0}`

Whichever spell/minigame the player engages with nudges that school's
counter up. The minigame choice *is* the training choice — no separate
specialization menu needed.

### Dark magic's tradeoff
Every point gained in Dark affinity also ticks a small amount off
Happiness or Health over time. Leaning into Dark should feel like a real
tradeoff (power for upkeep cost), not just "the edgy option."

### Evolution branching
At each Knowledge threshold, branch based on the dominant school:
- Must be the highest affinity **and** clear a minimum share of total
  points (e.g. ≥40%) to qualify — stops a generalist from accidentally
  locking into a school they barely touched
- Stage 2 (Apprentice): generic, no branch yet
- Stage 3: branches into 5 forms (one per school) based on dominant
  affinity at that point
- Stage 4: can branch again off the Stage 3 choice using a secondary
  affinity (tree structure, Digimon-style)

---

## 3. Dungeon Layer (opt-in, fully procedural)

No hand-authored levels — only weighted tables the game assembles at
random each run.

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
  ties back into the core caretaker loop — you can't dungeon-crawl
  forever without feeding/resting
- A loss (Health hits 0 mid-run) ends the run early and hits Health/
  Happiness hard on return

---

## 4. Minigames (train affinity, don't trivialize the dungeon)

Two minigames, each mapped to two schools:

- **Spellcasting** (rhythm-timing or Simon-style sequence memory) →
  raises Elemental / Illusion / Dark depending on which spell is cast
- **Potion-making** (ingredient matching or mix-ratio meter) → raises
  Restoration / Nature

### Keeping minigames from being an "infinite grind" exploit
The design goal: repeating a minigame endlessly should **not** be the
optimal way to prep for the dungeon.

1. **Mana gates spellcasting.** Capped resource, regenerates slowly
   (like Energy). Can't spam-cast past a few uses without waiting.
2. **Ingredients gate potion-making.** Ingredients mostly come from
   dungeon loot, with only a slow trickle from other sources. Running
   out of ingredients caps how many potions you can brew, so the
   dungeon feeds the minigame rather than the other way around.
3. **Diminishing returns on repeating the same spell.** Casting the same
   spell back-to-back gives shrinking affinity gains ("fatigue"),
   resetting after a Rest or a day passing. Encourages variety over
   looping one action.
4. **Dungeon difficulty scales to the pet's current power** (see §3),
   so even a perfectly optimized pet doesn't outrun the challenge.

Together: a caretaker-only player never has to touch Mana, ingredients,
or the dungeon at all. A dungeon-diver's grinding is bounded on multiple
sides, and even maxed-out stats don't make runs trivial.

---

## 5. Architecture

Keep game logic and presentation completely separate so the CLI, a
future GUI, and a future Arduino port can all share the same core.

- **`Pet`** — pure state: stat dict, affinity dict, stage, last-updated
  timestamp. Methods: `tick(elapsed_seconds)`, `feed()`, `play()`,
  `rest()`, `teach()`, `get_mood()`. No I/O.
- **`Dungeon`** — room/monster/loot tables, `generate_room(depth, seed)`,
  encounter resolution. Also pure logic.
- **Minigames** — standard interface, e.g. `run_minigame() -> score`.
  CLI renders as text prompts; GUI/Arduino swap in sprites or physical
  input (buttons, LEDs, a potentiometer for the mix-ratio game) behind
  the same interface.
- **Save/load** — serialize state + last-tick timestamp to JSON; decay
  is recalculated from elapsed real time on load, not stored per-tick.
- **Frontend shells** — `cli.py` now; `gui.py` (Phase 2, sprite-based);
  Arduino C++ port (Phase 3) reusing the same state machine.

---

## 6. Open Questions / Next Steps
- Exact evolved forms per school (names, sprites, stat bonuses) at each
  evolution tier
- Full monster/trap/loot tables for the dungeon generator
- Exact Mana pool size/regen rate and ingredient drop rates
- Combat resolution formula (pet ATK/DEF derived from stats + stage vs.
  monster stats, plus minigame-driven bonuses)