# W9d's probes: what they ask, what sets which finding, and how to run them

The script is `probe/w9d_probes.py`. It measures what `W9D-INTERFACES.md` §11 owes before W9d's packages rely on it:
the three things the plan's last section names, plus the calls W9d adds that the app has never made and that could
raise a dialog or change a document. It proposes findings in the log (`propose NAME = value  # evidence`) and sets
none; each is set per version (`_ON_2026`, `_ON_2024`) from the reviewed log. **Revised** to the review
(`W9D-INTERFACES-REVIEW.md`, `f0eb516`): every probe fault P1–P13 is taken (the table at the end); then to its re-check (`8d3695b`): R2, S-b, S-c and S-d
are in the script, R1, S-a, S-e, S-f and S-g in the contract.

**How it runs.** As W9c's probes do: it runs W9a's script's `main` with its own three sections, through
`probe/w9c_probes.py` (imported for the watch, `swconst`, `mate_definition`, `select_face`, `raw_mate`, `open_doc6`,
`p2_make_sub`). So the attach and PID check, the dialog watch and the What's Wrong rule, keep-awake, the JSON after
every section (`w9d-probes-<time>.json`), APPDATA in the run folder and the guarded close are W9a's, unchanged. No
document title but the run's own is logged, and never SolidWorks' frame title. Every document is a copy in the run's
folder or one the script makes, closed unsaved at its section's end; the only saves are of the probe's own copy
(`Save3`, so the reads start unmarked, as W9c's s5 (e)) and of assemblies the script makes (the app's `save_as`).

