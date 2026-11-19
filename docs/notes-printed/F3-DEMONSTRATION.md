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

## The first run on SolidWorks 2026 (2026-11-18, from c5d4391, then 75d27cf; SolidWorks 2026 34.1.1)

**Setup.**
- Run folder `<probe folder>\f3-demo-sw2026-20261118-214917`. `snap` a `git archive` of `c5d4391` with `SNAPSHOT_COMMIT` beside
  `src` (runs 1 and 2); `snap2` a `git archive` of `75d27cf`, the fixes below, for run 3. Each log's head names its snapshot (3).
- `--self-check` on each snapshot: under Linux's Python 18 ok, 0 failed; under the run's Windows `python.exe` 17 ok, **1 failed**:
  *pins* (F3-0's STRIP hashes for the five machined gears). The plans differ from Linux's in the last bit of two dimension
  label coordinates (`at=(17.182694782833106, 17.182694782833103)` on Linux, `…106, …106` on Windows; `-4.596194077712559`
  against `-4.59619407771256`): libm's `sin`/`cos`, nothing geometric. The SIDECARS hashes match on both, and the live
  `allowance` section holds the machined records to `sidecar_text` only, so the run does not lean on STRIP. Not changed;
  for a ruling (F3-0's pins are Linux-only as committed).
- Three sessions, each started fresh in the background with nothing open (PIDs 56800, 57792, 36236) and exited after
  (`taskkill` without `/F`; each went). Before the first, `tasklist` showed no SLDWORKS.exe, no Excel and no python.exe (only
  SolidWorks' two `sldworks_fs.exe` services, before and after). Each invocation started and quit its own Excel.
- Master, only copied: W9a's `setup.master` (`<probe folder>\w9a-final-sw2026-20261117-023433\out`). **The masters' hashes are the
  runner's statement, outside the script, not in the logs**: `sha256sum` of both versions' `setup.master` (34 files) was
  taken before the 2026 run, between the versions and after the 2024 run. The first listing was lost when the runner's scratch
  folder was cleared during the run; the second and third match exactly, and no file of either master is newer than
  2026-11-17 (the newest 02:53 that day), so nothing was written into them.
- **Nothing written outside the run folders**, the runner's statement: a listing of `<probe folder>` outside the `f3-demo-*`
  folders (50,415 entries, path, size and mtime) was the same between the versions and after the 2024 run (the listing before
  the 2026 run was lost with the hashes); nothing in it, and nothing in the user's Documents or Desktop two levels down, is
  newer than the 2026 run's start but the probe folder itself (the run folders made in it). APPDATA went to `out\appdata`.
- Run 1: `--sections dshape`, alone first (S7). Run 2: `--sections allowance,print,built,hub,userwork --user-master …`.
  Run 3, after the fixes: `--sections print,built,userwork --redo --user-master …` into the same `out`, the machined 12 : 1's
  master of run 2 set aside by hand (`f3-reducer-machined.master.prev-…`: a section's `--redo` keeps the reducers' masters,
  and run 2's had been built printed, below), the switch-off and switch-on masters reused. No close flag.
- Logs `probe/results/f3-demo-sw2026-20261118-1-dshape-clean.log` (JSON `f3-demo-20261118-215150.json`),
  `…-2-allowance-print-built-hub-userwork-13-failed.log` (`…-215759.json`) and `…-3-print-built-userwork-rerun-2-failed.log`
  (`…-223549.json`); below, `1:`, `2:` and `3:` are their lines.
- SolidWorks time about 71 min (21:51 to 23:02), the runs 4.5, 34.5 and 24 min.

| Section | Run | Time | ok | FAIL | STOP | SolidWorks private, peak logged | Free, least logged |
|---|---|---|---|---|---|---|---|
| dshape | 1 | 268 s | 44 | 0 | 0 | 1.12 GB | 9.47 GB |
| allowance | 2 | 485 s | 15 | 0 | 0 | 1.08 GB | 9.59 GB |
| print | 2 | 36 s | 23 | 2 (script) | 0 | 1.14 GB | 9.54 GB |
| built (three reducers built here) | 2 | 370 s | 90 | 5 (script 4, app 1) | 0 | 1.63 GB | 9.08 GB |
| hub | 2 | 212 s | 23 | 0 | 0 | 1.94 GB | 8.87 GB |
| userwork | 2 | 997 s | 37 | 6 (script) | 0 | 2.40 GB | 8.45 GB |
| print | 3 | 40 s | 25 | 0 | 0 | 0.98 GB | 9.40 GB |
| built (machined 12 : 1 rebuilt) | 3 | 218 s | 62 | 1 (app) | 0 | 1.49 GB | 8.73 GB |
| userwork | 3 | 1213 s | 46 | 1 (script) | 0 | 2.21 GB | 8.34 GB |

**Every FAIL, with its cause.**
- *print, D and round* (2:162, 2:271): *41 planes in the D, not one*, *40 plane(s) in a round bore*. **Script.** The STEP reader
  took every plane square to the end faces whose plane passed within (D + a)/2 + 1 of the axis as in the bore, and each tooth's
  radial flank lies on a plane through the axis (the files hold 40, at 14.1 mm out). Fixed in `75d27cf`: a plane face is in the
  bore when every vertex its bounds reach is; a square plane face whose bounds reach no vertex fails. Run 2's own files read
  clean through it offline, and run 3's print is clean (3:129, 3:238).
- *built: a quiet Update values on Coupon_F2* (2:376, 3:347). In run 2 the check said none of its parts; `75d27cf` says each
  apart, nothing loosened. Run 3: one job, ok, *Nothing to update…*, no SolidWorks file moved, the .gear.json the same, and the
  part's **save flag False before, True after**. **App** (or SolidWorks): the plan's *a quiet Update values runs and changes
  nothing (no file, no .gear.json, no save flag)* does not hold. The likely cause, read from the code and not traced:
  `swbuild.update_variables` calls `Session.detect_trig_units` before it knows nothing changes, which adds the equation
  `"Gear Generator Trig Check"` and deletes it, and that marks the part. Nothing is written to disk. The same on 2024. For a
  ruling: it is pre-F3 code (any built part), not F3's.
- *built-f2: an allowance typed on G2 is structural* (2:961). **Script.** It required no changed part, but
  `workbook/update.py`'s `_part` lists a structurally changed part among the changed parts with its sentence beside it (read:
  `['Gear_m1.5_N68_P.SLDPRT']`). Fixed in `75d27cf` to G2's part being the one changed part; run 3 holds (3:401).
- *f3-reducer-machined: the four parts plan machined* (2:1574), and from it *built-machined* (2:2121, 2:2132). **Script.**
  W9a's `spec_reducer` keeps the fixture's blank Process, and a blank Process on a workbook with no record reads back Printed
  (F1, PLAN-PRINTED §2.8 item 5): the "machined" 12 : 1 was built printed. Fixed in `75d27cf` (Machined on its Box); run 3
  rebuilt it machined (3:479) and the guard-4 checks hold (3:1027, 3:1038).
- *userwork: Sun was built with no bore and holds the User Keyway* (2:3050). **Script.** The keyway was read before RangeBox
  was opened, and `features_of` reads an open part only. Fixed in `75d27cf`; run 3 reads code 0 (3:1066).
- *userwork: the in-place Update* (2:3496), and from it *Sun in place* (2:3498), *Sun's newest part* (2:3855), *keeps its
  allowance* (2:3857) and *the bore mate carried* (2:3858). **Script, by K2.** The user's concentric on Sun's bore face was made
  before the in-place Update of Sun's allowance and Flat, and the app refused that Update before any write, exactly as K2
  (ISSUE-1-PLAN, accepted by the user) rules for a user mate to a gear's own faces: *In modes H, N and L, UserBoreMate is a mate
  in RangeBox_r2.SLDASM that Gear Generator did not make, on Sun, which Update SolidWorks puts back, and a mate of that kind is
  not moved with its gear, so nothing is changed; in SolidWorks, lock your component to Sun instead, and Update SolidWorks puts
  it with Sun, or suppress UserBoreMate in H, N and L, and press Update SolidWorks again.* The four after it follow from the
  refusal (the last Build again… then kept 0.2 as built, the Flat 7.2 typed). Fixed in `75d27cf`: the bore mate is made after
  the in-place Update, on the D it leaves (radius 4.15). **For a ruling:** PLAN-PRINTED §2.8 says *a user's mate on an app
  gear's face is re-solved by those puts*; K2 and the app refuse instead.
- *userwork: the bore mate carried* (3:1892): remade none, *named ['UserBoreMate']*. **Script.** The check required the mate
  made again on SunGear; K5, as W9D-INTERFACES §4.4 rules it, names every face of an app part made new (`WHY_PART_NEW`) and
  never re-finds it. Fixed in `771f492` to that rule; not rerun on 2026 (the budget), but run 3's log bears it out (the app's
  sentence below, the eight other mates remade), and 2024 ran the fixed check clean.

**dshape** (1:11-395): DShape (m 1.5, z 20, face 8, Bore 8, a 0.2, Flat 7) built by the form, *Bore as cut* '8.2 · 8 + 0.2' and
*Flat as cut* '7.2 · 7 + 0.2' (1:13), its .gear.json at 4 (1:115). Each state read and judged (D, a, Flat; volume against its
twin from scratch; the round's radius and its box's x range; the chord link's Value; the flat's span against the chord):

| Step | D, a, F | Volume mm³ (twin) | R | Round's box x | Chord's Value = span |
|---|---|---|---|---|---|
| as built (1:119) | 8, 0.2, 7 | 4983.796 (4983.796) | 4.1 | −4.1 to 3.1 | 5.366563 |
| Flat 7 → 5 (1:126) | 8, 0.2, 5 | 5094.350 (5094.350) | 4.1 | −4.1 to 1.1 | 7.899367 |
| Flat 5 → 7.6 (1:133) | 8, 0.2, 7.6 | 4962.007 (4962.007) | 4.1 | −4.1 to 3.7 | 3.532704 |
| Flat 7.6 → 7 (1:138) | 8, 0.2, 7 | 4983.796 (twin 1) | 4.1 | −4.1 to 3.1 | 5.366563 |
| Bore 8 → 10, Flat 9 (1:145) | 10, 0.2, 9 | 4756.219 (4756.219) | 5.1 | −5.1 to 4.1 | 6.066300 |
| allowance 0.2 → 0.4 (1:152) | 10, 0.4, 9 | 4730.675 (4730.675) | 5.2 | −5.2 to 4.2 | 6.131884 |
| Flat 6.1, h = 0.25 R (1:159) | 10, 0.4, 6.1 | 4930.058 (4930.058) | 5.2 | −5.2 to 1.3 | 10.069757 |
| Flat 9.7, 0.3 deep (1:169) | 10, 0.4, 9.7 | 4702.889 (4702.889) | 5.2 | −5.2 to 4.9 | 3.481379 |
| back to 8, 0.2, 7 (1:177) | 8, 0.2, 7 | 4983.796 (twin 1) | 4.1 | −4.1 to 3.1 | 5.366563 |
| allowance −0.1, press fit (1:184) | 8, −0.1, 7 | 5013.557 (5013.557) | 3.95 | −3.95 to 2.95 | 5.253570 |
| DShape_Round (1:289) | 8, 0.2, round | 4954.394 (4954.394) | 4.1 | −4.1 to 4.1 | Bore@ 8.2 |
| DShape_D, round to D (1:393) | 8, 0.2, 7 | 4983.796 (twin 1) | 4.1 | −4.1 to 3.1 | 5.366563 |

- **No far-side solve, no sliver, nothing in error** in any state: the round one face of R about the axis reaching −X, one flat
  at h on +X by PlaneParams, the Bore Sketch fully defined (status 3), each volume equal to its twin's to the logged places.
- Each value step: the strip counted exactly the globals changed and Update values set those in one rebuild, the record
  following (1:122 to 1:180). The bound steps refused by the form in A's words, nothing sent: *The flat is 1.2 mm from the axis,
  under a quarter of the hole's radius (1.3 mm); type a Flat of at least 6.1 mm, or use a round bore.* (1:162) and *Your shaft's
  flat is 0.2 mm deep (Bore 10 less Flat 9.8), under the 0.3 mm a printed D needs to hold; …* (1:172). The structural steps in
  B's words, nothing sent: *A bore allowance cannot be added to or taken out of a built part through its values; build it again
  as a new part.* (1:187), *The drive changed from 'flat' to 'round'; …* (1:190), *The drive changed from 'round' to 'flat'; …*
  (1:290).
- **Facts the review asked for**: SolidWorks' own Value of each link agreed **in mm**, the radius's too (the self-check allowed m
  for it); `GetBox` on these faces is **tight** (padding beyond −R 0, the round's greatest x the flat's h exactly, the flat's
  span the chord to 1e-4), so W9b's 0.24 mm padding is not met on a part's bore faces; the tip lands number 20 with the two
  nearest +X at +8.983° and −8.982° against the half pitch 9°, none crossing +X: ruling 2's tooth space on +X, read.

**allowance** (2:11-44): 15 parts, each built clean, the hole as cut by its faces to 1e-4 mm and judged round: spur 5.1, 4.95
(a −0.1), 5.0 machined; helical 5.1, 5.15, 5.0; herringbone 5.1, 5.15, 5.0; bevel 5.1, 5.15, 5.0; hub 4.1, 4.125, 4.0 (2:14-42).
`"Bore Allowance"` as typed or 0.2 printed, no F3 global machined; schema 4 printed, 1 machined, each machined record F3-0's pin.

**print** (3:12-241): Print_D and Print_R each judged whole by F2's `written` (one new folder, the file and the list alone,
`{'SaveAs': 1}`, SolidWorks as it was), AP203, millimetres, 344 vertices to radius 16.501185 over 8.000031. From the STEP file:
the D one cylinder of 4.1 about Z, one plane face in the bore on x = h, its corners at x = h, the least vertex radius 4.1
(3:129); the round one cylinder, no plane (3:238). The list: *bore 8 mm + 0.2 mm allowance (8.2 mm as cut), D-flat 7 mm (7.2 mm
as cut)* and *bore 8 mm + 0.2 mm allowance (8.2 mm as cut)*, each *printed default* (3:130, 3:239).

**built** (3:246-1040): **nothing built before F3 moves.** Coupon_F2 at schema 3 with no F3 global (3:344); opened with the
switch on: count 0, *Bore as cut* '8', 0 allowance planned (3:346); the quiet Update values: the FAIL above; an allowance typed
refused in B's words (3:348). F2's printed 12 : 1: four .gear.json at 3 (3:369); the footer word for word as with the switch off
(3:375); a quiet Update writes nothing, marks nothing (3:387). **The structural refusal's sentence**: *Gear_m1.5_N68_P (G2): A
bore allowance cannot be added to or taken out of a built part through its values; build it again as a new part.*, the footer
offering Build again… (3:401); cleared, nothing planned (3:413). The 12 : 1 built with the switch on: every part 0.2 on record
(3:432); G2's 0.3 a value, one Update (12.1 s, `ForceRebuild3` 2) changing G2 alone, its hole 6.15 by its faces, 0.3 in
SolidWorks and on record, nothing saved (3:444-455). **K11**: 0.5 set by hand and saved, the press refused: *Bore Allowance in
Gear_m1.5_N68_P is 0.5 in SolidWorks and 0.3 in the workbook: type 0.5 in Gears!V3, or set it back to 0.3 in SolidWorks, and press
Update SolidWorks again.* (3:466-467). The machined 12 : 1 built before F3 (3:479-999), Printed typed: the four parts in place
(3:1027), one Update (25 s): Backlash 0.45, 0.45, 0.6, 0.6 → 0.3, no F3 global in SolidWorks or on record, each .gear.json at 3
(3:1038).

**hub** (2:2135-3026): RangeBox_Fixed printed, its Hub row D 8, a 0.2, Flat 7, read with no error (2:2147); built by the app's
Build, six parts, turning, every sketch fully defined, **no interference** (2:2998-3012); Hub Output's anchor with RangeSlv
splined to it (2:3013). **Turned through H, N and L**: every body at its frame on record (6.6e-10 at worst), no mate in error,
every gear free, RangeSlv at 55.5, 48 and 40.5 mm as on record, every mate's flag as on record, and **no interference read in
any mode** (2:3014-3021). The Hub's hole read as a D: R 4.1, the flat at h, links, Values, globals, the sketch status 3
(2:3023), schema 4 (2:3024).

**userwork** (3:1042-1895, at `75d27cf`): Sun with no bore and the User Keyway at code 0 (3:1066); Printed and one Update (208 s)
ok, the user's work as before (3:1101); Sun's bore and D structural, Sun alone: *Gear_m1.25_N29 (Sun): Drive changed from round to
flat, which its values cannot carry; build it again as a new part.*; Build again… (277 s) gave Sun a D read as dshape reads one
(the new Gear_m1.25_N29_P); the keyway cut again, a quiet press (107 s) recording it (3:1480); **Sun's allowance 0.3 and Flat 7.2 in
place by one Update** (166 s): ok, Sun read as D 8, a 0.3, F 7.2 (3:1517), the user's eight mates and keyway as before (3:1519);
the user's concentric made on the D's arc face, read by `mate_definition` as a face of radius 4.15, the arc one face, on in every
mode (3:1523), recorded by a quiet press (3:1535); then Part name SunGear, allowance cleared, Build again…: SunGear keeps 0.3 as
built (ruling 1, 3:1891). **The carry's reading of a D bore**: *UserBoreMate was on a face of Sun, and Sun's part is new because
its Part name changed, so it is not made again*; the eight other mates made again. W9d does not read a concentric's face on a part
made new (its walk reads a gear mate's only), so it says *a face of Sun*, not *Sun's bore*: `COAXIAL_FACE_READ` on a partial
cylinder is still unread live.

**Windows.** No What's Wrong. SolidWorks' notification box once, during FeatureExtrusion3 in the first 12 : 1 build of
`built` (2:465, exempt by ruling); otherwise progress boxes (*Opening*, *Loading…*, *Calculating Interference Detection*, the untitled
*Post load updating*).

## The confirming run on SolidWorks 2024 (2026-11-18, from 771f492, SolidWorks 2024 32.5.0)

**Setup.**
- Run folder `<probe folder>\f3-demo-sw2024-20261118-230231`, `snap` a `git archive` of `771f492` (log heads 1:3, 2:3).
  `--self-check` on it as on 2026: 17 ok, the pins check failing on Windows alone.
- Two sessions, each fresh, PIDs 3164 (`userwork,hub`) and 18504 (`dshape,allowance,print,built`), each exited after; the 2026
  session had exited first. Both with `--close-outlived-whats-wrong`; `userwork` and `hub` first, WSL idle but for a process
  check and a log grep every 15 s. The close path never acted. Master W9a's 2024 `setup.master`, only copied (the statements
  above).
- Logs `probe/results/sw2024/f3-demo-sw2024-20261118-1-userwork-hub-clean.log` (JSON `f3-demo-20261118-230436.json`) and
  `…-2-dshape-allowance-print-built-1-failed.log` (`…-234157.json`); below, `1:` and `2:` are these.
- SolidWorks time about 61 min (23:03 to 00:04).

| Section | Run | Time | ok | FAIL | STOP | SolidWorks private, peak logged | Free, least logged |
|---|---|---|---|---|---|---|---|
| userwork | 1 | 1880 s | 47 | 0 | 0 | 11.91 GB (4.41 at its end) | 8.67 GB |
| hub | 1 | 244 s | 23 | 0 | 0 | 7.05 GB | 9.42 GB |
| dshape | 2 | 312 s | 44 | 0 | 0 | 1.87 GB | 9.87 GB |
| allowance | 2 | 560 s | 15 | 0 | 0 | 2.82 GB | 10.18 GB |
| print | 2 | 39 s | 25 | 0 | 0 | 2.98 GB | 10.14 GB |
| built (three reducers built here) | 2 | 415 s | 94 | 1 (app) | 0 | 8.30 GB | 9.56 GB |

Run 1: 0 failed, 1 noted (the notification box), 0 STOPs (1:1766); run 2: 1 failed, 0 STOPs (2:2525).

**Every check reads as on 2026**, but the one FAIL, the same: *built: a quiet Update values on Coupon_F2*, the save flag False
before and True after (2:760). dshape every state clean (2:11-395), the same steps, the same refusals in the same words; allowance
the same holes (2:398-427); print the same bore from each STEP file and the same list lines (2:546-547, 2:655-656); built: schema 3
kept (2:757, 2:1313), the quiet Update writing nothing (2:1331), the structural sentence (2:1345), G2 in place to 6.15 (2:1934),
K11 with Gears!V3 (2:1946), the machined 12 : 1 planned machined (2:1958) and its Backlash written with no F3 global (2:2517);
hub turning in H, N and L with no interference (1:1754), the Hub's hole a D (1:1756); userwork through every step, the in-place
Update ok over the user's work (1:486-490), the bore mate on the 4.15 face (1:494), and **the carry check at `771f492` holding**:
UserBoreMate named `part new` for the Part name, its subjects `('Sun', 'its Part name changed', 'face', '')`, the eight remade
(1:863-864).

**Windows.** No What's Wrong box anywhere (none expected: nothing of the user's was left in error). The notification box once,
during `GetNextFeature` (1:473-474, exempt); progress boxes otherwise.

