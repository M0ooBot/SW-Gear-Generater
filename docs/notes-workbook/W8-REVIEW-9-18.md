# Review of ruling 9.18's commits: `eff7bad`, `933de81`, `d3c2e97`, `29ecba5`

*Independent, 2026-11-15, read only on code.* Under review: the commits that answer W8 s2 on SolidWorks 2026
(34.0.0, this host). s2 read a turn of the mated E4 train, given in 2H, showing in 4H, N and 4L. The plan had assumed
the other way, from the spike's follow-up (a free component turned by a `Transform2` put).

- R1, `eff7bad`: a put on a quiet Update leads to the visit of every mode.
- R2, `933de81`: three sentences reworded.
- R3, `d3c2e97`: the finding split into `TURN_PER_CONFIGURATION_ON_*`, which the sentences read, and
  `POSITIONS_PER_CONFIGURATION_ON_*`, which nothing reads.
- `29ecba5`: ruling 9.18 and the dated notes.

Line numbers are at `914553a`. The commits after `29ecba5` touch only tests and design files, so `src` lines are the
same as at `29ecba5`.

**Verdict.** R1 and R3 are right in substance, and the code does what the messages say:

- No SolidWorks call and no branch depends on either finding.
- A quiet Update that puts nothing makes exactly the calls it made.
- After a quiet put, the visit is the changed path's loop, on both variants of the fake.
- The finding agrees with its evidence, clause by clause.

Four things should change:

1. **Must fix.** The path the coordinator ruled a wording matter is worse than the ruling assumed. Right after the
   press, the footer shows the job's sentence alone, not the record line that carries the shared-turn warning.
   Turn the 2H train, press Update in 2H, and the user reads a green "already matches" while 4L stands with a dog
   across its sleeve. Nothing on screen says otherwise (point 1). The fix is one sentence, resting on the finding and
   on a reading the Update already makes.
2. **Should fix.** On 2026 as committed, the shared-turn sentence now repeats once per coupling found out of step.
   s2's own quiet Update in 4L found two couplings out of step, so it would say the sentence twice (point 2).
3. **Should fix.** No test run in this venv shows what a build or an Update says with the committed value. A mutant
   hard-wiring the old `True` into both passes the whole suite (point 3).
4. **Should fix.** The records leave out a reading s2 itself made: the app's own put of the mated train in 4L showed
   in 2H, 4H and N. So the split the findings draw is free against mated, not put against turn, and J26's premise
   does not hold for the app's puts (point 4).

The rest are notes.

---

## Points

**1. Must fix (a sentence, not behaviour): after a turn the active mode holds in step, a quiet Update says all is
well, and the turn warning is not on screen.** `ui_text.py:3995-3998` (the quiet "It worked in …" sentence),
`ui_text.py:3325-3332` (*"The gears stand where they were turned in SolidWorks."*), `ui_text.py:2490`.

- *The path, run on the fake with the finding as committed (False), on both variants (scratch test):*
  - The 2H train is turned: RangeSlv, ModeSlv and InDog by 37°. 2H is in step.
  - Update pressed in 2H puts nothing and shows nothing.
  - Status: *"SolidWorks already matches the workbook: nothing was changed. The gears stand where they were turned in
    SolidWorks. It worked in 2H, the configuration that was active; it did not show the other modes, since nothing in
    2H needed changing."*, green.
  - With shared positions, 4L then stands with RangeSlv across LoDog. That is s2's own reading in 4L: 531.913 mm³ of
    interference, `…111951…log:113`.
- *Why the ruling's safeguard is not there.* The ruling relies on the record line's *"A turn you give the gears in one
  mode shows in every mode, … press Update SolidWorks with that mode showing …"*. But `workbook_footer` gives a job's
  note in place of the state's text when both are fine (`ui_text.py:2490`: `text, ok = note.text + …, note.ok`).
  The note is kept until the workbook next changes (UI-DESIGN §9, "kept until the file next changes"). A scratch call
  of `workbook_footer`, with this note and a modes record and `positions_per_configuration=False`, returns the note
  alone. The record line comes back only after the next edit.
