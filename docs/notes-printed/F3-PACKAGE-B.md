# F3, package B, handed back

Package B of PLAN-PRINTED's stage F3 (§4.1.1, §4.4, §4.6; `docs/notes-printed/F3-INTERFACES.md` §6, §7, §11, §13, §14):
the record's comparisons, the workbook, Update and Print files, reading a blank Bore allowance on record as built through
`spec.as_built` and nowhere else. On branch `printed`, written against F3-0's interface while packages A and C were
written beside it in the same worktree. No SolidWorks and no Excel: everything is shown against the fake.

## Commits

1. `0212eae`: the threading in `workbook/gearbox.py`, `workbook/update.py`, `swbuild.py`, `printout.py`, `workbook/assess.py`
   and `workbook/build.py`, and the new `tests/test_bore_workbook.py` (23 tests). It lands after package A's `e855b36`, as
   the landing order has it.
2. This note.

**Suite, switch off** (`spur.PRINTED_DEFAULT_IN_PLANS` False, as committed): at `0212eae`, run in a scratch copy holding exactly that commit's tree, so without C's
work in progress: **5351 passed, 1 skipped, 1 failed**. The failure is the known Tk font test
(`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`). In this
worktree, with C's work in progress beside it: 5379 passed, 1 skipped, with the font test deselected.

