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
