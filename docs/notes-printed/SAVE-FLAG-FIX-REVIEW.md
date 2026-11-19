# Review of the save-flag fix (b668cf0)

Reviewer: an Opus subagent, independent of the fix's author, on branch `printed` at `c53d6c6` (the fix is `b668cf0`;
`741c3da` and `c53d6c6` after it touch no code under review). No code was changed. Scratch copies were made and
deleted. No SolidWorks was started.

**Verdict: right and minimal. No must-fix.** For an Update values that sets something, every call that changes or
marks the part, and their order, is what it was. The only change in what such an Update sends SolidWorks is the reads:
the Equation Manager is read twice (`equations`, then `equation_values`, which calls `equations` again) *before*
`detect_trig_units`' add and delete, where it used to be read once *after* them. Two paths changed in what they send
SolidWorks: the quiet one, and the refusal of a part that is missing a global. Neither of them writes anything now.

## 1. An Update that sets something: same calls, same order

Before: `begin_build`, `detect_trig_units` (Add2, Value, Delete), `equations`, `planned_changes` in the measured
unit, then evaluate, the landing route and the batches. After: `begin_build`, `equations`, `planned_changes` in
both units (pure), `equation_values` (a read, `swcom.py:1445`, the same `GetCount`/`Equation`/`Value` calls
`equations` makes), `_held_unit` (pure), and then the rest exactly as it was.

- **The units are measured before the first set.** `_held_unit` returns a unit only when that unit's plan is empty
  (`swbuild.py:3193-3199`). So when there is something to set in the unit the part holds, `held` is `""`,
  `detect_trig_units` runs, and `changes = by_unit[measured]` is exactly what `planned_changes(current, variables,
  measured)` was. `current` is the same text whether it is read before or after the add/delete pair.
- **W9c's landing route and the rebuilds** take `current`, `variables` and `result.trig`, and all three are as
  before. `_landing_route` (`:1637`) reads only the equations' text, never the floats in `current`, so reading
  before the add/delete cannot move it.
- **Measured, not just argued.** I wrapped `update_variables` in a pytest plugin and ran `test_swbuild.py`,
  `test_swbuild_print.py` and `test_workbook_update.py` under the old code (`b668cf0^`'s swbuild.py) and the new
  code. That made 77 calls: 71 that set something, 4 quiet, 2 refusals. For all 71 that set something, the fake's
  logged call sequence, `changed`, `trig` and `failures` are identical. Every call made from the workbook
  tests was one that sets something: the workbook's Update reaches `update_variables` only for documents its
  `_check_live` found not holding their values. The fake does not log reads, so the read order above comes from
  reading the code.

So every SolidWorks demonstration of W4 to W9 and F1 to F3 that passed through an Update values or the workbook's
Update still stands as evidence for the code now. The only difference is the extra reads before the add, and those
reads are the very calls `_read_live` makes on every workbook Update. The notes record that they mark nothing
(`swbuild.py:3063-3067`, gearbox_smoke 2026-11-13).

## 2. The quiet path

Calls now: `_gate`, `active_document`, `begin_build`, `equations`, `equation_values`, the pure evaluate,
`end_build`. `begin_build` and `end_build` only get and restore a user preference toggle
(`swcom.py:1294-1317`) and were made before too. Nothing is added, deleted, put, rebuilt, suppressed or saved.

What it returns: `changed == []`, `unchanged` is every name, `rebuilt` False, `failures` empty, all as before.
`ui_text.update_status` (`:938-944`) reads only `failures`, `changed` and `rebuilt`, so the user still reads
*Nothing to update: every value in … already matches the form.*

**`result.trig` is the one difference.** It is now the unit the text and the values show, degrees first, where it used
to be the measured unit. The two can differ only on a part that holds no global whose degree and radian forms differ.
On such a part degrees is reported whatever the document's setting. Every involute gear holds such globals (a spur at
defaults: Base Diameter, Involute Fn, Flank Arc Radius), and there `_values_off` tells the units apart. On a part
with none, the text is the same in both units, so nothing written from `trig` changes:
- the strip's `_finish_update` writes the record only when `changed` is not empty (`gui.py:2045`);
- the workbook's finish (`workbook/update.py:2172-2189`) writes `expression_for(trig)`, which has the same text,
  and stores `entry.trig` only when it writes anything at all. It is reached for such documents only after
  `_check_live`, which already makes the same degrees-first choice (W4 review S2).

This is not a fault. It is said here so that nobody reads a quiet path's `trig` as a measurement.

## 3. Can reading first go wrong where measuring first did not?

