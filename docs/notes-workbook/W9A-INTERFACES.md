# W9a package A (the worker side of issue #1): what package B may call and rely on

Package A of `ISSUE-1-PLAN.md` §5's W9a, written against the fake from `a648e0a`. Authority: the plan as amended by
*Changes after S0 and its review* (route (c1) is K2's route; every other kind of user mate on a put gear refuses),
then `W9-S0.md` and the W9 S0 findings in `findings.py`. Nothing here touches the window, `ui_text.py`, `gui.py`,
the record's schema or the boards: those are package B's. A change to a shape below is a stop-and-ask, as at W8.

## 1. Where the reads and refusals live

- **`swcom.Session`**, reads only: `components()` → `[ComponentInfo(name, path, fixed, state, code)]` (top level,
  `GetComponents(True)`); `mate_info(handle)` → `MateInfo(name, type, components)` (`IMate2.Type`, each
  `MateEntity(i).ReferenceComponent.Name2`, `""` for the assembly's own); `feature_states()` →
  `[FeatureState(name, type_name, code, warning)]` (top-level tree with `GetErrorCode2`). `UNREAD = -1` for what
  would not answer. None is behind a finding: the plan measures them in W9a's demonstration (M1, M2), whose STOP on a
  `GetSaveFlag` change stands.
- **`swbuild`**, in `update_gearbox`'s check phase (the motion path; the static W4 path reads K11 and the features
  only): `_read_user_work`, `_judge_user_work` (K2), `_user_check` (the end of the check phase, every problem raised
  at once), `_value_edits` (K11, documents), K11 for Face Z / slides / flags in `_update_motion` and `_modes_check`,
  `_find_by_part` (K1). In the change phase: `_put_train(..., carried=)` and `_put_carried` (route (c1)),
  `_modes_tie_read` (a mode whose user flags differ, read when shown, before its put), `_mate_problems(...,
  user_before=, user_found=)`, `_components_after`, `_free_to_turn(..., mates_on=)`, `_update_document` (K3).
- **`workbook/update.py`**: `classify` fills what the worker needs (§3); `finish_update` writes a component found by
  its part into the record by the name found.

## 2. What the worker returns (B may rely on these shapes)

**On a result** (`GearboxUpdate`, motion path):

| Field | Meaning |
|---|---|
| `user_work: Optional[UserWork]` | The user's work as read before anything changed; `None` when the assembly was not read. On the static path, a `UserWork` holding only `features` (or `None`). A `UserWork` is falsy when it holds nothing; test `is not None` for "read". |
| `carried: [(component, gear, configuration)]` | Each put of a user component with its gear (route (c1)), in the order put; configuration `""` with no modes. |
| `renamed: [(gear, Name2 on record, Name2 found)]` | K1. `finish_update` already records the found name (`ComponentEntry.name`, a carrier's `CarrierEntry.component`); no schema change. |
| `user_in_error: [(mode, name)]` | Each user mate or component read in error after the change (mode `""` with no modes), those in error before included. |
| `user_features_in_error: [UserFeature]` | Each user feature read in error once its document was rebuilt (K3): the user's, never a failure. |
| `extra_mates` | Unchanged meaning: the user's mates suppressed in every mode (the ones on are in `user_work.mates`). |

`UserWork(read_at, components, mates, features, carried)`; `read_at` is `store.now()`'s UTC stamp; `in_error` (a
property) names every user mate, component and feature found in error before the change (`"Keyway in
Gear_m1.25_N17.SLDPRT"` for a feature). `carried` there is `(component, gear, the user's locks that hold it)`: what
route (c1) would put, judged before the press — the footer's *"it turns your Sprocket-1, which your Lock3 holds to
Sun"*.

- `UserComponent(name, path, fixed, code, state)` — a top-level component not on record.
- `UserMate(name, kind, type, touches, on, code, warning)`; `kind` is `USER_LOCK`, `USER_GEAR` or `USER_OTHER`;
  `touches` per entity `(what, name)` with `what` one of `APP` (name a gear or carrier id), `LAYOUT`, `ASSEMBLY`
  (`name` `""`), `USER` (a top-level Name2; a leaf in a user sub-assembly is named by its top level); `on` the modes
  it is on in, in mode order (no modes: `("",)` on, `()` suppressed); `gears()` and `components()` helpers.
- `UserFeature(path, name, type_name, code, warning)`.

**On a refusal**: `UserWorkRefused(BuildError)` before any write, `str()` every sentence joined;
`.problems: (UserProblem(kind, sentence, mates, values), …)` in the order values first, then mates; `.user_work`, the
inventory as read (for the record a refused job writes, K4). Kinds: `PROBLEM_VALUE` (K11, `values` holds the
`ValueEdit`s), `PROBLEM_OTHER_KIND`, `PROBLEM_LOCK_BY_MODE`, `PROBLEM_TWO_BODIES`, `PROBLEM_TIE`, `PROBLEM_UNSETTLED`
(a finding route (c1) or the tie read rests on is missing), `PROBLEM_COMPONENT` (a component route (c1) would put is
suppressed or lightweight). `ValueEdit(document, name, live, wanted, recorded, mode, cell)`: numbers as text; a
flag's values are `"on"` / `"suppressed"`. Another `BuildError` met earlier in the check (a `NotAsBuilt`, a missing
finding) carries no inventory: the user's work is read at the end of the check phase.

