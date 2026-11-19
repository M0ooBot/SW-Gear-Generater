# Review of F3-0 (the pins and the interface), before packages A, B and C

**Read at `2c47c06` on `printed`**: `062a38e` (the pins), `124a7f9` (the interface and the schema step), `2c47c06`
(`F3-0.md`), against `docs/PLAN-PRINTED.md` at `6f0a462` and `docs/notes-printed/F3-INTERFACES.md`. No SolidWorks and no
Excel. Every run below was made in scratch copies made by `git archive` (deleted afterwards), with `PYTHONPATH=src` and
the import path checked:

| Run | Result |
|---|---|
| **The pins on `08db5ba`'s code** (`git archive 062a38e`: `src` is `08db5ba`'s, `tests` the pins') | `tests/test_printed_rule.py` **448 passed** |
| **The suite at `2c47c06`** | **5187 passed, 1 skipped, 1 failed**: the known Tk font-width test, `test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`. F3-0's figure exactly. |
| **Self-checks** `f1_demonstration`, `f2_demonstration`, `f2_probes` | 0 failed each |
| **`F2_built.json` made again** with the code at `08db5ba` (§1) | a true record |
| **A's default simulated at `2c47c06`**: `"Bore Allowance"` added to the spur's and the helical's globals for a printed blank allowance, then also the summed bore link and the derived `bore_allowance` | both times the same **11 failed**: the six new pins, the four guard tests F3-0 names, and the Tk test. **F3-0's claim is confirmed.** No printed new-build pin outside §4.3's table moved. |

## 1. The pins

**Taken before any F3 code, and they pass there.** `062a38e` changes only `tests/test_printed_rule.py` and adds the
fixture. Its `src` is `08db5ba`'s, and `test_printed_rule.py` passes there, 448 of 448.

**`F2_built.json` is a true record of what F2's code writes.** I made every entry again with the code at `08db5ba`:
- *The three gearboxes:* each built with `test_workbook_in_place_round_trip.Desk` from the test's own
  `_f2_gearbox(name)`.
  - Every record is identical once the `digest` is masked. The digest is `hash(repr(spec))`, salted per process by
    Python's string hashing.
  - Every file list is identical.
  - Every `.gear.json` is identical but for `record_id`, a random `uuid4` (`store.new_record_id`).
- *The four strip parts:*
  - their spec, derived and `variables` equal what `kind.derive` and `kind.variables` give at `08db5ba`;
  - their print lists are identical, through `form_print` and `print_list_text`;
  - `built_sidecar` writes them at sidecar 3.
- *One limit:* the strip parts' `features` (`["Gear"]`), `dimensions` (`[]`) and `manual_steps` (`[]`) are stand-ins, not
  what a build records. Nothing the pins assert reads them except the print list's own `made`, so this is a note, not a
  fault.

**What the pins prove.**
- *Machined:* the strip plans, `.gear.json`s and record entries of a spur, helical, herringbone and bevel gear, a dog
  and a hub. Each also holds read through `as_built` with its own globals (`124a7f9`).
- *Printed parts on record:* classify finds nothing; Build again… reuses every part; the footer is word for word;
  `_changed_columns` is `[]`; `_bore_mm` is the shaft; Print files is not refused, its part blocks word for word;
  nothing is written; the strip's `_update_target` counts 0.
- That is every reader of a recorded blank allowance the plan names, **but for three things they miss:**
  1. **No printed bevel gear on record.** The bevel is where A's change is in link *expressions*
     (`bevel.py:881-893`), not one global. Only the machined bevel is pinned. A printed bevel built before F3 that A's
     code read through the default would go unseen. **Should-fix S1**, before A lands: add a printed bevel with a bore
     (8) to the fixture's strip set, made with the code at `08db5ba` as the rest was. A crown can go with it.
  2. **Nothing that F3 writes to a part built before F3.** The pins read; they never press. Three such writes are
     unguarded:
     - a value Update on a printed part built before F3, say a Teeth change, must leave it without `"Bore Allowance"`,
       its sidecar at 3, and its derived without `bore_allowance`;
     - the strip's Update values on such a record, likewise;
     - Build again… of a row made new by another change, keeping its as-built figure (ruling 1).

     These are B's and C's tests by the plan (§4.6), and they are what keeps the guards honest after the switch below.
     Name them as owed (S2).
  3. **The window's checks.** `assess` validates each row with no record (`build.plan_parts`). So for a printed gearbox
     built before F3, its warnings (the printed rim, the bore against the root) speak of a hole cut at Bore + 0.2 that
     was never cut. The footer pinned holds no warnings, and `workbook/assess.py` and `build.py` are in no package's
     list. Either give them to B as a tenth caller, or say it as a caveat (S3). Its effect is small: only warnings
     near a threshold.