**Masters:** `--user-master` (W9a's `setup.master` for this version; built here first through W9a's builders when not
given, which needs `--master`, S0's `rangebox.master`). **`--other-version-file`**: a file the *other* SolidWorks last
saved, read closed by `VersionHistory` only, never opened — `FILE_VERSION_READ`'s negative control (S-b).

## Sections, in order

| Section | What it asks | Proposes | 2026 (estimate) |
|---|---|---|---|
| `faces` | (a) On a copy of setup.master, Sprocket-5, -6 and -7 inserted and four mates made through `GetCorresponding` (m1's route): a concentric on Sprocket-5's bore face to Input Axis; a coincident between Sprocket-5's and Sprocket-6's end faces; a concentric on Sprocket-6's circular bore edge; a **parallel** (a kind never made or read before) between Sprocket-7's end face and Sun's; the copy then saved and read unmarked (P1). (b) Each face or edge entity: its `ReferenceType2` and the kind it gives, against which of `GetSurface`, `GetCurve`, `GetPoint` answer; what `IEntity.GetComponent` names; its coaxial read (`CylinderParams` of the part-level face against the part's Z axis); three routes to its part-level reference — **r1** `GetCorrespondingEntity2` in the assembly then the part's `GetPersistReference3`, **r2** the mate's entity straight to the part's `GetPersistReference3`, **r3** (the follow-up round, below) the part's faces or edges carried into the assembly by `IComponent2.GetCorresponding` and the one `IsSame` as the mate's entity, then the part's `GetPersistReference3` — each resolved in the part, carried back through the component and held to the original by `ISldWorks.IsSame` (else the face's area); the assembly-context reference's length (read only); Sun's cylindrical faces, its off-axis User Keyway among them, read for coaxial (the negative control, S-d), and the coaxial read taken on r2's resolved entity too; each face's and edge's place in its part (a plane's offset, a cylinder's or circle's axis); each user component's `ReferencedConfiguration`, its document's active configuration and configuration names, `IsVirtual` and `IsPatternInstance` (facts, R2); GetSaveFlag of every document around, and which were already marked at the start. (c) The four made again in a second assembly, each entity by its own kind's clean route (P10), layout and Sun fixed, definitions and frames compared; the copy's documents' flags read before the inserts, after them and after the mates. (d) The second assembly and the copy closed, each part opened alone, every face and edge reference resolved there again and held to its kind, its place in the part and a face's area, the save flags read around each resolve (P12, S-c; the not-open path's resolve). | `PERSIST_REFERENCE_ROUTE_FOR_FACES`, `_FOR_EDGES`, `COAXIAL_FACE_READ`, `CARRY_INSERT_MARKS_USER_DOCUMENTS`, `PERSIST_REFERENCE_SURVIVES_RELOAD` | 6 min |
| `state` | (a) On a copy of setup.master, Housing-1 suppressed in H (the mode showing) and Sprocket-4 in L, saved and read unmarked; Sprocket-4's mates' flags read unshown (a fact). (b–d) With nothing shown, GetSaveFlag of every document around each, the start's flags kept (P4): **candidate 1** `IConfiguration.GetComponentSuppressionState(Name2)` per mode; **candidate 2** `GetRootComponent3(False)` per mode; **candidate 3**, W9c's marking route taken apart call by call for each mode not showing, naming the first call that marks (P5); then the truth, each mode shown. (e) Sprocket-2 suppressed in N and **not saved**: candidate 1 again (proposed only when (b–d) chose it, P6). (f) Sprocket-1 set lightweight: candidate 1, the active configuration's `GetRootComponent3(False)` and `(True)`, every state after each — facts only (P7); all resolved again. Then the copy closed. (v) Closed-file reads only: the copy's `ISldWorks.VersionHistory` against `GetLatestSupportedFileVersion`, the other version's file's `VersionHistory` (S-b), and the copy's `GetDocumentDependencies2` with each dependency's `VersionHistory` (S-f). (g) The Housing part opened unchanged and the Sprocket part opened and changed (a global added); the assembly opened `Silent | ReadOnly` beside them under the watch; what became of each part (open, flag, read-only; the global read back, P2); candidate 1 there; its modes shown. (h) That read-only document closed unsaved (`QuitDoc`) under the watch, 3 s waited inside the job; every document it loaded checked gone (P3), both parts as they were after the open, the shows and the close, every file's time unchanged. | `COMPONENT_STATE_PER_CONFIGURATION_ROUTE`, `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED`, `FILE_VERSION_READ`, `DEPENDENCIES_READ`, `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS`, `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` | 8 min |
| `sub` | A healthy sub-assembly made from a copy of the sprocket. (a) Not loaded: `OpenDoc6` Silent, its flag straight after and after 5 s. (b) Opened `Silent | ReadOnly`, a new assembly saved, the sub-assembly inserted by `AddComponent5` (of a read-only document: new): inserted, its children, its flag and read-only state. (c) A host holding it made in `p2_make_sub`'s order and saved by the app's `save_as` only (P8), reopened so the sub-assembly is loaded as a component only; `OpenDoc6` of it (the warning, its flag), then inserted into another new assembly (its flag). Every step under the watch; a dialog that comes and goes ends that step with a STOP line and its finding proposed None (P9). | `SUBASSEMBLY_OPEN_MARKS`, `SUBASSEMBLY_READ_ONLY_INSERT`, `SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED` | 3 min |

**About 19 minutes on 2026** with the harness's start (attach, Excel) and setup.master given; **about 37 minutes on
2024** (S5 ran 1.6–2× slower there), in one fresh session or each section in its own.

**Which answer sets which finding** (each per version; *settled when* as `W9D-INTERFACES.md` §8):

- `COMPONENT_STATE_PER_CONFIGURATION_ROUTE`: the candidate that agrees with the shown truth on every component and mode
  (Housing-1 suppressed in H only, Sprocket-4 in L only, Sprocket-2 nowhere) **and** turned no document's flag on,
  from a bracket that started with the assembly unmarked. Candidate 1 is proposed as
  `IConfiguration.GetComponentSuppressionState(Name2)`. None if neither 1 nor 2 does.
- `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED`: proposed only when candidate 1 was chosen; True when it reads
  Sprocket-2 suppressed in N after the unsaved change.
- `FILE_VERSION_READ`: the route string only when **both** hold: the closed copy's last `VersionHistory` entry is the
  version `GetLatestSupportedFileVersion` gives (the copy was saved by this SolidWorks in (a)), and the other version's
  file reads a different one (S-b); None without `--other-version-file` or when either read fails. It gates the
  not-open read at all (the contract's R1), so it is never set from the same-version control alone.
- `DEPENDENCIES_READ`: the route string when `GetDocumentDependencies2` of the closed copy names Sprocket.SLDPRT,
  Housing.SLDPRT and the layout part, and every dependency's `VersionHistory` answers.
- `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS`: True when, after the read-only open, the Housing part is still open, unmarked
  and not read-only, and the Sprocket part still open, changed (its global read back) and not read-only; None when the
  Housing part was not unmarked before the open.
- `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN`: True when the read-only document's modes were shown, it closed by `QuitDoc` with
  no dialog, it and every document it loaded are gone, both parts are as they were after the open, the shows and the
  close, and no file's time changed.
- `PERSIST_REFERENCE_ROUTE_FOR_FACES` / `_FOR_EDGES`: the first route (r1, then r2, then r3) clean on every face (five)
  or the one edge — read, resolved to its own kind, the round trip the same object — from a bracket that started
  unmarked and marked nothing. r3 is held to more (below). A resolve to another kind is §0.3's STOP for W9d and is said in the log as such.
- `PERSIST_REFERENCE_SURVIVES_RELOAD`: True when every face and edge reference (the route proposed for its kind) resolves again, in its part opened alone
  after the copy closed, to its own kind, **its own place in the part** (a sprocket's two end faces have the same area,
  S-c) and a face's own area, and the resolve's bracket starts unmarked and marks nothing; None otherwise.
- `COAXIAL_FACE_READ`: True when Sprocket-5's bore reads coaxial by every route's part-level entity that was read (r1,
  r2, r3), every other face reads not (a plane is not a cylinder; a face with no read at all is not clean), and **Sun's User Keyway** (an off-axis Ø3 cylinder in Sun's part, which setup.master holds) reads not — the
  control the rule exists for (S-d) — from an unmarked start marking nothing. No keyway read: not proposed True.
- `REFERENCED_CONFIGURATION_READ`: **not proposed** (the re-check's R2). Every component here references its file's
  only configuration, so a read that answered the active one whatever was referenced would look right: the read is
  logged as a fact, and M9 sets the finding on Sprocket-11, whose configuration differs. `IsVirtual` and
  `IsPatternInstance` are likewise facts: `VIRTUAL_READ` and `PATTERN_INSTANCE_READ` stay None.
- `CARRY_INSERT_MARKS_USER_DOCUMENTS`: True when inserting the user's parts into the second assembly turned any of the
  copy's documents on; None when one was already on before (P11).
- `SUBASSEMBLY_OPEN_MARKS` / `_WHEN_LOADED`: True when that open turned the sub-assembly's flag on (settled when
  **False**); None when it was already on or a dialog came. `SUBASSEMBLY_READ_ONLY_INSERT`: True when the read-only
  sub-assembly inserted with its child and its flag stayed off.

**r3, the follow-up round's route** (added after the first 2026 run, whose r1 and r2 read nothing; from that run's hand
diagnostic). For each mate entity, every face (an edge: every edge) of its component's part is carried into the assembly
by `IComponent2.GetCorresponding` and compared with the mate's entity by `ISldWorks.IsSame`. All of them are walked, so
the matches are counted, and exactly one must match: none, or several, is not clean, said with the count. That
part-level entity's place and coaxial read are taken. Its `GetPersistReference3` is resolved in the part by
`GetObjectByPersistReference3`, the code said by its `swPersistReferencedObjectStates_e` name. The round trip must
hold both ways, with no area fallback: the resolved object of the entity's kind and `IsSame` as the part-level entity,
and carried back through the component `IsSame` as the mate's entity. It has its own bracket: every document of the copy
(the assembly and its parts) read before and after, starting unmarked and marking nothing. The walk's count, its
seconds and the route's are logged per entity: the app would pay this walk per mate, and a gear part has hundreds of
faces. (c) and (d) use the route (b) proposes for each kind. `--self-check` holds r3's judgement on made-up readings
(63 checks).

Logged as facts, proposing nothing: the root read with a lightweight component (P7; the contract dropped
`ROOT_COMPONENT_UNRESOLVED_READ`), the remake's equal definitions (P13; the remake's gate is M9's `CARRY_REMAKE_KINDS`),
`ReferenceType2`'s kind against the members', candidate 3's first marking call.

A dialog in any step ends that case with a STOP line and its finding proposed None; a job that does not return in
120 s, or a dialog that stays, ends the run (W9c's `watched`). Recovery: a fresh SolidWorks, the remaining sections into
a fresh `<out>`, or the same with `--redo`.

## Command lines (SolidWorks 2026 first; then 2024)

`<probe folder>` is the probe folder under the Windows account's Documents (`…\Documents\GearGeneratorProbe`).

```
python.exe RUN\snap\probe\w9d_probes.py RUN\snap\src RUN\out --pid PID --log RUN\w9d-probes-sw2026.log ^
    --sections faces,state,sub ^
    --user-master <probe folder>\w9c-whole-sw2026-20261117-123612\out\setup.master ^
    --master <probe folder>\w9c-whole-sw2026-20261117-123612\out\rangebox.master ^
    --other-version-file <probe folder>\w4-demo-sw2024-20261113-200555\run\a\Reducer_12to1.SLDASM
python.exe RUN\snap\probe\w9d_probes.py RUN\snap\src RUN\out24 --pid PID --log RUN\w9d-probes-sw2024.log ^
    --sections faces,state,sub --user-master <2024's setup.master> --master <2024's rangebox.master> ^
    --other-version-file <probe folder>\w9c-whole-sw2026-20261117-123612\out\RangeBox.SLDASM
```

The 2026 control is a 12 : 1 assembly in a folder a 2024 run made on 2026-11-13 (its folder name says so; that 2024
last saved it is what the read itself shows, and if it reads otherwise the finding is simply not proposed). The 2024
control is the 2026 whole run's RangeBox. Both files are only read closed, never opened, so neither version's CAM box
can come up; whether 2024's `VersionHistory` reads a newer version's file at all is itself unknown, and a failure there
leaves the finding unproposed on 2024.

Commit the logs as `probe/results/w9d-probes-sw2026-<date>.log` and `probe/results/sw2024/w9d-probes-sw2024-<date>.log`
with their JSON.

## The run on SolidWorks 2026 (2026-11-17, from 23ed8c5)

**Setup.**
- Run folder `C:\Users\M0obo\Documents\GearGeneratorProbe\w9d-probes-sw2026-20261117-140201`, on the second Windows
  host.
- SolidWorks 2026 revision **34.0.0**, PID 41968, started for the run and exited after.
- Masters: the W9c whole run's `setup.master` and `rangebox.master`, both unchanged by the run (their files' sizes,
  times and md5 compared before and after).
- The command as above.

**Result.** `probe/results/w9d-probes-sw2026-20261117-1-face-routes-none.log` and `w9d-probes-20261117-140231.json`.

| Section | Time | Failed |
|---|---|---|
| faces | 79 s | 1 |
| state | 40 s | 0 |
| sub | 39 s | 0 |

There was no STOP, and no dialog but the progress boxes and the exempt notification box. No script change was
made.

- **faces: neither route reads a part-level reference, on any face or the edge.**
  - **r1:** `GetCorrespondingEntity2` on the assembly's extension hands back nothing for a mate entity's `Reference`.
    Its help gives the call exactly as made, and says it returns null if none is found. So r1's
    `GetPersistReference3` then meets a type mismatch.
  - **r2:** the part's `GetPersistReference3` on the assembly entity gives a 70- or 82-byte reference. In the part it
    resolves to nothing, with code 1 (`swPersistReferencedObject_Invalid`). The "GetCorresponding: Type mismatch" in
    the log is the script carrying that nothing back.
  - So both `PERSIST_REFERENCE_ROUTE_FOR_*` are proposed None, (c) has nothing to make again (its FAIL), and (d)
    resolves nothing.
  - `COAXIAL_FACE_READ` is proposed False: the part-level entity it needs came only from r1. Sun's User Keyway read
    not coaxial on its own read.
  - The reads marked nothing.
- **A hand diagnostic after the run (not this script; its code and output are in the run folder, `diag_r1.py`).** It
  ran on the run's own `d-faces` copy: opened silently, read, closed by `QuitDoc`, every flag unmarked throughout.
  - `GetCorrespondingEntity2` gave `None` for UserFaceConc's, UserEdgeConc's and UserFaceCoin's entities.
  - A third route did work for each: the part's faces (or edges) each carried by `IComponent2.GetCorresponding`, and
    the one `ISldWorks.IsSame` as the mate's entity taken. Its part-level `GetPersistReference3` (583, 599 and 8096
    bytes) resolved in the part to an object.
  - Its kind, place and round trip were not checked. A route for the probe to take up, not a measurement.
