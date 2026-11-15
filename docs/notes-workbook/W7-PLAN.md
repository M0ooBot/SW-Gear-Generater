# W7 (planetary): the implementation plan

**Authority and reading order.** `docs/PLAN-WORKBOOK.md` (§1, §3.3, §3.5, §4.2–§4.5, §6) is the authority, then
`W5-DECISIONS.md` (its rulings carry over unless this plan says otherwise), then this plan. The user's answer of
2026-11-14 recorded in `docs/HANDOFF-WORKBOOK.md` ("Answered ahead of its phase") settles what stands for a carrier
in SolidWorks: **a skeleton only**, a part of axes and planes with no solid, as the layout part is, free to turn
about its own shaft's axis, each planet mated to an axis in it; the app makes no plate and no pins. W5's plan
(`W5-PLAN.md`), its review and `W5-INTERFACES.md` are the model for this plan's shape.

*Revised 2026-11-14* after the independent review (`W7-PLAN-REVIEW.md`, `939b726`) and the spike that measured the
plan's riskiest point on SolidWorks 2026 (`W7-SPIKE.md`, `8a798fe`; results `probe/results/w7-spike-20261114-192709.*`),
with the orchestrator's rulings. §10 lists every change, item by item.

W7 starts **after W6 closes** (W6, turned axes and bevel meshes, revised in `W6-PLAN.md` at `eb195d0`, is built
first). W7's shared shapes use W6's names (§5.3), and §9 says what W7 assumes of W6.

Rules carried over unchanged (HANDOFF, "Rules carried over"): commits by explicit path, prose messages with the why,
no Claude co-author or attribution line, never `add -A` / `commit -a` / stash / reset / rebase; the orchestrating
session pushes, subagents commit only; findings only from committed `findings.py`, read with `getattr(findings,
NAME, None)`, a missing one refusing with a sentence; every raise a full sentence; the repo is public (no user
document titles in committed logs). **Testing (the user, 2026-11-14):** the phase is written against the fake and
then built end to end on SolidWorks 2026 early; what that build gets wrong is probed step by step; probing ahead is
kept only for a call not used before that could hang, raise a dialog, or damage a file or a session (§7). SolidWorks
2024 gets one confirming build at the phase's end. One follow-up probe round per phase. An Opus subagent reviews the
plan, the interface commit and each package before the next step.