- *What it is.* Every clause on screen is true, but this is the one path where a mode is left with a coupling out of
  step and the user is told all is well. The app has what it needs to say more without reading anything new: the
  finding (False) and the check phase's `result.turned` in the active mode (True here: it says *"The gears stand where
  they were turned"*). With a shared turn, a turn read in the active mode is a turn in every mode.
- *Change.* In `_mode_after`, add one sentence when all of these hold: `positions_per_configuration is False`,
  `result.turned`, the mode worked in was not put, and nothing was visited. Proposed, verbatim:

  > *"This version of SolidWorks shows that turn in every mode, so a dog may stand across its sleeve in another mode;
  > to put the gears back there, press Update SolidWorks with that mode showing."*

  - It claims only what the finding and the reading give. "May" is right: whether a given coupling is crossed
    depends on the turn against that coupling's pitch.
  - It is not said on True or None, nor after a put, since R1's visit then reads every mode.
  - Pin it in all three states of the switch, and in the window's quiet-Update test.
  - Ruling 9.18's last bullet (`W8-INTERFACES.md:351-354`) says *"the switch-False sentence above tells the user to
    press Update with the other mode showing"*. Amend that bullet: the sentence is not on screen after the press.

**2. Should fix: the shared-turn sentence, and "back at the turn", repeat once per coupling.** `ui_text.py:3970-3977`.

- The loop over `result.out_of_step` appends *"…; the gears of 4L are back at the turn they were built at."* and,
  when the switch is False, *"This version of SolidWorks shows a turn given in one mode in every mode, so the turn
  may have been given in another."* once per coupling pair.
- This code was there before these commits. Until R3, though, the False branch was unreachable on any committed
  version. It is now what 2026 says.
- s2's quiet Update in 4L found two couplings out of step: RangeSlv with LoDog and ModeSlv with FrontDog
  (`…111951…log:142`, `:189`). A scratch call with that result and the switch False returns both sentences twice:
  - *"In 4L, RangeSlv's teeth stood across LoDog's; the gears of 4L are back at the turn they were built at."*
  - *"This version of SolidWorks shows a turn given in one mode in every mode, so the turn may have been given in
    another."*
  - *"In 4L, ModeSlv's teeth stood across FrontDog's; the gears of 4L are back at the turn they were built at."*
  - *"This version of SolidWorks shows a turn …"* again.
- *Change.*
  - One sentence per crossed pair: *"In 4L, RangeSlv's teeth stood across LoDog's."*
  - Then once: *"…the gears of 4L are back at the turn they were built at."*
  - Then the shared-turn sentence once.
  - Or join the pairs: *"In 4L, RangeSlv's teeth stood across LoDog's and ModeSlv's across FrontDog's; the gears of
    4L are back at the turn they were built at."*
  - Pin the case with two pairs in each state of the switch.
- The s2 rerun will print this status, so fix it first.

**3. Should fix (tests): nothing run here shows what a build or an Update says with the committed value.**
`tests/test_swbuild.py:6060-6085` (`mode_findings` pins `TURN_PER_CONFIGURATION_ON_*` True).

- *Mutants, the whole suite run on each:*
  - `_modes_check` writing `result.positions_per_configuration = True` whatever the finding (`swbuild.py:4041`):
    `3130 passed, 10 skipped, 2 deselected`.
  - The build doing the same (`swbuild.py:2989`): the same result.
  - In other words, the app could go back to saying *"A turn you give the gears in one mode stays in that mode.
    Switching mode never by itself puts a dog tooth on tooth."* on 2026, and nothing run in this venv would notice.
- *What covers the value today.*
  - `test_findings` pins the constant, and the switch reads it (`test_findings.py:1107-1143`).
  - `ui_text` tests feed hand-made results with each state.
  - The window test added in `d7a3074` (`test_workbook_window.py:2581`) pins the build's footer with False. It is
    skipped here (no `tkinter`), and it monkeypatches False rather than reading the committed value.
  - Nothing covers an Update end to end.
