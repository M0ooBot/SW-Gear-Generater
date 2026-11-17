# Review of W9a's changes after the 2026 run review, and of its closing run on SolidWorks 2026

*Independent, 2026-11-17. I started no SolidWorks or Excel and changed no source, test or document. This file is the
only one I wrote.* It builds on my review of the first run (`W9A-RUN-2026-REVIEW.md`, `6700505`).

**Under review:** the commits since `6700505`, none reviewed before this:

- the worker: `ebcd23d` and `049fdb8`;
- package B: `84b9303`, `b73af2e`, `596bcb1` and `6f3d6fb`;
- the script: `40212d3` and `6b9d8aa`;
- the plan: `3e7307a`.

**The evidence**, committed in `19651ee` and `820c002` under `probe/results/`:

| cited as | log | snapshot | sections |
|---|---|---|---|
| c1:N | `w9a-close-sw2026-20261116-1-m3-reducer-k3-setup-lightweight.log`, JSON `w9a-demo-20261116-225659.json` | `6f3d6fb` | m3, reducer, k3, setup, lightweight |
| c2:N | `w9a-close-sw2026-20261116-2-go-m1-refuse-again-nocarrier.log`, JSON `…-232221.json` | `6f3d6fb` | go, m1, refuse, again ×3, nocarrier |
| c3:N | `w9a-close-sw2026-20261117-3-again-rerun.log`, JSON `…-001138.json` | `6b9d8aa` | again, again-dirty, again-closed |
| w:N | `w9a-window-sw2026-20261117.log` | `6f3d6fb` | the window check's W8 stage |
| v24:N | `sw2024/w9a-confirm-sw2024-20261117-1-m3-stopped-by-whats-wrong.log`, JSON `sw2024/w9a-demo-20261117-002344.json` | `19651ee` | m3 (stopped) |

`git diff 6f3d6fb HEAD -- src` is empty, so all five logs drove the same app. `6b9d8aa` changes only the again
sections' checks in the script (`stays_said`, `local_clock`) and one line of the note.

**What I ran:**

- The whole suite once. I ran it with `-x` by mistake, so it stopped at the known font-width test: 3378 passed,
  1 skipped, 1 failed (`test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`). That
  left unrun the 25 Tk tests after it in `tests/test_workbook_window.py` and `tests/test_workbook_xlsx.py`.
- Then `tests/test_workbook_xlsx.py` and `tests/test_findings.py`, which are not Tk: 185 passed.
- I did not run the 25 Tk tests again.

---

## Verdict

- **On SolidWorks 2026, W9a's *Done when* is now met, but for review of what follows.** One session (PID 6328,
  0.68 GB at attach, c1:4) ran all twelve sections at one app source, 0 failed in each last run. The window check's
  W8 stage ran in the same session, 0 failed.
  - Shown: go's two Updates, the two refusals, K3 in an app part (k3), M3's consequence in m3, the carried
    component in error refused before any write, lightweight held to a raw read, and K12 on the real screen.
  - M1 stands as the plan now rules it (`3e7307a`).
  - The three logs can stand as one closing run of twelve sections (finding 9).
- **The worker's change keeps the four conditions in every case I could construct but one.** The read of "nothing
  of the app's in error" covers mates, components and app parts' features. It does not cover the assembly's own
  feature tree: its equations and any assembly-level item of the app's (finding 4).
- **The new sentences never soften a failure.** Any failure returns "Update SolidWorks stopped …" before any of
  them is said. But in that case the user's features in error are not named at all. So K3 holds only when the
  Update succeeds, and 2024's k3 will fail the script's own check while 2024's findings stay `None` (finding 2).
- **W9a cannot close until SolidWorks 2024 is settled (finding 1).** During the app's own value Update, 2024 opened
  What's Wrong with only the user's mates in error. W9a let that Update go ahead where the app before it refused
  every user mate. So the gap is W9a's, on 2024, and none of the gated findings covers it: the gate is about a
  False rebuild, and this rebuild need not be False.
