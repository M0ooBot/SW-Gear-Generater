# F4's review: the stage as built

**Read at `4bba7e5` on `f4`.** That is F4-0 with package A (reviewed in `F4-0-REVIEW.md`, and its should-fixes
`6c99f45`, `9b4e27d`, `7053532`), package B (`f004334`, `6331975`, note `F4-PACKAGE-B.md`) and package C (`50efc82`,
`fda18e7`, `6eb13dd`, `4bba7e5`, note `F4-PACKAGE-C.md`). Every run used `PYTHONPATH=src`, and the import path was
checked to be this worktree's. Nothing was run on SolidWorks or Excel, and no code was changed. My calculations are
scratch scripts (since deleted) that rebuild §5.2's rules apart from `workbook/strength.py`. They take the ratings from
`gears.strength.rate`, which F4-0-REVIEW checked against my own independent geometry.

**Suite at `4bba7e5`:** 5560 passed, 1 skipped, 1 failed. The failure is the known Tk font test
(`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`), run again
alone and failing alone on its shortened labels.

**Verdict: F4 is done.** There is no must-fix. Four should-fixes are below, none affecting a figure.

## 1. Against §5 and its Done-when

**Done-when, item by item:**
- F4-0's pins hold, and its interface was reviewed (`0b886c5`).
- B and C are in with their tests. A1 to A10 are pinned in `test_strength.py`; B1 to B8 in `test_strength.py` and again
  through B's own path in `test_strength_workbook.py`.
- The suite passes but for the font test.
- Exactly §5.5's three pinned lines moved, each named in its package's note: the Box's titles, the Box's order, and
  B's `STRENGTH_SAID` (§4).
- The README, UI-DESIGN (*What a tooth is rated to take (F4)*) and the boards (`PrintedStrength`, `WorkbookStrength`,
  `WorkbookPrinted` regenerated) say what the row, the warning and the block mean.
- This review is the stage's subagent review.

**Not built:**
- the boards' PNG renders, left for the Mac as F3's were;
- the user's own allowable (U-a), which is the user's step;
- what §5.7 leaves for afterwards (U-b to U-e). No figure in §5 is missing.

## 2. Package B by my own calculation

**Every loaded mesh in every mode of every fixture.** I compared:
- planetary_4to1, RangeBox, RangeBox_Fixed and `RangeBox_W9.xlsx`;
- the E4 transfer case and TransferCase_Parallel, every mode;
- Idler_Train at 1 and 0.25 N·m;
- Risky_Placements, Reducer_12to1 and Arc_Move, all marked printed.

My forces come from `checks.check`'s torques (planets: the member's torque over d·N × 1.25; idlers: the largest
non-idler mate's force). Against `report.strength`, my force, weaker gear, its figure and the share agree in every rated
row: **0 mismatches**. That includes:
- **B1, B2:** 92.593 and 88.926 N, 641.5 % and 616.1 %;
- **B3 to B5:** 66.667 N with GI at 28.984, 230.0 %; 57.5 % at 0.25 N·m, with no warning;
- **B6, B7:** 229.885 and 220.782 N, 1364.3 % and 1310.2 % in L;
- **B8:** 335.605 N at 662.3 %, 453.154 N at 721.2 %, 723.563 N at 1428.0 %;
- E4 at 2141.6 % and 2056.8 %, and TransferCase_Parallel at 1152.1 % and 2258.1 % in 4L.

The two-way flag is right everywhere: planets and idlers take the 0.7, and a ring on a held shaft does not.

**The unrated ring's mesh.** I built a planetary with sun 9, planet 12 and ring 33 at module 1, 3 planets, 1 N·m. The ring
is not rated (31.000 mm against 31.010).
- Planet–Ring reads 88.926 N, *Planet (Ring not rated)*, 728.8 %, a true lower bound.
- Its warning gives the planet's sentence, then *Ring is not rated: …; the share counts Planet alone.*, then the remedy.
- *Worst share* reads *Sun–Planet, 758.8 %* and lists *not rated: Ring (tips inside the base circle)*. The lower bound
  never stands unmarked.

