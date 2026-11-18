# F2's demonstration on SolidWorks: the sections, the masters, the commands, the STOPs

The script is `probe/f2_demonstration.py`. It is the SolidWorks part of PLAN-PRINTED §3.3's *Done when* ("the
demonstration has run on 2026 and on 2024, every section clean, and been reviewed"), and it takes in the six things
F2-PROBES-REVIEW §4 says the probe did not show. **It has not run yet.** It was written on Linux against branch
`printed` at `ac83420` (the findings set in `ae42722`; B's review fixes `dcefc9d`, `4b34f59`; C's `2cc34d9`), every
sentence held to the app's own code there; its self-check passes there (31 checks, 0 failed). Expect script faults on
its first live run, as every demonstration had.

**How it works.** It runs W9a's `main` with its own five sections, as F1's script does, and changes no other script. From
W9a's harness: the attach by `--pid` and its check, the dialog watch with the What's Wrong rule per version, keep-awake,
the JSON after every section, APPDATA in `<out>\appdata`, the guarded close, `--sections` and `--redo`, Desk9, `press`
(Update SolidWorks), `keyway`, `save_user`, `users_in_copy` and `entities_of`; `--close-outlived-whats-wrong` is W9c's own
close path, put in only when the flag is given. Two things are its own:

- **The presses are the app's own.** On the form, the strip's real `gui.GearApp` (its own link not started, as F1's):
  the form's `_print_files`, its bar's line (`_refresh_print_line` from the strip's own `_read_snapshot` of the
  session), and the form's `_collect_build` / `_finish_print`. In the Workbook window, `DeskP`: W9a's Desk9 carrying
  `WorkbookWindow.press_print`, `_submit`, `_collect_job`, `_finish_print`, `_worker_free`, `_foreign_record` and
  `_folder` themselves. Only the worker each hands its job to is the script's (`Strand`): the job runs on this run's
  worker under W9a's watch, as an app job under the What's Wrong rule, and its answer is handed back for the app's own
  finish. The self-check holds DeskP to the window's source: every attribute those seven methods read on the window or
  its strip is one DeskP has.
- **Every SolidWorks call a press's job makes is counted by member** (a wrapper over W9a's counted `swcom.call`, on
  only while a press's job runs). That is how "nothing opened or activated" is read, not assumed.

The STEP files are read twice: by the app's own check (its facts in the result) and by the script's own reader
(`step_read`, written apart from printout's and the probe's): the frame, the FILE_SCHEMA (AP203 both editions, AP214,
AP242), one MANIFOLD_SOLID_BREP in a CLOSED_SHELL, no open shell or surface model, every length unit
`MILLI.METRE` (this machine's export options), and from the VERTEX_POINTs the largest radius from Z and the extent along
Z against the gear's own d_a / 2 and face, both worked in the script (not taken from the app), to 0.01 mm. The span over
k teeth is worked in the script from §3.0's closed form and the nearest-contact rule, held to all ten rows of §3.0's
table to 1e-4 mm in the self-check.

## The masters each section needs

- `gates`, `form`: none. Each builds into a fresh folder of `<out>`; `gates` also writes the 12 : 1's workbook (not
  built) for the window.
- `workbook`, `refusals`: the printed 12 : 1, W9's fixture `Reducer_12to1.xlsx` with Printed on its Box (four parts,
  Gear_m1.5_N17_P, Gear_m1.5_N68_P, Gear_m2_N17_P, OutputGear). The first of the two to run builds it through the
  app's own Build (W8's `write_fixture` and `build_turning`, about 1.5 min) and keeps `<out>\f2-reducer.master`; the
  other copies it. `--printed-reducer-master` gives one kept by an earlier run of the same SolidWorks version.
- `userwork`: **`--user-master` is required**, W9a's `setup.master` for the version run (RangeBox with the user's work:
  Sprocket-1..4, Housing-1, eight user mates, the User Keyway in Sun's part), only copied. The section stops unless its
  record is below link 11 with no part saying a process (built before F1).
  - SolidWorks 2026: `<probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master`
  - SolidWorks 2024: `<probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master`
  - The 2026 master does not open in 2024.
- Every section uses the user's own part, S0's Housing (and Sprocket), built by the strip once a run into
  `<out>\user-parts` (W9a's `user_parts`).

`<probe folder>` is `C:\Users\M0obo\Documents\GearGeneratorProbe` on this laptop.

## Sections

Times are estimates from the measured steps of W9a's, F1's and F2's probe runs (a part 15 to 25 s, a pair about 40 s,
the 12 : 1 built about 1.5 min on both versions, an export 0.4 s, a value Update on the 12 : 1 about 25 s, RangeBox's
first Update 2.7 min on 2026 and 5 on 2024).

