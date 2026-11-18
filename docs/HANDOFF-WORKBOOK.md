# Handoff: the workbook import (branch `workbook`)

Rewritten the night of 2026-11-13, when work on the Windows host was wound down so it can carry on from
another machine. **`docs/PLAN-WORKBOOK.md` is the plan and the authority**; this note only says where things
stand within it. The working papers of the session (plans, reviews, reports) are in `docs/notes-workbook/`
and are named below where they matter. Where one of them names a script such as `w4x_….py` or `w5r_….py`,
that was a throwaway repro in a temp folder and was not kept; the fixes' regression tests replace them.

**Updated 2026-11-14**, on the Windows host again (a WSL clone, with SolidWorks 2026 and 2024 both started and
exited by the agents): W4 was closed and W5 begun. The dated paragraphs below say what changed; the user's
answers of that day and the rulings that follow from them are in `notes-workbook/W5-DECISIONS.md`.

**Updated 2026-11-15 (later that day), from a second Windows host** (`DESKTOP-QJTI7HF`, a WSL clone; its SolidWorks
2026 is SP0, revision **34.0.0**, where W5 to W7 and the W8 spike ran on the other machine at 34.1.1): W8 was picked
up again at the user's word. *W8 picked up* under "W8 in detail" says where it stands. The run folders of W5 to W7
(`w6-full-…`, `w7-full-…`) are on the other machine, not this one.

**Updated 2026-11-15, evening: the work moves to another device again.** Every branch is on `origin` and
`workbook` there is the whole state; nothing is uncommitted. W8 is paused, not closed: *Paused at the user's
word* and *Left* under "W8 in detail" say what remains. What stays behind on the second host and has to be made
again elsewhere:

- **The 2024-built `s1.master`** (`…\w8-sw2024-20261115\out`). `s2` on SolidWorks 2024 starts from it, so on
  another device run `s1` on 2024 again first. The committed result files under `probe/results/` stand as they
  are; no run folder is needed to read them.
