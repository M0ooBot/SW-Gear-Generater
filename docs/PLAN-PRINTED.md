# Gear Generator — gears made to be 3D printed in PLA

**Draft of 2026-11-16, revised the same day to its first review (`docs/PLAN-PRINTED-REVIEW.md`) and
then to the user's answers. Nothing of it is built, and nothing is to be built yet** (the user,
2026-11-16: *"w9 first, dont actually build anything yet"*). **It waits behind W9.** D3, D6 and D7 still
stand as assumed, and the revision has not been reviewed: when the plan is taken up, after W9 closes, it
is first read against the code as W9 left it and reviewed again. Executed like `docs/PLAN.md`: its "For the executing agent" section, and
the rules in `docs/HANDOFF-WORKBOOK.md` (*Rules carried over*), apply here.

Its stages are **F1 to F4** (F for filament). W9's probes are already called P0, P1 and P2.


## Context

The gears the app builds are correct textbook gears, drawn for SolidWorks. The user now wants to print
them: FDM, ordinary PLA. Read against that use, on 2026-11-16, the code shows:

- **The geometry is right** (true involute, 0.38 × module root fillet, profile shift, undercut and
  thin-tip warnings), and nothing in it knows about a nozzle, a printer's error or plastic.
- **Backlash is `0.3 × "Module"` per gear.** A printer's error is a fixed size, not a share of the
  module: at module 3 the pair has 1.8 mm of play.
- **The thin-tip warning is at 0.3 × module**, so a module 1 tooth whose tip is 0.37 mm, narrower than one
  line from a 0.4 mm nozzle, passes without a word.
- **Undercut is warned about and not drawn.** A hob would remove that material; a printer prints the
  flank as drawn. Unshifted at 20°, a 13-tooth pinion clears an outside mate of up to 16 teeth, 14 up to
  26, 15 up to 45, 16 up to 101; 12 and fewer clear nothing.
- **No feature a printed gear wants:** the bore is a plain hole at its nominal size, no drive flat, no
  file a slicer reads.
- **No strength check.** The workbook works out each shaft's torque and compares it with nothing.

What was read online the same day (maker and vendor guides and one series of bench tests; peer-reviewed
data on printed gears is thin, and the guides differ on backlash by about four times) is under *Sources*.
The reviewer did not fetch them. What they agree on: module 1.5 to 2 for a 0.4 mm nozzle and 1 for light
duty; 20° pressure angle, 25° for a stronger root; a root fillet of 0.3 to 0.5 × module; herringbone
where possible; a flank clearance built into the tooth, 0.1 to 0.2 mm per flank in the most careful of
them; a 0.5 mm chamfer or the slicer's compensation for the first layer; a D-flat, key or insert rather
than a press fit, since PLA creeps; five walls or more.

### The rule this plan keeps

**A gear marked `Machined` builds exactly what every gear builds today, and is told exactly what it is
told today**: the same globals, steps, file name, warnings and Solve rows. Every new check, default and
feature below is for printed gears only. §2.7 says how that is proved.