**The ten guard tests, switch on** (F3-INTERFACES §13, in their own process, `tests/test_printed_rule.py`,
`tests/test_printed_window.py` and `tests/test_swbuild_user_work.py` whole): **638 passed, 2 failed**, on the same tree.
- **B's four are green**: guards 1 and 2 (`test_a_gearbox_built_before_f3_reads_after_it_as_it_did[reducer_printed]`,
  `[rangebox_fixed_printed]`), 3 and 4 (`test_printed_window.py`'s two Update tests).
- In a scratch copy with B's six files put back to HEAD and A's code in, guards 1 to 5 and 10 fail. So it is this
  threading that turns 1 to 4 green.
- **Guard 5 fails, and cannot be turned green by B's threading** (below).
- **Guard 10 fails**: C's `_update_target`, C's guard.
- C's strip pins (6 to 9, `[bevel]`, `[bevel_crown]`) and every other pin of `test_printed_rule.py` pass.

Probe self-checks, each **0 failed**: `f1_demonstration`, `f2_demonstration`, `f2_probes`, `w9b_demonstration`,
`w9c_demonstration`, `w9d_demonstration`, `w9c_probes`, `w9d_probes`, `workbook_assembly_check`.

No existing test was changed. The pins and the guards are untouched. `tests/test_bore_workbook.py` is new.

## What was built: every reader of a blank allowance on record that is B's

| # | Where | What it does now |
|---|---|---|
| 1 | **Reuse**, `gearbox._match` (new) / `_matches` (kept, its signature too) / `_Parts.find` | Tried **per candidate entry**. Both sides are read as built from that entry's own `variables`: the recorded spec through `as_built`, and the job through `as_built_job`. The match returns the as-built job, which `_Found.job` carries into the `PartReuse`. So the live check holds the part to the globals it really holds. The same applies to entries on record, to `.gear.json`s found by name, and to journaled parts. |
| 1b | **The journal** (B1), `gearbox.journal` | Each new or journaled-reused part's `PartEntry` carries the job's globals, in degrees, and `trig` "degrees". The journaled match passes the entry's own `variables` and `trig`, where it passed `()` and "". So a part an interrupted build cut at 0.2 is never reused for a row asking 0. An older journal holds none and reads as built with no allowance. |
| 2 | **Update**, `update._part` and `_ignored_fields_as_built` | The job goes through `as_built_job(job, entry.variables)` and the built spec through `as_built(from_dict(entry.spec), entry.variables)`. The `PartUpdate` holds the as-built job's spec, derived and globals, which the finish writes. So a value Update of a part built before F3 writes no `"Bore Allowance"`, keeps its `.gear.json` at 3, and writes no derived allowance. `_ignored_fields_as_built` gains an optional `variables` argument, and reads each trial as built from it. |
| 3 | **`swbuild.structural_change`** | Details below. |
| 4 | **Build again…'s made-new rows** (ruling 1), `gearbox.made_new_job` and `recorded_entry` (new) | A job made new whose row's gear has a part on record (`record.current_parts()`, the first serving any of its gear ids) is planned through `as_built_job` with that part's globals. A row with no part keeps the planned job, which is the default. Reused jobs carry their candidate's as-built job (row 1). |
| 5 | **Print files**, `printout.bore_figures` | Reads `as_built(part.spec, part.variables)`: the bore, the allowance (typed, or the recorded global, or 0), and the Flat with Drive flat. With no bore it gives (0, 0, None). `workbook_print` is not refused for a gearbox built before F3, because `classify` (row 2) finds nothing. |
| 6 | **W9d's carry**, `update._bore_mm` | The hole as cut: Bore plus the allowance as built. None when the allowance on record does not read. `carry_for` reads the plan's jobs, which are as built (rows 1 and 4). The test shows a D's arc face at R = (D + a)/2 named "bore", its flat (not coaxial) not, through `plan_carry`. |
| 7 | **K11**, `swbuild._value_edits`, `_wanted_words`, `_back_words` | Details below. |
| 8 | **K11's cells and W9d's columns** | `_GLOBAL_COLUMN` gains `"Bore Allowance"` → `bore_allowance` and `"Bore Flat"` → `flat`. `_SPEC_COLUMNS` gains *Bore allowance*, *Drive* and *Flat*. Drive is compared in any case, and a missing key is read as round. |
| 9 | **The window's checks** (S3, the tenth caller), `assess.assess(..., record=None)`, `build.plan_parts(..., built=None)`, `build.check_gear(..., variables=None)`, `build.gear_diagnostics(..., built=None)`, `build.built_globals(record)` (new) | Given the record, each row whose gear has a part on record is checked **and planned** as built from that part's globals. Not given (every caller today), nothing changes. |

**Row 3, `swbuild.structural_change`.**
- `drive` joins `STRUCTURAL`. A missing key reads round and the word is read in any case. The sentence is *The drive changed from 'round' to 'flat'; build it again as a new part.*
- Has-an-allowance is read on the built side from `built_variables` (`"Bore Allowance"` present). On the wanted side it is the typed figure (0 is none), or, when blank, the built side's: a blank is as built.
- The sentence is *A bore allowance cannot be added to or taken out of a built part through its values; build it again as a new part.*, beside `has_shift`.
- Has-a-flat is read from `"Bore Flat"` and Drive. That reading only speaks when a record's spec and its globals disagree, since a Drive change is caught first. It says *A D-flat cannot be given to or taken from a built part's bore through its values; …*.
- `update._structural` says *Drive changed from round to flat, which its values cannot carry; build it again as a new part.* (`_COLUMNS` gains Drive) and passes `built_variables` on.

**Row 7, K11.** `DocumentValues` and `PartUpdate` gain `blank_cells`, which `_part` sets to `("Bore Allowance",)` when the part's wanted globals hold it and its cell is blank. K11 then says *Bore Allowance in Gear_m1.5_N25_P is 0.3 in SolidWorks and 0.2 (from its blank cell, the allowance as built) in the workbook: type 0.3 in Gears!V2, or set it back to 0.2 in SolidWorks, and press Update SolidWorks again.* The set-back is the literal. The unsaved-mark sentence and the no-cell sentence take the same words.

**Update after an allowance or a flat is typed (§4.4), shown on the fake:**
- a part without the global, given a typed allowance, is structural;
- a part with it is a value, set in place by `set_global_variable("Bore Allowance", …)`;
- typing 0 on a part with the global is structural;
- a cleared typed figure is kept as built (nothing changes);
- a Flat change is a value (`set_global_variable("Bore Flat", …)`);
- a Drive change is structural.

**The hub row** (W9b) takes all three as any gear. On RangeBox_Fixed its Hub, built with 0.3, flat and 7, holds the three globals, its `.gear.json` is at 4, and a Flat change and a Drive change go as above.

## Every SolidWorks call a D bore's build and Update make, and where the app already makes it

The ops are package A's (`spur._d_bore_ops`, `spur.py` near :1717 in A's tree; `_bore_ops` near :1698). B's `swbuild`
runs them through the runners it has, one per op type (`swbuild.py:447-509`), with no new runner and no new Session
member. On the fake: `test_a_d_bore_is_built_and_updated_through_the_calls_the_app_already_makes`.

