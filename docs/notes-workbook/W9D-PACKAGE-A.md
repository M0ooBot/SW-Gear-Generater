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
- `log_lines()` gains no carry lines yet (§2.4's `ok      carried …`); B's sentences say the result.
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
