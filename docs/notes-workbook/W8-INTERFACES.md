# W8 (sleeves and modes): the interface commit

Package I of `W8-PLAN.md` §3.2, with its ownership table §3.4. Packages A, B and C work in parallel from here, against
the fake, on disjoint files, reading this note and the code it names. **A change to a shape pinned here is a
stop-and-ask**; private helpers, and keyword-only parameters with defaults in your own module, are free. Authority:
`docs/PLAN-WORKBOOK.md`, then `W5-DECISIONS.md`, then `W8-PLAN.md` as revised (its *Changes after the spike* win over
*Changes after the review*), with W6 and W7 as built (`W6-INTERFACES.md` §7, `W7-INTERFACES.md` §6) beneath it.

## 1. Where it starts, and what moved since W8-PLAN §0.1 was read

- **Starting commit: `c22dc23`** (branch `workbook`): W7's packages and demonstration written (`a920abe`), its
  rulings marked (`931fe1a`), and A's two put-order pins (`7a34852`, `c22dc23`). The spike W8 rests on is
  `ca079ca` / `53e6f33` (`W8-SPIKE.md`, SolidWorks 2026 34.1.1).
- Suite on a clean `git archive` of `c22dc23` with this commit's files laid over it, Linux, the window tests
  included, under `timeout 600`: **2876 passed, 1 skipped**. Windows Tk tests: not run here (Linux only).
- **§0.1 re-read against `c22dc23`** (review S10). Holds as written: `schema.KINDS` lists `sleeve` and `dog`;
  `model.parse_slides`, `_read_modes`, `Mode`, `GearboxSpec.sliders`; `build.LATER` / `later_rows`;
  `Assessment.lay_out_refusal`; `geometry.LATER_KINDS`; `checks.MODE_KINDS` / `overall_ratio`; `export`'s
  "counted at its At only"; `kinematics.solve` knows no coupling; `findings.THIS_CONFIGURATION = 1`,
  `SUPPRESSION_ROUTE`; `Session.set_mate_suppressed` works in the active configuration only. **What moved:**
  1. `gears.kind_for` now returns the two workbook kinds (this commit: `WORKBOOK_KINDS`), whose bodies refuse with
     a sentence until B writes them. Safe meanwhile: every caller that checks a gear row skips `build.LATER` rows,
     and sleeves and dogs are still in `LATER`.
  2. **W5's `internal` is gone** (W6 replaced it with `senses`: gear mate name -> `k > 0`), and so is
     `GearboxPlan.ring_meshes`, and `swbuild._internal_meshes`. W8-PLAN §1.7 and §3.2's "`internal` keeps its
     meaning and is given the splines' and the couplings' names" reads, as built, as §6 item 2 below.
  3. W7's coaxial exemption in `checks._check_shafts` applies only to shafts on a **carrier's** axis
     (`if carriers:`), so TransferCase_Parallel's coaxial frame shafts (In, Lo, Rear, FrontDrv at the origin) still
     draw "passes over another shaft's axis" **warnings**. "Checks clean" is "no errors" (§2.2), so this blocks
     nothing; B decides whether a coaxial pair with no carrier is exempt too (§0.2 assumed it).
  4. Everything else §0.2 assumes of W7 holds at `c22dc23`: `kinematics.solve` through a carrier, a gear on the
     carrier's own shaft locked to the carrier, W7's motion plan over bodies, `MateEntry.on` / `plane`, schema 5.
- **W6 and W7 rulings carried unchanged** (none re-decided): W6 §7.1 (a parallel mesh's sense 0 is legal; a
  finisher writes the real ±1), **§7.2 `mate_senses[name] = (plan.sense == -1)`**, §7.4, §7.5, §7.11 (no
  `NotImplementedError` reaches a user), §7.18; W7 §6.1 (a record the app writes is never refused on its next read),
  §6.2 (the `gears` map covers carriers), §6.5 (`held ⊆ fixed`), §6.8 (`MatePlan.on` for AXIS only), §6.10, §6.13
  and §6.16 (put order, `placed` in the order put), §6.14, §6.15. Findings are read with `getattr`; a missing one is
  refused with a sentence before anything is made; no gate after a change.

## 2. Who edits what (W8-PLAN §3.4)

