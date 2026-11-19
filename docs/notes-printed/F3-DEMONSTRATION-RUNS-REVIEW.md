# Review of F3's SolidWorks demonstration runs (2026 34.1.1, 2024 32.5.0)

**Read at `ab998d3` on `printed`**:
- the five logs and their JSON (`probe/results/f3-demo-sw2026-20261118-{1,2,3}-*.log` and
  `probe/results/sw2024/f3-demo-sw2024-20261118-{1,2}-*.log`);
- the runner's two fixes, `75d27cf` and `771f492`;
- the run sections of `docs/notes-printed/F3-DEMONSTRATION.md`.

The write-up is held to the logs and to the code. No code was changed and SolidWorks was not run. Below, `26-1:`, `26-2:`,
`26-3:`, `24-1:` and `24-2:` are lines of the five logs.

**Verdict.** The D is shown sound across its range on both versions, and no probe is owed. Every Done-when item is shown
on both versions but one check in `built`. That FAIL is the app's, it is older than F3, and it is not F3's (§3). F3 can
close once the coordinator rules on it and the points of §5 are settled. Nothing here is a must-fix in F3's code.

## 1. Section by section, against the logs

**Every ok checked is a real reading against a value worked by the script.** No ok passes on an empty set. No STOP and
no What's Wrong box on either version; SolidWorks' notification box came up once per version, during a job, and is
exempt by ruling (26-2:466, 24-1:474).

**dshape** (26-1, 24-2:11-395), clean on both, 0 failed. Read from the facts lines of every state:
- **Volume**: each Update state's volume equals its from-scratch twin's to the last logged digit on both versions
  (2026 4983.795575580371 against its twin's, as built; 2024 4983.981521093568). The 2024 figures are uniformly
  0.186 mm³ over 2026's, as the write-up says.
- **Faces**: the round is one face of R = (D + a)/2 by `CylinderParams`, reaching −X, in all eleven D states and on
  both round-to-D Builds. The flat is one face at h on +X by `PlaneParams`. Nothing is in error. The Bore Sketch is
  status 3.
- **The chord link's own value**: SolidWorks' Equation Manager `Value` for `"Flat@Bore Sketch"` is the chord worked
  here exactly (5.3665631459994945 at D 8, a 0.2, F 7, on both versions), and `"Bore@Bore Sketch"` is R, both in mm.
  So SolidWorks evaluates the bracketed `2 * ( ( abs ( … ) ) ^ 0.5 )` as the app does: the precedence question behind
  the coordinator's bracket ruling is answered on both versions.
- **The range**: h went from 3.1 to 1.1 (Flat 7 → 5), to 0.25 R exactly (Flat 6.1 at D 10, a 0.4), to a flat 0.3 mm
  deep (Flat 9.7), to a press fit (a −0.1), and back. Each value step counted and set exactly its globals in one
  rebuild with no landing route. The two bound steps and the three structural steps were refused in A's and B's words
  with nothing sent (26-1:162, :172, :187, :190, :290).
- **The box facts** the review had made facts: `GetBox` is tight on these faces on both versions (padding 0; the
  round's greatest x is h; the flat's span is the chord to 1e-4). W9b's 0.24 mm padding is not met here. The tip lands
  number 20, the two nearest +X at ±8.98° (2026) and ±9.000° (2024): ruling 2's space on +X, read.

**No far-side solve, no sliver, no wrong branch anywhere.** The volume, the plane, the radius, the −X reach and the
links' own values each rule it out independently. **The D sketch is sound across its range on both versions; no probe
or follow-up round is owed.**

**allowance** (26-2:11-44, 24-2:398-427): fifteen parts each (spur, helical, herringbone, bevel, hub; default, typed,
machined). For each: the hole by its faces to 1e-4 mm (5.1, 4.95, 5.0; 5.1, 5.15, 5.0 ×3; 4.1, 4.125, 4.0), judged
round with no flat; the global as typed or 0.2, none machined; schema 4 or 1; each machined record equal to F3-0's pin.
Clean.

**print** (26-3:12-241, 24-2): each press judged whole by F2's `written`. From the STEP file itself: the D one cylinder
of 4.1, one plane face in the bore on x = h, the corners at x = h, the least vertex radius 4.1; the round no plane. The
list's bore lines word for word. Clean at `75d27cf` on 2026 and at `771f492` on 2024.

**built** (26-3:246-1040, 24-2):
- Coupon_F2 built by F2's code: schema 3, no F3 global. Opened with the switch on it counts 0 and shows *Bore as cut*
  8; an allowance typed is refused in B's words.
- F2's printed 12 : 1: four `.gear.json` at 3; the footer word for word as with the switch off; a quiet Update writes
  and marks nothing (26-3:387, 24-2:1331); G2's allowance structural with B's sentence (26-3:401, 24-2:1345).
- The switch-on 12 : 1: G2's 0.3 set in place, its hole 6.15 by its faces, nothing else touched or saved (26-3:455,
  24-2:1934); K11 naming `"Bore Allowance"` and `Gears!V3` (26-3:467, 24-2:1946).
