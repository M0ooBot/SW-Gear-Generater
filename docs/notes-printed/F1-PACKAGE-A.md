# F1, package A, handed back

The gear maths of PLAN-PRINTED §2.2, §2.3 and §2.5, on branch `printed`, against F1-0's interface
(`F1-INTERFACES.md`). Pure code; no SolidWorks call is added or changed.

## Commits

1. `c2b9496`: the printed checks, the pair stubs filled, Solve, the shift for a centre distance, the workbook's
   shift fix, the command line, and `tests/test_printed_gears.py` (61 tests).
2. This note.
3. `tests/test_printed_rule.py::test_the_pair_stubs_answer_as_the_machined_maths_until_package_a_fills_them` deleted,
   that one test and nothing else in the file, as the coordinator ruled; made last, after F1-0's follow-up
   (`707369a`, `792d026`) had landed and the file was clean. Its four stubs are now tested for what they do in
   `test_printed_gears.py`.

No other test was changed. `test_printed_rule.py`'s pins pass at every commit above.

## What was built

All of it is said for a printed gear only (`g.printed`, the nozzle on the derived section). A machined gear goes
down the same lines as before; the only refactor on a machined path is the rim test in `spur.section_diagnostics`,
which keeps its condition and sentence.

**Per gear** (`spur.section_diagnostics`, `internal.section_diagnostics`, `helical.HelicalGear.validate`,
`bevel.validate`; signatures unchanged):

- *Tip* under one nozzle line, after backlash. Spur and helical: the section's `tip_thickness`, which already has the
  backlash in its space; helical is the transverse section, the one a layer is sliced through. Ring: the ring's
  `tip_thickness`. Bevel: at the toe, `bevel.toe_tip_thickness(g)` = heel section's tip × `toe_scale`
  (`(R − b) / R`, since the build scales the whole heel section toward the apex); the heel's own tip sentence is set
  aside (`d != heel_tip`). A crown gear's rack is judged at its toe too.