**Printed is the default everywhere** (the user, 2026-11-16: *"workbook also go 3d printed, just make
everything go 3d printed default"*). What that carries with it is in §1.


## Decisions wanted

Each has the answer this plan assumes; say where it is wrong.

| | Question | Assumed |
|---|---|---|
| D1 | How is a gear marked? | **Answered 2026-11-16.** A **Process** row on the form, `Printed` or `Machined` (one row for a pair), and a `Process` setting on the workbook's Box sheet for the whole gearbox. |
| D2 | What is the default? | **Answered 2026-11-16: `Printed`, everywhere, the workbook too.** A blank Process is Printed. Only the record of a part already built reads as `Machined` when it has no Process (§1). |
| D3 | Printed backlash when the cell is blank | **The smaller of 0.3 mm and 0.3 × module**, per gear: 0.3 mm from module 1 up (0.14 mm off each flank, measured square to it), and today's value below module 1. Never more than today's, so nothing that builds today is refused. To be replaced by the user's own measurement (§3.2). |
| D4 | Which shaft drive first? | **Answered 2026-11-16: D-flat.** Hex and a keyway are the same kind of sketch and can follow; a boss with a setscrew or a heat-set insert is not in this plan. |
| D5 | The file for the slicer, and which slicer | **Answered 2026-11-16: the user's slicer is Bambu Studio, so STEP.** Bambu Studio is said to open STEP; F2's own step, the user opening an exported gear there, is what shows it. No STL export. |
| D6 | Undercut | **Warn, and check each printed pair for it** (§2.3); drawing the true undercut root is another sketch topology and not in this plan. |
| D7 | PLA's allowable tooth stress | **Provisional: 17 MPa**, a third of the roughly 50 MPa a PLA datasheet gives, against a stress that includes the fillet's concentration (§5). No standard gives a figure for printed PLA, so this is the writer's judgement, typed on the Box sheet and replaced by the user's own tests. |
| D8 | Where this sits beside W9 | **Answered 2026-11-16: W9 first.** This plan starts after W9 closes, on a branch `printed` cut from `workbook` as W9 leaves it. What it then takes on from W9 is in §6. |
| D9 | The edge chamfer against first-layer squish | **Answered 2026-11-16: left to the slicer for now.** Not built in F1 to F4; the export's print list asks for the slicer's first-layer compensation. The review found the chamfer is the costliest piece here (§4.3). It gets a plan of its own only if the test prints show the slicer's setting is not enough. |
| D10 | A printed part's file name | **Answered 2026-11-16: ends `_P`** (`Gear_m1.5_N25_P`), as a shifted gear ends `_x0.09`: it is a different part from the machined gear of the same sizes, and without the mark the second of the two is refused as existing. Machined names stay as they are. |


## 1. What `Printed` means

Two new fields on `GearSpec`:

- `process`: `printed` or `machined`. **Blank is `printed`.** Written into every new record as one of
  the two words, never blank.
- `nozzle`: the line width in mm, `0.4` when blank. Checks only; it changes no plan, so the as-built
  comparison ignores it (`update._ignored_fields_as_built`).

In the workbook both are Box settings (`Gear.spec_values` fills them into each gear; `model.to_sheets`
writes them). In pair mode the one Process row goes to both gears (`pair.apply`).

**A key missing from a record means the part was built before that key existed.** One function, the
record reader, fills a missing `process` with `machined` (and, from F3, a missing `bore_allowance` with
`0` and a missing `drive` with `round`). `GearSpec.from_dict` alone cannot do this: it fills a missing
key with the form's default, which is now Printed. Every place that compares a record's raw values
reads through that function or takes the same default, as `teeth_side` already does:
`swbuild.structural_change`, `update._structural` and `_ignored_fields_as_built`, `gui._load_record`
and `_update_target`, `gearbox.same_part`. A test holds each to it.

What the default carries with it:

- **An old `.gear.json` opens as Machined**, since that is what was built. Changing its row to Printed
  is a change of one global's text, which Update values carries.
- **A workbook without a `Process` setting is now Printed.** One whose gearbox is already built reads
  as *changed since it was built*: `"Backlash"` in each part goes from `0.3 * "Module"` to §2.1's
  equation. Update SolidWorks carries that; typing `Machined` on the Box sheet keeps the gearbox as
  built. The footer says so whenever the only changes are these (no stored "first time").
- **New workbook…** writes `Process` `Printed` and `Nozzle` `0.4`.
- **No `Process` custom property.** Update writes globals and never properties, so a property would go
  stale the first time Update changed a part's process. The record and the file name carry it.
- **Sleeves and dogs** pass `process` through to the spur and ring kinds they are built from, and take
  the printed backlash as those do.
- **The record schemas go up by one at F1**, from wherever W9 leaves them (the link record and the
  `.gear.json`; `store.py`). An app
  from before F1 would otherwise read a printed workbook as machined, and its Update would write every
  backlash back. What an older app does with a newer schema is read from `store.py` before F1's first
  line; if it does not refuse, that is a STOP.


## 2. Stage F1 — defaults and checks (no new SolidWorks call)

### 2.1 Backlash

Blank backlash on a printed gear is `IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )`, the shape of the
depth IIF the app already writes, so no kind of equation is new. It is written by all five variable
writers (`spur.py`, `helical.py`, `internal.py` twice, `bevel.py`) and the four `derive`s. The card
shows it as a default (*0.3 mm · printed default*), a third state beside typed and `0.3 × module`.

On the involute this is an exact allowance for walls printed evenly fat: turning an involute about its
centre moves it square to itself by the same distance everywhere, `(j / 2) cos α`. **It is not one
anywhere else.** The tip and root circles do not move, and the radial line and fillet under the base
circle are turned, not offset; §2.2's clearance check is what watches those. On a bevel gear the
allowance shrinks toward the small end with the tooth (0.70 of it at the toe of a 20 / 40 pair at module
1.5 and face 10), so **a bevel gear's toe governs**: the card gives the toe's figure, and §2.2's tip
check is made there.

A slicer's own horizontal compensation adds to this; the card and the print list say to use one or the
other.

### 2.2 Checks for printed gears (warnings)

- **Tip:** tip thickness after backlash under one nozzle width; at the toe on a bevel gear. With the
  default it warns at module 1 (0.27 to 0.45 mm from 12 to 40 teeth), passes at module 1.25 from 12
  teeth, and at module 1.5 from 8 (0.58 mm at 12, 0.71 at 20; a 6- or 7-tooth pinion warns).
- **Module:** under 2.5 × nozzle (1.0 at 0.4 mm): the guides' floor, below which a profile rounds off.
- **Radial clearance, per pair:** `pair.tip_clearance` at the working centre distance (Gleason's for a
  bevel pair) under 0.3 mm less a rounding tolerance. Two printed surfaces take about that. Unshifted
  spur and helical pairs pass from module 0.75; **bevel pairs warn under module 1.6** (Gleason's
  clearance is 0.188 × module), and shifted pairs wherever the shifts have eaten it. The depth is left
  alone; the sentence says to use a larger module or less shift.
- **Rim:** the wall between the bore and the root under three nozzle widths. A printability floor only;
  today's one-module warning is the stricter above module 1.2 and stays.
- **Helix:** a helix angle over 45°, a flank that prints as an overhang (conservative by a few degrees:
  the flank's own angle is the base helix angle).
- **Ring fillet:** a ring's 0.15 × module default fillet is under the 0.3 the guides ask; one sentence
  says so and why it is small (the pinion's tips). No change to the default.

### 2.3 Undercut and interference (warnings, printed pairs only)

The single gear's undercut warning gains a printed sentence: *a printed gear keeps this material, so the
mate's tips may run into it*, ahead of the shift it already names. For a printed pair, on the form and
per Meshes row, with shifts and the working centre distance, in transverse values for helical kinds
(`rb` from `αt`, addendum `mn (1 + x)`):

- **outside pair:** each gear's tip must not reach past the other's base-circle tangent point,
  `ra₂ ≤ √(rb₂² + (C sin αw)²)` and the same with the gears exchanged;
- **ring and pinion:** the ring's tip must not reach inside the pinion's tangent point,
  **`ra₂ ≥ √(rb₂² + (C sin αw)²)`** (the first draft had this the wrong way round; it cleared three of
  the repo's own rings that fail and warned on one that passes);
- **bevel pair:** the outside condition on the Tredgold pair at the back cone, with Gleason's addenda;
- **crossed helical pair:** no pair check; each gear's own undercut limit stands, and the sentence says
  that is all that was checked.

In a planetary stage it takes the place of the sentence that already says this
(`workbook/checks.py`, "is below the undercut limit … and meshes …"), so nothing is said twice. It is a
warning, not an error: the app cannot say the drawn root meets the tip, only that the pair is at risk.

### 2.4 The undrawn part of the flank

Today's warning that the involute starts above the form diameter (from 26 teeth at module 1.5 with the
default fillet) stays as it is. Curing it means a smaller default fillet on large gears, which costs
root strength; left for the user to rule on after the first prints.

### 2.5 Solve and the workbook's fixes

For a printed pair, Solve's shifted rows and the workbook's profile-shift fix (`pair._shifted`,
`pair.shift_for_centre`, `workbook/fixes.py`) test what a printed gear needs: the tip **after** backlash
against the nozzle, and clearance against the larger of 0.1 × module and 0.3 mm. Rows whose module is
under §2.2's floor or whose tips are under a nozzle are ranked after the clean ones and marked (*thin
for a 0.4 nozzle*). A row whose tip comes to a point is not offered. Machined pairs keep today's tests.

### 2.6 A measurement to calibrate by

The Derived panel of a printed spur or helical gear gives its **span over k teeth** (the base tangent
length, what calipers across k teeth read), for the gear as drawn, backlash included. A printed gear
measures more than that by twice what the printer adds to a flank. This is what §3.2 uses; it needs no
rig.

### 2.7 Proving the rule

Before F1's first line, at the commit it starts from (W9's last), pin (as `BEFORE_W8` does, by hash of
plans, diagnostics and motion): strip plans of every kind and recipe in both trig variants, the hub
among them; the three pair assembly plans; Solve's rows for a set of pairs; the nine workbooks of
`BEFORE_W8`, the W8 fixtures, RangeBox and whatever fixtures W9 adds; and **what Update and the strip say for a record with no `process` key against a form or
workbook marked Machined, which must be nothing**. After F1 each is taken again marked machined and
must be identical.

The suite builds 194 `GearSpec`s by hand in 24 files, and the probe scripts more; each that pins sizes,
a plan or a warning is marked machined. The three workbooks Excel itself saved
(`tests/fixtures/`) are not touched: the tests put `Machined` into the Box as read.

**Done when:** §2.7 holds; a printed spur, helical, herringbone, ring and bevel gear, a sleeve and a
dog each derive, check and plan against the fake; a workbook built before this plan opens as changed,
says why, and Update carries it against the fake; the boards in `design/` show the Process row and one
printed warning; `design/UI-DESIGN.md`, the README and the backlash hints say what Printed does; one
printed spur gear and one printed pair are built on SolidWorks 2026, and again on 2024; the stage's
result is reviewed by a subagent. **Cost:** no SolidWorks run longer than minutes; three to four agent
runs (pin and fields; checks; window and boards; review).


## 3. Stage F2 — the file for the slicer, and the first prints

### 3.1 Export

**Export STEP** on the form (the active built gear) and in the Workbook window (every distinct part of
the built gearbox, into `print/` beside it, with a text list: part, how many to print, and the settings
of *Sources*: flat on the bed, five walls, 35 % infill or more, 0.2 mm layers, first-layer compensation
0.15 to 0.2 mm, the seam off the tooth roots, grease). The app keeps its rule: it never writes over a
file, and an export that exists is named `_r2`.

`IModelDocExtension.SaveAs3` to a `.step` name is a call the app has not made, one that writes a file
and may raise a dialog, so by the rule it is **probed first**: on a scratch part, that it returns
without a dialog and leaves the part's own path and modified mark as they were (a save under a new
name renames a document; an export must not). The file is checked without SolidWorks, by counting the
solids in its text: opening a STEP in SolidWorks can raise import dialogs of its own. One short run on
2026, the same on 2024.

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

