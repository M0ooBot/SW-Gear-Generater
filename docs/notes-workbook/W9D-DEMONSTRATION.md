# W9d's demonstration on SolidWorks (M9): the sections, the gates, what each line bears out

The script is `probe/w9d_demonstration.py`. It covers ISSUE-1-PLAN §5's W9d *Done when* on SolidWorks:

- after Sun's Flank change and a shaft added, **Build again…** makes RangeBox_r2;
- both clusters are carried, their mates made again and on in the modes they were on in;
- the mate on Sun's face is named (the plan's "bore mate on Sun": RangeBox's Sun has no bore, so it is shown as a mate
  on Sun's end face, as W9D-INTERFACES §12 rules);
- the keyway in Sun is named in the question and the result;
- every app gear is free to turn in every mode;
- the carried items are left unsaved;
- the old assembly and every user file are unchanged on disk.

Around that it shows W9D-INTERFACES §15's further items: face mates, a gear mate of the user's on an app gear (on its
Gear Axis, on a root cylinder and on a root fillet), the parallel and limit kinds, states per mode, a lightweight
component, one suppressed in the mode showing, a component in a second configuration, a mate to the assembly's own
plane, the tied cluster's fallback, the not-open read, the record at schema 10 and the footer.

It is written to the Workbook window's path and the contract's fields, not to the packages' internals:

- every edit is typed in Excel by W8's `edit` (W9c's `edit_live`, from the fixtures' own rows);
- every Build again… goes through Desk9 with the window's `_start_build` as it now is: `old_assembly` as `before` and
  `carry_for` from that very object as `carry`, `job.revision` taken in the job, then the window's own `_finish_build`
  (`DeskD`, a Desk9 whose `build` is that one method);
- the fields read are W9D-INTERFACES §2.4's (`CarryResult`, with package A's `anchors`, `facts`, `changed_files`
  and `OldWork.walks`) and §7's (`CarryEntry`).

**How it runs.** It runs W9a's script's `main` with its own four sections, as W9b's and W9c's do, so it inherits the
attach and PID check, the dialog watch with the What's Wrong rule per version, keep-awake, the JSON after every section
(`w9d-demo-<time>.json`), APPDATA in the run folder, the guarded close, `--sections` and `--redo`. It imports W9c's
demonstration for the press, the edits and the record reads, W9b's for the per-mode judgement, and W9c's probes for
the raw mates on faces (`raw_mate`, `select_face`, `part_faces_of`). No document title but the run's own is logged,
and SolidWorks' frame never is.

**Masters:**

