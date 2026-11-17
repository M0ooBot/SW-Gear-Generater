# Review of W9a's demonstration script and its note

*Independent, 2026-11-16. I started no SolidWorks or Excel, ran neither script and changed no source, test or
document. This file is the only one I wrote.* Under review: `a05911c` (`probe/w9a_demonstration.py`, new, and the W8
stage of `probe/workbook_window_check.py`) and `dd9e13b` (`docs/notes-workbook/W9A-DEMONSTRATION.md`), read against
the app as it stands at `dc7b4e1`. Line numbers are HEAD's.

I read ISSUE-1-PLAN §0 (§0.3's STOPs above all), §2.1, §2.6, §3, §4, §5's W9a and *Changes after S0 and its review*;
`W9-S0.md` and `probe/w9_user_work_check.py`; `W9A-INTERFACES.md`; `W9A-PACKAGE-B.md`; the parts of `W9A-REVIEW-A.md`
and `W9A-REVIEW-B.md` on what only SolidWorks can show, with B's fix-round re-check; and the handoff's *Rules carried
over*. Beyond reading I ran `py_compile` on both scripts and an AST check, from the scratchpad, that every attribute
the script takes from `W`, `S0`, `findings`, `store`, `swbuild`, `swcom`, `ui_text`, `spur` and the `workbook`
modules exists at HEAD. I also read the three fixture workbooks' cells with `zipfile`.

---

## Verdict

- **The shape is right.** Every Update and Build is the app's own. The sections run alone from kept masters, and the
  run is guarded the way S0's is since `d086705`. Every name the script uses exists at HEAD with the signature it
  assumes. The expected problems in `refuse` are what `judge_user_work` and `_user_check` return at HEAD, the two
  steps the author flagged included. The patched finding cannot leak out of `nocarrier`.
- **But it is not ready for the first run.** Four points must be fixed first:
  - **The `refuse` section dies at its first step (1).** With Sprocket-1 lightweight, the script's own read before
    the press raises. Both of *Done when*'s refusals come after that step in the same section, so neither is shown.
  - **A section-only STOP ends the whole run (2).** That is the outcome the note expects from `again-dirty`, and it
    would cost `again-closed`, `reducer` and `nocarrier`.
  - **One check fails on every run (3).** It asserts the footer turns green once the workbook changes after the
    housing-lock refusal. At HEAD the footer predicts the same refusal again, in red, which is right.
  - **The `again` sections do not show what review B's fix round asked for (4).** The read is made with the old
    assembly as the active document, and nothing records which document is active.
- **Eight should-fix points** make the run prove what it claims. The main ones: judge a refused press by its traced
  calls, not by reads alone (5); measure K3 in an app part, which the 12 : 1 allows (6); check that the inventory
  lists the keyway at all (7); and compare entities, which §0.3 asks for (8).

---

## Findings

**1. Must fix before the first run: the lightweight step raises in the script's own read and ends `refuse`, before
the housing lock, the tie, the two bodies, the Bore and all-at-once.**

- *Where.* `refuse_press` reads before the press: `read_now(...)` at `w9a_demonstration.py:1224`. Its pairs include
  the user's components (`pairs_of(box, rb_users())`), and `read_now` finds each one with
  `s.find_component(f"rn{i}", n)` at `:388`.
- *Why it fails.* `Session.find_component` refuses a lightweight component unless it is passed `lightweight_ok=True`
  (`swcom.py:3435-3438`: *"Sprocket-1 is loaded lightweight in …"*). Sprocket-1 was set to state 1 at `:1341`, so the
  job raises. `run()` turns that into an `AssertionError`, which leaves `section_refuse` through `refuse_press`. No
  step of the section catches it.
- *The cost.* `end_copy` runs, and the section is over. Both of *Done when*'s refusals and review B's housing-lock
  item are lost on every run. They come after the lightweight step at `:1340-1350`.
- *Fix.*
  - In `read_now`, find the user's components with `lightweight_ok=True`. The frame and the constrained status
    still read.
  - Move the lightweight step to the end of the section.
  - Run each refusal step under its own `try` that records a failed check, so one surprise does not take the rest.
- *Worth knowing.* The quiet press before it (`quiet_then_edit`) is not affected: the worker's `_read_user_work`
  never calls `find_component` on a user's component.

**2. Must fix before the first run: `section_stop` ends the whole run, not its section.**

- *Where.* `section_stop` (`:141-144`) calls `W.stop_check(False, what)`, which appends to `W.STOPS`
  (`workbook_assembly_check.py:5360-5366`). After every section, `main` calls `watch_check(name)` at `:1715`. That
  check stops the run whenever `W.STOPS` is not empty (`:151-152`). So the `SectionStop` caught at `:1703-1705` is
  followed at once by a `DemoStop`.
- *Why it matters.* The note says changes in the `again` sections "end only their section" (`W9A-DEMONSTRATION.md`,
  lines 135-144). It even predicts one: *"`again-dirty` sees a rebuild by Sprocket-4 moving 0.5 mm"*. If that
  happens, `again-closed`, `reducer` and `nocarrier` are lost in the default order.
- *Fix.*
  - `section_stop` records a failed check and `RESULT["stops"]`, never `W.STOPS`.
  - Or `watch_check` counts only the STOPs added since the last check that are not the section's own.

**3. Must fix before the first run: the "green once the workbook changes" check (`:1358-1362`) is wrong at HEAD
and fails every run.**

- *What HEAD does.* After the housing-lock refusal, Backlash 0.41 is typed. `user_work_ahead` (`workbook/update.py:2128-2145`)
  sees the refusal on record and the workbook changed since, so it judges again on the inventory as last read.
- *Why it is red.* That inventory is the refused press's own, and it holds `UserHousingLock` on in every mode. The
  cluster {Sun, Sprocket-1, Sprocket-3} therefore holds `Housing-1@UserHousingLock` as ground, and the train loop
  adds a `PROBLEM_TIE` with `_ground_sentence` (`swbuild.py:5357-5364`). `_prediction` then returns red
  (`ui_text.py:4253-4256`). This is ruling 5 working as designed: review B's re-check reproduced the same shape (*"The
  workbook has changed since …"*, then, red, the foreseen refusal).
- *Fix.* Assert three things: `"has changed since"` in the line, `ok` False, and `ahead.problems` being exactly one
  `PROBLEM_TIE` naming `UserHousingLock`.
- *For the coordinator.* Review B's list of what SolidWorks must show still reads "green once the workbook
  changes". It predates ruling 5's fix.

**4. Must fix before the first run: the `again` sections read the old assembly while it is the active document, so
they do not show the read on a document that is not active, which the fix round asked for.**

- *What was asked.* `W9A-REVIEW-B.md`, *What the demonstration must add for the fix round*, asks for the old-assembly
  reads on a document that is not the active one. It also asks for the old assembly behind another document: its
  window stays behind, nothing rebuilds, `GetSaveFlag` is unchanged and no dialog opens. `W9A-PACKAGE-B.md:108-124`
  adds "which document is active" to the things that must be unchanged.
- *What the script does.* At `:1438` it opens the old assembly with `job(old, …)`, which is `in_assembly`:
  `open_document`, and so `ActivateDoc3`. In `again-dirty` it edits there. Then `read_now(..., activate=False)` reads
  it in place, and the build runs. The old assembly is the front document throughout, so `use_open_document`'s
  promise not to activate is never put to the test. The active document is never read, and the note's list
  (`W9A-DEMONSTRATION.md:61-72`) leaves it out.
- *Fix.*
  - After the old assembly is open (and dirtied), bring another document forward, for example `Housing.SLDPRT` by
    `open_document`, and read the active document's path.
  - Then run the app's own `swbuild.read_old_assembly(s, wb_update.old_assembly(desk.record, desk.plan))` alone, as
    one worker job. Read the active document, the old assembly's `GetSaveFlag`, `NeedsRebuild2` and the windows
    before and after it.
  - Then run the build as now. The build activates the documents it makes, so only the read alone can show that
    nothing was activated.
  - Optionally add `ActivateDoc3` to `W.TRACED` for the build and assert that neither `OpenDoc6` nor `ActivateDoc3`
    names the old assembly before the first new document is made.
  - Add the active document to the note's list.

**5. Should fix: a refused press is judged "nothing written" by reads alone, though its call trace is free; and
the note's STOP for a mark after a refusal is only a check.**

- *The trace is thrown away.* `press` (`:350-354`) discards the calls `W.w8_update` returns. A press that shows a
  mode and shows the first one back, suppresses and restores a flag, puts a gear and puts it back, or rebuilds, would
  pass `written()` (`:453-470`). W8's s3 judged refusals by `W.nothing_changed_calls(calls)`
  (`workbook_assembly_check.py:6535-6538`).
- *Fix for refusals.* Keep the calls and assert `nothing_changed_calls(calls) == []` for every refused press.
- *Fix for `go`.* Assert that every traced `put` is an app body or one of `RB_LOCKED`. §0.3's first STOP is
  "anything that would write to … a component … not on record" but for route (c)'s puts. Sprocket-4's distance
  check (`:1113`) would miss a put that writes the same frame.
- *The note overclaims a STOP.* It says (`W9A-DEMONSTRATION.md:127-128`) that a document marked after a refused press
  is a STOP. In the script it is a check (`:1244`). Make it `stop(...)`, or correct the note.

**6. Should fix: K3 in an app part can be shown, and the note's reason for not showing it is wrong.**

- *The note's reason.* `W9A-DEMONSTRATION.md:160-162` says failing a keyway in an app part "takes an app value,
  which K11 refuses".
- *Why that is wrong.* K11 refuses a value typed in SolidWorks, not one changed in the workbook. The 12 : 1's gears
  have bores (G1 8, G2 and G3 12, G4 16; `Gears!J2:J5` of the fixture). A user keyway at (5, 0), Ø3, in G1's part,
  then G1's Bore 8 → 14 in the workbook, is S0's P0 failure reached through an ordinary value Update. Check that
  `classify` makes it an Update first, as `go_press` does.
- *What it would measure.* This is the M3 case that matters to the app (§2.1 item 5: "does not stop the job, if M3
  shows the rebuild reports it"): the Update's own part rebuild returning failure because of a user feature, and
  whether `update_gearbox` lists it in `user_features_in_error` and says *"SolidWorks rebuilt your User Keyway in
  Gear_m1.5_N17 after the app's features, and it is in error."* or stops.
- *What m3 measures instead.* `m3` never has the app rebuild a part holding a failing user feature. Its feature case
  rebuilds the user's own Sprocket part, which the Update does not touch.
- *Fix.* Add a `k3` section on a copy of `reducer.master`, about 5 minutes on 2026. Put it on 2024's list if M3's
  answer is wanted there.

**7. Should fix: M2 and the inventory's features are asserted vacuously.**

- *Where.* `_inventory_checks` (`:973-974`) checks that every feature listed as the user's starts with "User". It
  never checks that the keyway is listed.
- *Why it matters.* If the quiet press does not walk Sun's part, the check passes with nothing listed, and M2 (the
  app's split of its own features from the user's) is unanswered. The first visible failure would then be in
  `again`, three sections later, where `stays.left` holds no keyway.
- *Fix.* Assert that `work.features` is exactly `User Keyway Sketch` and `User Keyway` in Sun's part, and check the
  record's `entry.features` after each `go` press.

**8. Should fix: §0.3's "every user item's flag, error code and entities before and after" is not met for
entities.**

- *The rule.* §0.3 ends: "on SolidWorks each demonstration compares every user item's flag, error code and entities
  before and after, in the old assembly as well after a Build again…".
- *What the script compares.* `go` compares flags (`:1121-1123`) and codes. The `again` sections compare codes,
  flags and frames. No user mate's entities (`mate_info`'s components) are read after a press or after the build.
