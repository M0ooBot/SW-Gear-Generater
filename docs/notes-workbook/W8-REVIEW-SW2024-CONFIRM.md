# Review of W8's 2024 confirming build on the next device, and the handoff written from it

*Independent, 2026-11-16. I changed no code, started no SolidWorks and opened no window.* Under review, all said to
be from one `git archive` of `0e7f203`, on SolidWorks 2024 (32.5.0):

- `233e03d` s1, `b6bb186` s3, `c3ed9b6` the window stage (`--only w8`), `eae38c9` s2. Their logs are under
  `probe/results/sw2024/`. Below they are "s1:N" (`w8-workbook-assembly-20261115-224101-s1.log`), "s3:N" (`…-230215-s3.log`),
  "s2:N" (`…-233045-s2.log`) and "win:N" (`w8-window-20261115-232543.log`).
- `c583f48`: `docs/HANDOFF-WORKBOOK.md`, namely the W8 row (46), the 2024 bullet (663-690) and *Left* (708-712).

I compared them with the 2026 logs: s3 `probe/results/w8-workbook-assembly-20261115-114929-s3.log` (34.0.0, `e670e7e`,
"s3-26:N"), s2 `…-151412-s2.log` (34.0.0, `4871a85`, "s2-26:N"), the window stage `w8-window-20261115-150900.log`
(snapshot `074df2c`, "win-26:N") and s1 of `…-220745-s1-s7-case8.log` (34.1.1, `fe74276`). I also read the earlier
2024 s1 and s7 logs, `findings.py`, ruling 9.18, both probe scripts and `workbook_gui.py`. To compare check lines I
took every `ok`/`FAIL`/`STOP`/`NOTE` line and replaced each number with `#`. Line numbers are at `c583f48`.

**Verdict.**

- **No must-fix. Pushable as is.** Every count, failure total and reading the commits and the handoff state is in the
  logs. Each section ran all of its 2026 counterpart's checks and more; nothing was skipped or cut short. Every
  difference in check lines is accounted for: newer source, the order SolidWorks lists FIdler's two clashes in, or
  which body is named as the largest gap. None is a SolidWorks 2024 difference.
- The window failure is what the agent says it is. It would fail the same way on 2026 on this device.
- The `s7` case 7 reading does answer "To pick W8 up" item 2. The finding's comment should now say so (S1).
- Should fix:
  1. The `SUPPRESSED_GEAR_MATE_SENSE_READ` comment still says 2024 is not covered. The wording to use is below (S1).
  2. The handoff sets 2024's s2 against 34.0.0's s2 without saying the two ran different sequences (S2).
  3. The 2024 comments in `findings.py` and ruling 9.18 do not take in what 2024's s2 read (S3).
  4. None of the four logs names its snapshot, and the window log does not name the revision. `0e7f203` and "on
     2024" rest on the commit messages alone (S4).
  5. The W8 row still says "No W8 code has run on SolidWorks" (S5).
  6. The handoff calls the window problem one of "a short screen". The code says that includes an ordinary
     1080-px screen at 100 % (S6).
- Notes: eight, below.

---

## Question 1: do the logs hold what was said?

| | s1 | s3 | s2 | window |
|---|---|---|---|---|
| `ok` lines / checks claimed | 555 / 555 | 409 / 409 | 603 / 603 | 13 ok, 1 FAIL |
| `done` | 0 failed, 1 noted (s1:1753) | 0 failed, 1 noted (s3:862) | 0 failed, 3 noted (s2:1199) | `fails` has the one footer line (win:77) |
| STOP | none | none | none | none |
| NOTEs | notification box during `GetNextFeature` (s1:1576) | box, no call (s3:9) | box, no call (s2:9), during `GetTypeName2` (s2:375), no call (s2:1107) | none |
| seconds | 1216 (s1:1746) | 1351 (s3:855) | 2575 (s2:1190) | — |
| revision in head | 32.5.0 (s1:2) | 32.5.0 (s3:2) | 32.5.0 (s2:2) | **not logged** (the script never logs it) |
| snapshot in head | **absent** | **absent** | **absent** | **absent** |

Every NOTE comes with the exempt untitled box (`Title`, `Description`, `Button1` …). s1:1635 is a second DIALOG, the
open-summary panel ("Opened 15 Components …"). It is not a NOTE, and earlier 2026 and 2024 logs show it too.

**s1 against 2026 34.1.1's s1 (`fe74276`).** The section is the same, line for line (555 against 555). The
differences are these:

- in four lines, the order the interference list names FIdler's two clashes in;
- in two lines, which body is named as the largest gap;
- the NOTE.

Against the other host's 2024 s1 (`48ab0aa`), the one changed check is the positions finding: `None` there, `False`
here (`ce775a6`). The three couplings were made again with the other Flip on both 2024 runs (s1:1022), as `233e03d`
says.

**s3 against 2026 (`e670e7e`, 401 `ok` lines).** No 2026 line is missing. Eight lines are new, all from source newer
than `e670e7e`, all from `7c9634d`:

- the D10 Update's four status sentences (s3:127-130);
- the status sentence and "every sense read" for M2 suppressed in every mode (s3:738-739), and for Exploded added
  (s3:820-821).

In four lines only FIdler's clash order differs. The `GetSystemValue3` reads that `b6bb186` mentions appear in `fact`
lines, not checks.

**s2 against 2026 (`4871a85`, 591 `ok` lines).** No 2026 check is lost. Every difference has one of these causes:

- *The wording of newer source* (`f765894`, `5989c7d`, `7c9634d`): "the turn finding is False, so …" where 2026 has
  "this version shows the turn in every mode, so …"; `ui_text.TURN_SHOWN_ELSEWHERE` cited by name.
- *Checks added since `4871a85`* (`7c9634d`, review M1 and S1):
  - after the fresh turn, 4H, N and 4L are each shown and read (s2:354-370). 2026's run showed 4L alone;
  - after the Update in 2H, "every sense read" and "every slide's value read in every mode" (s2:344, 346);
  - "the record's frames after the press are the built ones" (s2:236, 478);
  - "the turn finding (False) gives the sentence ending …" (s2:232, 474);
  - for the second Update in 4L, the `expect` line ("the turn finding is False, so 4L's couplings are found across",
    s2:455), and "the couplings found across are those 2H's turn crosses in 4L" (s2:465). The second is gated on
    `expect == "finding"`, which 2026's `expect=None` call skipped.
- *Not from the code:* FIdler's clash order (4 lines); the largest-gap body (4 lines); one drive's RangeSlv–InDog
  residual printed as `#e+#°` where 2026 printed `#°` (a number below 1e-4, still a pass); the paths
  (`out2` → `out`).

None of these is a SolidWorks 2024 difference. On 2024 every quiet or changed Update that puts took 511-521 s (s2:203,
445, 583, the `fact` lines before them). On 2026 34.0.0 the same presses took 210-238 s.

## Question 2: s2's reading across modes

It is in the log, as stated:

- *The fresh +37° in 2H* reads in 4H, N and 4L. Each body's turn from its own frame on record is 2H's: Sun, InDog,
  RangeSlv and ModeSlv +37°, LoDog and the carrier +9.25°, each Pl −18.5°, FrontDog and the front train 0 (s2:356, and
  the N and 4L lines after it). Only 4L reads interference, LoDog–RangeSlv 531.557 mm³ (s2:369). These are fact lines,
  not checks.
- *The Update in 4L after it* shows 2H, puts there, then shows 4H, puts, and so on (s2:443, the order of shows and
  puts). Read when each mode was shown, before its put (s2:462-465):
  - 2H: in step, turned;
  - 4H: out of step at ModeSlv–FrontDog, not turned;
  - N: in step, turned;
  - 4L: out of step at RangeSlv–LoDog and ModeSlv–FrontDog.

  4H's out-of-step is exactly the fresh turn: ModeSlv +37° against FrontDog at 0, residual 1.75e-2 rad (s2:438).
  Had 2H's put reached 4H, 4H would have read in step at its built frames. So 2H's put did not carry to 4H, N or 4L.
  The first quiet Update read the same four judgements (s2:220-223), as 2026's first press did (s2-26:224-227).
  `ModeCheck.turned` is unjudged while a coupling is out of step (probe 6703); the probe prints these judgements as
  "post-check of …" (probe 6512, s2:446-449). Both are as `W8-REVIEW-CASE8-2026.md` described.
- *After each put*, every body in every mode reads at its built frame through fresh handles, largest 8.3e-10 mm
  (s2:237-244, 479-486). The frames are held to those copied from the master, not to the record the app rewrote
  (probe 6735). The changed Update's own every-mode reads come after it (s2:584-587 are its judgements on showing,
  FDrive off its axis in 2H and 4L as the edit moved it).

