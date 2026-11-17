# W9a's demonstration on SolidWorks: the sections, the commands, the STOPs

The script is `probe/w9a_demonstration.py`. It covers the assembly side of ISSUE-1-PLAN §5's W9a *Done when*, the
coordinator's no-carrier measurement, and the additions from `W9A-REVIEW-B.md`. The window side (K12) is the W8 stage
of `probe/workbook_window_check.py`.

**How it works.** It imports W8's demonstration and S0's script and changes neither:

- from W8's: the attach, the dialog watch, Excel, copying and keeping masters, the drive and the user's turn;
- from S0's: the user's parts, the pose of a part relative to its gear, the window list, staying awake.

Every Update and Build is the app's own (`swbuild.update_gearbox` / `build_gearbox`). They run through `Desk9`, which is
W8's `Desk` with the calls the Workbook window makes since W9a:

- `classify(..., read_sidecar=)`;
- the session's revision passed to `finish_update`;
- `_record_refusal`;
- `before=` and the stayed-behind sentence in a Build again….

## Sections, in the default order

Each section runs alone with `--sections NAME` and starts from a kept master, so a lost session costs one section.
Every copy section ends with its copy closed (`end_copy`).

Times are estimates, not measurements. They are scaled from S0 (a case took about 6 min on 2026 and 8 to 11 min on
2024), from W8 (a press that puts every mode took 238 s on 2026 and 515 s on 2024), and from RangeBox's build (124 s).