- *Fix.* Read `mate_info` for the eight user mates before and after each `go` press, and on the old assembly before
  and after the build, and compare.

**9. Should fix: `Desk9` drifts from the window in small ways, and could call the window's own methods instead.**

Line by line against `workbook_gui.py` at HEAD:

- *`plan_solidworks` (`:195-219`) against `_plan_solidworks_pass` (`:710-760`).*
  - No `_settled` and no `record_owner`. Equivalent here: `copy_built` asserts the owner is `OURS`.
  - No strip templates are passed to `plan_gearbox`, as in W8's `Desk`.
  - No `try`/`plan_trouble`: a raise is louder, which is fine.
  - `parts_only` now includes `turned_refusal()`, like the window.
- *`update_solidworks` (`:221-268`) against `press_update` (`:1317-1339`), `_collect_job` (`:1455-1490`) and
  `_finish_update` (`:1564-1595`).*
  - **No footer gate.** The window presses only when `footer.update_enabled`, and goes to Build again… when
    `needs_new_revision`. The script never asserts `update_enabled` or `update_shown` before a press, so it could
    demonstrate a press the window does not offer, for instance after a recorded refusal. `ahead_of` already has the
    footer: assert both there.
  - No `_mark_not_as_built` on `NotAsBuilt`.
  - The revision is taken in the job as the window takes it.
  - Dropping W8's `TURNED`/`note_made` bookkeeping is harmless here: `drive_proof` is not used.