**One principle of scope (the orchestrator's ruling on J11/J12, applied throughout):** W7 builds only what its
demonstration builds and measures on SolidWorks. Everything else that reads as a planetary is refused at Build with
a sentence (§1.2) and listed for the user as something a later pass could open (§3.2).

---

## 1. Scope

### 1.1 What W7 adds (PLAN-WORKBOOK §6: "Carriers, copies, loops in kinematics and phases — A 4 : 1 planetary with
the ring fixed builds")

- **Carriers**: a shaft row that other shafts are `Mounted on` (§1, Shafts). It is laid out, checked, solved and
  built: in SolidWorks as a skeleton part that turns about its own axis, or is held.
- **Copies**: a mounted shaft's `Copies` (§1: "that many, evenly round it"), with its gear, placed, phased, checked
  and built as that many components of one part file.
- **Loops in kinematics**: the mesh equation with its carrier term (§3.5), a planetary's Willis relation; torques
  through a planetary stage (§3.5: "Loops wait for W7").
- **Loops in phases**: each planet copy and the ring placed so their teeth mesh at every copy at once; a loop that
  does not close is the assembly condition failing (§3.3), an error.
- **Loops in mates**: the gear mates of a planetary over-determine the motion; which are made and which are left out
  (W5-PLAN D6's `unmated` hook, review M13). Measured right on SolidWorks 2026 by the spike (§2.7).
- **Update SolidWorks** on a planetary stage: values, moves (the carrier part's globals among them), a turned
  carrier put back, and the structural cases.

**What W7 builds**, exactly: a workbook with **one simple planetary stage** — one sun, one ring, one planet gear on a
planet shaft with any number of copies, all spur, every shaft of the stage facing the carrier's way along Z+ or Z-,
**exactly one member held** (sun, ring or carrier) and one input. Beside the stage's own gears:

- **more gears on the sun's or the ring's shaft**: ordinary W5 — the first gear on the shaft is its anchor and every
  other is locked to it; they may mesh other frame gears by W5's rules (on a held ring's shaft they are held too,
  W5-PLAN D9);
- **gears on the carrier's own shaft**, each **locked to the carrier skeleton** (*reading J8*, restored; §2.7), meshing
  nothing (a carrier gear on Meshes is refused, §1.2); on a held carrier they are held;
- **other frame shafts on the carrier's axis** (coaxial, not members of the stage) with their own gears and W5/W6
  trains: built as any frame shaft, with the coaxial exemptions of §2.3 item 5.

That is what W8's E4 transfer case asks of W7 (`W8-PLAN.md` §0.2 and §2.1, `9e1937f`): `InDog` locked to `Sun` on In,
`LoDog` on the Carrier's own shaft locked to the carrier, and Rear and FrontDrv as further frame shafts on the
carrier's axis, every axis Z+, one stage (§10, "After the W8 check"). §6 demonstrates the ring held with a gear on the
carrier, the sun held, the carrier held, a Z- stage, Copies 4, and Update's values, moves and puts on it.

### 1.2 What stays refused, and with which sentence

Today every carrier row is refused (`workbook/build.py`, `later_rows`): *"P is mounted on C, with 3 copies round it:
carriers and copies are laid out in phase W7, and the gearbox is not checked until then."* That sentence goes.
Refused at Build after W7, as `later_rows` warnings at their cells (so Build parts still builds every gear's part):

| Row | Sentence (B writes) |
|---|---|
| bevel, sleeve, dog, sliding gears, modes | as W6 and W8 leave them |
| a shaft mounted on a shaft that is itself mounted | *"P2 is mounted on P, which is itself mounted on C: a carrier riding another carrier is not built by this version."* |
| a carrier whose axis is not Z+ or Z- | *"C's axis is X+: a planetary stage is built only on an axis along Z+ or Z- by this version."* |
| a planet shaft whose Axis, read in its carrier's frame, is not Z+ (it faces away from the carrier, or across it) | *"P faces Z- on C, the other way from its carrier: a planet that faces away from its carrier is not built by this version."* / *"P's axis is X+ on C: a planet turns about an axis parallel to its carrier's, so this is not built by this version."* |
| a sun or ring of the stage whose shaft faces the other way from the carrier | *"S faces Z- and C faces Z+: a planetary stage whose shafts face different ways is not built by this version."* |
| no member of the stage held (two inputs: a differential) | *"S, C and R form a planetary stage with no member held: a differential is not built by this version; set one of them to Role fixed."* |
| a planet shaft with more than one gear (a compound or stepped planet) | *"P carries Planet and Planet2: a compound planet is not built by this version."* |
| a planet meshing another planet (a double planet) | *"Planet meshes PlanetB on the same carrier: a double planet is not built by this version."* |
| a gear on a carrier's own shaft listed on Meshes (it would mesh a frame gear, or lock the planets if it meshed them) | *"CarrierGear is on C, the carrier, and meshes G8: a gear on the carrier that meshes another gear is not built by this version; it is built locked to the carrier when it meshes nothing."* |
| a helical or herringbone gear in a planetary stage | *"Planet is helical: a planetary stage is built with spur gears only by this version."* |
| two or more carriers in one workbook | *"C2 is a second carrier: one planetary stage per workbook is built by this version."* |

Errors, in `checks` (Build parts waits for them): a mesh between a planet and a gear on a frame shaft that is not
coaxial with the planet's carrier (§3.5: *"a mesh that fits no carrier is an error"*); a mount chain that loops (`A`
on `B`, `B` on `A`); `Copies` below 1. The model already makes `Copies` other than 1 on a frame shaft an error
(`model._check_references`).

### 1.3 What exists for each piece, and what is missing (code read at `0f5a121`; the ring/shift checks re-read at the
review's base)

| Piece | Exists | Missing |
|---|---|---|
| Format | `schema.SHAFTS` has `Mounted on` and `Copies` (whole); `model.Shaft.mount()`; `_check_references` refuses an unknown mount, a self-mount, Copies on a frame shaft | Copies ≥ 1; a mount chain |
| Refusal | `build.later_rows` refuses every mounted shaft | narrowed to §1.2 |
| Layout | `geometry.layout` returns `later` for any mounted shaft | copies placed (§2.2) |
| Phases | `geometry.phases` walks meshes from the input; a gear reached twice that disagrees is a `conflict`, which `checks.check` makes a **warning** | meshes expanded per copy; the conflict an **error** for a carried loop (§2.4) |
| Kinematics | the linear system in `Fraction`s; mounted shafts set `later`; after W6, own-axis unknowns with a per-mesh sense and W6's "carrier-ready form" written down for W7 (W6-PLAN §2.4) | the carrier term; planetary torques (§2.5) |
| Checks | `checks.check` stops at `layout.later`; `_check_clearances`, `_check_shafts`; since `d3f4dcf`/`9efde87`, a shifted pinion inside a ring is held to its **working** centre distance (`checks.internal_working_centre`), with the outside pair's error and fixes, a refusal when no angle answers the shift, and a warning when its tips cannot be checked (`internal.CLASH_CHECK_BELOW`, 20 teeth between); unshifted, `_check_ring_tips` warns of a tip clash | coaxial shafts and carriers exempted from two warnings; the planetary checks; every fix withheld on a planetary mesh (§2.3) |
| Layout part | `layout.shaft_layouts` raises on a mounted shaft; `layout_plan` makes offset planes and a named axis, globals as literals, a base plane at 0 | mounted shafts skipped; the carrier part, made by `layout_plan` (§2.6) |
| Motion | `motion.motion_plan`: union-find over shafts, a mesh touching a fixed gear skipped, a loop-closer `unmated` (D6), one anchor per shaft | bodies per copy, the mates chosen by rank (§2.7) |
| Planning | `gearbox.plan_gearbox`: one component per Gears row, handle `gear<index>`; identical rows share one part | a component per copy; the carrier part, made or reused; its journal entry |
| Worker | `swbuild.build_gearbox` builds parts → layout → assembly; the sense read-back; `train_check` of meshes and locks over the **mated** gears only; `_update_motion` puts each train whole, then re-places fixed gears | carrier documents; a carrier link and the held members of a carrier mesh in `train_check` and `_trains`; the held member put first, then the carrier (§2.9) |
| COM | `_component_ref` selects `"<handle>:<feature name>"` in any component, so `carrier1:P copy 2 Axis` needs nothing new | nothing (§2.9) |
| Record | schema 4 after W6 (`MateEntry.plane`, `MateEntry.sense`) | carriers, the copy a component is of, the part a mate's axis is in (§2.11) |
| Demonstration | W4–W6 sections; `copy_built` (W6-PLAN §6.2) | the planetary sections (§6) |

---

## 2. The design

### 2.1 The workbook rows of a planetary stage, and how the model reads them

A planetary stage is written with the rows §1 already has. The 4 : 1 fixture (§4):

| Shaft | Mounted on | X | Y | Z | Axis | Role | Copies | Speed | Torque |
|---|---|---|---|---|---|---|---|---|---|
| S | frame | 0 | 0 | 0 | Z+ | input | | 1000 | 2 |
| C | frame | 0 | 0 | 0 | Z+ | output | | | |
| P | C | 18 | 0 | 0 | | | 3 | | |
| R | frame | 0 | 0 | 0 | Z+ | fixed | | | |

Gears `Sun` on S, `Planet` on P (one row, three components), `Ring` on R (internal); Meshes `Sun–Planet`,
`Planet–Ring`. The model needs no new field.

- **A carrier** is a frame shaft another shaft is mounted on. It may carry gears of its own, each locked to the
  carrier skeleton and meshing nothing (J8; §1.1, §2.7).
- **A planet shaft is placed by composing frames** (PLAN-WORKBOOK §1: "X Y Z are then measured on that shaft at its
  starting turn"; §3.3: "`mounted on` composes frames"; *reading J4*, review M4). Its X, Y, Z and its Axis are read
  in the carrier's own frame at the carrier's starting turn: the carrier's frame is `base_frame` of its direction
  (W6: `F₊ = I`, `F₋ = rot_x(180°)`) at the carrier's point. A point typed `(x, y, z)` on the carrier lands at
  `p_c + F_σc·(x, y, z)`: on a Z- carrier, y and z are negated in the origin's frame. A planet's Axis blank or `Z+`
  means the carrier's own +Z; anything else is refused (§1.2). For a Z+ carrier this is the origin's axes translated,
  as the first draft had it.
- **Copies** stand evenly round the carrier's axis: copy k (k = 1 … N) is copy 1 turned `ψ_k = (k − 1)·360/N`
  degrees about the carrier's own +Z, so it lands at `p_c + F_σc·rot_z(ψ_k)·(x, y, z)` — anticlockwise from +Z on a
  Z+ carrier, clockwise on a Z- one. Copy 1 is at the typed point.
- **Copy names** (*reading J3*): with Copies = 1 a shaft and its gear keep their own names. With N > 1, copy k of
  gear `Planet` is `Planet copy k` and of shaft `P` is `P copy k`. A space is not allowed in a workbook name
  (`schema.NAME_PATTERN`), so a copy name never equals a gear's or shaft's own. Pure helpers in a new
  `workbook/planetary.py`: `copy_id(name, k, copies)`, `copy_offsets(x, y, z, copies)` (in the carrier's frame).
- **The stage** is recognised, not typed: `planetary.stages(spec, placed)` finds, per carrier, its planet shafts and
  gears, the frame gears coaxial with the carrier that mesh a planet outside (sun) or inside (ring), and the held
  member. `planetary.Stage` is pinned in §5.3.

### 2.2 Placing copies (`geometry`)

`geometry.layout` places the planet gear once per copy, keyed by its copy id, at the composed point of §2.1 plus its
`At` along its own axis (the carrier's direction), with W6's `Placed.axis` and `Placed.centre` set for the copy, and
three additive fields: `row` (the Gears row id), `copy` (k, or 0 when Copies = 1), `carrier` (the carrier shaft, or
`""`). **`Placed.shaft` is the copy's own shaft id** (`"P copy 2"`; review S1), so every rule that groups by shaft
(`_check_clearances`' same-shaft skip, `_check_shafts`, `motion`'s anchors, `preview`) treats each copy as its own
shaft. `geometry.expand_meshes(spec, placed)` lists the meshes at copy level, in Meshes-sheet order and copy order
within a row (`Sun–Planet` becomes `Sun–Planet copy 1`, `… copy 2`, `… copy 3`); everything that takes "the listed
meshes" takes this list, `_check_clearances`' `listed` among them (else every copy would get "sits where it would
mesh: list them on Meshes"). Downstream code that names a cell goes through `Placed.row`.

### 2.3 Checks (`checks`, `planetary`)

Every check names its cell. Per expanded mesh run the clearance and the phase; the centre, kind, module, pressure
angle and face checks run **once per Meshes row** (copy 1), since the copies are the same mesh turned.

**What the existing checks already give a planetary** (review M2; `checks._check_mesh` since `d3f4dcf`, `9efde87`):
the sun–planet mesh is held to its working centre distance with both shifts (`pairs.describe`); the planet–ring mesh
to `checks.internal_working_centre` with the planet's shift (a ring takes none), or to the plain `m(z_r − z_p)/2`
unshifted; a shift no angle answers is an error; a shifted planet with fewer than 20 teeth between it and the ring
gets the warning that its tips could not be checked; an unshifted one within that difference gets
`_check_ring_tips`' tip-clash warning. The ring probe's shifted pinion built clean at its working distance
(`probe/results/ring-shift-2026-20261114-185630.log`). So a shifted planet is **not** an error in W7: the planet's
one distance from the carrier's axis must satisfy both working centres, and each mesh's existing centre error says
so when it does not.

**What W7 adds on top:**

1. **The ring's tooth count**, for a simple stage with no gear shifted and `z_ring ≠ z_sun + 2·z_planet`, said **in
   place of whichever centre errors that causes** (review S2): *"Gears!F4: Ring has 56 teeth, and a ring around Sun
   (18) and Planet (18) needs 18 + 2 × 18 = 54: with 56 the planets cannot mesh with both at once."* With a shift
   anywhere, the two working-centre errors stand as they are.
2. **The assembly condition.** Evenly spaced copies mesh with the sun and the ring at once exactly when
   `(z_sun + z_ring)/N` is a whole number (a planet between an outside sun and an inside ring; profile shift changes
   nothing, being symmetric about the space centre). The phase walk of §2.4 closing at every copy is the general
   form, and for the simple stage it reduces to this. The error: *"Shafts!H4: 5 copies of Planet cannot all mesh with
   Sun and Ring at once: (18 + 54) / 5 = 14.4 is not a whole number. With these teeth the copies can be 1, 2, 3 or 4;
   more would not fit round C."* (the list is every N that divides `z_s + z_r` and passes item 3).
3. **Neighbouring copies.** Copies k and k+1 stand `2a·sin(π/N)` apart (a the planet's distance from the carrier's
   axis); their outer diameters plus `CLASH_GAP · m` must fit (review S3): *"Shafts!H4: 6 copies of Planet stand 18 mm
   apart round C, and their tips need 20.5 mm: 5 is the most that fit round C, and of those 1, 2, 3 and 4 also mesh
   with Sun and Ring."* It replaces `_check_clearances`' pairwise errors for copies of one shaft (which see each copy
   as its own shaft, §2.2).
4. **A member held.** No member held is refused at Build (§1.2); two held jam it (the existing jammed error).
5. **Coaxial shafts and carriers.** Sun, carrier and ring on one line (within `CENTRE_TOLERANCE`) are exempt from
   `_check_shafts`' "passes over another shaft's axis" warning; a carrier is exempt from its "carries no gear" warning
   (review S4).
6. **No fix on a planetary mesh** (review M3). `fixes.move_fix` withholds Move only when the shaft graph has a cycle
   (`_is_tree`); a planetary's shafts form a tree (S – P – R), so for Ring typed 56 it would offer moving R off the
   sun's axis, and `shift_fix` / `unshift_fix` would offer shifts the stage cannot take on one gear alone. So
   `checks` withholds **every** fix (`report.fixes[where]` stays empty) on a mesh whose `planetary.mesh_carrier` is a
   carrier, and the error ends *"; no fix is offered for a planetary stage, whose three gears and copies must change
   together."*
7. **Undercut, and a small sun.** W7 models no undercut. A sun or planet below the undercut limit keeps the strip's
   warning (`spur.section_diagnostics`). Since `0f5a121` a 6- or 7-tooth pinion builds, with an arc on its tip cap,
   and on SolidWorks 2026 such pinions meshed a 24-tooth gear at the default backlash with zero interference at five
   phases (`probe/results/small-pinion-2026-20261114-184220.log`); a positively shifted 6- or 7-tooth pinion is
   refused as pointed. For a planetary that means: a small sun is accepted and built like any spur part; its
   undercut is not modelled; the cure the warning offers (a shift) is not open to a 6- or 7-tooth sun; and the only
   evidence of clean running is that measurement against a 24-tooth partner, not against a planet of the sun's own
   size, which neither W7's checks nor its demonstration cover. So W7 says it: a planetary whose sun or planet is
   below the undercut limit gets one warning at the gear's cell, *"Sun (7 teeth) is below the undercut limit, which is
   not modelled, and meshes Planet (19 teeth): the build checks interference only where the gears stand, so check
   Sun with Planet turning in SolidWorks."*, and the build's interference sentence, when a clash involves such a gear,
   ends *"; Sun is below the undercut limit and its undercut is not modelled, so the clash may be the bottom of its
   flanks"*. The fixture uses 18 teeth (limit 17.1), so the demonstration is not muddied by it.

`checks._worked_out_as` says the stage: *"Planetary, R fixed · 3 planets · 4.000 : 1 · output turns the same way"*
(with parallel meshes joined: *"Planetary and parallel · …"*).

### 2.4 Phases

`geometry.phases` runs on the expanded meshes in the family frame W6 gives it. It starts from the first input's gear
(θ = 0), so for the fixture: `Sun` θ 0; each `Planet copy k` from the sun by `external_space`; the ring from copy 1
by `ring_space`; the ring reached again from copies 2 and 3 must agree to a hundredth of its pitch, or it is a
conflict, §2.3 item 2's error. Each copy has its own θ: the copies are components of one part, each placed at its
own frame. A carrier has no teeth and no θ: it is built unturned. Tests compare a ring's θ **modulo its pitch**
(`_wrap` can return ≈6.6666° for 0).

For the fixture every copy comes out at θ = 10° (`2ψ_k + 170° ≡ 10° (mod 20°)` at ψ_k = 0°, 120°, 240°), and the ring
at 0 modulo its pitch (6.6667°) from every copy. Numbers in §4.

### 2.5 Kinematics with a loop

**The mesh equation with its carrier**, in W6's own-axis form (W6-PLAN §2.4, its "carrier-ready form"; review S15).
Unknowns stay one per **shaft row**: a planet shaft's copies turn at one speed about their own axes, so they share one
unknown and add no rows. For a mesh between gears on shafts p and q, its carrier c is: `frame` when both are frame
shafts; the carrier C when one is mounted on C and the other is a frame shaft coaxial with C; otherwise the mesh fits
no carrier, an error. With W6's per-mesh sense `c_m = ±1` (PARALLEL: `a_p·a_q` outside, `−a_p·a_q` inside a ring) and
`s_x = a_x·a_c` each shaft against the carrier:

    z_p·(ω_p − s_p·ω_c) + c_m·z_q·(ω_q − s_q·ω_c) = 0,        ω_frame = 0

Inputs are their speed, held shafts 0, and the exact rank says settled, free or jammed. **What "loops" means for the
solver:** it was always one linear system, not a walk, so a planetary's loop (sun – planet – ring, closed through the
carrier's term) needs no new method; only the carrier columns are new. Loops show in the mates (§2.7) and the phases
(§2.4).

**The Willis equation** follows: `(ω_s − ω_c)/(ω_r − ω_c) = −z_r/z_s` (all facing one way). With one member held:

| held | input → output | ratio (input ÷ output) | fixture (z_s 18, z_r 54) |
|---|---|---|---|
| ring | sun → carrier | `1 + z_r/z_s` | **4.000 : 1**, same way |
| sun | ring → carrier | `1 + z_s/z_r` | 1.333 : 1, same way |
| carrier | sun → ring | `−z_r/z_s` | 3.000 : 1, the other way |

**Planet speeds.** `Motion.speeds` holds each planet shaft's own-axis speed in the origin's frame. `Motion.relative`
(new) holds each mounted shaft's speed relative to its carrier, `ω_p − s_p·ω_c` (fixture: P −500 rpm, −750 on C).

**Torques** (*reading J10*). For the stage, with one member held and one input: η₀ is the product of the meshes'
efficiencies from sun to ring through one planet (96.04 % by default); in the carrier's frame the member whose
relative power is positive drives and the other receives η₀ of it:

    T_s + T_r + T_c = 0,   T_receiver·(ω_receiver − ω_c) = −η₀·T_driver·(ω_driver − ω_c)

Ring held: `T_c = T_s·(1 + η₀·z_r/z_s)` = **7.7624 N·m** for T_s = 2, stage 97.03 %, the ring holding **5.7624**. Each
planet shaft carries 0 about its own axis (W3's idler rule). The held member's torque is reported as held
(`Motion.held`, new). The stage joins W3's power-path walk as one link from its input member to its output member, so
a parallel train joined to the sun or ring gets torques on. `Motion.torque_note` says why a torque is missing.

### 2.6 The carrier part (`layout`)

One part per carrier: `<Name>_<Carrier>_Carrier.SLDPRT` (`Planetary_4to1_C_Carrier`; a revision
`<Name>_r<n>_<Carrier>_Carrier`), made by **`layout.layout_plan` itself** on the carrier's own axes, its
`BuildPlan.kind` `"carrier"` (`layout.CARRIER_KIND`), so it is built and checked like the layout part and has no
solid, no plate, no pins (the user's answer). In its own coordinates, which by §2.1's composition are the workbook's
offsets turned by ψ_k and nothing else (on a Z- carrier as on a Z+ one; review M4):

- `"<C> Axis"`, through the Right and Top base planes (`AXIS_THROUGH_BASE_PLANE`);
- per copy k, the plane offset from Right by `x_k` and the one from Top by `y_k`, `(x_k, y_k) = rot_z(ψ_k)·(x, y)`
  (`"P copy 2 X Plane"`, …; the base plane at 0) and `"P copy 2 Axis"` through them, driven by globals
  `"P copy 2 X"`, `"P copy 2 Y"` holding **literal** values the app works out (*reading J1*), which Update sets as it
  sets the layout's. Signed as `layout_globals` writes them (`LAYOUT_NEGATED_LINK`).

Its origin sits **on the layout's Front plane**, at `(x_c, y_c, 0)`, whatever the carrier's Z (*reading J2*); the
planets are held along their shafts from the layout's Front plane themselves (§2.7), so a carrier never meets W5's
Front-plane structural rule. Its frame in the assembly is `base_frame(a_c)` at that origin, unturned.

`shaft_layouts(spec)` returns the frame shafts and **skips** mounted ones (it raises on them today); the carrier, a
frame shaft, keeps its `"C Axis"` in the layout part on the same line as `"S Axis"` and `"R Axis"`. Pinned shapes in
§5.3.

Every planet axis is parallel to its carrier's, so it is the line where a plane offset from the carrier part's Right
plane meets one offset from its Top plane, whatever the copy's angle: no plane at an angle is needed (PLAN §4.2 had
feared it), and nothing of W6's slanted-axis construction.

### 2.7 The turning assembly (`motion`)

Components, in insertion order: the layout (`layout`), the carrier (`carrier1`), each gear and copy (`gear<index>`,
copy k `gear<index>c<k>`; index in Gears-sheet order). Each inserted, placed at its frame and fixed, then unfixed
immediately before its own mates (W5's sequence).

Mates, every one a W5 kind, named by `motion.mate_name`:

| What | Mate | Name |
|---|---|---|
| a turning carrier on its shaft | `coincident` `carrier1:C Axis` ~ `layout:C Axis` | `C carrier on C Axis` |
| … along it | `point` `carrier1:origin` ~ `layout:plane1` (always coincident: §2.6) | `C carrier along C` |
| each planet copy on its carrier axis | `coincident` `gear2c2:Gear Axis` ~ `carrier1:P copy 2 Axis` | `Planet copy 2 on P copy 2 Axis` |
| … along its shaft | `point distance` `gear2c2:origin` ~ `layout:plane1` (W6's `plane` `"front"`), D1 linked to **one global per row**, `"Planet Face Z"`, added once and shared by the copies (*reading J7*; review S5) | `Planet copy 2 along P copy 2` |
| a gear on the carrier's own shaft (J8) | `lock`, bare handles, the carrier component first as anchor (W5's lock route, `Select4` with a mark-1 select data); the gear is unfixed immediately before it; no axis or along mate of its own (a locked gear also on an axis over-defines: tier 8) | `CarrierGear locked to C carrier` |
| frame shafts (a second gear on the sun's or ring's shaft locked to that shaft's anchor) | as W5 | `Sun on S Axis`, `Sun along S`, `InDog locked to Sun` |
| gear mates | as W5 (§ below) | `Sun meshes Planet copy 1` |

`MatePlan` gains `on: str = ""`: the component holding the axis the mate is made to (`""` the layout, else a carrier
id); `shaft` holds the axis stem (`"P copy 2"`), so the axis is always `f"{shaft} Axis"`. `motion_assembly_plan`
adds each face global once, and `BuildPlan.check()` refuses a global added twice (review S5). A **held carrier** is
inserted, placed and fixed, never unfixed and never mated; its copies are mated to its axes as above, and the gears on
its own shaft stay fixed with it (`still_shafts` names the held carrier's shaft). A **held sun or ring** stays fixed
(W5-PLAN D9; *reading J6*). A gear on the carrier's shaft meshes nothing, so it adds no row to the rank below and the
carrier never becomes a node of the mate count (review S6's case needs a carrier gear on Meshes, which §1.2 refuses);
it joins the carrier's train by its lock.

**Which gear mates, by rank** (*reading J5*; review S6, S12). Each listed mesh at copy level is one row of the system
of §2.5 written per **body** — a frame shaft or one copy — with the carrier's column (the spike's interpretation:
SolidWorks turns a gear mate's gears relative to the line joining their axes, §2.9). Held bodies are 0. In
Meshes-sheet order, copy order within a row: a mesh between two held gears is skipped (W5); a mesh whose row is
independent of the rows already chosen (exact rank in `Fraction`s, `kinematics._reduce`) gets a gear mate; one that is
not goes to `unmated`. For every case W7 builds this gives the union-find answer of the first draft:

- ring held (§4.1): `Sun meshes Planet copy 1`, `… copy 2`, `… copy 3`, `Planet copy 1 meshes Ring`; unmated
  `Planet copy 2–Ring`, `Planet copy 3–Ring`;
- sun held (§4.2): the same four (three of them to the fixed sun) and the same two unmated; the ring is mated to
  `R Axis`;
- carrier held (§4.4): the same four and the same two unmated, every axis still.

N + 2 freedoms with one member held after the axis and along mates, N + 1 independent gear mates, one freedom left.
W5's rule "a mesh with a fixed gear gets no mate" is narrowed to "a mesh between two held gears".

**Measured** (`W7-SPIKE.md`, SolidWorks 2026, the fixture built in this shape): this exact set turned the 4 : 1 right —
sun +30°, carrier +7.5°, each planet −15° (−22.5° relative to the carrier), ring 0; every mate status 1, no error
code; no interference on any of the six meshes, the two unmated ring meshes included, when driven; one planet or
three, 0.11 s per rebuild alike; saved, closed and reopened, every document unmodified on open and the same drive
again. With only `Sun meshes Planet copy 1` and `Planet copy 1 meshes Ring`, copies 2 and 3 stayed free and clashed:
every copy needs its sun mate.

**What the read-back must show** (`swbuild._check_mates`, unchanged in rule): every planned mate present, status 1,
code 0, not suppressed; every unfixed component — sun, carrier, every copy — `COMPONENT_UNDER_DEFINED` (the spike read
the sun and carrier under-defined without the drive); every gear mate read back by `_settle_sense` (on W6's
`sense_reading`, `same_sense = k > 0`, the axes the copies' frames give) and remade with the other Flip when wrong.
The spike: the sun–planet mates read right with Flip False; **the ring mate read wrong with Flip False** — driven that
way the carrier turned −15° and the planets −60°, with clashes — and remade with Flip True read right and turned
right. So the read-back works unchanged on a moving axis, and the ring mate must go through it. The held member reads
fixed. No mate is named for an unmated mesh; the record lists it in `unmated`.

`MotionPlan` gains `carriers: Tuple[str, ...] = ()` (carrier ids mated to turn); a held carrier's id joins `fixed`.
`trains` and `drag` are per train; a train includes its carrier. `still_shafts` never names a mounted shaft (a copy's
axis orbits even at 0 rpm about its own axis; review note).

**"Drag the input"** (*reading J14*). The person drags the input's gear (the fixture: `Sun`): the copies orbit and
spin, the carrier's axes turn with them, the ring stays. A carrier input has nothing to grab, so the drag gear is then
the first turning gear of its train, and the footer says the carrier is axes and planes only. The API proof is the
demonstration's temporary driving mate (`DRAG_OPERATOR_TURNS_TRAIN` False).

### 2.8 Copies in the build, the record and Update

**One part file inserted N times** (PLAN's judgement call; *reading J3*). `build.plan_parts` already makes one job
per distinct part; `plan_gearbox` makes one component per copy from it. SolidWorks names them `Planet-1`, `Planet-2`,
`Planet-3`; the record maps each **copy id to the Name2 SolidWorks kept** (`ComponentEntry`), never assumed from the
order. The spike found three copies of one part file and mated them without trouble. A value change to the planet's
part is one `update_variables` on the one file, which every copy follows.

### 2.9 SolidWorks: the worker (`swbuild`) and COM (`swcom`)

- `build_gearbox(..., *, carriers=())`: each carrier part a `BuildPlan` to make or a `DocumentValues` to reuse (checked
  live like the layout), built **after the layout and before the assembly**; a failure skips the assembly. Pre-flight
  adds the carriers' paths to "made" and "reused" and to the paths the assembly may insert.
  `GearboxResult.carriers: List[BuildResult]`, `carriers_reused: List[str]`; progress `Step(STAGE_CARRIER, stem)`.
  `senses` (W6's replacement of `internal`) covers every gear mate, copies included.
- `update_gearbox(..., *, carriers=())`: each carrier part's globals read in the check phase and set in the change
  phase after the layout's (`_update_values`' rules), so its axes move before the assembly rebuild; the mates then
  carry the copies, and the train is put back.
- **`train_check` with carriers and held members** (pure, written in full in the interface commit with its tests;
  review M1): given `carriers: Sequence[CarrierLink]` and `held: Sequence[str]`, the carrier's own turn δ_c is read
  first; every gear on its planet shafts (`CarrierLink.planets`; review S7) has its wanted frame carried round the
  carrier's axis by `σ_c·δ_c` before its origin and axis are judged, and its δ measured against that carried frame
  (its turn relative to the carrier); in a mesh whose `MeshLink.carrier` is set, a frame gear's δ is taken relative to
  the carrier, `δ − s·δ_c`; a **held** gear that a recorded gear mate touches is judged too, against its wanted frame
  (its δ must be 0 or whole pitches, its origin and axis in place), so `Planet copy 1 meshes Ring` is judged in the
  check phase and in the post-check; then `δ_b − k·δ_a` is a whole pitch of b, k the tooth ratio `mesh_links` makes.
  A carrier's pitch is 0, so any carrier turn makes the train `turned`. A gear on the carrier's own shaft is a
  `LockLink(anchor="C carrier", follower="CarrierGear")`, tested exactly as W5's locks are (its δ equal to δ_c); it is
  coaxial with the carrier, so it is not carried. With neither carriers nor held gears it is W5's function byte for
  byte.
- `_trains` joins a carrier to its planets and a held gear to the trains its gear mates touch. **Order of a put**
  (review M1, M5; *reading J15*): a gear-mated held member that must be re-placed is put **first** (`REPLACE_FIXED_ROUTE`),
  then the carrier, then every gear of the train, with the gear mates on (`MESH_PHASE_ROUTE`) and every lock of the
  train suppressed around the puts (W5 M1, M8) — the carrier gear's lock among them, so the carrier is put with its
  lock off and the carrier gear is put to its own wanted frame (the carrier's turn applied about their shared axis),
  then the lock turned back on in a `finally`, as W5's `_put_train` does for any lock. Fixed gears no gear mate touches keep W5's place at the end. A put of a
  component whose axis is mated to another free component is not covered by the spike; `place_component` reads each
  frame back and the post-check reads every frame again (held members included), so a put that does not hold is a
  sentence, never silence; §6's p3 shows it on SolidWorks.
- The mate check, the constrained-status check and interference are unchanged. A carrier is a handle in a `Mate` op
  whose last `Fix`/`Unfix` is `Unfix`, so `_mated_handles` includes it.
- **COM:** nothing new. Every call is one W4–W6 used: `NewPart` and `layout_plan`'s ops; `AddComponent`/`Place`/
  `Fix`/`Unfix`; `add_mate` coincident, point, point distance and gear, with references `_component_ref` resolves in
  any component by feature name; `lock` between a carrier skeleton (no body) and a gear is W5's lock route on a
  component the spike did not lock, shown first by p1. The new combinations — an axis mate between two free components, a gear mate with
  one fixed component, a coaxial carrier, one part inserted three or four times — were made by the spike on 2026
  without a dialog or an error.

**The fake** (package A, `tests/test_swbuild.py`): an axis mate whose target is in a component other than the layout
puts the gear's axis where that component's document globals put it, transformed by that component's frame; a
carrier with an axis mate to the layout goes to its axis like an anchor, swung 13° the wrong way when its X/Y moved,
and carries its planets (each swung too); a put on a held component re-places it, and a held component gear-mated to
a train is not moved by the fake's solve. Over-definition is judged **by the rank of the R rows with the carrier
column** (review S12), not by the planner's own rule, so a test can find a wrong count. As in W5 the fake turns nothing
by a gear mate: a test helper sets a consistent planetary turn from the kinematics.

**No fallback.** The first draft kept a "kinematic" route in reserve (each body gear-mated to the input at its solved
absolute ratio). The spike built it and it is **wrong** on SolidWorks: the planets turned −3.75° where −15° is right,
with clashes, because a planet's gear mate is measured relative to the carrier. It is removed, and with it the
review's alternative mate set for a fixed-frame reading and the follow-up probe M6 asked to design for it.

### 2.10 Update's classification for a planetary stage (`update.classify`)

| Edit | Class | How |
|---|---|---|
| any gear's teeth, module, face, bore … (the part's globals), the checks passing | value Update | `update_variables` on the part (one file for every copy); a gear mate's ratio by the remake (`GEAR_MATE_RATIO_ROUTE` "remake"); copy 1's planet carries two gear mates, so `IDLER_UPDATE_HOLDS` gates it as today |
| a planet's X, Y on its carrier, every copy staying on the same side of the carrier part's base planes | value Update of the carrier part | valid only with a teeth or module edit that keeps both centres (else the checks refuse it first, review S14); the carrier part's globals set, the train put back |
| a copy coordinate changing side, reaching or leaving 0 | structural | `OFFSET_GLOBAL_CROSSES_ZERO` False, as for the layout |
| a frame shaft's X, Y (carrier, sun, ring together) | move | the layout's globals; the mates carry the gears and the carrier; the train put back |
| a gear's At or face width (planets: one `"Planet Face Z"`) | move | as W5; an anchor's front face reaching, leaving or crossing the Front plane is structural (W5-DECISIONS answer 3) |
| a held member's At or face width (the ring) | move | the held member re-placed first, then the train put (M1's order) |
| the carrier's Z | move | it moves the planets along (§2.1); one that brings a planet's front face onto, off or across the Front plane is structural (review S14) |
| a tooth or Copies edit that breaks the assembly condition or brings the copies too close | Checks error | Build and Update are not offered (review S14) |
| `Copies` changed, the checks passing | structural | *"P now has 4 copies where it was built with 3, and Update SolidWorks cannot add or take out a planet, so the gearbox needs building again."* |
| `Mounted on` changed; a shaft becoming or ceasing to be a carrier | structural | *"P is now mounted on C2 where it was built on C, and its mates hold it to C's axes, so the gearbox needs building again."* |
| the held member changes (a Role to or from fixed) | structural | W5's rule |
| a shaft's Axis changed | structural | W5/W6's rule |
| a mesh added or removed | structural | W4's rule |
| speeds, torques, efficiencies | nothing in SolidWorks | as W4 |

The record's mates are never re-derived (W5). `classify` compares copies through `ComponentEntry.of`, so the planet's
components are not called "new" one by one; the Copies sentence says it once. `MotionUpdate` gains `carriers` and
`held` (the held gears a recorded gear mate touches), `MeshLink.carrier` is set for every gear mate of the stage, and
placements include the carrier component (pitch 0) and the held member. `MotionUpdate.face_globals` lists a shared
global once (review S5).

### 2.11 The record (`store`, schema 5)

`store.LINK_SCHEMA_VERSION = 5`: W6 sets 4, W7 is one past it, W8 will be one past W7's. Code and tests read the
constant — a "newer record" fixture is `LINK_SCHEMA_VERSION + 1`, a "previous" one `LINK_SCHEMA_VERSION − 1` — and
never write another phase's number. A W6-era build refuses a v5 record and leaves it byte-identical (W5-PLAN D11's
mechanism); v1–v4 read as v5. Additive, defaulted:

```python
@dataclass
class CarrierEntry:                    # one carrier part of the current revision
    shaft: str = ""
    path: str = ""                     # <Name>_C_Carrier.SLDPRT
    component: str = ""                # its Name2 in the assembly
    rotation: List[float] = []         # its frame, as placed or last put
    at: List[float] = []
    direction: List[float] = []        # its axis, as W6's ShaftEntry.direction
    axes: List[ShaftEntry] = []        # layout.CarrierLayout.axes, field for field
GearboxRecord += carriers: List[CarrierEntry] = []
ComponentEntry += of: str = ""         # the Gears row a copy is of ("" when the gear has no copies)
MateEntry += on: str = ""              # motion.MatePlan.on; W6's plane and sense are used as W6 defines them
```

A mesh entry's W6 `sense` holds its carrier-frame sense (the parallel rule's c), as made. The journal gains a
`PartEntry(kind="carrier")` per new carrier part, reused once checked live like a pending layout part. A refused
train leaves the carrier part saved and on record, as W5's answer 1 leaves the layout part.

### 2.12 The sentences and the window

C writes these in `ui_text` (exact; `{…}` from fields):

- **Before Build** (`motion_ready_line`): *"C is built as a carrier of axes and planes only, turning with Planet copy
  1, Planet copy 2 and Planet copy 3; Ring stays fixed."* (a held carrier: *"C is built as axes and planes only, held
  fixed; its planets turn on it."*)
- **After Build** (`motion_done_line`): *"… drag Sun in SolidWorks and the rest of its train follow: the planets turn on
  C, and Ring stays fixed. Planetary_4to1_C_Carrier holds C's axes and planes only: a plate and pins are yours to
  add."* The built list names the carrier part. Unmated meshes are logged (`mate    … left unmated: the others turn
  it as its teeth do`) and recorded, not said in the window (*reading J17*).
- **Update summary**: *"move the planets on C in Planetary_4to1_C_Carrier"*; *"move Planet (3 copies) along P"*;
  *"re-place Ring"* first when the held member moves.
- **After Update**: W5's pieces; a restored train lists the carrier as *"C (the carrier)"*.
- **Interference**: §2.3 item 7's undercut clause.
- **Speeds** (`workbook_speed_lines`): *"P  −500 rpm, −750 on C · 3 copies"* with W6's seen-from word; a held member
  *"R  held · 5.762 N·m"*. **Results** (`export.results_sheet`, B): a column *"On its carrier (rpm)"* for mounted
  shafts; a held member's torque with *"held"*.

**The window** needs **no new control**. The end view (`preview.layout_gearbox`) draws every copy and the carrier as a
dashed circle through its planets' axes, named at its cross. Boards (D): `WorkbookPlanetary` (the fixture built) and
`WorkbookPlanetaryCopies` (Copies 5: the assembly-condition error). `UI-DESIGN.md` §9 gains *"Planetary stages (W7)"*.

---

## 3. Readings

### 3.1 Readings the work proceeds with by default (to go to the user afterwards)

| # | Question | Options | Default, and why |
|---|---|---|---|
| J1 | How the carrier part's planet axes follow the workbook | (a) literal globals per copy; (b) SolidWorks equations with cos/sin | **(a)**: the layout part's proven pattern; trigonometric part equations are unprobed. |
| J2 | Where the carrier part's origin sits along its axis | (a) on the layout's Front plane, always coincident; (b) at the carrier's Z with a distance mate | **(a)**: a skeleton has no thickness. |
| J3 | Copies as files and names | (a) one part file, N components, ids `Planet copy k`; (b) N files | **(a)**: PLAN's judgement call; shown by the spike. |
| J4 | What a planet's typed X Y Z and Axis mean | (a) offsets along the origin's axes; (b) composed in the carrier's frame (PLAN-WORKBOOK §1, §3.3) | **(b)**, as the authority writes it (review M4); identical for a Z+ carrier; p6 builds a Z- one. (a) is offered to the user as an alternative only. |
| J5 | Which gear mates of a planetary are made | (a) by exact rank of the carrier-frame rows, Meshes-sheet order expanded copy by copy (fixture: N sun mates and one ring mate); (b) all 2N; (c) (a) with external meshes before internal ones | **(a)**: measured right by the spike; (c), fewer ring mates when Planet–Ring is listed first, is the user's to choose. |
| J6 | How a held member is held | `Fix` (W5-PLAN D9) | as W5. |
| J7 | Planet copies along their shafts | one Face Z global per row, added once, shared | reuses W5's along mate. |
| J8 | A gear on the carrier's own shaft | (a) locked to the carrier skeleton, meshing nothing; (b) refused; (c) locked and free to mesh frame gears | **(a)**: W8's E4 needs it (`LoDog`), p1 builds and drives one (`CarrierGear`), and meshing nothing it adds no row to the mate count. (c) is left for a later pass: a carrier gear on Meshes makes the carrier a node (review S6) and no section builds one. |
| J9 | Planetary checks | the ring/shift checks as they stand; the `z_r` sentence only unshifted; assembly condition and neighbours as errors; no fix offered | review M2, M3. |
| J10 | Torque through a planetary | basic-train efficiency, one held member, joined to W3's walk | the textbook method, pinned by numbers. |
| J11 | A stage with no member held (a differential) | refused at Build | the orchestrator's ruling (review S16); listed for a later pass. |
| J12 | Compound (stepped) and double planets | refused at Build | likewise. |
| J13 | Nested carriers, planetaries off Z±, planets not parallel to their carrier, opposite-facing members, helical planetaries, two stages | refused at Build (§1.2) | the scope principle; listed for a later pass. |
| J14 | What to drag | the input's gear; a carrier input: the first turning gear | a skeleton has nothing to grab. |
| J15 | Update's put of a planetary train | held member first, carrier next, then the train, back at its built turn | W5 answer 2 and M1, with review M1's order. |
| J16 | The record | `LINK_SCHEMA_VERSION = 5`; `CarrierEntry`, `ComponentEntry.of`, `MateEntry.on` | one past W6's. |
| J17 | Saying the unmated meshes | log and record, not the window | they need nothing of the user. |
| J18 | Planet speeds | own-axis, with the speed on its carrier beside it | both are asked for. |
| J19 | Undercut and a small sun | not modelled; one warning and one clause; the fixture avoids it | §2.3 item 7. |
| J20 | Gating the planetary build on a finding | no gate before the first build; once the demonstration has measured the planetary turning right, `findings.PLANET_GEAR_MATE_ROUTE = "teeth"` is committed with that evidence and `motion_reason` reads it for a plan with a carrier | the spike measured it but commits no finding (its note); the demonstration confirms it through the app. |

### 3.2 For the user afterwards, and what cannot proceed without them

Nothing needs the user before W7 can be built: the riskiest point is measured. Listed for them as a later pass could
open: differentials (J11), compound and double planets (J12), a gear on the carrier's shaft that meshes (J8 (c)), helical and
herringbone planetaries, opposite-facing members, two stages in one workbook, J4 (a) and J5 (c). One STOP stays: if
SolidWorks 2024's confirming build turns the planetary otherwise than 2026 did (the spike ran on 2026 only) and no
read-back remake puts it right, W7 cannot be confirmed on 2024, and the user is asked.

---

## 4. The fixtures

### 4.1 `Planetary_4to1` — the ring held (PLAN §6)

Box: Name `Planetary_4to1`, Pressure angle 20, Efficiency 98. Shafts as in §2.1. Gears (spur, involute, module 1,
face 10, At 10, so every front face is at z = 5 and every anchor gets a Face Z global):

| Gear | Shaft | Side | Teeth | Bore | Part name |
|---|---|---|---|---|---|
| Sun | S | external | 18 | 6 | Sun |
| Planet | P | external | 18 | 8 | Planet |
| Ring | R | internal | 54 | — | (default) |
| CarrierGear | C | external | 20 | 10 | CarrierGear (face 6, At 30) |

`CarrierGear` is J8's gear on the carrier's own shaft (the part W8's `LoDog` plays in E4, here a plain spur): it
meshes nothing, sits at z 27–33, clear of the stage's faces (z 5–15), and is locked to the carrier. Meshes
`Sun–Planet`, `Planet–Ring`. Four parts, the layout part, `Planetary_4to1_C_Carrier`, the assembly. Every number
below but CarrierGear's was recomputed by the review with `geometry.external_space` / `ring_space` /
`pinion_space`; CarrierGear changes none of them.

- **Checks:** `54 = 18 + 2·18` ✓; centres `m(18 + 18)/2 = 18 = m(54 − 18)/2` ✓; assembly `(18 + 54)/3 = 24` ✓;
  neighbours `2·18·sin 60° = 31.177 mm` > 20.5 ✓; 18 teeth above the undercut limit 17.1. Copies that fit: up to 5
  (21.16 mm at 5, 18.000 at 6); of those 1, 2, 3, 4 divide 72.
- **Positions** (mid-face z = 10, front face z = 5): Sun (0, 0); Planet copy 1 (18, 0); copy 2 (−9, 15.588457268);
  copy 3 (−9, −15.588457268); Ring (0, 0); carrier origin (0, 0, 0).
- **Phases:** Sun 0; every copy 10°; Ring 0 modulo 6.6667°. Frames: Sun I at (0, 0, 5); copy k `rot_z(10°)` at its
  centre, z 5; Ring I at (0, 0, 5) modulo its pitch; carrier I at (0, 0, 0); CarrierGear (reached by no mesh, so θ 0)
  I at (0, 0, 27).
- **Carrier part:** `C Axis`; `P copy 1 X Plane` 18 from Right with Top (base); copy 2: x −9, y 15.588457268; copy 3:
  x −9, y −15.588457268; globals `P copy 1 X`, `P copy 2 X`, `P copy 2 Y`, `P copy 3 X`, `P copy 3 Y`.
- **Speeds** (own-axis, rpm): S 1000, C 250, P −500 (−750 on C), R 0; **4.000 : 1**, same way.
- **Torques:** S 2.000; C 7.7624 (η₀ 0.9604, stage 97.03 %); R held 5.7624; P 0.
- **Mates (15), components (8):** `Sun on S Axis`, `Sun along S` (`Sun Face Z` 5), `C carrier on C Axis`, `C carrier
  along C`, `CarrierGear locked to C carrier`, per copy `Planet copy k on P copy k Axis` and `Planet copy k along P copy k` (`Planet Face Z` 5, once),
  gear mates `Sun meshes Planet copy 1/2/3`, `Planet copy 1 meshes Ring`; unmated `Planet copy 2–Ring`,
  `Planet copy 3–Ring`; fixed `Ring`.
- **A 30° drive of the sun** (measured by the spike to match, CarrierGear apart): carrier +7.5° and CarrierGear +7.5°
  with it, its origin unmoved; each copy's own turn −15° (−22.5° on C); Ring 0; copy origins at (17.846008, 2.349471), (−10.957706, 14.280360), (−6.888302, −16.629832), z unchanged; the
  unmated meshes in step, `(−22.5)·18 = −405 = (0 − 7.5)·54`.

### 4.2 The sun held

The same workbook with S `fixed` (Speed and Torque cleared) and R `input`, 1000 rpm, 2 N·m (an Excel edit in §6 p5,
a spec in the tests).

- **Phases:** from Ring (θ 0): every copy 10° (`pinion_space`); Sun 0 from every copy — §4.1's frames.
- **Speeds:** R 1000, C 750, P 1500 (+750 on C), S 0; **1.333 : 1**, same way.
- **Torques:** R 2.000; C 2.6403 (stage 99.01 %); S held 0.6403; P 0.
- **Mates:** gear mates `Sun meshes Planet copy 1/2/3` (to the fixed sun), `Planet copy 1 meshes Ring`; unmated as
  §4.1; `Ring on R Axis`, `Ring along R` made; `Sun` fixed.
- **A 30° drive of the ring:** carrier +22.5°, each copy +45° (+22.5° on C), Sun 0.

### 4.3 The stage on Z-

The same workbook with S, C and R on `Z-` (P blank: it faces C's way). By §2.1's composition the copies land at
`F₋·rot_z(ψ_k)·(18, 0, 0)`: copy 1 (18, 0), copy 2 (−9, −15.588457268), copy 3 (−9, 15.588457268); the carrier part
holds the same local coordinates as §4.1's. Mid-faces at z = −10, front faces at z = −5. Phases about each part's own
axis: Sun 0, every copy 10°, Ring 0 modulo its pitch; frames `F₋·rot_z(θ)`. Own-axis speeds as §4.1 (S 1000, C 250,
P −500, R 0); the same 4.000 : 1; seen from +Z every turn is reversed.

### 4.4 The carrier held

The same workbook with C `fixed` and R `output` (S input 1000). Speeds: S 1000, P −1000 (on C as well), R −333.33,
C 0; **3.000 : 1**, the other way. Torques: R 5.7624, C held 7.7624, P 0. Gear mates as §4.1, every axis still; the
ring mated to `R Axis`; CarrierGear held fixed with the carrier, no lock made. A 30° drive of the sun: each copy
−30°, Ring −10°, carrier and CarrierGear 0.

### 4.5 The tests' made-up specs

Copies 5 (assembly error, the list 1, 2, 3, 4), Copies 6 (neighbour error, "5 is the most that fit"), Ring 56 (the
`z_r` sentence in place of the planet–ring centre error, and no fix), a Sun–Planet centre error (no fix), a shifted
sun with the planet at the sun–planet working distance and the ring checked at the planet's plain distance, a +0.3
shifted planet at both working distances (accepted, with the tips warning), a 7-tooth sun (the undercut warning),
and one spec per §1.2 refusal.

---

## 5. Work packages, files and the shared shapes

### 5.1 Order

```
W6 closed ──► I (interface commit) ──► A (SolidWorks side) ─┐
                                       B (planning)       ──┼──► D (window, boards, docs) ──► E (demonstration)
                                       C (record, words)  ──┘
```

An independent review after I, after each of A–D, and after E's runs.

### 5.2 Who edits what

| Package | May edit |
|---|---|
| I | everything under §5.3, once, then hands over; `docs/notes-workbook/W7-INTERFACES.md` |
| A — SolidWorks | `swcom.py`, `swbuild.py`, `tests/test_swbuild.py` (the fake), `tests/test_swcom.py`; may add to `tests/test_swbuild_train.py`, never change an assertion there |
| B — planning | `workbook/planetary.py` (new), `geometry.py`, `kinematics.py`, `checks.py`, `fixes.py`, `assess.py`, `build.py`, `model.py`, `layout.py`, `motion.py`, `gearbox.py`, `update.py`, `export.py`, `gears/base.py` (`BuildPlan.check`'s duplicate-global refusal only); `tests/test_workbook_{planetary,geometry,checks,model,layout,motion,gearbox,update,export,demo_fixtures}.py`, `tests/test_probe_workbook.py` |
| C — record, words | `store.py`, `ui_text.py`, `tests/test_store.py`, `tests/test_ui_text.py` |
| D — window, boards, docs | `workbook_gui.py`, `preview.py`, `tests/test_preview.py`, `tests/test_workbook_{build,window}.py`, `design/**`, `docs/**`, `README.md` |
| E — demonstration | `probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, `probe/results/**`, `tests/fixtures/excel-windows/Planetary_4to1.xlsx`; after E's first 2026 run, `findings.py` and `tests/test_findings.py` for J20's finding only |
| nobody | `gears/*.py` but `base.py` as above |

### 5.3 The interface commit (I): the shared shapes

Starts on the commit that closes W6, named in `W7-INTERFACES.md` with the ring/shift checks it reads (`d3f4dcf`,
`9efde87`) and a restatement of what W6 changed that W7 builds on (review S15): own-axis kinematics with
`solve(..., senses=)`; `Placed.axis`, `centre`, `family`, `origin`; `geometry.base_frame`, `family`; `layout.frame`
on `base_frame`; `motion.mesh_links(meshes, teeth, sense)` with `k = −c·z_a/z_b`; `MatePlan`/`MateEntry` `plane` and
`sense`; `swcom.sense_reading` and `Session.gear_mate_sense(handle, same_sense, axes)`; `build(..., senses=)`,
`build_gearbox(..., senses=)`, `GearboxPlan.mate_senses`; `copy_built` (W6-PLAN §6.2). Shapes only, except where
marked **written**; a change to a pinned shape after it is a stop-and-ask; private helpers and keyword-only parameters
with defaults are free.

`swbuild.py` (shared by A and B):

```python
@dataclass(frozen=True)
class CarrierLink:
    carrier: str                          # the carrier's component id, layout.carrier_id(shaft): "C carrier"
    planets: Tuple[str, ...]              # every gear id on its planet shafts (copy ids), in plan order (review S7)
    point: Tuple[float, float, float]     # its origin as placed, mm (on the Front plane: z 0)
    axis: Tuple[float, float, float]      # its own +Z in the origin's frame (W6's Vec3)
MeshLink(a, b, k, pitch, carrier: str = "")   # carrier: a CarrierLink.carrier the mesh is measured against
def train_check(found, wanted, meshes, locks, pitch, tolerance=TRAIN_TOLERANCE, *,
                carriers: Sequence[CarrierLink] = (), held: Sequence[str] = ()) -> TrainCheck   # WRITTEN, with tests
MotionUpdate.carriers: Tuple[CarrierLink, ...] = ()
MotionUpdate.held: Tuple[str, ...] = ()       # held gears a recorded gear mate touches: judged, and re-placed first
STAGE_CARRIER = "carrier"
GearboxResult.carriers: List[BuildResult] = []; GearboxResult.carriers_reused: List[str] = []
def build_gearbox(..., *, carriers: Sequence[Union[BuildPlan, DocumentValues]] = (), senses=None, ...)   # body: A
def update_gearbox(..., *, carriers: Sequence[DocumentValues] = (), ...)                                  # body: A
```

`workbook/planetary.py` (new): `copy_id`, `copy_offsets` **written** with tests; `Stage(carrier: str, sun: str,
ring: str, planet: str, planet_shaft: str, copies: int, held: str)` (`held`: the member shaft whose Role is fixed);
stubs `stages(spec, placed) -> Tuple[Stage, ...]`, `assembly_counts(z_sun, z_ring, fit) -> Tuple[int, ...]`,
`most_that_fit(a, outer_diameter, module) -> int`, `mesh_carrier(spec, a, b) -> Optional[str]` (`"frame"`, a carrier
shaft, or None), `refusals(spec) -> List[Diagnostic]` (§1.2's rows, for `later_rows`).
`geometry.py`: `Placed.row: str = ""`, `Placed.copy: int = 0`, `Placed.carrier: str = ""` (beside W6's fields;
`Placed.shaft` the copy's own shaft id); stub `expand_meshes(spec, placed) -> Tuple[Tuple[str, str], ...]`.
`kinematics.py`: `Motion.relative: Dict[str, Fraction]`, `Motion.held: Dict[str, float]`, `Motion.torque_note: str = ""`.
`checks.py`: `Report.stages: Tuple[planetary.Stage, ...] = ()`.
`layout.py`: `CARRIER_KIND = "carrier"`, `CARRIER_SUFFIX = "_Carrier"`, `CARRIER_HANDLE = "carrier"`,
`CarrierLayout(shaft, x, y, z, direction, axes: Tuple[ShaftLayout, ...])`, stubs `carrier_id(shaft)`,
`carrier_stem(box_name, revision, shaft)`, `carrier_layouts(spec, report)`, `carrier_frame(carrier) -> Frame`,
`carrier_plan(carrier, template, path) -> BuildPlan`.
`motion.py`: `MatePlan.on: str = ""`; `MotionPlan.carriers: Tuple[str, ...] = ()`; `mesh_links(meshes, teeth, sense,
*, carrier_of: Mapping[Tuple[str, str], str] = {})`; stub `carrier_links(spec, report, plan) -> Tuple[CarrierLink, ...]`.
`gearbox.py`: `GearboxPlan.carriers: Tuple[Union[BuildPlan, CarrierReuse], ...] = ()`, `GearboxPlan.carrier_paths:
Mapping[str, str] = {}`, `GearboxPlan.carrier_layouts: Tuple[CarrierLayout, ...] = ()`; `CarrierReuse(path, variables,
features, journaled=False)`; `build_kwargs()` adds `"carriers"` **only when non-empty**.
`update.py`: `UpdatePlan.carriers: Tuple[DocumentValues, ...] = ()`, `UpdatePlan.carriers_moved: Tuple[str, ...] = ()`;
`update_kwargs()` adds `"carriers"` only when non-empty.
`store.py`: §2.11's shapes and `LINK_SCHEMA_VERSION = 5` (C fills the refusals: a `CarrierEntry` with no shaft or
path, an `on` naming no carrier on record).
`ui_text.py`: stubs `carrier_phrase(record_or_plan) -> str`, `copies_phrase(row, n) -> str`,
`planetary_speed_line(...) -> str`.

**Done:** the suite green but for stubs nobody calls; `train_check`'s tests pass: a planetary turned consistently is
in step and `turned`; one copy turned alone is out of step; a copy carried but not turned relative to the carrier is
out of step with the sun; a copy off its carried place is `off_axis`; the held ring judged (a carrier turned off its
Willis turn while the sun mates still hold is **out of step** through `Planet copy 1 meshes Ring`, review M1's
scenario 1); Z- carrier signs; with no carriers and no held gears, W5's results unchanged and every existing test of
`test_swbuild_train.py` untouched.

### 5.4 A — SolidWorks side

§2.9: the carriers step, pre-flight, progress, log lines; carriers in Update's values phase; `_trains` with carrier
and held links; the put order (held member, carrier, train); the fake. **Done (against the fake):** a planetary build
makes the carrier part then the assembly, every mate status read, carrier, copies and CarrierGear under-defined, ring fixed, CarrierGear's lock made carrier
first; a plan
doctored to add `Planet copy 2 meshes Ring` is over-defined by the fake's rank → refused (W5 answer 1), carrier part
and layout kept; a failed carrier part skips the assembly; a reused carrier checked live; Update: a consistent turn →
nothing put, `turned`; the ring mate suppressed and the carrier turned off Willis → out of step → put (M1 scenario 1);
a ring re-place with the train turned → ring first, then carrier, then train, post-check clean (M1 scenario 2, M5); a
carrier globals change → carrier part updated, the fake's swing put right; a W5 or W6 train's calls byte for byte as
before.

### 5.5 B — planning

§2.1–§2.8, §2.10, the Results column. **Done (pure):** §4's numbers pinned for §4.1–§4.4 (positions, phases modulo
pitch, frames, speeds incl. `relative`, torques incl. `held`, the carrier part's ops and globals, mates and unmated,
ids and handles, the §4.1 `motion_assembly_plan` op order golden list with `check() == []` and `Planet Face Z` added
once); every check of §2.3 with its sentence and no fix on a planetary mesh; every §1.2 refusal; every row of §2.10;
W5's and W6's fixtures' plans unchanged; the round trips on the fake once A lands (B's second pass).

### 5.6 C — record and words

§2.11, §2.12. **Done:** every new sentence filled from fields in a test; v4 read as v5, round trip byte-deterministic,
`LINK_SCHEMA_VERSION + 1` refused and untouched; the new `StoreError`s.

### 5.7 D — window, boards, docs

`workbook_gui` passes the new fields; `preview.layout_gearbox` draws copies and the carrier's circle; the two boards
drawn and looked at; `UI-DESIGN.md` §9; PLAN-WORKBOOK dated notes under §3.3/§3.5/§4.2 (*Readings chosen (W7)*) and §6's
W7 row; HANDOFF. **Done:** the window launched on §4.1 against the fake, footer read in each state; Windows Tk tests
green.

### 5.8 E — the demonstration

§6. **Done:** logs committed, 0 failed, for 2026 in full and 2024's confirming run; the person's step handed over.

---

## 6. The demonstration (package E), full build first

New sections in `probe/workbook_assembly_check.py`, `--only planetary` running them. Through the app's own code as
W5's sections go, every footer sentence logged, Excel edits by the script's own Excel, no user titles.

**Build once, copy after.** `p1` builds `Planetary_4to1` once into a master folder; later sections start from a copy
made by **`copy_built(master, section)`** (W6-PLAN §6.2, pinned in W6-INTERFACES; review S13): the master closed and
renamed for the run, every path the record and the sidecars hold rewritten through `store`, the copy's assembly
opened once and every component's path asserted in the copy (else that section builds fresh), two copies never open
together. Before each copy is opened the script also asserts that `documents()` holds no document with any of the
copy's file names. The carrier part is one more file the helper's path rewrite covers (`CarrierEntry.path`).

Measurements, all from SolidWorks' own readings:

- **Every build:** every component's frame against `layout.frames` to 1e-6, copies and carrier included; the carrier
  part's axes (`GetRefAxisParams`) carried into the assembly by the carrier component's transform: each copy's axis
  through its centre, along the carrier's direction; the mates exactly the record's names, codes 0, none suppressed;
  sun, carrier and every copy `GetConstrainedStatus` 2, the held member `IsFixed`; no mate for an unmated mesh.
  **Interference controls per copy:** `Planet copy k` turned half its pitch (a put with its gear mates on) must clash
  with exactly its sun and its ring, and nothing else; put back, none again. Saved, closed, reopened: the same.
- **The driven proof:** W5's temporary angle mate on the input gear, `"Drive"` 90 → 120, top-only rebuild; against the
  kinematics of the section's fixture (§4): every gear's own turn, the carrier's turn, every copy's origin carried to
  its place to 1e-6 mm, the held member unmoved, and the unmated meshes in step (relation residual ≤ 1e-6 rad).
  **`interferences()` with Drive at 120** (review S11): no clash, so the unmated copies are seen clearing the ring by
  SolidWorks itself. **Wrong-sense control:** the section's chosen gear mate suppressed and a temporary one with the
  other Flip in its place: the comparison must see the carrier or a copy turning wrong (in p1, the spike's numbers:
  carrier −15° for the ring mate's wrong Flip). Then W5 M12's hygiene. A section whose input is on Z- (p6) judges the
  drive's sense from the input's own turn: `DEMONSTRATION_DRIVE_SENSE` is stated for a Z+ input.
- **A build whose mate check refuses** (review M6, kept as a guard though the spike measured the base case): the
  section logs every component's constrained status and AddMate5 status, adds the temporary drive in the refused,
  unsaved assembly the script opened, reads which components turn, then closes it as the CAM-box protocol does; the
  run then stops that fixture's later sections (they copy it).

Sections:

- **`p1` — `Planetary_4to1`, ring held.** Fresh build. Every-build checks (`CarrierGear locked to C carrier` among
  the mates, CarrierGear `GetConstrainedStatus` 2), the driven proof (control on `Planet copy 1 meshes Ring`;
  CarrierGear's own turn read against the carrier's, +7.5° for +30° on the sun, to 1e-6, its origin unmoved), reopen; the marks after a build (no part, layout or carrier part marked; the assembly marked). Kept
  as the master. The fixture saved by Excel and copied to `tests/fixtures/excel-windows/Planetary_4to1.xlsx`.
- **`p2` — the user's turn and a quiet Update** (copy). Drive 37° and delete; Update with nothing changed: nothing
  put, *"… The gears stand where they were turned in SolidWorks."*; `train_check`'s residuals with the carrier and the
  held ring logged; every frame before and after equal to 1e-6; no document marked.
- **`p3` — puts, moves and values on a turned carrier** (copy; review M5, S8). Before **each** edit the train is
  driven 37° and the drive deleted, so the carrier stands at δ_c = 9.25°. (1) `Planet` At 10 → 12 → Update:
  `"Planet Face Z"` set once, the train put back, the log's put order carrier first, the lock `CarrierGear locked to
  C carrier` suppressed around the puts and on again after, every frame, carrier and CarrierGear included, at the
  built frame to 1e-6. (2) `Ring` At 10 → 12 → Update: the gear-mated held Ring re-placed **first**, then the
  carrier, then the train (M1's order, asserted from the log); frames; the ring mesh judged in step after. (3) Sun 18 →
  21, Ring 54 → 57, P's X 18 → 19.5 → Update: two parts' values, the carrier part's globals (copies at (19.5, 0),
  (−9.75, 16.887495374), (−9.75, −16.887495374)), all four gear mates remade (copy 1's planet carries two:
  `IDLER_UPDATE_HOLDS`) and read back, the swing put right, frames against the new `layout.frames` (every copy θ 10°,
  Ring 0 modulo 6.3158°), interference and its controls, the drive at **3.714 : 1** (for +30° on the sun: carrier
  +8.0769°, each copy −17.5°), interference at Drive 120, reopen. Centres 19.5 / 19.5, assembly (21 + 57)/3 = 26,
  neighbours 33.775 mm; torques T_c 7.2136 for T_s 2.
- **`p4` — the number of planets** (copy). Copies 5: the assembly error logged, Build and Update not offered.
  Copies 6: the neighbour error. Copies 4: the structural sentence, Build again… makes `Planetary_4to1_r2` with four
  copies of the one Planet part (copies 2 and 4 on the carrier part's Right base plane), every-build checks, driven
  proof (copies at 0°, 90°, 180°, 270°, each θ 10°), earlier files' sha256 and mtime unchanged.
- **`p5` — the sun held** (copy). §4.2's Role edits → structural → Build again… `_r2`: every-build checks, the driven
  proof driving the **ring** (its Top plane to the layout's Right plane), the control on `Planet copy 1 meshes Ring`,
  reopen.
- **`p6` — the stage on Z-** (copy). §4.3's Axis edits → structural → Build again… `_r2`: every-build checks (the
  copies where §4.3 puts them, the carrier part's local coordinates equal to p1's), the driven proof, reopen.
- **`p7` — the carrier held** (copy; review S10). §4.4's Role edits → structural → Build again… `_r2`: every-build
  checks (the carrier and CarrierGear fixed and never mated), the driven proof (copies −30°, Ring −10° for +30° on the sun), reopen.
- **window** (`workbook_window_check.py`, 2026): the built planetary footer and end view; the Copies 5 error.

**SolidWorks 2024, the confirming run:** `p1` and `p5` (the ring mates, where the versions have differed), and the
window check. **The person's step** (2026, then 2024): *open `Planetary_4to1.SLDASM` from the log's folder, drag Sun
round its axis by about a quarter turn, and watch the three planets: they roll round inside the ring the same way as
Sun, about a quarter as fast, each spinning the other way on its own axis; the ring does not move. Then press Update
SolidWorks with nothing changed: the footer should say the gears stand where they were turned.*

---

## 7. Calls not used before that could hang, raise a dialog, or damage a file or a session

**None in W7.** The demonstration's one such step, opening a copied assembly whose stored references point at a
folder renamed away, is W6's: W6-PLAN §7.1 runs it under a dialog watcher on the first copy of its master, on 2026 and
on 2024, before its own sections depend on it, and W7 reuses `copy_built`. If W6 dropped the copy route, every W7
section builds its fixture fresh. Everything the app calls in W7 has been called before (§2.9), and the new
combinations were made by the spike on 2026 without a dialog or an error.

---

## 8. Definition of done, and the order of work

1. W6 closed; this revision's points reviewed if the orchestrator asks; a `W7-DECISIONS.md` holding the rulings.
2. I committed and reviewed; `W7-INTERFACES.md` names its base commit and restates W6's shapes.
3. A, B, C in parallel; each reviewed; fixes in. B's second pass. D after; reviewed. Suite green on a clean `git
   archive` (`PYTHONPATH=src .venv/bin/python -m pytest -q`) and the Windows Tk tests.
4. E's full run on 2026 (`p1`–`p7`, window). What fails is probed in one follow-up round, fixed, and only the affected
   sections rerun; then one full run at the phase's close. J20's finding committed from that run's evidence.
5. SolidWorks 2024: `p1`, `p5`, window; what fails there fixed then.
6. The person's drag on both versions; the result recorded.
7. HANDOFF's W7 row closed, with what was left open, §3.1's readings and §3.2's list for the user.

PLAN-WORKBOOK §6's demonstrable — *"A 4 : 1 planetary with the ring fixed builds"* — is `p1`'s build, measured, and
driven at 4 : 1 the right way.

---

## 9. Risks, and what reading could not determine

1. **Measured, no longer a risk on 2026:** how SolidWorks treats a gear mate whose axis rides a carrier (`W7-SPIKE.md`).
   Not measured: 2024 (the confirming run), and the cases the spike left out, each now a section: a held sun (p5), a
   held carrier (p7), a Z- carrier (p6), a carrier whose globals Update changes and a put on a carrier train (p3).
2. **Puts on a carrier train.** A put of the carrier, and of copies mated to its axes, with the gear mates on, is
   unprobed; `place_component`'s read-back and the post-check make a failure a sentence; p3 shows it, three times.
3. **SolidWorks' swing on a carrier move** (p3's third edit) is put right by the puts if they hold.
4. **Three coincident axes in the layout part** (S, C, R through the same base planes). The spike's layout held one
   axis with the carrier coaxial to it, never three layout axes on one line; expected harmless, the build shows it.
5. **The ring's Flip**: wrong with Flip False on 2026 in the spike and remade right; every gear mate is read back, so
   2024's opposite need (W5's ring finding) is handled the same way.
6. **W6 underneath.** W7 edits `geometry`, `kinematics`, `checks`, `layout`, `motion` after W6 has; it assumes of W6
   only what §5.3 restates. If W6 changes one of those shapes at its close, I restates it.
7. **The demonstration's copy route** is W6's; if W6 dropped it, W7 builds every section fresh (time, not correctness).
8. **Memory and time on 2024:** five builds of 7–8 components and up to 16 mates in the full 2026 run, two on 2024.
9. **Not determined from reading:** every `ui_text` footer state a planetary record passes through (C reads them all);
   whether `store._entries` reads a nested `ShaftEntry` list in a new entry type unchanged (C); how
   `workbook_assembly_check.py`'s `drive_job` compares a component's origin (it must compare carried origins for
   copies; E).

---

## 10. Changes after the review and the spike

Review: `W7-PLAN-REVIEW.md` (`939b726`). Spike: `W7-SPIKE.md` (`8a798fe`). Rulings: the orchestrator, 2026-11-14.

**From the spike.**
- §2.7 records what was measured: J5's set turned the 4 : 1 right on 2026 (carrier +7.5°, planets −15° / −22.5° on
  C, ring 0), every status 1, no interference on all six meshes, one planet or three alike, save and reopen holding;
  both kinds of gear mate read back right on a moving axis, the ring mate wrong with Flip False and right remade.
- §2.9: the kinematic fallback is **removed** (it turned the planets −3.75° on SolidWorks), and with it interpretation
  A's alternative set and the follow-up probe M6 would have designed. §3.2's STOP on both routes failing is gone.
- §9 risk 1 rewritten as measured; the spike's uncovered cases each became a section (p3, p5, p6, p7).

**Must-change.**
- **M1** (accepted as written): `train_check` and `_trains` take the held gears a recorded gear mate touches
  (`held`), judged in the check phase and the post-check; a gear-mated held member is re-placed **before** the
  carrier and the train; `MotionUpdate.held` pinned; fake tests for both scenarios (§2.9, §2.10, §5.3, §5.4).
- **M2**: §2.3 rebased on the current ring/shift checks (`d3f4dcf`, `9efde87`; `ring-shift-2026-20261114-185630.log`).
  A shifted planet is no longer a blanket error: the plan says what the existing checks give a planetary (working
  centres both sides, the shift-too-large error, the tips warning) and what W7 adds; the `z_r` sentence applies only
  unshifted; J9 rewritten.
- **M3**: every fix withheld on a planetary mesh, with the reason (§2.3 item 6); tests for Ring 56 and a Sun–Planet
  centre error.
- **M4**: J4 follows PLAN-WORKBOOK — offsets and the planet's Axis composed in the carrier's frame; Z- carriers are
  built, not refused (§2.1, §2.6), and shown by p6 (§4.3). The carrier part's local coordinates are now the typed
  offsets turned by ψ_k on either sense.
- **M5**: p3 drives and deletes before each edit, asserts the put order and every frame back at the built frame, and
  adds the Ring At edit that re-places the held member after a turn; fake tests for the same.
- **M6**: the follow-up probe is no longer needed for the base case; p1 (every section) keeps measuring in a refused
  assembly as a guard (§6).

**Should-fix**, each taken:
- **S1** `Placed.shaft` is the copy's own shaft id; `listed` is the expanded meshes (§2.2).
- **S2** the `z_r` sentence's condition: simple, unshifted, `z_r ≠ z_s + 2z_p`, replacing whichever centre errors.
- **S3** the neighbour sentence: "5 is the most that fit; of those 1, 2, 3 and 4 also mesh"; the list includes 1.
- **S4** a carrier exempt from "carries no gear".
- **S5** one shared Face Z global, added once; `BuildPlan.check()` refuses a duplicate global; `face_globals` once.
- **S6** gear mates chosen by exact rank of the carrier-frame rows; a carrier gear meshes nothing in what W7 builds
  (§1.2), so the carrier is never a node, and the rank rule stays right if a later pass opens J8 (c).
- **S7** `CarrierLink.planets` holds every gear on the carrier's planet shafts.
- **S8** p3's value edit is teeth (Sun 21, Ring 57, P X 19.5: 3.714 : 1), so unequal sun and planet teeth are built
  and driven.
- **S9** moot: the fallback is removed.
- **S10** the carrier-held control is section p7 (§4.4).
- **S11** `interferences()` with Drive at 120 in every driven proof.
- **S12** the fake judges over-definition by rank, not by the planner's rule.
- **S13** the copy protocol is W6's `copy_built`, plus the `documents()` name check before each open; E0 is gone (§7).
- **S14** §2.10's three rows: a Checks error for a broken condition, the carrier Z bringing a front face to the Front
  plane structural, a planet X/Y edit valid only with the teeth or module that keep both centres.
- **S15** §5.3 restates W6's shapes and writes the carrier row in W6's own-axis form (§2.5).
- **S16** with the orchestrator's ruling: J11 and J12 refused at Build and listed for the user.

**Notes taken:** `still_shafts` never names a mounted shaft (§2.7); a ring's θ compared modulo its pitch (§2.4, §4.1);
a gear on C meshing its own planets is covered by the refusal of a carrier gear on Meshes; helical and herringbone planetaries are refused rather
than given a spec test, under the scope principle.

**Other rulings and alignments.**
- **Scope principle** (the J11/J12 ruling applied throughout): beyond J11 and J12, W7 also refuses a gear on the
  carrier's shaft that meshes (J8 (c)), opposite-facing members, helical and herringbone planetaries and two stages in one workbook,
  since no section builds them (§1.2, §3.2). This goes further than the ruling's letter; it is its reason applied the
  same way everywhere, and each item is listed for the user.
- **Schema:** `LINK_SCHEMA_VERSION = 5`, the constant named and read by code and tests, no other phase's number
  hard-coded (§2.11).
- **A small sun** (§2.3 item 7): what `0f5a121` and `small-pinion-2026-20261114-184220.log` mean for a planetary, and
  the warning and clause W7 adds.
- **W6 names** (§5.3): `copy_built`, `swcom.sense_reading` and `Session.gear_mate_sense(handle, same_sense, axes)`,
  `senses` / `mate_senses` in place of `internal` / `ring_meshes`, `MateEntry.sense` holding the carrier-frame sense,
  `MateEntry.plane` `"front"` for copies' along mates, `geometry.base_frame` for the carrier's frame, `Placed.axis`
  and `centre` set per copy; `CarrierLink.axis` as a W6 vector in place of `sigma`.
- **Not taken:** nothing from the review or the rulings is left out.

**After the W8 check** (the orchestrator, after `c6df0a4`: W8 builds on W7, and its E4 fixture's low range is a
planetary). Read against `W8-PLAN.md` (`9e1937f`) §0.2 and §2.1:

- **A gear on the carrier's own shaft — needed.** E4's `LoDog` (a dog, Shaft `Carrier`, At 70) sits on the carrier's
  shaft, and W8-PLAN §0.2 counts on W7 locking it to the carrier (*"LoDog locked to Carrier carrier"*, from J8 as
  first written). `c6df0a4` had refused it. J8 is restored as (a): locked to the carrier skeleton, meshing nothing; how
  it is mated (§2.7's table: a lock, carrier first, no axis or along mate), judged (a `LockLink` to the carrier, exact,
  §2.9) and put (lock suppressed around the train's puts, put to its own wanted frame, lock on again in a `finally`,
  §2.9); held with a held carrier (§2.7). Shown by p1's new `CarrierGear` (§4.1), driven with the rest and read
  against the carrier's turn, and by p3's puts and p7's held carrier (§6). A carrier gear on Meshes stays refused
  (J8 (c)); E4's `LoDog` meshes nothing (its coupling to Rear is W8's own gear mate, per mode).
- **A second gear on the sun's shaft — ordinary W5.** E4's `InDog` on In beside `Sun` is a follower locked to In's
  anchor `Sun`, as W5 builds every compound shaft; nothing new (§1.1). The same holds for a second gear on a turning
  ring's shaft; on a held ring's shaft it is held (W5-PLAN D9). E4's ring shaft carries only `Ring`.
- **Other frame shafts on the carrier's axis — needed and allowed.** E4's Rear and FrontDrv lie on the carrier's
  axis without being members of the stage; §1.1 now says such shafts are built as any frame shaft, with §2.3 item 5's
  coaxial exemptions. The first revision's last §1.2 row, which could be read as refusing them, is gone.
- **Two stages in one workbook — not needed.** E4 has one carrier; the refusal stays.
- **Members facing different ways — not needed.** Every E4 axis is Z+ (W8-PLAN §0.2: *"every axis is Z+"*); the
  refusal stays.
- **The mate count.** W8-PLAN §0.2 assumes W7's union-find over bodies with still bodies merged; the rank rule this
  revision adopted (review S6) chooses the same joins on every case W7 builds, E4's included (its planetary is §4.1's
  shape at 24/24/72), which `W8-INTERFACES.md` should restate.
- **Kept for the user**, as a later pass could open (§3.2): differentials, compound and double planets, a carrier
  gear that meshes, helical and herringbone planetaries, opposite-facing members, two stages, J4 (a), J5 (c).
