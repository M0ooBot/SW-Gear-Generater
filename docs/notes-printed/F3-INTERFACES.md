# F3's interface, as F3-0 built it

PLAN-PRINTED §4.6 names what F3-0 fixes so that packages A (the gear maths and the plans of the bore), B (the record's
comparisons, the workbook, Update and Print files) and C (what the user sees) cannot collide. This is that list as it
stands in the code at F3-0's interface commit, on branch `printed` (from `08db5ba`). Every name here is importable from
that commit on. Stubs return the neutral value, what every part built before F3 reads, so B's and C's paths run before
A lands. The three packages meet only through these names.

Where this note and the plan differ, the plan is the authority and the difference is in `docs/notes-printed/F3-0.md` as a
point for the coordinator. The re-check's five points (the last section of `docs/PLAN-PRINTED-REVIEW.md`) are taken here,
each said where it lands (§10).

What must not move (§4.6): W9's pins (`BEFORE_W7`, `BEFORE_W8`, the W8 and W9 fixtures' counts, every W9 test against the
fake); every machined pin of F1 and `tests/test_printed_rule.py` but for the lines §12 lists; F2's `test_span.py` and the
findings and their pins (`tests/test_findings.py` is untouched); no SolidWorks call added or changed; and **a printed part
on record never moves** (§1).

## 1. The rule, and the pins that hold it

**The rule (§4.1.1).** For a part on record, a blank Bore allowance is the figure the part holds: the literal of
`"Bore Allowance"` in the record's `variables`, or 0 when the part has no such global, as no part built before F3 has.
For a row or a form with no part on record, a blank is the current default: `spec.BORE_ALLOWANCE_DEFAULT` (0.2) printed,
0 machined. A typed figure is what it says, 0 and negatives included.

**Its one home is `spec.as_built(spec, variables) -> GearSpec`**, written whole in F3-0 (§2). It sets
`GearSpec.built_allowance`, which `bore_allowance_mm()` reads after a typed figure and before the default, and which no
record ever holds. So every `derive` and every plan of an as-built spec sees the hole the part holds, with no record
entry in hand.