- **state:**
  - Candidate 1, `GetComponentSuppressionState(Name2)`, agreed with the shown truth on every component and mode and
    marked nothing. Candidate 2, `GetRootComponent3(False)`, gave no root in N, the mode not showing. Candidate 3's
    calls marked nothing either.
  - The unsaved suppression read right.
  - The lightweight Sprocket-1 read state 1, as the other sprockets did, through every read.
  - `VersionHistory`: the copy last (19000, 2025) against `GetLatestSupportedFileVersion` 19000. The 2024-built
    control read last (17000, 2024).
  - `GetDocumentDependencies2` named all nine parts, each one's `VersionHistory` answering.
  - The read-only open beside the open Housing (unchanged) and Sprocket (changed) answered warning 32
    (`swFileLoadWarning_NeedsRegen`). Both parts stayed open, not read-only, as they were. The read-only
    `RangeBox.SLDASM` itself read **flag True straight after the open**, its referenced Sprocket part being changed.
    It was shown mode by mode and closed by `QuitDoc` with no dialog. Every document it loaded was gone after, and no
    file's time changed.
- **sub:**
  - Opening a healthy sub-assembly marked nothing, not loaded or loaded as a component (warning 128,
    `swFileLoadWarning_AlreadyOpen`).
  - Opened read-only, it inserted with its child, its flag off.
