# Review of W9 S0: the user's locked component on a put gear, the grounded tie, and What's Wrong

*Independent, 2026-11-16. I started no SolidWorks or Excel, changed no code, and ran one suite file
(`tests/test_findings.py`, 123 passed, through the repo's `.venv`). This file is the only one I wrote.* Under review:

| what | where |
|---|---|
| the script | `probe/w9_user_work_check.py` at `HEAD` (`cecd666`; unchanged since `423e227`, which runs 2 and 3 ran) |
| run 1, 2026 34.1.1, at `55a82c1` | `probe/results/w9-s0-sw2026-20261116-050200.log` ("r1:N"), `w9-s0-20261116-045653.json` |
| run 2, 2026 34.1.1, at `423e227`, route (c) | `probe/results/w9-s0c-sw2026-20261116-054300.log` ("r2:N"), `w9-s0-20261116-054213.json` |
| run 3, 2024 32.5.0, at `423e227` | `probe/results/sw2024/w9-s0-sw2024-20261116-065000.log` ("r3:N"), no JSON |
| the note | `docs/notes-workbook/W9-S0.md` ("note:N") and its proposed findings |
| W8's close, never reviewed | `782d774` (findings comments, tests, probe order) and `e20440f` (handoff, PLAN-WORKBOOK, W8-PLAN, UI-DESIGN) |

I read the handoff's *Where W9 stands*, *How W8 closed* and *Rules carried over*, ISSUE-1-PLAN's K2, §0.3, §3 and §4,
the script end to end, `findings.py` around the lock, mesh and constrained-status findings, and `tests/test_findings.py`.
I searched the logs rather than reading them whole, and recomputed the angle table and every "worst" figure from the
logs and run 1's JSON frames (a throwaway parser in the scratchpad, not in the repo).

**Verdict.**

- **The runs say what the note says, with one wrong number.** The counts are right (r1 243 `ok` and 1 FAIL, the
  plan's STOP; r2 466 and 0; r3 528 and 1). Routes (a) and (b) fail on both versions exactly as tabled. Route (c)
  is clean in A, B and E on both versions, in all 24 of its puts on each. The tie reads 3 in C on both versions, and
  C2 reads as described on 2026. P0 reads as described on both. The one wrong figure is 2024's B (finding S2).
- **Route (c) is implemented as the note describes, and its checks can fail.** Run 1 and 2024's A-a and A-b fail
  the same "each locked sprocket at its pose" test that route (c) passes, at 0.60 and 0.96. The script touches only
  its own copies, its own scratch part and its own Excel.
- **The proposed findings cannot go into `findings.py` as worded.** Four must-fix points:
  - the plan still forbids route (c)'s write (M1);
  - `USER_MATE_PUT_ROUTE` covers user locks only, and a user gear mate on a put gear is a known silent failure that
    nothing measured (M2);
  - the What's Wrong reading was measured on a part's rebuild only (M3);
  - `USER_TIE_READ` needs its value, its rule and its per-mode reading written apart, with 2024's per-mode reading
    `None` (M4).
- **For 2026**, all four findings can be set once those four are taken. **For 2024**, these can be set from run 3's
  per-case lines: the route, the tie's value (3), the part-rebuild What's Wrong reading and D. C2's per-mode tie
  reading cannot be set.
- **The 2024 run's end points at the script as well as at SolidWorks.** SolidWorks was gone between two jobs, and
  nothing in the script explains that. But the script's own `finally` then lost the JSON, the `propose` lines and
  the `done` line (S1). Fix that before C2 is rerun on 2024.
- **W8's close documents hold against the logs**, with one wrong line number in a `findings.py` comment (S5) and
  W9's stage count already stale when `e20440f` wrote it (S6).

---

## Points

**M1. Must fix before the findings are set: the approved plan still forbids route (c), and its K2 and K4 name only
routes (a) and (b).**

- ISSUE-1-PLAN §0.3 (lines 80-83) is a STOP for anything that would "write to, delete, move or rename a component …
  not on record". It allows two exceptions only: route (b)'s suppression, and W9d's writes into the new revision.
- Route (c) moves the user's component by `Transform2` (`put_c_job`, script 448-453). That is a move of an item not
  on record.
- K2 (plan line 66) offers only "(a)" or "(b)". K4 (line 68) has the footer name "what of the user's it will suppress
  around a put (route b)". The plan never mentions (c).
- The handoff (line 79) records that the user accepted route (c). The plan, which binds the packages, does not say
  so. A worker following the plan would have to STOP on the finding's own instruction.

*Do:* amend ISSUE-1-PLAN before `USER_MATE_PUT_ROUTE` is set, as a dated note in the style of *Changes after the
review*:

- K2 states route (c1).
- §0.3 adds the exception: a user component rigid to a put gear through the user's locks is moved by that gear's
  rigid motion, in the mode shown, and each one is read back by `place_component`.
- K4's footer names what of the user's will be moved.
- §5 W9a's tests say the fake fails on any other move of a user component.

**M2. Must fix before the findings are set: `USER_MATE_PUT_ROUTE` covers user lock mates only. The constant and K2
must say so, and must say what happens to every other user mate on a put gear.**

What S0 measured:

- A user component joined to an app gear by a **lock**, directly or through a chain of user locks (A, B, E).
- A plane-coincident mate with no lock (D).

Which components are tied comes from the case's own list (`ties()`, script 503-513), not from reading mates. The
note says so (note 233-235). Three more limits are not in the note's proposal:

- *A user gear mate is unmeasured and is expected to fail silently.* Picture a sprocket meshed with Sun by a user's
  gear mate rather than locked to it. `findings.py` 601-603 and `MESH_PHASE_ROUTE` (610) record what a
  `Transform2` put does with a gear mate on: "the gear mate takes the new phase". That is the same silent re-take
  that sank routes (a) and (b) for locks (`LOCK_RETAKES_AFTER_A_PUT`, 731). Route (c) as ruled ("through the user's
  locks") does not carry such a component. K2 says a user mate on a moved gear "does not stop Update", so W9a would
  re-phase the user's mesh with no error.
- *Other mates that make a user part rigid to a gear are unmeasured:* concentric, coincident, parallel or angle mates
  to a gear's own faces or planes. D's plane mate was never stressed by the put: it holds axial position, and the
  put turned RangeSlv only.
- *Lock flags per mode are unmeasured.* The script carries a tied component in every mode whatever its lock's flag
  there. A user lock suppressed in one mode makes the component free in that mode, and route (c) must not carry it
  there.

*Do:*

- Word the constant for what was measured: user components rigid to a put gear through user lock mates that are
  on in the mode being put, chains included.
- In the plan (K2), say that until measured, a user mate of any other kind on a gear Update must move refuses before
  any change, named (gear mates above all). Otherwise that kind is measured in W9a's full build (M1/M3's section)
  before the worker relies on it.
- The chain must come from reading each user lock's entities in the mode shown (M1's read), as the note says.

**M3. Must fix before the findings are set: What's Wrong was measured on a part's rebuild only. The proposed name
claims every API rebuild.**

- P0 rebuilt a part by `s.rebuild()` (script 283 and 287). For a part that is `ForceRebuild3(False)`
  (`swcom.rebuild_call`, swcom.py 382-383).
- The setup was a visible, active part opened by the app's `OpenDoc6` route, a user keyway in error, and toggle 77
  on (r1:9-11, r3:8-10).
- Update also rebuilds the assembly, by `MATED_ASSEMBLY_REBUILD_ROUTE` `"ForceRebuild3(True)"` (findings.py 785).
  An assembly rebuild with only a user mate or feature in error is M3 of the plan's §4 table, which is still to come.
- `WHATS_WRONG_OPENS_ON_API_REBUILD = False` would cover a rebuild nobody has run.

*Do:*

- Name the constant for the part's rebuild, e.g. `WHATS_WRONG_OPENS_ON_PART_REBUILD = False`, on both versions, with
  the call, the toggle and the error codes (71 on 2026, 51 on 2024; never read for meaning, as `MATE_ERROR_2024`'s
  comment already rules).
- Leave the assembly case to M3's section of W9a's full build.

**M4. Must fix before the findings are set: write `USER_TIE_READ` as three things, and give 2024 only what 2024
read.**

1. *The value read.* `GetConstrainedStatus` 3 on every app body of the tied train. On 2026 (r2:909, 914, 929; r1
   likewise) and on 2024 (r3:1840, 1857) it read 3 unshown with H active, shown in H and shown in L. This is
   `COMPONENT_FULLY_DEFINED`. It may be set for both versions.
2. *The rule.* The app should test "not `COMPONENT_UNDER_DEFINED`", as `swbuild._free_to_turn` (1068-1074) already
   does. It should not test "== 3".
   - "never 4 here" (note 219) is true of the reads.
   - But SolidWorks itself raised "The assembly is over defined" during C's drive, on both versions (r2:917,
     r3:1843; S3).
   - A tie whose geometry conflicts could read 4, and an equality test would let it through as free.
