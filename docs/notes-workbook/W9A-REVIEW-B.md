# Review of W9a package B: what the user sees of their own work, and what the record keeps

*Independent, 2026-11-16. I started no SolidWorks or Excel and changed no source, test or document. This file is the
only one I wrote.* Under review: `git diff e9b2ebe..dac5c7e`, the five commits `e3cb13d` (W99 and "the last phase"),
`9f53276` (schema 7, the footer, the Build again? clause, the build job's read), `9c33e3b` (the two boards),
`feec547` (K12 in the window) and `dac5c7e` (UI-DESIGN and the package's note). Line numbers are `dac5c7e`'s.

I read ISSUE-1-PLAN §0, §2.1 (items 6 and 8 above all), §2.4's record paragraph, §2.5, §2.6, §5's W9a and *Changes
after S0 and its review*; `W9A-INTERFACES.md`; `W9A-PACKAGE-B.md`; the changed parts of `design/UI-DESIGN.md`; the
handoff's *Rules carried over*; and `W9A-REVIEW-A.md` for its form. Beyond the repo's own tests I ran throwaway tests
from the scratchpad against the repo's fake (no copy of the repo), and regenerated every board with `gen.py`'s writes
redirected to the scratchpad.

**The tree moved under me.** Another agent committed `f2feac0` and `5610795` (package A's re-check) on top of
`dac5c7e` while I worked. The whole suite, run once, gave **1 failed, 3417 passed, 1 skipped**: the one failure is
the known font-width test `test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`; the seven
tests beyond the expected 3410 are that agent's. I did not chase their changes. Every finding below is about the
commit range.

---

## Verdict

- **The shape is right.** Schema 7 is written and read as the plan asks, and older records read as before. The
  footer's prediction is package A's own judgement, with `branches` always given. The build job's read of the old
  assembly is made with package A's read and never stops the build. K12 is built the way §2.6 rules it, and its Tk
  tests can fail. Every existing board regenerates byte for byte, and only the planned pins moved.
- **But it is not ready for the demonstration.** Three points must be fixed first:
  - **K12 clips the footer's sentence (1).** Every sentence the window sets outside `_refresh_state` keeps the
    previous sentence's box: a two-line "SolidWorks cannot be reached" is shown 40 px wide and one line tall. This
    is a new regression.
  - **Neither the window check nor the new Tk test can see that clipping (2).** Both measure the label, which is
    always drawn at its full size inside its canvas. The window check's two assertions K12 asks for are not
    written either.
  - **The footer promises a carry the press refuses (3).** A user component loaded lightweight or suppressed is
    said to "move with Sun"; the press then refuses it, so the package's claim that it never promises what the
    worker would refuse does not hold.
- **Two of the implementer's choices need a ruling.**
  - The Build again? question says nothing at all when the record holds no inventory (4, judgement call 5).
  - A recorded refusal hides a foreseeable new refusal once the workbook changes (5, judgement call 2).

---

## Findings

**1. Must fix before the demonstration: a sentence set outside `_refresh_state` is clipped to the box of the sentence
before it.**

- *What the code does.* K12 moved the footer's label into a canvas, `_status_box` (`workbook_gui.py:498-513`), whose
  width and height only `_fit_status` sets (`:1241-1257`). `_fit_status` is called from `_refresh_state` (`:855`)
  and `_fit` (`:1227`), never from `_set_status` (`:1287-1291`).
- *Where it bites.* `_set_status` is also called on its own at five places. In each, the new text goes into a
  canvas still sized for the previous sentence:
  - `_tick`'s "collect failed" (`:610`);
  - Export's "Nothing was exported" (`:1159`);
  - `_worker_free`'s "SolidWorks cannot be reached", "the strip is busy" and "a job is still running" (`:1431-1438`);
  - "The workbook could not be opened" (`:1635`).
- *Reproduced on the Tk fake.* I built a workbook, set the note to "Built.", and refreshed: the box was 40 × 17 px.
  Then I called `_set_status(ui_text.job_unreachable(...))`. The label asked 586 × 30 px, and the box stayed
  40 × 17 with no bar. On screen the user would read about five letters of the one sentence that says why nothing
  happened.
- *Before K12* the label was gridded directly and always showed whole.
- *What to do.* Have `_set_status` call `_fit_status(work_area(self)[2] // FOOTER_SHARE)`, after `_wrap_status`
  where the room changes. Add a Tk test that sets a long sentence by `_set_status` alone after a short one, and
  asserts that the box shows it whole.

**2. Must fix before the demonstration: the window check and the K12 test measure the label, which cannot show
clipping, and the window check's two new assertions are not written.**

- *The window check.* `w8_footer_whole` (`probe/workbook_window_check.py:630-639`) passes when
  `label.winfo_height() >= label.winfo_reqheight()` and the label's bottom is inside the window.
  - A label inside a canvas is always drawn at its requested size, so the first test always passes, however
    little of it the box shows (point 1).
  - When the sentence scrolls in itself above the ceiling, the label's bottom lies below the box and may lie below
    the window, so the check would fail a footer that is right.
- *The new Tk test* has the same flaw. Its "the sentence whole" assert
  (`tests/test_workbook_window.py:805`) compares the label with itself.
- *Not written.* §2.6's *Done when* asks the window check to assert two more things: the frame's bottom
  (`GetWindowRect`) inside the work area, and the body's last line scrolled into view. Neither assertion is in
  `workbook_window_check.py`. Package B's note lists them as what the demonstration must show, but no commit
  writes them.
- *What to do.*
  - Measure `_status_box` against the label's requested height: whole when they are equal; at the ceiling with
    its bar mapped when it scrolls.
  - Change the same assert in the Tk test.
  - Write the two assertions into the W8 stage before the window check runs: the frame by `GetWindowRect`
    against `gui._work_area`, and `_page.yview_moveto(1)` then the body's last widget inside the page.
  - Whose job the script is (package B's or the demonstration's) is the coordinator's to say. It must be done and
    reviewed before that run.

**3. Must fix before the demonstration: the prediction does not foresee the worker's refusal of a carried component
that is suppressed or lightweight.**

- *What the worker does.* `_user_check` refuses, after `judge_user_work`, any component route (c1) would carry that
  is suppressed or loaded lightweight (`PROBLEM_COMPONENT`, `swbuild.py:5598-5608`).
- *What the prediction does.* `update.user_work_ahead` (`update.py:2098-2128`) calls only `judge_user_work`, although
  the record keeps each component's `state`.
- *Reproduced on the fake.* A sprocket locked to G1 with `component_states["Sprocket-1"] = 1` (lightweight); a quiet
  press records it; then a layout move. The footer says *"… moves your Sprocket-1 with G1, which your Lock3 holds it
  to …"* in green, and the press refuses: *"… Sprocket-1 is loaded lightweight in Reducer_12to1.SLDASM, so nothing is
  changed; in SolidWorks, set it to Resolved …"*.
- *Why it matters.* A large assembly opened with components lightweight is a common SolidWorks setting. The commit
  message, the note (*so the footer never promises a carry the worker would refuse*) and UI-DESIGN all make the claim
  this case breaks.
- *What to do.* The cleaner fix is to move the state check into `judge_user_work`, so the worker and the prediction
  share it; that is package A's code, the coordinator's call. Failing that, `user_work_ahead` applies the same check
  to the recorded states. Add a test either way.

**4. Should fix, needs a ruling: the Build again? question says nothing of the user's work when the record holds no
inventory (judgement call 5).**

- *What the code does.* `stays_behind` returns None, and the clause is left out, when `user_work` is None or empty
  (`update.py:2146-2162`, `ui_text.py:2186-2190`).
- *Who gets no clause.* A gearbox built before W9a and never updated since. A new revision before its first Update
  (`finish_build` drops the inventory, `gearbox.py:1430`). A record whose last press failed before the read.
- *Why it falls short.* Plan §1.5 names exactly this as the problem: *"it never says that the user's components,
  mates, or features in parts made new stay behind"*. K5's interim promise is *"Until W9d, Build again… says what
  stays behind, as read at a stated time"*. With no read there is no time to state, but the plan does not say the
  user may be told nothing. The build job's read after the press names what it finds, but by then the user has
  answered.
- *My recommendation.* With nothing on record, the question says without a time that anything the user added in
  SolidWorks stays in the old assembly: components, mates, and features in parts this revision makes new.
  `RangeBox_r2` has none of it. With an inventory, the clause should add "and anything added since", since the read
  may be days old.
- This is a wording decision for the coordinator.

**5. Should fix, needs a ruling: once the workbook changes after a recorded refusal, the footer turns green and runs no
prediction (judgement call 2).**

- *What the code does.* With `entry.problems` set, `user_work_ahead` returns the recorded refusal alone
  (`update.py:2113-2115`). Once the digest differs, `user_work_line` says *"The workbook has changed since …"*
  in green.
- *Reproduced on the fake.*
  - A quiet press refuses on K11 alone. Nothing is put, so a coincident mate of the user's on G1 is not judged.
  - The user types the bore and moves G4. The footer is green and says only the old refusal and *"The workbook has
    changed since"*.
  - The press then refuses: *"Coinc7 is a mate … on G1, which Update SolidWorks puts back …"*.
- *Why it matters.* The recorded inventory is still the best knowledge there is. Without a tie read, the recorded
  sentences are a superset only for the press they came from.
- *What to do.* When `changed_since`, run the prediction on the recorded inventory as for a press that went ahead,
  after the recorded sentence. Its colour is the prediction's.

**6. Should fix: the build job's read of the old assembly is proven by the fake only in part, and it activates the old
assembly.**

- *Activation.* `read_old_assembly` (`swbuild.py:5421-5449`) calls `open_document`. On a document already open,
  that is `OpenDoc6` (warning 128) followed by `ActivateDoc3(title, False, 0, …)` (`swcom.py:3267-3330`).
  - This brings the user's old assembly to the front.
  - Option 0 of `ActivateDoc3` is the rebuild-on-activation choice; I could not settle from the code what it does
    to an assembly that needs a rebuild. Update already does this to the current assembly, but on the old one it
    is new.
  - The reads need only the document as the build document. A route that sets it without activating would avoid
    the question.
- *The preference toggle.* `begin_build`/`end_build` set and restore `swInputDimValOnCreate`. That is an
  application preference, not a document or anything of the user's, and it is restored in `finally`. The plan does
  not forbid it, as every job does the same.
- *What the test proves, and what it does not.*
  `test_the_build_job_reads_the_old_assemblys_user_work_first_and_writes_nothing_to_it` checks that every call
  is in `READS` and that the fake's mates and frames are unchanged.
  - It does not check the fake's active configuration or anything standing for a save flag.
  - `READS` admits `begin_build`, `end_build` and `open_document`, whose real effects the fake does not model.
  - No repo test covers a read that raises. I ran one on the fake (`mate_info` raising): the build completed,
    `old_read` held the sentence, and nothing else was disturbed.
- *What to do.* Add the raising-read test, asserting the build is whole and the sentence is said. The demonstration
  must read `GetSaveFlag`, the active configuration and the active document's rebuild state of the old assembly
  before and after, with the old assembly needing a rebuild in one of the runs (below).

**7. Should fix: the Workbook window's wheel handler acts whatever window the pointer is over.**

- *What §2.6 item 5 asks.* *"Both handlers act only for their own toplevel."*
- *What the code does.* The strip's handler gained that guard (`gui.py:322-323`). `WorkbookWindow._on_wheel`
  (`workbook_gui.py:1274-1285`) has none: when the pointer is over another window, or over no window
  (`winfo_containing` None), it still scrolls its page.
- *When it matters.* Where Tk delivers the wheel to the focused widget, a Workbook window with focus scrolls its own
  page and the strip's at once when the pointer is over the strip. Where Tk delivers it to the widget under the
  pointer, the handler is not reached in that case. Which of the two Windows' Tk does here, I could not check.
- *Not tested.* Neither guard has a test; the Workbook test calls `_on_wheel` with `winfo_containing` patched.
- *What to do.* Return unless `over` is in this toplevel, and test both guards.

**8. Should fix: the new sentences, read in combinations on the fake.**

- `stays_behind_sentence`, with one item, still says *"your Sprocket-1 stays in RangeBox.SLDASM; RangeBox_r2 has none
  of them."* (`ui_text.py:4336`). `stayed_behind_status` was fixed to "it"; this one was not.
- After a read that raised, the sentence reads *"Reducer_12to1.SLDASM could not be read again (SolidWorks did not
  answer the read of Reducer_12to1.SLDASM: …): As read at …"*. The file is named twice, and a capital follows a
  colon. The same capital follows *"… was not open in SolidWorks, so it was not read again: As read at …"*.
- With nothing on record, `stayed_behind_status` says *"stays in the old assembly"*, though `job.before.path` names
  it.
- The tie clause, *"asks SolidWorks, when pressed, whether your Lock3 leaves Sun's train free to turn"*, does not say
  what follows: Update stops if it does not. Nor does it say what the user can do. The worker's tie sentence says
  both.
- After an Update, *"Your Lock3 in H and L is in error in SolidWorks after it."* has two problems:
  - "after it" reads as "because of it";
  - items that were already in error before (`user_work.in_error`) are not told apart, although the plan's item 2
    is that a later failure is not laid to the app.
- Several features in one part are each named with the part (*"Keyway in Gear_m1.5_N17 and Groove in
  Gear_m1.5_N17"*). This is a nit.
- Everything else I tried reads as grammatical and true, and the inventory is never called complete:
  - carried components;
  - leftovers named up to three, then counted;
  - one mate named, several counted;
  - "other mates" after some were named;
  - items already in error;
  - a component found under a new name;
  - a refusal recorded and said.

**9. Should fix: "W8 is the last phase" still stands in the public `README.md:550` and in
`tests/test_workbook_modes.py:438`'s docstring.** The note says it was rewritten "everywhere it stood". §0.1's list did
not name these two, but the README is what the issue's readers see. The test file is being edited by package A's
agent now: leave that one to them.

**10. Note: where the footer is silent, or says "leaves … as they are", when the press may still act.**

- *Silent.* With no inventory on record the footer says nothing; that is by design and honest.
- *A quiet press.* `bodies_put` predicts nothing. The worker, though, also puts a train it finds live out of step
  or off its axis, or, with modes, the active mode off its frames (`swbuild.py:5584-5590`). Then the press may carry
  or refuse what the footer said it leaves "as they are". The sentence does say "As read at …".
- *Features in the layout or a carrier part.* These are said to be left "as they are" even when the layout changes,
  since `followed` takes only `changed_parts` (`update.py:2112`).
- *Equivalence on the fixtures.* `bodies_put` matched the worker's `may_put` on every edit I tried:
  - on the reducer: quiet, backlash, Face Z, bore, a shaft moved;
  - on RangeBox: quiet, a slide.
- *Trains.* With modes the prediction joins trains over every mode, and the worker over the active mode's links.
  Only the wording of tie and unsettled sentences can differ, never whether one is foreseen.

**11. Note: the prediction judges on the revision the inventory was read on; the press, on the one running.** A user
moving between 2024 and 2026 could be told the other version's answer once the branch findings differ by year. Today
every branch finding is None on both, and an unknown revision (`[]`) foresees refusal, which is safe.

**12. Note: what schema 7 newly puts in the record.**

- *What is new.* The record beside the workbook now holds:
  - each user component's full file path, possibly anywhere on the user's disk;
  - the names of the user's components, mates and features;
  - the refusal sentences.
- *What it held already.* App part and assembly paths in the same folders.
- *Where it lives.* The file is local. Nothing in the range logs these names: no `log_lines` changed, and the boards
  use `C:\Parts\…`.
- *The one way out.* A user who attaches the record to an issue would publish their own file paths.
- *What is used.* Only the extension (`.sldasm`, for the sub-assembly branch).
- *What to do.* Consider keeping the file name, or a sub-assembly flag, instead of the path. W9d reads the old
  assembly again anyway.

**13. Note: what the record does not keep.**

- A refused press replaces the last successful inventory. Only its `carried` history is lost, and nothing reads that.
- After Build again…, `finish_build` drops the inventory (the assembly changed), and the build job's fresh read of
  the old assembly (`old_user_work`) is said but not kept. A later question about the old revision has nothing on
  record. W9d's schema 9 is where this belongs; say so in the note.

**14. Note: the old-assembly read finds no renamed component.** It takes the record's `Name2`s with no K1 search by
part, so an app component the user renamed in the old assembly is listed as the user's in the build's sentence.

---

## The implementer's judgement calls

1. **The prediction's "put".** Within the plan. The quiet-press limit (10) should be said in UI-DESIGN's new section.
2. **A recorded refusal said as recorded.** Right while the workbook is the one refused. Once it changed, the
   prediction should run too (5). **Ruling wanted:** run it after the recorded sentence.
3. **The line follows the state, never after a job's sentence.** Within the plan.
4. **Wording.** Within the plan, but for the sentence fixes in (8).
5. **The Build again? clause only with a non-empty inventory.** A gap against §1.5 and K5. **Ruling wanted:** my
   recommendation is a timeless clause when nothing is on record (4).
6. **The old assembly read only when open, by `open_document`.** Within the plan (S5's read-only open is W9c's). The
   activation is a demonstration item (6).
7. **The scroll lane is the right padding.** It departs from the letter of §2.6 item 4 ("counted in the left column's
   width") and keeps its purpose exactly: no column narrows, and the lane's width is tested. I accept it; the
   coordinator should note it, but it needs no ruling.
8. **K12's numbers.** These are FRAME px(40) as the strip has it, the 160 px least height and a third of the work area
   for the footer. All within §2.6. The board draws the plan's 1570 px, while the code caps at the work area less
   60 px at 150 %. On a screen with a taskbar that may come out shorter than the board shows; the window check
   measures it.
9. **The boards in UTC at 14:02 today.** Fine. They regenerate byte for byte.

## What the SolidWorks demonstration must show that the fake cannot

- *The build job's read of the old assembly*, with that assembly open and, in one run, needing a rebuild. Before and
  after, the old assembly's `GetSaveFlag`, its active configuration, every user mate's flag and error code, and no
  dialog: `ActivateDoc3` with option 0 is the open question (6). Once more with the old assembly closed.
- *The footer before a press on S0's master*:
  - after a quiet Update, the sprocket named going with Sun;
  - the same with the sprocket set to lightweight, which after fix 3 must foresee the refusal;
  - the record's `user_work.revision` reading 34.1.1.
- *The refusals.* The lock-to-housing and Bore refusals recorded, said with their time, and green once the
  workbook changes, with the prediction (after fix 5).
- *The window check's W8 stage on this device, after fix 2*:
  - the footer box whole, measured on `_status_box`;
  - the frame's bottom by `GetWindowRect` inside the work area;
  - the body's last line scrolled into view.
  - Also a sentence set by `_set_status` alone, such as SolidWorks unreachable, shown whole (1).
- *The wheel over each window with the other focused* (7).

## What I checked and found right

- **Schema 7.** The shape is as the note says. A v3–v6 record reads with `user_work` None and writes back as 7. A
  newer record is refused and left byte-identical. Every malformed shape is refused with a sentence. The entity
  words match the worker's (pinned by a test). Records round-trip byte for byte. A W8 reader refuses a v7 record and
  leaves it alone, as every schema step has. `__bool__` on the entry is used only where None is first excluded.
- **Recording.** `finish_update` records the inventory only for the record's own assembly. `_record_refusal` reads
  the record again from disk, checks it is this workbook's, and writes only `user_work`. A non-user refusal changes
  nothing. `Job.revision` is captured on the worker thread before the press can raise.
- **The prediction.** It is package A's `judge_user_work`, `branches` always `user_carry_branches(...)`, and the
  revision given explicitly. `bodies_put` agrees with the worker's `may_put` on the fixtures I tried.
- **The build job's read.** It comes after the gates and before any check or write. It is wrapped so any exception
  becomes `old_read` (confirmed on the fake). It is not nested inside another `begin_build`, so the preference is
  restored. The read leaves `_build_doc` on the old assembly, but every later step opens or begins its own document
  first.
- **The worker.** Package B changed nothing in package A's worker beyond `OldAssembly`, `read_old_assembly`,
  `_read_before`, `build_gearbox(before=)` and two `GearboxResult` fields; `finish_update`'s `revision`;
  `finish_build`'s drop; and `read_sidecar` passed to `classify` (safe: `store.read_sidecar` never raises). The edit
  to `W9A-INTERFACES.md` §2.3 records the coordinator's correction only.
- **K12.**
  - `_fit` caps at the work area less the frame and places the window inside it.
  - The page has a least height.
  - The footer's ceiling is a third of the work area.
  - Grid shrinks the weighted page row first, so the footer stays whole when the user drags the window shorter.
  - `_fit_page` converges with no loop: same sizes produce no new `<Configure>`, and the lane is fixed-width, so the
    bar never changes the canvas.
  - `_fit_status`'s re-wrap is monotone.
  - The header and footer keep their old width.
- **The K12 tests can fail.** With `_fit` uncapped, both tests fail (955 ≤ 715). With the ceiling removed, the
  ceiling test fails.
- **Boards.** `9c33e3b` precedes `feec547`. Git shows no existing board, render or `canvas.json` entry changed. All
  33 boards and `canvas.json` regenerate byte-identical to `dac5c7e`.
- **Pins moved, each justified.**
  - The schema number in `test_store.py`: five asserts, and the "newer" test now at 8 (§2.4).
  - The window test's schema number.
  - "phase W9" → "W99" in `test_workbook_build.py`, `test_workbook_window.py` and UI-DESIGN (§0.1). The asserts
    beyond §0.1's line list follow from the fixture's string.
  - `test_the_window_keeps_its_width_with_update_shown_and_a_long_sentence`, now `min(reqheight, cap)` (§2.6).
  - No other pin moved.
- **UI-DESIGN.** Its three "grows taller" places are rewritten. Its new section states the inventory's gaps
  (assembly features, the static path, per-mode states) as `W9A-INTERFACES` §5 asks. Its claim "never promises what
  the worker would refuse" is false until fix 3.

## What I could not verify

- Everything SolidWorks does:
  - whether the reads mark the old assembly modified;
  - `ActivateDoc3`'s rebuild behaviour;
  - the What's Wrong dialog;
  - the reads' cost on a large assembly.
- How Windows' Tk routes the wheel, and the real frame and work area on this device.
- The renders: taken with Windows' Chrome from WSL. I looked at both PNGs; the short-screen board's bar thumb is
  barely visible.
- The suite against `dac5c7e` alone: the tree moved under me (above).
