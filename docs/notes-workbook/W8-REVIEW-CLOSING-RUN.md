# Review of W8's closing run on SolidWorks 2026 (34.1.1) at `c583f48`

*Independent, 2026-11-16. I changed no code, started no SolidWorks, ran no test and made no commit.* Under review, five
commits made from one `git archive` of `c583f48`, run folder `…\GearGeneratorProbe\w8-close-sw2026-20261116-001758`:

| commit | sections | log (under `probe/results/`), short name below |
|---|---|---|
| `c351b1f` | s0 s1 s3 | `w8-workbook-assembly-20261116-002245-s0-s1-s3.log`, "g1:N" |
| `8fd13c9` | s4 s5 | `w8-workbook-assembly-20261116-010649-s4-s5.log`, "g2:N" |
| `c2eed05` | s2 s7 | `w8-workbook-assembly-20261116-020805-s2-s7.log`, "g3:N", and `w8-s7-20261116-023505.json` |
| `aff9bfe` | r1 r2 r3 m5 m8 p1 p3 | `w8-close-20261116-025616-r-m-p.log`, "g4:N" |
| `fb85bcc` | the full window check | `w8-window-20261116-031412.log`, "win:N" |

I compared them with each section's last earlier run: s0/s1 `…-102101-s0-s1.log` and s1 of `…-220745-s1-s7-case8.log`,
s3 `…-114929-s3.log`, s4 `…-120522-s4.log`, s2 `…-151412-s2.log` ("s2-340:N", 34.0.0), s5 `…-140811-s5.log`, s7
`…-135401-s7.log`, the 2024 logs under `sw2024/`, W7's close `w7-close-20261115-021540-p-r-m.log` (`c0d3832`), p3's
last full run `w7-put-fix-20261115-014257-p3-p4.log`, and the window logs `w7-window-20261115-015017.log`,
`w8-window-20261115-150900.log` and `sw2024/w8-window-20261115-232543.log`. To compare check lines I took every
`ok`/`FAIL`/`NOTE`/`STOP` line of a section and replaced each number and path with a placeholder. I also read the
handoff's *W8 in detail* and *Rules carried over*, W8-PLAN §5 and §6, ruling 9.18, `findings.py` 1243-1317, both
probe scripts where they bear on this, and the earlier reviews' open points. Line numbers in docs are at `HEAD`
(`fb85bcc`); no source file changed after `c583f48` (`git diff --stat c583f48 HEAD` touches docs and results only).

**Verdict.**

- **The run is what the commits say.** Every count, every `done 0 failed`, the absence of any STOP, the snapshot
  `c583f48` and revision 34.1.1 in each assembly log's head, and s5 (g2, 01:06) before s2 (g3, 02:08) are in the logs.
  Every section the handoff's *Left* bullet defines ran to its `close section` line. Nothing inside a section was
  skipped, and every difference from its last earlier run is newer source or the run's own shape (p3 from a copy).
  The window check's stage 4 is skipped exactly as at W7's close, and nothing else there is skipped.
- **s7's and s5's corrected expectations are not weakened.** s7's is stricter, and s5's holds exactly what SolidWorks
  did. s5 (ii) still leaves the `AddMate5` status-5 path on the fake only.
- **s2 on 34.1.1 reads as reported.** It is s2's *current* sequence, not the one 34.0.0 ran, so it does not settle
  34.0.0's reading. Six documents need words changed (S1). The findings' values stand.
- **W8 cannot be written closed yet.** Two must-fix points: s6 is not ready to hand over (M1), and the window
  failure needs its ruling taken and written (M2). Five should-fix points are records and handoff work (S1-S5). The
  full list of what is left is under question 5.

---

## Question 1: do the logs hold what was said?

