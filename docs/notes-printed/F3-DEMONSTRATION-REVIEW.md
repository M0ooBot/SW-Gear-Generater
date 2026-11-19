# Review of F3's SolidWorks demonstration, before its first run

**Read at `11f2a25` on `printed`**: `probe/f3_demonstration.py` and `docs/notes-printed/F3-DEMONSTRATION.md` (`fb5346b`), against
PLAN-PRINTED §4.6 (*The SolidWorks demonstration*, *Done when*), the app at `262c0f7`/`fd7da8c`, and the scripts it leans on
(W9a's harness, F2's live part, W9b's, W9c's and W9d's). No SolidWorks, no Excel, no code changed. **The self-check, run
here: 15 checks, 0 failed** (Tk present, the switch on).

**Verdict: not yet fit for its first run on SolidWorks 2026.** Two must-fix points. **M1:** the D is judged partly
on `GetBox` with a 0.1 mm tolerance, where W9b measured SolidWorks padding a face's box by 0.24 mm, so every D state
would likely FAIL falsely. **M2:** the Done-when's hub gearbox is not shown. Both are small. Every other judgement is
a real reading against a value worked here, and none passes on an empty set.

## 1. Against the Done-when

| Done-when (§4.6) | Shown by | Holds? |
|---|---|---|
| `dshape`'s every value within 0.1 % by volume of its twin | `dshape`: 9 value states and 2 Builds, each against a twin built from scratch (`twin`, `volume_judged`) | yes |
| every sketch fully defined | `dshape` reads `GetConstrainedStatus` of the Bore Sketch at every state | **partly**: `allowance`, `print`, the twins and the gearbox builds judge `result.ok`, and `swbuild.build` puts an under-defined sketch in `result.checks`, not `failures` (`swbuild.py:1188-1195`), so `ok` passes it (S2) |
| the STEP-read hole to 0.01 mm | `print`, `step_bore_judged` on the file's own ADVANCED_FACEs and VERTEX_POINTs | yes |
| the structural refusals with their sentences | `dshape` (the allowance to 0, Drive both ways, on the strip), `built-f2` (none to some, in the window) | yes |
| **the hub gearbox turning with no interference** | nothing | **no (M2)** |
| a gearbox built before F3 unchanged in its bore | `built-f2`: the printed 12 : 1 (bores 8, 12, 12, 16) built with the switch off, read with it on, a quiet Update writing nothing | yes |

The other two items the author lists as not shown:
- **A herringbone with an allowance** is named by the plan's `kinds`. It is three parts more in `allowance` (about a
  minute): add it (S5).
- **The bevel's D-flat refusal** is A's diagnostic, made before any SolidWorks call. SolidWorks has nothing to show;
  leaving it to A's tests is right.

## 2. dshape, the probe's stand-in

**Does the face read tell the 278° D from a far-side solve? Yes, without the box readings.** The candidates:
- The flat reflected to x = −h, either arc: `PlaneParams`' point is at −h, so *not at h on +X* (exact, 1e-4 mm).
- The minor arc (the sliver) at +h: the cylinder's box does not reach −X. The volume is about 7 % off its twin (the hole
  some 3 mm² against 49).
- A wrong chord, which is how SolidWorks taking `^` and `*` otherwise would show: the flat's plane is off h.
- A wrong radius: `CylinderParams`.

Those readings are exact or one-sided. The box readings are not:

