# W9c's demonstration on SolidWorks: the sections, the gates, what each line bears out

The script is `probe/w9c_demonstration.py`. It covers ISSUE-1-PLAN §5's W9c *Done when* on SolidWorks:

- on a copy of RangeBox with W9a's user work, the workbook edited to `RangeBox_Fixed` and **one Update**:
  - it adds Hub;
  - it gives RangeSlv its bands in place, keeping the user's groove;
  - it leaves every user item as it was;
  - each mode then engages and turns as §3;
- then a mode added and one removed by Update (M10).

Around that it measures M4, M5, M6 and M8, a gear taken out, and a tooth change with modes.

It is written to the Workbook window's own path and the plan's numbers, not to the packages' internals. Every press
goes through W9a's `Desk9`: the window's own planning, footer, `press_update` job and `_finish_update`. Every edit is
typed in Excel by W8's `edit`, from the fixtures' own rows. So the joining round under way in package B (`AddedGear.refs`,
`NewMate.ref`) and the review's fixes should not move it. The fields it reads are named in W9C-INTERFACES §6: the
result's `inserted`, `mates_made`, `bands_added`, `modes_added`, `flags_lost`, `took_active_state` and the rest.

**How it runs.** It runs W9a's script's `main` with its own seven sections, as W9b's does. So it inherits, unchanged:

