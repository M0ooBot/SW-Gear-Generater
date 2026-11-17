# W9d: Build again… carries the user's work — the interface between planning (B) and the worker (A)

Stage W9d of `ISSUE-1-PLAN.md`: §0.2 K5 (the user's answer), §0.3, §2.1 item 8, **§2.5**, §4 S5 and M9, §5 "W9d", and
*Changes after W9b, W9c's probes and the review of W9c's packages* ("Owed before W9d is designed"). Written before any
W9d code, at `64bec58`, against S5's and P2's readings on both versions (`W9C-PROBES.md`, `W9C-PROBES-REVIEW.md` and
its 2024 addendum, `probe/results/w9c-probes-sw2026-20261117-2.log`, `sw2024/w9c-probes-sw2024-20261117.log`, the
W9c block of `findings.py`), the installed SolidWorks API help (2024's `sldworksapi.chm`, decompiled as the macro
database's connect/12 says) and the macro database.

Package A is the worker (`swbuild.py`, `swcom.py`, the fake); package B is planning, the question, the result's
sentences, the record and the window (`workbook/update.py`, `workbook/gearbox.py`, `ui_text.py`, `store.py`,
`workbook_gui.py`, UI-DESIGN §9). This note fixes the shapes the two share, where the carry sits in the Build again…
job and in what order it runs, how each entity is found and what of that is measured, the findings it reads, the
record, every sentence, and the tests each package owes. A change to a shape here is a stop-and-ask, as at W8, W9a and
W9c. **What the plan does not settle is marked ⟨D1⟩ … ⟨D21⟩ and listed in §12 for the coordinator's ruling.** §11 works
through the three things owed before W9d is designed; the probe that measures them is `probe/w9d_probes.py`
(`W9D-PROBES.md`).

What is verified and what is not: a statement about the code cites the code at `64bec58`; a statement about SolidWorks
cites a committed log line or a `findings.py` constant; one that rests on the API help alone says so; one that rests on
nothing measured says *unmeasured*. Nothing here assumes a probe result: where the design forks on one, both branches
are written.

## 1. The contract in one sentence

**A Build again… given a `Carry` reads the old assembly before it makes anything, builds, checks and saves the new
revision exactly as today, then inserts the user's components into the new assembly, remakes their mates where every
entity is found by a measured route, judges the clusters, and hands back a `CarryResult` that names everything not
carried with its reason; nothing is saved after the new assembly's first save, and nothing is written to the old
assembly or to any file of the user's.**

- `build_gearbox(..., before=OldAssembly(...), carry=Carry(...))`. `carry=None` is W9a's Build again… call for call
  (`before` alone: the old assembly read when open, what stays behind said). `carry` given with `before` None is a
  fault (`BuildError`, "a fault in Gear Generator").
- The carry never stops the build and never makes the build's own result depend on it (plan §2.5: "so the app's own
  result never rests on the carried items"). Whatever the carry meets, `GearboxResult.ok` is what the build alone made
  it, and the record's new revision is written as today ⟨D21⟩.

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
    names: Tuple[str, ...] = () # the app's own feature names in the NEW file (tier 2): the layout's axes and planes
                                # (layout.layout_features), a carrier's, a gear part's ("Gear Axis", "Mid Plane",
                                # "Profile Plane"); ⟨D3⟩
    old_names: Tuple[str, ...] = ()   # the app's own feature names in the OLD file (the record's features for it), so
                                # a feature of the user's in an app part is told from the app's

@dataclass(frozen=True)
class Carry:
    old: OldAssembly                      # W9a's (path, bodies, layout, recorded mates, modes on record), unchanged
    bodies: Tuple[CarryBody, ...]         # every app body on record, the layout first, carriers, then gears
    modes: Tuple[str, ...] = ()           # the new revision's configurations, in Modes-sheet order (() with none)
    first: str = ""                       # the old record's first mode (GearboxRecord.modes[0]): what a mode new in
                                          # the revision takes its states from ⟨D14⟩
```

B fills `Carry` from the record and the `GearboxPlan` it is about to build (`workbook.update.carry_for(record, again)`,
beside W9a's `old_assembly`): planet copy *k* to copy *k*; a body the new plan has no handle for gets `handle ""`;
`same_file` from `again.reuse` (a `PartReuse` whose path is the old component's part); `why_new` from the update plan's
structural reasons and `again.made_new` (`MadeNew.why`). The window passes it as `kwargs["carry"]` in `_start_build`
beside `before`, and only for a Build again… (W9a's `old_assembly` already decides that).

### 2.2 What A reads (crosses to B on the result)

```python
ENTITY_WHOLE    = "whole"     # a whole component (a lock's entity; ReferenceType2 0 or swSelCOMPONENTS)
ENTITY_FEATURE  = "feature"   # a reference feature by name (an axis, a plane that is not a base plane)
ENTITY_PLANE    = "plane"     # a base plane, by tree order ("plane1".."plane3"), never by its English name
ENTITY_ORIGIN   = "origin"    # a component's origin point
ENTITY_FACE, ENTITY_EDGE, ENTITY_VERTEX = "face", "edge", "vertex"
ENTITY_UNREAD   = "unread"

@dataclass(frozen=True)
class OldEntity:
    what: str                   # APP, LAYOUT, ASSEMBLY, USER or UNREAD_ENTITY (W9a's words; a carrier is APP)
    owner: str                  # the gear or carrier id (APP), the top-level Name2 (USER), "" (LAYOUT, ASSEMBLY)
    kind: str                   # ENTITY_*
    feature: str = ""           # ENTITY_FEATURE: its name; ENTITY_PLANE: "plane<n>"; ENTITY_ORIGIN: "origin"
    leaf: str = ""              # inside a user sub-assembly: the leaf's Name2 path ("UserSub-1/P2Sprocket-1")
    reference: str = ""         # the part-level persistent reference, hex (tier 1); "" when not read or not needed
    select_type: int = UNREAD   # IMateEntity2.ReferenceType2 as read
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
    entities: Tuple[OldEntity, ...]
    on: Tuple[str, ...]         # the old modes it is on in (UserMate.on's convention)
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
    frame: Optional[Frame9]     # its frame in the mode showing; None when it would not read (suppressed)
    suppressed_in: Optional[Tuple[str, ...]] = None   # the old modes it is suppressed in; None: not read per mode
                                                      # (only `state`, the mode showing's, is known) ⟨D2⟩
    on_disk: bool = True        # its file is on disk (os.path.isfile); False for a virtual component or a lost file

@dataclass
class OldWork:
    read_at: str                # store.now()'s stamp, when the read began
    assembly: str               # the old assembly's path
    how: str                    # OLD_OPEN ("open": read as it stands in the session) or OLD_READ_ONLY (opened by
                                # this job, read-only, and closed unsaved after the read); OLD_UNREAD with `unread`
    active: str                 # the old mode showing ("" with no modes)
    modes: Tuple[str, ...]      # the old configurations on record, found by name
    components: List[OldComponent]
    mates: List[OldMate]        # every user mate (not on record), suppressed in every mode included
    app_frames: Tuple[Tuple[str, Frame9], ...]   # each old app body's frame in the mode showing (by CarryBody.old)
    states_route: str = ""      # the finding route the per-mode states were read by; "" when not read (⟨D2⟩)
    marked: List[str] = field(default_factory=list)   # documents a read turned modified (GetSaveFlag False → True):
                                                      # §0.3's STOP; the carry then does nothing
    unread: List[str] = field(default_factory=list)   # sentences: what could not be read, and why

    def user_work(self) -> UserWork: ...         # W9a's view of it, for GearboxResult.old_user_work as today
```

### 2.3 What A decides (pure, shared with B's foresight)

```python
CARRY_PART, CARRY_SUBASSEMBLY = "part", "sub-assembly"
# why something is not carried (CarryNamed.why); B words each (§9)
WHY_KIND          = "kind"            # a mate kind this version never remakes (§2.5's list)
WHY_UNMEASURED    = "unmeasured"      # a kind, entity kind or step whose finding is not set on this SolidWorks
WHY_PART_NEW      = "part new"        # a face, edge or vertex of an app part made new (tier 4), or the user's own
                                      # feature in it
WHY_GONE          = "gone"            # its app body, shaft or named feature is not in the new revision
WHY_ASSEMBLY_FEATURE = "assembly feature"   # an entity on a feature the user made in the old assembly
WHY_NOT_CARRIED   = "component not carried"  # an entity on a user component that is not carried
WHY_UNREAD        = "unread"          # SolidWorks would not describe it, or its reference would not read
WHY_LIGHTWEIGHT   = "lightweight"     # an entity on a component loaded lightweight in the old assembly ⟨D10⟩
WHY_NO_FILE       = "no file"         # a component whose file is not on disk (a virtual component included)
WHY_LEAF          = "leaf"            # an entity inside a user sub-assembly ⟨D13⟩
WHY_NOT_FOUND     = "not found"       # a reference read but not resolved in the new instance, or resolved to an
                                      # entity of another kind (§0.3's STOP for the latter: the carry stops)
WHY_ORIGIN        = "assembly origin" # the assembly's own origin: no route selects it ⟨D19⟩

@dataclass(frozen=True)
class CarryNamed:
    item: str                   # the mate's or component's name in the old assembly
    what: str                   # "mate" or "component"
    why: str                    # WHY_*
    subjects: Tuple[str, ...] = ()   # what the sentence names besides: the gear, the part, its why_new, the finding,
                                     # the kind word, the entity kind

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
    targets: Tuple[str, ...]    # per entity, how it is found, as the session's reference grammar takes it (§4)

@dataclass(frozen=True)
class CarryPlan:
    components: Tuple[CarryPlanItem, ...]
    mates: Tuple[CarryMateItem, ...]
    named: Tuple[CarryNamed, ...]
    clusters: Tuple[Tuple[str, ...], ...]        # each cluster's components (old Name2s), in first-mate order
    gates: Tuple[Tuple[str, str], ...]           # (step, finding) for every gate not set, as in_place_gates

def plan_carry(work: OldWork, carry: Carry, revision: Sequence[int], *,
               new_frames: Mapping[str, Frame9] = {}) -> CarryPlan: ...
```

`plan_carry` is pure. The worker calls it on the fresh `OldWork` and the new revision's frames; B's question calls it
on an `OldWork` made from the record's inventory (`workbook.update.recorded_old_work(record)`: no frames, no
definitions beyond what the inventory keeps, §7), with `new_frames` empty, to foresee what is carried and named. Where
the inventory cannot say (a mate of a schema 9 inventory has no entity kinds), the foresight says *may* (§9.1).

### 2.4 What A hands back

```python
@dataclass
class CarryResult:
    work: Optional[OldWork]                       # what was read (None: nothing could be read, `stopped` says why)
    inserted: List[Tuple[str, str]] = ...         # (old Name2, Name2 SolidWorks kept in the new revision)
    states: List[Tuple[str, Tuple[str, ...]]] = ...   # (new Name2, the new modes it reads suppressed in, read back)
    remade: List[Tuple[str, str, Tuple[str, ...]]] = ...  # (old mate name, name kept, the new modes it reads on in)
    same_error: List[Tuple[str, int]] = ...       # remade mates back in the error they had before (carried, said)
    named: List[CarryNamed] = ...                 # everything not carried, the plan's and the post-check's
    fixed: List[CarryFallback] = ...              # the clusters that fell back (§6)
    moved: List[Tuple[str, float]] = ...          # carried components the solver moved from where placed, mm ⟨D7⟩
    clashes: List[Tuple[str, Clash]] = ...        # (mode, clash) naming a carried component ⟨D8⟩
    marked_user: List[str] = ...                  # user documents SolidWorks reads modified after the carry (said)
    stopped: str = ""                             # a sentence when the carry stopped part way, else ""
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
    mode: str = ""                # the mode the post-check read it in ("" with no modes)
    subjects: Tuple[str, ...] = ()   # the gear read unable to turn (FELL_TIE), the mate and its code (FELL_NEW_ERROR)
```

`GearboxResult` gains `carry: Optional[CarryResult] = None`. `old_user_work` and `old_read` stay (W9a's sentence is
still said when `carry` is None). `log_lines()` gains a line per item (`ok      carried Sprocket-1 as Sprocket-1`,
`ok      made UserLock1 again, on in H, N and L`, `CHECK   not carried: Concentric5 (part new)`, `FIXED   …`).

## 3. The order of the job, and where it sits

`swbuild.build_gearbox`, with the steps it has today in **bold**:

1. **The gates and the plans' checks** (`_gate`, `_modes_gate`, `_assembly_rebuild_gate`, …).
2. **R. The old assembly read** (replaces W9a's `_read_before` when `carry` is given; ⟨D1⟩), before anything is
   made, in its own build bracket (`begin_build` / `end_build`, as `read_old_assembly`):
   1. every document of the old assembly and every user file it names: `GetSaveFlag` read (`documents()` walk), each
      file's time read (`mtime`, injected as today);
   2. *open in the session* (`use_open_document`): read as it stands, never activated, never shown in another mode;
      *not open*: opened `OpenDoc6(path, assembly, Silent | ReadOnly)` while
      `findings.OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN_ON_<year>` is that route (set on both versions), under the rule of
      §11.2 for the documents already open; when the finding is not that route, `OldWork.how = OLD_UNREAD` and nothing
      is carried;
   3. the components (`components()`), their frames in the mode showing (`find_component` with `lightweight_ok`,
      `component_frame`), the app bodies' frames likewise, each file `on_disk`;
   4. the states per mode by the route `COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_<year>` names (§11.1), or, opened
      read-only and `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_<year>` True, by showing each mode in that read-only
      document; else not read (`suppressed_in` None);
   5. every user mate's definition (`Session.mate_definition`, §10) and every entity classified (§4); for each entity
      that tier 1 finds, its part-level persistent reference read through its component (§4.1); the read of the
      root's `Name2` as W9c's `_read_user_work` has it (never on an assembly with a lightweight component);
   6. `GetSaveFlag` of every document again: any turned on is `OldWork.marked` (§0.3's STOP: the carry does nothing
      more, says so, and the build goes on);
   7. *opened read-only by this job*: closed unsaved (`QuitDoc`, under the job; documents it found open stay open).
3. **The new parts, the layout part, the carrier parts, the assembly built, mate-checked and saved**
   (`_build_gearbox_body`, `SaveAs3` with option 1). **The interference per mode** (`_modes_interference`), the
   assembly left in its first mode. *Nothing below runs unless the assembly saved (`result.assembly.ok` and
   `saved`).*
4. **C. The carry** (`_carry`, its own step `Step(STAGE_CARRY, stem)`, inside the change phase's bracket as W9c's
   in-place steps are), in this order, each failure stopping the carry with `stopped` and `skipped` set and every
   later step not run; nothing saved, ever:
   1. the new revision's frames read (`find_component`, `component_frame` per handle in `result.components`), then
      `plan_carry(work, carry, revision, new_frames=…)`;
   2. the gates: a step whose finding is not set leaves its items named (`WHY_UNMEASURED`, `subjects` the finding),
      never refuses the build;
   3. each carried component's file opened (`open_document`; a sub-assembly by `SUBASSEMBLY_INSERT_ROUTE`, §11.3),
      then the new assembly made the build document again by the route W9c's `AddedGear` insert uses;
   4. each inserted (`add_component` at its frame's origin), placed (`place_component`, its frame), fixed where it was
      fixed (`fix_component`); first mode showing;
   5. the states: for each component suppressed in some mode, that mode shown, `set_component_suppressed(handle,
      True)` (§10), read back; the first mode shown again; every carried component's state read in every mode on
      the way (a mismatch is a failure: §0.3, "a new component … whose per-configuration state does not read back");
   6. the mates, cluster by cluster in `CarryPlan.mates` order: entities selected by their targets (§4), `AddMate5`
      from the definition (`Session.remake_mate`, §10), renamed to the old name (`MATE_RENAME_ROUTE`; a name taken
      keeps SolidWorks' name ⟨D15⟩), its status kept; then its flags set in every new mode from `on` mapped by name
      (`set_mate_suppressed_in`) and read back (`mate_suppression`), a mode where one of its components is suppressed
      left as SolidWorks has it and not judged;
   7. one top-only rebuild (`rebuild(kind=ASSEMBLY_TRAIN)`);
   8. **the post-check, with the carried mates on** (§6): every mode shown in turn, the build's own per-mode check
      (frames, the app's mates sound, every gear free to turn) and, for the carry, each remade mate's code against
      its old code, each carried component's state and frame; the clusters judged; a cluster that falls back has its
      app-side mates deleted again, its components put back where placed and fixed, and that mode read again;
   9. the interference in each mode once more, its clashes with a carried component kept ⟨D8⟩;
   10. the first mode shown again; `GetSaveFlag` of every user document read (`marked_user`) and every old and user
       file's time read again (a change is §0.3's STOP, said, never "fixed").

**Never written:** the old assembly (no show, flag, value, put, mate, insert, delete, save, close of a document the
user had open); any user file (no save; its document may be opened, and is read, as §11.2 and §11.3 say); the new
assembly after its first save (no `Save3`, no `SaveAs3`). **Written:** only the new assembly in memory, after its
save: the inserts, the states, the mates, the fallbacks — §0.3's W9d exception.

A carry that stops leaves what it made in the new assembly, unsaved; the saved file is the build's. `CarryResult`
names what was done, what was not (`skipped`, at W9c's grain: *"making Sprocket-4's mates again and checking the
assembly"*), and everything not carried.

## 4. How each entity is found (§2.5's four tiers), against what was measured

### 4.1 Tier 1 — a file both revisions use

Every user component (the same file, inserted again) and every app part `same_file`. The entity's part-level
persistent reference is read in the old instance's part (`IComponent2.GetModelDoc2`, then the part's
`Extension.GetPersistReference3`) and resolved in the new instance's part (`GetObjectByPersistReference3`), then carried
into the new assembly through the new component (`IComponent2.GetCorresponding`) and selected (`Select4`, mark 1). The
same document is in fact used twice (one file, one document in the session), so the reference resolves against the
very document it was read from. The resolved entity's kind must be the read one's; another kind is §0.3's STOP.

| Entity on a file both use | 2026 | 2024 | Finding |
|---|---|---|---|
| a reference axis or plane (user part, the layout; Front, Top, Right, Gear Axis, Input Axis) | **measured**: 13 read, resolved, 10 mates remade equal (`w9c…-2.log` :265-279) | **measured** (`w9c24` :266-280) | `PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES_ON_<year>` (set) |
| a face | not measured | not measured | `PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_<year>` (new; the W9d probe) |
| an edge | not measured | not measured | `PERSIST_REFERENCE_ROUTE_FOR_EDGES_ON_<year>` (new; the W9d probe) |
| a vertex | not measured | not measured | `PERSIST_REFERENCE_ROUTE_FOR_VERTICES_ON_<year>` (new; None; nothing in W9d sets it) |
| a whole component (a lock) | **measured** (tier 3) | **measured** | — |

The route from the **assembly-context** entity (`IMateEntity2.Reference`) to the part-level one is not measured: for a
feature S5 found it by name in the part (`FeatureByName`). For a face or edge the API help gives
`IModelDocExtension.GetCorrespondingEntity2` ("the entity in the underlying part … that corresponds to the specified
entity in this assembly", SOLIDWORKS 2018 and later; never called by the app or the macro database); the probe
measures it beside handing the assembly entity straight to the part's `GetPersistReference3` (§11.4).

### 4.2 Tier 2 — what the app names, and base planes by tree order

On the layout part and each carrier part (new files every revision) and on an app gear part, same file or new ⟨D3⟩: a
reference feature the app names (`CarryBody.names`: `Input Axis`, `S2 X Plane`, a carrier's axes, `Gear Axis`, `Mid
Plane`, `Profile Plane`) by name; a base plane by its tree order (`plane1`..`plane3`); an origin as `origin`. The
target is the session's reference grammar the build mates by (`_component_ref`: `"<handle>:Input Axis"`,
`"<handle>:plane2"`, `"<handle>:origin"`; `"asm:plane1"` for the assembly's own planes). A name the new file does not
hold (a shaft removed) is `WHY_GONE`. A feature of the user's in an app part (not in `old_names`, not a base plane) is
tier 1 on a same file and `WHY_PART_NEW` on a new one.

| Entity | 2026 | 2024 |
|---|---|---|
| the layout's axis by name | **measured** (S5 c: UserAxis1, 2, 4, 6) | **measured** |
| the layout's base plane by tree order | **measured** (UserAngle4 to the layout's Right Plane, by name in S5; the app selects `lay:plane3` by order in W9a's setup) | **measured** |
| the assembly's own plane by tree order | **measured** (UserAsm6, `asm:plane1`) | **measured** |
| a carrier's axis or plane by name | the app's own selection (W7's builds), never in a carry | the same |
| an app gear's `Gear Axis` by name | the app's own selection (every build's mates); in a carry, not measured | the same |
| the assembly's own origin | **no route** (`_component_ref` refuses `asm:origin`): `WHY_ORIGIN` ⟨D19⟩ | the same |
| a feature the user made in the old assembly (a sketch, a plane) | `WHY_ASSEMBLY_FEATURE` (an `ASSEMBLY` entity whose feature is not one of its first three planes) | the same |

The assembly's own entity names the root component on both versions (`ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_<year>`
True); W9c's `_read_user_work` maps it, and reads the root never on an assembly with a lightweight component, where
such an entity is `UNREAD` and its mate `WHY_UNREAD` (the probe measures the root read there, §11.5).

### 4.3 Tier 3 — whole components

A **lock**'s entities are whole components (ReferenceType2 0, S5 (a): UserLock1–3), found through the component map:
a user component by its new instance, an app body by `CarryBody.handle`, selected whole (`Select4` with a mark-1
select data, the app's lock route). A body with no handle is `WHY_GONE`.

**A gear mate's entities are not whole components** (§13 item 1): m1's user gear mate on Sun read two axes,
ReferenceType2 5, features `Gear Axis` (`w9c…-2.log` :156). Each of its entities goes by its own tier (an app gear's
`Gear Axis` by name, tier 2; a user part's axis or face, tier 1).

### 4.4 Tier 4 — a face, edge or vertex of an app part made new

Never re-found (ruled, K5). `WHY_PART_NEW`, `subjects` (the gear, its `why_new`, the entity kind): *"Concentric5 was on
Sun's bore, and Sun's part is new because its Flank changed; it was not made again."* The sentence says "bore" only
where the read can say so (a cylindrical face whose axis is the gear's); otherwise "a face of Sun", "an edge of Sun".

### 4.5 Mate kinds: carried, named, and measured

§2.5's carried kinds are coincident, concentric, parallel, perpendicular, tangent, distance, angle (with limits),
lock and gear; every other kind is `WHY_KIND`. A carried kind is remade only when it is in
`CARRY_REMAKE_KINDS_ON_<year>` ⟨D4⟩, else `WHY_UNMEASURED`.

| Kind | Definition read (m1, S5 a) | Remade from its definition | Into a configured assembly, flags per mode |
|---|---|---|---|
| coincident (axis–axis, plane–plane) | both versions | both (S5 c, ×5) | not measured |
| distance (plane–plane) | both | both (×2) | not measured |
| angle (plane–plane) | both | both (×1) | not measured |
| lock | both | both (×3) | not measured |
| concentric (face–axis) | both (m1) | not measured | not measured |
| limit distance, limit angle | both (m1; range in Maximum/Minimum) | not measured | not measured |
| gear (axis–axis, user on app gear) | both (m1) | not measured | not measured |
| parallel, perpendicular, tangent | **never read** | not measured | not measured |
| width | both (m1; made only with the tab at mark 16) | — named (`WHY_KIND`) | — |
| path, slot, symmetric, profile-centre, cam, hinge, rack-and-pinion, screw, universal joint, belt/chain | — | — named | — |
| a flipped mate (any kind) | not read flipped | not measured | — |

"Into a configured assembly, flags per mode" is what the carry does: the mate is made in the new revision with its
first mode showing, then its flags set and read back in every mode. W9c sets and reads back flags this way for the
app's own mates (J10's discipline, measured on both versions), and W9a's setup did it for user mates made by the app's
`add_mate` in a configured assembly (`w9a-final…` setup, flags read back as set). For a mate remade from a user's
definition it is M9's to measure.

## 5. The read's rules, the states per mode, and placement

### 5.1 Components

Carried: a top-level user component whose file is on disk, a part or (gated, §11.3) a sub-assembly, with its file,
its referenced configuration as inserted by default ⟨D13⟩, fixed or floating, and its state per mode. Named: a file not
on disk (`WHY_NO_FILE`; a virtual component's file is "Part1^RangeBox.sldprt" inside the assembly and reads not on
disk, so it is named the same way, with "virtual" said where the name has `^`). Said, not read: a sub-assembly comes
over rigid ("set it flexible again if it was"); display states and appearances set in the assembly are not carried; a
component pattern is not carried and an instance of one comes over as a component of its own ⟨D12⟩; a part of the
user's with in-context references to the old assembly's parts still refers to them (M4 is not measured, so this is said
generally whenever a user part is carried).

### 5.2 States per mode

- Old mode → new mode by name, case aside. A mode of the new revision the old assembly has not takes the old record's
  first mode's state (`Carry.first`; plan §2.5) and is said once. An old mode the new revision has not (renamed or
  removed) loses its states, said ⟨D14⟩.
- A component `suppressed_in` None (not read per mode, §11.1) takes the mode showing's state in every mode, said once
  for all such components ⟨D2⟩.
- A lightweight component (state 1 or 4 in the mode showing) is inserted resolved and never set lightweight: the
  user's next save of the new assembly must not meet SOLIDWORKS CAM's box (plan, *Changes after W9a's demonstration*).

### 5.3 Placement

- **Clusters**: the user's components joined through user mates whose entities are on two or more user components
  (user–user mates), connected components of that graph, numbered in first-mate order; a component no user–user mate
  joins is a cluster of its own; a user mate with no user component (between app bodies, the layout, the assembly) is
  cluster −1 and falls back alone (§6).
- **Anchor** of a cluster: the app body (`CarryBody.old`) its mates reach, in this order of preference ⟨D20⟩: a user
  lock from one of its components to an app body; any other user mate to an app body; the layout or the assembly
  (world frame). Among several of one rank, the first in mate order. A body with no handle in the new revision is
  passed over. None: world frame.
- **Frame**: `new(anchor) · old(anchor)⁻¹ · old(component)` (plan §2.5), each frame as `component_frame` reads it,
  the anchor's new frame in the new revision's first mode and its old one in the old mode showing; world frame
  `old(component)` unchanged. A sprocket locked to a Sun the user turned 37° goes in at 37° to Sun's new frame.

## 6. Clusters, the fallback and the post-check

- **Made**: every mate whose entities are all found and whose kind and entity kinds are measured (§4) is remade;
  every other is named. The components stay floating where placed (or fixed): an under-defined component stays put,
  and leaving a mate out over-defines nothing.
- **The same error**: a remade mate that reads, in a mode, the error code it read in the old assembly's mode showing
  is carried as it was (`same_error`, said) and not counted against its cluster. (Its old code was read in one mode
  only: §2.1 item 2 of the plan reads codes in the mode showing.)
- **A cluster falls back in three cases, and only these**:
  1. `FELL_NEW_ERROR` — a remade mate reads, in some mode where it is on, an error code (warning or not, as the build's
     check counts it) it did not have before;
  2. `FELL_OVER_DEFINED` — `AddMate5` answered `ADD_MATE_OVER_DEFINED` (5) for one of its mates, or one of its
     components reads `COMPONENT_OVER_DEFINED` after the rebuild;
  3. `FELL_TIE` — the post-check reads, in some mode, an app gear not free to turn (`_free_to_turn`'s read, any status
     but under-defined), and the cluster has a mate on in that mode with an entity on a body of that mode's train (the
     train as that mode joins it) ⟨D6⟩.
- **The fallback**: the cluster's remade mates to app bodies, the layout, carriers and the assembly are deleted
  (`MATE_DELETE_ROUTE`, the job's own just-made mates, by the name kept); its user-to-user mates are kept; each of its
  components is put back where it was placed (`place_component`) and fixed (`fix_component`) ⟨D9⟩. Then that mode is
  read again; still failing, the carry stops (`stopped`), naming the mode and what still reads wrong, and leaves the
  new assembly as it is, unsaved. Cluster −1's mates are deleted alone.
- **The post-check with the carried mates on**: per mode, shown in Modes order then the first again (as the build
  checks): the build's own per-mode check on the app's bodies and mates, unchanged; each remade mate's code and flag;
  each carried component's state and frame against what was set (a frame off by more than 1e-6 mm or 1e-9 in a
  rotation entry is `moved`, said, ⟨D7⟩); then the clusters judged as above. The app's own check failing for a reason
  no cluster explains (an app mate in error with no carried mate on its bodies) is the build's own failure as today,
  laid to the app, and the carry stops.

## 7. The record: schema 10

`store.LINK_SCHEMA_VERSION = 10` (`_W9C_LINK_SCHEMA = 9`). New, each defaulted:

```python
@dataclass
class CarriedComponentEntry:
    name: str = ""              # Name2 in the new revision
    was: str = ""               # Name2 in the old assembly
    kind: str = ""              # "part", "assembly"
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
    subjects: List[str] = field(default_factory=list)
    sentence: str = ""

@dataclass
class CarryFallbackEntry:
    components: List[str] = ...; deleted: List[str] = ...; kept: List[str] = ...; why: str = ""; mode: str = ""

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
```

- `GearboxRecord.carry: Optional[CarryEntry] = None` — on the new revision's gearbox block; None for every gearbox
  not made by a carrying Build again… (and on a schema 9 record).
- `GearboxRecord.user_work` of the new revision: an inventory built from the carry (`UserWorkEntry`, `read_at` the
  carry's time, `assembly` the new one, `revision` the SolidWorks, `components` the carried ones, `mates` the remade
  ones with their touches in the new revision's terms and their `on`, `features` the user's features in parts the new
  revision reuses (from the old inventory), `modes` the new modes), so the footer foresees the next Update from it as
  from any inventory; the next press reads the new assembly's live work as always. (W9a set it None after a Build
  again…, UI-DESIGN §9 *"the record holds no inventory until the new revision's first Update"*; that sentence changes.)
- `UserMateEntry.entities: List[List[str]]` — per entity `[what, name, kind, feature]` (W9a's `what` and `name`, §2.2's
  `kind` and `feature`), filled by every Update's inventory from W9d on (`mate_info` read through the members S5 (a)
  read marking nothing on both versions) and by the carry; `[]` on an older inventory ⟨D5⟩.
- `LinkRecord.unsaved[new assembly] = mtime` (the existing field, the file's time after its save) whenever
  `CarryResult.unsaved`: the existing machinery (`clear_saved`, `result.opened`) then says *save it to keep them* until
  the file is newer, and a later job that finds the assembly loaded from its file says the carried items were lost
  (§9.4) ⟨D16⟩.

**Older readers**: a W9c-era app reading schema 10 refuses with its own sentence and leaves the file byte-identical
(`store.py:1324`, `:1372-1376`, as committed: *"The record of what was built, RangeBox.workbook.json, cannot be read: it
was written by a newer Gear Generator (schema 10, this one reads 9). It is left alone, so Build and Update SolidWorks
wait."*). It would otherwise drop `carry` and `entities` on its next write. **Schema 9 read forward**: `carry` None,
every `entities` `[]`, everything else as read at 9; written forward as 10 on the next write. Schema 1–8 as before.

## 8. The findings W9d reads

Each is per version (`_ON_2026`, `_ON_2024`), read with `getattr` from committed `findings.py`; a missing or None one
keeps its items from being carried, named with the finding (`WHY_UNMEASURED`), and never stops the build. Reads are
set from the W9d probe's reviewed logs; writes from M9's (patched True in that run's process for the measurement only,
as W9a's `nocarrier` and W9c's gates).

| Finding | Kind | What it gates | Set by |
|---|---|---|---|
| `OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN` | read (set, both) | the old assembly read when not open | W9c probes s5 (d) |
| `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` (new) | read | that open while some of its documents are already open (one modified): they stay as they were | W9d probe `state` (g) |
| `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` (exists, None) | read | per-mode states read unshown | W9d probe `state` (b)–(e) |
| `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED` (new) | read | that route used on an old assembly holding unsaved changes | W9d probe `state` (e) |
| `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` (new) | read | the not-open fallback: modes shown in the job's own read-only document, then closed unsaved | W9d probe `state` (h) |
| `PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES` | read (set, both) | tier 1 on axes and planes | W9c probes s5 (b) |
| `PERSIST_REFERENCE_ROUTE_FOR_FACES`, `_FOR_EDGES` (new) | read | tier 1 on faces, edges | W9d probe `faces` |
| `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` (new) | read | tier 1 on vertices | nothing in W9d: None |
| `ROOT_COMPONENT_UNRESOLVED_READ` (new) | read | the assembly's own entity read on an old assembly with a lightweight component (`GetRootComponent3(False)`) | W9d probe `state` (f) |
| `SUBASSEMBLY_OPEN_MARKS`, `_WHEN_LOADED` (new) | read | opening a user sub-assembly to insert it (§11.3) | W9d probe `sub` |
| `SUBASSEMBLY_READ_ONLY_INSERT` (new) | read | the sub-assembly opened read-only, then inserted | W9d probe `sub` (c) |
| `SUBASSEMBLY_INSERT_ROUTE` | read (set, both) | the insert itself | W9c probes p2 |
| `CARRY_INSERTS` (new) | write | user parts inserted, placed, fixed, their states set per mode and read back | M9 |
| `CARRY_INSERTS_A_SUBASSEMBLY` (new) | write | a user sub-assembly inserted by its file | M9, if its fixture holds one (else None) |
| `CARRY_REMAKE_KINDS` (new; a tuple of kind words) | write | which kinds are remade (§4.5) ⟨D4⟩ | M9 |
| `CARRY_REMAKES_ON_A_LEAF` (new) | write | a mate on a leaf of a user sub-assembly | nothing in W9d: None ⟨D13⟩ |
| `CARRY_INSERT_MARKS_USER_DOCUMENTS` (new, a fact) | read | whether inserting a user part marks its document; True only adds a sentence | W9d probe `faces` (c) |

`swbuild.carry_gates(work, carry, revision) -> List[Tuple[str, str]]` (pure) returns `(step, finding)` for each gate
not set that something in `work` needs, for A's naming and B's question, as `in_place_gates`. Steps:
`STEP_CARRY_OPEN`, `STEP_CARRY_STATES`, `STEP_CARRY_INSERT`, `STEP_CARRY_SUBASSEMBLY`, `STEP_CARRY_FACES`,
`STEP_CARRY_EDGES`, `STEP_CARRY_VERTICES`, `STEP_CARRY_KIND` (one per kind word), `STEP_CARRY_LEAF`.

## 9. What the user sees (`ui_text`)

In the register of W9a's and W9c's sentences: the user's items as *your*, names whole, counts beside nouns, the time
read, no "please", the reason after the comma.

### 9.1 The question (`build_again_question`; `carry_sentence(foresight, again)` replaces W9a's `stays_behind_sentence`)

From the record's inventory with its time, through `plan_carry` on it (§2.3). With the gates set:

> *As read at 14:02, RangeBox_r2 takes your Sprocket-1, Sprocket-2, Chain-1 and Housing-1, each where it stands against
> the gear it is mated to, and makes your 8 mates again on what they join, each on in the modes it was on in;
> Concentric5 is not made again, since it is on Sun's bore and Sun's part is new because its Flank changed. Your Keyway
> stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox.SLDASM and that file keep it. RangeBox_r2 is saved
> as built, and holds what it carries unsaved: save it in SolidWorks to keep them. The press reads RangeBox.SLDASM again
> first, and says whatever it cannot carry.*

Clauses added as they apply, each in the result too:
- a feature in a part made new only because the user typed an app value in SolidWorks (`MISMATCHED`): *Gear_m1.25_N29
  is new only because it holds Bore Diameter 12 where the workbook asks 10: answer No, type 12 in Gears!J2, and Build
  again… reuses that part with your Keyway.* (the value and cell from the record's K11 `ValueEditEntry` for that
  document; without one, *answer No, make the workbook ask what that part holds in SolidWorks, and Build again… reuses
  it with your Keyway.*) ⟨D17⟩; only because an Update left it unsaved (`UNSAVED`): *answer No and save it in
  SolidWorks first, and Build again… reuses it with your Keyway.*;
- a mate whose inventory entry has no entity kinds (schema 9 inventory) on a part made new: *your Lock3 and UserAxis4
  join Sun, whose part is new: a mate on one of its faces or edges is not made again, and the press reads which they
  are.*;
- a component lightweight as read: *Sprocket-4 was lightweight as read, so its 3 mates cannot be read through it: set
  it resolved in SolidWorks before you press, or they are not made again.*;
- states per mode not readable on this SolidWorks (§11.1): *Your components take in every mode the state they have in
  the mode RangeBox.SLDASM shows when you press: whether you suppressed one in another mode cannot be read without
  changing RangeBox.SLDASM.*;
- a gate not set: *Gear Generator has not yet been shown to carry concentric mates into a new revision on SolidWorks
  2024 (findings.CARRY_REMAKE_KINDS_ON_2024), so Concentric5 and Concentric8 are not made again.*; with
  `CARRY_INSERTS` not set, W9a's sentence follows, led by *Gear Generator has not yet been shown to carry your work into
  a new revision on SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024), so as read at 14:02, …*;
- the version not known (a record no job of this version wrote): W9c's mixed form, *Whether RangeBox_r2 takes your
  work depends on the SolidWorks in use: Gear Generator has been shown to do so on SolidWorks 2026, not yet on
  SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024), and the press reads which it runs on.*;
- nothing on record: *Anything you added to RangeBox.SLDASM in SolidWorks the press reads first and carries into
  RangeBox_r2 where it can, saying whatever it cannot.*

### 9.2 The result (`carried_status(result, again, old_path)`, after `gearbox_status`, replacing `stayed_behind_status`)

> *Carried into RangeBox_r2, unsaved: your Sprocket-1, Sprocket-2, Chain-1 and Housing-1, each where it stood against
> its gear, and 7 of your 8 mates, each on in the modes it was on in. Not carried: Concentric5, which was on Sun's
> bore, and Sun's part is new because its Flank changed. Your Keyway stays in Gear_m1.25_N29 (RangeBox.SLDASM and that
> file keep it). Save RangeBox_r2 in SolidWorks to keep what was carried.*

Then, as they apply: the fallback, as the plan words it, *Sprocket-1 and Chain-1 are fixed where they stood in
RangeBox_r2: with your Lock3 and Concentric5 made again SolidWorks reads Sun unable to turn, so those two were not
kept; Coincident7 between them was.* (`FELL_NEW_ERROR`: *… with your Lock3 made again it reads error 46, which it did
not in RangeBox.SLDASM, …*; `FELL_OVER_DEFINED`: *… your Lock3 made again over-defines them, …*); *Your UserDist4 was in
error in RangeBox.SLDASM and is in RangeBox_r2 too, as it was.*; *SolidWorks moved Sprocket-4 2.0 mm from where it stood
against Sun when your mates were made again.*; a clash, *In mode L, your Sprocket-2 interferes with RangeSlv
(12.3 mm³).*; the states, *Your components take in every mode the state they had in H, the mode RangeBox.SLDASM showed:
their states in N and L could not be read without changing it.*, *2L, a mode new in RangeBox_r2, takes H's states and
flags for your items.*, *Your items' states in 4L, which RangeBox_r2 has not, are not carried.*; *Your sub-assembly
Drive-1 comes over rigid: set it flexible in SolidWorks again if it was.*; *Assembly features of yours (cuts, patterns,
sketches, planes) are not carried; a component of a pattern comes over as a component of its own. A part of yours made
in context of RangeBox.SLDASM still refers to its parts.*; *SolidWorks reads Sprocket.SLDPRT modified since it was
inserted into RangeBox_r2; nothing in it changed.* (only with `CARRY_INSERT_MARKS_USER_DOCUMENTS` True); a stop, *Carrying
your work stopped at making UserDist4 again (SolidWorks: …), so it did not get to making Sprocket-4's other mates again
and checking the assembly; what was carried before it is in RangeBox_r2, unsaved, and RangeBox_r2 as built is saved.*;
nothing read, *RangeBox.SLDASM could not be read (…), so nothing of yours was carried; it and your files are as they
were.*; a read that marked a document (§0.3), *Reading RangeBox.SLDASM marked Sprocket.SLDPRT as changed in SolidWorks,
which Gear Generator never does on purpose, so nothing of yours was carried; nothing in it changed, and RangeBox.SLDASM
and your files are as they were on disk.* The build's own sentence is said first and unchanged in every case.

### 9.3 Each reason (`carry_named(named)`, one clause per item, joined)

| `why` | Clause |
|---|---|
| `kind` | *Width1 is a width mate, which Gear Generator does not make again* |
| `unmeasured` | *Concentric5 is a concentric mate, which Gear Generator has not yet been shown to make again on SolidWorks 2024 (findings.CARRY_REMAKE_KINDS_ON_2024)*; for an entity kind: *… is on a face of Sprocket-1, which …(findings.PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024)* |
| `part new` | *Concentric5 was on Sun's bore, and Sun's part is new because its Flank changed* |
| `gone` | *Lock4 was on G5, which RangeBox_r2 does not have*; *UserAxis2 was on the layout's Output Axis, and RangeBox_r2 has no shaft Output* |
| `assembly feature` | *Coincident9 is on Plane1, a plane you made in RangeBox.SLDASM, which is not carried* |
| `component not carried` | *Lock6 joins Part1^RangeBox, which is not carried* |
| `unread` | *SolidWorks would not describe Mate12 wholly* |
| `lightweight` | *Lock7 is on Sprocket-4, which was lightweight in RangeBox.SLDASM, so what it joins could not be read* |
| `no file` | *Part1^RangeBox is a virtual component, with no file of its own, so it is not carried*; *Bracket-1's file Bracket.SLDPRT is not on disk, so it is not carried* |
| `leaf` | *LeafAxis is on a part inside your sub-assembly Drive-1, which Gear Generator does not make again* |
| `not found` | *Coincident8's face of Sprocket-1 could not be found again in Sprocket.SLDPRT* |
| `assembly origin` | *Coincident10 is on RangeBox.SLDASM's own origin, which Gear Generator cannot select* |

### 9.4 The footer afterwards

While the new assembly is marked unsaved by the carry: *RangeBox_r2 holds what Build again… carried of yours, not
saved: save it in SolidWorks to keep it.* Found closed unsaved by a later job: *RangeBox_r2 was closed without saving
after Build again… carried your work into it, so it does not hold it; RangeBox.SLDASM still does.* Nothing offers to
carry again ⟨D11⟩.

## 10. What A adds to `swcom.Session` (each a wrapper, with `GetSaveFlag` read around it in the probe and M9)

- `mate_definition(handle) -> MateDefinition` — S5 (a)'s read (`GetTypeName2`, `IMate2` Type, Alignment, Flipped,
  variations, `GetDefinition`'s fields, `MateEntity(i)`'s ReferenceComponent, ReferenceType2, Reference and its kind),
  measured marking nothing on both versions.
- `entity_reference(mate_handle, index) -> (kind, hex or "", why)` — tier 1's read for feature, face and edge entities
  (§4.1; the face and edge route as the probe finds it).
- `component_states(names, configurations) -> Dict[str, Dict[str, bool]]` — the unshown route
  `COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_<year>` names; refused while it is None.
- `open_read_only(path) -> Optional[DocInfo]` and `close_unsaved(path)` — `OpenDoc6(Silent | ReadOnly)` and `QuitDoc`,
  the latter refusing a document this session did not open.
- `select_by_reference(handle, kind, hex, append)` — tier 1's resolve, `GetCorresponding`, kind checked, `Select4`.
- `remake_mate(handle, definition, targets, name) -> (name kept, status)` — `AddMate5` from the definition on the
  selected targets (S5 (c)'s call), renamed.
- `set_component_suppressed(handle, suppressed)` — `IComponent2.SetSuppression2` in the mode showing, read back
  (measured by the W9c probes' s5 (e) and W9a's `lightweight` as the probe's own call, never the app's).

## 11. The three things owed before W9d is designed, and two more

### 11.1 A component's state per configuration without marking the assembly

*What is measured* (both versions): `IFeature.IsSuppressed2(swSpecifyConfiguration, names)` on the component's feature
reads every mode unsuppressed, wrong in L; each configuration's `GetRootComponent3(True)` and its child's
`GetSuppression2` read right and marked the assembly (`w9c…-2.log` :281-284, `w9c24` :282-285). A show marks the
assembly on both versions and stales every handle (assemblies/13; GOTCHAS §108). `IModelDoc2` has nothing that clears
the flag but a save.

*Candidates, from the installed API help* (2024's `sldworksapi.chm`), in the order the probe tries them, every one with
`GetSaveFlag` of every document around it, nothing shown:
1. **`IConfiguration.GetComponentSuppressionState(CompName)`** — "Gets the suppression state of the specified component
   in this configuration", Boolean (True suppressed); since SOLIDWORKS 2001Plus; its example calls it with
   `IComponent2.Name` on the active configuration. Reached by `GetConfigurationByName(mode)`, which is measured. It
   resolves nothing by its signature. Never called by the app or the macro database. **The likeliest.**
2. **`IConfiguration.GetRootComponent3(False)`** — the help's Return Value: "Null or Nothing, if Resolve is set to false
   and the configuration is not active". So it cannot read another mode by its documentation; the probe confirms that
   cheaply, and reads it on the active mode (it is also §11.5's read).
3. **`GetRootComponent3(True)` taken apart**: `GetConfigurationByName`, `GetRootComponent3(True)`, `GetChildren`,
   `Name2`, `GetSuppression2`, each with the flags read after it, to name the call that marks (the review's ask). It is
   known to mark; this only says where.
4. The not-open case's own route: the job's read-only document shown mode by mode and closed unsaved (§11.2).

Considered and not taken: `IAssemblyDoc.CompConfigProperties6` (a setter); opening a copy of the old assembly file
under another name (the app would write a file, the copy reads the disk not the session, and two documents of the same
parts are new territory).

*What the probe also asks of candidate 1*: that it reads the state of an unsaved change (a component suppressed in N
and not saved: `…_READS_UNSAVED`), that it leaves a lightweight component lightweight, and that it answers for a
component suppressed in the mode showing.

*What the app does* ⟨D2⟩:
- **Candidate 1 (or any) agreeing with the shown truth and marking nothing, on both versions**: the route, in both
  situations (old open, possibly unsaved: only if `…_READS_UNSAVED` is True, else as the next bullet when its
  `GetSaveFlag` is True; not open: always).
- **No clean route, the old assembly open in the user's session** (possibly with unsaved changes): never shown
  (§0.3 as the user approved it; the "third exception" cannot keep the flag as it was when it starts clear, and when it
  starts set a show still re-solves that mode's mates in the user's document, a change of its state). Each component
  takes the mode showing's state in every mode, said in the question and the result (§9). Recommended.
  *Alternatives:* show and restore, leaving the flag set and saying *RangeBox.SLDASM shows as changed: nothing in it
  was* (needs the user's word: it is their document); refuse the carry until the user closes or saves it (costly for
  the common case, where nothing is suppressed per mode at all).
- **No clean route, the old assembly not open**: the job opened it read-only; if `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN`
  is True (no dialog on the close, no file time changed, the documents that were open before as they were), each mode
  is shown there and read, and the document closed unsaved: its mark goes with it. Else as the open case.

### 11.2 Opening the old assembly read-only when some of its documents are open

After a Build again… builds, the parts the new revision reuses are open in the session (the same files as the old
assembly's), and a part of the user's may be open in its own window with unsaved edits. The read-only open of the old
assembly then loads into those documents. Measured: the read-only open of an assembly not open, every component
closed, reads read-only with its flag False (`OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN`). Not measured: what it does to
documents already open (made read-only? their changes kept? marked?), and closing it after its modes were shown. The
probe measures both (`state` (g), (h)). Until `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS` is True, the not-open case reads
only when none of the old assembly's user documents is open — else it is `OLD_UNREAD` for those components' mates,
named *"Sprocket.SLDPRT is open in SolidWorks, and opening RangeBox.SLDASM beside it has not been shown to leave it as
it is"* ⟨D1⟩. The read happens before the build (⟨D1⟩), so the reused parts are not yet open then unless the user had
them open.

### 11.3 Whether opening a healthy user sub-assembly marks it

The insert route opens the sub-assembly first (`SUBASSEMBLY_INSERT_ROUTE`); a sub-assembly with a missing part read
**modified** straight after a Silent open (`SUBASSEMBLY_MISSING_PART_READS`). A healthy one's flag after the open was
not read. The probe reads it in three situations: not loaded at all (`OpenDoc6` Silent), loaded as a component of an
open assembly (`OpenDoc6` answers the loaded document, warning 128 for a part, `API-LEDGER.md` OpenDoc6), and opened
read-only then inserted. *Ruling recommended* ⟨D13⟩: a sub-assembly is carried only by a situation whose open is
measured marking nothing (`SUBASSEMBLY_OPEN_MARKS` / `_WHEN_LOADED` False), or by the read-only insert if
`SUBASSEMBLY_READ_ONLY_INSERT` is True; otherwise it is named, *your sub-assembly Drive-1 is not carried: opening it to
insert it marks it as changed in SolidWorks, and Gear Generator never changes a file of yours*. A mate on a leaf inside
it is named while `CARRY_REMAKES_ON_A_LEAF` is None (no run makes one).

### 11.4 A face's persistent reference

The probe makes a concentric on a sprocket's bore (face–axis), a coincident between two sprockets' end faces
(face–face, user–user), a concentric on a sprocket's circular edge (edge–axis) and a parallel between a sprocket's end
face and Sun's (a face of an app part on the same file, and the parallel kind read for the first time). It reads each
entity's kind (`GetSurface` / `GetCurve` / `GetPoint` answering) and whether the assembly-context reference names its
component (`IEntity.GetComponent`), then two routes to the part-level reference (`GetCorrespondingEntity2` in the
assembly; the mate's reference handed to the part's `GetPersistReference3`), resolves each in the part, carries it back
through the component, and asks `ISldWorks.IsSame` of the original and the round trip. Then the four mates are made
again in a second assembly from their read definitions on the resolved entities, as S5 (c) did, with the user's
documents' flags read around the inserts. *Ruling*: a face or edge entity is tier 1 only by the route the probe
proposes, set per version; unset, `WHY_UNMEASURED`.

### 11.5 Two more the contract depends on

- **The root read on an assembly with a lightweight component** (the W9c review's should-fix 5, not yet measured):
  `GetRootComponent3(False)` and `(True)` on the active configuration with a lightweight user component, flags and
  states around each. W9d reads an old assembly the user may have left with lightweight components; a mate to its own
  plane is otherwise `WHY_UNREAD` there.
- **A mate on a component suppressed in a mode**: read by the probe as a fact (its flags in that mode), so §3 step 4.6
  ("a mode where one of its components is suppressed left as SolidWorks has it") rests on a reading.

## 12. Choices for the coordinator

- **⟨D1⟩ Read before anything is made, carry after the save.** The plan has the read after the build. Reading first is
  W9a's place (`_read_before`); the read changes nothing of the new revision, so the build's result still never rests
  on the carry, and the old assembly is then read before the build opens the reused parts (§11.2), and a read-only one
  is closed before the build begins. *Alternative:* the plan's order (read after the save, the reused parts open).
  Recommended: before.
- **⟨D2⟩ States per mode with no clean route** (§11.1): open → the mode showing's state in every mode, said; not open
  → shown in the job's own read-only document and closed, if measured clean, else the same. *Alternatives:* show and
  restore in the user's document with the flag left set (needs the user's word); refuse the carry. Recommended as
  written. Moot if candidate 1 is clean on both versions.
- **⟨D3⟩ An app gear part's own named features (`Gear Axis`, `Mid Plane`, `Profile Plane`) and its base planes are
  found by name and tree order on a part made new too** (tier 2 widened). The plan's tiers do not cover them (tier 1
  needs the same file, tier 2 lists the layout, carriers and the assembly, tier 4 names faces, edges and vertices), and
  its tier 3 sends a gear mate through the component map, which S5 found wrong (§13 item 1). These are the app's own
  names, which every build's mates already select by; it is not finding by geometric role. *Alternative:* name every
  mate on an app part made new except a lock. Recommended: widened.
- **⟨D4⟩ One per-version tuple of kinds, `CARRY_REMAKE_KINDS_ON_<year>`**, set from M9's kinds remade clean in a
  configured assembly with their flags read back, rather than a finding per kind. S5's
  `MATE_REMAKE_ON_AXES_PLANES_AND_LOCKS_ROUTE` alone lets no kind through (one-configuration assembly, no flags).
  *Alternative:* a finding per kind (more names, the same evidence). Recommended: the tuple.
- **⟨D5⟩ Entity kinds kept in the inventory (`UserMateEntry.entities`)**, read by every Update from W9d on, so the
  question foresees a face mate on a part made new. The read is S5 (a)'s, marking nothing on both versions, but it is
  a new read in the Update's path. *Alternative:* the question says only *may*. Recommended: kept.
- **⟨D6⟩ A tie laid to every cluster with a mate on in that mode on that train** (conservative), after all clusters are
  made, then that mode read again. *Alternatives:* remake cluster by cluster with a tie read after each (a show per
  cluster per mode: slow); bisect. Recommended: as written, said per cluster.
- **⟨D7⟩ A carried component the solver moved is said, not a fourth fallback case.** The plan lists three. Recommended.
- **⟨D8⟩ Interference per mode again after the carry**, clashes with the user's components named (W9a names them
  already in Update). Not in the plan; costs a few seconds a mode. Recommended.
- **⟨D9⟩ The fallback's writes have no gate of their own**: deleting the job's own just-made mates (`MATE_DELETE_ROUTE`,
  verified on both versions on mates) and fixing (`fix_component`) are not new kinds of write. M9 must still exercise a
  fallback (a tied cluster). *Alternative:* `CARRY_FALLS_BACK_ON_<year>`, None until M9, the carry stopping where a
  fallback is needed. Recommended: no gate.
- **⟨D10⟩ A lightweight component in an open old assembly**: carried by its file, resolved; its mates' entities on it
  are `WHY_LIGHTWEIGHT` (no document to read a reference in; resolving it would write the user's document). The
  question foresees it from the recorded state. *Alternative:* refuse the Build again… before anything is made until
  it is resolved (the build would then rest on the user's work). Recommended as written.
- **⟨D11⟩ No "carry again".** A stopped or partial carry names what is left; there is no press that carries into an
  existing revision. *Alternative:* a later W-stage. Recommended: deferred, said.
- **⟨D12⟩ Component patterns are not read** (`IsPatternInstance` is new and no fixture has one): an instance comes over
  as a component of its own; one generic sentence. *Alternative:* the read behind a finding, M9 given a pattern made
  by hand. Recommended: not read.
- **⟨D13⟩ Sub-assemblies by measured open only** (§11.3); a leaf mate named; the referenced configuration as inserted
  by default (not read: `IComponent2.ReferencedConfiguration` is verified as a put for in-context parts only).
- **⟨D14⟩ Modes by name**; a new mode takes the old record's first mode's states ("first mode" in §2.5 read as the old
  one's); an old mode not in the new revision dropped and said; renamed rows not matched by position.
- **⟨D15⟩ Remade mates keep their old names**; a taken name keeps SolidWorks' name, said in the log.
- **⟨D16⟩ The new assembly marked unsaved on record** when anything was carried, through the existing `unsaved` field.
- **⟨D17⟩ The MISMATCHED advice's value and cell** come from the record's K11 refusal for that document; else generic.
- **⟨D18⟩ M9's edit**: Sun's Flank to arcs as the plan says, if the workbook takes a mixed-flank mesh without an error;
  else Sun's Part name (W9a's `again` sections' edit, the same class: the file must change).
- **⟨D19⟩ The assembly's own origin is named** (no route selects it; `_component_ref` refuses it).
- **⟨D20⟩ The anchor rule** of §5.3 (a lock first, then any mate to an app body, then the world).
- **⟨D21⟩ The carry never refuses the build.** A carry that cannot run (gates unset, a read that marks, the old
  assembly unreadable) names everything and lets the build stand.

## 13. In the plan, contradictory or not buildable as written

1. **§2.5 tier 3 and K5, "a lock or gear mate references whole components"**: measured false for a gear mate (m1's
   user gear mate on Sun: two axes, ReferenceType2 5, `Gear Axis`); only a lock does (S5 (a)). ⟨D3⟩.
2. **§0.3's third exception and §2.5, "shows the old assembly's modes and restores … `GetSaveFlag` unchanged"**: a show
   turns the flag on (both versions), so it cannot hold for an assembly that starts unmarked (already said in the
   plan's last section). ⟨D2⟩.
3. **§2.5's carried kinds include parallel, perpendicular and tangent**, which no run has even read; and M9 as written
   (two clusters, a bore mate, a keyway) measures only some kinds. Under the standing rule each other kind stays named
   until a run remakes it; M9's fixture below widens the kinds it carries.
4. **"A mode new in this revision takes the first mode's state"**: which first mode is not said. ⟨D14⟩.
5. **§2.5's record "schema 9"** is superseded by the last section's 10; this note follows 10.
6. **"Frames are read in the old assembly's active mode only" and "placed once, in the first mode"**: the two modes
   may differ (the user left L showing). Placement relative to the anchor's own frame in each (§5.3) makes this
   consistent for every component anchored to a gear; one anchored to the world keeps its world frame.
7. **"No `Save3` … the result ends *RangeBox_r2 holds them unsaved*"**: true, and the new assembly is already marked
   modified by the build's own per-mode interference shows today; nothing changes in what is saved.

## 14. Tests each package owes against the fake

### 14.1 Package A (the worker)

- Each row of §2.5's table, on a `RangeBox` built by the fake with a carry: a user part carried fixed and floating, its
  state per mode set and read back; a sub-assembly carried (gate patched) and named (gate None); a virtual component
  and a file not on disk named; a pattern instance carried as its own (D12); each carried kind remade with alignment,
  flip, values (limits, gear ratio and Reverse) and flags per mode; each other kind named `WHY_KIND`; a kind not in
  `CARRY_REMAKE_KINDS` named `WHY_UNMEASURED`; an assembly feature's mate named.
- A mate whose entity is not found (`WHY_NOT_FOUND`, `WHY_GONE`): named, its component floating where placed, its other
  mates remade. A reference resolving to another kind stops the carry (§0.3).
- A remade mate in the error it had before: carried, `same_error`, its cluster not fallen back.
- A cluster that ties a gear: its mates to app parts, the layout and the assembly deleted again, its user–user mates
  kept, its components back where placed and fixed, every app gear free after; a new error and an over-definition
  (status 5) each falling back; cluster −1 alone.
- A sprocket locked to a Sun turned 37° in the old assembly goes in at 37° to the new Sun; one anchored to RangeSlv
  read in L and placed in H stands against RangeSlv's H frame as it stood against its L frame.
- Nothing written to the old assembly (the fake fails any write while the old assembly is the current document, any
  show of it, any `close_unsaved` of a document the job did not open); nothing saved after the new assembly's first
  `save_as`; every user file's saved state and time unchanged; on the read-only path, the job's own document shown and
  closed unsaved only with `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` patched.
- A mode new in the revision takes the old first mode's states and flags; an old mode not in it is said.
- Every gate None: nothing carried, every item named with its finding, the build's result and record unchanged from
  W9c's.
- A read that marks a document (the fake doctored): nothing carried, said, the build stands.
- Old open: never `open_document`ed, never activated; old not open: opened read-only and closed.
- A lightweight user component: its mates `WHY_LIGHTWEIGHT`, the component carried resolved, nothing resolved in the old.
- Tier 1 on faces and edges (findings patched) and named while None; tier 2 by name, a shaft gone named, base planes by
  order, the assembly's plane by order, its origin named; a gear mate on the new Sun's `Gear Axis` found by name (D3).
- A carry that stops part way (a raise at the third `remake_mate`): `inserted`, `remade` list what was done,
  `skipped` what was not, the new assembly saved as built, the rest unsaved.
- `plan_carry` and `carry_gates` on hand-made `OldWork`s.

**What the fake gains**: a user mate's whole definition (type, alignment, flipped, values) and per-end entity kinds
(`whole`, `feature`, `plane<n>`, `origin`, `face:<id>`, `edge:<id>`, `vertex:<id>`) on a part file; a persistent
reference per (file, entity) that resolves in any instance of the same file and in no other; `component_states` per
configuration with a `states_mark` knob (marks or not) and an `states_read_unsaved` knob; `open_read_only` and
`close_unsaved` with the read-only document's own marks; `set_component_suppressed` in the mode showing;
`remake_mate` with doctorable status, error after, and a tie (`constrained` 3 on a train's gears while a given user
mate is on in that mode); the old assembly's documents' saved state and times, with an `AssertionError` on any write to
them; an `AssertionError` on any `save_as` after the new assembly's.

### 14.2 Package B (planning, the question, the result, the record, the window)

- `carry_for` from a record and a plan: planet copy *k* to copy *k*; a gear removed with handle `""`; the layout and
  carriers; `same_file` from `reuse`; `why_new` from the structural reasons and `made_new` (Flank, Part name,
  `UNSAVED`, `MISMATCHED`).
- The question from the record's inventory with its time: carried and named, the feature in a part made new with why,
  the `MISMATCHED` advice with the cell and value and without, the `UNSAVED` advice, a schema 9 inventory's *may*, a
  lightweight component, the states clause, a gate None (each kind and `CARRY_INSERTS`), the version mixed, nothing on
  record.
- The result's sentences for each `why` and each fallback kind, `same_error`, `moved`, a clash, a stop, nothing read, a
  read that marked.
- Schema 10 written and read back; a schema 9 record read forward and written as 10; a W9c-era reader (the store at 9)
  refusing 10 with its sentence and leaving the file byte-identical.
- After a carry: the new revision's `user_work` from the carried items, the footer's foresight of the next Update from
  it; the new assembly marked unsaved and the footer's line; found closed by a later job, the lost line.
- The round trip through the window's path: classify → the question → `_start_build` with `carry` → `build_gearbox` on
  the fake → `_finish_build` → the record → the footer.
- UI-DESIGN §9's *Build again?* paragraph and the W9a section's last sentence rewritten (not a test).

## 15. The demonstration (M9), in outline

**Fixture**: a copy of W9a's `setup.master` (RangeBox with Sprocket-1 and -3 locked to Sun and on Input Axis,
Sprocket-2 locked to RangeSlv on Output Axis, Sprocket-4 by a distance to Sprocket-3 and an angle to the layout, the
fixed Housing-1, the User Keyway in Sun's part; `W9A-DEMONSTRATION.md`), to which the script adds, by the probe's
routes: Chain-1 (a user part) concentric on Sprocket-1's bore face and coincident face to face with it (cluster one:
Sprocket-1, -3, Chain-1, on Sun); Housing-2 mated to the layout by planes (cluster two); a concentric on Sun's bore from
Sprocket-5 (tier 4, named); a parallel and a limit distance on user parts (kinds); a user gear mate from Sprocket-6's
axis to Sun's `Gear Axis` (D3); Sprocket-7 suppressed in L (states per mode); a mate to the assembly's own Front plane
(tree order); a tied cluster, Sprocket-8 locked to Sun and to the fixed Housing-1 (FELL_TIE); with the sub-assembly
findings set, a user sub-assembly on Output Axis. Saved as the run's own copy before the sections, as W9a's setup does.

**The edit**: Sun's Flank changed (⟨D18⟩) and a shaft added (a gear on a new shaft meshing nothing it would refuse), so
Sun's part is a new file and every other part is reused; typed in Excel by W8's `edit`.

**Sections**: `carry-gates` (every W9d write gate None: the question and the result name everything with its finding,
the build as W9c's; ~10 min); `carry` (the gates patched True in the process, the old assembly open with H showing:
the Done-when below; ~35 min); `carry-closed` (the old assembly closed: read read-only, the states by the route or the
read-only show; ~20 min); a 2024 run of `carry` alone in a fresh session (~70 min).

**Judged** (every mode shown, every read before and after): RangeBox_r2 saved as built; both clusters carried, each
component at its pose against its gear to 1e-6, every remade mate's definition equal to the old one and on in the modes
it was on in, code 0; the bore mate on Sun named `WHY_PART_NEW`; the keyway named in the question and the result with
why; the tied cluster fixed with its user–user mate kept and Sun free to turn in every mode; Sprocket-7 suppressed in L
alone; the gear mate on `Gear Axis` remade; every app gear free to turn in every mode; the carried items unsaved and
RangeBox_r2's file time that of its save; RangeBox.SLDASM's flag, active mode, every component's frame and state, every
mate's code, flag per mode and entities, and every user file's time unchanged; no dialog; the record at schema 10
holding the carry, and the footer's line. Proposes `CARRY_INSERTS`, `CARRY_REMAKE_KINDS` (the kinds remade clean) and,
with a sub-assembly, `CARRY_INSERTS_A_SUBASSEMBLY`.

## 16. What each package writes, in parallel, in this one checkout

- **A** first commits the shapes of §2 and the pure `plan_carry` and `carry_gates` (one commit, so B can import them),
  then the read (§3 R), then the carry's steps in order, each with its fake support (§14.1), then the findings' names
  in `findings.py` (all None but those already set).
- **B** writes `carry_for`, `recorded_old_work`, the question's and the result's sentences (§9), schema 10 and the
  finish (`finish_build` writing `carry`, the new `user_work` and the unsaved mark), the window's `_start_build` and
  `_finish_build`, UI-DESIGN §9; against the dataclasses and pure functions first, then against the fake once A's
  worker lands. Neither changes the other's files; a shape change here is a stop-and-ask.
