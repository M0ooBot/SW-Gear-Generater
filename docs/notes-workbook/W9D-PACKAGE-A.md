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