**Is it consistent?** Yes, with `TURN_PER_CONFIGURATION_ON_2024 = False`: the turn reached every mode, and the status
said "so the turn may have been given in another" (s2:474). It is also consistent with the 2024 comments in
`findings.py` 1302-1315 and 1251-1258 and with ruling 9.18's 2024 sentences (`W8-INTERFACES.md` 358-370). None of
them is now contradicted. Each understates a little, because each cites s7 alone (S3). Nothing in them overstates.

## Question 3: the window failure

**It is the whole cause.**

- *The check.* `w8_footer_whole` (`probe/workbook_window_check.py` 630-639) passes when the label is drawn at its
  requested height and its bottom lies inside `win.winfo_height()`. Here the label got its full 281 px. Its bottom
  is at 1657, and the window is 1570 tall inside (win:68).
- *The app.* `WorkbookWindow._fit` (`workbook_gui.py` 1160-1170) asks for `max(winfo_reqheight, current)` with no cap.
  It keeps `y >= 0` against `winfo_screenheight()`, the whole screen rather than the work area, and never against a
  height larger than the screen. Windows then holds the window at its largest size. On a 1600-px-tall screen that
  is consistent with 1570 inside (the frame is 22 px wider than inside, win:70).
- *The arithmetic.* On 2026 at 100 % the built window was 1097 inside, the footer 156 px (win-26:61). Scaled by 1.498
  (1080 → 1618, win:70) that is about 1643. The footer wraps to 281 px here, not the 234 a straight scale gives, so
  the window wants about 1690. That is far over 1570. The read state wants 1501 (win:18), which fits.
- *On 2026 on this device.* The built footer's eight sentences are word for word the same on both versions here.
  Both turn findings are False, so the "can show" sentence is said on both, and nothing else in that status depends on
  the version. So the same stage would fail the same way on SolidWorks 2026 on this device.
- *What else differs from win-26.* Nothing that is SolidWorks':
  - win:1 has no `snapshot` field (win-26:1 has `074df2c`);
  - three "head lines are §2.3's" checks and five "the footer says" checks are new since `074df2c` (`7c9634d`);
  - the turn sentence reads "can show …" where 2026's read "shows in every mode …" (`5989c7d`);
  - the folder is `window` here, `scratch` there;
  - the width is 1618 here, 1080 there.

  The build progress samples are out of order in both logs, which is sampling.
- *The earlier stages of the full check.* Only the W8 stage calls `w8_footer_whole`, and no earlier committed window
  log records a height. So stages 1-9 would not fail on this screen whatever they draw, and whether their footers
  would be cut is unmeasured. I expect them to fit. Their longest status is 615 characters (06-structural-unsaved),
  against 525 for W8's read state, which fits at 106 px. Their Speeds panels are 3-4 lines against E4's 11 plus the
  chooser, and their fixtures have far fewer shafts and gears than E4's 8 and 11. That is inference.

## Question 4: `s7` case 7 and `SUPPRESSED_GEAR_MATE_SENSE_READ`

`probe/results/sw2024/w8-workbook-assembly-20261115-162357-s7.log` 1175 shows the reading item 2 asked for, and the
JSON `w8-s7-20261115-162418.json` `cases[6].suppressed_sense` holds it too:

- the copy of the 2024-built `s1.master` opened from its files (1151). Every document read `GetSaveFlag` False
  straight after the open, so the copy was opened from disk and unmodified;
- 2H active. `RangeSlv engages LoDog` read suppressed there: the build suppressed it in 2H and saved it so;
- read once by `Session.gear_mate_sense`, the call `swbuild._sense_read` makes (`swbuild.py` 954). It answered
  right, τ (1, 1). The control, `RangeSlv engages InDog`, on in 2H, answered the same;
- no document marked modified before or after;
- the raw flag reads after it marked nothing either (1188).

It differs from 2026's reading in three ways, none of which defeats it:

- the mate is a collinear coupling, not the parallel mesh `Planet copy 1 meshes Ring`. W8's suppressed gear mates are
  the couplings, so this is the case the app relies on;
- it was suppressed by the build in a configuration, not by hand and then saved;
- it was read once, not twice.

The call passes no `meet` where `_sense_read` passes one; for a collinear pair that is the default.

The app's own route on 2024 corroborates it. Quiet Updates that read every sense marked nothing, before or after:

- s3:739/742 (M2, suppressed in every mode);
- s3:821/824 (Exploded added);
- s2:344/349 (Update in 2H, with LoDog's and FrontDog's couplings suppressed there).

