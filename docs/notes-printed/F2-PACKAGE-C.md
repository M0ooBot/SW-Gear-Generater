# F2, package C, handed back

Package C of PLAN-PRINTED's stage F2 (§3.0, §3.1.3, §3.2, §3.3; `F2-INTERFACES.md` §6, §8): what the user sees of the
span over k teeth and of Print files. On branch `printed`, written beside packages A and B against F2-0's interface,
then shown end to end on A's (`b09a036`) and B's (`2d32c03`) commits. No SolidWorks, no Excel.

## Commits

1. `7d92748` The code and its tests: `ui_text.py`, `gui.py`, `workbook_gui.py`; `tests/test_ui_text.py` (additions),
   `tests/test_print_form.py` and `tests/test_print_window.py` (new).
2. `8328263` `design/UI-DESIGN.md`, `design/canvas/gen.py`, two new boards, every board regenerated.
3. `19cff09` `README.md`.
4. This note.

**Tests changed:** none. `tests/test_ui_text.py` only gains tests; `tests/test_print_form.py` and
`tests/test_print_window.py` are new. `tests/test_printed_rule.py`, F1's and W9's tests are untouched and green.

**Suite** at `7d92748` (`PYTHONPATH=src`, the import path checked against this worktree; A's and B's commits in): **5087 passed,
1 skipped, 1 failed**, the known Tk font test
(`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`). C's own:
`test_print_form.py` 18, `test_print_window.py` 15, the F2 block of `test_ui_text.py` about 100; the Tk ones run
alone too, green.

## What was built