**The pins** (`tests/test_printed_rule.py`, F3-0's file; no package edits it):

- *Machined* (pins commit). The `.gear.json` and record entry of every kind a bore reaches, the ungrooved herringbone and
  the dog added to `RECORDED` beside the spur, helical, bevel and hub already there; every strip plan of every kind
  (`STRIP`, already); K11 and the card (already). At the interface commit, also: every gear of `GEARS` read through
  `as_built` with its own recorded globals plans, says and records as at the cut
  (`test_a_machined_gear_read_as_built_from_its_record_plans_says_and_names_as_at_the_cut`).
- *Printed parts on record* (pins commit). `tests/fixtures/printed/F2_built.json`, made by running the code at `08db5ba`
  in a scratch archive, holds four parts built from the form (a printed spur, helical and herringbone gear at
  GearSpec's default Bore 10, and §3.2's Coupon_C with its offset typed in Bore, 8.2) and three gearboxes built on the
  fake as `test_workbook_in_place_round_trip.Desk` builds them (the 12 : 1 reducer printed; RangeBox_Fixed printed and
  machined, its Sun 8, Planet 4, dogs 8 and Hub 8 bored, since the fixture's rows have none), each with what the code
  said of it then. Two tests read them as F3 must:
  - `test_a_printed_part_built_from_the_form_before_f3_reads_after_it_as_it_did`: the form put back holds the record's
    spec; no Gears column changed; `structural_change(..., built_variables=...)` empty; `gui.GearApp._update_target`
    counting 0 with the strip holding the record open (§5's contract); `form_print` not refused; the print list's part
    blocks word for word F2's, *bore 10 mm*, no allowance named.
  - `test_a_gearbox_built_before_f3_reads_after_it_as_it_did`: `update.classify` changes nothing and matches the record;
    `plan_gearbox` reuses every part (through `_Parts.find`); the footer word for word; `_changed_columns` `[]`;
    `update._bore_mm` the shaft's own size; `workbook_print` not refused and its part blocks word for word; nothing
    written (the record's text but for the schema number a write moves, the `.gear.json` files as F2 wrote them, at 3
    printed and 1 or 2 machined).
  - At the interface commit, also `test_every_part_f1_and_f2_built_reads_as_built_with_no_allowance`: each part of the
    fixture through `as_built` reads `built_allowance` "0", allowance 0, the hole its Bore, and its `to_dict` the
    recorded spec.

**They fail when a part F1 or F2 built is made to read changed** (scratch copies of the interface commit, since
deleted; counts of `test_printed_rule.py`'s 483):

| Made to read changed | Failed |
|---|---|
| A's global for a printed blank allowance (`"Bore Allowance" 0.2` in `SpurGear.variables` and the helical's), with no B or C threading: M1 itself | 6: the four strip parts (`_update_target` counts 1) and the printed reducer and RangeBox_Fixed (Update changes their bored parts, the record no longer matches); the machined RangeBox holds |
| `to_dict` writing `built_allowance` | 112, every machined record pin among them |
| `derived_dict` keeping `bore_allowance` at 0 | 55, the machined `.gear.json` pins among them |
| the print list saying *+ 0 mm allowance* on every bore | 7: every fixture's part blocks |
| `as_built` reading a part with no global as not on record (the default) | 26 |

**What A's global does to the rest of the suite until B and C land** (the first row above, the whole suite): besides
the six pins, four existing tests fail, each a part on record that the threading must keep as it is, and **none of
them is to be changed by any package**:

- `tests/test_printed_window.py`: `test_an_old_records_form_changed_to_printed_is_one_global_for_update_values` (the
  strip counts the allowance's global as a second change: C's `_update_target`),
  `test_a_gearbox_built_before_f1_opens_machined_as_built_and_unchanged` and
  `test_printed_typed_on_a_built_gearbox_says_the_names_kept_once_and_not_on_the_next_update` (Update says each part
  needs the global "Bore Allowance": B's `update._part`);
- `tests/test_swbuild_user_work.py::test_a_printed_gears_blank_backlash_is_said_as_the_printed_default_and_set_back_as_its_exact_iif`
  (`NotAsBuilt` on "Bore Allowance": B's planning of the job through `as_built_job`).

Nothing else in the suite moved under that run: no pinned printed new-build line outside §12's table moves when A's
default lands. So the suite is whole again only once A, B and C are all in (F3-0.md, decision 2).

## 2. `spec.py`, whole (F3-0's; nobody else edits it)

- `DRIVE_ROUND = "round"`, `DRIVE_FLAT = "flat"`, `DRIVES` (both), `BORE_FIELDS = ("bore_allowance", "drive", "flat")`,
  `RECORD_ONLY_FIELDS = ("built_allowance",)`, `BORE_ALLOWANCE_GLOBAL = "Bore Allowance"`, `BORE_FLAT_GLOBAL = "Bore Flat"`,
  `BORE_ALLOWANCE_DEFAULT = 0.2` (mm on the diameter; the one constant V1 replaces; spur's and the Gears column's note
  follow it).
- `GearSpec` gains, after `nozzle`: `bore_allowance: str = ""`, `drive: str = "round"`, `flat: str = ""`,
  `built_allowance: str = ""`.
- `bore_allowance_mm() -> float`: a typed figure (any sign, 0 included); else `built_allowance`; else 0.2 printed; else
  0. Raises `InputError("Bore allowance must be a number (got 'x').")` on text that does not read. It does not ask
  whether the gear has a bore.
- `bore_as_cut_mm() -> float`: Bore plus the allowance, 0 with no bore.
- `drive_value() -> str`: round or flat in any case, blank round; else `InputError("Drive must be round or flat (got
  'x').")`. `has_flat() -> bool`: Drive is flat in any case; never raises.
- `flat_mm() -> Optional[float]`: None when blank; `InputError("Flat must be a number (got 'x').")`.
- `to_dict` leaves out `bore_allowance` and `flat` when blank (spaces aside), `drive` when blank or round in any case,
  and `built_allowance` always. A typed 0 allowance is kept: it differs from a blank.
- `from_dict` drops `built_allowance` should a record hold one (the re-check's point 2).
- `with_values` keeps `built_allowance` unless changed: it says what the part on record holds.
- **`as_built(spec, variables)`**, pure, never raises:
  - `variables` None (no part on record), or a typed allowance: `built_allowance` "".
  - `variables` given and the allowance blank: the literal of `"Bore Allowance"` among them, spaces aside; `"0"` when
    there is none. **An empty `variables` reads "0"** (the re-check's point 3): a part on record whose record lists no
    globals reads as built with no allowance. That is a v1 record (which the reuse match refuses anyway) and the build
    journal's entries, which `gearbox.journal` writes with `variables` empty and which `_Parts.find` matches with `()`
    (`gearbox.py:606`). B must not let that reuse a part F3 built at 0.2 as one at 0 (§6).
  - Nothing else changes; `as_built(s, v).to_dict() == s.to_dict()`.

## 3. The gears' names (`gears/spur.py` and `bevel.py`; package A's from here)

- `spur.BORE_ALLOWANCE` ("Bore Allowance"), `spur.BORE_FLAT` ("Bore Flat"), `spur.BORE_ALLOWANCE_DEFAULT` (0.2): the spec's,
  imported. `spur.FLAT_LEAST_H = 0.25` (× R) and `spur.FLAT_LEAST_DEPTH = 0.3` (mm).
- `SpurDerived` and `bevel.RackSection` gain, last: `bore_allowance: float = 0.0` (the allowance the hole is cut with,
  mm) and `bore_flat: Optional[float] = None` (the shaft's Flat with Drive flat), and a property `bore_as_cut` (bore plus
  allowance, 0 with no bore). `spur.derived_dict` leaves them out at 0 and None, so the four derived `to_dict`s
  (spur, internal, helical's section, bevel's section) write what they wrote. A helical, herringbone or bevel gear's
  figures are on its `section`.
- **Not yet set by any derive**: A sets them from `spec.bore_allowance_mm()` and `spec.flat_mm()` when the gear has a
  bore. A's globals: `"Bore Allowance"` only when the allowance is not 0 (as `"Profile Shift"`), `"Bore Flat"` only with
  a D; the link and the D's sketch exactly as §4.2 states them (the major arc from the chord's +Y end, direction +1;
  the chord's link `2 * ( abs ( R * R - h * h ) ) ^ 0.5`, never `sqr`).
- **Where the flat sits** (ruling 2, and the re-check's point 1): on +X, square to the X axis, facing a tooth space's
  middle. In a spur gear, a dog and a hub a space is centred on +X on the Front plane; **in a helical gear it is so at
  its section plane, one overrun behind the Front plane** (`helical.py:206-232`, `:558-564`), so the Front-plane face is
  turned `hand · 360 · overrun / L` from it; **in a herringbone at its mid-plane**. Unverified, and said so: that a sketch
  on those offset planes keeps the model's +X; mirrored, the space would be on −X, the same thing for an even tooth
  count only. Nothing the app reads would tell, and the assembly does not model the flat (ruling 2).
- A's checks and their sentences are §9's.

## 4. The Gears columns and the model (`workbook/schema.py`, `model.py`; F3-0's commit, then B's)

- `schema.DRIVE_WORDS = spec.DRIVES`. In `schema.GEARS`, after End band and before Part name (G3):
  - `Column("bore_allowance", "Bore allowance", "mm", blank="0.2 printed for a new part, as built for a part on record, 0
    machined", numeric=True, width=19, help=...)`, the 0.2 from `BORE_ALLOWANCE_DEFAULT`;
  - `Column("drive", "Drive", blank="round", words=("round", "flat"), width=8, help=...)`;
  - `Column("flat", "Flat", "mm", numeric=True, width=10, help=...)`.
  So Bore allowance is column V, Drive W, Flat X, Part name Y and Notes Z.
- `model.Gear` gains `bore_allowance`, `drive`, `flat` (all `""`), after `end_band` and before `row`. `spec_values` passes
  them (`drive or "round"`) and `built_allowance=""`: a row's spec is not on record until B's planning reads its record
  through `as_built`.
- A diagnostic's `field` of `bore_allowance`, `drive` or `flat` names its cell through `build._where` as any field
  whose key is its column's, so a ring's or sleeve's typed bore field is an error at that cell with no mapping added.

## 5. The form (`gui.py`; package C's from here)

- `gui.GEAR_VARS` gains `("bore_allowance", ...)`, `("drive", ...)`, `("flat", ...)` (each side's StringVar exists from
  F3-0; C gives them their rows under Bore, Flat showing while Drive is flat).
- `gui.GEAR_RECORD_ONLY = ("built_allowance",)` beside `GEAR_WORKBOOK_ONLY`.
- **The strip's contract, which the pins hold** (`_f2_strip_form`): while a record is open (`self._loaded`), the form's
  spec is read through `spec.as_built(spec, self._loaded.record.variables)` before every `derive`, so `_derived["a"]` is
  the as-built gear and *Bore as cut* says what the part holds. **`_update_target` takes the form's spec from
  `_gear_spec("a")` as it is and applies `as_built` itself**, for the globals it compares and for
  `structural_change(..., built_variables=self._loaded.record.variables)`; Update values writes the record from the
  same as-built spec (its `to_dict` holds no `built_allowance`) and its globals.

## 6. The record's comparisons, the workbook and Update (package B's)

Stubs, each neutral and each saying so in its docstring:

- `gearbox.as_built_job(job: PartJob, variables) -> PartJob`: the job replanned for the part on record whose globals
  are `variables`: `spec.as_built(job.spec, variables)` and its derived and plan from that spec; None gives the job as
  planned. **Stub: gives the job as it is.** The reuse match is tried per candidate entry through it: `_matches` keeps
  its signature (`spec_dict, variables, trig, job`) and replans `job` with the candidate's `variables` before `same_part`
  and `_variables_match`.
- `swbuild.structural_change(built, wanted, built_variables=None)`. **Stub: the argument is accepted, not read.** B
  reads *has an allowance* and *has a flat* on the built side from those globals and on the wanted side from the
  resolved figure, beside `has_shift`, and adds `drive` to `STRUCTURAL` (a missing key read as round).

**Every place a blank allowance on record is read, through `as_built`, and its owner** (§4.1.1's nine):

| # | Where | How | Owner |
|---|---|---|---|
| 1 | Reuse: `gearbox._Parts.find`, `_matches` | per candidate entry, the job through `as_built_job(job, entry.variables)`; a journaled entry (no variables) must not reuse a part F3 built at an allowance | B |
| 2 | Update: `update._part`, `_ignored_fields_as_built` | the built spec `as_built(from_dict(entry.spec), entry.variables)`, the job through `as_built_job` with the same variables | B |
| 3 | `swbuild.structural_change` | `built_variables` from the entry or the sidecar | B |
| 4 | Build again…, a row whose part is on record made new (ruling 1) | `as_built_job(job, old_entry.variables)`; only a row with no part takes the default | B |
| 5 | Print files: `printout.workbook_print`, `print_part`, `bore_figures` (§7) | plans through `classify` (2 and 3); the bore figures from the as-built spec | B |
| 6 | W9d's carry: `update._bore_mm`, `carry_for` (and `gearbox`'s `occupant`, `free_name`) | `_bore_mm` the hole as cut, Bore plus the as-built allowance; the jobs as-built | B |
| 7 | K11: `swbuild._blank_meaning`, `_wanted_words` | a blank allowance said as built (§9); the set-back the literal | B |
| 8 | K3: `ui_text._expression_words`, `_value_under` | a blank allowance said as built, never *type 0.2 in Gears!V2 again* (§9) | C |
| 9 | The strip: `gui._load_record`, the form's derive, `_update_target`, Update values | §5's contract | C |

B also owns `update._GLOBAL_COLUMN` (`"Bore Allowance"` → `bore_allowance`, `"Bore Flat"` → `flat`) and
`update._SPEC_COLUMNS` (*Bore allowance*, *Drive*, *Flat*).

## 7. Print files (package B's figures, package C's words)

- `printout.BoreFigures(bore: float = 0.0, allowance: float = 0.0, flat: Optional[float] = None)`, frozen: the part's
  hole as built, in mm.
- `printout.bore_figures(part: PrintPart) -> BoreFigures`: from `spec.as_built(part.spec, part.variables)`. **Stub: the
  bore as recorded, no allowance, no flat**, what every part built before F3 holds.
- The list's line (C's `ui_text._print_sizes` or its successor) **for a part with no allowance and a round bore is
  word for word today's** (*… · bore 10 mm · …*): the pins hold every fixture's part blocks. Words for the others are §9's.

## 8. The record (`store.py`, F3-0's)

- `_F1_LINK_SCHEMA = 11` beside `_W9D_LINK_SCHEMA`; `LINK_SCHEMA_VERSION = 12`, with the comment for schema 12.
- `BORE_SCHEMA = 4`, `SCHEMA_VERSION = 4`, `BORE_GLOBALS = ("Bore Allowance", "Bore Flat")`.
- `sidecar_schema(spec, variables=None)`: 4 when `variables` hold either global, whatever the spec; else 3, 2 or 1 as
  before. None (the default) asks the spec alone (the re-check's point 4), so its one-argument calls mean what they meant.
- `built_sidecar` and `updated_sidecar` pass the record's `variables`. The globals a caller passes are what the part holds
  after its build or Update: the strip and B pass the as-built job's.
- An F2-era app refuses a link 12 record and a sidecar 4 `.gear.json`, byte-identical (pinned in `test_store.py`).

## 9. The words (drafts; each package writes its own and may reword, saying so in its note)

**In the code at F3-0** (`spec.py`): *Bore allowance must be a number (got 'x').*, *Drive must be round or flat (got
'x').*, *Flat must be a number (got 'x').*

**A** (diagnostics, at the field named, the hole as cut with `R = (D + a) / 2`, `h = F − D/2 + a/2`):
- `flat`, `h < FLAT_LEAST_H · R`: *The flat is {h} mm from the axis, under a quarter of the hole's radius ({0.25R} mm);
  type a Flat of at least {Fmin} mm, or use a round bore.*
- `flat`, `D − F < FLAT_LEAST_DEPTH` (the re-check's point 5, **the shaft's own flat**): *Your shaft's flat is {D − F} mm
  deep (Bore {D} less Flat {F}), under the 0.3 mm a printed D needs to hold; type a Flat of at most {D − 0.3} mm, which
  leaves the flat a little play, or use a round bore.*
- `drive`, flat with no Bore: *Drive flat needs a Bore: type your shaft's diameter in Bore, or choose round.*
- `flat`, flat with no Flat (not in the plan's list; A's to keep or drop): *Drive flat needs a Flat: type your shaft's
  size across its flat.*
- `drive`, a bevel gear (G5): *A bevel gear's bore is the edge of its revolved blank and takes no flat: use a round bore,
  or a hub row.*
- each typed bore field of a ring or a sleeve (G9): *A ring has no bore to give an allowance or a flat.* / *A sleeve has
  no bore to give an allowance or a flat.*
- the bore checks on the hole as cut name both: *Bore of 8 mm with its 0.2 mm allowance (8.2 mm as cut) reaches the
  root diameter of …*

**B** (`swbuild`, `update`):
- structural, the strip (`structural_change`): *A bore allowance cannot be added to or taken out of a built part through
  its values; build it again as a new part.* Drive through `STRUCTURAL`'s own sentence.
- structural, the workbook (`update._structural`): *Drive changed from round to flat, which its values cannot carry;
  build it again as a new part.* and the allowance's as above.
- K11, a blank allowance: *Bore Allowance in Gear_m1.5_N25_P is 0.3 in SolidWorks and 0.2 (from its blank cell, the
  allowance as built) in the workbook: type 0.3 in Gears!V2, or set it back to 0.2 in SolidWorks, and press Update
  SolidWorks again.*

**C** (`ui_text`, README):
- K3, a blank allowance: was *0.2 (from its blank cell, the allowance as built)*, the way back *clear Gears!V2 again*.
- Explainers (kept out of `EXPLAINER_FIELDS`, as the span's card is, since the card pin iterates it):
  - *Bore allowance*: added to Bore when the hole is cut, on the diameter, so Bore stays your shaft's size. Blank: 0.2 mm
    for a printed gear not yet built (your printer's figure once the coupons give it), 0 machined, and for a gear
    already built the allowance it was built with, whichever its Process is now. **Clearing a typed allowance keeps the
    figure as built; to take the default, type it.** *Bore as cut* shows which. Negative for a press fit.
  - *Drive*: round for a round shaft; flat for a shaft with a flat, given in Flat.
  - *Flat*: your shaft's size across its flat, from the flat to the opposite round side; the hole's flat takes the same
    half allowance as its round.
- The Derived row: *Bore as cut* `8.2` (`8 + 0.2`), from the derived gear's `bore_as_cut`. **Not on a machined gear with no
  allowance and a round bore**, whose card the pin holds.
- The print list: *bore 8 mm* as today; *bore 8 mm + 0.2 mm allowance (8.2 mm as cut)*; with a D, *…, D-flat 7 mm*.
- README: the flat on +X facing a tooth space's middle, and that gears fixed to one D-shaft are phased by their flats in
  the machine and by their meshes in the assembly (ruling 2); the coupon instructions before and after F3 (M3); hole
  compensation kept 0.

## 10. The re-check's five points, where each landed

| Point | Where |
|---|---|
| a helical's and a herringbone's space centred at the section plane, not the Front plane; the mirror caveat | §3 |
| an empty `variables` in `as_built` | §2: "0", with what that asks of B's journaled match (§6, row 1) |
| `from_dict` skips `built_allowance` | §2, pinned |
| `sidecar_schema`'s `variables` defaults to None | §8, pinned |
| the depth refusal says it is the shaft's own flat, D − F | §9, A's sentence |

## 11. Who owns which file

- **F3-0 (done):** `docs/notes-printed/F3-INTERFACES.md`, `F3-0.md`; `src/gear_generator/spec.py` and `store.py`; the names'
  lines in `gears/spur.py` and `bevel.py`; `workbook/schema.py`'s `DRIVE_WORDS` and three columns; `workbook/model.py`'s
  three fields and `spec_values`; `gui.py`'s two tuples; the stubs in `workbook/gearbox.py`, `swbuild.py` and
  `printout.py`; `probe/f1_demonstration.py`'s link schema (§12); tests `test_printed_rule.py` and
  `fixtures/printed/F2_built.json`, `test_workbook_model.py`, `test_gui_spec.py`, and the moved lines of §12.
- **A:** `gears/spur.py`, `helical.py`, `bevel.py`, `internal.py`, `clutch.py`; tests `test_gears_spur.py`, `_helical`,
  `_bevel`, `_internal`, `_clutch` and a new `tests/test_bore.py`.
- **B:** `workbook/gearbox.py`, `workbook/update.py`, `swbuild.py`, `printout.py`; a new `tests/test_bore_workbook.py`.
  If B finds `workbook/model.py`'s reading must change for the three columns, that is B's and said in its note.
- **C:** `gui.py`, `ui_text.py`, `design/`, `design/UI-DESIGN.md`, `README.md`; tests `test_ui_text.py` and a new
  `tests/test_bore_form.py`.
- **Nobody** edits `spec.py`, `store.py`, `tests/test_printed_rule.py`, its fixture, `tests/test_findings.py` or the four
  guard tests of §1 to make them pass: what fails there is the threading's to put right. A name of §2 to §8 a package
  must change goes to the coordinator first.

## 12. The pinned lines F3-0 moved

**§4.3's table, every line** (each pins the current schema, one past it refused, or a printed part at the schema its
contents need; F3 moves the current schema by one and adds one content case, and each test holds what it held):

- `test_store.py` :227 and :1123 (11 → 12), :833 (the literal "newer" 12 → 13), :1419-1426 (a raw 13 refused, *reads
  12*), :1600-1610 (parametrized: no bore global, 3, refused by W9's reader; with `"Bore Allowance"`, 4, refused by
  F2's, byte-identical);
- `test_workbook_bands.py` :354, :368, :378; `test_workbook_carry.py` :52, :76, :80, :96, :1119;
  `test_workbook_user_record.py` :56, :85-91; `test_workbook_window.py` :312; `test_printed_workbook.py` :367, :379, :394,
  :440, :526 (:530, sidecar 3 for parts built before F3 with Printed typed, does not move);
- `test_printed_rule.py` :456 to :458 (renamed `…_link_schema_12_and_a_printed_part_at_sidecar_schema_3_or_4_by_its_globals`:
  `(12, 11, 10)`, `(4, 4, 3, 2, 1)`, and the sidecar cases from the globals) and :550 (12).

**Named by §4.6 item 4 and 5:** `test_workbook_model.py:19-23` (the three titles after End band); `test_gui_spec.py:49-52`
(the union gains `GEAR_RECORD_ONLY`, and the test now also asserts it is `{"built_allowance"}` and disjoint).

**Beyond the plan, found by the suite run**, each a column's position moved by the three columns inserted before it,
each asserting the same thing of the same column:
- `test_workbook_model.py:157-159`: Teeth moved to the far right is now column AA, the 27th (was X);
- `test_workbook_bands.py:42`: the column after End band is now Bore allowance, then Drive, Flat and Part name (was Part
  name), so the bands still follow Slides and still come before Part name;
- `test_workbook_build.py:78`, `:82`, `:776`: Part name's cell is Y (was V);
- `test_workbook_export.py:97`, `:160`: a header added after the last column lands at Z1 (was W1);
- `test_workbook_window.py:1629`: the save that changes the workbook writes Notes, now Z2 (was W2, which is now Drive and
  read as a bad Drive word).

**Added, not moved:** `RECORDED` gains the ungrooved herringbone and the dog with their hashes, taken at `08db5ba`.

**A probe script's literal** (as F1 treated W9d's in `e0a8d62`): `probe/f1_demonstration.py`'s `LINK_SCHEMA = 11` held two
meanings. *A master built before F1 is below F1's 11* stays a literal, `F1_LINK_SCHEMA`, and its self-check holds it to
`store._F1_LINK_SCHEMA`; *the record a run writes* is held to `store.LINK_SCHEMA_VERSION`, in the run's check and the
self-check's alike, with a comment. Self-check 0 failed. Its printed sidecar judgement (3) is left: a rerun on
SolidWorks after A would meet 4 for a printed part with a bore (F3-0.md, decision 13).
