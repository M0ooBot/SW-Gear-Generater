# W9d package A (the worker): hand-back note

Package A of W9d, against `W9D-INTERFACES.md` as committed at `23ed8c5` (the re-check's R1, R2, S-a to S-g taken).
Written and tested against the fake (`tests/test_swbuild.FakeSolidWorks`) only; no SolidWorks or Excel was started.

## State

See the commits beginning "W9d shapes:", "W9d plan_carry:" and "W9d worker:" on branch `w9d`.

**Done** (§17's order): the shapes; `plan_carry` and `carry_gates`; `UserMate.entities`; the read R, open path and
not-open path under R.2's conditions as revised (R1, S-e, S-f), with the states per mode by the unshown route, by the
read-only show, or not read (D2); the carry C: frames, plan, open and insert (a file of several configurations with its
configuration passed and read back), place, fix, states in every mode read back, mates cluster by cluster (made, read
back, flagged per mode and read back, one top-only rebuild, judged: new error, over-definition, tie; the same error
carried; the fallback alone), the post-check per mode (`moved` in the anchor's frame, per-mode clusters judged there,
clashes naming a carried component), the user documents' flags and the files' times. `swcom.Session` gains §10's members.

**Not done, or done only in part** (each also in the lists below):
- The "once reversed" retry of §10 (a remade mate whose read-back has its entities the other way is made again
  reversed once): not written. A read-back that differs is deleted again and named `WHY_DIFFERS`.
- A gear mate made again with the wrong sense is not made again with the other Flip once (§10, W5's remake): it is
  deleted and named `WHY_DIFFERS` ("sense").
- `log_lines()` gains the carry's lines (§2.4) through `CarryResult.log_lines()`, worded here, not by B.
- The pattern instance's read (`PATTERN_INSTANCE_READ`) and `IsVirtual` (`VIRTUAL_READ`) are never read: both
  findings None, so the `^` rule decides and `pattern_instance` stays None.
- The coaxial read: `Session.entity_reference` never reads `coaxial` (no route is written for it until
  `COAXIAL_FACE_READ` is set); the fake gives it behind its knob, so §4.3's face rule is shown on the fake only.
- A sub-assembly is inserted by `add_component` like a part (no read-only insert route is written); it is reached only
  with `CARRY_INSERTS_A_SUBASSEMBLY` patched, and no test inserts one on the fake.
- A virtual component, a file not on disk, a pattern instance, a kind not carried, an assembly feature's mate, an
  origin entity, tier 2 by name and a shaft gone: tested in `plan_carry` on hand-made work, not end to end on the fake.
- The per-mode tie of a cluster whose flags differ by mode (tying in L only) is written (`_carry_post_check`) but has
  no test on the fake.
- The interference run inside the carry's post-check uses `findings.INTERFERENCE_CHECKED`; no test makes a clash
  naming a carried component.

## Shape changes and deviations

1. **`STAGE_CARRY = "carry"`** (§3 C names `Step(STAGE_CARRY, stem)` but §2 does not list it). Added beside the
   `STEP_CARRY_*` names, and left out of `STAGES` (a W8 test pins `STAGES[-1] == STAGE_MODE`). `ui_text.progress_text`
   falls back to the step's name for a stage it does not know, so nothing of B's breaks; B may give it its own words.
2. **`STEP_CARRY_STEPS`** and **`ENTITY_KINDS`**: tuples of the `STEP_CARRY_*` and `ENTITY_*` names, added for tests
   and B's wording tables. Additions only.
3. **`OldComponent.configurations: Optional[Tuple[str, ...]] = None`**, at the end, defaulted. The revision at `23ed8c5`
   (§5.1, S-a) carries a file of one configuration by today's insert and a file of several only with both findings set,
   so the worker must know how many configurations the file has (`GetConfigurationNames` on its document), which §2.2
   has no field for. None means not read. `plan_carry`'s rule: one configuration, carried by today's insert (gate
   `CARRY_INSERTS` only); several, carried only while `REFERENCED_CONFIGURATION_READ` and
   `CARRY_INSERTS_IN_A_CONFIGURATION` are True, its configuration always passed; None, it cannot tell, so it names the
   component `WHY_CONFIGURATION` (never guessed). **For B**: an `OldWork` built from the record's inventory
   (`recorded_old_work`) has None here unless the record keeps it, so the foresight names such a component as one whose
   configuration may not be carried; B may keep the count in the inventory or word that clause as *may*.
4. **`findings.DEPENDENCIES_READ_ON_<year>`**, None, added after the shapes commit at the coordinator's word (the
   revision's S-f), pinned with the others in `tests/test_findings.py`.
5. **`STEP_CARRY_FEATURES = "find a reference feature again"`**, a step not in §8's list, for tier 1 on an axis or
   plane (`PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES`, set on both versions). It is met only on a SolidWorks whose
   version is not known; B may word it or leave it to the fallback.
6. **Additions beside `plan_carry`** (public, pure, for B's wording and tests): `CARRY_KIND_WORDS` (§4.5's carried
   kind words, the values `CARRY_REMAKE_KINDS` is made of), `carry_kind(mate)` (the kind word of an `OldMate`, a
   limit told by "Limit" in `GetTypeName2` or a Maximum/Minimum value), `selection_reversed(kind, entities)` (§10's
   ledger rule), `gear_sense(values, params)` (§10's sense), `SEL_*` (`swSelectType_e` as `ReferenceType2` reads it),
   `OPEN_READ_ONLY_ROUTE`.

## Where the contract was unclear, and what was chosen

- **`STEP_CARRY_KIND` "one per kind word"** (§8): `carry_gates` gives `(STEP_CARRY_KIND, "CARRY_REMAKE_KINDS_ON_<y>")`
  **once**, however many kinds it keeps back; each kind word is in its mate's `CarryNamed.subjects` (`("parallel",
  finding, version)`). A step string per word would not compare equal to `STEP_CARRY_KIND`.
- **A mate on a leaf**: always named `WHY_LEAF` (subjects: the sub-assembly's Name2), and the gate
  `CARRY_REMAKES_ON_A_LEAF` kept while it is None. §2.3's reference grammar has no form for a leaf, so even with the
  finding set nothing could be made; named until a grammar is written.
- **An origin entity**: named `WHY_UNMEASURED` ("origin", `ORIGIN_ENTITY_READ_ON_<y>`) whether or not that finding is
  set, for the same reason (§4.2 writes no route).
- **Reasons, one per item, in this order**: a mate not wholly read (`WHY_UNREAD`, also an entity of kind `""` or
  `ENTITY_UNREAD`, which is how B's schema 9 inventory will come in), on a lightweight component, a kind not carried,
  on a leaf, on a component not carried, then entity by entity in `MateEntity` order (the first entity that cannot be
  found names the mate), then `CARRY_REMAKE_KINDS`, then the gear-mate gate. Components: virtual, not on disk,
  `CARRY_INSERTS`, sub-assembly gates, configuration, frame.
- **Tier 1 targets with no reference read**: `plan_carry` still plans `"ref:<handle>:<kind>:"` (B's foresight has no
  references: the inventory does not keep them); the worker names `WHY_NOT_FOUND` when an empty or unresolved
  reference meets it.
- **User component handles** in targets: `"carried<i>"`, by the order of `CarryPlan.components` (1-based).
- **Clusters** are made from the mates planned to be made again only (a named mate joins nothing), numbered from 0 in
  first-mate order, each listing its components in the order the mates first name them; a component no planned
  user–user mate joins is a cluster of its own, after them, in component order.
- **Anchor** (D20): any user lock read (planned or named), then the cluster's, then any user mate to an app body; with
  `new_frames` given (the worker), a body whose old or new frame is missing is passed over; without (the foresight),
  the anchor is still named and the old frame kept.
- **The not-open read's gates** in `carry_gates` for an `OLD_UNREAD` work: `FILE_VERSION_READ`, `DEPENDENCIES_READ`,
  `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` and the route, whichever are not set. `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS`
  depends on what is open at the press, which an `OldWork` does not hold: the worker's `unread` sentence says it.
- **The states route** is a gate (`STEP_CARRY_STATES`) when the work has two or more modes, a component is carried and
  `OldWork.states_route` is "" (it is not one when the read-only show read them).
- **`UserMate.entities` is read by `mate_info`, not by a new call**: `swcom.MateInfo` gains `entities` (per entity
  `(kind, feature)`, defaulted `()`), read inside `Session.mate_info` from `ReferenceType2` and the reference's name
  (a base plane by tree order among the part's first three `RefPlane` features). A separate `mate_definition` call in
  `_read_user_work` would have changed the calls every Update and W9a's old-assembly read make (W9a's tests pin
  them). The fake gives the kinds only with **`FakeSolidWorks.read_entity_kinds = True`** (default False, so every
  suite written before W9d, B's `test_workbook_carry` among them, reads as before); **B's round trip should set it**.
  `tests/test_swcom.py`'s `mate_info` test (owned by neither package) gains the kinds read; nothing else there changed.
- **`OldComponent` with `configurations` None, or a reference read with no hex**: named, as above.
- **The over-definition and the tie a same-error mate causes** are not counted against its cluster (§6: "carried as it
  was … not counted against its cluster"); the fake's rule reads a component in a mate in error over-defined, which
  otherwise fell back the cluster on the very mate §6 carries.
- **A read-only document the job opened and showed** is not counted in `OldWork.marked` (a show marks it; it is closed
  unsaved, so its mark is lost with it). Every other document's mark stops the carry.
- **`old_read`** on a carrying Build again…: `""` when read, `OLD_NOT_OPEN` when the old assembly was unread (closed,
  R.2 not met), the read's sentence when it raised; `old_user_work` is `OldWork.user_work()` when read.
- **The interference check that raises** no longer returns before the carry when a carry is given (the build's
  `interference_error` is set as before, and the carry then runs).

## Shape changes, continued

7. **`Session.component_states_in(names, configurations)`**, not `component_states` (§10): the fake already has a
   `component_states` dict (W9a's knob, Name2 -> state) that existing tests set, which would shadow a method of that
   name. Same call, other name.
8. **`Session.add_component_in(handle, path, at, configuration)`**, beside `add_component` unchanged, rather than a
   `configuration=""` argument on `add_component` (§10): every existing call and the fake's keep their signature.
9. **`Session.component_configurations(handle) -> (referenced, its document's active, its file's configurations)`**
   for §10's `referenced_configuration(handle)`, so the file's configurations come in the same read (shape change 3).
10. **`Session.save_flags()`, `file_version(path)`, `running_file_version()`, `dependencies(path)`, `delete_mate(handle)`,
    `swcom.MateDefinition`, `swcom.MateEntityRead`, `swcom.entity_kind`, `swcom.MATE_DEFINITION_VALUES`**: not named in
    §10; R.1, R.2 (as revised) and the fallback need them.
11. **`swbuild.read_old_work(sw, carry)`**, the read R as a function of its own (returns the `OldWork`, R.1's
    documents and their flags), and `STATES_SHOWN_READ_ONLY = "shown read-only"` (`OldWork.states_route`'s value
    for the read-only show).
12. **`remake_mate(handle, definition, targets, name, ratio)`**: the ratio passed beside the definition (§10's
    signature has none; the plan's swap is in `CarryMateItem.ratio`).

## Covered only on the fake (for the demonstration's author)

Every SolidWorks call W9d adds is written from the API help and S5's reads and has **never run**; the fake models what
the contract says SolidWorks does. In particular:
- `mate_info`'s entity kinds (`ReferenceType2`, the reference's `Name`, the base plane by tree order among the part's
  first three `RefPlane`s) and `mate_definition`'s `GetDefinition` fields by name.
- `entity_reference`: `GetPersistReference3` through `GetModelDoc2` / `FeatureByName` for a feature, and for a face or
  edge the route the finding names (if its text holds "GetCorrespondingEntity2" that route, else the entity straight
  to the part); `select_by_reference`'s `GetObjectByPersistReference3`, `GetCorresponding`, `Select4` with a mark-1
  data; whether a reference survives the read-only close (the fake's `reload_ok`).
- `component_configurations` (`ReferencedConfiguration`, `GetActiveConfiguration`, `GetConfigurationNames` on the
  component's document) and `add_component_in`'s `AddComponent5(path, 0, "", True, configuration, …)` read back.
- `component_states_in` by `GetConfigurationByName(…).GetComponentSuppressionState(Name2)` (§11.1's candidate 1).
- `open_read_only` (`OpenDoc6` with Silent | ReadOnly = 3), `close_unsaved` (`QuitDoc` by title), the documents left
  after it, and the read-only show per mode (`show_configuration` in the read-only document).
- `file_version` (`VersionHistory`'s last entry, its first number taken as the version) against
  `GetLatestSupportedFileVersion`, and `dependencies` (`GetDocumentDependencies2`, every second entry a path): the
  number formats are guesses until the probe's `state` (v) log shows them.
- `set_component_suppressed` (`SetSuppression2` 0 / 2 and `GetSuppression2` read back) on a component the job inserted.
- `remake_mate`: `AddMate5` with the old type, alignment and flip, `Distance`/`Angle` and the limits as its
  max/min arguments, the gear ratio swapped, a renamed mate keeping SolidWorks' name when the old one is taken; the
  read-back by `mate_definition`; `delete_mate` by `Select2` then `EditDelete`.
- The ledger's selection order is modelled in the fake as the contract states it; the tie is the fake's `locks` knob.
- Placement relative to a sliding anchor in another mode (contradiction 6): the fake solves no lock on a show, so the
  test anchors to a body that does not slide; M9 must show it on RangeSlv.
- The carried component's frame in every configuration after one put (the fake seeds it in every configuration's
  frames where the component had none).

## Fix round after W9D-REVIEW-A.md (and the contract at d3bb9e7)

**Must-fix, each with a test that failed before:**
- M1 faces and edges by r3: `Session.entity_references(component, items, candidates=, seconds=)`, one walk per
  component, the area / circle-radius / line prefilter, each candidate carried once, `IsSame` (swObjectSame 1)
  deciding, exactly one match, the cap (`swbuild.CARRY_WALK_CANDIDATES = 200`, `CARRY_WALK_SECONDS = 20.0`; the item
  and every later item of the component `capped`, its mate `WHY_TOO_LONG`), the resolve code `Ok` (0) required with
  its kind and `IsSame`, `coaxial` and `radius_mm` from the part entity's `CylinderParams` / `CircleParams` once
  `COAXIAL_FACE_READ` is True. The route is taken only when the finding equals `swcom.PERSIST_ROUTE_R3` exactly.
  `entity_reference` now reads features and planes only. Never read on a part made new, **except** a gear mate's
  face there, whose coaxial read alone can carry it (§4.3); its hex is dropped. Choice: "bore"/"axis" wording on a
  part made new is therefore said only for a gear mate's face (the other faces there are not walked: the cap's cost).
- M2 the tie only on `_mated_handles` gears, only against what was free before, after every fallback and in the
  post-check; a body on no train is its own; named by gear id.
- M3 the post-check reads each remade mate's code per mode where it is on (new error falls its cluster back there,
  same error kept), and the app's gears meant to turn free in every mode (else a stop naming them).
- M4 `find_component(..., suppressed_ok=True)` for R's reads (Session and fake); the frame judged before the
  configurations; a cluster's mates made in the first mode where its components are resolved (shown, then the first
  shown again), or named `WHY_UNREAD` ("a component it joins is suppressed in every mode…"); a selection that fails
  names the mate (`WHY_REFUSED`), never stops the carry.
- M5 a wrong sense made once more with the other Flip (`remake_mate(..., flip=)`); a gear mate whose ratio values or
  sense did not read is named `WHY_UNREAD`; a remade sense 0 is "sense" (differs).
- M6 a read-back with only its two entities swapped made once more reversed; the read-back compares against the old
  mate's `MateEntity` order whatever order was selected.
- M7 a lightweight or suppressed component's configurations read closed (`ISldWorks.GetConfigurationNames(path)`,
  **inferred, unmeasured**: M9 should log it), its active configuration "".

**Should-fix:** S1 `unsaved` on every remake, delete and fallback. S2 a fallback drops its deleted mates from
`remade` and `same_error`; a body is excused its over-definition and tie only when every mate of the cluster on it is
back in its old error. S3 a cluster falls back once (`fallen`). S4 the new assembly opened and its first mode shown
before C.1 (the fake's `begin_drops_document` knob). S5 the carry's interference read is caught. S6 `skipped` is what
is left (not the step in hand); C.8 runs in a `finally`. S7 a face with no reference read is `WHY_UNREAD` with R's
clause; an AddMate5 refusal is `WHY_REFUSED` (new, below); a mate made though AddMate5 answered None is deleted
again first. S8 the resolve's code, kind and `GetCorresponding` checked; another kind raises
`swcom.ReferenceKindError`, a stop. S9 `QuitDoc` by the title read at the open; a document still open after it says
so. S10 a plane with no document is `("unread", "")`. S11 a component suppressed in a mode is not pose-checked there;
a world-anchored one is checked against its placed frame. S12 a build that did not finish sets `carry.skipped`.

**The review's notes:** a `.SLDASM` dependency, a path not on disk or a history that does not read refuses R.2;
R uses the build's `exists`; the read-only document is judged from its flag straight after `OpenDoc6` (not counted
there), its own per-mode show on the None path not counted (not logged either: no log line exists in the worker);
`close_unsaved` by `GetTitle`; `set_component_suppressed` rebuilds (top-only) before its read-back.

**What `mate_info`'s extra reads cost every Update** (counted from the code; unmeasured on SolidWorks): per entity,
`ReferenceType2` (1 call). A reference feature adds `Reference` and `Name` (2). A datum plane adds `GetModelDoc2` and
a walk of the part's tree to its 3rd `RefPlane` (`FirstFeature`, then `GetNextFeature` and `GetTypeName2` per
feature: about 2 per feature before the 3rd plane, then `Name` of 3): on the app's parts some 10–25 calls. So a mate
on two planes costs about 50 more calls, a lock 2. Not material beside the Update's own reads, so they stay on every
Update (D5).

**Rulings taken:** `CarryResult.anchors` (per component, at the end); the trailing owner slot for `unmeasured` (whose
face, edge, origin, plane: the component's Name2 or the gear id) and for `gone` ("feature", name, gear id);
`exists` passed to the read; `CarryBody.bore_mm`; `OldEntity.radius_mm`, `OldEntity.capped`; no code-after field.

**New shape additions (B must word them):** `WHY_REFUSED = "refused"`, subjects `(SolidWorks' sentence,)`;
`WHY_TOO_LONG` subjects `(kind, owner, file, "candidates" or "seconds")`; `part new`'s 4th slot is now "bore",
"axis" or "". `swcom.ReferenceKindError`, `swcom.PERSIST_ROUTE_R3`, `swcom.OBJECT_SAME`, `swcom.PERSIST_REFERENCED_OK`.

**What B can now use:** `CarryResult.anchors` instead of re-deriving them; the owner slots; `CarryBody.bore_mm`
(fill it in `carry_for`); `build_gearbox` passes `exists` to the read, so the round trip need not patch
`os.path.isfile`; the fake's `read_entity_kinds` knob (still default False); B's tests that patch the face and edge
findings must use `swcom.PERSIST_ROUTE_R3` (any other string reads nothing now). With §8.1 set on 2026, the not-open
read and the states read now pass their gates on the fake's 2026: a test that wants them unset must patch them None.
The "moved 30 mm in N and L" of B's round trip: the fake solved no lock on a show, so a carried component locked to a
body that moves per mode stayed put there. The `moved` comparison is in the anchor's frame per mode (pinned by
`test_a_carried_component_off_its_pose_in_a_mode_is_said_moved_in_its_anchors_frame`); the fake now carries a lock's
follower with its anchor in every configuration when the lock is made, and seeds a put component in every
configuration. Not re-run in B's test by me (B's file); B should check it reads no `moved` now.

**What the fake now refuses that it allowed before:** finding a suppressed component without `suppressed_ok`;
selecting anything of a suppressed component in `remake_mate`; a face or edge reference under any route but r3's
exact string; `entity_reference` on a face or edge at all; a component's document (configurations, active one) for a
lightweight or suppressed component. It now models: r3's walk (filtered count, matches, resolve code, seconds per
candidate, the cap), a resolve to another kind, per-mode remake codes, a gear mate read the wrong way for the Flip
given, a read-back alignment otherwise, a drift per configuration, a gear held only after the save, the read-only
document marked by its own open, and the build bracket dropping the build document.

**Still only on the fake** (beyond the list above): r3 grouped, filtered and capped as written in `entity_references`
(the probe walked one entity at a time, unfiltered); `_walk_key`'s area and circle reads on the mate's entity;
`ISldWorks.GetConfigurationNames(path)`; `find_component` with `suppressed_ok` and `component_frame` of a suppressed
component; `remake_mate` with a Flip given; `set_component_suppressed`'s rebuild; whether selecting a suppressed
component's entity fails (inferred).

## After the re-check of the fix round (W9D-REVIEW-A.md, fd599f8)

- **N1**: the post-check judges a cluster's tie again only in a mode where its flags differ from the mode it was made
  in (K2's rule); one cluster's fallback never stops the carry (ruled): what still reads unable to turn after it is a
  fact, and the post-check's check of the app's gears in every mode stops the carry when nothing of the user's
  explains it. The fallback no longer raises.
- **N2**: in a mode where one of a cluster's components is suppressed, its mates' codes and its tie are not judged;
  what was read there goes into `CarryResult.facts` ("Lock1 in N, where Sprocket-1 is suppressed: on, code 46; not
  judged") and the log as `fact    …`.
- **N3, ruled**: while `CARRY_INSERTS_ON_<year>` is None, R makes no r3 walk and never opens a closed old assembly
  (`OLD_UNREAD`, its clause naming that finding; `carry_gates` gives `CARRY_INSERTS` for it). The open path reads as
  before.
- **M3's rest**: each app mate's code is read in every mode in C.5 (before any user mate is made) and again in the
  post-check; a new one falls back, by `FELL_NEW_ERROR` with subjects `(app mate, code, code before, mode)`, the first
  cluster on in that mode with a mate on the app's bodies and its components resolved, until it clears; none left, a
  stop.
- **Item 5**: the 2026 pin test compares every boolean with its log line (a flipped `COAXIAL_FACE_READ_ON_2026` or a
  None `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026` now fails it: checked by hand). The comment on a reference resolving
  to another kind says it stops the carry.
- **Item 6**: the prefilter's relative match is 1e-6 (comment in `swcom`); each walk is a line in `OldWork.walks`
  (logged `fact    walk Sprocket-1: face of 163: 2 after the prefilter (key ('area', …)), 1 matched; 2 carried,
  0.41 s, cap not reached`), from `Session.last_walk`.
- **Item 7**: `CarryResult.changed_files` (base names), the sentence in `stopped` unchanged.
- **Item 8**: a stop part way shows the first mode again (`finally`); a retry whose read-back or delete raises names
  the mate `WHY_DIFFERS` with subjects `("left", name in the new assembly)` and a fact; a `ComError` (a lost session
  above all) in a remake stops the carry, never "refused". The resolve's out code starts at -1
  (`swcom._out_unwritten`, `_by_ref_status`): a code SolidWorks does not write reads as not Ok. Whether pywin32 hands
  the written code back in the return tuple or the VARIANT is still for the demonstration to log.

**New fields, all at the end:** `CarryResult.facts`, `CarryResult.changed_files`, `OldWork.walks`. Nothing renamed.
**Changed for readers:** `WHY_DIFFERS` gains a 2nd slot only in the "left" case (`("left", name)`); a fallback no
longer stops the carry (its fact says what still reads wrong); `FELL_NEW_ERROR`'s first slot may now be an app mate's
name.

**For the demonstration's author to log, since none of it is measured as written** (the re-check, verbatim):
- the walk grouped per component (shared candidates carried once);
- the area and radius prefilter, part against assembly;
- seconds per candidate under the app, with the growth;
- `IEntity.GetType` on a resolved face or edge;
- whether the out code of `GetObjectByPersistReference3` is written. `_by_ref` reads an unwritten code as 0, which
  is Ok (`swcom.py:764`); the probe had the same blind spot;
- the cap's two numbers.

(On the fifth point: the app now reads an unwritten code as -1, not Ok; the probe's own blind spot stands.)

## Third round (W9D-DEMONSTRATION-REVIEW.md, 6f67791)

Each test below was checked to fail with its fix undone (by hand, on a backup).
1. The N1 test puts the innocent cluster (Lock0) first in the tree, as the reviewer's reproduction did.
2. `_app_mates_check` blames only a cluster with a mate on the bodies of the app mate in error (`mate_info` of that
   mate) or on their train. Test: `test_an_app_mate_in_error_blames_only_a_cluster_on_its_bodies` (Lock0 on LoDog first
   in the tree, not blamed for InDog's axis mate).
3. Ruled: R.2 refuses when a stored dependency path lies outside the old assembly's folder while a same-named file sits
   in that folder (SolidWorks loads the one beside the assembly first); the clause names base file names only. Tests:
   refused; own folder not refused; legitimately elsewhere with nothing beside not refused.
4. Ruled (D20): a component fixed in the old assembly is placed by its world frame with no app anchor; `anchors` says
   "" for it. Tests: pure (a fixed housing in a cluster locked to a turned Sun) and end to end.
5. `CarryResult.after_unread` (at the end): why C.8 could not read; no longer appended to `stopped`.
6. D10's fact: on the open path, the old assembly's lightweight instances of each carried part are read before and
   after their parts are opened (`use_open_document`, read only); those that went to resolved are in
   `CarryResult.resolved_in_old` (at the end) and a fact; never a stop, never set back. Inferred: the fake's
   `open_resolves_lightweight` models it. Not read on the not-open path (the old assembly is closed then).

New fields, at the end: `CarryResult.after_unread: str = ""`, `CarryResult.resolved_in_old: Tuple[str, ...] = ()`.

## Fourth round: the first M9 run on SolidWorks 2026 (50a8e54)

1. **The r3 walk read nothing.** True cause, confirmed: `call(body, member)` with the member name in a variable
   (`GetFaces` / `GetEdges`). Through late binding those come back as a bound method, uncalled (GOTCHAS §55), and
   `list()` of that raised; the probes' r3 used `raw()`, which calls it. Fix: `_read` (call when a method comes back)
   for every zero-argument member the W9d code reads: `GetFaces`, `GetEdges`, `GetSurface`, `GetCurve`, `GetArea`,
   `IsCircle`, `IsLine`, `IsCylinder`, `CircleParams`, `CylinderParams`, `GetType`, `GetDefinition`,
   `GetConfigurationNames`, `GetTypeName2`, `GetModelDoc2`, `GetSuppression2`, `GetSaveFlag`,
   `GetActiveConfiguration` (34 call sites changed file-wide; `_read` is a no-op for a property get). Test:
   `tests/test_swcom.py::test_the_r3_walk_calls_the_members_late_binding_hands_back_uncalled`, COM doubles whose
   members are methods, run through the real `Session.entity_references`; fails with the old `call`.
2. **The carry stopped after the states: "No component is kept as 'gear7'".** True cause: `Session.end_build`
   forgets every handle, so the build's handles are gone in the carry's bracket; C.1 found again only the bodies on
   record (`Carry.bodies`), and gear7 is the Aux gear new in this revision. Fix: C.1 finds again every component the
   build placed (`GearboxResult.components`, by Name2) before anything reads by handle. Fake: `strict_handles` (on in
   every carry test): `end_build` forgets the handles and `constrained_status` / `component_frame` refuse one not found
   or added since. Test: `test_a_gear_new_in_the_revision_is_found_again_before_its_tie_is_read` (fails on the old C.1).
3. **Python text in sentences.** Causes: `entity_reference(s)` formatted any exception into its clause; for
   UserAxisLight the lightweight component has no part document (`GetModelDoc2` None) and R read it anyway. Fixes: a
   fault of Gear Generator's never reaches a sentence (`_carry_said`: SolidWorks' own refusal as it came, else "a
   fault in Gear Generator, not in SolidWorks", the Python text kept as a log fact); a part not loaded says so.
   **Choice for UserAxisLight, for you to rule:** D10 carries a lightweight component resolved and names its mates
   `WHY_LIGHTWEIGHT` ("what it joins could not be read"); the contract is silent on reading such a mate's entity, so R
   now reads nothing of a lightweight component's entities (no reference, no walk) and `plan_carry` names the mate
   `WHY_LIGHTWEIGHT` before any unread check. Resolving the component in the old assembly to read it would change the
   user's document, which §0.3 forbids. Fake: `entity_reference` on a lightweight or suppressed component answers as
   the Session now does. Tests: `test_a_mate_on_a_lightweight_components_feature_is_named_lightweight_and_never_read`,
   `test_a_fault_of_ours_never_reaches_a_sentence_as_python_text`.

**Audit.** (a) Zero-argument members through `call`: the list in 1, all now `_read`. `GetTitle`, `GetPathName`,
`Name` stay `call` (property gets, read so in this run's log). (b) Reads by a build handle: C.1 (fixed); the
post-check's anchors and the mated gears (now found in C.1); carried components' handles are the carry's own
(`add_component` in its bracket); the app mate in `_app_mates_check` is found by its own new handle. (c) Exception
text formatted into a reason: `entity_reference`, `entity_references` (fixed), `stopped` and `after_unread` and the
read's failure (now `_carry_said`); `WHY_REFUSED` and the "left" fact take only `SolidWorksError` sentences.
(d) After the states, read again with this run's eyes: `remake_mate`'s selection by `_component_ref` and whole
`Select4` use handles C.1 now keeps; `select_by_reference` passes `bytes` as the probe did; `mate_definition` reads
through `_read`. Nothing else found that only the fake's kindness made pass; all of it is still unrun on SolidWorks.

**For B:** nothing in B's files must change for these; a sentence B builds from `stopped` may now end in "a fault in
Gear Generator, not in SolidWorks" instead of Python text.

## Fifth round (W9D-REVIEW-A.md eb66f22, W9D-DEMONSTRATION-REVIEW.md e2207d9)

- **M1**: `_read` calls a member handed back uncalled under `_guarded`, so a COM error there is a `ComError` (SolidWorks'
  sentence, a lost session marked, `_remake`'s `except ComError: raise` meets it). Pin:
  `tests/test_swcom.py::test_a_member_handed_back_uncalled_is_called_under_the_com_error_guard` (fails on the old).
- **M2**: `_set_flags` sets a mate's flag in every mode as recorded; in a mode where one of its components is
  suppressed, what SolidWorks reads back is a fact, never a stop. Pin:
  `test_a_mates_flag_read_otherwise_where_its_component_is_suppressed_is_a_fact_not_a_stop` (fails on the old).
- **M3**: `_judge` never excuses a gear's tie; the same-error excuse keeps only the code and a body's over-definition.
  Pin: the "same error" case of `test_a_new_error_or_an_over_definition_falls_back_and_the_same_error_is_carried`
  (Lock1 back in 46 ties G1: it now falls back). Rule written into W9D-INTERFACES §6's same-error paragraph.
- **S1**: a fault of ours reads "The carry stopped while …: a fault in Gear Generator, not in SolidWorks." and "The
  read of … stopped: …"; SolidWorks is the subject only of its own refusals.
- **S2**: a walk's faults are appended to its logged walk line; `entity_reference`'s fault text kept in
  `Session.reference_faults` (not yet copied to the log: **not done**).
- **S4**: `entity_references` on a component with no part document says "its part is not loaded in SolidWorks
  (lightweight or suppressed)".
- **Why-fields**: an entity SolidWorks gives no component for carries its why: "the assembly's own plane is not told
  while a component of it is lightweight" (UserAsm6) or "SolidWorks would not say what it is on"; a feature on a
  suppressed component carries the Session's "its part is not loaded in SolidWorks (lightweight or suppressed)"
  (UserAxis9). B gets them as `WHY_UNREAD`'s one slot, the clause.
- **Notes**: an empty Name2 is skipped in C.1. **Not done**: inserting each file's instances in their old order (not
  checked against cluster order and placement in this round's budget); S3's closer stand-ins (`GetModelDoc2` and
  `Extension` as attributes, a Session test with no part document, `strict_handles` in every handle-taking fake
  member, the two carry tests without it); the gear sense against real geometry: the W9d probes remade no gear mate,
  so nothing measured exists to model; left for the run.

### Fifth round, finished
- **S3.** The r3 stand-in has `GetModelDoc2` and `Extension` as plain attributes; only `GetFaces` and the face members
  come back as uncalled methods, so the old `call(body, member)` fails there, where SolidWorks failed (checked).
  `tests/test_swcom.py::test_with_no_part_document_both_reference_reads_say_the_part_is_not_loaded` pins S4's
  sentence for `entity_references` and `entity_reference`. `strict_handles` now refuses, as the Session's
  `_component` does, in every fake member that takes a component handle: `constrained_status`, `component_frame`,
  `place_component`, `fix_component`, `unfix_component`, `delete_component`, `component_configurations`,
  `set_component_suppressed`, `entity_references` (its component), `component_resolved`, `is_fixed`,
  `component_path`, a mate's targets in `remake_mate` and `select_by_reference`'s handle (`_resolve`). The two carry
  tests built without it now have it. No carry test failed with strictness on everywhere: no finding.
- **S2's remainder.** `Session.reference_faults` reaches the log's facts ("reference read fault: …") after R's mates,
  then is emptied. Pin: `test_a_fault_in_a_features_reference_read_reaches_the_logs_facts`.
- `probe/w9d_demonstration.py --self-check` at `a366938`: 0 failed (M2 and M3 change none of its expectations).

## Sixth round (W9D-REVIEW-A.md 2ad7ad8)

- **A1.** The fake reads a user mate's entity on a component suppressed in the mode showing as kind `unread`, as
  SolidWorks did (run 2, log 2 line 621). R then hands the cause out as structure. `OldEntity` gains, at the end,
  `cause: str = ""` and `cause_parts: Tuple[str, ...] = ()`, with constants
  `swbuild.CAUSE_SUPPRESSED = "suppressed"` (parts: the component's Name2, the old mode showing; "" with no modes)
  and `swbuild.CAUSE_BESIDE_LIGHTWEIGHT = "beside lightweight"` (parts: the lightweight component's Name2).
  `unread` keeps its clause. A mate named `WHY_UNREAD` carries subjects `(clause,)` as before, or
  `(clause, cause, *parts)` where the cause is known. Pins:
  `test_a_mate_on_a_component_suppressed_in_the_mode_showing_hands_its_cause_as_structure` and
  `test_the_assemblys_plane_beside_a_lightweight_component_hands_its_cause_as_structure`. An entity whose kind reads
  unread for no known cause says "SolidWorks would not say what kind of entity it is".
- **A2.** `test_a_same_error_mate_that_ties_no_gear_is_carried`: Lock2 (Chain-1 to a fixed Housing-1, 46 before and
  after) comes over in `same_error`, not fallen.
- The item-8 stop test now suppresses Sprocket-1 in N rather than in the mode showing: with the fake reading as
  SolidWorks does, a lock on a component suppressed in the mode showing is named unread and never remade.
- The demonstration script's self-check passes (0 failed). Its `expected_outcome` should now expect a mate on a
  component suppressed in the mode showing (Sprocket-10's) named `WHY_UNREAD` with subjects
  `(clause, "suppressed", "Sprocket-10", <mode showing>)`. I have not read whether its fake desk reads that entity's
  kind unread.

## Seventh round (W9D-REVIEW-A.md 0d45c9a)

- **N1.** `_read_back` takes a remade mate's entity named by the new assembly's root component as the assembly's own.
  The root is read from SolidWorks once in C.1 (`root_component(True)`; the new assembly holds no lightweight
  component, since carried ones go in resolved), never from a title. The fake's `assembly_entity` default is now
  `"root"`, as 2026 and 2024 measured; `"none"` only where a test asks. Pin:
  `test_a_mate_to_the_assemblys_own_plane_is_made_again_and_kept`, first mode and per mode; both cases fail without
  the fix. Changing the default broke one test: the lightweight test asserted no `root_component(True)` anywhere. The
  test was wrong (its rule is "never in the old assembly beside its lightweight component"), so it now checks R only.
- **The wider audit of the fake's defaults was not done this round**: only `assembly_entity` was changed. Still owed: go
  through every default standing for a measured `*_ON_2026` finding or a W9D-PROBES.md behaviour.
- **S5.** `test_a_carry_that_stops_in_a_later_mode_leaves_the_first_mode_showing` fails with the `finally`'s show
  removed.
- **S6.** When `ReferenceType2` answered a type the app does not take, the cause is
  `swbuild.CAUSE_TYPE_NOT_TAKEN = "type not taken"` with parts `(the number as read,)`, and the clause "it is on a kind
  of entity Gear Generator does not make mates on again". "SolidWorks would not say what kind…" now covers only a
  type not read. Pin: `test_an_entity_of_a_type_the_app_does_not_take_says_so_as_structure`.