- *`_record_refusal` (`:270-286`) against `:1597-1612`.* The `store.foreign_workbook(self._settled(record), …)`
  guard is missing. Equivalent on a copy whose record is its own.
- *`build` (`:288-328`) against `_start_build` (`:1380-1396`) and `_finish_build` (`:1530-1562`).*
  - The stayed-behind clause is not gated on `result.assembly.saved` (`:1541`), and `job.before.path` is not passed.
    The second is equivalent while the record has an assembly.
  - A fresh record's `own_digest` and `recalc` are not set.
  - `positions_per_configuration` is not taken from a build. W8's `Desk.build` did take it (`workbook_assembly_check.py:1222`),
    so this is a regression in the footer the `again` sections log.
  - No `_settle_journal` on a raise, and no `plan.refusal` guard.
- *A check that proves nothing.* `again`'s `expected in desk.note[0]` (`:1461-1473`) compares Desk9's own
  composition with itself. Only the build's `old_user_work` there is evidence.
- *Calling the window's own code.* `_plan_solidworks_pass`, `_record_refusal`, `_finish_update` and `_finish_build`
  are plain functions on `WorkbookWindow`. Each could be called unbound on a small object that has `link`, `state`,
  `app`, `recalc` and `_open_record`/`_write`, with `workbook_gui.Job`. `workbook_gui` is imported already.
  - **One caution.** The window's `_write` calls `store.save_recent(self.app.recent)`, which would overwrite the
    user's Recent list. Point APPDATA into the run folder first, as `workbook_window_check.py` does.
  - With that done, the drift above goes away. Only `press_update`'s two-line `work` closure would stay a copy.