- **M1, `probe/f3_demonstration.py:327` and `:333` (and `:109`).** `BOX_TOL = 0.1` mm, but SolidWorks pads `IFace2.GetBox`:
  W9b measured 0.240284 mm at each end of a bore (`W9B-DEMONSTRATION.md:194`; the W9c runs' logs say the same). Two
  checks would then fail on a correct D:
  - the round's box `box[3] > h + 0.1`: the arc's greatest x is h exactly, at its ends, so a padded box exceeds it;
  - the flat's span along Y against the chord to 0.2 mm: padded at both ends, about 0.48 over.

  The check that the round reaches −X is safe, since padding only widens the box. **Fix**: log the two as facts
  (with the padding measured, as W9b logs it), or give them a tolerance clear of it (say 1 mm). The far side stays
  caught by the plane, the radius, the −X reach and the volume.
- **`lands_judged` (`:338-355`), same root.** The count is sound. A cut pattern of spaces through the blank's outer
  cylinder leaves one partial cylinder per tooth, coaxial at d_a/2: 20 for DShape, 29 for Sun. But the ±half-pitch
  angles are read from box centres of partial cylinders, and no run has read `GetBox` on a partial face. If SolidWorks
  gives a partial cylinder a loose box (the whole circle's, as some kernels do), every centre is near the axis and
  every state FAILs falsely. Ruling 2's angle is not in the Done-when, and the build fixes it, not the Update. For the
  first run, keep the count judged and log the angles as a fact; judge them once a log shows the boxes are tight.
  (Part of M1.)
- **A split arc, S1, `:316`, `:469`, `:1733`.** If SolidWorks or the STEP writer makes the 278° arc two faces,
  `bore_judged` says *2 cylinders in the D, not one*, `step_bore_judged` likewise, and `bore_mate` makes no mate
  (`len(mine) != 1`). All three are false FAILs. A native extrude of one sketch arc is very likely one face, but it
  costs little to accept several coaxial faces all at R whose boxes together reach −X, with the count logged as a fact.
  For `bore_mate`, pick the first.
- **The chord link: read back and evaluated, yes.** `link_judged` takes `"Flat@Bore Sketch"` from the Equation Manager
  by name. It must be the only one, equal to the app's `chord_expression` text with spaces aside, with no `sqr`, and,
  evaluated by the app's own evaluator on the globals SolidWorks holds, equal to the chord worked here to 1e-6 mm.
  `"Bore@Bore Sketch"` is likewise held to R (to D + a on a round). What is not judged is SolidWorks' own evaluation,
  the equation's `Value`, which is logged with its unit unsure. The flat's plane at h stands for it. Judging the
  `Value` against the chord in either mm or m would make it a direct reading (S4).
- The steps themselves are right:
  - Flat 6.1 at D 10, a 0.4 puts h at 1.3 = 0.25 R, inside A's 1e-9.
  - Flat 9.7 puts the flat 0.3 mm deep at the bound.
  - Flat 7 → 5 moves h from 3.1 to 1.1, the step a far-side solve would show on.
  - Each refused step reads the part's globals and `.gear.json` before and after.
  - Each value step holds the strip's count and `result.changed` to exactly the globals changed, with no landing route.

**Rebuild errors.** A D that fails to solve rather than solving wrong raises SolidWorks' What's Wrong. On 2026 that is
the STOP, by the house rule, and it ends the run with `allowance` to `userwork` unrun. The 2026 command runs all five
in one invocation. Run `dshape` alone first (S7).

## 3. The two departures

**(a) built.** The script is right, by the plan and by B's code:
- §4.4: *a part without the global (built before F3, …): none to some is structural, refused by Update with its
  sentence, made new by Build again…*.
- `swbuild.structural_change` reads *has an allowance* from the part's globals, which a pre-F3 part lacks.
- So the in-place change and K11 can only be shown on a 12 : 1 whose parts hold `"Bore Allowance"`, the one built with
  the switch on. The script does that, and also shows the refusal on the pre-F3 one: both halves of §4.4.

The sentence the user meets is true: *Gear_m1.5_N68_P (G2): A bore allowance cannot be added to or taken out of a built
part through its values; build it again as a new part.*, with Build again… offered. It is useful enough, since it says
what to do. It does not say why to someone who built last week (their part was built with none), nor that clearing the
cell keeps the hole as built. A wording like *G2's part was built with no bore allowance, so one cannot be added
through its values: build it again as a new part, or clear the cell to keep the hole as built* would serve better.
That is a words change for after the run, not for this script (S8).

**(b) userwork: sound.**
- setup.master's rows leave Bore blank, so Sun has no bore. Typing one is *a bore appears*, structural, and Build
  again… is the only way.
- The in-place Update is then made on the part that Build again made, which holds both globals. That is §4.4's
  *a part with the global: a value, set in place*, with the user's keyway and mates read before and after.
- The last Build again… (Part name changed, allowance cleared) is ruling 1 with the carry.
- The keyway (Ø3 at (5, 0)) leaves 0.4 mm of material to the flat at h 3.1 and 0.15 mm at h 3.35 after the in-place
  step. It never cuts the D, so it cannot split the arc. Worth a fact line; not a fault.

What `userwork` cannot show is the plan's *a copy of setup.master with Printed typed: nothing written for the bore*,
because none of its parts has a bore: the claim is empty there. `built-f2` covers *a gearbox built before F3 unchanged
in its bore* on printed parts. The live counterpart of guard 4 is still missing: a machined gearbox with bores, built
before F3, typed Printed, whose Update writes Backlash and no `"Bore Allowance"`. A machined 12 : 1 built with the switch
off, then Printed and one Update, adds it in about 3 minutes (S6).

## 4. userwork's first live readings

- **The concentric on the D's partial cylinder** (`bore_mate`). Sun's face is chosen by radius alone (4.1 to 1e-4, and
  it must be the only one), and Sprocket-4's at 5. `AddMate5` is type 1, concentric, through W9c's `raw_mate` and
  `select_face` as W9d's fixture made its face mates. It is then read on in every mode and in no error. A mate SolidWorks
  would not make, or one in error, fails.
- **The carry's "bore" on a partial cylinder.** `_bore_mm` of the old Sun's entry is 8 + 0.3 (typed, on record), so the
  carry looks for a coaxial cylinder of 4.15. SunGear keeps 0.3 by ruling 1 and is read as that D. The check needs the
  mate in the carry's `remade`, not `named`, and made again in no error.
  - A carry that ignored the allowance (looking for 4.0) would name the mate, not remake it: **fails**.
  - A carry that refused partial cylinders: **fails**.
  - A carry that remade the mate onto **another coaxial face** would **pass**: a concentric is the same constraint on
    any face about the axis.

  To close that, read the remade mate with `Session.mate_definition` (the app's, W9d's) and hold Sun's entity to a
  face whose `EntityParams` radius is 4.15 mm. Do the same for the mate the script makes, at 4.1 (S3).

## 5. Safety, nobody at the keyboard

- **Calls.** None new to the repo, as the note says, each found where it names it:
  - the face reads are W9b's `part_faces`;
  - `ws.Columns(n).Insert()` is W9c's `ensure_headers` (`w9c_demonstration.py:1849`);
  - `AddMate5` and `GetCorresponding` on a face are W9c's probes as used by W9d's fixture;
  - `set_global_variable` and the assembly rebuild by hand are W9a's `refuse` step.

  The self-check holds the 96 names it borrows and every Session member it calls. New in kind only: `CreateMassProperty`
  on a part made the build document by `use_open_document` rather than activated, and every read on a D.
- **The dialog watch** is W9a's, the What's Wrong rule per version, every app job submitted `app_job=True`.
  `--close-outlived-whats-wrong` is W9c's own path and goes in on 2024 only.
- **Memory**: W9a's 2 GB floor, plus 6 GB (`F2.PRESS_FREE_GB`) before `userwork`'s copy, its first press and each
  Build again….
- **Where it writes.**
  - Masters are only copied (`A.copy_desk`, `D.copy_desk`), and the reducers are kept as masters under `<out>`.
  - APPDATA is redirected, so the strip's Recent list and records stay in the run folder.
  - The switch is changed only by F2's `patched`, in this process, said, and put back in a `finally`.
  - Excel is the script's own.
- **The switch** is read in the log's head and again at each section, and is in the JSON. `allowance`, `print` and
  `built` stop their section with it off.
- **The session's build document**: `part_read` leaves `use_open_document`'s document set, but every Update values runs
  after `F2.activate`, which clears it (`swcom.py:1408`), and `update_variables` refuses a wrong active document. No
  stale read.

## 6. The self-check

Fifteen checks against F2's thirty-five, but each holds many cases, and every pure judgement is failed each way it can
fail:
- the faces: 9 bad cases;
- the STEP reader: 6;
- the links: 5;
- the volume, the words and the maths;
- the thirteen dshape steps run through the strip's own form.

Reading F2's pure part by `exec` of everything above its `if SELF_CHECK:` line is acceptable. F2's file is unchanged,
its head is pure, and a change to its shape fails the import at once. Restating 300 lines would be worse.

What it cannot see is what M1 and S1 are about. Its made-up faces have exact boxes and one face per arc, so it confirms
the assumptions that may be wrong. Add a D whose boxes are padded 0.25 mm and one whose arc is two faces, each of
which must hold once M1 and S1 are fixed. The live-only judgements (`bore_mate`, the carry, K11's cell) are not pure
and are not held, which is acceptable.

## 7. Must-fix, should-fix, and the runs

**Must-fix**
- **M1** `probe/f3_demonstration.py:327`, `:333` (with `BOX_TOL` at `:109`) and `:348-354`: box readings judged at 0.1 mm
  against a padding measured at 0.24. Make the round's reach past the flat, the flat's span and the lands' angles
  facts (keep the −X reach and the lands' count judged), or give them a tolerance clear of the padding. Add a padded
  case to the self-check.
- **M2** The Done-when's hub gearbox turning with no interference: a section, or the coordinator's ruling taking it
  out of the Done-when with the reason in the plan. Suggested section: RangeBox_Fixed printed, its Hub row Bore 8, an
  allowance typed and Drive flat, Flat 7, built with the switch on, the Hub read as a D by its faces, turned through
  every mode with the interference read, as W9b's and W9c's `fixed` sections do. On 2024, put it in `userwork`'s fresh
  session or one of its own.

**Should-fix**
- **S1** accept a split arc (`:316`, `:469`, `:1733`).
- **S2** judge every build's `result.checks` free of *not fully defined* (`allowance` `:1382`, `print` and the twins
  `:1237`), so the Done-when's *every sketch fully defined* is read everywhere.
- **S3** `Session.mate_definition` of the bore mate, made and carried, its Sun entity's radius held to (D + a)/2.
- **S4** judge each link's Equation Manager `Value` against the chord or R, accepting mm or m.
- **S5** a herringbone in `ALLOWANCE_KINDS` (`:149`).
- **S6** a machined 12 : 1 built before F3, typed Printed, one Update: Backlash written, no `"Bore Allowance"` in
  SolidWorks or on record, its `.gear.json` still at 1 or 2 (the plan's `workbook` bullet; guard 4 live).
- **S7** on 2026 run `dshape` alone first.
- **S8** after the run, the structural sentence for an allowance on a pre-F3 part to say why and what clearing does (B's
  words).
- In `allowance`, judge a round hole with `bore_judged(faces, R)` (no flat) rather than the smallest radius alone.

**The runs** (after M1 and M2; a snapshot by `git archive`, `--self-check` on it first; each invocation a fresh
SolidWorks and its own log):

- **SolidWorks 2026.**
  1. `--sections dshape`.
  2. `--sections allowance,print,built,userwork`, or `userwork` in a third fresh session if the 6 GB floor stops it,
     with the hub section beside `built` if added.

  `--user-master …\w9a-final-sw2026-20261117-023433\out\setup.master`. No close flag.
- **SolidWorks 2024**, the confirming build, WSL idle, `--close-outlived-whats-wrong` on each.
  1. `--sections userwork` (with the hub section) and `--user-master …\w9a-confirm-sw2024-20261117-002313\out\setup.master`.
  2. `--sections dshape,allowance,print,built` in a second fresh session, `dshape` first.
