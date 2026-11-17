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
