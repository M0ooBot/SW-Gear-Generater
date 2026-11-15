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
   shaft along Z±, checked at every mode's positions (§1.2). **Sliding gears are designed and tested against the
   fake with made-up workbooks only:** neither fixture has a gear that slides into or out of mesh, so no sliding mesh
   is built on SolidWorks in W8's demonstration (review S5). They use the same mechanism the couplings do (a gear
   mate switched per configuration), which the demonstration does show.
3. Engagement worked out per mode: a sleeve over a dog couples their shafts; a sliding gear meshes its listed partner
   only where their faces overlap (§1.3).
4. Kinematics, ratios, checks and phases per mode (§1.4–§1.6), and the Results sheet per mode.
5. The turning assembly with one configuration per mode: one distance mate per slider with a value per configuration,
   couplings and splines as 1 : 1 gear mates, per-configuration suppression of the couplings (§1.7–§1.9).
6. Update SolidWorks across configurations: classification, D10 per configuration, post-check per mode (§1.10).
7. The record at the schema one past W7's (§1.11); the sentences, a mode chooser in the Speeds panel, boards (§1.12).
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
W7, once built, provides what `W7-PLAN.md` as committed (`8ebddb0`, reviewed in `W7-PLAN-REVIEW.md`) says it will:

- frame shafts sharing one axis (In, Carrier, Ring, Rear and FrontDrv all at the origin): several `"<Shaft> Axis"`
  on one line in the layout part (W7-PLAN §2.6: the carrier's `"C Axis"` beside `"S Axis"` and `"R Axis"`), and
  coaxial shafts exempt from `checks._check_shafts`' "passes over another shaft's axis" warning (W7-PLAN §2.3 item 5;
  today it warns for any two coaxial shafts whose gears' spans overlap);
- `kinematics.solve` through a carrier (today it returns `later` for any mounted shaft), on which W8's per-mode
  solve builds, and W7's planetary torque rule (W7-PLAN §2.5, its reading J10);
- a gear row on the carrier's own shaft (E4's LoDog): W7-PLAN §2.1 allows it ("it may carry gears of its own") and
  §2.7 locks it to the carrier component (`LoDog locked to Carrier carrier`, W7's reading J8). W8 changes nothing
  there;
- W7's motion plan over **bodies** (a frame shaft or one copy of a mounted shaft, still bodies merged into ground:
  W7-PLAN §2.7), whose mates are W5's four kinds with `MatePlan.on` naming the component an axis is in. W7's mates
  are always on: W8 never suppresses them per mode, and W8's per-mode union-find (J15) starts from W7's joins;
- the record at W7's schema, with `MateEntry.on` (W7) and `MateEntry.plane` (W6-PLAN §2.8), on which §1.11 builds.

**W8 stays independent of W7 where it can.** Package A and B are written and tested against a second fixture,
**TransferCase_Parallel** (§2.2), the same transfer case with its low range on a layshaft instead of a planetary: all
frame shafts along Z+, no carrier. It exercises every W8 mechanism, and the demonstration builds it first as the
shakedown (section `s0`, §5), so a fault in W8's machinery is never confused with one in W7's.

**Of W6** W8 assumes only that W5's AXIS and ALONG mates for ±Z shafts keep their meaning, with W6's `plane` field
reading `"front"` for them; a SLIDE carries `plane = "front"` likewise. Sliders on turned axes are refused (§0.1).

**Starting commit.** The interface commit starts on the commit that closes W7 (its demonstration and review), named
in `W8-INTERFACES.md`, as W5's ruling M3 did for W4. Every claim §0.1 makes about the code was read at `0f5a121`;
W6 and W7 change motion (bodies, the carrier as an anchor), the layout (coaxial axes), checks (the coaxial exemption)
and the record, so the interface commit reads §0.1 again against W7's close and writes in `W8-INTERFACES.md` what
moved (review S10).

### 0.3 Readings the work proceeds with (the user may overrule)

Each is argued where it is used; the column says where.