- *Module* under 2.5 × nozzle (`spur.PRINTED_MODULE_NOZZLES`), on the typed module (a bevel gear's heel module).
- *Rim* between bore and root under 3 × nozzle (`spur.PRINTED_RIM_NOZZLES`). Where 3 × nozzle is more than the module,
  the printed floor is said in place of today's one-module warning; above that, today's warning is said as it is.
  A bevel gear's rim is from its bore to its root at the toe.
- *Helix* over 45° (`helical.PRINTED_HELIX_MAX`), helical and herringbone gears and rings.
- *Ring fillet*: a printed ring's default 0.15 × module fillet, said with why it is small
  (`internal.PRINTED_FILLET_FACTOR = 0.3`). Not said for a typed fillet.
- *Undercut* (§2.3): the generated-gear lead-in is replaced by *Printed, the gear is made as drawn, with no undercut;
  … turn the pair in SolidWorks.*, the named shift kept.

**Per pair** (`pair.mesh_warnings(g1, g2)`; when either gear is printed): the tip clearance under 0.3 mm
(`pair.PRINTED_CLEARANCE`, less 1e-9) through `pair.printed_clearance_sentence`:

- outside pairs: `tip_clearance` as today; the machined *cannot be built* sentence is kept at ≤ 0, and the machined
  tenth-of-a-module sentence between 0.3 mm and 0.1 m (module over 3);
- a pinion in a ring, in either order: `ring_tip_clearance`;
- bevel pairs: `min(dedendum₁ − addendum₂, dedendum₂ − addendum₁)`, 0.188 × module, at the heel;
- crossed pairs: nothing (recognised by a different helix angle or the wrong hand for parallel shafts).

No pair interference check (§2.3, by ruling).

**`pair.py`'s names**

- `ring_tip_clearance`: the ring's tip circle `r2 − m`, root `r2 − m + h`, the pinion's tip `r1 + m (1 + x1)`, root
  that less `h` (`internal.section`, `spur.profile`), pitch radii in the transverse module, `h` the user's depth
  IIF. On the line of centres the two gaps are `rf2 − (a + ra1)` and `ra2 − (a + rf1)`. A shifted pinion is at its
  working centre, `inv αw = inv αt + 2 tan αn (x2 − x1) / (z2 − z1)`, `a = mt (z2 − z1) cos αt / (2 cos αw)` (the
  formula `workbook.checks.internal_working_centre` already uses). `shift_2` other than 0 raises ValueError (rings
  are cut unshifted), as does a pinion shift no working angle answers.
- `printed_tip_thickness` = `tip_thickness` − `(d_a / d) · j / cos β`, `j = spur.printed_backlash(module)`: the
  backlash widens the space by `j_t` at the pitch circle, and `s_a = d_a (s / d + inv αt − inv αa)` carries it to the
  tip scaled by `d_a / d`. Tested equal to `spur.profile`'s `tip_thickness` for the printed gear, spur and helical.
  Its `nozzle` argument changes no figure (see point 6 below).
- New beside them: `printed_ring_tip_thickness` (through `internal.section`), `printed_mark`,
  `printed_clearance_sentence`, `_shift_refusal`, `_finish`, `_printed_row`, `_bevel_toe_tips`.
- `solve(process=, nozzle=)`: `process` printed in any case. Each row is marked `thin for a 0.4 nozzle` (the
  nozzle's figure) when its module is under 2.5 nozzle widths or a tip after the printed backlash is under one line;
  a row with a tip at or below 0 is not offered. Tips: outside rows both gears with their shifts; ring rows the pinion
  and the ring; crossed rows each gear at its own helix; bevel rows at the toe of each gear, with `face_width`.
  Shifted rows (`_shifted`) are tested as `shift_for_centre(printed=True)` is.
- `Candidate.mark: str = field(default="", repr=False)`, and `bool(mark)` in `rank()` after `not standard` and
  before `undercut`. `repr=False` keeps a machined row's `repr`, which the pins hash, as it was.
- `solve_spec` passes gear A's process and, when printed, its `nozzle_mm()` (a bad nozzle is an InputError), and a
  bevel pair's face width.
- `shift_for_centre(printed=False, nozzle=0.4)`: printed, the tip after the printed backlash against one nozzle line,
  and the clearance against `max(0.1 m, 0.3 mm)`, with its own two sentences; machined, the same tests and
  sentences as before.

**`workbook/fixes.py`**: `shift_fix` passes `printed=True` and the derived nozzle when either gear is printed.

**`gears/__main__.py`**: keys `process` and `nozzle`; left out, the gear is machined.

## The plan's figures, as the tests hold them

Module 1 at a 0.4 mm nozzle warns from 6 to 25 teeth and not from 26 (0.271 at 12, 0.365 at 20, 0.396 at 25, 0.401
at 26, 0.446 at 40). Module 1.25 passes from 11 (0.402; 0.375 at 10). Module 1.5 passes from 8 (0.437; 0.305 and
0.379 at 6 and 7; 0.581 at 12, 0.712 at 20). Unshifted outside pairs pass from module 0.75 (0.2999999999999998
within the tolerance). Bevel pairs warn at 1.5 (0.282 mm) and not at 1.6. The bevel toe of a 20 / 40 at module 1.5,
face 10 is at 0.702 of the heel (§2.1's 0.70).

**Where my code differs from a figure in the plan:** §2.2 says a ring pair's two gaps are "each 0.4 × module
unshifted". That is so only up to module 1.25; above it the depth IIF gives 0.25 × module, as for an outside pair
(0.375 mm at module 1.5). The code follows the drawn depth.

## Choices the plan left open, each the coordinator's to rule

1. A pair is judged printed when **either** gear is printed.
2. Solve ranks a marked row after `not standard` and before `undercut`: a row too thin to print is worse than an
   undercut one, which prints as drawn.
3. Solve uses the **printed default** backlash for its marks, not a typed one, as `printed_tip_thickness` does.
4. A bevel pair's clearance is Gleason's at the **heel** (the plan's module 1.6). At the toe it is that × the toe
   scale, smaller still; not said.
5. A bevel gear's module check is on its typed (heel) module, not the toe's.
6. `printed_tip_thickness`'s `nozzle` changes no figure (the default backlash does not depend on it); kept because
   the interface names it.
7. The rim: the printed floor replaces today's one-module sentence where 3 nozzle widths is more than the module,
   so one rim sentence is said, not two. A ring gets no nozzle rim check: its two-module warning is stricter from
   module 0.6, where the module check already warns below.
8. The tip sentence's advice. A **ring** is told only *use a larger module*: a ring's tip thins toward a rack's as
   its teeth grow (module 0.5: 0.438 mm at 20 teeth, 0.341 at 40), so *more teeth* would point the wrong way. A
   **bevel** gear is told *a larger module, more teeth or a narrower face*, since a narrower face brings the toe
   nearer the heel. The spur sentence is ruling 10's.
9. The clearance sentence says *or less profile shift* only when the pair has a shift.
10. The ring fillet sentence is also said for a printed sleeve (an internal spur) and an internal bevel gear, whose
    default fillets are the same 0.15 × module; for a sleeve "the pinion's tips" are the dog's.
11. A printed crossed pair gets no clearance sentence; its Solve rows are marked by each gear's tip.
12. `solve()` called with no face width judges a bevel row's toe at the form's default face (10 mm), at most a third
    of the cone distance.
13. A row whose tip comes to a point is dropped only when printed; a machined Solve is as pinned.

## What the interface did not say, for B and C

- **C:** Solve's mark is `Candidate.mark` (`""` or *thin for a 0.4 nozzle*). `ui_text.candidate_row` has to show it
  (C's file); nothing does yet.
- **C:** `gui.py:1300` calls `mesh_warnings` only for outside pairs on a centre distance (`not ui_text.is_ring(b)`,
  not crossed, symbol C). `mesh_warnings` now answers a printed ring pair and a printed bevel pair as well, but the
  form says them only if C widens that call. A machined ring or bevel pair would still be told nothing.
- **B:** `ring_tip_clearance` raises ValueError for a shifted ring and for a pinion shift no angle answers (B's
  `_check_mesh` already meets the second). `printed_clearance_sentence(clearance, shifted)` gives the sentence's
  words, for B to prefix at a Meshes row.
- `shift_for_centre` gained a `nozzle` keyword beside `printed` (additive; only `fixes.py` passes it).

## What the reviewer should look at hardest

- That every machined path is unchanged: `test_printed_rule.py` passes (plans, warnings, Solve rows, records), but
  read `spur.section_diagnostics`' rim branch and `Candidate.rank` by eye too.
- `mesh_warnings`' test for a crossed pair (a different helix angle, or a hand that does not fit parallel shafts
  with or without a ring). It decides only whether a printed pair is judged at all.
- `bevel.validate` sets aside the heel's tip sentence by equality with `spur.printed_tip_warning` of the same
  section. If either side's words drift apart the heel's sentence would come back beside the toe's.
- `ring_tip_clearance` with a shifted pinion: the formula and sign convention are the ones `checks` uses; I tested
  them against a hand computation, not against a drawn outline.
- The bevel Solve derives two gears per row; fine for its 120 rows, but it is the only Solve path that derives.