| Section | What it does | 2026 | 2024 |
|---|---|---|---|
| `gates` | The findings as they stand; a coupon and the 12 : 1's workbook; Print files on both as they stand, then with each gate patched shut in this process; the job's own gate. | 2 min | 3 min |
| `form` | Coupon_A built by the form and pressed twice; a printed helical and a printed herringbone, each built and pressed. | 4 min | 6 min |
| `workbook` | The printed 12 : 1 (built here first if no master: 1.5 min more); five presses from the window and the changes between them. | 6 min | 9 min |
| `refusals` | The form's refusals on Coupon_R; the window's on a copy of the printed 12 : 1, with a quiet Update and a value Update; the user's pair built. | 9 min | 14 min |
| `userwork` | RangeBox copied; a press as built; Printed typed, one Update; a press before and one after the save; the user's work read before and after. | 8 min | 14 min |

About 30 minutes on 2026 and 45 on 2024, more than the plan's 15 and 25: the plan's two sections are here five, and the
probe review's six points, the refusals word for word and the user's work are each made and read.

### gates: what each line bears out

- **The findings as they stand**, each of the six (for the year attached) said beside the review's value, with
  `EXTENT_MEASURED` and `swcom.DOCUMENT_BY_PATH_ROUTE`. Facts, not checks: this section is for any state. EXTENT_MEASURED
  not True is a NOTE (the app's size check is then skipped everywhere; the script's own size reading still runs).
- **As they stand**, on the form (Coupon_G built, active) and in the window (the 12 : 1 written, nothing built):
  - gate shut (the script's own reading of F2-INTERFACES §3, held to `printout.gate` in the self-check): the press says
    GATE_COPY's or GATE's words exactly, submits nothing, the bar names no file, no press folder is made, SolidWorks'
    documents are as they were;
  - gate open (the findings set, as now): the form's press writes one file (the form section judges a press whole);
    the window's planning, past the gate, says NO_PART's words for G1, G2, G3 and G4 and submits nothing.
- **Shut in this process only, said in the log and put back after:** `SAVE_AS_COPY` None (GATE_COPY on both), then
  `STEP_EXPORT_ON_<year>` None with SAVE_AS_COPY the review's 2 (GATE by year and revision, on both).
- **The job's own gate.** The form's own plan for Coupon_G, its revision replaced by the other version's, handed to
  `swbuild.print_parts`: the "SolidWorks changed since Print files was pressed (…)" words, no SolidWorks call at all
  in the job, nothing written. If the findings were shut as they stand, the gate is patched open for this one plan,
  said; nothing past the revision check runs.

### form: what each line bears out

For Coupon_A (§3.2: module 1.5, 20 teeth, face 8, bore 8, Printed), then a printed helical (m_n 2, z 20, β 15°, face 10,
no bore; the probe's) and a printed herringbone (the same, face 20), each built by the form's own plan, job and finish
with the user's Housing open behind:

- **The span on the form.** The Derived panel's labels as drawn (read from the widgets): one row *Span over k teeth*
  whose figure is the script's W to three places, and package A's figure within 1e-4 mm. Coupon k 3, 11.2088; helical
  and herringbone k 3, W_n 15.0972.
- **The bar** names the file it will write, C's words, shown.
- **Each press, judged whole** (`written`):
  - the job's answer: every part written and checked by the app, none failed, the active document as it was, no
    save flag turned on;
  - **one new folder** in the Output folder's print folder, named by the press's own local date and time (to the
    second, with a counter allowed), holding the STEP file and `print list.txt` alone; every earlier press folder,
    file by file (size and sha256), as it was;
  - **the status in C's words** (*Print files wrote Coupon_A.step and its print list in …*, the folder as
    `ui_text.short_path` shows it);
  - **the file by the app's check** (schema accepted, unit `MILLI.METRE`, size fact `checked`) **and by the script's
    reading** (above), outer radius 16.5 (helical 22.706) and face to 0.01 mm;
  - **the list**: *Print list: <stem>*, *Process: Printed, 0.4 mm nozzle*, the part's block (*print 1*, its span line
    with k and W to three places, *Checked: one closed solid …; outer diameter and face width match the gear.*), the
    settings once, no DO NOT PRINT;
  - **SolidWorks as it was**: no document opened, closed, renamed or marked, every window (Visible) and the active
    document as before; no `.SLDPRT` or `.SLDASM` changed (size, time, sha256): no save;
  - **the calls**: one SaveAs and nothing that opens, activates, closes or saves.
