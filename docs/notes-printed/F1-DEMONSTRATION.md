# F1's demonstration on SolidWorks: the sections, the masters, the commands, the STOPs

The script is `probe/f1_demonstration.py`. It is the SolidWorks part of PLAN-PRINTED §2.8's *Done when*, which the F1
review (`F1-REVIEW.md` §1, §8) left to do: on SolidWorks 2026, and then on 2024 as the confirming build, one printed
spur gear built, one printed pair built, and Printed typed on the Box sheet of a copy of W9a's `setup.master` with
one Update SolidWorks. **It has not run on SolidWorks.** It was written on Linux against the app at `e0a8d62` on
branch `printed`; its self-check passes there (51 checks, 0 failed), and its rangebox planning was rehearsed offline
on scratch copies of both masters (below). Expect script faults on its first live run, as every demonstration had.

**How it works.** It runs W9a's `main` with its own three sections, as W9b's and W9c's scripts do, and changes no
other script. From W9a's harness: the attach by `--pid` and its check, the dialog watch with the What's Wrong rule
per version, keep-awake, the JSON after every section, APPDATA in `<out>\appdata` (the run refuses to start
otherwise), the guarded close, `--sections` and `--redo`, Desk9 (the Workbook window's own planning and finish),
`press`, `ahead_of` and W9a's reads of the user's work. `--close-outlived-whats-wrong` is W9c's own close path
(`w9c_demonstration.close_outlived_on`), put in only when the flag is given; importing W9c's script for it also adds
`AddComponent5` to W8's traced writes, as W9c's runs have it.

Two things are its own, both said in the log:

- **The strip's form is the app's own.** The spur and pair sections make the real `gui.GearApp` in a hidden Tk root,
  with `GearApp._start_link` replaced by a no-op for the run (its own worker would attach to the newest SolidWorks, a
  second driver). The script sets the form's variables as a person does (Process, Module, Gear pair, Motion), and the
  form's own `_derive_now`, `_gear_spec` / `_pair_spec`, `_plan_single` / `_plan_pair` and `_finish_single` /
  `_finish_pair` do the rest. Only `_build_gear`'s two lines are restated: the context's job is run on this run's
  worker, and the existing-file check is a check here. The Recent list the form writes goes into the run's APPDATA.
- **The Desk reads a blank Process as the window does.** The rangebox section reads the workbook through W9a's
  Desk9. Its W8 Desk resolves a blank Process by the Workbook window's own `_blank_process` since `e3705a1`. See
  *Found while writing it*.

The tooth and the turn are measured by the scripts that already measure them, imported and not changed:
small_pinion_check's `readings`, `expected_volume` and `judge_part` (its `say` and `check` rebound to this run's,
so its lines and failures land in this log), and gear_pairs_check's `drive`.

## The masters each section needs

- `spur` and `pair`: none. Each builds into a fresh folder of `<out>`.
- `rangebox`: **`--user-master` is required.** It is W9a's `setup.master` for the version run: RangeBox with the
  user's work (four sprockets and a housing, eight user mates, the User Keyway in Sun's part), built by an app before
  F1. The script does not build one. It reads the master's own record from its file (nothing written) and stops the
  section if the record is at link 11 or later, or any part's spec says a process.
  - SolidWorks 2026: `<probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master`
  - SolidWorks 2024: `<probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master`
  - Both were read from WSL on 2026-11-18, read-only: each record is at link schema 7, no part says a process, the
    workbook has no Process row (Units is the last Box row, row 9), and `blank_process` of the record is machined.
  - The 2026 master does not open in 2024.

`<probe folder>` is `C:\Users\M0obo\Documents\GearGeneratorProbe` on this laptop.

## Sections

Times are estimates, from W9a's, W9b's and the gear scripts' measured steps (a part about 15 to 25 s, a pair about
40 s on both versions, W9a's go press 3 min on 2026 and 6 on 2024, a quiet press 1.5 and 3).

| Section | What it does | 2026 | 2024 |
|---|---|---|---|
| `spur` | The form as it opens (Printed, Gear_m1.5_N25_P), then Machined (Gear_m1.5_N25), then both at module 0.8 (Gear_m0.8_N25_P, Gear_m0.8_N25): four parts built by the form, each read back. | 3 min | 5 min |
| `pair` | The form's pair, 25 / 50 at module 1.5 with Motion gear mate, Printed then Machined: two pairs built by the form, each driven and read back. | 4 min | 6 min |
| `rangebox` | A copy of `setup.master` opened as built; Printed typed; one Update; the reads; saved, closed, a second Update. | 15 min | 30 min |

