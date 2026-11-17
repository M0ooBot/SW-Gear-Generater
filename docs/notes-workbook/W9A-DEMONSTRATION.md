# W9a's demonstration on SolidWorks: the sections, the commands, the STOPs

The script is `probe/w9a_demonstration.py`. It covers the assembly side of ISSUE-1-PLAN §5's W9a *Done when*, the
coordinator's no-carrier measurement, and the additions from `W9A-REVIEW-B.md`. Its review is
`W9A-DEMONSTRATION-REVIEW.md` (`a8e07b4`), taken in one fix round (`1008cf5`) under the coordinator's rulings. The
window side (K12) is the W8 stage of `probe/workbook_window_check.py`.

**How it works.** It imports W8's demonstration and S0's script and changes neither.

- From W8's: the attach, the dialog watch, Excel, copying and keeping masters, the drive and the user's turn, and the
  call trace.
- From S0's: the user's parts, a part's pose relative to its gear, the window list, staying awake.

Every Update and Build is the app's own (`swbuild.update_gearbox` / `build_gearbox`). `Desk9` runs the Workbook
window's own code: `_plan_solidworks_pass`, `_open_record`, `_write`, `_finish_update`, `_finish_build`,
`_record_refusal` and `_mark_not_as_built` are `WorkbookWindow`'s functions themselves, run on Desk9.

