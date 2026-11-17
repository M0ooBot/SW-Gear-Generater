# W9d's probes: what they ask, what sets which finding, and how to run them

The script is `probe/w9d_probes.py`. It measures what `W9D-INTERFACES.md` §11 owes before W9d's packages rely on it:
the three things the plan's last section names, plus the calls W9d adds that the app has never made and that could
raise a dialog or change a document. It proposes findings in the log (`propose NAME = value  # evidence`) and sets
none; each is set per version (`_ON_2026`, `_ON_2024`) from the reviewed log.

**How it runs.** As W9c's probes do: it runs W9a's script's `main` with its own three sections, through
`probe/w9c_probes.py` (imported for the watch, `swconst`, `mate_definition`, `select_face`, `raw_mate`, `open_doc6`,
`p2_make_sub`). So the attach and PID check, the dialog watch and the What's Wrong rule, keep-awake, the JSON after
every section (`w9d-probes-<time>.json`), APPDATA in the run folder and the guarded close are W9a's, unchanged. No
document title but the run's own is logged, and never SolidWorks' frame title. Every document is a copy in the run's
folder or one the script makes, closed unsaved at its section's end; the only saves are of the probe's own copy
(`Save3`, so the reads start unmarked, as W9c's s5 (e)) and of assemblies the script makes.

**Masters:** `--user-master` (W9a's `setup.master` for this version; built here first through W9a's builders when not
given, which needs `--master`, S0's `rangebox.master`).

## Sections, in order

| Section | What it asks | Proposes | 2026 (estimate) |
|---|---|---|---|
| `faces` | On a copy of setup.master, Sprocket-5, -6 and -7 inserted and four mates made through `GetCorresponding` (m1's route): a concentric on Sprocket-5's bore face to Input Axis; a coincident between Sprocket-5's and Sprocket-6's end faces; a concentric on Sprocket-6's circular bore edge; a **parallel** (a kind never made or read before) between Sprocket-7's end face and Sun's. (b) Each face or edge entity: its kind (which of `GetSurface`, `GetCurve`, `GetPoint` answer), what `IEntity.GetComponent` names, and two routes to its part-level reference — **r1** `GetCorrespondingEntity2` in the assembly then the part's `GetPersistReference3`, **r2** the mate's entity straight to the part's `GetPersistReference3` — each resolved in the part, carried back through the component and held to the original by `ISldWorks.IsSame` (else the face's area); the assembly-context reference's length beside (read only); GetSaveFlag of every document around. (c) The four made again in a second assembly by the first clean route, layout and Sun fixed, definitions and frames compared; the copy's documents' flags read before the inserts, after them and after the mates. | `PERSIST_REFERENCE_ROUTE_FOR_FACES`, `PERSIST_REFERENCE_ROUTE_FOR_EDGES` (the route, or None), `CARRY_INSERT_MARKS_USER_DOCUMENTS`, `MATE_REMAKE_ON_FACES_AND_EDGES_ROUTE` | 4 min |
| `state` | On a copy of setup.master, Housing-1 suppressed in H (the mode showing) and Sprocket-4 in L, saved; Sprocket-4's mates' flags read unshown (a fact for §11.5). (b–d) With nothing shown, GetSaveFlag of every document around each: **candidate 1** `IConfiguration.GetComponentSuppressionState(Name2)` per mode; **candidate 2** `GetRootComponent3(False)` per mode (the API help: None for a configuration not active); **candidate 3**, W9c's marking route taken apart call by call for each mode not showing, naming the first call that marks; then the truth, each mode shown. (e) Sprocket-2 suppressed in N and **not saved**: candidate 1 read again. (f) Sprocket-1 set lightweight: candidate 1, then the active configuration's `GetRootComponent3(False)` and `(True)`, every state read after each; all resolved again. (g) The copy closed; its Sprocket part opened alone and changed (a global added); the assembly opened `Silent | ReadOnly` beside it under the watch; what became of the part (open, flag, read-only); candidate 1 there; its modes shown. (h) That read-only document closed unsaved (`QuitDoc`) under the watch, 3 s waited inside the job; every file's time before and after. | `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` (the first candidate agreeing with the truth and marking nothing), `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED`, `ROOT_COMPONENT_UNRESOLVED_READ`, `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS`, `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` | 6 min |
| `sub` | A healthy sub-assembly made from a copy of the sprocket. (a) Not loaded: `OpenDoc6` Silent, its flag straight after and after 5 s. (b) Opened `Silent | ReadOnly`, a new assembly saved, the sub-assembly inserted by `AddComponent5` (of a read-only document: new): inserted, its children, its flag and read-only state. (c) A host holding it saved and reopened, so the sub-assembly is loaded as a component only; `OpenDoc6` of it (the warning, its flag), then inserted into another new assembly (its flag). Every step under the watch. | `SUBASSEMBLY_OPEN_MARKS`, `SUBASSEMBLY_READ_ONLY_INSERT`, `SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED` | 3 min |

**About 13 minutes on 2026** with the harness's start (attach, Excel) and setup.master given; about twice that on
2024, each section in a fresh session if the coordinator prefers (as W9c's 2024 run).

**Which answer sets which finding** (each per version):

- `COMPONENT_STATE_PER_CONFIGURATION_ROUTE`: the candidate that agrees with the shown truth on every component and mode
  (Housing-1 suppressed in H only, Sprocket-4 in L only, Sprocket-2 nowhere) **and** turned no document's flag on.
  Candidate 1 is proposed as `IConfiguration.GetComponentSuppressionState(Name2)`. None if neither 1 nor 2 does.
- `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED`: True when candidate 1 reads Sprocket-2 suppressed in N after the
  unsaved change. False means it reads the file: the app then uses the route only on an old assembly with no unsaved
  changes (W9D-INTERFACES §11.1).
- `ROOT_COMPONENT_UNRESOLVED_READ`: True when `GetRootComponent3(False)` names the root, as `(True)` does, and leaves
  Sprocket-1 lightweight; False when it resolves it or will not answer. Whether it marks is not read (the copy is
  marked by then); say so beside it.
- `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS`: True when the changed Sprocket part is still open, still changed and not
  read-only after the assembly's read-only open beside it.
- `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN`: True when the read-only document's modes were shown, it closed by `QuitDoc`
  with no dialog, it is gone after, no file's time changed, and the Sprocket part is as it was.
- `PERSIST_REFERENCE_ROUTE_FOR_FACES` / `_FOR_EDGES`: the first route (r1, then r2) clean on every face (three) or the
  one edge: read, resolved to its own kind, the round trip the same object. A resolve to another kind is §0.3's STOP
  for W9d and is said in the log as such.
- `CARRY_INSERT_MARKS_USER_DOCUMENTS`: True when inserting the user's parts into the second assembly turned any of
  the copy's documents on (W9D-INTERFACES §8: True only adds a sentence).
- `SUBASSEMBLY_OPEN_MARKS` / `_WHEN_LOADED`: True when that open turned the sub-assembly's flag on; None when it was
  already on. `SUBASSEMBLY_READ_ONLY_INSERT`: True when the read-only sub-assembly inserted with its child and its
  flag stayed off.

A dialog in any step ends that case with a STOP line and its finding proposed accordingly; a job that does not return
in 120 s, or a dialog that stays, ends the run (W9c's `watched`). Recovery: a fresh SolidWorks, the remaining
sections into a fresh `<out>`, or the same with `--redo`.

## Command lines (SolidWorks 2026 first; then 2024)

```
python.exe RUN\snap\probe\w9d_probes.py RUN\snap\src RUN\out --pid PID --log RUN\w9d-sw2026.log ^
    --sections faces,state,sub --user-master <W9a's setup.master for 2026> --master <S0's rangebox.master>
python.exe RUN\snap\probe\w9d_probes.py RUN\snap\src RUN\out24 --pid PID --log RUN\w9d-sw2024.log ^
    --sections faces,state,sub --user-master <W9a's 2024 setup.master> --master <S0's 2024 rangebox.master>
```

Commit the logs as `probe/results/w9d-probes-sw2026-<date>.log` and `probe/results/sw2024/w9d-probes-sw2024-<date>.log`
with their JSON.

## What is untested

Only `--self-check` and `--help` have run (the Linux venv, no SolidWorks): the pure judgements on made-up readings
(30 checks, 0 failed). Nothing that talks to SolidWorks has run, so expect script faults first, as every probe script
here has met. In particular, unverified and resting on the API help or on reading other scripts:

- that `GetComponentSuppressionState` takes the top-level `Name2` (its example passes `IComponent2.Name`; for a
  top-level component the two are expected to be the same, not checked) and answers a Boolean through late binding;
- `GetCorrespondingEntity2`, `IEntity.GetComponent`, `ISldWorks.IsSame` through late binding, and `swObjectEquality`
  and `swPersistReferencedObjectStates_e` being in `swconst.tlb` (read optionally: if missing, IsSame's answer is
  compared to nothing and the area decides for faces, so an edge would read not clean);
- the sprocket's geometry as m1 read it (a bore of radius 5 mm, end faces at −1 and +5 mm in its own coordinates),
  the circular-edge filter (`CircleParams` index 6 the radius, index 2 the centre's z), and Sun's last planar face
  being an end face;
- that a read-only document can be shown mode by mode and found again by its path for `QuitDoc`, and what `GetTitle`
  answers for it;
- `Save3` of an assembly this script made holding a sub-assembly, and `AddComponent5` of a sub-assembly opened
  read-only;
- the harness's own paths for four new folder names (`d-faces`, `d-faces-second`, `d-state`, `d-sub`).

The face mates' positions (Sprocket-5 at 200 mm, -6 at 206 mm, -7 at 230 mm on Input Axis) were chosen clear of
setup.master's bodies by the numbers in `W9A-DEMONSTRATION.md`; not checked against an interference read.