**Failures** the change phase adds (as `(file, sentence)` in `failures`): a tie in a mode read only when shown
(*"In mode L, Update SolidWorks must turn …"*; the job stops there, what was changed said, as any change-phase
failure); *"Your mate X is in error in SolidWorks, and was not before this Update."* (and the same for a component);
a gear's *"cannot turn"* sentence with *"; your Lock3 and Coincident7 are on its train."*; a failed assembly rebuild
with *" Your Lock3 was already in error before this Update."*.

## 3. What the worker needs from planning (`classify` fills it; defaults keep W8's behaviour)

- `DocumentValues.recorded`: `(global, expression)` as the record says the file holds it; `None` judges nothing.
  `classify` gives `PartEntry.variables`, the layout's globals from the recorded shafts and a carrier's from its
  recorded axes, each `None` where the file is in `record.unsaved` or `record.mismatched`.
- `DocumentValues.cells`: `(global, cell)`; `DocumentValues.made`: the plan's feature names (`swbuild.plan_features
  (plan)` for a part; `layout_features` for the layout and a carrier).
- `Placement.part`: the component's part (`ComponentEntry.part`, a carrier's path), for K1.
- `MotionUpdate.layout_component`, `record_holds` (no unsaved or mismatched mark on the assembly), `recorded_faces`
  (`(gear row, |z_front|)` of each along mate with a Face Z), `cells` (a Face Z global's or a slide's name → the
  gear's At or Slides cell).

**What schema 7 must hold for the footer before the press** (B's to shape): per part path the user's features (name,
type, code); the user's components (name, path, fixed, code) and mates (name, kind, touches, on, code); the
components route (c1) would put and by which locks; `read_at`. All of it is `UserWork`'s, as returned on the result
and on `UserWorkRefused`.

## 4. Judgement calls where the plan left room

1. **Route (c1) on every put**, not only a carrier train's: a train with no carrier is put with its gear mates on,
   as W5-W7 put it; a held gear put first and a fixed gear re-placed W4's way carry their user components too. The
   rigid motion is read after the app's locks (and a carrier train's gear mates) are off and the assembly rebuilt,
   as S0's `put_c_job`; the components are put after every app body of the step and before the app's mates go back.
2. **"May put", judged before any change, conservatively.** No modes: a train out of step or off its axis against
   the wanted frames, one whose Face Z changes or whose gear mate is remade, every train when the layout or a carrier
   changes (or a recorded mate is to be turned back on), each fixed gear not where it belongs. With modes: every body
   whenever the press changes anything or would put in the active mode (ruling 9.18 puts every train in every mode
   then), none on a truly quiet press. A user mate on a gear nothing puts never refuses.
3. **Clusters through the user's locks on in every mode.** A lock suppressed in every mode is no tie (listed in
   `extra_mates`); one on in some modes and reaching a put body refuses (`PROBLEM_LOCK_BY_MODE`).
4. **Two bodies, not only two trains:** a cluster holding any two app bodies, one of them put, refuses — a lock
   straight between two gears, or through the user's components. Telling "rigid anyway" pairs apart was not tried.
5. **A lock chain to the ground** (the layout, a fixed component of the user's) is a tie without the read.
6. **A user gear mate on a component route (c1) would put refuses** (the put re-phases it); a mate of another kind
   on such a component (S0's axis mate to the layout) is left on.
7. **The user's mates "on a train"**: those with an entity on a body of the train, and on through the user's floating
   components, of any kind; a fixed one ends the walk. All are named in the tie sentence, each with its modes.
8. **The other-kind refusal keeps W5's M7 sentence word for word** (one sentence per mate, all at once), which keeps
   the W5 and W8 pins on it; finding D (`USER_PLANE_MATE_ON_SLIDER_FOLLOWS`) is not read, as the plan rules.
9. **K11 by data, not by a switch:** `recorded` None / `record_holds` False is W8's behaviour (set back), which is
   also what an unsaved or mismatched mark gives. The cell map covers the literal part globals (teeth, module, bore,
   pressure angle, face width, backlash, fillet, profile shift), shaft X/Y/Z, a Face Z (the gear's At) and a slide (its
   Slides); a carrier's global or a formula global is named without a cell. A Face Z or slide sentence speaks in mm
   and says "change <cell> so the workbook asks …", since neither is typed as is.
10. **The user's features** are the top-level features after the plan's first that are none of the plan's; the
    template's before it are nobody's. The user's assembly features are not read.
11. **A part rebuild failing only on the user's features is not a failure** while `findings.
    WHATS_WRONG_OPENS_ON_PART_REBUILD` is False (P0: such a rebuild returned False and opened no window); an
    assembly rebuild failure stays a failure (M3 unmeasured), its sentence naming what of the user's was in error.
12. **Errors after**: a user mate or component newly in error is a failure as the user's; with modes only in the mode
    active at the check (another mode's state before was never read), elsewhere listed in `user_in_error` only.
13. **"The app's own mates leave it free" is taken from the record** (an assembly is on record only after its
    post-check), never read.
14. **K1 on the motion path only**, and only with exactly one top-level instance of the part that no placement
    claims; the static path is unchanged.
15. **A mate's kind** is `findings.MATE_LOCK` / `MATE_GEAR` against `IMate2.Type`; anything else or unread is "other",
    never a lock.
16. **A component's state per mode is not read** (S5's question); a carried component suppressed or lightweight in
    the active configuration refuses.

## 5. Pins this package moves, left unedited (for the coordinator)

- `tests/test_swbuild.py::test_the_w7_put_back_calls_are_pinned_whole`: the log gains W9a's reads (one `components`,
  one `feature_states` per document the classify path hands `made`): 149 calls for 142. With those reads removed the
  log is the pinned one, hash for hash.
- `tests/test_workbook_modes.py`: `test_e4_a_turn_in_2h_then_a_flags_or_values_update_in_4l_puts_every_turned_mode_back`
  `[flag]` / `[value]`, `test_e4_a_flags_or_values_update_of_a_gearbox_nobody_turned_puts_nothing[flag]` /
  `[value]`, `test_e4_a_turn_put_back_in_the_mode_worked_in_names_the_modes_read_at_the_built_turn`: each makes a
  flags-only or values-only Update by changing a recorded flag or slide value in the fake, which K11 now refuses
  (*"The mate ModeSlv engages FrontDog is suppressed in 4H in SolidWorks, …"*). With `record_holds` False they pass
  unchanged; a J14 edit in the workbook, or an unsaved mark on the assembly, would make the same Update without
  overturning K11.
