# Gear Generator

Builds parametric spur gears in SolidWorks from a form, and solves gear pairs:
given a centre distance and a ratio, it finds module and tooth counts that work,
builds both gears and mates them in an assembly. A whole gearbox written in an
Excel workbook can be imported, checked and built: its parts, a layout part and
an assembly whose gears are mated to their shafts and to each other, so that
dragging the input in SolidWorks turns the whole train (shown on SolidWorks
2026 and 2024 for gearboxes on parallel shafts; for shafts at an angle, still
to be shown).

The gear it builds is parametric in SolidWorks itself. Its sizes live in the
Equation Manager as global variables, starting with the ten a person would type
(`"No. of Teeth"`, `"Module"`, `"Bore Diameter"`, `"Pressure Angle"`, …), and
every dimension in the part is driven by them. Change `"No. of Teeth"` to 40 in
SolidWorks and the part rebuilds as a 40-tooth gear; nothing refers back to this
app.

No runtime dependencies beyond Python 3.9+ with tkinter. Building into
SolidWorks needs Windows, SolidWorks 2024 or newer, and `pywin32`.

## Running

```
python main.py
```

or, installed, `gear-generator`. On a machine without SolidWorks or `pywin32`
the window still works out, checks and draws gears and solves pairs; only
**Build** needs SolidWorks.

## Using it

1. Choose **Single gear** or **Gear pair**, and the flank: **Involute** (a true
   involute, as an equation-driven curve — the default) or **Arcs** (circular
   arcs approximating it). **Process** says how the gear will be made:
   **Printed** (the default, with the printer's **Nozzle** under it, blank
   0.4 mm) or **Machined**; see *Printed gears* below.
2. Type the gear: module, number of teeth, pressure angle, face width, and bore
   (blank for none). Backlash defaults to 0.3 × module on a machined gear and to
   0.3 mm (0.3 × module below module 1) on a printed one, and fillet radius to
   0.38 × module; type a value to override either.
3. A card at the foot of the panel says what the field you are typing in means
   and what your value comes to: *Module · m … here m 1.5 × z 20 = PD 30 mm ·
   tooth depth 3.375*. It follows the caret.
4. The **Derived** panel draws the gear — in **Gear pair** mode both gears
   meshed, at one scale, with the centre distance dimensioned under them — and
   lists every size it comes to, with anything worth knowing: an undercut tooth
   count, a thin tip or rim. Errors, such as a bore bigger than the root circle,
   disable **Build** and say which field to change.
5. Choose an output **Folder**. The part is saved there as `Gear_m1.5_N25.SLDPRT`
   (or the name you type), with a `Gear_m1.5_N25.gear.json` record beside it.
6. With SolidWorks open, **Build**. The status line says what was built, or
   exactly where the build stopped and what SolidWorks said. A build never
   overwrites a file: an existing name is refused before anything is made.

Material is left unset, and the status line counts it as a step to do by hand.

### Changing a built gear

**Open .gear.json** puts a built gear back on the form. With its part the active
document in SolidWorks, change a value and press **Update values**: only the
globals that differ are set, in one batch, and the part rebuilds once. A change
the equations cannot carry — the other flank recipe, adding or removing a bore,
or shifting an unshifted gear — is refused with a sentence saying to build a new
part instead.

Editing the globals in SolidWorks' own Equation Manager works just as well.

### Printed gears

A gear made to be 3D printed (FDM, PLA) is the same involute gear, built the
same way, with three differences.

- **Backlash.** A blank Backlash is the smaller of 0.3 mm and 0.3 × module per
  gear, written into SolidWorks as `IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )`:
  room for walls printed a little fat. It is a starting value until your own
  prints are measured, and it does the job a slicer's X-Y compensation does, so
  use one or the other. The card and the Derived panel say *printed default*
  beside it.
- **Checks for printing.** The Derived panel also warns of a tooth tip thinner
  than one nozzle line after backlash (at the toe on a bevel gear), a module
  under 2.5 nozzle widths, a rim under three, a helix over 45°, a tip clearance
  under 0.3 mm in a pair, and a ring's small default fillet. A printed gear
  under its undercut limit is made as drawn, so the warning says to turn the
  pair in SolidWorks. Solve marks the rows that are thin for the nozzle.
- **The name.** A printed part's file name ends `_P` (`Gear_m1.5_N25_P`), and
  so does a printed pair's assembly, so it never clashes with the machined gear
  of the same sizes.

A machined gear is built, checked and recorded exactly as before. A
`.gear.json` written before printed gears existed opens as **Machined**, which is
what was built.

## The gear in SolidWorks

