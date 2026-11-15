# W8 review of probe tier 11 and its findings (independent, read-only)

**Verdict: two must fix, six should fix, four notes.** The probe is sound where it counts. The show into a fighting
configuration returned in 0.31 s, the rebuild in 0.08 s, and nothing the watch had to answer opened. Both slides read
47 with warning False. The app's own mate check, now running on the probe's assembly, named both slides. The
read-order verdicts come from the file's own reads. Three things are wrong or missing:

- One clause of the findings comment is not what the file shows: the balloon tip did not close after 0.79 s.
- The function that turns the file into the finding ignores half of what the finding claims.
- The app does not do what draft ruling (1) assumes. Update's refusal of a mate it did not make looks only at the
  active configuration, though J12 says every mode's configuration.

**What was reviewed.** These commits:

- `b296c7f`: `probe/p11_modes.py`, `tests/test_probe_modes.py`, and one import in `probe/__main__.py`.
- `2b530eb`: the rerun's two changes.
- `49a7787`: the result files `probe/results/w8-over-defined-20261115-100312.json` / `.txt` and
  `w8-over-defined-attempt-20261115-094752.txt`.
- `171175f`: `show_over_defined`.
- `a75c617`: `findings.py` lines 1322-1385 and `tests/test_findings.py` lines 1128-1182.

I judged them at HEAD (`a75c617`).

**How it was checked.**
- **The finding against the file.** I read each fight's reading in the JSON key by key: `slides.into`, `after`,
  `also`, `again`, `back`; `coupling_and_lock.*`; `read_order.*`; `watched_calls`; `closes`; `disk_*`. I checked
  each against each clause of the finding and its comment.
- **The first run.** I parsed the attempt file's `w8_over_defined` fact (it has no JSON) and compared it with the
  evidence run.
- **The derivation.** I ran `fight_reading` / `show_over_defined` on doctored copies of the JSON, outside the repo.
- **The app.** I read the build's per-mode check (`swbuild._set_up_modes`, `_mode_problems`) and Update's
  (`_modes_check`, the M7 loop at `swbuild.py:4511-4520`, `_modes_post_check`). I ran two scratch tests on the fake,
  outside the repo: a code 47 in one mode in a build, and in an Update with a mate the user made on in that mode only.
- **The order.** I checked every caller of `IsSuppressed2(3, …)` and `GetSystemValue3(3, …)` in the app.
- **Privacy.** I grepped the three result files for titles and paths.
- **Tests.** I ran the tests the brief named and the whole suite.

No SolidWorks, no Excel and no Windows program.

---

## Must fix

**M1. The balloon tip did not "close itself after 0.79 s". 0.79 s is where the watch stopped looking. The file shows
the balloon still standing seconds later, at the start of the next configuration's show.**

- *Evidence.*
  - **When it was seen.** `slides.into.rebuild.windows[0]`: `first_s` 0.26, `stood_s` 0.79. The rebuild took
    0.083 s (`watched_calls`), and `ModesWatch` watches 1.0 s after the call (`linger`). 0.26 + 0.79 = 1.05 s is the
    end of the watch, not the end of the balloon.
  - **Still standing after the watch.** `slides.into.standing_after` lists `swBalloonTip`. So does
    `slides.after.standing_before`. So do `standing_at_entry` of both "the other configuration after it:
    ShowConfiguration2(Y)" and "… ForceRebuild3(True) in Y". It is gone only by `slides.after.standing_after`.
  - **Its real lifetime.** It stood through every read after Z's rebuild and through Y's show plus its 1 s linger:
    at least about 2.3 s, and more by the length of the reads, which the file does not time. Whether it closed by
    itself or Y's show closed it is not told.
  - **The first run is the same.** In the attempt file the balloon's `stood_s` is 0.77 and it is in
    `slides.into.standing_after`.
  - **Where the wrong figure is written.** `findings.py:1343-1344` ("It closed itself after 0.79 s"). The same
    figure is in the messages of `49a7787` and `a75c617`, in `171175f`'s ("as the rebuild's Over Defined balloon tip
    did"), and in the summary the coordinator was given.
  - **Line 1351 overstates too.** "Z shown again read as the first time" leaves out that the second show and rebuild
    of Z put up no balloon (`slides.again.rebuild.windows == []`).
- *Why it matters.* The finding string itself still stands: the balloon is non-modal, and Y's show and rebuild ran
  while it stood. But draft ruling (3) would tell s5's watcher to expect a 0.79 s window during one rebuild. That
  watcher has to expect a window that outlives the call and stands at the next one.
