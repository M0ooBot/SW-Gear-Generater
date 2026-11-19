# F3's demonstration on SolidWorks: the sections, the masters, the commands, the STOPs

The script is `probe/f3_demonstration.py`. It is the SolidWorks part of PLAN-PRINTED §4.6's *Done when* for stage F3 (the bore
allowance and the D-flat): every section clean on SolidWorks 2026, and on 2024 as the confirming build. It was written on
Linux against branch `printed` with packages A, B and C in, F3-REVIEW's fixes and the switch's commit (`262c0f7`, which turned
`spur.PRINTED_DEFAULT_IN_PLANS` on). It was then brought to its review (`F3-DEMONSTRATION-REVIEW.md`, `743cd75`): M1, M2 and
every should-fix but S8 (the words, after the run) are taken, below. Its self-check passes at `743cd75`'s tree (**18 checks,
0 failed**, Tk present, the switch on). **It has not run on SolidWorks.** Expect script faults on its first live run, as
every demonstration had.

**How it works.** It runs W9a's `main` with its own six sections, as F1's and F2's scripts do, and changes no other script.
It imports F2's live part (`import f2_demonstration as F2`), which brings W9a's harness with it: the attach by `--pid` and its
check, the dialog watch with the What's Wrong rule per version, keep-awake, the JSON after every section, APPDATA in
`<out>\appdata`, the guarded close, `--sections` and `--redo`, Desk9 and its `press` (Update SolidWorks), `keyway`, `save_user`,
`copy_desk` and `users_in_copy`; and F2's own: the strip's real `gui.GearApp` (its link not started; `make_form`), the
presses' `Strand`, `activate`, `features_of`, `press_form`, `written` (a Print files press judged whole) and `patched`.
`--close-outlived-whats-wrong` is W9c's own close path, put in only when the flag is given. Build again… in `userwork` is
W9d's `DeskD` (the window's `_start_build` with `old_assembly` as `before` and `carry_for` as `carry`), by `w9d_demonstration.copy_desk`.
`hub` turns RangeBox_Fixed through its modes with W9b's own `mode_read` and `judge_every`.

The self-check cannot import F2's live part (W9a's harness parses the run's arguments at import). It reads F2's pure
part instead, everything above F2's `if SELF_CHECK:` line, executed into a module of its own (`_f2_head`), which the review
found acceptable. F2's file is not changed.

**The switch.** `spur.PRINTED_DEFAULT_IN_PLANS` (F3-INTERFACES §13) is read from the module at call time. The log's first
line says what it reads, and every section says it again. `allowance`, `print` and `built` judge the printed default, and
each ends at its start with a sentence (a section STOP, not the run's) when the switch is off. `dshape`, `hub` and `userwork`
judge typed and as-built figures only and run either way. Where `built` needs what F2's code built, it builds it in the run
with the switch set False in this process only, says so in the log (`switch` and `patch` lines), and puts it back.

**Every build's sketches.** `swbuild` puts a sketch not fully defined in a build's `checks`, not its failures, so `result.ok`
passes one (the review's S2). Every build here is held free of it: the form's builds, the twins, `allowance`'s parts, the
12 : 1's three builds, RangeBox_Fixed's and both of `userwork`'s Build again… (each part a gearbox build built).

## Where this departs from the plan and the brief

The review found both departures right (§3 of it).

1. **The sections are the coordinator's brief's five and the review's `hub`**, not PLAN-PRINTED §4.6's (`dshape`, `bore`,
   `kinds`, `update`, `workbook`). Where the plan's items are: `bore` is `allowance` and `print`; `kinds`' helical, herringbone and
   bevel are in `allowance`; `update`'s two refusals are `dshape`'s structural steps and `built`'s G4; `workbook`'s hub gearbox is
   `hub`, and its setup.master with Printed is `userwork` with, for a gearbox built before F3 that has bores, `built`'s machined
   12 : 1. **Not here:** the bevel's D-flat refusal on SolidWorks (A's diagnostic, made before any SolidWorks call and held
   by A's tests).
2. **built: an allowance typed on a part built before F3 cannot change its bore in place.** Such a part has no
   `"Bore Allowance"` global, so none to some is structural (G4, §4.4): Update refuses it and Build again… makes the part
   new. The script shows exactly that on F2's 12 : 1, and shows the in-place change and K11 on the printed 12 : 1 built with
   the switch on, whose parts hold the global.
3. **userwork: setup.master's Sun has no bore** (RangeBox's rows leave Bore blank; Sun holds `"Bore Diameter" = 0`), so it
   has no bore to take an allowance or a D, and no bore face for a mate. Typing Bore, an allowance and a D for Sun is
   structural, so the first press is Build again…, which gives Sun its D. The user's work is then put on the new Sun, Sun's
   allowance and Flat are changed in place by one Update, and a last Build again… (Sun's Part name changed, its allowance
   cleared) shows the as-built allowance kept and the bore-face mate carried.
4. **dshape's "from round to D and back"**: Drive is structural (§4.2), so Update values refuses each way in B's words
   and the form's Build makes each new.
5. **The hub in `allowance`** is not a strip kind: it is built by the app's `plan_for` and `swbuild.build` (the strip's own
   job) and its `.gear.json` written by the form's own `_write_sidecar`, as every part of `allowance` is. The hub in a gearbox is
   `hub`.

