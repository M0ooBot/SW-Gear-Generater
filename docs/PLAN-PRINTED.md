# Gear Generator — gears made to be 3D printed in PLA

**Drafted on 2026-11-16 and revised the same day to its first review (`docs/PLAN-PRINTED-REVIEW.md`) and to the
user's answers; revised on 2026-11-18 against the code as W9 leaves it, read at `c2d95cc` on branch `w9d`
(`51870ca`); and revised again the same day to its second review (the last section of
`docs/PLAN-PRINTED-REVIEW.md`, `158b06f`, which read the code at `51870ca`, the same as `c2d95cc` in `src`).**

W9's code is written and shown on SolidWorks 2026; its confirmation on SolidWorks 2024 was still running. On
2026-11-16 the user said *"w9 first, dont actually build anything yet"*. On 2026-11-18 the user told the
coordinating session to carry on past W9 down the plans, so this plan comes next. **Nothing of it is built yet.**

**Two things must happen before any code.**

1. W9 is merged into `workbook` and the branch `printed` is cut from it.
2. The pins and sentences of §2.7 are taken there. If W9's work changes `src/` after `c2d95cc` (tonight's
   `ui_text.py` and `findings.py` changes among it), every part of this plan that cites a changed file is read
   again first.

**D11 is ruled by the coordinating session** (answer (B), 2026-11-18, the user's to overrule; it is put to them
when they wake). §1 says where the one switch is if they choose (A). D3, D6 and D7 still stand as assumed; §2.8
says why F1 can go ahead on them.

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
  10 teeth, 11 up to 7, 10 up to 4, and none of those mates clears it back. Inside a ring, an unshifted pinion of 17
  teeth or fewer clears no ring at all (§2.3).
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
| D6 | Undercut | **Warn, and check each printed pair for it** (§2.3); drawing the true undercut root is another sketch topology and not in this plan. F1 can go ahead on it (§2.8). |
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
  - The literal `10` is pinned at eight lines in five test files, all moved in F1-0 (§2.8): `test_store.py:227`
    and `:1123`, `test_workbook_bands.py:353` and `:367`, `test_workbook_carry.py:51` and `:75`,
    `test_workbook_user_record.py:56`, and `test_workbook_window.py:312`. The second review counted six; the two
    read-forward lines, `bands:367` and `carry:75`, assert the current schema as a literal too.
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

- `assess.assess` (`assess.py:148`) gains a keyword `blank_process`, `printed` by default, and puts it into
  the Box when the Box's Process is `""`. The window passes `assess.blank_process(record)` from
  `WorkbookWindow._assess` (`workbook_gui.py:825-830`), its one pipeline. To do so, `_plan`
  (`workbook_gui.py:699-706`) reads the record before it assesses, where today `_plan_solidworks_pass` reads it
  after.
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
    ring's tip to the pinion's root, each 0.4 × module unshifted. `internal.tip_clash` (`internal.py:381`) is the
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

### 2.3 Undercut and interference (warnings, printed pairs only)

The single gear's undercut warning (`spur.py:877-880`) gains a printed sentence: *a printed gear keeps this
material, so the mate's tips may run into it*, ahead of the shift it already names.

For a printed pair the check runs on the form and at each Meshes row. It uses the shifts and the working centre
distance, and transverse values for helical kinds (`rb` from `αt`, addendum `mn (1 + x)`):

- **outside pair:** each gear's tip must not reach past the other's base-circle tangent point,
  `ra₂ ≤ √(rb₂² + (C sin αw)²)`, and the same with the gears exchanged. Made both ways, it passes no pair that has a
  gear of 12 teeth or fewer;
- **ring and pinion:** the ring's tip must not reach inside the pinion's tangent point,
  **`ra₂ ≥ √(rb₂² + (C sin αw)²)`**. The first draft had this the wrong way round: it cleared three of the repo's
  own rings that fail and warned on one that passes;
- **bevel pair:** the outside condition on the Tredgold pair at the back cone, with Gleason's addenda
  (`pair.bevel_candidate`, `pair.py:675`, already uses that pair for its clash);
- **crossed helical pair:** no pair check. Each gear's own undercut limit stands, and the sentence says that is all
  that was checked.

