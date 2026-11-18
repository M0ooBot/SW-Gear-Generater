# Gear Generator — gears made to be 3D printed in PLA

**Drafted on 2026-11-16 and revised the same day to its first review (`docs/PLAN-PRINTED-REVIEW.md`) and to the
user's answers; revised on 2026-11-18 against the code as W9 leaves it, read at `c2d95cc` on branch `w9d`
(`51870ca`); and revised again the same day to its second review (the last section of
`docs/PLAN-PRINTED-REVIEW.md`, `158b06f`, which read the code at `51870ca`, the same as `c2d95cc` in `src`); and once more to its third check (`d2e34a6`)
and the coordinating session's ruling on the ring pair check.**

**Where it stands (2026-11-18, evening; read at `f28cb75` on `printed`).**

- **W9 is closed** and merged into `printed` (`138d646`).
- **F1 is closed:** built, reviewed, shown on SolidWorks 2026 and confirmed on 2024 (`5e2f386`, runs reviewed in
  `0e7000d`). Its notes are in `docs/notes-printed/F1-*.md`.
- **F2 is closed short of §3.2, the user's own step:** built, reviewed, its STEP probe run on both versions and its
  findings set (`ae42722`). Its demonstration ran clean on SolidWorks 2026 34.1.1 and 2024 32.5.0 (`9c1275f`),
  and the runs were reviewed (`70a2c42`, no must-fix). The herringbone was then lifted from the size check's
  skipped kinds (`550a8a9`).
  - **What F2 leaves open:**
    - §3.2: the coupons built, printed and measured; Bambu Studio opening the files (U5); and from the numbers, D3's
      printed backlash and F3's bore allowance, on the user's word (U4);
    - standing caveats, none blocking (`F2-DEMONSTRATION-RUNS-REVIEW.md` §5).
  - **Nothing of the printed work is merged into `workbook`.** It lives on `printed`.
- **F3 is made ready in §4.6**, to be reviewed before its interface step.
- **F4 does not wait on the user** (pure maths; the same review, §5).

D11 is ruled (B) by the coordinating session, the user's to overrule. D3, D6 and D7 stand as assumed.

The plan is executed like `docs/PLAN.md`: its "For the executing agent" section applies, and so do the rules in
`docs/HANDOFF-WORKBOOK.md` (*Rules carried over*). Where the two differ, the handoff's rules win: commits carry no
attribution line, the full build comes first, and SolidWorks 2024 confirms at the stage's end.

The stages are **F1 to F4** (F for filament). W9's own probes are already called P0, P1 and P2. **Every file and line
cited below is as of `c2d95cc`** unless the text gives another commit.


## Context

The gears the app builds are correct textbook gears, drawn for SolidWorks. The user now wants to print them: FDM,
ordinary PLA. The code was read against that use on 2026-11-16 and again on 2026-11-18 at `c2d95cc`. W9 changed
none of the following:

- **The geometry is right** (true involute, 0.38 × module root fillet, profile shift, undercut and
  thin-tip warnings), and nothing in it knows about a nozzle, a printer's error or plastic.
- **Backlash is `0.3 × "Module"` per gear** (`spur.BACKLASH_FACTOR`, `gears/spur.py:86`). A printer's error is
  a fixed size, not a share of the module: at module 3 the pair has 1.8 mm of play.
- **The thin-tip warning is at 0.3 × module** (`spur.TIP_THICKNESS_WARNING`, `spur.py:91`, said at
  `spur.py:885-888`). So a module 1 tooth whose tip is 0.37 mm, narrower than one line from a 0.4 mm nozzle,
  passes without a word.
- **Undercut is warned about and not drawn** (`spur.py:870-880`). A hob would remove that material; a printer
  prints the flank as drawn. Unshifted at 20°, a 13-tooth pinion clears an outside mate of up to 16 teeth, 14 up to
  26, 15 up to 45, 16 up to 101. No pair with a gear of 12 teeth or fewer clears both ways: 12 clears a mate of up to
  10 teeth, 11 up to 7, 10 up to 4, and none of those mates clears it back. That is the condition for a *generated* gear.
  The app draws a radial flank below the base circle instead, and §2.3 finds the drawn parts clear where this
  condition reports a clash.
- **No feature a printed gear wants:** the bore is a plain hole at its nominal size, no drive flat, no
  file a slicer reads. W9b's hub is built "with the row's Bore", its fixing to the shaft left to the user.
- **No strength check.** The workbook works out each shaft's torque and compares it with nothing.

What was read online the same day (maker and vendor guides and one series of bench tests; peer-reviewed
data on printed gears is thin, and the guides differ on backlash by about four times) is under *Sources*.
The reviewer did not fetch them. What they agree on: module 1.5 to 2 for a 0.4 mm nozzle and 1 for light
duty; 20° pressure angle, 25° for a stronger root; a root fillet of 0.3 to 0.5 × module; herringbone
where possible; a flank clearance built into the tooth, 0.1 to 0.2 mm per flank in the most careful of
them; a 0.5 mm chamfer or the slicer's compensation for the first layer; a D-flat, key or insert rather
than a press fit, since PLA creeps; five walls or more.

### The rule this plan keeps

**A gear marked `Machined` builds exactly what every gear builds today, is told exactly what it is told today, and
is recorded exactly as it is recorded today.** That means the same globals, steps, file name, warnings and Solve
rows, and the same bytes in its `.gear.json` and in its entry in a gearbox's record. Every new check, default and
feature below is for printed gears only. §2.7 says how that is proved.

**Printed is the default everywhere the user chooses** (the user, 2026-11-16: *"workbook also go 3d printed, just
make everything go 3d printed default"*). The user chooses in two places: the form's Process row and the Box
sheet's Process setting. On a gearbox built before F1, a blank Box setting means *as built*, which is Machined (D11). A gear the code builds without saying which is machined. That covers a record written
before F1, a test, a probe script and a design board, and it is what keeps the rule with no edit to any of them
(§1). What the default carries with it is also in §1.


## Decisions wanted

Each row has the answer this plan assumes; say where it is wrong.

| | Question | Assumed |
|---|---|---|
| D1 | How is a gear marked? | **Answered 2026-11-16.** A **Process** row on the form, `Printed` or `Machined` (one row for a pair), and a `Process` setting on the workbook's Box sheet for the whole gearbox. The Box setting is a word, checked as it is read (§1). |
| D2 | What is the default? | **Answered 2026-11-16: `Printed`, everywhere, the workbook too.** A blank Process row or Box setting is Printed. Three things read as Machined: the record of a part built before F1, which has no Process; a gearbox built before F1 whose Process is blank (D11); and a spec the code builds without saying (§1). |
| D3 | Printed backlash when the cell is blank | **The smaller of 0.3 mm and 0.3 × module**, per gear: 0.3 mm from module 1 up (0.14 mm off each flank, measured square to it), and today's value below module 1. Never more than today's, so nothing that builds today is refused. To be replaced by the user's own measurement (§3.2). F1 can go ahead on it (§2.8). |
| D4 | Which shaft drive first? | **Answered 2026-11-16: D-flat.** Hex and a keyway are the same kind of sketch and can follow; a boss with a setscrew or a heat-set insert is not in this plan. |
| D5 | The file for the slicer, and which slicer | **Answered 2026-11-16: the user's slicer is Bambu Studio, so STEP.** Bambu Studio is said to open STEP; F2's own step, the user opening an exported gear there, is what shows it. No STL export. |
| D6 | Undercut | **Warn on the single gear, and build no pair check in F1** (§2.3, the coordinating session's ruling of 2026-11-18, the user's to overrule). The radial test planned before reports overlaps the drawn parts do not have; a sweep of the drawn outlines is later work (§7). Drawing the true undercut root is another sketch topology and not in this plan. F1 can go ahead on it (§2.8). |
| D7 | PLA's allowable tooth stress | **Provisional: 17 MPa**, a third of the roughly 50 MPa a PLA datasheet gives, against a stress that includes the fillet's concentration (§5). No standard gives a figure for printed PLA, so this is the writer's judgement, typed on the Box sheet and replaced by the user's own tests. F4's only; F1 does not touch it. |
| D8 | Where this sits beside W9 | **Answered 2026-11-16: W9 first; on 2026-11-18 the user said to carry on past W9.** This plan starts once W9 is merged into `workbook`, on a branch `printed` cut from it. What it takes on from W9 is in §6. |
| D9 | The edge chamfer against first-layer squish | **Answered 2026-11-16: left to the slicer for now.** Not built in F1 to F4; the export's print list asks for the slicer's first-layer compensation. The review found the chamfer is the costliest piece here (§4.3). It gets a plan of its own only if the test prints show the slicer's setting is not enough. |
| D10 | A printed part's file name | **Answered 2026-11-16: ends `_P`** (`Gear_m1.5_N25_P`), as a shifted gear ends `_x0.09`. It is a different part from the machined gear of the same sizes, and without the mark the second of the two would be refused as existing. Machined names stay as they are. As W9b ruled for a sleeve's bands (`W9B-INTERFACES.md` §7), the mark is the default name only. An Update that makes a built machined part printed keeps its file and name, since a default stem that drifts with the values is a value change (`gearbox.name_changed`, `workbook/gearbox.py:405-415`). So only a part *built* printed carries `_P`. |
| D11 | A gearbox already built, opened after F1 | **Ruled (B) by the coordinating session, 2026-11-18; the user's to overrule, and put to them when they wake.** A gearbox built before F1 opens exactly as it does today. Nothing reads as changed and nothing is written until the user types Printed for it. A blank Process means *as built*: Machined while the record's current parts were all built machined, Printed otherwise. The rule goes by the record's parts, not its schema number (§1). Why (B): it writes nothing into a gearbox the user already has; it keeps D2's *the record of a part already built reads as Machined* for a gearbox as for a part, as the strip already does; and issue #1 was the user's fear of the app overwriting their work. (A), reading Printed and changed, is kept in §1 with its one switch. |


## 1. What `Printed` means

### 1.1 The spec, and the record

Two new fields on `GearSpec` (`spec.py:134-159`), after the bands:

- `process`: `printed` or `machined` (`spec.PROCESS_PRINTED`, `spec.PROCESS_MACHINED`).
  - A reader, `GearSpec.process_value()`, checks the word as `teeth_side_value` checks Side (`spec.py:223-227`).
    `is_printed()` answers it and never raises: anything but `printed` in any case is not printed.
  - **The dataclass default is `machined`, and so is a blank.** That is what a spec written before F1, or built in
    code without saying, means. The user never meets this default. The form's Process row starts at Printed, and a
    Box's Process resolves as §1.3 says. Both write the word into every spec they make.
- `nozzle`: the line width in mm, `0.4` when blank. It is used by checks only and changes no plan, so the as-built
  comparison already sets it aside (`update._ignored_fields_as_built`, `workbook/update.py:244-266`, ignores any
  field whose built value leaves the wanted plan as it is).

**`GearSpec.to_dict` (`spec.py:161-167`) leaves out `process` and `nozzle` for any spec that is not printed**:
blank, `machined` in any case, or a word that does not read, and with a typed nozzle too. It never raises. W9b made
it leave out a sleeve's blank bands in the same way. So a machined part's `spec` in its `.gear.json` and in its
record entry is byte for byte what W9 writes.

`GearSpec.from_dict` (`spec.py:169-172`) then needs no change: a missing key takes the dataclass default,
machined, which is what a part built before F1 is. One consequence is harmless but said here: a machined spec with
a typed Nozzle does not round-trip its nozzle. Nothing compares `GearSpec`s with `==`; the one comparison of
two forms, `update.py:2151`, compares their `to_dict`s, which agree.

**The derived gear carries the nozzle too, and stays out of the record when machined.** The checks of §2.2 run on
the derived gear, and `spur.section_diagnostics(g, recipe)` (`spur.py:822`, called at `:731-732` and from
`helical.py:364-365` and `bevel.py:579`), the ring's `internal.section_diagnostics` (`internal.py:522`, called at
`:891`, `:968` and `bevel.py:577`) and `pair.mesh_warnings(g1, g2)` (`pair.py:989`) see no spec. So:

- the three section classes, `SpurDerived` (`spur.py:149`), `InternalDerived` (`internal.py:157`) and the
  bevel's `RackSection` (`bevel.py:209`), each gain **one field, `nozzle: Optional[float] = None`**: None when
  the spec is not printed, the line width in mm when it is. It is set by each derive through the section's
  constructors (`spur.profile`, `internal.section`, and the bevel's three `RackSection`s at `bevel.py:461-477`);
- `printed` and `backlash_printed` (blank backlash on a printed gear) are **properties**, not fields, so
  `asdict` never sees them;
- `HelicalDerived` (`helical.py:146`) and `BevelDerived` (`bevel.py:262`) reach all three through their
  `section`, as they reach `backlash_typed` today;
- each of the four `to_dict`s that write a derived gear into a record, `spur.py:255`, `internal.py:260`,
  `helical.py:252-255` (the section's `asdict` merged with its own) and `bevel.py:388-395` (the section nested),
  leaves `nozzle` out while it is None.

`GearRecord.derived` is that `to_dict`, written into every part's `.gear.json` (`gui.py:1698`,
`workbook/gearbox.py:1383`, `:1409`, `workbook/update.py:2474`, through `store.py:374` and `:392`). With the
field left out when None, a machined part's `derived` is byte for byte W9's as well, and §2.7's pin on the whole
`.gear.json` holds at every commit of F1. The first revision put a `backlash_printed` *field* on `SpurDerived`
alone. That would have written `"backlash_printed": false` into every machined record and failed its own pin.

Some comparisons read raw spec dicts instead of `GearSpec`s. Each takes `machined` for a missing `process`, as
each already takes `external` for a missing `teeth_side`:

- `swbuild.structural_change` (`swbuild.py:1291-1358`) and `update._structural` (`update.py:276-287`):
  `process` is not structural in F1, so nothing changes there until F3's Drive;
- W9d's `update._changed_columns` (`update.py:3210-3219`), which gains Process (§6);
- `gui._update_target` (`gui.py:1496-1515`), through `structural_change` and the variables it counts.

Four functions read through `from_dict` and need nothing: `gearbox.same_part` and `_matches`
(`gearbox.py:418-449`), `update._part` (`update.py:294-337`) and `gui._load_record` (`gui.py:1460-1487`). The
first revision's one record reader is not needed. `from_dict` has six callers (`update.py:304` and `:1680`,
`swbuild.py:1374`, `gearbox.py:444`, `spec.py:376`, `gui.py:1470`), and every one already reads a missing key
as machined.

### 1.2 The schemas

- **The link record goes to schema 11, whatever its parts' process** (`store.LINK_SCHEMA_VERSION`,
  `store.py:421-426`, with `_W9D_LINK_SCHEMA = 10` kept beside it as each stage's number is), as W9b's 8 was.
  - Any write moves it to 11: Build, Update, Apply fix and Export (`_record_own_write`,
    `workbook_gui.py:1195-1215`). After that a W9-era app waits on the gearbox, even an all-machined one. That is
    the cost every W9 stage's bump had.
  - The literal `10` is pinned at **ten lines in five test files** (`git grep` at `ffe8812`, again at `d2e34a6`):
    - `test_store.py:227` and `:1123`;
    - `test_workbook_bands.py:353` and `:367`;
    - `test_workbook_carry.py:51`, `:75`, `:79` and `:1057`;
    - `test_workbook_user_record.py:56`;
    - `test_workbook_window.py:312`.
  - All of them move in F1-0 (§2.8). **F1-0 does not work from this list**: it moves every literal 10 that
    `git grep` finds at the commit `printed` is cut from, since the W9 work still landing may add more.
  - Outside the suite, `probe/w9d_demonstration.py:1007` checks a written record's schema is 10. That is W9d's
    demonstration script and is left alone; it runs from W9's own commit, and a rerun with an app at or after F1
    would read 11 there.
- **The `.gear.json` goes to sidecar schema 3 for a printed part** (`PRINTED_SCHEMA`). `store.sidecar_schema`
  (`store.py:88-92`) gives 3 for a printed part, else 2 for a banded part or 1 as now, and `store.SCHEMA_VERSION`
  (`store.py:35`) becomes 3. A machined part stays at 1 or 2.

**An older app with a newer schema, read and tested.** The first revision made a STOP of this; it is now answered.

- For a link record, `store` raises `UnknownSchema` (`store.py:1461-1464`), leaves the file byte-identical,
  and `save_link_record` refuses with "Build and Update SolidWorks wait" (`test_store.py:310-321`, `:833-848`).
- For a `.gear.json`, `load` re-raises `UnknownSchema` without moving the file (`store.py:212-218`,
  `:247-248`), and the planning read `read_sidecar` returns None and writes nothing (`store.py:1808-1822`).
- So a W9-era app never writes a printed part's backlash back.
- A W9-era app reading an F1 *workbook* that has no record skips the Box's Process and Nozzle rows, as it skips any
  label it does not know (`model._read_box`, `workbook/model.py:348-350`), and builds it machined. That is the
  same acceptable failure W9b accepted for a banded sleeve read by an older app.

### 1.3 Where the user chooses

**The form.** A **Process** row (`Printed` · `Machined`) goes in the Gear panel under Make, one row for both gears
of a pair. **Nozzle** (mm, placeholder *0.4*) goes under it, shown while Process is Printed.

- Both are fields the two gears share, like Kind and Flank. `gui.GEAR_COMPOUND` (`gui.py:83`) gains `process`
  and `nozzle`, and `_gear_spec` (`gui.py:1110-1133`) puts them into each gear as it puts Kind and Flank.
- `pair.apply` writes through `with_values` and leaves the rest of each gear as the form gave it (`pair.py:860-880`),
  so a Solve keeps the form's Process. `solve_spec` (`pair.py:769`) reads it for Solve's printed ranking; both
  callers (`ui_text.py:636`, `gui.py:1387`) go through it.
- `tests/test_gui_spec.py:49-52` keeps holding the form's fields to `fields(GearSpec)`.
- The row starts at Printed. It is not taken from `GearSpec()`, as the other fields are (`gui.py:154-164`).
- `_load_record` sets the row from the record, so a `.gear.json` from before F1 opens as Machined. **A new part
  built from that form afterwards is machined too**, unless the user changes the row, which shows it.

**The developer's command line**, `python -m gear_generator.gears` (`gears/__main__.py:35-52`, `README.md:606`),
gains a `process` key like its others. Blank, it is machined, as in code; the README says so.

**The workbook.** Two Box settings go into `schema.BOX_SETTINGS` (`workbook/schema.py:102-112`), after Efficiency
and before Units:

- **Process**: a word. Its note says *Printed or Machined; blank: Printed for a new gearbox, as built for one
  already built*.
- **Nozzle**: mm, numeric, blank 0.4.

The Box sheet has no drop-down lists (`to_sheets` gives lists to table columns only, `model.py:612-618`), so the
word is checked as it is read. Anything but Printed or Machined, in any case, is an error at its cell: *Process is
Printed or Machined (got 'x').* `schema.Setting` (`schema.py:88-99`) has no field for a word list today and
gains `words`.

`model.Box` (`model.py:27-41`) gains `process` and `nozzle`. Their dataclass defaults are `machined` and
`""`, as in code everywhere. `_read_box` (`model.py:337-376`) keeps a blank or missing Process as `""`, the
user's blank; it does not resolve it. The rest of the Box:

- `to_sheets` (`model.py:598-610`) writes the word as held, so a gearbox built in code and written out reads back
  machined;
- `template` (`model.py:638-640`, behind *New workbook…*) writes Printed and 0.4;
- `Gear.spec_values` (`model.py:115-137`) fills each gear's `process` from the Box's resolved word, and
  `tests/test_workbook_model.py:389-390` keeps holding it to `fields(GearSpec)`.

**What a blank Process means (D11, ruled (B)), in one function.** `assess.blank_process(record) -> str` in
`workbook/assess.py` is the switch. It answers `machined` when the record lists current parts
(`LinkRecord.current_parts`, `store.py:1015`) and none of them was built printed (no part entry's `spec` holds
`"process": "printed"`). Otherwise, with no record, no parts, or any part built printed, it answers `printed`.

- `assess.assess` (`assess.py:148`) gains a keyword `blank_process`, `printed` by default. When the Box's Process
  is `""`, it puts that word into the Box of **both** the assessment's `read` and its `spec`, so no `Assessment`
  holds a blank Process. A blank left in `read` would become `GearSpec`'s machined default, without a word, in
  anything that later builds a spec from `a.read.box`.
- The window resolves inside `WorkbookWindow._assess` (`workbook_gui.py:825-830`), its one pipeline. That way both
  of its callers get the same answer: `_plan` (`:699-706`), and the raw assessment at `:692` that feeds
  `wb_link.consequence`.
  - `_assess` reads the record itself, without moving anything, as `_plan_solidworks_pass` does (`:717`), and
    passes `assess.blank_process(record)`.
  - When the record beside the workbook is another workbook's, a copy not yet settled (`store.foreign_workbook`,
    `store.py:1683`), it passes no record. Otherwise a copied workbook would read Machined from its original's
    parts.
- The rule goes by what the record's parts were built as, not by the record's schema number. Any F1 write moves the
  record to 11 (§1.2), so a rule on the number would flip a machined gearbox to Printed after its first Export or
  Apply fix.
- An F1-built machined part also has no `process` key (§1.1), so a gearbox the user built Machined after F1 and
  then left blank also stays Machined, as built.