| Package | May edit |
|---|---|
| **P** — probes | `findings.py`, `probe/p9_modes.py`, `probe/decide.py`, `probe/__main__.py`, `tests/test_findings.py`, `tests/test_probe_modes.py`, `probe/results/**` |
| **A** — SolidWorks | `swcom.py`, `swbuild.py`, `tests/test_swbuild.py` (the fake), `tests/test_swcom.py`; may add to `tests/test_swbuild_train.py` and `tests/test_swbuild_modes.py` (I's: never change an assertion there) |
| **B** — planning | `workbook/*.py` but `link.py` and `xlsx.py`, `gears/__init__.py`, `gears/clutch.py`, `spec.py` (`default_stem` only), `tests/workbook_fixtures.py`, `tests/test_workbook_*.py` but `build` and `window`, `tests/test_gears_clutch.py` |
| **C** — record, words | `store.py`, `ui_text.py`, `tests/test_store.py`, `tests/test_ui_text.py` |
| **D** — window, boards, docs | `workbook_gui.py`, `preview.py`, `gui.py` if needed, `tests/test_workbook_{build,window}.py`, `tests/test_preview.py`, `design/**`, `docs/**`, `README.md` |
| **E** — demonstration | `probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, `probe/results/**` |
| nobody | `gears/*.py` but `__init__.py` and `clutch.py`, `workbook/link.py`, `workbook/xlsx.py` |

I wrote, beside the pinned code: `tests/test_swbuild_modes.py` (new), the first tests of `tests/test_workbook_modes.py`
and `tests/test_gears_clutch.py` (new, B's from now), schema 6's tests in `tests/test_store.py`; and moved a few lines
of other packages' tests mechanically: `tests/test_store.py` and `tests/test_workbook_window.py`'s `== 5` (the record's
schema number), `test_store.py`'s two lists of the mate kinds and a lock entry's written keys, and
`tests/test_workbook_motion.py`'s field-for-field mirror (a `MateEntry.values` dict compared as `MatePlan.values`'
pairs).

## 3. Pinned shapes: the worker's side (`swbuild.py`, `swcom.py`)

**Written in full with tests at I:** `ModesPlan.check`, `swbuild.on_in` / `links_in`, the `modes=` gate
(`_modes_gate`), `swcom.positions_per_configuration`, `Session._raise_epoch`. Everything else is a signature and a
docstring that refuses with a full sentence (`SolidWorksError` in swcom, `BuildError` before anything is made in
swbuild, `ValueError` in planning and `ui_text`), never `NotImplementedError`.

- **`ModeStep(name, ops=(), on=(), off=(), values={}, frames={})`** (frozen) and **`ModesPlan(steps, same_way=())`**
  as §3.2 gives them, `check(plan=None) -> List[str]`; **`ModeCheck(name, mates, suppressed, values, clashes,
  interference_error="")`**. `check`'s rules are its docstring; `tests/test_swbuild_modes.py` has one case each.
- **Results:** `GearboxResult.modes: List[ModeCheck]`; `GearboxUpdate.configuration`, `visited`,
  `unsuppressed_in`, `suppressed_in`, `slid`, `values_restored`, `put_in`, `extra_configurations`, `modes`; both
  results also carry **`positions_per_configuration: Optional[bool]`** (§6 item 7).
- **Links:** `MateRef.values` (pairs) / `modes`; `MeshLink.modes`, `LockLink.modes`; `MotionUpdate.configurations`,
  `mode_placements`, `recorded_by_mode`, `slide_values`, `on_sets`. Every one defaults to what a gearbox with no
  modes holds, so every W7 call and result is unchanged.
- **`on_in(modes, configuration)`** is the one home of "which mates are on in mode M": `()` is every
  configuration, names compare ignoring case. **`links_in(links, configuration)`** filters any links by it (a link
  with no `modes`, a `CarrierLink`, is always on); it is what `train_check` is given in a configuration.
- **`STAGE_MODE = "mode"`** (last in `STAGES`); `build(..., modes=None)` and `build_gearbox(..., modes=None)`,
  keyword. `_modes_gate` refuses, before anything is made (parts included, in `build_gearbox`): modes with no
  assembly; a plan `check(plan)` finds unsound, naming every problem; and, until A writes §1.8, any modes at all
  (*"This version of Gear Generator does not make an assembly's configurations yet, so a gearbox with modes is not
  built and nothing is made."*). A lifts that last raise in the same change that passes `modes` through
  `_build_in_job` to the assembly's `build`.
- **The `SolidWorks` protocol** gains the nine members §3.2 lists (it says "eight"; it lists nine):
  `configurations`, `active_configuration`, `add_configuration`, `show_configuration`, `delete_configuration`,
  `set_mate_suppressed_in`, `mate_suppression`, `set_dimension_in`, `dimension_values`. Each is in `swcom.Session`
  with §3.2's contract as its docstring, refusing until A writes it. **`swcom.ConfigurationGone(ComponentGone)`**.
- **`swcom.positions_per_configuration(revision) -> Optional[bool]`**: `findings.POSITIONS_PER_CONFIGURATION_ON_
  <release year>` by getattr — `_ON_2026` for major 34, `_ON_2024` for 32 — True or False when it is a bool, else
  None (missing, unsettled, 2025, no revision): **neither claim**. The one home of the switch; the worker reads it
  once per job onto the result.

### The handle rule: who fetches again, and when

- **Who:** `swcom.Session`, and nothing else. Only the Session holds an `IComponent2` or a mate `IFeature`; swbuild
  and planning hold ids (`gear3`) and names (`Name2` from insertion or `find_component`, a mate's tree name), never
  a COM object, so no plan, result or record changes for this rule, and swbuild never calls `find_component` again
  just because a configuration changed.
- **When:** lazily, at the first use after the **configuration epoch** was raised. `Session._epoch` (an int, 0 at
  connect) is raised by `_raise_epoch()` straight after `AddConfiguration2`, `ShowConfiguration2`, and an
  `open_document` / `activate` of an assembly — and after anything else that can change the active configuration.
  `DeleteConfiguration2` and a rebuild do not raise it. A kept component entry holds `{"component", "path", "name",
  "epoch"}`; **`Session._component(handle)`** (stub here, A writes it) returns the kept object when its epoch is
  current, else fetches it again by `name` (`findings.COMPONENT_FIND_ROUTE`), keeps it with the current epoch and
  returns it; nothing found is `ComponentGone` with W5's sentence. Every member that uses a kept component goes
  through it (today they read `self._handles[handle]["component"]` directly: A changes each). **`_kept_mate`**
  already walks the MateGroup by name on every call, so it never holds a mate across an epoch; it stays so.
  Selections after a change go by `SelectByID2("<feature>@<component>@<assembly>")` built from held names, never a
  fresh handle's `Name2` or `GetModelDoc2`.
- **The fake that makes a held handle loud** is the COM-level fake the Session runs against in
  `tests/test_swcom.py` (A): every object its `GetComponentByName` / `GetComponents` / MateGroup walk gives out is
  stamped with the document's epoch, `AddConfiguration2` / `ShowConfiguration2` / `OpenDoc6` raise it, and **any
  member call on an object of an older epoch raises `StaleHandle(AssertionError)`**, failing the test (SolidWorks
  answers `Transform2` None and `IsFixed` False silently). The protocol fake (`tests/test_swbuild.py`
  `FakeSolidWorks`) models what a configuration holds — per-configuration flags, values and frames, the active
  configuration — so a build that reads mode k's frames or `IsFixed` without showing k reads the active
  configuration's and fails its check; ids there are not epoch-bound, by the rule above.

### What a quiet Update reads and leaves unread (J25)

A quiet Update shows no configuration (`ShowConfiguration2` marks the assembly modified). **Read:** in the active
configuration, every frame, every recorded mate found, `mate_states()` codes, constrained statuses, `IsFixed`, and
`train_check` with `links_in(…, active)`; in every mode's configuration, every recorded mate's flag
(`mate_suppression`, `IsSuppressed2(3, …)`), every SLIDE's value (`dimension_values`, `GetSystemValue3(3, …)`), and
every gear mate's sense, suppressed couplings included. **Left unread:** every other mode's frames, error codes,
constrained statuses and `IsFixed`, so its `train_check` and its interference — a train turned or put out of step in
a mode that is not active is seen only when Update works in that mode or a changed Update visits it. No sentence
claims more (*"It worked in 4H, the configuration that was active; it did not show the other modes, since nothing
needed changing."*).

## 4. Pinned shapes: planning (`workbook/`, `gears/`, `spec.py`)

- **`motion.SLIDE, SPLINE, COUPLE = "slide", "spline", "couple"`**, appended to `MATE_KINDS` (W5's four first; the
  store's `_MATE_GEARS` keeps the same order, a test pins it). **`mate_name`** written: SLIDE `(slider,)` with its
  shaft → `"RangeSlv along Rear"`; SPLINE `(anchor, slider)` → `"ModeSlv splined to RangeSlv"`; COUPLE
  `(sleeve, dog)` → `"RangeSlv engages InDog"`; wrong gear count or shaft is a ValueError sentence.
- **`MatePlan.values: Tuple[Tuple[str, float], ...]`** (a SLIDE's **signed** z_front per mode, mode order; its
  `z_front` the first mode's, `plane` "front", `face_global` "") and **`MatePlan.modes`** (a per-mode mate's
  on-set, mode order; `()` = every mode). `mate_entry` writes them as `MateEntry.values` (dict) and `modes` (list);
  `mate_ref` gives them back as `MateRef.values` pairs (in the entry's order — read them as a dict; a re-read file
  holds them sorted) and `modes`. A SPLINE or COUPLE has `ratio (1, 1)`.
- **`MotionPlan.modes`** (the configurations, Modes-sheet order) and **`drag_by_mode`**; `drag` stays the first
  mode's. **`motion.modes_plan(motion, handle_of, frames_by_mode) -> Optional[ModesPlan]`** stub (ValueError
  sentence); **`motion.modes_reason() -> str`** stub that *returns* a refusal sentence for every gearbox with modes
  until B writes it (W8-PLAN §1.9: `""` when settled).
- **`checks.ModeReport`** as §3.2 (with defaults after `name`), **`Report.modes: Tuple[ModeReport, ...] = ()`**.
- **`GearboxPlan.modes_plan: Optional[ModesPlan] = None`**; `build_kwargs()` adds `"modes"` only when it is set.
- **`gears/clutch.py`**: `SleeveKind` (delegate `InternalSpurGear`) and `DogKind` (delegate `SpurGear`), recipes
  taken from the delegate, every body refusing with *"A sleeve is not built by this version of Gear Generator yet,
  so its part cannot be worked out."*; `gears.WORKBOOK_KINDS`, found first by `kind_for`; never in `KINDS`, so
  `gui.KIND_VALUES` is unchanged. **`spec.default_stem`**: `Sleeve_m1.5_N30`, `Dog_m1.5_N30` (`spec.CLUTCH_WORDS`).

## 5. The record: schema 6 (`store.py`)

`LINK_SCHEMA_VERSION = _W7_LINK_SCHEMA + 1` (W7 left 5, so 6). A v1–v5 record reads as v6 with no modes; a newer one
is refused (`UnknownSchema`) and left byte-identical. New fields, every one defaulted:

- `MateEntry.values: Dict[str, float]` (configuration → signed z_front, mm) and `MateEntry.modes: List[str]`;
- `GearboxRecord.modes: List[str]` (as built, Modes-sheet order; the first is the one saved);
- `ComponentEntry.frames: Dict[str, Dict[str, List[float]]]` — **JSON shape `{"2H": {"rotation": [9 by rows],
  "at": [3 mm]}}`** (`store.FRAME_KEYS`); `{}` = the one frame; `rotation` / `at` stay the frame of the
  configuration the assembly was saved in.
- `_MATE_GEARS` gains `slide: 1, spline: 2, couple: 2`, since a finish writes those kinds.
- Written at I (`_w8_read`): the shapes are type-checked and every number made a float, so a round trip is
  byte-deterministic. **C's** (W8-PLAN §1.11): a SLIDE's `values` naming every `GearboxRecord.modes`, no 0, one
  sign; a couple's or spline's ratio `[1, 1]`; `modes` within `GearboxRecord.modes` — each written so a record
  the app writes (and a continued build's) still reads.

Tests at I: v3, v4 and v5 records → read → write → read, equal, and v5 equal to what was written; a W8 record round
trips byte for byte, whole numbers read as floats, a continued build's two records read clean, each new shape
refusal, schema 7 refused untouched.

## 6. Readings where two were possible

1. **The handle rule's fake** is the COM-level one (§3): W8-PLAN §3.2 makes the Session the only holder of handles
   and plans' ids untouched by the rule, so a held handle can only be caught under the Session; §3.5 names "the
   fake" in `tests/test_swbuild.py`. If the coordinator wants swbuild to re-find ids after each change instead, that
   is a change to this note, before A starts.
2. **`internal` → `senses`, one home per gear mate:** the base plan's gear mates (meshes and **splines**) take their
   sense from `build`'s `senses` (B widens `gearbox.mate_senses` to SPLINE: `(sense == -1)` unchanged; `_sense_gate`
   refuses a gear mate missing from it); the steps' gear mates (couplings, sliding meshes) take theirs from
   `ModesPlan.same_way` (listed ⇔ same way), never from `senses`. A reads `kind in ("mesh", "spline", "couple")`
   wherever W6 reads `"mesh"` for a gear mate's sense or remake.
3. `ModesPlan.check` takes an optional `plan` (§3.2 wrote `check(self)`); "each LinkDimension after its mate" is
   read, after the spike (no slide global), as "a step holds gear mates only".
4. **`ModeStep.values` are magnitudes** (§3.2: `|z_front|`), checked `> SLIDE_TOLERANCE` (1e-9 mm,
   `layout.BASE_TOLERANCE`); the one-sign rule (J27) is checked where the sign is known: B's planning on
   `MatePlan.values` (signed) and C's parse of `MateEntry.values` (signed). Identity:
   `step.values[name] == abs(dict(slide.values)[step.name])`.
5. `on_in` compares names ignoring case (J6 makes that unambiguous, and a mode may use a template configuration of
   another case).
6. The protocol gets nine members, not eight (§3.2 lists nine).
7. **The positions switch** is `swcom.positions_per_configuration`, carried on both results; the record has no field
   for it (it describes the running SolidWorks, not the build). `ui_text.turning_note(positions_per_configuration)`
   is written now (§1.12's two sentences exactly, `""` for None), the one home of the wording switch.
8. `modes_reason()` returns its refusal sentence (it is a sentence-giving function, like `motion_reason`) instead of
   raising; `modes_plan` raises a ValueError sentence.
9. `LockLink.modes` exists for the rule's sake: a spline is always on, so it holds `()`.
10. The dataclasses §3.2 pins without defaults are given defaults after their first field (additive only).

## 7. Identities and worked examples (TransferCase_Parallel and E4, W8-PLAN §2.3)

| What | Identity | Worked example |
|---|---|---|
| a SLIDE's value per configuration | `MateEntry.values == dict(MatePlan.values)`; `ModeStep(m).values[slide] == abs(MatePlan.values[m])`; `MatePlan.z_front` = the first mode's | `RangeSlv along Rear` 2H 46, 4H 46, N 56, 4L 66; `ModeSlv along Rear` 96, 106, 96, 106 |
| a coupling's on-set | `MatePlan.modes == tuple(MateEntry.modes) == MateRef.modes`; `on_in(modes, m)` | `RangeSlv engages InDog` (2H, 4H); `RangeSlv engages LoDog` (4L,); `ModeSlv engages FrontDog` (4H, 4L) |
| where a per-mode mate is made | in the first step whose `on` holds it (`check`) | 2H makes InDog's, 4H FrontDog's, N none, 4L LoDog's |
| a step's `on` / `off` | `on` = every base-plan mate + the per-mode mates on there; `off` = the per-mode mates off there; `on ∪ off` the same in every step | N: `off` = all three couplings |
| a coupling's sense | `MatePlan.sense = −1` (same way, `k = σ_S·σ_D = +1` on one axis) ⇒ `mate_senses` / `same_way` True | all three couplings and the spline: True |
| speeds per mode (input In +1500 rpm, own axes) | `ModeReport.motion.speeds`; a free member absent | Rear 1500 / 1500 / free / 375; Front free / 1500 / free / 375 (2H / 4H / N / 4L) |
| the configuration it opens in | `GearboxRecord.modes[0] == ModesPlan.steps[0].name` | `2H` |

## 8. Open points (what each package writes against this)

**A.** The nine members and `_component` (copying tier 9's raw calls), the epoch raised where §3 says, every member
through `_component`; `build`'s mode phase (W8-PLAN §1.8, steps 1–8, in that order), its log lines and *"In mode
4L, …"* problems; interference per mode; Update's per-configuration reads, D10 per configuration, per-mode puts and
post-check (§1.10); `couple` / `spline` gear mates read and remade as `mesh` ones; the COM-level stale fake and the
protocol fake's configurations (§3.5), every Update test both with `shared_positions` False and True.
**B.** `SleeveKind` / `DogKind` bodies; §1.1–§1.7; `MatePlan.values` / `modes`, `MotionPlan.modes` /
`drag_by_mode`, `modes_plan`, `modes_reason`, `mate_senses` over splines; `update._bad_mates` and `classify` over the
three kinds (`_bad_mates` today counts gears as 1 only for axis and along); `finish_build` / `finish_update` writing
`GearboxRecord.modes`, every SLIDE's `values`, every mate's `modes`, every component's `frames`; both fixtures.
**C.** Schema 6's refusals (§5), every §1.12 sentence into the stubs (`modes_ready_line`, `modes_done_line`,
`mode_problem`, `modes_record_line`, `mode_update_lines`, `mode_speed_lines`), `turning_note` wherever a sentence
says where a turn shows. **D.** After A–C.

## 9. Rulings on the interface review (2026-11-14)

The independent review of `e9efab9` checked both fixtures by hand (the sliders' spans and covers, the eight slide
values, what is engaged in each of 2H, 4H, N and 4L, the speeds) and found the shapes right. It found two faults of
the kind the last two interface reviews found, and asked for written rules. These bind A, B, C and E from now.

1. **A mate that belongs to modes is never on in none of them.** `MateEntry.modes == []` means "on in every
   configuration". An edit after which a coupling or a sliding mesh would be on in no mode is therefore structural
   (Build again…), never an Update: otherwise `finish_update` would write `[]` for it, and the next Update's rule
   that a recorded mate found suppressed is turned back on would switch it on in every mode — in 2H both dogs
   engaged, the train jammed in SolidWorks. B's classify owns the rule and tests it.
2. **`update_gearbox` has a modes gate, before anything is read.** It refuses with a sentence when any of these is
   non-empty: `motion.configurations`, `slide_values`, `on_sets`, any `MateRef.modes`, `MeshLink.modes` or
   `LockLink.modes`, or a `MateRef` of kind slide, spline or couple. Without it a W8 record goes down W7's motion
   path, which reads only the active configuration and turns on every recorded mate it finds suppressed. A lifts
   this refusal in the same change that writes the Update across configurations (W8-PLAN §1.10), and lifts the
   build gate no earlier.
3. **A coupling's sense follows the two shafts' facing; it is not always "the same way".** About each gear's own
   axis `k = σ_S·σ_D`. So: COUPLE `sense = −σ_S·σ_D`; SPLINE `sense = −1`; and `same_way ∋ name ⇔ plan.sense == −1`,
   the identity of W6 §7.2. The spike's case pins it: parallel shafts, the first Flip read right, both entities
   along +Z. Until a coupling between shafts facing opposite ways has been shown on SolidWorks, planning refuses it
   with a sentence. For Update, a SPLINE (a `LockLink`, which has no k) is read with `same_sense` True from its
   kind, and a COUPLE is a `MeshLink` with `k = σ_S·σ_D`.
4. **No code outside `swcom.py` touches `Session._handles`.** A held component object answers `IsFixed` False and
   `Transform2` None silently after any `AddConfiguration2` or `ShowConfiguration2`. A adds a public
   `Session.is_fixed(handle)` that goes through `_component`, calls `_raise_epoch` from `open_document` and
   `activate` too, and adds a test that scans `src/` and `probe/` for `_handles[` and fails on any use outside
   `swcom.py`; E moves `probe/workbook_assembly_check.py`'s direct read (about line 4559) to the public member.
   Every `Session` member that touches a component has a test run after an add and after a show. The handle rule
   itself stands as the interface commit has it (§3): only the `Session` holds COM handles and re-fetches them at
   first use after the epoch is raised, and the COM-level fake's `StaleHandle` is what catches a held one; the
   protocol fake goes on modelling per-configuration state.
5. **The per-version refusal is the worker's.** `_modes_gate` reads the per-version findings from the running
   SolidWorks' revision before anything is made, as `_sense_gate` does. `modes_reason()` runs at planning, cannot
   know which SolidWorks will run, and covers only findings that do not depend on the version.
6. **Mode names are compared in one way everywhere:** through `on_in`'s casefold — against SolidWorks'
   configuration names, in C's check that a mate's `modes` are among `GearboxRecord.modes`, and in B's classify.
   `GearboxRecord.modes` keeps the workbook's spelling.
7. **`ModesPlan.check(plan)` also refuses** a step op whose `a` or `b` is not a component of the plan, and a
   coupling missing from `same_way` where the planned axes (the third column of each component's `Place`) say it
   belongs there.
8. **Sliders with no Modes rows:** `MatePlan.values == ()` and `MateEntry.values == {}`, which C allows when
   `GearboxRecord.modes` is `[]`.
9. **Modes reordered is an Update with nothing to do.** `GearboxRecord.modes` is never reordered by an Update;
   its first entry stays the configuration the assembly was saved in.
10. **`MotionPlan.modes` is non-empty exactly when `modes_plan` is set** (B's invariant, tested), so `build_kwargs`
    can never drop `"modes"` and build a gearbox without its configurations.
11. **Every quiet Update of a gearbox with modes says which mode it worked in and that it did not show the others.**
    Flags and senses are read in every mode without showing it; another mode's frames, error codes and constrained
    statuses are not, so a turn or a put out of step there goes unseen until that mode is shown. The sentence is
    said always, not only "when it matters".
12. **What the record cannot say, the caller passes.** `ui_text.modes_record_line(record, *,
    positions_per_configuration=None, modes=())` and the same keyword on `workbook_footer`. The window passes the last
    job result's `positions_per_configuration`, which is None after a restart, and then neither claim about a turn
    staying in its mode is made. `modes` is the workbook's current Modes order (the footer takes it from
    `assessment.spec.modes`), used for the sentence about reordered rows.
13. **Three things C words are pinned by their owners, not worked out in `ui_text`:** which outputs share a torque
    and with whom, and which members are past a split (B, on the kinematics result); each mode's overall ratio and
    what makes a mode "front not driven" or "neutral" (B, one home shared with the checks); and what an Update found
    out of step in each mode it showed (A, on `ModeCheck`). C says nothing about a mode an Update did not show
    beyond ruling 11's sentence.
14. **What an Update says about each mode it showed.** `ModeCheck` gains `out_of_step: List[Tuple[str, str]]`,
    `off_axis: List[str]` and `turned: bool`. `GearboxUpdate.modes` holds a `ModeCheck` only for each mode the Update
    showed: empty lists for a mode shown and found right, no entry for a mode it did not show. `GearboxUpdate.
    configuration` is always set for a gearbox with modes. The build gate came off with the modes build (`f9a8cae`)
    ahead of the Update across configurations; until that is written, the Update gate of ruling 2 is what keeps a
    built gearbox with modes off W7's motion path.
15. **SolidWorks 2024 behaves as 2026 on what W8 rests on** (`W8-SPIKE.md`, the SolidWorks 2024 section): a slide's
    value held per configuration, positions kept per configuration, a put holding in the active configuration only,
    handles stale after an add or a show, `SetSuppression2` after `AddConfiguration2`. So modes are built on both, and
    the claims about a turn staying in its mode are made on both. One difference was measured: a collinear spline's
    gear mate needed Flip True on 2024 and False on 2026, and the read-back named the right one each time. No Flip is
    assumed for a spline or a coupling, as for every other gear mate.
16. **A gear mate's sense in a mode that has it off** (package A's review, 2026-11-15). While
    `findings.SUPPRESSED_GEAR_MATE_SENSE_READ` is not set to "answers, marks nothing", the check phase does not read
    the sense of a coupling, spline or sliding mesh that is suppressed in the configuration shown: an unmeasured read
    could mark a saved assembly modified in a quiet Update. So (a) each mode an Update shows reads, in its post-check
    through fresh handles, the sense of every gear mate on in it; a wrong one is a failure naming the mate and the
    mode, never a raise and never a remake. (b) Every recorded gear mate no read reached is listed in the additive
    `GearboxUpdate.senses_unread: List[str]` (the record's spelling and order; empty when all were read), with one
    line under the result; package C words it from that field. (c) With the finding set, the check phase reads them
    all and `senses_unread` is empty. Making a gear mate of a gearbox with modes again (a new ratio, a sense found
    wrong, a mate the workbook now turns the other way) stays refused in the check phase, before anything changes,
    with a sentence that says to build the gearbox again: a default the user may overrule, listed in the handoff.
17. **A whole-box jam with modes** (package B's review). With Modes rows, "the box cannot turn at all" is said only
    when every mode jams; a mode that jams is an error at its own Modes row naming what engages what, and reads the
    same wherever that row stands. One home: `checks._check_motion`.
18. **A turn of a mated train can show in other modes; a put on a quiet Update obliges the visit** (W8's s2 and the
    check after it, SolidWorks 2026 34.0.0 on this host, 2026-11-15; `eff7bad`, `933de81`, `d3c2e97`).
    - *What s2 and s7 measured, and what is not settled* (corrected after `W8-REVIEW-DEMO-S2-S7.md` M1).
      - A turn given in one configuration has been read in others. On copies no Update had moved, in all four: the
        drive's +37° on the Sun in 2H stood in 4H, N and 4L, LoDog in interference with RangeSlv in 4L (531.913 mm³)
        (`probe/results/w8-workbook-assembly-20261115-111951-s2-turn-carried-per-body.log`, and the check after it,
        `probe/results/w8-turn-across-configurations-20261115-115500.txt`), and s7's cases 1-3
        (`probe/results/w8-s7-20261115-135428.json`): as built, after no-op puts by the app's route, for a turn
        given in 4L, and after a save and reopen for one given in N. After an Update had put every mode, in 4L:
        `probe/results/w8-workbook-assembly-20261115-151412-s2.log` line 356.
      - Not settled. In that same state the fresh turn was not read in 4H and N: shown after a put in 2H, both read
        at the built turn, in step and not turned (the same log, lines 448-451). So whether a turn reaches every
        configuration once an Update has put every mode is open, and so is whether a put that moves a body can
        reach another configuration: s2 twice found 2H's put in 4H and N and not in 4L (lines 448-451, and the
        changed Update's FDrive, lines 569-572 and 709; the same in the 111951 log, lines 297-300), where s7's
        case 5, the s2 rerun's puts in 4L and 4H (`…-132348-s2-put-kept-per-configuration.log`) and the spike's
        follow-up (`e670e7e`) read each moving put kept in the configuration showing alone.
        s7's case 4 in the 135428 run does not decide it: its Update moved only the front train, so the turn "after
        the app's own Update" rests on no-op puts of the driven train (review S2). s7's case 8 (a turn, an Update
        that puts every mode, a turn, a moving put, every configuration read after each) is to measure it on 2026;
        it has not run there. This stays not settled for 2026.
      - *On 2024* (SolidWorks 2024 32.5.0, s7: `probe/results/sw2024/w8-s7-20261115-162418.json` and its log
        `…/sw2024/w8-workbook-assembly-20261115-162357-s7.log`; case 8 rerun:
        `…/sw2024/w8-s7-20261115-172104-case8.json` and `…-172046-s7-case8.log`, 0 failed), read on that version
        alone:
        - every turn of the train read in all four configurations by the same amount: on copies no Update had
          moved (cases 1-3), after the app's changed Update had put the turned train back (case 4), and after its
          quiet Update had put every mode (case 8). So `TURN_PER_CONFIGURATION_ON_2024` is False (`ce775a6`);
        - case 8 read neither of the two 2026 possibilities above: the fresh turn reached all four, and the moving
          put in 2H after it stayed in 2H;
        - case 5's moving puts each stayed in their configuration (log 831-859, 909). Then FrontDog driven +15° in
          N left FIdler, which stood at 0, +10, +20 and 0 in 2H, 4H, N and 4L, at −2.5° in all four (log
          863-884, `same_amount_or_place`): a body driven in one configuration left its meshed neighbour at the same
          place in every configuration, not moved by the same amount, and 4H's earlier moving put was gone. So a
          moving put is kept by its configuration only until that train is next turned in any configuration.
          2026's s7 has not given that drive.
      - Behaviour depends on none of this, since every mode an Update shows is put to its built frames and
        post-checked. Not measured: a turn given while the configurations already stand differently on 2026, a drag
        in the user interface, and 34.1.1.
    - *The split.* `findings.TURN_PER_CONFIGURATION_ON_<year>` (2026 False; 2024 False since its s7, `ce775a6`; a
      version with no finding of its own None, neither claim) is what the sentences about a turn and a switch read,
      through `swcom.positions_per_configuration`, which keeps its name and its three states.
      `POSITIONS_PER_CONFIGURATION_ON_<year>` stays as the put fact it was measured as and is read by nothing. No
      behaviour reads either: Update's per-mode puts are right either way (W8-PLAN §1.9). The pins on s7's file
      (`4b164a7`) are of what s7 read, not rules; the s2 lines above are pinned beside them
      (`test_s2_after_an_update_had_put_every_mode_the_turn_was_read_in_4l_and_not_in_4h_or_n`), and 2024's s7 readings
      beside those (`test_s7_on_2024_…`).
    - *A put on a quiet Update obliges the visit* (J13, W8-PLAN §1.10's post-check, "all of them when anything
      changed"). An Update with nothing changed in the workbook that finds the active mode out of step and puts it
      has changed something: every other mode is then shown and handled as a changed Update handles it (put only
      where its own train needs it, J26 unchanged; post-checked; its `ModeCheck` on `result.modes`), the active
      mode last and left active, its own `ModeCheck` last, then every per-mode flag read in every configuration.
      This holds whichever way positions are kept. A quiet Update that puts nothing stays as it was: nothing shown,
      nothing marked. The test that had pinned the opposite, the shared-positions variant of
      `test_a_train_turned_in_another_mode_is_left_unseen_by_a_quiet_update_which_says_so` ("put back in 2H alone,
      nothing shown"), now pins the visit, renamed `test_a_turn_in_another_mode_is_unseen_by_a_quiet_update_or_if_shared_put_back_with_every_mode_visited`.
      *Amended after s2's rerun* (`probe/results/w8-workbook-assembly-20261115-132348-s2-put-kept-per-configuration.log`,
      `a87c1c5`): there the 4L put stayed in 4L, so 2H and N, turned in step and not put, failed their post-check
      against the built frames. So a quiet Update that has anything to put is a changed Update from there (W5's
      answer 2): the active mode is judged without a put, then every mode is shown and every train put whole to its
      built frames, the active mode last, then the flags read. No mode is left turned after an Update that put
      anything. On E4 that is 52 puts, what a changed Update costs.
      *And* (`baa1a56`): in every mode an Update shows, a train found turned in step is put whole to its built
      frames, as one found out of step is; J26's "put where that mode needs it" includes "turned". So a changed
      Update whose only changes are flags or slide values (D10, a slide's place set back), which before left a
      mode found turned in step as it stood and failed its post-check against the built frames, ends every mode it
      shows at its built frames whatever SolidWorks kept there (W5's answer 2: an Update that changes the assembly
      returns a turned train to its built turn). Such an Update of a gearbox nobody turned still puts nothing. A
      quiet Update that changes nothing leaves a turn in step in the mode showing where it stands and says so.
    - *Three sentences say only what was read*, verbatim:
      - a quiet Update: *"It worked in 4H, the configuration that was active; it did not show the other modes,
        since nothing in 4H needed changing."* (before: *"…since nothing needed changing."*; with no
        configuration named, *"…since nothing there needed changing."*, after the review of these commits, point
        8), whatever the switch says;
      - the switch False: *"A turn you give the gears in one mode can show in other modes, so a dog can stand
        across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode
        showing."* (before: *"A turn you give the gears in one mode shows in every mode, so a dog can stand across
        its sleeve in another mode; …"*, said only what every reading supports after `W8-REVIEW-DEMO-S2-S7.md`
        ruling 1);
      - the switch False, after a put in the mode worked in and the visit: *"The gears of 2H and N stood at the
        turn they were built at when Update SolidWorks showed them."*, naming only the visited modes whose own
        judgement on showing read them so (not put there, in step, on their axes, not turned).
    - *For the user's list:* the app's sentences about a turn on SolidWorks 2026 and 2024 claim only that it can show
      in other modes. On 2026, before any Update has moved the train that has been read in every mode; after an
      Update has put every mode, the app found 4L turned and 4H and N, shown after its put in 2H, at the built turn
      (above), and s7's case 8 is to settle it there. On 2024 it has been read in every mode in every state s7 tried.
    - *Not taken, for the user to overrule:* with a turn shared between modes, a quiet Update could judge every
      mode's couplings from the rotations it reads in the active mode, without showing anything, and say which mode
      stands with a dog across its sleeve. Today a quiet Update judges the mode showing alone (J25).
    - *What is on screen when* (corrected after the review of these commits, `W8-REVIEW-9-18.md` point 1). The
      record line's turning note (the switch-False sentence above) is in the footer when no job's note is showing:
      after a read, or once a job's note gives way, when the workbook next changes. Right after a press the footer
      shows the job's status alone. So when the switch is False and an Update found the gears turned in the mode
      showing, put nothing and showed no other mode, its status itself adds, straight after *"The gears stand where
      they were turned in SolidWorks."*: *"This version of SolidWorks can show that turn in other modes, so a dog may
      stand across its sleeve in another; to put the gears back there, press Update SolidWorks with that mode
      showing."* Nothing is added when the switch is True or None, or after a put, which shows and checks every
      mode.