- *What I would change.*
  1. **The comment.** Rewrite lines 1342-1344 to say what the file shows. The balloon was first seen 0.26 s into the
     rebuild. It was still standing after the reads that followed, and when Y's show and rebuild began. It was gone
     once Y's reads ended. Nothing answered it, and the calls went on while it stood. How long it lasted, and what
     closed it, are not told.
  2. **Line 1351.** Add "with no balloon".
  3. **The watch.** In `ModesWatch.report`, record whether each window was still visible when the watch ended (for
     example `open_at_exit`), so `stood_s` is never read as a lifetime again.

**M2. Update refuses a mate it did not make only when that mate is on in the active configuration. J12 and §1.10 say
"in any mode's configuration". A user's second slide, on in a mode that is not active, is the case ruling (1) is
about, and it goes straight through.**

- *Evidence.*
  - **The plan.** `W8-PLAN.md:145` (J12): "An unsuppressed mate not on record in any mode's configuration refuses the
    Update (W5 M7)". `W8-PLAN.md:593` (§1.10): "an unsuppressed mate not on record refuses (M7, read the same way)",
    that is, in every mode's configuration.
  - **The code.** `swbuild.py:4511-4520` reads `mate_states()`, which is this configuration's flag only
    (`IsSuppressed2(THIS_CONFIGURATION, …)`). A mate not on record that is suppressed here goes into
    `extra_mates`. `_modes_check` (`swbuild.py:3994`) reads flags only for `motion.mates`.
  - **On the fake** (scratch test, the `tc_built` fixture, both position variants):
    - *The setup.* A user mate `Distance3` is suppressed in 2H, 4H and 4L and on in N. A code 47 with warning False
      is reported on it and on `RangeSlv along Rear` while N is shown. 4L's slide is changed, so Update shows every
      mode.
    - *What happened.* Update showed 4H, N, 4L and 2H. The only failure was "In mode N, the mate RangeSlv along Rear
      is in error in SolidWorks."
    - *What it said about the culprit.* The log says "CHECK suppressed mates Gear Generator did not make, left as
      they are: Distance3". That is untrue in N. The mate actually at fault is never named.
  - **The cause.** `_modes_post_check` loops over `motion.mates` only (`swbuild.py:4332`). The build's
    `_mode_problems` flags every mate read.
