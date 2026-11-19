# F2's probe: what it asks, what proposes which finding, and how to run it

The script is `probe/f2_probes.py`. It measures, before package B's job relies on it, the one call **Print files** adds
that the app has never made (PLAN-PRINTED §3.1.2): `IModelDocExtension.SaveAs` writing a part to a STEP file as a copy.
It writes a file, and could raise a dialog or rename a document, so by the house rule it is probed first, on both
versions. It proposes findings in the log (`propose NAME = value  # evidence`) and in the JSON, and sets none; each is
set per version (`_ON_2026`, `_ON_2024`; `SAVE_AS_COPY` once) from the reviewed log, in a commit of its own that is
reviewed too (`F2-INTERFACES.md` §7). Written by F2-0 against the plan revised to F2's review and its re-check (the last
two sections of `docs/PLAN-PRINTED-REVIEW.md`); first run on SolidWorks 2026 and 2024 on 2026-11-18 (the run sections at the end).

**How it runs.** As W9c's and W9d's probes do: it runs W9a's script's `main` with its own two sections, through
`probe/w9c_probes.py` (imported for the watch, `swconst`, `in_build` and `part`). So the attach and PID check, the dialog
watch and the What's Wrong rule per version, keep-awake, the JSON after every section (`f2-probes-<time>.json`), APPDATA
in the run folder and the guarded close are W9a's, unchanged; `--close-outlived-whats-wrong` (SolidWorks 2024 only, the
coordinator's ruling of 2026-11-18) is W9c's own path, put in as F1's demonstration puts it. W9a's `main` starts its own
Excel and quits it; the probe asks nothing of it.

**No master.** Every part is built in the run's folder by the app's own routes (`gears.plan_for` and `swbuild.build`, as
the strip builds one gear; `pair.assembly_plan` and `swbuild.build_pair`, as the form builds a pair, fixed) and saved,
so every read starts from a saved, unmarked document.

