# F1-0, reviewed

**Read at `bc2b0f5`** (branch `printed`, cut from `w9d` at `f3c4873`): commits 1342e4c, fe89e56, 7991634, 8f201df,
85c1d2d and bc2b0f5, against PLAN-PRINTED §2.8 and the three checks in `docs/PLAN-PRINTED-REVIEW.md`. No SolidWorks.
Everything run below ran in scratch copies made by `git archive` under the session's scratchpad, since deleted;
nothing in either checkout was changed but this file.

**Verdict.** F1-0 is sound and does what §2.8 gives it.

- The pins were taken before any F1 code and hold.
- A machined record is W9's byte for byte.
- The branch behaves for a user as `w9d` does, but for two foreseen differences.
- The marks work.

**Package A may start now. B and C should wait for one small F1-0 follow-up commit** (§7's must-fixes 1 to 3): an
interface name C needs and B must provide, the pair assembly's `_P` ruled and given an owner, and pins for two
kinds of machined sentence that today are guarded only by the test files of the packages about to edit them.

## 1. The pins

**Taken before F1's code.**

- `git diff --stat f3c4873 fe89e56` touches only `docs/PLAN-PRINTED.md` and `tests/test_printed_rule.py`.
- fe89e56's `test_printed_rule.py`, run against f3c4873's `src` and `tests`: **56 passed**.
- At `bc2b0f5`: **268 passed**.
- No hash changed between the two commits (`git diff fe89e56 printed` on the file adds tests and parameters
  only).

**What they hold.** The strip's plan, globals in both trig variants, warnings and file name for 23 gears of every
kind; six assembly plans; Solve on eight pairs, with what the first rows' pairs are told; the four W8 fixtures'
fingerprints; the whole `.gear.json` and record entry of eleven machined parts; and a reducer recorded before F1,
against which Update, Build again…, W9d's columns and the strip's Update values find nothing. At the interface
commit the same hold for each gear said Machined four ways, one with a typed nozzle, and for a Box blank against that
record. That is the rule for a gear, a part, a record and a gearbox.

**Breaking a machined record.**

- F1-0's own mutations (`to_dict` keeping `process`; `"nozzle": null` in `derived`; the machined factor at 0.31)
  are each caught, as its note says.
- `Sidecar`'s default `schema_version` is now 3, but every construction that writes one passes
  `sidecar_schema(...)` (`store.py:387`, `:402`, `:411`) or the version read (`:231`). So no machined file can be
  written at 3 by default.
- The printed equation in the five writers and four derives is held by `WRITERS` (twelve gears) and by the machined
  pins together.
- **What the pins do not hold** (must-fix 3): two kinds of sentence a machined gear is told, which B and C are about
  to edit.
  - I changed `swbuild._blank_meaning`'s `" × "` to `" x "`, which changes K11's sentence for every machined blank
    Backlash. `test_printed_rule.py` passed; only `tests/test_swbuild_user_work.py:556`, B's own file, failed.
  - I changed the card's `" · 0.3m"` in `ui_text.py`. `test_printed_rule.py` passed; only
    `tests/test_ui_text.py:37`, C's own file, failed.
  - The plan's rule says a machined gear "is told exactly what it is told today". The guard for those two sentences
    should not live only in the files of the packages that will rewrite the functions.

## 2. What F1-0 built

- **§2.8 items 1 to 7 are in, as F1-INTERFACES.md states them:**
  - item 1: `spec.py`;
  - item 2: the IIF in all five writers (`spur.backlash_expression`, every writer through it, bevel passing
    `"Module"` quoted, the same global) and the four derives through `blank_backlash`;
  - item 3: `nozzle` on the three section classes, with `derived_dict` in the four `to_dict`s;
  - item 4: `pair.py`'s stubs, with no `printed_pair_warnings`, as ruled;
  - item 5: `Box`, `Setting.words`, the two settings, `to_sheets`' keys and the titles pin;
  - `assess.blank_process` and the keyword;
  - item 6: `GEAR_COMPOUND`;
  - item 7: the schemas.
- **One thing beyond the plan's list:** `spur.field_errors` now reads the Process word and a printed Nozzle (decision
  3). It is in A's file but is F1-0's interface, and is sound.
