# F2, package B, handed back

Package B of PLAN-PRINTED's stage F2 (§3.1.3, §3.1.4, §3.3; `docs/notes-printed/F2-INTERFACES.md` §2 to §5): the export.
On branch `printed`, written against F2-0's interface while packages A and C were written beside it. No SolidWorks and no
Excel: everything is shown against the fake, with each F2 finding patched where a test needs it. Every F2 finding is
still None in `findings.py`, so in the app every press is refused GATE_COPY until the findings' commit after the probe's
rerun is reviewed.

## Commits

1. `2d32c03` The export: `printout.py` (the planners, the gate, the folder, the file check, the list), `swcom.py`
   (`export_step`, `document_by_path`, `use_document`, `window_read`, `StepExportError`), `swbuild.py` (`print_parts` and
   what it alone calls, two Protocol lines), the fake's six members in `tests/test_swbuild.py`, and the tests
   `tests/test_printout.py` (73), `tests/test_swbuild_print.py` (70) and the `export_step` block of `tests/test_swcom.py` (8).
2. This note.

**Suite** at `2d32c03` with A's commits in and C's work uncommitted in the tree: **5081 passed, 1 skipped, 2 failed**. One
is the known Tk font test (`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`).
The other is C's `tests/test_ui_text.py::test_every_code_has_a_sentence_of_its_own` (C's file, not committed yet), which
fails only because `printout.CODES` now holds `LIGHTWEIGHT` and C has no sentence for it yet (see *For C* below). No
existing test was changed or loosened; the edits to `test_swbuild.py` and `test_swcom.py` are additions only.
`test_printed_rule.py`, F1's tests and W9's pins are green, and no build, Update or Build again… path changed.

## What was built

- **The gate**, `printout.gate(version)`, read by both planners and again by the job: GATE_COPY while `SAVE_AS_COPY` is
  None (first, on every version, connected or not); GATE with no detail when none is connected; GATE with `year` and
  `revision` while `STEP_EXPORT_ON_<year>` is not True. The job also refuses GATE with `planned_year` and
  `planned_revision` when the session is not the one the plan was read for. Both before any document is touched.
- **`form_print`**: the gate, NOT_A_PART (nothing active, or not a .SLDPRT; its file name in `parts`), NO_RECORD (no
  `.gear.json`), else one part named by its stem.
- **`workbook_print`**: the gate, FOREIGN_RECORD, WORKBOOK_ERROR, NO_PART, WORKBOOK_ERROR again when Update cannot say
  what it would change, UNSAVED_MARK, MISMATCHED_MARK, CHANGES_ON_UPDATE, each naming every part it applies to (the
  rules and their reasons are `workbook_print`'s docstring). Each part of `LinkRecord.current_parts` that a Gears row
  still uses, once, hubs, dogs and sleeves among them; its rows in the workbook's order; its count one per row times
  the row's shaft's Copies; its span from A's `span` of the recorded spec; the user's features from the record's
  inventory; its recorded globals and the app's features (from `PartUpdate.made`).
- **The press's folder**: `<Output folder>\print\<%Y-%m-%d %H.%M.%S>`, the press's local time, with " (2)", " (3)" …
  when taken (`press_folder`, `free_folder`); chosen at planning, made by the job after every read has passed, taking
  the next counter if the name has come to exist since. Each file is the part's stem plus `.step`, so `_r2` stays a
  part's revision.
- **`read_step` / `check_step`** on the file as text, in REASONS' order. The schema by its FILE_SCHEMA name's prefix
  (AP203 both names, AP214, AP242); instances counted as instances (a name in a string or a comment is none); **the
  length unit taken from each GLOBAL_UNIT_ASSIGNED_CONTEXT** (F2-0-REVIEW S3: an inch file also holds the SI unit its
  conversion refers to, so the probe's every-LENGTH_UNIT rule would refuse it; a file with no such context falls back
  to that rule). Facts per file: the schema as written, the unit, and the extent "checked" or "skipped: <why>".
- **The size check**: the vertices' largest radius from Z against d_a / 2 and their axial extent against the face,
  each to `EXTENT_TOL` 0.01 mm. Skipped as a fact for a bevel gear, a ring, a sleeve, a dog, a hub, a part holding the
  user's features (on record, or read live by the job from `feature_states` against the record's `made`, so the form's
  parts are covered too), and **every part while `printout.EXTENT_MEASURED` is False**, as it is committed. *The
  tolerance*: the probe's runs (8d2c5fb) read 2026's tip radius up to 0.0012 mm over d_a / 2 (16.501185 against 16.5,
  39.000237 against 39) and the face 0.00003 over; 2024 within 0.00001. 0.01 mm keeps eight times 2026's excess, while
  a cut missing, another part's file or a unit slip is off by far more. I kept the interface's 0.01.
