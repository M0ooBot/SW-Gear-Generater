# F1, package C, handed back

Package C of PLAN-PRINTED's stage F1 (§2.8; `F1-INTERFACES.md` §5, §6, §8): what the user sees. On branch `printed`,
written beside packages A and B against F1-0's interface. No SolidWorks, no Excel.

## Commits

1. `a66ef2c` The strip's Process and Nozzle rows, `_gear_spec`, `_load_record`, the Backlash placeholder and hint,
   the card's and the Derived rows' printed default; the Workbook window's `_assess` resolving a blank Process and
   its Process line; `tests/test_printed_window.py` (new) and additions to `tests/test_ui_text.py`.
2. `512c76f` Solve's printed mark (A's `Candidate.mark`) shown in the candidate list and the chosen card.
3. `c87195b` The strip calls `pair.mesh_warnings` for printed ring and bevel pairs (the coordinator's word).
4. `b7be972` `design/UI-DESIGN.md` and `README.md`.
5. `b890be8` A test: an old `.gear.json` changed to Printed is one global for Update values.
6. `815f31a` The design boards (`gen.py`, every `.dc.html` regenerated, three new boards).
7. `7e469a0` The window's Process line end to end on B's read, no stand-in.
8. `bc6ec8f` Update's name sentence for parts whose Process it changed, once for the gearbox (the coordinator's word).
9. `74998f6` UI-DESIGN says that sentence. 10. This note.

**Tests changed:** none. `tests/test_ui_text.py` and `tests/test_printed_window.py` only gain tests;
`tests/test_workbook_window.py` was not edited (its pinned texts did not move: no test there reads the whole Workbook
panel, and the window tests pass with the Process row in). `tests/test_printed_rule.py` untouched and green.

**Suite** on a `git archive` of `74998f6` (committed code only, A's and B's in): 4669 passed, 1 skipped, 1 failed,
the known Tk font test. `test_printed_window.py`: 17 tests, all Tk; run twice alone, green.

## What was built

**The strip (`gui.py`).** Gear panel, under Make: **Process** (`Printed` · `Machined`), starting at Printed on every
launch (not remembered in `recent`), and **Nozzle** (mm, placeholder *0.4*, hint *the printer's line width*), shown
only while Printed. `_gear_spec` puts `process` and `nozzle` into each gear; a Machined gear's nozzle goes across
blank. `_pair_spec`'s gears carry it, so Solve (`solve_spec`) and an applied candidate keep it. `_load_record` sets
the row from `spec.is_printed()` (a record before F1: Machined) and the nozzle when printed. Each gear's Backlash
placeholder and hint follow the row. The card gets the form's Process (`explainer(..., printed=)`), so its copy is
right while a gear does not work out. The Derived panel now calls `mesh_warnings` for a pair when it is outside on a
centre distance (as before) **or** either gear is printed, crossed pairs never: a printed ring pair at module 0.5 shows
*Printed, the tip clearance is 0.2 mm, under the 0.3 mm two printed surfaces take; use a larger module.*, a printed
bevel pair at module 1.5 the same at 0.282 mm; machined ring and bevel pairs are told nothing new.

**The Workbook window (`workbook_gui.py`).** `_assess` passes `blank_process=self._blank_process()`: the record read
with `store.read_link_record` (no move), settled by this session's moved-or-copy answer, and dropped when
`store.foreign_workbook` says it is another workbook's; unreadable or newer → no record (Printed; both buttons wait
then anyway). Both callers of `_assess` therefore agree. The Workbook panel gains a **Process** row between Output
folder and Worked out as, wrapping as Worked out as does.

## Every new or changed sentence, with the state that says it

- Process row labels: *Printed*, *Machined*. Nozzle: placeholder *0.4*, hint *the printer's line width*.
- Backlash field, Printed: placeholder *0.3 · printed*, hint *0.3 × m below m1*. Machined: as before (*0.3 × module*,
  *ISO: 0.02–0.05 × m*).
- Derived Backlash row, printed gear, blank Backlash: *0.3 · printed default* (*0.15 · printed default* at module 0.5).
  Typed: the value alone. Machined: *0.45 · 0.3m* as before.
- Backlash card, printed (or form Printed): *How much each tooth is thinned at the pitch circle so the pair does not
  bind: the space grows by this and the tooth shrinks by it, on both gears, so the play in the mesh is twice the
  number. Printed, blank uses 0.3 mm, or 0.3 × module below module 1: room for walls printed a little fat, and a
  starting value until your own prints are measured. A slicer's X-Y compensation does the same job, so use one or the
  other, not both.* Worked line, printed blank: *blank → 0.3 mm · printed default · tooth 2.056 · space 2.656 · play in
  the mesh 0.6*; printed bevel: *… printed default, 0.211 at the toe · …* (20 / 40, module 1.5, face 10).