- **`ui_text`** (F2-0's five stubs filled, and the words around them): `span_rows`, `span_label`, `span_withheld`,
  `measured_line` (wording `gears.span.measured`, A's, by the coordinator's ruling: no sums here), `span_explainer`
  (the Measured entry's card, kept out of `EXPLAINER_FIELDS` so no machined card moves), `print_refusal` (one sentence
  per B code, LIGHTWEIGHT included), `print_result`, `print_list_text`, `print_bar_line`, and the window's own
  sentences (`PRINTING`, the waits, the close, the list unwritten). `workbook_footer` gains `printing=` (both buttons
  held, *Print files is writing STEP files from SolidWorks…*).
- **The form (`gui.py`).** The span row after *Tooth at pitch* in each column with a figure (`_rows_with_span`; A's
  `span` by the kind's recipe); a **Measured** entry (84 px, mm) under the rows in that column, made once so the caret
  stays; one line under the rows for a reading typed or a span withheld (*A:*/*B:* in a pair); the span's card on the
  caret in Measured (the Teeth diagram: `widgets` is not C's). **Print files** in the footer between Update values and
  Build; the status wraps in the room the buttons leave (`_wrap_footer`; 260 px with Update values hidden, as before).
  The SolidWorks bar's line (`print_bar_line` of `form_print`'s plan); the snapshot carries `revision`. The press:
  B's `form_print`, its refusal said, the Output folder checked, one job (`swbuild.print_parts`), the finish writing
  `print list.txt` by `printout.write_list`. `CloseGuard` names a workbook build's journal only for a build.
- **The Workbook window (`workbook_gui.py`).** **Print files**, the footer's fifth button after Export and Export
  as…; `FOOTER_COLUMNS` moves the build button and Update SolidWorks one column right. `JOB_PRINT` and
  `Job.printing`/`print_plan`; `press_print` (planned again, then B's `workbook_print` from the record, the state,
  Update's plan, the Box's or strip's folder and the strip's snapshot's revision); its finish a standing note writing
  the list; the close, close-anyway, worker-busy and Export-busy sentences in Print files' words.
- **`design/`**: `gen.py` draws the span row, Measured and its line, the span's card, the bar's line and Print files
  in both footers; boards `PrintedSpan` and `WorkbookPrintRefused` added, every board regenerated (each footer gains
  Print files; `PrintedGear` gains its span row). PNG renders not redone (`render.py` needs the Mac's Chrome), as
  since F1. `UI-DESIGN.md`: the strip's bar and footer, §9's footer (five buttons), and a section *Print files and the
  span over k teeth (F2)* with every sentence.
- **`README.md`**: the span and Print files under *Printed gears*, *Calibrating your printer* (§3.2 as instructions,
  Coupon_E's rule for a shaft over 18 mm included), and a paragraph on the window's Print files.

## Every new sentence, with the state that says it

The refusals (`print_refusal`; `tests/test_ui_text.py` REFUSALS pins each exactly):

- GATE_COPY (SAVE_AS_COPY None, every version): *Print files waits until writing a STEP file is measured on this
  SolidWorks; nothing was written.*
- GATE, by year: *Print files waits until writing a STEP file is measured on SolidWorks 2024 (32.5.0); nothing was
  written.* None connected: *Print files needs SolidWorks running and connected; nothing was written.* Changed since
  the plan: *SolidWorks changed since Print files was pressed (2026 (34.1.1) then, 2024 (32.5.0) now): press it again.
  Nothing was written.* (*none connected now* when none is).
- UNSAVED_MARK: *Print files wrote nothing: Gear_m1.5_N20_P has changes from Update SolidWorks that are not saved; save
  it in SolidWorks, then print.* (plural *have … save them*)
- MISMATCHED_MARK: *Print files wrote nothing: Gear_m1.5_N20_P no longer holds what the record says; press Update
  SolidWorks, then print.*
- CHANGES_ON_UPDATE: *Print files wrote nothing: Update SolidWorks would change the values in Gear_m1.25_N29_P (and make
  Gear_m1.25_N13_P new); press Update SolidWorks and save, then print.*; values alone the same without the bracket; new
  alone *… would make Gear_m1.25_N13_P new; press Update SolidWorks, then print.*
- NO_PART: *Print files wrote nothing: G3 has no part yet, and Gear_x is not on disk; build them first, then print.*
  (one clause and *it* for one)
- WORKBOOK_ERROR: *Print files wrote nothing: the workbook as it stands cannot be compared with what is built; the
  footer says why.* (true of each of B's cases: an error, a provisional read, fixes chosen, no Update plan)
- FOREIGN_RECORD: *Print files wrote nothing: the record beside this workbook is another workbook's, so nothing built is
  this workbook's to print yet; Build makes its own.*
- NO_RECORD: *Print files prints a part Gear Generator built: Part1.SLDPRT has no .gear.json beside it, so nothing was
  written.* (no file: *the active part has*)
- NOT_A_PART: *Print files prints the part active in SolidWorks, and Assem1.SLDASM is not a part: make a gear part
  active there; nothing was written.* (no file: without the clause)
- MODIFIED: *Print files wrote nothing: Gear_m1.5_N20_P is changed in SolidWorks and not saved; save it, or close it
  without saving, then print.*
- GLOBALS_DIFFER: *Print files wrote nothing: in Gear_m1.5_N20_P, "Face Width" is 9 where its record says 8; press
  Update values (Update SolidWorks in the Workbook window), or put it back, then print.*
- FEATURE_IN_ERROR: *Print files wrote nothing: in Gear_m1.5_N20_P, User Keyway is in error in SolidWorks; fix it there,
  then print.* (several: *in A, Cut1 and Cut2 are in error in SolidWorks; in B, Hole is …; fix them there*)
- COMPONENT_ONLY: *Print files wrote nothing: Gear_m1.25_N29_P is open only inside RangeBox; close the assembly or open
  the part, then print.*; no assembly: *… is open in SolidWorks but not as the active document; make it active, or close
  it, then print.*; several such: *… are open in SolidWorks but not as the active document; close them, then print.*
  (only one document can be active).
- LIGHTWEIGHT: *Print files wrote nothing: with RangeBox open, Gear_m1.25_N29_P may be a lightweight component of it;
  resolve it there, or open the part itself, then print again.* (no assembly named: *with an assembly open*; several:
  *… may be lightweight components of it; resolve them there, or open the parts themselves*). "May be": B's job cannot
  tell a lightweight component from a part not loaded, and opening the part clears both.
- SOLIDWORKS_REFUSED: *Print files stopped: SolidWorks would not write Gear_m1.5_N20_P.step (errors 1, warnings 0).*,
  or *…: <swcom's sentence>.*
- FILE_CHECK: *Print files stopped: Gear_m1.5_N20_P.step is not fit to print: <reason>.* with the seven reasons of
  §2.3 as drafted.

The result (`print_result`): *Print files wrote Coupon_A.step and its print list in <folder>.* / *… wrote 4 STEP
files and their print list in <folder>.*; after a stop the refusal then *What was written is in <folder>, and its print
list says not to print this set.*; then as each holds: *SolidWorks warns about Fillet3 in Gear_h; it was written as
SolidWorks built it.*; *SolidWorks now marks A.SLDPRT as changed since Print files ran, and nothing was saved: close it
without saving to leave its file as before.*; *The document you had active could not be made active again.*; B's two
extra facts: *Print files opened X and could not close it: close it in SolidWorks without saving.* and *Whether Print
files left any document marked as changed in SolidWorks could not be read; nothing was saved.*; the list unwritten:
*Its print list could not be written (OSError: …), so nothing in that folder says what each file is or whether to print
it: press Print files again for a set with its list.* Green only for a whole set with everything put back.

Around the press: *Print files is writing STEP files from SolidWorks…* (both footers while it runs); *SolidWorks cannot
be reached from here, so Print files wrote nothing. <why>*; *Print files wrote nothing: choose an output folder that
exists; it writes into a print folder there.* (form); *Print files wrote nothing: the output folder … does not exist;
make it, or change it on the Box sheet.* (window); *Print files wrote nothing: the workbook does not read as it is now;
the footer says why.*; *Print files wrote nothing: Export wrote cells that formulas in the workbook may depend on; open
and save it in Excel first, so what is built can be compared with what it says.*; *The strip is busy in SolidWorks;
press Print files when it has finished.*; *A Workbook window is busy in SolidWorks; press Print files when it has
finished.*; *A job from a Workbook window that was closed while SolidWorks had not answered is still running in
SolidWorks; press Print files when it has finished.*; *Print files is running in SolidWorks; export when it has
finished.*; *This window closes once Print files has finished and its print list is written; it stays open if
something needs saying.*; the close-anyway question *SolidWorks has not answered yet: Print files is still running
there, perhaps held up by a dialog open in SolidWorks. Close this window anyway? Its print list will not be written, so
do not print what it leaves in its folder; nothing will be overwritten.*; a job that raised *Print files stopped — …*.

The span: the row *Span over 3 teeth* `11.209`; withheld *Span over k teeth: not one figure on arcs; choose Involute to
measure* / *…: face too narrow to measure: it needs 13.0 mm* / *…: no span: no k has both jaws on the involute*; the
Measured line *Your printer adds 0.041 mm a flank: a backlash of 0.173 mm a gear keeps 0.04 mm of play a flank.*, *Your
printer adds nothing to a flank* / *takes 0.019 mm off a flank*, at the floor *…: a backlash of 0.1 mm a gear, the least
proposed (0.04 mm of play a flank alone would ask less).*, past 0.3 × module *… That is more than 0.3 × module (0.45
mm), the most a gear of this module is given today: whether it should take more is yours to decide (README: Calibrating
your printer, step 6).*, a reading not a number *Measured: type the calipers' reading in mm, a number such as 11.25.*;
the card (`SPAN_CARD_COPY`) and its worked line *k 3 · W 11.209 mm · jaws touch at Ø 30.337 mm*. The bar: *Print files
will write Gear_m1.5_N20_P.step from the active part.* The print list's lines are in UI-DESIGN's F2 section and pinned
whole for one coupon in `test_the_print_list_of_one_coupon`.

## Choices the plan left open, each the coordinator's to rule

1. **The Measured row and line in a pair**: an entry in each gear's column with a figure, one line each prefixed A:/B:;
   two gears with different k get two span rows, each with a dash in the other column.
2. **A withheld span is a line under the rows, not a table row** (the reason does not fit a 96 px column).
3. **The Measured line's wording** (*adds … a flank*, *takes … off a flank*, the floor said with *the least proposed*, the
   0.3 × module sentence pointing to the README's step 6). S6's draft arithmetic (0.22) is not used; the line says A's
   figures (0.173 for 11.291 on the coupon).
4. **The span's card** borrows the Teeth diagram and is not one of `EXPLAINER_FIELDS`.
5. **Print files' place**: the form's footer between Update values and Build; the window's after Export as… and before
   the build button, `FOOTER_COLUMNS` 5 and 6.
6. **Print files is enabled whenever no job runs**; window states B cannot see are said by the window before B's planner:
   a failed read, a read Excel has yet to recalculate, an Output folder not on disk, and **FOREIGN_RECORD** (see below).
7. **A print's finish is a standing note** (as an Export's), never a job note; it writes no record.
8. **WORKBOOK_ERROR reworded** from the draft (*has an error; the footer says which*), which B's choice 7 made untrue for
   a provisional read, chosen fixes and a missing Update plan.
9. **COMPONENT_ONLY for several parts not active** says only *close them*.
10. **The print list's layout**: head, a block a part (*For G2 and G3 · print 2*, sizes and backlash, span, features,
    warnings, *Checked:* the schema as *AP214 (AUTOMOTIVE_DESIGN)*, the unit in words, the size check or why skipped),
    the settings once, and a line on how to measure a span. Machined: *Machined: its backlash is a cutter's, not a
    printer's; no span.* (E4's words, the value being on the sizes line).
11. **The README's numbers**: §3.2's steps 1 to 7 as written, Coupon_E as module 2, 30 teeth with module 1.5 coupons and
    module 1.5, 20 teeth when the shaft is over 18 mm (F2-0's decision 18, accepted).
12. **The strip's footer wrap** now follows the buttons shown (`_wrap_footer`), since three buttons with Update values
    shown would otherwise push the strip past 460 px.

## What I found wrong or short in the interface

- **FOREIGN_RECORD cannot reach B's planner from the window.** B reads it from `update_plan.foreign_record`, but the
  window plans no Update for a record that is another workbook's (`self.record` and `self.update_plan` are None then).
  The window therefore gives `Refusal(FOREIGN_RECORD)` itself after B's plan when B's gate passes
  (`WorkbookWindow._foreign_record`). For a ruling: pass the workbook's path (or the owner verdict) to
  `workbook_print` so the code is B's alone.
- **No code for an Output folder that is not on disk**: C says it, after B's plan, as Build does.
- **`print_bar_line`'s plan is a fresh `form_print` on every derive**, its sidecar read cached by file time.
- B's extra facts (`<title>|close`, `job|flags`) are worded in `print_result`; they are B's choice 10 for the ruling.

## Shown end to end, and what still waits

Shown against the fake with B's real planners, job and `write_list` and the findings patched as a reviewed run would
set them: a coupon built on the form, named on the bar, printed with its list (`test_end_to_end_a_built_coupon_…`);
the built reducer printed whole from the window, the record unchanged, and refused by name while `PART_WINDOW_READ` is
None (`test_print_window.py`). With the findings as committed (all None) every press says GATE_COPY and submits nothing,
on both. Waiting: the probe's reviewed findings, F2's SolidWorks demonstration, and the user's Bambu Studio and
measurements (§3.2). The boards' PNG renders are not redone.

## What the reviewer should look at hardest

- `WorkbookWindow.press_print`: the order (window waits, B's plan, FOREIGN_RECORD after B's gate, folder, worker), and
  that a print job never takes a build's paths (`_collect_job`, `close`, `_worker_free`, `CloseGuard`).
- `_show_derived`: the Measured fields gridded and removed with the rows; the machined panel unchanged
  (`derived_rows` untouched; `test_printed_rule.py` green).
- Each sentence true in every state that reaches it, chiefly WORKBOOK_ERROR, LIGHTWEIGHT and the COMPONENT_ONLY plural.
- `print_list_text` against a STEP set B actually writes (facts keyed by file name or path).
