# F1, package B, handed back

Package B of PLAN-PRINTED's stage F1 (§2.8; `docs/notes-printed/F1-INTERFACES.md` §5 and §8): the records and the
workbook. On branch `printed`, written against F1-0's interface while packages A and C were written beside it. No
SolidWorks and no Excel: everything below is shown against the fake.

## Commits

1. `a8868e1` K11's words for a printed gear's blank Backlash (`swbuild.py`, `tests/test_swbuild_user_work.py`).
2. `70d8694` The workbook: the Box's Process and Nozzle read, checked and written, the gears given only checked
   values, `template`, the Backlash column's blank words, the printed clearance at each Meshes row, Process in
   `update._SPEC_COLUMNS`; `tests/test_printed_workbook.py` and its fixtures (`tests/fixtures/printed/`).
3. `d54d237` The Meshes row's clearance sentence taken from package A's `pair.printed_clearance_sentence` once A had
   landed it, so the form and the workbook say the same words.
4. This note.

Suite at the last code commit: 4662 passed, 1 skipped, 1 failed, the known Tk font test
(`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`), with A's
and C's commits in. B's files were also run on F1-0's head with A's work not yet committed (A's stubs): the same tests
pass there. `test_printed_rule.py` is green and was not touched. No test was loosened or changed; the only test edits
are additions (`test_swbuild_user_work.py` gains three tests).

## What was built

- **`workbook/model.py`.** `_read_box` keeps a blank or missing Process as `""` (never resolved there), reads the
  word in any case and keeps it lower case (ruling 7), and says anything else once at its cell: *Box!B9: Process is
  Printed or Machined (got 'wood').*, the text kept as typed after the error, as `_check_value` keeps any cell it
  could not read. Nozzle goes through the Box's numeric check, then *Nozzle must be more than zero (got '0').*
  `Box.process_cell` is set to where Process was read, `""` when the sheet has no row labelled Process.
  `Gear.spec_values` passes only checked values into the gears (ruling 3), through two small public helpers,
  `model.checked_process(box)` and `model.checked_nozzle(box)`. `template` (*New workbook…*) writes `printed` and
  `0.4`.
- **`workbook/schema.py`.** The Backlash column's blank words: *printed: 0.3, or 0.3 × module below module 1;
  machined: 0.3 × module*. (They are documentation only; nothing in the app shows `Column.blank` today.)
- **`workbook/checks.py`.** A printed pair's tip clearance under 0.3 mm is a warning at its Meshes row, prefixed
  *G1 and G2:* as the file prefixes its sentences: outside pairs by `pair.tip_clearance`, a pinion in a ring by
  `pair.ring_tip_clearance`, bevel pairs by Gleason's `(WHOLE_DEPTH − WORKING_DEPTH) × module` (0.188 m), crossed
  pairs by `tip_clearance` unshifted. Machined pairs are told nothing new. W7's planetary sentence,
  `report.undercut` and every gearbox-level warning are the same printed as machined for RangeBox, planetary_4to1
  and Risky_Placements (tested); no pair interference check (§2.3).
- **`workbook/update.py`.** `_SPEC_COLUMNS` gains `("process", "Process")`, last; `_changed_columns` reads a missing
  `process` as machined and the word in any case, so a part made new because of Process is carried with *its Process
  changed*.
- **`swbuild.py`, K11's words only.** `_wanted_words` and `_back_words` recognise the printed default by comparing
  `ValueEdit.blank` with `spur.printed_backlash_expression()` stripped as `_blank_meaning` strips it, and say *0.3
  (from its blank cell, the printed default: 0.3 mm, or 0.3 × Module below module 1)* and *set it back to the
  equation IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )*. `ValueEdit.blank` keeps its meaning; every other K11
  sentence is unchanged (the K11 pins hold).
- **The gearbox build and the records** needed no code of B's: with the Box's word in each spec, a printed gearbox
  builds `_P` parts recorded with `process` and `nozzle`, the record at link 11 and each `.gear.json` at sidecar 3,
  and a machined one records no `process` at sidecar 1 or 2 (tested on the fake; the machined bytes are
  `test_printed_rule`'s pins). Update in place needed none either: the Backlash global is one value of each part.

## What a user's gearbox built before F1 meets the first time it is opened, under (B)

Shown on a record W9's own code wrote: `tests/fixtures/printed/RangeBox_W9_record.json` and `RangeBox_W9.xlsx` were
made by running W9's code at `f3c4873` (a `git archive` in a scratch directory, since deleted): RangeBox built on the
fake with W9a's user work (Sprocket-1 locked to Sun, Housing-1, a Keyway and a Groove) read onto the record by a quiet
press, exactly as `test_workbook_in_place_round_trip.Desk` does it. The snapshot keeps the record's text (link schema
10), each part's `.gear.json`, the files on the fake disk, and what W9 said then (its footer, Update's parts, Build
again…'s reuse). `test_a_gearbox_w9_built_opens_machined_with_nothing_changed_and_nothing_written` then shows:

- the workbook has no Process row: Process reads `""` and `process_cell` `""` (the panel's *(add a row labelled
  Process)*, C's);
- `blank_process` of the record is machined, so the assessment's read and spec say machined, no gear plans printed
  and no name gains `_P`;
- Update finds nothing to do (no part changed, the record matches), Build again… reuses all five parts, and W9d's
  columns find nothing changed for any part;
- the footer is word for word what W9 said (the read time masked);
- nothing is written: the record re-serialises to W9's text but for the schema number a write would move, and the
  `.gear.json` texts are as W9 wrote them.

Said Machined in so many words, it opens the same. With Printed typed: every part reads changed on Update in its
`Backlash` global alone (`0.3 * "Module"` to the IIF), with no structural change, no new revision and no put, each
file keeping its name; Build again… makes all five parts new as `_P` parts, and W9d's carry names each gear body's
reason *its Process changed*. On the fake, end to end with the user's work, one Update writes the five Backlash
globals, keeps Lock3, the two components and the features, writes the record at 11 with each part printed and its
`.gear.json` at 3; a second press, and a press with the cell blank again, find nothing to do (the blank now reads
printed, as built). Then a Backlash the user types in SolidWorks is refused by K11 in its printed words.

## Choices the plan left open, each the coordinator's to rule

1. **A Process word that does not read goes into the gears as the spec's blank (machined).** The Box's error refuses
   Build and Update anyway; the gears' own checks run as machined meanwhile. The other answer is `printed`.
2. **Nozzle is checked (a number, above zero) whatever the Process.** A Machined Box with Nozzle 0 is an error and
   refuses Build. The other answer is to read Nozzle only when the resolved Process is printed, which `_read_box`
   cannot know (the blank resolves in `assess`).
3. **The clearance advice says *use a larger module* alone when the pair has no shift**, *or less profile shift* only
   when it has one. F1-INTERFACES §8's draft always named the shift; A's sentence makes the same split, and B now uses
   A's sentence.
4. **Crossed helical pairs are checked** as unshifted outside pairs (`tip_clearance`, depth less two addenda). The
   plan names outside, ring and bevel pairs; a crossed pair is an outside pair of two helical gears. The form does not
   judge a crossed pair (A's `mesh_warnings`, C's call), so here the workbook says more than the strip.
5. **The bevel figure is taken from `bevel.WHOLE_DEPTH − WORKING_DEPTH` in `checks.py`**; the interface names no
   function for it.
6. **The clearance warning is said before the centre-distance checks**, so a printed pair placed off its distance is
   told both.
7. **`template` writes the Nozzle as 0.4**, not blank, as §1.3 says.
8. **Process is the last of `_SPEC_COLUMNS`**, so a part changed in both says *its Teeth and Process changed*.
9. **Beyond the plan, one W9d fix in `_why_part_new`:** a planet's copy (*Planet copy 2*) now finds its row's job
   through `planetary.copy_of`. Before, a copy made new found none and said *its values changed* whatever had
   changed, so a printed RangeBox would have said Process for every gear but the planets. Words only.
10. **The fixture** (78 KB of JSON and a 6 KB workbook) is committed under `tests/fixtures/printed/`, a new folder of
    B's. The record holds only fake paths (`C:\Out\`, `C:\B\`, `C:\Parts\`).

## Found and not fixed (not B's to change, or outside F1)

- **W9d, planet copies made new carry no feature names.** In `update.carry_for`, a body whose part is new looks its
  job up by `c.gear in j.gear_ids`; a planet copy's id is never a row id, so its `names` are `()` (shown with a
  Planet face-width change: `names` 0 for each copy, 6 for every other new body). This predates F1, but typing
  Printed on a planetary gearbox and pressing Build again… meets it for every planet. The fix is the same
  `copy_of` lookup; it changes what W9d's carry hands SolidWorks, so it is left for a ruling.