One tooth space is cut from a blank the size of the outer diameter and
patterned round the gear axis:

| Feature | What it holds |
|---|---|
| `Gear Axis` | the axis the teeth are patterned about |
| `Blank Sketch`, `Blank` | the outer diameter (`OD`) and face width (`Width`) |
| `Tooth Space Sketch`, `Tooth Space` | one space: root arc, fillets, flanks, and a chord beyond the tip (an arc on a pinion too small for a chord) |
| `Teeth` | the circular pattern, its count (`Count`) linked to `"No. of Teeth"` |
| `Bore Sketch`, `Bore` | the bore, when there is one |

Every sketch is fully defined. The build measures whether the part's Equation
Manager works in degrees or radians before writing a single global, and after
the rebuild reads every global's value back and compares it with the maths.

**Custom properties** — `Description` (*Spur gear, involute flank*), `Gear Kind`,
`Flank` and `Generated By` — are written on every part, so a bill of materials
can list the gear. The sizes are not: the `custom_properties` probe found that
a property naming a global (`"No. of Teeth"`) stays that text rather than
following the global, and a size written as plain text would be wrong the first
time the global was edited. The probe passed on SolidWorks 2024 and 2026.

## Helical and herringbone gears

Choose **Helical** or **Double** (herringbone) as the Kind, and two rows appear on
each gear: **Helix angle** and **Hand**. Module and pressure angle are then the
*normal* ones — what a hob is sold by — and the tool works out the transverse
module `m / cos β`, the transverse pressure angle, the pitch diameter they make,
the lead, how far a tooth turns across the face, and the overlap ratio εβ, which
it warns about below one.

In SolidWorks the part carries the same ten globals as a spur gear, with
`"Helix Angle"`, `"Transverse Module"` and `"Transverse Pressure Angle"` ahead of
the ones that now depend on them, and `"Lead"`, `"Overrun"`, `"Path Length"` and
`"Twist Angle"` after. The tooth space is the spur sketch drawn in the transverse
plane on a **Profile Plane** one module in front of the part, swept as a cut
along a **Path Sketch** on the axis to one module past the far face, turning at a
constant rate, then patterned. A herringbone is half a gear so built from a **Mid
Plane**, patterned, and its body **Mirror**ed about that plane, so its apex is
exactly the section drawn. Change `"Helix Angle"` or `"Face Width"` in SolidWorks
and the teeth re-twist; the hand is structural, and changing it means building a
new part.

A herringbone can have a **Groove**: a plain channel round the middle, between
the two helices, for a hob or grinding wheel to run out into. Its floor is two
modules inside the root circle (`"Groove Diameter"`). The toothed **Blank** stops
`"Groove Width"` / 2 short of the Mid Plane (`"Toothed Width"`), a **Hub** runs on
under the root to it, and the sweep and mirror are unchanged. Adding or removing
a groove is structural. Built only from features the probes verified, **but not
yet built on SolidWorks as a whole**.

In **Gear pair** mode the two gears must share module, helix angle and kind, and
have opposite hands: gear B's **Hand** follows gear A's (*follows gear A*),
the other one on parallel shafts, the same one round a ring, and on crossed
shafts whichever **Hands** says. Leave the Pair panel's **Helix angle** blank and **Solve**
finds, for every standard module, each tooth sum whose helix angle falls within
**Helix range**, so every exact-ratio row meets the centre distance exactly
(*β18.19° · exact*). Choosing a row writes the helix angle into both gears and
makes gear B the other hand. The assembly is mated at the transverse centre
distance, with a herringbone pair's mid-planes coincident so the apexes line up.

## Solving a pair

In **Gear pair** mode the **Pair** panel sits above the two gears, since solving
is what fills them in. Type the **Centre distance** and the **Ratio**, driven
over driver: `3` (or `3:1`) makes the second gear three times the first, and
`1:3` makes it a third. Choose a module series and **Solve**. The candidates
open beside the form — **Candidates**, in the Pair panel's own header, shows and
hides them — best first: hitting the centre distance exactly, a standard module,
no undercut, no profile shift, the smallest ratio error, then the larger module.
Click one to put its module, tooth counts and profile shifts on both gears;
nothing else on the form changes, and the Solve line then reads
`69 candidates · 3 exact · 2 with shift · m1.5 20 : 60 chosen`.

**Build** then makes both parts and an assembly, `Pair_m1.5_20T_60T.SLDASM`. The
second gear is mated at the centre distance its teeth make, turned so a tooth
meets the first gear's space, and the distance is driven by the assembly global
`"Centre Distance"`. Once the assembly is built the tool runs SolidWorks'
interference detection on it: no interference is reported as done, and any is
a check with the count and volume, telling you where to look.

