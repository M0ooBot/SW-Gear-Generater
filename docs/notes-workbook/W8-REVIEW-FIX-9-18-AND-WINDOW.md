# Review of the fixes to `W8-REVIEW-9-18.md`, and of the window and boards after them

*Independent, 2026-11-15. I changed no code.* Under review:

- **A, the fixes:** `7ada83d` (`TURN_SHOWN_ELSEWHERE`), `1f08117` (each crossed coupling said once), `f746293`
  (tests from the committed finding), `46ef6d9` (the findings comment and pin), `f6a2ab7`, `7cbf1ff`, `e63a7f4`.
- **B, the window and boards:** `d7a3074`, `0435b8a`, `1c04645` (window tests); `1012a7a`, `3579c0c` (boards and
  PNGs); `914553a`, `6e882b6`, `ab0c38c` (UI-DESIGN); `076845e` (new behaviour: `_fit_part_cells`).

Line numbers are at `ab0c38c`. The s2 log is
`probe/results/w8-workbook-assembly-20261115-111951-s2-turn-carried-per-body.log` (written ":N" below).

**Verdict.**

- B's new behaviour is sound. `_fit_part_cells` measures what the grid really lays out, cannot oscillate, keeps
  1080 px at 100 %, 125 % and 150 %, and its tests catch three mutants.
- A1's warning is reachable only with modes. The boards regenerate byte for byte, and UI-DESIGN quotes `ui_text`
  exactly.
- Four things should change:
  1. **Must fix (records, not behaviour).** The reading `46ef6d9` adds to `findings.py` is not in the log
     (point 1). It is the reading `W8-REVIEW-9-18.md` point 4 asked for, and that point misread the log. The
     "not turned" of 2H and 4L was never judged: `train_check` judges a turn only for a train in step, and FDrive
     stood off its place in the one joined train. 4H and N were shown after 2H's own put in the same Update. The
     same log shows a put that did not reach every configuration, so *"a put of it show[s] in every
     configuration"* overstates.
  2. **Should fix.** Each crossed coupling is still said twice in the full status, in two different forms
     (point 2). `1f08117` removed the repeat inside `_mode_after` only.
  3. **Should fix.** After an earlier unsaved Update, *"that turn"* has no antecedent (point 3).
  4. **Should fix (test).** The warning's `not visited` guard is not covered: dropping it passes every suite,
     Linux and Windows (point 4).

---

## Points

**1. Must fix (records): the "app's own put showed in 2H, 4H and N" reading is not in the log, and "a put shows in
every configuration" is contradicted by it.** `findings.py:1281-1290`, `W8-INTERFACES.md:322-331` (ruling 9.18's
first bullet), `W8-PLAN.md:162-167` (the J11/J26 note), `tests/test_findings.py:1105-1131`.

- *What the comment rests on.* After the quiet Update put the train in 4L, the changed Update's judgement of each
  mode on showing read `turned False` everywhere: `:437`, *"2H alone found turned when shown: [('2H', False), ('4H',
  False), ('N', False), ('4L', False)]"*, and `:297-300`.