- Solve, a row A marks: error column *… · thin for a 0.4 nozzle*; chosen card detail ends *· thin for a 0.4 nozzle*.
- Workbook Process line (`ui_text.workbook_process_line`):
  - Printed (typed, any case, or a blank resolved Printed): *Printed, 0.4 mm nozzle* (the Box's nozzle).
  - Blank resolved Machined, row present: *Machined, as built: type Printed beside Process on the Box sheet to print it*
  - the same with no Process row (`process_cell` blank): that, then * (add a row labelled Process)*.
  - Machined typed: *Machined, as the Box sheet says: type Printed beside Process to print it*.
  - A word that is neither: *Process does not read: the Checks panel says why*.
  - Printed with a Nozzle not a number above zero: *Printed; its Nozzle does not read: the Checks panel says why*.
- Update result, default-named parts whose Process the Update changed, once for the gearbox (D10):
  *The 4 parts now printed keep their file names, without the _P a part built printed is named with: Update SolidWorks
  never renames a file, and Build again… makes new parts named with _P if you want the mark.* One part: *Gear_m1.5_N17,
  now printed, keeps its file name, without the _P … makes a new part named with _P if you want the mark.* The other
  way: *…, now machined, keeps its file name, with the _P it was built printed with: Update SolidWorks never renames a
  file, and Build again… makes a new part named without it if you want.* The per-part clause compares names with the
  _P set aside, so it no longer says *(its file keeps its name, which no longer says what it holds)* for Process alone.

Not written, by D11's ruling (B): the (A)-only footer sentence and `_reuse_advice`'s Process case (F1-INTERFACES §8).
The task's "sentences of the new warnings and of the footer in ui_text.py": no §8 warning sentence is ui_text's (A's
are in the gears, B's in the workbook), and the footer's only F1 sentence is (A)-only, so none was added there.

## Choices the plan left open, each the coordinator's to rule

1. The typed-Machined line, and the two unread lines (the plan words only Printed and as-built).
2. The Backlash placeholder *0.3 · printed* and hint *0.3 × m below m1*; the Nozzle hint (the Box note's words).
3. The printed Backlash copy, naming a slicer's *X-Y compensation*.
4. The derived row drops *mm* (*0.3 · printed default*, not the draft's *0.3 mm · printed default*): the Derived rows
   carry no unit, one *mm* heads each column. The worked line keeps *mm*.
5. A bevel's toe figure is in the card's worked line, not the Derived row (§2.1 "the card gives the toe's figure").
6. Process starts Printed every launch, is not remembered; loading a machined record leaves a typed nozzle (hidden).
7. No explainer card for Process or Nozzle: the Gear panel has no card, and adding them to `EXPLAINER_FIELDS` would move
   test_printed_rule's machined `CARD` pins. The hint says what Nozzle is.
8. Solve's mark shown (beyond §2.8's list for C, but §2.5's mark is otherwise invisible).
9. Update's one name sentence (the coordinator asked for it; D10 says the name keeps, so it is said, not changed).
10. **Not built: §2.6's span over k teeth** in a printed gear's Derived panel. It is in §2 (stage F1) but in no package's
    list in §2.8, nor in Done when or the tests owed; C's list is "the backlash readouts' third state, the explainers,
    the Workbook panel's Process line". For the coordinator: build it (C, `derived_rows`, needs a base-tangent formula
    per kind and recipe) or move it to F2 with §3.2.
11. The Gear panel's readout (`Spur · involute curve`) does not name the Process.
12. B's choice 4: the workbook judges a printed crossed pair's clearance; the strip does not (A's `mesh_warnings`
    returns nothing for one, and the strip never calls it for a crossed pair). They differ there.

## Design

`gen.py` draws the Process row from each board's spec: the existing strip boards' specs are built in code, so their
row says **Machined**; `PrintedGear` is the strip as it opens, printed, with the thin-tip warning and the Backlash card.
The Workbook boards resolve a blank as the window does and draw the Process line; `WorkbookBeforeF1` (the reducer built
machined by an app before F1, no Process row: *Machined, as built … (add a row labelled Process)*, every gear built)
and `WorkbookPrinted` (Printed typed: every gear *changes on Update*). Every board was regenerated from the committed
code, so `WorkbookAgain` and `WorkbookInPlace` also took W9 sentences they predated. **The PNG renders are not
redone**: `render.py` runs the Mac's Chrome; a try with the Windows host's from WSL wrote nothing (its scratch and the
profile it made under `C:\Windows\Temp` were removed). The renders were already stale since W9a.

## What needed the others

Written against the interface first; now shown end to end on A's and B's commits: B's read (blank and no row both
`""`, `process_cell`, lower case, the unread word kept as typed after its error) gives every line above in
`test_end_to_end_*`; A's mark and clearance sentences reach the form. Nothing is left waiting on another package.
Not run on SolidWorks (F1's SolidWorks run is the coordinator's).

## What the reviewer should look at hardest

- `WorkbookWindow._blank_process`: the record it reads, the settle and foreign tests, and that `_plan` and the raw read
  at `_show` (only when a fix is chosen) agree; a mutation returning Printed always, or dropping the foreign test, fails
  `test_printed_window` (checked in a scratch copy).
- `workbook_process_line` reading the raw Box for typed-or-blank and `process_cell`, the resolved Box for the word.
- The `mesh_warnings` condition in `_show_derived`: machined pairs must be called exactly as before.
- `_kept_name` with the _P set aside, and `_process_names_kept` reading `update.parts[i].spec` by index as
  `_kept_name` already did.
- That no machined sentence moved: test_printed_rule's `CARD` pins hold.
