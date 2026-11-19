# Review of stage F3 as built (packages A, B and C), before its switch commit

**Read at `3557847` on `printed`**: F3-0 (`062a38e`, `124a7f9`, `21cac8b`), package A (`e855b36`, `bea3a45`), package B
(`0212eae`) and package C (`7051698`, `1dfde10`, `5000c82`), against `docs/PLAN-PRINTED.md` §4 and
`docs/notes-printed/F3-INTERFACES.md`, held to the plan and the code rather than to the hand-back notes. No SolidWorks and
no Excel; no code changed. Every run below was made in scratch copies of the tree (`git archive 3557847`, deleted
afterwards), `PYTHONPATH=src`, the import path checked to be the copy's.

| Run | Result |
|---|---|
| **The suite, switch off** (as committed) | **5384 passed, 1 skipped, 1 failed**: the known Tk font test (`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`). C's figure exactly. |
| **The suite, switch on** (`spur.PRINTED_DEFAULT_IN_PLANS = True` in the file, nothing else) | **5376 passed, 1 skipped, 9 failed**: the Tk test; guard 5; `test_printed_gears.py`'s rim test; and **six of B's own tests** in `tests/test_bore_workbook.py` (M1 below). Guards 1 to 4 and 6 to 10, the bevel and crown strip pins and every other pin of `test_printed_rule.py` pass. |
| **The suite, switch on with the three test changes of §7** (the rim test's two cases from F3-PACKAGE-A.md, guard 5's input as §3 recommends, `pre_f3_desk` turning the switch off itself) | **5385 passed, 1 skipped, 1 failed** (the Tk test). One more than off: the rim test is two cases. |
| The same three changes, switch off | the rim test's default case fails (it must, until the switch), everything else in those three files passes |
| **Probe self-checks, switch on**: `f1_demonstration`, `f2_demonstration`, `f2_probes`, `w9b_demonstration`, `w9c_demonstration`, `w9d_demonstration`, `w9c_probes`, `w9d_probes`, `workbook_assembly_check` | 0 failed each |
| **`design/canvas/gen.py`**, switch off / on | off: every committed board reproduced byte for byte; on: **`PrintedGear.dc.html` and `PrintedSpan.dc.html` change** (the placeholder *0 · printed* becomes *0.2 · printed*; *Bore as cut* 6 and 8 become *6.2 · 6 + 0.2* and *8.2 · 8 + 0.2*), nothing else |

**Verdict.** F3 does what §4 says, the geometry is right, and the rule holds for every part F1 and F2 built. It is **not
yet fit for its switch commit**: the commit as F3-PACKAGE-A.md writes it down (the switch and the rim test) leaves the
suite red (M1, M3), and with the switch on a new row identical to one on record is refused (M2). With those three put
right it is fit for the switch and then for its SolidWorks demonstration, which is still to be written.

## 1. Against §4 and its Done-when

**Built, and as §4 says:**
- §4.1: the allowance on the diameter; the global only when it is not 0; the summed link; the bevel's two blank links;
  the globals of spur, helical, herringbone, bevel, dog and hub; every check on the hole as cut (bore against root,
  one-module rim, printed rim, groove floor, bevel toe); a ring's and a sleeve's typed fields errors at the cell (G9);
  the switch with its one helper `spur.bore_allowance_of`, read at call time.
