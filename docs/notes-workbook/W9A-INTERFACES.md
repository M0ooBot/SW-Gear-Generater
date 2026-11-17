# W9a package A (the worker side of issue #1): what package B may call and rely on

Package A of `ISSUE-1-PLAN.md` §5's W9a, written against the fake from `a648e0a`, reviewed in `W9A-REVIEW-A.md`
(`51b398b`) and revised in one fix round under the coordinator's rulings 1 to 8 on that review (§6 below), then
under the demonstration's ruling on SolidWorks 2026 with the run review's conditions (`W9A-RUN-2026-REVIEW.md`,
finding 1; §4 item 11). Authority:
the plan as amended by *Changes after S0 and its review* (route (c1) is K2's route; every other kind of user mate on a
put gear refuses), then `W9-S0.md` and the W9 findings in `findings.py`. Nothing here touches the window,
`ui_text.py`, `gui.py`, the record's schema or the boards: those are package B's. A change to a shape below is a
stop-and-ask, as at W8.

## 1. Where the reads and refusals live

- **`swcom.Session`**, reads only: `components()` → `[ComponentInfo(name, path, fixed, state, code)]` (top level,
  `GetComponents(True)`); `mate_info(handle)` → `MateInfo(name, type, components, counted)` (`IMate2.Type`, each
  `MateEntity(i).ReferenceComponent.Name2`, `""` for the assembly's own, `None` for an entity that would not answer;
  `counted` False when the count would not; `whole` says all was read); `feature_states()` →
  `[FeatureState(name, type_name, code, warning)]`. `UNREAD = -1` for a code or type not given. None is behind a
  finding: the plan measures them in W9a's demonstration (M1, M2), whose STOP on a `GetSaveFlag` change stands.
