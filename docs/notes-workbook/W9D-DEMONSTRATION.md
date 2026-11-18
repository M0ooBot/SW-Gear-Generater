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
| s8 | Sprocket-8 | the tie | UserLock8a (to Sun), then UserAngle8b (90° from its Top plane to the fixed Housing-1's Right plane: one freedom) |
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
| `CARRY_INSERTS` | `carry-gates`: the press itself (nothing carried, every component named with it) | True | `propose CARRY_INSERTS_ON_<y> = True  # carry: every user part inserted, placed …` | every mate's outcome as `expected_outcome` says; every component carried (Sprocket-9 may be named `no frame`); each against the fixture's anchor and at its pose against it in every mode where it is resolved (a frame that does not read is a FAIL); its states per mode as the script reads them by showing each mode; the tied cluster alone fixed; nothing moved or stopped; every app gear free; the new assembly unsaved; the old assembly and the user's files untouched |
| `CARRY_INSERTS_IN_A_CONFIGURATION` | `carry-gates`: `plan_carry` on the press's own read, this gate as it stands and the others patched | True | `… = True  # carry: SprocketConf-1 inserted in Z20 …` | SprocketConf-1 inserted, `ReferencedConfiguration` Z20 read back in every mode of RangeBox_r2 |
| `REFERENCED_CONFIGURATION_READ` | the same | True | `… = True  # carry: ReferencedConfiguration read Z20 …` | R read Z20 on SprocketConf-1 beside its document's Default (the re-check's R2) |
| `CARRY_REMAKE_KINDS` | the same | every kind word | `… = ('coincident', …)  # carry: the kinds whose every mate was made again, read back equal …` | per kind (the fixture's own kind of each mate): every mate of it made again; its definition **and entities** read by the script's own read in RangeBox_r2 equal to the script's own read of the old one before the press (M2: type, alignment, values, flipped except for a gear mate, whose sense is compared by `gear_sense`; each entity mapped old→new: its component, its reference, a feature's name, a face's or edge's place in its own component); its flags per mode as before, read again. Perpendicular, tangent and limit angle are not in the fixture and are never proposed |
| `CARRY_GEAR_MATE_ON_AN_APP_GEAR` | the same | True | `… = True  # carry: UserGear6 made again on the new Sun's Gear Axis …` | UserGear6 made again, ratio and sense read back by the worker, its definition re-read equal; UserGearRoot's outcome said beside it |
| `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY` (a fact, not a gate; the review's M1 (b), ruled) | — | — | `… = True/False  # carry: SprocketLight-1 … read 1 before the press and 2 after …` | SprocketLight-1's state in the open old assembly read before and after the press: carrying it opens its file, and lightweight is per file in the session. For D10, and for a sentence the result will need if True |
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

**About 1 h 30 to 1 h 45 on 2026** (the review's estimate after the revision: `carry`'s own reads of the old and new
mates' definitions, the every-mode read and W9b's read come on top of a carry of 17 components and about 31 mates; it
may take 45 min rather than 35), against the plan's 1 h 15 min. On 2024 at about twice the time per press, about
3 h, each section in a fresh session. **What to cut first:** `carry-closed`'s lost line (the later Update; the fake
shows it), then W9b's read inside `carry` (said as cut: it is the only read compared with `CarryResult.clashes`).
**Never `carry-closed` whole**: it is the only section for the not-open read, contradiction 6, UserAsm6 and the light
part's mate.

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