**Assembly** `Gear mate` builds the pair to turn instead of fixed: gear 1 is
held only on its axis, gear 2 is placed with a tooth in gear 1's space, and a
SolidWorks gear mate at the tooth ratio turns gear 2 when gear 1 is dragged —
the other way for an external pair, the same way round a ring. It is for gears
on parallel shafts. The `gear_mate` probe settled the mate's enum value, which
gear the ratio's numerator goes with, and the flip, on two cylinders on
SolidWorks 2024 and 2026: driven 30°, the second turned 15° the opposite way
with Flip off. Pairs built through the app's own assembly plan were then
driven the same way on both versions (`probe/gear_pairs_check.py`, logs in
`probe/results/` and `probe/results/sw2024/`): a 20 / 40 pair turned 1 : 2 the
opposite way, and a 20-tooth pinion in a 60-tooth ring 3 : 1 the same way, with
no interference after the turn. The ring takes the same Flip as an external
pair: with the opposite one, which the app used to give it, the pinion turned
against the ring and the teeth clashed.

## Profile shift

**Profile shift** (x, in modules) moves the rack that cuts the gear outward:
the tip and root circles grow by 2 x m and the tooth thickens at the pitch
circle by 2 x m tan α, while the pitch and base circles stay put. A positive
shift cures undercut on a small pinion — an undercut warning names the least
shift that would clear it, (17 − z) / 17 at 20° — and a pair's two shifts move
its centre distance to a ≈ a₀ cos α / cos αw, which is how a standard module is
made to fit a centre distance it does not divide. A helical gear's shift is the
normal one. Rings, bevel gears (whose Gleason addendum is already a shift) and
crossed pairs are built unshifted, and the row is hidden for them.

A shifted part adds a `"Profile Shift"` global after `"Pressure Angle"` and
carries it in `"Outer Diameter"` and `"Arc Length"`; an unshifted part's
equations are exactly what they were. Its file is named for the shift,
`Gear_m2_N15_x0.12`.

**Solve** offers shifted rows for spur and helical pairs on parallel shafts at a
standard module: a row that misses the centre distance again with the total
shift that meets it exactly, split evenly unless that leaves a gear undercut,
and an exact row whose pinion undercuts again with equal and opposite shifts,
which leave the centre distance where it was (*x +0.12/−0.12 · exact*). A row is
not offered if either tip, before backlash, would be under 0.3 module thick, or
the tips would come within a tenth of a module of the other gear's root; the
form still warns if the backlash — 0.3 × module unless typed — thins a tip past
that. The Derived panel shows the
working pressure angle, and the assembly is mated at the working centre
distance.

## Internal gears

On a spur, helical or double gear, **Teeth side** `Internal` makes a ring: the
teeth point inward from a solid rim. **Rim** takes the place of Bore (blank
leaves three modules outside the root circle), the default fillet is 0.15 ×
module so it stays clear of a pinion's tips, and the part's globals carry
`"Inner Diameter"` and `"Rim Diameter"` in place of the outer and bore
diameters. A ring is cut the way its external kind is — straight through, or
swept and mirrored — from an annular blank.

In **Gear pair** mode choose **Mesh** `Internal`: gear B becomes the ring round
gear A, turning the same way, at C = m (z₂ − z₁) / 2. The ratio must be more
than one. Solve ranks a row whose pinion would clash with the ring's tips as it
turns after the clean ones and marks it *clash 0.14 mm*. A helical ring meshes
with a pinion of the **same** hand. The assembly fixes the ring at the origin
and mates the pinion inside it, half a pinion tooth round.

## Crossed-axis helical pairs

For a helical pair choose **Shafts** `Crossed` and a **Shaft angle**. **Hands**
`Same` makes the helix angles add up to the shaft angle; `Opposite` makes them
differ by it, which reaches a small shaft angle with two steep helices (β₁ 45° R
and β₂ 15° L cross at 30°). Either way C = (mₙ / 2)(z₁ / cos β₁ + z₂ / cos β₂).
Of opposite hands Solve tries both ways round, β₂ = β₁ − Σ and β₁ + Σ, and
prefers the pair whose steeper helix is gentler; the assembly is named `_XO30`
rather than `_X30`. Opposite-hand placement is checked here — the tooth lines lie
along each other at the contact point — **but has not been built on SolidWorks**. Leave Helix angle blank and Solve
finds, for each module and tooth pair, the β₁ that meets the centre distance
exactly nearest half the shaft angle (*β45°/45° · exact*); type it and the rows
are ranked by how near they come. The parts are ordinary helical gears. The
assembly places gear 2 across gear 1 at the contact point, then mates it there
— its axis at `"Centre Distance"` from gear 1's right plane, at `"Shaft Angle"`
to gear 1's axis, and turned by `"Mesh Angle"` — and checks interference.

