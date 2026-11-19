# F1's interface, as F1-0 built it

PLAN-PRINTED §2.8 names what F1-0 fixes so that packages A, B and C cannot collide. This is that list as it stands
in the code at F1-0's interface commit, on branch `printed` (cut from `w9d` at `f3c4873`). Every name here is
importable from that commit on. Stubs return neutral values and never raise, so B's and C's printed paths run before
A lands. §2.7's pins are `tests/test_printed_rule.py`; they hold at every commit of F1.

Where this note and the plan differ, the plan is the authority and the difference is in
`docs/notes-printed/F1-0.md` as a point for the coordinator.

## 1. `spec.py`, whole (F1-0's; nobody else edits it)

- `PROCESS_PRINTED = "printed"`, `PROCESS_MACHINED = "machined"`, `PROCESSES` (both), `PROCESS_FIELDS =
  ("process", "nozzle")`, `NOZZLE_DEFAULT = 0.4`, `PRINTED_STEM_MARK = "_P"`.
- `GearSpec.process: str = "machined"` and `GearSpec.nozzle: str = ""`, after the bands.
- `GearSpec.process_value() -> str`: `printed` or `machined` in any case, blank machined; any other word raises
  `InputError("Process must be printed or machined (got 'x').")`.
- `GearSpec.is_printed() -> bool`: `printed` in any case; never raises.
- `GearSpec.nozzle_mm() -> float`: 0.4 when blank; raises `InputError` naming Nozzle on text that does not read
  (`Nozzle must be a number (got 'x').`) or is not above zero (`Nozzle must be more than zero (got '0').`).
- `GearSpec.to_dict()` leaves out `process` and `nozzle` for any spec that is not printed (blank, machined in any
  case, a word that does not read, a typed nozzle with them); never raises. A printed spec keeps both as typed.
  `with_values` goes through `to_dict`, so it also turns a bad word into machined.
- `default_stem` ends a printed spec's stem `_P`, after everything else: `Gear_m1.5_N25_P`,
  `Gear_m1.5_N15_x0.09_P`, `Pinion_..._P` in a pair. A typed name is kept as typed.
- `pair_stems` ends a pair's assembly stem `_P` when either gear is printed (`Pair_m1.5_20T_60T_P`), after every
  other suffix; a typed assembly name is kept, and a machined pair's names are pinned as at the cut (the
  coordinator's ruling 2, F1-0's follow-up).

## 2. The printed backlash (in `gears/spur.py`, F1-0's for items 2 and 3 only; A owns the file after)

- `spur.PRINTED_BACKLASH = 0.3`, `spur.PRINTED_BACKLASH_UP_TO_MODULE = 1.0`.
- `spur.printed_backlash(module) -> float`: `0.3 × module` up to module 1, `0.3` above.
- `spur.printed_backlash_expression(module_name="Module") -> str`: `IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )`;
  `module_name` is the global's name unquoted.
- `spur.blank_backlash(spec, module) -> float`: what a blank Backlash means for the spec, printed or machined.
  All four derives (`spur`, `helical` for its rings too, `internal`, `bevel`) take a blank backlash from it.
- `spur.backlash_expression(section, module="") -> str`: the `"Backlash"` global's text for a derived section,
  shared by all five variable writers (`SpurGear.variables`, `HelicalGear._section_variables`,
  `InternalSpurGear.variables`, `InternalHelicalGear._section_variables`, `bevel.variables`): the literal when
  typed, the IIF when printed and blank, `0.3 * "Module"` otherwise.
- `spur.spec_nozzle(spec) -> Optional[float]`: the nozzle a derive puts on its section, None when not printed.
- `spur.field_errors` reads the Process word for every spec and the Nozzle for a printed one, so a bad word or
  nozzle is an error at its field (`process`, `nozzle`) and derive never meets it. A machined spec's Nozzle is not
  read.

Sleeves, dogs and hubs take all of it through `clutch._Clutch._as_spur`, which uses `dataclasses.replace` and so
keeps `process` and `nozzle`. Nothing in `clutch.py` changed.

## 3. On the derived gears