3. *The per-mode reading.* In C2 the tie was suppressed in H and N and on in L. On 2026 (r2:996, 1012) it read free
   unshown with H active and shown in H, and tied only when L was shown. On 2024 it was never read (r3 ends at 1920).

*Do:*

- Keep the per-mode reading as its own constant or field, per version, as `POSITIONS_PER_CONFIGURATION_ON_2024`
  is done: True on 2026, and **`None` on 2024**, with the comment saying C2 is owed there.
- The app's behaviour must not depend on it. On every version, K2's rule already reads each mode when shown whenever
  a user mate on the train has different flags in different modes. That rule is safe without a measurement, so 2024
  loses nothing while the reading is `None`.
- Do not write the converse ("same flags, so the showing mode decides every mode") as measured; see S7.

**S1. Should fix before C2 is rerun on 2024: the script loses everything after a lost session, and the note puts the
loss on SolidWorks.**

- *What the log shows.* r3:1920-1955:
  - The read job's first call, `begin_build`'s `SetUserPreferenceToggle` (swcom.py 1080), found the server
    disconnected (0x80010108). The reopen job just before had ended normally (r3:1919).
  - `Case.run` turned that into an `AssertionError`. Then `run_case`'s `finally` (script 974-975) called `end_copy`.
    Its `save_modified_in` made the worker reconnect, and `connect_pid` raised `NotRunning` (the log's PID line).
    That replaced the `AssertionError`, and `main`'s outer handler logged it (script 1082-1085).
  - `propose()` (1076) was skipped, so 2024 has no `propose` lines.
  - In `main`'s `finally`, `W.run(worker, W.close_ours, 600)` (1100) raised `NotRunning` again. Only `WorkerHung`
    is caught there (1104). The exception left the `finally` before the JSON write (1110), and the `noted`, `stop`
    and `done` lines (1113-1117) were never written. The log ends at "excel quit our own Excel" (r3:1955).
- *What the note says.* Note 27-30 says "The run's close found no session either, so no JSON was written". It was
  the script's exception path, not the close, that lost the JSON. Two and a half hours of readings on 2024 survive
  only as log text, and the note's "528 passed" (note 22) is a count of `ok` lines, not a `done` line.
- *What the log points at for the crash itself.* SolidWorks went away between two jobs, not inside a new call. The
  same reopen-then-read sequence had run eleven times before it. Nothing in the script explains the crash.
  - The one thing the run did against the handoff's rule ("prefer a freshly restarted session for long runs") was to
    put twelve cases in one 2024 session.
  - SolidWorks' private memory grew from 0.66 GB at attach (r3:2) to 13.6 GB after C (r3:1880), with 10.0 GB still
    free, above the 2 GB stop.
  - Memory is the likelier cause, not a proven one.

*Do:*

- Catch any exception around `close_ours` and `open_titles` in `main`'s `finally`, and write the JSON first.
- Write the JSON after each case as well, so a lost session keeps what was read.
- Reword note 27-30.
- Then run `--cases C2 --master <2024's rangebox.master> --skip-p0` alone in a fresh 2024 session, as the handoff
  says.

**S2. Should fix: the note's 2024 B figures are wrong.** Note 127 gives B (c1) and (c2) on 2024 as "clean, 2.6e-15".

- r3 reads 7.1e-15 for both, from the L tie read through the last read (e.g. r3:1308-1340 for B-c1, and the put
  lines 1324 and 1340 "Sprocket-2 7.1e-15"). That is the same as 2026.
- Every other figure in that table matches the logs: 2.9, 2.5, 7.1, 7.1, 4.1 and 3.5e-15 on 2026; 3.6, 3.1, 5.1 and
  4.4e-15 on 2024.
- *Do:* correct it to 7.1e-15, which is still far inside 1e-6.

**S3. Should fix: "the drive against the tie … the drive job saw no error" (note 171) leaves out what SolidWorks
said.**

- During C's drive in H, SolidWorks raised the balloon "The assembly is over defined. Click here to view mate errors"
  (r2:917 before the step at r2:920; r3:1843 before r3:1848).
- The drive job returned `errors []`, and the reads after it show no mate in error and status 3.
- So the drive's own error read did not see SolidWorks' over-definition. The likeliest reading is that the drive's
  angle mate, deleted before the read, is what over-defined the assembly.
- *Do:* say this beside "never 4 here" (M4), and in *Other readings* (note 205-206), which mentions the balloon but
  not when it came.

**S4. Should fix: the proposed `USER_LOCK_RETAKES_PUT_OFFSET` duplicates two findings already set, and the note cites
a third.**

- Route (a)'s result is `LOCK_RETAKES_AFTER_A_PUT = True` (findings.py 720-731): "a put with a lock on silently
  changes the pair's relation". It was measured on both versions in W5's P0b and is pinned (tests 704).
- Route (b)'s result is `LOCK_UNSUPPRESS_KEEPS_THE_NEW_ANGLE = True` (611).
- The note cites only `LOCK_RETAKES_AN_OFFSET` (note 106; script docstring 42). That one is the suppressed-lock
  offset along and round the shaft (684).
- Run 1 therefore re-measured what `findings.py` already predicted for routes (a) and (b), on a user lock and a
  gearbox with modes, and found it again on both versions.
- *Do:* add no new constant. Add S0's reading, with its log lines, to the comments of `LOCK_RETAKES_AFTER_A_PUT` and
  `LOCK_UNSUPPRESS_KEEPS_THE_NEW_ANGLE`. Add to the record one thing they did not hold: the re-taken offset is the
  mate's, so it reaches every mode. Run 1's A-a read Sprocket-1 at +74° in H, N and L alike in the last read, and C2
  under route (a) left L's Sun at -37° (recomputed from run 1's JSON frames).

