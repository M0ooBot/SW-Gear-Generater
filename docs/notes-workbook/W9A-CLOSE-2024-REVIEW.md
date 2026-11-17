# Review of W9a on SolidWorks 2024: the What's Wrong box, the ruling on it, and the changes since the close review

*Independent, 2026-11-17. I started no SolidWorks or Excel and changed no source, test or document. This file is the
only one I wrote.* It builds on my reviews of the 2026 run (`W9A-RUN-2026-REVIEW.md`) and of the 2026 close
(`W9A-CLOSE-2026-REVIEW.md`, `2a8f9d1`).

**Under review:** the commits `2a8f9d1..91d40f5`, none independently reviewed:

- the worker: `81e85c8`, `71c07a5`, `11a0f54`, `5eda959`, `c18ce99` and `0a60fd3`;
- package B: `d1664b5` and `9916d31`;
- the script: `73805d2`, `b985cab`, `a072efa` and `10a6a08`;
- the box's note: `d7cbcda`.

**The 2024 logs**, all under `probe/results/sw2024/`, each in a fresh session of SolidWorks 2024 32.5.0 (0.66 GB at
attach):

| cited as | log | snapshot | PID | sections |
|---|---|---|---|---|
| v24:N | `w9a-confirm-sw2024-20261117-1-m3-stopped-by-whats-wrong.log` | `19651ee` | 42932 | m3, stopped at the box |
| s2:N | `w9a-confirm-sw2024-20261117-2-setup-go-reducer-nocarrier.log` | `19651ee` | 21616 | setup, go, reducer, nocarrier |
| b1:N | `w9a-box-sw2024-20261117-1-box.log` | `b985cab` | 2904 | box |
| b2:N | `w9a-box-sw2024-20261117-2-reducer-box-k3.log` | `b985cab` | 33236 | reducer, box-k3 |
| s3:N | `w9a-confirm-sw2024-20261117-3-m3-stopped-by-the-scripts-rule.log` | `0a60fd3` | 48808 | m3, stopped by the script's own rule |
| s4:N | `w9a-confirm-sw2024-20261117-4-m3.log` | `10a6a08` | 43164 | m3 |
| s5:N | `w9a-confirm-sw2024-20261117-5-reducer-k3.log` | `10a6a08` | 33096 | reducer, k3 |

`git diff 10a6a08 91d40f5 -- src probe/w9a_demonstration.py` is empty, so s4 and s5 ran the final app and script.
I ran the whole suite once, without `-x`: 3493 passed, 1 skipped, 1 failed (the known font-width test).

---

## Verdict

- **The ruling on the box is defensible on this evidence, as a default put to the user.** In every Update run on 2024
  with something of the user's in error, the box came up, went while the job carried on, and the Update returned:
  - 3 to 23 s up;
  - SolidWorks' frame enabled;
  - a second connection answering;
  - the call count growing.

  The run checked afterwards what the job had done: it wrote only what it meant to, its bodies at their frames, the
  user's components and mates as before. And SolidWorks shows the same box when a person does what the app does
  (s4:115-118). The residual risk is a person acting in the box during the job (FeatureXpert above all), which
  nothing measured. The app's sentences should say "leave it" and should not say "a few seconds" of a box that
  stayed 23 s (finding 4).
- **SolidWorks 2024's confirming set is complete.** m3, setup, go, reducer, k3 and nocarrier each ran 0 failed in
  its last run (s2, s4, s5). setup, go and nocarrier ran at an earlier app source. None of the changes since could
  change their outcome (finding 7), so they need not run again on 2024.
- **The worker's gate change is sound, and the failure path now names K3's features without softening the stop.**
- **Three must-fix points before W9a closes:**
  - one 2024 finding's comment is contradicted by the logs (finding 1);
  - the plan and handoff do not say the ruling (finding 2);
  - the final 2026 run at `91d40f5` is owed, with its addendum (finding 3).

---

## Findings

**1. Must fix before W9a closes: two 2024 findings' comments are contradicted, or left behind, by s3 and s4.**