| Op | Session member | SolidWorks call | Already made by the app at |
|---|---|---|---|
| `OpenSketch("bore", 1)` | `open_sketch` | select the Front plane, `InsertSketch` (`swcom.py:1688-1702`) | every gear's bore and tooth sketch today |
| `Arc("bore_arc", (0,0), start, end, 1)` | `sketch_arc` | `CreateArc`, direction +1 counter-clockwise (`swcom.py:1743-1747`) | the tooth space's arcs (`spur._space_ops_arcs`, `Arc("E+", …, 1)`, `Arc("R", …, 1)`); a **major** arc is new in kind only |
| `Line("bore_flat", end, start)` | `sketch_line` | `CreateLine` (`swcom.py:1753-1756`) | the tip chord `Line("T", …)` |
| `Relation("coincident", ("bore_arc.centre", ORIGIN))`, the two end coincidents, `Relation("vertical", ("bore_flat",))` | `add_relation` | `SketchAddConstraints` (`swcom.py:1852-1875`) | point-to-point coincidents of a line's end on an arc's end (`spur.py` near :1475, `Relation("coincident", ("T.start", "E+.end"))`); `vertical` at `helical.py:644-645` and `bevel.py:962` |
| `Dimension("Bore", ("bore_arc",), …)` (a radius, `findings.ARC_DIMENSION`) and `Dimension("Flat", ("bore_flat",), …)` (a line's length) | `dimension` | `AddDimension2` (`swcom.py:1890-1902`) | an arc's: `Dimension("Root", ("R",))`, `Dimension("Flank", ("E+",))` in `spur.py`; a line's: `bevel.py:942`, `:976` |
| `CloseSketch` | `close_sketch` | `InsertSketch` (`swcom.py:1712-1715`) | every sketch |
| `Cut("bore_cut", "bore", …)` | `cut_extrude` | `FeatureCut4` through all (`swcom.py:1961-1966`) | today's bore |
| `AddGlobal("Bore Allowance" / "Bore Flat")` | `add_global_variable` | the Equation Manager's `Add2` (`swcom.py:1422-1434`) | every global |
| `LinkDimension("Bore@Bore Sketch", '( "Bore Diameter" + "Bore Allowance" ) / 2')`, `LinkDimension("Flat@Bore Sketch", '2 * ( ( abs ( … ) ) ^ 0.5 )')` (the power bracketed since `bea3a45`) | `link_dimension` | `Add2` (`swcom.py:1436-1438`) | a link to an expression of two globals: `clutch.py:82` (`"Face Width" - "End Band"`); `( abs ( … ) ) ^ 0.5`: `spur.profile_variables`'s Involute t1 and t2 |
| the build's sketch status read | `sketch_status` | `GetConstrainedStatus` (`swcom.py:1724-1726`) | every built sketch |

**The Update of a D in place** (a Flat, a Bore or an allowance changed on a part holding the globals) makes:
- `set_global_variable`: `IEquationMgr.Equation` read and put (`swcom.py:1455-1466`). The app makes it at `swbuild.py:1516` (the strip's Update values) and in W9c's workbook Update. The test shows a Flat change is this one call and no sketch, feature, global or link made.
- The rebuild the Update already makes.
- W9a's reads (equations, feature states), unchanged.

**W9d's "bore" on a D** reads `COAXIAL_FACE_READ` (`swcom.py:4024`), as today. A D's arc face is a partial cylinder. That reading is shown against the fake only, as the plan says: a caveat.

**The fake was not changed.** It takes the D's ops as it takes every op: it records calls and keeps globals. So the build and its Update run on it as they are. What the fake cannot show is the geometry: which branch the arc takes, its sweep, the cut's volume, and a far-side solve after a value change. Those are the demonstration's `dshape` section.

## Choices the plan left open, each the coordinator's to rule

1. **`_match` returns the as-built job**, carried by `_Found.job` into `PartReuse`. Its spec, derived and globals are those of the part found, so the live check and the record hold what the part holds. `_matches` keeps its signature as a bool wrapper.
2. **Ruling 1's "part on record" for a row**: `recorded_entry`, the first of `record.current_parts()` serving any of the job's gear ids. A split (rows that shared a part now differing) gives each new part the old part's allowance.
3. **The journal's units**: globals written in degrees with `trig` "degrees". The document's own units are measured only when it is built, and the match reads the entry in the units it says.
4. **`structural_change` with `built_variables=None`**: read as a part with no allowance, as `as_built` reads an empty `variables`. This is the safe side: adding is refused, not tried. Today only C's strip and old callers pass None, and C's tree now passes the record's globals. Also a D-flat sentence of its own, and the drive sentence giving the words 'round'/'flat' rather than the raw keys (a missing key would have printed None).
5. **`DocumentValues.blank_cells` / `PartUpdate.blank_cells`** (interface short, below): how K11 knows a Bore allowance cell is blank.
6. **The window's rows planned as built, not only checked**, when `assess` is given the record. A row on record then plans the hole its part holds, which is ruling 1 at its root. A consequence, with the switch on: a **new** row identical to a row on record built before F3 plans the default and its part the as-built figure. The two then read as two parts of one file name, an error asking for a Part name, where they would have shared a file. It is the truth (the holes differ) but a new refusal. The other way is to plan as built for the diagnostics only.
7. **`_changed_columns` compares the Bore allowance as recorded text.** So a blank compares blank whatever it was built at, and *its Bore allowance changed* is said only for a typed change.
8. **An allowance or Flat on record that does not read**: `bore_figures` leaves it out (0, None), `_bore_mm` gives None (not "bore"), and `as_built_job` gives the job as planned (the match fails, the part is made new).

## Where the interface was wrong or short

- **Guard 5 cannot be turned green by B's threading.** That is `tests/test_swbuild_user_work.py::test_a_printed_gears_blank_backlash_is_said_as_the_printed_default_and_set_back_as_its_exact_iif`.
  - The test builds its `DocumentValues` by hand from `_values(replace(S17, process="printed"))`: `SPUR.variables` of a printed spec with no record. With the switch on, that holds `"Bore Allowance" 0.2`. The part on the fake was built from S17 without it, so the worker's check phase meets `NotAsBuilt` before K11.
  - No planning runs in this test, so no `as_built_job` can reach it. F3-0's attribution (*B's planning of the job through as_built_job*) does not hold.
  - In the app the worker's variables come from `update._part`, which is as built. There a printed gear on a part built without the allowance plans none, and K11 speaks (`test_k11_says_a_blank_allowance_as_built_…` here).
  - The fix is in the guard's own construction: read its spec through `as_built` with the part's globals. That is an edit to a guard, which only the coordinator can allow. Changing the worker's order, K11 before NotAsBuilt, would move W9a's behaviour for every user and I did not.
- **K11 had no way to know a cell was blank.** `_blank_meaning` sees only the global, and a blank allowance's global is a literal. I added `blank_cells` to `DocumentValues` (swbuild, B's) and to `PartUpdate` (update, B's), default `()`, so every other caller's documents are equal to before.
- **The window does not pass the record to `assess` yet.** `WorkbookWindow._assess` in `workbook_gui.py` passes `blank_process=self._blank_process()`, which reads the record and keeps it to itself. `workbook_gui.py` is no package's file, so I did not wire it. Until a ruling gives that line to someone (pass `record=` the record `_blank_process` reads, None when it is another workbook's), S3 holds for every caller that passes the record, and the window's own warnings still read a row on record as not built. Build again…, Update and Print files do not depend on it: rows 1 to 8 hold without it.
- **The stub pin requires the filled docstrings to keep the phrases.** `test_the_stubs_are_importable_and_neutral_until_their_packages_fill_them` asserts each filled function's docstring still contains "F3-0's stub" and "package B". So the three docstrings say *the body is package B's, over F3-0's stub*.

