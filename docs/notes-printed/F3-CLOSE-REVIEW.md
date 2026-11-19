# F3's close: review of the reruns' SolidWorks evidence

**Read at `f8c8bcd` on `printed`**:
- the runner's addition to the script, `c53d6c6`;
- the rerun's two logs and their JSON:
  - `probe/results/f3-demo-sw2026-20261119-4-built-userwork-clean.log` (`f3-demo-20261119-002811.json`);
  - `probe/results/sw2024/f3-demo-sw2024-20261119-3-built-clean.log` (`f3-demo-20261119-005450.json`);
- the rerun section of `docs/notes-printed/F3-DEMONSTRATION.md`;
- what was owed by `F3-DEMONSTRATION-RUNS-REVIEW.md` (`c641f3d`) §5, the fix `b668cf0` and its review
  (`SAVE-FLAG-FIX-REVIEW.md`), the plan's correction `741c3da`, and PLAN-PRINTED §4.6's *Done when*;
- for question 4, `git diff printed...f4 -- src` (f4 at `de9e795`, merge base `abdf450`).

No code was changed and SolidWorks was not run. Below, `26:` and `24:` are lines of the 2026 and 2024 rerun logs.

**Verdict.** The reruns are clean and say what the write-up says. The runner's addition is a real check and loosens
nothing. Every item §5 of the runs' review listed as owed for F3's SolidWorks evidence is now met. **F3 is done by its
*Done when*.** What is left is paperwork and the two items already known: the boards' PNG renders, which wait for the
Mac, and F3-0's hashed pins under Windows' `python.exe`. F4's merge touches no path that a SolidWorks build, Update or
export takes past the assessment that comes before them, so F3's SolidWorks evidence stands for the merged branch.

## 1. The reruns

**Provenance.**
- Both logs name the snapshot `c53d6c603a6a…` in their heads (26:3, 24:3), and so do both JSONs.
- `c53d6c6` holds `b668cf0`. Between `771f492` and `c53d6c6` the only commit under `src/` is `b668cf0`, and the
  only one under `probe/` is `c53d6c6`. So the note's *nothing else in the script moved since 771f492* holds.
- The revisions are 34.1.1 (26:5, PID 57896) and 32.5.0 (24:5, PID 49476). Each session opened with no document
  (`open before: []`).
- Both runs end `done 0 failed: []; 0 noted; 0 STOP(s)` (26:2730, 24:1879). Both JSONs have `fails []` and
  `stops []`.
- The `ok` counts by section are 95 for built on 2026, 47 for userwork on 2026 and 95 for built on 2024, as the note's
  table says. The section times are 407 s, 1059 s and 404 s (26:1871, 26:2724, 24:1873).

**The quiet Update values** (26:112-113 and 24:112-113, identical on both versions):
- The one job's status is *Nothing to update: every value in Coupon_F2.SLDPRT already matches the form.*, with
  `changed []` and `ok True`.
- `GetSaveFlag` of every document under the run folder reads `{'Coupon_F2.SLDPRT': False}` before and the same after.
  `flags_in` reads this from SolidWorks, not from the app.
- No SolidWorks file moved, and the `.gear.json` is the same.
- **The calls by member, 133 in all:** `ActiveDoc 3, Equation 60, GetCount 2, GetEquationMgr 2, GetPathName 1,
  GetTitle 1, GetType 1, GetUserPreferenceToggle 1, SetUserPreferenceToggle 2, Value 60`. The sum is 133.
  - Every member is a read except `SetUserPreferenceToggle`. That is `begin_build`'s and `end_build`'s
    dimension-dialog preference: an application setting, turned off and put back, not the part.
  - There is no `Add2`, no `Delete` and no put of `Equation`.
  - The 60 `Equation` and 60 `Value` reads are `equations()` read twice: once directly and once through
    `equation_values()`, as `b668cf0`'s `update_variables` now does before deciding.
- This is the fix shown live on both versions. Before `b668cf0` the same step turned the flag on (the runs' review §3,
  26-3:347, 24-2:760).

**Is `c53d6c6` a real check? Yes.**
- **The counting is wired where the calls go.**
  - F2's wrapper rebinds `swcom.call`, the module global that every `Session` method looks up at call time.
    `swbuild` does not import `call` by name.
  - `c53d6c6` rebinds `swcom._put_indexed` the same way, which `set_global_variable` reaches as a module global.
  - `detect_trig_units` reaches `Add2` (`_add_equation`) and `Delete` through `call`. A part's rebuild reaches
    `ForceRebuild3` or `EditRebuild3` through `call` too.
  - So on the code before the fix this check fails on `Add2` and `Delete`.
  - The added `bool(quiet_calls)` conjunct fails the check if the counting is not wired at all.