**One pin was changed after it was taken.** `_f2_strip_form` was `strip_form(sidecar, form)` at `062a38e`. At `124a7f9` it
builds its own stand-in whose `_derived["a"]` is derived through `as_built` (`tests/test_printed_rule.py:1067-1074`).
- *What the change means.* It encodes §5's contract that the strip derives through `as_built` while a record is open,
  in place of making `_update_target` derive again itself.
- *Why it is not a loosening.* `_update_target` must still apply `as_built` to the form's spec, and my simulation shows
  the four strip pins failing without that.
- *What it costs.* The strip's own derive (`_load_record`, the Derived panel, and the `derived` that Update values
  writes) is now guarded by no pin. It never was, but at `062a38e` a lazy `_update_target` could not have passed.
- *What should follow* (**should-fix S4**): F3-INTERFACES §12 lists this as a moved line, with why. C's
  `test_bore_form.py` must hold the strip's real path on an opened printed record built before F3: *Bore as cut* says
  the Bore; `_derived["a"].bore_allowance` is 0; Update values after a Teeth change writes no `"Bore Allowance"` and no
  derived `bore_allowance`. That blocks C's done, not its start.

## 2. `spec.as_built` and the record

**`as_built` is right, and it is the one home.** Read line by line (`spec.py`):
- a typed figure wins, and an old `built_allowance` is cleared;
- None means not on record;
- otherwise it takes the recorded literal, spaces squashed, or "0".
- `to_dict` never writes `built_allowance`, `from_dict` drops it (`spec.py`, `known - RECORD_ONLY_FIELDS`), and
  `with_values` keeps it. The last is what `update._ignored_fields_as_built`'s trials need: they replan
  `wanted.with_values(key=…)`, so the as-built figure survives them.
- No code compares `GearSpec`s with `==`, and nothing else iterates `fields(GearSpec)` but `model.py:137`'s pin.

**The nine callers.** Each is the right place and has the right owner, as F3-INTERFACES §6 has them:
- *Reuse* goes per candidate entry through `as_built_job`, which is necessary because the match decides the entry.
- *`update._part`* takes both sides from the same entry's globals.
- *`structural_change`* reads `built_variables`.
- *Ruling 1*, *Print files* (`bore_figures`) and *W9d's `_bore_mm`* are B's.
- *K11* is B's and *K3* C's.
- *The strip* is C's.

One addition: the stub `as_built_job(job, None) is job` is right for "not on record". B's version must also replan the
job's `plan` and `derived`, not only its `spec`, since `_variables_of(job)` reads `job.derived` (`gearbox.py:452-453`).
The docstring says so.