**Loaded meshes not worked out (my should-fix of the plan review).** *Worst share* names them:
- TransferCase_Parallel and E4: *not worked out: FDrive–FIdler, FIdler–FOut in 4H and 4L (past a shared output)*;
- an input driving two outputs: *not worked out: G1–G2, G1–G3 (its torque is not given)*;
- an idler meshing three gears: *G1–GI, 246.6 %* first, then the two meshes past it.

The should-fix is done.

**`UNWORKED`, B's seventh state, is true where it is said.**
- *Where it fires.* In my split and idler-of-three gearboxes, kinematics gives no torque past the split and both
  branches reach a turning output. They read *the torque here is not given (past a split, not worked out)*, never *turns
  unloaded*.
- *A stage with nothing held.* B's docstring also names this case. It is refused as an error before it could be rated
  (*a differential is not built by this version*), so the state's *past a split* wording is never said of it.
- *Every *turns unloaded here* checked.* I checked each place the fixtures say it, by kinematics:
  - RangeBox in H and N: the stage spins with nothing on the carrier;
  - E4 in 2H, 4H and N, and TransferCase_Parallel's low range in 2H, 4H and N: a branch reaching no output;
  - the transfer cases' front branch in 2H and N: free.

  None of these is a loaded branch. *No torque here* is said nowhere.

**The one pinned test B moved** (`test_printed_workbook.py:296-336`) is not a loosening.
- It still asserts the printed diagnostics begin with exactly the machined twin's, which keeps §2.3's ruling and W7's
  sentence. `undercut` and `stages` are still asserted equal.
- It now also asserts exactly the six strength sentences that follow, word for word with their figures, in order.
- That is stricter than before, as asked. The sentences' constants sit a few lines above the test; nothing else in the
  file changed.

## 3. Package C

**The row's value.** Every state reads *about … N·m · … N at 17 MPa*. A ring past range adds *· stress factor past its
range*. A ring not rated reads *not rated: tips inside the base circle*, on recipe A and recipe B alike: I checked
m 1, z 30, both recipes, and each gives the row and the line.

**The line under the rows** names the fillet, or quotes A's reason. Each is pinned in `test_strength_form.py`, the
form's path included.

**The row is withheld:**
- for a machined gear: its rows are `derived_rows` exactly, pinned on A1, A6 and A10;
- for a bevel gear: no row and no line, which is what §5.4 says and the README says (*No row for … a bevel gear*);
- for either gear of a crossed pair, and for a dog, hub or sleeve;
- for a gear not rated for any reason but M1's, which is a gear that does not validate.

**An outside gear with a sharp typed Fillet** (A1 at 0.1 mm, q_s 11.2) says *· stress factor past its range* and *the
gear's 0.1 mm fillet …*. That is true, and C's choice is right.

**Width.** `holds_value_lines` breaks the value at its own *·* first, and at spaces only inside a phrase too long. A test
holds the panel at or under 460 px in pair and single mode.

**A machined gear's Derived panel** has the same rows and lines as before. The one layout change is that the empty
second value column no longer keeps 96 px in single mode, for every gear. It held blank space only, nothing visible
moves, and no test in the suite relied on it. I accept it.

**Plainness.** One clause is not plain, and both B and C quote it (should-fix S1): A's reason for an unrated ring ends
*where a tooth cannot be involute, so the tip load the rating takes is outside what it covers*
(`gears/strength.py:144`). It is true, but *the tip load the rating takes is outside what it covers* will not read to a
user. A plain form: *…, where its teeth cannot be involute, and the rating needs an involute tip to load.*

