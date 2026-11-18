# Review of W9d's demonstration script (M9), and of package A's second fix round

*Independent, 2026-11-17.*

- **Reviewed:**
  - `probe/w9d_demonstration.py` and `docs/notes-workbook/W9D-DEMONSTRATION.md` at `7d3a49e`;
  - package A's commits `4a9bae5` and `177aae8`.
- **Read beside them:**
  - `ISSUE-1-PLAN.md` §0.3, §4 M9 and §5 W9d;
  - `W9D-INTERFACES.md` §3, §5, §6, §15 and §17.1 at `d3bb9e7`;
  - `probe/w9c_demonstration.py`, `w9b_demonstration.py` (`judge_every`) and `w9c_probes.py` (`raw_mate`,
    `part_faces_of`, `select_face`);
  - the window's `_start_build`.
- **No SolidWorks or Excel was started.** Nothing was changed but this file. Package B's uncommitted wording round
  is left alone; the code reviewed is what is committed.

**Scratch work** (scratchpad, clean `git archive` extracts):
- the suite at HEAD (`9a21c6d`);
- package A's N1, N2 and N3 each undone in a copy, with the carry tests run against each;
- a flipped 2026 boolean finding;
- the script's `--self-check`.

**Verdict.**

- **May it run on SolidWorks 2026? Yes, once two must-fixes in the script are in.** Neither is in package A or B.
  - **M1:** a guard so RangeBox_r2 is never saved with a lightweight component, and a ruling on what the press does
    when carrying SprocketLight resolves the old assembly's lightweight instance.
  - **M2:** remade mates compared on their entities, against the script's own read of the old mates.
- **What holds:**
  - Everything runs on copies.
  - Each write the script itself makes is under W9a's dialog watch.
  - The STOPs are wired to raise before any proposal can come out clean.
  - The `propose` lines rest mostly on the script's own reads.
- **The weak spots are the "unchanged" evidence and the definitions.** Two kinds of evidence there are weaker than
  the note says. The trace sees fewer write members than it lists. The definition check never looks at which entity a
  remade mate is on.
- **Package A's second round is in.** It adds one new should-fix (the M3 blame), and the N1 test does not pin its
  fix.
- **Package B:** nothing must change. The question need not name UserSunFace (see 2 below).
- **The contract:** two rulings are owed (R.2's stored paths and D10's spread). Neither blocks the 2026 run.

**Suite at HEAD (clean extract):** 2 failed, 3880 passed, 10 skipped. The two are the known tkinter-only tests
(`test_gears_clutch.py::test_the_strip_never_offers_them`, `test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`).
None is in A's or B's files.

---

## 1. Package A's second round (`4a9bae5`, `177aae8`)

| Re-check item | At HEAD | Its test, with the fix undone in scratch |
|---|---|---|
| N1, a tie blamed on the wrong cluster | **Fixed.** A tie is re-judged only where a cluster's flags differ from its made mode. One cluster's fallback never stops the carry; the post-check's gear check does. My reproduction (`test_review_tie_blame.py`) passes at HEAD and fails with the fix undone. | **The new test does not pin it.** `test_a_cluster_on_in_every_mode_is_not_blamed_…` still passes with the fix undone. Its guilty cluster (Lock1) is added before the innocent one, so it is judged first and the bug never shows. Put the innocent cluster's mate first, as my reproduction does. |
| N2, judged where a component is suppressed | **Fixed.** That mode is skipped and what reads there is kept in `CarryResult.facts`. | Yes: fails with the fix undone. |
| N3, walks while nothing can be carried | **Fixed.** No r3 walk while `CARRY_INSERTS` is None. **Ruled further:** no not-open read at all then. | Yes: each half fails with its fix undone. |
| M3, the app's own mates per mode | **In:** `_app_mates_check`. **New should-fix** below. | Has a test. |
| The findings pin | **Fixed.** Every boolean is compared with its log line. | Verified: `COAXIAL_FACE_READ_ON_2026 = False` now fails it. |
| The 1e-6 prefilter; `walks`, `facts`, `changed_files`; the `finally` that shows the first mode; the -1 out code; `ComError` re-raised; a retry that cannot be read back or deleted named "left" | All in as described. B words "left" (`ui_text.py:5167`). | |

**New should-fix: `_app_mates_check` (`swbuild.py`, after `_carry_post_check`) blames any cluster.**
- *What it does:* when an app mate reads a new error in a mode, it falls back the first cluster that is not fallen,
  has a mate to an app body on in that mode, and has its components resolved there. It does so whether or not that
  cluster touches the erring mate's bodies. It repeats until the error clears.
- *The fault:* innocent clusters are fixed and named `FELL_NEW_ERROR` for another's error. This is N1's pattern
  again (reasoned, not reproduced).
- *M9's fixture is unlikely to meet it:* its tie falls back in its made mode, before the post-check.
- *Fix:* blame only clusters whose app handles are on the erring mate's bodies or train.

---

## 2. The plan's Done-when and §15

**The Done-when, item by item:**

| Done-when item | How the script checks it |
|---|---|
| r2 made after Sun's Flank change and a shaft added | The edit typed through `C9.edit_live`, then `classify` holds it to Build again… for Flank **and** Aux. |
| Both clusters carried, mates made again, on in their modes | Every mate's outcome against `expected_outcome`; the script's own every-mode flag read. `CLUSTER_ONE` and `CLUSTER_TWO` are defined but never used. The clusters are covered only through the per-mate outcomes, which is enough. |
| The bore mate on Sun named | UserSunFace on Sun's end face, `part new`, and the result must name it (`"UserSunFace" in status`). |
| The keyway named in the question and the result | Both checked. |
| Every app gear free in every mode | The script's own `GetConstrainedStatus` per mode, with the held Ring excluded through `box.fixed`. |
| Carried items unsaved | The script's own `GetSaveFlag` of RangeBox_r2, beside `CarryResult.unsaved`. |
| Old assembly and every user file unchanged on disk | SHA-256 fingerprints of the old assembly and all five user files. |

**The question and UserSunFace: not a miss.** The Done-when reads *"the bore mate on Sun named, the keyway in Sun
named in the question and the result"*. "In the question and the result" belongs to the keyway. The bore mate must be
named, and the result names it, which the script checks. §9.1's example names Concentric5 in the question, but §9.1 is
an example, not the Done-when. B's grouping is a choice the review of B accepted. Nothing for B to fix.

**The departures from §15:**

- **Face mates on Chain-2, joined to cluster one through Chain-1 — sound.**
  - Why: §15's bore concentric to Input Axis repeats Chain-1's axis coincident, and the face coincident repeats the
    distance to Sprocket-1. Both are redundant constraints. SolidWorks may or may not flag those; avoiding them is the
    careful choice.
  - The Done-when's "chain on Sun" is still Chain-1, and Chain-2 joins cluster one through UserFaceCoin (user–user).
  - I checked every other mate of the fixture for over-definition:
    - Housing-2's coincident, distance and parallel leave Y free and are redundant only in rotations already
      consistent;
    - UserAsm6 fixes Sprocket-6 axially while its rotation follows Sun through UserGear6;
    - UserLimit10 bounds two axially free sprockets;
    - each gear mate couples a sprocket that is free about its own axis;
    - the parallel mate is fully redundant but consistent.

    I found none that over-defines. The fixture's own check that every mate reads code 0 in H will say if SolidWorks
    disagrees.
- **The assembly-plane mate on Sprocket-6, not Housing-2 — sound.** Housing-2's Front plane is already held to the
  layout's.
- **SprocketLight and SprocketConf as files of their own — sound and necessary.** Lightweight spreads to every instance
  of a file (`w9d…-1.log:121`), and a configuration belongs to the file. M1 below follows from the first.
- **UserAsm6 judged `unread` in `carry`, made again only in `carry-closed` — sound.** The worker reads the root never
  beside a lightweight component. The assembly's own plane then reads as the root component's entity, which comes out
  unread. §15 puts the lightweight component in `carry`, so this is where the worker's rule lands; the Done-when does
  not need it.
- **No sub-assembly — sound.** That is what my first review asked.

**One contract point the fixture will expose: a fixed component anchored to a gear.** Housing-1 is **fixed** in the
old assembly. Through UserLock8b (user–user) it is in Sprocket-8's cluster, whose anchor is Sun (UserLock8a). So by D20
the user's fixed housing is placed against Sun.
- Where Sun's old frame differs from the new one, the housing turns about Sun's axis in the world. The same holds for
  Sprocket-4, which is placed against Sun through cluster one while its angle mate holds it to the layout.
- In any mode where Sun's frame differs from the first mode's, the fixed Housing-1 reads off its pose against Sun. Both
  `moved` and `poses_judged` would then fail, and `CARRY_INSERTS` would not be proposed.
- This is inferred. Whether Sun's frame differs is unknown until read.
- *Before the run:* the script should log Sun's old frame against the new one, and each mode's Sun frame. The contract
  (D20) should say whether a fixed component, or one held to the layout, is anchored to the world.

---

## 3. The seven places to look hardest

1. **The fixture's picks and raw mates.**
   - The picks are the probes' own routes:
     - `part_faces_of`: a plane's z from `PlaneParams[5]`, kept only when its normal is along Z;
     - the bore by its radius of 5 mm;
     - "root" as Sun's least coaxial radius (16.375 mm, `-2.log:92`) and "fillet" as its least off-axis one (0.475 mm,
       beside the keyway's 1.5 mm).
   - "low" and "high" take the least and greatest planar z of each part, as the W9d probe did, with the same
     assumption about end faces.
   - `raw_mate`'s limit distance passes (20, 30, 10) mm as `AddMate5`'s distance and its two limits. Whether that
     makes a **limit** mate rather than a plain distance is unmeasured in this repo. If it does not, "limit distance"
     simply never comes out clean. No over-definition found (see 2).
2. **The `ReferencedConfiguration` put.**
   - It is a documented get/set member, put once in each mode and read back per mode by the script.
   - It runs in a watched job, on the copy.
   - A failure is said, and the configuration item is then not shown. Sound.
   - The part's second configuration is made by the app's `add_configuration` on a **part**. That member is measured
     on assemblies only; it is low risk, watched, and on a copy.
