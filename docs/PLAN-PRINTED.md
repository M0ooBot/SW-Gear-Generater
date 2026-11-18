# Gear Generator — gears made to be 3D printed in PLA

**Drafted on 2026-11-16 and revised the same day to its first review (`docs/PLAN-PRINTED-REVIEW.md`) and to the
user's answers; revised again on 2026-11-18 against the code as W9 leaves it, read at `c2d95cc` on branch `w9d`.**
W9's code there is written and shown on SolidWorks 2026; only its confirmation on SolidWorks 2024 was still running.
On 2026-11-16 the user said *"w9 first, dont actually build anything yet"*. On 2026-11-18 the user told the
coordinating session to carry on past W9 down the plans, so this plan comes next. **Nothing of it is built yet. Two
things must happen before any code.** First, this revision is reviewed by a subagent, since the first revision never
was; the review also rules on the points listed at the end of §2.8. Second, W9 is merged into `workbook` and the
branch `printed` is cut from it. If W9's 2024 runs change `src/` after `c2d95cc`, every part of this plan that
cites a changed file is read again before F1 starts.

D3, D6 and D7 still stand as assumed. §2.8 says why F1 can go ahead on them. D11 is new and is put to the user.

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
  26, 15 up to 45, 16 up to 101; 12 and fewer clear nothing.
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
sheet's Process setting. A gear the code builds without saying which is machined. That covers a record written
before F1, a test, a probe script and a design board, and it is what keeps the rule with no edit to any of them
(§1). What the default carries with it is also in §1.


## Decisions wanted

Each row has the answer this plan assumes; say where it is wrong.

| | Question | Assumed |
|---|---|---|
| D1 | How is a gear marked? | **Answered 2026-11-16.** A **Process** row on the form, `Printed` or `Machined` (one row for a pair), and a `Process` setting on the workbook's Box sheet for the whole gearbox. The Box setting is a word, checked as it is read (§1). |
| D2 | What is the default? | **Answered 2026-11-16: `Printed`, everywhere, the workbook too.** A blank Process row or Box setting is Printed. Only two things read as Machined: the record of a part built before F1, which has no Process, and a spec the code builds without saying (§1). |
| D3 | Printed backlash when the cell is blank | **The smaller of 0.3 mm and 0.3 × module**, per gear: 0.3 mm from module 1 up (0.14 mm off each flank, measured square to it), and today's value below module 1. Never more than today's, so nothing that builds today is refused. To be replaced by the user's own measurement (§3.2). F1 can go ahead on it (§2.8). |
| D4 | Which shaft drive first? | **Answered 2026-11-16: D-flat.** Hex and a keyway are the same kind of sketch and can follow; a boss with a setscrew or a heat-set insert is not in this plan. |
| D5 | The file for the slicer, and which slicer | **Answered 2026-11-16: the user's slicer is Bambu Studio, so STEP.** Bambu Studio is said to open STEP; F2's own step, the user opening an exported gear there, is what shows it. No STL export. |
| D6 | Undercut | **Warn, and check each printed pair for it** (§2.3); drawing the true undercut root is another sketch topology and not in this plan. F1 can go ahead on it (§2.8). |
| D7 | PLA's allowable tooth stress | **Provisional: 17 MPa**, a third of the roughly 50 MPa a PLA datasheet gives, against a stress that includes the fillet's concentration (§5). No standard gives a figure for printed PLA, so this is the writer's judgement, typed on the Box sheet and replaced by the user's own tests. F4's only; F1 does not touch it. |
| D8 | Where this sits beside W9 | **Answered 2026-11-16: W9 first; on 2026-11-18 the user said to carry on past W9.** This plan starts once W9 is merged into `workbook`, on a branch `printed` cut from it. What it takes on from W9 is in §6. |
| D9 | The edge chamfer against first-layer squish | **Answered 2026-11-16: left to the slicer for now.** Not built in F1 to F4; the export's print list asks for the slicer's first-layer compensation. The review found the chamfer is the costliest piece here (§4.3). It gets a plan of its own only if the test prints show the slicer's setting is not enough. |
| D10 | A printed part's file name | **Answered 2026-11-16: ends `_P`** (`Gear_m1.5_N25_P`), as a shifted gear ends `_x0.09`. It is a different part from the machined gear of the same sizes, and without the mark the second of the two would be refused as existing. Machined names stay as they are. As W9b ruled for a sleeve's bands (`W9B-INTERFACES.md` §7), the mark is the default name only. An Update that makes a built machined part printed keeps its file and name, since a default stem that drifts with the values is a value change (`gearbox.name_changed`, `workbook/gearbox.py:405-415`). So only a part *built* printed carries `_P`. |
| D11 | A gearbox already built, opened after F1 (new, for the user) | **Assumed, from D2: it reads Printed and *changed since it was built*.** Update SolidWorks would give every gear the printed backlash in place, under W9a's rules for the user's work. Build again… would make every gear a new part, and W9d would carry the user's components onto those parts. `Machined` typed on the Box sheet keeps the gearbox as built. The other answer is that a workbook whose record was written before F1 reads Machined until Printed is typed (§1). |