- *Change.* Add two tests in `tests/test_swbuild.py`, which runs here, that put the committed value back over
  `mode_findings` (capture `findings.TURN_PER_CONFIGURATION_ON_2026` at module import, before any fixture, and set
  that back):
  - a build of the TC fixture on the fake (revision 34): `result.positions_per_configuration is False`, and
    `modes_done_line` holds `TURN_SHOWS_EVERYWHERE` and not `SWITCH_IN_STEP`;
  - a quiet Update on the shared variant after a put in 2H: the status lines in full, the shared-turn sentence and
    the visited-at-the-built-turn sentence included.

  My scratch tests of exactly these pass at HEAD. The second gives:

  > *"… In 2H, RangeSlv's teeth stood across InDog's; the gears of 2H are back at the turn they were built at. This
  > version of SolidWorks shows a turn given in one mode in every mode, so the turn may have been given in another.
  > The gears of 4H, N and 4L stood at the turn they were built at when Update SolidWorks showed them. It worked in
  > 2H, …"*

**4. Should fix (records): s2 also read a put of the mated train showing in every configuration. The findings and the
ruling draw the line between a put and a turn, where the evidence draws it between free and mated.**
`findings.py:1249-1263` and `:1265-1290`; `W8-INTERFACES.md:320-325`; the dated notes in `W8-PLAN.md` (§0.3 table,
§1.9) and `PLAN-WORKBOOK.md`.

- *What s2 read.*
  - The quiet Update in 4L, at `90a5571`, put the whole train with 4L showing:
    - locks and gear mates suppressed in 4L alone (`SetSuppression2(…, 0, ['4L'])`, `…111951…log:194`);
    - 13 `Transform2` puts (`:191`).
  - The changed Update that followed showed 2H first. 2H read **not turned** when shown, as did 4H, N and 4L:
    - `:437`: *"FAIL s2 changed Update: 2H alone found turned when shown: [('2H', False), ('4H', False), ('N', False),
      ('4L', False)]"*;
    - `:297-300`: every mode's `ModeCheck` has `turned False; out of step []`.
  - So a put made by the app's own route, on mated components, with 4L showing, showed in 2H, 4H and N, where
    those mates were on throughout.
- *What it means.*
  - The put fact (`POSITIONS_PER_CONFIGURATION`) was read on a component with **no** mates.
  - The turn finding was read on a mated train moved by the solver.
  - The app's put is a `Transform2` put, like the follow-up's, and it was shared like the turn. So "put against turn"
    is not the variable. At least "free against mated" is.
  - J26's premise, *"A put holds only in the configuration shown (2026)"*, does not hold for the app's puts on E4.
- *What does not change.* Behaviour: every put is to the built frame, so shared puts are redundant, not wrong (point
  6 below). `False` for the turn is still right. The evidence is stronger than the comment says.
- *Change.*
  - In `findings.py`'s turn block, add the `:437` / `:297-300` reading as a third observation. In the put block,
    narrow *"such a put holds in the active configuration only"* to a component no mate holds.
  - Say the same in ruling 9.18's first bullet and in the W8-PLAN J26 note.
  - Pin `:437`'s line in `test_a_turn_of_the_mated_train_…`.
  - s7 must measure the app's put route as a case of its own (below).
- *"The difference is the case, not the host or the revision"* (`findings.py:1282`).
  - Read narrowly, it is supported. Both cases were read on one host and revision (34.0.0), and they differ. The put
    case reads the same on 34.0.0 and 34.1.1 (`w8-followup-20261115-114828.*`, 34 of 34).
  - Nothing has read the mated turn on 34.1.1. The comment lists 34.1.1 under "Not covered", but the sentence can be
    read as saying more.
  - Suggest: *"On this host both cases were read and they differ, so the case, not the host, explains the two
    readings; the mated turn has not been read on 34.1.1."*

**5. Should fix (docstrings and a test name, stale after R1).**

