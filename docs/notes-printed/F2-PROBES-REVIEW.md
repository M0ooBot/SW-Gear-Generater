# Review of F2's probe runs, so that its findings can be set

Read at `78ded52` on `printed`. The runs reviewed are the reruns from `d333ff8`:

- SolidWorks 2026 34.1.1: `probe/results/f2-probes-sw2026-20261118-3-rerun-geometry-all-proposed.log`, cited **q26:**, with
  `f2-probes-20261118-103547.json`;
- SolidWorks 2024 32.5.0: `probe/results/sw2024/f2-probes-sw2024-20261118-2-rerun-geometry-all-proposed.log`, cited
  **q24:**, with `f2-probes-20261118-104015.json`.

The first runs (`8d2c5fb`) are read where they bear on a point. Package B as built is read at `2d32c03` (`printout.py`,
`swcom.py`, `swbuild.py`). The write-up is the rerun section of `docs/notes-printed/F2-PROBES.md`. Nothing was run;
the two JSONs' `proposal` blocks were read and agree with the logs' `propose` lines.

**Verdict.** Every one of the six findings may be set, on both versions, to the values below, with **one must-fix in the
value**: `PART_WINDOW_READ_ON_<year>` must be set to the word `"Visible"`, which is what `swcom.Session.window_read`
compares (`swcom.py:3933-3936`). The probe proposes its prose (*"IModelDoc2.Visible, True for a document open in its own
window"*), and set as written that would read as "another read", so window_read would answer None. `EXTENT_MEASURED`
True is borne out for printed external spur and helical gears, with one caveat (herringbone). The job matches the probe
call for call in every way the findings open, with three differences the F2 demonstration must cover (§3, §4).

## 1. Step by step

Both logs have 88 lines, at the same numbers, and both end *"0 failed: []; 0 noted; 0 STOP(s)"* (q26:88, q24:88).

| Step | 2026 | 2024 | Borne out? |
|---|---|---|---|
| attach, rules | 34.1.1, What's Wrong a STOP (q26:5, :8) | 32.5.0, What's Wrong ruled, the close path in force (q24:5, :8-9) | yes; no What's Wrong came |
| built | spur and helical saved, unmarked (q26:14-16) | the same (q24:14-16) | yes |
| 1 | Silent 1, Copy 2, 13 members (q26:18-19) | Silent 1, Copy 2, 12 members (q24:18-19) | yes; the positive control (mate types) agrees (q26:17, q24:17) |
| 2, 3 | True plain, errors 0, warnings 0, options 3, 0.41 s, 909 852 bytes, no window; bracket identical; AP203, 1 solid, 1 closed shell, mm, extent 16.501185 / 8.000031 holds (q26:20-24) | the same at 887 873 bytes, extent 16.500000 / 8.000009 (q24:20-24) | yes |
| 4 | the helical the same, extent exact (q26:25-29) | the same (q24:25-29) | yes |
| 5 | overwrote its file; text not the same (9 093 statements differ); same part by geometry, 59 kinds, 4 698 points, 202 radii (q26:31-34) | the same: 9 040 statements, 4 429 points, 273 radii (q24:31-34) | yes |
| 6 | the spur's window Visible True, ActiveView True **with the helical active** (q26:35); exported by its object, the active document the helical before and after, nothing marked (q26:36-38); the file the spur's own (q26:45) | the same (q24:35-38, :45) | yes; the label is a real reading of a background window |
| 8 | the spur active at the change, flag on; exported, flag stays on, path unchanged, not the same part as the saved spur, extent 9.00003 (q26:39-43) | the same, 9.0000085 (q24:39-43) | yes, facts |
| controls (export) | spur twice the same; spur against helical not (26 kinds differ); 8 mm against 9 mm not (points not one to one) (q26:44) | the same (q24:44) | yes, read in the run |
| loaded | the assembly opened alone, unmarked, both components state 2, **the walk reaches both** (q26:56); assembly Visible True, both parts Visible False, ActiveView False (q26:57); `GetOpenDocumentByName` by path gives both parts, None for the absent file, None by file name only (q26:58) | the same (q24:56-58); the exempt open-progress box at q24:55 | yes |
| 7a | exported by `GetOpenDocumentByName`'s object, nothing activated, the assembly and the component (2 to 2) unchanged, `walk_doc` the same document (q26:60-63) | the same (q24:60-63) | yes |
| 7b | resolved before; opened beside, Visible True on both windows; after `CloseDoc` the assembly open, unmarked, active again, state 2 to 2, the gear Visible False again (q26:64-67) | the same (q24:64-67) | yes |
| 7d | everything closed; the gear twice the same part (10 946 points, 504 radii); gear against pinion not (16 kinds) (q26:68-69); extent 39.000237 / 8.000031 holds (q26:70); `GetOpenDocumentByName` open alone its own path, closed None (q26:71) | 10 265 points, 681 radii; 39.000000 / 8.000009 (q24:68-71) | yes |
| judged | 7a and 7b the gear's own (q26:72-73) | (q24:72-73) | yes |
| windows | 4 own, 2 background (the spur with the helical active, the gear with the pinion active), 3 component-only, Visible separates them (q26:74-75) | the same (q24:74-75) | yes |
| 7c | reopened unmarked; lightweight reads 1; the assembly's flag False; walk False, `GetOpenDocumentByName` None; opened beside, exported clean, closed; the assembly open, flag False, the component **2 after the close** (resolved by the opening); resolved again 2; no window (q26:76, :78) | the same (q24:76, :78) | yes, facts |
| close | all closed unsaved, the user's documents as at start, none (q26:80-81, :84) | (q24:80-81, :84) | yes |

**The controls are real readings.** Each pair is two files written in that run and compared by the probe's own
`same_part`:

- the positives are two exports of one document (2 and 5; 7d twice);
- the negatives are another part (spur and helical; gear and pinion: counts differ) and another state of the same
  document (8 and 9 mm: same counts, points moved).

`GetOpenDocumentByName`'s controls are both ways too: None for a file that does not exist and for the gear closed, its
own path when it is open alone.

**Does the write-up say anything the logs do not?** Three things, each fair but not in the logs:

- that the snapshots' self-check read 0 failed and imported their own `src` before the run;
- that nothing was written outside the run folders (the account searched by hand);
- that *in the first 2024 run [the open-progress box] came at 7c's open instead*, which is in `8d2c5fb`'s log, not
  these.

Say the first two as the operator's account, as W9D-DEMONSTRATION-REVIEW's N1 asked. Everything else it cites is at the
line it gives. The q24:55 box is SolidWorks' open-progress window (*Opened 2 Components … Post load updating*, a Close
button): exempt in W9a's watch (`box_windows`, the *Elapsed time* text), and seen and accepted in W9d's runs
(W9D-DEMONSTRATION.md:709). The *"other windows the watch logged: 0"* line (q24:85) agrees.

