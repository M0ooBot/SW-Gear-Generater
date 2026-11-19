# F3's demonstration on SolidWorks: the sections, the masters, the commands, the STOPs

The script is `probe/f3_demonstration.py`. It is the SolidWorks part of PLAN-PRINTED §4.6's *Done when* for stage F3 (the bore
allowance and the D-flat): every section clean on SolidWorks 2026, and on 2024 as the confirming build. It was written on
Linux against branch `printed` with packages A, B and C in, and every sentence it expects is held to the app's own code at
`fd7da8c`: after F3-REVIEW's fixes (B `60e58b5`, C `2edbe17`, `5a72057`, `4812df9`) and the switch's commit (`262c0f7`, which
turned `spur.PRINTED_DEFAULT_IN_PLANS` on while this was being written). Its self-check passes there (**15 checks, 0
failed**, Tk present, the switch on). **It has not run on SolidWorks.** It is written for the switch on (below). Expect script faults on its first live run, as every demonstration had.

**How it works.** It runs W9a's `main` with its own five sections, as F1's and F2's scripts do, and changes no other script.
It imports F2's live part (`import f2_demonstration as F2`), which brings W9a's harness with it: the attach by `--pid` and its
check, the dialog watch with the What's Wrong rule per version, keep-awake, the JSON after every section, APPDATA in
`<out>\appdata`, the guarded close, `--sections` and `--redo`, Desk9 and its `press` (Update SolidWorks), `keyway`, `save_user`,
`copy_desk` and `users_in_copy`; and F2's own: the strip's real `gui.GearApp` (its link not started; `make_form`), the
presses' `Strand`, `activate`, `features_of`, `press_form`, `written` (a Print files press judged whole) and `patched`.
`--close-outlived-whats-wrong` is W9c's own close path, put in only when the flag is given. Build again… in `userwork` is
W9d's `DeskD` (the window's `_start_build` with `old_assembly` as `before` and `carry_for` as `carry`), by `w9d_demonstration.copy_desk`.

The self-check cannot import F2's live part (W9a's harness parses the run's arguments at import). It reads F2's pure
part instead, everything above F2's `if SELF_CHECK:` line, executed into a module of its own (`_f2_head`): F2's STEP
statement splitter and vertex reader, `patched`, `make_form`, `shown_rows`, `Strand` and its fixture names. F2's file is
not changed. A reviewer may prefer these restated; the cost is about 300 lines kept in step by hand.

**The switch.** `spur.PRINTED_DEFAULT_IN_PLANS` (F3-INTERFACES §13) is read from the module at call time. The log's first
line says what it reads, and every section says it again. `allowance`, `print` and `built` judge the printed default, and
each ends at its start with a sentence (a section STOP, not the run's) when the switch is off. `dshape` and `userwork` judge
typed and as-built figures only and run either way. Where `built` needs what F2's code built, it builds it in the run
with the switch set False in this process only, says so in the log (`switch` and `patch` lines), and puts it back.

## Where this departs from the plan and the brief (for the coordinator's ruling)

1. **The sections are the coordinator's brief's five**, not PLAN-PRINTED §4.6's (`dshape`, `bore`, `kinds`, `update`, `workbook`).
   What the plan names and where it is: `bore` is `allowance` and `print`; `kinds`' helical and bevel are in `allowance`;
   `update`'s two refusals are `dshape`'s structural steps and `built`'s G4; the plan's setup.master with Printed is `userwork`.
   **Not here:** a herringbone with an allowance; the bevel's D-flat refusal on SolidWorks (A's diagnostic, made before any
   SolidWorks call and held by A's tests); and the plan's RangeBox_Fixed hub gearbox built with an allowance and
   a D, turned through every mode with no interference read. The Done-when's "the hub gearbox turning with no
   interference" is therefore not shown by this script.
2. **built: an allowance typed on a part built before F3 cannot change its bore in place.** Such a part has no
   `"Bore Allowance"` global, so none to some is structural (G4, §4.4): Update refuses it and Build again… makes the part
   new. The script shows exactly that on F2's 12 : 1 (the footer offering Build again…, the one structural sentence naming
   G2's part alone, nothing written), and shows the in-place change and K11 on the printed 12 : 1 built with the switch on,
   whose parts hold the global.
3. **userwork: setup.master's Sun has no bore** (RangeBox's rows leave Bore blank; Sun holds `"Bore Diameter" = 0`), so it
   has no bore to take an allowance or a D, and no bore face for a mate. Typing Bore, an allowance and a D for Sun is
   structural, so the first press is Build again…, which gives Sun its D. The user's work is then put on the new Sun (the
   keyway cut again, a concentric of Sprocket-4's bore on Sun's D arc face, recorded by a quiet press), Sun's allowance and
   Flat are changed in place by one Update with the user's feature and mates read before and after, and a last Build again…
   (Sun's Part name changed, its allowance cleared) shows the as-built allowance kept and the bore-face mate carried.
4. **dshape's "from round to D and back"**: Drive is structural (§4.2), so Update values refuses each way in B's words
   and the form's Build makes each new (a round part from the D's record, then a D from the round's).
5. **The hub** is not a strip kind: it is built by the app's `plan_for` and `swbuild.build` (the strip's own job) and its
   `.gear.json` written by the form's own `_write_sidecar`, as every part of `allowance` is, rather than through a gearbox.

