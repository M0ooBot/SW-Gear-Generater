# Review of W9a package A: the worker side of issue #1

*Independent, 2026-11-16. I started no SolidWorks or Excel and changed no source, test or document. I ran single
test files, the whole suite once (7 failed, 3349 passed, 1 skipped, as expected), and a handful of throwaway tests in
the scratchpad, outside the repo, against the repo's own fake. This file is the only one I wrote.* Under review:

| what | where |
|---|---|
| the reads | `e5e8ee1`: `swcom.py` (`components`, `mate_info`, `feature_states`), `tests/test_swcom.py` |
| the worker | `1c789f6`: `swbuild.py`, the fake in `tests/test_swbuild.py`, `tests/test_swbuild_user_work.py` |
| planning | `ccb2a4e`: `workbook/update.py`, `tests/test_workbook_user_work.py` |
| the interface note | `381eda7`: `docs/notes-workbook/W9A-INTERFACES.md` and its sixteen judgement calls |
| lightly | `d086705`, `c5cb163` (the coordinator's), `1cc0bf6`, `1a6370a`, `ba06c4f` (the S0 review's points) |

I read ISSUE-1-PLAN §0, §1, §2.1, §4's M1 to M3, §5's W9a and *Changes after S0 and its review*; `W9-S0.md`; the W9
S0 section of `findings.py`; the handoff's *Rules carried over*; the whole `git diff a648e0a..381eda7`; and the
code around it (`_motion_assembly`, `_modes_assembly`, `_modes_put`, `_put_train`, `finish_update`, `clear_saved`).
Line numbers are `HEAD` (`381eda7`).

**Verdict.**