- `--master`: S0's `rangebox.master`, and `--user-master`: W9a's `setup.master` (RangeBox, Sprocket-1..4,
  Housing-1, their eight mates, the User Keyway in Sun's part). Each is built first where missing, by its own section.
- `--fixture-master`: this script's `w9d-fixture.master`, kept by `fixture` for the other three sections.
- `--other-version-file`: optional, a SolidWorks file the other version last saved (on 2026 a 2024 one), read closed
  only, for R.2's refusal (as the W9d probe takes it).

## The fixture (`fixture`)

A copy of `setup.master`, to which the script adds, all by the session's own calls (the app's `add_component`,
`add_mate` and `add_configuration`; the probes' `raw_mate` on faces):

| Handle | Name2 (as SolidWorks numbers them) | What it is for | Its mates |
|---|---|---|---|
| c1 | Chain-1 (`Chain.SLDPRT`) | cluster one, on feature mates | UserChainAxis (Gear Axis on Input Axis), UserChainDist (plane to Sprocket-1's, 150) |
| c2 | Chain-2 | face mates (`PERSIST_REFERENCE_ROUTE_FOR_FACES`) | UserFaceConc (its bore on Input Axis), UserFaceCoin (its end face on Chain-1's) |
| h2 | Housing-2 | cluster two, on the layout | UserHousingRight (coincident), UserHousingDist (distance 420), UserHousingPar (parallel) |
| s5 | Sprocket-5 | a face of a part made new | UserAxis5, UserSunFace (its end face on Sun's end face) |
| s6 | Sprocket-6 | a gear mate on Sun's Gear Axis; the assembly's own Front plane | UserAxis6, UserGear6 (20 : 29), UserAsm6 (distance to `asm:plane1`) |
| s7 | Sprocket-7 | suppressed in L | UserAxis7 |
| s8 | Sprocket-8 | the tie | UserLock8a (to Sun), UserLock8b (to the fixed Housing-1) |
| s9 | Sprocket-9 | suppressed in H, the mode showing | UserAxis9 |
| s10 | Sprocket-10 | a gear mate on a root cylinder of Sun (coaxial) | UserAxis10, UserGearRoot, UserLimit10 (limit distance 20, 10–30, to Sprocket-11) |
| s11 | Sprocket-11 | a gear mate on a root fillet of Sun (off-axis) | UserAxis11, UserGearFillet |
| lt | SprocketLight-1 (`SprocketLight.SLDPRT`) | set lightweight in `carry` only | UserAxisLight |
| cf | SprocketConf-1 (`SprocketConf.SLDPRT`) | in its file's second configuration Z20 | UserAxisConf |

§15's names map so: its Sprocket-9 (lightweight) is SprocketLight-1, its Sprocket-10 (suppressed in the mode showing)
is Sprocket-9, its Sprocket-11 (configuration) is SprocketConf-1. Chain, SprocketLight and SprocketConf are S0's
sprocket's spec, each built by the strip into a file of its own: one Sprocket set lightweight reads every instance of
its file lightweight (`w9d…-1.log:121`), and a second configuration is the file's, so neither may touch
`Sprocket.SLDPRT`.

Changed from §15 as written, so that nothing is over-defined: §15 puts Chain-1 on Input Axis by its axis, a distance to
Sprocket-1 **and** its bore and an end face on Sprocket-1's, which fix the same freedoms twice; the face mates are on
Chain-2, joined to cluster one through Chain-1. The mate to the assembly's own plane is a distance on Sprocket-6 (§15's
"a mate to the assembly's own Front plane"), not on Housing-2, whose Front plane is already held to the layout's.

Then: Sprocket-7 suppressed in L and Sprocket-9 in H, each shown and set (`SetSuppression2`, as the probes did);
SprocketConf-1 set to reference Z20 in every mode (`IComponent2.ReferencedConfiguration`, a put **new** to the repo; a
failure is said and that item is then not shown); every new mate set on in every mode and read back (a flag not
reading back is §0.3's STOP); H shown; the truth read per mode; interference with the user's components said as facts;
saved and closed. **A quiet press then records the inventory** (W9d's entity kinds in it). It may refuse over the tie
(K2's grounded tie, Sprocket-8 locked to Sun and to the fixed housing); a refused press records the inventory as read
all the same, which is what the question needs. The names go into `w9d-fixture.json` in the master.

## The gates, and the line that proposes each

Each W9d write gate, and the read `REFERENCED_CONFIGURATION_READ`, is None on both versions. `carry-gates` shows the
app with them as they stand; `carry` and `carry-closed` patch them in this process only (`PATCH findings.X = … (was
None)`, put back after), and `carry` proposes. Nothing is set.

| Finding (`_ON_<year>`) | Refusal shown | Patched to | `propose` line | What it rests on |
|---|---|---|---|---|
| `CARRY_INSERTS` | `carry-gates`: the press itself (nothing carried, every component named with it) | True | `propose CARRY_INSERTS_ON_<y> = True  # carry: every user part inserted, placed …` | every component carried (Sprocket-9 may be named `no frame`), at its pose against its anchor in every mode, states read back per mode, the tied cluster alone fixed, nothing moved or stopped, every app gear free, the new assembly unsaved, the old assembly and the user's files untouched |
| `CARRY_INSERTS_IN_A_CONFIGURATION` | `carry-gates`: `plan_carry` on the press's own read, this gate as it stands and the others patched | True | `… = True  # carry: SprocketConf-1 inserted in Z20 …` | SprocketConf-1 inserted, `ReferencedConfiguration` Z20 read back in every mode of RangeBox_r2 |
| `REFERENCED_CONFIGURATION_READ` | the same | True | `… = True  # carry: ReferencedConfiguration read Z20 …` | R read Z20 on SprocketConf-1 beside its document's Default (the re-check's R2) |
| `CARRY_REMAKE_KINDS` | the same | every kind word | `… = ('coincident', …)  # carry: the kinds whose every mate was made again, read back equal …` | per kind: every mate of it made again, its definition re-read in RangeBox_r2 equal to the old (type, alignment, values; flipped except for a gear mate), its flags per mode as before. Perpendicular, tangent and limit angle are not in the fixture and are never proposed |
| `CARRY_GEAR_MATE_ON_AN_APP_GEAR` | the same | True | `… = True  # carry: UserGear6 made again on the new Sun's Gear Axis …` | UserGear6 made again, ratio and sense read back by the worker, its definition re-read equal; UserGearRoot's outcome said beside it |
| `CARRY_INSERTS_A_SUBASSEMBLY`, `CARRY_REMAKES_ON_A_LEAF`, `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`, `ORIGIN_ENTITY_READ`, `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` | — | — | `… = None  # <why>` | no sub-assembly, leaf, virtual component, pattern, origin or vertex in the fixture (package A's sub-assembly route is not the measured read-only insert, W9D-REVIEW-A) |

The probe reads (`PERSIST_REFERENCE_ROUTE_FOR_FACES`, `COAXIAL_FACE_READ`, the state route, the closed-file reads, …)
are left as findings.py holds them: set on 2026, None on 2024. The expectations follow them (`expected_outcome`,
`expected_states`), so on 2024 a face mate is judged as named, never as a failure.

## Sections

Times are estimates for SolidWorks 2026 from W9a's and W9c's runs (a Build again… of RangeBox about 5 min, a quiet
press about 2 min, an every-mode read about 1 min).

| # | Section | 2026 |
|---|---|---|
| 1 | `fixture` | 15 min (5 more if `setup.master` is built first) |
| 2 | `carry-gates` | 12 min |
| 3 | `carry` | 35 min |
| 4 | `carry-closed` | 20 min |

**About 1 h 20 min on 2026** against the plan's 1 h 15 min. On 2024 at about twice the time per press, about 2 h 30 min
against the plan's 2 h 15 min, each section in a fresh session. **I would cut first** `carry-closed`'s lost line (the
later Update), then the W9b per-mode read inside `carry` (the script's own every-mode read already judges every gear
free), then `carry-gates`' per-gate replays (pure, but they need the section's press).

### `carry-gates`

1. A copy of the fixture; the old assembly opened as the user has it (H showing).
2. **The edit**, typed in Excel: Sun's Flank to arcs, a Shafts row Aux (frame, x 80, Z+) and a Gears row Aux (spur,
   20 teeth, m1.25, face 6, at 10.5). classify: Build again… as RangeBox_r2, for Sun's Flank **and** the shaft Aux. The
   question printed in full: W9a's clause led by `findings.CARRY_INSERTS_ON_<y>`, the Keyway named.
3. **The press**, bracketed (below). RangeBox_r2 built and saved as today; `carry.inserted` and `remade` empty, not
   unsaved; every component named `unmeasured` with `CARRY_INSERTS`; the old assembly read **open**; **no r3 walk**
   (package A's N3: while `CARRY_INSERTS` is None, R walks nothing and never opens a closed old assembly). The result
   says W9a's sentence led by the finding, and the Keyway. The record at schema 10 holds the carry with
   `unsaved_at` 0, no inventory on r2, no footer line.
4. **Each gate's own refusal**: `plan_carry` (pure) on what this press read on SolidWorks, that gate as it stands and
   every other patched; the items it keeps back are said and must not be empty.

### `carry` (the Done-when)

1. A copy of the fixture; the old assembly opened, H showing (checked); its frames read where it stands;
   SprocketLight-1 set lightweight by the user (`SetSuppression2(1)`, in the session only, never saved: SOLIDWORKS
   CAM's box on saving an assembly with a lightweight component); SprocketLight-1 alone must read lightweight.
2. The edit, as above. With the gates patched, **the question**: the Keyway in Sun's part made new because its Flank
   changed, with the time read; whether it names UserSunFace by name or in a count is said (B's question groups).
3. **The press**, bracketed. RangeBox_r2 built and saved as today; read **open**. Logged: R's read whole (every
   component's state, frame read or not, referenced and active configuration, file configurations, suppressed-in;
   every mate's definition and entities with reference read, coaxial, radius, capped), `CarryResult.facts`, the walks.
4. **Judged** (`judge_carry`):
   - every mate's outcome against `expected_outcome` for the findings as they stand: on 2026 every feature mate and both
     face mates made again; UserSunFace and UserGearFillet named `part new`; UserGearRoot made again on the new Sun's
     Gear Axis; UserAsm6 named `unread` (no root read beside a lightweight component, §4.2) and UserAxisLight
     `lightweight` (D10); UserLock8a fallen back. On 2024 the face mates `unmeasured`, UserGearRoot `part new`,
     UserAxis9 `unread` (D2: Sprocket-9 takes H's state, suppressed, in every mode);
   - every component carried, or Sprocket-9 named `no frame`, which is a reading, not a failure;
   - **the tied cluster alone fell back**: `FELL_TIE`, UserLock8a deleted, UserLock8b kept, Sprocket-8 and Housing-1
     fixed;
   - no `same_error`, nothing `moved`, no stop, unsaved;
   - Sprocket-7 suppressed in L alone and Sprocket-9 in H alone where the route reads states; resolved / suppressed
     everywhere on D2's path;
   - every remade mate on in the modes it was on in (the worker's read and the script's own every-mode read);
   - every remade mate's definition re-read in RangeBox_r2 (`mate_definition`) equal to the old one;
   - every app gear free to turn in every mode (the script's own `GetConstrainedStatus` read per mode, the fixed ring
     aside), then W9b's `mode_read` and `judge_every` (no app–app interference, every frame and flag as recorded),
     the carried components left to:
   - interference per mode with a carried component: what SolidWorks reports against `CarryResult.clashes`;
   - each carried component's pose against its anchor (`CarryResult.anchors`; the world frame for ""), in every mode,
     against its pose against that anchor in the old assembly's mode showing, to 1e-6;
   - SprocketConf-1's referenced configuration Z20 in every mode of RangeBox_r2, and Z20 read by R beside Default;
   - SprocketLight-1's configurations as read from its file closed (`ISldWorks.GetConfigurationNames(path)`), a fact;
   - RangeBox_r2's GetSaveFlag True; the record at schema 10 on disk, `unsaved_at` the file's time, the footer's line.
5. **The proposals** (in the section's `finally`, None for whatever did not hold).
6. **The user saves RangeBox_r2** alone (SprocketLight-1 resolved first, in the old assembly): the window's read drops
   the footer's line. The copy is closed unsaved.

### `carry-closed`

1. A copy of the fixture; the user shows L and saves (the save also writes the assembly's references to this copy's
   files: `GetDocumentDependencies2` gives the *stored* paths, and the master's were the master's folder's, which R.2
   would refuse as not on disk); its frames read in L; everything closed.
2. The edit; the question (its closed-assembly clause); the gates patched; **the press**. R reads **read-only**, L
   showing as saved, nothing left open or marked; the old assembly closed again by the job. The traced calls allow its
   own read-only open and close, and its per-mode show only where the state route is None (2024).
3. Judged as `carry` (no lightweight now: UserAsm6 and UserAxisLight made again; tier 1 on the faces after the reload
   by `PERSIST_REFERENCE_SURVIVES_RELOAD`), with Sprocket-7 the one that may be named `no frame` (suppressed in L, the
   mode showing). **Contradiction 6**: Sprocket-2, locked to the sliding RangeSlv, read in L, is placed against
   RangeSlv in H and holds its pose against it in every mode.
4. **R.2's refusals**, by closed-file reads only (`swbuild._not_open_refusal`, nothing opened): a record written on
   another version; with `--other-version-file`, that file as the old assembly.
5. **The lost line**: RangeBox_r2 and everything closed without saving; a later Update (if the footer offers one) says
   the carry was lost, and the footer's carry line is gone.

### The bracket around every Build again… (`press_build`)

- the footer must offer Build again…;
- **fingerprints** (size, mtime, SHA-256) of the old assembly and every user file (Sprocket, Housing, Chain,
  SprocketLight, SprocketConf) before and after: any change is a STOP;
- **GetSaveFlag** of every open document of the copy before and after; a user document or the old assembly newly marked
  is a STOP (open path);
- **the old assembly read where it stands** before and after, never opened or activated (`use_open_document`):
  frames, every mate's code, flag per mode and entities, the mode showing, its rebuild state, every component's state
  (`old_read`, which finds a suppressed component with `suppressed_ok`, where W9a's `read_now` would raise on M9's two);
  any difference is a STOP;
- **the traced calls**: every `ShowConfiguration2`, `ForceRebuild3`, `EditRebuild3`, `AddMate5`, `AddComponent5`,
  `EditDelete`, `Save3`, `SaveAs3`, `QuitDoc`, `CloseDoc`, `OpenDoc6` and `ActivateDoc3` with the file it is on
  (`trace_problems`): none on the old assembly or a user file but the closed path's own read-only open, close (and show
  on the None path), no `OpenDoc6`/`ActivateDoc3` of an open old assembly, and **no `SaveAs3` or `Save3` after the new
  assembly's first save**;
- no window (W9a's watch and `windows_new`).

## Logged as facts: what only the fake had shown

Each W9d member the worker calls is wrapped and logged with its arguments (file names only, references cut), answer
and seconds: `entity_references`, `entity_reference`, `component_configurations`, `component_states_in`,
`open_read_only`, `close_unsaved`, `file_version`, `running_file_version`, `dependencies`, `add_component_in`,
`set_component_suppressed`, `remake_mate` (its targets, ratio and Flip), `select_by_reference`, `delete_mate`. For the
re-check's list (W9D-PACKAGE-A.md, the last section):

- **the walk grouped per component**: one line per `entity_references` call, its items, seconds, candidates carried
  (`Session.last_walk`), seconds per candidate, and per item: listed, kept by the part-against-assembly prefilter, its
  key, matched; the calls it made by member (`GetArea`, `CircleParams`, `GetCorresponding`, `IsSame`, …); the cap's two
  numbers and whether either was reached; `OldWork.walks` as the worker logs it;
- **the growth**: the seconds per candidate in each walk, in order through the session;
- **`IEntity.GetType`** on each resolved face or edge;
- **whether `GetObjectByPersistReference3` writes its out code**, and where pywin32 hands it back (the return tuple's
  second item, and the by-reference parameter after the call);
- `CarryResult.facts` (N2: what reads in a mode where a cluster's component is suppressed, not judged: Sprocket-7 in L
  is M9's case, the first reading of it on SolidWorks), `changed_files` (must be empty);
- R's read of a suppressed component (found, its frame read or not) and of a lightweight one's configurations closed.

## STOPs

As W9a's and W9c's, plus the plan's W9d (§0.3):

- any dialog during a job, by the version's What's Wrong rule;
- the old assembly or a user file changed on disk; a user document or the old assembly newly marked; the old
  assembly's frames, mates, flags, entities, states or mode showing changed; a traced write, show, rebuild, save or
  close of either; anything saved after the new assembly's first save;
- a read that marks a document; a new mate's flag in the fixture not reading back as set.

A gate's refusal, a named item and a fallback are results, not failures.

## Without SolidWorks

`PYTHONPATH=src python probe/w9d_demonstration.py --self-check` (the Linux venv) checks, at this commit 0 failed:

- **the edit**: RangeBox's workbook written by the app's `write_new`, the edit typed by `write_cells` at the cells
  W8's `cell` finds (W9c's `_offline`, its sheets with Shafts added), read back: legal, Sun's arcs meshing Planet's
  involute (D18) with the arcs note; classify on a record built on the fake: Build again…, for Sun's Flank and the
  shaft Aux; `carry_for`: Sun's part new because its Flank changed, every other gear part reused;
- **the carry end to end on the fake** (B's round-trip desk: RangeBox, W9a's user work, plus Sprocket-8 tied and
  Chain-1 on Input Axis, read by a quiet press): the gates as they stand (nothing carried, each component named with
  `CARRY_INSERTS`, W9a's sentence led, the Keyway); each gate's own refusal by `plan_carry` with the others patched;
  the gates patched (every component carried, the tied cluster alone fallen back, the result's sentence, schema 10,
  `unsaved_at`, the footer's line); the old assembly closed (read read-only, nothing left open or marked); R.2 refusing
  a record another version wrote;
- **the pure judgements on made-up readings**, each failing way: `expected_outcome` and `expected_states` for 2026
  open with a lightweight component, 2024 open, closed, closed without the reload finding; `outcome_problems`,
  `outcome_of`, `fingerprint_diff`, `trace_problems` (open and closed), `old_diff`, `definition_problems`,
  `kinds_clean`, `pose_gap`; the kind words pinned to the worker's; every gate named a finding of findings.py, and every
  patched one None there on both versions.

`--help` imports nothing of SolidWorks.

## What the packages could not be driven to, and what is not a measurement here

- **`FELL_NEW_ERROR` and `FELL_OVER_DEFINED`** are the fake's only (§6): no fixture provokes them without contriving a
  broken mate.
- **A user sub-assembly** is not in the fixture: package A's insert of one is `open_document` + `add_component`, not
  the measured read-only insert, and the review asked it not be patched without a test (W9D-REVIEW-A). So
  `CARRY_INSERTS_A_SUBASSEMBLY` stays None, and so does every leaf mate.
- **A virtual component, a pattern instance, an origin and a vertex** are not in the fixture: their findings stay None.
- **Perpendicular, tangent and limit angle** are not made in the fixture, so `CARRY_REMAKE_KINDS` never holds them.
- **The mate to the assembly's own plane cannot be carried in `carry`**: R never reads the root beside a lightweight
  component (§4.2, `_read_old_mates`), and §15 puts SprocketLight-1's lightweight state in the same section. It is
  judged `unread` there and made again in `carry-closed`, which has no lightweight component.
- **CARRY_INSERTS gates R's walk and the not-open read** (package A's N3): `carry-gates` cannot show the not-open read
  refusing on its own conditions; `carry-closed` shows it under the patch, and its R.2 refusals by closed-file reads.
- **The "SolidWorks reads … as changed" sentence** rests on `CARRY_INSERT_MARKS_USER_DOCUMENTS` (False on 2026, one
  probe case): the GetSaveFlag bracket says what this run read.
- **The later Update's lost line** needs the footer to offer an Update straight after a Build again…; where it does not,
  it is said, and the fake's test is the evidence.
- **SprocketConf-1's configuration** is set by `IComponent2.ReferencedConfiguration` as a put, new to the repo; a
  failure leaves that item not shown.
- **The question's mate names**: package B names a few items and counts the rest, so the script holds the question to
  its distinctive parts (the Keyway, the time read, the finding) and says whether UserSunFace is named.
- Every judgement of "unchanged" is by reads, file fingerprints and traced document calls; a component-level
  `SetSuppression2` is not mapped to its assembly in the trace, so the old assembly's states are compared by reads.

## Command lines

2026 (fresh session; `RUN` the run folder with `snap` the repo snapshot):

```
python.exe RUN\snap\probe\w9d_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9d-demo-sw2026-1.log ^
    --sections fixture,carry-gates,carry,carry-closed --master <S0's rangebox.master> ^
    --user-master <W9a's setup.master> --other-version-file <a 2024-saved assembly, e.g. W9c's 2024 setup.master's RangeBox.SLDASM>
```

About 80 min. 2024, after the 2024 W9d probes, in fresh sessions (each about twice as long):

```
python.exe RUN\snap\probe\w9d_demonstration.py RUN\snap\src RUN\out24 --pid PID --log RUN\w9d-demo-sw2024-1.log ^
    --sections fixture,carry-gates,carry --master <2024 rangebox.master> --user-master <2024 setup.master>
python.exe RUN\snap\probe\w9d_demonstration.py RUN\snap\src RUN\out24 --pid PID --log RUN\w9d-demo-sw2024-2.log ^
    --sections carry-closed --other-version-file <a 2026-saved assembly>
```

The second run finds `w9d-fixture.master` in the same `RUN\out24`, or takes `--fixture-master`. Folders are written
`<probe folder>\…` in any note about a run.
