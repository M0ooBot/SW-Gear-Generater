# W9a package A (the worker side of issue #1): what package B may call and rely on

Package A of `ISSUE-1-PLAN.md` §5's W9a, written against the fake from `a648e0a`, reviewed in `W9A-REVIEW-A.md`
(`51b398b`) and revised in one fix round under the coordinator's rulings 1 to 8 on that review (§6 below). Authority:
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
  (each carried pose read again), `_free_to_turn(..., mates_on=)`, `_update_document` (K3).
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
| `user_features_in_error: [UserFeature]` | Each user feature read in error once its document was rebuilt (K3): the user's, never a failure. |
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
`PROBLEM_VALUE` (K11, with `ValueEdit(document, name, live, wanted, recorded, mode, cell)`), `PROBLEM_OTHER_KIND`,
`PROBLEM_LOCK_BY_MODE`, `PROBLEM_TWO_BODIES`, `PROBLEM_TIE` (read by SolidWorks, or a lock chain to the ground: its
sentence says which), `PROBLEM_UNSETTLED` (a finding route (c1), one of its branches, or the tie read rests on is
missing), `PROBLEM_COMPONENT` (a component route (c1) would put is suppressed or lightweight), `PROBLEM_UNREAD` (a user
mate SolidWorks would not describe).

**Schema 7 must hold**, per refused or finished job, with `read_at`: the inventory (per part path the user's features;
the user's components; the user's mates with kind, touches, on and code) and, for a refused press, its `problems`
(kind, sentence, mates, values). A tie is a solver read: B cannot recompute it, so the recorded refusal is what the
footer says until the next press reads again. Another `BuildError` met earlier in the check (a `NotAsBuilt`, a missing
finding) carries no inventory: the user's work is read at the end of the check phase.

### 2.3 Predicting a press before it is made (the footer)

`judge_user_work(work, modes, put, *, file, trains, mated, read_tie=None, branches, revision) -> UserJudgement` is the
worker's own judgement, pure. Called with `read_tie=None` it reads nothing and lists in `unread_ties` each train a tie
would be read on. B calls it on the recorded inventory with `put` the bodies a press would put (every mated body of
the gearbox for a gearbox with modes, which ruling 9.18 puts whole whenever it changes anything), `branches =
user_carry_branches(plan.motion, plan.placements)` and the revision last seen, and says `carried` (gear -> [(component,
locks)]) and `problems` before the press. `user_carry_branches` and `user_branch_settled` are pure too.

**The build job's read of the old assembly** (§2.1 item 8) has no worker entry point in W9a: `_read_user_work` reads
the assembly an Update has open. Its worker-side counterpart is written in W9d. W9a's Build again… clause reads, from
the record, the inventory the last Update or refusal kept, with its `read_at`, and says it as read at that time.

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

1. **Route (c1) only where S0 measured it**, on a train with a carrier. Every other branch is its own finding,
   `findings.USER_MATE_PUT_<NO_CARRIER|HELD_GEAR|FIXED_GEAR|SUBASSEMBLY>_ON_<year>`, None on both versions, and
   refuses naming the user's lock until set True (ruling 4; the sub-assembly branch is mine, beside the three the
   ruling names). The rigid motion is read after the app's locks (and a carrier train's gear mates) are off and the
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
11. A part rebuild failing only on the user's features is not a failure while
    `findings.WHATS_WRONG_OPENS_ON_PART_REBUILD` is False; an assembly rebuild failure stays one, naming what of the
    user's was in error before (M3 unmeasured).
12. A user item newly in error is a failure as the user's in the mode active at the check; elsewhere listed only.
13. "The app's own mates leave it free" is taken from the record.
14. K1 on the motion path only; the layout renamed in SolidWorks is still the app's, by its part.
15. A mate's kind is `findings.MATE_LOCK` / `MATE_GEAR` against `IMate2.Type`, plus the motion types; anything else is
    "other". **A mate not wholly read refuses whenever anything is put** (ruling 2); a quiet press puts nothing.
16. A component's state per mode is not read (S5's); a carried component suppressed or lightweight in the active
    configuration refuses.

## 5. Gaps package B must say, not hide

- **The static (W4) path judges no user mate** (review point 15): a user lock to a static gear Update re-places is
  re-taken silently, as before W9a. Every gearbox since W5 turns; B's words should not promise otherwise.
- **The user's assembly-level features** (cuts through a gear, component patterns) are not read (point 16): an
  assembly rebuild failure they cause is said as the app's, but for the "already in error" clause. The inventory is
  not complete.
- **Per mode**, only the active configuration's component states and user mate errors are read before (point 17).

## 6. Pins moved at the fix round, deliberately (the coordinator's rulings 5 and 8)

- `tests/test_swbuild.py::test_an_unsuppressed_mate_the_record_does_not_know_refuses_the_update_naming_it` (W5's M7
  sentence) and the three cases of `tests/test_swbuild_modes.py::test_a_mate_not_on_record_on_in_a_mode_not_active_
  refuses_before_anything_is_shown` (W8's): the other-kind sentence names the gear and the way through (ruling 5).
- `tests/test_swbuild.py::test_the_w7_put_back_calls_are_pinned_whole`: re-pinned to the 149-call log
  (`W9A_PUT_BACK_LOG`), with the W9a reads taken out still hashing to `W7_PUT_BACK_LOG`.
- The five E4 tests of `tests/test_workbook_modes.py`: each is now the lost-Update case (the assembly marked unsaved
  in the record and loaded from its file, `_lost_update`), every assertion as written; beside them
  `test_e4_a_flag_or_value_the_user_changed_refuses_where_the_record_vouches` asserts K11's refusal.
