# W9d: Build again… carries the user's work — the interface between planning (B) and the worker (A)

Stage W9d of `ISSUE-1-PLAN.md`: §0.2 K5 (the user's answer), §0.3, §2.1 item 8, **§2.5**, §4 S5 and M9, §5 "W9d", and
*Changes after W9b, W9c's probes and the review of W9c's packages* ("Owed before W9d is designed"). Written before any
W9d code, at `64bec58`, against S5's and P2's readings on both versions (`W9C-PROBES.md`, `W9C-PROBES-REVIEW.md` and
its 2024 addendum, `probe/results/w9c-probes-sw2026-20261117-2.log`, `sw2024/w9c-probes-sw2024-20261117.log`, the
W9c block of `findings.py`), the installed SolidWorks API help (2024's `sldworksapi.chm`, decompiled as the macro
database's connect/12 says) and the macro database. **Revised** after its review (`W9D-INTERFACES-REVIEW.md`,
`f0eb516`) and the coordinator's rulings of 2026-11-17 (§12): every must-fix and should-fix is taken; §18 lists each
review point and where it went. **Revised again** after the W9d probes' two runs on SolidWorks 2026 (34.0.0) and their
review (`W9D-PROBES-REVIEW.md`, `94fbebf`): the contract now says what was measured (§4.1, §8.1, §10, §11), bounds tier
1's face and edge walk (§10, must-fix 1), and folds in the two packages' hand-back notes (`W9D-PACKAGE-A.md`,
`W9D-PACKAGE-B.md`): the shapes and member names as built, and B's requests awaiting the package reviews (§17).

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
    bore_mm: Optional[float] = None   # RULED (§17.1), proposed with the probes' revision: the OLD
                                # gear part's bore in mm from its sidecar (the spec's bore, what its Bore Diameter
                                # global was written from; a blank or 0 Bore is no bore, None); None for the layout, a
                                # carrier, or not known. Only "bore" in a sentence rests on it (§4.4)

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
plan's structural reasons and `again.made_new` (`MadeNew.why`). A part made new is found in `again.build` and
`again.made_new` by its Gears row: a planet copy's id (*Planet copy 2*) is never in a job's or a `MadeNew`'s
`gear_ids`, which hold the row (*Planet*), so the lookup takes `planetary.copy_of(id)[0]`, for `names` and
`why_new` alike; and the reasons the sentences read (`update.why_new_of`) are keyed by each copy and by its row too,
the id W9a's features left in a part are recorded by (W9D-DEMONSTRATION-REVIEW.md, *A planet copy made new*,
`7f91037`: before, a copy made new got no names and *its values changed*, and a feature in a planet's part was said
to stay in a part the new revision *does not use*). The window passes it as `kwargs["carry"]` in
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
    coaxial: Optional[bool] = None  # a face on an app gear: a CYLINDER whose axis is the part's Gear Axis
                                # (CylinderParams of the part-level face, in part coordinates, against the line through
                                # the origin along Z, which every recipe's Gear Axis is: spur.py:804's Axis on planes 2
                                # and 3); None when not read (COAXIAL_FACE_READ unset, or not a face on an app gear).
                                # Coaxial is not "bore": Sun's 29 tip and 29 root cylinders read coaxial too
                                # (w9d…-2.log:92); "bore" is said only by §4.4's rule
    unread: str = ""            # why this entity, or its reference, could not be read (a sentence's clause)
    radius_mm: Optional[float] = None   # RULED shape change (the probes' review, §17): a cylindrical face's (or a
                                # circular edge's) radius in mm, from the same part-level read as `coaxial`; None when
                                # not read or not a cylinder or circle. §4.4's "bore" compares it with CarryBody.bore_mm
    capped: str = ""            # §10's cap reached before this face or edge was searched: "candidates" or "seconds";
                                # "" searched (or not a face or edge). A capped entity has no reference, and its mate
                                # is named WHY_TOO_LONG (§2.3)

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
    configurations: Optional[Tuple[str, ...]] = None   # AS BUILT (A's shape change 3): its file's configurations
                                # (GetConfigurationNames on its document); None not read. §5.1's rule: one, today's
                                # insert; several, only with both configuration findings set; None, WHY_CONFIGURATION

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
stays as it is. **As built** (A's note): read inside `Session.mate_info`, whose `swcom.MateInfo` gains `entities` (per
entity `(kind, feature)`, defaulted `()`), not by a separate `mate_definition` call, so the calls every Update and W9a's
old-assembly read make are unchanged. The fake gives the kinds only with `FakeSolidWorks.read_entity_kinds = True`
(default False); B's round trip sets it.