- The machined 12 : 1 built before F3, typed Printed: Backlash 0.45/0.45/0.6/0.6 → 0.3, no F3 global in SolidWorks or
  on record, `.gear.json` below 4 (26-3:1038, 24-2:2517).
- **One FAIL on both** (26-3:347, 24-2:760): the quiet Update values' save flag. §3.

**hub** (26-2:2135-3026, 24-1): RangeBox_Fixed printed, its Hub D 8, a 0.2, Flat 7. Built by the app's Build: six parts,
turning, every sketch fully defined, no clash. In each of H, N and L: every body at its recorded frame (6.6e-10 at
worst), no mate in error, every gear free, RangeSlv at 55.5, 48 and 40.5 mm, every flag as recorded, and **no
interference in any mode** (26-2:3014-3021, 24-1:1754). The Hub's hole read as a D (26-2:3023, 24-1:1756). This is the
Done-when's item, shown on both versions.

**userwork**:
- 2026, run 3 at `75d27cf` (26-3:1042-1895): every check holds but the last.
  - The keyway is read after the open (26-3:1066).
  - Printed and one Update ok (26-3:1101).
  - Sun's D is structural; Build again… gives Sun the D.
  - The keyway is cut again; a quiet press records it (26-3:1480).
  - The in-place Update of Sun's allowance and Flat holds over the user's keyway and eight mates (26-3:1517-1519).
  - The bore mate is read on the 4.15 face by `mate_definition`, the arc one face (26-3:1523).
  - The last Build again… keeps 0.3 (ruling 1, 26-3:1891) and names UserBoreMate (26-3:1859, 1881). The app's
    sentence is in the status, 26-3:1866: *UserBoreMate was on a face of Sun, and Sun's part is new because its Part
    name changed, so it is not made again.*
- 2024, run 1 at `771f492`: clean, the fixed check holding (24-1:863-864).

**Does the write-up say anything the logs do not bear out? No.** Every line number I followed says what the note says.
Its statements about the masters and about writing nothing outside the run folders are marked as the runner's own,
outside the logs, and the loss of the first listing is said. Two places to read narrowly:
- The note's userwork sentence is the app's status line, not a log line of the script's own (26-3:1866).
- *the K11 refusal* on the switch-on 12 : 1 is of a **typed** cell. B's blank-cell words (*the allowance as built*)
  were not met live (§5).

## 2. The runner's script changes

Each was the script's fault, and none loosens a check. No tolerance moved in either commit (`BOX_TOL`, `VOLUME_TOL`,
`RADIUS_TOL`, `FLAT_TOL`, `STEP_TOL` unchanged).

- **The STEP reader's planes** (26-2:162, :271: 41 and 40 planes). Each tooth space's radial flank lies on a plane
  through the axis, so a plane's distance from the axis cannot place it in the bore. Script. A plane face now counts
  as in the bore when every vertex its bounds reach is within reach, and a square plane face whose bounds reach
  nothing fails. Stricter, not looser. The self-check now carries forty radial flanks.
- **The "machined" 12 : 1 built printed** (26-2:1574). W9a's `spec_reducer` keeps the fixture's blank Process, and a
  blank on a workbook with no record is Printed by D11 (B). Script. It now says Machined, and 26-3:479 and 24-2:1958
  read machined.
- **The structural part among the changed parts** (26-2:961). `update._part` returns a structural part as changed with
  its sentence beside it, by W4's design, and `printout.workbook_print` relies on that. Script. The check now requires
  G2's part to be the one changed part: stricter than *none*.
- **The quiet Update values' message**: the same five conjuncts, now said apart. Not loosened.
- **The keyway read before the open**: `features_of` reads an open part. Script.
- **The bore mate before the in-place Update.** K2 (ISSUE-1-PLAN, accepted by the user) refuses an Update that puts
  back a gear holding a user mate to its own faces or planes. The app did exactly that, before any write: the D still
  read 4.1 and 3.1 afterwards (26-2:3490, 3498). The script expected otherwise because PLAN-PRINTED §2.8 says such a
  mate *is re-solved by those puts* (§4). Moving the mate after the Update is not a loosening: the app is right, and
  its refusal on a D-face mate was read live once (26-2:3490, logged as a FAIL by the old check).