## Needs the other packages before it can be shown working

- **A's `PRINTED_DEFAULT_IN_PLANS`, `bore_globals` and `_d_bore_ops`.** `tests/test_bore_workbook.py` turns the switch on and builds a D through A's plan. B's commit comes after A's, as the landing order has it.
- **Guard 10 and C's strip pins are C's.** With A's tree and C's work in progress the strip pins pass and guard 10 fails. That is C's `_update_target`, not B's.
- **The window's as-built checks** wait on the `workbook_gui.py` line above.

## What the reviewer should look at hardest

1. **`gearbox._match`**: the candidate's `variables or ()` on both sides, and the `name_changed` check made before replanning. Ask whether any recorded entry (a v1 part, a sidecar with no globals, a journal from before B1) can now match where it did not, or the reverse.
2. **`plan_gearbox`'s reuse holding `found.job`** in place of the row's job. The live check, the finish's `PartEntry` and the `.gear.json` of a journaled part all now come from the as-built job.
3. **`structural_change`'s order.** The allowance and flat tests sit after the bore, shift, groove and band tests and before the small-pinion arc test. A bore added and an allowance typed at once is said as the bore.
4. **Choice 6** (rows planned as built in `plan_parts`) and its shared-file consequence.
5. **Guard 5's analysis** above, by running it with the switch on.

