# F4-0's review: the pins, package A's maths and the interface for B and C

**Read at `2835d09` on `f4`** (cut from `printed` at `abdf450`), reviewing commits `2893224`, `0496e85`, `6d81160` and
`2835d09` as code, before packages B and C start. Every python run used `PYTHONPATH=src`, and the import path was checked
to be this worktree's. Nothing was run on SolidWorks or Excel, and no code was changed. My figures come from scratch
scripts, since deleted, and from the code I wrote for the plan's review (docs/PLAN-PRINTED-REVIEW.md, the F4 sections).

**Suite at `2835d09`:** 5491 passed, 1 skipped, and the known Tk font test, which failed in a first run and was then
deselected.

## 1. The pins

- **Taken before any F4 code, and they pass there.** `git diff abdf450 2893224 -- src` is empty. I ran `2893224`'s
  `src` and `tests` from a scratch copy, and `test_a_machined_gearboxs_results_and_diagnostics_are_as_before_f4` passes
  there. It also passes at `2835d09`, inside the full suite.
- **What they prove.** Each pin hashes, for five machined gearboxes, every row and the note of the Results sheet (with a
  fixed `when`, the review's S7) and every diagnostic in order, by level, sentence and field:
  - RangeBox, RangeBox_Fixed and planetary_4to1, built in code at 10, 10 and 2 N·m;
  - Risky_Placements and Reducer_12to1, read from `excel-windows` and marked machined.

  Any strength warning, Results block or reworded sentence that reaches a machined gearbox breaks a hash. The
  `TURNED_GEAR_MATE_SENSE_READ_BACK` monkeypatch is the house's own (`test_printed_rule.py:249`, `:966`, and
  `test_workbook_planetary.py:400`).
- **W9's and F1 to F3's pins.** They are the existing tests, and every one passes at `2835d09`. `git diff abdf450 HEAD`
  touches only two lines of existing test files, the two below; everything else in `tests` is new (`test_strength.py`
  and the appended pin).
- **The two lines moved are not a loosening.**
  - `test_workbook_model.py:27-29` lists the Box's titles exactly, now eleven with *Allowable stress (MPa)* between
    *Nozzle (mm)* and *Units*.
  - `test_printed_rule.py:535` keeps Process after Efficiency and puts Allowable after Nozzle and Units after Allowable,
    as two asserts. The order is pinned as tightly as before.
  - These are the two lines §5.5 names. B's third (`test_printed_workbook.py:296-311`) is written in F4-INTERFACES §9
    in the stricter form the review asked for.

## 2. `gears/strength.py` against the plan and my own code

**Every expression is as §5.1 states it.**
- Q is `C + ρ(−sin τ, cos τ)` outside and `C + ρ(sin τ, cos τ)` on a ring, which are (cos(90° ± τ), sin(90° ± τ)). It
  is checked to lie on the drawn arc between the fillet's two ends.
- s_Fn = 2|v_Q|. h_F runs along the centreline to where the load's line crosses it.
- On recipe A the load's normal is (−sin u, cos u), and mirrored on a ring. That is the involute's normal: the tangent is
  r_b t (cos u, sin u), with u = t + φ. On recipe B it is the arc's radius.
- Y_F is 6(h_F/m)cos α_F / ((s_Fn/m)² cos α_n), with α_n the section's own α (the normal one on a virtual gear).
- Y_S is (1.2 + 0.13 L)·max(q_s, 1)^(1/(1.21 + 2.3/L)).
- The figure is σ·b·m/(Y_F·Y_S), and the torque is F·d/2000 with d transverse.
- The virtual gear is drawn with the normal module, normal α, normal backlash (`SpurDerived.backlash` holds the normal j;
  the section gets j/cos β separately), the shift and ρ.
