# W8 review of C's and D's last passes (independent, read-only)

**Verdict: one must fix, two should fix, three notes.** The four commits do what they say, and the state words,
the window's width and the boards agreed with one another at `93708d6`. Since then, a findings commit has changed
what a quiet Update says, and three things still describe the old behaviour: a window test (which fails at HEAD),
a board with its render, and a row of UI-DESIGN §9. The other points are about the chooser's sizing and a Tk trace
that is never removed.

**What was reviewed.** `45479ea` (C: the sentence for gear pairs whose turning an Update could not read; this is not
a state-shortening commit, despite the handoff grouping it with one), `295a214` (C: the Gears table's states fitted
to `GEAR_STATE_CHARS`, and "Neutral" capitalised), `22d0dce` (D: the build test re-pinned to "same as G1"),
`14d1125` (D: the window at 1080 px with modes) and `93708d6` (D: the boards and UI-DESIGN §9). None of the files
they touch has changed since `93708d6`. I judged them at HEAD (`fa4e508`).

**How it was checked.**
- I read each diff and the code it lands in.
- I regenerated every board with `design/canvas/gen.py` under Windows Python, in copies of the tree at `93708d6` and
  at HEAD, and compared the output with the committed `.dc.html` files byte for byte.
- I bisected the one failing window test across the commits after `93708d6`.
- I ran the window's rename test with `-s` to see what Tk reports.
- I looked at `design/renders/WorkbookModesUpdated.png`.

No SolidWorks, no Excel, and no GUI beyond the test suite.

---

## Must fix

**M1. At HEAD the quiet Update with modes no longer says which pairs it could not read. A window test fails, and the
board, its render and UI-DESIGN §9 still show the old sentence.**

- *Evidence.*
  - `tests/test_workbook_window.py:2481`, `test_a_quiet_update_and_a_modes_pick_changed_update_a_gearbox_with_modes`,
    fails at its assert on line 2492. The status now ends at "…since nothing needed changing.", and the
    "Which way RangeSlv and LoDog, and ModeSlv and FrontDog, turn against each other was not checked this time…"
    sentence that `14d1125` pinned is gone.
  - Bisected: the test passes at `93708d6` and fails at `c29ea2e`, `9f21d99`, `5fcaa6a` and HEAD.
  - `c29ea2e` set `findings.SUPPRESSED_GEAR_MATE_SENSE_READ = "answers, marks nothing"` (`findings.py:1320`). By
    ruling 9.16(c), `swbuild._suppressed_readable()` (`swbuild.py:3907`) then reads every sense, so `senses_unread`
    (`swbuild.py:4665`) is empty on the fake.
  - The window test's `mode_findings` fixture (`tests/test_swbuild.py:6033`) says it pins "every finding a build
    with modes reads … never the committed values". It does not pin this finding, so the committed value leaks into
    the test.