- the attach and PID check;
- the dialog watch, with the What's Wrong rule per version;
- keep-awake;
- the JSON after every section (`w9c-demo-<time>.json`, each mode's readings in it);
- APPDATA in the run folder;
- the guarded close, and a failed section closing what it opened;
- `--sections`, `--redo`.

W9b's per-mode judgement is imported, not copied: `mode_read`, `judge_every`, `measured`, `judge_mode`,
`section3_of`, §3's table, `part_faces` and `step_faces`. So "each mode as §3" means exactly what it meant for W9b's
`build`. No document title but the run's own is logged, and SolidWorks' frame never is.

**Masters:**

- `--master`: S0's `rangebox.master`.
- `--user-master`: W9a's `setup.master`, RangeBox with the user's work. That work is:
  - Sprocket-1 and -3 locked to Sun;
  - Sprocket-2 locked to RangeSlv;
  - Sprocket-4 by a distance and an angle;
  - the fixed Housing-1;
  - their eight mates;
  - the User Keyway in Sun's part.
- `--reducer-master`: W9a's `reducer.master`.
- `--fixed-master`: this script's own `fixed-updated.master`, which `fixed` keeps for the next four sections.

Each master is built first where it is missing, by its own section.

## The gates, and the line that proposes each

Every new kind of write is behind a per-version finding that is None. In each case, the section first shows the
app's refusal with the finding as it stands, as W9a's `nocarrier` did:

- the footer's sentence, foreseen by `update.in_place_ahead`;
- the user saving;
- the press refused before any write, judged by W9a's `refuse_press`, which looks at:
  - its traced calls (no show, flag, value, rebuild, put, mate or insert);
  - frames, mates, flags and entities read before and after;
  - a part's globals;
  - the record keeping the refusal;
- every file's time and every document's save flag, unchanged.

Then the finding is patched True in this process only, logged as `PATCH findings.X = True … (was None)` and put back
as `PATCH … back to None`, and the section measures. A section proposes and never sets:

| Finding (`_ON_<year>`) | Section | Log line | What it rests on |
|---|---|---|---|
| `UPDATE_INSERTS_A_GEAR` | `fixed` | `propose UPDATE_INSERTS_A_GEAR_ON_<year> = True  # fixed: Hub built, inserted, mated and resolved in every mode, …` | Hub's part built in the copy, inserted under the `Name2` the result gives, its three mates on in every mode (`mates_made`), resolved in every mode (M5), nothing of the user's moved, each mode as §3, the second press quiet |
| `UPDATE_BANDS_IN_PLACE` | `fixed` | `propose UPDATE_BANDS_IN_PLACE_ON_<year> = True  # fixed, giving bands only …` | the band globals and the five relief features after the groove, in no error, the bore over the relief exact, the groove unchanged. **The taking away is not reached by any legal edit (below)**; `bands-off` adds its script-side evidence as `UPDATE_BANDS_IN_PLACE_taking_away_script_side` |
| `UPDATE_ADDS_A_MODE` | `modes` | `propose UPDATE_ADDS_A_MODE_ON_<year> = True  # modes: H2 added from the mode showing, …` | H2 made, the record's modes H, N, L, H2, the mode showing the same before and after, every flag and slide value as the record in every mode, H2 judged against §3's H row, each user item there said as read there (`took_active_state`) |
| `UPDATE_REMOVES_A_MODE` | `modes` | `propose UPDATE_REMOVES_A_MODE_ON_<year> = True  # modes: N deleted unshown …` | N deleted with H showing; the user's UserAngle4, suppressed in N alone, said in `flags_lost` exactly as read before; every other configuration's flags and slide values unchanged; H2 refused while it shows; H deleted with H2 showing, L the record's first |
| `UPDATE_MAKES_MATES_WITH_MODES` | `remake` | `propose UPDATE_MAKES_MATES_WITH_MODES_ON_<year> = True  # remake: gear mates of a gearbox with modes remade, …` | the four gear mates classify remakes, in `remade_in_modes`, each one's sense read (none in `senses_unread`), the user's mates unchanged, every mode judged. **A coupling or sliding mesh newly made by Update is not exercised (below)** |
| `EXTERNAL_REFERENCES_READ` | `m4` | `propose EXTERNAL_REFERENCES_READ_ON_<year> = None  # m4: no positive case …`, and `propose EXTERNAL_REFERENCES_READ_ROUTE_CANDIDATES_<year> = [...]` | stays None: no in-context reference can be made by proven calls, so no read is held to a positive case; C4's refusal stands |

The removal gates (`COMPONENT_DELETE_*`) are P1's, already set on both versions, so `remove`'s 12 : 1 press needs no
patch.

## Sections

Times are estimates for SolidWorks 2026, from W9a's and W9b's measured runs. An Update that puts every mode took about
4 min there; a refused press about 1 min; W9b's `part` 88 s.

| # | Section | What it does | 2026 |
|---|---|---|---|
| 1 | `fixed` | **The Done-when.** Details below. Kept as `fixed-updated.master`. | 30 min |
| 2 | `modes` | **M10.** Four edits, three presses and three refusals. Details below. | 30 min |
| 3 | `remove` | G4 out of the 12 : 1; HighDog out of setup refused, twice. Details below. | 15 min |
| 4 | `remake` | Sun 29 → 30, Planet 13 → 12, Ring 55 → 54 with modes. Details below. | 15 min |
| 5 | `bands-off` | The take-away side. Details below. | 8 min |
| 6 | `m4` | The external-references read, a probe. Details below. | 5 min |
| 7 | `w9b-part` | W9b's `part` section again, so its step-face read runs on SolidWorks in this session. | 2 min |

**About 1 h 45 min on 2026**, inside the plan's 2 h 20 min. Add 5 min if `setup.master`, and 4 min if the 12 : 1's
master, must be built first. On 2024, at about twice the time per press, about 3 h 30 min against the plan's
3 h 35 min, each section in a fresh session as before. **I would cut first** `w9b-part` (its question rides along),
then `bands-off`'s script-side probe, then `m4`'s comparison read on Sun.

### `fixed`

1. **The copy and the groove.** A copy of `setup.master`. Its workbook must hold the fixture's RangeBox rows;
   otherwise the section stops, naming the rows. The User Keyway in Sun's part is read as there (setup made it).
   - **The user's groove is cut in RangeSlv's part:** an axial Ø 2 cut through the sleeve's wall at 14.25 mm,
     between the teeth's root (12.375) and the outside (16.125), clear of the relief's Ø 25. It is made by the
     session's own sketch and cut calls, as W9a's keyway. A ring groove would need a revolve cut, which is not
     proven. Saved, and read: its feature, its dimensions and the cylinders it cut.
   - **A quiet press records the inventory with the groove in it.**
2. **The edit.** The workbook is edited in Excel to RangeBox_Fixed: RangeSlv's At, Face width, Slides, Start band and
   End band, and Hub's row typed in, all from `model.to_sheets` of the fixture.
   - **classify:** one Update in place. Hub is added with its three mates; RangeSlv's bands are given; nothing is
     structural.
   - The read's warnings are the fixture's four.
3. **The gates' refusal**, then the findings patched.
4. **The press.** The footer foresees nothing in place. The mode showing is read before and after.
   - **The result:**
     - Hub's part built in the copy;
     - `inserted` `[("Hub", Name2)]`;
     - each of Hub on Output Axis, Hub along Output and RangeSlv splined to Hub in `mates_made` with every mode (M6);
     - `bands_added` `["RangeSlv"]`;
     - `not_resolved` empty;
     - the spline's sense read (not in `senses_unread`).
   - **The record:**
     - Hub's component under that `Name2`;
     - RangeSlv's component and file as before;
     - W9b's `hub_mates`;
     - the sleeve's sidecar at schema 2 with Relief.
5. **M8.** RangeSlv's part reads:
   - Start Band 5, End Band 5 and Relief Diameter 25;
   - the relief's five features in no error;
   - W9b's `relief_bore` exact;
   - the groove kept (`groove_kept`): present, in no error, before the relief's first feature, its dimensions and
     its cut faces as before.

   W9b's step-face read rides along here.
6. **M5.** Hub read resolved in every mode, each shown (`Session.components`).
7. **Every user item** (`user_items_judged`, every mode shown and rebuilt, before and after), each holding:
   - Sprocket-1, -2 and -3 where they were relative to Sun or RangeSlv (route (c1)'s carry);
   - Sprocket-4 and Housing-1 where they were;
   - every user mate's flag in every mode as before, and in no error where on.

   The user's own files are unwritten.
8. **Each mode H, N, L as §3** (W9b's `judge_every` with §3's table):
   - every body at its frame on record;
   - every mate's flag as recorded;
   - the slide's value and side;
   - every app gear free;
   - no interference;
   - the bands, relief, engagement and least running gaps as §3;
   - Hub at −55.5…−35.5, 1.0 from HighDog.
9. **Saved as the user would, then a second press:** quiet, by W8's `check_quiet_update`.
10. Kept as `fixed-updated.master`.

### `modes`, M10

On a copy of `fixed-updated.master`:

1. **A Modes row H2 is added** (RangeSlv at H), first refused with `UPDATE_ADDS_A_MODE` as it stands.
   - **The press:** `modes_added` `["H2"]`, H2 among the configurations, the record's modes H, N, L, H2, and the mode
     showing the same before and after.
   - **Each user mate's flag and each user component's state in H2** is read (the flag unshown, the state shown) and
     held to the result's `took_active_state`, item by item.
   - **Every mode is judged:** H2 against §3's H row, the others their own.
2. **The user suppresses UserAngle4 in N alone** and saves.
3. **N's row is cleared** while H shows, first refused with `UPDATE_REMOVES_A_MODE`. The user's flags are read before:
   UserAngle4's in N differs from H's.
   - **The press:** `modes_removed` `["N"]`, N gone from the configurations, the record's modes H, L, H2.
     `flags_lost` equals what was read: `[("N", "UserAngle4", "suppressed")]`.
   - **Every remaining configuration's** app flags and slide values are as before (W9b's `mode_read`), and the mode
     showing is unchanged.
4. **The user shows H2**, and H2's row is cleared. classify takes it out in place (the showing is read only at the
   press); the footer cannot foresee it (C12, said).
   - **The press refuses before any write:** `PROBLEM_MODE_SHOWING`, naming H2 in its subjects and sentence, with
     the user's work unread (`user_work` None). This is a script-side judgement, since W9a's `refuse_press` holds a
     record rule this refusal does not follow.
   - **Nothing is written,** by traced calls, reads, file times and save flags.