3. **`expected_outcome` and `expected_states` against the worker's real rules.** Right on most counts:
   - UserSunFace on 2026: `part new`. The Sprocket-5 entity is tier 1 by r3, and Sun's face is a face of a part made
     new. If Sprocket-5's walk fails, the mate becomes `unread`, which is correctly a failure of r3.
   - The D2 path (2024): Sprocket-9 takes H's suppressed state in every mode, `_cluster_mode` finds no mode, and
     UserAxis9 is `unread`.
   - UserGearFillet is never taken as Gear Axis. UserGearRoot is taken as Gear Axis on 2026.
   - UserAsm6 is `unread` with a lightweight component present, since the root is not read.
   - UserLock8a falls back; UserLock8b, being user–user, is kept.

   **One false FAIL:** when Sprocket-9 (open path) or Sprocket-7 (closed path) is named `no frame`, which the script
   accepts, its mate is named "component not carried". The expectation still says `remade` there (or `unread` on
   D2's path). It is only a CHECK line, but it would read as a fault. Allow "component not carried" for those mates
   whenever their component is named `no frame`.
4. **`trace_problems` sees fewer writes than it lists.**
   - The trace is the wrapped `swcom.call`, but several writes the worker makes do not go through `call`:
     - `EditDelete`: `delete_mate` and `delete_component` reach it by `_guarded`;
     - `FixComponent` and `UnfixComponent`: invoked on the document directly;
     - the `Transform2` put and a mate's `Name` put: by `_put`;
     - a mate feature's `SetSuppression2`: through `call`, but not in the list.
   - So `EditDelete` is in `WRITES` but can never appear. A fix, unfix, move, rename or flag write on the old assembly
     would not be in the trace.
   - Leaving out the component-level `SetSuppression2` is right. Its `_target` would be the component's own file,
     falsely a user file.
   - On the open path these writes fall to `old_diff` and the GetSaveFlag bracket. But in `carry` the old assembly is
     already marked by the user's lightweight set, so the bracket is blind to it there. `old_diff` compares frames,
     mates' codes, flags and components, states, the mode showing and the rebuild state. It does not compare:
     - fixed or floating;
     - a mate's values (a changed distance);
     - SprocketConf-1's referenced configuration.
   - *Fix (should):* add `IsFixed`, each user mate's definition values, and the referenced configuration to
     `old_read`. Say in the note which writes the trace cannot see.
   - `_target` takes `QuitDoc`, `CloseDoc` and `ActivateDoc3` by their **title** argument, which may lack the
     extension under Windows' setting. The old assembly's name would then not match. Compare stems.
5. **`poses_judged`, `CarryResult.anchors` and the gear check.**
   - Poses are read by the script on both sides. The anchors are the worker's own (`cr.anchors`), so the check
     confirms the worker's choice of anchor, not D20. The script asserts only Sprocket-2 against RangeSlv (closed).
     *Should:* state the fixture's expected anchors (Sprocket-1 and -3 and cluster one: Sun; Sprocket-2: RangeSlv;
     Sprocket-8: Sun; Housing-2: the world) and hold `anchors` to them.
   - **A carried component whose frame does not read is silently skipped.** `rel` returns None and the pair is
     dropped; the check needs only one gap anywhere. *Should:* require a frame for every carried component in every
     mode where it is resolved.
   - The gear check is sound: the script's own status per mode, excluding the app's fixed gears (`box.fixed`). The
     Aux gear is included and should read free.
6. **`DeskD.build` is a copy of the window's `_start_build`.** It matches the code line for line today:
   `old_assembly`, `carry_for` in a `try`, `kwargs["carry"]`, the journal, and `job.revision` in the job. It is not the
   window's own method, so it can drift. W9a's and W9c's `Desk9` share the same pattern and risk. *Should:* a
   self-check line comparing the two (for instance that `_start_build`'s source still holds `carry_for(` and
   `kwargs["carry"]`).
7. **W9b's `judge_every` with the Aux gear.**
   - Aux is one more gear on record: it is in `W.bodies(box)`, has record frames per mode, and is not fixed. Nothing
     in `judge_every` assumes every gear meshes: bands and dogs concern RangeSlv's train, and "free" excludes only
     fixed gears.
   - I expect it copes. It is not exercised by anything offline.
   - Aux at x 80 with a tip radius of about 13.75 mm should clear the Ring. An app–app clash with it would show there
     as W9b's failure.

---

## 4. Could it report clean while the app is wrong, or STOP falsely?

**Each `propose` line, and what it really rests on:**

- **`CARRY_INSERTS`**
  - Rests on: `components`, `states`, `poses`, `unsaved`, `fallback`, `same_error` and `free`.
  - `states` is the **worker's own** `cr.states`. The script's every-mode read records frames and status but never
    `GetSuppression2`. *Should:* read each carried component's state per mode itself and compare.
  - `outcome`, `definitions` and `flags_read` are not among its conditions. Each is checked, but a failure there still
    lets the gate be proposed. Add `outcome` at least.
  - The STOPs (old assembly changed, file changed, trace) raise before the `finally`, so they leave `clean` empty and
    every proposal None. That is right.
- **`CARRY_REMAKE_KINDS` — must-fix M2.** It rests on `kinds_clean` over the outcomes and `definition_problems`.
  - `definition_problems` compares type, alignment, flipped and values, but **never the entities**. A mate remade on
    the wrong face, the wrong axis or the wrong component reads equal.
  - The old side is `cr.work.mates`: the worker's **own** read of the old assembly, not the script's.
  - Both sides go through `Session.mate_definition`, so a misread common to them both passes.
  - *Fix:*
    - read the old mates' definitions with the script's own `definitions_in` on the old assembly, before the press,
      inside the flag bracket;
    - compare each entity: its component mapped old→new (`cr.inserted`, the bodies' Name2s), its kind and its feature
      name;
    - for a face or an edge, at least the component and the kind, and a plane's z or a cylinder's radius through
      `part_faces_of` where it can.
- **`CARRY_REMAKE_KINDS`, the gear mates (should).** `definition_problems` compares `Reverse` as a value. A gear
  mate's sense is `Reverse` together with the two entities' directions (`gear_sense`).
  - UserGearRoot goes from a face to Sun's Gear Axis, so its direction may change and `Reverse` with it while the
    sense stays right. That would leave "gear" out of the kinds for no fault.
  - *Fix:* keep `EntityParams` in `definitions_in`, and compare `gear_sense` instead of `Reverse`.
  - Flags per mode (`flags_read`) should also count against a kind.
- **`CARRY_INSERTS_IN_A_CONFIGURATION`:** the script's own `ReferencedConfiguration` read per mode. Independent.
- **`REFERENCED_CONFIGURATION_READ`:** R's read held to Z20 beside a different active configuration. It fails (None) if
  SolidWorks reports the part document's active configuration as Z20, which is the right outcome.
- **`CARRY_GEAR_MATE_ON_AN_APP_GEAR`:** UserGear6 remade, plus definitions. The sense comes from the worker's read-back
  only. Acceptable: the ledger's rule is the measurement, and the definition carries `Reverse` on the same Gear Axes.

**The "unchanged" evidence:**
- *Fingerprints:* sound.
- *Flags:* blind to the old assembly in `carry` (see 3.4).
- *The old read:* the holes are listed in 3.4.
- *The trace:* incomplete (3.4).
- *Closed path:* fingerprints plus the read-only document checked gone. Sound for files.

**Calls the script makes that have never run on SolidWorks:**
- `add_configuration` on a part, the `ReferencedConfiguration` put, `SetSuppression2(1)` on the old copy's component,
  and the raw mates. Each runs inside `run` or `job`, so under the watch, and on copies only.
- **Must-fix M1, (a) the CAM box on save.** The user's save of RangeBox_r2 in `carry` (`save_one`) comes after
  SprocketLight-1 is resolved **in the old assembly**.
  - Lightweight is a file-level state in the session. So r2's instance of SprocketLight may still read lightweight, or
    be made so.
  - Saving an assembly with a lightweight component brings up SOLIDWORKS CAM's modal box (GOTCHAS §100, §15's S-g).
    That box ignores `WM_CLOSE` and would end the run.
  - *Fix:* read every component's state in r2 right before `save_one`. If any reads 1 or 4, do not save, and say
    so.
- **Must-fix M1, (b) a ruling first.** C.3 opens SprocketLight.SLDPRT (`open_document`) to insert it.
  - If opening a part loaded lightweight resolves it, the old assembly's SprocketLight-1 changes state. That is
    inferred, from the spread the probe measured: `w9d…-1.log:121`.
  - The script's `old_diff` then STOPs `carry` at its press, and the whole Done-when section is lost.
  - That STOP would be a true finding against D10 (carrying a lightweight component changes the user's open
    assembly). But the coordinator should rule before the run on one of two courses:
    - keep the STOP;
    - or have the script record a change confined to SprocketLight-1's state as D10's finding (a FAIL), and measure
      the rest.

  I recommend the second: run the lightweight case with the rest, but let its one known consequence be a stated
  finding, not a STOP that takes the Done-when with it.

**False STOPs considered and set aside:**
- `needs_rebuild` in `old_diff`: W9a's bracket compared it on its Build again… and ran clean.
- The user's parts opened by C.3 (`OpenDoc6` and `ActivateDoc3` are not in `WRITES`): allowed, as they should be.

**One possible false STOP, unmeasured:** inserting SprocketConf-1 in Z20 might mark SprocketConf.SLDPRT. The probe
measured `CARRY_INSERT_MARKS_USER_DOCUMENTS` False for a single-configuration part only. If it marks, the user-document
check STOPs `carry`. Note it for the run's reader.

---

## 5. R.2 and stored dependency paths

**What happens now.** `GetDocumentDependencies2(path, False, False, False)` gives the paths **stored** in the
assembly, not those SolidWorks will load. For an assembly copied or moved and not saved since, they name the old
folder.

**Is the worker's present behaviour safe? Not always.**
- *The stored files are gone:* `isfile` is False and R.2 refuses. Safe.
- *The stored files are still on disk* (the usual case for a copied project): R.2 reads the versions of the
  **original** files and opens the copy read-only. SolidWorks then loads the files its search rules find, which can
  be the copies beside the assembly. Their versions were never read.
- *Why it matters:* a copy holding a part saved by the other SolidWorks is exactly what R.2 exists to keep out (the
  CAM box on `QuitDoc`).
- *Likelihood:* rare, but the guard is defeated without anyone being told.
- *The demonstration:* it avoids this by having the user save the copy before closing it, which writes the copy's own
  paths.

**What the contract should say (R.2).** The versions judged must be those of the files SolidWorks would load.