- **`swbuild`**, check phase (the motion path; the static W4 path reads K11 and the features only):
  `_read_user_work`, **`judge_user_work`** (K2, pure, §2.3), `_user_check` (the end of the check phase, every problem
  raised at once), `_vouches` and `_value_edits` (K11, documents), K11 for Face Z / slides / flags in
  `_update_motion` and `_modes_check`, `_find_by_part` (K1). Change phase: `_put_train(..., carried=, user=)` and
  `_put_carried` (route (c1)), `_bind` (a put the check did not judge, where the user's work is, stops the job),
  `_modes_tie_read`, `_mate_problems(..., user_before=, user_found=)`, `_components_after`, `_carried_problems`
  (each carried pose read again), `_free_to_turn(..., mates_on=)`, `_update_document` (K3), and, at each assembly
  rebuild that returns False, `_rebuild_laid_to_user` (§4 item 11, gated by `assembly_rebuild_settled`).
- **`workbook/update.py`**: `classify(..., read_sidecar=None)` fills what the worker needs (§3); `finish_update`
  writes a component found by its part into the record by the name found.

## 2. What package B may rely on

### 2.1 On a result (`GearboxUpdate`, motion path)

| Field | Meaning |
|---|---|
| `user_work: Optional[UserWork]` | The user's work as read before anything changed; `None` when the assembly was not read. On the static path, a `UserWork` holding only `features` (or `None`). Falsy when it holds nothing: test `is not None` for "read". |
| `carried: [(component, gear, configuration)]` | Each put of a user component with its gear (route (c1)), in the order put; configuration `""` with no modes. |
| `renamed: [(gear, Name2 on record, Name2 found)]` | K1. `finish_update` already records the found name; no schema change. |
| `user_in_error: [(mode, name)]` | Each user mate or component read in error after the change, those in error before included. A mate the Update put in error in a mode other than the one active at the check is listed here only (its state before was never read): B shows it with its mode. |
| `user_features_in_error: [UserFeature]` | Each user feature read in error once its document was rebuilt (K3): the user's, never a failure. **Filled on a failed Update too** (the close review's must-fix 2), on both paths, as are `user_work`, `values_set` and so both methods below: B can name the user's features newly in error after "Update SolidWorks stopped". `user_feature_was_in_error(f)` is True for one already in error when the check phase read it, before anything changed ("was in error … before this Update changed anything, and still is"), False for one newly in error ("is in error … now"); `values_under(f)` is what this Update set in that feature's document, `[ValueSet(path, name, was, now, cell)]` (k3: G1's Bore 8 -> 14, `Gears!J2`). |
| `rebuild_from_user_alone: [str]` | §4 item 11: an assembly rebuild returned False and was laid to the user's work alone; what of the user's was in error then, by name (a feature as `"Keyway in Gear_m1.25_N17.SLDPRT"`). The Update went on: no failure, nothing saved, as any Update. `rebuilt` stays as SolidWorks answered (False), so B must not say the app's "error rebuilding" when this is non-empty, and the same for a part whose `rebuilt` is False while only the user's features in it are in error (no failure names it). Empty otherwise. |
| `values_set: [ValueSet]`, `features_read: {path: bool}` | Each global the Update set, per document, with what it held before; each document whose features were read after its change, True where a feature the app made read in error. |
| `extra_mates` | Unchanged: the user's mates suppressed in every mode. `user_work.mates` holds every user mate, suppressed or not; `on` says where each is on. |

`UserWork(read_at, components, mates, features, carried)`; `read_at` is `store.now()`'s UTC stamp; `in_error` names
everything of the user's found in error before the change. `carried` is `(component, gear, the user's locks that hold
it)`, what this press put or would have put. `UserComponent(name, path, fixed, code, state)`; `UserMate(name, kind,
type, touches, on, code, warning, whole)` — `kind` `USER_LOCK`, `USER_GEAR` (a gear, cam, rack-and-pinion, screw or
linear-coupler mate) or `USER_OTHER`; `touches` per entity `(what, name)`, `what` one of `APP` (a gear or carrier id),
`LAYOUT`, `ASSEMBLY`, `USER` (a top-level Name2; a sub-assembly's leaf named by its top level) or `UNREAD_ENTITY`;
`on` the modes it is on in (no modes: `("",)` on, `()` suppressed); `whole` False when SolidWorks would not describe
it. `UserFeature(path, name, type_name, code, warning)`.

### 2.2 On a refusal, and what the record must keep (K4)

`UserWorkRefused(BuildError)`, raised before any write; `str()` is every sentence joined; `.problems` is a tuple of
`UserProblem(kind, sentence, mates, values)`, values first, then mates; `.user_work` the inventory as read. Kinds:
`PROBLEM_VALUE` (K11, with `ValueEdit(document, name, live, wanted, recorded, mode, cell, unsaved, blank)`; `blank`
says what the workbook's value stands for where its cell can be blank: `"no bore"` for a Bore of 0, or the default
equation of a blank Backlash or Fillet, `"0.3 × Module"`; the sentence says it so, never "0 in the workbook"),
`PROBLEM_OTHER_KIND`,
`PROBLEM_LOCK_BY_MODE`, `PROBLEM_TWO_BODIES`, `PROBLEM_TIE` (read by SolidWorks, or a lock chain to the ground: its
sentence says which), `PROBLEM_UNSETTLED` (a finding route (c1), one of its branches, or the tie read rests on is
missing), `PROBLEM_COMPONENT` (a component route (c1) would put is suppressed, lightweight, reads in error, or its
error code could not be read — the last two since the run reviews (finding 1 of the first, finding 5 of the close
review: unread counts as in error), unmeasured, its own part most likely holding a feature in error: judged inside
`judge_user_work` since package B's fix round, so the footer's prediction foresees it), `PROBLEM_UNREAD` (a user mate
SolidWorks would not describe).

**Schema 7 must hold**, per refused or finished job, with `read_at`: the inventory (per part path the user's features;
the user's components; the user's mates with kind, touches, on and code) and, for a refused press, its `problems`
(kind, sentence, mates, values). A tie is a solver read: B cannot recompute it, so the recorded refusal is what the
footer says until the workbook changes; then the prediction runs on the inventory as well (the coordinator's ruling 5
on package B's review). As written (`store.UserWorkEntry`, `W9A-PACKAGE-B.md`), a user component is kept by name and
kind (`part`, `assembly`, or `""` when its file was not named), never by the user's own file path; reading the
record back gives the judgement a path of that kind's extension. Another `BuildError` met earlier in the check (a `NotAsBuilt`, a missing
finding) carries no inventory: the user's work is read at the end of the check phase.

### 2.3 Predicting a press before it is made (the footer)

`judge_user_work(work, modes, put, *, file, trains, mated, read_tie=None, branches, revision) -> UserJudgement` is the
worker's own judgement, pure. Called with `read_tie=None` it reads nothing and lists in `unread_ties` each train a tie
would be read on. B calls it on the recorded inventory with `put` the bodies a press would put (every mated body of
the gearbox for a gearbox with modes, which ruling 9.18 puts whole whenever it changes anything), `branches =
user_carry_branches(plan.motion, plan.placements)` and the revision last seen, and says `carried` (gear -> [(component,
locks)]) and `problems` before the press. `user_carry_branches` and `user_branch_settled` are pure too.
**`branches` defaults to the safe reading** (re-check N6): `None` means nothing measured, every carry refused as a
fault ("how Sun is put was not said to this judgement"), and no lock is offered in an other-kind sentence; `{}`
means every body on S0's measured branch. Package B's one call (`update.user_work_ahead`) passes
`user_carry_branches(...)` explicitly and is unchanged.

**The build job's read of the old assembly** (§2.1 item 8) is W9a's, package B's (the coordinator's correction of
an earlier ruling that put it in W9d): `swbuild.read_old_assembly(sw, OldAssembly)` reads, with `_read_user_work`
itself, the user's work in the assembly a Build again… leaves behind, only when that assembly is open in the session,
as it stands there (no mode shown, nothing written or saved; made the document read by
`swcom.Session.use_open_document`, which neither opens nor activates it: no `OpenDoc6`, no `ActivateDoc3`), and
`build_gearbox(..., before=)` makes that read first,
into `GearboxResult.old_user_work` / `old_read`. When it is not open, the result says what the record's inventory
holds, with its `read_at`. The Build again? question says, from the record, the inventory the last Update or refusal
kept, with its time and "nor anything added since", or, with none on record, without a time that anything added
stays behind. Carrying anything over stays W9d's. (`W9A-PACKAGE-B.md`.)

## 3. What the worker needs from planning (`classify` fills it; defaults keep W8's behaviour)

- `DocumentValues.recorded`: `(global, expression)` as the record says the file holds it (None judges nothing);
  `mark`: the record's mark on the file, `MARK_UNSAVED`, `MARK_MISMATCHED` or `""`. The worker decides from both
  (`_vouches`, ruling 3): no mark, the record vouches; mismatched, it does not; unsaved, it vouches when the job did
  not load the file from disk (W4's third review: `_note_opened` lists such a document in `result.opened`) and
  SolidWorks reads it modified — it stayed open since the Update that marked it — and not otherwise (the lost Update,
  where W8's set-back stands).
- `DocumentValues.cells`: `(global, cell)`, every row's cell joined for a part two rows share (`"Gears!J3 and
  Gears!J5"`); a global with none is said as "no cell of the workbook sets it alone: set it back in SolidWorks".