- *`WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2024 = False`.* The comment scopes it to "the explicit assembly rebuild
  call only", and rests it on the mate case (v24:51, b1:54). With a part feature in error, the script's own step
  that activates and rebuilds the assembly showed the box: up 0.53 s in with the worker in `ActivateDoc3`, gone
  1.05 s in during `ForceRebuild3` (s4:115-120). At `0a60fd3` the same box stopped the run (s3:116-118).
  - So, as worded, False holds for mates only.
  - Either split it by kind, or say plainly: "with a feature in error in a part the box shows when the assembly is
    activated for the rebuild (s3:116-118, s4:115-120); False covers only the mate case and only the
    `ForceRebuild3` call".
  - Nothing reads it any more, so the fix is the comment and its pin.
- *`ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2024 = False`.* The comment says "no explicit assembly rebuild
  was read with a feature in error on 2024". s4:119 is exactly that: `ForceRebuild3(True)` returned False, What's
  Wrong count 1, Sprocket-1 code 51. The two Updates laid their False rebuilds to the user: m3 (s4:172,
  `['Sprocket-1']`) and k3 (s5:611, the keyway).
  - I accept the value.
  - Replace the box-k3 inference (b2:605-608) with these direct lines, and pin them.
- *The other 2024 findings need their s3, s4 and s5 lines added* (see *How each 2024 finding stands*).

**2. Must fix before W9a closes: the plan and the handoff still say what was true before the ruling.**

- The plan's last section says "where the findings are None (2024 until its confirming run) the Update stops as
  before" (ISSUE-1-PLAN.md:1018). 2024 is now settled, and the Update goes ahead under the ruling.
- `HANDOFF-WORKBOOK.md` (`f8520b2`) says W9a is "stopped on 2024 at What's Wrong, waiting on the user's answer".
- The ruling is to be put to the user as a default. Write it as a dated change to the plan, with what was not
  measured: toggle 77 off, a person in the box, a Build, the mate case without modes. Update the handoff's account.

**3. Must fix before W9a closes: the final run on 2026 at `91d40f5`, and its review.**

The 2026 closing run was at `6f3d6fb`'s app. Since then the app changed (`git diff 6f3d6fb 91d40f5 -- src`):

- a carried component with its code unread refuses;
- the failed status names the user's features;
- the gate turns on `WHATS_WRONG_IN_UPDATE_BLOCKS`;
- the What's Wrong sentences;
- the window passes the revision.

On 2026 the helper is False and the gate's three values are unchanged, so no behaviour on 2026 should differ. That
is what the run now in progress must show. It needs the short addendum promised.

**4. Should fix: the two What's Wrong sentences.**

- *"For a few seconds" is not what was measured.* The box stood 22 to 23 s in each RangeBox Update (b1:103-110;
  s3:92-93; s4:89-92, 155-158) and 3 to 5 s on the 12 : 1 (b2:597-603, s5:596-597). "For a short while" or "for up
  to half a minute" would be true.
- *The sentence before the press should say to leave the box alone.* Nothing measured a person pressing
  FeatureXpert, Close or the "Display What's Wrong during rebuild" check box during the job. FeatureXpert repairs
  the model while the app's job runs, and the check box changes the very setting that shows the box. "It closes by
  itself; leave it, and the Update carries on" says what is known.
- *The sentence after the press is said after a quiet press, where no box can come and none came.* It is keyed on
  "something of the user's in error" (`_users_in_error`), not on the job having rebuilt anything. Every quiet press
  of m3 on 2024 says it: s3:63, s4:62, 128 and 182, with no box in any of them (and none in v24's quiet press,
  v24:56-66). Key it on the press having changed or put something.
- *It is not shown that one footer never carries both sentences.* After an Update that leaves something of the
  user's in error, the status ("may have shown") and the recorded line's prediction ("may show") may both be in
  the footer. The tests count each in its own sentence (`tests/test_workbook_user_record.py:642-667`). Neither
  shows the footer whole after a 2024 press, and the script does not log the footer after m3's presses. Test it,
  and say one or the other.