**The smallest change, in two steps.**
1. *Now (package A, a few lines in `_not_open_refusal`):* refuse (`OLD_UNREAD`, with *"it was moved or copied since
   it was last saved: open it in SolidWorks first"*) when the case is ambiguous:
   - any stored dependency path lies outside the old assembly's own folder **and** a file of the same name exists in
     that folder;
   - or the old assembly's folder differs from the folder the record has it in.

   It never refuses a library part that is only referenced in place. It refuses exactly the copied-folder case.
2. *Then:* read `GetDocumentDependencies2(path, False, True, False)` (Searchflag True, the resolved paths) beside it
   in the 2024 probe run. Once it is shown to give the paths SolidWorks loads, judge those.

This is a should-fix for A and the contract. It does not block the 2026 run, since the script saves the copy first.

---

## 6. The self-check, and the time

**The self-check:** `PYTHONPATH=src:tests python probe/w9d_demonstration.py --self-check` ran **33 ok, 0 failed** here.

**What it does not cover:**
- **Nothing of the live part.** Everything after `if SELF_CHECK:` is never imported: `DeskD.build`, `press_build`,
  `old_read`, `old_diff`'s real inputs, `judge_carry`, `poses_judged`, `_propose`'s wiring, `fixture_job`'s picks,
  `states_job`, the trace wrapper and `_target`. A slip there shows only on SolidWorks.
- **`expected_outcome` against the worker's real `plan_carry` on an `OldWork` shaped like the fixture.** Its 23 mates
  and 17 components are checked only on hand-written expectations. *Should:* build that `OldWork` (the kinds, owners
  and states of the fixture), run `plan_carry` for each `fs`, and hold it to `expected_outcome`. That would have caught
  3.3's false FAIL.
- **The trace against the worker's real call sites.** A fake session whose writes go through `_guarded` and `_put`
  would show 3.4's gaps.

**The time: 1 h 20 min on 2026 is optimistic but credible, with 1 h 30–1 h 45 as likely.**
- `carry` does a great deal: R over about 31 mates with three r3 walks; 17 inserts; about 31 remakes, each read back
  and flagged per mode; a post-check per mode with interference. On top of that come the script's two old reads, the
  every-mode read, W9b's mode read, the definitions and the per-mode configuration read.
- Its 35 min could well be 45.

**What to cut first if a section must go:**
- I agree with the author's order: the later Update's lost line first (the fake shows it), then the W9b read in
  `carry`.
- The W9b read is the only interference read that `C9.interference_judged` compares with `CarryResult.clashes`.
  Cutting it loses that comparison, so cut it only with that said.
- Never cut `carry-closed` whole. It is the only section for the not-open read, contradiction 6, UserAsm6 and the
  light part's mate.

---

## Summary

**Must-fix before the first run:**
- **Script, M1.**
  - (a) Never save RangeBox_r2 with a lightweight component: read the states first, and skip the save, saying so.
  - (b) A ruling on SprocketLight-1's state possibly changing in the old assembly when C.3 opens its file. My
    recommendation: a stated finding, not a STOP that loses the section.
- **Script, M2.** Compare each remade mate's entities, mapped old→new, against the script's own read of the old mates'
  definitions taken before the press.

**Should-fix:**
- *Script:*
  - compare a gear mate's sense, not `Reverse`, and count flags per mode against a kind;
  - read the carried states per mode with the script's own reads;
  - require every carried component's frame;
  - hold `anchors` to the fixture's expected anchors;
  - give `old_read` fixed, mate values and the referenced configuration, and name in the note what the trace cannot
    see; compare stems in `_target`;
  - allow "component not carried" for a `no frame` component's mates;
  - make `outcome` a condition of `CARRY_INSERTS`;
  - a self-check of `expected_outcome` against `plan_carry` on a fixture-shaped `OldWork`, and a parity line for
    `DeskD.build`;
  - log Sun's old and new frame per mode before judging poses.
- *Package A:*
  - the N1 test reordered so it pins the fix;
  - `_app_mates_check` blaming only clusters on the erring mate's bodies or train;
  - R.2's copied-folder refusal (§5).
- *Contract:*
  - R.2 judges the files SolidWorks would load (§5);
  - D10 says what a carried lightweight component does to the old assembly's instance;
  - D20 says whether a fixed component, or one held to the layout, is anchored to the world rather than to a gear
    through its cluster.
- *Package B:* nothing. Its uncommitted wording round must keep the phrases the script checks: *"Carried into
  RangeBox_r2, unsaved"*, *"has not yet been shown to carry your work"*, *"As read at"*, *"was closed without saving
  after Build again… carried your work into it"*. Run the self-check again after it.

**May it run on SolidWorks 2026 once the must-fixes are in? Yes.** It works only on copies. Every unmeasured call it
makes is under the dialog watch. With M1(a) it saves nothing lightweight. Its STOPs keep proposals from coming out of
a broken run. The should-fixes make its proposals stronger, but none of them risks a file.

---

## Addendum: the first run on SolidWorks 2026 (34.0.0)

*Independent, 2026-11-17. What I reviewed:*
- *the commits:* `10426c5` and `2fb3946` (the script) and `50a8e54` (the logs and the note);
- *the logs and JSON:* `probe/results/w9d-demo-sw2026-20261117-1-first-contact-light-flag-stop.log` (run 1),
  `…-2-carry-app-faults.log` (run 2), `…-3-carry-closed-read-only.log` (run 3), and the three
  `w9d-demo-20261117-*.json`;
- *the note:* `W9D-DEMONSTRATION.md`, "The first run on SolidWorks 2026";
- *the code the logs point at:* `swbuild._judge` and `_read_old_mates`.

*No SolidWorks.* Nothing in `src/`, the script or the handoff was changed. The two app faults the run named are
being fixed, and I do not re-diagnose them.

**In order of weight.**

1. **Must-fix (fixture and §15): the tie as built cannot show `FELL_TIE`, even after the app's fix.**
   - In the old assembly it over-defines: `UserLock8b` was made with status 5 (run 1 :60), and `UserLock8a` and the
     app's `Sun along Input` read 46 (run 1 :70).
   - `_judge` carries a remade mate that reads the error it had before (`same_error`). It then **excuses every body
     that only such mates of the cluster touch**.
   - Sun is touched in that cluster only by UserLock8a, which will read 46 again. So Sun's tie is excused and no
     `FELL_TIE` comes. What comes instead is an over-definition fallback, or the post-check's stop on Sun ("no cluster
     of yours explains it"), or `_app_mates_check` blaming another cluster for `Sun along Input`.
   - This is reasoned from `_judge` (`swbuild.py`, the `excused` loop); it never ran, since the carry stopped before
     any mate.
   - A replacement is under item 5 below.
2. **Must-fix (script): checks over remade mates passed with nothing remade.** Item 3 below lists each line and what
   the script should do.
3. **Must-fix (package A, not named in the run report): a lightweight component's mate is named "unread" with raw
   Python text, not `lightweight`** (D10).
   - What was read: R called `entity_reference` on SprocketLight-1's Gear Axis while the component was lightweight.
     `GetModelDoc2` gave None, so the read raised *"'NoneType' object has no attribute 'FeatureByName'"* (run 2 :627).
   - `_read_old_mates` keeps that as the entity's `unread`. `plan_carry` tests `unread` before lightweight, so
     UserAxisLight is named *"SolidWorks would not describe UserAxisLight wholly (its reference could not be read
     ('NoneType' …))"* (run 2 :565). The expectation was `lightweight`.
   - *Fix:* do not read a tier-1 reference through a lightweight or suppressed component in R; its mate is named by
     its component's state.
4. **Should-fix (script): the expectations must take two readings this run measured.** On SolidWorks:
   - the entities of a mate on a component **suppressed in the mode showing** read unread (UserAxis9 in `carry`, run 2
     :621; UserAxis7 in `carry-closed`, run 3's outcome);
   - a suppressed component's frame **does** read.

   So M4 (b)'s "make it in a mode where its component is resolved" is never reached on the open path. That mate is
   named `unread` instead, which is honest. `expected_outcome` should accept `unread` for UserAxis9 (open) and
   UserAxis7 (closed). §11.5 of the contract should record the reading.
5. **The rest, by item, below.**

**A correction to my own review.** I wrote that the save-flag bracket is blind to the old assembly in `carry`, because
the user's lightweight set would mark it. It did not mark it: *"GetSaveFlag before none"* (run 2 :566). The bracket was
live, and the old assembly's flag did not turn.

### 1. The two script fixes

- **`10426c5` (the light file's flag): exact as far as it goes.**
  - It sets apart only `flips[LIGHT_FILE] == (None, False)` (not open → open, unmarked), and only while `went`
    (SprocketLight-1 read 1 or 4 before and 2 or 3 after). The file marked, the file loaded while the component stays
    lightweight, the old assembly marked beside it, or any other file's flag still STOPs. Its self-checks show each.
  - Run 2 set apart exactly two things: the state 1 → 2 and the flag (run 2 :570).
- **But `old_diff`'s earlier set-apart (`90cdf20`, M1 (b)) is wider than the ruling** (`probe/w9d_demonstration.py:386-428`).
  When `went` holds, it also sets apart:
  - the light component **moving** (`:404`);
  - its **fixed** state and **referenced configuration** (`n == light` across every key, `:405`);
  - every difference in the **definitions and entities** of each mate on it (`involved`): a changed value too, not only
    an entity read going from unread to read.

  The ruling covers its state going lightweight → resolved, and what that alone changes.

  *Should-fix:* set apart only:
  - `states` of the light component;
  - its frame only None → read;
  - an involved mate's entity going from unread to read.

  A move, a fix, a configuration or a value still STOPs.
- **`2fb3946` (`carry-closed` saves the old assembly itself): the same act as a person's Save of that document.**
  - First `save_modified_in(folder)`, as SolidWorks' own Save would offer for modified references. Then `SaveAs3` to
    its own path, silent: one document, no references saved.
  - It writes nothing a person's Save would not. It saves with L showing, as §15 asks, and writes the copy's paths,
    which is why it is there.
  - It happens before the press bracket, so the fingerprints are taken after it.
  - The section still shows R.2 refusing the unsaved copy first (run 3 :75), then reading the saved one (run 3 :641).
  - Nothing it shows is the script's write.

### 2. What stands as measured from this run (the app at `90cdf20`)

A fix's path is either the r3 walk in R (`swcom.py:3942`) or the code after C.5 (`swbuild.py:8060`).

| Reading | Stands without being shown again? |
|---|---|
| 17 components inserted (`add_component`, `add_component_in`), each placed against its anchor, poses 0 in H (run 2 :642, :650) | The routes stand (`AddComponent5` and the put). **Show again** as part of `CARRY_INSERTS`' evidence. The r3 fix changes which face mates are planned, and so cluster membership and some anchors (Chain-2's), and the next run must prove placement with the mates on. Sun read identity, the same in old and new and in every mode (run 2 :649), so the D20 concern about a fixed Housing-1 did not bite here. |
| `AddComponent5` with `Z20`; Z20 read back in every mode by the script (run 2 :660) | **Stands.** C.4 is before both faults. `CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026 = True` may be taken from it. I would still set it with `CARRY_INSERTS` from the next run: it means nothing alone, and the next run repeats it at no cost. |
| R read Z20 beside its document's Default (run 2 :661) | **Stands.** `component_configurations` is not on either fix's path. `REFERENCED_CONFIGURATION_READ_ON_2026 = True` may be set. |
| States per mode: Sprocket-7 in L, Sprocket-9 in H, by the script's own shown read (run 2 :643, run 3 :654) | **Measured.** C.5 ran to its end. But `swbuild.py:8060`, the fault, is the line straight after it, so **show again** with the fix. |
| SprocketLight-1 resolved in the old assembly by the carry's open, its file open and unmarked, the old assembly's flag not turned (run 2 :566, :570) | **Stands.** C.3 is not on either fix's path. The proposed fact `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY_ON_2026 = True` may be recorded. |
| R.2's refusals: the unsaved copy, a record of another version, the 2024 `Reducer_12to1.SLDASM` (run 3 :75, :681, :685) | **Stands.** Closed-file reads only. |
| The not-open read: open read-only in 5.0 s, close in 0.3 s, L as saved, nothing left open or marked (run 3 :104, :156, :641) | The open and close **stand**. **Show again**: the fixed r3 walk will, for the first time, carry candidates (`GetCorresponding`, `IsSame`, `GetPersistReference3`) inside the job's read-only document, which no run has measured (marks, time). |
| A suppressed component's frame read in R; `ISldWorks.GetConfigurationNames(path)` for a lightweight and a suppressed component, answering `('Default',)` (run 2 :594, :596) | **Stand**, as facts. |
| A mate on a component suppressed in the mode showing reads unread (run 2 :621) | **Stands** as a fact: §11.5 and item 4. |

### 3. The vacuous passes (must-fix, script)

**The lines.** In run 2 (`carry`) and run 3 (`carry-closed`), with no mate remade and the post-check never reached:
- `every remade mate's definition and entities in RangeBox_r2 as the old one's` (run 2 :645, run 3 :656;
  `probe/w9d_demonstration.py:1838`);
- `every remade mate on in the modes it was on in, read again` (run 2 :646, run 3 :657; `:1849`);
- `every app gear free to turn in every mode with the carried mates on` (run 2 :648, run 3 :659; `:1857`). The gears
  were read, but no carried mate was on;
- `every interference SolidWorks reports with a carried component the carry named, and none other` (run 2 :659, run 3
  :670; `:1883`). The carry's own clash read is in its post-check, which never ran, so "the carry named" holds of
  nothing;
- `Sprocket-2 placed against RangeSlv, read in L and placed in H (contradiction 6)` (run 3 :671; `:2214`). It is
  judged on the anchor alone. Its pose FAILed in N and L (run 3 :661, "Sprocket-4", its new Name2) because its lock
  was never made.
- The run-2 superseded `carry-closed` block (run 2 :1132-1149) is the same with 0 components.

**What the script should do:**
- **(a)** Take the population each check should cover from `expected_outcome`: the mates expected `remade` or `fell`.
  - Each remade-mate check covers exactly those, and FAILs naming the mates *not reached* when any is missing.
  - With none remade where some are expected, it says *"not reached: nothing was remade (the carry stopped at …)"*
    and counts as a FAIL.
- **(b)** The two post-check claims ("with the carried mates on" and "the carry named") are judged only when
  `cr.stopped == ""` and `cr.remade` is not empty. Otherwise each is *not reached*, a FAIL.
- **(c)** Contradiction 6 also requires Sprocket-2's pose against RangeSlv in N and L within tolerance.
- **(d)** Every `clean[...]` key fed to a proposal is False when *not reached*.

### 4. Every "not made again" sentence (run 2), against §15

**The question** (run 2 :79; the gates patched; this is the foresight, from the record's inventory, not a read):

| Sentence | What it is |
|---|---|
| UserSunFace, on a face of Sun, part new | **Expected** (§4.4, §12). |
| *"SolidWorks would not describe UserGear6 wholly (its gear ratio could not be read)"* | **Neither R nor the fixture. The foresight:** the record's inventory keeps no definition values. `plan_carry`'s M5 rule (no `GearRatio*` → `WHY_UNREAD`) then fires on every user gear mate in the question. R read it whole: `GearRatioNumerator 29, GearRatioDenominator 20, Reverse 1` (run 2 :616). It is not named in the result. **It does not block `CARRY_GEAR_MATE_ON_AN_APP_GEAR`.** *Should-fix, package B (with A):* where the inventory holds no values, say a gear mate as *may*, or skip the ratio and sense rule for a recorded `OldWork`. |
| *"SolidWorks would not describe UserAxis9 wholly"* | **Something else, now measured:** a mate on a component suppressed in the mode showing reads unread (item 4 above). True, but the clause should say why: *"Sprocket-9 is suppressed in H, so SolidWorks would not describe UserAxis9 there"* (A gives the clause, B words it). |
| UserGearRoot, on a face of Sun, part new | **Foresight:** the inventory keeps no coaxial read, so it cannot know. It should be said as *may*, not *is not*. |
| UserGearFillet, part new | **Expected.** |
| Sprocket-9 suppressed in the mode showing: show a mode where it is resolved | **Expected** (§9.1). |

**The result** (run 2 :565):

| Sentence | What it is |
|---|---|
| UserFaceConc, UserFaceCoin, UserSunFace *"would not describe … wholly (its reference could not be read ('method' object is not iterable))"* | **App fault 1** (the r3 walk), and the raw text (named). UserSunFace should be part new: it is named unread because its Sprocket-5 entity's walk failed. |
| UserAsm6 *"would not describe wholly"* | **Expected** (no root read beside a lightweight component). The sentence gives no why. *Should-fix (A, B):* *"its plane of RangeBox.SLDASM is not read while a component is lightweight"*. |
| UserAxis9 unread | Item 4 above. |
| UserGearRoot part new | **App fault 1:** its coaxial read is the walk's. It is expected to be made again on Gear Axis on 2026. |
| UserGearFillet part new | **Expected.** |
| UserAxisLight *"('NoneType' object has no attribute 'FeatureByName')"* | **New app fault** (must-fix 3 above). It should be `lightweight`. |
| *"SolidWorks stopped the carry … No component is kept as 'gear7'"* and the list it did not get to | **App fault 2.** |
| *"SprocketLight-1 was lightweight … resolved there now"* | **Expected** (M1 (b), ruled). |

**Two further readings the run report did not name:**
- **Names (should-fix, script and note).** The pose FAIL keys components by their **new** Name2: "Sprocket-5 in N/L"
  in `carry` and "Sprocket-4" in `carry-closed`. The note reads them as two different components. Both are **old
  Sprocket-2**, carried as Sprocket-5 (run 2 :535) and as Sprocket-4 (run 3 :558), off by RangeSlv's slide (5 and
  10 mm) because its lock to RangeSlv was never made: app fault 2's consequence. The note should say so, and the
  script should name both (*Sprocket-2, as Sprocket-5*).
  - *A note for the contract:* SolidWorks numbers the inserted instances in insertion order, so the user's components
    come back renumbered (*"Sprocket-2 (was Sprocket-3)"*, run 2 :565). §2.4 allows it. Inserting each file's instances
    in the order of their old numbers would keep most names.
- **The record check FAILed on the footer** (run 2 :666, run 3 :674): `unsaved_at` equals the file's time, but the
  footer's text after the build does not hold §9.4's line (`probe/w9d_demonstration.py:1928`). The run report does not
  name it.
  - Either the window shows the finish's note in place of the idle footer until the next read (then the script should
    read the footer after `desk.read()`), or B's footer drops the line while a note stands (then it is B's, against
    §9.4).
  - Look before the next run. `after the save the footer's carry line is gone` (run 2 :684) reads the record, not the
    footer, so it does not settle this.