- *Why 2H's and 4L's `turned False` say nothing.*
  - `train_check` sets `turned = in_step and …` (`swbuild.py:1768-1770`), so a train with any gear off its place
    reads `turned False`, whatever its turn.
  - `_modes_put` judges trains joined over every mode's relations (`swbuild.py:4314`, `_trains(…, motion.meshes,
    …)`), and a coupling is a `MeshLink` in `motion.meshes` (`workbook/update.py:1400-1416`). So ModeSlv engages
    FrontDog joins the Sun train to FrontDog, FDrive, FIdler and FOut: on E4 every mated body is one train.
  - The workbook had moved FDrive from 130 to 132 (`:205`, `:217`). In 2H and 4L the judgement on showing reads
    `off axis ['FDrive']` (`:247-248`, `:297`, `:300`), so in those two modes the turn was never judged.
  - Scratch check: a three-gear train turned 37°, in step, gives `turned=True`. Move one gear 2 mm and it gives
    `off_axis=('C',), turned=False`.
  - The pin in `test_findings.py:1131` matches only the prefix *"post-check of {mode}: turned False; out of step
    []"*. That hides the `off axis ['FDrive']` that follows it on 2H's and 4L's lines.
- *Why 4H's and N's readings do not show the 4L put either.* The changed Update showed 2H first and put the whole
  train there, because `moved` is True, so `needed` holds for every train (`:295`, `:439`). Only then did it show
  4H and N. Their reading at the built turn is explained by 2H's put as well as by 4L's.
- *What the log does show.*
  - A put of the mated train in one configuration reached others. 4H and N had stood +37° after the 2H turn
    (`:68`, `:85`). When shown in the changed Update, before their own put, they read in step, not turned, and with
    FDrive at its new 132 place: off axis `[]` (`:298-299`). Only 4L's quiet put and 2H's put came between, and
    FDrive's new place can only come from 2H's.
  - It did not reach every configuration. 4L, shown last, read FDrive at its old place (`:248`, `:300`) after
    the puts in 2H, 4H and N.
- *Change.*
  - In `findings.py`, replace the third observation and the "So" sentence with what was read:
    - the changed Update's put of the mated train in 2H (its locks and gear mates off in 2H alone) showed in 4H
      and N: FDrive was found at its new place there, and the train in step and not turned, before their own put;
    - it did not show in 4L, where the quiet Update had put earlier: FDrive was found at its old place;
    - 2H's and 4L's "not turned" were not judged, since FDrive stood off its place in the joined train;
    - whether the quiet put in 4L reached 2H was not read.
  - Then the conclusion: a mated train's turn is shared, and a put of it reached the configurations that had no
    earlier put of their own, not all of them.
  - J26's "a put holds only in the configuration shown" is still contradicted (2H reached 4H and N). But "shows in
    every configuration" must go from the comment, the ruling's first bullet and the W8-PLAN note.
  - In `test_findings.py`, pin the full lines `:297-300`, `off axis` included, and `:247-248`. Reword the docstring
    the same way.
- *Behaviour:* unaffected (W8-PLAN §1.9). Every put is to the built frame, and the changed Update puts every mode,
  4L included, so 4L ended right (`:300`'s mode then post-checked clean, `:435`, `:438`).

**2. Should fix: a crossed coupling is said twice in the full status.** `ui_text.py:3322-3325` (`_motion_after`'s
loop over `result.out_of_step`) with `ui_text.py:3988-3998` (`_mode_after`).

- *Why.* `result.out_of_step` is the active mode's check-phase judgement (`swbuild.py:4715-4716`), and couplings
  are among its pairs. `_motion_after` says every pair, *"RangeSlv and LoDog had been turned out of step with each
  other in SolidWorks; they are back in mesh."*. Then `_mode_after` says the same pair again as *"In 4L, RangeSlv's
  teeth stood across LoDog's; …"*.
- *Where it shows.*
  - s2's real status (`:189`): four sentences for two pairs.
  - `f746293`'s own pin repeats it (`tests/test_swbuild.py:6573-6574`).
  - In a scratch read of the full status, with three crossed pairs in 4L and the switch False, the status has six
    pair sentences, then the shared-turn sentence.
- *What `1f08117` did get right.*
  - With one, two and three pairs, "the gears of 4L are back at the turn they were built at" is said once, on the
    last pair, and the shared-turn sentence once.
  - Each clause names the right mode: the mode is always the active one, and so are the pairs.
  - With pairs crossed in two modes (2H active and 4L visited), only 2H's are named. 4L's is put silently under
    *"re-placed … in 4L and 2H"*, and *"The gears of 4H and N stood at the turn …"* rightly leaves out 4L, which was
    put. That is true, and it is how the code stood before.
- *Also.* *"They are back in mesh"* is said of a dog coupling, since `_pair_kind` knows only `lock` and otherwise
  says mesh.
- *Change.* In `_motion_after`, skip a pair that `_couple_pair` names whenever `result.configuration` is set and that
  mode is in `put_in`, since `_mode_after` says it. Re-pin `test_swbuild.py:6572-6580` and `test_ui_text`'s two-pair
  test on the full status, not only `mode_update_lines`.

**3. Should fix: after an earlier unsaved Update, "that turn" has no antecedent.** `ui_text.py:3339-3344`.

- *Why.* With `finished.earlier_update` set, the sentence before the warning is *"The gears stand as they were found
  in SolidWorks."*. Scratch status, with `turned=True`, configuration 2H, the switch False and `earlier_update='not
  saved'`:

  > *"SolidWorks already matches the workbook: nothing was changed. The gears stand as they were found in SolidWorks.
  > This version of SolidWorks shows that turn in every mode, …"*

  With `'lost'`, the same follows *"The last Update SolidWorks was not saved before TransferCase.SLDASM was closed;
  … so nothing needed making again."*