**Also as built, additions only** (A's shape changes 1, 2, 5, 6, 11): `STAGE_CARRY = "carry"` beside the `STEP_CARRY_*`
names (not in `STAGES`; `ui_text.progress_text` falls back to the step's name); the tuples `STEP_CARRY_STEPS` and
`ENTITY_KINDS`; `STEP_CARRY_FEATURES = "find a reference feature again"` (tier 1 on an axis or plane, met only on a
version not known); beside `plan_carry`, `CARRY_KIND_WORDS`, `carry_kind(mate)`, `selection_reversed(kind, entities)`,
`gear_sense(values, params)`, `SEL_*` and `OPEN_READ_ONLY_ROUTE`; `swbuild.read_old_work(sw, carry)` (the read R as a
function of its own) and `STATES_SHOWN_READ_ONLY = "shown read-only"` (`OldWork.states_route`'s value for the read-only
show).

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
WHY_TOO_LONG      = "too long"        # §10's cap reached before the mate's face or edge was searched (OldEntity.capped)
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
| `unmeasured` | (what, finding, version) — what is a kind word ("concentric"), an entity kind ("face", "edge", "vertex", "origin"), "insert", "sub-assembly", "configuration", "gear mate on an app gear" or "leaf"; finding the full name with its year; version "2026". *A 4th slot, whose face or edge (the component's Name2 or the gear id), is B's request 3: requested, awaiting the reviews (§17); B's clause says it without one* |
| `part new` | (gear id, why_new, entity kind, where) — where is "bore" for a cylinder with `coaxial` True whose `radius_mm` is the old part's `CarryBody.bore_mm`/2 (to 1e-4 mm); "axis" for any other cylinder with `coaxial` True (*a face of Sun on its axis*: a tip or root cylinder); "" otherwise (*a face of Sun*). With `bore_mm` None, never "bore" (§4.4) |
| `gone` | (what, name) — what is "gear" (a body with no handle), "shaft" (a layout or carrier feature the new file lacks: the shaft's id), "feature" (an app part's feature the new file lacks: its name). *A 3rd slot, the owner of a feature (the gear id), is B's request 3: requested, awaiting the reviews (§17)* |
| `assembly feature` | (feature name,) |
| `component not carried` | (component Name2,) |
| `unread` | (why clause,) |
| `lightweight` | (component Name2,) |
| `no file` | (file name, "virtual" or "") |
| `leaf` | (sub-assembly Name2,) |
| `not found` | (entity kind, component Name2, file name) |
| `configuration` | (component Name2, its referenced configuration, its document's active one) |
| `no frame` | (component Name2, the mode showing) |
| `differs` | (what differed: "entities", "alignment", "ratio", "sense"); or ("left", name in the new assembly): a retry whose read-back or delete raised, so the mate may stand in the new assembly under that name (as built) |
| `refused` | (SolidWorks' sentence,): `WHY_REFUSED`, SolidWorks refused to make it again or to select what it joins (as built) |
| `old unread` | (why clause,) |
| `too long` | (entity kind, component Name2 or gear id, file name, "candidates" or "seconds") — the 4th slot is which cap was reached, for the log; the sentence does not say it |
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
`ok      made UserLock1 again, on in H, N and L`, `CHECK   not carried: Concentric5 (part new)`, `FIXED   …`); **as
built**, worded by A in `CarryResult.log_lines()`, not by B. `old_read` on a carrying Build again… is `""` when read,
`OLD_NOT_OPEN` when the old assembly was unread, the read's sentence when it raised (A's note).

**As built since** (§17.1), each at the end of `CarryResult`: `anchors` (new Name2, `CarryBody.old` or "", B's request
1, ruled); `facts` (what was read but not judged, for the log); `changed_files` (the files C.8 read changed on disk,
base names); `after_unread` (why C.8's times and flags could not be read, "" when read); `resolved_in_old` (the old
assembly's lightweight instances the carry resolved, D10 †). The code after (B's request 2) was ruled no field.

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
        `GearboxRecord.solidworks`), **and** `FILE_VERSION_READ_ON_<year>` is set **and** the file's own last saved
        version (`ISldWorks.VersionHistory(path)`, read closed: its **last** entry, compared by its **number**, never
        its year label: 2026 labels itself 2025, and a 2026 file's history begins with its template's 17000) is the one
        the running SolidWorks writes (`GetLatestSupportedFileVersion`). **While that finding is None the job never
        opens a closed old assembly** (the re-check's R1: the record cannot see a save on the other SolidWorks after
        the last job);
      - `DEPENDENCIES_READ_ON_<year>` is set **and** every file the old assembly references
        (`ISldWorks.GetDocumentDependencies2(path, False, False, False)`, read closed) was last saved by the running
        version too (S-f, §11.2: so a part of the user's that another SolidWorks saved is never loaded by the job).
        The paths it gives are the **stored** ones and **top level only** (Traverse False, `w9d…-1.log:124-125`). So
        the read is **refused** (`OLD_UNREAD`) when any dependency is itself an assembly (`.SLDASM`: its own files are
        not listed, until a reviewed run shows Traverse True listing them, the probe's `sub` (t)), when any path is not
        on disk (`os.path.isfile`), or when any one's `VersionHistory` does not read;
      - **no stored dependency path suggests a copied or moved folder** (ruled, the demonstration's review §5): the
        paths `GetDocumentDependencies2` gives with Searchflag False are those **stored** in the assembly when it was
        last saved, not the files SolidWorks will load; for an assembly copied or moved and not saved since they name
        the old folder, while SolidWorks loads the copies its search rules find beside it, whose versions were never
        read. So the read is **refused** (`OLD_UNREAD`, *"RangeBox.SLDASM was moved or copied since it was last saved:
        open it in SolidWorks first"*) when any stored path lies outside the old assembly's own folder **while a file of
        the same name sits in that folder**. A library part referenced in place, with no namesake beside the
        assembly, does not refuse. Unmeasured (§11.2): whether Searchflag True gives the paths SolidWorks would load;
      - no document is open in the session but those `Carry.app_files` names, **and**, when any is open,
        `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_<year>` is True (S-e);
      - `OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN_ON_<year>` is that route (set on both) and
        `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_<year>` is True (the close of a read-only document, shown or not, under no
        dialog: GOTCHAS §100's CAM box follows the file's version);
   3. the components (`components()`), each one's frame in the mode showing (`find_component` with `lightweight_ok`,
      `component_frame`), referenced configuration and its document's active configuration (gated,
      `REFERENCED_CONFIGURATION_READ`), virtual (§5.1), pattern instance (gated, D12), on disk; the app bodies' frames;
   4. the states per mode by the route `COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_<year>` names (§11.1; **set on
      2026**, so there the states are read unshown on both paths); only when it is None (2024 until its run) and this
      job opened the document read-only (all of R.2's conditions held), by showing each mode in that read-only
      document; else not read (`suppressed_in` None, D2 †);
   5. every user mate's definition (`Session.mate_definition`, §10), every entity classified by `ReferenceType2` (§4),
      tier 1's part-level references read through the component (§4.1; a face's or an edge's by §10's walk, one per
      component, prefiltered, capped), a face's `coaxial` and `radius_mm` from the same read (gated,
      `COAXIAL_FACE_READ`); the root's `Name2` read as W9c's `_read_user_work` has it (never on an assembly with a
      lightweight component; the probe does not license more, §11.5). The job's own read-only document is read **as
      loaded**, never rebuilt (§11.2);
   6. `GetSaveFlag` of every document again: any turned on is `OldWork.marked` (§0.3's STOP: the carry does nothing
      more, `stopped` says so, the build goes on). **The job's own read-only document** (the not-open path) is not in
      R.1's list; it is judged from its flag read **straight after its `OpenDoc6`**: True there (warning 32,
      NeedsRegen, measured beside a changed app part, `w9d…-1.log:126-127`) is logged, not a mark; only a turn after
      that read counts, as for every other document. The turn its per-mode show makes (R.4's None path only: the job's
      own show in its own read-only document, closed unsaved) is logged and not counted. *As built* A leaves that
      document out of `marked` altogether; the fix round reads it after the open as here (§17);
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
   4. each inserted (`add_component` at its frame's origin, its configuration as §5.1 rules: passed explicitly,
      `AddComponent5(path, 0, "", True, configuration, …)`, whenever `CARRY_INSERTS_IN_A_CONFIGURATION` is set; a file
      of one configuration by the app's insert today), its referenced configuration read back (another is not carried:
      the component deleted again by `delete_component`, the job's own, and named `WHY_CONFIGURATION`), placed
      (`place_component`), fixed where it was fixed (`fix_component`); first mode showing;
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

**One change to the old assembly that is not a STOP** (D10 †, ruled): C.3 opens a carried lightweight component's part
to insert it, and lightweight is a state of the file in the session (`w9d…-1.log:121`), so the old assembly's
lightweight instance may be resolved by it. That change, **confined to that component going from lightweight to
resolved** (and the old assembly's save flag if it turns on with it, which is unmeasured), is not a STOP and is not
undone: the worker reads each such instance's state in the old assembly before C.3 and after C.8, and the result says
it when it happened (`CarryResult.resolved_in_old`, §9.2). **Every other change to the old assembly remains a STOP**,
as §0.3 says: another component's state, a frame, a mate, a value, a flag turned on with nothing of this kind to
explain it.

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
| a face | **measured** by r3: 5 faces on two files, read, resolved `Ok`, round trip `IsSame` both ways, 4 mates remade equal (`w9d…-2.log` :83-89, :96-101) | not yet (the 2024 run) | `PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_<year>` |
| an edge | **measured** by r3: 1 circular edge (`w9d…-2.log` :86, :90) | not yet | `PERSIST_REFERENCE_ROUTE_FOR_EDGES_ON_<year>` |
| a vertex | not measured | not measured | `PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_<year>` (None; nothing in W9d sets it) |
| any, after a reload (the not-open path) | **measured**: 6 references (5 faces, 1 edge) resolved `Ok` in their parts reopened alone, kind, place and area as read (`w9d…-2.log` :103-104) | not yet | `PERSIST_REFERENCE_SURVIVES_RELOAD_ON_<year>` |
| a whole component (a lock) | **measured** (tier 3) | **measured** | — |

For a feature, the part-level entity is found by name in the part (`FeatureByName`, S5). **For a face or an edge**, the
part-level entity is the one face (or edge) of the component's part that, carried into the assembly by
`IComponent2.GetCorresponding`, is `ISldWorks.IsSame` as the mate's entity: walked **once per component**,
**prefiltered** by area (a circle's radius for an edge), **exactly one** match required, and **capped** (§10's four
rules). Then the part's `GetPersistReference3`, resolved by its `GetObjectByPersistReference3`, must answer
`swPersistReferencedObject_Ok`, to the entity's own kind and `IsSame` as the part-level entity. The two routes the
contract first named read nothing on 2026: `GetCorrespondingEntity2` gives nothing for a mate's entity, and the part's
`GetPersistReference3` on the assembly entity resolves `swPersistReferencedObject_Invalid` (`w9d…-1.log:51-80`). The
walk's cost grew through the measured session (§11.4), hence the cap.

`w9d…-1.log` is `probe/results/w9d-probes-sw2026-20261117-1-face-routes-none.log`; `w9d…-2.log` is
`…-2-faces-r3-clean.log` (both 34.0.0).

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
whether the old entity was the gear's `Gear Axis` or a cylindrical face of it, **provided the face is coaxial**. Where
the face came from does not decide: the app's own faces are not all coaxial either. Sun's 58 root fillets are app-made
cylinders of radius 0.475 mm off the axis, while its 29 tip and 29 root cylinders are coaxial; a face of a feature the
user cut into the gear part (W9a's keyway, an off-axis Ø 3 hole) is not (`w9d…-2.log:92`). **The `coaxial` read
decides** (S-d): an axis named `Gear Axis`, or a **cylindrical face** with `coaxial` True, is taken as `Gear Axis`;
a cylindrical face with `coaxial` False or None, and **every conical face and circular edge** (not read), is
`WHY_PART_NEW` on a part made new and tier 1 on a same file. The other side goes by its own tier. This keeps K5's "a gear mate is found through the
component". Behind `CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_<year>`, which M9 sets only with the remade mate's ratio and sense
read back right (§10).

### 4.4 Tier 4 — a face, edge or vertex of an app part made new

Never re-found (ruled, K5), but for §4.3's gear-mate rule. `WHY_PART_NEW`, subjects (gear, why_new, entity kind,
where): *"Concentric5 was on Sun's bore, and Sun's part is new because its Flank changed; it was not made again."*
"bore" only for a cylinder whose `coaxial` is True **and** whose `radius_mm` is the old part's Bore Diameter/2
(`CarryBody.bore_mm`, to 1e-4 mm; a gear with no bore has none, and with `bore_mm` None nothing is "bore"); any other
coaxial cylinder is *a face of Sun on its axis* (a tooth's tip or root cylinder reads coaxial too, and is not a bore);
otherwise *a face of Sun*, *an edge of Sun*.

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
  `REFERENCED_CONFIGURATION_READ`, **set by M9** on Sprocket-11, whose referenced configuration differs from its
  document's active one: the probe's components all reference their file's only configuration, so it can log the read
  but not show it right, the re-check's R2), beside its file's configurations (`IModelDoc2.GetConfigurationNames` on
  its document, verified). `AddComponent5`'s option 0 inserts a file's **last saved** configuration
  (`swAddComponentConfigOptions_e`), not its document's active one (S-a), so:
  - a file with **one configuration** is carried by the insert the app has today: there is nothing else it could be
    (no gate beyond `CARRY_INSERTS`);
  - a file with several is carried only while `REFERENCED_CONFIGURATION_READ` and
    `CARRY_INSERTS_IN_A_CONFIGURATION_ON_<year>` are True, and then the referenced configuration is **always** passed
    explicitly (`UseConfigForPartReferences` True, `ExistingConfigName`: the same member, arguments the app has not
    passed), whatever the document's active one is;
  - otherwise, or where it would not read, the component is named (`WHY_CONFIGURATION`), never carried in another.
  After the insert it is read back; another is deleted again (`delete_component`, the job's own) and named.
- **Named**: a file not on disk (`WHY_NO_FILE`); a **virtual component** (`WHY_NO_FILE`, "virtual"), told by a `^` in
  its file name (should-fix 7): the macro database has a virtual part's path in the session's temporary folder
  (assemblies/12, "a virtual part (whose path is in the session's temporary folder)"), so `os.path.isfile` reads True
  and must not decide; the `^` name is reading/01's rule for a virtual component's name. Unmeasured for a component's
  path read by `_component_path`; `IComponent2.IsVirtual` (a documented get) decides once `VIRTUAL_READ_ON_<year>` is
  set (the probe reads it negative only; no fixture has a virtual component).
- **Said, not read**: a sub-assembly comes over rigid (in the standing list only where `CARRY_INSERTS_A_SUBASSEMBLY`
  is True on the version and no sub-assembly is named as not carried; review of the second 2026 run, must-fix 2);
  display states and appearances set in the assembly are not
  carried; a component pattern is not carried and an instance comes over as a component of its own (D12 †); a part of
  the user's with in-context references to the old assembly's parts still refers to them (M4 unmeasured, said once
  whenever a user part is carried).

### 5.2 States per mode

- Old mode → new mode by name, case aside. A mode of the new revision the old assembly has not takes the old record's
  first mode's state (`Carry.first`, D14), said. An old mode the new revision has not (removed, or renamed: a renamed
  Modes row is one of the edits that reach Build again…, `update.py:1508-1512`, so this is a central case) loses its
  states, said plainly.
- With no clean unshown route and the old assembly open (D2 †), each component takes the mode showing's state in every
  mode, said once for all. That is the path where `COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_<year>` is None (2024
  until its run); on 2026 it is set, with `…_READS_UNSAVED` True, and the states are read unshown on both paths.
- A component set lightweight sets every instance of its file lightweight (one Sprocket set so read every
  `Sprocket.SLDPRT` instance lightweight, `w9d…-1.log:121`), so D10's `WHY_LIGHTWEIGHT` falls on each of them, as each
  one's own read says; the question is not surprised by it. A mate's own suppression flag is what `IsSuppressed2` reads,
  not its effective state (Sprocket-4's mates read on in L, where it is suppressed, `:113`): C.6.1's "left as
  SolidWorks has it" rests on that.
- A lightweight component (state 1 or 4 in the mode showing) is inserted resolved and never set lightweight (D10): the
  user's next save of the new assembly must not meet SOLIDWORKS CAM's box. Opening its part to insert it may resolve
  the old assembly's instance too (lightweight is per file in the session): read before and after, said, not a STOP
  and not undone (§3 *One change …*, D10 †).

### 5.3 Placement

- **Clusters**: the user's components joined through user mates whose entities are on two or more user components
  (user–user mates), connected components of that graph, numbered in first-mate order; a component no user–user mate
  joins is a cluster of its own; a user mate with no user component (between app bodies, the layout, the assembly) is
  cluster −1, one mate per cluster, and falls back alone.
- **Anchor**, per component (D20, should-fix 2, and the ruling after the demonstration's review):
  - **a component fixed in the old assembly has no app anchor**: it is placed by its world frame (`old(component)`
    unchanged), whatever its cluster reaches. The user fixed it in the world, and a gear its cluster is locked to may
    stand otherwise in the new revision (the fixture's Housing-1, fixed and joined to Sprocket-8's cluster on Sun);
  - **a floating component** keeps the order: its own user lock to an app body first; then its cluster's anchor (the
    first user lock in mate order from one of the cluster's components to an app body; then any other user mate to an
    app body; then the layout or the assembly, the world frame).
  A body with no handle in the new revision is passed over. None: the world frame.
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
  as "which it did not in H, the mode RangeBox.SLDASM showed". The excuse covers the mate's code, and a body's
  over-definition only where every mate of the cluster on that body is back in its old error; it **never excuses a
  gear's tie** (the first run's review, §4; K2): a gear free to turn in the new revision before the cluster and not
  free after it is tied by that cluster, whatever codes its mates read, and the cluster falls back (`FELL_TIE`).
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
`limit angle`, `lock`, `gear`), and set to the words whose mates M9 remade clean. `REFERENCED_CONFIGURATION_READ`, a
read with no positive case in the probe, is patched True in M9's process and set from M9's reading of Sprocket-11
(the re-check's R2). In the table `p24` is the 2024 probe run's log, `probe/results/sw2024/w9d-probes-sw2024-20261118.log`
(§8.3).

| Finding (`_ON_<year>`) | Kind | Settled when | What it gates | Set by |
|---|---|---|---|---|
| `OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN` | read (set, both) | its route string | the not-open read's open | W9c probes s5 (d) |
| `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` (new) | read | True | the not-open read at all (its close), and its per-mode show | W9d probe `state` (h): 2026 `w9d…-1.log:128-129`; 2024 `p24:150-151` |
| `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` (new) | read | True | the not-open read with app documents open (one changed) | W9d probe `state` (g): 2026 `w9d…-1.log:126-127`; 2024 `p24:148-149` |
| `FILE_VERSION_READ` (new) | read | its route string | the not-open read at all: unset, a closed old assembly is never opened (R1) | W9d probe `state` (v), only with its negative control: a file the other version saved, read closed (S-b): 2026 `w9d…-1.log:122-123` (a 2024-saved control); 2024 `p24:143-144` (a control 2026 saved, read closed with no dialog) |
| `DEPENDENCIES_READ` (new) | read | its route string | the not-open read at all: every referenced file read closed, each last saved by the running version (S-f); top level only, so a sub-assembly dependency, a path not on disk or a history that does not read refuses (§3 R.2) | W9d probe `state` (v): 2026 `w9d…-1.log:124-125`; 2024 `p24:145, 147`, each path under the copy (a plain copy of the folder refused, `p24:142`) |
| `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` (exists, None) | read | its route string | per-mode states read unshown | W9d probe `state` (b)–(d): 2026 `w9d…-1.log:114-118`; 2024 `p24:132-134, 137` |
| `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED` (new) | read | True | that route on an open old assembly with unsaved changes | W9d probe `state` (e): 2026 `w9d…-1.log:119-120`; 2024 `p24:138-139` |
| `PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES` | read (set, both) | its route string | tier 1 on axes and planes | W9c probes s5 (b) |
| `PERSIST_REFERENCE_ROUTE_FOR_FACES`, `_FOR_EDGES` (new) | read | a route string | tier 1 on faces, edges, by §10's walk (grouped, prefiltered, counted, capped) | W9d probe `faces` (b), **r3**: 2026 `w9d…-2.log:83-90` (r1 and r2 read nothing, `w9d…-1.log`); 2024 `p24:53-87` (the walks did not grow; the edge prefilter slower than the walk, `p24:94`) |
| `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` (new) | read | a route string | tier 1 on vertices | nothing in W9d: None (2026: `…-1.log:1571`) |
| `PERSIST_REFERENCE_SURVIVES_RELOAD` (new) | read | True | tier 1 on the not-open path | W9d probe `faces` (d), r3's references: the kind, the place in the part (a plane's offset, a cylinder's or circle's axis) and a face's area, the part unmarked by the resolve (S-c): 2026 `w9d…-2.log:103-104`; 2024 `p24:105-106` |
| `COAXIAL_FACE_READ` (new) | read | True | `OldEntity.coaxial` and `radius_mm` on a cylindrical face: §4.4's "bore" (with the radius) and §4.3's gear-mate rule on a face | W9d probe `faces` (b), r3's part-level face: the bore True, every plane False, **Sun's User Keyway (off-axis) False** (S-d), Sun's root fillets False: 2026 `w9d…-2.log:92-93`; 2024 `p24:89-90`, the same counts |
| `REFERENCED_CONFIGURATION_READ` (new) | read | True | the referenced configuration read on a file of several configurations; unset, such a component is named | **M9** (the re-check's R2; the probe logs the read as a fact and proposes nothing): 2026 **True**, M9's second run on 34.1.1, SprocketConf-1 in Z20 (`w9d-demo…-1.log:823, 1438, 1516`, proposal 1555; read-only, `…-2.log:738`); 2024 **True**, M9's confirming run on 32.5.0, SprocketConf-1 in Z20 (`…-1…log:820, 1519`, proposal 1558) |
| `VIRTUAL_READ` (new) | read | True | `IsVirtual` instead of the `^` rule | probe reads it negative only: None until a run meets a virtual component (2026: M9's fixture has none, `w9d-demo…-1.log:1568`; 2024 negative only, `p24:92`) |
| `PATTERN_INSTANCE_READ` (new) | read | True | `IsPatternInstance`: the per-instance sentence (D12) | probe reads it negative only: None until a run meets a pattern (2026: M9's fixture has none, `…-1.log:1569`; 2024 negative only, `p24:92`) |
| `ORIGIN_ENTITY_READ` (new) | read | True | an origin as a mate entity | nothing in W9d: None (2026: `…-1.log:1570`) |
| `SUBASSEMBLY_OPEN_MARKS` (new) | read | **False** | a sub-assembly not loaded, opened to insert it | W9d probe `sub` (a): 2026 `w9d…-1.log:135-136`; 2024 `p24:158-159` |
| `SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED` (new) | read | **False** | a sub-assembly loaded as a component, opened to insert it | W9d probe `sub` (c): 2026 `w9d…-1.log:141-142`; 2024 `p24:163-164` |
| `SUBASSEMBLY_READ_ONLY_INSERT` (new) | read | True | a sub-assembly opened read-only, then inserted | W9d probe `sub` (b): 2026 `w9d…-1.log:138-139`; 2024 `p24:160-161` |
| `SUBASSEMBLY_INSERT_ROUTE` | read (set, both) | its route string | the insert itself | W9c probes p2 |
| `CARRY_INSERT_MARKS_USER_DOCUMENTS` (new) | a fact | — (True or False) | nothing: True adds a sentence (§9.2) | W9d probe `faces` (c): 2026 `w9d…-2.log:101-102`; 2024 `p24:98-104` |
| `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY` (new) | a fact | — (True or False) | nothing: the worker reads the old instance before and after whatever it holds, and the result says what it read (D10 †); nothing in `src` reads the finding | M9 `carry` (SprocketLight-1), as read: 2026 **True** (`w9d-demo…-1.log:1402, 1408, 1410`; the result's sentence 1397), added to `findings.py` as a pair by the coordinator's ruling; 2024 **True** (`…-1…log:1403, 1409, 1411`; the result 1398) |
| `CARRY_INSERTS` (new) | write | True | user parts inserted, placed, fixed, their states set in every mode and read back | M9: 2026 **True** (`w9d-demo…-1.log:1477-1518`, proposal 1553; closed, `…-2.log:777-834`); 2024 **True** (`w9d-demo-sw2024…-1…log:1478-1537`, proposal 1556; closed, `…-2…log:773-836`) |
| `CARRY_INSERTS_IN_A_CONFIGURATION` (new) | write | True | an insert in a referenced configuration other than the document's active one | M9: 2026 **True** (`…-1.log:859-860, 1515`, proposal 1554); 2024 **True** (`…-1…log:1518`, proposal 1557) |
| `CARRY_INSERTS_A_SUBASSEMBLY` (new) | write | True | a user sub-assembly inserted by its file | M9, if its fixture holds one (else None): 2026 None, the fixture has none (`…-1.log:1566`); while unset the standing list does not say *sub-assemblies come over rigid* (§9.1) |
| `CARRY_REMAKE_KINDS` (new) | write | the kind's word is in the tuple | which kinds are remade (§4.5, D4) | M9: 2026 the eight shown, `coincident`, `concentric`, `parallel`, `distance`, `angle`, `limit distance`, `lock`, `gear` (`…-1.log:1484, 1486, 1499, 1556-1563`, proposal 1564; closed, `…-2.log:784, 786, 800`); perpendicular, tangent and limit angle not in the fixture, so named; 2024 the same eight (`…-1…log:1487, 1489, 1502, 1559-1566`, proposal 1567; closed, `…-2…log:786, 788, 802`) |
| `CARRY_GEAR_MATE_ON_AN_APP_GEAR` (new) | write | True | §4.3's rule | M9: 2026 **True** (`…-1.log:1457, 1464, 1484`, proposal 1565; closed, `…-2.log:784`); 2024 **True** (`…-1…log:1487`, proposal 1568; closed, `…-2…log:786`) |
| `CARRY_REMAKES_ON_A_LEAF` (new) | write | True | a mate on a leaf of a user sub-assembly | nothing in W9d: None (2026: `…-1.log:1567`) |

Dropped after the review: `ROOT_COMPONENT_UNRESOLVED_READ` (should-fix 12; the probe cannot tell whether that read marks,
so nothing may rest on it: the root read keeps `_read_user_work`'s rule; the probe logs it as a fact only) and the
probe's `MATE_REMAKE_ON_FACES_AND_EDGES_ROUTE` (P13; the remake is `CARRY_REMAKE_KINDS`' with the face and edge routes).

`swbuild.carry_gates(work, carry, revision) -> List[Tuple[str, str]]` (pure) returns `(step, finding)` for each gate
not settled that something in `work` needs, for A's naming and B's question, as `in_place_gates`. Steps:
`STEP_CARRY_OPEN`, `STEP_CARRY_STATES`, `STEP_CARRY_INSERT`, `STEP_CARRY_CONFIGURATION`, `STEP_CARRY_SUBASSEMBLY`,
`STEP_CARRY_FACES`, `STEP_CARRY_EDGES`, `STEP_CARRY_VERTICES`, `STEP_CARRY_RELOAD`, `STEP_CARRY_ORIGIN`,
`STEP_CARRY_KIND` (one per kind word), `STEP_CARRY_GEAR_MATE`, `STEP_CARRY_LEAF`. **As built** (A's note):
`STEP_CARRY_KIND` is given **once**, however many kinds it keeps back, each kind word being in its mate's
`CarryNamed.subjects`; and `STEP_CARRY_FEATURES` gates tier 1 on an axis or plane on a version not known. For an
`OLD_UNREAD` work the not-open read's gates are `FILE_VERSION_READ`, `DEPENDENCIES_READ`,
`OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` and the route, whichever are unset; `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` depends on
what is open at the press, so the worker's `unread` sentence says it.

### 8.1 The values for SolidWorks 2026 (34.0.0)

Measured by the W9d probes' two runs on **34.0.0** and set as the probes' review gives them (`W9D-PROBES-REVIEW.md`,
*The findings, one by one*). Package A's fix round copies each into `findings.py` as `<NAME>_ON_2026`, its comment
carrying the caveat and naming the revision; W9c's S5 ran on 34.1.1, and one reading differs between the two (the
marking route, first row). Each `_ON_2024` is set since from the 2024 run, to its 2026 twin (§8.3). `-1.log` and `-2.log`
are `w9d…-1.log` and `w9d…-2.log` of §4.1.

| Finding | Set `_ON_2026` to | Caveat the comment must carry |
|---|---|---|
| `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` | `"IConfiguration.GetComponentSuppressionState(Name2)"` | Agreed with the shown truth on 3 components × 3 modes, from an unmarked start, marking nothing (`-1.log:114-118`). Covered: suppressed in the mode showing (Housing-1 in H) and in another (Sprocket-4 in L). It reads a lightweight component False (not suppressed) (`:121`). Top-level `Name2` only. Run on **34.0.0**: there `GetRootComponent3(True)` per configuration marked nothing (`:117`), where W9c measured it marking on 34.1.1 (`w9c…-2.log:282`). Marking can differ by revision or state, so R.6's check after the read stays the guard. |
| `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED` | `True` | One component suppressed in one mode, unsaved, read right (`:119-120`). |
| `FILE_VERSION_READ` | `"ISldWorks.VersionHistory(path), its last entry against GetLatestSupportedFileVersion"` | The copy just saved read last `19000[2025/260]` against latest 19000. The negative control, a 2024-saved assembly, read `17000[2024/282]` (`:122-123`). Compare the **number**, never the year label: SolidWorks 2026 labels itself 2025. Take the **last** entry: the 2026 file's history begins with 17000 (its template). |
| `DEPENDENCIES_READ` | `"ISldWorks.GetDocumentDependencies2(path, False, False, False), each one's VersionHistory"` | It named all nine parts (`:124-125`). Traverse is False, so the paths are **top level only**: a referenced sub-assembly's own files are not listed. The paths are the **stored** ones (Searchflag False). Here the copy had just been saved in place in (a), so they were the copy's files. That is my inference: the JSON keeps file names only. A path not on disk, or a history that does not read, is not the running version. |
| `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` | `True` | Two user parts stood in for the app documents R.2 allows: one changed (a global added), one unchanged. Each was open, with the same flag and not read-only after the open and after the shows, and the change was kept (`:126-127`). The read-only assembly itself read **modified** straight after its open (warning 32, NeedsRegen) beside the changed part. See below. |
| `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` | `True` | Files saved by this version only. Closed by `QuitDoc` **with its flag True** (shown, NeedsRegen), with no dialog, every document it loaded gone, no file time changed, and the open parts as they were (`:128-129`). |
| `SUBASSEMBLY_OPEN_MARKS` | `False` | A healthy one-part sub-assembly with no configurations of its own, opened Silent and not loaded: flag False straight after and 5 s later (`:135-136`). One with a missing part marks (W9c, `SUBASSEMBLY_MISSING_PART_READS`). |
| `SUBASSEMBLY_READ_ONLY_INSERT` | `True` | Inserted with its child. The sub-assembly read flag False and read-only after the insert; the host it went into read modified, as it is the job's own (`:138-139`). |
| `SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED` | `False` | Loaded as a component of an open host; `OpenDoc6` answered warning 128, flag False before, after the open and after the insert (`:141-142`). |
| `PERSIST_REFERENCE_ROUTE_FOR_FACES` | r3's route string as proposed (`-2.log:89`): `"each face (or edge) of the component's part carried into the assembly by IComponent2.GetCorresponding, the one ISldWorks.IsSame as the mate's entity (exactly one), then the part's GetPersistReference3, resolved by its GetObjectByPersistReference3"` | 5 faces on two files: one cylinder (a bore), three sprocket end planes, one Sun end plane. r1 is dead on 2026: `GetCorrespondingEntity2` gives nothing for a mate's entity, so `GetPersistReference3(None)` fails. r2 is dead too: the reference resolves `swPersistReferencedObject_Invalid`. **The walk's cost grew through the session** (0.26 s to 8.1 s for the same 163 faces), and the contract bounds it (must-fix 1). |
| `PERSIST_REFERENCE_ROUTE_FOR_EDGES` | the same string (`-2.log:90`) | One circular edge; 482 edges walked in 8.2 s. |
| `PERSIST_REFERENCE_SURVIVES_RELOAD` | `True` | 6 references (5 faces, 1 edge) resolved `Ok` in their parts reopened alone and unchanged on disk: kind, place and area as read, nothing marked (`-2.log:103-104`). A part edited and saved since may resolve otherwise. Any code but `Ok`, or another kind, is `WHY_NOT_FOUND`. |
| `COAXIAL_FACE_READ` | `True` | Cylinders only, by `CylinderParams` of r3's part-level entity, in part coordinates (`-2.log:92-93`). Positives: the sprocket's bore, and Sun's 29 tip and 29 root cylinders. Negatives: Sun's User Keyway (Ø3 at (5, 0)), **Sun's 58 root-fillet cylinders (r 0.475, app-made and off-axis)**, and every plane. |
| `CARRY_INSERT_MARKS_USER_DOCUMENTS` | `False` | One case: user parts loaded as components of the open old assembly, unchanged, opened (activated) and inserted into a second assembly, which marked none of them (`-2.log:101-102`). A user part open in its own window with unsaved edits is not measured. |
| `REFERENCED_CONFIGURATION_READ` | stays **None** here | Every component references its file's only configuration (`-2.log:94`). M9 set it True on SprocketConf-1 (R2): §8.2. |
| `VIRTUAL_READ`, `PATTERN_INSTANCE_READ` | stay **None** | Read negative only (`-2.log:95`). |

"See below" in the `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` row is the review's 3 (a), taken into §3 R.6 and §11.2: the
job's own read-only document is judged from its flag straight after its open, and read as loaded. "My inference" in the
`DEPENDENCIES_READ` row is the reviewer's; the 2024 run logs each dependency's place to settle it.

These reads were measured on 34.0.0. M9's second run read the closed path clean on **34.1.1** too, the read-only open
and its close (`w9d-demo-sw2026-20261118-2-carry-closed-clean.log:771-772`); nothing was set again from it.

### 8.2 The values M9 set for SolidWorks 2026 (34.1.1)

Measured in M9's second run on **34.1.1** and set as its review gives them (`W9D-DEMONSTRATION-REVIEW.md`, *The second
run on SolidWorks 2026 (34.1.1), and `41afa37`*, §4, `7996089`). "Log 1" is
`probe/results/w9d-demo-sw2026-20261118-1-whole-closed-read-mode-fault.log` (snapshot `f7c2f0d`; `fixture`,
`carry-gates`, `carry`, `carry-closed`), "log 2" `…-2-carry-closed-clean.log` (snapshot `41afa37`, `carry-closed`
alone). The five writes were patched True together in that run's process (log 1:794-798, log 2:80-84), the kinds as
all eleven. `findings.py`'s M9 block carries each caveat in full; `tests/test_findings.py` pins the values to the logs.
Each `_ON_2024` is set since from M9's confirming run on 2024, to its 2026 twin (§8.4).

| Finding | `_ON_2026` | Rests on (log 1 unless said) | Its main caveat |
|---|---|---|---|
| `CARRY_INSERTS` | `True` | 1477-1482, 1489, 1503, 1505, 1512, 1518, 1534, 1404, 1406; proposal 1553; closed, log 2:777-782, 789, 806, 808, 818, 834 | the fallback shown is `FELL_TIE` only; the other fallbacks, the per-mode fix, `same_error`, `moved`, a clash, a mode new or gone and a stop part way are the fake's only; the fixed state is read in the mode showing |
| `CARRY_INSERTS_IN_A_CONFIGURATION` | `True` | 859-860, 1515; proposal 1554 | one part of two configurations, its document's active one Default |
| `REFERENCED_CONFIGURATION_READ` | `True` | 823, 1438, 1516; proposal 1555; read-only, log 2:738 | on a lightweight or suppressed component the document's configuration reads '' (821-822) |
| `CARRY_REMAKE_KINDS` | the eight kinds | 1484, 1486, 1499, kinds 1556-1563; proposal 1564; log 2:784, 786, 800 | FlipDimension 0 and Flipped False on every distance and angle; a gear mate of the other sense not remade on SolidWorks; perpendicular, tangent and limit angle named |
| `CARRY_GEAR_MATE_ON_AN_APP_GEAR` | `True` | 1457, 1464, 1484; proposal 1565; log 2:784 | on Sun, a part made new; an app gear reused as the same file not shown; alignment 2 not judged |
| `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY` | `True`, a fact | 1402, 1408, 1410; the result 1397 | one component, set lightweight in the session; read by nothing in `src` |
| `CARRY_INSERTS_A_SUBASSEMBLY`, `CARRY_REMAKES_ON_A_LEAF`, `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`, `ORIGIN_ENTITY_READ`, `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` | stay **None** | proposals 1566-1571 | none is in the fixture; each item is named with its finding and left in the old assembly |

What this leaves settled, by version: on **2026** every gate of §8 but the six of the last row, the probes' reads on
34.0.0 (§8.1) and M9's writes on 34.1.1 (this table); on **2024** the same, from the probes' fourteen reads on 32.5.0
(§8.3) and M9's confirming run on 32.5.0 (§8.4), each 2024 value its 2026 twin's.

### 8.3 The values for SolidWorks 2024 (32.5.0)

Measured by W9d's probes in one fresh session on **32.5.0** from `891a707` (`4623701`; `faces`, `state` and `sub`,
0 failed) and set as their review gives them (`W9D-PROBES-REVIEW.md`, *The 2024 run (32.5.0, from `891a707`),
reviewed*, `23107c2`). `p24` is `probe/results/sw2024/w9d-probes-sw2024-20261118.log`, its JSON
`w9d-probes-20261118-051605.json`; the JSON's `proposal` is `{}`, as in the 2026 probe runs, so the pins in
`tests/test_findings.py` are the log's lines and the JSON's `sections`. Every one of the fourteen is set to **its
2026 twin's value**, written in `findings.py` as that twin (the two r3 route strings must equal
`swcom.PERSIST_ROUTE_R3`, which `entity_references` compares); `findings.py`'s 2024 block carries each caveat.

| Finding | `_ON_2024` | Rests on (`p24`) |
|---|---|---|
| `PERSIST_REFERENCE_ROUTE_FOR_FACES` | r3, as 2026 | 53-85 (r1 and r2 dead on every entity, r3 clean on all five faces), 86 |
| `PERSIST_REFERENCE_ROUTE_FOR_EDGES` | r3, as 2026 | 68, 83, 87 |
| `PERSIST_REFERENCE_SURVIVES_RELOAD` | `True` | 105-106 |
| `COAXIAL_FACE_READ` | `True` | 53, 58-77, 89-90 (2026's counts exactly) |
| `CARRY_INSERT_MARKS_USER_DOCUMENTS` | `False` | 98-104 |
| `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` | `"IConfiguration.GetComponentSuppressionState(Name2)"` | 132-134, 137 (W9c's 2024 candidate, `GetRootComponent3(True)`, had marked; this one marked nothing, 136) |
| `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED` | `True` | 138-139 |
| `FILE_VERSION_READ` | 2026's route | 143-144 |
| `DEPENDENCIES_READ` | 2026's route | 145, 147; a plain copy refused, 142 |
| `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` | `True` | 148-149 (the read-only assembly marked straight after its open, warning 32, as on 2026) |
| `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` | `True` | 150-151 |
| `SUBASSEMBLY_OPEN_MARKS` | `False` | 158-159 |
| `SUBASSEMBLY_READ_ONLY_INSERT` | `True` | 160-161 |
| `SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED` | `False` | 163-164 |

Stay None on 2024, as on 2026: `REFERENCED_CONFIGURATION_READ` (every component references its file's only
configuration, `p24:91`; the 2024 demonstration's SprocketConf-1 set it since, as M9 did on 2026, §8.4), `VIRTUAL_READ` and
`PATTERN_INSTANCE_READ` (negative only, `p24:92`), `ORIGIN_ENTITY_READ` and `PERSIST_REFERENCE_ROUTE_FOR_VERTICES`
(nothing in W9d). Every `CARRY_*` write and the lightweight fact are the 2024 demonstration's (§8.4).

**Measured differing from 2026** (facts; nothing in `src` changed for them):
- r3's walks did not grow on 2024: every 163-face walk took 2.26-2.36 s through the session, five repeats 1.68-2.07 s,
  private memory flat (`p24:80-85, 93, 95`). Whether 2026's growth (§8.1) was per call or a slower session is not
  known; 2026's `faces` (b) has not been rerun. The cap stays the answer on both versions.
- The edge prefilter costs more than the walk on 2024: `("circle", 0.005)` kept 82 of 482 edges in 8.05 s, its walk
  0.83 s, against 5.07 s for the full walk (`p24:94`); it lost no match (`p24:97`). The cost is time, never a wrong
  answer, but `swcom.entity_references` reads each candidate's key again per item and filters before it checks the
  clock, so §10's 20 s cap does not bound the filter: the review's should-fix (a key read once per component, the clock
  inside the filter, and for edges on 2024 no circle filter or a per-kind rule 2). M9's fixture has no edge mate.
- 2024 read a 2026-saved file's version history closed, with no dialog and no window left (`p24:143, 168-169`): what
  `FILE_VERSION_READ` needs on 2024. One file read.
- Searchflag, Traverse True and each dependency's place were read for the first time, on 2024 only (`p24:141-142,
  145-146, 165`): Searchflag False (the app's) gives the stored paths, so a plainly copied folder is refused, as ruled;
  Traverse True lists a sub-assembly's parts, a 2024 fact only, so R.2 keeps refusing a sub-assembly dependency.

### 8.4 The values M9 set for SolidWorks 2024 (32.5.0)

Measured in M9's confirming run on **32.5.0** from `5aca9c1`, in two fresh sessions, 0 failed and no STOP, and set as
its review gives them (`W9D-DEMONSTRATION-REVIEW.md`, *The confirming run on SolidWorks 2024 (32.5.0), reviewed*, §2
and §3, `e51de95`). "24-1" is `probe/results/sw2024/w9d-demo-sw2024-20261118-1-fixture-gates-carry-clean.log`
(`fixture`, `carry-gates`, `carry`; JSON `w9d-demo-20261118-060738.json`), "24-2" `…-2-carry-closed-clean.log`
(`carry-closed`; JSON `…-073438.json`). With numbers and instance names masked every `ok` line is 2026's. Each value
is **its 2026 twin's**, written in `findings.py` as that twin; the 2026 caveats of §8.2 hold word for word, and
`findings.py`'s 2024 M9 block adds those below. `tests/test_findings.py` pins the values to 24-1's proposals and JSON
and to the lines cited; `test_workbook_carry.py` carries a Build again… end to end on the fake at 32.5.0 with nothing
patched.

| Finding | `_ON_2024` | Rests on (24-1 unless said) |
|---|---|---|
| `CARRY_INSERTS` | `True` | proposal 1556, every condition True; 1405, 1407, 1478-1485, 1492, 1506, 1508, 1515, 1517, 1521, 1537; closed, 24-2:773, 779-784, 791, 808, 810, 820, 836 |
| `CARRY_INSERTS_IN_A_CONFIGURATION` | `True` | 1518; proposal 1557 |
| `REFERENCED_CONFIGURATION_READ` | `True` | 820, 1519; proposal 1558 |
| `CARRY_REMAKE_KINDS` | the eight kinds | 1487, 1489, 1502, kinds 1559-1566 (the same mates as 2026's); proposal 1567; 24-2:786, 788, 802 |
| `CARRY_GEAR_MATE_ON_AN_APP_GEAR` | `True` | 1487; proposal 1568; 24-2:786 |
| `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY` | `True`, a fact | 1403, 1409, 1411; the result 1398 |
| the six of §8.2's last row | stay **None** | proposals 1569-1574: none is in the fixture |

**Measured differing from 2026** (the review's §3; caveats on every 2024 value):
- *Memory:* SolidWorks 2024 reached 11.03 GB private by the end of `carry`'s Build again… (24-1:1397) and 9.12 GB in
  `carry-closed`'s (24-2:706), against about 6.4 GB for a build with nothing carried (24-1:80, 592); it was given back
  when the copy closed (5.57 and 3.59 GB), and free memory never fell under 8.4 GB. On 2026 SolidWorks stayed under
  2.4 GB. The app reads no memory in a press; whether the question should say so on 2024 is for a ruling (the review
  recommends a known limit only).
- *Time:* the carrying Build again… took 1389 and 1161 s against 723 and 625 s; a build with nothing carried 429 s, so
  the carry adds about 16 to 20 minutes on 2024; R's entity reads 3.7-6.5 s each against 2.1-3.0 s.
- *The face prefilter:* on Sun's 235 faces the area key kept 29 and 58, 87 carried (24-1:829, 24-2:132), against 1
  and 2, 3 carried, on 2026; so on 2024 the 200-candidate cap comes at about 100 teeth for a fillet and 200 for a root,
  and then names the mate. Time, not a wrong answer.
- *Constrained status 5* did not come on 2024 (24-1:1505); nothing in the app reads it.

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
  Gear Generator reads it then only when …* the condition that fails, one of: *it and every file it uses were last saved
  by this SolidWorks* (*a file saved since on another SolidWorks is not read*), *Gear Generator has been shown to read
  which SolidWorks last saved a file (findings.FILE_VERSION_READ_ON_2026)* (or `DEPENDENCIES_READ`), *nothing else is
  open in SolidWorks*, *(findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026)*, *(findings.OPEN_READ_ONLY_KEEPS_OPEN_
  DOCUMENTS_ON_2026)* — then *, so nothing of yours would be carried: open RangeBox.SLDASM in SolidWorks before you
  press, and it is read as it stands there.* While `FILE_VERSION_READ` is None this clause is said whenever the old
  assembly is not open (R1);
- states per mode not readable (D2 †), said **only where `COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_<year>` is None**
  (2024 until its run; on 2026 it is set and the clause is not said): *Your components take, in every mode of
  RangeBox_r2, the state they have in the mode RangeBox.SLDASM shows when you press: whether you suppressed one in
  another mode cannot be read without changing RangeBox.SLDASM.*;
- a mode renamed or removed: *RangeBox_r2 has no mode 2L: what your items were in 2L stays in RangeBox.SLDASM. Its new
  mode 4L takes what they were in H.* (D14, plain);
- a gate not set: *Gear Generator has not yet been shown to carry concentric mates into a new revision on SolidWorks
  2024 (findings.CARRY_REMAKE_KINDS_ON_2024), so Concentric5 and Concentric8 are not made again.*; with `CARRY_INSERTS`
  not set, W9a's sentence follows, led by *Gear Generator has not yet been shown to carry your work into a new revision
  on SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024), so as read at 14:02, …*;
- the version not known (a record no job of this version wrote): W9c's mixed form, *Whether RangeBox_r2 takes your
  work depends on the SolidWorks in use: Gear Generator has been shown to do so on SolidWorks 2026, not yet on
  SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024), and the press reads which it runs on.*; *as built after the
  coordinator's ruling of 2026-11-18:* the mixed form only where `CARRY_INSERTS` itself differs between the versions.
  Where it is alike, the question is foreseen as on each version (`CarryForesight.per_year`): what every version says
  is said as fact, its version words made general (*on the SolidWorks it runs on*, *findings.…_ON_<year>*), and only
  what differs as may, each version's own sentences first behind *If the press runs on SolidWorks 2024:*, the rest
  behind *Whichever it runs on:*. It never says carrying is *not yet shown on the SolidWorks it runs on* when it is
  shown on both (it did, once both were set, until this ruling); with `CARRY_INSERTS` unset on both it says so of
  either, led by `findings.CARRY_INSERTS_ON_<year>`;
- nothing on record: *Anything you added to RangeBox.SLDASM in SolidWorks the press reads first and carries into
  RangeBox_r2 where it can, saying whatever it cannot.*;
- **the standing list of what is not carried as it was**, once, at the end, whenever anything of the user's is on
  record: *Not carried as they are: assembly features of yours (cuts, patterns, sketches, planes), display states and
  appearances; a sub-assembly comes over rigid, and a component of a pattern of yours comes over as a component of its
  own.* (the pattern clause leaves this list for the per-instance sentence once `PATTERN_INSTANCE_READ` is set, D12 †).
  *As built after the review of the second 2026 run (must-fix 2):* the app's words are *Assembly features, display
  states and appearances stay behind; pattern instances come over as components of their own.*, and the clause
  *sub-assemblies come over rigid* is said in it only where `CARRY_INSERTS_A_SUBASSEMBLY` is True on the version known
  and no sub-assembly is named as not carried (*…stay behind; sub-assemblies come over rigid, pattern instances as
  components of their own.*). While that finding is unset a sub-assembly is named and left, so the clause would
  contradict the sentence beside it (the 2026 runs' fixture holds no sub-assembly; the review drove both sentences
  together on the fake at `c2d95cc`).

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
  RangeBox.SLDASM showed, …*; `FELL_OVER_DEFINED`: *… your Lock3 made again over-defines them, …*). Each component
  fixed is named by its name in the new revision with its old beside it where SolidWorks renumbered it, as the first
  clause names it: *Housing-1 and Sprocket-9 (was Sprocket-8) are fixed where they stood in RangeBox_r2: …* (must-fix 1
  of the review of the second 2026 run: log 1:1397 called the old Sprocket-9 and the new one, the old Sprocket-8, by
  one name). The moved, clash, sub-assembly and pattern-instance sentences name a carried component the same way;
- *Your UserDist4 was in error in RangeBox.SLDASM and is in RangeBox_r2 too, as it was.*;
- *In L, SolidWorks moved Sprocket-4 2.0 mm from where it stood against Sun when your mates were made again.*;
- a clash: *In mode L, your Sprocket-2 interferes with RangeSlv (12.3 mm³).*;
- **placed once** (should-fix 13): *Your components were placed where they stood in H, the mode RangeBox.SLDASM showed;
  a floating one that stood elsewhere in another mode stands, in RangeBox_r2, where it stood in H.* (with modes, once,
  whenever a floating component was carried);
- the states (the None path only, as §9.1's clause): *Your components take in every mode the state they had in H, the
  mode RangeBox.SLDASM showed: their states in N and L could not be read without changing it.*; the D14 sentence of §9.1;
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
- a lightweight component's old instance resolved by the carry (D10 †, `CarryResult.resolved_in_old`): *Sprocket-9 was
  lightweight in RangeBox.SLDASM and is resolved there now: SolidWorks loaded its part to carry it.* (one sentence per
  component, its old Name2; nothing else in RangeBox.SLDASM changed, or the carry would have stopped);
- the old assembly moved or copied (§3 R.2, `OLD_UNREAD`): *RangeBox.SLDASM was moved or copied since it was last saved,
  so it was not read and nothing of yours was carried: open it in SolidWorks before you press Build again… to carry it.*

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
| `differs` | *Lock4 made again read otherwise than it was (its entities), so it was taken out again*; "left" (B's wording, `ui_text.py:5167`): *Lock4 made again read otherwise than it was and could not be taken out again: it is left in RangeBox_r2 as Lock4; delete it there in SolidWorks* |
| `refused` | *Lock4 is not made again: SolidWorks refused it, saying …* (B's wording, `ui_text.py:5163`) |
| `old unread` | *(the not-open clause of §9.1)* |
| `too long` | *Coincident8 is on a face of Sprocket-5 that Gear Generator did not look for, since finding it among Sprocket.SLDPRT's faces would have taken too long* (an edge: *an edge of Sprocket-5 … among Sprocket.SLDPRT's edges*; an app gear part on a file both use: *a face of Sun*). Nothing for the user to do; it is said so the mate's absence is not a surprise |

`part new`'s where slot (§2.3): "bore" *… was on Sun's bore …*; "axis" *… was on a face of Sun on its axis …*; ""
*… was on a face of Sun …*.

### 9.4 The footer afterwards

While `CarryEntry.unsaved_at` stands: *RangeBox_r2 holds what Build again… carried of yours, not saved: save it in
SolidWorks to keep it.* Found closed unsaved by a later job: *RangeBox_r2 was closed without saving after Build again…
carried your work into it, so it does not hold it; RangeBox.SLDASM held it when it was carried.* (never the present:
the app cannot see whether the old assembly changed since). Nothing offers to carry again (D11).

**Beside advice to close the assembly without saving** (the merge's ruling on `7ce641e`): where the app says to close
the record's assembly without saving (a stop in a part left in error, the footer's line on documents left in error,
the still-in-error sentence; the assembly named with the part, or among the documents), saving it would save the part
in error with it, so that advice stands, says what it costs inside its parenthesis, and the carry's save line is not
said beside it, in the footer or after a job's sentence: *(the files on disk are as before that Update; closing
RangeBox_r2 so also discards whatever else is unsaved in it, including what Build again… carried into it, which
RangeBox.SLDASM held when it was carried)* (the review of `9cbfc08`'s words: the carry counted once, as part of what
is unsaved, and the old assembly in the past). With no carry unsaved it ends *…; closing RangeBox so also discards
whatever else is unsaved in it)*, said whenever the assembly is closed so (W9C-RUNS-REVIEW's low should-fix): no press reads the save flag of an assembly open before it (`_note_opened` reads only a document it
loads, `_vouches` only one marked), so it is said as what closing can lose, never as a fact. A later Build again… does
not carry it again from RangeBox.SLDASM (it reads the record's current revision), so the sentence does not promise
it. With no such advice everything is as above.

## 10. What A adds to `swcom.Session` (each a wrapper, with `GetSaveFlag` read around it in the probe and M9)

Names **as built** (A's shape changes 7–12), where they differ from this section's first draft.

- `mate_definition(handle) -> MateDefinition` — S5 (a)'s read (`GetTypeName2`, `IMate2` Type, Alignment, Flipped,
  variations, `GetDefinition`'s fields, `MateEntity(i)`'s ReferenceComponent, ReferenceType2, Reference and its feature
  name, `EntityParams`), measured marking nothing on both versions. As built with `swcom.MateDefinition`,
  `swcom.MateEntityRead`, `swcom.entity_kind` and `swcom.MATE_DEFINITION_VALUES`; `mate_info`'s `MateInfo.entities`
  gives the kinds on every Update (§2.2).
- `entity_reference(mate_handle, index) -> (kind, hex or "", coaxial, why)` — tier 1's read for a **feature** entity
  (by name in the part, `FeatureByName`, S5), as built.
- **`entity_references(component, items) -> List[(kind, hex or "", coaxial, radius_mm, capped, why)]`** — tier 1's
  read for **face and edge** entities, one call per component, `items` that component's `(mate_handle, index)` pairs in
  mate order (RULED with the probes' review, must-fix 1; A's fix round replaces the face and edge branch of
  `entity_reference`, which follows `GetCorrespondingEntity2` or hands the entity straight to the part: both read
  nothing on 2026). Route r3, `PERSIST_REFERENCE_ROUTE_FOR_FACES` / `_FOR_EDGES`, with **four rules**:
  1. **One walk per component.** The part's faces are listed once (`GetBodies2(0, True)`, each body's `GetFaces`) and
     its edges once when any item is an edge (`GetEdges`). Each candidate is carried by `IComponent2.GetCorresponding`
     **at most once** (kept by its index), and compared by `ISldWorks.IsSame` with every item of the group whose
     prefilter it passed.
  2. **A prefilter before `GetCorresponding`**, read in the part, with no call into the assembly: a face's `GetArea`
     against the mate's entity's `GetArea`, relative 1e-9 (a part face and its assembly correspondent have one area:
     every entity of both runs read equal pairs); an edge's curve: a circle against circles of the same radius
     (`CircleParams[6]`, relative 1e-9), a line against lines, any other curve against every edge. A candidate whose key
     does not read is kept. `IsSame` still decides, so the filter can lose no true match; on the parts measured it
     leaves 2 (a sprocket's equal end faces) to 29 (Sun's tip cylinders).
  3. **Exactly one match inside the filtered set**: every filtered candidate is compared, never stopping at the first
     (uniqueness was measured 6 of 6, and after the filter counting costs almost nothing). None or several: `unread`
     *"SolidWorks did not say which one face of Sprocket-5 it is on"*, and the mate is `WHY_UNREAD`.
  4. **A cap**, `CARRY_WALK_CANDIDATES = 200` candidates carried and `CARRY_WALK_SECONDS = 20.0` per component
     (constants in `swbuild`). Items are taken in mate order. Before an item's walk, if carrying its filtered candidates
     not yet carried would take the component past 200, or the component's walk has already taken 20 s, that item and
     every later item of the component are **not searched**: `capped` "candidates" or "seconds", hex "", and the plan
     names each mate `WHY_TOO_LONG` (§2.3, §9.3). The clock is read between candidates too: an item whose walk passes
     20 s part way is stopped and capped, its matches so far dropped. **The cap never stops the carry**: the
     component's other items, and every other component, go on.

  Then, per item found: the part's `GetPersistReference3` on the part-level entity, resolved by its
  `GetObjectByPersistReference3`, must answer `swPersistReferencedObject_Ok`, to the item's own kind and `IsSame` as the
  part-level entity (else `unread`; another kind is §0.3's STOP); `coaxial` and `radius_mm` from that part-level
  entity's `CylinderParams` (a circle's `CircleParams`), in part coordinates. `why` holds the clause.

  *Why these numbers.* On 2026 one `GetCorresponding` + `IsSame` cost 1.6 ms at the session's start and about 50 ms by
  its end (the same 163-face walk 0.26 s, then 8.1 s, `w9d…-2.log:83-88`). 200 carried candidates is 0.3 s at the
  first rate and 10 s at the slowest measured, inside 20 s; with the prefilter leaving 2–29 per entity, 200 covers a
  component with half a dozen face or edge mates on look-alike faces, and one past it is where the cost would grow.
  20 s per component is twice the slowest unfiltered walk measured (482 edges, 8.2 s), and bounds R's walks at 20 s
  per component with face or edge mates however the session slows. Both are the review's suggestion; they are revisited
  when the growth measurement (the 2024 run, the short 2026 rerun of `faces` (b)) says how the cost scales. The fake
  models a cap reached (§14.1).
- `component_states_in(names, configurations) -> Dict[str, Dict[str, bool]]` — **as built**, named so because the fake
  already has a `component_states` dict (W9a's knob) that would shadow a method of that name. The unshown route
  `COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_<year>` names (`GetConfigurationByName(…).GetComponentSuppressionState(
  Name2)`, set on 2026); refused while it is None.
- `component_configurations(handle) -> (referenced, its document's active, its file's configurations)` — **as built**,
  for the first draft's `referenced_configuration(handle)`, so the file's configurations (`OldComponent.configurations`)
  come in the same read; the referenced one gated `REFERENCED_CONFIGURATION_READ`.
- `open_read_only(path) -> Optional[DocInfo]` and `close_unsaved(path)` — `OpenDoc6(Silent | ReadOnly)` and `QuitDoc`,
  the latter refusing a document this session did not open. The read-only document's flag is read straight after the
  open (§3 R.6).
- `select_by_reference(handle, kind, hex, append)` — tier 1's resolve, `GetCorresponding`, kind checked, `Select4`.
- `add_component_in(handle, path, at, configuration)` — **as built**, beside `add_component` unchanged (every existing
  call and the fake's keep their signature): `AddComponent5(path, 0, "", True, configuration, x, y, z)` (gated
  `CARRY_INSERTS_IN_A_CONFIGURATION`); the carry uses it for every component of a file with several configurations
  once that is set (§5.1, S-a), and `add_component` otherwise.
- `set_component_suppressed(handle, suppressed)` — `IComponent2.SetSuppression2` in the mode showing, read back
  (measured as the probes' own call: W9c's s5 (e), W9a's `lightweight`; never the app's).
- `save_flags()`, `file_version(path)`, `running_file_version()`, `dependencies(path)`, `delete_mate(handle)` — **as
  built**, the reads R.1 and R.2 and the fallback need. `file_version` takes `VersionHistory`'s **last** entry's number
  against `GetLatestSupportedFileVersion` (§8.1); `dependencies` gives `GetDocumentDependencies2`'s stored, top-level
  paths, every second entry, which R.2 refuses on as §3 says.
- **`remake_mate(handle, definition, targets, name, ratio) -> (name kept, status)`** — `AddMate5` from the definition on
  the targets selected **in selection order** (should-fix 5), renamed; **as built** the ratio is passed beside the
  definition (`CarryMateItem.ratio`). The ledger (`API-LEDGER.md:612`, verified both
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
  (a gear mate) ratio and sense, against the old; a difference left is `WHY_DIFFERS`, the mate deleted again. *Not built
  yet* (A's note): the once-reversed retry and the other-Flip retry; as built, either difference is deleted and named
  `WHY_DIFFERS` at once (§17).

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

*Measured on 2026 (34.0.0)*: candidate 1 agreed with the shown truth on 3 components × 3 modes from an unmarked start
and marked nothing; it read the unsaved suppression right; candidate 2 gave no root in a mode not showing; candidate 3's
calls marked nothing there, where W9c saw `GetRootComponent3(True)` mark on 34.1.1 (`w9d…-1.log:114-121`). So
`COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_2026` and `…_READS_UNSAVED_ON_2026` are set (§8.1): **on 2026 the states
are read unshown in both situations**, and R.6's check after the read stays the guard. 2024 waits for its run.

*What the app does* (D2 †, ruled):
- **A clean route on the running version** (2026): used in both situations. On an open old assembly whose
  `GetSaveFlag` reads True, only if `…_READS_UNSAVED` is True; else as the next bullet.
- **No clean route** — the path only where the finding is None (2024 until its run) — **the old assembly open in the
  user's session**: never shown in another mode. Each carried
  component takes the mode showing's state in every mode, said plainly in the question and the result (§9). The user
  may overrule (the other two ways: show and restore leaving the flag set; refuse until the user saves or closes it).
- **No clean route (None only), the old assembly not open**: the job's own read-only open and the per-mode show happen
  only under R.2's conditions (the record's version, nothing but the app's documents open,
  `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` True); otherwise the old assembly is not read at all (`OLD_UNREAD`), said before
  the press with the way round (open it in SolidWorks first) — never a hang.

### 11.2 The not-open read, and the documents already open

After a Build again… builds, the parts the new revision reuses are open; R runs before the build (D1), so at R's time
the session holds what the user had open. Measured: the read-only open of an assembly not open, every component
closed, reads read-only with its flag False (`OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN`). Not measured: what it does to
documents already open (made read-only? their changes kept? marked?), closing it after its modes were shown, and
`QuitDoc` on a file another SolidWorks saved (GOTCHAS §100: on 2026 the CAM add-in's modal "Save changes to …?" for a
2024 file, which ignores `WM_CLOSE` and Escape; the app has no dialog watch). R.2's conditions keep the
open off those cases:
- **the file's own version** (R1): the record's `solidworks` is the version the last *job* wrote the file on, which
  cannot see a save by the user on the other version since; so the not-open read also requires `FILE_VERSION_READ` set
  and the file's `VersionHistory` (a closed-file read, verified on 2026 in the ledger, `API-LEDGER.md:115`, never by the
  app) to name the running version last. **While `FILE_VERSION_READ` is None the job never opens a closed old
  assembly**: `OLD_UNREAD`, and the question says to open it in SolidWorks first (§9.1). The probe sets the finding
  only with a negative control, a file the other version saved, read closed (S-b);
- **the files it references** (S-f): the user's own parts may have been saved by the other version (a 2026 RangeBox
  holding a sprocket part saved on 2024 is plausible), and whether `QuitDoc` of a same-version assembly raises the CAM
  box for such a component is **unmeasured** (GOTCHAS §100 was seen on 2024-saved assemblies). The contract does not
  find out: the not-open read also requires `DEPENDENCIES_READ` set and every file `GetDocumentDependencies2` names to
  have been last saved by the running version. **So a part of the user's that is not loaded in the session is never
  opened by the job unless the closed-file reads have shown it and every file beside it saved by the running
  SolidWorks.** Where they have, it is opened twice: inside the read-only open (and closed with it, R.7 checking it is
  gone), and again by C.3 to insert it into the new revision, where it then stays loaded as a component of the new,
  unsaved assembly, as every part the build inserts does. On the open path nothing new is opened: the user's parts are
  already loaded with their assembly;
- **the documents already open** (S-e): the open goes ahead beside the app's own documents only when
  `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` is True.

*Measured on 2026 (34.0.0)*, from the probe's `state` (g), (h) and (v) (`w9d…-1.log:122-129`): both parts open beside the
read-only open stayed open, with their flags and not read-only, the changed one's change kept; the read-only
`RangeBox.SLDASM` read **modified straight after its `OpenDoc6`** (warning 32, NeedsRegen) beside the changed part, was
shown mode by mode, and closed by `QuitDoc` with its flag True and no dialog, every document it loaded gone and no file
time changed. With nothing changed beside it, W9c's s5 (d) read it flag False and warnings 0 (`w9c…-2.log:291`). So:
- **The job's own read-only document is judged from its flag straight after its open** (§3 R.6): True there is logged,
  not a mark; only a turn after that read counts. It is the job's own in-memory, read-only load, not a document of the
  user's, so §0.3's STOP is not about it; without the rule every not-open carry with a changed app part beside it would
  stop with a false *"Reading RangeBox.SLDASM marked …"*.
- **R reads that document as loaded**, without a rebuild: its frames and mates are read before any regeneration, and a
  changed app part beside it could make them differ from what a rebuild would show. That is inferred, not measured.
- `FILE_VERSION_READ` and `DEPENDENCIES_READ` are set on 2026 (§8.1), so there a closed old assembly saved by this
  SolidWorks, with every file it references, may be read; one the other version saved is refused without being opened.
  `DEPENDENCIES_READ` reads top level only: a sub-assembly dependency refuses (§3 R.2).

**Stored paths, and a copied or moved folder** (ruled after the demonstration's review, §5). `GetDocumentDependencies2`
with Searchflag False gives the paths stored in the assembly at its last save, not the files SolidWorks will load. For a
project folder copied or moved and not saved since, the stored paths still name the old folder; where those files are
still on disk, R.2 would read *their* versions and open the copy, and SolidWorks would then load the copies its search
rules find beside it, whose versions were never read: exactly the file of another version R.2 exists to keep out. So R.2
refuses (`OLD_UNREAD`, *"open it in SolidWorks first"*) when a stored path lies outside the old assembly's own folder
while a file of the same name sits in that folder; a library part referenced in place is not refused. **Unmeasured**:
whether `GetDocumentDependencies2(path, False, True, False)` (Searchflag True) returns the paths SolidWorks would load.
The 2024 probe run reads it beside Searchflag False, on the probe's saved copy and on a plain copy of the master's
folder that SolidWorks never opened (a fact, proposing nothing, `W9D-PROBES.md`); once a reviewed run shows it, R.2 can
judge those paths instead and refuse less.

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
(`IEntity.GetComponent`), three routes to the part-level reference, resolves each in the part, carries it back through
the component and asks `ISldWorks.IsSame`; the coaxial read on each face; each user component's referenced
configuration, `IsVirtual` and `IsPatternInstance`. It then makes the four again in a second assembly, the route chosen
per entity kind (P10), with the copy's documents' flags read around the inserts; and resolves every face and edge
reference again after the copy is closed and the parts opened alone (the reload, should-fix 9). *Ruled*: a face or edge
entity is tier 1 only by the route the probe proposes for its kind, set per version; unset, `WHY_UNMEASURED`.

*Measured on 2026 (34.0.0).* **r1** (`GetCorrespondingEntity2` in the assembly) and **r2** (the mate's entity straight
to the part's `GetPersistReference3`) read nothing on any entity: r1's call gives nothing for a mate's entity, r2's
reference resolves `swPersistReferencedObject_Invalid` (`w9d…-1.log:51-80`). **r3** (the part's faces or edges each
carried by `IComponent2.GetCorresponding`, the one `IsSame` as the mate's entity, then the part's
`GetPersistReference3`) read all six clean, both ways: exactly one match each, resolved `Ok` to its kind, `IsSame` as
the part entity and, carried back, as the mate's entity, every bracket unmarked; (c) remade all four mates equal with
every frame unmoved, and (d) resolved every reference again in its part reopened alone (`w9d…-2.log:83-104`). The
review found no way r3's log could read clean while wrong (`W9D-PROBES-REVIEW.md`). **The walk's cost grew through the
session**:

| Entity | Walked | Found in |
|---|---|---|
| Sprocket bore face | 163 faces | 0.26 s |
| Sprocket end face | 163 faces | 2.1 s |
| Sprocket end face | 163 faces | 3.7 s |
| Sprocket circular edge | 482 edges | 8.2 s |
| Sun's end face | 235 faces | 5.6 s |
| Sprocket end face | 163 faces | 8.1 s |

About 50 ms per `GetCorresponding` + `IsSame` by the end, up from 1.6 ms; why is not known (per-call accumulation or a
slower session). R runs before the build (D1), so this is paid before anything is made: §10 bounds it (one walk per
component, the prefilter, the count, the cap). The growth is measured in the 2024 run and a short 2026 rerun of
`faces` (b) (`W9D-PROBES.md`); until then the cap is the answer, and the caveat stays on the finding.

### 11.5 Two more the contract depends on

- **The root read on an assembly with a lightweight component** (the W9c review's should-fix 5): the probe reads
  `GetRootComponent3(False)` and `(True)` there as facts (does each answer, does either resolve the component); it
  cannot tell whether either marks (the copy is marked by then), so nothing rests on it: `_read_user_work`'s rule stands.
  *Read on 2026*: both answered `RangeBox` and resolved nothing (`w9d…-1.log:121`); whether either marks is still
  unknown.
- **A mate on a component suppressed in a mode**: read by the probe as a fact (its flags there), so §3 C.6.1's "a mode
  where one of its components is suppressed left as SolidWorks has it" rests on a reading; M9 holds one in the mode
  showing. *Read on 2026 (M9's first run, 34.0.0; ruled the contract's, 2026-11-17)*: on the open path, a mate on a
  component suppressed in the mode showing reads **unread** (UserAxis9, Sprocket-9 suppressed in H; on the closed path
  UserAxis7, Sprocket-7 suppressed in L as saved), so it is named `WHY_UNREAD` and "made in a mode where its
  components are resolved" is not reached there; the suppressed component's own frame **does** read, and it is
  carried.

## 12. The choices, as ruled (the coordinator, 2026-11-17; † the user's to overrule)

- **D1 — ruled as recommended**: read before anything is made, carry after the save; `open_before` is R.1's list, and
  R.7 checks the session is left as found (should-fix 8).
- **D2 † — ruled as recommended**: an old assembly open in the session is never shown in another mode; with no clean
  unshown route each carried component takes the mode showing's state in every mode, said plainly. Not open: the
  read-only open and per-mode show only under must-fix 2's conditions; otherwise the old assembly is unread, said,
  never a hang. A clean unshown route makes this moot: **on 2026 it is set** (§8.1, §11.1), so D2's fallback and the
  not-open path's per-mode show are the path only where the finding is None (2024 until its run). M9's judged list
  keeps both branches.
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
- **D10 — ruled**: a lightweight component carried resolved, its mates named; foreseen in the question. **† Its
  consequence for the old assembly, ruled after the demonstration's review** (the user's to overrule): opening the
  part to insert it may resolve the old assembly's lightweight instance (lightweight is per file in the session). That
  change, confined to that component going from lightweight to resolved, is not a STOP and not undone; the worker reads
  it before and after and the result says it (§3, §9.2); M9 proposes
  `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY_ON_<year>` as a fact. Every other change to the old
  assembly remains a STOP. *The alternative the user may choose*: such a component is named and not carried, so the old
  assembly is never changed at all.
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
- **The plan's "bore mate on Sun" (the coordinator's ruling, the re-check)**: RangeBox's Sun has no bore
  (`tests/workbook_fixtures.py:84`, no Bore), so M9 shows it as a mate on Sun's front end face — the same test of the
  rule: a face of an app part made new is named (`WHY_PART_NEW`), not re-found. Not a silent change of the Done-when.
- **D17, D18, D19, D21 — ruled as recommended** (D18 verified, §15: a mixed-flank mesh is legal in the code now; D19's
  origin is now any origin, unmeasured, §4.2).
- **D20 — ruled with the review's change**: each component takes its own lock to an app body first, then its cluster's
  anchor. **Ruled further** (the demonstration's review): a component fixed in the old assembly is placed by its world
  frame and has no app anchor, whatever its cluster reaches; a floating one keeps the order (§5.3).
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
8. **The not-open read's residual risk** (§11.2): **closed on 2026** (the re-check's R1, then the 2026 run). The record
   knows the version of the last *job*, not of a user's save since, so the not-open read requires `FILE_VERSION_READ`
   and the file's own last saved version, and the same of every file it references (`DEPENDENCIES_READ`, S-f, top
   level only: a sub-assembly dependency refuses); while either finding is None the job never opens a closed old
   assembly. **On 2026 both are set** (§8.1): a closed file the other version saved reads so, closed, and is refused
   without being opened. **Open on 2024** until its run. What stays unmeasured, and is never reached by that rule:
   whether `QuitDoc` of a same-version assembly raises SOLIDWORKS CAM's box for a component another version saved.

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
- **The not-open path**: refused (`OLD_UNREAD`, said, the assembly never opened) when the record's version is not the
  running one, when `FILE_VERSION_READ` or `DEPENDENCIES_READ` is None (R1, S-f), when the file or any file it references
  reads last saved by another version, when a document the record does not name is open, when app documents are open
  and `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` is None, or when `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` is None; otherwise
  opened read-only,
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
- **Added with the probes' revision** (the fix round): §10's walk on the fake — one walk per component (the fake counts
  `GetCorresponding` calls: each candidate carried at most once for a component with three face mates), the prefilter
  (a candidate of another area never carried), none or two matches `WHY_UNREAD`, and **a cap reached** (a knob lowering
  `CARRY_WALK_CANDIDATES`, and a fake clock passing `CARRY_WALK_SECONDS`): the items after it `capped`, their mates named
  `WHY_TOO_LONG`, the component and every other one still carried; `part new`'s where slot ("bore" only with
  `radius_mm` at `bore_mm`/2, "axis" for a coaxial tip cylinder, "" otherwise); the job's own read-only document read
  flag True straight after its open not counted as a mark, and a turn after it counted; R.2 refused on a dependency that
  is an assembly, one not on disk, and one whose history does not read; the states read unshown on the not-open path
  where the route is set (no per-mode show).
- **Added after the demonstration's review**: a fixed user component joined to a cluster anchored on Sun placed by its
  world frame, with anchor "" (D20); R.2 refused on a stored path outside the folder with a namesake beside the
  assembly, and not on a library part referenced in place; a lightweight component whose carry resolves the old
  instance (the fake doctored) said in `resolved_in_old` and not a stop, while any other change to the old assembly
  still stops the carry.

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

*Brought in line with the script as reviewed* (`probe/w9d_demonstration.py`, `W9D-DEMONSTRATION.md`,
`W9D-DEMONSTRATION-REVIEW.md` §2, `6f67791`). The departures from the first outline are listed after the fixture, each
with its reason.

**Fixture**: a copy of W9a's `setup.master` (RangeBox with Sprocket-1 and -3 locked to Sun and on Input Axis,
Sprocket-2 locked to RangeSlv on Output Axis, Sprocket-4 by a distance to Sprocket-3 and an angle to the layout, the
fixed Housing-1, the User Keyway in Sun's part; `W9A-DEMONSTRATION.md`), to which the script adds, before the sections,
saved as the run's own copy (`w9d-fixture.master`):
- **the Done-when's clusters, on feature mates** (should-fix 15): cluster one, Sprocket-1, -3 and Sprocket-4 on Sun
  (setup's own), plus Chain-1 (`Chain.SLDPRT`, a user part) on Input Axis by its axis and a distance between its plane
  and Sprocket-1's; cluster two, Housing-2 mated to the layout by its planes (coincident, distance and parallel);
- **face mates, as a further item resting on `PERSIST_REFERENCE_ROUTE_FOR_FACES`**, on **Chain-2**: a concentric on its
  bore to Input Axis (UserFaceConc), a coincident between its end face and Chain-1's (UserFaceCoin, user–user, so
  Chain-2 joins cluster one); with that finding None both are named and the Done-when still holds on the feature mates;
- a coincident between Sprocket-5's end face and **Sun's front end face** (UserSunFace; RangeBox's Sun has no bore: a
  face of an app part made new, named `WHY_PART_NEW`);
- a parallel (Housing-2's) and a limit distance between Sprocket-10 and Sprocket-11 (kinds);
- a user gear mate from Sprocket-6's `Gear Axis` to Sun's `Gear Axis` (UserGear6; §4.3,
  `CARRY_GEAR_MATE_ON_AN_APP_GEAR`, ratio and sense read back);
- **the face variant, on SolidWorks** (the probes' review: Sun's tip and root cylinders read coaxial, `w9d…-2.log:92`):
  Sprocket-10's gear mate picked on **Sun's root cylinder** (UserGearRoot, r 16.375 mm, coaxial), taken as `Gear Axis`
  on the new Sun and remade with its ratio and sense; Sprocket-11's picked on **a root fillet** of Sun (UserGearFillet,
  r 0.475 mm, off-axis), named `WHY_PART_NEW` with where "" (*a face of Sun*: Sun has no bore). Each sprocket is
  otherwise free to turn, so neither ties Sun's train;
- **a mate to the assembly's own Front plane** (tree order): a distance from **Sprocket-6** (UserAsm6);
- Sprocket-7 suppressed in L (states per mode); Sprocket-9 suppressed in **H, the mode showing**, with a mate
  (should-fix 3, and what R reads of its mate);
- **SprocketLight-1** (`SprocketLight.SLDPRT`) with a mate, **set lightweight in the session in the `carry` section
  only** (D10; never saved lightweight: saving an assembly with a lightweight component meets SOLIDWORKS CAM's box, the
  re-check's S-g);
- **SprocketConf-1** (`SprocketConf.SLDPRT`, its part given a second configuration Z20, the component set to it):
  `CARRY_INSERTS_IN_A_CONFIGURATION`, `REFERENCED_CONFIGURATION_READ`;
- the tied cluster, Sprocket-8 locked to Sun and held at 90° to the fixed Housing-1 by an angle mate: one freedom,
  so the old assembly reads every mate 0 while Sun cannot turn (`FELL_TIE`) (the coordinator's ruling after the first
  2026 run: a lock to the fixed housing over-defined, 46, and the same-error rule would have excused it);
- no user sub-assembly: package A inserts one by `open_document` + `add_component`, not by the measured read-only
  insert, so `CARRY_INSERTS_A_SUBASSEMBLY` and every leaf finding stay None (W9D-REVIEW-A).

**The departures from the first outline, and why** (each found sound by the demonstration's review):
- *The face mates are on Chain-2, not Chain-1.* As first written, Chain-1's bore concentric repeated its axis
  coincident and its face coincident repeated its distance to Sprocket-1: the same freedoms fixed twice, over-defined.
  Chain-2 joins cluster one through UserFaceCoin, and "the chain on Sun" is still Chain-1.
- *The assembly-plane mate is on Sprocket-6*, not Housing-2, whose Front plane is already held to the layout's.
- *The lightweight and the two-configuration parts are files of their own* (SprocketLight, SprocketConf: the
  sprocket's spec, each built into its own file). Lightweight is a state of the file in the session: setting one
  Sprocket lightweight reads every `Sprocket.SLDPRT` instance lightweight (`w9d…-1.log:121`), so a shared file would
  take Sprocket-1..11 with it. A configuration belongs to the file, so a second one in `Sprocket.SLDPRT` would be in
  every sprocket's file. Neither may touch `Sprocket.SLDPRT`.
- *UserAsm6 is judged `unread` in `carry` and made again in `carry-closed`.* R never reads the root beside a lightweight
  component (§4.2, §11.5), and an assembly plane reads as the root component's entity, so beside SprocketLight-1 it
  comes out unread; `carry-closed` has no lightweight component and remakes it. The Done-when does not need it.
- *The question need not name UserSunFace.* The Done-when's "named in the question and the result" belongs to the
  keyway; the mate on Sun's face must be named, and the result names it. §9.1's example is an example; B groups.
- §15's earlier "Sprocket-9 lightweight, Sprocket-10 suppressed in the mode showing, Sprocket-11 in a configuration"
  are SprocketLight-1, Sprocket-9 and SprocketConf-1.

Each item depends on the findings named beside it; the script reads them first and says which items will be named
rather than carried, so a None finding is a named item judged as named, never a failure.

**The edit**: Sun's Flank to arcs (D18, **verified in the code now**: `assess.assess` of `range_box()` with Sun's
`flank="arcs"` gives no error and no build refusal, only the note *Sun: Arcs stand in for the involute on this gear to
within 34.7 µm*; nothing checks the flanks of two meshing gears against each other) and a shaft added (a gear on a new
shaft meshing nothing it would refuse), so Sun's part is a new file and every other part is reused; typed in Excel by
W8's `edit`.

**Sections**: `carry-gates` (every W9d write gate None: the question and the result name everything with its finding,
the build as W9c's; ~10 min); `carry` (the gates patched in the process, the old assembly open with H showing: the
Done-when below; ~35 min, 45 likely); `carry-closed` (the old assembly **saved with L showing** and **no lightweight
component**, then closed: read read-only under R.2's conditions, RangeSlv's train read in L and placed in H,
contradiction 6 shown with the sliding RangeSlv, UserAsm6 and SprocketLight-1's mate made again; the states by the
route or the read-only show; ~20 min); on 2024 the same sections in fresh sessions, about twice as long.

**Judged** (every mode shown, every read before and after; on 2026 the states route and the closed-file findings are
set, §8.1, so `carry` and `carry-closed` take the unshown branch there and the shown one only on 2024 while its
findings are None): RangeBox_r2 saved as built; both feature-mate clusters
carried, each component at its pose against its own anchor to the post-check's tolerance, every remade mate's
definition equal to the old one and on in the modes it was on in, code 0; the face mates carried or named as their
finding says; the mate on Sun's face (UserSunFace) named `WHY_PART_NEW` in the result; the keyway named in the question
and the result with why;
the tied cluster alone fixed, its angle mate kept, Sun free to turn in every mode, every other cluster on Sun's
train carried; **Sprocket-7 suppressed in L alone where the states route is clean, and resolved everywhere, said, where
it is not** (D2); SprocketLight-1's mate named `WHY_LIGHTWEIGHT`, it carried resolved, and whether its old instance
was resolved by the carry read before and after and said (D10 †, a fact); UserAsm6 `unread` in `carry` and made again in `carry-closed`; Sprocket-9 placed or named as its
frame read; SprocketConf-1 in Z20; the gear mate on `Gear Axis` remade with its ratio and sense; the gear mate on Sun's
root cylinder remade on `Gear Axis`, the one on a root fillet named; Housing-1 (fixed) placed by its world frame, not
against Sun (D20); R's face and edge walks within the cap, their seconds logged per component; every app gear free to
turn in every mode; the carried items unsaved, `unsaved_at` the file's time; RangeBox.SLDASM's flag, active mode, every
component's frame and state, every mate's code, flag per mode and entities, and every user file's time unchanged; no
dialog; the record at schema 10 holding the carry, and the footer's line. Proposes `CARRY_INSERTS`,
`CARRY_INSERTS_IN_A_CONFIGURATION`, `REFERENCED_CONFIGURATION_READ`, `CARRY_REMAKE_KINDS` (the kinds remade clean),
`CARRY_GEAR_MATE_ON_AN_APP_GEAR`, and `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY` as a fact (True or
False, as read). `FELL_NEW_ERROR` and `FELL_OVER_DEFINED` are the fake's only.

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

### 17.1 Shape changes since the packages started

**Ruled, for package A to make and B to use** (with the probes' revision, `94fbebf`):
- `OldEntity.radius_mm: Optional[float] = None` (approved by the coordinator): a cylindrical face's or a circular
  edge's radius in mm from r3's part-level read, beside `coaxial`; §4.4's "bore" rests on it. `plan_carry`'s `part new`
  where slot becomes "bore" / "axis" / "" (§2.3); today's `"bore" if coaxial` (`swbuild.py:7360`) changes with it, and
  B's clause says *on its axis* for "axis".
- `WHY_TOO_LONG = "too long"`, `OldEntity.capped: str = ""`, `CARRY_WALK_CANDIDATES = 200` and
  `CARRY_WALK_SECONDS = 20.0` (the cap-exceeded reason the coordinator asked for, §10's rule 4): subjects (entity kind,
  component Name2 or gear id, file name, "candidates" or "seconds"); B's clause in §9.3.
- `Session.entity_references(component, items)` for face and edge entities (§10's four rules), beside
  `entity_reference` for features; the read R groups each component's face and edge items and calls it once.
- The R.6 rule for the job's own read-only document (judged from its flag straight after `OpenDoc6`; only a later turn
  counts, its per-mode show's excepted), where A as built leaves it out of `marked` altogether; and R.2's three
  refusals on `DEPENDENCIES_READ` (a `.SLDASM` dependency, a path not on disk, a history that does not read).
- `findings.py`'s `_ON_2026` values of §8.1, each with its caveat; `_ON_2024` None until that run is reviewed.

**Proposed with the probes' revision, since ruled and built**: `CarryBody.bore_mm: Optional[float] = None`, filled by
B from the old part's sidecar (§2.1), so "bore" can be told from *on its axis*; with it None nothing is called a bore.

**As built by A, now the contract's names** (A's note, shape changes 1–12): `STAGE_CARRY`; `STEP_CARRY_STEPS`,
`ENTITY_KINDS`; `OldComponent.configurations`; `findings.DEPENDENCIES_READ_ON_<year>`; `STEP_CARRY_FEATURES`;
`CARRY_KIND_WORDS`, `carry_kind`, `selection_reversed`, `gear_sense`, `SEL_*`, `OPEN_READ_ONLY_ROUTE`;
`Session.component_states_in` (for `component_states`); `Session.add_component_in` (beside `add_component`);
`Session.component_configurations` (for `referenced_configuration`); `save_flags`, `file_version`,
`running_file_version`, `dependencies`, `delete_mate`, `MateDefinition`, `MateEntityRead`, `entity_kind`,
`MATE_DEFINITION_VALUES`; `read_old_work`, `STATES_SHOWN_READ_ONLY`; `remake_mate`'s `ratio`; `MateInfo.entities`
read in `mate_info` with the fake's `read_entity_kinds` knob. §2, §8 and §10 now say these. A's other choices where the
contract was unclear (one `STEP_CARRY_KIND`, a leaf and an origin always named, the order of reasons, `"carried<i>"`
handles, cluster numbering, the anchor's pass-over, `old_read`'s values) stand as A's note records them.

**Not built by A, for the package reviews to rule**: the once-reversed retry and the other-Flip retry of `remake_mate`
(§10; as built, deleted and named `WHY_DIFFERS` at once); the sub-assembly's read-only insert route; the pattern and
virtual reads (both findings None, so nothing changes until they are set).

**After the demonstration's review (ruled)**, for A to make and B to word:
- R.2's copied-or-moved-folder refusal (§3 R.2, §11.2), with its clause.
- D20's fixed component placed by its world frame, with no app anchor (§5.3); `CarryResult.anchors` then gives it "".
- D10 † (§3, §9.2): `CarryResult.resolved_in_old: List[str]` (the old Name2s of lightweight instances the carry
  resolved in the old assembly), read before C.3 and after C.8, said, never a STOP; and the fact finding
  `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY_ON_<year>` (None until M9).

**New fields and reasons, as built or being built** (A's note and its later rounds; each at the end of its class,
defaulted, nothing renamed):
- `CarryResult`: `anchors` (B's request 1, ruled); `facts` (what was read but not judged, a mode where a cluster's
  component is suppressed: for the log); `changed_files` (the files C.8 read changed on disk, base names);
  `after_unread: str` (why C.8's times and flags could not be read after the carry, "" when read: B's request, so the
  fact is said as a fact and `stopped` stays a stop); `resolved_in_old` (D10 †, above).
- `OldWork.walks`: §10's walk per component as measured (items, candidates carried, seconds, cap reached), for the log.
- `CarryEntry.changed_files` (the record keeps the files' names, never paths).
- `WHY_REFUSED = "refused"`, subjects (SolidWorks' sentence,): SolidWorks refused to make the mate again, or to select
  what it joins; named, never a stop (a `ComError`, a lost session above all, stops the carry instead).
- `WHY_DIFFERS` gains a 2nd slot only in the "left" case, `("left", name in the new assembly)`: a retry whose read-back
  or delete raised, so the mate may be left in RangeBox_r2 under that name.
- `FELL_NEW_ERROR`'s first slot may be an **app mate's** name: an app mate reading a new error in a mode falls back a
  cluster on in that mode with a mate on the app's bodies (the demonstration's review asks it to blame only clusters on
  the erring mate's bodies or train: a should-fix for A).
- Also ruled since this section was first written: `CarryBody.bore_mm` (taken), the owner slots of B's request 3
  (taken), and no code-after field (B's request 2). B's request 5 (`CarryEntry.lost_at`) as below.

**B's requests — as first recorded** (recommendations; 1, 2 and 3 are now ruled as above):
1. **`CarryResult` hands back each component's anchor** (B: `gearbox.carry_anchors` works it again by `plan_carry` on
   what was read). *Recommended*: an `anchors: List[Tuple[str, str]]` field (new Name2, `CarryBody.old` or "" for the
   world frame), filled from the worker's own `CarryPlan`. B's recomputation runs without `new_frames`, so where the
   worker passed over a body whose new frame was missing (A's note) the two can name different anchors, and the record
   and the sentence would then say an anchor the worker did not use.
2. **A remade mate's code after** (B: `CarriedMateEntry.code_after` is its `same_error` code, else 0). *Recommended*:
   no shape change. By §6 a kept remade mate reads either 0 or the error it had before (a new error falls its cluster
   back), so B's rule is exact; §7 would then say so. If the reviews want the read itself, a `codes: List[Tuple[str,
   int]]` (kept name, code in the first mode after the post-check) is the field.
3. **The `unmeasured` and `gone` subjects say whose** face or feature. *Recommended*: take both, as trailing optional
   slots — `unmeasured` (what, finding, version, owner: the component's Name2 or the gear id, for an entity kind only)
   and `gone` (what, name, owner: the gear id, for "feature" only) — filled by `plan_carry`; B's clauses already say
   them when present and read without them.
5. **The lost line has no field** (B says it once, in the later Update's sentence). *Recommended*: `CarryEntry.lost_at:
   str = ""` (the stamp of the job that found the new assembly closed without its carry), so §9.4's lost line stays in
   the footer until the next Build again… from that revision, as §9.4 means. A defaulted field inside schema 10, which
   is not yet released.

B's other notes (4: the inventory keeps no user file path or configurations, so the foresight says *may*; 6: `exists`
not threaded to the read's `isfile`; 7: the fake's `moved` 30 mm in N and L; 8: `ui_text.CARRY_KIND_WORDS` pinned
equal to swbuild's) are for the package reviews and A, not shape changes.

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

**The re-check (`W9D-INTERFACES-REVIEW.md`, *Re-check of the revision*, `8d3695b`).** R1 → §3 R.2, §11.2, §13 item 8
(closed), §9.1, §14.1. R2 → §5.1, §8. S-a → §5.1, §3 C.4, §10. S-b → §8, the probe's `state` (v) with
`--other-version-file`. S-c → §8, the probe's `faces` (d). S-d → §2.2, §4.3, §8, the probe's `faces` (b). S-e → §3
R.2, §11.2, §9.1. S-f → §3 R.2, §11.2, §13 item 8, `DEPENDENCIES_READ`. S-g → §15. The bore mate's equivalence → §12.

**The probes' review (`W9D-PROBES-REVIEW.md`, `94fbebf`).** Must-fix 1 (bound r3) → §10's four rules and cap, §4.1,
§14.1 (the fake's cap). Its point 4: §4.1 → §4.1 (r3, the table measured on 2026); §10 `entity_reference` →
`entity_references` (§10); §11.4 → §11.4 (r1 and r2 dead, r3 clean, the timings); "bore" → §2.2, §2.3's `part new`
slot, §4.4, `OldEntity.radius_mm` (§17.1); §4.3 → §4.3 (root fillets, the read decides); §15 → §15 (the face variant on
SolidWorks); §11.1, D2, §9.1's states clause → each (the None path only); R.1/R.6 and §11.2 → §3 R.6, §11.2;
R.2's `DEPENDENCIES_READ` → §3 R.2, §8; §13 item 8 → closed on 2026; §8 → the set-by entries and §8.1's values. The
cap-exceeded reason → `WHY_TOO_LONG` (§2.3, §9.3). Its facts (a mate's own flag, lightweight on every instance) → §5.2;
the root read → §11.5. Its point 5 (the 2024 run) → the probe and `W9D-PROBES.md`.

**The demonstration's review (`W9D-DEMONSTRATION-REVIEW.md`, `6f67791`), its contract points, as ruled.** R.2 and
stored paths (§5) → §3 R.2, §11.2, §9.2, the probe's `state` (v) Searchflag read. D10's spread (M1 (b)) → §3 *One
change …*, §5.2, §8, §9.2, D10 †. D20 for a fixed component → §5.3, D20. The departures from §15 (§2) → §15. The new
fields and reasons as built → §2.3, §2.4, §9.3, §17.1.