- **Restated, not the window's own:** only `press_update`'s job (the session's revision, then `update_gearbox`) and
  `_start_build`'s (`old_assembly` as `before`).
- **Before every press:** the footer must offer it (`update_shown`, `update_enabled`, not Build again…).
- **The app's Recent list:** APPDATA is pointed into `<out>\appdata` before anything of the app is imported, and the
  run refuses to start if `store.recent_path()` is not there. The user's own settings are never written.

## Sections, in the order for the first run on SolidWorks 2026

The short sections come first, so a fault in the script shows in minutes. Run them one or two at a time into the same
`<out>`: a section `<out>` already holds is skipped, and kept masters are found there.

Times marked "measured" are from the run on SolidWorks 2026 at `9dded70` (2026-11-16,
`w9a-demo-sw2026-20261116-204824`). The others are estimates, scaled from that run and from S0 and W8 (a press
putting every mode took 238 s on 2026 and 515 s on 2024; on 2024, about twice 2026).

| # | Section | What it does and proves | Answers | 2026 | 2024 |
|---|---|---|---|---|---|
| 1 | `m3` | On a copy of S0's master: a user sprocket on Input Axis held by one distance to the layout's Front plane (UserFront), and a fixed housing. The baseline is clean by construction; the distance it leaves to the housing is read. (1) A second mate, UserGap, to the housing at that distance plus 1 mm, which no side can satisfy; an assembly rebuild by the app's route with it in error, then the app's value Update with it; then UserGap suppressed and the assembly clean again. (2) A keyway in the user's own Sprocket part, put in error by its Bore 10 → 14 (S0's P0 mechanism); the part's and the assembly's rebuild, then a value Update. Each is read for the rebuild's return, What's Wrong count, the codes and any new window. | **M3** for the assembly rebuild, first, because a dialog there is a STOP | 7 min (measured) | 15 min |
| 2 | `setup` | On a copy of S0's master, the user's work (below), saved in place, closed and reopened. The app's reads (`components`, `mate_info`, `feature_states`) with GetSaveFlag around them. A quiet Update that records the inventory, with the footer before and after. The pure judgement showing each unmeasured branch refusing. Kept as `setup.master`. | **M1** (coincident, distance, angle and lock; user–user, user–layout and user–gear; marks nothing), **M2** (the inventory must list the keyway in Sun's part and nothing of the app's), the record's revision | 4 min (measured) | 8 min |
| 3 | `go` | On a copy of setup.master, two presses, each after the user's turn of +37° in the mode it puts (H, then L): a value Update (Sun's Backlash 0.4) and a slide-offset Update (RangeSlv `L=+5.5`). Before each press: the footer's prediction and every user mate's entities. After: the checks listed below. | ***Done when*: both Updates go ahead, the sprockets found on their gears, every user mate on in its modes and in no error, the keyway rebuilt; the inventory and the footer before and after; review B's item 3 (the carry foreseen is the carry done)** | 17 min (measured) | 35 min |
| 4 | `m1` | On a copy of setup.master: a user gear mate, and a distance mate suppressed in H (asserted to be the active mode) but on in N and L. Read by `mate_info` and by a quiet Update's inventory. | **M1**: the gear kind, and a mate suppressed in the active mode. Whether the latter reads whole is proposed, not asserted. | 3 min (measured) | — |
| 5 | `refuse` | On a copy of setup.master, six steps (below), each under its own net. Each press is judged by its own call trace (no show, flag, value, rebuild, put or mate made) and by reads before and after: frames, the user mates' codes, flags and entities, and Sun's globals. A document marked by a refused press is a STOP. The record keeps each refusal, and the footer says it in red. | ***Done when*: a lock to a fixed housing refuses naming it; a Bore Diameter typed in SolidWorks refuses naming the cell**. Also review B's item 3, ruling 5, and `PROBLEM_OTHER_KIND` | 32 min (measured, with the lightweight step) | 60 min (by name only) |
| 5a | `lightweight` | On a copy of setup.master: Sprocket-1 set lightweight; a quiet press records it from the live session; the footer foresees the refusal; a press refuses it. All on the assembly as it stands, never saved while a component is lightweight. Sprocket-1 is resolved again before the copy is saved or closed. | **review B's item 4**: a carried component loaded lightweight refuses, foreseen | 6 min | 12 min (by name only) |
| 6 | `again` | On a copy of setup.master, Sun's Part name changed, so Build again…. The question must name the user's components and the User Keyway, with the time read. The old assembly is opened, then put behind `Housing.SLDPRT`. The app's own `swbuild.read_old_assembly` runs alone, then the build. | §2.1 item 8; review B's item 2; review point 4 | 6 min | — |
| 7 | `again-dirty` | As `again`, but the old assembly also needs a rebuild: UserDist4 is changed and not rebuilt. | review B's item 2 | 6 min | — |
| 8 | `again-closed` | As `again`, with the old assembly closed: not read and not opened; the window's sentence gives the record's inventory. | §2.1 item 8 | 5 min | — |
| 9 | `reducer` | The 12 : 1, written by `write_new` with its Output folder blank and built to turn. Kept as `reducer.master`. | — | 4 min | 7 min |
| 10 | `k3` | On a copy of reducer.master: a user keyway in G1's part. A quiet press must list it (M2 on the 12 : 1). Then G1's Bore 8 → 14 in the workbook, an ordinary value Update, rebuilds the keyway into error. The footer must say the keyway follows. The Update must name it as the user's (`user_features_in_error`, its sentence), and G1's app features must read no error. A window here ends this section only. | **K3 in an app part, and M3 as the app meets it** (review point 6) | 6 min | 11 min |
| 11 | `nocarrier` | On a copy of reducer.master, three sprockets: locked to the driving G1 (S0's A), to the driven G4 (B), and one locked to the first (E, a chain). The user's turn and G4 At 27 → 30, first with `USER_MATE_PUT_NO_CARRIER_ON_<year>` None: the app's refusal, foreseen by the footer and judged by its trace. Then the finding patched True in this process only, the press, the reads. A further rebuild, a second turn, and G4 At 30 → 27. Every put must be an app body or a locked sprocket. | **The coordinator's measurement**: proposes the finding True only if both presses and every read are clean | 11 min | 19 min |

**m3's first run** (2026-11-16, snapshot `2920a09`) failed in its own set-up, and this is why m3 is built as above.

- UserFront (100 mm to the layout's Front) and UserGap (40 mm to the housing's Front) agreed in value but not in side.
  A plane-to-plane distance mate's side is AddMate5's Flip, which the app's `distance` leaves False, and no finding
  says which side that is.
- So UserGap came back status 5, with codes 46 and 47 (`findings.MATE_ERROR_OVER_DEFINED` / `MATE_ERROR_ILL_DEFINED`),
  before the step meant to make the contradiction.
- That step set UserGap's value in every mode in one `set_dimension_in` call, and it read 0 in N and L. The app sets a
  distance one configuration per call, and a configuration never set reads 0 (`findings.VALUE_UNSET_READS_ZERO`).
- Kept as a fact: with those two user mates in error, the assembly rebuild returned True, GetWhatsWrongCount read 3,
  and no window came up.

For the same reason, setup's Sprocket-4 now stands 90 mm from Sprocket-3, inserted at z 130. Either side SolidWorks
takes (130 or −50) is clear of every body. setup reads which side it took and checks that no user component
interferes, and go holds Sprocket-4 to the distance as copied. m1's per-mode distance is to the layout's Front (±160).
`again-dirty` changes UserDist4 in the active mode only, by one `set_dimension_in` call, from the value read.

**setup's user work:**

- Sprocket-1 on Input Axis, locked to Sun;
- Sprocket-2 on Output Axis, locked to RangeSlv;
- Sprocket-3 locked to Sprocket-1;
- Sprocket-4 on Input Axis, held by a 90 mm distance to Sprocket-3 (user–user) and an angle to the layout;
- Housing-1, fixed;
- a keyway in Sun's part.

**What `go` checks after each press**, with every mode shown:

- each app body is at its frame on record;
- each locked sprocket is at its pose on its gear, as set up, to 1e-6;
- every user mate is on in the modes it was on in, reads no error code, and joins what it joined before (entities);
- every traced put is an app body or a locked sprocket (any other put is a STOP);
- Sprocket-4 is at its distance from Sprocket-3;
- the train is free;
- the keyway reads code 0;
- the record holds the carried sprockets, the keyway, and revision 34.1.1 (32.5.0 on 2024).

**refuse's steps, in order:**

1. A user lock from Sprocket-1 to the fixed Housing-1. Foreseen and refused naming Housing-1. Then, with the workbook
   changed (ruling 5), the footer says "has changed since" and foresees the same refusal, in red, naming the lock.
2. A mate of another kind on Sun: Sprocket-4's axis on Sun's own axis.
3. The solver's tie: Sprocket-1's Top plane on Housing-1's.
4. A user lock from Sun to RangeSlv.
5. Sun's Bore Diameter typed 12 in SolidWorks, refused naming `Gears!J2`.
6. Steps 1, 4 and 5 together: every problem in one press, the value first.

At `9dded70` there was a seventh step, Sprocket-1 lightweight. Its save before the press raised SOLIDWORKS CAM's modal
box (see *Found on SolidWorks*) and hung the session. That step is now the `lightweight` section: no save while
Sprocket-1 is lightweight, and the script's own reads find it with `lightweight_ok`. The six steps above passed in that
run with 0 failed.

**What the `again` sections check on the old assembly.** These are read without activating it (the app's
`use_open_document`), before and after `read_old_assembly` and again after the build. The front document is checked
only around `read_old_assembly`, since the build brings forward the documents it makes.

- the front document, which must stay `Housing.SLDPRT`;
- GetSaveFlag, both ways;
- `NeedsRebuild2`;
- the active configuration;
- every mate's code, flag per mode and entities;
- every component's frame;
- the windows of SolidWorks' process;
- the user files' modification times.

A changed state ends that section only. A window is a §0.3 STOP and ends the run (ruling 1).

**SolidWorks 2026: all twelve sections, about 1 h 50 min.**

**SolidWorks 2024's confirming set** (`--sections confirm`) follows *Rules carried over*: one full turning build with
its edits, plus the sections where the versions may differ. That is m3, setup, go, reducer, k3 and nocarrier, about
1 h 35 min.

- `setup` and `go` are the build with its edits.
- `m3` and `k3` are rebuilds that can raise a dialog there.
- `reducer` and `nocarrier` give `USER_MATE_PUT_NO_CARRIER_ON_2024`.
- `refuse` is not in the set, because S0 saw no difference between the versions in the reads it rests on. It runs on
  2024 by name (about 60 min); whether to run it there is the user's call. So does `lightweight` (about 12 min);
  2024 is the version said to open components lightweight, so it is the cheap one to add. The plan's *Done when*
  ("2024 confirms the assembly sections") reads broader than the rule, and the note follows the rule.
- Run it as two fresh sessions: `m3,setup,go`, then `reducer,k3,nocarrier`.

## Command lines

Make a `git archive` of the commit to run into `RUN\snap`, with `SNAPSHOT_COMMIT` beside `src` (`RUN\snap\SNAPSHOT_COMMIT`).
Start SolidWorks for the run and give its PID. Keep the same `RUN\out` for every invocation of one version, and give
each invocation its own log.

```
rem SolidWorks 2026: the first two sections
python.exe RUN\snap\probe\w9a_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9a-sw2026-1.log ^
    --sections m3,setup --master C:\Users\M0obo\Documents\GearGeneratorProbe\w9-s0-20261116-045513\out\rangebox.master

rem then, one or two at a time, into the same RUN\out (setup.master and reducer.master are found there)
python.exe RUN\snap\probe\w9a_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9a-sw2026-2.log ^
    --sections go,m1 --master C:\Users\M0obo\Documents\GearGeneratorProbe\w9-s0-20261116-045513\out\rangebox.master
rem … refuse; lightweight; again,again-dirty; again-closed,reducer; k3,nocarrier

rem SolidWorks 2024, two fresh sessions into RUN24\out
python.exe RUN24\snap\probe\w9a_demonstration.py RUN24\snap\src RUN24\out --pid PID --log RUN24\w9a-sw2024-1.log ^
    --sections m3,setup,go ^
    --master C:\Users\M0obo\Documents\GearGeneratorProbe\w9-s0-sw2024-20261116-064725\out\rangebox.master
python.exe RUN24\snap\probe\w9a_demonstration.py RUN24\snap\src RUN24\out --pid PID2 --log RUN24\w9a-sw2024-2.log ^
    --sections reducer,k3,nocarrier

rem the window check's W8 stage, SolidWorks 2026 only
python.exe RUN\snap\probe\workbook_window_check.py RUN\snap\src RUN\window --pid PID --only w8 --log RUN\w9a-window.log
```

**Re-running.**

- A section `RUN\out` already holds is skipped and said. `--redo` sets its folder aside (`<name>.prev-<time>`) and runs
  it again; for `setup` or `reducer` that also sets their master aside, and later sections then use the new one.
- Masters from another `<out>` are given by path: `--user-master`, `--reducer-master`.
- A section that needs a master that is neither given nor in `<out>` builds it first, and says so.

The JSON (`w9a-demo-<time>.json`) is written beside the log after every section. Its `proposal` holds:

- M3's readings, for the assembly and for an app part (`M3_app_part`);
- M1's "suppressed in the active mode reads whole";
- `USER_MATE_PUT_NO_CARRIER_ON_<year>`.

## What must be open or closed

- **SolidWorks.** A session started for the run, and no other SolidWorks running: the window check attaches to the
  newest.
  - No document of the user's open whose file name a copy uses: `RangeBox*.SLDASM`, `Gear_m1.25_*`, `SunGear.SLDPRT`
    (the again sections make it), `Sprocket.SLDPRT`, `Housing.SLDPRT`, `Reducer_12to1*`, `Gear_m1.5_*`, `Gear_m2_*`,
    `OutputGear`.
  - The user's documents are never touched, and are logged as `<user document N>`.
- **Excel.** The script starts and quits its own. The user's Excel may stay open, but not with a fixture workbook open.
- **The laptop.** On mains power, with the lid open. The script asks Windows to stay awake, but a closed lid still
  sleeps the machine (S0's run 3 was lost that way). At least 3 GB free; under 2 GB the run stops.
- **The window check.** The screen at 2560 × 1600, 150 %, and nothing dragged over the window.

## The STOPs it can raise

**Each of these ends the run:**

- **Any window.** A window W8's watch logs WHILE a job runs is a STOP at once: the dialog is named, the worker is
  marked hung and left alone, and nothing more is asked of SolidWorks (`watched_wait`; at `9dded70` such a window was
  only a NOTE, and the run waited behind it until the session hung). A #32770 or titled window that appears after an
  assembly rebuild, a part rebuild, an Update, the old-assembly read or a build also stops the run. What's Wrong in
  m3 is one of these.
  - Exempt, and logged as facts: SolidWorks' notification box, its balloon tips (class `swBalloonTip`, such as the
    "Over Defined" one m3 brings), and its progress boxes that close themselves.
  - k3 is the exception: a window seen there after its job has answered ends k3 only (ruling 3). A modal one during
    the job holds the worker, so it stops the run like any other.
- **A document marked modified** by a `read_now` read, by the setup and m1 reads (`components`, `mate_info`,
  `feature_states`), or by a refused press (§0.3). `feature_list` and `users_in_copy` read without it.
- **An Update that puts a component** that is neither an app body nor a locked sprocket (§0.3, from the call trace).
- **A user mate made or set that does not read back as set** in every mode (§0.3).
- **A frame read None** (W8's rule).
- **Under 2 GB of free memory.**
- **A hung worker or a lost session.** The JSON is written, and the remaining sections are re-run into the same `<out>`.

**These end only their section:**

- in `again`, `again-dirty` and `again-closed`, any change to the old assembly across `read_old_assembly` or the build:
  - the front document;
  - its save flag;
  - its active configuration;
  - its rebuild state;
  - a mate's code, flag or entities;
  - a component's frame (in `again-dirty`, a rebuild shows as Sprocket-4 moving 0.5 mm);
  - a user file's modification time;
- a window in `k3`;
- any raise of the script's own, which fails its section only. Within `refuse`, it fails its step only.

**Not STOPs: failures the coordinator reads.** These say the app or the plan is wrong:

- a press that refuses when it should go ahead, or the reverse;
- a carried sprocket off its gear;
- the footer's prediction differing from the press;
- the no-carrier put not clean (then the finding stays None).

## Found on SolidWorks

Facts the runs found, for W9d and anything else that will save, close or act on an assembly holding the user's
components.

1. **SOLIDWORKS CAM blocks a save of an assembly with a lightweight component.** With the SOLIDWORKS CAM add-in
   loaded (as on this device's SolidWorks 2026 34.1.1), saving such an assembly (`SaveAs3`, as a person's save)
   raises a modal Yes/No dialog, "SOLIDWORKS CAM Warning": *"SOLIDWORKS CAM data cannot be stored as lightweight parts
   have been detected. Proceeding with save operation will result in loss of previous SOLIDWORKS CAM data. Do you want
   to continue?"* `SaveAs3` does not return until it is answered.
   - Seen in `refuse`'s lightweight step at `9dded70` (`w9a-demo-sw2026-20261116-204824\stdout-2.txt`, lines
     413-520).
   - The app never saves (Update leaves everything unsaved; W9d is planned not to save the carried items). A W9d that
     saves, closes or saves-as an assembly holding the user's components must first resolve them, or must expect the
     box.
2. **Two user mates in error, and the assembly rebuild still returns True.** With UserFront and UserGap over-defined
   (codes 46 and 47), the assembly rebuild by the app's train route returned True, GetWhatsWrongCount read 3, and no
   window came up (m3's first run, `2920a09`).

## What the script cannot show, and what it leans on

**What it cannot show:**

- **M1's width, limit and path mates, and a leaf inside a user sub-assembly.** The app's `add_mate` has no verified
  route for those kinds, and inserting a sub-assembly is P2's probe ahead. These move to S5 in W9c's sessions, which
  reads every mate kind.
- **A lock joining two different trains.** RangeBox is one train over every mode's links, so `refuse` shows the
  two-body refusal on one train. The judgement does not tell the two cases apart.
- **`PROBLEM_LOCK_BY_MODE` on SolidWorks.** A user lock on in some modes only, on a put gear, would also tie Sun
  through Sprocket-4's angle to the layout. It is tested against the fake.
- **K1's component found by its part under a new name.**
- **The held-gear, fixed-gear and sub-assembly branches.** These are shown refusing only by the pure judgement on a
  real inventory, as the coordinator asked. They are not measured.
- **The wheel over each window with the other focused** (W9A-REVIEW-B point 7). This is a person's step.
- **The footer's ceiling, where the sentence scrolls in itself.** It is not reached on this screen (E4's built footer
  is about 281 px against a ceiling near 523 px), so only the Tk test covers it.
- **K12 itself**, which is the window check's job. Its W8 stage measures:
  - the footer on its box, `_status_box`;
  - the frame's `GetWindowRect` inside the work area;
  - the window's real height;
  - every footer button whole;
  - the body's last line scrolled into view.

  After a sentence set by `_set_status` alone, it checks the box and the buttons again.

**What it leans on beyond the app's interfaces:**

- `Desk9`'s two restated jobs.
- `wb_update._judged_trains`, for the pure branch judgement.
- Raw reads and writes the app does not have: `NeedsRebuild2`, `GetWhatsWrongCount`, and `SetSuppression2(1)` for
  lightweight.
- The window attributes the window check measures: `_status_box`, `_status_bar`, `_status_scrolls`, `_foot`, `_page`,
  `_page_bar`, `_body`, `status_label`, the four footer buttons, `_set_status`, `_refresh_state`, `work_area` and
  `FOOTER_SHARE`.