- *The same change, elsewhere.*
  - **The board.** At HEAD, `gen.py` writes `WorkbookModesUpdated.dc.html` without the sentence. It is the only board
    out of 31 that differs from what is committed; at `93708d6` all 31 regenerate identically. The committed
    `.dc.html` and `design/renders/WorkbookModesUpdated.png` still show the sentence.
  - **UI-DESIGN.** §9's quiet-Update row (`design/UI-DESIGN.md:1093`) and the board's description (line 1085, "the
    couplings' turning it could not read") also still say it.
  - **The handoff.** `docs/HANDOFF-WORKBOOK.md:555` says "The suite is green", which is not true at HEAD.
- *What I would change.*
  1. **The fixture.** Pin `SUPPRESSED_GEAR_MATE_SENSE_READ` in `mode_findings` (its docstring's own rule).
  2. **The tests.** Keep this test on the unset value, so the unread sentence is still exercised end to end through
     the window. Add its twin with "answers, marks nothing", which says the quiet sentence alone.
  3. **The board.** Regenerate `WorkbookModesUpdated` and its render. It then differs from `WorkbookModesBuilt` only
     by the quiet sentence; either say so in its title, or draw it with the finding unset and say that.
  4. **UI-DESIGN.** Reword the §9 row: the unread sentence is said only while the finding is unset.
  5. **The handoff.** Correct "The suite is green". Note that the finding is measured on 2026 only but is applied on
     2024 as well; handoff step 2 already plans the read on 2024.

## Should fix

**S1. A destroyed mode chooser's trace on `self.mode` stays registered, and fires on every later write.**

- *Evidence.*
  - `widgets.Segmented` registers `variable.trace_add("write", …_paint)` (`widgets.py:645`) and never removes it.
  - `WorkbookWindow._place_mode_chooser` destroys the choosers when the names change (`workbook_gui.py:962`), then
    sets `self.mode` (`:965`, `:981`). Each dead trace then calls `_paint` on destroyed cells.
  - `test_a_mode_renamed_only_in_case_keeps_its_choice` (`tests/test_workbook_window.py:2401`, added in `14d1125`)
    passes. Run with `-s`, it prints `Exception in Tkinter callback` twice, with
    `_tkinter.TclError: invalid command name ".!workbookwindow…!segmented.!frame"`.
- *How it grew.* The pattern dates from `33c4729`, with one chooser. `14d1125` makes it one dead trace per row, and
  every change of names adds more, each re-fired on every later choice.
- *Impact.* In the windowed exe the report goes nowhere, so there is no visible failure: it is a leak and a source
  of noise.
- *What I would change.*
  - Give `Segmented` a `destroy` that calls `trace_remove` on its own trace.
  - In the window tests, make a Tk callback exception fail the test (patch `report_callback_exception`), so a test
    cannot pass over a traceback again.

**S2. The header's 200 px (`MODE_HEADER_ROOM`) is a constant, not the room the header has left.**

- *The code.*
  - `mode_chooser_rows` (`workbook_gui.py:156-167`) puts the chooser in the header whenever its segments total at
    most 200 px, whatever the Speeds readout beside it holds.
  - `Panel`'s header has `grid_propagate(False)` (`widgets.py:429`), so a header that is too full does not widen the
    window. Instead it squeezes the readout's column, which has weight 1, and clips the readout. Neither
    `winfo_reqwidth` nor the 1080 px assertion in `test_the_window_keeps_its_width_with_modes_…` (`:2379`) can see
    that.
- *My estimate, not measured.*
  - With "seen from +Z", four 2-character modes leave room.
  - The readout can also be "seen from each shaft's + end" (`ui_text.py:1210`) when any shaft is not along Z. Then
    the 12 px pad, the title, the readout of about 160 px, the chooser's 200 px and the pads come to more than the
    panel's 416 px inner width.
- *Whether it can happen.* Sliders must stand on a Z shaft (`workbook/modes.py:259`). I found no check that refuses a
  turned shaft without sliders in a gearbox with modes, but I did not build such a workbook to confirm one is
  accepted.
- *What I would change.*
  - Decide header-or-rows from the room actually left: the panel's width less the title's and the readout's
    measures.
  - Add a test that asserts the chooser's right edge lies within the header and the readout is not squeezed.

## Notes

**N1. A mode name of 48 characters or more breaks "every name shows whole, and the window keeps its 1080 px".**
`mode_segment_width` is 8 × n + 16, so for n ≥ 48 one segment is wider than `END_VIEW[0]` (392). `per` then floors to
1 (`workbook_gui.py:166`) and the segment widens the right column. The comment at `workbook_gui.py:107` says each row
is "no wider than the end view", and UI-DESIGN §9 (line 1041) makes the same promise. Nothing caps a mode name's
length (`workbook/model.py:441`, `schema.MODE_NAME`). This is unlikely in practice, but either shorten a long name
head and tail as the Part column does, or say the limit in both places.

**N2. The state column's shortening of a gear name protects one column while the Gear column shows the same name
whole.**
- `295a214` shortens a gear id inside "same as …" to 12 characters (`ui_text.py:882`).
- The Gear and Shaft columns show `gear.id` and `gear.shaft` whole (`ui_text.py:880`; minimum widths 40 and 44 in
  `TABLE_WIDTHS`), and no check caps their length. So a gear id long enough to need shortening, like the test's
  `Gear_Twenty_Chars_AB`, already widens the window through the Gear column.
- The 20-character bound is also checked only in characters (`test_ui_text`). The window's width test measures the
  fixtures' 16-character "same as RangeSlv", never a state at the 20-character limit in Tk's 12 px sans.
- What I would change: measure a 20-character state in the window test. Then either bound the Gear and Shaft columns
  by the same rule, or say in UI-DESIGN §9 that a long id widens the window.

**N3. No board shows the chooser in rows.** `gen.py` draws the rows layout, but every Workbook board has four short
names in the header. The handoff (line 573) lists "the chooser goes to rows above the Speeds lines when its segments
pass 200 px" among the defaults for the user to overrule, yet there is no render of it for them to look at. A board
with `six_modes()` (as in the width test) would show it.

---

## Checked and found sound

- **The shortened states.**
  - Every fixed state is at most 17 characters. The shared-part state applies only to an unbuilt gear sharing a job
    (`index` > 0); a built gear sharing a file still reads "built", so "same as G1" never stands beside a recorded
    part.
  - "changes on Update" and "new part on Build" keep the near-black dot and come from the same branches as before
    (`_built_state`). Dropping "built ·" loses nothing the Part cell does not show.
  - Two different long gear ids are kept apart by `_part_cells`' widening rule, as the test shows.
  - "Neutral" is capitalised only when there is no mode name, and that is tested.
  - No old wording ("built · …", "the same part as …") remains in the code, the tests, the boards or UI-DESIGN; the
    one occurrence left is in a comment that quotes it.
- **The re-pins.** `22d0dce` and `14d1125` change exact strings to the new exact strings; none was loosened or
  deleted. `14d1125` adds a parametrised width test (reducer, both fixtures, long names, six modes) that measures each
  segment's name in the real bold font against its share, plus the rename test.
- **The unread-pairs sentence (`45479ea`).** It reads correctly for one pair, for several, and with three named and
  the rest counted. It is never asked of the user, and the jam sentence is shown whole in the footer. The ui_text unit
  tests still pass, since they build the result by hand.
- **Labels on the end view.** The new order (`preview.LABEL_SIDES`: below right, above right, below left, above left)
  still leaves a shaft at the origin labelled below left: the above-right box overlaps the Y arrow's box. UI-DESIGN §9
  says this order.
- **The window's layout.** *Worked out as* wraps, with B's no-break spaces holding each mode's ratio together. The
  footer's wrap allows for the label's padding. The chooser's rows sit in a frame above `speeds_body`, removed when
  the chooser moves to the header or there are no modes.
- **`gen.py` against the window.** `gen.py` holds no Workbook copy of its own any more: the states, the Speeds lines,
  the chooser's note and its placement all come from `ui_text` and the window's new helpers (`chosen_mode`,
  `mode_placed`, `speeds_panel`, `mode_chooser_rows`). That is why the boards could not drift from the window, only
  from a later change of behaviour (M1).

## Could not check

- The header overflow in S2, which I estimated from font sizes and did not measure. I did not open a Tk window
  outside the test suite.
- Whether a gearbox with modes and a turned shaft passes the checks.
- Any render other than `WorkbookModesUpdated.png`, which I looked at. I did not re-render the PNGs; I compared only
  the `.dc.html` files.
- Anything on SolidWorks.

## Tests run

- Linux venv: `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_ui_text.py tests/test_preview.py`
  - Result: `1 failed, 289 passed`.
  - The failure is `test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`, which imports
    `workbook_gui` and so needs tkinter, which this venv lacks. That test predates these commits (`634f37c`).
- Windows Python, same files: `290 passed`.
- Linux venv: `tests/test_swbuild.py tests/test_findings.py`: `548 passed`.
- Windows Python (a copy of HEAD on `C:`): `python.exe -m pytest tests/test_workbook_window.py
  tests/test_workbook_build.py -q`
  - Result: `1 failed, 147 passed, 1 skipped`.
  - The failure is M1's test.