- My own A1 to A9 figures (the plan review's script) agree with the module's to the last digit. So do three rings on
  recipe B, which no row pins: z 54 m 1, z 80 m 2, and a helical ring z 60 at 15°, against the test's own beam working.

**Rings not rated (M1).**
- *Spur ring:* `tip_below_base` is tested before anything else.
- *Helical ring:* not rated when its drawn section *or* its virtual ring has its tips inside the base circle. The
  sentence's figures are the drawn section's whenever that section is the one below.
- A10 and every ring of 20 to 33 teeth at 20° are not rated, and z 34 is rated (Y_F 2.1242, Y_S 2.6416, q_s 8.756,
  matching my re-check).

**Y_S past its range.** q_s ≥ 8 sets `past_range` and the formula is carried on. A q_s under 1 is taken at 1. That is
right, and pinned (A6, A9).

**The 0.7.**
- `holds(..., two_way=True)` multiplies by `TWO_WAY`, and the docstring words it as R1 rules: an allowance for running,
  never part of a figure called *once*.
- Deciding who is two-way is B's job (a shaft torque of exactly 0), and the interface says so.

**A gear it cannot rate.**
- `rate` never raises. Its own reasons (bevel, tips inside the base circle, pointed, off the fillet, not drawn, not a
  gear) each come with a clause and a short form. Any exception becomes *tooth not drawn* with the exception's text.
- `holds` raises `ValueError` on a rating that is not rated, so a not-rated gear can never be shown as a number.
- `allowable_mpa` gives 17 for blank, unreadable, zero, negative, inf and nan.
- All of this is sound, with one caution for the stage review: the catch-all in `rate` would also turn a programming
  slip into *not rated*. The rated sweep in `test_outside_gears_stay_in_the_stress_factors_range…` is what guards
  against that, and it asserts every validating outside gear rates.

**Mutations, run on a scratch copy.** Each one turns tests red:

| Mutation | Tests failing |
|---|---|
| tangent + 1° | 39 |
| z_n → z/cos³β_b | 11 |
| Y_S exponent's 2.3 → 2.2 | 17 |
| a spur ring's `tip_below_base` test removed | 15 |

## 3. The tests: is the beam working independent?

**In code, yes.**
- The test's `beam` and its helpers (`drawn_tooth`, `section_point`, `virtual_here`) import nothing from
  `gears.strength`.
- They find the 30° (60°) point by bisection along the drawn fillet, not by the module's closed form, and the tip by
  bisection along the drawn flank. The normal comes from differencing the flank, not from (−sin u, cos u).
- Y_F comes from the moment of a unit normal force about the section's middle, (p_u − q_u)n_v − p_v n_u, which is
  h_F cos α_F. That is beam statics, not the Y_F expression.
- Y_S is the source's expression written out again.

**What both share is the app's drawn geometry** (`spur.involute_flank`, `arc_flank` and the ring's), which is the point.
`test_the_form_factor_is_the_beams_on_the_drawn_outline` checks that the tip and the fillet's ends are vertices of
`kind.outline`.