- *Why it matters.* On real SolidWorks the user would also read "RangeSlv stands at … where this mode places it"
  (tier 11: S stood at 30 mm, neither slide's value). They would be told the recorded slide is at fault and that
  their own mate is suppressed. W8-PLAN §4.2's fallback sentence named exactly that mate ("the mate {Distance3} is on
  beside {RangeSlv along Rear}").
- *What I would change.*
  1. **The check.** In the check phase of an Update with modes, find each mate not on record (`find_mate`) and read
     its flag in every mode's configuration with `mate_suppression`. That is one `IsSuppressed2(3, [name])` per
     configuration, which marks nothing (the spike). No new probe is needed.
  2. **The refusal.** If the mate is on in any mode, refuse before anything is shown, as M7 does now, and name the
     mate and the configurations it is on in.
  3. **The CHECK line.** Keep it, but list only mates suppressed in every mode's configuration.
  4. **The test.** Add the fake test above, turned into a refusal.

---

## Should fix

**S1. `show_over_defined` decides "others solve after" from Y alone, where the sleeve did not have to move. It never
looks at X, and it would also say "no window asks" for a watch that had died.**

- *Evidence.*
  - **Only Y counts.** `fight_reading` (`p11_modes.py:149-169`) sets `other_clean` from `fight["after"]`, which is Y.
    `windows` and `windows_answered` cover `into`, `after`, `again` and `back`, but not `also`.
  - **Y proves little about solving.** In Z the sleeve stayed at 30 mm, Y's own value (`slides.into.S_z`), so Y
    reading "clean at 30" shows nothing re-solved. X is the configuration where S moved (30 to 15 mm), and it is not
    used.
  - **Doctored copies of the JSON** (scratch, outside the repo):

    | doctored copy | `show_over_defined` |
    |---|---|
    | X reads code 47, app sentence, S status 4 | still the finding |
    | a box the watch answered during X's show | still the finding |
    | the watch thread dead: `watch_error` set, no windows recorded | still the finding |
    | the app sentence names an unrelated mate | still the finding |
    | an unanswered box that stood 4.9 s during the show | still the finding |
    | a box answered during Z's show | None |
    | the show returned False | None |
    | Y's S at 31 mm | None |

  - **The pins.** `test_findings.py:1142` pins X only through `S_z == 15.0`. A file that read 47 in X with S at
    15 mm would pass. Nothing pins `watch_error`.
- *What I would change.*
  1. **`other_clean`.** Require both `after` and `also` to be clean, each in its own configuration.
  2. **The windows.** Count `also` in `windows` and `windows_answered`.
  3. **The watch.** Return None when any watched call of the fight has a `watch_error`. At present the watch's
     silence is read as "no window".
  4. **The app sentences.** Require each mate in error to be named by one of them.
  5. **The tests.** Pin X's codes and the absence of `watch_error` in `test_findings`. Add a doctored-reading case
     for each of the above to `test_probe_modes`.

**S2. The app depends on `VALUE_READ_ORDER` without reading it.**

- *Evidence.* `swcom.Session.dimension_values` (`swcom.py:3014-3031`) asks `GetSystemValue3(3, names)` with several
  names. It pairs the answers with the names in the order passed (`zip(configurations, values)`). Its callers are
  `_modes_check` (every mode's configuration), the build's step 4, and `set_dimension_in`'s read-back. Its gate,
  `_configuration_gate("SLIDE_VALUE_ROUTE", "SPECIFY_CONFIGURATIONS")`, does not include the new finding. The house
  rule is that the app depends only on what a committed finding says. `SUPPRESSION_READ_ORDER` has no consumer and
  needs none, because `mate_suppression` asks one name per call (`03a4e51`).
- *What I would change.* Either add `("VALUE_READ_ORDER", "the order passed")` to `dimension_values`' gate, with a
  fake test that another value refuses, or read one name per call as `mate_suppression` does.

**S3. Ruling (1) rests on `CONFIGURATION_SHOW_OVER_DEFINED`, but nothing in the app reads it.**

- *Evidence.*
  - **What the gates read.** `MODES_UPDATE_FINDINGS` (`swbuild.py:3889`) and `MODES_FINDINGS` (`swbuild.py:1989`)
    gate on `CONFIGURATION_SHOW_RAISES_DIALOG False`. That was measured on configurations that solve (the spike).
    W8-PLAN's table (line 1180) says "no — except into an over-defined configuration (§4.2)".
  - **Who reads the new finding.** No one does (grep).
  - **Where it would matter.** If 2024 or a later revision asks on such a show, nothing refuses.
- *What I would change.*
  1. **The gates.** Add `("CONFIGURATION_SHOW_OVER_DEFINED", "shown; no window asks; its mates read in error; others
     solve after")` to both tuples. The build's step 6 shows every mode, and would meet a fight that step 5 let
     through.
  2. **The fixture.** Pin it in `mode_findings`.
  3. **The comment.** Say it applies on 2024 unmeasured until the confirming run, as `SUPPRESSED_GEAR_MATE_SENSE_READ`
     does.

**S4. No committed test shows that a mate error in one mode reaches the user as "In mode N, the mate … is in error
in SolidWorks."**

- *Evidence.*
  - **The fake cannot set it.** `FakeSolidWorks.mate_codes` (`tests/test_swbuild.py:872`) applies in every
    configuration, and no test in `test_swbuild_modes.py`, `test_workbook_modes.py` or the modes tests of
    `test_swbuild.py` sets a code at all.
  - **The scratch tests.** With a wrapper that reports 47 / False only while N is shown:
    - The build's per-mode check gave exactly "In mode N, the mate RangeSlv along Rear is in error in SolidWorks.",
      and `saved == ""`.
    - Update gave the same sentence for the same mate and mode.
  - **So the path works on the fake**, but it is pinned nowhere.
- *What I would change.* Give the fake per-configuration codes, for example
  `mate_codes_in = {configuration: {name: (code, warning)}}`, and add the two tests: one build and one Update, both
  asserting the sentence and nothing saved.

**S5. Privacy: the three tier-11 result files carry the SolidWorks main window's title, which names the licence
edition on this machine.**

- *Evidence.*
  - **The title.** It is in `standing_at_start` of the JSON, and in the `.txt` and attempt fact lines. It comes from
    `standing(pid)` describing every window at start, the main frame included.
  - **New to these files.** Only these three of the committed result files contain it.
  - **The account folder.** The Windows account folder in the scratch paths (`meta.argv`, `scratch`) is already in
    161 committed result files, so it is not new here.
- *What I would change.*
  1. **The probe.** Leave windows present at the start out of the facts. Record only that they were there, by class.
  2. **The committed files.** Ask the user whether to redact the title in the three files before more agents copy
     from them.

**S6. The first run's NOTE, and "Both runs read the same" in the findings comment, leave out two differences, and
the NOTE names the wrong mates.**

- *Evidence.*
  - **A window in the first run's show of Z.** The watch saw two windows open: `swWelcomeScreen` at 0.78 s and
    `SysShadow` at 1.05 s. Nothing answered them, and they stayed standing (`slides.into` / `after` / `also` /
    `again` `standing_after`). The evidence run's show saw none.
  - **Its likely cause** is the fresh session's own Welcome dialog arriving late, not the show. It neither blocked a
    call nor asked anything. But the NOTE says "Everything else read the same in both runs: the show into the
    two-slide configuration …", and `findings.py:1353` says "Both runs read the same".
  - **The wrong mates.** The NOTE says the lock alone left "codes 46, warning True, on D's axis and along mates and
    S's slide". The attempt file's `coupling_and_lock["Y with the lock alone"].errors_on` reads otherwise:
    - `Coincident3` code 1, warning True. That is S's axis mate, which the first run had not yet renamed.
    - `Distance2` code 46 (D's along mate).
    - `S slide` code 46.

    `findings.py:1359-1362` has this right.
- *What I would change.*
  1. **The NOTE.** Correct the lock sentence. Add that the first run's show of Z saw the Welcome screen open, not
     answered and asking nothing, and the rerun saw none.
  2. **The comment.** Change line 1353 to say the same.

---

## Notes

**N1. The read order: what the reads tell apart.**

- *The active configuration.* At all three moments of tier 11, Y was active (`read_order.*.active`). Y is also last
  in the document's order. So tier 11 alone cannot tell "the document's order" from "the active configuration
  last". The s0 file can. With 2H active and second, it read `['N', '2H'] -> (False, True)`, and
  `test_findings.py:1181` pins that line.
- *Default and X.* Their flags are equal in every pattern read, so their relative position is not told.
- *Creation order.* It is the same as `GetConfigurationNames`' order in both files.
- *What I would change.* Say all this in the comment at `findings.py:1377`. Nothing else, since no reader depends on
  the flag order.
- *What is sound.* The judging (`read_order`, `order_of` returns None on any "neither"). There are 18 distinguishing
  flag reads and 12 value reads over four mates, and single-name truths equal what was set.

**N2. The second slide's value was never read back.** `slides["second's value set"]` keeps only SetSystemValue3's
answers (0 each). The read-order reads cover the first slide only. "20 against 25" rests on AddMate5's 25 and the set
call. The finding does not depend on it, but `findings.py:1339` should say "set to 25 mm".

**N3. The balloon came once per run.** There was none on "into the fight again", and in the first run none on the
lock's over-defined rebuild either. A watcher must not require it.

**N4. `app_mate_states` reads warning True for every code-0 mate, where the probe's raw read gives False.** That is
`Session.mate_states` by design (`warning=bool(warning) if code else True`), not a fault. I note it because someone
reading the JSON side by side will trip on it.

---

## The three draft rulings

**(1) No refusal before showing, for fighting slides: agreed on the dialog question, not yet as worded.**

- *What the file supports.* On 2026 (34.0.0) with options as installed, nothing modal opened. The show returned in
  0.31 s and the rebuild in 0.08 s. Anything that blocked would have held the call until the watch answered it, at
  5 s at the earliest. The balloon is non-modal, and calls ran while it stood.
- *What the code does.* The build's step 6 (`_mode_problems`) and Update's `_modes_post_check` both turn 47 with
  warning False on a recorded mate into "In mode N, the mate … is in error in SolidWorks." (fake, S4). On SolidWorks,
  the sleeve's frame sentence would come too.
- *What it needs first.*
  - M2: J12's per-configuration M7, so the user's mate is refused and named before anything is shown. Without it the
    culprit is never named.
  - S3: the reliance read from the finding.
  - S4: the sentence pinned.
- *What stays open.* 2024 (W5: every such mate reads 51 there; the app treats any non-zero code as an error, so the
  sentence would still come), and the "show errors every rebuild" option.

**(2) A coupling beside a lock as a caveat, no pre-check: agreed.**

- *No path of the app makes the pair.* `workbook/motion.py` `_with_modes` (lines 600-627) puts couplings through a
  union-find per mode, and leaves off any coupling that joins two bodies already joined there. A LOCK only joins
  gears of one shaft, which is one body. The build only makes the ops the plan gives.
- *D10 per configuration* only turns recorded mates on and off. It could turn a user's quiet arrangement (their own
  lock across a coupled pair, with the recorded coupling, slide and axis mate off in one mode) into an over-defined
  mode, by turning the recorded mates back on. Tier 11's first run shows how: lock status 5; codes 46 and 1 on
  recorded mates. That would be caught by the post-check reading recorded mates, but with the user's lock unnamed.
  That gap is M2's: with M2 fixed, the user's lock refuses the Update first.
- *The frames and flags* hold either way.

**(3) s5 may run, with the watcher told to expect the balloon "during that one rebuild": not as worded.**

- *s5 never shows an over-defined configuration.* With the doctored distance mate in N's ops, the build makes it in
  step 5 while N is shown, beside N's slide. The refusal the plan expects, "In mode N, … over-defines the assembly.",
  is `_status_sentence` on AddMate5's status 5. `_set_up_modes` then returns before step 6 ever shows N. So the
  plan's note "The build shows N to check it" (`W8-PLAN.md`, the s5 bullet) is wrong.
- *Where the balloon would come is unmeasured.* It could come at the make (rebuild held by `CommandInProgress`), when
  `CommandInProgress` is released, at the close, or not at all. One data point: the first run's over-defining AddMate5
  (the lock, status 5) opened no window, and its rebuild put up no balloon.
- *The balloon outlives the call* (M1), and it may not come at all (N3).
- *What to tell the watcher.* Tolerate a `swBalloonTip` whose children read "Over Defined" / "The assembly is over
  defined…" at any call from the make to the close. It may be present or absent, and may stand any length of time.
  Never answer it. Any other window is a STOP.
- *The doctored distance.* Give it a value other than N's own slide value, as tier 11's 25 against 20. A redundant
  pair with equal values is unmeasured, and tier 11's redundant pair (the coupling beside the lock) read no error.
- *When.* s5 can run once M1 is corrected.

---

## Checked and found sound

- **Handles.** Fetched again (`_w8_refresh`) after every show, before `_state`, and after each AddConfiguration2.
  Mates are found by name from the tree on every read.
- **Flags before each show.** Every flag change is read back one name per call (`_single_flag`), and every `took` is
  True in the file. The fight is real:
  - Both slides read on in Z by IsSuppressed2 in that configuration (`slides.into.this_configuration`).
  - The second slide reads suppressed in Default, X and Y (single-name reads), and in Y and X when they are shown.
  - The first slide reads 20 mm in Z (single-name GetSystemValue3).
- **The lock and the coupling.** In Y the lock holds S alone, with the slide and axis mate read suppressed there. The
  coupling was turned on from X and read back. Y was shown with the lock and coupling on.
- **Nothing saved.** The assembly was never saved. The part mtimes are identical before and after (`saved_nothing`
  True). All four documents were closed by `CloseDoc` under the watch with no window (`closes[*].dialog` False), and
  nothing was standing at the end. `watched_close` refuses titles the probe did not create.
- **The rerun's change.** `px.session._worker._session` is the real `swcom.Session` (`probe/__main__.py:177-188`).
  Setting `_build_doc` makes `Session._doc()` (`swcom.py:1090`) read the probe's assembly. The two reads ran the
  app's real `mate_states` and `swbuild._mate_problems` on the worker thread, and the old value is restored in a
  `finally`.
- **The watch's coverage.** It polls every 0.25 s for any visible top-level window of the SolidWorks process,
  whatever its class. It answers only after 5 s, and watches 1 s after each call returns. A modal box would have
  blocked the call and been seen and answered. No `watch_error` in any of the 28 watched calls.
- **Revisions.** The findings comment says 34.0.0 for both runs and 34.1.1 for the spike and W5-W7.
  `test_findings` asserts `meta.version == "SolidWorks 2026 (revision 34.0.0)"`.
- **The read-order pins** derive from the file (`order_of` over every read). They would fail if it said otherwise.

## Could not check

- Anything on SolidWorks: no run, by the brief.
- How long the balloon stood, or what closed it: the file does not time the reads between watches.
- Whether AddMate5 under `CommandInProgress` gives status 5 for a second distance mate, or raises the balloon.
- 2024; a saved and reopened assembly; a fight among gear mates; the "show errors every rebuild" option; what an
  over-defined show marks. All are unmeasured, as the comment says.
- The attempt run's full JSON (not committed): I read its fact line in the `.txt` only.

## Tests

```
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_findings.py tests/test_probe_modes.py tests/test_probe_planetary.py tests/test_probe_harness.py
129 passed in 0.53s

PYTHONPATH=src .venv/bin/python -m pytest -q
FAILED tests/test_gears_clutch.py::test_the_strip_never_offers_them - ModuleN...
FAILED tests/test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights
2 failed, 3087 passed, 10 skipped in 42.85s
```

The two failures are the known `No module named 'tkinter'` in this Linux venv.