- **A second press of the coupon** makes a second folder, the first untouched, and its file is the same part as the
  first's by its vertices (one to one within 1e-4 mm, the probe's tolerance).
- **The herringbone**: its file is judged structurally by the script and its size reading is a **fact** for the
  reviewer (radius and extent against d_a / 2 and the face). Since `ae42722` the app skips its size check
  (*size not checked (a herringbone, not yet measured)*), which the list must say; if the app ever checks it, the
  script holds the app's verdict to its own reading.

### workbook: what each line bears out

On a copy of the printed 12 : 1, the assembly opened as the app opens one (its parts loaded only as components), the
user's Housing active:

- **The state is read first**: every part's `Visible` False (the read `PART_WINDOW_READ` names), the assembly's True,
  the user's part active.
- **Component-only press** (the review's points 1 and 5): all four written with nothing activated, opened or closed —
  the job's calls are four SaveAs and nothing else of WATCHED — so each was written by the handle the job itself takes
  (the walk, `DOCUMENT_BY_PATH_ROUTE` "walk"); every file checked by the app (`checked`) and by the script (radii 14.25,
  52.5, 19, 53; faces 15, 15, 20, 20: four sizes up to z 68, the review's ask for larger gears); the list with each
  part's row (*For G2 · print 1*) and span (k 2, 8, 2, 6); the assembly's flag, every component's state (resolved
  after) and the active document unchanged.
- **The job's reads off parts that are not the active document** (the review's points 2 and 3):
  - G2, loaded only as a component, its Face Width set 16 in its own window, saved, the window closed (read back
    Visible False): **GLOBALS_DIFFER**, C's words with *"Face Width" is 16 where its record says 15*. The positive
    reading is the clean press before (the same reads finding nothing). Put back, saved, closed.
  - G1 open in its own window behind the user's part, Face Width 16, not saved (read: Visible True, flag on, not
    active): **MODIFIED**; then saved: **GLOBALS_DIFFER** on a part in its own window but not active. Put back.
  - Each refusal: nothing written, SolidWorks' documents as they were (G1's flag stays on), and the job called
    nothing that opens, activates, saves or writes.
  - The feature-error read off a part not active is in `refusals` (FEATURE_IN_ERROR on G1, not active); its positive
    reading is every clean press here.