- **Equations that cannot be read.** `equations()` raises as before, now without the add/delete having marked the
  part first. If `equation_values` fails (`SolidWorksError`, `EquationError`), `values = None`, the part
  is measured, and the old path runs. It is never judged quiet on the text alone. Every COM failure comes out as
  `ComError(SolidWorksError)` from `swcom.call`, so that catch covers what can reach it.
- **No equations, or a global missing.** `planned_changes` raises the same BuildError with the same sentence, but
  now before any measurement. This is the second path that changed in what it sends:
  `test_update_values_refuses_a_part_without_the_globals` used to log `detect_trig_units` and now logs none, with
  the same error. That is an improvement: a refused part is no longer marked. A missing name raises in either unit,
  so planning both units adds no new refusal.
- **The angle units needed to compare a value.** None are needed from SolidWorks. `_values_off` evaluates the form's
  values in each candidate unit with the app's evaluator and compares them with SolidWorks' `Value`s.
  - A false "off" (a value judged different when it is not) only falls back to measuring, which is the old behaviour.
  - A false "held" (a part judged to hold the form in a unit it is not in) would need two things at once: (a) the
    part's text to equal the form exactly in that unit, and (b) no trig global whose value differs between units, or
    the form's values not evaluating in that unit at all, which makes `_values_off` return None. Case (b) with no
    trig global is the harmless case in section 2. The second case of (b) would need a part whose own text, built and
    verified by the app, no longer evaluates in degrees. Even then the result is a refusal (*the new values do not
    evaluate*), never a wrong write.
- **A part SolidWorks will not let be changed.** Before, a quiet Update could fail at `detect_trig_units`' Add2.
  Now it reports nothing to update. That is the truer answer.

## 4. The three tests and the fake

I ran each test against `b668cf0^`'s swbuild.py with `b668cf0`'s tests:
- `test_a_quiet_update_values_makes_no_changing_call_and_leaves_the_save_flag_as_it_was[degrees]` and `[radians]`
  **fail before the fix**. With the call-name assertion removed in a scratch copy, they still fail on the save flag
  alone (`touched` holds the part).
- `test_print_files_after_a_quiet_update_values_is_not_refused_as_changed` **fails before the fix**. With its
  `detect_trig_units` clause removed in the scratch copy, it still fails on the print step alone:
  `Refusal(code='MODIFIED')`. So each assertion is meaningful on its own.
- `test_an_update_values_that_sets_a_value_measures_the_units_first_as_before` passes before and after, as intended.
  It pins the order measure, then set, then one rebuild.

The fake: `add_global_variable` now calls `_touch()`. What was measured on real SolidWorks is the add/delete pair
marking the document (gearbox_smoke 2026-11-13 on 2026, F3's runs on 2026 and 2024). An add left in place was not
measured separately, but it is a stronger change than an add followed by a delete, so marking it is a safe inference
and not one that flatters the code. It changes no other test: the old tests pass against the new code (649 in the
three files). With the fix, the full suite has 5395 passed, 1 skipped, and 1 failed: the known Tk font-width test,
`test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`. No test was loosened.

## 5. The other callers of detect_trig_units

- **A new part's build** (`swbuild.py:728`): a new, unsaved document that is about to be written. Right.
- **`_evaluates`** (`:3228`, called at `:4440` and `:9612` only for documents whose `holds` unit is `""`,
  so documents about to change). It opens the document and measures only when the new values evaluate in one unit and
  not the other. Right in intent. One edge, older than this commit and not in its scope: if `_evaluates` then raises
  (the values fail in the document's unit), or the job stops at `_held_in_error` just after, the document is left
  marked with nothing written. This needs values that evaluate in one unit only (an acos or asin near its domain
  edge), so it is rare. **For the coordinator to rule on: note it, or fix it some day by deciding the unit from the
  text first. It does not block this fix.**
- **The in-place bands' steps** (`_band_step`, `:6484` given back, `:6496` added): each sets or adds globals, or
  runs band ops, on the part straight after measuring. Right.

None of them is a quiet path.

## 6. Must any SolidWorks section be run again?

No, beyond F3's `built` section, which is being rerun on both versions now. Since `c53d6c6` that section also
counts the strip's calls by member and fails on any Add2, Delete or Equation put. No changing call and no ordering of
changing calls differs on any path that sets something. The new reads are the ones `_read_live` has made on real
SolidWorks on every workbook Update since W4's fix 3 (`a9d20ab`). One suggestion that is not a must: let the rerun's
log show one Update values that *sets* (F3's value steps do) with `detect_trig_units`' Add2 counted before the first
put. That would show the moved read order live.
