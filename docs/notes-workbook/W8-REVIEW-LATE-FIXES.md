# W8 review of the late fixes: the Update's puts, the "can show" sentences, s7 case 8 and the 2024 s7 run

*Independent, read-only, 2026-11-15. I changed no code, test or finding, and ran nothing on the Windows host.* Line
numbers are at `8702389`. Under review:

- **A, app behaviour:** `a87c1c5`, `baa1a56`, `c4b827a`, `d149e01`, `c41590c`, `c825611`.
- **B, record and sentences:** `8140d35`, `a90a2ee`, `81aa0bb`, `4b164a7`, `28c903c`, `5989c7d`, `4e8acea`,
  `985bcbe`, `2d6d3ef`.
- **C, the demonstration script:** `48ab0aa`, `7c9634d`, `f765894`, `1560b25`, and the script change in `8702389`.
- **D, the window:** `d9747af`, `a666a27`, `b70aa40`.

`6b16963` landed while I wrote this: case 8 rerun alone on 2024 at `8702389`, 0 failed
(`probe/results/sw2024/w8-workbook-assembly-20261115-172046-s7-case8.log`, written ":c8" below). I read it and folded
it in. It closes MF1's 2024 half, and it sharpens N2.

Logs are cited by file and line. The lines are of the logs read through `iconv -f cp1252`.

---

## Verdict

**The app holds in every state the evidence allows.** I found no path through the modes Update that leaves a mode
wrong while reporting it right, and none that reports red for a right document. That holds under both possibilities
left open on 2026: a turn that does not reach some modes, or a put that does. Since `a87c1c5` and `baa1a56`, every
mode an Update shows is put whole to its built frames wherever it is off its axis, out of step or turned, or wherever
the Update has anything to put at all. The puts in different modes all go to the same rotations. The only per-mode
difference in the wanted frames is a slider's place along its axis, and a slide mate holds that place in every
configuration. The one state in which a mode can stand wrong under a green status is the quiet Update that puts
nothing. That status says it did not show the other modes (ruling 11), so it does not claim the mode is right.

**The sentences are true where they are said, with one exception and one overclaim in the docs.**

- *The exception.* After an earlier Update that was never saved, a coupling crossed in the mode worked in is still
  said twice. The second time it comes with "the turn may have been given in another", which lays a turn to the
  user (S1).
- *The overclaim.* UI-DESIGN §9 says SolidWorks carried a turn "into some modes and not others" after an Update.
  Ruling 9.18 itself leaves that open, and 2024 now reads the opposite in that state (S4).

**The demonstration closes M1 and M2 in the script, but not in the evidence.**

- s7 now holds its turns and its moving puts to the version's findings, with STOP lines, and the 2024 run shows those
  holds working.
- Case 8 is the measurement M1 asked for. It has now finished on 2024 (`6b16963`), but it has not run on 2026, where
  the question is open.
- Case 8 also holds nothing about the app's own Update, which it presses (MF1).
- On 2024, case 8 read neither 2026 possibility. In that state the turn reached all four configurations, and the
  moving put stayed in 2H. So 2026's s2 reading needs 2026's own case 8 (N2).

**The 2024 s7 log supports its commit message on every reading I checked, with one overstatement:** that the 2024
readings "match 2026's" (N1). On 2024 it justifies **`TURN_PER_CONFIGURATION_ON_2024 = False`** (S3).

**Must fix before the closing run:** one item, MF1. **Should fix:** six. **Notes:** ten.

---

## Must fix before the closing run

**MF1. s7 case 8 has not run on 2026, and it holds nothing about the Update it presses.** (`probe/workbook_assembly_check.py`
8010-8045; `probe/results/sw2024/w8-workbook-assembly-20261115-162357-s7.log` 1136-1140)

- *What it is for.* Ruling 9.18 (`W8-INTERFACES.md` 335-338) and the turn comment in `findings.py` (1271-1274) name
  this case as the measurement that settles the open question on 2026. The sequence is: a turn, an Update that puts
  every mode, a fresh turn, then a moving put, with every configuration read after each.
- *Where it stopped on 2024.* At the moving put (log 1136): *"Gear_m1_N24-2 did not take its frame (rotation off
  1.1e-16, origin 3.9e+00 mm)"*. The saved-and-reopened step after it never ran.
