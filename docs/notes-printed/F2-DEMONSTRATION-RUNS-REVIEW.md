# Review of F2's demonstration runs on SolidWorks 2026 and 2024

Read at `9c1275f` on `printed`: the run sections of `docs/notes-printed/F2-DEMONSTRATION.md` held to the committed logs and JSONs.

| Log | Lines | Cited as |
|---|---|---|
| `probe/results/f2-demo-sw2026-20261118-1-gates-form-workbook-refusals-userwork-clean.log` | 1674 | *26:* |
| `probe/results/sw2024/f2-demo-sw2024-20261118-1-userwork-clean.log` | 143 | *1:* |
| `probe/results/sw2024/f2-demo-sw2024-20261118-2-gates-form-workbook-refusals-clean.log` | 1554 | *2:* |

The JSONs are `f2-demo-20261118-114919.json`, `…-120326.json` and `…-121309.json`. The script that ran is `b3fe4a1`'s,
reviewed in `F2-DEMONSTRATION-REVIEW.md` §9. Nothing was run here, and no code changed.

**Verdict.** Both runs are clean, and the write-up is faithful to its logs, with one small misattribution of memory
(§4). F2's SolidWorks demonstration meets its row of the Done-when. With this review **F2 is done by its own Done-when,
short of the user's step (§3.2)**. There is no must-fix. The herringbone may be lifted from the size check's skipped
kinds (§3).

## 1. Section by section

**The counts are as the write-up gives them.**

| Run | ok | FAIL | STOP | noted | done line |
|---|---|---|---|---|---|
| 26 | 336 | 0 | 0 | 1 (the herringbone verdict) | 26:1674 |
| 1 | 55 | 0 | 0 | 0 | 1:143 |
| 2 | 282 | 0 | 0 | 2 (the herringbone verdict; 2024's What's Wrong) | 2:1554 |

The snapshot is `b3fe4a1` (26:2). The findings read the review's values and EXTENT_MEASURED True, and the route is `walk`
(26:11-17).

Every line the write-up cites that I read says what it is cited for. I read:

- the gates: 26:134-173;
- the coupon's presses: 26:273-300;
- the helical and the herringbone: 26:409-548;
- workbook: 26:1065, 26:1100-1211;
- refusals: 26:1317-1537;
- userwork: 26:1545-1665, 1:12-143;
- 2024's herringbone and bore Update: 2:7, 2:541-547, 2:1495-1510.

**Each ok is a real reading over the items it names.**

- **Writes.** Every ok on a write rests on the job's own result, the press folder's listing byte for byte, both readings
  of each file, the list, the documents' read and the calls by member.
  - The calls lines show what the job called, so "nothing opened or activated" is read, not assumed: `{'SaveAs': 4}` at
    26:1118 and 26:1169; `{'ActivateDoc3': 4, 'OpenDoc6': 4, 'CloseDoc': 4, 'SaveAs': 4}` at 26:1189 and 26:1208.
  - The "job's calls by member" lines (26:1154, 26:1408, 26:1518, 26:1528) show the reads were really made:
    - `Equation` ×120, `GetErrorCode2` ×100 to 102 and `Visible` ×3 or 4 where parts were found;
    - only the walk, `GetSaveFlag` and `GetType` for a set refused as LIGHTWEIGHT before any read.
- **Refusals.** Every refusal's ok is the app's own status compared word for word, with the press folder, the
  SolidWorks files, the documents and the calls each read as unchanged.

**Two readings are inferred, not logged.** The write-up states both as made; both inferences hold.

- **G1 "open in its own window, not active" at the clean write (26:1152-1169).** No line reads G1's Visible at that
  press.
  - It rests on 26:1150: the window was left open by the put-back, the same window 26:1136 read Visible True.
  - It rests also on the documents' read before and after being equal.
  - SaveAs ×4 with no ActivateDoc3 shows it was written by its object.
- **The open-beside press (26:1191-1211).** The parts are not re-read Visible False just before it. It is the calls
  that show the path was the fallback: four OpenDoc6 and four CloseDoc with the assembly open. A part not found while
  an assembly is open would have been refused LIGHTWEIGHT, so these parts were found as components.

**What the write-up says that the logs do not bear.** Both are already labelled as the runner's statements, as they
should be:

- the masters' hashes;
- "nothing written outside the run folder".

The process lists, `taskkill` and the session start are the runner's account too.