- **Findings.** The W9a findings in `findings.py` I accept as they stand, with comment additions (finding 3). For
  2024, only `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2024 = True` may be set from v24:51. Its What's Wrong
  finding must stay `None`. A new per-version fact about What's Wrong during an Update is proposed in *The 2024
  fact and the options*.

---

## Findings

**1. Must fix before W9a closes: on SolidWorks 2024 an Update with only the user's mates in error meets What's Wrong,
and nothing in the app prevents it.**

- *What happened.* With "show errors every rebuild" on (v24:37), two user mates over-defined (codes 51, v24:51) and
  the footer naming them (v24:82), the app's value Update raised "What's Wrong" (v24:88-90). The script's own
  assembly rebuild with the same mates in error had raised none (v24:51). Details are in *The 2024 fact and the
  options*.
- *Why it is W9a's.* The gate (`assembly_rebuild_settled`) only decides whether a False rebuild is laid to the
  user. With mates alone the rebuild returned True on 2024 too (v24:51), so the gate is not reached. With 2024's
  findings `None`, the Update simply goes ahead. Before W9a it refused every user mate.
- *What is needed.* The decision the coordinator is putting to the user, then its measurement on 2024. Until then,
  the app on 2024 should not press on with the user's work in error. Option 1 below is the one that needs no new
  SolidWorks call, as far as it reaches.

**2. Must fix before W9a closes: a failed Update does not name the user's features in error, so K3 holds only when
the Update goes ahead.**

- *The code.* `ui_text.gearbox_update_status` returns early on `result.failures` with "Update SolidWorks stopped.
  …", before `_user_after` and `_user_feature_sentences`. `_rebuild_sentence` adds only what was in error *before*
  (`user.in_error`). So a user feature newly in error is in `result.user_features_in_error` but not in the status:
  - when the Update fails for another reason (an app feature in error as well:
    `test_the_same_with_an_app_feature_in_error_in_another_part…` asserts only the failure text);
  - whenever the M3 findings are `None`, which is all of 2024 today.
- *The consequence for 2024.* That is exactly the first run's k3 failure, still standing on 2024. The script's k3
  check on a version whose findings are `None` expects the sentence to name the keyway
  (`judge_user_error_update`'s else branch, `bool(frags)`). So 2024's confirming k3 will fail as the code stands.
- *What to do.* Either the failure status names the user's features as theirs, before or newly, as the success
  status does (K3 asks it of every job), or the expectation is changed by a ruling.

**3. Should fix: the findings' comments cite only the first run, though the closing run strengthens and in one place
corrects them.**

- *`WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2026`.* The comment says "Show errors every rebuild was not read in this
  run". The closing run read it True (c1:41) and repeated each reading:
  - the mate case, True with What's Wrong 3 (c1:55);
  - the feature case, False with What's Wrong 1 and Sprocket-1 code 1 (c1:111-113);
  - no window after either (c1:51, 55, 107, 111, 113).

  More important after 2024 (finding 1): the finding's name covers an assembly rebuild. What the app relies on is
  that its whole Update opens no window with the user's work in error. On 2026 that is now shown with the toggle
  on, by the Updates themselves:
  - m3's mate Update (c1:91-105);
  - m3's feature Update (c1:148-161);
  - k3 (c1:786-800).

  Add those lines to the comment and pin them.
- *`USER_MATE_PUT_NO_CARRIER_ON_2026`.* The closing run ran nocarrier with the finding committed True, so the patch
  was a no-op, and read both presses clean with the footer's carry equal to the press's (c2:1350-1414). Add it.
- *The gate's reach.* Its comment lists what was not measured. It should also say what the gate opens:
  `user_carry_branches` labels every no-carrier train of a gearbox without modes `NO_CARRIER`. That includes
  crossed-axis trains, ring trains, idlers, several trains and compound pairs, of which only the parallel 12 : 1 was
  run. The risk is bounded, since route (c1) reads every carried pose back. But "the 12 : 1" is the evidence, not
  the scope of what the app now allows.
- *The CAM finding.* `LIGHTWEIGHT_SAVE_RAISES_AN_ADDIN_DIALOG_ON_2026` is right as written (findings.py:933-940).

**4. Should fix: condition 2 does not read the assembly's own feature tree.**

`_rebuild_laid_to_user` judges every mate (`mate_states`), every top-level component (`components`) and every app
part's features (`features_read`). The assembly's own non-mate features are not read: its equations (the Face Z
globals), reference geometry, and the user's assembly-level cuts or patterns (`W9A-INTERFACES` §5 already names the
last as unread).