- `nozzle: Optional[float] = None`, the last field of `spur.SpurDerived`, `internal.InternalDerived` and
  `bevel.RackSection`; set through `spur.profile(..., nozzle=)`, `internal.section(..., nozzle=)` and the three
  `RackSection` / section constructions in `bevel.derive`.
- Properties `printed` (`nozzle is not None`) and `backlash_printed` (`printed and not backlash_typed`) on those
  three, and on `HelicalDerived` and `BevelDerived` through `section`.
- `spur.derived_dict(section)`: `asdict` with `nozzle` dropped while None. `SpurDerived.to_dict`,
  `InternalDerived.to_dict`, `HelicalDerived.to_dict` (its section part) and `BevelDerived.to_dict` (its nested
  section) all use it, so a machined `derived` is byte for byte W9's.

## 4. The pair maths' names (`gears/pair.py`, stubs; A owns the file and fills them)

- `ring_tip_clearance(module, teeth_1, teeth_2, pressure_angle=20.0, helix_angle=0.0, shift_1=0.0, shift_2=0.0)
  -> float`, of `tip_clearance`'s signature, `teeth_2` the ring's. Stub: returns `tip_clearance(...)`.
- `printed_tip_thickness(module, teeth, pressure_angle=20.0, helix_angle=0.0, shift=0.0, nozzle=0.4) -> float`.
  Stub: returns `tip_thickness(module, teeth, pressure_angle, helix_angle, shift)`.
- `solve(..., process="machined", nozzle=0.4)`: accepted and ignored by the stub.
- `shift_for_centre(..., printed=False)`: accepted and ignored by the stub.

Each stub's docstring says it is F1-0's stub and package A's to fill. No pair interference check and no
`printed_pair_warnings` (§2.3, the coordinating session's ruling).

## 5. The workbook's names

- `model.Box.process: str = "machined"` and `model.Box.nozzle: str = ""`, after `format`, so no positional
  construction moves.
- `model.Box.process_cell: str = ""` (`field(compare=False)`), the Box's last field (F1-0's follow-up, the review's
  must-fix 1): **where the Process value was read**, `"Box!B9"`, or `""` when the Box sheet has no row labelled
  Process and for a gearbox built in code. `Box.process` is `""` both for a blank cell and for no row; this field
  is how they are told apart. **B sets it** in `_read_box` (from its `rows` dict, as `at(key)` does); **C reads
  it** for the Workbook panel's *(add a row labelled Process)*. It is left out of `==`, as `GearboxSpec.columns`
  is, and `to_sheets` never writes it.
- **A typed word or a blank, for C.** `Assessment.read` and `.spec` hold the resolved word, never `""`. Whether
  the user typed Machined or left the cell blank and it resolved *as built* is in the window's raw read
  (`reading.spec.box.process`, `""` for a blank), before `assess`.
- **The rulings B works to** (the coordinator, 2026-11-18): B canonicalises the Box's Process to lower case as it
  reads it, any case being accepted (ruling 7); and B passes into the gears' specs (`spec_values`) only a Process
  word and a Nozzle that checked, so that one bad Box cell is said once, at the Box, and not again at every gear row
  (ruling 3). A bad word or a printed gear's bad Nozzle that does reach a spec is an error at its field.
- `schema.Setting.words: Tuple[str, ...] = ()`; `schema.PROCESS_WORDS = ("printed", "machined")`.
- In `schema.BOX_SETTINGS`, after Efficiency and before Units:
  - `Setting("process", "Process", words=PROCESS_WORDS, note="Printed or Machined; blank: Printed for a new gearbox,
    as built for one already built")`, not numeric, no default;
  - `Setting("nozzle", "Nozzle", unit="mm", default="0.4", numeric=True, note="the printer's line width; blank: 0.4")`.
- `to_sheets`' `box_values` gains `"process": box.process` and `"nozzle": box.nozzle`: a gearbox built in code is
  written `machined`, never a blank Process. These two, the settings and the titles pin
  (`tests/test_workbook_model.py`, now "… Efficiency per mesh (%)", "Process", "Nozzle (mm)", "Units") landed in one
  commit.
- `Gear.spec_values(box)` passes `process=box.process` and `nozzle=box.nozzle` (`gear_spec` with it).
- `assess.blank_process(record: Optional[LinkRecord]) -> str`, written whole: `machined` when the record has current
  parts and none reads printed (`GearSpec.from_dict(part.spec).is_printed()`), else `printed` (no record, no parts,
  any part printed). Its body is D11's one switch.
