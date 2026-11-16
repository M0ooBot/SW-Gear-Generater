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