- **The preview exe** of `29e6c34` (`dist/` is not tracked). Build one with `build.bat` from a copy on `C:`.
- **The sessions' own notes** (not in the repo). What they held is in *Rules carried over* below, plus these three:
  a run that will tie SolidWorks up says so to the user first, with how long; a build always names its output
  folder (a blank Output folder cell means the folder the app last remembered, which may be another project's);
  and on a host whose Linux venv has no tkinter the two tests named under "W8 in detail" fail for that alone.

The rule "no agent starts SolidWorks on the host until the user says so" was said of the second host. On another
device ask once before the first run.

**Updated 2026-11-15/16, night, on a third device** (a WSL clone; it is in fact the machine W5 to W7 ran on:
SolidWorks 2026 revision **34.1.1**, SolidWorks 2024 32.5.0; its `GearGeneratorProbe` folder still holds
`w6-full-20261114-210827` and `w7-full-20261115-000138`). **W8 is closed but for three things** (*W8 in detail*,
*How W8 closed*), and **W9 is planned and approved** (issue #1, below). What ran here, in order, each run from a `git
archive` snapshot in its run folder under `C:\Users\M0obo\Documents\GearGeneratorProbe\`, each SolidWorks started
for the run and exited after:

- `s7` case 8 alone on 2026 34.1.1, after `s1` built there (`w8-s7c8-sw2026-20261115-220518`; `9bd3a58`, the
  findings' comments and pins `0e7f203`, reviewed `867d1af`, its points `5946fdf`);
- the rest of 2024's confirming build, `s1`, `s3`, the window stage, `s2` (`w8-sw2024-20261115-223821`; `233e03d`,
  `b6bb186`, `c3ed9b6`, `eae38c9`; the handoff `c583f48`; reviewed `fd44e7c`, `W8-REVIEW-SW2024-CONFIRM.md`);
- the closing run on 2026 34.1.1 from one snapshot of `c583f48` (`w8-close-sw2026-20261116-001758`; `c351b1f`,
  `8fd13c9`, `c2eed05`, `aff9bfe`, `fb85bcc`; reviewed `ec14e4f`, `W8-REVIEW-CLOSING-RUN.md`).

The first two runs' snapshots had no `SNAPSHOT_COMMIT` file beside them, so the logs of `9bd3a58`, `233e03d`,
`b6bb186`, `c3ed9b6` and `eae38c9` do not name their snapshot in their heads; their commit messages do, and no log line
can tell `0e7f203` from the source just before it (its changes after `ce775a6` were comments). The closing run's
logs name `c583f48`. Write the file with every snapshot from now on. The window check's log never prints SolidWorks'
revision: its 2024 run had a session of its own (PID 18160 in the log; that it was SolidWorks 2024 32.5.0 rests on
`c3ed9b6`'s message), its closing run a fresh one (PID 16424; SolidWorks 2026 34.1.1 by `fb85bcc`'s message). A
later change to the window check could log the revision as the assembly check does; it would be reviewed as code. The user was told how long each run would tie SolidWorks
up and gave the word for all of them. Before the first, the user's own SolidWorks 2024 session had documents open;
at the user's instruction they were saved and closed and that session exited. That session did not show in the
running object table as an application, only its documents; every SolidWorks an agent started here did.

**GitHub issue #1** (opened by the user 2026-11-16): sleeves built with no hub and no check that one can reach its
dog, a neutral with no running clearance, no relief bore in a sleeve, and Update unable to add a part. The user's
words on the last: once they have edited parts or added their own in the built assembly they cannot use the app any
more, for fear of it overwriting their work. Its plan is `notes-workbook/ISSUE-1-PLAN.md`, phase **W9**, stages W9a
to W9d, reviewed in `ISSUE-1-PLAN-REVIEW.md` and revised to its second review (`ISSUE-1-PLAN-REVIEW-2.md`). The
user's answers of 2026-11-16: every stage approved; a value the app owns that the user changed in SolidWorks makes
Update stop and name it; Build again… carries the user's components and remakes their mates; the hub is built by the
app from a row. **So W8 is not the last phase** (PLAN-WORKBOOK §3.4 and §6 carry dated notes). The W8 readings the
issue overturns stay as W8 built them until W9 changes them, and are marked *under issue #1* below: J1's "no hub",
J22's bridging warning (it fires only when `length > gap`), and ruling 9.16 (a gear mate of a gearbox with modes is
not made again).

**2026-11-18, morning: W9 is closed (read this first; the small-hours paragraph after it is superseded where the two
differ).** Written at head `06d818f` on branch `w9d`. W9c and W9d are closed on SolidWorks 2026 and 2024, and with
them W9 (issue #1's plan, `notes-workbook/ISSUE-1-PLAN.md`): items 10 (W9c) and 11 (W9d) of *Where W9 stands* give
their accounts. W9d's confirming run on SolidWorks 2024 32.5.0 passed (`69b6354`, from a snapshot of `5aca9c1`: every
section 0 FAIL, no STOP, no What's Wrong box, the script unchanged), was reviewed (`e51de95`), and its six 2024
findings were set and pinned (`e7a3577`); the contract's §8 followed (`d8a12f6`) and the Build again? question for a
record with no version on it was fixed by ruling (`06d818f`). A fault in W9d's planet-copy lookup, found by the
printed-gears work, was assessed (`7f91037`), fixed (`d496cfd`) and re-checked (`12cf15d`). W9c's remake-m3 ran on
SolidWorks 2026 (`5aca9c1`) with its finding re-based (`ea4efec`) and the notes (`7f110f1`). The whole suite at
`06d818f`, run by the coordinator: 4134 passed, 1 skipped, 1 failed (the known font-width test). **The coordinator
merges `w9d` into `workbook` after this commit (done: `4d72c36`). GitHub issue #1 is left open for the user to close.**
- *What W9 leaves open* (the lists are in items 8, 10 and 11, from the last sections of `W9C-RUNS-REVIEW.md` and
  `W9D-DEMONSTRATION-REVIEW.md`):
  - **gates still None, and what the app says.** W9a's: route (c1) on a held gear, a fixed gear, a sub-assembly, a
    no-carrier train with modes, each refused with a sentence naming it (item 8). W9c's:
    `UPDATE_MAKES_A_NEW_COUPLING`, `UPDATE_SUPPRESSES_THE_RELIEF` and `EXTERNAL_REFERENCES_READ` on both versions; an
    Update that needs one refuses before any write, naming the step and its finding, and a removal refuses while any
    of the user's components is present (item 10). W9d's: `CARRY_INSERTS_A_SUBASSEMBLY`, `CARRY_REMAKES_ON_A_LEAF`,
    `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`, `ORIGIN_ENTITY_READ` and `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` on both;
    Build again… names what each covers and leaves it in the old assembly, a pattern instance being carried as a
    component of its own (item 11);
  - **shown on the fake only:** W9c's plain gear added and removal on a gearbox with modes; W9d's fallbacks other than
    the tie, the per-mode fix, the planet-copy path and the rest of item 11's list;
  - **known limits measured on SolidWorks 2024:** a carrying Build again… takes SolidWorks to about 11 GB private and
    adds about 16 to 20 minutes; an Update of a gearbox with modes grows it by 3.3 to 4 GB on a freshly opened copy,
    and W9c's `modes` run reached 14 GB; each is given back when the assembly closes, and the app does not watch
    memory. The What's Wrong box raised after a stopped Update stays until it is closed, and the app says so
    (`WHATS_WRONG_STAYS_WITHOUT_A_REBUILD_ON_2024`). The face prefilter narrows less on 2024, so the carry's
    200-candidate cap comes sooner on a many-toothed gear's root or fillet;
  - **other known limits:** an unmarked part with an app feature in error lets the press write and offer saving (item
    10); the edge prefilter's cost outside the cap, a should-fix (item 11);
  - **for the user:** the questions under *Questions waiting for the user*, among them the rulings of 2026-11-18 (10
    to 14, 17, 18), and the person's steps of W8 (question 5).
- *Printed gears* (the phase table's last row; updated after the merge of `w9d` into `workbook` at `4d72c36`): **stage
  F1 of `docs/PLAN-PRINTED.md` is closed on branch `printed`** (worktree `~/SW-Gear-Generater-printed`), **and not
  merged into `workbook`**: that merge changes what the app does for the user, so it waits for the user's word. F1-0,
  packages A, B and C, their review and its should-fixes; `w9d` and then `workbook` merged into `printed` (`91f6a6f`,
  `138d646`); the SolidWorks demonstration `probe/f1_demonstration.py` written, reviewed (`cf40e4a`) and run clean on
  SolidWorks 2026 34.1.1 and 2024 32.5.0 from one snapshot of `c1c9046` each (`5e2f386`: 2026 110 ok, 2024 56 and 53
  ok, 0 failed, no STOP, no What's Wrong box), the runs reviewed (`0e7000d`): F1 is done by its Done-when. The suite
  on `printed` at `138d646`: 4747 passed, 1 skipped, 1 failed (the known font-width test). The record of that work is
  `docs/notes-printed/` on branch `printed` (read with `git show printed:<path>`):
  - `F1-0.md`: F1-0's hand-over (the pins of §2.7, the interface step, what each package must keep) and the
    coordinator's twelve rulings on its review;
  - `F1-0-REVIEW.md`: the review of F1-0;
  - `F1-INTERFACES.md`: the interface as F1-0 built it, every name with its signature and the words of every new
    sentence;
  - `F1-PACKAGE-A.md`, `F1-PACKAGE-B.md`, `F1-PACKAGE-C.md`: each package's hand-back (A the printed gear maths, B the
    records and the workbook, C what the user sees), with its choices and the rulings on them;
  - `F1-REVIEW.md`: the independent review of packages A, B and C (`be5ae7a`);
  - `F1-DEMONSTRATION.md`: the SolidWorks demonstration's sections, masters, commands and STOPs, with the runs'
    write-up;
  - `F1-DEMONSTRATION-REVIEW.md`: the review of the script before its first run; `F1-DEMONSTRATION-RUNS-REVIEW.md`:
    the review of the two runs.
  - *What F1 leaves open:* the design boards' PNG renders are not redone (the renderer runs the Mac's Chrome; they
    have been stale since W9a); the span over k teeth is moved to F2's first step; nothing of F1 is merged into
    `workbook`; the runs review's should-fixes are to documents only; and the user's word on the rulings of question
    19.
  - *Next by the plan, F2* (`docs/PLAN-PRINTED.md` §3): the span over k teeth on Linux (§3.0); a probe of saving a
    part as STEP, a call the app has never made, on both versions (§3.1); Export STEP on the form and in the Workbook
    window; then the user prints and measures (§3.2), which only the user can do. The coordinator was having F2 made
    ready to execute when this was written.
  - GitHub issue #1 is still open, for the user to close.

**2026-11-18, small hours to morning, on this laptop (superseded by the morning paragraph above where they differ;
the paragraph "W9c at the session's close, 2026-11-17 midday" after it is superseded by this one and kept as
history).** Written at head `7f110f1` on branch
`w9d`. The record is the commit log and `notes-workbook/W9C-*.md` and `W9D-*.md`; this paragraph and items 10 and 11
of *Where W9 stands* only map them.
- *Where the work is.* Every W9 commit since 2026-11-17 midday is on branch `w9d`. `workbook` was merged into `w9d`
  three times (`5e783a6`; `7ce641e`, reviewed in `notes-workbook/W9D-MERGE-REVIEW.md`, `2c306bc`; and `f7c2f0d`, which
  brought W9c's 2024 confirming run `06d5141`). `workbook` has had nothing since `06d5141`; W9 goes back into it when
  W9 closes, which it has not. The printed-gears work is on branch `printed`, cut from `w9d` at `f3c4873` and checked
  out in a second worktree, `~/SW-Gear-Generater-printed`, beside this checkout (`~/SW-Gear-Generater`, on `w9d`).
- *Where it ran.* On 2026-11-17, afternoon and evening, on the second host (SolidWorks 2026 34.0.0; SolidWorks 2024
  32.5.0 by `06d5141`'s message). From about 03:00 on 2026-11-18 on this laptop, the third device of 2026-11-15/16
  (SolidWorks 2026 34.1.1, SolidWorks 2024 32.5.0), with the user asleep, having said to carry on past W9 down the
  plans with Opus subagents and a review of each step (the head of `docs/PLAN-PRINTED.md` records the word). Each
  SolidWorks run here was, by its note, a fresh session started for the run with no other SolidWorks running, and
  exited after.
- *W9c is closed on SolidWorks 2026 and 2024* (item 10): its five gates True on both versions, remake's M3 measured to
  step 3 on both, the What's Wrong sentences and their finding. Owed: the whole suite at the commit that closes it.
- *W9d is shown on SolidWorks 2026 and its findings are set there* (item 11); on 2024 its probes are run and their
  fourteen reads set, and its demonstration was running when this was written. Its result goes in the marked paragraph
  at the end of item 11.
- *Printed gears* (the phase table's last row): the plan revised against W9's code and checked three more times,
  `printed` cut early, F1-0 in hand there.
- *The coordinator's rulings of 2026-11-18*, each the user's to overrule, are items 10 to 14 of *Questions waiting for
  the user*. What the night taught about working is at the end of *Rules carried over*.
- *When this was written* SolidWorks 2024 was running W9d's demonstration, and other agents were committing in both
  checkouts. The coordinator pushes.

**W9c at the session's close, 2026-11-17 midday (superseded by the paragraph of 2026-11-18 above; kept as it was written).** Nothing is
running: no SolidWorks, no Excel, no agent. Head is pushed. W9c is written, reviewed and shown on SolidWorks 2026,
but **not closed**: its gate findings are still None on both versions and the 2024 confirming run has not been made.
- *Shown on 2026 (app code `887916b`), reviewed in `notes-workbook/W9C-RUNS-REVIEW.md` (`6e023e7`):* `fixed` (the
  plan's Done-when: Hub built, inserted and mated, bands given in place, every user item kept), `modes`, `bands-off`
  (run 5, `probe/results/w9c-demo-sw2026-20261117-5-…log`), `remove` (run 4), `remake` with 28/14/56 (run 6). The
  review allows `UPDATE_INSERTS_A_GEAR`, `UPDATE_BANDS_IN_PLACE`, `UPDATE_ADDS_A_MODE`, `UPDATE_REMOVES_A_MODE` and
  `UPDATE_MAKES_MATES_WITH_MODES` True for 2026 once its must-fix is in (it is, below); `UPDATE_MAKES_A_NEW_COUPLING`,
  `UPDATE_SUPPRESSES_THE_RELIEF` and `EXTERNAL_REFERENCES_READ` stay None. **None is set yet.**
- *App code changed after those runs* (so the final evidence must be run again): the footer's false refusal after a
  mode is added and the save advice after a stop in a part left in error (B: `0eb0768`, `d432846`, `5c02c6a`,
  `ff98d5a`; the record gains `UserWorkEntry.modes` and `LinkRecord.unsaved_in_error`, schema still 9); **the ring
  fault** (an older one the demonstration found: a ring set one tooth down, 55 to 54, lands the new flank start where
  the Tooth Space sketch's short line `Li+` ended, SolidWorks solves it to the far side, code 72, and the part does
  not recover) fixed by routing through a safe tooth count (A: `63bbc33`, `c997e85`; `gears/landing.py`,
  `swbuild.update_variables`, threshold 0.2 of the line's length). The fixes were reviewed in
  `notes-workbook/W9C-FIXES-REVIEW.md` (`8407159`); its three must-fixes and S1 to S7 are answered in `c997e85` and
  `ff98d5a`, which **no reviewer has read yet** and **no SolidWorks run has exercised**.
- *The landing fix as first written (`63bbc33`) measured clean on 2026* (run 7, stopped by the coordinator after
  `landing`: `…-7-landing-measured-then-stopped.log` and `w9c-demo-20261117-114848.json`; the commit message of
  `d88096c` wrongly says no JSON was written): routed cases clean to the from-scratch volume; set straight, a ring
  fails at 0.038 and is clean at 0.144 and 0.173, an external gear is clean at 0.100 and 0.128.
- *Next, in order:* (1) a whole run on SolidWorks 2026 from head, `landing,fixed,modes,remove,remake,bands-off,m4,
  w9b-part` (about 2 h 20; the script is `probe/w9c_demonstration.py` at `96a0835`, its note
  `notes-workbook/W9C-DEMONSTRATION.md` has the command; the new `landing` cases and `remake`'s press-again step have
  never run on SolidWorks, so expect script faults first); (2) the same on 2024 (about 4 h); (3) one independent
  review of both runs and of `c997e85`/`ff98d5a` (addendum to `W9C-RUNS-REVIEW.md`); (4) set the findings the review
  allows, per version, in `findings.py` with `tests/test_findings.py` pinned to the committed logs; (5) the whole
  suite (last whole run, at `0eb0768`: the one known font-width failure, 3786 passed); (6) rewrite item 10 and the
  phase table, close W9c; then W9d.
- *One 2024 run and one 2026 run were stopped by the coordinator, not by a fault:* a 2024 whole run 21 minutes in
  and 2026's run 7 during `fixed`, both because fixes landed after their snapshots.
- *For the user, defaults standing:* an Update that adds a gear into one of their components adds it and names the
  interference in red afterwards (the footer before the press is silent); a removal refuses while any of their
  components is present, until the in-context-reference read (M4) is measured with a part made by hand; plain gear
  added and removal on a gearbox with modes are measured on the fake only; the sketch itself is not changed (a
  construction that removes the ambiguity for new builds is described in A's hand-back, unmeasured); the earlier
  open questions in this file still stand.

**Where W9 stands (resumed on the user's word, 2026-11-16 afternoon).** **W9a is closed (2026-11-17, early
morning):** measured, written, reviewed and shown on SolidWorks 2026 and 2024. W9b is closed on both versions (item 9); W9c and W9d are closed on both versions, and with them W9 (items 10 and 11, 2026-11-18). How W9a went, in order, and what it leaves open:

1. **S0's readings** are in `notes-workbook/W9-S0.md`, from `probe/w9_user_work_check.py` on the issue's RangeBox
   (`tests/workbook_fixtures.range_box`). In short: when Update puts a gear back to its built frame, a component of
   the user's locked to that gear is left where the drive took it, and the lock takes the new offset with no error,
   whether the user's mate is left on or suppressed around the put (the plan's routes (a) and (b)). The coordinator
   ruled a third route, **(c)**: the app puts the user's locked component by its gear's own rigid motion in the same
   step. **The user accepted route (c) on 2026-11-16.** It held on SolidWorks 2026 (466 checks, 0 failed) and on 2024
   in cases A, B, E and D.
2. **Case C2 on SolidWorks 2024 is read** (run 4, `probe/results/sw2024/w9-s0-c2-sw2024-20261116-155327.log`, 0
   failed, the same as 2026). Run 3 had lost its session there 30 s after the laptop's lid closed into Modern Standby
   (Windows' event log), not through the script. **On this device a closed lid, or the display's idle timeout, puts
   the whole machine into standby and freezes a run.** The S0 script now asks Windows to stay awake while it runs and
   writes its JSON after every case (`d086705`); no other script asks Windows to stay awake, so give the next
   demonstration script that request, and its results written as it goes, before its first long run. The user raised the plugged-in timeouts
   themselves on 2026-11-16 (screen 30 min, no sleep); a closed lid still sleeps the machine.
3. **S0 is reviewed** (`notes-workbook/W9-S0-REVIEW.md`, `2ded80a`), with W8's close documents. Its four must-fix
   points are taken: the plan names route (c) (`1cc0bf6`), the note and W8's documents are corrected (`1a6370a`), and
   the findings are set and pinned (`ba06c4f`, and 2024's per-mode tie reading with run 4): `USER_MATE_PUT_ROUTE`
   (a user's lock that is on in the mode put, and nothing else), `USER_TIE_READ`, `USER_TIE_RULE`,
   `USER_TIE_READ_PER_MODE_ON_2026` / `_2024`, `WHATS_WRONG_OPENS_ON_PART_REBUILD`. The coordinator's ruling that every
   other kind of user mate on a put gear refuses until measured is question 9 under *Questions waiting for the user*.
   The review's notes N1 to N7 are not taken; the taking of the points and the script's fix were checked by the
   coordinator, not by a second reviewer, and are read with package A's review.
4. **W9a's packages A and B are written, reviewed, fixed and re-checked** (2026-11-16 evening), against the fake
   only. Package A, the worker: `e5e8ee1` to `381eda7`, reviewed in `notes-workbook/W9A-REVIEW-A.md` (`51b398b`), fixed
   (`5c5043e` to `66cbb77`), re-checked (`e9b2ebe`), and its re-check's points N1 to N4 and N6 fixed (`f2feac0`,
   `5610795`; checked by the coordinator and package B's reviewer in passing, not re-reviewed). Package B, the window
   and the record's schema 7: `e3cb13d` to `dac5c7e`, reviewed in `notes-workbook/W9A-REVIEW-B.md` (`6056d71`), fixed
   (`2c59e9c`, `c74986a`, `dc7b4e1`), re-checked (`4dff5f2`). Their contracts are `notes-workbook/W9A-INTERFACES.md`
   and `W9A-PACKAGE-B.md`. Linux suite at `dc7b4e1`: 1 failed (the known font-width test), 3424 passed, 1 skipped;
   Windows window tests 165 passed, 1 skipped. **Rulings made on the way, the user told of each:** route (c1) runs
   only on a train with a carrier until each other branch is measured (`USER_MATE_PUT_{NO_CARRIER,HELD_GEAR,
   FIXED_GEAR,SUBASSEMBLY}_ON_<year>`, all `None`, each refusing with a sentence); a user mate SolidWorks will not
   describe refuses when anything is put; K11 holds for a document that stayed open since an unsaved Update, and only
   one loaded from its file since falls back to W8's set-back; Build again… always says what of the user's stays
   behind; the record keeps a user component's name and kind, never its path. **Open, for one small fix round after
   the demonstration:** the re-check's R1 (after a refusal over a value typed in SolidWorks, any workbook change
   turns the footer green though the value still differs), R2 and R3 (two sentences); `ValueEdit.unsaved` stays in
   the record.
5. **W9a's demonstration has run on SolidWorks 2026, twice over, and its closing run there is clean** (2026-11-16
   night into 11-17). The script is `probe/w9a_demonstration.py` (sections that run alone; note
   `notes-workbook/W9A-DEMONSTRATION.md`; reviewed before its first run in `W9A-DEMONSTRATION-REVIEW.md`). First run:
   `probe/results/w9a-demo-sw2026-20261116-*.log`, reviewed in `notes-workbook/W9A-RUN-2026-REVIEW.md` (`6700505`):
   everything 0 failed but k3, which found that an assembly's rebuild returns False when a part has a feature in
   error and the Update then stopped without naming the user's keyway. Fixed in the worker (`ebcd23d`) and in
   `ui_text` (`596bcb1`), with package B's leftovers (`84b9303`); the rulings are in the plan's last section
   (`3e7307a`). **Closing run on 2026, all twelve sections 0 failed, and the window check's W8 stage with K12 0
   failed** (`probe/results/w9a-close-sw2026-2026111*.log`, `w9a-window-sw2026-20261117.log`; `19651ee`), reviewed
   with the fixes in `notes-workbook/W9A-CLOSE-2026-REVIEW.md` (`2a8f9d1`): *Done when* is met on 2026 but for its
   should-fix points. Findings set for 2026 and pinned: `USER_MATE_PUT_NO_CARRIER_ON_2026` True (the 12 : 1, no
   modes; `USER_MATE_PUT_NO_CARRIER_MODES_ON_*` stays None), `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2026` True,
   `ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2026` False, `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2026` False,
   and SOLIDWORKS CAM's box on saving an assembly with a lightweight component (a fact for W9d).
6. **SolidWorks 2024's confirming set is complete, 0 failed, under a ruling on its What's Wrong box**
   (2026-11-17, small hours). The first 2024 session stopped in m3 at What's Wrong during the app's own Update with
   the user's mates in error (`sw2024/w9a-confirm-sw2024-20261117-1-*.log`), a §0.3 STOP. The box was then measured,
   watched and never answered (`sw2024/w9a-box-sw2024-20261117-1-box.log`, `-2-reducer-box-k3.log`): it comes up,
   blocks nothing, goes by itself in 3 to 23 s, and the Update returns with its results right. **The coordinator
   ruled that the app leaves the box alone** (no SolidWorks setting changed, no refusal; a sentence tells the user),
   and put it to the user as the default they may change; the plan's last section says it and what was not
   measured. With 2024's findings set (`5eda959`, `c18ce99`) and the script's rule for the box (`a072efa`,
   `10a6a08`): setup, go, reducer, nocarrier (`-2-*.log`), m3 (`-4-m3.log`) and reducer, k3 (`-5-*.log`) all 0
   failed. Reviewed in `notes-workbook/W9A-CLOSE-2024-REVIEW.md` (`8e984e2`): the set is complete, no 2024 rerun is
   needed, the ruling is defensible as a default put to the user.
7. **W9a closed** (2026-11-17, about 04:00). The 2024 review's list was worked off: 2024's findings' comments
   and pins re-based on its last three logs, with the feature-in-error case of a plain assembly rebuild recorded on
   its own (`ebc33f3`: `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2024` True, `_ON_2026`
   None because the 2026 runs looked every 2 s and that box lasts half a second; nothing reads it); the two What's
   Wrong sentences (`633fd83`: "for up to half a minute", "leave it alone", *may have shown* only after a press that
   changed or put something, never both in the footer); the script checking SolidWorks' frame on every poll
   (`9280433`). **The final full run on SolidWorks 2026**, one session from `91d40f5`: all twelve sections 0 failed,
   0 STOPs, and the window check's W8 stage with K12 no fails (`probe/results/w9a-final-sw2026-20261117.log`,
   `w9a-demo-20261117-023503.json`, `w9a-final-window-sw2026-20261117.log`; `f0c5ff7`). Reviewed in the addendum at
   the end of `notes-workbook/W9A-CLOSE-2024-REVIEW.md` (`bf2960d`): the fixes answer the review, the run is no
   weaker than the closing run it replaces, and the three commits after `91d40f5` change nothing the worker does on
   2026, so nothing is re-run. Suite at `ebc33f3`: Linux 1 failed (the known font-width test), 3498 passed, 1
   skipped; Windows window tests at `633fd83` 165 passed, 1 skipped.
8. **What W9a leaves open.** *Questions the user has not answered:* the ruling that the app leaves SolidWorks
   2024's What's Wrong box alone (the default stands until they say otherwise; the other way is the app turning
   SolidWorks' "show errors every rebuild" off for its job, unmeasured, and theirs to allow); question 9 (other
   kinds of user mate on a put gear refuse until measured); whether three older W8 result files that carry
   SolidWorks' frame title (with the licence edition) should be scrubbed; whether `refuse` should be run on 2024
   (not in the confirming set by rule). *Not measured, each said in the plan's last section:* a person pressing the
   What's Wrong box during an Update, a box that outlives its job, a Build with the user's work in error, the mate
   case on a gearbox without modes on 2024. *Refusing until measured (`None` findings):* route (c1) on a held gear,
   a fixed gear, a sub-assembly, and a no-carrier train with modes. *Moved to S5 in W9c:* M1's unread kinds
   (concentric, width, limit, path, a user gear mate on an app gear, a sub-assembly's leaf). *Small, known:* under
   the window check's W8 helper a blocking What's Wrong box is logged at once but the run waits out W8's timeout
   before stopping (time, not safety); `PROBLEM_COMPONENT` and `PROBLEM_UNSETTLED` can say one thing twice; the
   assembly's own feature tree is not read for the user's features. **Agent runs in W9a: far over the plan's 11**;
   the user was told and said to keep going without asking (2026-11-16).
9. **W9b is closed on SolidWorks 2026 and 2024 (2026-11-17, morning).** *2024:* the demonstration ran there in a
   fresh session from `529f939` (`probe/results/sw2024/w9b-demo-sw2024-20261117.log`, `9e77303`): build, update
   and old 0 failed, every mode as §3; in part the relief reads exact and the coarse volume guard failed at 1.3e-4
   against a fixed 1e-4. The review's 2024 addendum (`W9B-REVIEW.md`, `9b85411`) lays that to SolidWorks 2024's
   mass properties (the unbanded sleeve reads 2.2e-4 over its own section there, the geometry the same on both
   versions) and rules the guard's allowance be taken from that control in the same session (factor 1.0, floor
   1e-4, cap 5e-4); with it both versions' readings replay clean (`6bdf802`), and no 2024 rerun is owed. The step
   faces are one planar face each on both versions; the next run of `part` integrates their edges. *How it went
   on 2026:* One implementer wrote it against the fake: the interface note
   `notes-workbook/W9B-INTERFACES.md` (`42dff4d`), package B (`fcbf70b`, `baee8bd`; the Gears columns Start band and
   End band after Slides, the banded sleeve's part as the internal ring plus three globals, two planes, a circle on
   each and a loft cut named Relief, the `hub` kind built and made its shaft's anchor, record schema 8, sidecar
   schema 2), `RangeBox_Fixed` in the fixtures (`3278dd2`), package A (`d43c6e3`; reach, hub and running-clearance
   warnings), the boards (`d72db30`; **their PNGs are not rendered, this host has no Chrome**). Reviewed in
   `notes-workbook/W9B-REVIEW.md` (`11550e3`): the plan's answer key held by an independent hand-working; one
   must-fix (a band over a hub on another shaft read as neutral) and five should-fix, all taken (`172e47c`,
   `ce712b4`, `7ce72dd`), re-checked in the review's closing section (`e5cbc98`), whose one new point is fixed
   (`fca29a2`: a hub goes to the sleeve that covers it in every mode). **Demonstration** `probe/w9b_demonstration.py`
   (note `notes-workbook/W9B-DEMONSTRATION.md`; it runs W9a's script's `main` with sections part, build, update,
   old): the first whole run's eleven FAILs were three faults of the script's checks
   (`probe/results/w9b-demo-sw2026-20261117-1-script-faults.log`; the review agrees no fault of the app was
   explained away); **the run from `b15450f`, 0 failed, no STOP** (`probe/results/w9b-demo-sw2026-20261117-2.log`,
   `w9b-demo-20261117-051122.json`; `de0a470`): the relief one true cylinder of radius 12.5 between the step faces
   at 5 and 21, RangeBox_Fixed built from scratch with H, N and L as §3's table, no interference, a band changed by
   a value Update, the bands taken off refused or answered with Build again…, RangeBox as before with its seven
   warnings. Suite at `fca29a2`: Linux 1 failed (the known font-width test), 3574 passed, 1 skipped. **Rulings by
   the coordinator, each the user's to overrule** (W9B-INTERFACES §7): a one-band sleeve is not built; a hub keys
   one sleeve; a banded and a plain sleeve of one size share a default file name and need a Part name on one; a
   thin-wall warning over the relief (the review's N4) is not added. **Left open:** `de0a470`'s message says "the
   exact form's to 3.8e-5": against the true section (the end face's area) it is 9.0e-5, inside the 1e-4 allowed
   but with little room, and its ratios are the app's report, not measured by turning; the script (`203ce86`, not
   run on 2024 only) takes the section from the face; **the two step faces' `GetArea` read 114.30 mm²
   where the geometry gives 114.558**, the same to nine figures on both versions (the volumes side with 114.558;
   why the area reads low is not known; printed, not judged). `fca29a2` was in 2024's snapshot. Not measured: a banded sleeve on a Z− shaft, unequal bands from
   scratch, a hub with a bore, a typed Rim on a banded sleeve.
10. **W9c is closed on SolidWorks 2026 and 2024 (2026-11-18, morning)**
    (plan §5 and §2.1: Update adds, removes and re-mates, and adds and removes modes). `UPDATE_INSERTS_A_GEAR`,
    `UPDATE_BANDS_IN_PLACE`, `UPDATE_ADDS_A_MODE`, `UPDATE_REMOVES_A_MODE` and `UPDATE_MAKES_MATES_WITH_MODES` are
    True on 2026 (`74024a1`, re-checked in `4315774`) and on 2024 (`d0e32bb`, re-checked in `b725b32`);
    `UPDATE_MAKES_A_NEW_COUPLING`, `UPDATE_SUPPRESSES_THE_RELIEF` and `EXTERNAL_REFERENCES_READ` stay None on both, as
    ruled (C1 to C12 of `notes-workbook/W9C-INTERFACES.md` §10). The probes, the interface and the packages are in
    `notes-workbook/W9C-PROBES.md`, `W9C-PROBES-REVIEW.md`, `W9C-INTERFACES.md`, `W9C-REVIEW.md` and
    `W9C-FIXES-REVIEW.md`; the demonstration is `probe/w9c_demonstration.py`, its note
    `notes-workbook/W9C-DEMONSTRATION.md`, its review `notes-workbook/W9C-RUNS-REVIEW.md` with its addenda and
    re-checks.
    *On the second host, 2026-11-17 afternoon and evening (SolidWorks 2026 34.0.0).* The eighth and ninth runs
    (`1221807`) and the fixes they led to: a press that finds a part left in error still open stops before any write
    (`89615aa`, `1cc2978`, `3a9e592`, `007b3aa`; reviewed in `3a6013d` and `c76def2`). The final run, runs 10 and 11
    from `3a9e592`'s `src` in one session (`d878105`; `probe/results/w9c-demo-sw2026-20261117-10-…` and `-11-…`;
    `<probe folder>\w9c-final-sw2026-20261117-143421`): every section 0 failed with no STOP but run 10's remake M3,
    which died on a script fault fixed in `eabf14e`, so run 11 is M3's evidence. Reviewed in W9C-RUNS-REVIEW's "The
    final runs on SolidWorks 2026" (`dbf9870`): the Done-when is met on 2026 on the final app code. The five 2026
    gates (`74024a1`); should-fix A, the record's assembly named in the close-without-saving advice (`f4eabf5`); the
    script made ready for 2024 (`15bd445`); all re-checked (`4315774`). The confirming run on SolidWorks 2024 32.5.0
    from `4315774` (`06d5141`; `<probe folder>\w9c-confirm-sw2024-20261117-171854`, four sessions, its masters built
    in the run): `landing`, `fixed`, `modes`, `remove`, `bands-off` and `m4` 0 failed; remake's M3 stopped before step
    2, because What's Wrong, raised at the script's own activation of RangeBox with the ring in error, was still up
    60.11 s after that job (the STOP).
    *On this laptop, 2026-11-18 (SolidWorks 2026 34.1.1, SolidWorks 2024 32.5.0).* The 2024 run reviewed (the addendum
    "SolidWorks 2024", `78fdcb6`) and the note's 2024 section corrected from its logs' own lines (`c5f113a`). The five
    gates set True for 2024 (`d0e32bb`, with the re-check's `bf765b3`). A close path for a What's Wrong that outlives
    its job, asked for by a flag (`b1230ab`, `eee5ffe`; re-checked in `b725b32` and `d48ecbf`). remake's M3 rerun on
    2024 from `c2d95cc` with `--close-outlived-whats-wrong` (`1dc9350`; 1287 s, 42 ok, 1 FAIL, no STOP;
    `probe/results/sw2024/w9c-demo-sw2024-20261118-5-remake-m3-second-pass-assembly-flag.log`; `<probe
    folder>\w9c-remake-m3-sw2024-20261118-045041`): steps 2, 2b and 3 measured; two boxes outlived their jobs, one at
    the script's read and one in the app's own press, and each was closed by the script; the one FAIL is
    RangeBox.SLDASM read marked at its first activation after step 1. Reviewed (`6665b4e`): the evidence stands, the
    FAIL is a fact of SolidWorks, the sentences must change. Then `WHATS_WRONG_STAYS_WITHOUT_A_REBUILD` (`5de0290`;
    True on 2024, False on 2026, re-based on the 2026 run in `ea4efec`); the What's Wrong sentences (`7d96316`,
    narrowed to a press that stopped before rebuilding in `29d09da`); the script states the mark as a fact of the
    attached version (`746595a`, `25a0bd3`); `ISSUE-1-PLAN.md`'s What's Wrong section (`67ee901`, `7f110f1`);
    re-checked (`1f8540f`). remake's M3 on SolidWorks 2026 34.1.1 from `23107c2`, without the flag (`5aca9c1`; 989 s,
    42 ok, 1 FAIL, no STOP; `probe/results/w9c-demo-sw2026-20261118-12-remake-m3.log`; `<probe
    folder>\w9c-remake-m3-sw2026-20261118-053114`): step 2b read as on 2024, no What's Wrong anywhere, and the one
    FAIL the same mark, which the coordinator ruled a fact on both versions (`7f110f1`).
    *The review's lists of what remained, item by item* (W9C-RUNS-REVIEW: §5 of the final-runs addendum, §6 of the
    2024 addendum, §4 of the review of `1dc9350`):
    - the five 2026 findings: **done**, `74024a1`. The five 2024 findings and the no-fixture gate-list test: **done**,
      `d0e32bb`, `bf765b3`;
    - the note's 2024 section corrected (the box did not go): **done**, `c5f113a`;
    - a ruling on a box that outlives its job, the script's must-fix on code 72, and remake's M3 rerun on 2024:
      **done**, the ruling in `ISSUE-1-PLAN.md`, `b1230ab`, `eee5ffe`, `1dc9350`;
    - step 2b on 2026: **done**, `5aca9c1`; it reads as on 2024;
    - should-fix A: **done**, `f4eabf5`, with package B's `9cbfc08` and `0b7582f` on the user's own unsaved work; its
      premise (a part closed alone stays loaded in error, its flag no longer saying so) measured by 2b on both
      versions;
    - if the app's own press left the box up on 2024, the not-measured list and the sentences take it: it did, and
      **done**, `5de0290`, `7d96316`, `29d09da`, `67ee901`;
    - the second pass's FAIL ruled a fact, the script's check amended and `read_now`'s first flags logged before step
      2: **done**, `746595a`, `25a0bd3`, `7f110f1`. Neither M3 run has that new log line, both having run before it;
    - `findings.py`'s 2024 comments (the entity-kind caveat lifted, M3 to step 3, the assembly's mark as a fact):
      **done**, `5de0290`;
    - the low docstrings, `_close_unsaved`'s premise and `gears/landing.py` on 2024's code 51: **done**, `67ee901`;
    - the handoff (the stale bullet, this item, the phase table, the memory advice and the interference volumes):
      **done** here;
    - the whole suite at the commit that closes W9c: **done** with W9d's close, at `06d818f`, by the coordinator: 4134
      passed, 1 skipped, 1 failed (the known font-width test). Earlier whole runs by reviewers: 4099 / 1 / 1 at
      `f7c2f0d`, 4101 / 1 / 1 at `b1230ab`, 4103 / 1 / 1 at `c2d95cc`;
    - **not done, low:** the run-10 section of `W9C-DEMONSTRATION.md` still writes its run folder under the Windows
      account folder, where the house form is `<probe folder>\…`; the re-check's notes on a part in two gearboxes'
      assemblies and on `gated_refusal`'s "already True" branch, which no self-check drives; and the final-runs
      addendum's own low notes (its §5 item 5: the external bevel foreseen in the virtual frame, a recipe A part with
      a user's `Pitch` dimension in the app's tooth-space sketch, `_evaluates` measuring trig units before the M3
      stop, a relief op failing before the sleeve is listed as changed, the raise path in `_update_document` dropping
      what was set).
    *What W9c leaves open:*
    - **a known limit** (`W9C-INTERFACES.md` §11, "Known caveat, for after W9c"): an *unmarked* part with an app
      feature in error, which the press leaves alone, still lets the press write into the assembly and then offer
      saving. It is pinned as today's behaviour; W9d did not take it;
    - **defaults standing for the user:** an Update that adds a gear into one of their components adds it and names
      the interference afterwards (the footer before the press is silent); a removal refuses while any of their
      components is present, until the external-references read (M4) is measured with a part made by hand; a plain
      gear added, and a removal on a gearbox with modes, are measured on the fake only; the ring's sketch itself is
      not changed (a ring set one tooth down is routed through a safe tooth count; a construction that removes the
      ambiguity for new builds is described in A's hand-back, unmeasured);
    - **What's Wrong, not measured** (`ISSUE-1-PLAN.md`'s What's Wrong section, 2026-11-18): a person bringing the
      assembly forward by hand after a stop, and closing documents with the box up; a box past 60 s; a press that
      stops before any rebuild with the user's own work in error; which document's activation raised the box in the
      app's press; "show errors every rebuild" off; and the older items listed there;
    - **measured differences from 2026, for the record:** the straight one-tooth-down ring fails on code 51 on 2024
      and 72 on 2026, and nothing in the app reads the number. SolidWorks 2024's summed interference volumes differ
      from the app's: the app only prints its number and acts on none, but on 2024 the number can be some 5 % off what
      SolidWorks' own Interference Detection then shows (2024 addendum §4);
    - **memory on SolidWorks 2024** (2024 addendum §4): the first Update of a gearbox with modes on a freshly opened
      copy grew SolidWorks 2024 by 3.3 to 4 GB, a refused press included, and the memory came back only when the copy
      was closed; the script, keeping one copy open for six presses, reached 14.76 GB private in `modes`. On 2026 the
      whole run stayed under 2.3 GB. The app does not watch memory. It is said to the user as question 15;
    - the user's questions of W9a's item 8 still stand.
11. **W9d (Build again… carries the user's work) is closed on SolidWorks 2026 and 2024 (2026-11-18, morning)** (plan §5, W9d).
    Its contract is `notes-workbook/W9D-INTERFACES.md`, with §8 the findings by version; the probes
    `probe/w9d_probes.py` (note `W9D-PROBES.md`, review `W9D-PROBES-REVIEW.md`); the packages' notes and reviews
    `W9D-PACKAGE-A.md`, `W9D-PACKAGE-B.md`, `W9D-REVIEW-A.md`, `W9D-REVIEW-B.md`; the demonstration (M9)
    `probe/w9d_demonstration.py` (note `W9D-DEMONSTRATION.md`, review `W9D-DEMONSTRATION-REVIEW.md`). The link record
    is schema 10 (`22c33dc`).
    *Written on the second host, 2026-11-17 afternoon and evening (SolidWorks 2026 34.0.0).* The contract (`57cda76`),
    reviewed (`W9D-INTERFACES-REVIEW.md`, `f0eb516`), revised to the review and the coordinator's rulings (`7e13344`,
    `23ed8c5`) and re-checked (`8d3695b`). The probes (`7e478b3`), run on 2026 (`64acec9`; `faces` again with a third
    route, r3, `890df13`), reviewed (`94fbebf`), their 2026 reads set (`013c14c`). Package A, the worker (the read R
    and the carry C behind `build_gearbox`'s carry keyword, from `3c6a954`), and package B (the record, `carry_for`,
    the question, the result and the footer, the window's carrying Build again…), each reviewed and fixed in rounds, A
    through seven, with an audit of the fake against SolidWorks as measured (`ee78ee3` to `a2d0ff2`, `0e755ed`;
    reviewed in `e056f33`; the coordinator's rulings on it `7e3ad9a`). The demonstration script (`7d3a49e`, reviewed
    `6f67791`). Its first run on 2026 34.0.0 (`50a8e54`, `<probe folder>\w9d-demo-sw2026-20261117-155112`) met three
    faults of the app (the r3 walk read nothing through a late-bound member handed back uncalled; the carry stopped
    after the states for want of a new gear's handle; Python text reaching a sentence), fixed in `94f57f8` and
    reviewed (`eb66f22`); the fixture's tie was rebuilt so it no longer over-defines the old assembly (`7ea8864`,
    re-checked `b44594d`).
    *On this laptop, 2026-11-18 (SolidWorks 2026 34.1.1, SolidWorks 2024 32.5.0).* The second run on 2026 (`c2d95cc`;
    `<probe folder>\w9d-demo-sw2026-20261118-031029`; logs `probe/results/w9d-demo-sw2026-20261118-1-…` and
    `-2-carry-closed-clean.log`): every section from `f7c2f0d` in one session, `fixture`, `carry-gates` and `carry` 0
    failed with the Done-when whole; `carry-closed`'s one FAIL was the script's, fixed in `41afa37`, and that section
    is 0 failed rerun from it. No FAIL was the app's. Reviewed (`7996089`): the evidence stands and the 2026 findings
    may be set, with two wording must-fixes, both taken (`891a707`: a fallen component named with its old name beside
    the new, and the sub-assembly clause said only where sub-assemblies are carried). The 2026 findings set
    (`225e3d7`): `CARRY_INSERTS`, `CARRY_INSERTS_IN_A_CONFIGURATION`, `REFERENCED_CONFIGURATION_READ` and
    `CARRY_GEAR_MATE_ON_AN_APP_GEAR` True, `CARRY_REMAKE_KINDS` the eight kinds shown (coincident, concentric,
    parallel, distance, angle, limit distance, lock, gear), and the lightweight fact as a pair by ruling, True on 2026
    and None on 2024; `CARRY_INSERTS_A_SUBASSEMBLY`, `CARRY_REMAKES_ON_A_LEAF`, `VIRTUAL_READ`,
    `PATTERN_INSTANCE_READ`, `ORIGIN_ENTITY_READ` and `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` stay None, the fixture
    having none. The probes on 2024 from `891a707` (`4623701`; `<probe folder>\w9d-probes-sw2024-20261118-051527`; 0
    failed, no STOP), reviewed (`23107c2`); the fourteen reads set on 2024, each as its 2026 twin (`a3e05fe`);
    `REFERENCED_CONFIGURATION_READ`, `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`, `ORIGIN_ENTITY_READ` and the vertex
    route stay None there with why. `W9D-INTERFACES.md` §8 brought up to date after each (`e3395d3`, `2b51fbe`). W9d's
    script takes `--close-outlived-whats-wrong` (`f3c4873`, the coordinator's extension of the ruling). The re-check
    of all of it before the 2024 run (`017624e`): fit, nothing to fix first.
    *The confirming run on SolidWorks 2024 32.5.0, closing W9d* (`69b6354`, from a `git archive` of `5aca9c1`;
    `<probe folder>\w9d-demo-sw2024-20261118-060436`; two fresh sessions, each with `--close-outlived-whats-wrong`;
    logs `probe/results/sw2024/w9d-demo-sw2024-20261118-1-fixture-gates-carry-clean.log` and
    `…-2-carry-closed-clean.log`): `fixture`, `carry-gates` and `carry` in one session (20, 27 and 45 ok),
    `carry-closed` in the second (46 ok); 0 FAIL and no STOP anywhere, no What's Wrong box (so the close path never
    fired), the script unchanged. Every row of the Done-when reads as on 2026. Reviewed in W9D-DEMONSTRATION-REVIEW's
    "The confirming run on SolidWorks 2024 (32.5.0), reviewed" (`e51de95`): the evidence stands, the Done-when is met
    on both versions. The six 2024 findings set, each as its 2026 twin, and pinned (`e7a3577`): `CARRY_INSERTS`,
    `CARRY_INSERTS_IN_A_CONFIGURATION`, `REFERENCED_CONFIGURATION_READ` and `CARRY_GEAR_MATE_ON_AN_APP_GEAR` True,
    `CARRY_REMAKE_KINDS` the eight kinds, and the lightweight fact True; the other six stay None. `W9D-INTERFACES.md`
    §8 (a new §8.4 with the 2024 values and differences) and the note (`d8a12f6`). With the findings alike on both
    versions, the Build again? question for a record with no SolidWorks version on it said nothing would be carried;
    it now says what is true whichever version the press meets, by the coordinator's ruling (`06d818f`). Beside it, a
    fault in the planet-copy lookup of `carry_for`, found by the printed-gears work: a planet copy made new got no app
    feature names and a vague reason, so a user mate on its Gear Axis was named as on a feature its new part "does not
    have" (conservative, wrong in words); assessed (`7f91037`), fixed (`d496cfd`), re-checked (`12cf15d`), on the fake
    only. The whole suite at `06d818f`, by the coordinator: 4134 passed, 1 skipped, 1 failed (the known font-width
    test). The last re-check of `e7a3577`, `d8a12f6` and `06d818f` (`235f658`, in `W9D-DEMONSTRATION-REVIEW.md`): fit
    to close W9d.
    *What W9d leaves open* (W9D-DEMONSTRATION-REVIEW's last sections, W9D-PROBES-REVIEW's last section):
    - **gates still None on both versions, and what the app says for each:** `CARRY_INSERTS_A_SUBASSEMBLY` (a
      sub-assembly of the user's is named, not carried, and the old assembly keeps it), `CARRY_REMAKES_ON_A_LEAF` (a
      mate on a part inside a sub-assembly is named), `VIRTUAL_READ` (a virtual component is named, with no file of
      its own), `PATTERN_INSTANCE_READ` (a pattern instance is carried as a component of its own, which the standing
      clause says), `ORIGIN_ENTITY_READ` and `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` (a mate on an origin or a vertex
      is named with its finding). Each is a true sentence and nothing is lost: the old assembly keeps all of it;
    - **known limits measured on SolidWorks 2024** (W9D-DEMONSTRATION-REVIEW's last section §3, `W9D-INTERFACES.md`
      §8.4): a carrying Build again… of a gearbox this size took SolidWorks 2024 to about 11 GB private (11.03 and
      9.12 GB at the end of the app's job; a build alone about 6.4 GB), given back when the copy closed, and carrying
      17 components and 31 mates added about 16 to 20 minutes; the face prefilter kept 87 of Sun's faces on 2024
      against 3 on 2026, so the 200-candidate cap comes sooner on a many-toothed gear's root or fillet (about 100
      teeth for a fillet), and the cap names the mate with a true sentence. Recorded as known limits; no sentence is
      added (question 17);
    - **an edge prefilter, should-fix, open:** in `swcom.entity_references` the edge's circle prefilter took 8.05 s on
      2024 against 5.07 s for the full walk, and the 20 s cap does not bound it (W9D-PROBES-REVIEW); M9's fixture has
      no edge mate;
    - **shown on the fake only, or named, never on SolidWorks** (one fixture of 17 parts on RangeBox; the caveats are
      in `findings.py`'s M9 comments): the fallback shown on SolidWorks is the tie (`FELL_TIE`) alone, with one
      FixComponent fixing in every mode; `FELL_NEW_ERROR`, `FELL_OVER_DEFINED`, the per-mode fix, a clash sentence,
      `same_error`, `moved`, a mode new or gone in the revision, a distance or angle whose FlipDimension reads 1, a
      gear mate of the other sense, perpendicular, tangent and limit angle mates, an old assembly open with unsaved
      changes, a user part open with unsaved edits, a fixed state that differs by mode, an app gear reused as the same
      file under a user gear mate, the planet-copy path of `d496cfd`, and an `UNSAVED` planet's sentence. The review
      traced each unshown path: each writes only into the new revision's assembly after its first save, never into the
      old assembly or the user's files, so at worst the carry is less faithful and says so;
    - **documents:** W9's closing entry in `ISSUE-1-PLAN.md` (the review's last item 7) was not in the log when this
      was written.

Run folders kept on this device under `C:\Users\M0obo\Documents\GearGeneratorProbe\`: `w9-s0-20261116-045513`
(2026's `out\rangebox.master`, where W9a's demonstration starts) and `w9-s0-sw2024-20261116-064725` (2024's, with its `out\rangebox.master`) and `w9-s0c2-sw2024-20261116-155303` (run 4). The
person's steps of W8 (`s6` on both versions, the two hand drags) are still theirs to do, under *Questions waiting for
the user*.

**Run folders and masters, 2026-11-18** (under `<probe folder>`, the `GearGeneratorProbe` folder in the Windows
account's Documents). *On this laptop:* the 2026 masters W9c's and W9d's runs here started from are S0's
`w9-s0-20261116-045513\out\rangebox.master` and W9a's final `w9a-final-sw2026-20261117-023433\out\setup.master` (with
`reducer.master`); the 2024 masters are S0's `w9-s0-sw2024-20261116-064725\out\rangebox.master` and W9a's
`w9a-confirm-sw2024-20261117-002313\out\setup.master` (with `reducer.master`). W9d's 2026 fixture master is
`w9d-demo-sw2026-20261118-031029\out\w9d-fixture.master`, and the 2026-saved `RangeBox_r2.SLDASM` in that run's
`out\carry` served the 2024 probes as their other-version file. Tonight's run folders:
`w9d-demo-sw2026-20261118-031029`, `w9c-remake-m3-sw2024-20261118-045041`, `w9d-probes-sw2024-20261118-051527`,
`w9c-remake-m3-sw2026-20261118-053114` and `w9d-demo-sw2024-20261118-060436` (running when this was written). *On the
second host only:* `w9c-whole-sw2026-20261117-123612` (the 2026 34.0.0 masters that W9c's runs 10 and 11 and W9d's
2026 probes and first M9 run took), `w9c-final-sw2026-20261117-143421` (runs 10 and 11),
`w9c-confirm-sw2024-20261117-171854` (W9c's 2024 confirming run, with the 2024 masters it built: `rangebox`, `setup`,
`fixed-updated` and `reducer`), `w9d-probes-sw2026-20261117-140201` and `w9d-demo-sw2026-20261117-155112`. Nothing on
this laptop needs those: every run here took this laptop's own masters. By their notes, the runs here only copied
their masters.

## Where it stands

| Phase | State |
|---|---|
| W0–W1 xlsx read/write, model, schema | done, reviewed, review fixes in |
| W2 Workbook window, live link, Build parts | done, reviewed, fixes in. The batch build (`swbuild.build_many`) ran on SolidWorks 2024 and 2026 (`208712c`); logs `probe/results/w2-build-20261113-164647.log` and `probe/results/sw2024/w2-build-20261113-165706.log`. |
| W3 geometry, phases, kinematics, checks, fixes, Export, Results sheet, two-column window | done, reviewed twice, every item fixed. The Excel checks passed on Windows: the Windows-saved fixture (`aa86cc7`) reads, and exported files open in Excel with no repair prompt. |
| W4 layout part + static assembly, Update SolidWorks, build-again `_r<n>` | **closed 2026-11-14**: the rebuild fault probed and fixed, pass 4 verified, both demonstrations rerun on SolidWorks 2026 and 2024 with every check passing, each step reviewed. Details and what is left open below. |
| W5 motion | **closed 2026-11-14**: probes P0 to P0d and the two ring rounds run and reviewed, packages A to E written and reviewed, the demonstration run in full on SolidWorks 2026 and confirmed on 2024, the user's hand drag passed on both. Details, and what is left open, below. |
| W6 right-angle | **closed 2026-11-15, but for the person's drag**: planned, reviewed and revised; probe tier 9 (a turned gear mate's sense, on cylinders, SolidWorks 2026) run and reviewed; packages A to E written and each reviewed; the full build run on SolidWorks 2026 and the confirming build on 2024, both from one snapshot (`931fe1a`), every check passing, each run reviewed. Left for the user: drag G1 in the built right-angle gearbox. Details below. |
| W7 planetary | **closed 2026-11-15, but for the person's drag**: planned, reviewed and revised; the spike on SolidWorks 2026 (`W7-SPIKE.md`); packages A to E written and each reviewed; the demonstration run on SolidWorks 2026 — its first run found one app fault (a turned planetary's put did not hold), the probe `planetary_put_back` measured the route that does, the fix `9f21d99` was reviewed, and every section then passed, the planetary sections and the W5/W6 Update sections once more on the final code; the confirming build on 2024 passed; the run's evidence reviewed. Left for the user: drag Sun in the built planetary. Details below. |
| W8 sleeves and modes | **closed 2026-11-16, but for three things: the built footer on a screen shorter than the window asks (cut off; open as K12 of W9), the person's step `s6`, and the two hand drags of W6 and W7**: planned, reviewed and revised to the spike (`W8-PLAN.md`, `W8-PLAN-REVIEW.md`, `W8-SPIKE.md`); the interface commit with its rulings (`W8-INTERFACES.md` §9); the findings set and reviewed (`ea7a46f`); packages A to D written and each reviewed; probe tier 11, and the one app fault the first build found, fixed and reviewed; package E's demonstration run on SolidWorks 2026 (34.0.0 on the second host, 34.1.1 here); the closing run from one snapshot of the final source (`c583f48`, 34.1.1): `s0` to `s5` and `s7` and the W5 to W7 sections r1, r2, r3, m5, m8, p1 and p3, every check passing (`c351b1f` to `aff9bfe`), and the full window check 1 failed, the built footer's height (`fb85bcc`); the confirming build on 2024 (32.5.0): `s0`, `s1`, `s2`, `s3`, `s7` 0 failed, its window stage the same one failure (`c3ed9b6`); each run reviewed (`W8-REVIEW-SW2024-CONFIRM.md`, `W8-REVIEW-CLOSING-RUN.md`). The ruling on the footer, the steps for the user and what is left are under *How W8 closed* below. |
| W9 the user's work in a built assembly, and dog-clutch sleeves (issue #1) | **Closed 2026-11-18 on SolidWorks 2026 and 2024; merged into `workbook` by the coordinator after the handoff commit that says so; GitHub issue #1 left open for the user to close.** W9a closed 2026-11-17: the user's work is kept by Update or refused by name before any write; shown on SolidWorks 2026 and confirmed on 2024 under the coordinator's ruling that its What's Wrong box is left alone. W9b (sleeve checks, bands with a relief, the hub) closed on both the same morning. W9c (Update adds, removes and re-mates, and adds and removes modes) closed on both on 2026-11-18: its five gates True on both versions, remake's M3 shown to step 3 on both, the What's Wrong sentences said as measured. W9d (Build again… carries the user's work) closed on both on 2026-11-18: M9 on 2026 twice and confirmed on 2024 (`69b6354`, reviewed `e51de95`), its findings set alike on both. Whole suite at `06d818f`: 4134 passed, 1 skipped, 1 failed (the known font-width test). What W9 leaves open is in the morning paragraph of 2026-11-18 and items 8, 10 and 11 of *Where W9 stands*. Planned, reviewed, approved by the user (2026-11-16). The plan is `notes-workbook/ISSUE-1-PLAN.md` (stages W9a to W9d), reviewed in `ISSUE-1-PLAN-REVIEW.md` and revised to its second review (`ISSUE-1-PLAN-REVIEW-2.md`). |
| Printed gears (FDM, PLA): stages F1 to F4 | **Stage F1 closed on branch `printed` (worktree `~/SW-Gear-Generater-printed`) on 2026-11-18, by its Done-when, on SolidWorks 2026 34.1.1 and 2024 32.5.0; not merged into `workbook`, which waits for the user's word.** Taken up on 2026-11-18 at the user's word to carry on past W9. The plan `docs/PLAN-PRINTED.md` was revised against W9's code and checked three times more in `docs/PLAN-PRINTED-REVIEW.md` (`158b06f`, `d2e34a6`, `6dc7359`). `printed` was cut from `w9d` at `f3c4873`; `w9d` and then `workbook` were merged into it (`91f6a6f`, `138d646`). On that branch: F1-0 (the pins `fe89e56`, the interface `7991634`, reviewed in `docs/notes-printed/F1-0-REVIEW.md`), packages A, B and C (reviewed in `F1-REVIEW.md`, `be5ae7a`, its should-fixes taken), and the demonstration `probe/f1_demonstration.py` (`F1-DEMONSTRATION.md`, reviewed `cf40e4a`), run clean on both versions (`5e2f386`) and the runs reviewed (`0e7000d`). Suite on `printed` at `138d646`: 4747 passed, 1 skipped, 1 failed (the known font-width test). Left open: the boards' PNG renders, the span over k teeth (F2's first step), the merge, and the user's word on question 19's rulings. Next: F2 (§3), the span over k teeth, a STEP save probe on both versions, Export STEP, then the user's prints. The record of this work is `docs/notes-printed/` on branch `printed`; the morning paragraph of 2026-11-18 above names each note. |
| How the user's absence is handled | the user said on 2026-11-14 to carry on, in order, until W8 is done. Judgement calls are taken at each plan's recommended reading and listed for the user as readings to overrule. On 2026-11-18, going to sleep, the user said to carry on past W9 down the plans with Opus subagents and a review of each step; the rulings taken since are questions 10 to 14, 17 and 18 below. |
| The small-pinion tip cap | `fix/small-pinion-cap` merged at `0f5a121` (the user's instruction): 6- and 7-tooth pinions build with an arc on the tip cap, version 0.3.2. Built on SolidWorks 2024 by the branch; the 2026 build and the merge's review are in hand. |

Suite, measured on a clean `git archive` of `2250ceb` (WSL, 2026-11-13): `PYTHONPATH=src .venv/bin/python -m
pytest -q` → **1559 passed, 10 skipped**. On the 2026-11-14 clone (another Python, fewer skips): 1699 passed, 1
skipped at `8504856`, where W4 closed; 1759 passed, 1 skipped at the W5 interface commit `07fd66a`; 2096 passed, 1 skipped at `c7770c8`, after D's review and B's
and C's fixes (2026-11-14); **2258 passed, 1 skipped** on a clean archive of `4cd8e7f`, where W5 closed (source as
`d99654a`).
The window's Tk tests run under Windows Python: `python.exe -m pytest tests/test_workbook_build.py
tests/test_workbook_window.py -q` → 115 passed, 2 skipped at `c7770c8` (a "no display for Tk" skip is a known flake that moves between tests;
rerun). The `PYTHONPATH` matters in a copy: the
venv's editable install otherwise imports the working tree's `src`, uncommitted edits and all.
At the closing run's snapshot `c583f48` (2026-11-16, the third device): Linux **3280 passed, 1 skipped, 1 failed**;
Windows window tests (`python.exe -m pytest tests/test_workbook_build.py tests/test_workbook_window.py -q`) 160
passed, 1 skipped. This host's Linux venv has tkinter, and its one failure is
`tests/test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`,
for this host's Linux Tk font width alone: it expects `Slee…m1.5_N30_r2`, and the wider room here leaves
`Sleeve_m1.5_N30_r2` whole. It passes under Windows Python; it is not a fault of the app.

## W4 in detail

**What exists.** Probe tier 7 passed on SolidWorks 2026 (a full run, `probe/results/latest.json` at the time)
and 2024 (`probe/results/sw2024/`), every decision the same; findings set in `bfc9ef5`. Then the interfaces
(`a93d6d9`), the record's schema 2 (`1f0548b`), the planning (`cb7e042` layout, `17f4bce` gearbox, `a623610`
update), the worker (`afb0c00`, `7ce7a26`, `d0203cd`), the footer and every sentence (`4b128a6`, `8fa0216`),
the window (`ccef692`), boards and docs (`b215dee`, `649d8db`, `47e4648`); the helical phase across Z+/Z−
was fixed first (`119da25`), and the ring pair's gear-mate Flip in `4c8a73a`.

**Demonstrated before the reviews** (`5154de1` and before): SolidWorks 2026 — all of it, 244 checks, 0
failed (`probe/results/w4-workbook-assembly-20261113-194228.log`, `…-200255-a2.log`,
`w4-window-20261113-195843.log`); SolidWorks 2024 — tier 7, the 12 : 1 build, its measurements and
controls, the Excel edit and Update only (`probe/results/sw2024/w4-workbook-assembly-20261113-200555.log`).
The user's 2024 session ran out of memory then; they have restarted it since.

**Reviews and fixes.** Three independent reviews, four fix passes:

- review 1 → pass 1, worker, planning and record (`042f276`, `9c64960`, `88385f1`, `a6abd5d`, `2b752a1`),
  and pass 2, the window, every sentence and the docs (`a8bb817`, `7dc0d90`, `571cf1a`, `2a4653e`,
  `94c85d7`, `01b889e`). Rulings: `notes-workbook/W4-DECISIONS.md`, `W4-REVIEW-RULINGS.md`.
- review 2 (N1–N6) → pass 3 (`45173e0`, `a9d20ab`, `707bfcb`, `7de851a`, `d5eecb2`, `fb3bbdc`, `ae1d208`,
  `d2cd2d6`, `d37ae52`): a part's own name claimed before any suffix; the held-values check compares
  evaluated values; every COM action through `swcom._guarded`; whose a record is, by the file, and asked
  once when its workbook is gone; marks a job can prove cleared; a build's journal; close anyway / quit
  anyway; the demonstration's new section a3. Report: `notes-workbook/W4-REPORT-FIX3.md`.
- review 3 (`notes-workbook/W4-REVIEW-3.md`: the 200-document cap that could clear an unsaved mark, a file
  id of 0 making two workbooks one, the journal wiped by any refused job, a false sentence after "No") →
  pass 4 (`f335379`, `2250ceb`). Report: `notes-workbook/W4-REPORT-FIX4.md`. **Pass 4 has not been verified
  by a reviewer**, and it was wound down early: its code and tests are complete and green, but four boards'
  `.dc.html` were regenerated without redrawing their PNGs in `design/renders/` (`WorkbookCloseAnyway`,
  `WorkbookMoved`, `WorkbookUnsaved`, `WorkbookUpdated`).

**The rerun on SolidWorks 2026** (code at `9aeed80`, that is pass 3 without pass 4; logs in `8b1ef15`;
report `notes-workbook/W4-RERUN-2026.md`): **292 checks passed, 3 failed, all three from one fault in the
app.** After an Update, SolidWorks marks every part modified, including parts Update never changed, because
the app rebuilds an assembly with `ForceRebuild3(False)` (`swcom.py`: `rebuild()` and the re-place of a
component), which rebuilds every component. So SolidWorks would ask to save parts nothing changed, parts
shared with earlier revisions among them. A repro on a saved assembly showed `ForceRebuild3(True)` and
`EditRebuild3` marking the assembly only. The fake SolidWorks does not model this. What only SolidWorks
could confirm did hold: `QuitDoc` closed modified documents without a dialog, `documents()` listed every
document in memory, and the value comparison never disagreed falsely. Journal reuse and the marks clearing
(section a3) passed.

**Open for W4, in order:**

1. **The rebuild fault.** Probe first (the house rule): which assembly rebuild still shows a put's new
   frame, the layout's moved axes and a changed part, while leaving unchanged components unmodified. Nothing
   of this probe is written; `notes-workbook/W4-REBUILD-PROBE-TODO.md` says exactly what to build and run
   (a new tier-7 item, on 2026 and 2024). Then change the two rebuild sites, teach the fake that a full
   rebuild marks every component modified, and add the regression test.

   *2026-11-14: done as far as code goes.* The probe is `assembly_rebuild_scope` (`e79e863`, `6d0b1bb`); it
   passed in a full run on 2026, now 34.1.1 (76 of 76, `latest.json`), and alone on 2024 (27 of 27,
   `sw2024/probe-results-20261114-014813`), every decision the same (`9b9f546`): every route, even no rebuild,
   showed the put, the layout move and the changed part; `ForceRebuild3(True)` marked only what changed and
   returned False on a failed component; `ForceRebuild3(False)` marked every component. Findings in `e57aca7`
   (`ASSEMBLY_REBUILD_ROUTE` and the rest). The fix is `9c39fb8`, narrowed after its review: `swcom.rebuild_call`
   is the one place that decides, and the CALLER says which of three kinds of assembly it is, refused with a
   sentence when it does not. A part rebuilds as always. STATIC (fixed components: today's workbook gearbox)
   takes `ASSEMBLY_REBUILD_ROUTE`, top-only, which it requires: unsettled, a build or Update refuses before
   changing anything. TRAIN (W5's mated workbook gearbox, any plan with a `Mate` op built outside `build_pair`;
   nothing builds one yet) takes `MATED_ASSEMBLY_REBUILD_ROUTE`, full while None (set to the top-only route by W5's probes in
   `8504856`; `notes-workbook/W5-DECISIONS.md` says what that does and does not yet cover). PAIR (everything `build_pair`
   makes, and the p5 half-pitch controls) keeps the full `ForceRebuild3(False)` probe tiers 4 and 5 ran, whatever
   the train's finding says, since that is measured on other mates; an absent `PAIR_ASSEMBLY_REBUILD_ROUTE` is
   where a later pair probe could change it. The probe tried no mate and no assembly equation. The fake
   marks what the probe saw for the static route (a full rebuild marks every component, top-only the
   assembly, a put nothing; the reads after a put or a build mark the assembly, which the fake pins on the interference check though the probe did not isolate it); it models nothing unprobed.
   Since the review of `31d1ac9` an assembly's kind must always be said, and a pair's gate is back before its
   gears. **What the SolidWorks rerun (step 3) must still confirm:** the three checks the 2026 rerun failed
   now pass under the demonstration's corrected invariant (marked modified = `GearboxUpdate.changed` ∪ the
   assembly when Update rebuilt it or ran the interference check: `changed` keeps meaning content changed);
   the new part-only Update step in b; after a fresh build no part or layout part reads `GetSaveFlag` True and
   the assembly does (the reads after its save mark it — frame reads and/or the interference check, not yet
   isolated: the rerun logs the flags after each as fact lines, and an extra probe step is to settle it — with
   nothing to lose by not saving it); a document just opened from its file reads False. Still unprobed for
   the static route, and shown only by that rerun: a put
   and its top-only rebuild under `set_rebuild_suppressed(True)` (Update places with `CommandInProgress` on); an
   assembly BUILT with the top-only route; whether the assembly still reports needing a rebuild after the
   route; and a part opened alone by path reading `GetSaveFlag` False.
2. **A brief independent verification of pass 4** (`git diff 8b1ef15..f335379`).

   *2026-11-14: verified* (`notes-workbook/W4-REVIEW-PASS4.md`). It found one fault outside the diff, of the
   same kind as review 3's item 2: Export as… could write over another file on a volume whose file ids are all
   0. Fixed in `8bd2530`.
3. **Rerun both demonstration scripts** (`probe/workbook_assembly_check.py`,
   `probe/workbook_window_check.py`) on SolidWorks 2026, and on 2024 in a fresh session — there, for the
   first time, the structural step and `_r2`, a2, a3, b, c and the window run. Commit the logs. The 2026
   rerun went through a launcher that lets the app see only one SolidWorks process, because
   `swcom.find_candidates` asks every running SolidWorks for its version and the user's 2024 was running;
   that launcher was a scratch file on the host and has to be written again (`W4-RERUN-2026.md`, "How it
   ran"). Pass 4 added one expectation a rerun must confirm: a document just opened from its file reads
   `GetSaveFlag` False.

   *2026-11-14: rerun done, every check passed on both versions*, from a `git archive` snapshot of `9ac36c5`
   (the app as of `388c8d3`, with `findings.py` as of `8504856`, whose new values only the train kind reads and
   W4 never builds; `cross_version_open_check.py` as committed with these logs), one SolidWorks at a time, each started for the run and exited
   after it (no launcher needed). `workbook_assembly_check.py`: 322 of 322 on 2026 (34.1.1,
   `probe/results/w4-workbook-assembly-20261114-053855.log`) and 322 of 322 on 2024 (32.5.0, all five sections
   for the first time, `sw2024/w4-workbook-assembly-20261114-055924.log`), exit 0 both. `workbook_window_check.py`:
   10 of 10 on each (`w4-window-20261114-055011.log`, `sw2024/w4-window-20261114-061023.log`).
   `gear_pairs_check.py` on 2026: spur, ring, crown and internal all ok, as before the three kinds
   (`gear-pairs-20261114-055230.log`). The three checks the 2026 rerun failed now pass; after a build no part
   or layout part is marked and the assembly is; the part-only Update in b marks G2's part and the rebuilt
   assembly, the record the part alone; every document reads `GetSaveFlag` False straight after a reopen. The
   new fact lines isolate what marks the assembly: the frame reads leave every flag False, `interferences()`
   marks the assembly (six reopens on each version). A gearbox saved by 2024 and opened in 2026
   (`probe/cross_version_open_check.py`, `w4-cross-version-2024-in-2026-*.log`): every document reads False
   straight after the open and no file changes; but `QuitDoc` on each such assembly raised a modal "SOLIDWORKS
   CAM Warning: Save changes to <assembly>?" from the CAM add-in. The flag was read only straight after the
   open, not again before the close, so what it read when the prompt came up is not known. The agent running
   the script dismissed each prompt from outside it: a separate Python helper found the dialog's "&No" button
   and posted it `BM_CLICK`; nothing was saved and the files compared equal afterwards. The logs have no trace
   of the dialog (that script has no dialog watcher), and the commit message of `64f4620` calls this "answered
   No by hand". A 2026-made assembly closed by `QuitDoc` in a3 raised none. The app never closes a document,
   so it cannot meet this prompt; a person closing a 2024-saved gearbox in 2026 will. The first 2026 attempt stopped at a script fault
   (a local shadowing the new `marked()`), kept as `w4-workbook-assembly-20261114-053142-stopped-by-a-script-fault.log`.
4. Redraw the four board PNGs. Then W4 can be called closed.

   *2026-11-14: redrawn* (`41b92eb`, `3dd5ec8`).

**W4 was closed on 2026-11-14**, after an independent review of the rerun (its points on the notes and the
scripts are in `eb5dff5`). The reviews of that day found these and left them open; none blocks W4:

- **Whether the assembly still reports needing a rebuild after the top-only route** was never read, and a put
  with its top-only rebuild under `set_rebuild_suppressed(True)` was shown only by the reruns, not by a probe.
  `PUT_NEEDS_REBUILD` is False in `findings.py` but **not established**: nothing may skip a rebuild on it.
  Extra steps for probe `assembly_rebuild_scope` are planned.
- **A journaled file on a drive that is disconnected is treated as gone** (`W4-REVIEW-PASS4.md`). A design call
  for the user.
- Probe `assembly_rebuild_scope`'s own limits, from its review: its "shown" readings could not tell the routes
  apart (every route showed every change), and the failed-rebuild case was tried only on a failing part.

**Known and left:** a journaled assembly (an interrupted build that had got as far as saving the assembly)
forces a whole `_r<n>`, and its layout part and assembly stay in the journal; with two SolidWorks sessions
running, a document left unsaved in the other session cannot be seen.

## W5 in detail

*Rewritten 2026-11-14, after packages A–D.* The authority order is `PLAN-WORKBOOK.md` → `notes-workbook/W5-DECISIONS.md`
→ `W5-PLAN-REVIEW.md` → `W5-PLAN.md`; the shapes the packages share are pinned in `notes-workbook/W5-INTERFACES.md`.

**Probes.** Tier 8 (`probe/p8_motion.py`: `c53bc2d`, `b9ddb12`; results `853e91b`; findings `9aeed80`) passed on
SolidWorks 2026 (75 of 75) and 2024 (31 of 31), every decision the same. Report: `notes-workbook/W5-PROBE-REPORT.md`
(one misstatement: a mate was deleted by "Select2 then EditDelete()", not `DeleteSelection2`). A gear's axis is mated
*coincident* with the layout's shaft axis (concentric is refused); one gear per shaft, the anchor, is held that way and
along the shaft, every other gear on it by a lock mate alone; every gear mate took Flip False in tier 8 (no longer assumed: see *The ring* below); a 12 : 1 train driven
30° turned its output 2.5° the right way. No API drag reproduces a mouse drag: "drag the input" is a person's step, and
the API proof is a temporary driving mate. PLAN-WORKBOOK §4.4 now carries this as a dated note (*Readings changed by
probe tier 8*), and §6's W5 row says "once probe tier 8 has passed".

**Plan and decisions.** `notes-workbook/W5-PLAN.md`, reviewed in `W5-PLAN-REVIEW.md` (M1–M13). The user's answers of
2026-11-14 and the rulings on the review and on P0 are in `W5-DECISIONS.md` and in PLAN-WORKBOOK §4.5 as *Readings
chosen (W5)*: a refused mate stops the build (no static fallback); Update returns a turned train to its built turn
whenever it has to move any gear (the user's words; ruled per train with review M1: only a train it must put is
put back, whole); no datum plane, so an anchor's Front-plane edits need Build again…; a follower's
place along its shaft is an Update; a tooth change that alters a gear mate's ratio is an Update, by the remake
(Build again… only until probe P0b settled the route); W4 static gearboxes stay static; a recorded mate found suppressed is turned back on.

**Probe rounds.** P0 (`0d638db` … `8504856`), P0b (to `4f865d8`), P0c (to `c66d321`) and P0d (to `26cbf9c`) ran on
both versions and were each reviewed; `W5-DECISIONS.md` has a section of rulings for each. What they settled, in one
line each: a tooth change the globals carry is an Update, by deleting the gear mate and making it again
(`GEAR_MATE_RATIO_ROUTE = "remake"`), also on a gear with two gear mates; a train is built and updated under the
top-only rebuild; mates are found by walking the mate group, may sit in folders, and are made under
`CommandInProgress`; a turning Update refuses while a gear is lightweight. Two more rounds followed the first
demonstration's ring fault (`ad08864` … `79e5341`, then `5fcbdc3` … `9afe65b`); see *The ring* below.

**Interface commit** `2f82a0e`, its review's rulings `07fd66a` (`W5-INTERFACES.md` §6). The packages, each reviewed
independently (D's review of 2026-11-14 asked for the fixes now in, below):

- **A — SolidWorks** (`swcom.py`, `swbuild.py`, the fake): `e231ae3` (the train's mate members from tier 8),
  `6ffc84a` (the fake learns mates), `171a50b` (the mate check before the save; a refused mate stops the build),
  `bad8fc8` (Update's motion path); review fixes `3eba2ec`, `39ddf45`, `0459c04`, `885de1c`.
- **B — planning** (`motion.py`, `gearbox.py`, `update.py`): `e39b9d4` (the mates: anchors, locks, gear mates, loops,
  shafts held still), `84db947` (build to turn whenever the findings allow; record what was made or refused),
  `8bb1d86` (classify and finish a turning Update), `0536153` (the turning round trip on the fake), `1b1bb39` (tests
  pin the findings a probe round may change).
- **C — record and sentences** (`store.py`, `ui_text.py`): `e224e2e`, `5c25a1b`, `0110c88`, `bf3202e`.
- **D — window, boards, docs**: `f71c5c4` (the window passes the read's digest to the footer and the record to the
  Build again? question; its tests restored and the W5 states added), `aa9c5f0` (boards), and the docs commit after
  it; after D's review, `fe62c5f` (C's fixed sentences pinned; W4's failure cases on a turning gearbox: an Update
  lost with SolidWorks, one that stops part way, the structural step with Update unsaved) and a docs commit. The
  window needed no new control. `c7770c8` passes the update's finish to its sentence (B's and C's fix for what an
  unsaved Update left). Its two hanging tests hung on a Build again? question no test answered; every
  window test now gets a stand-in that fails at once on an unexpected question. The four tests about W4's
  tooth-change Update run on a gearbox built as W4 built it (`built_w4`); the W5 findings are pinned in the test file.
  New boards: `WorkbookRefused`, `WorkbookTurned`, `WorkbookStatic` (no fallback board: there is no fallback); every
  board after a build is redrawn with the gears mated. Their Update boards use an edit Update carries whatever the
  ratio finding says (G3 and G4 to module 2.5 with S3 X 148.75, G4's At 27 → 30) in place of G2 68 → 69.

**The ring (found by the first demonstration, 2026-11-14).** The first full run passed on SolidWorks 2024 and failed
seven checks on 2026, all one fault: the ring of Risky_Placements turned the wrong way. No Flip can be chosen from the
plan: every toothed ring probed needs the opposite Flip on the two versions, and which one depends on the ring. On
2024 a new ring gear mate made straight after an Update had moved its pinion 2 mm along its shaft needed the other
Flip from one made after the build and a reopen; whether the move, the Update's puts and rebuild, or the missing
reopen caused it was not separated. So the app assumes none. Each gear mate is read
back after it is made (`swcom.gear_mate_sense`: right when `(Reverse == directions parallel) == internal`) and a wrong
one is deleted and made again with the other Flip; one wrong both ways stops the job as a refused mate. Update's
check phase reads every recorded gear mate the same way (a suppressed one only after Update has turned it back on)
and remakes one found wrong. The record holds no Flip. Code: A `a0d5fad`, `6d7172f`, `8ee3c59`, `c2e8489`, `980f10b`,
`b4d4bdd`, `d99654a`; B `7dbc10f`, `7c0eecc`, `f32e744`; C `1df2384`, `17ff636`; each reviewed, the last must-fix closed
in `d99654a`.

**The demonstration (package E), as run.** Scripts `probe/workbook_assembly_check.py` (sections m1 to m8 for W5; a, a2,
a3, b, c from W4), `probe/workbook_window_check.py`, `probe/cross_version_open_check.py`. Every run started a fresh
SolidWorks and used a `git archive` snapshot named in its log's run line.

- *SolidWorks 2026, the full run* (from `9afe65b`; logs `probe/results/w5-*-20261114-163249*`): every section passes
  once m3 and m7 were rerun with a control that drives both Flips (the main log's two FAILs are the old control, which
  assumed the mate still had the first Flip). Window check 21 of 21.
- *SolidWorks 2026, after the last code* (src of `d99654a`; `…-171802.log`, `…-174603-m8.log`, `…-180303.log`): m1,
  m6 with a suppressed mate folder, m8, and m5, a and a3 pass. Those are the sections whose path the commits after
  the full run changed (`W5-DECISIONS.md`, *Rulings at W5's close*).
- *SolidWorks 2024, the confirming run* (src of `d99654a`; `probe/results/sw2024/w5-*-20261114-171802*`,
  `…-174603.log`): m1, m3, m7, m8 and the window check pass. The one FAIL in the `171802` log is an assertion of the
  script whose premise was wrong (that a fresh ring gear mate needs the Flip the recorded one was made with, after a
  move); `7e2135f` asserts it only while neither gear has moved, and the `174603` rerun of m7 passes.
- *m8, on both:* the app itself moves the ring's pinion (G5 At 45 → 47) and then changes the ring mesh's teeth
  (14/36 → 15/37, an Update). The remade gear mate reads back wrong and is turned round, and a drive at the new ratio
  turns the ring the right way, again after a save and reopen.
- *A 2024-built ring gearbox opened in 2026* reads unmodified and no file changes
  (`w5-cross-version-2024-in-2026-20261114-174215.log`). Closing it there raises the SOLIDWORKS CAM add-in's Yes/No
  "Save changes?" box, which ignores Escape; the scripts answer No. The app closes nothing itself.
- *The person's step* (W5-PLAN §4.4): the user dragged G1 by hand in the 12 : 1 on SolidWorks 2026 and on 2024
  (2026-11-14); the train turned as it should on both, closing asked nothing, and the files on disk were unchanged.

The first demonstration's logs (`…-20261114-112629*`) are kept: 2024 1307 of 1307, 2026 with the seven ring failures.
What the runs leave out, with the reasons, is in the scripts' headers (a fixed shaft, a loop-closer, Update on a pair,
an idler's tooth change: no fixture has one; the idler was shown by probe P0c).

**Open, none of it blocking:**

- **The refused `Assem<n>` left open** is named once, in the build's sentence; the window does not track it, so
  neither the footer afterwards nor a close mentions it (UI-DESIGN §9 says so).
- Caveats the reviews asked to be written down and not run again are at the end of `W5-DECISIONS.md` (for example:
  section c takes the app's word that it turned the ring's mate round and does not drive the ring; the remake under
  `CommandInProgress` from wrong to right was a probe step on 2026 only, and m8 is what shows the app doing it on
  2024).
- The app took a +0.3 shifted pinion inside an unshifted ring at the unshifted centre distance, and the build then
  reported a clash (seen by the ring probe; a question for the user below).
- From W4: whether the assembly still reports needing a rebuild after the top-only route (`PUT_NEEDS_REBUILD` not
  established); a journaled file on a disconnected drive is treated as gone (below).
- For the next phase's demonstration: build each fixture once and start later sections from a copy (*Rules carried
  over*).

## W6 in detail

*Written 2026-11-14, after packages A–D (A on a small second pass, A's and B's reviews running).* The authority order
is `PLAN-WORKBOOK.md` → `notes-workbook/W6-PLAN.md` (revised after its review `W6-PLAN-REVIEW.md`, at `eb195d0`; its
*Changes after the review* section says what moved) → `W6-INTERFACES.md`, whose §7 holds the rulings (eighteen so far) on the
interface review that bind the packages. W5's decisions stay in force.

**What W6 adds.** Shafts along `X±`, `Y±` or any direction; bevel meshes between shafts that meet and crossed
helical meshes between shafts that pass each other; speeds about each shaft's own axis; the layout part with planes
for cardinal turned axes and a fixed 3D-sketch line for a slanted one; anchors measured from the base plane square to
the shaft; gear mates between non-parallel axes, read back by a rule probe tier 9 found; the record's schema 4. The
decisions D1–D18 are in PLAN-WORKBOOK §4.5 as *Readings chosen (W6)*, and §4.2 has a dated note on turned axes;
the ones to put to the user first are D1 (one facing per shaft), D4 (if the 3D line fails, slanted axes are refused
in W6) and D16 (a turned mesh is refused before Build while the finding is missing, with no static fallback).

**Probe tier 9** (package P, `turned_gear_mate_sense`, W6-PLAN §7.2): run first, on SolidWorks 2026, while the
packages were written (D6). `8f529f6`, `1b9b281`, `c2fbaca`; results `c0483f3`; findings `11ee1e2`
(`TURNED_GEAR_MATE_SENSE_READ_BACK = "entity senses"`, `TURNED_GEAR_MATE_SENSE_ANGLES = (30.0, 150.0)`) and, after
the tier 9 review's must-fix, `9ac7d6d` (`TURNED_GEAR_MATE_SENSE_ANGLES_SKEW = (60.0, 120.0)`: axes that pass each
other were run only at 60°, 90° and 120°). Both gates read the class of the mesh (`swcom.lines_meet`) and its
range (`swcom.turned_angles`), ruling §7.12–§7.13.

**Interface commit** `34bfb85`, its review's rulings `9d3b43f`, `8200fcb`, `c65cd15`, `92dd04e`, `63c6e65`. The packages:

- **A — SolidWorks** (`swcom.py`, `swbuild.py`, the fake): `11ec034` (`lines_meet`, `turned_angles`), `8b6a080`
  (the turned sense read by rule H, gated per class), `128aa8e` (build and update turned gear mates against their
  planned axes; remake a mesh whose sense moved), `ec85d3e`, `377921a` (W5's ring list dropped once planning passes
  senses), `293fdee` (the fake works a turned mesh's sense out itself; fixture B driven whole). A second pass is in
  hand.
- **B — planning** (`workbook/`): `25d677a` (turned layout, own-axis speeds), `59b196f` (check, refuse and plan
  turned meshes; bevel and turned rows built), `1d14dbd` (the turned refusal asked only with a turned mesh),
  `efe2709` (classify turned Updates, the resense remake, the slanted lines to the worker), `e3ae0ce` (Results rows
  for bevel and crossed meshes; *seen from*), `2d660fa` (the move fix in any parallel family's plane), `f38036e`
  (bevel rows of `plan_parts`), `107c6ea` (a mesh's recorded sense kept on a failed Update).
- **C — record and sentences** (`store.py`, `ui_text.py`): `c2e48b5` (schema 4's refusals), `7657e62` (sense 0 legal
  on a parallel mesh, ruling §7.1), `95c1589` (speeds, the turned refusal, the sense remake), `34ed1c8` (W6's
  structural sentences), `26c6776` (the remake and refusal sentences made true).
- **D — window, boards, docs**: `f88e331` (five later-phase tests re-pinned to a carrier, a sleeve and a slide, since
  W6 builds bevel rows and turned axes), `872e596` (the end view draws turned shafts; the window plans Build parts
  when a turned mesh is refused, which the footer already offered and the press could not run; W6's window tests),
  `cd1c168` (a turned shaft's name kept on the canvas; the Speeds lines wrap at the end view's width so the window
  keeps its own), `34e1238` (boards `WorkbookRightAngle` and `WorkbookCrossed`; `WorkbookError` redrawn, its bevel
  row now an error), and the docs commit after it. The window has no new control (D15), checked from the code: the
  only changes to `workbook_gui.py` since W5 closed are the end view's lines, the Speeds wrap and the parts-only
  plan.

**The two fixtures** (W6-PLAN §5), written as specs in `tests/test_workbook_turned.py`, to be committed as Excel
saves them by E: A, `Bevel_Reducer` (a bevel stage, S1 along X+ into S2, feeding a parallel stage: 6.000 : 1, output at 90°
to the input); B, `Crossed_Slant` (a crossed helical stage, then a bevel stage at 120° onto the slanted S3: 3.000 :
1). Their Checks panels, header lines and speeds are pinned by B. In the window both build to turn on the fake; a crossed
shaft moved to its partner's other side is an Update that remakes the gear mate (D17).

**The demonstration (package E), as run.** `probe/workbook_assembly_check.py` sections r1 to r8 (fixture A,
`Bevel_Reducer`: r1 built, r2 to r4 and r7 from copies or variants; fixture B, `Crossed_Slant`: r5 built, r6 and r8
from copies), `probe/workbook_window_check.py`, `probe/cross_version_open_check.py`. `copy_built` builds each fixture
once and starts the later sections from a copy of the built folder.

- *The first full build on SolidWorks 2026* (2026-11-14; `probe/results/w6-workbook-assembly-20261114-210827.log`)
  found one fault of the app: `swcom.line_axis` asked the sketch manager for `Insert3DSketch2`, which is a member of
  the document; the sketch manager's is `Insert3DSketch`. Fixed in `b3a88f6` (and `0c32b17`), checked step by step on
  SolidWorks (`w6-line-axis-steps-20261114-221843.log`), and the sections that needed fixture B rerun
  (`…-221901-r5-r6-r8.log`). The log's seven FAIL lines are that fault (six) and one fault of the script.
- *The run that closes the phase*, both versions from one `git archive` of `931fe1a`: SolidWorks 2026, every W6
  section (`w6-workbook-assembly-20261114-233518-w6-931fe1a.log`, 1146 checks, none failed); SolidWorks 2024, the
  confirming set r1, r5, r3, r6, r8 and W5's m3 (`sw2024/w6-workbook-assembly-20261114-224626-confirm.log`, 949
  checks, none failed), the window check on each, and a 2024-built `Crossed_Slant` opened unmodified in 2026
  (`w6-cross-version-2024-in-2026-20261114-233432.log`).
- *What only real teeth could show, and did, on both versions:* on every turned mesh the drive matches the plan's
  hand-worked turns, exactly one Flip turns right, the right Flip runs clear and the wrong one clashes with its
  partner alone (142 to 497 mm³), and the app's read-back agrees with the drive on both Flips. Fixture A's bevel mate
  is right as first made; fixture B's crossed mate and its 120° bevel mate are made wrong, read wrong and made again,
  the same on 2024 as on 2026.
- *Also shown on both:* the slanted axis on its line; anchors on the negative side of the Right and Top planes; a
  turned gear mate made again at a new ratio (r3, r6, r8); a quiet Update on a turned gearbox marking no document.

**Left for the user (W6-PLAN §6.1):** drag G1 in `Bevel_Reducer.SLDASM` and watch G4 turn at one sixth, the other
way round as the Speeds panel says. The 2026 build is kept at
`C:\Users\M0obo\Documents\GearGeneratorProbe\w6-full-20261114-210827\out\r1`.

**Caveats the reviews asked to be written down and not run again** are in `W6-INTERFACES.md` §7.21.

## W7 in detail

*Written 2026-11-14 and brought to the close on 2026-11-15.* The
authority order is `PLAN-WORKBOOK.md` → `W5-DECISIONS.md` → `notes-workbook/W7-PLAN.md` (revised after its review
`W7-PLAN-REVIEW.md`, `939b726`, and the spike `W7-SPIKE.md`, `8a798fe`; its §10 lists every change, "After the W8
check" included) → `W7-INTERFACES.md`, whose §6 holds the rulings on the interface review that bind the packages.

**The user's decision, taken before W7:** a carrier is built as **a skeleton only** — a part of axes and planes with
no solid, as the layout part is, free to turn about its own shaft's axis, each planet mated to an axis in it. The app
makes no plate and no pins: that geometry depends on the gearbox at hand and is left to the user.

**The orchestrating session's rulings, taken while the user was away; the user may overrule each** (PLAN-WORKBOOK
§4.5 marks them *ruled*): the first draft's absolute-ratio fallback dropped, since SolidWorks showed it turning the
planets wrong; a gear on the carrier's own shaft built, locked to the carrier, because W8's transfer case needs one,
and refused if it meshes; no fix offered on a planetary mesh; every planetary form W7 does not build refused as an
error, not left for a phase; and J5's gear mates as below (`W7-INTERFACES.md` §6.14).

**What W7 adds.** One simple planetary stage per workbook: a sun, a ring and a spur planet gear on a planet shaft
`Mounted on` a carrier, with any number of `Copies`, every shaft of the stage along Z+ or Z− facing the carrier's way,
exactly one member held and one the input; beside it, W5's trains, other frame shafts on the carrier's axis, and
gears on the carrier's own shaft locked to it (J8). Copies placed in the carrier's frame (J4) and phased so every
copy meshes at once; the assembly condition and the room round the carrier as errors; speeds with the carrier term
and torques with the held member's reaction; the carrier part (`<Name>_<C>_Carrier`); the gear mates (J5, by
default, which the user may overrule): one for each sun mesh, so one per copy, and exactly one with the ring, from
copy 1, chosen by member and not by the order of the Meshes sheet's rows; Update's puts held member first, carrier
next (J15); schema 5. The readings J1–J20 as revised are in PLAN-WORKBOOK §4.5, *Readings chosen (W7)*, with notes
under §3.3, §3.5 and §4.2. Everything else that reads as a planetary is **refused as an error of the workbook** at
its cell: a differential, two inputs on a stage (whether or not their speeds agree: §6.15), a compound or double
planet, a gear on the carrier that meshes, a helical planetary, members facing different ways, a carrier on a
carrier or off Z±, a second carrier — each listed for the user as something a later pass could open.

**The spike** (`w7_planetary_spike` in `probe/p8_motion.py`, results `probe/results/w7-spike-20261114-192709.*`, on
SolidWorks 2026 only): a gear mate between a carrier-borne axis and another turns its gears relative to the line
between their axes, so in a planetary relative to the carrier; the plan's mates turned the 4 : 1 right (sun 30°,
carrier 7.5°, each planet −15°, ring still, no interference); the ring mate read back wrong with Flip False and right
remade. The first draft's kinematic fallback turned the planets wrong and is gone.

**Interface commit** `5d5d51d`, its review's rulings `abca489`, `541585b`. The packages:

- **A — SolidWorks** (`swcom.py`, `swbuild.py`, the fake): `75d089b` (the carrier part built and updated; a planetary
  train put back in order), `f1395ae` (a held gear joined by its gear mates; the stages the drive had not covered),
  `7a34852`; after the run, `9f21d99` (the put with the gear mates off). Reviewed.
- **B — planning** (`workbook/`): `366ff42` (lay out, solve and check a stage), `5146b75` (the carrier part, mates and
  build; the carrier on record), `42fbe29` (Update's classification of a stage), `4700a3e` (the Results sheet: a
  planet's speed on its carrier, a held member's torque), `a22369f` (every fixture driven on the fake after its build
  and each Update), then the review's points (`6ed3439`, `765c2ca`). Reviewed.
- **C — record and sentences** (`store.py`, `ui_text.py`): `efe47a2` (schema 5's refusals), `f81fec5` (the carrier id
  suffix in the store), `0e8df59` (a stage's words: carrier, copies, speeds), `ff57941` (the refusals whole, with
  Build parts offered), `60f2fbe` (a carrier part's moved planets after Update), `cc106e5` (the review's points on the
  record and the Speeds panel).
- **D — window, boards, docs**: `c37c1e7` (the later-phase tests re-pinned to W8's rows; a carrier builds),
  `bac9eef` (the end view's carrier circle through its planets, the torque note in prose, the window tests of every
  fixture), `d650e0f` (boards `WorkbookPlanetary`, `WorkbookPlanetaryCopies`), and these notes; then the review's
  points: the carrier's axis and the Speeds panel's prose rows asked of `geometry.carrier_axes` and
  `ui_text.speeds_prose_rows`, names on a shared cross in the Shafts sheet's order (`S, C, R`, as the Speeds panel)
  and every end-view name on a plain backing (every Workbook board redrawn), a 4 : 1 off the origin in the tests,
  two inputs among the refused kinds.

**The fixtures** (W7-PLAN §4), as B's `tests/test_workbook_planetary.py` writes them: `Planetary_4to1` (the ring
held, sun in at 1000 rpm, carrier out, three copies, `CarrierGear` on the carrier: 4.000 : 1), the sun held (1.333 :
1), the stage on Z−, the carrier held (3.000 : 1, the other way).

**The demonstration, as run** (package E, `probe/workbook_assembly_check.py` sections p1 to p7; W7-PLAN §6). Every
number below is SolidWorks' own reading, judged against the plan's hand-worked turns.

- **The 4 : 1 built through the app turns right** (p1): the sun's +30° gives the carrier and CarrierGear +7.5°,
  every copy −15°, the ring 0, to about 1e-13°; all six meshes stay in step, the two ring meshes with no gear mate
  among them; no interference as built, at three other phases, or driven. A wrong Flip clashes (about 50 mm³ at each
  planet–ring mesh). The carrier part has no solid body, and each copy's axis passes through its copy's centre to
  2e-9 mm.
- **The other stages** build, drive and reopen: the sun held (p5: carrier +22.5°, planets +45°), the stage on Z−
  (p6), the carrier held (p7: ring −10°, planets −30°), four copies (p4). A second planet–ring gear mate (p2, never
  saved) was logged as facts only.
- **Update** (p3): after a turn of 37° on the sun and an edit, the whole train goes back — the carrier first, or the
  held ring first when it is off — and a tooth change to 3.714 : 1 remakes its four gear mates and turns right
  (carrier +8.077°).
- **The one app fault the run found, and its fix.** The first full run (snapshot `39ecf66`) stopped in p3: the
  carrier's put did not hold while the train's gear mates were on (ruling 13's unshown assumption). The probe
  `planetary_put_back` (tier 10, `probe/p10_planetary.py`, results `w7-planetary-put-20261115-012409.*` and its
  follow-ons) tried four routes on SolidWorks 2026; the one that held is **every gear mate of the train and its
  locks suppressed around the puts**, then everything turned back on (`findings.PLANETARY_PUT_ROUTE`). A's `9f21d99`
  does that for a train with a carrier only; a train without one makes the calls it always made (468 call sequences
  on the fake compared identical). `5fcaa6a` then keeps a per-mode gear mate off through such a put (W8's path).
- **SolidWorks 2024, the confirming build** (log `w7-2024-20261115-020234-p1-p5-p3-step1.log`): p1, p5
  and p3's put-back pass. One difference, handled by the read-back as everywhere: on 2024 the planet–ring gear mate
  turns right as first made, on 2026 the build turns it round.
- **The window** ran through its boards on 2026 (`w7-window-20261115-015017.log`): the planetary builds with its
  carrier part, its footer says to drag Sun, and five copies give the assembly-condition error with Build not
  offered.

Logs: `probe/results/w7-workbook-assembly-20261115-000138-*.log` (the first run and the regression of W6's and W5's
sections, all passing, on `39ecf66`), `w7-put-fix-20261115-014257-p3-p4.log`, and the two named above (on `9f21d99`).
The closing run, from one archive of HEAD `08fd712` (which holds `5fcaa6a`), on SolidWorks 2026:
`w7-close-20261115-021540-p-r-m.log` — p1, p2, p5, p6, p7 again, and the W6 and W5 sections that press Update (r1 a
quiet Update, r2 a turned train put back, r3 a ratio remade, m8 a move and the ring mate remade, m5 a lost Update
pressed again), all passing: the review of the evidence asked for it, since `db4d4e3` and `ccb05ae` had changed
Update and the sense read for every gearbox after the first run.

**Caveats at the close** (`W7-INTERFACES.md` §6.17 has them in full): the put order is logged from the app's own
result, SolidWorks confirming the frames after the puts; in p7 a wrong Flip lands every gear a whole number of
pitches off, so there the right sense rests on the frames, not on a clash; 2024 ran p1, p5 and p3's first step
only; a gear mate remade inside the suppression (a tooth change on a planetary) is read when remade and not again
once turned back on; `Planetary_4to1.xlsx` as Excel saves it is not committed (no test or script reads it).

**Left for the user:** open `Planetary_4to1.SLDASM` in the built folder
`C:\Users\M0obo\Documents\GearGeneratorProbe\w7-full-20261115-000138\out\p1` and drag Sun by hand: the carrier
should follow at a quarter of the turn with the planets rolling between sun and ring. Close without saving.

**Open:**

- `assess.lay_out_refusal`'s *"The gearbox cannot be laid out yet, since it is not checked: …"* is reached by no
  input found: `Report.unchecked` is set only from `planetary.not_laid_out` (a carrier riding a carrier, a planet
  across its carrier), and `planetary.refusals` says each of those as an error at its cell under the same
  conditions, so `build_refusal` answers first.

## W8 in detail

*Written 2026-11-15, while packages A, B and C land their passes.* The authority order is `PLAN-WORKBOOK.md` →
`W5-DECISIONS.md` → `notes-workbook/W8-PLAN.md` (revised after its review `W8-PLAN-REVIEW.md` and after the spike
`W8-SPIKE.md`, with its follow-up and its SolidWorks 2024 rerun; *Changes after the review* and *Changes after the
spike* list every change, and where they differ the second wins) → `W8-INTERFACES.md` (interface commit `e9efab9`),
whose §9 holds the rulings on the interface review that bind the packages.

### How W8 closed (2026-11-16)

**W8 is closed but for three things:** the built footer on a screen shorter than the window asks (cut off; open, K12
of W9), the person's step `s6`, and the two hand drags of W6 and W7. The record below this block, from *What W8
adds* on, is kept as it was written day by day; where it and this block differ, this block is the later word.

**The closing run** (`W8-REVIEW-CLOSING-RUN.md`, `ec14e4f`): one `git archive` of `c583f48` in one run folder,
`C:\Users\M0obo\Documents\GearGeneratorProbe\w8-close-sw2026-20261116-001758` on the third device, its
`SNAPSHOT_COMMIT` in every log's head, run as five invocations, each in a fresh SolidWorks 2026 34.1.1 session
exited after (the window check's log names no revision; its commit message does):

| commit | sections | checks | result |
|---|---|---|---|
| `c351b1f` | `s0`, `s1` (kept as `s1.master`), `s3` | 517, 555, 409 | 0 failed |
| `8fd13c9` | `s4`, `s5` | 1864, 16 | 0 failed |
| `c2eed05` | `s2`, `s7` (every case) | 603, 154 | 0 failed |
| `aff9bfe` | `r1`, `r2`, `r3`, `m5`, `m8`, `p1`, `p3` | 152, 96, 128, 73, 141, 236, 290 | 0 failed, W7's close's counts but p3's (built from a copy, not fresh) |
| `fb85bcc` | the full window check, W4's to W8's stages | — | 1 failed: the built footer's height |

`s2`, `s4` and `s7` copied the first group's `s1.master`. Five invocations rather than one `--only modes`, because
`--only modes` then put `s5` after `s2`, and `s5` builds fresh and was to run before the copy sections; `W8_ORDER`
now puts it first of them. Every NOTE was SolidWorks' untitled notification box, exempt. No STOP.

**What it read** (ruling 9.18, `findings.py`'s comments, the pins in `tests/test_findings.py`): on 34.1.1 `s2`'s
current sequence (4H, N and 4L shown after the fresh turn, then the press in 4L) and every `s7` case read a turn in
every mode, and `s2` read 2H's put not carried to 4H and N, as 2024's `s2` and both case 8s read. 34.0.0's own first
press read the same; its one differing reading came from a sequence (4L alone shown before the press) that nothing
has re-read. It is recorded as unexplained and **not pursued** (the coordinator, 2026-11-16): the app does not depend
on it. The changed Update's put of FDrive in 2H found in 4H and N and not in 4L recurs on 34.0.0, 34.1.1 and 2024; it
is recorded as read. `s7` case 5 on 34.1.1 read what 2024's did, and case 7 read a suppressed coupling's sense right,
marking nothing, on both versions. No finding's value changed.

**Rulings taken at the close by the coordinating session, dated 2026-11-16, each for the user to overrule:**

- **The window check's one failure** (`W8 built: the footer whole … its bottom at 1657 of 1570`, on this device's
  2560 × 1600 screen at 150 %; the same on SolidWorks 2024 and 2026; by the code a 1920 × 1080 screen at 100 % would
  be cut too, inferred, not measured): **W8 does not change the app for it.** It is carried into the next phase as
  K12 of `notes-workbook/ISSUE-1-PLAN.md`: the window stops at the screen's work area and its two columns scroll
  between a fixed header and footer, and the window check asserts the footer whole on this device. UI-DESIGN §9
  says what the window does today on such a screen. W8-PLAN §6 item 4's "the window check pass(es)" is met but for
  this one check.
- **The three mode boards** (`WorkbookModes`, `WorkbookModesBuilt`, `WorkbookModesUpdated`) are **not redrawn now**:
  W9 redraws them with K12 and its new footer words. Checked against the app's sentences today, their words are
  right for the states they draw; the one sentence change since they were drawn (`0ff56d3`) is said only after an
  earlier unsaved Update, which no board draws. Only the 1 % text width between hosts (*W8 picked up*, first bullet)
  stands against them.
- **`s5`'s status-5 path** (SolidWorks refusing the coupling at the make) has no SolidWorks run on either version:
  SolidWorks accepted the doctored coupling both times and the build's step 6 caught it. It stays covered on the fake
  only, a caveat, not run again (ruling 9.19, which also writes down `s5`'s other two departures from W8-PLAN §5).
- **34.0.0's own `s2` sequence** is not re-read on any version and not pursued (above).

**W8-PLAN §6, item by item:** 1 to 3 met earlier; 4 met but for the footer's height (above); 5, the person's step
handed to the user with the readings J1–J27 (*Questions waiting for the user*, item 5, and *Open, for the user to
overrule* at the end of this section); 6, the documents: PLAN-WORKBOOK §4.5 (*How W8 ended*) and §6 (dated notes),
UI-DESIGN §9 (*The layout* and *Modes*' last words), this table's row and this section; the boards as ruled above;
the macro database is the user's to update (GOTCHAS §83 against 2026's reading: *Questions waiting*, item 8).

**The two reviews' points, each done or answered** (the records and comments in `782d774`, the rest with this note):

- `W8-REVIEW-SW2024-CONFIRM.md`: **S1** done (the `SUPPRESSED_GEAR_MATE_SENSE_READ` comment in the review's words,
  with the closing run's 34.1.1 read beside it; `swbuild.py`'s "as SUPPRESSED_GEAR_MATE_SENSE_READ does" dropped;
  a pin on both JSON files). **S2** done (the 2024 bullet says the two `s2`s ran different sequences). **S3** done
  (2024's `s2` lines in `findings.py` and ruling 9.18). **S4** answered: the missing snapshot and the unlogged
  revision are recorded (the dated paragraph at the top); logging the revision in the window check is left for a
  reviewed script change. **S5** done (the W8 row). **S6** done (the ruling above; UI-DESIGN and this note say a
  1920 × 1080 screen at 100 % would be cut too, inferred). N1 to N4 taken in the 2024 bullet and *Left*.
- `W8-REVIEW-CLOSING-RUN.md`: **M1** done (s6 reworded as a dated note in W8-PLAN §5; both E4 folders given back as
  `s1` by hand, below; the steps in *Questions waiting*, item 5). **M2** ruled (above). **S1** done (`findings.py`,
  ruling 9.18, PLAN-WORKBOOK §4.5's J11 note, W8-PLAN's two dated notes, `ui_text`'s comment, the handoff; a pin on
  the closing `s2`). **S2** done (ruling 9.19; W8-PLAN §5's `s5` annotated; "names the bodies, not the mate" on the
  list to overrule). **S3** done (as above). **S4** done but for one part: the probe's docstring corrected and
  `W8_ORDER` puts `s5` before the copy sections (nothing else reads the order); `give_back_r1` does not give back
  `s1`, and is not changed here (a probe change with no run to show it): the next run that builds an E4 for a person
  should add it, with a W8 person-step line. **S5** done (*Questions waiting*, item 5). N1 and N3 done; N2 recorded;
  N4 in the suite paragraph; **N5** (the probe labels each mode's judgement on showing "post-check of …") not done:
  rename it when the probe is next touched.

**The folders handed to the user (made ready 2026-11-16, no SolidWorks started).** The probe leaves a built E4 as
`out\s1.master`, whose record and `.gear.json` files name `out\s1`; `give_back_r1` renames only r1 and p1 back. In
both run folders the E4's `s1.master` was renamed back to `s1` by hand, the same plain rename the script makes for
r1 and p1, with nothing open (no SolidWorks, no Excel running), and every path in the records then read back as an
existing file (10 of 10 in each): `…\w8-close-sw2026-20261116-001758\out\s1` (built on 2026 34.1.1) and
`…\w8-sw2024-20261115-223821\out\s1` (built on 2024 32.5.0, at `0e7f203`, whose app source differs from `c583f48`
in comments only). The hand drags' folders are the closing run's `out\r1` and `out\p1`, given back by the script
(built on 2026 34.1.1).

**What W8 adds.** The `sleeve` and `dog` kinds (the strip's ring and spur teeth, `gears/clutch.py`, never offered by
the strip), gears that slide (`Slides`) on frame shafts along Z±, and the Modes sheet: each mode places every slider,
what it engages is worked out (a sleeve covering a dog's whole face couples their shafts), and speeds, torques,
ratios and checks are per mode. Build makes one configuration per mode, named as the mode, the first Modes row the
one the assembly opens in; one distance mate per slider with a value per configuration; each coupling and each
spline a 1 : 1 gear mate between collinear axes, settled by the read-back, a coupling switched on only in the modes
that engage it. Update works across the configurations (W8-PLAN §1.10). The record's schema 6. W8 was the last phase
of the import as planned on 2026-11-11; W9 (issue #1) builds on it and leaves no row waiting for a phase, and what
this version does not build is an error naming no phase. The readings J1–J27
as revised are in PLAN-WORKBOOK §4.5, *Readings chosen (W8)*, with a note under §3.4 and one under §6.

**The orchestrating session's rulings, taken while the user was away; the user may overrule each** (PLAN-WORKBOOK
§4.5 marks them *ruled*): the sleeve and dog as toothed rings with **no fork groove, hub or chamfers** (J1) and at
the Box's **20° by default**, not canvas E4's 30° spline, which the strip's full-depth teeth would make a 0.022 mm tip
(J2); the collinear gear mate (J8); **a slide as one distance mate with a value per mode** (J7, after the spike);
**one configuration per mode** (J10); a Modes edit that needs no new mate is an Update (J14), but **one that would
leave a coupling or sliding mesh on in no mode is Build again…** (W8-INTERFACES §9.1); **a coupling between shafts
facing opposite ways is refused until one has been shown** (§9.3); every quiet Update of a gearbox with modes says
which mode it worked in and that it did not show the others (§9.11). J16 departs from PLAN-WORKBOOK §3.4's warning
and is announced as such. W8-PLAN §0.4 puts J1, J2, J16, J14 and J11 at the top of the list for the user.

**Measured by the probes, not yet by the app:** **positions are kept per configuration** (a turn the user gives in
one mode stays in that mode, J11) and **a put holds in the configuration shown only** (so Update puts mode by mode,
J26). The W8 spike's follow-up measured both on SolidWorks 2026, and its rerun on 2024 measured the same, against
what GOTCHAS §83 recorded for a free mechanism (the findings are committed in `ea7a46f`). No W8 code had run on
SolidWorks yet (so on 2026-11-15; it has since: *How W8 closed*): the spike and its follow-up, on both versions,
were all W8 had shown there. What the app says about a turn follows the running version's finding
(`swcom.positions_per_configuration`), and makes neither claim where it is unsettled or after a restart.

**The window (package D).** The **mode chooser** in the Speeds panel's header — the window's first new control since
W5, drawn on the board first (`WorkbookModes`) — one segment per Modes row, the first chosen, kept across re-reads
while a mode of that name is there. It chooses which mode's speeds and end view *the window* shows; it does not
switch SolidWorks' configuration and clicking it sends nothing to SolidWorks, and a grey line at the panel's foot says
so (`ui_text.mode_chooser_note`). The end view draws each slider at the chosen mode's place: a slide runs along the
view, so a sleeve over a dog is drawn in that dog's face colour. Every end-view name now stays on the canvas, clear
of the names placed before it where a side allows, and a name many coaxial shafts share breaks onto lines. The
footer passes the last job's `positions_per_configuration` to C's sentences (§9.12). The strip refuses a sleeve's or
dog's `.gear.json` with C's sentence (W8-PLAN §1.1, review S9), at Open .gear.json, the only way a record reaches
the live link's Update values.

**For the user to look at:** the mode chooser — `design/renders/WorkbookModes.png` (the E4 transfer case, on 4L) and
`WorkbookModesBuilt.png` (TransferCase_Parallel built, on 2H), and UI-DESIGN §9, *Modes*, which says why it exists
and what it does not do; and the readings above.

**Packages so far** (`git log e9efab9..`): **P/E — probes and logs** `ed81031`, `eca568d`, `bdc4c50` (the spike and
follow-up on 2024); **A — SolidWorks** `6a54fb1`, `3ea4d87`, `a6c04cc`, `d872ca5`, `f9a8cae` (the build's mode phase,
the build gate lifted), `39ecf66`, `db4d4e3` (Update across configurations); **B — planning** `120192d` (the sleeve
and dog kinds), `bb1a946`, `73e3ebe`, `33b28b3`, `124df33`, `f0417a7`, `7fbc56c`, `a13dd18`, `6669717`, `7124394`,
`0ea5cc1`, `a25f9be`, `0665c40`, `bdefb90`; **C — record and words** `d005549`, `5bf7825`, `131bcd2`, `0f1defd`,
`5a49a04`, `4f1e1bd`, `3b1bcc1`, `634f37c`; **D — window, boards, docs** `2b45315` and `e23f41e` (the later-phase tests re-pinned: no real kind waits now, the channel tested with a dog made a made-up W9's), `33c4729` (the chooser, the end view per mode, the footer's claim, the strip's refusal), `527f65e` (boards `WorkbookModes`, `WorkbookModesBuilt`) and these notes.

**The fixtures** (W8-PLAN §2, `tests/workbook_fixtures.py`): **TransferCase_Parallel**, the low range on a reverted
layshaft (17 : 34 twice at 51 mm), every shaft a frame shaft — W7-free, built first as the shakedown; and the **E4
transfer case**, E3's 4 : 1 planetary as the low range. Modes 2H, 4H, N, 4L for both: Rear 1500 / 1500 / free / 375
rpm, Front free / 1500 / free / 375.

**What the demonstration (package E) still has to show** (W8-PLAN §5), on SolidWorks 2026 and then one confirming
build on 2024: TransferCase_Parallel built through the app as the shakedown (the sleeve and dog kinds' own parts
first), then the E4 transfer case; each mode's configuration, slides at their values, couplings on where they
engage, driven per mode with the both-Flips control; interference per mode with a half-pitch control; Update across
modes (an inactive configuration's value and flag set back, a J14 edit, a turn in one mode left alone by an Update in
another); and the window through these states. Sliding gears are tested against the fake only: neither fixture has
one.

**Where W8 was paused (2026-11-15, the user's call, to keep usage down).** Every package is written and reviewed,
and each review's points are in: A (`6a851c2` the slide's dimension reached as the probes reached it, `ccb05ae` and
ruling 9.16, `5fcaa6a`), B (`13043de` the frames each mode hands the build pinned from the teeth, `89f143b` and
ruling 9.17, `e56e892`), C (`45479ea`, `295a214`: the Gears table's states shortened to fit their column — "same as
G1", "changes on Update", "new part on Build"), D (`22d0dce`, `14d1125` the window back at 1080 px with modes and
every mode name whole, `93708d6` the boards redrawn as the window draws). The suite is green. No W8 code had run
on SolidWorks then (it has since), and the findings were set, so the app WILL build a gearbox with modes there: treat it as unshown.

**W8 picked up (2026-11-15, the second host; the coordinating session with Opus subagents, each step reviewed
by a separate one, every commit pushed as it lands).** The list under *To pick W8 up* below is kept as it was written;
this paragraph says what has been done of it.

- **The late passes were reviewed** (item 3 below): C's and D's in `notes-workbook/W8-REVIEW-LATE-CD.md`, A's
  `5fcaa6a` in `W8-REVIEW-LATE-A.md`. The suite was NOT green at `fa4e508`: one window test failed under Windows
  Python, because `c29ea2e`'s finding (a suppressed gear mate's sense is read) took a sentence out of a quiet Update
  that a test, a board and UI-DESIGN still showed. Fixed (`08318d7`), with the chooser's dead trace (`a4ae910`) and
  the Speeds header's room (`b12838d`: the chooser now gets the room the header leaves beside its readout, 172 px
  beside "seen from +Z" and 91 px beside a turned shaft's readout at 100 %, at most 200 px — so 2H 4H N 4L goes to
  rows whenever a shaft is off Z; no board draws that yet). Their review is `W8-REVIEW-FIX-CD.md`, its points in
  (`34e48b5`, `7e6c09d`, `4c233b2`). The redrawn `WorkbookModesUpdated.png` stands; this host draws text about 1 %
  wider than the host that drew its neighbours, so the three mode boards should be redrawn together next time.
- **A's fixes from that review**: a carrier train with modes is put back through the measured per-configuration
  suppression, and every per-mode mate's flag is read in every configuration after Update's mode loop (`c14e1b2`);
  E4 through a changed Update on the fake (`ff1c4dd`); a gear mate lost inside a planetary's put is said gone, not
  "left suppressed" (`c48b6ef`, `963eac4`). Reviewed in `W8-REVIEW-FIX-A.md`. Item 4 below (a gear mate remade inside
  a planetary's suppressed put is not read again) is **left as a caveat**: W7's p3 showed the case on 2026, W8 never
  remakes, and the gap is 2024.
- **The first build on SolidWorks found one app fault**, fixed: `IFeature.IsSuppressed2(3, names)` answers in the
  document's configuration order whatever order the names are passed in, and the app paired the answers with the
  order asked, so a build refused itself on flags it had set right
  (`probe/results/w8-workbook-assembly-20261115-091456-s0-stopped-by-an-app-fault.log`,
  `w8-configuration-order-20261115-092100.txt`). The app asks one configuration per call since `03a4e51`; an answer
  that is not a flag is a sentence (`2d8fb47`).
- **Probe tier 11** (`src/gear_generator/probe/p11_modes.py`; W8-PLAN §4.2 item 1, which the plan called
  `p9_modes`; results `probe/results/w8-over-defined-20261115-100312.*`, SolidWorks 2026 34.0.0): a configuration
  whose two slides fight shows with no window that asks; a non-modal "Over Defined" balloon tip came once and stood
  at least about 2.3 s; both slides read code 47 and the app's mate check names them; the configurations shown after
  it solve. A coupling beside a lock across the same pair reads **no error at all** (left as a caveat: no path of the
  app makes that pair). Findings `CONFIGURATION_SHOW_OVER_DEFINED`, `SUPPRESSION_READ_ORDER`, `VALUE_READ_ORDER`
  (`a75c617`, comments corrected in `6f35d33`). Reviewed in `W8-REVIEW-TIER11.md`, which also found that **Update
  refused a mate it did not make only when it was on in the active configuration**; since `d2f492e` it reads such a
  mate in every mode and refuses before showing anything. The two new findings gate a gearbox with modes (`f87ecc3`,
  `0c49d24`). Tier 9 item 2 of §4.2 (the copied folder) was already W6's `copy_built`.
- **Package E, `s0` and `s1`** (`probe/workbook_assembly_check.py`, `--only modes`; the script reviewed in
  `W8-REVIEW-DEMO-S0-S1.md`, every point in before the run): both pass on SolidWorks 2026 34.0.0 from a snapshot of
  `31f5966` — `probe/results/w8-workbook-assembly-20261115-102101-s0-s1.log`, s0 517 checks, s1 555, 0 failed, no
  STOP. Each mode's flags (the app's read and a raw read in document order, against §2.3), slides, frames, mates,
  interference, a clash control on every mesh and every dog in every mode, the driven proof per mode against the
  key, the both-Flips controls in 4H and 4L (exactly one Flip right, the read naming it), reopen. Facts: every
  coupling was first made with Flip False, read wrong and remade with True on this host (the spike's host had it
  right with False); the drive's global link was accepted with four configurations, so the script's value route
  never ran. Two NOTEs, both the same untitled SolidWorks notification box (texts 'Title', 'Description',
  'Button1', …) coming up mid-run, unanswered: ruled a notification, exempt whenever it appears.
  `s1.master` is in `C:\Users\M0obo\Documents\GearGeneratorProbe\w8-s0s1-20261115-095232\out2\s1.master`.
- **Package E, `s2` to `s5`, `s7` and the window stage, on SolidWorks 2026 34.0.0** (the script reviewed in
  `W8-REVIEW-DEMO-S2-S7.md`, its points in with `7c9634d`):
  - `s3` 0 failed (`probe/results/w8-workbook-assembly-20261115-114929-s3.log`): D10 per configuration, the refusal
    of a mate the app did not make in one mode word for word with the call trace, a listed mate left as it is, an
    exploded view, a mode deleted in SolidWorks sending the user to Build again….
  - `s4` 0 failed (`…-120522-s4.log`, `ee4ba90`): three Updates, J14, the `_r2` revision with five configurations.
  - `s2` 0 failed at `4871a85` (`…-151412-s2.log`, `bdfa870`), after two stopped runs kept beside it
    (`…-111951-s2-turn-carried-per-body.log`, `…-132348-s2-put-kept-per-configuration.log`). See *Positions across
    configurations* below.
  - The window check's W8 stage (`--only w8`) 0 failed (`w8-window-20261115-150900.log`, `4871a85`); the check now
    ends on any Tk callback failure, writes its log line by line and has a 15-minute watchdog (a run had hung 46
    minutes on a callback error with nothing written).
  - `s7` ran once (`…-135401-s7.log`, `w8-s7-20261115-135428.json`, `725566e`) with five failures that were the
    script's; since fixed, **not rerun on 2026**. `s5` ran once (`…-140811-s5.log`, `148bac1`): the gate refuses the
    doctored distance mate; SolidWorks accepted the doctored Sun–LoDog coupling, which the build then catches at its
    step 6 (the plan's `AddMate5` status-5 path is covered on the fake only); one FAIL against an expectation since
    corrected, **not rerun**.
- **Positions across configurations (ruling 9.18, `W8-INTERFACES.md` §9; the day's hardest point).** The spike's
  finding said positions are kept per configuration. `s2` showed that a hand turn of the mated train is not: it
  showed in other modes, so a dog could stand across its sleeve there. The finding is split
  (`POSITIONS_PER_CONFIGURATION_ON_<year>`, the put fact, read by nothing; `TURN_PER_CONFIGURATION_ON_<year>`, read
  by `swcom.positions_per_configuration`, False on 2026). The Update now: a quiet Update that has anything to put
  puts every train in every mode back to the built frames (`a87c1c5`; 52 puts on the E4, about 15 minutes on 2024 on the second host, about 9 on the third device),
  and a mode found turned in step is put as one found out of step (`baa1a56`); every mode shown is post-checked.
  The sentences say a turn **can** show in other modes (`5989c7d`), not that it does. **Read on 2026 34.1.1 and
  on 2024; one 34.0.0 reading stays unexplained:** in `s2`'s 34.0.0 log (`…-151412-s2.log`) a fresh turn in 2H, after an Update had put every mode, read in 4L,
  yet 4H and N were then found at the built turn — either the turn did not reach them or 2H's put did. `s7` case 8
  alone, run on 34.1.1 (2026-11-15, another device; `fe74276`, after `s1` built there, 0 failed:
  `probe/results/w8-workbook-assembly-20261115-220745-s1-s7-case8.log`, `w8-s7-20261115-222252-case8.json`), read
  neither: after the app's quiet Update in 4L had put every mode (every configuration then at its built frames), a
  fresh +37° in 2H read in all four by the same amount, and the moving put in 2H after it stayed in 2H: 4H, N and
  4L still stood at the fresh turn, through a save and reopen — what 2024's case 8 read. In that Update, after its put in
  2H, 4H and N still showed the first turn. Then W8's closing run on 34.1.1 (2026-11-16, `c2eed05`) ran `s2`'s
  current sequence, which shows 4H, N and 4L between the fresh turn and the press (`7c9634d`), and read what 2024's
  `s2` and both case 8s read: the turn in every mode shown, 2H's put not carried; and every `s7` case read the turn
  in every mode. The 151412 sequence showed 4L alone before the press; it has not run again on any version, and on
  34.0.0 itself the first press, made after every mode had been shown, read the same as 34.1.1 and 2024 (lines
  224-227). So 34.0.0's one differing reading came from a sequence nothing has re-read and stays unexplained; it is
  not pursued (the coordinator, 2026-11-16), since the app does not depend on it. One reading against the put fact
  recurs: the changed Update's put of FDrive in 2H was found in 4H and N and not in 4L on 34.0.0, on 34.1.1 and on
  2024; it is recorded as read, and nothing is built on it. The findings keep their values (`TURN_PER_CONFIGURATION_ON_2026` False,
  `POSITIONS_PER_CONFIGURATION_ON_2026` True); their comments and ruling 9.18 say this. The app does not depend on
  the answer (`W8-REVIEW-LATE-FIXES.md` walked every path: the one state where a mode can stand wrong under a green
  status is the quiet Update that puts nothing, whose status says it did not show the other modes).
- **SolidWorks 2024 (32.5.0), the confirming build: every section in, one window failure for a ruling** (results
  under `probe/results/sw2024/`; a fresh session per section, exited after each). *On the second host* (run folders in
  `C:\Users\M0obo\Documents\GearGeneratorProbe\w8-sw2024-20261115` there): `s0` 0 failed (`29e6c34`);
  `s1` 0 failed at `48ab0aa` (`bb79b6f`); `s7` at `1560b25` 1 failed, the script's own put order in case 8
  (`8702389`), and case 8 alone 0 failed at `8702389` (`6b16963`). Read on 2024: a turn showed in every
  configuration in every state tried, case 8's included; a moving put stayed in its configuration; a body driven
  in one configuration left its meshed neighbour at the same place in every configuration, not moved by the same
  amount; a turn in N overwrote 4H's earlier moving put. `8702389`'s message overstates "the readings match
  2026's" (case 4 as redesigned and case 5's drive have no 2026 run yet; case 8 ran on 34.1.1 since).
  `TURN_PER_CONFIGURATION_ON_2024` is set False from these (`ce775a6`). `s7` case 7 there also read a suppressed
  gear mate's sense on the copy as opened, unmodified (`RangeSlv engages LoDog`, suppressed in 2H): it answered right
  (τ +1, +1), as the mate left on did, and no document read modified before or after — what
  `SUPPRESSED_GEAR_MATE_SENSE_READ` says of 2026 (`sw2024/w8-workbook-assembly-20261115-162357-s7.log`; the
  finding's comment says so since the close, and a pin holds it).
  *On the next device* (2026-11-15 night, run folder `C:\Users\M0obo\Documents\GearGeneratorProbe\w8-sw2024-20261115-223821`,
  one `git archive` of `0e7f203`, which has `ce775a6`; its logs name no snapshot, since no `SNAPSHOT_COMMIT` was
  written beside the archive, so `0e7f203` is the commit messages' record): `s1` again to make this device's `s1.master`, 555 checks, 0
  failed (`233e03d`); `s3` 409 checks, 0 failed (`b6bb186`), read as 2026 read it at `e670e7e`, so the first `s3`
  anywhere on the current Update (`a87c1c5`, `baa1a56`); `s2` 603 checks, 0 failed (`eae38c9`), each Update that
  puts 511-521 s (52 puts; 210-238 s on 2026 34.0.0), the section 43 minutes. In
  `s2` the fresh +37° in 2H read in 4H, N and 4L alike, and the Update in 4L after it found 4H out of step at
  ModeSlv–FrontDog and N turned when it showed them after 2H's put, as in its first quiet Update: the turn reached
  every mode and 2H's put did not carry to the others. That is what 2024's and 34.1.1's case 8 read; 34.0.0's `s2` had
  found 4H and N at the built turn there. (34.0.0's `s2` showed 4L alone between the fresh turn and the press; this
  `s2` shows 4H, N and 4L, the sequence the closing run repeated on 34.1.1. The first press is the like-for-like
  comparison, and it read the same on both versions.) The window stage (`--only w8`) 1 failed (`c3ed9b6`), not SolidWorks': this
  device runs Windows at 150 % on a 2560 × 1600 screen, so the window is 1618 px wide and the built E4 footer asks
  281 px, its bottom at 1657 where Windows holds the window to 1570; the shot (`…\window\shots\20-transfer-case-built.png`
  in the run folder) shows the footer's last lines, the turn sentence and the material to-do, cut off. Every footer
  sentence the stage asserts was said, the read state's footer fitted (106 px, bottom 1483 of 1501), and the chooser
  drew the Speeds panel on 2H, 4L and N. Left for a ruling: the window's height on any screen shorter than it asks,
  which by the code includes a 1920 × 1080 screen at 100 % (inferred, not measured). Ruled at the close: *How W8
  closed*.
- **Reviews of the day** (all under `notes-workbook/`): `W8-REVIEW-9-18.md`, `W8-REVIEW-FIX-9-18-AND-WINDOW.md`,
  `W8-REVIEW-DEMO-S2-S7.md`, `W8-REVIEW-LATE-FIXES.md` (must-fix: `s7` case 8 holds nothing of the Update it
  presses, and must run on 2026 alone before the closing run).
- **Paused at the user's word (2026-11-15, about 6:15 pm): the user needed SolidWorks and the app.** The
  coordinator force-ended the 2024 `s3` run then in progress (its own Python, SolidWorks and Excel; 16 checks in,
  no FAIL; the run is void, its folder renamed `s3-20261115-180714.stopped-for-the-user`) and built a preview exe
  of `29e6c34` for the user (`…\GearGeneratorProbe\build-workbook-29e6c34\dist`). **No agent starts SolidWorks
  on the host again until the user says so.** Also done by then: `s0` on 2024 0 failed (`29e6c34`); the late
  review's points in (`cbdb7ac` for its must-fix, not yet run; `ce775a6` sets `TURN_PER_CONFIGURATION_ON_2024`
  False from 2024's s7; `76e4e6e`, `0ff56d3`, `d2b435a`). The review's S6 was not taken: the advice "press Update
  SolidWorks with that mode showing" stays as it is.
- **Two things done to the user's SolidWorks 2024 by the runs, both told to the user:** (1) the first `s7` start
  there was stopped mid-call and its instance then closed; SolidWorks 2024 faulted on that exit (16:13:53, fault
  module `sldappu`) and left its crash-report window for the user to answer; only a scratch copy was open. Rule
  since: a run ends by its own path or its own STOP, never by stopping its Python mid-call and then quitting
  SolidWorks. (2) The next 2024 start showed "Toolbar information is inconsistent, default toolbar setting will be
  used." and the agent answered OK, so **the user's 2024 toolbars may be back at their defaults**.
- **Left:** ~~2024's remaining sections~~ (run on the next device); ~~the late review's points~~ (in; its S6 not
  taken); ~~`s7` case 8 on 2026~~ (done on 34.1.1); ~~one closing run on 2026 from the final source~~ (done,
  `c351b1f` to `fb85bcc`); ~~PLAN-WORKBOOK §4.5 and UI-DESIGN's last words~~ (in at the close); ~~the close~~
  (2026-11-16). What is truly left is under *How W8 closed* above: the built footer on a short screen (K12 of W9), the
  person's step `s6`, and the two hand drags.
- **Slips on record:** `3579c0c`'s message says the footer is "a line shorter"; it is not.
- **Small things open:** `tests/test_workbook_planetary.py::test_an_update_on_the_fake_leaves_the_train_turning_as_worked_by_hand`
  still rides on the committed `PLANETARY_PUT_ROUTE` (a one-line pin); W8-PLAN §2.2's sentence on the Checks
  panel's warnings does not match the app (Parallel gives 9, E4 gives 7: `W8-REVIEW-DEMO-S0-S1.md` N5); the NOTE at
  the head of `probe/results/w8-over-defined-attempt-20261115-094752.txt` names the wrong mates for the lock alone
  (`findings.py` has it right); the three tier 11 result files carry SolidWorks' main window title, which names
  the licence edition (asked of the user; the probe now leaves such windows out).
- **On this host the Linux venv has no tkinter** (Python 3.14): two tests fail there for that alone
  (`tests/test_gears_clutch.py::test_the_strip_never_offers_them`,
  `tests/test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`) and pass under
  Windows Python. At `74ac826`: 3112 passed, 10 skipped, those 2 failed. *On the third device* (2026-11-16) the
  Linux venv has tkinter, and one test fails there for its Tk font width alone, as the suite paragraph under *Where it
  stands* says.

**To pick W8 up:**

1. Package E writes W8's sections of the demonstration (W8-PLAN §5) — fresh handles after every configuration
   switch; every mode shown and post-checked after a per-mode put, which also settles the one path the review of the
   findings found unmeasured (a put on a gear whose gear mates are on in every configuration).
2. The full build on SolidWorks 2026, fixes, then one confirming build on 2024. On 2024 read once a suppressed gear
   mate's sense on a reopened, unmodified copy: `SUPPRESSED_GEAR_MATE_SENSE_READ` is measured on 2026 only.
3. D's last pass (`14d1125`, `93708d6`) and C's (`45479ea`, `295a214`) had no separate review; A's `5fcaa6a` was
   read by the orchestrating session only.
4. The lesser point left from A's review: a gear mate remade inside a planetary's suppressed put is not read again
   once it is turned back on (`swbuild._put_train`, the comment says so). Reading it again changes W7's call
   sequence, so it waits for a run on SolidWorks.

**Open, for the user to overrule:** making a gear mate of a gearbox with modes again (a tooth change, a sense found
wrong) is refused with a sentence that says to build the gearbox again (ruling 9.16; *under issue #1*: W9c lifts
it); when a mode's mates lock a train, the build's step 6 names the mode and every body that cannot turn, not the
mate (ruling 9.19, `s5`); the built footer on a screen shorter than the window asks is cut off, left so in W8 and
taken up as K12 of W9 (*How W8 closed*); a slider whose place moves in
a workbook with no Modes rows needs a new revision; the chooser goes to rows above the Speeds lines when its
segments pass the room the header leaves beside the readout (at most 200 px; `b12838d`); the sleeve's and dog's
pressure angle is the Box's (20° by default), with no fork groove, hub or chamfers (J1's "no hub" *under issue #1*:
the user chose a hub built from a row, W9b); a stroke that bridges two dogs is warned of only when the sleeve is
longer than the gap (J22, `length > gap`, *under issue #1*).

## Questions waiting for the user

Questions 1 to 5 of 2026-11-14 are answered (`notes-workbook/W5-DECISIONS.md`; PLAN-WORKBOOK §4.5, *Readings chosen
(W5)*), and so is the one after them on a profile-shifted pinion inside a ring (**yes**, 2026-11-14: `d3f4dcf`,
`9efde87`). The issue #1 plan's questions were answered on 2026-11-16 (`notes-workbook/ISSUE-1-PLAN.md`, *Changes
after the user's answers*). Still open (updated 2026-11-16; item 7 brought up to date and items 10 to 19 added on 2026-11-18):

1. **A journaled file on a disconnected drive is treated as gone** — keep that, or hold such entries until the drive
   is back?
2. Readings the user may overrule: Update SolidWorks does not save; a part keeps its file name after a teeth change;
   one build button; no static option in the window once W5 is in (a gearbox is built static only when a W5 finding
   is missing, and a W4 one stays static until Build again…).
3. **Defaults taken while the user was away (2026-11-14 to 16), each to overrule.** They are the rulings of the
   orchestrating session, listed whole in `W6-INTERFACES.md` §7, `W7-INTERFACES.md` §6 and `W8-INTERFACES.md` §9, and
   marked *ruled* in PLAN-WORKBOOK §4.5. The ones a user would notice: W6 — long part names in the Gears table are
   shortened head and tail. W7 — a planetary's gear mates are one per sun mesh and one with the ring from copy 1,
   whatever the Meshes sheet's row order (§6.14); two inputs on a stage are refused (§6.15), as are compound
   planets, a second stage, helical planetaries and a carrier gear that meshes. W8 — the readings J1–J27, J1, J2,
   J16, J14 and J11 first (W8-PLAN §0.4), and the list at the end of *W8 in detail*; J1's "no hub", J22's bridging
   warning and ruling 9.16 are *under issue #1* and change in W9.
4. **The Workbook window on a screen shorter than it asks** (ruled 2026-11-16 by the coordinating session; overrule
   it if you want W8 itself changed): today the window grows past the screen and the footer's last lines are cut off
   (on this device's 2560 × 1600 screen at 150 % the built E4 footer's turn sentence and material to-do; by the code
   also on a 1920 × 1080 screen at 100 %, not measured). W8 leaves it so; W9a takes it up as K12 of
   `notes-workbook/ISSUE-1-PLAN.md`: the window stops at the screen's work area, its two columns scroll between a
   fixed header and footer, and the footer is always whole.
5. **The person's steps** (what the scripts cannot stand in for). Everything is on this device, under
   `C:\Users\M0obo\Documents\GearGeneratorProbe\`, and nothing in these folders has been opened since it was built.
   Have one SolidWorks running at a time (the app talks to whichever is running), and start the app as W8 closed it:
   in a Command Prompt, `cd C:\Users\M0obo\Documents\GearGeneratorProbe\w8-close-sw2026-20261116-001758\snap`, then
   `python main.py`; in its Gear panel, **Import workbook… → Open a workbook…** opens a workbook in the Workbook
   window. If the window's footer runs off the bottom of the screen (item 4), tell us the lines you can see, or set
   Windows' display scale to 100 % for the step to see them all.

   **W8's step `s6`, on SolidWorks 2026, then on 2024** (W8-PLAN §5, its 2026-11-16 note):
   1. Start SolidWorks 2026 alone. Open `w8-close-sw2026-20261116-001758\out\s1\TransferCase_E4.SLDASM` in it, and
      `TransferCase_E4.xlsx` from the same folder in the Workbook window. The assembly opens in 2H.
   2. Double-click **4L** in SolidWorks' ConfigurationManager. RangeSlv, the sleeve between the two dog rings, now
      sits over LoDog, and ModeSlv over FrontDog. Drag the sun, the small gear at the front on In, round by about a
      quarter turn: the rear sleeves and the front output gear should turn the same way as the sun at a quarter of
      its angle, and the idler between the front gears the other way.
   3. Double-click **N** and drag the sun again: the planets should roll round it and LoDog, the dog ring on the
      carrier, turn the same way at a quarter; the rear and the front should stand still.
   4. Double-click **4L** again. Tell us whether the gears stand where you left them in 4L or where you left them in
      N. (A turn has been read in every mode on both versions, so we expect where you left them in N; a drag by hand
      has never been read, which is why we ask.)
   5. With 4L showing, press **Update SolidWorks** in the Workbook window with nothing changed. It shows and puts
      every mode, about 4 minutes on 2026 (about 9 on 2024). The footer should begin *"Updated SolidWorks: re-placed
      … in every mode"* and say *"In 4L, RangeSlv's teeth stood across LoDog's; the gears of 4L are back at the turn
      they were built at. This version of SolidWorks can show a turn given in one mode in the others, so the turn may
      have been given in another. It worked in 4L, the configuration that was active, then showed and checked 2H, 4H
      and N and left the assembly in 4L."* If it says instead that the gears stand where they were turned and that
      it did not show the other modes, or anything else, copy the footer to us: that is the reading we lack.
   6. Close the assembly without saving, and exit SolidWorks.
   7. Then the same in SolidWorks 2024, alone, with `w8-sw2024-20261115-223821\out\s1` (the E4 built on 2024; the
      2026 folder does not open in 2024).

   **The two hand drags, on SolidWorks 2026** (W6-PLAN §6.1, W7-PLAN §6; both folders built on 2026 34.1.1 by the
   closing run):
   1. Open `w8-close-sw2026-20261116-001758\out\r1\Bevel_Reducer.SLDASM` in SolidWorks 2026 and `Bevel_Reducer.xlsx`
      from the same folder in the Workbook window. Drag **G1**, the small bevel gear on the horizontal shaft S1, round
      its axis by about a quarter turn: G2, the large bevel gear on the upright shaft, turns half as far, and G3 under
      it with it; G4, the large spur gear on S3, turns a sixth as far as G1 and the other way round from G2. Nothing
      leaves its axis or passes through another gear. Press Update SolidWorks with nothing changed: the footer says
      the gears stand where they were turned. Close without saving.
   2. Open `w8-close-sw2026-20261116-001758\out\p1\Planetary_4to1.SLDASM` and `Planetary_4to1.xlsx` the same way.
      Drag **Sun** round its axis by about a quarter turn: the three planets roll round inside the ring the same way
      as Sun, about a quarter as fast, each spinning the other way on its own axis; the ring does not move. Press
      Update SolidWorks with nothing changed: the footer says the gears stand where they were turned. Close without
      saving.
   3. If a gear does anything else (turns the wrong way or by another amount, leaves its axis, passes through
      another, or SolidWorks asks something on closing), tell us which gear did what, and copy the footer.

   *The older drag folders* (`w6-full-20261114-210827\out\r1`, `w7-full-20261115-000138\out\p1`, built before W8's
   code) are on this device too and still serve, but the closing run's are built by the app as W8 closed it.
6. **`tests/fixtures/excel-windows/Planetary_4to1.xlsx`** as Excel saves it was not committed: the session's
   permission check refused the write, and no test or script reads it. Commit it by hand if it is wanted; the file
   is in `…\GearGeneratorProbe\w7-full-20261115-000138\fixtures\`.
7. **Probe folders** under `C:\Users\M0obo\Documents\GearGeneratorProbe` hold several gigabytes of built gearboxes;
   only the two run folders of item 5 (`w8-close-sw2026-20261116-001758` and `w8-sw2024-20261115-223821`) are still
   needed, and those only until the steps are done. *2026-11-18:* until W9 closes, the masters and run folders named in
   *Run folders and masters, 2026-11-18* (after item 11 of *Where W9 stands*) are needed too.
8. **The macro database is yours to update** (W8-PLAN §6 item 6): GOTCHAS §83 and assemblies/07 record, on 2024, that
   component positions are not stored per configuration. What W8 read is finer: a put that moves a component is
   kept by its configuration (until that train is next turned anywhere), while a turn of a mated train by its drive
   shows in every configuration, on 2026 (34.0.0 and 34.1.1) and 2024 alike (`findings.py`,
   `POSITIONS_PER_CONFIGURATION_ON_<year>` and `TURN_PER_CONFIGURATION_ON_<year>`; ruling 9.18).
9. **A mate of yours other than a lock, on a gear Update puts back** (ruled 2026-11-16 by the coordinating session
   after S0's review; overrule it if you want). Route (c), which you accepted, puts a component of yours with its
   gear when your own locks hold it there, as they are in the mode being put; that is the one kind S0 measured. Every
   other kind of mate of yours that ties your component to a gear Update would put back makes Update refuse before
   it changes anything, naming the mate: a gear mate of yours above all, a mate to a gear's own faces or planes, and
   a lock of yours that is on in some modes and off in others. Why: SolidWorks lets a gear mate take a put gear's new
   phase without any error (measured in W5 on the app's own gear mates), so your component's teeth would be left out of
   step with the gear's with no word, and the other kinds were never tested against a put. Measuring those kinds in W9a's demonstration would
   lift the refusal for each kind that holds, at the cost of more SolidWorks time on both versions
   (`notes-workbook/ISSUE-1-PLAN.md`, K2 and *Changes after S0 and its review*).
10. **A What's Wrong box on SolidWorks 2024 that outlives its job** (ruled 2026-11-18 by the coordinating session;
    overrule it if you want). On 2024, the box SolidWorks raises when an Update has stopped with a part left in error
    stays up until someone closes it. A demonstration script may close such a box with the box's own Close button only
    when its run asks for that by a flag (`--close-outlived-whats-wrong`), so that one box cannot end an unattended
    run; the app itself never closes the box and changes no SolidWorks setting, and instead tells you what the box
    does: that it stays if the Update stops before SolidWorks rebuilds, and that you close it with its Close button
    (`notes-workbook/ISSUE-1-PLAN.md`, the What's Wrong section). W9a's question of letting the app turn "show errors
    every rebuild" off for its job (item 8 of *Where W9 stands*) is still yours.
11. **The assembly reads modified after a stopped Update** (ruled 2026-11-18). After an Update stops with a part left
    in error, SolidWorks marks the assembly modified the first time anything brings it forward, on 2024 and 2026
    alike, though nothing was written; this is taken as a fact of SolidWorks and not a fault of the app, and the
    stop's sentence already tells you to close the assembly without saving.
12. **The lightweight fact is recorded as a finding pair** (ruled 2026-11-18). When Build again… carries a component
    of yours that is lightweight in the old assembly, opening its part to insert it can leave that instance resolved
    in the old assembly; that one change is allowed, read before and after, and said in the result (D10 †,
    `W9D-INTERFACES.md`). The coordinator ruled it be kept in `findings.py` as the pair
    `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY_ON_2026` (True) and `_ON_2024` (set from the 2024
    run), which nothing in the app reads. The other way, which you may choose, is that such a component is named and
    not carried, so the old assembly is never changed at all.
13. **Printed gears, D11:** now item 1 of question 19.
14. **Printed gears, D6: no pair interference warning in F1** (item 2 of question 19; ruled 2026-11-18; it departs from the assumed D6,
    "warn, and check each printed pair"). The words for you are the last section of `docs/PLAN-PRINTED-REVIEW.md`:
    *"We had planned that the app would warn whenever one printed gear's teeth might run into the bottom of the
    other's. Checked against the gears as the app actually draws them, that warning would have fired on almost every
    printed planetary for a clash the parts do not have. With the printed default backlash none of the pairs checked
    touch, and even with no backlash the most is 0.07 mm. So F1 adds no pair warning: a small gear still says it is
    printed exactly as drawn and that you should turn the pair in SolidWorks, and a proper check is planned after your
    test prints. Helical, shifted and bevel pairs were not checked this way, and if you type a backlash under about
    0.1 mm the parts may touch slightly without a warning."*
15. **For you to know: memory on SolidWorks 2024** (measured 2026-11-17, `W9C-RUNS-REVIEW.md`'s 2024 addendum §4). An
    Update of a gearbox with modes can take SolidWorks 2024 3 to 4 GB more memory, kept until the assembly is closed;
    on 2026 it stayed under 2.3 GB for the whole run. On a machine with little free memory, save and close the
    assembly between rounds of Updates, or restart SolidWorks; the app does not watch memory. Also on 2024, the
    interference volume the app prints can be some 5 % off what SolidWorks' own Interference Detection shows; the app
    names the interfering pairs either way.
16. **The Windows account's folder name in committed files** (asked 2026-11-17). Notes now write a run folder as
    `<probe folder>\…`, but the logs, tonight's too, carry the full path with the account's folder name
    in their run lines, as this file's older paragraphs do. Rewrite the old logs, or leave them?
17. **Telling a SolidWorks 2024 user about memory in a carrying Build again…** (ruled 2026-11-18 by the coordinating
    session; overrule it if you want). On SolidWorks 2024 a carrying Build again… of a gearbox the size of RangeBox
    took SolidWorks to about 11 GB and about 25 minutes (W9D-DEMONSTRATION-REVIEW's last section). For now this is
    recorded as a known limit, here and in the notes, and the app adds no sentence about it; the other way is for the
    question to say so on 2024, for example that you save other work first.
18. **Printed gears, two changes to the plan:** now items 5 and 6 of question 19.
19. **Printed gears: the coordinating session's rulings of 2026-11-18 on `docs/PLAN-PRINTED.md`, gathered** (each
    yours to overrule; the details are in `docs/notes-printed/F1-0.md` and the three package notes on branch
    `printed`, and in `docs/PLAN-PRINTED.md`'s decision table and *Changes after* sections there). How cheaply each is
    changed is the coordinator's reading of those notes:
    1. **D11 answered (B).** A gearbox built before F1 opens exactly as it does today, a blank Process meaning *as
       built*, and nothing reads as changed or is written until you type Printed. Cheap to change: (A) is one switch,
       the body of `assess.blank_process` (§1).
    2. **No pair interference warning in F1**, against the assumed D6 ("warn, and check each printed pair"); the words
       for you are question 14's. A small gear still says it is printed exactly as drawn and to turn the pair in
       SolidWorks. Not cheap to change: the radial check was withdrawn because it reports overlaps the drawn parts do
       not have, so a warning wants the sweep of the drawn outlines the plan lists as later work.
    3. **A printed pair's assembly carries `_P`**, as its parts do; a machined pair's names stay exactly as they are.
       Cheap: one function, `pair_stems`, and its pins.
    4. **A bad Process word or a printed gear's bad Nozzle is an error at its field** (the form's field, or the Box
       sheet's cell), and only checked Box values go into the gears, so one bad cell is said once. Cheap to word otherwise.
    5. **The form judges a printed crossed helical pair's tip clearance as the Workbook window does** (`368db90`), so
       the two never disagree. Cheap: one call in the form.
    6. **The span over k teeth moved to F2's first step** (§3.0), before any print is measured, since nothing in F1
       needed it. Only the order of work; it is still built before you measure a print.
    7. **D3 and D7 stand as assumed.** D3: a printed gear's blank Backlash is the smaller of 0.3 mm and 0.3 × module,
       to be replaced by your own measurement (§3.2). D7: PLA's allowable tooth stress 17 MPa, provisional, for F4
       only, nothing built on it. D3 is one formula (the Backlash IIF) and its pins; D7 is not yet in the code.

Answered ahead of its phase (the user, 2026-11-14), for W7's sub-plan:

- **A carrier is built as a skeleton only.** W7 makes a carrier as a part of axes and planes with no solid, as the
  layout part is, free to turn about its own shaft's axis, with each planet mated to an axis in it. The app makes
  no solid carrier (a plate, pins): that geometry depends on the gearbox at hand and is left to the user. PLAN-WORKBOOK
  already has the carrier as a shaft row that planets are `Mounted on`; this settles what stands for it in
  SolidWorks.

## Rules carried over

- Commits and PRs carry **no Claude co-author or attribution line**. Commit by explicit path only
  (`git add <paths>`; `git commit -m "…" -- <paths>`), prose messages with the why; never `add -A`,
  `commit -a`, stash or reset. ~~Push only when the user says so.~~ Since 2026-11-14 the user wants each
  reviewed step pushed to `origin` as the work goes; the orchestrating session pushes, subagents commit only.
- **The repo is public**: no user document titles in committed logs (`<user document N>`), no other
  personal data.
- Each phase's plan and result is reviewed by a separate subagent before moving on. In the 2026-11-13
  session the user asked for Opus subagents only, with no cap on their number.
- ~~Every SolidWorks call is probed before the app depends on it.~~ **Since 2026-11-14 (the user, after W5's
  six probe rounds): the full build comes first.** A phase is written against the fake and then built end to
  end on SolidWorks early; what that build gets wrong is what gets probed step by step. Probing before the
  app depends on a call is kept for one kind only: a call not used before that could hang, raise a dialog, or
  leave a file or a session damaged. **SolidWorks 2026 is the working version**: probes and the full test run
  there, and SolidWorks 2024 gets one full build at the phase's end to confirm, with what fails there fixed
  then. One follow-up probe round per phase; a reviewer's point the app does not depend on is written down as a
  caveat, not run again. After a fix only the affected demonstration sections are rerun, with one full run at
  the phase's close. Findings are still read from committed `findings.py` only, a missing one still refuses
  with a sentence, and the plan's STOP-and-ask triggers apply.
  *What the confirming build on 2024 is:* not the whole demonstration again. It is one full turning build
  with its edits, plus every section in which the two versions have been seen to differ (for W5: `m1`, and the
  ring sections `m3` and `m7`; about 12 minutes where the whole run takes 36).
  *Not done yet, for the phase after W5:* the demonstration builds each fixture from scratch in nearly every
  section (the 12 : 1 seven times). Build each fixture once and start the later sections from a copy of the
  built folder; the records hold paths, so the script has to carry them over, and that change is reviewed like
  any other.
- **SolidWorks runs only on the Windows host.** SolidWorks 2024 there is the user's live session: record
  the open titles before a run, close only documents the run created, never save, close or modify theirs,
  never exit it, stop under 2 GB of free RAM, and prefer a freshly restarted session for long runs (one
  long probe run grew it by about 5 GB). An agent may start and exit its own SolidWorks 2026. One driver at
  a time. *On the user's own device (2026-11-14):* the user allows both SolidWorks 2026 and 2024 to be started,
  exited, and killed when one will not exit or memory is short; still one SolidWorks running at a time (the
  app asks every running SolidWorks for its version), and nothing the user has open is touched.
- Excel on the Windows host may be opened: use only an Excel the run starts, close only the workbook you
  opened, never quit the user's Excel.
- Screenshots on the Mac: capture by window id (`screencapture -l`), not by region, because a region
  capture picks up whatever app is in front.
- **Learned on 2026-11-18, on this laptop.**
  - *Two checkouts.* `~/SW-Gear-Generater` holds `w9d` and `~/SW-Gear-Generater-printed` holds `printed`, both
    worktrees of one repository. An agent resumed after the session's working directory changed may not be in the
    checkout it was in: tell every agent its checkout by absolute path, and have it work and commit only there.
  - *False Tk failures.* Two suite runs at the same time (two agents, or two checkouts) give Tk failures that are not
    the app's. A Tk test that fails is run again alone before it is reported as a failure.
  - *Run folders and masters.* This laptop holds the 2026 and 2024 masters every W9c and W9d run here starts from, and
    the second host holds others that nothing here needs; the paragraph *Run folders and masters, 2026-11-18* after
    item 11 of *Where W9 stands* lists both. A run takes the masters of the host it runs on and of the SolidWorks
    version it runs on (a 2026-built master does not open in 2024).
  - *Keeping the laptop awake.* The demonstration and probe scripts ask Windows to keep the system and the display
    awake only while they run (`keep_awake` in `probe/w9_user_work_check.py`). For the night of 2026-11-17/18 the
    coordinator started, at the session's start, a hidden PowerShell holding `SetThreadExecutionState` (continuous,
    system and display required) for 14 hours. It ends by itself after that, or when its PowerShell process is ended.
    It does not stop a closed lid from sleeping the machine: leave the lid open for an unattended run.
  - *Unattended 2024 runs* take `--close-outlived-whats-wrong` (question 10); runs on 2026 do not, a What's Wrong box
    there being the STOP.