## 1. What `Printed` means

Two new fields on `GearSpec` (`spec.py:134-159`), after the bands:

- `process`: `printed` or `machined` (`spec.PROCESS_PRINTED`, `spec.PROCESS_MACHINED`). A reader,
  `GearSpec.process_value()`, checks the word as `teeth_side_value` checks Side (`spec.py:223-227`), and
  `is_printed()` answers it. **The dataclass default is `machined`, and so is a blank.** That is what a spec
  written before F1, or built in code without saying, means. The user never meets this default: the form's Process
  row starts at Printed and a blank Box setting is Printed, and both write the word into every spec they make
  (below).
- `nozzle`: the line width in mm, `0.4` when blank. It is used by checks only and changes no plan, so the as-built
  comparison already sets it aside (`update._ignored_fields_as_built`, `workbook/update.py:244-266`, ignores any
  field whose built value leaves the wanted plan as it is).

**The record.** `GearSpec.to_dict` (`spec.py:161-167`) leaves out `process` and `nozzle` when the spec is
machined, as W9b made it leave out a sleeve's blank bands. So a machined part's `.gear.json` and its record entry
are byte for byte what W9 writes. `GearSpec.from_dict` (`spec.py:169-172`) then needs no change: a missing key
takes the dataclass default, machined, which is what a part built before F1 is.

This replaces the first revision's design of one record reader that filled a missing key with `machined` while
the dataclass said Printed. That design would have turned the suite's 200 hand-built `GearSpec`s printed. It would
also have needed every caller of `from_dict` to remember the rule; there are six, at `update.py:304` and
`:1680`, `swbuild.py:1374`, `gearbox.py:444`, `spec.py:376` and `gui.py:1470`.

Some comparisons read raw spec dicts instead of `GearSpec`s. Each takes `machined` for a missing `process`, as
each already takes `external` for a missing `teeth_side`:

- `swbuild.structural_change` (`swbuild.py:1291-1358`) and `update._structural` (`update.py:276-287`):
  `process` is not structural in F1, so nothing changes there until F3's Drive;
- W9d's `update._changed_columns` (`update.py:3210-3219`), which gains Process (§6);
- `gui._update_target` (`gui.py:1496-1515`), through `structural_change` and the variables it counts.

Four functions read through `from_dict` and need nothing: `gearbox.same_part` and `_matches`
(`gearbox.py:418-449`), `update._part` (`update.py:294-337`) and `gui._load_record` (`gui.py:1460-1487`).
A test holds each to the rule (§2.7).

**The schemas.**

