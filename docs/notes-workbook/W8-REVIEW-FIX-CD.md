# W8 review of the fixes to the late C/D review (independent, read-only)

**Verdict: no must fix, three should fix, two notes.** The three commits do what
`W8-REVIEW-LATE-CD.md` asked. M1's window test pins both branches exactly. S1's trace goes with its row, and the
conftest fixture catches the traceback that the old code left behind. S2's room is measured from the real widget
tree, and the readout is drawn whole at 100 %, 125 % and 150 %. The points below are:
- one finding the mode fixture still leaves at its committed value;
- one new code path no test reaches;
- one stale line in the handoff;
- the boards' fixed 200 px;
- the render.

**What was reviewed.**
- `08318d7` (M1: the window test, `mode_findings`, the `WorkbookModesUpdated` board and PNG, UI-DESIGN §9).
- `a4ae910` (S1: `widgets.Segmented.destroy`, `tests/conftest.py`).
- `b12838d` (S2: `mode_header_room`, `_label_width`, `_mode_header_room`, `mode_chooser_rows(names, room)`,
  `_mode_layout`, `Panel.title_label`).

None of the files they touch has changed since `b12838d`. I judged them at `2d8fb47`, and confirmed that nothing
they touch differs at `26e565b`. Line numbers are at HEAD.

**How it was checked.**
- I read each diff and the code it lands in.
- I ran the suites on `git archive` exports: the Linux venv in my scratch folder, Windows Python under `C:\tmp`.
- I regenerated every board with `gen.py` under Windows Python and compared them byte for byte.
- I re-rendered three boards with the host's headless Chrome.
- I mutated scratch copies to see which tests fail.
- I wrote throwaway tests in those copies (none committed): a header↔rows flip, the room at three display scales,
  and `Segmented.destroy`'s edge cases.

No SolidWorks, no Excel, no GUI beyond withdrawn Tk test windows and headless Chrome.

---

## Should fix

**S1. `mode_findings` still lets one committed finding into the mode tests: `PLANETARY_PUT_ROUTE`.**

- *What the fixture says.* The fixture (`tests/test_swbuild.py:6033-6049`) says it pins "every finding a build with
  modes reads … never the committed values".
- *Where the build reads this finding.* An Update of a gearbox with a carrier reads `findings.PLANETARY_PUT_ROUTE`
  at `swbuild.py:4419` and refuses unless it is "gear mates off around the puts".
- *Evidence.* In a copy of HEAD with `findings.PLANETARY_PUT_ROUTE = None`, five `mode_findings` tests in
  `tests/test_workbook_modes.py` fail, each with that refusal:
  - `test_after_an_update_with_nothing_to_do_each_fixture_still_turns_in_every_mode[e4_transfer_case]` (`:908`);
  - `test_e4_changed_update_keeps_every_flag_in_every_configuration` (`:991`);
  - `test_e4_put_refused_part_way_leaves_flags_as_recorded` (`:1004`);
  - `test_e4_put_suppresses_and_restores_in_the_configuration_shown_alone_by_the_measured_route` (`:1022`);
  - `test_e4_a_flag_a_put_changes_in_a_mode_already_checked_is_a_failure_naming_the_mate_and_the_mode` (`:1062`).
- *When it started.* The first of these predates the fix: in a copy of `08318d7` with the same mutation, it is the
  one failure. So leaving it unpinned was wrong when the fixer did it, not only after `ff1c4dd` added the other four.
- *Impact today.* None: the pinned and committed values agree.
- *What I would change.*
  - Add `("PLANETARY_PUT_ROUTE", "gear mates off around the puts")` to `mode_findings`, the value probe
    `planetary_put_back` found on 2026.
  - Name it in the docstring beside the suppressed-sense read.

**S2. A header↔rows rebuild with the names unchanged is new in `b12838d`, and no test reaches it.**

- *The code.* `_place_mode_chooser` now rebuilds when `(names, in_header)` changes (`workbook_gui.py:981-982`), not
  only when the names change. This is the path a save takes when it turns a shaft off Z, or back:
  - the readout widens to *seen from each shaft's + end*;
  - the room drops from 172 to 91 px;
  - `2H 4H N 4L` must move to rows.

  The new test opens each spec fresh, so it never flips.
