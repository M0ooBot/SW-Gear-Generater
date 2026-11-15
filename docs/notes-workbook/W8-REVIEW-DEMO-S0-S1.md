# W8 review of the demonstration's first part, s0 and s1 (independent, read-only)

**Verdict: run it after two should-fixes; nothing in it gives a wrong verdict on a right assembly, and its answer
key is right number for number.** Its job handles meet §1.8's rule everywhere: every job opens the assembly, shows its
mode and rebuilds before it finds a component, and no component handle is held across a show. Its flag reads all go
through the app's per-name reader. None of its controls can pass because a read failed, since an interference read
that fails raises rather than answering empty. Every clause of §5 for s0 and s1 has a check.

What is wrong is where some checks take their expectations from, and what happens around them:

- the driven proof and several STOP-weight reads judge SolidWorks against the app's own numbers (its kinematics, its
  record). §2.3's key is held against those numbers only by FAIL-weight checks elsewhere;
- configuration N has no positive interference control;
- on SolidWorks 2024, s1.master would be saved with 4L active;
- three of §0.5's STOP triggers are not STOP lines, and a STOP does not keep s1.master from later sections.

**What was reviewed.** `4d9ce4b` (the W8 sections, `drive_job`'s per-mode route) and `497d89f` (a refused build ends
the section), in `probe/workbook_assembly_check.py`. Line numbers are at HEAD (`b296c7f`), where the file is as
`497d89f` left it. I read the W8 part whole, and of the old part `drive_job`, `input_sense`, `close_turn`,
`expected_frames`, `mesh_residuals`, `drive_assumptions`, `in_assembly`, `close_ours`, `open_titles`, `end_clean`,
`keep_master`, `build_turning`, `carrier_part_check`, `DialogWatch` and `main`. Of `swcom` I read `mate_suppression`,
`set_mate_suppressed_in`, `dimension_values`, `set_dimension_in`, `component_frame`, `interferences`, `_component`,
`show_configuration`, `link_dimension` and `_add_equation`.

**How it was checked.** I worked §2.3 again from §2's tables by hand, then ran the script's own pure functions on the
two fixtures through the app's read and plan, in the Linux venv. The harness imports the script with `win32*`,
`xlhelp` and `workbook_gui` stubbed, and lives in my scratchpad, outside the repo. The functions run were
`expect_modes_read` and `check_modes_plan`, which passed on both fixtures with no false FAIL, `mesh_controls` and
`coupling_controls` with the put stubbed (to list which gear each control turns, with which locks, against which
partners), and `drive_assumptions`. I also compared the record's one frame with the first mode's in the plan: they
are exactly equal, so `check_modes_record`'s `== 0.0` test cannot fail on rounding. No SolidWorks, no Excel, no
Windows program.

---

## Should fix

**S1. Configuration N has no positive interference control, so N's "no interference" can pass vacuously.**
(should fix; lines 5665–5668, 5614–5625)
- In N no coupling is engaged, so all three dog controls are "clashes with nothing" (I listed them: InDog, LoDog and
  FrontDog, each with its lock suppressed, partners empty, on both fixtures).
- The mesh controls run in the first mode only, which is 2H.
- So in N every interference reading passes if `interferences()` answers empty in that configuration: the per-mode
  "no interference" (a STOP), the three disengaged controls and the drive's interference at 120. Nothing in N shows
  that the read can see a clash.
- 2H, 4H and 4L each have an engaged dog whose clash is required, so the gap is N's alone.
- *Change:* run `mesh_controls` in every mode, or at least one mesh control in every mode with no engaged coupling.
  FIdler is the natural choice: it turns with no lock suppressed and must clash with FDrive and FOut on both
  fixtures.

**S2. On SolidWorks 2024, s1.master would be saved with 4L active.** (should fix; must be fixed before the 2024
confirming run; lines 5884, 5950, 3828–3829)
- `reopen_modes` ends with `measure_modes(..., controls=False)`, which shows 2H, 4H, N and 4L in turn. Each show
  marks the assembly, so 4L is left active and the assembly modified.
- `section_s1` then calls `keep_master` → `end_clean`. On 2024 (`TAG["major"] == 32`), `end_clean` saves every
  modified document of the folder before `quit_in`. So the master is saved in 4L.
