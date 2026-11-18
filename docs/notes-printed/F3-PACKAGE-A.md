# F3, package A, handed back

The gear maths and the plans of the bore (PLAN-PRINTED §4.1, §4.2, §4.6 package A), on branch `printed` against F3-0's
interface (`F3-INTERFACES.md` §3, §9, §11, §13, §14) and the coordinator's rulings on F3-0. Pure code: no SolidWorks
call is added or changed (`CreateArc`, `CreateLine`, `SketchAddConstraints`, `AddDimension2`, `FeatureCut4` and `Add2`
as the app makes them), and no file but package A's is touched.

## Commits

1. `e855b36`: `gears/spur.py`, `helical.py`, `bevel.py`, `internal.py`, `clutch.py` and `tests/test_bore.py` (new). Its
   message says 145 tests; there are **139** (the message's count is wrong, the commit is not).
2. This note.

No existing test was changed; F3-0's printed-bevel fixture commit (`21cac8b`) was in the log before `e855b36`.

## The numbers

Packages B and C had uncommitted edits in the worktree throughout, so every run below is of a scratch copy (`git
archive 7c9b473` with package A's six files over it; deleted afterwards), `PYTHONPATH=src`, the import path checked.

- **Switch off** (as committed), the whole suite: **5328 passed, 1 skipped, 1 failed**, the known Tk font test
  (`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`). That is
  F3-0's 5189 with these 139.
- **Switch on** (`spur.PRINTED_DEFAULT_IN_PLANS = True` in the process), the whole suite: **8 failed, 5321 passed, 1
  skipped**:
  - the known Tk test;
  - **six of the ten guards** of F3-INTERFACES §13, each B's or C's threading: #1 and #2 (the reducer and RangeBox_Fixed
    printed), #3, #4, #5 (B's), and #10 (`test_an_old_records_form_changed_to_printed_is_one_global_for_update_values`,
    C's). Guards #6 to #9 (the strip pins `[spur]`, `[helical]`, `[herringbone]`, `[coupon]`) and the bevel and crown strip
    pins **pass** (see *The interface*, 2);
  - **one test outside the guards**: `tests/test_printed_gears.py::test_the_printed_rim_is_three_nozzle_widths_where_that_is_more_than_a_module`
    (see *The interface*, 3).
- **`tests/test_bore.py` shown failing** on six mutations of `spur.py` in the scratch copy: the arc's ends swapped (25
  failed), h reflected (61), the chord through `sqr` (2), the bore check not on the hole as cut (1), the switch ignored
  (8), the depth bound dropped (6).

## What was built

- **The switch** `spur.PRINTED_DEFAULT_IN_PLANS = False`, read at call time by **`spur.bore_allowance_of(spec)`**, the
  one helper every kind calls: 0 with no bore; else `spec.bore_allowance_mm()` (typed, else `built_allowance`, else the
  printed default, else 0), except that while the switch is off a blank on a gear not on record (`built_allowance` "")
  plans 0. `spec.py` is untouched. **`spur.bore_flat_of(spec)`**: the Flat with a bore, Drive flat and a Flat typed,
  else None (round).