5. **H2's row is put back and H's cleared** in one edit, with H2 showing. classify gives `modes_removed` `("H",)` and
   `first_mode` `"L"`.
   - **The press:** H deleted, the record's modes L, H2, and H2 still showing.
   - **Every mode is judged:** L as §3's L, H2 as §3's H.
   - **The user items are as before.**

H's coupling to HighDog stays on in H2. That is why H2 is added first: removing H from RangeBox_Fixed alone is
*Build again…* by ruling 9.1, and the self-check shows it.

### `remove`

- **G4 out of a copy of the 12 : 1** (no user component, no modes). It goes ahead by P1's route.
  - **The result:** `deleted` `[("G4", Name2)]`, and `mates_deleted` equal to classify's `RemovedGear.mates` (G4 on
    S3 Axis, G4 along S3, G3 meshes G4).
  - **SolidWorks after:** G4 is gone from the components, those mates are gone by name, every other mate is still
    there, and nothing else moved.
  - **The record** is without G4, and its part's file is still on disk.
- **HighDog out of a copy of `setup.master`.** The footer foresees `PROBLEM_REFERENCES` (C4), and the press refuses
  naming `EXTERNAL_REFERENCES_READ_ON_<year>`, nothing written.
  - Then **the user inserts Sprocket-5 on Input, locked to HighDog** (`UserLock5`). The press refuses with
    `PROBLEM_REMOVED`, naming `UserLock5` and HighDog, and `PROBLEM_REFERENCES`.
  - The footer could not foresee the lock: the recorded inventory predates it (said).