- The link record goes to **schema 11** (`store.LINK_SCHEMA_VERSION`, `store.py:421-426`, with
  `_W9D_LINK_SCHEMA = 10` kept beside it as each stage's number is). It is written at 11 whatever the parts'
  process, as W9b's schema 8 was. The pin `tests/test_store.py:227` (`== 10`) moves with it.
- The `.gear.json` goes to **sidecar schema 3** for a printed part (`PRINTED_SCHEMA`). `store.sidecar_schema`
  (`store.py:88-92`) gives 3 for a printed part, and 2 for a banded part or 1 as now; `store.SCHEMA_VERSION`
  (`store.py:35`) becomes 3.

The first revision left open what an older app does with a newer schema, and made a STOP of it. That is now read
and answered. `store` refuses a link record past its own schema (`UnknownSchema`, `store.py:1461-1464`) and a
`.gear.json` past its own (`store.py:212-218`), and leaves each byte-identical; `tests/test_store.py` holds
both. So a W9-era app refuses an F1 record and never writes a printed part's backlash back.

A W9-era app reading an F1 *workbook* that has no record skips the Box's Process and Nozzle rows, as it skips any
label it does not know (`model._read_box`, `workbook/model.py:348-350`), and builds the gearbox machined. That
is the same acceptable failure W9b accepted for a banded sleeve read by an older app.

**The form.** A **Process** row (`Printed` · `Machined`) goes in the Gear panel under Make, one row for both gears
of a pair. **Nozzle** (mm, placeholder *0.4*) goes under it, shown while Process is Printed.

- Both are fields the two gears share, like Kind and Flank. `gui.GEAR_COMPOUND` (`gui.py:83`) gains `process`
  and `nozzle`, and `_gear_spec` (`gui.py:1110-1133`) puts them into each gear as it puts Kind and Flank.
- The first revision said `pair.apply` carries them. That was wrong: `pair.apply` writes only module, teeth,
  shift and the pair's angles (`pair.py:860-880`) and leaves the rest of each gear as the form gave it, so a
  Solve keeps the form's Process.
- `tests/test_gui_spec.py:49-52` keeps holding the form's fields to `fields(GearSpec)`.
- The row starts at Printed. It is not taken from `GearSpec()`, as the other fields are (`gui.py:154-164`).
  `_load_record` sets it from the record, so a `.gear.json` from before F1 opens as Machined.

**The workbook.** Two Box settings go into `schema.BOX_SETTINGS` (`workbook/schema.py:102-112`), after Efficiency:

- **Process**: a word, blank meaning Printed. Its note: *Printed or Machined: a printed gear gets a backlash for a
  printer and is checked against the nozzle.*
- **Nozzle**: mm, numeric, blank meaning 0.4.

The Box sheet has no drop-down lists (`to_sheets` gives lists to table columns only, `model.py:612-618`), so the
word is checked as it is read. Anything but Printed or Machined, in any case, is an error at its cell: *Process is
Printed or Machined (got 'x').* `schema.Setting` (`schema.py:88-99`) has no field for a word list today and
gains `words`.

`model.Box` (`model.py:27-41`) gains `process` and `nozzle`.

- As in `GearSpec`, the dataclass default is machined, and `_read_box` (`model.py:337-376`) writes Printed for
  a Box sheet whose Process is blank or missing.
- `to_sheets` (`model.py:598-610`) writes the word as held, so a gearbox built in code and written out reads
  back machined.
- `template` (`model.py:638-640`, behind *New workbook…*) writes Printed and 0.4.
- `Gear.spec_values` (`model.py:115-137`) fills both into each gear, and `tests/test_workbook_model.py:389-390`
  keeps holding it to `fields(GearSpec)`.

The workbook stays at Format 1, as W8 and W9b added to it at Format 1.

What the default carries with it:

- **An old `.gear.json` opens as Machined**, since that is what was built. Changing its row to Printed is a change
  of one global's text, which Update values carries.
- **A workbook without a `Process` setting is now Printed (D11).** So every gearbox built before F1 reads as
  *changed since it was built*. That includes the user's own (the issue's RangeBox with their sprockets, housing
  and keyway) and W9's demonstration masters. Each part's `"Backlash"` goes from `0.3 * "Module"` to §2.1's
  equation, which is a value change.
  - Update SolidWorks carries it in place under W9a's rules. K11 reads every owned global live first. A part the
    record marks unsaved or mismatched is said as W9a says it.
  - Build again… would make every gear a new part, since a part is reused only when its globals are as recorded
    (`gearbox._matches`, `gearbox.py:440-449`). W9d would then carry the user's components onto the new parts and
    name every mate on a face of an app part it cannot make again.
  - Typing `Machined` on the Box sheet keeps the gearbox as built.
  - The footer says this whenever the only changes are these, every time; there is no stored "first time". What
    Build again… says is in §6.
- **New workbook…** writes `Process` `Printed` and `Nozzle` `0.4`.
- **No `Process` custom property.** Update writes globals and never properties, so a property would go
  stale the first time Update changed a part's process. The record and the file name carry it.
- **Sleeves, dogs and hubs** pass `process` through to the spur and ring kinds they are built from, and take the
  printed backlash as those do. `clutch._Clutch._as_spur` (`gears/clutch.py:109-112`) replaces kind, side, helix
  and shift and keeps the rest. A sleeve on its dog or hub is a coupling, not a Meshes row. Its play is the two
  backlashes: 0.6 mm at the pitch circle when printed above module 1, against 0.6 × module machined.


## 2. Stage F1 — defaults and checks (no new SolidWorks call)

### 2.1 Backlash

Blank backlash on a printed gear is `IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )`. It has the shape of the depth
IIF the app already writes (`spur.py:771`), and IIF was probed in P1 (`probe/p1_equations.py:109`), so no kind
of equation is new.

