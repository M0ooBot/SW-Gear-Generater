# Review of W9d package A (the worker)

*Independent, 2026-11-17, at `24aea8c` (package A's last commit). HEAD has since moved to `51e489a`, but only the probe
script and `W9D-PROBES-REVIEW.md` changed, so every line number below is the same at both. I started no SolidWorks or
Excel and changed no source, test or document.*

- *The suite, run once on the worktree (clean, HEAD `51e489a`):* 2 failed, 3824 passed, 10 skipped. The two failures
  are the known tkinter-only tests (`test_gears_clutch.py::test_the_strip_never_offers_them`, `test_ui_text.py::
  test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`). Neither is in a file of package A or B.
- *Scratch work:* clean extracts of `24aea8c` (`git archive`) in the scratchpad: seven mutations of `swbuild.py` run
  against `tests/test_swbuild_carry.py`, and three reproductions on the suite's fake. None is in the repo.
- *What I read:*
  - `W9D-INTERFACES.md` whole, its review, and `ISSUE-1-PLAN.md` §0.3, §2.5 and §5 "W9d";
  - `W9D-PACKAGE-A.md`; `W9D-PROBES.md`, both 2026 logs and `probe/w9d_probes.py`'s routes (r3, `last_saved`,
    `dependency_paths`, `state_close`, `faces_remake`); `W9D-PROBES-REVIEW.md` (committed after A's last commit);
  - the macro database's ledger on `AddMate5`, `IMate2` and `IGearMateFeatureData`;
  - the diff `5e783a6..24aea8c` over `swbuild.py`, `swcom.py`, `findings.py` and the four test files, and the code it
    calls (`find_component`, `begin_build`, `_component`, `_component_ref`, `_free_to_turn`, `_mated_handles`,
    `_carry_frame`, the planner's lock and gear mates).
- *What I wrote:* this file only.

**Verdict.**

- **The skeleton is right.** R reads before anything is made, in its own bracket. R.2's conditions are all checked
  before any open, by closed-file reads only. The read-only document is closed in a `finally`. C runs only after the
  new assembly saved, and nothing in it calls a save. The fake now fails a test that writes to, shows, saves or closes
  the old assembly or a user file. I found no path, error paths included, that writes to the old assembly or a user
  file, or saves anything after the first save.
- **The tests pin behaviour, not just the happy path.** Seven mutations of central rules each failed a test (below).
- **It is not yet fit for M9's script.** Seven must-fixes stand between it and the demonstration's central items:
  - the face and edge route is not r3 (M1);
  - a fixed Ring on Sun's train stops the carry after the tied cluster falls back, reproduced (M2);
  - the post-check reads no mate code per mode (M3);
  - a component suppressed in the mode showing goes wrong on SolidWorks in two places the fake hides (M4);
  - the gear mate has no second Flip (M5);
  - the "once reversed" retry is missing (M6);
  - a lightweight component is named instead of carried (M7).

  Each fix is local. With them in, I would expect a demonstration script to be writable against it.

---

## Must fix before the demonstration is written

**M1. `swcom.Session.entity_reference` reads a face or an edge by r1 or r2, never r3** (`swcom.py:3766-3794`).

- *What the code does:*
  - it takes r1 when the finding's text holds "GetCorrespondingEntity2";
  - otherwise it takes r2: the mate's assembly entity handed straight to the part's `GetPersistReference3`.
- *What SolidWorks does:* both are dead on 2026. r1 gives nothing; r2's reference resolves
  `swPersistReferencedObject_Invalid` (`w9d…-1.log`, `-2.log:89-90`). The route proposed for both findings is r3's
  string, which does not contain "GetCorrespondingEntity2".
- *The scenario (reasoned from the code and the logs):* set `PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2026` as proposed.
  1. R reads a 70- to 82-byte reference by r2.
  2. C's `select_by_reference` resolves it to nothing and raises "could not be found again".
  3. `_carry_cluster` (`swbuild.py:7974-7976`) names the mate `WHY_NOT_FOUND`.

  So every face and edge mate in M9 would be named *"…could not be found again in Sprocket.SLDPRT"*, which is not
  true.
- *The cost is not handled either: there is no walk at all.* `_read_old_mates` (`swbuild.py:7739-7741`) also asks for a
  reference on every face, edge or vertex of **any** app body, including parts made new, which `plan_carry` then names
  `WHY_PART_NEW` anyway. Each `entity_reference` call also reads the whole `mate_definition` again.
- *Fix* (the probes review's must-fix 1, which this implements):
  1. Write r3 as `probe/w9d_probes.py:route_r3` does it: `GetBodies2(0, True)` → `GetFaces` / `GetEdges`; per
     candidate, `IComponent2.GetCorresponding`, then `ISldWorks.IsSame` against the mate's entity; exactly one match
     counted. Then the part's `GetPersistReference3`, resolved by `GetObjectByPersistReference3` with its code
     `swPersistReferencedObject_Ok` required.
  2. Walk once per component for all of its entities that are still needed. Group them in `_read_old_mates` and hand
     the session a list, not one `(mate, index)` at a time.
  3. Prefilter by area (a circle's radius for an edge). Keep the count.
  4. Cap the walk by a count or a time budget. A cap that is reached names the entity `WHY_UNREAD` with the cap's
     clause and never stops the carry.
  5. Read only what can be carried: a USER component, or an app body that is `same_file`.
  6. Take `coaxial` from the same part entity (`CylinderParams`), once `COAXIAL_FACE_READ` is set. Today it is always
     None (see M5's note on the face variant).
  7. The fake should refuse a route string that is not r3's and model a cap that is reached.

**M2. A held gear or a carrier on the train stops the carry after a tied cluster falls back** (`swbuild.py:8127`,
`:8166`).

- *What the code does:*
  - `_trains_of` (`:7775`) joins every body that a gear or lock mate of the plan names. On RangeBox that includes the
    **fixed Ring** (`tests/workbook_fixtures.py:82`: Ring on "fixed"; "a gear mate may reach a held gear … never
    unfixed", `motion.py:929`).
  - `_carry_cluster` compares against `before`, so it does not fall back on the Ring. But `_fall_back`'s re-read,
    `still = [h for h in train if … != UNDER_DEFINED]`, has no `before`. Neither has the post-check's per-mode tie
    (`not_free`, `:8166`). The post-check's train also keeps carriers and the layout, which `_carry_cluster` filters
    out.
- *Reproduced on the fake:* in the tied-cluster test, I held G1 fixed (`constrained["gear1-1"]` fully defined, as the
  Ring is). The cluster falls back as it should, and then the carry stops:
  *"After the fallback, gear1 still reads unable to turn, so the carry stopped"*. Every later cluster and the
  post-check are skipped.
- *Why it matters:* M9's tied cluster (Sprocket-8 locked to Sun and to Housing-1) is on exactly this train. The
  sentence also names a handle ("gear1"), not a gear.
- *Fix:* judge only the gears meant to turn (`_mated_handles(assembly)`, the set the build's own check uses), and only
  against what was free before, in all three places. Name each gear by its id. Add a test with a fixed gear on the
  train.

**M3. The post-check reads no mate's code in any mode and runs no app check per mode** (`_carry_post_check`,
`:8134-8175`).

- *What the contract says:* §3 C.7 and §6 ask, per mode:
  - each remade mate's code and flag. A code it did not have before, in a mode where it is on, is `FELL_NEW_ERROR`
    there (§6's *"which it did not in H"*);
  - the build's own per-mode check. A failure no cluster explains stops the carry.
- *What the code does:* it reads poses, the per-mode ties and the clashes. A mate that errors only in L is carried and
  reported as made, and the app's own check after the carry never runs.
- *Why no test catches it:* the fake cannot show this. `remake_codes` is one code per mate, not one per mode.
- *Fix:*
  - in each show, `mate_states()` over the remade mates that are on in that mode, with the same-error rule;
  - `_free_to_turn(_mated_handles(assembly))` in each show as well;
  - a fallback there, with the mode in its subjects;
  - in the fake, per-mode remake codes, and a test.

**M4. A component suppressed in the mode showing: two places where SolidWorks will differ from the fake.**

- *(a) In R its frame is never read, and it is named with the wrong reason.*
  - `Session.find_component` refuses a suppressed component (`swcom.py:3570-3573`). The fake's `find_component`
    (`tests/test_swbuild.py:872`) does not.
  - So on SolidWorks `frame` is always None for it. `component_configurations` then raises (no handle was kept), so
    `configurations` is None.
  - `_component_named` checks the configurations (`swbuild.py:7240`) before the frame (`:7250`). The component is
    therefore named `WHY_CONFIGURATION`, with an empty referenced configuration: *"Sprocket-10 uses its configuration ,
    not … which its file opens in"*.
  - §5.3 asks for the frame to be read (unmeasured), with `WHY_NO_FRAME` only when it will not read.
  - *Fix:*
    - read the frame through a find that does not refuse a suppressed component (a keyword beside `lightweight_ok`),
      or else name it `WHY_NO_FRAME`;
    - test the frame before the configurations;
    - make the fake's `find_component` refuse as the Session does.
- *(b) In C a mate on a component suppressed in the new first mode stops the whole carry.*
  - C.5 sets the states before C.6 makes the mates, in the first mode. That covers Sprocket-10 suppressed in H, and,
    under D2, every component suppressed in the mode showing.
  - Selecting an entity of a suppressed component will fail on SolidWorks. That is inferred (W9c's probes note "a
    suppressed component has no document"), and the fake's `remake_mate` does not care.
  - `_select_target`'s error does not contain "could not be found again", so `_carry_cluster` re-raises it
    (`:7974-7976`) and the carry stops part way.
  - *Fix:* make a cluster's mates in a mode where its components are resolved, then set the flags per mode as now, or
    name the mate. A selection failure should never stop the carry.

**M5. A gear mate is never made again with the other Flip, and an unread ratio or sense is guessed.**

- *The Flip:* `remake_mate` passes `IMate2.Flipped` as `AddMate5`'s `Flip` (`swcom.py:3923`).
  - The ledger (`IGearMateFeatureData`, `AddMate5(10, …)`) says the right `Flip` varies with the geometry, and the
    app's own remake reads the mate back and remakes it with the other `Flip`.
  - Here a wrong sense is deleted and named `WHY_DIFFERS` ("sense"), with no second try (`swbuild.py:8035-8038`).
    §10 asks for one.
  - M9's gear-mate item depends on this.
- *The guesses:*
  - with no `GearRatio*` values read, the ratio is (1, 1) (`:7499`), and the read-back skips the ratio (`if key in
    values`);
  - with the old sense unread (`item.sense` 0) or the new one unread (`sense` 0), the sense is not compared;
  - so a gear mate can be remade 1 : 1, or the wrong way, and reported as carried.
- *Fix:* remake once with `not flipped` when the sense reads wrong. Name a gear mate whose ratio values or sense did
  not read (`WHY_UNREAD`). Treat a remade sense of 0 as "differs".
- *The fake:* every entity's `EntityParams` is `(0, 0, 0, 0, 0, 1)`, and a gear mate reads back the `Flip` it was
  given. So no test can show a wrong sense.

**M6. The "once reversed" retry of §10 is not written.**

- *What the code does:* every entity pair the ledger does not cover is selected in `MateEntity` order. That covers
  plane–plane coincident, distance and angle, face–face coincident, parallel and the limits. A read-back with the two
  entities the other way is deleted and named "entities".
- *Neither order is measured:* `same_definition` in the W9c and W9d probes compares type, alignment, flip and values,
  never the order of the entities. So M9's *"every remade mate's definition equal"* rests on a guess.
- *Fix:* when the read-back differs only by the two entities swapped, delete the mate and make it once more with the
  targets reversed, then judge it.

**M7. A lightweight component is named `WHY_CONFIGURATION`, not carried resolved (D10).**

- *What the code does:* `component_configurations` reads the file's configurations through `GetModelDoc2`
  (`swcom.py:3796-3810`). The project's own notes (`W9C-PROBES.md:75`) say GetModelDoc2 gives none for a suppressed
  or lightweight component.
- *The scenario:* R's `except` leaves `configurations` None (`swbuild.py:7634-7637`). `plan_carry` names the component
  `WHY_CONFIGURATION`, so M9's Sprocket-9 is not carried. The fake answers for every component.
- *Hedge:* the lightweight half is the API help's reading as the notes give it, not measured.
- *Fix:*
  - read a file's configuration names closed (`ISldWorks.GetConfigurationNames(path)`, a documented closed-file read;
    unmeasured, so let M9 log it first, or gate it);
  - otherwise name such a component with a sentence that is true;
  - have the fake answer None for a lightweight or suppressed component.

## Should fix

**S1. `CarryResult.unsaved` stays False when only mates were written.**

- *Where:* it is set only on an insert (`swbuild.py:7860`).
- *Reproduced:* a user mate between two app gears' base planes (cluster −1), with no component carried. The mate is
  remade and `unsaved` is False.
- *Why it matters:* B then writes no `unsaved_at`, and the footer never says to save.
- *Fix:* set `unsaved` on every remake, delete and fallback too.

**S2. `same_error` keeps a mate that the fallback deleted.**

- *Reproduced:* Lock4 (Sprocket-2 to G1) in error 46 before and after, in the cluster that ties G4. The fallback deletes
  Lock3 and Lock4, and `same_error` still says `[("Lock4", 46)]`. B would say *"…is in RangeBox_r2 too, as it was"*,
  which is false.
- *A second fault, reasoned:* the same-error excuse is kept by **handle** (`:8077-8078`). A tie or an over-definition
  caused by another mate of the cluster on the same gear is excused too.
- *Fix:*
  - drop the deleted mates from `same_error` in `_fall_back`;
  - excuse a status only when that mate is the only one of the cluster on that body.

**S3. The post-check's per-mode fallback can run twice for one cluster** (`:8160-8169`).

- *What happens:* a cluster whose flags differ from the first mode in N and in L, and that ties in both, falls back in
  N. In L it is still in `per_mode`, so `_fall_back` runs again. The second `delete_mate` of a handle already popped
  raises, and the carry stops.
- *Fix:* take the cluster out of `per_mode` once it has fallen back.
- *Test:* §14.1 owes "a cluster tying in L only". Today it has no test.

**S4. C.1 reads the new frames before the new assembly is the build document.**

- *What the code does:* `_carry_in_job` calls `begin_build`, which sets `_build_doc` to None (`swcom.py:1195`). So C.1's
  `find_component` and `component_frame` (`swbuild.py:7837`) read from **ActiveDoc**, and `open_document(asm)` comes
  only after them (`:7848`).
- *The fake hides it:* its `begin_build` leaves `current` alone.
- *The risk (reasoned):* the old and new assemblies share every app component's Name2 ("gear1-1"). Frames read from
  the wrong document would place every component wrongly, and nothing would say so.
- *Also:* nothing shows the first mode before C.1 or C.4, which §3 C.4 asks for. That matters when the interference
  check raised part way (S5).
- *Fix:* `open_document(asm)` and a show of the first mode before C.1.

**S5. The interference change is right, but the carry's own interference read is unguarded.**

- *The change is right:* a clash check that cannot run is a CHECK, and the assembly is saved, so §3 says C runs.
- *The fault:* `_carry_post_check` calls `sw.interferences()` bare (`:8171`). When the build's check raised, this one
  likely raises too. The carry then stops at the very end with *"SolidWorks stopped the carry while checking every
  mode…"*, after everything was made.
- *Fix:* catch it as `_modes_interference` does (`:2480-2483`).

**S6. A stop says the wrong thing was skipped, and C.8 never runs after one.**

- *The wrong skip:* `cr.skipped = done[-1]` (`:7824`) is the step that was in progress or just finished. After the
  fallback's stop in M2's reproduction it read *"making Lock3 again"*, but Lock3 had been made. B would say *"it did
  not get to making Lock3 again"*.
- *C.8 skipped:* `_carry_after` (the user documents' flags and the files' times, §0.3's check) sits in the same `try`
  (`:7821`), so it is skipped on every stop.
- *Fix:* build `skipped` from what is left (the remaining clusters, the post-check). Run `_carry_after` in a guarded
  `finally`.

**S7. Three items are named with a reason that is not true.**

- *A face whose reference would not read in R, its finding set:*
  - `unread` stays `""` (`:7745` sets it for features and planes only);
  - `plan_carry` plans `ref:h:face:`;
  - the worker names it `WHY_NOT_FOUND`, *"could not be found again"*.

  It should be `WHY_UNREAD` with R's own clause.
- *An `AddMate5` refusal (`MateRefused`):* it is named `WHY_NOT_FOUND`, with subjects `("entity", "", "")` when no
  target is tier 1 (`:7970-7972`, `:8000-8007`).
- *`remake_mate`'s raise:* it raises `MateRefused` when `AddMate5` returned None even if one mate was made
  (`swcom.py:3930`). That leaves an unrecorded mate in the new assembly. Delete it first.
- *Fix:* for a refusal, a reason of its own is a shape change. Ask through the coordinator.

**S8. `select_by_reference` checks neither the resolve's code, nor the kind, nor `GetCorresponding`'s None**
(`swcom.py:3952-3969`).

- *The contract:* §4.1 makes a resolve to another kind §0.3's STOP, and §14.1 owes its test. Neither exists.
- *The fake:* its `_resolve` never returns another kind either.
- *Fix:*
  - require `swPersistReferencedObject_Ok`;
  - compare `IEntity.GetType()` (or a feature's type) with the kind;
  - raise a distinct error that `_carry_cluster` turns into a `_CarryStop`.

**S9. `close_unsaved` passes `QuitDoc` the path's base name; the probe passed the document's `GetTitle`.**

- *The measurement:* the probe passed `GetTitle` and waited 3 s (`state_close`).
- *The risk:* a title can lack its extension under Windows' setting.
  - On a mismatch the document stays open. R.7 reads it as left, so nothing is carried, but the old assembly stays
    open read-only in the user's session.
  - If `close_unsaved` raises, R's error (`build_gearbox`'s `except`) does not say that the document is still open.
- *Fix:* keep the title read at the open and pass it. On a failure, list the documents and say what is still open.

**S10. `_entity_kind_read` classifies a base plane by its English name when the component has no document**
(`swcom.py:2624-2631`).

- *What happens:* on a lightweight component `GetModelDoc2` is None, so `planes` is `[]`. "Front Plane" comes back as
  `("feature", "Front Plane")`. §2.2 says never by its English name.
- *Where it lands:* in every Update's inventory (D5) and in B's foresight.
- *Fix:* with no document, `("unread", "")`.

**S11. The post-check's pose read can stop the carry, and some components are never checked.**

- *The stop:* the post-check reads the frame of a carried component even in a mode where it is suppressed. Whether
  `Transform2` answers there is unmeasured, and `component_frame` raises on None. Skip a component suppressed in that
  mode.
- *Never checked:* a world-anchored component is never checked for `moved` (§6 says each carried component). That is
  minor.

**S12. A build that failed leaves a `CarryResult` that says nothing** (`swbuild.py:3605-3619`).

- *What happens:* the carry is not run, so `named`, `stopped` and `skipped` are all empty.
- *Fix:* set `skipped` ("carrying your work, because the build did not finish"), as `_carry` does for an unsaved
  assembly (`:7813-7815`).

## Notes

- `_set_flags` judges a mate's flag even in a mode where one of its components is suppressed, which §3 C.6.1 says to
  leave. The probes review found that a mate's own flag reads as set there (`IsSuppressed2`, `-1.log:113`), so the
  read-back should agree. I leave it.
- `_fall_back` reads the train again only after a tie. §6 says after every fallback.
- A gear new in the revision is not in `Carry.bodies`, so it is never in a tie read (`gear_of` filters it out).
- `mate_info` now makes more COM reads on **every** Update's inventory, not just a carry's. Per feature entity it reads
  `ReferenceType2`, `Reference.Name`, `GetModelDoc2` and a walk of the part's feature tree. They are reads, unmeasured
  as a set, and the fake's call log cannot show them.
- The probes review's contract edits that touch A's code are not in it yet:
  - a `.SLDASM` dependency refuses the not-open read;
  - the read-only document is judged from its flag straight after the open. A excludes it from `marked` altogether,
    which is laxer by one case;
  - "bore" by radius.

## The fake: where it is kinder than SolidWorks as measured

1. `find_component` answers a suppressed component, where the Session refuses it (M4a).
2. `component_configurations` answers for a lightweight or suppressed component, where the Session's `GetModelDoc2` is
   None (M7).
3. `begin_build` keeps the current document, where the Session's falls back to ActiveDoc (S4).
4. `remake_mate` selects on a suppressed component (M4b).
5. `entity_reference` gives a reference under any route string, and `_resolve` never meets another kind, an Invalid
   code or the walk's cost. The Session's r1/r2 read nothing usable (M1, S8).
6. Every entity's `EntityParams` is the same, and a gear mate reads back the `Flip` it was given, so a wrong sense
   cannot appear (M5).
7. Mate codes after a remake are one per mate, not per mode (M3).
8. No test train holds a fixed gear during the carry, though the fake models fixed as fully defined (M2).
9. `_entity_kind` is never unread for a lightweight component (S10).
10. `close_unsaved` closes by path, where the Session goes by base name and the probe went by title (S9).
11. The read-only open loads no part documents. On SolidWorks it loads every part (all unmarked, `-1.log:126`), and R.6
    reads their flags. That is harmless as measured.

What it does fail on, correctly:
- a write while a protected document is current;
- a show of the old assembly when the job did not open it read-only;
- a save after the new assembly's first save;
- a save of a protected path;
- `close_unsaved` of a document the job did not open;
- a read-only open of a document already open.

## `swcom`'s new members against the measurements

| Member | Verdict |
|---|---|
| `save_flags` | Matches (the probes' `GetSaveFlag` over the document walk). |
| `component_states_in` | Matches candidate 1: `GetConfigurationByName(…).GetComponentSuppressionState(Name2)`, clean and right on 2026, unsaved changes included (`-1.log:115-120`). |
| `open_read_only` | Matches: `OpenDoc6(path, 2, Silent \| ReadOnly)`. Warning 32 is not read, which is fine. |
| `file_version` / `running_file_version` | Matches the measured layout: `['17000[2024/282]', '19000[2025/260]']`, whose first number of the last entry is 19000, against 19000 (`-1.log:122`). A single `\|`-joined string, which the probe also handles, would be split into characters and refuse (safe; watch it on 2024). |
| `dependencies` | Matches `GetDocumentDependencies2(path, False, False, False)` and the probe's `dependency_paths` (odd entries). |
| `mate_definition` | Matches S5 (a)'s reads; the wrapper itself has not run. |
| `entity_reference`, features and planes | Matches S5 (b) (`GetModelDoc2`, `FeatureByName`, the part's `GetPersistReference3`). |
| `entity_reference`, faces and edges | **Wrong**: r1 or r2 by the finding's text; must be r3 with its bounds (M1). `coaxial` is never read. |
| `select_by_reference` | Matches W9c s5 (c) and W9d faces (c) (`GetObjectByPersistReference3`, `GetCorresponding`, `Select4(append, data)`). Missing: the Ok code, the kind check and the None check (S8). |
| `delete_mate` | Matches `MATE_DELETE_ROUTE`. |
| `close_unsaved` | Plausible, unmeasured as written: `QuitDoc` by base name where the probe used `GetTitle` (S9). |
| `component_configurations` | Plausible, unmeasured. `ReferencedConfiguration` was read only as a fact; fails on lightweight or suppressed (M7). |
| `add_component_in` | Plausible, unmeasured (`AddComponent5(path, 0, "", True, configuration, …)`; M9 measures it). |
| `set_component_suppressed` | Plausible: `SetSuppression2(0 / 2)` as the probes call it, but read back with no rebuild, where the probes rebuilt. |
| `remake_mate` | Plausible for axes, planes and locks (S5 (c)); unmeasured for limits, concentric, parallel and gear. For a gear mate the `Flip` passed has no measured basis (M5). |
| `_entity_kind_read` (inside `mate_info`) | `ReferenceType2` and `Reference.Name` match S5. The base plane by tree order is unmeasured, and wrong with no document (S10). |

## The tests

**Seven mutations, each caught** (`tests/test_swbuild_carry.py` on a scratch extract):

| Mutation | Failed |
|---|---|
| The fallback deletes user–user mates too | the tied-cluster test |
| R.2 drops the dependencies' versions | "a part of the user's saved on 2024" |
| R.2 drops "nothing else is open" | "another document open" |
| Placement ignores the anchor (`frame = c.frame`) | both 37° placement tests |
| The tie read never ties | the tied-cluster test |
| The states shown in an old assembly that is open | the D2 case (the fake's show guard) |
| A read's mark does not stop the carry | the read-that-marks test |

**§14.1's list against what exists:**

| Item | Where | Verdict |
|---|---|---|
| Inserted floating, states per mode, a new mode takes the first | end to end | Done. "Fixed as it was" is not asserted on its own; cheap to add. |
| Configuration carried in it and read back otherwise | end to end | Done. Gate None is in `plan_carry` only, which is enough. |
| Sub-assembly | `plan_carry` only | **Caveat**, if M9 does not patch `CARRY_INSERTS_A_SUBASSEMBLY`. Today a sub-assembly would go in by `open_document` + `add_component`, not the measured read-only insert. Do not patch it without a test. |
| Virtual, no file, kind not carried, assembly feature, origin, gone, tier 2 by name, cluster −1 | `plan_carry` only | Acceptable: pure decisions, and the worker passes their names through unchanged. |
| Pattern instance | nowhere | Acceptable caveat (`PATTERN_INSTANCE_READ` None; it comes over as its own). |
| A resolve to another kind stops | nowhere (not written) | Should be done with S8. |
| A cluster tying in one mode only | nowhere | **Before the demonstration** (S3's bug lives there). |
| A clash naming a carried component | nowhere | Acceptable caveat once S5 is in; a cheap test is easy. |
| `moved` | nowhere | Should have one (a component put elsewhere in L in the fake). |
| §10's "once reversed" | not written | **Must** (M6). |
| The gear mate's other Flip | not written | **Must** (M5). |
| `IsVirtual`, `IsPatternInstance` | not written | Acceptable (findings None, `^` rule). |
| `coaxial` never read by the Session | not written | Comes with M1. The face rule's None case is safe meanwhile: `WHY_PART_NEW`. |
| A fixed gear on the train | nowhere | **Must** (M2). |
| Mate codes per mode in the post-check | nowhere | **Must** (M3). |

## The shape changes and deviations

All acceptable as additions.

- `STAGE_CARRY` is not in `STAGES`. That is fine, since `progress_text` falls back.
- `OldComponent.configurations` None from the record names every component `WHY_CONFIGURATION` in B's foresight. B
  has worded that as *may* (`W9D-PACKAGE-B.md` item 4), so nothing B relies on broke silently. On SolidWorks, though,
  None also comes from M7's lightweight read, which is not what the field meant.
- The fake's `read_entity_kinds` defaults to False, and `tests/test_workbook_carry.py` never sets it. So B's round trip
  never carries an inventory with entity kinds. Tell B; it is one line.
- The same-error excuse "by its over-definition or tie": the intent is right, the grain is not (S2).
- The read-only document left out of `marked`: right as measured (flag True straight after the open, NeedsRegen).
  Bring it to the probes review's rule.
- `component_states_in` and `add_component_in` instead of §10's names: fine.
- The carry still runs when the interference check raised: right by §3, with S4 and S5.

---

## Re-check of the fix round

*Independent, 2026-11-17, at `6441e34`. Package A's commits are `98ed62e` (the code), `e5c1978` (the tests),
`013c14c` (the 2026 findings) and `0c0e5be` (the note). The contract was read at `d3bb9e7`: §3 R.2 and R.6, §4.1,
§8.1, §10 and §17.1. As before, I started no SolidWorks or Excel and changed nothing but this file. Package B's
uncommitted edits (`gearbox.py`, `test_workbook_carry.py`, the UI-DESIGN and its note) are left alone; every run
below that matters is on a clean `git archive HEAD` in the scratchpad.*

- *The suite at HEAD:* 2 failed, 3859 passed, 10 skipped.
  - The same counts hold on a clean extract of HEAD and on the worktree with B's uncommitted edits in it.
  - The two failures are the known tkinter-only tests (`test_gears_clutch.py::test_the_strip_never_offers_them`,
    `test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`).
  - None fails in B's files or in A's.

**Verdict.**

- **Every must-fix and should-fix is in.** I undid each must-fix by hand in a scratch copy of HEAD, and each one
  failed its own new test (below). My three reproductions from the first round now pass.
- **The r3 code as written matches the probe's route call for call.** I ran it over COM doubles. It finds the one
  match, reads the coaxial read and the radius, carries each shared candidate once, and caps.
- **Three new faults should be fixed** (N1–N3), one of them reproduced. None stands in the demonstration's way as
  planned: M9 has no tie that happens in one mode only, and N2 can be logged in its run.
- **One gap in the findings test:** a boolean 2026 value can change and the whole suite still passes.
- **Package A is fit for M9's script to be written and run against.**

### Each review item at HEAD

| Item | At HEAD | Undone in scratch, its test fails |
|---|---|---|
| M1 r3 | **Fixed.** `Session.entity_references` (`swcom.py:3887`); R groups the face and edge items per component (`swbuild.py:7807`). | yes, all six `test_faces_by_r3_…` cases |
| M2 held gear | **Fixed.** Only `_mated_handles` gears, and only against what was free before, everywhere. A body on no train is its own. | yes, `test_a_gear_not_free_before_…`; my first-round reproduction passes |
| M3 per-mode codes | **Partly.** Each remade mate's code in every mode where it is on, and the app's gears free in every mode. The app's own mates' codes per mode (the rest of the build's per-mode check) are still not read. | yes, `test_a_remade_mate_in_error_in_one_mode_only_…` |
| M4 suppressed | **Fixed.** (a) `find_component(suppressed_ok=True)` for R's reads, and the frame judged before the configurations. (b) The mates made in the first mode where the cluster's components are resolved, else named; a failed selection names the mate. | yes, each half alone fails `test_a_component_suppressed_in_the_mode_showing_…` |
| M5 Flip | **Fixed.** The other Flip once; the first, wrong mate is deleted before the retry. An unread ratio or sense is named. | yes, two tests |
| M6 reversed | **Fixed.** The read-back compares against the old `MateEntity` order whatever order was selected. | yes, `test_a_remade_mate_read_back_with_its_entities_swapped_…` |
| M7 lightweight | **Fixed**, see 4 below. | yes, three tests, when the fake's closed read is made to fail |
| S1 `unsaved` after mates alone | Fixed; my reproduction passes. | |
| S2 `same_error` after a fallback | Fixed; my reproduction passes. | |
| S3 a cluster falling back twice | Fixed (`c.fallen`). | |
| S4 C.1's reads | Fixed: the new assembly is opened and its first mode shown before C.1. | |
| S5 the carry's own clash check | Fixed: caught. | |
| S6 `skipped`, C.8 | Fixed: `skipped` comes from what is left, and C.8 runs in a `finally`. | |
| S7 untrue reasons | Fixed. `WHY_UNREAD` with R's own clause; `WHY_REFUSED`; a stray mate deleted. | |
| S8 resolve checks | Fixed: the resolve's code, the kind (`ReferenceKindError`, a stop) and `GetCorresponding`'s None. | |
| S9 `QuitDoc` | Fixed: by the title read at the open, with a still-open check after it. | |
| S10 a plane with no document | Fixed: unread. | |
| S11 a suppressed pose | Fixed: no pose read where the component is suppressed; a world-anchored component is checked. | |
| S12 a build that did not finish | Fixed: `skipped` is set. | |

*Notes on the fixes:*

- **S2's stricter excuse is conservative.** A mate back in its old error excuses only bodies that no other mate of its
  cluster touches. So a same-error mate that shares a component with another mate of its cluster now falls that
  cluster back as over-defined. My first-round reproduction now reads exactly that. I accept it.
- **A gear mate between perpendicular axes is now always named "unread".** `gear_sense` gives 0 when the two directions
  are perpendicular. The ledger's rule for axes that are not parallel is `Reverse` alone. This is rare, and it is named
  rather than guessed.
- **`_remake` names any `SolidWorksError` as `WHY_REFUSED` and goes on** (`swbuild.py:8156`). That includes an RPC
  failure, because `call` turns it into `ComError`. If SolidWorks dies part way, each remaining mate is named
  "refused" until a call outside `_remake` stops the carry. That is a note: the stop comes, but the earlier names
  overstate.

### r3 as written, against `probe/w9d_probes.py:route_r3` and `-2.log`

**The calls and their arguments match the probe.**
- `GetBodies2(0, True)`, then `GetFaces` / `GetEdges`.
- `component.GetCorresponding(candidate)`.
- `app.IsSame(carried, mate entity)`, in the probe's order, against `swObjectSame` 1 (the JSON's `same_value`).
- The part's `GetPersistReference3(part entity)` as bytes, and `GetObjectByPersistReference3(bytes, out long)`, with
  a tuple or the out code read as the probe did. The code must be 0, `swPersistReferencedObject_Ok`; all six read 0
  in the JSON.
- The round trip `IsSame(got, part entity)`.
- `CylinderParams` with the probe's coaxial test, the same 1e-9 tolerances (`AXIS_TOL`).

**What r3 adds that the probe did not do:**
- a kind check by `IEntity.GetType` (only edge, face or vertex can refuse, so a feature or an unread type passes);
- for an edge, the radius read from `CircleParams[6]`.

**Run on COM doubles** (scratch, `Session.entity_references` itself, not the fake):
- Two face items on one component, sharing 10 look-alike candidates by area: each candidate was carried once (10
  `GetCorresponding` calls for both). The bore came back coaxial with radius 5 mm, the plane not coaxial.
- 250 faces of one area: capped "candidates" before any `GetCorresponding`.
- No test in the suite runs this code: the fake replaces it with a model of its own. That is the place where a
  slip would show only on SolidWorks.

**The prefilter.**
- *It can lose the true match, never pick a wrong one.* `IsSame` still decides. A lost match comes out as "0 matched",
  which is `WHY_UNREAD`.
- *Faces.* The key is the face's `GetArea` read in the part against the mate's assembly-context `GetArea`, relative
  1e-9, both in m². Shown on doubles: an assembly area off by 2e-9 relative loses the match.
  - The contract's ground for 1e-9 is that "every entity of both runs read equal pairs". Those pairs were the mate's
    entity against the **carried-back** entity: both in the assembly (JSON `area`).
  - A part face against its assembly correspondent was never compared. It is plausible, but unmeasured until the
    2024 run or the short 2026 rerun (`51e489a`'s growth section checks that the filtered walk finds the same match).
- *Edges.* A circle is matched by its radius. A line is matched against lines. Any other curve, or a key that does not
  read, keeps every candidate. A spline edge on a 482-edge part is therefore capped "candidates" (`WHY_TOO_LONG`) at
  once. Safe.
- *The cost.* Every item recomputes every candidate's key (`swcom.py:3925`): items × candidates part-level reads,
  never cached. A filter pass cannot be interrupted, and the 20 s clock is read only before and inside the walk. That
  is a note while the part-level reads stay cheap. Cache the keys per component when convenient.

**"Exactly one" is counted inside the filtered set.** That is enough, since `IsSame` decides.

**The cap matches §10.** It counts fresh candidates past 200 or 20 s per component, then caps that item and every later
one of the component, and never stops the carry.

**A made-new part is walked only for a gear mate's face.** Its hex is dropped; only the coaxial read and the radius
are kept. This is right: it is the only read on a made-new part that can change an outcome (§4.3). The cost is that
"on its axis" and "bore" are said only for gear mates there; any other face of a made-new part is said as "a face
of Sun". That is never wrong.

**For the demonstration's author to log, since none of it is measured as written:**
- the walk grouped per component (shared candidates carried once);
- the area and radius prefilter, part against assembly;
- seconds per candidate under the app, with the growth;
- `IEntity.GetType` on a resolved face or edge;
- whether the out code of `GetObjectByPersistReference3` is written. `_by_ref` reads an unwritten code as 0, which
  is Ok (`swcom.py:764`); the probe had the same blind spot;
- the cap's two numbers.

### The 2026 findings (`013c14c`)

- **The values match §8.1 and the logs' proposals.** The route strings are byte for byte the proposed ones, and
  `PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2026 == swcom.PERSIST_ROUTE_R3` is asserted.
- **The comments carry §8.1's caveats with their log lines.**
- **One contradiction, the contract's own:** `findings.py:2137` (from §8.1's row) says *"another kind, is
  WHY_NOT_FOUND"*. §4.1 makes it §0.3's STOP, and the code stops (`ReferenceKindError`). Fix the comment and §8.1
  to §4.1.
- **Nothing that should stay None is set.**
  - Every `_ON_2024` is None.
  - On 2026, `REFERENCED_CONFIGURATION_READ`, `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`, `ORIGIN_ENTITY_READ`, the
    vertices route and every `CARRY_*` write stay None.
  - The test asserts each of these.
- **The pin test is half a pin** (`test_w9d_2026_findings_rest_on_the_probes_two_runs`).
  - It fails when a log line changes. Verified: the r3 log's `COAXIAL_FACE_READ = True` edited to False fails it.
  - It compares the **string** findings to their proposals.
  - For the **booleans** it checks only the log's text ("True", "False"), never the value in `findings.py`. Verified:
    `COAXIAL_FACE_READ_ON_2026 = False`, and separately `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026 = None`, each pass
    the **whole suite** (2 failed, 3859 passed, the usual two).
  - *Fix:* `assert proposed(...) == repr(findings.<NAME>_ON_2026)` for each boolean too. That is eight lines.

**What a real user's Build again… does at this HEAD.**

*On SolidWorks 2026:*
- *R reads the old assembly before anything is made.*
  - Open: read as it stands, its states per mode by `GetComponentSuppressionState`.
  - Closed: now opened read-only and closed by `QuitDoc`, since every condition of R.2 can now hold (all measured
    clean for files saved by this version).
  - Either way, every user component's face and edge mates are walked by r3, up to 20 s per component.
- The build runs as W9c's.
- C then opens the new assembly and shows its first mode, which was already showing (the build's own post-save shows
  already marked it).
- C reads the app frames and plans. Because `CARRY_INSERTS` and `CARRY_REMAKE_KINDS` are None, every component is
  named `WHY_UNMEASURED` ("insert") and every mate is named (its component not carried, or its kind unmeasured).
- So nothing is inserted, no mate is made, and no state or fallback is written.

*On SolidWorks 2024:*
- A closed old assembly is never opened (`FILE_VERSION_READ` None).
- An open one is read with no per-mode states (D2) and no walk (the face and edge routes are None).
- The same C names everything.

*The two-sentence answer:*
- Every write of W9d (insert, state, mate, fallback) is still behind a `CARRY_*` gate that is None on both versions,
  so today a Build again… carries nothing and names everything with its finding.
- On 2026 the reads now set do run on a real user's session before M9: the read-only open of a closed old assembly,
  and r3's walk, whose grouped and filtered form is not yet measured. See N3.

### New faults from the fix round

**N1 (should-fix, reproduced): the post-check's per-mode tie blames the first cluster on the train.**

- *What the code does:* `_carry_post_check` (`swbuild.py:8316-8350`) now re-reads ties for **every** cluster in
  every mode it was not made in, in cluster order, against `free_before`. The first round's code did this only for
  clusters whose flags differ by mode, which is K2's rule (`USER_TIE_READ_PER_MODE`).
- *Reproduced on the fake* (scratch `test_review_tie_blame.py`, `_tc_again`'s TransferCase):
  - cluster A, Sprocket-2 locked to InDog, on in every mode and judged clean;
  - cluster B, Sprocket-1's Lock1, on in N and 4L only, which ties InDog when on.
  - In N, A is checked first and falls back: `FIXED (('carried2-1',), ('Lock0',), 'tie', ('InDog', 'N'))`.
  - Then the carry stops: *"After the fallback, InDog still reads unable to turn in N"*.
  - B's Lock1 stays made, and the user's fine cluster is fixed and blamed.
- *Fix:* in the post-check, re-judge a tie only for clusters whose mates' flags in that mode differ from their
  `made_in` mode, as K2 rules. Leave a tie no such cluster explains to the existing "no cluster of yours explains it"
  stop.

**N2 (should-fix; do it before M9 judges Sprocket-7): a cluster's mates are judged in modes where one of its
components is suppressed.**

- *What the contract says:* §3 C.6.1 says such a mode is left as SolidWorks has it and not judged.
- *What the code does:* the post-check reads each made mate's code and the train's ties in every mode
  (`swbuild.py:8339-8345`), including modes where a carried component of the cluster is suppressed.
- *What is measured:* the probe read only those mates' flags there (on, `-1.log:113`), never their codes. The fake
  gives the remade code whatever the component's state.
- *Why it matters:* if SolidWorks gives a mate on a suppressed component a code, M9's Sprocket-7, suppressed in L,
  falls back in L: its mates are deleted and it is fixed.
- *Fix:* skip a cluster in a mode where `_wanted_suppressed` holds for any of its components. At the least, M9 logs
  those mates' codes in L.

**N3 (should-fix): on 2026, R does r3's walk for real users although nothing can be carried yet.**

- *What happens:* with `CARRY_INSERTS_ON_2026` None, every user component is named in any case. Yet
  `_read_old_mates` walks every face and edge mate's component, up to 20 s each, before the build.
- *Why it matters:*
  - the walk's grouped and filtered form is unmeasured;
  - its cost grew through the measured session;
  - its only use today would be "on its axis" wording, which needs a gear mate on a made-new part, and that is behind
    `CARRY_GEAR_MATE_ON_AN_APP_GEAR`, also None.
- *Fix:* walk only when `CARRY_INSERTS` is settled (and, for an app part, the gear-mate gate). M9 patches both, so
  the demonstration is unaffected.
- *The not-open read-only open is different:* it feeds W9a's stays-behind sentence, and it is measured clean. It may
  stay.

**Notes:**
- *Making a cluster's mates in a mode other than the first.*
  - This is consistent with C.5 and C.7, which already show modes in the new assembly, and the old assembly is never
    shown. But §3 C.6.3 still says "judged in the first mode": record the deviation there.
  - The mode is restored at the end of the cluster, not on a stop part way, which leaves the unsaved new assembly in
    that mode.
  - The cluster's `made_in` mode is skipped in the post-check, so a later cluster putting an earlier one's mate into
    error in that mode is caught only by the global gear check.
- *The fallback's place.* A fallback in the post-check (mode L) places the components in L. Puts are per configuration
  on 2024 (`positions_per_configuration`), so they may stand elsewhere in the other modes. That is unmeasured;
  M9 shows only a fallback in the first mode.
- *`close_unsaved`'s still-open check runs straight after `QuitDoc`*, where the probe waited 3 s. A slow close would
  read as still open, which is safe (nothing is carried) but alarming.
- *M7's `ISldWorks.GetConfigurationNames(path)`.*
  - It is in the ledger as verified for a closed file on 2026 SP1.1 (`API-LEDGER.md:114`, beside `VersionHistory`).
    It opens nothing, so by the ledger it raises no dialog.
  - Unmeasured: the app calling it, a file loaded lightweight in the session, and 2024.
  - It needs no probe first, but M9 should log it on Sprocket-9.
- *`WHY_REFUSED` and `remake_mate(flip=)`* are sound as written. `find_component(suppressed_ok=)` is used only for
  R's reads, and its handles go with R's `end_build`.

### The fake, against the probe logs now

**Now as unkind as SolidWorks** (each from my first list):
- a suppressed component's find and selection are refused;
- there is no document for a lightweight or suppressed component;
- the build bracket can drop the document (`begin_drops_document`, off by default, so only one test sees it);
- a face or edge route other than r3's exact string reads nothing;
- per-mode remake codes;
- a Flip read wrong;
- a gear held after the save;
- the read-only document marked by its own open (also a knob).

**Still kinder:**
- `entity_references` is a model, not the Session's COM code; the prefilter's part-against-assembly area is never
  exercised;
- `_entity_kind` still names a plane on a lightweight component "plane", where the Session now says unread (S10);
- a mate's code in a mode where its component is suppressed is the remade code (N2);
- `EntityParams` are still the same for every entity, so `gear_sense`'s geometry, and a perpendicular pair, are
  never exercised;
- `place_component` seeds every configuration, where 2024 puts per configuration;
- an unwritten out code reads Ok, here as in the Session.

---

## Addendum: package A's fourth round (`94f57f8`), before the second SolidWorks run

*Independent, 2026-11-17.* I reviewed `git show 94f57f8` and the code around it, not the commit message's account. I
read it against:
- the first run's evidence at `50a8e54`:
  - `w9d-demo-sw2026-20261117-2-carry-app-faults.log`;
  - `…-3-carry-closed-read-only.log`;
  - the run section of `W9D-DEMONSTRATION.md`;
- the probe's `raw()` (`probe/w9c_probes.py:267`, which `probe/w9d_probes.py` imports);
- r3's log, `w9d-probes-sw2026-20261117-2-faces-r3-clean.log`.

No SolidWorks was started.

**Suite.** At the tree's head: **2 failed, 3897 passed, 10 skipped**. The two failures are the known tkinter tests.
The head includes `e2207d9` (docs only) and someone's uncommitted edits to `ui_text.py`, `probe/w9d_demonstration.py`
and two test files, which I did not touch or judge.

**The three new carry tests and the new swcom test, on `90cdf20`'s code.** I ran them in a scratch copy: `94f57f8`'s
tests and fake, with `90cdf20`'s `swcom.py` and `swbuild.py` put back. `90cdf20..94f57f8^` changed no `src`. All four
fail there:
- `test_a_gear_new_in_the_revision_…` fails with SolidWorks' own sentence: *"No component is kept as 'gear4', so it
  cannot be read or changed; that is a fault in Gear Generator, not in SolidWorks."* This is fault 2 exactly.
- `test_a_fault_of_ours_never_reaches_a_sentence_…` fails with the Python text in `stopped`: *"…it stopped on an
  unexpected TypeError: 'method' object is not iterable."* This is fault 3's sentence.
- `test_a_mate_on_a_lightweight_components_feature_…` fails as `'unread' == 'lightweight'`. That is the precedence in
  `plan_carry`, not SolidWorks' failure (`'NoneType' object has no attribute 'FeatureByName'` in
  `Session.entity_reference`). The fake's `entity_reference` never reaches a `None` part, and no swcom test drives
  `entity_reference` with `GetModelDoc2` answering `None`. The guard at `swcom.py:3899-3900` is right but unpinned
  (S3 below).
- `test_the_r3_walk_calls_the_members_late_binding_hands_back_uncalled` fails earlier than SolidWorks did: *"'function'
  object has no attribute 'GetBodies2'"*. Its double makes `IComponent2.GetModelDoc2` a method. On SolidWorks it came
  back a value through `call`: in run 2 the old code got past `GetBodies2` and failed on `GetFaces` (*'method' object
  is not iterable*). With `GetModelDoc2` and `Extension` as plain attributes, the double would fail on the old code
  for SolidWorks' reason (S3).

### Verdict

**Fit for the second SolidWorks run.** The three faults are fixed at their causes:
- the r3 walk now calls what late binding hands back;
- C.1 finds again every component the build placed, before anything reads one;
- no Python exception text reaches a carry sentence.

The `_read` decision cannot misread a COM object, `None` or a tuple, and no conversion can break a member `call` read
correctly before.

Before the run, I would make two small changes, each a few lines, because each could cost a two-hour run:
- **M1, the `_read` guard.** A SolidWorks failure inside a method `_read` invokes is not turned into `ComError`. It is
  said as "a fault in Gear Generator", and a lost session is not marked.
- **M2, `_set_flags` judges every mode.** It judges the modes where one of the mate's carried components is
  suppressed, which §3 C.6.1 says to leave as SolidWorks has it. On SolidWorks that could stop the whole carry at
  Sprocket-7's cluster, before the tie.

One thing outside `94f57f8` will make the run FAIL as the first one did, and it is the script's to change:
- the expectations for UserAxis9 (`carry`) and UserAxis7 (`carry-closed`), which must accept `unread`
  (`W9D-DEMONSTRATION-REVIEW.md`'s addendum, item 4);
- at head, `expected_outcome` (`probe/w9d_demonstration.py:205-207`) still expects `remade` on 2026.

### Must-fix before the run

**M1. `_read` calls an uncalled method outside `_guarded` (`swcom.py:756-767`).**

`value = call(obj, name)` is guarded, but `return value()` is not.

The probe's `raw()`, the only variant measured on 2026, calls it as `swcom._guarded(name, value)`
(`probe/w9c_probes.py:269-270`).

So a `pywintypes.com_error` from the invocation leaves as itself, not `ComError`. That covers a call rejected while
SolidWorks is busy, RPC gone, or a member that needs arguments. Then:
- `CONNECTION.lost` is never set, so the next press fails its pre-flight against a dead session instead of connecting
  again (W4 review N4's reason for `_guarded`);
- `_carry_said` (`swbuild.py:8012`) takes it for a fault of ours and says *"a fault in Gear Generator, not in
  SolidWorks"*;
- in `entity_references` (`swcom.py:3994-3997`) a failing `GetFaces` is said the same way;
- in `_remake`, `except ComError: raise` does not see it.

Since `94f57f8`, every `GetFaces`/`GetEdges`, `GetArea`, `GetSurface`, `GetCurve` and `GetType` of the walk goes
through this path. That is several hundred calls per component.

**Fix:** `return _guarded(name, value) if type(value).__name__ in ("method", "function") else value`.

**M2. `_set_flags` judges every mode, including one where the mate's own component is suppressed (`swbuild.py:8302-8320`).**

It sets the remade mate's flag in every new mode and raises `_CarryStop` if any mode reads otherwise. §3 C.6.1 says a
mode where one of its components is suppressed is "left as SolidWorks has it and not judged". The post-check does
exactly that (`swbuild.py:8424-8433`, the `hidden` fact), but `_set_flags` does not.

The next run reaches this:
- UserAxis7 is made again in `carry`, where Sprocket-7 is resolved in H.
- It is then flagged on in L, where Sprocket-7 is suppressed.
- No run has read a newly made mate's `IsSuppressed2` in a mode where its component is suppressed. The old
  assembly's mates read their own flag there (W9D-PROBES-REVIEW's fact (a)), which is reassuring but not this.
- A mismatch stops the whole carry, and Sprocket-7's cluster comes before the tie in cluster order. One unmeasured
  read could so end the run's main demonstration.
- The fake's `mate_suppression` returns what was set, so no test can see it.

**Fix:**
- Compare `read_on` and `on` only over the modes where every carried component the mate joins is resolved
  (`_wanted_suppressed`).
- Keep the other modes' reads as a fact, as the post-check does.
- Add a fake knob that reads such a mode otherwise, so a test pins it.

### Should-fix

**S1. The stop's sentence contradicts itself.**
- For a fault of ours, `swbuild.py:8003` now says *"SolidWorks stopped the carry while making the mates of Sprocket-1
  again: a fault in Gear Generator, not in SolidWorks"*, as the new test asserts.
- The read's failure (`:3537-3539`) says *"SolidWorks did not answer the read of RangeBox.SLDASM: a fault in Gear
  Generator, not in SolidWorks"*.
- Each opens by blaming SolidWorks and closes by clearing it.
- Fix: let `_carry_said` decide the lead as well. *"The carry stopped while …: a fault in Gear Generator, not in
  SolidWorks."* and *"RangeBox.SLDASM could not be read: a fault in Gear Generator, not in SolidWorks."*

**S2. The Python text is not always kept where a developer can find it.**
- `_carry_said` puts it in `CarryResult.facts`, which `log_lines` prints. Good.
- But `entity_references` puts it in `Session.last_walk["faults"]`, and `_read_old_mates` copies only `items`,
  `carried`, `seconds` and `capped` into `work.walks` (`swbuild.py:7850-7854`). The next component's walk then
  replaces `last_walk`, so the text is lost.
- `entity_reference`'s fault branch (`swcom.py:3905-3907`) keeps the text nowhere.
- Fix:
  - add `walk.get('faults')` to the `work.walks` line;
  - keep a `last_reference_fault` on the Session, which `_read_old_mates` copies to `work.walks` (or an `OldWork`
    facts list).

**S3. The tests could be closer to SolidWorks.**
- **The r3 double.** In `test_the_r3_walk_calls_…`, make `Component.GetModelDoc2` and `Part.Extension` plain
  attributes, as SolidWorks answered them in run 2. Keep `GetFaces`, `GetArea`, `GetSurface` and `GetType` as
  methods. The test then fails on the old code with *'method' object is not iterable*.
- **A swcom test of `entity_reference` with `GetModelDoc2` `None`.** The walk's sibling, `entity_references` with
  `part is None`, needs one too (S4).
- **`strict_handles`.**
  - It refuses only in `component_frame` and `constrained_status` (`tests/test_swbuild.py:936`, `:1328`). The
    Session refuses in every member that takes a component handle (`_component`, `swcom.py:3237-3248`):
    `place_component`, `fix_component`, `set_component_suppressed`, `component_configurations`, `delete_component`,
    `remake_mate`'s whole-component and `"<handle>:<feature>"` targets, `select_by_reference` and `entity_references`.
  - It is on through `_old_train` and `_tc_again` only. `test_states_and_flags_are_set_in_every_mode_…`
    (`tests/test_swbuild_carry.py:805`) and `test_a_cluster_with_only_mates_between_app_bodies_…` build their fakes
    otherwise and run without it.
  - Today C.1 finds every handle, so nothing leaks. But the fake would not catch the next forgotten handle in a
    target, which is where the plan's app handles go.

**S4. A component suppressed in the mode showing gets the wrong reason.**
- Its face or edge mate goes to `entity_references`, whose `part is None` branch (`swcom.py:3934-3936`) says *"no
  measured route for a face here"*. On 2026 the route is set, so that is false.
- `entity_reference` says the right thing: *"its part is not loaded in SolidWorks (lightweight or suppressed)"*.
- Fix: use the same words in `entity_references`.
- The demonstration's two suppressed components have feature mates only (UserAxis7, UserAxis9), so the run does not
  meet this; a user will.

### Notes

**`_read`'s decision against pywin32.**
- It invokes only a value whose type is named `method` or `function`. pywin32's dynamic dispatch hands a member it
  knows as a function back through `_make_method_`, a bound method (`types.MethodType`, named `method`).
- A COM object comes back as `CDispatch`. That object is callable (its call invokes the default member), but it is
  never invoked here, because its type name is not `method` or `function`.
- `None`, tuples, numbers, strings and `bytes` are returned as they came.
- So the only way to go wrong is a method that needs arguments, and M1 makes that a `ComError` sentence. Every
  converted member is zero-argument, and their arguments match what the probes' `raw()` passed:
  `GetTypeName2`, `GetArea`, `GetCurve`, `IsCircle`, `CircleParams`, `IsLine`, `GetSurface`, `IsCylinder`,
  `CylinderParams`, `GetType` (`IEntity` and `IModelDoc2`), `GetSaveFlag`, `GetDefinition`, `GetModelDoc2`,
  `GetConfigurationNames`, `GetActiveConfiguration`, `Name`, `GetSuppression2`, `GetFaces`, `GetEdges`.
- `_read` differs from `call` only when `call` returned a method. So no conversion can break a member that an earlier
  run read correctly as a property through `call`: `GetType`, `GetSaveFlag`, `GetDefinition` and `GetModelDoc2` on
  the build path read exactly as before.

**Members still read through `call` on the carry path.**
- Each has come back a value on SolidWorks in an earlier run: `GetTitle`, `GetPathName`, `FirstFeature`,
  `GetNextFeature`, `Name2`, `IsFixed`, `Extension`, `SelectionManager`, and `GetSpecificFeature2` in
  `_component_by` and `constrained_status`.
- `GetLatestSupportedFileVersion` (`swcom.py:4082`) is the one I checked for its effect. Had it come back a method,
  `int()` would have failed, `running_file_version` would have answered None, and R.2 would have refused. Run 3
  opened the old assembly read-only, so it answered a value.
- The tier 1 resolve of a carried part's feature (`select_by_reference`) is new on this path. Its members match S5
  (c)'s and the probe's r3 resolve: `GetObjectByPersistReference3(bytes, code)`, `GetCorresponding`, and `Select4`
  with two arguments.
- The out code is written by SolidWorks. r2's resolve read code 1 over a holder that began at 0. So the `-1`
  initial value cannot misread an Ok.

**C.1 (`swbuild.py:8036-8039`).**
- `GearboxResult.components` holds each component's `Name2` as `add_component` read it back (`swcom.py:2190`,
  `swbuild.py:553`). These are top-level components of the assembly the build made seconds earlier, so instance
  suffixes are SolidWorks' own, and nothing renames them before the carry.
- A name not found raises `ComponentGone`, a `SolidWorksError`. The stop says *"… X is not in RangeBox_r2.SLDASM any
  more: it was renamed or deleted in SolidWorks."*, a sentence and not Python text.
- One corner: a component whose `Name2` SolidWorks did not give is kept as `""` (the finish's own note). C.1 would
  then stop on *" is not in …"*. Skip empty names.

**Reads by handle after C.1.**
- Every later read takes a handle the carry's own bracket found or made: the app bodies from C.1; the carried
  components from `add_component`; the mates from `remake_mate` and `find_mate`.
- `_component` finds a handle again by name after every show or open (the epoch rule), so the post-check, `_free`,
  `_judge`, the fallback's `place_component`/`fix_component`, `_app_mates_check` and the per-mode `component_frame`
  reads are all covered.
- `_mated_handles` is a subset of `result.components`.

**The lightweight choice (D10) is done as ruled.**
- R reads nothing through a lightweight component's part: no walk and no `entity_reference` (`who in light`,
  `swbuild.py:7834`, `:7870`).
- `plan_carry` names its mates `WHY_LIGHTWEIGHT` before the unread check (`:7503-7511`).
- `mate_definition`'s own reads (type, `ReferenceType2`, `EntityParams`) still run. Run 2 read them without
  resolving anything; SprocketLight-1 resolved only when its file was opened to insert it, M1 (b)'s ruled fact.
- The user reads, before the press, B's *"SprocketLight-1 was lightweight as read: its UserAxisLight is made again
  only if you set it resolved in SolidWorks before you press."*
- After the press: *"UserAxisLight is on SprocketLight-1, which was lightweight in RangeBox.SLDASM, so what it joins
  could not be read, so it is not made again."* That is followed by *"SprocketLight-1 was lightweight in
  RangeBox.SLDASM and is resolved there now: SolidWorks loaded its part to carry it."* True, and not contradictory,
  since the order is said. The double *so* is B's to smooth.
- `expected_outcome` agrees: UserAxisLight `{"lightweight"}`, and UserAsm6 `{"unread"}`, since there is no root read
  beside a lightweight component.

**The rest of the carry after the states.**
- These lean on the fake only where the earlier addendum's "still kinder" list says: identical `EntityParams` (the
  gear sense and the Flip retry are never met against real geometry), and remade codes per mode.
- New in this round: the fake's `mate_suppression` returns what was set (M2), and the walk's exception path is
  modelled, not COM's.
- The reversed retry, the fallback and the post-check now read only handles the carry's bracket holds. I found no
  further place that would have met fault 2.

---

## Re-check of package A's fifth round (`a366938`, `2bab5db`), before the second SolidWorks run

*Independent, 2026-11-17.* I read the two commits' diffs against my addendum (`eb66f22`) and the coordinator's M3.
Scratch tests in the scratchpad drove A's worker on the fake, once with the fake's entity read made as SolidWorks
read it in run 2. No SolidWorks was started.

**Suite** at head: **2 failed, 3904 passed, 10 skipped**. The two failures are the known tkinter tests.

### Verdict

Package A's head is **fit for the two-hour run**:
- M1 and M2 are fixed as asked.
- M3 is the right line.
- S1 to S4 are done.
- The fake's `strict_handles` now refuses wherever the carry's Session members refuse.

Two things remain, neither a reason to hold the run:
- **UserAxis9 still has no why on SolidWorks.** The why-field A added for it is reached only on the fake (A1 below).
- **No worker test still shows a same-error mate carried.** M3 changed the only one (A2).

### M1, M2, M3

**M1 is fixed** (`swcom.py:766`). The call goes through `_guarded(name, value)`, so a COM error from the invocation is
a `ComError`:
- `_guarded` sets `CONNECTION.lost` when the error says the session has gone;
- `_remake`'s `except ComError: raise` now meets it;
- `_carry_said` says it as SolidWorks' own sentence.

It is pinned by `test_a_member_handed_back_uncalled_is_called_under_the_com_error_guard`.

**M2 is fixed** (`swbuild.py:8343-8356`).
- The flag is set in every mode as recorded and read back.
- A mode counts as one "where a component of the mate is suppressed" by `_wanted_suppressed`. That is the state C.5
  set in that mode and **read back from SolidWorks** before any mate was made: `_carry_states` stops if a state does
  not read as set. So the decision rests on what SolidWorks reported.
- Those modes' reads become a fact. Every other mode is compared exactly as before, and a mismatch there still stops
  the carry.
- The post-check skips the same modes (`hidden`), so nothing is blamed there.

**M3 is the right line** (`swbuild.py:8388`, `W9D-INTERFACES.md` §6).
- `tied` no longer subtracts `excused`. A gear on the cluster's train that was free before it and is not free after it
  falls the cluster back (`FELL_TIE`), whatever codes its mates read. So no gear free before and tied after can be
  excused any more.
- The excuse still covers what §6 now says, and only that:
  - the mate's own code (`same_error`);
  - a user body's over-definition, only where every remade mate of the cluster on that body is back in its old error.
- A cluster that read over-defined in the old assembly and ties no gear still comes over as before: its codes are
  `same_error`, its bodies are excused, and `_free` finds no gear newly held.
- The changed expectation in `test_a_new_error_or_an_over_definition_falls_back_and_the_same_error_is_carried` ("same
  error") follows from K2 and from §6 as written. There Lock1 alone holds Sprocket-1 to G1, comes back in 46, and G1,
  free before, reads held after. Under K2 the user's work never keeps a gear from turning, so the cluster falls back
  `FELL_TIE ("G1", "")`. The new §6 sentence says exactly that.

### S1 to S4

- **S1 is done.**
  - A fault of ours reads *"The carry stopped while making the mates of … again: a fault in Gear Generator, not in
    SolidWorks."* and *"The read of RangeBox.SLDASM stopped: …"*.
  - SolidWorks is the subject only of a `SolidWorksError`.
- **S2 is done.**
  - A walk's `faults` go to its logged walk line.
  - `entity_reference`'s fault text goes to `Session.reference_faults`, which `_read_old_mates` copies into
    `work.walks` (printed as `fact    reference read fault: …`) and then clears.
- **S3 is done.**
  - The r3 stand-in now has `GetModelDoc2` and `Extension` as attributes, so the old code fails at `GetFaces`, where
    SolidWorks failed.
  - A Session-level test pins both reference reads with no part document.
  - The fake's `_strict` is now in `fix_component`, `unfix_component`, `place_component`, `is_fixed`,
    `component_path`, `component_frame`, `delete_component`, `constrained_status`, `component_resolved`,
    `component_configurations`, `set_component_suppressed` and `entity_references`. It is also in the target
    resolution `remake_mate` uses: a whole component, `"<handle>:<feature>"`, and `select_by_reference`'s handle.
  - **Against the Session**, whose `_component` is reached from `_component_ref`, `_lock_mate`, `_remake`,
    `_select_target`, `component_configurations`, `component_frame`, `component_path`, `component_resolved`,
    `component_translation`, `constrained_status`, `delete_component`, `entity_references`, `fix_component`,
    `is_fixed`, `place_component`, `raw_component`, `select_by_reference`, `set_component_suppressed` and
    `unfix_component`. Every member the carry calls is covered. The four the fake leaves lenient
    (`component_translation`, `_lock_mate`, W5's `_remake`, `raw_component`) are the build's and Update's, never the
    carry's.
  - The two carry tests built without strictness now have it.
- **S4 is done.** `entity_references` with no part document says *"its part is not loaded in SolidWorks (lightweight
  or suppressed)"*.
- The note is taken too: C.1 skips an empty `Name2`.

### A1 (should-fix). The why for UserAxis9 is reached only on the fake

A's note says a feature on a suppressed component now carries the Session's *"its part is not loaded …"*. That
happens only when the entity's kind reads `feature`, which sends it to `entity_reference`.

On SolidWorks it did not read so. Run 2 read UserAxis9's Sprocket-9 entity as `('user', 'Sprocket-9', 'unread', '', …)`
(`-2-carry-app-faults.log:621`): `ReferenceType2` gives nothing through a component suppressed in the mode showing.
So:
- the kind is `unread`;
- no reference read is made;
- the new `UNREAD_ENTITY` why does not apply, since `what` is `USER`;
- the entity's `unread` stays `""`.

Two scratch runs on A's worker:
- **The fake as it is** (its `_entity_kind` answers `feature`): *"SolidWorks would not describe UserAxis9 wholly (its
  part is not loaded in SolidWorks (lightweight or suppressed)), so it is not made again."*
- **The fake's `_entity_kind` answering `unread` for that component, as SolidWorks did:** *"SolidWorks would not
  describe UserAxis9 wholly, so it is not made again."* That is no why, the run's sentence again.

**Fix:**
- In `_read_old_mates`, when an entity's kind is `unread` and its owner is a user component whose state in the mode
  showing is suppressed, set `unread` to *"{who} is suppressed in {work.active}, the mode {old} showed"*. B's clause
  already says the slot.
- Make the fake's `_entity_kind` answer `unread` for a component suppressed in the mode showing, as run 2 measured.

The run is not hurt by this: UserAxis9 is named unread either way, as the script now expects. Only the sentence lacks
its why.

### A2 (should-fix). No worker test shows a same-error mate carried any more

The parametrised test's "same error" case now falls back, so `same_error` non-empty is shown only by B's hand-made
results.

Add one case where a mate between two user components (no app gear on its train) reads its old code again and is
carried in `same_error`, its cluster kept. The test's name still says "the same error is carried", which it no longer
shows.

### A3 (note). The UserAsm6 why is SolidWorks-shaped only by reasoning

The new why for an `UNREAD_ENTITY` beside a lightweight component reads *"the assembly's own plane is not told while
a component of it is lightweight"*.
- **Whether the code path is reached is unproven on the fake.** The fake names the assembly's own entity `""` (taken
  as `ASSEMBLY` with no root read). So on the fake a mate to `asm:plane1` beside a lightweight component is simply
  carried (scratch run: `named` empty).
- **On SolidWorks it is reached.** There the entity names the root (`ASSEMBLY_ENTITY_COMPONENT_IS_ROOT`), the root is
  not read beside a lightweight component, and the entity is `UNREAD_ENTITY`. That is run 2's UserAsm6, and this why
  then applies.
- **The words are wrong for the user.** *"is not told"* is not English for "cannot be told", and it is Gear
  Generator's own rule, not something SolidWorks withheld. Yet B's clause frames every `WHY_UNREAD` as *"SolidWorks
  would not describe … wholly (…)"*. Shared with B in `W9D-REVIEW-B.md`.

### What the second run meets for the first time

The run's reviewer should look at each of these. Each so far has been shown only on the fake, or only by the probe's
own code.
- **C.1**: every app component found again by `Name2` after the build's bracket, a gear new in the revision included.
- **The r3 walk through the Session's own code**:
  - grouped per component;
  - the area or radius prefilter, part entity against assembly entity;
  - the cap's two numbers;
  - seconds per component as the session ages;
  - `IEntity.GetType` on the resolved entity.
- **Tier 1's resolve and select on a carried component** (`select_by_reference`: `GetObjectByPersistReference3`,
  `GetCorresponding`, `Select4` with mark 1).
- **`remake_mate` for each kind the app has never remade**: concentric on a face, parallel, limit distance (`AddMate5`'s
  limit arguments) and gear (the ratio swap). Coincident, distance, angle and lock on features were remade by S5 (c);
  on faces and edges only by the probe.
- **The read-back**:
  - entities by `ReferenceComponent`, the assembly's own read as `""`;
  - alignment;
  - values;
  - a gear's sense from real `EntityParams` (the fake's are identical);
  - the reversed retry;
  - the Flip retry.
- **The rename of a remade mate** to its old name, and SolidWorks' name kept when the old one is taken.
- **`set_mate_suppressed_in` and `mate_suppression` on a user mate the app remade**, including a mode where its
  component is suppressed (M2's fact; UserAxis7 in L).
- **`_judge`**:
  - mate codes after one top-only rebuild;
  - `GetConstrainedStatus` on the new assembly's gears for the tie;
  - the tie now never excused (M3).
- **The fallback**: `delete_mate` (`Select2` then `EditDelete`) of a mate just made, then the cluster's components
  placed and fixed again.
- **The post-check per mode**:
  - each carried component's pose against its anchor (`moved`);
  - the app's own mates' codes against before (`_app_mates_check`, `find_mate` on an app mate);
  - the interference naming a carried component.
- **A record whose carry holds remade mates** (run 2's held none), and the footer's line after it.