- *Evidence.*
  - With line 982 reverted to `if names != self._mode_layout[0]:`, `tests/test_workbook_window.py` and
    `tests/test_workbook_build.py` still pass (`154 passed, 1 skipped`; the skip is the known Tk flake).
  - A throwaway test fails on that mutation and passes at HEAD. It opens `transfer_case_parallel()`, chooses 4L, saves
    an `Aux` shaft along X+ on Shafts row 9 through `save_in_excel`, then blanks the row. It asserts that:
    - the chooser moves to `_mode_rows` and back to the slot;
    - 4L, then N, stays chosen;
    - `len(window.mode.trace_info()) == len(window.mode_choosers)`;
    - `tk_callback_exceptions == []`.
- *So the code is right.* HEAD keeps the chosen mode and leaks no trace across the flip (S1's fix holds there too);
  only the test is missing.
- *What I would change.* Commit a test of that shape beside
  `test_the_speeds_readout_is_never_clipped_by_the_mode_chooser`.

**S3. The handoff still tells the user the old default.**

- *Evidence.* `docs/HANDOFF-WORKBOOK.md:573-574`, under "Open, for the user to overrule", says "the chooser goes to
  rows above the Speeds lines when its segments pass 200 px".
- *Why it matters.* Since `b12838d` the threshold is the room the header leaves. That is 172 px beside *seen from +Z
  · provisional* and 91 px beside *seen from each shaft's + end · provisional*, so the transfer case's own four
  modes go to rows whenever a shaft is off Z. This is a change the user sees, in the very list the user is asked to
  overrule from.
- *What I would change.* Reword the line as UI-DESIGN §9 now has it (the room the title and the widest readout leave
  in the 416 px header, never more than 200 px), with the turned-shaft consequence.
- *Also in that paragraph.* Line 555's "The suite is green" is true again at HEAD (Windows run below). Item 3 ("D's
  last pass … had no separate review") is now out of date. Both are for whoever next updates the handoff.

## Notes

**N1. `gen.py`'s fixed 200 px agrees with the window only for the boards that exist.**

- *Where the claim is too wide.* The comment at `design/canvas/gen.py:929-931` says the 200 px is "the same answer for
  every board's names beside a seen-from-+Z readout". That holds only for choosers of at most 172 px. The fixer's
  own test case `(five=True, turned=False)` is a 200 px chooser beside *seen from +Z*: the window puts it in rows,
  while `gen.py` would draw it in the header.
- *Today's boards.* No board differs. All three mode boards draw `2H 4H N 4L` (one 128 px Segmented) beside *seen from
  +Z*, which the window also puts in the header. Every board regenerates byte-identical.
- *What I would change.* Make the drift loud rather than silent. One way: have `gen.py` assert that a header chooser
  is at most 128 px, or that the readout is *seen from +Z*. Another: pass `mode_chooser_rows` a `room` from the two
  figures UI-DESIGN §9 quotes (172 and 91, at 100 %).

**N2. The redrawn PNG is a faithful drawing of the board. It differs from its neighbours only where today's Chrome
sets text a little wider: let it stand.**

- *The board.* `design/renders/WorkbookModesUpdated.png` is 2160 × 1989 and shows the committed `.dc.html` whole:
  - the quiet sentence on two footer lines, ending at "since nothing needed changing.";
  - nothing clipped;
  - the chooser in the header beside *seen from +Z*;
  - every panel at the same heights as the old render.
- *Line count.* It is three footer lines fewer, not two: the old render's sentence ran to five lines (2084 → 1989,
  95 px).
- *Reproducible.* My headless render of the committed `.dc.html` on this host (`render.py` with the Windows Chrome
  path) is byte-identical to the committed PNG.