A sleeve on its dog or hub is a coupling of equal tooth counts, not a pair, and is not checked here.

**How common the ring case is, and what this plan does about it.**

*Facts, from the second review's calculation and checked again here:* unshifted at 20°, a pinion of 17 teeth or
fewer clears no ring at all. 18 teeth needs a ring of 161 or more, 19 needs 86, 20 needs 64, 24 needs 40 and 30
needs 34. So nearly every printed planetary would carry this warning. The interference is a matter of the tooth
counts. It is just as real for machined gears (KHK's `z₁/z₂ ≥ 1 − tan αa₂ / tan αw`), and the check is
printed-only here for the rule's sake, not because printing causes it.

*How deep it is.* The ring's tip reaches inside the pinion's tangent radius by `√(rb₂² + (C sin αw)²) − ra₂`. At
module 1, by a calculation here (not measured), that is:

- with a 54-tooth ring, 0.369 mm for a 12-tooth pinion, 0.278 for 14, 0.191 for 16, 0.108 for 18 and 0.029 for 20;
- for RangeBox's 13 in 55 at module 1.25, 0.401 mm;
- for planetary_4to1's 18 in 54 at module 1, 0.108 mm.

The depth grows with the module.

**The ruling proposed (the coordinating session's to confirm, the user's to overrule):** a warning nearly every
planetary shows is a warning nobody reads. So the pair check, for every printed pair alike, warns only when a tip
reaches past the other gear's tangent point by **more than half the nozzle width**, measured radially (0.2 mm at
0.4). Two reasons:

- A printed tip's corners come out rounded by about half a line, which is the very sliver the condition is about.
  That is an inference from how a line is laid down, not a measurement; §3.2's pair print is where it is first seen,
  and the margin is one constant if it proves wrong.
- At module 1 it still warns a 54-tooth ring's pinions of 15 teeth or fewer and RangeBox's planet, and stops warning
  where the overlap is a tenth of a millimetre.

The sentence then gives the depth in mm and says what clears it: a pinion of more teeth, or a larger ring. It says
the interference comes from the tooth counts, not from printing, and that the build checks interference only where
the gears stand. Below the margin, nothing is said. The pair check's other cases are unchanged by this.