## What differs between the versions

Every check reads the same on both. Measured differences, none judged a fault:
- **Volumes**: each dshape state's volume on 2024 is 0.186 mm³ over 2026's (4983.982 against 4983.796 as built), each twin the
  same on its own version, so every state is its twin's on both. Sun's D part 9382.060 against 9381.261.
- **The tip lands**: the two nearest +X at ±9.000° on 2024, +8.983° and −8.982° on 2026.
- **The STEP files**: 346 vertices to radius 16.500000 over 8.000009 on 2024, 344 to 16.501185 over 8.000031 on 2026 (F2 measured
  the same); the faces 175 with 43 planes (D) and 42 (round) on both.
- **The hub's build sense**: 2026 made *Planet copy 1 meshes Ring* again with the other Flip; 2024 RangeSlv's spline and its two
  dog mates (each by its version's route, nothing left turned round).
- **Time and memory**: userwork 1213 s on 2026, 1880 s on 2024 (RangeBox's Printed Update 208 s and 348 s, the in-place Update
  166 s and 360 s); SolidWorks 2024's private memory peaked at 11.91 GB in userwork and 8.30 GB in built, against 2.40 GB on
  2026. Free memory never under 8.3 GB, so neither floor came near.
- What's Wrong: `whats_wrong_shows_in_update` True on 2024, False on 2026; no box came on either.

**Not measured by these runs**, beyond *What the script does not measure*: the carry's `COAXIAL_FACE_READ` on a D's partial
cylinder (W9d reads a face's axis on a part made new for a gear mate only); an Update over a user's mate on a D bore face (K2
refuses it, shown on 2026 run 2 only); `userwork` at `771f492` on 2026 (run 3 was at `75d27cf`); a What's Wrong that outlives
its job, and either memory floor's STOP.

**Script changes for these runs**: `75d27cf` (the STEP reader's planes in the bore by their vertices; built's machined 12 : 1
said Machined; the structural refusal's changed part; the quiet Update values' conjuncts said apart; userwork's keyway read after
the open and its bore mate made after the in-place Update) and `771f492` (the bore mate named, by K5). Self-check after each: 18
checks, 0 failed (Linux).