- It is written by all five variable writers (`spur.py:743`, `helical.py:371`, `internal.py:895` and `:973`,
  `bevel.py:640`) and the four `derive`s (`spur.py:714`, `helical.py:333`, `internal.py:878`, `bevel.py:452`),
  from one pair of constants beside `BACKLASH_FACTOR` (`spur.py:86`).
- The card shows it as a default, *0.3 mm · printed default*: a third state beside typed and `0.3 × module`.
  `SpurDerived` (`spur.py:149`) gains `backlash_printed`, set by the derive, and `ui_text` reads it where it
  now reads `backlash_typed` (`ui_text.py:128`, `167`, `517-523`).
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

Each gear's checks see `spec.process` and `spec.nozzle` through each kind's `validate(spec, derived)`, so no
signature changes. That answers the first review's finding 14, which was about where the nozzle lives.

- **Tip:** the tip thickness after backlash under one nozzle width, measured at the toe on a bevel gear. It goes in
  `spur.section_diagnostics` (`spur.py:822-898`) beside today's thin-tip warning. With the default it warns at
  module 1 (0.27 to 0.45 mm from 12 to 40 teeth). It passes at module 1.25 from 12 teeth, and at module 1.5 from 8
  teeth (0.58 mm at 12, 0.71 at 20); a 6- or 7-tooth pinion warns.
- **Module:** under 2.5 × nozzle (1.0 at 0.4 mm). This is the guides' floor, below which a profile rounds off.
- **Radial clearance, per pair:** the clearance at the working centre distance under 0.3 mm, less a rounding
  tolerance. Two printed surfaces take about that.
  - `pair.tip_clearance` (`pair.py:190-204`) covers outside pairs, and Gleason's figure covers a bevel pair.
  - A ring pair's clearance is new pure code beside `tip_clearance`: the pinion's tip to the ring's root, and the
    ring's tip to the pinion's root. `internal.tip_clash` (`internal.py:381`) is the tip clash, not this.
  - On the form the check is said through `pair.mesh_warnings` (`pair.py:989-1009`, shown at `gui.py:1300`). In
    a workbook it is said at each Meshes row from `checks._check_mesh` (`workbook/checks.py:378`).
  - Unshifted spur and helical pairs pass from module 0.75. **Bevel pairs warn under module 1.6** (Gleason's
    clearance is 0.188 × module), and shifted pairs warn wherever the shifts have eaten the clearance.
  - The depth is left alone; the sentence says to use a larger module or less shift.
- **Rim:** the wall between the bore and the root under three nozzle widths. This is a printability floor only.
  Today's one-module warning (`spur.py:881-884`) is the stricter above module 1.2 and stays.
- **Helix:** a helix angle over 45°, a flank that prints as an overhang. It is conservative by a few degrees, since
  the flank's own angle is the base helix angle.
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
  `ra₂ ≤ √(rb₂² + (C sin αw)²)`, and the same with the gears exchanged;
- **ring and pinion:** the ring's tip must not reach inside the pinion's tangent point,
  **`ra₂ ≥ √(rb₂² + (C sin αw)²)`**. The first draft had this the wrong way round: it cleared three of the repo's
  own rings that fail and warned on one that passes;
- **bevel pair:** the outside condition on the Tredgold pair at the back cone, with Gleason's addenda
  (`pair.bevel_candidate`, `pair.py:675`, already uses that pair for its clash);
- **crossed helical pair:** no pair check. Each gear's own undercut limit stands, and the sentence says that is all
  that was checked.

A sleeve on its dog or hub is a coupling of equal tooth counts, not a pair, and is not checked here.