- **C's Update result says *(its file keeps its name, which no longer says what it holds)*** for every part after
  Printed is typed (`ui_text`'s name note compares the file's stem with the printed default stem, which ends `_P`).
  D10 says only a part built printed carries `_P`, so the clause is true but may read as alarming; C's to word.

## The interface

Nothing in it was wrong for B. It was short in two places, both filled by A after B had started: no name for the
printed clearance's sentence and constant (A added `pair.printed_clearance_sentence` and `PRINTED_CLEARANCE`, which B
now uses) and none for a bevel pair's clearance figure (B computes it from `bevel`'s constants).

## What only B's tests show, and what needs the others

The window's `_assess` passing `blank_process(record)` is C's and has landed (`a66ef2c`), so a W9 gearbox opened in
the app now resolves as above. What the user sees of it (the Workbook panel's Process line, the strip's rows) is C's
and shown in C's tests; everything in this note is shown only through `test_printed_workbook.py` and
`test_swbuild_user_work.py`, against the fake. Nothing of it has run on SolidWorks; F1's SolidWorks run (§2.8, Done
when) is what shows the Update of a W9a master with Printed typed.

## What the reviewer should look at hardest

- `_read_box` and `spec_values`: that a blank and a missing row are both `""`, that only checked values reach a
  gear, and that a workbook written by `to_sheets` from a gearbox built in code still reads back equal.
- K11's recognition of the printed default by string equality with `printed_backlash_expression` stripped: if A ever
  changes the IIF's text, both move together, but a SolidWorks that stores the IIF differently would fall to the
  machined words (it would also differ from what `_value_edits` compares, with spaces squashed).
- The W9 snapshot test: that it is a fair stand-in for a user's gearbox (fake paths, the read time masked in the
  footer), and that *nothing written* is shown as strongly as a pure planning call can show it.
- The clearance check's placement in `_check_mesh` and `_check_turned`, and that no machined gearbox's report moves
  (`test_printed_rule`'s W8 fingerprints and `BEFORE_W7` / `BEFORE_W8` hold).
- The planet-copy change in `_why_part_new` (choice 9).

## The coordinator's rulings on the F1 review (`F1-REVIEW.md`, `be5ae7a`; 2026-11-18, each the user's to overrule)

- **Ruling 2:** every choice above is accepted as the review recommends. Choice 2 (Nozzle checked whatever the
  Process) is accepted for F1, to be revisited if a user meets it. Choice 5 (the bevel figure) is accepted with S4,
  below. Choice 9 (a planet copy's reason) is ruled in as the one change to what a machined gearbox is told.
- **Ruling 3:** choice 9 is kept, and `w9d` has since fixed the same fault its own way (`d496cfd`, reviewed). Where the
  two meet, `w9d`'s code stands: `_why_part_new` looks a planet copy up by its row alone, `why_new_of` gives the
  reasons, and `carry_for` finds a copy's job by its row, which also gives a planet copy made new its feature names
  (the first of *Found and not fixed* above, now fixed on `w9d`). Of B's change only Process in `_SPEC_COLUMNS` stays.
- **Ruling 4:** the review's should-fixes are taken, each by the author of its files.

## After the review

- `91f6a6f` **The merge of `w9d` (`12cf15d`) into `printed`.** One conflict, in `update._why_part_new`, resolved to
  `w9d`'s version by ruling 3. No pin moved: `test_printed_rule.py` pins no planet copy's reason. B's tests agree with
  the merged behaviour as they stood (a printed RangeBox's planet copies say *its Process changed*).
- `f1d36bf` **S4, S6, S7** (A's and B's files, A's author not recalled):
  - **S4.** `pair.bevel_tip_clearance(g1, g2)`, each gear's dedendum less its mate's addendum (0.188 × module for a
    cone pair), is the one figure `mesh_warnings` and `checks._check_turned` judge a printed bevel pair by; tested
    equal to Gleason's at four shaft angles, and the Meshes row's sentence equal to the form's for the same gears.
  - **S7.** A printed bevel Solve row whose gear does not derive with the form's face width is dropped, as a pointed
    row is, where before it was offered unmarked; machined rows as before.
  - **S6.** A printed crossed Solve is tested to mark each row by each gear's own helix angle.
- F1-0's should-fix 4 (a reader of sidecar 2 refusing a printed `.gear.json`) was taken by F1-0's author (`f6fe978`).