- `swbuild.py:4144-4145`, `_modes_assembly`: *"With nothing to change, only the active mode is judged, from where it
  stands, and nothing is shown."* Add: unless it is put there, when every mode is then shown, as on a changed Update.
- `swbuild.py:4298`, `_modes_put`: *"(or, ``check`` None, the active one judged where it stands)"*. No caller passes
  None now.
- `swbuild.py:3208`, `GearboxUpdate.visited`: *"(none in a quiet Update)"*; `:3211-3212`, `put_in`: *"in the order put
  (the active one last)"*. After a quiet put, the active mode is **first** in `put_in`.
- `tests/test_swbuild.py:6501`: `test_a_train_turned_in_another_mode_is_left_unseen_by_a_quiet_update_which_says_so`.
  Its shared variant now sees the turn and visits every mode. The re-pin itself is exact (point 9 under "sound");
  only the name is stale.

**6. Should fix (length): the shared-turn sentence can say the same in 37 words instead of 50.** `ui_text.py:3551-3553`.

- `TURN_SHOWS_EVERYWHERE` is said in a build's status and in the footer's record line. Its last clause, *"since an
  Update pressed in another mode may leave them as they stand"*, repeats what *"with that mode showing"* already
  makes the condition.
- Proposed, verbatim:

  > *"A turn you give the gears in one mode shows in every mode, so a dog can stand across its sleeve in another mode;
  > to put the gears back there, press Update SolidWorks with that mode showing."*

  - It is true wherever it is reached (False only).
  - It drops no claim: the instruction stays and the guarantee stays unmade.
  - Re-pin `test_ui_text.py` (`test_the_turning_note_promises_only_what_an_update_does`), the window twin, the
    UI-DESIGN row and the ruling's verbatim quote.
- *"A dog can stand across its sleeve"* is what s2 measured: LoDog, the dog, in interference with RangeSlv, its
  sleeve, in 4L (`:113`). The Update's own sentence puts it the other way round, *"RangeSlv's teeth stood across
  LoDog's"*. Both describe the same thing.

**7. Note: the active mode can in principle be put twice.** `swbuild.py:4214-4231`.

- After a quiet put, the active mode is shown again last and judged again by `_modes_put` with `check=found_here`.
- If it read out of step again, three things would follow:
  - it would be put again, and `put_in` would hold it twice (*"re-placed … in 2H and 2H"*, from `ui_text._put_where`);
  - `found_here.out_of_step` would hold the pair twice, and so would the log's *"found in mode 2H"* line.
- On the evidence this cannot happen. Every put is to the built frame, which is in step in every mode, shared or
  not, so the second judgement finds nothing. Neither fake variant reaches it.
- If a guard is wanted: de-duplicate `put_in`, and extend `found_here` only on the first judgement.

**8. Note: sentence 1 with no configuration named has two "it"s with different subjects.** `ui_text.py:3965`.

- The sentence: *"It worked in the configuration that was active; it did not show the other modes, since nothing in
  it needed changing."*
- The first two "it"s are Update; the last is the configuration.
- Suggest *"…, since nothing there needed changing."*
- With a configuration named, *"since nothing in 4H needed changing"* is right, and true in all three states. It is
  reached only when nothing was moved or fixed and nothing was put in the mode worked in.

**9. Note: sentence 3 next to the shared-turn sentence.** `ui_text.py:3979-3988`.

- On the quiet path, the active mode is put **before** the others are shown. *"The gears of 4H, N and 4L stood at the
  turn they were built at when Update SolidWorks showed them"* is then the shared put's effect.
- It is read and true, but it follows *"This version … shows a turn given in one mode in every mode"*, and a reader
  may take it as contradicting that.
- The order-neutral *"when Update SolidWorks showed them"* is right for the changed path, where the others are shown
  first. I would keep it.
- If the wording is revisited, *"When Update SolidWorks then showed 4H, N and 4L, their gears stood at the turn they
  were built at."* is true on the quiet path only, so it would need the path passed in. Not worth it now.