- **The carry check** (26-3:1892). K5, W9D-INTERFACES §4.4: a face of an app part made new is never re-found but
  named. Swbuild's M1 walk reads a face's axis on such a part for a gear mate only (`swbuild.py` near :8030), so a
  concentric's face is *a face of Sun* (`where` ""). Script. My own review's S3 assumed a remake, which was wrong.
  The fixed check (`771f492`) requires the mate named `part new`, a face, for the Part name, nothing else named, and
  the eight made again in no error: stricter on what the app says, and true to K5.

## 3. The FAIL left: the quiet Update values turns the part's save flag on

**What marks the part.** `swbuild.update_variables` (`swbuild.py:1481-1510`) runs `sw.detect_trig_units()` (:1499)
before it knows whether anything changes. `Session.detect_trig_units` (`swcom.py:1475-1487`) adds the equation
`"Gear Generator Trig Check"= sin ( 90 )` with `Add2`, reads its `Value` and `Delete`s it. Only then does
`planned_changes` find nothing and the function return (:1508). The runner's guess is right, and it is not a guess: the
code says it, and so do three notes in the app itself:
- `swbuild.py:3047-3050`: *on SolidWorks 2026 (34.0.0, gearbox_smoke 2026-11-13) that alone left each document marked
  modified*;
- `swbuild.py:4266-4268`: W4 review S2, *measuring the units alone left every part marked modified*;
- `ui_text.py:3238`.

The workbook's Update was changed then to read the units from the equations' text and measure nothing for a document
that already holds its values. The strip's Update values never was.

**Before F3? Yes, since the strip's Update values was written.** The same lines are at F2's close (`2656479`:
`begin_build`, `detect_trig_units`, then `if not changes`), at `workbook`'s head (`4714176`), at `w9d`, and back to
`0c48a61` (2026-09-14) by `git log -L`. F3 did not add it, and nothing of F3's rule rests on it: nothing is written,
the record and the `.gear.json` are unchanged, and saving the part would store the same globals.

**Does anything the app tells the user become untrue? Yes, one sentence, later.**
- *Nothing to update: every value in Coupon_F2.SLDPRT already matches the form.* is still true.
- But **Print files** refuses a part whose own save flag is on (`printout.MODIFIED`, `swbuild.print_parts`' start). After
  a quiet Update values it says *Print files wrote nothing: Coupon_F2 is changed in SolidWorks and not saved; save it,
  or close it without saving, then print.* (`ui_text.py:6890-6892`). *Changed* is then untrue.
- SolidWorks also asks to save on close.

**The fix** (pre-F3 code, one function): in `update_variables`, read `sw.equations()` first and plan the changes in both
units, as `update_gearbox`'s check does (`_held_unit`). When the document already holds every global in one unit's
form, and evaluates them as that unit would, return *nothing to update* with that unit and add no equation. Measure
the units only when something is to be set, since the document is about to change anyway. One fake test: a quiet
Update values makes no `add_global_variable` and no `Delete`, and turns no save flag.

**Recommended ruling**: not F3's, and not a reason to hold F3's close. Either fix it now as a small follow-on, after
which `built`'s coupon step passes as written (it is not to be loosened), or close F3 with it said as a known pre-F3
caveat and fix it separately. If it is fixed before F3 closes, rerun `built` on one version to show it.

## 4. The runner's other points

- **PLAN-PRINTED §2.8 (`docs/PLAN-PRINTED.md:2635-2636`, and the *0.035 mm* line after it)** says a user's mate on an app
  gear's face *is re-solved by those puts*. K2, the user's accepted rule, refuses an Update over *a mate to a gear's own
  faces or planes* before any write, named, and the app does: 26-2:3490. The plan's sentence is wrong. Correct it in
  the plan's record (a user's face mate on a gear Update puts back is refused by K2; lock the component to the gear
  instead). No code.
- **PLAN-PRINTED §4.4's *W9d's word "bore" … still names a printed bore*** is moot as the code stands. "bore" is said only
  for a face read coaxial (`swbuild.py:7600-7605`), a face on a part made new is read so only for a gear mate (M1), and
  a gear mate's coaxial face goes to §4.3's Gear Axis rule first. So "bore" is unreachable live, before F3 as after.
  F3's `_bore_mm` change is right and harmless, but no user will see the word. Worth a line in the plan's record; a W9d
  matter, not F3's.
- **2026's userwork at `771f492`.** The fix changed only the last check; every SolidWorks action is the same as run 3's.
  Run 3's log bears out each conjunct of the new check: UserBoreMate the only mate named, `part new` (26-3:1859, 1881),
  for the Part name, on a face (26-3:1866), and the eight made again (26-3:1873-1880). Only the eight's mate codes after
  the carry are not logged by run 3 as the new check reads them. 2024 ran the fixed check clean. So the facts are not in
  doubt, but the house rule (*after a fix only the affected sections are rerun*) owes a clean 2026 `userwork`.
  **Recommended: rerun `userwork` alone on 2026** in a fresh session (about 20 minutes), with `built` beside it if the
  save-flag fix is made first. The coordinator may instead rule run 3's log sufficient, with the reason above.