A printed bore is cut at `"Bore Diameter" + "Bore Allowance"`, so `"Bore Diameter"` stays the shaft's
size. Blank is the figure §3.2 found (0.2 mm on the diameter until then). The global and the changed
link exist only when the allowance is not zero, as `"Profile Shift"` does, so going between none and
some is structural (`swbuild.structural_change`) and a change of size is a value. A form row and a
Gears column, `Bore allowance`. A bevel gear's bore (its own code in `bevel.py`) takes it the same way.

**A printed part built before F3 has no allowance, and its record has no key for it, so it reads as
allowance 0** (§1's rule) and stays a true record of what it is. Giving it one means a new part:
Build again… in a workbook, a new name on the strip. That includes §3.2's test prints.

### 4.2 D-flat

`Drive`: `round` or `flat`, and `Flat`, the shaft's size across its flat. The bore sketch becomes an arc
and a chord from ops the app already has (`Arc`, `Line`, `Relation`, `Dimension`); the flat takes half
the allowance. Changing Drive is structural. Columns `Drive` and `Flat`. The rim check is unchanged:
the thinnest wall is at the round part, never at the flat.

### 4.3 The edge chamfer is not here (D9)

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
need the virtual gear at the mean cone and are said to be unrated. To be checked against ISO 6336-3
itself before a line is written (the reviewer and the writer both have these from memory): the
critical section is where a 30° tangent meets the root fillet on an outside gear and a 60° tangent on
a ring; the whole load at the tip of one tooth; **with** the stress-correction factor for the fillet,
which the app has the radius and section to work out and which is roughly 1.5 to 2. Taken from the
app's own outline, so backlash and shift are in it.

- **The form:** the tangential force and torque one tooth takes at the allowable, named for what it
  is: *holds about … N·m once, not running*.
- **The workbook:** each Meshes row's **tangential force** (`2 T / d`, the same on both gears) against
  the weaker gear's, per mode: divided among a stage's planets with an allowance for uneven sharing;
  an idler, whose teeth bend both ways, held to 0.7 of the figure. A warning at the row, the share used
  on the Results sheet. Box setting `Allowable stress`.

Every sentence says what it does not cover. It is a static figure for a tooth printed flat, bending
within its layers. A helical tooth's side load and any load across layers meet the weaker bond between
them, and are not derated. A gear that runs for long fails first by heat (PLA softens near 55 to
60 °C), by wear, or by creep at its bore; none is worked out.

**Done when:** hand-worked cases are pinned in the suite, among them a gear thinned by backlash
carrying less than the same gear without, and a ring; reviewed. **Cost:** two agent runs and the
review; no SolidWorks.


## 6. After W9 (D8)

W9 goes first and is planned as if this plan were not there: its answer keys, its schema numbers (7, 8
and 9, and sidecar 2) and S0's master are untouched. This plan is read against the code W9 leaves, and
takes on from it:

- **W9's pinned results must not move.** Every new check here is for printed gears, and W9's fixtures
  are marked machined (§2.7). That is why the pair check is printed-only.
- **Gearboxes W9 built**, the user's own among them, have workbooks with no `Process`, and read as
  changed once this lands (§1). That is the default the user chose; the footer's sentence is what
  tells them, and `Machined` on the Box sheet is what keeps one as built.
- **K11** (Update refuses a value the app owns that the user changed in SolidWorks): F3's
  `"Bore Allowance"` and the flat's dimension join the values it reads, and F1's backlash equation is
  one of them from the start.
- **The hub (W9b)** is built "with the row's Bore", its fixing to the shaft left to the user. F3's
  allowance and flat are that fixing: a hub row takes `Bore allowance`, `Drive` and `Flat` as any gear.
- **K9's running clearance**, `max(0.5, 0.5 m)`, is argued from a backlash that scales with the tooth.
  Printed, it no longer does above module 1; F1 says whether it stands for printed sleeves.
- **Carrying the user's work** (W9c, Build again… remaking their mates): a part that F3 makes new
  because its allowance or drive changed is carried like any other part made new.
- **Files both touch:** the form and `ui_text.py` (W9a's K12), `store.py`, `workbook/update.py`,
  `workbook/checks.py`, `workbook/schema.py`. Every file and line this plan and its review cite is as
  of `d953db5`, before W9; each is found again before it is relied on.


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


## 8. Risks

- **The numbers are borrowed.** 0.3 mm, 0.2 mm and 17 MPa come from guides that disagree and from no
  measurement of the user's printer. §3.2 replaces the first two; until then every card that shows one
  says it is a starting value. Nothing in this plan replaces the third.
- **Two allowances stacking:** the app's and the slicer's. Said on the card and in the print list.
- **The missing-key rule** (§1) is what everything already built rests on; a comparison that misses it
  makes every old part read as printed. §2.7 pins the case.
- **The plan ages while W9 runs.** It was written and reviewed against the code before W9; the second
  review, when it is taken up, is against the code after.


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


## Sources

- Sovol, *3D Printing Gears That Actually Work* — <https://www.sovol3d.com/blogs/news/3d-printing-gears-that-actually-work-backlash-orientation-and-material-tips>
- How To Mechatronics, *How To 3D Print Gears* (bench tests) — <https://howtomechatronics.com/how-it-works/how-to-3d-print-gears-the-ultimate-guide/>
- Hackaday's summary of the same — <https://hackaday.com/2024/06/12/studying-the-finer-points-of-3d-printed-gears>
- Instructables, *A Practical Guide to FDM 3D Printing Gears* — <https://www.instructables.com/A-Practical-Guide-to-FDM-3D-Printing-Gears>
- RepRap wiki, *Gear Design* — <https://reprap.org/wiki/Gear_Design>
- University of Warwick, printed nylon gears against moulded — <https://core.ac.uk/download/228159444.pdf>
- On VDI 2736's limits — <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10537784/>
