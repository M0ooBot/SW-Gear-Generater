# W7 (planetary): the interface commit

Package I of `W7-PLAN.md` §5.3. Packages A, B and C work in parallel from here, against the fake, on disjoint files,
reading this note and the code it names. **A change to a shape pinned here is a stop-and-ask**; private helpers, and
keyword-only parameters with defaults in your own module, are free. Authority: `docs/PLAN-WORKBOOK.md`, then
`W5-DECISIONS.md`, then `W7-PLAN.md` as revised (its §10, "After the W8 check" included: a gear on the carrier's own
shaft is built, locked to the carrier), with W6 as built (`W6-INTERFACES.md`, all twenty rulings of §7) beneath it.

## 1. Where it starts, and what W6 left that W7 builds on

- **Starting commit: `3cbde55`** (branch `workbook`), with W6's packages A–D written and reviewed on the fake
  (`8e27b7f`) and W6's demonstration still running on SolidWorks 2026; the ring/shift checks W7 reads are `d3f4dcf`
  and `9efde87`; the spike W7 rests on is `8a798fe` (`W7-SPIKE.md`).
- Suite on a clean `git archive`, Linux: **2609 passed, 1 skipped** at the interface commit. Windows Tk tests:
  123 passed, 1–2 skipped (the "no display for Tk" flake).
