# W8 (sleeves and modes): the implementation plan

**Authority and reading order.** `docs/PLAN-WORKBOOK.md` is the authority (§1's `sleeve` and `dog` kinds, the
`Slides` column and the Modes sheet; §3.4's refusals; §3.5; §4.4–§4.5; §6's W8 row: *"Sleeve and dog kinds, Slides,
Modes → configurations — The E4 transfer case's four modes; own sub-plan and probes (per-configuration mate
suppression)"*). Then `notes-workbook/W5-DECISIONS.md`, whose rulings W8 inherits unchanged (a refused mate stops the
build; Update puts a turned train back whole; no datum plane; D10), then this plan. The design canvas
(<https://claude.ai/artifact/XQ4UL6FgR1BH6a15g1ArJj>, boards **E3**, **E4** and **F4**) is what the user approved
for the format; where this plan departs from it, it says so and why (PLAN-WORKBOOK, Context: "raise it rather than
choosing"). W5-PLAN is the model for this plan's shape.

W8 is built after W6 and W7, which are being planned in parallel. §0.2 says what W8 takes from them; everything else
here is written against the code on `workbook` at `0f5a121` (W5 closed, the small-pinion tip cap merged).

Rules carried over (HANDOFF, *Rules carried over*), unchanged: commits by explicit path only, prose messages with the
why, no Claude co-author or attribution line, never `add -A` / `commit -a` / stash / reset; findings read only from
committed `findings.py` with `getattr(findings, NAME, None)`, a missing one refused with a sentence; every raise a
full sentence; the repo is public. **Testing (the user, 2026-11-14):** written against the fake, then the full build
on SolidWorks 2026 early; what that build gets wrong is probed step by step; a call is probed *ahead* only when it is
new to the app and could hang, raise a dialog, or damage a file or a session (§4 lists exactly those); SolidWorks
2024 gets one confirming build at the phase's end. One follow-up probe round. The user is away and has said to carry
on through W8 without stopping: every judgement call below names the reading the work proceeds with (§0.3), and
those go to the user afterwards as readings they may overrule.

---

## 0. Summary

W8 makes three things buildable that are read, checked and refused today: the **sleeve** and **dog** kinds, gears
that **slide** (the `Slides` column), and the **Modes** sheet. A sleeve is an internal spline ring that turns with its
shaft and slides along it; a dog is a ring of external teeth fixed to its shaft. Slid over a dog, a sleeve locks the
dog's shaft to its own. Each mode places every slider at one of its named positions; what each mode engages is worked
out from the overlaps, never typed (canvas F4). Each mode becomes an assembly configuration; the first Modes row is
the one the assembly opens in. In SolidWorks each configuration holds its sliders at their positions with distance
mates of its own and has the couplings it engages switched on, everything else switched off; the train turns in every
configuration as W5's does.

### 0.1 What W8 adds, what stays refused, and what exists

**What exists today, read from the code.**

- *Format and read.* `schema.KINDS` already lists `sleeve` and `dog` (`workbook/schema.py`); `Gear.slides` is read
  and parsed by `model.parse_slides` (`"H=-10, N=0, L=+10"` → `{name: offset}`, a name twice or a piece that is not
  `name=offset` refused with a sentence); the Modes sheet is read by `model._read_modes` into `Mode(name, positions,
  notes, row)` and `GearboxSpec.sliders` (its middle columns, in order); the read's validation (`model.py`, after
  the meshes) refuses a slider column that is not a gear or has no Slides, a mode named twice, and a pick that is
  not one of the slider's positions. A blank pick is skipped there. `model.to_book` writes the Modes sheet with a
  data-validation list per slider column. `link.py` reports a mode added, removed or changed in the change list.
  `tests/test_workbook_model.py`'s `transfer_case()` is a read-and-round-trip fixture with the E4 rows, its shafts all
  at the origin: it is not a gearbox that checks.
- *Refused today.* `gears.kind_for` returns None for `sleeve` and `dog` (`gears/__init__.py`: neither is in `KINDS`,
  and an internal spec looks only in `INTERNAL_KINDS`). `workbook/build.py`'s `LATER` and `later_rows` say each
  sleeve, dog, sliding gear and the modes as a later phase's warning (*"G4 slides: sliding gears are placed in phase
  W8, with modes, and it is checked only at its At until then."*, *"2H, 4H, N and 4L are modes: they become the
  assembly's configurations in phase W8."*), and `Assessment.lay_out_refusal` holds the layout and assembly back for
  any such row. `geometry.layout` leaves sleeves and dogs out (`LATER_KINDS`) and places a sliding gear at its At.
  `checks.overall_ratio` withholds the ratio for any box with modes (`MODE_KINDS`: *"it changes with the modes,
  worked out in phase W8"*). `export.py` notes a slider counted at its At only. `kinematics.solve` has no notion of
  a coupling.
- *SolidWorks.* Nothing about configurations is in `findings.py` beyond W5's `THIS_CONFIGURATION = 1` and
  `SUPPRESSION_ROUTE = "SetSuppression2 this configuration, None"`. `swcom.Session.set_mate_suppressed` suppresses in
  the active configuration only. Nothing in the app adds, activates, deletes or reads a configuration.

**What W8 adds.**

1. The `sleeve` and `dog` part kinds (§1.1), registered for the workbook only.
2. Slides: per-mode placement of every slider (sleeves and sliding spur, helical or herringbone gears) on a frame
   shaft along Z±, checked at every mode's positions (§1.2).
3. Engagement worked out per mode: a sleeve over a dog couples their shafts; a sliding gear meshes its listed partner
   only where their faces overlap (§1.3).
4. Kinematics, ratios, checks and phases per mode (§1.4–§1.6), and the Results sheet per mode.
5. The turning assembly with one configuration per mode: per-position distance mates, couplings and splines as 1 : 1
   gear mates, per-configuration suppression (§1.7–§1.9).
6. Update SolidWorks across configurations: classification, D10 per configuration, post-check per mode (§1.10).
7. The record at schema 4 (§1.11); the sentences, a mode chooser in the Speeds panel, boards (§1.12).
8. The demonstration on the E4 transfer case (§5).

**What stays refused, after W8.** PLAN-WORKBOOK §3.4's *"Refused at Build"* list names sleeves, dogs and modes as rows
a later phase builds; W8 is the last phase, so what W8 does not build is refused with a sentence that names no
phase — *"… is not built by this version of the app."* (reading J18):

- a slider, sleeve or dog on a shaft whose Role is `fixed`, or on a shaft held still through one
  (`motion.still_shafts`) — a sleeve braking a ring to the case is a real design, but its gears are fixed parts in
  W5's assembly and a slider needs mates;
- a slider, sleeve or dog on a turned axis (W6's), or on a shaft mounted on a carrier (W7's planets);
- a bevel gear that slides.

Errors, not refusals: a sleeve or dog listed on Meshes; a dog with Slides; a sleeve whose Side is `external` or a dog
whose Side is `internal`; a Helix angle or Profile shift on either; every per-mode error of §1.5.

### 0.2 What W8 assumes of W6 and W7

**The E4 transfer case needs W7 and not W6.** Canvas E4: *"The low range is E3's 4 : 1 planetary (sun on In, ring
held)."* So E4 has a carrier shaft, three planet copies mounted on it and a fixed ring; every axis is Z+. W8 assumes
W7, once built, provides:

- frame shafts sharing one axis (In, Carrier, Ring, Rear and FrontDrv all at the origin): several `"<Shaft> Axis"`
  through the same base planes in the layout part, and `checks._check_shafts` not warning that a gear "passes over"
  a coaxial shaft's axis at 0 mm (it does today, for any two coaxial shafts whose gears' spans overlap). If W7 has not
  exempted coaxial shafts, package B does (`d` below `layout.BASE_TOLERANCE`).
- `kinematics.solve` through a carrier (today it returns `later` for any mounted shaft), on which W8's per-mode
  solve builds;
- a gear row on the carrier's own shaft (E4's LoDog) held to the carrier: whatever stands for the carrier in the
  assembly (W7's skeleton part, the user's answer of 2026-11-14) and the gears on that shaft are one turning body.
  If W7 does not allow a gear row on a carrier shaft, package B adds it with W5's lock;
- W7's own mates (planets on carrier axes, its loop rule) are always on: W8 never suppresses them per mode.

**W8 stays independent of W7 where it can.** Package A and B are written and tested against a second fixture,
**TransferCase_Parallel** (§2.2), the same transfer case with its low range on a layshaft instead of a planetary: all
frame shafts along Z+, no carrier. It exercises every W8 mechanism, and the demonstration builds it first as the
shakedown (section `s0`, §5), so a fault in W8's machinery is never confused with one in W7's.

**Of W6** W8 assumes only that W5's AXIS and ALONG mates for ±Z shafts keep their meaning. Sliders on turned axes are
refused (§0.1).

**Starting commit.** The interface commit starts on the commit that closes W7 (its demonstration and review), named
in `W8-INTERFACES.md`, as W5's ruling M3 did for W4.

### 0.3 Readings the work proceeds with (the user may overrule)

Each is argued where it is used; the column says where.