## After F3's review: the coordinator's rulings and B's fixes

F3-REVIEW (`docs/notes-printed/F3-REVIEW.md`, `d394a85`) was ruled by the coordinating session on 2026-11-18, each ruling
the user's to overrule. B's choices 1 to 5 and 8 above are accepted as written. Two are changed, and both are done here:

- **Choice 6 → "rows on record are read as built for the checks only, and the jobs are planned as typed"** (M2).
  - `build.plan_parts` checks a row on record as built (`check_gear(..., variables)`), so its diagnostics speak of the
    hole its part was cut with. It plans the job from the typed row.
  - So a new row identical to a row on record built before F3 shares the old part again with the switch on: one job,
    no *not the same gear*. Build again… reuses the old part for both rows, as built. A row that truly differs (a Face
    width, a typed allowance) is still refused by name.
  - Reuse, Update and ruling 1 already read each recorded part as built from its own entry, so nothing depended on the
    assessment's jobs being as built.
  - One case is planned as built: a typed row that does not work out (its hole at the default reaching the root) gets
    its job from the as-built spec, the part it has. Without that, a row clean as built would have no job, and the
    window would say it is not placed.
  - Tests: `test_the_windows_checks_read_a_row_on_record_as_built_and_its_job_is_planned_as_typed` (which replaces
    `test_the_windows_checks_and_jobs_read_a_row_on_record_as_built`, changed by this ruling),
    `test_a_new_row_identical_to_a_row_on_record_shares_its_part_with_the_default_on` and
    `test_a_new_row_that_truly_differs_from_a_row_on_record_is_still_not_the_same_gear`.
- **Choice 7 → "compare the allowance as built, as a number"** (S3).
  - `update._changed_columns` takes the built part's globals (`variables`, default none). It reads both forms' Bore
    allowance through `spec.as_built` and compares the figures.
  - So a typed 0.3 cleared on a part made new for another reason, which keeps 0.3 by ruling 1, says nothing; nor does
    0 typed where the part holds none. A figure that does not read compares as text, as before.
  - `_why_part_new` passes the entry's globals.
  - Test: `test_w9ds_columns_compare_the_allowance_as_built_as_a_number`.
- **M1.** `pre_f3_desk` no longer asserts the switch is off. It turns the switch off for the build alone, as F2's code
  built the gearbox, and puts it back, so B's tests hold with the switch committed on or off.
- **Guard 5** is corrected by the coordinator's ruling in its own input (M3, `_values(as_built(printed, _recorded(S17)))`).
  The worker is not changed. That edit is not B's.
- **The window's wiring** (`workbook_gui._assess` passing the record) is C's, done at `7051698`. M2 needs no change there:
  `assess`'s signature and `record` argument are as they were.

**Tests and pins, after these fixes**, run in this worktree beside A's and C's work in progress:
`tests/test_bore_workbook.py` (26), `test_printed_rule.py`, `test_printed_window.py`, `test_swbuild_user_work.py`,
`test_workbook_build.py`, `test_workbook_update.py`, `test_workbook_carry.py` and `test_printout.py`.
- **Switch off**: 1071 passed.
- **Switch on**, in its own process: 1070 passed, 1 failed. The failure is guard 5, until its ruled correction lands.
- **The whole suite, switch off**: 5388 passed, 1 skipped, 2 failed: the Tk font test, and
  `test_bore_form.py::test_the_windows_warnings_for_a_gearbox_built_before_f3_are_unchanged_with_the_default_on`, a Tk
  window test of C's that passes run alone (a false failure while other suites ran).