**10. Should fix: an exception other than `AssertionError` from the script's own code ends the whole run, and a
re-run into the same folder exits.**

- *Where.* `main` (`:1698-1709`) catches only `SectionStop` and `AssertionError` per section. A few examples would
  escape to the outer handler and end the run:
  - an `AttributeError` from `Desk9.update_solidworks` when `desk.update` is None (`:227`);
  - from `copy_desk` when the copy has no record (`:684`);
  - from `nocarrier`'s `desk.update.motion` (`:1584`);
  - a `StopIteration` from `W.cell`.
- *Fix.* Catch `Exception` per section, re-raising `DemoStop`, `W.WorkerHung`, `swcom.NotRunning`, `W.Stopped` and
  `W.Halt`.
- *Re-runs.* `copy_built` raises `SystemExit` when `OUT/<section>` exists (`workbook_assembly_check.py:4172-4173`),
  so re-running a section into the same `<out>` stops the run. The note's re-run paragraph (lines 102-104) should
  say to use a fresh `<out>` and give the masters by path.

**11. Should fix: `windows_new` counts windows the note says are exempt.**

- *Where.* `windows_new` (`:479-490`) counts any titled window of SolidWorks' process. It exempts only the untitled
  notification box. Every count is a STOP of the run in `m3` (`:724-725`), the first section.
