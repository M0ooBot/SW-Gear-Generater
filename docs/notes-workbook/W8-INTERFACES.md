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