- *Whether the commit's reason holds.* The commit says the script put the planets before the carrier, so the planet's
  axis mate, which belongs to the carrier part, held it at the carried place. That is consistent with the log.
  - 3.9 mm is the planets' radial offset with the carrier turned 9.25° (the table at 1110-1124: `[3.870]`).
  - The error names the first planet, put just after the Sun.

  The rerun bears this out. With the carrier put first (`8702389`), the same put took on 2024 (:c8 219-224).
- *On 2026.* The case has never run. The 2026 s7 run (`…-135401-s7.log`) predates it.
- *What it does not hold.* Case 8 presses the app's quiet Update (8024) and logs `put_in` and `failures` as a fact
  (8028). It checks neither, and it does not hold the read after the Update (`c.read`, 8029) to the built frames. So a
  closing s7 passes case 8 even if the app's Update fails or leaves a mode turned. Case 4 does check its Update
  (`check(result is not None and result.ok, …)`, 7964).
- *Change.*
  1. In case 8, add a check that the Update went through: `result.ok`, no failures, and `put_in` holding every mode.
  2. Hold the read after the Update to the frames on record in every configuration (`frames_gap`, as `S7Case.read`
     already computes them). The 2024 tables at 1091-1105 and :c8 174-188 read 0.000 everywhere, so this passes on
     the evidence. The rerun still only logs the result (:c8 172).
  3. Before the closing run, run `--only s7 --s7-cases 8` alone on 2026. Its put path has never run on 2026, and ruling
     9.18 is to be written from its result.

---

## Should fix

**S1. After an earlier unsaved Update, a crossed coupling is said twice, and a turn is laid to the user.**
(`src/gear_generator/ui_text.py` 3328-3336, 4004-4017, and `_earlier_update_sentence` 3398-3445)

- *Why it happens.*
  - `d149e01` skips a coupling in `_motion_after` only inside `if not earlier:` (3328). With `earlier` set, that whole
    loop is skipped, and `_earlier_update_sentence` says the pair instead (from `Finished.out_of_step_after_update`).
  - `_mode_after` takes no `earlier` and says the pair again in its per-mode form. Then it says that the turn may have
    been given in another mode.
- *Verified by a scratch run* of `gearbox_update_status`, using `test_ui_text`'s `_tc_update` and `_tc_moved`. The
  setup: 4L worked in, RangeSlv–LoDog crossed, every mode put, the switch False. With `earlier="not saved"` the status
  reads:

  > *Updated SolidWorks: re-placed RangeSlv in every mode; no interference between the gears where they stand.
  > RangeSlv and LoDog were not in step as the last Update SolidWorks, which is not saved, has them on record; they are
  > in step again. In 4L, RangeSlv's teeth stood across LoDog's; the gears of 4L are back at the turn they were built
  > at. This version of SolidWorks can show a turn given in one mode in the others, so the turn may have been given in
  > another. …*

  With `lost`, the first sentence is *"… so its changes were made again: RangeSlv and LoDog are back in step with each
  other."*, and the rest is the same.
