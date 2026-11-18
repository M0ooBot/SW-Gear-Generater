# F2's demonstration on SolidWorks: the sections, the masters, the commands, the STOPs

The script is `probe/f2_demonstration.py`. It is the SolidWorks part of PLAN-PRINTED §3.3's *Done when* ("the
demonstration has run on 2026 and on 2024, every section clean, and been reviewed"), and it takes in the six things
F2-PROBES-REVIEW §4 says the probe did not show. **It ran on 2026-11-18 from `b3fe4a1`, on SolidWorks 2026 and then on
2024, every section clean with no fix to the script** (the run sections at the end). It was written on Linux against branch
`printed` at `ac83420` (the findings set in `ae42722`; B's review fixes `dcefc9d`, `4b34f59`; C's `2cc34d9`) and brought
to its review (`F2-DEMONSTRATION-REVIEW.md`, `0d1dfee`) and to the app's answers to it (B's `888035a`, C's `567773c` and
`5e45718`), every sentence held to the app's own code at `5e45718`; its self-check passes there (35 checks, 0 failed). Expect script faults on
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
  its strip is one that DeskP, W9a's Desk9 or W8's Desk gives, each read from its own source (DeskP is not importable
  off Windows), and it shows the check failing without DeskP's body.
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
| `workbook` | The printed 12 : 1 (built here first if no master: 1.5 min more); six presses from the window and the changes between them. | 7 min | 10 min |
| `refusals` | The form's refusals on Coupon_R and its Update values; the window's on a copy of the printed 12 : 1, with a quiet Update and a value Update; the user's pair built. | 10 min | 15 min |
| `userwork` | RangeBox copied; a press as built; Printed typed, a press, one Update; a press before and one after the save; the user's work read before and after. | 8 min | 14 min |

About 31 minutes on 2026 and 48 on 2024, more than the plan's 15 and 25: the plan's two sections are here five, and the
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
- **The herringbone**: its file is judged structurally by the script, and its size reading gets a **verdict**, logged as
  a NOTE and kept in the JSON (*holds* or *does not hold* against d_a / 2 and the face to 0.01 mm), for the ruling on
  `"herringbone"` in `printout.EXTENT_SKIPPED`. Since `ae42722` the app skips its size check (*size not checked (a
  herringbone, not yet measured)*), which the list must say; if the app ever checks it, the script holds the app's
  verdict to its own reading.

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
    active): **MODIFIED**; then saved: **GLOBALS_DIFFER** on a part in its own window but not active. Put back, saved,
    its window left open: a clean press writes the set with G1 open behind the user's part, by its object, nothing
    activated (four SaveAs alone; the review's nit on point 3). G1's window closed after.
  - Each refusal: nothing written, SolidWorks' documents as they were (G1's flag stays on), and the job called
    nothing that opens, activates, saves or writes.
  - The feature-error read off a part not active is in `refusals` (FEATURE_IN_ERROR on G1, not active); its positive
    reading is every clean press here.
