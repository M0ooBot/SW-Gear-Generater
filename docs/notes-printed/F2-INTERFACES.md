# F2's interface, as F2-0 built it

PLAN-PRINTED §3.3 names what F2-0 fixes so that packages A (the span over k teeth), B (the export) and C (what the user
sees) cannot collide. This is that list as it stands in the code at F2-0's interface commit, on branch `printed` (from
`02b3ff1`). Every name here is importable from that commit on. Stubs return neutral values, the ones the filled code gives
while every F2 finding is None, so C's window runs before A and B land; `Session.export_step` alone raises, as the plan
says. The three packages meet only through these names.

Where this note and the plan differ, the plan is the authority and the difference is in `docs/notes-printed/F2-0.md` as
a point for the coordinator. The re-check's seven should-fixes (the last section of `docs/PLAN-PRINTED-REVIEW.md`) are
taken here or in the probe, each said where it lands (§9).

What must not move (§3.3): `tests/test_printed_rule.py` whole and F1's tests; W9's pins and every W9 test against the
fake; `tests/test_findings.py`'s existing values and log lines (F2 only adds); no SolidWorks call but the new export and
its reads; no build, Update or Build again… path; the machined Derived panel and every machined record; the workbook's
own Export and Export as….

## 1. `gears/span.py` (new; A's)

