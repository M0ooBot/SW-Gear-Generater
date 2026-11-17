# W9d: Build again… carries the user's work — the interface between planning (B) and the worker (A)

Stage W9d of `ISSUE-1-PLAN.md`: §0.2 K5 (the user's answer), §0.3, §2.1 item 8, **§2.5**, §4 S5 and M9, §5 "W9d", and
*Changes after W9b, W9c's probes and the review of W9c's packages* ("Owed before W9d is designed"). Written before any
W9d code, at `64bec58`, against S5's and P2's readings on both versions (`W9C-PROBES.md`, `W9C-PROBES-REVIEW.md` and
its 2024 addendum, `probe/results/w9c-probes-sw2026-20261117-2.log`, `sw2024/w9c-probes-sw2024-20261117.log`, the
W9c block of `findings.py`), the installed SolidWorks API help (2024's `sldworksapi.chm`, decompiled as the macro
database's connect/12 says) and the macro database. **Revised** after its review (`W9D-INTERFACES-REVIEW.md`,
`f0eb516`) and the coordinator's rulings of 2026-11-17 (§12): every must-fix and should-fix is taken; §18 lists each
review point and where it went.

Package A is the worker (`swbuild.py`, `swcom.py`, the fake); package B is planning, the question, the result's
sentences, the record and the window (`workbook/update.py`, `workbook/gearbox.py`, `ui_text.py`, `store.py`,
`workbook_gui.py`, UI-DESIGN §9). §17 says who owns which file and in what order the work goes. This note fixes the
shapes the two share, where the carry sits in the Build again… job and in what order it runs, how each entity is found
and what of that is measured, the findings it reads, the record, every sentence, and the tests each package owes. A
change to a shape here is a stop-and-ask, as at W8, W9a and W9c. The choices the plan left open are §12, each now
ruled; the ones marked † change what K5 or §2.5 told the user and are the user's to overrule. §11 works through the
three things owed before W9d is designed; the probe that measures them is `probe/w9d_probes.py` (`W9D-PROBES.md`).

What is verified and what is not: a statement about the code cites the code at `64bec58`; a statement about SolidWorks
cites a committed log line, a `findings.py` constant or the API ledger; one that rests on the API help alone says so;
one that rests on nothing measured says *unmeasured*. Where the design forks on a probe result, both branches are
written.

## 1. The contract in one sentence

**A Build again… given a `Carry` reads the old assembly before it makes anything, builds, checks and saves the new
revision exactly as today, then inserts the user's components into the new assembly, remakes their mates where every
entity is found by a measured route, judges each cluster as it is made, and hands back a `CarryResult` that names
everything not carried with its reason; nothing is saved after the new assembly's first save, and nothing is written
to the old assembly or to any file of the user's.**

- `build_gearbox(..., before=old, carry=Carry(old=old, ...))`: `carry.old` **is** the `OldAssembly` passed as `before`
  (the same object). `carry=None` is W9a's Build again… call for call. `carry` given with `before` None, or with
  `carry.old is not before`, is a fault (`BuildError`, "a fault in Gear Generator").
- The carry never stops the build and never makes the build's own result depend on it (plan §2.5). Whatever the carry
  meets, `GearboxResult.ok` is what the build alone made it, and the record's new revision is written as today (D21).

## 2. The shapes (`swbuild`; B builds `Carry`, A fills the rest)

### 2.1 What B hands A

```python
@dataclass(frozen=True)
class CarryBody:
    """One body on record in the old assembly, and what stands for it in the new revision (plan §2.5, "Components map
    first")."""
    old: str                    # gear or carrier id as on record ("Sun", "Planet copy 2", "C carrier"); "layout"
    old_name: str               # its Name2 in the old assembly (ComponentEntry.name, CarrierEntry.component,
                                # GearboxRecord.layout_component)
    handle: str                 # the new plan's handle for it ("gear3", "carrier1", "layout"); "" when the new
                                # revision has no such body (a gear removed, a copy no longer there)
    same_file: bool             # the new component is an instance of the very file the old one was (a reused part;
                                # never the layout or a carrier, which are new files every revision)
    why_new: str = ""           # when not same_file and handle != "": B's phrase for why its file is new, as the
                                # sentences say it ("its Flank changed", "its Part name changed", "it had changes from
                                # Update SolidWorks that were not saved", "its layout part is new with every revision")
    names: Tuple[str, ...] = () # the app's own feature names in the NEW file (tier 2, D3): a part made new,
                                # swbuild.plan_features(its BuildPlan); a part reused, its sidecar's
                                # GearRecord.features; the layout and each carrier, layout.layout_features (and the
                                # carrier's own); never a fixed tuple
    old_names: Tuple[str, ...] = ()   # the app's own feature names in the OLD file, by the same rule from the record
                                # (the old part's sidecar features; the old layout's from its recorded shafts), so a
                                # feature of the user's in an app part is told from the app's

@dataclass(frozen=True)
class Carry:
    old: OldAssembly                      # W9a's, unchanged, and the very object passed as `before`
    bodies: Tuple[CarryBody, ...]         # every app body on record, the layout first, carriers, then gears
    modes: Tuple[str, ...] = ()           # the new revision's configurations, in Modes-sheet order (() with none)
    first: str = ""                       # the old record's first mode (GearboxRecord.modes[0]): what a mode new in
                                          # the revision takes its states from (D14)
    written_on: Tuple[int, ...] = ()      # GearboxRecord.solidworks of the old revision: the SolidWorks the last job
                                          # that wrote the old assembly ran on (schema 9), () when not known (§3 R.2)
    app_files: Tuple[str, ...] = ()       # every file the record names as the app's (every revision's parts, layout,
                                          # carriers and assemblies, `earlier` included): what may be open for the
                                          # not-open read (§3 R.2)
```

B fills `Carry` from the record and the `GearboxPlan` it is about to build (`workbook.update.carry_for(record, again,
old)`, beside W9a's `old_assembly`): planet copy *k* to copy *k*; a body the new plan has no handle for gets `handle
""`; `same_file` from `again.reuse` (a `PartReuse` whose path is the old component's part); `why_new` from the update
plan's structural reasons and `again.made_new` (`MadeNew.why`). The window passes it as `kwargs["carry"]` in
`_start_build` beside `before`, and only for a Build again… (W9a's `old_assembly` already decides that).

### 2.2 What A reads (crosses to B on the result)

```python
ENTITY_WHOLE    = "whole"     # a whole component (a lock's entity; ReferenceType2 0 or swSelCOMPONENTS)
ENTITY_FEATURE  = "feature"   # a reference feature by name (an axis, a plane that is not a base plane)
ENTITY_PLANE    = "plane"     # a base plane, by tree order ("plane1".."plane3"), never by its English name
ENTITY_ORIGIN   = "origin"    # an origin point: never read as a mate entity by any run, so WHY_UNMEASURED (§4.2)
ENTITY_FACE, ENTITY_EDGE, ENTITY_VERTEX = "face", "edge", "vertex"
ENTITY_UNREAD   = "unread"
# The kind is told by IMateEntity2.ReferenceType2 (m1's and S5's measured read, swSelectType_e read from swconst.tlb:
# swSelFACES, swSelEDGES, swSelVERTICES, swSelDATUMAXES, swSelDATUMPLANES, swSelCOMPONENTS, swSelDATUMPOINTS, 0), the
# reference's GetTypeName2 only to name a feature; never by GetSurface/GetCurve in the inventory's read (D5).

@dataclass(frozen=True)
class OldEntity:
    what: str                   # APP, LAYOUT, ASSEMBLY, USER or UNREAD_ENTITY (W9a's words; a carrier is APP)
    owner: str                  # the gear or carrier id (APP), the top-level Name2 (USER), "" (LAYOUT, ASSEMBLY)
    kind: str                   # ENTITY_*
    feature: str = ""           # ENTITY_FEATURE: its name; ENTITY_PLANE: "plane<n>"; ENTITY_ORIGIN: "origin"
    leaf: str = ""              # inside a user sub-assembly: the leaf's Name2 path ("UserSub-1/P2Sprocket-1")
    reference: str = ""         # the part-level persistent reference, hex (tier 1); "" when not read or not needed
    select_type: int = UNREAD   # IMateEntity2.ReferenceType2 as read
    coaxial: Optional[bool] = None  # a face on an app gear: a cylinder or cone whose axis is the part's Gear Axis
                                # (CylinderParams of the part-level face, in part coordinates, against the line through
                                # the origin along Z, which every recipe's Gear Axis is: spur.py:804's Axis on planes 2
                                # and 3); None when not read (COAXIAL_FACE_READ unset, or not a face on an app gear)
    unread: str = ""            # why this entity, or its reference, could not be read (a sentence's clause)

@dataclass(frozen=True)
class OldMate:
    name: str
    type: int                   # swMateType_e (IMate2.Type)
    type_name: str              # GetTypeName2 ("MateCoincident", "MateLimitDistanceDim", …)
    alignment: int              # IMate2.Alignment
    flipped: bool               # IMate2.Flipped
    values: Tuple[Tuple[str, float], ...]   # the definition's numbers as read (Distance, Angle, MaximumDistance,
                                            # MinimumDistance, MaximumAngle, MinimumAngle, GearRatioNumerator,
                                            # GearRatioDenominator, Reverse and FlipDimension as 0/1), metres/radians
    entities: Tuple[OldEntity, ...]         # in MateEntity(i) order, as read (§10's remake turns it into a selection
                                            # order per kind)
    params: Tuple[Tuple[float, ...], ...] = ()   # each entity's EntityParams as read (a gear mate's sense, §4.3)
    on: Tuple[str, ...] = ()    # the old modes it is on in (UserMate.on's convention)
    code: int = 0               # GetErrorCode2 in the mode showing, before anything changed
    warning: bool = True
    whole: bool = True          # False: SolidWorks would not describe it wholly

@dataclass(frozen=True)
class OldComponent:
    name: str                   # Name2
    path: str                   # its file as SolidWorks names it
    kind: str                   # "part", "assembly", "" (UserComponentEntry.kind's rule)
    fixed: bool
    code: int
    state: int                  # GetSuppression2 in the mode showing
    frame: Optional[Frame9]     # its frame in the mode showing; None when it would not read (§5.3)
    configuration: str = ""     # IComponent2.ReferencedConfiguration (a get; REFERENCED_CONFIGURATION_READ), "" unread
    active_configuration: str = ""  # its document's active configuration as loaded (GetActiveConfiguration's Name),
                                    # what the app's insert takes by default
    suppressed_in: Optional[Tuple[str, ...]] = None   # the old modes it is suppressed in; None: not read per mode
                                                      # (only `state`, the mode showing's, is known; D2)
    virtual: bool = False       # a virtual component: "^" in its file name (§5.1), or IComponent2.IsVirtual once
                                # VIRTUAL_READ is set
    pattern_instance: Optional[bool] = None   # IComponent2.IsPatternInstance once PATTERN_INSTANCE_READ is set; None
                                              # unread (D12)
    on_disk: bool = True        # its file is on disk (os.path.isfile), not virtual

@dataclass
class OldWork:
    read_at: str                # store.now()'s stamp, when the read began
    assembly: str               # the old assembly's path
    how: str                    # OLD_OPEN ("open": read as it stands in the session), OLD_READ_ONLY ("read-only": opened
                                # by this job and closed unsaved after the read), or OLD_UNREAD ("unread": not read;
                                # `unread` says why: §3 R.2's conditions, a gate)
    active: str                 # the old mode showing ("" with no modes)
    modes: Tuple[str, ...]      # the old configurations on record, found by name
    components: List[OldComponent]
    mates: List[OldMate]        # every user mate (not on record), suppressed in every mode included
    app_frames: Tuple[Tuple[str, Frame9], ...]   # each old app body's frame in the mode showing (by CarryBody.old)
    states_route: str = ""      # what the per-mode states were read by: the finding's route, "shown read-only", or ""
                                # (not read: each component takes the mode showing's state, D2)
    marked: List[str] = field(default_factory=list)   # documents a read turned modified (GetSaveFlag False → True):
                                                      # §0.3's STOP; the carry then does nothing more
    left: List[str] = field(default_factory=list)     # documents open after the read that were not before it (R.7)
    unread: List[str] = field(default_factory=list)   # sentences: what could not be read, and why

    def user_work(self) -> UserWork: ...         # W9a's view of it, for GearboxResult.old_user_work as today
```

**`swbuild.UserMate` gains `entities: Tuple[Tuple[str, str, str, str], ...] = ()`** — per entity `(what, name, kind,
feature)`, W9a's `what` and `name` and §2.2's `kind` (by `ReferenceType2`) and `feature` — filled by A's
`_read_user_work` on every Update from W9d on (D5) and kept by B's finish as `UserMateEntry.entities` (§7). `touches`
stays as it is.

### 2.3 What A decides (pure, shared with B's foresight)

```python
CARRY_PART, CARRY_SUBASSEMBLY = "part", "sub-assembly"
WHY_KIND, WHY_UNMEASURED, WHY_PART_NEW, WHY_GONE = "kind", "unmeasured", "part new", "gone"
WHY_ASSEMBLY_FEATURE, WHY_NOT_CARRIED, WHY_UNREAD = "assembly feature", "component not carried", "unread"
WHY_LIGHTWEIGHT, WHY_NO_FILE, WHY_LEAF, WHY_NOT_FOUND = "lightweight", "no file", "leaf", "not found"
WHY_CONFIGURATION = "configuration"   # a component whose referenced configuration cannot be carried (D13)
WHY_NO_FRAME      = "no frame"        # a component suppressed in the mode showing whose frame would not read (§5.3)
WHY_DIFFERS       = "differs"         # made again, it read otherwise than it was (§10), so it was taken out again
WHY_OLD_UNREAD    = "old unread"      # the old assembly was not read (§3 R.2): every item
FELL_NEW_ERROR, FELL_OVER_DEFINED, FELL_TIE = "new error", "over-defined", "tie"

@dataclass(frozen=True)
class CarryNamed:
    item: str                   # the mate's or component's name in the old assembly
    what: str                   # "mate" or "component"
    why: str                    # WHY_*
    subjects: Tuple[str, ...] = ()   # in the slots of the table below, in that order, each a plain string

@dataclass(frozen=True)
class CarryPlanItem:            # one component to insert
    component: OldComponent
    anchor: str                 # the CarryBody.old it is placed against (§5.3), or "" (world frame)
    frame: Frame9               # where it goes in the new revision's first mode
    cluster: int

@dataclass(frozen=True)
class CarryMateItem:            # one mate to make again
    mate: OldMate
    cluster: int                # -1: a mate with no user component (between app bodies, the layout, the assembly)
    targets: Tuple[str, ...]    # per entity, in SELECTION order (§10), how it is found, in the session's reference
                                # grammar ("<handle>:Gear Axis", "<handle>:plane2", "asm:plane1", "<handle>" whole,
                                # "ref:<handle>:<kind>:<hex>" tier 1)
    ratio: Tuple[float, float] = (1.0, 1.0)   # a gear mate's AddMate5 ratio, first selection's first (§10)
    sense: int = 0              # a gear mate's sense to read back (+1 same way, −1 opposite; 0 no gear mate)

@dataclass(frozen=True)
class CarryPlan:
    components: Tuple[CarryPlanItem, ...]
    mates: Tuple[CarryMateItem, ...]
    named: Tuple[CarryNamed, ...]
    clusters: Tuple[Tuple[str, ...], ...]        # each cluster's components (old Name2s), in first-mate order
    gates: Tuple[Tuple[str, str], ...]           # (step, finding) for every gate not set, as in_place_gates

def plan_carry(work: OldWork, carry: Carry, revision: Sequence[int], *,
               new_frames: Mapping[str, Frame9] = {}) -> CarryPlan: ...   # new_frames keyed by CarryBody.old
```

**`subjects`, slot by slot** (each `CarryNamed.why` and each `CarryFallback.why`; B words them, §9.3):

| `why` | `subjects` |
|---|---|
| `kind` | (kind word,) — "width", "path", … |
| `unmeasured` | (what, finding, version) — what is a kind word ("concentric"), an entity kind ("face", "edge", "vertex", "origin"), "insert", "sub-assembly", "configuration", "gear mate on an app gear" or "leaf"; finding the full name with its year; version "2026" |
| `part new` | (gear id, why_new, entity kind, "bore" or "") — "bore" only where `coaxial` is True on a cylinder |
| `gone` | (what, name) — what is "gear" (a body with no handle), "shaft" (a layout or carrier feature the new file lacks: the shaft's id), "feature" (an app part's feature the new file lacks: its name) |
| `assembly feature` | (feature name,) |
| `component not carried` | (component Name2,) |
| `unread` | (why clause,) |
| `lightweight` | (component Name2,) |
| `no file` | (file name, "virtual" or "") |
| `leaf` | (sub-assembly Name2,) |
| `not found` | (entity kind, component Name2, file name) |
| `configuration` | (component Name2, its referenced configuration, its document's active one) |
| `no frame` | (component Name2, the mode showing) |
| `differs` | (what differed: "entities", "alignment", "ratio", "sense") |
| `old unread` | (why clause,) |
| `FELL_NEW_ERROR` | (mate, its code now, its code before, mode) |
| `FELL_OVER_DEFINED` | (mate,) — the mate AddMate5 answered 5 for, or "" when a component read over-defined |
| `FELL_TIE` | (gear id read not free, mode) |

`plan_carry` is pure. The worker calls it on the fresh `OldWork` and the new revision's frames; B's question calls it
on an `OldWork` made from the record's inventory (`workbook.update.recorded_old_work(record)`: no frames, no
definitions beyond what the inventory keeps, §7), with `new_frames` empty, to foresee what is carried and named. Where
the inventory cannot say (a schema 9 inventory has no entity kinds), the foresight says *may* (§9.1).

### 2.4 What A hands back

```python
@dataclass
class CarryResult:
    work: Optional[OldWork]                       # what was read; None only when the read raised (stopped says it);
                                                  # an old assembly not read is an OldWork with how OLD_UNREAD
    inserted: List[Tuple[str, str]] = ...         # (old Name2, Name2 SolidWorks kept in the new revision)
    states: List[Tuple[str, Tuple[str, ...]]] = ...   # (new Name2, the new modes it reads suppressed in, read back)
    remade: List[Tuple[str, str, Tuple[str, ...]]] = ...  # (old mate name, name kept, the new modes it reads on in)
    same_error: List[Tuple[str, int]] = ...       # remade mates back in the error they had before (carried, said)
    named: List[CarryNamed] = ...                 # everything not carried, the plan's and the carry's own
    fixed: List[CarryFallback] = ...              # the clusters that fell back (§6)
    moved: List[Tuple[str, str, float]] = ...     # (new Name2, mode, mm): off its pose in its anchor's frame (D7)
    clashes: List[Tuple[str, Clash]] = ...        # (mode, clash) naming a carried component (D8)
    marked_user: List[str] = ...                  # user documents SolidWorks reads modified after the carry (said)
    stopped: str = ""                             # a sentence when the carry stopped part way, or did nothing because
                                                  # R.6 found a mark or R.7 a document left open; else ""
    skipped: str = ""                             # what it did not get to, as W9c's skipped
    gates: List[Tuple[str, str]] = ...            # the gates that kept something from being carried
    unsaved: bool = False                         # anything was written into the new assembly (it is unsaved)

@dataclass(frozen=True)
class CarryFallback:
    components: Tuple[str, ...]   # new Name2s, fixed where they were placed
    deleted: Tuple[str, ...]      # the mates made again and deleted again (to app parts, the layout, carriers, the
                                  # assembly), each by its old name
    kept: Tuple[str, ...]         # its user-to-user mates, kept
    why: str                      # FELL_NEW_ERROR, FELL_OVER_DEFINED or FELL_TIE
    subjects: Tuple[str, ...] = ()   # as the table above
```

`GearboxResult` gains `carry: Optional[CarryResult] = None`. `old_user_work` and `old_read` stay (W9a's sentence is
still said when `carry` is None). `log_lines()` gains a line per item (`ok      carried Sprocket-1 as Sprocket-1`,
`ok      made UserLock1 again, on in H, N and L`, `CHECK   not carried: Concentric5 (part new)`, `FIXED   …`).

## 3. The order of the job, and where it sits

`swbuild.build_gearbox`, with the steps it has today in **bold**:

1. **The gates and the plans' checks** (`_gate`, `_modes_gate`, `_assembly_rebuild_gate`, …).
2. **R. The old assembly read**, before anything is made (D1). It replaces W9a's `_read_before` when `carry` is given
   and sits where it does today (`swbuild.py:3439`), in its own build bracket (`begin_build` / `end_build`):
   1. **the session's documents** (`documents()`): listed, each one's `GetSaveFlag` read; that list is the job's
      `open_before` from here on (today `_refuse_paths` reads it after `_read_before`, `:3457`; with a carry it is the
      list read here, so nothing R opens counts as open before); every user file R will read and the old assembly's
      file: their times (`mtime`, injected as today);
   2. **open or not**: *open in the session* (`use_open_document`): read as it stands, never activated, never shown in
      another mode. *Not open*: opened `OpenDoc6(path, assembly, Silent | ReadOnly)` only when **all** of these hold
      (must-fix 2, as ruled), else `how = OLD_UNREAD` and nothing is read (§9.1 says so before the press):
      - the record says the old assembly was last written by a job on the running major version (`Carry.written_on`,
        `GearboxRecord.solidworks`); and, once `FILE_VERSION_READ_ON_<year>` is set, the file's own last saved version
        (`ISldWorks.VersionHistory(path)`, read closed) is the running one too (a save on the other SolidWorks after
        the last job is otherwise not seen; §11.2);
      - no document is open in the session but those `Carry.app_files` names;
      - `OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN_ON_<year>` is that route (set on both) and
        `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_<year>` is True (the close of a read-only document, shown or not, under no
        dialog: GOTCHAS §100's CAM box follows the file's version);
   3. the components (`components()`), each one's frame in the mode showing (`find_component` with `lightweight_ok`,
      `component_frame`), referenced configuration and its document's active configuration (gated,
      `REFERENCED_CONFIGURATION_READ`), virtual (§5.1), pattern instance (gated, D12), on disk; the app bodies' frames;
   4. the states per mode by the route `COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_<year>` names (§11.1); when it is
      None and this job opened the document read-only (all of R.2's conditions held), by showing each mode in that
      read-only document; else not read (`suppressed_in` None, D2 †);
   5. every user mate's definition (`Session.mate_definition`, §10), every entity classified by `ReferenceType2` (§4),
      tier 1's part-level references read through the component (§4.1), a face on an app gear's `coaxial` (gated,
      `COAXIAL_FACE_READ`); the root's `Name2` read as W9c's `_read_user_work` has it (never on an assembly with a
      lightweight component; the probe does not license more, §11.5);
   6. `GetSaveFlag` of every document again: any turned on is `OldWork.marked` (§0.3's STOP: the carry does nothing
      more, `stopped` says so, the build goes on);
   7. *opened read-only by this job*: closed unsaved (`close_unsaved`, `QuitDoc`); then the session's documents listed
      again: any not in R.1's list is `OldWork.left`, the carry does nothing more and `stopped` says so (should-fix 8).
3. **The new parts, the layout part, the carrier parts, the assembly built, mate-checked and saved**
   (`_build_gearbox_body`, `SaveAs3` with option 1). **The interference per mode** (`_modes_interference`), the
   assembly left in its first mode. *Nothing below runs unless the assembly saved (`result.assembly.ok` and
   `saved`).*
4. **C. The carry** (`_carry`, its own step `Step(STAGE_CARRY, stem)`, inside the change phase's bracket as W9c's
   in-place steps are), in this order, each failure stopping the carry with `stopped` and `skipped` set and every
   later step not run; nothing saved, ever:
   1. the new revision's frames read (`find_component`, `component_frame` per handle in `result.components`), keyed by
      `CarryBody.old`; then `plan_carry(work, carry, revision, new_frames=…)`;
   2. the gates: a step whose finding is not set leaves its items named (`WHY_UNMEASURED`), never refuses the build;
   3. each carried component's file opened (`open_document`; a sub-assembly by `SUBASSEMBLY_INSERT_ROUTE`, §11.3),
      then the new assembly made the build document again by the route W9c's `AddedGear` insert uses;
   4. each inserted (`add_component` at its frame's origin; in its referenced configuration where it differs from its
      document's active one, D13: `AddComponent5(path, 0, "", True, configuration, …)`), its referenced configuration
      read back (another is not carried: the component deleted again by `delete_component`, the job's own, and named
      `WHY_CONFIGURATION`), placed (`place_component`), fixed where it was fixed (`fix_component`); first mode showing;
   5. **the states, in every mode** (should-fix 4): each mode shown in turn, every carried component set to its wanted
      state there (`set_component_suppressed(handle, suppressed)`, suppressed or resolved) and read back; the first
      mode shown again; a state that does not read back as set is a failure (§0.3: "a new component … whose
      per-configuration state does not read back as set");
   6. **the mates, cluster by cluster** in `CarryPlan` order (must-fix 1, D6 ruled), each cluster:
      1. its mates made: targets selected in selection order (§10), `remake_mate` from the definition, renamed to the
         old name (`MATE_RENAME_ROUTE`; a name taken keeps SolidWorks' name, D15), the status kept; the remade mate's
         entities, alignment, ratio and sense read back against the old (§10; `WHY_DIFFERS`: deleted again, named);
         its flags set in every new mode from `on` mapped by name (`set_mate_suppressed_in`) and read back
         (`mate_suppression`), a mode where one of its components is suppressed left as SolidWorks has it and not
         judged (the probe reads what SolidWorks does there, §11.5);
      2. one top-only rebuild (`rebuild(kind=ASSEMBLY_TRAIN)`);
      3. **judged in the mode showing** (the new revision's first mode): each of its remade mates' codes; its
         components' constrained status; `_free_to_turn`'s read on the train(s) its mates touch, as the mode showing
         joins them. A fallback case (§6) falls this cluster back at once. When every one of the cluster's mates has
         the same flag in every mode, this read decides every mode (K2's rule, measured by S0, `USER_TIE_READ_PER_
         MODE_ON_<year>`); a cluster whose mates' flags differ by mode is read again in those modes in 4.7's shows;
   7. **the post-check, with the carried mates on** (§6): every mode shown in turn, the build's own per-mode check on
      the app's bodies and mates, each remade mate's code and flag, each carried component's state and its pose in its
      anchor's frame (D7), the mode-dependent clusters judged there, the interference read once more with clashes
      naming a carried component (D8); the first mode shown again;
   8. `GetSaveFlag` of every user document read (`marked_user`) and every old and user file's time read again (a
      change is §0.3's STOP, said, never "fixed").

**Never written:** the old assembly (no show, flag, value, put, mate, insert, delete, save, close of a document the user
had open); any user file (no save; its document may be opened, and is read, as §11.2 and §11.3 say); the new assembly
after its first save (no `Save3`, no `SaveAs3`). **Written:** only the new assembly in memory, after its save: the
inserts, the states, the mates, the fallbacks — §0.3's W9d exception.

A carry that stops leaves what it made in the new assembly, unsaved; the saved file is the build's. `CarryResult`
names what was done, what was not (`skipped`, at W9c's grain: *"making Sprocket-4's mates again and checking the
assembly"*), and everything not carried.

## 4. How each entity is found (§2.5's four tiers), against what was measured

### 4.1 Tier 1 — a file both revisions use

Every user component (the same file, inserted again) and every app part `same_file`. The entity's part-level
persistent reference is read in the old instance's part (`IComponent2.GetModelDoc2`, then the part's
`Extension.GetPersistReference3`) and resolved in the new instance's part (`GetObjectByPersistReference3`), then carried
into the new assembly through the new component (`IComponent2.GetCorresponding`) and selected (`Select4`, mark 1). The
resolved entity's kind must be the read one's; another kind is §0.3's STOP.

*On the open path* the part's document stays loaded from the read to the carry, so the reference resolves against the
document it was read from. *On the not-open path* it does not (should-fix 9): R reads the reference in the read-only
load, closes it, and the carry resolves it in a fresh load. Persistent references exist to survive a reload, but no run
has resolved one after one: the not-open path's tier 1, for every kind, rests on `PERSIST_REFERENCE_SURVIVES_RELOAD_ON_
<year>` (the probe's `faces` (d)); while it is None, tier 1 entities on the not-open path are `WHY_UNMEASURED`.

| Entity on a file both use | 2026 | 2024 | Finding |
|---|---|---|---|
| a reference axis or plane (user part, the layout; Front, Top, Right, Gear Axis, Input Axis) | **measured**: 13 read, resolved, 10 mates remade equal (`w9c…-2.log` :265-279) | **measured** (`w9c24` :266-280) | `PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES_ON_<year>` (set) |
| a face | not measured | not measured | `PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_<year>` (the W9d probe) |
| an edge | not measured | not measured | `PERSIST_REFERENCE_ROUTE_FOR_EDGES_ON_<year>` (the W9d probe) |
| a vertex | not measured | not measured | `PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_<year>` (None; nothing in W9d sets it) |
| any, after a reload (the not-open path) | not measured | not measured | `PERSIST_REFERENCE_SURVIVES_RELOAD_ON_<year>` (the W9d probe) |
| a whole component (a lock) | **measured** (tier 3) | **measured** | — |

The route from the **assembly-context** entity (`IMateEntity2.Reference`) to the part-level one is not measured: for a
feature S5 found it by name in the part (`FeatureByName`). For a face or edge the API help gives
`IModelDocExtension.GetCorrespondingEntity2` ("the entity in the underlying part … that corresponds to the specified
entity in this assembly", SOLIDWORKS 2018 and later; never called by the app or the macro database); the probe
measures it beside handing the assembly entity straight to the part's `GetPersistReference3` (§11.4), each route per
entity kind.

### 4.2 Tier 2 — what the app names, and base planes by tree order

On the layout part and each carrier part (new files every revision) and on an app gear part, same file or new (D3): a
reference feature the app names (`CarryBody.names`) by name; a base plane by its tree order (`plane1`..`plane3`, read
from the part, never assumed: `_component_ref`, `swcom.py:2136-2138`). The target is the session's reference grammar
the build mates by (`"<handle>:Input Axis"`, `"<handle>:plane2"`; `"asm:plane1"` for the assembly's own planes). A name
the new file does not hold is `WHY_GONE` (a shaft removed; `Mid Plane` and `Profile Plane` exist only on helical and
herringbone parts, so a mate on one of a part made spur is gone). A feature of the user's in an app part (not in
`old_names`, not a base plane) is tier 1 on a same file and `WHY_PART_NEW` on a new one.

| Entity | 2026 | 2024 |
|---|---|---|
| the layout's axis by name | **measured** (S5 c: UserAxis1, 2, 4, 6) | **measured** |
| the layout's base plane | **measured** (UserAngle4 to the layout's Right Plane in S5; the app selects `lay:plane3` by order in W9a's setup) | **measured** |
| the assembly's own plane by tree order | **measured** (UserAsm6, `asm:plane1`) | **measured** |
| a carrier's axis or plane by name | the app's own selection (W7's builds), never in a carry | the same |
| an app gear's `Gear Axis` by name | the app's own selection (every build's mates); in a carry, not measured | the same |
| an origin point (a component's or the assembly's) | **never read as a mate entity**: `WHY_UNMEASURED` (`ORIGIN_ENTITY_READ_ON_<year>`, None; should-fix 6) | the same |
| a feature the user made in the old assembly (a sketch, a plane) | `WHY_ASSEMBLY_FEATURE` (an `ASSEMBLY` entity whose feature is not one of its first three planes) | the same |

The assembly's own entity names the root component on both versions (`ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_<year>`
True); W9c's `_read_user_work` maps it, and reads the root never on an assembly with a lightweight component, where
such an entity is `UNREAD` and its mate `WHY_UNREAD`.

### 4.3 Tier 3 — locks by whole component, and a user gear mate on an app gear

A **lock**'s entities are whole components (ReferenceType2 0, S5 (a): UserLock1–3), found through the component map:
a user component by its new instance, an app body by `CarryBody.handle`, selected whole (`Select4` with a mark-1 select
data, the app's lock route). A body with no handle is `WHY_GONE`.

**A user gear mate's entity on an app gear** (contradiction 1 †, ruled): a gear mate takes rotational entities only (an
axis, a cylindrical or conical face, a circular edge; m1's read two axes, ReferenceType2 5, `Gear Axis`,
`w9c…-2.log:156`). Its entity on an app gear is taken as that gear's `Gear Axis` in the new part (by name, tier 2),
whether the old entity was the gear's `Gear Axis` or a face or edge of it, **provided it is coaxial**: every rotational
face the app makes on a gear (a bore, a relief) is coaxial with `Gear Axis` by construction, but a face of a feature
the user cut into the gear part (W9a's keyway is an off-axis Ø 3 hole) is not. So: an axis named `Gear Axis`, or a
face or edge with `coaxial` True, is taken as `Gear Axis`; `coaxial` False or None is `WHY_PART_NEW` on a part made new
and tier 1 on a same file. The other side goes by its own tier. This keeps K5's "a gear mate is found through the
component". Behind `CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_<year>`, which M9 sets only with the remade mate's ratio and sense
read back right (§10).

### 4.4 Tier 4 — a face, edge or vertex of an app part made new

Never re-found (ruled, K5), but for §4.3's gear-mate rule. `WHY_PART_NEW`, subjects (gear, why_new, entity kind,
"bore"): *"Concentric5 was on Sun's bore, and Sun's part is new because its Flank changed; it was not made again."*
"bore" only where `coaxial` is True on a cylinder; otherwise *a face of Sun*, *an edge of Sun*.

### 4.5 Mate kinds: carried, named, and measured

§2.5's carried kinds are coincident, concentric, parallel, perpendicular, tangent, distance, angle (with limits),
lock and gear; every other kind is `WHY_KIND`. A carried kind is remade only when its word is in
`CARRY_REMAKE_KINDS_ON_<year>` (D4), else `WHY_UNMEASURED`.

| Kind | Definition read (m1, S5 a) | Remade from its definition | Into a configured assembly, flags per mode |
|---|---|---|---|
| coincident (axis–axis, plane–plane) | both versions | both (S5 c, ×5) | not measured |
| distance (plane–plane) | both | both (×2) | not measured |
| angle (plane–plane) | both | both (×1) | not measured |
| lock | both | both (×3) | not measured |
| concentric (face–axis) | both (m1) | not measured | not measured |
| limit distance, limit angle | both (m1; range in Maximum/Minimum) | not measured | not measured |
| gear (axis–axis, user on app gear) | both (m1) | not measured | not measured |
| parallel | **never read** (the W9d probe makes and remakes one) | not measured | not measured |
| perpendicular, tangent | **never read** | not measured | not measured |
| width | both (m1; made only with the tab at mark 16) | — named (`WHY_KIND`) | — |
| path, slot, symmetric, profile-centre, cam, hinge, rack-and-pinion, screw, universal joint, belt/chain | — | — named | — |
| a flipped mate (any kind) | not read flipped | not measured | — |

"Into a configured assembly, flags per mode" is what the carry does. W9c sets and reads back flags this way for the
app's own mates (J10's discipline, both versions), and W9a's setup did it for user mates made by the app's `add_mate`
in a configured assembly. For a mate remade from a user's definition it is M9's to measure.

## 5. The read's rules, the states per mode, and placement

### 5.1 Components

- **Carried**: a top-level user component whose file is on disk and not virtual, a part or (gated, §11.3) a
  sub-assembly, with its file, **its referenced configuration** (must-fix 4, D13 ruled), fixed or floating, and its
  state per mode.
- **Its referenced configuration**: read as `IComponent2.ReferencedConfiguration` (a get; gated
  `REFERENCED_CONFIGURATION_READ`, the probe's `faces` (b)). Where it equals its document's active configuration, the
  insert the app has today carries it. Where it differs, the insert passes it (`AddComponent5`'s
  `UseConfigForPartReferences` True and `ExistingConfigName`: the same member, arguments the app has not passed) while
  `CARRY_INSERTS_IN_A_CONFIGURATION_ON_<year>` is True; else, or where it would not read, the component is named
  (`WHY_CONFIGURATION`), never carried in another. After the insert it is read back; another is deleted again and
  named.
- **Named**: a file not on disk (`WHY_NO_FILE`); a **virtual component** (`WHY_NO_FILE`, "virtual"), told by a `^` in
  its file name (should-fix 7): the macro database has a virtual part's path in the session's temporary folder
  (assemblies/12, "a virtual part (whose path is in the session's temporary folder)"), so `os.path.isfile` reads True
  and must not decide; the `^` name is reading/01's rule for a virtual component's name. Unmeasured for a component's
  path read by `_component_path`; `IComponent2.IsVirtual` (a documented get) decides once `VIRTUAL_READ_ON_<year>` is
  set (the probe reads it negative only; no fixture has a virtual component).
- **Said, not read**: a sub-assembly comes over rigid; display states and appearances set in the assembly are not
  carried; a component pattern is not carried and an instance comes over as a component of its own (D12 †); a part of
  the user's with in-context references to the old assembly's parts still refers to them (M4 unmeasured, said once
  whenever a user part is carried).

### 5.2 States per mode

- Old mode → new mode by name, case aside. A mode of the new revision the old assembly has not takes the old record's
  first mode's state (`Carry.first`, D14), said. An old mode the new revision has not (removed, or renamed: a renamed
  Modes row is one of the edits that reach Build again…, `update.py:1508-1512`, so this is a central case) loses its
  states, said plainly.
- With no clean unshown route and the old assembly open (D2 †), each component takes the mode showing's state in every
  mode, said once for all.
- A lightweight component (state 1 or 4 in the mode showing) is inserted resolved and never set lightweight (D10): the
  user's next save of the new assembly must not meet SOLIDWORKS CAM's box.

### 5.3 Placement

- **Clusters**: the user's components joined through user mates whose entities are on two or more user components
  (user–user mates), connected components of that graph, numbered in first-mate order; a component no user–user mate
  joins is a cluster of its own; a user mate with no user component (between app bodies, the layout, the assembly) is
  cluster −1, one mate per cluster, and falls back alone.
- **Anchor**, per component (D20, should-fix 2): its own user lock to an app body first; then its cluster's anchor
  (the first user lock in mate order from one of the cluster's components to an app body; then any other user mate to
  an app body; then the layout or the assembly, the world frame). A body with no handle in the new revision is passed
  over. None: the world frame.
- **Frame**: `swbuild._carry_frame(old(anchor), new(anchor), old(component))`, the code route (c1) puts by
  (`swbuild.py:5384`), the anchor's new frame read in the new revision's first mode and its old one in the old mode
  showing; the world frame: `old(component)` unchanged. It keeps the component's pose **relative to its anchor**: a
  sprocket that stood at θ to a Sun the user had turned 37° goes in at θ to the new Sun, so 37° less in the world than
  it stood (worked: old Sun Rz(37°) at (0, 0, 10), the sprocket Rz(37° + θ) at (0, 0, 20), new Sun Rz(0) at
  (0, 0, 10.5) → the sprocket Rz(θ) at (0, 0, 20.5)).
- **A component suppressed in the mode showing** (should-fix 3): its frame is read as any other's
  (`component_frame`; whether a suppressed component's transform reads is unmeasured, M9 holds one); if it reads, it
  is placed by the rules above; if not, `WHY_NO_FRAME`, and the question, which knows its state from the record, says
  to show a mode where it is resolved before pressing.
- **The mode the components stand in**: placed once, in the new revision's first mode, from the old mode showing; a
  floating one that stood elsewhere in another mode stands where it stood in the mode showing (plan §2.5), said
  whenever the gearbox has modes and a floating component is carried (§9.2).

## 6. Clusters, the fallback and the post-check

- **Made**: every mate whose entities are all found and whose kind and entity kinds are measured (§4) is remade;
  every other is named. The components stay floating where placed (or fixed): an under-defined component stays put,
  and leaving a mate out over-defines nothing.
- **The same error**: a remade mate that reads, in a mode, the error code it read in the old assembly's mode showing
  is carried as it was (`same_error`, said) and not counted against its cluster. Its old code was read in one mode
  only, so a mate in error before in another mode falls back as a new error there: conservative, said in the sentence
  as "which it did not in H, the mode RangeBox.SLDASM showed".
- **A cluster falls back in the plan's three cases, and only these, and only that cluster** (must-fix 1, D6 ruled
  against the first draft):
  1. `FELL_NEW_ERROR` — one of its remade mates reads, in a mode where it is on, an error code it did not have before;
  2. `FELL_OVER_DEFINED` — `AddMate5` answered `ADD_MATE_OVER_DEFINED` (5) for one of its mates, or one of its
     components reads `COMPONENT_OVER_DEFINED` after its rebuild;
  3. `FELL_TIE` — with its mates just made, `_free_to_turn` reads a gear not free (any status but under-defined) on a
     train its mates touch, which was free before this cluster's mates (the build's post-check, then each earlier
     cluster's judgement, says so). Read in the mode showing; that read decides every mode when each of the cluster's
     mates has the same flag in every mode (K2's rule, `USER_TIE_READ_PER_MODE_ON_<year>`, measured); else that
     cluster is read again in each mode where its flags differ, in 4.7's shows, and falls back there.
- **The fallback**: the cluster's remade mates to app bodies, the layout, carriers and the assembly are deleted
  (`MATE_DELETE_ROUTE`, the job's own just-made mates, by the name kept); its user-to-user mates are kept; each of its
  components is put back where it was placed (`place_component`) and fixed (`fix_component`) (D9). The train is read
  again; still not free, the carry stops (`stopped`), naming the mode and what still reads wrong, and leaves the new
  assembly as it is, unsaved. Cluster −1's mate is deleted alone.
- **The post-check with the carried mates on**: per mode, shown in Modes order then the first again: the build's own
  per-mode check on the app's bodies and mates, unchanged; each remade mate's code and flag; each carried component's
  state; each carried component's pose in its anchor's frame (`swbuild._relative(anchor, component)`, should-fix 1)
  against what it was when placed, to the tolerance the build's post-check holds a gear's origin to (`POSE_TOLERANCE`,
  `swbuild.py:1537`, as `_modes_post_check` uses it at `:5095`): off is `moved`, said (D7); the clusters whose mates'
  flags differ by mode judged there; the interference, with clashes naming a carried component (D8). The app's own
  check failing for a reason no cluster explains (an app mate in error with no carried mate on its bodies) is the
  build's own failure as today, laid to the app, and the carry stops.
- **What M9 can show**: the tied cluster (`FELL_TIE`). `FELL_NEW_ERROR` and `FELL_OVER_DEFINED` are shown on the fake
  only (no fixture provokes them without contriving a broken mate).

## 7. The record: schema 10

`store.LINK_SCHEMA_VERSION = 10` (`_W9C_LINK_SCHEMA = 9`). New, each defaulted:

```python
@dataclass
class CarriedComponentEntry:
    name: str = ""              # Name2 in the new revision
    was: str = ""               # Name2 in the old assembly
    kind: str = ""              # "part", "assembly"
    configuration: str = ""     # the referenced configuration it was inserted in
    fixed: bool = False
    suppressed_in: List[str] = field(default_factory=list)   # new modes, as read back
    anchor: str = ""            # the CarryBody.old it was placed against, "" world

@dataclass
class CarriedMateEntry:
    name: str = ""; was: str = ""; type: int = -1
    on: List[str] = field(default_factory=list)              # new modes, as read back
    code_before: int = 0; code_after: int = 0

@dataclass
class CarryNamedEntry:
    item: str = ""; what: str = ""; why: str = ""
    subjects: List[str] = field(default_factory=list)       # §2.3's slots
    sentence: str = ""

@dataclass
class CarryFallbackEntry:
    components: List[str] = ...; deleted: List[str] = ...; kept: List[str] = ...; why: str = ""
    subjects: List[str] = ...

@dataclass
class CarryEntry:
    assembly: str = ""          # the old assembly carried from
    read_at: str = ""           # when the old assembly was read
    how: str = ""               # "open", "read-only", "unread"
    carried_at: str = ""
    revision: List[int] = ...   # the SolidWorks it ran on
    states_read: bool = False   # per-mode states read (else the mode showing's, said)
    components: List[CarriedComponentEntry] = ...
    mates: List[CarriedMateEntry] = ...
    named: List[CarryNamedEntry] = ...
    fixed: List[CarryFallbackEntry] = ...
    stopped: str = ""
    unsaved_at: float = 0.0     # the new assembly's file time after its save, when anything was carried into it
                                # unsaved (D16 ruled: a field of its own, not LinkRecord.unsaved); 0.0 nothing unsaved
```

- `GearboxRecord.carry: Optional[CarryEntry] = None` — on the new revision's gearbox block; None for every gearbox not
  made by a carrying Build again… (and on a schema 9 record).
- `GearboxRecord.user_work` of the new revision: when anything was carried, an inventory built from the carry
  (`UserWorkEntry`, `read_at` the carry's time, `assembly` the new one, `revision` the SolidWorks, `components` the
  carried ones, `mates` the remade ones with their touches and entities in the new revision's terms and their `on`,
  `features` the user's features in parts the new revision reuses (from the old inventory), `modes` the new modes), so
  the footer foresees the next Update from it; when nothing was carried, None, as W9a has it. The next press reads the
  new assembly's live work as always. UI-DESIGN §9's *"the record holds no inventory until the new revision's first
  Update"* changes accordingly.
- `UserMateEntry.entities: List[List[str]]` — per entity `[what, name, kind, feature]` from `swbuild.UserMate.entities`
  (§2.2), filled by every Update's inventory from W9d on and by the carry; `[]` on an older inventory (D5).
- **`CarryEntry.unsaved_at`** (D16, should-fix 10): set to the new assembly's file time after its save whenever
  `CarryResult.unsaved`; read by §9.4's two lines only; dropped once the file on disk is newer (the rule `clear_saved`
  applies to `LinkRecord.unsaved`, applied to this field by its own code), and turned into the *lost* line when a later
  job finds the assembly loaded from its file (`result.opened`). `LinkRecord.unsaved` is not touched by a carry: its
  readers (`update._earlier_update`, `Finished.off_after_update`, `workbook_built_tag`, `ui_text`'s `UPDATE_LOST`
  sentence) mean an Update's changes.

**Older readers**: a W9c-era app reading schema 10 refuses with its own sentence and leaves the file byte-identical
(`store.py:1323-1325`, worded at `:1366-1371`: *"The record of what was built, RangeBox.workbook.json, cannot be read:
it was written by a newer Gear Generator (schema 10, this one reads 9). It is left alone, so Build and Update
SolidWorks wait."*). **Schema 9 read forward**: `carry` None, every `entities` `[]`, everything else as read at 9;
written forward as 10 on the next write. B adds the nested readers (`GearboxRecord(**_known(...))` alone would leave a
dict in `carry`). Schema 1–8 as before.

## 8. The findings W9d reads

Each is per version (`_ON_2026`, `_ON_2024`), read with `getattr` from committed `findings.py`; one not settled keeps
its items from being carried, named with the finding (`WHY_UNMEASURED`), and never stops the build. Reads are set from
the W9d probe's reviewed logs; writes from M9's, patched in that run's process for the measurement only (as W9a's
`nocarrier` and W9c's gates): a True one patched True; `CARRY_REMAKE_KINDS` patched to every carried kind word
(`coincident`, `concentric`, `parallel`, `perpendicular`, `tangent`, `distance`, `angle`, `limit distance`,
`limit angle`, `lock`, `gear`), and set to the words whose mates M9 remade clean.

| Finding (`_ON_<year>`) | Kind | Settled when | What it gates | Set by |
|---|---|---|---|---|
| `OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN` | read (set, both) | its route string | the not-open read's open | W9c probes s5 (d) |
| `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` (new) | read | True | the not-open read at all (its close), and its per-mode show | W9d probe `state` (h) |
| `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` (new) | read | True | the not-open read with app documents open (one changed) | W9d probe `state` (g) |
| `FILE_VERSION_READ` (new) | read | its route string | R.2's file-version condition (else the record's alone) | W9d probe `state` (v) |
| `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` (exists, None) | read | its route string | per-mode states read unshown | W9d probe `state` (b)–(d) |
| `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED` (new) | read | True | that route on an open old assembly with unsaved changes | W9d probe `state` (e) |
| `PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES` | read (set, both) | its route string | tier 1 on axes and planes | W9c probes s5 (b) |
| `PERSIST_REFERENCE_ROUTE_FOR_FACES`, `_FOR_EDGES` (new) | read | a route string | tier 1 on faces, edges | W9d probe `faces` (b) |
| `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` (new) | read | a route string | tier 1 on vertices | nothing in W9d: None |
| `PERSIST_REFERENCE_SURVIVES_RELOAD` (new) | read | True | tier 1 on the not-open path | W9d probe `faces` (d) |
| `COAXIAL_FACE_READ` (new) | read | True | `OldEntity.coaxial`: "bore" in sentences, §4.3's gear-mate rule on a face | W9d probe `faces` (b) |
| `REFERENCED_CONFIGURATION_READ` (new) | read | True | the referenced configuration read; unset, every component whose configuration cannot be told is named | W9d probe `faces` (b) |
| `VIRTUAL_READ` (new) | read | True | `IsVirtual` instead of the `^` rule | probe reads it negative only: None until a run meets a virtual component |
| `PATTERN_INSTANCE_READ` (new) | read | True | `IsPatternInstance`: the per-instance sentence (D12) | probe reads it negative only: None until a run meets a pattern |
| `ORIGIN_ENTITY_READ` (new) | read | True | an origin as a mate entity | nothing in W9d: None |
| `SUBASSEMBLY_OPEN_MARKS` (new) | read | **False** | a sub-assembly not loaded, opened to insert it | W9d probe `sub` (a) |
| `SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED` (new) | read | **False** | a sub-assembly loaded as a component, opened to insert it | W9d probe `sub` (c) |
| `SUBASSEMBLY_READ_ONLY_INSERT` (new) | read | True | a sub-assembly opened read-only, then inserted | W9d probe `sub` (b) |
| `SUBASSEMBLY_INSERT_ROUTE` | read (set, both) | its route string | the insert itself | W9c probes p2 |
| `CARRY_INSERT_MARKS_USER_DOCUMENTS` (new) | a fact | — (True or False) | nothing: True adds a sentence (§9.2) | W9d probe `faces` (c) |
| `CARRY_INSERTS` (new) | write | True | user parts inserted, placed, fixed, their states set in every mode and read back | M9 |
| `CARRY_INSERTS_IN_A_CONFIGURATION` (new) | write | True | an insert in a referenced configuration other than the document's active one | M9 |
| `CARRY_INSERTS_A_SUBASSEMBLY` (new) | write | True | a user sub-assembly inserted by its file | M9, if its fixture holds one (else None) |
| `CARRY_REMAKE_KINDS` (new) | write | the kind's word is in the tuple | which kinds are remade (§4.5, D4) | M9 |
| `CARRY_GEAR_MATE_ON_AN_APP_GEAR` (new) | write | True | §4.3's rule | M9 |
| `CARRY_REMAKES_ON_A_LEAF` (new) | write | True | a mate on a leaf of a user sub-assembly | nothing in W9d: None |

Dropped after the review: `ROOT_COMPONENT_UNRESOLVED_READ` (should-fix 12; the probe cannot tell whether that read marks,
so nothing may rest on it: the root read keeps `_read_user_work`'s rule; the probe logs it as a fact only) and the
probe's `MATE_REMAKE_ON_FACES_AND_EDGES_ROUTE` (P13; the remake is `CARRY_REMAKE_KINDS`' with the face and edge routes).

`swbuild.carry_gates(work, carry, revision) -> List[Tuple[str, str]]` (pure) returns `(step, finding)` for each gate
not settled that something in `work` needs, for A's naming and B's question, as `in_place_gates`. Steps:
`STEP_CARRY_OPEN`, `STEP_CARRY_STATES`, `STEP_CARRY_INSERT`, `STEP_CARRY_CONFIGURATION`, `STEP_CARRY_SUBASSEMBLY`,
`STEP_CARRY_FACES`, `STEP_CARRY_EDGES`, `STEP_CARRY_VERTICES`, `STEP_CARRY_RELOAD`, `STEP_CARRY_ORIGIN`,
`STEP_CARRY_KIND` (one per kind word), `STEP_CARRY_GEAR_MATE`, `STEP_CARRY_LEAF`.

## 9. What the user sees (`ui_text`)

In the register of W9a's and W9c's sentences: the user's items as *your*, names whole, counts beside nouns, the time
read, no "please", the reason after the comma.

### 9.1 The question (`build_again_question`; `carry_sentence(foresight, again)` replaces W9a's `stays_behind_sentence`)

From the record's inventory with its time, through `plan_carry` on it (§2.3). With the gates set:

> *As read at 14:02, RangeBox_r2 takes your Sprocket-1, Sprocket-2, Chain-1 and Housing-1, each where it stands against
> the gear it is mated to, and makes your 8 mates again on what they join, each on in the modes it was on in;
> Concentric5 is not made again, since it is on Sun's bore and Sun's part is new because its Flank changed. Your Keyway
> stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed; RangeBox.SLDASM and that file keep
> it. RangeBox_r2 is saved as built, and holds what it carries unsaved: save it in SolidWorks to keep them. The press
> reads RangeBox.SLDASM again first, and says whatever it cannot carry.*

The feature clause carries the part's why itself (should-fix 13), whether or not a mate clause before it did. Clauses
added as they apply, each in the result too:
- a feature in a part made new only because the user typed an app value in SolidWorks (`MISMATCHED`): *Gear_m1.25_N29
  is new only because it holds Bore Diameter 12 where the workbook asks 10: answer No, type 12 in Gears!J2, and Build
  again… reuses that part with your Keyway.* (the value and cell from the record's K11 `ValueEditEntry` for that
  document; without one, *answer No, make the workbook ask what that part holds in SolidWorks, and Build again…
  reuses it with your Keyway.*) (D17); only because an Update left it unsaved (`UNSAVED`): *answer No and save it in
  SolidWorks first, and Build again… reuses it with your Keyway.*;
- a mate whose inventory entry has no entity kinds (schema 9) on a part made new: *your Lock3 and UserAxis4 join Sun,
  whose part is new: a mate on one of its faces or edges is not made again, and the press reads which they are.*;
- a component lightweight as read: *Sprocket-4 was lightweight as read, so its 3 mates cannot be read through it: set
  it resolved in SolidWorks before you press, or they are not made again.*;
- a component suppressed in the mode showing as read: *Sprocket-7 was suppressed in H, the mode RangeBox.SLDASM
  showed, as read; if SolidWorks cannot say where it stands there, it is not carried: show a mode where it is resolved
  before you press.*;
- a referenced configuration not carried (the gate unset, or unread): *Sprocket-1 uses its configuration Z20, which
  Gear Generator cannot yet carry on SolidWorks 2024 (findings.CARRY_INSERTS_IN_A_CONFIGURATION_ON_2024), so it is not
  carried, nor are its 3 mates.*;
- the old assembly **not open**, and R.2's conditions not all met: *RangeBox.SLDASM is not open in SolidWorks, and
  Gear Generator reads it then only when …* the condition that fails, one of: *it was last written on this SolidWorks*
  (*a file saved since on another SolidWorks is not read*), *nothing else is open in SolidWorks*, *(findings.OPEN_READ_
  ONLY_SHOWN_CLOSES_CLEAN_ON_2026)* — then *, so nothing of yours would be carried: open RangeBox.SLDASM in SolidWorks
  before you press, and it is read as it stands there.*;
- states per mode not readable (D2 †): *Your components take, in every mode of RangeBox_r2, the state they have in the
  mode RangeBox.SLDASM shows when you press: whether you suppressed one in another mode cannot be read without changing
  RangeBox.SLDASM.*;
- a mode renamed or removed: *RangeBox_r2 has no mode 2L: what your items were in 2L stays in RangeBox.SLDASM. Its new
  mode 4L takes what they were in H.* (D14, plain);
- a gate not set: *Gear Generator has not yet been shown to carry concentric mates into a new revision on SolidWorks
  2024 (findings.CARRY_REMAKE_KINDS_ON_2024), so Concentric5 and Concentric8 are not made again.*; with `CARRY_INSERTS`
  not set, W9a's sentence follows, led by *Gear Generator has not yet been shown to carry your work into a new revision
  on SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024), so as read at 14:02, …*;
- the version not known (a record no job of this version wrote): W9c's mixed form, *Whether RangeBox_r2 takes your
  work depends on the SolidWorks in use: Gear Generator has been shown to do so on SolidWorks 2026, not yet on
  SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024), and the press reads which it runs on.*;
- nothing on record: *Anything you added to RangeBox.SLDASM in SolidWorks the press reads first and carries into
  RangeBox_r2 where it can, saying whatever it cannot.*;
- **the standing list of what is not carried as it was**, once, at the end, whenever anything of the user's is on
  record: *Not carried as they are: assembly features of yours (cuts, patterns, sketches, planes), display states and
  appearances; a sub-assembly comes over rigid, and a component of a pattern of yours comes over as a component of its
  own.* (the pattern clause leaves this list for the per-instance sentence once `PATTERN_INSTANCE_READ` is set, D12 †).

### 9.2 The result (`carried_status(result, again, old_path)`, after `gearbox_status`, replacing `stayed_behind_status`)

> *Carried into RangeBox_r2, unsaved: your Sprocket-1, Sprocket-2, Chain-1 and Housing-1, each where it stood against
> its gear, and 7 of your 8 mates, each on in the modes it was on in. Not carried: Concentric5, which was on Sun's
> bore, and Sun's part is new because its Flank changed. Your Keyway stays in Gear_m1.25_N29, which Sun's new part
> replaces because its Flank changed (RangeBox.SLDASM and that file keep it). Save RangeBox_r2 in SolidWorks to keep
> what was carried.*

Then, as they apply:
- the fallback, as the plan words it: *Sprocket-8 is fixed where it stood in RangeBox_r2: with your Lock8 and Lock9
  made again SolidWorks reads Sun unable to turn, so those two were not kept; Coincident7 beside them was.*
  (`FELL_NEW_ERROR`: *… with your Lock3 made again it reads error 46 in L, which it did not in H, the mode
  RangeBox.SLDASM showed, …*; `FELL_OVER_DEFINED`: *… your Lock3 made again over-defines them, …*);
- *Your UserDist4 was in error in RangeBox.SLDASM and is in RangeBox_r2 too, as it was.*;
- *In L, SolidWorks moved Sprocket-4 2.0 mm from where it stood against Sun when your mates were made again.*;
- a clash: *In mode L, your Sprocket-2 interferes with RangeSlv (12.3 mm³).*;
- **placed once** (should-fix 13): *Your components were placed where they stood in H, the mode RangeBox.SLDASM showed;
  a floating one that stood elsewhere in another mode stands, in RangeBox_r2, where it stood in H.* (with modes, once,
  whenever a floating component was carried);
- the states: *Your components take in every mode the state they had in H, the mode RangeBox.SLDASM showed: their
  states in N and L could not be read without changing it.*; the D14 sentence of §9.1;
- *Your sub-assembly Drive-1 comes over rigid: set it flexible in SolidWorks again if it was.*;
- **the standing list** of §9.1's last clause (display states and appearances included), and *A part of yours made in
  context of RangeBox.SLDASM still refers to its parts.*;
- with `CARRY_INSERT_MARKS_USER_DOCUMENTS` True: *SolidWorks reads Sprocket.SLDPRT as changed since it was inserted
  into RangeBox_r2, though nothing in it changed: saving RangeBox_r2 with its parts saves that file again too.*;
- a stop: *Carrying your work stopped at making UserDist4 again (SolidWorks: …), so it did not get to making
  Sprocket-4's other mates again and checking the assembly; what was carried before it is in RangeBox_r2, unsaved, and
  RangeBox_r2 as built is saved.*;
- nothing read: *RangeBox.SLDASM was not read (…), so nothing of yours was carried; it and your files are as they
  were.*;
- a read that marked a document (§0.3): *Reading RangeBox.SLDASM marked Sprocket.SLDPRT as changed in SolidWorks, which
  Gear Generator never does on purpose, so nothing of yours was carried; nothing in it changed, and RangeBox.SLDASM and
  your files are as they were on disk.*; a document left open by the read (R.7): *Reading RangeBox.SLDASM left
  Sprocket.SLDPRT open in SolidWorks, so nothing of yours was carried; close it without saving.*

The build's own sentence is said first and unchanged in every case.

### 9.3 Each reason (`carry_named(named)`, one clause per item, from §2.3's slots)

| `why` | Clause |
|---|---|
| `kind` | *Width1 is a width mate, which Gear Generator does not make again* |
| `unmeasured` | *Concentric5 is a concentric mate, which Gear Generator has not yet been shown to make again on SolidWorks 2024 (findings.CARRY_REMAKE_KINDS_ON_2024)*; an entity kind: *… is on a face of Sprocket-1, which … (findings.PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024)*; an origin: *… is on an origin, which …* |
| `part new` | *Concentric5 was on Sun's bore, and Sun's part is new because its Flank changed* |
| `gone` | *Lock4 was on G5, which RangeBox_r2 does not have*; *UserAxis2 was on the layout's Output Axis, and RangeBox_r2 has no shaft Output*; *Coincident6 was on Sun's Mid Plane, which Sun's new part does not have* |
| `assembly feature` | *Coincident9 is on Plane1, a plane you made in RangeBox.SLDASM, which is not carried* |
| `component not carried` | *Lock6 joins Bracket-1, which is not carried* |
| `unread` | *SolidWorks would not describe Mate12 wholly* |
| `lightweight` | *Lock7 is on Sprocket-4, which was lightweight in RangeBox.SLDASM, so what it joins could not be read* |
| `no file` | *Part1^RangeBox is a virtual component, with no file of its own, so it is not carried*; *Bracket-1's file Bracket.SLDPRT is not on disk, so it is not carried* |
| `leaf` | *LeafAxis is on a part inside your sub-assembly Drive-1, which Gear Generator does not make again* |
| `not found` | *Coincident8's face of Sprocket-1 could not be found again in Sprocket.SLDPRT* |
| `configuration` | *Sprocket-1 uses its configuration Z20, not Z15 which its file opens in, and Gear Generator cannot carry it in Z20 here, so it is not carried* |
| `no frame` | *Sprocket-7 is suppressed in H, the mode RangeBox.SLDASM showed, and SolidWorks would not say where it stands, so it is not carried* |
| `differs` | *Lock4 made again read otherwise than it was (its entities), so it was taken out again* |
| `old unread` | *(the not-open clause of §9.1)* |

### 9.4 The footer afterwards

While `CarryEntry.unsaved_at` stands: *RangeBox_r2 holds what Build again… carried of yours, not saved: save it in
SolidWorks to keep it.* Found closed unsaved by a later job: *RangeBox_r2 was closed without saving after Build again…
carried your work into it, so it does not hold it; RangeBox.SLDASM still does.* Nothing offers to carry again (D11).

## 10. What A adds to `swcom.Session` (each a wrapper, with `GetSaveFlag` read around it in the probe and M9)

- `mate_definition(handle) -> MateDefinition` — S5 (a)'s read (`GetTypeName2`, `IMate2` Type, Alignment, Flipped,
  variations, `GetDefinition`'s fields, `MateEntity(i)`'s ReferenceComponent, ReferenceType2, Reference and its feature
  name, `EntityParams`), measured marking nothing on both versions.
- `entity_reference(mate_handle, index) -> (kind, hex or "", coaxial, why)` — tier 1's read for feature, face and edge
  entities (§4.1; the face and edge route as the probe finds it, per kind), and the coaxial read (§2.2).
- `component_states(names, configurations) -> Dict[str, Dict[str, bool]]` — the unshown route
  `COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_<year>` names; refused while it is None.
- `referenced_configuration(handle) -> (referenced, document's active)` — gated `REFERENCED_CONFIGURATION_READ`.
- `open_read_only(path) -> Optional[DocInfo]` and `close_unsaved(path)` — `OpenDoc6(Silent | ReadOnly)` and `QuitDoc`,
  the latter refusing a document this session did not open.
- `select_by_reference(handle, kind, hex, append)` — tier 1's resolve, `GetCorresponding`, kind checked, `Select4`.
- `add_component(handle, path, at, configuration="")` — `configuration` given: `AddComponent5(path, 0, "", True,
  configuration, x, y, z)` (gated `CARRY_INSERTS_IN_A_CONFIGURATION`); unchanged otherwise.
- `set_component_suppressed(handle, suppressed)` — `IComponent2.SetSuppression2` in the mode showing, read back
  (measured as the probes' own call: W9c's s5 (e), W9a's `lightweight`; never the app's).
- **`remake_mate(handle, definition, targets, name) -> (name kept, status)`** — `AddMate5` from the definition on the
  targets selected **in selection order** (should-fix 5), renamed. The ledger (`API-LEDGER.md:612`, verified both
  versions): for a **gear** mate and a point-to-plane **distance**, `MateEntity(0)` is the first selection; for an
  **axis–axis coincident**, a **face–axis concentric** and a point-to-plane coincident, `MateEntity(0)` is the
  **second**. So the plan's targets are `MateEntity` order for the first group and reversed for the second; for every
  other kind and entity pair (no measurement) `MateEntity` order, then read back as below, and once reversed if the
  read-back has them the other way. **Gear ratio** (`:552`, `:618`, `:620`): `GearRatioNumerator` reads the second
  selection's count while `AddMate5`'s numerator argument goes with the first, so the remake passes the read
  `GearRatioDenominator` as `AddMate5`'s numerator and the read `GearRatioNumerator` as its denominator. **Sense**: a
  gear mate's sense (its gears turning the same way or opposite) is worked from the old mate's `Reverse` and its two
  entities' `EntityParams` directions by the rule `gear_mate_sense` reads (`API-LEDGER.md:623`, W6's rule H) and held
  as `CarryMateItem.sense`; the remade mate's is read the same way, and a wrong one is made again with the other Flip
  once, as W5's remake does. **Read back**: the remade mate's entities' components, alignment, flipped, values and
  (a gear mate) ratio and sense, against the old; a difference left is `WHY_DIFFERS`, the mate deleted again.

## 11. The three things owed before W9d is designed, and two more

### 11.1 A component's state per configuration without marking the assembly

*Measured* (both versions): `IFeature.IsSuppressed2(swSpecifyConfiguration, names)` on the component's feature reads
every mode unsuppressed, wrong in L; each configuration's `GetRootComponent3(True)` and its child's `GetSuppression2`
read right and marked the assembly (`w9c…-2.log` :281-284, `w9c24` :282-285). A show marks the assembly on both versions
and stales every handle (assemblies/13; GOTCHAS §108). `IModelDoc2` has nothing that clears the flag but a save.

*Candidates, from the installed API help*, in the order the probe tries them, each with `GetSaveFlag` of every
document around it, nothing shown, only when the assembly read unmarked at the bracket's start (P4):
1. **`IConfiguration.GetComponentSuppressionState(CompName)`** — Boolean, True suppressed; since 2001Plus; its example
   calls it with `IComponent2.Name` on the active configuration. Reached by `GetConfigurationByName(mode)`, measured.
   Never called by the app or the macro database. **The likeliest.**
2. **`IConfiguration.GetRootComponent3(False)`** — the help: "Null or Nothing, if Resolve is set to false and the
   configuration is not active". It cannot read another mode by its documentation; the probe confirms that cheaply.
3. **`GetRootComponent3(True)` taken apart** (`GetConfigurationByName`, `GetRootComponent3(True)`, `GetChildren`, `Name2`,
   `GetSuppression2`), the flags after each, to name the call that marks (the W9c review's ask).
4. The not-open path's own route: the job's read-only document shown mode by mode and closed unsaved.

Considered and not taken: `IAssemblyDoc.CompConfigProperties6` (a setter); opening a copy of the old file under
another name.

*What the probe also asks of candidate 1*: that it reads an unsaved change (`…_READS_UNSAVED`, asked only if candidate 1
was chosen, P6), that it leaves a lightweight component lightweight, that it answers for a component suppressed in the
mode showing.

*What the app does* (D2 †, ruled):
- **A clean route on the running version**: used in both situations. On an open old assembly whose `GetSaveFlag` reads
  True, only if `…_READS_UNSAVED` is True; else as the next bullet.
- **No clean route, the old assembly open in the user's session**: never shown in another mode. Each carried
  component takes the mode showing's state in every mode, said plainly in the question and the result (§9). The user
  may overrule (the other two ways: show and restore leaving the flag set; refuse until the user saves or closes it).
- **No clean route, the old assembly not open**: the job's own read-only open and the per-mode show happen only under
  R.2's conditions (the record's version, nothing but the app's documents open, `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN`
  True); otherwise the old assembly is not read at all (`OLD_UNREAD`), said before the press with the way round (open
  it in SolidWorks first) — never a hang.

### 11.2 The not-open read, and the documents already open

After a Build again… builds, the parts the new revision reuses are open; R runs before the build (D1), so at R's time
the session holds what the user had open. Measured: the read-only open of an assembly not open, every component
closed, reads read-only with its flag False (`OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN`). Not measured: what it does to
documents already open (made read-only? their changes kept? marked?), closing it after its modes were shown, and
`QuitDoc` on a file another SolidWorks saved (GOTCHAS §100: on 2026 the CAM add-in's modal "Save changes to …?" for a
2024 file, which ignores `WM_CLOSE` and Escape; the app has no dialog watch). Must-fix 2's conditions (R.2) keep the
open off those cases: the record's `solidworks` is the version the last *job* wrote the file on; a save by the user on
another version since is not in the record, so once `FILE_VERSION_READ` is set the file's own `VersionHistory` (a
closed-file read, verified on 2026 in the ledger, `API-LEDGER.md:115`, never by the app) is required to agree too. With
it unset the record's word alone stands, and a file saved on the other version since remains the one residual way to
reach the CAM box; said in §13.

### 11.3 Whether opening a healthy user sub-assembly marks it

The insert route opens the sub-assembly first (`SUBASSEMBLY_INSERT_ROUTE`); a sub-assembly with a missing part read
**modified** straight after a Silent open (`SUBASSEMBLY_MISSING_PART_READS`). A healthy one's flag after the open was
not read. The probe reads it not loaded (`OpenDoc6` Silent), loaded as a component of an open assembly, and opened
read-only then inserted. *Ruled* (D13): a sub-assembly is carried only by a situation whose open is measured marking
nothing (`SUBASSEMBLY_OPEN_MARKS` / `_WHEN_LOADED` False), or by the read-only insert if `SUBASSEMBLY_READ_ONLY_INSERT`
is True; otherwise it is named, *your sub-assembly Drive-1 is not carried: opening it to insert it marks it as changed in
SolidWorks, and Gear Generator never changes a file of yours*. A mate on a leaf inside it is named while
`CARRY_REMAKES_ON_A_LEAF` is None. Its referenced configuration is carried as a part's (§5.1).

### 11.4 A face's persistent reference

The probe makes a concentric on a sprocket's bore (face–axis), a coincident between two sprockets' end faces
(face–face, user–user), a concentric on a sprocket's circular edge (edge–axis) and a parallel between a sprocket's end
face and Sun's (a face of an app part on the same file, and the parallel kind read and remade for the first time), then
saves its own copy so the reads start unmarked (P1). It reads each entity's kind (`ReferenceType2`, and which of
`GetSurface` / `GetCurve` / `GetPoint` answer, for the probe only), whether its reference names its component
(`IEntity.GetComponent`), two routes to the part-level reference (`GetCorrespondingEntity2` in the assembly; the
mate's entity straight to the part's `GetPersistReference3`), resolves each in the part, carries it back through the
component and asks `ISldWorks.IsSame`; the coaxial read on each face; each user component's referenced configuration,
`IsVirtual` and `IsPatternInstance`. It then makes the four again in a second assembly, the route chosen per entity kind
(P10), with the copy's documents' flags read around the inserts; and resolves every face and edge reference again after
the copy is closed and the parts opened alone (the reload, should-fix 9). *Ruled*: a face or edge entity is tier 1 only
by the route the probe proposes for its kind, set per version; unset, `WHY_UNMEASURED`.