- RAM fell to 1.84 GB free at `sub`'s end (WSL's page cache had grown), under the 2 GB floor. Dropping that cache gave
  back 4.8 GB.

## What is untested

Only `--self-check` and `--help` have run (the Linux venv, no SolidWorks): the pure judgements on made-up readings
(63 checks since r3, 0 failed). Nothing that talks to SolidWorks has run, so expect script faults first, as every probe script
here has met. In particular, unverified and resting on the API help or on reading other scripts:

- that `GetComponentSuppressionState` takes the top-level `Name2` (its example passes `IComponent2.Name`) and answers a
  Boolean through late binding;
- `GetCorrespondingEntity2`, `IEntity.GetComponent`, `ISldWorks.IsSame`, `ReferencedConfiguration`, `IsVirtual`,
  `IsPatternInstance`, `VersionHistory`, `GetLatestSupportedFileVersion` through late binding, and
  `swObjectEquality` being in `swconst.tlb` (read optionally: if missing, the area decides for faces and an edge reads
  not clean);
- the sprocket's geometry as m1 read it (a bore of radius 5 mm, end faces at −1 and +5 mm in its own coordinates),
  the circular-edge filter (`CircleParams` index 6 the radius, index 2 the centre's z), Sun's last planar face being an
  end face, and `CylinderParams`' layout (origin, axis, radius) for the coaxial read;
- `GetDocumentDependencies2`'s flat name, path array through late binding, `PlaneParams` and `CylinderParams`'
  layouts as `where_of` reads them, Sun's keyway being its only cylinder of radius 1.5 mm;
- that a read-only document can be shown mode by mode and found again by its path for `QuitDoc`;
- `equation_values` naming the added global `W9dProbe` as such;
- `AddComponent5` of a sub-assembly opened read-only;
- the harness's paths for four new folder names (`d-faces`, `d-faces-second`, `d-state`, `d-sub`).

The face mates' positions (Sprocket-5 at 200 mm, -6 at 206 mm, -7 at 230 mm on Input Axis) were chosen clear of
setup.master's bodies by the numbers in `W9A-DEMONSTRATION.md`; not checked against an interference read.

## The review's probe points

| Point | Taken |
|---|---|
| P1 | `faces` (a) saves the copy (`Save3`) and checks it unmarked; (b)'s proposals are None when any document was marked at the bracket's start |
| P2 | `state` (g) opens Housing.SLDPRT unchanged beside the changed sprocket and holds it unmarked and not read-only after the open, the shows and the close; the sprocket's global is read back |
| P3 | `read_only_close_verdict` requires every document the read-only open loaded to be gone after `QuitDoc` |
| P4 | `state_candidates` keeps the start's flags; no proposal unless the assembly read unmarked there |
| P5 | `first_marking` is kept only once one is found |
| P6 | (e) proposes only when (b–d) chose candidate 1 |
| P7 | the root reads are facts; no proposal |
| P8 | `sub_make_host` in `p2_make_sub`'s order, saved by `save_as` only, no `Save3` |
| P9 | every `sub` step catches `CaseStop`, says STOP and proposes its finding None |
| P10 | (c) takes each entity's route by its kind |
| P11 | `CARRY_INSERT_MARKS_USER_DOCUMENTS` is None when a document was already marked before the inserts |
| P12 | (d) the reload; the referenced configuration read in (b). The third bullet (open another version's file read-only and `QuitDoc` it, expecting the CAM box) **not taken**: the coordinator's ruling keeps the not-open read to a file the record says the running version wrote, and `FILE_VERSION_READ` (state (v)) covers a later save without opening one |
| P13 | the remake's proposal dropped; its result logged as a fact |