- **The derived gears.** `spur.profile` takes `bore_allowance` and `bore_flat`; the spur's and the helical's derive pass
  them (a ring's not), the bevel's sets the allowance on its section (never a flat). `BevelDerived` gains the
  properties `bore_allowance`, `bore_flat` (None) and `bore_as_cut`; `InternalDerived` the class attributes 0.0, None,
  0.0 (not fields, so no record moves). `SpurDerived.values()` lists the bore's globals the part holds.
- **The globals** (`spur.bore_globals`): `"Bore Allowance"` only when the allowance is not 0, `"Bore Flat"` only with a
  D, both right after `"Bore Diameter"` in the spur's, the helical's and the bevel's lists (a dog's and a hub's through
  the spur's).
- **The round bore** (`spur._bore_ops`): the circle at the hole as cut, linked to `"Bore Diameter" + "Bore Allowance"`;
  with no allowance it is the ops it was, op for op (pinned in `test_bore.py` and by F3-0's machined pins).
- **The D** (`spur._d_bore_ops`, `spur.DFlat`, `spur.d_flat`), on the Front plane for every kind:
  `Arc("bore_arc", (0, 0), (h, +c/2), (h, −c/2), +1)`, `Line("bore_flat", (h, −c/2), (h, +c/2))`, coincident centre on
  the origin, the line's start on the arc's end and its end on the arc's start, `vertical` on the line; `Dimension("Bore",
  ("bore_arc",))` (a radius) linked to `( "Bore Diameter" + "Bore Allowance" ) / 2` and `Dimension("Flat",
  ("bore_flat",))` linked to `spur.chord_expression`, `2 * ( abs ( ( R ) * ( R ) - ( h ) * ( h ) ) ) ^ 0.5` with
  `R = ( "Bore Diameter" + "Bore Allowance" ) / 2` and `h = "Bore Flat" - "Bore Diameter" / 2 + "Bore Allowance" / 2`;
  with no allowance the same with the allowance's terms left out. The helical's and the herringbone's bore ops are the
  spur's (they call `spur._bore_ops`); the flat on +X faces the space centred there at their section plane, as
  F3-INTERFACES §3 says, with its unverified-mirror caveat.
- **The bevel gear**: the blank's points at the hole as cut and `"Bore Diameter" / 2` become `( "Bore Diameter" + "Bore
  Allowance" ) / 2` in the Back and Front links, both trig forms; the cone's and the crown's alike.
- **The checks** (`spur.bore_checks(spec, kind, cut)`, called by every kind's validate but the ring's;
  `spur.no_bore_errors(spec, what)` for rings in `field_errors` and for the sleeve in `clutch`). Each sentence is in
  `test_bore.py` word for word:
  - the bore against the root, the one-module rim, the printed rim, the herringbone's groove floor and the bevel's toe
    are measured on the hole as cut; each names the allowance only when there is one (`spur.bore_words`), so every
    sentence a gear said before F3 is the same;
  - at Flat: *The flat is {h} mm from the axis, under a quarter of the hole's radius ({0.25R} mm); type a Flat of at
    least {(5D − 3a)/8} mm, or use a round bore.* and F3-INTERFACES §9's depth sentence (*Your shaft's flat is {D − F}
    mm deep …*), as drafted;
  - *Drive flat needs a Bore …* (Drive), *Drive flat needs a Flat …* (Flat), the bevel's G5 sentence (Drive);
  - G9: *A ring has no bore to give an allowance or a flat.* at each typed field of a spur, helical or herringbone ring;
    *A sleeve has no bore …* at a sleeve's (the sleeve's `_as_spur` clears the three, so the ring it delegates to never
    sees them);
  - the parse errors of F3-0's `spec.py` at their cells (`field_errors`).

## The formulas and the bounds, with where each comes from