The one inexact sentence is the 2024 memory one (§4).

## 2. F2's Done-when (PLAN-PRINTED §3.3), row by row

| Done when | Evidence | Met |
|---|---|---|
| §3.0's span on the form for a printed involute external gear, with its Measured line, held by tests | `tests/test_span.py`, `test_ui_text.py`, `test_print_form.py`; on SolidWorks the coupon's row 11.209 against the script's 11.2088 and package A's (26:273, 2:272), the helical's 15.097 (26:409, 2:408) | yes |
| The interface reviewed | `F2-0-REVIEW.md` | yes |
| The probe run on 2026 and 2024 and reviewed; its findings set with pins; that commit reviewed | `F2-PROBES.md`, `F2-PROBES-REVIEW.md`; `ae42722`; `F2-REVIEW.md` §10 (flips fail the pins) | yes |
| Print files from the form and the window against the fake: each refusal said, files checked, the list written, the documents left as they were | `test_printout.py`, `test_swbuild_print.py`, `test_print_form.py`, `test_print_window.py` | yes |
| Boards, UI-DESIGN, README updated | `8328263`, `2d6d288`, `19cff09`, `843d794` (the PNG renders not redone, as since F1) | yes |
| The demonstration run on 2026 and 2024, every section clean, reviewed | the logs above, 0 FAIL, 0 STOP; this review | yes |
| The coupons exported, and the STEP files open in the user's Bambu Studio | the user's step (§3.2 step 2, U5) | **owed** |
| §3.2's measurements in its table; D3's number and F3's allowance set from them, on the user's word | the user's step (U1 to U4) | **owed** |
| The stage's result reviewed by a subagent, its should-fixes done | `F2-REVIEW.md` and its re-check §10 | yes |

**The demonstration's own items (§3.3), against the logs.**

- **The form.**
  - A printed spur built and pressed (26:276-286, 2:278-285):
    - its file checked by the app (fact `checked`) and by the script (AP203, mm, one closed solid, radius and face);
    - path, title and flag unchanged, the active document as it was, the list as said.
  - One global changed and unsaved, refused (26:1317, 2:1318); saved, refused (26:1325, 2:1326).
  - After **Update values** (26:1332, 2:1333), a press writes a folder of its own (26:1337-1344, 2:1338). A second
    press makes a second folder (26:289-300).
- **The workbook.**
  - The printed 12 : 1 built (26:1065, 2:1059).
  - The component press writes every part and the list with counts (26:1105-1120, 2:1106-1121).
  - A Gears cell edited is refused until Update: CHANGES_ON_UPDATE (26:1492; userwork 26:1614, 1:84).
  - Updated and not saved, refused: UNSAVED_MARK (26:1511, 26:1634, 1:104).
  - Saved, a second folder: userwork 26:1643-1658, 1:113-128. On the 12 : 1 the same save leads to FEATURE_IN_ERROR,
    by design (the keyway falls in the bore).

**The items the reviews asked the demonstration to show.**

- **The job's reads of globals on a part not active or open only in an assembly.**
  - G2, a component only (Visible False, 26:1124): GLOBALS_DIFFER with *16 where its record says 15* (26:1127, 2:1128).
  - G1 behind the user's part: MODIFIED (26:1139, 2:1140), then GLOBALS_DIFFER (26:1146, 2:1147).
  - In each, `Equation` and `Value` ×120 in the job's calls.
  - **This was the one proof that `equations()` reads live off a non-active document, and it holds on both versions.**
- **Feature errors.** FEATURE_IN_ERROR on G1, not active, read without activation, naming *User Keyway* as the script
  read it (26:1517-1523, 2:1525-1528).
  - G1 was then open in its own window: the keyway and the Update opened it, and no line reads it Visible False.
  - So the feature-error read is shown positively on a background part. On a component-only part it is shown only by
    every clean component press, where the same reads found nothing.
  - It is the same call on the same kind of document object as the equations read shown on G2. A caveat, not a gap
    that needs a run.
- **The export of a component-only part through the job's own handle.** All four with Visible False read first
  (26:1100, 2:1101), and the job calling `SaveAs` ×4 and nothing else watched (26:1118, 2 the same). With
  `GetOpenDocumentByName` counted at 0, the handle was the walk's.
