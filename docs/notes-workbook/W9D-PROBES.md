# W9d's probes: what they ask, what sets which finding, and how to run them

The script is `probe/w9d_probes.py`. It measures what `W9D-INTERFACES.md` §11 owes before W9d's packages rely on it:
the three things the plan's last section names, plus the calls W9d adds that the app has never made and that could
raise a dialog or change a document. It proposes findings in the log (`propose NAME = value  # evidence`) and sets
none; each is set per version (`_ON_2026`, `_ON_2024`) from the reviewed log. **Revised** to the review
(`W9D-INTERFACES-REVIEW.md`, `f0eb516`): every probe fault P1–P13 is taken (the table at the end).

**How it runs.** As W9c's probes do: it runs W9a's script's `main` with its own three sections, through
`probe/w9c_probes.py` (imported for the watch, `swconst`, `mate_definition`, `select_face`, `raw_mate`, `open_doc6`,
`p2_make_sub`). So the attach and PID check, the dialog watch and the What's Wrong rule, keep-awake, the JSON after
every section (`w9d-probes-<time>.json`), APPDATA in the run folder and the guarded close are W9a's, unchanged. No
document title but the run's own is logged, and never SolidWorks' frame title. Every document is a copy in the run's
folder or one the script makes, closed unsaved at its section's end; the only saves are of the probe's own copy
(`Save3`, so the reads start unmarked, as W9c's s5 (e)) and of assemblies the script makes (the app's `save_as`).