- That contradicts the record. `GearboxRecord.modes[0]` and every component's one frame are "the configuration the
  assembly was saved in" (W8-INTERFACES §5, §9 ruling 9).
- It also contradicts s6's person step ("It opens in 2H") and the reopen check that s2–s7 inherit through
  `copy_built`: "reads the copy's state as a reopened gearbox".
- On 2026 `quit_in` closes without saving, so the master stays as `reopen_modes` saved it, in 2H. s0's folder is
  saved in 4L by `close_ours` on both versions, but nothing reuses it.
- *Change:* end `reopen_modes`, and so `modes_built`, with the first mode shown and the train rebuilt, as
  `reopen_modes` already does before its own save. Or measure the first mode last.

**S3. The driven proof judges SolidWorks against the app's kinematics, not §2.3's key.** (should fix; lines
5197–5204, 5727, 5732, 5782)
- `mode_expected` takes every body's δ, and the set of free bodies, from `ModeReport.motion.speeds`, which is the
  app's own result.
- §2.3's 30° row is held against those speeds only in `expect_modes_read`, by `check` (FAIL weight), before the
  build.
- So if the read ever disagrees with the key, every STOP-weight turn assertion of the drive judges SolidWorks against
  the wrong numbers. A shaft that the app wrongly leaves free (for example FrontDrv in 4H) has its turn only NOTEd,
  never judged. The both-Flips "right" test (line 5782) inherits both the numbers and the free set.
- Today the read agrees with the key on both fixtures (I ran it), so this does not change a verdict now. It is the
  "expectation from the app" pattern §5 rules out ("the script's, never the app's").
- *Change:* `expected[g] = sense · (step / 30) · w8_turns(desk, mode)[body_shaft(desk, g)]`, with `free` the bodies
  whose shaft maps to None. Log the app's numbers beside them.

**S4. The live flags, slide values and per-mode suppression are compared with the record the app wrote, not with
the key.** (should fix; lines 5412–5426, 5483, 5503, 5841, 5849–5850, 5698)
- `modes_unshown` (flags and values, both STOP), `judge_mode_frames` (the slider's value, STOP), `measure_mode` (the
  off set, `off_in(box, …)`, STOP), and the drive's hygiene (`off == off_in`, and `flags_after` against
  `flags_wanted`, STOP) all build their expectation from `box.mates[*].modes` and `.values`.
- The record is held to §2.3 only in `check_modes_record`, by `check`.
- The chain is transitive, so it is not vacuous: a wrong record still FAILs once. But then the STOP lines pass, and
  §0.5's "a configuration whose suppression does not read back as planned" is judged against the app's plan rather
  than the plan's.
- The same applies to the both-Flips spec's `"same": int(entry.sense) == -1` (line 5698). W8-INTERFACES §9 ruling 3
  pins SPLINE sense −1 and COUPLE −σ_S·σ_D, which is −1 for these Z+ shafts. So `same` is True for both controls,
  from the key.
- The record's spline sense is never checked: `check_modes_record` checks each coupling's sense, but not the
  spline's. If the record held 0, the app's read would be handed `same` False, call the wrong Flip right, and halt
  the run on a false STOP.
- *Change:* compare against `W8_COUPLES`, `W8_SLIDES` and `W8_ALWAYS` directly (the record's mate names already
  equal the key's, by `check_modes_record`). Set `same = True` from the key. Add the spline's ratio and sense −1 to
  `check_modes_record`.

**S5. Three of §0.5's STOP triggers end as a plain FAIL, or as nothing.** (should fix; lines 510, 5899–5902; the
section wrapper in `main`, 6089)
- *A modal dialog from a configuration call.* `DialogWatch` only logs `DIALOG`. Nothing reaches `STOPS`, and nothing
  reaches `FAILS` unless the blocked call later times out.
- *A frame reading None* (a held handle). `component_frame` raises "SolidWorks gave no frame for …". The section then
  ends with "section s1 raised SolidWorksError", which is a FAIL but is not listed with the STOPs.
- *A coupling or spline that reads wrong both ways round.* The build refuses, and `modes_built` raises its
  AssertionError (a FAIL); it is not marked as a STOP.
- *Change:* append any DIALOG that is neither a progress box, nor a box dismissed under `DISMISS`, nor CAM's save
  question to `STOPS`. In `main`'s handler, add a STOP line when the exception text is "gave no frame". In the
  refused branch, add one when a `mate_problems` sentence says a gear mate reads wrong both ways.

