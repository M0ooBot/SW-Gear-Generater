# W9c's probes: what they measure, the calls new to the app, and what a dialog leaves

The script is `probe/w9c_probes.py`. It measures the four things ISSUE-1-PLAN §4 puts ahead of W9c's and W9d's
packages:

- **P1**, deleting a component;
- **M1's leftovers**, the user-mate kinds W9a left unread (plan, *Changes after W9a's demonstration*);
- **S5**, W9d's spike;
- **P2**, inserting a user sub-assembly.

Nothing of W9c or W9d exists in the app. Each section proposes findings in the log (`propose NAME = value  # what
bears it out`, `findings.py`'s style) and sets none.

**How it runs.** It runs W9a's script's `main` with these four sections, as W9b's demonstration does. So the attach,
the dialog watch and the What's Wrong rule (as `swbuild.whats_wrong_shows_in_update` reads it for the version),
keep-awake, the JSON after every section (`w9c-probes-<time>.json`), APPDATA in the run folder and the guarded close
are W9a's, unchanged.

- **Masters:** `--master` (S0's `rangebox.master`), `--user-master` (W9a's `setup.master`) and `--reducer-master`
  (W9a's `reducer.master`). Each missing master is built here first by W9a's own builders.
- **Copies:** every probe works on a copy of a master, closed unsaved at its end.
- **Never logged:** SolidWorks' frame title, or any document title that is not the run's own.

**Without SolidWorks:** `python probe/w9c_probes.py --self-check` runs the pure judgements on made-up readings:

- p1's verdict on a delete, including a touching mate the MateGroup walk misses but `FeatureByName` finds, a walk
  that comes back short, no touching mate read, and a held handle that answers another frame, another name, or was
  read in a new epoch;
- s5's entity classification (below) and its definition comparison;
- a per-configuration route against the truth;
- the save-flag check.

It passes at this commit. `--help` imports nothing of SolidWorks.

## Sections, in order, and their times on 2026

| Section | What it does | 2026 (first run, ea1f8bf) |
|---|---|---|
| `p1` | Deletes G4, with its app mates, from a fresh copy of the 12 : 1 reducer, by each of three routes (below). Then deletes HighDog from a copy of RangeBox by the first route, so there are mode configurations and per-mode flags. Reads after each: the component gone from every configuration (each shown); the mates that touched it gone or left (named, with codes and what `mate_info` reads of them); every other body's frame, by the handle held across the delete and by a fresh find; the assembly marked or not; the held handles answering or stale. | 93 s |
| `m1` | On a copy of RangeBox with the user's Sprocket and Housing, each kind on its own sprocket: concentric (the bore face to Input Axis), limit distance, limit angle, width (the sprocket's two end faces and the housing's), and a user gear mate on Sun. Path is not made. Each new mate is set on in every mode, then read: `mate_info`, flags per mode, code, the whole definition, with GetSaveFlag of every document before and after. Then a quiet press, Backlash typed, and the footer's judgement: is each mate in the recorded inventory, and named by a problem? | 303 s |
| `s5` | On a copy of `setup.master` (W9a's user work, plus one sprocket mated to the assembly's own Front plane): (a), (b), (c), (e), (d) and (f) below. | stopped at 39 s (fault in (a), fixed below) |
| `p2` | A user sub-assembly (a sprocket in a new assembly) is made, opened and inserted into a copy of RangeBox. A coincident mate is made from its leaf's Gear Axis to the layout's Input Axis and read by `mate_info` (M1's leaf item: the leaf's `Name2` should be a path). Then a sub-assembly whose part file was deleted from disk is opened on its own and then inserted into the copy, each under the watch with 10 s waited after the call (below). | 29 s |

**About 7 minutes for p1, m1 and p2 on 2026**; s5 is still unmeasured (estimated 15 min). 2024 takes about twice
that, each section in a fresh session.

**If `s5` runs long,** cut the remake to the user–layout and user–user mates (drop the locks to app gears and their
inserted gear parts), and drop (e)'s second candidate.

**S5, part by part.**

Each part runs on its own: a part that raises is a FAIL with its sentence, and the next part still runs.
(b) and (c) need (a)'s read and say so when it did not complete. (e) and (d) need only the copy. The copy is closed
before (d)'s second open; if it does not close, that open is skipped and says so.

- **(a)** Every user mate's definition is read as the macro database's assemblies/06 does, each mate and each entity
  on its own:
  - `GetTypeName2`;
  - `IMate2` `Type`, `Alignment`, `Flipped` and the two variations;
  - whatever `GetDefinition` answers;
  - its dimensions;
  - each entity's component, reference type, parameters, what its reference is (a feature, a whole component, a
    face or edge, or none), and the feature's name.

  Each entity is then classified, and the log says which and why:
  - **assembly:** no component, the root component (`GetActiveConfiguration.GetRootComponent3(True).Name2`), or a
    name no top-level component has on a feature that is one of the assembly's own planes. Found again by tree order.
  - **whole:** a reference type for a whole component, a reference that is a component, or no reference.
  - **layout:** a feature on the layout. Found again by name.
  - **feature:** a feature on another part. Found again by its part-level persistent reference.
  - **unresolved, geometry, unread:** a component name nothing at the top answers to, a face or edge, or an entity
    that would not read. None of these is remade, and the log gives the reason.

  The part-level reference is read only for a layout or part feature. Its component is found by name, and its
  `GetModelDoc2` must give a document: a component with none (suppressed or lightweight) is recorded with its state,
  never asked for one.
- **(b)** Each feature entity's part-level reference is read and resolved in its part. It must resolve to the
  feature it was read from.
- **(c)** A second assembly is made from the default template. Every top-level component a user mate touches is
  inserted into it from the same file, at the frame it stood at, each on its own. The layout, the app's gears and
  the housing are fixed. A component that will not insert is said, and the mates on it fail with that sentence. Each
  user mate is made again by `AddMate5`, through the app's own wrapper, from the read definition. Its entities are
  found:
  - by the part-level persistent reference, resolved in the same part and carried through `GetCorresponding`;
  - by name, for the layout's axes;
  - by tree order, for the assembly's own plane;
  - whole, for a lock.

  Each remade definition is then compared with the read one, and each component's frame with where it stood.
- **(e)** Sprocket-4 is suppressed in L, the assembly saved (the probe's own copy, so the reads start unmarked), and H
  shown. Then, with nothing shown, two candidate routes are read, with GetSaveFlag around each:
  - the component's feature `IsSuppressed2(swSpecifyConfiguration, names)`;
  - `IConfiguration.GetRootComponent3(True)` per configuration, with `GetSuppression2`.

  Each is held against the truth, read with each mode shown.
- **(d)** `OpenDoc6` with Silent | ReadOnly: first on the assembly already open, then after it is closed unsaved.
  Read: what came back, `IsOpenedReadOnly`, the save flag.
- **(f)** GetSaveFlag before and after every read. Its checks are reported under (a) and (e).

**p1's three routes.**

1. `IComponent2.Select4(False, null, False)`, then `IModelDoc2.EditDelete()`.
2. The component's feature (`FeatureByName(Name2)`) `Select2(False, 0)`, then `EditDelete()`: `MATE_DELETE_ROUTE`'s
   form, which the app uses for a mate.
3. `Select4`, then `IModelDocExtension.DeleteSelection2(0)`.

## Calls new to the app, and what the macro database says of each

The log says "NEW" at each use.

| Call | Where | The macro database |
|---|---|---|
| Deleting a component: `Select4` + `EditDelete()`, its feature `Select2` + `EditDelete()`, `Select4` + `DeleteSelection2(0)` | p1 | No entry for a component. `EditDelete` is verified on a mate (2026, 2024) and on drawing annotations; `DeleteSelection2(options)` is "verified, SW 2026" on a folder only. |
| `AddMate5` concentric between a face and an axis | m1 | Face-to-axis concentric verified for its `MateEntity` order on 2026 and 2024 (made by a probe, not the app); concentric between two axes is refused (GOTCHAS §94). |
| `AddMate5` width | m1 | **No entry.** The first run's two forms (width mark 1 and tab mark 2; all four at mark 1) made no mate on 2026, status 0. A third form is new: width mark 1, tab mark 16. It comes from the installed API help (`AddMate5` Remarks: "swMateWIDTH … 16"; `IWidthMateFeatureData` Remarks: tab Mark = 16, width Mark = 1). Each form is tried only if the ones before made nothing. |
| `IAssemblyDoc.CreateMateData(swMateWIDTH)`, `IWidthMateFeatureData` `ConstraintType`, `WidthSelection`, `TabSelection`, then `IAssemblyDoc.CreateMate` | m1 | **NEW, no entry.** It is the help's other route ("Create and Edit Width Mate" example), and both installs' `sldworks.tlb` carry all four names. It is tried last, only if no `AddMate5` form made the mate. The puts are late-bound, so if SolidWorks' `IDispatch` there does not answer the width members, the error is the finding. |
| `AddMate5` limit distance and limit angle (upper and lower values) | m1 | The range read back on `IMate2` as offsets is "an inference from a handful of mates" (assemblies/06). |
| A part face selected through `IComponent2.GetCorresponding(face)` | m1 | Verified for a feature only. |
| `GetPersistReference3` on a part-level feature reached through a component, and `GetObjectByPersistReference3` in that part | s5 | Both "verified, SW 2026" on a part's own feature (curves/10). Never through a component, never on 2024. |
| `GetPersistReference3` on the assembly-context feature (the plan's unverified route) | s5 | Read only (its length or its error), not resolved elsewhere. |
| `IFeature.IsSuppressed2(3, names)` on a component's feature | s5 (e) | Verified on mates (2026, 2024); no entry for a component's feature. |
| `IConfiguration.GetRootComponent3(True)` per configuration, then `GetSuppression2` | s5 (e) | `GetRootComponent3` verified on 2024 for the active configuration; not for another. |
| `OpenDoc6` with `swOpenDocOptions_ReadOnly` | s5 (d) | **No entry.** reading/08 advises it, unmeasured. |
| `IModelDoc2.Save3` on the probe's own copy | s5 (e) | Verified on 2026 SP1.1. The app never calls it (plan §2.5): here it only clears the copy's save flag before the reads. |
| `AddComponent5` of an assembly file, `IComponent2.GetChildren`, a mate to a leaf through `GetCorresponding` | p2 | The ledger's "open it first" (`API-LEDGER.md:531`) is for a part. **No entry** for an assembly. |
| `OpenDoc6` of an assembly with a part file missing, then `AddComponent5` of it | p2 | **No entry.** |
| `IConfiguration.GetRootComponent3(True)` of the active configuration and its `Name2` | s5 (a) | Verified on 2024 for the active configuration; its `Name2` is new. assemblies/06 has `ReferenceComponent` both None for the assembly's own and "naming the top assembly", on a coordinate mate. |

Every enumeration value (mate types, alignments, width options, open options, delete options, suppression states,
configuration options, select types, document types) is read from `swconst.tlb` beside the running `sldworks.exe`,
found from the attached PID. A positive control, the six mate types `findings.py` already holds, must agree, or the
section stops.

## A dialog, and what it leaves behind

Every call that may raise a dialog runs under a watch that logs it and answers nothing (W9a's box watch). It logs:

- the dialog's class, caption, buttons, texts and style;
- its owner by class only;
- when it came, and the call in progress.

There are three outcomes:

- **The job returned and the dialog went.** The case stops (a p1 route, s5 (d), a p2 step). Its copy is closed
  unsaved, and the next case starts from a fresh copy.
- **The job did not return within 120 s, or the dialog stays up.** The session cannot go on. The script says so,
  marks the worker hung and ends the run. Nothing more is asked of SolidWorks, and nothing is closed or saved: the
  open copy and the dialog are left as they are.
- **Recovery:** close SolidWorks and start it fresh, then run the remaining sections into a fresh `<out>` (or the same
  one with `--redo` for the section that stopped).

A dialog is never a FAIL. A proposed finding records it (`COMPONENT_DELETE_DIALOG`, `OPEN_READ_ONLY_DIALOG`,
`SUBASSEMBLY_MISSING_REFERENCE_DIALOG`).

## What the plan's S5 row asks that this does not measure

- **A face's persistent reference.** setup.master's user mates sit on reference features and whole components, so
  (b) measures features. m1's concentric is on a face but is not remade.
- **The assembly-context route resolved in another assembly.** It is read, not resolved.
- **A gear mate, and a limit mate, remade from their definitions.** setup.master has no user gear mate and no limit.
  m1 reads both kinds' definitions but remakes neither.
- **A lightweight state per configuration.** (e) reads suppressed and resolved only.
- **Path mates**, not made in m1: they need a sketch path in the assembly, a feature the app has no route for.
- **Width:** if none of the four forms makes the mate, `M1_READS_WIDTH` stays None. The kind stays unread, so the
  app refuses it, and the log gives each form's answer.

## The first run on 2026 (ea1f8bf, from 3e11f2b), and what changed

p1, m1 and p2 ran with 0 failed and no dialog. s5 stopped after 39 s on a fault in the script.

**s5's fault.** `s5_read` asked `_component_by` for an entity's component, got None, and called `GetModelDoc2` on
it. A `ReferenceComponent` of None never reached that line: the read already turned None into an empty name, and an
empty name went to tree order first. The name that reached it was not empty, and no top-level component answers to
it. The likely entity is UserAsm6's side on the assembly's Front plane, with `ReferenceComponent` naming the root
(assemblies/06: "naming the top assembly"). That is not confirmed: the run stopped before any entity was logged. The
rerun's (a) logs each entity's component, its kind and why, and the root component's `Name2`.

The same assumption sat elsewhere in s5, and each place is now guarded:
- the touched components' frame and file reads, which used the same name;
- the remake's lookups by component name;
- (e)'s component found for `SetSuppression2`, the configuration's root component, its children, and each mode's
  fresh find;
- a component with no document.

**m1's width.** The macro database has no entry, but the installed API help has two forms the first run did not
try. `AddMate5` with the tab at mark 16 is tried third. `CreateMateData` / `IWidthMateFeatureData` / `CreateMate` is
tried fourth. Both are NEW. If neither makes the mate, `M1_READS_WIDTH` stays None, and width stays unread and so
refused.

**p1's proposals, checked against the reads they rest on.**

- **The mates gone.** `mates_after` was the MateGroup walk by `Name`, which is the feature tree. `mate_info` only
  chose which mates touched the target. In all four cases, the mates gone from the walk were exactly the touching
  ones, and every other mate was still listed (6 on the reducer, 18 on RangeBox).

  The 2026 run did not look each one up by name, and its verdict did not require the other mates to remain, so a
  short walk would have passed. Now `FeatureByName` looks for each touching mate after the delete. The verdict
  fails on a mate still found, on another mate missing, and on no touching mate read.
- **The other handles held.** `held_after` read `Transform2` through each handle kept before the delete. Nothing in
  between starts an epoch (only a configuration change or an open does), so `_component` handed back the kept
  object, not a fresh find. Every frame equalled its frame from before the delete.

  The verdict, though, counted only a raise or None as stale. Now each held handle also answers its own `Name2`,
  its frame must equal the one from before, and the epoch is recorded at the keep and at the read. A new epoch
  means "untested", and the proposal is then None.

The 2026 proposals stand on those reads. The new reads come in on the next run of p1.

**p2's `SUBASSEMBLY_MISSING_REFERENCE_DIALOG = False`.**

What the 2026 log shows:
- `OpenDoc6(UserSubMissing.SLDASM, assembly, Silent)` returned a document.
- The box watch ran from before the call until the job returned, and p2 logged no DIALOG.
- `extra None`: `OpenDoc6` returns the document itself, not a tuple, so its errors and warnings were not read.

What it does not show:
- whether a late dialog came, since nothing watched after the job returned;
- the document's components, the missing one's state, or any save flag;
- an insert of the sub-assembly.

The script did nothing more with the document. It stayed open until p2's end closed everything under `p2-parts`
unsaved. So False rested only on the open returning with no dialog while it ran.

Now the open reads the errors and warnings by reference, each component's `Name2`, `GetSuppression2`, file and
whether a document is loaded, and the save flag. It then waits 10 s inside the job, with the watch still running.
Then the sub-assembly is inserted into the copy by `AddComponent5`, its children read the same way, and the host's
flag read, with another 10 s under the watch. The proposal is True on a dialog in either step, False only if both
steps ran with none, and None otherwise. A step refused without a dialog is that step's finding.

## Command lines (SolidWorks 2026 first; then 2024, each section in a fresh session)

```
python.exe RUN\snap\probe\w9c_probes.py RUN\snap\src RUN\out --pid PID --log RUN\w9c-sw2026-1.log --sections p1 ^
    --master <S0's rangebox.master> --reducer-master <W9a's reducer.master>
python.exe RUN\snap\probe\w9c_probes.py RUN\snap\src RUN\out --pid PID --log RUN\w9c-sw2026-2.log --sections m1,s5 ^
    --master <S0's rangebox.master> --user-master <W9a's setup.master>
python.exe RUN\snap\probe\w9c_probes.py RUN\snap\src RUN\out --pid PID --log RUN\w9c-sw2026-3.log --sections p2 ^
    --master <S0's rangebox.master>
```
