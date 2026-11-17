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
  *"Update SolidWorks would delete the configuration L from RangeBox.SLDASM, and it is the configuration showing in
  SolidWorks, so nothing is changed; show another mode in SolidWorks and press Update SolidWorks again."* (as
  committed). It is read before the user's work, so that refusal's `UserWorkRefused.user_work` is **None** (nothing
  read): B keeps the record's inventory as it was. The gates' `unsettled` problems come with it.
- **`PROBLEM_UNSETTLED`** (W9a's kind) — a step whose finding gate (§8) is None or not the measured value on the
  version in use, naming the finding.
- **`PROBLEM_CONFIGURATION = "configuration"`** — a configuration of an added mode's name already in the assembly
  and not on record (it is not the app's to overwrite, §0.3; C10): named as the user's. *(Amended at package A's
  first commit: its own kind, not W9a's `PROBLEM_COMPONENT`.)*

Every `UserProblem` gains **`subjects: Tuple[str, ...] = ()`** (package A's first commit): the other things its
sentence names, so B can word it — the gear removed and the user's components (`references`), the gear removed
(`removed`), the mode (`mode showing`), the configuration (`configuration`), the finding (`unsettled` from an in-place
gate). `mates` keeps the user's mates named.

Faults (`BuildError`, "a fault in Gear Generator"), as committed (`_in_place_faults`, before anything is read): a
placement with `component == ""` and no `AddedGear`, or an `AddedGear` with no such placement; an `AddedGear` whose
ops do not insert its own handle exactly once, hold an op other than `AddGlobal`, `AddComponent`, `Place`, `Fix`,
`Unfix`, `Mate`, `LinkDimension`, or name a handle neither its own nor in `handles`; a `RemovedGear` that anchors a
gear (a `LockLink` with it first) or that stays, or whose mates are still in `motion.mates`; a `NewMate` on in no
configuration (ruling 9.1) or naming a handle not in its `handles`; a `BandChange` on a part not in `parts`, or with
nothing to make or suppress; a mode added not in `motion.configurations` or one removed still in it; a mate on record
left on in no mode once the modes removed are gone (ruling 9.1). B never sends these; A refuses them rather than act.

Also refused before any write (`BuildError`, said to the user): an added gear's new part whose file is already on
disk (*"… is already on disk, so Update SolidWorks would not build G5's new part over it, and nothing is changed;
move it away or delete it, then press Update SolidWorks again."*); and, on a gearbox with modes where
`UPDATE_MAKES_MATES_WITH_MODES_ON_<year>` is not True, a gear mate to be made again (ruling 9.16 kept, now naming the
finding: *"The gear mate G3 meshes G4 in T.SLDASM would have to be made again, and making a gear mate of a gearbox
with modes again has not been measured on this SolidWorks (findings.UPDATE_MAKES_MATES_WITH_MODES_ON_2026 is None),
so nothing is changed; build the gearbox again."*). A suppressed gear mate that may need remaking with modes keeps
W8's sentence.

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
| `mates_made: List[Tuple[str, Tuple[str, ...]]]` | `(mate name kept, the configurations it reads on in)`, every mate made: an added gear's, a new coupling or sliding mesh. `()` with no modes (its one configuration); with modes, `()` only for a mate made when the job stopped before its flags were set (listed so nothing made goes unsaid) |
| `remade_in_modes: List[str]` | gear mates made again on a gearbox with modes (also in `ratios`, as without modes) |
| `bands_added: List[str]`, `bands_removed: List[str]` | sleeves (gear ids) given bands, or relieved of them, in place |
| `modes_added: List[str]`, `modes_removed: List[str]` | configurations made and deleted |
| `took_active_state: List[Tuple[str, str, str]]` | `(mode added, the user's item, its state there)`: each user mate's flag (`"on"`, `"suppressed"`) and each user component's state, read in the new configuration, which copied the active mode's — the plan's "said by name" |
| `not_resolved: List[Tuple[str, str, int]]` | `(gear, configuration, the state read)` for an added gear's component reading other than resolved there: a failure (C9), its facts for B's sentence |
| `flags_lost: List[Tuple[str, str, str]]` | `(mode removed, the user's mate, its flag there)` for each user mate whose flag in that configuration differed from the active mode's, read unshown before the delete (`mate_suppression`); a user component's state there is not readable unshown (no route, the review's must-fix 2) and is said generally ⟨C5⟩ |

Everything W9a returns stays (the user's items put, in error, kept). A failure part way says what was done, as every
Update does, nothing saved; `inserted`, `deleted` and the rest list only what was done, and `skipped` names what was
not, in §4's order (*"adding the configuration 2L and putting the gears back and checking the assembly, because the
job stopped in TransferCase.SLDASM"*; a new part or a band part that fails: *"… and the assembly, because
Hub_m1.5_N30.SLDPRT failed"*). The configuration that was active is shown again. `log_lines()` gains a line for each
(`ok      inserted G5 as gear5-1`, `CHECK   your UserFlush was suppressed in N, deleted with it`, …).

## 7. The record

**Schema 9 (the coordinator's ruling on the review; W9b's was 8, W9d's carried items will be 10).** The gearbox gains
`left_globals` (`[document path, name]`, each global an in-place step of a press that stopped added and no press has
used since), `left_configurations` (each configuration such a press added for a mode, not yet a mode on record) and
`solidworks` (the SolidWorks revision its last Build or Update ran on, `[]` on older records); a user-work inventory
gains `refused_at` and `unread`, a problem `subjects`. `left_*` decides whether something in SolidWorks is the app's
or the user's, so a W9b-era app refuses a schema 9 record (as `store.py` refuses any newer one) and leaves it
byte-identical; schema 6, 7 and 8 records read as before (nothing left, no revision known) and are written forward as
9 on the next write. An added gear is a `ComponentEntry` (`name` from `inserted`, `frames` per mode from
`mode_placements`), its mates `MateEntry`s from the plan (`values`, `modes` as built), a new part a `PartEntry` with
its sidecar; a removed gear's `ComponentEntry` and `MateEntry`s are dropped, and its part's `PartEntry` too when no
gear of the revision uses that file (the file is never deleted) ⟨C6⟩; `modes` is the configurations after the Update in
the Modes sheet's order; bands ride in the sleeve's spec (sidecar schema 2), with the relief's features in its
recorded features. `user_work` is recorded as W9a records it. `finish_update` (B) writes all of it from the result, as
W8's finish writes frames and on-sets.

## 8. The findings each step reads (gates; a None refuses, naming it, before any write)

| Step | Reads | 2026 | 2024 |
|---|---|---|---|
| remove a gear | `COMPONENT_DELETE_ROUTE_ON_<year>` = `"select4-editdelete"`; `COMPONENT_DELETE_TAKES_ITS_MATES_ON_<year>` True; `COMPONENT_DELETE_DIALOG_ON_<year>` False; with modes `COMPONENT_DELETE_ROUTE_IN_EVERY_CONFIGURATION_ON_<year>` True | set (P1) | set (P1 on 2024, `6ca42da`) |
| remove a gear with any user component present | `EXTERNAL_REFERENCES_READ_ON_<year>` (new, M4) | None (refuses) | None |
| add a gear (insert and mate in a reopened assembly) | `UPDATE_INSERTS_A_GEAR_ON_<year>` (new, M5 and M6) | None until the full build reads it clean ⟨C7⟩ | None |
| a gear mate remade with modes (ruling 9.16 lifted) | `UPDATE_MAKES_MATES_WITH_MODES_ON_<year>` (new, M6); the remake also `GEAR_MATE_RATIO_ROUTE` "remake" | None ⟨C7⟩ | None |
| a coupling or sliding mesh newly made between components on record (`NewMate`) | `UPDATE_MAKES_A_NEW_COUPLING_ON_<year>` (split at the demonstration's ruling) | None | None |
| bands given (globals and the relief made after the user's features) | `UPDATE_BANDS_IN_PLACE_ON_<year>` (new, M8) | None ⟨C7⟩ | None |
| bands taken away (the Relief suppressed) or given back (`BandChange.back`: turned back on, no second relief) | `UPDATE_SUPPRESSES_THE_RELIEF_ON_<year>` (split at the demonstration's ruling) | None | None |
| a mode added; a mode removed | `UPDATE_ADDS_A_MODE_ON_<year>`, `UPDATE_REMOVES_A_MODE_ON_<year>` (new, M10) | None ⟨C7⟩ | None |
| the assembly's own entity | `ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_<year>` (read through `root_component`, `7e0d095`; nothing gates on it) | True | True (`6ca42da`) |

The new findings are measured by W9c's full build (the plan's demonstration, `RangeBox` → `RangeBox_Fixed`, then a
mode added and one removed), patched True in the demonstration's own process for the measurement only, as W9a's
`nocarrier` was, and set in `findings.py` from its reviewed log. `swbuild.in_place_gates(in_place, revision, *,
modes=False, remakes=False) -> List[Tuple[str, str]]` (pure) returns `(step, finding)` for each gate not settled, for
A's refusal and B's footer; `step` is one of `STEP_REMOVE`, `STEP_ADD`, `STEP_MATES`, `STEP_BANDS`,
`STEP_MODE_ADD`, `STEP_MODE_REMOVE`, and, since the split, `STEP_COUPLING` and `STEP_RELIEF`. An added gear's own
mates (its axis, along, lock or spline, and its per-mode couplings in `AddedGear.ops`) read `UPDATE_INSERTS_A_GEAR`
alone, as they always did: the Done-when's Hub measures them there.

**What the full build must measure, per gate** (each read on the user's SolidWorks, every write read back by the
worker's own calls, a watch on dialogs throughout; patched True only in that run's process):
- `UPDATE_INSERTS_A_GEAR`: in a saved, reopened assembly with modes and the user's items, a gear's part opened then
  `AddComponent5` (the `Name2` kept), `Place`, `Fix`/`Unfix`, its axis, along and lock or spline made by `add_mate`
  (a gear mate's sense read straight after, as the build's), `LinkDimension` on its Face Z; then every new mate's flag
  set and read back in every configuration, and the component's `GetSuppression2` read resolved in every mode shown
  (C9); the save flag of the parts and the user's components unmarked by the insert; no dialog.
- `UPDATE_MAKES_MATES_WITH_MODES`: a gear mate of a gearbox with modes given a new ratio by the remake route in a mode
  it is on in, its flags in every other configuration set and read back, its sense read in each mode shown; the
  user's mates' flags unchanged (read before and after).
- `UPDATE_MAKES_A_NEW_COUPLING` (no legal edit of the demonstration's fixtures reaches it; None after it unless a later
  run measures it through an Update): a coupling made between components on record in the first mode it is on in
  (shown), its sense read, its flags set elsewhere and read back.
- `UPDATE_BANDS_IN_PLACE`: on a built sleeve with a user feature after the app's, the band globals added and the
  relief's planes, sketches and loft cut made after it, the part rebuilt clean, the user's feature unchanged.
- `UPDATE_SUPPRESSES_THE_RELIEF` (the demonstration probes the suppression script-side; None after it unless a later
  run measures it through an Update): the relief suppressed by `suppress_feature` (`SetSuppression2` on a part
  feature, read back), the part rebuilt, the assembly's mates on that sleeve without error; and given back, the relief
  turned back on and the band globals set, no second relief.
- `UPDATE_ADDS_A_MODE`: `AddConfiguration2` from the mode showing in the reopened assembly, the handle rule (every
  handle fetched again), one top-only rebuild before any flag, every app mate's flag and slide value set there and
  read back, the user's mates' flags and components' states there read (they copy the active mode's); the mode
  showing again after.
- `UPDATE_REMOVES_A_MODE`: `DeleteConfiguration2` of a mode not showing, the user's mates' flags there read unshown
  first, the configuration gone after, every other configuration's flags and slide values unchanged.
- `EXTERNAL_REFERENCES_READ` (M4): a read of each user part's external references that names a reference into a
  gear's part (none is written yet; until it is, any user component refuses a removal, C4).

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

### From B (planning, `dda8795`): how classify fills the shapes, for A to rely on or object to

- **A new part is not in `parts`.** `UpdatePlan.parts` (and so `update_kwargs()["parts"]`) holds only parts on
  record; an added gear's new part is `AddedGear.build` alone (its path in `AddedGear.part`). §1's "a new part
  included once built" is read as the worker's: B never hands a `DocumentValues` for a file not yet on disk.
- **A sleeve given bands**: its `PartUpdate.variables` carry **no** band global (`Start Band`, `End Band`, `Relief
  Diameter`): they are `BandChange.ops`' `AddGlobal`s, added in the bands' step. `recorded` is the record's own pairs;
  `made` is the record's features plus the five relief features (C2). Taken away: `BandChange.ops` empty,
  `features == ("Relief",)` (C8), and the unbanded spec's variables, which hold no band global.
- **`configurations` after the Update**: the record's configurations in the record's order less those removed,
  then the added ones in Modes-sheet order (a reorder of Modes rows still changes nothing, W8 §9.9). `first_mode` is
  set only when the record's first is removed, and is then the first remaining. `recorded_by_mode` for an added mode
  is its wanted frames (nothing is on record there).
- **`RemovedGear.mates`**: every recorded mate whose `gears` hold the gear, per-mode couplings included; none of
  them is in `motion.mates`, `meshes` or `locks`.
- **`AddedGear.ops`** are filtered from `motion.motion_assembly_plan` over every gear (the layout `layout`, carriers
  `carrier<i>` in the record's order, gears `gear<index>` by Gears-sheet index): its `AddGlobal` (Face Z),
  `AddComponent`, `Place`, `Fix` and `Unfix`s, each `Mate` touching it, their `LinkDimension`s, then its per-mode
  mates' ops from `motion.modes_plan`. `handles` names every other handle those mates use with its `Name2` on record.
- **The footer's foresight** calls `judge_in_place` with the revision of the record's user-work inventory, or `()`
  when there is none, so every gated step then reads unsettled (`…_ON_?`); B words those itself by the finding's name
  (`ui_text.in_place_line`) and uses A's sentences for every other problem kind.

### From A (the worker, `95530bd`, `0ea9ae9` and after): what the worker relies on, and what changed after B started

- **Changed after B started (additive, defaults keep B's calls working):** `AddedGear.refs: Tuple[MateRef, ...] = ()`
  and `NewMate.ref: Optional[MateRef] = None` — the record's `MateRef` for each mate made (matched by name). The
  worker adds them to `motion.mates` once made, so the puts and post-checks judge them by kind: **B should fill them**
  (the `MateEntry`s B records for the mates made, as `MateRef`s). Without one a mate is judged for presence, flags and
  error only (a lock by its two gears), never for sense. A lock or spline an added gear makes needs its `MateRef` (or
  the `LockLink` in `motion.locks` reads as a lock with no mate on record, a fault). `UserProblem.subjects` and
  `PROBLEM_CONFIGURATION` (first commit); `GearboxUpdate.not_resolved`; the mode-showing refusal's `user_work` None
  (§5). All in this note above.
- **`motion.meshes`, `locks`, `carriers` hold the links of the gearbox after the Update**, new ones included (a mesh or
  lock with an added gear, a new coupling's `MeshLink` with its `modes`): the check phase leaves out any link to a gear
  not yet inserted, and the change phase puts each train whole with them. `recorded_meshes` holds only what is on
  record. A new coupling's `MeshLink` is needed for its sense in the post-checks.
- **`Unfix`** in `AddedGear.ops` is run (B's `dda8795` sends `Fix` then `Unfix`, as the build's plan has them).
- **A new part's path must not be on disk** before the press (refused, §5): after a failed press that built it, the
  file is there and the record does not list it. B may want the footer to say so; the worker never builds over it.
- **A tooth change on a gearbox with modes needs no `InPlace`**: `motion.ratios` with `motion.configurations` is
  remade by the worker where `UPDATE_MAKES_MATES_WITH_MODES_ON_<year>` is True, and refused naming it otherwise.
- **`workbook/gearbox.py`**: nothing the worker needs changed there; B need not touch it for package A.

### From B (the joining round): the round trip through the window's path, and what it found on A's side

B now fills `AddedGear.refs` (the record's `MateRef` for each of the added gear's mates, from `motion.mate_entry`, a
mate on in some modes with its on-set in the record's spelling) and `NewMate.ref`, and adds the new links to
`motion.meshes` and `motion.locks` (a lock's or spline's `LockLink`, a coupling's `MeshLink` with `k = σ_S·σ_D` and its
`modes`, a gear mate's from its teeth and sense). A tooth change with modes hands no `InPlace`. A new part whose file is
on disk though no record holds it is no longer structural: B says it in the footer before the press
(`UpdatePlan.new_parts_on_disk`), and the worker refuses it. `tests/test_workbook_in_place_round_trip.py` runs each
in-place kind through `classify` → `update_kwargs()` → `update_gearbox` on the fake → `finish_update` → the footer and
the result's sentence. Three faults on A's side, each a test marked xfail (strict) with its reason:

- **F1, an assembly global added again after a failed insert.** RangeBox → RangeBox_Fixed with `add_component` made
  to fail: the press built Hub's part, gave the bands and added the global `Hub Face Z`, then stopped. Once the user
  moves the new part's file away, the next press runs Hub's `AddGlobal` again and stops on *"Hub Face Z" is defined
  twice* (an unexpected `EquationError`) instead of going on or refusing by name. The global is the app's own name, so
  the worker could set it where it is already there with that name, or refuse saying so.
  (`test_after_an_insert_that_failed_and_the_part_moved_away_the_next_press_goes_on`)
- **F2, puts not judged when only modes change.** A mode added or removed on RangeBox_Fixed with the user's Sprocket-1
  locked to Sun: with nothing else changing, the check phase judges no put (`may_put` empty), then the change phase puts
  every train in every mode, Sun among them, and stops half way, after the configuration was added or deleted: *Update
  SolidWorks would now put Sun, which its check before any change found it would not put, and your work is on it, …*.
  Without the user's work the same presses go through. The check could judge the puts the change phase will make
  whenever modes are added or removed, or the change phase could leave alone the gears no mode change moves.
  (`test_a_mode_added_on_the_result_is_one_update_and_a_second_press_quiet[True]`, `…removed…[True]`)
- **F3, `skipped` names a step that was done.** When the job stops at an added gear's mate (or its state read after the
  insert), `result.inserted` lists Hub and `result.skipped` still begins *"inserting Hub and putting the gears back
  …"*, so the sentence reads *… inserted Hub as gear7-1 … It did not get to inserting Hub and putting the gears back
  …*. Once the component is in, the step left could be called *mating Hub* (no xfail: the sentence is A's wording).

**`swbuild.structural_change`'s bands sentence** (*Bands cannot be given to or taken from a built sleeve through its
values; …*) should stay. On a gearbox built to turn B now hands Update the sleeve's values without the band keys, so the
sentence is not reached there. It is still reached for a sleeve on a record with no gearbox built to turn (parts built
alone), where Update gives no bands in place.

**On a part built by a press that then failed** (the coordinator to rule): rather than the worker taking an unrecorded
file on disk as its own (it may be the user's), B could record a new part the failed press built and saved
(`result.built`) as a `PartEntry` with its `.gear.json`. The next `classify` then finds it on record and hands an
`AddedGear` with `build` None, which the worker already inserts as it does any part on record (the G5 path), with no
change on A's side. Until ruled, the record does not hold it and the footer names the file to move.

### From A (the joining round's faults): F1, F2 and F3 on the worker's side

**F2: what each step puts, and where the check judges it.** The rule from W9a holds: every put the change phase
makes on a body the user's work is on is judged before the first write (`_user_check`, then route (c1) carries the
user's locked components in each mode put, or the press refuses by name).

| §4 step | What it puts | Where the check judges it |
|---|---|---|
| 1. new parts built | nothing in the assembly | — |
| 2. values, bands | nothing itself; a part changed makes the assembly "changed" | with modes, as 3.7 below |
| 3.1 modes removed | nothing; the removed mode is never put | the user's work is judged over the modes after the Update (the removed mode left out) |
| 3.2 gears removed | nothing; the trains left are judged as they will stand (B leaves the gear's links out of `motion`) | `_may_put` on the trains after |
| 3.3 modes added | nothing itself (a copy of the mode showing) | each added mode is judged as the mode it copies: `work_in_added_modes(work, modes_added, active)` puts each user mate on in the active mode on in the new one too, and the added modes join the modes judged (K2's per-mode lock rule, route (c1)'s carry in every mode) |
| 3.4 gears added | the gear's `Place` only (no user work can be on it) | without modes, the trains as they stand after (`after`: the motion after, every placement, the added gear at its wanted frame) are judged by `_may_put` too, so a train that gains a gear and is then out of step (a turn the user gave it) is judged put; with modes, as 3.7 |
| 3.5 new couplings, 3.6 remakes | nothing themselves | with modes, as 3.7 |
| 3.7 W8's modes path | **every train whole in every mode** whenever anything changed (ruling 9.18): any `InPlace`, or a gear mate remade, always changes something | with modes, `changing` is now True for any `InPlace` and any remake, so every mated body is judged put (and a held or fixed gear only off its frame), in every mode, the added ones included |
| W7's path (no modes) | each train out of step, moved or remade, against the live frames | as before, plus the trains after an insert (3.4) |

So a modes-only press with the user's sprocket locked to Sun either carries it in each mode put (`carried` lists
every mode, the added one too) or, with a mate of another kind on a put body, refuses by name before the first write.
**For B's footer:** the foresight should judge the same way: call `swbuild.work_in_added_modes` on the recorded
inventory with the mode the press will copy (the record's active mode where it has one) before `judge_user_work`, or
the footer foresees *"your lock … suppressed in R"* where the press goes through. That is why B's
`test_a_mode_added_on_the_result_is_one_update_and_a_second_press_quiet[True]` still fails at its footer assertion,
while the press itself now goes through; `…removed…[True]` now passes.

**F1: a step repeated after a press that stopped.** Each looks for what the stopped press left, in the check phase,
before any write:
- *An assembly global an added gear adds* (`Hub Face Z`), or *a band global in a sleeve's part*: there at the value
  wanted, taken as done (not added again, not in `globals_added`); there at another value and named in the new
  **`InPlace.left`** (the record of the stopped press), set; otherwise the user's, refused by name with the new kind
  **`PROBLEM_GLOBAL = "global"`** (`subjects`: the global, the file): *'T.SLDASM already holds a global "G5 Face Z" = 35
  that Gear Generator did not add, where Update SolidWorks would add it as 40, so nothing is changed; rename or
  delete "G5 Face Z" in SolidWorks and press Update SolidWorks again.'*
- *A configuration an added mode names*: named in `InPlace.left`, gone on from (not added again; its flags and slide
  values set unshown and read back; listed in `modes_added`); otherwise still `PROBLEM_CONFIGURATION`.
- *A relief already made* in a sleeve to be given bands: refused by name (`BuildError`), *"Sleeve….SLDPRT already
  holds Relief Start Plane, the relief of bands an Update SolidWorks that stopped part way began to give it, so
  nothing is changed; delete it in SolidWorks and press Update SolidWorks again, or build the gearbox again."*
- *A mate made without its flags*: on record by B, set by the check's D10 per mode (goes on, as B's test has it).
- *A component inserted without its mates*: B sends Build again… by name; the worker has nothing of it to go on from
  (it is not in `InPlace`), consistent with that.
- **New on the result:** `GearboxUpdate.globals_added: List[(document path, name)]`, each global an in-place step
  added. **For B:** keep these names (and `modes_added`) on the record of a press that stopped, and hand them back
  as `InPlace.left` on the next press; without it a global left at the value wanted is still taken as done (B's F1
  test passes on that), but one left at another value refuses as the user's.
- **A part built by a press that then failed (the ruling):** `result.built` holds each new part's `BuildResult` in
  `InPlace.added` order (those with `build`), its `saved` path set once saved, whatever happened after; B has the
  spec in its own plan. Nothing more is needed from the worker.

**F3: `skipped` names only what was not done**, at the result's grain: once a gear is inserted its step becomes
*"making Hub's mates"*; once its mates are made, *"setting Hub's mates on in their modes and reading Hub back"* (with
no modes, *"reading Hub back"*); a mode added becomes *"setting every mate and slide in the configuration R"*; a new
coupling made, *"setting … on in its modes"*; a gear mate remade, the same. The last entry stays *"putting the gears
back and checking the assembly"*.

### From A (the demonstration's ruling): two gates split, and bands given back

- **Two more gate names for B's footer to word** (`in_place_gates` returns them with their steps):
  `UPDATE_MAKES_A_NEW_COUPLING_ON_<year>` (`STEP_COUPLING`, any `NewMate`) and `UPDATE_SUPPRESSES_THE_RELIEF_ON_<year>`
  (`STEP_RELIEF`, a `BandChange` taking bands away, or giving them back). Both None on both versions.
  `UPDATE_MAKES_MATES_WITH_MODES` now covers only a gear mate remade with modes; `UPDATE_BANDS_IN_PLACE` only bands
  given. The worker's own refusal sentence for each (`judge_in_place`'s `unsettled`) uses the step's words.
- **New: `BandChange.back: bool = False`** (with `add`): bands given back to a sleeve an earlier Update relieved of them.
  B sets it where the record shows the sleeve's relief made and then suppressed (its features hold the relief, its
  spec no bands). The worker then turns the relief's features back on (`suppress_feature(name, False)`), sets the band
  globals it finds (adds one that is gone), and makes no second relief; a relief no longer in the part refuses by name.
  A give that is not `back` finding the relief there still refuses by name (F1). **B's tests** that patch only the five
  gates before the split (`GATES` in `test_workbook_in_place_round_trip.py`) need the two new names where a coupling is
  made or bands are taken away.

### From B (the second joining round): what the record holds after each refusal and each stop, and one ask of A

**What B now sends.** The footer's foresight judges an added mode as the press does: `swbuild.work_in_added_modes` on
the recorded inventory, copying the gearbox's first mode (the record holds no mode showing; it is the mode the
assembly was built and saved in, and every Update shows it again). The gate sentence words the two new steps: *make a
coupling or sliding mesh between gears already in the assembly and set its flag in each mode*
(`UPDATE_MAKES_A_NEW_COUPLING`) and *suppress a sleeve's relief to take its bands away, or turn it back on to give them
back* (`UPDATE_SUPPRESSES_THE_RELIEF`). `make a mate` now reads *make a gear mate in an assembly with modes again …*,
and `bands in place` reads *give a built sleeve its bands in its own part*. `BandChange.back` is set where bands are
given to a sleeve whose `.gear.json` lists `Relief` (an earlier Update took the bands away, ruling C8). Its `ops` are
then the band globals alone, and its `features` are `("Relief",)`. `InPlace.left` is `GearboxRecord.left` (below).

**What the record holds, for the demonstration script to check:**
- **A refusal before any write raised as `UserWorkRefused`** (W9a's kinds, `unsettled` from an in-place gate,
  `removed`, `references`, `configuration`, `global`): `gearbox.user_work` is the inventory the press read, with
  `digest` the press's workbook, `revision` its SolidWorks, and `problems` every problem said. Each problem keeps its
  `kind`, `sentence`, `mates`, `values` and now `subjects` (`UserProblemEntry.subjects`, additive). Nothing else on
  the record changes. The footer says *Update SolidWorks refused at hh:mm, before changing anything: …* until the
  workbook changes or the next press reads again.
- **The mode-showing refusal** (`user_work` None, nothing of the user's read): the inventory on record is kept as it
  was (its `components`, `mates`, `features`, `carried`). Its `read_at` becomes the refusal's time, and `digest`,
  `revision` and `problems` (one, kind `mode showing`, `subjects` `["2H"]`) are the refusal's. With no inventory on
  record, an empty one carries them: `components`, `mates`, `features` and `carried` all `[]`, which claims nothing
  of the user's, and the next press reads it all. Either way it is said as every other refusal is.
- **A press that stopped part way**: the record holds what was done. Each new part built and saved (`result.built`)
  is a `PartEntry` (`gears` the gear it was built for) with its `.gear.json`, whether or not it was inserted.
  Bands given or taken are in the sleeve's spec. A gear inserted is a `ComponentEntry`, and each mate made is on
  record with its on-set. `gearbox.left` holds the names of each global the press added (`globals_added`) and each
  configuration it added (`modes_added`), as the app's leftovers. A configuration added by a press that stopped is
  not in `gearbox.modes` (it is in `left`); the next press adds it again and the worker goes on from it. The next
  press hands `left` as `InPlace.left` and the part as an `AddedGear` with `build` None. `left` is `[]` once a press
  runs to its end. A new part's file on disk that no record holds still refuses, with the footer's sentence before
  the press.
- **A gear inserted whose mates were not made** is Build again…, by name (B's sentence, as before).

**One ask of A (xfail `test_a_tooth_change_refused_by_its_gate_is_recorded_as_every_other_refusal_before_a_write`).**
The refusal of a gear mate remade with modes while `UPDATE_MAKES_MATES_WITH_MODES_ON_<year>` is not True is raised as
a `BuildError`. So the window shows it as a failure, the record keeps no refusal of it, and after the press it is said
differently from every other gate. Every other in-place gate is a `UserWorkRefused` with `PROBLEM_UNSETTLED`. B asks
the worker to raise this one the same way: `UserWorkRefused([UserProblem(PROBLEM_UNSETTLED, <its sentence>,
subjects=("UPDATE_MAKES_MATES_WITH_MODES_ON_2026",))], work)`, with the work it read (or None if raised before
reading). B records and says it then with no change. The other refusals before a write that are still `BuildError`s
can stay so. A new part's file already on disk is foreseen from the record and said before the press every time. A
relief already made, or one no longer in the part, is a state of the part the footer cannot read, and Build again…
is what its sentence offers.

### From A (the review's fix round, `W9C-REVIEW.md`)

- **The root read (should-fix 5).** `_read_user_work` now reads the root's `Name2` only when a mate entity names no
  top-level component (a mate on the assembly's own planes on 2026), once per press, and **never on an assembly with a
  lightweight component** (`GetSuppression2` 1 or 4 read by `components()`): there such an entity reads
  `UNREAD_ENTITY` (not wholly read; it refuses only where something is put, as W9a refuses an unread mate). W9a's
  call log is back to its own (`W9A_PUT_BACK_LOG` as before `7e0d095`, 149 calls). `Session.root_component(resolve)`
  takes the argument; the worker passes `True`, the only one measured (s5 (a), an all-resolved assembly, nothing
  marked); `False` was never called. **The demonstration must measure:** the root read on an assembly holding a
  lightweight user component, with each document's save flag and every component's `GetSuppression2` read before and
  after it, for `True` and for `False`; until then the worker never calls it there.
- **The fake as strict as measured (should-fix 8):** `delete_component` raises the epoch and a handle to the
  component deleted answers no more (found again by name, `ComponentGone`); `root_component(True)` on an assembly with
  a lightweight component resolves it and marks the assembly (`False` marks nothing); `delete_configuration` marks
  the assembly. Nothing in the worker failed under it.
- **Failures pinned (should-fix 6):** at `delete_configuration`, at `delete_component` (with a mode removed in the same
  press: the mode said done, the gear left for the next press, which takes it out alone), at `suppress_feature` (the
  job stops before the assembly), and at the remake with modes (`set_gear_ratio`); each with `skipped` and the next
  press.
- **Must-fix 1, the worker's half:** `swbuild.work_without_modes(work, modes_removed)` (pure) is the mirror of
  `work_in_added_modes`, for B's footer. `judge_user_work` judges a lock over the modes it is given alone, so a mode in
  a mate's `on` that is not among them (one being removed) counts for nothing, and `PROBLEM_LOCK_BY_MODE` can no longer
  be said with an empty side.
- **Schema:** no worker test pins the record's schema; nothing to change for 9.

### From B (the review's round): what the footer judges, what the record keeps, and three asks of A

**The footer judges what the worker will judge.** Gates are judged on the SolidWorks the record last saw: the
inventory's `revision`, else `GearboxRecord.solidworks` (the Build's or last Update's, schema 9). With neither (a
record from before schema 9 that no Update has read), each gate is judged over every version the findings know. If it
is set on all of them, nothing is foreseen stopping. If it is None on all of them, the refusal is foreseen as before.
If it is mixed, one sentence, neither red nor offering Build again…: *Whether Update SolidWorks can take a gear out of
the assembly depends on the SolidWorks in use: Gear Generator has been shown to do so on SolidWorks 2026, not yet on
SolidWorks 2024 (findings.COMPONENT_DELETE_ROUTE_ON_2024), and the press reads which it runs on before it changes
anything.* W9a's foresight of the user's work always has a version (its inventory's), so it shares nothing of this.
The recorded inventory is judged as the worker reads it:
- each mode removed is taken out of each mate's on-list first (`update.work_without_modes`, the mirror of
  `swbuild.work_in_added_modes`);
- an added mode is judged as a copy of each mode on record in turn, and only what every one of them foresees is
  foreseen. The summary says *add the mode R, a copy of the mode showing in SolidWorks when you press (your items
  there take that mode's state)*, naming no mode it cannot know.

A gear removed whose mates the inventory lists is judged by `judge_in_place` as the worker judges it. A gear added and
bands put nothing of the user's that the check does not judge in both.

**What the record keeps of a stopped press, and when it lets go** (the review's must-fix 2):
- **A global** (`left_globals`) stays until a press uses it, that is, a step of its in-place change names it and that
  step is done (the gear inserted, the bands given).
- **A configuration** (`left_configurations`) stays until a press that runs to its end adds the mode, which puts it in
  `modes`.
- **A part** built for a gear no component names stays as a `PartEntry` with that gear, until a press inserts the gear.
  It is used only while its file is on disk.
- While the workbook does not use them, the footer before the press and the result after it say each as the app's:
  *An Update SolidWorks that stopped part way left the global Hub Face Z and the part Hub_m1.25_N17.SLDPRT, which the
  workbook no longer uses: Update SolidWorks leaves them as they are and keeps them on record as its own, so a later
  press can use them again; delete them in SolidWorks if you no longer want them.* The result's sentence on
  configurations the app did not make leaves out a configuration `left_configurations` names.
- Nothing is taken away, so the worker needs no new call.

**The mode-showing refusal's record** (should-fix 3):
- *An inventory on record:* it keeps its own `read_at`; the refusal's time is `refused_at`, which the footer's
  *refused at hh:mm* reads.
- *No inventory on record:* the entry that carries the refusal is `unread` (`read_at` empty, nothing listed), and every
  foresight takes it as no inventory at all. So it never hides the user's components from a later C4 foresight; the
  press reads them.

**Ruling C6 is now kept.** A removed gear's `PartEntry` leaves `parts` when no gear of the revision uses its file, and
stays with the gears left when one does (HighDog and LowDog). The result says *took FIdler (gear11-1) out with 4 mates,
leaving its part Gear_m2_N20.SLDPRT on disk*. Before this, `finish_update` looked for the entry through
`current_parts()`, which no longer named it once its component was gone.

**Asks of A:**
1. `work_without_modes` belongs beside `work_in_added_modes` as a pure `swbuild` function. B uses its own
   (`workbook/update.py`) until it lands, and will switch.
2. `PROBLEM_LOCK_BY_MODE`'s sentence should never be built with an empty side (*suppressed in ,*). B no longer sends
   the case, but `_and([])` should not reach a sentence.
3. Taking a leftover configuration away: would the worker accept a name in `InPlace.modes_removed` that is in
   `left_configurations` but not among the record's modes (delete it by the mode-removal route, behind
   `UPDATE_REMOVES_A_MODE`)? Until then B leaves it and names it, as above.