**S6. A STOP does not keep s1.master from the sections that copy it.** (should fix before s2 is written; lines
5917–5950, 5107–5129)
- The header and `stop_check`'s docstring say "nothing is built on it".
- But `s_blocked` reads only `W8_MASTER["failed"]`, which is set only when `modes_built` raises. A STOP-weight
  failure, such as wrong flags, a slider off its place, a dog not caught, or interference in a mode, goes on to
  `keep_master`, and s2–s7 will copy that master.
- This is latent until s2 exists. W7's p1 keeps its master on a FAIL too, but §0.5 names these as STOPs.
- *Change:* in `section_s1`, take `len(STOPS)` before `modes_built`. If it grew, set `W8_MASTER["failed"]` (and keep
  the folder for the log, not as a master).

## Notes

**N1. The drive's fallback route is right in its units and its hygiene. It has never run; what a first run should
watch.** (lines 1578–1590, 1619–1627, 1683–1706)
- *Units.* `set_dimension_in(handle, value_mm, …)` sends `value_mm / 1000` to `SetSystemValue3`, so
  `math.radians(value) · 1000` arrives as radians, SolidWorks' system unit for an angle. The read-back
  (`GetSystemValue3` × 1000 against the value, to `VALUE_TOLERANCE_MM` 1e-6) compares the same scaled radians, which
  is 1e-9 rad. This is right.
- *The switch.* Only `link_dimension`'s SolidWorksError switches routes. That covers both of `_add_equation`'s
  refusals: Add2 −1, and "holds X where Y was added". `drop_drive_equations` then removes every equation quoting
  `"Drive"`, the global included, and `made["global"]` goes False, so the cleanup does not delete twice.
- *The hygiene.* The angle value is set back in the mode before any control mate is deleted. The angle mate is
  deleted. The checks after are frames, equations equal to before, the mates as before, and every flag in every
  configuration. The checks are the same as on the global route. This is complete.
- *What the first run should watch:*
  - the `route` fact line in every mode;
  - that `SetSystemValue3` answers 0 on an angle mate's D1 (`_slide_dimension` takes the first display dimension,
    which the spike only read on a distance mate);
  - that a per-configuration set on the *active* configuration moves the input after the train rebuild (the spike
    moved slides after a show and rebuild);
  - that the input turns +30.000000° (the value route has no measured sense of its own; `input_sense` halts on −30
    or on 60°, which is what an angle read as its supplement would give).
- *What has no fallback.* A refusal of `add_global_variable` itself has none. It ends in the "90° drive could not be
  added" Halt; the spike's global add was accepted with several configurations.
- The angle mate, made with a mode shown, probably comes out on in every other configuration too. The spike saw a new
  mate suppressed only in the template's configuration, which the build deletes. It is at 90° everywhere, so this is
  harmless, and `reopen_modes` reads every mode's frames afterwards anyway.

**N2. The read-order fault cannot show in the script's own reads.** (lines 5390–5398)
- Once the build deletes Default, the document's configuration order is 2H, 4H, N, 4L. That is exactly the order
  `box.modes` asks in.
- So a multi-name `IsSuppressed2` or `GetSystemValue3` would pair right here whichever order it answers in. The
  build's own read-back, made while Default still exists, is what exercises `03a4e51` on the run.
- A second read in reversed order, required to give the same answers, would make s0 and s1 show it independently.
  It is cheap, and optional.

**N3. A suppression call that fails its read-back can leave a mate suppressed.** (lines 5543–5563, 1651–1655)
- `put_in_mode` turns back on only the locks in `held`. `drive_job` sets `made["suppressed"]` only after
  `set_mate_suppressed_in` returns.
- `set_mate_suppressed_in` raises when its read-back disagrees. Normally that means the call did not take, so there
  is nothing to undo. But a raise from the read-back itself leaves the state unknown, and the mate is then never
  turned back on.
- The later no-lock check (FAIL) and `flags_after` (STOP) would report it. Before that, `close_ours` saves the
  assembly with the lock still suppressed, and on 2026 that is the save s1.master keeps.
- *Change:* mark before the call, and in the cleanup turn on every lock that was found.

