# F4's interface, as F4-0 built it

PLAN-PRINTED §5.6 makes F4-0 one run with package A: the pins first, then A's maths written whole (not a stub, since it
is pure and small and both packages need it), the Box's Allowable stress, and this note, so that packages B (the
workbook) and C (what the user sees) can be written against it without colliding. This is that interface as it stands
at F4-0's interface commit on branch `f4` (cut from `printed` at `abdf450`). Every name here is importable from that
commit on. B's and C's own names are stubs that answer the neutral value, so the app reads exactly as before until each
package writes its part.

Where this note and the plan differ, the plan is the authority and the difference is in `docs/notes-printed/F4-0.md`
as a point for the coordinator. F4's review and its re-check (the last two sections of `docs/PLAN-PRINTED-REVIEW.md`)
are taken here, each said where it lands (§10).

## 1. What must not move, and the pins that hold it

- **Machined gears and gearboxes are told exactly what they were** (§5.5). F4's check runs only for a printed gearbox
  (F1's `checks._printed` for a pair; the Box's Process for the Results block), the form's row only for a printed
  derived gear. `gears.strength` is pure and is read by nothing machined.
- **F4-0's pins** (commit `2893224`, at `abdf450` before any F4 code), in `tests/test_printed_rule.py`,
  `test_a_machined_gearboxs_results_and_diagnostics_are_as_before_f4`: the Results sheet (rows and note) and every
  diagnostic (level, sentence, field, in order) of RangeBox, RangeBox_Fixed and planetary_4to1 as built in code
  (machined; 10, 10 and 2 N·m), and of the committed `excel-windows` Risky_Placements (5 N·m) and Reducer_12to1
  (10 N·m) read and marked machined, as `BEFORE_W8` reads them; by sha256, `results_sheet` called with
  `when=STAMP` (the review's S7). They hold at every later commit of F4.
- **W9's, F1's, F2's and F3's pins** are untouched: `BEFORE_W7`, `BEFORE_W8`, the W8 and W9 fixtures' counts and
  fingerprints, RangeBox's warnings, every pin of `test_printed_rule.py` but line 535 (§9), `test_span.py`, the
  findings and `PRINT_SETTINGS`, every bore pin and `test_ui_text.py:4513-4528`.
- **No schema number moves.** Link stays 12 and sidecar 4: F4 writes nothing into a link record or a `.gear.json`.
  The allowable lives in the workbook's Box only; `GearSpec` gains nothing. An F3-era app reading a workbook with the
  row skips it (`model._read_box` skips a label it does not know).
- **The stub run** (§5.5's last line), on a scratch copy of the interface's code (since deleted) with the Box as built
  and three stubs: a warning at every Meshes row of a printed gearbox whose input has a torque (more than B will say),
  a printed Results block, and C's row in `gui._rows_with_span` for every printed gear that rates. It gave 5386 passed,
  1 skipped and 6 failed: the known Tk font test, `test_workbook_model.py:27-29`, `test_printed_rule.py:535` and
  the three cases of `test_printed_workbook.py:296-311`. **No other pinned line moves**; §5.5's table holds, its fourth
  line (`test_ui_text.py:4520`) unmoved because the row is in `gui.py`. F4-0's own Results pins held in that run.

## 2. `gears/strength.py`, whole (F4-0's, package A's maths; nobody else edits it)

Constants: `ALLOWABLE_DEFAULT = 17.0` (MPa), `TWO_WAY = 0.7`, `PLANET_SHARE = 1.25`, `TANGENT_OUTSIDE = 30.0`,
`TANGENT_RING = 60.0` (degrees), `QS_RANGE = (1.0, 8.0)`.

`ToothRating`, frozen: `rated`, `why`, `y_f`, `y_s`, `s_fn`, `h_f`, `alpha_f_deg`, `rho_f`, `q_s`,
`past_range`, `module` (normal), `width` (toothed, mm), `d` (pitch, mm, transverse), `teeth` (z, or zn), and past
the plan's list `short` (the reason in a few words) and `ring` (F4-0's decision 2). A gear not rated still carries
`module`, `width`, `d`, `teeth` and `ring` where it has them.

- `rate(derived, recipe="A") -> ToothRating`: never raises. `derived` is a kind's `derive` result; `recipe` `"A"`
  or `"B"` (the kind's `recipe_for(spec)`). §5.1 exactly: the critical section at the 30° tangent (60° on a ring) on
  the drawn fillet, the whole load at one tooth's tip along the drawn flank's normal, ρF the drawn fillet, YS carried
  past qs 8 with `past_range` set, a qs under 1 taken at 1; a helical or herringbone gear (or ring) on ISO's virtual
  spur gear with `d` the drawn section's (a helical ring's at z mn / cos β, never z mn).
- `holds(rating, allowable=ALLOWABLE_DEFAULT, width=None, two_way=False) -> float`, N at the pitch circle:
  `σFP · b · mn / (YF · YS)`, `width` None the gear's own toothed width, × 0.7 with `two_way`. **Raises
  `ValueError` on a rating not rated**: the caller shows *not rated* instead.
- `torque_held(rating, force) -> float`, N·m: `force · d / 2000`.
- `allowable_mpa(text) -> float`: the figure when it reads as a number above zero, else 17 (a blank, and a figure
  that does not read, which `_read_box` says at its cell). Feed it `model.checked_allowable(box)`.
- Also public: `stress_correction(s_fn, h_f, q_s)`, `virtual_teeth(z, β, αn)`, `virtual_section(helical_derived)`,
  `toothed_width(derived)` (the face, or a herringbone's 2 × `toothed_width`), and the rounding of §6.6:
  `newtons(F)`, `newton_metres(T)`, `times(x)`, `megapascals(σ)`, each without its unit.
- The reasons, as `why` (a clause naming no gear, lower case, no full stop: *"Ring is not rated: " + why*) and
  `short`:

  | Not rated | `short` | `why` |
  |---|---|---|
  | a bevel gear | *a bevel gear* | *a bevel gear's tooth tapers along its face, and rating it needs ISO 10300's virtual gear at the mean cone, which this check does not work out* |
  | a ring whose tips lie inside its base circle (M1) | *tips inside the base circle* | *its tips lie inside its base circle (31.000 mm against 31.010), so the last of each tooth is a straight radial line and its tip load has no involute to act along* |
  | a pointed tooth (S6; never built) | *pointed teeth* | *its teeth come to a point below the outer diameter, so there is no tip corner to load (a pointed tooth is never built)* |
  | the 30° or 60° point off the drawn fillet (never met) | *section off the fillet* | *the point where its root fillet's tangent makes 30° with the tooth's centreline is not on the fillet as drawn, so its critical section is not defined* |
  | a tooth that does not draw, an unknown recipe, an involute starting outside the tip | *tooth not drawn* | *its tooth could not be drawn (…)* |
  | anything else | *not a gear rated here* | *only spur, helical and herringbone gears, outside and ring, are rated* |

- **Not `rate`'s to know, the callers' to leave out:** a dog or a hub derives a `SpurDerived` and would read as a spur
  gear (their couplings are splines, not on Meshes); a crossed pair's gears are helical gears and rate as such, but
  their mesh is not rated (§5.1). B leaves both out of the Meshes figures and says *not rated: a crossed pair*; C shows
  no row for either gear of a crossed pair in pair mode.

## 3. The Box (`workbook/schema.py`, `workbook/model.py`; F4-0's, whole)

- `schema.BOX_SETTINGS` gains, after Nozzle and before Units,
  `Setting("allowable", "Allowable stress", unit="MPa", default="17", numeric=True, note=…)`, its default and note
  written from `strength.ALLOWABLE_DEFAULT` (§6.5).
- `model.Box.allowable = ""` (the text as typed), `model.checked_allowable(box) -> str` (the text when it reads as a
  number above zero, else `""`, as `checked_nozzle`); `_read_box` reads it like Nozzle, with its errors at its cell;
  `to_sheets` writes it as held (blank for a gearbox built in code); `template` (*New workbook…*) writes 17. In a
  workbook written by `to_sheets` the row is `Box!B11` (Process stays `B9`, Nozzle `B10`, Units moves to `B12`).
- It is not a gear's field: `Gear.gear_spec(box)` is the same with any allowable typed. **B's test owed:** typing it on
  a built printed gearbox changes no part in `update.classify` (`link.describe_changes` listing the cell is right).

## 4. Package B: the workbook

**Files:** `workbook/strength.py` (F4-0's stub, B's from now), `workbook/checks.py` (one call at the end of `check`,
before `report.worked_out_as`, and a new field `Report.strength: Tuple[MeshStrength, ...] = ()`, additive),
`workbook/export.py` (the Results block, printed only); tests `tests/test_strength_workbook.py` (new) and B's one edit
in `tests/test_printed_workbook.py:296-311` (§9).

**The stub's names** (B may add fields after these; it does not rename or reorder them, since C's board and the words
read them):

- states `RATED`, `UNLOADED`, `NOT_SHARED`, `NOT_RATED`, `BEVEL`, `CROSSED`; the Results' wordings
  `TURNS_UNLOADED = "turns unloaded here"` and
  `NOT_SHARED_OUT = "the torque past a shared output is not shared out (not worked out)"`;
- `GearSide(gear, rating, held=None, two_way=False)`: one gear's side of a mesh in one mode, `held` in N at the
  mesh's width (× 0.7 when `two_way`), None when not rated;
- `MeshStrength(a, b, row, mode="", state=RATED, force=None, width=0.0, sides=(), weaker="", share=None, planets=0,
  unrated=())`: one Meshes row in one mode; `share` a fraction (1.0 is 100 %), `unrated` the ids not rated;
- `mesh_strengths(spec, report) -> Tuple[MeshStrength, ...]`: every Meshes row in every mode, Meshes order then each
  mode's; `()` for a machined gearbox or one whose first input has no torque (stub: `()`);
- `warning_sentence(rows, allowable, typed) -> str`: the one warning of one Meshes row, `""` when it says nothing
  (stub: `""`). B puts it at the row's cell with the house's `_warning`, the pair first as F1's clearance warning is
  said (`checks.py:514`).

**The rules** are §5.2 and §5.4 as written; B reads them there. In short: the torques are `report.motion` (no modes)
or each `ModeReport.motion`, with `kinematics.py` unchanged; a mesh is loaded only when both shafts carry a torque in
this mode (in `torques`, 0 counting, or in `held`); a planetary mesh takes the member's torque over `d · N` ×
`PLANET_SHARE` (N ≥ 2); any other the larger of 2000 T / d over its two gears, a shaft driving two meshes giving each
its whole torque; an idler (shaft torque exactly 0) passes on the largest force its non-idler mates give it; b is
`geometry.faces_overlap`, no more than either toothed width; each gear's figure is `holds(rating, allowable, width=b,
two_way=…)`, two-way for a shaft torque of exactly 0 in this mode; the share is Ft over the smaller figure, that gear
the weaker.

**Plus, from the re-check of F4's review (the two should-fixes it leaves for B):**

1. **The Results' *Worst share* row also names every loaded mesh not worked out**, after the list of meshes and gears
   not rated, with its modes: in TransferCase_Parallel and E4 the front branch FDrive–FIdler–FOut carries torque past a
   shared output in 4H and 4L, and FIdler, a gear whose teeth are loaded both ways, is never rated; the row must not
   read the low range's figure as the gearbox's worst and stay silent about it. Words in §6.3.
2. **§5.2's opening covers a mesh where one gear rates and the other is a ring that is not rated**: such a mesh is
   worked out (state `RATED`), its share over the gear that rates alone, a true lower bound, said as such, and the ring
   in `unrated`. *Each Meshes row whose two gears are rated* in §5.2's first line is to be read that way; the
   coordinator may want the plan's sentence changed in the plan's record.

**The rules the review asked stated here (§5.6 item 4):**

- **M1** (the coordinator's ruling, 2026-11-18, the user's to overrule): a ring whose tips lie inside its base circle is
  not rated (`rate` says so, §2). It is named with its reason at its Meshes row whenever the mesh is loaded in some
  mode, whether or not the other gear's share passes 100 %; the share counts the gear that rates alone; on Results its
  row says so and the *Worst share* row never lets it stand on its own figure (§6.3). With nothing rated in a loaded
  mesh, the state is `NOT_RATED`.
- **A pointed tooth** is not rated (never built, but `rate` says so).
- **The two *not worked out* wordings**, told apart by `Motion.shared` and `past_split`: *turns unloaded here*
  (RangeBox's stage in H and N, a branch reaching no output, the transfer cases' front branch in 2H) and *the torque
  past a shared output is not shared out (not worked out)* (the transfer cases' front branch in 4H and 4L). *No torque
  here* is never said.
- **R1** (the coordinator's ruling, the user's to overrule): the 0.7 stays, as an allowance for a tooth loaded in both
  directions as the gearbox runs (an idler, a planet), never part of a figure called *once*: the warning gives the
  gear's figure once and the allowance beside it; Results mark it *(0.7)*.

**B's tests owed** (§5.6): B1 to B8 with Idler_Train (B8's three Risky_Placements meshes, so a force taken at a
helical ring's z · mn fails); a planetary or ring pair with a ring of 33 teeth (the ring named at its Meshes row with
its reason, the share over the pinion alone, the *Worst share* row listing it); the two wordings; RangeBox not worked
out in H and N; a machined gearbox told nothing and its Results unchanged (F4-0's pins hold it too); a typed 34
halving the shares (B3 115.0 %) and a bad one leaving 17; a shared output and a shaft past a split not worked out; a
bevel and a crossed mesh *not rated* on Results; nothing for a sleeve's couplings; the allowable typed on a built
printed gearbox changing no part in `update.classify`; the re-check's two points above.

## 5. Package C: what the user sees

**Files:** `gui.py` (the row in `_rows_with_span`, through `strength.rate` and `ui_text.holds_row`), `ui_text.py`
(`HOLDS_LABEL` and `holds_row`, F4-0's stub at the file's end, C's from now, and the line under the rows),
`README.md`, `design/UI-DESIGN.md`, `design/canvas/gen.py` and the boards it writes; tests
`tests/test_strength_form.py` (new).

- `ui_text.HOLDS_LABEL = "Holds once"`; `ui_text.holds_row(rating, allowable=17.0) -> Optional[Tuple[str, str]]`
  (stub: None). C may change its signature (it is C's alone) but keeps the label.
- **Which gears show the row:** a printed spur, helical, herringbone or ring gear that rates, and a ring not rated by
  M1 (*not rated: tips inside the base circle*). No row: a machined gear, a bevel gear, either gear of a crossed pair in
  pair mode, a dog, a hub, a sleeve, and a gear not rated for another reason (it does not validate and is never built).
  In pair mode each gear's column has its own. The figure is at 17 MPa (`strength.ALLOWABLE_DEFAULT`), at the gear's
  own toothed width (`rating.width`), for a single load.
- The row goes in `gui._rows_with_span` after the rows `ui_text.derived_rows` gives, **not in `derived_rows`**,
  whose last rows are pinned (`test_ui_text.py:4520`). The stub run put it last, after F2's span row, and nothing moved.
- The full sentence of a ring past YS's range, or of a ring not rated, goes on one line under the rows after any line
  F2 puts there; if C's suite run finds that moves a pin of `_measured_lines`, the sentence goes in the row's value
  instead (§5.4).
- **C's tests owed** (§5.6): the row on a printed spur, helical, herringbone and ring with A1, A4, A5 and A6's
  figures; none on a machined gear, a bevel gear or a crossed pair's gears; each column of a pair its own; the
  README's section read from the file. Also: the A10 ring's *not rated* row.

## 6. The words (drafted here; each package writes its own and may reword, saying so in its note)

### 6.1 The warning at a Meshes row (B's)

The pair first, in the house's form; one warning per row, naming the mode with the largest share (H8). In full (a
planet, a blank allowable, modes), B6's figures:

> Meshes row 2: Sun and Planet: Printed, these teeth take about 230 N at the pitch circle in L, 13.6 times the 17 N
> Planet's teeth are rated to take at 17 MPa (provisional: type your own in the Box's Allowable stress): 24 N once,
> with an allowance of 0.7 because a planet's teeth are loaded in both directions as the gearbox runs; the load is
> shared by 3 planets, one taking 1.25 of an even share. Use a larger module, a wider face, less torque, or your own
> tested allowable. An estimate for teeth printed flat, with the whole load on one tooth's tip: not a running rating;
> heat, wear and creep are not worked out.

The variants:

- **no modes:** no *in L*;
- **the weaker gear not two-way** (B8's G1–G2): *…, 6.6 times the 51 N G1's teeth are rated to take once at 17 MPa
  (provisional: type your own in the Box's Allowable stress). Use …*: *once* moves before *at*, and the allowance
  clause goes;
- **an idler the weaker** (B3): *…: 41 N once, with an allowance of 0.7 because an idler's teeth are loaded in both
  directions as the gearbox runs. Use …*;
- **no planets:** no sharing clause; **one planet:** no sharing clause (K_γ 1);
- **an allowable typed on the Box:** no *(provisional: …)* bracket, and the figure the Box's: *… at 34 MPa*;
- **the weaker gear a ring past YS's range:** after its name, *Ring's teeth (its 0.15 mm fillet is sharper than the
  stress factor's range, which is carried past it) are rated to take once at 17 MPa …*, the fillet its `rho_f` in mm;
- **a ring not rated (M1), the mesh loaded in some mode and the other gear's share at or under 100 %:**

  > Meshes row 3: Sun and Ring: Printed, Ring is not rated: its tips lie inside its base circle (31.000 mm against
  > 31.010), so the last of each tooth is a straight radial line and its tip load has no involute to act along; the
  > share counts Sun alone.

- **a ring not rated and the other gear's share past 100 %:** one warning, the full sentence for the gear that rates,
  then *Ring is not rated: …; the share counts Sun alone.* before *Use a larger module, …*;
- forces with `strength.newtons` (whole from 10 N, to 0.1 N under), the times with `strength.times` (to 0.1), the
  allowable with `strength.megapascals`. Nothing is said at a row whose shares are all at or under 100 % and that has
  no ring not rated in a loaded mode (B5: no warning).

### 6.2 The form's row (C's)

- Label *Holds once*; value *about 0.58 N·m · 39 N at 17 MPa* (A1): the torque about the gear's own axis with
  `strength.newton_metres`, then the force at its pitch circle with `strength.newtons`.
- A ring past YS's range: *about 0.80 N·m · 29 N at 17 MPa · stress factor past its range* (A6), and under the rows:
  *Holds once: the ring's 0.15 mm fillet is sharper than the stress factor's range, which is carried past it.*
- A ring not rated (M1): *not rated: tips inside the base circle* (A10), and under the rows: *Holds once: not rated:
  its tips lie inside its base circle (31.000 mm against 31.010), so the last of each tooth is a straight radial line and
  its tip load has no involute to act along.*
- In pair mode the line under the rows is prefixed *A:* or *B:*, as F2's are.

### 6.3 The Results block (B's)

For a printed gearbox whose first input has a torque, after the box size (and its *Not in the box size* row), a blank
row, then:

    Tooth strength (printed) | Mode | Force (N) | Weaker gear          | Rated to take (N) | Share used (%)
    Sun–Planet               | H    | —         |                      |                   | turns unloaded here
    Sun–Planet               | L    | 229.885   | Planet               | 16.851 (0.7)      | 1364.3
    Sun–Ring                 | L    | 120.000   | Sun (Ring not rated) | 40.000            | 300.0
    FDrive–FIdler            | 4H   | —         |                      |                   | the torque past a shared output is not shared out (not worked out)
    G1–G2                    |      | not rated: a bevel pair

- (the Sun–Ring and FDrive–FIdler rows show the forms only, their figures made up; the rest are B6 and B7's);
- the Meshes sheet's order and each mode's; with no modes, the Mode cell is blank;
- the force to 0.001 N and the share to 0.1 % as numbers; a figure with the 0.7 marked *(0.7)*, a ring past YS's range
  *(stress factor past its range)*; a mesh with a ring not rated names the gear that rates as the weaker with *(Ring
  not rated)*;
- a bevel or crossed mesh, one row each: *not rated: a bevel pair* (or *a crossed pair*) in the second cell; nothing
  for a sleeve's couplings;
- then **Worst share**: *Sun–Planet in L, 1364.3 %* in its second cell (*(Ring not rated)* after the figure when the
  worst is such a mesh's lower bound), and in a third cell, joined by *; *, every mesh or gear not rated, by name with
  its reason, *not rated: Ring (tips inside its base circle)*, then every loaded mesh not worked out with its modes,
  *not worked out: FDrive–FIdler, FIdler–FOut in 4H and 4L (past a shared output)* (the re-check's should-fix). With
  nothing rated the second cell is *—*;
- then **Allowable stress (MPa)** | 17 | *blank: provisional, type your own in the Box's Allowable stress* (or the
  Box's figure and *the Box's*);
- then a note row: *An estimate for teeth printed flat, the whole load on one tooth's tip: rated to take once, not a
  running rating. Heat, wear, creep and load across layers are not worked out.*
- A machined gearbox's Results are what they are today (F4-0's pins).

### 6.4 The Box's error (F4-0's, built)

*Box!B11: Allowable stress must be a number (got 'x').* and *Box!B11: Allowable stress must be more than zero (got
'0').*, as Nozzle's are; the checks then use 17.

### 6.5 The Box's note (F4-0's, built)

*printed teeth only: the root stress a tooth is rated to take once; blank: 17, provisional (about half a printed PLA
data sheet's 35 MPa within the layers) until you type your own figure here*

### 6.6 The rounding (F4-0's to fix, §5.4)

Forces whole from 10 N, to 0.1 N under that; torques to 0.01 N·m under 10, to 0.1 under 100, whole from 100; times
to 0.1; the allowable as few figures as it needs (*17*, *12.5*). On Results, figures as numbers: forces to 0.001 N,
shares to 0.1 %. One home: `strength.newtons`, `newton_metres`, `times`, `megapascals`.

### 6.7 The README's paragraph (C's)

Under *Printed gears*, *What a tooth holds* (C may align the title with *rated to take*, as the re-check notes):

> A printed spur, helical, herringbone or ring gear's Derived panel shows what one tooth is rated to take once: about
> so many N·m about the gear's own axis, and N at its pitch circle, at 17 MPa. It is ISO 6336-3's tooth-root stress
> (Method B's form and stress-correction factors) worked out on the tooth as the app draws it, backlash and shift
> included, with the whole load on one tooth's tip: an estimate for one load on teeth printed flat, not a running
> rating. 17 MPa is provisional, about half the 35 MPa a printed PLA data sheet gives within the layers; in a workbook,
> type your own in the Box's Allowable stress, best one from a printed tooth broken in a jig. The workbook works out
> each mesh's force from the Shafts sheet's torque, mode by mode, warns at a Meshes row whose teeth take more than they
> are rated to, and lists every share on the Results sheet. A planetary stage's load is shared among its planets with
> one taking 1.25 of an even share, and a planet's or an idler's teeth, loaded in both directions as the gearbox runs,
> are rated at 0.7 of their figure. A ring's 0.15 × module fillet is sharper than the stress-correction factor's range,
> which is carried past it, and said; a ring whose tips lie inside its base circle (33 teeth or fewer at 20°) is not
> rated, and said. Not covered: heat (PLA softens near 55 to 60 °C), wear, creep at the bore or under a steady load,
> fatigue, load across the layers, the seam behind the walls of a root wider than five walls (above about module 2),
> bevel and crossed pairs, and a sleeve's couplings.

## 7. What the sources are, and what is not verified

The formulas are as `gears/strength.py`'s docstring and §5.1 state them. Their sources are secondary (MITcalc's ISO
6336 notes, re-read for F4-0 on 2026-11-19; excerpts of the 2006 text in search results); the standard was not read.
F4-0's note says what each figure rests on.

## 8. Who owns which file

| File | Owner from F4-0's interface commit |
|---|---|
| `src/gear_generator/gears/strength.py` | F4-0 (package A's maths, whole); a fix goes through the coordinator |
| `src/gear_generator/workbook/schema.py`, `workbook/model.py` (the Box) | F4-0 |
| `tests/test_strength.py`, `tests/test_printed_rule.py`, `tests/test_workbook_model.py` | F4-0 |
| `src/gear_generator/workbook/strength.py` (stub), `workbook/checks.py`, `workbook/export.py` | B |
| `tests/test_strength_workbook.py` (new), `tests/test_printed_workbook.py` (lines 296-311 only) | B |
| `src/gear_generator/gui.py`, `src/gear_generator/ui_text.py` (`HOLDS_LABEL`, `holds_row` stub) | C |
| `README.md`, `design/UI-DESIGN.md`, `design/canvas/gen.py` and its boards, `tests/test_strength_form.py` (new) | C |

B and C meet only through §2's names and §6's words; their files are disjoint.

## 9. The pinned lines F4-0 moved, and the one B moves

| File and line | Was | Is | Why it is not a loosening |
|---|---|---|---|
| `tests/test_workbook_model.py:27-29` | the Box's ten titles, *Nozzle (mm)* then *Units* | eleven, *Allowable stress (MPa)* between them | it pins the Box's settings and their order, and gains the one F4 adds; every other title and its place is asserted as before |
| `tests/test_printed_rule.py:535` | Process after Efficiency, Units after Nozzle | Process after Efficiency, Allowable after Nozzle, Units after Allowable | the same order pinned, with the setting between; the next lines (Process's words and note, Nozzle's title, numeric and default, the machined Box written) are unchanged |
| `tests/test_printed_workbook.py:296-311` (B's, three cases) | a printed gearbox's diagnostics equal its machined twin's | machined's plus exactly B's strength sentences for that gearbox, in order, each with its figures | stricter (the review's S7): it still pins §2.3's ruling (no pair interference warning, W7's sentence), and pins B's sentences word for word instead of allowing nothing new |

No schema number moved; the stub run found no other line (§1).

## 10. The review's and the re-check's points, where each landed

- M1 and M2: in §5's revision; A10 and A9 pinned in `test_strength.py` (A9's force and torque at d 76.6208, a test
  failing at z mn); B8 is B's.
- S1 (17 MPa's basis): the Box's note (§6.5) and the README's paragraph (§6.7).
- S2 (*about* and the allowable on the form; *rated to take once* and *provisional*): §6.1, §6.2.
- S3 (two wordings): §4, §6.3, and the stub's two constants.
- S4 (A's note's comparisons): `F4-0.md`, with three of them pinned (the module-2 and module-1 YF, and the 30°
  section against the beam's worst on A1, A2, A8 and m 2 z 100).
- S5 (0.17 σF between layers): the module's docstring and `F4-0.md` say no derating, with the figure.
- S6 (a pointed tooth): `rate`, pinned.
- S7 (a fixed `when`; B's exact sentences): F4-0's pins; §9's third line.
- The re-check's two should-fixes for B: §4, items 1 and 2, and §6.3's *Worst share* row.