### `remake`

On a copy of `fixed-updated.master`: Sun 30, Planet 12, Ring 54. The centre distance is m(30 + 12)/2 = 26.25 as
before; 30 + 2 × 12 = 54; and (30 + 54)/3 = 28, so three planets stay evenly spaced.

- **classify:** a value Update remaking four gear mates: Sun meshes Planet copy 1–3, and Planet copy 1 meshes Ring.
- **Unpatched, the press refuses before any write.** It refuses with a `BuildError` naming
  `UPDATE_MAKES_MATES_WITH_MODES_ON_<year>`, not a `UserWorkRefused`, so it is judged script-side.
- **Patched, the press shows:**
  - every one of those mates in `ratios` and `remade_in_modes`;
  - none in `senses_unread`;
  - the user's keyway in Sun's part not in error;
  - the user items as before (Sprocket-1 and -3 carried with Sun);
  - every mode judged against §3's engagement and spans;
  - the app's read of L at 1 + 54/30 = 2.8.

### `bands-off`

The self-check searched for an edit that takes the bands off RangeBox_Fixed's sleeve in place and leaves the gearbox
legal. **None exists:**

| Edit | Answer |
|---|---|
| The bands alone | Illegal: L jams (both dogs) |
| RangeSlv as RangeBox has it, Hub kept | Illegal: the sleeve and Hub do not cover one another in H and L |
| The same, with Hub moved over the dogs | Illegal: Hub clashes with HighDog and LowDog |
| The same, with Hub's row cleared | *Build again…*: Hub anchors RangeSlv, and Update takes out only a gear that anchors none |

So this section is a refusal check:

- the first edit is refused at the workbook, with nothing offered;
- the last is *Build again…*, naming Hub as RangeSlv's anchor;
- nothing is written by either.