### 5. The fixture's tie: the recommendation

**What the tie is for.** §6 and §14.1: on RangeBox's one train, a cluster whose remade mates tie a gear that is free
in the new revision falls back **alone**:
- its mates to app bodies are deleted and its user–user mates kept;
- its components are put back where placed and fixed;
- every other cluster on that train is carried;
- every app gear is free after.

M9 is the only place this shows on SolidWorks (§6: "What M9 can show").

**Why the present one fails it.**
- Locking Sprocket-8 to Sun and to the **fixed** Housing-1 takes all six freedoms of a body that Sun's own mates
  already hold in five. That is over-definition (46) in the old assembly, not a tie.
- The same-error rule then excuses it in the new revision (item 1 at the top of this addendum).
- A user's working assembly does not stand in error.

**The change.**
- Keep **UserLock8a** (Sprocket-8 locked to Sun).
- Replace UserLock8b by **UserAngle8b**: an **angle of 90°** between Sprocket-8's Top plane (`s8:plane2`) and the
  fixed Housing-1's Right plane (`uh:plane3`), made by the app's `add_mate("angle", …, 90.0)` after the lock. Both
  are inserted at identity frames, so the 90° holds as made and nothing moves.
- An angle between two planes whose normals both lie across Sun's axis removes **one** freedom: the rotation Sun alone
  still has. So in the old assembly Sun reads fully defined (it cannot turn, which is the tie), and **no mate reads in
  error**. The fixture's "every mate on in H reads code 0" holds and becomes worth keeping as a STOP.