**S5. Should fix (W8's close, `782d774`): one line citation is wrong.** The `SUPPRESSED_GEAR_MATE_SENSE_READ`
comment cites `sw2024/w8-workbook-assembly-20261115-162357-s7.log` "line 1175".

- Line 1175 is the suppression-order read ("names passed reversed …").
- The suppressed-sense read is line 1170.
- The JSON citation (`cases[6].suppressed_sense`) is right, and it is what the new pin reads.
- *Do:* correct it to 1170.

**S6. Should fix (W8's close, `e20440f`): W9's stage count was stale when it was written.**

- `e20440f` (04:48) wrote "stages W9a to W9e" and "a second review of its revision in hand" into HANDOFF line 64
  (and the W9 row) and PLAN-WORKBOOK line 748.
- ISSUE-1-PLAN had been revised to its second review at `953e630` (04:33): "in four stages W9a–W9d" (plan line 41).
- The handoff's own item 4 (line 88) says "W9b, W9c and W9d".
- *Do:* make both files say W9a–W9d and "revised to its second review".

**S7. Should fix: the note's tie rule is wider than C and C2.** Note 220-221 says the showing mode's read "decides
every mode only when every user mate on the train has one flag in every mode". Two limits:

- *C compared H and L only.* N was never read before a put in any case. It was read only in the last read, after the
  puts. In that read N's tied set differs: RangeSlv, uncoupled there, reads 2 (r2:945). So the bodies a tie holds,
  and the train the refusal names, depend on the mode's couplings even when every user flag is the same.
- *Nothing tested a tie that reaches the train through a slider.* For example, a user component locked to RangeSlv
  and tied to the housing would tie Sun's train in H and L but RangeSlv alone in N.
- *Do:* record "same flags: H and L read the same (C)", not "decides every mode". In K2, have W9a's worker name the
  tied train from the mode it reads.

**N1. The last read checks only L's frames** (script 954-959). H's and N's gaps are logged but not checked. All 84
last-read lines across the three runs read 6.6e-10, so the note's "every mode … at its built frame" (note 144-145)
holds. Check every mode when the script is next touched.

**N2. D's check would pass if RangeSlv had not slid.** It compares Sprocket-2's z less RangeSlv's against the setup
(script 828-831 and 969-973) and never asserts the slide. Run 2's JSON shows RangeSlv at z -34.5, -29.5 and -24.5 in
H, N and L, with Sprocket-2 on it each time, so D stands.

**N3. A misleading fact line.** "each locked sprocket at its pose of the setup: True ({… 'Sprocket-2': '1.0e+01'})"
(r2:948-950) prints an untied sprocket's gap next to "locked". The value judged (`tied_home`) is right. Print the
tied ones only.

**N4. "That is not what API-LEDGER:220 records" (note 200) compares unlike cases.** The ledger's case had a template
`Default` configuration beside the active one. RangeBox's configurations are H, N and L only (r2:35). Say "differs
from the ledger's case with a Default configuration".

**N5. Route (c)'s failure path, for W9a's worker.** If a job fails after a gear's put and before its user
component's, then under (c1), and under (c2) once the lock is turned back on, the user's lock silently re-takes the
wrong offset (`LOCK_RETAKES_AFTER_A_PUT`). The worker should name such a component and its lock in the failure
sentence. S0 had no such failure (every put clean).

**N6. The handoff's account of the closing order (`e20440f`).** It says `s5` "was to run before the copy sections".
`s3` and `s4` copy `s1.master` (probe 7066, 7140) and ran before `s5` in the closing run (groups `c351b1f` and
`8fd13c9`). The probe's docstring (`782d774`, "s5 before s2") is the accurate one.

**N7. `782d774` left `W7_PUT =LATEST.parent …` (tests/test_findings.py) without a space.** Cosmetic.

**N8. D's proposed `USER_PLANE_MATE_ON_SLIDER_FOLLOWS`** was not asked for by the plan, and nothing will read it. If
set, scope it: an axis mate plus a plane-coincident mate, no lock; the put turned RangeSlv only, and the slide came
from showing each mode.

## How each proposed finding may be set

| finding | 2026 (34.1.1) | 2024 (32.5.0) |
|---|---|---|
| `USER_MATE_PUT_ROUTE` (c1), scoped as M2 | yes: r2:1034-1035, and each case's four "clean True" lines | yes: no `propose` line exists (S1); cite r3's put lines 1055-1104 (A-c1), 1171-1220 (A-c2), 1289-1340 (B-c1), 1408-1457 (B-c2), 1526-1575 (E-c1) and 1644-1695 (E-c2), and the last-read checks |
| the lock re-take (S4's comments, no new constant) | r1's A-a, A-b, B-a, B-b; the table recomputes exactly | r3's A-a, A-b (0.60, 0.96) |
| `USER_TIE_READ`, value 3 and the rule not-2 | yes (C, r2 and r1) | yes (C, r3:1840, 1857) |
| the tie read per mode (C2) | True for H against L only (S7) | **`None`** until C2 runs alone in a fresh session |
| What's Wrong, a part's rebuild (M3) | False (r1:9-12) | False (r3:8-12) |
| D | True, scoped as N8 | True |

Pin them as `tests/test_findings.py` pins W8's: run 2's JSON for 2026 (revision `[34, 1, 1]`, snapshot `423e227`,
`proposal`, `cases`), and for 2024 the log lines themselves (head lines 1-2 for revision and snapshot, then each cited
line by content), since 2024 has no JSON.

## What I checked and found right

- *Counts and heads.* r1 243 `ok`, 1 FAIL ("a put holds in neither route"), `done 1 failed`, snapshot `55a82c1`. r2
  466 `ok`, 0 FAIL, `done 0 failed; 4 noted; 0 STOP(s)`, snapshot `423e227`, master from r1. r3 528 `ok`, 1 FAIL,
  snapshot `423e227`. Each run had its own PID (46140, 42496, 12968), and each SolidWorks was fresh at attach
  (0.66-0.68 GB). The app source is the same at `55a82c1` and `423e227` (`git diff --stat`: probe, docs and results
  only).
- *Routes (a) and (b).* Every angle in note 91-97 matches run 1's JSON frames (Sun 37 → 0; Sprocket-1 37, 74;
  RangeSlv 47.59/23.36 → 10.59; Sprocket-2 37, 49.77). 2024's A-a and A-b read the same, at 0.60 and 0.96.
- *Route (c)'s code.* `carry` computes R_t R_bᵀ R_u and R_t R_bᵀ (p_u − p_b) + p_t, consistent with `relative`'s
  convention, and the 1e-15 results confirm the convention against SolidWorks' reads. App bodies are put first,
  carriers first, then the user components. Mates go back on in a `finally`, with flags read in every configuration.
  A put is judged on the user's components' targets as well as the app's.
- *Route (c)'s results.* Each A, B and E variant has four clean puts and both last-read checks on both versions. The
  second drive carried each locked sprocket to 2e-16 or better (r2's `a second drive` lines). L shown after H's put
  read every locked sprocket home (8 checks on 2026, 7 on 2024).
- *C, C2 and D.* C2's run 1 L read Sun at -37° after route (a) (recomputed). The moving put against the tie in run 1
  held with no error. D's dz is 0 in every mode, through every put and in the last read, on both versions.
- *P0.* The toggle was on as found and after, on both versions. The keyway alone was in error. `GetWhatsWrongCount`
  read 1. No new window came up, and the dialog watch logged none in P0.
- *Reads mark nothing.* Every read's `GetSaveFlag` check passed, and each reopened assembly read unmarked.
- *`782d774`.* Every other line it cites reads as described:
  - 020805 lines 357, 362, 367, 368, 461-464, 723, 1993, 2018, 2043, 2070 and 2382;
  - 2024's 233045 lines 220-223, 237-244, 344-349, 354-370, 462-465, 479-486 and 724 (the FDrive tuple, the same
    text on 34.0.0, 34.1.1 and 2024);
  - 230215 lines 739-742 and 821-824;
  - both s7 JSONs' case 7 reads.

  `W8_ORDER` now runs `s5` before `s2`, `s3`, `s4` and `s7`. The `swbuild.py` comment no longer leans on
  `SUPPRESSED_GEAR_MATE_SENSE_READ`. `tests/test_findings.py` passes (123).
- *`e20440f`.* Its table matches `W8-REVIEW-CLOSING-RUN.md`'s verified counts. "`0e7f203`, whose app source differs
  from `c583f48` in comments only" is true (one `swcom.py` docstring and comments). The review points it lists as done
  are done in `782d774` or the handoff text.

## What I could not verify

- Anything on the Windows host: the run folders and masters, the hand-renamed `s1` folders and their "10 of 10"
  paths, and whether SolidWorks 2024 left a crash record.
- The user's acceptance of route (c) (handoff 79). It is in no repo file but the handoff.
- Run 3's wall time ("about 2 h 27 min"): its log has no end time. Its case times sum to 2 h 0 min before C2.
- `e20440f`'s suite figures at `c583f48` (3280 passed, 1 skipped, 1 failed; Windows 160 passed): the full suite
  includes the Tk tests I was not to run.
- Whether What's Wrong would open on an assembly rebuild, or for a document opened another way (M3).
