# W9a's demonstration on SolidWorks: the sections, the commands, the STOPs

The script is `probe/w9a_demonstration.py`. It covers the assembly side of ISSUE-1-PLAN §5's W9a *Done when*, the
coordinator's no-carrier measurement, and the additions from `W9A-REVIEW-B.md`. Its review is
`W9A-DEMONSTRATION-REVIEW.md` (`a8e07b4`), taken in one fix round (`1008cf5`) under the coordinator's rulings. The
2026 runs are reviewed in `W9A-RUN-2026-REVIEW.md` (`6700505`), whose findings 1, 3, 5, 6, 7, 8 and 9 the script and
this note now take. The window side (K12) is the W8 stage of `probe/workbook_window_check.py`.

Two of the run review's notes are W8's wording, which this script imports and does not change: "post-check of H: …
out of step" after go's slide press is the `ModeCheck` of H as found on showing, before the put (finding 11), and the
CAM NOTE's "before this run made any configuration" is W8's boilerplate (finding 13).

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

Times marked "measured" on 2026 are from the closing run on SolidWorks 2026 (34.1.1), one session at `6f3d6fb` with
the again sections rerun at `6b9d8aa`: `probe/results/w9a-close-sw2026-2026111*.log`, reviewed in
`W9A-CLOSE-2026-REVIEW.md` (`2a8f9d1`), about 70 min for the twelve sections. On 2024 they are from the confirming run
on SolidWorks 2024 (32.5.0), `probe/results/sw2024/w9a-confirm-sw2024-20261117-*.log`. The others are estimates.