So if a user's component is in error while an app equation in the assembly fails, the rebuild is laid to the user,
and the status says "nothing of the app's is in error". The combination is rare and nothing measured it. Either read
the assembly's feature tree for errors (anything not a mate and not the user's counting as the app's), or say the gap
in item 11 and the plan.

**5. Should fix: the new refusal of a carried component in error is not shown foreseen on SolidWorks.**

- *What the log shows.* The step's refusal was judged before any write: no changing call, nothing written, recorded,
  then said in red (c1:182-203). But the footer before the press was green: "leaves your Sprocket-1, Housing-1 and 3
  mates as they are. Your Sprocket-1 was already in error" (c1:179). Its inventory predates UserLockSun (made at
  c1:163, with no quiet press after it), and the script passes no `ahead` to `refuse_press`.
  - That is K4 working for what the record did not hold.
  - But the claim "foreseen by the footer" is not on the log.
- *What to add.* A quiet press after the lock, so the record holds it (a quiet press carries nothing, so it does
  not refuse), then the footer's prediction held against the refusal.
- *A related gap.* A carried component whose error code reads UNREAD is not refused: `_in_error(UNREAD)` is False.
  That is unlike condition 2's "unread counts as in error". Refuse it too, or say why not.

**6. Should fix: `stays_said` can pass a question that omits something.**

- *Features.* A feature is "said" when its name and its part's file stem each occur anywhere in the text. "User
  Keyway" is a substring of "User Keyway Sketch". Every Build again… question opens with the old part's stem
  ("Gear_m1.25_N29 (Sun): its Part name…", c3:46). So a question naming only the sketch, or naming the keyway
  without its part, passes.
- *Mates and components.* The mates' count (`\b8 mates\b`) and the components' "N other components" are found
  anywhere in the text, not in the clause that says what stays behind.