- *The sentence before the press is not said where the press will break a feature* (k3: s5:586-588; the box came at
  s5:596). The footer cannot know a feature will break, so this is right as "may", but it is the k3 case the user
  meets without warning.

**5. Should fix: the script's What's Wrong rule detects a blocking What's Wrong late, not never.**

- *How the rule works.* Under the rule (2024 only; the helper is False on 2026, so `ruled` is False and
  `_WhatsWrongTolerated` passes everything through), a `#32770` titled exactly "What's Wrong" and owned by
  SolidWorks' frame is a fact. Any other dialog, or an unowned What's Wrong, is still the STOP. At the job's end the
  box must go within 60 s and the frame must be enabled, or the STOP.
- *A box that never goes:* the STOP 60 s after the job ✓.
- *A What's Wrong that blocks the job.* The same dialog template carries a hidden "&Save Anyway?" button (b1:103,
  b2:597), so a modal variant exists. Such a box would hold the job, and the rule would wait until the job's own
  timeout (2400 s for an Update, 900 s for a script step) and then end as a hung worker. It would not pass, but it
  would cost up to 40 minutes before being named.
- *The fix.* `ww_poll` could read `frame_enabled` each tick and STOP at once when the frame is disabled with the box
  up.
- *`w8_step`'s wrap of W8's helpers* is right: the thread polls only while `WW["job"]` holds, W8's own watch is told
  through the wrapped `STARTUP_BOXES` only then, and a W8 note never read as owned here is the STOP.
- *2026's proof is not weakened.* `whats_wrong_rule()` is False there, so every path is as before.

**6. Should fix: the evidence for "blocks nothing" has gaps the findings should name.**

- *Shown in every case run.* The box came up, it went while SolidWorks went on working, the job returned, and the
  frame was enabled at the end:
  - b1: up 97.45 to 120.08 s, calls 21648 to 23767 while up, return at 306.5 s, ok (b1:103-110, 130-145);
  - b2: up 17.57 to 22.59 s, return at 22.59 s (b2:597-604);
  - s3: up 90.41 to 112.51 s, return at 300.9 s (s3:92-95);
  - s4, mate case: up 99.92 to 123.01 s, return at 314.4 s (s4:89-94);
  - s4, feature case: up 98.02 to 120.63 s, return at 352.8 s (s4:155-160);
  - s5, k3: up 17.12 to 20.13 s, return at 22.7 s (s5:596-599);
  - the script's own step: 0.53 to 1.05 s (s4:115-117).
- *What only the box runs checked.* The frame enabled *while* the box was up, and a read on a second connection
  answering in 0.5 s with it up: b1:103-104 and b2:597-598 only. The confirming runs check the frame at the job's
  end.
- *What was written, read raw before and after,* only in b1 and b2: Backlash 0.375 to 0.4, the save flags, and the
  toggle True before and after (b1:143, b2:614). The app bodies, user components and mates were as before (b1:145,
  b2:616).
- *b2's box went at the moment the job returned* ("calls grew … after it went False", b2:613). That case does not
  tell "went by itself" from "went with the job's end". s5 does: gone at 20.13 s, the job on until 22.7 s.
- *Not run:*
  - the toggle off;
  - a person in the box;
  - the mate case on a gearbox without modes;
  - a Build (the again sections never ran on 2024);
  - an Update that puts with the user's work in error and a lock carried (route (c1) with errors);
  - mate errors other than two over-defined distances;
  - any box longer than 23 s.
- *The 60 s allowance.* It applies only after the job's end, and in no case did a box outlive its job, so the
  lifetimes do not threaten it. A box outliving a job would end the script's run, not the app's.
- m3's second Update covers a feature in error in the user's own part (s4:153-173). That case is run.

**7. Note: setup, go and nocarrier need not run again on 2024.**

They ran in s2 at `19651ee`, whose app is `6f3d6fb`'s. `git diff 6b9d8aa 91d40f5 -- src` changes four things:

- `judge_user_work` refuses a carried component with its code unread. In s2 every carried sprocket's code read 0
  (s2:70, 91), so the judgement on the same reads is the same.
- `_rebuild_laid_to_user`'s gate acts only on a False rebuild. None of s2's sections has anything of the user's in
  error (s2:81, 183, 241, 826, 895, 936), and no box came (only notification boxes, s2:8, 214).
- `ui_text`'s new sentences and the revision the window passes act only with something of the user's in error.
- `findings`: `USER_MATE_PUT_NO_CARRIER_ON_2024` is now True. s2 ran nocarrier with it patched True for the press,
  the same behaviour.

The confirming set therefore stands across its three sessions. Each was fresh, as the note's command lines asked.
refuse and lightweight were not run on 2024; they are run by name only, at the user's call. 2024 is the version said
to open components lightweight.

**8. Note: the gate change.**

- `assembly_rebuild_settled` now needs both rebuild findings set and `WHATS_WRONG_IN_UPDATE_BLOCKS_ON_<year>` False.
  `_rebuild_laid_to_user` still needs feature False and every other condition (`swbuild.py`, `c18ce99`).
- *Can an Update go ahead where it should not?*
  - On a version without findings (2025, major 33, which `MINIMUM_MAJOR` 32 to `HIGHEST_TESTED_MAJOR` 34 admits)
    the gate is None and a False rebuild stays a failure ✓.
  - An Update with only user mates in error goes ahead on any version, gate or not, since the rebuild returns True.
    On a version where a box might block, nobody measured. That has been so since W9a; 2025 is untested in
    everything.
  - The static path is unchanged: a failure.
  - The app's own items in error: unchanged, a failure.
- *The re-pinned tests* patch the 2024 findings, or `WHATS_WRONG_IN_UPDATE_BLOCKS_ON_*`, to None or True
  (`tests/test_swbuild_user_work.py:636-650, 754, 775, 844, 861, 905-906, 961`). They still drive the unmeasured
  path.
- `WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2026 = False` holds vacuously: no box came on 2026.

**9. Note: the failure path and K3.**

- `d1664b5` appends the user's features newly in error after "Update SolidWorks stopped. …". It keeps `ok` False.
  A feature in error before is said once, unless the stop's own sentence has already named it.
- b2:607 shows it on 2024: the stop, then "Your User Keyway in Gear_m1.5_N17 is in error in SolidWorks now, after
  this Update set Bore Diameter 8 to 14 (Gears!J2) …". My close review's must-fix 2 is taken.
- A blank cell is said as blank ("clear Gears!P2 again"), and an equation as the workbook shows it: should-fix 7
  taken.

**10. Note: smaller items.**

- *The foreseen refusal.* m3's carried step now makes a quiet press after the lock, and the footer foresees the
  refusal (s4:203-206, 229): close review finding 5 taken.
- *The unread code.* The carried component with its code unread is refused (`81e85c8`).
- *Memory.* SolidWorks 2024 grows to about 7 GB in each RangeBox m3 (b1:130, s4:94), with 9.8 GB or more free.
  Below the 2 GB stop, but worth the note's sentence.

---

## The ruling on the box, judged

*The ruling:* on 2024, What's Wrong shows for some seconds during an Update when something of the user's is in error,
blocks nothing and goes by itself. The app leaves it alone, changes no SolidWorks setting, does not refuse for it, and
says so.

- **"Blocks nothing" is shown in the cases run.** Five Updates (b1, s3, s4 ×2, s5) and one failed Update (b2), with
  the frame enabled, a second connection answering, the calls growing, and the job returning with every check of its
  result passing. The box is a popup owned by the frame, not a modal frame (`dlg_modal_frame` False, b1:103).
- **"Goes by itself" is shown in five of six.** In b2 it went with the job's end.
- **It is SolidWorks' own behaviour for the user's preference.** The box showed when the script's own step did what a
  person does (s4:115-118). Turning it off for the job would change a persistent setting of the user's, and that
  was not measured.