1. A copy of the fixture; the old assembly opened, H showing (checked);
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
   - **the tied cluster alone fell back**: `FELL_TIE`, UserLock8a deleted, UserAngle8b kept, Sprocket-8 and Housing-1
     fixed;
   - no `same_error`, nothing `moved`, no stop, unsaved;
   - the anchors (`CarryResult.anchors`) held to the fixture's (D20 **as ruled 2026-11-17**: a component fixed in the
     old assembly, Housing-1, is placed by its world frame, never turned about an app gear through its cluster; a
     floating one by its own lock to an app body, then any mate to an app body, then the world): cluster one and
     Sprocket-5, -6, -8, -10, -11 against Sun, Sprocket-2 against RangeSlv, Housing-1 the world, the rest the world or
     the layout;
   - Sprocket-7 suppressed in L alone and Sprocket-9 in H alone where the route reads states; resolved / suppressed
     everywhere on D2's path — **by the script's own read**, each mode shown and every carried component's
     `GetSuppression2` read, held to the route's expectation and to what the carry said; every other carried component
     resolved in every mode;
   - every remade mate on in the modes it was on in (the worker's read and the script's own every-mode read);
   - **M2**: every remade mate's definition and entities, by the script's own read (the probes' `mate_definition`,
     assemblies/06's route, not the app's), in RangeBox_r2 against the same read of the old mate taken before the press:
     each entity mapped old→new by the fixture's map (a user component by its carried Name2, an app body by gear id,
     the layout, the assembly's own root by the assembly's stem), its reference (feature, component, geometry), a
     feature's name, a face's or an edge's place in its own component (`entity_key`: `EntityParams`' point and
     direction taken into the component's frame: a plane's offset along its normal, an axis' distance from the
     component's origin, the radius), either order of the two entities; a gear mate's face on an app gear expected as
     that gear's Gear Axis (§4.3); a gear mate's sense by `gear_sense` (`Reverse` with the entities' directions), never
     `Reverse` alone. A mate made again on the wrong face, axis or component FAILs, and its kind is not proposed;
   - every app gear free to turn in every mode (the script's own `GetConstrainedStatus` read per mode, the fixed ring
     aside), then W9b's `mode_read` and `judge_every` (no app–app interference, every frame and flag as recorded),
     the carried components left to:
   - interference per mode with a carried component: what SolidWorks reports against `CarryResult.clashes`;
   - Sun's frame in the old assembly and in each mode of RangeBox_r2, logged before the poses are judged;
   - each carried component's pose against its anchor (the world frame for ""), in every mode where it is resolved,
     against its pose against that anchor in the old assembly's mode showing, to 1e-6; a frame that does not read in
     such a mode is a FAIL (where the script's read of the old one does not read, R's frame is held, said);
   - SprocketConf-1's referenced configuration Z20 in every mode of RangeBox_r2, and Z20 read by R beside Default;
   - SprocketLight-1's configurations as read from its file closed (`ISldWorks.GetConfigurationNames(path)`), a fact;
   - RangeBox_r2's GetSaveFlag True; the record at schema 10 on disk, `unsaved_at` the file's time, the footer's line.
5. **The proposals** (in the section's `finally`, None for whatever did not hold).
6. **The user saves RangeBox_r2** alone (SprocketLight-1 resolved first, in the old assembly), **only if no component
   of RangeBox_r2 reads lightweight** (M1 (a): saving an assembly with a lightweight component brings up SOLIDWORKS
   CAM's modal box, which ignores `WM_CLOSE`); otherwise it is not saved, said, and the footer's line going is said
   as not shown. Saved, the window's read drops the footer's line. The copy is closed unsaved.

**M1 (b), ruled 2026-11-17.** Carrying SprocketLight-1 opens its file (C.3), and lightweight is per file in the
session, so the old assembly's lightweight instance may come out resolved. That change, and only that, is set apart by
`old_diff` and is not a STOP (narrowed by ruling 4 after the first run): its state; its frame going from unread to
read; a mate's entity on it going from unread to read, everything else of that mate equal; its file going from not
open to open and unmarked (`10426c5`). Its moving, its fixed state, its referenced configuration or any mate's value
changing is a STOP. Its
state before and after is a fact and `propose CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY_ON_<y>` says
which. Anything else changed in the old assembly or a user file remains a STOP.

### `carry-closed`

1. A copy of the fixture; the edit typed; **R.2 on the copy as copied**, before any save: `_not_open_refusal` (closed-file
   reads only) must refuse it — its stored dependency paths are the master's folder's (the ruling of 2026-11-17: a
   copied folder whose stored paths lie outside its own folder, where a same-named file sits, is refused, "open it
   first"; before package A's change it refuses as a file not found). Then the user shows L and saves (the save also writes the assembly's references to this copy's
   files: `GetDocumentDependencies2` gives the *stored* paths, and the master's were the master's folder's, which R.2
   would refuse); the old assembly read where it stands (frames, states, every mate's definition and entities by the
   script's own read: M2's old side); everything closed.
2. The question (its closed-assembly clause); the gates patched; **the press**. Where the closed-file findings are not
   set (2024 until its probes are reviewed) the old assembly must come out `OLD_UNREAD`, nothing carried, and the
   section ends there. R reads **read-only**, L
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
  frames, every mate's code, flag per mode and entities, every user mate's definition and entities by the script's
  own read (values and places), the mode showing, its rebuild state, every component's state, fixed or floating and
  referenced configuration (`old_read`, which finds a suppressed component with `suppressed_ok`, where W9a's
  `read_now` would raise on M9's two); any difference is a STOP but M1 (b)'s. In `carry` the old assembly is marked
  already by the user's lightweight set, so its save-flag bracket is blind there and this read carries the weight;
- **the traced calls**: every `ShowConfiguration2`, `ForceRebuild3`, `EditRebuild3`, `AddMate5`, `AddComponent5`,
  `Save3`, `SaveAs3`, `QuitDoc`, `CloseDoc`, `OpenDoc6` and `ActivateDoc3` through `swcom.call`, with the file it is
  on; and, by wrapping the Session members that make them without `swcom.call` or on no document object, `EditDelete`
  (`delete_mate`, `delete_component`, through `_guarded`), `FixComponent` / `UnfixComponent`, the `Transform2` put
  (`place_component`) and a mate's `SetSuppression2` (`set_mate_suppressed`, `_in`), each on the document the
  session is building in; names compared by their stems (a title may lack its extension) (`trace_problems`): none on the old assembly or a user file but the closed path's own read-only open, close (and show
  on the None path), no `OpenDoc6`/`ActivateDoc3` of an open old assembly, and **no `SaveAs3` or `Save3` after the new
  assembly's first save**;
- no window (W9a's watch and `windows_new`).

**What the trace cannot see**: a mate's `Name` put (`_rename`, a static helper on the feature) and a component's own
`SetSuppression2` (its object is the component, whose file is the user's own: it would read as a write to a user
file). Both fall to the old assembly's read before and after (mate names, component states).

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
- **`expected_outcome` against the worker's own `plan_carry`** on an `OldWork` shaped like the fixture (its 17
  components' kinds, states and configurations, its 31 mates' kinds and entities by owner, kind and feature), for
  2026 open with a lightweight component, 2024 open, 2026 closed, closed without the reload finding, and Sprocket-9
  without a frame; a fallback and D2's unread are the carry's, not the plan's, and are allowed for there;
- **`DeskD.build` against the window's `_start_build`**, read as source: the same calls, kwargs for kwargs
  (`old_assembly`, `carry_for` from that very object, the journal, the revision in the job, `build_gearbox`);
- **the pure judgements on made-up readings**, each failing way: `expected_outcome` and `expected_states` for 2026
  open with a lightweight component, 2024 open, closed (readable or not), closed without the reload finding, a
  component named no frame; `outcome_problems`, `outcome_of`, `fingerprint_diff`, `trace_problems` (open and closed,
  by stems), `old_diff` (and M1 (b)'s set-apart, which a second change beside it does not hide), `entity_key` (a face's
  place survives its component's move, its other end face differs), `entity_problems` (the wrong face, component or
  axis each FAIL; a gear mate's face made again on the gear's Gear Axis passes), `definition_problems` (a gear's
  other Flip with its sense kept passes, its sense turned FAILs), `kinds_clean`, `pose_gap`; the kind words pinned to
  the worker's; every gate named a finding of findings.py, and every patched one None there on both versions.

At this commit: 44 ok, 0 failed. `--help` imports nothing of SolidWorks.

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

## The first run on SolidWorks 2026 (2026-11-17, `src` at 90cdf20, SolidWorks 2026 34.0.0)

**Setup.**
- Run folder `<probe folder>\w9d-demo-sw2026-20261117-155112`.
- One session, PID 9768, started for the run and exited after.
- Masters: the W9c whole run's `rangebox.master` and `setup.master`, which the script only copies (`copy_built`'s
  `copytree`, the sprocket's `copy2`). Their files' sizes, times and md5 were the same before and after.
- `--other-version-file`: the 2024-built `Reducer_12to1.SLDASM`, read closed only, its file unchanged.
- Three invocations, each snapshot holding 90cdf20's `src`:
  - 90cdf20: every section;
  - 10426c5: `carry` and `carry-closed` with `--redo`;
  - 2fb3946: `carry-closed` with `--redo`.
- Logs `probe/results/w9d-demo-sw2026-20261117-1-first-contact-light-flag-stop.log`, `-2-carry-app-faults.log` and
  `-3-carry-closed-read-only.log`, with their JSON.

| Section | Run | Time | ok | FAIL | STOP |
|---|---|---|---|---|---|
| fixture | 1 | 485 s | 19 | 1 | 0 |
| carry-gates | 1 | 1080 s | 26 | 0 | 0 |
| carry | 1 | 933 s (cut) | 13 | 1 | the script's (below) |
| carry | 2 | 1152 s | 36 | 5 | 0 |
| carry-closed | 3 | 763 s | 38 | 5 | 0 |

Run 2's `carry-closed` (401 s, 8 failed) is superseded by run 3: its closed read never ran (below).

**The script's faults, fixed:**
- **`old_diff`'s save flags (10426c5).** In run 1, `carry` stopped on `save flags {'SprocketLight.SLDPRT': (None,
  False)}`. SprocketLight-1, set lightweight by the user, came out resolved in the old assembly (M1 (b), ruled), and
  that loads its file as a document, open and unmarked, where before it was not open. The ruled change is now set
  apart with it, and only it; anything else in the flags is still a STOP.
- **`carry-closed`'s save (2fb3946).** W9a's `save_user` saves only what SolidWorks reads modified, and showing L does
  not mark the assembly. So run 2 saved nothing there, and R.2 refused the closed read, the copy's stored paths still
  being the master's. The assembly is now saved itself, by W8's `SaveAs3` route, and its file being written is checked.

**The app's faults, not fixed here:**
- **The r3 walk reads nothing.** Every face or edge item reads "its reference could not be read ('method' object is
  not iterable)", in 0.8–1.8 s per component with 0 candidates carried.
  - The cause: `src/gear_generator/swcom.py:3942-3943` lists the part's faces by `list(call(body, member) or ())`.
    Through late binding `IBody2.GetFaces`/`GetEdges` come back as a bound method, uncalled. The probe's r3 went
    through `raw()`, which calls it.
  - So UserFaceConc, UserFaceCoin and UserSunFace are named unread, and the sentence the user reads carries the Python
    error.
- **The carry stops at its states.** In both `carry` and `carry-closed` the carry stopped after setting the states:
  "No component is kept as 'gear7', so whether it is free to turn cannot be read; that is a fault in Gear Generator,
  not in SolidWorks".
  - This is `swbuild.py:8060`, `c.free_before = _free(sw, c.mated)`, and `swcom.py:2630`. `gear7` is the new Aux
    gear: its handle from the build is not kept in the session when the carry reads it. Why is not traced.
  - So no mate was made again and the tie never fell back. The carried components stand where they were placed,
    which is why Sprocket-5 (`carry`) and Sprocket-4 (`carry-closed`) are off in N and L. The record holds 17
    components and 0 mates.
  - Several `ok` lines about remade mates hold vacuously: nothing was remade.

**What SolidWorks did, measured:**
- All 17 components were inserted and placed against the fixture's anchors.
- SprocketConf-1 went in by `AddComponent5` with `Z20`, reading `Z20` in every mode. R read `Z20` beside its
  document's `Default`.
- The states were set per mode: Sprocket-7 suppressed in L alone and Sprocket-9 in H alone, by the script's own shown
  read as by the route.
- SprocketLight-1 read 1 before the press and 2 after in the open old assembly, its file then open and unmarked.
- R's old-entity reads (`entity_reference`) took 2.4–3.3 s each.
- In `carry-closed`, R.2 refused the unsaved copy (closed-file reads only). After the save, R opened the old assembly
  read-only (5.0 s), with L showing as saved, and closed it (`close_unsaved`, 0.3 s). Nothing was left open or
  marked, and no file changed.
- The record another version wrote and the 2024 `Reducer_12to1.SLDASM` (17000) were refused by closed reads.
- The later Update said the carry was lost.
- **The fixture's tie over-defines** (§15's tie: Sprocket-8 locked to Sun and to the fixed Housing-1). `UserLock8b`
  was made with status 5, and `Sun along Input` and `UserLock8a` read 46 (`swFeatureErrorMateOverdefined`) in the old
  assembly. The fixture's own "code 0" check FAILs on it. That is the script's expectation against §15's design, left
  for review, not changed. The quiet press read nothing of the user's in error there.

## The revision after the review (`W9D-DEMONSTRATION-REVIEW.md`, 6f67791)

- **M1 (a)** RangeBox_r2 is saved by the user only when none of its components reads lightweight (above, `carry` 6).
- **M1 (b), ruled** SprocketLight-1's lightweight-to-resolved change in the old assembly is set apart and proposed as a
  fact; anything else is a STOP (above).
- **M2** remade mates compared on their entities, mapped old→new, against the script's own read of the old mates
  before the press (above).
- **Should-fixes, all the script's, done**: the gear sense by `gear_sense`; flags per mode counted against a kind;
  the states per mode by the script's own shown read; every carried component's frame required; the anchors held to
  the fixture's; `outcome` and the anchors among `CARRY_INSERTS`' conditions; "component not carried" accepted for the
  mates of a component named `no frame`; `expected_outcome` against `plan_carry` and `DeskD.build` against the
  window's `_start_build` in the self-check; Sun's frames logged; the trace sees `EditDelete`, fix and unfix, the
  `Transform2` put and a mate's flag, by stems; the old read holds fixed, the mates' values and entities and the
  referenced configuration.
- **Rulings of 2026-11-17 written into the expectations**: a fixed component is placed by its world frame (Housing-1's
  expected anchor is ""); R.2 refuses a copied folder whose stored paths lie outside it (the unsaved copy's refusal in
  `carry-closed`). Package A is being changed to match: until it is, Housing-1's anchor FAILs `carry`'s anchor check.
- **B's last wording round** (`1ab1029`, `9a21c6d`): every fragment the script matches is in `ui_text` at head
  (*Carried into RangeBox_r2, unsaved*, *has not yet been shown to carry your work*, *As read at*, *fixed where*, *was
  closed without saving after Build again… carried your work into it*); the self-check's fake runs say them.

## The revision after the first 2026 run (the review's addendum, `e2207d9`; the coordinator's rulings)

1. **The tie replaced.** UserLock8b (a lock from Sprocket-8 to the fixed Housing-1) over-defined the old assembly
   (status 5, 46), and the same-error rule would have excused it. It is now **UserAngle8b**, an angle of 90° from
   Sprocket-8's Top plane to Housing-1's Right plane, made after UserLock8a: one freedom, so the old assembly reads
   every mate 0 while Sun cannot turn. Both components stand at identity rotations, so Top's normal (Y) and Right's
   (X) are at 90°, both across Sun's axis; the fixture checks this from their frames before making the mate
   (`angle_pair`) and takes another Top/Right pair that is if they stand turned, saying which. **The fixture STOPs**
   when any mate on in H reads a code other than 0, or Sun does not read fully defined (the tie the carry must find
   again) (`fixture_problems`). Expected: UserLock8a made and deleted by `FELL_TIE`'s fallback, UserAngle8b made and
   kept, Sprocket-8 and Housing-1 fixed. §15 of W9D-INTERFACES says so.
2. **No check passes with nothing to judge.** Each check over remade mates (definitions and entities, flags per mode)
   takes its population from `expected_outcome` and FAILs naming every mate not reached ("not reached: nothing was
   remade (the carry stopped at …)", `not_reached`); a mate whose outcome is not the expected one counts as unclean
   for its kind. The post-check's two claims (every app gear free with the carried mates on; the interference the
   carry named) are judged only when the carry did not stop and remade something, else FAIL as not reached.
   Contradiction 6 requires Sprocket-2's pose against RangeSlv in N and L. The states check FAILs when Sprocket-7 or
   -9 was not carried, the "every other component resolved" check when none was, the anchors when nothing was
   inserted, the record check when nothing was left unsaved in a section that expects it. Every key feeding a proposal
   is False when not reached, and the proposals are a pure `proposal_values`, self-checked with a carry that remade
   nothing (every write gate None, the configuration insert standing).
3. **The measured reading on a suppressed component** is the contract's (§11.5): `expected_outcome` takes `unread`
   for UserAxis9 on the open path and UserAxis7 on the closed one, exactly; the fixture-shaped read the self-check
   gives `plan_carry` has those entities unread, so plan and expectation agree.
4. **The light set-apart narrowed** (above, M1 (b)).
5. **Poses and components named by old and new Name2** (*Sprocket-2 as Sprocket-5*): SolidWorks numbers inserted
   instances in insertion order, so the first run's "Sprocket-5" and "Sprocket-4" were both the old Sprocket-2.
6. **The footer.** The first run's record check FAILed on the footer after the build. Reading `ui_text.workbook_footer`:
   while the job's note stands (the build's own sentence) the footer is that sentence, and the idle footer's lines,
   §9.4's among them, are added only when there is no note or the note is an answer. So straight after the build a
   user sees the build's sentence, which asks for the save itself; §9.4's line appears once the note goes (the
   workbook read again with a change, or the window opened again). `desk.read()` does not clear the note, as the
   window's read does not. `record_judged` now reads the footer after `desk.read()` both ways: with the note standing
   (it must ask for the save) and with it set aside (it must say §9.4's line). The window may be right; whether a
   finished carry should keep §9.4's line visible beside the build's sentence is package B's to say.
7. **UserAxisLight** is expected `lightweight` (named, never read), and the self-check's `plan_carry` agrees.

## Following A's fifth round (`a366938`) and B's round (`5f52913`), after the re-check (`b44594d`)

- **Flags in a mode where a component is suppressed** (a366938, §3 C.6.1): the worker sets the flag as recorded there,
  keeps what SolidWorks reads back as a fact, and judges nothing. The script's flags check (`flags_judged`) now judges
  only the modes where every carried component the mate joins reads resolved (the script's own shown read); in the
  others it prints what SolidWorks read beside the worker's own fact (`fact    … UserAxis7 in L, where a component it
  joins (Sprocket-7 as …) is suppressed: set on as recorded, SolidWorks reads it …`). That is UserAxis7 on the open
  path and UserAxis9 on the closed one, never measured before. `_judge` no longer excuses a gear's tie by the
  same-error rule; the fixture's tie has no same error, and the self-check's fake carry still falls back by
  `FELL_TIE`.
- **The footer** (5f52913): §9.4's line now follows a job's sentence unless that sentence asks for the save itself.
  `record_judged` takes exactly what fits what the carry did: finished, the build's phrase "Save RangeBox_r2 in
  SolidWorks to keep what was carried" with the note standing, and not §9.4's line beside it; stopped, §9.4's line;
  the idle footer (note gone) says §9.4's line either way.
- **The question** (5f52913): with the gates patched it must say UserGear6 as *made again if the press reads its gear
  ratio and which way it turns* and UserGearRoot as *made again only if the face of Sun it is on proves to be on Sun's
  axis*, each in its sentence, and say no mate of the user's in error (`question_problems`).
- **The fallback check** follows the closed path without the reload finding (UserAngle8b not made again, so nothing
  ties and nothing falls back); no run meets that path (2026 holds the finding; 2024's closed path is not read).
  After the fallback, the code SolidWorks reads for UserAngle8b, joining two components the fallback fixed, is printed
  per mode as a fact.
- **`CARRY_INSERTS`, ruled**: proposed from the inserts' own lines (every component inserted, placed against its
  anchor in every mode, its states set and read back, the carry not stopped and nothing moved, nothing written to the
  old assembly, the tied cluster's components fixed). The mates' definitions and flags feed `CARRY_REMAKE_KINDS` and
  the gear-mate gate only. The proposal line prints every condition. The self-check shows the insert gate proposed
  with the mates' checks failed, and the gear kind and gate then withheld.

## Following package A's seventh round and the audit's rulings (`7e3ad9a`)

- **UserAsm6** is made again and kept wherever the old assembly holds no lightweight component: `expected_outcome`
  says `remade` on the closed path and `unread` beside the lightweight SprocketLight-1 on the open one (unchanged;
  the self-check's `plan_carry` agrees).
- **Kind words.** The worker no longer takes a plain distance or angle (its range equal to its value) for a limit
  one. The script's `CARRY_REMAKE_KINDS` line now uses the worker's own words (`swbuild.carry_kind` on what R read),
  per mate shown and read back clean, so a finding set from it opens the gate for the kinds the run showed and for no
  limit kind it did not show. It prints, per kind, the mates that stood for it, and where the worker's word differs
  from the fixture's. For a distance or an angle `flipped` is no longer compared (its Flip now stands for its
  FlipDimension; its side is the pose check's), as the worker does.
- **The worker's facts** (`CarryResult.facts`) are each logged under a tag: `flip dimension`, `renamed`, `fixed after
  a fallback`, `fixed as in the old`, `flag where suppressed`, else `worker`.
- **The script's own reads beside them:**
  - **fixed in every mode** (a check, and a condition of `CARRY_INSERTS`): every component of the fallen cluster
    and every component fixed in the old assembly (Housing-1) reads `IsFixed` in every mode of RangeBox_r2 after the
    carry; which of the worker's two sentences it gave (one FixComponent, or "had to be fixed") is printed. This is
    the first measurement of what one FixComponent does across configurations;
  - **FlipDimension** of each distance or angle mate, read in the old assembly before the press and in RangeBox_r2
    after, with `IMate2.Flipped` read both times too (nothing measured says which of the two stands for AddMate5's
    Flip; UserAngle8b has never been made), printed side by side with the worker's sentence (a fact; the audit
    review's D1);
  - a gear mate's alignment is printed before and after and not judged, since AddMate5 ignores it (D3);
  - (the re-check's D4–D6) the fixed-in-every-mode check skips, and says, a mode where the component is suppressed (a
    suppressed component reads `IsFixed` False); one suppressed in every mode is not reached, a FAIL. Beside `IsFixed`
    per mode the fallen cluster's and the old-fixed components' frames are printed: their largest difference from
    where they stand in the first mode, and a fixed one's from its world frame in the old assembly.
    `swConstrainedStatus_e`'s names are read once per run from `swconst.tlb` and every constrained status printed
    (the app bodies' and the carried components' per mode, Sun's in the fixture) carries its name.
  - **kept names**: every remade mate's name against its old one, a check that passes when equal and, when not, only
    if the worker said `<old> is carried as <kept>`. Every mate check finds the mate under its kept name.

## The second run on SolidWorks 2026 (2026-11-18, from f7c2f0d, SolidWorks 2026 34.1.1)

**Setup.**
- Run folder `<probe folder>\w9d-demo-sw2026-20261118-031029`. This laptop's SolidWorks 2026 is revision 34.1.1;
  the first run was on another host's 34.0.0.
- One session, PID 53472, started for the run and exited after (by its own close, nothing left open). No other
  SolidWorks, Excel or Python was running before it; the run started and quit its own Excel each time.
- Masters, only copied: S0's `rangebox.master` (`<probe folder>\w9-s0-20261116-045513\out`) and W9a's final
  `setup.master` (`<probe folder>\w9a-final-sw2026-20261117-023433\out`), which the fixture's copy read as valid
  and built from its workbook (log 1:22, 36). `--other-version-file`: the RangeBox assembly of W9a's 2024
  `setup.master` (`<probe folder>\w9a-confirm-sw2024-20261117-002313\out`), read closed only. The md5 of every
  file of the three master folders was the same before and after.
- Two invocations into the same `out`:
  - snapshot f7c2f0d (`snap`): every section;
  - snapshot 41afa37 (`snap-41afa37`): `carry-closed` with `--redo`, from the `w9d-fixture.master` the first
    kept. 41afa37 is the script's fix below on top of f7c2f0d and the workbook branch's W9c commits merged since
    (`d0e32bb` to `d48ecbf`): in `src` those change only findings.py's `_ON_2024` W9c gates and their comments,
    and in the harness a What's Wrong close path W9d leaves off.
- Logs `probe/results/w9d-demo-sw2026-20261118-1-whole-closed-read-mode-fault.log` (with
  `w9d-demo-20261118-031226.json`) and `…-2-carry-closed-clean.log` (with `w9d-demo-20261118-042519.json`).
- SolidWorks time about 1 h 35, of which the first invocation 72 min.

| Section | Run | Time | ok | FAIL | STOP | SolidWorks private after (peak logged) |
|---|---|---|---|---|---|---|
| fixture | 1 | 564 s | 20 | 0 | 0 | 1.07 GB (1.63 GB after the quiet press) |
| carry-gates | 1 | 773 s | 27 | 0 | 0 | 1.31 GB (1.71 GB after the build) |
| carry | 1 | 1716 s | 45 | 0 | 0 | 1.21 GB (2.07 GB after the build) |
| carry-closed | 1 | 1242 s | 45 | 1 | 0 | 1.30 GB (2.33 GB after the build) |
| carry-closed | 2 | 1208 s | 46 | 0 | 0 | 1.60 GB (2.38 GB after the build) |

Free memory never went under 9.6 GB. Run 1's `carry-closed` is superseded by run 2 for its one FAIL; everything
else of run 1's `carry-closed` read the same in run 2. No dialog came during a job: SolidWorks' notification box
came twice outside one (log 1:595-596, 1399-1400, exempt), and the rest were progress boxes that close themselves.

**The script's fault, fixed (41afa37).** Run 1's `carry-closed` FAILed M2 on one mate (log 1:2345):
`{'UserAxis9': ['a None where a feature']}`.
- What was read: in RangeBox_r2, UserAxis9's entity on Sprocket-9 (carried as Sprocket-6) came back with reference
  None and feature None, its `EntityParams` read (the run's JSON, `carry-closed.definitions`). The old assembly's
  read of it, taken with L showing as saved, gave Sprocket-9's Gear Axis.
- Why: the script read the new definitions where `every_mode` leaves RangeBox_r2, its first mode H, and Sprocket-9
  is suppressed in H. The same read on the open path gives the same None: in `carry` the old assembly showing H read
  UserAxis9's entity on Sprocket-9 as reference None too (`carry.old_before.definitions`). So it is the mode of the
  read, not the remade mate (an inference from the two reads, the mate itself read on and code 0 in every mode,
  log 1:2346-2347).
- The fix: `definitions_in` shows the mode the old assembly's read was taken in (rebuilt as `every_mode` does, the
  first mode put back after) before reading. In `carry` that mode is H, where RangeBox_r2 already stands, so `carry`
  reads as before. No check was changed or loosened; self-check 0 failed.
- Run 2 (41afa37): UserAxis9 read Gear Axis on Sprocket-9 and the check passed, every one reached (log 2:784).

**The app.** No FAIL was the app's. Both faults of the first run are gone at this head: the r3 walk carried its
candidates (log 1:826-832, 1.16 to 1.69 s per candidate, nothing capped), and the carry did not stop, so every mate
expected was made again and the tie fell back.

**Against the plan's Done-when (`carry`, log 1):**
- after Sun's Flank change and a shaft Aux added, Build again… made RangeBox_r2 (723 s), saved as today, the old
  assembly read open (1409);
- both clusters carried, all 17 components (1477), each placed against the fixture's anchor, Housing-1 by its world
  frame as ruled (1480), at its pose against its anchor in every mode where it is resolved, 49 reads, none off
  (1505); every mate expected made again (1476), its definition and entities read back equal by the script's own
  read (1484), on in the modes it was on in (1486), kept under its own name (1499);
- the mate on Sun's end face named: UserSunFace `part new`, its Flank changed (1471), named by name in the question
  (802); UserGearFillet likewise (1474); UserGearRoot made again on the new Sun's Gear Axis;
- the Keyway in Sun's part named in the question, made new because its Flank changed, with the time read (800), and
  in the result with why (1470);
- every app gear free to turn in every mode with the carried mates on (1503), and W9b's read clean in H, N and L
  (1506-1511); no interference with a carried component, none named (1514);
- the carried items left unsaved, GetSaveFlag True (1518); the record at schema 10 with `unsaved_at` the file's time
  and the footer's carry line (1534); after the user's save of RangeBox_r2, nothing in it reading lightweight, the
  line goes (1540, 1552);
- the old assembly and every user file unchanged on disk (1404), its save flag, mode, frames, states, mates, flags and
  entities as before but M1 (b)'s set-apart (1402-1403), no traced write, show, rebuild, save or close of either and
  nothing saved after the first save (1406).

**Further items of §15 shown:**
- the tied cluster alone fell back by `FELL_TIE`, UserLock8a deleted, UserAngle8b kept, Housing-1 and Sprocket-8
  fixed (1478), both reading fixed in every mode at the same frame, Housing-1 at its world frame in the old assembly
  (1487-1489); UserAngle8b between the two read code 0 in every mode (1500);
- Sprocket-7 suppressed in L alone and Sprocket-9 in H alone, by the script's shown read, the route and the carry
  (1481); every other component resolved everywhere (1482);
- SprocketConf-1 inserted in Z20 and read Z20 in every mode (1515), R reading Z20 beside its document's Default
  (1516); SprocketLight-1's configurations read from its file closed (1517);
- UserAsm6 named `unread` beside the lightweight SprocketLight-1, UserAxisLight `lightweight`, UserAxis9 `unread`
  as suppressed in H, the mode showing (1472-1475), each as `expected_outcome` says (1476);
- `carry-gates` (log 1): the question led by `CARRY_INSERTS_ON_2026` with the Keyway (154); the press built
  RangeBox_r2 (270 s) and carried nothing, 48 items named (655), no r3 walk (654), the result W9a's sentence led by the
  finding (656), the record at schema 10 with `unsaved_at` 0 and no footer line (672-673), nothing written to the old
  assembly or a user file (598-601); each gate's own refusal by `plan_carry` on that read keeps its items back (685,
  696, 707, 718, 729);
- `carry-closed` (log 2): R.2 refused the copy as copied (75); after the save with L showing (77), R read the old
  assembly read-only, L showing, nothing left open or marked (771), the job closing it again (772); UserAsm6 and
  UserAxisLight made again, only UserSunFace, UserAxis7 (suppressed in L, the mode showing) and UserGearFillet named
  (776); contradiction 6, Sprocket-2 read in L and placed against RangeSlv in H, at its pose against it in every mode
  (818); the record another version wrote refused (841), and the 2024-saved file refused by closed reads only (845);
  RangeBox_r2 closed unsaved and the later Update said the carry was lost, its mark gone (847, 859).

**Facts logged for the first time** (log 1 unless said):
- `swConstrainedStatus_e` as `swconst.tlb` gives it (67): 1 swUnknownConstraint, 2 swUnderConstrained, 3
  swFullyConstrained, 4 swOverConstrained, 5 swNoSolution, 6 swInvalidSolution, 7 swAutosolveOff. In the fixture Sun
  read 3 with the tie on (68). Status 5 came once: Sprocket-9 (carried as Sprocket-11) in H, where it is suppressed,
  in `carry` (1502); it read 2 in N and L. Sprocket-7 suppressed in L read 2 there, and in `carry-closed` every
  carried component read 2 or 3 in every mode (2364). So 5 is not tied to suppression alone; why that one read 5 is
  not traced.
- One FixComponent in H fixes a component in every mode: Housing-1 and the fallen Sprocket-8 read `IsFixed` True in
  H, N and L with frames that do not move (1487-1489; log 2:787-789), the worker saying one FixComponent (1490).
- FlipDimension and `IMate2.Flipped` of every distance and angle mate, UserAngle8b's first making included, read 0 and
  False before and after (1491-1496; in `carry-closed` UserAsm6 too, log 2:791-797). With no mate reading 1 or True, which of the
  two stands for AddMate5's Flip is still not told apart.
- A gear mate's alignment read 2 before and 2 after on UserGear6 and UserGearRoot (1497-1498), not judged.
- `GetObjectByPersistReference3`'s out code: not in the return (`returned_tuple` False) and the by-reference parameter
  0 after the call, every time; `IEntity.GetType` 2 on the faces resolved, 5 on axes, 4 on planes (from 825 on).
- R's old-entity reads (`entity_reference`) took 2.1 to 2.8 s each, about as on 34.0.0.
- The build itself took 723 s in `carry` and 654 s (run 2: 625 s) in `carry-closed`, against 270 s with nothing
  carried in `carry-gates`.
- Component instance numbers in RangeBox_r2 followed the order of insertion and differed between the two
  `carry-closed` runs (Housing-1 as Housing-2 in run 2, log 2:778), the poses and mates held either way.

**Gate proposals printed** (`carry`, log 1; nothing set in findings.py):
- 1408: `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY_ON_2026 = True`, SprocketLight-1 read 1 before
  and 2 after, set apart: its state and its file going from not open to open, unmarked;
- 1553: `CARRY_INSERTS_ON_2026 = True`, every condition True;
- 1554: `CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026 = True`;
- 1555: `REFERENCED_CONFIGURATION_READ_ON_2026 = True`;
- 1564: `CARRY_REMAKE_KINDS_ON_2026 = ('coincident', 'concentric', 'parallel', 'distance', 'angle', 'limit distance',
  'lock', 'gear')`, the mates standing for each kind at 1556-1563;
- 1565: `CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2026 = True`, UserGear6 on the new Sun's Gear Axis, UserGearRoot remade;
- 1566-1571: `CARRY_INSERTS_A_SUBASSEMBLY`, `CARRY_REMAKES_ON_A_LEAF`, `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`,
  `ORIGIN_ENTITY_READ` and `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` `_ON_2026 = None`, none of them in the fixture.

These come from `carry` at f7c2f0d. The fix of 41afa37 changes nothing `carry` reads (its old read and RangeBox_r2
both stand in H), and `carry-closed` prints no proposal.

**Not measured by this run:** every 2024 value; `FELL_NEW_ERROR` and `FELL_OVER_DEFINED`; a user sub-assembly, a
virtual component, a pattern instance, an origin and a vertex; perpendicular, tangent and limit angle mates; a
distance or angle mate whose FlipDimension reads 1; the state route's None path (D2), which is 2024's.

## The confirming run on SolidWorks 2024 (2026-11-18, from 5aca9c1, SolidWorks 2024 32.5.0)

**Setup.**
- Run folder `<probe folder>\w9d-demo-sw2024-20261118-060436`, snapshot `snap` a `git archive` of 5aca9c1 with
  `SNAPSHOT_COMMIT` beside `src`. Its `--self-check` (the Linux venv, on the snapshot) read 62 ok, 0 failed before
  SolidWorks was started. 5aca9c1's `src` holds the fourteen 2024 probe reads (a3e05fe) and every W9d write gate None
  on 2024, so `carry` and `carry-closed` patched the five writes in their own process and put them back (log 1:791-795,
  1538-1542; log 2:81-85, 837-841).
- Two sessions of SolidWorks 2024 (32.5.0 in both logs and both JSON files), each started for its invocation and
  exited after it: PID 52508 for `fixture,carry-gates,carry`, PID 32312 for `carry-closed`. Each log reads
  `open before: []` (line 5). No other SolidWorks, Excel or Python was running before either (the operator's
  account, by `tasklist`); each invocation started and quit its own Excel. Each SolidWorks exited on a plain close
  request (`taskkill` without `/F`) within 45 s, nothing of the run open.
- Masters, only copied: S0's 2024 `rangebox.master` (`<probe folder>\w9-s0-sw2024-20261116-064725\out`) and W9a's
  2024 `setup.master` (`<probe folder>\w9a-confirm-sw2024-20261117-002313\out`); the second session took the
  `w9d-fixture.master` the first kept in the same `out` (log 2:11). `--other-version-file`: `RangeBox_r2.SLDASM` of the
  second 2026 run's `carry` (`<probe folder>\w9d-demo-sw2026-20261118-031029\out\carry`), read closed only. The md5 of
  every file of the two master folders and of that file was the same before and after (the operator's account).
- Both invocations with `--close-outlived-whats-wrong` (log 1:8, log 2:8). The second also named `--master` and
  `--user-master`, as `W9D-PROBES-REVIEW.md`'s 2024 command line does; it used neither.
- Logs `probe/results/sw2024/w9d-demo-sw2024-20261118-1-fixture-gates-carry-clean.log` (with
  `w9d-demo-20261118-060738.json`) and `…-2-carry-closed-clean.log` (with `w9d-demo-20261118-073438.json`).
- SolidWorks time about 2 h: the first invocation 84 min, the second 34 min, plus starting and exiting.

| Section | Session | Time | ok | FAIL | STOP | SolidWorks private after (largest logged) |
|---|---|---|---|---|---|---|
| fixture | 1 | 846 s | 20 | 0 | 0 | 1.77 GB (6.41 GB after the quiet press, 1:80) |
| carry-gates | 1 | 1228 s | 27 | 0 | 0 | 2.71 GB (6.34 GB after the build, 1:592) |
| carry | 1 | 2990 s | 45 | 0 | 0 | 5.57 GB (11.03 GB after the build, 1:1397) |
| carry-closed | 2 | 2054 s | 46 | 0 | 0 | 3.59 GB (9.12 GB after the build, 2:706) |

Each log ends `done 0 failed: []; … 0 STOP(s)` (1:1586, 2:870). The least free memory logged was 8.62 GB (1:1397);
the operator's samples between log lines never read under 8.48 GB. Between sections SolidWorks stood at 1.77, 2.71
and 5.57 GB private, under the 7 GB at which the session would have been ended, so session 1 ran its three sections
through; inside `carry`'s build it reached 11 GB, and inside `carry-closed`'s 9.1 GB, against 2.4 GB at most on 2026.

**No FAIL, no STOP, no script change.** Nothing in `probe/w9d_demonstration.py` or `src` was changed for this run, and no
check was changed.

**The boxes, every one.**
- **No What's Wrong** came in either session, and the close path never fired: neither log has an *outlived* line.
- **SolidWorks' notification box** (Title, Description, two buttons, two links; exempt by the coordinator's ruling,
  nothing answers it) came five times:
  - in `carry`'s Build again…: at 1:856-857, between R's entity reads and the first insert, "while no SolidWorks call
    was in progress", and at 1:959-960, while `GetNextSubFeature` was in progress, during the remakes;
  - at the script's own reads after that press: 1:1400-1401 (`GetNextSubFeature`) and 1:1482-1483 (`GetNextFeature`);
  - in `carry-closed`'s Build again…: 2:265-266, while `GetNextSubFeature` was in progress.
  Each job went on and returned its result; the run's summary lists them as noted (1:1582-1585, 2:869).
- **SolidWorks' open-progress window** (`Opening Component …`, `Opened 15 Components … Post load updating`, with a
  Close button) came at 1:24 and 1:42 (the fixture's opens), and at 2:20, 2:76 and 2:105; 2:105 is inside the job's
  read-only open of the old assembly. Each closed by itself.
- **SOLIDWORKS CAM's box** on saving an assembly with a lightweight component did not come. The script saved no
  assembly holding one: SprocketLight-1 read lightweight alone before the press (1:755), came out resolved (below),
  and RangeBox_r2 read no lightweight component before the user's save (1:1544).

**Against the plan's Done-when (`carry`, log 1):**
- after Sun's Flank change and a shaft Aux added, classify sends it to Build again… as RangeBox_r2 (789); Build again…
  made RangeBox_r2 (1389 s, 1399), saved as today, the old assembly read open (1410);
- both clusters carried, all 17 components (1478), each placed against the fixture's anchor, Housing-1 by its world
  frame as ruled (1481), at its pose against its anchor in every mode where it is resolved, 49 reads, none off (1508);
  every mate expected made again (1477), its definition and entities read back equal by the script's own read (1487),
  on in the modes it was on in (1489), kept under its own name (1502);
- the mate on Sun's end face named: UserSunFace `part new`, its Flank changed (1472), named by name in the question
  (799); UserGearFillet likewise (1475); UserGearRoot made again on the new Sun's Gear Axis (1477, 1568);
- the Keyway in Sun's part named in the question, made new because its Flank changed, with the time read (797), and in
  the result with why (1471);
- every app gear free to turn in every mode with the carried mates on (1506), and W9b's read clean in H, N and L
  (1509-1515); no interference with a carried component, none named (1517);
- the carried items left unsaved, GetSaveFlag True (1521); the record at schema 10 with `unsaved_at` the file's time
  and the footer's carry line (1537); after the user's save of RangeBox_r2, nothing in it reading lightweight (1544),
  the line goes (1555);
- the old assembly and every user file unchanged on disk (1405), its save flag, mode, frames, states, mates, flags and
  entities as before but M1 (b)'s set-apart (1404, 1409), no traced write, show, rebuild, save or close of either and
  nothing saved after the first save (1407);
- confirmed on 2024: this run, reviewed in `W9D-DEMONSTRATION-REVIEW.md`'s last section (e51de95), which allows the
  2024 findings; they are set in `findings.py` (e7a3577).

**Further items of §15 shown:**
- the fixture (log 1): the three parts of their own built by the strip (11-13); every mate made (67) and on in H at
  code 0, Sun reading 3 (swFullyConstrained) with UserAngle8b's tie on (70-71); Sprocket-7 suppressed in L alone and
  Sprocket-9 in H alone (72); SprocketConf-1 referencing Z20 in every mode by the put (73); the quiet press went
  through in 458 s and recorded the inventory whole (80, 88-89);
- the tied cluster alone fell back by `FELL_TIE`, UserLock8a deleted, UserAngle8b kept, Housing-1 and Sprocket-8
  (carried as Sprocket-9) fixed (1479), both reading fixed in every mode at the same frame, Housing-1 at its world
  frame in the old assembly (1490-1492); UserAngle8b between the two read code 0 in every mode (1503);
- Sprocket-7 suppressed in L alone and Sprocket-9 in H alone, by the script's shown read, the route and the carry
  (1484); every other component resolved everywhere (1485);
- SprocketConf-1 inserted in Z20 and read Z20 in every mode (1518), R reading Z20 beside its document's Default (1519,
  820); SprocketLight-1's configurations read from its file closed, `('Default',)` (1520);
- UserAsm6 named `unread` beside the lightweight SprocketLight-1, UserAxisLight `lightweight`, UserAxis9 `unread` as
  suppressed in H, the mode showing (1473-1476), each as `expected_outcome` says (1477); UserAxis7 in L, where
  Sprocket-7 is suppressed, set on and read on, not judged (1488);
- the result names a fallen component with its old name, *Housing-1 and Sprocket-9 (was Sprocket-8) are fixed where
  they stood* (1398), the review's must-fix 1 as it now reads on SolidWorks;
- `carry-gates` (log 1): the question led by `CARRY_INSERTS_ON_2024` with the Keyway (154); the press built
  RangeBox_r2 (429 s, 594) and carried nothing, 48 items named (653), no r3 walk (652), the result W9a's sentence led
  by the finding (654), the record at schema 10 with `unsaved_at` 0 and no footer line (670-671), nothing written to
  the old assembly or a user file (596-599); each gate's own refusal by `plan_carry` on that read keeps its items back
  (683, 694, 705, 716, 727);
- `carry-closed` (log 2): R.2 refused the copy as copied (75); after the save with L showing (78), R read the old
  assembly read-only (`open_read_only` 3.0 s, 106), L showing, by `GetComponentSuppressionState(Name2)`, nothing left
  open or marked (724, 773), the job closing it again (`close_unsaved` 0.3 s, 160; 774); the old assembly and every user
  file unchanged on disk (709), the traced calls on them the job's own `OpenDoc6`/`QuitDoc` of the old assembly and
  the opens of the user's parts for their inserts, as on 2026 (710-711); UserAsm6 and UserAxisLight made again, only
  UserSunFace, UserAxis7 (suppressed in L, the mode showing) and UserGearFillet named (775-778); all 17 carried (779),
  the tie fallen back with Housing-1 (as Housing-2) and Sprocket-8 fixed in every mode (780, 789-791); every remade
  mate equal and on as before (786, 788); contradiction 6, Sprocket-2 read in L and placed against RangeSlv in H, at
  its pose against it in every mode (820); the record another version wrote refused (843), and the 2026-saved file,
  read as 19000 against this SolidWorks' 17000 (844, 846), refused by closed reads only (847); RangeBox_r2 closed
  unsaved and a later Update (86 s) said the carry was lost, its mark gone (849-861).

**Facts logged** (log 1 unless said):
- One FixComponent in H fixes a component in every mode on 2024 too: Housing-1 and the fallen Sprocket-8 read
  `IsFixed` True in H, N and L with frames that do not move (1490-1492; log 2:789-791).
- FlipDimension and `IMate2.Flipped` of every distance and angle mate read 0 and False before and after
  (1494-1499; log 2:793-799, UserAsm6 too). Which of the two stands for AddMate5's Flip is still not told apart.
- A gear mate's alignment read 2 before and 2 after on UserGear6 and UserGearRoot (1500-1501), not judged.
- `GetObjectByPersistReference3`'s out code: not in the return and the by-reference parameter 0 after the call, every
  time; `IEntity.GetType` 2 on faces, 5 on axes, 4 on planes, as on 2026.
- `GetConstrainedStatus` of the carried components read 2 or 3 in every mode in both sections (1505; log 2:807). No 5
  was read on 2024.
- Sun's frame in the old assembly and in each mode of RangeBox_r2 the same, at z 5.5 (1507; log 2:809).
- Component instance numbers in RangeBox_r2 followed insertion order and differed between the two sections
  (Sprocket-8 as Sprocket-9 in `carry`, Housing-1 as Housing-2 in `carry-closed`); the poses and mates held either way.

**What differs from 2026** (measured; the 2026 figures are the second 2026 run's):
- **Time.** Sections 846, 1228, 2990 and 2054 s against 564, 773, 1716 and 1208 s: 1.5 to 1.7 times. The builds: 429 s
  in `carry-gates` (270 s), 1389 s in `carry` (723 s), 1161 s in `carry-closed` (654 and 625 s); the fixture's quiet
  press 458 s.
- **Memory.** SolidWorks 2024 rose to 11.03 GB private in `carry`'s build and 9.12 GB in `carry-closed`'s, and gave
  most of it back once the copy closed (5.57 and 3.59 GB after the sections); 2026 stayed under 2.4 GB. Free memory
  never went under 8.4 GB, so nothing was cut for it.
- **R's reads are slower.** `entity_reference` took 3.7 to 6.5 s each in `carry` (53 reads) and 3.5 to 4.4 s in
  `carry-closed` (27), against 2.1 to 2.8 s. The r3 walks carried the same candidates: 3.1 to 4.4 s per candidate on
  Chain-2, Chain-1 and Sprocket-5 in `carry` (823-827) and 2.2 to 2.7 s in `carry-closed` (2:126-130), against 1.16 to
  1.69 s; Sun's 87 candidates at 0.095 and 0.072 s each (829; 2:132). Nothing was capped. That the walks did not
  grow through either session is read from these few lines only.
- **The face prefilter barely narrowed Sun's faces.** On Sun's part (235 faces) the area key kept 29 for UserGearRoot
  and 58 for UserGearFillet, 87 carried (829; 2:132), where on 2026 it kept 1 and 2, 3 carried (2026 log 1:832);
  `IsSame` still found exactly one each. That the 2024-built Sun's equal tooth faces read equal areas to within the
  key's tolerance, where 2026's did not, is the review's likely reason, not traced. On 2024 a face mate on a gear's
  root cylinder or fillet therefore carries about one candidate per tooth (two for a fillet), so the 200-candidate cap
  comes at about 100 teeth for a fillet and 200 for a root, and then names the mate; the cost is time, not a wrong
  answer.
- **Constrained status 5 did not come.** On 2026 the old Sprocket-9, suppressed in H with no mate on it in the new
  assembly, read 5 there (2026 log 1:1502); on 2024 the same component (carried as Sprocket-3) read 2 in H (1505). So
  the review's *suppressed and unmated* pattern for 5 is 2026's only; nothing in the app depends on 5 (the review's §6).
- Everything the checks judge read the same as on 2026: the outcomes per mate, the names, the fallback, the states,
  the anchors and poses, the configuration, the record, the footer, R.2's refusals and the lost line. SprocketLight-1
  came out resolved in the old assembly on 2024 too (1409).

**Gate proposals printed for 2024** (`carry`, log 1; set since in findings.py as the review allows, e7a3577):
- 1409: `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY_ON_2024 = True`, SprocketLight-1 read 1 before
  and 2 after, set apart: its state and its file going from not open to open, unmarked;
- 1556: `CARRY_INSERTS_ON_2024 = True`, every condition True;
- 1557: `CARRY_INSERTS_IN_A_CONFIGURATION_ON_2024 = True`;
- 1558: `REFERENCED_CONFIGURATION_READ_ON_2024 = True`;
- 1567: `CARRY_REMAKE_KINDS_ON_2024 = ('coincident', 'concentric', 'parallel', 'distance', 'angle', 'limit distance',
  'lock', 'gear')`, the mates standing for each kind at 1559-1566, the same mates as on 2026;
- 1568: `CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2024 = True`, UserGear6 on the new Sun's Gear Axis, UserGearRoot remade;
- 1569-1574: `CARRY_INSERTS_A_SUBASSEMBLY`, `CARRY_REMAKES_ON_A_LEAF`, `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`,
  `ORIGIN_ENTITY_READ` and `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` `_ON_2024 = None`, none of them in the fixture.

Each is its 2026 twin's value. `carry-closed` prints no proposal; its lines above are the closed path's evidence.

**Not measured by this run:** `FELL_NEW_ERROR` and `FELL_OVER_DEFINED`; a user sub-assembly, a leaf, a virtual
component, a pattern instance, an origin and a vertex; perpendicular, tangent and limit angle mates; a distance or
angle mate whose FlipDimension reads 1; a gear mate of the other sense remade; the state route's None path (D2), which
no version now takes; a What's Wrong during a carry, and with it the close path under W9d (no box came); an edge mate,
and so the edge prefilter's cost the probe review flagged (the fixture has none); the user's work in error at a Build
again….

## Command lines

2026 (fresh session; `RUN` the run folder with `snap` the repo snapshot):

```
python.exe RUN\snap\probe\w9d_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9d-demo-sw2026-1.log ^
    --sections fixture,carry-gates,carry,carry-closed --master <S0's rangebox.master> ^
    --user-master <W9a's setup.master> --other-version-file <a 2024-saved assembly, e.g. W9c's 2024 setup.master's RangeBox.SLDASM>
```

About 1 h 30 to 1 h 45. 2024, after the 2024 W9d probes, in fresh sessions (each about twice as long):

```
python.exe RUN\snap\probe\w9d_demonstration.py RUN\snap\src RUN\out24 --pid PID --log RUN\w9d-demo-sw2024-1.log ^
    --sections fixture,carry-gates,carry --master <2024 rangebox.master> --user-master <2024 setup.master> ^
    --close-outlived-whats-wrong
python.exe RUN\snap\probe\w9d_demonstration.py RUN\snap\src RUN\out24 --pid PID --log RUN\w9d-demo-sw2024-2.log ^
    --sections carry-closed --other-version-file <a 2026-saved assembly> --close-outlived-whats-wrong
```

`--close-outlived-whats-wrong` (2024 only; the coordinator's ruling of 2026-11-18 on a What's Wrong that outlives its
job, extended the same day to every demonstration run on 2024 that asks for it, `ISSUE-1-PLAN.md`): W9c's close
path, wired by W9d's own `main` (not inherited: W9d calls W9a's `main`, never W9c's). A What's Wrong owned by
SolidWorks' frame, the frame enabled, still up 60 s after a job is logged as having outlived it, with the job and the
call it came at, and closed with its own Close button (a visible, enabled Button; `BM_CLICK`, then its `WM_COMMAND`
as a second try), gone within 10 s of the last try; the log says which press closed it. Anything else stays the
STOP, so one such box no longer ends an unattended 2024 run. Without the flag the run is as before. Not given on
2026, where no box shows and the path is not in force anyway.

The second run finds `w9d-fixture.master` in the same `RUN\out24`, or takes `--fixture-master`. Folders are written
`<probe folder>\…` in any note about a run.