- `assess.assess(..., blank_process="printed")`: a Box whose Process is `""` (stripped) takes the word in both
  `Assessment.read` and `Assessment.spec`; a typed word is left as it is.
- **Not yet**: `_read_box` still builds `Box` without the two keys, so every workbook read today is `machined` by
  the dataclass default. B makes it keep the user's blank as `""`, check the word, and canonicalise it; until then
  `assess` never meets a blank from a read.

## 6. The form's names

`gui.GEAR_COMPOUND = ("kind", "recipe", "process", "nozzle")`. `_gear_spec` does not set them yet (C).

## 7. The record

- `store._W9D_LINK_SCHEMA = 10`, `store.LINK_SCHEMA_VERSION = 11` (the comment above `_W9C`'s says what 11 is).
- `store.PRINTED_SCHEMA = 3`, `store.SCHEMA_VERSION = 3`; `sidecar_schema(spec_dict)` gives 3 when the dict's
  `process` reads printed, else 2 for bands, else 1.
- The literal 10s moved, every one `git grep` found at the cut: `test_store.py` 227 and 1123, plus the refusal at
  1419-1425 (now 12 refused by a reader of 11); `test_workbook_bands.py` 353, 367 and the older reader's message at
  377 (schema 11); `test_workbook_carry.py` 51 (with `_W9D_LINK_SCHEMA == 10`), 75, 79, 95 (the W9c-era reader's
  message, schema 11) and 1057; `test_workbook_user_record.py` 56 and the refusal at 85-91 (12 refused);
  `test_workbook_window.py` 312. `test_store.py:833`'s literal 12 is left for F3 (§4.1); with 11 it parametrises
  12, 13 and 12, which pytest runs. `probe/w9d_demonstration.py:1007` is W9d's script and is not moved.

## 8. Labels and words

`update._SPEC_COLUMNS` gains `("process", "Process")` (B; not in F1-0's commit). Every new sentence's words, for the
package that writes it. Lines in `ui_text.py` are as found at the cut, not the plan's.

**Already in the code (F1-0):**
- `Process must be printed or machined (got 'wood').` (`process_value`, at the `process` field).
- `Nozzle must be a number (got 'x').` / `Nozzle must be more than zero (got '0').` (`nozzle_mm`, at `nozzle`).
- The Box's Process note: *Printed or Machined; blank: Printed for a new gearbox, as built for one already built*.
  Nozzle's: *the printer's line width; blank: 0.4*.

**A (each printed only; `{x}` filled as today's sentences fill theirs, by `_num`):**
- Tip, spur: *Printed, the tooth tip is {t} mm thick after backlash, under one {n} mm nozzle line, so the slicer
  will drop or round it; use a larger module or more teeth.* (Ruling 10: more teeth give a thicker tip.)
  Ring: *Printed, the ring's tooth tips are
  {t} mm thick after backlash, under one {n} mm nozzle line, …* Bevel: *Printed, the tooth tip at the toe is {t} mm
  thick after backlash, …*
- Module: *Printed, a module of {m} mm is under 2.5 nozzle widths ({2.5n} mm), below which a {n} mm nozzle rounds
  the profile off.*
- Radial clearance (said by `mesh_warnings` on the form and by B at a Meshes row, prefixed there as that file
  prefixes its sentences): *Printed, the tip clearance is {c} mm, under the 0.3 mm two printed surfaces take; use a
  larger module or less profile shift.*
- Rim: *Printed, the bore leaves {r} mm of rim under the teeth, under three nozzle widths ({3n} mm).*
- Helix: *Printed, a helix angle of {b}° is over 45°, so the flanks print as an overhang.*
- Ring fillet: *Printed, the ring's {f} mm root fillet is 0.15 × module, under the 0.3 × module printed gears are
  given; it is kept small so the pinion's tips clear it.*
- Single gear's undercut, printed (§2.3), replacing the lead-in after the limit and keeping the named shift:
  *{z} teeth at {α}° is below the undercut limit of {L}. Printed, the gear is made as drawn, with no undercut;
  whether a mate's tip clears its flank below the base circle is not checked here, so turn the pair in
  SolidWorks.{ A profile shift of {x} or more would clear it.}* A machined gear's sentence is unchanged.
- Solve's mark: *thin for a 0.4 nozzle* (the nozzle's figure).

**B:**
- The Box's word check, at its cell: *Process is Printed or Machined (got 'x').* Nozzle: the Box's numeric check
  as for any numeric setting, then *Nozzle must be more than zero (got '0').*
- K11, the printed default (`swbuild._wanted_words` / `_back_words`, `swbuild.py:5474-5489` at the cut): the
  workbook's value *{wanted} (from its blank cell, the printed default: 0.3 mm, or 0.3 × Module below module 1)*;
  the set-back *the equation IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )*, built from
  `spur.printed_backlash_expression()`.
- W9d's reason for a part made new by it: *its Process changed* (through `_SPEC_COLUMNS`).

**C:**
- The card's third state: *0.3 mm · printed default* (`ui_text.py:128`, `:167` and `:520-521` at the cut read
  `backlash_typed`; each reads `backlash_printed` beside it).