**The README's *What a tooth is rated to take*** tells a user truly what the figure is: ISO's method on the drawn tooth,
the whole load on one tip, secondary sources, the standard unread. It also tells what it is not:
- not a life or a running rating;
- fatigue far lower;
- 15 to 32 % weaker than ISO's generated tooth;
- the 17 MPa basis and where to type one's own;
- the ring cases;
- the 0.7 as an allowance for running;
- what is not covered.

It says plainly that the example gearboxes read 6 to 23 times over because their torques were typed for steel. Its
figures match §5.3.

One word overstates (should-fix S3, `README.md:226`): *so printed as typed they would break*. The review's best estimate
put planetary_4to1 only about 1.3 times past a one-time break. *They would break, or would not run* is the truth.

## 4. Nothing machined or pinned moved, and one rounding home

- **F4-0's hashed pins** hold at `4bba7e5`. They cover the machined Results sheet and every diagnostic of RangeBox,
  RangeBox_Fixed, planetary_4to1, Risky_Placements and Reducer_12to1. A machined gearbox, and a printed one with no input
  torque, get no block and no warning (B's tests).
- **Existing tests.** `git diff 0b886c5 4bba7e5 -- tests` touches only `test_printed_workbook.py` (B's edit above) and
  F4-0's own `test_strength.py` (A's should-fixes, and the stub asserts retired at the coordinator's ruling). Every W9,
  F1, F2 and F3 pin is untouched and passes. No schema number moved.
- **One figure, one rounding.** The form and the workbook give the same figure for the same gear at the same width. Both
  call `gears.strength.holds` and round with `strength.newtons` and `newton_metres`. For example, the 20-tooth
  module-1.5 gear reads *39 N* on the form and *the 39 N G1's teeth* in `WorkbookStrength`'s warning.
- **The width can legitimately differ.** The form rates at the gear's own toothed width, the workbook at the faces'
  overlap (§5.1). The form never applies the 0.7.

## 5. The packages' choices, and the points to fix

**B's choices (its note lists ten).** Accept all:
1. `UNWORKED` and *the torque here is not given (past a split, not worked out)*: true where reached; the nothing-held
   case is refused before it.
2. The sentence without the pair, as F1's.
3. Bevel and crossed words in the third cell, as §6.3's table draws it.
4. *Worst share* lists every unrated gear and crossed or bevel mesh, with A's `short`.
5. A NOT_RATED row shows no force.
6. An unreadable Box figure is said as such.
7. Mixed cell types (a number, or text with its marks).
8. §6.1's word order kept.
9. A row out of mesh in a mode is left out of it.
10. Printed is the Box's Process as `assess` resolved it.

**C's choices (its note lists seven).** Accept all:
1. The gate in `ui_text.holds_rating`.
2. An outside gear past range said.
3. The wrapped value, and column 2's blank minimum dropped in single mode.
4. The label at the top of its cell.
5. No card.
6. The README's title and place.
7. The two new boards.

**Must-fix:** none.

**Should-fix**, none blocking the close:
- **S1.** `src/gear_generator/gears/strength.py:144` (`why_tips_inside_base`): reword the clause plainly, as in §3. B and
  C quote it from there, so one edit fixes the warning, the line under the rows and B's test, which reads it from the
  module.
- **S2.** `src/gear_generator/workbook/strength.py:334` (`_not_loaded_state`, `UNLOADED`): for a mesh whose shafts do not
  turn (free members: the transfer cases' front branch in 2H and N, which `Motion.free` lists), *turns unloaded here* is
  not true. The branch is not driven, and may not turn at all. A third wording, *not driven here*, keyed on a shaft
  missing from `motion.speeds`, would be true. §5.4 named this case *turns unloaded*, so this is a ruling on the plan's
  word, not a slip of B's.
- **S3.** `README.md:226`: *they would break* → *they would break, or would not run*.
- **S4.** `tests/test_strength_form.py`: pin the recipe-B ring not rated on the form, which today is checked only through
  the shared gate.