- *Change.* One wording needing no antecedent, true on both paths (the record's frames may be the unsaved
  Update's, but whatever stands in the mode showing shows in every mode):

  > *"This version of SolidWorks shows the gears at the same turn in every mode, so a dog may stand across its sleeve
  > in another mode; to put the gears back there, press Update SolidWorks with that mode showing."*

  Or keep "that turn" when `not earlier` and use this wording otherwise. Pin both `earlier` kinds.

**4. Should fix (test): the warning's `not visited` guard is not covered.** `ui_text.py:3342-3343`.

- *Mutant.* Dropping `and not getattr(result, "visited", ())`:
  - Linux: `2 failed, 3139 passed, 10 skipped`, the two `tkinter` failures only.
  - Windows, the three Tk files: `439 passed, 1 skipped`.
- *Reachable.* A changed Update (a part variable, say) with the active mode's train turned in step: nothing mated is
  put, every other mode is shown and judged, and the warning would then say that another mode may stand crossed
  after the app has just looked.
- *What the existing case covers.* Its "after a put" case (`test_ui_text.py:3320-3322`) is excluded by `put`, not
  by `visited`.
- *Change.* Add `turned=True, visited=["4H", "N", "4L"], placed=[], changed=[part]` with the switch False, and assert
  the warning is absent.
- *Related.* The `configuration` guard is redundant on real results: without modes the switch stays None
  (`swbuild.py:4040-4042` is the only setter on an Update). Dropping it also survives. Harmless, and it is the
  stated rule, so keep it, but the "gearbox without modes" assertion at `test_ui_text.py:3323` tests the switch
  being None, not this guard.

**5. Note: the window tests say "as committed" but set `False` literally.** `tests/test_workbook_window.py:2663`,
`:2696`.

- `1c04645`'s message and docstring say *"with the turn finding as committed for 2026"*. If the committed value
  changes, these two still pass on their own value.
- The committed value is guarded by `test_swbuild.py`'s three tests: the finding mutated to True fails 5 tests.
- Reword the docstrings, or set `test_swbuild.COMMITTED_TURN_2026` as those do.

**6. Note: TURN_SHOWN_ELSEWHERE and TURN_SHOWS_EVERYWHERE can both be on screen, in one rare state.**
`ui_text.py:2440-2447`, `:2476-2496`.

- The record line goes in only while the state is fine. A `record_problem` then makes `ok` False after it, so
  `_after_note` shows the job's note, *"Since then:"*, and the state with the record line: two near-identical
  sentences.
- This needs a newer or broken record right after an Update that wrote one. I found it by reading, not by running.
  Otherwise the note replaces the state, and nothing is said twice.

**7. Note: UI-DESIGN's Part-column figure.** `design/UI-DESIGN.md:457`, *"the column holds about 16
(`Sleeve_m1.25_N100` whole)"*.

- That name is 17 characters and fits whole. The `_r2` name at 17 (`Slee…_m1.5_N30_r2`) does not, so the loop
  settles on 16.
- The *…* measures wider than a mono character in the table's font.
- Suggest *"about 17 characters, 16 once shortened"*.

**8. Note: `_fit_part_cells`'s cost.** `workbook_gui.py:930-945`.

- Every paint costs one extra `update_idletasks`. When the cells do not fit, it also calls `workbook_gear_rows`
  once per character count tried, up to 8 times, recomputing every row.
- Calling `ui_text._part_cells(names, chars)` on the painted names would do the same. The cost is negligible at
  tens of gears, so no change is needed.

**9. Note: the shortened cell and the whole name.**

- Under the 18-character rule, names over 18 were already shortened, with no tooltip.
- `076845e` extends that to names the measured room cannot hold (16–18 here, down to 10 in the extreme).
- The head (kind) and the tail (teeth and the `_r2`) are kept, and different parts never share a cell
  (`_part_cells` lengthens a clash, at the floor too). Past the floor the window widens, which I find the right
  thing to give.
- The fixer says sentences name parts whole. The build's status in `WorkbookModesBuilt` names the layout and the
  assembly, not the parts (*"Built 6 parts, …"*). So for a part file's exact name, the user has the output folder
  shown in the Workbook panel. I did not check which sentences name an `_r2` part.
- A tooltip on a shortened cell is the remedy, if the user wants one. It is the user's call, not a defect of this
  change.

---

## The FDrive reading, and what s7 should measure

**The reading.**

- 2H's `FDrive off its axis` (`:247`, `:297`) is expected. The workbook moved FDrive, 2H was shown first, and the
  judgement is taken before 2H's put.
- What needs explaining is 4H and N on place (`:298-299`) against 4L off (`:248`, `:300`). It is also why the run
  ended green: every mode is put while `moved`, and 4L's post-check after its put was clean.

**The fixer's hypothesis** (a configuration with an earlier put keeps its own positions from then on, while the
others share) is **consistent with the log, not established by it, and not contradicted.** At least three causes
coincide in 4L:

1. **The earlier put.** 4L is where the quiet Update had put the train.
2. **The active configuration.** 4L was active when the document was opened, in both Updates (`:143`, `:245`).
   One rival hypothesis is that a put made with another configuration shown does not reach the one active at open.
3. **FDrive free in 4L.** FDrive's only mates are *FDrive locked to FrontDog* and *FDrive meshes FIdler*. It has no
   axis or along mate (`:249-281`, every mate listed). During the quiet put, both were suppressed in 4L alone
   (`:194`), so FDrive was a component no mate holds, the follow-up's case, whose put holds per configuration.
   That put of FDrive moved nothing: FDrive stood at its recorded frame, since the 2H turn did not drive the front
   train.

   The same was true in 2H during the changed Update's put, and 2H's put still reached 4H and N. So "a free put
   splits that configuration" does not explain it alone. It does if only the first such put splits, which is the
   fixer's hypothesis again.

**The findings comment.** *"A put of it shows in every configuration"* overstates. The same log has a put that did
not show in 4L (point 1).

**What s7 should measure.** Each case on a fresh copy of the built E4, every body's frame read through fresh handles
in every configuration after each step, then saved, reopened and read again. Read frames per body, not
`ModeCheck.turned`, which is unjudged while any gear of the joined train is off its place.

