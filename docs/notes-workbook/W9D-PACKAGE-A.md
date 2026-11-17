# W9d package A (the worker): hand-back note

Package A of W9d, against `W9D-INTERFACES.md` as committed at `23ed8c5` (the re-check's R1, R2, S-a to S-g taken).
Written and tested against the fake (`tests/test_swbuild.FakeSolidWorks`) only; no SolidWorks or Excel was started.

## State

See the commits beginning "W9d shapes:", "W9d plan_carry:" and "W9d worker:" on branch `w9d`. What is done and what is
not is kept below as the work goes.

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
