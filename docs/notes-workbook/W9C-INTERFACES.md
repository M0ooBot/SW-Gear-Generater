# W9c: Update adds, removes and re-mates — the interface between planning (B) and the worker (A)

Stage W9c of `ISSUE-1-PLAN.md` (§2.1 "W9c — Update adds, removes and re-mates (K6)" to "Still Build again… after
W9c", §2.4 "In place (W9c)", §4 M4, M5, M6, M8, M10, §5 "W9c", K6, §0.3), written before any W9c code, against the
probes' review (`W9C-PROBES-REVIEW.md`, `88a251e`) and the findings it set (`findings.py`, the W9c block, `c8da5bb`).
Package B is planning (`workbook/update.py` `classify`, `finish_update`, the sentences, UI-DESIGN §9); package A is
the worker (`swbuild.py`, `swcom.py`, the fake). This note fixes the shapes the two packages share, the order the
worker runs in, what it refuses before any write, what it hands back, the record, the findings each step reads and
the calls each step makes. A change to a shape here is a stop-and-ask, as at W8 and W9a. **Choices the plan left
open are marked ⟨C1⟩ … ⟨C12⟩ and listed in §10 for the coordinator's ruling.**

## 1. The contract in one sentence

**`MotionUpdate` describes the gearbox as it is to stand after the Update, less what is new in SolidWorks; the new
`InPlace` describes only what the Update makes or takes away.** So the worker's check phase, which finds every
recorded mate and component by name (a miss is `NotAsBuilt`) and reads every mate not on record as the user's, keeps
working: it is told which of the components and mates it finds are about to go (`InPlace.removed`), and nothing it
cannot yet find is asked of it before it is made.

- `update_gearbox(..., motion=MotionUpdate(...), in_place=InPlace(...))`. `in_place=None` (or an empty `InPlace`)
  is W9a's Update exactly, call for call.
- `motion.mates`: the recorded mates that stay. A mate of a removed gear is **not** in it (it is in
  `RemovedGear.mates`), and a mate the Update makes is not in it either (it is in `AddedGear.ops` or
  `InPlace.new_mates`). The worker adds each mate it makes to its own list once made, so the post-checks and the
  flags-after read cover it.
- `placements` (and `motion.recorded`, `mode_placements`, `recorded_by_mode`): every gear that stands after the
  Update. **An added gear's `Placement.component` is `""`**: the worker fills it with the `Name2` SolidWorks kept at
  the insert (`GearboxUpdate.inserted`). A removed gear is in none of them. ⟨C1⟩
- `motion.configurations`, `slide_values`, `on_sets`, `mode_placements`: the configurations **after** the Update, in
  the record's order (`InPlace.modes_added` among them, `InPlace.modes_removed` not). An added mode's slide values,
  on-sets and frames are given there as any mode's.
- `motion.ratios`: every gear mate whose ratio changes, as today. On a gearbox with modes the worker now remakes them
  (lifting ruling 9.16) where the finding gate of §8 is set.
- `parts`: every part of the revision after the Update, a new part included once built (its `DocumentValues` holds
  its globals, checked after the build), a removed gear's part left out when no other gear uses it.

## 2. The shapes (`swbuild`; B builds them, A reads them)

```python
@dataclass(frozen=True)
class AddedGear:
    """A gear the Update inserts on an existing frame shaft along Z+ or Z− (K6)."""
    gear: str                                   # its gear id ("Hub", "G5")
    handle: str                                 # the gearbox plan's handle for its component (base.AddComponent.id)
    part: str                                   # its part's path
    build: Optional[BuildPlan] = None           # the part's plan when its file is new: built and saved first
                                                # (None: a part file on record, shared with another row)
    ops: Tuple[base.Op, ...] = ()               # its ops from the gearbox's assembly plan, in plan order: AddGlobal
                                                # (its Face Z), AddComponent, Place, Fix (a fixed gear), every Mate
                                                # that touches it (axis, along, lock, spline, mesh; a hub's spline to
                                                # its sleeve), LinkDimension
    handles: Tuple[Tuple[str, str], ...] = ()   # every other plan handle those ops name -> the Name2 on record
                                                # (the layout's, the anchor's, a mesh partner's, the sleeve's)
    senses: Tuple[Tuple[str, bool], ...] = ()   # each gear mate's name -> turns its two gears the same way (W6)
    on_sets: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()  # each of its mates on in some modes only -> where
                                                # (absent: on in every configuration)

@dataclass(frozen=True)
class RemovedGear:
    """A gear the Update takes out with its app mates; it anchors no other gear (K6)."""
    gear: str
    component: str                              # its Name2 on record
    part: str                                   # its part's path (the file stays on disk)
    mates: Tuple[str, ...]                      # every recorded mate that touches it, by name: gone with it

@dataclass(frozen=True)
class NewMate:
    """A coupling or sliding mesh newly needed between components on record (K6), made as the build makes it."""
    op: base.Mate                               # the gearbox plan's op (kind "gear", ratio (1, 1) for a coupling)
    handles: Tuple[Tuple[str, str], ...]        # its two plan handles -> Name2 on record
    on: Tuple[str, ...]                         # the configurations it is on in (never empty: ruling 9.1)
    same_way: bool                              # as ModesPlan.same_way

@dataclass(frozen=True)
class BandChange:
    """A built sleeve given bands, or relieved of them, in place (§2.4)."""
    gear: str
    part: str                                   # the sleeve's part path (kept: its file, the user's groove, its mates)
    add: bool                                   # True: bands given; False: bands taken away
    ops: Tuple[base.Op, ...] = ()               # add: the band globals (AddGlobal "Start Band", "End Band",
                                                # "Relief Diameter") and gears.clutch.relief_ops, as the banded plan
                                                # has them after the teeth
    features: Tuple[str, ...] = ()              # the relief's feature names (both ways: to add, or to suppress)

@dataclass(frozen=True)
class InPlace:
    added: Tuple[AddedGear, ...] = ()
    removed: Tuple[RemovedGear, ...] = ()
    new_mates: Tuple[NewMate, ...] = ()
    bands: Tuple[BandChange, ...] = ()
    modes_added: Tuple[str, ...] = ()           # configuration names to add, Modes-sheet order
    modes_removed: Tuple[str, ...] = ()         # configuration names (as on record) to delete
    first_mode: str = ""                        # the record's first mode after the Update, when it changes

    def __bool__(self) -> bool: ...             # anything to do
```

Each `base.Op` is the gearbox planner's own op (`workbook/gearbox.py`, `workbook/motion.py`), taken from the plan
the same workbook would build, so the worker makes nothing a build would not. A hub that becomes its shaft's anchor
(J9) is an `AddedGear` whose `ops` hold its AXIS, ALONG and the sleeve's SPLINE to it (`motion._sliding_shaft`): the
sleeve's AXIS and SLIDE keep their names and stay on record. A Modes row added is `modes_added` plus its entries in
`MotionUpdate`'s per-mode fields; a row removed is `modes_removed`.

## 3. What B hands A, and the rules B keeps

`UpdatePlan` gains `in_place: InPlace = InPlace()`, and `update_kwargs()` passes `"in_place"` when it is non-empty.
`classify` moves out of `structural` exactly these (each now an `InPlace` entry):

| Edit (K6) | `InPlace` | Still structural when |
|---|---|---|
| a gear added on a shaft on record whose direction is Z+ or Z− | `added` | the shaft is new, slanted or crossed; the gear is a planet copy (the number of copies); a recorded mate would change name, kind or gears (an anchor that is no longer the first gear that does not slide, a lock that becomes a spline) |
| a hub added under a sleeve (it becomes the shaft's anchor) | `added` (its spline in `ops`) | as above: e.g. another slider on that shaft already splined to the old anchor |
| a gear removed that anchors no other gear | `removed` | it anchors a gear (a LOCK or SPLINE on record with it first); a mesh between two gears that stay would go |
| a coupling or sliding mesh newly needed between components on record | `new_mates` | ruling 9.1: one that would be on in no mode |
| a tooth change on a gearbox with modes (9.16) | `motion.ratios`, as without modes | the part's file must change |
| bands given to, or taken from, a built sleeve | `bands` | the sleeve's file must change (Flank, Part name) |
| a Modes row added | `modes_added` + per-mode fields | — |
| a Modes row removed | `modes_removed` | the row removed is the mode showing (refused by A, live: §5); a coupling or sliding mesh would be on in no mode (9.1) |

Everything §2.1 lists under "Still Build again… after W9c" stays structural, said in the question. B also passes
`DocumentValues.made` for a part given bands **including** the relief's feature names, so K3 tells the user's
features (now before the relief) from the app's (after them) ⟨C2⟩.

## 4. The order the worker runs in, and why

**Check (reads only; any refusal changes nothing).** W9a's check phase, with the removed gears' components found by
`RemovedGear.component` and their mates by name (counted as the app's, not the user's); then §5's refusals; then the
gates of §8. **Change**, each step stopping the job on a failure, nothing saved:

1. **New parts built** (`AddedGear.build`), each by the build's own `build` and saved to its path. *Why first:* they
   are new files of the app's, the assembly is not yet touched, and a part that fails stops the job with nothing in
   the user's assembly changed.
2. **Parts and the layout set**, as today (W4/W9a, K3, K11). **Bands in place** run in their part's own step, after
   its values: given — the band globals added, the relief ops run on the opened part (they land after the user's
   features), a rebuild, the features read (K3); taken away — the relief's features suppressed (§9). *Why here:* the
   part's geometry is settled before the assembly rebuilds over it, as for any value change.
3. **The assembly opened**, then, in this order:
   1. **Modes removed** (`delete_configuration`, a configuration that is not showing; the user's mates' flags there
      read first, unshown, for §6). *Why first:* every flag set afterwards is set once, in the configurations that
      remain, and deleting a configuration that is not active does not stale handles (`Session.delete_configuration`:
      held handles survived it in W8's spike).
   2. **Gears removed** (`Select4` + `EditDelete`, `findings.COMPONENT_DELETE_ROUTE_ON_<year>`), each verified by
      reads: the component gone, each of `RemovedGear.mates` gone by name, every other mate still found. *Why before
      any add:* nothing new can then be mated to, or judged with, a body about to go; the puts and post-checks run on
      the gearbox as it is to stand.
   3. **Modes added** (`add_configuration` copies the active configuration and makes the new one active), handles
      fetched again (ruling 9.4), one top-only rebuild before any flag (`API-LEDGER.md:333`), every app mate's flag
      and every slide value set in it and read back, the user's mates' flags and components' states read there for
      §6. *Why before the inserts:* a component inserted and a mate made afterwards get their flags set once, across
      the final set of configurations.
   4. **Gears added**: the active mode shown again; for each, its `ops` run by the build's own op runners (the part
      opened, `AddComponent5`, `Place`, `Fix`, each `Mate` with its sense read and made again with the other Flip if
      wrong, `LinkDimension`); then every mate it made has its flag set in every configuration from its on-set and
      read back; its component's state in each mode read when that mode is shown (step 3.7). *Why the active mode:*
      the user is in it, and the build makes a step's mates in the mode shown.
   5. **New couplings and sliding meshes** (`new_mates`): made in the first mode they are on in, shown, as the build's
      step 5 makes them; flags set in every configuration and read back.
   6. **Gear mates remade** (`motion.ratios`, `findings.GEAR_MATE_RATIO_ROUTE` "remake"): W5's remake (delete, add,
      rename) in a mode the mate is on in, its flags set in every configuration and read back, its sense read in
      each mode it is on in when shown. *Why after the inserts:* a mesh with a new gear is made new, not remade.
   7. **Then W8/W9a's modes path as today**: D10 and the flags and slide values per configuration, Face Z, every
      train put whole in every mode (ruling 9.18), route (c1), the post-check per mode (which now also reads each new
      component's state and each new mate in that mode), the interference, the active configuration shown again.
      *Why last:* the post-checks then judge everything the Update made, in every mode, before the job ends.

On a gearbox with no modes, 3.1 and 3.3 are empty and 3.5's "first mode" is the one configuration. ⟨C3⟩

## 5. Refused before any write, by name

Each is a `UserProblem` in `UserWorkRefused` (recorded by B as W9a's are), or a `BuildError` where it is no one's
work. New kinds:

- **`PROBLEM_REMOVED = "removed"`** — a user mate on a gear to be removed (from W9a's inventory: a user mate with an
  entity on that gear's component, a leaf of it included): *"Update SolidWorks would take G4 out of
  Reducer_12to1.SLDASM, and your UserLock2 is on it, so nothing is changed; delete or suppress UserLock2 in
  SolidWorks, or keep G4 in the workbook, and press Update SolidWorks again."* The mates named, `values` empty.
- **`PROBLEM_REFERENCES = "references"`** — M4 is unread (no external-references read is measured), so while any
  component of the user's is in the assembly a removal refuses: *"Update SolidWorks would take G4 out, and whether
  your Sprocket-1 or Housing-1 holds a reference to G4's part has not been measured on this SolidWorks
  (findings.EXTERNAL_REFERENCES_READ_ON_2026 is None), so nothing is changed; …"* Once the read is measured this
  becomes "a user part with in-context references to it", named. ⟨C4⟩
- **`PROBLEM_MODE_SHOWING = "mode showing"`** — the Modes row removed is the configuration showing (read live):
  *"The mode L is no longer on the Modes sheet, and RangeBox.SLDASM is showing it, so nothing is changed; show
  another mode in SolidWorks and press Update SolidWorks again."*
- **`PROBLEM_UNSETTLED`** (W9a's kind) — a step whose finding gate (§8) is None or not the measured value on the
  version in use, naming the finding.
- **`PROBLEM_CONFIGURATION = "configuration"`** — a configuration of an added mode's name already in the assembly
  and not on record (it is not the app's to overwrite, §0.3; C10): named as the user's. *(Amended at package A's
  first commit: its own kind, not W9a's `PROBLEM_COMPONENT`.)*

Every `UserProblem` gains **`subjects: Tuple[str, ...] = ()`** (package A's first commit): the other things its
sentence names, so B can word it — the gear removed and the user's components (`references`), the gear removed
(`removed`), the mode (`mode showing`), the configuration (`configuration`), the finding (`unsettled` from an in-place
gate). `mates` keeps the user's mates named.

Faults (`BuildError`, "a fault in Gear Generator"): a `RemovedGear` that anchors a gear on record, an `AddedGear`
on a shaft that is not on record or is not along Z±, an op naming a handle neither added nor in `handles`, a
`NewMate` on in no configuration, a `BandChange` on a part that is not a sleeve's. B never sends these; A refuses
them rather than act.

**For the footer** (B foresees the press, as W9a's `judge_user_work`): `swbuild.judge_in_place(work, in_place, *,
file="the assembly", revision=(), modes=(), remakes=False) -> List[UserProblem]` is pure and returns, in this order,
the `unsettled` problems of the gates, then per gear removed the `removed` problem, then an `unread` problem for each
user mate on in some mode that could not be read (it may be on the gear removed), then `references`, from the
recorded inventory. `modes`: the configurations on record (a gearbox with modes); `remakes`: a gear mate of a gearbox
with modes is made again (`motion.ratios`). `mode showing` cannot be foreseen (the record does not hold the configuration showing); it is
said after the press, recorded, until the workbook changes.

## 6. What the worker hands back (`GearboxUpdate`, new fields)

| Field | Meaning, for the sentences |
|---|---|
| `built: List[BuildResult]` | each new part's build, in order |
| `inserted: List[Tuple[str, str]]` | `(gear, Name2 SolidWorks kept)`, in the order inserted (the record's `ComponentEntry.name`) |
| `deleted: List[Tuple[str, str]]` | `(gear, Name2)` taken out |
| `mates_deleted: List[str]` | the app mates gone with them, each read gone by name |
| `mates_made: List[Tuple[str, Tuple[str, ...]]]` | `(mate name kept, the configurations it reads on in)`, every mate made: an added gear's, a new coupling or sliding mesh |
| `remade_in_modes: List[str]` | gear mates made again on a gearbox with modes (also in `ratios`, as without modes) |
| `bands_added: List[str]`, `bands_removed: List[str]` | sleeves (gear ids) given bands, or relieved of them, in place |
| `modes_added: List[str]`, `modes_removed: List[str]` | configurations made and deleted |
| `took_active_state: List[Tuple[str, str, str]]` | `(mode added, the user's item, its state there)`: each user mate's flag (`"on"`, `"suppressed"`) and each user component's state, read in the new configuration, which copied the active mode's — the plan's "said by name" |
| `not_resolved: List[Tuple[str, str, int]]` | `(gear, configuration, the state read)` for an added gear's component reading other than resolved there: a failure (C9), its facts for B's sentence |
| `flags_lost: List[Tuple[str, str, str]]` | `(mode removed, the user's mate, its flag there)` for each user mate whose flag in that configuration differed from the active mode's, read unshown before the delete (`mate_suppression`); a user component's state there is not readable unshown (no route, the review's must-fix 2) and is said generally ⟨C5⟩ |

Everything W9a returns stays (the user's items put, in error, kept). A failure part way says what was done, as every
Update does, nothing saved; `inserted`, `deleted` and the rest list only what was done.

## 7. The record

**Schema 8 gains nothing.** An added gear is a `ComponentEntry` (`name` from `inserted`, `frames` per mode from
`mode_placements`), its mates `MateEntry`s from the plan (`values`, `modes` as built), a new part a `PartEntry` with
its sidecar; a removed gear's `ComponentEntry` and `MateEntry`s are dropped, and its part's `PartEntry` too when no
gear of the revision uses that file (the file is never deleted) ⟨C6⟩; `modes` is the configurations after the Update in
the Modes sheet's order; bands ride in the sleeve's spec (sidecar schema 2), with the relief's features in its
recorded features. `user_work` is recorded as W9a records it. `finish_update` (B) writes all of it from the result, as
W8's finish writes frames and on-sets.

## 8. The findings each step reads (gates; a None refuses, naming it, before any write)

| Step | Reads | 2026 | 2024 |
|---|---|---|---|
| remove a gear | `COMPONENT_DELETE_ROUTE_ON_<year>` = `"select4-editdelete"`; `COMPONENT_DELETE_TAKES_ITS_MATES_ON_<year>` True; `COMPONENT_DELETE_DIALOG_ON_<year>` False; with modes `COMPONENT_DELETE_ROUTE_IN_EVERY_CONFIGURATION_ON_<year>` True | set (P1) | None until its run is reviewed |
| remove a gear with any user component present | `EXTERNAL_REFERENCES_READ_ON_<year>` (new, M4) | None (refuses) | None |
| add a gear (insert and mate in a reopened assembly) | `UPDATE_INSERTS_A_GEAR_ON_<year>` (new, M5 and M6) | None until the full build reads it clean ⟨C7⟩ | None |
| a coupling or sliding mesh made by Update; a gear mate remade with modes | `UPDATE_MAKES_MATES_WITH_MODES_ON_<year>` (new, M6); the remake also `GEAR_MATE_RATIO_ROUTE` "remake" | None ⟨C7⟩ | None |
| bands in place | `UPDATE_BANDS_IN_PLACE_ON_<year>` (new, M8) | None ⟨C7⟩ | None |
| a mode added; a mode removed | `UPDATE_ADDS_A_MODE_ON_<year>`, `UPDATE_REMOVES_A_MODE_ON_<year>` (new, M10) | None ⟨C7⟩ | None |
| the assembly's own entity | `ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_<year>` (read through `root_component`, `7e0d095`; nothing gates on it) | True | None |

The new findings are measured by W9c's full build (the plan's demonstration, `RangeBox` → `RangeBox_Fixed`, then a
mode added and one removed), patched True in the demonstration's own process for the measurement only, as W9a's
`nocarrier` was, and set in `findings.py` from its reviewed log. `swbuild.in_place_gates(in_place, revision, *,
modes=False, remakes=False) -> List[Tuple[str, str]]` (pure) returns `(step, finding)` for each gate not settled, for
A's refusal and B's footer; `step` is one of `STEP_REMOVE`, `STEP_ADD`, `STEP_MATES`, `STEP_BANDS`,
`STEP_MODE_ADD`, `STEP_MODE_REMOVE`.

## 9. The calls each step makes, and where each was measured

No step makes a call the app has not made; where a call is new in this context the context is named and §8 gates it.

| Step | Calls (`swcom.Session`) | Measured |
|---|---|---|
| new part | `build`'s whole part route | every build, 2026 and 2024 |
| bands given | `open_document`, `add_global_variable`, `ref_plane`, `open_sketch`, `sketch_circle`, `dimension` + `link_dimension`, `close_sketch`, `loft_cut`, `rebuild`, `feature_states` | the relief route: W9b's build of `RangeBox_Fixed` on 2026 (`W9B-INTERFACES.md` §4); on an opened part after the user's features: M8, the full build |
| bands taken away | `IFeature.SetSuppression2` on the relief's features (the member `set_mate_suppressed` calls on a mate) | on a part feature: M8, the full build ⟨C8⟩ |
| mode removed | `mate_suppression` (unshown flags, W8), `delete_configuration` (`DeleteConfiguration2`, the build's step 7) | W8's configurations probe (`API-LEDGER.md:138-139`), every W8 build; in a reopened assembly with the user's items: M10 |
| gear removed | `find_component`, `Select4(False, null, False)` + `EditDelete()`, `components`, `mate_states`, `find_mate` | P1 on 2026 (`w9c-probes-sw2026-20261117-2.log` :14-108); 2024 owed |
| mode added | `add_configuration` (`AddConfiguration2`), `rebuild` top-only, `set_mate_suppressed_in`, `mate_suppression`, `set_dimension_in`, `dimension_values` | W8's configurations probe and builds (`API-LEDGER.md:138-139`, `:220`, `:333`); in a reopened assembly with the user's items: M10 |
| gear added | `open_document` (its part), `add_component` (`AddComponent5`), `place_component`, `fix_component`, `add_mate` (`AddMate5`), `gear_mate_sense` and the remake with the other Flip, `link_dimension`, `set_mate_suppressed_in`, `mate_suppression`, `component_resolved` per mode shown | the build's own, both versions; into a reopened assembly with modes: S0, W9a's demonstration, m1 and s5 inserted and mated there with no dialog, every flag read back (the probes' review, "May rely on"); the new component's state per mode: M5 |
| coupling or sliding mesh made | `show_configuration`, `add_mate`, sense read, `set_mate_suppressed_in`, `mate_suppression` | the build's step 5 (W8, both versions); in a reopened assembly: M6 |
| gear mate remade with modes | `remake_gear_mate` (`MATE_DELETE_ROUTE`, `AddMate5`, `MATE_RENAME_ROUTE`), `set_mate_suppressed_in`, `mate_suppression`, the sense read per mode | W5's remake (both versions); with modes: M6 |
| the user's work read | W9a's reads, and `root_component` (the third component-find route's calls) | W9a; `root_component` read on 2026 in s5 (a), marking nothing |

What A adds to `swcom.Session`, each a wrapper over a member above, with `GetSaveFlag` read around it in the
demonstration: `delete_component(handle)` (P1's route), `suppress_feature(name, suppressed)` (a part feature, this
configuration) ⟨C8⟩. Nothing else.

## 10. Choices for the coordinator

- **⟨C1⟩** An added gear's `Placement.component` is `""` until the worker fills it; the alternative, B predicting
  SolidWorks' `Name2`, would guess. Recommended as written.
- **⟨C2⟩** The relief lands after the user's features in a part given bands in place, and `made` names it, so K3
  reads the user's features as before the app's relief. The alternative (insert the relief before the user's
  features, `EditRollback`) is a new call; not taken.
- **⟨C3⟩** The order of §4: removals before additions, modes before mates, everything new before W8's put and
  post-check. The alternative (additions first) would set flags in configurations about to be deleted and mate to
  bodies about to go.
- **⟨C4⟩** While M4 is unmeasured, a removal refuses whenever any component of the user's is in the assembly (the
  review's reading), not only a user *part*: a user sub-assembly can hold in-context references too.
- **⟨C5⟩** A mode removed loses the user's own states in that configuration; the worker says each user mate whose
  flag there differed from the active mode's (readable unshown) and the components generally. The alternative,
  refusing a mode removal while any user item's state there differs, would need the unshown component read W9d still
  owes.
- **⟨C6⟩** A removed gear's part entry leaves `parts` when no gear uses the file; the file stays on disk, never
  deleted by the app.
- **⟨C7⟩** Insert, mates made with modes, bands in place and modes added and removed are each gated by a new
  per-version finding, None until W9c's full build reads it clean (patched True in that run's process, as W9a's
  `nocarrier`). The alternative is W9b's: no gate, the build's own calls trusted and the full build the measurement.
  Recommended: the gates, since each writes into an assembly that holds the user's work.
- **⟨C8⟩** Bands taken away suppress only the `Relief` loft cut (its planes and sketches stay, unsuppressed and
  invisible), by `IFeature.SetSuppression2` on a part feature, a member the app calls on mates only. The band globals
  stay in the part, unread by the unbanded spec. Bands given again to a sleeve whose relief is suppressed unsuppress
  it and set the globals (a value Update) rather than add a second relief.
- **⟨C9⟩** An added gear's component reading anything but resolved in a mode is a failure (§0.3's STOP: a new
  component whose per-configuration state does not read back as set), not put right: setting a component's state per
  configuration has no measured route.
- **⟨C10⟩** A configuration of an added mode's name already in the assembly and not on record refuses as the user's
  (it is not on record, so not the app's to reuse); the build, by contrast, keeps a template's configuration of that
  name.
- **⟨C11⟩** Removing the record's first mode: the record's first mode becomes the next (`InPlace.first_mode`), said;
  SolidWorks opens the assembly in whatever configuration the user saves it in, so nothing is shown for it.
- **⟨C12⟩** `PROBLEM_MODE_SHOWING` cannot be foreseen by the footer; it is said after the press and recorded as W9a's
  refusals are, until the workbook changes or the user shows another mode.

**Rulings.** C1 to C12 were taken as written by the coordinator on 2026-11-17, and are the user's to overrule; with
them, the `_ON_2026` / `_ON_2024` pair on every W9c finding (`COMPONENT_STATE_PER_CONFIGURATION_ROUTE` included), and
an entity naming neither a top-level component nor the assembly's root read as not wholly read (a leaf of a user
sub-assembly still maps to its top-level component, pinned). C7 is the house rule: a per-version gate for each new
kind of write, None until the full build reads it clean. C8's suppress of a part feature sits behind
`UPDATE_BANDS_IN_PLACE`. C9 and C10 carry their sentences' facts in the result (`not_resolved`; the
`configuration` problem's `subjects`).

## 11. What each package writes against the fake, in parallel

- **B** builds `InPlace` in `classify` from the new and the recorded plans, moves §3's edits out of `structural`,
  calls `judge_in_place` and `in_place_gates` for the footer, writes §7 in `finish_update`, and the sentences from §6.
  It tests against the dataclasses and pure functions above, and against the fake once A's worker lands.
- **A** adds the shapes and pure functions first (one commit, so B can import them), then the steps of §4 in order,
  each with its fake support: the fake inserts a component (it already does for a build), deletes one with its mates
  and refuses to delete a user's, adds and deletes configurations (it does for the build), and suppresses a part
  feature; every user item written stays an `AssertionError`, as W9a's fake has it.