- (a) **The active configuration at open apart from the configuration of the first put.**
  - Open with N active.
  - Put the train in 2H with its locks and gear mates off in 2H alone (the app's route), moving FDrive axially and
    the Sun train by a turn. Read 4H, N and 4L.
  - Then put in 4L. Then put in 2H again, to a different place, and read 4L.
  - Repeat with 4L active at open and no earlier put.
- (b) **A no-op put.** A `Transform2` to where a body already stands, in 4L, then a moving put in 2H: does the no-op
  alone separate 4L?
- (c) **A body held during the put against one left wholly free.** The Sun keeps its on-axis and along mates; FDrive
  has every mate off. Separately: does the split follow the body or the configuration?
- (d) As already listed in `W8-REVIEW-9-18.md`:
  - a put of a component no mate holds;
  - s2's turn by W5's drive on a copy no put has touched;
  - **new:** the same turn after an Update has put in another mode. `TURN_SHOWS_EVERYWHERE` and
    `TURN_SHOWN_ELSEWHERE` say *every mode*. If a mode with an earlier put keeps its own place, a user's turn after
    such an Update may not show there, and the sentences hedge only "may stand across".

Until then, the sentences' "may" keeps them true for the hazard. Only *"shows that turn in every mode"* would
overclaim, and only after an earlier put.

---

## What I checked and found sound

- **A1, the condition.**
  - The warning is said exactly when `configuration` is set, the switch is False, `result.turned` holds, no mated
    gear was put and nothing was visited.
  - It is unreachable without modes: `configuration` is set only in `_modes_check`, `swbuild.py:4040`, and the
    switch stays None.
  - The window test shows it whole at 1080 px.
  - Every other state was read in scratch: no warning on True or None, none after a put, none without modes.
- **A3.** The tests do test the committed value.
  - `TURN_PER_CONFIGURATION_ON_2026 = True` in a scratch copy fails 5 tests: the three in `test_swbuild.py` from
    `f746293`/`7ada83d` and two in `test_findings.py`.
  - The Update's field hard-wired True fails 2 (`test_a_turn_in_step_…`, `test_a_quiet_update_that_puts_on_2026_…`).
  - `COMMITTED_TURN_2026` is read at import, before any fixture. No module assigns the finding directly.
- **A4, clause by clause, outside point 1.**
  - 13 `put` calls (`:190`).
  - `SetSuppression2(…, 0, ['4L'])` (`:194`). The 24 `SetSuppression2` calls are 12 mates off and back on.
  - The changed Update showed 2H first (`:295`).
  - The 4H, N and 4L as-built turns (`:68`, `:85`, `:102`) and the 531.913 mm³ clash (`:113`).
- **`f6a2ab7`, `7cbf1ff`, `e63a7f4`.**
  - The docstrings now say what the code does: `put_in` puts the active mode first after a quiet put, `visited`
    holds every other mode after it, and `_modes_put` documents no `check=None` case.
  - The renamed test exists (`test_swbuild.py:6588`).
  - The short `TURN_SHOWS_EVERYWHERE` is true wherever it is said, and so is *"nothing there"*.
- **B1, `_fit_part_cells`.**
  - The arithmetic matches the widget tree: body pads, the right column's grid pads and requested width, and the
    Gears panel's border and pads (as panel reqwidth less table reqwidth). Every other column is
    `max(minsize, slave reqwidth + padx)`, header labels included, as the grid lays it out.
  - The only spanning widget, *No gears yet*, appears only with no rows, when the early return applies.
  - Requested widths need no mapping.
  - No oscillation. Each `_paint` repaints at `PART_CHARS` and refits from scratch, from inputs the Part column
    does not feed. A scratch repaint gave the same cells.
  - The chooser is placed before the fit, and the footer is a separate row. `_mode_chosen` repaints Speeds without
    refitting, but Speeds lines wrap at `END_VIEW` width, the chooser's room is measured at the widest readout and
    the Panel header does not propagate, so the right column keeps its width.
  - At 125 % and 150 % (scratch, `theme.setup(root, s)`), the window is 1350 and 1620 px, as `px(1080)` gives. The
    `_r2` names fit whole there, since the fonts round smaller, and the reducer's cells are as the rows give.
  - At the floor, two parts never share a cell. Rows at the default are unchanged, which the third test pins, and
    no other test relies on the window's cells equalling them for long ids.
- **B2.** The tests are exact. Mutants under Windows Python, each failing
  `test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`:
  - `others` taken from `TABLE_WIDTHS` alone;
  - the right column's pads ignored (8 px);
  - always the floor.

  Nothing was weakened: `0435b8a` and `d7a3074` re-pin to the new sentence, exactly.
- **B3.** `design/canvas/gen.py`, run in the export under Windows Python with `PYTHONUTF8=1`, rewrote every
  `.dc.html` and `canvas.json` byte-identical to what is committed. In the three PNGs (`WorkbookModes`,
  `WorkbookModesBuilt` 2160 × 2219, `WorkbookModesUpdated`), nothing is clipped. The Built footer wraps inside its
  column beside the buttons, and the Speeds sentences wrap inside their panel.
- **B4.** `TURN_SHOWS_EVERYWHERE`, `TURN_STAYS`, `SWITCH_IN_STEP`, `TURN_SHOWN_ELSEWHERE` and `ALREADY_MATCHES`
  appear in `UI-DESIGN.md` verbatim. So do the shared-turn sentence, *"The gears stand where they were turned in
  SolidWorks."* and the quiet sentence for 2H. The two-pair example matches `1f08117`'s output. The only remaining
  copy of the long sentence is ruling 9.18's "shortened from" quote, which is correct.

## What I could not check

- Anything on SolidWorks: another agent is driving it. The FDrive hypotheses are argued from the log alone.
- The PNGs' re-render (`render.py`, Chrome). I compared the `.dc.html` sources byte for byte and looked at the
  committed PNGs.
- The window at a real 125 % or 150 % display. I measured only by `theme.setup` scale in a test.
- Which status sentences name an `_r2` part whole (point 9).
- Point 6's state, which I found by reading only.

## Tests run

- Linux venv, HEAD (`ab0c38c`): `PYTHONPATH=src .venv/bin/python -m pytest -q`, giving `2 failed, 3139 passed, 10
  skipped in 43.37s`. Both failures are the known `tkinter` ones.
- Windows Python 3.13, `git archive HEAD` in `C:\tmp\gg-review-w`, `PYTHONPATH=src`: `python -m pytest
  tests/test_workbook_window.py tests/test_workbook_build.py tests/test_ui_text.py -q`, giving `440 passed in
  116.72s (0:01:56)`.
- Mutants (scratch copies only):
  - **Caught:**
    - `TURN…_2026 = True`: 5 failed in `test_swbuild.py`, `test_findings.py` and `test_swbuild_modes.py`.
    - The Update's switch hard-wired True: 2 failed beyond the `tkinter` pair.
    - `others` from `TABLE_WIDTHS`, the right pads ignored, always the floor: 1 failed each, the `_r2` window test.
  - **Survived:**
    - The `not visited` guard dropped: Linux `2 failed, 3139 passed`; Windows `439 passed, 1 skipped`.
    - The `configuration` guard dropped: Linux, the same.
- Scratch reads: the full status with 1, 2 and 3 crossed pairs, and with pairs in two modes; the warning after
  `earlier_update` `not saved` and `lost`; `train_check` with a gear off its place; the window at scales 1.0, 1.25
  and 1.5; a repaint.