- A probe script or test that calls `assess` on a gearbox built in code has `machined` in its Box and never meets
  the keyword.

**What (B) means for a gearbox built before F1.** It opens exactly as it does today: nothing reads as changed, the
footer says nothing new, and Update and Build again… have nothing to do. The Workbook panel's Process line says
*Machined, as built*, with how to change it (§6, open point 3). When the user types Printed beside Process on its
Box sheet, every part reads as changed in its Backlash alone, and Update SolidWorks carries it in place under W9a's
rules (§6). New gearboxes and *New workbook…* are Printed.

**What (A) would have done, and its switch.** Under (A), a blank Process is Printed whatever was built. A gearbox
built before F1 then opens with every gear *changed since it was built*, only because of Process. To keep it as
built, the user adds a row labelled Process with Machined beside it, since a workbook written before F1 has no such
row and has Units in B9.

**The one switch is the body of `assess.blank_process`**: under (A) it returns `printed` always. Under (A), three
sentences come back as additions, not changes:

- the footer's sentence when every change is Process's (C, `ui_text.workbook_footer`, `ui_text.py:2495`);
- a third `made_new` reason in `gearbox.py` beside `UNSAVED` and `MISMATCHED` (B);
- its way back in `ui_text._reuse_advice` (`ui_text.py:5440-5463`, C).

Each of the three names the Box's Process cell only when the row exists (`_read_box`'s `at(key)` already
returns "Box" when it does not), and otherwise says to add a row labelled Process. F1-0's interface note keeps all
three sentences' words, so a later (A) is the switch and three small additions.

**Other things the default carries:**

- **An old `.gear.json` opens as Machined**, since that is what was built. Changing its row to Printed is a change
  of one global's text, which Update values carries.
- **Typing Printed on a built gearbox** changes, in each gear, dog, sleeve and hub part whose Backlash cell is
  blank, one global: `"Backlash"` goes from `0.3 * "Module"` to §2.1's equation.
  - At module 1.25 its value goes from 0.375 to 0.3 mm: **the printed tooth is thicker** by 0.075 mm at the pitch
    circle (about 0.035 mm on each flank, square to it), and the pair's play falls from 0.75 to 0.6 mm. Printed is
    tighter than machined at every module above 1.
  - At module 1 and below the value is equal, but the text differs, so the part is still written.
  - A typed Backlash is not written.
  - The record moves to 11 and each changed part's `.gear.json` to sidecar 3 (`updated_sidecar`,
    `store.py:386-399`).
- **No `Process` custom property.** Update writes globals and never properties, so a property would go stale the
  first time Update changed a part's process. The record and the file name carry it.
- **Sleeves, dogs and hubs** pass `process` through to the spur and ring kinds they are built from, and take the
  printed backlash as those do. `clutch._Clutch._as_spur` (`gears/clutch.py:109-112`) replaces kind, side, helix
  and shift and keeps the rest. A sleeve on its dog or hub is a coupling, not a Meshes row. Its play is the two
  backlashes: 0.6 mm at the pitch circle when printed above module 1, against 0.6 × module machined.

## 2. Stage F1 — defaults and checks (no new SolidWorks call)

**Closed 2026-11-18.** Shown on SolidWorks 2026 and confirmed on 2024 (`5e2f386`; `F1-DEMONSTRATION-RUNS-REVIEW.md`,
`0e7000d`). The span over k teeth moved to F2.

### 2.1 Backlash

Blank backlash on a printed gear is `IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )`. It has the shape of the depth
IIF the app already writes (`spur.py:771`), and IIF was probed in P1 (`src/gear_generator/probe/p1_equations.py:109`), so no kind
of equation is new.

- It is written by all five variable writers, when the spec is printed and its Backlash blank, (`spur.py:743`, `helical.py:371`, `internal.py:895` and `:973`,
  `bevel.py:640`) and the four `derive`s (`spur.py:714`, `helical.py:333`, `internal.py:878`, `bevel.py:452`),
  from one pair of constants beside `BACKLASH_FACTOR` (`spur.py:86`).
- The card shows it as a default, *0.3 mm · printed default*: a third state beside typed and `0.3 × module`.
  `ui_text` reads the derived gear's `backlash_printed` property (§1.1) where it now reads `backlash_typed`
  (`ui_text.py:128` through `g.section`, `:167`, `:517-523`), whichever of the five derived classes it is given.
- K11's sentence says the printed default in words (§6).

On the involute this is an exact allowance for walls printed evenly fat. Turning an involute about its centre moves
it square to itself by the same distance everywhere, `(j / 2) cos α`. **It is not one anywhere else.** The tip and
root circles do not move, and the radial line and fillet under the base circle are turned, not offset; §2.2's
clearance check is what watches those.

On a bevel gear the allowance shrinks toward the small end with the tooth: at the toe of a 20 / 40 pair at module
1.5 and face 10 it is 0.70 of the heel's. So **a bevel gear's toe governs**: the card gives the toe's figure, and
§2.2's tip check is made there.

A slicer's own horizontal compensation adds to this. The card and the print list say to use one or the other.

### 2.2 Checks for printed gears (warnings)

The checks reach the process and the nozzle in two ways.

- **Each kind's `validate(spec, derived)`** sees the spec, and its signature does not change.
- **The functions that see only a derived gear** read its `nozzle` field and `printed` property (§1.1):
  `spur.section_diagnostics`, the ring's `internal.section_diagnostics` and `pair.mesh_warnings`. None of their
  signatures changes either. The first revision's "no signature changes" was true only because of this; it now
  says how.

The checks:

- **Tip:** the tip thickness after backlash under one nozzle width, measured at the toe on a bevel gear. It is said
  in `spur.section_diagnostics` (`spur.py:822-898`) beside today's thin-tip warning (`:885-888`), and in the
  ring's `internal.section_diagnostics` (`internal.py:522`) beside its own thin tip (its
  `TIP_THICKNESS_WARNING`, `internal.py:132`).
  - With the default backlash and a 0.4 mm nozzle (by `spur.profile`, recomputed by the second review), **module 1
    warns below 26 teeth only**: 0.271 mm at 12, 0.365 at 20, 0.396 at 25, 0.401 at 26 and 0.446 at 40.
  - **Module 1.25 passes from 11 teeth** (0.402 mm; 0.375 at 10).
  - Module 1.5 passes from 8 teeth (0.437 mm; 0.581 at 12, 0.712 at 20); a 6- or 7-tooth pinion (0.305, 0.379)
    warns.
- **Module:** under 2.5 × nozzle (1.0 at 0.4 mm). This is the guides' floor, below which a profile rounds off.
- **Radial clearance, per pair:** the clearance at the working centre distance under 0.3 mm, less a rounding
  tolerance (at module 0.75 it computes as 0.2999999999999998). Two printed surfaces take about that.
  - `pair.tip_clearance` (`pair.py:190-204`) covers outside pairs, and Gleason's figure covers a bevel pair.
  - A ring pair's clearance is new pure code beside `tip_clearance`: the pinion's tip to the ring's root and the
    ring's tip to the pinion's root, each the depth less two modules (h − 2m) unshifted: 0.4 × module up to module
    1.25 and 0.25 × module above, as the depth IIF gives. `internal.tip_clash` (`internal.py:381`) is the
    tip clash, not this.
  - On the form the check is said through `pair.mesh_warnings` (`pair.py:989-1009`, shown at `gui.py:1300`). In
    a workbook it is said at each Meshes row from `checks._check_mesh` (`workbook/checks.py:378`).
  - Unshifted spur and helical pairs pass from module 0.75. **Bevel pairs warn under module 1.6** (Gleason's
    clearance is 0.188 × module, under 0.3 mm below module 1.596), and shifted pairs warn wherever the shifts have
    eaten the clearance.
  - The depth is left alone; the sentence says to use a larger module or less shift.
- **Rim:** the wall between the bore and the root under three nozzle widths. This is a printability floor only.
  Today's one-module warning (`spur.py:881-884`) is the stricter above module 1.2 and stays.
- **Helix:** a helix angle over 45°, a flank that prints as an overhang. It is conservative by a few degrees, since
  the flank's own angle is the base helix angle (41.6° at 45°).