**N4. §5's "put back, the locks turned on again, none" is read in a different order.** (lines 5553–5565)
- The interference read after the put-back comes before the locks are turned on again. After the locks, only frames
  are read.
- Since every frame is then held to its frame on record to 1e-6, this is equivalent. An `interferences()` after the
  restore rebuild would match the letter of §5.

**N5. §2.3 numbers, and one §2.2 sentence, that the script does not hold.**
- The torque table, the five phases (InDog 0, RangeSlv 6°, LoDog 0, FrontDog 0, ModeSlv 6°) and W5's ALONG globals
  are not asserted. The phases are proved physically instead, by the sleeves over their dogs reading no interference
  and by each dog's half pitch being caught. I checked all three groups against the app's read; they agree:
  - Parallel: Lay 19.6, Lo 38.416, Rear 38.416 in 4L; Rear 10 in 2H and 4H; In only in N.
  - Phases mod 12°: LoDog reads +12°, which is 0 mod 12°.
- The Checks panel is logged, not held. W6's and W7's `expect_read` held it exactly.
- §2.2's sentence on warnings does not match the app's read. It says each sleeve and dog gets the form-diameter
  warning and each sleeve also the tips-inside-base warning. The read gives:
  - *TransferCase_Parallel, 9 warnings:* form diameter on the three dogs and on LayGear, LoGear, FDrive and FOut; the
    two sleeves get tips-inside-base only.
  - *E4, 7 warnings:* form diameter on the dogs and on FDrive and FOut; tips-inside-base on the sleeves.
- The plan's sentence wants correcting before anyone holds the panel to it.

**N6. On the author's readings.**
- *W5's and W7's mesh controls in the first mode only: right.* §5's enumerated list asks only for the coupling
  controls; the "§4.1 of W5-PLAN per configuration" is a pointer to that list. Every mode's frames are held to 1e-6
  against frames that place the meshes identically, so the meshes' phase holds in every mode without a control. The
  one cost is S1.
- *A control on every dog in every mode: right.* §5's own last sentence asks for it: "A disengaged dog shows no
  clash". Its weakness, no positive control in N, is S1.
- *Interference with the drive at 120 in every mode: right,* and at FAIL weight, which is right too. §0.5 names only
  the built turn. At 120 every coupling and mesh is in step by construction, so a clash there would also show as a
  turn off its kinematics, which is already a STOP.
- *Which Flip a recorded coupling or spline holds, logged as a fact and not asserted: right.* W8-INTERFACES §9
  ruling 15 has the spline needing Flip True on 2024 and False on 2026, and W5-DECISIONS rules that no Flip is
  predicted. The recorded mate's correctness is proved by every body's driven turn, independently of its Flip. The
  fact line's "Flip {made_with}" assumes the build first makes a gear mate with `findings.GEAR_MATE_FLIP`. That is
  worth confirming, or the line could mislead, but it judges nothing.
- *The drive: the global link first, the angle mate's own value if refused: right, with a ruling to record.* §5
  says "a global Drive". The fallback moves the same D1 in the mode shown, and everything is judged on measured
  frames: the input's turn must be ±30° with DEMONSTRATION_DRIVE_SENSE's sign, or the run halts. So the route cannot
  change a verdict. If it fires, the W8 notes should say §5's drive ran by the value route. Units and hygiene: N1.

---

## §5 for s0 and s1, clause by clause

"Does" means a check exists at the weight shown; "differently" says how it departs; "no" means no check.

