# W7 (planetary): the implementation plan

**Authority and reading order.** `docs/PLAN-WORKBOOK.md` (§1, §3.3, §3.5, §4.2–§4.5, §6) is the authority, then
`W5-DECISIONS.md` (its rulings carry over unless this plan says otherwise), then this plan. The user's answer of
2026-11-14 recorded in `docs/HANDOFF-WORKBOOK.md` ("Answered ahead of its phase") settles what stands for a carrier
in SolidWorks: **a skeleton only**, a part of axes and planes with no solid, as the layout part is, free to turn
about its own shaft's axis, each planet mated to an axis in it; the app makes no plate and no pins. W5's plan
(`W5-PLAN.md`), its review and `W5-INTERFACES.md` are the model for this plan's shape.

W7 is planned to start **after W6 closes** (W6, turned axes and bevel meshes, is planned in parallel by someone else
and built first). §5 says what W7 assumes of W6 and how it stays apart from it.

Rules carried over unchanged (HANDOFF, "Rules carried over"): commits by explicit path, prose messages with the why,
no Claude co-author or attribution line, never `add -A` / `commit -a` / stash / reset / rebase; the orchestrating
session pushes, subagents commit only; findings only from committed `findings.py`, read with `getattr(findings,
NAME, None)`, a missing one refusing with a sentence; every raise a full sentence; the repo is public (no user
document titles in committed logs). **Testing (the user, 2026-11-14):** the phase is written against the fake and
then built end to end on SolidWorks 2026 early; what that build gets wrong is probed step by step; probing ahead is
kept only for a call not used before that could hang, raise a dialog, or damage a file or a session (§7). SolidWorks
2024 gets one confirming build at the phase's end. One follow-up probe round per phase. An Opus subagent reviews the
plan, the interface commit and each package before the next step.

---

## 1. Scope

### 1.1 What W7 adds (PLAN-WORKBOOK §6: "Carriers, copies, loops in kinematics and phases — A 4 : 1 planetary with
the ring fixed builds")

- **Carriers**: a shaft row that other shafts are `Mounted on` (§1, Shafts). It is laid out, checked, solved and
  built: in SolidWorks as a skeleton part that turns about its own axis.
- **Copies**: a mounted shaft's `Copies` (§1: "that many, evenly round it"), with every gear on it, placed, phased,
  checked and built as that many components of one part file.
- **Loops in kinematics**: the mesh equation with its carrier term (§3.5), a planetary's Willis relation; torques
  through a planetary stage (§3.5: "Loops wait for W7").
- **Loops in phases**: each planet copy and the ring placed so their teeth mesh at every copy at once; a loop that
  does not close is the assembly condition failing (§3.3), an error.
