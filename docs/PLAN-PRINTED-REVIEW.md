# Review of `docs/PLAN-PRINTED.md` (gears made to be 3D printed in PLA), draft of 2026-11-16

**Verdict: not ready to approve. Five changes are needed first, then it can go ahead.** The numbers the plan quotes
are almost all right; I recomputed them. The direction is sound: a fixed flank allowance, nozzle checks, a STEP
export, then the bore and edges, then strength. The problems are elsewhere:

- The pair interference condition is wrong for ring gears. It gives the wrong answer both ways on the repo's own
  fixtures.
- The plan applies that check to every pair. That breaks its own proof that a machined gear builds as it does today,
  and it moves W9's pinned answer keys.
- A fixed 0.3 mm backlash turns every fine-module gear into a refused part. The plan says nothing about that.
- "A record without Process reads as Machined" is stated, but not designed. Three things have no answer: where
  "missing" differs from "blank"; the Process custom property, which Update never writes; and printed parts built
  in P1, which go stale when P3 changes what Printed builds.
- The sequencing claim against W9 ("whichever lands second carries the merge") leaves out two semantic collisions.
  Landing P1 first moves W9's independently checked warning counts. It also changes the baseline of S0's master,
  which W9a's demonstration starts from.

The STEP and chamfer stages and the strength method have smaller faults. They are listed as should-fix.

**How it was checked.** I read the whole plan and `README.md`. I read *Rules carried over* and *Where W9 stands* in
`docs/HANDOFF-WORKBOOK.md`, and the hub, sleeve, fixture and stage sections of `notes-workbook/ISSUE-1-PLAN.md`. I
read this code:

- `spec.py`; `gears/spur.py`, `helical.py`, `internal.py`, `bevel.py`, `clutch.py`, `pair.py`, `properties.py`,
  `base.py`;
- in `swbuild.py`: `structural_change`, `planned_changes`, `update_variables`;
- in `swcom.py`: `save_as`, every `Select2`/`SelectByID2` call, `revolve`, `mirror_body`;
- `store.py` (the schema constants);
- in `workbook/`: `schema.py`, `model.py`, `checks.py` (the planetary undercut and ring-tip checks), `update.py`
  (`_part`, `_ignored_fields_as_built`, `_structural`), `gearbox.py` (`same_part`, `_matches`, the reuse
  docstring), `fixes.py`;
- `gui.py` (`_load_record`, `_update_target`, the build refusal);
- the tests' pins (`tests/test_workbook_modes.py` `BEFORE_W8`, `tests/test_workbook_planetary.py` `_fingerprint`),
  `tests/workbook_fixtures.py`, the committed `.xlsx` fixtures, and the probe scripts that build `GearSpec`s.

I recomputed every figure with `.venv/bin/python` against `gear_generator`. I did not run SolidWorks, Excel or any
window test, and I did not run the test suite.

---

## Findings, most important first

### 1. The interference condition is reversed for internal pairs and unstated for helical, crossed and bevel pairs. *Must fix before approval.*

**The plan (§2.3)** proposes a check on every pair, per Meshes row too: *"a gear's tip circle must not reach inside
the other's base-circle tangent point, `ra₂ ≤ √(rb₂² + (C sin αw)²)`."*

**What I found.** For two external gears the condition is right. With unshifted 20° teeth it gives exactly the plan's
table: 13 clears 16, 14 clears 26, 15 clears 45, 16 clears 101, and 12 or fewer clear no mate that clears them back.
For a ring it is the wrong way round.