- **Ring fillet:** a ring's 0.15 × module default fillet (`internal.FILLET_FACTOR`, `internal.py:128`) is under
  the 0.3 × module the guides ask. One sentence says so and why it is small (the pinion's tips). The default does not
  change.
- **A sleeve's relief** (W9b) clears a dog's tip by 0.5 × module a side (Ø m(z + 3), `W9B-INTERFACES.md` §4). That
  is under 0.3 mm below module 0.6, where the module check already warns. Nothing more is added.

### 2.3 Undercut and interference (no pair check in F1)

**The single gear.** The undercut warning (`spur.py:877-880`) says today that *a generated gear would lose the
bottom of its flanks, which this profile does not show*. On a printed gear that is not what happens: nothing
generates it, and the flank is made as drawn, a radial line and a fillet below the base circle. So a printed gear's
warning gains one sentence in place of the cure's lead-in: *Printed, the gear is made as drawn, with no undercut;
whether a mate's tip clears its flank below the base circle is not checked here, so turn the pair in SolidWorks.*
The shift it already names stays. A machined gear's sentence is unchanged.

**No pair interference warning is built in F1** (the coordinating session's ruling, 2026-11-18, the user's to
overrule). This applies to ring pairs, outside pairs and bevel pairs alike. The first two revisions planned a
check by the radial measure: whether one gear's tip circle reaches past the other's base-circle tangent point,
`√(rb₂² + (C sin αw)²)` against `ra₂`. That measure is the generated-gear condition (KHK's), and it does not
describe the parts the app draws.

*Ring pairs.* The third review swept the app's own drawn outlines (`kind.outline`, recipe A) through three pitches,
at the app's phases, with depth measured normal to the boundary. This was pure Python, not run on SolidWorks:

- Where the radial measure reports 0.11 to 0.56 mm of reach (a 12- to 20-tooth pinion in a 54-tooth ring at modules
  1 and 2; RangeBox's 13 in 55 at module 1.25, 0.401 mm), the drawn parts overlap by at most 0.026 mm with no
  backlash.
- With the printed default they do not overlap at all, and every ring case clears once each gear has 0.04 mm of
  backlash.
- So the second revision's fact that "a pinion of 17 teeth or fewer clears no ring" is true of the radial measure
  and not of the drawn parts. A warning built on it would be said on nearly every printed planetary about an
  overlap the parts do not have. The half-nozzle margin that revision proposed is withdrawn with it.

*Outside pairs, the same test applied.* The same sweep ran five outside pairs: 6 / 30, 8 / 40, 10 / 40, 12 / 60 and
13 / 80, at modules 1 and 1.5. Below its base circle the pinion's flank is drawn, a radial line and a fillet, not
undercut, and the mate's tip reaches 1 module past its pitch line where a hob reaches 1.25.

- The radial measure reports 0.24 to 0.62 mm of reach for those pairs.
- The drawn flanks overlap by 0.005 to 0.067 mm with no backlash, and by nothing with the printed default.
- The worst, 6 / 30, clears from about 0.08 mm of backlash, against the printed default's 0.3 mm per gear.

So for outside pairs too, the radial measure states an overlap the drawn parts do not have, at the printed default.
These figures are the third review's sweep, read and not rerun for this revision. They are an inference from the
app's outlines, not a measurement. Not modelled: helical, shifted and bevel pairs, recipe B, and a printed tip's
radial growth. **So no outside-pair warning is kept either**: none is true of the parts as drawn at the printed
default in any case the sweep covered. The cases it did not cover are not checked by F1 at all, rather than checked
by a measure shown to overstate.

**A typed small backlash is not guarded.** The overlap the sweep found appears below about 0.04 mm of backlash a
gear for a ring pair, and below about 0.08 mm for a pair like 6 / 30. A user who types a backlash under those values
gets parts that, as drawn, can overlap by up to about 0.03 mm (rings) or 0.07 mm (6 / 30), with no warning, and a
printer's fat walls add to that. The single gear's *turn the pair in SolidWorks* is then the only guard.

**W7's planetary sentence stays exactly as it is** for printed and machined stages alike
(`checks._check_stages`, `workbook/checks.py:358-366`, with `report.undercut` at `:362` feeding the build's
interference clause, `gearbox.py:280-282`). It already says the right thing: the undercut is not modelled, and the
pair is to be turned in SolidWorks.

**Later work** (§7): a check that sweeps the two drawn outlines through the mesh with each gear's own backlash, less
a printer's allowance of the size D3 budgets (about 0.1 mm a flank), and warns on any overlap. It is pure code beside
`internal.tip_clash`, which samples the pinion only above its base circle. It is to be rated once §3.2's prints
give the printer's real figure. Its signature would take each gear's recipe, since the outlines need it.

### 2.4 The undrawn part of the flank

Today's warning that the involute starts above the form diameter (from 26 teeth at module 1.5 with the
default fillet) stays as it is. Curing it means a smaller default fillet on large gears, which costs
root strength; left for the user to rule on after the first prints.

### 2.5 Solve and the workbook's fixes

For a printed pair, Solve's shifted rows and the workbook's profile-shift fix test what a printed gear needs: the
tip **after** backlash against the nozzle, and clearance against the larger of 0.1 × module and 0.3 mm. That means
`pair._shifted` (`pair.py:248-289`, whose two tests are at `:278-282`), `pair.shift_for_centre`
(`pair.py:292-329`, at `:323-328`; `CLEARANCE_MIN` at `:92`) and `fixes.shift_fix`
(`workbook/fixes.py:158`, calling `shift_for_centre` at `:173`).

- `pair.tip_thickness` (`pair.py:207`) is the tip before backlash; a printed variant takes the printed backlash
  off it.
- `pair.solve` (`pair.py:387`) gains keywords for the process and the nozzle, machined by default, and
  `solve_spec` (`pair.py:769`) passes the form's.
- Rows whose module is under §2.2's floor, or whose tips are under a nozzle, are ranked after the clean ones and
  marked (*thin for a 0.4 nozzle*).
- A row whose tip comes to a point is not offered.
- Machined pairs keep today's tests.

### 2.6 A measurement to calibrate by (moved to F2)

**Not part of F1** (the coordinator's ruling 1 on F1's review, 2026-11-18). The span over k teeth is F2's first step,
§3.0, built before any print is measured.

### 2.7 Proving the rule

Before F1's first line, pin the following in a new `tests/test_printed_rule.py`, by hash as `BEFORE_W8` does
(`tests/test_workbook_modes.py:232-259`, through `_fingerprint`, `tests/test_workbook_planetary.py:369-384`).
The pins are taken at the commit `printed` is cut from, which is W9 merged into `workbook`:

- strip plans of every kind and recipe in both trig variants, among them the hub, the sleeve, the dog and a banded
  sleeve;
- the three pair assembly plans (`pair.crossed_assembly_plan`, `bevel_assembly_plan` and `assembly_plan`,
  `pair.py:1056`, `1141`, `1193`);
- Solve's rows for a set of spur, helical, ring, bevel and crossed pairs;
- the fingerprints of the W8 fixtures, RangeBox and RangeBox_Fixed (`transfer_case_parallel`, `e4_transfer_case`,
  `range_box` and `range_box_fixed` in `tests/workbook_fixtures.py`). Beside them, `BEFORE_W7` and
  `BEFORE_W8` and W9b's pinned counts (`tests/test_workbook_rangebox.py:19-27`: four warnings and W9b's three)
  stay as they are;
- **the whole `.gear.json` of a machined part, its `spec` and its `derived` both**, for a spur, helical, ring and
  bevel gear and a banded sleeve, and the part's entry in a link record;
- **what Update, the strip and Build again… say for a record written before F1 (no `process` key)**:
  - against a form or workbook marked Machined, and against a workbook whose Process is blank (D11's (B)), which
    must be nothing;
  - that is `update.classify` with no change, `gui._update_target` counting 0, `gearbox._matches` reusing the
    part, and W9d's `update._changed_columns` giving `[]`.

After F1 each is taken again and must be identical, and they pass at every commit of F1, F1-0's interface commit
included (§1.1 is what makes that true of the `.gear.json`).

**What has to be marked machined.** A `GearSpec` or `Box` built in code without saying is machined (§1), so most
of the suite needs no edit:

- the 200 `GearSpec(` constructions in 27 test files;
- the gearboxes built in tests and probe scripts (`tests/workbook_fixtures.py`,
  `src/gear_generator/probe/p7_workbook.py`, `src/gear_generator/probe/p8_motion.py`,
  `probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, W9's demonstration scripts);
- the boards in `design/canvas/gen.py`.

What reads printed is what a user's blank reads with no record, and `model.template()`. That covers the **five**
committed workbooks that Excel or LibreOffice saved, none of which has a Process row: `tests/fixtures/excel-windows/`'s
three, and `tests/fixtures/excel/`'s and `tests/fixtures/libreoffice/`'s Reducer. They are read in ten test files:
`test_workbook_axes`, `_bands`, `_build`, `_demo_fixtures`, `_export`, `_model`, `_modes`, `_motion`,
`_planetary` (`BEFORE_W7`, `:388-405`) and `_xlsx`. No package owns them, and they would fail only when B's
reading and A's maths are both in, at the merge.

So **F1-0 marks every read of a committed workbook in those ten files machined**, through one helper it adds to
`tests/workbook_fixtures.py`: `machined(spec) -> GearboxSpec`, the spec with its Box's Process set to
`machined`. Marking the read inside `test_workbook_demo_fixtures.assessed` also covers its two importers,
`test_workbook_update.py:1298` and `test_workbook_gearbox.py:1383`, so B's files need no mark. Until B lands the mark changes nothing, since a blank Process then reads machined. After it, they keep
what they pin. Package B adds the tests that read those files printed, in its own new file.

W9's masters on the Windows host (`<probe folder>\...`) were written before F1 and have no Process row. Under (B)
they open Machined, as built. A W9 demonstration run again with an app at or after F1 needs nothing written into
them.

### 2.8 F1, ready to execute

**F1-0's interface.** This is what F1-0 fixes so that packages A, B and C cannot collide. It lands in one commit
after the pins (§2.7), and is written up in `docs/notes-printed/F1-INTERFACES.md`. Every name below is
importable from then on. Stubs return neutral values, never raise, so B's and C's printed paths run before A lands.

1. **`spec.py`, whole:**
   - `PROCESS_PRINTED`, `PROCESS_MACHINED`, `NOZZLE_DEFAULT = 0.4`;
   - the fields `process = "machined"` and `nozzle = ""`;
   - `process_value()` (raises `InputError` on a bad word), `is_printed()` (never raises) and `nozzle_mm()`;
   - `to_dict` leaving both keys out for any spec not printed (§1.1);
   - the `_P` stem in `default_stem` (`:285-317`) for a printed spec.
2. **The printed backlash itself:**
   - `spur.PRINTED_BACKLASH = 0.3` and `spur.PRINTED_BACKLASH_UP_TO_MODULE = 1.0`;
   - `spur.printed_backlash_expression(module_name) -> str`, giving the IIF text;
   - its use in the five variable writers and the four derives (§2.1) when `spec.is_printed()` and the Backlash is
     blank.

   It is small and pure, and moves no machined pin. Without it, B's and C's printed tests could not tell printed
   from machined until A lands.
3. **On the derived gears:**
   - `nozzle: Optional[float] = None` on `SpurDerived`, `InternalDerived` and `RackSection`, set through their
     constructors by each derive;
   - the properties `printed` and `backlash_printed` on those three, and on `HelicalDerived` and
     `BevelDerived` through `section`;
   - the four `to_dict`s leaving `nozzle` out while None (§1.1).
4. **The pair maths' names, in `pair.py`, stubbed:**
   - `ring_tip_clearance(...)`, of `tip_clearance`'s signature. The stub returns `tip_clearance`'s figure;
   - `printed_tip_thickness(module, teeth, pressure_angle, helix_angle, shift, nozzle) -> float`. The stub returns
     `tip_thickness`;
   - `solve`'s keywords `process="machined"` and `nozzle=0.4`, accepted and ignored by the stub;
   - `shift_for_centre`'s keyword `printed=False`, the same.
5. **The workbook's names:**
   - `model.Box.process = "machined"` and `model.Box.nozzle = ""`;
   - `schema.Setting.words: Tuple[str, ...] = ()`;
   - **the two `Setting`s, Process and Nozzle, in `schema.BOX_SETTINGS`** (after Efficiency, before Units, with
     their notes and Process's words);
   - **`to_sheets`' two `box_values` keys** (`model.py:601-604`), writing the Box's word as held and its nozzle;
   - **the pin of the Box's titles, `tests/test_workbook_model.py:24-27`, moved to the two new titles.**

   These three land in one commit. `to_sheets` writes `box_values.get(key, "")` for every setting
   (`model.py:605-606`), so the settings without the keys would write a gearbox built in code with a blank
   Process. Read back with no record, that blank is Printed. And the pin is in a file only F1-0 may touch, so B
   could not add the settings without breaking a test it may not edit.
   - `assess.blank_process(record) -> str`, written whole (§1.3: it is D11's switch);
   - `assess.assess(..., blank_process=PROCESS_PRINTED)`, resolving a blank Process in both `read` and `spec`;
   - `Gear.spec_values` passing `process` and `nozzle` from the Box.
6. **The form's names:** `gui.GEAR_COMPOUND` gains `process` and `nozzle`, so `test_gui_spec.py:49-52` stays
   green. `_gear_spec` does not yet set them.
7. **The record:**
   - `store.LINK_SCHEMA_VERSION = 11` with `_W9D_LINK_SCHEMA = 10`;
   - `store.PRINTED_SCHEMA = 3` and `SCHEMA_VERSION = 3`;
   - `sidecar_schema` giving 3 for a printed spec;
   - every literal 10 of §1.2 moved: the ten lines listed there, and any more `git grep` finds at the cut.
8. **The labels and words:**
   - `update._SPEC_COLUMNS`'s new pair is `("process", "Process")`;
   - every new sentence's words go in the note: the checks of §2.2, the single gear's printed undercut sentence of §2.3, K11's two (§6), the Box's error and
     note, the Workbook panel's Process line in both states, and the three (A)-only sentences of §1.3, kept for a
     later switch.

**Which test files F1-0 touches, and only these:**

- the new `tests/test_printed_rule.py` (§2.7's pins);
- `tests/workbook_fixtures.py` (the `machined` helper);
- the ten files that read a committed workbook: `test_workbook_axes`, `_bands`, `_build`, `_demo_fixtures`,
  `_export`, `_model`, `_modes`, `_motion`, `_planetary`, `_xlsx` (each read marked machined);
- the files of the eight schema pins not already listed: `test_store`, `test_workbook_carry`,
  `test_workbook_user_record`, `test_workbook_window`.

F1-0's source files are `spec.py`, `store.py`, `gears/spur.py`, `helical.py`, `internal.py`, `bevel.py`
(item 2 and item 3 only), `gears/pair.py` (stubs), `workbook/model.py` (item 5's lines: `Box`, `spec_values`,
`to_sheets`' keys), `workbook/schema.py` (`Setting.words` and the two settings), `workbook/assess.py`, and `gui.py`
(`GEAR_COMPOUND`). The whole suite and §2.7's pins
pass at its commit.

**The packages.** Each owns its files outright from F1-0's commit on. No two share a file, in `src` or in
`tests`.

- **A, the gear maths** (pure).
  - Files: `gears/spur.py`, `helical.py`, `internal.py`, `bevel.py` (the checks of §2.2, the ring's tip, the
    bevel's toe, the ring-fillet sentence), `gears/clutch.py` if it needs anything, `gears/pair.py` (the stubs
    made real, Solve's ranking and marking, `mesh_warnings`), `gears/__main__.py` (the command line's
    `process` key), `workbook/fixes.py`.
  - Tests: `test_gears_spur`, `_helical`, `_internal`, `_bevel`, `_clutch`, `_pair`, `test_profile_shift`,
    and a new `test_printed_gears.py`.
- **B, the workbook, the record's comparisons and Update.**
  - Files: `workbook/schema.py` (the Backlash column's blank words, `:155`; the two settings are F1-0's),
    `workbook/model.py` (`_read_box` keeping the blank, the word check, `template`; `to_sheets`' keys are F1-0's),
    `workbook/checks.py` (§2.2's radial clearance at each Meshes row; W7's planetary sentence untouched),
    `workbook/update.py` (`_SPEC_COLUMNS`), and `swbuild.py` (K11's words only, `:5460-5489`).
  - Tests: `test_workbook_checks`, `test_workbook_update`, `test_workbook_gearbox`,
    `test_swbuild_user_work` (K11's words), and a new `test_printed_workbook.py`, which also reads the committed
    workbooks printed and tests `blank_process` with each kind of record. It also tests that no `Assessment` holds a
    blank Process, in `read` or in `spec`. `test_workbook_model` was F1-0's; B
    adds its Box tests to the new file instead, so the ten files stay F1-0's alone.
- **C, what the user sees.**
  - Files: `gui.py` (the rows, `_gear_spec`, `_load_record`, Solve passing the process), `ui_text.py` (the
    backlash readouts' third state, the explainers, the Workbook panel's Process line), `workbook_gui.py` (the
    third review's three should-fixes: `_assess` reads the record and passes `blank_process(record)`, so that both
    its callers, `_plan` and the raw assessment at `:692`, resolve the blank alike; it passes no record when the
    record is another workbook's, by `store.foreign_workbook`; and it relies on `assess` leaving no blank in
    `read`; plus the panel's line), `design/` (the
    board first: the strip with its Process row, and a gearbox built before F1 opened Machined, then typed Printed),
    `README.md`.
  - Tests: `test_gui_spec`, `test_ui_text`, and a new `test_printed_window.py` for the window.
    `test_workbook_window.py` is F1-0's; its pinned panel text for every gearbox moves by the Process line (open
    point 3). C rewrites those lines there after F1-0 is in, as its only edit to that file, and no other package
    touches it.

B's `checks.py` calls A's ring-pair clearance, and C's readouts read the derived gear's properties and the Box's
resolved Process. Each meets the others only through item 1 to 8's names. For two implementers in place of three, A and B
are one package (the model) and C the other (the view). The review then reads the merged head, and one SolidWorks
run follows.

**When each package can start.**

1. **F1-0 first, alone**, once W9 is merged into `workbook` and `printed` is cut. It needs nothing more settled:
   the third review's three open items (the schema lines, the Box settings with their pin, and the pair check's
   signature) are settled above.
2. **B and C next, in parallel**, as soon as F1-0's commit is in. Neither waits on A, since F1-0 lands the printed
   backlash and stubs every name A fills.
3. **A at the same time.** The third review had A wait on §2.3. That wait is discharged by the ruling written
   there: no pair interference check, and no `printed_pair_warnings` in the interface. A's remaining work is §2.2's
   per-gear checks, the ring-pair clearance, the printed tip, Solve's ranking and the fixes, all settled. If the
   coordinating session wants this revision checked again first, A is the only package that waits for it.

**What must not move.**

- Every pin W9 left: `BEFORE_W7` and `BEFORE_W8`, with the three `excel-windows` workbooks marked machined as
  read (§2.7).
- RangeBox's four warnings and W9b's three; the W8 fixtures' counts, each moved by three in W9b.
- Every test of W9a to W9d against the fake, unchanged, since their fixtures are built in code and so are machined.
- `tests/test_findings.py`: F1 adds no finding, and every 2026 and 2024 value, gate and pinned log line stays.
- W9's demonstration scripts' self-checks.
- No SolidWorks call is added or changed.
- **What moves, by ruling:**
  - the eight schema lines (§1.2);
  - the Workbook window's pinned panel text, by the Process line, for machined gearboxes too (open point 3);
  - the Box rows *New workbook…* writes (`test_workbook_model.py:307`).

**Tests F1 owes against the fake**, beside §2.7's pins:

- *The default, where the user chooses:*
  - a blank form, and a Solve applied to it, give printed specs, and the form's Process covers both gears of a pair;
  - a form loaded from an old `.gear.json` is Machined and builds machined.
- *The record:*
  - a printed spec's `to_dict`, `derived` and sidecar (schema 3), and a link record at 11;
  - `to_dict` on a bad Process word does not raise and drops the keys, and drops a typed Nozzle when machined;
  - a schema 10 record from W9 reads, and its parts are machined; a schema 12 record is refused and left
    byte-identical;
  - machined bytes, `derived` included, equal W9's.
- *The Box and D11:*
  - the Process word check (any case; an error at the cell for anything else); Nozzle positive;
  - *New workbook…* writes Printed and 0.4, and `to_sheets` / `from_book` round-trip both words;
  - `blank_process` gives Machined for a record whose parts are all machined, both before F1 and after it;
    Printed with no record, with no parts, and with any part built printed;
  - the rule does not change after an F1 write moves the record to 11;
  - the Process line's words when the Box has no Process row.
- *The equation:* its text in each of the five writers, and the derived backlash at modules 0.5, 1 and 1.5 (equal
  to the machined value at module 1 and below, never more than it).
- *Each check of §2.2 and §2.3*, with this plan's figures:
  - module 1 warning below 26 teeth and passing at 26; module 1.25 passing from 11;
  - the module floor; clearance at module 0.75 passing within the tolerance; bevel pairs under module 1.6;
  - the rim; helix 45°; the ring's tip; the ring-fillet sentence;
  - no pair interference warning, printed or machined, on any pair: RangeBox, planetary_4to1 and Risky_Placements
    printed carry exactly the warnings they carry machined, except §2.2's per-gear ones;
  - W7's planetary sentence and `report.undercut` the same printed as machined;
  - the single gear's printed undercut sentence in place of the generated-gear lead-in, the named shift kept.
- *Solve and the fixes:* printed ranking and marking; no row with a pointed tip; machined rows equal to the pin.
- *K11:* for a printed default the user changed in SolidWorks, the sentence names the workbook's value in words
  and the set-back as the exact IIF text SolidWorks must hold (§6).
- *A gearbox built before F1:*
  - RangeBox is built machined against the fake, then read with a blank Process. It is Machined, nothing changes,
    and the footer is as today.
  - With Printed typed, every part reads *changes on Update* for Backlash alone; none needs a new part or a put;
    Update runs end to end on the fake.
  - Build again… names each part's reason as *its Process changed*.

**The open decisions.** F1 can go ahead on each without a word from the user:

- **D3** is two constants and one equation text. Changing the number later is a one-line change and its tests. A
  printed part already built then reads *changes on Update* for Backlash, and Update carries it in place. No part is
  made new.
- **D6** is now one sentence on a printed single gear, and no pair check (§2.3). The later sweep check (§7) adds a
  function and its warnings and moves no machined pin. Drawing the true undercut would be a plan of its own, and
  nothing in F1 stands in its way.
- **D7** is F4's only; F1 does not read it.
- **D11** is ruled (B). If the user chooses (A), the switch is `assess.blank_process`'s body, and three sentences
  are added (§1.3). Packages B and C can be written now.

**Done when:**

- §2.7 holds.
- A printed spur, helical, herringbone, ring and bevel gear, a sleeve, a dog and a hub each derive, check and plan
  against the fake.
- A workbook built before this plan opens Machined and unchanged, and after Printed is typed, Update carries it
  against the fake.
- The boards in `design/` show the Process row, the Workbook panel's Process line and one printed warning.
- `design/UI-DESIGN.md`, the README and the backlash hints say what Printed does.
- Not in F1: the span over k teeth (§2.6), which is F2's first step (§3.0).
- On SolidWorks 2026, three things: one printed spur gear built; one printed pair built; and, on a copy of W9a's
  `setup.master` (RangeBox with the user's work), Printed typed on its Box sheet and one Update. That Update writes
  every part's Backlash in place, touches none of the user's items, and reads back as W9a reads its own Update.
- The same three on 2024, as the confirming build. Its first press on a freshly opened RangeBox costs SolidWorks
  2024 3.3 to 4 GB, as W9c measured, so it runs in a fresh session.
- The stage's result is reviewed by a subagent.

**Cost:** about six agent runs: F1-0, three packages, the review, and the SolidWorks run. SolidWorks time is an
estimate, not a measurement: about 20 minutes on 2026 and 30 on 2024.

**Open points, as ruled after the second review.** Each is the user's to overrule.

1. In code, a `GearSpec` or `Box` that does not say its process is machined; only the form's row and the Box
   sheet's blank are the user's; `to_dict` and the derived `to_dict`s leave the new keys out unless printed (§1).
   *Confirmed by the review.*
2. K9's running clearance stands for printed sleeves unchanged (§6). *Confirmed.*
3. The Workbook panel shows *Process* for every gearbox, Machined too. Under (B) the machined ones are the ones that
   need saying. *Confirmed*; `test_workbook_window`'s pinned panel text moves by that line.
4. *Withdrawn by the coordinating session's ruling of 2026-11-18:* no pair check replaces W7's planetary
   sentence, which stays word for word, printed and machined (§2.3).
5. The link record goes to 11 whatever the process, as W9b's 8 did. *Confirmed.*
6. F2's export refuses a part the record marks unsaved or mismatched (§3.1). *Confirmed.*
7. *Withdrawn by the same ruling:* the half-nozzle margin. No pair interference warning is built in F1 (§2.3).
8. **New:** D11 answered (B) by the coordinating session.


## 3. Stage F2 — the span over k teeth, the file for the slicer, and the first prints

**Closed 2026-11-18, short of §3.2, the user's own step.** Every row of §3.3's *Done when* that does not need the
user is met (`F2-DEMONSTRATION-RUNS-REVIEW.md` §2, `70a2c42`). Its demonstration ran clean on SolidWorks 2026
34.1.1 and 2024 32.5.0 (`9c1275f`).

- **Still owed, all the user's:**
  - the coupons built, exported and printed;
  - Bambu Studio opening the STEP files (U5);
  - §3.2's table filled;
  - from it, D3's printed backlash (U4, with the choice above 0.3 mm) and F3's bore allowance.
- **Nothing of it is merged into `workbook`.** The README's *Calibrating your printer* and §3.2 below are the
  user's instructions.

Read against the code at `61460b9` on branch `printed`, which holds F1 closed and W9 merged (`138d646`); `src` is
unchanged at `926cf50`. Lines below are as of that commit. Revised to F2's review (the last section of
`docs/PLAN-PRINTED-REVIEW.md`, `926cf50`) and the coordinating session's ruling on repeat presses.

### 3.0 First, the span over k teeth

F2's first step, before any print is measured (moved from §2.6 by the coordinator's ruling 1 on F1's review,
2026-11-18). It is pure code and the form's text, and needs no SolidWorks.

**What it is.** The *span over k teeth* is the base tangent length: the distance between two flat caliper jaws laid
across k teeth, each jaw on the outside flank of an end tooth. On an involute gear the jaws' common normal is
tangent to the base cylinder, so the reading is the same wherever the jaws touch the involute. That makes it the one
tooth dimension a person can measure well with ordinary calipers.

**The maths.** For an external involute gear, the app's own sizes are enough. In the transverse plane:

    W_t = (k − 1) · p_bt + s_bt
    p_bt = π · d · cos α_t / z          (the base pitch)
    s_bt = d_b · (s_t / d + inv α_t)    (the tooth's thickness on the base circle)
    inv α = tan α − α

Here `s_t` is the drawn tooth's thickness at the pitch circle, after backlash and shift: the derived gear's `s`
(`spur.SpurDerived.s`, `gears/spur.py:178`; a helical gear's `section.s`, which is transverse, `helical.derive`
thinning it by `j / cos β`, `helical.py:354`, so the app's backlash is a normal one). For a helical gear the
calipers read square to the teeth:

    W_n = W_t · cos β_b,   sin β_b = sin β · cos α_n

The same in closed form, which the tests hold the first form to:

    W_n = m_n cos α_n [ (k − 0.5) π + z inv α_t ] + 2 x m_n sin α_n − j_n cos α_n

Here `j_n` is the backlash the gear was drawn with (0.3 mm printed from module 1 up). This is the standard base
tangent length: KHK's *Gear Technical Reference*, span measurement (its Tables 5.10 and 5.11; the review fetched the
page, whose formulas are images, so only its text is quoted), with the backlash term `A_Wk = A_sn cos α_n`. DIN 3960
and ISO 21771 give the same as the reviewer and writer know them; neither was checked.

**Which k.** The jaws' common normal is the base-cylinder tangent, inclined at β_b. The jaws lie ±W_n/2 along it from
the tangent point, so projected on the transverse plane they are `W_n cos β_b / 2` from it, and the contact radius is:

    r_c = √(r_b² + (W_n · cos β_b / 2)²)

For a spur gear, where β_b = 0, this is `√(r_b² + (W/2)²)`. The panel takes the k whose `r_c` is nearest
`r + x · m_n`, the middle of the working flank. That is the textbook k through `d_M = d + 2 x m_n`: the usual
`k ≈ z α / 180° + 0.5` for an unshifted spur gear, KHK's shifted rule, and the helical one. The first revision took
`W_t / 2` for a helical gear, which chose k 3 where the textbook chooses 4 for m_n 1.5, z 25, β 20°, an error that
grows with β (the review's must-fix M1).

**Bounds on the contact.**

- If `r_c` falls below where the app's involute starts, `max(flank_start_d, form_d) / 2` (below it the app draws a
  radial flank), or within 0.2 mm of the tip radius `d_a / 2` (a printed tip rounds by about half a line), the next
  k inward or outward is taken. If no k has its contact inside, no span is shown.
- None of the figures below is near either bound. The closest is RangeBox's Planet, 8.112 against 7.635.

**A helical face too narrow to measure.** Both jaws must lie whole on the flanks, so a helical gear needs
`b ≥ W_n · sin β_b + Δb` with `Δb = 3 mm` (KHK's text: "Δb > 3 mm to make a stable measurement"). Below that the row
says the face is too narrow and gives no figure. For a herringbone gear, `b` is one half,
`HelicalDerived.toothed_width` (the face less the groove, halved; `helical.py:180-183`; the first revision called it
`half_width`).

**Which gears show it.**

- **Shown:** a printed external spur, helical or herringbone gear drawn with the involute recipe (A, the default),
  a printed dog and a printed hub (each an external spur gear by `clutch._as_spur`).
- **Not shown:**
  - a ring or a sleeve, whose span is taken over pins (balls for a helical ring), not jaws;
  - a bevel gear, whose tooth is not of one size along its face;
  - a machined gear. Its Derived panel is unchanged, as the rule asks, and `tests/test_printed_rule.py` holds it.

**A gear drawn with arcs (recipe B): the ruling** (this revision's, the user's to overrule). On arcs the span is not
one figure. On the printed m 1.5, z 20 gear it runs from 11.139 to 11.221 mm across the flank (the review, read off
the app's own outline). That 0.08 mm is about the size of what the user is measuring.

- **The least misleading thing is to show no figure.** The row reads *Span over k teeth: not one figure on arcs;
  choose Involute to measure*.
- A range would invite the user to average two numbers that are not a measurement. One mid figure would look exact
  and be up to 0.04 mm off.
- §3.2's coupons are built with Involute, so the user's calibration never meets this.
- The print list says the same for an arcs part.

**Where the user sees it.**

- **The form's Derived panel** gains one row, *Span over 3 teeth* with `11.209`, after *Tooth at pitch*
  (`ui_text.derived_rows`, `ui_text.py:118-180`). Under it goes an entry, **Measured**, mm, blank by default.
  - When the user types their calipers' reading, the line under it gives what their printer adds to each flank,
    `e = (reading − W) / 2`, square to the flank: *your printer adds 0.041 mm a flank*.
  - It also gives the backlash per gear that would keep D3's running play: `j = 2 (e + 0.04) / cos α_n`, with the
    gear's own `α_n`.
  - **The floor.** The line never proposes less than 0.1 mm a gear, and says so when it holds there. Below about
    `e = −0.04` the formula reaches 0, and §2.3's sweep found the drawn parts overlapping under about 0.04 mm a gear
    (0.08 for a 6 / 30 pair).
  - **When it exceeds today's default.** When the proposed `j` exceeds `0.3 × module` for this gear, the line says
    so. That is the case D3's *never more than today's* is about (U4, §3.4).
  - The entry is the form's only, and is not saved.
- **The print list** of §3.1 gives each printed involute part's k and span, so each print can be measured. A
  machined part's block says *no span: machined*, as E1 has it. An arcs part's block says it is not one figure.
- **The explainer card** for the new row says what the span is and how to hold the calipers: square to the axis on a
  spur gear, tilted with the teeth on a helical one. It also says that the figure is the gear as drawn, backlash
  included.

**Figures the tests owe.** These are this plan's calculation at `61460b9`, and the review's recomputation three ways
agrees with them. Each test holds a figure to 1e-4 mm, in both forms.

| Gear | Backlash (mm) | k | W (mm) | Contact radius / pitch radius |
|---|---|---|---|---|
| spur m 1.5, z 20, printed | 0.3 | 3 | 11.2088 | 15.169 / 15.0 |
| spur m 1.5, z 20, machined (not shown; the formula only) | 0.45 | 3 | 11.0678 | 15.143 / 15.0 |
| spur m 1, z 12, printed | 0.3 | 2 | 4.3144 | 6.037 / 6.0 |
| spur m 2, z 30, printed | 0.3 | 4 | 21.2233 | 30.122 / 30.0 |
| spur m 1.5, z 15, x +0.3, printed | 0.3 | 3 | 11.4115 | 12.013 / 11.25 (+0.45) |
| spur m 1.25, z 29 (RangeBox's Sun), printed | 0.3 | 4 | 13.1414 | 18.255 / 18.125 |
| spur m 1.25, z 13 (its Planet), printed | 0.3 | 2 | 5.4809 | 8.112 / 8.125 |
| helical m_n 2, z 20, β 15°, printed | 0.3 | 3 | 15.0972 (W_t 15.5645) | 20.713 / 20.706 |
| helical m_n 1.5, z 25, β 20°, printed | 0.3 | **4** | **15.8438 (W_t 16.7315)** | 20.062 / 19.953 |
| helical m_n 2, z 20, β 30°, printed (new) | 0.3 | 4 | 21.2255 (W_t 24.0448) | 23.260 / 23.094 |

The face each helical row needs, `W_n sin β_b + 3`, is 6.67, 8.09 and 12.97 mm (β_b 14.076°, 18.747°, 28.024°).

**The check owed by package A, in place of a textbook example.** ISO 21771 is sold, and KHK's formulas are images.
So package A checks the formula against the app's own drawn outline: for recipe A, the span read off
`SpurGear.outline`'s points across k teeth equals the formula to 1e-4 mm. The review did this for four spur rows, the
involute holding to 1e-15 rad. It tests the app's own backlash and shift conventions, which a textbook example
cannot. If a printed worked example is found, it is quoted in A's note as well.

Beside the table, the tests owe:

- the row on a printed gear, and not on a machined one, a ring, a sleeve or a bevel gear;
- the β 20° and β 30° k;
- the contact bound, on a z 6 pinion and on a negative shift;
- the narrow-face sentence at `W_n sin β_b + 3` mm, and on a herringbone's half;
- recipe B's sentence;
- the Measured line for a reading above, at and below the span, its `cos α_n`, its floor, and its line when `j`
  passes `0.3 × module`;
- the explainer.

### 3.1 Export: a probe first, then the files for the slicer

**The name and the place.** The Workbook window already has **Export** and **Export as…**, which write fixes and
the Results sheet into the workbook (`workbook_gui.py:518-520`). In this app an ellipsis means a question or a
dialog follows, and the new press asks nothing. So the new button is **Print files**, without an ellipsis, and its
sentences say *STEP file* (E5).

- **On the form** it goes in the **footer**, beside **Update values** and **Build**. The Output panel holds the
  folder, the templates and *Open .gear.json* (`design/UI-DESIGN.md:210-228`).
- **In the Workbook window** it goes in the footer's button row, a fifth button. The board must show that the
  footer's sentence keeps its 400 px at 1080 (`UI-DESIGN.md:623-628`).

#### 3.1.1 What is already known

- **The route is in the user's macro database, on SolidWorks 2026 only.** `/home/m0obot/SW-Macro-Database`,
  `entries/files/04-export-a-body-to-step.md` and `API-LEDGER.md:190`:
  `IModelDocExtension.SaveAs(path.STEP, 0, 1 | 2, null, out errors, out warnings)`. That is the current version,
  options *silent* (1) and *save as copy* (2), the format taken from the extension.
  - It was verified on SolidWorks 2026 by the Airfoil Converter (2026-09-16), on the active part, through the same
    `_out_long()` and `_null_dispatch()` this repo's `swcom` has. Its STEP files were read back and measured.
  - *Copy* is what keeps the open document under its own name. Without it a save-as renames the document
    (`documents/02`).
  - Not seen there: non-zero `errors` or `warnings`; the AP and the export options (the user's *Tools > Options >
    Export*); the unit the file declares; a document not active, modified, or open only as a component of an
    assembly; and any run on SolidWorks 2024.
- **Which call.** The app already calls `SaveAs3` on the same `Extension` with the same typed nulls, on both
  versions (`swcom.py:1366-1376`). The ledger says to prefer `SaveAs`, which takes the export data argument and gives
  `errors` and `warnings` back. **F2 uses `SaveAs`** for that reason, and F2-0's note says so.
- **`SaveAs3` overwrites an existing file without a word** (the macro database's `GOTCHAS.md` §34, and this repo's
  probe `save_as`, `src/gear_generator/probe/p3_files.py`). Under §3.1.3's folder per press, the app never writes
  to a path that exists; `export_step` refuses one anyway.
- **Opening a STEP file in SolidWorks is its own trap**: `OpenDoc6` fails on STEP and `LoadFile4` is the import
  route (`GOTCHAS.md` §20). This is one more reason the app never reopens what it wrote.
- **Verified on both versions in the ledger:** `GetSaveFlag`, `CloseDoc` (discards, with no prompt, for parts),
  `OpenDoc6` and `ActivateDoc3` (`API-LEDGER.md:107-116`, `:150`, `:171`). The ledger's line 113 records a 2024
  *Save Modified Documents* box on closing an **assembly**.
- **This repo has never written a file other than a part, an assembly and its own records.** `findings.py` has
  `SAVE_AS_SILENT = 1` (`:58`) and nothing for a copy or a foreign format.

So by the house rule the export is **probed first**, on both versions. It is a call the app has not made, it
writes a file, and it could raise a dialog or rename a document.

#### 3.1.2 The probe, call by call

`probe/f2_probes.py`, written in the manner of `probe/w9d_probes.py`. It uses W9a's harness: attach by `--pid`,
check the version, the dialog watch (which logs a window and never answers it), keep-awake, the run's own APPDATA,
JSON after every section, and `--self-check` for its pure judgements. Its note is
`docs/notes-printed/F2-PROBES.md`.

- **Scratch only.** Every part is built in the run's folder by the app's own build routes, and saved, so the reads
  start unmarked:
  - one printed spur gear (m 1.5, z 20, face 8, no bore);
  - one printed helical gear (m_n 2, z 20, β 15°);
  - one printed pair, 25 / 50 at module 1.5, built fixed by the form's pair route, for step 7.
- **Nothing of the user's is touched.** The run records the open documents' titles **and save flags** first, and
  reads them again at the end. It closes only what it opened, unsaved.

Each step reads `GetPathName`, `GetTitle` and `GetSaveFlag` before and after, and the dialog watch runs across it.

1. **The constants.** It reads `swSaveAsOptions_e`'s `swSaveAsOptions_Silent` and `swSaveAsOptions_Copy` from
   `swconst.tlb`, as W9d's probes read their enums. *Sets* `findings.SAVE_AS_COPY` (expected 2) beside
   `SAVE_AS_SILENT`.
2. **The export.** `IModelDocExtension.SaveAs(<run>\print\Gear.step, 0, silent | copy, None, out, out)` on the
   saved spur part, active.
   - Asks whether it returns True with `errors` and `warnings` 0, whether the file is on disk and not empty, and
     whether no window appears within the watch.
   - Asks whether the path, the title and the save flag are all unchanged.
   - Logs the time it takes.
   - *Sets* `STEP_EXPORT_ON_<year>` True when every answer is as expected here and in step 4, with its log lines. A
     rename, a marked flag, a dialog, a non-zero code or no file each leave it None, and the log says which.
3. **The file, read as text.** Facts for the note, and the evidence for §3.1.4's check:
   - the frame: the file opens `ISO-10303-21;` and ends `END-ISO-10303-21;`;
   - the `FILE_SCHEMA` written (an AP the user's settings chose);
   - the count of entity instances `= MANIFOLD_SOLID_BREP(`, `= CLOSED_SHELL(`, `= OPEN_SHELL(` and
     `= SHELL_BASED_SURFACE_MODEL(`;
   - the length unit;
   - and, from the `VERTEX_POINT`s' coordinates, the largest radius from the part's axis and the axial extent,
     against the app's `d_a / 2` and face width.

   Nothing here is pinned per version (M2, §3.1.4).
4. **The helical part**, the same as 2 and 3. Its flanks are spline surfaces, so the file differs in kind, not in
   count.
5. **Onto an existing path.** A second export to step 2's file. This is a fact only, expected to overwrite as
   `SaveAs3` does; the app never asks it to.
6. **A part open in its own window but not active.** The spur part is open in its window, the helical part is made
   active, and the spur is exported by its own document object.
   - **The file is right** when it is **the same part** as step 2's file and not step 4's, **by geometry, not text**
     (the coordinating session's ruling 1, 2026-11-18, after the probe's runs: SolidWorks numbers each export's
     entities otherwise, so two exports of one unchanged document differ in nearly every statement, and the first
     revision's text test could never hold). Two files are the same part when, header and entity numbering aside,
     they hold the same count of every entity kind, the same set of CARTESIAN_POINTs one to one and the same circle,
     cylinder, sphere and torus radii, each within 1e-4 mm. The run holds the comparison to its own files first: step
     2's and step 5's (one document twice) the same part; the spur against the helical (steps 2, 4) and the 8 mm spur
     against the 9 mm one (steps 2, 8) not. Without those, no file is judged.
   - *Sets* `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>`: False if the file is right and the active document, its title and
     every save flag are unchanged, else True.
7. **A part open only as a component of an assembly (the Workbook window's case, must-fix M5).**
   - The pair's assembly is open and active, and the gear's own window is closed, so the part is loaded only as the
     assembly's component. The gear is reached by `ISldWorks.GetOpenDocumentByName(<part path>)` and exported by
     that document object, with no activation.
   - It reads the assembly's title and save flag, the active document, and the component's state before and after.
   - The file is right by step 6's test (the same part by geometry) against a fresh export of the same part, opened
     alone after the step, and not the pinion's; that pair and two exports of the gear alone are this step's own
     controls, beside step 6's.
   - *Sets* `STEP_EXPORT_FROM_COMPONENT_ON_<year>` True when the file is right, nothing is activated, and the
     assembly's save flag is unchanged.
   - **Then the fallback, the same part opened in its own window by `Session.open_document`** (`swcom.py:3541`, which
     activates), exported, then closed by `CloseDoc` on its title. It reads whether the assembly is still open,
     unmarked, its component still loaded and resolved, and whether any window came. This *sets*
     `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>`, **for a resolved component only**.
   - **A lightweight component** (the coordinating session's ruling 2, 2026-11-18): the runs showed that neither the
     document walk nor `GetOpenDocumentByName` reaches its part, and that opening the part beside the assembly resolves
     the component in the user's assembly, a change to their session. Until a run shows what that leaves behind, **the
     export refuses a lightweight component by name** and tells the user to resolve it or open the part
     (`LIGHTWEIGHT`, `F2-INTERFACES.md` §5.2). The probe's next run reads the assembly's save flag and the component's
     state after that close, as facts.
8. **A modified part.** One global changed and rebuilt, the part not saved, then exported. It asks whether the file
   holds the changed solid (not the same part as step 2's by geometry, a fact, and step 6's negative control) and whether the save flag stays
   set and the path unchanged.
   - This is the evidence for refusing unsaved parts. The app refuses them by ruling (open point 6) whatever this
     shows.
9. **Closing.** Every probe document is closed unsaved under the watch: the parts, then the assembly last. The open
   titles and save flags are compared with the start.

**The first revision's step 8 (a part built into error) is dropped, as this revision's proposal for the coordinating
session.** Nothing in the app rests on it, since a part in error is refused before any export. It would add the one
dialog the run expects, and on 2026 a What's Wrong box is the STOP. By the handoff's rule, a point the app does not
depend on is written as a caveat: *a STEP export of a part in error is not measured; the app never makes one*.

**Which answer sets which finding** (`findings.py`, each None until its run is reviewed, with its log lines in the
comment as every finding has):

| Finding | Set from | While it is None |
|---|---|---|
| `SAVE_AS_COPY` | step 1 | **Print files** is shown and enabled, and refuses on every version: *Print files waits until writing a STEP file is measured on this SolidWorks; nothing was written.* |
| `STEP_EXPORT_ON_2026`, `STEP_EXPORT_ON_2024` | steps 2 and 4 | The same refusal on that version, by name: *… measured on SolidWorks 2024 (32.5.0) …*. |
| `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` | step 6 | The app activates each part before exporting it, then puts the user's active document back (§3.1.3). |
| `STEP_EXPORT_FROM_COMPONENT_ON_<year>` | step 7, first half | A part open only as a component is opened in its own window by the fallback, if that is measured, else the press refuses it by name: *Gear_m1.25_N29_P is open only inside RangeBox; close the assembly or open the part, then print*. |
| `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>` | step 7, second half | The fallback is not used. |

**On SolidWorks 2026 and 2024.** The two runs set each version's findings separately, as W9c's gates were set.

- *2026:* run on this laptop's 34.1.1, about 12 minutes. SolidWorks 2026 is where the route was verified before, by
  another program; this measures it under the app's own session and builds.
- *2024:* run on 32.5.0, about 18 minutes, in a fresh session. Any window is the STOP, now that step 8 is gone.
- The house rule allows one follow-up round per version. §3.3's cost counts it.

#### 3.1.3 The export on the form and in the Workbook window

**On the form.**

- **Print files** exports **the part active in SolidWorks** when it is a part with a readable `.gear.json` beside
  it: the same condition the SolidWorks bar's snapshot and `_update_target` (`gui.py:1573`) use to find *this part*.
- That part may not be the gear on the form, so the SolidWorks bar says which file it will write, as it does for
  Update values (`UI-DESIGN.md:216-221`): *Print files will write Gear_m1.5_N20_P.step from the active part.*

**In the Workbook window.**

- **What is exported.** Every part of the record's current revision (`store.LinkRecord.current_parts`,
  `store.py:1026`), hubs, dogs and sleeves among them, each once however many rows share it.
  - Not exported: carrier parts (axes and planes only), the layout, the assembly, and the user's own components.
  - A gear part holding a feature of the user's (a keyway) is exported as it stands, feature and all, and the list
    says so.
- **When it is refused, before any job** (pure, from the window's planning read), naming each part:
  - the record marks a part **unsaved or mismatched** (W9a's marks, `update._mark`, `workbook/update.py:676-683`);
  - **a part the workbook asks for is not the part on record**: Update SolidWorks would change its values, or it
    needs a new part, or a gear row has no part yet;
  - the workbook has an error, or the record is not this workbook's.
  - A change Update would make only to the layout or the assembly (a shaft's place, a slide) does **not** refuse,
    since a print set does not depend on where the shafts are (E3).

**Refused in the job, on the form and in the window alike**, per part, before any file is written:

- the part is **modified in SolidWorks and not saved**: its own `GetSaveFlag`, read on the part's document object as
  the job reaches it. `Session.has_unsaved_changes` (`swcom.py:1161`) reads only the build document, so the job reads
  it once each part is the build document;
- its **globals are not what its record says**: the live `equations()` (`swcom.py:1422`) against the record's
  `variables`, spaces aside, by `swbuild._squash` as K11's `_value_edits` compares them (`swbuild.py:5423-5457`);
- **any feature in the part is in error**: `GetErrorCode2` through `swcom`'s helper (`swcom.py:1083-1095`), over the
  part's features as the build walk reads them (`:2614`, `:2816`). The first revision cited `:900-925`, which is
  `MateState` and `ComponentInfo`.

**A refusal of one part refuses the whole set, and no file is written. Half a set is worse than none.**

**How each part is reached, and what is put back (must-fix M5).** One job on the shared worker, `print_parts`:

1. It first records the active document's title (`Session.active_document`) and every open document's title and save
   flag.
2. For each part, by its path:
   - **open in its own window**: it becomes the build document by `use_open_document` (`swcom.py:3528`), with no
     activation, unless `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` is True, when it is activated by `ActivateDoc3`;
   - **a lightweight component of an open assembly** (its `GetSuppression2` read, no activation): refused by name,
     never opened beside (ruling 2);
   - **open only as a component of an open assembly**: it is reached by `GetOpenDocumentByName` and exported by that
     object, if `STEP_EXPORT_FROM_COMPONENT_ON_<year>` is True. Otherwise it is opened in its own window by
     `Session.open_document` (`:3541`, which activates), if `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>` is True.
     Otherwise the press refuses it, by name, before anything is written;
   - **not open**: `Session.open_document`, which activates.
3. All three reads above are made on each part before any part is exported. Then each is exported to its file in the
   press's folder.
4. **It closes only what it opened**, by `CloseDoc` on the part's title, never an assembly, and never a document
   the user had open.
5. At the end, in a `finally`, it activates the document that was active at the start, if it is still open, and reads
   every open document's save flag again. A flag the job turned on is a failure said in the result. It is never
   saved over.

**Machined parts** are exported too, when the Box says Machined. The list marks each: *machined: its backlash is a
cutter's, 0.3 × module, not a printer's; no span* (E4).

**The files' place: a folder per press (must-fix M3; the coordinating session's ruling, 2026-11-18, the user's to
overrule).**

- Each press of **Print files** writes into its own new folder inside the Output folder's `print` folder:
  `<Output folder>\print\2026-11-18 14.32.05\`, named by the press's date and time. If that name exists, a counter
  goes on it: `2026-11-18 14.32.05 (2)`.
- The app makes `print` and the press's folder before the first file.
- The folder holds that press's `.step` files, named by each part's stem (`Gear_m1.25_N29_P.step`), and its list,
  `print list.txt`.
- Nothing is ever overwritten, and **`_r2` keeps meaning only a part's second revision**: a part
  `Gear_m1.5_N20_P_r2.SLDPRT` prints as `Gear_m1.5_N20_P_r2.step`, and nothing else carries `_r2`.
- The Output folder is the Box's (or the strip's when the Box has none) in the window, and the strip's Output folder
  on the form.

**A set that fails its file check (§3.1.4)** after export keeps its files where they are, since they are the app's
own. Its `print list.txt` is still written, and opens with *DO NOT PRINT THIS SET:* and the file and the reason, so
the folder never stands without a word.

**The print list** is plain UTF-8 text, written by the app after every file's check. It holds:

- a head: the gearbox's name, the time, the app's version, the process and the nozzle;
- one block per part:
  - the file, the rows it serves (*Sun, Planet ×3*), and **how many to print**: one per row it serves, times a
    planet's copies (Shafts' *Copies*);
  - module, teeth, face, bore, backlash (*0.3, printed default*);
  - for a printed involute part, **span over k teeth** and k (§3.0); *no span* for a machined one, *not one figure*
    for an arcs part;
  - the user's features left in the part, by name;
- the settings, said once, as §3.2 gives them to the user:
  - flat on the bed, on the face the part was built from;
  - 0.2 mm layers; five walls; 35 % infill or more;
  - the first layer's squish taken off by the slicer's own setting (0.15 mm);
  - X-Y compensation for holes and contours 0, since the app's backlash already allows for the walls;
  - seam aligned, and each print measured away from the tooth that carries the seam;
  - Bambu Studio's mesh precision on import left at its default;
  - grease on the running teeth.

On the form the list is the same with one block.

#### 3.1.4 Checking a file without opening it (must-fix M2)

Each file is read back as text, never opened in SolidWorks (§3.1.1). The schema and the unit are not version facts:
the AP is the user's *Tools > Options > Export* setting, and the unit follows the document. So the check pins
nothing from the probe's session.

**It passes a file that has all of these:**

- the frame: it begins `ISO-10303-21;` and ends `END-ISO-10303-21;`;
- a `FILE_SCHEMA` among AP203 (`CONFIG_CONTROL_DESIGN`), AP214 (`AUTOMOTIVE_DESIGN`) and AP242
  (`AP242_MANAGED_MODEL_BASED_3D_ENGINEERING`);
- **exactly one** entity instance `= MANIFOLD_SOLID_BREP(`, counted as instances and not substrings, at least one
  `CLOSED_SHELL`, and no `OPEN_SHELL` and no `SHELL_BASED_SURFACE_MODEL`;
- a length unit it can read: an `SI_UNIT` of metres with or without a prefix, or a `CONVERSION_BASED_UNIT` it knows
  (inch, foot). Millimetre is expected; Bambu Studio reads the others.

**It refuses**, naming the file and the reason:

- a broken frame;
- any other schema (AP209, an IGES-in-STEP, an unknown one);
- no solid, more than one solid, an open shell or a surface model;
- a unit it cannot read.

The schema and the unit written are logged in the result as facts. **No finding records them**, so the first
revision's `STEP_FILE_CHECK` is withdrawn.

**What the frame check cannot see, and a cheap check that can** (a should-fix, built if step 3 bears it out):

- One closed solid of the wrong shape would pass the frame check: another document's part (the activation
  question), a part as it was before an unsaved change, a scale or unit slip, or a body with a cut missing.
- So, from the `VERTEX_POINT`s' coordinates in the file's unit, the check also requires the largest radius from the
  part's axis to be the part's outer radius (`d_a / 2`; a ring's or sleeve's rim radius), and the axial extent to be
  its face width, each to 0.01 mm. The build's frame is the app's own: the axis on Z, the face from the Front plane.
- It is skipped, and said to be, for a bevel gear, and wherever step 3 shows the vertices do not give these extents
  on its two parts.

The solid's volume is not read: that needs a STEP reader the app does not have. §3.2's slicer step is where the user
sees the solid.

### 3.2 What you print and measure (the user's step)

This is the part of F2 only you can do. It tells the app how much your printer adds to a printed tooth, and which
bore fits your shaft. Nothing needs a rig, and no gear has to run. Allow about two hours of printing (two and a half
with the optional fifth gear) and half an hour of measuring.

**What you need.**

- Your Bambu printer with a 0.4 mm nozzle, PLA, and Bambu Studio.
- Calipers that read to 0.01 mm. Digital ones are fine.
- One length of the shaft you mean to use. Measure its diameter at three places and write down the smallest
  reading, for example 8.00.

**1. Make the parts in the app.**

On the form, choose *Single gear*, *Spur*, *Involute*, Process **Printed**, and Nozzle 0.4 (or yours). Then type:

- Module **1.5**, Teeth **20**, Face width **8**, Pressure angle 20, Backlash and Fillet left blank;
- Bore: your shaft's diameter plus **0.0**, for example 8.0;
- Name: **Coupon_A**.

Press **Build**. Then, with the part open and active in SolidWorks (the SolidWorks bar names the file **Print
files** will write), press **Print files**. Do the same three more times, changing only the Bore and the Name:

| Name | Bore |
|---|---|
| Coupon_A | shaft + 0.0 |
| Coupon_B | shaft + 0.1 |
| Coupon_C | shaft + 0.2 |
| Coupon_D | shaft + 0.3 |

- Each name has to be typed, because a gear's default name does not include its bore.
- Keep the Derived panel's **Span over 3 teeth** figure. With the printed default it should read 11.209.
- If your shaft is over 18 mm, use Module 2 and Teeth 30 for all four instead. The panel then gives its own span
  (k = 4, 21.223 mm).

*Optional, recommended:* a fifth gear, **Coupon_E**: Module **2**, Teeth **30**, Face **8**, no bore. A single size
cannot tell a fixed flank growth from PLA's shrink, which grows with the part (a few tenths of a per cent, about
0.02 mm a flank across 11 mm). Two sizes can. It adds about twenty minutes of printing.

- **If your shaft is over 18 mm**, your four coupons are already Module 2, Teeth 30, so Coupon_E is the other size:
  Module **1.5**, Teeth **20**, Face **8**, no bore. Its span is then over 3 teeth (11.209 mm), and the four coupons'
  over 4 (21.223 mm). Printed at the same size as the others it would measure nothing new.

**Where the files are.** Each press of **Print files** makes a new folder inside the `print` folder of the Output
folder you built into, named by the date and time of the press, for example `print\2026-11-19 10.05.12`. It holds
the `.step` file and `print list.txt`, which repeats these settings and the span.

**2. Slice them in Bambu Studio.** Open the four (or five) `.step` files.

- *Opening them in Bambu Studio is itself a check this stage asks of you: say if it refuses them.*
- If it asks about mesh precision or tolerance on import, keep its default. A coarser mesh lays straight chords
  inside the curved flanks and makes the gear measure small.

Lay each flat on its face. Then set these, under the names this plan reads them by. They are not checked against
your version; if a name differs, the setting described is the one meant:

- **Layer height** 0.2 mm;
- **Wall loops** 5;
- **Sparse infill density** 35 %;
- **Elephant foot compensation** 0.15 mm;
- **X-Y hole compensation** 0 and **X-Y contour compensation** 0, so that what you measure is the printer and the
  app, not a correction on top;
- **Seam position**: Aligned. Note which tooth the seam is on (a faint vertical line), and measure away from it;
- no brim, no supports;
- your usual PLA filament profile.

Print them all on one plate and let them cool on the plate.

**3. Measure the span over 3 teeth**, on each gear (span over 4 on the m 2, z 30 gear).

- Zero the calipers first. Close them the same light way each time, with the thumb roller, not by squeezing the
  jaws.
- Lay the flat outside jaws across three teeth, one jaw on the outer flank of the first tooth and one on the outer
  flank of the third. The jaws touch the flanks about halfway up the teeth, not the tips and not the roots.
- Hold the calipers square to the gear's axis, at mid-face, not at the bed face, where the first layer spreads.
  These are spur gears. On a helical gear the calipers would tilt with the teeth.
- Rock them gently and take the **smallest steady reading**.
- Do this at three places round the gear, about a third of a turn apart, none across the seam's tooth.

That is twelve readings for the four coupons. Any reading more than 0.05 mm off the others is taken again. The
figure that counts is **the mean of the twelve**.

**4. Try your shaft in each bore**, from the **top face** and again from the **bed face**, where the first layer
narrows the hole. For each coupon and each face, write down one of:

- (a) it does not go in;
- (b) it goes in with a firm push and does not wobble;
- (c) it slides in by hand with no play you can feel;
- (d) it is loose.

Then measure each bore with the inside jaws, at two places a quarter turn apart.

*If all four are (a)*: small printed holes often come out 0.1 to 0.3 mm under size, which is the writer's
understanding and not measured. Print four more at shaft + 0.4, + 0.5, + 0.6 and + 0.7. *If all four are (d)*:
print shaft − 0.1 and below.

A round bore says nothing about F3's D-flat, whose flat is a straight wall. That is measured when F3 builds one.

**5. Optionally,** measure each gear's outside diameter at three places (the panel says 33.0 for module 1.5, 20
teeth) and its face width (8.0).

**6. Type and send the numbers.**

- Type **the mean of the twelve** into the form's **Measured** box under *Span over 3 teeth*, with the same gear on
  the form. The app says how much your printer adds to each flank, the mean less 11.209, halved, and the backlash
  that would keep D3's running play.
- Then send the coordinating session:
  - the twelve readings, and Coupon_E's three if you printed it;
  - for each coupon, the bore typed, the bore measured, and the two fit grades (top and bed face);
  - the optional diameters;
  - **what you printed with**: the printer, the filament (brand, colour), Bambu Studio's version, the nozzle, and
    any setting not as listed.

  They are written into the table below.

**What is done with them (the user's word on each, U4).**

- **D3's printed backlash.**
  - From what your printer adds per flank, `e`, the backlash that keeps D3's 0.04 mm a flank of running play is
    `j = 2 (e + 0.04) / cos α_n` (cos 20° for these coupons). It is never less than 0.1 mm (§3.0's floor). 0.3 mm
    stays if `e` is about 0.10 mm.
  - **A choice to make with your numbers:** if `j` comes out above 0.3 mm, it is more than today's `0.3 × module`
    for every gear under module `j / 0.3` (module 1.13 for `j = 0.34`). Then either the cap stays and those small
    gears keep the smaller figure (the equation's breakpoint moves to `"Module" <= j / 0.3` with its constant to
    `j`), or the cap goes and they take `j`, at the cost of thinner tips, which can come to a point at the smallest
    modules. That is the point of D3's *never more than today's*, and it is yours to decide.
  - With Coupon_E, the session separates a fixed flank growth from a growth with size, and sets `j` from the fixed
    part.
- **F3's bore allowance.**
  - The coupon graded (c) from both faces sets it. If two are (c), the smaller is taken. If none is (c), the
    allowance is between the last (b) and the first (d). If the faces differ, the bed face's grade decides, since
    the shaft must pass it.

**7. Optionally, a pair.** If you have a place to run one on your own shafts, print a pair from the app and turn it
by hand through whole turns, before and after a short run. It confirms step 3; it does not replace it.

**Measured (filled in when you report):**

| | Coupon_A | Coupon_B | Coupon_C | Coupon_D | Coupon_E (optional) |
|---|---|---|---|---|---|
| Bore typed (mm) | | | | | none |
| Bore measured (mm, two readings) | | | | | |
| Shaft fit, top face / bed face (a–d) | | | | | |
| Span over 3 teeth (mm, three readings; over 4 on E) | | | | | |
| Outside diameter (optional) | | | | | |

Printed with: printer ___, filament ___, Bambu Studio ___, nozzle ___, settings not as listed ___.

### 3.3 F2, ready to execute

**F2-0, the interface and the probe** (one agent, first, alone; the interface reviewed before A, B and C start).

The interface note is `docs/notes-printed/F2-INTERFACES.md`. Every name below is importable from its commit, with
stubs that return neutral values.

- **`gears/span.py`** (A's): `span(derived, recipe) -> SpanReading`.
  - `SpanReading(kind: str, k: int, w_mm: float, w_t_mm: float, contact_d: float, needed_face_mm: float)`.
  - `kind` is one of `"span"`, `"arcs"`, `"narrow_face"`, `"no_contact"` and `"none"` (a ring, sleeve, bevel gear
    or machined gear). The figures are 0 unless `kind` is `"span"`; `needed_face_mm` is set for `"narrow_face"`.
  - `contact_d` is `2 r_c` by §3.0's helical-correct radius.
  - The stub returns `"none"`.
- **`printout.py`** (B's): pure planning, which returns **structure, never a sentence a user reads**.
  - `form_print(sidecar: Sidecar, part_path: str, output_folder: str, version: SolidWorksVersion) -> PrintPlan`.
  - `workbook_print(record: LinkRecord, assessment: Assessment, update_plan: UpdatePlan, output_folder: str,
    version: SolidWorksVersion) -> PrintPlan`.
  - `PrintPlan(refusal: Optional[Refusal], parts: Tuple[PrintPart, ...], folder: str)`.
    - `folder` is the press's own new folder, by M3's rule, chosen at plan time and made in the job.
    - `PrintPart(path, stem, rows: Tuple[str, ...], count: int, process: str, span: SpanReading, user_features:
      Tuple[str, ...], spec: GearSpec)`.
  - `Refusal(code: str, parts: Tuple[str, ...], detail: Mapping[str, str])`, its `code` one of:
    - planning: `GATE`, `GATE_COPY`, `UNSAVED_MARK`, `MISMATCHED_MARK`, `CHANGES_ON_UPDATE`, `NO_PART`,
      `WORKBOOK_ERROR`, `FOREIGN_RECORD`, `NO_RECORD` (the form: no `.gear.json`), `NOT_A_PART`;
    - job: `MODIFIED`, `GLOBALS_DIFFER` (`detail`: name, live, recorded), `FEATURE_IN_ERROR` (`detail`: feature
      names), `COMPONENT_ONLY`, `SOLIDWORKS_REFUSED` (`detail`: SolidWorks' codes), `FILE_CHECK` (`detail`: file,
      reason code from §3.1.4).
  - `check_step(text: str, part: PrintPart) -> Optional[str]`: None when the file passes, else a reason code
    (`FRAME`, `SCHEMA`, `SOLIDS`, `OPEN_SHELL`, `SURFACE_MODEL`, `UNIT`, `EXTENT`), with the schema and unit read
    as facts beside it.
  - `write_list(result: PrintResult, text: str) -> str` writes `print list.txt` into the press's folder, never over
    a file, and returns its path.
- **In `swcom.Session`** (B's): `export_step(path: str) -> Tuple[int, int]`.
  - It exports the current build document by `SaveAs` with `SAVE_AS_SILENT | SAVE_AS_COPY`, refuses a path that
    exists, and returns SolidWorks' `(errors, warnings)`.
  - It raises `SolidWorksError` with SolidWorks' codes in its fields, not a sentence for the user.
  - The stub raises.
  - Also `document_by_path(path) -> Optional[Any]` (`GetOpenDocumentByName`) and `save_flags() -> Dict[str, bool]`
    (exists, `swcom.py:3838`).
- **In `swbuild`** (B's): `print_parts(sw, plan: PrintPlan) -> PrintResult`, the job of §3.1.3's *How each part is
  reached*.
  - `PrintResult(written: Tuple[Tuple[str, str], ...], folder: str, refusal: Optional[Refusal], failed:
    Tuple[Tuple[str, str], ...], facts: Mapping[str, str], active_restored: bool, flags_turned_on: Tuple[str,
    ...])`.
  - `written` is part path and file; `failed` is file and reason code.
- **In `ui_text`** (C's): every sentence a user reads.
  - `span_rows(reading: SpanReading, measured: Optional[float], alpha_n: float, module: float) -> List[Tuple[str,
    str]]`;
  - `print_refusal(refusal: Refusal) -> str`;
  - `print_result(result: PrintResult) -> str`;
  - `print_list_text(plan: PrintPlan, result: PrintResult, version: str) -> str`;
  - `print_bar_line(...)` for the SolidWorks bar.
  - The stubs return `""`. **Package C owns these words**, and package B hands it the structure above, as W9's
    packages did (must-fix M4). The interface note gives every code's sentence once, so C writes to it and B's tests
    do not read words.
- **The gate is checked twice, both by B.**
  - In planning, `form_print` and `workbook_print` return `GATE` (or `GATE_COPY`) for the connected version from
    the snapshot, so the press refuses before a job.
  - In the job, `print_parts` reads the session's revision and returns the same refusal before any document is
    touched, if the version is not gated or the session changed since the plan.
  - C only words it.
- **In `findings`** (F2-0's): `SAVE_AS_COPY`, `STEP_EXPORT_ON_2026`, `STEP_EXPORT_ON_2024`,
  `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>`, `STEP_EXPORT_FROM_COMPONENT_ON_<year>` and
  `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>`, all None. There is no `STEP_FILE_CHECK` (M2).
- **The probe** of §3.1.2, `probe/f2_probes.py`, with its self-check and note. It is run on 2026, then on 2024, in
  fresh sessions, with one follow-up round per version if a reviewer asks it. It is reviewed by a subagent, and its
  findings are then set in `findings.py` with `tests/test_findings.py`'s pins, in a commit of its own that is
  reviewed too.

F2-0's files: `docs/notes-printed/F2-INTERFACES.md`, `docs/notes-printed/F2-PROBES.md`, `probe/f2_probes.py`,
`src/gear_generator/findings.py`, `tests/test_findings.py`, and the stubs' lines in `gears/span.py` (new),
`printout.py` (new), `swcom.py`, `swbuild.py` and `ui_text.py`.

**Then three packages, each owning its files outright, disjoint in `src` and in `tests`:**

- **A, the span** (pure). It starts once the interface is reviewed, before the probe has run.
  - Files: `gears/span.py`, and a new `tests/test_span.py` with everything §3.0 lists, its check against the drawn
    outline included.
- **B, the export.** It starts with A. Its job runs only against the fake until the findings are set.
  - Files: `printout.py`, `swcom.py` (`export_step`, `document_by_path`), `swbuild.py` (`print_parts`).
  - Tests: a new `tests/test_printout.py`. It covers each refusal code; E3's layout-only change not refusing; the
    count with planet copies; the folder per press and its counter; that a part `…_r2` prints as `…_r2.step` and
    nothing else gains `_r2`; the list never overwritten; and `check_step` on made-up texts of each schema, unit and
    fault.
  - Also a new `tests/test_swbuild_print.py`: each way a part is reached, the gate in the job, closing only what was
    opened, the active document put back, and a save flag turned on said.
  - In `tests/test_swbuild.py`, the fake `FakeSolidWorks` gains `export_step`, `document_by_path` and the reads
    they need, as its only edit there. `tests/test_swcom.py` covers `export_step` on `FakeSession`.
- **C, what the user sees.** It starts with A and B, the board first.
  - Files: `gui.py` (the span row, the Measured entry, **Print files** in the footer, the SolidWorks bar's line, the
    job and its finish), `ui_text.py` (every sentence of the interface, the explainer, the list's text),
    `workbook_gui.py` (the footer's fifth button, its planning read and finish, `write_list` called there),
    `design/` (the form with the span row and a reading typed; the window's footer with five buttons at 1080 px, the
    sentence keeping its 400 px; one refusal), `design/UI-DESIGN.md` and `README.md`.
  - Tests: `tests/test_ui_text.py` (each code's sentence, the Measured line's floor, `cos α_n` and the line past
    `0.3 × module`, recipe B's words, the list's text for each kind of part), and new `tests/test_print_form.py` and
    `tests/test_print_window.py`.

B's `printout` calls A's `span`. C words what B and A return. Each meets the others through F2-0's names only.

**What must not move.**

- F1's pins: `tests/test_printed_rule.py` whole, which holds the machined Derived panel among the rest, and F1's
  tests.
- W9's pins: `BEFORE_W7`, `BEFORE_W8`, the W8 and W9 fixtures' counts, and every W9 test against the fake.
- `tests/test_findings.py`'s existing values and log lines; F2 only adds.
- No SolidWorks call changes but the new export and its reads: no build, Update or Build again… path changes.
- The machined Derived panel and every machined record. The workbook's own Export and Export as… are unchanged.

**The SolidWorks demonstration**, `probe/f2_demonstration.py`, on W9a's harness as F1's was.

- `form`: from the strip's own form, a printed spur gear built and **Print files** pressed.
  - The file is checked by the app and by the script, which reads the part's path, title and save flag unchanged,
    the active document put back, and the list.
  - Then one global changed in SolidWorks, unsaved: refused. Saved but not the record's: refused.
  - After Update values, a second press makes a second folder.
- `workbook`: the 12 : 1 reducer fixture, printed and built.
  - With its assembly open and the parts' own windows closed, the component case: **Print files** writes every part
    and the list, with the counts.
  - Then one Gears cell edited: refused until Update SolidWorks. Updated and not saved: refused. Saved: a second
    folder.
- About 15 minutes on 2026, and 25 on 2024 as the confirming build, each in a fresh session.

**Done when:**

- §3.0's span shows on the form for a printed involute external gear, with its Measured line, and is held by its
  tests.
- The interface has been reviewed.
- The probe has run on 2026 and 2024 and been reviewed, and its findings are set in `findings.py` with their pins,
  that commit reviewed.
- **Print files** exports from the form and from the Workbook window against the fake, each refusal said, the files
  checked, the list written, and the open documents left as they were.
- The boards, `design/UI-DESIGN.md` and `README.md` are updated.
- The demonstration has run on 2026 and on 2024, every section clean, and been reviewed.
- The coupons are exported, and the STEP files open in the user's Bambu Studio (the user's step, §3.2 step 2).
- The measurements of §3.2 are in its table, and D3's number and F3's allowance are set from them, on the user's
  word.
- The stage's result is reviewed by a subagent, and its should-fixes are done.

The code can close before the user's measurements are in; the stage closes with them.

**Cost**, restated as the review has it: **thirteen to fifteen agent runs**.

- F2-0's interface and probe script (1), the interface's review (1);
- the probe's runs on both versions (1), a follow-up round if asked (0 or 1), its review (1), the findings commit's
  review (1);
- the three packages (3);
- the stage review (1) and its should-fix round (1);
- the demonstration's script and runs (1 or 2), and its review (1).

**About 90 SolidWorks minutes** in five or six fresh sessions: the probe about 12 minutes on 2026 and 18 on 2024, a
follow-up round about 10 and 15, the demonstration about 15 and 25. The first revision's 65 minutes is the floor,
with no follow-up round.

### 3.4 The decisions F2 needs

**Ruled by the coordinating session, the user's to overrule:**

- **M3, repeat presses.** A new folder per press, by date and time with a counter, inside the Output folder's
  `print` folder; `_r2` only ever a part's revision (§3.1.3).

**Ruled in this revision, the user's to overrule:**

- **A gear drawn with arcs** shows no span figure, with one line saying why and to choose Involute to measure
  (§3.0).
- **Probe step 8 dropped** (a part in error), written as a caveat; *for the coordinating session to confirm*
  (§3.1.2).
- **E3 refined:** a change Update would make only to the layout or the assembly does not refuse a print.

**Standing on an assumed answer, so the code can go ahead:**

- **E1. Which gears show the span:** printed external spur, helical and herringbone gears, dogs and hubs, on the
  involute recipe; never a machined gear (the list says *no span* for one).
- **E2. The Measured entry** on the form, not saved, with its floor of 0.1 mm a gear.
- **E3. Refusals:** a part unsaved or mismatched, one whose globals differ from its record, one in error, one Update
  would change or make new, and a part reachable only in a way not measured. A whole print set or nothing.
- **E4. Machined parts are exported**, each marked in the list. Refusing them would be one line.
- **E5. The button's name**, **Print files**, with no ellipsis since it asks nothing, in the form's footer and the
  window's footer.
- **E6. The files:** `.step`, each part's stem, `print list.txt` in UTF-8, a failed set's list headed *DO NOT PRINT
  THIS SET*.
- **E7. The slicer settings in the list and in §3.2**, from *Sources*. Bambu Studio's names are read, not checked.

**Needing the user, but not before code:**

- **U1.** Their shaft's diameter, and whether it is under 18 mm (§3.2's coupon module).
- **U2.** Their printer, its nozzle (0.4 assumed) and their PLA.
- **U3.** That they have calipers reading 0.01 mm.
- **U4.** After §3.2, D3's printed backlash and F3's bore allowance, from their numbers. This includes, plainly:
  **if their printer needs more than 0.3 mm, whether gears under module `j / 0.3` keep today's smaller `0.3 ×
  module` (D3's *never more than today's* kept, the breakpoint moved) or take the measured backlash (thinner tips,
  a point at the smallest modules)** (§3.2).
- **U5.** That Bambu Studio opens the files (§3.2 step 2).

**Needing the user before code: none.** The coordinating session may still put E4 and E5, and the arcs ruling, to
them, since each is something they will see.


## 4. Stage F3 — the bore (existing ops only)

Read against the code at `f28cb75` on `printed` (F1 closed, F2 closed short of §3.2). Lines below are as of that
commit. §4.1 to §4.5 say what F3 builds and why; §4.6 makes it ready to execute.

### 4.1 Bore allowance

A printed bore is cut at `"Bore Diameter" + "Bore Allowance"`, so `"Bore Diameter"` stays the shaft's size.

**What it builds.** Today's bore (`spur._bore_ops`, `gears/spur.py:1447-1457`) is one sketch on the Front plane:

- `OpenSketch`, `Circle` centred by `Relation("coincident", (centre, origin))`, `Dimension("Bore")`, `CloseSketch`;
- `Cut` through all;
- `LinkDimension("Bore@Bore Sketch", "Bore Diameter")`.

With an allowance, two things change. The part gains a global `AddGlobal("Bore Allowance", <literal>)`, and the link
becomes `LinkDimension("Bore@Bore Sketch", '"Bore Diameter" + "Bore Allowance"')`. Nothing else in the sketch or
the cut changes.

- **Every SolidWorks call here is one the app already makes**, on both versions:
  - `CreateCircleByRadius` (`swcom.py:1737`), `SketchAddConstraints` (`:1875`), `AddDimension2` (`:1902`),
    `FeatureCut4` (`:1966`);
  - the Equation Manager's `Add2` (`:1425`) for the global and for the link.
  - A dimension linked to an expression of two globals is made today: W9b's relief planes, `"Face Width" - "End
    Band"` (`gears/clutch.py:82`), and the bevel's blank (`bevel.py:881-893`).
  - **No probe.** The full build comes first, by the house rule, and F3's first SolidWorks run is its measurement.
- **The global exists only when the allowance is not zero**, as `"Profile Shift"` does. So going between none and
  some is structural (`swbuild.structural_change` gains `has_allowance` beside `has_shift`, `swbuild.py:1333`). A
  change of size is a value, which Update carries in place.
- **A helical or herringbone gear** takes it through the same ops (`helical._bore_ops` calls `spur._bore_ops`,
  `helical.py:417-418`), and so do a dog and a hub (`clutch._as_spur`).
- **A bevel gear's bore** is not a cut. It is the inner edge of the revolved blank, its two lines driven by
  expressions in `"Bore Diameter" / 2` (`bevel.py:881-893`). There the allowance replaces `"Bore Diameter"` with
  `( "Bore Diameter" + "Bore Allowance" )` in those expressions, a text change and no new op.
- **A ring and a sleeve** have no bore (`internal.py:972`, `:1026`) and take none.
- **Checks.** The bore check (`spur.py:913-916`), the one-module rim (`:963-972`) and F1's printed rim
  (`:1025-1028`) are made on the bore as cut, `Bore + allowance`.

**Which gears take it, and the default.**

- **Printed, a blank Bore allowance is the default.** That is **0.2 mm on the diameter**, a placeholder until §3.2's
  coupon gives the user's figure (U4).
- **Machined, a blank is 0**, so a machined part builds and records exactly as today, by the rule.
- **A typed allowance is honoured on either**: it is the user's explicit choice, and it moves no machined default.

**The placeholder replaced without rebuilding anything the user did not ask for: a blank allowance is *as built*.**
This is the same principle as D11's (B).

- For a part **not yet built**, a blank Bore allowance is the current default.
- For a part **on record**, a blank is the figure the part was built with, read from its recorded globals
  (`"Bore Allowance"`'s literal in the record's `variables`, or 0 when the part has no such global, as every part
  built before F3 has none).
- So when the default later moves from 0.2 to the user's figure, nothing already built reads as changed, and
  neither Update nor Build again… writes to it. A part takes the new figure when it is new, or when the user types
  the figure in its cell.
- The rule lives in one function, `gearbox.as_built_allowance(entry) -> Optional[float]`, used where planning turns
  a row into a spec for a part on record (the workbook's `gearbox` planning; the strip's `_update_target` for an
  opened record).
- **The figure itself** is one constant, `spur.BORE_ALLOWANCE_DEFAULT = 0.2`. Changing it is a one-line change and
  its pins, as the review of F2's runs says (`F2-DEMONSTRATION-RUNS-REVIEW.md` §5).

**Parts built before F3** have no allowance and no key for it. They read as allowance 0 by §1.1's rule, and as built
by the rule above, so each stays a true record of what it is. That includes §3.2's coupons, whose bores the user
typed in full. Giving such a part an allowance is a new part (none to some): Build again… in a workbook, or a new
name on the strip.

### 4.2 D-flat

`Drive` is `round` (the default) or `flat`. `Flat` is the shaft's size across its flat, measured from the flat to
the opposite round side.

**What it builds.** With Drive flat, the bore sketch is a D: a **major arc** and a **chord**, cut through all, where
today it is a circle.

- `OpenSketch("bore", 1)`.
- `Arc("bore_arc", origin, start, end)`: the major arc, its ends at the chord's ends.
- `Line("bore_flat", start, end)`: the chord, horizontal, on the +Y side.
- Relations:
  - `Relation("coincident", ("bore_arc.centre", ORIGIN))`;
  - the arc's two ends coincident with the line's;
  - `Relation("horizontal", ("bore_flat",))`.
- Dimensions:
  - `Dimension("Bore", ("bore_arc",))`: an arc's radius, linked to `( "Bore Diameter" + "Bore Allowance" ) / 2`;
  - `Dimension("Flat", ("bore_flat",))`: the chord's length, linked to `2 * sqr ( R * R - h * h )`, where
    `R = ( "Bore Diameter" + "Bore Allowance" ) / 2` and `h = "Bore Flat" - "Bore Diameter" / 2 + "Bore Allowance"
    / 2`. `h` is the flat's distance from the axis: the shaft's `Flat − D/2`, plus half the allowance, so the flat
    takes half the allowance on its wall, as the round does.
- `CloseSketch`, `Cut` through all, and the global `"Bore Flat"`.

The sketch is fully defined by these, the arc centred, the chord horizontal, its length fixing its height. The
build reads it with the sketch status it reads today (`GetConstrainedStatus`, `swcom.py:1726`).

- **Every op is one the app has**, and so is every call: `CreateArc` (`:1747`), `CreateLine` (`:1756`),
  `SketchAddConstraints` for coincident and horizontal, `AddDimension2` on an arc (a radius, as the fillet's,
  `spur.py:1368`) and on a line (a length, as the bevel's `Back` and `Front`, `bevel.py:911-912`), `FeatureCut4`, and
  links with `sqr` (the app's guarded `sqr` beside its comment that SolidWorks 2026 refuses `sqr ( 0 )`,
  `spur.py:1158`). Here `R * R - h * h` is never 0: the Flat check below keeps `h < R`.
- **Two things in it are new in kind though not in call:**
  - a **major** arc (every arc the app has drawn is under a half turn, by its sketches' shapes);
  - an arc's ends meeting a line's ends where the line is drawn starting on the arc's end. The macro database's
    `GOTCHAS.md` §35 says such a point is shared, and the coincident is then skipped, as the app's tooth sketches
    already do.
- Neither is a call that could hang, raise a dialog or damage a file, so by the house rule **the full build is the
  measurement** and no probe comes first. If F3's first build shows either wrong, that is what gets probed, step by
  step.
- **Changing Drive is structural** (`drive` joins `swbuild.STRUCTURAL`, `swbuild.py:1305`, a missing key read as
  `round`). A change of Flat is a value.
- **Checks**, errors at the Flat cell:
  - Flat not more than half the bore (the flat would pass the axis);
  - Flat not less than the bore (no flat);
  - Drive flat with no Bore;
  - Drive flat on a **bevel gear**, whose bore is the revolved blank's edge and cannot take a flat with existing ops
    (G5). Its sentence says to use a round bore or a hub row.

  The rim check is unchanged: the thinnest wall is at the round part, never at the flat.
- **The flat's place** is on +Y in the part's own frame, square to the Front plane's Y. No angle to a tooth is set
  (G6).

### 4.3 The record: link schema 12, sidecar 4

- **The link record goes to 12, whatever its parts**, as F1's 11 was: one policy, the number set by the app that
  writes it (`store.LINK_SCHEMA_VERSION`, `store.py:426-432`, with `_F1_LINK_SCHEMA = 11` kept beside it).
- **A `.gear.json` goes to sidecar 4** (`BORE_SCHEMA`) when its part has the allowance global or a flat. Every other
  part keeps its number: 1, 2 or 3 by `store.sidecar_schema` (`:91`). A machined part with a blank allowance and a
  round bore is byte for byte what F2 writes.
- **The spec's three keys**, `bore_allowance`, `drive` and `flat`, are left out of `GearSpec.to_dict` at their
  defaults (blank, `round`, blank), as the bands and F1's keys are. So a missing key is the default, as
  `from_dict` reads it.
- **The derived gear's new fields** (the allowance and the flat, in mm) are left out of the derived `to_dict`s while
  they are 0 and None. This is F1's lesson (§1.1): a derived field in `asdict` goes into every `.gear.json`.
- **An older app.** An F2-era app refuses a link 12 record and a sidecar 4 `.gear.json`, as `store` refuses any
  newer one (§1.2), so it never writes a flat part back as round.
- **Every literal 11 that `git grep` finds at F3-0's base moves to 12**, in F3-0. At `f28cb75` that is fifteen lines
  in seven files:
  - `tests/test_store.py:227`, `:1123`;
  - `tests/test_workbook_bands.py:354`, `:368`;
  - `tests/test_workbook_carry.py:52`, `:76`, `:80`, `:1119`;
  - `tests/test_workbook_user_record.py:56`;
  - `tests/test_workbook_window.py:312`;
  - `tests/test_printed_workbook.py:379`, `:394`, `:440`, `:526`;
  - `tests/test_printed_rule.py:550`.

  `test_store.py:833` parametrises a literal 12 as "newer"; it becomes 13.

### 4.4 What W9 asks of F3

- **K11.** `"Bore Allowance"` → `bore_allowance` and `"Bore Flat"` → `flat` join `update._GLOBAL_COLUMN`
  (`workbook/update.py:670`), so that K11's sentence names their cells, as it names Bore's.
  - A blank allowance's value in that sentence is said as *0.2 (from its blank cell, the allowance as built)*.
  - The set-back is the literal, since the global holds one.
  - K11 reads every planned global already (`swbuild._value_edits`), so no new read.
- **W9d's carry, why a part is new.** `update._SPEC_COLUMNS` (`:3196`) gains *Bore allowance*, *Drive* and *Flat*, so
  a part made new by them says *its Drive changed*.
- **W9d's "bore".** `update._bore_mm` (`:3275`, `CarryBody.bore_mm`) gives **the hole as cut, Bore plus the
  allowance as built**, read from the old part's recorded `"Bore Allowance"`.
  - W9d's word "bore" needs a coaxial cylinder of exactly the recorded radius (to 1e-4 mm, `W9D-INTERFACES.md` §4.4).
    Without this it would never name a printed bore, and a mate on it would be said as on *a face of Sun on its
    axis*.
  - A D-flat's arc face is that cylinder, so it is still "bore". Its flat face is a plane, said as *a face of Sun*.
- **Mates on faces.** A mate of the user's on the bore face of a part made new by its allowance or drive is named,
  not found again, by K5's ruling (no finding by geometric role).
- **The hub (W9b)** is built as a dog's toothed ring with the row's Bore, its fixing left to the user. A hub row
  takes Bore allowance, Drive and Flat as any gear, through `clutch._as_spur` and `spur._bore_ops`: that is its
  fixing. W9b's rule that a hub's teeth, module and pressure angle are its sleeve's is untouched.
- **Update in place (W9c).** No new kind of write. An allowance's or a flat's size is a global set by the Update
  that sets every global. None to some, and a Drive change, are a new part, as a Flank change is.

### 4.5 The edge chamfer is not here (D9)

The first draft put a chamfer on both end faces by selecting each face. The review found the app has never selected
a face or an edge (every selection is a feature, plane or sketch entity by name), so that is new traversal code for
four kinds of end face, not one call. It also found that a chamfer of 0 cannot be a value, and that at module 1 a
0.3 mm chamfer leaves 0.06 to 0.14 mm of tooth near the tip on the bed face. A chamfered blank made by the existing
`Revolve` needs no new call but relieves the tips only, and the squish that binds a mesh is on the flanks. Every
slicer has the setting that deals with it. If the prints of §3.2 show that is not enough, the chamfer gets a plan of
its own.

### 4.6 F3, ready to execute

**F3-0, the interface and the pins** (one agent, first, alone; reviewed before A, B and C start). The note is
`docs/notes-printed/F3-INTERFACES.md`, with every name, signature, sentence and constant below. Everything is
importable from its commit, with stubs that return neutral values, and the whole suite passes there.

1. **The machined pins first, in their own commit.** Pin in `tests/test_printed_rule.py` a new set, at the commit
   F3-0 starts from:
   - a machined part's plan and `.gear.json` with a bore, for a spur, helical, herringbone and bevel gear, a dog and
     a hub;
   - the same for a printed part built before F3 read back by the as-built rule.

   Both must be identical after F3, as F1's pins were.
2. **`spec.py`:**
   - fields `bore_allowance = ""`, `drive = "round"`, `flat = ""` after F1's;
   - readers `bore_allowance_mm(printed: bool, as_built: Optional[float]) -> float`, `drive_value()` and
     `flat_mm()`;
   - `to_dict` leaving each out at its default.
3. **The gears' names:**
   - `spur.BORE_ALLOWANCE = "Bore Allowance"`, `spur.BORE_FLAT = "Bore Flat"` and `spur.BORE_ALLOWANCE_DEFAULT = 0.2`;
   - the derived gear's `bore_allowance: float = 0.0` and `flat: Optional[float] = None` on `SpurDerived` and the
     bevel's `RackSection`, left out of each `to_dict` (four, as §1.1) while 0 and None;
   - `spur._bore_ops`'s signature unchanged.
4. **The workbook's columns.** In `schema.GEARS`, after End band and before Part name, as W9b placed its bands, so no
   earlier column's letter moves:
   - **Bore allowance** (mm; blank *0.2 printed, as built once built; 0 machined*);
   - **Drive** (words `round` and `flat`, blank `round`);
   - **Flat** (mm, blank *none*).

   Also `model.Gear`'s three fields after `end_band` and before `row`, and `Gear.spec_values` passing them. The
   pin of the Gears titles, `tests/test_workbook_model.py:19-23`, moves with them in this commit (F1-0's lesson,
   the Box's titles).
5. **The form's fields.** `gui.GEAR_VARS` (`gui.py:73-90`) gains the three, so `test_gui_spec.py`'s field test stays
   green. Package C gives them their rows.
6. **The record:**
   - `store.LINK_SCHEMA_VERSION = 12` with `_F1_LINK_SCHEMA = 11`;
   - `store.BORE_SCHEMA = 4` and `SCHEMA_VERSION = 4`;
   - `sidecar_schema` giving 4 for a spec with an allowance or a flat;
   - the fifteen literal 11s of §4.3, and any more grep finds, moved; `test_store.py:833`'s 12 to 13.
7. **The as-built rule:** `gearbox.as_built_allowance(entry: Optional[PartEntry]) -> Optional[float]`. The stub
   returns None, read as "the current default".
8. **The words:** every new diagnostic, the structural sentences (*Drive changed from round to flat, which its
   values cannot carry; build it again as a new part.*, and the allowance's none and some), K11's blank allowance,
   the explainers for the three fields, the print list's lines (*bore 8 + 0.2 allowance, D-flat 7.5*), and the
   Derived row *Bore as cut*.

F3-0's files:

- `docs/notes-printed/F3-INTERFACES.md` (new);
- `src/gear_generator/spec.py`, `store.py`;
- the names' lines in `gears/spur.py` and `bevel.py`;
- `workbook/schema.py`, `workbook/model.py`;
- `gui.py` (`GEAR_VARS` only);
- `workbook/gearbox.py` (the stub);
- tests: `tests/test_printed_rule.py`, `tests/test_workbook_model.py`, and the seven files of §4.3's literals
  (`test_store`, `test_workbook_bands`, `test_workbook_carry`, `test_workbook_user_record`, `test_workbook_window`,
  `test_printed_workbook`, `test_printed_rule`).

**Then three packages, each owning its files outright, disjoint in `src` and in `tests`.** All three start as soon
as F3-0's interface is reviewed. None needs SolidWorks or the user.

- **A, the geometry and the checks.**
  - Files: `gears/spur.py` (`_bore_ops` with the allowance and the D, the globals, the checks of §4.1 and §4.2, the
    derived fields), `gears/helical.py` (the bore's globals list, `:426`), `gears/bevel.py` (the allowance in the
    blank's expressions, `:881-893`; Drive flat refused), `gears/clutch.py` (if anything).
  - Tests: `tests/test_gears_spur.py`, `_helical`, `_bevel`, `_clutch`, and a new `tests/test_bore.py`. Each kind's
    plan with an allowance and with a flat, op by op. The D sketch's figures: the chord length for an 8 mm shaft
    with a 7 mm flat and 0.2 allowance, h = 3.1, R = 4.1, chord = 5.367 mm. Each check's sentence; the volume of the
    part against the maths (circle area less the D's); and machined plans unchanged.
- **B, the record, the workbook and Update.**
  - Files: `swbuild.py` (`structural_change`: `drive` in `STRUCTURAL`, `has_allowance` and `has_flat` beside
    `has_shift`; K11's words for a blank allowance), `workbook/update.py` (`_GLOBAL_COLUMN`, `_SPEC_COLUMNS`,
    `_bore_mm` as cut), `workbook/gearbox.py` (`as_built_allowance` and its use in planning), and `printout.py` (the
    block's bore figures handed to C as structure).
  - Tests: a new `tests/test_bore_workbook.py`:
    - the as-built rule (a part built before F3 unchanged; a part built at 0.2 unchanged after the default moves to
      0.25; a new row at 0.25);
    - each structural and value case through `update.classify`;
    - K11's sentence;
    - W9d's `_bore_mm` and `_changed_columns`;
    - a hub row with all three;
    - machined bytes.
    `tests/test_workbook_update.py` and `tests/test_workbook_carry.py` are F3-0's (literals) and A's neither; B adds
    its cases to its new file only.
- **C, what the user sees.**
  - Files: `gui.py` (the three rows under Bore, Flat shown while Drive is Flat), `ui_text.py` (the explainers, the
    Derived row *Bore as cut*, the print list's bore line), `design/` (the form with a D-flat typed; the board
    first), `design/UI-DESIGN.md`, `README.md`.
  - Tests: `tests/test_ui_text.py`, and a new `tests/test_bore_form.py`.

A's diagnostics and B's structural and K11 sentences stay in their own files, as the house has them; C words the
form and the list. Each meets the others through F3-0's names.

**What must not move.**

- **W9's pins:** `BEFORE_W7`, `BEFORE_W8`, the W8 and W9 fixtures' counts, every W9 test against the fake.
- **F1's:** `tests/test_printed_rule.py` whole, with F3-0's new machined pins.
- **F2's:** `tests/test_span.py`, `test_printout.py`, `test_swbuild_print.py`, the findings and their pins.
  - **One exception, by design, listed in F3-0's note:** a printed plan *with a bore* built new after F3 carries the
    allowance. Any F1 or F2 test that pins such a plan, or a print list line naming its bore, is re-taken in F3-0 by
    name, each said why.
  - A machined plan, and a printed part on record, never move.
- **No SolidWorks call** is added or changed.

**The SolidWorks demonstration**, `probe/f3_demonstration.py`, on W9a's harness as F1's and F2's were.

- `bore`: from the strip's own form, printed spur gears with an 8 mm bore:
  - blank allowance (the global 0.2, the link's text);
  - typed 0.3;
  - D-flat with a 7 mm flat.

  Each built, and read by:
  - the sketch status *fully defined* (`GetConstrainedStatus`);
  - its volume against the maths (small_pinion_check's `judge_part`, its expected volume less the D);
  - **the hole measured by F2's own route.** **Print files** is pressed, and its STEP file's `VERTEX_POINT`s give
    the bore's least radius, `(8 + allowance) / 2`, and on the D the flat's distance from the axis, `h`, to 0.01 mm.
- `kinds`: a helical, a herringbone and a bevel gear with an allowance, the bevel's bore read the same way; a D-flat
  on the bevel refused.
- `update`:
  - Update values carries an allowance 0.2 → 0.3 and a Flat 7 → 7.2, each read back in SolidWorks;
  - it refuses Drive round → flat and an allowance going to 0, each with its sentence, and nothing is written.
- `workbook`:
  - RangeBox_Fixed printed, its Hub row with an allowance and a D-flat, built, turned through every mode, with no
    interference read;
  - then a W9a `setup.master` copy, Printed typed: its parts built before F3 read *unchanged* in Bore (the as-built
    rule), nothing written by it.
  - W9d's "bore" on a mate on a printed bore is shown against the fake only. No master holds such a mate, and
    building one is not worth a run. Said as such.
- **Times.** F2's demonstration took about twice its estimate, so these are doubled from F2's measured sections:
  about 35 minutes on 2026 and 55 on 2024, the confirming build, each in a fresh session, and one rerun round of
  about 30 minutes in all.

**Done when:**

- F3-0's interface is reviewed, and F3-0's machined pins are taken and hold.
- Packages A, B and C are in, each with its tests, the suite passing but for the known font-width test.
- On SolidWorks 2026, and again on 2024 as the confirming build, every section of the demonstration is clean. Every
  sketch is fully defined; volumes and the STEP-measured bore agree with the maths to 0.01 mm; Update carries the
  values and refuses the structural changes with their sentences; the workbook gearbox with its hub turns with no
  interference; and a gearbox built before F3 reads unchanged.
- The boards, `design/UI-DESIGN.md` and the README are updated.
- The stage is reviewed by a subagent and its should-fixes are done, the demonstration's runs reviewed too.
- **Not in F3's *Done when*:** the allowance's default from the user's coupon (a one-line change and its pins when
  §3.2's numbers come), and a D-flat coupon's fit (G7).

**Cost**, honest after F2 (which took about twice its first estimate). About **sixteen to twenty agent runs**:

- F3-0 and the interface review (2);
- the three packages (3);
- the stage review, its should-fix round and the re-check (3);
- the demonstration's script, its review, a fix round, the runs and the runs' review (5 to 7);
- the coordinator's hand-over notes and plan records (1 to 2);
- one spare for a probe if the first build shows the major arc or the shared point wrong (0 to 2).

**About 120 SolidWorks minutes** in four or five fresh sessions: 35 on 2026 and 55 on 2024, a rerun round of about
30, more if a probe is needed.

**The decisions F3 needs.**

*Standing on an assumed answer, so the code can go ahead:*

- **G1.** The placeholder default: 0.2 mm on the diameter for a printed bore; 0 for machined; a typed figure
  honoured on either.
- **G2.** A blank allowance is *as built* for a part on record (§4.1), so moving the default rebuilds nothing.
- **G3.** The new Gears columns go after End band and before Part name; the form's rows go under Bore.
- **G4.** None to some allowance, and a Drive change, are a new part. Sizes are values.
- **G5.** A bevel gear takes the allowance but no D-flat in F3.
- **G6.** The flat on +Y in the part's own frame, at no set angle to a tooth; it takes half the allowance on its
  wall.
- **G7.** No D-flat coupon in F3's code. If the user wants one, the form builds it with Drive flat, and its fit is
  graded as §3.2's bores are, as a short follow-on to their step.
- **G8.** The global names `"Bore Allowance"` and `"Bore Flat"`, and a link schema of 12 whatever the parts.

*Needing the user, but not before code:*

- **V1.** The allowance figure from their coupons (U4), replacing 0.2 by one constant and its pins.
- **V2.** Whether their shafts carry a D-flat, and its across-flat size. This is typed per row and needs nothing
  from code.

*Needing the user before code:* **none.**


## 5. Stage F4 — what a tooth can carry

Pure maths, no SolidWorks. **Spur, helical and herringbone gears and rings; not bevel gears**, which
need the virtual gear at the mean cone and are said to be unrated. Nor are a sleeve's couplings to its dogs and
hub, which are splines. To be checked against ISO 6336-3 itself before a line is written (the reviewer and the
writer both have these from memory):

- the critical section is where a 30° tangent meets the root fillet on an outside gear, and a 60° tangent on a
  ring;
- the whole load is taken at the tip of one tooth;
- the stress-correction factor for the fillet is **included**. The app has the radius and section to work it out,
  and it is roughly 1.5 to 2.

The figure is taken from the app's own outline, so backlash and shift are in it.

- **The form:** the tangential force and torque one tooth takes at the allowable, named for what it is: *holds
  about … N·m once, not running*.
- **The workbook:** each Meshes row's **tangential force** (`2 T / d`, the same on both gears) against the weaker
  gear's, in each mode.
  - The torques per shaft are the assessment's own (`report.motion.torques`; in each mode, W8's mode reports), and
    a planetary stage's planets are in `report.stages`.
  - The force is divided among a stage's planets, with an allowance for uneven sharing.
  - An idler, whose teeth bend both ways, is held to 0.7 of the figure.
  - A warning goes at the row, and the share used on the Results sheet (`workbook/export.py`).
  - The Box gets a setting `Allowable stress`, beside Process and Nozzle.

Every sentence says what it does not cover. It is a static figure for a tooth printed flat, bending
within its layers. A helical tooth's side load and any load across layers meet the weaker bond between
them, and are not derated. A gear that runs for long fails first by heat (PLA softens near 55 to
60 °C), by wear, or by creep at its bore; none is worked out.

**Done when:** hand-worked cases are pinned in the suite, among them a gear thinned by backlash
carrying less than the same gear without, and a ring; reviewed. **Cost:** two agent runs and the
review; no SolidWorks.


## 6. What W9 left, and what F1 to F4 do with it (D8)

W9 went first and was planned as if this plan were not there. It is read here at `c2d95cc`. Item by item, in place
of the first revision's forward-looking sentences:

- **W9's pinned results do not move.**
  - F1 keeps them by §1's default: every fixture W9 built in code is machined without an edit, and the three
    five Excel- or LibreOffice-saved workbooks are marked machined as read in F1-0, in the ten files that read them
    (§2.7).
  - Every new check is for printed gears. No pair interference check is built (§2.3), so W7's planetary sentence
    and W9's warning counts are untouched by it.
  - F1 adds no finding and changes no SolidWorks call, so `findings.py` and `tests/test_findings.py`, with
    W9c's and W9d's 2024 gates, are untouched.
- **W9 took link schemas 7, 8, 9 and 10 and sidecar schema 2** (`store.py:421-426`, `:30-35`). F1 takes link 11
  and sidecar 3, and F3 takes 12 and 4, each link number whatever the parts (§1.2, §4.1). An older app's refusal is
  read and holds (§1.2).
- **The record's shapes grew in W9.** It now holds the user-work inventory (7), bands in a sleeve's spec (8), what a
  stopped press left (`GearboxRecord.left`, 9) and the carry (10). F1 adds nothing to any of them: `process` and
  `nozzle` ride in a part's `spec` as the bands do, and are left out when machined.
- **Gearboxes W9 built, the user's own among them**, have workbooks with no `Process`. Under D11's ruling (B)
  they open Machined, as built, and nothing reads as changed (§1.3). The Workbook panel's Process line says so and
  says how to print one.
  - **When the user types Printed** on one, *Update SolidWorks* carries the change in place, as a value of each
    part: one global per part (§1.3). W9a's rules apply as to any Update: K11 first; K4's footer before the press; a
    part marked unsaved or mismatched said as W9a says it; on 2024, a What's Wrong that comes and goes when something
    of the user's is in error.
  - No gear moves: a gear's phase is set by the centre of its tooth space (`workbook/geometry.py:8`, `phases` at
    `:430-497`), and backlash widens the space evenly about that centre. That is read from the code, and F1's runs
    bear it out: every app body stood at its record frame after the press, in H, N and L, on both versions.
    K2's refusals are not met. **Route (c1)'s puts are made all the same** (measured, F1's SolidWorks runs of
    2026-11-18, `F1-DEMONSTRATION-RUNS-REVIEW.md`): on SolidWorks 2026 and 2024 alike the Update re-placed the whole
    train in every mode (the carrier, Sun, the three planet copies, both dogs and RangeSlv, 33 puts, the locked
    sprockets carried along as the footer foresaw), each gear put where it already stood, harmlessly
    (`probe/results/f1-demo-sw2026-20261118-1-spur-pair-rangebox-clean.log`:936-939, 1012;
    `probe/results/sw2024/f1-demo-sw2024-20261118-1-rangebox-clean.log`:93-96, 169). W9a's own value Update of
    Sun's Backlash does the same (`w9a-final-sw2026-20261117.log`:95, 98). So a user's mate on an app gear's face is
    re-solved by those puts, as by any of W9a's value Updates; `setup.master` has no such mate, so that was not seen.
  - W9c's landing guard (`swbuild._landing_route`) foresees no landing for this change: by the second review's
    calculation, each tooth line's new start lies about a whole line length from its old end.
  - A user mate on a tooth face re-solves by about 0.035 mm, as for any change of values.
  - F1's SolidWorks run shows this on a copy of W9a's `setup.master` with Printed typed (§2.8).
  - *Build again…* after Printed is typed makes every gear new, since a part is reused only when its globals are as
    recorded (`gearbox._matches`, `gearbox.py:440-449`). W9d then carries the user's components onto the new parts
    and names, with *its Process changed*, the user's features and the mates on faces it cannot make again. That is
    what the user asked for by typing Printed, so under (B) no way back is added. Under (A) it would be: §1.3's
    three sentences, which never name a cell the workbook does not have. The first revision's *type Machined in
    Box!B9* was wrong for every workbook written before F1, which has Units in B9 and no Process row.
- **K11** (Update refuses a value the app owns that the user changed in SolidWorks):
  - F1's backlash equation is one of those values from the start. No new code reads it, since `_value_edits`
    (`swbuild.py:5423-5457`) compares every planned global.
  - F1 changes K11's words only, and only for the printed default. Today `_blank_meaning` (`:5460-5471`) turns a
    non-numeric expression into words by removing quotes and turning ` * ` into ` × `, and `_back_words`
    (`:5484-5489`) prints that same text as *the equation …*. For the IIF that would read *IIF ( Module <= 1 ,
    0.3 × Module , 0.3 )*, which SolidWorks cannot take back as typed.
  - So `ValueEdit.blank` keeps its meaning (it is in memory only; `store.ValueEditEntry`, `store.py:656-667`,
    does not hold it). `_wanted_words` (`:5474-5481`) and `_back_words` recognise the printed default by
    comparing `blank` with the printed expression stripped the same way, and take their words from their own
    source:
    - the workbook's value: *0.3 (from its blank cell, the printed default: 0.3 mm, or 0.3 × Module below module 1)*;
    - the set-back, built from `spur.printed_backlash_expression`: *set it back to the equation IIF ( "Module" <= 1
      , 0.3 * "Module" , 0.3 )*, the exact text SolidWorks must hold for K11 to read it as the app's again.
  - Every other K11 sentence is unchanged.
  - F3's `"Bore Allowance"` and the flat's dimension join `_GLOBAL_COLUMN` (§4.3).
- **The hub (W9b)** is built as a dog's toothed ring "with the row's Bore", its fixing to the shaft left to the user.
  - In F1 it takes Process through `clutch._as_spur`, and so the printed backlash. W9b's rule that a hub's teeth,
    module and pressure angle are its sleeve's is untouched, and Process is the Box's, so the two cannot differ.
  - In F3 a hub row takes `Bore allowance`, `Drive` and `Flat` as any gear: that is its fixing.
- **K9's running clearance**, `max(0.5, 0.5 m)` (`workbook/modes.py:606-609`), **stands for printed sleeves
  unchanged.** This is the ruling the first revision left to F1.
  - It was argued from a chamfer and backlash that scale with the tooth. Printed, the backlash stops scaling above
    module 1.
  - But the gap is axial, and a printed part's axial error is in its layers and its first layer, which D9 leaves to
    the slicer.
  - A printed part's first-layer squish spreads the bed face outward in the plane of the bed, not along the shaft.
    The axial error is about a layer, 0.2 mm, and the faces' places are the user's housing. The 0.5 mm floor covers
    both, and from module 1 up the gap still grows with the tooth, as a dog's chamfer would. (The first revision
    leaned on §2.2's 0.3 mm, which is a radial figure, not an axial one; the conclusion does not rest on it.)
  - So nothing changes, and W9b's pins hold. If D9's chamfer is ever built, this is read again.
- **Carrying the user's work (W9d).**
  - In F1, `update._SPEC_COLUMNS` (`workbook/update.py:3196-3201`) gains Process, so a part made new because of it
    says *its Process changed*, not *its values changed*. Its raw comparison (`_changed_columns`, `:3210-3219`)
    reads a missing `process` as `machined`.
  - In F3 it gains the bore's three columns, and `_bore_mm` gives the hole as cut (§4.3).
  - A part made new by any of these is carried like any other part made new.
- **Update in place (W9c).** An Update that inserts a gear, or gives a sleeve its bands in place, builds or changes
  printed parts by the same routes as machined ones. Each of those routes is already behind W9c's per-version
  findings, which F1 does not touch. No new kind of write by Update is in F1 or F2. F3's allowance given in place
  would be one, and is left out (§4.1).
- **The Workbook window (K12).** The window now scrolls its two columns between a fixed header and footer, and the
  footer has a ceiling above which its sentence scrolls (`design/UI-DESIGN.md:406-420`). So F2's Export button fits
  whatever else the footer says. The Box's Process shows as one line in the Workbook panel for every gearbox:
  *Printed, 0.4 mm nozzle*, or *Machined, as built: type Printed beside Process on the Box sheet to print it*, with
  *(add a row labelled Process)* when the sheet has none (open point 3, §2.8).
- **Files both touch**, each with its lines in §1 and §2.8: the form (`gui.py`), `workbook_gui.py` and
  `ui_text.py`, `store.py`, `workbook/assess.py`, `workbook/update.py`, `workbook/checks.py`, `workbook/schema.py`,
  `workbook/model.py`, the gear kinds, and K11's words in `swbuild.py`. Under (B), `workbook/gearbox.py` is not
  touched. They were read at `c2d95cc`. `ui_text.py` and `findings.py` have changed since (`891a707`, `225e3d7`),
  so `ui_text`'s lines are read again. If W9's 2024 runs change any other of them before `printed` is cut, the
  coordinator has the affected parts of §1, §2.8 and this section read again.


## 7. Not in this plan, and what a printed train will still want

- **Tip relief.** PLA is about a sixtieth as stiff as steel, so loaded teeth bend and meet early. The
  first thing a loaded printed train will ask for.
- **A radial allowance.** Tips and roots are not offset for fat walls, and tip corners print rounded,
  so the real contact ratio is a little under the drawn one. §2.2's clearance check watches it; nothing
  corrects it.
- **The shafts' spacing.** The housing is the user's, and an error there moves the play by about 0.73
  of the error. The layout part gives exact distances with no printed allowance.
- A true undercut root (D6). The edge chamfer (D9). A boss, setscrew or insert pocket. Spokes or
  lightening holes. Crowning. Bevel strength. Materials other than PLA. Wear, heat and creep. Setting
  a SolidWorks material: it stays the manual step it is.
- A Process per Gears row (one gearbox with printed and machined gears). Process is the Box's, as D1 has it.
- **A pair interference check on the drawn parts** (§2.3, the coordinating session's ruling). It would sweep the two
  drawn outlines through the mesh with each gear's own backlash, less a printer's allowance of about 0.1 mm a flank,
  and warn on any overlap. It would take each gear's recipe, and be rated once §3.2's prints give the printer's
  real figure.


## 8. Risks

- **The numbers are borrowed.** 0.3 mm, 0.2 mm and 17 MPa come from guides that disagree and from no measurement of
  the user's printer. §3.2 replaces the first two; until then every card that shows one says it is a starting
  value. Nothing in this plan replaces the third.
- **Two allowances stacking:** the app's and the slicer's. This is said on the card and in the print list.
- **The default in code is machined (§1).** A path that makes a `GearSpec` for the user without setting its
  process would build machined silently. The paths are the form (`gui._gear_spec`), the workbook
  (`Gear.spec_values`, which a test holds to every field), Solve, which keeps the form's fields, and the developer's
  command line, which gains a key (§1.3). §2.8's tests hold
  each. The review should look for any other `GearSpec(` in `src` that serves the user; at `c2d95cc` the only bare
  one is the form's defaults (`gui.py:154`).
- **D11 may be overruled to (A).** Then a user's built gearboxes all read as changed, and the first Update after F1
  writes to every part of their RangeBox. It is a value write W9a's rules govern, but a write to each of their files
  nonetheless, and on 2024 the first press on RangeBox is memory-heavy (W9c). The switch is one function and three
  sentences (§1.3).
- **A gear may be printed in a gearbox the user built before F1 only after they say so.** Under (B) a new row added
  to such a gearbox is machined too, as built, until Printed is typed. The Process line in the Workbook panel is
  what tells them.
- **A field on a derived class reaches every record.** The derived gear is written whole into each `.gear.json`, so
  any field added to one later goes there too. §1.1 keeps F1's out while machined, and §2.7's pin on the whole
  `.gear.json` is what catches the next one.
- **No pair is checked for interference in F1 (§2.3).** The sweep that cleared the drawn parts at the printed
  default is an inference from the app's outlines, and did not cover helical, shifted or bevel pairs or recipe B.
  A printed pair whose flanks do meet is found by turning it in SolidWorks, or by printing it, as W7's sentence
  already says for a planetary.
- **K11's set-back for the printed default is an equation.** A user who typed a number in SolidWorks is told to
  type the IIF back, given exactly, or the number in the cell. That is the same burden as today's `0.3 * "Module"`,
  but a longer text.
- **The plan's citations age.** They are as of `c2d95cc`, before W9 is merged and before W9's 2024 confirmation
  ends.


## Sources

- Sovol, *3D Printing Gears That Actually Work* — <https://www.sovol3d.com/blogs/news/3d-printing-gears-that-actually-work-backlash-orientation-and-material-tips>
- How To Mechatronics, *How To 3D Print Gears* (bench tests) — <https://howtomechatronics.com/how-it-works/how-to-3d-print-gears-the-ultimate-guide/>
- Hackaday's summary of the same — <https://hackaday.com/2024/06/12/studying-the-finer-points-of-3d-printed-gears>
- Instructables, *A Practical Guide to FDM 3D Printing Gears* — <https://www.instructables.com/A-Practical-Guide-to-FDM-3D-Printing-Gears>
- RepRap wiki, *Gear Design* — <https://reprap.org/wiki/Gear_Design>
- University of Warwick, printed nylon gears against moulded — <https://core.ac.uk/download/228159444.pdf>
- On VDI 2736's limits — <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10537784/>


## Changes after the first review

By the review's finding numbers. **1** §2.3: the ring condition reversed, helical, bevel and crossed
pairs stated, the planetary sentence taken over. **2** the pair check and every new check printed-only;
the rule now covers warnings and Solve rows. **3** D3 and §2.1: the smaller of 0.3 mm and 0.3 × module,
so no gear that builds today is refused. **4** §1: one record reader and the comparisons that use it,
no Process property, §4.1 for parts printed before F3. **5** §6 and D8; stages renamed F1 to F4. **6**
clearance per pair, with bevel and shifted pairs and a tolerance. **7** §2.5. **8** §2.7. **9** D9 and
§4.3: the chamfer taken out. **10** §3.2: a span measurement and a bore coupon in place of a rig.
**11** §5: the ring's 60°, the stress-correction factor, force per mesh, planets and idlers, layers, no
bevel, the wording. **12** §2.1: what the allowance is exact for, and the bevel's toe. **13** D10.
**14** §1 and §4.1: where each value lives. **15** §3.1: the file checked without reopening; D5 worded
as read. **16** each stage's 2024 build, cost and review. **17** the smaller figures corrected in
place.


## Changes after W9

2026-11-18. The plan read against the code at `c2d95cc` (branch `w9d`, W9's code shown on SolidWorks 2026, its
2024 confirmation still running), by section, each with why.

- **Head.** It no longer says nothing is to be built. It says what the user said on 2026-11-18, that this
  revision's review comes before any code, which commit was read, and when it is read again.
- **Context.** The cited lines found again and the facts confirmed unchanged by W9; the hub's bore added.
- **The rule.** It now covers the record's bytes too, and says where the user chooses Printed: W9b made a sleeve's
  record byte for byte what it was, and the same is now possible for a machined part.
- **Decisions.** D3, D6 and D7 say whether F1 can go ahead on them. D8 records the user's 2026-11-18 word. D10 says
  that an Update keeps a part's name, from W9b's ruling on bands and `gearbox.name_changed`. D11 is new: a
  W9-era gearbox reads Printed, since W9d makes Build again… on such a gearbox remake every gear, which the user
  should confirm.
- **§1, the default (the largest change).** The first revision had the dataclass say Printed and one record reader
  fill a missing key with Machined. Now `GearSpec`'s and `Box`'s defaults are machined, the user's blank is
  Printed, and `to_dict` leaves a machined spec's new keys out, as W9b's bands are left out. Why: `from_dict` has
  six callers, the raw-dict comparisons grew in W9d (`_changed_columns`), and the suite's 200 hand-built specs and
  W9's code-built fixtures would all have turned printed. Now they stay machined with no edit, and machined
  records are byte for byte W9's.
- **§1, the schemas.** Link 11 and sidecar 3 replace "up by one from wherever W9 leaves them". The older app's
  behaviour is read (it refuses a newer schema and leaves it alone), so that STOP is answered.
- **§1, the form and the Box.** `pair.apply` corrected to `gui._gear_spec` and `GEAR_COMPOUND`. The Box's
  Process is checked as read, since the Box has no lists and `Setting` had no words. The hub is added to the kinds
  that pass Process through.
- **§1, what the default carries.** What Update and Build again… do with a W9-era gearbox, the user's work in it
  included, from W9a's and W9d's code.
- **§2.1–§2.5.** Each citation corrected. The card's third state is given its field. Nozzle in `GearSpec` answers
  where checks find it. A ring pair's radial clearance is new code, since `tip_clearance` is outside only. The
  sleeve's relief is noted. Couplings are not pairs. The planetary sentence is replaced only when printed.
  `solve`'s keywords are named.
- **§2.7.** Pins taken where `printed` is cut, now including W9's fixtures and the bytes of a machined record. The
  marking burden is recomputed (200 specs in 27 files, none to edit; the Excel-saved workbooks marked where pinned).
  W9's masters on the host are noted.
- **§2.8, new.** F1 made ready: its files, what must not move, its tests, packages F1-0, A, B and C with disjoint
  files, the open decisions, Done when (now with an Update of a W9 master, on both versions), cost, and the open
  points for the review. The first revision's F1 *Done when* moved here.
- **§3.1.** What the window exports from W9's record. Refused while a part is unsaved or mismatched. The button kept
  whole by K12. What's Wrong on 2024 not assumed for an export.
- **§4.** None ↔ some allowance stays a new part rather than a W9c-style in-place write. F3's schema numbers. New
  §4.3, what W9 asks of F3: K11's cells, W9d's columns and its "bore" radius, mates on faces. The chamfer section
  renumbered to §4.4.
- **§5.** Couplings not rated; where the torques and planets are read.
- **§6.** Rewritten item by item, with the code each meets: pins, schemas, the record's shapes, W9-era gearboxes
  under Update and Build again…, K11's words, the hub, K9 ruled to stand, W9d's columns, W9c's gates, K12's window,
  the files.
- **§7.** A Process per row added to what is not in the plan.
- **§8.** New risks: the machined default in code, the user's gearboxes all changing, K11's equation set-back, the
  citations' age.

## Changes after the second review

2026-11-18. To the second review (the last section of `docs/PLAN-PRINTED-REVIEW.md`, `158b06f`, which read
`51870ca`) and to the coordinating session's ruling on D11. Each change is by section, with why.

**The review's must-fixes:**

- **1. The derived gear in the record (§1.1, §2.8 item 3).** The first revision put a `backlash_printed` field on
  `SpurDerived`, and `asdict` would have written it into every machined `.gear.json` and failed §2.7's pin at
  F1-0's own commit. Now:
  - one field, `nozzle: Optional[float] = None`, goes on each of the three section classes;
  - `printed` and `backlash_printed` are properties;
  - the four `to_dict`s that write a derived gear leave `nozzle` out while None;
  - §2.7's pin covers the whole `.gear.json`, `derived` included.
- **2. Every derived class, and the functions that see no spec (§1.1, §2.2).** `SpurDerived`, `InternalDerived`
  and `RackSection` are named, with the helical and bevel classes reached through `section`. The process and nozzle
  reach `spur.section_diagnostics`, the ring's `internal.section_diagnostics` and `pair.mesh_warnings` on the
  derived gear, so their signatures still need not change. That is now said, where before "no signature changes"
  was untrue as written. The ring's tip check is named.
- **3. The schema pins (§1.2, §2.8 item 7).** All the lines that pin the literal 10 move in F1-0. That is eight
  lines in five files: the review's six, and the two read-forward lines `test_workbook_bands.py:367` and
  `test_workbook_carry.py:75`, which assert the current schema as a literal too.
- **4. The tests over the five committed workbooks (§2.7, §2.8).** F1-0 owns them. It adds `machined(spec)` to
  `tests/workbook_fixtures.py` and marks every read in the ten files. Marking inside
  `test_workbook_demo_fixtures.assessed` also covers its two importers in B's files. B reads them printed in its own
  new file.
- **5. *Type Machined in Box!B9* (§1.3, §6).** It is gone. A workbook written before F1 has Units in B9 and no
  Process row. Under (B) no way back is needed. Under (A) the kept sentences name the cell only when the row exists,
  and otherwise say to add a row labelled Process.

**The review's should-fixes:**

- **1.** §2.2's tip figures corrected: module 1 warns below 26 teeth only; module 1.25 passes from 11.
- **2.** Context: "12 and fewer clear nothing" restated as a statement about pairs, with what 12 to 10 teeth clear.
- **3.** §6: K11's set-back takes its own source, the exact IIF text. `ValueEdit.blank` keeps its meaning.
- **4.** §2.8: stubs return neutral values, and F1-0 lands the printed backlash equation and derive (items 2 and 4).
- **5.** §2.3: `report.undercut` stays filled when the printed check replaces W7's sentence.
- **6.** §1.1: `to_dict` never raises, and drops a typed Nozzle when machined; the harmless failure to round-trip
  is said.
- **7.** §2.3: the ring case's commonness, depth, cure and cause, and the margin below.
- **8.** `src/gear_generator/probe/` paths, and "five" workbooks throughout.
- **9.** §1.3: the developer's command line gains a `process` key.
- **10.** §4.1: F3's link 12 is one policy with F1's 11, and the literal 12 at `test_store.py:833` changes then.
- **11.** §2.8: the window's pinned panel text is listed as moving by the Process line.
- **12.** §1.3: a new part built from a loaded old record's form is machined.
- **13.** D11, §1.3, §6, §2.7, §2.8 and §8 rewritten to (B), keyed on the record's parts.
- The review's note on K9's loose sentence (a radial figure in an axial argument) is taken in §6.

**The rest:**

- **The planetary warning (§2.3, open point 7).** The second review found that an unshifted pinion of 17 teeth or
  fewer clears no ring, so nearly every printed planetary would warn. A warning that nearly every planetary shows
  is a warning nobody reads. So this revision proposes, for the coordinating session to confirm and the user to
  overrule, that every printed pair warns only when a tip reaches more than half the nozzle width past the other's
  tangent point. Why: that sliver is about what a printed tip's rounded corner takes off (an inference, one
  constant). The sentence gives the depth, the cure, and that the cause is the tooth counts, not printing.
- **D11, the coordinating session's ruling (B)** (the D table, the head, §1.3, §6, §8). A gearbox built before F1
  opens exactly as today until the user types Printed.
  - Why: it writes nothing into a gearbox the user already has; it keeps D2's *a part already built reads Machined*
    for the gearbox as the strip keeps it for a part; and issue #1 was the user's fear of the app overwriting their
    work.
  - The rule is `assess.blank_process(record)`, keyed on whether the record's current parts were built machined,
    not on the schema number, which any F1 write moves to 11.
  - What (A) would do is kept in one paragraph, with its one switch (that function's body) and its three
    sentences.
  - Under (B), B no longer touches `workbook/gearbox.py`; the footer's Process sentence and `_reuse_advice`'s
    Process case are not written; F1's SolidWorks run types Printed on the master first.
- **§2.8, F1-0's interface stated precisely:**
  - eight numbered items of names, signatures and stub returns;
  - the source and test files F1-0 touches;
  - each package's source and test files, disjoint in `tests` as in `src`. B's Box tests and C's window tests go
    into new files, since `test_workbook_model` and `test_workbook_window` are F1-0's. C's one edit to the window
    file is the panel line's pins.
  - The first revision's file table is folded into the interface and the packages.
- **Open points.** 1 to 6 are recorded with the review's verdicts. 7 (the margin) and 8 (D11) are new.


## Changes after the third check

2026-11-18. To the third check (the last section of `docs/PLAN-PRINTED-REVIEW.md`, `d2e34a6`, which read `ffe8812`
against the code at `5de0290`) and to the coordinating session's ruling on the ring pair check. Each change is by
section, with why.

**The check's must-fixes:**

- **The schema pins (§1.2, §2.8 item 7).** There are ten lines, not eight; `test_workbook_carry.py:79` and `:1057`
  were missed. I counted again with `git grep` and listed every one. F1-0 now moves every literal 10 that grep finds
  at the cut, not a list, since W9's work still landing may add more. `probe/w9d_demonstration.py:1007` checks the
  schema too; it is W9d's demonstration script and is noted, not moved.
- **The Box settings (§2.8 item 5, packages).** F1-0 now takes the two `Setting`s, `to_sheets`' two `box_values`
  keys and the pin `tests/test_workbook_model.py:24-27` together in one commit. Why: `to_sheets` writes
  `box_values.get(key, "")`, so the settings alone would write a gearbox built in code with a blank Process, which
  reads Printed with no record. And the pin is in a file only F1-0 may touch. B keeps `_read_box`'s word check and
  `template`.
- **The pair check's signature (§2.8 item 4).** `printed_pair_warnings` and `PairWarning` are removed from the
  interface, following the ruling below.

**The check's should-fixes, for package C (§1.3, §2.8):**

- `_assess` itself resolves the blank, so its second caller (`workbook_gui.py:692`, feeding
  `wb_link.consequence`) agrees with `_plan`.
- It passes no record when the record is another workbook's (`store.foreign_workbook`).
- `assess` resolves `read`'s Box as well as `spec`'s, so no `Assessment` holds a blank Process; B's new test
  file holds it.

**The ring pair check (§2.3, D6, Context, §2.8, §7, §8, open points 4 and 7): the coordinating session's ruling,
2026-11-18, the user's to overrule.** F1 builds no interference warning for a pinion inside a ring, with or without
a margin, and W7's planetary sentence stays exactly as it is.

- Why: the third check swept the drawn outlines through the mesh. The radial measure reports overlaps the drawn
  parts do not have: at most 0.026 mm with no backlash, and none at the printed default, RangeBox's 13 in 55 among
  them.
- The half-nozzle margin and the "nearly every planetary warns" consequence go with it.
- A check that sweeps the drawn outlines with a printer's allowance is listed in §7 as later work.

**Outside pairs (§2.3).** The same test was applied, from the third check's sweep of five outside pairs (6 / 30 to
13 / 80, modules 1 and 1.5), read and not rerun.

- The pinion's flank below its base circle is drawn, not undercut.
- The radial measure reports 0.24 to 0.62 mm, while the drawn flanks overlap by at most 0.067 mm with no backlash,
  and by nothing at the printed default (6 / 30 clears from about 0.08 mm).
- So no outside-pair warning is true of the parts as drawn at the printed default in any case covered, and none is
  kept. Bevel pairs, which rested on the same measure, go with them.
- The single gear's undercut warning gains a printed sentence that says what is true: made as drawn, no undercut,
  the mate not checked, turn it in SolidWorks.
- The Context's generated-gear figures are marked as such.

**When packages start (§2.8).** F1-0 first, once `printed` is cut. Then B and C in parallel. A can start with them,
since the §2.3 wait the check gave it is discharged by the ruling; it waits only if the coordinating session wants
this revision checked again.

## Changes after F1's review

2026-11-18. To F1's review (`docs/notes-printed/F1-REVIEW.md`, `be5ae7a`) and the coordinator's rulings on it, each
the user's to overrule.

- **§2.2, the ring pair's gaps (the review's S3).** Each gap is the depth less two modules, so 0.4 × module only up
  to module 1.25, where the depth IIF is 2.4 × module, and 0.25 × module above, where it is 2.25 × module. The plan
  said 0.4 × module at every module; package A's maths was right and the text was not.
- **§2.6 and §3.0, the span over k teeth (ruling 1).** It was not built in F1, and it is not part of F1: it is F2's
  first step, before any print is measured. §2.6 now points to §3.0, which holds its text; §2.8's *Done when* says it
  is not in F1, and F2's *Done when* opens with it.
- **The rule's pins (ruling 4, the review's S1).** `tests/test_printed_rule.py` now also holds the seven ways the
  review found of telling a machined gear or gearbox something new that only the packages' own tests caught: a
  machined gearbox's Meshes rows and fixes, a machined pair on the form, a machined helix over 45°, W9d's columns, and
  the Workbook window's blank Process on a gearbox built machined. A reader of sidecar 2 refusing a printed
  `.gear.json` is tested (`tests/test_store.py`).
- **Recorded, not changed here:** the form judges a printed crossed pair as the workbook does (ruling 2); package B's
  planet-copy wording in *Build again…* is kept until `w9d` is merged, whose own fix (`d496cfd`) then stands
  (ruling 3).


## Changes before F2

2026-11-18. Section 3 read against the code at `61460b9` on `printed` (F1 closed; W9 merged at `138d646`) and made
ready to execute, as §2.8 made F1. Each change is by section, with why.

- **§3.0, the span over k teeth.** The maths is given in two forms that agree, with its sources (ISO 21771's base
  tangent length and KHK's span measurement), and package A checks it against a worked example before code. The
  rule for k is stated, through the contact radius. The plan says which gears show the span, where the user sees it
  (a Derived row, a *Measured* entry, the print list, the explainer), and gives nine figures for the tests,
  computed from the app's own derived gears at `61460b9`. Before, it was one paragraph with no maths, no figures and
  no place on the window.
- **§3.1, Export.**
  - What is already known is gathered from the user's macro database (`entries/files/04`, `API-LEDGER.md:190`,
    `GOTCHAS.md` §20 and §34) and this repo: the route, its copy option, the overwrite, and STEP not to be reopened.
  - The probe is written call by call. Each answer is tied to a finding in `findings.py`, with what the app does
    while that finding is None, on 2026 and on 2024. Before, it was one sentence.
  - The button is renamed **Print files…**, since the window's *Export* already writes the workbook.
  - What is exported, when it is refused, the files' names and place, the print list's contents and the file check
    are made concrete on the form and in the window. Refusals: an unsaved or mismatched part, globals not the
    record's, a feature in error, or a workbook Update would change; a whole set or nothing.
  - Citations corrected: `store.LinkRecord.current_parts` is now at `store.py:1026`, and `gui._update_target` at
    `gui.py:1573`.
- **§3.2, the user's step.** It is rewritten as instructions the user follows: four copies of one gear as span gears
  and bore coupons at once, the Bambu Studio settings by name (read, not checked), how to hold the calipers, the
  shaft-fit grades, where each number is typed (the form's *Measured* entry, then the session), how D3's number
  follows from them (`j = 2 (e + 0.04) / cos 20°`), and a table to fill. Before, it was three short items.
- **§3.3, new.** F2 made ready: F2-0 (the interface, then the probe run and reviewed on both versions, its findings
  set), then packages A (span), B (export) and C (window and form) with disjoint files in `src` and `tests`; what
  must not move; the demonstration on both versions; Done when (the code can close before the measurements, the
  stage with them); and the cost, about ten agent runs and about 65 SolidWorks minutes.
- **§3.4, new.**
  - Seven decisions on assumed answers (E1 to E7), each said to go ahead.
  - Five that need the user but not before code (U1 to U5): their shaft, printer, calipers, the numbers and the
    slicer's opening.
  - None needs the user before code.


## Changes after F2's review

2026-11-18. To F2's review (the last section of `docs/PLAN-PRINTED-REVIEW.md`, `926cf50`) and to the coordinating
session's ruling on repeat presses. Each change is by section, with why.

**The five must-fixes:**

- **M1, the helical span (§3.0).** The contact radius is now `√(r_b² + (W_n cos β_b / 2)²)`, the jaws' common
  normal being the base-cylinder tangent at β_b. With it, the nearest-to-`r + x m_n` rule gives the textbook k. The
  m_n 1.5, z 25, β 20° row becomes k 4, W_n 15.8438 (W_t 16.7315), contact 20.062 mm, recomputed here and agreeing
  with the review. A β 30° row is added (k 4, 21.2255). The spur rows and the β 15° row are unchanged, since for them
  the rule picks the same k. The source is stated as KHK's span measurement (Tables 5.10, 5.11) with `A_Wk = A_sn cos
  α_n`; ISO 21771 and DIN 3960 are named as unchecked.
- **M2, the STEP check (§3.1.4, §3.3).** It accepts AP203, AP214 or AP242, and any length unit it can read, since the
  user's export options set them. It refuses a broken frame, any other schema, no solid or more than one, an open
  shell or a surface model, and an unreadable unit. Instances are counted, not substrings. `STEP_FILE_CHECK` is
  withdrawn. The vertex-extent check is added as a should-fix, built if probe step 3 bears it out.
- **M3, repeat presses (§3.1.3; the coordinating session's ruling).** Each press writes into its own new folder,
  `<Output folder>\print\<date time>\` with a counter if the name exists, holding its files and `print list.txt`.
  Nothing is overwritten, and `_r2` keeps meaning only a part's second revision. A failed set's list says *DO NOT
  PRINT THIS SET*.
- **M4, who owns the sentences (§3.3).** `printout`, `swcom` and `swbuild` (package B) return structure:
  `Refusal` codes with details, `PrintResult`, and the check's reason codes. `ui_text` (package C) owns every
  sentence a user reads, the print list's text included, as W9's packages did. The gate is checked by B twice, in
  planning and again in the job, and C only words it.
- **M5, the component case and the documents (§3.1.2 step 7, §3.1.3, §3.3).** The probe now exports a part open only
  as a component of an open assembly, reached by `GetOpenDocumentByName`, with the assembly's save flag read. It
  also measures the fallback of opening that part in its own window and closing it. Two findings follow. The job says
  how each part becomes the build document, what is activated, that it closes only what it opened (never an
  assembly), that it reads every save flag before and after, and that it puts the user's active document back in a
  `finally`.

**The review's other points:**

- **§3.0.**
  - The contact is bounded (the involute's start, 0.2 mm under the tip).
  - The narrow-face margin is KHK's 3 mm, a herringbone taking its half.
  - **Arcs: the ruling** is to show no figure, with one line. The span runs 11.139 to 11.221 mm on the m 1.5, z 20
    gear, about the size of what is measured. A range invites a false average, and §3.2's coupons are Involute.
  - A ring is measured over pins.
  - Package A's check is against the app's own drawn outline, a textbook example being unobtainable.
  - The Measured line uses the gear's `cos α_n`, holds a floor of 0.1 mm a gear, and says when `j` passes
    `0.3 × module`.
- **§3.1.**
  - `SaveAs` is chosen over `SaveAs3`, and why.
  - Probe step 6's "right file" is defined.
  - Step 8 is dropped as a proposal for the coordinating session.
  - The user's documents' save flags are read.
  - The `SAVE_AS_COPY` row says one thing.
  - The feature-error citation is corrected to `swcom.py:1083-1095` and the build walk.
  - `has_unsaved_changes` is said to read the build document only.
  - The button is moved to the form's footer and named **Print files** without an ellipsis, and the SolidWorks bar
    says which file it writes.
  - The window's fifth button is to be drawn at 1080 px.
  - A machined part's list block says *no span*.
  - A layout-only change no longer refuses (E3).
- **§3.2, the user's instructions.**
  - Where the files are: the press's folder in the Output folder's `print`.
  - One seam rule: Aligned, and measure away from the seam's tooth.
  - The calipers zeroed and closed by the thumb roller; square on spur, tilted on helical.
  - The mean of twelve, with any reading 0.05 mm off taken again.
  - The bore tried from both faces; the rule for two (c), none (c), all (a) and all (d); the D-flat not covered.
  - An optional m 2, z 30 coupon to separate flank growth from shrink.
  - What to record of the print.
  - Bambu Studio's mesh precision left at its default.
  - The backlash formula with `cos α_n` and its floor.
  - **A measured backlash above 0.3 × module set out plainly as the user's decision** (U4).
- **§3.3, the cost** restated as the review has it: thirteen to fifteen agent runs, about 90 SolidWorks minutes
  (the 65 is the floor). The *Done when* gains the interface review, the findings commit's review, the boards and
  documents, and the stage review's should-fixes.


## Changes after F2-0's review

2026-11-18. To F2-0's review (`docs/notes-printed/F2-0-REVIEW.md`, `0c4b7c3`) and the coordinating session's rulings on
F2-0's twenty decisions (all accepted as the review recommends; recorded in `docs/notes-printed/F2-0.md`).

- **§3.2, Coupon_E for a shaft over 18 mm.** It is then Module 1.5, Teeth 20, the other size, since the four coupons are
  already Module 2, Teeth 30 (the re-check's should-fix, ruled).
- **§3.0, a citation.** The herringbone's half is `HelicalDerived.toothed_width` (`helical.py:180-183`), not
  `half_width`.
- The probe's changes for its run (`probe/f2_probes.py`, `F2-PROBES.md`): `PART_WINDOW_READ` is proposed only from a
  reading of a part open in its own window but not active, the case the job uses it for (M1); `STEP_EXPORT` needs the
  spur's file to be the spur's size (S1); step 7c, the lightweight case, runs last (S2).

## Changes after F2's probe runs

2026-11-18. To the probe's runs on SolidWorks 2026 34.1.1 and 2024 32.5.0 (`8d2c5fb`, `docs/notes-printed/F2-PROBES.md`)
and the coordinating session's two rulings on them, each the user's to overrule.

- **Ruling 1, §3.1.2 steps 6 to 8: a file is told by its geometry, not its text.** Two exports of one document differ in
  nearly every statement on both versions, so the text test never held and three findings went unproposed. Two files are
  now the same part when their entity counts, their CARTESIAN_POINTs and their radii agree within 1e-4 mm, header and
  numbering aside, with the run's own controls (one document twice; the spur against the helical; 8 mm against 9 mm).
- **Ruling 2, §3.1.2 step 7 and §3.1.3: a lightweight component is refused by name** (resolve it or open the part),
  since the fallback resolves it in the user's assembly. `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` is proposed for a resolved
  component only, and the probe reads the assembly's flag and the component's state after the fallback's close.
- The probe is changed to both and run again on both versions (`F2-PROBES.md`, *After the runs*).


## Changes before F3

2026-11-18, evening. F2 recorded as closed short of §3.2, and §4 read against the code at `f28cb75` on `printed`
and made ready to execute, as §2.8 made F1 and §3.3 made F2. Each change is by section, with why.

- **Head.** It no longer says nothing is built. It says where things stand:
  - W9 closed and merged;
  - F1 closed (`5e2f386`, `0e7000d`);
  - F2 closed short of §3.2 (`9c1275f`, `70a2c42`, `550a8a9`), with what it leaves open (the user's step, and
    D3's and F3's figures from it);
  - nothing printed merged into `workbook`;
  - F3 made ready;
  - F4 not waiting on the user.

  The two "before any code" conditions it carried are long met.
- **§2 and §3.** Each opens with its close, in the manner of the head, F2's with what is still owed.
- **§4.1, the allowance.**
  - What it builds, op by op: the bore's link becomes `"Bore Diameter" + "Bore Allowance"` with one new global.
    Each SolidWorks call is named and shown to be one the app already makes, so no probe comes first.
  - The bevel's revolved bore takes it in its expressions.
  - Which gears take it: 0.2 placeholder printed, 0 machined, typed honoured.
  - **The as-built rule** (one function), so a later default from the user's coupon rebuilds nothing they did not
    ask for.
- **§4.2, the D-flat.** The D sketch, op by op: a major arc, a horizontal chord, its length linked through `sqr`.
  It uses only calls the app makes. Two things are new in kind though not in call (a major arc, an arc's end shared
  with a line's); by the house rule the full build measures them. Also: its checks, the bevel refused, and the
  flat's place.
- **§4.3, the record.**
  - Link 12 whatever the parts, sidecar 4 for a part with an allowance or a flat.
  - The three spec keys and the derived fields left out at their defaults (F1's lesson).
  - The fifteen literal 11s counted by grep and listed, and `test_store.py:833`.
- **§4.4, what W9 asks.** K11's two globals and their blank's words, W9d's three columns and its bore radius as cut
  (the arc of a D still "bore"), K5's naming of mates on faces, the hub row taking all three, and W9c's in-place
  Update with no new kind of write.
- **§4.6, new.**
  - F3-0 (machined pins first, then the interface with its eight items and its files);
  - packages A (geometry and checks), B (record, workbook, Update) and C (the form and words), disjoint in `src` and
    `tests`;
  - what must not move, with the one by-design exception named;
  - the demonstration, measuring the hole through F2's own STEP route;
  - Done when;
  - a cost doubled from F2's experience: sixteen to twenty agent runs, about 120 SolidWorks minutes;
  - decisions G1 to G8 on assumed answers, V1 and V2 for the user later, none before code.