- **The job opening the parts itself** (the review's point 6; the "not found, no assembly open" way): the copy's
  documents closed, the user's part alone open: four written, the calls four OpenDoc6, four CloseDoc and four SaveAs
  (ActivateDoc3 any number: each open activates, the end puts the user's back); after, nothing of the copy open and
  the user's part active, its flag as it was.
- **Every component resolved** is read on the assembly's own components by name (the four gears and the layout): a
  read of none, or of others, fails.
- **The open-beside fallback, where the job takes it.** With the findings as set the job never takes it for a found
  component (`STEP_EXPORT_FROM_COMPONENT` True). So `STEP_EXPORT_FROM_COMPONENT_ON_<year>` is patched False **in this
  process only**, said, put back after, and the press made with the assembly open: each component opened beside it
  (four OpenDoc6), written, its window closed (four CloseDoc); after, the assembly open, unmarked, every component
  resolved, every part Visible False again, the user's part active.

### refusals: what each line bears out

Each refusal is a state made as a person makes it, then the press: **C's words exactly**, no press folder made, no
SolidWorks file changed, SolidWorks' documents as they were with the user's document active (where it is), and for a
refusal in the job, no call that opens, activates, saves or writes; for one at planning, nothing submitted.

- **The form, on Coupon_R**: Face Width 9, not saved: **MODIFIED**; saved: **GLOBALS_DIFFER**; then the form's own
  **Update values** (its record loaded by the build's finish) sets it back and rebuilds, the person saves, and a press
  **writes** a folder of its own (§3.3's "after Update values"). The user's keyway cut in the coupon (W9a's `keyway`)
  and saved: the press **writes**, the size fact *skipped: user features* from the job's own live read (no record lists
  it), the list saying *size not checked (your features in it)* and naming the user's features as the script reads them
  in the part (*Your features left in it: User Keyway.*; the keyway's sketch beside it where SolidWorks keeps it
  top-level), since `5e45718` names a written part's features from the job's live read. An Output
  folder that does not exist: **NO_FOLDER** (the folder as the app shortens it), nothing made. The user's Sprocket
  (no `.gear.json`) active: **NO_RECORD**.
- **The window, on a copy of the printed 12 : 1**, the assembly open, the user's part active:
  - G4's component set lightweight (W9a's `set_state` route): **LIGHTWEIGHT**, *OutputGear is not open where Print
    files can reach it while Reducer_12to1 is open: it may be a lightweight or suppressed component of it, or simply
    closed; …* (C's words since `567773c`); after the press the component still reads lightweight and the
    assembly's flag is unchanged. Resolved again.
  - **G4's component suppressed: a fact, not pinned.** If SolidWorks drops the part, the app meets it with the same
    LIGHTWEIGHT words, which name that case, held exact; if SolidWorks keeps the
    part loaded, the app writes the set, judged whole. The log says which. Resolved; the copy closed unsaved and opened
    again.
  - The user's keyway in G1's part, saved, a **quiet Update** records it (W9a's k3 route): the press **writes** the
    set, G1's size *skipped: user features*, its list block naming the user's features the script reads in G1's part
    (the record's inventory is checked to hold the User Keyway; the review's M1: the sketch may be listed beside it),
    the others checked.
  - G4's Flank typed *arcs* in Excel (a change Update cannot carry: G4's part made new, as W9d's Sun): **NEW_REVISION**
    naming OutputGear; the cell cleared, Update plans nothing again.
  - G1's Bore typed 14 in Excel: **CHANGES_ON_UPDATE** naming G1's part.
  - Update SolidWorks (the keyway rebuilt into error inside the bore, W9a's k3; on 2024 the What's Wrong rulings
    apply, under W9a's watch): the record marks G1's part alone unsaved: **UNSAVED_MARK**.
  - Saved as the person saves: G1's features read without activating it (User Keyway in error):
    **FEATURE_IN_ERROR**, the features named as the script read them, G1 not active.
  - The copy closed, the user's own pair (25 / 50 at module 1.5, machined, built by the app's pair route into
    `refusals-pair`) open and active: **LIGHTWEIGHT** naming all four parts *… while Pair_m1.5_25T_50T is open: they may
    be lightweight or suppressed components of it, or simply closed …*: they are simply closed. Then the form pressed
    with that assembly active: **NOT_A_PART** naming it (*… and Pair_m1.5_25T_50T.SLDASM is not a part …*, since
    `567773c`).
- **The LIGHTWEIGHT sentence.** The job does not read component states (F2-PROBES-REVIEW §3.3): it refuses every part
  not found while any assembly is open. Since `567773c` the sentence names all three cases it stands for (lightweight,
  suppressed, simply closed); the section shows the first and third always and the second as SolidWorks has it.

### userwork: what each line bears out

On a copy of W9a's setup.master, RangeBox opened (the user's own document, active):

- **Before**: no Process row, the blank read Machined; the user's components in the copy (`users_in_copy`); every user
  mate's entities (`entities_of`); the User Keyway in Sun's part at code 0 (read without activation).
- **As built, Machined (E4)**: the press writes the five parts (Gear_m1.25_N29, Gear_m1.25_N13, Ring_m1.25_N55,
  Dog_m1.25_N17, Sleeve_m1.25_N17), the list *Process: Machined*, each block *Machined: … no span.*, the counts from
  the workbook's Copies (Planet 3, the dogs 2), Sun's size skipped for the user's feature, the ring's, dog's and
  sleeve's skipped by kind, the Planet's checked (radius 9.375, face 10).
- **Printed typed** on the Box sheet in Excel (F1's way: a row labelled Process), Update plans the five parts in place;
  **Print files: CHANGES_ON_UPDATE** naming the five, nothing submitted (the review's S4: the plan's whole sequence,
  edited, refused, updated unsaved, refused, saved, written, on one gearbox); one Update SolidWorks (W9a's `press`), ok,
  nothing of the user's in error.
- **Before the save**: the record marks the five parts unsaved: **UNSAVED_MARK** naming all five.
- **Saved as the person saves; the press**: the five written and nothing else in the folder (no Sprocket or Housing
  file); the list printed, Sun's and the Planet's spans (k 4, 13.1414; k 2, 5.4809), the ring's and sleeve's *over
  pins*, Sun's block naming the user's features the script reads in Sun's part (the User Keyway; the as-built press
  likewise) with *size not checked (your features in it)*, and no such line in the other four; nothing
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

`python probe/f2_demonstration.py --self-check` (from the worktree, `PYTHONPATH=src`): **35 checks, 0 failed** at
`5e45718`. Each judgement the live sections make is a plain function, held on the app's own figures and failed each way
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
  feature not named, a feature named where none is expected, DO NOT PRINT, another name, nothing expected, the settings
  twice; and C's machined and ring blocks as userwork expects them, a machined list read as printed failing), **the
  herringbone's verdict** (radius off, face off, no vertex), **the components resolved** (none read, others read, one
  lightweight, nothing expected), **the findings** (each of the six
  unset, 1 for True, the probe's prose for Visible) and **the gate** (the script's reading equal to `printout.gate`'s
  code, detail and words in four states, connected and not).
- **The planners on the app's own fixtures**: W9's 12 : 1 with Printed plans the four parts named, printed; on W9's
  record of RangeBox (as built) the window's planner gives the five parts with the rows and counts the script works
  from the Copies, and the size check skipped as the script expects.
- **The window**, read as source: every attribute `press_print` and the methods it reaches read on the window or its
  strip is one DeskP, Desk9 or W8's Desk gives, read from their sources; without DeskP's body the check fails.
- **The strip's own form** (Tk): Coupon_A's span row drawn; its record written by the form's `_write_sidecar`; pressed
  with SAVE_AS_COPY None (GATE_COPY, nothing submitted, no bar line), STEP_EXPORT_ON_2026 None (GATE by year), the gate
  open (the bar names the file, one job submitted, its answer finished by the form's own `_collect_build`: C's status
  and the list written into the folder), no `.gear.json` (NO_RECORD) and an assembly active (NOT_A_PART, naming it).

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
rem SolidWorks 2026: all five in one invocation (about 31 min)
python.exe RUN\snap\probe\f2_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\f2-demo-sw2026-1.log ^
    --sections gates,form,workbook,refusals,userwork ^
    --user-master <probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master

rem SolidWorks 2024, the confirming build: userwork first, in a fresh session, WSL idle (about 14 min)
python.exe RUN24\snap\probe\f2_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\f2-demo-sw2024-1.log ^
    --sections userwork --close-outlived-whats-wrong ^
    --user-master <probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master

rem then the rest, in a fresh session (SolidWorks 2024 grows by 3 to 7 GB over a RangeBox Update; about 34 min)
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

Taken from `F2-DEMONSTRATION-REVIEW.md`: M1, S1 to S6 and the nit, in `2e5f7f5` and the commit after it. The points to
look at hardest: DeskP's restatements (none but the worker), `refused` and `written` as the only judges of a press,
the calls expected per way, the suppressed component left a fact, NEW_REVISION's G4 Flank edit (expected to name
OutputGear alone, as W9d's Sun was), and the user's features in a written part's list read by the script as the
features named User… (every feature of the user's here is W9a's keyway).

## The first run on SolidWorks 2026 (2026-11-18, from b3fe4a1, SolidWorks 2026 34.1.1)

**Setup.**
- Run folder `<probe folder>\f2-demo-sw2026-20261118-114738`, `snap` a `git archive` of `b3fe4a1` with `SNAPSHOT_COMMIT`
  beside `src` (the log's head names it, 2). `--self-check` on the snapshot, under the run's `python.exe`: 35 ok,
  0 failed.
- One session, PID 33080, started in the background for the run with nothing open, and exited after it (`taskkill`
  without `/F`: SolidWorks' own close; nothing was open by then). Before it, `tasklist` showed no SLDWORKS.exe, no
  Excel and no python.exe (only SolidWorks' two `sldworks_fs.exe` services, running before and after). The run started
  and quit its own Excel (PID 40868).
- Master, only copied: W9a's `setup.master` (`<probe folder>\w9a-final-sw2026-20261117-023433\out`). **The masters'
  hashes are the runner's statement, taken outside the script, and are not in the logs**: from WSL, in `<probe folder>`,
  `find w9a-final-sw2026-20261117-023433/out/setup.master w9a-confirm-sw2024-20261117-002313/out/setup.master -type f
  -exec sha256sum {} + | sort -k2` (34 files), taken before the 2026 run, between the versions and after the 2024 run;
  the three outputs matched exactly.
- **Nothing written outside the run folder**, also the runner's statement: a listing of `<probe folder>` outside the run
  folders (48,537 entries, each path, size and modification time) taken before each version's run and after it was
  the same both times, and nothing in the user's Documents or Desktop (two levels down, the probe folder aside) was
  newer than the 2026 run's start once both versions were through. The app's settings went to `out\appdata` (3).
- One invocation, `--sections gates,form,workbook,refusals,userwork --user-master …`, no close flag. Log
  `probe/results/f2-demo-sw2026-20261118-1-gates-form-workbook-refusals-userwork-clean.log`, JSON
  `f2-demo-20261118-114919.json`. Line numbers below are that log's.
- SolidWorks time about 13 min (11:48 to 12:01), of which the run 11.6 min (11:49:19 to 12:00:56), against the 31
  estimated.

| Section | Time | ok | FAIL | STOP | SolidWorks private, peak logged | Free, least logged |
|---|---|---|---|---|---|---|
| gates (with the user parts) | 59 s | 36 | 0 | 0 | 0.93 GB | 8.24 GB |
| form | 68 s | 44 | 0 | 0 | 0.95 GB | 8.13 GB |
| workbook (the printed 12 : 1 built here, 79 s) | 162 s | 91 | 0 | 0 | 1.47 GB (after the build) | 7.91 GB |
| refusals | 132 s | 110 | 0 | 0 | 1.61 GB (the bore Update) | 7.96 GB |
| userwork | 273 s | 54 | 0 | 0 | 1.56 GB (after the Update) | 8.07 GB |

Plus the run's own check that APPDATA is in the run folder (3): 336 ok, 0 failed, 1 noted (the herringbone's verdict),
0 STOPs (1674). **The script needed no fix**: nothing in `probe/f2_demonstration.py` changed for this run or the 2024
one.

**gates.** The six findings read the review's values and EXTENT_MEASURED True, the route `walk` (11-17); the gate
open as they stand (18). As they stand, the form's press wrote Coupon_G.step (134) and the window's, with the
12 : 1 written and not built, said *Print files wrote nothing: G1, G2, G3 and G4 have no part yet; build them first,
then print.*, nothing submitted (136-139). `SAVE_AS_COPY` None in this process only: on the form and in the window
*Print files waits until writing a STEP file is measured on this SolidWorks; nothing was written.*, the bar naming no
file, nothing submitted, no press folder, the documents as they were (141-154). `STEP_EXPORT_ON_2026` None: *Print files
waits until writing a STEP file is measured on SolidWorks 2026 (34.1.1); nothing was written.* on both (156-169). Each
patch put back and said (154, 169). The job's own gate, the form's plan read as for 32.5.0: *SolidWorks changed since
Print files was pressed (2024 (32.5.0) then, 2026 (34.1.1) now): press it again. Nothing was written.*, the job's calls
by member `{}` (172-173).

**form.** Coupon_A (module 1.5, 20 teeth, face 8, bore 8, Printed) built by the form with the user's Housing behind.
The Derived panel shows *Span over 3 teeth* `11.209`; the script's W 11.2088 and package A's 11.2088 (273). Each of
the two presses judged whole (276-286, 289-299): the bar named the file; written and checked by the app, the active
document restored, no flag turned on; one new folder each (`2026-11-18 11.50.36`, then `… 11.50.37`) holding the
STEP file and the list alone, the earlier one byte for byte; the status *Print files wrote Coupon_A.step and its print
list in C:\…\out\form\print\2026-11-18 11.50.36.*; the file AP203 (`CONFIG_CONTROL_DESIGN`), `MILLI.METRE`, one
closed solid, 344 vertices reaching radius 16.501185 over 8.000031 (the gear's 16.5 and 8), the app's fact
`checked` (282-283); the list (*Process: Printed, 0.4 mm nozzle*, *print 1*, *Span over 3 teeth: 11.209 mm (the
calipers square to the axis, at mid-face).*, *Checked: one closed solid, AP203 (CONFIG_CONTROL_DESIGN), millimetres;
outer diameter and face width match the gear.*, the settings once); no document opened, closed, renamed or marked and
no `.SLDPRT` changed; the job's calls `{'SaveAs': 1}`. The second press's file is the first's part, the same 344
vertices one to one within 1e-4 mm (300). The printed helical (m_n 2, z 20, β 15°, face 10): span 3 teeth `15.097`
against W_n 15.0972 (409); written and held the same way, radius 22.705524 over 10.000000 against d_a / 2 22.705524
(418-419). The printed herringbone (face 20): span `15.097`; written, judged structurally, the app's fact *skipped:
herringbone* and the list *size not checked (a herringbone, not yet measured).* (543-544).

**The herringbone's reading and its verdict** (547-548, JSON `form.herringbone`): the script's own reading, radius
22.70552360820168 over 20.0 along Z against d_a / 2 22.70552360820166 and the face 20.0: **holds** to 0.01 mm (to
about 1e-13 mm in fact), logged as a NOTE for the ruling on `"herringbone"` in `printout.EXTENT_SKIPPED`. 480
vertices, one closed solid.

**workbook.** The printed 12 : 1 built by the app's own Build (1065, 79.3 s, turning, no interference) and kept as
`f2-reducer.master`; a copy opened as the app opens one, nothing marked by the open (1086-1091). The six points
F2-PROBES-REVIEW §4 asked, which the probe did not show:
1. *Component-only press.* Every part read `Visible` False, the assembly in its own window, the user's Housing active
   (1100). The press wrote all four (1105), the job calling `{'SaveAs': 4}` and nothing that opens or activates (1118),
   so each by the job's own handle (the walk); the documents, flags, windows and the active document as before (1117);
   the list's rows, counts and spans *For G1 · print 1* … (1116); every component of the assembly read by name, each
   resolved after (1120).
2. *GLOBALS_DIFFER off a part not active.* G2, a component only, Face Width 16 saved and its window closed (read back
   Visible False, 1124): *Print files wrote nothing: in Gear_m1.5_N68_P, "Face Width" is 16 where its record says 15;
   press Update values (Update SolidWorks in the Workbook window), or put it back, then print.* (1127), refused in the
   job with no call that opens, activates, saves or writes (1130). G1 open in its own window behind the user's part,
   changed and not saved (Visible True, flag on, not active, 1136): MODIFIED, *Print files wrote nothing: Gear_m1.5_N17_P
   is changed in SolidWorks and not saved; save it, or close it without saving, then print.* (1139); saved: GLOBALS_DIFFER
   with *16 where its record says 15* (1146).
3. *A part open in its own window, not active.* G1 put back and saved, its window left open: the press wrote the set by
   G1's object, `{'SaveAs': 4}` and nothing activated, the user's part active after (1156-1169).
4. *A lightweight component* is in `refusals` below.
5. *The size check on every part of the 12 : 1*: each file `checked` by the app and held by the script, radius 14.251195,
   52.500051, 19.001573, 53.000076 against 14.25, 52.5, 19, 53; faces 15, 15, 20, 20 to 3e-5 mm (1108-1115); the
   herringbone as above.
6. *A part the job opens itself.* The copy closed, the user's part alone open: four written, the calls `{'ActivateDoc3': 4,
   'OpenDoc6': 4, 'CloseDoc': 4, 'SaveAs': 4}`, nothing of the copy left open and the user's part active after
   (1176-1189).

The open-beside fallback, `STEP_EXPORT_FROM_COMPONENT_ON_2026` False in this process only (1191, put back 1209): four
written with the same calls as point 6 (1208), every component read and resolved after the closes (1211).

**refusals.** Each refusal in C's words exactly, no press folder, no SolidWorks file changed, the documents as they were,
and for a refusal in the job no call that opens, activates, saves or writes; for one at planning, nothing submitted.
- *The form, on Coupon_R.* Face Width 9 not saved: *Print files wrote nothing: Coupon_R is changed in SolidWorks and not
  saved; save it, or close it without saving, then print.* (1317). Saved: *Print files wrote nothing: in Coupon_R, "Face
  Width" is 9 where its record says 8; press Update values (Update SolidWorks in the Workbook window), or put it back,
  then print.* (1325). The form's own **Update values** set it back to 8 and rebuilt (1332); saved; the press wrote a
  folder of its own, held whole (1337-1344). The user's keyway cut and saved (1346-1347); the script reads *User Keyway
  Sketch* and *User Keyway* top-level (1348); the press wrote, the app's fact *skipped: user features*, and the list
  *Your features left in it: User Keyway Sketch and User Keyway.* with *size not checked (your features in it).*
  (1352-1357). An Output folder that does not exist: *Print files wrote nothing: the output folder
  C:\…\out\refusals\no such folder does not exist; make it, or choose another, then print.*, the folder not made
  (1363-1367). The user's Sprocket active: *Print files prints a part Gear Generator built: Sprocket.SLDPRT has no .gear.json
  beside it, so nothing was written.* (1371).
- *The window, on a copy of the printed 12 : 1* (copied from `f2-reducer.master`, 1377). G4's component set lightweight
  (reads 1, 1396): *Print files wrote nothing: OutputGear is not open where Print files can reach it while Reducer_12to1 is
  open: it may be a lightweight or suppressed component of it, or simply closed; resolve it there, or open the part
  itself, then print again.* (1399); after the press still 1, the others 2 (1404). **Suppressed (state 0), the fact:**
  the job did not find the part, and the app met it with the same LIGHTWEIGHT sentence, held exact (1407-1414); no
  window came. The user's keyway in G1's part and a quiet Update (10.0 s, `{'OpenDoc6': 7, 'IsSuppressed2': 9}`) recorded
  it, the inventory listing *User Keyway Sketch* and *User Keyway* (1431); the press wrote the set, G1's fact *skipped:
  user features* and its block naming both, the other three `checked` (1435-1448). G4's Flank typed *arcs*:
  *Print files wrote nothing: the workbook's changes to OutputGear need a new revision, which Update SolidWorks cannot
  make; press Build again…, then print the new revision.* naming OutputGear alone (1461-1463); the cell cleared, nothing
  planned again (1478). G1's Bore typed 14: *Print files wrote nothing: Update SolidWorks would change the values in
  Gear_m1.5_N17_P; press Update SolidWorks and save, then print.* (1492). Update SolidWorks (8.0 s): ok, the User Keyway
  in error in G1's part, nothing of the app's (1502-1508); the record marks G1's part alone unsaved: *Print files wrote nothing:
  Gear_m1.5_N17_P has changes from Update SolidWorks that are not saved; save it in SolidWorks, then print.* (1509-1511).
  Saved as the person saves: *Print files wrote nothing: in Gear_m1.5_N17_P, User Keyway is in error in SolidWorks; fix
  it there, then print.*, G1 never activated (1517-1523).
- *The user's pair open, the copy closed* (Pair_m1.5_25T_50T built, 1527): *Print files wrote nothing: Gear_m1.5_N17_P,
  Gear_m1.5_N68_P, Gear_m2_N17_P and OutputGear are not open where Print files can reach them while Pair_m1.5_25T_50T is
  open: they may be lightweight or suppressed components of it, or simply closed; …* (1530): they were simply closed
  (1534). The form with that assembly active: *Print files prints the part active in SolidWorks, and
  Pair_m1.5_25T_50T.SLDASM is not a part: make a gear part active there; nothing was written.* (1537).

**userwork.** The master's record at link 7, no part saying a process (1545); the blank Process read Machined
(1567); the user's five components (1569); the User Keyway in Sun's part at code 0 (1571); the script reads *User Keyway
Sketch* and *User Keyway* in Sun's part and nothing of the user's in the other four (1573).
- *As built, Machined:* five written, `{'SaveAs': 5}` (1576-1591); the list *Process: Machined*, each block *Machined …
  no span*, Planet *print 3*, the dogs *print 2*, Sun's size skipped for the user's feature and named, the ring's, dog's
  and sleeve's skipped by kind, the Planet's checked (radius 9.375840 against 9.375) (1589).
- *Printed typed* on the Box sheet; Update plans the five parts in place (1612); the press before the Update: *Print files
  wrote nothing: Update SolidWorks would change the values in Gear_m1.25_N29, Gear_m1.25_N13, Ring_m1.25_N55,
  Dog_m1.25_N17 and Sleeve_m1.25_N17; press Update SolidWorks and save, then print.*, nothing submitted (1614).
- *One Update SolidWorks* (172.7 s, the same calls by member as F1's 2026 press, 1624): ok, nothing of the user's in
  error (1631); the five marked unsaved (1632); the press: *Print files wrote nothing: Gear_m1.25_N29, Gear_m1.25_N13,
  Ring_m1.25_N55, Dog_m1.25_N17 and Sleeve_m1.25_N17 have changes from Update SolidWorks that are not saved; save them in
  SolidWorks, then print.* (1634).
- *Saved; the press:* the five written and nothing else, `{'SaveAs': 5}` (1643-1658); the list printed: Sun *Span over 4 teeth:
  13.141 mm*, *Your features left in it: User Keyway Sketch and User Keyway.*, *size not checked (your features in it)*;
  the Planet *print 3*, *Span over 2 teeth: 5.481 mm*, checked; the ring and the sleeve *No span: internal teeth are
  measured over pins, not jaws.*; no feature line in the other four (1656).
- *The user's work neither exported nor touched:* no file of Sprocket or Housing in the press folder (1659); the record
  file unchanged (1660); the user's part files unchanged (1661); every document, flag and window as before with RangeBox
  active, no SolidWorks file saved by the press (1657); the user's components there after; every one of the eight user
  mates joins what it joined before (1664); the User Keyway at code 0 after (1665).

**Windows.** No dialog during a job but SolidWorks' progress boxes: *Opening* (1385), an untitled *Post load updating*
box at the copy's reopen (1417) and at RangeBox's open (1568), *Calculating Interference Detection* (1526). Two balloon
tips logged as facts (8, 21). No What's Wrong (none is expected on 2026), though the bore Update put the user's keyway
into error.

**Facts logged.**
- The farthest vertex beyond d_a / 2: the coupons and G1 1.2e-3 mm, G3 1.6e-3, G2 5e-5, OutputGear 8e-5, Sun 9e-4 and
  the Planet 8e-4; past the face 2e-5 to 3e-5 mm; the helical and the herringbone neither (to 1e-6). All within the
  0.01 mm tolerance; F1 measured the same tip excess on 2026's solids (1.1e-3 mm).
- The list writes OutputGear's span *33.62 mm*, the app's number style dropping the trailing zero; the script held it
  as C's own.
- *Script nit, judged nowhere:* the fact lines for RangeBox's parts give *the gear's … and 10.0* as the face for every
  part (`rangebox_expect`), the dog's included, whose part is 5 mm thick (read 5.000025; the list says *face 5 mm*).
  The script makes no size reading of its own where the radius is None, so nothing is judged on that figure; left as
  it ran, so the committed log matches the script.

## The confirming run on SolidWorks 2024 (2026-11-18, from b3fe4a1, SolidWorks 2024 32.5.0)

**Setup.**
- Run folder `<probe folder>\f2-demo-sw2024-20261118-120146`, `snap` a `git archive` of `b3fe4a1` with
  `SNAPSHOT_COMMIT` (log heads 1:2, 2:2). `--self-check` on the snapshot: 35 ok, 0 failed.
- Two sessions, each started fresh in the background with nothing open and exited after (`taskkill` without `/F`):
  PID 46964 for `userwork`, then PID 45812 for the rest. The 2026 session had exited first; one SolidWorks at a time.
  Each invocation started and quit its own Excel.
- Master, only copied: W9a's 2024 `setup.master` (`<probe folder>\w9a-confirm-sw2024-20261117-002313\out`), hashes
  unchanged and nothing written outside the run folder (the runner's statements above).
- Both invocations with `--close-outlived-whats-wrong`; `userwork` first with WSL idle but for a process check and a
  log grep every 15 s. The close path never acted.
- Logs `probe/results/sw2024/f2-demo-sw2024-20261118-1-userwork-clean.log` (JSON `f2-demo-20261118-120326.json`) and
  `…-2-gates-form-workbook-refusals-clean.log` (JSON `f2-demo-20261118-121309.json`); below, `1:` and `2:` are their lines.
- SolidWorks time about 20 min (12:02 to 12:21), of which the runs 15.5 min (12:03:26 to 12:11:14, 12:13:09 to
  12:20:54), against the 48 estimated.

| Section | Run | Time | ok | FAIL | STOP | SolidWorks private, peak logged | Free, least logged |
|---|---|---|---|---|---|---|---|
| userwork | 1 | 465 s | 54 | 0 | 0 | 6.21 GB (after the Update; 2.30 at the section's end) | 8.22 GB |
| gates | 2 | 57 s | 36 | 0 | 0 | 1.40 GB | 8.45 GB |
| form | 2 | 73 s | 44 | 0 | 0 | 1.70 GB | 8.32 GB |
| workbook (the 12 : 1 built here, 76 s) | 2 | 175 s | 91 | 0 | 0 | 3.81 GB (after the build) | 7.94 GB |
| refusals | 2 | 157 s | 110 | 0 | 0 | 7.18 GB (the bore Update; 7.13 after the quiet one) | 8.03 GB |

Run 1: 55 ok, 0 failed, 0 noted, 0 STOPs (1:143); run 2: 282 ok, 0 failed, 2 noted (the herringbone's verdict, the What's
Wrong box), 0 STOPs (2:1554). Free memory never under 7.9 GB, so neither floor came near.

**Every check reads as on 2026**, the same sentences word for word but for the version in GATE's and the job gate's,
line for line:
- *gates:* findings 2:11-17; the form wrote 2:133; NO_PART 2:135; GATE_COPY 2:143, 149; GATE by year *… measured on
  SolidWorks 2024 (32.5.0) …* 2:158, 164; the job's own gate, the plan read as for 34.1.1, calls none, 2:172.
- *form:* span 2:272, 408; the coupon's presses 2:278-285 (radius 16.500000 over 8.000009, 346 vertices), the same part
  2:299; the helical 2:418; the herringbone 2:542-543, its verdict **holds** (radius 22.705523608201677 over 20.0, 2:546-547).
- *workbook:* Visible False 2:1101; component-only 2:1106-1121 (`{'SaveAs': 4}`); G2 GLOBALS_DIFFER 2:1128; G1 MODIFIED 2:1140,
  GLOBALS_DIFFER 2:1147; G1 behind written 2:1157-1170; the job opening the parts 2:1177-1190; the fallback 2:1192-1212.
- *refusals:* MODIFIED 2:1318; GLOBALS_DIFFER 2:1326; Update values 2:1333, written 2:1338; the keyway 2:1349-1358; NO_FOLDER 2:1364-1368;
  NO_RECORD 2:1372; LIGHTWEIGHT 2:1397-1405; suppressed, the same sentence 2:1408-1412; the keyway recorded and the set written
  2:1431-1448; NEW_REVISION 2:1463; CHANGES_ON_UPDATE 2:1492; UNSAVED_MARK 2:1516; FEATURE_IN_ERROR 2:1525-1528; the pair's
  LIGHTWEIGHT 2:1534; NOT_A_PART 2:1541.
- *userwork:* master 1:12; as built 1:46-61; CHANGES_ON_UPDATE 1:84; the Update (296.3 s, the same calls by member as on 2026)
  1:94, ok 1:101; UNSAVED_MARK 1:104; written 1:113-128; the user's work 1:129-135.

**Windows. One What's Wrong box, in the app's bore Update in `refusals`, as the note expected** (W9a's `box-k3`): up
9.55 s into the job with the worker in `ActivateDoc3`, owned by SolidWorks' frame, gone by itself 1.01 s later with
the worker in `GetNextFeature`, nothing closing it; none up at the job's end, the frame enabled (2:1499-1503). Under the
2024 rule a fact, not a STOP; it did not outlive its job, so the close path did nothing. The Update's status said
*SolidWorks may have shown its What's Wrong box for up to half a minute during the Update; nothing in it needed
answering.* (2:1507), a clause 2026's status does not have. Otherwise progress boxes only: *Opening* (1:22), the untitled
*Post load updating* box at RangeBox's open (1:38) and at each 12 : 1 copy's open (2:1089, 1395).

## What differs between the versions

Every check reads the same on both. Measured differences, none judged a fault:
- **The STEP files.** On 2024 every spur part reaches d_a / 2 exactly (to 1e-6) and passes the face by 8e-6 to 9e-6
  mm; on 2026 by up to 1.6e-3 mm and 2e-5 to 3e-5 mm (the facts above). Some files hold two or four more vertices on
  2024 (the coupon 346 against 344, G2 1162 against 1160, OutputGear 876 against 874, the ring 940 against 936); the helical
  (322) and the herringbone (480) are the same, and their radius 22.705524 on both. The files are AP203,
  millimetres, one closed solid on both.
- **What's Wrong** came in the bore Update on 2024 (up 1 s) and not on 2026, as the harness's rule read them
  (`swbuild.whats_wrong_shows_in_update` True on 2024, 2:7; False on 2026, 7); the status's extra clause follows it.
- **Time and memory.** RangeBox's Update 172.7 s on 2026, 296.3 s on 2024 (userwork 273 s and 465 s); SolidWorks 2024's
  private memory reached 6.21 GB after that Update, and 7.13 to 7.18 GB in run 2's `refusals` after the 12 : 1's quiet
  Update (from 2.50 at `workbook`'s end; 3.23 at `refusals`' end), against 2026's peak of 1.61 GB. Free memory stayed
  over 7.9 GB on both.
- The 12 : 1's build checks its gear mates' sense by the version's own route (2026 made again with the other Flip, 2024
  the probe's `ring_mate_sense`), both finding nothing turned round.

**Not measured by these runs**, beyond *What the script does not measure*: a What's Wrong that outlives its job (none
did; the close path was never used); either memory floor's STOP; the suppressed component met by any way but
LIGHTWEIGHT's sentence (on both versions the job did not find the suppressed part and refused it so); a STEP file in
Bambu Studio (the user's step).