- `SpanReading(kind: str, k: int = 0, w_mm: float = 0.0, w_t_mm: float = 0.0, contact_d: float = 0.0,
  needed_face_mm: float = 0.0)`, frozen.
  - `kind` is one of `KIND_SPAN` "span", `KIND_ARCS` "arcs", `KIND_NARROW_FACE` "narrow_face", `KIND_NO_CONTACT`
    "no_contact", `KIND_NONE` "none" (`KINDS`). The figures are 0 unless `kind` is "span"; `needed_face_mm` is set for
    "narrow_face" alone.
  - `w_mm` is W_n (a spur gear's W), what the calipers read square to the teeth; `w_t_mm` is W_t (equal on a spur gear);
    `contact_d` is 2 r_c, r_c = √(r_b² + (W_n cos β_b / 2)²) (§3.0, M1).
- `NONE = SpanReading("none")`.
- `span(derived, recipe) -> SpanReading`. `derived` is what the kind derives (`gears.kind_for(spec).derive(spec)`);
  `recipe` is `spec.RECIPE_INVOLUTE` "A" or `RECIPE_ARCS` "B" (the kind's `recipe_for(spec)`). A tells the gears apart from
  what it is given: a `SpurDerived` is a spur gear, a dog or a hub; a `HelicalDerived` is helical or herringbone
  (`.kind`), and a ring when its `section` is an `InternalDerived`; an `InternalDerived` is a spur ring or a sleeve; a
  `BevelDerived` is a bevel gear; `derived.printed` is False for a machined gear (F1). All of those but the printed
  external ones answer "none". **Stub: answers `NONE` for every gear; never raises.**
- The herringbone's half the plan calls `HelicalDerived.half_width` is `HelicalDerived.toothed_width`
  (`helical.py:180-183` at `02b3ff1`: face / 2 less groove / 2).
- **The β 30° test row** (m_n 2, z 20, printed, k 4, W_n 21.2255) is built with **face 14 mm**: at the default 10 it is
  under its 12.97 mm and reads "narrow_face" (the re-check's should-fix). Its narrow-face test is the same gear at 12.
- A's tests are `tests/test_span.py` (new), everything §3.0 lists, its check against `SpurGear.outline` included.

## 2. `printout.py` (new; B's)

Pure planning. It imports, at run time, `gears.span` and `spec` only; `store`'s, `workbook.assess`'s and
`workbook.update`'s types are annotations only (`workbook.update` imports `swbuild`, which imports this module).

### 2.1 The dataclasses (all frozen)

- `SolidWorksVersion = Tuple[int, ...]`: the revision, as `swcom.Session.revision` reads it, `(34, 1, 1)`; `()` when no
  SolidWorks is connected. (The plan names the type; nothing in the repo had it.)
- `Refusal(code: str, parts: Tuple[str, ...] = (), detail: Mapping[str, str] = {})`. `parts` are stems (for
  `NO_PART` the Gears rows or stems, for `NOT_A_PART` and `NO_RECORD` the active document's file name or none);
  `detail` is keyed per code as §2.3 gives.
- `PrintPart(path, stem, rows: Tuple[str, ...] = (), count: int = 1, process: str = "", span: SpanReading = NONE,
  user_features: Tuple[str, ...] = (), spec: GearSpec = GearSpec())`. `count` is one per row the part serves, times a
  planet's copies; `user_features` is the record's inventory of the user's features in that part (W9a), `()` on the
  form; `spec` is the part's spec as recorded; `span` is A's `span(derived, recipe)` of it.
- `PrintPlan(refusal: Optional[Refusal], parts: Tuple[PrintPart, ...] = (), folder: str = "", revision:
  SolidWorksVersion = (), name: str = "", pressed: float = 0.0)`. A refusal comes with no parts and no folder.
  **F2-0's additions**: `revision` (the version the gate was read for; the job refuses GATE if the session's is not
  this one), `name` (the gearbox's name, the Box's; on the form the part's stem) and `pressed` (the press's time,
  seconds since the epoch, the one its folder is named by), for the job and for the list's head.
- `PrintResult(written: Tuple[Tuple[str, str], ...] = (), folder: str = "", refusal: Optional[Refusal] = None, failed:
  Tuple[Tuple[str, str], ...] = (), facts: Mapping[str, str] = {}, active_restored: bool = True, flags_turned_on:
  Tuple[str, ...] = (), warnings: Tuple[Tuple[str, Tuple[str, ...]], ...] = ())`, defined here (not in `swbuild`, so
  that `write_list` and `ui_text` need not import `swbuild`). `written` is (part path, file); `failed` is (file, reason
  code); `folder` is the press's folder, `""` when none was made; `active_restored` is True when the document active at
  the start is active again (also when the user closed it meanwhile, or none was); `flags_turned_on` names documents
  (paths, a never-saved one by its title) whose save flag the job turned on, a failure C says. **F2-0's addition**:
  `warnings`, (part path, feature names) of features whose `GetErrorCode2` is a warning (§5.4).
- `facts`' keys are `"<file>|schema"` (the FILE_SCHEMA name as written), `"<file>|unit"` (`MILLI.METRE`, `METRE`,
  `INCH`, `FOOT` …) and `"<file>|extent"` (`"checked"` or `"skipped: <why>"`, the why one of `EXTENT_SKIPPED`): data for
  C, never a sentence, never a refusal. `FACT_SCHEMA`, `FACT_UNIT`, `FACT_EXTENT` are the three suffixes.

### 2.2 The codes

Planning (pure, before any job; `PLANNING_CODES`): `GATE`, `GATE_COPY`, `UNSAVED_MARK`, `MISMATCHED_MARK`,
`CHANGES_ON_UPDATE`, `NO_PART`, `WORKBOOK_ERROR`, `FOREIGN_RECORD`, `NO_RECORD`, `NOT_A_PART`. The job (`JOB_CODES`):
`MODIFIED`, `GLOBALS_DIFFER`, `FEATURE_IN_ERROR`, `COMPONENT_ONLY`, `SOLIDWORKS_REFUSED`, `FILE_CHECK`. `CODES` is both.
Each is a module constant whose value is its own name; B returns them, C's tests and B's import them, and no test of B
reads a word.

**The order a planner takes them in** (F2-0's choice, the first that applies is the refusal): `GATE_COPY`, `GATE`; then
on the form `NOT_A_PART`, `NO_RECORD`; in the window `FOREIGN_RECORD`, `WORKBOOK_ERROR`, `NO_PART`, `UNSAVED_MARK`,
`MISMATCHED_MARK`, `CHANGES_ON_UPDATE`. One refusal names every part it applies to. **In the job**: the gate again,
then every part reached and read, then the first failing part's first failing read in the order `COMPONENT_ONLY`,
`MODIFIED`, `GLOBALS_DIFFER`, `FEATURE_IN_ERROR` (one refusal, naming every part that fails that read), before any file
is written; then `SOLIDWORKS_REFUSED` or `FILE_CHECK` during the export, after which the files written stay and the set
is not to be printed.

### 2.3 Each code's detail, and its sentence (C's words, drafted once here)

The sentences are drafts in the plan's words where it gives them; C owns them and may reword, keeping what each says.
`{parts}` is the stems joined as `ui_text` joins names (`_and`); a plural agrees.

| Code | `parts` | `detail` | Draft sentence |
|---|---|---|---|
| `GATE_COPY` | () | {} | *Print files waits until writing a STEP file is measured on this SolidWorks; nothing was written.* |
| `GATE` | () | `year`, `revision` ("2024", "32.5.0"); {} when none is connected; with `planned_year`, `planned_revision` when the session changed since the plan | *Print files waits until writing a STEP file is measured on SolidWorks 2024 (32.5.0); nothing was written.* None connected: *Print files needs SolidWorks running and connected; nothing was written.* Changed: *SolidWorks changed since Print files was pressed (2026 then, 2024 (32.5.0) now): press it again. Nothing was written.* |
| `UNSAVED_MARK` | stems | {} | *Print files wrote nothing: Gear_m1.5_N20_P has changes from Update SolidWorks that are not saved; save it in SolidWorks, then print.* |
| `MISMATCHED_MARK` | stems | {} | *Print files wrote nothing: Gear_m1.5_N20_P no longer holds what the record says; press Update SolidWorks, then print.* |
| `CHANGES_ON_UPDATE` | stems | {stem: "values" or "new part"} | *Print files wrote nothing: Update SolidWorks would change the values in Gear_m1.25_N29_P (and make Gear_m1.25_N13_P new); press Update SolidWorks and save, then print.* |
| `NO_PART` | rows or stems | {name: "no part" or "not on disk"} | *Print files wrote nothing: G3 has no part yet (Gear_x is not on disk); press Build first.* |
| `WORKBOOK_ERROR` | () | {} | *Print files wrote nothing: the workbook has an error; the footer says which.* |
| `FOREIGN_RECORD` | () | {} | *Print files wrote nothing: the record in this folder is another workbook's.* |
| `NO_RECORD` | (file,) or () | {} | *Print files prints a part Gear Generator built: Part1.SLDPRT has no .gear.json beside it.* |
| `NOT_A_PART` | (file,) or () | {} | *Print files prints the part active in SolidWorks: make a gear part active there.* |
| `MODIFIED` | stems | {} | *Print files wrote nothing: Gear_m1.5_N20_P is changed in SolidWorks and not saved; save it, or close it without saving, then print.* |
| `GLOBALS_DIFFER` | (stem,) | `name`, `live`, `recorded` (the first differing global of the first part) | *Print files wrote nothing: in Gear_m1.5_N20_P, "Face Width" is 9 where its record says 8; press Update values (Update SolidWorks in the Workbook window), or put it back, then print.* |
| `FEATURE_IN_ERROR` | stems | {stem: feature names joined by ", "} | *Print files wrote nothing: in Gear_m1.5_N20_P, User Keyway is in error in SolidWorks; fix it there, then print.* |
| `COMPONENT_ONLY` | stems | {stem: the assembly's file name, or ""} | *Gear_m1.25_N29_P is open only inside RangeBox; close the assembly or open the part, then print.* With "": *Gear_m1.25_N29_P is open in SolidWorks but not as the active document; make it active, or close it, then print.* |
| `SOLIDWORKS_REFUSED` | (stem,) | `file` and `errors`, `warnings` (SolidWorks' codes), or `said` (swcom's sentence) | *Print files stopped: SolidWorks would not write Gear_m1.5_N20_P.step (errors 1, warnings 0). The files written are in print\2026-11-18 14.32.05; its print list says not to print them.* |
| `FILE_CHECK` | (stem,) | `file`, `reason` (§2.4) | *Print files stopped: Gear_m1.5_N20_P.step is not fit to print: it does not hold exactly one solid. Its print list says not to print this set.* |

The reasons' words for `FILE_CHECK`: `FRAME` *the file is cut short or is not a STEP file*; `SCHEMA` *it is written in a
STEP schema other than AP203, AP214 or AP242 (Tools > Options > Export sets it)*; `SOLIDS` *it does not hold exactly one
solid*; `OPEN_SHELL` *it holds an open surface*; `SURFACE_MODEL` *it holds surfaces, not a solid*; `UNIT` *its length
unit cannot be read*; `EXTENT` *its outer diameter or face width is not the gear's (by more than 0.01 mm)*.

### 2.4 `check_step(text: str, part: PrintPart) -> Optional[str]` (§3.1.4, M2)

None when the file passes, else the first failing reason in `REASONS`' order: `FRAME`, `SCHEMA`, `SOLIDS`, `OPEN_SHELL`,
`SURFACE_MODEL`, `UNIT`, `EXTENT`.

- **The schema is matched by its name's prefix** (the re-check's should-fix): the FILE_SCHEMA's first string, up to its
  first space or brace, upper case, starting with one of `STEP_SCHEMAS`' prefixes: AP203 `CONFIG_CONTROL_DESIGN` or
  `AP203_CONFIGURATION_CONTROLLED_3D_DESIGN` (its second edition), AP214 `AUTOMOTIVE_DESIGN`, AP242
  `AP242_MANAGED_MODEL_BASED_3D_ENGINEERING`. SolidWorks writes the name and then `{ 1 0 10303 … }`.
- Instances are counted as instances (an instance's entity name, a complex instance's every top-level name), never
  substrings, so a name inside a quoted string is not one.
- **The length unit**: an `SI_UNIT` of `METRE` with or without a prefix in a `LENGTH_UNIT` instance, or a
  `CONVERSION_BASED_UNIT` `INCH` or `FOOT`; two that differ is unreadable.
- **The extent** (built if probe step 3 bears it out, §3.1.4's should-fix; `EXTENT_TOL` 0.01 mm): from the
  `VERTEX_POINT`s' `CARTESIAN_POINT`s in the file's unit, the largest radius from Z against the outer radius
  (`d_a / 2`) and the axial extent against the face width. **Never a refusal for a part with user features** (the
  re-check's should-fix: a boss of the user's can pass the tip circle): there it is a fact, `"skipped: user features"`.
  Also skipped, as a fact, for a bevel gear, a ring, a sleeve, a dog and a hub (`EXTENT_SKIPPED`: a dog's and a hub's
  face teeth and a ring's rim are not `d_a / 2` and the face width), and for every part when the probe's step 3 did not
  bear it out on its two parts (`"skipped: not measured"`). It is checked on printed or machined external spur, helical
  and herringbone gears.
- The probe's own parser (`probe/f2_probes.py`, `step_facts` and its self-check) reads the same things the same way; B
  may lift it.

**Stub: answers None.** Nothing calls it until B fills it.

### 2.5 The files' place (M3)

`PRINT_FOLDER` "print"; `PRESS_FOLDER_FORMAT` "%Y-%m-%d %H.%M.%S" (the press's time; a name that exists gets " (2)",
" (3)" …); `LIST_NAME` "print list.txt"; `STEP_SUFFIX` ".step", each file its part's stem plus it, so
`Gear_m1.5_N20_P_r2.SLDPRT` prints as `Gear_m1.5_N20_P_r2.step` and nothing else gains `_r2`. The planner chooses the
folder (`<Output folder>\print\<press time>`); the job makes `print` and it, after every part's reads have passed and
before the first file, and takes the next counter if the folder has come to exist meanwhile.

### 2.6 The planners and the list

- `form_print(sidecar: Optional[Sidecar], part_path: str, output_folder: str, version: SolidWorksVersion, *, now:
  Optional[float] = None, exists: Callable[[str], bool] = os.path.exists) -> PrintPlan`.
- `workbook_print(record: Optional[LinkRecord], assessment: Optional[Assessment], update_plan: Optional[UpdatePlan],
  output_folder: str, version: SolidWorksVersion, *, now=None, exists=os.path.exists) -> PrintPlan`.
- `now` and `exists` are F2-0's additions, keyword-only, for tests: the press's time (None is the clock) and the folder
  test. Every part of `LinkRecord.current_parts` once, hubs, dogs and sleeves among them; not carriers, the layout, the
  assembly or the user's components. A layout- or assembly-only change Update would make does not refuse (E3). The K11
  comparison B reuses is its own `swbuild._squash` and `_value_edits`.
- `write_list(result: PrintResult, text: str) -> str`: writes `text` as `print list.txt` in `result.folder`, UTF-8,
  never over a file; the path. C calls it after the job's finish (the form's and the window's), with
  `ui_text.print_list_text`'s text, whenever `result.folder` is not "".
- **Stubs**: both planners answer `PrintPlan(Refusal(GATE_COPY), revision=version)`, which is what the filled planners
  answer while `findings.SAVE_AS_COPY` is None; `write_list` writes nothing and answers "".

## 3. The gate (B, twice; C words it)

- `findings.SAVE_AS_COPY` None: `GATE_COPY` on every version.
- `findings.STEP_EXPORT_ON_<year>` not True for the connected version (the year by `swcom.release_year`), or none
  connected: `GATE`.
- In planning, from the version the window's or the form's SolidWorks snapshot gives. In the job, `print_parts` reads
  `sw.revision` and refuses the same way before any document is touched, and with `GATE` (with `planned_*`) if it is
  not the plan's `revision`.

## 4. `swcom.Session` (B's lines)

- `export_step(path: str) -> Tuple[int, int]`: the build document to STEP by `IModelDocExtension.SaveAs(path, 0,
  SAVE_AS_SILENT | SAVE_AS_COPY, null, out errors, out warnings)`, the format from the extension; a path that exists
  refused before SolidWorks is asked; SolidWorks' `(errors, warnings)` back; `SolidWorksError` with the codes in its
  fields (not a sentence for the user) when it answers False, a code is not 0 or no file is on disk. **`SaveAs`, not the
  `SaveAs3` the app already calls** (`swcom.py:1366-1376`): the ledger says to prefer it (`API-LEDGER.md:189`), it is the
  route the macro database verified for STEP (`:190`, files/04), and it gives the codes back. Whether it answers a
  plain bool or a tuple is the probe's step 2. **Stub: raises `SolidWorksError`, writing nothing.**
- `document_by_path(path: str) -> Optional[Any]`: the open document of a file, in its own window or loaded only as a
  component. **`GetOpenDocumentByName` is unverified in the macro database (`API-LEDGER.md:94`) and new to the app**
  (the re-check's should-fix): probe step 7 is its first use, measured beside the document walk
  `use_open_document` already makes (`GetFirstDocument` / `GetNext`, verified). B fills it with the route the probe's
  review settles: `GetOpenDocumentByName` if its answers and controls hold, else the walk. **Stub: answers None.**
- `save_flags()` exists (`swcom.py:3837`), as do `active_document`, `documents`, `activate` (`ActivateDoc3`),
  `close_document` (`CloseDoc`), `use_open_document`, `open_document` (activates), `has_unsaved_changes` (the build
  document only), `equations` and `feature_states` (`GetErrorCode2` with its warning flag).
- `swbuild.SolidWorks`, the Protocol, gains `save_flags`, `activate`, `close_document`, `export_step` and
  `document_by_path` (F2-0's lines). In `tests/test_swbuild.py` the fake `FakeSolidWorks` gains them and the reads they
  need, as B's only edit there; `tests/test_swcom.py` covers `export_step` on `FakeSession`.

## 5. `swbuild.print_parts(sw: SolidWorks, plan: PrintPlan) -> PrintResult` (B's; M5)

**Stub: touches no document and writes nothing; answers the plan's refusal, or `GATE` for `sw.revision`.**

### 5.1 At the start

The gate (§3). Then the active document's title (`active_document`) and every open document's title and save flag
(`save_flags`), before anything is reached.

### 5.2 How each part is reached

W is the window read: True when the part is the active document, or `findings.PART_WINDOW_READ_ON_<year>` reads it in
its own window; False when that read says it is loaded only as a component; None while that finding is None and the
part is not active. "Found" is `document_by_path`.

| The part | How it becomes the build document | Closed after? |
|---|---|---|
| found, W True | by its object (`use_open_document`), no activation, when `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` is False; else (True or None) activated by `ActivateDoc3` first | never |
| found, W False | by its object when `STEP_EXPORT_FROM_COMPONENT_ON_<year>` is True; else, when `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>` is True, `open_document` (activates, opens its window); else refused, `COMPONENT_ONLY` | only the window `open_document` opened, by `CloseDoc` on its title |
| found, W None | by its object when `STEP_EXPORT_FROM_COMPONENT_ON_<year>` is True **and** `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` is False (right either way); else refused, `COMPONENT_ONLY` with ""  | never |
| not found | `open_document` (activates). **When any assembly is open in the session**, only when `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>` is True, else refused `COMPONENT_ONLY`: a part not found may be a lightweight component of it (probe step 7c) | yes, by `CloseDoc` on its title |

**Lightweight components** (the re-check's should-fix): a part whose component is lightweight is reached only as the
table says. `STEP_EXPORT_FROM_COMPONENT` is proposed True only if step 7c shows a lightweight component's document is
either not reached by the object route or reached and written right, and `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` only if 7c's
not-open path is clean; so neither way is used for one unless the probe covered it. The job never sets a component's
state.

### 5.3 The reads, all before any export

On each part, as its document is the build document: its own `GetSaveFlag` (`has_unsaved_changes`): `MODIFIED`; its
globals (`equations`) against the record's `variables`, spaces aside by `_squash` as K11's `_value_edits` compares
them: `GLOBALS_DIFFER`; its features (`feature_states`): `FEATURE_IN_ERROR`. One refusal of one part refuses the set;
nothing is written.

### 5.4 Errors and warnings (the re-check's should-fix)

A feature whose `GetErrorCode2` is non-zero with `IsWarning` False (`FeatureState.warning` False) refuses. One whose code
is a warning does not: the part is exported, and the feature is named in `PrintResult.warnings` and in the list.
(SolidWorks builds a part with a warning; refusing it would block a user's part that SolidWorks itself accepts.)

### 5.5 The export, the check and the end

Each part into `plan.folder` (made then) by `export_step`; each file read back as text (never opened in SolidWorks,
GOTCHAS §20) by `check_step`, its schema, unit and extent kept in `facts`. A `SolidWorksError` from `export_step` is
`SOLIDWORKS_REFUSED`; a failing check is in `failed` and `FILE_CHECK`; the files written stay. In a `finally`: every
window the job opened closed (never an assembly, never a document open at the start), the document active at the
start activated again if it is still open (`active_restored`), and every save flag read again: one the job turned on is
in `flags_turned_on`, never saved over.

B's tests: `tests/test_printout.py` (new) and `tests/test_swbuild_print.py` (new), as §3.3 lists, plus each row of the
table in §5.2 with each finding True, False and None, the lightweight row, and a warning named and not refused.

## 6. `ui_text` (C's lines)

Every sentence a user reads. C owns the words; B hands it the structure above.

- `span_rows(reading: SpanReading, measured: Optional[float], alpha_n: float, module: float) -> List[Tuple[str,
  str]]`: the Derived panel's row after *Tooth at pitch*, and the Measured line. `[]` for "none". Drafts: "span"
  `("Span over 3 teeth", "11.209")` (W_n on a helical gear); "arcs" *not one figure on arcs; choose Involute to
  measure*; "narrow_face" *face too narrow to measure: it needs 13.0 mm*; "no_contact" *no span: no k has both jaws on
  the involute*. The Measured line, for a reading typed (C computes): `e = (reading − w_mm) / 2`, `j = 2 (e + 0.04) / cos
  α_n` never under 0.1 (said when it holds there), and said when `j > 0.3 × module`: *your printer adds 0.041 mm a flank;
  0.172 mm a gear keeps the running play* (2 (0.041 + 0.04) / cos 20°; corrected from 0.22 by F2-0-REVIEW's S6).
- `print_refusal(refusal: Refusal) -> str`: §2.3's sentence.
- `print_result(result: PrintResult) -> str`: the status after a press: the files written and the folder, or the
  refusal; a flag turned on and the active document not put back said.
- `print_list_text(plan: PrintPlan, result: PrintResult, version: str) -> str`: `print list.txt` (§3.1.3), `version` the
  app's (`gear_generator.__version__`); headed *DO NOT PRINT THIS SET:* with the file and the reason when
  `result.refusal` or `result.failed` says so; the user's features by name; the warnings; per part *span over k teeth*
  and k, *no span: machined* (E1, E4), *not one figure* for arcs; the settings said once.
- `print_bar_line(plan: Optional[PrintPlan]) -> str`: the SolidWorks bar's *Print files will write Gear_m1.5_N20_P.step
  from the active part.* for a form plan with one part and no refusal, else "". (The plan left its arguments open.)
- **Stubs**: `span_rows` answers `[]`, the others "".
- **The user's instructions** (C's `README.md`, from §3.2): when the shaft is over 18 mm the four coupons are module 2,
  30 teeth, so the optional Coupon_E is then **module 1.5, 20 teeth, face 8, no bore** (span over 3 teeth 11.209), the
  other size, or it measures nothing new (the re-check's should-fix). §3.2 of the plan is not edited by F2-0.

## 7. `findings` (F2-0's)

All None until a reviewed run of `probe/f2_probes.py` sets them, in a commit of its own that is reviewed;
`tests/test_findings.py` (`test_f2_findings_are_not_measured_until_a_reviewed_probe_run_sets_them`) pins every one unset.

| Finding | From the probe | While it is None |
|---|---|---|
| `SAVE_AS_COPY` (one name, as `SAVE_AS_SILENT`; set when both versions' runs agree) | step 1 | `GATE_COPY` on every version |
| `STEP_EXPORT_ON_2026`, `_ON_2024` | steps 2 to 4 | `GATE` on that version |
| `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` | step 6 | a part open in its window is activated first; the active document put back |
| `STEP_EXPORT_FROM_COMPONENT_ON_<year>` | step 7 (a), (c) | a component-only part goes by the fallback if measured, else `COMPONENT_ONLY` |
| `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>` | step 7 (b), (c) | the fallback is not used; a part not found while an assembly is open is refused |
| `PART_WINDOW_READ_ON_<year>` (**F2-0's addition**, the coordinator's to rule) | step 7's window reads | only the active document counts as in its own window |

There is no `STEP_FILE_CHECK` (M2).

## 8. Who owns which file

- **F2-0 (done):** `docs/notes-printed/F2-INTERFACES.md`, `F2-PROBES.md`, `F2-0.md`, `probe/f2_probes.py`,
  `src/gear_generator/findings.py` (the F2 block), `tests/test_findings.py` (one test), and the stubs' lines in
  `gears/span.py` (new), `printout.py` (new), `swcom.py` (two methods), `swbuild.py` (the import, five Protocol
  lines, `print_parts`) and `ui_text.py` (two imports, five functions).
- **A:** `src/gear_generator/gears/span.py`; `tests/test_span.py` (new).
- **B:** `src/gear_generator/printout.py`; `swcom.py` (`export_step`, `document_by_path`, any private helper they need);
  `swbuild.py` (`print_parts` and what it alone calls); tests `tests/test_printout.py` and `tests/test_swbuild_print.py`
  (new), in `tests/test_swbuild.py` only `FakeSolidWorks`'s new members, in `tests/test_swcom.py` only `export_step` on
  `FakeSession`. B changes no constant or dataclass of §2 without the coordinator; one it must add is said in its note.
- **C:** `gui.py`, `ui_text.py` (the five functions, the explainer, the list's text), `workbook_gui.py`, `design/`,
  `design/UI-DESIGN.md`, `README.md`; tests `tests/test_ui_text.py`, `tests/test_print_form.py` and
  `tests/test_print_window.py` (new).
- Disjoint in `src` and in `tests`. B's `printout` calls A's `span`; C words what A and B return. No package edits
  `findings.py` or `tests/test_findings.py`: the findings' commit after the probe's review does.

## 9. The re-check's should-fixes, where each landed

| Should-fix | Where |
|---|---|
| the β 30° row needs a face over 12.97 mm | §1: face 14 mm (A's test) |
| the schema matched by its name's prefix | §2.4, `printout.STEP_SCHEMAS`; the probe's `schema_ap`, self-checked against it |
| the size check not refusing a part with the user's features | §2.4: a fact, never a refusal |
| `GetOpenDocumentByName` unverified and new | §4; probe step 7 measures it by path and by file name, with two controls, beside the walk |
| lightweight components | §5.2; probe step 7c |
| whether a warning refuses | §5.4: an error refuses, a warning is named |
| Coupon_E for a shaft over 18 mm | §6: module 1.5, 20 teeth, in C's instructions |