Then, **script-side only** (not the window's path), the app's own `Session.suppress_feature("Relief", True)` runs
on the copy's sleeve (C8's call, on a part's feature):

- **Suppressed:** the part rebuilt, its volume up (the teeth back over the relief), and the assembly read in every
  mode with RangeSlv's mates in no error.
- **Then on again:** the volume back, the relief's features as before (no second relief), and the assembly read
  again.

The copy ends unsaved.

### `m4`

A probe, since no app code makes the read yet. On a copy of `setup.master`, each user component (and Sun, for
comparison) is read by each documented candidate, with GetSaveFlag around each. The candidates come from the
installed API help (`sldworksapi.chm`):

- `IComponent2.ListExternalFileReferencesCount()` and `ListExternalFileReferences2` (nine out arguments);
- `IModelDocExtension.ListExternalFileReferencesCount()` and `ListExternalFileReferences` (nine out arguments) on
  its part.

What the macro database says of them:

- **Unverified in the ledger:** `ListExternalFileReferences` on IModelDoc2, and `ListExternalFileReferences2` on
  IFeature.
- **No entry:** the rest.
- **The control:** `ISldWorks.GetDocumentDependencies2`, "Verified" for a closed file's references. On the
  assembly it must list every app part.

All of these are marked NEW in the log, and a read that marks a document is a STOP. **A part with an in-context
reference to an app gear is not made.** It needs `IAssemblyDoc.EditPart2` and a sketch converting a gear's edge, both
new to the app and an edit mode with a dialog risk. So no candidate is held to a positive case.

## STOPs

As W9a's, plus the plan's W9c:

- **§0.3:** any dialog during a job, by the version's What's Wrong rule.
- **The user's work:**
  - a user item moved, changed or marked modified by anything but the measured carry (`users_unchanged`);
  - the groove changed;
  - a read marking a document.
- **A mode** reading other than the record and §3 say (`judged_modes`).
- **A half-change the result does not say:** a failure with nothing in `skipped`.

A refusal the app makes by name is a result, not a failure.

## Without SolidWorks

`python probe/w9c_demonstration.py --self-check` writes each starting workbook with the app's own `write_new`. It
types every edit the live run types into a copy with the app's own `write_cells`, at the address W8's `cell` would
find, reads it back with the app's own reader, and classifies it against a record built on the suite's fake
(`tests/test_swbuild.FakeSolidWorks`; pytest's decorators are stood in for where pytest is not installed). It checks:

- **fixed:** in place, with its two gates, and the footer foreseeing them; §3's row per mode from the read after the
  edit.
- **modes:** H2 added; N removed; H2 removed; H2 put back with H removed and L first.
- **remove:** G4 and HighDog removed in place, no gate unsettled.
- **remake:** legal, four remakes, its gate, L at 2.8.
- **bands-off:** the four candidates above.
- **The pure judgements, on made-up readings:** `user_items_judged`, `flags_lost_expected`, `took_active_differs`,
  `groove_kept`.

At this commit it passes, 0 failed. `--help` imports nothing of SolidWorks.

## What the packages could not be driven to, and what is not a measurement here

- **A coupling or sliding mesh newly made by Update (`NewMate`, §4 step 3.5)** is not exercised. No legal edit of
  RangeBox, RangeBox_Fixed or the 12 : 1 needs a new one: H2 reuses H's coupling, whose on-set grows. So
  `UPDATE_MAKES_MATES_WITH_MODES` would rest on the remake alone, though the gate covers both writes. Its
  measurement needs a fixture where a new mode engages a pair no mode engaged before (a third dog, say).
- **Bands taken away through the window** cannot be reached on the plan's fixture (above). The suppression is
  measured script-side only. "Bands given back unsuppress it and add no second relief" (C8) is not driven through
  Update: the script only turns the relief back on. `UPDATE_BANDS_IN_PLACE` gates both directions, so the proposal
  says it rests on giving.
- **M4 has no positive case** (above). `EXTERNAL_REFERENCES_READ` stays None, and every removal with a user
  component refuses (C4). So removal with the user's work is measured only as refusals; the 12 : 1 carries the
  going-ahead path.
- **A gear added that is not a hub** (a plain gear on a frame shaft along Z±, K6) is not exercised: the Done-when's
  Hub is the only add. Hub also covers the anchor change, which is the harder case.
- **The user's groove is an axial cut,** not a ring groove (above).
- **A user component's state in a removed mode** is not read: the worker says it generally (C5), and no unshown read
  exists (must-fix 2, W9d's).
- **The mode-showing refusal is not foreseen by the footer** (C12), and the script says so rather than asserting
  anything about the record after it. The remake's gate refusal is a `BuildError`, so W9a's refusal record does not
  keep it; the script logs what the record holds after each.
- **On 2024,** the What's Wrong box may come in `fixed` (a user feature rebuilt after the relief), and is handled by
  W9a's rule. Nothing here is version-specific beyond the `_ON_<year>` names.

## Command lines (2026; then 2024 in fresh sessions)

```
python.exe RUN\snap\probe\w9c_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9c-demo-sw2026-1.log ^
    --sections fixed,modes --master <S0's rangebox.master> --user-master <W9a's setup.master>
python.exe RUN\snap\probe\w9c_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9c-demo-sw2026-2.log ^
    --sections remove,remake,bands-off,m4,w9b-part --user-master <W9a's setup.master> ^
    --reducer-master <W9a's reducer.master>
```

The second run finds `fixed-updated.master` in the same `RUN\out`, or takes `--fixed-master`.
