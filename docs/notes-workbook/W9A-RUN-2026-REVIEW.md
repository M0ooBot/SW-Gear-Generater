# Review of W9a's demonstration run on SolidWorks 2026

*Independent, 2026-11-16. I started no SolidWorks or Excel, changed no source, test or document, and ran one suite
file (`tests/test_findings.py`, 131 passed, through the repo's `.venv`). This file is the only one I wrote.* Under
review: the four logs and JSONs committed in `e7a58d7`, read against the script at the commits they ran (`9dded70`
for runs 1 to 3, `311ce5a` for run 4) and the plan.

| run | log (cited as) | JSON | snapshot | sections |
|---|---|---|---|---|
| 1 | `probe/results/w9a-demo-sw2026-20261116-1-m3-setup-go.log` ("r1:N") | `w9a-demo-20261116-204840.json` | `9dded70` | m3, setup, go |
| 2 | `…-2-m1-refuse-stopped-by-a-dialog.log` ("r2:N") | `w9a-demo-20261116-211735.json` | `9dded70` | m1, refuse (hung in its seventh step) |
| 3 | `…-3-again-reducer-k3-nocarrier.log` ("r3:N") | `w9a-demo-20261116-215415.json` | `9dded70` | again, again-dirty, again-closed, reducer, k3, nocarrier |
| 4 | `…-4-lightweight.log` ("r4:N") | `w9a-demo-20261116-221451.json` | `311ce5a` | lightweight |

I read the plan's §0.2 (K2, K3, K4, K11), §0.3, §2.1, §4's M1 to M3, §5's W9a and *Changes after S0 and its review*;
the demonstration note and its pre-run review; `W9A-INTERFACES.md` items 10 to 12; `W9-S0-REVIEW.md`; the W9
findings and their tests; and *Rules carried over*. I read each section's key passages in full and searched the rest.
Where the script's checks matter I read them at the run's commit (`git diff 9dded70 311ce5a` touches only the
watch and the lightweight section; `git diff 9dded70 e7a58d7 -- src` is empty, so the app the runs drove is the app
at `e7a58d7`). Script line numbers here are HEAD's (`311ce5a`). The functions cited are the same at `9dded70`,
except the watch and `section_lightweight`. The working tree has uncommitted changes to `swbuild.py`, `findings.py` and `tests/test_swbuild.py`
(the coordinator's M3 change, by its look). I did not review them; where the drafted finding comments in it
misstate the logs, I say so in finding 2, since those comments are what is about to be set.

---

## Verdict

- **The logs say what the coordinator's readings (a), (b), (d), (e), (f) and (g) say, each with limits it does not
  state.** `go` shows the *Done when*'s two Updates on 2026. `refuse` shows its two refusals and four more, each
  before any write. The `again` sections show the old assembly read behind another document and left as it was.
  `nocarrier` reads route (c1) clean on a train with no carrier. Every one of those checks could have failed: the
  same "on its gear as set up" test failed at 0.60 for S0's routes (a) and (b).
- **Reading (c) is right on the facts, and the checks behind it could not fail on the point it rests on.** m3's two
  Update checks pass whether the Update goes ahead or stops (script `:893`, `:948`). So "the Update goes ahead" and
  "the Update stops" are facts from the result lines, not assertions. k3 is the one assertion, and it failed: on
  2026 an ordinary value Update that rebuilds a user's keyway in an app part into error stops as a failure. It also
  leaves its write unsaved, and its sentence does not name the keyway. K3 is not met on 2026. The app change the
  coordinator intends is the right direction (§2.1 item 5 asks for it). It needs four conditions, given in finding 1.
- **One refusal names more than the run set up.** `lightweight` set Sprocket-1 lightweight, and the app refused
  naming Sprocket-1, Sprocket-2 and Sprocket-3 as lightweight. No line says whether the other two were (finding 3).
- **Findings that may be set now,** each scoped as in *How each proposed finding may be set*:
  - `USER_MATE_PUT_NO_CARRIER_ON_2026 = True`;
  - the three M3 readings on 2026, after the corrections in finding 2;
  - the SOLIDWORKS CAM save box on 2026, cited from the committed log.

  Every `_ON_2024` stays `None`.
- **W9a's *Done when* on 2026 is not yet met.** Shown at `9dded70`: the go clause and both refusals. Not shown or not
  met:
  - K3 in an app part (k3's failure);
  - M1 in full (concentric, width, limit, path and the sub-assembly leaf were not read, and only width, limit, path
    and the leaf are ruled into S5);
  - the window check's W8 stage;
  - the suite;
  - 2024.

  Runs 1 to 3 ran under `9dded70`'s watch, which only noted a dialog during a job. So the phase's closing run must
  repeat every section under `311ce5a`'s watch or later.

## The run table, as verified

| | run 1 | run 2 | run 3 | run 4 |
|---|---|---|---|---|
| started (local) | 20:48:40 (r1:2) | 21:17:35 (r2:2) | 21:54:15 (r3:2) | 22:14:51 (r4:2) |
| snapshot | `9dded70` | `9dded70` | `9dded70` | `311ce5a` (committed 21:57:05, after run 3 began) |
| SolidWorks | 34.1.1, PID 6628, 1.05 GB at attach (r1:4) | the same session, 1.16 GB (r2:4) | 34.1.1, PID 53340, 0.68 GB, fresh (r3:4) | run 3's session, 1.06 GB (r4:4) |
| Excel (own) | 35452 | 43376 | 34588 | 49716 |
| `ok` lines | 134 | 93 | 132 | 22 |
| FAIL lines | 0 | 1 (WorkerHung, r2:359) | 1 (k3, r3:1441) | 0 |
| done line | 0 failed, 1 noted, 0 STOP (r1:381) | 1 failed, 6 noted, 0 STOP (r2:372) | 1 failed, 1 noted, 0 STOP (r3:1606) | 0 failed, 0 noted, 0 STOP (r4:97) |
| JSON `revision` | [34, 1, 1] | [34, 1, 1] | [34, 1, 1] | [34, 1, 1] |

| section | `ok` | failed | time | note's figure |
|---|---|---|---|---|
| m3 (with the user parts' build) | 27 | 0 | 442 s (r1:120) | 7 min ✓ |
| setup | 51 | 0 | 241 s (r1:231) | 4 min ✓ |
| go | 55 | 0 | 1030 s (r1:374) | 17 min ✓ |
| m1 | 24 | 0 | 191 s (r2:71) | 3 min ✓ |
| refuse | 68 | 0 (but cut by the hang) | 1932 s (r2:358) | "32 min with the lightweight step": about 20 min were the six steps, 10 min the wait behind the CAM box (`save_user`'s 600 s timeout), the rest the seventh step's quiet press |
| again | 18 | 0 | 395 s (r3:294) | 6 min est. |
| again-dirty | 19 | 0 | 391 s (r3:578) | 6 min est. |
| again-closed | 16 | 0 | 100 s (r3:853) | 5 min est. |
| reducer | 14 | 0 | 88 s (r3:1381) | 4 min est. |
| k3 | 18 | 1 | 59 s (r3:1444) | 6 min est. |
| nocarrier | 46 | 0 | 159 s (r3:1599) | 11 min est. |
| lightweight | 21 | 0 | 435 s (r4:91) | 6 min est. |

The JSONs' `sections` agree with the logs (seconds, `failed`), as do their `proposal`s (r1:118, r3:1598) and `notes`.
Memory stayed between 1.05 and 1.71 GB private and 10.28 GB or more free in every run. Every section but `refuse`
ended clean, with no document of its copy left open and Excel's workbook closed (the "ends clean" lines; r1:376,
r3:1601, r4:93 "left of ours []; stray []; lost []"). Run 2 ended with everything left open in a hung session
(r2:362). No log says how session 6628 ended; run 3 attached to a fresh one.

---

## Findings

**1. Must fix before W9a closes: K3 fails on 2026, and an Update with only the user's feature in error stops after
it has written.**

- *What the logs show.* k3: G1's Bore 8 → 14 rebuilt the user's keyway into error (code 71). G1's app features read
  no error (r3:1439-1440), and the keyway was not in error before (JSON `sections.k3.update.in_error_before` []).
  - The Update's result lists the keyway in `user_features_in_error` (r3:1432).
  - It failed on the assembly's rebuild, "SolidWorks reported an error rebuilding Reducer_12to1.", with "It had
    already changed Gear_m1.5_N17, not saved" (r3:1434).
  - The sentence does not name the keyway (r3:1441, the run's one FAIL).

  m3's second Update did the same with the keyway in the user's own Sprocket part. Its sentence said "Your Sprocket-1
  was already in error before this Update" and "It had already changed Gear_m1.25_N29, not saved". It stopped before
  any show or put (r1:110-115).
- *What the plan asks.* K3: the job reads each user feature's error state afterwards and names any in error, as
  theirs. §2.1 item 5: "A rebuild error that comes only from the user's features does not stop the job, if M3 shows
  the rebuild reports it." M3 now shows that it does on 2026: the assembly's rebuild returns False (r1:90). The app
  already lays a part's failed rebuild to the user's features alone (`W9A-INTERFACES.md` item 11, gated on
  `WHATS_WRONG_OPENS_ON_PART_REBUILD`). Item 11 left the assembly's rebuild a failure only because M3 was unmeasured.
- *What the change must hold to.* I agree with the coordinator's rule only with all four of these:
  1. *Something of the user's must be found in error.* A False rebuild with nothing found in error stays a failure.
  2. *"Nothing of the app's own in error" must be a whole read.* That means every app mate in the mode rebuilt, and
     every app feature (the record's list) in every app part, the layout and carrier parts included. An unread one
     counts as in error.
  3. *An app component's own error code must not count against the app when it comes from a user feature in its
     part.* In m3 a feature in error in Sprocket.SLDPRT made the component Sprocket-1 read code 1 (r1:90). In k3 the
     same should make G1's component read in error, though k3 never read component codes. A rule that tests "no app
     component in error" would still fail k3.
  4. *Gate on a finding, per version.* `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_<year>` is False on 2026 and `None`
     on 2024, as item 11 gates the part on `WHATS_WRONG_OPENS_ON_PART_REBUILD`. On 2024 the failure stays until its
     confirming m3 and k3 run.

  The change also has to reach both paths the runs took. m3's failure came from the modes path (" in H"); k3's came
  from a gearbox without modes. One case is unmeasured: going on to put a carried component whose own part is in
  error. In m3 the component in error was not locked to a gear. Until that is run, either refuse such a press before
  any write, or say in the finding that it is not covered.
- *What must be repeated.* m3's second Update and k3, at the snapshot with the change. Each must assert that the
  Update goes ahead (`ok` True, the puts and post-checks as in m3's first Update), that the sentence names the keyway
  (k3) or Sprocket-1 (m3) as the user's, and that the app's features read no error.

**2. Must fix before the findings are set: the M3 readings must be worded to what was measured, from committed lines
only.**

- *The readings themselves are sound.* With two user mates over-defined (UserFront 46, UserGap 47) the app's
  assembly rebuild (`ForceRebuild3(True)`) returned True, GetWhatsWrongCount read 3, and no window came up (r1:48-51).
  Suppressing UserGap brought every code back to 0 (r1:84-85). With one user feature in error in a part the rebuild
  returned False and GetWhatsWrongCount read 1, with no window (r1:88-91). The app's Update with the mates in error
  went ahead and named both as the user's, in error before (r1:71, 73, 81-82). The one with the feature in error
  stopped (r1:110-117; r3:1432-1441).
- *The checks could not fail on go or stop.* `check(result.ok or named, …)` (`:893`) and `check(result.ok or
  "Sprocket" in desk.note[0], …)` (`:948`) pass either way. The ok line at r1:81 even says "an Update that fails …
  (ok True)". `"whats_wrong_window": False` in the JSON's proposal is hard-coded (`:960`). The evidence for "no
  window" is the `windows new none` lines (r1:45, 49, 84, 90). At `9dded70` there is also the absence of a "NOTE a
  SolidWorks window" line in runs 1 and 3; that watch only noted a dialog during a job.
- *Corrections to the comment drafted in the working tree:*
  - *UserFront is not "between user components".* It joins Sprocket-1's Front plane to the layout's (script `:830`,
    `"lay:plane1"`), so it touches an app component. UserGap joins Sprocket-1 and Housing-1. Write "two user mates
    on one user component, one to the layout's plane and one to the user's fixed housing".
  - *"The part's own rebuild reported it" in k3 has no log line.* k3 reads no part rebuild's return and no What's
    Wrong count. The only evidence is the failure entry naming the assembly (r3:1432, 1434) and the trace's two
    `ForceRebuild3` calls (r3:1435). Say only that the Update's assembly rebuild reported failure.
  - *"show errors every rebuild" was not read in W9a's run.* The draft says so, and it must stay. The toggle was
    last read on in S0's P0, another session of the same install (`w9-s0-sw2026-20261116-050200.log:9`). The closing
    run's m3 should read it (as S0's P0 did) and put it on the record.
  - *Cite no uncommitted run.* The note's *Found on SolidWorks* item 2 rests on m3's first run at `2920a09`, which is
    not committed. r1:49 reproduces the reading (the same codes, True, What's Wrong 3), so cite that.
- *What must not be concluded.* What was measured:
  - two mates of one kind (distance), over-defined;
  - one feature kind (a cut swallowed by the bore, code 71), in one part at a time;
  - RangeBox in H, and the 12 : 1 without modes.

  It says nothing about a user mate in error of another error kind, a user mate in error on an app gear, several
  parts in error, an app feature in error, or 2024. It does not say that the app may go on after a False rebuild:
  that is finding 1's change, gated on these readings.

**3. Must fix before W9a closes: the lightweight refusal names three components where the run set one.**

- `lightweight` set Sprocket-1 lightweight (`SetSuppression2(1)`, reads 1, r4:32). The footer foresaw, and the press
  made, three refusals: Sprocket-1, Sprocket-3 and Sprocket-2 each "is loaded lightweight in RangeBox.SLDASM"
  (r4:57, 67, 73-76). `refuse` at `9dded70` gave the same (r2:348-351).
- The app reads `GetSuppression2` per top-level component (`swcom.components`). So either SolidWorks made every
  instance of Sprocket.SLDPRT lightweight when one was set, or the read is wrong. Sprocket-4, the fourth instance, is
  not carried, so it would not be named either way.
- The script's check (`"Sprocket-1"` among the words said, r4:78) cannot tell the two apart. No line reads
  Sprocket-2's or Sprocket-3's state, before the press or after Sprocket-1 is resolved again (r4:88-89).
- The refusal errs on the safe side, and review B's item 4 is shown for Sprocket-1. But the sentence tells the user
  that two components are lightweight that may not be. Before W9a closes, the closing run's lightweight section must
  read every instance's state by the script's own raw read, after the set and after the reset, and assert the
  refusal names exactly those that read 1 or 4. If SolidWorks makes every instance lightweight, say it as a fact in
  the note (and the sentence is right). If not, the app's read is a fault to fix.

**4. Must fix before W9a closes: M1 is not answered in full, and the plan's *Done when* still says it is.**

- *Read on 2026, by the app's own `mate_info` and inventory, marking nothing* (r1:167-177, r2:48):
  - kinds: coincident (type 0, axis to axis), distance (5), angle (6), lock (16) and gear (10);
  - joins: user–user (UserLock3, UserDist4, UserGear5), user–layout (UserAxis1/2/4, UserAngle4, UserDist5) and
    user–gear (UserLock1 to Sun, UserLock2 to RangeSlv);
  - a distance mate suppressed in the active mode reads whole, and the inventory gives its modes as N and L
    (r2:49, 54, 67, 69).

  `refuse` adds a coincident on Sun's axis, judged as touching Sun (r2:177-186).
- *Not read:* concentric (type 1; every "axis" mate here is a coincident, as the app mates gears), width, limit, path,
  a user gear mate on an app gear, and a leaf in a user sub-assembly. The note moves width, limit, path and the leaf
  to S5 in W9c's sessions (as the pre-run review's point 14 asked). It does not list concentric.
- *What to do.* Add concentric to that list. Record the move in the plan, under a dated *Changes after W9a's run*,
  as a ruling for the user to overrule, since §5's *Done when* says "M1–M3 answered" and §4's M1 row lists them.

**5. Should fix: `refuse` is recorded as passed though the hang cut it, and its time is mostly the wait.**

- The seventh step's `save_user` hung behind the CAM box (r2:354-355). Its 600 s timeout raised WorkerHung, and the
  section still wrote "time refuse: 1932 s; 0 failed" (r2:358). The JSON says `refuse` `failed: []`.
- The six steps that matter all ran and passed before it (r2:141-304). But the section never reached `end_copy`.
  The record of a section cut by a run-ender should say so (for example `failed: ["cut: WorkerHung"]`).
- The done line counts 0 STOPs while the JSON's `stops` holds the hang (r2:372 against `stops` in the JSON). The
  note lists a hung worker among the STOPs that end the run, so the two should agree.
- The note's "32 min (measured, with the lightweight step)" should become about 20 min for the six steps.

**6. Should fix: the bore step's mark check was blind for the assembly, and a refused press's trace does not see a
global's write.**

- *The mark check.* After the person's save before "refuse bore typed", SolidWorks updated the assembly ("Component(s)
  have been modified", r2:252), and the read before the press found RangeBox.SLDASM already marked (r2:253). The
  STOP on a document "marked by the refused press" compares after with before, so it could not see a mark on the
  assembly in that step. Sun's part stayed clean.
- *The trace.* W8's `nothing_changed_calls` traces `SetSystemValue3`, but not the equation write that sets a part's
  global. m3's failed Update changed Sun's Backlash with no such call in its trace (r1:113 against r1:112).
- *Why the claim still stands.* Each refused press could only have written Sun's globals, and `refuse_press` reads
  Sun's globals before and after (`:1415`, `:1424`). So "nothing written" holds for these six steps.
- *For the closing run.* Rebuild before the person's save in that step so the press starts clean, and add the
  equation write to the trace or say in the note that the globals' read covers it.

**7. Should fix: m3 does not show the footer before its presses.**

§2.1 item 2 asks that a user item already in error is named before the press. m3 calls no `ahead_of` before either
Update (r1:66-67, 106-107), so whether the footer said UserGap or Sprocket-1 was in error is not shown. Add it with
finding 1's rerun.

**8. Should fix: the note's citations and estimates.**

- *Found on SolidWorks* item 1 cites `w9a-demo-sw2026-20261116-204824\stdout-2.txt` lines 413-520, which is not in
  the repo. Cite r2:354-359.
- Item 2 cites the uncommitted `2920a09` run (finding 2).
- The section table's estimates can now be the measured times above.

**9. Should fix: k3's proposal says `named_as_users: true` (r3 JSON) where the sentence named nothing.**

The field is `bool(named)` from the result's `user_features_in_error`, not the sentence (script `:1879-1886`). Name
it for what it is, or add the sentence's test beside it.

**10. Note: the bore sentence says "0 in the workbook" for a blank cell.** Sun's Bore is blank in the fixture
(`tests/workbook_fixtures.py:81`, `_gear(..., "10")` with no bore). The sentence reads "is 12 in SolidWorks and 0 in
the workbook: type 12 in Gears!J2, or set it back to 0" (r2:258). The cell is named, as the *Done when* asks. "Blank
(no bore)" would read truer, for the small fix round with R1 to R3.

**11. Note: "post-check of H: … out of step [('RangeSlv', 'HighDog')]" after go's slide press (r1:352) is not a fault.**
It is the `ModeCheck` of H as found on showing, before the put (`swbuild.ModeCheck`: "when it was shown and before
anything was put"). Every app body then read at its frame in H, N and L (r1:368-370). The script's label
"post-check" is W8's and misleads.

**12. Note: sessions.** Run 1 attached to a session already at 1.05 GB, not a fresh one (r1:4). Run 2 used the same
session, and run 4 used run 3's session after nocarrier (r4:4). The note asks for a session started for the run.
Nothing here is shown to depend on it, but the closing run should start fresh.

**13. Note: smaller items, none changing a reading.**

- The CAM NOTE says "before this run made any configuration" (r2:355), which is W8's boilerplate and misleading.
- The part rebuild in m3 brought two new windows of class `tooltips_class32` and `SysShadow`, untitled. They are not
  dialogs and were rightly not counted (r1:88).
- nocarrier's footer before the first patched press still showed the recorded refusal (r3:1534). So "the carry
  foreseen is the carry done" is shown on its second press only (r3:1592).
- `go` does not read Sprocket-4's or Housing-1's absolute frames. That they did not move rests on the trace, which
  has no put of either (r1:302, 358), and on Sprocket-4's distance to Sprocket-3 (r1:312-314, 368-370).
- `9dded70`'s and `311ce5a`'s script changes ran without an independent review. I read `311ce5a`'s diff, the watch
  and the lightweight section, and found nothing wrong. `9dded70`'s m3 set-up is borne out by its baseline (r1:41-46).

---

## The coordinator's readings, one by one

- **(a) `go`: true.**
  - *What ran.* setup.master's copy, as set up in r1:143-163. The user turned the train +37° in H, then a value
    Update (Sun's Backlash 0.4, r1:265-317). The user turned it +37° in L, then a slide-offset Update (RangeSlv
    L = +5.5, r1:321-372).
  - *What each press did.* Each put 33 times, in all three modes: eight app bodies and three sprockets, in each
    mode, all app bodies or locked sprockets (r1:294, 302, 350, 358).
  - *After each press, in H, N and L shown:*
    - every app body was at its frame on record (6.6e-10);
    - each locked sprocket was on its gear, worst 7.1e-15;
    - no mate was in error;
    - Sprocket-4 was 90 mm from Sprocket-3;
    - the train read free;
    - the user's mates were on in their modes and joined what they joined before;
    - the keyway read code 0 (r1:311-316, 367-372);
    - the footer's foreseen carry was the carry done (r1:301, 357).
  - *What was exercised.* Locks on in every mode only, with one chain (Sprocket-3 on Sprocket-1). The turn went one
    way. One axial carry: Sprocket-2 with RangeSlv's 0.5 mm in L. Each carried sprocket was put six times. The
    keyway was rebuilt by the value press only; the slide press changed no part.
- **(b) `refuse` and `lightweight`: true, with findings 3, 5 and 6.** Each of the six steps was refused with no
  changing call in its trace, frames, codes, flags, entities, marks and Sun's globals as before, and the refusal
  recorded and said in red (r2:141-150, 186-194, 213-221, 239-247, 267-276, 295-304).
  - The housing lock and the lightweight component were foreseen before the press (r2:123-127, 150; r4:57-62, 87).
    The other four were recorded after it, as K4 has it for what the record did not hold.
  - "Has changed since" was said after a workbook change (r2:164-169).
  - The housing lock is named by Housing-1 (r2:141), and the bore by `Gears!J2` (r2:276).
  - The two-body and the all-at-once steps also drew the solver's tie, with app mates already in error before the
    press (r2:226, 281). The note's "one train" caveat stands.
- **(c) m3 and k3: true on the facts, with finding 2's limits.** The app change is finding 1.
- **(d) the `again` sections: true.**
  - The read ran alone with Housing.SLDPRT in front before and after. It left the save flag, rebuild state
    (0, or 1 in again-dirty), active configuration H, mates, flags, entities and frames as before, with no window
    (r3:51-56, 336-342).
  - The build changed none of those on the old assembly or the user's files' times (r3:287-290, 571-574).
  - again-closed read nothing and opened nothing (r3:619, 847-849).
  - The question and the result say what stays behind, with the record's time (r3:46-47, 284-286, 614-615, 845).
  - *What was not exercised.* The old assembly was always in H, with nothing lightweight and nothing in error.
- **(e) `nocarrier`: true for the two presses run.**
  - The default refusal was foreseen and made, writing nothing (r3:1503-1532).
  - With the finding patched in the process only (r3:1533, 1596), two presses ran, each after the user's +37° turn
    of G1: G4 At 27 → 30, then back.
  - Each press made seven puts with the gear mates on (r3:1545, 1588) and read clean, and again after a further
    rebuild (r3:1551-1552, 1594-1595). The proposal is True with `presses_clean [true, true]` (r3:1598).
  - The trace's two `SetSuppression2` calls per press are not named in the log. That the gear mates stayed on rests
    on the branch's code path (`_put_train`).
- **(f) setup and m1: true for what was read** (finding 4). M2 is shown in Sun's part (r1:178-179, 217) and G1's
  (r3:1410), with the keyway's code read after a rebuild in go and k3.
- **(g) the CAM box: true, and the app's W9a paths make no such save.**
  - The box came up under the script's own `SaveAs3` of an assembly holding a lightweight component (r2:354-355).
  - The Update never saves. Build again… saves only the new revision, which holds none of the user's components
    (r3:276), and never opens a closed old assembly (r3:848).
  - The box was never answered. What Yes or No does, and whether the save would complete, were not seen.
  - Two findings already set say the add-in also boxes an open with lightweight components and the close of a
    modified cross-version assembly (`LIGHTWEIGHT_OPEN_RAISES_AN_ADDIN_DIALOG`, `CROSS_VERSION_CLOSE_ASKS_TO_SAVE`).
    W9d must expect all three.

## How each proposed finding may be set

**`USER_MATE_PUT_NO_CARRIER_ON_2026 = True`** (`_ON_2024` stays `None`).

- *Evidence:*
  - r3:1463, the user's work;
  - r3:1480, the branch labels;
  - r3:1503-1532, the default refusal;
  - r3:1541-1552 and 1584-1595, the two presses and their reads;
  - r3:1598, the proposal;
  - the JSON's `sections.nocarrier.clean` [true, true] and its `proposal`.
- *Scope:*
  - the 12 : 1 (G1 → G2, G3 locked to G2 → G4), one configuration, no modes;
  - user locks to the driving G1 and the driven G4, and a chain of one;
  - each press after a +37° turn of G1, the whole train put back to its built turn, with G4 moved 3 mm along S3
    and back;
  - two presses, seven puts each.
- *Not measured:* a no-carrier train in an assembly with modes (the branch gates it too, since
  `user_carry_branches` joins every mode's links); a user lock to G2 or G3, the gears the app's own lock joins; an
  idler; the turn the other way; 2024.

The comment drafted in the working tree says this and cites the right lines. I would accept it as drafted.

**The M3 readings, with finding 2's corrections.**

| name | 2026 | 2024 | evidence |
|---|---|---|---|
| `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_<year>` | True | None | r1:48-51, 84; JSON `sections.m3.mate_error`, `proposal.M3` |
| `ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_<year>` | False | None | r1:88-91 (JSON `feature_error`, `part_rebuild`); r3:1432-1440 (JSON `sections.k3.update`) |
| `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_<year>` | False | None | r1:45, 49, 84, 90 ("windows new none"); no window NOTE in r1 or r3; k3's watch (script `:1860-1866`) stopped nothing |

The names are the working tree's, and I accept them. Each comment must carry three things: the scope in finding 2,
that the toggle was not read, and the Update outcomes as facts (r1:73, 112; r3:1434), not as what the app may do.
Pin them as `tests/test_findings.py` pins S0's, from run 1's and run 3's JSON (snapshot `9dded70`, revision
[34, 1, 1]) and the cited lines by content.

**`LIGHTWEIGHT_SAVE_RAISES_AN_ADDIN_DIALOG_ON_2026 = True`** (`_ON_2024` `None`), if a constant is wanted; a comment
beside `LIGHTWEIGHT_OPEN_RAISES_AN_ADDIN_DIALOG` would do as well, since no app code reads it.

- *Evidence:* r2:354-355, and the hang after it, r2:358-362.
- *Scope:* the SOLIDWORKS CAM add-in's modal Yes/No "SOLIDWORKS CAM Warning" under `SaveAs3` of an assembly holding a
  lightweight component, on this machine's 34.1.1. One occurrence. It was never answered.

**`M1_suppressed_in_active_read_whole`** (r2 JSON) need not become a finding: no app code gates on it. If it is set,
scope it to a distance mate, user–layout, suppressed in the active mode H only (r2:43, 54).

## *Done when*, clause by clause, for SolidWorks 2026

| clause | on this run |
|---|---|
| the suite is green | outside this run |
| a value Update and a slide-offset Update go ahead on a copy of S0's master with the user's components, mates among themselves and to the layout, a keyway in a gear part, and user locks from free sprockets to Sun and to RangeSlv; the sprocket found on its gear; every user mate on in its modes and in no error; the keyway rebuilt | **shown** at `9dded70` (r1:300-317, 356-372) |
| a lock to a fixed housing refuses naming it | **shown** (r2:132-150) |
| a Bore Diameter typed in SolidWorks refuses naming the cell | **shown** (r2:258-276; finding 10 on its wording) |
| M1–M3 answered | M2 shown. M3 measured on 2026 (finding 2), but K3, which it serves, fails (finding 1). M1 partial (finding 4). |
| the window check's W8 stage passes with K12's assertions | **not run** |
| 2024 confirms the assembly sections | **not run** |
| reviewed | this review, for the 2026 run; the closing run needs its own |

## What the phase's closing run must repeat

*Rules carried over*: affected sections after a fix, and one full run at the phase's close.

- *On 2026, at the closing snapshot* (after finding 1's change and the R1 to R3 fix round), in one session started
  for it, under `311ce5a`'s watch or later: all twelve sections.
  - m3 reads the toggle and asserts both Updates go ahead.
  - k3 asserts the Update goes ahead and names the keyway as the user's.
  - lightweight reads every instance's state (finding 3).
  - refuse's bore step starts clean (finding 6).
- *Then* the window check's W8 stage on 2026.
- *Then* 2024's confirming set: m3, setup, go, reducer, k3 and nocarrier, with refuse and lightweight by name at the
  user's call. It gives every `_ON_2024`.
- *And* the suite.

The go, refuse, again and nocarrier evidence here was taken under the old watch and an app that will change, so it
counts toward W9a but must be repeated. It cannot stand as the closing run.

## What I could not verify

- Anything on the Windows host: the run folders, the masters, how session 6628 ended, and whether the hung
  `SaveAs3` changed `refuse`'s copy on disk.
- Whether SolidWorks makes every instance of a part lightweight when one is set (finding 3).
- Whether G1's component read in error in k3 (finding 1, condition 3): k3 read no component codes.
- The uncommitted app change in the working tree, which I did not review.
- Whether "show errors every rebuild" was on during W9a's run.