### `spur`: what each line bears out

For each of the four parts:

- **The name.** The form names the printed part with _P and the machined one without, and the file is new.
- **The Backlash global.** `Session.equations` reads one `"Backlash"` equation. Its text, spaces aside, is
  `IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )` printed or `0.3 * "Module"` machined. SolidWorks' value is the
  plan's figure, worked in the script and not taken from the app: 0.3 at module 1.5 printed, 0.45 machined, 0.24 at
  module 0.8 either way. The app's derived figure must be the same.
- **The tooth.** By small_pinion_check's own checks: no feature in error, one solid body, the volume within 0.1 % of
  the app's outline less the bore, times the face, and the tip corners (four a tooth) on the outer radius.
- **The `.gear.json` the form's finish wrote.** Printed: sidecar 3, the spec's `process` printed, the derived nozzle
  0.4, the IIF. Machined: as W9 records a machined part. That is sidecar 1, the spec's keys exactly W9's eighteen (no
  `process`, `nozzle` or bands), no nozzle in `derived`, and `0.3 * "Module"`.

Then across the four:

- **At module 1.5 the two teeth are told apart by their volume.** The app's outlines are 9842.33 and 9717.03 mm³, 1.29 %
  apart. Each part's volume must be within 0.1 % of its own outline and not within 0.1 % of the other's.
- **At module 0.8 the two parts are one solid.** Their volumes agree to 1e-6, since the two backlashes are one value
  there. Only the equation's text tells them apart, and the Backlash line reads it.

### `pair`: what each line bears out

For the printed pair and the machined pair alike:

- **The names.** Pinion_m1.5_N25_P, Gear_m1.5_N50_P and Pair_m1.5_25T_50T_P printed; the same without _P machined.
- **It builds.** The form's `_plan_pair` (`pair.assembly_plan`, motion gear mate) and `swbuild.build_pair`; the
  assembly ok.
- **It turns.** gear_pairs_check's `drive`: an angle mate from gear A's Top plane on a global, driven 10° then 40°.
  Gear A must turn 30°, and gear B −0.5 of it to 1e-6, with no interference at 10° or at 40°, and gear A not fixed.
  The printed pair passing the same judgement as the machined pair is "turning as a machined pair does".
- **Each part's Backlash and `.gear.json`**, as in spur (the form's finish writes both sidecars, with partner and
  assembly).

**The backlash in the mesh is not measured.** No script measures it in SolidWorks, so none is reused. What is read is
each part's Backlash global and the interference at two angles.

### `rangebox`: what each line bears out

**Opened as built (D11 (B)).**

- The copy reads as built from its workbook, its assembly in the copy.
- **The Process.** The workbook has no Process row, and the blank resolves machined. All six gears plan machined, none
  named _P. Update has nothing to do: no refusal, structural change, missing file, re-place, moved shaft or changed
  part, and `record_matches`.
- **The footer** begins *SolidWorks already matches the workbook on record*, W9's words for this state
  (`w9a-final-sw2026-20261117.log:241`). It says none of *Process*, *printed*, *Printed* or *_P*.
- **The Workbook panel's Process line** is *Machined, as built: type Printed beside Process on the Box sheet to print
  it (add a row labelled Process)*.