- **Loops in mates**: the gear mates of a planetary over-determine the motion; which are made and which are left out
  (W5-PLAN D6's `unmated` hook, review M13).
- **Update SolidWorks** on a planetary stage: values, moves (the carrier part's globals among them) and the
  structural cases.

### 1.2 What stays refused, and with which sentence

Today every carrier row is refused (`workbook/build.py`, `later_rows`): *"P is mounted on C, with 3 copies round it:
carriers and copies are laid out in phase W7, and the gearbox is not checked until then."* That sentence goes. Still
refused at Build after W7, as `later_rows` warnings (so Build parts still builds the gears):

| Row | Sentence (B writes; `later_rows` style, at the cell) |
|---|---|
| bevel, sleeve, dog, sliding gears, modes | as today: W6, W8 (W6 removes the bevel row's) |
| a shaft mounted on a shaft that is itself mounted | *"P2 is mounted on P, which is itself mounted on C: a carrier riding another carrier is not built by this version."* |
| a carrier, or a shaft mounted on one, whose axis is not Z+ or Z- | *"C's axis is X+: a planetary stage is built only on an axis along Z+ or Z- by this version."* |
| a planet whose axis is neither parallel nor opposite to its carrier's | *"P's axis is Y+ and C's is Z+: a planet turns about an axis parallel to its carrier's, so this is not built by this version."* |

Errors (not refusals), in `checks`: a mesh between a planet and a gear on a frame shaft that is not coaxial with the
planet's carrier (§3.5: *"a mesh that fits no carrier is an error"*); a carrier mounted on itself through a chain
(`A` on `B`, `B` on `A`); `Copies` below 1. The model already makes `Copies` other than 1 on a frame shaft an error
(`model._check_references`).

### 1.3 What exists for each piece, and what is missing (read from the code at `0f5a121`)

| Piece | Exists | Missing |
|---|---|---|
| Format | `schema.SHAFTS` has `Mounted on` and `Copies` (whole); `model.Shaft.mount()`; `_check_references` refuses an unknown mount, a self-mount, Copies on a frame shaft | Copies ≥ 1; a mount chain; nothing else |
| Refusal | `build.later_rows` refuses every mounted shaft | narrowed to §1.2 |
| Layout | `geometry.layout` returns `later` for any mounted shaft and places nothing | copies placed (§2.2) |
| Phases | `geometry.phases` walks meshes outward from the input; a gear reached twice that disagrees is a `conflict`; `checks.check` makes it a **warning** ("a loop of meshes that does not close") | meshes expanded per copy; the conflict an **error** for carried loops (§2.4) |
| Kinematics | `kinematics.solve` is the linear system in `Fraction`s; mounted shafts set `later` ("Speeds through a carrier … phase W7"); its mesh row is `za·ωa ± zb·ωb = 0`, the carrier term absent; torque is W3's power-path walk | the carrier term; planetary torques (§2.5) |
| Checks | `checks.check` stops at `layout.later` (`report.unchecked`); `_check_clearances` covers any two placed gears; `_check_shafts` warns when a gear passes over another shaft's axis | coaxial shafts exempted from that warning (sun over the carrier's and ring's axes); the planetary checks (§2.3) |
| Layout part | `layout.shaft_layouts` raises on a mounted shaft; `layout_plan` makes planes offset from Right/Top and a named axis through them, globals as literals, a base plane at 0 | mounted shafts skipped; the carrier part (§2.6), reusing `layout_plan` |
| Motion | `motion.motion_plan`: union-find over **shafts**, a mesh touching a fixed gear skipped, a loop-closer `unmated` (D6), one anchor per shaft | bodies per copy, ground merged, the carrier as an anchor (§2.7) |
| Planning | `gearbox.plan_gearbox`: one component per Gears row, handle `gear<index>`; identical rows share one part (`build.plan_parts`) | a component per copy; the carrier part, made or reused; the journal's carrier entry |
| Worker | `swbuild.build_gearbox` builds parts → layout → assembly; `_settle_sense` reads each gear mate back; `train_check` judges meshes and locks; `_update_motion` puts each train whole (`_put_train`) | carrier documents built and updated; a carrier link in `train_check` and `_trains`; carriers put first |
| COM | `swcom.Session._component_ref` selects `"<handle>:<feature name>"` in any component by `FeatureByName` (so `carrier1:P copy 2 Axis` needs nothing new); `add_mate` makes coincident, point, point distance, lock and gear mates | nothing expected (§2.9) |
| Record | `store` schema 3: `GearboxRecord`, `ComponentEntry`, `MateEntry`, `ShaftEntry` | carriers, the copy a component is of, the part a mate's axis is in (§2.11) |
| Words | none for planetaries | §2.12 |
| Demonstration | `probe/workbook_assembly_check.py` W4/W5 sections; its header says a fixed shaft and a loop-closer are not shown | the planetary sections (§6) |

---

## 2. The design

### 2.1 The workbook rows of a planetary stage, and how the model reads them

A planetary stage is written with the rows §1 already has. The 4 : 1 fixture (§4):

| Shaft | Mounted on | X | Y | Z | Axis | Role | Copies | Speed | Torque |
|---|---|---|---|---|---|---|---|---|---|
| S | frame | 0 | 0 | 0 | Z+ | input | | 1000 | 2 |
| C | frame | 0 | 0 | 0 | Z+ | output | | | |
| P | C | 18 | 0 | 0 | Z+ | | 3 | | |
| R | frame | 0 | 0 | 0 | Z+ | fixed | | | |

Gears `Sun` on S, `Planet` on P (one row, three components), `Ring` on R (internal); Meshes `Sun–Planet`,
`Planet–Ring`. The model needs no new field: `Shaft.mount()` and `Shaft.copies` already carry it.

- **A carrier** is any frame shaft that another shaft is mounted on. It may carry gears of its own (an output gear on
  the carrier's shaft); it need not.
- **A planet shaft** is a shaft mounted on a carrier. Its X, Y, Z are **offsets from the carrier's point along the
  origin's X, Y and Z**, at the carrier's starting turn (§1: "measured on that shaft at its starting turn"; the
  carrier is built unturned, so its frame then is the origin's, translated). *Reading J4.*
- **Copies** of a planet shaft stand evenly round the carrier's axis: copy k (k = 1 … N) is copy 1 turned by
  `(k − 1)·360/N` degrees about the carrier's own Axis by the right-hand rule, so in the view from +Z they are
  numbered anticlockwise for a Z+ carrier and clockwise for a Z- one. Copy 1 is at the typed X, Y.
- **Copy names** (*reading J3*): with Copies = 1 a shaft and its gears keep their own names. With N > 1, copy k of
  gear `Planet` is `Planet copy k` and of shaft `P` is `P copy k`. A space is not allowed in a workbook name
  (`schema.NAME_PATTERN`), so a copy name never equals a gear's or shaft's own. Pure helpers in a new
  `workbook/planetary.py`: `copy_id(name, k, copies)`, `copy_offsets(x, y, copies, sigma_c)`.
- **The stage** is recognised, not typed (PLAN: "There is no type cell"): `planetary.stages(spec, placed)` finds, per
  carrier, its planet shafts and gears, the frame gears coaxial with the carrier that mesh a planet outside (suns) or
  inside (rings), and which member is fixed. `planetary.Stage` is pinned in §3.

### 2.2 Placing copies (`geometry`)

`geometry.layout` places every gear on a planet shaft once per copy, keyed by its copy id: centre
`(x_c + dx_k, y_c + dy_k)` from `copy_offsets`, mid-face `z = z_c + z_p + σ_p·At` (σ_p the planet shaft's own sense,
as `_place` does for a frame shaft), each `Placed` with three additive fields: `row` (the Gears row id), `copy` (k, or
0 when Copies = 1), `carrier` (the carrier shaft, or `""`). `geometry.expand_meshes(spec, placed)` lists the meshes at
copy level, in Meshes-sheet order and copy order within a row: `Sun–Planet` becomes `Sun–Planet copy 1`, `… copy 2`,
`… copy 3`. A mesh between two planets on the same carrier pairs copy k with copy k. Everything downstream that reads
`report.layout.placed` keyed by gear id reads copy ids; where it names a cell it goes through `Placed.row`.

### 2.3 Checks (`checks`, `planetary`)

Every check below names its cell. The general checks run on what is placed: per expanded mesh the clearance and the
phase, but the centre, kind, module, pressure-angle, hand and face checks **once per Meshes row** (copy 1), since the
copies are the same mesh turned, and the same error three times is noise.

1. **The ring's tooth count** (a simple stage: one sun, one ring, one planet gear per copy, unshifted):
   `z_ring = z_sun + 2·z_planet`. It follows from the two centre checks already made (the sun–planet centre
   `m(z_s + z_p)/2` and the planet–ring centre `m(z_r − z_p)/2` must both be the planet's typed distance), so it is
   said in their place, once, when both fail together: *"Gears!F4: Ring has 56 teeth, and a ring around Sun (18) and
   Planet (18) needs 18 + 2 × 18 = 54: with 56 the planets cannot mesh with both at once."* **Shifted form:** the sun
   may be shifted (its working centre distance from `pair.describe`'s shifted branch must equal `m(z_r − z_p)/2`); a
   **planet with profile shift meshing a ring is an error**, *"Planet is shifted (+0.3 × m) and meshes inside Ring,
   which is built without profile shift, so its tips would clash with Ring's teeth at this centre distance."* — the
   clash the ring probe saw (HANDOFF, open item), here made a check because a planet always meets the ring. *Reading
   J9; it does not answer HANDOFF question 2 for parallel trains, which stays the user's.* (`checks._check_mesh` calls
   the internal `describe` without the shifts today, so a shifted pinion in a ring passes the checks silently. W7
   adds the error for a **carried** planet's ring mesh only; a ring mesh between frame shafts keeps today's behaviour
   until the user answers question 2.)
2. **The assembly condition.** Evenly spaced copies mesh with the sun and the ring at once exactly when
   `(z_sun + z_ring)/N` is a whole number (for a planet on a Z+ carrier between an outside sun and an inside ring; the
   phase-corrected form for any stage is that the phase walk of §2.4 closes at every copy, which reduces to this for
   the simple stage and holds with profile shift, since shift is symmetric about the space centre). For the simple
   stage the error says it in numbers and lists what works: *"Shafts!H4: 5 copies of Planet cannot all mesh with Sun
   and Ring at once: (18 + 54) / 5 = 14.4 is not a whole number. With these teeth the copies can be 2, 3 or 4 (6, 8,
   9, 12, 18, 24, 36 or 72 also divide 72, but their neighbours would clash)."* For any other stage (a compound or
   double planet) the phase walk's conflict is the error, naming the copy and the gear that disagree. W3's warning
   for a loop of frame shafts stays a warning.
3. **Neighbouring copies.** Copies k and k+1 stand `2a·sin(π/N)` apart (a the planet's distance from the carrier
   axis); their outer diameters plus `CLASH_GAP · m` (0.5 m, the existing constant) must fit: *"Shafts!H4: 6 copies of
   Planet stand 18 mm apart round C, and their tips reach 20 mm with 0.5 mm to spare needed: 4 is the most that fit."*
   `_check_clearances` would also catch it pairwise; this sentence replaces its pairwise ones for copies of one shaft.
4. **A member fixed.** A stage with one input and no member fixed is free; kinematics already says so per shaft
   (*"nothing settles C's speed …"*). The planetary sentence replaces those for the stage: *"S, C and R form a
   planetary stage with one input, S: one of the others must be fixed (Role fixed) or be a second input, or nothing
   settles their speeds."* Two members fixed jam it (the existing jammed error).
5. **Coaxial shafts** (sun, carrier, ring on one line, within `CENTRE_TOLERANCE`) are exempt from `_check_shafts`'
   "passes over another shaft's axis" warning: they are concentric shafts, which is what a planetary is.
6. **Undercut**, honestly: W7 models none. A sun or planet below the undercut limit keeps the strip's warning
   (`spur.section_diagnostics`: *"… below the undercut limit …: a generated gear would lose the bottom of its flanks,
   which this profile does not show."*). The modelled gear keeps the material a generated one would lose, so a
   mating tip may reach into it; SolidWorks' interference check sees one position only, so it may or may not show
   such a clash at the built phase, and a drag may pass through one. W7 adds one clause to the interference result
   (C): when a reported clash involves a gear the Checks warned is undercut, the sentence ends *"; Sun is below the
   undercut limit and its undercut is not modelled, so the clash may be the bottom of its flanks"*. The fixture uses
   18 teeth (limit 17.1 at 20°), so the demonstration is not muddied by it.

No fix is offered for a planetary centre error (PLAN §3.6 already withholds Move inside a loop; a shift fix would
have to keep three meshes and the assembly condition at once). *Reading J9.*

`checks._worked_out_as` says the stage: *"Planetary, R fixed · 3 planets · 4.000 : 1 · output turns the same way"*
(several stages or a stage feeding parallel meshes: *"Planetary and parallel · …"*).

### 2.4 Phases

`geometry.phases` runs on the expanded meshes. It starts from the first input's gear (θ = 0) as today, so for the
fixture: `Sun` θ 0; each `Planet copy k` from the sun by `external_space`; the ring from copy 1 by `ring_space`; the
ring reached again from copies 2 and 3 must agree to a hundredth of its pitch, or it is a conflict. A conflict whose
loop passes through a carried copy is §2.3 item 2's error; the copies' and the ring's θ are those of the first way
reached (as today), so the end view still draws something. Each copy has its own θ: the copies are components of one
part, each placed at its own frame. A carrier has no teeth and no θ: it is built unturned.

For the fixture every copy comes out at θ = 10° (half of the 20° pitch, as `pair.mesh_angle` gives for an even
partner at φ = 0, and `2ψ_k + 170° ≡ 10° (mod 20°)` for ψ_k = 0°, 120°, 240°), and the ring at 0 modulo its pitch
(6.6667°) from every copy: `(z_s + z_r)/N = 24` is whole. Numbers in §4.

### 2.5 Kinematics with a loop

**The mesh equation with its carrier** (PLAN §3.5). Unknowns stay one per **shaft row** (a planet shaft's copies all
turn at one speed about their own axes, by symmetry, so they share one unknown and add no rows). For a mesh between
gears on shafts p and q, its carrier c is: `frame` when both are frame shafts; the carrier C when one or both are
mounted on C and the other is mounted on C or is a frame shaft coaxial with C; otherwise the mesh fits no carrier, an
error. Then, projected on the reference axis n as today (ω̃ = ω · (a·n)):

    (ω̃_p − ω̃_c)·z_p = ∓ (ω̃_q − ω̃_c)·z_q        − outside, + a pinion in a ring;  ω̃_frame = 0

so the row `kinematics.solve` adds is `z_p·ω̃_p ± z_q·ω̃_q − (z_p ± z_q)·ω̃_c = 0`. Nothing else in the solver
changes: inputs are their speed, fixed shafts 0, and the exact rank says settled, free or jammed. **What "loops"
means for the solver:** it was always one linear system, not a walk, so a planetary's loop (sun – planet – ring, closed
through the carrier's term) needs no new method; the only change is the carrier column. Loops show elsewhere: in the
mates (§2.7: N copies over-determine the gear mates) and in the phases (§2.4).

**The Willis equation** falls out of it: `(ω_s − ω_c)/(ω_r − ω_c) = −z_r/z_s`. With any one member held:

| held | input → output | ratio (input ÷ output) | fixture (z_s 18, z_r 54) |
|---|---|---|---|
| ring | sun → carrier | `1 + z_r/z_s` | **4.000 : 1**, same way |
| sun | ring → carrier | `1 + z_s/z_r` | 1.333 : 1, same way |
| carrier | sun → ring | `−z_r/z_s` | 3.000 : 1, the other way |

**Planet speeds.** `Motion.speeds` holds each planet shaft's speed about its own axis in the frame of the origin
(absolute), as every other shaft. `Motion.relative` (new) holds, for each mounted shaft, its speed relative to its
carrier about its own axis: `ω_p − σ_p·σ_c·ω_c` (signs for an opposite-facing planet). Fixture: P −500 rpm, −750 on
C. The window's Speeds panel and the Results sheet show both (§2.12).

**Torques** (*reading J10*). For a stage with one member held and one input, by the basic-train efficiency: η₀ is the
product of the efficiencies of the meshes from sun to ring through one planet (98 % × 98 % = 96.04 % by default); in
the carrier's frame the member whose relative power is positive drives, and the other receives η₀ of it:

    T_s + T_r + T_c = 0,   T_receiver·(ω_receiver − ω_c) = −η₀·T_driver·(ω_driver − ω_c)

Ring held, sun driving: `T_c = T_s·(1 + η₀·z_r/z_s)` = 2 × (1 + 0.9604 × 3) = **7.7624 N·m**, stage efficiency
97.03 %; the ring holds **5.7624 N·m** against it. Each planet shaft carries 0 about its own axis (W3's idler rule:
the tooth forces pass the planet). The held member's torque is reported as held (`Motion.held`, new: shaft → N·m),
since a housing must take it. The stage is joined to W3's power-path walk as one link from its input member to its
output member (ratio and η of the stage), so a planetary feeding a parallel train gets torques on. Not given, with
`Motion.torque_note` saying why: two inputs (a differential), compound or double planets, two stages in one power
path that splits.

### 2.6 The carrier part (`layout`)

One part per carrier shaft that turns or is held: `<Name>_<Carrier>_Carrier.SLDPRT` (`Planetary_4to1_C_Carrier`;
a revision `<Name>_r<n>_<Carrier>_Carrier`), made by **`layout.layout_plan` itself** on the carrier's own axes, its
`BuildPlan.kind` `"carrier"` (`layout.CARRIER_KIND`), so it is built and checked like the layout part and has no
solid, no plate, no pins (the user's answer). It holds, in its own coordinates:

- `"<C> Axis"`, through the Right and Top base planes (a shaft at 0, 0: `AXIS_THROUGH_BASE_PLANE`, as S1 of the 12 : 1
  is made in the layout part);
- per copy k of each planet shaft, the plane offset from Right by its local x and the one from Top by its local y
  (`"P copy 2 X Plane"`, …; the base plane at 0) and `"P copy 2 Axis"` through them, the two driven by globals
  `"P copy 2 X"`, `"P copy 2 Y"` holding **literal** values the app works out (*reading J1*: no trigonometry in
  SolidWorks equations, which nothing has probed; Update sets each global as it sets the layout's). Local
  coordinates are `F_σcᵀ·(offset)`: `(dx, dy)` on a Z+ carrier, `(dx, −dy)` on a Z- one.

Its origin sits **on the layout's Front plane**, at `(x_c, y_c, 0)`, whatever the carrier's Z (*reading J2*): the
carrier has no thickness, so its place along its axis means nothing except as the planets' base, and the planets are
held along their shafts from the layout's Front plane themselves (§2.7). So a carrier never meets W5's Front-plane
structural rule. Its frame in the assembly is `F_σc` at that origin, unturned.

Pinned (B writes, interface commit gives shapes): `CarrierLayout(shaft, x, y, z, sigma, axes:
Tuple[ShaftLayout, ...])` (its own axis first, then each copy's, in carrier coordinates), `carrier_layouts(spec,
report)`, `carrier_stem(box_name, revision, shaft)`, `carrier_plan(carrier, template, path)`, `carrier_frame(carrier)
-> Frame`, `carrier_id(shaft) -> "C carrier"` (the carrier component's id in handles, the record and mates: a space,
so never a gear's name), `CARRIER_KIND`, `CARRIER_HANDLE = "carrier"`. `shaft_layouts(spec)` returns the frame shafts
and **skips** mounted ones (it raises on them today); a carrier shaft is a frame shaft and keeps its `"C Axis"` in the
layout part too, on the same line as `"S Axis"` and `"R Axis"`.

Why this works with no plane at an angle (PLAN §4.2 said carriers "need a plane at an angle, or an axis from a point
and a direction"): every planet axis is parallel to its carrier's, so it is the line where a plane offset from the
carrier part's Right plane meets one offset from its Top plane, whatever the copy's angle round the carrier. Only a
planet not parallel to its carrier (refused, §1.2) would need W6's construction.

### 2.7 The turning assembly (`motion`)

Components, in insertion order: the layout (`layout`), each carrier (`carrier<i>`, Shafts order), each gear and copy
(`gear<index>` for a gear with no copies, `gear<index>c<k>` for copy k; index in Gears-sheet order). Each inserted,
placed at its frame and fixed, then unfixed immediately before its own mates (W5's sequence, `mated_train`).

Mates, every one a W5 kind (`AXIS`, `ALONG`, `LOCK`, `MESH`), named by `motion.mate_name`:

| What | Mate | Name |
|---|---|---|
| a turning carrier on its shaft | `coincident` `carrier1:C Axis` ~ `layout:C Axis` | `C carrier on C Axis` |
| … along it | `point` `carrier1:origin` ~ `layout:plane1` (always coincident: §2.6) | `C carrier along C` |
| a gear on the carrier's own shaft | `lock`, the carrier component as anchor (*reading J8*) | `G7 locked to C carrier` |
| each planet copy's anchor on its carrier axis | `coincident` `gear2c2:Gear Axis` ~ `carrier1:P copy 2 Axis` | `Planet copy 2 on P copy 2 Axis` |
| … along its shaft | `point distance` `gear2c2:origin` ~ `layout:plane1`, D1 linked to **one global per row**, `"Planet Face Z"`, shared by the copies (*reading J7*) | `Planet copy 2 along P copy 2` |
| a compound planet's second gear | `lock` to its copy's anchor | `Gear5 copy 2 locked to Planet copy 2` |
| frame shafts | as W5 | `Sun on S Axis`, `Sun along S` |
| gear mates | as W5, one per mesh that joins two bodies not yet joined | `Sun meshes Planet copy 1` |

`MatePlan` gains `on: str = ""`: the component holding the axis or plane the mate is made to (`""` the layout, else a
carrier id); `shaft` holds the axis stem (`"P copy 2"`), so the axis is always `f"{shaft} Axis"`. A **held carrier**
(Role fixed) is inserted, placed and fixed, never unfixed and never mated; its planets are mated to its axes as above.
A **held member** (the ring of the fixture) stays fixed as W5-PLAN D9 has it (*reading J6*).

**Which gear mates** (*reading J5*; W5-PLAN D6 generalised, review M13). A **body** is a frame shaft or one copy of a
mounted shaft. Union-find over bodies, with **every still body merged into one node, ground** (`motion.still_shafts`
decides still, as today; a held carrier is ground too), and the carrier never a node of its own. The expanded meshes,
in Meshes-sheet order and copy order: a mesh between two still gears is skipped (W5); a mesh whose two bodies are
already joined goes to `unmated` (it closes a loop); otherwise its bodies are joined and it gets a gear mate. W5's
rule "a mesh with a fixed gear gets no mate" is narrowed: a mesh between a still gear and a gear on a turning carrier's
planet **is** gear-mated (to the fixed component). For the fixture: `Sun meshes Planet copy 1`, `… copy 2`, `… copy 3`,
`Planet copy 1 meshes Ring`; unmated `Planet copy 2–Ring`, `Planet copy 3–Ring`.

*Why this count is right.* Once the axis and along mates are made, each turning body has one freedom (the sun, the
carrier, each copy: N + 2 with the ring held) and the train must keep one, so exactly N + 1 independent gear mates are
wanted; the union-find over bodies with ground merged gives a spanning tree of N + 1 edges on {ground, sun, copies}
here and, by the same count, in the sun-held and carrier-held cases (§4.2 pins both). A gear mate between a planet and
the sun constrains three bodies (the planet's axis rides the carrier), which is why the carrier is not a node: the
mates' graph never needs to reach it, and its freedom is taken by the first ring mate. The 2N − (N + 1) = N − 1 left
out are implied by the teeth (W3's kinematics: an inconsistent count is already "jammed"; the assembly condition makes
their phase agree). Making them would be redundant constraint, which SolidWorks has not been asked about and the fake
treats as over-defined (W5-PLAN §3.1). Alternatives (§3, J5).

**What the read-back must show** (the build's mate check, `swbuild._check_mates`, unchanged in rule): every planned
mate present, AddMate5 status 1, error code 0, not suppressed; every unfixed component — the sun, the carrier, every
copy — `COMPONENT_UNDER_DEFINED`; every gear mate read back by `_settle_sense` and remade with the other Flip when
wrong (the ring mate among them: no Flip is assumed, W5-DECISIONS on the ring), a mate wrong both ways a refused mate
that stops the build. The held ring reads fixed. No mate named for an unmated mesh, and the record lists it in
`unmated`.

`MotionPlan` gains `carriers: Tuple[str, ...] = ()` (carrier ids mated to turn); a held carrier's id joins `fixed`.
`trains` and `drag` are per train as W5; a train includes the carriers of its planets.

**"Drag the input"** (*reading J14*). The person drags the input's anchor gear in SolidWorks (the fixture: `Sun`): the
copies orbit and spin, the carrier's axes (shown when the user shows axes) turn with them, the ring stays. A carrier
has no face to grab, so when the input is a carrier with no gear of its own, the drag gear is the first gear of its
train that turns, and the footer says the carrier is axes and planes only. The API proof is the demonstration's
temporary driving mate, as in W5 (`DRAG_OPERATOR_TURNS_TRAIN` False).

### 2.8 Copies in the build, the record and Update

**One part file inserted N times** (PLAN's judgement call: "Identical gears share one part file … Planet copies rely
on this"; *reading J3*). `build.plan_parts` already makes one job per distinct part with its rows in `gear_ids`;
`plan_gearbox` makes one component per copy from it. SolidWorks names them `Planet-1`, `Planet-2`, `Planet-3`; the
record maps each **copy id to the Name2 SolidWorks kept** (`ComponentEntry`, never assumed from the order), as W4 does
for every component. Update finds each copy by that Name2, reads and puts its frame, and judges it in `train_check`
like any gear. A value change to the planet's part (teeth, module, face, bore) is one `update_variables` on the one
file, which every copy follows.

### 2.9 SolidWorks: the worker (`swbuild`) and COM (`swcom`)

- `build_gearbox(..., *, carriers=())`: each carrier part a `BuildPlan` to make or a `DocumentValues` to reuse
  (checked live like the layout), built **after the layout and before the assembly**; a failure skips the assembly
  (`skipped`), as a failed layout does. Pre-flight adds the carriers' paths to "made" and "reused" and to the paths the
  assembly may insert. `GearboxResult.carriers: List[BuildResult]`, `carriers_reused: List[str]`; progress
  `Step(STAGE_CARRIER, stem)`.
- `update_gearbox(..., *, carriers=())`: each carrier part's globals read in the check phase and set in the change
  phase after the layout's (`_update_values`, the same rules: a document already holding its values is not touched),
  so its axes move before the assembly rebuild. The mates then carry the copies (as `LAYOUT_MOVE_CARRIES_MATES` for a
  layout axis; unprobed for a carrier's, so the post-check is what tells), and the train is put back.
- **`train_check` with carriers** (pure, written in full in the interface commit with its tests, as W5's was): given
  `carriers: Sequence[CarrierLink]`, the carrier's own turn δ_c (its component's frame about its own Z) is read first;
  each planet's wanted frame is carried round the carrier's axis by `σ_c·δ_c` before its origin and axis are judged,
  and its δ is measured against that carried frame (its turn relative to the carrier); in a mesh whose `MeshLink.carrier`
  is set, a frame gear's δ is taken relative to the carrier, `δ − σ_g·σ_c·δ_c`; then `δ_b − k·δ_a` is a whole pitch of
  b as today, with `k` the tooth ratio `mesh_links` already makes (Willis is exactly this relation in the carrier's
  frame). A carrier's pitch is 0, so any carrier turn makes the train `turned`. With no carriers it is W5's function
  byte for byte.
- `_trains` joins a carrier to its planets; `_put_train` puts the **carrier first**, then every gear of the train, with
  the gear mates on (`MESH_PHASE_ROUTE`) and the locks suppressed around the puts (W5, M1, M8) (*reading J15*). A put
  of a component whose axis is mated to another free component is unprobed; `place_component` reads each frame back
  and the post-check reads every frame again, so a put that does not hold is a sentence, never silence.
- The mate check, the sense read-back, the constrained-status check and interference are unchanged. A carrier is a
  handle in a `Mate` op whose last `Fix`/`Unfix` is `Unfix`, so `_mated_handles` already includes it and it must read
  under-defined.
- **COM:** nothing new is expected. Every call W7's plans lead to is one W4 or W5 used: `NewPart` and `layout_plan`'s
  ops for the carrier part; `AddComponent`/`Place`/`Fix`/`Unfix` for it; `add_mate` coincident, point, point distance,
  lock and gear, with references `_component_ref` already resolves in any component by feature name. What is new is
  *combinations*: an axis mate between two free components (a copy to its carrier), a gear mate with one fixed
  component (a copy to the held ring), a lock with a bodiless component (only when a gear sits on the carrier's shaft),
  one part inserted four times. None is a hang, dialog or damage risk by anything W5's probes saw (AddMate5 reports
  over-definition by status, with no dialog: tier 8 `compound_lock`); the build shows each (§7).

**The fake** (package A, `tests/test_swbuild.py`): an axis mate whose target is in a component other than the layout
puts the gear's axis where that component's document globals (`"P copy 2 X"`, signed as `LAYOUT_NEGATED_LINK` says)
put it, transformed by that component's frame; a carrier with an axis mate to the layout goes to its axis like an
anchor, swung 13° the wrong way when its X/Y moved, and carries its planets (each also swung 13°, standing in for
SolidWorks); a gear mate that closes a cycle in the graph of **bodies with every fixed component merged into one**
is over-defined (status 5, code 46), so a plan that made a redundant planetary mate fails in the fake. As in W5 the
fake turns nothing by a gear mate: a test helper sets a consistent planetary turn from the kinematics (carrier δ_c,
each copy carried and turned).

**The kinematic fallback, not built unless needed** (§9, risk 1). If the first build's drive shows SolidWorks
measuring a gear mate's turns in the origin's frame rather than relative to a moving axis (so a planet riding the
carrier turns wrong under its tooth-ratio gear mates), the alternative route is a gear mate per extra freedom at the
**solved speed ratio** (each turning body to the input body, coaxial or not, ratio the exact `Fraction` from
`kinematics`). That route is written down here so the follow-up probe can compare the two; nothing builds it before
the build shows it is needed. If neither turns a planetary right, that is a STOP and ask (§3.2).

### 2.10 Update's classification for a planetary stage (`update.classify`)

| Edit | Class | How |
|---|---|---|
| any gear's teeth, module, face, bore … (the part's globals) | value Update | `update_variables` on the part (one file for every copy); a gear mate's ratio by the remake (`GEAR_MATE_RATIO_ROUTE` "remake"); a copy-1 planet carries two gear mates, so `IDLER_UPDATE_HOLDS` gates it as today |
| a planet's X, Y on its carrier, every copy staying on the same side of its carrier's base planes | value Update of the carrier part | its globals set (`UpdatePlan.carriers`), the train put back whole |
| a copy coordinate changing side, reaching or leaving 0 | structural | the carrier part's plane cannot follow (`OFFSET_GLOBAL_CROSSES_ZERO` False), as for the layout |
| a frame shaft's X, Y (the carrier, the sun, the ring) | move | the layout's globals; the mates carry the gears and the carrier; the train put back |
| a gear's At or face width (planets included: one `"Planet Face Z"`) | move | as W5; an anchor's front face reaching, leaving or crossing the Front plane is structural (W5-DECISIONS answer 3) |
| the carrier's Z | move | it offsets the planets' Z only (§2.6) |
| `Copies` changed (the number of planets) | structural | *"P now has 4 copies where it was built with 3, and Update SolidWorks cannot add or take out a planet, so the gearbox needs building again."* |
| `Mounted on` changed; a shaft becoming or ceasing to be a carrier | structural | *"P is now mounted on C2 where it was built on C, and its mates hold it to C's axes, …"* |
| the held member changes (a Role to or from fixed) | structural | W5's rule (`still_shafts` decides), sentence as W5 |
| a planet's or carrier's Axis flipped | structural | W5's rule |
| a mesh added or removed | structural | W4's rule |
| speeds, torques, efficiencies | nothing in SolidWorks | as W4 |

The record's mates are never re-derived (W5): a reordered Meshes sheet keeps the recorded gear mates and unmated list.
`classify` compares copies through `ComponentEntry.of` and the copy ids, so a planet row's components are not called
"new" or "no longer in the workbook" one by one; the `Copies` sentence says it once. `MotionUpdate` gains `carriers:
Tuple[CarrierLink, ...]`, and `MeshLink.carrier` is set for every recorded gear mate of a stage. Placements include the
carrier component (pitch 0).

### 2.11 The record (`store`, schema one past W6's)

`LINK_SCHEMA_VERSION` becomes one more than W6 leaves it (4 if W6 does not change it), so a W5- or W6-era build
refuses a W7 record and leaves it byte-identical, as W5-PLAN D11 did. Additive, defaulted:

```python
@dataclass
class CarrierEntry:                    # one carrier part of the current revision
    shaft: str = ""
    path: str = ""                     # <Name>_C_Carrier.SLDPRT
    component: str = ""                # its Name2 in the assembly
    rotation: List[float] = []         # its frame, as placed or last put
    at: List[float] = []
    sigma: int = 1
    axes: List[ShaftEntry] = []        # layout.CarrierLayout.axes, field for field
GearboxRecord += carriers: List[CarrierEntry] = []
ComponentEntry += of: str = ""         # the Gears row a copy is of ("" when the gear has no copies)
MateEntry += on: str = ""              # motion.MatePlan.on
```

The journal (`LinkRecord.pending`) gains a `PartEntry(kind="carrier")` per new carrier part, and a pending carrier
part on disk is reused once checked live, like a pending layout part. A refused train leaves the carrier parts saved
and on record, as W5's answer 1 leaves the layout part.

### 2.12 The sentences and the window

House style as W4 and W5: full sentences, the workbook's words, true in every state. C writes these in `ui_text`
(exact; `{…}` from fields):

- **Before Build** (`motion_ready_line`, appended): *"C is built as a carrier of axes and planes only, turning with
  Planet copy 1, Planet copy 2 and Planet copy 3; Ring stays fixed."* (a held carrier: *"C is built as axes and planes
  only, held fixed; its planets turn on it."*)
- **After Build** (`motion_done_line`): *"… drag Sun in SolidWorks and the rest of its train follow: the planets turn on
  C, and Ring stays fixed. C_Carrier holds C's axes and planes only: a plate and pins are yours to add."* The built
  list names the carrier part: *"Built 3 parts, Planetary_4to1_Layout, Planetary_4to1_C_Carrier and
  Planetary_4to1.SLDASM; …"*. The unmated meshes are logged (`mate    … left unmated: the others turn it as its teeth
  do`) and recorded, not said in the window (*reading J17*).
- **Update summary**: *"move the planets on C in Planetary_4to1_C_Carrier"*; *"move Planet (3 copies) along P"* for
  the shared Face Z (W5's *"move {G4} along {S3}"* per copy would list three).
- **After Update**: W5's pieces; a restored train lists the carrier as *"C (the carrier)"*.
- **Interference**: §2.3 item 6's undercut clause.
- **Speeds** (`workbook_speed_lines`): *"P  −500 rpm, −750 on C · 3 copies · clockwise seen from +Z"*; a held member
  *"R  held · 5.762 N·m"*. **Results** (`export.results_sheet`, B): a column *"On its carrier (rpm)"*, filled for
  mounted shafts; a held member's torque in Torque with *"held"* in a Notes column.

**The window** needs **no new control**. The end view (`preview.layout_gearbox`) draws every copy (it draws whatever
is placed) and the carrier as a dashed circle through its planets' axes, named at its cross. Boards (D):
`WorkbookPlanetary` (the fixture built, footer with the drag sentence) and `WorkbookPlanetaryCopies` (Copies 5: the
assembly-condition error and its list). `UI-DESIGN.md` §9 gains *"Planetary stages (W7)"*.

---

## 3. Readings the work proceeds with by default (to go to the user afterwards)

The user is away and has said to carry on through W8 without stopping. Each reading below is taken by default and
listed afterwards as one the user may overrule.

### 3.1 The readings

| # | Question | Options | Default, and why |
|---|---|---|---|
| J1 | How the carrier part's planet axes follow the workbook | (a) literal globals per copy, worked out by the app; (b) one global per planet row and SolidWorks equations with cos/sin | **(a)**: it is the layout part's proven pattern, Update sets globals the same way, and trigonometric equations in a part (units, `detect_trig_units`) have not been probed for planes. |
| J2 | Where the carrier part's origin sits along its axis | (a) on the layout's Front plane, always coincident; (b) at the carrier's Z, with a distance mate and a Face Z global | **(a)**: a skeleton has no thickness; (b) would bring W5's Front-plane structural rule to carriers for no geometry. |
| J3 | Copies as files and names | (a) one part file, N components, ids `Planet copy k` (`P copy k`), the row's own name when Copies = 1; (b) N files; (c) ids with `#k` | **(a)**: PLAN's judgement call; one Update changes every copy; a space cannot be in a workbook name, so no collision, and it reads well in the tree. |
| J4 | What a planet's typed X Y Z mean | (a) offsets along the origin's axes from the carrier's point, at its starting turn; (b) offsets in the carrier's own frame (turned over on Z-) | **(a)**: the carrier starts unturned, so (a) is (b) for Z+, and for Z- the user types what they see from +Z. Copies numbered the way the carrier turns positively. |
| J5 | Which gear mates of a planetary are made | (a) union-find over bodies, still bodies merged, carrier never a node, Meshes-sheet order expanded copy by copy (fixture: N sun mates and one ring mate); (b) all 2N; (c) (a) with external meshes before internal ones, so only one ring mate whatever the order | **(a)**: one freedom per train by count, nothing redundant, the same rule as W5's D6 and its order. (b) is redundant constraint SolidWorks has not been asked about. (c) would mean fewer ring mates (the Flip-prone kind) if the user lists Planet–Ring first, but changes W5's rule for every loop; offered to the user. |
| J6 | How a held member is held | (a) `Fix` (W5-PLAN D9); (b) mated to the layout and locked | **(a)**: what fixed means, as W5 builds it. |
| J7 | Planet copies along their shafts | (a) each copy's origin at a distance from the layout's Front plane, one Face Z global per row shared by the copies; (b) to the carrier part's Front plane; (c) a global per copy | **(a)**: reuses W5's along mate, Update sets one global for every copy. |
| J8 | A gear on the carrier's own shaft | (a) locked to the carrier skeleton, which is that shaft's anchor; (b) refused | **(a)**: an output gear on the carrier is ordinary, and a lock is W5's proven way to hold two bodies together. |
| J9 | Planetary checks | assembly condition and neighbours as **errors**; a shifted planet in a ring an error; no fix offered for a planetary centre error | A build that cannot mesh is not worth making; the clash the ring probe saw is certain for a planet. HANDOFF question 2 (parallel trains) stays open. |
| J10 | Torque through a planetary | (a) basic-train efficiency, one held member, joined to W3's walk; (b) ideal torques only; (c) none | **(a)**: the textbook method, honest about losses, pinned by numbers; anything it does not cover says so. |
| J11 | A stage with no member held and two inputs (a differential) | (a) built with its two freedoms, the footer naming both inputs; (b) refused | **(a)**: the kinematics settle it and the mates follow by the same count; no fixture shows it on SolidWorks, which the handoff will say. |
| J12 | Compound (stepped) and double planets | (a) built by the same machinery (locks per copy, planet–planet meshes on one carrier), the copies required to need the same relative turn between their gears; (b) refused | **(a)**, untested on SolidWorks; locks and gear mates are W5's. |
| J13 | Nested carriers, planetaries on turned axes, planets not parallel to their carrier | refused at Build with §1.2's sentences | No phase builds them; they need W6 and W7 together. |
| J14 | What to drag | the input's anchor; a carrier input with no gear: the first turning gear of its train | A skeleton has nothing to grab. |
| J15 | Update's put of a planetary train | the whole train back at its built turn, carrier first (W5 answer 2 and M1 carried over) | The user's W5 answer, applied to the carrier as to any body of the train. |
| J16 | The record | schema one past W6's; `CarrierEntry`, `ComponentEntry.of`, `MateEntry.on` | As W5-PLAN D11. |
| J17 | Saying the unmated meshes | in the log and the record, not in the window | The window's sentences are long already, and an unmated mesh needs nothing of the user. |
| J18 | Planet speeds | absolute about its own axis, and relative to its carrier beside it | Both are asked for by someone; the absolute one keeps the column's meaning. |
| J19 | Undercut | not modelled; the fixture avoids it; one clause on the interference sentence | Honest and cheap; modelling the trochoid is a strip change outside W7. |
| J20 | Gating the planetary build on a finding | no new finding gates the first build; once the demonstration has measured a planetary turning right, `findings.PLANET_GEAR_MATE_ROUTE = "teeth"` is committed with that evidence and `motion_reason` reads it for a plan with carriers | A gate before any evidence would block the full build the user wants first; committing it after keeps a later SolidWorks version from changing the behaviour unseen. |

### 3.2 What cannot proceed without the user

Nothing, as planned. One branch would: if the first full build shows the planets turning wrong under tooth-ratio gear
mates **and** the follow-up probe finds the kinematic route of §2.9 wrong too, no turning planetary can be built from
what the probes know. That is a STOP and ask (whether to build planetaries static, as W5's static-by-necessity path
would, or to wait). Everything else in W7 proceeds by the defaults above.

---

## 4. The fixtures

### 4.1 `Planetary_4to1` — the ring held (PLAN §6)

Box: Name `Planetary_4to1`, Pressure angle 20, Efficiency 98. Shafts as in §2.1. Gears (spur, involute, module 1,
face 10, At 10, so every front face is at z = 5 and every anchor gets a Face Z global — no Front-plane structural
case in the demonstration's edits):

| Gear | Shaft | Side | Teeth | Bore | Part name |
|---|---|---|---|---|---|
| Sun | S | external | 18 | 6 | Sun |
| Planet | P | external | 18 | 8 | Planet |
| Ring | R | internal | 54 | — | (default) |

Sun and Planet differ in bore, so they are two parts; their Part names keep their file names apart (the default stem
would be the same). Meshes: `Sun–Planet`, `Planet–Ring`. Three parts, the layout part, `Planetary_4to1_C_Carrier`,
the assembly. A reviewer can recompute every number below from these rows (computed here with the app's own
`geometry.external_space` / `ring_space`; script kept in the planning session's scratchpad, not committed).

- **Checks:** `z_r = 18 + 2·18 = 54` ✓; centres `m(z_s + z_p)/2 = 18 = m(z_r − z_p)/2` ✓; assembly
  `(18 + 54)/3 = 24` ✓; neighbours `2·18·sin 60° = 31.177 mm` > tip diameter 20 + 0.5 ✓; Sun and Planet 18 teeth,
  above the undercut limit 17.1. Copies that pass both: 2, 3, 4 (6 divides 72 but stands 18.000 mm apart).
- **Positions** (mid-face z = 10, front face z = 5): Sun (0, 0); Planet copy 1 (18, 0); copy 2 (−9, 15.588457268);
  copy 3 (−9, −15.588457268); Ring (0, 0); carrier origin (0, 0, 0).
- **Phases** (θ about each part's own +Z): Sun 0; every Planet copy 10° (= `2ψ_k + 170°` mod 20°); Ring 0 modulo its
  pitch 6.6667°, the same from all three copies. Frames: Sun I at (0, 0, 5); copy k `rot_z(10°)` at its centre, z 5;
  Ring I at (0, 0, 5); carrier I at (0, 0, 0).
- **Carrier part:** `C Axis` (base planes); `P copy 1 X Plane` 18 from Right, `P copy 1 Axis` with Top; copy 2: X −9
  (minus side), Y 15.588457268; copy 3: X −9, Y −15.588457268; globals `P copy 1 X`, `P copy 2 X`, `P copy 2 Y`,
  `P copy 3 X`, `P copy 3 Y` (signed as `LAYOUT_NEGATED_LINK` makes `layout_globals` write them).
- **Speeds** (rpm, about each shaft's own axis): S 1000, C 250, P −500 (−750 on C), R 0. Overall **4.000 : 1**, the
  output turning the same way. Check: `(1000 − 250)·18 = 13500 = −(−750)·18`; `(−750)·18 = −13500 = (0 − 250)·54`.
- **Torques:** S 2.000; C 7.7624 (η₀ 0.9604, stage 97.03 %); R held 5.7624; P 0.
- **Mates:** `Sun on S Axis`, `Sun along S` (`Sun Face Z` 5), `C carrier on C Axis`, `C carrier along C`, per copy
  `Planet copy k on P copy k Axis` and `Planet copy k along P copy k` (`Planet Face Z` 5), gear mates `Sun meshes Planet
  copy 1`, `… copy 2`, `… copy 3`, `Planet copy 1 meshes Ring`; unmated `Planet copy 2–Ring`, `Planet copy 3–Ring`;
  fixed `Ring`. 14 mates, 7 components.
- **A 30° drive of the sun:** carrier +7.5°; each copy's own turn −15° (−22.5° relative to C); Ring 0; copy origins
  at (17.846008, 2.349471), (−10.957706, 14.280360), (−6.888302, −16.629832), z unchanged. The unmated meshes stay in
  step: `(−22.5)·18 = −405 = (0 − 7.5)·54`.

### 4.2 `Planetary_4to1` with the sun held — a different fixed member

The same workbook with two Role edits: S `fixed` (Speed and Torque cleared), R `input`, 1000 rpm, 2 N·m. It is made
by an Excel edit in the demonstration (a structural change: Build again… makes `_r2`), and as a spec in the tests.

- **Phases:** the walk starts at Ring (θ 0); every copy 10° (`pinion_space`); Sun 0 from every copy — the same frames
  as §4.1.
- **Speeds:** R 1000, C 750, P 1500 (+750 on C), S 0; **1.333 : 1**, same way.
- **Torques:** R 2.000; C 2.6403 (stage 99.01 %); S held 0.6403; P 0.
- **Mates:** ground is {Sun}: gear mates `Sun meshes Planet copy 1/2/3` (each to the fixed sun) and `Planet copy 1
  meshes Ring`; unmated `Planet copy 2–Ring`, `Planet copy 3–Ring`; the Ring turns, so `Ring on R Axis` and `Ring along
  R` are made and `Sun` is fixed.
- **A 30° drive of the ring:** carrier +22.5°, each copy's own turn +45° (+22.5° on C), Sun 0.

It exercises what §4.1 does not: gear mates to a held external gear, a turning ring whose gear mate is read back
inside a loop, and a planetary input on a ring.

The carrier-held case (`−3.000 : 1`) needs no fixture of its own: its gear-mate set is pinned by a made-up spec in B's
tests (ground {carrier}: `Sun meshes Planet copy 1/2/3`, `Planet copy 1 meshes Ring`).

Tests also pin, by made-up specs: Copies 5 (assembly error, the list 2, 3, 4), Copies 6 (neighbour error, "4 is the
most"), Ring 56 (the `z_r` sentence), a +0.3 shifted Planet (the shifted-planet error), a Z- carrier (copies clockwise
from +Z, local y negated), a planet on Z- on a Z+ carrier, a gear on the carrier's shaft (locked to the carrier), a
compound planet, and a no-member-held stage (§2.3 item 4).

---

## 5. Work packages, files and the shared shapes

### 5.1 Order

```
W6 closed ──► I (interface commit) ──► A (SolidWorks side) ─┐
                                       B (planning)       ──┼──► D (window, boards, docs) ──► E (demonstration)
                                       C (record, words)  ──┘
              E0 (the one probe ahead, §7) ─────────────────────────────────────────────────┘
```

An independent review after I, after each of A–D, and after E's runs, as before. E0 may run any time before E.

### 5.2 Who edits what

| Package | May edit |
|---|---|
| I | everything under §5.3, once, then hands over; `docs/notes-workbook/W7-INTERFACES.md` |
| A — SolidWorks | `swcom.py`, `swbuild.py`, `tests/test_swbuild.py` (the fake), `tests/test_swcom.py`; may add to `tests/test_swbuild_train.py`, never change an assertion there |
| B — planning | `workbook/planetary.py` (new), `geometry.py`, `kinematics.py`, `checks.py`, `assess.py`, `build.py`, `model.py`, `layout.py`, `motion.py`, `gearbox.py`, `update.py`, `export.py`; `tests/test_workbook_{planetary,geometry,kinematics,checks,model,layout,motion,gearbox,update,export,demo_fixtures}.py`, `tests/test_probe_workbook.py` |
| C — record, words | `store.py`, `ui_text.py`, `tests/test_store.py`, `tests/test_ui_text.py` |
| D — window, boards, docs | `workbook_gui.py`, `preview.py`, `tests/test_preview.py`, `tests/test_workbook_{build,window}.py`, `design/**`, `docs/**`, `README.md` |
| E0, E — probes and demonstration | `probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, a new `probe/copied_folder_check.py`, `probe/results/**`, `tests/fixtures/excel-windows/Planetary_4to1.xlsx`; after E's first 2026 run, `findings.py` and `tests/test_findings.py` for J20's finding only |
| nobody | `gears/*.py` |

B owns `geometry`, `kinematics` and `checks` in W7 (W5 left them to nobody): W6 will have changed them, and W7 starts
on its closing commit, so only W7's B touches them during W7.

### 5.3 The interface commit (I)

Starts on the commit that closes W6 (named in `W7-INTERFACES.md`). Shapes only, except where marked **written**; a
change to a pinned shape after it is a stop-and-ask; private helpers and keyword-only parameters with defaults are
free.

`swbuild.py` (shared by A and B):

```python
@dataclass(frozen=True)
class CarrierLink:
    carrier: str                          # the carrier's component id, layout.carrier_id(shaft): "C carrier"
    planets: Tuple[str, ...]              # gear ids (copy ids) whose axes ride it, in plan order
    point: Tuple[float, float, float]     # its origin as placed, mm (on the Front plane: z 0)
    sigma: int                            # +1 its own +Z along global +Z, -1 along -Z
MeshLink(a, b, k, pitch, carrier: str = "")   # carrier: a CarrierLink.carrier the mesh is measured against
def train_check(found, wanted, meshes, locks, pitch, tolerance=TRAIN_TOLERANCE, *,
                carriers: Sequence[CarrierLink] = ()) -> TrainCheck          # WRITTEN, with tests (§2.9)
MotionUpdate.carriers: Tuple[CarrierLink, ...] = ()
STAGE_CARRIER = "carrier"
GearboxResult.carriers: List[BuildResult] = []; GearboxResult.carriers_reused: List[str] = []
def build_gearbox(..., *, carriers: Sequence[Union[BuildPlan, DocumentValues]] = (), ...)   # body: A
def update_gearbox(..., *, carriers: Sequence[DocumentValues] = (), ...)                    # body: A
```

`workbook/planetary.py` (new): `copy_id`, `copy_offsets` **written** with tests; `Stage(carrier: str, suns:
Tuple[str, ...], rings: Tuple[str, ...], planets: Tuple[str, ...], planet_shafts: Tuple[str, ...], copies: Mapping[str,
int], held: str, simple: bool)` (`held`: the member shaft whose Role is fixed, or `""`; `simple`: one sun, one ring, one
planet gear per copy); stubs `stages(spec, placed) -> Tuple[Stage, ...]`, `assembly_counts(z_sun, z_ring, max_copies)
-> Tuple[int, ...]`, `mesh_carrier(spec, a, b) -> Optional[str]` (`"frame"`, a carrier shaft, or None: fits none).

`geometry.py`: `Placed.row: str = ""`, `Placed.copy: int = 0`, `Placed.carrier: str = ""`; stub `expand_meshes(spec,
placed) -> Tuple[Tuple[str, str], ...]`.
`kinematics.py`: `Motion.relative: Dict[str, Fraction]`, `Motion.held: Dict[str, float]`, `Motion.torque_note: str = ""`.
`checks.py`: `Report.stages: Tuple[planetary.Stage, ...] = ()`.
`layout.py`: `CARRIER_KIND`, `CARRIER_SUFFIX = "_Carrier"`, `CARRIER_HANDLE`, `CarrierLayout`, stubs `carrier_id`,
`carrier_stem`, `carrier_layouts`, `carrier_frame`, `carrier_plan`.
`motion.py`: `MatePlan.on: str = ""`; `MotionPlan.carriers: Tuple[str, ...] = ()`; `mesh_links(..., *, carrier_of:
Mapping[Tuple[str, str], str] = {})` (sets `MeshLink.carrier`); stub `carrier_links(spec, report, plan) ->
Tuple[CarrierLink, ...]`.
`gearbox.py`: `GearboxPlan.carriers: Tuple[Union[BuildPlan, CarrierReuse], ...] = ()`, `GearboxPlan.carrier_paths:
Mapping[str, str] = {}` (shaft → path), `GearboxPlan.carrier_layouts: Tuple[CarrierLayout, ...] = ()`; `CarrierReuse(path,
variables, features, journaled=False)`; `build_kwargs()` adds `"carriers"` **only when non-empty**, so a W5 plan's call
is key for key what it was.
`update.py`: `UpdatePlan.carriers: Tuple[DocumentValues, ...] = ()`, `UpdatePlan.carriers_moved: Tuple[str, ...] = ()`;
`update_kwargs()` adds `"carriers"` only when non-empty.
`store.py`: §2.11's shapes, the schema number, the parse (C fills the refusals: a `CarrierEntry` with no shaft or
path, an `on` naming no carrier on record, are `StoreError` sentences).
`ui_text.py`: stub helpers `carrier_phrase(record_or_plan) -> str`, `copies_phrase(row, n) -> str`,
`planetary_speed_line(...)`.

**Done:** the suite green but for stubs nobody calls; `train_check`'s carrier tests pass (a planetary turned
consistently is in step and `turned`; one copy turned alone is out of step; a copy carried but not turned relative to
the carrier is out of step with the sun; a copy off its carried place is `off_axis`; Z- carrier and opposite-facing
planet signs; no carriers → W5's results unchanged, every existing test of `test_swbuild_train.py` untouched).

### 5.4 A — SolidWorks side

§2.9: `build_gearbox` carriers step, pre-flight, progress, log lines (`ok      carrier Planetary_4to1_C_Carrier
built` / `reused`); `update_gearbox` carriers in the values phase; `_trains` with carrier links; `_put_train` carrier
first; `train_check` already written; the fake (§2.9). **Done (against the fake):** a planetary build makes carrier
part then assembly, saves once, every mate status read, the carrier and copies read under-defined, the ring fixed; a
plan doctored to add `Planet copy 2 meshes Ring` is over-defined → refused (W5 answer 1), carrier part and layout kept
and recorded; a carrier part that fails skips the assembly; a reused carrier checked live, a mismatched one stops the
job with nothing made; Update: a consistent planetary turn → nothing put, `turned`; a carrier globals change → the
carrier part updated, rebuild, the fake's swing put right, carrier put first, post-check clean; one copy turned alone →
out of step → the whole train put; a W5 train's calls byte for byte as before.

### 5.5 B — planning

§2.1–§2.8, §2.10 and the Results column. **Done (pure):** the §4 numbers pinned (positions, phases, frames, speeds
incl. `relative`, torques incl. `held`, the carrier part's ops and globals, the mates and unmated of §4.1 and §4.2 and
the carrier-held spec, ids and handles, the `motion_assembly_plan` op order golden list for §4.1 with `check() ==
[]`); every check of §2.3 with its sentence; every row of §2.10 with its sentence; W5's fixtures' plans unchanged
(their golden lists pass untouched); `classify` and `finish_update` round trips on the fake once A lands (B's second
pass, as W5's).

### 5.6 C — record and words

§2.11, §2.12. **Done:** every new sentence filled from fields in a test; schema read of the previous version as the
new one, round trip byte-deterministic, a newer one refused and untouched; the new `StoreError`s.

### 5.7 D — window, boards, docs

`workbook_gui` passes the new fields (no new control); `preview.layout_gearbox` draws copies and the carrier's circle;
the two boards drawn and looked at; `UI-DESIGN.md` §9; PLAN-WORKBOOK: a dated note under §3.3/§3.5/§4.2 (*Readings
chosen (W7)*, §3's defaults), §6's W7 row; HANDOFF. **Done:** the window launched on §4.1 against the fake, footer
read in each state; Windows Tk tests green.

### 5.8 E — the demonstration on SolidWorks

§6. **Done:** logs committed, 0 failed, for 2026 in full and for 2024's confirming run; the person's step handed over.

---

## 6. The demonstration (package E), full build first

New sections in `probe/workbook_assembly_check.py`, `--only planetary` running them; default order adds them after
W5's. Through the app's own code as W5's sections go (`plan_gearbox` → `build_gearbox(**build_kwargs())` →
`finish_build`; `classify` → `update_gearbox` → `finish_update`; every footer sentence logged), Excel edits by the
script's own Excel, no user titles.

**Build once, copy after** (the rule HANDOFF carries over). Section `p1` builds `Planetary_4to1` once and saves it
into a master folder; each later section copies that folder, unless a fresh build is the point. The record holds
absolute paths and the assembly references its parts by path, so the copy protocol is: every document of the master
closed (`QuitDoc`, the CAM add-in's box answered No as now); the folder copied; in the copy, the `.workbook.json`'s
paths and each `.gear.json`'s `workbook` rewritten to the copy (with `store`'s own load and save); the master folder
renamed aside while the copy is in use, so SolidWorks cannot resolve a reference to it; the copy's assembly opened and
**every component's path read and asserted to lie in the copy's folder** before anything is changed (else STOP:
nothing is changed in either folder); the master renamed back when the section ends. E0 (§7) shows the protocol holds
before E depends on it. The copy function is reviewed like app code.

Measurements, all from SolidWorks' own readings:

- **§4.1 of W5, extended** (every build): every component's frame (`Transform2`) against `layout.frames` to 1e-6,
  copies and carrier included; the carrier part's axes read in its document (`GetRefAxisParams`) and carried into the
  assembly by the carrier component's transform: each copy's axis through its copy's centre, reading +Z; the mates
  exactly the record's names, codes 0, none suppressed; Sun, carrier and every copy `GetConstrainedStatus` 2, Ring
  `IsFixed`; no mate for an unmated mesh. **Interference controls per copy:** `Planet copy k` turned half its pitch (a
  put with its gear mates on) must clash with exactly Sun and Ring, and nothing else, for each k (so every mesh, unmated
  ones included, is shown to bite); put back, none again. Saved, closed, reopened: the same.
- **§4.2 of W5, the driven proof:** a temporary angle mate from the input anchor's Top plane to the layout's Right
  plane at 90°, `"Drive"` 90 → 120, top-only rebuild. Against `kinematics.solve` (§4.1's numbers): Sun +30°, the
  carrier's own turn +7.5°, each copy's own turn −15°, each copy's origin carried to §4.1's positions to 1e-6 mm,
  Ring unmoved; the unmated meshes in step (relation residual ≤ 1e-6 rad, by the same arithmetic `train_check` uses).
  **Wrong-sense control:** `Sun meshes Planet copy 1` suppressed and a temporary gear mate with the other Flip in its
  place: the comparison must see the carrier or a copy turning wrong. Then M12's hygiene: Drive back to 90, the control
  deleted and the recorded mate back on, the drive deleted, every frame back at the built frames, and before any save
  no Drive, angle or control mate left and nothing suppressed.

Sections:

- **`p1` — build `Planetary_4to1` (ring held).** Fresh build. §4.1, §4.2, reopen. The marks after a build (no part,
  layout or carrier part marked; the assembly marked). Kept as the master folder. The fixture saved by Excel and
  copied to `tests/fixtures/excel-windows/Planetary_4to1.xlsx` (`keep_fixture`).
- **`p2` — the user's turn and a quiet Update** (copy of `p1`). Drive 37° and delete the drive; Update with nothing
  changed: nothing put, nothing changed, *"… The gears stand where they were turned in SolidWorks."*; `train_check`'s
  residuals with the carrier link logged; every frame before and after the press equal to 1e-6; no document marked.
- **`p3` — moves and values** (copy of `p1`). Excel `Planet` At 10 → 12 → Update: `"Planet Face Z"` set once, the
  three copies moved, the whole train put back (carrier first), frames, drive. Then Module 1 → 1.25 on all three gears
  with P's X 18 → 22.5 → Update: three parts' values, the carrier part's globals (copies at (22.5, 0),
  (−11.25, 19.485571585), (−11.25, −19.485571585)), the mates carry the copies (the swing logged), the train put back,
  frames against the new `layout.frames`, interference and its controls, drive at the same 4 : 1, reopen.
- **`p4` — the number of planets** (copy of `p1`). Excel Copies 3 → 5: the Checks error and its list logged, Build
  and Update not offered. Copies 6: the neighbour error logged. Copies 4: the structural sentence, Build again… makes
  `Planetary_4to1_r2` with four copies of the one Planet part (copy 2 on the carrier's Right base plane: a base-side
  copy), §4.1, §4.2 (copies at 0°, 90°, 180°, 270°, each θ 10°), every earlier file's sha256 and mtime unchanged.
- **`p5` — the sun held** (copy of `p1`). The two Role edits of §4.2 → the structural sentence (a member starts and
  one ceases to be held) → Build again… makes `_r2`: §4.1, §4.2 driving the **ring** (its Top plane to the layout's
  Right plane), the control on `Planet copy 1 meshes Ring`, reopen. Fresh in substance (another fixture) but from a
  copy.
- **window** (`workbook_window_check.py`, 2026): screenshots of the built planetary footer and end view (three copies,
  the carrier circle) and of the Copies 5 error.

**SolidWorks 2024, the confirming run:** `p1` and `p5` (the ring mates: where the two versions have differed), E0's
check, and the window check. **The person's step** (2026, then 2024): *open `Planetary_4to1.SLDASM` from the log's
folder, drag Sun round its axis by about a quarter turn, and watch the three planets: they roll round inside the ring
the same way as Sun, about a quarter as fast, each spinning the other way on its own axis; the ring does not move.
Then press Update SolidWorks with nothing changed: the footer should say the gears stand where they were turned.*

---

## 7. Calls not used before that could hang, raise a dialog, or damage a file or a session

Only one, and it is the demonstration's, not the app's: **opening an assembly from a copied folder while the
folder its references were saved with is renamed aside** (`OpenDoc6`, silent, as `swcom.open_document` calls it).
SolidWorks resolves missing references by its own search rules (documents in memory, paths used in the session, the
referencing document's folder, the saved path); if it resolves to the master folder, an Update in the copy would
change the master's parts (damage), and a reference it cannot find at all may ask the user to browse for it (a
dialog, which `Silent` is meant to suppress). **Probe E0** (`probe/copied_folder_check.py`, on 2026 before E, again
first in 2024's run): build nothing; take a built W5 12 : 1 folder from a committed run's layout (or build one), close
everything, copy it, rename the original aside, open the copy's assembly under a dialog watcher (`press_dont_save`'s
pattern): no dialog; every component's `GetPathName` in the copy; `GetSaveFlag` read after the open (if True, the
marks checks of §6 in copied sections expect the assembly marked from the open, and the log says so); close with
`QuitDoc`, the copy's files byte-identical, the original folder's files byte-identical after it is renamed back. If a
dialog appears or a path resolves to the original, E builds every section fresh (W5's way) and the copy protocol is
dropped, recorded in the handoff.

Everything the **app** calls in W7 has been called before (§2.9, COM). The new combinations — an axis mate between two
free components, a gear mate to a fixed component, a lock with a bodiless component, a part inserted four times, a
put on a component another free component is mated to — are not of the three kinds: SolidWorks answers a bad mate by
status and error code, with no dialog (tier 8), and a put that does not hold raises in `place_component`'s read-back.
They are what the full build shows; what it gets wrong is the follow-up probe round's.

---

## 8. Definition of done, and the order of work

1. W6 closed; this plan reviewed by an independent Opus subagent and its points ruled on (a `W7-DECISIONS.md`).
2. I committed and reviewed; `W7-INTERFACES.md` names the starting commit.
3. A, B, C in parallel; each reviewed; fixes in. B's second pass (the round trips on the fake). D after; reviewed.
   Suite green on a clean `git archive` (`PYTHONPATH=src .venv/bin/python -m pytest -q`), and the Windows Tk tests
   (`python.exe -m pytest tests/test_workbook_build.py tests/test_workbook_window.py -q`).
4. E0 on 2026. E's full run on 2026 (`p1`–`p5`, window). What fails is probed in **one** follow-up round (the first
   candidate: the planets' turn under tooth-ratio gear mates, §2.9's fallback compared), fixed, and only the affected
   sections rerun; then one full run at the phase's close. J20's finding committed from that run's evidence.
5. SolidWorks 2024: E0, `p1`, `p5`, window; what fails there fixed then.
6. The person's drag on both versions; the result recorded.
7. HANDOFF's W7 row closed, with what was left open and §3's readings listed for the user.

PLAN-WORKBOOK §6's demonstrable — *"A 4 : 1 planetary with the ring fixed builds"* — is `p1`'s build, measured, and
driven at 4 : 1 the right way.

---

## 9. Risks, and what reading could not determine

1. **How SolidWorks measures a gear mate whose axis rides a moving component** (the riskiest point). The tooth-ratio
   gear mates are right only if SolidWorks relates the two gears' turns relative to each other as the axes move (then
   Willis holds in the carrier's frame, as `train_check` and the kinematics assume). If it relates turns in the
   origin's frame, a planet's ring mate to a held ring would hold the planet from spinning, and the train would jam
   or turn wrong. Nothing in the code or the probe record says which; tier 8 drove only frame shafts. The first build's
   drive in `p1` answers it; §2.9's kinematic route is the candidate if it fails; §3.2 is the STOP if both fail.
2. **Puts on a carrier train.** Update puts the carrier and then each copy with the gear mates and the copy-to-carrier
   axis mates on; whether each put holds while the next is made, and whether a carrier put drags the copies through
   the solver, is unprobed. `place_component`'s read-back and the post-check make a failure a sentence; `p3` shows it.
3. **SolidWorks' swing on a carrier move.** On a layout move SolidWorks swings mated gears' phase the wrong way (tier
   8); a carrier part's axes moving (p3's module edit) may swing the copies too, which Update puts right if the puts
   hold.
4. **Three coincident axes in the layout part** (S, C, R through the same two base planes). W4 made one axis at the
   origin per layout, never two on one line. Expected harmless; the build shows it.
5. **The ring's Flip** with the ring held (a gear mate to a fixed component) and with the ring turning in a loop
   (`p5`): no Flip is assumed and every gear mate is read back (W5-DECISIONS), so a wrong one is remade; a mate wrong
   both ways stops the build as a refused mate.
6. **A skeleton's constrained status and the lock with a bodiless part** have not been read on SolidWorks; the
   layout part is bodiless but always fixed. The mate check tells.
7. **W6's changes underneath.** W7 edits `geometry`, `kinematics`, `checks`, `layout`, `motion` after W6 has; if W6
   changes kinematics to a vector projection or adds mate kinds, B adapts the carrier term and the new fields to it
   (§5). W7 assumes of W6 only: the linear system in `Fraction`s with one unknown per shaft; `later_rows` still
   refusing mounted shafts until W7; `MateEntry.kind` an open list; the record's schema number W6 leaves.
   Combinations (a planetary on a turned axis, a bevel differential) are refused (§1.2), so W7 does not depend on W6's
   new geometry at all.
8. **The demonstration's copy protocol** (§7): if SolidWorks resolves references to the master, every copied section
   is built fresh instead; time rather than correctness.
9. **Two-input planetaries, compound and double planets** (J11, J12) are built by the same rules but no fixture shows
   them on SolidWorks; the handoff says so.
10. **Memory and time on 2024:** 7 components and 14 mates per build, below W5's Risky_Placements; the guard stays.
11. **Not determined from reading:** the full text of every `ui_text` footer state a planetary record passes through
    (C reads them all); whether `export.results_sheet` has room for a Notes column without breaking the Results
    sheet's tests (B); whether `store`'s `_entries` parse handles a nested list of `ShaftEntry` inside a new entry
    type without change (C); how `probe/workbook_assembly_check.py`'s `drive_job` reads a component's origin (it must
    compare carried origins, not unchanged ones, for copies).