- *How to tighten it.* Match whole names (as the components' regex already does) and find the stays-behind clause
  first ("stay in RangeBox.SLDASM", "stay in <stem>").
- *Why the run is still sound.* The closing run's questions do say everything (c3:46, 334, 622). The looseness is in
  what the check could catch, not in what was said.

**7. Should fix: the value under a user feature can be said as a raw equation, and "type … again" can name a value
the cell never held.**

- *The raw equation.* `_values_set` gives `now` as `_number_text(_literal(expression), expression)`. For a global set
  to an equation, such as a blank Backlash's default, that is the raw expression with its quotes, said in "after
  this Update set Backlash 0.4 to …".
- *The wrong value to retype.* `was` is SolidWorks' evaluated value. For a cell that was blank, "type 0.375 in
  Gears!P2 again" names a value the cell never held.
- k3's case is a typed Bore, which reads right (c1:790).

**8. Should fix: three things the plan and the note should say.**

- *The static path.* A False assembly rebuild there stays a failure, and its user locks are not judged (INTERFACES
  §4 item 11 and §5). The plan's new section says the rule without the limit. Put it there, since the user reads
  the plan.
- *Lightweight, as the run read it.* After `SetSuppression2(1)` on Sprocket-1 alone, `GetSuppression2` read 1 on all
  four instances of Sprocket.SLDPRT; Housing-1 stayed 2 (c1:936-938). The app's inventory agreed (c1:969), and the
  refusal named exactly the three carried ones (c1:996).
  - This proves the app's read is not the fault: it reads what the script's own raw call reads.
  - It does not prove that SolidWorks "made every instance lightweight". Both reads are the same member, and no
    second kind of read was made.
  - The reset set each instance back one by one (c1:997-1003), so whether resolving one resolves all is not known.
  - Write it as "SolidWorks reports every instance of the part lightweight when one is set". It is a fact for W9d,
    which will resolve components before saving.
- *The 2024 decision (finding 1),* once taken, as a dated change to the plan's new section. That section now says
  "where the findings are None … the Update stops as before", which is not what 2024 did.

**9. Note: the three closing logs stand as one closing run of twelve sections.**

- *The case for it:*
  - one app source;
  - one session started fresh for the run (c1:4, c2:4, c3:4, all PID 6328);
  - one `out` folder, with setup.master made in c1 and used by c2 and c3;
  - each section's last run 0 failed.
- *The again sections.* They failed in c2 only on the script's checks of the question's words (c2:481, 763, 1047,
  1279). Their reads of the old assembly passed there too. They were then rerun whole with `--redo` at `6b9d8aa`
  (c3:2), whose diff touches only those checks.
- *Section times:* m3 942 s, reducer 85, k3 41, setup 190, lightweight 244, go 682, m1 132, refuse 1154, nocarrier 57,
  and in the rerun again 283, again-dirty 284, again-closed 88. That is about 70 min, with no hang and no cut.
- *Counts:* 159, 231 and 60 `ok` lines. c2's done line says 4 failed, all again's wording (c2:1423).
- *Clean:* no STOP and no dialog but progress boxes, balloons and the notification box (`grep` of the three logs).
  Every copy ended clean.

**10. Note: m3's and k3's checks now fail when the app does the wrong thing.**

- *What `judge_user_error_update` demands.* With the Update expected to go ahead, `result.ok` must be True, the
  sentence must name the item, it must say "in error … before" exactly when the item was, and the check phase must
  have read it so.
- *What it would catch:* a stop; a missing name; "before" said of k3's newly broken keyway, or left out for m3's
  Sprocket-1.
- *The one way left to pass wrongly* is a go-ahead for the wrong reason, with nothing of the app's in error in the
  scene. m3 and k3 set up no such scene, but the unit tests cover it (`test_an_app_mate_in_error_after_the_rebuild…`,
  `…app_feature_that_cannot_be_read…`, `…not_read_stays_a_failure`, `…nothing_of_the_users_in_error…`).
- *The facts on the log.* The app laid each False rebuild to the user: `['Sprocket-1']` (c1:160) and `['User Keyway
  in Gear_m1.5_N17.SLDPRT']` (c1:798). G1's own component read code 1 after k3 (c1:800), which is why condition 3
  was needed.
- *A remaining gap.* m3 does not read frames after its gone-ahead Updates. It rests on the app's own post-check,
  which would have made `ok` False.

**11. Note: K12 on the real screen holds, on W8's footers.**

- *The geometry, in read and built* (w lines at 00:07:44 and 00:11:05; 2560 × 1528 work area):
  - the frame runs 0…1524 inside the work area 0…1528;
  - the client runs 45…1513, 1468 px, equal to Tk's height;
  - the body pages scroll (`page_scrolls` True);
  - the footer box is 1166 × 106 and then 893 × 281, its bottom at 1450 of 1468, not scrolling;
  - every footer button is whole, and the body's last line is scrolled into view.
- *A sentence set alone* fits the same way with the page not scrolling (00:11:05).
- *Not shown on screen:*
  - the footer's ceiling;
  - a W9a footer carrying the user-work line, the longest the app now writes (this stage builds W8's TransferCase,
    not RangeBox with user work). The Tk test is the only cover for both.
- The doubled full stop in "press again.." comes from the probe's own injected sentence (`workbook_window_check.py`
  :734), not the app.

**12. Note: smaller items.**