**Privacy.** The run, setting and result lines hold the Windows profile path (q26:3-4, :87; q24:3-4, :87), as every
earlier committed log does. No user document was open (q26:6, q24:6), and no STEP header is logged.

## 2. Each finding, per version

| Finding | 2026 | 2024 | Pin to |
|---|---|---|---|
| `SAVE_AS_COPY` | **2** | **2** (one name; both agree) | q26:18-19, q24:18-19 |
| `STEP_EXPORT_ON_<year>` | **True** | **True** | q26:20-30, q24:20-30 |
| `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` | **False** | **False** | q26:35-38, :44-46; q24:35-38, :44-46 |
| `PART_WINDOW_READ_ON_<year>` | **`"Visible"`** (not the proposal's prose) | **`"Visible"`** | q26:35, :57, :67, :71, :74-75; q24 the same |
| `STEP_EXPORT_FROM_COMPONENT_ON_<year>` | **True** | **True** | q26:56-63, :69-72, :76-77; q24 the same |
| `OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN_ON_<year>` | **True** | **True** | q26:64-67, :73, :79; q24 the same |

Caveats for the comments:

- **SAVE_AS_COPY:** the value read from each install's `swconst.tlb` with Silent held to the app's 1.
  `swSaveAsOptions_e` has 13 members on 2026 and 12 on 2024; Copy is 2 on both.
- **STEP_EXPORT:** `IModelDocExtension.SaveAs(path, 0, 1 | 2, null, out, out)` answers a plain True with both
  codes 0 and marks nothing, on the active part, spur and helical, unbored and unshifted.
  - **AP203 (`CONFIG_CONTROL_DESIGN`) and millimetres are what this machine's export options gave.** A user's own
    options may give AP214 or AP242, which the check accepts and logs.
  - **2026 writes the spur's tip vertex 0.001185 mm over d_a/2 and its face 0.000031 over** (2024: 0 and 0.000009).
  - Export onto an existing file overwrites without a word (q26:34), so the app's own refusal of an existing path
    stands.
- **STEP_EXPORT_NEEDS_ACTIVE False:** measured on a part in its own window, by `use_open_document`'s object, with
  another part active. **The active-document label at step 6 read the helical** before, during and after (q26:35-38),
  so the export did not activate the spur, nor rest on its being active. The file is the spur's by geometry under the
  run's own controls.
- **PART_WINDOW_READ "Visible":**
  - True on every document seen in its own window, active or not, part or assembly. False on every part loaded only as
    a resolved component, including the gear after its own window was closed.
  - Not measured: a minimised window, a document an add-in opened hidden, a lightweight component (it has no document
    to read).
  - With `STEP_EXPORT_FROM_COMPONENT` True, the job's way for a found part no longer depends on it (§3).
- **STEP_EXPORT_FROM_COMPONENT True:**
  - Measured on a **resolved** component of an assembly opened alone, exported by `GetOpenDocumentByName`'s object
    with nothing activated, the assembly and the component unchanged.
  - **A lightweight component is reached by neither `GetOpenDocumentByName` nor the walk**, so it is never exported by
    object. The job refuses it by name by the coordinator's ruling (`LIGHTWEIGHT`).
  - The app's `document_by_path` uses the walk (`DOCUMENT_BY_PATH_ROUTE = "walk"`, `swcom.py:1129`). The walk reached
    the same document (`walk_doc`, q26:61), but the export by the walk's object of a component-only part was not made
    (§3).
- **OPEN_BESIDE_ASSEMBLY_CLOSES_CLEAN True:**
  - For a resolved component only: opened beside by `open_document`, exported, closed by `CloseDoc`, the assembly
    left open, unmarked and the component resolved.
  - **On a lightweight component the same path resolves it in the user's assembly** (state 1 to 2, q26:76), with the
    assembly's flag still False. That is why the job never takes it for one.
  - With `STEP_EXPORT_FROM_COMPONENT` True the job never takes this path at all (§3). It is set as measured, for a
    future change of the route.

**`EXTENT_MEASURED` True: borne out**, for what the probe measured. The size check held on the printed spur (z 20), the
helical (m_n 2, z 20, β 15°) and the 50-tooth spur, on both versions, the largest miss 0.001185 mm against 0.01
(q26:23, :28, :70; q24 the same). Two caveats:

- **A herringbone is not measured**, and `printout.EXTENT_SKIPPED` does not skip it. Either skip it until a run shows its
  vertices give d_a/2 and the face, or have the demonstration export one.
- **Larger gears are not measured.** 2026's error at the tip was 0.0012 mm at z 20 and 0.0002 at z 50. The
  demonstration's reducer (several sizes) must show every part passing on 2026, since a miss is a false refusal of a
  good set.

## 3. Package B's job against the probe, call for call

With the findings set as above (`NEEDS_ACTIVE` False, `FROM_COMPONENT` True, `OPEN_BESIDE` True, `PART_WINDOW_READ`
"Visible"), `reach_way` (`swbuild.py:10224-10249`) gives:

| The part | Way | The job's calls | The probe |
|---|---|---|---|
| active, or in its own window | object | `document_by_path` (walk), `window_read` (Visible), `use_document`, the reads, `export_step` (`SaveAs` 1\|2) | step 6: walk object (`use_open_document`), `SaveAs`, nothing activated: **matches** |
| loaded only as a component (found) | object | the same | 7a: the **`GetOpenDocumentByName`** object, `SaveAs`: **the same call on another handle of the same document** |
| not found, no assembly open | open | `open_document` (`OpenDoc6` + `ActivateDoc3`), walk, `use_document`, reads, `SaveAs` (no re-activation, `NEEDS_ACTIVE` False), then `CloseDoc` | the app's own verified open and close; `SaveAs` on an opened part as in 7d: **matches** |
| not found, an assembly open | refused, `LIGHTWEIGHT` | none | 7c: never reached, opening beside resolves it: **matches the ruling** |
| the end | | `CloseDoc` of what it opened, `ActivateDoc3` of the start's document, `GetSaveFlag` on all | the probe's own put-back after 7b (q26:67): **matches** |

`export_step` is the probe's call exactly (`swcom.py:3867-3896`): `SaveAs(path, 0, SAVE_AS_SILENT | SAVE_AS_COPY,
_null_dispatch(), out, out)`, both answer forms read, an existing path refused first.

**What the job does that the probe did not show:**

1. **Its reads on a document that is not active**: `GetSaveFlag`, `equations()` (the Equation Manager's `Equation` and
   `Value`) and `feature_states()` (`GetErrorCode2` over the tree), on a background part and on a component-only part.
   The probe read `GetSaveFlag` on both kinds (the brackets), never the other two. Run 1's step 8 showed that a global
   *set* on a non-active part did not take on 2026. A *read* is a different call, but nothing has shown that
   `equations()` reads live there, and `GLOBALS_DIFFER` rests on it.
2. **The export of a component-only part by the walk's handle**, not `GetOpenDocumentByName`'s. It is the same document
   (q26:61), so the risk is small, but the call was not made. Either set `DOCUMENT_BY_PATH_ROUTE` to
   `"GetOpenDocumentByName"`, measured with its controls on both versions and by full path as the job passes it, or
   keep the walk and let the demonstration show it.
3. **`LIGHTWEIGHT` is inferred, not read.** `reach_way` refuses *every* part not found while *any* assembly is open.
   The interface (§5.2, *How the job knows*) said to read each open assembly's components and refuse those reading
   lightweight. So a part that is simply closed while an unrelated assembly is open, or whose component is suppressed,
   is refused with a sentence saying it is lightweight. That errs safe (nothing is touched), but the words are untrue in
   those cases. Should-fix: read the states as the interface says, or word the code *not open, and an assembly is open*.

## 4. Before the findings are set, and what the demonstration must show

**Must-fix before the findings commit:** set `PART_WINDOW_READ_ON_2026` and `_ON_2024` to `"Visible"` (the word
`window_read` compares), with the proposal's prose in the comment, and pin that word in `tests/test_findings.py`. Move
the six names out of `test_f2_findings_are_not_measured_until_a_reviewed_probe_run_sets_them` into pins on their values
and log lines, as W9d's findings commit did.

**Should-fix, not blocking the findings:** herringbone in `EXTENT_SKIPPED` until measured; `LIGHTWEIGHT` read or
reworded (3.3); the document route chosen (3.2); the write-up's three operator statements said as such.

**The F2 demonstration (PLAN-PRINTED §3.3) must show on SolidWorks, on 2026 and in the 2024 confirming build, what the
probe did not:**

1. **The Workbook window's press with the gearbox assembly open and its parts loaded only as components** (the plan's
   `workbook` section already asks it). Every part written by the walk's handle with nothing activated; the
   assembly's flag and active document unchanged; every file checked.
2. **`GLOBALS_DIFFER` read on a part that is not active.** A global changed in SolidWorks and saved, in one gear that
   is a component only (and, on the form's side, in a part open behind another). The press must refuse it, naming the
   global and both values. This is the one proof that `equations()` reads live off a non-active document.
3. **A part open in its own window but not active**, during a window press: exported by its object, not activated, and
   the user's active document unchanged after.
4. **A lightweight component** in the open gearbox assembly: refused by name, the component still lightweight and the
   assembly unmarked after the press.
5. **The size check on every part of the 12 : 1 reducer** (several modules and tooth counts) passing on 2026, and on a
   herringbone if one is not skipped.
6. **A part the job opens itself** (no assembly open, the part closed): opened, exported, closed, nothing left open,
   the start's document active again.