| # | Reading | Instead of | § |
|---|---|---|---|
| J1 | **A sleeve is an internal spline ring and a dog an external one**, each the strip's own proven ring or spur plan at the row's teeth, module and face; **no fork groove, hub, chamfers, back-cut or synchro cone**. | A skeleton-only sleeve and dog, as the user chose for W7's carrier; or canvas E4's sleeve *"with a groove round it for the shift fork"*. | 1.1 |
| J2 | A sleeve and a dog have **no pressure angle of their own**: a blank takes the Box's, as every row does (20°, the strip's own); a workbook may type another. Canvas E4's 30° stub-tooth spline is **not built**: the strip makes full-depth teeth only, and at 30° a full-depth 30-tooth dog's tip is 0.022 mm thick. | A 30° default (canvas E4). | 1.1 |
| J3 | A sleeve's teeth are always inside, a dog's outside; Side, Helix angle and Profile shift that say otherwise are errors. | Allowing helical splines or shifted splines. | 1.1 |
| J4 | **Engaged means full overlap**: a dog is engaged when the sleeve covers the dog's whole face; partial overlap is an error at that mode's cell; no overlap is disengaged. The same for a sliding gear and its listed partner (the narrower face covered). | Any overlap engaging. | 1.3 |
| J5 | A blank Modes cell is the slider's position whose offset is 0; a slider with none is an error at the cell. With sliders and no Modes rows, a slider with no position at 0 is an error at its Slides cell. | The slider at its At whatever its positions. | 1.2 |
| J6 | Mode names follow the gear-name rule (letters, digits, `_`, `-`) and are unique ignoring case: they become configuration names. | Any text. | 1.2 |
| J7 | **One distance mate per slider** (its SLIDE), its value set **per configuration** with `IDimension.SetSystemValue3(value_m, 3, [mode])` and read with `GetSystemValue3(3, modes)` without activating: no slide global, no second mate, nothing suppressed for a slide (the W8 spike's follow-up, SolidWorks 2026). Every mode's value is set explicitly at the build and read back. | One distance mate per position with its own global, switched per configuration (the plan before the spike: its second link by `IEquationMgr.Add2` returned −1 once there were several configurations). | 1.7 |
| J8 | **A coupling (a sleeve over a dog) and a spline (a slider turning with its shaft) are 1 : 1 gear mates between collinear axes**, read back and turned round as a ring's gear mate is. The W8 spike (SolidWorks 2026) made both, drove them and ran the both-Flips control: exactly one Flip right, the read-back naming it; caveats: each entity pointed along its own +Z (the per-entity sign was never −1), and the parts were the strip's spur and internal ring, not yet the sleeve and dog kinds. Canvas E4 says the configurations *"switch off the locks"*; a lock is not used. | A lock per engagement (it also holds the sleeve along the shaft and fights its slide mate: tier 8, a locked gear with an axis mate over-defines); an angle mate (0° degenerate, and with an odd tooth count a 180° flip lands tooth on tooth). | 1.7 |
| J9 | A shaft's anchor is its **first non-sliding gear**; with none, its first slider (a *sliding anchor*: axis mate and slide mates, no ALONG). Every other slider has an axis mate, slide mates and a spline to the anchor. | — | 1.7 |
| J10 | **One configuration per mode, named as the mode.** Every always-on mate and every SLIDE (at its first mode's value) is made while only the template's configuration exists; then every configuration is added (each starts as a copy of the active one's positions, so every mode starts at the built turn); a top-only rebuild before any flag is set; every slide value set per configuration and read back; each coupling or sliding mesh made while the first configuration using it is shown; every flag set explicitly in every configuration and read back (never the call's return); component handles fetched again after every configuration change (§1.8, the rule of §3.2); the template's configurations that are not modes deleted; the assembly saved in the first mode. Sliders but no Modes rows: no configuration is added. | Renaming the template's configuration (`IConfiguration.Name` put, unverified). | 1.8 |
| J11 | **Each configuration keeps its own positions** on SolidWorks 2026 (the spike's follow-up B): a turn the user gives in one mode stays in that mode, every other mode keeps its own last positions, a put holds only in the configuration shown, and a newly engaged coupling inherits no angle from another mode. The app is built to be right also if SolidWorks 2024 shares positions (GOTCHAS §83, recorded there): §1.9 says how, and where it cannot be. | Rotations shared between configurations (the plan before the spike, from GOTCHAS §83). | 1.9 |
| J12 | **D10 per configuration:** a recorded mate found suppressed in a configuration where the record has it on is turned back on there; one found on where the record has it off is suppressed again there; both said. An unsuppressed mate not on record in any mode's configuration refuses the Update (W5 M7). | Leaving per-configuration differences alone. | 1.10 |
| J13 | Update works in the **configuration active when it opens** the assembly, refuses before changing anything when that is not one of the gearbox's, and visits the other modes' configurations to post-check only after it changed something, returning to the one that was active. | Switching configurations on every press. | 1.10 |
| J14 | **Update carries** W5's edits and **any edit after which every mate the modes need is already on record**: a slide offset, a slider's At or face, a Modes pick changed, a position renamed — each by setting that configuration's slide value (even while another is active) and the per-configuration flags of couplings and sliding meshes, the calls the build and D10 per configuration make. **Structural** (Build again…): Modes rows added, removed or renamed (configurations), a slider column added or removed, a gear gaining or losing Slides or becoming or ceasing to be a sleeve or dog, any edit needing a coupling or sliding mesh that is not on record, a mode whose slide value would reach, cross or sit on the Front plane. Row order alone changes nothing in SolidWorks and is said. | Every Modes edit structural (the plan's first reading). | 1.10 |
| J15 | **Loops per mode:** always-on relations first, then the mode's sliding meshes, then its couplings, in sheet order; one that joins two bodies already joined in that mode is left off there (W5's D6), an inconsistent one is a jam. | — | 1.4 |
| J16 | **A departure from PLAN-WORKBOOK §3.4**, which asks for a warning on *"a gear on an `output` shaft that nothing drives in some mode"*: W8 warns only on an output that turns in **no** mode. A member free in a mode (neutral; "front not driven") is not a problem: the Speeds panel says it. A meshed shaft free in every mode stays W3's error. A jam in any mode is an error at that mode's row. | §3.4 as written, which would warn on both of E4's outputs on every read. | 1.5 |
| J17 | Torque per mode: a coupling is a lossless 1 : 1 link; a branch that reaches **no output** in that mode carries none (a fixed shaft is a reaction, not a load); **an output shaft that also drives onward is a split**: it is given the torque arriving at it, marked as shared, and nothing past it is given (W3's rule for a split, applied at the output). | Passing an output's whole torque onward, as W3's walk does today. | 1.4 |
| J18 | What W8 does not build is refused with a sentence naming no phase (§0.1). | — | 0.1 |
| J19 | The Results sheet holds one block per mode. | Results of the first mode only. | 1.12 |
| J20 | Interference is judged in every mode, against a half-pitch control on each coupling (demonstration). | First mode only. | 5 |
| J21 | The window gets a **mode chooser in the Speeds panel** (canvas E4: *"Results get a mode switch in the app"*); the end view is unchanged, since a slide runs along the view direction. | A chooser for the whole window. | 1.12 |
| J22 | Two sliders on one shaft that overlap in any mode are an error; a sleeve long enough to bridge two dogs on its way between positions is a warning (canvas E4's *"it passes through neutral"*). | — | 1.5 |
| J23 | Mate names: `RangeSlv along Rear` (one SLIDE per slider), `ModeSlv splined to RangeSlv`, `RangeSlv engages InDog`. No slide globals. | — | 1.7 |
| J24 | The demonstration builds each fixture once and starts later sections from a copy of the built folder, its references repointed by opening the copy's assembly once with the original folder moved aside and saving it, the scheme rehearsed first on the probe's scratch assembly (§4.2, §5). | Building the fixture again per section; `ReplaceReferencedDocument` (unverified) or Pack and Go. | 5 |
| J25 | **A quiet Update reads only what needs no configuration change**, since `ShowConfiguration2` marks the assembly modified (the spike): the active configuration's frames, error codes and constrained statuses; every mate's flag in every configuration (`IsSuppressed2(3, …)`); every slide's value in every configuration (`GetSystemValue3(3, …)`); every gear mate's sense, suppressed ones included (the spike read a suppressed coupling's sense cleanly, marking nothing). **Left unread:** every other mode's frames, error codes and constrained statuses — a train turned or put out of step in a mode not active is seen only when Update works in that mode or a changed Update visits it. No sentence claims more. | Showing every configuration on every press (which would leave the assembly modified after a press that changed nothing). | 1.10 |
| J26 | **Puts are made mode by mode.** A put holds only in the configuration shown (2026), so restoring a mode takes a put made with that configuration shown. In each mode that needs a put, the set put is the gears connected over **every** mode's relations (for both fixtures, the whole gearbox: review M5). A mode needs a put when a workbook change moves its gears (a shaft moved, a tooth count, an At — these touch every mode, so every mode is visited and put) or when its own `train_check` finds it off its axis or out of step. A mode whose own train is in step and that no change touches keeps the user's turn (W5's answer 2). Right also if 2024 shares positions (§1.9). | W5's single put in the active configuration; the review's M5 set without per-mode puts. | 1.10 |
| J27 | **A slide never reaches the Front plane:** every mode's value of one SLIDE is non-zero and on one side of the plane (|z_front| ≥ `layout.BASE_TOLERANCE`, one sign), else the gearbox is refused at Build, and an edit that would take one there is structural. A distance of 0 and a change of side were not tried on one mate with per-configuration values; W5's answer 3 (no datum plane) already makes an anchor's front face reaching the plane structural, and this is the same rule for a slide. | A coincident mate for a position at 0 (W5's ALONG rule), which a single SLIDE with per-configuration values cannot switch to. | 1.7 |

*(2026-11-15: J11 and J26 — W8's s2 measured, on SolidWorks 2026 34.0.0, that a turn of a mated train given in one
configuration shows in every configuration, while a free component's put stays per configuration. The sentences now
read `TURN_PER_CONFIGURATION_ON_<year>`, and a put on a quiet Update now leads to the visit of every mode:
W8-INTERFACES §9.18. The text above is as approved.)*

### 0.4 What needs the user

Nothing blocks W8. These readings are closest to a decision of the user's and go at the top of the list handed to
them, in this order:

1. **J1** — toothed rings with no fork groove, hub or chamfers: the user chose a skeleton carrier in W7 "because
   every solid geometry may look different", and canvas E4 draws a fork groove and names a hub.
2. **J2** — the 20° full-depth teeth in place of canvas E4's 30° spline: a stub-tooth spline would be new solid
   geometry, which J1 promises not to make.
3. **J16** — the departure from PLAN-WORKBOOK §3.4's warning.
4. **J14** — a Modes pick between existing positions is an Update (a slide value and flags); rows added, removed or
   renamed stay structural.
5. **J11** — what a turn means across modes, which may differ between SolidWorks 2026 and 2024 (§1.9).

### 0.5 STOP and ask (implementers)

- A SolidWorks call this plan does not tie to a finding or to the macro database's verified entries (§4), or a
  finding read differently from §4.
- Changing a shape `W8-INTERFACES.md` pins.
- On SolidWorks (package E): any modal dialog from a configuration call; a configuration whose suppression does not
  read back as planned; a slider not at its position to 1e-6 mm in its configuration; a coupling or spline gear mate
  that reads wrong both ways round (the build already stops on it — the stop is for the plan, J8 then needs a
  probe); a driven gear off its mode's kinematics by more than 1e-6 relative or turning the wrong way; a both-Flips
  control in which not exactly one Flip turns right (§5); interference at the built turn in any mode, or a half-pitch control not caught.
- A W7 assumption of §0.2 that does not hold.
- A component handle held across a configuration change (§3.2's rule): the fake fails a test on one; on SolidWorks a
  frame reading None or a fixed component reading unfixed is a STOP, not a retry.
- On SolidWorks 2024 (the confirming run): per-configuration slide values refused, or positions found shared between
  configurations where §1.9 assumes the 2026 behaviour (§5, section `s7`).

---

## 1. Design

### 1.1 The parts: sleeve and dog

**Geometry.** A dog is an external spline ring: the strip's spur plan (`SpurGear.plan`) at the row's teeth, module,
pressure angle and face, with its bore. A sleeve is an internal spline ring: the strip's internal spur plan
(`InternalSpurGear.plan`), its rim the Rim column or the ring's default (root plus six modules). Both plans are the
ones the strip builds and `probe/gear_pairs_check.py` has built on both versions; W8 writes no new solid geometry.
With equal teeth, module and pressure angle, a ring's tooth space is the external gear's tooth turned inside out
(`gears/internal.py`'s docstring), so the dog's teeth sit in the sleeve's spaces with the backlash and the radial
clearance both plans already leave: for 30 teeth and module 1.5 the dog's root is ⌀41.25 and the sleeve's tip ⌀42;
the dog's tip ⌀48 and the sleeve's root ⌀48.75 (the depths do not depend on the pressure angle). Each part carries
the strip's backlash (0.3 × module, 0.45 mm), so a sleeve over a dog has 0.45 mm of play per flank at the pitch
circle, 0.9 mm in all, about ±1.15° of turn.

**Pressure angle (J2).** A sleeve and a dog take the row's Pressure angle, blank meaning the Box's (20°, the strip's
own), exactly as every other row. At 20°, 30 teeth, module 1.5, the review ran the existing kinds (`SpurGear`,
`InternalSpurGear`): the dog's tooth tip is **0.626 mm** thick and the sleeve's **1.153 mm**; what is left under
Checks is the strip's usual warnings (the form diameter, and the ring's tips inside its base circle, since ⌀42 is
under the base circle ⌀42.29). Canvas E4's *"internal spline ring (30° pressure angle)"* is not built: a real 30°
involute spline (ANSI B92.1, ISO 4156) has stub teeth, addendum 0.5 × module, and the strip makes full-depth teeth
only (addendum 1 × module). Built full-depth at 30°, the dog's tip is 0.022 mm thick (0.449 mm even with 0.05 mm of
backlash typed), a sliver for SolidWorks' interference check and for the part. A workbook may still type 30° on a
sleeve and dog row; Checks then shows the strip's thin-tip warning on each. Stub teeth would be new solid geometry,
which J1 promises not to make, so the choice goes to the user beside J1 (§0.4).

**Why teeth and not a skeleton (J1).** The user's reason for a skeleton carrier was that its solid "depends on the
gearbox at hand". For a sleeve and a dog the workbook specifies exactly what the teeth are — teeth, module, face — as
it does for a gear, and canvas E4 checks that *"sleeve, hub and dog teeth match"*. The teeth are the specified thing,
and the interference check in each mode is what proves a mode engages what it says and nothing else (a skeleton
would leave that to the mates' word). What does depend on the gearbox at hand is left out: the fork groove (its width
and depth depend on the fork), the hub the sleeve rides on (canvas E4 names it: *"sleeve, hub and dog teeth match"*,
and its half section labels each sleeve *"splined to Rear"*), the way a dog ring joins its gear, tooth-end chamfers and
back-cut, synchro cones and blocker rings (canvas E4 already leaves out the last three). The same reasoning the user
gave for the carrier is applied to those, and not to the teeth. The review's point stands against this argument and
goes to the user with it: with J2, what is built is a full-depth 20° tooth, not the stub spline a real sleeve has, so
the teeth are less exactly "the specified thing" than they would be on a gear. The canvas's fork groove and hub are
the departures from E4, said to the user with this reading; the existing `Groove (mm)` column (a herringbone's centre groove) is where a
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
shift on either (J3). `Gear.spec_values` gives a sleeve `teeth_side="internal"`; its pressure angle is the row's or
the Box's, as for any row (J2). The delegated plans write the custom property for the kind they were made by
(`property_ops(self.kind…)` would say "spur"); `SleeveKind.plan` and `DogKind.plan` put their own kind word there.
So a sleeve or dog plan equals the internal spur or spur plan of the same values but for its stem and that one
property.

**Outside the workbook** (review S9). `kind_for` finds the two kinds for every caller, the strip included, while the
strip's kind control (`gui.KIND_VALUES`) never offers them. When the strip meets a sleeve's or dog's `.gear.json` (Open
.gear.json, or the live link to such a part), it refuses with a sentence: *"Sleeve_m1.5_N30.SLDPRT is a sleeve made from
a gearbox workbook; open that workbook to change it."* (`gui.py`, package D; its sentence in `ui_text`, C).

### 1.2 Slides and positions

A slider is any gear with Slides: a sleeve, or a spur, helical or herringbone gear that slides in and out of mesh.
A position is `name=offset`, the offset in mm along the shaft's Axis from the gear's At (`model.parse_slides`), so a
slider at position p has its face centre at `point + (At + offset) × axis` (`geometry._place` with `at + offset`).
A mode picks one position per slider; a blank pick is the slider's position whose offset is 0, and a slider with no
such position is an error at the cell: *"Modes!B4: RangeSlv has no position at 0, so a blank here does not say where
it sits; pick one of H and L."* (J5). With sliders and no Modes rows (PLAN §1), there is one implicit mode, every
slider at its 0 position, and no configuration is added; there is no Modes cell to name then, so a slider with no
position at 0 is an error at its Slides cell: *"Gears!S7: RangeSlv has no position at 0, and with no Modes rows each
slider sits at its position 0; add one, or add Modes rows."* A Modes sheet with rows but no slider column is an error
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
  same shaft engage nothing (a warning). Sleeves engage dogs only. The teeth-match check reads each row's pressure
  angle through `Gear.spec_values` (the row's, else the Box's), not `ga.pressure_angle or box` as `_check_mesh` does.
  A coupling never goes through `_check_mesh`: with equal teeth at centre distance 0 it would refuse it (a ring needs
  more teeth than its pinion), as would `internal.tip_clash` (*"A ring of 30 teeth cannot hold a pinion of 30"*);
  sleeves and dogs on Meshes are errors, so neither is ever called on one.
- **A sliding mesh** is a listed mesh with a slider among its two gears; it is in mesh in a mode when the narrower
  face is covered, out of mesh with no overlap, an error between (J4). A listed mesh in mesh in no mode is a warning.

`checks` gains, per mode, a `ModeReport` (shape pinned in §3.2): each slider's position and offset, the engaged
couplings, the meshes out of mesh, that mode's `Placed` for each slider, and that mode's `kinematics.Motion`.

### 1.4 Kinematics per mode

`kinematics.solve` gains a mode: the meshes out of mesh in that mode are left out and each engaged coupling adds a
row `ω̃_p − ω̃_q = 0` (projected speeds, as every row is, so a Z− shaft keeps its sense). The rank tells the rest
exactly, as now: settled, free (a member nothing drives in this mode), or jammed. Speeds are about each shaft's own
axis.

**Torque per mode (J17)** follows W3's `_torques` with three additions. A coupling is a lossless 1 : 1 link. A branch
that reaches no output in that mode is pruned before the walk: it idles and carries no torque (a fixed shaft on it is
a reaction, not a load, so E4's planetary in 2H — Sun, planets, the held Ring, a carrier that drives nothing — is
pruned). **An output shaft that also drives onward is a split:** W3's walk today passes an output's whole torque on
when it has one onward link, as if the output took none; W8 stops there. Such a shaft is given the torque that
arrives at it and nothing past it is given, since how it shares that torque with what it drives depends on the loads,
which the workbook does not say. The Results sheet and the Speeds panel show that number marked as shared: *"Rear
10.000 N·m, shared with FrontDrv (the share depends on the loads)"*, and FrontDrv, Idler and Front show none, with
*"past a split"* in the note. No new theory is needed: it is W3's split, applied at the output. Planetary torques
are W7's rule (W7-PLAN §2.5), joined to this walk as W7 joins them to W3's.

Loops per mode
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
  required to have no overlap at all; the exemption comes **before** `_check_clearances`' ring branch, which would
  otherwise warn that a coaxial dog of equal teeth *"sits where it would mesh inside"* its sleeve, since its `near`
  test reads |0 − 0| < 0.1 m); a sleeve or dog on Meshes; a dog with Slides; a blank pick with no 0 position;
  the refusals of §0.1 become errors only at Build, as warnings in Checks.
- *Warnings:* a dog no mode engages; a listed sliding mesh in mesh in no mode; a sleeve longer than the gap between
  two dogs within its travel (*"RangeSlv is 16 mm long and InDog and LoDog are 14 mm apart: on its way from H to L it
  would hold both at once."*, J22); an output that turns in no mode (W3's warning, now across modes — **a departure
  from PLAN-WORKBOOK §3.4**, which asks for the warning on an output nothing drives in *some* mode and would so warn
  on both of E4's outputs on every read; announced as reading J16 and put to the user, §0.4); two modes that engage
  the same couplings and meshes (*"4H and 4X engage the same: they are one mode twice"*).
- *Not a problem* (J16): a member free in a mode. `checks._check_motion` today makes a meshed shaft no input settles an
  **error** (*"nothing settles FrontDrv's speed…"*); FrontDrv meshes FIdler and is free in 2H and N, so in a box with
  modes that check runs across the modes: a meshed shaft free in **every** mode keeps W3's error, one free in some
  modes is said by the Speeds panel only: *"N: neutral — Rear, FrontDrv, Idler and Front turn freely."* and *"2H: … the
  front is not driven."*
- *The top-level motion.* In a box with modes, `Report.motion` is the first mode's, so every reader that does not know
  modes yet sees a true state; the Speeds panel and Export read `Report.modes` (§1.12).
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
  none, the first slider is a *sliding anchor*: AXIS and its SLIDE, no ALONG.
- **Every other non-sliding gear** is locked to the anchor (W5).
- **Every other slider** gets AXIS (`RangeSlv on Rear Axis`, W5's axis-coincident route, `Unfix` straight before it as
  W5 does), its SLIDE, and a SPLINE to the anchor. A slider is never locked: a lock holds it along the shaft too.
- **A SLIDE** is **one distance mate per slider** (J7), W5's ALONG route: `"point distance"` from the slider's origin
  to the layout's Front plane, made at its first mode's `z_front`, its Flip from that sign (`AXIAL_MATE_ROUTE`), linked
  to **no global**. Its `D1` takes a value per configuration: `IDimension.SetSystemValue3(|z_front| / 1000, 3,
  [mode])` (`swSetValue_InSpecificConfigurations` 3; returns `swSetValue_Successful` 0), read back with
  `GetSystemValue3(3, modes)` without activating (the W8 spike's follow-up A, SolidWorks 2026: the value read back as
  typed in each configuration, a set made while another configuration was active moved only its own, and it survived
  a save and reopen). Named `RangeSlv along Rear`; on in every configuration; nothing about a slide is suppressed.
  Two cautions from the same run, written into the code's contract: before a configuration has a value of its own,
  `GetSystemValue3` reads **0** for every configuration that is not active, so the build sets every mode's value
  explicitly, the first mode's included, and reads them all back; and `IDimension.SystemValue` read 30 in X while
  the sleeve stood at 10, so it is never read — only the per-configuration get. **No mode's value is 0 or of the other
  sign** (J27): a distance of 0, and a change of side on one mate with per-configuration values, were not tried, and
  W5's coincident mate for a face on the plane cannot be one configuration's choice of one mate; so a slider whose
  positions would put its front face on or across the Front plane in some mode is refused at Build, with W5's
  answer 3's reason (*"RangeSlv's position L puts its front face on the Front plane, from which a slide is measured,
  so it is not built: move the slide off the plane."*).
- **A SPLINE** is a gear mate at 1 : 1 between the slider's `Gear Axis` and its anchor's — two collinear axes —
  turning them the same way. Named `ModeSlv splined to RangeSlv`. On in every configuration.
- **A COUPLE** is a gear mate at 1 : 1 between the sleeve's `Gear Axis` and the dog's, the same way round. Named
  `RangeSlv engages InDog`. On only in the configurations whose mode engages that pair (and does not leave it off as
  a loop-closer, J15).
- **A sliding mesh's** gear mate is W5's MESH, on only in the configurations whose mode has it in mesh.

**Why gear mates for couplings and splines (J8).** A spline and a coupling hold one thing: the turn of one body to
another's, and nothing along the shaft, since the slide holds that. A lock holds all six freedoms, so a lock between
a sleeve and its dog fights the sleeve's slide mate (tier 8: a locked gear also mated to its axis over-defines), and a
lock re-takes the offset it finds when it is turned on (`LOCK_RETAKES_AN_OFFSET`, and the macro database's
assemblies/11). An angle mate between Top planes holds a turn but is degenerate at 0°, and its 180° flip puts an
odd-toothed sleeve tooth on tooth. A gear mate holds only the turn, and everything around it is W5's: made under
`CommandInProgress`, renamed at once, its sense read back by `swcom.gear_mate_sense` and made again with the other
Flip if wrong, its remake route, its mate check. `gear_mate_sense` accepts two collinear axes (it refuses only axes
whose cosine is below 0.99, and computes `parallel` from the sign); "the same way" is the condition W5 reads for a
ring, so couplings and splines are passed as same-sense gear mates (in `build`'s `internal`,
`GearboxPlan.ring_meshes` widened to "the gear mates whose two gears turn the same way").

**Measured by the W8 spike** (`W8-SPIKE.md`, SolidWorks 2026, `probe/results/w8-spike-20261114-204436.*`): the spline
between collinear axes was accepted (`AddMate5` 1), nothing moved when it was made, the sleeve stayed free to slide
(constrained status 2); driven, the sleeve turned +30° with the anchor and the dog not at all; the both-Flips control
showed exactly one Flip right (False here: `Reverse` True, both entities along +Z) and the read-back named it, by W5's
rule and by W6's H alike; the slide moved the sleeve 10.0 mm with the spline on, its relative turn unchanged and the
drive still 1 : 1; the coupling, made the same way, turned the dog with them; the sense of a suppressed coupling
read cleanly in a configuration it is off in, marking nothing. **Caveats carried:** each entity pointed along its own
+Z, so the per-entity sign τ was never −1 (a sleeve or dog on a Z− shaft is not shown); and the parts were the
strip's spur and internal ring, not the `sleeve` and `dog` kinds, which delegate to those plans (§1.1) but are
first built in the shakedown `s0`.

**Ratios for the record:** COUPLE and SPLINE `ratio` is `(1, 1)`; `mesh_links` gives a COUPLE `k = σ_S·σ_D` (both
turn the same way about the world, so about each own axis by the product of senses) and pitch `360/z_D`; a SPLINE
is a `LockLink` (tested exactly: no hub phase, the slider turns with the anchor). Both carry the modes they are on in
(§3.2), so `swbuild.train_check` judges in a configuration only the links on in it.

**Names** (J23): gear, shaft and position names are letters, digits, `_` and `-` (schema; `model._SLIDE`), so these
names cannot collide with each other or with W5's.

### 1.8 Configurations: the build order

`BuildPlan.check` requires exactly one rebuild and the save last (`gears/base.py`), and W5's assembly plan is one such
plan. W8 keeps it so: the assembly `BuildPlan` is W5's train plus the sliders' AXIS mates, their SLIDEs (each at its
first mode's value) and the SPLINEs, every slider placed at its first mode's position. The configurations are a
second, pure structure handed to the worker beside it: a `ModesPlan` of one `ModeStep` per mode (§3.2).
`build_gearbox(..., modes=ModesPlan)` runs, inside the same job and document, after W5's run, rebuild, verify and mate
check, and **before the save**:

1. `configurations()` read: the template's own configurations (normally `Default`). Every component's `Name2` is
   already held from its insertion (`BuildResult.components`); from here on no component or mate handle survives a
   configuration change (the handle rule below).
2. A configuration per mode, in Modes-sheet order: `add_configuration(name)` (`AddConfiguration2(name, "", "", 0,
   "", "", True)`: it adds and activates, and returns an `IConfiguration`; the spike, 2026, with no window), the active
   name read back. A mode whose name equals one of the template's configurations (ignoring case) uses it instead.
   Each new configuration starts as a copy of the active one's positions and fixed states (the spike: the free
   components read the same turns in X and Y as before the adds, and the layout read `IsFixed` True in both through
   fresh handles), so every mode starts at the built turn with its sliders at the first mode's place.
3. **A top-only rebuild** before any flag is set: straight after `AddConfiguration2`, the spike's first two
   `SetSuppression2` calls misbehaved in all four runs (one raised 0x80010105 and took effect, the other returned
   False and did nothing); after a rebuild every call behaved.
4. **Every slide value, per configuration:** for each SLIDE and each mode, `set_dimension_in(slide, |z_front|,
   [mode])` (`SetSystemValue3`, no configuration activated), then `dimension_values(slide, modes)` read back against
   the plan for every mode. The first mode's value is set too, although the mate was made at it (J7's caution).
5. For each mode in order: `show_configuration(name)` (the active name read back, never the return, GOTCHAS §23;
   False when already active, as the spike saw after a reopen) and the train's rebuild, which the spike found enough
   to stand each slider at its configuration's value; then this mode's couplings and sliding meshes not made yet (the
   step's ops), each made under `CommandInProgress`, renamed at once, and its sense read back and turned round if
   wrong (W5's `_settle_sense`). Every gear stands at the built turn in this configuration (step 2), so each coupling
   is made in phase (§1.6). Then, for each mate just made, `set_mate_suppressed_in(name, True, <every configuration
   whose mode does not use it, and the template's>)` and `set_mate_suppressed_in(name, False, <every configuration
   whose mode uses it>)` (`SetSuppression2(0 or 1, 3, names)`), **every flag read back** with `mate_suppression(name,
   <every configuration>)` (`IsSuppressed2(3, names)`) and the call's return never trusted. A mate made while one
   configuration is shown came out, in the spike, **suppressed in the template's configuration and on in every
   other** — neither "on everywhere" nor "only here" — which is why every flag is set explicitly. Configuration k is
   shown holding only the always-on mates and the couplings made so far that are on in k, so none is ever shown
   over-defined.
6. **The mate check per mode:** for each mode, show it, rebuild, fetch every handle again, and check as W5's
   `_check_mates` does with this mode's lists: every mate on in it present, unsuppressed, error code 0 (any number
   logged, never interpreted); every per-mode mate off in it reads suppressed (and is not judged by its code: GOTCHAS
   §103); every mated gear `COMPONENT_UNDER_DEFINED`; every slider's frame at its value (`_verify`'s tolerance); the
   layout part and every gear meant to stay fixed reading `IsFixed` True **through a handle fetched after the show**
   (a held one reads False even for the fixed layout: the spike). A fixed component that reads unfixed through a fresh
   handle is a problem sentence, not a cue to fix it (the spike found the state carried; the 2024 run checks it). A
   problem is a sentence in `BuildResult.mate_problems` beginning *"In mode 4L, …"*, so W5's rule holds unchanged: a
   refused mate stops the build, nothing is saved, the document is left open and named, and Build waits for a changed
   workbook.
7. Show the first mode; `delete_configuration` for each of the template's configurations that is not a mode
   (`DeleteConfiguration2`, names read back; the spike: True with another configuration active, no window, the other
   flags unchanged, held handles still good); rebuild; save (`SaveAs3` silent: no window in the spike; it reopens in
   the configuration active at the save, every document unmodified).
8. Interference, after the save as W4 does it, **once per mode**: show it, the train's rebuild, fresh handles,
   `interferences()`; finally show the first mode again and rebuild. A clash in a mode is a CHECK naming the mode and
   the gears. Showing a configuration marks the assembly modified and no part (the spike, on the reopened file), as
   W4's interference check already does, so W4's invariant after a fresh build stands: no part marked, the assembly
   marked.

`CommandInProgress` is off around every show and rebuild, as W5 has it around its rebuilds, and on only while mates
are made (W5's `MATES_UNDER_COMMAND_IN_PROGRESS`), which is how the spike called them.

**The handle rule** (a rule of package A's whole session layer, pinned in §3.2). After every `AddConfiguration2` and
every `ShowConfiguration2` — and after anything else that changes the active configuration, opening the assembly
included — every `IComponent2` held from before answers `Transform2` with None and `IsFixed` with False, a wrong answer
and no error (the spike, every run; it held across `DeleteConfiguration2` of a configuration not active). So
`swcom.Session` never keeps a component or mate handle across such a call: it keeps the names (`Name2` as recorded at
insertion or found again, a mate's tree name) and fetches the handle again by name (`GetComponentByName`, the mate
group walk) the first time it is used after the change. Selections after a change go by those held names —
`SelectByID2("<feature>@<component>@<assembly>")` — never by a fresh handle's `Name2` or `GetModelDoc2`, each of which
answered wrongly once in the spike's earlier runs. The fake makes a stale handle fail a test loudly (§3.5).

**What a configuration holds.** Suppression, every slide's value, and — on SolidWorks 2026 — every component's place
(§1.9). Every mode has every slide at its own value and its couplings set. With sliders and no Modes rows, steps 1–8
are skipped: each slider's SLIDE is made at its one value and the assembly keeps the template's configuration.

### 1.9 Turning, and a change of configuration

*(2026-11-15: on SolidWorks 2026 34.0.0 a turn of a mated train shows in every configuration (W8's s2), which is
this section's "if SolidWorks shares positions" case for a turn, while a free component's Transform2 put stays per
configuration (the follow-up, rerun on that host). What the app says follows `TURN_PER_CONFIGURATION_ON_<year>`:
W8-INTERFACES §9.18. The text below is as approved.)*

A train turns in a configuration exactly as W5's does: one freedom per train in that mode (a free member in neutral
is a train of its own, as an unmeshed shaft is in W5), the drag gear the input's anchor.

**On SolidWorks 2026 each configuration keeps its own positions** (the spike's follow-up B, `w8-followup-20261114-
205913.*`): a free component with no gear mate, turned 20° in Y, stood at 0° when X was shown and at 20° again when Y
was; turned 10° in X, it left Y's 20° alone; all of it through a save and reopen. A put on a fresh handle holds in the
active configuration only. The spike's dog, put 5° in Y while its coupling was off there, stood at X's angle when X
was shown: the same thing, not the coupling restoring a relation. So:

- **The user's turn belongs to the mode it was made in.** Every other mode keeps the positions it last had, and
  switching back finds each mode as it was left.
- **A newly engaged coupling inherits no angle from another mode.** The phase at which a sleeve's teeth enter a dog's
  is whatever that configuration's own positions give. The build sets it per configuration: every configuration
  starts as a copy of the built turn (§1.8 step 2) and each coupling is made in its own configuration at that turn
  (step 5), so every mode shows its dogs in its sleeves. Switching alone never puts a dog tooth on tooth.
- **Out of step** (J11, J26) arises only where a mode's own positions have gone out of step — a turn made in that mode
  with a coupling or spline off, a put by hand, an Update that changed the teeth — and Update repairs it in that mode,
  with that configuration shown.
- **Puts are per mode.** Restoring the built turn in every mode takes a put in each, made with its configuration shown
  (J26).

**If SolidWorks 2024 shares positions between configurations** (GOTCHAS §83 and assemblies/07, recorded on 2024 for a
free mechanism, say "component positions are not stored per configuration"), the two versions differ here, and the
2024 confirming run measures it (§5, `s7`). The design is right either way where it can be:

- *The build:* right either way. Every configuration starts at the built turn; with shared positions they share it;
  each slider's place comes from its slide's per-configuration value, which a show and rebuild apply in either case;
  couplings are made at the built turn.
- *Update's per-mode puts:* right either way. Each put sets a gear's frame to its built frame in the mode shown. With
  shared rotations a later put in another mode sets the same built turn; a slider's put along its axis in mode B, if
  positions are shared, is undone in mode A by A's slide value at A's next show and rebuild. Every put is to the built
  frame, so the order of the modes cannot leave two of them disagreeing. With per-configuration positions the extra
  puts restore only what that mode needs.
- *A quiet Update:* reads the same things either way (J25); with shared positions a turn made in another mode is seen
  in the active one, and its `train_check` judges it as any turn.
- **Where it cannot be right for both:** what the app *says* about a turn and a switch. On 2026 "a turn stays in its
  mode" and "switching never shows a dog tooth on tooth" are true; with shared positions both are false — a turn in one
  mode is a turn in all, and switching can engage a coupling at whatever angle the turn left (the plan's first
  reading). The sentences that make either claim (the person's step, the footer after a switch, §1.12's *"turned in
  another mode"*) are chosen by a per-version finding, `POSITIONS_PER_CONFIGURATION_ON_2026 = True` (from the
  follow-up) and `…_ON_2024` (from `s7`), read by the running version's revision number, as W5 reads its per-version
  Flip tables; while `…_ON_2024` is unsettled, the 2024 sentences make neither claim. If 2024 also refuses
  per-configuration slide values, modes are refused on 2024 with `modes_reason()`'s sentence: no design of this plan
  holds a slide per mode without them.

### 1.10 Update SolidWorks with modes

**Classify** (`update.classify`, B; J14). A record with `modes` adds, to W5's rules, one test that decides most cases:
**are all the mates the new read's modes need already on record?** — one SLIDE per slider (always, now), and each
coupling and sliding mesh each mode engages, with the same gears. A slide's place in a mode is a value, not a mate, so
it never needs a new mate.

- *Update:* W5's edits (part values, layout moves, a follower's At, a meshed tooth change by the remake), including a
  sleeve's or dog's teeth, module or face when the pair still matches; **a slider's place in any mode** — an offset, a
  slider's At or face, a Modes pick changed, a position renamed or a new position picked — set as that configuration's
  slide value (`set_dimension_in`, which the follow-up showed works while another configuration is active, moving only
  its own); and **the flags** of couplings and sliding meshes whose on-sets change while every one needed is on record.
  `finish_update` writes the new values and on-sets. A coupling on record switched on in a new mode stands in phase
  there only if that mode's own positions are at the built turn: the put rule below sees to it (a newly engaged
  coupling is judged by `train_check` in its mode and put if out of step). Sentence pieces: *"moved {RangeSlv} in {4L}
  to {66.5} mm along {Rear}"*, *"switched the mates of {4H} to {ModeSlv at 2WD}"*.
- *Structural* (each with its sentence): Modes rows added, removed or renamed, a slider column added or removed
  (*"The Modes sheet has a new mode, 4X, and each mode's configuration is made when the assembly is built, so it needs
  a new revision."*); a gear gaining or losing Slides, or becoming or ceasing to be a sleeve or dog; any edit after
  which some mode needs a coupling or sliding mesh that is not on record (*"In 2H ModeSlv would now cover LoDog, which
  no mode engaged when the assembly was built, so it needs a new revision."*); a mode whose slide value would reach,
  cross or sit on the Front plane (J27, naming the edit).
- *No change in SolidWorks:* the Modes rows reordered. The assembly opens in the configuration it was saved in; the
  footer says the next Build again… would open in the new first mode. A position renamed whose offsets every mode
  keeps changes nothing either.

Why this is sound: a slide value per configuration and a flag per configuration are the build's own calls, both
measured (the spike and its follow-up); making a mate or a configuration in a reopened assembly would be new and stays
a Build again…. The user's W5 answers chose an Update wherever the route was proven; this follows them.

`MotionUpdate` gains the configurations on record, the wanted and recorded placements per mode, each SLIDE's wanted
value per mode, and each recorded mate's modes; `MeshLink` and `LockLink` gain the modes they hold in (§3.2).

**The worker's order** (A), W5's motion path with these changes. Every component and mate handle is fetched again by
name after every configuration change, the open included (§1.8's handle rule).

*Check — writes nothing, shows nothing.* Open the assembly (`UPDATE_OPEN_ROUTE`; it opens in the configuration last
saved active, the spike); `active_configuration()`; a recorded mode missing from `configurations()` → `NotAsBuilt`
(*"The configuration 4H is not in TransferCase.SLDASM any more: it was renamed or deleted in SolidWorks."*), so the
window offers Build again…; a configuration the record does not know is left alone and listed; the active configuration
not one of the gearbox's modes → `BuildError` before anything changes (*"Update SolidWorks works in one of the
gearbox's own configurations (2H, 4H, N and 4L), and Exploded is active in SolidWorks: pick one of them and press
Update SolidWorks again."*, J13). Then, **without showing any configuration** (J25), since a show marks the assembly
modified (the spike):

- in the active configuration, W5's reads: components, every frame, every recorded mate found (`MateGone` →
  `NotAsBuilt`), `mate_states()` (error codes), constrained statuses, and `train_check` with that mode's links and
  wanted frames;
- in every mode's configuration: every recorded mate's flag (`mate_suppression(name, modes)`, `IsSuppressed2(3, …)`,
  which marked nothing in the spike), compared with the record (on where its modes say on, off elsewhere, always-on
  mates on everywhere); an unsuppressed mate not on record refuses (M7, read the same way);
- in every mode's configuration: every SLIDE's value (`dimension_values(slide, modes)`, `GetSystemValue3`, which marked
  nothing), compared with the record; a value reading 0 is a configuration that lost its own value (J7's caution) and
  is set again with the rest;
- every gear mate's sense, the suppressed couplings included: the spike read a suppressed coupling's `Reverse` and
  entities cleanly in a configuration it is off in, marking nothing. W5's ruling that the check phase reads every gear
  mate's sense therefore stands in full (the narrowing the review's S8 asked about is not needed).

**What a quiet Update leaves unread** (J25): every mode but the active one's frames, error codes and constrained
statuses. On 2026 each configuration keeps its own positions, so a train turned, or put out of step, in a mode that is
not active is seen only when Update works in that mode or a changed Update visits it. Every sentence says so when it
matters: *"It worked in {4H}, the configuration that was active; it did not show the other modes, since nothing
needed changing."*

*Change — nothing raises out (W4's B1).* As W5: part and layout values; rebuild; then **D10 per configuration (J12)**,
for couplings and sliding meshes only (a slide is never suppressed): each recorded mate found off where the record has
it on is turned on there, each found on where the record has it off is suppressed there, both with
`set_mate_suppressed_in` and every flag read back (never a call on a mate already in the wanted state: W5's ruling,
`UNSUPPRESS_ON_LOCK_ALREADY_ON_MARKS_MODIFIED`), and the flags a J14 edit changes, the same way. **D10 for values:**
each SLIDE value found other than the record's in a configuration is set back to it there, and each value a J14 edit
changes is set, every one read back; said (*"set {RangeSlv}'s place in {4L} back to {66} mm, where it had been
changed in SolidWorks"*). Then the Face Z globals (W5). Then the puts.

**What is put, and where (J26).** Puts are per mode, each with that configuration shown and its handles fetched again:
on 2026 a put holds only in the configuration shown. A mode needs a put when a workbook change moves its gears' wanted
frames (a shaft moved, a tooth count, an At, a Face Z: these touch every mode, so every mode is visited) or when, once
shown, its own `train_check` finds a gear off its axis or a relation out of step. In such a mode the set put is the
gears connected over **every** mode's relations — W5's meshes and locks, W7's, the splines, every coupling and sliding
mesh of any mode — with every lock of it suppressed in this configuration around the puts (W5's M1, M8; review M5).
For both fixtures that is the whole gearbox. A mode no change touches and whose own train is in step is not put and
keeps the user's turn (W5's answer 2). The active mode is done last, so Update ends where the user left it. Why
"every mode's relations" when puts are per mode: it makes the same set right if positions turn out to be shared (2024,
§1.9), at the cost of putting back, in a mode that needs a put, a train the user turned there that no change touched —
which W5's answer 2 already chose ("whenever it has to move any gear").

*Post-check.* In every mode visited (all of them when anything changed; none in a quiet Update): shown, rebuilt,
handles fetched again, its frames (sliders at their values; every gear of a set that was put at its wanted frame; a
mode not put judged by its own `train_check`, never by built frames), its mates as §1.8 step 6 judges them, the senses
of the gear mates on in it, its interference; then the configuration that was active shown again and rebuilt (J13).
`GearboxUpdate.changed` gains the assembly when a flag, a slide value or a put changed anything (W5's rule).

**How D10 lives with mates suppressed on purpose.** W5's D10 reads "a recorded mate found suppressed is turned back
on". In W8 the record says, per coupling and sliding mesh, the configurations it is on in; "found suppressed" means
*found off in a configuration where the record has it on*, and the mirror (found on where the record has it off) is
put right too, since such a mate can over-define that configuration the next time it is shown. A mate on in every
configuration (W5's, the splines, the sliders' axis and slide mates) is exactly W5's D10, read in each configuration.
With one SLIDE per slider there are fewer mates to reconcile than the plan first had (five slide mates in E4 became
two, and none of them is ever suppressed); what a slide can lose is its value, which the value read above covers.

**`finish_update`** (B): each SLIDE entry's per-mode values follow the values set; each `MateEntry.modes` follows the
flags set (D10 puts the record's state back, so it changes nothing; a J14 edit writes the new on-sets); the per-mode
frames on record follow what was put in each mode; W5's rules otherwise.

### 1.11 The record (the schema one past W7's)

`store.LINK_SCHEMA_VERSION` is **one more than W7 leaves it**. W6-PLAN §2.8 sets it to 4 and W7-PLAN §2.11 to one past
W6's (W7-PLAN-REVIEW: so 5), which would make W8's 6; this plan names no number, since the phases before it own
theirs, and the interface commit writes `LINK_SCHEMA_VERSION = <W7's> + 1` from the constant as W7 left it. A record of
any earlier version reads as W8's, with no modes; a record newer than W8's is refused and left byte-identical; a
W7-era reader refuses W8's (W5's D11 mechanism). The shapes build on W7's, which build on W6's (`MateEntry.plane`,
W6-PLAN §2.8) and W5's:

```python
MateEntry += values: Dict[str, float] = {}   # SLIDE: configuration -> its z_front in mm, as set; {} for other kinds
          += modes: List[str] = []           # couples, sliding meshes: the configurations it is on in; [] = every one
GearboxRecord += modes: List[str] = []       # the configurations as built, in Modes-sheet order; the first is the one
                                             # the assembly was saved in; [] = no configuration was added
ComponentEntry += frames: Dict[str, Frame] = {}   # per configuration, the frame last put there; {} = the one frame
```

A SLIDE entry carries W6's `plane = "front"`, W7's `on = ""` (the layout), and W5's `z_front` as its first mode's
value; its `face_global` is `""` (no global). `MateEntry.kind` gains `"slide"`, `"spline"` and `"couple"` on top of
W7's set (W5's four, which W7 keeps: W7-PLAN §2.7); the parse (C) refuses a kind outside that set, gears not as many
as the kind holds (slide 1, spline and couple 2), a SLIDE whose `values` does not name every configuration in
`GearboxRecord.modes` (when there are modes) or holds a 0 or values of both signs (J27), a couple or spline whose ratio
is not `[1, 1]`, and a mate whose `modes` names a configuration not in `GearboxRecord.modes`, each with a
`StoreError` sentence, beside W6's and W7's own refusals. `ComponentEntry.frames` holds each configuration's frame,
since on 2026 each configuration keeps its own (§1.9); with shared positions they are all the same, which the record
cannot tell from per-configuration ones and need not. `finish_build` (B) writes `modes`, every SLIDE's `values`, every
mate's `modes` and every component's per-mode frames (all the built frame, sliders at their values) from the plan.

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
  the assembly."*, *"In mode {N}, the mate {RangeSlv engages InDog} is not suppressed in {N}, where it should be."*,
  *"{RangeSlv}'s place in {4L} reads {0} mm in SolidWorks, not the {66} mm set."*,
  *"SolidWorks would not make the configuration {4L}."*, *"In mode {4L}, {RangeSlv} is not at its position L
  ({66} mm from the Front plane) once the assembly rebuilt."*
- *Footer, on record:* *"It was built with a configuration per mode ({2H, 4H, N and 4L}): pick one in SolidWorks and
  drag {Sun} to turn it."* · after a reorder: *"The Modes rows are in another order now; SolidWorks still opens it in
  {2H}, and Build again… would make {4L} the configuration it opens in."*
- *Update summary:* *"move {RangeSlv} in {4L} to {66.5} mm along {Rear}"*.
- *After Update:* *"moved {RangeSlv} in {4L} to {66.5} mm along {Rear}"* · *"set {RangeSlv}'s place in {4L} back to
  {66} mm, where it had been changed in SolidWorks"* · *"turned the mate {RangeSlv engages LoDog} back on
  in {4L}"* · *"suppressed the mate {RangeSlv engages InDog} again in {4L}, where it was on"* · *"It worked in {4H},
  the configuration that was active, then showed and checked {2H, N and 4L} and left the assembly in {4H}."* · with a
  coupling found out of step in the mode it was found in: *"In {4L} {RangeSlv}'s teeth stood across {LoDog}'s; the
  gears of {4L} are back at the turn they were built at."* (true on either version; a sentence saying the turn came
  from another mode is said only where `POSITIONS_PER_CONFIGURATION` for the running version is False, §1.9) · *"{TransferCase.SLDASM} also has a configuration the
  app did not make ({Exploded}); Update SolidWorks left it as it is."*
- *Progress:* *"Setting up the configuration {4L}…"*, *"Checking mode {4L}…"* (a new `STAGE_MODE`).
- *Speeds panel:* *"{4L}: Rear 375 rpm · Front 375 rpm · 4.000 : 1"*; *"{N}: neutral — {Rear, FrontDrv, Idler and
  Front} turn freely."*; a shared output's torque *"{Rear} {38.416} N·m, shared with {FrontDrv} (the share depends on
  the loads)"*, the members past it *"— (past a split)"* (J17).
- *Quiet Update with modes* (J25): *"It worked in {4H}, the configuration that was active; it did not show the other
  modes, since nothing needed changing."*
- *Footer, about turning* (by `POSITIONS_PER_CONFIGURATION` for the running version; neither claim while it is
  unsettled): True — *"A turn you give the gears in one configuration stays in that configuration."*; False — *"A turn
  you give the gears in one configuration shows in every configuration, so a dog can stand across its sleeve in
  another mode until Update SolidWorks puts the gears back."*

**The window** (D; J21): when the workbook has modes, the Speeds panel's header gets a mode chooser (the theme's
segmented control, one button per mode, the first chosen), and the speeds, torques and ratio lines are that mode's.
The choice is kept across re-reads while a mode of that name exists. The end view draws sleeves and dogs through
`kind_for` (`preview.layout_gearbox`) at the chosen mode's placements; a slide runs along the view direction, so it
does not show there. The header counts modes (`workbook_counts`: *"8 shafts · 11 gears · 4 meshes · 4 modes"* for E4).
Export's Results sheet gets one block per mode, each headed with the mode's name, a shared output's torque in its
Torque column with *"shared with FrontDrv; the share depends on the loads"* in the row's note and nothing in the rows
past it (J17, J19; `export.py`, B). Boards
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

The same, with the planetary replaced by a reverted layshaft train: a 17-tooth pinion on In drives a 34-tooth gear on
the layshaft, whose 17-tooth pinion drives a 34-tooth gear on Lo, a shaft on In's axis carrying LoDog. (The first
version had 15 and 30 teeth at 45 mm; at 20° a 15-tooth pinion carries the strip's undercut warning, so the review's
17 and 34 at 51 mm are used: the same 4 : 1.)