**An empty `variables` read as "built at 0" (F3-0's decision 3) is right, if B does one thing.**
- *Why "0" is right.* Every journal entry and every record with no globals written before F3 is of a part with no
  allowance.
- *The hazard.* Journal entries F3 writes (`gearbox.journal`, `gearbox.py:1113-1121`, `spec` only) would read as 0 too.
  `_Parts.find`'s journaled branch matches with `()` (`:606`), and `_variables_match` with an empty record says
  nothing. So both sides plan at 0 and **a part cut at 0.2 is reused as one at 0**, and its record then lies.
- **Must-fix B1** (blocks B's done, not its start). `journal` writes each job's `variables` (and `trig`), and the
  journaled match passes `entry.variables`. An old journal still reads "0", rightly.

**`sidecar_schema` from the globals is right** (`store.py`).
- It returns 4 when either global is present, machined included (decision 8), and the one-argument calls are unchanged.
- `built_sidecar` and `updated_sidecar` pass `record.variables`. So the strip's Update values and B's finishes must pass
  the *as-built* job's globals (F3-INTERFACES §8 says so); otherwise a part built before F3 would be moved to 4 by its
  first Update.

## 3. The schema step

- **Every moved line is named, and none is weaker.**
  - §4.3's table, and the re-check's `test_printed_rule.py` lines 456 to 458 and 550, are moved as they read in the diff.
    456 to 458 become `(12, 11, 10)`, `(4, 4, 3, 2, 1)` and the sidecar cases from the globals, which assert strictly
    more.
  - `test_store.py:1600-1610` is parametrised. It holds 3, refused by W9's 2, and 4, refused by F2's 3, each
    byte-identical.
- **The five column-letter tests are the same column three letters on.** Each still names the same column, now
  `Y` (Part name), `Z` (Notes) or `AA` (Teeth), and `test_workbook_bands.py:42` now asserts the order of five columns
  where it asserted two.
- **Old workbooks are safe.** Reading is by header (`model.py:336-337`), and so is Apply fix's writing
  (`export.py:226-235`). A user's workbook written before F3, with Part name in V and Notes in W, is read and written
  where its own headers are. No cell lands in the wrong column.
- **An older app and the newer files.**
  - An F2-era app (link 11, sidecar 3) refuses a link 12 record and a sidecar 4 `.gear.json` by `UnknownSchema`, and
    leaves each byte-identical. The mechanism is held for an 8, a 9 and a 3 reader, and the sentence names both numbers.
  - A link 12 record written for a gearbox whose parts are all from before F3 locks the F2 app out of it, as F1's 11
    did. That is the accepted policy.

## 4. The landing order (decision 2)

**What the simulation shows.** The ten guards (six pins, four tests) go red only because *a printed gear with a blank
allowance and no part on record* gets 0.2 in its plan, while the threading that reads a part on record as built is not
yet in. The guards split cleanly between the two packages:
- **B turns five green:** the two gearbox pins, `test_printed_window`'s two Update tests, and
  `test_swbuild_user_work`'s.
- **C turns five green:** the four strip pins and `test_printed_window`'s Update values test.

**Recommended: A lands with the printed blank default behind one switch in A's own file, and the switch is turned on by
a last one-line commit once B and C are in.**

- **A.**
  - Add `spur.PRINTED_DEFAULT_IN_PLANS = False`, and one helper every kind calls for the allowance a plan is cut with.
  - While the switch is False, a blank allowance on a printed gear *not on record* (`built_allowance` "") plans 0; a
    typed figure and an as-built figure plan what they say.
  - Every kind must read the switch from the `spur` module at call time (`spur.PRINTED_DEFAULT_IN_PLANS`), never by
    `from … import`, so that one assignment turns it on everywhere.
  - A's own tests of the default monkeypatch it True.
  - With the switch off the whole suite is green at A's commit.
- **B and C.**
  - Each lands green with the switch off.
  - Each, before it commits, runs the five guards it owns with the switch on, and says the result in its note. For
    example: `PYTHONPATH=src python -c "import sys, pytest; import gear_generator.gears.spur as s; s.PRINTED_DEFAULT_IN_PLANS = True; sys.exit(pytest.main(['-q', 'tests/test_printed_rule.py', 'tests/test_printed_window.py', 'tests/test_swbuild_user_work.py']))"`
  - Each one's new tests set the switch True where they test the default.
- **The switch's commit,** the coordinator's or the last package's: `True`, then deleted with its helper's branch.
  - The full suite must pass there.
  - If a guard is red, the fault is in the threading of the package that owns that guard, never in the guard.
  - The pins are never edited.

Why this rather than one window:
- With other agents committing in this worktree, a branch red for hours between A and the last of B and C is exactly
  the false failure the house rule warns of.
- Here every commit is green.
- Each guard is shown green under its owner's own run.
- The order of B and C does not matter.

## 5. The interface

- **The files are disjoint**: A (gears), B (`gearbox`, `update`, `swbuild`, `printout`), C (`gui`, `ui_text`, design,
  README).
- **A's D sketch needs nothing outside A.** `base.Arc` carries `direction` (`base.py:170-178`) and `swbuild._arc`
  passes it (`swbuild.py:457-459`). `vertical` is in `findings.RELATIONS`. So A touches no `swbuild` and adds no
  SolidWorks call.
- **Sentences** stay with their owners, as the house has them: A's diagnostics in gears, B's structural and K11
  sentences, C's K3, the print list's line and the explainers. They meet through `BoreFigures`, `bore_figures`,
  `structural_change`'s `built_variables`, `as_built_job` and `spec.as_built`.
- **Gaps:**
  - S3's window checks;
  - **one point S4's contract should state outright:** `_update_target` must apply `as_built` to the spec whose
    globals it counts; reading `self._derived["a"]` with the plain spec fails the pins (§1).
- **Decision 3, the print list and the card: right.**
  - A part with no allowance and a round bore keeps *bore 10 mm*, so every list F2 wrote reads the same.
  - A plain machined gear shows no *Bore as cut*, so the machined card pin holds.
  - A printed gear built new at the default shows *8 mm + 0.2 mm allowance (8.2 mm as cut)*, which is what it is.

## 6. The sixteen decisions, my recommended rulings

1. Two notes, as F1-0 and F2-0: **take it.**
2. The default not in the geometry at F3-0: **take it**, landed by §4's switch.
3. An empty `variables` reads "0": **take it**, with B1, journal entries holding their globals.
4. `built_allowance` takes part in equality and `with_values` keeps it: **take it.** It is what the trials need, and
   nothing compares specs with `==`.
5. The default constant in `spec.py`, `spur`'s the same object: **take it.**
6. The names beyond the plan's: **take them.**
7. `to_dict`'s defaults, a typed 0 kept, a Flat kept with Drive round: **take it.** A Flat with Drive round changes no
   plan, so `_ignored_fields_as_built` sets it aside. A may warn; no error.
8. Sidecar 4 whenever the globals hold either name, machined included: **take it.**
9. The fixtures: **take them, and add a printed bevel (S1).**
10. The print list's pin is the whole part block: **take it.**
11. A strip Build while a record is open: **keep the opened part's as-built figure, as ruling 1 does for Build again….**
    The Derived panel shows the as-built hole, and a Build that cut another would contradict it. To take the default,
    type it.
12. The card pin binds C (no *Bore as cut* on a plain machined gear; the explainers out of `EXPLAINER_FIELDS`): **take
    it.**
13. `probe/f1_demonstration.py`'s sidecar judgement left at 3: **take it.** Say in F1's demonstration note that a rerun
    after A meets 4 for a printed part with a bore.
14. The drafted words, and *Drive flat needs a Flat*: **take them.** That check is needed, since `flat_mm()` is None
    there.
15. An allowance typed on a gear with no Bore: **a warning at the cell**, *there is no Bore, so the allowance is not
    used*, not an error. It is harmless, unlike a ring's typed bore fields.
16. The test names: **take them.**

## 7. Must-fix and should-fix

**Must-fix.** None in F3-0's code; the interface, pins and schema step stand. One for package B, blocking B's done
(not its start):
- **B1.** `gearbox.journal` (`workbook/gearbox.py:1118-1121`) writes each job's `variables` and `trig`, and the
  journaled match (`gearbox.py:606`, `_matches(entry.spec, (), "", job)`) passes `entry.variables`. Otherwise a part F3
  cut at 0.2 and left journaled by an interrupted build is reused as one at 0, and its record says so.

**A ruling needed before A starts:** the landing order (§4). A must know whether to write the switch.

**Should-fix:**

| # | What | Blocks |
|---|---|---|
| S1 | A printed bevel with a bore (and a crown) added to `F2_built.json`'s strip set, made with the code at `08db5ba` | A's commit |
| S2 | The writes to parts built before F3 named as owed tests: a value Update and the strip's Update values leaving no global, sidecar 3 and no derived allowance; ruling 1's made-new row | B's and C's done |
| S3 | The window's checks of a row whose part is on record: B's tenth caller, or a caveat in the note (`assess.py` and `build.py` are in no package's list) | a ruling, nothing urgent |
| S4 | `_f2_strip_form`'s change at `124a7f9` listed in F3-INTERFACES §12 with why. §5 says outright that `_update_target` applies `as_built` to the spec it counts globals from. C's `test_bore_form.py` holds the strip's real derive and Update values on a printed record built before F3. | C's done |
| S5 | `as_built_job` replans `derived` and `plan` as well as `spec` (`_variables_of` reads `job.derived`) | B, as written |

**A, B and C may start** once the landing order is ruled. A must have the switch, and B1 and S1 to S5 go into the
packages' instructions.