Those copies had been saved, not reopened.

**S1 gives the replacement wording.**

## Points

**S1. Should fix: the finding's comment.** `src/gear_generator/findings.py` 1377-1379. Replace the "Not covered"
sentence with:

```
# On 2024 (32.5.0, W8 s7 case 7 at 1560b25; probe/results/sw2024/w8-workbook-assembly-20261115-162357-s7.log line
# 1175, w8-s7-20261115-162418.json cases[6].suppressed_sense): on a copy of the 2024-built E4 opened from its files,
# every document GetSaveFlag False, 2H active, the coupling "RangeSlv engages LoDog", suppressed in 2H by the build,
# read once by gear_mate_sense answered right (τ +1, +1), as the control "RangeSlv engages InDog" left on did, and no
# document read modified before or after. The app's own quiet Updates on 2024 then read every sense, the suppressed
# couplings included, and marked nothing (sw2024/…-230215-s3.log lines 739-742 and 821-824, …-233045-s2.log lines
# 344-349).
# Not covered: on 2024, a suppressed mesh between parallel axes (2024 read a collinear coupling, 2026 a planet's
# mesh), or a second read.
```

Then `swbuild.py` 1998-2000 ("as SUPPRESSED_GEAR_MATE_SENSE_READ does", unmeasured on 2024) should drop that clause.
The handoff's "(…; the finding's comment still says 2024 is not covered)" (675-676) should drop with it. A pin in
`tests/test_findings.py` beside the `test_s7_on_2024_…` ones would hold the JSON to the comment, as the s7 readings
are held.

**S2. Should fix: 2024's s2 is set against 34.0.0's s2 as if both ran the same sequence.** `HANDOFF-WORKBOOK.md`
681-684 says: "That is what 2024's and 34.1.1's case 8 read; 34.0.0's `s2` had found 4H and N at the built turn
there." The sequences differ. Tonight's s2 showed 4H, N and 4L between the fresh turn and the press (probe 6837-6841,
added by `7c9634d` after `4871a85`). The 151412 s2 showed 4L alone (s2-26:356, the line "a fact until s7 settles it").
So this is a third reading of the open question, not a 2024-against-2026 difference. It is the first run anywhere of
the s2 sequence the closing run will repeat on 34.1.1. Add after the sentence: "(34.0.0's `s2` showed 4L alone between
the fresh turn and the press; this `s2` shows 4H, N and 4L, the sequence the closing run repeats on 34.1.1.)" The
first press is the like-for-like comparison, and it read the same on both (s2:220-223, s2-26:224-227). It is worth
saying so.

**S3. Should fix (records): the 2024 comments and ruling 9.18 cite s7 alone.** Three places:

- `findings.py` 1302-1310 (TURN on 2024): add that s2 on 2024 (`…-233045-s2.log` 354-370) read the fresh turn in 4H,
  N and 4L after an Update had put every mode;
- `findings.py` 1251-1258 (POSITIONS on 2024): add that both of the app's quiet Updates in 4L found 4H out of step and
  N turned after their put in 2H (220-223, 462-465), and then every mode at its built frames (237-244, 479-486);
- `W8-INTERFACES.md` 358-370, and "On 2024 it has been read in every mode in every state s7 tried" (423): add the
  same s2 lines.

The sentence in ruling 9.18 at 355-357 ("The closing run's `s2` on 34.1.1 … is what re-reads `s2`'s own sequence")
should note that this sequence has now run once, on 2024, with the reading above. Nothing behavioural changes.

**S4. Should fix: the snapshot is in no log, and the revision is not in the window log.**

- *Snapshot.* `workbook_assembly_check.snapshot()` (probe 8215-8221) and `workbook_window_check.py` 333-336 read
  `SNAPSHOT_COMMIT` beside `src`. Every earlier log carries it (`(snapshot: …)`, `"snapshot": …`). All four of
  tonight's lack it, so the archive was made without that file.
- *What the logs do show.* They are consistent with any source from `ce775a6` on. The findings line has
  `_ON_2024 False`. The probe did not change between `ce775a6` and `0e7f203`. `0e7f203`'s, `867d1af`'s and
  `5946fdf`'s source changes are comments only (I diffed them). So no log line can tell `0e7f203` from `d2b435a`.
- *Revision.* The window check has never logged the revision. That this window run was on 2024 rests on
  `c3ed9b6`'s message alone. The footer is the same on both versions, and PID 18160 says nothing.