## Bevel gears

**Bevel** makes a straight bevel gear on the Gleason system: **Mate teeth** is
the tooth count of the gear it meshes with and **Shaft angle** the angle between
the two shafts (90° for a right-angle drive). From them come the pitch cone δ,
the cone distance R, the unequal addendum and dedendum, face and root angles,
the outside diameter and the crown's distance from the apex, and the Tredgold
virtual tooth count the section is drawn for. The form warns when the face is
wider than a third of the cone distance or ten modules.

Past a 90° shaft angle the bigger gear's cone opens out, and the tooth counts
and the shaft angle decide what it is:

- **Crown gear**, δ = 90° (within 0.01°): at cos Σ = −z₂ / z₁, so 40 teeth with
  a mate of 20 at 120°. Its pitch cone is a plane and its teeth stand on its
  face; its back cone is a cylinder, so its section is a **rack's** — straight
  flanks at the pressure angle, a root fillet each side — the same for either
  flank recipe. It is a disc, three modules behind its root at the heel. Gleason's
  addendum ratio is infinite beside it, so it takes 0.54 m and its pinion 1.46 m.
- **Internal bevel gear**, δ of 91° or more: its teeth are inside a cone, and
  its section is a **ring's**, drawn for the back cone's N / |cos δ| teeth. It is
  a conical ring three modules behind its root, with no bore (a typed Bore is
  warned about and not cut). Gleason tabulates nothing for internal bevels, so
  both gears of the pair take an addendum of one module.
- Between 89° and 91°, but not within 0.01° of 90°, a gear is too near a crown
  gear to build either way; the form refuses it and names the shaft angle that
  makes it one.

Which way SolidWorks turns a heel plane's sketch once the cone reaches 90° was
measured by probe `bevel_planes_beyond_90` on cones of 90° and 120°, on
SolidWorks 2024 and 2026: as below 90°, its x points the way the tips do. A
crown bevel pair and an internal bevel pair have each been built through the
app on 2026 with no failure and no interference; neither has been built on 2024.
Spiral and zerol bevel gears are not built: their teeth curve along
the face, which needs a cutter-path geometry and SolidWorks calls this tool has
not probed.

In SolidWorks the pitch apex is at the part origin and the axis along +Z. The
**Blank Sketch**'s half section is revolved into the **Blank**; the **Cone
Sketch** holds the pitch cone line, and **Heel Plane** and **Toe Plane** stand
square to it one module past each end of the face. The tooth space is the spur
section drawn for the virtual gear on the heel plane and scaled onto the toe
plane, and **Tooth Space** is a cut lofted between them, patterned as **Teeth**.
Every dimension is linked, so changing `"No. of Teeth"`, `"Mate Teeth"` or
`"Shaft Angle"` rebuilds the cone, the planes and the teeth.

In **Gear pair** mode a bevel pair is solved from **Cone distance** and Ratio,
each gear's mate teeth being the other's. Rows with a crown or internal bevel
gear say so (*B crown · exact*), and an internal bevel pair is checked for tip
clash on its back cones, as a ring is. The assembly sets the two apexes
together, gear 2's axis in gear 1's top plane at `"Shaft Angle"` to gear 1's,
and turns gear 2 by `"Mesh Angle"` so a tooth meets gear 1's space.

## A gearbox from a workbook

A whole gearbox — every gear, where each shaft is from one origin you choose,
and which gears mesh — can be written in an Excel workbook (`.xlsx`) and
brought in. **Import workbook…** in the Gear panel's header offers *Open a
workbook…*, *New workbook…* (a blank one, saved where you say and opened in
Excel, with drop-down lists for the words a column takes), and the
last few workbooks you opened.

| Sheet | Holds |
|---|---|
| Box | the gearbox's Name, its Output folder (blank: the form's Folder), part and assembly templates, the pressure angle and efficiency per mesh that blank cells elsewhere take, and its Process (`Printed` or `Machined`) and Nozzle (mm, blank 0.4) for every gear in it |
| Shafts | one row per shaft: X, Y and Z of a point on its axis, from the origin; its Axis (`Z+`, `Z-`, `X+`, `Y-` …, or a direction `dx, dy, dz`); its Role (`input`, `output`, `fixed`); on an input, its speed in rpm and torque in N·m; and on a planet shaft, the carrier it is Mounted on and its Copies |
| Gears | one row per gear: the shaft it is on, how far along the axis its face's middle is (At; a bevel gear's pitch apex), and the values the form takes — Kind, Teeth, Module, Face width, Bore, Helix angle, Hand, Profile shift … — a blank cell taking the form's default; and a Part name if you want one |
| Meshes | one row per pair of gears in mesh, and its efficiency |
| Modes | the positions of sliding gears, one row per mode |
| Results | written by the app on Export, and never read |

