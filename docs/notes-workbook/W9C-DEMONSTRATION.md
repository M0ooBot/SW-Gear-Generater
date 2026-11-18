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

After a refusal before any write, the record is held to W9C-INTERFACES §11 (B's second joining round): its
inventory carries the press's workbook digest and SolidWorks and every problem with its subjects (the finding's
name), and nothing else on the record changed. After every press that goes through, `gearbox.left` is empty.

Then the finding is patched True in this process only, logged as `PATCH findings.X = True … (was None)` and put back
as `PATCH … back to None`, and the section measures. A section proposes and never sets:

| Finding (`_ON_<year>`) | Section | Log line | What it rests on |
|---|---|---|---|
| `UPDATE_INSERTS_A_GEAR` | `fixed` | `propose UPDATE_INSERTS_A_GEAR_ON_<year> = True  # fixed: Hub built, inserted, mated and resolved in every mode, …` | Hub's part built in the copy, inserted under the `Name2` the result gives, its three mates on in every mode (`mates_made`), resolved in every mode (M5), nothing of the user's moved, each mode as §3, the second press quiet |
| `UPDATE_BANDS_IN_PLACE` (bands given, since 957b7c0) | `fixed` | `propose UPDATE_BANDS_IN_PLACE_ON_<year> = True  # fixed: bands given in place …` | the band globals and the five relief features after the groove, in no error, the bore over the relief exact, the groove unchanged |
| `UPDATE_SUPPRESSES_THE_RELIEF` (bands taken away or given back; split off in 957b7c0) | `bands-off` | `propose UPDATE_SUPPRESSES_THE_RELIEF_ON_<year> = None  # bands-off: not measured through Update …`, its facts in the JSON under `…_facts` | **no legal edit reaches it through the window (below)**: the facts are the script-side probe's (the call the worker makes, `Session.suppress_feature`, on the copy's sleeve: suppressed, on again, no second relief, RangeSlv's mates in no error in every mode) |
| `UPDATE_ADDS_A_MODE` | `modes` | `propose UPDATE_ADDS_A_MODE_ON_<year> = True  # modes: H2 added from the mode showing, …` | H2 made, the record's modes H, N, L, H2, the mode showing the same before and after, every flag and slide value as the record in every mode, H2 judged against §3's H row, each user item there said as read there (`took_active_state`) |
| `UPDATE_REMOVES_A_MODE` | `modes` | `propose UPDATE_REMOVES_A_MODE_ON_<year> = True  # modes: N deleted unshown …` | N deleted with H showing; the user's UserAngle4, suppressed in N alone, said in `flags_lost` exactly as read before; every other configuration's flags and slide values unchanged; H2 refused while it shows; H deleted with H2 showing, L the record's first |
| `UPDATE_MAKES_MATES_WITH_MODES` (the remake, since 957b7c0) | `remake` | `propose UPDATE_MAKES_MATES_WITH_MODES_ON_<year> = True  # remake: gear mates of a gearbox with modes remade, …` | the four gear mates classify remakes, in `remade_in_modes`, each one's sense read (none in `senses_unread`), the user's mates unchanged, every mode judged; its refusal first, a recorded `UserWorkRefused` since 816c261 |
| `UPDATE_MAKES_A_NEW_COUPLING` (split off in 957b7c0) | — | none | **not exercised**: no legal edit of these fixtures makes a new coupling or sliding mesh (below) |
| `EXTERNAL_REFERENCES_READ` | `m4` | `propose EXTERNAL_REFERENCES_READ_ON_<year> = None  # m4: …`, `propose EXTERNAL_REFERENCES_READ_ROUTE_CANDIDATES_<year> = [...]`, and with `--m4-part` `propose EXTERNAL_REFERENCES_READ_ROUTE_<year> = '…'` | stays None: the finding gates the app's own read, which is not written; with a part the user made by hand (below) the route is proposed from a positive case; C4's refusal stands |

The removal gates (`COMPONENT_DELETE_*`) are P1's, already set on both versions, so `remove`'s 12 : 1 press needs no
patch.

## Sections

Times are estimates for SolidWorks 2026, from W9a's and W9b's measured runs. An Update that puts every mode took about
4 min there; a refused press about 1 min; W9b's `part` 88 s.

| # | Section | What it does | 2026 |
|---|---|---|---|
| – | `ring` | By name only. The ring's Tooth Space sketch dumped as built at 55, set to 54 and built at 54, the last two compared; routes to 54 and 56 → 55; Sun at 30: a diagnostic, facts only. Details under the fifth run, below. | 2 min |
| – | `landing` | By name only. A's fix (63bbc33, c997e85) measured, with the fixes review's cases. Details below. | 9 min |
| 1 | `fixed` | **The Done-when.** Details below. Kept as `fixed-updated.master`. | 20 min (run 5) |
| 2 | `modes` | **M10.** Four edits, three presses and three refusals. Details below. | 48 min (run 5) |
| 3 | `remove` | G4 out of the 12 : 1; HighDog out of setup refused, twice. Details below. | 15 min |
| 4 | `remake` | Sun 29 → 28, Planet 13 → 14, Ring 55 → 56 with modes, on a copy of `setup.master` (it needs nothing of `fixed`'s); then the fixes review's M3 on its own copy. Details below. | 30 min |
| 5 | `bands-off` | The take-away side. Details below. | 8 min |
| 6 | `m4` | The external-references read, a probe. Details below. | 5 min |
| 7 | `w9b-part` | W9b's `part` section again, so its step-face read runs on SolidWorks in this session. | 2 min |

**About 2 h 10 min on 2026**, inside the plan's 2 h 20 min. Add 5 min if `setup.master`, and 4 min if the 12 : 1's
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
2. **The record brought forward.** `setup.master` was kept by W9a, before W9b: its record is at link schema 7 and its
   workbook has no band columns. The quiet press's finish writes the record at this app's schema, checked on disk.
3. **The edit.** The workbook's Gears header row is read and what it lacks of the app's columns said. A person
   inserts the two band columns after Slides and heads them exactly as the app's `write_new` does (`Start band (mm)`,
   `End band (mm)`), which the log says (`person … two columns inserted after Slides`); any other header missing is
   a sentence naming it, never W8's bare `StopIteration` (the first run's fault). Then the workbook is edited in Excel
   to RangeBox_Fixed: RangeSlv's At, Face width, Slides, Start band and
   End band, and Hub's row typed in, all from `model.to_sheets` of the fixture.
   - **classify:** one Update in place. Hub is added with its three mates; RangeSlv's bands are given; nothing is
     structural.
   - The read's warnings are the fixture's four.
4. **The gates' refusal**, then the findings patched.
5. **The press.** The footer foresees nothing in place. The mode showing is read before and after.
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
6. **M8.** RangeSlv's part reads:
   - Start Band 5, End Band 5 and Relief Diameter 25;
   - the relief's five features in no error;
   - W9b's `relief_bore` exact;
   - the groove kept (`groove_kept`): present, in no error, before the relief's first feature, its dimensions and
     its cut faces as before.

   W9b's step-face read rides along here. **Its reference is W9b's unbanded F0, 440.547728 mm²** (the unbanded
   part's front end face, 2026). The in-place sleeve's own end face is pierced by the user's groove (π × 1² less), and
   gave 111.4168 in the third run. The tooth outline's own loops, outer less inner (490.873329 − 376.314987 =
   114.558342), are said beside it as a fact.
7. **M5.** Hub read resolved in every mode, each shown (`Session.components`).
8. **Every user item** (`user_items_judged`, every mode shown and rebuilt, before and after), each holding:
   - Sprocket-1, -2 and -3 where they were relative to Sun or RangeSlv (route (c1)'s carry);
   - Sprocket-4 and Housing-1 where they were;
   - every user mate's flag in every mode as before, and in no error where on.

   The user's own files are unwritten.
9. **Each mode H, N, L as §3** (W9b's `judge_every` with §3's table):
   - every body at its frame on record;
   - every mate's flag as recorded;
   - the slide's value and side;
   - every app gear free;
   - no interference between two of the app's bodies (a FAIL and a STOP);
   - the bands, relief, engagement and least running gaps as §3;
   - Hub at −55.5…−35.5, 1.0 from HighDog.

   **The user's components and interference** (the coordinator's ruling on the third run). W9a's set-up stands
   Sprocket-4 on the Output axis behind the old sleeve, exactly where RangeBox_Fixed puts Hub and the longer sleeve.
   This clash is kept as it stands: a hub landing on the user's part is a real case, and the app naming it is the
   behaviour to show. Every interference SolidWorks reports with a user's component must be one the app's result
   named:
   - by pair, in each mode the app checked (its post-checks, `GearboxUpdate.modes`), with SolidWorks' Name2s mapped
     to the result's gear ids;
   - with none named that SolidWorks does not report.

   That is a check, not a STOP (`interference_judged`, `interference_said`). Said as facts:
   - the modes the app checked;
   - that the result's log CHECK lines carry the active mode's clashes only, while its status names every mode's;
   - each pair's volume, summed over SolidWorks' many small interferences, against the app's;
   - the status sentence and the footer after the press.

   The same holds in `modes` and `remake`, after each press that goes through.
10. **Saved as the user would, then a second press:** quiet, by W8's `check_quiet_update`.
11. Kept as `fixed-updated.master`, with the record also holding Hub's part entry and its `.gear.json`.

### `modes`, M10

On a copy of `fixed-updated.master`:

1. **A Modes row H2 is added** (RangeSlv at H), first refused with `UPDATE_ADDS_A_MODE` as it stands.
   - **The press:** `modes_added` `["H2"]`, H2 among the configurations, the record's modes H, N, L, H2, and the mode
     showing the same before and after.
   - **Each user mate's flag and each user component's state in H2** is read (the flag unshown, the state shown) and
     held to the result's `took_active_state`, item by item.
   - **Every mode is judged:** H2 against §3's H row, the others their own.
   - **The inventory follows the add** (B's 0eb0768, the runs review's must-fix 1). In memory and on disk, the
     record's inventory names H2 in its `modes`, and in each user mate's on-list exactly where SolidWorks' own flag
     in H2 (read unshown) reads on, and nowhere it reads suppressed. A FAIL otherwise.