**10. Note: on 2024 the app now says nothing about where a turn shows, and 2024 is the version the user runs daily.**
`findings.py:1290`.

- `None` follows the plan's rule: no claim while unsettled. It is better than before: `POSITIONS…_2024 = True` had the
  app claim *"stays in that mode"* and *"never … tooth on tooth"*, which GOTCHAS §83 says is false on 2024.
- End to end on the fake with revision (32, 5, 0) (scratch): the switch is None; the turning and switching notes are
  `""`; the Update's status carries neither the shared-turn sentence nor sentence 3.
- So on 2024 the hazard of point 1 has no warning anywhere, not even in the footer.
- If the user wants one before s7 on 2024, a sentence true in every state could stand for None:

  > *"Whether a turn given in one mode shows in the others has not been measured on this version of SolidWorks; to
  > be sure a mode's dogs sit in their sleeves, press Update SolidWorks with that mode showing."*

  That is the user's call. Running s7 on 2024 early settles it either way.

**11. Note: the demonstration script still expects positions per configuration.**
`probe/workbook_assembly_check.py:6461-6490`, `:6513`, `:6974-6979`.

- s2 measures 4H, N and 4L "as built" after the 2H turn: each is a STOP under the corrected finding.
- It expects the quiet Update in 4L to put nothing, with `result.positions_per_configuration is True`, `not
  result.visited` and `not result.modes`.
- It expects "2H alone found turned" at the changed Update.
- Its header logs `POSITIONS_PER_CONFIGURATION_ON_*`, the unread put fact, and labels the switch "positions per
  configuration here".
- The s2 rerun cannot pass until the script says what is now expected (below).

**12. Note: the cost of the visit.** A quiet Update that puts now costs about what a changed Update does. In s2, the
quiet press took 102.1 s (`:190`) and the changed one 197.4 s (`:294`), the extra being 4 shows, 69 rebuilds against 16,
and interference per mode. Worth one line to the user. J13 requires the visit.

**13. Note: what reads the turn finding.**

- `findings.py:1283-1284` says it is read for *"the sentences about a turn and a switch (ui_text.turning_note and
  switching_note)"*. `_mode_after` also reads it, for the shared-turn sentence and sentence 3 (`ui_text.py:3975`,
  `:3979`). Add those.
- The same holds for `swcom.positions_per_configuration`'s docstring.

**14. Note (pre-existing, outside these commits): "teeth stood across" for a pair 1° out of step with no
interference.**

- In s2's 4L, ModeSlv (+37°) and FrontDog (0°) are 1° out of step on a 12° pitch: residual 1.75e-02 rad (`:185`).
- Interference read only LoDog with RangeSlv (`:113`). Yet the status says *"In 4L, ModeSlv's teeth stood across
  FrontDog's"* (`:189`).
- "Out of step" is the true word here, and "across" claims more. For the user's list, not for this fix.

---

## The option not taken: judge every mode's couplings from the rotations read in the active mode

- *What it would be.* On a quiet Update with the switch False, for each other mode, `train_check` run on the frames
  already read in the active mode, against that mode's wanted frames and links (`links_in(…, mode)`), showing
  nothing. It would say which mode stands with which coupling across, for example: *"At this turn, in 4L, RangeSlv's
  teeth stand across LoDog's; press Update SolidWorks with 4L showing to put them back."*
- *Size.* About 30–50 lines in `_modes_assembly`'s quiet branch:
  - a field on `GearboxUpdate` (say `crossed_elsewhere: List[Tuple[str, str, str]]`);
  - a sentence in `_mode_after`;
  - tests on both fake variants and in all three states;
  - an amendment to J25 (*"No sentence claims more"*) and to §1.10, since this is the first sentence about a mode the
    Update did not show. No SolidWorks call.
- *What it rests on.*
  - The turn finding: one host, one revision (34.0.0), and solver-driven turns only. The drag is s6's.
  - The assumption that showing another configuration does not change the rotations. s2 supports it for gear-mated
    couplings: LoDog stayed 3.75° across in 4L, so a gear mate re-solved on a show does not snap phase.