| # | Section | What it does and proves | Answers | 2026 | 2024 |
|---|---|---|---|---|---|
| 1 | `m3` | On a copy of S0's master: a user sprocket (Sprocket-1) on Input Axis, held by one distance to the layout's Front plane (UserFront), and a fixed housing. It reads SolidWorks' "show errors every rebuild" and the three M3 findings (by `getattr`; a check fails if one is missing), held against the app's own `assembly_rebuild_settled`. The baseline is clean by construction; the distance it leaves to the housing is read. (1) UserGap to the housing at that distance plus 1 mm, which no side can satisfy; the assembly rebuild with it in error; a quiet press, then the footer naming UserGap as in error; a value Update. Then UserGap suppressed and the assembly clean again. (2) A keyway in the user's own Sprocket part, put in error by its Bore 10 → 14; the part's and the assembly's rebuild; a quiet press, the footer naming Sprocket-1, a value Update. Sprocket-1 is carried by nothing. Each Update is judged by the findings and by the rebuild just read: where they let it, it goes ahead, and its result and sentence name the user's item as already in error before; otherwise it stops as before, its sentence naming it. (3) Sprocket-1, its part still in error, locked to Sun so a press would carry it; a quiet press then records the lock (it carries nothing, so it does not refuse), the footer must foresee the refusal of Sprocket-1, and the press must refuse before any write (the app's new rule), judged by its trace and reads and held against the footer's prediction. | **M3** for the assembly rebuild, first, because a dialog there is a STOP; K3 for a feature in a user's part | 16 min (measured, closing run) | 5 min until the STOP (stopped at What's Wrong; see `box`) |
| 2 | `setup` | On a copy of S0's master, the user's work (below), saved in place, closed and reopened. The app's reads (`components`, `mate_info`, `feature_states`) with GetSaveFlag around them. A quiet Update that records the inventory, with the footer before and after. The pure judgement showing each unmeasured branch refusing. Kept as `setup.master`. | **M1** (coincident, distance, angle and lock; user–user, user–layout and user–gear; marks nothing), **M2** (the inventory must list the keyway in Sun's part and nothing of the app's), the record's revision | 3 min (measured) | 6 min (measured) |
| 3 | `go` | On a copy of setup.master, two presses, each after the user's turn of +37° in the mode it puts (H, then L): a value Update (Sun's Backlash 0.4) and a slide-offset Update (RangeSlv `L=+5.5`). Before each press: the footer's prediction and every user mate's entities. After: the checks listed below. | ***Done when*: both Updates go ahead, the sprockets found on their gears, every user mate on in its modes and in no error, the keyway rebuilt; the inventory and the footer before and after; review B's item 3 (the carry foreseen is the carry done)** | 11 min (measured) | 25 min (measured) |
| 4 | `m1` | On a copy of setup.master: a user gear mate, and a distance mate suppressed in H (asserted to be the active mode) but on in N and L. Read by `mate_info` and by a quiet Update's inventory. | **M1**: the gear kind, and a mate suppressed in the active mode. Whether the latter reads whole is proposed, not asserted. | 2 min (measured) | — |
| 5 | `refuse` | On a copy of setup.master, six steps (below), each under its own net. Each press is judged by its own call trace (no show, flag, value, rebuild, put or mate made) and by reads before and after: frames, the user mates' codes, flags and entities, and Sun's globals. A document marked by a refused press is a STOP. The record keeps each refusal, and the footer says it in red. | ***Done when*: a lock to a fixed housing refuses naming it; a Bore Diameter typed in SolidWorks refuses naming the cell**. Also review B's item 3, ruling 5, and `PROBLEM_OTHER_KIND` | 19 min (measured, closing run) | 40 min (by name only) |
| 5a | `lightweight` | On a copy of setup.master: each instance's state read by the script's own `GetSuppression2` before, after Sprocket-1 alone is set lightweight, and after the reset; a quiet press records the states from the live session; the footer foresees the refusal; a press refuses, and must name exactly the carried instances the raw read shows lightweight. All on the assembly as it stands, never saved while anything is lightweight; Sprocket-1 is set back first and every instance read again, to log whether resolving one is reported as resolving the others; whatever still reads lightweight is then resolved, one by one, before the copy is closed. | **review B's item 4**; W9A-RUN-2026-REVIEW finding 3 (the refusal named three sprockets where one was set) | 4 min (measured) | 8 min (by name only) |
| 6 | `again` | On a copy of setup.master, Sun's Part name changed, so Build again…. The question must say what stays behind, held to the clauses that say it (*your … stay in RangeBox.SLDASM*, *your … stay in <the old part>*) and without pinning the app's wording otherwise; whole names only, each count beside its noun in that clause, the features beside their part: every user component named or covered by an "N other components" that adds up, the mates by their count, the User Keyway and its sketch with Sun's old part, the time the inventory was read (its date too, if one is said), and "nor anything added since". The build's sentence is held to the same: as the build read the old assembly (open), or the record's inventory with its time (closed). The old assembly is opened, then put behind `Housing.SLDPRT`. The app's own `swbuild.read_old_assembly` runs alone, then the build. | §2.1 item 8; review B's item 2; review point 4 | 5 min (measured) | — |
| 7 | `again-dirty` | As `again`, but the old assembly also needs a rebuild: UserDist4 is changed and not rebuilt. | review B's item 2 | 5 min (measured) | — |
| 8 | `again-closed` | As `again`, with the old assembly closed: not read and not opened; the window's sentence gives the record's inventory. | §2.1 item 8 | 1.5 min (measured) | — |
| 9 | `reducer` | The 12 : 1, written by `write_new` with its Output folder blank and built to turn. Kept as `reducer.master`. | — | 1.5 min (measured) | 1.5 min (measured) |
| 10 | `k3` | On a copy of reducer.master: a user keyway in G1's part. A quiet press must list it (M2 on the 12 : 1). Then G1's Bore 8 → 14 in the workbook, an ordinary value Update, rebuilds the keyway into error. The footer must say the keyway follows. The result must list it, and the SENTENCE must name it as the user's and newly in error; where the M3 findings let it (2026 after the app's change) the Update goes ahead, otherwise it stops as before. Every component's error code is read after it: G1's, in error through the keyway in its part, is not counted against the app. A window seen after the job ends this section only. | **K3 in an app part**, and M3 as the app meets it | 1 min (measured, gone ahead) | 2 min |
| 11 | `nocarrier` | On a copy of reducer.master, three sprockets: locked to the driving G1 (S0's A), to the driven G4 (B), and one locked to the first (E, a chain). The user's turn and G4 At 27 → 30, first with `USER_MATE_PUT_NO_CARRIER_ON_<year>` None: the app's refusal, foreseen by the footer and judged by its trace. Then the finding patched True in this process only, the press, the reads. A further rebuild, a second turn, and G4 At 30 → 27. Every put must be an app body or a locked sprocket. | **The coordinator's measurement**: proposes the finding True only if both presses and every read are clean | 1 min (measured) | 3.5 min (measured) |

**Why m3 is built as it is.** An earlier attempt (not kept) made two distance mates that agreed in value but not in
side. A plane-to-plane distance mate's side is AddMate5's Flip, which the app's `distance` leaves False, and no finding
says which side that is. The same attempt also set a distance in every mode in one `set_dimension_in` call, where the
app sets one configuration per call and a configuration never set reads 0 (`findings.VALUE_UNSET_READS_ZERO`). m3 now
holds the sprocket by one axial mate, reads the distance it leaves, and makes the contradiction as a second mate.

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

**refuse's bore step** rebuilds the assembly after Sun's Bore is typed and before the person's save. At `9dded70`
SolidWorks updated the assembly after the save, so the assembly was marked before the press and its mark check was
blind (W9A-RUN-2026-REVIEW finding 6). Any press that starts with a document already marked says so in the log; for
that document, frames, mates' codes, flags and entities and the part's globals are still compared. The press's trace
(W8's `nothing_changed_calls`) does not see an equation write that sets a part's global; the part's globals read
before and after every refused press cover it.

**SolidWorks 2026: all twelve sections, about 70 min** (the closing run's measured times).

**The phase's closing run on 2026** repeated all twelve sections in one session started for it, at `6f3d6fb` under the
current watch, with the again sections rerun at `6b9d8aa` after their checks were corrected; every section's last run
0 failed, and the window check's W8 stage 0 failed (`W9A-CLOSE-2026-REVIEW.md`, finding 9). The script changes since
(the carried step's quiet press, the tighter `stays_said`, the lightweight reset read) are for the next run of m3,
again and lightweight; `box` and `box-k3` are new and run on 2024 only by name.

**SolidWorks 2024's confirming set** (`--sections confirm`) follows *Rules carried over*: one full turning build with
its edits, plus the sections where the versions may differ. That is m3, setup, go, reducer, k3 and nocarrier. setup,
go, reducer and nocarrier ran 0 failed in 36 min (`sw2024/w9a-confirm-sw2024-20261117-2-*.log`). m3 stopped there at
What's Wrong (Found on SolidWorks, item 4); under the coordinator's ruling below, m3 and k3 now run on 2024 with
*the What's Wrong rule*:

- **The rule.** The script reads `swbuild.whats_wrong_shows_in_update(revision)` by `getattr` once a session, and the
  log's `rule` line says which rule is in force. Where it is True (2024), a #32770 box titled "What's Wrong" owned by
  SolidWorks' frame, during ANY job the script waits on, is logged as a fact: when it came, the call in progress, when
  it went. Under an app job (an Update or a Build) it is said "as the app's Update shows it"; under the script's own
  steps, which stand for what a person does in SolidWorks (activating a document, an explicit rebuild, a read, a
  save), "as SolidWorks shows it when a person does this". The confirming m3 at `0a60fd3` showed why: on 2024 the box
  also came up when the script's own assembly rebuild activated the assembly with the user's keyway in error, and the
  narrower rule called it the STOP. The job is waited for as usual. At its end the box must go within 60 s (`box` saw it
  stay 22 s; how long it took is logged) and SolidWorks' frame must be enabled. A box still up after that, a frame
  disabled, a What's Wrong not owned by the frame, or one W8 noted that the watch never read as owned by the frame,
  is the STOP. Where the helper is False, None or missing, What's Wrong during a job stays a STOP, as any dialog.
  Every other window is judged as before.
- **W8's helpers.** `end_copy`, `copy_built`, `keep_master`, `write_fixture`, `build_turning` and the closing
  `close_ours` wait with W8's own unwatched wait; under the rule each runs through `w8_step`, which looks for the box
  from a thread while it runs and makes the same end check after it. W8's watch is kept from calling the box its own
  FAIL or STOP, during any ruled job, by a wrapper on the set of boxes it treats as known (its file is not changed).
- **The window list after a step** (`windows_new`): under the rule, a What's Wrong that came and went is a fact, not a
  window left standing; one still up when the list is read is what counts. m3's two assembly-rebuild answers now say
  whether the box showed during the step, not "no window".
- **Every section checked for the pattern:** after anything of the user's is in error on 2024, every following job is
  under the rule: m3's later steps (the part's bore, the assembly rebuild, the quiet presses, the carried step, its
  refusal's reads, the save, the copy's end); k3's reads after its Update and its copy's end; refuse's two-body and
  all-at-once steps, where app mates read in error; `box` and `box-k3` keep their own log-only watch and are not
  under it.
- **Where the box is expected.** After m3's two Updates and k3's, where
  `WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_<year>` or `…_WITH_PART_FEATURE_IN_ERROR_ON_<year>` is True
  and the rule is in force, the section asserts that What's Wrong showed during the app's Update and went by itself:
  a fact a user will see, so the 2024 logs say it plainly, not a failure of the app. Only the app's Updates feed
  this assertion; a box under the script's own steps is a fact only. Elsewhere what the watch saw is said.
- **The gate.** m3's and k3's judgement of whether an Update goes ahead follows the app's own gate,
  `swbuild.assembly_rebuild_settled(revision)`, as it stands, so it stays right as the gate changes; the check that
  the three findings it names exist is kept.
- **The waits.** Every Update and Build is waited for 2400 s (`Desk9.update_solidworks`, `Desk9.build`). 2024's
  longest was go's value Update at 351 s, and `box`'s Update with modes took 306 s. The other jobs: read every mode
  1200 s, the user's work 900 s, a save 600 s, the user's turn 600 s, an explicit assembly rebuild 300 s (m3's on
  2024 took well under a minute), any other job 900 s.

- `setup` and `go` are the build with its edits.
- `m3` and `k3` are rebuilds that can raise a dialog there.
- `reducer` and `nocarrier` give `USER_MATE_PUT_NO_CARRIER_ON_2024`.
- `refuse` is not in the set, because S0 saw no difference between the versions in the reads it rests on. It runs on
  2024 by name (about 40 min); whether to run it there is the user's call. So does `lightweight` (about 14 min);
  2024 is the version said to open components lightweight, so it is the cheap one to add. The plan's *Done when*
  ("2024 confirms the assembly sections") reads broader than the rule, and the note follows the rule.
- setup, go, reducer and nocarrier have run (above). What remains is m3 in one fresh session and reducer,k3 in another
  (the command lines below).

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

rem SolidWorks 2026, after a fix: m3, k3 and lightweight again into the same RUN\out (re-archive RUN\snap at the
rem new commit first; --redo sets the old folders aside; m3 needs S0's master, k3 and lightweight find theirs)
python.exe RUN\snap\probe\w9a_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9a-sw2026-5.log ^
    --sections m3,k3,lightweight --redo ^
    --master C:\Users\M0obo\Documents\GearGeneratorProbe\w9-s0-20261116-045513\out\rangebox.master

rem the window check's W8 stage, SolidWorks 2026 only
python.exe RUN\snap\probe\workbook_window_check.py RUN\snap\src RUN\window --pid PID --only w8 --log RUN\w9a-window.log
```

**Re-running.**

- A section `RUN\out` already holds is skipped and said. `--redo` sets its folder aside (`<name>.prev-<time>`) and runs
  it again; for `setup` or `reducer` that also sets their master aside, and later sections then use the new one.
- Masters from another `<out>` are given by path: `--user-master`, `--reducer-master`.
- A section that needs a master that is neither given nor in `<out>` builds it first, and says so.

The JSON (`w9a-demo-<time>.json`) is written beside the log after every section. Its `proposal` holds:

- M3's readings, for the assembly and for an app part (`M3_app_part`: whether the Update went ahead and was expected
  to, the keyway named in the result and in the sentence, each separately, and G1's component code);
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

A section a STOP or a hung worker cuts is recorded as cut, not passed: its `failed` holds `cut: <the raise>`, and the
time line says CUT. Its time ends where a dialog was seen, so no wait behind the dialog is counted (the time after it
goes to `seconds_after_the_dialog_not_counted`). The done line counts every entry of the JSON's `stops`, a hung
worker included, so the log and the JSON agree. (At `9dded70` refuse wrote "0 failed" and 1932 s after the hang, and
the done line said 0 STOPs while the JSON held one: W9A-RUN-2026-REVIEW finding 5.)

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
   - Seen in `refuse`'s lightweight step at `9dded70`: `probe/results/w9a-demo-sw2026-20261116-2-m1-refuse-stopped-by-a-dialog.log` lines 354-359.
   - The app never saves (Update leaves everything unsaved; W9d is planned not to save the carried items). A W9d that
     saves, closes or saves-as an assembly holding the user's components must first resolve them, or must expect the
     box.
2. **Two user mates in error, and the assembly rebuild still returns True.** With UserFront and UserGap over-defined
   (codes 46 and 47), the assembly rebuild by the app's train route returned True, GetWhatsWrongCount read 3, and no
   window came up (`probe/results/w9a-demo-sw2026-20261116-1-m3-setup-go.log` lines 48-51). With one user feature in error in a part, it returned False,
   GetWhatsWrongCount 1, no window (lines 88-91). These are the findings `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2026`,
   `ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2026` and `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2026`. "Show errors
   every rebuild" was not read in those runs; m3 now reads it.
3. **SolidWorks reports every instance of a part lightweight when one is set.** In the closing run's `lightweight`
   (`probe/results/w9a-close-sw2026-20261116-1-m3-reducer-k3-setup-lightweight.log`, lines 936-938), after
   `SetSuppression2(1)` on Sprocket-1 alone, the script's own `GetSuppression2` read 1 on all four instances of
   Sprocket.SLDPRT, and 2 on Housing-1. The app's inventory read the same (line 969), and the refusal named exactly
   the three carried ones (line 996). So the app reads what SolidWorks reports. It is not shown that SolidWorks made
   each instance lightweight: both reads are the same member. Whether resolving one instance is reported as resolving
   the others is what the section now logs (at `6f3d6fb` the reset set each back one by one). A fact for W9d, which
   resolves components before it saves.
4. **SolidWorks 2024 opens What's Wrong inside the app's value Update with only the user's mates in error.** With
   "show errors every rebuild" on, UserFront and UserGap over-defined (codes 51), and the script's own assembly
   rebuild raising no window, the app's value Update raised "What's Wrong" (Show errors, Show warnings, "Display
   What's Wrong during rebuild", FeatureXpert, Close, Help) while the worker was in `GetNextSubFeature`
   (`probe/results/sw2024/w9a-confirm-sw2024-20261117-1-m3-stopped-by-whats-wrong.log`, lines 37, 53, 88-91). 2026
   opened nothing in the same Updates. The watch stopped on sight, so which call raised it, whether it is modal and
   what had been written are not known: `box` and `box-k3` below measured them, and the coordinator ruled on them.

## `box` and `box-k3`: SolidWorks 2024's What's Wrong box, measured

**What they read** on SolidWorks 2024 (32.5.0) at `b985cab`, each in a fresh session, "show errors every rebuild" on
(`probe/results/sw2024/w9a-box-sw2024-20261117-1-box.log` line 39):

| | `box` (two user mates in error, value Update with modes) | `box-k3` (the Update rebuilds the user's keyway into error, no modes) |
|---|---|---|
| the box came | 97.45 s into the press, the worker in `ActivateDoc3` (box:103) | 17.57 s in, in `ActivateDoc3` (k3:597) |
| what it is | a #32770 popup owned by SolidWorks' frame, not topmost; the frame enabled (box:103) | the same (k3:597) |
| a read with it up | the open documents on a second connection, answered in 0.5 s (box:104) | the same, 0.5 s (k3:598) |
| it went | by itself at 120.08 s, last seen 119.57 s, the worker then in `ShowConfiguration2` (box:110) | by itself at 22.59 s (k3:603) |
| the job | returned at 306.49 s, `ok` True (box:141); the calls grew after the box came and after it went (box:142) | returned at 22.59 s, stopped as failed, the findings being None then; its sentence names the keyway as the user's, newly in error, with the cell to retype (k3:612) |
| after it | the app's bodies 6.6e-10 from their frames on record, the user's components not moved, the user's mates as before (box:145) | the app's bodies at their frames, nothing of the user's moved (k3:616) |
| written | Sun's Backlash 0.4, Sun's part and the assembly marked (box:143) | G1's Bore 14, G1's part marked (k3:614) |

(box: `probe/results/sw2024/w9a-box-sw2024-20261117-1-box.log`; k3: `probe/results/sw2024/w9a-box-sw2024-20261117-2-reducer-box-k3.log`.) Nothing closed the box; no frame title is in either log.

**The coordinator's ruling.** On SolidWorks 2024 the box is left alone: the app changes no setting and does not
refuse for it. It opens during the app's Update when the user's work is in error, blocks nothing, and goes by itself.
Package A sets the findings (`WHATS_WRONG_IN_UPDATE_BLOCKS_ON_<year>` False on both versions;
`WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_<year>` and `…_WITH_PART_FEATURE_IN_ERROR_ON_<year>` True on
2024, False on 2026; `ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2024` and
`WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2024` False) and the helper `swbuild.whats_wrong_shows_in_update`. The
confirming m3 and k3 run under *the What's Wrong rule* above.

Two sections, run by name only (never in `all` or `confirm`), so the user decides on facts what the app does on 2024
(W9A-CLOSE-2026-REVIEW, *The 2024 fact and the options*). Neither sets a SolidWorks setting, answers a box, or closes
or saves anything once a box has been seen; neither proposes a finding's value.

- **`box`:** m3's set-up to just before its first value Update: the sprocket and housing, the clean baseline, UserGap
  made over-defining, the quiet press, Sun's Backlash 0.4 typed. Then the app's Update is pressed.
- **`box-k3`:** k3's set-up on the 12 : 1: the user's keyway in G1's part, the quiet press, G1's Bore 8 → 14 typed.
  Then the app's Update, which rebuilds the keyway into error; with 2024's findings None it is expected to stop as
  failed.

**How the press is watched.** The press is waited for up to `--box-wait` seconds (1800 by default) under a watch that
only logs (`BOX`). The first `box` run (`73805d2`, its log not committed) waited 300 s, which was too short to see the
Update finish on 2024, where its quiet press alone took 131 s. A second
connection to the same SolidWorks is made before the press, and every read is a raw call (`W._RAW_CALL`, so W8's "call
in progress" is never moved by the script's own reads). Recorded, as read:

- before the press: Sun's Backlash (or G1's Bore) as its Equation Manager holds it, each copy document's save flag,
  "show errors every rebuild" (toggle 77, read, never set), and SolidWorks' frame (`IsWindowEnabled`);
- when a box is first seen: the seconds into the press; the call the worker is in (W8's `CALLS["now"]`) and the last
  traced call; whether SolidWorks' frame is enabled (a disabled frame means a modal box); the box's class, title,
  texts, style, extended style, owner and whether the owner is the frame;
- with the box up: whether a harmless raw read (the open documents) answers on the second connection, and how fast
  (20 s at most);
- every 10 s, when either has changed, the call in progress and the number of calls made and traced, with the time:
  enough to tell a slow job from a stuck one;
- when the box was last seen and, when it went, the call in progress then (nothing here closes it); any further box;
- whether the job returned, after how long, and whether the box was still up when it did; its result and status
  sentence if it did;
- whether the calls made grew after the box was seen, and after it went;
- at the end: the call the worker is in, the frame enabled or not, and the boxes still up;
- what was written: the same raw reads after the press, against before (on the main worker if its job returned, else
  on the second connection if it answered), and toggle 77 again;
- if the job returned with no box up, the reads the other sections make, in the active mode with nothing shown,
  against the same read before the press: every app body at its frame on record, the user's components' frames
  (`box`: Sprocket-1 and Housing-1), and each user mate's code, suppression and flags (`box`: UserAxis, UserFront,
  UserGap). That is what tells whether an Update that ran through the box did its work.

SolidWorks' frame, and any window's owner, are logged by class, and their title only as present or not and as holding
the document's name or not: a frame's title can hold the licence edition, which this repo keeps out of its logs (S0's
P0 lists windows by class only for that reason). A box's own title ("What's Wrong") and texts are SolidWorks' words
and are logged; so is any new #32770's title in the other sections' window lists, while any other new window's title
is written only as `<titled>`.

A box seen ends the run by design (`BoxSeen`, not a failure): the worker is marked hung so nothing more is asked of
SolidWorks, and the session is left as it stands for the coordinator to end. W8's own watch keeps its rule (a box
during a configuration call is its FAIL and STOP); what it logged during the press is recorded beside the facts. If the
job does not return in the wait, the worker is left alone and the section says so. With no box, the section ends as any
copy section does.

**Command lines, SolidWorks 2024: the confirming m3 and k3** under the What's Wrong rule, each in a fresh session,
with `RUN\snap` archived at a commit holding package A's 2024 findings and helper:

```
python.exe RUN\snap\probe\w9a_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9a-confirm-sw2024-3-m3.log ^
    --sections m3 ^
    --master C:\Users\M0obo\Documents\GearGeneratorProbe\w9-s0-sw2024-20261116-064725\out\rangebox.master

python.exe RUN\snap\probe\w9a_demonstration.py RUN\snap\src RUN\out --pid PID2 --log RUN\w9a-confirm-sw2024-4-reducer-k3.log ^
    --sections reducer,k3
```

In a `RUN\out` that already holds `reducer.master`, `reducer` is skipped and the master used. `--redo` runs every named
section again, `reducer` included, so add it only when that is wanted.

**Command lines, SolidWorks 2024: `box` and `box-k3`.** Each in a fresh session, as the last thing asked of it; `RUN`
holds `snap\` and `out\`.

```
rem box: first, alone in a fresh session
python.exe RUN\snap\probe\w9a_demonstration.py RUN\snap\src RUN\out --pid PID --log RUN\w9a-box-sw2024-1.log ^
    --sections box --box-wait 1800 ^
    --master C:\Users\M0obo\Documents\GearGeneratorProbe\w9-s0-sw2024-20261116-064725\out\rangebox.master

rem box-k3: in another fresh session, with reducer before it (skipped if RUN\out already holds reducer.master)
python.exe RUN\snap\probe\w9a_demonstration.py RUN\snap\src RUN\out --pid PID2 --log RUN\w9a-box-sw2024-2.log ^
    --sections reducer,box-k3 --box-wait 1800
```

**What each answer would mean for the three options.**

- **Option 1, refuse first** (on 2024, when something of the user's is in error, before any write):
  - `box` with a box: option 1 covers it, since the check phase already reads the two mates in error.
  - `box-k3` with a box: option 1 alone cannot cover K3 on 2024, since the keyway is put in error by the Update's own
    write; it would need option 2 or 3 as well.
  - `box-k3` with no box: option 1 covers 2024 for what the check phase sees, and k3's stop stays a stop.
- **Option 2, the app turns toggle 77 off for its job:**
  - A box that does not depend on the toggle cannot be avoided this way. These sections do not set 77, so they cannot
    show that the box obeys it. They show only whether there is a box to avoid, at which call, and what it costs. If
    a box is seen, option 2 still needs its own measurement with the setting turned off and set back.
  - The box raised at a rebuild call: option 2 is a candidate there. Raised at a read (`GetNextSubFeature`, as on the
    first sighting) after the rebuild had returned: the toggle may still govern it, but that needs the same test.
- **Option 3, leave the box to the user:**
  - The job returns, with the box up or gone of itself, the frame enabled, a read answering and the calls growing
    after the box came: the box does not block. Option 3 then needs the after-press reads clean (the app bodies at
    their frames, the user's components and mates as they were) and the result as on 2026 (`ok`, puts, sentence).
  - The calls stop growing while the box stands, or the frame is disabled, or the read does not answer: the box
    blocks. A person must close it during the job, and the app must say so while it waits. Whether the job then
    completes cleanly is another measurement.
  - The calls keep growing but the job does not return in the wait: a slow job, not a blocked one; the wait is
    raised and the section run again.
- **In every case,** what was written before the box (Sun's Backlash, the save flags) tells whether a refusal after
  the box would leave the user's documents changed but unsaved.

## What the script cannot show, and what it leans on

**What it cannot show:**

- **M1 in full.** On 2026 the app's `mate_info` and inventory read, marking nothing: coincident (axis to axis),
  distance, angle and lock mates, a user–user gear mate, and a distance mate suppressed in the active mode (it read
  whole, on in N and L); joins user–user, user–layout and user–gear (setup, m1; `refuse` adds a coincident on Sun's
  axis). Not read: concentric, width, limit and path mates, a user gear mate on an app gear, and a leaf inside a user's
  sub-assembly. These move to S5 in W9c's sessions, which reads every mate kind (the coordinator records it in the
  plan); until then the app refuses, when anything is put, a user mate it cannot read wholly.
- **Frames after m3's gone-ahead Updates.** m3 does not read the bodies' frames after its two Updates; it rests on
  the app's own post-check, which would have made `ok` False (W9A-CLOSE-2026-REVIEW finding 10). go reads them.
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
