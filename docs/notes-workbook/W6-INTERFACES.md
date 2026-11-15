# W6 (right-angle): the interface commit

Package I of `W6-PLAN.md` §4.1. Packages A, B and C work in parallel from here, against the fake, on disjoint files,
reading this note and the code it names. **A change to a shape pinned here is a stop-and-ask**; private helpers, and
keyword-only parameters with defaults in your own module, are free. Authority: `docs/PLAN-WORKBOOK.md`, then
`W6-PLAN.md` as revised (`eb195d0`, its *Changes after the review*), with W5's decisions in force.

## 1. Where it starts

- **Starting commit: `ed3a3b4`** (branch `workbook`): the revised plan `eb195d0`, with the small-pinion merge
  `0f5a121` and the working-centre checks `d3f4dcf`/`9efde87` under it, and probe tier 9 (package P, `8f529f6`)
  committed alongside; its findings (`TURNED_GEAR_MATE_SENSE_READ_BACK`, `TURNED_GEAR_MATE_SENSE_ANGLES`) are not.
- Suite on a clean `git archive`, Linux: baseline at `8a798fe` **2279 passed, 1 skipped**; at the interface commit,
  **2413 passed, 1 skipped**. Windows Tk tests: 116 passed, 1 skipped.

## 2. Who edits what (W6-PLAN §4.2)