| Shaft | X | Y | Role | Speed | Torque |
|---|---|---|---|---|---|
| In | 0 | 0 | input | 1500 | 10 |
| Lay | 0 | −51 | | | |
| Lo | 0 | 0 | | | |
| Rear | 0 | 0 | output | | |
| FrontDrv | 0 | 0 | | | |
| Idler | 50 | 0 | | | |
| Front | 100 | 0 | output | | |

| Gear | Shaft | At | Kind | Teeth | Module | Face | Slides |
|---|---|---|---|---|---|---|---|
| InPin | In | 10 | spur | 17 | 2 | 10 | |
| InDog | In | 50 | dog | 30 | 1.5 | 6 | |
| LayGear | Lay | 10 | spur | 34 | 2 | 10 | |
| LayPin | Lay | 30 | spur | 17 | 2 | 10 | |
| LoGear | Lo | 30 | spur | 34 | 2 | 10 | |
| LoDog | Lo | 70 | dog | 30 | 1.5 | 6 | |
| RangeSlv | Rear | 60 | sleeve | 30 | 1.5 | 8 | H=-10, N=0, L=+10 |
| FrontDog | FrontDrv | 110 | dog | 30 | 1.5 | 6 | |
| ModeSlv | Rear | 100 | sleeve | 30 | 1.5 | 8 | 2WD=0, 4WD=+10 |
| FDrive | FrontDrv | 130 | spur | 30 | 2 | 10 | |
| FIdler | Idler | 130 | spur | 20 | 2 | 10 | |
| FOut | Front | 130 | spur | 30 | 2 | 10 | |