- **What is not counted, and why it does not matter here.**
  - `set_rebuild_suppressed` sets `CommandInProgress` by a plain attribute, and `_put` puts names. Neither is
    counted.
  - Neither is reached on the quiet path, which returns before `apply`. `CommandInProgress` is an application flag,
    not the document.
  - `CHANGING_CALLS` is a denylist. But the log prints the whole member list, and I read it above: there is nothing in
    it the denylist could have missed.
- **Nothing was loosened.**
  - The existing conjuncts are unchanged: `r.ok`, `not r.changed`, files, record and save flags. Two are added.
  - The check fails on more than it did before, never on less.
  - No tolerance moved, and the script makes no SolidWorks call new to the repo. The added wrapper only appends a name
    and then calls through.

**Everything else in built**, on both versions, at the lines the note cites (each read):
- G2's allowance is structural on F2's 12 : 1 (26:699, 24:697).
- G2 changes in place to 12 + 0.3, its hole 6.15 by its faces (26:1287, 24:1287).
- K11 names `"Bore Allowance"` and `Gears!V3` (26:1299, 24:1299).
- The machined 12 : 1 plans machined (26:1311, 24:1311).
- The machined 12 : 1's Backlash is written with no F3 global, and each `.gear.json` stays below schema 4 (26:1869,
  24:1871).

**userwork on SolidWorks 2026 with `771f492`'s check** (26:1872-2724):
- Sun changes in place to D 8, a 0.3, Flat 7.2, by its faces and links (26:2345). The user's keyway and eight mates are
  in no error (26:2347).
- The user's concentric is read on the 4.15 face by `mate_definition` (26:2351).
- SunGear keeps 0.3 as built (ruling 1, 26:2719).
- The carry's subjects are `('Sun', 'its Part name changed', 'face', '')` (26:2720).
- **The fixed check holds** (26:2721): UserBoreMate is the only mate named, as `part new`. The eight are remade:
  UserAngle4, UserAxis1, UserAxis2, UserAxis4, UserDist4, UserLock1, UserLock2 and UserLock3.
- The CHECK lines of the app's own carry agree (`not carried: UserBoreMate (part new)`).
- This is the clean 2026 `userwork` the house rule owed. The section is now clean on both versions (2024 at
  `771f492`, 24-1:863-864 of the earlier run).

**The write-up against the logs.** Every line I followed says what the note says. One precision point: the note's
*Windows* paragraph says there was no notification box, which is true, but it does not mention the two SolidWorks
balloon tips the 2026 log records as facts:
- *Simplified Interface* (26:9);
- *The sketch is no longer over defined.* during `SketchAddConstraints` (26:202).

Both are exempt by the coordinator's ruling, as in runs 2 and 3. No What's Wrong box appears in either log. The 2024
JSON's `close_outlived` is `in_force`, and nothing in the log shows it acting. The statements about the masters'
hashes and the probe folder's listing are the runner's own, outside the logs, and are said as such.

## 2. What was owed, and F3's *Done when*

The runs' review §5 listed six items. Their state now:

1. **The save-flag ruling.** Ruled a fix. Fixed in `b668cf0`, reviewed in `SAVE-FLAG-FIX-REVIEW.md` (no must-fix),
   and `built` rerun clean on both versions with the stricter check. **Met.**
2. **2026 `userwork` at `771f492` or later.** Run from `c53d6c6`, clean (§1). **Met.**
3. **The plan's record.** `741c3da`:
   - corrects the re-solve sentence and the 0.035 mm line to K2 (both are in §6, at what the review called §2.8's
     lines);
   - says §4.4's "bore" is never said live;
   - records the pre-F3 fix in *Changes after F3's demonstration runs*.

   **Met**, but for one line: the record does not yet say that the reruns closed F3. §4 also has no *Closed* line like
   §3's. That belongs with item 6.
4. **The pins under Windows.** Ruled expected for now: the note says the self-check's pins check alone fails under
   `python.exe`. The later commit that makes the hashed pins hold under Windows Python as well as Linux is **still
   owed** (known). The self-check's line 9 still does not say that it is Linux-only. Either that commit or a word in the
   line settles it.