- `DocumentValues.made`: the features the record lists for the part (its `.gear.json`, given `read_sidecar`), else
  today's plan's (`swbuild.plan_features`); the layout's and a carrier's `layout_features`. **B must pass
  `read_sidecar` to `classify` in the window** (`workbook_gui.py`); until then today's plan is the fallback.
- `Placement.part` for K1; `MotionUpdate.layout_component`, `record_holds` (the record's word given),
  `assembly_mark`, `recorded_faces`, `cells`.

## 4. Judgement calls where the plan left room (as revised)

1. **Route (c1) only where measured**: S0's train with a carrier, and since the demonstration a train with no
   carrier on a gearbox with no modes on 2026 (`USER_MATE_PUT_NO_CARRIER_ON_2026` True, section `nocarrier`). Every
   other branch is its own finding, `findings.USER_MATE_PUT_<NO_CARRIER|NO_CARRIER_MODES|HELD_GEAR|FIXED_GEAR|
   SUBASSEMBLY>_ON_<year>`, None, and refuses naming the user's lock until set True (ruling 4; the sub-assembly
   branch is mine, and so is `NO_CARRIER_MODES`, split off at the demonstration's ruling because the run put a
   train with no carrier on a gearbox with no modes only, while `user_carry_branches` would have labelled the
   TransferCase's trains `NO_CARRIER` too). The rigid motion is read after the app's locks (and a carrier train's gear mates) are off and the
   assembly rebuilt; components are put after every app body of the step, before the app's mates go back on.
2. **"May put", before any change.** No modes: a train out of step or off its axis against the wanted frames, one
   whose Face Z changes or whose gear mate is remade, every train when the layout or a carrier changes; with modes,
   every mated body whenever the press changes anything or would put in the active mode. **A held or fixed gear only
   when it is off its wanted frame**, whole pitches allowed (ruling 1). The change phase is bound to it (`_bind`).
3. Clusters through the user's locks on in every mode; a lock on in some modes reaching a put body refuses.
4. Two app bodies held together through user locks refuse, whether of one train or two.
5. A lock chain from a put gear to the ground (the layout, the assembly, a fixed component of the user's) refuses
   with its own sentence, no read made or claimed (ruling 1, review point 10).
6. A user gear, cam, rack-and-pinion, screw or linear-coupler mate on a component route (c1) would put refuses.
7. The user's mates "on a train": those on a body of it, and on through the user's floating components.
8. **The other-kind sentence says the way through** (ruling 5): a lock to that gear goes with it — or, where route
   (c1) on that gear is not yet measured, will once it is — or suppress the mate.
9. **K11 by the record's word and its mark** (ruling 3, above).
10. **The user's features** are those after the app's first that the record (else today's plan) does not list.
11. **A rebuild that fails on the user's work alone is not a failure** (the coordinator calls this judgement call
    12). A part's: while `findings.WHATS_WRONG_OPENS_ON_PART_REBUILD` is False, when only the user's features read in
    error and the app's none. An assembly's (the demonstration's ruling, M3 measured on 2026, with the run review's
    four conditions; motion path, with modes and without), at every rebuild that returns False,
    `_rebuild_laid_to_user` reads, and the Update goes on only when all hold:
    1. something of the user's is found in error — a component of theirs, a feature of theirs in an app part, or a
       mate of theirs, a mate alone only where `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_<year>` is False (on 2026
       it is True: a mate in error alone leaves the rebuild True, so it does not explain a False);
    2. nothing of the app's is in error, read whole: every recorded mate on and in error (not a warning, as the
       post-check), every feature the app made in every app part (the parts, the layout, the carriers: each app
       component's part must have been read, after its change where this Update set it, else in the check phase);
       anything unread counts as in error;
    3. an app component's own error code is not judged (a user feature in its part sets it: m3's Sprocket-1 read 1);
       its part's features and its mates are;
    4. `assembly_rebuild_settled(revision)`: `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_<year>`,
       `ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_<year>` (False) and `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_
       <year>` (False) all set; on 2024 the mate finding is True (v24:51) but the other two are None, so there it stays
       today's failure.
    Then `rebuild_from_user_alone` names the user's items and the log says "CHECK   the assembly's rebuild reported
    an error, from your work alone: …"; the post-checks run as after any rebuild. Otherwise the failure is as
    before, naming what of the user's was already in error. The static path reads no mate or component, so an
    assembly rebuild failure there stays one. Not measured, so refused before any write: a press that would put by
    route (c1) a component of the user's that reads in error (`PROBLEM_COMPONENT`).
12. A user mate or component newly in error is a failure as the user's in the mode active at the check; elsewhere
    listed only. A user feature newly in error never is (K3, item 11).
13. "The app's own mates leave it free" is taken from the record.
14. K1 on the motion path only; the layout renamed in SolidWorks is still the app's, by its part.
15. A mate's kind is `findings.MATE_LOCK` / `MATE_GEAR` against `IMate2.Type`, plus the motion types; anything else is
    "other". **A mate not wholly read refuses whenever anything is put** (ruling 2); a quiet press puts nothing.
    A mate read with fewer than two entities is not wholly read (re-check N2). While any mate on in some mode is not
    wholly read, every body counts as touched by the user's work for `_bind` (re-check N3), so a quiet press that
    the change phase finds it must put after all stops before the put.
17. **A carried component whose file did not read** (`ComponentInfo.path` `""`) takes the sub-assembly branch,
    gated by `USER_MATE_PUT_SUBASSEMBLY_ON_<year>` (re-check N4): the smaller change than a new refusal, and the
    same answer until measured (the sentence says the file was not named and it is taken for a sub-assembly).
18. **K11 on a document the record marks unsaved** (re-check N1, the coordinator's ruling): `_vouches` cannot tell a
    document open since the Update that marked it from one reopened from its file and then touched, so an honest
    lost Update can refuse. The refusal stands (the safe side), and the sentence (`ValueEdit.unsaved`) says both
    readings: the value differs from what Update SolidWorks last set and left unsaved, either because it was changed
    in SolidWorks since or because SolidWorks closed without saving that Update and the document was changed after;
    and what to do in each case. Nothing is added to the record's schema: the sentence is what is kept.
16. A component's state per mode is not read (S5's); a carried component suppressed, lightweight or in error in the
    active configuration refuses.

## 5. Gaps package B must say, not hide

- **The static (W4) path judges no user mate** (review point 15): a user lock to a static gear Update re-places is
  re-taken silently, as before W9a. Every gearbox since W5 turns; B's words should not promise otherwise.
- **The user's assembly-level features** (cuts through a gear, component patterns) are not read (point 16): an
  assembly rebuild failure they cause is said as the app's, but for the "already in error" clause. The inventory is
  not complete.
- **Per mode**, only the active configuration's component states and user mate errors are read before (point 17).
- **The branch labels join trains over every mesh** (re-check N5): `user_carry_branches` joins a train over every
  mode's meshes, where the no-modes change phase joins through a held gear only by its gear-mated meshes. A train
  with no carrier meeting a carrier train only through an unmated mesh to a held gear would be labelled S0's branch
  while put with its gear mates on. No fixture has such a train; left as a note.
- **A document marked mismatched is never vouched for** (re-check N8): a user's edit made in it after the mark is
  set back silently, as the record cannot say what that file holds. Narrow: a later job found the earlier Update lost
  and did not put it right.
- **The other-kind sentence for a gear mate between two of the user's components** (re-check N9), one of them carried,
  says the mate is "on G1", the carrying gear, though it is on the user's components. Left as a note.
- **Known and left for a later stage** (the coordinator's addendum; changing them would change how many problems a
  refusal carries, which B's footer, the record and the demonstration's expected problem lists all count):
  `PROBLEM_COMPONENT` is one problem per component, so three sprockets loaded lightweight say the same refusal three
  times in full (it should become one problem per reason naming the components together); `PROBLEM_UNSETTLED` for
  an unmeasured branch is one problem per gear, repeating the whole reason (it should become one per branch).
- **The static (W4) path: a False assembly rebuild there stays a failure** (item 11). That path reads no mate and no
  component of the assembly, only the documents' values and features, so nothing could tell the user's error from the
  app's; and its user locks are not judged (above).
- **The assembly's own feature tree is not read for errors** (the close review's finding 4): item 11's "nothing of the
  app's in error" reads every mate, every top-level component and every app part's features, not the assembly's
  equations (the Face Z globals) or any other assembly-level feature, the app's or the user's. Reading them would take
  `GetErrorCode2` on top-level assembly features other than components, a read the app has never made and no run has
  measured (which of them reads in error when a component does is not known), so the worker does not add it. An app
  equation in error beside a user component in error would be laid to the user. Rare; said in
  `ASSEMBLY_REBUILD_…`'s comment in `findings.py` too.
- **What's Wrong during an Update on 2024** (`WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_2024` True, 2026
  False): SolidWorks 2024 opened the box during the app's value Update with only the user's mates in error. No app
  behaviour reads the finding; what the app does waits on the user's answer to that §0.3 STOP. On 2024 today the
  Update goes ahead over the user's mates in error, as on 2026.