| section | `ok` lines (claimed) | last earlier run | difference, and why |
|---|---|---|---|
| s0 | 517 (517) | 517 + 1 NOTE (`31f5966`, 34.0.0) | "positions finding: True" → "False": the split of the finding (`TURN_…`). No NOTE this time |
| s1 | 555 (555) | 555 (`fe74276`, 34.1.1) | none but numbers; against `31f5966` the same True → False line |
| s3 | 409 (409) | 401 (`e670e7e`, 34.0.0); 409 on 2024 | +8, all `7c9634d` (the D10 status sentences, M2's status and "every sense read"); against 2024 only FIdler's clash order |
| s4 | 1864 (1864) | 1857 (`ee4ba90`, 34.0.0) | +7 "the status says …" checks, `7c9634d` (the review's S4) |
| s5 | 16 (16) | 14 + 1 FAIL (`148bac1`) | the FAIL replaced by two checks, `074df2c` (question 2) |
| s2 | 603 (603) | 591 (`4871a85`, 34.0.0); 603 on 2024 (`0e7f203`) | +12 from `7c9634d`/`f765894`, exactly as the 2024 review listed; against 2024 only clash order and largest-gap body names |
| s7 | 154 (154) | 100 + 5 FAIL (`725566e`) | the five FAILs became "as §2.3 has it" checks (`be07ebd`); the rest are new reads and holds (`48ab0aa`, `7c9634d` M2, `cbdb7ac`); no earlier check is missing |
| r1 r2 r3 m5 m8 p1 | 152 96 128 73 141 236 | the same counts in `c0d3832` | identical but numbers; m8 adds the exempt NOTE (g4:2345) |
| p3 | 290 (290) | 297 (`55e194b`) | that run built p3 fresh (no master in it): its 10 "built fresh" checks are replaced by 3 copy checks. Not a regression |

- *`done` lines.* g1:4205 "0 failed, 0 noted", g2:4292 "0 failed, 3 noted", g3:2497 "0 failed, 1 noted", g4:5052
  "0 failed, 1 noted". Every NOTE is the untitled notification box (`Title`, `Description`, `Button1` …), exempt.
  The `FAIL` lines at g2:4250-4256 are indented: they are the build's own step-6 report inside s5 (ii), which s5
  expects, not check failures.
- *Heads.* Each assembly log's first line names `(snapshot: c583f48)` and its second `SolidWorks 2026 (revision
  34.1.1)`. Each group is a different PID (18636, 46148, 43788, 47960; the window 16424), so each ran in its own
  session. `open before: []` in all four, and each section ends `left of ours []`.
- *One run or five.* The closing run is five invocations from one archive and one folder, not one `--only modes`
  call. That is the better shape: `--only modes` expands to `W8_ORDER` (probe 342), which puts s5 *after* s2, so the
  handoff's "s5 before s2" could only be had this way. Say so in the handoff (N1).
- *The window check.* `win:1` names `c583f48`. It does not name the revision; `fb85bcc`'s message says so. Its check
  lines are W7's close's, line for line, plus the W8 stage's 20. Those match 2024's W8 stage (the "head lines are
  §2.3's" checks included), with the same single FAIL (win:283). `win:68` is the only `skipped` line: "the W4 static
  record's footer: no --w4-static folder", the same line as `w7-window-…:68`. The W8 stage's read-state footer fits
  (win:234, 106 px, bottom 1483 of 1501).

## Question 2: s7 and s5, the corrected expectations

- **s7.** The five 135401 FAILs were one check: after a put, every mate the route suppressed was to be on "in every
  configuration". `be07ebd` holds each flag to `key_suppressed(n, c)`, §2.3's per-mode flags. The couplings are off by
  design in modes that do not engage them, so the old assertion was wrong and the new one is stricter: a flag left on
  where §2.3 has it off now fails, and before it passed. Everything added since asserts more, not less:
  - every turn held to `TURN_…` ("wants the turn read in every configuration"), and each moving put held to the put
    fact (g3:1993, 2018, 2070);
  - case 8's Update held to "went through and put every mode", with every configuration at its built frames after it
    (g3:2266-2269, `cbdb7ac`).
- **s5.** `074df2c` replaced "the build stops at the make in step 5 naming mode N and the mate" with two checks:
  - `AddMate5` status 1, no error (g2:4270);
  - step 6's mate check alone, every sentence of the form "In mode N, X cannot turn: SolidWorks reads it fully
    defined.", and the bodies exactly the seven of N's locked train (g2:4271).

  That is narrow and exact. It asserts what SolidWorks did in 140811 (status 1, step 6), not anything looser. What it
  gives up is §5's own clause, SolidWorks refusing the mate at the make. That was never a passing assertion (it failed
  in 140811), so nothing was weakened into passing. The path s5 (ii) takes now has a fake test
  (`tests/test_workbook_modes.py` 795-818, the seven sentences).
- **Status 5 is still fake-only.** Nothing in either run reaches `AddMate5` status 5 in a mode. The only cover is
  `tests/test_swbuild.py` 6198 (`test_a_mode_whose_coupling_over_defines_stops_the_build_naming_the_mode_and_nothing_is_saved`).
  The handoff's parenthetical (641) is right. Two rulings that s5 depends on are written only in the probe's comments
  (S2):
  - (i)'s gate refusal is "the coordinator's ruling 3 of stage 2d" (probe 198, 7329);
  - "whether it should name the mate is ruled separately" (probe 7373-7374).

## Question 3: s2 at ruling 9.18's open point

**Verified in g3.**

- *The first press.* After the user's turn in 2H, 4H, N and 4L each stand at 2H's turn (84, 104, 124). The quiet
  Update in 4L puts every mode (211-216). Its judgements on showing are 2H turned, 4H out of step at ModeSlv–FrontDog,
  N turned, 4L out of step at both couplings (221-224). After it every mode is at its built frames (237-245).
- *The fresh turn.* The fresh +37° in 2H (259-269) and the quiet Update in 2H that puts nothing (its status, 338).
  Then 4H (357), N (362) and 4L (367) each read every body at 2H's turn: Sun, InDog, RangeSlv and ModeSlv +37°, LoDog
  and the carrier +9.25°, each Pl −18.5°, the front train 0. 4L reads LoDog–RangeSlv 531.913 mm³ (369).
- *The Update in 4L after it.* It shows 2H first and puts there. Its judgements on showing are 2H turned, **4H out of
  step at ModeSlv–FrontDog, N turned**, 4L out of step at both (461-464; the same at 445-448, the lines the probe
  labels "post-check"). Had 2H's put reached 4H, ModeSlv would have stood at 0 against FrontDog's 0, in step. Every
  mode is at its built frames after the press (479-486).

So the turn reached every mode shown and 2H's put did not carry. That is 2024's s2 (`sw2024/…-233045-s2.log`
462-465), 2024's case 8, and 34.1.1's case 8, both before and again tonight (g3:2093 on).

**It is not 34.0.0's sequence.**

- s2-340 showed **4L alone** between the fresh turn and its second press (s2-340:354-358). `7c9634d` added the shows
  of 4H and N afterwards. On 34.0.0, 4H and N, not shown since the first press's put, read at the built turn
  (s2-340:433-435).
- So the closing run re-ran s2's *current* sequence, the one 2024 ran. It did not re-run the sequence that gave
  34.0.0's reading.
- s2-340's own first press, where every mode had been shown after the turn, read exactly what 34.1.1 and 2024 read
  (s2-340:224-227). The one divergent reading is the one press before which 4H and N were not shown.
- That points at the shows, not the revision, as the likelier cause. It is not shown: no version has run the
  4L-alone sequence again (N2).

**The words to change** (S1 gives replacement wording). The sentences that say the closing run's s2 "is what
re-reads" s2's sequence:

- `src/gear_generator/findings.py` 1273-1274 ("…stays unexplained between revision, machine and sequence; the
  closing run's s2 on 34.1.1 is what re-reads s2's own sequence.") and 1299-1301 ("…so s2's 34.0.0 reading stays
  unexplained; the closing run's s2 on 34.1.1 re-reads that sequence.");
- `W8-INTERFACES.md` 354-356, ruling 9.18 ("The closing run's `s2` on 34.1.1, which now shows 4H, N and 4L after the
  fresh turn and then presses in 4L, is what re-reads `s2`'s own sequence.").

Those that set 34.1.1 against 34.0.0 with case 8 alone, and so need the closing s2 added:

- `HANDOFF-WORKBOOK.md` 650-659 ("Read on 2026 34.1.1, not on 34.0.0 … stays unexplained; 34.0.0 has not run case 8")
  and 681-684 ("That is what 2024's and 34.1.1's case 8 read; 34.0.0's `s2` had found 4H and N at the built turn
  there.");
- `PLAN-WORKBOOK.md` 641-644 ("s7 case 8 on 34.1.1, in its own sequence, read …; 34.0.0's reading was not seen there
  and stays unexplained.");
- `W8-PLAN.md` 166-168 (the J11/J26 note) and 513-514 (the §1.9 note), the same sentence;
- `W8-INTERFACES.md` 419-423 ("For the user's list": s2 on 34.0.0 against case 8 on 34.1.1);
- the comment at `ui_text.py` 3584-3587 says the same and should follow.

Stale for another reason. Since tonight's s7 ran every case on 34.1.1, these "not yet" sentences are no longer true:

- `findings.py` 1258 and `W8-INTERFACES.md` 371 ("2026's s7 has not given that drive"). Case 5's FrontDog drive in N
  on 34.1.1 left FIdler at −2.5° in all four, the same place and not the same amount, as on 2024 (g3:2043);
- `findings.py` 1277 ("Not covered: … case 5's moving puts on 34.1.1"). They each stayed in their configuration
  (g3:1993, 2018, 2070);
- `findings.py` 1315 and `W8-INTERFACES.md` 373-375 ("s7's cases other than 8 on 34.1.1"; "a turn given while the
  configurations already stand differently on 2026"). Case 5's drive is exactly that.

**Do the values stand? Yes.**

- *`TURN_PER_CONFIGURATION_ON_2026 = False`.* The turn was read in every mode in s2 (357-369) and in s7 cases 1-4 and
  8 ("shared" fits, "per_configuration" ruled out).
- *`POSITIONS_PER_CONFIGURATION_ON_2026 = True`* (the put fact, read by nothing). Case 5's three moving puts, case 8's
  put and s2's second-press reading all keep a put in its configuration.
- *One reading against the put fact recurs.* The changed Update's put of FDrive in 2H was found in 4H and N and not in
  4L. That is the reading `findings.py` 1259-1261 cites for 34.0.0, and it came again on 34.1.1 (g3:723) and on 2024
  (`sw2024/…-233045-s2.log` 724). It is not a 34.0.0 peculiarity. The comment should say so (S1). No behaviour
  depends on it.

## Question 4: what has not been shown

**W8-PLAN §5 items no committed 2026 run shows:**

1. **s5's refusal by SolidWorks at the make**: `AddMate5` status 5 in a mode, and *"In mode N, … over-defines the
   assembly."* That path is fake-only (question 2). The doctored distance mate is refused at the app's gate instead
   (g2:3449, the sentence naming the script's own id `'inject1'`, which no user path makes).
2. **The built footer whole on the final source.** It was shown whole on 34.0.0 at `074df2c` at 100 % (1080 px wide,
   footer 156 px, bottom 1085 of 1097: `w8-window-20261115-150900.log`). At `c583f48` it fails on this device (win:283).
   Its sentences were all said; it is the height that fails.
3. **s6**, the person's step, on both versions.

Not a gap:

- §5's s2 sentence "on 2026 every other mode stands exactly as built" is superseded by ruling 9.18. The script holds
  the False reading.
- §5's "2H's 37° turn put back too" is not met by s2's own changed Update, because every mode is already at its built
  frames when it runs (g3:583-586, `turned False` everywhere). A turn put back by an Update is shown by s2's two
  putting quiet Updates (237-245, 479-486) and by s7 case 4's changed Update after a +37° (g3:1854, no failure, then
  every mode read) (N3).
- Sliding gears are fake-only by design (§0.1; neither fixture has one).

**SolidWorks 2024, against "Rules carried over" (803-805) and W8-PLAN §5 / §6 item 4.**

- *Run, all on the final app source.* s0, s1 (twice), s2, s3 and the window stage on 2024, and s7 with case 8 rerun
  alone. The source changes after `0e7f203` are comments only.
- *One full turning build with its edits.* s1 is the build. Its edits are s2's (quiet Updates that put, a changed
  Update) and s3's (D10 flags and values per configuration, the refusals, Build again… offered). s0 is a second build.
- *Every section where the versions were seen to differ.* s7 and s2 are where §1.9 said they might. No difference was
  found.
- *Small gaps, none required:*
  - s7 in full on 2024 had one failure, in case 8, the script's own put order (`8702389`). Case 8 then passed alone,
    but before `cbdb7ac`'s holds; 2024's s2 asserts the same thing (frames held after every putting Update);
  - the 2024 window stage was `--only w8`.
- *s4 and s5: neither is required.* No difference between the versions was ever seen in what they exercise, and
  W8-PLAN's 2024 list (§5 end, §6 item 4) leaves both out, as the 2024 review's N5 said:
  - s4's per-configuration value set while 2H is active is shown on 2024 by s3 (N's value set back) and s7 case 7;
  - its J14 flag switch is the same per-configuration suppression s3 shows;
  - its fifth configuration on Build again… uses no call a four-mode build does not;
  - s5 (i) makes no SolidWorks call;
  - s5 (ii)'s constrained-status read per mode is read in every 2024 build.

## Question 5: what remains before W8 is written closed

Besides the person's step s6 (on 2026 and 2024) and the two hand drags:

1. **Make s6 ready to hand over (M1):**
   - reword its text for `TURN_… = False`;
   - name the real file;
   - give its folder back as `s1`, on 2026 and on 2024;
   - hand it with the readings J1-J27 (W8-PLAN §6 item 5).
2. **Take and write the window ruling (M2).** If it changes the app, rerun the full window check on 2026, the W8 stage
   on 2024, and whatever the change touches. Otherwise the closing run is no longer from the final source.
3. **The positions records (S1):** the sentences listed under question 3, and the FDrive reading.
4. **Write s5's rulings down (S2).**
5. **The 2024 confirm review's S1-S6, carried into the close (S3).** The window check still does not log the revision
   (S4 there).
6. **The handoff (S4, S5):**
   - the W8 row, *Positions across configurations* and *Left*: the closing run recorded;
   - the two hand drags' folders: the closing run's `out\r1` and `out\p1` on this device;
   - the macro database line (W8-PLAN §6 item 6);
   - the suite as measured: Linux 3280 passed, 1 skipped, and 1 failed, the r2-parts width test, a font matter on
     this host; it passes under Windows Python.
7. **W8-PLAN §6 item 6:**
   - PLAN-WORKBOOK §4.5's readings and a dated note under §6's W8 row saying W8 closed;
   - UI-DESIGN §9's last words;
   - the three mode boards redrawn together (handoff 591-592).
8. **This review's points in; then the close itself,** committed and pushed.

## Question 6: public repo

Clean. Across the five logs and the JSON:

- *No user document.* `open before: []` in every assembly log, and every file named is the run's own (`TransferCase_E4*`,
  `Gear_m…`, `Dog_m…`, `Sleeve_m…`, `Bevel_…`, `Planetary_4to1…`, `Reducer_12to1…`).
- *No licence edition and no main-window title.* The DIALOG lines are SolidWorks' progress boxes, the open-summary
  panel and the untitled notification box. The balloon tips are "Simplified Interface" and "The sketch is no longer
  over defined."
- *No e-mail and no host name.* The only personal datum is `C:\Users\M0obo\…`, which earlier logs carry: 66, 52, 4, 91
  and 27 lines in the five logs, none in the JSON.

---

## Points

**M1. Must fix before s6 is handed over: its text predicts what the 2026 finding now contradicts, and its folder is
not where its record points.**

- *The prediction.* W8-PLAN §5 (1386-1395) still says that after a drag in N and back in 4L, an Update in 4L "should
  say the gears stand where they were turned and that the other modes were not shown". On 34.1.1 (and 2024) a turn in
  N shows in 4L. In N no sleeve engages a dog, so dragging the sun turns LoDog but not RangeSlv. In 4L the two are
  coupled, so 4L will read out of step, and the Update will put every mode and say so (as g3:461-464).
  `W8-REVIEW-9-18.md` 344-347 asked for exactly this rewording. It has not been done.
- *The file name.* The text names "TransferCase.SLDASM"; the file is `TransferCase_E4.SLDASM`.
- *The folder.*
  - `give_back_r1` (probe 8225-8243) renames r1.master and p1.master back for the W6 and W7 steps (g4, end). It
    does nothing for W8. No log prints a W8 person step.
  - The E4 built tonight stands as `out\s1.master`, whose record names `out\s1`. Opened from there, the workbook
    would read as another's, and s6's Update press would not do what s6 asks.
- *What to do.* Rename it back to `s1` (with nothing open), and the same for the 2024-built E4. Write the folder
  into the text.

**M2. Must fix: the window failure needs its ruling taken and written before W8 is written closed.**

- *Where it stands.* `fb85bcc` leaves it "for the ruling already asked". It is the only failed check of the closing
  run, on the final source.
- *What the ruling can be.*
  - (a) Accept it as the layout's known limit. Write it into UI-DESIGN §9 and the handoff's "Open, for the user to
    overrule", with the 2024 review's S6: by arithmetic, a 1080-px screen at 100 % would cut it too.
  - (b) Change the layout. Then rerun the full window check on 2026, the W8 stage on 2024, and any section the change
    touches.
- *Either way, write it down.* As it stands, *Left* lists "that ruling" and W8-PLAN §6 item 4's "the window check
  pass(es)" is not met.

**S1. Should fix (records): the positions sentences.** The places are listed under question 3. Suggested sense for
the "re-reads" sentences:

> The closing run's s2 on 34.1.1 (`c583f48`, `…-020805-s2-s7.log` 357-369, 461-464) ran s2's current sequence, which
> shows 4H, N and 4L between the fresh turn and the press (`7c9634d`), and read what 2024's s2 and both case 8s read:
> the turn in every mode shown, and 2H's put not carried. The 151412 sequence, 4L alone shown before the press, has
> not run again on any version, so 34.0.0's reading stays unexplained between revision, machine and sequence. On
> 34.0.0 itself, the first press, made after every mode had been shown, read the same as 34.1.1 and 2024.

Also:

- add the 34.1.1 case 5 readings where "not yet" now stands;
- add to `findings.py` 1259-1261 that the changed Update's FDrive reading recurred on 34.1.1 and 2024;
- carry the closing run's case 7 suppressed-sense read on 34.1.1 (g3:2382, τ (1, 1)) into the
  `SUPPRESSED_GEAR_MATE_SENSE_READ` comment beside 2024's (the 2024 review's S1);
- optionally, `tests/test_findings.py` 1402-1409's docstring.

No value changes.

**S2. Should fix: s5's two departures from W8-PLAN §5 are rulings recorded only in the probe.**

- *What is recorded where.*
  - (i)'s refusal at the gate is "the coordinator's ruling 3, stage 2d" (probe 198, 7329).
  - (ii)'s acceptance of step 6 naming bodies, not the mate, "is ruled separately" (probe 7371-7374). No such ruling is
    in `W8-INTERFACES.md` §9, PLAN-WORKBOOK §4.5 or the handoff's rulings list.
  - W8-PLAN §5's s5 (1380-1385) and §6 item 4 are not annotated.
  - `W8-REVIEW-DEMO-S2-S7.md` S3 asked for a ruling that the status-5 clause stays fake-only.
- *What to do.* Write one ruling covering all three: status 5 fake-only; the doctored distance mate refused at the
  gate; step 6's sentence naming the locked bodies, the mate not named. Annotate §5's s5. Put the "names the bodies,
  not the mate" choice on the user's list.

**S3. Should fix: the 2024 confirm review's six should-fix points are still open.** `fd44e7c` says they "go in with
the close". None is in at `HEAD`:

- `SUPPRESSED_GEAR_MATE_SENSE_READ`'s "Not covered: SolidWorks 2024" (`findings.py` 1377);
- the 2024 s2 sentence (handoff 681-684), which S1 above also touches;
- the 2024 comments citing s7 alone;
- the snapshot and revision logging;
- the W8 row's "No W8 code has run on SolidWorks" (handoff 46);
- "a short screen".

The revision point applies again tonight: win:1 names the snapshot, but not the revision, so "34.1.1" for group 5
rests on `fb85bcc`'s message.

**S4. Should fix: the probe's own description of `--only modes` is stale.** Probe 127 says it "runs s0 to s4, the
sections written so far: s5–s7 are a later stage's". `W8_ORDER` (342) is s0 s1 s2 s3 s4 s5 s7, with s5 after s2, the
order the closing run had to avoid. Correct the sentence. Either put s5 before s2 in `W8_ORDER` or say why not. Add
`s1` to `give_back_r1` (M1). These are probe changes, reviewed like any other.

**S5. Should fix: the handoff's pointers for the person's steps are out of date.**

- *Questions waiting* 5 (765-768) sends the two hand drags to folders "on the machine W5 to W7 ran on". The closing
  run has just left fresh ones for them on this device: `…\w8-close-sw2026-20261116-001758\out\r1` and `\out\p1`
  (g4, end).
- The handoff should name these, and, after M1, `…\out\s1` for s6.

**N1.** Record in the handoff that the closing run was five groups, each in a fresh session, from one archive and one
folder (s2, s4 and s7 copying g1's s1.master). Say why: `--only modes` cannot put s5 before s2. The 2024 rule ("a
fresh session per section") already prefers that shape.

**N2.** The likelier cause of 34.0.0's reading is the sequence: whether 4H and N were shown between the turn and the
press. That is inference from the 34.0.0 log's two presses. Nothing depends on it, because every Update that puts
shows and puts every mode. A run of the 4L-alone sequence on 34.1.1 or 2024 would settle it, if the user wants it
settled.

**N3.** If W8-PLAN §5 is annotated at the close, say that "2H's 37° turn put back too" is shown by the putting quiet
Updates and by s7 case 4, not by s2's changed Update, which finds nothing turned.

**N4.** `c351b1f`'s message records the suite at the snapshot: Linux 1 failed,
`test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`
(`tests/test_workbook_window.py` 2036), put down to this host's Tk font. Windows 160 passed, 1 skipped. Put it in the
handoff beside the tkinter note (720-723), so the next host does not mistake it for a fault.

**N5.** The probe still labels each mode's judgement on showing "post-check of …" (g3:205-208, 445-448). This was
noted twice before (2024 review N6, case 8 review). Rename it when the probe is next touched.

## What I could not verify

- That group 5 ran on SolidWorks 2026 34.1.1. The window log names no revision.
- Anything on screen: the shot `20-transfer-case-built.png`, the screen size and scale, and whether the earlier
  window stages' footers are whole. Those stages have no height check.
- The suite counts in `c351b1f`'s message (I ran no test), and that the r2-parts failure is the font alone.
- That `out\s1.master` (2026) and the 2024 run folder's E4 still exist and are unopened. They are on the Windows
  host's disk, not in the repo.
- Whether this device is the machine W5 to W7 ran on. The paths have the same account name on every host.