| Section | What it does and proves | Answers | 2026 | 2024 |
|---|---|---|---|---|
| `m3` | On a copy of S0's master: a user sprocket with two distance mates and a fixed housing. (1) An assembly rebuild by the app's route with a user mate in error (UserGap 40 → 41 against UserFront), then the app's value Update with that mate in error. (2) A user keyway in the user's own Sprocket part, its own Bore 10 → 14 (S0's P0 mechanism), the part's and the assembly's rebuild, then a value Update. Each is read for the rebuild's return, What's Wrong count, the codes and any new window. | **M3**, first, since a dialog there is a STOP | 12 min | 24 min |
| `setup` | On a copy of S0's master, the user's work: Sprocket-1 on Input Axis locked to Sun; Sprocket-2 on Output Axis locked to RangeSlv; Sprocket-3 locked to Sprocket-1; Sprocket-4 on Input Axis, with a distance to Sprocket-3 (user–user) and an angle to the layout; Housing-1 fixed; a keyway in Sun's part. Saved in place as a person would, closed and reopened. Then the app's reads (`components`, `mate_info`, `feature_states`) with GetSaveFlag around them, and a quiet Update that records the inventory, with the footer before and after. Then the pure judgement on that inventory, showing the held-gear, fixed-gear, no-carrier and sub-assembly branches refusing. Kept as `setup.master`. | **M1** (coincident, distance, angle and lock; user–user, user–layout and user–gear; reads mark nothing), **M2**, the record's inventory and revision, the branches refusing | 7 min | 13 min |
| `m1` | On a copy of setup.master: a user gear mate between two sprockets, and a distance mate suppressed in H but on in N and L. Both read by `mate_info` with H active and by a quiet Update's inventory. | **M1**: a gear mate, and a mate suppressed in the active mode. Whether the latter reads whole is proposed, not asserted. | 5 min | — |
| `go` | On a copy of setup.master, two presses, each after the user's turn of +37° (in H, then in L): a value Update (Sun's Backlash 0.4) and a slide-offset Update (RangeSlv `L=+5.5`). Before each press, the footer's prediction. After each, every mode is shown and read. | ***Done when*: a value and a slide-offset Update go ahead, the sprocket found on its gear, every user mate on in its modes and in no error, the keyway rebuilt; the inventory and the footer before and after; the footer's carry against the press's (review B, item 3)** | 16 min | 32 min |
| `refuse` | On a copy of setup.master, six refusals. Each press is checked to write nothing (frames, mate codes and flags, marks, Sun's globals). The record keeps each refusal and the footer says it, red. | ***Done when*: a lock to a fixed housing refuses naming it; a Bore Diameter typed in SolidWorks refuses naming the cell**. Also review B's item 4 (lightweight) and the footer's refusal against the press's. | 16 min | 30 min |
| `again` | On a copy of setup.master, Sun's Part name changed, so Build again…. The question names what stays behind, with its time. The build job reads the old assembly first while it is open. | §2.1 item 8; review B's item 2 | 5 min | — |
| `again-dirty` | As `again`, with the old assembly open and needing a rebuild: UserDist4 is changed and not rebuilt. | review B's item 2 | 5 min | — |
| `again-closed` | As `again`, with the old assembly closed. The sentence gives the record's inventory. | §2.1 item 8 | 5 min | — |
| `reducer` | The 12 : 1, written by `write_new` with its Output folder blank and built to turn. Kept as `reducer.master`. | — | 4 min | 7 min |
| `nocarrier` | On a copy of reducer.master, three sprockets: one locked to the driving G1 (S0's A), one to the driven G4 (B), and one to the first (E, a chain). Then the user's turn and G4 At 27 → 30, first with `USER_MATE_PUT_NO_CARRIER_ON_<year>` None (the app's refusal, foreseen by the footer), then with the finding patched True in this process only. After that, a further rebuild, a second turn and G4 At 30 → 27. | **The coordinator's measurement**: proposes `USER_MATE_PUT_NO_CARRIER_ON_<year>` True only if both presses and every read are clean | 10 min | 18 min |

**The refusals in `refuse`:**

1. Sprocket-1 set lightweight, recorded by a quiet press, foreseen by the footer, refused.
2. A user lock from Sprocket-1 to the fixed Housing-1. Foreseen and refused with "Housing-1" named. Then green once
   the workbook changes.
3. The solver's tie: Sprocket-1's Top plane coincident with Housing-1's.
4. A user lock between Sun and RangeSlv.
5. Sun's Bore Diameter typed 12 in SolidWorks, refused naming `Gears!J2`.
6. 2, 4 and 5 together, all named at once, the value first.

**What `go` checks after each press**, with every mode shown:

- each app body is at its frame on record;
- each locked sprocket is at its pose on its gear, as set up, to 1e-6;
- every user mate is on in the modes it was on in and reads no error code;
- Sprocket-4 is at its distance from Sprocket-3;
- the train is free;
- the keyway reads code 0;
- the record holds the carried sprockets and revision 34.1.1 (32.5.0 on 2024).

**What the `again` sections check on the old assembly.** Before and after the build job, without activating it, they
read:

- GetSaveFlag;
- the active configuration;
- `NeedsRebuild2`;
- every mate's code and flag per mode;
- every component's frame;
- the windows of SolidWorks' process;
- the user files' modification times.

A change in any of them is a STOP for that section.

**SolidWorks 2026: every section, about 1 h 25 min.**

**SolidWorks 2024: `--sections confirm`,** which is m3, setup, go, refuse, reducer and nocarrier, about 2 h 05 min.

- This is the confirming build: one full turning build with its edits (`go`), plus the sections where the versions may
  differ: the tie and the user-lock put (`refuse` and `nocarrier`).
- `m3` is included because a dialog on 2024's assembly rebuild would undo every 2024 Update.
- Run it as two fresh sessions, as W8's 2024 runs were: `m3,setup,go` first, then `refuse,reducer,nocarrier` with
  `--user-master` pointing at the first session's `setup.master`.

## Command lines

Make a `git archive` of the commit to run into the run folder, with `SNAPSHOT_COMMIT` beside `src`. Start SolidWorks for
the run and give its PID. `<out>` must be a fresh folder.

```
python.exe <snap>\probe\w9a_demonstration.py <snap>\src C:\Users\M0obo\Documents\GearGeneratorProbe\w9a-sw2026-<ts>\out ^
    --pid <PID> --log C:\Users\M0obo\Documents\GearGeneratorProbe\w9a-sw2026-<ts>\w9a-sw2026-<ts>.log ^
    --master C:\Users\M0obo\Documents\GearGeneratorProbe\w9-s0-20261116-045513\out\rangebox.master

python.exe <snap>\probe\w9a_demonstration.py <snap>\src C:\...\w9a-sw2024-<ts>\out --pid <PID> --log C:\...\w9a-sw2024-<ts>.log ^
    --sections m3,setup,go --master C:\Users\M0obo\Documents\GearGeneratorProbe\w9-s0-sw2024-20261116-064725\out\rangebox.master
python.exe <snap>\probe\w9a_demonstration.py <snap>\src C:\...\w9a-sw2024b-<ts>\out --pid <PID2> --log C:\...\w9a-sw2024b-<ts>.log ^
    --sections refuse,reducer,nocarrier --master <the same 2024 master> --user-master C:\...\w9a-sw2024-<ts>\out\setup.master

python.exe <snap>\probe\workbook_window_check.py <snap>\src C:\...\w9a-window-<ts> --pid <PID> --only w8 --log C:\...\w9a-window-<ts>.log
```

**Re-running one section** after a lost session: `--sections NAME` with the masters the earlier run kept
(`--user-master <out>\setup.master`, `--reducer-master <out>\reducer.master`). A section that needs a master that is
neither given nor in its `<out>` builds it first, and says so.

The JSON (`w9a-demo-<ts>.json`) is written beside the log after every section. Its `proposal` holds M3's readings, M1's
"suppressed in the active mode reads whole" and `USER_MATE_PUT_NO_CARRIER_ON_<year>`.

## What must be open or closed

- **SolidWorks.** A session started for the run, and no other SolidWorks running (the window check attaches to the
  newest). No document of the user's open whose file name a copy uses (`RangeBox*.SLDASM`, `Gear_m1.25_*`,
  `Sprocket.SLDPRT`, `Housing.SLDPRT`, `Reducer_12to1*`, `Gear_m1.5_*`, `Gear_m2_*`, `OutputGear`). The user's
  documents are never touched and are logged as `<user document N>`.
- **Excel.** The script starts and quits its own. The user's Excel may stay open, but not with a fixture workbook open.
- **The laptop.** On mains power, the lid open. The script asks Windows to stay awake, but a closed lid still sleeps the
  machine: S0's run 3 was lost that way. At least 3 GB free; under 2 GB the run stops.
- **The window check.** The screen at 2560 × 1600, 150 %. Nothing to be dragged over the window while it runs.

## The STOPs it can raise

**Each of these ends the run:**

- **Any window**: W8's watch logs a dialog, or a titled window, or a #32770 appears after an assembly rebuild, a
  part rebuild or an Update. That includes What's Wrong in M3. SolidWorks' notification box and its balloon tips
  ("Over Defined" in `m3`) are exempt (the coordinator's ruling).
- **A read marking a document modified**: GetSaveFlag before and after any `read_now`, `components`, `mate_info` or
  `feature_states` read, and after every refused press (§0.3).
- **A user mate made or set that does not read back as set in every mode** (§0.3: a new mate whose per-configuration
  state does not read back).
- **A frame read None** (W8's rule).
- **Under 2 GB of free memory.**
- **A hung worker or a lost session**: the run ends, the JSON is written, and the remaining sections are re-run alone.

**These end only their section** (the coordinator, item 2): in `again`, `again-dirty` and `again-closed`, any change
to the old assembly across the build job:

- its save flag;
- its active configuration;
- its rebuild state;
- a mate's code or flag;
- a component's frame (`again-dirty` sees a rebuild by Sprocket-4 moving 0.5 mm);
- a user file's modification time;
- a window.

**Not STOPs: failures the coordinator reads.** These mean the app or the plan is wrong, not that the run must halt:

- a press that refuses when it should go ahead, or goes ahead when it should refuse;
- a carried sprocket off its gear;
- the footer's prediction differing from the press;
- the no-carrier put not clean (then the finding stays None).

## What the script cannot show, and what it leans on

**What it cannot show:**

- **M1's width, limit and path mates, and a leaf inside a user sub-assembly.** The app's `add_mate` has no verified
  route for those kinds. Inserting a sub-assembly is P2's probe ahead (a "find file" dialog risk), planned for W9c's
  sessions.
- **K3's "a user feature in an app part rebuilt into error is named as the user's"** on SolidWorks. RangeBox's gears
  have no bore. Failing a keyway in an app part takes an app value, which K11 refuses. M3's feature case therefore
  fails a feature in the user's own part; SolidWorks' rebuild report does not depend on who made the part.
- **A lock joining two different trains.** RangeBox is one train over every mode's links, so `refuse` shows the two-body
  refusal on one train. The judgement does not tell the two cases apart.
- **The held-gear, fixed-gear and sub-assembly branches.** These are shown refusing only by the pure judgement on a
  real inventory, as the coordinator asked. They are not measured.
- **K12 itself**, which is the window check's.

**What it leans on beyond the app's interfaces:**

- `Desk9` mirrors five window methods (`_plan_solidworks_pass`, `press_update`, `_record_refusal`, `_start_build`,
  `_finish_build`), because the window's own cannot run without Tk.
- `wb_update._judged_trains`, for the pure branch judgement.
- `Session.use_open_document`, for reading the old assembly without activating it. The script falls back to setting
  `_build_doc` itself where the source lacks it.
- Raw reads and writes the app does not have: `NeedsRebuild2`, `GetWhatsWrongCount`, and `SetSuppression2(1)` for
  lightweight.
- The window attributes: `_status_box`, `_status_bar`, `_status_scrolls`, `_foot`, `_page`, `_page_bar`, `_body`,
  `status_label`, the four footer buttons, `_set_status`, `_refresh_state`, `work_area` and `FOOTER_SHARE`.