## The masters each section needs

- `dshape`, `allowance`, `print`: none. Each builds into a fresh folder of `<out>`.
- `built`: none given. It builds the printed 12 : 1 (W9's fixture with Printed on its Box) twice through the app's own
  Build (W8's `write_fixture` and `build_turning`, about 1.5 min each): with the switch off as `f3-reducer-off.master` and with
  it on as `f3-reducer-on.master`, each kept in `<out>` and reused by a rerun there; `--reducer-off-master` and
  `--reducer-on-master` give ones an earlier run of the same SolidWorks version kept. (F2's own `f2-reducer.master` is not
  taken: its workbook has no Bore allowance column, and F3's switch-off build is F2's code by F3-0's pins.)
- `userwork`: **`--user-master` is required**, W9a's `setup.master` for the version run, only copied:
  - SolidWorks 2026: `<probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master`
  - SolidWorks 2024: `<probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master`
  - The 2026 master does not open in 2024. `<probe folder>` is `C:\Users\M0obo\Documents\GearGeneratorProbe` on this laptop.

## Sections

Times are estimates from the measured steps of W9a's, F1's and F2's runs (a part 15 to 25 s, the 12 : 1 built about
1.5 min, a value Update on the 12 : 1 about 25 s, RangeBox's first Update 2.7 min on 2026 and 5 on 2024). F2's sections ran
in about a third of their estimates, so these are generous.

| Section | What it does | 2026 | 2024 |
|---|---|---|---|
| `dshape` | The D built by the form; 13 steps of Update values (9 written, 2 past a bound, 2 structural); D to round and back by Build; 9 twins built from scratch; every state read. | 6 min | 9 min |
| `allowance` | 12 parts (4 kinds × default, typed, machined), each built, read and closed. | 5 min | 8 min |
| `print` | 2 parts built by the form and pressed; each STEP file read. | 2 min | 3 min |
| `built` | The coupon by F2's code and its strip reads; the 12 : 1 built twice; a quiet Update, a typed allowance, an in-place Update and K11's press. | 9 min | 13 min |
| `userwork` | RangeBox copied; Printed and one Update; two Build again…; a quiet press; one in-place Update; the user's keyway and bore mate. | 15 min | 28 min |

About 37 minutes on 2026 and 61 on 2024 (the plan's 25 and 40; `userwork`'s two RangeBox Build again… are most of the
difference). Expect about a third of that.

### dshape: what each line bears out

A printed spur, m 1.5, z 20, face 8, Bore 8, allowance 0.2 typed, Drive flat, Flat 7 (§4.6's), named DShape, built by
the strip's form and left active; its record open in the strip.

- **The form** shows *Bore as cut* 8.2 · 8 + 0.2 and *Flat as cut* 7.2 · 7 + 0.2; the .gear.json is at schema 4.
- **Each state, read by** `part_read` (the part not activated: `use_open_document`) and judged by `judge_hole`:
  - nothing in error; the Bore Sketch `GetConstrainedStatus` 3;
  - **the bore by its faces** (`bore_judged`): exactly one cylinder about the axis (CylinderParams: axis along Z through the
    origin) of radius R = (D + a)/2 to 1e-4 mm; exactly one plane square to the end faces within the bore, its normal along
    X, its plane at x = h (PlaneParams' point) to 1e-4 mm, on +X; its extent along Y the chord (to 0.2 mm, GetBox being
    padded); the round's box reaching −X and not past the flat. The sliver (the 81.76° minor arc) fails the last two;
  - **a tooth space faces the flat** (`lands_judged`, ruling 2): the tip lands (cylinders about the axis at d_a / 2) number
    20, none crosses +X, the two nearest it have their box centres at ±9° (to 1°);
  - **the links as SolidWorks holds them** (`link_judged`): `"Flat@Bore Sketch"`'s expression, spaces aside, is the app's
    `chord_expression` text (`2 * ( ( abs ( … ) ) ^ 0.5 )`), holds no `sqr`, and evaluated by the app's evaluator on the
    values SolidWorks holds gives the chord worked here to 1e-6 mm; `"Bore@Bore Sketch"` evaluates to R (a round's to D + a).
    The Equation Manager's own Value of each link is logged as a fact (its unit is not judged);
  - the F3 globals: `"Bore Allowance"` the allowance, `"Bore Flat"` the Flat;
  - **the volume within 0.1 % of its twin**: the same spec built from scratch by the app's plan and build in a folder of its
    own, read, closed unsaved (once per spec).
- **Each value step** (Flat 7 → 5 → 7.6 → 7; Bore 8 → 10 with Flat 9; allowance 0.2 → 0.4; Flat 6.1, h at 0.25 R exactly;
  Flat 9.7, the flat 0.3 deep exactly; back to 8, 7, 0.2; allowance −0.1, a press fit): the strip counts exactly the globals
  the step changes, Update values sets those and no other in one rebuild with no landing route, and the record follows.
- **Each bound step** (Flat 6 at D 10 a 0.4, h 1.2 under 1.3; Flat 9.8, 0.2 deep): A's sentence at Flat on the form (the
  script's copy held to `bore_checks` in the self-check), Update values says *The gear on the form does not work out yet, so
  nothing was updated.*, nothing sent, the part's globals and its .gear.json as they were.
- **Each structural step** (the allowance −0.1 → 0; Drive flat → round): B's sentence exactly, nothing sent, nothing
  changed.
- **D to round and back**: a round part (DShape_Round, a 0.2) built by the form from the D's record; judged as above (one
  cylinder, no flat); Drive flat on it refused in B's words; a D (DShape_D) built from it, judged against the first twin.

A far-side solve shows as a flat at −h, a round that does not reach −X, a chord off, or a volume off its twin; per the plan
it is the run's finding, with one follow-up round.

### allowance: what each line bears out

For each of F3-0's pinned machined gears that a bore reaches and the strip or a hub row builds (tests/test_printed_rule.py's
`spur` m 1.5 z 25 Bore 10, `helical` β 20°, `bevel` 20 on 40, `hub` m 1.25 z 17 face 20 Bore 8), three parts in folders of
their own: printed with the allowance blank (the default, 0.2), printed with one typed (spur −0.1, helical 0.3, bevel 0.3,
hub 0.25), and machined.

- the part built clean (nothing in error);
- **the hole as cut**: the smallest cylinder about the axis, by CylinderParams, at (Bore + a)/2 to 1e-4 mm (a bevel's is its
  revolved blank's inner edge);
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
- **the bore from the STEP file itself** (`step_bore_judged`, ADVANCED_FACEs read here apart from printout's reader): one
  CYLINDRICAL_SURFACE about Z of radius (D + a)/2 to 0.01 mm; on the D exactly one PLANE square to the end faces within the
  bore, its normal along X and its location on x = h; on the round none; the least VERTEX_POINT radius (D + a)/2; on the D at
  least two vertices of that radius at x = h (the flat's corners);
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
- **The printed 12 : 1 by F3's code** (`f3-reducer-on.master`): every part holds `"Bore Allowance" 0.2` on record; G2's allowance typed
  0.3 is a value, Update changing G2's part alone; one Update: the result changes G2 alone, G2's hole by its faces (12 +
  0.3)/2 to 1e-4 mm, the global 0.3 in SolidWorks and on record, the other three parts' globals as they were, no file saved.
  **K11**: `"Bore Allowance"` set 0.5 by hand in G2's part, the assembly rebuilt and saved as the person would (W9a's `refuse`
  bore step), pressed again: refused (`UserWorkRefused`) naming `"Bore Allowance"` with its cell `Gears!V…` and the live 0.5, G2's
  globals as they were after.

### userwork: what each line bears out

On a copy of setup.master (W9a's RangeBox with Sprocket-1..4, Housing-1, eight user mates, the User Keyway in Sun's part):

- Sun read on record as built with no bore, its keyway in no error; every mate's code and state read (`mate_states`).
- **Printed** typed on the Box sheet (F1's and F2's way); Update plans the five parts in place; one Update ends ok with
  nothing of the user's in error; saved as the person saves; every mate and the keyway as before.
- **Sun given Bore 8, allowance 0.2, Drive flat, Flat 7** (the three columns inserted before Part name and headed as the app
  heads them, said, where the workbook lacks them): one structural sentence, Sun's alone; **Build again…** as the window
  runs it (W9d's DeskD, the carry); the carry's lines logged, run to its end with no user file changed; Sun's new part read
  as dshape reads a D (no twin), its .gear.json at 4; saved.
- **The user's work on the new Sun**: W9a's keyway cut again; a concentric of Sprocket-4's bore (radius 5) on Sun's D arc face
  (radius 4.1), by AddMate5 on the two faces as W9d's fixture made its face mates, on in every mode, in no error; saved; a
  quiet press changes nothing and records the mate and the keyway in the inventory.
- **Sun's allowance 0.3 and Flat 7.2, one Update**: Sun's part alone in place; the Update ends ok, nothing of the user's in
  error; Sun read as a D at R 4.15, h 3.35; every mate's code and state as before (the bore mate among them, every user
  mate in no error), the keyway in no error; saved.
- **Sun's allowance cleared and its Part name SunGear, Build again…**: SunGear keeps `"Bore Allowance" 0.3` (ruling 1, the cell
  blank on record) and is read as the same D; **the mate on Sun's bore face is carried** (in the carry's `remade`, not `named`;
  made again in no error), as W9d's "bore" says of a coaxial cylinder of the hole as cut, here a D's partial cylinder; the
  user's components in the new revision.

## SolidWorks calls

**None new to the repo.** Each is the app's, or an earlier script's:

- builds: the strip's `swbuild.build` through the form (F1's and F2's demonstrations) and from a plan (W9c's `landing` twins);
  the 12 : 1's `build_gearbox` (W8, F2); Build again… with the carry (W9d's DeskD);
- the strip's Update values, `swbuild.update_variables` (F2's `refusals`); the window's Update, `update_gearbox` (W9a's `press`);
- reads: `GetBodies2`, `GetFaces`, `GetSurface`, `IsCylinder`, `CylinderParams`, `IsPlane`, `PlaneParams`, `GetBox` (W9b's `part`
  section's `part_faces`); `feature_states`, `sketch_status`, `volume_mm3`, the Equation Manager's `Equation` and `Value` (the
  app's build check; W9c's landing); `mate_states` (W8, W9a); `GetSaveFlag` by the walk (F2);
- the person's steps: `set_global_variable` and `rebuild` on a part in an assembly, then the assembly's rebuild and W9a's
  `save_user` (W9a's `refuse`); W9a's keyway; AddMate5 on two faces carried into the assembly by `GetCorresponding` and
  `Select4` (W9c's probes' `raw_mate` and `select_face`, as W9d's fixture); Excel's edits (W8) and `Columns(n).Insert` (W9c's
  `ensure_headers`); Print files (F2).

**New in kind, not in call** (the reviewer's to weigh): every read and Update above on a part whose bore is a D (a major
arc and its chord; package B's table lists each call the D's build and Update make and where the app already makes it);
AddMate5's concentric on a partial cylinder (W9d's were on full ones); the carry's "bore" on a partial cylinder
(`COAXIAL_FACE_READ` was verified on full cylinders only, W9D-INTERFACES §4.4: this run is its first live reading); and a
RangeBox Build again… that gives a part a bore.

## STOPs

As W9a's, which end the run: any window during a job under the version's What's Wrong rule (with
`--close-outlived-whats-wrong` on 2024, W9c's close path); under 2 GB free before a section; a hung worker or a lost
session. These end their section only: the switch off in `allowance`, `print` and `built`; the F2 findings not the reviewed
ones (`print`); under 6 GB free before `userwork`'s copy, its first Update or either Build again…. A script fault fails its
section with the traceback's tail. No What's Wrong is expected: nothing here rebuilds a feature of the user's into error.

## Without SolidWorks

`PYTHONPATH=src python probe/f3_demonstration.py --self-check`: **15 checks, 0 failed** at `fd7da8c` (Tk present, the switch on). Each judgement the
live sections make is a plain function, held on the app's own figures and failed each way it can fail:

- **the names**: the switch exists; the bounds 0.25 R and 0.3 mm, the default 0.2, the Bore Sketch, the three globals and
  the Gears titles are the app's;
- **§4.2 worked here**: R, h, the chord, the sweep and the bounds' Flats hold the plan's six rows and agree with A's
  `d_flat` on every dshape state;
- **dshape offline**: every value step plans exactly its own globals and is no structural change; the two bound steps are A's
  error at Flat in the script's words; the two structural steps, and D to round and round to D, are B's sentences;
- **the links**: the app's chord and radius texts evaluate to the figures here on every dshape state; `sqr`, a chord 0.01
  off, none, two and another text each fail;
- **the faces**: the D and a round hold; a D read as round, no cylinder, the sliver, the flat on −X, two flats, the radius
  2e-4 over, the flat 2e-4 off, a round where a D is wanted and a short chord each fail; the tooth space on +X holds and a
  tooth on +X, a land missing and the teeth turned 3° each fail; the volume's 0.1 %;
- **the STEP reader** on made-up files: the D and a round hold; a D read as round, the plane on −X, two planes, the radius
  0.02 over, the vertices 0.02 out each fail;
- **the words**: Bore as cut and Flat as cut, the list's bore line (a D typed, a round at the default, a press fit, a part
  built before F3), Update values' refusal of a form that does not work out, each the app's;
- **allowance offline**: each kind's hole as cut, global and schema, printed (switch on) and machined; the default planning 0
  with the switch off;
- **F3-0's pins**: the four machined gears are `test_printed_rule.py`'s `GEARS`, their plans and .gear.json hold `STRIP` and
  `SIDECARS` (pytest stood in where it is not installed, for the module's decorators only);
- **the live part as source**: each of the 96 names it takes from W9a's, W8's, F2's, W9c's, W9d's and W9c's probes' scripts is
  defined there, and every Session member it calls is `swcom.Session`'s;
- **the strip's own form** (Tk): the D on the form, its rows, its record at 4; every dshape step through the form's own
  Update values with a job answered here (each value step counting and sending exactly its globals, the record following;
  each bound and structural step refused in its words, nothing sent); the round part's record and Drive flat on it refused.

## What the script does not measure

- The hub gearbox (RangeBox_Fixed with a Hub row bored, an allowance and a D) built and turned through every mode with no
  interference (the plan's `workbook`); a herringbone with an allowance; a D on a helical gear (its flat's angle at the section
  plane, F3-INTERFACES §3, unverified and unread: nothing here reads a helical's flat).
- The bevel's D-flat refusal and a ring's or sleeve's bore fields refused on SolidWorks: diagnostics before any call, held
  by A's tests.
- The Equation Manager's own Value for a link (logged; its unit not judged) and the D's sketch's arc sweep as SolidWorks
  holds it (the faces and the volume stand for it).
- A D bore printed and fitted on a shaft; the allowance's figure from the user's coupons (V1).
- W9d's carry of a bore mate on a part made new **by** its allowance or drive (K5's ruling: named, not found again); the
  carry here is of a part made new for its Part name, the bore as built.
- The window's own warnings (C's `_assess` wiring) on SolidWorks: the window's checks are pure.

## What must be open or closed

- **SolidWorks**: a session started for the run, alone, its PID given; nothing of the user's open with a file name the run
  uses (`DShape*`, `Twin*`, `Gear_m1.5_N25*`, `Helical_*`, `Bevel_*`, `Hub_*`, `Print_D`, `Print_R`, `Coupon_F2`, `Gear_m1.5_N17_P`,
  `Gear_m1.5_N68_P`, `Gear_m2_N17_P`, `OutputGear`, `Reducer_12to1`, `RangeBox*`, `Gear_m1.25_*`, `SunGear`, `Ring_m1.25_N55`, `Dog_m1.25_N17`,
  `Sleeve_m1.25_N17`, `Sprocket`, `Housing`).
- **Excel**: the script starts and quits its own; no `Reducer_12to1.xlsx` or `RangeBox.xlsx` open in the user's.
- **The laptop**: on mains power, the lid open; over 6 GB free for `userwork`; WSL idle during the 2024 `userwork`.
- **Tk**: every section but `userwork` opens a hidden Tk window in the script's own process.

## Command lines

Make a `git archive` of the commit to run (at or after the switch's commit, `262c0f7`) into `RUN\snap` with `SNAPSHOT_COMMIT` beside `src`,
run `--self-check` on the snapshot first, start SolidWorks for the run and give its PID. One `RUN\out` per version; each
invocation its own log.

```
rem SolidWorks 2026: all five in one invocation, dshape first (about 37 min estimated)
python.exe RUN\snap\probe\f3_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\f3-demo-sw2026-1.log ^
    --sections dshape,allowance,print,built,userwork ^
    --user-master <probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master

rem SolidWorks 2024, the confirming build: userwork first, in a fresh session, WSL idle (about 28 min)
python.exe RUN24\snap\probe\f3_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f3-demo-sw2024-1.log ^
    --sections userwork --close-outlived-whats-wrong ^
    --user-master <probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master

rem then the rest, in a second fresh session (about 33 min)
python.exe RUN24\snap\probe\f3_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f3-demo-sw2024-2.log ^
    --sections dshape,allowance,print,built --close-outlived-whats-wrong
```

**The order on 2024, for memory**: `userwork` first in its own fresh session (RangeBox's Updates and two Build again… grow
SolidWorks 2024 by several GB; F1 measured 3.1 to 7.0 GB over two RangeBox presses), then the four others in a second fresh
session, `dshape` first. On 2026 `userwork` runs last; if the 6 GB floor ends it on a grown session, rerun it alone in a fresh
one. `--close-outlived-whats-wrong` is in force on 2024 only.

**Re-running.** A section `RUN\out` already holds is skipped and said; `--redo` sets its folders aside (`<name>.prev-<time>`) and
runs it again. The two `f3-reducer-*.master` folders are not a section's and are kept.

The JSON (`f3-demo-<time>.json`) is written beside the log after every section: the switch as read; dshape's every state
(its faces summed up, its links and their Values, its globals, its volume, what did not hold) and the twins' count;
allowance's hole, schema and problems per part; print's press folders; built's K11 sentences; userwork's carry lines.

## For the reviewer

Look hardest at:

1. **dshape's judgement of the D by its faces** (`bore_judged`): whether one cylinder and one flat at x = h, the round's box
   reaching −X, is enough to tell the 278° D from any far-side solve, and whether SolidWorks may split the D's arc into two
   faces (it would FAIL here, falsely).
2. **The tooth-space read** (`lands_judged`): it assumes each tooth's tip land is its own cylinder about the axis at d_a / 2, as
   the blank's outer cylinder left between spaces; if SolidWorks merges or splits them the count fails.
3. **The departures above**, chiefly that `built`'s in-place change and K11 are on a 12 : 1 built with the switch on, and that
   `userwork` gives Sun its D by Build again… first; and what is not here (the hub gearbox turning).
4. **userwork's bore mate** carried as "bore" on a partial cylinder: the first live reading of that contract.
5. **The self-check's reading of F2's pure part by `exec`** rather than restating it.