- **Nothing of A's, B's or C's work.** `ui_text.py`, `swbuild.py`, `checks.py`, `update.py` and `workbook_gui.py` are
  untouched.

**For a user, the branch now behaves as `w9d`, but for two differences:**

- **It writes link records at 11**, which a `w9d` app then refuses. This is by ruling.
- **New workbook… writes two more Box rows, with Process filled `machined`.** `template` still builds
  `Box(name=name)`, whose default is machined, and `to_sheets` now writes the word. A workbook made on this branch
  before B lands is therefore Machined in so many words. B's `template` writes Printed. Nothing else is
  half-done: the form builds `GearSpec`'s machined default, and `_read_box` does not yet read Process.

Do not hand the branch to the user between F1-0 and B.

**The marks, checked independently.** In a scratch copy I simulated B's read (`_read_box` keeping the cell's
Process, blank when there is no row, and its Nozzle) with F1-0's printed backlash live. The whole suite ran
**4389 passed, 1 skipped**, the known Tk font test deselected. With `template` also writing Printed and 0.4,
`test_workbook_window`, `_model`, `_build` and `test_ui_text` gave 503 passed. So no test outside the ten marked
files reads a blank Process today.

## 3. The schema numbers

- **The link record is at 11 whatever its parts.** The `.gear.json` is at 3 only when the dict's `process` reads
  printed, in any case; else 2 for bands, else 1 (held at `test_printed_rule`'s schema test).
- **An older app:** a `w9d` reader (10) refuses 11 by `version > LINK_SCHEMA_VERSION`, and `save_link_record`
  refuses to write over it. A reader of sidecar 2 refuses 3 in `from_json`, and `load` re-raises without moving the
  file.
- **The tests:** the readers of 8 and 9 refusing 11 are tested (`test_workbook_bands.py:377`,
  `test_workbook_carry.py:95`). A reader of 2 refusing a printed `.gear.json` is not; the logic is the same line as
  for 2 against 1. A should-fix, low.
- **Every pinned literal moved, and none asserts less.** The two refusals that wrote 11 as newer now write 12 against
  a reader of 11, with the message's numbers (`test_store.py:1419-1427`, `test_workbook_user_record.py:84-93`);
  each still proves that the next schema is refused and the file left byte-identical. `test_store.py:833` now
  parametrises 12, 13 and 12 (a duplicate case, harmless, F3's to change).

## 4. The tests changed

**None is loosened.** The schema lines change their number only. The ten files' marks wrap each read of a committed
workbook in `machined()`, or patch `link.from_book` for the three window tests in `test_workbook_build`.

**What the marks change** is that those tests no longer prove anything about how a committed workbook's
missing Process is read. That is intended, and it becomes B's to prove: B's new file must assert that each of the five
reads a blank Process (`""` before `assess`) and plans printed with no record (should-fix 2).

**Something to keep:** `machined_reads` patches `workbook.link.from_book`. C's window must keep reading through
`link`, as F1-0's note says.

## 5. The interface, and who owns what

**The interface is precise for A and for most of B and C, and the source files are disjoint.**

- A: `gears/*` and `fixes.py`.
- B: `workbook/schema.py`, `model.py`, `checks.py`, `update.py` and `swbuild.py`.
- C: `gui.py`, `ui_text.py`, `workbook_gui.py`, `design/` and `README.md`.

The test files are disjoint as listed. `test_workbook_window.py` is shared only by C's panel-line edit, which is
ruled.

**One name is missing (must-fix 1).** C's Workbook panel line says *(add a row labelled Process)* "when the sheet
has none" (F1-INTERFACES §8). But `Box.process` is `""` both for a blank cell and for a missing row, and `assess`
then resolves it. C has no way to tell the two apart. B's `_read_box` knows (its `rows` dict) and must expose it. The
name should be fixed now in F1-INTERFACES §5, for example `Box.process_cell: str = ""` (`Box!B9`, or `""` with no
row), the Box's last field. B sets it and C reads it.

C can tell a typed Machined from a blank resolved as built only from the window's raw `reading.spec`, since
`Assessment.read` is resolved. That works, but the note should say it.

**Files with no owner after F1-0:**

- `spec.py` (decision 2 needs an owner);
- `store.py`;
- `workbook/assess.py`, `link.py`, `gearbox.py` (empty under (B)), `build.py`, `geometry.py`, `modes.py` and
  `export.py`;
- `findings.py`, `swcom.py`, `preview.py` and `widgets.py`;
- `src/gear_generator/probe/*`;
- in tests: `test_printed_rule.py`, `workbook_fixtures.py` and the ten marked files.

None needs a change in F1 except `spec.py` (`pair_stems`, if decision 2 is ruled yes) and `test_printed_rule.py`
(must-fix 3). Both are F1-0's to finish before B and C start.

## 6. The twelve decisions

1. **Two notes:** keep both.
2. **A printed pair's assembly: mark it `_P`** (`Pair_m1.5_20T_60T_P`), for D10's own reason. Otherwise a printed
   pair beside a machined pair of the same sizes is refused "already exists" for its assembly alone. It is a
   one-line change to `pair_stems` (`spec.py:497-530`, after the suffixes, when either gear is printed). F1-0 should
   make it, with a pin of `pair_stems` for machined pairs of each shape in `test_printed_rule.py`.
3. **A bad Process word or printed Nozzle is an error at its field: yes.** On the form only a printed gear's Nozzle
   is read, and its row shows only then. **In a workbook, B must pass into the specs only a word and a nozzle that
   checked.** Otherwise one bad Box cell is said once at the Box and again at every gear row (should-fix 1).
4. **Helpers:** keep. `backlash_expression` ignores `module` when printed; every writer passes `"Module"`, so that
   is right.
5. **Signatures:** keep.
6. **Box fields last; no default for Process; Nozzle's default "0.4":** keep.
7. **Case:** keep. B canonicalises the Box's word to lower case.
8. **`with_values` turning a bad word into machined:** accept. The form and the Box never pass one.
9. **The schema tests:** keep, as §3 above.
10. **The drafted words:** accept, with one correction. The tip sentence's *"use a larger module or fewer, larger
    teeth"* points the wrong way for a fixed module, since more teeth give a thicker tip (module 1: 0.27 mm at 12
    teeth, 0.40 at 26). Say *"use a larger module or more teeth"*.
11. **`_SPEC_COLUMNS` in B:** keep.
12. **`test_workbook_xlsx`:** nothing to mark. Agreed.

## 7. Before B and C start

**Must fix** (one F1-0 follow-up commit; A need not wait):

1. **`docs/notes-printed/F1-INTERFACES.md` §5 and §8:** name the field by which B tells C that the Box has no
   Process row (for example `Box.process_cell`, set by `_read_box`, `workbook/model.py:337-376`).
2. **`src/gear_generator/spec.py:497-530` (`pair_stems`):** rule decision 2 and give it to F1-0 to do now, with a
   machined pin. Left as it is, a printed pair beside a machined one is refused for its assembly, and `spec.py` has
   no owner.
3. **`tests/test_printed_rule.py`:** pin what a machined gear is told by K11 and by the card. Two things:
   - `swbuild._value_sentence`, `_wanted_words` and `_back_words` for a blank Backlash and Fillet;
   - `ui_text`'s derived rows and the Backlash field's hint, for a spur, a ring and a bevel gear.

   Today those are held only at `tests/test_swbuild_user_work.py:556` and `tests/test_ui_text.py:37`, the files of
   the packages about to edit those functions.

**Should fix:**

1. **B:** pass only a checked Process word and Nozzle from the Box into each gear (decision 3).
2. **B's new test file:** assert the five committed workbooks read a blank Process and plan printed with no record.
3. **F1-INTERFACES §8:** the tip sentence's advice, *"more teeth"* (decision 10).
4. **`tests/test_store.py`:** a reader of sidecar 2 refuses a printed `.gear.json` and leaves it byte-identical.
5. **Do not hand the branch to the user between F1-0 and B:** New workbook… writes Process *machined* until B's
   `template` lands.