- §4.1.1: `as_built` threaded through every row of the table (§2 below), and the tenth caller, the window's checks
  (B's `assess`/`plan_parts`, wired by C in `workbook_gui._assess`).
- §4.2: the D exactly as written (§4 below), its bounds, Drive flat refused on a bevel, `drive` in `STRUCTURAL`.
- §4.3: link 12, sidecar 4 by the part's globals (F3-0).
- §4.4: K11's cells and blank words, K3, W9d's columns and `_bore_mm`, the hub, Update in place with no new write.
- The README (the coupon table after F3, *The bore*, ruling 2), `design/UI-DESIGN.md`'s section and the boards.

**Not built** (the first two are F3's still to come, not faults):
- `probe/f3_demonstration.py` and its runs on 2026 and 2024 (`dshape`, `bore`, `kinds`, `update`, `workbook`), its review
  and the runs' review.
- The switch commit (§7), with the boards regenerated there.
- PNG renders under `design/renders` (they need the Mac's Chrome).
- The allowance and the flat in the part's custom properties (A's choice 8; the plan is silent).
- `probe/f1_demonstration.py`'s printed sidecar judgement (3): a rerun of F1's or F2's demonstration after the switch
  builds printed parts at 0.2 and sidecar 4 (F3-0.md decision 13); the F3 demonstration should not lean on those
  scripts unchanged.

## 2. Nothing already built reads as changed

With the switch on, every pin of `tests/test_printed_rule.py` passes: the machined plans, records and `.gear.json`s of
spur, helical, herringbone, bevel, dog and hub (also read through `as_built`), and every printed part of
`F2_built.json` (the four strip parts, the bevel and the crown, the reducer and both RangeBox_Fixed) through classify,
reuse, the footer, `_changed_columns`, `_bore_mm`, `workbook_print`, `form_print` and the strip's count. C's
`tests/test_bore_form.py` holds the strip's real path on every F2 strip part with the switch on. So each of the nine
callers reads them unchanged.

**Trying to break it**, every call in `src` that derives or plans a gear outside `gears/` was read:
- `gearbox._match`/`as_built_job`, `update._part`/`_ignored_fields_as_built`, `made_new_job`, `printout.bore_figures`,
  `update._bore_mm`, `build.check_gear`, `gui.held_spec` (derive, `_update_target`, Update values, Build): through
  `as_built`.
- `gearbox.journal` now writes each job's globals and trig, and the journaled match passes them (F3-0-REVIEW B1): held.
- Reads that derive a recorded spec without `as_built`, each harmless because it reads no bore: `swbuild._caps_with_arc`
  (the tip cap), `printout._derived` (span, d_a and face width for the STEP check), `ui_text._print_backlash`,
  `geometry._place` (placements; bores are not in the layout).
- New parts only, where the default is right: W9c's added gears (`update.py:2504`), `gearbox.py:1461`'s sidecars of
  built jobs (made-new jobs already through `made_new_job`), a pair built from the strip, a copy's parts (record None).
- **One path does change what the user meets with the switch on**: the window's planning with the record (M2). It does
  not misread a part on record; it refuses a new row that would have shared that part.

No path was found that plans a recorded part's hole without `as_built`.

## 3. Guard 5

`tests/test_swbuild_user_work.py:576-579` builds the worker's input by hand: `DocumentValues(P17, _values(printed),
recorded=_recorded(S17), …)`, the globals of `replace(S17, process="printed")` planned as a row **with no record**. With
the switch on those hold `"Bore Allowance" 0.2`, which the part (built from S17, machined) does not, and the worker's
check phase raises `NotAsBuilt` (`swbuild.py:3081`: *"Bore Allowance" is not in this part*) before K11. Run alone, that is
the failure seen.

**Is the input a state a user can reach once F3 lands? No.** The only producer of a part's `DocumentValues` in an Update
is `UpdatePlan` from `update._part`, which now plans through `as_built_job(job, entry.variables)`: for this part, built
with no allowance and typed Printed, that is `_values(as_built(printed, recorded))`, with no `"Bore Allowance"` (guard 4
and B's `test_a_process_change_keeps_the_figure_as_built_either_way` show it end to end). B's analysis holds.

**Recommendation: correct the guard's input, not the worker.**
`doc = swbuild.DocumentValues(P17, _values(as_built(printed, _recorded(S17))), recorded=_recorded(S17), cells=…)`, with
`as_built` imported. Not a loosening: the guard's input stood for *what Update hands the worker for this part*, which
before F3 was `_values(printed)` and after F3 is the as-built form of it; every assertion (the blank meaning, the
sentence word for word, the set-back) is unchanged, and it passes with the switch on and off. Changing the worker to
speak K11 before `NotAsBuilt` would weaken W9a's own test for a document missing a global its record says it holds, for
every user: rejected. Optionally B adds the guard's scenario end to end through `classify` and a press in
`test_bore_workbook.py`, so the hand-built input is never again the only witness. The edit is to a guard, so it is the
coordinator's to allow, in the switch commit.

## 4. Package A, recalculated

My own script from the formulas, then against `spur.d_flat` and the planned ops (evaluating the link texts by
substituting the planned globals, `^` as a power):

| D, F, a | h | R | chord | sweep | area / circle |
|---|---|---|---|---|---|
| 8, 7, 0.2 | 3.1000 | 4.1000 | 5.3666 | 278.24° | 49.1350 / 52.8102 |
| 8, 7, 0 | 3.0000 | 4.0000 | 5.2915 | 277.18° | |
| 8, 7, 0.3 | 3.1500 | 4.1500 | 5.4037 | 278.76° | |
| 8, 7.2, 0.2 | 3.3000 | 4.1000 | 4.8662 | 287.20° | |
| 5, 4.5, 0.2 | 2.1000 | 2.6000 | 3.0659 | 287.74° | |
| 3, 2.5, 0.2 | 1.1000 | 1.6000 | 2.3238 | 266.87° | |

Every figure is the plan's and the code's. On each planned D (and at a −0.1 allowance): the arc starts at the chord's +Y
end `(h, +c/2)`, direction +1, sweeps over 180° through −X; the line starts on the arc's end and ends on its start; it is
vertical at x = h on +X; the drawn radius and chord equal what the links evaluate to, to 1e-6; the chord's link is
`2 * ( ( abs ( R * R - h * h ) ) ^ 0.5 )` with R and h bracketed, no `sqr`. With no allowance the links drop its terms and
no global is added.

- **The allowance on each kind**: spur, dog and hub 0.2 printed and blank (switch on), 0 machined; helical and
  herringbone on their section; bevel in the two blank links and its global, never a flat; ring, sleeve and internal
  bevel none (their typed fields errors or warnings as ruled).
- **Bounds**: `h ≥ 0.25 R` gives F ≥ (5D − 3a)/8, 4.925 at D 8, a 0.2, refused at 4.92 and passed at 4.925;
  `R − h = D − F ≥ 0.3` passes 7.7 and refuses 7.71, at any allowance; the least chord there 3.0790 = 2√(0.6R − 0.09).
  The depth bound is the shaft's own flat, as the re-check asked.
- **The rim test's figures**: m 0.8, z 30: d_a 25.6, h 1.92, d_f 21.76; Bore 20 gives (21.76 − 20)/2 = 0.88 at a typed 0
  and (21.76 − 20.2)/2 = 0.78 at the default; Bore 21 gives 0.38 and 0.28; m 2, z 20, Bore 33: d_f 35, 1 and 0.9. The
  code says each. **A's two-case test** (F3-PACKAGE-A.md) was dropped into a copy: both cases pass with the switch on; the
  default case fails with it off, as it must. Nothing it asserted is dropped (the machined lines stay; the typed-0 case
  keeps F1's figures).
- Two faults in A's words (S1, S2 below): the least Flat is said rounded to nearest, and the rim sentences do not name
  the hole as cut although A's note says every bore check does.

## 5. Package B

- **SolidWorks calls.** Every call the build and Update make for an allowance or a D is one the app makes:
  `CreateArc` (`swcom.py:1741-1750`, the tooth space's arcs), `CreateLine` (`:1752-1756`, the tip chord),
  `SketchAddConstraints` (`:1852-1875`, coincident as for the tip chord's ends, vertical as at `helical.py:644`,
  `bevel.py:962`), `AddDimension2` on an arc and a line (`:1890-1902`; `Dimension("Root", ("R",))`, `bevel.py:942`),
  `FeatureCut4` (`:1959-1967`), `Add2` for globals and links (`:1422-1438`; a link of two globals at `clutch.py:82`, the
  `( abs ( … ) ) ^ 0.5` form in `profile_variables`), `GetConstrainedStatus` (`:1724-1726`), and in Update
  `set_global_variable` (`:1455-1466`). New in kind only: a **major** arc and its dimension read as a radius
  (`findings.ARC_DIMENSION` was read on minor arcs), which `dshape` measures first. B's table is right.
- **Update in place.** A typed allowance on a part with the global, and a Flat change, are one `set_global_variable`
  each (B's tests); none to some, some to none and a Drive change are structural with their sentences. K11 owns
  `"Bore Allowance"` and `"Bore Flat"` (`_GLOBAL_COLUMN`), and `DocumentValues.blank_cells` tells a blank allowance cell
  from a typed one: *0.2 (from its blank cell, the allowance as built)*, set back to the literal. Right; the interface
  had no way to know (B's finding).
- **The journal** (B1) keeps each job's globals in degrees with trig "degrees", and the journaled match passes them;
  an older journal reads "0". Held, and tested.
- **Build again…** keeps the as-built allowance of a part made new (ruling 1, `made_new_job`); a row with no part takes
  the default. Tested with W9d's carry: Sun made new says *its Face width changed* and its old hole 8.
- **W9d's carry**: `_bore_mm` is the hole as cut as built; a D's arc face at R is "bore", its flat a face. Fake only.
- **The hub row** takes all three, at sidecar 4; a Flat change is a value, a Drive change structural in the workbook's
  words.
- **Print files' bore figures** read the record as built: *bore 8 mm* for a pre-F3 part, the allowance and flat
  otherwise.
- **B's choice 6 is not right for the user** (M2). With C's wiring the window passes the record, and a row on record
  is planned as built while a new identical row is planned at the default. Checked in a copy: RangeBox_Fixed built
  before F3, a row `Sun2` added identical to `Sun`, switch on: `assess(…, record=…)` says *Gears row 9: Sun2 and Sun would
  both be Gear_m1.25_N29_P.SLDPRT, but they are not the same gear; give one of them a Part name.*, and Build waits.
  Without the record the two rows share one job and `plan_gearbox` reuses the old part for both, as built. The user
  typed the same gear twice and is told it is not the same gear; before F3 they shared a file. Recommended: read rows
  as built **for the checks only** (B's own alternative), keeping `plan_parts`' jobs as typed so identical rows share a
  file; reuse (per candidate entry), `made_new_job` and `update._part` already make every recorded part's job as built,
  so nothing depends on the jobs being as built in the assessment.

## 6. Package C

- **The form**: Bore allowance, Drive and Flat under Bore; Flat only while Drive is flat; none on a ring; no Drive or
  Flat on a bevel; a hidden row goes across blank. The placeholder says what a blank cuts (*0.2 · printed*,
  *0 · as built*, *0*). Right.
- **A plain machined gear's card is unchanged**: `bore_rows` is empty for a machined gear with no allowance and a round
  bore; the three cards are kept out of `EXPLAINER_FIELDS`; the card pins pass with the switch on.
- **Sentences** checked by running them on every kind, printed and machined, on and off record: *Bore as cut* and
  *Flat as cut* (helical and bevel included), the Bore card's *8 mm, cut at 8.2 → rim …*, the cards' worked lines, the
  Build line *with no bore allowance, as Gear_X was built, since Bore allowance is blank*, the print list. True in each
  state with the switch on. With it off the allowance card's *Blank: 0.2 mm* is untrue, which the switch ends. The
  Drive card says the flat faces a tooth space *the same in every gear* without the helical's section-plane caveat
  the README gives (S4).
- **The README**: the coupon table after F3 types the shaft in Bore and 0 (typed), 0.1, 0.2, 0.3 in Bore allowance,
  and reads old coupons as their offset; *The bore* gives the blanks, hole compensation 0, the D-flat, the fixed angle
  (with the helical's and herringbone's planes) and that the assembly does not model a shaft's flat. Right, and
  written for after the switch.
- **K3** (`ui_text.py`, `_value_under`): *type 0.2 in Gears!V2*, never *clear … again*. **C is right and the interface's
  draft is not**: an in-place change of `"Bore Allowance"` needs a typed new figure (a blank is as built, so it changes
  nothing), so after the Update the part holds the new figure and clearing the cell would keep it. Typing the old figure
  is the only way back whether the old cell was blank or typed, and dropping *again* avoids saying the user typed it.
  `blank_cells` describes the new cell, which is never blank here, so it cannot help. The plan's §4.1.1 K3 row and
  F3-INTERFACES §9 should be brought to C's words.
- C's two finds outside F3 (Open .gear.json not setting Kind; the fixture's blank Flank) are for the coordinator. The
  second looks like an artefact of the fixture being made from `GearSpec` defaults rather than the form, which writes a
  recipe; not verified here.

## 7. The switch commit

It must contain, in one commit with the whole suite run there:
1. `src/gear_generator/gears/spur.py:119`: `PRINTED_DEFAULT_IN_PLANS = True`.
2. `tests/test_printed_gears.py:97-107`: the two cases as F3-PACKAGE-A.md writes them (checked: green on, the default
   case red off). If S2 is taken, its second case's words follow S2.
3. `tests/test_swbuild_user_work.py:578-579`: guard 5's input through `as_built` (§3), on the coordinator's word.
4. `tests/test_bore_workbook.py:48-50`: `pre_f3_desk` sets the switch off for its build and puts it back (it asserts it
   off today, so six of B's tests fail once it is on). B's file; better done by B before the switch commit (M1).
5. `design/canvas/PrintedGear.dc.html` and `PrintedSpan.dc.html` regenerated by `gen.py` (nothing else moves); the PNGs
   stay owed to the Mac.
6. The record of it: PLAN-PRINTED's change record and F3-INTERFACES §13, and K3's words (§6).

With 1 to 4 the suite is 5385 passed, 1 skipped, 1 failed (the Tk font test); nothing else fails, and the probe
self-checks are 0 failed. M2 should land before it (it is not caught by the suite).

## 8. Rulings, must-fixes and should-fixes

**Must-fix**
- **M1** `tests/test_bore_workbook.py:48-50`: `pre_f3_desk` asserts `PRINTED_DEFAULT_IN_PLANS is False`; with the switch
  committed on, six of B's tests fail. Build the pre-F3 desk with the switch off inside the helper (B).
- **M2** `src/gear_generator/workbook/build.py:96` and `:154` (with `workbook_gui.py:850` passing the record): a new row
  identical to a row on record is refused as *not the same gear*. Read the record for the checks only, jobs as typed
  (B), and change B's `test_the_windows_checks_and_jobs_read_a_row_on_record_as_built` to match, adding the
  identical-row case.
- **M3** `tests/test_swbuild_user_work.py:578-579`: guard 5 red with the switch on; correct its input (§3), the
  coordinator allowing.

**Should-fix**
- **S1** `src/gear_generator/gears/spur.py:1653`, `:1658`: the least and most Flat are said rounded to nearest, so the
  advice can be refused: at a −0.1 allowance *type a Flat of at least 5.037 mm* and 5.037 is refused (5.0375 is the
  bound). At 0.3 the bound 4.8875 happens to round up to 4.888, which passes; whether the advice holds depends on the
  rounding. Round the least up and the most down at the shown precision (A).
- **S2** `spur.py:1012-1014`, `:1068-1070`: the rim sentences say *The bore leaves 0.9 mm of rim* for a Bore of 33 cut at
  33.2, without naming the hole as cut, though F3-PACKAGE-A.md says every bore check names the allowance; with the
  switch on that is every printed gear with a bore. Name it as the root check does (`bore_words`), before the switch so
  the rim test's second case is written once (A).
- **S3** `src/gear_generator/workbook/update.py:3238`, `:3260`: `_changed_columns` compares Bore allowance as text, so a
  typed 0.3 cleared on a part made new for another reason says *its Bore allowance changed* while ruling 1 keeps 0.3;
  §4.1.1 says that is never said for a hole that did not change. Compare as built where the entry is at hand, or accept
  and say so (B).
- **S4** `src/gear_generator/ui_text.py:600-605`: the Drive card's *facing the middle of a tooth space, the same in every
  gear* wants the README's *on a helical gear at its section plane* (C).
- **S5** Bring PLAN-PRINTED §4.1.1's K3 row and F3-INTERFACES §9 to C's K3 words; note A's message count (139, not 145)
  is already corrected in its note.

**Recommended rulings**
- *Accept as built*: A 1 (globals after `"Bore Diameter"`), 2 (an allowance with no Bore warns, typed 0 included), 3
  (Flat with Drive round warns), 4 (an allowance that closes the hole is an error), 5 (internal bevel warns), 6 (a
  ring's bad Drive is the ring's error), 7 (two sentences below D ≈ 0.8 − a), 8 (no custom properties now; for later if
  the user asks). B 1 (`_match` returns the as-built job), 2 (`recorded_entry`, a split keeping the old allowance), 3
  (journal in degrees), 4 (`built_variables=None` read as none, the safe side), 5 (`blank_cells`), 8 (an unreadable
  figure is left out and the part made new). C: a pair never read as built; no Drive or Flat on a bevel; Flat sent blank
  while Drive is round; K3's *type the figure* (amend the interface).
- *Change*: B 6, to checks only (M2). B 7, either compare as built or accept with a sentence in the plan (S3).
- *Moot after the switch*: C's note that the cards say 0.2 while plans cut 0.
- *Guard 5*: correct the input (M3).