| §5 clause | Script | Where |
|---|---|---|
| Through the app's own code (plan → `build_gearbox` → `finish_build`), every footer sentence logged | does | `Desk`, `build_turning` |
| Excel driven by the script's own; logs with no user titles | does (`open_titles` anonymises; new lines log only this run's titles) | `write_fixture`, 5873 |
| A dialog watcher throughout | does, but a dialog is only logged, never a STOP (S5) | `main`, `DialogWatch` |
| `s0`, `s1`; `--only modes` | does (s2–s7 left for later, by design) | 286, 293 |
| Handle rule: handles fetched again by name after every configuration change | does: every job opens, shows, rebuilds, then finds; mates are re-walked by name at each use | 5440, 5538, 1601–1609 |
| Every selection by full name | does through `swcom`; `delete_mate` (old) uses `Select2` on a mate feature walked fresh, not `SelectByID2` | 1170 |
| Build each fixture once | does | 5926–5950 |
| The active name read back | does (STOP) | 5410, 5467 |
| Unshown: every mate's flag in every configuration, against the record | does (STOP), expectation from the record (S4) | 5393–5415 |
| Unshown: every slide's value in every configuration, against the record | does (STOP), from the record (S4); none 0 checked | 5396–5426 |
| Shown: the train rebuilt, handles fetched again | does (rebuild answer checked) | 5440–5446, 5469 |
| Each slider at its value to 1e-6 mm | does (STOP), value from the record (S4) | 5479–5487 |
| Every other gear at its frame on record for that configuration | does (STOP); record against the read at FAIL | 5473–5478 |
| Every mate that is on reads code 0 | does (FAIL) | 5514 |
| Every per-mode mate that is off reads suppressed | does (STOP); also every other mate reads on | 5511 |
| Every mated gear `GetConstrainedStatus` 2 | does | 5516 |
| The layout and every fixed gear `IsFixed` through a fresh handle | does (STOP) | 5519 |
| Interference none | does (STOP); no positive control in N (S1) | 5521–5523 |
| Half pitch: the dog put 6° about its own axis, coupling on | does (pitch/2 of the read's placed dog = 6°) | 5582–5585 |
| … every lock touching the dog suppressed in this configuration around the put | does (read back by `set_mate_suppressed_in`) | 5543–5548, 5622 |
| … interferes with its sleeve only | does (STOP; exactly that pair, nothing else) | 5595–5598 |
| … put back, locks on again, none | differently: read before the locks are back; frames after (N4) | 5553–5565, 5603 |
| … every frame against its frame on record to 1e-6 | does | 5608 |
| … no lock left suppressed | does, in every configuration, through the per-name reader | 5566, 5605 |
| Each mode's control made and undone with that mode shown; the other modes read afterwards | does (frames of every mode after every control) | 5669–5673 |
| A disengaged dog shows no clash | does (every dog, every mode) | 5599–5601 |
| No control on a sliding mesh | n/a (none in either fixture) | — |
| Saved, closed, reopened; opens in the first mode | does (STOP) | 5867–5881 |
| Every document unmodified straight after the open | does | 5876–5878 |
| The flags, values and frames the same | does (against the record, and with mates, constrained status, fixed state and interference per mode) | 5884 |
| Driven proof: the script's own; W5's angle mate on the input's anchor, global "Drive" 90 → 120 | differently when the link is refused: the angle mate's value in the mode (N1, N6) | 1613–1627 |
| Every gear's turn about its own axis (`turn_between`), sleeves and dogs included | does | 5730 |
| … against §2.3's 30° row to 1e-6 relative, sign included | differently: against the app's kinematics, held to the key only before the build (S3); sign measured and ruled by DEMONSTRATION_DRIVE_SENSE | 5727–5738 |
| A free gear must not turn; more than 1e-6 is a NOTE | does; a free gear off its axis is a FAIL | 5739–5743 |
| Both Flips in 4L on `RangeSlv engages LoDog`, in 4H on the spline | does | 5174, 5911 |
| … the recorded mate suppressed in that configuration | does | 1651–1653 |
| … Flip False and Flip True, each read, logged, driven, every gear read, deleted | does (order set by `findings.GEAR_MATE_FLIP`, which does not matter) | 1659–1677 |
| … exactly one right, the read-back naming it; otherwise FAIL and STOP | does (STOP and Halt); "right" is every body right, "wrong" is the decided gear mirrored | 5794–5811 |
| … Drive set back before the control mate is deleted | does | 1674–1676 |
| … the recorded mate back on in that configuration only | does; "only" is proved by `flags_after` in every configuration | 1691–1698, 5847–5852 |
| … every frame at its built frame to 1e-6 | does (in the mode shown) | 5824–5832 |
| … no Drive global, angle mate or control mate left; no lock suppressed | does | 5833–5842 |
| … every flag in every configuration as recorded | does (STOP), expectation from the record (S4) | 5847–5852 |
| s1 kept as `s1.master` | does; kept even after a STOP (S6); on 2024 saved in 4L (S2) | 5950 |

**§5 clauses with no check:** none. Five are checked differently, as the table says:

- the drive's route when the link is refused;
- the drive's expectation source;
- the interference read after the locks are back;
- the flag, value and suppression expectations, which come from the record;
- the dialog watcher, which never raises a STOP.

One §0.5 trigger has no check at all: a modal dialog (S5).

## The answer key: recomputed beside the script's

Worked from §2.1 and §2.2's tables alone, then compared with the script's tables. **Every number agrees.**

| Item | Recomputed | Script | |
|---|---|---|---|
| RangeSlv: H, N, L offsets; z; front face | −10, 0, +10; 50, 60, 70; 46, 56, 66 | `W8_POSITIONS` H −10, N 0, L +10 | = |
| ModeSlv: 2WD, 4WD | 0, +10; z 100, 110; front 96, 106 | `W8_POSITIONS` 2WD 0, 4WD +10 | = |
| Spans (face 8) | Range 46–54, 46–54, 56–64, 66–74; Mode 96–104, 106–114, 96–104, 106–114 (2H, 4H, N, 4L) | `want_spans` = slide value to value + 8 | = |
| Slide values | `RangeSlv along Rear` 46, 46, 56, 66; `ModeSlv along Rear` 96, 106, 96, 106 | `W8_SLIDES` | = |
| Covers | H covers InDog 47–53; N clear by 3 each side; L covers LoDog 67–73; 2WD 3 short of FrontDog 107–113; 4WD covers it | `W8_ENGAGED` | = |
| Couplings on in | InDog: 2H, 4H; LoDog: 4L; FrontDog: 4H, 4L | `W8_COUPLES` | = |
| Always on | the two axes, the spline | `W8_ALWAYS` | = |
| Parallel low range, 30° row | In +30; Lay −30·17/34 = −15; Lo +15·17/34 = +7.5 | `W8_LOW` | = |
| E4 low range, 30° row | Carrier 30/(1 + 72/24) = +7.5; planet absolute 7.5 + (30 − 7.5)·(−24/24) = −15; Ring 0 | `W8_LOW` | = |
| 2H | Rear +30 (InDog → RangeSlv); front free | `W8_REAR_FRONT` | = |
| 4H | Rear +30; FrontDrv +30; Idler −30·30/20 = −45; Front +45·20/30 = +30 | `W8_REAR_FRONT` | = |
| N | Rear and front free | `W8_REAR_FRONT` | = |
| 4L | Rear +7.5; FrontDrv +7.5; Idler −11.25; Front +7.5 | `W8_REAR_FRONT` | = |
| Speeds | 50 × the row (1500 rpm ↔ 30°) | `want = 50 · t` | = |
| Ratio In : Rear | 1, 1, none, 4 | `W8_RATIOS` | = |
| Both-Flips controls | 4H the spline (ModeSlv decides); 4L `RangeSlv engages LoDog` (RangeSlv decides) | `W8_FLIP_CONTROLS` | = |
| Per-shaft map | RangeSlv, ModeSlv → Rear; InDog → In; LoDog → Lo / Carrier; FrontDog, FDrive → FrontDrv; FIdler → Idler; FOut → Front | `body_shaft` over the spec | = |

The fixtures in `tests/workbook_fixtures.py` match §2.1 and §2.2 row for row: the shafts, X and Y, the roles, the
gears' order, At, kind, teeth, module, face and slides, the meshes and the modes. The script's checks of the read
against this key ran clean on both fixtures through the app in the Linux venv, so the key will not FAIL a right read.

## What I could not check

- Anything on SolidWorks. In particular, whether a dog whose only lock is suppressed stays where it is put with just
  the coupling's gear mate on. The plan sanctions this, citing P0/P0b. For FrontDog, suppressing `FDrive locked to
  FrontDog` also leaves FDrive held only by its mesh, so it could move on the put's rebuild and add a clash that is
  not expected (a false STOP). The first run should watch FrontDog's controls.
- The value route of the drive (N1), and whether the global link is refused at all once the template's
  configuration is gone.
- `copy_built` and `keep_master`'s rename for a gearbox with configurations: tier 9 item 2, and later sections.
- That the build first makes a gear mate with `findings.GEAR_MATE_FLIP`, which the "Flip {made_with}" fact line
  assumes (N6).
- `mode_drive_proof`'s judging on real readings. I traced it by hand, and did not rerun the author's synthetic
  answers.