A blank Process means Printed for a new gearbox and *as built* for one already
built: a gearbox built before printed gears existed, whose workbook has no
Process row, opens Machined and unchanged, with nothing written, until you type
Printed beside Process on its Box sheet (adding the row). The Workbook window's
**Process** line says which, and how to change it.

Headers are found by name, so columns may be in any order; a column the app
does not know, and a row starting `#`, are left alone. Units are mm, degrees,
rpm and N·m. A formula is read as the value Excel last saved. Axes are written
`Z+`, not `+Z`, which Excel would take for a formula.

The **Workbook** window then stays linked to the file: save in Excel and,
within about two seconds, it is read again, checked again, and the window lists
what changed, cell by cell. Every problem names its cell (*Gears!F3: Teeth must
be a whole number (got '68.5').*), and every gear says what Build will do with
it. The window works out what the rows add up to (*Parallel train · 2 meshes ·
12.000 : 1 · output turns the same way*), draws the gears seen from +Z, each
turned so its teeth sit in its partner's spaces — a gear on a shaft along X, Y
or a slant as its section seen side-on, its shaft as a line — and gives each
shaft's speed, which way it turns and its torque (about the shaft's own axis,
seen from its + end, once any shaft is not along Z). Nothing reaches SolidWorks until you press
**Build** or **Update SolidWorks**.

**Checks and fixes.** Two gears listed in Meshes must sit where their teeth put
them, within 0.005 mm. When they do not, the error offers fixes: move the shaft
(and every shaft beyond it, so the other meshes stay right) to where the teeth
need it, or keep your positions and profile-shift both gears to meet them
(*x +0.084550 / +0.084550 → 64.000 exact*). A chosen fix is checked at once
and can be undone; it is written to the workbook only on **Export**, and Build
and Update SolidWorks wait until it is, so the workbook and SolidWorks agree.
A profile-shifted pinion inside a ring is held to the working centre distance
its shifts make, not the plain one, with the same error and move fix as an
outside pair (a shifted pinion at the plain distance clashes when built).

**Shafts at an angle (phase W6).** A shaft's Axis may be `X±`, `Y±` or any
direction. Across an angle, gears on shafts that meet are a bevel pair — each
bevel gear is cut for its partner's teeth and the angle between the shafts,
worked out from its Meshes row and the two axes, and the two must meet apex to
apex (the check gives the At that would put them there) — and gears on shafts
that pass each other are a crossed helical pair, whose hands and helix angles
must make the angle the shafts cross at, at the centre distance along their
common perpendicular. Spur and ring gears mesh only on parallel shafts. A shaft
along X or Y is laid out from two offset planes, as a Z shaft is, so moving it
is an Update; a slanted shaft is a fixed line, so any change of it needs Build
again…. The gear mate between shafts at an angle turns the right way by a rule
probe tier 9 found on SolidWorks 2026 for the angles it ran (30° to 150°
between shafts that meet, 60° to 120° between shafts that pass); a mesh outside
those, or on a SolidWorks whose findings lack the rule, is refused before Build
with a sentence, and Build parts still makes its parts. Moving a crossed shaft
to the other side of its partner turns its mesh the other way round, and
Update makes that gear mate again. Shown on SolidWorks 2026 by the
demonstration, with a confirming build on 2024 (logs in `probe/results/`).