- *2024 memory.* SolidWorks 2024 grew from 0.66 GB at attach to 4.04 GB before its first quiet press, and to 6.97 GB
  after it (v24:4, 57-58). The second 2024 session should watch it against the 2 GB stop.
- *The ok line's mate codes.* It says "(46 over defined, 47 ill defined)" on 2024, where the codes read 51
  (v24:52). That text is the script's, not a reading (`MATE_ERROR_2024`'s comment rules against reading codes for
  meaning).
- *The repeated refusal.* The lightweight refusal says the same reason three times in full (c1:975). INTERFACES
  defers it, rightly flagged.
- *The bore sentence* now reads "no bore (its Bore blank or 0)" (c2:395), my first review's finding 10.

---

## 1. The worker's change against the four conditions

- **Condition 1, something of the user's in error:** a user component's code, a user feature in an app part (after
  its change where this Update set the part, else before), or a user mate only where the version's mate finding
  says mates make the rebuild False. On 2026 it does not, so mates alone never explain a False. ✓
  (`test_a_false_rebuild_with_nothing_of_the_users_in_error_stays_a_failure`,
  `…only_a_user_mate_in_error_is_not_laid_to_it_on_2026`).
- **Condition 2, nothing of the app's in error, read whole:**
  - every recorded mate on and in error, a warning excepted as in the post-check; an UNREAD code fails;
  - every app component's part must be in `features_read`, after its change or before, or it fails;
  - an app feature in error or UNREAD fails;
  - a raise from `mate_states` or `components` fails.

  A document set by this Update but not re-read after drops out of the before-read and then fails the
  component-part test, so the gap closes on the safe side. The gap is the assembly's own feature tree (finding 4). ✓
  otherwise.
- **Condition 3, an app component's own code not judged:** right, and the log shows it was needed (c1:800). ✓
- **Condition 4, gated per version:** `assembly_rebuild_settled` returns None unless all three findings are set.
  The rule also requires What's Wrong False and feature False. ✓ The gate does not reach finding 1's case.
- **Both paths.** The rule is applied in `_modes_assembly.rebuild` and `_motion_assembly.rebuild`. m3 (modes, c1:160)
  and k3 (no modes, c1:798) each went ahead. The static path is unchanged and stays a failure (finding 8).
- **The new refusal.** `judge_user_work` refuses a carried component that reads in error. It is the same judgement
  the footer runs, and it is judged in the check phase before any write (c1:186-197). Not foreseen on the log
  (finding 5).
- **What "in error before" rests on:**
  - for features, the check phase's `feature_states` of each app part, which are part-level;
  - for components and mates, the check phase's read in the active configuration only (INTERFACES §4 items 12
    and 16). The status says so: "in the mode showing before this Update changed anything" (c1:96, 152).
- **`NO_CARRIER_MODES`.** It is right: `user_carry_branches` would have given the TransferCase's no-carrier trains the
  2026 finding. The only other `_ON_{year}` gates in the app are the branch findings, the M3 trio,
  `SLIDE_VALUE_PER_CONFIGURATION` and `TURN_PER_CONFIGURATION` (`grep`). Of what W9a set True, only `NO_CARRIER`
  opens anything, and finding 3 says how far.

## 2. The new sentences

- **A failure.** Any failure returns "Update SolidWorks stopped. …" first. `_users_alone` keeps a part's "(SolidWorks
  reported an error rebuilding it)" off only when there is no failure at all and a user feature in that part is in
  error. A part not rebuilt with no failure implies `theirs_alone`, so the app's features there were read clean.
  `_rebuild_from_user` speaks only when the worker set `rebuild_from_user_alone` and the last rebuild is False. No
  path softens an app failure. ✓
- **The combinations of a user feature in error:**
  - before: "was in error … before this Update changed anything, and still is";
  - newly, with a value set and its cell: "is in error … now, after this Update set Bore Diameter 8 to 14 (Gears!J2)
    in that part: change your User Keyway to fit, or type 8 in Gears!J2 again" (c1:790);
  - newly, with no value under it: "rebuilt after the app's features: change … to fit".

  All are true, but for finding 7's equation and blank cases.