2. **The user suppresses UserAngle4 in N alone** and saves.
3. **N's row is cleared** while H shows.
   - **First, with the gate patched and before its refusal is on record,** the footer is read. Either the gate's own
     stop or a recorded refusal is said in place of the prediction, so either would hide it, as in run 5 (log line
     569). It must name no user mate as suppressed in H2 (a FAIL otherwise). Every problem it foresees is kept, and
     the press that later goes through must meet none of them (a FAIL otherwise).
   - **Then it is refused** with `UPDATE_REMOVES_A_MODE` as it stands. The user's flags are read before: UserAngle4's
     in N differs from H's.
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

**The link record's JSON, as the store wrote it to disk,** goes into the run JSON (`records`) after each press and
each refusal, so a later replay can stand on the real record.

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

On a copy of `setup.master`, RangeBox with the user's work: Sun 28, Planet 14, Ring 56. It needs nothing of
`fixed`'s, so it runs when `fixed` has not (the first run's `remake` died for want of `fixed-updated.master`). The
centre distance is m(28 + 14)/2 = 26.25 as before; 28 + 2 × 14 = 56; and (28 + 56)/3 = 28, so three planets stay
evenly spaced. The workbook needs no band column for this edit.

**Not 30/12/54, as it was until the fifth run.** The ring's part from S0's master does not rebuild when set from 55 to
54 teeth: its Tooth Space cut reads code 72, a self-intersecting contour, and the pattern after it fails. Set to 56,
53, 50 or 60 it rebuilds, and so does a 54-tooth ring built from scratch. That is a fault of the part's sketch older
than W9c, which `ring` reads on its own; it is not what `remake` is here to show.

- **classify:** a value Update remaking four gear mates: Sun meshes Planet copy 1–3, and Planet copy 1 meshes Ring.
- **Unpatched, the press refuses before any write**, a `UserWorkRefused` with `PROBLEM_UNSETTLED` naming
  `UPDATE_MAKES_MATES_WITH_MODES_ON_<year>` since 816c261 (it was a `BuildError`), so it is judged and its record
  held as every other gate's.
- **Patched, the press shows:**
  - every one of those mates in `ratios` and `remade_in_modes`;
  - none in `senses_unread`;
  - the user's keyway in Sun's part not in error;
  - the user items as before (Sprocket-1 and -3 carried with Sun);
  - every mode judged by W9b's `judge_every` for an unbanded sleeve, each engaging as §3's RangeBox (H HighDog, N
    nothing, L LowDog);
  - the record brought forward to this app's schema and nothing left over (`left` empty);
  - the app's read of L at 1 + 56/28 = 3.

**Then the fixes review's M3** (B's ff98d5a), on its own copy of `setup.master`, with the gate patched as above:

1. Sun 30, Planet 12, Ring 55 → 54 is pressed with `swbuild.LANDING_STEPS = ()` for that press only, so it stops in
   the ring. The status names the ring, left in error, to close without saving; since f4eabf5 (should-fix A of
   W9C-RUNS-REVIEW.md's addendum on the final runs) it also names RangeBox and says to answer No when SolidWorks asks
   to save (`says_close_with_assembly`); the record marks the ring (`unsaved_in_error`); the patch is restored.
2. Pressed again without closing. Since 89615aa the app stops this press after its check phase and before any write
   (the eighth run found it writing a gear mate and rebuilding the assembly here). Checked, as the fixes review's
   addendum §6 asks (3a6013d):
   - **The status** says the ring is still open in SolidWorks, in error, that this press set nothing in it, and to
     close it without saving. That sentence stands alone: never that SolidWorks already matches, and no offer to save
     or keep anything. The mark stays, and nothing is set in a part.
   - **Nothing was written** (`wrote_nothing`):
     - No traced call that changes or shows anything (`nothing_changed_calls`), and no `AddComponent5` or `SaveAs3`.
     - Every part's, the layout's, the carrier's and the assembly's own globals the same before and after
       (`live_globals`; equation writes are not traced, and the assembly's flag is already set by step 1).
     - Every document of the copy with the same save flag and file time just before and just after the press. The
       flags and times are read last before the press and first after it. Which documents read modified beyond the
       three parts step 1 changed is a printed fact (`beyond_step_1`), not a check: run 11 on 34.0.0 read RangeBox.SLDASM
       modified after step 1, SolidWorks marking the open assembly when a part of it is changed and rebuilt.
     - The result's `changed`, `mates_made`, `remade_in_modes` and `placed` empty, `skipped` said, and its failures
       naming the ring's file alone.
     - The ring still in error at 54 teeth, with the same features and codes it read just before the press. Since the
       2024 addendum of `W9C-RUNS-REVIEW.md` (§4) the ring is held to itself across the press, not to 2026's codes:
       2026 reads Tooth Space 72 and Teeth 1 there, 2024 reads 51 and 51, and either is said as a fact.
     - The assembly read by W9a's `read_now` before and after, `written` empty (frames, mates' codes and flags per
       mode), and the four gear mates' ratios (`Session.gear_mate_ratio`) the same.
   - **The footer** says the ring is to be closed without saving: either "left in error when it stopped" or "still
     open in SolidWorks", with RangeBox named and "answering No when SolidWorks asks to save". The script's footer
     carries the press's note, which is now the still-in-error sentence alone. It must offer to keep nothing. The
     self-check holds the judgements to the app's own `ui_text.still_in_error_sentence`, to its stop and footer
     wording, and to the eighth and eleventh runs' statuses (which they reject).
2b. **Only the parts' windows closed** (the addendum's §6.2: should-fix A's premise, measured). Sun's, Planet's and
   Ring's own windows are closed without saving (`QuitDoc` by title), RangeBox left open, as a user who closed only the
   parts would. Facts: what SolidWorks still holds (`documents()`), every save flag, and the ring's codes where it is
   still held (no read opens a part SolidWorks let go). Then one press: whether it stops again on the ring held in
   error (`stopped_again`) is a fact; if it does, it is checked to have written nothing (`wrote_in_press`: no traced
   call that changes or shows anything, every flag and file time as before, nothing changed, made, remade or placed)
   and to say to close the ring and RangeBox without saving, answering No.
3. Every document of the copy is closed without saving, as the sentences say, and it is pressed again. It goes
   through routed (the ring by way of 53), the ring at 54 with nothing in error, the mark gone, the stage's gear mates
   remade and the footer quiet.

Sentences are matched by their distinctive parts, not whole strings.

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

The copy ends unsaved. These are proposed as the facts of `UPDATE_SUPPRESSES_THE_RELIEF_ON_<year>` (957b7c0's
split), the finding itself proposed None: no Update made that write.

### `landing` (by name only)

A's fix (63bbc33), measured. `gears.landing` foresees from the part's globals, before and after, that the new flank
start lands within 0.2 of the short solved line's new length of where it ends now. The ring's line is `Li+` to the tip
cap; the external gear's is `L+` to the root fillet. `swbuild.update_variables` then sets the change by way of the
nearest safe tooth count, with two rebuilds.

Twelve parts are built from scratch, `landing_builds`: every start that S0's master does not hold, and every routed
case's target. Each case then runs on a fresh copy, nothing is saved, and every document is closed. The rebuilds are
counted by wrapping the session's `rebuild` on its instance for the one call only.

1. **Routed by the app as it stands:**
   - ring m1.25 55 → 54, by way of 53 (foreseen at 0.038), from S0's master;
   - ring m1.25 56 → 55, by way of 54 (0.038);
   - ring m1 30 → 28, by way of 27 (0.144).

   Each is checked: `by_way_of` as foreseen, both rebuilds true, no feature in error, the target's tooth count, and the
   volume within 1e-4 (W9b's volume floor) of the target built from scratch.
2. **The threshold.** With `swbuild.LANDING_STEPS` patched to `()` in this process, the same three are set straight,
   plus spur m1 18 → 17 (0.10) and 17 → 16 (0.128); then the two externals are routed (by way of 16 and of 15). The
   straight outcomes are facts beside the foresight's fraction, for setting the threshold. The routed ones are checked
   as in 1.
3. **Unhazardous:** ring 55 → 53 and 55 → 56, and Sun 29 → 30, from the master. Each is checked: nothing foreseen,
   `by_way_of` empty, one rebuild, clean, the volume of the target built from scratch.
4. **A module change with a tooth change:** ring m1.25 40 → m1.5 32 (0.173, by way of 31), checked routed, and as a fact
   straight.
5. **The leftover:** the straight 55 → 54's file, closed without saving after its failure and reopened, read at 55
   teeth with no feature in error, against 55 built from scratch.

**The fixes review's cases** (`W9C-FIXES-REVIEW.md`, 8407159; the app as c997e85 has it):

6. **Just above 0.2, unrouted by the app:** ring m1 27 → 25 (0.204), spur m1 15 → 14 (0.203) and 14 → 13 (0.239).
   Each is checked: one rebuild, nothing foreseen, clean. No target is built for these.
7. **The old end past the new start, away from the cap:** ring m1 36 → 34 (0.056), a fact set straight and checked
   routed by way of 33; and ring m1 44 → 42 (0.367), unrouted and checked clean.
8. **Recipe B** ring 55 → 54: set straight, a fact; then by the app, checked one rebuild with no route and clean
   (c997e85 tells recipe B by its sketch's dimension links and never routes it). The dimension links among the
   equations, as the app reads them, are printed for it, and for the recipe A ring 55 → 54 (none of `HalfSpace`,
   `Flank`, `Base`, `Pitch` expected there).
9. **A module-only landing:** S0's ring 55, m1.25 → 1.225 (0.041), set straight as a fact. Routed, it is checked to go
   by way of 54 and back with both rebuilds true; clean, at 55 teeth and module 1.225; the volume of a from-scratch
   build; and the count reported unchanged (in `unchanged`, not `changed`).
10. **A user's own feature in error on a routed part** (the review's M1): on S0's ring 55, a cut through all is made
    on a circle on the ring's centre, Ø69 (it takes the tooth tips), checked clean; its diameter is then linked to Ø3
    by the user's own equation, which leaves it in the ring's hollow centre removing nothing, so it reads in error (as
    W9a's keyway did inside its Bore 14). SolidWorks will not make a cut that removes nothing at all (the eighth run,
    below). The ring is then set to 54 by the app. It must end at 54 teeth with both legs taken, Tooth Space and Teeth
    clean, and the user's cut the only feature in error before and after.

For every straight case, the short solved line (`Li+` or `L+`) is found in the Tooth Space sketch by its ends, as the
sketch's maths put them before the set. That segment's ends are read before and after the set, beside where the maths
put them after, with whether the solved end went past the origin. Recipe B draws no such line, and it is said so.

The self-check also holds each recipe B plan to the app foreseeing nothing once the dimension links its plan makes
are among the equations.

Every case also checks that it closed unsaved (the file's time and size unchanged) with nothing left open, and that
`LANDING_STEPS` is as it was. The section proposes nothing; there is no gate. It ends with one line saying whether the
fix is shown: every foreseen change routed clean as foreseen, every unforeseen one set straight clean, and the leftover
clean.

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
new to the app and an edit mode with a dialog risk. So no candidate is held to a positive case by the script.

**The first run (2026, e47d114)** answered every candidate on the five user parts and Sun, marking nothing: each
count 0, each list nine empty arrays (`[[], [], [], [], [], [], [], 0, '']`), each part's dependencies None, and the
control listing all five app parts. So every route reads "none" where there is none. Nothing yet shows which, if any,
names a reference where there is one.

**Making a positive case by hand (once, so the user can be asked).** In SolidWorks, on a copy of `setup.master`'s
folder (never the master):

1. Open `RangeBox.SLDASM` and show H.
2. In the FeatureManager tree, right-click `Housing-1` and choose *Edit Part*. The housing turns blue and the rest
   transparent.
3. Pick the housing's flat front face and start a sketch on it (*Sketch*).
4. Pick Sun's outer edge (its tip circle, or any circular edge of `Gear_m1.25_N29-1`) and press *Convert Entities*.
   The sketch now holds a circle taken from Sun's part: that is the in-context reference.
5. *Extruded Boss/Base*, Blind, 1 mm, OK. The new feature shows `->` after its name in the tree.
6. *Edit Component* again (or the confirmation corner) to leave the part's edit, then *File > Save All*. Answer the
   save dialog as it asks: this is the person's own copy.
7. Close the assembly, and give the housing's path: `--m4-part <folder>\Housing.SLDPRT --sections m4`.

With `--m4-part`, the section also reads that part read-only. Its dependencies come first
(`GetDocumentDependencies2`, closed). Then it is opened by `OpenDoc6(path, part, Silent | ReadOnly)`: the probes'
route for an assembly, options 3, and NEW for a part. Its `IModelDocExtension` count and list are read, with
GetSaveFlag around each, and it is closed again if the run opened it, never saved. Only its file name is logged.
`propose EXTERNAL_REFERENCES_READ_ROUTE_<year> = '…'` names the first candidate that names another document: a count
above 0, or a path other than the part's own. `m4_route` is pure and self-checked. `EXTERNAL_REFERENCES_READ_ON_<year>`
stays None: it gates the app's own read, which is not written yet.

## A footer's foresight held to the press (every section)

Every press in the script goes through `press`, which wraps W9a's. Just before the press, `foresight_unmasked` reads
what the footer foresees would stop it:
- the user-work problems `user_work_ahead` predicts, on a copy of the record whose inventory holds no refusal (a
  recorded refusal is said in place of the prediction until the workbook changes);
- the in-place stops `in_place_ahead` foresees, with the findings as they stand in this process.

When the press then goes through, any problem foreseen is one it did not meet, a FAIL naming each. A press that
refuses is judged by its section, as before. This is cheap: it costs no SolidWorks call.

## STOPs

As W9a's, plus the plan's W9c:

- **§0.3:** any dialog during a job, by the version's What's Wrong rule. With `--close-outlived-whats-wrong` (the
  coordinator's ruling of 2026-11-18, SolidWorks 2024 only; off unless given) a What's Wrong of the frame's that
  outlives its job is closed by its own Close button instead of stopping the run, as the 2024 section below says; any
  other window, owner or state stays the STOP.
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
- **remake:** on RangeBox with Sun 28, Planet 14, Ring 56: legal, four remakes, its gate, L at 3.
- **ring, pure:** 54 and 56 each with their Sun and Planet legal; `arc_sweep` and `sketch_diff` on made-up dumps;
  `start_lands_on_cap` by the app's own maths (55 → 54 and 56 → 55 within 0.03 mm, 55 → 53, 55 → 56, 53 → 54 not).
- **bands-off:** the four candidates above.
- **The pure judgements, on made-up readings:** `user_items_judged`, `flags_lost_expected`, `took_active_differs`,
  `groove_kept`.
- **A workbook written before W9b:** the two band columns inserted after Slides with the app's headers give the
  app's own layout, and any other missing header is named.
- **`m4_route` on made-up answers:** a route names another document, never the part itself or a count of 0.
- **The first run's footer before HighDog's removal** (`w9c-demo-sw2026-20261117-1-first-contact.log`), replayed
  against the window's W9c rule: red, and the C4 stop said, not W9a's prediction.

- **landing's plan:** each case's foresight by the app's own `_landing_route` and `gears.landing` on the part's
  equations as SolidWorks writes them, against A's numbers (to 0.0015), and against `line_gap`, the sketches' own
  maths (`internal`/`spur.involute_flank`; `start_lands_on_cap` is that for the ring), to 1e-9. Also the count each
  goes by way of, and the unhazardous ones foreseeing nothing at 1.0 and above.

At this commit it passes, 0 failed. `--help` imports nothing of SolidWorks.

## What the packages could not be driven to, and what is not a measurement here

- **A coupling or sliding mesh newly made by Update (`NewMate`, §4 step 3.5)** is not exercised. No legal edit of
  RangeBox, RangeBox_Fixed or the 12 : 1 needs a new one: H2 reuses H's coupling, whose on-set grows. Since 957b7c0
  it has its own gate, `UPDATE_MAKES_A_NEW_COUPLING`, which stays None here. Its measurement needs a fixture where a
  new mode engages a pair no mode engaged before (a third dog, say).
- **Bands taken away through the window** cannot be reached on the plan's fixture (above). The suppression is
  measured script-side only. "Bands given back unsuppress it and add no second relief" (C8) is not driven through
  Update: the script only turns the relief back on (`BandChange.back`, B's second round, is not driven). Since
  957b7c0 this side has its own gate, `UPDATE_SUPPRESSES_THE_RELIEF`, proposed None with the probe's facts.
- **M4 has no positive case** (above). `EXTERNAL_REFERENCES_READ` stays None, and every removal with a user
  component refuses (C4). So removal with the user's work is measured only as refusals; the 12 : 1 carries the
  going-ahead path.
- **A gear added that is not a hub** (a plain gear on a frame shaft along Z±, K6) is not exercised: the Done-when's
  Hub is the only add. Hub also covers the anchor change, which is the harder case.
- **The user's groove is an axial cut,** not a ring groove (above).
- **A user component's state in a removed mode** is not read: the worker says it generally (C5), and no unshown read
  exists (must-fix 2, W9d's).
- **The mode-showing refusal is not foreseen by the footer** (C12), and the script says so. After it the record is
  held to §11: the inventory kept as it was, one problem of kind `mode showing` with subjects `["H2"]`, the press's
  SolidWorks.
- **On 2024,** the What's Wrong box may come in `fixed` (a user feature rebuilt after the relief), and is handled by
  W9a's rule. Nothing here is version-specific beyond the `_ON_<year>` names.

## The confirming run on SolidWorks 2024 (2026-11-17, from 4315774, SolidWorks 2024 32.5.0)

**Setup.**
- Run folder `<probe folder>\w9c-confirm-sw2024-20261117-171854`, one `git archive` of 4315774.
- Every section but `w9b-part`, `remake` last (the re-check's advice).
- No 2024 masters were on this host, so the run built its own into `out\`: `rangebox.master` (in `landing`),
  `setup.master` and `fixed-updated.master` (in `fixed`) and `reducer.master` (in `remove`). Nothing writes to them
  after; W9d's 2024 work takes them from there.
- Four sessions of SolidWorks 2024, each started for its part and exited after:
  - PID 27368: `landing`, `fixed`, `modes`;
  - PID 64480: `remove`;
  - PID 75080: `bands-off`, `m4`;
  - PID 66428: `remake`.
- Logs `probe/results/sw2024/w9c-demo-sw2024-20261117-1-…` to `-4-…`, with their JSON.

| Section | Time | ok | FAIL | SolidWorks private after |
|---|---|---|---|---|
| landing | 987 s | 107 | 0 | 4.68 GB |
| fixed | 2541 s | 122 | 0 | 6.75 GB |
| modes | 3886 s | 80 | 0 | 9.98 GB (14.76 GB at its peak) |
| remove | 1033 s | 58 | 0 | 3.76 GB |
| bands-off | 405 s | 13 | 0 | 2.61 GB |
| m4 | 35 s | 7 | 0 | 2.82 GB |
| remake | 1542 s, cut | 46 | 1 (its time line counts 2: the FAIL and the cut, 24-4:317) | 6.38 GB |

*Corrected on 2026-11-18 from the logs' own lines, as `W9C-RUNS-REVIEW.md`'s addendum "SolidWorks 2024" (§1, `78fdcb6`)
shows: what the first version of this section said of the What's Wrong box, the memory, the times, the codes and the
interference volumes. Citations: `24-1:` to `24-4:` are the four logs in order, by line.*

**Memory, a measured difference.** SolidWorks 2024 had grown to 14.19 GB private during `modes`, with 1.90 GB free,
when the watch set its memory STOP (24-1:1680), between N's removal and the refusal of the mode showing. By the
script's rule the guard acts before the next section, so the section ran on: H's removal started at 14.69 GB private
and 1.91 GB free and ended at 14.76 GB and 0.94 GB free (24-1:1755, 1758), its checks all passing. The run then ended
after the section, 0 failed in it (24-1:1855). On 2026, runs 10 and 11 stayed under 2.3 GB private (2.29 GB at most).
- The remaining sections were split over fresh sessions, as ruled.
- In `remake`, SolidWorks grew from 3.59 to 7.09 GB private in the first press, a refusal that only reads (24-4:70,
  97), and the watch set its memory STOP during the change press, at 7.30 GB private and 1.94 GB free (24-4:98).
  `remake` was the session's only section and the guard acts between sections, so M3 ran on after it, starting at
  2.03 GB private and 2.71 GB free once the first copy was closed (24-4:251). The `done` line does not count that STOP
  (24-4:329).

**What matches 2026:**
- `landing` "the fix is shown": every foreseen change routed clean, every unforeseen one set straight clean, the
  leftover clean.
- `fixed`, `modes`, `remove`, `bands-off` and `m4` 0 failed with every proposal as on 2026.
- `remake`'s first part (28/14/56) passed and proposed its gate True. M3's step 1 stopped in the ring and marked it,
  its stop naming RangeBox and saying to answer No.
- The step faces: `GetArea` 114.303 and 114.295 against 114.558342 integrated, as on 2026.

**What differs:**
- **`landing`.** Set straight, the ring 55 → 54 and 56 → 55 still fail, and the short line's solved end lies past
  the origin as on 2026 (24-1:810, 817), so the cause reads the same. Only the codes differ: Tooth Space and Teeth read
  51 and 51 (24-1:807, 814), where 2026 read 72 and 1. 51 is the number 2024 has given for every feature in error seen
  so far (W5's over-defined mates, W9a's Sprocket-1, here the ring and the user's cut); no meaning is read into it.
- **`landing`, case 10** (the user's own feature in error on a routed part). The user's cut reads code 51 before the
  set (24-1:905), where 2026 read 71. The route and the outcome are as on 2026: both rebuilds False, ending at 54
  teeth, the user's cut the only feature in error (24-1:902).
- **The interference volumes.** Within each version SolidWorks' own sums and the app's agree in every mode but one per
  press, and the pairs are right in every mode (24-1:1282, 1521).
  - The two that differ are both the RangeSlv and Sprocket-4 pair, the app's read low: in N after `fixed`'s press,
    392.129 summed from SolidWorks' interferences against the app's 374.463 (24-1:1281), 4.5 % low; in H2 after the
    add, 160.748 against 152.629 (24-1:1520), 5.1 % low. `modes`' own press read N at 392.129 (24-1:1404). Why the
    app's read came low is not known.
  - Across versions, Hub and Sprocket-4 read 1408.381 on 2024 and 1408.364 on 2026, both sides agreeing within each
    version. That the two differ by the geometry kernel's sums is an inference; nothing measured says why.
- **Time.** Where a section can be compared, 2024 took 1.2 to 4 times as long as run 10 on 2026: `landing` 987 s
  against 824 (and 2024's built `rangebox.master` too), `modes` 3886 against 1115, `bands-off` 405 against 101,
  `m4` 35 against 17. `fixed` and `remove` also built their masters on 2024.
- **`remake` M3, a STOP before step 2.** The script's own read before step 2 (W9a's `read_now` of the assembly,
  just after step 1 left the ring in error) brought up What's Wrong 0.47 s into the job, the worker in
  `ActivateDoc3`, owned by SolidWorks' frame (24-4:310). W8's watch listed its controls, `&Close` among them
  (24-4:311).
  - **The box did not go.** At the job's end the harness waited the ruling's 60 s for it, and it was still up then:
    the fact line reads "stayed [] s; after the job it took 60.11 s to go (allowed 60); 1 up at the end, SolidWorks'
    frame enabled True" (24-4:313), and the JSON's `whats_wrong_lifetimes` holds `stayed []` and `still_up 1`.
    "Took 60.11 s to go" is the harness's words for the time it waited, which `whats_wrong_end` printed whether or
    not the box went. Nothing logged says the box ever went. This section first said it went by itself after
    60.11 s; that was wrong. It is the first What's Wrong seen to outlive its job.
  - The harness took it as the STOP (24-4:314; the log names W8-PLAN §0.5, 24-4:315), marked the worker hung, closed
    nothing and left SolidWorks as it stood (24-4:321). By the operator's account, which the log does not hold, the
    session was then killed, since it would not close with the copy's changed parts open.
  - So steps 2, 2b and 3 did not run on 2024; step 2b's facts are not measured there.
  - 2026 showed no box at that read.

**After the review: the rerun of `remake`'s M3 on 2024, made ready (2026-11-18; not run).** The review's §4 and §5
asked three things of the script before M3 runs again on 2024, and the coordinator ruled on the box:

- **The ruling** (the coordinating session's, 2026-11-18, the user's to overrule; recorded in `ISSUE-1-PLAN.md`
  beside the What's Wrong ruling it extends). On SolidWorks 2024, in a demonstration run only, a What's Wrong box owned
  by SolidWorks' own frame, with the frame enabled, that is still up 60 s after a job is logged as having outlived its
  job; the script then closes it with the box's own Close button and requires it gone within 10 s, and goes on.
  Anything else (another dialog, another owner, a disabled frame, a box that will not close) stays the STOP it is. The
  app itself is unchanged by this: it still leaves the box alone and changes no SolidWorks setting.
- **The close path** is behind the flag `--close-outlived-whats-wrong`, so every other run behaves as before. The
  flag puts W9c's `close_outlived` into W9a's harness (`WW_OUTLIVED`, None by default, which W9a's own runs and
  W9d's leave so); the log's `rule` lines say it is asked and whether it is in force (2024 with the rule True only).
  At a job's end, after W9a's 60 s, the script says the box outlived its job, then judges it (`outlived_close_refused`:
  2024; every box up one this job's watch read as the frame's; none unowned; the frame read enabled; nothing blocking;
  no other window logged), presses the box's own Close (`&Close`, the control W8's watch listed on it at 24-4:311;
  never FeatureXpert or its check box) and requires every box gone within 10 s with the frame still enabled
  (`outlived_close_failed`). *Since the re-check of these commits (`b725b32`) and the coordinator's ruling on it:*
  before either press the control is checked to be the box's one child named Close, a visible, enabled `Button`
  (`close_control`), else the STOP; the first press is a `BM_CLICK` posted to it; if the box is still up 10 s
  later, the second try posts the box the `WM_COMMAND` that control itself sends when clicked (`BN_CLICKED` with
  its id), which the ruling counts as a press of its own Close button; the box must be gone within 10 s of the last
  try. The log says which press closed it and the control's class. Microsoft documents that `BM_CLICK` to a dialog
  that is not active may fail, which is why the second try exists; neither press has been made on SolidWorks yet. The
  glue (`close_outlived_with`) reaches the windows only through an `io` the self-check stands in for, and the
  self-check drives it in every failing way. Anything it refuses or that fails is the STOP, naming why. The JSON's
  `whats_wrong_lifetimes` entry carries what was done under `outlived`. W9a's fact line now says "it was still up
  after … s" where a box is still up or was closed, and keeps "it took … s to go" for a box that went by itself.
- **Step 2's ring** is held to its own reading just before the press (above), so 2024's code 51 is no fault.
- **`remake-m3`**, by name only, runs remake's M3 alone (`remake_again`, its first pass), without remake's first
  part, whose gate is set on both versions, and then a second pass on its own copy (`remake_first_press`, folder
  `remake-first`), below. It needs only `setup.master`: from `--user-master`, or this `<out>`'s; with neither,
  W9a's `setup` runs first and builds it (about 6 minutes on 2024, W9a's confirming run's 352 s), building RangeBox
  too through S0's `build_master` unless `--master` gives `rangebox.master`. Its folder is `remake-again`, as in
  `remake`. Every press there reads the inventory, so head's reads of each user mate entity's kind run inside an
  Update on 2024 too (the review's §2).
- **The two passes of `remake-m3`** (the coordinator's ruling 5 on `b725b32`). In the first pass, the strict one
  kept as it was, the script's own read before step 2 activates RangeBox before the app's press does (06d5141's box
  came there), so a box at that read says nothing about the app, and no box in the press afterwards settles nothing:
  a user's press straight after the stop would be the first activation. The second pass makes it so: step 1 as in
  the first, then the press again at once, nothing of the script's between them opening or activating a document.
  - *It can show:* whether What's Wrong comes in the app's press as the first activation since step 1, when and at
    which call, and whether it goes by itself, outlives the press, or is closed by the close path (W9a's record of
    that app job, in the JSON under `first_press`); that the press stops again on the ring and says to close it and
    RangeBox without saving; and that it wrote nothing by its traced calls, every file's time and its result.
    *Corrected 2026-11-18, as the re-check `d48ecbf` says:* the save flags (read in a job that opens nothing) cannot
    show it, not for the documents step 1 had already modified (the three parts, marked before the press, so a
    further write leaves their flags as they were), and the 2024 run below found RangeBox.SLDASM unmarked after step 1
    and marked after the press, which made no traced call that changes anything; only the traced calls, the file
    times and the result speak to what the press wrote.
  - *It cannot show:* the parts' and the assembly's globals, the assembly's frames, mates and flags, the gear mates'
    ratios and the ring's codes are not read in it, since each of those reads opens and activates a document; so the
    strict wrote-nothing check is not made there (the first pass's step 2 makes it). It does not repeat steps 2b
    and 3.
  - *The first pass can show* everything step 2 checks, strictly, and 2b and 3; *it cannot show* what the app's press
    meets as the first activation.
  - Chosen over reordering the first pass, which would have changed a step measured on 2026 and taken the strict
    check's "before" from fewer reads; the second pass costs a copy, step 1 and one press (about 7 minutes on 2024).
- **The self-check** now holds the app's own still-in-error sentence as head words it, the ring at 51 and 51 before and
  after (passing) and changed across the press (said), and each way the close path refuses or fails; it reads 0
  failed.

*On this laptop.* The confirming run's folder, and so its 2024 masters, are on the host that ran it, not here. The
2024 masters here are `<probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master` (W9a's 2024 confirming
run, built at 19651ee on 32.5.0, its setup 0 failed) and `<probe folder>\w9-s0-sw2024-20261116-064725\out\rangebox.master`
(S0's). `remake-m3` needs the first only; given by `--user-master` it builds nothing. Its record is of W9a's schema
and is brought forward when read, as W9c's 2026 runs 1 to 7 read W9a's 2026 `setup.master` (before M3 was added;
M3 has never run from a W9a-built master, and runs 8 to 11 and the 2024 run used masters W9c's harness built; step
1's own check reads the premise, the ring stopping and marked, so a master that differs would fail there, not pass
falsely); nothing writes to the master, the section working on a copy. The command line is under "Command lines" below. *Its time is an estimate, not a
measurement:* about 32 minutes on 2024, the first pass about 25 and the second about 7, from 06d5141's M3 first press
(181 s, three times 2026's 61 s) and run 11's M3 presses on 2026 (41, then 111 s) at the same ratio; up to about 45 if
a box comes at every activation with the ring in error and each is closed (each close costs the 60 s wait and up to
10 s, or 20 with the second try; some ten such activations across the two passes). Run it from a `git archive` of the commit that carries this, in a fresh SolidWorks 2024 session with no
other SolidWorks running, in a new run folder.

## `remake-m3` on SolidWorks 2024 (2026-11-18, from c2d95cc, SolidWorks 2024 32.5.0)

**Setup.**
- Run folder `<probe folder>\w9c-remake-m3-sw2024-20261118-045041`, one `git archive` of c2d95cc with
  `SNAPSHOT_COMMIT` beside `src` (the log's head names it); the snapshot's self-check read 0 failed before the run.
- One fresh session of SolidWorks 2024 32.5.0, PID 52980, started for the run with no other SolidWorks running, and
  exited after.
- The command line under "Command lines" below, `--close-outlived-whats-wrong` given, on this laptop's W9a 2024
  `setup.master`; the section only copied it (17 files into each of `remake-again` and `remake-first`).
- Log `probe/results/sw2024/w9c-demo-sw2024-20261118-5-remake-m3-second-pass-assembly-flag.log` and
  `w9c-demo-20261118-045156.json`. Citations `24-5:` are that log's lines.

| Section | Time | ok | FAIL | STOP | SolidWorks private |
|---|---|---|---|---|---|
| remake-m3 | 1287 s | 42 | 1 | 0 | 6.86 GB at most (24-5:440), 2.63 GB after |

About 23 minutes from SolidWorks' start to its exit, against the note's estimate of 32 to 45. Free memory never fell
under 9.4 GB.

**The first pass** (`remake_again`, on `remake-again`):
- **Step 1** stopped in the ring and marked it, the status naming RangeBox and saying to answer No (24-5:65, 117, 118).
  Its press took 125.6 s.
- **The script's own read before step 2** (W9a's `read_now`, which activates RangeBox) raised What's Wrong 0.41 s
  into it, the worker in `ActivateDoc3`, owned by SolidWorks' frame (24-5:119): the box `06d5141` stopped on. It
  was still up 60.18 s after the job, the frame enabled (24-5:122), so it had outlived its job. The close path
  pressed the box's own Close (`&Close`, class `Button`, visible, enabled, id 1) by `BM_CLICK`, and the box was
  gone 0.25 s later with the frame enabled (24-5:123; the JSON's first `whats_wrong_lifetimes` entry, `closed_by`
  `BM_CLICK`). The `WM_COMMAND` second try was not needed. The read then found RangeBox.SLDASM modified beside
  step 1's three parts (24-5:125, 126), as run 11 did on 2026.
- **Step 2, pressed again without closing,** stopped before any write and passed the strict check (24-5:178): no
  call that changes or shows anything (by member `OpenDoc6` 8, `IsSuppressed2` 112, `GetSystemValue3` 1,
  24-5:133, the same members and counts as run 11's 11:316), every part's and the assembly's globals, every save flag
  and file time, the assembly's frames, mates and flags and the gear mates' ratios as before, the ring in error at 54
  teeth with Tooth Space 51 and Teeth 51 before and after. The status was the still-in-error sentence alone, naming
  the ring and RangeBox and saying to answer No (24-5:176, 177), and so was the footer (24-5:181). The press took
  127.1 s, three times run 11's 41.1 s. No What's Wrong came in it.
- **Step 2b, only the parts' windows closed,** ran on SolidWorks for the first time (no committed 2026 log holds it).
  After `QuitDoc` of Sun's, Planet's and Ring's windows, SolidWorks still held all three, the ring still in error
  at 54 teeth with codes 51 and 51; only RangeBox.SLDASM read modified, the three parts' flags reading unmarked
  (24-5:182). So the premise of should-fix A holds on 2024: a part closed alone stays loaded, in error, holding the
  new value, and its save flag no longer says so. The press (134.1 s, 24-5:191) stopped again on the ring alone,
  wrote nothing by its check, and said to close the ring and RangeBox without saving, answering No (24-5:233, 234).
  No What's Wrong came in it.
- **Step 3**, every document closed unsaved (24-5:235), went through routed by way of 53: the ring at 54 with nothing
  in error, the mark gone, the four gear mates remade, the footer quiet (24-5:322). It took 332.3 s (24-5:243). No
  What's Wrong came in it.
- Head's inventory read ran inside every press (`inventory read yes`, 24-5:62, 130, 188, 240, 375, 441), and step 3
  carried Sprocket-1, -3 and -2 with their gears in every mode (24-5:240).

**The second pass** (`remake_first_press`, on `remake-first`):
- Step 1 as in the first pass: 130.6 s, stopped in the ring and marked it (24-5:378, 430).
- Read in a job that opens nothing, before the press again: the three parts marked, every other document, RangeBox
  among them, unmarked (the JSON's `first_press.flags`, first entry).
- **The app's press again, the first activation since step 1,** raised What's Wrong 5.56 s into the job, the worker
  in `ActivateDoc3`, owned by the frame (24-5:433; W8's watch logged the call in progress as
  `GetComponentByName`, 24-5:435). The press ended with its result, the still-in-error stop, and the box was still
  up 60.24 s after it, the frame enabled (24-5:438): **it outlived the app's press.** The close path closed it by
  `BM_CLICK` on its own Close, gone 0.25 s later, the frame enabled (24-5:439; the JSON's second
  `whats_wrong_lifetimes` entry, kind `app`). The press took 191.7 s with the wait and the close (24-5:444); its
  calls by member were step 2's.
- The status was the still-in-error sentence alone; the result changed, made, remade and placed nothing and named the
  ring's failure alone; no traced call changed or showed anything (24-5:486).
- **The one FAIL** (24-5:488) is the check that the press wrote nothing by its traced calls, every save flag and file
  time, and its result: RangeBox.SLDASM's flag read False before the press and True after (`flags
  [('RangeBox.SLDASM', False, True)]`). Every other flag was as before and no file's time changed.
  - *Fact:* after step 1, RangeBox read unmarked by a read that activates nothing; across the app's press, whose
    `ActivateDoc3` is where the box came, it turned marked, with no traced call that changes or shows anything and
    no file written. In the first pass the script's own activating read found it marked (24-5:126), as run 11 did.
  - *Inference, not shown:* SolidWorks 2024 marks the assembly when it is first activated after step 1 changed and
    rebuilt its parts, whoever activates it. No read separates the activation from the rest of the press. If so,
    run 11's inference above ("it is step 1's press that leaves the assembly modified") does not hold on 2024, where
    step 1 left RangeBox unmarked; on 2026 nothing read the flag without activating, so it is not known there.
  - The check is left as it stands, for review: whether a flag SolidWorks sets on an activation the app makes counts
    as a write is a ruling, not a script fix. The status already tells the user to close RangeBox without saving and
    answer No.

**What's Wrong, box by box.**

| Box | Where it came | At | How it ended |
|---|---|---|---|
| 1 | the script's own read before step 2, first pass, `ActivateDoc3` | 0.41 s | outlived its job (up 60.18 s after it); closed by the script's `BM_CLICK` on its Close, gone 0.25 s later |
| 2 | the app's press again, second pass, the first activation since step 1, `ActivateDoc3` | 5.56 s | outlived the press (up 60.24 s after it); closed by `BM_CLICK` on its Close, gone 0.25 s later |

No box went by itself, and none came in either pass's step 1 or in the first pass's steps 2, 2b and 3; the JSON
holds these two entries only. The `BM_CLICK` closed both, so the close path's first press works on SolidWorks 2024's
box; the `WM_COMMAND` try has still never been made. Both times the frame read enabled before and after.

**What this answers** (`W9C-RUNS-REVIEW.md`'s 2024 addendum, §5 and its re-check):
- Steps 2, 2b and 3 are measured on 2024 and hold, with the strict check in step 2.
- The app's own press, made with the ring held in error as the first activation after the stop, raises What's Wrong
  on 2024 and leaves it standing after the press: the case §5 says the ruling's not-measured list and the sentences
  must take ("AHEAD should say the box goes by itself once SolidWorks rebuilds, and to close it if the Update stops
  first; the held-in-error stop on 2024 should gain a sentence"). No sentence is said around this press today
  (nothing of the user's is in error), and `src` is not changed here; that is for the coordinator.
- The first pass's step 2, the second activation, raised no box, as point for a ruling B foresaw: the box comes at
  the first activation with the ring in error.

## `remake-m3` on SolidWorks 2026 (2026-11-18, from 23107c2, SolidWorks 2026 34.1.1)

**Setup.**
- Run folder `<probe folder>\w9c-remake-m3-sw2026-20261118-053114`, one `git archive` of 23107c2 with
  `SNAPSHOT_COMMIT` beside `src` (the log's line 2 names it); the snapshot's self-check read 101 ok, 0 failed before
  the run. `probe/w9c_demonstration.py` at 23107c2 is `eee5ffe`'s, the script the 2024 run above ran.
- One fresh session of SolidWorks 2026 34.1.1, PID 35548, started for the run with no other SolidWorks running
  (26-12:4, 10.23 GB free), and exited after by a plain close request; none was left running.
- The command line under "Command lines" below, **without** `--close-outlived-whats-wrong` (the ruling that allows
  closing a box is for 2024 alone; on 2026 a What's Wrong box in a job is the STOP, 26-12:7), on this laptop's W9a
  2026 `setup.master` (`w9a-final-sw2026-20261117-023433`); the section only copied it (17 files into each of
  `remake-again` and `remake-first`, 26-12:11, 323).
- Log `probe/results/w9c-demo-sw2026-20261118-12-remake-m3.log` and `w9c-demo-20261118-054420.json`. Citations
  `26-12:` are that log's lines.

| Section | Time | ok | FAIL | STOP | SolidWorks private |
|---|---|---|---|---|---|
| remake-m3 | 989 s | 42 | 1 | 0 | 1.66 GB at most (26-12:429), 0.99 GB after |

Free memory never fell under 8.86 GB (26-12:123). SolidWorks was started at about 05:31 and the script attached at
05:44: the shell call that started SolidWorks did not return until its own timeout, so the session stood idle about
13 minutes before the run; it was exited at about 06:01.

**The first pass** (`remake_again`, on `remake-again`):
- **Step 1** stopped in the ring and marked it, the status naming RangeBox and saying to answer No (26-12:64, 117,
  118). Its press took 111.2 s (26-12:65; run 11 on 34.0.0, 61.1 s).
- **The script's own read before step 2** (`read_now`, which opens and activates RangeBox) raised no window, and
  found RangeBox.SLDASM modified beside step 1's three parts (26-12:119-121), as run 11 and the 2024 run did. No
  STOP came from `read_now`'s own guard against a flag newly set by the read, so, by the same deduction as the
  review of the 2024 run (`W9C-RUNS-REVIEW.md`, its §2), RangeBox was already marked when that read's
  `flags_before` was taken, straight after its open-and-activate. The log has no line of `flags_before` itself.
- **Step 2, pressed again without closing,** stopped before any write and passed the strict check (26-12:173): no call
  that changes or shows anything (by member `OpenDoc6` 8, `IsSuppressed2` 112, `GetSystemValue3` 1, 26-12:128,
  the members and counts of run 11's 11:316 and of the 2024 run), every part's and the assembly's globals, every save
  flag and file time, the assembly's frames, mates and flags and the gear mates' ratios as before, the ring in error at
  54 teeth with Tooth Space 72 and Teeth 1 before and after (2024 read 51 and 51; run 11 read 72 and 1). The status
  was the still-in-error sentence alone, naming the ring and RangeBox and saying to answer No (26-12:171, 172), and so
  was the footer (26-12:176). The press took 109.1 s (run 11: 41.1 s). No window came in it.
- **Step 2b, only the parts' windows closed,** ran on SolidWorks 2026 for the first time. After `QuitDoc` of Sun's,
  Planet's and Ring's windows, SolidWorks still held all three, the ring still in error at 54 teeth with codes 72 and
  1; only RangeBox.SLDASM read modified, the three parts' flags reading unmarked (26-12:177; the JSON's
  `parts_closed`). This is what 2024 read (24-5:182): a part closed alone stays loaded, in error, holding the new
  value, and its save flag no longer says so, so the premise of the advice that names the assembly holds on 2026 too.
  The press (89.6 s, 26-12:186) stopped again on the ring alone, wrote nothing by its check, and said to close the
  ring and RangeBox without saving, answering No (26-12:228, 229). In this press SolidWorks' notification box came up
  while `GetNextFeature` was in progress (26-12:180, 181), logged as the box the coordinator's ruling exempts and
  answered by nothing; it is not What's Wrong (its controls are `Title`, `Description`, `Button1`, `Button2` and
  two hyperlinks), and it is the run's one `noted` (26-12:488).
- **Step 3**, every document closed unsaved, went through routed by way of 53: the ring at 54 with nothing in error,
  the mark gone, the four gear mates remade, the footer quiet (26-12:319). It took 313.8 s (26-12:239; run 11:
  110.7 s), and carried Sprocket-1, -3 and -2 with their gears in every mode (26-12:236). Its post-checks of N and H
  read the three planets out of step with the sun and the ring off axis before the put (26-12:242, 244), the same
  lines as the 2024 run's (24-5:246, 248). The only windows were the assembly's open-progress box and the
  interference-detection progress box (26-12:233, 234), both progress boxes the watch passes.
- Head's inventory read ran inside every press (`inventory read yes`, 26-12:62, 125, 183, 236, and in the second pass 372, 431).

**The second pass** (`remake_first_press`, on `remake-first`):
- Step 1 as in the first pass: 114.7 s, stopped in the ring and marked it (26-12:374, 375, 427).
- Read in a job that opens nothing, before the press again: the three parts marked, every other document, RangeBox
  among them, unmarked (the JSON's `first_press.flags`, first entry).
- **The app's press again, the first activation since step 1,** raised no window at all: What's Wrong did not come
  (26-12:476; the JSON's `first_press.whats_wrong`, `came` and `stayed` empty), and no `DIALOG` line lies between
  the press's start and its end (26-12:428-478). It stopped again on the ring alone with the still-in-error sentence
  (26-12:433, 476), its calls by member step 2's (26-12:434), and took 93.1 s.
- The result changed, made, remade and placed nothing and named the ring's failure alone; no traced call changed or
  showed anything (26-12:476).
- **The one FAIL** (26-12:478) is the same leg as 2024's: the check that the press wrote nothing by its traced calls,
  every save flag and file time, and its result. RangeBox.SLDASM's flag read False before the press and True after
  (`flags [('RangeBox.SLDASM', False, True)]`; the JSON's `first_press.flags`, both entries). Every other flag was
  as before, no file's time changed, and `changing_calls` is empty.
  - *Fact:* on 2026 34.1.1 too, step 1 left RangeBox unmarked by a read that activates nothing, and across the app's
    press it turned marked, with no traced call that changes or shows anything and no file written. In the first pass
    the script's own activating read found it marked (26-12:119), with no STOP from that read's guard.
  - *Inference, not shown:* SolidWorks 2026 marks the assembly at its first open-and-activate after step 1, as the
    review placed it on 2024, whoever makes the activation; on 2026 it does so with no window. Run 11's inference
    ("it is step 1's press that leaves the assembly modified") does not hold on 2026 either. No read separates
    `OpenDoc6` on the open document from `ActivateDoc3`.
  - The check is left as it stands, as the task required; the review of the 2024 run says how it should read (the
    assembly's mark said as a fact when it is the only flag that changed, no traced call changed anything and no
    file's time changed). Read that way, this run's second pass would pass.

**What's Wrong.** None came on 2026 in either pass: not at the script's read before step 2, not in steps 2, 2b or 3,
not in the second pass's step 1, and not in the app's press made as the first activation since step 1. The JSON
holds no `whats_wrong_lifetimes`, and `stops` is empty. The windows the watch logged were the assembly's open-progress
box at each open (26-12:20, 233, 331, 370), the interference-detection progress box in step 3 (26-12:234, seen twice by the run's count, 26-12:485), SolidWorks'
notification box once in 2b (26-12:180), and a balloon tip about the Simplified Interface before any job (26-12:8).

**What this answers** (the review of the 2024 run, `W9C-RUNS-REVIEW.md`, its §2 and §4 item 5):
- Step 2b is measured on 2026 and reads as on 2024.
- On 2026, as on 2024, the assembly is unmarked after step 1 and marked at its first activation since; the second
  pass's flags leg reads that mark as a FAIL on both versions. Whether it is ruled the same fact on 2026 is the
  coordinator's.
- On 2026 the first activation with the ring in error raises no What's Wrong box, by the script's read and by the
  app's press alike, where on 2024 both raised one that outlived its job. This is the reading the proposed
  `WHATS_WRONG_STAYS_WITHOUT_A_REBUILD_ON_2026 = False` rested on with run 11's caveat that its press was the second
  activation; here the app's press was the first. Nothing is set in `findings.py`.

## The tenth and eleventh runs on 2026: the final run (2026-11-17, `src` at 3a9e592, SolidWorks 2026 34.0.0)

**Setup.**
- Run folder `C:\Users\M0obo\Documents\GearGeneratorProbe\w9c-final-sw2026-20261117-143421`.
- One session, PID 62172, started for the run and exited after.
- The masters were this morning's, from `…\w9c-whole-sw2026-20261117-123612\out`: `rangebox.master`,
  `setup.master` and `reducer.master`, given by `--master`, `--user-master` and `--reducer-master`. The script only
  copies them (`copy_built`'s `copytree`, `landing`'s `copy2`). The files' sizes, times and md5 were the same before
  and after.
- `fixed-updated.master` was made afresh by this run's `fixed`.

**The tenth run, every section, from a `git archive` of 3a9e592:**
`probe/results/w9c-demo-sw2026-20261117-10-final-whole-remake-script-fault.log` and `w9c-demo-20261117-143454.json`.

| Section | Time | Failed |
|---|---|---|
| landing | 824 s | 0 |
| fixed | 700 s | 0 |
| modes | 1115 s | 0 |
| remove | 396 s | 0 |
| remake | 397 s | 1 |
| bands-off | 101 s | 0 |
| m4 | 17 s | 0 |
| w9b-part | 97 s | 0 |

There was no STOP. Everything measured matches the eighth and ninth runs: `landing`'s straight facts, `fixed`'s
interference volumes, the step faces and m4's answers.
- `remake`'s first part (28/14/56) passed again and proposed its gate True.
- Its M3 step stopped after step 1 on the script's own `AttributeError`. `gear_entry(box, "Planet")` is None: the
  record holds the planet only as Planet copy 1 to 3. This was fixed in eabf14e (`files_of`), checks unchanged.

**The eleventh run, `remake` again with `--redo`, in the same session and `out`:**
`probe/results/w9c-demo-sw2026-20261117-11-final-remake-step2-assembly-flag.log` and `w9c-demo-20261117-153629.json`.
697 s, one FAIL, no STOP. Its snapshot is `git archive 3a9e592` with `probe/w9c_demonstration.py` alone from eabf14e.
Its `src` is 3a9e592's, compared file by file; 007b3aa, which changed `update.py` since, is not in it.

- **Step 1** stops in the ring and marks it, as before.
- **Step 2 wrote nothing, and the app stopped before any write.**
  - The press made no call that changes or shows anything: by member, `OpenDoc6`, `IsSuppressed2` and
    `GetSystemValue3` only.
  - Every part's globals, every document's save flag and file time, the assembly's frames, mates and flags per mode,
    and the four gear mates' ratios (29 : 13 and 13 : 55, as built) were the same before and after.
  - The result's `changed`, `mates_made`, `remade_in_modes` and `placed` were empty. `skipped` said "the assembly,
    because Ring_m1.25_N55.SLDPRT is in error", and the one failure named the ring's file.
  - The ring still read Tooth Space 72 and Teeth 1 at 54 teeth.
  - The status and the footer were the still-in-error sentence alone.
- **The one FAIL is the script's expectation, not a write.** Only step 1's three parts were expected to read modified,
  but `RangeBox.SLDASM` read modified before step 2 as well as after. The fact line says so:
  `before step 2, modified ['Gear_m1.25_N13.SLDPRT', 'Gear_m1.25_N29.SLDPRT', 'RangeBox.SLDASM',
  'Ring_m1.25_N55.SLDPRT']`, as did `read_now`'s own read before the press.
  - No SolidWorks call came between step 1's press and that read. So it is step 1's press (its part value sets and
    rebuilds) that leaves the assembly modified on SolidWorks.
  - The check is left as it stands, for review.
- **Step 3**, after every document was closed unsaved, loaded each from its file, the ring at 55. It went through
  routed by way of 53 (rebuilt twice), and the ring ended at 54 with nothing in error. The mark was gone, the four gear
  mates were remade, and the footer was quiet.
  - The log does not show whether the mark went by 1cc2978's check-phase read (`read_clean`, not logged by the
    script) or by the ring's change: both apply here.

## The eighth and ninth runs on 2026 (2026-11-17, from 64bec58, on SolidWorks 2026 34.0.0)

On the second Windows host (`DESKTOP-QJTI7HF`), whose SolidWorks 2026 is revision 34.0.0, where the earlier runs had
34.1.1. One session, PID 74488, started for the run and exited after. Run folder
`C:\Users\M0obo\Documents\GearGeneratorProbe\w9c-whole-sw2026-20261117-123612`.

None of the masters was on this host, so the run built each where it was first needed, into its own `out`:
- S0's `rangebox.master` by S0's `build_master` at the start of `landing`;
- W9a's `setup.master` by W9a's `setup` at the start of `fixed`;
- W9a's `reducer.master` by W9a's `reducer` at the start of `remove`.

Every check of each build passed. `fixed` keeps `fixed-updated.master` in the same `out`.

**The eighth run, every section, from a `git archive` of 64bec58:**
`probe/results/w9c-demo-sw2026-20261117-8-whole-remake-m3-again-fails.log` and `w9c-demo-20261117-123719.json`. It took
70 minutes:

| Section | Time | Failed |
|---|---|---|
| landing | 690 s | 1 |
| fixed (with setup.master) | 967 s | 0 |
| modes | 1197 s | 0 |
| remove (with reducer.master) | 396 s | 0 |
| remake | 713 s | 2 |
| bands-off | 96 s | 0 |
| m4 | 18 s | 0 |
| w9b-part | 94 s | 0 |

There was no STOP. `fixed`, `modes` and `remake` proposed their gates True on 2026 as before. `bands-off` and `m4`
proposed theirs None as before.

- **`landing`, case 10 (the script's fault).** `FeatureCut4` on the Ø3 circle at x = 200 mm handed back no feature.
  SolidWorks will not make a cut that removes nothing, so the case never reached the app. The cut is now made valid
  and put in error after (above). The other 25 cases and the leftover read as the seventh run's, to the same
  volumes: 0.0379 and 0.0378 fail set straight (codes 72 and 1), and the rest are clean.
  - The fixes review's new cases ran for the first time, all clean: just above 0.2 unrouted, 36 → 34 routed by way
    of 33, recipe B never routed, the module-only landing by way of 54 and back with the count reported unchanged.
  - Set straight, these rebuilt clean: 36 → 34 (0.056), recipe B's 55 → 54, and S0's ring at module 1.225 (0.041).
- **`remake`, the fixes review's M3, pressed again without closing (the app's fault, not fixed here).** On
  SolidWorks the second press does not end clean, as it does on the fake. Every part reads as already holding the
  workbook's values. The job then goes on into the assembly: it makes one gear mate again (`AddMate5` once). The
  assembly's rebuild then fails, since the ring is still in error in SolidWorks.
  - The status names RangeBox and says "press Update SolidWorks again once that is put right, or save it in
    SolidWorks to keep what it did". It never says that the ring is still open in error, nor to close without saving.
    The footer says the same.
  - The record keeps the ring's mark, and nothing is set in a part.
  - The cause, at 64bec58: `Finished.still_in_error` is filled only when the press has no failure
    (`workbook/update.py` 2263), and `ui_text.gearbox_update_status` says it only then (1888). Head still has both
    conditions.
  - The press after closing without saving goes through, routed by way of 53. The mark goes, the footer is quiet,
    and the four gear mates are remade.

**The ninth run, `landing` again with `--redo`, into the same `out` and session:**
`probe/results/w9c-demo-sw2026-20261117-9-landing-again-clean.log` and `w9c-demo-20261117-134821.json`. 571 s,
0 failed, the fix shown. Its snapshot is `git archive 64bec58` with `probe/w9c_demonstration.py` alone taken from
550767c, the script's fix. The scripts it imports are 64bec58's. Its `src` is 64bec58's: on `workbook`, 550767c
sits on others' changes to `src`, which this evidence does not cover.
- Case 10: the user's cut was made clean at Ø69, then read code 71 once linked to Ø3.
- The app routed 55 → 54 by way of 53, both rebuilds reading false for the user's cut.
- The ring ended at 54 teeth with that cut the only feature in error before and after, and the volume of a 54 built
  from scratch.

**What differs from 34.1.1:**
- Nothing measured. The interference volumes in `fixed` (1408.364, 160.785, 392.233), the step faces (`GetArea`
  114.302999694 against the integrated 114.558341769) and m4's answers are the same to every figure printed.
- The post-check's "Ring off its axis" and "out of step" after `remake`'s presses read as in the sixth run.
- `modes` took 20 min, against 48 on 34.1.1.

## The seventh run on 2026 (from 71d8510): `landing`

`landing` passed: 0 failed, 305 s, and "the fix is shown" True. Set straight, 0.0379 and 0.0378 failed; 0.0996 and
0.1276 (external), and 0.1438 and 0.1730 (rings), rebuilt clean. Since then, the fixes review's cases were added on
A's c997e85 (above), and its M3 on B's ff98d5a, in `remake`.

## The sixth run on 2026 (from 30bf0e9), and what changed

`probe/results/w9c-demo-sw2026-20261117-6-remake-clean-ring-cause.log` (6cdc709). **`remake`, on 28/14/56, passed
with 0 failed.** `ring` confirmed the hypothesis:

- in the 54 set from 55, against the 54 built from scratch, lines #4–#6 end 62.4 mm off;
- 56 → 55 fails too;
- through 56 or 53 to 54 is clean;
- a forced rebuild does not mend it, and 54 → 55 does not recover.

A fixed it in the app (63bbc33), measured by the new `landing` section above. `ring` and `landing` leave the default
order and run by name.

- **The spline reads in `sketch_dump` failed** (`GetStartPoint2`/`GetEndPoint2`: AttributeError; `GetPoints2` handed
  back objects, not doubles). As the macro database's API-LEDGER records, `ISketchSpline.GetPoints2` gives sketch
  point objects, and a spline has no `GetStartPoint2`. The dump now reads each point's X and Y, and takes the first
  and last as the spline's ends.

## The fifth run on 2026 (from 9efcb2c), and what changed

`probe/results/w9c-demo-sw2026-20261117-5-fixed-modes-bands-off-clean.log` (88289c4). `fixed`, `modes` and
`bands-off` passed with 0 failed. `remake` stopped again in the ring's part. `ring` said where: set from 55 to 54 by
the app's own `update_variables`, Tooth Space reads code 72 (`swFeatureErrorSketchContainsSelfIntersectingContour`)
and Teeth code 1. Every sketch still reads fully defined, and no equation is in error. Set to 56, 53, 50 or 60 the
same part rebuilds; a 54-tooth ring built from scratch is clean.

- **`remake` now changes Sun 29 → 28, Planet 13 → 14, Ring 55 → 56** (above), which the diagnostic shows rebuilds and
  keeps the stage. L's ratio is 3.
- **`ring` is now short (about 2 min) and facts only.** 53, 50 and 60 are dropped. On fresh copies, nothing saved,
  every copy closed:
  - **The Tooth Space sketch dumped** (`sketch_dump`) on (i) the part as built at 55, (ii) after the set to 54, and
    (iii) a 54-tooth ring built from scratch by the strip's `plan_for` and `swbuild.build`. The dump holds:
    - every segment in `GetSketchSegments` order: its `swSketchSegments_e` type, construction flag, end points, and
      for an arc its centre, radius, `GetRotationDir` and sweep, in sketch coordinates to 1e-6 mm (a spline its
      point count and first and last points);
    - the sketch's dimensions by name, as `SystemValue` (m, rad);
    - the relations' `swConstraintType_e` kinds.

    Every member returning an array goes through `member`, which calls one late binding hands back uncalled. Then
    `sketch_diff` prints (ii) against (iii): which segments differ and by how much, and any dimension or relation
    kind that differs; also (i) against (ii), the segments whose direction or sweep changed.
  - **Routes on fresh copies,** each reporting only whether every feature ends clean, and the volume:
    - 54, then a second forced rebuild (`ForceRebuild3(False)`);
    - 56, then 54;
    - 53, then 54;
    - 54, then 55 (does it recover?);
    - 56, then 55, the hypothesis's own test (below).
  - **No `begin_build`/`end_build` route:** `swbuild.update_variables` already runs inside that bracket.
  - **Sun 29 → 30,** the external-gear control.
- **The hypothesis, from `gears/internal.py`'s `_space_ops_involute`.** The ring's sketch holds two fixed equation
  curves `I±`. `Li±` is a radial line from each curve's start (the flank start, diameter da − m here, since
  db < da − m) to the tip-cap circle (diameter da − 2m). It is held only by "origin on `Li±`" and "`Li±.end` on
  `cap`", and is 0.625 mm long. The chord `T` joins the two `Li` ends.
  - For every count from 51 up, n's cap diameter (nm − 4m) is exactly (n − 1)'s flank start (nm − 3m).
  - So set from 55 to 54, the new `I+.start` lands 0.024 mm from where `Li+` ends now (`start_lands_on_cap`). The
    0.625 mm line collapses almost to a point and turns nearly tangential.
  - From there "on the cap, on a line through the origin" has two solutions: the near end (0.625 mm inward) and
    the far one, past the origin (about 63 mm). If the solver takes the far one, or swaps `T`'s ends, the contour
    crosses itself, and is still fully defined.
  - 55 → 53, 55 → 56 and 53 → 54 put the new start 0.6 mm or more away, and they rebuild.
  - The dump confirms this if, in (ii) against (iii), a short line (`Li+` or `Li-`) or `T` differs by tens of
    mm while the curves, fillets and root arc agree, and if 56 → 55 fails too. It refutes it if (ii) and (iii) differ
    first in a fillet or `R`'s sweep (an arc's other side), or if 56 → 55 rebuilds.

## The fourth run on 2026 (from cdd3bbb), and what changed

`probe/results/w9c-demo-sw2026-20261117-4-fixed-and-remove-clean.log`. `fixed` passed with 0 failed, proposing both
its gates True, and `remove` passed with 0 failed. `modes` did not start, and `remake` stopped in the ring's part.

- **`modes`: the master kept unsaved marks (the script's fault).** An Update saves nothing, so `fixed-updated.master`'s
  record listed the assembly and the sleeve as unsaved. A copy of it then read as not valid: `clear_saved` dropped
  them, since the saved files were newer. The record on disk loses such a mark only when a later finish writes it,
  and only for a document that press loaded from its file. The window's read clears it in memory only, never on disk.
  So `fixed` now does what a person would:
  1. saves;
  2. reads the save flags;
  3. closes everything of the copy;
  4. presses again, which loads every document from its file and finds it holding what the workbook asks;
  5. checks that this second press is quiet (W8's `check_quiet_update`), and that the record on disk then holds no
     unsaved or mismatched document;
  6. only then keeps the master.

  `bands-off` starts from the same master.
- **`remake`: "nothing else on it changed (False)" was the script's comparison, by design of the app.** B's
  `update.refused_update` writes the SolidWorks the press read onto `gearbox.solidworks` (schema 9). setup.master's
  record is from before that field, so it had none.
  - In `fixed` the same check passed on a record of the same age because `fixed`'s quiet press, before its gate's
    refusal, had already written the field.
  - `refusal_on_record` now allows exactly that change, `gearbox.solidworks` from none to the press's revision, and
    says so. It names any other difference with its value before and after (`record_changes`, self-checked).
- **`remake` stopped in the ring's part.** Sun and Planet rebuilt at 30 and 12 teeth; `Ring_m1.25_N55.SLDPRT` set to
  54 reported a rebuild error, and the Update stopped. It said what it had changed and that nothing was saved, which
  is right for a failed part. No gear mate was remade. `remake` now ends there, as a FAIL naming the part, rather
  than judging modes on a half-done change. It stays on 30/12/54 until the cause is known.
- **A new section `ring`, run first:** a diagnostic, script-side, facts only, proposing nothing. Every step runs on a
  fresh copy of the part from S0's master, and nothing is saved.
  - **(a)** No. of Teeth 54, set by the app's own `swbuild.update_variables` and rebuilt.
  - **(b)** The same at 56, 53, 50 and 60. With Sun 84 − n and Planet n − 42, each keeps the stage's centre distance
    and three evenly spaced planets, and the self-check reads each fixture legal.
  - **(c)** A 54-tooth ring built from scratch by the strip's `plan_for` and `swbuild.build`, with the plan's checks
    and what the strip's read says of the ring.
  - **(d)** Sun 29 → 30, which rebuilt in `remake`.

  For each step it reads and logs:
  - every feature's error code (`feature_states`), and for each one in error its `swFeatureError_e` name and what
    `GetErrorCode2` returns beside it;
  - each sketch's constrained status, and its relations counted by every `swSketchRelationFilterType_e` filter;
  - every equation's text, value and `IEquationMgr.Status`;
  - `GetWhatsWrong` (NEW);
  - the globals, the bodies and the volume.

  The enumerations are read from the install's `swconst.tlb`, by the probes' own reader. It takes about 4 minutes.

## The third run on 2026 (from ad2bcd9), and what changed

`probe/results/w9c-demo-sw2026-20261117-3-fixed-updated-in-place.log`. The Done-when's Update went through:
- Hub built, inserted, mated and resolved in every mode;
- the bands given in place, the relief exact and the user's groove kept;
- every user component and mate as it was;
- H, N and L as §3.

Then `fixed` stopped itself on the script's judgement, not the app: it counted Sprocket-4's interference with Hub and
the sleeve as "a mode other than §3". The judgement is now as above. The self-check replays it on that run's JSON
and log:
- SolidWorks reported interferences in H (21), N (20) and L (1), none between two app bodies;
- each pair with Sprocket-4 was named by the app's post-check of that mode, and none named was unreported;
- SolidWorks' volumes summed per pair equal the app's (H: 1408.364 and 160.785; N: 1408.364 and 392.233; L: 1408.364).

**Elsewhere after the cut, on the same or a neighbouring ground:**
- **The second press, the kept master and `bands-off`** judge no interference, so nothing there would have failed.
- **`modes` would have failed after N's removal.** W9b's `judge_every` measured the slide from N's frame, and a
  record without N has none. It now leaves `moved` unsaid there. The §3 rows are held through `section3_of`, which
  needs no N.
- **The step faces** are now held to W9b's F0 (above). The replay shows the in-place integrated area, 114.558342,
  lands on 114.558403 to 1e-4.

## The first run on 2026 (e47d114, from 957b7c0), and what changed

`probe/results/w9c-demo-sw2026-20261117-1-first-contact.log`; `m4` and `w9b-part` 0 failed, `remove` 2 FAILs,
`fixed` stopped before its edit, and `modes`, `remake` and `bands-off` did not run.

- **`fixed` (the script's fault):** W9a's `setup.master` holds a workbook written before W9b, with no band columns,
  and W8's `cell` raised a bare `StopIteration` for *Start band*. The script now reads the header row, inserts the two
  band columns after Slides with the app's own headers where they are missing, says so, and names any other missing
  header in a sentence. `same_sheets` had passed, since it compares the rows as the app reads them, not the headers;
  the header row is now said. The record there is at schema 7: the first press's finish brings it forward (checked
  on disk), and the sidecars at schema 1 become 2 where bands are given (checked).
- **`remake` no longer needs `fixed`.** It runs on `setup.master`. `modes` and `bands-off` still need
  `fixed-updated.master`, which is a guard.
- **`remove`, FAIL 1 (the app's: B's footer):** the 12 : 1's record holds no SolidWorks version, so the footer
  foresaw `COMPONENT_DELETE_*_ON_?` unsettled, red, and the press then went ahead. The check stays; B is changing the
  footer to judge over the versions the findings know.
- **`remove`, FAIL 2 (the script's expectation was stale):** with C4's refusal foreseen, B's footer
  (`ui_text.workbook_footer`) says the stop, red, in place of W9a's prediction of what the press does with the
  user's work. That is right: a green line predicting a carry beside a red footer saying the press would not run
  would be wrong. The script's `footer_ahead` now holds the footer to that rule (`ui_text.in_place_line` said, the
  prediction not), and W9a's `ahead_of` otherwise. The self-check replays the run's own footer line against it.
- **`remove`, not checked then and checked now:** after G4's removal the record still listed `OutputGear.SLDPRT`
  among its parts, though no gear uses that file any more. C6 says the entry leaves `parts`. This now FAILs as a
  check (below).
- **`w9b-part` answered W9b's step-face question.** Each step face is one planar face. Its outer loop is one circle
  of r 12.5; its inner loop is 170 edges (68 arcs at r 0.1875, 9.375 and 12.375, 68 lines and 34 splines). Its area
  integrated from GetTessPts points is 114.558342 mm², against F0 − π(Ro² − r²) = 114.558403. `GetArea` reads
  114.303, 2.2e-3 low. So GetArea under-reads this face, and the geometry is right.
- **Since the script was written:**
  - A split two gates (957b7c0).
  - The remake's gate refusal became a recorded `UserWorkRefused` (816c261), now checked as every other gate's.
  - B's second round says what the record holds after each refusal and each stop. The script checks the refusals'
    subjects, digest and SolidWorks, that nothing else changed, the mode-showing refusal's kept inventory, and
    `gearbox.left` empty after each press that went through.

## Command lines (2026; then 2024 in fresh sessions)

```
python.exe RUN\snap\probe\w9c_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9c-demo-sw2026-1.log ^
    --sections fixed,modes --master <S0's rangebox.master> --user-master <W9a's setup.master>
python.exe RUN\snap\probe\w9c_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9c-demo-sw2026-2.log ^
    --sections remove,remake,bands-off,m4,w9b-part --user-master <W9a's setup.master> ^
    --reducer-master <W9a's reducer.master>
```

The second run finds `fixed-updated.master` in the same `RUN\out`, or takes `--fixed-master`.

SolidWorks 2024, `remake`'s M3 alone with the ruling's close path (2026-11-18), on this laptop's masters:

```
python.exe RUN\snap\probe\w9c_demonstration.py RUN\snap\src RUN\out --pid PID ^
    --log RUN\w9c-demo-sw2024-5-remake-m3.log --sections remake-m3 --close-outlived-whats-wrong ^
    --user-master <probe folder>\w9a-confirm-sw2024-20261117-002313\out\setup.master
```

Without the flag the run is as before, and a What's Wrong that outlives its job is the STOP.

SolidWorks 2026, `remake`'s M3 alone (2026-11-18), without the flag, on this laptop's W9a 2026 master:

```
python.exe RUN\snap\probe\w9c_demonstration.py RUN\snap\src RUN\out --pid PID ^
    --log RUN\w9c-demo-sw2026-12-remake-m3.log --sections remake-m3 ^
    --user-master <probe folder>\w9a-final-sw2026-20261117-023433\out\setup.master
```