5. **The boards' PNG renders.** **Owed** (the Mac's Chrome; known).
6. **The hand-over notes** (HANDOFF and the plan's §4 head). **Owed.**

**PLAN-PRINTED §4.6's *Done when*, item by item:**
- F3-0's pins and interface reviewed: in (`F3-0-REVIEW.md`).
- The packages and the suite: in (`F3-REVIEW.md`). The fix review ran the suite at `b668cf0`: 5395 passed,
  1 skipped, and only the known font-width test failed. I did not rerun the suite, since this task changed no code.
- Every demonstration section is clean on 2026 and on 2024:
  - `dshape`, `allowance`, `print` and `hub`: clean on both in the first runs (the runs' review §1);
  - `built`: clean on both now;
  - `userwork`: clean on both now.

  That covers each named sub-item: within 0.1 % of the twin, fully defined, the hole to 0.01 mm, the structural
  refusals, the hub turning with no interference, and a gearbox built before F3 unchanged in its bore.
- README, boards (the HTML) and `design/UI-DESIGN.md`: in. The PNG renders are outside the item as the stages have
  read it (F1 and F2 closed with the renders waiting too).
- The stage and the runs reviewed, should-fixes done: yes, with this review.

**F3 is done by its *Done when*.** Still owed, none of it evidence: the hand-over and the plan's *Closed* line, the PNG
renders, and the pins under Windows' `python.exe`.

**One open ruling, not F3's:** the `_evaluates` edge `SAVE-FLAG-FIX-REVIEW.md` §5 put to the coordinator. A document
can be left marked when its values evaluate in one unit only and the job then stops. It is rare, older than F3, and
should be noted or fixed.

## 3. Caveats for the handoff: what stays unmeasured

- **The fix's setting path has not been run on SolidWorks since `b668cf0`.** No section of the rerun runs an Update
  values that sets something:
  - `built`'s typed allowance is refused before any job;
  - `dshape`'s value steps ran before the fix.

  The fix's review found that the changing calls and their order are unchanged on every setting path: 71 calls logged
  identically on the fake. The reads it adds are ones the workbook's Update has made live since W4. Its suggestion to
  show an `Add2` counted before the first put was not taken up. A small risk, not a gap in F3.
- The carry's `COAXIAL_FACE_READ` on a D's partial cylinder (never read live, and by W9d's M1 never read for a non-gear
  mate).
- K2 over a user mate on a D face: read once, 2026 run 2, under the old check.
- K11's blank-cell words (*the allowance as built*) live: only a typed cell was met.
- K3 with a user feature in the bore.
- A D on a helical gear, its angle at the section plane.
- A D printed and fitted on a shaft, and the allowance's figure from the user's coupons (V1).
- A What's Wrong box outliving a job on 2026, and either memory floor's STOP.
- **The demonstration under Windows' `python.exe`**: F3-0's pins are bit-exact on Linux only until the later commit.

## 4. Does the F3 evidence stand once F4 is merged?

**Yes.** `git diff printed...f4 -- src` touches eight files:
- `gears/strength.py` and `workbook/strength.py`, both new;
- `gui.py`, `ui_text.py`, `workbook/checks.py`, `export.py`, `model.py` and `schema.py`.

**What it does not touch.** It changes nothing in `swcom.py`, `swbuild.py`, `printout.py`, `workbook/gearbox.py`,
`update.py`, `build.py`, `link.py` or `workbook_gui.py`. No module on a SolidWorks path imports `strength`: only
the six files above name it. `ui_text.py` gains lines and loses none.

**What a build or Update meets first.** `workbook/checks.check` now calls `_check_strength`. `check` runs in
`assess.assess`, the Linux-side assessment that comes before every workbook Build and Update. What it adds:
- `report.strength`;
- warnings (`_warning`) at Meshes rows of a printed gearbox whose first input has a torque, never an error;
- nothing for a machined gearbox, or for one with no torque.

It runs before SolidWorks is reached and changes nothing sent to it.
- `gears/strength.rate` catches its own faults.
- `mesh_strengths` has no guard of its own. An exception there would stop the assessment, before any SolidWorks call.
- `F4-REVIEW.md` checked it over every fixture and mode with no mismatch.

That is a merge-time consideration for F4's review, not a change to what F3's runs measured.

**The Box.**
- `Box` gains `allowable`, and there is a new *Allowable stress* row after Nozzle. It is read by its label, and a
  workbook without the row reads `""`.
- An error is raised only at that Box cell, for a typed figure that is not above zero.
- No gear spec, record, `.gear.json` or plan sees it. The one `spec == job.spec` on a build path
  (`gearbox.py:480`) compares gear specs, not the Box.
- No schema number moves.

**Export.** `export.results_sheet` appends the Results block when `report.strength` is non-empty. That is written to
the `.xlsx` by `xlsx.write_cells` after the workbook's fixes. It is file I/O, not SolidWorks, and not STEP export.

**The form.** `gui.py` changes only the Derived panel: the Holds once row and its layout, caught in `_rating_of`. The
strip's Update values, Build and Print files are untouched.

**The merge itself.** `git merge-tree --write-tree printed f4` reports no conflict, and `b668cf0`'s `swbuild.py`
survives unchanged.

**One thing to know.** F4 adds warning sentences to a printed gearbox with a torque, so diagnostics lists on such a
workbook gain lines. The F3 demonstration's word-for-word comparisons are made within one run under one code, so they
hold. But the demonstration has not been run on the merged tree, and this review does not claim it would pass
unchanged: its log is evidence for `c53d6c6`, and for the merged branch only through this reading of the diff.
F4-REVIEW reports every W9 and F1 to F3 pin holding on `f4` on Linux.