- **`write_list`**: UTF-8, opened "x", so a file already there is a FileExistsError and nothing is written; "" with no
  folder.
- **`print_parts`**: §5 of the interface, step by step in its docstring. Nothing in the job compares exports as text:
  each file is judged alone by `read_step`.

## Every SolidWorks call the job makes, and what gates it

All of them come after the gate (`SAVE_AS_COPY` and `STEP_EXPORT_ON_<year>` True); none is made while either is None.

| Call (swcom) | SolidWorks | When | Gated further by |
|---|---|---|---|
| `active_document` | `ActiveDoc` | start; end | — (verified) |
| `save_flags` | walk + `GetSaveFlag` | start; end | — (verified) |
| `documents` | walk | start (which assemblies are open); end (is the user's still open) | — |
| `document_by_path` | walk + `GetPathName` (`DOCUMENT_BY_PATH_ROUTE` "walk") | each part, before anything is opened | the route constant; `GetOpenDocumentByName` only if the coordinator sets it |
| `window_read` | `IModelDoc2.Visible` or `ActiveView` (read) | each found part not active | `PART_WINDOW_READ_ON_<year>` (None: no read, the part counts as unknown) |
| `open_document` | `OpenDoc6` + `ActivateDoc3` | a part not found with no assembly open; a found component, no window | `UPDATE_OPEN_ROUTE` (W4's); the component case `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>` True |
| `use_document` | none (`GetTitle` etc. to describe) | each part, before its reads and its export | — |
| `activate` | `ActivateDoc3` | a part in its own window while `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` is not False; one it opened, likewise; the user's document at the end | `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` |
| `has_unsaved_changes` | `GetSaveFlag` | each part | — |
| `equations` | `GetEquationMgr`, `Equation`, `Value` | each part | — |
| `feature_states` | `FirstFeature` walk, `GetErrorCode2` | each part | — |
| `export_step` | `IModelDocExtension.SaveAs(path, 0, 1¦2, null, out, out)` | each part, after every part's reads | `SAVE_AS_COPY`; by object without activation only when NEEDS_ACTIVE is False, or FROM_COMPONENT is True for a component |
| `close_document` | `CloseDoc` | only a window the job's `open_document` opened | — |

**Does any call depend on which document is active?** No call the job makes acts on "the active document": every read
and the export act on the build document, which the job sets by `use_document(doc)` (by object) before each part's
reads and again before its export, also after any `activate` (which forgets the build document). The activations are
only there while `STEP_EXPORT_NEEDS_ACTIVE` is not False, as the interface says, and the job sets nothing in any
document. The reads (`GetSaveFlag`, the equations, the feature walk) on a document not active are what W9's
`use_open_document` reads already make on both versions; the probe's failed put (8d2c5fb, step 8 run 1) was a write
(`set_global_variable`), which the job never makes. The probe's hand diagnostic says the export by object on a part not
active wrote that part's own geometry, but that is not a finding until the rerun is reviewed, so the job still activates.

## Choices the plan left open, each the coordinator's to rule

1. **`PrintResult.active_restored` is a required keyword** (`field(kw_only=True)`, no default), S7 read strictly: leaving
   it out is a TypeError. C's code and tests must pass it when they build a PrintResult.
2. **`PrintPart` gains `variables` and `made`** (defaults ()): the interface had no field for the record's globals, which
   the job compares (GLOBALS_DIFFER), nor for the app's features, from which the job tells the user's live.
3. **A new job code, `LIGHTWEIGHT`**, to the ruling after the probe run: a part not found while an assembly is open is
   refused by name whatever the findings, detail as COMPONENT_ONLY's (`{stem: the one open assembly's file name, or ""}`),
   said after COMPONENT_ONLY. Without reading the assembly's components the job cannot tell a lightweight component from
   a part not loaded at all, so a part in no assembly is refused too while some unrelated assembly is open (opening the
   part, or closing the assembly, clears it). The open-beside fallback stays for a found component (the walk reaches only
   resolved ones) with `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` True.
4. **`document_by_path` walks** (`DOCUMENT_BY_PATH_ROUTE = "walk"`): the probe shows the walk reaches resolved
   component-only parts and neither route reaches a lightweight one, so the walk is enough; `GetOpenDocumentByName` is
   built behind the constant, unused.
5. **`use_document(doc)` and `window_read(doc)`** are the two members added to swcom and the Protocol (S4, and the read
   `PART_WINDOW_READ` names); `StepExportError` carries SolidWorks' codes.
6. **`EXTENT_MEASURED`** (False) is a constant in `printout`, not a finding (`findings.py` is not B's): the findings'
   commit should set it True with the others, the probe's step 3 having borne the size out on both versions.
7. **The window's rules**: WORKBOOK_ERROR also for a provisional read, fixes chosen and not exported, and when there is no
   Update plan or it is refused for another reason (the assembly not made yet, unreadable mates); CHANGES_ON_UPDATE
   "new part" for a part classify says needs one (found by its stem opening a sentence of `update_plan.structural`, the
   one place it is said), for a shared part whose rows now differ, and for any gear Update would add in place; a part
   whose every row has gone from the workbook is left out of the set, not refused; marks only on the parts count, never
   on the layout or the assembly.
8. **The job's order**: COMPONENT_ONLY and LIGHTWEIGHT are decided for every part before anything is opened; then the
   first code in the order MODIFIED, GLOBALS_DIFFER, FEATURE_IN_ERROR that any part fails, naming every part failing it
   (GLOBALS_DIFFER the first part alone, with its first global, as the table gives it). A SolidWorksError while reaching
   or reading is SOLIDWORKS_REFUSED with `said` at once. The export stops at the first SOLIDWORKS_REFUSED or FILE_CHECK.
9. **A feature SolidWorks would not give a code for** (`UNREAD`) neither refuses nor is named as a warning.
10. **Facts beyond the three**: `"<title>|close"` "failed: …" for a window the job could not close, `"job|flags"` "unread: …"
    when the flags could not be read at the end. An OSError making the folder propagates (the finally still closes and
    restores).
11. **An empty Output folder**: the part's own folder on the form; the assessment's folder, then the workbook's, in the
    window.
12. **`printout` imports at run time** `findings`, `gears`, `store.same_path` and `swcom.release_year` beside `spec` and
    `gears.span` (the interface listed the last two); none imports `swbuild`.

## For C

`LIGHTWEIGHT` needs a sentence (the coordinator's words: resolve it, or open the part, and press again); C's
`test_every_code_has_a_sentence_of_its_own` fails until it has one. Any PrintResult C builds must pass `active_restored`.
The detail values are the interface's ("values", "new part", "no part", "not on disk"), now also constants in
`printout`.

## What the reviewer should look at hardest

- **The reach table (`reach_way` and the job's step 3)** against §5.2 and the ruling: every None must refuse or take the
  conservative way, and nothing the user had open may be closed. `test_swbuild_print.py` holds each row with each finding
  True, False and None.
- **CHANGES_ON_UPDATE's "new part"** read from `update_plan.structural`'s sentence prefix: if classify's label ever changes,
  such a part still refuses, as "values".
- **The fake's assumptions**: export by object writes the object's document whether active or not, CloseDoc leaves the
  most recently opened window active, a component-only part stays loaded after its window closes. Each is the probe's
  reading or its hand diagnostic, none a finding yet.
- **The unit from the context** and the made-up inch file: no real inch file has been read.