| # | Reading | Instead of | § |
|---|---|---|---|
| J1 | **A sleeve is an internal spline ring and a dog an external one**, each the strip's own proven ring or spur plan at the row's teeth, module and face; **no fork groove, hub, chamfers, back-cut or synchro cone**. | A skeleton-only sleeve and dog, as the user chose for W7's carrier; or canvas E4's sleeve *"with a groove round it for the shift fork"*. | 1.1 |
| J2 | A blank Pressure angle on a sleeve or dog is **30°** (canvas E4's spline), not the Box's. | The Box's 20°. | 1.1 |
| J3 | A sleeve's teeth are always inside, a dog's outside; Side, Helix angle and Profile shift that say otherwise are errors. | Allowing helical splines or shifted splines. | 1.1 |
| J4 | **Engaged means full overlap**: a dog is engaged when the sleeve covers the dog's whole face; partial overlap is an error at that mode's cell; no overlap is disengaged. The same for a sliding gear and its listed partner (the narrower face covered). | Any overlap engaging. | 1.3 |
| J5 | A blank Modes cell is the slider's position whose offset is 0; a slider with none is an error at the cell. | The slider at its At whatever its positions. | 1.2 |
| J6 | Mode names follow the gear-name rule (letters, digits, `_`, `-`) and are unique ignoring case: they become configuration names. | Any text. | 1.2 |
| J7 | **Each slide position is held by its own distance mate** with its own assembly global, switched on only in the configurations that use it. | Configuration-specific dimension values or equations (GOTCHAS §26: `Add3` and `SetEquationAndConfigurationOption` refused). | 1.7 |
| J8 | **A coupling (a sleeve over a dog) and a spline (a slider turning with its shaft) are 1 : 1 gear mates between collinear axes**, read back and turned round as a ring's gear mate is. Canvas E4 says the configurations *"switch off the locks"*; a lock is not used. | A lock per engagement (it also holds the sleeve along the shaft and fights its slide mate: tier 8, a locked gear with an axis mate over-defines); an angle mate (0° degenerate, and with an odd tooth count a 180° flip lands tooth on tooth). | 1.7 |
| J9 | A shaft's anchor is its **first non-sliding gear**; with none, its first slider (a *sliding anchor*: axis mate and slide mates, no ALONG). Every other slider has an axis mate, slide mates and a spline to the anchor. | — | 1.7 |
| J10 | **One configuration per mode, named as the mode**, made after the always-on mates; each per-mode mate made while the first configuration using it is active; suppression set explicitly in every configuration and read back; configurations of the template that are not modes deleted before the save; the assembly saved in the first mode. Sliders but no Modes rows: no configuration is added. | Renaming the template's configuration (`IConfiguration.Name` put, unverified). | 1.8 |
| J11 | **Rotations are shared between configurations** (GOTCHAS §83): a train turned in one mode and then switched to another can show a dog tooth on tooth with its sleeve; Update puts the train back (W5's answer 2), and the footer says so. | — | 1.9 |
| J12 | **D10 per configuration:** a recorded mate found suppressed in a configuration where the record has it on is turned back on there; one found on where the record has it off is suppressed again there; both said. An unsuppressed mate not on record in any mode's configuration refuses the Update (W5 M7). | Leaving per-configuration differences alone. | 1.10 |
| J13 | Update works in the **configuration active when it opens** the assembly, refuses before changing anything when that is not one of the gearbox's, and visits the other modes' configurations to post-check only after it changed something, returning to the one that was active. | Switching configurations on every press. | 1.10 |
| J14 | **Update carries** a slide offset or a slider's At (its slide globals), and W5's edits; **structural** (Build again…): any change to the Modes sheet but its row order, a position added, removed or renamed, a gear gaining or losing Slides or becoming or ceasing to be a sleeve or dog, any edit that changes what engages in any mode, a slide position's front face reaching, leaving or crossing the Front plane. Row order alone changes nothing in SolidWorks and is said. | A Modes pick changed between existing positions as a suppression-only Update. | 1.10 |
| J15 | **Loops per mode:** always-on relations first, then the mode's sliding meshes, then its couplings, in sheet order; one that joins two bodies already joined in that mode is left off there (W5's D6), an inconsistent one is a jam. | — | 1.4 |
| J16 | A member free in a mode (neutral; "front not driven") is not a problem: the Speeds panel says it. A jam in any mode is an error at that mode's row. | Warning about every free member. | 1.5 |
| J17 | Torque per mode: a coupling is a lossless 1 : 1 link, a branch that reaches no output carries none, and nothing past a split is given (W3's rule). | — | 1.4 |
| J18 | What W8 does not build is refused with a sentence naming no phase (§0.1). | — | 0.1 |
| J19 | The Results sheet holds one block per mode. | Results of the first mode only. | 1.12 |
| J20 | Interference is judged in every mode, against a half-pitch control on each coupling (demonstration). | First mode only. | 5 |
| J21 | The window gets a **mode chooser in the Speeds panel** (canvas E4: *"Results get a mode switch in the app"*); the end view is unchanged, since a slide runs along the view direction. | A chooser for the whole window. | 1.12 |
| J22 | Two sliders on one shaft that overlap in any mode are an error; a sleeve long enough to bridge two dogs on its way between positions is a warning (canvas E4's *"it passes through neutral"*). | — | 1.5 |
| J23 | Mate and global names: `RangeSlv along Rear at H`, `RangeSlv Face Z at H`, `ModeSlv splined to RangeSlv`, `RangeSlv engages InDog`. | — | 1.7 |
| J24 | The demonstration builds each fixture once and starts later sections from a copy of the built folder, its references repointed by opening the copy's assembly once with the original folder moved aside and saving it (§5). | Building the fixture again per section. | 5 |

### 0.4 What needs the user

Nothing blocks W8. Two readings are closest to a decision of the user's and are put first when the readings go to
them: **J1** (the user chose a skeleton carrier in W7 "because every solid geometry may look different", and canvas
E4 draws a fork groove), and **J14** (whether a Modes edit should become an Update later).

### 0.5 STOP and ask (implementers)

- A SolidWorks call this plan does not tie to a finding or to the macro database's verified entries (§4), or a
  finding read differently from §4.
- Changing a shape `W8-INTERFACES.md` pins.
- On SolidWorks (package E): any modal dialog from a configuration call; a configuration whose suppression does not
  read back as planned; a slider not at its position to 1e-6 mm in its configuration; a coupling or spline gear mate
  that reads wrong both ways round (the build already stops on it — the stop is for the plan, J8 then needs a
  probe); a driven member off its mode's kinematics by more than 1e-6 relative or turning the wrong way; the
  wrong-sense control not caught; interference at the built turn in any mode, or a half-pitch control not caught.
- A W7 assumption of §0.2 that does not hold.

---

## 1. Design

### 1.1 The parts: sleeve and dog

**Geometry.** A dog is an external spline ring: the strip's spur plan (`SpurGear.plan`) at the row's teeth, module,
pressure angle and face, with its bore. A sleeve is an internal spline ring: the strip's internal spur plan
(`InternalSpurGear.plan`), its rim the Rim column or the ring's default (root plus six modules). Both plans are the
ones the strip builds and `probe/gear_pairs_check.py` has built on both versions; W8 writes no new solid geometry.
With equal teeth, module and pressure angle, a ring's tooth space is the external gear's tooth turned inside out
(`gears/internal.py`'s docstring), so the dog's teeth sit in the sleeve's spaces with the backlash and the radial
clearance both plans already leave: for 30 teeth, module 1.5, 30°, the dog's root is ⌀41.25 and the sleeve's tip
⌀42; the dog's tip ⌀48 and the sleeve's root ⌀48.75.

**Why teeth and not a skeleton (J1).** The user's reason for a skeleton carrier was that its solid "depends on the
gearbox at hand". For a sleeve and a dog the workbook specifies exactly what the teeth are — teeth, module, face — as
it does for a gear, and canvas E4 checks that *"sleeve, hub and dog teeth match"*. The teeth are the specified thing,
and the interference check in each mode is what proves a mode engages what it says and nothing else (a skeleton
would leave that to the mates' word). What does depend on the gearbox at hand is left out: the fork groove (its width
and depth depend on the fork), the hub the sleeve rides on, the way a dog ring joins its gear, tooth-end chamfers and
back-cut, synchro cones and blocker rings (canvas E4 already leaves out the last three). The same reasoning the user
gave for the carrier is applied to those, and not to the teeth. The canvas's fork groove is the one departure from
E4, said to the user with this reading; the existing `Groove (mm)` column (a herringbone's centre groove) is where a
fork groove's width would go if the user wants one later.

**As kinds.** A new module `gears/clutch.py` holds `SleeveKind` and `DogKind`, each `kind = "sleeve"` / `"dog"`,
delegating `derive`, `validate`, `variables`, `outline` and `plan` to `InternalSpurGear` / `SpurGear` on the spec
with `kind="spur"` (and `teeth_side="internal"` for the sleeve). They are registered in a separate
`WORKBOOK_KINDS = {"sleeve": …, "dog": …}` in `gears/__init__.py`, never in `KINDS`, because `gui.KIND_VALUES` is
`tuple(KINDS) + tuple(PLANNED_KINDS)` and the strip would offer them. `kind_for` looks in `WORKBOOK_KINDS` first,
before its internal branch (an internal sleeve spec would otherwise look in `INTERNAL_KINDS` and find nothing).
`spec.default_stem` names them `Sleeve_m1.5_N30` and `Dog_m1.5_N30`: today it would call a dog `Gear_m1.5_N30` and a
sleeve `Ring_m1.5_N30` (its `words.get(kind, "Gear")` and its ring rule), the same file names as a 20° spur gear or
ring of the same module and teeth, which `plan_parts` would refuse as two gears of one file name. The validation
adds, as errors at their cells: a sleeve with Side `external`, a dog with Side `internal`, a Helix angle or a Profile
shift on either (J3). `Gear.spec_values` gives a sleeve or dog a blank Pressure angle of `"30"` (J2) and a sleeve
`teeth_side="internal"`.

### 1.2 Slides and positions

A slider is any gear with Slides: a sleeve, or a spur, helical or herringbone gear that slides in and out of mesh.
A position is `name=offset`, the offset in mm along the shaft's Axis from the gear's At (`model.parse_slides`), so a
slider at position p has its face centre at `point + (At + offset) × axis` (`geometry._place` with `at + offset`).
A mode picks one position per slider; a blank pick is the slider's position whose offset is 0, and a slider with no
such position is an error at the cell: *"Modes!B4: RangeSlv has no position at 0, so a blank here does not say where
it sits; pick one of H and L."* (J5). With sliders and no Modes rows (PLAN §1), there is one implicit mode, every
slider at its 0 position, and no configuration is added. A Modes sheet with rows but no slider column is an error
(*"the Modes sheet has modes but no slider column"*). Mode names are checked like gear names and unique ignoring case
(J6), since they become configuration names. Positions no mode picks are read and checked but get no mate.

### 1.3 Engagement, worked out per mode

For each mode, with every slider at its pick:

- **A coupling** is a sleeve S and a dog D on two different frame shafts whose axes coincide (same X, Y within
  `layout.BASE_TOLERANCE`, axes parallel or antiparallel), with S's face covering D's whole face. Then S's shaft and
  D's shaft turn as one. Partial cover (0 < overlap < D's face) is an error at that mode's cell (J4); teeth, module or
  pressure angle that differ while they overlap at all is an error (*"RangeSlv (30 teeth, module 1.5) cannot engage
  LoDog (28 teeth): a sleeve and the dog it engages have the same teeth, module and pressure angle."*); one sleeve
  covering two dogs at once is reported by the kinematics as a jam, and said specifically. A sleeve and a dog on the
  same shaft engage nothing (a warning). Sleeves engage dogs only.
- **A sliding mesh** is a listed mesh with a slider among its two gears; it is in mesh in a mode when the narrower
  face is covered, out of mesh with no overlap, an error between (J4). A listed mesh in mesh in no mode is a warning.

`checks` gains, per mode, a `ModeReport` (shape pinned in §3.2): each slider's position and offset, the engaged
couplings, the meshes out of mesh, that mode's `Placed` for each slider, and that mode's `kinematics.Motion`.

### 1.4 Kinematics per mode

`kinematics.solve` gains a mode: the meshes out of mesh in that mode are left out and each engaged coupling adds a
row `ω̃_p − ω̃_q = 0` (projected speeds, as every row is, so a Z− shaft keeps its sense). The rank tells the rest
exactly, as now: settled, free (a member nothing drives in this mode), or jammed. Speeds are about each shaft's own
axis. Torque per mode follows W3's `_torques` with a coupling as a lossless 1 : 1 link, a branch that reaches no
output and no fixed shaft in that mode pruned (it idles), and nothing given past a split (J17). Loops per mode
(J15): the always-on relations (W5's meshes, W7's planetary, the splines) are joined first, then the mode's sliding
meshes, then its couplings, each in sheet order; one that joins two bodies already joined is off in that mode —
the record says so — and the kinematics has already called an inconsistent one a jam.

`checks.overall_ratio` becomes per mode: the first input to the first output joined to it in that mode, or *"neutral"*
when no output turns. `worked_out_as` names the modes: *"Parallel train with modes · 4 meshes · 2H 1.000 : 1, 4H
1.000 : 1, N neutral, 4L 4.000 : 1"* for the Parallel fixture (W7 supplies the planetary's words for E4).

### 1.5 Checks per mode

Each is a diagnostic at its cell; W5's answer 4 stands (the Checks panel lists problems only).

- *Errors:* a jam in a mode (*"Modes!A5: in 4L RangeSlv engages InDog and LoDog at once, which joins In to Carrier:
  as written the box is jammed in this mode."*); partial engagement; teeth that cannot engage; two sliders on one
  shaft overlapping in a mode (J22); a slider clashing with any gear in a mode (W3's `_check_clearances` run on each
  mode's placements, with every engaged coupling exempt and every coaxial sleeve–dog pair not engaged in that mode
  required to have no overlap at all); a sleeve or dog on Meshes; a dog with Slides; a blank pick with no 0 position;
  the refusals of §0.1 become errors only at Build, as warnings in Checks.
- *Warnings:* a dog no mode engages; a listed sliding mesh in mesh in no mode; a sleeve longer than the gap between
  two dogs within its travel (*"RangeSlv is 16 mm long and InDog and LoDog are 14 mm apart: on its way from H to L it
  would hold both at once."*, J22); an output that turns in no mode (W3's warning, now across modes); two modes that
  engage the same couplings and meshes (*"4H and 4X engage the same: they are one mode twice"*).
- *Not a problem* (J16): a member free in a mode. The Speeds panel says *"N: neutral — Rear, FrontDrv, Idler and Front
  turn freely."* and *"2H: … the front is not driven."*
- *Unchanged:* W3's checks on everything that does not slide, at its At. A slider is checked at each mode's position,
  never at its At alone, so `later_rows`'s *"checked only at its At"* goes.

### 1.6 Phases

`geometry.phases` walks the meshes from the first input as now, and also the couplings of every mode: an engaged
sleeve and dog need the dog's teeth in the sleeve's spaces, `g_S ≡ g_D + π/z (mod 2π/z)` in global space angles
(`Placed.space_angle`). Both parts are built with a space centred on +X; the sleeve's tooth sits half a pitch off it
and so must the dog's space. The condition holds for any σ, since ±π/z are the same modulo 2π/z. A spline puts no
condition on phase (no hub is modelled), and neither does a lock, so a dog's phase is free on its shaft and a sleeve's
on its own. A walk reaches each gear once, couplings visited after meshes and in the dogs' Gears-sheet order; a gear no
walk reaches starts a new walk at phase 0, in Gears-sheet order; a sleeve that reaches a dog already phased otherwise
is W3's loop-conflict warning. **Test:** in every mode, every engaged sleeve's and dog's `preview.layout` outlines,
turned and placed, do not overlap, and do overlap when the dog is turned half a pitch — the same test W3 holds the
meshes to.

### 1.7 The turning assembly with modes: mates

`motion.motion_plan` keeps W5's rules for everything that does not slide (D9, M9, D6 and the rest) and adds, per frame
shaft that is not still:

- **The anchor** (J9) is the first non-sliding gear in Gears-sheet order, mated as W5 mates it (AXIS, ALONG). With
  none, the first slider is a *sliding anchor*: AXIS, and a SLIDE per position its modes use, no ALONG.
- **Every other non-sliding gear** is locked to the anchor (W5).
- **Every other slider** gets AXIS (`RangeSlv on Rear Axis`, W5's axis-coincident route, `Unfix` straight before it as
  W5 does), a SLIDE per position its modes use, and a SPLINE to the anchor. A slider is never locked: a lock holds it
  along the shaft too.
- **A SLIDE** is W5's ALONG route at one position: `"point distance"` from the slider's origin to the layout's Front
  plane at that position's `z_front`, `D1` linked to an assembly global `"<Gear> Face Z at <position>"`, or
  `"point"` coincident at 0 (W5's rule, and W5's answer 3: a position's front face reaching, leaving or crossing the
  Front plane is structural). Named `RangeSlv along Rear at H`. On only in the configurations whose mode picks that
  position.
- **A SPLINE** is a gear mate at 1 : 1 between the slider's `Gear Axis` and its anchor's — two collinear axes —
  turning them the same way. Named `ModeSlv splined to RangeSlv`. On in every configuration.
- **A COUPLE** is a gear mate at 1 : 1 between the sleeve's `Gear Axis` and the dog's, the same way round. Named
  `RangeSlv engages InDog`. On only in the configurations whose mode engages that pair (and does not leave it off as
  a loop-closer, J15).
- **A sliding mesh's** gear mate is W5's MESH, on only in the configurations whose mode has it in mesh.

**Why gear mates for couplings and splines (J8).** A spline and a coupling hold one thing: the turn of one body to
another's, and nothing along the shaft, since the slide mates hold that. A lock holds all six freedoms, so a lock
between a sleeve and its dog fights the sleeve's slide mate (tier 8: a locked gear also mated to its axis
over-defines), and a lock re-takes the offset it finds when it is turned on (`LOCK_RETAKES_AN_OFFSET`, and the macro
database's assemblies/11) while positions are not kept per configuration (GOTCHAS §83), so it would hold whatever
position the last configuration left. An angle mate between Top planes holds a turn but is degenerate at 0°, and its
180° flip puts an odd-toothed sleeve tooth on tooth. A gear mate holds only the turn, keeps the relative angle it is
made at (a put with the gear mate on holds: `MESH_PHASE_ROUTE`), and everything around it is W5's: made under
`CommandInProgress`, renamed at once, its sense read back by `swcom.gear_mate_sense` and made again with the other
Flip if wrong, its remake route, its mate check. What is new is two collinear axes. `gear_mate_sense` accepts them
(it refuses only axes whose cosine is below 0.99, and computes `parallel` from the sign); "the same way" is the
condition W5 reads for a ring, so couplings and splines are passed as same-sense gear mates (in `build`'s
`internal`, `GearboxPlan.ring_meshes` widened to "the gear mates whose two gears turn the same way"). Whether
SolidWorks turns collinear gear mates as the read-back says is what the full build's drive shows first (§5); it is
not probed ahead (§4: it cannot hang or raise a dialog, and a wrong sense stops the build as a refused mate).

**Ratios for the record:** COUPLE and SPLINE `ratio` is `(1, 1)`; `mesh_links` gives a COUPLE `k = σ_S·σ_D` (both
turn the same way about the world, so about each own axis by the product of senses) and pitch `360/z_D`; a SPLINE
is a `LockLink` (tested exactly: no hub phase, the slider turns with the anchor). Both carry the modes they are on in
(§3.2), so `swbuild.train_check` judges in a configuration only the links on in it.

**Names** (J23): gear, shaft and position names are letters, digits, `_` and `-` (schema; `model._SLIDE`), so these
names cannot collide with each other or with W5's.

### 1.8 Configurations: the build order

`BuildPlan.check` requires exactly one rebuild and the save last (`gears/base.py`), and W5's assembly plan is one such
plan. W8 keeps it so: the assembly `BuildPlan` is W5's train plus the sliders' AXIS mates and the SPLINEs, with an
`AddGlobal` for every SLIDE global (assembly globals belong to no configuration), placed with every slider at its
first mode's position. The configurations are a second, pure structure handed to the worker beside it: a
`ModesPlan` of one `ModeStep` per mode (§3.2). `build_gearbox(..., modes=ModesPlan)` runs, inside the same job and
document, after W5's run, rebuild, verify and mate check, and **before the save**:

1. `configurations()` read: the template's own configurations (normally `Default`).
2. A configuration per mode, in Modes-sheet order: `add_configuration(name)` (`AddConfiguration2(name, "", "", 0,
   "", "", True)`, which also activates it; the macro database's assemblies/07, verified on 2024), the active name read
   back. A mode whose name equals one of the template's configurations (ignoring case) uses it instead. No per-mode
   mate exists yet, so every configuration is the same consistent train with its sliders free along their shafts.
3. For each mode in order: `show_configuration(name)` (`ShowConfiguration2`, the active name read back: GOTCHAS §23)
   unless it is active, and the train's rebuild; each slider put at its frame in this mode (`place_component`, a
   put along its own axis with its spline and any coupling on: `MESH_PHASE_ROUTE`), so each new mate is made where
   its gear stands, as W5's were; then this mode's mates not made yet (the step's ops: SLIDEs with their
   `LinkDimension`, COUPLEs, sliding meshes), each made under `CommandInProgress`, renamed at once and, for a gear
   mate, its sense read back and turned round if wrong (W5's `_settle_sense`); then, for each mate just made,
   `set_mate_suppressed_in(name, True, <every configuration whose mode does not use it, and the template's>)` and
   `set_mate_suppressed_in(name, False, <every configuration whose mode uses it>)` (`SetSuppression2(action, 3,
   names)`; assemblies/07, verified on 2024), read back with `mate_suppression(name, <every configuration>)`
   (`IsSuppressed2(3, names)`) against the plan — a mate made while one configuration is active can come out the
   inverse of what was meant (assemblies/07), and the read-back catches it. Configuration k is activated holding only
   the always-on mates and the mates made so far that are on in k, a subset of k's own, so no configuration is ever
   activated over-defined.
4. **The mate check per mode:** for each mode, show it, rebuild, and check as W5's `_check_mates` does with this
   mode's lists: every mate on in it present, unsuppressed, error code 0 (any number logged, never interpreted);
   every per-mode mate off in it reads suppressed (and is not judged by its code: GOTCHAS §103); every mated gear
   `COMPONENT_UNDER_DEFINED`; every slider's frame at its position (`_verify`'s tolerance). A problem is a sentence
   in `BuildResult.mate_problems` beginning *"In mode 4L, …"*, so W5's rule holds unchanged: a refused mate stops the
   build, nothing is saved, the document is left open and named, and Build waits for a changed workbook.
5. Show the first mode; `delete_configuration` for each of the template's configurations that is not a mode
   (`DeleteConfiguration2`, names read back; verified on 2026 SP1.1 in the macro database's ledger); rebuild; save.
6. Interference, after the save as W4 does it, **once per mode**: show it, `interferences()`, and finally show the
   first mode again. A clash in a mode is a CHECK naming the mode and the gears.

**What a configuration holds**, read from GOTCHAS §83 and assemblies/07: suppression, not where free components sit.
So every position is held by mates (the SLIDEs), and every configuration holds a complete set: in each mode every
slider has exactly one SLIDE on. With sliders and no Modes rows, steps 1–6 are skipped: each slider's one SLIDE is
an always-on mate in the plan, and the assembly keeps the template's configuration.

### 1.9 Turning, and a change of configuration

A train turns in a configuration exactly as W5's does: one freedom per train in that mode (a free member in neutral
is a train of its own, as an unmeshed shaft is in W5), the drag gear the input's anchor. **Rotations are not stored
per configuration** (GOTCHAS §83: neither are positions; the SLIDEs hold those). Switching configuration re-solves
with the new mate set from wherever the gears stand. At the built turn every coupling of every mode is in phase
(§1.6), so every configuration shows its dogs in its sleeves. After the user turns the train in one mode, members
that mode left free stand still while the others turn, so in another mode a newly engaged coupling holds whatever
relative angle it finds — a gear mate keeps the relative angle it finds (`MESH_PHASE_ROUTE`) — and SolidWorks can
show a dog tooth on tooth with its sleeve (J11). That is also what a real dog clutch would meet; the app does not hide
it. In that configuration `train_check` finds the coupling out of step (a MeshLink, judged modulo the dog's pitch),
and Update puts the whole train back to its built turn (W5's answer 2, ruled train by train: M1). The footer says so
when it happens (§1.12).

### 1.10 Update SolidWorks with modes

**Classify** (`update.classify`, B; J14). A record with `modes` (schema 4) adds, to W5's rules:

- *Update:* a slide offset or a slider's At or face width (its SLIDE globals, each `|z_front|` at its position);
  W5's edits on everything else (part values, layout moves, a follower's At, a meshed tooth change by the remake),
  including a sleeve's or dog's teeth, module or face when the pair still matches and nothing engages differently.
- *Structural* (each with its sentence): any change to the Modes sheet but its row order — a row added, removed or
  renamed, a pick changed, a slider column added or removed (*"The Modes sheet changed (4H now puts ModeSlv at 2WD),
  and which mates each configuration holds was set when the assembly was built, so it needs a new revision."*); a
  position added, removed or renamed; a gear gaining or losing Slides, or becoming or ceasing to be a sleeve or dog;
  any edit after which some mode engages other couplings or other sliding meshes (*"In 4L RangeSlv would now engage
  nothing (its position L moved off LoDog), so it needs a new revision."*); a position's front face reaching, leaving
  or crossing the Front plane (W5's answer 3, naming the edit).
- *No change in SolidWorks:* the Modes rows reordered. The assembly opens in the configuration it was saved in; the
  footer says the next Build again… would open in the new first mode.

`MotionUpdate` gains the configurations on record, the wanted and recorded placements per mode, the slide globals
wanted, and each recorded mate's modes; `MeshLink` and `LockLink` gain the modes they hold in (§3.2).

**The worker's order** (A), W5's motion path with these changes:

*Check — writes nothing.* Open the assembly (`UPDATE_OPEN_ROUTE`); `active_configuration()`; a recorded mode missing
from `configurations()` → `NotAsBuilt` (*"The configuration 4H is not in TransferCase.SLDASM any more: it was renamed
or deleted in SolidWorks."*), so the window offers Build again…; a configuration the record does not know is left
alone and listed; the active configuration not one of the gearbox's modes → `BuildError` before anything changes
(*"Update SolidWorks works in one of the gearbox's own configurations (2H, 4H, N and 4L), and Exploded is active in
SolidWorks: pick one of them and press Update SolidWorks again."*, J13). Then W5's reads, in the active configuration:
components, every frame, every recorded mate found (`MateGone` → `NotAsBuilt`), `mate_states()`. **Suppression is read
for every recorded mate in every mode's configuration** with `mate_suppression(name, modes)` — no configuration is
activated — and compared with the record: on where its modes say on, off elsewhere (always-on mates on everywhere).
An unsuppressed mate not on record, in any mode's configuration, refuses (M7, read the same way). `train_check` in the
active mode, with that mode's links and wanted frames. Gear mates' senses are read for the gear mates on in the
active configuration only: a per-mode gear mate off here is off on purpose, and W5 reads a suppressed mate's sense
only once it is back on.

*Change — nothing raises out (W4's B1).* As W5: part and layout values; rebuild; then **D10 per configuration (J12)**:
each recorded mate found off where the record has it on is turned on there, each found on where the record has it
off is suppressed there, both with `set_mate_suppressed_in` and read back (never a call on a mate already in the
wanted state: W5's ruling, `UNSUPPRESS_ON_LOCK_ALREADY_ON_MARKS_MODIFIED`); then the Face Z and slide globals; then
the puts, in the active configuration, every mated gear of a train that needs one with its locks suppressed in this
configuration around them (W5's M1, M8). A slider is put at its frame in the active mode. Puts set rotations, which
every configuration shares, and the SLIDEs carry each slider to its own position elsewhere.

*Post-check.* W5's, in the active configuration. **Then, only if anything changed**, each other mode in turn: show
it, the train's rebuild, its frames (sliders at their positions, every other gear at its wanted frame), its mates as
§1.8 step 4 judges them, the senses of the gear mates on in it, its interference; then show the configuration that
was active (J13). A quiet Update activates nothing. `GearboxUpdate.changed` gains the assembly when D10 per
configuration or a slide global changed anything (as W5's rule for step 3–5).

**How D10 lives with mates suppressed on purpose.** W5's D10 reads "a recorded mate found suppressed is turned back
on". In W8 the record says, per mate, the configurations it is on in; "found suppressed" means *found off in a
configuration where the record has it on*, and the mirror (found on where the record has it off) is put right too,
since such a mate can over-define that configuration the next time it is activated. A mate on in every configuration
(W5's, the splines, the sliders' axis mates) is exactly W5's D10, read in each configuration.

**`finish_update`** (B): SLIDE entries' `z_front` follow the slide globals set; the per-mode frames on record follow
what was put (a slider's per-mode frames from its SLIDEs); W5's rules otherwise.

### 1.11 The record (schema 4)

```python
LINK_SCHEMA_VERSION = 4

MateEntry += position: str = ""            # SLIDE: the position's name; "" for every other kind
          += modes: List[str] = []         # the configurations it is on in; [] = every configuration
GearboxRecord += modes: List[str] = []     # the configurations as built, in Modes-sheet order; the first is the one
                                           # the assembly was saved in; [] = no configuration was added
```

`MateEntry.kind` gains `"slide"`, `"spline"`, `"couple"`; the parse (C) refuses a kind outside the seven, gears not
as many as the kind holds (slide 1, spline and couple 2), a SLIDE without a position, a couple or spline whose ratio
is not `[1, 1]`, and a mate whose `modes` names a configuration not in `GearboxRecord.modes`. A v3 file reads as v4
with no modes; a v5 file is refused and left byte-identical; a W5-era reader refuses a v4 file (its newer-schema
sentence: W5's D11). The component frames on record are the first mode's; a slider's frame in another mode follows
from its SLIDE's `z_front`. `finish_build` (B) writes `modes` and every mate's `modes` and `position` from the plan.

### 1.12 Sentences and the window

House style as W5's: whole sentences, the workbook's words, true in every state, never a check that was not made.
C writes these (exact; `{…}` filled from fields):

- *Before Build* (`_ready_build`): *"It has {4} modes, {2H, 4H, N and 4L}: each becomes a configuration of the
  assembly, and it opens in {2H}."* · with sliders and no rows: *"{RangeSlv and ModeSlv} slide, but the Modes sheet
  has no rows, so the assembly has one configuration with each at its position 0."*
- *After Build* (`motion_done_line` with modes): *"Its gears are mated to turn in each of its {4} modes, one
  configuration each ({2H, 4H, N and 4L}), and SolidWorks reports no mate in error in any of them: it opens in {2H};
  pick a configuration and drag {Sun} in SolidWorks, and the rest of its train follow."*; the interference ending
  *"; no interference between the gears in any mode, where they stand"*, or a CHECK naming the mode.
- *Mate problems* (A writes them, C shows each whole): *"In mode {4L}, the mate {RangeSlv engages LoDog} over-defines
  the assembly."*, *"In mode {N}, the mate {RangeSlv along Rear at N} is not suppressed in {2H}, where it should be."*,
  *"SolidWorks would not make the configuration {4L}."*, *"In mode {4L}, {RangeSlv} is not at its position L
  ({66} mm from the Front plane) once the assembly rebuilt."*
- *Footer, on record:* *"It was built with a configuration per mode ({2H, 4H, N and 4L}): pick one in SolidWorks and
  drag {Sun} to turn it."* · after a reorder: *"The Modes rows are in another order now; SolidWorks still opens it in
  {2H}, and Build again… would make {4L} the configuration it opens in."*
- *Update summary:* *"slide {RangeSlv}'s position {L} along {Rear}"*.
- *After Update:* *"slid {RangeSlv}'s position {L} along {Rear}"* · *"turned the mate {RangeSlv engages LoDog} back on
  in {4L}"* · *"suppressed the mate {RangeSlv engages InDog} again in {4L}, where it was on"* · *"It worked in {4H},
  the configuration that was active, then checked {2H, N and 4L} and left the assembly in {4H}."* · with a coupling
  found out of step: *"In {4L} the gears had been turned in another mode, so {RangeSlv}'s teeth stood across
  {LoDog}'s; they are back at the turn they were built at."* · *"{TransferCase.SLDASM} also has a configuration the
  app did not make ({Exploded}); Update SolidWorks left it as it is."*
- *Progress:* *"Setting up the configuration {4L}…"*, *"Checking mode {4L}…"* (a new `STAGE_MODE`).
- *Speeds panel:* *"{4L}: Rear 375 rpm · Front 375 rpm · 4.000 : 1"*; *"{N}: neutral — {Rear, FrontDrv, Idler and
  Front} turn freely."*

**The window** (D; J21): when the workbook has modes, the Speeds panel's header gets a mode chooser (the theme's
segmented control, one button per mode, the first chosen), and the speeds, torques and ratio lines are that mode's.
The choice is kept across re-reads while a mode of that name exists. The end view draws sleeves and dogs through
`kind_for` (`preview.layout_gearbox`) at the chosen mode's placements; a slide runs along the view direction, so it
does not show there. The header counts modes (`workbook_counts`: *"8 shafts · 11 gears · 4 meshes · 4 modes"* for E4).
Export's Results sheet gets one block per mode, each headed with the mode's name (J19; `export.py`, B). Boards
(`design/canvas/gen.py`): `WorkbookModes` (the E4 fixture checked, the chooser on 4L) and `WorkbookModesBuilt` (the
built footer with the configurations); `UI-DESIGN.md` §9 gains the chooser and every sentence above, and its
later-row sentences for sleeves, dogs, slides and modes go.

---

## 2. The fixtures (every number pinned)

Both are written by a builder in `tests/workbook_fixtures.py` (B) through `model.to_book` and `xlsx.write_new`; the
demonstration writes the same file, opens it in its own Excel and saves it there before reading it (W5's
`keep_fixture` pattern). Every shaft is on the frame along Z+ unless said; the Box's pressure angle is 20° and its
efficiency 98 %. An independent subagent recomputes §2.3 from these tables alone before the tests are committed
(PLAN §3.5's rule).

### 2.1 The E4 transfer case (the PLAN's demonstration; needs W7)

Canvas E4's five rows, unchanged (Teeth, Module, At, Slides as drawn; faces 6 and 8 as `test_workbook_model.py`'s
`transfer_case()` and E4's *"dog rings 14 mm apart, sleeve teeth 8 long"*), E3's planetary as the low range, and the
front drive *"through an idler and an equal gear"*, its numbers chosen here.

**Shafts**

| Shaft | Mounted on | X | Y | Role | Copies | Speed | Torque |
|---|---|---|---|---|---|---|---|
| In | frame | 0 | 0 | input | | 1500 | 10 |
| Carrier | frame | 0 | 0 | | | | |
| Planet | Carrier | 24 | 0 | | 3 | | |
| Ring | frame | 0 | 0 | fixed | | | |
| Rear | frame | 0 | 0 | output | | | |
| FrontDrv | frame | 0 | 0 | | | | |
| Idler | frame | 50 | 0 | | | | |
| Front | frame | 100 | 0 | output | | | |

**Gears** (in this order; blank cells take their defaults)

| Gear | Shaft | At | Kind | Side | Teeth | Module | Face | Slides |
|---|---|---|---|---|---|---|---|---|
| Sun | In | 20 | spur | | 24 | 1 | 10 | |
| Pl | Planet | 20 | spur | | 24 | 1 | 10 | |
| Ring | Ring | 20 | spur | internal | 72 | 1 | 10 | |
| InDog | In | 50 | dog | | 30 | 1.5 | 6 | |
| LoDog | Carrier | 70 | dog | | 30 | 1.5 | 6 | |
| RangeSlv | Rear | 60 | sleeve | | 30 | 1.5 | 8 | H=-10, N=0, L=+10 |
| FrontDog | FrontDrv | 110 | dog | | 30 | 1.5 | 6 | |
| ModeSlv | Rear | 100 | sleeve | | 30 | 1.5 | 8 | 2WD=0, 4WD=+10 |
| FDrive | FrontDrv | 130 | spur | | 30 | 2 | 10 | |
| FIdler | Idler | 130 | spur | | 20 | 2 | 10 | |
| FOut | Front | 130 | spur | | 30 | 2 | 10 | |

**Meshes:** Sun–Pl, Pl–Ring, FDrive–FIdler, FIdler–FOut. **Modes** (canvas F4): 2H = (H, 2WD) *road*; 4H = (H,
4WD); N = (N, 2WD) *towing*; 4L = (L, 4WD) *crawl*.

Centres: Sun–Pl `1·(24+24)/2 = 24` = the planet's X; Pl–Ring `1·(72−24)/2 = 24`; FDrive–FIdler `2·(30+20)/2 = 50`;
FIdler–FOut `2·(20+30)/2 = 50` = 100 − 50. E3's assembly conditions hold: `72 = 24 + 2·24`, `(24 + 72)/3 = 32`.

### 2.2 TransferCase_Parallel (W7-free; packages A and B, and the shakedown)

The same, with the planetary replaced by a reverted layshaft train: a 15-tooth pinion on In drives a 30-tooth gear on
the layshaft, whose 15-tooth pinion drives a 30-tooth gear on Lo, a shaft on In's axis carrying LoDog.

| Shaft | X | Y | Role | Speed | Torque |
|---|---|---|---|---|---|
| In | 0 | 0 | input | 1500 | 10 |
| Lay | 0 | −45 | | | |
| Lo | 0 | 0 | | | |
| Rear | 0 | 0 | output | | |
| FrontDrv | 0 | 0 | | | |
| Idler | 50 | 0 | | | |
| Front | 100 | 0 | output | | |

| Gear | Shaft | At | Kind | Teeth | Module | Face | Slides |
|---|---|---|---|---|---|---|---|
| InPin | In | 10 | spur | 15 | 2 | 10 | |
| InDog | In | 50 | dog | 30 | 1.5 | 6 | |
| LayGear | Lay | 10 | spur | 30 | 2 | 10 | |
| LayPin | Lay | 30 | spur | 15 | 2 | 10 | |
| LoGear | Lo | 30 | spur | 30 | 2 | 10 | |
| LoDog | Lo | 70 | dog | 30 | 1.5 | 6 | |
| RangeSlv | Rear | 60 | sleeve | 30 | 1.5 | 8 | H=-10, N=0, L=+10 |
| FrontDog | FrontDrv | 110 | dog | 30 | 1.5 | 6 | |
| ModeSlv | Rear | 100 | sleeve | 30 | 1.5 | 8 | 2WD=0, 4WD=+10 |
| FDrive | FrontDrv | 130 | spur | 30 | 2 | 10 | |
| FIdler | Idler | 130 | spur | 20 | 2 | 10 | |
| FOut | Front | 130 | spur | 30 | 2 | 10 | |

**Meshes:** InPin–LayGear, LayPin–LoGear, FDrive–FIdler, FIdler–FOut. **Modes:** as §2.1. Centres: both layshaft
meshes `2·(15+30)/2 = 45` = |Y| of Lay.

### 2.3 The answer key

**Where the sliders sit** (face centre z = At + offset; front face z_front = z − face/2; the dog faces InDog 47–53,
LoDog 67–73, FrontDog 107–113):

| Slider | Position | z | Face span | Covers | SLIDE global |
|---|---|---|---|---|---|
| RangeSlv | H | 50 | 46–54 | InDog, whole (6 of 6) | `RangeSlv Face Z at H` = 46 |
| RangeSlv | N | 60 | 56–64 | nothing (3 mm clear each side) | `RangeSlv Face Z at N` = 56 |
| RangeSlv | L | 70 | 66–74 | LoDog, whole | `RangeSlv Face Z at L` = 66 |
| ModeSlv | 2WD | 100 | 96–104 | nothing (3 mm short of FrontDog) | `ModeSlv Face Z at 2WD` = 96 |
| ModeSlv | 4WD | 110 | 106–114 | FrontDog, whole | `ModeSlv Face Z at 4WD` = 106 |

InDog and LoDog are 67 − 53 = 14 mm apart and RangeSlv is 8 long: no stroke bridges them. The two sleeves on Rear never
overlap (RangeSlv ends at 74 at most, ModeSlv starts at 96 at least).

**What each mode engages:** 2H: RangeSlv–InDog. 4H: RangeSlv–InDog, ModeSlv–FrontDog. N: nothing. 4L:
RangeSlv–LoDog, ModeSlv–FrontDog.

**Speeds**, rpm, each about its own shaft's axis (+Z here), input In at +1500. In every mode: E4 Carrier +375 (ring
fixed: `1500/(1 + 72/24)`), Ring 0, the planets −750 absolute (−1125 relative to the carrier: W7's convention decides
which the Speeds panel shows); Parallel Lay −750 (`−1500·15/30`), Lo +375 (`+750·15/30`).

| | Rear | FrontDrv | Idler | Front | In : Rear | In : Front |
|---|---|---|---|---|---|---|
| 2H | +1500 | free | free | free | 1.000 : 1 | front not driven |
| 4H | +1500 | +1500 | −2250 | +1500 | 1.000 : 1 | 1.000 : 1 |
| N | free | free | free | free | neutral | neutral |
| 4L | +375 | +375 | −562.5 | +375 | 4.000 : 1 | 4.000 : 1 |

(Idler: `−ω_FrontDrv · 30/20`; Front: `−ω_Idler · 20/30`.) These are canvas E4's *"rear 1500 · front not driven"*,
*"rear 1500 · front 1500"*, *"neutral · outputs free"*, *"rear 375 · front 375 (4 : 1)"*. The rear output turns the
same way as the input in every mode that drives it; so does the front.

**A 30° drive of the input** (δ = 30° · ω/1500; free members must not turn): 2H Rear +30°, front members 0; 4H Rear
+30°, FrontDrv +30°, Idler −45°, Front +30°; N Rear and front members 0, E4 Carrier +7.5° / Parallel Lo +7.5°, Lay
−15°; 4L Rear +7.5°, FrontDrv +7.5°, Idler −11.25°, Front +7.5°.

**Torque** (J17; Parallel, η 0.98 per mesh, the input 10 N·m): 2H Rear 10.000 (the coupling is lossless; the idle
In → Lay → Lo branch carries none); 4H the power splits at Rear, so nothing past In; N nothing past In; 4L Lay 19.600
(`10·30/15·0.98`), Lo 38.416 (`19.6·30/15·0.98`), then the split at Rear. E4: 2H Rear 10.000 (the planetary idles);
the rest by W7's planetary rule and the split.

**Phases** (§1.6's rule, mod 12°): InDog 0, RangeSlv 6°, LoDog 0, ModeSlv 0, FrontDog 6°.

**The mates W8 adds** (E4 and Parallel alike), with each configuration's state:

| Mate | Kind | 2H | 4H | N | 4L |
|---|---|---|---|---|---|
| RangeSlv on Rear Axis | axis | on | on | on | on |
| ModeSlv on Rear Axis | axis | on | on | on | on |
| ModeSlv splined to RangeSlv | spline | on | on | on | on |
| RangeSlv along Rear at H | slide | on | on | off | off |
| RangeSlv along Rear at N | slide | off | off | on | off |
| RangeSlv along Rear at L | slide | off | off | off | on |
| ModeSlv along Rear at 2WD | slide | on | off | on | off |
| ModeSlv along Rear at 4WD | slide | off | on | off | on |
| RangeSlv engages InDog | couple | on | on | off | off |
| RangeSlv engages LoDog | couple | off | off | off | on |
| ModeSlv engages FrontDog | couple | off | on | off | on |

RangeSlv is Rear's sliding anchor (Rear has no other gear). In: anchor Sun (E4) / InPin (Parallel), InDog locked to it.
FrontDrv: anchor FrontDog (first in sheet order), FDrive locked to it. Parallel Lo: anchor LoGear, LoDog locked. E4
Carrier: one body with LoDog (§0.2). Made in the order: in 2H the H and 2WD slides and RangeSlv engages InDog; in 4H
the 4WD slide and ModeSlv engages FrontDog; in N the N slide; in 4L the L slide and RangeSlv engages LoDog. W5's
ALONG globals: Sun 15 / InPin 5, LayGear 5, LoGear 25, FrontDog 107, FIdler 125, FOut 125.

---

## 3. Work packages, ownership and the interface commit

### 3.1 The order of work

```
P (probes ahead, §4) ───────────────────────────────────────────────┐
I (interface commit, after W7 closes) ──► A (SolidWorks) ─┐          ├──► E (demonstration on 2026, then 2024)
                                          B (planning)  ──┼──► D ────┘
                                          C (record, words)┘
```

P and I start together; code reads findings by `getattr` and refuses when one is missing. A, B and C run in parallel
after I. D after A–C. E after D, P and W7's close: the shakedown `s0` first, then the E4 full build `s1`; what it gets
wrong is probed step by step (the one follow-up round), fixed, and only the affected sections rerun; one full run at
the close; 2024's confirming build last. An independent Opus review after I, after each of A–D, and after E.

### 3.2 The interface commit (one agent): shapes A, B and C share

Written as stubs with docstrings that are the contract, as W5's was, with `W8-INTERFACES.md` beside it. A change to
any of these is a stop-and-ask.

**`swcom.py`** (A writes the bodies):

- `Session.configurations() -> List[str]` (`GetConfigurationNames`); `active_configuration() -> str`
  (`ConfigurationManager.ActiveConfiguration.Name`).
- `add_configuration(name) -> None` (`AddConfiguration2(name, "", "", 0, "", "", True)`; the active name read back;
  otherwise `SolidWorksError` *"SolidWorks would not make the configuration 4L."*).
- `show_configuration(name) -> None` (`ShowConfiguration2`; success judged by the active name read back, never the
  return: GOTCHAS §23). Does not rebuild.
- `delete_configuration(name) -> None` (`DeleteConfiguration2`; names read back; refuses the active one).
- `set_mate_suppressed_in(handle, suppressed: bool, configurations: Sequence[str]) -> None` (`SetSuppression2(0 or
  1, findings.SPECIFY_CONFIGURATIONS, names)` as a `VT_ARRAY | VT_BSTR`; read back with `IsSuppressed2`; raises with a
  sentence if any configuration disagrees). Does not rebuild.
- `mate_suppression(handle, configurations: Sequence[str]) -> Dict[str, bool]` (`IsSuppressed2(3, names)`, one flag
  per name, no configuration activated).
- `ConfigurationGone(ComponentGone)`: a recorded configuration is not in the assembly (Update → `NotAsBuilt`).
- Every member through `call` / `_guarded`, as W4's N3 requires.

**`swbuild.py`**:

```python
@dataclass(frozen=True)
class ModeStep:
    name: str                                   # the configuration's name: the mode's
    ops: Tuple[base.Op, ...]                    # the Mate (and LinkDimension) ops first made in this configuration
    on: Tuple[str, ...]                         # every mate name on in this configuration
    off: Tuple[str, ...]                        # every per-mode mate name off in it
    frames: Mapping[str, Tuple[Tuple[float, ...], Tuple[float, float, float]]]   # slider handle -> its frame here

@dataclass(frozen=True)
class ModesPlan:
    steps: Tuple[ModeStep, ...]                 # Modes-sheet order; steps[0] is the one the assembly opens in
    same_way: Tuple[str, ...] = ()              # the steps' gear mates that turn their gears the same way (couples)
    def check(self) -> List[str]: ...           # ids unique across plan and steps; each LinkDimension after its
                                                # mate; on ∪ off the same set in every step; on ∩ off empty; every
                                                # name made exactly once, in the first step it is on in

@dataclass
class ModeCheck:
    name: str
    mates: List[MateState]                      # as read in this configuration
    suppressed: Dict[str, bool]                 # every per-mode mate's state here, as read back
    clashes: list                               # this configuration's interference, as GearboxResult.clashes holds it
    interference_error: str = ""

GearboxResult += modes: List[ModeCheck]
MateRef += position: str = ""; modes: Tuple[str, ...] = ()
MeshLink += modes: Tuple[str, ...] = ()        # the configurations it holds in; () every one
LockLink += modes: Tuple[str, ...] = ()
MotionUpdate += configurations: Tuple[str, ...] = ()
             += mode_placements: Tuple[Tuple[str, Tuple[Placement, ...]], ...] = ()   # wanted, per configuration
             += recorded_by_mode: Tuple[Tuple[str, Tuple[Placement, ...]], ...] = ()  # on record, per configuration
             += slide_globals: Tuple[Tuple[str, str, GlobalVariable], ...] = ()       # (gear, position, wanted)
GearboxUpdate += configuration: str = ""       # the one Update worked in
              += visited: List[str]            # the others it post-checked
              += unsuppressed_in: List[Tuple[str, str]]; suppressed_in: List[Tuple[str, str]]   # (mate, configuration)
              += slid: List[Tuple[str, str]]   # (gear, position) whose slide global was set
              += extra_configurations: List[str]
              += modes: List[ModeCheck]        # the post-check per visited configuration
STAGE_MODE = "mode"                            # Step.name: the mode's name
build(..., modes: Optional[ModesPlan] = None)            # keyword; None is W5 byte for byte
build_gearbox(..., modes: Optional[ModesPlan] = None)    # keyword, passed to build for the assembly
```

The `SolidWorks` protocol gains the six swcom members. `update_gearbox`'s signature is unchanged: `motion` carries the
modes. `internal` keeps its meaning and is given the splines' and the couplings' names too (§1.7).

**`gears/`**: `gears/clutch.py` with `SleeveKind` and `DogKind` stubs; `WORKBOOK_KINDS` and `kind_for`'s lookup in
`gears/__init__.py`; `spec.default_stem`'s two words (§1.1).

**`workbook/motion.py`** (B): `SLIDE, SPLINE, COUPLE = "slide", "spline", "couple"` added to `MATE_KINDS`;
`MatePlan += position: str = "", modes: Tuple[str, ...] = ()`; `mate_name(kind, gears, shaft="", *, position="")`
written for the three kinds; `slide_global(gear, position)` → `"RangeSlv Face Z at H"`; `MotionPlan += modes:
Tuple[str, ...] = ()` (the configurations, in order) and `drag_by_mode: Mapping[str, Tuple[str, ...]]`; stub
`modes_plan(motion, handle_of, frames_by_mode) -> Optional[swbuild.ModesPlan]`.

**`workbook/checks.py`** (B), consumed by C and D:

```python
@dataclass
class ModeReport:
    name: str                                       # "" for the implicit mode of sliders with no Modes rows
    row: int
    positions: Dict[str, Tuple[str, float]]         # slider -> (position, offset mm)
    engaged: Tuple[Tuple[str, str], ...]            # (sleeve, dog), dogs in Gears-sheet order
    out_of_mesh: Tuple[Tuple[str, str], ...]        # listed meshes a slide takes out of mesh here
    off: Tuple[Tuple[str, str], ...]                # relations left off here as loop-closers (J15)
    placed: Dict[str, Placed]                       # every slider placed at its position here
    motion: kinematics.Motion
Report += modes: Tuple[ModeReport, ...] = ()
```

**`workbook/gearbox.py`** (B): `GearboxPlan += modes_plan: Optional[ModesPlan] = None`; `build_kwargs()` adds
`"modes"` only when it is set, so every W5 call is unchanged key for key.

**`store.py`** (C owns it after I): §1.11's fields, schema 4 and its parse shapes.

**`ui_text.py`** (C): stubs `modes_ready_line(plan)`, `modes_done_line(plan, result)`, `mode_problem(problem)`,
`modes_record_line(record)`, `mode_update_lines(update, result)`, `mode_speed_lines(spec, report, mode) ->
Tuple[List[str], str]`; existing functions keep their signatures and call these.

### 3.3 The packages

**P — probes ahead** (§4): `findings.py`, `probe/p9_modes.py`, `probe/decide.py`, `probe/__main__.py`'s registry,
`tests/test_findings.py`, `tests/test_probe_modes.py`, `probe/results/**`. Commits first the findings the macro
database has verified (§4.1, with its entries cited in the comments), then runs the probe on SolidWorks 2026 and
commits what it found. **Done:** the findings committed and pinned against the result file; reviewed.

**A — SolidWorks** (`swcom.py`, `swbuild.py`, `tests/test_swbuild.py`, `tests/test_swcom.py`; may add to
`tests/test_swbuild_train.py`, never change an assertion there): the six swcom members; `build`'s mode phase (§1.8,
order exactly); the per-mode mate check and its sentences; interference per mode; Update's per-configuration reads,
D10 per configuration, the per-mode post-check and the return to the active configuration (§1.10); gear mates of
kinds `couple` and `spline` read for sense and remade as `mesh` ones are (`_internal_meshes` and its callers today
know only `"mesh"`); the fake (§3.5). Log lines: `config  2H made` / `config  4L: 11 mates as planned` /
`mode    4L: every mate sound, every gear free to turn, no interference`. **Done:** §3.5's A list against the fake;
`tests/test_swcom.py` covers each new member with a mocked COM object, including `ShowConfiguration2` answering
False with the right name active.

**B — planning** (`workbook/{model,schema,geometry,kinematics,checks,build,assess,export,motion,gearbox,update,
layout}.py`, `gears/__init__.py`, new `gears/clutch.py`, `spec.py`'s `default_stem` only, `tests/workbook_fixtures.py`,
`tests/test_workbook_{model,schema,geometry,kinematics,checks,build,export,motion,gearbox,update,layout,
demo_fixtures,modes}.py`, new `tests/test_gears_clutch.py`): §1.1–§1.7, §1.10's classify and finish, §1.11's
`finish_build` fields, the two fixtures. `later_rows` stops naming sleeves, dogs, slides and modes and names §0.1's
refusals instead. **Done:** §3.5's B list.

**C — record and words** (`store.py`, `ui_text.py`, `tests/test_store.py`, `tests/test_ui_text.py`): §1.11, §1.12.
**Done:** every sentence of §1.12 filled from fields in a test and read as written; v3 → v4 read, v4 round trip
byte-deterministic, v5 refused and untouched, each new parse refusal.

**D — window, boards, docs** (`workbook_gui.py`, `preview.py`, `gui.py` if needed, `tests/test_workbook_{build,
window}.py`, `tests/test_preview.py`, `design/**`, `docs/**`, `README.md`): the mode chooser, the counts, the end view
at the chosen mode, the footer's new states; the two boards rendered and looked at; `UI-DESIGN.md` §9;
PLAN-WORKBOOK §4.5 *Readings chosen (W8)* (J1–J24) and §6's W8 row note; HANDOFF. **Done:** the window launched on
the Parallel fixture against the fake, the chooser switched through all four modes, each footer state read.

**E — the demonstration** (`probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, `probe/results/**`):
§5. **Done:** logs for 2026 and 2024 committed, 0 failed; the person's step handed to the user.

### 3.4 Who edits what

| Package | May edit |
|---|---|
| I | everything listed in §3.2, once, then hands over |
| P | `findings.py`, `probe/p9_modes.py`, `probe/decide.py`, `probe/__main__.py`, `tests/test_findings.py`, `tests/test_probe_modes.py`, `probe/results/**` |
| A | `swcom.py`, `swbuild.py`, `tests/test_swbuild.py`, `tests/test_swcom.py`, additions to `tests/test_swbuild_train.py` |
| B | `workbook/*.py` but `link.py` and `xlsx.py`, `gears/__init__.py`, `gears/clutch.py`, `spec.py` (`default_stem`), `tests/workbook_fixtures.py`, `tests/test_workbook_*.py` but `build` and `window`, `tests/test_gears_clutch.py` |
| C | `store.py`, `ui_text.py`, `tests/test_store.py`, `tests/test_ui_text.py` |
| D | `workbook_gui.py`, `preview.py`, `gui.py` if needed, `tests/test_workbook_{build,window}.py`, `tests/test_preview.py`, `design/**`, `docs/**`, `README.md` |
| E | `probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, `probe/results/**` |
| nobody | `gears/*.py` but `__init__.py` and `clutch.py`, `workbook/link.py`, `workbook/xlsx.py` |

### 3.5 What each package's tests must show; the fake

**The fake SolidWorks (A, `tests/test_swbuild.py`).** Per document: its configurations (the template's `Default` at
`new_assembly`), the active one, saved with the document and reopened in the one it was saved in. Per mate, a
suppression flag per configuration. `add_configuration` adds and activates; a mate made while a configuration is active
is on in **every** configuration (the plausible default the app must not rely on), with an override
`new_mate_elsewhere="suppressed"` that models assemblies/07's inverse. Positions and turns are shared across
configurations (GOTCHAS §83). A rebuild in a configuration moves each slider to its one SLIDE on there, and calls a
configuration with two SLIDEs on for one slider over-defined (status 5 at `add_mate`, code 46 on its mates, constrained
status 4); a coupling gear mate holds the relative turn it is made at, as the fake's gear mates do now. `show_configuration`
answers like `ShowConfiguration2` (False when already active). What it does not model, so only SolidWorks shows it: a
gear mate between collinear axes turning anything; whether `ShowConfiguration2` marks a document or raises a dialog;
whether the top-only rebuild after a show re-solves the positions; real interference of the splines.

**A (against the fake):** a build with modes makes every configuration, makes each per-mode mate in the first
configuration using it, sets and reads back every flag, runs the mate check per mode, deletes `Default`, saves in the
first mode, runs interference per mode, and ends in the first mode; the same with `new_mate_elsewhere="suppressed"`;
a mode whose step over-defines (a doctored plan) stops the build with *"In mode N, …"*, nothing saved; a build with no
`modes` is W5's call for call. Update: in a non-mode configuration refuses before anything changes; a missing
configuration → `NotAsBuilt`; D10 both ways in an inactive configuration, said, never a call on a mate already right;
a slide global set; a turned train in 2H then switched to 4L → out of step there → every gear put, locks suppressed
around the puts, the post-check visiting 2H, 4H and N and returning to 4L; a quiet Update activates no configuration and
changes nothing; an extra configuration listed and left.

**B (pure):** both fixtures check clean; §2.3's speeds, ratios, engagements, slider positions, SLIDE globals and
phases pinned per mode; the torque of J17 for Parallel; each check of §1.5 with a made-up workbook (a partial cover, a
teeth mismatch, one sleeve over two dogs, two sliders overlapping, a bridging stroke, a dog never engaged, a blank pick
with no 0, a sleeve on Meshes, a dog with Slides); the outline test of §1.6 in every mode; `motion_plan` and
`modes_plan` for both fixtures against §2.3's mate table and build order (`ModesPlan.check() == []`); a loop closed by
a coupling in one mode left off there (J15); every classify case of J14 with its sentence; `finish_build` and
`finish_update` round trips; every sleeve and dog plan equal to the spur or ring plan of the same values but its stem
and its 30° default; `kind_for` never returning a workbook kind for a strip spec (`gui.KIND_VALUES` unchanged).

**Suite:** `PYTHONPATH=src .venv/bin/python -m pytest -q` on a clean `git archive`, and the Tk tests under Windows
Python, as W5.

---

## 4. Calls probed ahead

PLAN-WORKBOOK's W8 row says "probes (per-configuration mate suppression)". Under the user's rule of 2026-11-14 only a
call new to the app that could hang, raise a dialog, or damage a file or a session is probed before the full build;
the rest is first met in the full build, which the mate checks and read-backs of §1.8 make loud.

### 4.1 Every new call, and whether it carries that risk

| Call | Already proven | Risk of a hang, dialog or damage | Probed ahead? |
|---|---|---|---|
| `IConfigurationManager.AddConfiguration2(name, "", "", 0, "", "", True)` | 2024 SP5, the macro database's assemblies/07 (it adds and activates) | none seen; a new document | no — first met in the build; read back |
| `IModelDoc2.ShowConfiguration2(name)`, `ConfigurationManager.ActiveConfiguration.Name` | 2026 SP1.1 on parts (API-LEDGER; GOTCHAS §23); 2024 SP5 on a slider-crank assembly, followed by `ForceRebuild3(False)` (assemblies/07) | **yes**: in a mated gear train it re-solves the configuration; a configuration whose mates fight, or a rebuild error, could bring up a "What's Wrong" or rebuild dialog; never run by the app, never on 2026 on an assembly, never with the top-only rebuild after it | **yes** |
| `IFeature.SetSuppression2(0 / 1, 3, names)` on a mate | 2024 SP5, assemblies/07 | none: activates nothing | no |
| `IFeature.IsSuppressed2(3, names)` | 2024 SP5, assemblies/07 | none: a read | no (read along in the probe, since a quiet Update needs to know it marks nothing) |
| `IModelDoc2.DeleteConfiguration2(name)` | 2026 SP1.1, on parts | none: a new document, never the active configuration | no (read along) |
| `IModelDocExtension.SaveAs3(path, 0, 1, …)` of an assembly with several configurations | W4/W5's save, one configuration | **yes**: a save can ask about configurations that need a rebuild or their display data | **yes** |
| `OpenDoc6` of that assembly, then `QuitDoc` | W4/W5, one configuration; W5 P0c: a same-version unsaved close asks nothing | **yes**, together with the save: which configuration it opens in, and whether a close of it asks | **yes** (with the save) |
| `IAssemblyDoc.AddMate5(MATE_GEAR, …)` between two collinear axes | gear mates between parallel axes, tier 8 onwards | none: AddMate5 answers with a status | no — the build reads its sense and drives it |
| `IAssemblyDoc.AddMate5` while a configuration other than the first is active | 2024 SP5, assemblies/07 (one configuration's position mates, each made with its configuration active) | none | no — read back per configuration |
| `ToolsCheckInterference` after `ShowConfiguration2` | W4's interference, one configuration | none beyond the show | no |

### 4.2 The probe (P): `probe/p9_modes.py`, tier 9, item `configuration_switch_and_save`

One scratch assembly on SolidWorks 2026 in a fresh session, with a dialog watcher thread (the demonstration's
`press_dont_save` pattern widened: every new top-level window of the SolidWorks process is logged with its title and
buttons; a Yes/No save box is answered No; any other modal stops the probe and is reported):

1. Through `swcom` as the app will call it: a layout part with two coaxial axes, a gear on one shaft as its anchor, a
   sleeve on the other with its axis mate, a 1 : 1 gear mate between them (collinear: the app's coupling, made and
   read back as the app will; its outcome is recorded for J8 but nothing waits on it here), and two configurations
   `A` and `B` added; in `A` the sleeve's slide mate at 10 mm, in `B` at 20 mm, each made in its own configuration
   and suppressed in the other by `SetSuppression2(…, 3, names)`, read back by `IsSuppressed2(3, names)`.
2. `ShowConfiguration2` A → B → A → B under the watcher, each followed by the top-only rebuild; the active name, the
   sleeve's frame (it must read 10 and 20 mm), every mate's error code; `GetSaveFlag` before and after each show.
3. A third configuration `C` in which **both** slide mates are on (deliberately over-defined), shown under the
   watcher: what SolidWorks answers, whether any window opens, and whether showing A afterwards solves cleanly.
   This is the case §1.8's order is built never to meet; the probe meets it so the app knows what a user's edit
   could bring.
4. C deleted (`DeleteConfiguration2`, names read back); `SaveAs3` silent under the watcher; `QuitDoc`; `OpenDoc6`
   with configuration `""`; the active configuration (the one saved), every flag by `IsSuppressed2(3, …)`, every
   document's `GetSaveFlag` straight after the open and after the reads; then a show and `QuitDoc` unsaved under the
   watcher.

Findings (P commits; the first five from the macro database before the run, marked so, the rest from the run):

```python
CONFIGURATION_ADD_ROUTE = "AddConfiguration2(name, '', '', 0, '', '', True)"    # assemblies/07, 2024; 2026: tier 9
CONFIGURATION_SHOW_ROUTE = "ShowConfiguration2, active name read back"          # GOTCHAS §23
CONFIGURATION_DELETE_ROUTE = "DeleteConfiguration2, names read back"            # API-LEDGER, 2026 parts
SPECIFY_CONFIGURATIONS = 3                                                      # swInConfigurationOpts_e, assemblies/07
MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE = "SetSuppression2(action, 3, names); IsSuppressed2(3, names)"
CONFIGURATION_SHOW_RAISES_DIALOG = False      # tier 9 item 2; True is a STOP
CONFIGURATION_SHOW_OVER_DEFINED = "…"         # item 3: what an over-defined configuration answers
CONFIGURATION_SHOW_MARKS = "…"                # "nothing" or "assembly"
SUPPRESSION_READ_MARKS = "nothing"            # IsSuppressed2(3, …); anything else changes §1.10's check phase
MULTI_CONFIGURATION_SAVE_ASKS = False         # item 4; True is a STOP
REOPENS_IN_SAVED_CONFIGURATION = True
NEW_MATE_IN_OTHER_CONFIGURATIONS = "…"        # "on" or "suppressed": recorded; the app sets every flag anyway
```

`modes_reason()` (B, in `motion.py`, beside `motion_reason`) is `""` only when the five routes and
`SPECIFY_CONFIGURATIONS` are set as above, `CONFIGURATION_SHOW_RAISES_DIALOG` and `MULTI_CONFIGURATION_SAVE_ASKS` are
False, `REOPENS_IN_SAVED_CONFIGURATION` is True, and `CONFIGURATION_SHOW_MARKS` and `SUPPRESSION_READ_MARKS` are set
(`CONFIGURATION_SHOW_OVER_DEFINED` and `NEW_MATE_IN_OTHER_CONFIGURATIONS` are recorded, not gated on); otherwise a gearbox with modes is refused at Build with the sentence naming the finding (never built static: a
static assembly cannot hold modes). 2024 meets these calls in the confirming build, under the scripts' dialog
watcher.

---

## 5. The demonstration (package E), full build first

Through the app's own code as W5's script is (`plan_gearbox` → `build_gearbox(session, **plan.build_kwargs())` →
`finish_build`; `classify` → `update_gearbox` → `finish_update`; every footer sentence logged), Excel driven by the
script's own Excel, logs under `probe/results/` (2024 under `sw2024/`), no user titles, a dialog watcher running
throughout. New sections in `probe/workbook_assembly_check.py`, `s0`–`s6`, and `--only modes` to run them.

**Build each fixture once (J24).** `s0` and `s1` build. Every later section starts from a copy of `s1`'s built
folder: every SolidWorks document of it closed (`QuitDoc`); the folder copied; the copy's link record and `.gear.json`
files rewritten to the copy's paths (the script's own helper over `store`'s load and save); the original folder
renamed aside; the copy's assembly opened (`OpenDoc6`), so SolidWorks finds its parts and layout beside it; every
reference read back (each component's `GetPathName` in the copy's folder); the assembly saved by the script, so its
references are the copy's; closed; the original folder renamed back. The section then reads the copy's state as a
reopened gearbox (every flag False after the open). This is the change HANDOFF asks for; it is reviewed like code.

**What every mode gets measured, in every build and after every Update** (§4.1 of W5-PLAN per configuration): the
active name read back; every mate's flag in every configuration by `IsSuppressed2(3, …)` against the record's
modes; in each configuration after a show and the train's rebuild: every gear's frame (each slider at its position to
1e-6 mm, every other gear at its built frame), every on mate code 0 and every per-mode mate off reading suppressed,
every mated gear `GetConstrainedStatus` 2, interference none; per mode a **half-pitch control** on each engaged
coupling (the dog put 6° about its own axis with the coupling on: must interfere with its sleeve only; put back: none)
and on each sliding mesh; a disengaged dog with no clash. Saved, closed, reopened: opens in the first mode, every
document unmodified straight after the open, the flags and frames the same.

**The driven proof per mode** (the script's, never the app's; W5's angle-mate drive on the input's anchor, a global
"Drive" 90 → 120): every member's turn against §2.3's 30° row to 1e-6 relative, sign included; members free in that
mode must not turn (more than 1e-6 is a NOTE, logged and listed, not a FAIL: an unconnected train is SolidWorks'
solver's to leave). **Wrong-sense control** in 4L on `RangeSlv engages LoDog`: suppressed in 4L, a temporary 1 : 1
gear mate with the other Flip in its place, driven: the script must see Rear turning against the carrier; then W5's
M12 hygiene (Drive back, the control deleted, the coupling back on in 4L only, every frame at the built frame, no
Drive or control left, no lock suppressed, every flag in every configuration as recorded).

**Sections.**

- **`s0` — TransferCase_Parallel** (the shakedown, W7-free): build; every measurement above in each mode; the driven
  proof per mode; reopen. Run first on 2026; it isolates W8's machinery from W7's.
- **`s1` — the E4 transfer case:** build (the one fresh E4 build); every measurement in each mode; the driven proof in
  each mode, with the wrong-sense control in 4L; reopen. This is PLAN-WORKBOOK's *"The E4 transfer case's four
  modes"*.
- **`s2` — turning and switching** (a copy of s1): in 2H the user's turn simulated (driven 37°, the drive deleted);
  shown 4H, N, 4L: each coupling's relation logged (in 4L `RangeSlv engages LoDog` out of step by 37° · 3/4 = 27.75°,
  i.e. 3.75° modulo the dog's 12°) and SolidWorks' interference in each logged as a fact; in 4L Update with nothing
  in the workbook changed: `restored` for the train, the coupling in step, every frame built, the post-check visiting
  2H, 4H and N, the assembly left in 4L, no interference in any mode; then a quiet Update: no configuration shown,
  every frame and flag the same, every document reading `GetSaveFlag` False before and after.
- **`s3` — D10 per configuration and the refusals** (a copy of s1): in 4L `RangeSlv engages LoDog` suppressed and
  `RangeSlv engages InDog` turned on → Update in 2H puts both right in 4L and says so, activating nothing in the check;
  an angle mate the record does not know, on in N only → Update refuses naming it and N; suppressed → listed and left;
  a configuration `Exploded` added by the script → listed and left; made active → Update refuses before changing
  anything; `4H` deleted → `NotAsBuilt` and Build again… offered.
- **`s4` — the edits Update carries, then a structural one** (a copy of s1): Excel `RangeSlv` Slides `L=+10` → `L=+10.5`
  (still covers LoDog: 66.5–74.5 over 67–73) → Update sets `RangeSlv Face Z at L` 66 → 66.5, frames in 4L, the drive in
  4L; `ModeSlv` At 100 → 101 with Slides `2WD=0, 4WD=+9` (4WD stays at 110; 2WD 97–105 still clear) → Update sets
  `ModeSlv Face Z at 2WD` 96 → 97 and finds `ModeSlv Face Z at 4WD` already 106, frames in 2H and 4H; then Modes 4H's ModeSlv `4WD` → `2WD` → the structural sentence, Build again… → `_r2` built with
  its configurations, measured; every earlier file's sha256 and mtime unchanged.
- **`s5` — the refused mate in one mode, forced** (a copy of s1's workbook, built fresh: the refusal is the point): the
  plan doctored by the script so that N also has `RangeSlv along Rear at H` on → the build stops with *"In mode N, …
  over-defines the assembly."*; the parts and layout part saved and on record, no assembly file, the document left
  open and named; the footer never offering the same build again; then closed as W5's m4 closes it.
- **`s6` — the person's step** (handed to the user, 2026 then 2024): *"In SolidWorks, open the TransferCase.SLDASM the
  demonstration built (its folder is in the log). It opens in 2H. Pick the configuration 4L in the ConfigurationManager.
  RangeSlv, the sleeve between the two dog rings, now sits over LoDog, and ModeSlv over FrontDog. Drag the sun, the small
  gear at the front on In, round by about a quarter turn: the rear sleeves and the front output gear turn the same way
  as the sun at a quarter of its angle, and the idler between the front gears the other way. Then pick N: drag the sun
  again; the rear and front stand still. Tell us what you saw. Then in the Workbook window press Update SolidWorks with
  nothing changed: the footer should say the gears were put back at the turn they were built at, if you turned them,
  and in which configuration it worked."*
- **window** (`workbook_window_check.py`, 2026): the Speeds panel with the chooser on 4L, on N, and the built footer.

**SolidWorks 2024, the confirming build** (the rule's "one full build plus every section where the versions have been
seen to differ"): `s0`, `s1` and `s3` (the per-configuration suppression calls are 2024's verified ones, the
collinear gear mate's sense is not), and the window check. Each started fresh, the user's documents untouched.

---

## 6. Definition of done

1. Probe tier 9 run on 2026, its findings committed and pinned, reviewed.
2. Packages I, A–D committed, each reviewed independently; the suite green on a clean `git archive`; the Tk tests
   green under Windows Python.
3. Both fixtures check clean with §2.3's numbers, recomputed by an independent subagent from §2's tables alone.
4. On SolidWorks 2026: `s0`–`s5` pass, 0 failed; one full run at the close from the final source. On 2024: `s0`,
   `s1`, `s3` and the window check pass. Logs committed.
5. The person's step handed to the user; the readings J1–J24 handed with it as readings they may overrule.
6. `PLAN-WORKBOOK.md` §4.5 *Readings chosen (W8)*, a dated note under §6's W8 row, `UI-DESIGN.md` §9, the two
   boards, HANDOFF's table and W8 section.

## 7. Risks, and what reading could not settle

- **Collinear gear mates (J8) are the riskiest point.** Nothing in tier 8 or the macro database made a gear mate
  between two collinear axes. Whether SolidWorks accepts one, turns it the way `gear_mate_sense`'s rule reads, holds its
  relative angle across a configuration change, and solves cleanly when one is turned on at an arbitrary relative
  angle is first seen in `s0`. If it fails, the follow-up probe tries, in order, an angle mate between Top planes at the
  phase angle (with the odd-teeth flip handled by reading the angle back) and a gear mate between the sleeve and a
  parallel offset reference; until then a gearbox with sleeves is refused at Build with the sentence naming the probe.
- **Per-configuration distance mates.** The macro database saw plane-distance mates added per configuration fail
  with error 5 and leave mates at 51 (assemblies/07), where they fought an existing limit mate. W8's SLIDE holds the
  one freedom nothing else holds, which is why it should solve; `s0` shows it. If it does not, the follow-up probe
  tries assemblies/07's route: the slider's origin coincident with an exact point in an assembly sketch per position.
- **A mate's default state in other configurations** (assemblies/07's inverse, seen once by hand) — the plan sets and
  reads back every flag, so it cannot leave a wrong state unseen.
- **`ShowConfiguration2` on a mated assembly** (dialogs, marks, whether the top-only rebuild after it re-solves
  positions): probed ahead (§4.2).
- **The splines' fit.** The dog's root fillet (0.38 m by default in the spur recipe) and the sleeve's tip corner sit
  within a few tenths of a millimetre of each other at 30 teeth, module 1.5, 30°; the interference check in each mode
  is the judge. If they touch, the fixture's dogs take a Fillet of 0.2 mm and the sentence for a partial fit is
  reviewed; the parts stay the strip's.
- **W7 dependencies** (§0.2): a gear on a carrier shaft, coaxial frame shafts in checks and the layout part, W7's
  loop of gear mates in every configuration, and W7's carrier skeleton under four configurations. None is W8's to
  change; each, if missing, is a stop.
- **The copy of a built folder** depends on SolidWorks finding the copy's parts beside its assembly once the original
  folder is moved aside. The search order for referenced documents is not in the macro database; the script reads
  every component's path back before it trusts the copy, and stops otherwise.
- **Free trains under a drive.** Whether SolidWorks' solver leaves a train not joined to the driven one exactly where
  it stood is not recorded anywhere; the demonstration logs it as a NOTE.
- **Time and memory.** E4 has 11 gear rows, three planet copies and four configurations: four shows and rebuilds, four
  mate checks and four interference checks per build, and as many per changed Update. Not measured; 2024's memory
  guard stays.
- **What reading could not settle.** Canvas E4 gives only the five new rows, the planetary by reference to E3, and the
  front drive in words: the planetary's face widths and axial place, and the whole front drive (FDrive, FIdler, FOut,
  their shafts and teeth), are this plan's choices, as are the Parallel fixture's numbers. Canvas E4's *"switches off
  the locks it doesn't engage"* names locks; this plan uses gear mates (J8). How W7 will name and mate the carrier,
  and whether it gives the planets' speeds absolute or relative to the carrier, is W7's; §2.3 gives both. Whether a
  quiet Update's `IsSuppressed2(3, …)` reads mark the assembly is unknown until tier 9 (if they do, the check phase
  reads only the active configuration with W5's `IsSuppressed2(1, …)` and D10 per configuration waits for a changed
  Update's post-check).