**Planetary stages (phase W7).** A shaft row `Mounted on` another shaft is a
planet shaft on that carrier, its X, Y, Z and Axis read in the carrier's own
frame, and its Copies stand evenly round the carrier's axis (`Planet copy 1`,
`Planet copy 2` …: one part file, a component each). The stage is one sun, one
ring and one spur planet gear, every shaft of it facing the carrier's way along
Z+ or Z-, with exactly one of sun, ring and carrier set to Role `fixed`. The
checks hold the ring's teeth to the sun's and planets', the copies to the
assembly condition (sun and ring teeth together divisible by the copies) and to
the room round the carrier; speeds are worked out with the carrier term, a
planet's both about its own axis and on its carrier, and the torque through the
stage with the held member's reaction. The carrier is built as a part of axes and
planes only, `Planetary_4to1_C_Carrier`: no plate and no pins, which depend on
the gearbox at hand and are yours to add (the user's decision). A gear on the
carrier's own shaft is built locked to it. A planetary form this version does
not build — a differential (no member held), two of its members given Role
`input` (even at speeds that agree), a compound or double planet, a helical
planetary, a carrier on a carrier, two stages — is an error at its cell, not a
row waiting for a phase. Built and tested against the test suite's
fake SolidWorks; on SolidWorks only the gear mates of a 4 : 1 have been
measured (a spike on 2026), and the demonstration is still to run.

**Sleeves, dog rings and modes (phase W8).** A `sleeve` is a ring of teeth
inside that turns with its shaft and slides along it; a `dog` is a ring of
teeth outside fixed to its shaft. A gear with `Slides` (`H=-10, N=0, L=+10`:
named positions, mm along its shaft from its At) slides, and each row of the
Modes sheet puts every slider at one of its positions. What each mode engages
is worked out, never typed: a sleeve whose face covers a dog's whole face locks
the dog's shaft to its own; a sliding gear meshes its partner where it covers
the narrower face whole (a partial cover is an error in that mode). Speeds, torques, the ratio and every check are worked out per mode — a
shaft a mode leaves free *turns freely* there, and an output that also drives
onward has its torque marked as shared. In the Workbook window the Speeds
panel's header gets a **mode chooser**, one button per mode: the panel and the
end view show the chosen mode. It changes only what the window shows, never
SolidWorks. Build makes one assembly configuration per mode, named as the mode,
the first Modes row the one it opens in: each slider held at its place in each
configuration by one distance mate, and each coupling a 1 : 1 gear mate,
switched on only in the modes that engage it; switch mode in SolidWorks'
ConfigurationManager. The sleeve and dog parts are the strip's own ring and
spur teeth at the row's teeth, module and face, at the Box's pressure angle
(20° unless typed): no fork groove, hub or chamfers, which depend on the
gearbox at hand and are yours to add. The strip refuses to open a sleeve's or
dog's `.gear.json`; its workbook is where it changes. A slider on a fixed shaft,
on a shaft at an angle or on a planet, a bevel gear that slides, and a coupling
between shafts facing opposite ways are errors at their cells. Built and tested
against the test suite's fake SolidWorks; on SolidWorks only the probes have
run (the spike and its follow-up, on 2026 and on 2024), and the demonstration
is still to run.

**Export** writes the chosen fixes' cells and a Results sheet — each shaft's
speed and torque, each mesh's ratio, centres and contact ratio, the overall
ratio, and the box size (across the gears' outside diameters and faces, naming
any gear it leaves out) — into the workbook. It changes only those cells and
leaves everything else in the file as it was. It never writes over a formula:
when a fix's cell holds one, Export says what the fix would make it, and once
Excel has recalculated, Checks say whether the formula put that shaft where its
meshes need it; Results wait for that, and the window asks you to Export again.
Close the workbook in Excel first, or use **Export as…** to write a copy, which
never overwrites a file either. After Export has written cells into a workbook
that has formulas, Build and Export wait for you to open and save it in Excel,
since formulas may depend on the cells written and hold their old values until
Excel recalculates; until then Checks are marked provisional and offer no fixes.
If every cell a fix names holds a formula, nothing is written: change the
formula, or a cell it reads, in Excel.

**Build** makes the whole gearbox in the output folder, named for the Box's
Name: every gear as a part, exactly as the form builds the same values, each
with its `.gear.json` (identical gears share one part file); a layout part,
`Reducer_12to1_Layout.SLDPRT`, holding an axis per shaft, `"S2 Axis"`, through
planes set from the origin by globals such as `"S2 X"`; and an assembly,
`Reducer_12to1.SLDASM`, with the layout part fixed at the origin and each gear
placed on its shaft at its At, turned so its teeth sit in its partner's spaces,
then mated: one gear per shaft is mated to its shaft's axis and held along it
from the layout's Front plane, any other gear on the shaft is locked to it, and
each mesh is a gear mate at the tooth ratio. Before it saves, SolidWorks is
asked whether every mate took, whether any is in error, and whether every
turning gear is still free to turn (the app never drives the train itself);
if SolidWorks refuses or flags a mate, no assembly is saved (the parts and the
layout part are kept, and the sentence names the mate), and Build waits until
the workbook changes, since the same workbook would make the same mates. It
then runs SolidWorks' interference detection: *no interference between the
gears where they stand*, or a check naming the two gears and the volume, and
says which gear to drag: *drag G1 in SolidWorks and the rest of its train
follow*. That the app's own build then turns at its ratio, the right way, was
shown on SolidWorks 2026 and 2024: by a temporary driving mate in the
demonstration, and by a person dragging the input. (When a finding the mates need is missing for the SolidWorks in use,
the gears are placed meshed and fixed instead, and the window says so before
Build. A gearbox built before the gears could be mated stays static, and
Build again… offers a new revision whose gears turn.) A part
or layout already built and unchanged is reused, after it is opened and checked
to hold exactly what the workbook asks — one that does not (an update lost when
SolidWorks closed unsaved, a feature deleted by hand) is noted, nothing is
built, and the next press makes that part new; a build never overwrites a file,
and a part whose file name is taken gets its own `_r2` (never the name another
row's Part name asks for). A workbook copied with its folder builds a gearbox
of its own beside the original's files and leaves them alone; when the
workbook its record was written for is gone, the window asks once whether this
one was moved there or is a copy. "Moved" is remembered in the record; "a copy"
holds until Gear Generator closes, so until the copy builds a gearbox of its own
a mistaken answer is taken back by opening the workbook again in a new session.
While a build runs, the record keeps a journal of what it is about to make, so
if the app is killed, crashes or is quit while SolidWorks does not answer, the
next Build checks what SolidWorks saved and reuses it rather than go beside
it; a file stays in the journal until it is on record or gone. A workbook
build (and Update SolidWorks) rebuilds its assembly top-only, so the parts and
the layout part it inserts are expected to be left as saved (the next run on
SolidWorks is to confirm it); until 2026-11-14 it rebuilt every component, which
left them all marked modified. The assembly itself reads modified after a
build: the reads made after it is saved (its frames read back and/or the
interference check; which of them is not yet settled) leave it marked.
Nothing is lost by closing it without saving, since the file on disk is the
one the build saved. A gear pair's assembly, whose gears are held by mates, is
rebuilt in full as before, whatever a later finding says about the workbook's
own mated gearbox.

**Update SolidWorks** carries a later edit of the workbook into what was built:
the values of a part whose row changed (it keeps its file name, so
`Gear_m1.5_N68` may now hold 69 teeth; the sentence says so), the layout's
globals for a shaft that moved, and each gear whose place changed re-placed
where the workbook now puts it, then interference again. On a gearbox whose
gears turn, a gear turned by hand in SolidWorks stays where it was turned
unless Update must move a gear of its train; then the whole train is put back
at the turn it was built at, and the sentence says so. An anchor's move along
its shaft sets its distance from the Front plane; a change that would take its
front face onto, off or across that plane, or a tooth change that alters a gear
mate's ratio (until the probes settle how a ratio is changed), needs Build
again…, and the sentence names the edit. It compares with SolidWorks itself, not
only with its record, so a gear dragged by hand is put back. **Update does not
save**, as the form's Update values does not: the window names the documents
it changed — save them in SolidWorks to keep them — and says so until you
have (or, if SolidWorks closed them without saving, to press Update SolidWorks
again). Nothing waits for that save: a build that would reuse a part Update left
unsaved makes that part new instead, and says so; saved, the part is reused.
A later job that loads those documents from their files settles them: an
Update that finds them holding the workbook's values clears the marks, so a
change lost when SolidWorks closed unsaved never holds a part back for good.

**Build again…** builds the next revision, `Reducer_12to1_r2_Layout.SLDPRT`
and `Reducer_12to1_r2.SLDASM` (then `_r3`, …), beside the first: new parts for
the rows that need them, the unchanged parts reused, and nothing overwritten.
It is what a change Update cannot carry needs — a gear, shaft or mesh added or
removed, a shaft's X or Y crossing, reaching or leaving 0, another recipe, a
bore added or removed, a Part name changed, a built file moved away, a
component deleted in SolidWorks — and Update SolidWorks then offers it, asking
first (Build again… always asks). The question says what the new revision
makes and reuses, why a part is made new rather than reused (for one Update
left unsaved: answer No and save it to reuse it), and that the reused parts
are shared, so a later Update that changes one of them changes the earlier
assembly too.

`Reducer_12to1.workbook.json` beside the workbook records what was built, from
which version of the workbook, and what Update changed and has not been saved;
the header says *built from this version*, *changed since it was built*, or,
while an update is not saved, *updated from this version, not yet saved*.
Closing the app while a workbook's build or update, or the strip's own build,
runs waits until what it saved is on record; closing it a second time while
SolidWorks does not answer (a dialog open there, say) asks whether to quit
anyway.

The layout part and assembly were settled on SolidWorks 2026 and 2024 by probe
tier 7 (`p7_workbook`; `probe/results/latest.json`, `probe/results/sw2024/`), and
a smoke test of the gearbox build, its reuse and Update passed on 2026
(`probe/results/gearbox-smoke-20261113-191036.log`): a gearbox built with no
interference, and interference between the two gears of a mesh when one was
turned half a pitch; built again, reusing the saved parts and layout after
checking each; and updated, a dragged gear put back and nothing saved.

The W4 demonstration (`probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`):

- **SolidWorks 2026: all of it, 244 checks, 0 failed**
  (`probe/results/w4-workbook-assembly-20261113-194228.log`, the stopped-build
  rerun `…-200255-a2.log`, the window `w4-window-20261113-195843.log`): the
  12 : 1 reducer built, measured and checked by half-pitch controls; the Excel
  edit (S2 X 64.5, G2 69 teeth) carried by Update; the structural step built as
  `_r2` beside the first, every earlier file unchanged; a build whose assembly
  failed carried on; a pure move (Arc_Move) and helical, herringbone and ring
  placements across Z+ and Z− (Risky_Placements); and the real window run
  through Build, Update and Build again.
- **SolidWorks 2024**: tier 7, the 12 : 1 build, its measurements and controls,
  the Excel edit and Update (`probe/results/sw2024/w4-workbook-assembly-20261113-200555.log`).
  **Not yet shown on 2024:** the structural step and `_r2`, the continued
  build, the pure-move and risky-placement workbooks, and the window run — the
  2024 session ran out of memory; they are to be run in a fresh session.
- The W4 review's fixes made after the demonstration (an unsaved part made new
  rather than waited for, a part's own `_r` suffix, copied workbooks, Update
  touching only what it changes, a job's saved files kept on record whatever
  goes wrong, the footer's sentences, the app's close), and the second
  review's (whose a record is when its workbook is gone or reached by another
  path, marks a job can prove cleared, the journal, quitting while SolidWorks
  does not answer, a value check on the angle unit), and the third's (the
  whole list of open documents read, and a document holding unsaved changes
  never counted as loaded from its file; the journal never cleared
  wholesale; a copy's "No" for the session only), are tested against the
  test suite's fake SolidWorks only, and await a rerun of both scripts on
  SolidWorks — the assembly check's new section `a3` shows the journal and the
  marks clearing there.

