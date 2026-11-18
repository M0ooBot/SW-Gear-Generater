# F2's probe: what it asks, what proposes which finding, and how to run it

The script is `probe/f2_probes.py`. It measures, before package B's job relies on it, the one call **Print files** adds
that the app has never made (PLAN-PRINTED §3.1.2): `IModelDocExtension.SaveAs` writing a part to a STEP file as a copy.
It writes a file, and could raise a dialog or rename a document, so by the house rule it is probed first, on both
versions. It proposes findings in the log (`propose NAME = value  # evidence`) and in the JSON, and sets none; each is
set per version (`_ON_2026`, `_ON_2024`; `SAVE_AS_COPY` once) from the reviewed log, in a commit of its own that is
reviewed too (`F2-INTERFACES.md` §7). Written by F2-0 against the plan revised to F2's review and its re-check (the last
two sections of `docs/PLAN-PRINTED-REVIEW.md`); **not yet run anywhere**: only `--self-check` and `--help` have run.

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
| | 5 | the spur exported again onto (2)'s file: overwritten or not (a fact; the app never asks it to), and its text against (2)'s, **the determinism control**: two exports of one document the same but for `FILE_NAME` | (the control for 6) |
| | 6 | the helical activated; the spur, open in its own window but not active, made the build document by `use_open_document` (the app's route, no activation) and exported by its own object; **the file is right** when its text is (2)'s but for `FILE_NAME` and not (4)'s; the active document, its title and every flag held. Before the export, the spur's window is read while the helical is active (a part in its own window, not active: M1) | `STEP_EXPORT_NEEDS_ACTIVE`; the window read into `PART_WINDOW_READ` |
| | 8 | the spur's Face Width set to 9 (`set_global_variable`) and rebuilt, not saved; activated and exported: whether its flag stays on, its path unchanged, and the file holds the changed solid (its text not (2)'s, its axial extent 9). Facts: the app refuses an unsaved part by ruling (open point 6) whatever this shows | |
| | 9 | everything of `f2-export` closed unsaved under the watch; the user's documents as at the start | |
| `component` | built | a printed pair, 25 / 50 at module 1.5, fixed (`Pinion_m1.5_N25_P`, `Gear_m1.5_N50_P`, `Pair_m1.5_25T_50T_P`), built in `f2-component` and closed (saved by the build) | |
| | loaded | the assembly opened alone by `Session.open_document`, so both parts are loaded only as its components: the assembly read unmarked; the components' states; **whether the document walk** (`GetFirstDocument` / `GetNext`, what `use_open_document` walks) **reaches a component-only document**; the window reads (`IModelDoc2.Visible`, `ActiveView`) of the assembly and both parts; `ISldWorks.GetOpenDocumentByName` by full path for the gear, the pinion and a file that does not exist, and by file name only for the gear | |
| | 7a | the gear reached by `GetOpenDocumentByName(<path>)` and exported by that object, nothing activated: the assembly's path, title and flag, the active document, the gear component's state, the gear's own document and every flag before and after | with 7c, 7d: `STEP_EXPORT_FROM_COMPONENT` |
| | 7b | **the fallback**: the gear opened in its own window by `Session.open_document` (OpenDoc6, warning 128, then ActivateDoc3); the window reads with it open (the gear active, the assembly not); exported; closed by `CloseDoc` on its title; then whether the assembly is still open, its flag as it was, the component's state as it was, the gear still loaded (walk, window read, `GetOpenDocumentByName`), which document is active; then the assembly activated again, as the job puts the user's document back | with 7c, 7d: `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN` |
| | 7d | everything closed; the gear opened alone and exported **twice** (the reference and its determinism control), then the pinion opened and exported once (the file that must differ); **the gear's window read while it is open in its own window and the pinion is active** (M1); `GetOpenDocumentByName` on the gear open alone (it must answer, the part's own path) and closed (it must answer None): the read's two controls. 7a's and 7b's files are then judged against the reference and said, and `PART_WINDOW_READ` proposed, all before 7c, so a hang in 7c cannot void them (S2) | `PART_WINDOW_READ` (from every window read) |
| | 7c | **lightweight**, last (the re-check's should-fix; run after 7d by F2-0-REVIEW's S2): the assembly opened again (`open_document`); the gear's component set lightweight by `SetSuppression2` (as W9a's `lightweight` did; it marks the assembly, a fact); whether the walk and `GetOpenDocumentByName` still reach a document; if one, exported by it; then the not-open path as the job takes it (opened beside, exported, closed), the assembly open after, the component's state after; then set resolved again | (into 7a's and 7b's proposals) |
| | 9 | everything of `f2-component` closed unsaved; the user's documents as at the start | |

## Which answer proposes which finding

Each judgement is a pure function, held by `--self-check` on made-up readings, every failing way shown (109 checks,
0 failed, after F2-0-REVIEW's M1, S1 and S2).

- **`SAVE_AS_COPY`** (`save_as_copy_proposal`): `swSaveAsOptions_Copy`'s value, proposed only when `swSaveAsOptions_Silent`
  reads 1, the `SAVE_AS_SILENT` the app holds (the positive control); else None, and the section exports nothing.
- **`STEP_EXPORT_ON_<year>`** (`step_export_proposal`): True when the spur's and the helical's exports were both clean,
  every one of these holding: SaveAs answered True, errors 0 and warnings 0, the file on disk and not empty, no window
  came, the document's path, title and save flag unchanged from an unmarked start, the active document unchanged, no
  folder or user document's flag turned on or closed; both files pass §3.1.4's frame check (the frame, an accepted
  AP, exactly one solid and a closed shell, no open shell, no surface model, a readable unit); **and the spur's file is
  the spur's size**, its largest radius from Z d_a / 2 (16.5 mm) and its axial extent the face (8 mm), each to 0.01 mm
  (F2-0-REVIEW's S1; the helical's extent stays a fact). Else None, with each reason.
- **`STEP_EXPORT_NEEDS_ACTIVE_ON_<year>`** (`needs_active_proposal`, `rightness`): False when step 6's file is right and
  its export clean, the active document (the helical) unchanged; True when it ran and the file was wrong (the
  helical's, or another geometry) or something changed; None when the run cannot tell: a window, a start already
  marked, step 5's control failed (two exports of one document differ beyond `FILE_NAME`), or the text differs from
  (2)'s with the same geometry (counts and vertices, a fact for the reviewer).
- **`STEP_EXPORT_FROM_COMPONENT_ON_<year>`** (`from_component_proposal`): True when `GetOpenDocumentByName`'s controls
  held (None for a file that does not exist and for the gear closed; the gear's own path when it is open alone), it
  reached the gear loaded as a component, the export was clean (as above, the assembly's path, title and flag and the
  component's state included, from an unmarked assembly), its file is the gear's own (7d's reference but for
  `FILE_NAME`, not the pinion's, with 7d's control holding), **and the lightweight component was either not reached by
  that route or reached and written right**. False when one of those was measured wrong; None when the run cannot tell.
- **`OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>`** (`open_beside_proposal`): True when 7b's `open_document` gave the
  gear, its export was clean (open_document's own activation aside), its file is the gear's own, and after `CloseDoc`
  the assembly is still open with its flag as it was (from an unmarked start), the component in the state it had, no
  user document marked, no window; **and 7c's not-open path** came under no window, left the assembly open and wrote
  the gear's own file. False when one was measured wrong, None when the run cannot tell.
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