- **The open-beside fallback.** `STEP_EXPORT_FROM_COMPONENT` patched False in the process (26:1191, put back 1209). Four
  OpenDoc6, four CloseDoc and four SaveAs (26:1208); every component read by name and resolved after (26:1211); the
  same on 2024 (2:1192-1212).
- **Every part of the 12 : 1 passing the size check.**
  - The app's fact `checked` and the script's reading of every file (26:1108-1115, 2:1109-1116).
  - The farthest vertex past d_a/2: G1 1.19e-3, G2 5.1e-5, G3 1.57e-3, OutputGear 7.6e-5 mm on 2026, 0 on 2024. Past
    the face: 2e-5 to 3e-5 on 2026, 8e-6 on 2024.
  - All ten times under the 0.01 mm tolerance.
- **Each refusal word for word with nothing exported.** In the logs, each said word for word, with no press folder, no
  SolidWorks file changed, the documents the same, and no watched call in the job:
  - MODIFIED, GLOBALS_DIFFER, NO_FOLDER (the folder not made, 26:1367), NO_RECORD;
  - LIGHTWEIGHT (state 1 kept after, 26:1404), suppressed (the same sentence, 26:1411);
  - NEW_REVISION naming OutputGear alone (26:1461-1463, the structural sentence *OutputGear (G4): Flank changed from
    involute to arcs…*);
  - CHANGES_ON_UPDATE, UNSAVED_MARK, FEATURE_IN_ERROR;
  - LIGHTWEIGHT for parts simply closed (26:1530);
  - NOT_A_PART naming the user's assembly (26:1537);
  - the gate's three forms (26:141-173).
  
  All the same on 2024.
- **The user's work on the setup.master copy neither exported nor touched** (26:1659-1665, 1:129-135):
  - the press folder holds the five parts and the list alone;
  - no Sprocket or Housing file;
  - the record unchanged;
  - the user's part files unchanged by sha256;
  - every document, flag and window the same with RangeBox active;
  - the five user components there;
  - all eight mates joining what they joined;
  - the User Keyway at code 0;
  - the job calling SaveAs ×5 alone.

## 3. The herringbone

The size reading held on both versions, judged by the script against d_a/2 and the face worked apart from the app:

| | Radius | d_a/2 | Along Z | Lines |
|---|---|---|---|---|
| 2026 | 22.70552360820168 | 22.70552360820166 | 20.0 | 26:547-548, JSON `form.herringbone` |
| 2024 | 22.705523608201677 | 22.70552360820166 | 20.0 | 2:546-547 |

Both agree to about 2e-14 mm. Both files are AP203, millimetres, one closed solid with 480 vertices (26:542, 2:541).
The spur parts on 2026 overshoot d_a/2 by up to 1.6e-3 mm; the helical and herringbone tips land on it to 4e-7 mm on
both versions.

**Recommendation: lift "herringbone" from `printout.EXTENT_SKIPPED`.**

- **Pin it** in `findings.py`'s `EXTENT_MEASURED` comment and in `tests/test_findings.py`, to 26:542, 26:547-548, 2:541 and
  2:546-547, as the probe's lines are pinned.
- **Caveat:** measured on one gear only, printed, m_n 2, z 20, β 15°, face 20, **no groove**, unshifted, built from the
  form.
  - A grooved herringbone is not measured. The groove cuts to the root inside the face, so it should change neither the
    outermost radius nor the axial extent. A slip there would show as a FILE_CHECK EXTENT refusal, the safe side.
  - Spur and helical rest on as few gears.
- **The change touches four places** in one commit:
  - `printout.EXTENT_SKIPPED` and `extent_skipped` (B);
  - `ui_text.PRINT_SIZE_SKIPPED`'s "herringbone" entry (C), which `probe/f2_demonstration.py`'s self-check holds equal to
    `EXTENT_SKIPPED`, so its `SIZE_WORDS` must change with it or the script's self-check fails;
  - the tests that pin the skip;
  - the findings comment.
- **No SolidWorks rerun is needed for it:** the herringbone's size was judged by the script on both versions, and the
  app's check is the same arithmetic.

## 4. What differs between the versions

Each difference below is a caveat, not a fault.