In a **printed** planetary stage this check takes the place of the sentence that already says the same thing
(`checks._check_stages`, `workbook/checks.py:358-366`, "is below the undercut limit, which is not modelled, and
meshes …"), so nothing is said twice. A machined stage keeps that sentence word for word.

It is a warning, not an error: the app cannot say the drawn root meets the tip, only that the pair is at risk.
By the review's working, RangeBox's Planet 13 in Ring 55 at module 1.25 is at risk when printed.

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
  `range_box` and `range_box_fixed` in `tests/workbook_fixtures.py`). Beside them, `BEFORE_W8`'s nine and W9b's pinned counts (`tests/test_workbook_rangebox.py:19-27`: four warnings and
  W9b's three) stay as they are;
- the bytes of a machined part's `.gear.json` and of its record entry, plain and banded;
- **what Update, the strip and Build again… say for a record written before F1 (no `process` key) against a form
  or workbook marked Machined, which must be nothing.** That is `update.classify` with no change,
  `gui._update_target` counting 0, `gearbox._matches` reusing the part, and W9d's `update._changed_columns`
  giving `[]`.

After F1 each is taken again and must be identical.

**What has to be marked machined.** A `GearSpec` or `Box` built in code without saying is machined (§1), so most
of the suite needs no edit:

- the 200 `GearSpec(` constructions in 27 test files (the first revision counted 194 in 24 before W9);
- the gearboxes built in tests and probe scripts (`tests/workbook_fixtures.py`, `probe/p7_workbook.py`,
  `probe/p8_motion.py`, `probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, W9's
  demonstration scripts);
- the boards in `design/canvas/gen.py`.

What reads printed is what a user's blank reads. That is `model.template()`, and the five committed workbooks that
Excel or LibreOffice saved, which have no Process row (`tests/fixtures/excel-windows/`'s three,
`tests/fixtures/excel/`'s and `tests/fixtures/libreoffice/`'s Reducer). A test that pins a fingerprint, a count
or a sentence of one of them marks it machined as read (`replace(spec, box=replace(spec.box,
process="machined"))`), `BEFORE_W8`'s three among them. The other tests read it as a user would, printed, which
exercises printed on files Excel wrote.

W9's masters on the Windows host (`<probe folder>\...`) were written before F1 and have no Process row. If a W9
demonstration is ever run again with an app at or after F1, the script first writes Machined into its master's Box
sheet.

### 2.8 F1, ready to execute

**What F1 changes, by file.** Lines are as of `c2d95cc`; each is found again on the branch before it is relied on.

| File | What |
|---|---|
| `spec.py` | `process` and `nozzle` fields, their words and readers (`process_value`, `is_printed`, `nozzle_mm`), `to_dict` leaving both out when machined (`:161-167`), the `_P` stem in `default_stem` (`:285-317`) for a printed spec |
| `gears/spur.py` | the printed backlash constants and equation (`:86`, `:714`, `:743`), `SpurDerived.backlash_printed` (`:149`), the printed tip, module, rim, helix and undercut sentences in `section_diagnostics` (`:822-898`) |
| `gears/helical.py`, `internal.py`, `bevel.py` | the same equation and derive (`helical.py:333`, `:371`; `internal.py:878`, `:895`, `:973`; `bevel.py:452`, `:640`); the ring-fillet sentence; the bevel tip at the toe |
| `gears/pair.py` | the printed pair check (outside, ring, bevel), ring-pair radial clearance, the printed tip after backlash, printed thresholds in `_shifted` and `shift_for_centre`, `solve`'s keywords and ranking, `mesh_warnings` printed |
| `workbook/fixes.py` | `shift_fix` passing the gear's process to `shift_for_centre` (`:173`) |
| `workbook/schema.py` | the Process and Nozzle settings, `Setting.words` (`:88-112`); the Backlash column's blank words (`:155`) |
| `workbook/model.py` | `Box` fields (`:27-41`), `spec_values` (`:115-137`), `_read_box` with the word check (`:337-376`), `to_sheets` (`:598-610`), `template` (`:638-640`) |
| `workbook/checks.py` | the printed pair check at each Meshes row (`_check_mesh`, `:378`), and the planetary sentence taken over when printed (`:358-366`) |
| `store.py` | link schema 11 (`:421-426`), `PRINTED_SCHEMA` 3 and `sidecar_schema` (`:30-35`, `:88-92`) |
| `workbook/update.py` | `_SPEC_COLUMNS` gains Process with `machined` for a missing key (`:3196-3219`); `UpdatePlan` says which parts change only because of Process, for the footer |
| `workbook/gearbox.py` | a part that would be reused but for its Process is made new with that reason (a third `made_new` reason beside `UNSAVED` and `MISMATCHED`), so W9d's question can say how to keep it (§6) |
| `swbuild.py` | K11's words for the printed default: `_blank_meaning`, `_wanted_words` and `_back_words` (`:5460-5489`); no SolidWorks call changes |
| `gui.py` | the Process and Nozzle rows, `GEAR_COMPOUND` (`:83`), `_gear_spec` (`:1110-1133`), `_load_record` (`:1460-1487`), Solve passing the process |
| `ui_text.py` | the backlash readouts' third state (`:128`, `:167`), the Backlash explainer (`:366-370`, `:517-523`), the Process and Nozzle explainers, the footer's Process sentence (`workbook_footer`, `:2495`), the Process case in `_reuse_advice` (`:5440-5463`) |
| `workbook_gui.py` | the Workbook panel's Process line (open point 3 below) |
| `design/canvas/gen.py`, `design/UI-DESIGN.md`, `README.md` | the boards (the strip with its Process row; a W9-era gearbox read printed); the Gear panel rows (`UI-DESIGN.md:42-48`), the Backlash hint (`:96`), the Workbook panel (`:446-454`); the README's backlash lines (`:38`, `:187-189`) |

**What must not move.**

- Every pin W9 left: `BEFORE_W7` and `BEFORE_W8`, with the three xlsx marked machined as read (§2.7).
- RangeBox's four warnings and W9b's three; the W8 fixtures' counts, each moved by three in W9b.
- Every test of W9a to W9d against the fake, unchanged, since their fixtures are built in code and so are machined.
- `tests/test_findings.py`: F1 adds no finding, and every 2026 and 2024 value, gate and pinned log line stays.
- W9's demonstration scripts' self-checks.
- No SolidWorks call is added or changed.

**Tests F1 owes against the fake**, beside §2.7's pins:

- *The default, where the user chooses:* a blank form, a blank Box and a Solve applied to a blank form each give
  printed specs; the form's Process covers both gears of a pair. `test_gui_spec.py` and
  `test_workbook_model.py:389` still hold the fields.
- *The record:* a printed spec's `to_dict` and sidecar (schema 3) and a link record at 11. A schema 10 record from
  W9 reads, and its parts are machined. A schema 12 record is refused and left byte-identical. Machined bytes equal
  W9's.
- *The Box:* the Process word check (any case; an error at the cell for anything else); Nozzle positive; New
  workbook writes Printed and 0.4; `to_sheets` / `from_book` round trips of both words.
- *The equation:* its text in each of the five writers, and the derived backlash at modules 0.5, 1 and 1.5 (equal
  to the machined value at module 1 and below, never more than it).
- *Each check of §2.2 and §2.3*, with the figures this plan gives: tip 0.27 mm at module 1 and 12 teeth; the module
  floor; clearance at module 0.75 passing within the tolerance; bevel pairs under module 1.6; the rim; helix 45°;
  the ring-fillet sentence. The review's four ring cases come out right (RangeBox 13 in 55, planetary_4to1's 18 in
  54 and Risky_Placements' 14 in 36 at risk; E4's 24 in 72 clear). The planetary sentence is said once when printed
  and as today when machined.
- *Solve and the fixes:* printed ranking and marking; no row with a pointed tip; machined rows equal to the pin.
- *K11:* the sentence for a printed default the user changed in SolidWorks names it in words, not as an IIF.
- *A gearbox built before F1:* RangeBox built machined against the fake, then read with a blank Process. Every
  part reads *changes on Update* for Backlash alone, and none needs a new part or a put. The footer's Process
  sentence is said, and Update runs end to end on the fake. With `Machined` typed on the Box, nothing changes.
  Build again… on the same names each part's reason as *its Process changed*, and the question says how to keep
  the user's features (§6).

**Packages.** One sequential step, then three packages with disjoint files that run in parallel against one
interface, then the review. W8 and W9 split their work the same way.

- **F1-0, the pins and the interface** (one agent, before the others):
  - first, `tests/test_printed_rule.py` with §2.7's pins, taken and committed at the base before any `src`
    change;
  - then the interface commit: `spec.py` whole (it changes nothing a test sees, since the default is machined
    and the new keys are left out of a machined record), and the shared names as stubs (`SpurDerived.backlash_printed`
    False; `pair.printed_pair_warnings` and the printed tip raising `NotImplementedError`; the field on
    `UpdatePlan`; the `made_new` reason);
  - and a note, `docs/notes-printed/F1-INTERFACES.md`, with the signatures, the words of every new sentence and
    the constants.
  - The interface commit keeps the suite green. The two tests that hold the form and the workbook to every
    `GearSpec` field (`test_gui_spec.py:49-52`, `test_workbook_model.py:389-390`) would fail on the new fields, so
    it also adds `process` and `nozzle` to `gui.GEAR_COMPOUND` and to `Gear.spec_values` at the machined default.
    Packages C and B then complete them.
  - The pins pass at both commits.
- **A, the gear maths** (pure): `gears/spur.py`, `helical.py`, `internal.py`, `bevel.py`, `clutch.py` if it
  needs anything, `pair.py`, `workbook/fixes.py`. Tests: `test_gears_spur`, `_helical`, `_internal`,
  `_bevel`, `_clutch`, `_pair`, `test_profile_shift`, and a new `test_printed_gears.py`.
- **B, records, the workbook and Update:** `workbook/schema.py`, `model.py`, `checks.py`, `update.py`,
  `gearbox.py`, `store.py`, and in `swbuild.py` K11's words only. Tests: `test_store`, `test_workbook_model`,
  `_checks`, `_update`, `_gearbox`, `_carry`, `test_workbook_modes` (the xlsx marked), `test_swbuild_user_work`
  (K11's words), and a new `test_printed_workbook.py`.
- **C, what the user sees:** `gui.py`, `ui_text.py`, `workbook_gui.py`, `design/` (the board first, as every
  stage has drawn it), `README.md`. Tests: `test_gui_spec`, `test_ui_text`, `test_workbook_window`.

B's `checks.py` calls A's pair check, and C's readouts read A's `backlash_printed` and B's `UpdatePlan` field.
Each meets the other only through the interface's names, stubbed until it lands, as W9d's packages did. For two
implementers in place of three, A and B are one package (the model) and C the other (the view). The review then
reads the merged head, and one SolidWorks run follows.

**The open decisions.** F1 can go ahead on each assumed answer without a word from the user:

- **D3** is two constants and one equation text. Changing the number later is a one-line change and its tests. A
  printed part already built then reads *changes on Update* for Backlash, and Update carries it in place, as §1's
  old gearboxes are carried. No part is made new.
- **D6** is warnings on printed pairs only. Changing their wording or threshold later moves no machined pin.
  Drawing the true undercut would be a plan of its own, and nothing in F1 stands in its way.
- **D7** is F4's only; F1 does not read it.
- **D11** (a W9-era gearbox reads Printed) is the one answer that costs something to change after F1 lands.
  Reading such a workbook as Machined until Printed is typed would be one more rule in `_read_box`, or in the
  assessment given the record. It is cheap in code but is a second meaning of a blank cell. It should be put to the
  user before F1's B package is written; until it is answered, B builds D2 as the user gave it.

**Done when:**

- §2.7 holds.
- A printed spur, helical, herringbone, ring and bevel gear, a sleeve, a dog and a hub each derive, check and plan
  against the fake.
- A workbook built before this plan opens as changed and says why, and Update carries it against the fake.
- The boards in `design/` show the Process row and one printed warning.
- `design/UI-DESIGN.md`, the README and the backlash hints say what Printed does.
- On SolidWorks 2026, three things: one printed spur gear built; one printed pair built; and one Update of a copy
  of W9a's `setup.master` (RangeBox with the user's work), read printed. That Update gives every part's Backlash
  in place, touches none of the user's items and reads back as W9a reads its own Update.
- The same three on 2024, as the confirming build. Its first press on a freshly opened RangeBox costs SolidWorks
  2024 3.3 to 4 GB, as W9c measured, so it runs in a fresh session.
- The stage's result is reviewed by a subagent.

**Cost:** about six agent runs: F1-0, three packages, the review, and the SolidWorks run. SolidWorks time is an
estimate, not a measurement: about 20 minutes on 2026 and 30 on 2024.

**Open points for the review.** These are the rulings this revision made. The coordinating session confirms or
overturns each before code.

1. In code, a `GearSpec` or `Box` that does not say its process is machined; only the form's row and the Box
   sheet's blank are Printed; `to_dict` leaves a machined spec's two keys out (§1).
2. K9's running clearance stands for printed sleeves unchanged (§6).
3. The Workbook panel shows *Process* for every gearbox, Machined too, which re-renders the Workbook boards by one
   line. The alternative is to show it only when Printed and leave the boards as they are.
4. In a printed planetary stage the pair check replaces W7's undercut sentence; a machined stage keeps it (§2.3).
5. The link record goes to 11 whatever the process, as W9b's 8 did.
6. F2's export refuses a part the record marks unsaved or mismatched (§3.1).


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

A part with an allowance or a flat is written at **link schema 12 and sidecar schema 4**. An F1 app would otherwise
read it without either and write the record back without them, as §1 argues for Process.

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
    Excel-saved workbooks are marked machined as read where a pin needs them (§2.7).
  - Every new check is for printed gears, which is why the pair check is printed-only.
  - F1 adds no finding and changes no SolidWorks call, so `findings.py` and `tests/test_findings.py`, with
    W9c's and W9d's 2024 gates, are untouched.
- **W9 took link schemas 7, 8, 9 and 10 and sidecar schema 2** (`store.py:421-426`, `:30-35`). F1 takes link 11
  and sidecar 3, and F3 takes 12 and 4 (§1, §4.1). An older app's refusal is read and holds (§1).
- **The record's shapes grew in W9.** It now holds the user-work inventory (7), bands in a sleeve's spec (8), what a
  stopped press left (`GearboxRecord.left`, 9) and the carry (10). F1 adds nothing to any of them: `process` and
  `nozzle` ride in a part's `spec` as the bands do, and are left out when machined.
- **Gearboxes W9 built, the user's own among them**, have workbooks with no `Process`. They read Printed and
  changed once F1 lands (§1, D11).
  - *Update SolidWorks* carries the change in place, as a value of each part. W9a's rules apply as to any Update:
    K11 first; a part marked unsaved or mismatched said as W9a says it; on 2024, a What's Wrong that comes and goes
    when something of the user's is in error. No gear moves: a gear's phase is set by the centre of its tooth space
    (`workbook/geometry.py:8`, `phases` at `:430-497`), and backlash widens the space evenly about that centre.
    That is read from the code, not measured. So route (c1)'s puts and K2's refusals are not met. F1's SolidWorks run shows this on a copy of W9a's `setup.master`
    (§2.8).
  - *Build again…* would make every gear new. W9d would then carry the user's components onto the new parts, but
    not the user's features in the old ones, nor mates on their faces. So F1 adds a third `made_new` reason in
    `gearbox.py` beside `UNSAVED` and `MISMATCHED`: a part that would be reused but for its Process. With it,
    `ui_text._reuse_advice` (`ui_text.py:5440-5463`) gives the way back, as it does for those two: *Gear_m1.25_N29
    is new only because the Box sheet's Process is Printed where it was built machined: answer No, type Machined in
    Box!B9 (or press Update SolidWorks, which carries it in place), and Build again… reuses it with your Keyway.*
  - The footer says the same before either press (§1).
- **K11** (Update refuses a value the app owns that the user changed in SolidWorks):
  - F1's backlash equation is one of those values from the start. No new code reads it, since `_value_edits`
    (`swbuild.py:5423-5457`) compares every planned global.
  - F1 changes K11's words only. `_blank_meaning` (`:5460-5471`) today turns a non-numeric expression into a
    sentence by removing quotes and `*`, which would say *IIF ( Module <= 1 , 0.3 × Module , 0.3 )*. For the printed
    default it says *0.3 mm, the printed default (0.3 × Module below module 1)*. `_back_words` (`:5484-5489`)
    still gives the exact equation to set back, since SolidWorks must hold that text for K11 to read it as the
    app's again.
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
  - The floor of 0.5 mm already exceeds the 0.3 mm this plan takes for two printed surfaces, and from module 1 up the
    gap still grows with the tooth, as a dog's chamfer would.
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
  footer has a ceiling above which its sentence scrolls (`design/UI-DESIGN.md:406-420`). So the Process sentence in
  the footer and F2's Export button fit whatever else the footer says. The Box's Process shows as one line in the
  Workbook panel (open point 3, §2.8).
- **Files both touch**, now with their lines (§2.8's table): the form (`gui.py`) and `ui_text.py`, `store.py`,
  `workbook/update.py`, `workbook/gearbox.py`, `workbook/checks.py`, `workbook/schema.py`, `workbook/model.py`,
  and K11's words in `swbuild.py`. They were read at `c2d95cc`. If W9's 2024 runs change any of them before
  `printed` is cut, the coordinator has the affected parts of §1, §2.8 and this section read again.


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
  (`Gear.spec_values`, which a test holds to every field) and Solve, which keeps the form's fields. §2.8's tests hold
  each. The review should look for any other `GearSpec(` in `src` that serves the user; at `c2d95cc` the only bare
  one is the form's defaults (`gui.py:154`).
- **The user's built gearboxes all read as changed (D11).** The first Update after F1 writes to every part of their
  RangeBox. It is a value write W9a's rules govern, but it is still a write to each of their files, and on 2024 the
  first press on RangeBox is memory-heavy (W9c). If the user would rather keep a W9-era gearbox machined until they
  say so, D11's other answer is cheap only before F1's package B is written.
- **K11's set-back for the printed default is an equation.** A user who typed a number in SolidWorks is told to
  type the IIF back, or the number in the cell. That is the same burden as today's `0.3 * "Module"`, but a longer
  text.
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