**Masters:** `--user-master` (W9a's `setup.master` for this version; built here first through W9a's builders when not
given, which needs `--master`, S0's `rangebox.master`).

## Sections, in order

| Section | What it asks | Proposes | 2026 (estimate) |
|---|---|---|---|
| `faces` | (a) On a copy of setup.master, Sprocket-5, -6 and -7 inserted and four mates made through `GetCorresponding` (m1's route): a concentric on Sprocket-5's bore face to Input Axis; a coincident between Sprocket-5's and Sprocket-6's end faces; a concentric on Sprocket-6's circular bore edge; a **parallel** (a kind never made or read before) between Sprocket-7's end face and Sun's; the copy then saved and read unmarked (P1). (b) Each face or edge entity: its `ReferenceType2` and the kind it gives, against which of `GetSurface`, `GetCurve`, `GetPoint` answer; what `IEntity.GetComponent` names; its coaxial read (`CylinderParams` of the part-level face against the part's Z axis); two routes to its part-level reference — **r1** `GetCorrespondingEntity2` in the assembly then the part's `GetPersistReference3`, **r2** the mate's entity straight to the part's `GetPersistReference3` — each resolved in the part, carried back through the component and held to the original by `ISldWorks.IsSame` (else the face's area); the assembly-context reference's length (read only); each user component's `ReferencedConfiguration`, its document's active configuration, `IsVirtual` and `IsPatternInstance`; GetSaveFlag of every document around, and which were already marked at the start. (c) The four made again in a second assembly, each entity by its own kind's clean route (P10), layout and Sun fixed, definitions and frames compared; the copy's documents' flags read before the inserts, after them and after the mates. (d) The second assembly and the copy closed, each part opened alone, every face and edge reference resolved there again (P12, the not-open path's resolve). | `PERSIST_REFERENCE_ROUTE_FOR_FACES`, `_FOR_EDGES`, `COAXIAL_FACE_READ`, `REFERENCED_CONFIGURATION_READ`, `CARRY_INSERT_MARKS_USER_DOCUMENTS`, `PERSIST_REFERENCE_SURVIVES_RELOAD` | 6 min |
| `state` | (a) On a copy of setup.master, Housing-1 suppressed in H (the mode showing) and Sprocket-4 in L, saved and read unmarked; Sprocket-4's mates' flags read unshown (a fact). (b–d) With nothing shown, GetSaveFlag of every document around each, the start's flags kept (P4): **candidate 1** `IConfiguration.GetComponentSuppressionState(Name2)` per mode; **candidate 2** `GetRootComponent3(False)` per mode; **candidate 3**, W9c's marking route taken apart call by call for each mode not showing, naming the first call that marks (P5); then the truth, each mode shown. (e) Sprocket-2 suppressed in N and **not saved**: candidate 1 again (proposed only when (b–d) chose it, P6). (f) Sprocket-1 set lightweight: candidate 1, the active configuration's `GetRootComponent3(False)` and `(True)`, every state after each — facts only (P7); all resolved again. Then the copy closed. (v) The closed file's `ISldWorks.VersionHistory` against `GetLatestSupportedFileVersion`. (g) The Housing part opened unchanged and the Sprocket part opened and changed (a global added); the assembly opened `Silent | ReadOnly` beside them under the watch; what became of each part (open, flag, read-only; the global read back, P2); candidate 1 there; its modes shown. (h) That read-only document closed unsaved (`QuitDoc`) under the watch, 3 s waited inside the job; every document it loaded checked gone (P3), both parts as they were after the open, the shows and the close, every file's time unchanged. | `COMPONENT_STATE_PER_CONFIGURATION_ROUTE`, `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED`, `FILE_VERSION_READ`, `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS`, `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` | 8 min |
| `sub` | A healthy sub-assembly made from a copy of the sprocket. (a) Not loaded: `OpenDoc6` Silent, its flag straight after and after 5 s. (b) Opened `Silent | ReadOnly`, a new assembly saved, the sub-assembly inserted by `AddComponent5` (of a read-only document: new): inserted, its children, its flag and read-only state. (c) A host holding it made in `p2_make_sub`'s order and saved by the app's `save_as` only (P8), reopened so the sub-assembly is loaded as a component only; `OpenDoc6` of it (the warning, its flag), then inserted into another new assembly (its flag). Every step under the watch; a dialog that comes and goes ends that step with a STOP line and its finding proposed None (P9). | `SUBASSEMBLY_OPEN_MARKS`, `SUBASSEMBLY_READ_ONLY_INSERT`, `SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED` | 3 min |

**About 18 minutes on 2026** with the harness's start (attach, Excel) and setup.master given; **about 35 minutes on
2024** (S5 ran 1.6–2× slower there), in one fresh session or each section in its own.

**Which answer sets which finding** (each per version; *settled when* as `W9D-INTERFACES.md` §8):

- `COMPONENT_STATE_PER_CONFIGURATION_ROUTE`: the candidate that agrees with the shown truth on every component and mode
  (Housing-1 suppressed in H only, Sprocket-4 in L only, Sprocket-2 nowhere) **and** turned no document's flag on,
  from a bracket that started with the assembly unmarked. Candidate 1 is proposed as
  `IConfiguration.GetComponentSuppressionState(Name2)`. None if neither 1 nor 2 does.
- `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED`: proposed only when candidate 1 was chosen; True when it reads
  Sprocket-2 suppressed in N after the unsaved change.
- `FILE_VERSION_READ`: the route string when the closed copy's last `VersionHistory` entry is the version
  `GetLatestSupportedFileVersion` gives (the copy was saved by this SolidWorks in (a)); else None.
- `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS`: True when, after the read-only open, the Housing part is still open, unmarked
  and not read-only, and the Sprocket part still open, changed (its global read back) and not read-only; None when the
  Housing part was not unmarked before the open.
- `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN`: True when the read-only document's modes were shown, it closed by `QuitDoc` with
  no dialog, it and every document it loaded are gone, both parts are as they were after the open, the shows and the
  close, and no file's time changed.
- `PERSIST_REFERENCE_ROUTE_FOR_FACES` / `_FOR_EDGES`: the first route (r1, then r2) clean on every face (five) or the
  one edge — read, resolved to its own kind, the round trip the same object — from a bracket that started unmarked and
  marked nothing. A resolve to another kind is §0.3's STOP for W9d and is said in the log as such.
- `PERSIST_REFERENCE_SURVIVES_RELOAD`: True when every face and edge reference resolves again, to its own kind (a face
  to its own area), in its part opened alone after the copy closed; None otherwise.
- `COAXIAL_FACE_READ`: True when Sprocket-5's bore reads coaxial and every end face reads not, from an unmarked start
  marking nothing.
- `REFERENCED_CONFIGURATION_READ`: True when every user component answers a referenced configuration name, from an
  unmarked start marking nothing. (`IsVirtual` and `IsPatternInstance` are read and logged as facts: no fixture holds a
  virtual component or a pattern, so `VIRTUAL_READ` and `PATTERN_INSTANCE_READ` stay None.)
- `CARRY_INSERT_MARKS_USER_DOCUMENTS`: True when inserting the user's parts into the second assembly turned any of the
  copy's documents on; None when one was already on before (P11).
- `SUBASSEMBLY_OPEN_MARKS` / `_WHEN_LOADED`: True when that open turned the sub-assembly's flag on (settled when
  **False**); None when it was already on or a dialog came. `SUBASSEMBLY_READ_ONLY_INSERT`: True when the read-only
  sub-assembly inserted with its child and its flag stayed off.

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
    --master <probe folder>\w9c-whole-sw2026-20261117-123612\out\rangebox.master
python.exe RUN\snap\probe\w9d_probes.py RUN\snap\src RUN\out24 --pid PID --log RUN\w9d-probes-sw2024.log ^
    --sections faces,state,sub --user-master <2024's setup.master> --master <2024's rangebox.master>
```

Commit the logs as `probe/results/w9d-probes-sw2026-<date>.log` and `probe/results/sw2024/w9d-probes-sw2024-<date>.log`
with their JSON.

## What is untested

Only `--self-check` and `--help` have run (the Linux venv, no SolidWorks): the pure judgements on made-up readings
(41 checks, 0 failed). Nothing that talks to SolidWorks has run, so expect script faults first, as every probe script
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