- *Why it matters.* The earlier-update rule (`_earlier_update_sentence`'s docstring) is that a relation found out of
  step after an unsaved Update "is never said to be the user's doing". *"The turn may have been given in another"*
  breaks it.
- *Change.*
  1. Pass `earlier` to `_mode_after`.
  2. With it set, either say the crossed coupling only in the earlier-update sentence, or keep the per-mode form and
     drop the pair from that sentence.
  3. Drop the "may have been given" sentence in either case.
  4. Pin both kinds of earlier Update on the full status.

**S2. The records have not taken in what the 2024 s7 run read.** (`src/gear_generator/findings.py` 1243-1256,
1258-1281; `W8-INTERFACES.md` 336-338)

- *Case 5 on 2024 measured what the records list as not covered.*
  - *A mated body's moving put on 2024.* FIdler was put with its mates on, +20° in N and +10° in 4H, and each stayed in
    its configuration (log 831-859). `findings.py` 1256 still lists "a mated body … on 2024" as not covered.
  - *A turn given while the configurations already stood differently.* `findings.py` 1277 and ruling 9.18 line 336
    still list it as not covered. On 2024, FrontDog driven +15° in N (log 863-884; JSON
    `same_amount_or_place`) left FIdler at −2.500° in all four configurations. Before the drive it stood at 0, +10,
    +20 and 0. So the turn wrote N's place into every configuration, and 4H's own put of +10° was lost. Not one of
    s7's four hypotheses fits that reading (log 883: "fits none").
- *What that means for the put fact.* "Kept its place in the configuration showing alone" (`findings.py` 1245) holds,
  on 2024, only until that body's train is next turned in any configuration.
- *A citation is missing.* "And 2024, which _2024 rests on" (1250) names no file. The 2024 follow-up's result file
  should be cited.
- *The turn comment cites a run the script no longer reproduces.* *"s7 case 4's Update moved only the front train"*
  (1272) is true of the 2026 run `w8-s7-20261115-135428.json`. Since `7c9634d`, case 4 turns the train first, so a
  closing 2026 s7 will read otherwise. Say "in the 135428 run".
- *Change.* Record the three readings with the 2024 JSON cited. Pin them in `tests/test_findings.py` against
  `probe/results/sw2024/w8-s7-20261115-162418.json`, as `_s7_holds` pins 2026's. The JSON fields to pin:
  - case 5's three put judgements;
  - `same_amount_or_place` (same place True in all four, same amount True in N alone);
  - case 4's and case 8's turn judgements.

**S3. Set `TURN_PER_CONFIGURATION_ON_2024 = False`, from the 2024 s7 file, before 2024's s2 runs.**
(`findings.py` 1281; ruling 9.18's "2024 None until the confirming run's s2 and s7")

- *What the file shows.* In every turn s7 gave on 2024, every body the drive moved read "moved" in all four
  configurations, "shared" was among the fits and "per_configuration" was ruled out:
  - cases 1-3 (log 81-92, 205-216, 397-493);
  - case 4 after the app's changed Update, whose puts moved the turned train back (tables at 549-745; judgement 730-740,
    fits only "shared");
  - case 8's fresh turn after the app's quiet Update had put every mode (1110-1135; again in the rerun, :c8 193-218),
    fits only "shared". In the rerun, a moving put in 2H then stayed in 2H (:c8 225-250), the put fact's reading.

  The tables give LoDog +9.25° against RangeSlv +37° in 4L, where they are coupled: a dog across its sleeve. That is
  the hazard the False sentences warn of. "Can show in other modes" is therefore true on 2024 in every state measured.
  It is more strongly supported there than on 2026.
- *Why before s2.* `section_s2` asserts nothing about a turn in the other modes while the switch is None (probe
  6806-6809). So a 2024 s2 run with None cannot be the run that "chooses the sentences" (W8-PLAN §6 item 4). And on
  2024 today, a quiet Update after a turn in step says nothing of the other modes, though s7 reads the turn there.
- *What changes with it.*
  - *App.* `swcom.positions_per_configuration((32, …))` returns False, not None. No behaviour changes: the switch
    chooses sentences only.
  - *Sentences on 2024:*
    - the build footer and record line say `TURN_CAN_SHOW_ELSEWHERE`;
    - a quiet Update that finds the gears turned in step adds `TURN_SHOWN_ELSEWHERE`, or `GEARS_SHOWN_ELSEWHERE` after
      an earlier unsaved Update;
    - a put of a crossed coupling adds *"This version of SolidWorks can show a turn given in one mode in the others,
      …"*;
    - a flags-or-values Update can say *"The gears of … stood at the turn they were built at …"*;
    - `switching_note` stays empty.
  - *Tests.*
    - `tests/test_findings.py` 1135: the 2024 finding asserted None. 1233-1237:
      `positions_per_configuration((32, 5, 0)) is None` and the docstring's "on 2024 neither claim is made".
    - A new pin of the 2024 turn readings against the 2024 JSON, the twin of `_s7_holds`, with
      `revision == [32, 5, 0]` and `finding_turn` None at the time of the run.
    - `tests/test_swbuild_modes.py`'s switch test sets the finding itself, so it is unaffected. So is the
      `mode_findings` fixture, which pins True for both years.
  - *Script.* s7's `s7_hold` starts STOP-checking cases 1-3 on 2024. s2's turn expectations and `SHARED_MAY` checks
    apply on 2024.
  - *Docs.* UI-DESIGN §9's "Where it is unset (2024 until its confirming run): neither" (1111); ruling 9.18's "2024
    None"; the `findings.py` comment at 1277-1279.

**S4. UI-DESIGN states one of the two open readings as fact.** (`design/UI-DESIGN.md` 1111; also
`src/gear_generator/ui_text.py` 3584-3585, and `d9747af`'s message)

- *UI-DESIGN's built row* says *"SolidWorks was read carrying a turn into every mode on a gearbox no Update had moved,
  and, after an Update had put every mode, into some modes and not others"*.
- *What was read.* After an Update had put every mode, the fresh turn was read by the script in 4L
  (`…-151412-s2.log` 356). The app found 4H and N at the built turn **after its put in 2H** (448-451). Ruling 9.18
  says exactly that either the turn did not reach them or 2H's put did.
- *What 2024 adds.* On 2024, in the same state (case 8, 1110-1135; case 4, 730-740), the turn reached all four.
- *The `ui_text` comment at 3585* says *"read in 4L and not in 4H and N"* and drops the qualifier.
- *Change.* Reword both to what was read. For example: *"…and, after an Update had put every mode, in 4L, while 4H and
  N, shown after a put in 2H, stood at the built turn; which it reaches then is not settled on 2026."*

**S5. Two docs still describe superseded behaviour in their main text.**

- `docs/PLAN-WORKBOOK.md` 631-636. **J11 (measured)** still opens *"each configuration keeps its own positions: a turn
  the user gives in one mode stays in that mode"*. It also says the sentences follow
  `POSITIONS_PER_CONFIGURATION_ON_<year>`. The dated note under it says otherwise on both counts, and the sentences
  read `TURN_PER_CONFIGURATION_ON_<year>`. W8-PLAN marks its own approved text with "The text above is as approved".
  Do the same here, or correct the finding's name.
- `docs/notes-workbook/W8-INTERFACES.md` 343-352, ruling 9.18's *"A put on a quiet Update obliges the visit"*. Its
  first paragraph still gives the pre-`a87c1c5` behaviour as current: *"every other mode is then shown and handled as a
  changed Update handles it (put only where its own train needs it, J26 unchanged …)"*. Only the two amendments below
  it say what the code does. Mark the first paragraph as superseded by them.
- Neither doc says, as fact, that a turn "shows in every mode". W8-INTERFACES 373 quotes the old sentence only as
  "before:". W8-PLAN 1358 is the approved plan text.

**S6. The advice in the turn sentences leaves out what the press it recommends now does.**
(`ui_text.py` 3579-3588: `TURN_SHOWN_ELSEWHERE`, `GEARS_SHOWN_ELSEWHERE`, `TURN_CAN_SHOW_ELSEWHERE`)

- *The sentences.* *"…to put the gears back there, press Update SolidWorks with that mode showing."*
- *What they omit.* The sentences are true: with a dog across its sleeve in the mode showing, the quiet Update finds
  it out of step and puts. But since `a87c1c5` that press puts every train back in every mode. That includes the mode
  where the user turned the gears on purpose (2026 s2 204-214; 2024 s7 1014-1090).
- *Still open.* The s2-s7 review's N6 asked for this to be worded. It became broader with `a87c1c5` and is still not
  addressed.
- *Change.* This is C's to word, for example *"…; Update SolidWorks pressed there puts the gears of every mode back at
  the turn they were built at."* Alternatively, list it for the user as a reading to overrule.

---

## Notes

**N1. The 2024 s7 commit message (`8702389`) against its log and JSON.**

*Verified:*

| Claim | Where it is shown |
|---|---|
| The drive's turn showed in every configuration on unmoved copies, cases 1-3, held to nothing | log 92, 216, 408, 443, 493: "the turn finding is unset on this version" |
| Case 4's Update moved the turned train back, and the turn after it showed in every configuration | tables 549-745, judgement 730-740 |
| A moving put of one body stayed in its configuration, held to the put fact (True) | 834, 859, 909: `ok` lines from `stop_check` |
| A no-op put moved nothing | 184, 307-377; the per-body summary 1203-1264 |
| FrontDog +15° in N left FIdler "at the same place in every configuration, not moved by the same amount" | the `fact` line at 884; JSON case 5 `same_amount_or_place`: same place True in all four, same amount True in N only |
| The quiet Update in 4L put every mode in 903 s, with 52 puts | 1073, 1081-1082; JSON `update.put_in`, `seconds` 903.34 |
| The fresh turn in 2H then showed in every configuration | 1110-1135 |
| Case 7: the 4L value set with 2H active read back in 4L alone | 1189-1190: "before {… 4L: 66.0}; 4L set to 69 … -> {… 4L: 69.0}" |
| Case 7: a suppressed coupling's sense read right, marking nothing | 1188: "marks modified exactly []" |
| Case 7: the reversed raw flag read answered in document order | 1175-1187, the "names passed reversed" fact lines |
| The run's one failure is case 8's put | 1136; `done 1 failed` at 1275 |

*Contradicted or overstated:*

- *"On 2024 the readings match 2026's."* Three of the readings have no 2026 counterpart at the current script: case 4
  as redesigned, case 5's FrontDog drive, and case 8. In the state case 8 measured, 2026's only reading is the
  unsettled one (`…-151412-s2.log` 448-451).
- *"Its last step failed."* The failure was the moving put, the second-last step. The saved-and-reopened step never
  ran.
- *The order of the case-8 put.* The reason the message gives was, when it was written, an inference from the log.
  The rerun at `8702389` bore it out (:c8 219-224, 0 failed).

**N2. 2024 makes 2026's s2 reading harder to explain, not easier.** (the readings verified; the conclusion inferred)

- *What 2024 reads, in s2's own sequence.* Case 8, rerun at `8702389`, went through four steps:
  1. a turn in 2H;
  2. the app's quiet Update in 4L, which put every mode (761 s), after which every configuration read at its built
     frames (:c8 172-188);
  3. a fresh +37° turn in 2H, which showed in all four configurations (:c8 193-218, fits only "shared");
  4. the moving put of the train in 2H, back to its built frames by the app's route, which stayed in 2H. 4H, N and 4L
     still stood at the fresh turn (:c8 225-250, fits "per_configuration"; it survived a reopen).

  Case 5 adds that a turn writes its configuration's place into every configuration, and case 4 that the turn reaches
  all four after a changed Update.
- *What that predicts for 2026.* Had 2026 behaved like this, s2's second press would have found 4H and N still turned
  after 2H's put. They read at the built turn (`…-151412-s2.log` 448-451).
- *What is left.* Either 2026 differs from 2024 in that state, or the app's sequence differs from the script's in
  something that carries into other configurations. The app shows and rebuilds 2H before its put. Around the put it
  suppresses the lock and gear mates in 2H alone, turns them back on and rebuilds. Only then does it show 4H.
  Case 8 on 2026 can tell these apart, which is the other reason for MF1. Either way the app ends right: every mode is
  put and post-checked, and the script read every body of every mode at its frames after that press (464-471).

**N3. Each fix is covered, but `a87c1c5`'s own regression test no longer distinguishes it.** Mutants were run on a
`git archive` copy of HEAD:

| Mutant | Result | Tests that fail |
|---|---|---|
| `put_turned=False` (reverts `baa1a56`) | 5 failed | the two tkinter tests, plus `test_e4_a_turn_in_2h_then_a_flags_or_values_update_in_4l_puts_every_turned_mode_back[flag]` and `[value]`, and `test_e4_a_turn_put_back_in_the_mode_worked_in_names_the_modes_read_at_the_built_turn` |
| `moved = True` removed at `swbuild.py` 4231 (reverts the heart of `a87c1c5`) | 6 failed | the two tkinter tests, plus four in `test_swbuild.py`: `test_a_quiet_update_that_puts_on_2026_says_so_from_the_finding_as_committed`, `test_a_turn_in_another_mode_is_unseen_by_…[shared positions]`, and `test_a_put_in_the_active_mode_on_a_quiet_update_visits_every_other_mode_…` (both variants) |

- In the second mutant, `test_e4_a_turn_in_2h_then_an_update_in_4l_puts_every_mode_back_where_a_put_stays_in_its_configuration`
  (`test_workbook_modes.py` 1105) **passes**. Under `put_splits` every mode needs a put anyway (2H and N turned, 4H and
  4L crossed), and `put_turned` puts them.
- So since `baa1a56`, `moved = True` on the quiet path matters only where the judgement would miss something: a turn of
  whole teeth, or a mode found at the built turn. Where it does matter, it costs puts.
- Coverage holds through the exact-count tests. No change is asked.

**N4. `c825611`'s test pins a state a real Update no longer reaches.** Its message says a changed Update with a part
change and the active mode turned in step "puts no mated gear" and visits. Since `a87c1c5`, a part change makes `moved`
True (`swbuild.py` 4213), and every train is put. Since `baa1a56`, a flags-only Update puts a turned train. So
"turned, visited, nothing mated put" does not arise. The guard is harmless and the test is still a fair unit test, but
its docstring's claim that the state is reachable is stale.

**N5. The post-check sees a carrier-less train's whole turn only through its put.** (`swbuild.py` 4394-4410)

- The post-check holds every gear's origin and each train's step. A rigid turn of a train with no carrier (E4's front
  train) would pass it.
- That a mode "ends at its built frames" (`baa1a56`'s message) rests on `_put_train` reading each put back. In the
  demonstration it also rests on the script's independent reads after every press:
  - 2026 s2: 240-247 and 464-471, every body of every mode against its frames;
  - 2024 s7 case 8: the table at 1091-1105.
- This is W5's design, not new. It is said here because the Update's correctness is now claimed in exactly those
  words.

**N6. The `1560b25` exemption is narrow.**

- *How it matches.* A window is exempt only when its title is empty and its first eight child texts are exactly
  `NOTIFICATION_TEXTS` (`"Title", "Description", "Button1", "Button2", "Hyperlink Text 1", "Hyperlink Text 2"`, probe
  444, 711). A real dialog carries real texts.
- *A box that fills in later is judged again.* The `seen` key includes the texts (692), so a box whose texts are
  filled later is judged afresh and falls to the STOP branches.
- *What moved.* The only change is the branch order: the exemption now precedes `OPENING`. It already preceded the s5
  and configuration-call STOP branches. `DISMISS` still comes first.
- *What it does.* The exempt box is a NOTE, listed under "noted for a ruling". It is never answered: 2024 log 22, 617
  and 1270-1271.
- *Conclusion.* It cannot swallow a modal dialog that §0.5 says must STOP the run.

**N7. M1, M2 and the N points of `W8-REVIEW-DEMO-S2-S7.md`, as `7c9634d` left them.**

- **M1.** The script now does what M1 asked: s2 reads 4H, N and 4L after the fresh turn (6840-6841), and s7 has case 8.
  - The s2 reads are fact lines, not assertions. M1 asked to "assert them per the finding". With the finding meaning
    "can show", no assertion follows, so the fact lines are right.
  - The evidence is not in on 2026. s2 has not run there since `7c9634d`, and case 8 has run only on 2024 (MF1, N2).
- **M2.** Closed. `s7_hold` (7702-7723) STOP-checks a turn on an unmoved copy (cases 1-3) and case 5's moving puts
  against the version's finding where it is set. It logs them where the finding is unset. Case 7's value read is a
  `stop_check` (on 2024: 1190).
  - A closing 2026 s7 now fails if cases 1-3 read a turn per configuration, or if case 5 reads a moving put shared.
  - Case 4's turn, case 5's FrontDog drive and case 8 are measurements and can pass anything. That is right while the
    sentences say only "can show".
- **N2** (no-op rows in the JSON). Closed: they are marked "no-op put:" (2024 log 1203-1264).
- **N7** (a Halt ends only its own section). Closed by the message. I did not re-read `main`.
- **N8** (a drive whose mate moves the train on making ends the case). Closed: `S7Stop` (7823).
- **Not addressed.**
  - **N3**: the watchdog still runs in the Tk thread.
  - **N4**: the SOLIDWORKS CAM box is still answered No whatever the document.
  - **N6**: S6 here.

  None of the three was claimed.

**N8. The script still says "shown in every mode" in three places.** Docstrings and a log label at probe 185, 6673
and 6748. Line 6673 prints *"the sentence on a turn shown in every mode is …"* into every s2 log. Reword it when next
touched.

**N9. A quiet press that puts took 903 s on 2024.** That is 52 puts (1082), against 238 s on 2026 (`…-151412-s2.log`
205). It is the cost of `a87c1c5`'s "every train in every mode", and a 2024 user waits it out whenever a quiet press
finds a dog across. No change is asked. With N3 in mind, it is the user's to weigh.

**N10. The window tests.** `d9747af` re-pins the two 2026 turn sentences exactly. Its docstrings still say "as
committed" while setting `False` literally (`test_workbook_window.py` 2664, 2697; the earlier review's point 5). I
could not check its "1147 and 1087 px tall as before" here (no Tk on Linux). `a666a27`'s `gen.py` takes the footer from
`ui_text`, so the board says what the window says.

---

## The Update, path by path (question 1)

*Read in `swbuild.py` 4134-4471. "Possibility a": a turn that does not reach some modes. "Possibility b": a put that
reaches other modes.*

- **The quiet path with nothing to put** (4217-4229, `judge_only=True`). The active mode is judged where it stands,
  and a train turned in step there is not counted as needed (`put_turned` is False). Nothing is shown, put or marked.
  - Another mode may stand turned (a), or turned with a dog across (shared turn). The status says *"it did not show the
    other modes"*. That is ruling 11's sentence, and it does not claim that mode is right.
  - With the switch False and the active mode turned, `TURN_SHOWN_ELSEWHERE` adds the hazard. On 2024 today (None),
    nothing does (S3).
- **The quiet path with something to put** (4231, `moved = True`). Every mode is shown and every train put whole, the
  active mode last. Its `ModeCheck` is kept from where it stood, and every flag is read after the last put.
  - Under (a), each mode is put in its own showing.
  - Under (b), a later mode's put can reach a mode already post-checked. It carries the same built rotation, so the
    earlier mode stays right.
  - The one per-mode difference in wanted frames is a slider's place along Rear (`workbook/update.py` 1420). The slide
    mate holds that place with its per-configuration value. 2024 case 8's tables show axial offsets 0.000 in every
    configuration after a turn.
  - The script's independent reads after both 2026 presses found every body of every mode at its frames (s2 240-247,
    464-471).
- **The flags-only and values-only paths** (`fixes`, not `moved`). Every mode is shown. A train is put where it is off
  its axis, out of step or turned (`baa1a56`, 4346), and left where it is at the built turn.
  - Under (a), the untouched modes are found at built and post-check clean.
  - Under (b), a mode reached by an earlier mode's put is found at built and not put. This is the reading s2 gave for
    4H and N (448-451).
  - The active mode is judged in the loop like any other.
  - Without `baa1a56`, these paths failed red on a right intent: the 132348 log's planet copies. With it, the fake's
    `put_splits` tests are green.
- **One mode out of step.**
  - If it is the active mode on a quiet press, the path above puts every mode.
  - If it is another mode on a quiet press, nothing is seen, and the press says so.
  - On any changed press, that mode is put (`not here.in_step`).
- **Red for a right document.** I found no path.
  - The post-check's origins test (4394-4398) holds each gear to the mode's own wanted frame. Sliders are read after
    the show.
  - `_modes_flags_after` (4254) reads the flags against the record after the last put, so a flag a later put left
    changed is caught rather than missed.
- **Lone trains** (4345-4346). These are trains with no relation on in the mode; for them only "off its axis" counts.
  E4 has none in any mode, since every train holds a lock or a mesh that is always on.

## The sentences, state by state (question 2)

- **`TURN_CAN_SHOW_ELSEWHERE`** is the record line, and only with the switch False. It is true: cases 1-3 on both
  versions read a turn in other configurations, and so does 2024 case 8. The advice is incomplete (S6).
- **`TURN_SHOWN_ELSEWHERE`** (3349-3355) is said only with `result.turned` set, no mated gear put, nothing visited
  and the switch False. Since `a87c1c5` and `baa1a56` that means the quiet path with nothing to put, where the active
  mode is turned in step. "That turn" refers back to *"The gears stand where they were turned in SolidWorks."*, and
  "may stand across" is true.
- **`GEARS_SHOWN_ELSEWHERE`** is the same state after an earlier unsaved Update. It needs no antecedent, and it is
  true.
- **`_mode_after`'s "can show a turn given in one mode in the others, so the turn may have been given in another"**
  (4015-4017) is said with a coupling crossed in the active mode, the mode put and the switch False. It is true
  except after an earlier unsaved Update (S1).
- **"The gears of … stood at the turn they were built at when Update SolidWorks showed them"** (4018-4031) is said
  only for a visited mode that was not put, had nothing off its place and nothing out of step, and was not turned.
  - That needs a flags-or-values Update, as UI-DESIGN now says.
  - "Built at" means up to whole teeth (W5).
  - Under possibility (b) it is still a true reading, "when Update SolidWorks showed them", and it claims no more.
- **The quiet reason** (4039-4041), *"since nothing in 4H needed changing"*. A turn in step is not a need (answer 2),
  so it is true. After a failure the status takes another form ("Update SolidWorks stopped. …"), checked by a scratch
  run, so the reason is never said beside a stop.
- **The crossed-coupling line.** It is said once, in its per-mode form, when the mode worked in was put. The exception
  is the earlier case (S1).
- **`findings.py`'s comments.** They say only what the files show, and cite them: the 2026 s7 JSON, the s2 logs with
  lines, the follow-up JSON. The one gap is that the 2024 follow-up is uncited (S2).
- **The pins.** Each finding the app reads is pinned in `tests/test_findings.py`:
  - `TURN_PER_CONFIGURATION_ON_2026` against `…-111951-…log`, the 115500 check, the 135428 JSON and `…-151412-s2.log`;
  - `TURN_PER_CONFIGURATION_ON_2024` as None.

  `POSITIONS_…`, which nothing reads, is pinned too. The pins state the file's lines and fields; none re-derive them.

## Tests (question 4)

- `cd /home/m0obot/Gear-Generator && .venv/bin/python -m pytest -q` gave **2 failed, 3156 passed, 10 skipped in 44.16
  s**. The two failures are the known tkinter ones.
- Mutants: see N3.
- *Sentences stated or re-derived?*
  - The unit tests state each sentence literally at least once: `test_ui_text.py` 3292, 3318, 3343, 3370-3382;
    `test_swbuild.py` 6586, 6608; `test_workbook_window.py` 2675; `test_workbook_modes.py` 1226. Other assertions then
    use the constants, which is fine.
  - The demonstration takes `TURN_SHOWN_ELSEWHERE` from `ui_text` by design (probe 6546, 6777). So on SolidWorks, s2
    holds the app to its own wording. The wording itself is held by the unit tests above.
- The Tk window tests could not run here. I reviewed `d9747af` by reading (N10).

## Docs against the code (question 5)

- *UI-DESIGN §9 after `b70aa40`.* It describes the Update as it now is: every train put in every mode after a quiet put
  (`a87c1c5`), and a turned train put on a changed Update (`baa1a56`). It quotes the sentences verbatim, and the
  "stood at the turn" row is scoped right. The one overclaim is S4.
- *`PLAN-WORKBOOK.md` §4.5 and ruling 9.18.* Neither says, as fact, that a turn "shows in every mode". Each keeps
  superseded text in its main body (S5).

## What I verified, and what I infer

- **Verified, by reading the logs or JSON at the lines cited:**
  - every claim of `8702389` in N1;
  - case 5's same-place reading;
  - case 8's tables, in the 162357 run and in `6b16963`'s rerun (:c8);
  - the 2026 s2 readings at 204-247, 343-358, 430-471, 555-575 and 700-715;
  - s7's hold lines on 2024.
- **Verified, by running:**
  - the suite;
  - the two mutants (N3);
  - S1's status, in a scratch script on the test helpers;
  - that a failed Update's status does not carry the quiet reason.
- **Inferred, by reading the code:**
  - that no path leaves a mode wrong while reporting it right, or reports red when right (question 1);
  - that a leaking put can carry only the built rotation, and that slide mates hold the sliders' places;
  - N4 and N5;
  - why case 8's put failed (since borne out by the rerun);
  - N2's argument.
- **Not checked:**
  - anything on SolidWorks;
  - the window at 1080 px (no Tk);
  - the PNG render of `a666a27`;
  - `main`'s Halt handling (N7);
  - the 2024 follow-up file the `_2024` put fact rests on.