**Meshes:** InPin–LayGear, LayPin–LoGear, FDrive–FIdler, FIdler–FOut. **Modes:** as §2.1. Centres: both layshaft
meshes `2·(17+34)/2 = 51` = |Y| of Lay. LayGear's tip (⌀72) stays 15 mm clear of the axis at the origin (51 − 36), and
no gear on the origin's axis reaches Lay's (LoGear's tip radius 36 < 51; the sleeve's rim radius 28.875).

"Checks clean" for both fixtures means **no errors**. Warnings the strip itself gives a part stay: on each sleeve and
dog at 20°, the form-diameter warning and, on the sleeves, the ring's tips inside its base circle (§1.1).

### 2.3 The answer key

**Where the sliders sit** (face centre z = At + offset; front face z_front = z − face/2; the dog faces InDog 47–53,
LoDog 67–73, FrontDog 107–113):

| Slider | Position | z | Face span | Covers | its SLIDE's value (z_front) |
|---|---|---|---|---|---|
| RangeSlv | H | 50 | 46–54 | InDog, whole (6 of 6) | 46 mm |
| RangeSlv | N | 60 | 56–64 | nothing (3 mm clear each side) | 56 mm |
| RangeSlv | L | 70 | 66–74 | LoDog, whole | 66 mm |
| ModeSlv | 2WD | 100 | 96–104 | nothing (3 mm short of FrontDog) | 96 mm |
| ModeSlv | 4WD | 110 | 106–114 | FrontDog, whole | 106 mm |

