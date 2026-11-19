# F4, package B, handed back

Package B of PLAN-PRINTED's stage F4 (§5.2, §5.4, §5.6; `docs/notes-printed/F4-INTERFACES.md` §4, §6.1, §6.3): each
Meshes row's teeth worked out mode by mode against what they are rated to take once, the warning at a Meshes row and the
Results sheet's block. On branch `f4`, written against F4-0's interface while package C was written beside it in the same
worktree. No SolidWorks and no Excel.

## Commits

1. `f004334`: `workbook/strength.py` (F4-0's stub filled), `workbook/checks.py` (`Report.strength` and `_check_strength`,
   one call at the end of `check`, before `worked_out_as`), `workbook/export.py` (the block after the box size), the new
   `tests/test_strength_workbook.py` (33 tests) and B's one edit in `tests/test_printed_workbook.py`.
2. `6331975`: PLAN-PRINTED §5.2's opening reworded (the re-check's wording should-fix, F4-0's decision 14).
3. This note.

**Suite** (`PYTHONPATH=src`, the import path checked to be this worktree's), at `6331975` with C's commits and A's
`7053532` in: **5560 passed, 1 skipped, 1 failed**, the one the known Tk font test
(`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`). Before A's
`7053532` landed, F4-0's stub pin (`test_strength.py::test_the_stubs_are_importable_and_neutral_until_their_packages_fill_them`)
failed by design once B's body was in; A's author has since retired it at the coordinator's ruling. **Probe
self-checks**, each **0 failed**: `f1_demonstration`, `f2_demonstration`, `f2_probes`, `f3_demonstration`,
`w9b_demonstration`, `w9c_demonstration`, `w9d_demonstration`, `w9c_probes`, `w9d_probes`, `workbook_assembly_check`.
F4-0's machined pins hold. Four mutations of the module (no 1.25, no idler passing, no seventh state, no two-way) each
turn `test_strength_workbook.py` red.

**The one pinned line moved** is §5.5's third: `test_printed_workbook.py::test_printed_gearboxes_carry_the_gearbox_warnings_they_carry_machined`
(RangeBox, planetary_4to1, Risky_Placements) now asserts the printed gearbox's diagnostics are exactly its machined
twin's, then B's sentences, word for word with their figures, in order (`STRENGTH_SAID`). Not a loosening: it still pins
§2.3's ruling and W7's sentence, and allows nothing new but the six sentences it names. The sentences' constants sit
just above the test, a few lines past §5.6's *296-311*; nothing else in that file changed.

## What was built

- **`mesh_strengths(spec, report)`**: `()` unless the Box's Process (as `assess` resolved it) is printed and the first
  input (the first shaft with role input and a speed, kinematics' own) has a torque that is not 0. Then, in the Meshes
  sheet's order and each mode's, one `MeshStrength` per parallel Meshes row and mode, and one per bevel or crossed row
  (mode `""`). Rows with a sleeve, dog or hub, rows not laid out and rows laid out with a problem give nothing; a row a
  slide takes out of mesh in a mode is left out of that mode.
  - Loaded only when both shafts are in `torques` (0 counting) or `held` in that mode.
  - A planetary mesh (a gear on a carrier): `2000 T_member / (d_member · N)` × 1.25 for N ≥ 2, N counted from the placed
    copies; T from `torques` or `held`.
  - Any other: the larger of `2000 T / d` over its gears with T > 0; an idler (a frame gear whose shaft carries exactly
    0) takes the largest force its non-idler mates give, a chain of idlers (meshes between two idlers) sharing one figure.
  - b = min(faces' overlap, each `strength.toothed_width`); each gear `strength.holds(rating, allowable, width=b,
    two_way=shaft torque exactly 0)`; the share over the smaller, that gear the weaker (the first of two equal).
  - One gear not rated (M1's ring): state RATED, the share over the other alone, the ring in `unrated`. Neither rated:
    NOT_RATED.
  - Not loaded: NOT_SHARED when a shaft is in `past_split`; UNWORKED (below) when both shafts turn and one that carries
    no torque is, or reaches through turning shafts that carry none, a turning output; else UNLOADED.
- **`warning_sentence(rows, allowable, typed)`** and **`checks._check_strength`**: §6.1's sentence, without the pair;
  the check puts *a and b:* before it at `spec.cell("Meshes", row, "a")`, as F1's clearance warning.
- **`results_rows`**, **`worst_row`** and the words, in `workbook/strength.py`; `export.results_sheet` writes them after the
  box size and its *Not in the box size* row, behind a blank row, when `report.strength` is not empty.

## Each warning, in full, and the state that writes it

One per Meshes row at most, naming the mode with the largest share; nothing when every share is at or under 100 % and no
gear is not rated in a loaded mode (B5).

- *Share past 100 %, a planet the weaker, modes, blank allowable* (RangeBox, row 2):
  > Meshes row 2: Sun and Planet: Printed, these teeth take about 230 N at the pitch circle in L, 13.6 times the 17 N
  > Planet's teeth are rated to take at 17 MPa (provisional: type your own in the Box's Allowable stress): 24 N once,
  > with an allowance of 0.7 because a planet's teeth are loaded in both directions as the gearbox runs; the load is
  > shared by 3 planets, one taking 1.25 of an even share. Use a larger module, a wider face, less torque, or your own
  > tested allowable. An estimate for teeth printed flat, with the whole load on one tooth's tip: not a running rating;
  > heat, wear and creep are not worked out.
- *An idler the weaker, a typed 34 MPa* (Idler_Train): *…, 1.2 times the 58 N GI's teeth are rated to take at 34 MPa:
  83 N once, with an allowance of 0.7 because an idler's teeth are loaded in both directions as the gearbox runs. Use …*
- *Not two-way, no modes* (Risky_Placements, row 4): *Meshes!A4: G5 and G6: Printed, these teeth take about 724 N at the
  pitch circle, 14.3 times the 51 N G5's teeth are rated to take once at 17 MPa (provisional: type your own in the Box's
  Allowable stress). Use …*
- *One planet*: no sharing clause.
- *A ring past YS's range the weaker*: *… times the 29 N Ring's teeth (its 0.15 mm fillet is sharper than the stress
  factor's range, which is carried past it) are rated to take once at 17 MPa …* (unit-tested; no gearbox here has a ring
  weaker than its pinion).
- *A ring not rated, the pinion at or under 100 %* (a 15-tooth pinion in a 33-tooth ring, 0.05 N·m):
  > Meshes row 2: Pin and Ring: Printed, Ring is not rated: its tips lie inside its base circle (31.000 mm against
  > 31.010), where a tooth cannot be involute, so the tip load the rating takes is outside what it covers; the share
  > counts Pin alone.

  The clause after *Ring is not rated:* is `ToothRating.why`, package A's, quoted (A's author reworded it during this
  run; B's test reads it from `gears.strength`, not a literal).
- *A ring not rated and the pinion past 100 %* (2 N·m): one warning, the full sentence for Pin, then the ring's sentence,
  then *Use …*.
- *Neither gear rated, loaded*: *Printed, A is not rated: …; B is not rated: …; so no share is worked out.* (not met in
  any gearbox here).

## Each Results row, and the state that writes it

Head: *Tooth strength (printed) | Mode | Force (N) | Weaker gear | Rated to take (N) | Share used (%)*.

| State | Row |
|---|---|
| RATED | *Sun–Planet \| L \| 229.885 \| Planet \| 16.851 (0.7) \| 1364.3*; force to 0.001 N and share to 0.1 % as numbers; the figure a number, or text with *(0.7)* and/or *(stress factor past its range)* |
| RATED, a ring not rated | *Pin–Ring \| \| 266.667 \| Pin (Ring not rated) \| 19.161 \| 1391.7* |
| UNLOADED | *Sun–Planet \| H \| — \| \| \| turns unloaded here* |
| NOT_SHARED | *FDrive–FIdler \| 4H \| — \| \| \| the torque past a shared output is not shared out (not worked out)* |
| UNWORKED | *G1–G2 \| \| — \| \| \| the torque here is not given (past a split, not worked out)* |
| NOT_RATED | *A–B \| L \| — \| \| \| not rated: A (short), B (short)* |
| BEVEL, CROSSED | *G1–G2 \| \| not rated: a bevel pair* (or *a crossed pair*) |
| Worst share | *Worst share \| LayPin–LoGear in 4L, 2258.1 % \| not worked out: FDrive–FIdler, FIdler–FOut in 4H and 4L (past a shared output)*; *Pin–Ring, 1391.7 % (Ring not rated) \| not rated: Ring (tips inside the base circle)*; *— \| not rated: G1–G2 (a crossed pair)*; *— \| not worked out: G1–G2, G1–G3 (its torque is not given)*; no third cell when there is nothing to list |
| Allowable | *Allowable stress (MPa) \| 17 \| blank: provisional, type your own in the Box's Allowable stress*; *34 \| the Box's*; a figure that does not read: *17 \| the Box's does not read as a figure above zero: provisional, type your own there* |
| Note | *An estimate for teeth printed flat, the whole load on one tooth's tip: rated to take once, not a running rating. Heat, wear, creep and load across layers are not worked out.* |

*No torque here* is said nowhere (a test holds it for TransferCase_Parallel). A machined gearbox, and a printed one with
no input torque, have no block and no warning.

## Choices the plan left open, each the coordinator's to rule

1. **A seventh state, `UNWORKED`, with its wording `NOT_GIVEN`** (*the torque here is not given (past a split, not
   worked out)*), added after the stub's names. **The interface is short here**: its two wordings cover J17's pruning
   and a shared output, but W3's own split (one shaft driving two branches, with or without modes), a gear both idling
   and driving, and a stage with nothing held also leave a loaded, turning branch with no torque. Calling those *turns
   unloaded here* would repeat the error the review's S3 removed. It is told by reachability: a shaft of the mesh that
   carries no torque is, or reaches through turning shafts that carry none, a turning output. No committed gearbox meets
   it; a test builds one (`split`). The *Worst share* row names such meshes too, *(its torque is not given)*.
2. **`warning_sentence` returns the sentence without the pair**, as `pair.printed_clearance_sentence` does; the check
   prefixes *a and b:*.
3. **A bevel or crossed row puts its words in the third cell**, after a blank Mode, as §6.3's table draws it; §6.3's
   bullet says *the second cell*.
4. **The *Worst share* list** names every gear not rated in any parallel Meshes row (loaded or not) and every bevel and
   crossed mesh, then the loaded meshes not worked out grouped by their modes and reason. The reason is A's `short`,
   *tips inside the base circle*, where §6.3 wrote *its base circle*.
5. **A NOT_RATED row shows no force**, as the interface's `force` (None unless RATED) has it.
6. **A Box figure that does not read** says so on the Allowable row rather than *blank*.
7. **The figure's cell mixes types**: a number when plain, text when marked *(0.7)* (§6.3 asks both).
8. **The warning keeps §6.1's order** (the figure with the 0.7 first, *N once* after the colon); F4-0's review allowed a
   reorder and none was made. *Times* is `strength.times` of the share, so 115.03 % reads *1.2 times*.
9. **Out of mesh**: a row a slide takes out of mesh in a mode has no row for that mode (§5.2's *in each mode in which it
   is in mesh*). No committed gearbox meets it.
10. **Printed** is the Box's checked Process after `assess` (so D11's blank reads as the window resolves it); a
    `check` called directly on a spec built in code is machined unless it says printed.

## What the reviewer should look at hardest

- `_not_loaded_state` and `_reaches_output`: the line between *turns unloaded here* and *not worked out* in every mode of
  RangeBox, E4 and TransferCase_Parallel, and whether any loaded branch can still read as unloaded.
- `_forces`' idler chain and the planetary member (sun or ring, `torques` or `held`), and the two-way flag for a gear on
  a held shaft (not two-way: the ring).
- The *Worst share* row never letting an unrated ring's lower bound stand unmarked.
- That nothing machined moves: F4-0's pins and the `STRENGTH_SAID` edit.

## What needs the other packages

Nothing to show B working: the warnings and the block are pinned on fixtures. Package C's WorkbookStrength board and
the Workbook boards B's warnings reach (F4-PACKAGE-C.md) wait for a run of `gen.py` now that B is committed.

## The coordinator's rulings on F4's review (`F4-REVIEW.md`, `be19cc5`; 2026-11-18, each the user's to overrule)

- **Every choice of packages B and C is accepted**, B's ten among them; no must-fix.
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