- **W6's shapes W7 uses, as built** (W7-PLAN §5.3, review S15): own-axis kinematics, `kinematics.solve(spec,
  skip_gears=(), senses=…)`; `Placed.axis`, `centre`, `family`, `bevel`, `origin`; `geometry.base_frame`, `family`,
  `axis_vector`; `layout.frame` on `base_frame`; `motion.mesh_links(meshes, teeth, sense)` with `k = −c·za/zb`;
  `MatePlan`/`MateEntry` `plane` and `sense`; `swcom.sense_reading` and `Session.gear_mate_sense(handle, same_sense,
  axes)`; `build(..., senses=)`, `build_gearbox(..., senses=, lines=)`, `GearboxPlan.mate_senses`; `copy_built`
  (W6-INTERFACES §4). W6's rulings that carry over unchanged: **§7.1** a mesh entry's `sense` 0 is legal on a
  parallel mesh and every finisher that rewrites a mesh entry writes its real ±1; **§7.2** `mate_senses[name] =
  (plan.sense == -1)`; **§7.4** no single τ named on parallel axes; **§7.5** "parallel" is the family rule;
  **§7.14** `GearboxUpdate.resensed`; **§7.20** `Assessment.turned_refusal()` is the one home of the turned refusal
  (`assess.TURNED_KINDS`), which a planetary does not join (its meshes are all PARALLEL); **§7.11** no
  `NotImplementedError` reaches a user; **§7.18** the fake works a mesh's true sense out from where the gears stand.

## 2. Who edits what (W7-PLAN §5.2)

| Package | May edit |
|---|---|
| **A** — SolidWorks | `swcom.py`, `swbuild.py`, `tests/test_swbuild.py` (the fake), `tests/test_swcom.py`; may add to `tests/test_swbuild_train.py` and `tests/test_swbuild_planetary.py` (I's: never change an assertion there) |
| **B** — planning | `workbook/planetary.py`, `geometry.py`, `kinematics.py`, `checks.py`, `fixes.py`, `assess.py`, `build.py`, `model.py`, `layout.py`, `motion.py`, `gearbox.py`, `update.py`, `export.py`, `gears/base.py` (`BuildPlan.check`'s duplicate-global refusal only); `tests/test_workbook_{planetary,geometry,checks,model,layout,motion,gearbox,update,export,demo_fixtures}.py`, `tests/test_probe_workbook.py` |
| **C** — record, words | `store.py`, `ui_text.py`, `tests/test_store.py`, `tests/test_ui_text.py` |
| **D** — window, boards, docs (after A–C) | `workbook_gui.py`, `preview.py`, `tests/test_preview.py`, `tests/test_workbook_{build,window}.py`, `design/**`, `docs/**`, `README.md` |
| **E** — demonstration | `probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, `probe/results/**`, `tests/fixtures/excel-windows/Planetary_4to1.xlsx`; after E's first 2026 run, `findings.py` and `tests/test_findings.py` for J20's finding only |
| nobody | `gears/*.py` but `base.py` as above |

I wrote, beside the pinned code: `tests/test_swbuild_planetary.py` (new, `train_check` with carriers), the first tests
of `tests/test_workbook_planetary.py` (new, B's from now) and schema 5's tests in `tests/test_store.py`, and moved one
line of D's `tests/test_workbook_window.py` (`== 5`: the record's schema number).

## 3. Pinned shapes, and the identities that fix which way round they are filled

**Written in full with tests at I:** `swbuild.train_check` with `carriers` and `held` (and `CarrierLink`,
`MeshLink.carrier`); `planetary.copy_id`, `copy_of`, `copy_offsets`; `layout.carrier_id`, `carrier_stem`;
`motion.mesh_links(..., carrier_of=)`; `motion.mate_entry` carrying `on`; `GearboxPlan.build_kwargs` and
`UpdatePlan.update_kwargs` adding `"carriers"` only when non-empty; schema 5's reading. Everything else is a
signature and a docstring raising a full sentence (`ValueError` in planning and `ui_text`, `BuildError` in the
worker, before anything is made), never `NotImplementedError`.

### Names, handles and copies

| What | Identity | Worked example (W7-PLAN §4.1) |
|---|---|---|
| a copy's id (gear and shaft alike) | `planetary.copy_id(name, k, copies)`: `name` with Copies 1, else `f"{name} copy {k}"`, k = 1 … N | `Planet copy 2`, `P copy 2`; Copies 1: `Planet`, `P` |
| back from a copy id | `planetary.copy_of(id) -> (name, k)`, k 0 for a name with no copy word | `("Planet", 2)` |
| `ComponentEntry.of` | `copy_of(gear)[0]` when the gear's shaft has Copies > 1, else `""` | `"Planet"` |
| `Placed.gear`, `Placed.shaft` | the copy's own ids; `Placed.row` the Gears row id (a frame gear's own id), `Placed.copy` its k (0 with Copies 1), `Placed.carrier` its carrier shaft (`""` on the frame) | `("Planet copy 2", "P copy 2", "Planet", 2, "C")` |
| a carrier as a body | `layout.carrier_id(shaft) = f"{shaft} carrier"`: its key in `train_check`'s frames, `CarrierLink.carrier`, `MeshLink.carrier`, the gear side of its mate names, `MateEntry.on`, `MotionPlan.carriers` | `"C carrier"`, `"C carrier on C Axis"`, `"CarrierGear locked to C carrier"` |
| a carrier part's stem | `layout.carrier_stem(box_name, revision, shaft) = f"{stems(box_name, revision)[0]}_{shaft}_Carrier"` | `Planetary_4to1_C_Carrier`, `Planetary_4to1_r2_C_Carrier` |
| handles in the assembly plan | the layout `layout`; carrier i (Shafts-sheet order, from 1) `f"{CARRIER_HANDLE}{i}"`; gear index i (Gears-sheet order) `f"gear{i}"`, copy k of it `f"gear{i}c{k}"` (Copies > 1) | `carrier1`, `gear2c2` |
| a copy's point on its carrier | `planetary.copy_offsets(x, y, z, N)[k-1] = rot_z(ψ_k)·(x, y, z)`, `ψ_k = (k−1)·360/N` degrees about the carrier's OWN +Z, each coordinate rounded to 1e-12 mm, no `-0.0`; copy 1 is the typed point exactly | 3 copies of (18, 0, 0): (18, 0, 0), (−9, 15.58845726812, 0), (−9, −15.58845726812, 0) |
| a copy's point in world | `p_c + base_frame(a_c)·offset` (J4, review M4) | Z+ carrier at the origin: the offsets; **Z−**: (18, 0, 0), (−9, −15.588…, 0), (−9, 15.588…, 0) — y and z negated |
| a carrier part's axes | `layout.CarrierLayout.axes`: one `ShaftLayout` per copy in the carrier part's OWN coordinates (the offsets as they are, on either sense of carrier), `direction` (0, 0, 1), `sigma` +1, names `"P copy 2 X Plane"`, globals `"P copy 2 X"`, axis `"P copy 2 Axis"` | globals `P copy 1 X`, `P copy 2 X`, `P copy 2 Y`, `P copy 3 X`, `P copy 3 Y` |
| an along mate's axis target | `MatePlan.on`: `""` the layout, else the carrier id; `shaft` the axis stem, the axis always `f"{shaft} Axis"` in the component `on` names (the layout when `""`) | `Planet copy 2 on P copy 2 Axis`: `on = "C carrier"`, `shaft = "P copy 2"` |

### `train_check` with carriers (the one rule A and B both use)

- **`CarrierLink(carrier, planets, point, axis)`**: `point` and `axis` are the carrier's WANTED frame's origin and
  third column — the caller keeps that identity. `planets` holds every gear on the carrier's planet shafts (copy
  ids), in plan order (review S7).
- **The carrier's turn δ_c** is `turn_between(wanted, found)` of its own frame, about its own +Z. Each planet's
  wanted frame is **carried by δ_c about the line through `point` along `axis`** (Rodrigues, right-handed about
  `axis`) before it is judged; on a Z+ carrier that is `rot_z(δ_c)` about world +Z, on a Z− carrier `rot_z(−δ_c)`.
  A planet's δ is then **its turn relative to the carrier**. A carrier off its axis takes its planets off with it.
- **A mesh with `MeshLink.carrier`** takes each frame gear (sun, ring) relative to the carrier: `δ − s·δ_c`,
  `s = sign(a_gear · axis)`, `a_gear` the gear's wanted third column; `k = −c·za/zb` with `c` the **carrier-frame
  sense** (W6's parallel rule: `a·a` outside, `−a·a` inside). Fixture: `Sun–Planet copy k` c = +1, k = −1;
  `Planet copy 1–Ring` c = −1, k = +1/3. Driven +30° on Sun: δ_c = +7.5°, each copy's own turn −15° (relative −22.5°),
  Ring 0 → Sun relative +22.5, `−22.5 − (−1)(22.5) = 0`; Ring relative −7.5, `−7.5 − (1/3)(−22.5) = 0`. The carried
  copy origins are (17.846008, 2.349471), (−10.957706, 14.280360), (−6.888302, −16.629832) — the spike's.
- **`held`**: gears judged against their wanted frames exactly but for whole pitches — a held gear turned off a
  whole pitch, or moved, is **off its axis** (to be re-placed). A **held carrier is given in both `carriers` and
  `held`** (its δ_c must be 0). `MotionUpdate.held` is the held gears a recorded gear mate touches (review M1); a
  fixed gear nothing gear-mates stays out of `train_check`, as in W5.
- **Locks** are judged on the δ's as kept (a carrier's own, a frame gear's own, a planet's relative):
  `LockLink(anchor="C carrier", follower="CarrierGear")` holds exactly when CarrierGear turned as far as the carrier.
  The carrier is the lock's ANCHOR (selected first, W5's lock route).
- With no `carriers` and no `held` it is W5's function, result for result.

### By module

- **`swbuild.py`**: `CarrierLink`; `MeshLink.carrier: str = ""`; `train_check(..., *, carriers=(), held=())`
  (written); `MotionUpdate.carriers: Tuple[CarrierLink, ...] = ()`, `MotionUpdate.held: Tuple[str, ...] = ()`;
  `STAGE_CARRIER = "carrier"` (in `STAGES`); `GearboxResult.carriers: List[BuildResult]`,
  `GearboxResult.carriers_reused: List[str]`; `build_gearbox(..., *, carriers: Sequence[BuildPlan | DocumentValues]
  = ())` and `update_gearbox(..., *, carriers: Sequence[DocumentValues] = ())` — given any, each refuses with a
  `BuildError` sentence until A writes the step.
- **`workbook/planetary.py`** (new): `copy_id`, `copy_of`, `copy_offsets` (written); `Stage(carrier, sun, ring,
  planet, planet_shaft, copies, held)` (`held` the member SHAFT whose Role is fixed; `planet` and `planet_shaft`
  are row ids); stubs `stages`, `assembly_counts`, `most_that_fit`, `mesh_carrier` (`"frame"`, a carrier shaft, or
  None), `refusals`.
- **`geometry.py`**: `Placed.row: str = ""`, `copy: int = 0`, `carrier: str = ""`; stub `expand_meshes(spec,
  placed)` (Meshes-sheet order, copy order within a row, each pair in its row's order).
- **`kinematics.py`**: `Motion.relative: Dict[str, Fraction]` (`ω_p − s_p·ω_c`, `s_p = a_p·a_c`: fixture P −750 on
  C), `Motion.held: Dict[str, float]` (a held member's torque, N·m: R 5.7624), `Motion.torque_note: str = ""`.
- **`checks.py`**: `Report.stages: Tuple[planetary.Stage, ...] = ()`.
- **`layout.py`**: `CARRIER_KIND = "carrier"`, `CARRIER_SUFFIX = "_Carrier"`, `CARRIER_HANDLE = "carrier"`,
  `CARRIER_ID_SUFFIX`; `CarrierLayout(shaft, x, y, z, direction, axes)`; `carrier_id`, `carrier_stem` (written);
  stubs `carrier_layouts(spec, report)`, `carrier_frame(carrier) -> Frame` (`base_frame(direction)` at `(x, y, 0)`,
  J2), `carrier_plan(carrier, template, path)`.
- **`motion.py`**: `MatePlan.on: str = ""` (after `sense`); `MotionPlan.carriers: Tuple[str, ...] = ()`;
  `mesh_links(meshes, teeth, sense, *, carrier_of={})` (written); stub `carrier_links(spec, report, plan)`.
- **`gearbox.py`**: `CarrierReuse(path, variables, features, journaled=False)`; `GearboxPlan.carriers:
  Tuple[BuildPlan | CarrierReuse, ...] = ()`, `carrier_paths: Mapping[str, str] = {}` (carrier shaft → part path),
  `carrier_layouts: Tuple[CarrierLayout, ...] = ()`; `build_kwargs()` adds `"carriers"` (a `CarrierReuse` as
  `DocumentValues`) only when non-empty.
- **`update.py`**: `UpdatePlan.carriers: Tuple[DocumentValues, ...] = ()`, `carriers_moved: Tuple[str, ...] = ()`;
  `update_kwargs()` adds `"carriers"` only when non-empty.
- **`store.py`** (schema 5): `LINK_SCHEMA_VERSION = 5`; `CarrierEntry(shaft, path, component, rotation, at,
  direction, axes: List[ShaftEntry])`; `GearboxRecord.carriers: List[CarrierEntry] = []`; `ComponentEntry.of: str =
  ""`; `MateEntry.on: str = ""`. Reading: every new field defaulted, so **a v1–v4 record reads as v5 with no
  carriers and every `of`/`on` empty — what a record with no planetary stage holds — and writes and reads back the
  same** (tested on v3 and v4). A schema newer than 5 is refused untouched (`version > LINK_SCHEMA_VERSION`; W8 sets
  6). A carrier's `axes` are read as `ShaftEntry`s with no v3 fill. C adds the refusals (a `CarrierEntry` with no
  shaft or path; an `on` naming no carrier on record).
- **`ui_text.py`**: stubs `carrier_phrase(record_or_plan)`, `copies_phrase(row, n)`, `planetary_speed_line(shaft,
  motion, *, copies=1, carrier="")`.

## 4. Readings where two were possible

- `train_check` lists a held gear turned off a whole pitch under `off_axis` (it must be re-placed), not
  `out_of_step`, and a held carrier is given in both `carriers` and `held`.
- `layout.carrier_id` and `carrier_stem` are written, not stubs: they are names every package keys on (the W5
  `mate_name` precedent); `planetary.copy_of` is added as `copy_id`'s inverse, for `ComponentEntry.of`.
- `copy_offsets` rounds each coordinate to 1e-12 mm, so a quarter turn lands on a base plane exactly and the
  carrier part's literal globals are short.
- `planetary_speed_line`'s signature (§5.3 wrote `(...)`): `(shaft, motion, *, copies=1, carrier="")`.
- A superseded revision's carrier part goes into `EarlierRevision.parts` (paths only, as a part), since no field
  was pinned for it.
- `GearboxPlan.handles` stays gears and copies only; the carrier's handle is not in it.

## 5. Open points

**A.** The carrier step in `build_gearbox` and `update_gearbox` (pre-flight, progress `STAGE_CARRIER`, log lines,
a failure skipping the assembly); `_trains` joining a carrier to its planets and a held gear to the trains its gear
mates touch, passing both to `train_check`; the put order (held member, carrier, train, every lock of the train —
the carrier gear's among them — suppressed around the puts, on again in a `finally`); the fake of W7-PLAN §2.9
(rank of the carrier-frame rows for over-definition; a held component not moved by the solve). The mate-problem
sentences name a carrier by its id: pass `{carrier handle: carrier id}` through the `gears` map.
**B.** Every `Placed` and stage shape filled; `mesh_links(..., carrier_of=)` for every stage mesh; `MatePlan.on`,
the mates by rank (J5), `MotionPlan.carriers`; `CarrierLink`s for `MotionUpdate`, `held`; `build_kwargs` with
`"gears"` covering carrier handles if A asks; the round trips on the fake after A (second pass).
**C.** Schema 5's refusals, and every §2.12 sentence. **D.** After A–C. **E.** `copy_built` (W6-INTERFACES §4)
covers `CarrierEntry.path` by rewriting every string field under the original folder.

## 6. Rulings on the interface review (2026-11-14)

The independent review of `5d5d51d` worked the 4 : 1 by hand (Willis; sun +30° → carrier +7.5°, a planet −22.5°
relative to its carrier and −15° absolute, the ring still), recomputed the carried copy origins, ran 20 000 random
cases of `train_check` with no carriers against W6's with no difference, and found the shapes right. It asked for
written rules. These bind A, B and C from now; a line number is the line at `5d5d51d`.

1. **A record W7 writes is never refused on its next read.** Three parts. (a) Every finisher keeps one
   `CarrierEntry` per carrier of the plan, built or reused, whenever it writes mates: a Build that failed after the
   carrier part was saved and is carried on with a `CarrierReuse` must not finish with an empty `carriers` beside
   mates whose `on` names that carrier. (b) `update._bad_mates` (`update.py:585`) and C's checks treat
   `carrier_id(shaft)` of every `CarrierEntry` as a known body, beside the components: the carrier's own mates
   (`C carrier on C Axis`, `CarrierGear locked to C carrier`) name it in `gears`. (c) `store` owns
   `CARRIER_ID_SUFFIX = " carrier"` (it cannot import `layout`), `layout`'s constant equals it, and a test pins the
   equality. C tests: read a v3, a v4 and a v5 planetary record → write → read; and a continued build's record.
2. **The `gears` map covers the carrier.** `build_kwargs()["gears"]` is `GearboxPlan.handles` (gears and copies
   only, as §4 has it) plus `{f"carrier{i}": carrier_id(shaft)}`, with `i` counting carriers in Shafts-sheet order
   from 1. `CarrierEntry.component` comes from `result.components[f"carrier{i}"]`.
3. **A planetary Update always carries its carriers.** `UpdatePlan.carriers` lists every carrier part on record for
   a planetary gearbox, always, as the layout is passed, not only when a carrier part changed. A's update refuses,
   before anything is read, when `motion.carriers`, `motion.held` or any `MeshLink.carrier` is set and no carrier
   parts are given, and turns any `ValueError` from `train_check` into a `BuildError` sentence (W6-INTERFACES §7.11).
4. **The carrier is a `Placement`**: `Placement(gear=carrier_id, component=CarrierEntry.component, rotation, at,
   pitch=0.0)` in `placements`, with its recorded frame in `MotionUpdate.recorded`.
5. **`held ⊆ fixed`.** A held member is in `MotionUpdate.fixed` as W5 has it; `held` only adds "judged in
   `train_check`, and put first". A held carrier is also in `carriers`.
6. **The unmated ring meshes are `MeshLink`s** in `MotionUpdate.meshes`, so the post-check judges every mesh in
   step, mated or not. The record's mate entries hold only the mates made.
7. **The shared `"Planet Face Z"` global** is keyed by the row id (`Placed.row`) in `face_globals` and in
   `GearboxUpdate.axial`; C's "moved … along …" finds the shaft through the along mates of that row's copies.
8. **`MatePlan.on` is for AXIS mates only.** A planet's along mate goes to `layout:plane1` with `on = ""` and
   `z_front` the world Front coordinate. Line 66 of this note, which says "an along mate's axis target", is wrong.
9. **`gearbox.on_record`** (`gearbox.py:950`) lists `gearbox.carriers[].path`, so a carrier part's journal entry
   settles.
10. **The fixture's senses, as an identity:** for the 4 : 1, `mate_senses` is False for each sun–planet mate
    (k = −1, outside) and True for the planet–ring mate (k = +1/3, inside) — W6's `mate_senses[name] =
    (plan.sense == -1)` unchanged, since for coaxial parallel axes the sense in the carrier's frame is the sense in
    the world. The spike agrees: the ring mate read wrong with the first Flip.
11. **`GearboxUpdate.carriers: List[UpdateResult]`** (A's `75d089b`) holds each carrier part's values as the Update
    set them, after the layout's, as `GearboxUpdate.layout` holds the layout's. C says "moved the planets on C"
    after an Update from it (a carrier part whose values changed), and there is no separate list for that. The
    build's result has `GearboxResult.carriers` and `carriers_reused`; a reused carrier part found changed goes to
    `mismatched` and nothing is built.
12. **What the fake keys on, which planning must keep:** an axis mate is carrier-held when its target component's
    handle does not start with `layout`; a ring is read from a part file whose name starts with `Ring`.
13. **The order of puts in a planetary train** (A's `75d089b`): a held member that is off its place first, then the
    carrier, then every other gear; every lock of the train off around the puts and back on afterwards. No probe
    has shown that a put of the carrier holds with its planets' axis mates on, or that a planet put onto its carrier
    axis holds once the carrier stands at its frame; each put is read back and the post-check judges every train
    again, and the demonstration's Update sections are where SolidWorks first shows it.
14. **Which gear mates are made does not depend on the Meshes sheet's row order** (ruled after B's review, built in
    B's `6ed3439`). The candidates are ordered by member before the rank: the stage's sun meshes first, then its
    ring meshes, then every other mesh; within a group, Meshes-sheet order and then copy order. So every sun mesh
    gets its gear mate, one per copy, and the ring gets exactly one, with copy 1 — the set the spike measured —
    whichever member is held and however the rows are listed. This supersedes the J5 row of W7-PLAN §3, which shows
    rank in sheet order as the default; it is a default the user may overrule.
15. **A planetary stage has one input.** A second member of the stage given Role input is an error at its cell,
    whether or not its speed agrees with the first (ruled as "two inputs are refused"; B's checks let a consistent
    second input through until this ruling's fix).
16. **`GearboxUpdate.placed` is the order the puts were made in**, on every path (A's `7a34852` pins it; no code
    changed). Each name is appended straight after its own `place_component` returns, and a put that raises is not
    listed. For a planetary train: a held member that is off its place, then the carrier, then the rest in the
    order of planning's placements. The demonstration's p3 asserts that order from this list.