### 11.5 Two more the contract depends on

- **The root read on an assembly with a lightweight component** (the W9c review's should-fix 5): the probe reads
  `GetRootComponent3(False)` and `(True)` there as facts (does each answer, does either resolve the component); it
  cannot tell whether either marks (the copy is marked by then), so nothing rests on it: `_read_user_work`'s rule stands.
- **A mate on a component suppressed in a mode**: read by the probe as a fact (its flags there), so §3 C.6.1's "a mode
  where one of its components is suppressed left as SolidWorks has it" rests on a reading; M9 holds one in the mode
  showing (what R reads of such a mate's definition is not measured).

## 12. The choices, as ruled (the coordinator, 2026-11-17; † the user's to overrule)

- **D1 — ruled as recommended**: read before anything is made, carry after the save; `open_before` is R.1's list, and
  R.7 checks the session is left as found (should-fix 8).
- **D2 † — ruled as recommended**: an old assembly open in the session is never shown in another mode; with no clean
  unshown route each carried component takes the mode showing's state in every mode, said plainly. Not open: the
  read-only open and per-mode show only under must-fix 2's conditions; otherwise the old assembly is unread, said,
  never a hang. A clean unshown route makes this moot.
- **D3 — ruled as recommended**: an app gear part's own names and base planes by name and tree order on a part made new
  too; the names from `plan_features` (§2.1); `Mid Plane`/`Profile Plane` missing is gone.
- **D4 — ruled as recommended**: one per-version tuple `CARRY_REMAKE_KINDS`, settled for a kind when its word is in it;
  M9 patches it to every carried kind word and sets it to those remade clean.
- **D5 — ruled as recommended**: entity kinds kept in the inventory, classified by `ReferenceType2`.
- **D6 — ruled against the draft** (must-fix 1): clusters made and judged one by one, K2's rule for when one read decides
  every mode, the plan's three fallback cases, only the cluster that ties falls back.
- **D7 — ruled as recommended**: `moved` said, not a fourth case; compared in the anchor's frame per mode.
- **D8 — ruled**: interference per mode again, in the post-check's shows.
- **D9 — ruled**: the fallback's writes have no gate of their own; M9 shows a tied cluster.
- **D10 — ruled**: a lightweight component carried resolved, its mates named; foreseen in the question.
- **D11 — ruled**: no "carry again".
- **D12 † — ruled as recommended**: a pattern instance comes over as a component of its own; `IsPatternInstance` (a
  documented get) is read bracketed in the probe; the sentence is said per instance once `PATTERN_INSTANCE_READ` is
  set, and until then once, in the question's standing list of what is not carried as it was (§9.1).
- **D13 — ruled**: sub-assemblies by measured open only; **the referenced configuration is read and carried** (must-fix
  4, §5.1), behind `REFERENCED_CONFIGURATION_READ` and `CARRY_INSERTS_IN_A_CONFIGURATION`; a component whose
  configuration cannot be carried is named, never carried in another.
- **D14 — ruled**: modes by name, a new mode takes the old record's first mode's states, an old mode not in the new
  revision dropped; the sentence plain (§9.1).
- **D15 — ruled**: remade mates keep their old names.
- **D16 — ruled against the draft**: `CarryEntry.unsaved_at`, not `LinkRecord.unsaved` (§7).
- **D17, D18, D19, D21 — ruled as recommended** (D18 verified, §15: a mixed-flank mesh is legal in the code now; D19's
  origin is now any origin, unmeasured, §4.2).
- **D20 — ruled with the review's change**: each component takes its own lock to an app body first, then its cluster's
  anchor.
- **Contradiction 1 † — ruled**: a user gear mate's entity on an app gear is taken as that gear's `Gear Axis` on the new
  part, the other side by its own tier, behind `CARRY_GEAR_MATE_ON_AN_APP_GEAR`, ratio and sense read back (§4.3, §10).
  One refinement the code forces (§13 item 1): only a coaxial face or edge is taken so; a face of the user's own
  off-axis feature in the gear part is not.

## 13. In the plan, contradictory or not buildable as written, and where each is resolved

1. **§2.5 tier 3 and K5, "a lock or gear mate references whole components"**: a gear mate takes rotational entities
   (m1: two axes). Resolved in §4.3 (ruled †). Refinement: "every rotational face of an app gear is coaxial with its
   Gear Axis" holds for the faces the app makes, not for a user's feature cut into the gear part (W9a's keyway, an
   off-axis Ø 3 hole in Sun's part), hence `coaxial`.
2. **§0.3's third exception, "shows … and restores … `GetSaveFlag` unchanged"**: impossible when the assembly starts
   unmarked. Resolved in §11.1 (D2 †): never shown when open.
3. **§2.5's carried kinds include parallel, perpendicular and tangent**, never read by any run. Resolved in §4.5 and §8:
   each stays named until `CARRY_REMAKE_KINDS` holds it; M9 (§15) carries parallel and limit; perpendicular and tangent
   stay named on both versions after W9d.
4. **"A mode new in this revision takes the first mode's state"**: the old record's first mode (§5.2, D14).
5. **§2.5's record "schema 9"**: superseded by 10 (§7).
6. **"Frames read in the active mode only" and "placed once, in the first mode"**: may differ. Resolved in §5.3
   (placement relative to the anchor's frame in each) and §6 (`moved` compared in the anchor's frame per mode).
7. **"No `Save3` … *RangeBox_r2 holds them unsaved*"**: true; nothing changes in what is saved.
8. **The not-open read's residual risk** (§11.2): the record knows the version of the last *job*, not of a user's save
   since; until `FILE_VERSION_READ` is set, a file the user saved on the other SolidWorks after the last job can still
   reach GOTCHAS §100's CAM box on the close. The coordinator's ruling stands on the record; the probe reads
   `VersionHistory` so the gap can close.

## 14. Tests each package owes against the fake

### 14.1 Package A (the worker)

- Each row of §2.5's table, on a `RangeBox` built by the fake with a carry: a user part carried fixed and floating, its
  state set in every mode and read back; a part whose referenced configuration differs from its document's active one
  carried in it (gate patched) and named (gate None, or read back otherwise: deleted again); a sub-assembly carried
  (gate patched) and named (gate None); a virtual component (`^` in its file, the file existing in a temp folder)
  named; a file not on disk named; a pattern instance carried as its own (D12); each carried kind remade with
  alignment, flip, values (limits, gear ratio swapped, sense) and flags per mode, in §10's selection order; each other
  kind named `WHY_KIND`; a kind not in `CARRY_REMAKE_KINDS` named `WHY_UNMEASURED`; an assembly feature's mate named;
  an origin entity named `WHY_UNMEASURED`.
- A mate whose entity is not found (`WHY_NOT_FOUND`, `WHY_GONE`): named, its component floating where placed, its other
  mates remade. A reference resolving to another kind stops the carry (§0.3). A remade mate read back otherwise
  (`WHY_DIFFERS`): deleted again, named.
- A remade mate in the error it had before: carried, `same_error`, its cluster not fallen back.
- **Clusters one by one**: on RangeBox's one train, a tied cluster (locked to Sun and to a fixed housing) falls back —
  its mates to app parts, the layout and the assembly deleted, its user–user mate kept, its components back where
  placed and fixed — while every other cluster on that train (locked to Sun, to RangeSlv, a gear mate on Sun) is
  carried with every mate; every app gear free after. A cluster whose mates' flags differ by mode, tying in L only,
  falls back in L's show. A new error and an over-definition (status 5) each falling back; cluster −1 alone.
- **Placement**: a sprocket locked to a Sun the user had turned 37° goes in **at the angle to Sun it stood at** (its
  pose relative to Sun unchanged, `_carry_frame`; 37° less in the world), the test asserting `_relative(new Sun,
  sprocket) == _relative(old Sun, old sprocket)`; one anchored to RangeSlv read in L and placed in H keeps its pose
  relative to RangeSlv, and is not `moved` in L; a component of a cluster anchored to Sun but locked itself to RangeSlv
  is placed against RangeSlv; a component suppressed in the mode showing whose frame reads placed, one whose frame does
  not named `WHY_NO_FRAME`.
- Nothing written to the old assembly (the fake fails any write while the old assembly is the current document, any
  show of it, any `close_unsaved` of a document the job did not open); nothing saved after the new assembly's first
  `save_as`; every user file's saved state and time unchanged; `open_before` is R.1's list; a read that leaves a
  document open does nothing more, said.
- **The not-open path**: refused (`OLD_UNREAD`, said) when the record's version is not the running one, when a document
  the record does not name is open, or when `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` is None; otherwise opened read-only,
  shown and closed, and tier 1 named `WHY_UNMEASURED` while `PERSIST_REFERENCE_SURVIVES_RELOAD` is None.
- A mode new in the revision takes the old first mode's states and flags; an old mode not in it is said.
- Every gate None: nothing carried, every item named with its finding, the build's result and record unchanged from
  W9c's.
- A read that marks a document (the fake doctored): nothing carried, `stopped` said, the build stands.
- Old open: never `open_document`ed, never activated.
- A lightweight user component: its mates `WHY_LIGHTWEIGHT`, the component carried resolved, nothing resolved in the old.
- Tier 1 on faces and edges (findings patched) and named while None; tier 2 by name, a shaft gone named, base planes by
  order, the assembly's plane by order; a user gear mate on the new Sun's `Gear Axis` (gate patched), and on a coaxial
  face of Sun taken as `Gear Axis`, and on the keyway's off-axis face named.
- A carry that stops part way (a raise at the third `remake_mate`): `inserted`, `remade` list what was done, `skipped`
  what was not, the new assembly saved as built, the rest unsaved.
- `plan_carry` and `carry_gates` on hand-made `OldWork`s, with every `subjects` slot of §2.3.

**What the fake gains**: a user mate's whole definition (type, alignment, flipped, values) and per-end entity kinds
(`whole`, `feature`, `plane<n>`, `origin`, `face:<id>`, `edge:<id>`, `vertex:<id>`, each with its `ReferenceType2`) and
`coaxial`; **the ledger's selection-order rule** (`MateEntity(0)` the second selection for axis–axis coincident,
face–axis concentric and point–plane coincident, the first otherwise) and **the gear ratio's swap** (the numerator read
is the second selection's), so a remake in the wrong order or with the ratio unswapped reads back otherwise; a
persistent reference per (file, entity) that resolves in any instance of the same file and in no other, and after a
reload only with a `reload_ok` knob; `component_states` per configuration with `states_mark` and `states_read_unsaved`
knobs; a component's referenced configuration and its document's active one, and an insert in a configuration;
`open_read_only` and `close_unsaved` with the read-only document's own marks and a knob for a document left open;
`set_component_suppressed` in the mode showing; `remake_mate` with doctorable status, error after, and a tie
(`constrained` 3 on a train's gears while a given user mate is on in that mode); the old assembly's documents' saved
state and times, with an `AssertionError` on any write to them; an `AssertionError` on any `save_as` after the new
assembly's.

### 14.2 Package B (planning, the question, the result, the record, the window)

- `carry_for` from a record and a plan: planet copy *k* to copy *k*; a gear removed with handle `""`; the layout and
  carriers; `same_file` from `reuse`; `why_new` from the structural reasons and `made_new` (Flank, Part name,
  `UNSAVED`, `MISMATCHED`); `names` from `plan_features`, the sidecar and `layout_features`; `written_on`, `app_files`.
- The question from the record's inventory with its time: carried and named, the feature in a part made new with its
  why, the `MISMATCHED` advice with the cell and value and without, the `UNSAVED` advice, a schema 9 inventory's *may*,
  a lightweight component, a component suppressed in the mode showing, a configuration not carried, the not-open clause
  for each failing condition, the states clause, the renamed-mode clause, a gate None (each kind and `CARRY_INSERTS`),
  the version mixed, nothing on record, the standing list.
- The result's sentences for each `why` (every subjects slot) and each fallback kind, `same_error`, `moved`, a clash,
  placed once, the states, a stop, nothing read, a read that marked, a document left open, the marks fact.
- Schema 10 written and read back; a schema 9 record read forward and written as 10; a W9c-era reader (the store at 9)
  refusing 10 with its sentence and leaving the file byte-identical.
- After a carry: the new revision's `user_work` from the carried items (None when nothing was carried), the footer's
  foresight of the next Update from it; `unsaved_at` set and the footer's line; a save (file newer) dropping it; found
  closed by a later job, the lost line; `LinkRecord.unsaved` untouched by the carry.
- The round trip through the window's path: classify → the question → `_start_build` with `carry` → `build_gearbox` on
  the fake → `_finish_build` → the record → the footer.
- UI-DESIGN §9's *Build again?* paragraph and the W9a section's last sentence rewritten (not a test).

## 15. The demonstration (M9), in outline

**Fixture**: a copy of W9a's `setup.master` (RangeBox with Sprocket-1 and -3 locked to Sun and on Input Axis,
Sprocket-2 locked to RangeSlv on Output Axis, Sprocket-4 by a distance to Sprocket-3 and an angle to the layout, the
fixed Housing-1, the User Keyway in Sun's part; `W9A-DEMONSTRATION.md`), to which the script adds, before the sections,
saved as the run's own copy:
- **the Done-when's clusters, on feature mates** (should-fix 15): cluster one, Sprocket-1, -3 and Sprocket-4 on Sun
  (setup's own), plus Chain-1 (a user part) on Input Axis by its axis and a distance between its plane and
  Sprocket-1's; cluster two, Housing-2 mated to the layout by its planes (coincident and distance);
- **face mates, as a further item resting on `PERSIST_REFERENCE_ROUTE_FOR_FACES`**: a concentric on Chain-1's bore to
  Input Axis, a coincident between Chain-1's and Sprocket-1's end faces; with that finding None both are named and the
  Done-when still holds on the feature mates;
- a coincident between Sprocket-5's end face and **Sun's front end face** (RangeBox's Sun has no bore: a face of an app
  part made new, named `WHY_PART_NEW`);
- a parallel and a limit distance on user parts (kinds);
- a user gear mate from Sprocket-6's `Gear Axis` to Sun's `Gear Axis` (§4.3, `CARRY_GEAR_MATE_ON_AN_APP_GEAR`, ratio
  and sense read back; the face variant is shown on the fake only, since no face of Sun is coaxial);
- Sprocket-7 suppressed in L (states per mode);
- Sprocket-9 lightweight in the mode showing, with a mate (D10);
- Sprocket-10 suppressed in the mode showing, with a mate (should-fix 3, and what R reads of its mate);
- a mate to the assembly's own Front plane (tree order);
- Sprocket-11 with a configuration of its own (its part given a second configuration, the component set to it):
  `CARRY_INSERTS_IN_A_CONFIGURATION`;
- the tied cluster, Sprocket-8 locked to Sun and to the fixed Housing-1 (`FELL_TIE`);
- with the sub-assembly findings set, a user sub-assembly on Output Axis.

Each item depends on the findings named beside it; the script reads them first and says which items will be named
rather than carried, so a None finding is a named item judged as named, never a failure.

**The edit**: Sun's Flank to arcs (D18, **verified in the code now**: `assess.assess` of `range_box()` with Sun's
`flank="arcs"` gives no error and no build refusal, only the note *Sun: Arcs stand in for the involute on this gear to
within 34.7 µm*; nothing checks the flanks of two meshing gears against each other) and a shaft added (a gear on a new
shaft meshing nothing it would refuse), so Sun's part is a new file and every other part is reused; typed in Excel by
W8's `edit`.

**Sections**: `carry-gates` (every W9d write gate None: the question and the result name everything with its finding,
the build as W9c's; ~10 min); `carry` (the gates patched in the process, the old assembly open with H showing: the
Done-when below; ~40 min); `carry-closed` (the old assembly **saved with L showing**, then closed: read read-only under
R.2's conditions, RangeSlv's train read in L and placed in H, contradiction 6 shown with the sliding RangeSlv; the
states by the route or the read-only show; ~20 min); a 2024 run of `carry` alone in a fresh session (~80 min).

**Judged** (every mode shown, every read before and after): RangeBox_r2 saved as built; both feature-mate clusters
carried, each component at its pose against its own anchor to the post-check's tolerance, every remade mate's
definition equal to the old one and on in the modes it was on in, code 0; the face mates carried or named as their
finding says; the mate on Sun's face named `WHY_PART_NEW`; the keyway named in the question and the result with why;
the tied cluster alone fixed, its user–user mate kept, Sun free to turn in every mode, every other cluster on Sun's
train carried; **Sprocket-7 suppressed in L alone where the states route is clean, and resolved everywhere, said, where
it is not** (D2); Sprocket-9's mates named, it carried resolved; Sprocket-10 placed or named as its frame read;
Sprocket-11 in its configuration; the gear mate on `Gear Axis` remade with its ratio and sense; every app gear free to
turn in every mode; the carried items unsaved, `unsaved_at` the file's time; RangeBox.SLDASM's flag, active mode, every
component's frame and state, every mate's code, flag per mode and entities, and every user file's time unchanged; no
dialog; the record at schema 10 holding the carry, and the footer's line. Proposes `CARRY_INSERTS`,
`CARRY_INSERTS_IN_A_CONFIGURATION`, `CARRY_REMAKE_KINDS` (the kinds remade clean), `CARRY_GEAR_MATE_ON_AN_APP_GEAR`
and, with a sub-assembly, `CARRY_INSERTS_A_SUBASSEMBLY`. `FELL_NEW_ERROR` and `FELL_OVER_DEFINED` are the fake's only.

## 16. What each package writes, in parallel, in this one checkout

See §17 for the split; in short, A's shapes commit first, then both work against the fake, A's worker and B's planning
meeting at `build_gearbox`'s keywords and `CarryResult`.

## 17. Package split (for an implementer starting cold)

**Read first**: this note §1–§10; `W9C-INTERFACES.md` §2, §8 and §11 (the house pattern); `swbuild.build_gearbox`
(`:3311-3513`), `read_old_assembly` and `_read_before` (`:6681-6718`), `_read_user_work` (`:6587-6661`), `_carry_frame`
and `_relative` (`:5384-5409`); `workbook/update.py` `stays_behind` and `old_assembly` (`:3076-3128`); `ui_text`
`build_again_question` (`:2203`), `_stays_text`, `stayed_behind_status` (`:4527-4620`); `workbook_gui._start_build` and
`_finish_build` (`:1380-1568`); `tests/test_swbuild.FakeSolidWorks`.

**One shapes commit first, by A, before either starts** (as W9c's `2ffca52`): in `swbuild.py`, every dataclass and
constant of §2 (`CarryBody`, `Carry`, the `ENTITY_*`, `OldEntity`, `OldMate`, `OldComponent`, `OldWork` with `OLD_*`,
the `WHY_*`, `FELL_*`, `CarryNamed`, `CarryPlanItem`, `CarryMateItem`, `CarryPlan`, `CarryResult`, `CarryFallback`,
`UserMate.entities`), the `STEP_CARRY_*` names, `GearboxResult.carry`, `build_gearbox`'s `carry` keyword (accepted,
checked against `before`, and ignored until A's worker lands), and stubs of `plan_carry` and `carry_gates` raising
`NotImplementedError`; in `findings.py`, every new name of §8 at None. B may import all of it from then on.

**Package A owns** `swbuild.py` (the read R, `plan_carry`, `carry_gates`, the carry C, `_read_user_work`'s entities),
`swcom.py` (§10's members), `findings.py` (the names; values only from reviewed logs), `tests/test_swbuild.py`'s fake
and the new `tests/test_swbuild_carry.py`. **Order**: the shapes commit; `plan_carry` and `carry_gates` (pure, with
their tests: B's foresight needs them first); `UserMate.entities` in `_read_user_work`; the read R (open path, then the
not-open path under its conditions); the carry C step by step (insert and states, then mates cluster by cluster, then
the post-check), each with its fake support and tests.

**Package B owns** `workbook/update.py` (`carry_for`, `recorded_old_work`), `workbook/gearbox.py` (`finish_build`
writing `carry`, the new `user_work` and `unsaved_at`), `store.py` (schema 10, the new entries, nested readers,
`unsaved_at`'s newer-file rule), `ui_text.py` (§9), `workbook_gui.py` (`_start_build` passing `carry`, `_finish_build`
saying it, the footer's §9.4 lines), `design/UI-DESIGN.md` §9, and the new `tests/test_workbook_carry.py` plus edits
to the record and question tests. **Order**: after the shapes commit, `carry_for` and the record (schema 10) first;
then the question on `plan_carry`'s foresight once A's pure functions land (stubs until then: test against hand-made
`CarryPlan`s); then the result's sentences on hand-made `CarryResult`s; then the round trip on the fake once A's worker
lands.

**Neither changes the other's files.** A shape change is a stop-and-ask through the coordinator, recorded in this
note's §17 as W9c's §11 did.

## 18. The review's points, and where each went

Must-fix 1 → §3 C.6, §6, D6. Must-fix 2 → §3 R.2, §11.1, §11.2, §13 item 8. Must-fix 3 → §2.3's table, `OldEntity.coaxial`,
§2.2's `UserMate.entities`. Must-fix 4 → §5.1, §3 C.4, D13, §8. Must-fix 5 → the probe (P1, P2). Should-fix 1 → §6, D7.
2 → §5.3, D20. 3 → §5.3, `WHY_NO_FRAME`, §9. 4 → §3 C.5. 5 → §10, §14.1's fake. 6 → §4.2, `ORIGIN_ENTITY_READ`. 7 →
§5.1, `VIRTUAL_READ` (checked against the macro database: assemblies/12 has a virtual part's path in the session's
temporary folder, so `on_disk` reads True). 8 → §3 R.1, R.7. 9 → §4.1, `PERSIST_REFERENCE_SURVIVES_RELOAD`, probe
(d). 10 → §7, D16. 11 → §8's column, the patch rule, P13. 12 → §8 (dropped), §11.5. 13 → §9.1, §9.2. 14 → §1, §2.1,
§2.3, §2.4, §7. 15 → §15. Notes: the 37° wording → §5.3 and §14.1; `FELL_NEW_ERROR` conservative → §6;
`CARRY_INSERT_MARKS` sentence → §9.2; D5 by `ReferenceType2` → §2.2; D14 plain → §9.1; line numbers → §7; nested
reader → §7; `moved`'s tolerance → §6. Probe P1–P13 → `probe/w9d_probes.py` and `W9D-PROBES.md` (P12's third bullet,
another version's file, not taken: the ruling keeps the not-open read to a file the record says the running version
wrote, and `FILE_VERSION_READ` covers the rest without opening one).