**Nothing of the user's is touched; nothing is written outside the run's folder.** A document the run did not make is
logged as `<user document N>` (W8's `open_titles`); its save flag is read at each section's start and end and must be
as it was. Each section closes everything of its own folder unsaved (`QuitDoc`) under the watch. The only saves are the
builds' own, to new paths; every STEP file goes into the section's `print` folder. **No path is logged** but relative to
the run's output folder, and **no STEP header is logged**: a file's `FILE_NAME` holds an author and an organisation from
the session's settings, so the STEP files stay in the run folder and are not to be committed.

## Sections and steps

The plan's step numbers are kept; 7 is split (a) to (d), and step 8 (a part built into error) is not run, as the plan's
revision proposes.

| Section | Step | What it asks | Proposes |
|---|---|---|---|
| `export` | built | a printed spur gear (m 1.5, z 20, face 8, no bore, `Gear_m1.5_N20_P`) and a printed helical gear (m_n 2, z 20, β 15°, face 10, no bore, `Helical_m2_N20_15R_P`) built and saved in `f2-export`; both read unmarked | |
| | 1 | `swSaveAsOptions_e` (and `swFileSaveError_e`, `swFileSaveWarning_e` to name codes) read from the running install's `swconst.tlb`, after W9c's enumerations and their positive control; Silent held to `findings.SAVE_AS_SILENT` | `SAVE_AS_COPY` |
| | 2 | the spur, activated (`Session.activate`), exported by `SaveAs(<stem>.step, 0, Silent \| Copy, null, out errors, out warnings)` on its document: what it answers and in which form (a bool, or a tuple whose tail is the codes), both codes by name, the seconds, the file on disk and its size, any window; the document's path, title and save flag, the active document, every document of the folder's flags and the user's documents' flags read before and after | with 4: `STEP_EXPORT` |
| | 3 | the file read as text, never opened in SolidWorks (GOTCHAS §20): the frame; the FILE_SCHEMA and its AP **by its name's prefix**; `MANIFOLD_SOLID_BREP`, `CLOSED_SHELL`, `OPEN_SHELL`, `SHELL_BASED_SURFACE_MODEL` counted as instances; the length unit; from the `VERTEX_POINT`s the largest radius from Z and the axial extent against the app's d_a / 2 and face width, to 0.01 mm. Facts: nothing here is pinned per version (M2) | (evidence for §3.1.4's extent check) |
| | 4 | the helical part, as 2 and 3 | with 2: `STEP_EXPORT` |
| | 5 | the spur exported again onto (2)'s file: overwritten or not (a fact; the app never asks it to), its text against (2)'s (a fact: it differs, ruling 1) and **by geometry, the positive control**: two exports of one document the same part | (a control for 6) |
| | 6 | the helical activated; the spur, open in its own window but not active, made the build document by `use_open_document` (the app's route, no activation) and exported by its own object; **the file is right** when it is the same part as (2)'s by geometry and not (4)'s (ruling 1), judged after step 8 once the run's controls are read; the active document, its title and every flag held. Before the export, the spur's window is read while the helical is active (a part in its own window, not active: M1) | `STEP_EXPORT_NEEDS_ACTIVE`; the window read into `PART_WINDOW_READ` |
| | 8 | the spur's Face Width set to 9 (`set_global_variable`) and rebuilt, not saved; activated and exported: whether its flag stays on, its path unchanged, and the file holds the changed solid (not the same part as (2)'s by geometry, its axial extent 9). Facts: the app refuses an unsaved part by ruling (open point 6) whatever this shows. **Then the comparison's controls** (ruling 1): (2) and (5) the same part; the spur against the helical (2, 4) and the 8 mm spur against the 9 mm (2, 8) not | the controls for 6 and for step 7 |
| | 9 | everything of `f2-export` closed unsaved under the watch; the user's documents as at the start | |
| `component` | built | a printed pair, 25 / 50 at module 1.5, fixed (`Pinion_m1.5_N25_P`, `Gear_m1.5_N50_P`, `Pair_m1.5_25T_50T_P`), built in `f2-component` and closed (saved by the build) | |
| | loaded | the assembly opened alone by `Session.open_document`, so both parts are loaded only as its components: the assembly read unmarked; the components' states; **whether the document walk** (`GetFirstDocument` / `GetNext`, what `use_open_document` walks) **reaches a component-only document**; the window reads (`IModelDoc2.Visible`, `ActiveView`) of the assembly and both parts; `ISldWorks.GetOpenDocumentByName` by full path for the gear, the pinion and a file that does not exist, and by file name only for the gear | |
| | 7a | the gear reached by `GetOpenDocumentByName(<path>)` and exported by that object, nothing activated: the assembly's path, title and flag, the active document, the gear component's state, the gear's own document and every flag before and after | with 7c, 7d: `STEP_EXPORT_FROM_COMPONENT` |
| | 7b | **the fallback**: the gear opened in its own window by `Session.open_document` (OpenDoc6, warning 128, then ActivateDoc3); the window reads with it open (the gear active, the assembly not); exported; closed by `CloseDoc` on its title; then whether the assembly is still open, its flag as it was, the component's state as it was, the gear still loaded (walk, window read, `GetOpenDocumentByName`), which document is active; then the assembly activated again, as the job puts the user's document back | with 7d: `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN`, for a resolved component only (ruling 2; the component's state read before) |
| | 7d | everything closed; the gear opened alone and exported **twice** (the reference and the comparison's positive control), then the pinion opened and exported once (its negative control); **the gear's window read while it is open in its own window and the pinion is active** (M1); `GetOpenDocumentByName` on the gear open alone (it must answer, the part's own path) and closed (it must answer None): the read's two controls. 7a's and 7b's files are then judged against the reference by geometry, only when 7d's and the export section's controls both held in this run, and `PART_WINDOW_READ` proposed, all before 7c, so a hang in 7c cannot void them (S2) | `PART_WINDOW_READ` (from every window read) |
| | 7c | **lightweight**, last (the re-check's should-fix; run after 7d by F2-0-REVIEW's S2): the assembly opened again (`open_document`); the gear's component set lightweight by `SetSuppression2` (as W9a's `lightweight` did; the assembly's flag read after, a fact); whether the walk and `GetOpenDocumentByName` still reach a document; if one, exported by it; then the not-open path (opened beside, exported, closed), the assembly open after, and **the assembly's save flag and the component's state after that close, as facts** (ruling 2); then set resolved again | into 7a's proposal (not reached, or right); facts for 7b's (ruling 2) |
| | 9 | everything of `f2-component` closed unsaved; the user's documents as at the start | |

## Which answer proposes which finding

Each judgement is a pure function, held by `--self-check` on made-up readings, every failing way shown (125 checks,
0 failed, after F2-0-REVIEW's M1, S1 and S2 and the rulings on the runs).

- **`SAVE_AS_COPY`** (`save_as_copy_proposal`): `swSaveAsOptions_Copy`'s value, proposed only when `swSaveAsOptions_Silent`
  reads 1, the `SAVE_AS_SILENT` the app holds (the positive control); else None, and the section exports nothing.
- **`STEP_EXPORT_ON_<year>`** (`step_export_proposal`): True when the spur's and the helical's exports were both clean,
  every one of these holding: SaveAs answered True, errors 0 and warnings 0, the file on disk and not empty, no window
  came, the document's path, title and save flag unchanged from an unmarked start, the active document unchanged, no
  folder or user document's flag turned on or closed; both files pass §3.1.4's frame check (the frame, an accepted
  AP, exactly one solid and a closed shell, no open shell, no surface model, a readable unit); **and the spur's file is
  the spur's size**, its largest radius from Z d_a / 2 (16.5 mm) and its axial extent the face (8 mm), each to 0.01 mm
  (F2-0-REVIEW's S1; the helical's extent stays a fact). Else None, with each reason.
- **When a file is right** (`same_part`, `comparison_controls`, `rightness`; the coordinator's ruling 1, 2026-11-18): it
  is the same part as its reference export and not the other part's, **by geometry, not text**. `part_geometry` reads
  the DATA section only, so the header (FILE_NAME, its time and author) and every entity's number and reference are
  left out, and gives the count of every entity kind, every CARTESIAN_POINT in millimetres (the vertices, the B-spline
  curves' and surfaces' control points, every axis placement's origin) and the radii of every circle, cylinder, sphere
  and torus. Two files are the same part when the counts are equal, the points are the same set one to one within
  `GEOMETRY_TOL` 1e-4 mm (a point twice must be there twice) and the radii agree within it. **Why two different parts
  cannot pass:** a solid's faces are its surfaces and its edges its curves, each placed by a point or shaped by control
  points or a radius, so a part of another shape or size moves at least one point or radius by its whole change (the
  9 mm spur moves its far face's points by 1 mm), or counts its entities otherwise (the helical against the spur). The
  run holds this on its own files before any file is judged: (2) and (5), and 7d's two exports of the gear, must be the
  same part; the spur against the helical (2, 4), the spur at 8 mm against 9 mm (2, 8) and the gear against the pinion
  (7d) must not. If any of those fails, or was not read in this run, no file is judged and the findings resting on one
  are proposed None. The tolerance is a hundredth of the extent check's 0.01 mm; the runs' own files agree exactly.
- **`STEP_EXPORT_NEEDS_ACTIVE_ON_<year>`** (`needs_active_proposal`, `rightness`): False when step 6's file is right and
  its export clean, the active document (the helical) unchanged; True when it ran and the file was wrong (the
  helical's, or another geometry) or something changed; None when the run cannot tell: a window, a start already
  marked, or the comparison's controls not holding.
- **`STEP_EXPORT_FROM_COMPONENT_ON_<year>`** (`from_component_proposal`): True when `GetOpenDocumentByName`'s controls
  held (None for a file that does not exist and for the gear closed; the gear's own path when it is open alone), it
  reached the gear loaded as a component, the export was clean (as above, the assembly's path, title and flag and the
  component's state included, from an unmarked assembly), its file is the gear's own (the same part as 7d's reference
  by geometry, not the pinion's, with the run's controls holding), **and the lightweight component was either not reached by
  that route or reached and written right**. False when one of those was measured wrong; None when the run cannot tell.
- **`OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>`** (`open_beside_proposal`): **for a resolved component only** (the
  coordinator's ruling 2): True when the gear's component read resolved before 7b, 7b's `open_document` gave the gear,
  its export was clean (open_document's own activation aside), its file is the gear's own, and after `CloseDoc` the
  assembly is still open with its flag as it was (from an unmarked start), the component in the state it had, no user
  document marked, no window. False when one was measured wrong, None when the run cannot tell or the component was not
  read resolved. 7c's beside path (a lightweight component, which opening the part resolves in the user's assembly) is
  facts only: the job refuses a lightweight component by name (`F2-INTERFACES.md` §5.2).
- **`PART_WINDOW_READ_ON_<year>`** (`window_proposal`; F2-0's addition, the coordinator's to rule): the first of
  `Visible` and `ActiveView` that reads True on every document seen in its own window (the assembly active, the gear
  opened beside and active, the assembly not active beside it, the gear open alone) **and on every part seen in its own
  window but not active** (the spur in step 6 with the helical active, the gear in 7d with the pinion active: the case
  the job reads it on, F2-0-REVIEW's M1), and False on every one seen loaded only as a component (both parts when the
  assembly is opened alone, the gear after its window closed); None when neither tells them apart, or when no part was
  read in its own window but not active.

**Facts, proposing nothing**: the file's schema, unit and extents, and whether the extent check holds on the spur, the
helical and the 50-tooth gear (the evidence §3.1.4's should-fix waits on); the overwrite (5); the modified part (8);
whether the document walk reaches a component-only document (the job's `use_open_document` route); `GetOpenDocumentByName`
by file name only; the active document after `CloseDoc`; the lightweight component's states.

**A dialog is a finding, not a failure.** Every export, open, close and lightweight step runs under W9c's watch
(`w9c_probes.watched`: logs class, caption, buttons and texts, never SolidWorks' frame title, never answers). A dialog
that came and went ends that step with a STOP line and its findings proposed None; a job that does not return in 120 s,
or a dialog that stays, ends the run with nothing closed or saved. The builds are waited for up to 900 s (the pair
1800 s) under W9a's run-long watch. On 2026 a What's Wrong box is the STOP; on 2024 the flag below applies W9c's ruled
close path, and none is expected (every part builds clean).

**Not run, as the plan proposes (step 8 of its first revision):** a STEP export of a part in error is not measured; the
app never makes one, since the job refuses a part with a feature in error before any export.

## Command lines

`<probe folder>` is the probe folder under the Windows account's Documents (`…\Documents\GearGeneratorProbe`). `RUN` is
the run's own folder there, `RUN\snap` a snapshot (`git archive`) of the commit being run with `SNAPSHOT_COMMIT` beside
`src`, as for every probe here; run its `--self-check` first (0 failed). Start SolidWorks in the background, fresh, with
no other SolidWorks running, and pass its PID. No master or part is needed: the probe builds what it needs.

**SolidWorks 2026** (this laptop's 34.1.1; about 10 minutes):

```
python.exe RUN\snap\probe\f2_probes.py RUN\snap\src RUN\out --pid PID --log RUN\f2-probes-sw2026.log ^
    --sections export,component
```

**SolidWorks 2024** (32.5.0, a fresh session; about 15 minutes):

```
python.exe RUN\snap\probe\f2_probes.py RUN\snap\src RUN\out --pid PID --log RUN\f2-probes-sw2024.log ^
    --sections export,component --close-outlived-whats-wrong
```

The times are estimates (two scratch builds and a pair, about a dozen exports and reads, the harness's start), inside
the plan's 12 and 18 minutes. A section this `RUN\out` already holds is skipped; `--redo` runs it again, or
`--sections component` alone after a fresh SolidWorks (the component section reads `swconst.tlb` itself when run alone).

## What is untested

Everything that touches SolidWorks: the script has run only as `--self-check` and `--help`, and its live module was
imported on Linux with the Windows modules stubbed (its names resolve). Resting on the API help or on other programs'
use, unverified here:

- `IModelDocExtension.SaveAs` with `_null_dispatch()` and two `_out_long()`s through this app's session (the Airfoil
  Converter used the same helpers on 2026), and which form it answers in;
- `ISldWorks.GetOpenDocumentByName` by full path and by file name; `IModelDoc2.Visible` as a property get, and
  `ActiveView` answering None for a document with no window;
- `CloseDoc` on a part's own window while an open assembly holds it as a component; `Session.activate` on a part;
- `SetSuppression2` lightweight on a component of a fresh two-part assembly (W9a set one in RangeBox);
- the STEP parser on SolidWorks' own files (only on made-up texts): its complex unit instance, its FILE_NAME wrapping,
  whether its exports of one document repeat to the byte but for FILE_NAME (the controls in 5 and 7d say), and whether a
  part's vertices give d_a / 2 and the face width (the helical's tip corners are vertices of its swept faces);
- a printed spur and pair built with no bore (W9's fixtures all had bores).

## The plan's points this probe takes

| Point | Taken |
|---|---|
| §3.1.2 scratch only, nothing of the user's touched, titles and save flags read first and last | the sections' brackets and `closing` |
| step 1 to step 7 as written, step 8 dropped | as the table above |
| step 6's "the file is right" defined (F2's review) | `rightness`, with step 5 as its control |
| M5, the component case, with a measured fallback | 7a, 7b |
| re-check: the schema by its prefix | `schema_ap`, held to `printout.STEP_SCHEMAS` in the self-check |
| re-check: `GetOpenDocumentByName` unverified and new | measured in "loaded", 7a, 7b, 7c, 7d, with two controls, beside the walk |
| re-check: lightweight components | 7c, in both component proposals |
| re-check: the extent check beside the user's features | a fact here; the rule is `F2-INTERFACES.md` §2.4 |

## After F2-0's review (`0c4b7c3`)

- **M1**: `PART_WINDOW_READ` is proposed only with readings of a part open in its own window but not active (step 6, the
  spur; step 7d, the gear with the pinion active), held by `window_proposal`'s third list; the self-check shows it None
  with no such reading and a background window reading `Visible` False ruling `Visible` out.
- **S1**: `STEP_EXPORT` needs the spur's size check to hold; the self-check shows a wrong size and an unread one each
  None, and the helical's extent as a fact only.
- **S2**: 7c runs last, after 7d, opening the assembly itself; 7a's and 7b's files are judged and `PART_WINDOW_READ`
  proposed before it. `STEP_EXPORT_FROM_COMPONENT` and `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` still wait on 7c, as their rule
  is.
- **S3** (an inch file's two length units) is not changed here: the app writes millimetres, so the probe will not meet
  it; the coordinator's list for F2-0 did not include it, and the point stands for B's `check_step`.
- The command lines and times are unchanged.


## The run on SolidWorks 2026 (2026-11-18, from c764130; `export` again from e3dc598)

**Setup.**
- Run folder `<probe folder>\f2-probes-sw2026-20261118-100922`, on this laptop. `snap` a `git archive` of c764130 with
  `SNAPSHOT_COMMIT` beside `src`, its `--self-check` 0 failed and `import gear_generator` taken from `snap\src` before
  the run; `snap2` the same of e3dc598 (step 8's fix, below), checked the same way.
- SolidWorks 2026 revision **34.1.1**, PID 20700, a fresh session started for the run in the background, with no other
  SolidWorks, Excel or Python running; exited after (`taskkill` without `/F`, nothing open).
- Run 1: the command line above, both sections. Run 2: `--sections export --redo` from `snap2` in the same session, into
  the same `out` (run 1's folder set aside as `f2-export.prev-20261118-101341`), log `f2-probes-sw2026-2.log`.
- Logs `probe/results/f2-probes-sw2026-20261118-1-step8-fail-text-control-differs.log` (`r26:`) with
  `f2-probes-20261118-101100.json`, and `f2-probes-sw2026-20261118-2-export-step8-clean.log` (`r26b:`) with
  `f2-probes-20261118-101341.json`.

**Result.** Run 1: export 42 s, 1 failed (step 8, the script's own fault, below); component 59 s, 0 failed; no STOP.
Run 2: export 43 s, 0 failed, no STOP. About two minutes each from the attach to the close, against the 10 estimated.
SolidWorks stayed near 1.0 GB private; free memory above 9.2 GB. **Windows:** the *Simplified Interface* balloon tip at
the start (r26:9) and *The sketch is no longer over defined* balloon during the pair's build (r26:48), both exempt, and
the *Calculating Interference Detection* progress box once in the pair's build (r26:49); the watch logged no other
window (r26:80, r26b:51), and no export, open, close or lightweight step saw one.

**Each step, and what SolidWorks answered.**
- **built.** The spur and the helical built and saved by `swbuild.build`, both unmarked (r26:15-17); the pair built by
  `swbuild.build_pair` and closed (r26:50-51).
- **1.** `swSaveAsOptions_e`: Silent 1, Copy 2, 13 members; `swFileSaveError_e` 15 members, `swFileSaveWarning_e` 12
  (r26:18). W9c's enumerations' positive control agreed.
- **2.** The spur, active: `SaveAs` answered **True, plainly** (no tuple), errors 0, warnings 0, options 3, 0.495 s, the
  file on disk (909855 bytes); its path, title and flag, the active document and the folder's flags unchanged
  (r26:20-22). **3.** Its file: the frame whole; FILE_SCHEMA `CONFIG_CONTROL_DESIGN` (AP203); one
  MANIFOLD_SOLID_BREP, one CLOSED_SHELL, no OPEN_SHELL, no SHELL_BASED_SURFACE_MODEL; MILLI METRE; 340 vertices;
  largest radius 16.501185 mm against d_a / 2 = 16.5, axial extent 8.000031 against 8: the extent check holds at 0.01
  mm (r26:23).
- **4.** The helical, the same: True, 0, 0, 0.466 s, 1888148 bytes, everything unchanged; AP203, one solid, one closed
  shell, millimetres, 322 vertices, 22.705524 against 22.705524 and 10.000000 against 10 (r26:25-29).
- **5.** The spur again onto its file: True, 0, 0; the file **overwritten** (its time moved). **The control failed: the two
  exports of one document differ in 9092 of their statements**, FILE_NAME aside (r26:31-34; run 2: 9087, r26b:34).
- **6.** The helical activated; **the active-document label step 6 logs is `Helical_m2_N20_15R_P.SLDPRT`** at the window
  read (r26:35) and in the export's bracket before and after (r26:37-38), so the activation took and the spur's window
  read is a real reading of a part in its own window, not active: `Visible` True, `ActiveView` True. The spur, reached by
  `use_open_document` with no activation, exported by its own object: True, 0, 0, 0.405 s; the active document, every
  title and flag held (r26:36-38). Its file judged None, since step 5's control failed (r26:39).
- **8.** Run 1 FAILed before the export (r26:41): the change was made with the helical still active, and the Face Width
  equation's put read back unchanged, `'"Face Width"= 8' after being set to '"Face Width"= 9'`. The script did not
  activate the spur, which F2-0's decision 16 says it does: a fault of the script's (below). Run 2, with the spur
  activated first (r26b:41): the flag on after the change; exported, True, 0, 0; the flag stays on, the path unchanged,
  the file differs from the saved spur's and its axial extent is 9.000031 mm, the changed solid (r26b:42-45).
- **9.** Everything closed unsaved with no window; no user document was open (r26:42-43, 75-76; r26b:46-47).
- **loaded.** The assembly opened alone, unmarked, both components state 2 (resolved); **the document walk reaches both
  component-only parts**; window reads: the assembly `Visible` True, `ActiveView` True; both parts False, False
  (r26:52-53). `GetOpenDocumentByName` by full path gives each part (its path, title, flag False, window False/False),
  None for the file that does not exist, and **None for the gear by file name only** (r26:54).
- **7a.** The gear, reached by `GetOpenDocumentByName` with no activation, exported: True, 0, 0, 0.885 s; the assembly
  active, unmarked and its title unchanged, the gear unmarked, its component state 2 to 2 (r26:56-59). Its file judged
  None (the control, r26:67); the read's controls held (None for no such file and for the gear closed; the gear's own
  path open alone).
- **7b.** The fallback: `open_document` gave the gear active in its own window (`Visible`/`ActiveView` True; the
  assembly beside it True/True); exported True, 0, 0; after `CloseDoc` the assembly open and active, unmarked, the
  component 2 to 2, the gear still loaded (walk True, window False/False, `GetOpenDocumentByName` gives it); the assembly
  activated again (r26:60-63). Its file judged None (r26:68).
- **7d.** The gear alone exported twice: **the two differ beyond FILE_NAME** (the control failed); the pinion's differs;
  the gear's file AP203, one solid, 852 vertices, radius 39.000237 against 39, extent 8.000031 against 8, holds; with
  the pinion opened and active, the gear's window read `Visible` True, `ActiveView` True, the label logged
  `Pinion_m1.5_N25_P.SLDPRT` (r26:65-66, 69).
- **7c.** The assembly opened again unmarked; the gear's component set lightweight reads 1; **the assembly's flag read
  False after the set** (the log's words "marked by the set itself, a fact" are the script's expectation; the read says
  otherwise); **the walk does not reach the lightweight part, and `GetOpenDocumentByName` gives None**, so no export by
  object; the not-open path opened the gear, exported it (True, 0, 0, 0.809 s), closed it with the assembly still open;
  **the component then read 2, resolved, before the script resolved it** (opening the part beside resolved it) (r26:71).
  The assembly's flag after the close was not read. No window.

**The proposals** (none set):

| Finding | Proposed | Line |
|---|---|---|
| `SAVE_AS_COPY` | 2 | r26:19, r26b:19 |
| `STEP_EXPORT_ON_2026` | True | r26:30, r26b:30 |
| `STEP_EXPORT_NEEDS_ACTIVE_ON_2026` | None: step 5's control failed | r26:40, r26b:40 |
| `PART_WINDOW_READ_ON_2026` | `IModelDoc2.Visible` (`ActiveView` read the same everywhere; `Visible` is the first) | r26:70 |
| `STEP_EXPORT_FROM_COMPONENT_ON_2026` | None: 7d's control failed; the lightweight part not reached | r26:72 |
| `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_2026` | None: 7d's control failed | r26:74 |

## The run on SolidWorks 2024 (2026-11-18, from e3dc598)

**Setup.**
- Run folder `<probe folder>\f2-probes-sw2024-20261118-101515`, `snap` a `git archive` of e3dc598 with
  `SNAPSHOT_COMMIT`; its `--self-check` 0 failed and `import gear_generator` from `snap\src` before the run.
- SolidWorks 2024 revision **32.5.0**, PID 7268, a fresh session started in the background after 2026 had exited, no
  other SolidWorks, Excel or Python running; exited after.
- The 2024 command line above, both sections, `--close-outlived-whats-wrong` in force (the log's rule lines 8-9).
- Log `probe/results/sw2024/f2-probes-sw2024-20261118-1-clean-text-control-differs.log` (`r24:`) with
  `f2-probes-20261118-101657.json`.

**Result.** export 45 s, component 67 s, 0 failed, no STOP; about two minutes against the 15 estimated. SolidWorks
2024 grew to 2.85 GB private; free memory above 9 GB. **Windows:** one untitled box as the assembly opened again in 7c
(*Opened 2 Components*, *Post load updating*, *Elapsed time: 0s*, a Close button; r24:73), the open-progress box F1's 2024
runs saw, gone by itself; the watch counted no other window (r24:83), and 7c's own job logged none. **No What's Wrong
came**, so the close path did nothing.

**Each step reads as on 2026**, but for what the next section lists: SaveAs True plainly with errors 0 and warnings 0
on every export (r24:20, 25, 31, 36, 42, 58, 62; 7c in r24:74); everything held in every bracket; AP203
`CONFIG_CONTROL_DESIGN`, one solid, one closed shell, millimetres in every file read; the extent check holds on the
spur (16.500000 against 16.5, 8.000009 against 8, r24:23), the helical (r24:28) and the 50-tooth gear (39.000000,
8.000009, r24:67); step 5 overwrote the file and **its control failed, 9037 statements differing** (r24:34); **step 6's
active-document label is `Helical_m2_N20_15R_P.SLDPRT`** (r24:35, 37-38), the spur's window True/True, its export clean
(r24:36-38); step 8 with the spur active (r24:41) kept the flag on, the path, and wrote the changed solid, extent
9.000009 (r24:42-45); the walk reaches component-only parts, `GetOpenDocumentByName` reaches them by full path, None by
file name and for no such file (r24:54-56); 7a and 7b clean, the assembly unmarked, the component 2 to 2, the gear still
loaded after `CloseDoc` (r24:58-65); 7d's control failed, the gear's window True/True with the pinion active (r24:68,
71); 7c the same as 2026: lightweight reads 1, the assembly's flag False, neither the walk nor `GetOpenDocumentByName`
reaches the part, the beside path clean and the component resolved (2) after it (r24:74).

| Finding | Proposed | Line |
|---|---|---|
| `SAVE_AS_COPY` | 2 | r24:19 |
| `STEP_EXPORT_ON_2024` | True | r24:30 |
| `STEP_EXPORT_NEEDS_ACTIVE_ON_2024` | None: step 5's control failed | r24:40 |
| `PART_WINDOW_READ_ON_2024` | `IModelDoc2.Visible` | r24:72 |
| `STEP_EXPORT_FROM_COMPONENT_ON_2024` | None: 7d's control failed; the lightweight part not reached | r24:75 |
| `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_2024` | None: 7d's control failed | r24:77 |

## What differs between the versions

- `swSaveAsOptions_e` has 13 members on 2026 and 12 on 2024; Silent 1 and Copy 2 on both.
- The spur's file: 2026 writes 340 vertices with the largest radius 16.501185 mm and the extent 8.000031 (the 50-tooth
  gear 39.000237, 8.000031); 2024 writes 342 vertices on 16.500000 and 8.000009 (39.000000, 8.000009). Both within the
  0.01 mm tolerance. The helical reads the same on both. File sizes differ (the spur 909855 bytes against 887836).
- 2024 shows its open-progress box at the assembly's second open; 2026 does not.
- SolidWorks 2024 grows to 2.85 GB private in the run, 2026 stays near 1.0 GB.
- Nothing else: every answer, flag, window read, reach and judgement is the same.

## What the runs found that the probe did not foresee

- **SolidWorks' STEP exports of one document are not the same text twice.** On both versions, two exports of an
  unchanged document differ in nearly every DATA statement: the instances are numbered in another order each time (the
  first lines of the DATA section hold other entities at the same numbers), and the header's FILE_NAME time differs as
  expected. So the plan's definition of "the file is right" (§3.1.2 step 6: the text equal to step 2's but for
  FILE_NAME, F2's review) cannot hold for any export, the probe's controls in steps 5 and 7d fail as designed, and
  `STEP_EXPORT_NEEDS_ACTIVE`, `STEP_EXPORT_FROM_COMPONENT` and `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` are proposed None on
  both versions.
- **A hand diagnostic after the runs (not the probe's run; `geom_diag.py` in each run folder)** ran the probe's own
  pure `geometry_of` (instances counted by entity name, vertices in millimetres to 1e-6 mm) and `same_file` on the
  STEP files left in the run folders (the spur's step 2 file is step 5's, which overwrote it). On both versions:
  - step 5's file and step 6's have the same geometry, and step 6's differs from the helical's: **by geometry, step 6
    wrote the spur's own file** with the helical active, so the rule would read `STEP_EXPORT_NEEDS_ACTIVE` False;
  - step 8's file differs in geometry from the saved spur's (its vertices; its counts the same);
  - 7d's two exports of the gear have the same geometry and the pinion's differs; 7a's, 7b's and 7c's beside files each
    have the gear's geometry, not the pinion's. By geometry, the rule would read `STEP_EXPORT_FROM_COMPONENT` with 7a
    right and 7c's lightweight case not reached, and `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` with 7b and 7c right.
  This is evidence, not a proposal: the judgement the plan and F2-0's review fixed is textual, and changing it is the
  coordinator's to rule.
- **Setting a global by `set_global_variable` on a part reached by `use_open_document` while another part is active did
  not take** on 2026 34.1.1: the put read back unchanged (r26:41); with the part activated first it took (r26b:41,
  r24:41). Measured once, on one route; the app's own calls of `set_global_variable` were not examined here.
- **A lightweight component is reached by neither the walk nor `GetOpenDocumentByName`**, on both versions, and
  **opening its part beside the assembly resolves it** (state 1 before, 2 after the close), with no window and the
  assembly still open. The assembly's flag was not read after that close.
- **Setting a component lightweight did not mark the assembly** on either version (its flag read False after the set),
  where the note's table expected it to.

## Changes to the script in these runs

- **e3dc598, step 8 only.** The spur is activated (`Session.activate`) before its Face Width is changed, as F2-0's
  decision 16 says, and the active document at the change is logged. Evidence: r26:41 (the put read back unchanged with
  the helical active). No judgement and no check was changed; `--self-check` 0 failed. Run 1's component section ran
  from c764130 and stands, the change touching step 8 alone.

## For the coordinator to rule

- **"The file is right"**: the textual definition cannot hold on either version (above). Options: judge by geometry
  (`geometry_of`: instance counts by entity name and vertices to 1e-6 mm, the controls in 5 and 7d then two exports of
  one document geometrically equal, the other part geometrically different), which the hand diagnostic says would
  propose `STEP_EXPORT_NEEDS_ACTIVE` False and the two component findings from 7a, 7b and 7c on both versions; or
  another definition. Either needs the script changed, reviewed, and `export` and `component` run again on both
  versions (about 2 minutes each run here).
- Whether `set_global_variable` on a non-active part not taking matters to any of the app's routes.
- Whether the open-beside fallback resolving a lightweight component, a change of the user's assembly state, is
  acceptable for the job (F2-INTERFACES' lightweight rule), and whether the assembly's flag after that close needs
  reading.

## After the runs: the coordinator's rulings (2026-11-18) and the probe for its rerun

**Ruling 1: two STEP files are the same part when their geometry agrees, not their text.** The probe's judgement is now
`same_part` (above, *When a file is right*), held in the run itself to its controls: (2) and (5), and 7d's two exports of
the gear, the same part; the spur against the helical (2, 4), the spur at 8 mm against 9 mm (2, 8) and the gear against
the pinion (7d) not. Step 6's file is judged after step 8, whose file is one of the controls; step 7's files only when
both sections' controls held in this run (the component section alone judges nothing). Step 5's text comparison stays,
as a fact.

**Checked on the runs' own files** (read here, from WSL, in the two run folders; nothing written there): on 2026 and on
2024 alike, step 5's spur and step 6's file are the same part (2026: 59 kinds, 4698 points, 202 radii; 2024: 4429 points,
273 radii), the spur and the helical are not (26 entity kinds counted otherwise), the spur and the 9 mm spur are not (the
same counts, the points not one to one), the gear's two exports alone are the same part (10946 points, 504 radii on 2026;
10265 and 681 on 2024), the gear and the pinion are not, and 7a's, 7b's and 7c's beside files are each the gear's. So the
controls hold and the rerun should propose `STEP_EXPORT_NEEDS_ACTIVE` False on both versions, and the two component
findings from 7a and 7b, as the runner's `geom_diag.py` found; the rerun, not this check, is the evidence.

**Ruling 2: a lightweight component.** Opening its part beside the assembly resolved the component in the user's
assembly (state 1 to 2, both versions), a change to their session. The job refuses a lightweight component by name and
tells the user to resolve it or open the part (`F2-INTERFACES.md` §5.2, `LIGHTWEIGHT`). 7c now reads, after the
fallback's close, the assembly's save flag (`asm_after_close`) and the component's state, as facts, before the probe
resolves it; `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` is proposed only when the gear's component read resolved before 7b, and
no longer waits on 7c. `STEP_EXPORT_FROM_COMPONENT` still needs 7c's lightweight part not reached by the object route
(both runs: not reached).

**The self-check**: 125 checks, 0 failed, among them each new judgement's failing ways: a renumbered and reordered file
the same part, a point moved 5e-5 mm the same and 5e-4 mm not, another count, a point fewer, a circle's radius changed by
0.001 mm with every point kept, an unreadable unit and an unread file (cannot tell); a point twice, a cell's edge and 2D
points in `points_match`; a positive control failing, a negative control failing, a control not read and a missing side
in `comparison_controls`; `rightness` with the controls not holding or not read; `OPEN_BESIDE` with the component not
resolved or not read, and with any lightweight reading (facts only).

**The rerun's command lines** are the ones above, in a fresh `RUN` snapshotted from the commit that carries these
changes, both sections on each version: 2026 without and 2024 with `--close-outlived-whats-wrong`. About 2 minutes each,
as the first runs took.


## The rerun on both versions (2026-11-18, from d333ff8), to the coordinator's rulings

**Setup.**
- Both runs from one `git archive` of **d333ff8** each (F2-0's src with package A's span module; the probe of b49044f),
  `SNAPSHOT_COMMIT` beside `src`; each snapshot's `--self-check` read 0 failed (125 checks) and `import gear_generator`
  came from its own `snap\src` before the run. No script change was made.
- **SolidWorks 2026** 34.1.1, PID 17900, a fresh session started in the background with no other SolidWorks, Excel or
  Python running, exited after. Run folder `<probe folder>\f2-probes-sw2026-20261118-103409`; the 2026 command line
  above. Log `probe/results/f2-probes-sw2026-20261118-3-rerun-geometry-all-proposed.log` (`q26:`) with
  `f2-probes-20261118-103547.json`.
- **SolidWorks 2024** 32.5.0, PID 4624, a fresh session started after 2026 had exited, exited after. Run folder
  `<probe folder>\f2-probes-sw2024-20261118-103832`; the 2024 command line above, `--close-outlived-whats-wrong` in force.
  Log `probe/results/sw2024/f2-probes-sw2024-20261118-2-rerun-geometry-all-proposed.log` (`q24:`) with
  `f2-probes-20261118-104015.json`.
- Nothing new was written outside the two run folders (the account's folders searched for files changed since the
  first run began, and AppData for any part, assembly or STEP file); no user document was open.

**Result.** 0 failed and no STOP on either version (q26:88, q24:88). export 53 s and component 64 s on 2026, 46 s and
62 s on 2024. **Windows:** on 2026 the exempt *Simplified Interface* balloon (q26:9) and *The sketch is no longer over
defined* balloon in the pair's build (q26:53); on 2024 the untitled open-progress box (*Opened 2 Components*, *Post load
updating*, a Close button) as the assembly first opened alone (q24:55; in the first 2024 run it came at 7c's open
instead), gone by itself. The watch counted no other window on either (q26:85, q24:85); no What's Wrong came, so
2024's close path did nothing. SolidWorks 2024 reached 2.85 GB private, 2026 about 1.0 GB.

**The proposals**, every one of the six now proposed, the same on both versions:

| Finding | 2026 | 2024 |
|---|---|---|
| `SAVE_AS_COPY` | 2 (q26:19) | 2 (q24:19) |
| `STEP_EXPORT` | True (q26:30) | True (q24:30) |
| `STEP_EXPORT_NEEDS_ACTIVE` | False (q26:46) | False (q24:46) |
| `PART_WINDOW_READ` | `IModelDoc2.Visible` (q26:75) | `IModelDoc2.Visible` (q24:75) |
| `STEP_EXPORT_FROM_COMPONENT` | True, the lightweight part not reached (q26:77) | True, the same (q24:77) |
| `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` | True (q26:79) | True (q24:79) |

**The comparison's controls, read in each run, all held:**
- export (q26:44, q24:44): the spur's two exports (2, 5) the same part (2026: 59 entity kinds, 4698 points, 202 radii;
  2024: 59, 4429, 273); the spur against the helical not (26 entity kinds counted otherwise); the 8 mm spur against the
  9 mm one not (the same counts, the points not one to one within 1e-4 mm). Step 5's text still differs from (2)'s, 9093
  statements on 2026 and 9040 on 2024 (q26:34, q24:34), a fact.
- component (q26:69, q24:69): the gear's two exports alone the same part (2026: 10946 points, 504 radii; 2024: 10265,
  681); the gear against the pinion not (16 entity kinds counted otherwise). "The comparison's controls hold True"
  (q26:71, q24:71).
- `GetOpenDocumentByName`'s controls held on both: None for a file that does not exist and for the gear closed, the
  gear's own path when open alone (q26:72, q24:72).

**Each file judged:** step 6's the spur's own (q26:45, q24:45); 7a's and 7b's the gear's own (q26:72-73, q24:72-73); 7c's
beside file the gear's own, a fact only (q26:78, q24:78).

**Step 6's active-document label** reads `Helical_m2_N20_15R_P.SLDPRT` on both versions, at the spur's window read and in
the export's bracket before and after (q26:35-38, q24:35-38): the activation took, so the spur's `Visible` True /
`ActiveView` True is a real reading of a part in its own window, not active. 7d's reading has `Pinion_m1.5_N25_P.SLDPRT`
active (q26:74, q24:74).

**The lightweight step's facts (7c, q26:76, q24:76), the same on both versions:** the assembly opened again unmarked;
the gear's component set lightweight reads 1, and **the assembly's flag reads False after the set**; neither the walk nor
`GetOpenDocumentByName` reaches the part (None), so nothing is exported by object; the not-open path opened the gear,
exported it (True, errors 0, warnings 0), closed it, the assembly still open; **after that close the assembly's flag
reads False and the component's state 2** (resolved by the part's opening, before the probe resolves it; 2 again
after). No window.

**Read as in the first runs:** every SaveAs True plainly with errors and warnings 0, nothing marked or moved; AP203,
one solid, millimetres, the extent check holding on the spur, the helical and the gear (2026's spur 16.501185 mm, 2024's
16.500000); 7b's component read resolved before the open (q26:67, q24:67), the assembly unmarked and its component 2 to 2
after `CloseDoc`; step 8 with the spur active kept the flag on and wrote the changed solid, not the same part as the
saved spur, extent 9 mm (q26:39-43, q24:39-43). The differences between the versions are those of the first runs: 13
against 12 members of `swSaveAsOptions_e`, the vertex counts and 2026's 0.001 mm tip, file sizes, 2024's open-progress
box and its memory.