**Slide values per configuration** (what `GetSystemValue3(3, modes)` must read after the build, in mm):
`RangeSlv along Rear` 2H 46, 4H 46, N 56, 4L 66; `ModeSlv along Rear` 2H 96, 4H 106, N 96, 4L 106. All positive and
non-zero, so J27 holds.

InDog and LoDog are 67 − 53 = 14 mm apart and RangeSlv is 8 long: no stroke bridges them. The two sleeves on Rear never
overlap (RangeSlv ends at 74 at most, ModeSlv starts at 96 at least).

**What each mode engages:** 2H: RangeSlv–InDog. 4H: RangeSlv–InDog, ModeSlv–FrontDog. N: nothing. 4L:
RangeSlv–LoDog, ModeSlv–FrontDog.

**Speeds**, rpm, each about its own shaft's axis (+Z here), input In at +1500. In every mode: E4 Carrier +375 (ring
fixed: `1500/(1 + 72/24)`), Ring 0, the planets −750 absolute (−1125 relative to the carrier: W7's convention decides
which the Speeds panel shows); Parallel Lay −750 (`−1500·17/34`), Lo +375 (`+750·17/34`).

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
−15°; 4L Rear +7.5°, FrontDrv +7.5°, Idler −11.25°, Front +7.5°. Every gear turns with its shaft, and the driven
proof reads each one: RangeSlv and ModeSlv as Rear, InDog as In, LoDog as Carrier / Lo, FrontDog and FDrive as
FrontDrv, FIdler as Idler, FOut as Front (E4's planets by W7's convention).

**Torque** (J17 as revised; η 0.98 per mesh, the input 10 N·m; "shared" marks an output that also drives onward, §1.4):

| | Parallel | E4 |
|---|---|---|
| 2H | Rear 10.000 (the coupling is lossless; the idle In → Lay → Lo branch reaches no output and is pruned) | Rear 10.000 (the planetary reaches no output and is pruned, the held Ring included) |
| 4H | Rear 10.000, shared; nothing past Rear (FrontDrv, Idler, Front none) | the same |
| N | nothing past In (every branch from In is idle) | the same |
| 4L | Lay 19.600 (`10·34/17·0.98`), Lo 38.416 (`19.6·34/17·0.98`), Rear 38.416, shared; nothing past Rear | the Carrier's torque by W7's planetary rule (W7-PLAN §2.5), Rear the same, shared; nothing past Rear |

**Phases** (§1.6's rule, mod 12°). No mesh walk reaches a dog (a lock puts no condition on phase), so in Gears-sheet
order InDog starts a walk at 0, RangeSlv gets 6° from it and LoDog 0 from RangeSlv; then FrontDog, before ModeSlv in
both Gears tables, starts a walk at 0 and ModeSlv gets 6°. So: **InDog 0, RangeSlv 6°, LoDog 0, FrontDog 0, ModeSlv
6°** (the first version had FrontDog and ModeSlv the other way round, against its own rule).

**The mates W8 adds** (E4 and Parallel alike), with each configuration's state (a slide's cell is its value in mm; a
slide is on everywhere):

| Mate | Kind | 2H | 4H | N | 4L |
|---|---|---|---|---|---|
| RangeSlv on Rear Axis | axis | on | on | on | on |
| ModeSlv on Rear Axis | axis | on | on | on | on |
| ModeSlv splined to RangeSlv | spline | on | on | on | on |
| RangeSlv along Rear | slide | 46 | 46 | 56 | 66 |
| ModeSlv along Rear | slide | 96 | 106 | 96 | 106 |
| RangeSlv engages InDog | couple | on | on | off | off |
| RangeSlv engages LoDog | couple | off | off | off | on |
| ModeSlv engages FrontDog | couple | off | on | off | on |