**The figures are literals.** A1 to A9 are held to literal figures from §5.3 and the review (`ROWS`), and B1 to B8 to
literals from §5.3, never to the module's own output. The beam working is held to the same literals separately. The
`abs=5.5e-4` on the module 2, z 100 Y_F (2.54547 against §5.1's 2.546) is a double rounding in the plan, said in the test
and in F4-0.md, and is not a loosening.

## 4. z_n

There is no single exact virtual spur gear: a helical tooth's normal section is not an involute of any circle. Each
formula comes from a different way of matching one:

- **Matching the flank's curvature where the plane normal to the pitch helix cuts it at the pitch point.** I computed this
  numerically on the involute helicoid. It gives **z/cos³β** exactly: 24.103 for A4, 43.386 for A9, 16.872 for z 14
  (the test's own sweep is β 20° and 35°).
- **The base cylinder's ellipse in the plane normal to the base helix, with α_n.** This gives **z/cos³β_b**, MITcalc's
  (23.553 for A4). The identity cos α_t / (cos β cos α_n) = 1/cos β_b turns d_b/(cos²β_b m_n cos α_n) into z/cos³β_b.
- **ISO's own definition, z/(cos²β_b cos β).** This is d_n = d/cos²β_b with the normal module; as I recall it, DIN 3960,
  ISO 21771 and ISO 6336 all define it so. It gives 23.735 for A4, between the other two.

**Which is right:** for a rating by ISO 6336-3's Y_F and Y_S, ISO's own z_n is the one to use, since those factors were
calibrated with it. F4-0 uses it, and nothing should change.

**How much the choice moves the plan's rows**, at the figure one tooth is rated to take:

| Row | MITcalc's form | z/cos³β |
|---|---|---|
| A4 and A5 | −0.21 % | +0.40 % |
| A9 | +0.03 % | −0.06 % |
| B8's G1 and G5 (z 14, 20°) | −0.26 % | +0.51 % |
| B8's G3 (herringbone z 14 at 25°) | −0.42 % | +0.84 % |

All of these are far inside the method's other approximations.

**Wording:** F4-0.md's "not verified" should say this: the three forms differ by under 1 % on every pinned row, and ISO's
own is the calibrated one. The standard itself is still unread.

## 5. The interface for B and C

- **Precise enough to write against.**
  - §2 gives `rate`, `holds`, `torque_held`, `allowable_mpa`, the rounding helpers and every reason.
  - §4 gives B's stub names, which may gain fields but not be renamed or reordered, the rules (§5.2 in short) and the
    tests owed.
  - §5 gives C's `holds_row`, which gears show the row, and where it goes.
- **Files are disjoint (§8).** F4-0 keeps `gears/strength.py`, the Box and its three test files. B's files are
  `workbook/strength.py` (already stubbed), `checks.py`, `export.py`, `test_strength_workbook.py` and lines 296-311 of
  `test_printed_workbook.py`. C's files are `gui.py`, `ui_text.py`, the README, the design files and
  `test_strength_form.py`. The stubs in B's and C's files follow F3-0's precedent; each docstring says *F4-0's stub*
  and names its package, and a test holds them neutral.
- **My two should-fixes for B are written in**: §4 items 1 and 2, and §6.3's *Worst share* row, whose third cell names
  the loaded meshes not worked out with their modes.
- **The words (§6).** They read well and match §5.4.
  - The warning says *rated to take once* with *provisional* and where to type a figure, puts the 0.7 beside the figure
    for one load, and offers the user's own tested allowable as a remedy.
  - The variants are complete: no modes, not two-way, an idler, one or no planet, a typed allowable, a ring past the
    range, a ring not rated with the other gear at or under 100 %, and both at once.
  - The worked variant's figures check: B8's G1–G2 gives *6.6 times the 51 N*.

  Two small points for B and C to settle in their notes, neither blocking:
  - *the 17 N Planet's teeth are rated to take at 17 MPa … : 24 N once* puts the figure with the 0.7 first and the
    figure for one load after the colon. That is R1 as worded, but the sentence is long; B may reorder it, saying so.
  - The README title *What a tooth holds* should become *rated to take*, as §6.7 already allows.

## 6. The fourteen decisions

1. **Two notes.** Accept: the house pattern.
2. **`short` and `ring` on `ToothRating`.** Accept: both readers need them, and they are additive.
3. **A helical ring not rated if either its section or its virtual ring says so.** Accept: the two never disagree in
   either sweep, and the sentence then quotes the user's own diameters.
4. **`holds` raises on a gear not rated.** Accept: no not-rated gear can then reach a number; callers check `rated`
   (interface §2).
5. **`allowable_mpa` never raises, and gives 17.** Accept: the error is said once, at the cell.
6. **Three extra *not rated* reasons.** Accept: none is met in the app's gears, and each is said.
7. **The Box's note reads *rated to take once*.** Accept: §5.4's *rated to once* was a slip.
8. **The Box's errors are Nozzle's.** Accept: *must be a number (got 'x')* is the right sentence for text.
9. **`schema` imports `ALLOWABLE_DEFAULT`.** Accept: one home, and there is no import cycle (the suite is green).
10. **The rounding, in one home.** Accept.
11. **Stubs in B's and C's files.** Accept: F3-0's precedent, neutral and pinned as stubs.
12. **The words as settled.** Accept, with §5's two small points left to B and C.
13. **The B-row test in A's file.** Accept: it proves A's maths and the kinematics give every B figure now. B pins the
    same rows through its own module, and should not delete these.
14. **§5.2's opening read as covering a mesh with one ring not rated.** Accept. The coordinator should change the plan's
    sentence in the plan's record when B lands.

## 7. Must-fix and should-fix

**Must-fix:** none. B and C may start.

**Should-fix:** none of these blocks B or C.

- **S1. A ring on recipe B with its tips inside its base circle.**
  - M1's sentence (`strength.py`, `why_tips_inside_base`) says *the last of each tooth is a straight radial line and its
    tip load has no involute to act along*. On recipe B the ring's flank is an arc from the tip cap, with a defined
    normal: `internal.arc_flank` succeeds, for example m 1, z 30, B.
  - The app's own warning (`internal.py:571-575`) says the same for both recipes. That wording is older than F4 and is
    not F4's to change.
  - The ruling (not rated) stands, but the clause should say for B *its tips lie inside its base circle, where its teeth
    are not involute*, or the coordinator rules whether a recipe-B ring there may be rated.
  - This blocks nothing, and is F4-0's file through the coordinator.
- **S2. Ring recipe B is unpinned.** No pinned row covers a ring on recipe B or a helical ring through the beam working.
  Add the ring cases to `test_each_worked_row_by_beam_statics…` or to the αF/beam tests. My figures, as module equals beam:
  - z 54 m 1 printed B: Y_F 2.01028, Y_S 2.67363;
  - z 80 m 2 machined B: Y_F 2.26901, Y_S 2.55098.

  F4-0's test file; this blocks nothing.
- **S3. F4-0.md's z_n row should say what §4 here says**: ISO's form is the calibrated one, and the three forms differ by
  under 1 % on every pinned row. A note only.
- **S4. Wording in the warning and README, for B and C**, as in §5.