- **The shape is right and most of it holds.** Every write the package adds to an item not on record is one
  `place_component` in `_put_carried`. Route (c1)'s order in a carrier train matches S0's `put_c_job`. Every refusal
  but the per-mode tie (which the plan allows to stop part way) is raised before the first write, all at once. K11
  compares like with like (the record keeps each global in the file's own unit). The tests mostly test what their
  names say, and they can fail.
- **But it is not ready for the demonstration.** Four points must be fixed first:
  - A housing mated or locked to a planetary's held Ring refuses every changing press, although nothing puts the
    Ring (1).
  - A user mate whose type or entities SolidWorks would not give is let through as harmless. An unreadable lock
    leaves its sprocket behind, which is the silent re-take S0 found (2).
  - K11 is off for every document an earlier, still-unsaved Update touched. In the ordinary session, the user's
    Bore is set back without a word (3, needs a ruling).
  - Route (c1) is applied where S0 did not measure it: a train without a carrier, held gears and fixed gears (4,
    needs a ruling).
- **Two points must be fixed before package B.**
  - The interface note does not give B what K4 needs: the refusal recorded, and a pure prediction of what a press
    would carry (5).
  - The fake does not fail on a stray put of a user component, which the plan's tests require (6).
- **The six failing tests are no regression.** The pinned hash holds once the seven new reads are removed. The five
  E4 tests fail only on K11's refusal, as the plan requires. The coordinator's intended re-pin of the first is right.
  The intended re-make of the five through a workbook edit is not, for one of them; marking the assembly unsaved in
  the record keeps every assertion (§ *The six tests*).
- **The light commits are sound.** I found one stale exception in the plan's §0.3 (point 18) and one cosmetic nit.

---

## Points

**1. Must fix before the demonstration: a held or fixed app gear counts as "may put" and as a tie's anchor even when
nothing puts it, so a housing on a planetary's Ring refuses every changing press.**

- *What the code does.* With modes, `may_put = set(gears)` whenever the press changes anything
  (`swbuild.py:5321`). That set includes every fixed and held gear. Without modes, `_may_put` takes whole trains
  (`:5235-5254`), and a train includes its held gears.
  - `_judge_user_work` then refuses any user mate other than a lock that has an entity on such a gear (`:5141`).
  - It calls a lock chain from such a gear to the ground a tie (`:5095`, `:5187`).
  - Yet the change phase re-places a held or fixed gear only when it is off its frame: `_put_train` (`:6079-6083`),
    and the fixed-gear branches of `_modes_put` (`:4653-4657`) and `_motion_assembly` (`:5916-5920`).
- *Reproduced on the fake.* Take the turned `Planetary_4to1` (`_planetary_turned_and_pressed`, where `Ring` is both
  fixed and held). Add a fixed `Housing-1`.
  - A user lock from it to `Ring` refuses as `PROBLEM_TIE`.
  - A concentric from it to `Ring` refuses as `PROBLEM_OTHER_KIND`.
  - In both runs the Ring itself is not put (`result.placed[0]` is the carrier).
- *Why it matters.* The plan's words are "every gear of a mated train" (§2.1 item 3). A housing mated to the ring
  gear is the most natural mate a user makes on a planetary, so the rule refuses the user's ordinary case. The tie
  sentence also says "SolidWorks reads it as unable to turn" when nothing was read.
- *What to do.*
  - Count a fixed or held gear in `may_put` only when it is off its wanted frame (whole pitches allowed, as
    `_put_train` judges it).
  - Make a lock chain from the ground to a fixed or held gear that will not be re-placed no tie. Where it will be
    re-placed, keep the refusal, since the lock would re-take.
  - Give the unread tie its own sentence ("your Lock9 holds Sun to Housing-1").
  - Add both cases to the tests.

**2. Must fix before the demonstration: a user mate SolidWorks would not describe is judged harmless.**

- *What the code does.*
  - `Session.mate_info` (`swcom.py:2504-2523`) gives no entities when `GetMateEntityCount` does not answer.
  - It gives `""` (the assembly's own) both when `ReferenceComponent` is None and when the entity itself is None.
  - `_read_user_work` turns `""` into `(ASSEMBLY, "")` (`swbuild.py:4952-4960`).
- *What follows.*
  - A mate with no entities touches nothing. Its type then does not matter: the other-kind refusal needs a put
    body among `gears()`, and the train walk needs an entity on the train.
  - A lock with no entities joins no cluster.
  - An entity that would not answer counts as the assembly: ground for a lock, nothing for any other kind.
- *Reproduced on the fake.*
  - A user gear mate from `Sprocket-1` to `gear1-1`, its `MateInfo` unread: the moving Update ran and put G1 to G4,
    and the mate was listed as `other` touching nothing.
  - A user lock from `gear1-1` to `Sprocket-1` with its entities unread: `carried == []` and `user_puts == []`. On
    SolidWorks that is route (a), the lock silently re-taking the put's offset.
- *Why it matters.* `swcom.py`'s own comment says each read "answers what it could not read rather than guessing".
  The judgement then guesses "touches nothing". M1 is unmeasured on 2026.
- *What to do.*
  - Give an entity that would not answer, and a count that would not answer, an unread marker distinct from the
    assembly's `""`.
  - When a press may put anything, refuse every user mate that is on in some mode and was not wholly read, naming
    it: SolidWorks would not say what it joins.
  - Test both.

**3. Must fix before the demonstration, and needs a ruling: K11 is off for every document an earlier Update changed
until it is saved, so in an unsaved session the user's edit is set back silently.**

- *What the code does.* `classify` gives `recorded=None` for every part, layout or carrier in `record.unsaved` or
  `record.mismatched` (`update.py:556-562`). It sets `record_holds=False` when the assembly is marked
  (`update.py:638`). Every Update marks everything it changed as unsaved (`finish_update`, `:1697-1700`). The
  window's `clear_saved` drops a mark only once the file on disk is newer.
- *Reproduced through the round trip on the fake* (`fake_build`, `press`).
  - Update 1 sets G2's Bore to 13. The part is marked unsaved and stays open, as it does in SolidWorks.
  - The user then types Bore Diameter 14 in SolidWorks.
  - Update 2 changes G2's Backlash. It runs, and `parts[1].changed == ['Bore Diameter', 'Backlash']`: the user's 14
    is set back with no word.
  - The same holds for the assembly: after any Update that put a gear, a Face Z, a slide value or a recorded mate's
    flag the user then changes is set back, which is D10 living on.
- *Why it matters.*
  - Update never saves, so "press, keep working, press again" is the ordinary session. K11 is then off on exactly
    the documents the user is working in.
  - K11 is the user's own answer. Its exception reads "not explained by a lost or unsaved Update". An unsaved Update
    whose document is still open in SolidWorks explains nothing: memory holds what the record says. Only a lost one
    (closed unsaved, then reloaded from its file) does.
  - The demonstration's "a Bore Diameter typed in SolidWorks refuses naming the cell" may well come after a value
    Update to the same part. It would then pass silently.
- *What to do (ruling).*
  - Let the worker decide what `classify` cannot. Hand it the record's word and the mark both.
  - A marked document counts as vouched for when it was open before the job (`result.open_before`, as
    `_earlier_update` already tells `UPDATE_NOT_SAVED` from `UPDATE_LOST`, `update.py:1708-1727`) and reads
    modified (`GetSaveFlag`).
  - Only one reloaded from its file is unsure.
  - The coordinator should rule on the discriminator. A document the user closed unsaved and reopened by hand reads
    open but unmodified, which this rule treats as lost. That is the safe side.

**4. Must fix before the demonstration, and needs a ruling (judgement call 1): route (c1) is applied where S0 did not
measure it.**

- *What S0 measured.* S0 measured (c1) on RangeBox's one train with a carrier. The route
  `findings.USER_MATE_PUT_ROUTE` describes has "the app's locks, gear mates and couplings on there suppressed and the
  assembly rebuilt" before any put (`findings.py:1536-1540`).
- *What the code does.* `_put_train` suppresses gear mates only `if carriers` (`swbuild.py:6037`). It carries user
  components on every put (`:6077`, `:6098`):
  - a train with no carrier, put with its gear mates on;
  - a held gear re-placed first by `REPLACE_FIXED_ROUTE`;
  - a fixed gear re-placed W4's way in `_motion_assembly` (`:5922-5929`) and `_modes_put` (`:4662-4669`), where
    unfix, put and fix follow each other with the user's lock on.
- *Why it matters.*
  - None of these is S0's sequence. The judgement call's own words admit it.
  - The demonstration as planned runs on RangeBox, so it will not exercise them.
  - The fake exercises only the no-carrier T train, and the fake does not model a gear mate fighting a put. No test
    reaches the held-gear or fixed-gear branches with a carried component.
- *What to do (ruling).* Either:
  - refuse (`PROBLEM_UNSETTLED`, naming the lock) a carried component on a train without a carrier, or on a fixed or
    held gear, until measured; or
  - add such a case to W9a's demonstration (the 12 : 1 reducer has no carrier) and keep the refusal until it reads
    clean.
- *Also unmeasured.* Moving a user **sub-assembly** carried as one top-level component. Route it the same way.

**5. Must fix before package B: the interface note does not give B what K4 needs.**

- *The refusal is not in the record.*
  - K4 says what would refuse "makes the press refuse before any change and is recorded, so the footer then says
    it".
  - §3's list of what schema 7 must hold has the inventory but not `UserWorkRefused.problems`.
  - A tie is a solver read, so B cannot recompute it from the inventory.
  - Add the problems (kind, sentence, mates, values) with `read_at`.
- *B cannot predict what a press would carry.*
  - The footer must say "before the press … which of the user's components it would put with their gears". But
    `UserWork.carried` is what *this* press's `may_put` carried, so it is empty after a quiet press.
  - B can only recompute it by copying `_judge_user_work`'s clusters, and two copies of that logic will drift.
  - Expose a pure function over `UserWork` (which components each gear would carry, and which mates would refuse
    if that gear is put). Have the worker call it too.
- *Smaller.*
  - §2 says the mates on are in `user_work.mates`. They are all there, suppressed or not.
  - The build job's read of the old assembly (§2.1 item 8, package B) has no entry point: `_read_user_work` needs a
    `MotionUpdate` and a result. Say in the note who writes it.

**6. Must fix before the demonstration: the fake does not fail on a put of a user component outside route (c1).**

- *What the plan asks.* §5's tests say "the fake fails on any other move of a user component".
- *What the fake does.* `FakeSolidWorks.place_component` (`tests/test_swbuild.py:629-636`) records any put of a
  user component in `user_puts` and lets it through. A stray put is caught only in tests that assert `user_puts`
  exactly.
- *Guards missing.* `set_gear_ratio` and `remake_gear_mate` act on a mate by handle and have no `_not_users_mate`
  guard. The guards on `set_mate_suppressed_in` and `set_dimension_in` are present but untested.
- *What to do.*
  - Let the fake accept a put of a user component only when it is locked (on in the configuration shown) to a body
    already put in the same step, or chained to one. Fail anything else.
  - Guard the two gear-mate writes.
  - Extend `test_the_fake_fails_a_test_on_any_write_to_the_users_work_but_a_put` to every guarded call.

**7. Should fix: nothing binds what the change phase puts to what the check phase judged, and nothing reads a carried
component's pose afterwards.**

- *Without modes.* `_motion_assembly` chooses its trains from frames read after the change's rebuild
  (`swbuild.py:5893-5905`, "moved", "in step"). `_may_put` chose from the frames read before, and does not count a
  part's change as moving anything (`:5305`).
- *With modes.* The quiet-press test (`_may_put` with the active mode's joins) and `_modes_put(judge_only)` (joined
  over every mode) are two codings of one rule.
- *What I could and could not show.* I found no case on the fake where they disagree, and I cannot tell whether
  SolidWorks' rebuild after a part change ever moves a mated gear. If it ever does, a user lock on that train is not
  carried and silently re-takes, as S0 found.
- *What to do.*
  - Carry the judged set in `_UserPlan`. Before any put of a body outside it that has user work on its train or in
    a lock cluster, stop with a failure naming it.
  - After the puts, read each carried component's pose in its gear's frame against the pose before, which is S0's
    own check. A component left behind then becomes a failure, not silence.

**8. Should fix (judgement call 10): which features are the app's is decided by today's plan, not by what the record
lists.**

- *What the code does.* `classify` hands `made = plan_features(job.plan)` (`update.py:278-280`). `_user_features`
  (`swbuild.py:4863`) treats every feature after the first match as the user's unless today's plan names it.
- *What K1 says.* "What the record lists". Each part's `.gear.json` keeps the features the build actually kept
  (`GearRecord.features`, `store.py:53`).
- *Why it matters.* On a part built by an older version whose feature names differ:
  - the old-named app features are listed as "your features";
  - one of them in error after the rebuild counts as the user's, so `_update_document` (`:3634-3644`) excuses the
    failed rebuild. An app failure is then said as the user's and does not stop the job.
- *What to do.*
  - Take `made` as today's plan together with the sidecar's recorded features.
  - Excuse a failed part rebuild only when every feature in error is in neither.

**9. Should fix (judgement call 6): rack-and-pinion, screw, linear coupler and cam mates re-phase on a put as a gear
mate does.**

- *What the code does.* `geared` (`swbuild.py:5142`) refuses only `USER_GEAR` on a carried component.
- *Why it matters.* A carried sprocket driving the user's rack through a rack-and-pinion is the same silent re-phase
  that `MESH_PHASE_ROUTE` describes.
- *What to do.* Judge `swMateType_e` 9, 13, 17 and 18 (cam follower, rack and pinion, screw, linear coupler) as
  `USER_GEAR` for this rule.

**10. Should fix: a tie decided without a read is worded as a read.**

- *Where.* The grounded-cluster refusals (`swbuild.py:5174-5176`, `:5187-5190`) use `_tie_sentence`.
- *What it says.* "SolidWorks reads it as unable to turn", although no `constrained_status` was made.
- *Why it matters.* It is the plan's sentence for the solver read, and here it is not true.
- *What to do.* Give the lock-chain case its own sentence naming the ground it reaches. This goes with point 1.

**11. Should fix, and needs a ruling (judgement call 8): the other-kind refusal keeps W5's M7 sentence and never tells
the user the way through.**

- *What changed after S0.* A sprocket mated to Sun's hub by concentric and coincident, which is how most users mate
  one, now refuses.
- *What the plan says.* The first requirement says the ordinary case "goes through Update, not that it is refused
  with a better sentence". After S0 the only way through is a lock.
- *What the sentence says.* "Suppress Gear5", which leaves the sprocket free.
- *What to do.* Say that a lock between their component and the gear goes through, and that the app puts it with
  the gear. Keeping the W5 and W8 pins is not a reason to withhold that. The coordinator should rule on moving those
  pins.

**12. Should fix: K11's cells.**

- *A shared part.* `_gear_cells` (`update.py:583-595`) names the first gear's row only. For a part shared by two
  rows (G1 and G3), typing the value in that one cell splits the shared part, which is structural (Build again…).
  Name every row's cell.
- *A formula global.* One with no cell (Pitch Diameter, say) is told "change the workbook to 21.5"
  (`_value_sentence`). No cell holds it. Say it can only be set back in SolidWorks.

**13. Should fix: tests the plan or the code calls for that are not there.**

- `PROBLEM_COMPONENT` (a carried component suppressed or lightweight) has no test.
- No test covers a user lock between two *trains*. `test_a_user_lock_holding_two_of_the_apps_gears_together`
  locks G1 to G4, which are one train on the T fixture. The code does not tell the cases apart, but the plan names
  the two-train mate.
- No test covers a carried component on a held or fixed gear (point 4).
- No test covers unread entities (point 2).
- No test covers a leaf in a user sub-assembly (`owner`'s `split("/")`).
- No test covers K11 on a radians document.
- No test covers K11 through `classify` on E4 with the record vouching: the five tests below, made the other way.

**14. Note: a renamed layout component is listed as the user's.**

- *Where.* `layout_names` is the recorded `Name2` when there is one (`swbuild.py:4945`).
- *What follows.* A layout renamed in SolidWorks then becomes one of "your components", fixed, so it is ground. It
  stays harmless for every judgement but the inventory's word.
- *What to do.* Fall back to the layout's path when the recorded name is not among `components()`.

**15. Note: the static (W4) path judges no user mate at all.**

- *What happens.* A user lock to a static gear that Update re-places by unfix, put and fix re-takes silently.
- *Is it new?* No. It was so before W9a, and the plan holds that every gearbox since W5 turns.
- *What to do.* The interface note says it. Say it to the user too, or refuse an unrecorded mate on a static
  assembly whose gear would be re-placed.

**16. Note: the user's assembly-level features are not read.**

- *What is missing.* Cuts through a gear, component patterns: none is read.
- *Is it allowed?* Yes. The plan defers carrying them, and M3 is open.
- *What follows.*
  - An assembly rebuild failure they cause is said as the app's, with only the "already in error" clause for
    mates and components.
  - B's footer must not call the inventory complete.

**17. Note: per-mode state is read in the active configuration only.**

- *What is missing.* A component's state per mode is not read, and neither is a user mate's error before the
  change in any mode but the active one.
- *Is it allowed?* Yes: S5 is W9d's, and judgement calls 12 and 16 say so.
- *What follows.*
  - A user mate the Update put in error in another mode is a `CHECK` in `user_in_error`, never a failure. B must
    show it with its mode.
  - A carried component suppressed in another mode only makes that mode's put fail part way. It is not silent.

**18. Note (on `1cc0bf6`): the plan's §0.3 still allows route (b).**

- *Where.* ISSUE-1-PLAN line 81 still lists "route (b)'s suppression of the user's mates around a put" as an
  exception to the STOP.
- *Why it matters.* Route (b) is ruled out (K2's *Instead of*), and the exception widens what an implementer may
  write.
- *What to do.* Drop it at the next plan touch.

**19. Note (nit, on `d086705`).** `keep_awake` prints `SetThreadExecutionState`'s DWORD through ctypes' default
`c_int`, so run 4's log reads "previous state -0x80000000". It is harmless.

---

## The judgement calls

| # | Within the plan? | Ruling |
|---|---|---|
| 1 | No: (c1) beyond S0 (no carrier, held, fixed) | **Needs one** (point 4) |
| 2 | For mated trains yes; held and fixed gears counted when not put, no | Fix (point 1) |
| 3 | Yes (K2: a lock whose flag differs by mode refuses) | — |
| 4 | Conservative extension (any two app bodies). The sentence "puts each back to its own built place" is wrong for a pair the app locks itself, but refusing is safe | — |
| 5 | Right for mated gears (a lock is rigid). Wrong for held or fixed gears not re-placed; wording | Fix (points 1, 10) |
| 6 | A sound extension | Extend to the other motion mates (point 9) |
| 7 | Yes | — |
| 8 | Keeps pins at the cost of the plan's first requirement | **Needs one** (point 11) |
| 9 | The data route is fine; treating every unsaved mark as unsure is wider than K11's "lost or unsaved Update" | **Needs one** (point 3) |
| 10 | No: K1 says "what the record lists" | Fix (point 8) |
| 11 | Yes (§2.1 item 5, gated on `WHATS_WRONG_OPENS_ON_PART_REBUILD`) | — (see point 8) |
| 12 | Yes | B must show `user_in_error` |
| 13 | Yes (K2: "from the record") | — |
| 14 | Acceptable; the static path is legacy | Say it (point 15) |
| 15 | Yes for the type | Unread entities, point 2 |
| 16 | Yes (S5 is W9d's) | — |

---

## The six tests

All six fail as the implementer says, and none shows a regression.

- **`test_the_w7_put_back_calls_are_pinned_whole`.**
  - *What I found.* The log is 149 calls. The added ones are `feature_states` at indices 2, 6, 10, 14, 18 and 22
    (one per part document read with `made`) and one `components` at 71. With every `components`, `feature_states`
    and `mate_info` call removed, the 142 calls left hash to `W7_PUT_BACK_LOG` exactly, so no other call moved.
  - *The intended re-pin.* It is right. Keep the old hash asserted on the filtered log, so a later change to the W7
    sequence is still seen apart from W9a's reads.
- **The five in `test_workbook_modes.py`.**
  - *Why they fail.* Each raises `UserWorkRefused` with K11's sentence and nothing else:
    - three with "The mate ModeSlv engages FrontDog is suppressed in 4H in SolidWorks, …";
    - two with "RangeSlv along Rear in TransferCase_E4 in 2H is 50 mm in SolidWorks, …".
    K11 refuses exactly the edits these tests make in the fake, and the plan requires it ("overturning D10").
  - *What passes them.* They pass unchanged with `record_holds` forced False. They also pass through `classify`,
    every assertion unchanged (the full status sentences included), when the record carries an `unsaved` or a
    `mismatched` mark on the assembly before the press: the lost-Update case, where W8's set-back still serves.
  - *The intended ruling is not right for all five.* It would re-make the Updates by a workbook edit.
    - A workbook slide edit sets `result.slid`, so `_modes_assembly`'s `moved` is True (`swbuild.py:4488`) and
      every train is put in every mode. That contradicts `put_in == []` in
      `test_e4_a_flags_or_values_update_of_a_gearbox_nobody_turned_puts_nothing[value]`.
    - The status pieces ("turned … back on in 4H", "set RangeSlv's place in 2H back to 46 mm, where it had been
      changed in SolidWorks") would change in the others.
  - *What I recommend.*
    - Put an `unsaved` (or `mismatched`) mark on the assembly in the record before each press. That is the case the
      set-back still exists for, and all five assertions hold as written.
    - Beside them, add the vouching variant through `classify` that asserts the K11 refusal on E4.
    - A J14 workbook edit may be added for `[flag]`, as a third variant.

---

## What I checked and found right

- **Writes.** The only write to an item not on record is `_put_carried`'s `place_component`. Every
  `set_mate_suppressed(_in)`, `set_dimension_in`, `fix` and `unfix` targets recorded names or placed gears. Nothing
  is saved, and no user configuration is shown.
- **Route (c1) in a carrier train.** It matches S0's `put_c_job`:
  - the app's locks and gear mates off and a rebuild;
  - the gears and the user components read (`_carried_before` after the rebuild);
  - the held gears, then the carriers, then the rest put;
  - the user components put after every app body of the step;
  - then the mates back on.
  `_carry_frame` is `G_target · G_before⁻¹ · U_before` (its test can fail).
- **Refusals.** Every refusal is raised at the end of the check phase, before `_evaluates`'s writes, all problems at
  once, values first. The per-mode tie is read after the show and rebuild and before that mode's put, as K2 and S0's
  C2 require, and its test checks it.
- **Ground.** The ground is a node per lock, so two sprockets locked to one housing are two ties, not one cluster.
  User–user and user–layout mates never refuse. A lock on in no mode is listed in `extra_mates` as before.
- **K11.**
  - The record keeps each part's globals in the file's own unit (`finish_build` and `finish_update`, as
    `expression_for(trig)`).
  - The recorded Face Z is the build's own literal (`motion.py:902`).
  - A lost Update (the file closed unsaved) keeps its mark through `clear_saved`, so it is not refused.
  - A user value equal to what the workbook now asks is no conflict.
- **K1.** A renamed component is found by its part only when exactly one unclaimed instance is in the assembly. The
  new name reaches the change phase and the record (`finish_update`, gear and carrier).
- **Findings.** Read with `getattr`. A missing `USER_MATE_PUT_ROUTE`, `USER_TIE_RULE` or
  `WHATS_WRONG_OPENS_ON_PART_REBUILD` refuses or keeps the failure, with a sentence.
- **The inventory on the fake.** For the planetary and E4 it lists no app component as the user's.
- **`d086705`.** The JSON is written after each case and first in the `finally`, `propose()` runs there, and the
  close catches any exception.
- **`c5cb163`.** The finding, its comment and its test agree with run 4's log (lines 54, 59 and 75 as cited; 502 s;
  `done 0 failed`). `tests/test_findings.py` passes (130).
- **`1cc0bf6`, `1a6370a`, `ba06c4f`.** They take the S0 review's points as that review asked, but for point 18.

## What I could not verify

- **Nothing on SolidWorks.** I could not check:
  - M1: `ReferenceComponent` on 2026, a leaf's `Name2` as a path, `None` for the assembly's planes;
  - M2: a top-level `GetErrorCode2` walk marking nothing;
  - M3;
  - `FeatureByName(Name2)` giving a component's tree feature.
- **Untested on SolidWorks.** Whether (c1) holds with a train's gear mates on or across a fixed gear's unfix, put
  and fix; whether moving a user sub-assembly by `Transform2` holds; whether SolidWorks' rebuild after a part change
  can move a mated gear (point 7).
- **On the fake.** The fake's tie is hand-set (`fake.locks`), so the tie tests check the plumbing, not the solver.