- **The job opening the parts itself** (the review's point 6; the "not found, no assembly open" way): the copy's
  documents closed, the user's part alone open: four written, the calls four OpenDoc6, four CloseDoc and four SaveAs
  (ActivateDoc3 any number: each open activates, the end puts the user's back); after, nothing of the copy open and
  the user's part active, its flag as it was.
- **The open-beside fallback, where the job takes it.** With the findings as set the job never takes it for a found
  component (`STEP_EXPORT_FROM_COMPONENT` True). So `STEP_EXPORT_FROM_COMPONENT_ON_<year>` is patched False **in this
  process only**, said, put back after, and the press made with the assembly open: each component opened beside it
  (four OpenDoc6), written, its window closed (four CloseDoc); after, the assembly open, unmarked, every component
  resolved, every part Visible False again, the user's part active.

### refusals: what each line bears out

Each refusal is a state made as a person makes it, then the press: **C's words exactly**, no press folder made, no
SolidWorks file changed, SolidWorks' documents as they were with the user's document active (where it is), and for a
refusal in the job, no call that opens, activates, saves or writes; for one at planning, nothing submitted.

- **The form, on Coupon_R**: Face Width 9, not saved: **MODIFIED**; saved: **GLOBALS_DIFFER**; put back. The user's
  keyway cut in the coupon (W9a's `keyway`) and saved: the press **writes**, the size fact *skipped: user features*
  from the job's own live read of the part (no record lists it), the list saying *size not checked (your features in
  it)*. If the list does not name the keyway, a NOTE: a form part has no inventory, so the list names none. An Output
  folder that does not exist: **NO_FOLDER** (the folder as the app shortens it), nothing made. The user's Sprocket
  (no `.gear.json`) active: **NO_RECORD**.
- **The window, on a copy of the printed 12 : 1**, the assembly open, the user's part active:
  - G4's component set lightweight (W9a's `set_state` route): **LIGHTWEIGHT**, *with Reducer_12to1 open, OutputGear may
    be a lightweight component of it …* — true here; after the press the component still reads lightweight and the
    assembly's flag is unchanged. Resolved again.
  - **G4's component suppressed: a fact, not pinned.** If SolidWorks drops the part, the app meets it with the same
    LIGHTWEIGHT words, which are untrue of a suppressed component, and the words are held exact; if SolidWorks keeps the
    part loaded, the app writes the set, judged whole. The log says which. Resolved; the copy closed unsaved and opened
    again.
  - The user's keyway in G1's part, saved, a **quiet Update** records it (W9a's k3 route): the press **writes** the
    set, G1's size *skipped: user features*, its list block *Your features left in it: User Keyway.*, the others
    checked.
  - G4's Flank typed *arcs* in Excel (a change Update cannot carry: G4's part made new, as W9d's Sun): **NEW_REVISION**
    naming OutputGear; the cell cleared, Update plans nothing again.
  - G1's Bore typed 14 in Excel: **CHANGES_ON_UPDATE** naming G1's part.
  - Update SolidWorks (the keyway rebuilt into error inside the bore, W9a's k3; on 2024 the What's Wrong rulings
    apply, under W9a's watch): the record marks G1's part alone unsaved: **UNSAVED_MARK**.
  - Saved as the person saves: G1's features read without activating it (User Keyway in error):
    **FEATURE_IN_ERROR**, the features named as the script read them, G1 not active.
  - The copy closed, the user's own pair (25 / 50 at module 1.5, machined, built by the app's pair route into
    `refusals-pair`) open and active: **LIGHTWEIGHT** naming all four parts *with Pair_m1.5_25T_50T open …* — untrue:
    they are closed and in no assembly. Then the form pressed with that assembly active: **NOT_A_PART**, without the
    assembly's name (the form hands the planner no path for a document that is not a part).
- **The LIGHTWEIGHT sentence** says the parts *may be* lightweight components of the open assembly. The job does not
  read component states (F2-PROBES-REVIEW §3.3): it refuses every part not found while any assembly is open. So the
  sentence is untrue for a closed part with an unrelated assembly open, and for a suppressed component; the section
  shows the first always and the second as SolidWorks has it.

### userwork: what each line bears out

On a copy of W9a's setup.master, RangeBox opened (the user's own document, active):

- **Before**: no Process row, the blank read Machined; the user's components in the copy (`users_in_copy`); every user
  mate's entities (`entities_of`); the User Keyway in Sun's part at code 0 (read without activation).
- **As built, Machined (E4)**: the press writes the five parts (Gear_m1.25_N29, Gear_m1.25_N13, Ring_m1.25_N55,
  Dog_m1.25_N17, Sleeve_m1.25_N17), the list *Process: Machined*, each block *Machined: … no span.*, the counts from
  the workbook's Copies (Planet 3, the dogs 2), Sun's size skipped for the user's feature, the ring's, dog's and
  sleeve's skipped by kind, the Planet's checked (radius 9.375, face 10).
- **Printed typed** on the Box sheet in Excel (F1's way: a row labelled Process), Update plans the five parts in place,
  one Update SolidWorks (W9a's `press`), ok, nothing of the user's in error.
- **Before the save**: the record marks the five parts unsaved: **UNSAVED_MARK** naming all five.
- **Saved as the person saves; the press**: the five written and nothing else in the folder (no Sprocket or Housing
  file); the list printed, Sun's and the Planet's spans (k 4, 13.1414; k 2, 5.4809), the ring's and sleeve's *over
  pins*, Sun's block *Your features left in it: User Keyway.* with *size not checked (your features in it)*; nothing
  saved (every SolidWorks file of the copy by sha256), the record file unchanged, the user's part files unchanged,
  every document, flag and window as before with RangeBox active; after, the user's components, the eight mates'
  entities and the keyway's code as before.

## SolidWorks calls

**None new to the repo.** The job's calls are the app's (F2-PACKAGE-B's table), measured by F2's probe on both
versions (SaveAs as a copy, `Visible`, the walk, `GetSaveFlag`, the equations, `GetErrorCode2`, OpenDoc6 / ActivateDoc3 /
CloseDoc on parts). The script's own:

- builds: the form's `swbuild.build` (F1's demonstration), `build_pair` (F2's probe), the 12 : 1's `build_gearbox` (W9a);
- the person's steps: `set_global_variable` and `rebuild` on the active part (F2's probe step 8), W8's `save_docs`
  (SaveAs3 to its own path), `CloseDoc` on a part's own window while an assembly holds it (F2's probe step 7b),
  `SetSuppression2` on a component 1 and 2 (W9a's lightweight) and 0 (the app's own component suppression, W8), W9a's
  keyway, Update SolidWorks (W9a, F1), Excel's edits (W8);
- reads: the walk with `GetPathName`, `GetTitle`, `GetType`, `GetSaveFlag` and `Visible` (F2's probe), `ActiveDoc`,
  `Session.components` and `feature_states` by `use_open_document` (W9a, W9d).

On 2024, `Visible` on a component-only part and SaveAs were made by F2's probe there; nothing here is first on either.

## STOPs

As W9a's, which end the run: any window during a job under the version's What's Wrong rule (with
`--close-outlived-whats-wrong` on 2024, W9c's close path); a read marking a document; under 2 GB free before a section;
a hung worker or a lost session. These end their section only: the findings not the reviewed ones (every export
section, before anything is opened); `userwork`'s master not built before F1, or under 6 GB free before its copy or its
Update (F1's floor); the window's Output folder not under the run folder. A script fault fails its section with the
traceback's tail.

A What's Wrong is expected only in `refusals` on 2024: the Update that rebuilds G1's keyway into error (W9a's
`box-k3` saw it there; k3 ran under the rule, gone ahead).

## Without SolidWorks

`python probe/f2_demonstration.py --self-check` (from the worktree, `PYTHONPATH=src`): **31 checks, 0 failed** at
`ac83420`. Each judgement the live sections make is a plain function, held on the app's own figures and failed each way
it can fail:

- **C's words**: the script's copy of each refusal it expects (22, singular and plural, NEW_REVISION and NO_FOLDER
  among them), the status after a clean press (one file and four), the bar's line and the list's size words, each
  equal to `ui_text`'s own. A change of C's words fails here before a live run.
- **The span**: §3.0's ten rows to 1e-4 mm; package A's span and the app's d_a / 2 equal the script's on the coupon,
  the helical, the herringbone, the 12 : 1's four parts and RangeBox's Sun and Planet. The span-row judgement fails on
  another k, 0.001 off, no row, two rows and no figure.
- **The STEP reader** on made-up files (a ';' and a doubled quote inside names): the good file holds; a cut frame, AP209,
  two solids, no closed shell, an open shell, a surface model, inches, radius 0.02 over, face 0.02 short and no vertex
  each fail alone; `printout.check_step` agrees on the same texts (it reads inches, which the script, expecting
  millimetres, does not).
- **The vertices**, **the press folder** (its name and time; one new folder, none, two, an earlier one changed or
  removed), **SolidWorks' documents** (the active one, a flag, one opened, closed or renamed, a window, an empty read,
  the user's gone), **the calls**, **the list** (a part missing, a count, the span 0.002 off, the size said otherwise, a
  feature not named, DO NOT PRINT, another name, nothing expected, the settings twice), **the findings** (each of the six
  unset, 1 for True, the probe's prose for Visible) and **the gate** (the script's reading equal to `printout.gate`'s
  code, detail and words in four states, connected and not).
- **The planners on the app's own fixtures**: W9's 12 : 1 with Printed plans the four parts named, printed; on W9's
  record of RangeBox (as built) the window's planner gives the five parts with the rows and counts the script works
  from the Copies, and the size check skipped as the script expects.
- **The window**, read as source: every attribute `press_print` and the methods it reaches read on the window or its
  strip is one DeskP gives.
- **The strip's own form** (Tk): Coupon_A's span row drawn; its record written by the form's `_write_sidecar`; pressed
  with SAVE_AS_COPY None (GATE_COPY, nothing submitted, no bar line), STEP_EXPORT_ON_2026 None (GATE by year), the gate
  open (the bar names the file, one job submitted, its answer finished by the form's own `_collect_build`: C's status
  and the list written into the folder), no `.gear.json` (NO_RECORD) and an assembly active (NOT_A_PART).

**Rehearsed offline, not committed**: the live part imported on Linux with pywin32, PIL and the rest stood in (every
name it takes from W9a and W8 found), and DeskP pressed on the printed 12 : 1's workbook written by the app into a
scratch folder: GATE_COPY patched, then NO_PART with the gate open, through `WorkbookWindow.press_print` itself. The
scratch folder was deleted.

## What the script does not measure

- **A STEP file in Bambu Studio**: the user's step (§3.2 step 2, U5).
- **NO_RECORD for a `.gear.json` that does not read, a list that could not be written, SOLIDWORKS_REFUSED,
  FILE_CHECK on a real file, FOREIGN_RECORD, NO_PART on a built gearbox, MISMATCHED_MARK, COMPONENT_ONLY**: each needs
  a file damaged or a state no person makes on purpose; the fake's tests (package B's and C's) hold them.
- **A part open in its own window and active while an assembly holds it**, beyond the coupon; a minimised window; an
  add-in's hidden document; a lightweight component inside a user's sub-assembly (F2-INTERFACES §5.2: not covered).
- **The herringbone's size check**: skipped by the app (its reading here is a fact). Bevel gears, rings, sleeves, dogs
  and hubs are exported only through RangeBox (ring, sleeve, dog), their size checks skipped by kind.
- **A user's export options other than this machine's** (AP203, millimetres): the script expects millimetres.
- **`GetOpenDocumentByName`**: the route stays the walk (`DOCUMENT_BY_PATH_ROUTE`); its count is logged.
- **The Measured line** (§3.0): the form's figure for a reading is package A's and C's, held by their tests; the
  user's calipers are §3.2's.

## What must be open or closed

- **SolidWorks**: a session started for the run, alone, its PID given; nothing of the user's open with a file name the
  run uses (`Coupon_*`, `Helical_m2_N20_15R_P`, `Herringbone_m2_N20_15R_P`, `Gear_m1.5_N17_P`, `Gear_m1.5_N68_P`,
  `Gear_m2_N17_P`, `OutputGear`, `Reducer_12to1`, `Pinion_m1.5_N25`, `Gear_m1.5_N50`, `Pair_m1.5_25T_50T`, `RangeBox`,
  `Gear_m1.25_*`, `Ring_m1.25_N55`, `Dog_m1.25_N17`, `Sleeve_m1.25_N17`, `Sprocket`, `Housing`). SolidWorks 2024 in a
  fresh session for `userwork`.
- **Excel**: the script starts and quits its own; no `Reducer_12to1.xlsx` or `RangeBox.xlsx` open in the user's.
- **The laptop**: on mains power, the lid open; over 6 GB free for `userwork`; WSL idle during the 2024 `userwork` (its
  free memory is Windows', and other agents' test runs count against it).
- **Tk**: `gates`, `form` and `refusals` open a hidden Tk window in the script's own process.

## Command lines

Make a `git archive` of the commit to run into `RUN\snap` with `SNAPSHOT_COMMIT` beside `src`, run `--self-check` on
the snapshot first, start SolidWorks for the run and give its PID. One `RUN\out` per version; each invocation its own
log.

```
rem SolidWorks 2026: all five in one invocation (about 30 min)
python.exe RUN\snap\probe\f2_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\f2-demo-sw2026-1.log ^
    --sections gates,form,workbook,refusals,userwork ^
    --user-master <probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master

rem SolidWorks 2024, the confirming build: userwork first, in a fresh session, WSL idle (about 14 min)
python.exe RUN24\snap\probe\f2_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f2-demo-sw2024-1.log ^
    --sections userwork --close-outlived-whats-wrong ^
    --user-master <probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master

rem then the rest, in a fresh session (SolidWorks 2024 grows by 3 to 7 GB over a RangeBox Update; about 32 min)
python.exe RUN24\snap\probe\f2_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f2-demo-sw2024-2.log ^
    --sections gates,form,workbook,refusals --close-outlived-whats-wrong
```

**The order on 2024, for memory**: `userwork` first in its own fresh session (F1's rangebox measured 3.1 to 7.0 GB of
SolidWorks' private memory over two RangeBox presses), then the four others in a second fresh session, `workbook`
before `refusals` so the 12 : 1 is built once. `--close-outlived-whats-wrong` is in force on 2024 only.

**Re-running.** A section `RUN\out` already holds is skipped and said; `--redo` sets its folders aside
(`<name>.prev-<time>`) and runs it again. `f2-reducer.master` is not a section's folder and is kept.

The JSON (`f2-demo-<time>.json`) is written beside the log after every section: the findings as they stand and the
job gate's words (gates), each press's folder and the app's and the script's readings of each file (form, workbook,
userwork), what the suppressed component met (refusals).

## For the reviewer

The points to look at hardest are in the coordinator's report for this commit; in short: DeskP's restatements (none
but the worker), `refused` and `written` as the only judges of a press, the calls expected per way, the suppressed
component left a fact, and NEW_REVISION's G4 Flank edit (expected to name OutputGear alone, as W9d's Sun was).