What to do: say in the 2024 bullet (678) that the four logs name no snapshot (no `SNAPSHOT_COMMIT` was written beside
the archive), and that `0e7f203` is the run's own record. Write the file with every snapshot from now on. The
window check could log the attached revision as the assembly check does. That is a script change, and it would need
its own review.

**S5. Should fix: the W8 row still says "No W8 code has run on SolidWorks".** `HANDOFF-WORKBOOK.md` 46, at the end
of the row: "**No W8 code has run on SolidWorks:** the demonstration (package E), the full build on 2026, the
confirming build on 2024 and the close are left." It sits after "Before that:", but it is in the present tense and
in bold, and the same row now says both builds ran. Make it "Until then no W8 code had run on SolidWorks", or drop it.

**S6. Should fix: "a short screen" understates where the footer is cut.** Two places say it: `HANDOFF-WORKBOOK.md`
46, "not SolidWorks'", and 689-690 and 709-710, "the window's height on a short screen". By the arithmetic in
question 3:

- at 100 % the built E4 window asks 1097 px inside, plus its title bar;
- a 1920 × 1080 screen at 100 % holds a window to about 1060 inside;
- so the footer's last lines would be cut there too.

That is inference: no run has measured it. The ruling the handoff leaves open is the app's layout at any height
below about 1130 logical px, not one device's. `_fit` keeps the window on screen by moving it up, not by capping it,
and it measures against the full screen height, not the work area, which UI-DESIGN §9 ("moves left or up rather than
off the screen") does not cover. Say so where the ruling is listed, so the user rules on the general case.

**N1.** `HANDOFF-WORKBOOK.md` 648 ("about 15 minutes on 2024") and 680 ("about 515 s") are both right for their own
device: the second host took 903 s (`W8-REVIEW-LATE-FIXES.md` N9), this device took 511-521 s. Name the device at
648, or drop the number there.

**N2.** 680: "238 s on 2026 34.0.0" is the slowest of 2026's three puts (238, 210, 209 s); "210-238 s" is what was
read. "each quiet Update that puts" also covers the changed Update, which took the same time here (517 s).

**N3.** 679: "`s3` … read as 2026 read it" drops `b6bb186`'s qualification. The 2026 run was at `e670e7e`, before
`a87c1c5`/`baa1a56`, so tonight's 2024 s3 is the first s3 on the current Update anywhere. The closing run's `--only
modes` covers it on 2026.

**N4.** 709: *Left* still lists "the late review's points". The *Paused* bullet (694-701) says they are in, all but S6,
which was not taken, and MF1's run on 2026 is done (case 8 on 34.1.1). If none is open, strike it as the other done
items are. If one is, name it.

**N5.** 46 and 663: "every section in" holds against the plan the handoff had: `s0`, `s1`, `s7`, `s3`, the window
stage, `s2`. Neither `s4` nor `s5` was planned for 2024. "Rules carried over" (803-805) allows that.

**N6.** The probe prints each mode's judgement on showing as "post-check of …" (probe 6512). The same mislabel was
noted in `W8-REVIEW-CASE8-2026.md`. Rename it when the probe is next touched.

**N7.** s1:1635, the open-summary DIALOG, is not counted under "progress boxes seen" (s1:1749, `Opening: 0`). That is
harmless, but the tally under-reports.

**N8.** The privacy pass is clean (question 6). Searching the four logs for edition and licence words, e-mail
addresses, host names and `\Users\` paths finds only `C:\Users\M0obo\Documents\GearGeneratorProbe\…`, as earlier logs
have. `open before: []` holds in all three assembly logs, so no user document was open. The only file names are the
run's own (`TransferCase_E4*`, `Gear_m…`, `Ring_m…`, `Dog_m…`, `Sleeve_m…`), plus the stock "Reducer_12to1" person
step. The DIALOG lines are the untitled notification box and the open summary. There is no SolidWorks main-window
title.

## What I could not verify

- That the archive was `0e7f203`, and that the window stage ran against SolidWorks 2024 (S4).
- The device's screen: 2560 × 1600, 150 %, a work area 1019 logical px tall. None of it is logged; 1618 = 1080 × 1.498
  and the 1570 clamp are consistent with it. Nor did I see the shot `20-transfer-case-built.png`: it is in the run
  folder, not the repo.
- Whether the earlier window stages, or a 1080-px screen at 100 %, cut the footer (question 3, S6). That is reasoning
  from the code and the 2026 heights; nothing has measured it.