- **The failure combination** says nothing of the user's newly broken features (finding 2).
- **R1 to R3** read right on the run's footers: "has changed since … the next press would stop for the same reason"
  (c2:306); a tie read on more than three of the user's mates counted, not listed (c2:1347).

## How each finding in `findings.py` stands

| finding | as committed | |
|---|---|---|
| `USER_MATE_PUT_NO_CARRIER_ON_2026 = True`, `_2024 = None` | accept | add the closing run and the gate's reach (finding 3) |
| `USER_MATE_PUT_NO_CARRIER_MODES_ON_2026/2024 = None` | accept | |
| `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2026 = True` | accept | add c1:55 |
| `ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2026 = False` | accept | add c1:111-113 and k3's go-ahead (c1:798) |
| `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2026 = False` | accept | add the toggle (c1:41) and the three Updates (finding 3) |
| `LIGHTWEIGHT_SAVE_RAISES_AN_ADDIN_DIALOG_ON_2026 = True`, `_2024 = None` | accept | |
| every M3 `_ON_2024` | `None` | `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2024` may become True from v24:51; the What's Wrong one may not become False |

## *Done when*, clause by clause, for SolidWorks 2026

| clause | now |
|---|---|
| the suite is green | 3378 passed, 1 skipped, and the known font-width test failed; my run stopped there, so the last 25 Tk window tests are unverified by me; `test_workbook_xlsx` and `test_findings` pass |
| a value and a slide-offset Update go ahead with the user's work; the sprockets on their gears; every user mate on in its modes and in no error; the keyway rebuilt | **shown** at `6f3d6fb` (c2:78-94, 134-150) |
| a lock to a fixed housing refuses naming it | **shown** (c2:272-290) |
| a Bore Diameter typed in SolidWorks refuses naming the cell | **shown** (c2:395-413) |
| M1–M3 answered | M1 as ruled in the plan (`3e7307a`), read again (c1:851-859; c2:189-210); M2 (c1:901, 766); M3 answered, and K3 met in an app part (c1:786-800) and in the user's own part (c1:148-161) |
| the window check's W8 stage passes with K12 | **shown** (w, 0 failed; finding 11) |
| 2024 confirms the assembly sections | **not met**: stopped in m3 (finding 1) |
| reviewed | this review, with findings 1 and 2 open |

## The 2024 fact and the options

**What the log shows.**

- *The setting.* SolidWorks 2024 32.5.0, a fresh session (v24:4), "show errors every rebuild" read True (v24:37 —
  line 37, not 39).
- *The script's own rebuild.* With UserGap made over-defining (v24:50), the script's own `ForceRebuild3(True)`
  returned True, What's Wrong 3, codes 51 and 51, and no new window (v24:51).
- *The quiet press.* It read the same assembly and its user mates with no box (v24:56-66). So the check phase's reads
  alone do not raise it.
- *The footer* named both mates in error before the press (v24:82).
- *The value Update.* During it, the watch saw a #32770 titled "What's Wrong", with Show errors, Show warnings,
  "Display What's Wrong during rebuild", FeatureXpert, Close and Help (v24:88-89). The worker was inside
  `GetNextSubFeature` when it was seen. The script stopped at once and marked the worker hung (v24:90-96).

**What it does not show.**

- *Which call raised the box.* The watch polls every 2 s (`DialogWatch`, `time.sleep(2)`) and names the innermost
  traced call at that moment. `GetNextSubFeature` is a feature-tree walk, the app's mate or feature read, not a
  rebuild. Had the box held the rebuild call that raised it, that call would have been named. So the call that
  raised it had most likely returned, and the worker had gone on. That is evidence, not proof: `GetNextSubFeature`
  may itself have been held.
- *What had been written.* The press never returned, so its trace and steps are not in the log. Since the quiet
  press's identical reads raised nothing, the box most likely came after the first write (Sun's Backlash) and a
  rebuild. That is an inference.