What is not built yet:

- **Planetary stages (phase W7)** are shown on SolidWorks 2026, with a
  confirming build on 2024 (`docs/HANDOFF-WORKBOOK.md`, *W7 in detail*); what
  is left is a person's drag of the sun by hand.
- **Sleeves and modes (phase W8) on SolidWorks**: the demonstration is still to
  run. Sliding gears (as opposed to sleeves) are designed and tested against
  the fake with made-up workbooks only: neither W8 fixture has one.
- W8 was the last phase of the import as planned on 2026-11-11; W9 (issue #1)
  builds on it and leaves no row waiting for a phase. What this version does
  not build is an error at its cell that says so.

## Driving SolidWorks

The app attaches to a SolidWorks that is already running — it never starts one
— through the Running Object Table, so with several versions installed it uses
the one on screen. It needs SolidWorks 2024 (revision 32) or newer: every API
call it makes, and every kind of gear end to end, was probed on SolidWorks 2024
and 2026 (see `probe/results/sw2024/`); crown and internal bevel pairs, and a
workbook's layout part and assembly through the app, whose probes are newer,
have been built whole on 2026 only. 2025 sits between them and was not
probed.

It only ever works in documents it made. Nothing you have open is touched.

Every SolidWorks call the build makes was first run by the probe against a live
session, and the results are committed under `probe/results/`:

```
./probe.sh                 from WSL, through the Windows Python beside SolidWorks
probe.bat                  from Windows
python -m gear_generator.probe --list
```

The probe works in scratch documents under `Documents\GearGeneratorProbe` and
closes only what it created. Its last tier builds a whole gear through this
app's own code and changes it through its equations. What it settled is in
`src/gear_generator/findings.py`, and `tests/test_findings.py` holds those
constants to the committed results.

`python -m gear_generator.swcom [--templates] [--equations]` prints what this
machine's SolidWorks looks like from here: the sessions found, the default
templates, the open documents, and the active document's equations.

## Building the executable

```
pip install pyinstaller pywin32
build.bat
```

makes `dist\Gear Generator v0.3.exe`.

## Development

```
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
```

The tests need no SolidWorks and no display. The build runs against a fake
SolidWorks in `tests/test_swbuild.py`.

`python -m gear_generator.gears --spec m=1.5,z=25 --recipe A` prints the build
plan for a gear — every global and every step — without SolidWorks. Add
`process=printed` (and `nozzle=0.4`) to the spec for a printed gear; left out, it
is machined, as any spec built in code is.

`docs/PLAN.md` is the design the app was built to.
