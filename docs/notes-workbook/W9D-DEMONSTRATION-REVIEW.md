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