- **The tip vertices.**
  - 2026's spur files reach past d_a/2 by up to 1.57e-3 mm (G3; the coupon and G1 1.19e-3; Sun 9.2e-4; the Planet
    8.4e-4), and past the face by 2e-5 to 3.5e-5 mm.
  - 2024's land on d_a/2 to 1e-6, and pass the face by 8e-6 to 9e-6.
  - On both, the helical and the herringbone land on d_a/2 to 4e-7.
  - The largest, 1.57e-3, is a sixth of the 0.01 mm tolerance. F2-PROBES-REVIEW's caution about larger gears is
    answered for z up to 68: the overshoot is largest on the small gears, not the large ones.
- **Vertex counts.** Some 2024 files hold two or four more vertices (the coupon 346 against 344, G2 1162 against 1160,
  OutputGear 876 against 874, the ring 940 against 936). The tessellation of a face's edges differs; the solids pass
  every check alike.
- **The What's Wrong box on 2024**, in the app's bore Update (not in Print files):
  - up 9.55 s into the job with the worker in `ActivateDoc3`, gone 1.01 s later by itself, nothing closing it, none up
    at the end and the frame enabled (2:1499-1503);
  - the Update's status adds its clause (2:1507);
  - the 2024 rule read it as a fact (2:7). It is W9a's box-k3 measurement again, and outside F2's code.
- **Times and memory.**
  - 2024 is slower: RangeBox's Update 296.3 s against 172.7 s.
  - SolidWorks 2024's private memory reached 6.21 GB in run 1 and 7.18 GB in run 2, against 2026's 1.61 GB. Free
    memory stayed over 7.9 GB.
  - The write-up's *7.13 to 7.18 GB … after the 12 : 1's quiet Update (from 2.50 at workbook's end)*
    (`F2-DEMONSTRATION.md:599`) gives the quiet Update more than it did. The log has 5.51 GB already *before* the quiet
    Update (2:1422), and 7.13 after it (2:1423). The rise from 2.50 (2:1215) came over refusals' form presses, the
    copy's open and the lightweight and suppressed states.
  - Nothing in the Print files jobs is implicated: their calls are reads and SaveAs. A wording fix to the note, not a
    finding (should-fix S1).

## 5. Is F2 done short of the user's step?

**Yes.** Every row of §3.3's Done-when that does not need the user is met, this review included. There is no must-fix.

**Still owed:**

1. **The user's step (§3.2)**:
   - the coupons built and exported;
   - Bambu Studio opening the STEP files (U5);
   - the span and bore measurements in §3.2's table;
   - from them, on the user's word: D3's printed backlash (U4, including the choice above 0.3 mm) and F3's bore
     allowance.
2. **The herringbone ruling** (§3), and if taken, its one commit with its pins.
3. **Should-fix S1:** `F2-DEMONSTRATION.md:599`'s memory sentence.
4. **Standing caveats carried, none blocking:**
   - the boards' PNG renders, not redone since F1;
   - `GetOpenDocumentByName` built but unused (the walk is the route);
   - LIGHTWEIGHT inferred, not read (worded true of all its cases);
   - the feature-error read on a component-only part shown only by clean reads (§2).
5. **The plan's record of the stage's close:** a *Changes after F2's demonstration* section in PLAN-PRINTED, and the
   stage marked closed but for §3.2, as F1's close was.

**What F3 needs from the user's step.**

- **The bore allowance** (§4.1): "blank is the figure §3.2 found (0.2 mm on the diameter until then)". It is the coupon
  graded (c) from both faces, the bed face deciding.
- **The user's shaft size (U1):** whether the coupons are module 1.5 or 2.
- **Whether a D-flat's flat** fits as the round does. The flat takes half the allowance by rule; §3.2 says a round bore
  says nothing about the D-flat, which is measured when F3 builds one.

F3 can be **built** before the measurements, on the 0.2 mm placeholder: the global, the form row and Gears column, the
D-flat sketch, the schema 12 and sidecar 4 records, W9's K11 and carry hooks, its SolidWorks runs. Only the allowance's
default waits for the number, a one-line change with its pins.

- **D3's printed backlash (U4)** changes F1's `spur.PRINTED_BACKLASH` and its equation, not F3.
- **The edge chamfer (D9)** is planned only if §3.2's prints show the slicer's elephant-foot setting is not enough.

**F4 does not depend on the user's step.**

- It is pure maths on the app's own outline (backlash and shift included) against ISO 6336-3, checked against the
  standard before a line is written, with an *Allowable stress* on the Box.
- §3.2 measures no strength. A changed D3 backlash would change F4's figures through the outline, not its code.
- F4 can go ahead now, in parallel with F3, as both plans allow.