- **F3-0's pins under Windows' `python.exe`.** `strip_print` hashes `repr(plan)` and `describe(op, trig)`, which print
  every float to its last bit. Two dimension-label coordinates come from `sin`/`cos` and differ by one ulp between
  Linux's libm and the Windows CRT (the note's figures). Two things follow:
  - **The pins are bit-exact by construction.** They hold wherever the suite runs, which is Linux. They fail only where
    the demonstration's self-check runs them on Windows. `SIDECARS` (JSON floats of derived values) carries the same
    exposure and matched on Windows by luck.
  - **To hold on both without loosening them**: keep the hashes as the commit-to-commit check on Linux, and compare
    across platforms on the content, not the hash. Store each pinned print as data, generated on Linux at a commit
    where the existing hash still holds, which proves the data is the pinned content. Then compare strings exactly and
    floats with `math.isclose(rel_tol=1e-12, abs_tol=1e-9)`. That is millions of times finer than any change a plan
    could mean, and blind only to libm's last bit. Re-hashing floats rounded to fewer digits would also mostly work,
    but a value that straddles a rounding boundary can still flip, so it is not a guarantee.
  - Until then, the demonstration's Windows self-check should mark the `STRIP` comparison Linux-only, said in its line,
    and keep `SIDECARS`.
- **The same weakness elsewhere.**
  - F1's hashed pins are this same `STRIP`/`SIDECARS` in `tests/test_printed_rule.py`: the same exposure.
  - F2 added no hashed pin. Its fixture comparisons compare floats exactly in places, also Linux-only by construction.
  - F4 (branch `f4`, read-only, `tests/test_printed_rule.py` `RESULTS`) hashes the Results sheet's rows, whose floats
    the app rounds to six places (e.g. 517.857143), and diagnostics rounded by `_num`. The exposure is only a value
    within an ulp of a rounding boundary: far smaller, but not nil.
  - The W-era hashes `W7_PUT_BACK_LOG`, `W9A_PUT_BACK_LOG` (`repr` of frames) and `test_workbook_planetary`'s fingerprint
    (`float.hex`, the most exact) are Linux-only the same way. None is run on Windows today.
- **The masters' "before" hashes.** The between and after listings match, and no master file is newer than
  2026-11-17. A save by SolidWorks would move the file's time, so the 2026 run is covered by the times and the 2024
  run by the hashes. Acceptable as said. For the next run, keep the listing beside the run folder, not in a scratch
  folder.

## 5. Is F3 done by its Done-when?

**Shown on both versions**: the STEP-read hole to 0.01 mm; the structural refusals with their sentences; the hub
gearbox turning with no interference; a gearbox built before F3 unchanged in its bore; and these, which the
Done-when names:
- `dshape`'s every value within 0.1 % of its twin (equal in fact);
- every sketch fully defined.

F3-0's pins, the packages, the suite (5390 at `262c0f7`), the README, `design/UI-DESIGN.md` and the boards are in.

**Still owed, in order:**
1. **The coordinator's ruling on the save flag (§3)**: fix now and rerun `built` on one version, or a pre-F3 caveat for
   F3's close with the fix separate.
2. **2026 `userwork` at `771f492`** (or later): one fresh session, alone, with `built` if the save-flag fix is made. Or a
   ruling that run 3's log suffices.
3. **The plan's record**: §2.8's re-solve sentence and its *0.035 mm* line corrected to K2; §4.4's "bore" said as
   unreachable (W9d's M1); this review's findings and the runs in its change record.
4. **The pins' Windows ruling** (§4): Linux-only, said in the self-check, or the data-and-tolerance comparison.
   Not F3's Done-when, but the self-check line should say which.
5. **PNG renders** of the boards (the Mac's Chrome).
6. **The hand-over** notes.

**Unmeasured, and to be said so at F3's close:**
- the carry's `COAXIAL_FACE_READ` on a D's partial cylinder (never read, and by W9d's M1 never read for a non-gear mate);
- K2 over a user mate on a D face (read once, 2026 run 2, under the old check);
- K11's blank-cell words (*the allowance as built*) live (only a typed cell met);
- K3 with a user feature in the bore;
- a D on a helical gear, its angle at the section plane;
- a D printed and fitted on a shaft;
- the allowance's figure from the user's coupons (V1);
- a What's Wrong outliving a job, and either memory floor's STOP.