- In the new revision:
  1. UserLock8a and UserAngle8b are made again; Sun, free before them, reads fully defined: `FELL_TIE`.
  2. The fallback deletes UserLock8a (to an app body) and keeps UserAngle8b (user–user, both components the user's).
  3. Sprocket-8 and Housing-1 are fixed where placed (Housing-1 by its world frame, as ruled).
  4. Sun is free again and every other cluster on Sun's train is carried.

  That is everything the tie was meant to prove, and UserAngle8b is a second angle mate for `CARRY_REMAKE_KINDS`.
- The quiet press over the fixture will still meet a grounded tie (K2) and may refuse. The inventory is recorded
  either way, as now.

**The edits.**
- *Script:* `MATES`, the fixture's expected outcome (UserAngle8b `remade`, kept), and the fallback check
  (`kept == {"UserAngle8b"}`).
- *§15:* *"the tied cluster, Sprocket-8 locked to Sun and held at 90° to the fixed Housing-1 by an angle mate: one
  freedom, so the old assembly reads every mate 0 while Sun cannot turn (`FELL_TIE`)"*. Its *Judged* list: *"the tied
  cluster alone fixed, its angle mate kept"*.

**Should-fix (A and the contract), whatever the fixture.** §6's same-error excuse should never excuse the **tie** of a
gear that was free in the new revision before the cluster. The new revision is the app's own, and an old error says
nothing about it. Keep the excuse for the mate's own code and its components' over-definition only.

### 6. The quiet press over an assembly in error: my recommendation

**As designed, and not a safety hole.**
- An Update with nothing to change writes nothing and judges only what it would write. K2's tie judgement runs on a
  put, and the check phase reads the user's work for a put.
- So the quiet press "went through" (run 1 :89) over `Sun along Input` at 46 and Sun tied, and nothing was written
  over the broken assembly.

**But "SolidWorks already matches the workbook: nothing was changed" over one of the app's own mates in error is an
overstatement.** The values match, and the gearbox does not work. I recommend:
- **The Update's result** gains one CHECK clause when its read finds one of the app's own mates in error: *"SolidWorks
  reads Sun along Input in error (over-defined) in RangeBox.SLDASM; something of yours may hold Sun"*. The mates' codes
  are read in the press already; the cost is a sentence.
- **Build again's question** gains a clause when the record's inventory (or the live read) has mates **of the user's**
  in error: *"UserLock8a was in error in RangeBox.SLDASM as read; made again, it is carried only if it reads the same
  error, and it never keeps a gear from turning"*. It bears on what the carry does (`same_error`).
- An app mate in error in the old assembly needs no clause in the question: RangeBox_r2 builds it new.

---

**Summary.**
- **Must-fix before the next run:**
  1. the tie redesign (script and §15, item 5);
  2. the vacuous passes (script, item 3);
  3. UserAxisLight named unread with raw text instead of lightweight (package A, must-fix 3 at the top). This is
     beside the two app faults already being fixed.
- **Should-fix:**
  - *Script:* `old_diff`'s M1 (b) set-apart narrowed (item 1); `expected_outcome` taking the suppressed component's
    unread mate (item 4 at the top); poses named old and new; the footer check looked at.
  - *Package B:* the question's gear-ratio and coaxial foresight said as *may*.
  - *Package A and B:* clauses for UserAxis9 and UserAsm6.
  - *Package A and the contract:* the same-error excuse never covering a tie.
  - *The contract:* §11.5's reading recorded.
- **May the next run go once those are in, with the app's two fixes?** Yes. It must show again inserts and placement
  with the mates on, the states, and the not-open read with a working walk. These stand from this run:
  `REFERENCED_CONFIGURATION_READ`, the configuration insert, the lightweight fact, R.2's refusals, and the
  read-only open and close.

---

## Re-check of the revision `7ea8864`, before the second 2026 run

*Independent, 2026-11-17.*

- *Judged from the diff* `e2207d9..7ea8864` of `probe/w9d_demonstration.py`, `W9D-DEMONSTRATION.md` and
  `W9D-INTERFACES.md` §11.5 and §15.
- *Against:* the app as committed (package A's fourth round `94f57f8`; `_judge`, `_set_flags` and `plan_carry`), and
  the first run's logs and JSON.
- *The self-check:* run on a clean `git archive 7ea8864` (the tree holds package A's uncommitted fifth round in
  `src/` and tests): **0 failed**.
- *No SolidWorks.* Nothing but this file was changed.

**Verdict: the script is fit for the second run.**
- I found nothing in the revision that would end or spoil the run for a reason of the script's own.
- The two new STOPs fire in `fixture`, about eight minutes in, and only on what they should.
- Every check the review called vacuous now needs something to judge.
- No `propose` line can come out non-None on evidence that was not reached.
- Five points are below: one should-fix, four notes. Two of them depend on package A's and B's rounds still in flight.

### 1. The tie as built

**The plane pair.**
- `angle_pair` (`:462`) chooses Sprocket-8's Top and Housing-1's Right by default, and takes another Top/Right pair if
  the housing stands turned.
- It requires both normals across Sun's axis (their z below 1e-9) and at 90° to each other. That is exactly the
  condition for one angle equation to remove one freedom: the rotation about Z.
- The frames are read in the fixture job, after the lock and before the angle (`:1622`). The lock moves nothing, so
  the pair is judged as the angle will meet it. Self-checked: identity, a turned housing, and a tipped one that gives
  None.

**Whether `add_mate("angle", …)` makes it on SolidWorks.**
- Not measured between two components of the user's.
- But W9a's setup made **UserAngle4** by the same call, the same form and the same value: `u4:plane2` to `lay:plane3`
  at 90° (`probe/w9a_demonstration.py:968`), on both versions.
- The second end there was the layout's plane. The layout is a component like Housing-1, and each end is selected by
  `_component_ref` through its component's own tree order. The selection and the `AddMate5(6, …, radians(90))` call
  are the same code.
- I rate it low risk. If it is not made:
  - the try is logged and `missing` FAILs;
  - Sun then reads under-defined, and `fixture_problems` STOPs (*"Sun … can turn, so there is no tie"*);
  - the run ends in `fixture` with no master kept.

  That is the right end: it costs minutes, not the two hours.

**Sun unable to turn, every mate 0.**
- Sun has one freedom under the app's own mates: its axis coincident and its point distance along Input. The train
  has one freedom in each mode; the build's own per-mode check holds every gear free.
- UserLock8a makes Sprocket-8 rigid with Sun. UserAngle8b then removes the one freedom left, with no constraint
  repeated, so nothing over-defines.
- "Fully defined" (`COMPONENT_FULLY_DEFINED`, 3) is the right reading for "cannot turn": a Sun that cannot slide reads
  3 exactly when its rotation is held. It reads 4 if something conflicts and 2 if it can turn. K2's `_free` reads the
  same thing.
- **In run 1, Sun read 4 (over-defined) in the old assembly** (JSON `carry-gates/old_before`, Sun 4, Planet and Ring 3).
  The new `fixture_problems` STOPs on exactly that.
- The codes are read before Sprocket-9 is suppressed, so no mate reads an error there for that reason.

**The expected outcome after the fallback, against `_judge` as it stands.**
- In the cluster {Sprocket-8, Housing-1}, UserLock8a and UserAngle8b both read 0 as they did before, so no
  `same_error` arises and nothing is excused.
- Sun, free before the cluster, reads 3 after: `FELL_TIE`.
- `_fall_back` deletes the lock (to an app body) and keeps the angle (user–user). It fixes Sprocket-8 and Housing-1,
  the latter already fixed and placed by its world frame (`EXPECTED_ANCHORS["uh"] == {""}`).
- **Package A's fifth round does not change this.** The same-error excuse never excusing a tie does not apply, since
  there is no same error.
- **One note to log, not a STOP:** after the fallback, UserAngle8b joins **two fixed components**. Whether SolidWorks
  gives a satisfied mate between fixed components a code is not measured.
  - The worker skips a fallen cluster in its post-check, so the carry is unaffected.
  - W9b's `judge_every` counts every mate in error, so a code there would show as a FAIL on W9b's line, outside the
    proposals.
  - The run's reader should know that it is this mate and why.

**`_set_flags` in package A's fifth round (pending) may change an expectation.** Mates touched:
- UserAxis7 on the open path (Sprocket-7 suppressed in L);
- UserAxis9 on the closed path (Sprocket-9 suppressed in H).

The worker will no longer judge their flag in that mode. The script's flag check holds `flags read == the worker's
on-modes == the old on-modes` (`flags_wrong`). If the fifth round leaves that mode out of `CarryResult.remade`'s
on-modes, these two FAIL `flags`, and with it `CARRY_INSERTS`. **Should-fix, when A lands:** compare a mate's flags
only in modes where every component of it is resolved, or match whatever the fifth round reports there.

### 2. The closed path without the reload finding

**It is right by the contract and by `plan_carry`.**
- UserAngle8b's two ends are base planes of the user's components, which is tier 1. On the not-open path that waits
  for `PERSIST_REFERENCE_SURVIVES_RELOAD` (§4.1; `_entity_target`'s `tier1`, `not_open`), so the angle is named
  `unmeasured`.
- UserLock8a's ends are whole components, which is tier 3 and needs no reload, so it is made again.
- Sun then has only the lock on it and does not tie, so the expectation `remade` follows.

**On 2026 the branch is never taken.** The reload finding is True, so `carry-closed` makes the angle again and shows
the tie falling back exactly as `carry` does: it shows everything. On 2024, `closed_read` is None, so the whole closed
expectation is `old unread`.

**A note only:** the fallback check (`clean["fallback"]`) does not follow the branch. It would FAIL there, but only in
a configuration no run will meet.

### 3. Checks over remade mates; the proposals

**None of these can pass on an empty population or after a stop:**

| Check | What it now needs |
|---|---|
| `definitions` (`:2001`) | every mate expected `remade` reached (`not_reached`) and every outcome as expected |
| `flags` | the same population |
| `free` (`:2025`) and `interference` (`:2050`) | the carry finished and remade something (`post`) |
| contradiction 6 | Sprocket-2's pose against RangeSlv in every mode, N and L included |
| `states` | both state-carrying components carried |
| "every other carried component resolved" | at least one |
| `anchors` and `poses` | at least one carried and read |
| `record_judged` | something unsaved, where unsaved is expected |
| `outcome`, `fallback` and `same_error` | not vacuous before; still not |

**`proposal_values` (`:500`).**
- It is right that **the configuration insert stands when nothing was remade.** Its evidence is the insert in Z20 and
  the script's own read of Z20 in every mode. Neither needs a mate, and `clean["configuration"]` needs SprocketConf-1
  carried.
- `REFERENCED_CONFIGURATION_READ` likewise rests on R's own read.
- `CARRY_REMAKE_KINDS` drops any kind with a mate whose outcome is not the expected one. `unclean` now carries every
  such mate, including those not reached, so a carry that stops part way cannot propose a kind on its first few mates.
- The gear gate needs `definitions` (all reached).
- `CARRY_INSERTS` needs every key, `definitions` and `flags` among them.
- Self-checked with a carry that remade nothing: inserts, kinds and gear None, configuration True.
- **Note:** this ties `CARRY_INSERTS` to every expected mate being made again. One face mate named for an unrelated
  reason withholds the insert gate. That is conservative and acceptable, but the coordinator may want to set
  `CARRY_INSERTS` from the inserts' own lines if only a mate fails.

### 4. The narrowed set-apart

`old_diff` (`:386`) and `_only_light_reads` (`:435`) set apart exactly four things, and only while SprocketLight-1
goes from lightweight to resolved:
1. its **state**;
2. its **frame going from unread to read** (a read frame that moves is `moved`, a STOP);
3. a mate's **definition or entities differing only in its entity on the light component**, which was unread before
   (no reference, no `EntityParams`) and reads on it after; every other field equal;
4. the **light file's flag** going from not open to open and unmarked.

Every other change is a STOP. Self-checked: a move, the fixed state, the referenced configuration and a mate's value
beside the resolve each STOP.

Run 2's actual difference was the state and the flag only (run 2 :570), which the narrowed rule still sets apart. So
it passes the same reading.

Package A's fourth round now reads no entity of a lightweight component in R. The script's own reads of the old
assembly are the only ones (3) still bears on.

### 5. `record_judged`'s two footer readings (`:2085`)

**Both are what a user sees.**
- **First reading, after `desk.read()`, the finish's sentence standing:** the window as it stands after the build.
  `asks` requires that sentence to ask for the save (`:2107`).
- **Second reading, the note set aside:** the footer a user sees once the note goes, by reopening the window or by a
  read that changes something. The script sets `desk.note = None` and puts it back after, which arranges a state a user
  reaches; it adds nothing a user would not see.

**Neither is made to pass:** each needs its own text, and the record's `unsaved_at` must equal the file's time.

**Notes:**
- `asks` matches a literal phrase of package B's sentence: *"Save RangeBox_r2 in SolidWorks to keep what was
  carried"*. B's wording round in flight must keep it, or the script must follow it. Run the self-check after B lands;
  it says that phrase on the fake.
- If B decides the window shows both lines at once, both readings still hold.
- `carry-gates` calls it with `unsaved=False`, which is right there: nothing is carried.

### 6. What could end or spoil the run for the script's own reason

**Nothing I found.**
- The new STOPs are in `fixture` and fire only on a fixture that is not M9's: a mate in error, or Sun able to turn.
- The checks above are `check`s, not STOPs.
- The self-check covers each new pure judgement: `angle_pair`, `fixture_problems`, `not_reached`, `proposal_values`,
  `_only_light_reads` through `old_diff`, `as_new`, and the new expectations through `plan_parity`. The new tie is in
  `fixture_work`, so `plan_carry` itself is held to `expected_outcome` with it.
- The new live code (`record_judged`'s two readings, the fixture's `angle_pair` and `sun_status` reads) uses only
  members the script already used live (`desk.read`, `desk.note`, `component_frame`, `constrained_status`).

**Where a pending app change would alter an expectation:**
- **Package A, fifth round:**
  - `_set_flags` on a suppressed component's mode: item 1, should-fix when it lands;
  - the same-error excuse: no change for this fixture.
- **Package B:** the save phrase `asks` matches (item 5); the gear-ratio and coaxial foresight now said as *may*,
  which the script does not check.
- **Package A, fourth round (committed):** UserAxisLight now named `lightweight`, as expected. The r3 walk and the Aux
  gear's handle are fixed, so the face mates, UserSunFace (`part new`) and UserGearRoot (`remade` on Gear Axis) can
  meet their expectations for the first time on SolidWorks.

**The face mates' expectations rest on the walk's first real run.**
- An r3 failure on SolidWorks makes them `unread` and FAILs `outcome` and `definitions`: a reading, not a STOP.
- `CARRY_INSERTS` would then not be proposed (item 3's note).

## Re-check of `927487e` and `97628ef`, before the second 2026 run

The script at `97628ef` was run against package A at `c740f92` and package B at `11a63ab`. No SolidWorks was run.
- `--self-check` ends with 0 failed.
- The suite at `c740f92`: 3968 passed, with only the two tkinter failures.

### Verdict

**The script is fit for the run.**
- No new check can FAIL on a harmless measured fact in this fixture.
- No `propose` line comes out stronger than its evidence.
- One check could FAIL wrongly in another fixture (D4).
- Two small lines are worth adding (D5, D6).

**The whole head is fit for the two-hour run:** package A at `c740f92`, package B at `11a63ab`, and the script at
`97628ef`. B's round in flight, the limit-mate *may*, is not met by the run. What the run meets for the first time
is listed in `W9D-REVIEW-A.md`, at the end of its last section.

### The new checks, one by one

**`fixed_every_mode`, a condition of CARRY_INSERTS.**
- **What it reads:** `IsFixed` in every mode, for each fallen component and each component fixed in the old assembly.
- **Fetched fresh in each mode:** `comp_of` goes through `_component_by`, so a held handle cannot read False where
  W8 §9.4 warns it would.
- **The member answers on 2026:** run 1's and run 2's `old_before` read Housing-1 True and every other component
  False.
- **Which components:** in this fixture, Sprocket-8 and Housing-1. Neither is suppressed in any mode, so the check
  cannot FAIL on suppression here.
- **Where it could FAIL wrongly (D4):** a component suppressed in some mode reads IsFixed False there. Sprocket-9 read
  False in H, its suppressed mode. `fixed_problems` would then call that mode "not fixed". Judge only the modes where
  the component is resolved, as `flags_judged` already does.

**The kept-name check.**
- `renames_problems` passes a differing name only where a fact begins `"<old> is carried as <kept>"`.
- That is exactly the worker's own sentence (`7e3ad9a`, `_carry_cluster`), so differently worded facts cannot meet it.
- It is a plain `check`, not a `clean` key, so even a FAIL would hold back no finding.

**The fact tags.** The tags only label the log; nothing judges by them.
- `c740f92`'s new sentence, *"after … fell back in H: … read fixed in N but … mm from its frame there, so it was put
  back at it"*, contains "fell back in". So it falls under "fixed after a fallback", not "worker".
- A sentence under no tag would still be logged, as "worker".

**Proposals.**
- **CARRY_REMAKE_KINDS** now uses `swbuild.carry_kind` on what R read, the gate's own words.
  - `kinds_clean` counts a kind only if a mate of it was made again and read back clean, and no mate of it is unclean.
  - The mates expected to be made again but not reached sit in `unclean`, so they hold the kind back.
  - A kind R read as `unknown` is not a gate word and drops out.
  - No limit angle is in the fixture, so none can be proposed. "limit distance" rests on UserLimit10 alone, and its
    mates are now printed.
- **CARRY_INSERTS** gains a condition, so it can only get stricter.

**Gear alignment and Flipped.**
- A gear's alignment is printed and no longer judged, as the worker no longer compares it.
- A distance's or angle's `flipped` is no longer compared. Its FlipDimension and Flipped before and after are printed
  beside the worker's sentence.

**Self-check coverage.** Each new judgement has its failing way checked:
- a kept name the worker did not say;
- a mode read not fixed, or not read at all;
- a gear's alignment not judged, and another kind's still judged;
- no limit kind proposed that the run did not show;
- the worker's `carry_kind` on a plain distance and on a limit one.

The one gap is `fixed_every_mode`'s *"not reached: none"* (no component to judge), which is not self-checked. It
cannot happen in this fixture, because Housing-1 is always fixed in the old assembly.

### Should-do, none blocking

**D4.** `fixed_problems`: skip a mode where the component is suppressed (above).

**D5.** For the components that `c740f92` may put back, print the script's own frame read beside IsFixed per mode.
- The worker's *"read fixed … but … mm from its frame"* fact is the first measure of positions per configuration for a
  fixed component.

**D6.** Log `swConstrainedStatus_e`'s names once, from `swconst.tlb`, with the W9c script's reader.
- Run 2 and run 3 read 5 on carried user components. Its name is in no committed note (`W9D-REVIEW-A.md`, A7).

## The second run on SolidWorks 2026 (34.1.1), and `41afa37`

*Independent, 2026-11-18, at `c2d95cc`. What I reviewed:*
- *the commits:* `41afa37` (the script's fix made during the run) and `c2d95cc` (the two logs, their JSON and the
  note's section "The second run on SolidWorks 2026");
- *the logs:* `probe/results/w9d-demo-sw2026-20261118-1-whole-closed-read-mode-fault.log` ("log 1", snapshot
  `f7c2f0d`, `w9d-demo-20261118-031226.json`) and `…-2-carry-closed-clean.log` ("log 2", snapshot `41afa37`,
  `…-042519.json`), both `(34, 1, 1)` in the JSON;
- *the code the logs point at:* `swbuild._remake`, `_read_back`, `_judge`, `_fall_back`, `_component_named`,
  `ui_text.carried_status`, `_fallback_sentence`, `_standing`, and the script's `definitions_in`, `judge_carry`,
  `trace_problems`.

*How.* No SolidWorks was started; nothing in `src`, the script or the tests was changed. The suite at `c2d95cc`:
4103 passed, 1 skipped, 1 failed, the known
`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`. In a
scratch copy (`git archive`, deleted after) I set the five write findings as §4 below allows and ran the suite again,
and drove `ui_text.carried_status` on the fake for the two sentences of §7.

### Verdict

**The evidence stands, and the 2026 findings may be set** as §4 gives them. No section needs running again on 2026
for them.
- Every `ok` I traced is a real reading over the population it names. Three pass on an empty set that is the
  fixture's truth, not a skipped check (§1). No FAIL was the app's.
- `41afa37` is right and loosens nothing. `carry` at `f7c2f0d` stands for head: the fix does nothing on its path,
  and `src` differs from `f7c2f0d` only in `_ON_2024` values of W9c's gates.
- **Two must-fixes in the app's wording** (§7), both reached only once `CARRY_INSERTS_ON_2026` is True:
  - the fallback sentence names fallen components by their new Name2 with no *(was …)*, so it can give a name the
    same result uses for another of the user's components;
  - the standing clause says *sub-assemblies come over rigid* while a sub-assembly is named as not carried.
  Neither changes what is measured. Neither needs SolidWorks. Land both before or with the findings commit.
- The note says nothing the logs contradict. Three small points are said more strongly than the logs bear (§7, N1–N2).

### 1. Section by section, and the Done-when

**Counts.** Recounted from the logs, the note's table is exact:
- `fixture`: 20 ok, 0 FAIL, 564 s (log 1:92);
- `carry-gates`: 27 ok, 0 FAIL, 773 s (log 1:731);
- `carry`: 45 ok, 0 FAIL, 1716 s (log 1:1573);
- `carry-closed`: run 1 had 45 ok and 1 FAIL (log 1:2345, 2420), run 2 had 46 ok and 0 FAIL (log 2:861).
- The least free memory in either log is 9.63 GB (log 1:2265).
- Run 1's and run 2's `carry-closed` check lines differ only in instance names and in the one FAIL, which is now an
  ok.

**Checks that pass on an empty set.** Each is the fixture's truth, not a check skipped:
- *"no mate back in an old error []"* (1:1479, 2:779): no user mate was in error before the press.
- *"interference … unnamed none, unseen none"* (1:1514, 2:817): SolidWorks reported no interference with a carried
  component (1:1513). So the carry's clash sentence is not shown on SolidWorks.
- *"nothing moved []"*: the worker's `moved` compares the whole frame, the rotation included
  (`swbuild.py:8781-8785`). So this is a real reading of every carried component in every mode.

Each remade-mate check names its population and says *"every one reached"* (1:1484, 1486; 2:784, 786). These are the
fixes the addendum's §3 asked for, and they hold here.

**The plan's Done-when, row by row (`carry`, log 1, unless said).**

| Done-when | Lines | Stands? |
|---|---|---|
| After Sun's Flank change and a shaft added, Build again… makes RangeBox_r2 | edit 759-778; classify 792; built 723 s, saved 1398, 1409 | Yes |
| Both clusters carried | 17 components 1477; anchors 1480; poses, 49 reads, none off, 1505 | Yes |
| Their mates remade and on in the modes they were | definitions and entities read back equal 1484; flags 1486, 1512; names kept 1499 | Yes |
| The bore mate on Sun named | UserSunFace *part new* 1471, in the result 1397; UserGearFillet 1474. RangeBox's Sun has no bore: an end face stands for it (§15's departure) | Yes, as §15 words it |
| The keyway in Sun named in the question and the result | question 799-800; result 1470, 1397 | Yes |
| Every app gear free to turn in every mode | 1503; W9b's read clean in H, N and L, 1506-1511 | Yes |
| The carried items unsaved | GetSaveFlag True 1518; record at schema 10, `unsaved_at` the file's time, 1534; the line gone after the user's save 1552 | Yes |
| The old assembly and every user file unchanged on disk | size, time and hash 1404; save flag, mode, frames, states, mates as before but the ruled set-apart, 1402-1403; no traced write, show, rebuild, save or close, nothing saved after the first save, 1405-1406 | Yes |
| The closed path | read read-only with L showing, nothing left or marked, closed by the job, 2:771-772; on disk 2:707; traced 2:708-709 (the job's own `OpenDoc6`/`QuitDoc` of the old assembly, allowed by `trace_problems` on that path only) | Yes |
| Confirmed on 2024; reviewed | — | Not run |

**§15's further items** stand as the note gives them, each at the line it cites:
- the tie by `FELL_TIE` (1478, 1487-1489, 1500);
- the states per mode (1481-1482);
- SprocketConf-1 in Z20 (1515-1516);
- the names *unread* and *lightweight* (1472-1476);
- `carry-gates`' refusals (685, 696, 707, 718, 729);
- in `carry-closed`: R.2's refusals, contradiction 6 and the lost carry (2:75, 77, 818, 841, 845, 847, 859).

**Facts logged for the first time.** These also stand as written:
- `swConstrainedStatus_e`'s names (1:67);
- one FixComponent in H holding in every mode (1:1487-1490, 2:787-790);
- FlipDimension 0 and Flipped False on every distance and angle (1:1491-1496, 2:791-797);
- the out code of `GetObjectByPersistReference3` (1:825 on);
- the entity reads taking 2.1 to 2.8 s (1:833-858).

### 2. `41afa37`

**It is right.**
- *The cause.* The JSON shows it as the note says. Run 1's `carry-closed.definitions` read UserAxis9's entity on
  the carried Sprocket-9 (then Sprocket-6) with `reference` and `feature` None in H. `carry.old_before.definitions`
  read the same None on the old Sprocket-9 in H. Run 2's read, in L, gives `Gear Axis`.
- *The fix.* `judge_carry` calls `definitions_in` after `every_mode` (`w9d_demonstration.py:2170`, then `:2202`).
  `every_mode` leaves RangeBox_r2 in its first mode. `definitions_in` now shows `old_before["active"]` when it
  differs, with the same show and rebuild `every_mode` uses, reads, and puts the first mode back.
  - On the closed path `old_before` is read after the user's save with L showing (`:2679`), so both sides are read in
    L.
  - In `carry` both are H, so `mode == first` and nothing is shown. That section's reads at `f7c2f0d` are what
    head's script would read.

**It loosens nothing.**
- `definition_problems` and `entity_problems` are unchanged, and so is the population.
- Reading in a mode where the component is resolved can only expose more of a remade mate, not less.
- The show and rebuild touch only RangeBox_r2, which is the job's own document and already unsaved and shown by
  `every_mode`. Later checks read nothing that the extra show could have hidden.

**Head's script and `carry`.** Between `f7c2f0d` and `41afa37` the W9a harness gained the `WW_OUTLIVED` hook.
`WW_OUTLIVED` is None unless W9c's `main` sets it under its own flag (`w9c_demonstration.py:4093`). W9d imports
W9c's script for `press`, `specs`, `same_sheets`, `row_edits`, `edit_live`, `interference_judged` and
`record_on_disk`, and none of these is in the diff. `carry-closed` was rerun at `41afa37` and is clean.

**No section has to run again on 2026 before the findings are set.**

### 3. Head's `src`

`git diff f7c2f0d..HEAD -- src` is `findings.py` alone:
- W9c's five `UPDATE_*_ON_2024` set True;
- their comments.

Nothing in the carry reads a W9c gate. The later Update in `carry-closed` runs on 2026 and reads `_ON_2026`. So both
logs stand for head's `src`, which is `41afa37`'s `src` exactly (`git diff 41afa37..HEAD` touches only the note
and the logs).

### 4. The findings for 2026

| Finding | Set `_ON_2026` | Rests on |
|---|---|---|
| `CARRY_INSERTS` | **True** | log 1:1477-1482, 1489, 1503, 1505, 1512, 1518, 1534, 1404, 1406, proposal 1553 (every condition True); closed path log 2:777-782, 789, 806, 808, 818, 834 |
| `CARRY_INSERTS_IN_A_CONFIGURATION` | **True** | log 1:859-860 (`add_component_in` … `'Z20'`), 1515, proposal 1554 |
| `REFERENCED_CONFIGURATION_READ` | **True** | log 1:823, 1438, 1516, proposal 1555; closed, log 2:738 |
| `CARRY_REMAKE_KINDS` | **`('coincident', 'concentric', 'parallel', 'distance', 'angle', 'limit distance', 'lock', 'gear')`** | log 1:1484, 1486, 1499, the kinds 1556-1563, proposal 1564; log 2:784, 786, 800 |
| `CARRY_GEAR_MATE_ON_AN_APP_GEAR` | **True** | log 1:1457, 1464 (as read), 1484, proposal 1565; log 2:784 |
| `CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY` | **True, as a fact** (see below) | log 1:1402, 1408, 1410; the result's sentence 1397 |
| `CARRY_INSERTS_A_SUBASSEMBLY`, `CARRY_REMAKES_ON_A_LEAF`, `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`, `ORIGIN_ENTITY_READ`, `PERSIST_REFERENCE_ROUTE_FOR_VERTICES` | **stay None** | log 1:1566-1571: none is in the fixture |

**Every name but the fact's** exists in `findings.py` as written (`:2139-2172`), each at None on both versions.

**`CARRY_RESOLVES_A_LIGHTWEIGHT_COMPONENT_IN_THE_OLD_ASSEMBLY` is not in `findings.py`.** `W9D-INTERFACES.md` §17.1
asked for it as a fact, None until M9. Nothing in `src` reads it: the worker reads `resolved_in_old` itself, and the
result says it (1:1397). *For a ruling:*
- either add the pair (`_ON_2026 = True`, `_ON_2024 = None`) as a documented fact;
- or keep it in the comments only.
I recommend the pair, so the 2024 run has a name to set.

**Each comment should carry its caveats:**
- *All:*
  - measured on 34.1.1 at `f7c2f0d`, whose `src` differs from head only in W9c's 2024 values;
  - the probes' reads (§8.1) were measured on 34.0.0, and this run reads them clean on 34.1.1 too (log 2:771-772, the
    read-only open and close);
  - one fixture of 17 parts on RangeBox;
  - the old assembly unmarked at the press (1:806) on the open path. An old assembly open with unsaved changes is
    measured by the probe's state (e) only.
- **`CARRY_INSERTS`:**
  - the fallback shown is `FELL_TIE` only, with one FixComponent fixing in every mode;
  - `FELL_NEW_ERROR`, `FELL_OVER_DEFINED`, the per-mode fix, a refused put, `same_error`, `moved`, a clash
    sentence, a mode new or gone in the revision, and a stop part way are on the fake only. The stop was met once on
    SolidWorks, at `90cdf20` (the first run);
  - instances are renumbered in insertion order (log 2:778);
  - a user part open in its own window with unsaved edits is not measured;
  - the fixed state is read in the mode showing only. A component the user fixed in some modes and not others comes
    over by that one read. This is my inference from `OldComponent.fixed` and the one-FixComponent fact, not
    measured.
- **`CARRY_INSERTS_IN_A_CONFIGURATION`:** one part with two configurations, its document's active one Default.
- **`REFERENCED_CONFIGURATION_READ`:** the same component, read open (1:823) and read-only (2:738). On a lightweight
  or suppressed component the document's configuration reads '' while the referenced one reads Default (1:821-822).
- **`CARRY_REMAKE_KINDS`:** what stands for each kind:
  - coincident: 12 mates, on axes, planes and one face pair;
  - concentric: one, an axis to a bore face;
  - parallel: one, on planes;
  - distance: three, and UserAsm6 to the assembly's plane on the closed path;
  - angle: two, both 90°;
  - limit distance: one;
  - lock: three, one of them between two user parts;
  - gear: two, both Reverse 1. A gear mate of the other sense is not remade on SolidWorks: UserGearFillet, Reverse 0,
    was named for its face.

  Every distance and angle read FlipDimension 0 and Flipped False, so which of the two stands for AddMate5's Flip is
  not told apart.

  Perpendicular, tangent and limit angle are not in the fixture, and with this value they are named.
- **`CARRY_GEAR_MATE_ON_AN_APP_GEAR`:**
  - on Sun, a part made new, through its `Gear Axis` and through a root cylinder read coaxial (`COAXIAL_FACE_READ`);
  - an app gear reused as the same file is not shown;
  - the remake with the other Flip after a wrong sense is the fake's only;
  - alignment 2 is not judged.

**The pins.** `tests/test_findings.py` should pin, through `_w9a_run`, log 1 with `…-031226.json` (`(34, 1, 1)`,
`f7c2f0d`):
- `data["proposal"]` for the five set and the six None;
- the `propose` lines 1408 and 1553-1571;
- 1477, 1478, 1484, 1486, 1503, 1505, 1515, 1516 and 1518.

And log 2 with `…-042519.json` (`41afa37`): 771, 777, 784, 786 and 818.

**Ten tests now lean on these findings being None on 2026.** Setting them in the scratch copy failed:
- `test_findings.py`: the two W9d tests;
- `test_swbuild_carry.py`: three every-gate-None tests;
- `test_workbook_carry.py`: two;
- `test_workbook_user_record.py`: one;
- `test_workbook_window.py`: two.

They need a `w9d_unmeasured` fixture, as `74024a1` gave W9c's.

**What the app does for a user while each stays None (2026).**
- *A sub-assembly:* named with `CARRY_INSERTS_A_SUBASSEMBLY_ON_2026` and left. The sentence is true, but the
  standing clause beside it is not (§7, must-fix 2).
- *A mate on a leaf:* named, *"M1 is on a part inside your sub-assembly …"*.
- *A virtual component:* named by the `^` rule, *"… is a virtual component, with no file of its own"*.
- *A pattern instance:* carried as a component of its own, which the standing clause says.
- *An origin or a vertex:* the mate is named with its finding.

Each is a true sentence and nothing is lost. The old assembly keeps all of it.

### 5. What a real user's Build again… can reach that this run did not show

**Every gate open together.** That is what `carry` and `carry-closed` ran: the five write gates were patched True
together (1:794-798, 2:80-84), and the reads were committed. The one difference once committed is the kinds:
- the run patched all eleven, and the committed value is eight;
- so perpendicular, tangent and limit angle are named, by the same path that named UserSunFace, which was shown.

**What every unshown path has in common.** I traced each through `swbuild`. Each acts only after RangeBox_r2 is built
and saved, and writes only into RangeBox_r2. What the run showed, in `trace_problems` and the disk hashes, also holds
by construction:
- nothing is saved after that first save;
- the old assembly and the user's files are never written;
- the old assembly is never shown or rebuilt on the open path.

**The unshown paths:**
- **`FELL_NEW_ERROR` and `FELL_OVER_DEFINED`:**
  - They differ from the measured `FELL_TIE` only in their trigger: a remade mate's code
    (`swbuild.py:8548-8559`), and a status equal to 4 (`:8565-8567`).
  - Their writes are `_fall_back`'s, which `FELL_TIE` measured: delete the job's own mates, put back, one
    FixComponent.
  - Safe by construction.
- **The per-mode fix (`_fixed_in_every_mode` finding a mode not fixed):** a further FixComponent or put on the job's
  own component in RangeBox_r2. Safe.
- **A refused put, a refused `AddMate5`, a read-back that differs:**
  - `_remake` reads each mate back. A gear's sense is tried once more with the other Flip.
  - Anything still different is deleted again and named (`WHY_DIFFERS`). A refusal is named (`WHY_REFUSED`).
  - Nothing is kept unread. Safe.
- **A distance or angle on its other side (FlipDimension 1):**
  - It is made with that Flip, and its side is judged by `moved`, which compares the whole frame.
  - At worst the sentence says the component moved: true, and nothing is lost.
- **A COM failure or `_CarryStop`:**
  - It stops with the carry unsaved and said, and the build saved as built.
  - Seen on SolidWorks once, at `90cdf20`.
- **Kinds of component not in the fixture:** each gated or named (§4).

**I would keep no gate closed for safety.** What is unmeasured can at worst make RangeBox_r2 less faithful, and then
the app says so. The two places where it would say something untrue are §7's wording must-fixes, not gates.

### 6. Constrained status 5

**Nothing in the app depends on 5.**
- The carry tests a user component only for `== COMPONENT_OVER_DEFINED` (4), at `swbuild.py:8566`.
- It tests an app gear only for `!= COMPONENT_UNDER_DEFINED` (2), at `:8307`, `:8607-8608`, `:8757-8765` and
  `_free_to_turn`.
- So a 5 on a user component triggers nothing. A 5 on an app gear would read *not free*, which is the conservative way.
- `_judge` runs in the cluster's own mode, where its components are resolved.
- The script logs 5 as a fact only (1:1502).

**A pattern the note did not draw** (an inference from five readings, not traced). Each component that read 5 was
suppressed in that mode with no mate on it in the new assembly:
- old Sprocket-9 here, carried as Sprocket-11, its UserAxis9 named (1:1502);
- in the first run, where the carry stopped before any mate, Sprocket-9 as Sprocket-10 in H and Sprocket-7 as
  Sprocket-8 in L (`w9d-demo-sw2026-20261117-2-carry-app-faults.log:647`).

Each suppressed component with its mate remade read 2 there:
- Sprocket-7 in L here (1:1502);
- Sprocket-9 in H on the closed path (2:805).

So *"not tied to suppression alone"* is right. *"Suppressed and unmated"* fits every reading so far.

### 7. Must-fix and should-fix

**Must-fix 1 (app, `ui_text.py:6107`, `_fallback_sentence`; also the clash sentence at `:5954-5957`).** The fallen
components are named by their new Name2 with no *(was …)*, though the same result says *"Housing-1 (was Housing-2)"*
for an insert (`:5920`).
- Log 1:1397 says *"UserAxis9 is on Sprocket-9, which is suppressed in H"* (the old Sprocket-9). Two sentences later
  it says *"Housing-1 and Sprocket-9 are fixed where they stood in RangeBox_r2"*. That Sprocket-9 is the old
  Sprocket-8 (1:1478).
- Log 2:705 says *"Housing-2 and Sprocket-6 are fixed"*. The user's own Housing-2 (cluster two) and Sprocket-6 (the
  gear mate) are other components. These two are the old Housing-1 and Sprocket-8 (2:778).
- On the fake at head, `inserted=[("Sprocket-8", "Sprocket-9"), …]` with a fallback on Sprocket-9 gives *"Sprocket-9
  is fixed where it stood in RangeBox_r2"*.
- *Fix:* name each as the insert clause does, *"Sprocket-9 (was Sprocket-8)"*, from `done.inserted`.

**Must-fix 2 (app, `ui_text.py:5127-5129` and `_standing` at `:5815-5824`).** The standing clause always says
*"sub-assemblies come over rigid"*. With `CARRY_INSERTS_A_SUBASSEMBLY_ON_2026` None, on the fake at head, one result
says:
- *"… so Drive-1 is not carried …"*;
- then *"… sub-assemblies come over rigid, pattern instances as components of their own."*

*Fix:* say the sub-assembly clause only where the version's `CARRY_INSERTS_A_SUBASSEMBLY` is True, as the pattern
clause follows `PATTERN_INSTANCE_READ`; in the question likewise.

**Should-fix, the note (`W9D-DEMONSTRATION.md`, "The second run").**
- **N1.** Some of the setup is not in the logs:
  - the md5 of the master folders before and after;
  - that no other SolidWorks, Excel or Python ran;
  - that the session exited by its own close.

  Say these as the operator's account. The logs show PID 53472 and *"open before: []"* (1:4-5).
- **N2.** Two boxes are said as outside a job but need placing more exactly:
  - The notification box at 1:595-596 came *"while GetTypeName2 was in progress"*: the script's read after the
    press, outside the job.
  - SolidWorks' open-progress window (*"Opened 26 Components … Post load updating"*, with a Close button) came inside
    the job's read-only open (1:1665, 2:104). The job went on, and it closes by itself.

  Say both as they were.
- **N3.** The 5 pattern of §6, as an inference.

**Privacy.** The two logs hold the Windows profile path in their run lines, as the earlier committed logs do. Neither
holds a user document title (*"open before: []"*).

### 8. What remains before W9d can close

1. Must-fixes 1 and 2 (package B's wording), with tests on the exact strings. No SolidWorks.
2. Set the 2026 findings of §4 with their comments and pins, the fact by the ruling, and a `w9d_unmeasured` fixture
   for the ten tests.
3. W9d's probes on 2024 (`state`, `faces`, `sub`, about 40 min; `W9D-PROBES.md`'s command line), their review, and
   the `_ON_2024` reads set from it. None has run.
4. W9d's demonstration on 2024, from head with 1 and 2 in:
   - `fixture`, `carry-gates` and `carry` in one fresh session;
   - `carry-closed` in another, with a 2026-saved file;
   - about 2 h 15 min.

   Then its review, and the `_ON_2024` writes and the fact set from it. W9c's own 2024 `remake-m3` rerun is
   separate.
5. Carried as unmeasured caveats in the comments and the handoff:
   - the fallbacks other than the tie;
   - the per-mode fix;
   - a clash sentence, `same_error` and `moved`;
   - a mode new or gone;
   - FlipDimension 1;
   - a gear mate of the other sense;
   - perpendicular, tangent and limit angle;
   - a sub-assembly, a leaf, a virtual component, a pattern, an origin and a vertex;
   - an old assembly open with unsaved changes, and a user part open with unsaved edits;
   - a fixed state that differs by mode;
   - an app gear reused as the same file under a user gear mate.
6. Documents:
   - `W9D-INTERFACES.md` §8.1: the M9 rows set for 2026, and 34.1.1 named beside 34.0.0;
   - `ISSUE-1-PLAN.md`: W9d's Done-when met on 2026;
   - `W9D-DEMONSTRATION.md`: N1-N3;
   - `HANDOFF-WORKBOOK.md`: stale after 2026-11-17 midday, so W9d's state, both 2026 runs and the reviews;
   - `design/UI-DESIGN.md` §9 if must-fix 1 or 2 changes its examples.

## Re-check of `891a707`, `225e3d7`, `e3395d3`, `2b51fbe` and `a3e05fe`, before the 2024 run

*Independent, 2026-11-18, at `2b51fbe`. No SolidWorks was run. I ran no whole suite and changed nothing but this
file. In a `git archive` scratch copy, deleted after, I ran:*
- `test_findings.py`, `test_swbuild_carry.py`, `test_workbook_carry.py` and `test_workbook_user_record.py`: 473
  passed;
- W9d's `--self-check`: 0 failed;
- ten flips, one at a time, each against its test file.

**Verdict: fit for the 2024 run. Nothing must be fixed first.**

**The values.**
- `git diff c2d95cc HEAD -- src/gear_generator/findings.py` changes these assignments and no others:
  - on 2026, the five my §4 allowed, at exactly those values: the kinds are the eight words, with no perpendicular,
    tangent or limit angle;
  - the lightweight fact as a pair, True on 2026 and None on 2024;
  - on 2024, the fourteen probe reads, each written as its 2026 twin. The two r3 strings are the constant
    `entity_references` compares (`swcom.py:3947`);
  - `WHATS_WRONG_STAYS_WITHOUT_A_REBUILD`, from W9c's `29d09da`, which is outside these commits.
- Every `CARRY_*` write, `REFERENCED_CONFIGURATION_READ`, `VIRTUAL_READ`, `PATTERN_INSTANCE_READ`,
  `ORIGIN_ENTITY_READ` and the vertex route stay None on 2024.
- The comments carry the caveats as given, and §8, §8.2 and §8.3 of `W9D-INTERFACES.md` say the same.

**The pins pin.** Each of these flips fails its test:
- `CARRY_INSERTS_ON_2024` True;
- `COAXIAL_FACE_READ_ON_2024` False;
- `REFERENCED_CONFIGURATION_READ_ON_2024` True;
- the kinds without `gear`, and the kinds with `perpendicular`;
- the lightweight fact True on 2024;
- `DEPENDENCIES_READ_ON_2024` changed;
- the fallback sentence's `(was …)` taken out;
- the moved sentence's `(was …)` taken out;
- the rigid clause forced on.

**No test asserts less than before.**
- The eight tests given `w9d_unmeasured` still assert what they did, with the M9 findings None on both versions.
- The three tests that held a 2024 value at None now hold it equal to its 2026 twin and not None.
- The new `test_w9d_2024_findings_rest_on_the_probes_2024_run` pins each value to its `propose` line, and the
  differing facts to their lines and the JSON's `sections`.

**The wording** (`ui_text.py`) is true in each state that says it:
- Renamed components:
  - `_carried_as` takes the new → old map, so a component SolidWorks kept by its name is said alone, as the test's
    second half holds.
  - The fallback, moved, clash, sub-assembly and pattern-instance sentences each name a carried component by its new
    name with its old one beside it.
  - The moved sentence still finds its anchor by the old name.
- The rigid clause (`_standing`, `:5879-5891`):
  - It is said only where `CARRY_INSERTS_A_SUBASSEMBLY` is True on a known version and no sub-assembly is left. That
    finding is None on both versions today, so it is said nowhere.
  - In the question, `comps` is read only when there is a plan.
  - Where nothing is carried, every sub-assembly counts as left.
- No probe script matches the changed words.

**`carry-gates` on 2024 with the probe reads set and every write None.** This is the state the second 2026 run met,
with every write None and the reads set, which passed 27 ok:
- `section_gates` reads the standing gates through `finding_name`, which is `_ON_2024` there;
- `unset` holds `CARRY_INSERTS_ON_2024`, so the question and the result must lead with it;
- there is no r3 walk while it is None;
- each gate's own refusal is checked with the others patched True, and every one of them is None on 2024;
- `probe_reads(2024)` now gives the 2026 expectations, so `carry` and `carry-closed` take the unshown-states branch
  and the closed path is read;
- `test_what_a_carry_is_gated_on_per_version_as_committed` holds that on 2024 `CARRY_INSERTS` alone gates the
  carry.

**A correction to my probe review's watch list.** Since `f3c4873`, W9d takes `--close-outlived-whats-wrong` (the
coordinator's extension). Use `W9D-DEMONSTRATION.md`'s 2024 command lines, which carry it, not the ones in
`W9D-PROBES-REVIEW.md`'s last section. Without the flag, a box that outlives its job is still the STOP.

**Still open, not before the run:** the edge prefilter's should-fix in `swcom.entity_references` (`:3964`). M9's
fixture has no edge mate.

## A planet copy made new: `carry_for`'s names and why (assessed 2026-11-18, at `34e39ac`)

*Read-only. No SolidWorks was run, and no code was changed. I reproduced and fixed the fault only in a `git archive`
scratch copy, deleted after.*

**What happens.** In `update.carry_for` (`src/gear_generator/workbook/update.py:3306`), a body whose part is made
new looks up its build job by `c.gear in j.gear_ids`. `_why_part_new` (`:3226-3231`) looks up `made_new` and the
job the same way. A planet copy's id (*Planet copy 1*) is never in `gear_ids`, which hold the Gears row (*Planet*).
Reproduced on the fake: RangeBox with Planet's Face width changed gives each copy `names == ()` and
`why_new == "its values changed"`. Every other new body gets 6 names, and `old_names` is right for the copies too (6).

**What a carrying Build again… then does.** `names` is read only at `swbuild.py:7484` and `:7488`.
`old_names`, which is right, decides what is the app's.
- **A mate of the user's on a planet copy's own feature** (its Gear Axis, or any app feature named in its sidecar):
  - A gear mate on its Gear Axis or a coaxial face is not made. It is named `WHY_GONE`: *"UserGearP was on Planet
    copy 1's Gear Axis, which Planet copy 1's new part does not have"*.
  - A mate on any other app feature of the planet gets the same sentence.
  - The mate is left behind in the old assembly. Nothing is made on the wrong thing. **But the sentence is untrue:**
    the new part has that feature, and the mate should have been made on it.
  - Base planes (`plane1`-`plane3`) are not affected.
- **A feature of the user's in a planet's part, and a mate on it:**
  - The feature is still told from the app's by `old_names`, which is correct, so no app feature is called the user's.
  - A mate on it is named `WHY_PART_NEW` and the feature is named as staying behind, both true.
  - But the reason is only *"its values changed"*: *"its Face width changed"* is lost. Where the planet's part is new
    because Update left it unsaved (`UNSAVED`), *"its values changed"* is **untrue**, and `MISMATCHED`'s
    *how to keep it* sentence is lost. I reasoned this from the code and did not run it.
- **Nothing else reads these names.** Nothing is lost silently, and nothing is written outside the unsaved new
  assembly.

**So the effect is conservative but the words are wrong.** Each item affected is left behind, and none is made
wrongly. But two sentences can be untrue: *"… new part does not have"*, and *"its values changed"* where the cause was
unsaved or mismatched.

**Recommendation: fix now.** It is small and does not touch the SolidWorks evidence.
- *The change* (`update.py`):
  - `:3306`: `job = next((j for j in again.build if planetary.copy_of(c.gear)[0] in j.gear_ids), None)`;
  - in `_why_part_new`: `row = planetary.copy_of(gear)[0]`, and `row` in place of `gear` in its three
    `gear_ids` tests (`:3227`, `:3229`, `:3231`).
- *Checked in the scratch copy:* each copy gets 6 names and *"its Face width changed"*.
  `test_workbook_carry.py`, `test_swbuild_carry.py`, `test_workbook_update.py` and `test_workbook_user_record.py`:
  419 passed.
- *Tests it owes, on the fake:*
  - `carry_for` after Planet's Face width changes: each copy's `names` equal its job's `plan_features`, and its
    `why_new` is *"its Face width changed"*;
  - `_why_part_new` for a copy whose row is in `made_new` as `UNSAVED`, and as `MISMATCHED`, gives those phrases;
  - a carry end to end (gates set on 2026) with a user coincident on *Planet copy 2*'s Gear Axis and a user gear mate
    on a planet's Gear Axis, each made again on that copy's new Gear Axis, and the result naming neither as gone.
- *The evidence still stands for the fixed code.* `copy_of` returns any id without the copy word unchanged, and the
  changed lines run only for a part made new. In M9's fixture, on 2026 tonight and on 2024 now, the only parts made
  new are Sun and Aux, and the planets are reused, so every body those runs met takes exactly the same path.
- *Remaking by name on a gear part made new is measured on SolidWorks:* UserGear6 on Sun's Gear Axis was made again
  (log 1:1484, 1565). A copy takes that path with its own handle.
- No rerun is needed.

**Re-check of `d496cfd` (2026-11-18, at `d496cfd`).** I changed no code and started no SolidWorks; the targeted tests
ran in a `git archive` scratch copy, deleted after.

**Fit, and nothing must be fixed.**

- **The fix is as I gave it.** Both lookups now use the Gears row, `planetary.copy_of(id)[0]`: the job lookup in
  `carry_for`, and the `made_new` and job tests in `_why_part_new`.
- **The addition, `update.why_new_of`, is right.**
  - It keys each reason by body and also, with `setdefault`, by the planet's Gears row. That row is the id
    `StaysBehind.left` records W9a's features by.
  - The question (`_features_question`, through `carry_foresight`) and the result (`_parts_left`, through
    `carried_status`) now find a row such as *Planet* there. Before, they said the feature stays in a part
    *RangeBox_r2 does not use*, which was untrue.
  - The new sentence is true in each state that says it. All copies of a row share one part, so the row's reason is
    every copy's: *"Your PlanetPin stays in Gear_m1.25_N13, which Planet's new part replaces (its Face width changed)"*.
    With `UNSAVED` it says the unsaved reason with how to keep the part. A gear with no copies keys the same id twice
    to one reason. A part that is reused gives no reason, as before.
- **The tests pin.** At head the four carry and update test files and `test_findings.py` pass (581). The three new
  tests all fail with `7f91037`'s `src`. With only `why_new_of`'s row key taken out, two of them fail: the
  feature's reason, and the end-to-end carry.
- **The evidence stands.** M9's fixture on both versions makes only Sun and Aux new. Neither has the copy word, so
  `copy_of` returns each unchanged, and `why_new_of` returns the same dictionary as before for them. The planets are
  reused and give no reason. Every body those runs met, on 2026 tonight and in the 2024 demonstration running from
  `5aca9c1`, therefore takes the same path and gets the same words.