- **Leaving it alone is therefore defensible,** and the alternative needed more measuring and the user's word.
- **The residual risk to a user on 2024:**
  - a person pressing FeatureXpert or the check box while the job runs (not measured; the sentence should say to
    leave it);
  - a box that outlives the job (not seen; harmless if seen);
  - the shapes not run (finding 6), the Build above all.
- **The app's sentences are true as far as they go,** but for "a few seconds" and the after-sentence on quiet presses
  (finding 4).

## How each 2024 finding in `findings.py` stands

| finding | value | judgement |
|---|---|---|
| `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2024` | True | accept; add s3:53 and s4:52 (True, What's Wrong 3, codes 51) |
| `ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2024` | False | accept; replace the box-k3 inference with s4:119, and add s4:172 and s5:611 (finding 1) |
| `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2024` | False | correct the comment, or split by kind: with a feature in error the box shows at activation (s3:116-118, s4:115-120) (finding 1) |
| `WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_2024` | True | accept; add s3:90-94 and s4:89-93 |
| `WHATS_WRONG_OPENS_IN_UPDATE_WITH_PART_FEATURE_IN_ERROR_ON_2024` | True | accept; add s4:155-159 and s5:594-598 |
| `WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2024` | False | accept; add the three confirming Updates and k3 (s3:92-98, s4:89-107 and 155-173, s5:596-612), the lifetimes (3 to 23 s), and "frame and second-connection reads during the box in b1 and b2 only" |
| `USER_MATE_PUT_NO_CARRIER_ON_2024` | True | accept as written (s2:799-951) |

The pins in `tests/test_findings.py` cover v24, b1, b2 and s2, not s3, s4 or s5. Add pins for the lines above.

## *Done when*, clause by clause

| clause | SolidWorks 2026 | SolidWorks 2024 |
|---|---|---|
| the suite is green | 3493 passed, 1 skipped, the known font-width failure (my run, at `91d40f5`) | — |
| the value and slide-offset Updates go ahead with the user's work, sprockets on their gears, user mates on and in no error, the keyway rebuilt | shown at `6f3d6fb` (close review); owed again at `91d40f5` (finding 3) | go, 0 failed (s2:127-270) |
| a lock to a fixed housing refuses naming it | shown at `6f3d6fb` | refuse not in the confirming set (by name only) |
| a Bore typed in SolidWorks refuses naming the cell | shown at `6f3d6fb` | same |
| M1–M3 answered | M1 as ruled; M2, M3 and K3 shown at `6f3d6fb` | M3 answered: the mate case True (s4:52), the feature case False (s4:119), and What's Wrong as ruled. K3 met in an app part (s5:611-612) and the user's own part (s4:172-173). M2 shown (s5:573) |
| the window check's W8 stage with K12 | shown at `6f3d6fb` (w); the final run repeats it | — |
| 2024 confirms the assembly sections | — | **met**: m3, setup, go, reducer, k3 and nocarrier, 0 failed in their last runs (s2, s4, s5), under the ruling |
| reviewed | this and the close review; the final run's addendum owed | this review |

## What is still owed before W9a is closed

1. The comments, and their pins, of finding 1, and the s3/s4/s5 lines in each 2024 finding.
2. The plan's dated change for the ruling, and the handoff (finding 2).
3. The final 2026 run at `91d40f5`, every section and the window check, and its addendum (finding 3).
4. The user's answer to the ruling, which is put to them as a default.
5. Should-fix items 4 to 6, at the coordinator's discretion. Of them, I would not close without the "leave it"
   wording and the after-sentence keyed on a real change, since both are what the user reads.

## What I could not verify

- Anything on the Windows host, including how each box session was ended. The box sections end "by design" with
  SolidWorks left as it stood (b1:148, b2:619).
- Whether What's Wrong is ever modal in an Update, and what FeatureXpert, Close or the check box would do mid-job.
- The footer as a whole after a 2024 press (finding 4).
- The final 2026 run, still running when this was written.