## The masters each section needs

- `dshape`, `allowance`, `print`, `hub`: none. Each builds into a fresh folder of `<out>` (`hub` writes RangeBox_Fixed by the app's
  `write_new` and builds it).
- `built`: none given. It builds W9's 12 : 1 three times through the app's own Build (W8's `write_fixture` and `build_turning`,
  about 1.5 min each): printed with the switch off (`f3-reducer-off.master`), printed with it on (`f3-reducer-on.master`), and
  machined with it off (`f3-reducer-machined.master`), each kept in `<out>` and reused by a rerun there;
  `--reducer-off-master`, `--reducer-on-master` and `--reducer-machined-master` give ones an earlier run of the same SolidWorks
  version kept. (F2's own `f2-reducer.master` is not taken: its workbook has no Bore allowance column, and F3's switch-off
  build is F2's code by F3-0's pins.)
- `userwork`: **`--user-master` is required**, W9a's `setup.master` for the version run, only copied:
  - SolidWorks 2026: `<probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master`
  - SolidWorks 2024: `<probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master`
  - The 2026 master does not open in 2024. `<probe folder>` is `C:\Users\M0obo\Documents\GearGeneratorProbe` on this laptop.

## Sections

Times are estimates from the measured steps of W9a's, W9b's, F1's and F2's runs (a part 15 to 25 s, the 12 : 1 built about
1.5 min, a value Update on the 12 : 1 about 25 s, RangeBox's first Update 2.7 min on 2026 and 5 on 2024). F2's sections ran
in about a third of their estimates, so these are generous.

| Section | What it does | 2026 | 2024 |
|---|---|---|---|
| `dshape` | The D built by the form; 13 steps of Update values (9 written, 2 past a bound, 2 structural); D to round and back by Build; 9 twins built from scratch; every state read. | 6 min | 9 min |
| `allowance` | 15 parts (5 kinds × default, typed, machined), each built, read and closed. | 6 min | 9 min |
| `print` | 2 parts built by the form and pressed; each STEP file read. | 2 min | 3 min |
| `built` | The coupon by F2's code and its strip reads; the 12 : 1 built three times; a quiet Update, a typed allowance, an in-place Update, K11's press; the machined one typed Printed and Updated. | 12 min | 17 min |
| `hub` | RangeBox_Fixed printed with the Hub's D, built, every mode shown and read, the Hub's hole read. | 5 min | 8 min |
| `userwork` | RangeBox copied; Printed and one Update; two Build again…; a quiet press; one in-place Update; the user's keyway and bore mate. | 15 min | 28 min |

About 46 minutes on 2026 and 74 on 2024 (the plan's 25 and 40). Expect about a third of that.

### dshape: what each line bears out

A printed spur, m 1.5, z 20, face 8, Bore 8, allowance 0.2 typed, Drive flat, Flat 7 (§4.6's), named DShape, built by
the strip's form and left active; its record open in the strip.

- **The form** shows *Bore as cut* 8.2 · 8 + 0.2 and *Flat as cut* 7.2 · 7 + 0.2; the .gear.json is at schema 4.
- **Each state, read by** `part_read` (the part not activated: `use_open_document`) and judged by `judge_hole`:
  - nothing in error; the Bore Sketch `GetConstrainedStatus` 3;
  - **the bore by its faces** (`bore_judged`), with no reading a padded box could fail (the review's M1; W9b measured
    `GetBox` padding a face about 0.24 mm at each end): every cylinder about the axis in the bore (CylinderParams: axis along
    Z through the origin) of radius R = (D + a)/2 to 1e-4 mm, the arc free to be one face or more (S1); their boxes
    together reaching −X (one-sided: padding only widens a box, so it cannot pass a sliver, whose round lies between x = h
    and R); exactly one plane square to the end faces within the bore, its normal along X, its plane at x = h (PlaneParams'
    point) to 1e-4 mm, on +X. **Facts, not judged** (`bore_facts`): how many faces the round is, its boxes' x range and the
    padding beyond −R, the round's greatest x past the flat, and the flat's span along Y against the chord;
  - **the tip lands** (`lands_judged`): the cylinders about the axis at d_a / 2 the spaces leave number 20. Where they sit
    (ruling 2's space on +X: the box centres of the two nearest at ±9°, none crossing +X) rests on partial faces' boxes no
    run has read, so it is logged as a fact (`lands_facts`), to be judged once a log shows the boxes tight;
  - **the links as SolidWorks holds them** (`link_judged`): `"Flat@Bore Sketch"`'s expression, spaces aside, is the app's
    `chord_expression` text (`2 * ( ( abs ( … ) ) ^ 0.5 )`), holds no `sqr`, and evaluated by the app's evaluator on the
    values SolidWorks holds gives the chord worked here to 1e-6 mm; `"Bore@Bore Sketch"` evaluates to R (a round's to D + a);
    and **SolidWorks' own Value** of each agrees with the figure to 1e-6, read as mm or as m (S4: its unit is not documented
    for a dimension's equation; the unit it agreed in is logged);
  - the F3 globals: `"Bore Allowance"` the allowance, `"Bore Flat"` the Flat;
  - **the volume within 0.1 % of its twin**: the same spec built from scratch by the app's plan and build in a folder of its
    own, its sketches fully defined, read, closed unsaved (once per spec).
- **Each value step** (Flat 7 → 5 → 7.6 → 7; Bore 8 → 10 with Flat 9; allowance 0.2 → 0.4; Flat 6.1, h at 0.25 R exactly;
  Flat 9.7, the flat 0.3 deep exactly; back to 8, 7, 0.2; allowance −0.1, a press fit): the strip counts exactly the globals
  the step changes, Update values sets those and no other in one rebuild with no landing route, and the record follows.
- **Each bound step** (Flat 6 at D 10 a 0.4, h 1.2 under 1.3; Flat 9.8, 0.2 deep): A's sentence at Flat on the form (the
  script's copy held to `bore_checks` in the self-check), Update values says *The gear on the form does not work out yet, so
  nothing was updated.*, nothing sent, the part's globals and its .gear.json as they were.
- **Each structural step** (the allowance −0.1 → 0; Drive flat → round): B's sentence exactly, nothing sent, nothing
  changed.
- **D to round and back**: a round part (DShape_Round, a 0.2) built by the form from the D's record; judged as above (no
  flat); Drive flat on it refused in B's words; a D (DShape_D) built from it, judged against the first twin.

A far-side solve shows as the plane at −h, a round that does not reach −X, the plane off h (a wrong chord), a radius off,
or a volume off its twin; per the plan it is the run's finding, with one follow-up round. A D that fails to solve raises
What's Wrong, which on 2026 is the STOP: so on 2026 `dshape` runs alone first (S7).

### allowance: what each line bears out

For each of F3-0's pinned machined gears that a bore reaches and the strip or a hub row builds (tests/test_printed_rule.py's
`spur` m 1.5 z 25 Bore 10, `helical` β 20°, `herringbone` m 2 z 20 β 30° (S5), `bevel` 20 on 40, `hub` m 1.25 z 17 face 20 Bore 8),
three parts in folders of their own: printed with the allowance blank (the default, 0.2), printed with one typed (spur −0.1,
helical, herringbone and bevel 0.3, hub 0.25), and machined.

- the part built clean (nothing in error, every sketch fully defined);
- **the hole as cut**: the smallest cylinder about the axis, by CylinderParams, at (Bore + a)/2 to 1e-4 mm (a bevel's is its
  revolved blank's inner edge), and the bore judged round by its faces (every cylinder in it at that radius, no flat);
- the globals as SolidWorks holds them: `"Bore Allowance"` the allowance when printed, neither F3 global when machined;
- the .gear.json the form's `_write_sidecar` writes: schema 4 printed, 1 machined;
- the machined part's record (spec, derived, globals) equal to F3-0's pin's (`sidecar_text`), whose hash the self-check holds
  to `SIDECARS`, and its plan to `STRIP`: so "exactly as before F3" rests on F3-0's pins offline and on these reads live.

### print: what each line bears out

Print_D (the dshape D, 0.2 typed) and Print_R (round, Bore 8, the allowance blank: the default), each built by the form and
pressed on the form with the part active (F2's `require_findings` first):

- **the press judged whole by F2's `written`**: one new press folder named by its time, the file and the list alone, the
  status in C's words, the file framed, AP203/214/242, one closed solid in millimetres, the outer radius 16.5 and face 8 to
  0.01 mm, the app's size check (`checked`), SolidWorks as it was, one SaveAs;
- **the bore from the STEP file itself** (`step_bore_judged`, ADVANCED_FACEs read here apart from printout's reader): every
  CYLINDRICAL_SURFACE about Z in the bore of radius (D + a)/2 to 0.01 mm (the arc one face or more); on the D exactly one
  PLANE square to the end faces within the bore, its normal along X and its location on x = h; on the round none; the least
  VERTEX_POINT radius (D + a)/2; on the D at least two vertices of that radius at x = h (the flat's corners);
- **the list's bore line**: *bore 8 mm + 0.2 mm allowance (8.2 mm as cut), D-flat 7 mm (7.2 mm as cut)* and *bore 8 mm + 0.2
  mm allowance (8.2 mm as cut)*, within the part's sizes line.

### built: what each line bears out

- **The coupon by F2's code** (Coupon_F2, §3.2's, printed, Bore 8; the switch off in this process only): its .gear.json at
  schema 3 with no F3 global. With the switch on, opened by the strip's own *Open .gear.json* (`_load_record`): Update values
  counts 0, *Bore as cut* 8, the hole planned with 0 allowance; a quiet Update values runs and changes nothing (no file, no
  .gear.json, no save flag); an allowance typed is refused in B's words, nothing sent.
- **The printed 12 : 1 by F2's code** (`f3-reducer-off.master`, copied): its four .gear.json at schema 3 with no F3 global; the
  window's footer word for word as the same desk planned with the switch off; Update plans nothing; a quiet Update changes
  and places nothing, every SolidWorks file, .gear.json and the record's parts' spec and globals as they were, the only save
  flag the assembly's where the Update rebuilt it (W8's `expected_marks`); G2's allowance typed 0.3 in Excel: one structural
  sentence, naming G2's part, *A bore allowance cannot be added to or taken out of a built part…*, the footer offering Build
  again…, nothing pressed; cleared, Update plans nothing again.
- **The printed 12 : 1 by F3's code** (`f3-reducer-on.master`): every part holds `"Bore Allowance" 0.2` on record; G2's allowance
  typed 0.3 is a value, Update changing G2's part alone; one Update: the result changes G2 alone, G2's hole by its faces (12 +
  0.3)/2 to 1e-4 mm, the global 0.3 in SolidWorks and on record, the other three parts' globals as they were, no file saved.
  **K11**: `"Bore Allowance"` set 0.5 by hand in G2's part, the assembly rebuilt and saved as the person would (W9a's `refuse`
  bore step), pressed again: refused (`UserWorkRefused`) naming `"Bore Allowance"` with its cell `Gears!V…` and the live 0.5, G2's
  globals as they were after.
- **The machined 12 : 1 built before F3** (`f3-reducer-machined.master`; the review's S6, guard 4 live): Printed typed on the
  Box sheet, Update changes the four parts in place, none made new; one Update: each part's `"Backlash"` changed in
  SolidWorks, no `"Bore Allowance"` or `"Bore Flat"` in SolidWorks or on record, each .gear.json below schema 4 (3, a printed part
  with no F3 global, as `test_printed_workbook.py` pins it).

### hub: what each line bears out

The review's M2. RangeBox_Fixed (tests/workbook_fixtures.py, W9b's fixture with the hub) with Printed on its Box and the
Hub row given Bore 8, allowance 0.2, Drive flat and Flat 7. Its mate RangeSlv is a sleeve, which takes no bore field (G9),
so no other row is given one.

- the workbook read with no error and the Hub row's D as typed;
- **built** by the app's own Build (W8's `write_fixture` and `build_turning`, as W9b's `build` section): ok, every part's sketches
  fully defined, no interference in the build's own check; Hub as Output's anchor with RangeSlv splined to it (W9b's
  `hub_mates`);
- **turned through every mode** as W9b turns it (`mode_read`: each mode shown and rebuilt, every body's frame and status,
  every mate's code, the interferences; `judge_every` without §3's table, whose figures are the machined fixture's): every
  body at its frame on record, no mate in error, every app gear free, the bands and dogs where the app's read puts them,
  what is engaged as the app's report, every mate's flag per mode; and **no interference read in any mode**;
- **the Hub's hole as cut**, read as dshape reads a D (no twin): the round at 4.1, the flat at 3.1, the links and their
  Values, the globals, the Bore Sketch fully defined, the tip lands counted; its .gear.json at 4.

### userwork: what each line bears out

On a copy of setup.master (W9a's RangeBox with Sprocket-1..4, Housing-1, eight user mates, the User Keyway in Sun's part):

- Sun read on record as built with no bore, its keyway in no error; every mate's code and state read (`mate_states`).
- **Printed** typed on the Box sheet (F1's and F2's way); Update plans the five parts in place; one Update ends ok with
  nothing of the user's in error; saved as the person saves; every mate and the keyway as before.
- **Sun given Bore 8, allowance 0.2, Drive flat, Flat 7** (the three columns inserted before Part name and headed as the app
  heads them, said, where the workbook lacks them): one structural sentence, Sun's alone; **Build again…** as the window
  runs it (W9d's DeskD, the carry), every part's sketches fully defined; the carry's lines logged, run to its end with no
  user file changed; Sun's new part read as dshape reads a D (no twin), its .gear.json at 4; saved.
- **The user's work on the new Sun**: W9a's keyway cut again (it leaves 0.4 mm to the flat at h 3.1, 0.15 mm at h 3.35, and
  never cuts the D); a concentric of Sprocket-4's bore (radius 5) on Sun's D arc face (radius 4.1; the first such face if
  the arc is two), by AddMate5 on the two faces as W9d's fixture made its face mates, on in every mode, in no error, and
  **its entity on Sun read by `Session.mate_definition` (W9d's): a face whose EntityParams radius is 4.1 to 1e-4 mm** (S3);
  saved; a quiet press changes nothing and records the mate and the keyway in the inventory.
- **Sun's allowance 0.3 and Flat 7.2, one Update**: Sun's part alone in place; the Update ends ok, nothing of the user's in
  error; Sun read as a D at R 4.15, h 3.35; every mate's code and state as before (the bore mate among them, every user
  mate in no error), the keyway in no error; saved.
- **Sun's allowance cleared and its Part name SunGear, Build again…**: SunGear keeps `"Bore Allowance" 0.3` (ruling 1, the cell
  blank on record) and is read as the same D; **the mate on Sun's bore face is carried** (in the carry's `remade`, not `named`;
  made again in no error) and, read by `mate_definition` in the new revision, **lies on SunGear's face of radius 4.15**, so a
  carry onto another face about the axis fails; the user's components in the new revision.

## SolidWorks calls

**None new to the repo.** Each is the app's, or an earlier script's:

- builds: the strip's `swbuild.build` through the form (F1's and F2's demonstrations) and from a plan (W9c's `landing` twins);
  a gearbox's `build_gearbox` (W8, W9b, F2); Build again… with the carry (W9d's DeskD);
- the strip's Update values, `swbuild.update_variables` (F2's `refusals`); the window's Update, `update_gearbox` (W9a's `press`);
- reads: `GetBodies2`, `GetFaces`, `GetSurface`, `IsCylinder`, `CylinderParams`, `IsPlane`, `PlaneParams`, `GetBox` (W9b's `part`
  section's `part_faces`); `feature_states`, `sketch_status`, `volume_mm3`, the Equation Manager's `Equation` and `Value` (the
  app's build check; W9c's landing); `mate_states` (W8, W9a); `Session.mate_definition` (W9d); W9b's `mode_read`
  (`show_configuration`, `component_frame`, `constrained_status`, `interferences`, `mate_suppression`, `dimension_values`);
  `GetSaveFlag` by the walk (F2); the parts' globals by `live_globals` (W8);
- the person's steps: `set_global_variable` and `rebuild` on a part in an assembly, then the assembly's rebuild and W9a's
  `save_user` (W9a's `refuse`); W9a's keyway; AddMate5 on two faces carried into the assembly by `GetCorresponding` and
  `Select4` (W9c's probes' `raw_mate` and `select_face`, as W9d's fixture); Excel's edits (W8) and `Columns(n).Insert` (W9c's
  `ensure_headers`); Print files (F2).

**New in kind, not in call** (the reviewer's to weigh): every read and Update above on a part whose bore is a D (a major
arc and its chord; package B's table lists each call the D's build and Update make and where the app already makes it);
`CreateMassProperty` on a part made the build document by `use_open_document` rather than activated; AddMate5's concentric
on a partial cylinder (W9d's were on full ones); the carry's "bore" on a partial cylinder (`COAXIAL_FACE_READ` was verified
on full cylinders only, W9D-INTERFACES §4.4: this run is its first live reading); a RangeBox Build again… that gives a part
a bore; and RangeBox_Fixed built with a D in its Hub.

## STOPs

As W9a's, which end the run: any window during a job under the version's What's Wrong rule (with
`--close-outlived-whats-wrong` on 2024, W9c's close path); under 2 GB free before a section; a hung worker or a lost
session. These end their section only: the switch off in `allowance`, `print` and `built`; the F2 findings not the reviewed
ones (`print`); under 6 GB free before `userwork`'s copy, its first Update or either Build again…. A script fault fails its
section with the traceback's tail. No What's Wrong is expected: nothing here rebuilds a feature of the user's into error.
A D that will not solve would raise one; that is why `dshape` runs alone first on 2026.

## Without SolidWorks

`PYTHONPATH=src python probe/f3_demonstration.py --self-check`: **18 checks, 0 failed** (Tk present, the switch on). Each
judgement the live sections make is a plain function, held on the app's own figures and failed each way it can fail:

- **the names**: the switch exists; the bounds 0.25 R and 0.3 mm, the default 0.2, the Bore Sketch, the three globals and
  the Gears titles are the app's;
- **§4.2 worked here**: R, h, the chord, the sweep and the bounds' Flats hold the plan's six rows and agree with A's
  `d_flat` on every dshape state;
- **dshape offline**: every value step plans exactly its own globals and is no structural change; the two bound steps are A's
  error at Flat in the script's words; the two structural steps, and D to round and round to D, are B's sentences;
- **the links**: the app's chord and radius texts evaluate to the figures here on every dshape state, and SolidWorks' Value
  agrees read in mm (the chord) or in m (the radius); `sqr`, a chord 0.01 off, none, two, another text and a Value 0.01 off
  each fail, and a Value in neither unit;
- **the faces**: the D holds with exact boxes, **with every box padded 0.25 mm**, **with the arc as two faces**, and with both;
  a round holds; a D read as round, no cylinder, the sliver (also padded), the flat on −X, two flats, the radius 2e-4 over,
  the flat 2e-4 off and a round where a D is wanted each fail; the boxes' facts read the padding back; the tip lands
  counted, padded or not, a land missing failing; their place a fact (a space on +X read so, a tooth there not); the
  volume's 0.1 %;
- **the sketches**: a build's checks, and a gearbox build's parts' checks, saying a sketch is not fully defined are caught;
- **the bore mate's face**: an entity on Sun that is a face of radius 4.1 by EntityParams holds; another radius, an edge,
  none and two each fail;
- **the STEP reader** on made-up files: the D (one arc face, or two) and a round hold; a D read as round, the plane on −X,
  two planes, the radius 0.02 over, the vertices 0.02 out each fail;
- **the words**: Bore as cut and Flat as cut, the list's bore line (a D typed, a round at the default, a press fit, a part
  built before F3), Update values' refusal of a form that does not work out, each the app's;
- **allowance offline**: each of the five kinds' hole as cut, global and schema, printed (switch on) and machined; the
  default planning 0 with the switch off;
- **F3-0's pins**: the five machined gears are `test_printed_rule.py`'s `GEARS`, their plans and .gear.json hold `STRIP` and
  `SIDECARS` (pytest stood in where it is not installed, for the module's decorators only);
- **the live part as source**: each of the 104 names it takes from W9a's, W8's, F2's, W9b's, W9c's, W9d's and W9c's probes'
  scripts is defined there, and every Session member it calls is `swcom.Session`'s;
- **hub offline**: RangeBox_Fixed printed with the Hub's D assesses with no error; the Hub plans Flat 7 at 0.2, its two
  globals and schema 4;
- **the strip's own form** (Tk): the D on the form, its rows, its record at 4; every dshape step through the form's own
  Update values with a job answered here (each value step counting and sending exactly its globals, the record following;
  each bound and structural step refused in its words, nothing sent); the round part's record and Drive flat on it refused.

Not held offline (live only, as the review accepts): the bore mate made, the carry, K11's cell, the machined 12 : 1's
Update, the hub's modes.

## What the script does not measure

- Ruling 2's angle (a tooth space facing the flat) as a judgement: logged from the tip lands' boxes until a run shows
  partial faces' boxes tight. Likewise the boxes' lengths (the flat's span, the round's reach past the flat).
- A D on a helical gear (its flat's angle at the section plane, F3-INTERFACES §3, unverified and unread).
- The bevel's D-flat refusal and a ring's or sleeve's bore fields refused on SolidWorks: diagnostics before any call, held
  by A's tests.
- The D's sketch's arc sweep as SolidWorks holds it (the faces and the volume stand for it).
- RangeBox_Fixed's §3 table with the Hub bored (its figures are the machined fixture's; W9b holds them): `hub` holds the
  modes to the app's own read instead.
- A D bore printed and fitted on a shaft; the allowance's figure from the user's coupons (V1).
- W9d's carry of a bore mate on a part made new **by** its allowance or drive (K5's ruling: named, not found again); the
  carry here is of a part made new for its Part name, the bore as built.
- The window's own warnings (C's `_assess` wiring) on SolidWorks: the window's checks are pure.

## What must be open or closed

- **SolidWorks**: a session started for the run, alone, its PID given; nothing of the user's open with a file name the run
  uses (`DShape*`, `Twin*`, `Gear_m1.5_N25*`, `Helical_*`, `Herringbone_*`, `Bevel_*`, `Hub_*`, `Print_D`, `Print_R`, `Coupon_F2`,
  `Gear_m1.5_N17*`, `Gear_m1.5_N68*`, `Gear_m2_N17*`, `OutputGear`, `Reducer_12to1`, `RangeBox*`, `Gear_m1.25_*`, `SunGear`,
  `Ring_m1.25_N55`, `Dog_m1.25_N17`, `Sleeve_m1.25_N17`, `Sprocket`, `Housing`).
- **Excel**: the script starts and quits its own; no `Reducer_12to1.xlsx`, `RangeBox.xlsx` or `RangeBox_Fixed.xlsx` open in the
  user's.
- **The laptop**: on mains power, the lid open; over 6 GB free for `userwork`; WSL idle during the 2024 `userwork` and `hub`.
- **Tk**: every section but `hub` and `userwork` opens a hidden Tk window in the script's own process.

## Command lines

As the review gives them. Make a `git archive` of the commit to run (at or after this one) into `RUN\snap` with
`SNAPSHOT_COMMIT` beside `src`, run `--self-check` on the snapshot first, start a fresh SolidWorks for each invocation and give
its PID. One `RUN\out` per version; each invocation its own log.

```
rem SolidWorks 2026, first: dshape alone (a D that will not solve is a What's Wrong, the STOP on 2026; about 6 min)
python.exe RUN\snap\probe\f3_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\f3-demo-sw2026-1.log ^
    --sections dshape

rem SolidWorks 2026, then the rest in a fresh session (about 40 min; rerun userwork alone in a third fresh session if
rem the 6 GB floor stops it)
python.exe RUN\snap\probe\f3_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\f3-demo-sw2026-2.log ^
    --sections allowance,print,built,hub,userwork ^
    --user-master <probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master

rem SolidWorks 2024, the confirming build: userwork and hub first, in a fresh session, WSL idle (about 36 min)
python.exe RUN24\snap\probe\f3_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f3-demo-sw2024-1.log ^
    --sections userwork,hub --close-outlived-whats-wrong ^
    --user-master <probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master

rem then the rest, in a second fresh session, dshape first (about 38 min)
python.exe RUN24\snap\probe\f3_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f3-demo-sw2024-2.log ^
    --sections dshape,allowance,print,built --close-outlived-whats-wrong
```

**The order on 2024, for memory**: `userwork` and `hub` first in their own fresh session (RangeBox's Updates, two Build
again… and RangeBox_Fixed's build grow SolidWorks 2024 by several GB; F1 measured 3.1 to 7.0 GB over two RangeBox presses),
then the four others in a second fresh session, `dshape` first. No close flag on 2026; `--close-outlived-whats-wrong` on every
2024 invocation.

**Re-running.** A section `RUN\out` already holds is skipped and said; `--redo` sets its folders aside (`<name>.prev-<time>`) and
runs it again. The three `f3-reducer-*.master` folders are not a section's and are kept.

The JSON (`f3-demo-<time>.json`) is written beside the log after every section: the switch as read; dshape's every state
(its faces summed up, the boxes' facts, the tip lands' facts, its links, their Values and the unit each agreed in, its
globals, its volume, what did not hold) and the twins' count; allowance's hole, schema and problems per part; print's press
folders; built's K11 sentences; hub's modes and interferences and the Hub's hole; userwork's carry lines.

## For the reviewer (the re-check)

Taken from the review: M1 (`bore_judged` without the boxes' padding; `bore_facts` and `lands_facts` log what the boxes say; the
self-check's padded and split cases), M2 (`hub`), S1 (a split arc, in the faces, the STEP file and the bore mate), S2 (every
build's sketches), S3 (`mate_definition` on the bore mate, made and carried), S4 (the links' Values, mm or m), S5 (the
herringbone), S6 (the machined 12 : 1 typed Printed), S7 (the command lines), and the round hole in `allowance` judged by its
faces. S8 is words for after the run. Look hardest at `hub` (W9b's `judge_every` run without §3 on a printed fixture whose
Hub is bored) and at the bore mate's EntityParams radius in metres (W9d's `entity_key` reads it so).