- **Nothing is written by the open.** Every `.xlsx`, `.json`, `.SLDPRT` and `.SLDASM` of the copy has the same size,
  time and sha256 before the Desk reads and after its planning (Excel's lock file aside).

**The user's work, before.** W9a's go reads it: the user's components in the copy (`users_in_copy`) and the inventory
on record. Every mode is shown and read (`read_every`): the eight user mates on as set up, Sprocket-4's distance, and
`go_judge` as copied. Then every user mate's entities (`entities_of`) and the User Keyway's code in Sun's part.

**Printed typed.** In this run's Excel, the person adds a row labelled Process at the Box sheet's first empty row
(row 10 on both masters) with Printed beside it, saves, and the window's poll reads it. If a row labelled Process
exists, Printed is typed beside it instead.

- The Box reads `printed` at `Box!B10`, resolved printed, with no error. The Process line reads *Printed, 0.4 mm
  nozzle*.
- **Classify** plans one Update in place, with no structural change, new revision or in-place change. Each of the five
  parts changes and keeps its file name, and its planned globals differ from those on record in `Backlash` alone,
  from `0.3 * "Module"` to the IIF.
- **The footer before the press** begins with B's sentence: *Update SolidWorks will change the values in
  Gear_m1.25_N29 (Sun), Gear_m1.25_N13 (Planet), Ring_m1.25_N55 (Ring), Dog_m1.25_N17 (HighDog, LowDog) and
  Sleeve_m1.25_N17 (RangeSlv).* It foresees no problem of the user's, and what it foresees carrying is kept.

**One Update SolidWorks**, by W9a's `press` (the footer must offer it). The section stops first if under 6 GB is free
(*STOPs*).

- **What it wrote.** The result is ok with no failure. Each of the five parts' own `UpdateResult.changed` is
  `['Backlash']`, and the layout and carrier changed nothing.
- **Nothing made new.** No part is built, inserted or deleted, and no bands or modes are added.
- **The carry.** What the press carried is what the footer foresaw. Every put in the call trace is an app body or a
  sprocket locked to one, else a STOP. The puts and the carry are kept as facts: the plan's §6 expects no gear to move,
  but W9a's value Update put the train after a turn, and this run turns nothing, so the script does not assume either.
- **Nothing of the user's in error.**
- **Nothing saved by the app.** Every `.SLDPRT` and `.SLDASM` has the same size, time and sha256 as before the press.
- **The sentence.** It begins *Updated SolidWorks* and holds package C's sentence exactly once: *The 5 parts now
  printed keep their file names, without the _P a part built printed is named with: Update SolidWorks never renames a
  file, and Build again… makes new parts named with _P if you want the mark.* It does not hold the stale per-part
  clause *which no longer says what it holds*. The self-check holds the script's copy of that sentence to
  `ui_text._process_names_kept`'s output on W9's snapshot.

**Read back.**

- **Every part's Backlash.** `Session.equations` in each of the five parts reads the IIF, evaluating to 0.3 at module
  1.25.
- **The record**, read from its file: link schema 11, and the same five part files as before, so none is renamed or
  new. Each part's spec says `process` printed and its Backlash variable is the IIF. Each `.gear.json` is at sidecar
  3, printed.
- **The user's work, as W9a's go reads it:** every user mate joins what it joined before; every mode shown and
  `go_judge` again (each app body at its frame on record, the locked sprockets on their gears, the user mates on and
  in no error, Sprocket-4 where it was, the train free); the User Keyway's code 0; the user's components in the copy.

**A second Update.**

- **Saved and closed as the user would:** `save_user`, then everything of the copy closed without a further save.
- **Planned quiet.** Classify plans nothing changed (`record_matches`): the record now holds every part printed, and
  the workbook says Printed.
- **The press is quiet.** It changes and places nothing, says *SolidWorks already matches the workbook: nothing was
  changed.*, and does not hold the name sentence (the F1 review's S2, live). W8's `check_quiet_update` reads every
  gear where it stood and every document unmarked before and after. The record on disk then holds no unsaved or
  mismatched document.
- **K11 on the IIF.** This press reads every part's Backlash live against the record's IIF. If SolidWorks stores the
  IIF in any other form than the planned text with spaces aside, it refuses here, and the line fails with its
  sentence. That is the review's "things to watch on the run".

The copy is then ended by W8's `end_copy` (saved and closed, as every W9 copy section ends).

**What "the record at the new schema" rests on.** W8's `copy_built` puts the master's paths onto the copy through
store's own writer, so the copy's record is at link 11 before the app opens it. The log says so, with the number
read. The master's own schema (7) is read from its file before the copy. So the link number after the Update shows
little; the parts' specs, their variables and the sidecars at 3 are what F1 alone writes.

## SolidWorks calls

**None new to the repo.** The builds are `swbuild.build` and `build_pair` and the Update `update_gearbox`, as the
app makes them. The reads are:

- W9a's (`read_now`, `read_every`, `feature_list`, `components`);
- W9b's `Session.equations`;
- small_pinion_check's `readings`: the volume, `GetBodies2`, `IBody2.GetVertices` / `IVertex.GetPoint`, every
  feature's `GetErrorCode2`, and the Equation Manager's `Status`, logged;
- gear_pairs_check's `drive`: `AddMate5` (angle), the mate's `Name` set, `IEquationMgr.Add2`, the indexed put,
  `ForceRebuild3` and `interference_count`.

**On 2024:** small_pinion_check's readings have a committed log on SolidWorks 2026 only
(`small-pinion-2026-20261114-184220.log`), so on 2024 they are calls made there for the first time by a committed
script. gear_pairs_check's drive has a 2024 log (`sw2024/gear-pairs-20261113-184641.log`).

## STOPs

As W9a's, which end the run:

- any window during a job, under the version's What's Wrong rule;
- with `--close-outlived-whats-wrong` on 2024, W9c's close path for a What's Wrong that outlives its job;
- a read marking a document;
- an Update putting anything but an app body or a locked sprocket;
- under 2 GB free before a section;
- a hung worker or a lost session.

No What's Wrong is expected: nothing of the user's is in error in setup.master.

These end the `rangebox` section only, its copy ended:

- the master not built before F1;
- under 6 GB free just before the press (2024's first press on a freshly opened RangeBox costs 3.3 to 4 GB over the
  2 GB floor);
- the press refusing (its sentence kept).

A script fault fails its section with the traceback's tail, as in W9a.

## Without SolidWorks

`python probe/f1_demonstration.py --self-check` (from the worktree, with `PYTHONPATH=src`) ran 51 checks, 0 failed, on
2026-11-18 at `e0a8d62`. Each judgement the live sections make is a plain function, shown holding on the app's own
figures and failing each way it can fail:

- **The Backlash text and value**, on the app's own variables at modules 1.5 and 0.8 both ways. It fails on the IIF
  read machined, a wrong value, a literal, no equation, two equations, and the app's figure off.
- **The _P mark.**
- **The `.gear.json`**, on the app's own records. It fails on each read as the other process, and on a machined record
  with a `process` key, a nozzle, or at sidecar 2.
- **The volume**, on the app's own outlines. It fails on the other process's volume, on 0.2 % off, and on two outlines
  too near to tell apart. At module 0.8 the two outlines are one; a reading 2e-6 apart fails.
- **The turn.** It fails on the wrong sense, a short turn, an interference at either end, gear A fixed, and no turn.
- **The rangebox judgements, on W9's own record of RangeBox** (`tests/fixtures/printed`, written by W9's code at
  `f3c4873`), read and planned through the app with `blank_process` as the window does:
  - *as built:* holds, and fails with Printed typed, a _P name, a Process row, a blank read printed, or no plan;
  - *the footer:* W9's, and fails on one with work to do or naming Process;
  - *both Process lines* equal the pinned ones;
  - *Backlash alone:* holds, and fails on the as-built plan, on Sun's face width changed too (naming Face Width), on
    one part more than expected, on no plan, and on a part whose Backlash stays the machined rule;
  - *the footer before the press* begins with the pinned sentence.
- **C's name sentence.** It is the script's copy, said by C's code. It is not said again once the record holds the
  parts printed. It is singular for one part. The sentence check fails on twice, never, and the stale clause.
- **The Update's per-document result.** It fails on a part left unchanged, a second global, the layout or a carrier
  changed, and another document changed.
- **The record judgement.** It fails on link 10, the parts still machined, a renamed part, and a sidecar at 1.
- **The folder snapshot.** It ignores Excel's lock file, and finds a file rewritten or removed.
- **The strip's own form** (Tk needed; there is a display on this host): it opens Printed as Gear_m1.5_N25_P with no
  worker; each of the four spur cases and both pairs plans the names above, with the backlashes above.

**Rehearsed offline, not committed.** Both masters' `RangeBox.xlsx` and records were copied (read-only on the
masters) into a scratch folder, their paths moved onto it, and read through a Desk with the window's `_blank_process` (as W8's Desk now has it), pywin32 stood in. On each
master:

- *as built* holds; the footer is W9's; the line says to add the row; the read writes nothing;
- the row added at `Box!A10` / `B10` reads Printed;
- *Backlash alone* holds for the five parts;
- the footer before the press begins with the pinned sentence.

The scratch folder was deleted. A Linux import of the live part with pywin32 stood in found every name it uses in
W9a's, W8's and the two gear scripts.

## Found while writing it, and fixed

**W8's `Desk._after_read` assessed without the window's `blank_process`.** So W9a's Desk9 read a workbook with a
blank Process as Printed, and W9b's, W9c's and W9d's sections read it so through Desk9.

- Through the harness, the claim of PLAN-PRINTED §2.7 did not hold. That section says a W9 demonstration run again
  with an app at or after F1 needs nothing written into W9's masters.
- Any W9 section that copies a master built before F1 (setup, rangebox, reducer, fixed-updated) would have planned
  every part changed to the printed Backlash, and its first press would have written them.
- Fixtures the harness writes itself (`write_fixture`) are built in code and say *machined* on their Box, so they
  were not affected.

**The fix.** By the coordinator's ruling, W8's Desk now passes the window's own `_blank_process` (with its
`_settled`) to `assess` (`e3705a1`).

**Its check.** `probe/workbook_assembly_check.py --self-check`, the script's first self-check, shows it on W9's
snapshot:

- blank, Machined with no part changed (before the fix it read Printed with all five parts changed);
- Printed typed, printed;
- no record, Printed.

This script's own work-round Desk was then removed: Desk9 serves.

## What the script does not measure

- **The play in a mesh**, as said under pair.
- **A tooth's thickness itself.** The volume is an integral over the whole outline. At module 0.8 the printed and
  machined teeth are one shape, and only the global's text differs.
- **The footer word for word against W9's.** No W9 app runs here. The words for the state, and the absence of
  Process, are what is held. B's test on the fake (`test_printed_workbook`) holds the footer word for word against
  W9's own.
- **K11 refusing a printed default the user changed in SolidWorks.** The fake's test shows it; live, only K11 passing
  the IIF on the second press is read.
- **Build again… after Printed**, the planet-copy carry B found, a typed Nozzle, a typed Backlash on a printed
  gearbox, and the helical, herringbone, ring, bevel, sleeve, dog and hub kinds built printed alone. The dogs, the
  sleeve and the ring are changed by value in rangebox.
- **A user's mate on a tooth face re-solving by about 0.035 mm** (§6). setup.master has no mate on a tooth face.
- **The form's warnings.** They are logged only. The thin-tip, module-floor and clearance sentences are A's and C's
  tests.
- **Motion gear mate is set by the script.** The form's pair opens with Motion fixed, which would build a pair that
  does not turn.

## What must be open or closed

- **SolidWorks.** A session started for the run, alone, with its PID given.
  - No document of the user's open whose file name the run uses: `Gear_m1.5_N25*`, `Gear_m0.8_N25*`,
    `Pinion_m1.5_N25*`, `Gear_m1.5_N50*`, `Pair_m1.5_25T_50T*`, `RangeBox*`, `Gear_m1.25_*`, `Ring_m1.25_N55`,
    `Dog_m1.25_N17`, `Sleeve_m1.25_N17`, `Sprocket.SLDPRT`, `Housing.SLDPRT`.
  - SolidWorks 2024 in a fresh session for `rangebox`.
- **Excel.** The script starts and quits its own. No `RangeBox.xlsx` may be open in the user's.
- **The laptop.** On mains power, the lid open. Over 6 GB free for rangebox.
- **Tk.** The spur and pair sections open a hidden Tk window in the script's own process; nothing needs doing with it.

## Command lines

Make a `git archive` of the commit to run into `RUN\snap`, with `SNAPSHOT_COMMIT` beside `src`. Start SolidWorks for
the run and give its PID. Keep one `RUN\out` per version, and give each invocation its own log.

```
rem SolidWorks 2026: all three (about 22 min)
python.exe RUN\snap\probe\f1_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\f1-demo-sw2026-1.log ^
    --sections spur,pair,rangebox ^
    --user-master <probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master

rem SolidWorks 2024, the confirming build: rangebox first, in a fresh session (about 30 min)
python.exe RUN24\snap\probe\f1_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f1-demo-sw2024-1.log ^
    --sections rangebox --close-outlived-whats-wrong ^
    --user-master <probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master

rem then the spur and the pair, in the same session or another (about 11 min)
python.exe RUN24\snap\probe\f1_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f1-demo-sw2024-2.log ^
    --sections spur,pair
```

`--close-outlived-whats-wrong` is in force on 2024 only. Without it a What's Wrong that outlives its job is the STOP;
none is expected here.

**Re-running.** A section `RUN\out` already holds is skipped and said. `--redo` sets its folder aside
(`<name>.prev-<time>`) and runs it again.

The JSON (`f1-demo-<time>.json`) is written beside the log after every section. Per section it holds:

- for `spur` and `pair`, each case's equations, volume, expected volumes and drive;
- for `rangebox`, the master's schema, the as-built footer and line, the foreseen carry, the press's fact and
  sentence, and the second press's fact.