## 6. Pins moved deliberately

At the fix round (the coordinator's rulings 5 and 8):

- `tests/test_swbuild.py::test_an_unsuppressed_mate_the_record_does_not_know_refuses_the_update_naming_it` (W5's M7
  sentence) and the three cases of `tests/test_swbuild_modes.py::test_a_mate_not_on_record_on_in_a_mode_not_active_
  refuses_before_anything_is_shown` (W8's): the other-kind sentence names the gear and the way through (ruling 5).
- `tests/test_swbuild.py::test_the_w7_put_back_calls_are_pinned_whole`: re-pinned to the 149-call log
  (`W9A_PUT_BACK_LOG`), with the W9a reads taken out still hashing to `W7_PUT_BACK_LOG`.
- The five E4 tests of `tests/test_workbook_modes.py`: each is now the lost-Update case (the assembly marked unsaved
  in the record and loaded from its file, `_lost_update`), every assertion as written; beside them
  `test_e4_a_flag_or_value_the_user_changed_refuses_where_the_record_vouches` asserts K11's refusal.

At the demonstration's ruling (M3 and `nocarrier` on 2026) and its addendum:

- `test_an_unsuppressed_mate_the_record_does_not_know_refuses_the_update_naming_it` (W5): `NO_CARRIER` measured on
  2026, so the sentence now offers the lock as it stands ("lock your component to G1 instead, and Update SolidWorks
  puts it with G1, or suppress Angle1").
- The three cases of W8's `test_a_mate_not_on_record_on_in_a_mode_not_active_refuses_before_anything_is_shown`: the
  TransferCase's trains are the new `NO_CARRIER_MODES` branch, still unmeasured; the sentence says its words.
- `tests/test_findings.py::test_route_c1s_branches_s0_did_not_measure_are_not_measured_on_either_version`: no longer
  lists `NO_CARRIER` on 2026; adds `NO_CARRIER_MODES`.
- W9a's own: the tie sentence names each mate once (addendum); the K3 log line adds the value set under the feature;
  `test_a_user_feature_the_rebuild_put_in_error_is_named_as_theirs_and_does_not_stop_the_job` passes every part (the
  review's condition 2 reads them all).
- `tests/test_workbook_user_record.py::test_a_value_refusal_stands_in_the_footer_until_the_workbook_asks_what_
  solidworks_holds` (package B's): its premise patched, `USER_MATE_PUT_NO_CARRIER_ON_2026` None as when it was
  written; every assertion as written.

At the round after the closing run (the close review's should-fix points, findings only):

- `tests/test_findings.py::test_w9a_m3_an_assembly_rebuild_with_only_user_mates_in_error_returned_true_on_2026` no
  longer asserts `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2024` None: it is True from 2024's m3 (v24:51), pinned
  by its own test.