- *The balloon.* The note (lines 124-126) exempts balloon tips. But `m3`'s UserGap 41 is made to bring the "Over
  Defined" balloon (S0's run 2 log, line 917). If its top-level `swBalloonTip` window carries a title, it counts.
- *The progress box.* A self-closing progress box (`#32770` titled "Updating..." or "Calculating Interference
  Detection", `W.PROGRESS`) still up in the 8 s after a rebuild would count too.
- *Fix.* Exempt the class `swBalloonTip` and `W.PROGRESS`'s titles explicitly, and log them as facts.

**12. Note: the `use_open_document` fallback (`:360-370`) is dead at HEAD.**

- `Session.use_open_document` exists (`swcom.py:3270-3281`).
- The fallback did the same thing: it walked the documents, set `_build_doc` and raised the epoch. It returns `True`
  where the method returns a `DocInfo`, which is harmless because the caller only tests for None.
- Remove it, so a renamed method fails loudly instead of the script standing in for the app.

**13. Note: 2024's confirming set goes beyond the rule in *Rules carried over*.**

- *The rule.* The confirming build is "one full turning build with its edits, plus every section in which the two
  versions have been seen to differ".
- *What fits it.*
  - `setup` and `go` are the build with its edits.
  - `m3` stands on the probe-ahead rule: M3's assembly rebuild is unmeasured on 2024, with a dialog risk.
  - `reducer` and `nocarrier` are needed only if `USER_MATE_PUT_NO_CARRIER_ON_2024` is wanted.
- *What does not.* `refuse`, about 30 minutes: S0 saw no difference between the versions in the reads it rests on.
- *What the note should say.* The plan's *Done when* reads "2024 confirms the assembly sections", which is broader.
  The note should say which it follows and put `refuse` on 2024 to the user. A smaller choice is to keep only its
  lightweight step, since 2024 is the version said to open components lightweight.

**14. Note: gaps in the note's lists.**

- *A missing file name.* "What must be open or closed" lacks `SunGear.SLDPRT`, the file the `again` sections make
  (`SUN_PART_NAME`).
- *An overclaim.* The STOP list says `GetSaveFlag` is read around "any … `components` … or `feature_states` read".
  `feature_list` (`:473-476`) and `users_in_copy` (`:690-699`) read without it.
- *Missing from "What it cannot show".*
  - the wheel over each window with the other focused (W9A-REVIEW-B, point 7);
  - K1's component found by its part path under a new name;
  - `PROBLEM_OTHER_KIND` and `PROBLEM_LOCK_BY_MODE` on SolidWorks;
  - the entity comparison (8).
  Adding a coincident from a sprocket to Sun's Top plane to `refuse` would show the first refusal kind cheaply.
- *M1's remainder.* The note should say that the width, limit and path kinds and the leaf in a sub-assembly move to
  S5 in W9c's sessions, which reads every mate kind.

**15. Note: the window check's new assertions are sound, with two gaps.**

- *They use names that exist at HEAD:* `_status_box`, `_status_bar`, `_status_scrolls`, `_foot`, `_page`,
  `_page_bar`, `_body`, the four buttons, `work_area` and `FOOTER_SHARE`.
- *They would catch the closing run's fault.* `w8_k12` compares the client's real rectangle with the frame's and
  with Tk's height. A window Windows holds shorter than Tk thinks fails one of those two checks, and the buttons'
  bottoms are measured against the real client.
- *Gap 1.* `w8_set_status_whole` checks the box but not the buttons. Call `w8_k12` after it too.
- *Gap 2.* The footer's ceiling path, where the sentence scrolls in itself, is never reached on this screen. E4's
  built footer is about 281 px against a ceiling near 523 px, so only the Tk test covers it. The note should say so.

**16. Note: two small assumptions.**

- *`m1`.* It suppresses UserDist5 in `modes[0]` and calls that "the active mode" without checking. Assert
  `r["active"] == modes[0]`.
- *`go_turn`.* It measures Sun's turn from a read in the active mode (H, after `read_every`) to one in the mode
  driven (L). That holds for Sun, which has one frame in every mode. Using `s7_drive_job`'s own `before` and `after`,
  both read in the mode shown, would not lean on it.

---

## What I checked and found right

- **Names.**
  - Every attribute the script takes from `W`, `S0`, `findings`, `store`, `swbuild`, `swcom`, `ui_text`, `spur` and
    the workbook modules exists at HEAD (AST check), and both files compile.
  - Each `Session` call matches its signature: `add_mate`'s `ratio`, `set_dimension_in` in mm,
    `mate_suppression` one name per call, `find_component`, `use_open_document`, `feature_states`, `mate_info.whole`,
    and `components()`'s `state` and `code`.
  - So do the result fields: `GearboxUpdate.carried`, `renamed`, `user_in_error`, `user_features_in_error`,
    `put_in`, `user_work`; and the record's `UserWorkEntry`/`UserCarriedEntry`.
  - S0's import is harmless: it reads `--master` into its own `MASTER_GIVEN`, which nothing here uses.
- **`refuse` against `judge_user_work` and `_user_check` at HEAD.**
  - Lightweight: a `PROBLEM_COMPONENT` from the judgement itself since `2c59e9c`, foreseen by the footer.
  - Housing lock: `PROBLEM_TIE` by `_ground_sentence`, naming Housing-1; the footer foresees it the same.
  - Solver's tie: `PROBLEM_TIE`, "unable to turn".
  - Two bodies: `PROBLEM_TWO_BODIES`, naming every lock of the cluster.
  - Bore: `PROBLEM_VALUE`, with `cell` "Gears!J2" (Bore is column J; Sun is row 2), values first
    (`swbuild.py:5671-5673`).
  - All at once: `TWO_BODIES`. The `continue` skips the cluster's ground, as the author's comment says. A tie read may
    stand beside it, and the expected set allows that.
- **`nocarrier`.**
  - The default refusal is `PROBLEM_UNSETTLED` per cluster, naming the finding.
  - The footer's `bodies_put` and the worker's `_may_put` agree on a G4 axial move.
  - The patch is set and restored in one `try`/`finally`, in `nocarrier` only. The worker thread reads the same
    `findings` module, and the proposal is True only if both presses and all their reads are clean.
  - The footer's prediction is compared with the press where the footer predicts, and the recorded-refusal case is
    told apart.
- **`go`.**
  - The carried set the footer foresees ({Sprocket-1, Sprocket-3} with Sun, Sprocket-2 with RangeSlv) is the
    judgement's, and it is compared with `result.carried` before and with the record after.
  - The flags, codes, frames and keyway checks can each fail.
- **Fixtures.** RangeBox's Backlash is blank, so clearing the cell restores it. The 12 : 1's G4 is at 27 and S3 at
  x 131.75. The 2026 and 2024 master paths in the note match `W9-S0.md`.
- **Robustness and safety.**
  - Keep-awake is on.
  - The JSON is written after each section and first in the `finally`.
  - The close and Excel's quit are each guarded.
  - The revision and the snapshot (`SNAPSHOT_COMMIT` beside `src`) are in the log's head.
  - A memory guard runs before each section on any version.
  - User documents are logged as `<user document N>`.
  - Only documents under the run's folder are saved or closed, and only the run's own Excel is used.
  - The old assembly is never saved, shown or activated by the script's reads (`read_now(activate=False)` uses the
    app's `use_open_document`). The 2024 save in `end_copy` does not reach the `again` sections, which are not on
    2024's list.
- **The command lines** fit both scripts' argument parsing, and the time estimates are credible against S0's 124 s
  build and W8's 238 s and 515 s presses.

## What I could not verify

- **Nothing on SolidWorks.** I could not check:
  - whether the balloon's top-level window has a title (11);
  - whether `mate_info` reads a lightweight component's entities;
  - whether the quiet press walks Sun's part (7);
  - whether `GetConstrainedStatus` on the old assembly marks or solves anything;
  - whether `AddMate5` makes a gear mate between two coaxial sprockets (`m1` catches a refusal);
  - whether Tk's root coordinates and `GetWindowRect` agree under this device's DPI setting in `w8_k12`.
- **The test suite.** I did not run it; another agent was.