Here is the working for a pinion inside a ring. Both base circles are tangent to the line of action on the same side.
Take T2 (the ring's tangent point) as 0 along the line. The pinion's tangent point T1 is then at `C sin αw`, and the
pitch point lies beyond T1. The ring's tip contact is at `√(ra₂² − rb₂²)` from T2. To stay on the pinion's involute it
must lie at or beyond T1. So the ring's condition is **`ra₂ ≥ √(rb₂² + (C sin αw)²)`**. This is KHK's
`z1/z2 ≥ 1 − tan αa2 / tan αw` in another form.

Applied as written, the plan's inequality gives the wrong answer on the repo's own fixtures, in both directions:

| Pair (m, teeth) | Ring tip `ra₂` | `√(rb₂² + (C sin α)²)` | Plan's `≤` says | Correct `≥` says |
|---|---|---|---|---|
| RangeBox Planet 13 in Ring 55 (m 1.25) | 33.125 | 33.526 | clear | interferes |
| planetary_4to1 18 in 54 (m 1) | 26.000 | 26.108 | clear | interferes |
| Risky_Placements 14 in 36, β 20° (m 2, transverse) | 36.310 | 36.711 | clear | interferes |
| E4 Sun/Planet 24 in Ring 72 (m 1) | 35.000 | 34.811 | **warns** | clear |

The existing `internal.tip_clash` agrees that those three rings are marginal: 0.006, 0.0002 and 0.018 mm.

The plan also does not say which values a helical pair uses. It should use transverse values: `rb` from `αt`, the
transverse working angle, and the radial addendum `mn(1 + x)`. Crossed helical pairs have no common transverse plane,
and the formula does not apply to them at all. Bevel pairs need the Tredgold virtual pair at the back cone, which
`pair.bevel_candidate` already uses for its clash.

**The plan should say:**

- the external and internal conditions separately;
- transverse quantities for helical kinds;
- for bevel pairs, the virtual pair with Gleason's addenda;
- for crossed pairs, either no check or each gear's existing undercut (rack) limit, stated as such.

The check should also take over the planetary sentence it duplicates, `workbook/checks.py:352-359` ("is below the
undercut limit … and meshes …"). Otherwise RangeBox says the same thing twice.

### 2. "The pair check applies to every pair" contradicts the machined rule, its proof and W9's answer keys. *Must fix before approval.*

**The plan** keeps one rule: a machined gear builds exactly what it builds today, pinned by a test. P1's *Done when*
also says *"every fixture that was pinned before still passes with Process Machined and nothing else altered."* Yet
§2.3 adds the interference warning to machined pairs as well.

**What I found.** The repo already pins nine workbooks bit for bit in `BEFORE_W8` (`tests/test_workbook_modes.py:212-241`).
Its `_fingerprint` (`tests/test_workbook_planetary.py:369-384`) hashes every diagnostic's message together with the
plans. Under the correct conditions of finding 1, `planetary_4to1`, `sun_held`, `carrier_held` and
`Risky_Placements.xlsx` each gain a ring warning when marked Machined. Under the plan's own (wrong) inequality, E4 does.
So *"nothing else altered"* fails either way.

W9's §3 has hand-pinned, independently checked counts: RangeBox has "four warnings", and each W8 fixture's count
moves "by three". RangeBox's Sun 29 / Planet 13 is in the plan's own table as interfering (13 clears only 16). That
adds at least one warning, and W9b's STOP fires on *"any warning on a fixture other than §3's"*
(`ISSUE-1-PLAN.md:676`).

**The plan should say one of two things.** Either the pair check is printed-only in P1, which keeps the rule and the
pins whole. Or it applies to machined pairs too, in which case the plan must say plainly that this is a deliberate
change to machined diagnostics (not to builds), list which pins and which W9 answer-key counts move, and re-take them
in the same commit.

### 3. A fixed 0.3 mm backlash makes fine-module gears unbuildable, and the plan does not say so. *Must fix before approval.*

**The plan (D3, §2.1)** sets blank backlash on a printed gear to 0.3 mm "whatever the module". §2.2 adds a module
*warning* under 1.0. §2.5 says *"Nothing is dropped."*

**What I found.** Tip thickness after a 0.3 mm backlash (`spur.profile`) is:

| Module | Tip thickness (mm) |
|---|---|
| 0.5 | negative for every count under 17 (−0.012 at 15, −0.040 at 12); 0.017 at 20 |
| 0.75 | 0.116 at 12 teeth; 0.191 at 20 |

A tip at or below zero is an **ERROR** (`spur.py:843-847`: "the teeth come to a point"). The same holds for rings.

So under "Printed by default" every module-0.5 gear under 17 teeth is refused where it built yesterday. That
includes every workbook with such a gear and a blank Process, which is every existing workbook. Solve, with
"nothing dropped", will offer rows that refuse when applied. The 0.75 and 0.8 rows are not errors, but they come out
far under a nozzle.

**The plan should say** what printed blank backlash does below module 1. Three possibilities:

- the smaller of 0.3 mm and the machined 0.3 × module;
- a floor such as tip ≥ 0 that refuses with a sentence naming module and backlash;
- an explicit statement that printed gears below about module 0.8 are refused, and that the Box or form should say
  Machined for them.

It should also say that Solve drops, or marks as unbuildable, rows whose printed tip is ≤ 0.

### 4. "A record without Process reads as Machined" is a rule with no design behind it, and it drifts. *Must fix before approval.*

**The plan (§1, D2)** says: blank Process is Printed; a record from before this plan, which has no Process, is
Machined; Update carries a Machined → Printed change in P1 "(backlash only)", and that change becomes structural
from P3.

**What I found.**

- **Missing and blank are told apart nowhere today.** `GearSpec.from_dict` (`spec.py:157-160`) fills a missing key
  with the dataclass default. If `process`'s default is `""` (Printed, as D2 has it), every old record reads Printed.
  The rule needs a missing-key-means-`machined` step in `from_dict`, or in a dedicated record reader. It also needs
  the same rule in every place that compares raw spec dicts:
  - `swbuild.structural_change` (`swbuild.py:1239-1290`), which reads `built.get(key, default)`; `teeth_side`
    already has a missing-key default there, and P3 must add `process` the same way;
  - `workbook/update._structural` and `_ignored_fields_as_built` (`update.py:216-258`, `b.get(key, "")`);
  - `gui._update_target` (`gui.py:1505`).

  New records should always write `process` explicitly as `printed` or `machined`, never blank, so the ambiguity
  ends with this version.
- **The `Process` custom property is never carried by Update.** Properties are written only at build
  (`properties.py`; `swbuild._property`). `update_variables` sets globals only. A part flipped from Machined to
  Printed by Update keeps no Process property, and one flipped back keeps "FDM print, PLA". Meanwhile its record
  says the other thing. `same_part` compares plans, so the next Update sees the record and the plan agree, and the
  part's properties stay wrong silently. Either Update writes the property, which is `set_custom_property` on an
  opened part, a use not proven, or the property is left out of P1, or a process change is structural from the
  start.
- **Printed parts built in P1 or P2 go stale at P3.** P3 adds a `"Bore Allowance"` global, a changed bore link and
  chamfer features to every printed gear. A P1-built printed part has none of them. After P3, every such part and
  every printed workbook reads as changed. `planned_changes` then raises `"Bore Allowance" is not in this part, so
  it was not built by this tool` (`swbuild.py:1337`), and `update._part` says "needs a new part". The plan needs a
  stated answer for this. The test print's own parts are among them. Possible answers: a printed-scheme version in
  the record, P3 treating a printed part without the allowance as "printed, before P3", or simply saying those
  parts go to a new revision.

**The plan should say** where the missing-versus-blank rule lives and list every comparison that uses it. It should
settle the property question, and say what P3 does to P1's printed parts.

### 5. The W9 sequencing claim does not hold as stated. *Must fix before approval.*

**The plan (D8)** says P1 and P2 come before W9 resumes, that P1 and W9b both touch `workbook/schema.py`,
`ui_text.py` and the form, and that whichever lands second carries the merge.

**What I found.**

- **Answer keys.** See finding 2. W9's §3 counts were checked by an independent agent. P1's checks change them, and
  W9b's STOP rule then fires.
- **S0's master.** W9a's demonstration starts from `w9-s0-…\out\rangebox.master` on the Windows host
  (`HANDOFF-WORKBOOK.md:71-93`, `ISSUE-1-PLAN.md:590-591`). Its workbook was built before this plan and has no
  Process. After P1 it reads Printed: every part is "changed since it was built", and every Update in W9a's
  demonstration carries backlash changes nobody asked for. Adding `Process Machined` to `tests/workbook_fixtures.py`
  does not reach that file. The plan must say the master's workbook gains `Process Machined` before W9a's run, or
  that W9a rebuilds its master.
- **Record schema numbers.** W9 has already claimed link schema 7, 8 and 9 and sidecar schema 2
  (`ISSUE-1-PLAN.md` §2.4). The reason it gives for sidecar 2 applies here too: `from_dict` drops unknown keys, so
  an older app misreads a newer record. An app from before P1 reading a P1 workbook ignores the unknown Box
  setting, because `_read_box` skips unknown labels (`model.py:341-345`). It then plans the machined
  `0.3 * "Module"`. Its Update rewrites every printed part's Backlash back to the machined value. That is
  realistic while a `printed` branch and the `workbook` branch run side by side on one machine. The plan must
  either take schema numbers, and W9 renumber, or say why no bump is needed and accept the downgrade.
- **K11 (W9a).** Update must refuse a value the app owns that the user changed in SolidWorks. P3's new globals
  (`Bore Allowance`, the chamfer size, `Flat`) join the set K11 reads. The hub (W9b) is built "with the row's Bore",
  with fixing to the shaft left to the user. P3's D-flat and bore allowance are exactly that fixing, so the two plans
  must agree who owns it. K9's running clearance `max(0.5, 0.5 m)` is justified by "the chamfer and backlash a real
  dog needs scale with the tooth". Under Printed, backlash no longer scales. On sleeves, §1 says the chamfer "is
  P3's, and W9b changes them, so it is settled there", without saying which plan "there" is.
- **The file list is off.** Per `ISSUE-1-PLAN.md` §5, W9b has "no window control". The plans collide on the form and
  `ui_text` through W9a (K12, the footer), and on `store.py`, `update.py` and `checks.py` through W9a and W9b.
- **Names.** W9's own probes are called P0, P1 and P2 ("W9c: P1, then S5 and P2"). This plan's stages P1 to P4 reuse
  those names in the same documents' world. Rename one set, for example Stage F1–F4 here.

**The plan should say** which branch the W9 work runs on during P1/P2, and when `printed` merges. It should list the
semantic collisions above, beside the textual ones, each with its resolution.

### 6. The radial clearance check is stated per gear and misses shifted pairs, bevel gears and fat tips. *Should fix.*

**The plan (§2.2)**: *"the root clearance (tooth depth less two modules) under 0.3 mm … The depth IIF as it stands
passes this at every module from 0.75 up, so the depth is left alone."*

**What I found.**

- **Shifted pairs.** Clearance is a property of the pair, and the code already has it: `pair.tip_clearance`. With
  shifts the solver and the workbook fix accept clearance down to `CLEARANCE_MIN = 0.1 × m` (`pair.py:92, 281, 326`).
  At m 1.5, 12/30 with x = 0.5 + 0.5, it is 0.192 mm. At m 2 it is 0.256.
- **Bevel gears.** Gleason gives `2.188 m − 2 m = 0.188 m` (`bevel.py:85-86`): 0.28 mm at m 1.5. Every printed bevel
  under m 1.6 warns, so "passes from 0.75 up" is false for them.
- **Float edge.** At m 0.75 the computed clearance is `0.2999999999999998`, so `< 0.3` warns at the very module the
  plan says passes. Give the check a tolerance.
- **Fat walls.** §2.1's allowance only moves the involute (finding 12). Walls printed fat by e also grow each tip and
  raise each root, which takes 2e off this clearance: 0.375 − 0.28 ≈ 0.1 mm at m 1.5. The 0.3 mm threshold may be
  meant to cover this. If so, say it.

**The plan should say:** run the check per pair, on `tip_clearance` at the working centre distance, Gleason's for
bevel pairs; for printed pairs, raise `CLEARANCE_MIN` to `max(0.1 m, 0.3 mm)`; and whether the depth is left alone
knowing that bevel gears fail it.

### 7. The pair solver's and the workbook fix's thresholds stay machined for printed gears. *Should fix.*

`pair._shifted` and `pair.shift_for_centre` (`pair.py:278-282, 323-327`) refuse shifts whose tip *before backlash* is
under `0.3 × m`, or whose clearance is under `0.1 m`. `workbook/fixes.py:173` uses the latter. For printed gears the
meaningful test is the tip *after* the fixed backlash against the nozzle, and clearance against 0.3 mm. As written,
the profile-shift fix offers printed shifts whose tips print under a nozzle at m < 1. At m ≥ 2 it refuses shifts that
a printed gear would take. §2.5 covers ranking in Solve, but not these two.

### 8. Pinning machined: the proposed test is weaker than the repo's precedent and does not cover old records. *Should fix.*

**The plan** pins "the plans of today's gears, marked machined".

**What I found.** The precedent (`BEFORE_W8`) already hashes nine workbooks' diagnostics, motion and
`build_kwargs()`. To prove the rule, the pin should cover, all taken at the commit before P1's first line:

- strip plans of every kind and recipe in both trig variants;
- `pair.assembly_plan`, `crossed_assembly_plan` and `bevel_assembly_plan`;
- Solve's row lists for machined pairs;
- the W8 fixtures and RangeBox, which are not in `BEFORE_W8`;
- what `update.plan`/`_part` and the strip's `_update_target` say for a **record without a `process` key** against a
  workbook or form marked Machined. They should say nothing changed. This is the case the whole rule rests on, and
  "marked machined" in the test does not reach it.

The fixture burden is also larger than §1 suggests:

- 194 `GearSpec(...)` constructions in 24 test files;
- `GearSpec()` used as "the pinned m 1.5, z 25" in `test_equations.py` and others;
- the probe scripts that build `GearSpec`s: `probe/gear_pairs_check.py`, `small_pinion_check.py`, `gearbox_smoke.py`,
  `w9_user_work_check.py` and `src/gear_generator/probe/p1_equations.py` and `p5_*`;
- three `.xlsx` fixtures that **Excel itself saved** (`tests/fixtures/excel-windows/*`, `excel/`, `libreoffice/`).

The last cannot "gain Process Machined" without Excel saving them again; editing them with the app's writer
destroys what they test. Say instead that the tests inject Machined into the read Box for those three, and leave the
files as Excel wrote them.

### 9. The chamfer: what is new is larger than one call, "0" cannot go through Update, and the default nearly consumes a module-1 tip. *Should fix (before P3 is planned in detail).*

**The plan (§4)**: a new op `Chamfer` on both end faces, by face; `"Edge Chamfer"` is 0.3 × module, at most 0.5,
and `0` means none; *"The SolidWorks call (a chamfer by face) is one the app has not made"*. The fallback is *"a
revolved cut that chamfers the tips only"*.

**What I found.**

- **Selection.** The app never selects a face or an edge today. Every selection in `swcom.py` is a feature, a plane
  or a sketch entity by name (`SelectByID2`/`Select2`), and the only B-rep read is `GetBodies2` for body counts.
  Finding the two end faces means new B-rep traversal: faces of the body, plane tests, `IEntity.Select4` with a
  mark. All of it is uncalled. Ring, helical (oblique flank edges) and mirrored herringbone end faces each differ.
  This does not need probing first under the rule, since it should not hang or raise a dialog, so the full-build-
  first judgement is consistent. But the plan understates it, and the estimate should reflect it.
- **Update.** The plan wants Update to carry the chamfer size. A chamfer of 0 is not a valid SolidWorks chamfer, so
  `0` (none) versus non-zero must be structural, as a bore is (`structural_change`). It cannot be a value. Which
  dimension `LinkDimension` drives (`D1@<chamfer>`) also has to be found.
- **Tip.** At m 1 the default chamfer is 0.3 mm. The tooth's thickness 0.3 mm below the tip is 0.66 to 0.74 mm
  (12 to 60 teeth). Two 0.3 mm flank chamfers leave about 0.06 to 0.14 mm there: the bed-face tip is close to a
  knife edge, and the first layers of each tooth print narrower than a line. At m 1.5 (0.45 chamfer) about 0.3 mm
  is left. The plan needs a pure-maths check that the offset outline survives, and probably a smaller default.
- **Fallback.** A revolved *cut* is also a call the app has not made. `base.Revolve` is a boss
  (`FeatureRevolve2`, probed); there is no revolved-cut op. A fallback with **no** new call exists: make a printed
  gear's blank by `Revolve` of a chamfered profile before the teeth are cut. That chamfers tips and a ring's rim,
  leaves the flanks to the slicer's first-layer compensation (which the plan's sources offer as the alternative),
  and needs no face selection. It may be the better first route, not the fallback.

### 10. The test print cannot answer what P3 waits on, and it needs a bore that P3 has not built yet. *Should fix.*

**The plan (§3)** runs one pair at module 1.5, 20/20 teeth, herringbone and spur, at backlash 0.2, 0.3 and 0.4 mm,
"on two pins 30.0 mm apart". What turns freely without rattle becomes D3, and *"P3 does not start until this is back:
the allowances there take their sizes from it."*

**What I found.**

- **The bore.** P1/P2 gears have a nominal bore. P3's bore allowance comes later, and printed holes come out small,
  so the gears may not go on the pins at all. The user has to type an oversize Bore for the print, and the plan
  should say by how much.
- **The rig.** It is undefined. Printed hole spacing error feeds backlash directly: Δj ≈ 2 Δa tan α ≈ 0.73 Δa, so
  0.1 mm of centre error moves the play 0.07 mm, half a step of the test.
- **The measure.** Every variant will have some play at 0.4 to 0.8 mm. A better criterion is the smallest that turns
  through full turns under light load without tight spots, before and after a short run-in.
- **What it tests.** The print measures only backlash, yet P3's bore allowance (0.2 mm) and chamfer are said to take
  their sizes from it. Add a bore-fit coupon to the same print (pin + 0, + 0.1, + 0.2, + 0.3 mm), and a chamfered
  versus plain first-layer coupon if the chamfer default is to be grounded.

### 11. P4's strength method: ISO's angle is for external gears, the stress factor is dropped, and "torque per Meshes row" is the wrong quantity. *Should fix.*

**The plan (§5)**: the critical section "where a 30° tangent meets the root fillet (ISO 6336's definition)", the
whole load at the tip of one tooth, no stress-correction factor, against 17 MPa. The workbook compares "each Meshes
row's torque against the weaker gear's capacity".

**What I found.** These points rest on my knowledge of ISO 6336-3 and printed-PLA behaviour, which I could not check
here.

- **Ring gears.** The 30° tangent is ISO's for external gears. For internal gears it is 60°.
- **The stress factor.** Leaving out `Y_S` understates the peak fillet stress by roughly 1.5 to 2 for a 0.38 m
  fillet. "A third of 50 MPa" is then nearer a half or two-thirds at the notch, and the "share used" reads
  optimistic. The app has the fillet radius and the 30° section, which is all ISO's `Y_S` formula needs. Include it,
  or say plainly that the figure is nominal.
- **The quantity.** A Meshes row has two torques, one per gear. What both gears share is the tangential force
  `Ft = 2T/d`, and each gear's capacity is a force. Planetary meshes must divide by the planet copies, with a load-
  sharing allowance. An idler, such as the transfer cases' FIdler, bends both ways, which lowers what a plastic tooth
  can take.
- **Layers.** Printed flat, a spur tooth bends within its layers, so a datasheet in-plane figure is the right kind.
  A helical tooth's axial load component, and a bevel tooth's inclined bending, load the bond between layers, which
  is weaker. Say the figure is for spur and flat-printed teeth, or derate the others.
- **Coverage.** Bevel gears need the virtual gear at the mean cone. The plan does not say whether P4 covers them.
- **Wording.** The plan rightly says it is static. "Torque one tooth carries" in the Derived panel will still be read
  as a running rating. PLA creeps at room temperature under sustained load, and its fatigue limit is well under its
  static strength. Name the figure "once, not running" in the panel itself, not only in its caveat.

### 12. "An exact allowance for walls printed evenly fat" holds on the involute only. *Should fix (wording, and see 6).*

My working: widening the space by j at the pitch circle turns each flank by `(j/2)/rp`. An involute turned by δ
about its centre moves square to itself by `rb·δ`, so the flank moves `(j/2) cos α` = 0.141 mm. That is the plan's
0.14, and for helical kinds `(jn/2) cos αn`, since `transverse_backlash = j/cos β` (`helical.py:341`). The same holds
for a ring.

The radial line and the root fillet are turned, not offset. Their displacement `r·δ` is tangential and varies with
radius. The tip circle and root circle do not move at all. Fat walls grow tips and shrink roots, and nothing here
allows for that (finding 6).

**Bevel gears.** The allowance is not uniform along the face. The toe section is the heel's scaled toward the apex
(`bevel.py` docstring), so the toe gets `(R − b)/R` of it. For 20/40 at m 1.5 and b = 10, that is 0.70: 0.099 mm a
flank. The toe's tip is thinner by the same ratio: 0.37 mm at the toe where the heel has 0.53, so it is under a
nozzle where the heel check passes. §2.1's "a bevel gear the same" and §2.2's tip check should both say the toe
governs.

### 13. Printed and machined gears share a file name. *Should fix.*

`default_stem` (`spec.py:260-292`) gives a printed gear and a machined gear with the same values the same name. Its
own docstring says a shifted gear gets a suffix "since it is a different part". On the strip, building a printed
`Gear_m1.5_N25` beside a machined one is refused, "already exists" (`gui.py:1546`), until the user types a Part name.
In a workbook it becomes `_r2` with a "made new" sentence. Either mark printed stems (for example a trailing `_P`;
machined stems stay as today, which keeps the rule) or say why not.

### 14. Where the new values live is not settled. *Should fix.*

- `nozzle` is "the form in Printed, a Box setting", but not in `GearSpec`. Every kind's `validate(spec, derived)`
  sees only the spec, so either nozzle enters `GearSpec` (where `_ignored_fields_as_built` would ignore it, since it
  changes no plan) or every kind's `validate` signature changes.
- P3's `Bore Allowance` and `Edge Chamfer` are globals, but no form row or Gears column is named for them. Only
  `Drive` and `Flat` are.
- In pair mode it is not said whether Process is one row for the pair or one per gear. `pair.apply` must carry it to
  both specs either way.
- `Gear.spec_values` (`model.py:111-130`) must fill `process` from the Box. A test already holds that function to
  `fields(GearSpec)`, which is good. `to_sheets` (`model.py:393-404`) maps Box keys explicitly, so New workbook
  writes nothing for `Process` or `Nozzle` until they are added there.

### 15. The STEP probe's own reopen step is a dialog risk, and two claims rest on outside knowledge. *Should fix.*

The plan probes `SaveAs3` to `.step` first. That is right by the rule, because it writes a file and may raise a
dialog. It checks the part's path and modified mark afterwards, which is right too: `swcom.save_as` checks
`GetPathName` because a SaveAs renames the document, and an export must use the copy option or show that the
foreign format does not rename.

But "the file reopens as one solid of the same volume" means opening a STEP in SolidWorks. That can bring up import
dialogs (import diagnostics, 3D Interconnect). Either the probe opens it with silent import options and treats any
dialog as its STOP, or it checks the file without SolidWorks: count the solid B-reps in the STEP text, and leave
volume to the slicer step.

Two claims rest on outside knowledge: "current slicers open STEP" (not every slicer does natively, Cura among them as
far as I know) and "carries the involute as a curve" (SolidWorks stores an equation-driven curve as a spline, so the
STEP carries a spline surface). P2's user step covers the first in practice. Word both as what was read, not as
fact.

### 16. Rules and costs. *Note.*

- P1 has no 2024 confirming build. The rule asks one at every phase's end, even a short one.
- Only P3 has a time estimate, and no stage has an agent-run count. The user approved W9 by agent runs and is
  watching usage.
- `Done when` names no review step; the plan relies on "the rules apply".

Each stage should carry the rule's 2024 build, a time, an agent-run count and its review.

### 17. Smaller inaccuracies. *Notes.*

- §2.2: "module 1.5 with any count" passes the tip check from 8 teeth. At 6 and 7 teeth (`MIN_TEETH` is 6) the tip
  is 0.305 and 0.379 mm.
- §2.4: the 40-tooth example of the involute starting above the form diameter holds above module 1.25 (it fires from
  26 teeth at m 1.5). At module 1 it fires only from 47 teeth.
- §2.2 Helix: the overhang angle of a printed helical flank is the **base** helix angle `βb`
  (`sin βb = sin β cos αn`), 41.6° at β 45°. Warning on β is conservative by a few degrees. Fine, if that is the
  intent.
- §2.2 Rim: "(or drive flat)". A flat is nearer the centre than the bore's round part, so the thinnest wall is
  always at the round part. The flat never governs.
- §1: "the window says which in one sentence the first time such a workbook is opened". "First time" needs stored
  state (where?), or it says it every time.
- §2.1: writing printed blank backlash with `backlash_typed=True` makes `ui_text` (lines 128, 167, 520-523) show it
  as typed, with no "· default" mark. A third state is needed for the card to say "printed default". The hint at
  `ui_text.py:369` and `design/UI-DESIGN.md:96` ("ISO asks 0.02–0.05 × m") and README line 189 also need words for
  Printed.
- The 6/24 SolidWorks evidence (`small-pinion-2026-…log:558-567`) is a machined module-0.5 pair at four sampled
  positions. Under Printed that pinion is refused (finding 3). The evidence is fine for "a warning, not an error",
  but "the play taking it up" is a hypothesis, not a measurement.

---

## What a careful engineer printing PLA gears would still find wrong after all four stages

- **No radial allowance.** Tips and roots are not offset (findings 6 and 12), and tip corners print rounded (about
  half a line). The real contact ratio is a little below the drawn one. Nothing reduces the tip or deepens the root
  for printing.
- **Centre-distance error is outside the app.** The shafts or housing the gears run in are left to the user, and an
  error there moves the play by about 0.73 × the error. A workbook layout gives exact distances with no printed
  allowance.
- **No tip relief.** PLA's modulus is about 1/60 of steel's, so loaded teeth deflect and meet early, and that is what
  tip relief is for on plastic gears. The plan excludes it (§6). That is defensible, but say it is the first thing a
  loaded printed train will want.
- **Wear, heat and creep are not assessed.** Each is named, but PLA-on-PLA sliding wear and a D-flat creeping round
  under steady torque are the usual failures of printed drives, ahead of root bending. The export's list could at
  least advise grease, and a different material for one gear of a pair.
- **Seam placement.** A seam on a tooth root is a notch. "Seam at the tips or aligned" belongs in the export's print
  settings.
- **The printability floor is not strength.** Three nozzle widths (1.2 mm) under the root is a printability floor.
  Today's one-module warning is the stronger at every module above 1.2.

---

## Checked and found right

- **Flank offset.** 0.3 mm per gear gives `(j/2) cos α` = 0.1410 mm per flank. The pair's play is 0.6 mm at the
  pitch circle (`ui_text`'s "play in the mesh" is `2 × backlash`). At module 3 today the play is 1.8 mm; at module
  0.5 it is 0.0705 mm a flank.
- **Tip thickness after a 0.3 mm backlash.** At m 1: 0.271 (12 teeth) to 0.446 (40). At m 1.25 with 12 teeth: 0.426.
  At m 1.5: 0.581 (12) and 0.712 (20). The Context's 0.37 mm module-1 tip (20 teeth, 0.365) passes today's 0.3 m
  warning.
- **Interference table.** For external unshifted 20° pairs: 13→16, 14→26, 15→45, 16→101, 17→1309; nothing clears
  with 12 or fewer.
- **Root clearance.** 0.4 m to m 1.25 and 0.25 m above, so ≥ 0.3 mm for spur and helical unshifted pairs from
  m 0.75 up (apart from the float edge).
- **Module floor.** 2.5 × 0.4 = 1.0.
- **The 6/24 log.** As cited: module 0.5, four sampled turns, 0 interference.
- **Today's backlash default** (`0.3 * "Module"`) is in all five variable writers (`spur.py:743`, `helical.py:371`,
  `internal.py:895, 973`, `bevel.py:640`) and four `derive`s. The typed-literal path (`equations.literal`) exists in
  each, so P1 needs no new equation and no new SolidWorks call for a build.
- **Update carries equation text.** `update_variables` sets expressions through `set_global_variable` after
  `planned_changes` compares the texts with spaces removed. A change from `0.3 * "Module"` to `0.3` is a value
  Update, as §1 says, even at module 1, where the value is equal.
- **Helical, herringbone and ring backlash** is normal backlash, as now (`transverse_backlash = j / cos β`). A ring's
  space is widened the same way.
- **The internal tip-clash check** leaves backlash out (`internal.tip_clash` docstring), so a larger backlash cannot
  make it pass wrongly. It stays conservative.
- **Sleeves and dogs** delegate to the spur and internal-spur kinds with `dataclasses.replace`, so a `process` field
  passes through `clutch._as_spur` unchanged.
- **The probe-first judgement for STEP** (a call that writes a file and may raise a dialog) and the full-build-first
  judgement for the chamfer (a feature call that should not hang or ask) both match *Rules carried over*.
- **The cited files and functions exist and say what the plan says.** Among them: `structural_change`,
  `backlash_typed`, the 0.38 m and 0.15 m fillets, the undercut and thin-tip warnings, the one-module rim warning,
  `SaveAs3`'s overwrite rule.

## What I could not verify

- The guides' figures: module floor, backlash range, 0.5 mm chamfer, five walls; PLA's ~50 MPa and 55–60 °C;
  VDI 2736's scope. I did not fetch the sources.
- ISO 6336-3's 30°/60° rule and the size of `Y_S`; PLA creep and fatigue. These are from memory.
- Whether slicers in use open STEP.
- Whether SolidWorks chamfers a face of some hundreds of edges.
- Whether a STEP save renames the document.
- Whether the app's drawn root actually meets a mate's tip in the cases flagged as interference. SolidWorks'
  sampled check found none at 6/24.


---

# Second review, of the revision after W9 (2026-11-18)

**Read at `51870ca` on `w9d`** (the revision), against the code at the same commit. `git diff c2d95cc 51870ca` touches
only `docs/PLAN-PRINTED.md` and `docs/notes-workbook/W9D-DEMONSTRATION-REVIEW.md`, so the code is the code the plan was
written from. Every file and line below was read with `git show 51870ca:<path>`, not from the working tree, since
another agent is changing `ui_text.py` and `findings.py` tonight. I did not run SolidWorks, Excel, a window test or the
suite. The figures were recomputed in a scratch script against a `git archive` of `51870ca` (`spur.profile`,
`pair.tip_clearance`, `landing.line_landings`, `swbuild._global_values`) and by hand; the scratch copy is deleted.

**Verdict.** The revision answers the first review: the machined default in code is the right design, the schemas
are named and the older app's refusal is real, and the gear maths is right but for three figures. **F1-0 is not ready
to start as written.** Five points in its interface would break the plan's own pins or leave failing tests with no
owner (must-fix 1 to 5 below). Each is a paragraph of plan text, not a redesign. Package A can be written once F1-0
is. B should wait for D11. C can do everything except its D11 sentences. All of this waits for W9 to be merged
into `workbook` and `printed` to be cut. The plan says so itself, and tonight's `ui_text.py` change is one more
reason, since the pins of §2.7 include sentences.

## 1. Citations

**Every citation in §1, §2.1 to §2.8 and §6 was checked at `51870ca`.** Each file, function and line range holds
what the plan says, with these exceptions:

- `probe/p1_equations.py:109`, `probe/p7_workbook.py` and `probe/p8_motion.py` are under `src/gear_generator/probe/`.
  The repo-root `probe/` has no such files. The IIF line at `src/gear_generator/probe/p1_equations.py:109` is as
  the plan says.
- **`_back_words` (`swbuild.py:5484-5489`) does not "still give the exact equation".** It returns
  `f"the equation {edit.blank}"`, and `blank` is `_blank_meaning`'s output: the expression with its quotes removed
  and ` * ` turned into ` × `. If F1 gives `_blank_meaning` the printed words, `_back_words` will say *the
  equation 0.3 mm, the printed default (…)*. The set-back text needs its own source (should-fix 3).
- **`SpurDerived` (`spur.py:149`) is one of four derived classes.** `backlash_typed` is a field of
  `SpurDerived`, `InternalDerived` (`internal.py:172`) and the bevel's `RackSection` (`bevel.py:223`).
  `HelicalDerived` and `BevelDerived` read it through their `section`. `ui_text` reads it from whichever it is
  given (`:128` through `g.section`, `:167`, `:520-521`). See must-fix 2.
- **"No signature changes" holds for `validate` only.** `spur.validate` calls `section_diagnostics(g, recipe)` with
  the derived gear and no spec (`spur.py:731-732`). Helical does the same (`helical.py:364-365`). `pair.mesh_warnings(g1,
  g2)` takes two derived gears (`pair.py:989`). So the checks the plan puts in `section_diagnostics` and
  `mesh_warnings` cannot see `spec.process` or `spec.nozzle` as the code stands. A ring's own diagnostics
  (`internal.py:520-540`, its own `TIP_THICKNESS_WARNING` at `:132`) are not named for the printed tip at all.
- §6 says "the three Excel-saved workbooks" and §2.7 "the five committed workbooks". There are five
  (`tests/fixtures/excel-windows/` three, `excel/` one, `libreoffice/` one). BEFORE_W8 and BEFORE_W7 read the
  three in `excel-windows/`.

Confirmed among the rest: the six `from_dict` callers; the 200 `GearSpec(` lines in 27 test files; `GEAR_COMPOUND`
(`gui.py:83`) and the field test (`test_gui_spec.py:49-52`, which also pins `GEAR_WORKBOOK_ONLY` exactly);
`spec_values` and its test; the four W8/W9 fixtures by name; BEFORE_W8 (`test_workbook_modes.py:232-242`) and
`_fingerprint`; `pair.apply` writing through `with_values` and so keeping Process; `_SPEC_COLUMNS`,
`_changed_columns`, `_bore_mm`, `_GLOBAL_COLUMN`, `_mark`; K9 at `modes.py:606-609`; the phase rule at
`geometry.py:8`.

**A sample of F2 to F4**, all true: `LinkRecord.current_parts` (`store.py:1015`), `update._mark` (`:676-683`),
`swcom.Session.save_as` (`:1358-1370`), `STRUCTURAL` and `has_shift` (`swbuild.py:1291`, `:1319-1329`),
`_GLOBAL_COLUMN` (`:670-673`), `_bore_mm` (`:3245-3254`), `W9D-INTERFACES.md`'s 1e-4 mm (`:265`, `:540`), and
`UI-DESIGN.md:406-420`.

## 2. Machined in code, Printed where the user chooses

**The design is right, and it keeps W9's pins for every fixture built in code.** I traced it through
`update._part`, `_ignored_fields_as_built`, `_structural`, `gearbox.same_part` and `_matches`,
`gui._update_target` and `_changed_columns`. A record with no `process` key, compared against a machined form
or Box, compares equal everywhere: `to_dict` drops the keys on both sides, and `from_dict` fills the machined
default. Two leaks remain, and one sentence is wrong.

- **A machined `.gear.json` would change through `derived`, not `spec`.** `GearRecord.derived` is
  `derived.to_dict()`, which is `asdict(self)` for `SpurDerived` and `InternalDerived` and a merge of asdicts for
  the helical and bevel classes. It is written into every part's `.gear.json` (`gui.py:1698`,
  `gearbox.py:1383`, `:1409`, `update.py:2474`; `store.py:374`, `:392`). F1-0's interface adds
  `SpurDerived.backlash_printed = False`. That puts `"backlash_printed": false` into every machined part's record.
  §2.7's pin on the record's bytes then fails at the interface commit, where the plan says the pins pass
  (must-fix 1).