- The Workbook panel's Process line, every gearbox: *Printed, {n} mm nozzle*; or *Machined, as built: type Printed
  beside Process on the Box sheet to print it*, with * (add a row labelled Process)* when the sheet has none, that is
  when the raw read's `Box.process_cell` is `""` (§5).

The drafted words above are accepted by the coordinator's ruling 10 (2026-11-18), with the tip sentence's advice
corrected as shown. **What a machined gear is told by K11 and by the card is pinned** in `test_printed_rule.py`
(`K11`, `CARD`): B's and C's changes to those functions must leave a machined gear's words as they are.

**Kept for (A) only, not written under (B)** (D11's three additions; drafts, the coordinator's to rule if (A) is ever
chosen). Each names the Box's Process cell only when the row exists, else says to add the row:
- Footer (`ui_text.workbook_footer`, `ui_text.py:2509` at the cut), when every change is Process's: *Every change
  since this gearbox was built is its Process: the Box's Process is blank, which now means Printed. To keep it as
  built, type Machined beside Process ({cell} / add a row labelled Process with Machined beside it on the Box
  sheet).*
- A third `made_new` reason in `gearbox.py` beside `UNSAVED` and `MISMATCHED`, `PROCESS = "process"`: *it was
  built Machined, and the Box's blank Process now reads Printed*.
- Its way back in `ui_text._reuse_advice` (`ui_text.py:5494` at the cut): *To reuse it as built, type Machined
  beside Process on the Box sheet ({cell} / add a row labelled Process).*

## Who owns which file from now on

As PLAN-PRINTED §2.8 gives it; F1-0 kept to its own list.

- **F1-0 (done):** `spec.py`, `store.py`, `workbook/assess.py`, `gui.py`'s `GEAR_COMPOUND` line, `workbook/schema.py`'s
  `Setting.words` and two settings, `workbook/model.py`'s `Box`, `spec_values` and `to_sheets` keys, items 2 and 3
  in the four gear kinds, `pair.py`'s stubs; tests `test_printed_rule.py`, `workbook_fixtures.py`, the ten
  committed-workbook files and the schema-pin files.
- **A:** `gears/spur.py`, `helical.py`, `internal.py`, `bevel.py`, `clutch.py` if needed, `pair.py`, `gears/__main__.py`,
  `workbook/fixes.py`; tests `test_gears_spur`, `_helical`, `_internal`, `_bevel`, `_clutch`, `_pair`,
  `test_profile_shift`, new `test_printed_gears.py`.
- **B:** `workbook/schema.py` (Backlash column's blank words), `workbook/model.py` (`_read_box`, the word check,
  `template`), `workbook/checks.py`, `workbook/update.py`, `swbuild.py` (K11's words only); tests
  `test_workbook_checks`, `_update`, `_gearbox`, `test_swbuild_user_work`, new `test_printed_workbook.py`.
- **C:** `gui.py`, `ui_text.py`, `workbook_gui.py`, `design/`, `README.md`; tests `test_gui_spec`, `test_ui_text`, new
  `test_printed_window.py`, and in `test_workbook_window.py` only the pinned panel text the Process line moves.