- R = (D + a) / 2, h = F − D/2 + a/2, so the hole is F + a across its flat (§4.2); c = 2 √(R² − h²); the arc's sweep
  360° − 2 acos(h / R), over 180° for every h above 0 (§4.2, the re-check's table of the four branches).
- R − h = D − F whatever the allowance (the re-check, §3), so the depth bound is on the shaft's own flat.
- h ≥ `FLAT_LEAST_H` · R (0.25, §4.2, G6) gives F ≥ D/2 − a/2 + 0.25 (D + a)/2 = (5D − 3a)/8: 4.925 for D 8, a 0.2, as
  the re-check found; D − F ≥ `FLAT_LEAST_DEPTH` (0.3 mm, §4.2, G6) gives F ≤ D − 0.3. Both with a 1e-9 tolerance so a
  Flat typed at the edge passes.
- The least chord at the depth bound, 2 √(0.6 R − 0.09), 3.08 mm at R 4.1 (§4.2), tested.
- The D's area, 49.1350 mm² against the circle's 52.8102 (§4.2, the review's), from the segment's formula and from a
  20000-point polygon of the arc as planned.
- §4.2's six-row table (h, R, chord, sweep) from the formulas alone, to its printed places, and from `DFlat` to 1e-12.

## Choices the plan left open, each the coordinator's to rule

1. **Where the globals sit**: right after `"Bore Diameter"` (the user's ten keep their relative order, which is what
   the helical and bevel tests pin). The plan names only the lists.
2. **An allowance typed with no Bore** (the ruling on decision 15) warns for any text typed, a typed "0" included.
3. **A Flat typed with Drive round** warns: *Flat is read only with Drive flat, so with a round bore it is not used.*
   (decision 7 left it to A; F3-0 keeps such a Flat in the record).
4. **An allowance that closes the hole** (D + a ≤ 0, a press fit taken too far) is an error at Bore allowance: *A Bore
   allowance of {a} mm closes the {D} mm bore ({D + a} mm as cut); it must leave a hole.* The plan allows a negative
   allowance and says nothing of this.
5. **An internal bevel gear** (a ring, its Bore not cut): an allowance warns, *An internal bevel gear is a ring and has
   no bore, so the Bore allowance is not used.*; Drive flat is the G5 error; its `bore_as_cut` is 0.
6. **A ring's Drive**: anything but blank or round (a bad word included) is the ring's error, not the parse error.
7. **The two bounds cannot both hold** below about D = 0.8 − a mm (the least Flat passes the most); both sentences are
   then said. Not worth a third sentence, in my judgement.
8. **Not done**: the allowance and the flat in the part's custom properties (`property_ops`' sizes). The plan is
   silent; the properties stay what they were.
9. **The chord's link relies on `^` binding tighter than `*` in SolidWorks**: `2 * ( abs ( … ) ) ^ 0.5` is the plan's text,
   and the app's evaluator reads it so, but the app has never written a product with a `^` in it, and P1 probed only
   unary minus against `^` (GOTCHAS: `-2 ^ 2` is −4). If `dshape`'s first build reads half a chord or its square, the
   fix is `2 * ( ( abs ( … ) ) ^ 0.5 )` in `spur.chord_expression` alone.

## The interface: what I found wrong or short

1. **`BevelDerived` had no `bore_as_cut`, and reading it through its section gives 0** for a cone, whose heel section
   is profiled with bore 0; and `InternalDerived` had none of the three names, so a ring's or an internal bevel's
   derived gear would raise on them. Both are A's files; I added them (above). B and C may read `bore_as_cut` and
   `bore_allowance` on every derived gear.
2. **The four strip guards (#6 to #9), and the bevel and crown strip pins, do not fail with the switch on before C's
   threading.** A's globals come from the derived gear (`kind.variables(spec, derived)`, as every global does), and the
   pins' stand-in (`_f2_strip_form`) derives through `as_built`, so `_update_target` counts 0 even as it is at
   `7c9b473`. F3-0's simulation put the global in from the spec, which is why they failed there. So those guards do not
   by themselves prove that C's `_update_target` applies `as_built`; F3-0-REVIEW's S4, C's real-path
   `tests/test_bore_form.py`, is what does, and #10 still guards the strip's count.
3. **One test outside the guards moves when the switch is turned on:**
   `tests/test_printed_gears.py::test_the_printed_rim_is_three_nozzle_widths_where_that_is_more_than_a_module` pins F1's
   printed rim sentences for gears built new with a blank allowance (lines 99, 104 and 106-107). With the default in,
   the rim is measured on the hole as cut (§4.1: F1's printed rim among the checks), so 0.88 becomes 0.78, 0.38 becomes
   0.28, and at module 2, Bore 33, the printed gear's rim (0.9 mm on 33.2) no longer equals the machined one's. F3-0's
   run missed it because its stand-in did not move the rim. It is in no package's file list; the switch's commit
   cannot be one line unless the coordinator rules who changes it and how (for instance a typed `bore_allowance="0"`
   in its printed specs, which keeps the test about F1's floor, or the figures moved). I have not touched it.

## What needs the other packages before it can be shown working

- Guards #1 to #5 (B) and #10 (C) green with the switch on; then the switch's commit with the whole suite, and item 3
  above settled first.
- The D on SolidWorks: the arc's branch on Update, the major arc's dimension read as a radius, and item 9's
  precedence, all of which `dshape` measures first (§4.6).

## What the reviewer should look at hardest

- `spur._d_bore_ops` against §4.2 line by line: the arc's start and direction, the line's two shared ends, the link
  texts, and the sweep test (`test_the_arc_as_planned_is_the_major_d_and_never_the_sliver_…`).
- `bore_allowance_of`'s blank test (`bore_allowance` and `built_allowance` both blank) against F3-INTERFACES §13: a part
  on record with no global reads `built_allowance` "0", which is not blank, so it plans 0 with the switch on or off.
- That every pre-F3 sentence and op is unchanged at a 0 allowance: `bore_words`, the bevel's `s_heel` and `s_toe` now
  taken from `back_bore` and `front_bore` (the same float when a is 0), and the herringbone's groove sentence.
- `SleeveKind._as_spur` clearing the three fields, so a sleeve plans and records as before.