- **A machined spec with a typed Nozzle does not round-trip.** `spec_values` fills `nozzle` from the Box,
  `to_dict` drops it, and `from_dict` brings back the default. Nothing compares `GearSpec`s with `==` today; the one
  comparison, `update.py:2151`, compares the `to_dict` forms, which agree. So this is harmless, but it should be said.
  `to_dict` must also test "machined" without raising on a bad word, since `process_value()` raises.
- **The link record is not byte for byte W9's after an F1 write.** That is by ruling (open point 5) and is sound. But
  any write moves it to 11: a Build, an Update, Apply fix and Export (`_record_own_write`,
  `workbook_gui.py:1195-1215`). After that a W9-era app waits on a gearbox that is all machined.

**Paths by which a user-facing build would come out machined without the user choosing it:**

- **An old `.gear.json` opened on the strip.** It sets the row to Machined, as designed. A new part built from that form
  afterwards is machined too. The row shows it, so this is visible, but the plan should say it.
- **`python -m gear_generator.gears`** (`gears/__main__.py:35-52`, documented at `README.md:606`). It has no key
  for Process, so it prints and plans machined. It is a developer tool. Name it, or give it a key.
- **A W9 master run again by a script.** §2.7 already covers this: the script writes Machined first.
- **None found in `src` beyond these.** The bare `GearSpec(` constructions in `src` are the form's defaults
  (`gui.py:154`), `_gear_spec`, `Gear.gear_spec`, `with_values` (a round trip through `to_dict`, which keeps a
  printed spec's keys), the CLI and the probe modules. Solve reaches specs only through `apply`. `ui_text.py:636` and
  `gui.py:1387` both go through `solve_spec`, so it is enough that `solve_spec` reads the process.

**Consistency with D2.** At the user's surface it keeps D2: the form starts Printed, a blank or missing Box Process
is Printed, and an old record reads Machined. One inconsistency is D11's. The strip opens a part built before F1 as
Machined (`_load_record` sets the row from the record), while the workbook reads a gearbox built before F1 as Printed
and changed. The same history gives two answers. This is the strongest argument in §4 below.

**The way-back sentence is wrong for the workbooks it is written for (must-fix 5).** `to_sheets` writes the Box
as Format, Name, Output folder, Part template, Assembly template, Pressure angle, Efficiency, Units, at rows 2 to 9.
A workbook written before F1 therefore has **Units in B9** and no Process row. *"type Machined in Box!B9"* would
overwrite Units and set nothing, since `_read_box` reads by label. The sentence must say to add a row labelled
Process with Machined beside it, and name a cell only when the row exists (`_read_box`'s `at(key)` already
returns "Box" when it does not). The footer's sentence for D11's assumed answer needs the same words.

## 3. Schema numbers

- **Link 11 and sidecar 3 agree with `store.py`.** `LINK_SCHEMA_VERSION` is `_W9C_LINK_SCHEMA + 1` = 10 (`:421-426`),
  and `SCHEMA_VERSION` is `BANDED_SCHEMA` = 2 (`:33-35`). The per-part sidecar rule fits `sidecar_schema`
  (`:88-92`), so a machined part stays at 1 or 2.
- **What an older app does with a newer file is as the plan says, and the tests hold it.** For a link record,
  `UnknownSchema` is raised, the file is left byte-identical, and `save_link_record` refuses with `LINK_WAITS`:
  "Build and Update SolidWorks wait" (`test_store.py:310-321`, `:833-848`). For a `.gear.json`, `load` re-raises
  `UnknownSchema` without moving the file aside (`store.py:247-248`). The planning read `read_sidecar` returns None
  for a newer one and never writes (`:1808-1822`); a W9-era app reaches it only past a record it has already
  refused.
- **The pin to move is not one line but six** (must-fix 3): `== 10` at `test_store.py:227` and `:1123`,
  `test_workbook_bands.py:353`, `test_workbook_carry.py:51`, `test_workbook_user_record.py:56` and
  `test_workbook_window.py:312`. The last is package C's file, and the bands and user-record files are in no package.
- **F3.** §4.1 says "a part with an allowance or a flat is written at link schema 12". Read literally, that makes the
  link record's schema depend on its content, while F1's 11 is unconditional. Make it one policy. Also,
  `test_store.py:833` parametrises a literal 12 as "newer", which stops being true at F3.

## 4. Gearboxes already built, and D11

**What the first Update SolidWorks writes, traced in code under the plan's assumed answer.** For each app gear,
dog, sleeve and hub part whose Backlash cell is blank:

- `_part` finds the built spec machined and the wanted spec printed. `name_changed` is False, since neither has a
  typed Part name and only a typed name decides. `same_part` is False, since the Backlash text differs.
  `_ignored_fields_as_built` ignores `nozzle` and keeps `process`. `_structural` finds nothing, and the printed
  equation needs no new global. So the part is changed in place by its values.
- **The one write to each part is the global `"Backlash"`**: `0.3 * "Module"` becomes the IIF. At the user's module
  1.25 the value goes from 0.375 to 0.3 mm. That is a tooth 0.075 mm *thicker* at the pitch circle, about 0.035 mm
  normal on each flank, and the pair's play falls from 0.75 to 0.6 mm. **Printed is tighter than Machined at every
  module above 1.** At module 1 and below the value is equal, but the text differs, so the part is still written.
- A part whose Backlash cell is typed is not written: its literal stands, and with equal plans `changed` stays
  False.
- **The records.** The link record is written at 11, each changed entry's `spec` gains `process` and `nozzle`, and
  each part's `.gear.json` is rewritten at schema 3 (`updated_sidecar`, `store.py:386-399`). From then on the
  W9-era app waits on this gearbox.
- **No gear moves.** The phase is the centre of the tooth space (`geometry.py:8`), and backlash widens the space
  about it. That is read from the code, not measured.
- **The W9c landing guard (`swbuild._landing_route`) foresees no landing for this change.** I computed
  `line_landings` from `0.3 × module` to 0.3 mm for Sun 29, Planet 13, Ring 55, a dog 17, the sleeve 17 and a hub
  17 at module 1.25, and for rings of 55 at m1.5, 30 at m2 and 40 at m3. Each line's new start lies about a whole line
  length from its old end (Ring 55 at m1.25: 0.626 against 0.625), far from the 0.2 threshold. This is a pure
  calculation, not a run on SolidWorks.

**Do W9a's rules cover it?** Yes, as they cover any value Update, and to no greater degree. K11 sees nothing, since the
live Backlash equals the record. K4's footer says what will change before the press. K2's puts and refusals are not
met, since no gear moves. K3 keeps the user's features and names any rebuilt into error afterwards. A user mate on a
tooth face re-solves by about 0.035 mm, as it would for any change of values; W9a does not refuse that before a write,
for this change or any other. On 2024 the first press on a freshly opened RangeBox costs 3.3 to 4 GB (W9c). The only
thing new is that the user did not ask for this change.

**D11, for the coordinator to put to the user:**

- **(A) Opens as Printed and changed (the plan's assumption).** The first time you open your gearbox after F1, the
  window says every gear has changed since it was built, only because Process is now Printed: each gear's backlash
  would go from 0.375 to 0.3 mm, the teeth a little thicker. Nothing is written until you press. Update SolidWorks
  then rewrites that one equation in every gear part in place, keeps your sprockets, housing and keyway, and moves
  the gearbox's records to a version the older app will not open. Build again… would instead make every gear a new
  part. To keep it as built, you add a row "Process | Machined" to its Box sheet.
- **(B) Stays Machined until you type Printed.** It opens exactly as it does today: nothing changed, nothing to
  press, nothing written. New gearboxes and New workbook… are Printed. When you want this one printed, you type
  Printed on its Box sheet and press Update SolidWorks.

**My recommendation is (B).** It is what the strip already does for an old part. It keeps D2's "a part already built
reads Machined" true for the gearbox as well as the part. It writes nothing to the user's files that they did not
ask for, so no unrequested heavy first press on 2024. It makes the third `made_new` reason, the footer's Process
sentence and the D11 board unnecessary, or reduces each to one line. **Its rule must be keyed on what was built, not
on the schema number.** Any F1 write moves the record to 11, so a rule "schema 10 or below means Machined" would
flip the gearbox to Printed after its first Export or Apply fix. Say instead: a blank Process means Printed when the
record's current parts hold none built machined, and Machined when they were all built before F1 (no `process` key).
It is a second meaning of a blank cell, as the plan says, but it is the meaning "as built", which the user already
has for the strip.

## 5. The rulings

- **Open point 1, machined in code: sound**, with must-fix 1 and 5 and should-fix 6.
- **Open point 2, K9 stands for printed sleeves: sound.** K9 is an axial gap. A printed part's first-layer squish
  spreads the bed face outward in the plane of the bed, not along the shaft. The axial error is a layer, about 0.2
  mm, and the faces' places are the user's housing. The 0.5 mm floor covers both. One sentence of the argument is
  loose: the 0.3 mm "for two printed surfaces" is §2.2's radial figure, not an axial one. The conclusion does not
  rest on it.
- **Open point 3, a Process line for every gearbox: show it always.** Under (B) the Machined ones are the ones
  that need saying. It moves the window's pinned text for machined gearboxes as well, so list
  `test_workbook_window` under "What must not move" as moving by that line.
- **Open point 4, the printed pair check replaces W7's planetary sentence: sound**, if it replaces the warning only.
  `checks._check_stages` also fills `report.undercut`, which becomes `Plan.undercut`, the clause of the build's
  interference sentence (`gearbox.py:280-282`). A printed stage must still fill it.
- **Open point 5, link 11 whatever the process: sound.** It follows W9b's 8 and is simpler than a content-dependent
  schema. The cost, that the W9-era app waits after any F1 write, is the same as every W9 stage's.
- **Open point 6, F2's export refuses unsaved or mismatched parts: sound.** `SaveAs3` exports the open document,
  which is not the file while it is unsaved.
- **Elsewhere.** D10's "only a part built printed carries `_P`" agrees with `name_changed`. No Process property is
  right. Workbook Format 1, with an older app building an unbuilt F1 workbook machined, is the failure W9b
  accepted. Printed-only checks keep the rule.

## 6. F1's readiness

**The definition of done and the tests are nearly complete.** Add to the tests:

- the machined `.gear.json` pin, including `derived`;
- K11's set-back words naming the exact IIF;
- `to_dict` on a bad Process word not raising, and dropping a typed Nozzle when machined;
- `report.undercut` still filled for a printed planetary;
- the Box sentence when the Process row is missing;
- the six schema pins.

Under (B), the Done-when line "a workbook built before this plan opens as changed" becomes "opens Machined and
unchanged, and after Printed is typed Update carries it". The 2026 run of a copy of `setup.master` then types
Printed first.

**The packages' files are disjoint in `src`, not in `tests`.**

- B's store bump breaks C's `test_workbook_window.py:312` and two test files no package owns.
- The tests that read the committed xlsx are in ten files (`test_workbook_axes`, `_bands`, `_build`,
  `_demo_fixtures`, `_export`, `_model`, `_modes`, `_motion`, `_planetary`, `_xlsx`). Only `test_workbook_modes` is
  in a package, though BEFORE_W7 in `test_workbook_planetary.py:388` reads the same three files.
- Those tests fail only when B's blank-is-Printed reading and A's printed maths are both in. That is at the merge,
  with no owner.

**What F1-0's interface must fix so that A, B and C cannot collide:**

1. In `spec.py`: the fields and words; a `to_dict` that drops both keys for any machined spec (blank, any case, a
   typed nozzle), never raising; the `_P` stem.
2. **The printed backlash itself:** the two constants, the IIF text in the five writers and the four derives. It is
   small, pure and moves no machined pin, and without it B's and C's printed tests cannot tell printed from machined
   until A lands.
3. **On every derived class** (`SpurDerived`, `InternalDerived`, `RackSection`, and through `section` the helical and
   bevel ones): `backlash_printed` and whatever carries process and nozzle to `section_diagnostics`, the ring's own
   diagnostics and `mesh_warnings`. Either the derived gear carries them, or those functions take keywords. Each
   `to_dict` leaves the new fields out when machined.
4. The pair check's signature and return (sentences, level, which gear), the ring-pair clearance, the printed tip,
   and `solve`'s keyword names. **Stubs return neutral values rather than raise**, so B's and C's printed paths run
   before A lands.
5. `Box.process` and `Box.nozzle`, `Setting.words`, and a test helper that marks a read workbook machined. Each test
   that pins anything of a committed xlsx is marked in F1-0.
6. The six schema pins moved with `LINK_SCHEMA_VERSION` 11, `_W9D_LINK_SCHEMA` and `PRINTED_SCHEMA`.
7. The `UpdatePlan` field, the `made_new` reason's name and phrase, and the `_SPEC_COLUMNS` label.
8. The words of every new sentence, with the D11 sentences in both forms until the user answers.

**Before D11 is answered:** F1-0 can be written, with its D11 words left in both forms, and so can A. C can be
written but for the footer's Process sentence, the Process case of `_reuse_advice` and the board of a W9-era
gearbox. B should wait: `_read_box`'s blank rule, the `made_new` reason and the `UpdatePlan` field are what D11
decides. The plan's own §8 says D11's other answer is cheap only before B.

## 7. The gear maths, recomputed

- **D3.** The smaller of 0.3 mm and 0.3 × module thins each tooth by `j` at the pitch circle. Each flank moves
  `(j/2) cos α` = **0.141 mm** square to it from module 1 up, and 0.141 × module below; for a helical gear it is
  `(jn/2) cos αn` in the normal plane. The bevel toe gets `(R − b)/R` = **0.702** of it at 20/40, module 1.5, face
  10. The IIF equals `0.3 × module` at module 1 and is never larger. All as the plan says. It is smaller than
  machined above module 1, which the user should know (§4).
- **The thin tip after backlash against a 0.4 mm line** (`spur.profile`, backlash 0.3):
  - At module 1 it is 0.271 at 12 teeth, 0.365 at 20, **0.396 at 25 and 0.401 at 26**, and 0.446 at 40. So module 1
    warns **below 26 teeth only**. *"Warns at module 1 (0.27 to 0.45 mm from 12 to 40 teeth)"* is contradicted from
    26 teeth up.
  - At module 1.25: **0.402 at 11** (0.375 at 10). It passes from 11 teeth, not 12.
  - At module 1.5: 0.305 (6), 0.379 (7), 0.437 (8), 0.581 (12), 0.712 (20), as the plan says.
- **Radial clearance.** Unshifted it is 0.4 m to module 1.25 and 0.25 m above. At m 0.75 it is 0.2999999999999998,
  so the tolerance is needed. A ring pair works out the same both ways (pinion tip to ring root, ring tip to pinion
  root, each 0.4 m). Bevel at 0.188 m is under 0.3 below **m 1.596**. All as the plan says.
- **The outside pair condition** `ra₂ ≤ √(rb₂² + (C sin α)²)`, unshifted at 20°: 13 clears up to 16, 14 up to 26, 15
  up to 45, 16 up to 101, 17 up to 1309. Confirmed. **"12 and fewer clear nothing" is one-sided and not literally
  true.** 12 clears mates of up to 10 teeth, 11 up to 7, 10 up to 4, 9 up to 2, 8 up to 1, and 6 and 7 none. Each such
  mate is itself not cleared back, so the true statement is that no pair containing a gear of 12 teeth or fewer
  clears both ways. The check, being made both ways, gives that.
- **The ring condition** `ra₂ ≥ √(rb₂² + (C sin αw)²)` is right. The four cases come out as stated: RangeBox 13 in 55,
  33.125 against 33.526, at risk; planetary_4to1 18 in 54, 26.000 against 26.108, at risk; Risky_Placements 14 in 36
  at β 20°, transverse, 36.310 against 36.711, at risk; E4 24 in 72, 35.000 against 34.811, clear.
  **A consequence the plan does not state:** unshifted at 20°, a pinion of 17 teeth or fewer clears no ring at all,
  18 needs a ring of 161 teeth or more, 19 needs 86, 20 needs 64, 24 needs 40 and 30 needs 34. So nearly every
  printed planetary will carry this warning. The sentence should say what clears it: a positive shift on the planet,
  or a shorter ring addendum, which the app does not offer. The interference itself is just as real for machined
  gears (KHK's `z₁/z₂ ≥ 1 − tan αa₂ / tan αw`). It is printed-only here for the rule's sake, and the sentence
  should not imply that printing causes it.
- **§2.4, the undrawn flank.** The involute starts above the form diameter from 26 teeth at modules above 1.25, and
  from 47 at 1.25 and below; backlash does not move it. At module 1.5 and 40 teeth the gap is 57.96 against 57.59 mm
  on the diameter. The drawn radial line below the flank's start holds the tooth's angle at its start value, which
  is less than the involute's at any lower radius. So the drawn tooth is thinner there than the true one. This costs
  a little contact near the root and never adds material, and walls printed fat give some of it back. That is from
  the geometry, not measured. Leaving it to the first prints is sound.
- **Also confirmed:** the base helix angle at 45° (41.6°), `Δj = 2 tan α Δa` = 0.728 Δa, the module floor 1.0, the
  rim floor 1.2 mm against one module, and a sleeve's relief at 0.5 m a side.

## 8. Before F1-0 starts

**Must fix:**

1. Keep the new derived fields out of the record: each derived class's `to_dict` drops them when machined, or they
   live outside the dataclass. As written, F1-0's interface commit changes every machined `.gear.json` and fails
   §2.7's pin.
2. Name every derived class (`SpurDerived`, `InternalDerived`, `RackSection`, and the helical and bevel classes
   through `section`), the ring's own diagnostics, and how process and nozzle reach `section_diagnostics` and
   `mesh_warnings`, which see no spec. Correct "no signature changes".
3. Move all six `LINK_SCHEMA_VERSION == 10` pins in F1-0, not only `test_store.py:227`.
4. Give the tests that read the committed xlsx (ten files) an owner. Best: F1-0 adds a helper to mark a read
   workbook machined and marks every one that pins a plan, count or sentence.
5. Replace *"type Machined in Box!B9"*. A workbook from before F1 has Units in B9 and no Process row; the user must
   add a row labelled Process.

D11 must also be answered before package B is written. That is a sequencing rule, not a fault in the text, and the
plan already says it.

**Should fix:**

1. §2.2's tip figures: module 1 warns below 26 teeth only, and module 1.25 passes from 11.
2. Reword "12 and fewer clear nothing" as a statement about pairs.
3. Give K11's set-back words their own source, since `_back_words` prints `_blank_meaning`'s text.
4. Stubs return neutral values, and F1-0 lands the printed backlash equation and derive.
5. When the printed pair check replaces W7's sentence, `report.undercut` stays filled.
6. `to_dict` never raises, and drops a typed Nozzle when machined; say that a machined spec does not round-trip its
   nozzle.
7. The ring-pair sentence: say how common it is, what clears it, and that it is not caused by printing.
8. Paths: `src/gear_generator/probe/` for p1, p7 and p8. Say "five" xlsx consistently.
9. The CLI `python -m gear_generator.gears` plans machined; name it or give it a key.
10. Make F3's link schema 12 one policy with F1's 11. Note that `test_store.py:833`'s literal 12 must change then.
11. Open point 3 moves the window's pinned text for machined gearboxes; list it.
12. Say that a new part built from a loaded old record's form is machined.
13. Under (B), rewrite D11, §1's "what the default carries", §6's W9-era bullet and the Done-when line, and key the
    blank's meaning on the record's parts, not on the schema.


---

# Third check, of the revision to the second review (2026-11-18)

**Read at `ffe8812`** (the revision, with the coordinator's ruling of D11 as (B)), against the code at `5de0290`. Since
`ffe8812` the code has changed only in `findings.py` and ten lines of `swbuild.py`, which move none of the plan's
citations; K11's functions are still at `:5423`, `:5460` and `:5484`. The figures in §3 below come from a
pure-Python sweep of the app's own outlines (`kind.outline`, recipe A) in a `git archive` scratch copy, since
deleted. Nothing was run on SolidWorks or in the suite.

## 1. The five must-fixes

- **1, the derived gear in the record: fixed at its cause.** `nozzle: Optional[float] = None` is the one new field,
  on the three section classes. `printed` and `backlash_printed` are properties, so `asdict` never sees them,
  and the four `to_dict`s drop `nozzle` while it is None. A machined `.gear.json` is then W9's byte for byte, and
  the pin over the whole file can hold at F1-0's commit.
- **2, every derived class: fixed.** The checks read the process and nozzle from the derived gear, so the signatures
  stay as they are.
- **3, the schema pins: not quite.** `git grep` at `ffe8812` finds **ten** lines pinning the literal 10, not eight.
  The two the plan misses are `test_workbook_carry.py:79` (`["link_schema_version"] == 10`) and `:1057` (the
  same). Both are in a file F1-0 already touches, so the fix is two lines. But F1-0 written to the list of eight
  would be red at its own commit. Better still, say "every literal 10, found by grep at the cut", since the W9 work
  still landing tonight may add more.
- **4, the tests over the committed workbooks: fixed.** F1-0 owns the ten files, adds one helper, and marks inside
  `test_workbook_demo_fixtures.assessed`.
- **5, *Box!B9*: fixed.** The sentence is gone. Under (A), the sentences kept for a later switch name the cell only
  when the row exists.

**A collision the revision brings in (must-fix).** `test_workbook_model.py:24-27` pins `schema.BOX_SETTINGS`'s
titles exactly. Adding Process and Nozzle is listed under B (`workbook/schema.py`), but the pin is in a file only
F1-0 may touch, so B's commit would fail a test B may not edit. And the settings cannot land alone. `to_sheets`
writes `box_values.get(key, "")` for every setting, so without `box_values` mapping `process` and `nozzle`, a
gearbox built in code would be written with a blank Process. Read back with no record, that blank is Printed. **So
F1-0 should take the two `Setting`s, `to_sheets`' two `box_values` keys and that pin together.** B keeps
`_read_box`'s word check and `template`.

## 2. D11 as (B), keyed on the record's parts

**The rule is sound.** `LinkRecord.parts` holds gear parts only; the layout and the assembly are on `gearbox`. So
"current parts, none built printed" means what it says. I traced its cases:

- a fresh workbook (no record, or a journal only) is Printed;
- a gearbox built before F1 is Machined, and so is a v1 record whose parts carry no spec, which is right;
- a gearbox whose user typed Printed and updated, or one rebuilt printed, is Printed;
- a gearbox stopped part way, with any part printed, is Printed, so the rest of its parts read as changed;
- the schema moving to 11 changes nothing.

**It is one switch for what a blank means.** (A) would add three sentences, as the plan says.

Three should-fixes, all in C's `workbook_gui.py`:

- **Resolve inside `_assess`, not only in `_plan`.** `_assess` has a second caller,
  `raw = self._assess(reading.spec, reading.diagnostics)` (`workbook_gui.py:692`), which feeds `wb_link.consequence`.
  It must resolve the blank the same way.
- **Pass no record when the record beside the workbook is another workbook's** (`store.foreign_workbook`, a copy
  not yet settled). Otherwise a copied workbook would read Machined from its original's parts.
- **Leave no blank Process in the assessment.** `Assessment.read` keeps the unresolved Box. `Gear.spec_values` turns
  `""` into `GearSpec`'s default, which is machined, so anything that later builds a spec from `a.read.box` would be
  machined without a word. Resolve `read`'s Box too, and test that nothing in an `Assessment` holds `""`.

## 3. The planetary warning and the half-nozzle margin

**The measure itself is the problem, not the margin.** `√(rb₂² + (C sin αw)²) − ra₂` is how far the mate's tip
circle reaches past the pinion's tangent point. It is not how far the mate's tooth runs into the pinion **as the app
draws it**. Below its base circle the app draws a radial line and a fillet, not a tooth a hob would leave. And the
mate's tip reaches only 1 m past its pitch line, where a hob reaches 1.25 m.

I swept the two drawn outlines through three pitches. The app's phases were used, the detector was checked to find a
clash when one is forced, and depth was measured normal to the boundary:

| Pair (m, teeth) | Radial reach | Overlap, no backlash | Overlap, printed default | Printed, each flank 0.1 mm fat |
|---|---|---|---|---|
| ring 12 in 54 (1) | 0.369 | 0.025 | 0 | 0 |
| ring 14 in 54 (1) | 0.278 | 0.013 | 0 | — |
| ring 16 / 18 / 20 in 54 (1) | 0.191 / 0.108 / 0.029 | 0.006 / 0.002 / 0.001 | 0 | — |
| RangeBox 13 in 55 (1.25) | 0.401 | 0.023 | 0 | 0 |
| ring 14 in 54 (2) | 0.555 | 0.026 | 0 | 0 |
| ring 15 in 60 (1.5) | 0.333 | 0.012 | 0 | — |
| Sun 29 / Planet 13 (1.25) | 0.122 | 0.001 | 0 | 0 |
| outside 6 / 30, 8 / 40, 10 / 40, 12 / 60, 13 / 80 (1, 1.5) | 0.62 to 0.24 | 0.067 to 0.005 | 0 | — |

"Printed default" is 0.3 mm per gear. "Each flank 0.1 mm fat" is the flank offset only, taken as an effective
backlash of 0.087 mm. A dash is a case not run.

- **Every ring case clears once each gear has 0.04 mm of backlash.** The printed default's 0.3 mm leaves about 0.12
  mm per flank for the printer before any overlap.
- **The worst outside case, 6 / 30, needs about 0.08 mm.**

The deepest point is, as expected, below the pinion's base circle, for example at radius 7.40 on RangeBox's planet,
whose base radius is 7.64.

**Which pairs would warn.** With the half-nozzle margin, RangeBox 13 in 55, the 12 and 14 in 54 and the 14 in 54 at
module 2 would warn, and the 18 in 54 would not. All of them clear in the drawn parts with the default backlash.

**Limits of this sweep.** These are inferences from the app's outlines, not measurements:

- **Not modelled:** a printed tip's radial growth, a helical or shifted pair, recipe B, and SolidWorks' built
  geometry beyond its being the same sketch.
- **Sampling:** 40 to 150 positions over three pitches.

**Verdict: neither the margin nor the plain warning is a sound default.** Both rest on a measure that reports an
interference the drawn parts do not have. The margin would keep the warning on RangeBox, which clears by about 0.12
mm a flank, and would drop it elsewhere by accident rather than by geometry.

**Recommendation.**

- **For F1:** a printed planetary keeps W7's sentence word for word, as a machined one does. Add no pair interference
  warning, and keep the single gear's printed undercut sentence.
- **For the warning itself, later:** build it on a sweep of the drawn outlines with the gear's own backlash, less a
  printer allowance of the size D3 already budgets (about 0.1 mm a flank), warning on any overlap. This is pure code
  beside `internal.tip_clash`. That function samples the pinion only above its base circle, which is why it reads
  near zero. The sweep would be rated once §3.2's prints give the printer's real figure.
- **If the coordinator wants the warning in F1 regardless,** its signature (§2.8 item 4) must take each gear's recipe,
  since the outlines need it, and `PairWarning.depth_mm` must mean overlap, not reach. That has to be settled before
  F1-0 is written.

## 4. F1-0's interface, and whether it may start

**The interface is now precise.** Items 1 to 8 give names, defaults, stub returns and owners, and the packages' files
are disjoint in `src` and in `tests`, with three exceptions:

- the ten schema lines (§1);
- `BOX_SETTINGS` and its pin (§1);
- item 4's pair-check signature, which depends on §3's ruling.

**F1-0 may start once `printed` is cut, with those three settled in the plan first.** Each is a sentence or two.
After F1-0, A can start once §2.3 is rewritten, and B and C can start as they are, with §2's three should-fixes
going to C.


---

# Last check, of the revision to the third check (2026-11-18)

**Read at `5e5d5c1`**, against the code at `67ee901`. No new calculation was run; the figures are the third check's
sweep. Nothing was run on SolidWorks or in the suite.

## 1. The third check's points

**Each is taken.**

- **The schema pins.** The plan lists ten lines, and `git grep` at `67ee901` finds the same ten: `test_store` 227
  and 1123, `test_workbook_bands` 353 and 367, `test_workbook_carry` 51, 75, 79 and 1057, `test_workbook_user_record`
  56, and `test_workbook_window` 312. F1-0 moves every literal that grep finds at the cut, which is the right rule.
  `probe/w9d_demonstration.py:1007` is rightly noted, not moved.
- **The Box settings.** The two `Setting`s, `to_sheets`' two keys and the pin at `test_workbook_model.py:24-27`
  go into F1-0 together.
- **The pair-check signature** is withdrawn with the check.
- **C's three should-fixes are all in:** `_assess` resolves the blank for both its callers (`:692` included), it
  passes no record when the record is another workbook's, and `read`'s Box is resolved too, held by a test.

## 2. No pair warning in F1

**Sound on the sweep, and stated honestly**, with one omission.

- **What §2.3 says, and the figures are the sweep's:** at the printed default every swept pair clears; with no
  backlash the overlap is 0.005 to 0.067 mm, against the radial measure's 0.11 to 0.62.
- **The limits are named:** what was swept (recipe A, unshifted spur outlines, five rings, five outside pairs, Sun
  and Planet) and what was not (helical, shifted and bevel pairs, recipe B, a tip's radial growth).
- **What F1 does with the rest:** it leaves those cases unchecked rather than checking them by a measure shown to
  overstate.
- **The bevel caveat:** dropping the bevel pair check is by analogy, not by sweep. §2.3's "not modelled" list
  makes that plain enough.

**The omission (should-fix, wording only).** The plan does not say what a user who **types a small backlash**
meets. The overlap appears below about 0.04 mm of backlash a gear for the rings swept, and below about 0.08 mm for
the 6 / 30 outside pair. Under those values the drawn parts can overlap by up to about 0.03 mm (rings) and 0.07 mm
(6 / 30) with no warning, and a printer's fat walls add to that. One sentence in §2.3 should say so, and that the
single gear's "turn the pair in SolidWorks" is then the only guard.

**The single gear's undercut warning stands.** For a machined gear the generated undercut it describes is real,
and its words are unchanged. The printed sentence is true of what the app makes: made as drawn, no undercut, the
mate not checked, turn the pair in SolidWorks.

**For the user, on D6** (it departs from the decision "warn, and check each printed pair"):

> We had planned that the app would warn whenever one printed gear's teeth might run into the bottom of the
> other's. Checked against the gears as the app actually draws them, that warning would have fired on almost every
> printed planetary for a clash the parts do not have. With the printed default backlash none of the pairs checked
> touch, and even with no backlash the most is 0.07 mm. So F1 adds no pair warning: a small gear still says it is
> printed exactly as drawn and that you should turn the pair in SolidWorks, and a proper check is planned after your
> test prints. Helical, shifted and bevel pairs were not checked this way, and if you type a backlash under about
> 0.1 mm the parts may touch slightly without a warning.

## 3. Readiness

**Ready.** F1-0 may start once `printed` is cut, and then A, B and C together. The small-backlash sentence can go
into the plan or into F1-0's interface note; it changes no interface.

---

# Review of stage F2 as made ready to execute (2026-11-18)

**Read at `dce5aff` on `printed`**, which holds `6d616fa` (section 3, 3.0 to 3.4, and *Changes before F2*); `src`
is unchanged since `61460b9`, the commit the plan was read against. Nothing was run on SolidWorks or Excel, and the
suite was not run. The figures below are from scratch scripts run with `PYTHONPATH=src` against this checkout's
`gears/spur.py` and `gears/helical.py` (import path checked), plus an independent closed form and, for the spur
rows, the span read off the app's own drawn outline (`SpurGear.outline`). KHK's *Gear Technical Reference* page on
tooth thickness was fetched; its formulas are images there, so only its text is quoted. ISO 21771 was not available.

## 1. The span over k teeth (§3.0)

**The formula is right, and every W in the table is right.** The transverse form (`W_t = (k−1) p_bt + s_bt`, `s_bt
= d_b (s_t/d + inv α_t)`, `W_n = W_t cos β_b`) and the closed form `W_n = m_n cos α_n [(k−0.5)π + z inv α_t] +
2 x m_n sin α_n − j_n cos α_n` are the standard base tangent length (KHK's span measurement, Tables 5.10 and 5.11;
DIN 3960 and ISO 21771 give the same as I know them, not checked here; the backlash term is the usual `A_Wk = A_sn cos α_n`). The `− j_n cos α_n`
term is right for this app because `helical.derive` thins the transverse section by `j / cos β` (`helical.py:354`),
so its backlash is a normal one. I recomputed all nine rows three ways (the plan's first form from the derived gear,
the closed form from the spec alone, and for four spur rows the span measured off `SpurGear.outline`'s recipe-A
points, whose involute property held to 1e-15 rad). **All nine W agree with the plan to 1e-4 mm**, and so do the
seven spur contact radii.

**k is right for every spur row, shifted included**: the usual `zα/180° + 0.5` gives 2.72, 2.72, 1.83, 3.83, 3.72,
1.94 → 3, 3, 2, 4, 4, 2, and KHK's shifted rule gives 2.62 → 3 for z 15, x +0.3. The contact radius rule picks the
same.

**k is wrong for the second helical row, because the contact radius is wrong for helical gears (must-fix M1).**
The jaws' common normal is the base-cylinder tangent inclined at β_b, with the jaws ±W_n/2 along it from the tangent
point; projected on the transverse plane that is W_n cos β_b, so

    r_c = √(r_b² + (W_n cos β_b / 2)²)      not √(r_b² + (W_t / 2)²)

(the same for spur, where β_b = 0). With the right radius the plan's own nearest-to-`r + x m_n` rule agrees with
the textbook k (ISO 21771's rule through `d_M = d + 2 x m_n`, as I know it and computed it here):

| Gear | Plan k, W_n | Right k | W_n (W_t) at right k | r_c at k 3 / k 4, pitch r |
|---|---|---|---|---|
| helical m_n 2, z 20, β 15° | 3, 15.0972 | **3** (ISO 2.95) | 15.0972 (15.5645) | 20.713 / 21.890, 20.706 |
| helical m_n 1.5, z 25, β 20° | 3, 11.4156 | **4** (ISO 3.80) | **15.8438 (16.7315)** | 19.376 / 20.062, 19.953 |
| (β 30°, m_n 2, z 20: not in the plan) | rule gives 3 | 4 (ISO 3.79) | 21.2255 | 22.338 / 23.260, 23.094 |

11.4156 is a correct span over 3 teeth of that gear (its contact, r 19.38, is on the drawn involute), but the test
would pin a k the textbook does not choose, and the error grows with β. The table row, the `r_c` formula and the
`Span.contact_d` the interface names change; the face condition for that row becomes `15.8438 sin 18.747° + Δb`.

**Should-fix on §3.0:**

- **Bound the contact.** Withhold the span (or take the next k) when r_c falls below where the app's involute
  starts (`max(flank_start_d, form_d)/2`; below it the app draws a radial flank) or within a small margin of the tip.
  None of the nine rows is near either (the Planet's 8.112 against 7.635 is the closest), but a z 6 or a negative
  shift could be.
- **The narrow face.** KHK's text gives `b_min = W sin β_b + Δb` with "Δb > 3 mm to make a stable measurement";
  the plan's 2 mm is under it. And for a **herringbone** the b is one half, `HelicalDerived.half_width` (face/2 less
  half the groove, `helical.py:183`), which the plan does not say.
- **Recipe B (arcs).** The span is a constant only on an involute. On the m 1.5, z 20 printed gear drawn with
  arcs, the span read off the outline runs from 11.139 to 11.221 mm across the flank, 0.08 mm, about the size of
  what the user is measuring. Show it for recipe A only, or say *approximate* for B.
- **A ring** is measured over pins (balls for a helical ring), not balls only; the wording.
- **The check owed by package A** "against a worked example in ISO 21771 or KHK" may not be obtainable (ISO is
  sold; KHK's web formulas are images). Let the check also be the outline route above: the span read off the
  drawn outline equals the formula for recipe A, which tests the app's own backlash and shift conventions, which a
  textbook example cannot.

**What a measured span tells the user, and the arithmetic back.** The jaws read square to both flanks, so
`e = (W_measured − W) / 2` is how far the printer pushed each flank out, square to it, on spur and helical alike.
That is right. D3's 0.3 mm leaves `0.15 cos 20° = 0.141` mm a flank; less a printer's 0.10 it leaves 0.04, so
`j = 2 (e + 0.04) / cos α` keeps 0.04 mm a flank a gear (0.16 mm normal play for a pair), and e = 0.10 gives
0.298 (0.3 stays), as the plan says. Three should-fixes:

- write `cos α_n` of the gear, not `cos 20°`, in the Measured line;
- **a floor**: below e ≈ −0.04 mm the formula gives j ≤ 0, and §2.3 found drawn parts overlapping under about
  0.04 mm a gear (0.08 for a 6 / 30 pair);
- **D3's promise "never more than today's"**: a printer adding 0.12 mm gives j = 0.34, more than 0.3 × module
  below module 1.13. Setting D3 from the measurement moves the IIF's breakpoint (`"Module" <= j / 0.3`) as well as
  its constant, which the plan should say, and which is the user's to accept (U4).

## 2. The STEP probe (§3.1.2)

**The calls.** `IModelDocExtension.SaveAs(path, 0, 1|2, null, out, out)` is in the macro database exactly as the
plan cites it (`API-LEDGER.md:190`, `entries/files/04`), *Verified, SW 2026, Airfoil Converter 2026-09-16*, through
the same `_out_long()` and `_null_dispatch()` this repo's `swcom` has, on the active part. **Unverified, as the
plan says:** 2024; non-zero codes; the schema and unit written; a non-active document; a modified one. Also
unverified and not said: exporting a part **loaded only as a component of an open assembly**. `GetSaveFlag`,
`CloseDoc` (discards, no prompt, parts on both versions), `OpenDoc6` and `ActivateDoc3` are verified on both
versions in the ledger (lines 107-116, 150, 171). One choice is not argued: the app already calls `SaveAs3` on the
same `Extension` with the same typed nulls on both versions (`swcom.py:1366-1376`); the ledger says to prefer
`SaveAs`. Either is fine; F2-0's note should say which and why.

**Safe on a live session?** Yes, as written: scratch parts in the run's folder, titles recorded, only its own
documents closed unsaved, the dialog watch, fresh sessions. Steps 1 to 7 cannot overwrite anything of the user's
(step 5 overwrites its own file on purpose). Two points:

- **Step 8 (a part built into error) asks a question nothing depends on**, adds the one dialog the run expects, and
  on 2026 a What's Wrong box is the STOP. By the handoff's rule (a probe only for a call that could hang, raise a
  dialog or damage; a point the app does not depend on written as a caveat) it should be dropped, or run last on
  its own copy with the box allowed on both versions. *A ruling.*
- **Record the save flags of the user's own open documents** before and after, not only their titles.

**Does each finding gate exactly what depends on it?**

- `STEP_EXPORT_ON_<year>` gates the press per version, both steps 2 and 4 needed. Right.
- `SAVE_AS_COPY`'s row says *the export is not offered*; the next row says the button is *shown and enabled* and
  refuses. Say one thing.
- `STEP_EXPORT_NEEDS_ACTIVE_ON_<year>` is measured on parts in their own windows, but the Workbook window's press
  meets parts that are components of an open assembly, or not open at all. And `Session.export_step` exports the
  session's *build document*: a part already open becomes that by `use_open_document` (no activation,
  `swcom.py:3528`), one not open by `open_document`, which **always activates** (`:3546-3606`). So *activate=False*
  is only reachable for parts already open. The probe should export a part open only as an assembly component (the
  assembly's save flag read too), and the interface should say how each part becomes the build document, that the job
  closes only what it opened (never the assembly; the ledger's line 113 records a 2024 *Save Modified Documents* box
  on closing an assembly) and gives the user back the document that was active. **Must-fix M5**, since the probe
  gets one follow-up round per version.
- **Step 6's "the file is right" is not defined.** Define it: the file's text equal to step 2's but for the
  `FILE_NAME` header line, and unlike step 4's.
- `STEP_FILE_CHECK` is one name in the interface (§3.3) but *per version* in §3.1.4. **Must-fix M2, below.**

**Checking the file as text (§3.1.4).** Reading the frame, the solid count and `OPEN_SHELL` is sound and safe, and
never reopening a STEP file is right (`GOTCHAS.md` §20). Two faults:

- **The schema and the unit are not version facts.** The AP is the user's *Tools > Options > Export* setting (the
  plan says so in §3.1.1), and the unit follows the document. Pinning what the probe's session wrote would refuse
  every file of a user who exports AP242, with the list left unwritten. Accept the frame, exactly one solid, no open
  shell, a `FILE_SCHEMA` among AP203, AP214 and AP242, and a length unit the check can read (millimetre expected;
  Bambu Studio reads others through OpenCascade); log the rest as facts. `STEP_FILE_CHECK` then needs no per-version
  value. **Must-fix M2** (it changes F2-0's finding names).
- **What it misses.** A file with one closed solid of the wrong shape: another document's part (the activation
  question), a part as it was before an unsaved change (refused before, but the check would not catch a fault in
  that refusal), a scale or unit slip, a body with a cut missing. A cheap text check catches all of these: read the
  `VERTEX_POINT` coordinates and require the largest radius from the axis to be the part's `da/2` and the axial
  extent its face width, each to 0.01 mm (the build's frame is the app's own). Also count entity instances
  (`= MANIFOLD_SOLID_BREP(`), not substrings, and refuse `SHELL_BASED_SURFACE_MODEL`. Should-fix.

## 3. The export itself (§3.1.3)

**Refusals.** Unsaved, mismatched against the record (W9a's marks), globals not the record's (K11's read,
`swbuild.py:5407`), a feature in error, a workbook that Update would change, the whole set or nothing: right, and
nothing is written before every part has passed. One citation is wrong: the feature-error read is not at
`swcom.py:900-925` (that is `MateState` and `ComponentInfo`) but the `GetErrorCode2` helper at `:1083-1095` and the
build walk at `:2614`/`:2816`. And `Session.has_unsaved_changes` (`:1161`) reads the build document only.

**Nothing of the user's is overwritten or saved**, provided the probe shows `SaveAs` with *copy* leaves path, title
and save flag alone, which is what it asks. W9's rule holds: the user's features in a gear part go out in the file
and are named in the list; nothing in the assembly, the layout or a carrier is touched; no build, Update or Build
again… path changes. F1's rule holds: a machined part is exported, nothing of it changes, and its Derived panel
stays (but the list's *span over k teeth* "for an external spur or helical part" contradicts E1's *never a
machined gear*: say which).

**Names: must-fix M3.** *A name that exists gets `_r2`, `_r3`, as a part does.* In this app `_r2` already means a
part's second revision (Build again…). Print revision 1's `Gear_m1.5_N20_P` twice and you have
`Gear_m1.5_N20_P_r2.step`, which reads as the file of the part `Gear_m1.5_N20_P_r2.SLDPRT`; build that revision and
print it, and its file must become `…_r2_r2` or `…_r3`, either misleading. The list's own name is not said to take a
suffix at all, so a second press could overwrite it. A folder per press, `print\<Box name> <date time>\`, holding
the files and the list, never reused, removes the clash, keeps each set whole and lets the window name the set. *A
ruling* (it changes `PrintPlan.folder` and `list_name` in the interface).

**A set that fails its check after export** leaves files with no list beside them, and the next press writes the
whole set again. With a folder per press, name that folder *not checked* or write a list that says *do not print*.
Should-fix. Also say that the app makes the `print` folder before the first export.

## 4. The user's step (§3.2)

**Could someone who never saw the plan follow it?** Nearly. It is in order, names every field and what to type, and
the figures it quotes are right (11.209 for m 1.5, z 20; k 4 and 21.223 for m 2, z 30; outside diameter 33.0).
What is missing or may mislead:

- **Where the files are**: *the `print` folder inside the Output folder you built into*, and that a list file is
  there too.
- **The seam.** §3.2 says *Seam position: Aligned*; the list says *the seam kept off the tooth roots*. Say one thing,
  and tell the user to measure away from the tooth that carries the seam. (Whether Bambu Studio's *Aligned* puts a
  gear's seam in the roots was not checked here.)
- **The jaws.** Zero the calipers, close with the same light force each time (the thumb roller, not a squeeze), and
  for a helical gear (the explainer) let the calipers tilt with the teeth: *square to the axis* is for spur gears.
- **Which average.** The average of the twelve smallest-steady readings; any reading 0.05 mm off the rest is taken
  again.
- **The bore coupons' range and the rule's gaps.** Small FDM holes often print 0.1 to 0.3 mm under (my
  understanding, not measured), so all four may come out (a) or (b). The rule "(c), or between (b) and (c) if none
  is (c)" says nothing when two are (c) (take the smaller), when none is (b) or (c) (print +0.4 to +0.7, or −0.1
  and below if all are (d)), or which face the shaft enters from: try it from the top face and from the bed face,
  where the first layer narrows the hole. A round coupon also says nothing about F3's D-flat, whose flat is a
  straight wall; say so.
- **One size cannot tell shrink from a fat wall.** ΔW on one gear mixes a fixed flank growth with PLA's
  size-proportional shrink (a few tenths of a per cent, about 0.02 mm a flank over 11 mm). Printing one m 2, z 30
  gear beside them (k 4, 21.223) separates the two. Optional, about twenty minutes of printing.
- **The record of the print.** Add to the table: the printer, the filament (brand, colour), Bambu Studio's version,
  the nozzle, and any setting not as listed.
- **Bambu Studio's STEP import** may show a mesh-precision dialog in recent versions (not checked here): keep its
  default, since a coarser mesh lays chords inside the involute and shrinks the reading.

**Are the numbers used correctly?** The span gives e, square to the flank, and D3's j follows correctly from the
0.04 mm a flank the plan budgets (§1 above, with its floor, its cos α_n and its breakpoint). The bore allowance is a
grade, used as F3 needs it (F3's `Bore Allowance` added to the bore diameter). Both stay on the user's word.

## 5. Readiness

- **Disjoint files:** A (`gears/span.py`, `test_span.py`), B (`printout.py`, `swcom.py`, `swbuild.py`, four test
  files) and C (`gui.py`, `ui_text.py`, `workbook_gui.py`, `design/`, `README.md`, three test files) are disjoint,
  and F2-0's stubs in B's and A's files come first. **But the sentences have two owners (must-fix M4):** B's
  `PrintPlan.refusal` is a string, `export_step` raises "with a sentence" and `print_parts` returns a result, while C
  owns "every refusal and result sentence, the gate sentence" in `ui_text`. Either F2-0 stubs the `ui_text` functions
  B calls, with their exact words in the interface note, or B returns codes and C words them. Say which, and who
  checks the per-version gate (the planning read or the job).
- **The interface** also leaves `form_print(sidecar, ...)`'s other arguments and `PrintResult`'s fields open, and
  should name the K11 comparison B reuses (`workbook/update.py:3096`, private), so B does not need a file it does not
  own.
- **Tests owed, missing:** the helical k at β 20° (and a β 30° case), the contact bound, the herringbone half, recipe
  B, the Measured line's floor and breakpoint, the per-version gate, `_r2`/folder naming against existing revision
  stems and the list never overwritten, a part open only as a component, and that the job leaves the open documents
  and the active one as it found them.
- **Done when** should add the board and `UI-DESIGN.md`/`README.md` updated, and the interface reviewed.
- **Cost.** F1 was costed at six agent runs; its notes record about ten reviewed steps (F1-0 and its review, three
  packages, the review and its fixes, the demonstration script, its review, the runs and their review). F2's ten
  leave out the interface review, the should-fix round after the stage review, the review of the findings commit,
  and the probe's follow-up round the house rule allows. **Thirteen to fifteen** is the honest figure, and about 90
  SolidWorks minutes with one follow-up round per version (the 65 is the arithmetic of 10 + 15 + 15 + 25 and holds as
  the floor).
- **The button.** `design/UI-DESIGN.md` §2 puts **Build** and **Update values** in the form's **footer**; the
  **Output** panel is the folder, the templates and **Open .gear.json** (`:210-228`). *In the Output panel, beside the
  build buttons* cannot both hold: the footer is the place. In this app's names an ellipsis means a question or a
  dialog follows (**Export as…**, **Build again…**, **Locate…**); **Print files…** asks nothing, so **Print files**.
  The window's footer is drawn at 1080 px *with all four buttons* (`:623-628`); a fifth needs the board to show the
  sentence keeps its 400 px. And the form exports *the part active in SolidWorks*, which may not be the gear on the
  form: the SolidWorks bar should say which file it will write, as it does for Update values (`:216-221`).
- **Decisions taken silently:** the folder layout and repeat naming (M3); the D3 floor and breakpoint; refusing a
  print when only a shaft's place would change on Update (E3 as written refuses it; a print set does not depend on
  the layout); and dropping probe step 8.

## 6. Before F2-0 starts

**Must-fix** (each changes the interface note, the probe or a figure the tests pin):

- **M1.** The helical contact radius: `r_c = √(r_b² + (W_n cos β_b / 2)²)`; the m_n 1.5, z 25, β 20° row becomes
  k 4, W_n 15.8438 (W_t 16.7315); `Span.contact_d` follows.
- **M2.** `STEP_FILE_CHECK`: one set of accepted values (frame, one solid, no open shell, AP203/214/242, a readable
  length unit), not a per-version pin of the probe session's schema; the interface's finding names match.
- **M3.** Repeat presses: a folder per press, or a suffix that cannot be read as a part revision; the list never
  overwritten. A ruling, then the interface.
- **M4.** Who owns the refusal and result sentences between `printout`/`swbuild` (B) and `ui_text` (C), and who
  checks the gate.
- **M5.** The probe adds a part open only as an assembly component, and the interface says how each part becomes the
  build document, what is activated, what is closed, and what is put back.

**Should-fix** (can go into F2-0's note or the packages): the contact bound, Δb ≥ 3 mm and the herringbone half,
recipe B, the Measured line's cos α_n, floor and breakpoint, step 6's "right file" and step 8, the user documents'
save flags, the vertex-extent check, the failed-set folder, the list's span for machined parts, `SAVE_AS_COPY`'s
wording, the `swcom.py:900-925` citation, the button's place and ellipsis, the cost, and §3.2's items in section 4.

**Ready for F2-0 once M1 to M5 are in the plan or ruled.** None needs the user; M3 and step 8 need the coordinator.

---

# Re-check of the revision to F2's review (2026-11-18)

**Read at `a20108b`** (`docs/PLAN-PRINTED.md` §3 and *Changes after F2's review*), against the code at `dce5aff`. Small
scratch computations only; nothing run on SolidWorks, Excel or the suite.

## 1. The five must-fixes

- **M1, fixed at its cause.** §3.0 now gives `r_c = √(r_b² + (W_n cos β_b / 2)²)` with its derivation, and
  `Span.contact_d` becomes `SpanReading.contact_d = 2 r_c`. The three helical rows agree with my recomputation: β 15°
  k 3, W_n 15.0972, W_t 15.5645, r_c 20.713; β 20° k 4, 15.8438, 16.7315, 20.062; β 30° (new) k 4, 21.2255, 24.0448,
  23.260; the faces needed (`W_n sin β_b + 3`) 6.67, 8.09 and 12.97 mm, β_b 14.076°, 18.747°, 28.024°. Each k is the
  textbook one. **Should-fix:** the table gives no face width, and the β 30° gear at the default face of 10 mm is
  under its 12.97, so its test would read *narrow face*, not the figure. Give that row a face (14 mm, say).
- **M2, fixed.** No schema or unit is pinned; the check accepts AP203, AP214 and AP242 and any unit it can read, counts
  instances, and refuses a surface model; `STEP_FILE_CHECK` is withdrawn. Two should-fixes: match the schema by its
  name's prefix (SolidWorks writes the name followed by `{ 1 0 10303 … }`, and AP203's second edition is
  `AP203_CONFIGURATION_CONTROLLED_3D_DESIGN…`, not `CONFIG_CONTROL_DESIGN`; step 3 will show which); and the
  vertex-extent check should not refuse a part that holds the user's own features (a boss of theirs can pass the
  tip circle): there it is a fact in the list, not a refusal.
- **M3, fixed by the ruling.** A new folder per press, by date and time with a counter, `print list.txt` inside it,
  `_r2` left to revisions, and a failed set's list headed *DO NOT PRINT THIS SET*. Nothing can be overwritten.
- **M4, fixed.** B returns codes and structure, C's `ui_text` owns every sentence and the list's text, the interface
  note gives each code's sentence once, and B checks the gate in planning and in the job. Disjoint as before, with
  F2-0's stubs in `ui_text.py` added to its files.
- **M5, fixed.** Probe step 7 exports a part open only as an assembly component, with a measured fallback, and two
  findings gate them; the job says how each part is reached, reads everything before any export, closes only what it
  opened (never an assembly) and puts the active document back. The citations hold (`active_document` `swcom.py:1131`,
  `save_flags` `:3837`, `_squash` `swbuild.py:1414`, `_value_edits` `:5424`). Two should-fixes:
  `GetOpenDocumentByName` is *Unverified* in the ledger (`API-LEDGER.md:94`) and new to this app, so the note should
  say step 7 is its first use; and a **lightweight** component is not covered: the 12 : 1 fixture has been opened
  lightweight in W9a's runs. Say that a part whose component is lightweight is treated as not reachable (fallback or
  refusal), and have step 7 or the demonstration show it.

## 2. The arcs ruling

**Sound.** No figure and *choose Involute to measure* is the least misleading of the three choices, the coupons are
Involute, the list says the same, and `span(derived, recipe)` carries the recipe. It covers helical arcs gears too.

## 3. Dropping the part-in-error step

**Safe and true, as written.** The app refuses a part with a feature in error in the job, on the form and in the
window, after all reads and before any export (§3.1.3), so it never makes the export the step measured, and the
caveat says exactly that. One should-fix: say whether a feature whose `GetErrorCode2` is non-zero with `IsWarning`
True refuses. Refusing a warning would block a user's part that SolidWorks itself builds; I would refuse errors and
name warnings in the list. (Opening a part in error on 2024 can show a What's Wrong box, as W9's Update meets
already; that is not new to F2.)

## 4. The user's instructions

All my points are in: where the files are, the import precision, the seam, zeroing and light force, the tilt on a
helical gear, the mean of twelve with re-takes, both faces for the shaft, the coupon-range gaps and the D-flat
caveat, the optional second size, the record of what was printed, the floor, `cos α_n`, and the breakpoint put
plainly as the user's choice. One wording gap: a user whose shaft is over 18 mm prints all four at module 2, z 30,
so their optional Coupon_E should then be the other size (module 1.5, z 20), or it measures nothing new.

## 5. Readiness

**F2-0 may start.** M1 to M5 are fixed at their causes; what is left are the should-fixes above (the β 30° row's face,
the schema prefix, the extent check beside user features, `GetOpenDocumentByName` as unverified, lightweight
components, warnings against errors, Coupon_E for large shafts), each of which fits in F2-0's interface note or its
probe without changing the plan's structure.

---

# Review of stage F3 as made ready to execute (2026-11-18)

**Read at `2656479` on `printed`**, which holds `674d315` (§4, 4.1 to 4.6, and *Changes before F3*) against the code at
`f28cb75` (`src` unchanged since). Nothing was run on SolidWorks or Excel, and the suite was not run. Figures are from a
scratch script (plain Python, the formulas below); the code was read in this checkout (import path checked). The macro
database was read at `/home/m0obot/SW-Macro-Database` (`API-LEDGER.md`, `GOTCHAS.md` §27 and §35). Two web searches
were made on FDM hole fits; Bambu's wiki page itself could not be fetched (HTTP 402), so what it says is quoted from the
search's summary and marked so.

## 1. The bore allowance (§4.1)

**What it is in the part.** One global, `"Bore Allowance"`, a literal in mm, present only when not 0, and the bore
sketch's `Bore` dimension (a circle, so a diameter: `findings.CIRCLE_DIMENSION`) linked to `"Bore Diameter" + "Bore
Allowance"` in place of `"Bore Diameter"`. Positive enlarges the hole; `"Bore Diameter"` stays the shaft. It is on the
diameter, so the wall moves by half of it. It reaches spur, helical and herringbone gears (`helical._bore_ops` calls
`spur._bore_ops`, `helical.py:417-418`), dogs and hubs (`clutch._Clutch._as_spur` is a `dataclasses.replace` that
keeps every other field, `clutch.py:109-112`) and, through text in its two link expressions, the bevel's revolved bore
(`bevel.py:881-893`). A ring has none (`internal.py:972`, `:1026`) and a sleeve, an internal ring, none either; its
banded relief is not a shaft bore. All of this is right, and every citation in §4.1 is at the line it names
(`swcom.py:1425`, `:1726`, `:1737`, `:1747`, `:1756`, `:1875`, `:1902`, `:1966`; `spur.py:913-916`, `:963-972`,
`:1025-1028`; `swbuild.py:1305`, `:1333`; `store.py:91`, `:426-432`), with one exception: the helical's globals
are at `helical.py:492`, not `:426`, which is `_property_sizes` (the custom properties). The bevel's globals
(`bevel.py:716`) need the new global too; the plan names only its expressions.

**0.2 mm on the diameter, as a placeholder.** It is on the diameter, which matches §3.2's coupons (shaft + 0.0 to + 0.3,
typed in Bore). As an FDM figure it is defensible as a starting point and no more, which is what the plan says it is.
What I found:
- Several fit guides put a running or sliding fit at about 0.2 to 0.4 mm total on the diameter. One table gives PLA
  0.15 to 0.25 mm for a sliding fit. They disagree on whether a figure is on the diameter or per side, so each must be
  read for its convention.
- Holes print under size. By the search's summary of Bambu's wiki, which I could not open: the nozzle drags the bead
  toward the hole's centre; Bambu Studio's *X-Y hole compensation* defaults to 0; and its example corrects a hole
  0.5 mm small with +0.25, so that setting is per side. One forum report has round holes about 0.23 mm small on one
  Bambu printer.
- So on a stock profile, 0.2 on the diameter may leave little or no running clearance: a snug fit for a gear fixed to
  its shaft, tight for one that must spin free (an idler, a planet, a gear riding on its shaft until a dog engages
  it). The coupons decide this (V1), so the figure needs no change before code. Two points follow:
  - **A user who sets hole compensation counts it twice.** §3.2 already prints the coupons with X-Y hole compensation
    0 (`PLAN-PRINTED.md:1239`), and the README should tell the user to keep it at 0 for parts printed with the
    calibrated allowance. Should-fix (C, README).
  - **The coupon instructions break when F3 lands (must-fix M3, §6).**

**"A blank is *as built*" is the right rule, and it is not inert as written: must-fix M1.**

*The principle.* D11's (B) applied to a number is sound. Every part on record before F3 has no `"Bore Allowance"` in
its recorded `variables`, so it reads as 0, and moving the 0.2 later rebuilds nothing.

*Where the plan applies it.* In one function, `gearbox.as_built_allowance(entry)`, used "where planning turns a row
into a spec for a part on record", naming two places: the workbook's planning and the strip's `_update_target`. In the
code a blank allowance on record is read in many more places than those two, and each of them plans a spec with no
entry at hand:

- **Reuse.** `gearbox._Parts.find` (`gearbox.py:579-615`) compares each recorded entry with a job that the assessment
  planned from the row before any record was read, through `_matches` → `same_part` and `_variables_match`
  (`:418-449`).
  - That job of a printed row with a bore carries `"Bore Allowance" 0.2`, and a part built in F1 or F2 does not, so
    it never matches, and Build again… makes every such part new.
  - The match decides which entry is the part, so the as-built figure cannot simply be read "for the row's entry"
    first. It has to be tried per candidate entry, the job replanned with that entry's figure.
- **Update.** `update._part` (`update.py:294-337`):
  - `same_part(built, job.spec)` replans the *recorded* spec through `_plan_of`, which under F3 gives a printed
    blank the current default and not what was built;
  - `_variables_match` then sees the planned `"Bore Allowance"` missing from the record;
  - so the press either says "its new values need the global "Bore Allowance", which the built part does not have, so
    it needs a new part", or reaches `planned_changes`' BuildError "not built by this tool" (`swbuild.py:1412-1421`).
  - `_ignored_fields_as_built` and `swbuild.structural_change` read raw spec dicts. There a blank cannot tell "built
    at 0.2" from "built before F3, at 0", so `has_allowance` beside `has_shift` cannot be judged from
    `(built, wanted)` as the plan places it.
- **Print files.** `printout.workbook_print` refuses a gearbox that `classify` says Update would change (F2), so every
  printed gearbox with a bore built before F3 would be refused. `printout.print_part` derives the recorded spec
  (`printout.py:292-330`), so the list's new bore line would say *+ 0.2 allowance* for a part cut without one.
- **The strip.** `self._derived["a"]` is derived from the form on every edit. `_update_target` (`gui.py:1745-1764`)
  and the Update values path (`:1870`, `:1945`) use it. The Derived panel's *Bore as cut* would say 8.2 for a part cut
  at 8. All of this is in `gui.py`, package C's file, while the rule is given to B.
- **K3 and K11.** K11's `_blank_meaning` sees a `GlobalVariable` only (`swbuild.py:5474-5486`), and a blank
  allowance is a literal there, so it would be said as typed. K3's `ui_text._expression_words` and `_value_under`
  (`ui_text.py:5003-5038`) would say *type 0.2 in Gears!X2 again* where the cell was blank. The plan covers K11's words
  (B) but not K3's (C).

*How large it is.* `GearSpec`'s default Bore is `"10"` (`spec.py:153`). So every printed part F1 and F2 built from a
form left at its default has a bore: the user's coupons, and the dogs and hub of a printed RangeBox. Without the rule
threaded through all of the places above, the first Update or Build again… after F3 on a printed gearbox does exactly
what D11 (B) exists to prevent.

*What F3-0's interface must say*, since `kind.derive(spec)` has no entry:
- **How the as-built figure travels**: a spec field that `to_dict` never writes, set by planning; or a resolved
  literal in `bore_allowance`. The second changes the recorded spec and makes `_changed_columns` say *its Bore
  allowance changed* for a hole that did not change.
- **Each call site above, and its owner.**
- **A rule for structural judging**: "has the global" taken from the recorded `variables` on the built side, and from
  the resolved figure on the wanted side.

*What I could not check*, and the threading should cover: whether `gearbox.py`'s own same-file checks
(`occupant`, `free_name`) and W9d's `carry_for` see a job planned before the record is read.

**Is it inert for every record W9, F1 and F2 wrote?**
- **Machined, yes**, once M1 is done. A machined blank is 0 with or without the rule; there is no global, the link text
  is unchanged and `to_dict` leaves the three keys out. So the bytes are W9's, as F3-0's pins will hold. Without M1 it
  is inert too, since machined never resolves to 0.2.
- **Printed, no**, until M1 is done: see above.
- **Two cases the plan does not say** (should-fix):
  - a part on record whose Process changes, in either direction, keeps its as-built figure. The column note *0
    machined* is then not the whole truth for a printed part made machined;
  - a typed allowance cleared on a built part does nothing (blank is as built), so the user cannot go back to the
    default by clearing the cell. *Bore as cut* shows it, which is enough if the explainer says so.

**Update SolidWorks after the user types an allowance on an existing gearbox.**
- **A part without the global** (built before F3, machined, or printed at a typed 0): the change is none to some, and
  so structural. Update refuses that part with the plan's sentence and Build again… makes it new. W9a's and W9d's rules
  cover it as they cover a Flank change:
  - the user's features in the old part stay behind and are named;
  - a mate of theirs on the old bore is named, not found again (K5).
- **A part with the global** (printed and built at F3 with a blank or a typed figure): the change is a value. W9c's
  Update sets the global in place, and W9a's rules cover it:
  - K11, if the user changed `"Bore Allowance"` in SolidWorks;
  - K3, if a feature of theirs in the bore (a keyway) goes into error. The sentence then names *Bore Allowance 0.2 to
    0.3 (Gears!…)*, with the blank-cell wording gap above.
- **Going from some to none** (typing 0) is refused as structural, though the part's global could carry 0. This keeps
  house precedent (Profile shift), so I accept it.
- **New, and not decided (should-fix S5, a ruling):** when a part on record is made new for another reason, does it
  keep its as-built allowance or take the current default? Under the plan, a Teeth change carried by Update keeps
  0.2, while the same change through Build again… gives a part at the new default. I would keep the as-built figure
  for every row whose part is on record, and let only a row with no part take the default. That is D11's spirit: the
  user's printed hole does not change as a side effect.

## 2. The D-flat (§4.2)

**The geometry, by my own calculation.**

The shaft's flat is `F − D/2` from the axis, `F` being the across-flat size measured to the opposite round side. The
hole is `R = (D + a)/2` and its flat is `h = F − D/2 + a/2` from the axis. So the hole is `h + R = F + a` across its
flat, and the flat wall takes the same `a/2` as the round. The plan's formula is right, and so is its figure. For D 8,
F 7, a 0.2:
- h 3.1000, R 4.1000, chord `2 √(R² − h²)` 5.3666, arc sweep 278.24°;
- the circular segment the flat keeps is 3.6752 mm², so the D's area is 49.1350 mm² against the circle's 52.8102.

Other cases, for A's tests:

| Case | h | R | chord | sweep |
|---|---|---|---|---|
| a 0 | 3.0000 | 4.0000 | 5.2915 | 277.18° |
| a 0.3 | 3.1500 | 4.1500 | 5.4037 | 278.76° |
| F 7.2 | 3.3000 | 4.1000 | 4.8662 | 287.20° |
| D 5, F 4.5 | 2.1000 | 2.6000 | 3.0659 | 287.74° |
| D 3, F 2.5 | 1.1000 | 1.6000 | 2.3238 | 266.87° |

**The sketch is fully defined, but only up to its branch.**

*Counting.* The arc has 5 degrees of freedom (centre, start and end, less the equal-radius condition) and the line 4,
9 in all. The relations take 9: centre on origin 2, two shared ends 4, horizontal 1, radius 1, length 1. So
`GetConstrainedStatus` will read fully defined.

*Four solutions.* The dimensions are unsigned and the ends carry their identity, so four solutions satisfy every
relation. For `CreateArc`'s direction +1 (counter-clockwise from start, `swcom.py:1743-1748`; `API-LEDGER.md:385`):
- **The D wanted.** Start at the chord's −X end (−2.683, 3.1) and end at its +X end. This sweeps 278.24°, the major
  arc.
- **The plan's sketch does not fix this order.** `Arc(origin, start, end)` and `Line(start, end)` are written with the
  same `start` and `end`, and the natural reading, start on +X, draws the **81.76° minor arc**. Cut, that is a
  sliver, not a D.
- **The chord reflected to −h** with the same identities is the minor arc too, so the third solution is also a sliver.
  The fourth is a D with its flat at −Y.

*On Update.* The first build draws the right one, if A orders the ends right. An Update moves the dimensions and lets
SolidWorks solve from where the sketch was. This is W9c's situation: the ring's `Li+` was solved to the far side
after a one-tooth change, came out code 72, and did not recover (`gears/landing.py`'s docstring; `HANDOFF-WORKBOOK.md:
214`). The D has two shapes that invite the same:
- **A near-zero chord.** As F nears D the chord goes to 0: 1.277 mm at F 7.95 and 0.572 at 7.99, with D 8 and a 0.2.
  The plan's check only forbids F ≥ D, and that is the near-zero line W9c measured failing.
- **A near-diameter chord.** As F nears D/2, h goes to 0 (0.15 at F 4.05) and the reflected solution is 2h away.

*A negative allowance.* The plan does not say whether one (a press fit) is allowed. If it is, "Flat not more than half
the bore" is the wrong test: with a −0.1, F 4.04 passes it and gives h −0.01, a chord past the axis and a minor arc. The
condition is h > 0 as cut.

**Every call is one the app makes; one expression is not (must-fix M4).**
- *The calls.* `CreateArc`, `CreateLine`, `SketchAddConstraints` (coincident, horizontal), `AddDimension2` on an arc
  (`findings.ARC_DIMENSION = "radius"`, `findings.py:85-88`) and on a line, `FeatureCut4` and `Add2`. Each is in
  `swcom.py` at the lines cited and verified in the ledger (`:157-158`, `:281`, `:382-387`).
- *The expression.* The chord's link is written `2 * sqr ( R * R - h * h )`, "the app's guarded sqr" at
  `spur.py:1158`. That comment says the opposite: SolidWorks 2026 refuses `sqr ( 0 )` and `IIF` does not guard it, so
  the app writes square roots as `( abs ( … ) ) ^ 0.5` (`spur.py:1157-1162`; `GOTCHAS.md` §27, *"Write square roots as
  `( ... ) ^ 0.5`"*). No equation the app writes contains `sqr`: `grep "sqr ("` finds only that comment and the tier-1
  probe. `sqr` of a positive number works (the probe's `sqr ( 16 )`), so this is not a hang, but it is a form the app
  has never written. The house form is `2 * ( abs ( R * R - h * h ) ) ^ 0.5`.
- *Is a major arc's dimension a radius?* `ARC_DIMENSION` was measured on minor arcs. A diameter would make the link give
  half a hole, which the first build's volume or STEP read catches at once. That is the plan's "measured by the first
  build", and right.
- *The shared point.* `GOTCHAS.md` §35 is about a line drawn *starting* on another entity's end. The line's other end
  landing on the arc's start is not covered there. Either way `Session.relation` skips a coincident between one point
  and itself and adds it otherwise (`swcom.py:1860-1875`), so neither case is a risk.

**"New in kind, measured by the first full build": right as the house rule reads, with one change of order.**
- None of the calls can hang or damage a file. A wrong branch is a feature in error. On 2026 that is a What's Wrong box,
  and so the run's STOP, in the run's own part.
- The plan's `update` section changes Flat by only 0.2 (7 → 7.2, h 3.1 → 3.3), which tests nothing about branches.
- **Should-fix S6:**
  - make the D's value changes their own early section, as W9c's `landing` was: Flat 7 → 5 → 7.8 and back, Bore
    8 → 10 with Flat 7 → 9, an allowance 0.2 → 0.4, and the bounds A sets;
  - judge each by volume against the same D built from scratch;
  - and A's tests assert that the drawn points satisfy every relation, with a sweep over 180°.
- With that, no separate probe is needed before the full build. If the section shows a far-side solve, it gets one
  follow-up round, as W9c's did.

**Where the flat sits relative to a tooth.**
- One tooth space is centred on +X (`spur.py:4`, `:1394`), so +Y is z/4 pitches from a space centre:
  - on a space centre when z ≡ 0 (mod 4): 12, 16, 20;
  - on a tooth centre when z ≡ 2 (mod 4): 14;
  - a quarter pitch either side otherwise: 13, 15, 17, 25, 29.
- A helical gear's teeth turn along the face, so it is that at the Front plane only.
- **A pair's phase:** no. Each shaft turns as a whole, so a gear's phase is its shaft's, and the layout rotates each
  component to mesh.
- **Two gears fixed by D-flats to one shaft:** their phase to each other is set by the parts, and the assembly does not
  model it, since the layout rotates each gear on its own. This matters only where the mesh graph closes a loop, for
  example two meshes between the same pair of D-fixed shafts. A planet on its pin, or a gear free on its shaft until a
  dog engages, is not fixed. Say it in the README. A defined angle would cost nothing (the chord vertical, the flat on
  +X, centred on a space for every z), and that is the coordinator's choice, not the user's. Should-fix S8 (G6).
- **W9d's carry: no.**
  - `_bore_mm` becomes the hole as cut, and §4.4's "bore" needs a coaxial cylinder of radius `bore_mm/2` to 1e-4 mm
    (`swbuild.py:7168`, `:7537-7538`). The D's arc face is a partial cylinder of radius R, coaxial, so it qualifies; the
    flat is a plane, *a face of Sun*.
  - `COAXIAL_FACE_READ` was verified on full cylinders only (`W9D-INTERFACES.md:793`, `:848`). A partial one reading
    its radius by `CylinderParams` is very likely the same and is not shown; the plan shows "bore" against the fake
    only, which I accept as a caveat.

## 3. The record (§4.3)

**Link 12 whatever the parts, and older apps.**
- An F2-era app refuses a link record of 12 and a `.gear.json` of 4. It raises `UnknownSchema`, leaves the file
  byte-identical (`store.py:220`, `:1473`), and the planning read returns None. That is right, and it is the policy F1
  set.

**Sidecar 4 by the spec cannot see a blank allowance: must-fix M2.**
- §4.3 says a `.gear.json` goes to 4 "when its part has the allowance global or a flat". F3-0's item 6 says
  `sidecar_schema` gives 4 "for a spec with an allowance or a flat". `sidecar_schema` takes the spec dict only
  (`store.py:91-97`). A printed part built with a blank allowance has the global and no `bore_allowance` key, so the
  second reading writes it at sidecar 3.
- An F2-era strip then opens it, and its Update values writes `store.updated_sidecar(…, variables)` with F2's planned
  globals (`gui.py:1945`), which drops `"Bore Allowance"` from the record.
- After that, F3 reads the part as built at 0 while SolidWorks holds 0.2:
  - Update plans a link it does not hold;
  - W9d's `_bore_mm` misses the bore;
  - the print list misstates the hole.
- This is exactly what the bump exists to prevent. Decide sidecar 4 from the recorded globals (`"Bore Allowance"` or
  `"Bore Flat"` present), or from the spec resolved by M1, and pass what is needed to `built_sidecar` and
  `updated_sidecar`.
- Two existing pins take a side here: `test_printed_rule.py:458` (`GearSpec(process="printed")`, bore 10 by default,
  sidecar 3) and `test_store.py:1600-1610` (the same spec, sidecar 3).

**The fifteen lines are not all of them.** The fifteen listed are right, and `test_store.py:833`'s 12 is rightly
named. These pin the current schema too and are missing:
- `test_printed_rule.py:456`, `(LINK_SCHEMA_VERSION, _W9D_LINK_SCHEMA) == (11, 10)`. It becomes `(12, 11)` against
  `_F1_LINK_SCHEMA`.
- `test_printed_rule.py:457`, `(SCHEMA_VERSION, PRINTED_SCHEMA, …) == (3, 3, 2, 1)`. It becomes `(4, 3, 2, 1)` with
  `BORE_SCHEMA`. This test's name says 11 and 3, so "F1's `test_printed_rule.py` whole" (*What must not move*)
  cannot hold as written.
- `test_printed_workbook.py:367`, `== LINK_SCHEMA_VERSION == 11`.
- `test_store.py:1419-1426` and `test_workbook_user_record.py:85-91`. Each writes a raw 12 and expects *"schema 12,
  this one reads 11"*; at 12 the record is accepted and the test fails. Both become 13 and 12.
- `test_workbook_bands.py:378` (*"schema 11, this one reads 8"*) and `test_workbook_carry.py:96` (*"schema 11, this one
  reads 9"*), which become 12.

A `git grep` for `11` finds most of these but not the raw 12s, nor `(3, 3, 2, 1)`. Should-fix: F3-0 finds the lines by
what they pin, and by a run of the suite at its interface commit.

**What moves by design is wider than the plan suggests.**
- Because the default bore is 10, every `GearSpec(process="printed")` plan, sidecar, variables list or print list line
  that F1's and F2's tests pin gains the global and the summed link. That is `test_printed_gears.py`,
  `test_printed_workbook.py` (for example `:385`, a printed RangeBox's dogs and hub at sidecar 3),
  `test_printed_window.py`, `test_print_form.py`, `test_ui_text.py`, `test_printout.py` and `test_printed_rule.py`'s
  printed cases.
- The plan allows this, re-taken in F3-0 by name with each reason. F3-0 should count them before it starts, by running
  the suite with the default stubbed in, because the count sizes F3-0.
- **Machined, and printed parts on record, never move** once M1 and M2 are in. The machined pins F3-0 takes first are
  the right guard. The printed-on-record pin needs M1's threading to pass.

## 4. K11, the hub, the export

- **K11.**
  - `"Bore Allowance"` → `bore_allowance` and `"Bore Flat"` → `flat` in `update._GLOBAL_COLUMN` (`update.py:670`)
    are right, and K11 reads every planned global already (`swbuild._value_edits`, `:5437`).
  - The blank-allowance wording needs the as-built knowledge M1 provides, since `_blank_meaning` sees only the
    global.
  - K3's words in `ui_text` need the same (S4).
  - A user edit of the Bore Sketch's own dimension, as against the global, is not K11's, as today.
- **The hub row.** It takes all three through `_as_spur`, and W9b's rule (a hub's teeth, module and pressure angle are
  its sleeve's) is untouched. The flat's checks run in the delegate's `validate`, so a hub gets them.
- **Sleeve and ring rows.** Not said: what a typed Drive flat or allowance on a sleeve or ring row is. "Drive flat with
  no Bore" covers a blank Bore only. Say error or ignored (S7).
- **The export (F2).**
  - The size check is the largest radius from the axis (`d_a/2`) and the axial extent (`printout.py:89-91`, `:691`).
    A D-flat bore changes neither, and the dog, hub and bevel are skipped kinds anyway (`EXTENT_SKIPPED`, `:112`). So
    it still holds.
  - The print list's *bore 8 + 0.2 allowance, D-flat 7.5* must be taken from the record as built (M1), not from
    deriving the spec.
  - The demonstration's STEP read of the hole is the script's own, not the app's check:
    - "the bore's least radius" is right for a round bore: some vertex lies on each circular edge;
    - **h is not a radius.** The flat's corner vertices are at radius R. h is their Y in the part's frame, and the note
      should say so;
    - Done-when's "volumes … agree with the maths to 0.01 mm" mixes units. Say `small_pinion_check`'s 0.1 %.
- **Volume sensitivity.** For D 8 and a gear of about the area of a 30 mm circle:
  - the D against the round removes 0.52 %;
  - an allowance of 0.2 against 0, 0.36 %;
  - 0.3 against 0.2, 0.18 %.
  
  All are above 0.1 %, but not by much on larger gears. The STEP read is the exact check.

## 5. Readiness

- **Disjoint files.**
  - F3-0 comes first and alone. A (gears and `test_bore`), B (`swbuild`, `update`, `gearbox`, `printout`,
    `test_bore_workbook`) and C (`gui`, `ui_text`, design, README, `test_bore_form`) are disjoint in `src` and
    `tests`.
  - M1's strip side is in `gui.py`, C's file, while the rule is B's. Give C the strip's use of
    `as_built_allowance` by name (S10), or the rule falls between them.
- **Tests owed, missing.** Each of these should be named:
  - the as-built rule through `_Parts.find` (a pre-F3 printed part with a bore reused by Build again…), through
    `update._part` (unchanged, no refusal), through `workbook_print` (not refused) and through the strip (no Update
    button, *Bore as cut* 8);
  - M2's sidecar for a printed blank allowance, and an F2-era reader refusing it byte-identical;
  - the D's arc order and sweep;
  - h > 0 as cut, and the flat's bounds;
  - K3's blank-allowance sentence;
  - a ring or sleeve row with Drive flat;
  - the coupon instructions (M3).
- **The demonstration and its confirming build on 2024.**
  - The sections are right. Running all of them again on 2024 follows F1's and F2's precedent on `printed` rather
    than the handoff's lighter confirming build; either is defensible.
  - Add S6's D section.
  - "a W9a `setup.master` copy, Printed typed … nothing written by it" should say: nothing written *for the bore*.
    Typing Printed does change Backlash, which Update writes.
- **The cost.**
  - Sixteen to twenty agent runs is plausible; M1 makes B the largest package, and one more fix round is likely.
  - **The reason given for the SolidWorks time is wrong.** "F2's demonstration took about twice its estimate" is
    contradicted by its own note: the runs took 11.6 min on 2026 and 15.5 on 2024, against estimates of 31 and 48
    (`F2-DEMONSTRATION.md:388-389`, `:550-551`). What doubled was the plan's 15 and 25 into the script's estimate.
  - 35 and 55 minutes are therefore generous, which does no harm, but the sentence should say so.
- **Decisions taken silently**, beyond G1 to G8:
  - a new part replacing one on record takes the current default (S5, a ruling);
  - the coupon instructions after F3 (M3);
  - whether a negative allowance is allowed;
  - the flat's bounds (M4);
  - two gears on one D-shaft not phased by the app (S8);
  - the as-built figure kept across a Process change.

  None needs the user before code; S5 and S8 need the coordinator.

## 6. Before F3-0 starts

**Must-fix** (each changes F3-0's interface, a pinned figure, or what the user is told to do):

- **M1.** The as-built rule, made true where a blank allowance on record is read:
  - how the figure reaches `derive` without entering `to_dict`;
  - the reuse match tried per candidate entry (`_Parts.find`, `_matches`);
  - `same_part` and `_plan_of` on the recorded spec, `update._part`, `_ignored_fields_as_built`, and
    `structural_change`'s `has_allowance` from the recorded globals;
  - `printout`'s bore line and `workbook_print` through `classify`;
  - the strip's derive, `_update_target` and Update values;
  - K11's and K3's blank words;
  - each with its owner.
- **M2.** Sidecar 4 from the part's globals (or the resolved spec), so a printed part with a blank allowance is never
  written at 3 for an F2-era strip to write back without its global. Pin it, with `test_printed_rule.py:458` and
  `test_store.py:1610` re-taken.
- **M3.** §3.2 and the README's *Calibrating your printer* (`README.md:119-220`) are rewritten for F3: Bore = the shaft,
  **Bore allowance** 0, 0.1, 0.2, 0.3 typed (a typed 0 honoured), and the result read as the allowance itself. As
  written, a coupon built after F3 gains the 0.2 default on top of its typed offset, and V1's figure comes out 0.2 too
  large. Coupons already built stay valid as built.
- **M4.** The D sketch stated so that it cannot be built on the wrong branch:
  - the arc's start at the chord's −X end and its end at +X, direction +1, sweep over 180°;
  - the chord's link as `2 * ( abs ( R * R - h * h ) ) ^ 0.5`, not `sqr` (GOTCHAS §27);
  - the checks on the hole as cut: h > 0, which settles a negative allowance either way;
  - a least flat depth or chord, and a least h, so the near-zero chord W9c measured failing cannot be typed.

**Should-fix:**
- S1, the time sentence (§5);
- S2, the helical and bevel globals' lines (§1);
- S3, the herringbone's groove floor (`g.bore >= g.groove_d`, `helical.py`) on the bore as cut;
- S4, K3's blank-allowance words (C);
- S5, the ruling on a part made new;
- S6, the D's Update section first, by volume against from-scratch parts;
- S7, ring and sleeve rows with Drive flat or an allowance;
- S8, the flat's phase on a shared D-shaft (README, or a defined angle);
- S9, hole compensation kept 0 (README);
- S10, the strip's owner;
- the literal list by meaning (§3);
- h read as Y in the STEP check;
- volumes in per cent;
- a cleared typed allowance and a Process change said in the explainer.

**Not ready for F3-0 until M1 to M4 are in the plan.** None needs the user; S5 and S8 need the coordinator. On the
probe: by the house rule none is needed before the full build, provided M4 fixes the arc's order and S6 puts the D's
value changes first in the demonstration, where a far-side solve would show in the first minutes and get its one
follow-up round.


---

# Re-check of the revision to F3's review (2026-11-18)

**Read at `6f0a462`** (`docs/PLAN-PRINTED.md` §3.2, §4 and *Changes after F3's review*), against the code at
`f28cb75`. These are small scratch computations only; nothing was run on SolidWorks, Excel or the suite. The two
rulings (a part made new keeps its as-built allowance; the flat on +X, facing a tooth space's middle) are taken as
given.

## 1. The four must-fixes

**M1, the as-built rule, is fixed at its cause.**
- It has one home, `spec.as_built(spec, variables)`, written whole in F3-0.
- It sets `built_allowance`, which `to_dict` never writes, and `bore_allowance_mm()` reads it after a typed figure
  and before the default. So every `derive` sees the as-built figure without a record entry in hand.
- All nine callers are named with their owners: reuse per candidate entry, `update._part`,
  `structural_change`'s `built_variables`, Build again…'s made-new rows, Print files, W9d, K11, K3 and the strip.
  They cover every place I found, and the three I could not check (`occupant`, `free_name`, `carry_for`) are now
  tests in B.
- The pin of printed parts on record, written at F3-0's base, is the right guard.

Two small points for F3-0's note:
- `from_dict` keeps every known field (`spec.py:169-172`), and `built_allowance` will be one. So "never read by
  `from_dict`" needs an explicit exclusion.
- Say what `as_built` does with an **empty** `variables`: a journaled entry is matched with `()` (`gearbox.py:595`),
  and a v1 record has none. Treated as "on record, 0", a part built at 0.2 would be made new; that is the safe side,
  but say it.

**M2, the sidecar's schema, is fixed.**
- `sidecar_schema(spec, variables)` decides from the globals, and both writers pass them.
- Give `variables` a default of None ("as today"). Then the one-argument calls at `test_printed_rule.py:459-461` keep
  their meaning.
- `test_printed_workbook.py:530` (printed typed on a machined gearbox built before F3, parts at sidecar 3) is a useful
  extra check that M1 works: those parts have no global and must stay at 3.

**M3, the coupons, is fixed.**
- §3.2 now gives both tables, keyed on whether the form shows a **Bore allowance** row.
- After F3, the shaft goes in Bore and 0 (typed), 0.1, 0.2 and 0.3 go in the allowance, never both.
- The fit is read as the allowance itself, and coupons built before F3 stay valid.
- Package C carries the change into the README, and a test reads the README's table.

**M4, the D sketch, is fixed.** By my own calculation (R 4.1, h 3.1, chord 5.3666):

| Arc as drawn, direction +1 | Sweep | What it cuts |
|---|---|---|
| Start (h, +c/2), end (h, −c/2): the plan's | **278.24°** | the D, through +Y, −X and −Y |
| The chord reflected to x = −h, same ends | 81.76° | the sliver |
| The ends swapped | 81.76° | the sliver |
| Reflected and swapped | 278.24° | a D with its flat on −X |

So the stated start and direction cut the D at build, and A's sweep test forbids the sliver.
- The line, drawn from the arc's end to its start, shares the first point (GOTCHAS §35). `Session.relation` adds the
  second coincident.
- `vertical` is a verified relation (`findings.py:82`).
- The link is in the house form `( abs ( … ) ) ^ 0.5`.

## 2. "A tooth space centred on +X"

- **True as drawn for spur gears, dogs and hubs** (`spur.py:4`, `:1394`; dogs and hubs through `_as_spur`), and for
  rings (`internal.py:4`, `:828-841`), which have no bore.
- A bevel gear takes no D (G5), so its frame does not matter.
- **Helical and herringbone gears: not at the Front plane, as §4.2 says.**
  - A helical gear's section is drawn on a plane one overrun *behind* the Front plane (`helical.py:206-232`,
    `:558-564`), so the Front-plane face is already turned `hand · 360 · overrun / L` (`:226-229`).
  - A herringbone's section is on its mid-plane (`:553-556`), so it is the apex that has a space centred on +X.
  - Should-fix (wording): "on the section plane: for a helical gear one overrun behind the Front plane, for a
    herringbone its mid-plane".
- **One more caveat, unverified:** that a sketch on those offset reference planes keeps the model's +X. If it were
  mirrored, the space would be centred on −X, which is the same thing only when the tooth count is even. Nothing the
  app reads (volumes, size checks) would tell. The `kinds` section could read it from the STEP file: the flat's corners
  against a space's vertices. It is optional, since the assembly does not model the flat (ruling 2).

## 3. The bounds

- **The depth bound is about the shaft.** `R − h` equals `D − F` exactly, whatever the allowance, so "a flat at least
  0.3 mm deep" is a bound on the shaft's own flat depth.
- **`h ≥ 0.25 R`** depends on the allowance and is the guard against the reflected branch: the reflected solution is
  then at least 0.5 R away.
- For D 8 and a 0.2, Flat may be from **4.925 to 7.7**.
  - Refused: 7.71 (depth 0.29) and 7.8 (0.2); 4.9 (h/R 0.244); and 4.925 at a −0.2 (h/R 0.212). The negative allowance
    is handled.
  - Common shafts pass: 2/1.5, 3/2.5, 5/4.5 and 8/7.5, every one 0.5 deep.
  - The least chord at the depth bound is `2 √(0.6 R − 0.09)`: 3.08 mm at R 4.1, 1.84 at R 1.1.
- **One should-fix for the sentence.** A real shaft whose flat is under 0.3 mm deep cannot be typed as it is. The
  error should say to type a Flat at most D − 0.3, which leaves the flat a little rotational play, or to use a round
  bore.
- `dshape`'s values all lie inside the bounds:
  - 7 → 5 lands at h/R 0.268, near the edge, as intended;
  - 7.6 is 0.4 deep;
  - Bore 10 with Flat 9 gives h/R 0.80;
  - an allowance of 0.4 gives h 3.2.

## 4. The pinned lines

**The table in §4.3 is now complete**, as far as a search by meaning finds: `sidecar_schema(`, the schema constants,
`schema_version == n`, `reads n` and raw `link_schema_version` writes across `tests/`, fixtures excluded. Two
additions:
- `test_printed_workbook.py:385`, a printed RangeBox's dogs and hub built new with a bore, will move to 4. The plan
  leaves it to the suite run, which is enough.
- `:530` must not move (§1 above).

**Moving `test_printed_rule.py` 456 to 458 and 550 is not a loosening.**

| Line | Becomes | Why it is not weaker |
|---|---|---|
| 456 | `(12, 11)` against `_F1_LINK_SCHEMA` | It pins the current schema and its predecessor's constant, as before. |
| 457 | `(4, 3, 2, 1)` with `BORE_SCHEMA` | It keeps the three old numbers and adds one. |
| 458 | two cases: 3 with no global, 4 with `"Bore Allowance"` | It asserts strictly more. |
| 550 | 12 | A record is still read forward and written at the current schema, with `blank_process`'s answer unchanged. |

The test's name, `…_link_schema_11_and_…_sidecar_schema_3`, should be renamed with it.

## 5. Readiness

**F3-0 may start.** M1 to M4 are fixed at their causes, and the rulings are written in. What is left fits in F3-0's
note or the packages, without changing the plan:
- `from_dict` excluding `built_allowance`;
- `as_built` on an empty `variables`;
- `sidecar_schema`'s `variables` defaulting to None;
- the helical and herringbone wording of where a space is centred, and the unverified sketch-frame caveat;
- the depth bound's sentence naming the shaft.

The restated cost (seventeen to twenty-one agent runs, about 85 SolidWorks minutes) is consistent with F2's measured
runs.

---

# Review of stage F4 as made ready to execute (2026-11-19)

**Read at `a1a844c` on `printed`** (§5, 5.1 to 5.7, and *Changes before F4*). `src` and `tests` are unchanged since
`11f2a25`, the commit §5 was read against. Nothing was run on SolidWorks or Excel, and the suite was not run. Every figure
below is from my own scratch script, which imports the gear and workbook modules from this checkout (import path
checked). It does not reuse the plan's working:
- the 30° and 60° points are found from the fillet's centre as `spur.involute_flank` and `internal.involute_flank` give
  it, with a check that each lies between the arc's two ends;
- the load line is the numerically differentiated normal of the drawn flank at the tip, crossed with the centreline;
- Y_F is worked by beam statics, not taken from the formula;
- the torques are `checks.check`'s own, on each fixture marked printed.

On sources: the MITcalc page was fetched and read. ISO 6336-3:2006's sample PDF from iteh was fetched, but its text could
not be extracted here. The 2006 range of Y_S and the 60° tangent come from search summaries quoting the iteh preview; AGMA
2001's 70 % and Bambu's data sheet come from search summaries, and neither document was opened.

## 1. The formula (§5.1)

**Y_F from beam theory.** Take a cantilever tooth with the normal force F_n at its tip, along the flank's normal, at α_F to
the perpendicular of the centreline. Its bending part F_n cos α_F acts at h_F above the section of chord s_Fn, so
σ = 6 F_n cos α_F h_F / (b s_Fn²). The normal force is constant along the line of action and T = F_n r_b, so
F_n = F_t / cos α_n with F_t at the reference circle. Then σ = F_t/(b m_n) · 6 (h_F/m_n) cos α_F / ((s_Fn/m_n)² cos α_n):
the plan's Y_F, form and all. Like ISO and Lewis, it leaves out the radial part F_n sin α_F, which compresses the root.

**The ISO expressions, checked two ways.**
- MITcalc's page gives Y_F, Y_S, L = s_Fn/h_Fe and q_s = s_Fn/(2ρ_F) exactly as §5.1 writes them. It writes
  z_n = z/cos³β_b (so that is §5.1's "secondary source"), and T = π/6 for internal gears in its s_Fn and h_Fe, which is
  the 60° tangent. The iteh preview, as the search quoted it, gives 1 ≤ q_s < 8 for 2006 and the 30°/60° chord
  definition.
- **Independently:** I coded ISO's Method B for a hobbed gear (E, G, H, the ϑ iteration, s_Fn, ρ_F, h_Fe), with the load
  at the tip and the 1.25/0.38 basic rack. At z 20, x 0 it gives Y_Fa 2.800, Y_Sa 1.553 and Y_Fa·Y_Sa 4.347, which are the
  chart values I recall from ISO 6336-3 and DIN 3990 (2.8, 1.55, about 4.35). Its α_Fen, 29.5115°, is A3's α_F to the
  digit, since the tip of an involute is the same however the root was cut. So the expressions and the 30° method are as
  ISO has them. I could not read the standard: the chart values are from memory, and so is z_n = z/(cos²β_b cos β),
  which agrees with §5.1.

**The fillet the app draws.**
- *External gears:* 0.38 × module, `spur.FILLET_FACTOR` (`spur.py:94`). It is used printed or machined alike
  (`SpurGear.derive`, `:824-828`), and a helical gear's `fillet_factor` is the same.
- *Rings:* 0.15 × module (`internal.py:127`). A printed ring keeps it: `PRINTED_FILLET_FACTOR` 0.3 only sets the threshold
  of F1's warning (`internal.py:598-608`).
- A typed Fillet is used as typed. §5.1 is right on all of this.

**Q on the drawn arc, and the q_s ranges.**
- *Outside gears:* the 30° point is on the drawn arc in every one of the 1696 I swept (modules 0.5 to 3, teeth 6 to 300,
  14.5° to 30°, printed and machined, both recipes). q_s runs 1.213 to 3.544. The plan's upper 3.86 is not reproduced,
  which does not matter.
- *Rings:* the 60° point is on the arc in every ring that has an involute tip. At 20°, rings of 34 to 150 teeth give q_s
  7.78 to 8.97; from 14.5° to 30° the range is 7.09 to 11.26. So the ring is past 8 nearly always, as §5.1 says, and
  carrying the formula on is the right side to err.

**Two shapes §5.1 does not cover.**
- **A ring whose tips lie inside its base circle: must-fix M1.** At 20° that is every ring of fewer than 34 teeth
  (d_a = (z − 2)m < z m cos α). They validate with a warning only ("the last of each tooth is a straight radial line"), so
  they are built. Their tip corner is on the radial line, where there is no involute normal, so §5.1's load line is
  undefined. The plan's own sweep ("the 60° point on every ring", 20 to 150 teeth) must have done something with them,
  and it is not written down. F4-0 needs a stated rule. My proposal: load at the involute's start (the base circle, the
  innermost point the pinion can touch), with α_F taken from the normal there. The other choice is not rated, with a
  sentence.
- **Pointed teeth.** A tooth whose flanks meet below the outer diameter (tip thickness ≤ 0) is a validation error ("the
  teeth come to a point…"), so it is never built. `rate` should still say *not rated* for it rather than load a point
  past the apex, where my α_F stops matching the identity. Should-fix: name it among `rate`'s reasons.

**Where the app's tooth stands against ISO's.** §5.1 sets the app's Y_F against Lewis "as recalled" and calls the app 7 to
15 % weaker. Set against ISO's own generated tooth, with the load at the tip, unshifted and with no backlash:

| | ISO Y_Fa | app Y_F | ISO Y_Fa·Y_Sa | app Y_F·Y_S | app over ISO |
|---|---|---|---|---|---|
| m 2, z 20 | 2.800 | 3.326 | 4.347 | 5.549 | +19 % (Y_F), +28 % (product) |
| m 2, z 40 | 2.405 | 2.755 | 4.013 | 4.889 | +15 %, +22 % |
| m 2, z 100 | 2.195 | 2.546 | 3.939 | 4.656 | +16 %, +18 % |
| m 1, z 20 (depth 2.4 m) | 2.800 | 3.696 | 4.347 | 6.010 | +32 %, +38 % |

The chord shows why: s_Fn/m is 1.801 on the app's tooth at z 20 against ISO's 1.945. The point stands, but the size is
larger than §5.1 says. Should-fix: A's note compares with ISO's own tooth, in these figures.

**The 30° section is ISO's convention, not the beam's worst section.** The app's root is a fillet set on a radial line, so
the tooth narrows toward it. Scanning the fillet for the largest 6 h cos α_F / s², the worst section is at a tangent of
8° to 16°, and it reads above the 30° section by:
- A1 5.2 %, A2 3.6 %, A8 (m 1, z 12) 9.2 %, m 2 z 100 2.5 %;
- 3.9 %, 2.6 %, 7.4 % and 1.7 % once Y_S is taken at each point.

Keeping ISO's 30° is right, since Y_S is calibrated on it, but "exact" in §5.1 is about the geometry. Should-fix: A's note
says the 30° figure can read up to about 7 % low on small pinions.

**Helical gears.** The virtual spur gear is applied correctly:
- z_n = z/(cos²β_b cos β) gives A4 23.735, against 23.553 by z/cos³β_b and 24.103 by z/cos³β;
- normal module, normal pressure angle and normal backlash: the j that `HelicalGear.derive` takes is the normal one, and
  the section gets j/cos β (`helical.py:345-357`);
- F_t and d are transverse, and b is the face or a herringbone's 2 × toothed width.

The transverse-drawn fillet's radius in the normal section lies between ρ cos²β and ρ/cos β. At β 20° that moves Y_S by
at most about 3 % for A4 (exponent 1/(1.21 + 2.3/L) = 0.256), which A's note can say in place of "not exactly ρ".

**Layers, on a helical tooth.** §5.1's 0.035 counts only the shear from the axial force. The root's bending stress itself
runs along the fillet in the normal section, and at the 30° point that direction leaves the layer plane by
sin 30° · sin β = 0.17 at 20° (0.21 at 25°). That gives about 0.17 σ_F of shear between layers and 0.03 σ_F across them.
That is still small: Bambu's PLA Basic sheet gives 31 MPa across layers against 35 in them. So no derating is the right
answer (H11), but the figure in §5.1 should be the larger one. Should-fix (wording).

## 2. The worked rows, recomputed

**Single gears.** Every figure is reproduced to the plan's last digit:

| | Y_F | Y_S | q_s | Holds (N) | (N·m) |
|---|---|---|---|---|---|
| A1 | 4.1931 | 1.5749 | 2.131 | 38.614 | 0.5792 |
| A2 | 3.2708 | 1.6975 | 2.458 | 45.929 | 2.0668 |
| A3 | 3.3258 | 1.6685 | 2.370 | 45.952 | 0.6893 |
| A4 | 3.8769 | 1.6089 | 2.226 | 49.058 | 0.7831 |
| A5 | (as A4) | | | 32.705 | 0.5221 |
| A6 | 2.2574 | 2.5535 | 8.341 | 29.492 | 0.7963 |
| A7 | 3.4536 | 1.6274 | 2.288 | 45.369 | 0.6805 |
| A8 | 6.8916 | 1.4151 | 1.701 | 17.432 | 0.1046 |

Also reproduced:
- A1 machined 35.044 N, and A3's α_a − γ_a = 29.5115° (equal to my numerical α_F; the ring's α_a + γ_a = 13.3242°, equal
  too);
- the module 2 Y_F 3.326, 2.755 and 2.546, and 3.696 at module 1;
- A4's shear ratio 0.0345.

On recipe B the identity does not hold (A7's α_F is 35.14° against 30.30°), as §5.1 says.

**Meshes.** B1 to B7 are reproduced exactly, from `checks.check`'s torques:
- planetary_4to1: S 2, P 0, C 7.7624, held R 5.7624, so 92.593 and 88.926 N, shares 641.5 % and 616.1 %;
- Idler_Train, as §5.3 builds it (no diagnostics): In 1, Idl 0, Out 1.9208. G1's 66.667 N against G3's own 64.027, GI
  28.984 (0.7 × 41.406), 230.0 %, and 57.5 % at 0.25 N·m;
- RangeBox, RangeBox_Fixed and `RangeBox_W9.xlsx` in L: Input 10, Planet 0, Carrier 28.2145, held Ring 18.2145, so
  229.885 and 220.782 N, 1364.3 % and 1310.2 %. In H and N no Planet, Carrier or Ring torque exists, so the meshes are
  *not worked out*.

The kinematics agree with §5.2's reading:
- a planet's force is the member's torque over N d, × K_γ;
- the ring side comes out 0.98² of the sun side, because kinematics runs two mesh efficiencies through the stage; that
  does not matter here;
- an idler and a planet both show a shaft torque of exactly 0.

**Reversed bending.**
- A planet's tooth does bend both ways: the sun presses one flank and the ring the other, as on an idler.
- AGMA 2001's *70 percent of s_at for idler gears* is quoted in D04 and in C95 by several secondary sources, and one
  extends it to planets. ISO 6336-3:2019's Annex B (Y_M) is the ISO home of the same idea; I could not see its values.

**The six-to-23-times list.**
- Confirmed: planetary_4to1 6.41; RangeBox, RangeBox_Fixed and the W9 fixture 13.64 in L; E4 21.42 and
  TransferCase_Parallel 22.58 in 4L; Reducer_12to1 22.58; Arc_Move 6.90.
- **Risky_Placements reads 14.28, not 14.9.** Its worst is G5–G6 at 1428.0 % (G5's 723.563 N against G5's 50.670 N).
- 14.9 is reproduced exactly when G6, an internal helical ring, gives its force at d = z m_n = 72 mm instead of its
  transverse 76.621 mm: 2000 × 27.1656 / 72 = 754.6 N, and 754.6 / 50.670 = 14.89. So the plan's script slipped on the
  very rule §5.1 states (*F_t and d are transverse*).
- None of B1 to B7 is a helical mesh, and no A row is a helical ring, so nothing would catch the same slip in B's code.
  **Must-fix M2:** correct 14.9 to 14.3 in §5.3 and U-c, and add two pinned rows:
  - **A9**, ring helical m 2, z 36, β 20°, face 10, printed: z_n 42.723, d 76.6208, Y_F 2.0408, Y_S 2.6948, q_s 8.500 past
    the range, holds 61.823 N and 2.3685 N·m;
  - **B8**, Risky_Placements printed at 5 N·m: G5–G6 F_t 723.563 N (G6's own side 709.09), G5 50.670 and G6 61.823, G5
    the weaker, 1428.0 %. Beside it, the herringbone G3–G4: 453.154 N at b 12 (the overlap), G3 62.836 and G4 71.137,
    721.2 %.

**A wording that is false for a branch past a split.**
- In E4 and TransferCase_Parallel in 4H and 4L, the front drive (FDrive–FIdler–FOut) is `past_split`: it carries torque,
  but J17 does not share it out, so F4 says nothing of FIdler, a two-way gear, in any mode.
- That is §5.2's rule and it is acceptable. But §5.4's Results row *no torque here* would then be false: those teeth are
  loaded.
- Should-fix: two wordings, *turns unloaded here* (RangeBox in H and N, the front branch in 2H) and *the torque past a
  shared output is not shared out (not worked out)*, as `kinematics.Motion.shared` and `past_split` tell them apart.

## 3. The allowable stress, and what the user is told

**17 MPa as a default.**
- *What the plan's basis misses.* The print list names Bambu Studio, and Bambu's PLA Basic data sheet (V3.0, by the
  search summary) gives:
  - tensile strength 35 ± 4 MPa in X-Y and 31 ± 3 in Z (ISO 527, printed specimens);
  - bending strength 76 ± 5 in X-Y and 59 ± 6 in Z (ISO 178);
  - V2.0 gave 39 and 35 tensile.

  So *a third of the roughly 50 MPa a PLA datasheet gives* is not what the filament the app points at reports. 17 MPa is
  about half its in-layer tensile strength and under a quarter of its bending strength.
- *Not a fatigue figure.* Printed PLA's fatigue strength at 2 × 10⁶ cycles is reported at 10 to 25 % of its tensile strength
  (13.5 MPa in one dataset; secondary sources disagree). So 17 MPa is a one-time figure, which is what *once* says.
- *Why it is defensible.* As a provisional *once* default it holds:
  - σ_F includes the full notch factor (PLA is brittle enough that the notch counts);
  - the load is on one tooth's tip with Y_ε 1, worth 1.2 to 1.5 against load sharing;
  - and it sits at about half the in-layer tensile strength.
- **Should-fix:** D7's sentence, the README and the Box's note give this basis (a printed PLA data sheet's 35 MPa
  in-layer tensile strength, about half), not "a third of about 50".

**Layers and infill.**
- *Layers.* Printed flat, a spur tooth's root stress lies in the layers. The walls follow the outline, so the fillet's
  surface fibre runs along the beads, the best case and the one ISO 527's X-Y specimens measure.
- *Infill.* Bending is carried by the outer fibres, which are the five walls (2 mm a side). So even above module 2 the
  infill matters less than §5.1 implies: what weakens such a root is the seam between wall and infill, not the infill's
  density.
- The README can say both in a sentence.

**Is 6 to 23 times the truth, or a check too severe? The truth about the typed torques.**
- *Why the torques are high.* The fixtures' 5 and 10 N·m were typed for machined gearboxes before Printed existed. A
  steel tooth's allowable is some fifteen to twenty times 17 MPa.
- *How much margin the check stacks.* Against a best estimate of a one-time break (Y_ε about 0.75 at ε_α ≈ 1.5, the
  load at 35 MPa, no K_γ, no 0.7), the stack is about 1.33 × 2.06 = 2.7 for a plain gear and × 1.25 × 1.43 = 4.9 for a
  planet.
- *What that leaves.* Against a best-estimate break:
  - planetary_4to1 (6.4, a planet) is still about 1.3 times over;
  - Arc_Move (6.9, plain gears) about 2.5 times;
  - RangeBox (13.6, a planet) about 2.8 times;
  - Reducer_12to1 and TransferCase_Parallel (22.6, plain gears) about 8 times.
- *So:* printed as typed, all of them would break or would not run. U-c is the right question, and nothing in the check
  should be softened to make these read better.

**One rule to rule on (R1): 0.7 under *once*.**
- 0.7 is a fatigue allowance: a tooth bent both ways endures less over many cycles. A single static load does not weaken
  a tooth because the next contact is on its other flank.
- So *Holds, once* and 0.7 do not fit together. Either:
  - keep 0.7, as the realistic tilt (planets and idlers fail first in service), and word it as *teeth that bend both ways
    are rated at 0.7, for running*; or
  - drop it from the *once* figure.
- I would keep it and word it, but this is the coordinator's ruling. It moves B1, B2, B3, B4, B6 and B7, and B5's 57.5 %.

**The wording.**
- **The form's row breaks §5.1's own rule.** §5.1 says every place the figure shows says *about* and gives the
  allowable. §5.4's row *Holds, once — 0.58 N·m · 39 N* does neither. Should-fix: for example *about 0.58 N·m · 39 N at
  17 MPa* (label *Holds once*), so a reader sees an estimate at a stated stress.
- **The warning.**
  - *Holds* reads as a breaking load; *is rated to take once* does not.
  - A blank allowable should be called provisional, with where to type one.
  - The user's own tested allowable is a remedy as real as a larger module.

  Proposed, for F4-0 to settle:

  > Meshes row 2: Sun and Planet: Printed, these teeth take about 230 N at the pitch circle in L, 13.6 times the 17 N
  > one tooth of Planet is rated to take once at 17 MPa (provisional: type your own in the Box's Allowable stress)
  > (…the two brackets as §5.4…); use a larger module, a wider face or less torque. An estimate for teeth printed flat,
  > with the whole load on one tooth's tip: not a running rating; heat, wear and creep are not worked out.

  Nothing frightening is added and nothing reassuring is lost: the multiple is the true one at the stated stress, and
  the reader is told the stress is theirs to set.

## 4. What must not move

- **Machined gears.** They are told exactly what they were, by construction: the check is behind F1's `_printed`
  (`checks.py:508-511`), the form's row behind a printed derived gear, the Results block behind a printed gearbox, and
  every figure is pure maths. F4-0's pins (step 1) must give `export.results_sheet` a fixed `when`, or its timestamp
  breaks the hash (should-fix, small).
- **No schema number moves.** `store.py` keeps no Box value, so no record sees the setting. `_read_box` skips a label it
  does not know (`model.py:405-407`), so an F3-era app reads a workbook with the row. `link.describe_changes` will list
  *Box Allowable stress 17 → 34* as a changed cell, which is right; B's `update.classify` test holds that Update has
  nothing to do.
- **The three pinned lines.**
  - `test_workbook_model.py:27-29` and `test_printed_rule.py:535` are the Box's titles and order.
  - `test_printed_workbook.py:123`, *labels[7] == "Units"*, reads the committed `RangeBox_W9.xlsx`, so it does not move.
  - I did not rerun the stub run. F4-0 reruns it, as §5.5 says.
- **B's edit at `test_printed_workbook.py:296-311`.** As planned it is not a loosening, but it can be stricter at no cost.
  Should-fix: assert that printed's diagnostics are machined's plus exactly B's strength sentences for that gearbox, in
  order, rather than setting aside whatever carries the mark.
- **W9's, F1's, F2's and F3's pins.** Nothing in §5 touches them, and the row is placed in `gui._rows_with_span` (which
  takes `ui_text.derived_rows` unchanged) so `test_ui_text.py:4520` holds.

## 5. Readiness

- **Files.** F4-0, with A whole, then B and C: the files are disjoint as listed (F4-0: `gears/strength.py`, `schema.py`,
  `model.py`, `test_strength.py`, `test_printed_rule.py`, `test_workbook_model.py`; B: `workbook/strength.py`, `checks.py`,
  `export.py`, `test_strength_workbook.py`, `test_printed_workbook.py`; C: `gui.py`, `ui_text.py`, README, design,
  `test_strength_form.py`).
- **Tests and Done-when.** The tests owed are right, with M2's two rows added. The Done-when needs no SolidWorks, which
  is right, since nothing F4 writes reaches a part.
- **Cost.** Six to eight runs is honest by every earlier stage.
- **What F4-0's interface must also state:** M1's rule; *not rated* for pointed teeth; the two *not worked out*
  wordings; and R1's ruling.
- **Decisions taken without the user, beyond §5.7's list.** None that blocks code. Two are worth putting in U-c's
  question:
  - every printed workbook read with a blank Process and no record (printed by D11) and an input torque will now carry
    these warnings, the user's own copies of RangeBox among them;
  - a planet's 0.7 is applied to a figure called *once* (R1).

## 6. Before F4-0 starts

**Must-fix**
- **M1.** State what F4 does with a ring whose tips lie inside its base circle (every ring under 34 teeth at 20°; built,
  with a warning): the load at the involute's start, or not rated with a sentence. Pin one such ring in A.
- **M2.** Correct Risky_Placements' 14.9 to 14.3 (G5–G6, 1428.0 %) in §5.3 and U-c. Pin A9 (helical ring) and B8
  (Risky_Placements' helical, herringbone and helical-ring meshes) with §2's figures, so a force taken at a helical ring's
  normal-module diameter fails a test.

**Should-fix**
- S1. D7, the README and the Box's note give 17 MPa's basis as about half a printed PLA data sheet's 35 MPa in-layer
  tensile strength (Bambu PLA Basic V3.0), not "a third of about 50".
- S2. The form's row says *about* and the allowable (§5.1's own rule); the warning says *rated to take once*, calls a
  blank allowable provisional and says where to type one.
- S3. Results: *turns unloaded here* and *not shared out past a shared output* in place of one *no torque here*.
- S4. A's note: the app's tooth against ISO's own generated tooth (+15 to +32 % in Y_F, +18 to +38 % with Y_S); the 30°
  section reading up to about 7 % under the beam's worst on small pinions; the normal-section fillet bound (Y_S within
  about 3 % at 20°).
- S5. §5.1's interlayer figure: about 0.17 σ_F of shear at β 20° from the bending stress itself, not 0.035; the conclusion
  (no derating) stands.
- S6. `rate` says *not rated* for pointed teeth.
- S7. F4-0's results pins pass a fixed `when`; B's edit to `test_printed_workbook.py` asserts the exact added sentences.

**For a ruling:** R1, 0.7 under a *once* figure: keep it and word it for running (my preference), or drop it.

**Ready for F4-0 once M1 and M2 are in the plan.** Neither needs the user, and nothing else in §5 is in doubt: every one of
the plan's other figures was reproduced from the app's own geometry and kinematics.