RangeSlv is Rear's sliding anchor (Rear has no other gear). In: anchor Sun (E4) / InPin (Parallel), InDog locked to it.
FrontDrv: anchor FrontDog (first in sheet order), FDrive locked to it. Parallel Lo: anchor LoGear, LoDog locked. E4
Carrier: one body with LoDog (§0.2). Made in the order: with only the template's configuration, the two
axis mates, the spline and the two slides (at 46 and 96, the first mode's); then the four configurations, a rebuild, the
eight slide values set and read back; then in 2H RangeSlv engages InDog, in 4H ModeSlv engages FrontDog, in N
nothing, in 4L RangeSlv engages LoDog, each followed by its flags in all five configurations (the template's
included) read back. W5's ALONG globals: Sun 15 / InPin 5, LayGear 5, LoGear 25, FrontDog 107, FIdler 125, FOut 125.

---

## 3. Work packages, ownership and the interface commit

### 3.1 The order of work

```
P (probes ahead, §4) ───────────────────────────────────────────────┐
I (interface commit, after W7 closes) ──► A (SolidWorks) ─┐          ├──► E (demonstration on 2026, then 2024)
                                          B (planning)  ──┼──► D ────┘
                                          C (record, words)┘
```

The W8 spike and its follow-up have run (§4.3, `W8-SPIKE.md`); this plan is written to what they measured. P and I
start together; code reads findings
by `getattr` and refuses when one is missing. A, B and C run in parallel
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
- `set_dimension_in(mate_handle, value_mm: float, configurations: Sequence[str]) -> None` — the mate's `D1`
  (`IFeature.GetFirstDisplayDimension` → `GetDimension`), `SetSystemValue3(value_mm / 1000, 3, names)`; a return other
  than 0 (`swSetValue_Successful`) raises with a sentence; read back with `GetSystemValue3` for those configurations.
  Does not rebuild. Never reads `IDimension.SystemValue` (the follow-up: it answered another configuration's value).
- `dimension_values(mate_handle, configurations: Sequence[str]) -> Dict[str, float]` — `GetSystemValue3(3, names)`, mm,
  no configuration activated. A 0 for a configuration means it has no value of its own (J7's caution); the caller,
  not this member, decides what that means.
- **The handle rule** (pinned; §1.8): `Session` holds a *configuration epoch*, raised by `add_configuration`,
  `show_configuration`, `open_document` / `activate_document` of an assembly, and anything else that can change the
  active configuration (`delete_configuration` does not: held handles survived it in the spike). Every kept
  component handle (`_components`) and kept mate (`_kept_mate`) is stored with the epoch it was fetched in, beside the
  name it was found by. `Session._component(handle)` and `_kept_mate(handle)` fetch again by that name
  (`GetComponentByName`; the mate group walk, `MATE_FIND_ROUTE`) whenever the stored epoch is not the current one; no
  other code holds an `IComponent2` or mate `IFeature` across a call that raises the epoch. Names come from insertion
  (`BuildResult.components`) or `find_component`, never from a fresh handle's `Name2`; selections after a change use
  `SelectByID2("<feature>@<component>@<assembly>")` built from those names, never `GetModelDoc2` on a fresh handle.
  A re-fetch that finds nothing raises `ComponentGone` / `MateGone` with W5's sentences. (The plan's handles — `gear3`,
  `mesh1` — are ids that map to those names, never COM objects, so plans and results are untouched by this rule.)
- `ConfigurationGone(ComponentGone)`: a recorded configuration is not in the assembly (Update → `NotAsBuilt`).
- Every member through `call` / `_guarded`, as W4's N3 requires.

**`swbuild.py`**:

```python
@dataclass(frozen=True)
class ModeStep:
    name: str                                   # the configuration's name: the mode's
    ops: Tuple[base.Op, ...]                    # the Mate ops (couples, sliding meshes) first made in this configuration
    on: Tuple[str, ...]                         # every mate name on in this configuration
    off: Tuple[str, ...]                        # every per-mode mate name off in it
    values: Mapping[str, float]                 # every SLIDE's name -> its |z_front| in mm in this configuration
    frames: Mapping[str, Tuple[Tuple[float, ...], Tuple[float, float, float]]]   # handle -> its frame here (check)

@dataclass(frozen=True)
class ModesPlan:
    steps: Tuple[ModeStep, ...]                 # Modes-sheet order; steps[0] is the one the assembly opens in
    same_way: Tuple[str, ...] = ()              # the steps' gear mates that turn their gears the same way (couples)
    def check(self) -> List[str]: ...           # ids unique across plan and steps; each LinkDimension after its
                                                # mate; on ∪ off the same set in every step; on ∩ off empty; every
                                                # name made exactly once, in the first step it is on in; every
                                                # step's values name every SLIDE, none 0, one sign per SLIDE (J27)

@dataclass
class ModeCheck:
    name: str
    mates: List[MateState]                      # as read in this configuration
    suppressed: Dict[str, bool]                 # every per-mode mate's state here, as read back
    values: Dict[str, float]                    # every SLIDE's value here, as read back (mm)
    clashes: list                               # this configuration's interference, as GearboxResult.clashes holds it
    interference_error: str = ""

GearboxResult += modes: List[ModeCheck]
MateRef += values: Tuple[Tuple[str, float], ...] = (); modes: Tuple[str, ...] = ()   # SLIDE values on record; on-set
MeshLink += modes: Tuple[str, ...] = ()        # the configurations it holds in; () every one
LockLink += modes: Tuple[str, ...] = ()
MotionUpdate += configurations: Tuple[str, ...] = ()
             += mode_placements: Tuple[Tuple[str, Tuple[Placement, ...]], ...] = ()   # wanted, per configuration
             += recorded_by_mode: Tuple[Tuple[str, Tuple[Placement, ...]], ...] = ()  # on record, per configuration
             += slide_values: Tuple[Tuple[str, str, float], ...] = ()   # (SLIDE name, configuration, wanted mm)
             += on_sets: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()   # (per-mode mate, configurations wanted on)
GearboxUpdate += configuration: str = ""       # the one Update worked in
              += visited: List[str]            # the others it post-checked
              += unsuppressed_in: List[Tuple[str, str]]; suppressed_in: List[Tuple[str, str]]   # (mate, configuration)
              += slid: List[Tuple[str, str, float]]   # (SLIDE name, configuration, value) set
              += values_restored: List[Tuple[str, str]]   # (SLIDE name, configuration) set back to the record's
              += put_in: List[str]             # the configurations in which gears were put
              += extra_configurations: List[str]
              += modes: List[ModeCheck]        # the post-check per visited configuration
STAGE_MODE = "mode"                            # Step.name: the mode's name
build(..., modes: Optional[ModesPlan] = None)            # keyword; None is W5 byte for byte
build_gearbox(..., modes: Optional[ModesPlan] = None)    # keyword, passed to build for the assembly
```

The `SolidWorks` protocol gains the eight swcom members. `update_gearbox`'s signature is unchanged: `motion` carries the
modes. `internal` keeps its meaning and is given the splines' and the couplings' names too (§1.7).

**`gears/`**: `gears/clutch.py` with `SleeveKind` and `DogKind` stubs; `WORKBOOK_KINDS` and `kind_for`'s lookup in
`gears/__init__.py`; `spec.default_stem`'s two words (§1.1).

**`workbook/motion.py`** (B): `SLIDE, SPLINE, COUPLE = "slide", "spline", "couple"` added to `MATE_KINDS`;
`MatePlan += values: Tuple[Tuple[str, float], ...] = (), modes: Tuple[str, ...] = ()` (a SLIDE's z_front per
configuration; a per-mode mate's on-set); `mate_name` written for the three kinds (`RangeSlv along Rear`,
`ModeSlv splined to RangeSlv`, `RangeSlv engages InDog`); no slide global; `MotionPlan += modes:
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

**`store.py`** (C owns it after I): §1.11's fields on top of W7's shapes, `LINK_SCHEMA_VERSION` one past the value W7
left (written from W7's constant, never a number of this plan's), and the parse shapes.

**Re-reading §0.1** (review S10): the interface commit checks every claim §0.1 makes about the code against W7's
closing commit and writes in `W8-INTERFACES.md` what moved.

**`ui_text.py`** (C): stubs `modes_ready_line(plan)`, `modes_done_line(plan, result)`, `mode_problem(problem)`,
`modes_record_line(record)`, `mode_update_lines(update, result)`, `mode_speed_lines(spec, report, mode) ->
Tuple[List[str], str]`; existing functions keep their signatures and call these.

### 3.3 The packages

**P — probes ahead** (§4): `findings.py`, `probe/p9_modes.py`, `probe/decide.py`, `probe/__main__.py`'s registry,
`tests/test_findings.py`, `tests/test_probe_modes.py`, `probe/results/**`. Commits first the findings the W8 spike
and its follow-up measured (§4.2, each pinned against `probe/results/w8-spike-20261114-204436.json` or
`w8-followup-20261114-205913.json`), then runs tier 9's two items on SolidWorks 2026 and commits what they found. P starts beside I, before package A's swcom members exist, so the probe makes the **raw COM
calls itself in the shapes §3.2 pins** (the same arguments, the same read-backs), and A's members then copy the
probe's calls, as W5's members copied tier 8's. **Done:** the findings committed and pinned against the result file;
reviewed.

**A — SolidWorks** (`swcom.py`, `swbuild.py`, `tests/test_swbuild.py`, `tests/test_swcom.py`; may add to
`tests/test_swbuild_train.py`, never change an assertion there): the eight swcom members and the handle rule; `build`'s mode phase (§1.8,
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
**Done:** every sentence of §1.12 filled from fields in a test and read as written; every earlier schema read as
W8's, W8's round trip byte-deterministic, a newer one refused and untouched, each new parse refusal.

**D — window, boards, docs** (`workbook_gui.py`, `preview.py`, `gui.py` if needed, `tests/test_workbook_{build,
window}.py`, `tests/test_preview.py`, `design/**`, `docs/**`, `README.md`): the mode chooser, the counts, the end view
at the chosen mode, the footer's new states; the strip's refusal of a sleeve's or dog's `.gear.json` (§1.1); the
two boards rendered and looked at; `UI-DESIGN.md` §9; PLAN-WORKBOOK §4.5 *Readings chosen (W8)* (J1–J27, J16 as an
announced departure from §3.4) and §6's W8 row note; HANDOFF. **Done:** the window launched on
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

**The fake SolidWorks (A, `tests/test_swbuild.py`).** It models what the spike measured on SolidWorks 2026, and makes
the two silent faults loud. Per document: its configurations (the template's `Default` at `new_assembly`), the active
one, saved with the document and reopened in the one it was saved in. `add_configuration` adds and activates, the new
configuration a copy of the active one's flags, values and positions. Per mate, a suppression flag per configuration;
a mate made while a configuration other than the template's is shown comes out **suppressed in the template's and on
in every other** (the spike), with an override `new_mate_elsewhere="on"` for the other plausible default, so the app is
tested against both. **Flags right after an add:** until the first rebuild after an `add_configuration`, the fake's
`set_mate_suppressed_in` answers as the spike saw — the first call raises and still takes effect, the second returns
without taking effect — so a build that sets a flag before the rebuild, or trusts a return, fails its read-back.
**Per-configuration values:** each distance mate's value per configuration, `set_dimension_in` and
`dimension_values` as the follow-up measured (a set while another configuration is active changes only its own; a
configuration with no value of its own reads 0 through `dimension_values`); a rebuild in a configuration stands each
slider at its slide's value there. **Positions per configuration** (2026): each configuration keeps each component's
frame; a put holds in the active configuration only; with `shared_positions=True` the fake shares frames across
configurations (GOTCHAS §83, 2024 as recorded), and every Update test of §3.5 runs both ways. **Stale handles:** every
component and mate handle the fake gives out carries the configuration epoch it was fetched in; **any call on a
handle from an older epoch raises `StaleHandle` (an `AssertionError`), failing the test** — SolidWorks answers None and
False silently, so only the fake can catch a held one. `show_configuration` answers like `ShowConfiguration2` (False
when already active, judged by the name) and marks the assembly modified, never a part (the spike); the flag and value
reads mark nothing. A coupling gear mate holds the relative turn it is made at, as the fake's gear mates do now. What it
does not model, so only SolidWorks shows it: a gear mate between collinear axes turning anything (the spike did); real
interference of the splines; anything about SolidWorks 2024.

**A (against the fake):** a build with modes makes the always-on mates and the slides with only `Default`, adds every
configuration, rebuilds before any flag, sets and reads back every slide value in every configuration, makes each
per-mode mate with the first configuration using it shown, sets and reads back every flag, runs the mate check per
mode through fresh handles, deletes `Default`, saves in the first mode, runs interference per mode, and ends in the
first mode — once with each `new_mate_elsewhere`; a build that skips the rebuild after the adds, trusts a return, or
holds a handle across a show fails (the fake's faults above); a mode whose step over-defines (a doctored plan) stops
the build with *"In mode N, …"*, nothing saved; a build with no `modes` is W5's call for call. Update, each test with
`shared_positions` False and True: in a non-mode configuration refuses before anything changes; a missing
configuration → `NotAsBuilt`; a quiet Update shows no configuration, reads every flag, value and sense, and changes
nothing; D10 both ways for a coupling in an inactive configuration, said, never a call on a mate already right; a slide
value changed in SolidWorks in an inactive configuration set back, and a slide edit set in an inactive configuration,
neither showing it until the post-check; a J14 edit (4H's ModeSlv pick 4WD → 2WD) setting 4H's value and exactly the
changed flags; a shaft moved → every mode shown and put, the active one last, the set connected over every mode's
relations; a train turned in 4L only, Update pressed in 2H with nothing changed → nothing put, nothing shown, the
sentence saying the other modes were not shown; the same with a workbook change → 4L shown and put, every mode clean
after; with `shared_positions=True`, a turn in 2H seen in 4L as a coupling out of step, and every mode put back
consistently; an extra configuration listed and left.

**B (pure):** both fixtures check with no errors (§2.2); §2.3's speeds, ratios, engagements, slider positions, slide
values per configuration and phases pinned per mode; a slider whose positions would put its face on or across the
Front plane in a mode refused at Build (J27); the torque table of §2.3 for Parallel, E4's 2H, 4H and N, and the shared marking;
a meshed shaft free in every mode keeping W3's error and one free in some modes raising nothing (J16); the sleeve's and
dog's tip thicknesses at 20° (§1.1) pinned from the kinds; each check of §1.5 with a made-up workbook (a partial cover, a
teeth mismatch, one sleeve over two dogs, two sliders overlapping, a bridging stroke, a dog never engaged, a blank pick
with no 0, a sleeve on Meshes, a dog with Slides); the outline test of §1.6 in every mode; `motion_plan` and
`modes_plan` for both fixtures against §2.3's mate table and build order (`ModesPlan.check() == []`); a loop closed by
a coupling in one mode left off there (J15); every classify case of J14 with its sentence; `finish_build` and
`finish_update` round trips; every sleeve and dog plan equal to the spur or ring plan of the same values but for its
stem and its kind custom property; `kind_for` never returning a workbook kind for a strip spec (`gui.KIND_VALUES`
unchanged); sliding meshes (made-up workbooks only, §0.1): in and out of mesh per mode, a partial one an error, their
gear mates on only in the modes that mesh them.

**Suite:** `PYTHONPATH=src .venv/bin/python -m pytest -q` on a clean `git archive`, and the Tk tests under Windows
Python, as W5.

---

## 4. Calls probed ahead

PLAN-WORKBOOK's W8 row says "probes (per-configuration mate suppression)". Under the user's rule of 2026-11-14 only a
call new to the app that could hang, raise a dialog, or damage a file or a session is probed before the full build;
the rest is first met in the full build, which the mate checks and read-backs of §1.8 make loud. The W8 spike and its
follow-up (`W8-SPIKE.md`, `ca079ca`, `53e6f33`; results `probe/results/w8-spike-20261114-204436.*` and
`w8-followup-20261114-205913.*`, SolidWorks 2026 34.1.1, each in a fresh session under a dialog watcher) have since run
most of what this section first listed, and more.

### 4.1 Every new call, after the spike

| Call | What is known | Dialog seen? | Still probed ahead? |
|---|---|---|---|
| `AddConfiguration2(name, "", "", 0, "", "", True)` | 2024 SP5 (assemblies/07); 2026, the spike: adds, activates, returns an `IConfiguration`; carries positions and fixed states over | none | no |
| `ShowConfiguration2(name)`, the active name read back | 2026, the spike: True, False when already active; a top-only rebuild after it re-solves the slides; **marks the assembly modified, no part**; **every held component handle goes stale** | none, in every show, on a new and a reopened file | no — except into an **over-defined** configuration (§4.2) |
| `SetSuppression2(0 or 1, 3, names)` on a mate | 2024 (action 0, assemblies/07); 2026, the spike, both actions: right after a rebuild; **unreliable straight after `AddConfiguration2`** (one raised and took effect, one returned False and did nothing) | none | no — the build rebuilds first and reads every flag back |
| `IsSuppressed2(3, names)` | 2024; 2026, the spike: one flag per name, marks nothing | none | no |
| `IDimension.SetSystemValue3(m, 3, [config])`, `GetSystemValue3(3, configs)` | 2026, the follow-up: per configuration, while another is active, through a save and reopen; reads 0 for a configuration with no value of its own; `SystemValue` unreliable | none | no |
| `DeleteConfiguration2(name)` | 2026 parts (API-LEDGER); 2026 assembly, the spike: True, held handles survive it | none | no |
| `SaveAs3` silent with several configurations; `OpenDoc6`; `CloseDoc` unsaved after a switch | 2026, the spike: no window but the self-closing load-progress box; reopens in the configuration active at the save, every document unmodified; an unsaved close after a show discards without asking | none that needed an answer | no |
| `AddMate5(MATE_GEAR, …)` between two collinear axes; its sense read, also while suppressed | 2026, the spike (§1.7) | none | no |
| `IEquationMgr.Add2` linking a dimension once several configurations exist | 2026, the spike: **returned −1** | none | no longer used (J7) |
| `ToolsCheckInterference` after a show | W4's call, one configuration | — | no |
| `ShowConfiguration2` into a configuration whose mates fight | **not tried** | — | **yes** (§4.2) |
| Opening a copied assembly with its original folder moved aside (the scripts' J24 only) | **not tried** | — | **yes** (§4.2) |

### 4.2 What is still probed ahead: tier 9, two items

With the spike done, two things are left that could raise a dialog. Probe `p9_modes.py` (package P) runs them on
SolidWorks 2026 in a fresh session under the spike's dialog watcher, with the raw calls in §3.2's shapes and the
handle rule applied:

1. **An over-defined configuration shown.** The build never shows one (§1.8 step 5), but a user's edit in SolidWorks
   can make one, and Update shows configurations after any change (§1.10). On the spike's scratch shape: a second
   slide mate on the sleeve turned on in one configuration beside the first, that configuration shown and rebuilt
   under the watcher: what `ShowConfiguration2` answers, the error codes, whether any window opens, and whether showing
   another configuration afterwards solves cleanly. If a window opens that needs an answer, Update's post-check reads
   every flag and value first and refuses, before showing anything, when a configuration's on mates would fight
   (two slides on one slider, a coupling and a lock across the same pair), naming the mate (*"In {4L} the mate {Distance3}
   is on beside {RangeSlv along Rear}; suppress it in SolidWorks and press Update SolidWorks again."*).
2. **The copy of a built folder** (J24, review S7), the scripts' only: every document closed; the folder copied; the
   original renamed aside and the rename checked (Windows refuses one while a handle in it is open); the copy's
   assembly opened under the watcher (SolidWorks searches for references not where they were stored, and may ask);
   every component's `GetPathName` read back in the copy; the copy saved, closed, the original renamed back; reopened
   and read again. If anything asks or resolves outside the copy, E uses `ReplaceReferencedDocument` on the closed
   copy (GOTCHAS §16; unverified) or Pack and Go, probed the same way first, or builds each section's fixture afresh.

Nothing else W8 calls is new and able to hang or raise a dialog. SolidWorks 2024 meets every configuration call for the
first time in the confirming run (§5, `s7` first), under the scripts' dialog watcher; that is the rule's confirming
build, not a probe, but `s7` is ordered first so that a 2024 difference is seen before anything is built on it.

**Findings** (package P commits them, each pinned in `tests/test_findings.py` against the result file it comes from):

```python
# the W8 spike and follow-up, SolidWorks 2026 (34.1.1)
CONFIGURATION_ADD_ROUTE = "AddConfiguration2(name, '', '', 0, '', '', True)"
CONFIGURATION_SHOW_ROUTE = "ShowConfiguration2, active name read back"
CONFIGURATION_DELETE_ROUTE = "DeleteConfiguration2, names read back"
SPECIFY_CONFIGURATIONS = 3                      # swInConfigurationOpts_e.swSpecifyConfiguration
MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE = "SetSuppression2(action, 3, names) after a rebuild; IsSuppressed2(3, names)"
SUPPRESSION_RIGHT_AFTER_ADD = "unreliable"      # rebuild first, read every flag back
SLIDE_VALUE_ROUTE = "SetSystemValue3(m, 3, [configuration]); GetSystemValue3(3, configurations)"
SET_VALUE_IN_SPECIFIC_CONFIGURATIONS = 3        # swSetValue_InSpecificConfigurations; swSetValue_Successful is 0
VALUE_UNSET_READS_ZERO = True                   # set every configuration's value explicitly
HANDLES_STALE_AFTER_CONFIGURATION_CHANGE = True # after AddConfiguration2 and ShowConfiguration2; not after Delete
FIXED_KEPT_IN_NEW_CONFIGURATION = True          # read through a fresh handle
POSITIONS_PER_CONFIGURATION_ON_2026 = True      # follow-up B
POSITIONS_PER_CONFIGURATION_ON_2024 = None      # s7; until then the 2024 sentences make neither claim (§1.9)
NEW_MATE_IN_OTHER_CONFIGURATIONS = "suppressed in the template's, on in the others"
CONFIGURATION_SHOW_RAISES_DIALOG = False
CONFIGURATION_SHOW_MARKS = "assembly"
SUPPRESSION_READ_MARKS = "nothing"
VALUE_READ_MARKS = "nothing"
SUPPRESSED_GEAR_MATE_SENSE_READ = "answers, marks nothing"
MULTI_CONFIGURATION_SAVE_ASKS = False
REOPENS_IN_SAVED_CONFIGURATION = True
COLLINEAR_GEAR_MATE_SENSE_READ_BACK = True      # spike steps 1-3 and 5; tau never -1
COLLINEAR_GEAR_MATE_HOLDS_SLIDE = True          # spike step 4 (a global then), follow-up A (a value per configuration)
# tier 9
CONFIGURATION_SHOW_OVER_DEFINED = "…"           # item 1
COPY_REFERENCES_FOUND_BESIDE = …                # item 2: True, or the route E takes instead
```

`modes_reason()` (B, in `motion.py`, beside `motion_reason`) is `""` only when the routes, `SPECIFY_CONFIGURATIONS`
and `SET_VALUE_IN_SPECIFIC_CONFIGURATIONS` are set as above, `HANDLES_STALE_AFTER_CONFIGURATION_CHANGE` is not None
(the session layer refuses to run without knowing), `CONFIGURATION_SHOW_RAISES_DIALOG` and
`MULTI_CONFIGURATION_SAVE_ASKS` are False, `REOPENS_IN_SAVED_CONFIGURATION` and `COLLINEAR_GEAR_MATE_SENSE_READ_BACK`
are True, and the marks findings are set; otherwise a gearbox with modes is refused at Build with the sentence naming
the finding (never built static: a static assembly cannot hold modes). The findings are SolidWorks 2026's; the 2024
confirming run either confirms each or the plan's per-version reading applies (§1.9, §5 `s7`).

### 4.3 The collinear gear mate spike: run

§4.3 of the reviewed plan set out what a spike of J8 had to measure; the coordinator had it run, and `W8-SPIKE.md` is
its report. It measured every step asked (the spline made between collinear axes with the sleeve free to slide;
`Reverse` and both directions read back; the drive; the both-Flips control; the slide changed with the gear mate on;
the coupling; per-configuration suppression read back in each configuration; the coupling at an arbitrary angle;
save and reopen), and its follow-up measured two more (one distance mate with a value per configuration; what a
configuration keeps of a turn). What it showed is written into §1.7–§1.10 and the findings above; what it changed is
in *Changes after the spike*.

## 5. The demonstration (package E), full build first

Through the app's own code as W5's script is (`plan_gearbox` → `build_gearbox(session, **plan.build_kwargs())` →
`finish_build`; `classify` → `update_gearbox` → `finish_update`; every footer sentence logged), Excel driven by the
script's own Excel, logs under `probe/results/` (2024 under `sw2024/`), no user titles, a dialog watcher running
throughout. New sections in `probe/workbook_assembly_check.py`, `s0`–`s7`, and `--only modes` to run them. The
script's own SolidWorks calls follow §1.8's handle rule: every component and mate handle fetched again by a name held
from before after every configuration change, every selection by full name (`SelectByID2`); the spike's first three
runs stopped on exactly this.

**Build each fixture once (J24).** `s0` and `s1` build. Every later section starts from a copy of `s1`'s built
folder (by the route tier 9 item 2 settles): every SolidWorks document of it closed (`QuitDoc`); the folder copied; the copy's link record and `.gear.json`
files rewritten to the copy's paths (the script's own helper over `store`'s load and save); the original folder
renamed aside; the copy's assembly opened (`OpenDoc6`), so SolidWorks finds its parts and layout beside it; every
reference read back (each component's `GetPathName` in the copy's folder); the assembly saved by the script, so its
references are the copy's; closed; the original folder renamed back. The section then reads the copy's state as a
reopened gearbox (every flag False after the open). This is the change HANDOFF asks for; it is reviewed like code.

**What every mode gets measured, in every build and after every Update** (§4.1 of W5-PLAN per configuration): the
active name read back; without showing anything, every mate's flag in every configuration (`IsSuppressed2(3, …)`)
and every slide's value in every configuration (`GetSystemValue3(3, …)`) against the record; then in each
configuration after a show, the train's rebuild and handles fetched again: every gear's frame (each slider at its value
to 1e-6 mm, every other gear at its frame on record for that configuration), every on mate code 0 and every per-mode
mate off reading suppressed, every mated gear `GetConstrainedStatus` 2, the layout and every fixed gear `IsFixed` True
through the fresh handle, interference none; per mode a **half-pitch control** on each engaged coupling: the dog put 6°
about its own axis with the coupling on (`MESH_PHASE_ROUTE`) and **every lock touching the dog suppressed in this
configuration around the put** (a dog is locked to its shaft's anchor, and a put with the lock on moves the dog alone,
after which the lock takes the new angle: P0, P0b), which must interfere with its sleeve only; put back, the locks
turned on again, none; then, as W5's M12 rules (review S11), **every frame against its frame on record to 1e-6 and no
lock left suppressed**. The control's put holds in its own configuration only (2026), so each mode's control is made
and undone with that mode shown, and the other modes are read afterwards to show they were not touched. A disengaged
dog shows no clash. (No fixture has a sliding mesh, so no control runs on one: §0.1.) Saved, closed, reopened: opens
in the first mode, every document unmodified straight after the open, the flags, values and frames the same.

**The driven proof per mode** (the script's, never the app's; W5's angle-mate drive on the input's anchor, a global
"Drive" 90 → 120): **every gear's** turn about its own axis (`turn_between`), the sleeves and the dogs included, against
§2.3's 30° row to 1e-6 relative, sign included — not only one per shaft: a wrong spline (ModeSlv against RangeSlv)
and a wrong `ModeSlv engages FrontDog` would cancel at the Front in 4H and 4L, and only ModeSlv's own turn shows
them (review M6). Gears free in that mode must not turn (more than 1e-6 is a NOTE, logged and listed, not a FAIL: an
unconnected train is SolidWorks' solver's to leave).

**The both-Flips control** (review M6; W5-DECISIONS, *Rulings at W5's close*: the Flip a new gear mate needs is not
predicted, on either version, from anything, and W5's first 2026 run failed twice on a control that assumed it; m3
and m7 were rerun with a control that drives both Flips). In 4L on `RangeSlv engages LoDog`, and in 4H on the spline
`ModeSlv splined to RangeSlv`: the recorded mate suppressed in that configuration; a temporary 1 : 1 gear mate in its
place **with Flip False**, its `gear_mate_sense` read and logged, driven, every gear's turn read; deleted; a temporary
mate **with Flip True**, read, driven, read; deleted. **Exactly one of the two Flips must turn the gears the right way**
(in 4L Rear with the carrier, at a quarter of the input; in 4H ModeSlv with RangeSlv), and the one the read-back calls right must be
that one; both right, both wrong, or the read-back disagreeing is a FAIL and a STOP (§0.5). Then W5's M12 hygiene:
"Drive" set back before the control mate is deleted, the recorded mate back on in that configuration only, every frame
at the built frame to 1e-6, no Drive global, angle mate or control mate left, no lock suppressed, every flag in every
configuration as recorded.

**Sections.**

- **`s0` — TransferCase_Parallel** (the shakedown, W7-free): build; every measurement above in each mode; the driven
  proof per mode with both both-Flips controls; reopen. Run first on 2026; it isolates W8's machinery from W7's. It is
  the first build of the `sleeve` and `dog` kinds (the spike used the strip's spur and ring) and the second sight of
  the collinear gear mate.
- **`s1` — the E4 transfer case:** build (the one fresh E4 build); every measurement in each mode; the driven proof in
  each mode, with the both-Flips controls in 4L and 4H; reopen. This is PLAN-WORKBOOK's *"The E4 transfer case's four
  modes"*.
- **`s2` — turning and switching** (a copy of s1). In 2H the user's turn simulated (driven 37°, the drive deleted).
  Shown 4H, N, 4L in turn: every frame read and logged against its frame on record. On 2026 every other mode stands
  exactly as built — the turn stayed in 2H — and every coupling is in step with no interference (`POSITIONS_PER_
  CONFIGURATION_ON_2026`); 2H shown again stands at the 37° turn. In 4L, Update with nothing in the workbook changed: a
  quiet Update — nothing put, nothing shown, every flag, value and sense read, every frame and document flag the same
  before and after (`GetSaveFlag` False throughout, since nothing is shown), the sentence saying it did not show the
  other modes. Then a workbook change that touches every mode: Excel FDrive, FIdler and FOut At 130 → 132 (FIdler's
  and FOut's Face Z globals, assembly-wide, and FDrive a follower) → Update: every mode shown and put, the active one
  (4L) last; 2H's 37° turn put back too (W5's answer 2: a mode that needs a put is put whole); every mode clean in the
  post-check, every frame at its new wanted frame in every configuration; the assembly left in 4L; the sentence naming
  every mode shown. On SolidWorks 2024 the same section is run and its readings say which reading of §1.9 holds there
  (with shared positions the 37° turn shows in every mode, and the quiet Update in 4L finds a coupling out of step and
  puts 4L, then — having changed something — shows and checks the others).
- **`s3` — D10 per configuration and the refusals** (a copy of s1): in 4L `RangeSlv engages LoDog` suppressed and
  `RangeSlv engages InDog` turned on, and `RangeSlv along Rear`'s value in N set to 58 by the script
  (`SetSystemValue3`, 2H active) → Update in 2H puts all three right (the two flags in 4L, the value in N) and says
  so, showing nothing in the check, then shows and checks every mode since it changed something; an angle mate the
  record does not know, on in N only → Update refuses naming it and N; suppressed → listed and left; a configuration
  `Exploded` added by the script → listed and left; made active → Update refuses before changing anything; `4H`
  deleted → `NotAsBuilt` and Build again… offered.
- **`s4` — the edits Update carries, then a structural one** (a copy of s1, 2H active throughout the edits):
  Excel `RangeSlv` Slides `L=+10` → `L=+10.5` (still covers LoDog: 66.5–74.5 over 67–73) → Update sets
  `RangeSlv along Rear`'s value in 4L 66 → 66.5 **while 2H is active** (the follow-up's case) and changes no other
  configuration's value, read back for all four; 4L shown in the post-check, its frames and the drive there.
  `ModeSlv` At 100 → 101 with Slides `2WD=0, 4WD=+9` (4WD stays at 110; 2WD 97–105 still clear) → Update sets
  `ModeSlv along Rear` to 97 in 2H and N and finds 4H's and 4L's 106 already right. Then Modes 4H's ModeSlv `4WD` →
  `2WD` → an Update (J14): `ModeSlv along Rear`'s value in 4H set to 97 and `ModeSlv engages FrontDog` suppressed in
  4H, read back in every configuration; 4H's frames and the drive there, which now drives no front. Then a Modes row
  added, `4X` = (L, 2WD) → the structural sentence, Build again… → `_r2` built with its five configurations, measured;
  every earlier file's sha256 and mtime unchanged.
- **`s5` — the refused mate in one mode, forced** (a copy of s1's workbook, built fresh: the refusal is the point): the
  plan doctored by the script with a second distance mate on RangeSlv, on in N only, beside its SLIDE → the build stops
  with *"In mode N, … over-defines the assembly."*; the parts and layout part saved and on record, no assembly file, the
  document left open and named; the footer never offering the same build again; then closed as W5's m4 closes it. (The
  build shows N to check it, so tier 9 item 1 must have settled what showing an over-defined configuration does
  before this section runs.)
- **`s6` — the person's step** (handed to the user, 2026 then 2024): *"In SolidWorks, open the TransferCase.SLDASM the
  demonstration built (its folder is in the log). It opens in 2H. Pick the configuration 4L in the ConfigurationManager.
  RangeSlv, the sleeve between the two dog rings, now sits over LoDog, and ModeSlv over FrontDog. Drag the sun, the small
  gear at the front on In, round by about a quarter turn: the rear sleeves and the front output gear turn the same way
  as the sun at a quarter of its angle, and the idler between the front gears the other way. Then pick N: drag the sun
  again; the rear and front stand still. Then pick 4L again and tell us whether the gears stand where you left them in
  4L, or where you left them in N. Then, with 4L showing, press Update SolidWorks in the Workbook window with nothing
  changed: the footer should say the gears stand where they were turned and that the other modes were not shown. Tell
  us what you saw, on each version."* (The question about where the gears stand is the person's view of §1.9; the
  answer is expected to differ if 2024 shares positions.)
- **`s7` — what a configuration keeps, on 2024 first** (run on 2026 too, as the control that it reads as the
  follow-up did): on the built E4 (a copy of s1), with handles fetched again after every change: in N, where FrontDrv's
  train is free, FIdler put 20° about its own axis (a put on a fresh handle) and rebuilt; 4H shown and rebuilt: FIdler's
  turn read; N shown again: read; FIdler put 10° in 4H; N shown: read; saved, reopened, read in each. Also on the same
  copy: `RangeSlv along Rear`'s value in 4L set while 2H is active and read back without activating; every handle held
  across a show read once (logged: does 2024 answer None and False too, or something else?); the layout's `IsFixed`
  through fresh handles in each configuration. The readings set `POSITIONS_PER_CONFIGURATION_ON_2024` and confirm or
  deny each 2026 finding of §4.2 on 2024; a difference that §1.9 does not already cover is a STOP before the rest of
  the 2024 run.
- **window** (`workbook_window_check.py`, 2026): the Speeds panel with the chooser on 4L, on N, and the built footer.

**SolidWorks 2024, the confirming build** (the rule's "one full build plus every section where the versions have been
seen to differ"): `s7` first (it measures where 2024 may differ: positions per configuration, per-configuration
values, stale handles, the fixed state), then `s0`, `s1`, `s2` (turning and switching, which reads differently if
positions are shared) and `s3` (the per-configuration flags and values), and the window check. Each started fresh,
under the dialog watcher, the user's documents untouched. If 2024 refuses per-configuration values, the run stops
after `s7` and W8 refuses modes on 2024 with `modes_reason()`'s sentence (§1.9): that is the one outcome no design in
this plan survives on that version.

---

## 6. Definition of done

1. The W8 spike and its follow-up are in (`W8-SPIKE.md`). Probe tier 9's two items (§4.2) run on 2026; every finding
   of §4.2 committed and pinned against its result file; reviewed.
2. Packages I, A–D committed, each reviewed independently; the suite green on a clean `git archive`; the Tk tests
   green under Windows Python; the fake's stale-handle and flag-after-add faults on, with no test silenced.
3. Both fixtures check with no errors, with §2.3's numbers, recomputed by an independent subagent from §2's tables alone.
4. On SolidWorks 2026: `s0`–`s5` and `s7` pass, 0 failed; one full run at the close from the final source. On 2024:
   `s7`, `s0`, `s1`, `s2`, `s3` and the window check pass, `POSITIONS_PER_CONFIGURATION_ON_2024` committed, and the
   sentences of §1.9 chosen by it. Logs committed.
5. The person's step handed to the user; the readings J1–J27 handed with it as readings they may overrule, J1, J2,
   J16, J14 and J11 first (§0.4).
6. `PLAN-WORKBOOK.md` §4.5 *Readings chosen (W8)*, a dated note under §6's W8 row, `UI-DESIGN.md` §9, the two
   boards, HANDOFF's table and W8 section; the macro database is the user's to update (GOTCHAS §83 against 2026's
   reading), and HANDOFF says so.

## 7. Risks, and what reading could not settle

- **What is still probed ahead** (§4.2): with the spike done, two things only could raise a dialog — showing a
  configuration whose mates fight (a user's edit can make one, and Update and the build's mode check show
  configurations), and opening a copied assembly with its original folder moved aside (the scripts' J24 alone). No
  call the spike made raised a dialog. SolidWorks 2024 meets every configuration call first in its confirming run,
  `s7` first, under the dialog watcher.
- **The two versions may differ on what a configuration keeps** (J11, §1.9). The follow-up found 2026 keeping each
  component's place per configuration; GOTCHAS §83 and assemblies/07, recorded on 2024 for a free mechanism, say the
  opposite. The build, Update's per-mode puts and a quiet Update's reads are right either way; what the app *says*
  about a turn and a switch cannot be, and is chosen by a per-version finding that `s7` settles for 2024. If 2024
  refuses per-configuration slide values, modes are refused on 2024.
- **The handle rule** is the widest change the spike forced: a held handle answers None and False without an error,
  so a missed re-fetch is a silent wrong reading, not a failure. The fake fails a test on any held handle; on
  SolidWorks a None frame or an unfixed layout is a STOP. Twice in the spike's earlier runs a freshly fetched handle
  answered `GetModelDoc2` None or an empty `Name2`; the rule never relies on either.
- **Collinear gear mates (J8)** held in the spike, with two caveats: the per-entity sign τ was never −1 (no sleeve or
  dog on a Z− shaft has been made), and the parts were the strip's spur and ring, not the `sleeve` and `dog` kinds;
  `s0` is their first build. A sleeve on a Z− shaft facing a dog on a Z+ one (coaxial, opposite senses) is allowed by
  §1.3 and unshown: the sense read-back's cross-check against the shafts' senses (`_sense_read`) would stop a wrong
  one as a refused mate. If a later fixture needs it, it is the first thing to try.
- **A slide at the Front plane** (J27): a distance of 0, and values of both signs on one mate, were not tried; the
  plan refuses them rather than test them.
- **What a slide value set marks** could not be told in the follow-up (the new assembly read modified throughout);
  an Update that sets one has changed the assembly anyway, so nothing depends on it.
- **Per-configuration distance values** replaced the per-configuration distance mates that failed in assemblies/07
  (2024): one mate per slider, never two on at once, so nothing can fight it; the follow-up measured it on 2026 and
  `s7` on 2024.
- **The splines' fit** (corrected after the review, M1). The fillets are not where the fit is tight: the dog's
  0.57 mm root fillet rises about 0.03 mm off its flank at the sleeve's tip radius (21 mm). What a sleeve over a dog
  has is **play: 0.45 mm per flank at the pitch circle** (each part carries the strip's 0.3 × module backlash), 0.9 mm
  in all, about ±1.15° of turn. So at the built turn the teeth stand clear with room, the half-pitch control (6°) is
  far past the play and must clash, and a drive cannot bring them into contact while the coupling holds them. The
  thin tip was the other risk, and J2's 20° removes it (dog tip 0.626 mm, sleeve 1.153 mm, against 0.022 mm for a
  full-depth 30° dog). §1.6's outline test decides the fit, pure, before SolidWorks does; the interference check in
  each mode confirms it. A workbook that types 30° gets the strip's thin-tip warning on each sleeve and dog row.
- **W7 dependencies** (§0.2): a gear on a carrier shaft, coaxial frame shafts in checks and the layout part, W7's
  loop of gear mates in every configuration, and W7's carrier skeleton under four configurations — now also under the
  handle rule and per-configuration positions, which W7 did not have to meet. None is W8's to change; each, if
  missing, is a stop.
- **The record's schema** is owned by W6 and W7 before W8; W8's is one past whatever W7 leaves (§1.11). If W6 or W7
  change their numbering when they are built, W8 follows at its interface commit; nothing in this plan pins a number.
- **Free trains under a drive.** The spike's dog, not coupled in Y, stood still while the anchor was driven there; the demonstration still logs any other case as a NOTE.
- **Time and memory.** E4 has 11 gear rows, three planet copies and four configurations: four shows and rebuilds, four
  mate checks and four interference checks per build, and as many shows and puts per changed Update (per-mode puts).
  The spike's assembly took 141 s and its follow-up 75 s with three components; E4 is not measured. 2024's memory
  guard stays.
- **What reading could not settle.** Canvas E4 gives only the five new rows, the planetary by reference to E3, and the
  front drive in words: the planetary's face widths and axial place, and the whole front drive (FDrive, FIdler, FOut,
  their shafts and teeth), are this plan's choices, as are the Parallel fixture's numbers. Canvas E4's *"switches off
  the locks it doesn't engage"* names locks; this plan uses gear mates (J8), and its *"each sets every sleeve's slide
  distance"* is now exactly what a configuration does (J7). How W7 will name and mate the carrier, and whether it gives
  the planets' speeds absolute or relative to the carrier, is W7's; §2.3 gives both. Whether a configuration added
  later than the template copies the *active* configuration's positions or the template's was not separated in the
  spike (every add there came from a configuration standing at the same positions); the build adds every configuration
  before anything moves, so it does not depend on which.

---

## Changes after the review

The review is `W8-PLAN-REVIEW.md` (`24347e9`): go with six changes. The orchestrator's rulings on it, of the same day,
are followed item by item; nothing was declined.

- **M1 (the 30° default).** J2 now gives a sleeve and a dog no pressure angle of their own: a blank takes the Box's
  (20°, the strip's own), and a workbook may type another. Canvas E4's 30° stub-tooth spline is said not to be built,
  since the strip makes full-depth teeth only. §1.1 pins the tips at 20° (dog 0.626 mm, sleeve 1.153 mm) and gives the
  reason against 30° (a 0.022 mm dog tip). §7's fit risk is corrected: not the fillets but the 0.45 mm play per flank.
  J1 and J2 head the list for the user (§0.4).
- **M2 (torque).** The "and no fixed shaft" clause is gone: a branch is pruned when it reaches no output in that mode.
  J17 and §1.4 add that an output shaft that also drives onward is a split: it is given the torque arriving at it,
  marked as shared, and nothing past it — W3's split applied at the output, no new theory. §1.12 says what the
  Results sheet and the Speeds panel show for it. §2.3's torques are a table that agrees with the rule.
- **M3 (phases).** §2.3's key now follows §1.6's walk: InDog 0, RangeSlv 6°, LoDog 0, FrontDog 0, ModeSlv 6°.
- **M4 (schema).** §1.11 names no number: `LINK_SCHEMA_VERSION` is one past W7's (W6-PLAN sets 4, W7-PLAN one past
  W6's, so W8's would be 6), every earlier version reads, the shapes build on W6's `plane` and W7's `on`, and the kinds
  are W7's set plus the three. §0.2 cites what W7-PLAN already provides (a gear on a carrier shaft, the coaxial
  exemption, bodies, its torque rule).
- **M5 (Update's puts).** New reading J26: in a gearbox with modes the put set is connected over every mode's
  relations; a set not put is judged in the other modes by `train_check`, never by built frames (§1.9, §1.10). A fake
  test and s2's reverse case (turn in 4L, Update in 2H) show it.
- **M6 (the control).** The wrong-sense control is replaced by W5's both-Flips control (W5-DECISIONS, *Rulings at
  W5's close*): Flip False and Flip True each made, read and driven, exactly one turning right and the read-back
  agreeing, in 4L on a coupling and in 4H on the spline. The driven proof reads every gear's turn, sliders included.
- **S1 (J16).** Announced as a departure from PLAN-WORKBOOK §3.4 and put to the user; `_check_motion`'s free-shaft
  error is kept for a meshed shaft free in every mode only; `Report.motion` is the first mode's (§1.5).
- **S2.** A rebuild after every show, interference included (§1.8 step 6).
- **S3.** `IsFixed` of the layout and fixed gears read in each configuration, in tier 9 and in the per-mode check,
  with W5's `Fix` in each new configuration if it is not carried over.
- **S4.** Tier 9 links the slide mates' D1 to globals, turns a mate on in an inactive listed configuration (the
  citation of assemblies/07 for "0 / 1" corrected to action 0 only), reads every document's save flag around each show,
  calls `ShowConfiguration2` with `CommandInProgress` off as the app will, makes the raw calls in §3.2's shapes for A to
  copy, and drives its collinear coupling.
- **S5.** Sliding gears are said to be shown against the fake only (§0.1, §3.5, §5); no fixture gained one.
- **S6 (J14).** The cheaper reading is taken as the default: an edit after which every mate the modes need is on
  record (a Modes pick between existing positions) is an Update by flags alone; rows added, removed or renamed, and
  anything needing a new mate, stay structural. s4 shows both.
- **S7.** The copy of a built folder is rehearsed in tier 9 under the dialog watcher, the folder rename checked, with
  `ReplaceReferencedDocument` and Pack and Go named as the other routes (J24, §4.2 item 5, §7).
- **S8.** New reading J25: a quiet Update reads only the active configuration's gear mates' senses, a narrowing of
  W5's ruling, said in the sentences and lifted if tier 9 shows a suppressed gear mate's sense reads cleanly.
- **S9.** The strip refuses a sleeve's or dog's `.gear.json` with a sentence; the clutch kinds write their own kind
  custom property (§1.1, §3.3 D).
- **S10.** The interface commit re-reads §0.1 against W7's close and records what moved (§0.2, §3.2).
- **S11.** The half-pitch control suppresses the dog's locks around its put and ends with every frame at the built
  frame and no lock suppressed (§5).
- **Notes taken.** §1.5's coaxial exemption comes before `_check_clearances`' ring branch; the coupling's teeth check
  reads `spec_values`; a coupling never reaches `_check_mesh` or `internal.tip_clash` (§1.3). Parallel's pinions are
  17 and 34 teeth at 51 mm, so no undercut warning; "checks clean" means no errors (§2.2). J5 covers a slider with no
  position at 0 when there are no Modes rows.
- **The coordinator's addition.** §4.3, *The collinear gear mate spike (for the probe agent, as written)*: what a
  spike must make and measure — the mate between collinear axes with the sleeve free to slide, `Reverse` and the
  directions read back, the drive, the both-Flips control, the slide's distance mate changed with the gear mate on,
  and per-configuration suppression read back in each configuration. J8 and §1.7 mark the collinear read-back as
  untested until it or the shakedown has run.

---

## Changes after the spike

The W8 spike and its follow-up (`W8-SPIKE.md`, `ca079ca`, `53e6f33`; SolidWorks 2026 34.1.1) measured what this plan
had left open; the orchestrator's rulings on them, of 2026-11-14, are followed item by item. The rulings already made
stand: the Box's 20° pressure angle, no fork groove, the collinear gear mate, one configuration per mode, the schema one
past W7's. Where *Changes after the review* above describes something this section replaces, this section wins.

1. **The collinear 1 : 1 gear mate stays** (J8, §1.7): accepted, nothing moved on making it, the sleeve stayed free to
   slide, the both-Flips control showed exactly one Flip right and the read-back named it, the slide moved 10.0 mm with
   the spline on and the drive stayed 1 : 1, and a suppressed coupling's sense read cleanly. Carried as caveats: τ was
   never −1, and the parts were the strip's spur and ring, not the sleeve and dog kinds (`s0` builds those first).
   `COLLINEAR_GEAR_MATE_SENSE_READ_BACK` and `COLLINEAR_GEAR_MATE_HOLDS_SLIDE` are pinned from the result files (§4.2).
2. **Slides change design** (J7, J23, J27, §1.7, §1.8, §1.10, §1.11, §2.3, §3.2, §5): one distance mate per slider, its
   value set per configuration with `SetSystemValue3(m, 3, [configuration])` and read with `GetSystemValue3(3,
   configurations)` without activating; no slide globals, no mate per position, nothing suppressed for a slide (the
   per-position design's second `Add2` link returned −1 once several configurations existed). Written in: every
   configuration's value set explicitly at the build and all read back, since an unset one reads 0; never
   `IDimension.SystemValue`; what a set marks is unknown and nothing depends on it; a position at the Front plane, or
   values of both signs on one slide, are refused at Build and structural in Update (J27), since neither was tried.
   Update sets one configuration's value while another is active (measured). Classification (J14): every slider place
   in every mode is now a value, so a pick change, an offset, an At or a renamed position is an Update; only new
   configurations, new slide mates and new couplings are structural. The record keeps each SLIDE's per-configuration
   `values` in place of per-mode slide mates, and per-configuration component frames. D10 per configuration reconciles
   couplings and sliding meshes only (five slide mates in E4 became two, never suppressed), plus a value check for each
   slide in each configuration. The demonstration's s3 and s4 set and restore values in inactive configurations.
3. **Handles go stale** (§1.8's handle rule, §3.2, §3.5, §0.5): after every `AddConfiguration2` and
   `ShowConfiguration2` (and an open), every component and mate handle is fetched again by a name held from before;
   pinned as a configuration epoch in `swcom.Session`, with `_component` / `_kept_mate` re-fetching on a stale epoch,
   selections by full name, never a fresh handle's `Name2` or `GetModelDoc2`. The fake raises `StaleHandle` on any
   held handle, so a test catches one. §1.8's `IsFixed` reading is rewritten around a fresh handle (it read False on a
   held one even for the fixed layout); `AddConfiguration2` carries the fixed state over (measured), so a fixed
   component reading unfixed through a fresh handle is a problem, not a cue to fix it.
4. **A rebuild between `AddConfiguration2` and the first `SetSuppression2`**, and no return value trusted: §1.8 step 3,
   every flag read back with `IsSuppressed2(3, …)`; the fake misbehaves as the spike saw until the rebuild.
5. **Positions are kept per configuration on 2026** (J11, J25, J26, §1.9, §1.10, §5): the user's turn belongs to the mode
   it was made in; a put holds in the configuration shown, so Update's puts are made mode by mode, each with that
   configuration shown, the set in each the gears connected over every mode's relations (M5's ruling kept); a newly
   engaged coupling inherits no angle, and §1.9 is rewritten: each configuration starts as a copy of the built turn and
   each coupling is made in its own configuration at it. `COUPLING_KEEPS_ANGLE_ON_SWITCH` is gone, replaced by
   `POSITIONS_PER_CONFIGURATION_ON_2026 = True`. A quiet Update reads only what needs no show (a show marks the
   assembly): the active configuration's frames, codes and statuses; every flag, value and gear mate sense in every
   configuration. It leaves unread every other mode's frames, codes and constrained statuses, and says so. The S8
   narrowing of sense reads is not needed (a suppressed gear mate's sense reads cleanly).
6. **2024 may differ** (§1.9, §5 `s7`, §6, §7): GOTCHAS §83 and assemblies/07 (2024) say positions are shared. The
   confirming run starts with `s7`, which measures it (a free component turned in one configuration, a switch, a switch
   back), and also per-configuration values, stale handles and the fixed state on 2024. Right either way: the build,
   Update's per-mode puts (checked: every put is to the built frame, so with shared rotations a later mode's put sets
   the same turn, and a slider moved by a put in one mode is returned by its own value in the next), and a quiet
   Update's reads. Not right for both: what the app says about a turn and a switch — chosen by
   `POSITIONS_PER_CONFIGURATION_ON_2024` once `s7` sets it, neither claim made until then. And if 2024 refuses
   per-configuration values, modes are refused on 2024.
7. **A mate made while one configuration is shown came out suppressed in the template's configuration and on in the
   others** (§1.8 step 5, the fake, `NEW_MATE_IN_OTHER_CONFIGURATIONS`): recorded as the reason every flag is set
   explicitly, in place of assemblies/07's "inverse".
8. **What is still probed ahead** (§4, §7): showing an over-defined configuration (a user's edit can make one; the build
   and Update show configurations) and the copied-folder open (the scripts only). Everything else the spike ran raised
   no dialog; tier 9 shrinks to these two items, and §4.3 records the spike as run.