- *Out of family, and why.*
  - The text is about 1 % wider than in `WorkbookModesBuilt.png` and `WorkbookModes.png`, so Checks' Q6 wraps "so the
    bottom / of the working flank", where `WorkbookModesBuilt.png` has "bottom of / the working flank".
  - That comes from the environment, not the board. Re-rendering `WorkbookModesBuilt` and `WorkbookModes` here today
    gives the same dimensions and the same Q6 wrap as the new PNG, and differs from their committed PNGs. Those were
    drawn under another Chrome or font state.
- *What I would change.* Nothing now. The next time renders are redrawn, redraw the three mode boards together, so
  the family matches.

---

## Checked and found sound

### M1 (`08318d7`)

- **Both branches pinned exactly.** `test_a_quiet_update_and_a_modes_pick_changed_update_a_gearbox_with_modes`
  (`tests/test_workbook_window.py:2544-2580`) is parametrised:
  - with "answers, marks nothing", the status equals `QUIET_UPDATE_WITH_MODES` and nothing after it;
  - with None, it equals that plus the whole unread sentence.

  Both use `==`. The value is set by the test's own monkeypatch after `mode_findings`, so it wins.
- **Pinning in `mode_findings` changes no other test's meaning.**
  - `SUPPRESSED_GEAR_MATE_SENSE_READ` and `POSITIONS_PER_CONFIGURATION_ON_2024` are pinned to the values already
    committed (`findings.py:1320`, `:1257`).
  - The tests that need the unread branch set None themselves (`test_swbuild.py:6530`, `:6556`).
  - The 2024/2026 switch is tested per year in `test_swbuild_modes.py:248`.
- **The board.** `WorkbookModesUpdated.dc.html` is what `gen.py` writes at HEAD. All 31 boards and `canvas.json`
  regenerate byte-identical under Windows Python with `PYTHONUTF8=1`.
- **UI-DESIGN.** §9's board line (`design/UI-DESIGN.md:1092-1094`) and the quiet-Update row (`:1101`) say which
  sentence goes with which value, as `swbuild._suppressed_readable` (`swbuild.py:3907`) decides it.

### S1 (`a4ae910`)