- *Whether the Update would have completed,* or whether the box is modal. `watched_wait` stops on sight by design.
- *The other cases.* Whether a feature in error (m3's second case, k3) raises it on 2024: not reached. Whether it
  opens with the toggle off: not tried. Whether the same happens with mates in error that are not over-defined: not
  tried.

**What 2024's findings may say.**

- *May:*
  - `ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2024 = True` from v24:51 (one reading, same scope as 2026's). It
    changes no behaviour while the other two are `None`.
  - A new per-version fact, which the app could gate on: `WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_2024
    = True` ("show errors every rebuild" on; RangeBox in H; two user distance mates over-defined, codes 51; during
    the app's value Update; the call not known; never answered; v24:37, 51, 88-90). Its 2026 counterpart is False,
    from c1:41 and 91-105.
- *May not:*
  - set `WHATS_WRONG_OPENS_ON_ASSEMBLY_REBUILD_ON_2024`. Not False, since a box opened in the Update. Not True,
    since the explicit assembly rebuild opened none;
  - set the feature finding (not reached);
  - say the box is modal, which call raised it, that the Update would fail or would complete, or anything with
    the toggle off.

**The options, and what each needs before it can be relied on.**

- **Option 1: refuse on 2024 when something of the user's is in error, before any write.** It needs no new
  SolidWorks call: the check phase reads the user's mates, components and features in error already, and a refusal
  makes no rebuild. Its limits are what the check phase cannot see:
  - a user mate or component in error only in a mode not active, since modes other than the active one are read
    only after their put;
  - anything the Update itself puts in error, such as k3's keyway, newly broken after the write.

  Before relying on it: show on 2024 that a press with nothing of the user's in error raises no box. W8's and S0's
  2024 runs suggest so, but with no user work. And measure k3 on 2024, to learn whether a feature newly in error
  in an app part raises the box. If it does, option 1 alone cannot cover K3 on 2024.
- **Option 2: turn "show errors every rebuild" (toggle 77) off for the job and set it back,** as `begin_build` does
  with `INPUT_DIM_VAL_ON_CREATE`. Setting 77 False has not been done on either version. S0's P0 found it True on
  both and so never set it (`w9-s0-sw2024-20261116-065000.log:8`). Before relying on it, measure on 2024:
  - that with 77 off, m3's two Updates and k3 complete with no window and with the 2026 results;
  - that the box's "Display What's Wrong during rebuild" is this toggle;
  - that the app's error reads (`GetErrorCode2`, `GetWhatsWrongCount`) still see the errors;
  - that the set and the set-back mark no document;
  - that the toggle is restored, read back, on every exit, a raise included.

  Two facts must be said plainly. A hung or killed session leaves the user's SolidWorks preference changed, since it
  persists. And the user's word is needed, since it changes their setting during the job.
- **Option 3: leave the box to the user.** Before relying on it, measure on 2024 whether the box blocks the job.
  - If it does not, show the Update completes with the box standing, with every result as on 2026.
  - If it does, a person must close it during the job; show that the job then completes with the bodies home, the
    carried sprockets on their gears and the user's mates as they were.

  The app would then have to say, while it waits, that SolidWorks may show What's Wrong and that it should be
  closed. FeatureXpert, in the same box, is an action the app could not account for.

Whatever is chosen, 2024's confirming m3 and k3 cannot pass until then. setup, go, reducer and nocarrier have nothing
of the user's in error and are unaffected.

## What I could not verify

- Anything on the Windows host: the run folders and how the 2024 session (PID 42932) was ended.
- The 25 Tk tests after the font-width test, and the Windows window tests at `6f3d6fb`.
- Whether the What's Wrong box on 2024 is modal, which call raised it, and what the Update had written by then.
- Whether resolving one instance of a part resolves all its instances.
- Package B's R1 to R3 beyond the footer lines the run shows. I read `84b9303`'s diff to `workbook/update.py`, not
  every new test.
