# F4, package C, handed back

Package C of PLAN-PRINTED's stage F4 (§5.4, §5.6; `F4-INTERFACES.md` §5, §6.2, §6.7): what the user sees of what a
tooth is rated to take. Written beside package B in this worktree, against F4-0's interface and A's
`gears/strength.py` as of `9b4e27d` (S1's neutral reason for an unrated ring included). No SolidWorks, no Excel.

## Commits

1. `50efc82`: `gui.py`, `ui_text.py` (F4-0's stub filled, and the words round it), `tests/test_strength_form.py`
   (new, 33 tests: 20 pure, 13 on the strip).
2. `fda18e7`: `README.md`, *What a tooth is rated to take*.
3. `6eb13dd`: `design/UI-DESIGN.md` (section *What a tooth is rated to take (F4)*), `design/canvas/gen.py`, the new
   board `PrintedStrength`, the three printed strip boards regenerated, `canvas.json`.
4. This note.
5. After B landed: `design/UI-DESIGN.md` brought to B's words, `WorkbookStrength` and `WorkbookPrinted` written by
   `gen.py`, `canvas.json`, and this note (below).

**No existing test changed.** Suite at `50efc82` with B's work in progress uncommitted in the worktree: **5523 passed,
1 skipped, 5 failed**: the known Tk font test; the three cases of `test_printed_workbook.py:296-311` (B's file, B's
edit in progress); and `test_strength.py::test_the_stubs_are_importable_and_neutral_until_their_packages_fill_them`,
which fails by design now that B's and C's stubs are filled (below). My own file: 33 passed. The Tk files beside it
(`test_print_form`, `test_bore_form`, `test_printed_window`, `test_ui_text`): 516 passed with mine.

## Built

- **The row** (`ui_text.holds_row`), label *Holds once* (F4-0's `HOLDS_LABEL`), in `gui._rows_with_span` after every
  row of `derived_rows` (so after F2's span row and F3's *Bore as cut*); F2's Measured entry stays the panel's foot,
  as `test_print_form` pins. At 17 MPa (`strength.ALLOWABLE_DEFAULT`), the gear's own toothed width, a single load;
  every figure by `strength.newtons`, `newton_metres`, `megapascals`.
- **Which gears** (`ui_text.holds_rating(spec, derived, recipe, crossed=False)`): printed, kind spur, helical or
  herringbone (outside or ring), and rated, or a ring not rated for its tips inside its base circle. None for a
  machined gear, a bevel gear, either gear of a crossed pair (`gui._holding` passes `_crossed()` at show time), a dog,
  a hub or a sleeve by kind, a gear that does not work out, and any other *not rated*.
- **The line under the rows** (`ui_text.holds_line`), in `gui._measured_lines` after every line of F2's, *A:* / *B:* in
  a pair. No pin of `_measured_lines` moved, so the sentence stays under the rows (§5.4's fallback not needed).
- **Laid into its column** (`ui_text.holds_value_lines(value, room, measure)`): see choice 3.
- **README**, **UI-DESIGN.md**, **gen.py** and the boards: as the commits say.

## Every sentence, with the state that says it

The row's value (label *Holds once*):

| State | Value |
|---|---|
| a printed gear that rates (A1) | *about 0.58 N·m · 39 N at 17 MPa* |
| A4 helical / A5 herringbone | *about 0.78 N·m · 49 N at 17 MPa* / *about 0.52 N·m · 33 N at 17 MPa* |
| YS past its range: a ring (A6; A9 *about 2.37 N·m · 62 N at 17 MPa · …*), or an outside gear with a sharp typed Fillet | *about 0.80 N·m · 29 N at 17 MPa · stress factor past its range* |
| a ring whose tips lie inside its base circle (A10) | *not rated: tips inside the base circle* (`not rated: ` + A's `short`) |
| `holds_row(rating, 34)` (no caller yet) | *about 1.16 N·m · 77 N at 34 MPa* |

The line under the rows:

- YS past its range, a ring: *Holds once: the ring's 0.15 mm fillet is sharper than the stress factor's range, which is
  carried past it.* (the fillet as drawn: *0.3 mm* on A9);
- YS past its range, an outside gear (A1 with Fillet 0.1, q_s 11.2): *Holds once: the gear's 0.1 mm fillet is sharper
  than the stress factor's range, which is carried past it.*;
- a ring not rated: *Holds once: not rated:* + A's `why` + *.*, today *Holds once: not rated: its tips lie inside its
  base circle (31.000 mm against 31.010), where a tooth cannot be involute, so the tip load the rating takes is outside
  what it covers.* My test pins the composition and the diameters, not A's clause word for word (A's to word).
- in a pair, *A: * or *B: * before either.

The README's section and UI-DESIGN's are in the files; the README's key phrases are pinned in
`test_the_readme_says_what_the_figure_is_and_is_not`.

## Choices the plan left open, each the coordinator's to rule

1. **The rule of which gears show the row is in `ui_text.holds_rating`**, pure, so the strip, `gen.py` and the tests
   share it; `holds_row` also returns None for any *not rated* but M1's, so the two agree. Its signature keeps
   `holds_row(rating, allowable)`; `allowable` defaults to None meaning 17 (same answer as the stub's 17.0).
2. **An outside gear past YS's range is said too**, as *the gear's* fillet. The plan only names rings, but a Fillet
   typed 0.1 mm on A1 gives q_s 11.2 (the form accepts it), and the row must be true in that state.
3. **The value is laid into its column**, which the plan did not foresee. Measured on the strip: the row as one line
   widened the Derived panel to 528 px in an outside pair and 714 px with a ring (the strip is 460). So
   `_show_derived` breaks it at its own *·* first and at spaces only inside a phrase too long (`holds_value_lines`),
   with the room from the rows' 434 px; and in single mode the empty second column now keeps no minimum width (it
   held 96 px of blank), so a single gear's value is one line (two for a ring past range). A test holds the panel
   at or under 460 px in pair and single mode. The words are the plan's exactly; only the line breaks are new.
4. **The row's label sits at the top of its cell** (`sticky="nw"`) when the value takes several lines; every other
   row is laid as before.
5. **No card for the row**: it is a reading, as *Bore as cut* is. The README says what it is and is not.
6. **The README's title is *What a tooth is rated to take*** (F4-0-REVIEW's S4), its section after *The bore* and
   before *Calibrating your printer*, with a pointer bullet in the Printed gears list and the Allowable stress in the
   Box row of the sheets table. It names the shipped examples as *the workbooks under `tests/fixtures` and the
   gearboxes the tests build*, with §5.3's figures.
7. **Two new boards**: `PrintedStrength` (pair mode, a printed pinion z 20 in a printed ring z 54, module 1, showing
   both columns, the wrap and the *B:* line) and `WorkbookStrength` (a one-mesh printed gearbox, In 2 N·m, G1 z 20 to
   G2 z 40, module 1.5, so exactly one strength warning). `gen.py`'s stand-in measure (6.9 px a character) breaks the
   ring's last phrase after *past* where Tk on this host breaks it after *its*; UI-DESIGN says so.

## Where the interface was wrong or short

- **F4-0's stub pin turns red by design.** `test_strength.py::test_the_stubs_are_importable_and_neutral_until_their_packages_fill_them`
  asserts `ui_text.holds_row(rating_of("A1")) is None` (and B's `mesh_strengths(...) == ()`), so it cannot pass once
  either package fills its stub. It is F4-0's file and not mine to edit: its owner (or the coordinator) should drop the
  neutral asserts, or turn them into "filled" asserts. `holds_row`'s docstring keeps *F4-0's stub* and *package C*,
  so its docstring assert still holds.
- **§5.4's form row did not consider width** (choice 3).
- **Outside gears past range** (choice 2).

## Needs the other package before it can be shown working: done after B landed

Package B landed (`f004334`, note `F4-PACKAGE-B.md`) and F4-0's stub asserts were retired by their owner (`7053532`).
At the coordinator's word, in a fifth commit (design files and this note):

- **UI-DESIGN.md's warning and Results paragraphs** now give B's words as built, read from B's code and its note: the
  warning in each variant B pins (a planet, an idler at 34 MPa, not two-way, a ring past range, a ring not rated with the
  pinion under and past 100 %, neither gear rated), and the Results block's seven states, B's seventh, `UNWORKED`, with
  its wording *the torque here is not given (past a split, not worked out)*, then *Worst share* (with *(its torque is not
  given)* among the meshes not worked out), *Allowable stress (MPa)* in its three forms and the note row.
- **`gen.py` run with B in.** It changed one existing board, `WorkbookPrinted` (the reducer read printed at 10 N·m, now
  *2 new warnings (Meshes!A2, Meshes!A3)*, G1–G2 14.3 times), a real change, committed; no board differed by a date
  only. `WorkbookStrength` is written with exactly one strength warning (*Meshes!A2: G1 and G2: Printed, these teeth
  take about 133 N at the pitch circle, 3.5 times the 39 N G1's teeth are rated to take once at 17 MPa …*) beside G2's
  own form-diameter warning from spur (z 40 at module 1.5, as F4-0 found for Idler_Train's G3), and its `canvas.json`
  entry is in. The PNG renders are still for the Mac.
- The README's *In a workbook* bullet already matched B as built and is unchanged.

## What the reviewer should look at hardest

1. `gui._show_derived`'s room sum and the column-2 minsize change in single mode: whether any layout or test elsewhere
   relied on the 96 px blank column (none in the suite did).
2. `holds_rating`'s gate: `getattr(derived, "printed")` on a helical gear (its section's) and on a ring; a record
   opened as built (`_held_spec`) reaching the row; a pair with a printed gear and a machined Process (impossible on
   the form: Process is one row).
3. That every sentence is true in its state: *rated to take once* is never said beside the 0.7 (the form never applies
   it), and *about* and the MPa are in every figure.

## The coordinator's rulings on F4's review (`F4-REVIEW.md`, `be19cc5`; 2026-11-18, each the user's to overrule)

- **Every choice of packages B and C is accepted**, C's seven among them; no must-fix.
- **The four should-fixes were taken across the packages' files by package C's author**, at the coordinator's word, the
  parallel work being over:
  - **S1** (`gears/strength.py`, `why_tips_inside_base`): the unrated ring's reason now reads *its tips lie inside its
    base circle (31.000 mm against 31.010), where its teeth cannot be involute, and the rating needs an involute tip to
    load*, true of both recipes. So B's warning reads *Meshes row 2: Pin and Ring: Printed, Ring is not rated: its tips
    lie inside its base circle (31.000 mm against 31.010), where its teeth cannot be involute, and the rating needs an
    involute tip to load; the share counts Pin alone.*, and the form's line *Holds once: not rated: its tips lie inside
    its base circle (31.000 mm against 31.010), where its teeth cannot be involute, and the rating needs an involute tip
    to load.* Both are now pinned whole (`test_strength_workbook.py`, `test_strength_form.py`), beside the tests that
    compose them from `ToothRating.why`; `test_strength.py`'s two literals follow. The sentences quoted above in this
    note are as they stood before.
  - **S2, ruled** (`workbook/strength.py`, `_not_loaded_state`): an eighth state, `UNDRIVEN`, worded `NOT_DRIVEN`,
    *not driven here*, for a mesh a shaft of which does not turn in the mode (missing from `Motion.speeds`: the transfer
    cases' front branch in 2H and N, which `Motion.free` lists); *turns unloaded here* is kept for a branch whose shafts
    both turn with no load (RangeBox's stage in H and N, the low range in 2H, 4H and N). Not listed on *Worst share*,
    as an unloaded mesh is not. `test_strength_workbook.py`'s transfer-case test follows, asserting the new state, both
    Results rows and that the front branch never says *turns unloaded here*.
  - **S3** (`README.md`): *so printed as typed they would break, or would not run.*, pinned in `test_strength_form.py`.
  - **S4** (`test_strength_form.py`): a ring drawn by Arcs (recipe B), z 30, is pinned not rated on the form itself:
    *not rated: tips inside the base circle* and *Holds once: not rated: its tips lie inside its base circle (28.000 mm
    against 28.191), where its teeth cannot be involute, and the rating needs an involute tip to load.*
  - `design/UI-DESIGN.md` follows (the two sentences, eight states with *not driven here*); `gen.py` run again changed
    no board.