| Package | May edit |
|---|---|
| **P** — probe tier 9 | `src/gear_generator/probe/p9_turned.py` and its registry entry, `probe/decide.py`, `findings.py`, `tests/test_findings.py`, `tests/test_probe_turned.py`, `probe/results/**` |
| **A** — SolidWorks | `swcom.py`, `swbuild.py`, `tests/test_swbuild.py` (the fake), `tests/test_swcom.py`; add only to `tests/test_swbuild_train.py` and `tests/test_swcom_sense.py` (I's: never change an assertion there) |
| **B** — planning | `workbook/{geometry,kinematics,checks,fixes,layout,motion,gearbox,update,build,model,schema,export,assess}.py`, `tests/test_workbook_{geometry,checks,layout,motion,gearbox,update,model,export,demo_fixtures}.py`, new `tests/test_workbook_turned.py`, new `tests/test_workbook_parts.py`; add only to `tests/test_workbook_axes.py` (I's) |
| **C** — record and words | `store.py`, `ui_text.py`, `tests/test_store.py`, `tests/test_ui_text.py` |
| **D** — window, boards, docs (after A–C) | `workbook_gui.py`, `preview.py`, `tests/test_workbook_{build,window}.py`, `tests/test_preview.py`, `design/**`, `docs/**`, `README.md` |
| **E** — demonstration (after D and P's review) | `probe/workbook_assembly_check.py` (from this commit on), `probe/workbook_window_check.py`, `probe/results/**` |
| nobody | `gears/*.py` but `base.py` (I only), `gui.py` |

I touched outside its own files, mechanically: `probe/workbook_assembly_check.py`'s `ring_mate_reading` (section m8:
the new `gear_mate_sense` arguments, axes from the record's frames); `tests/test_swcom.py`'s six sense-read tests
(the new form); `tests/test_workbook_motion.py` (`mesh_links`' new third argument; `made_up`'s `Placed` gains
`axis` and `centre`); `tests/test_store.py` and `tests/test_workbook_window.py` (schema 4's numbers). The turning
round trip on the fake for fixtures A and B is **B's second pass** once A lands, as in W5.

## 3. Pinned shapes (W6-PLAN §4.3), by module

**Written in full with tests at I** (A and B both rest on them): `geometry.axis_vector`, `family`, `base_frame`,
`Placed.origin`; `layout.frame` on `base_frame`; `motion.face_global`, `mesh_links`; `swcom.sense_reading`;
`gears.base.LineAxis` and its `check()`; schema 4's reading. Everything else is a signature and a docstring.

### `gears/base.py`

- `LineAxis(id, name, point: Point3, direction: Point3, length: float = 100.0)`, property `sketch` (`"S3 Axis"` →
  `"S3 Line"`). In `OPS`, `GEOMETRY` and `Op`; `check()` defines `id` and refuses a direction not of unit length to
  1e-9, a length not above 0, a name not ending `" Axis"`, one made while a sketch is open; `describe` logs it.
  `swbuild._RUNNERS[LineAxis]` calls `sw.line_axis(op.id, op.name, op.point, op.direction, op.length)`.

### `workbook/geometry.py`

- `Vec3`; `DIRECTIONS` (the six words); `CARDINAL_SNAP = 1e-12`; `FAMILY_TOLERANCE = 1e-9`.
- `axis_vector(text) -> Vec3`: the six words exactly, **blank is Z+**, else `"dx, dy, dz"` (commas, spaces or
  semicolons; U+2212 is minus) normalised; within 1e-12 per component of a cardinal → that axis exactly. ValueError
  sentence otherwise.
- `family(direction) -> (plus, ±1)`: plus is the one whose first component of magnitude > 1e-12 is positive (the
  word's `+` for cardinals). No `-0.0`.
- `base_frame(direction) -> 9 by rows`, columns `[u₀ | a×u₀ | a]`, `u₀` = +X projected (or +Y when `|a×X| < 1e-9`);
  `Z+` is `I`, `Z-` is `diag(1,−1,−1)` exactly; no `-0.0`.
- `Placed += axis: Vec3 = (0,0,1); centre: Vec3 = (0,0,0); family: Vec3 = (0,0,1); bevel: bool = False`, property
  `origin` (`centre − axis·face/2`, a bevel's `centre`). **Every constructor gives `axis` and `centre`**:
  `geometry._place` does for the Z family now (`(0,0,σ)`, `(x,y,z)`), so `origin == (x, y, z_front)` exactly.
- `PARALLEL, BEVEL, CROSSED`; `MeshGeometry(a, b, kind, sense, shaft_angle, needed, placed, contact, psi_a, psi_b,
  problem="")`; `BevelCut(mate_teeth, shaft_angle, partners, problem="")`; stubs `mesh_geometry(a, b)`,
  `bevel_cuts(spec)`, `cylinder_gap(a, b)` (B).

### `workbook/kinematics.py`, `checks.py`

- `solve(spec, skip_gears=(), senses: Optional[Mapping[Tuple[str, str], int]] = None)`: None is W3 exactly;
  given, a stub until B's own-axis rewrite. `Motion.seen_from: Dict[str, str]` (empty until B).
- `Report.meshes: Dict[Tuple[str, str], MeshGeometry]` (empty until B).

### `workbook/layout.py`

- `ShaftLayout += direction: Vec3 = (0,0,1); z_side = ""; z_global = ""; z_plane = ""; line = ""; axis = ""`;
  `direction` is coerced to a tuple of floats (so a layout read back from the record's list is equal);
  `shaft_layouts` fills `direction` and `axis` for Z± now. `sigma` is 0 off the Z family.
- `frame(placed, theta) -> Frame`: `base_frame(placed.axis) · rot_z(θ)`, no `-0.0`, at `placed.origin`.
  `tests/test_workbook_axes.py` holds it to W4's formula bit for bit on every gear of the three committed Windows
  fixtures, at five turns each. `_rotation` (W4's formula) stays only because probe tier 8's test reads it.

### `workbook/motion.py`

- `MatePlan += plane: str = "front"; sense: int = 0` (after `z_front`); `mate_entry` copies both.
- `FRONT_PLANE, TOP_PLANE, RIGHT_PLANE`, `PLANES`, `PLANE_COORDINATE`.
- `face_global(gear, plane="front", bevel=False)`: `"G4 Face Z"`, `"G1 Face X"` (Right), `"G2 Face Y"` (Top),
  `"G2 Apex Z"` / `"G4 Apex Y"` for a bevel. ValueError for no gear or another plane.
- `mesh_links(meshes, teeth, sense: Mapping[(a, b), int])`: `MeshLink(a, b, −c·za/zb, 360/zb)`, keyed by the
  Meshes row's ordered pair; a missing pair, a sense not ±1 or teeth ≤ 0 is a ValueError sentence.
- Bridge, not pinned: `parallel_sense(a, b, sigma, internal)` gives W5's parallel `c`, used by `update.classify`'s
  W5 call of `mesh_links` and by two W5 tests; B replaces its uses with `Report.meshes` and `MateEntry.sense`.
- Stub: `turned_refusal(report) -> str` (B).

### `workbook/gearbox.py`, `update.py`

- `GearboxPlan.mate_senses: Mapping[str, bool] = {}` (gear mate name → `k > 0`). `ring_meshes` and `build_kwargs`'
  `"internal"` stay until B moves `build_kwargs` to `"senses"` (with A dropping `internal`).
- `UpdatePlan.resensed: Tuple[str, ...] = ()`.

### `swcom.py`

- `Vec3`; `TURNED_SENSE_ROUTES = ("entity senses",)`; `ENTITY_ALONG = 0.99`.
- `sense_reading(reverse, directions, axes, same_sense, *, mate: str = "") -> (right, (τa, τb))` — rule H, entities
  matched to gears by alignment in either order, pure (no finding read). Refusals are sentences (not a bool
  Reverse; not two directions; a direction or axis with no length; entities not one along each gear). `mate` names
  the mate in them. `tests/test_swcom_sense.py`: equal to W5's rule on every case of
  `GEAR_MATE_FLIP_NEEDED_ON_2026/2024` and `GEAR_MATE_FLIP_NEEDED_MORE_ON_2026/2024` (the plain annulus on every
  facing), every Reverse, every entity sense and both entity orders; on parallel axes in any family; H on 30–150°.
- `Session.gear_mate_sense(handle, same_sense: bool, axes: Tuple[Vec3, Vec3]) -> (right, (τa, τb))`: written for
  **parallel** axes (W5's gate, then `sense_reading`); on non-parallel axes a stub for A (the turned gate).
- Stubs: `Session.line_axis(handle, name, point, direction, length) -> str`, `Session.axis_line(handle, name) ->
  (point, direction)`.

### `swbuild.py`

- Protocol: `gear_mate_sense` in the new form, `line_axis`, `axis_line`.
- `build(sw, plan, exists, kind=None, *, gears=None, senses=None, internal=None)` and `build_gearbox(…, senses=None,
  internal=None)`. `senses` is the pinned form. **Bridge until A**: given `senses`, parallel gear mates become W5's
  `internal` (`_internal_from_senses`: inside a ring exactly when the same sense agrees with the planned axes
  pointing alike); a turned gear mate is a stub; both given is a `BuildError`. A removes `internal` (and the
  bridge) with its tests, writing `_planned_axes` and `_mesh_senses`.
- **Not moved at I, on purpose**: swbuild's own `sw.gear_mate_sense(handle, internal)` calls and the fake's
  `gear_mate_sense` keep W5's form; only the fake is called in tests. A moves both first (no SolidWorks run uses
  the app between I and A).

### `store.py` (schema 4)

- `LINK_SCHEMA_VERSION = 4`. A v1–v3 record reads as v4; **any** newer schema is refused untouched (the check is
  `version > LINK_SCHEMA_VERSION`, tested at 5, 6 and 12).
- `ShaftEntry += direction: List[float] = []; z_side; z_global; z_plane; line; axis: str` — field for field with
  `ShaftLayout`; a v3 entry reads `direction = [0, 0, ±1]` and `axis = "Z+"/"Z-"` from `sigma`; a tuple given is
  kept as a list.
- `MateEntry += plane: str = "front"; sense: int = 0` (a v3 entry reads with those defaults).
- C completes the refusals (a bad `plane`, a bad `sense` or 0 on a v4 mesh, a `direction` not three finite numbers
  of unit length).

### Conventions (unchanged from §4.3)

A gear's axis is its frame's third column in every `Place` and `Placement`; along mates name `"layout:plane1|2|3"`,
axis mates `"layout:<Shaft> Axis"`; the `sense` maps are keyed by the Meshes row's ordered pair `(a, b)`; A's fake
reads the layout from the plan's ops, never from B's code.

## 4. `copy_built` (W6-PLAN §6.2), pinned for E and for W7's demonstration

`copy_built(master: str, section: str) -> str` in `probe/workbook_assembly_check.py` (E writes it), returning the
copy's folder `OUT/<section>`. Its steps, in order, each a STOP with a sentence when it fails:

1. **The builder section ends clean** (before any copy): every document of its folder closed (`quit_in(folder)`;
   on 2024 W5's `close_ours` saves this run's modified parts first), Excel's workbook closed (`close_books`), no
   open SolidWorks document with a file name the folder holds (`open_titles`), and the folder renamed
   `<section>.master`, which it stays for the rest of the run.
2. **The copy**: `shutil.copytree(master, OUT/section)` (`copy2`, mtimes kept). Every `<Name>.workbook.json` read
   with `store.read_link_record`; every string field starting with the original folder (normcase) rewritten onto
   the copy's — `workbook`, each part's `path`, the gearbox's `layout`, `assembly`, each component's `part`, the
   journal, earlier revisions, `moved_from`, the keys of `unsaved` and `mismatched` — and written with
   `store.save_link_record`; every `.gear.json` likewise through `store`'s own reader and writer. Asserted after:
   `store.record_owner(record, workbook)` is OURS; every path in the record exists and lies in the copy;
   `store.clear_saved` drops nothing; the read's digest equals the record's (the Output folder is blank).
3. **SolidWorks finds the copy's files**: the copy's assembly opened once (`OpenDoc6`, silent; the first time under
   the dialog watcher with a 120 s timeout, §7.1), every component's and the layout's `GetPathName` in the copy or
   the section STOPs (*a copy loaded the master's files*) and builds fresh instead; the flags straight after the
   open logged as facts; closed **without saving** (`QuitDoc`).
4. **Two copies are never open together**: each copy section ends as step 1, without the rename.

## 5. Readings where two were possible

- `ShaftLayout` also gains `axis: str` (§2.8 says `ShaftEntry` mirrors it field for field and adds `axis`; §4.3
  lists `ShaftLayout` without it): so the mirror, `_recorded_shafts` and the round-trip test hold.
- `Session.gear_mate_sense` is written for parallel axes on `sense_reading` (the probe call fixed at I needed a
  working form); the turned gate is A's stub. swbuild's callers and the fake stay W5's form until A (above).
- `sense_reading` gains keyword-only `mate=""`, since §2.9's read-back refusal names the mate; it cannot name the
  gear (it is given axes, not gear ids), so the refusal names the axes and the caller names the mate.
- `build`/`build_gearbox` take `senses` now, bridged to `internal` for parallel meshes; `internal` and
  `ring_meshes` stay until A and B remove them, since removing them at I breaks A's and B's tests.
- `axis_vector("")` is Z+ (the Axis column's blank); `face_global(…, bevel=True)` names `Apex` on any plane.
- A v3 shaft's `axis` is read as `"Z+"`/`"Z-"` from its `sigma`.

## 6. Open points

**A.** Move swbuild's sense reads and the fake to the new `gear_mate_sense` first (`_planned_axes`, `_sense_read`
with axes, `_mesh_senses`), then drop `internal` and `_internal_from_senses`; the turned gate in
`Session.gear_mate_sense` and as swbuild's second guard; `line_axis`, `axis_line`; the fake per W6-PLAN §4.2.
**B.** Every `Placed` constructor gives `axis`, `centre`, `family`, `bevel`; every `ShaftLayout` its `direction`,
`axis` and planes; `solve(senses=…)`; replace `motion.parallel_sense`'s uses; move `build_kwargs` to `"senses"` from
`mate_senses` and drop `ring_meshes`; the turning round trip for fixtures A and B as its second pass.
**C.** Schema 4's refusals and every §2.9 sentence C shows. **E.** `copy_built` as §4; the turned interference
controls. **P.** The two findings, reviewed, before E.