**In a printed planetary stage** the check, with that margin, takes the place of W7's sentence
(`checks._check_stages`, `workbook/checks.py:358-366`, "is below the undercut limit, which is not modelled, and
meshes …"), so nothing is said twice. It replaces the warning only. `_check_stages` also fills `report.undercut`
(`:362`), which becomes `Plan.undercut`, the clause of the build's interference sentence (`gearbox.py:280-282`).
A printed stage still fills it as today. A machined stage keeps W7's sentence word for word.

The check is a warning, not an error: the app cannot say the drawn root meets the tip, only that the pair is at
risk.

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

### 2.6 A measurement to calibrate by

The Derived panel of a printed spur or helical gear gives its **span over k teeth** (the base tangent
length, what calipers across k teeth read), for the gear as drawn, backlash included. A printed gear
measures more than that by twice what the printer adds to a flank. This is what §3.2 uses; it needs no
rig.

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
   - `printed_pair_warnings(g1, g2, centre, *, ring=False, bevel=None, crossed=False) -> List[PairWarning]`, where
     `PairWarning(gear: str, depth_mm: float, message: str)` names which gear's tip reaches and how far past the
     half-nozzle margin. The stub returns `[]`;
   - `ring_tip_clearance(...)`, of `tip_clearance`'s signature. The stub returns `tip_clearance`'s figure;
   - `printed_tip_thickness(module, teeth, pressure_angle, helix_angle, shift, nozzle) -> float`. The stub returns
     `tip_thickness`;
   - `solve`'s keywords `process="machined"` and `nozzle=0.4`, accepted and ignored by the stub;
   - `shift_for_centre`'s keyword `printed=False`, the same.
5. **The workbook's names:**
   - `model.Box.process = "machined"` and `model.Box.nozzle = ""`;
   - `schema.Setting.words: Tuple[str, ...] = ()`;
   - `assess.blank_process(record) -> str`, written whole (§1.3: it is D11's switch);
   - `assess.assess(..., blank_process=PROCESS_PRINTED)`;
   - `Gear.spec_values` passing `process` and `nozzle` from the Box.
6. **The form's names:** `gui.GEAR_COMPOUND` gains `process` and `nozzle`, so `test_gui_spec.py:49-52` stays
   green. `_gear_spec` does not yet set them.
7. **The record:**
   - `store.LINK_SCHEMA_VERSION = 11` with `_W9D_LINK_SCHEMA = 10`;
   - `store.PRINTED_SCHEMA = 3` and `SCHEMA_VERSION = 3`;
   - `sidecar_schema` giving 3 for a printed spec;
   - the eight pinned lines of §1.2 moved.
8. **The labels and words:**
   - `update._SPEC_COLUMNS`'s new pair is `("process", "Process")`;
   - every new sentence's words go in the note: the checks of §2.2 and §2.3, K11's two (§6), the Box's error and
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
(item 2 and item 3 only), `gears/pair.py` (stubs), `workbook/model.py` (item 5's lines), `workbook/schema.py`
(`Setting.words`), `workbook/assess.py`, and `gui.py` (`GEAR_COMPOUND`). The whole suite and §2.7's pins
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
  - Files: `workbook/schema.py` (the Process and Nozzle settings, the Backlash column's blank words, `:155`),
    `workbook/model.py` (`_read_box` keeping the blank, the word check, `to_sheets`, `template`),
    `workbook/checks.py` (the pair check at each Meshes row; the planetary sentence when printed, with
    `report.undercut` still filled), `workbook/update.py` (`_SPEC_COLUMNS`), and `swbuild.py` (K11's words
    only, `:5460-5489`).
  - Tests: `test_workbook_checks`, `test_workbook_update`, `test_workbook_gearbox`,
    `test_swbuild_user_work` (K11's words), and a new `test_printed_workbook.py`, which also reads the committed
    workbooks printed and tests `blank_process` with each kind of record. `test_workbook_model` was F1-0's; B
    adds its Box tests to the new file instead, so the ten files stay F1-0's alone.
- **C, what the user sees.**
  - Files: `gui.py` (the rows, `_gear_spec`, `_load_record`, Solve passing the process), `ui_text.py` (the
    backlash readouts' third state, the explainers, the Workbook panel's Process line), `workbook_gui.py` (`_plan`
    reading the record before `_assess`, which passes `blank_process(record)`; the panel's line), `design/` (the
    board first: the strip with its Process row, and a gearbox built before F1 opened Machined, then typed Printed),
    `README.md`.
  - Tests: `test_gui_spec`, `test_ui_text`, and a new `test_printed_window.py` for the window.
    `test_workbook_window.py` is F1-0's; its pinned panel text for every gearbox moves by the Process line (open
    point 3). C rewrites those lines there after F1-0 is in, as its only edit to that file, and no other package
    touches it.

B's `checks.py` calls A's pair check, and C's readouts read the derived gear's properties and the Box's resolved
Process. Each meets the others only through item 1 to 8's names. For two implementers in place of three, A and B
are one package (the model) and C the other (the view). The review then reads the merged head, and one SolidWorks
run follows.

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
  - the ring cases with the half-nozzle margin: RangeBox 13 in 55 (0.401 mm) warns, planetary_4to1's 18 in 54
    (0.108 mm) does not, Risky_Placements' 14 in 36 warns, and E4's 24 in 72 is clear;
  - the planetary sentence said once when printed and as today when machined, with `report.undercut` filled either
    way.
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
- **D6** is warnings on printed pairs only. Changing their wording, threshold or margin later moves no machined
  pin. Drawing the true undercut would be a plan of its own, and nothing in F1 stands in its way.
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
4. In a printed planetary stage the pair check replaces W7's undercut sentence, the warning only, with
   `report.undercut` still filled (§2.3). *Confirmed with that condition.*
5. The link record goes to 11 whatever the process, as W9b's 8 did. *Confirmed.*
6. F2's export refuses a part the record marks unsaved or mismatched (§3.1). *Confirmed.*
7. **New:** the pair check's half-nozzle margin (§2.3), proposed so the ring warning keeps its meaning.
8. **New:** D11 answered (B) by the coordinating session.


## 3. Stage F2 — the file for the slicer, and the first prints

### 3.1 Export

**Export STEP** goes on the form, for the active built gear, and in the Workbook window. In the window it exports
every distinct part of the built gearbox into `print/` beside it, with a text list: each part, how many to print,
and the settings of *Sources* (flat on the bed, five walls, 35 % infill or more, 0.2 mm layers, first-layer
compensation 0.15 to 0.2 mm, the seam off the tooth roots, grease). The app keeps its rule: it never writes over a
file, and an export that exists is named `_r2`.

What W9 adds to the window's side of it:

- *Every distinct part* is the record's current revision (`store.LinkRecord.current_parts`, `store.py:1015`),
  hubs and sleeves among them. Carrier parts (axes and planes only) and the layout are not exported, and neither
  are the user's own components.
- A gear part holding a feature of the user's (a keyway) is exported as it stands in its file, feature and all;
  the list says so.
- **The export refuses while the record marks a part unsaved or mismatched** (W9a's marks, `update._mark`,
  `workbook/update.py:676-683`), naming each part. A STEP written from a document whose changes are not saved is
  not the file on disk, and the record does not vouch for it.
- The button sits in the footer's button row, which K12 keeps whole on a short screen (`design/UI-DESIGN.md:406-420`).

`IModelDocExtension.SaveAs3` to a `.step` name is a call the app has not made. It writes a file and may raise a
dialog, so by the rule it is **probed first**. Today `swcom.Session.save_as` (`swcom.py:1358-1368`) calls it with
`findings.SAVE_AS_SILENT` to save a part under its own name. The probe uses a scratch part and checks two things:
that the call returns without a dialog, and that it leaves the part's own path and modified mark as they were (a
save under a new name renames a document; an export must not).

On SolidWorks 2024, W9a's ruling lets a What's Wrong box come and go by itself during an Update. That ruling is not
assumed for an export: the probe also exports a part that holds a feature in error, and any box it raises is the
STOP until it is ruled on.

The file is checked without SolidWorks, by counting the solids in its text, since opening a STEP in SolidWorks can
raise import dialogs of its own. There is one short run on 2026, and the same on 2024.

### 3.2 The user prints and measures

No rig, and no gear has to fit a shaft:

1. **One spur gear**, module 1.5, 20 teeth, face 8, no bore, at the default backlash. Calipers across
   the teeth the panel names; the reading less the panel's span is twice what this printer adds to a
   flank. D3's 0.3 mm assumes about 0.1 mm a flank and leaves the rest as running play.
2. **A bore coupon**: a plain disc with the user's shaft size cut at + 0, + 0.1, + 0.2 and + 0.3 mm
   (four typed bores; the app's own gears with few teeth will do). The one the shaft goes into as wanted
   is F3's bore allowance.
3. **Then a pair** on the user's own shafts, if they have a place to run one: the smallest backlash
   that turns through whole turns under light load without a tight spot, before and after a short run.
   A centre distance out by 0.1 mm moves the play by 0.07 mm, so this confirms the first measurement; it
   does not replace it.

**Done when:** the probe's findings are in `findings.py`; a gear built by the app exports; the STEP
opens in the user's slicer (the user's step); the measurements of 1 and 2 are written down here and
D3's number and F3's allowance are set from them; reviewed. **Cost:** two short SolidWorks runs; two
agent runs and the review.


## 4. Stage F3 — the bore (existing ops only)

### 4.1 Bore allowance

A printed bore is cut at `"Bore Diameter" + "Bore Allowance"`, so `"Bore Diameter"` stays the shaft's size.
Blank is the figure §3.2 found (0.2 mm on the diameter until then).

- The global and the changed link exist only when the allowance is not zero, as `"Profile Shift"` does, so going
  between none and some is structural (`swbuild.structural_change`, beside `has_shift`, `swbuild.py:1319-1329`).
  A change of size is a value.
- A form row and a Gears column, `Bore allowance`.
- A bevel gear's bore (its own code in `bevel.py`) takes it the same way, and so does a hub row, whose bore W9b
  built from the row's Bore with its fixing left to the user: this is that fixing.
- An allowance given to a built part *in place*, as W9c gives a sleeve its bands, is not in this plan. It would be
  a new kind of write by Update, gated per version as W9c's are. So none ↔ some stays a new part.

**A printed part built before F3 has no allowance, and its record has no key for it.** It reads as allowance 0, by
§1's rule (`to_dict` leaves `bore_allowance` out at 0, and `drive` out at `round`), and so it stays a true record
of what it is. Giving it an allowance means a new part: Build again… in a workbook, or a new name on the strip.
That includes §3.2's test prints.

**F3 moves the link record to schema 12, whatever its parts, as F1's 11 is**: one policy, the record's number set by
the app that writes it. A part with an allowance or a flat is written at **sidecar schema 4**, and a part without
keeps its number, as §1.2's sidecar rule does. An F1 app would otherwise read such a part without either and write
the record back without them. `test_store.py:833` parametrises a literal 12 as "newer"; that line changes at F3.

### 4.2 D-flat

`Drive` is `round` or `flat`; `Flat` is the shaft's size across its flat. The bore sketch becomes an arc and a
chord, made from ops the app already has (`Arc`, `Line`, `Relation`, `Dimension`), and the flat takes half the
allowance. Changing Drive is structural (`drive` joins `swbuild.STRUCTURAL`, `swbuild.py:1291`, with a missing
key read as `round`). The Gears sheet gets columns `Drive` and `Flat`. The rim check is unchanged: the thinnest
wall is at the round part, never at the flat.

### 4.3 What W9 asks of F3

- **K11.** `"Bore Allowance"` and the flat's global join `update._GLOBAL_COLUMN` (`workbook/update.py:670-673`),
  so that K11's sentence names their cells, as it names Bore's.
- **W9d's carry.** `update._SPEC_COLUMNS` (`:3196-3201`) gains Bore allowance, Drive and Flat, so a part made new
  by them says why.
- **W9d's "bore".** `update._bore_mm` (`:3245-3254`, `CarryBody.bore_mm`) gives the hole as cut, Bore plus
  allowance, for a printed part. Without that, W9d's word "bore", which needs a coaxial cylinder of exactly the
  recorded radius (to 1e-4 mm, `W9D-INTERFACES.md` §4.4), would never name a printed bore, and a mate on it would be
  said as on *a face of Sun on its axis*.
- **Mates on faces.** A mate of the user's on the bore face of a part made new by its allowance or drive is named,
  not found again, by K5's ruling (no finding by geometric role).

### 4.4 The edge chamfer is not here (D9)

The first draft put a chamfer on both end faces by selecting each face. The review found the app has
never selected a face or an edge (every selection is a feature, plane or sketch entity by name), so
that is new traversal code for four kinds of end face, not one call; that a chamfer of 0 cannot be a
value; and that at module 1 a 0.3 mm chamfer leaves 0.06 to 0.14 mm of tooth near the tip on the bed
face. A chamfered blank made by the existing `Revolve` needs no new call but relieves the tips only,
and the squish that binds a mesh is on the flanks. Every slicer has the setting that deals with it. If
the prints of §3.2 show that is not enough, the chamfer gets a plan of its own.

**Done when:** printed spur, helical, herringbone and bevel gears build on SolidWorks 2026 with
allowance and flat, every sketch fully defined, volumes against the maths; Update values carries a
change of allowance and of Flat, and refuses a change of Drive and an allowance going to or from none,
each with its sentence; a workbook gearbox of printed gears builds, turns and shows no interference;
one confirming build on 2024; reviewed. **Cost:** an estimate, not a measurement: two SolidWorks runs
of the order of half an hour on 2026 and one on 2024; three agent runs and the review.


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
  - Every new check is for printed gears, which is why the pair check is printed-only.
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
    `:430-497`), and backlash widens the space evenly about that centre. That is read from the code, not measured.
    So route (c1)'s puts and K2's refusals are not met.
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
- **The half-nozzle margin is an inference (§2.3).** If a printed tip is not rounded as assumed, some at-risk ring
  pairs go unwarned. It is one constant, and §3.2's pair print is the first place it can be seen.
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