- **`Segmented.destroy` (`widgets.py:649-656`)**, checked on Windows Python with a throwaway script:
  - called twice: no error, no trace left;
  - parent destroyed (Tkinter's recursive `destroy` reaches the override): no trace left, and a later write raises
    nothing;
  - Tcl variable unset under the row: no error.
- **`trace_remove` raising.** The widget is then left alive, since `super().destroy()` is skipped. Nothing in this code
  can make `trace_remove` raise (the row holds its variable), so I make no point of it. A `try/finally` would close
  it if anyone wants it.
- **No other widget has the leak in practice.** `Field` (placeholder trace and `after_idle`, `widgets.py:521-524`) and
  `Check` (`:731`) also never remove their traces. But neither is built in `workbook_gui.py`, and `gui.py` builds its
  own once, over variables that live exactly as long as the widgets.
- **The conftest fixture.**
  - It patches `tkinter.Tk.report_callback_exception` through `monkeypatch`, which it depends on. The undo is
    therefore torn down after the fixture's own check, and runs whether or not the test fails.
  - It checks after `desk`'s teardown, since autouse fixtures are set up first, so exceptions raised while windows
    close are caught too.
  - It does nothing without tkinter: the Linux venv's full run is unchanged.
  - With Windows Python, every Tk-using file passes with it on: `test_workbook_window`, `test_workbook_build`,
    `test_ui_text`, `test_gears_clutch`, `test_preview`, `test_gui_spec`, `test_workbook_export`. Each test makes and
    destroys its own root, so a stray `after` cannot carry into the next test.
  - A failure is reported as a teardown ERROR, not a FAILED. That is fine, and still a non-zero run.
  - Background Tcl errors (`bgerror`) do not pass through `report_callback_exception` and are not caught. That is a
    limit, not a regression.
- **Mutation.** With the `trace_remove` lines deleted, the fixture fails `test_a_mode_renamed_only_in_case_keeps_its_choice`
  and `test_the_chosen_mode_is_kept_across_a_save_while_a_mode_of_that_name_is_there` (both as teardown errors), and
  the new trace test fails.

### S2 (`b12838d`)

- **The arithmetic matches the widget tree.**
  - The header is the Speeds panel's inner frame, as wide as the end view's: `px(392) + 2·px(12)`.
  - The pads are `px(12)` before the title, `(px(8), px(12))` around the readout and `(px(8), px(12))` around the slot:
    `SPEEDS_HEADER_PADS`.
  - The chooser's `Segmented` asks exactly `px(seg·n)`, its ring included; the test asserts `winfo_reqwidth`.
  - `_label_width` is the label's font measure plus `2·(padx + bd + highlightthickness)`, which is Tk's label request.
    For the title it equals `winfo_reqwidth` (48, 55 and 67 px at 1, 1.25 and 1.5).
  - At equality the three columns total the header exactly, and nothing shrinks.
- **Display scale.** I ran the new test and the width test with `theme.setup(root, scale)` patched in a scratch copy.
  All cases pass at 1.25 and 1.5.
  - The room measured at each scale:

    | Scale | Beside *seen from +Z* | Beside *seen from each shaft's + end* |
    |---|---|---|
    | 1 | 172 px | 91 px |
    | 1.25 | 234 px | 140 px |
    | 1.5 | 274 px | 156 px |

  - Fonts do not scale linearly, so a chooser of 173–187 design px (for example two 9-character names, 176 px) is in
    rows at 100 % and in the header at 125 %. Either is right by the rule.
  - UI-DESIGN's 172 and 91 are 100 % figures in Segoe UI, which it could say.
- **No jumping.**
  - The room uses the widest readout of any mode, with " · provisional" always added. The test cycles every mode with
    recalculation off and on and asserts the same placement each time.
  - Dropping the provisional tag fails the two cases it should.
  - Removing the room altogether fails the three non-header cases.
  - "Any mode's" cannot be told from "the chosen mode's" by a test, because `seen_from` is set per shaft from the spec
    (`workbook/kinematics.py:149`), so every mode reads the same. The maximum is defensive, and harmless.
- **Edge cases.**
  - No modes: no call to `_mode_header_room`, `(False, [])`.
  - One mode: header if it fits.
  - A name wider than the room: rows.
  - A name wider than 392 px: N1 of the late review, ruled "leave".
  - Resizing: the right column has weight 0 and the end view fixes its width.
  - A missing font: Tk measures the fallback it uses, so the arithmetic stays self-consistent.
- **The test is real.** `test_the_speeds_readout_is_never_clipped_by_the_mode_chooser` fails three of four cases with
  the room removed (the readout's `winfo_width() < winfo_reqwidth()`), and two with the tag removed.
- **No board differs from the window** (N1), and UI-DESIGN §9 (`:1043-1056`) states the rule as built.

### Tests

None was weakened, deleted or skipped. `08318d7` turns one exact assertion into two exact ones; `a4ae910` and
`b12838d` add tests.

## Could not check

- A real 125 % or 150 % Windows display. I only simulated the scale through `theme.setup(root, scale)`.
- Fonts other than this host's Segoe UI and Consolas.
- The Mac or other environment that drew the neighbouring PNGs.
- Anything on SolidWorks or Excel.

## Tests run

- Linux venv, export of `2d8fb47`: `PYTHONPATH=src .venv/bin/python -m pytest -q`
  - Result: `2 failed, 3083 passed, 10 skipped in 46.16s`.
  - The two failures are the baseline pair, `No module named 'tkinter'`.
- Linux venv: `tests/test_swbuild.py tests/test_workbook_modes.py tests/test_swbuild_modes.py tests/test_findings.py`
  - Result: `693 passed in 4.81s`.
- Windows Python, export under `C:\tmp`: `python.exe -m pytest tests/test_workbook_window.py
  tests/test_workbook_build.py tests/test_ui_text.py tests/test_gears_clutch.py tests/test_preview.py -q`
  - Result: `457 passed in 100.69s (0:01:40)`.
- Windows Python: `tests/test_gui_spec.py tests/test_workbook_export.py`
  - Result: `29 passed in 1.49s`.