- *What could go wrong.*
  1. Sliders. The active mode's frames hold its own slide positions. Judged against another mode's wanted frames,
     every slider whose place differs reads **off its axis**. The fake shows exactly this: judged without a re-solve,
     4L reads `off_axis ['RangeSlv', 'ModeSlv']` and no coupling out of step. A rotation-only judgement, with z taken
     from the mode's wanted frame, is needed, and `train_check` has no such mode today.
  2. A wrong finding (34.1.1, 2024, a drag) gives false alarms that name modes and couplings. That is worse than
     point 1's hedged sentence, which names none.
  3. Fixed and held gears, and carriers, judged off their own mode's frames.
  4. It cannot put. A put needs the mode shown (J26), and putting the active mode to undo a crossing elsewhere would
     undo a turn that is in step here (W5's answer 2).
- *My view.* Not now. Point 1's sentence gives the user the warning for a few lines, rests on what is measured, and
  makes no per-mode claim. Revisit the option after s7 and s6 on both versions, if the user wants the app to name the
  mode. Even then, judge rotation only.

---

## What the remaining SolidWorks sections must show

- **s2, rerun at HEAD under the corrected finding.** The script must first be changed as point 11 says. Then:
  - the read's and build-copy footer's turning sentence is `TURN_SHOWS_EVERYWHERE` and the switching sentence absent;
    the header logs `TURN_PER_CONFIGURATION_ON_*`;
  - after the 2H turn, 4H, N and 4L show every body turned as in 2H, and 4L shows LoDog in interference with
    RangeSlv. These are now expected readings, logged as facts, not STOPs;
  - the quiet Update in 4L:
    - finds RangeSlv with LoDog and ModeSlv with FrontDog out of step;
    - puts 4L, with locks and gear mates off in 4L alone;
    - then shows 2H, 4H and N and 4L last: `visited == ['2H', '4H', 'N']`, `put_in == ['4L']`;
    - each of 2H, 4H and N reads `turned False` and clean when shown. That repeats `:437` as an intended reading: the
      4L put showed in every configuration;
    - the post-check is clean in every mode, and `_modes_flags_after` reports no failure;
    - the raw flags afterwards are §2.3's;
    - the status carries the visited-at-the-built-turn sentence and the shared-turn sentence once (point 2);
    - log the elapsed time;
  - **new, the coordinator's case:** with 2H showing, turn the 2H train, then press Update in 2H.
    - It puts nothing and shows nothing.
    - The status as ruled, plus point 1's sentence once added.
    - Then the script shows 4L and reads LoDog across RangeSlv, logged as the residual hazard.
    - Then Update in 4L puts it right and visits.
  - the changed Update (At 130 → 132): every mode put, 4L last, every mode clean. "2H alone found turned" becomes
    "no mode found turned", since the quiet put already put every mode back.
- **s7, on the built E4, 2026 first, then 2024.** Each case read in every configuration through fresh handles, then
  saved, reopened and read again:
  - (a) a put of a component no mate holds. This is the follow-up's case on the E4. FIdler in N is not it, since its
    gear mates are on in every mode. Suppress FIdler's gear mates in every configuration first, or insert a free part;
  - (b) a put of a mated gear by the app's own route: locks and gear mates off in the shown configuration alone, the
    `Transform2` put, the mates restored. This is `:437`'s case, and the one J26 rests on;
  - (c) a turn of the mated train by W5's drive, s2's case;
  - (d) optionally, a put of a gear-mated component with its gear mates on (s7 as planned, FIdler in N): it separates
    "mated" from "mates off around the put".

  From these readings, set `TURN_PER_CONFIGURATION_ON_2024`, decide whether `POSITIONS_PER_CONFIGURATION_*` is
  narrowed or retired, and move the pins in `test_findings.py` to s7's file, as the comments promise.
- **s6, the person's step.** Its text expects *"the footer should say the gears stand where they were turned and that
  the other modes were not shown"* after an Update in 4L. Under the corrected finding, a drag in N may have put 4L out
  of step, and then the Update in 4L puts and visits. Reword s6 before it is handed over. Its answer is the only
  reading of a drag.

---

## What I checked and found sound

- **R3, the finding against its evidence.** Every clause of `findings.py:1265-1290` is in the two files:
  - 4H, N and 4L each list Sun, InDog, RangeSlv and ModeSlv at +37.000000°, each planet copy at −18.500000° and LoDog
    and the carrier at +9.250000°, off the frame on record (`…111951…log:68`, `:85`, `:102`);
  - the 531.913 mm³ clash (`:113`);
  - the check's two routes in all four configurations, the value route at 37/−18.5/9.25 and the global route at
    20/−10/5 (`w8-turn-across-configurations-…txt`, second attempt);
  - the front train absent from every "turned from the start" dict (the script prints only bodies that moved, from
    all of `box.components`);
  - 4L active on open;
  - the mate made where the Sun stood, moving nothing (*"moved 0.0e+00 on making"*).

  The first attempt's snap-back is kept and labelled. Route A cannot say whether the value was held per configuration
  (the mate was deleted before another configuration was shown), but it does show that a place solved in 2H is what
  the others show, which is the claim. `False` for 2026 is right on this evidence, and the "Not covered" line names
  34.1.1, the drag and 2024. The evidence files are committed.
- **The pins.** `test_a_turn_of_the_mated_train_…` reads the log and check file line by line, and asserts `False` and
  `None` (via `getattr(…, "missing")`, so a deleted constant fails too). Mutants caught:
  - `TURN…_2026 = True`;
  - `TURN…_2024 = False`;
  - `swcom` reading the put fact again (caught by `test_the_positions_switch_…[True-None-…]`, whose put findings are
    set the other way round).
- **Sentences only.** Every reader, checked:
  - `swcom.positions_per_configuration` is called at `swbuild.py:2989` and `:4041` only, and the results only carry
    it;
  - `ui_text` reads it in `turning_note`, `switching_note` and `_mode_after` (`:3975`, `:3979`);
  - `workbook_gui` stores it for the footer;
  - `POSITIONS_PER_CONFIGURATION_ON_*` is read by nothing in `src` (only the probe script's log header);
  - no branch of `swbuild` reads `result.positions_per_configuration`.
- **Behaviour with a shared turn: redundant, not unsafe, except point 1.**
  - Every put is to the built frame, which is in step in every mode, so the per-mode puts cannot leave two modes
    disagreeing.
  - A put with one mode showing, mates off in that configuration alone, did free the train and showed elsewhere. In
    s2, the 4L put ended *"no interference between the gears where they stand"* (`:189`), and every mode read at the
    built turn at the next Update (`:437`, `:297-300`).
  - s2's changed Update put every mode with per-configuration suppression. Every mode was clean (`:435-438`), the raw
    flags were §2.3's (`:488`), and every body stood at its wanted frame in every mode (for example `:494-496`). Its 7
    failures are the 3 "as built" frames, the 4L clash, the 2 quiet-Update expectations and "2H alone found turned",
    all from the per-configuration expectations.
  - The build makes each coupling at the built turn, which every configuration shares, so in step.
  - D10 and `_modes_flags_after` touch flags only.
  - A J14 edit is a changed Update: every mode is shown and judged by its own links, so a newly engaged coupling left
    out of step by a shared turn is put.
  - The coordinator's path (point 1) is the only one I found that leaves a coupling out of step under a status saying
    all is well.
- **R1.**
  - A quiet Update that puts nothing makes exactly the calls it made. `fake.calls` were logged on `e670e7e`'s tree
    against HEAD's, in four scenarios on both variants: identical, 83 calls each.
  - After a quiet put, the loop runs every other mode in mode order, put only where its own train needs it (`moved`
    stays False), each post-checked, with a `ModeCheck` on `result.modes` and its name on `visited`. Then the active
    mode is shown last and judged again, with its `ModeCheck` being the one that holds the pre-put judgement. Then
    `_modes_flags_after`. That is exactly the changed path's loop, on both variants.
  - The status, *"…no interference between the gears in any mode, where they stand. … It worked in 2H, the
    configuration that was active, then showed and checked 4H, N and 4L and left the assembly in 2H. Save …"*, is
    true clause by clause, and *"marked modified although nothing in it changed"* is rightly absent.
  - J13 (`W8-PLAN.md:146`: *"visits the other modes' configurations to post-check only after it changed something"*)
    and §1.10's post-check (`:638`: *"all of them when anything changed; none in a quiet Update"*) require the visit
    once a put changed something. Removing the old behaviour is justified as written.
  - The re-pin is exact and stricter: shown order, `visited`, every `ModeCheck`'s fields, the order of puts and
    shows, the configuration left, no failure, and the two sentences. The per-configuration variant gains "nothing
    put, rebuilt or set".
  - Mutants caught: R1 reverted; a fresh `ModeCheck` for the active mode.
- **R2's sentences**, in all three states of the switch:
  - "Since nothing in 4H needed changing" is true wherever it is reached (point 8 is style).
  - The shared-turn sentence is true: an Update pressed with the crossed mode showing judges it and puts it. It is in
    house style (whole sentence, the workbook's words, no check claimed), with point 6 on its length.
  - Sentence 3 is filtered to modes read clean and not put, and only when the mode worked in was put. It is pinned,
    including a turned mode excluded, a mode put excluded and the mode worked in not put.
  - Mutants caught: the old quiet words; sentence 3 said on None; the turned filter dropped; the put filter dropped.
- **Docs.** Ruling 9.18 says what was measured, what was ruled and what is left for the user. The dated notes leave
  the approved text alone and point at the ruling. The exceptions are point 4 (the put reading left out) and point 1
  (the claim that the footer warns after the press).

## What I could not check

- Anything on SolidWorks. I ran no Windows program: another agent is driving SolidWorks on this host.
- GOTCHAS §83 and `assemblies/07`. The SW-Macro-Database clone at `/home/m0obot/SW-Macro-Database` stops at §72 and
  has no `assemblies/07`, so "agrees with GOTCHAS §83" is taken from the plan's quotation of it.
- The window test of `d7a3074` and the design boards. They need `tkinter` or Chrome, and another agent owns them.
- Why s2's changed Update found FDrive off its axis in 2H and 4L only (`:247-248`, `:297`, `:300`) and still ended
  green, with every body later measured at its wanted frame. This is outside these commits and is left for the s2
  rerun to show again or not.

## Tests run

- `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_swbuild.py tests/test_swbuild_modes.py
  tests/test_workbook_modes.py tests/test_ui_text.py tests/test_findings.py tests/test_swcom.py`: `1 failed, 1272
  passed in 5.56s`. The failure is `tests/test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`,
  `ModuleNotFoundError` for `tkinter`.
- The whole suite: `2 failed, 3130 passed, 10 skipped in 43.05s`. Both failures are the known `tkinter` ones
  (`tests/test_gears_clutch.py::test_the_strip_never_offers_them`, the end-view readout above).
- Mutants, in a scratch copy of HEAD's `src` and `tests`:
  - caught (one failing test each, named above): `TURN…_2026 = True`; `TURN…_2024 = False`; `swcom` reading the put
    fact; R1 reverted; a fresh active `ModeCheck`; the old quiet words; sentence 3 on None; its turned filter dropped;
    its put filter dropped;
  - survived (point 3): the Update's switch hard-wired True, `3130 passed, 10 skipped, 2 deselected`; the build's,
    the same.
- Scratch tests against the fake, on `e670e7e` and HEAD:
  - call lists for four quiet scenarios on both variants;
  - the coordinator's path with the finding as committed (point 1);
  - a quiet put with the finding as committed, both variants (point 3's text);
  - two crossed couplings with the switch False (point 2);
  - the footer with a job note (point 1);
  - the 2024 None path end to end (point 10).
