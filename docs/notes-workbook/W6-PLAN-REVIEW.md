# W6 plan review (independent)

**Verdict: go, with these changes.** The design is sound. The facing rule, the base frame, the own-axis kinematics,
the phase condition and the read-back rule H are well founded. Every fixture number I recomputed is right, with one
exception: the slant's "seen from" (M6). Six things must change before code:

- the test of H covers only the angles it runs (M1);
- it cannot see an error in the mesh sense itself (M2);
- D6 bends a binding rule and has to be asked before E, not after (M3);
- a crossed mesh's sense can change on an Update, against the plan's claim, and the record has nowhere to keep it
  (M4);
- D8's bound warns falsely on both fixtures, and fixture B has real line-through-gear warnings (M5);
- the slant's "seen from" string contradicts §2.1 (M6).

D16 is consistent with the user's answer 1 in its letter. It departs from W5's own precedent, though, so it is a
should-fix (S2).

Numbers below are from `scratchpad/w6r.py` and `w6clear2.py`. They run `bevel.derive`, `bevel.blank_points`,
`crossed.placement` and `crossed.tooth_direction` on the fixtures' gears, plus hand derivations.

---

## Checked and found right

- **Fixture A.**
  - Cones and centres:
    - δ 26.565051° / 63.434949° and R 67.082039, both cones.
    - Both apexes at (0, 0, 60). The heel pitch point is (60, 0, 90) from either gear.
    - G3–G4 centres 68.
  - Anchors: G1 on Right (coincident), `"G2 Apex Z"` 60, G4 on Front.
  - Speeds and torques: ω2 −750, ω3 +250, 6 : 1. Torques 19.60 / 57.624.
  - Drive: G2 −15, G3 −15, G4 +5.
  - r3 (20 → 21): δ 27.699473°, R 67.766142; drive −15.75 / +5.25.
  - r4 (X−): the contact moves to (−60, 0, 90) and c stays +1. The rolling condition gives 30·ω1 = −60·ω2 again.
- **Fixture B.**
  - Crossed pair:
    - C 84.852814. The common perpendicular is +Y. The contact is (0, 28.284271, 8), inside both faces.
    - In world, t ∝ (−1, 0, 1): a·t is +1 on Z+ and on X−, so c = +1. The normal-velocity condition gives
      ω2 = −ω1/2 independently.
  - Bevel pair:
    - Σ 60°, δ 23.413224° / 36.586776°, R 62.915287.
    - The apex (−40, 84.852814, 8) is S3's point.
  - Anchors: `"G1 Face Z"` 2, `"G2 Face X"` 8, `"G4 Apex Y"` 84.852814.
  - Speeds and torques: −500 / +333.33, 3 : 1. Torques 9.80 / 14.406.
  - Drive: −15 / −15 / +10. r6: +9.677419 (δ 22.901696°, R 64.242380).
- **Senses.**
  - c = +1 holds for every bevel form. With w_p and w_q each in the axes' plane, pointing towards the other axis,
    a_p × w_p = −(a_q × w_q). So z_p·ω_p + z_q·ω_q = 0 whenever δ_p + δ_q = Σ, a crown or internal δ_q included.
  - The crossed c = s_p·s_q holds by the same normal-velocity argument as §2.4.
  - PARALLEL `c = ±a_a·a_b` reproduces W3's rows multiplied by the shafts' signs.
- **Phase.**
  - π + π/z ≡ `pair.mate_angle(z)` modulo a pitch, for both parities.
  - ψ_q = π with g_p = ψ_p gives `crossed.placement`'s spin modulo a pitch.
- **`base_frame`.** It gives I for Z+, diag(1, −1, −1) for Z−, and the X±/Y± columns as written.
- **H equals W5's rule on parallel axes,** outside and inside a ring, same and opposite senses. It is an identity
  once each entity lies along its gear's axis. It is also better supported than §2.6 says:
  - In W5's data, an external pair on opposite shafts was right with the stored Reverse True. findings: Reverse is
    "Flip, reversed once for opposed axes", and external +− needed Flip False.
  - A Reverse measured against SolidWorks' own "closest" alignment, the sign of d_a·d_b, would have made that pair
    turn wrong.
  - So on parallel axes Reverse is relative to the entities' own directions, which is H's reading.
  - What the parallel cases cannot show is a different behaviour that SolidWorks has only for non-parallel axes. M1
    is about that.
- **Is there a frame-independent "right way"?** Yes. Each gear's own +Z is an oriented line. The sign of
  k = ω_b/ω_a about those two lines follows from the contact alone: rolling for a bevel, normal velocity for a
  crossed pair. No world frame enters. The drive measures exactly that, from SolidWorks' frames, about each gear's
  third column.
- **Plumbing.**
  - `Place.rotation` is by rows, so the axis is (r[2], r[5], r[8]). This is "third column", as §2.6 says.
  - `place_component` reads all nine numbers back, so a turned put that does not hold is a failure.

---

## Must change before implementing

**M1. The first build tests H only at 90° and 60°, but the finding is committed for every angle.**
- *What the runs cover:*
  - Every turned mesh in r1, r3 and r5 has the two own axes at 90° (G1–G2 of A, the crossed pair of B) or at 60°
    (B's bevel).
  - The τ product is +1 in every case. Each Gear Axis is made Top-then-Right and reads +Z
    (`LAYOUT_AXIS_Z_SIGN`'s note). W5's 52 cases had the entities parallel exactly when the shafts were.
  - So sign(d_a·d_b) = sign(g_a·g_b) ≥ 0 in all six control cases. Σ > 90° is never run.
- *Why Σ > 90° matters:*
  - That is where a crown gear lives (cos Σ = −z_mate/z) and where an internal bevel lives (δ > 90° needs Σ > 90°).
    §9 admits that nothing on SolidWorks covers either.
  - That is also where any behaviour keyed to the sign of the angle between the axes disagrees with H.
  - At 90° such a behaviour is a rounding coin flip that can come out H's way in one session.
- *Scenario:*
  - SolidWorks treats non-parallel gear axes differently past 90°.
  - r1 and r5 pass six of six, and the finding is committed.
  - A workbook with a crown pair at Σ 110° builds. The read-back calls the wrong mate right and keeps it.
  - The train turns the wrong way, silently.
- *Change:*
  - Put one turned mesh with Σ > 90° into the first build, with its both-Flips control. The cheapest place is
    fixture B's bevel stage at 120°, re-laid (M5). With S2 X−, the slant (1, 1.732, 0) gives 120°. For 20 : 30 at
    m 2.5 that is δ 40.893° / 79.107° and R 38.188, still two cones.
    - Take care with the layout: at 120°, G4 is almost flat. A layout that puts S2's shaft through the apex runs
      that shaft through G4.
    - For example, turn S2 to X+ (the crossed pair only cares about lines; its c becomes −1, the same physical turn)
      with G3's apex beyond G3's body (At ≈ −110) and the slant then (−1, 1.732, 0). That keeps S2's shaft clear.
  - Otherwise, gate the finding to what was shown: the gate refuses a turned mesh outside 60–90° with a sentence.
  - Either way, write the angles tested into the finding's comment and its `test_findings.py` pin.

**M2. The drive and the read-back share one source, k, so neither can catch an error in k.**
- *How the three are tied:*
  - The read-back's verdict is `Reverse == (sign(k)·τa·τb > 0)`.
  - The expected turn is `δ_in·ω_i/ω_in`.
  - The speeds come from the same `MeshGeometry.sense`.
- *Scenario:*
  - A sign slip in `mesh_geometry` flips c for a crossed pair. Say t is carried to world through the base frame and
    not the placed frame, or s is taken against the family's plus direction.
  - The app keeps the mate H calls right for the wrong k. The drive turns the gear the way the wrong k predicts, and
    the both-Flips control "agrees" in all six cases.
  - The finding is committed. The teeth pass through each other in SolidWorks.
- *What would catch it:* the half-pitch control tests phase, not sense. The fixture values I recomputed are right,
  so the risk is in the code, not in this plan's numbers.
- *Change:* in r1, r3, r5 and r6, after each drive of every both-Flips control on a turned mesh, run the
  interference check. Drive off the built phase, as `ring_mate_sense` did:
  - the Flip the drive calls right must be clear;
  - the other must clash.

  This is SolidWorks' own reading and independent of k (`WRONG_GEAR_MATE_SENSE_CLASHES` held on parallel axes). Make
  it a condition of committing the finding.

**M3. D6 departs from a binding rule, and the plan sends it to the user only afterwards.**
- *The rule:* HANDOFF's *Rules carried over*: "Findings are still read from committed `findings.py` only."
- *What D6 does:* it runs the app on SolidWorks with an uncommitted finding set in memory. §3 lists D6 among "readings
  to overrule", after the fact. A binding rule is not the agent's to bend first and report later.
- *Is it sound?* As a probe, yes. The app's code is run under a stated hypothesis, and the result decides the finding,
  which is what every probe does.
- *Change: ask the user before E runs,* with the two honest options:
  - (a) D6 as written;
  - (b) §7.2's cylinder probe first, cut to the cases that matter (90° meeting, 90° skew, 60°, 120°; both Flips), and
    then the full build on the committed finding.

  (a) bends "committed findings only". (b) bends "full build first". Only the user can pick which.
- *If (a) is chosen:*
  - The flag is an in-process assignment in the probe script only. It is never an app option, an environment
    variable or a config.
  - The run line and the log header name it.
  - The criteria for committing are written down before the run: M1's coverage, M2's interference, reads after
    reopen.
  - `r1.master` and `r5.master` are used by copy sections only after the finding is committed with the same value.
    Each copy section's Update check phase then reads every turned mate on committed code.
  - §6.1's "nothing else of W6 waits on it" is not quite true: r2–r4 and r6 wait on the finding.

**M4. A crossed mesh's sense can change on an Update. §2.7's claim is false, and schema 4 has no place for the
sense.**
- *The claim:* §2.7: "an axis change is structural, so the senses cannot differ from the record's on an Update."
- *Why it fails:*
  - For a crossed pair, c = s_p·s_q depends on which side of p the contact is (e).
  - At 90° with equal hands, which is the commonest crossed pair and fixture B's, the signed crossing check passes on
    both sides, because −90 ≡ +90 modulo 180.
- *Scenario:*
  - Take fixture B's crossed stage on its own (no bevel stage pinning S2's point), shifted so S1 sits at Y = 200 and
    S2 at Y = 284.852814.
  - The user moves S2 to Y = 115.147186: the other side of S1, same side of Top. The checks pass, and it classifies as
    a move.
  - Worked out at the new contact (0, −28.28, 8): t ∝ (1, 0, 1), s_q = −1, so c = −1. ω2 = +500 about −X, where the
    built mate turns it −500.
  - `recorded_meshes` (update.py: the record's ratio with the *new* read's sigma) then carries the new sense:
    - `train_check` misjudges the user's turn;
    - the check phase reads the built mate "wrong" and remakes it under the `sense_found_wrong` sentence, which tells
      the user something went wrong in SolidWorks.
- *Change:*
  - Record each mesh's sense: `MateEntry.sense: int` (c, or same_sense), defaulted from the read for a v3 entry.
  - Build `recorded_meshes` from it.
  - Classify a change of c as structural, with its own sentence: *"S2 now meets S1 on the other side, so G6 turns the
    other way; …needs building again."* Or carry it as a remake with a true sentence. Pick one in I.
  - The same `MateEntry.sense` also gives W7 a place for its carrier-frame sense.

**M5. D8's bound is a capsule, not the cylinder it names, and it warns on both fixtures.**
- *What it computes:* "segment-to-segment distance less both radii" sweeps a sphere, so it reaches a radius past each
  end. A 61 mm bevel blank then reaches 61 mm along its axis.
- *Fixture A (the headline):*
  - S1's line passes G4's capsule (−3.0 mm). The true cylinder is 50 mm clear.
  - S1's line passes G2's capsule (−40.9). The true cylinder is 20 mm clear: G2's blank spans z 80.0–100.1, and S1 is
    at z 60.
- *Fixture B:*
  - G2–G4 is −33.8 by the capsule and about 19 mm clear by the cylinders.
  - Two warnings are real by any check on infinite lines:
    - S3's line passes 7.8 mm from S1's axis at z = 8, inside G1's face (2–18).
    - S3's line clips G2's −X face 55.4 mm from S2's axis, under G2's tip radius of 58.6.
  - More generally, any crown or near-crown bevel has its partner's infinite line through its blank.
- *Change:*
  - Compute a true distance between solid cylinders (closed form for each end disc and the side, or a short convex
    search).
  - For non-parallel shafts, take a shaft as the span of its own gears, not an infinite line, and exempt a bevel
    gear's partner shaft.
  - Re-lay fixture B now, not "if B's checks find" a warning. G3's At about 85–90, with S3's point with it, clears
    both lines at 60°. Redo this if M1 makes it 120°.
  - Pin the exact Checks panel each fixture shows, warnings included (the 20-tooth pinions' strip warnings, 45° outside
    8–30°), in W6-INTERFACES. Without that pin, B's fixture test and the boards have no target.

**M6. The slant's "seen from" in §2.9 and rw contradicts §2.1's family rule.**
- *The rule:* a slant's plus direction is "the direction whose first non-zero component is positive".
- *Fixture B:* for S3 = (−0.5, 0.866, 0) the plus direction is (0.5, −0.866, 0), not "(−0.5, 0.866, 0)". S3's
  +333.33 about its Axis is clockwise seen from (0.5, −0.866, 0).
- *The effect:* rw asserts the wrong string, so the screenshot check fails, or someone "fixes" the family rule to
  match it.
- *Change:* correct rw and the §2.9 example. Or change the rule to "seen from the Axis as typed", but the plan's D12
  argument is for the family + end.

---

## Should fix

**S1. Which entity is which gear.**
- `sense_reading` pairs `directions[i]` with `axes[i]`. That assumes `MateEntity(0)` is the first selection. W5 never
  needed the order: a dot product is symmetric.
- If the order differs, every turned mate is refused as "not along its gear's axis", which stops every right-angle
  build. That is not silent, but it is avoidable.
- *Change:* match each entity to the gear whose axis it lies along (|d·g| ≥ 0.99). On parallel axes either pairing
  gives the same τ product, so nothing W5 built changes.

**S2. D16: consistent with answer 1 in its letter, inconsistent with W5's precedent, and dead at the close.**
- *Why the letter holds:*
  - Answer 1 governs a mate SolidWorks refuses. A finding missing at planning is W5's *static by necessity*, which
    W5-INTERFACES §4 kept.
  - PLAN-WORKBOOK §0 backs it: "A static assembly is fine until the gear_mate probe has passed."
- *What W5 did instead:* when it could not tell a ring's sense, it **refused** Build at `_sense_gate`. It did not
  build static.
- *Why it is dead at the close:* W6's done item 2 requires the finding, so D16's per-gearbox `motion_reason(report)`
  branch ships as code no closed W6 takes.
- *Recommendation:* follow the ring precedent. A turned mesh without the finding is refused before anything is made,
  with the gate's sentence, said in the footer before Build. Drop the per-gearbox static reason.
  - If the user prefers static, keep D16. The footer then has to say that the next Build again turns it
    (ui_text already words "it was built static, and the new revision's gears turn").
  - Put the choice to the user with D6.

**S3. D1 is a user question.**
- One facing per shaft means two bevel gears on one shaft always face the same way.
- A cross shaft with a bevel at each end, both apexes outward (or back to back), cannot be written.
- (b), inferring the facing from the partner, is ambiguous, as the plan says. But a per-gear choice (for example the
  sign of a bevel's At relative to its shaft's other gears, or a word in `Side`) is a third option.
- The default stands, with that consequence stated for the user.

**S4. Kinematics: pin what W7 and every caller need.**
- `solve(senses=None)` is called from `checks.check` today, and its result feeds Export's Results sheet and Update.
  Say whether None means "parallel and bevel senses from the axes, crossed left out" or "every caller passes them".
- Keep `Fraction` with c ∈ {−1, +1}. W7 assumes "the linear system in Fractions, one unknown per shaft".
- Write down the carrier-ready form now. W7 §2.4 is written in the projected ω̃, which W6 removes. In own-axis form
  each ω_x becomes ω_x − (a_x·a_c)·ω_c.
- `mesh_links(meshes, teeth, sense)`: pin `sense`'s key, the ordered pair or the mate name. W7's planets also call
  it.

**S5. The Results sheet for turned meshes is unspecified.** "Centres needed / placed / off by" has no meaning for a
bevel row (0 against the apex distance). The contact ratio and `geometry.extent` need a 3D extent for turned gears.
Name the rows: for a bevel, shaft angle, cone distance and apex distance; for a crossed pair, shaft angle and the
common-perpendicular distance.

**S6. "A word ↔ a vector" (§2.7) should not be structural when both are the same direction.** `axis_vector` turns
`1, 0, 0` into X+. If the record keeps the canonical word, the edit is no change at all. Say so.

**S7. Slanted axes.**
- D4 holds the line fixed in the part, but nothing checks it afterwards. A person dragging the 3D-sketch line in
  SolidWorks moves the axis, and the record never knows.
- *Change:*
  - Read the line axis back (`GetRefAxisParams`) when a layout is reused and in Update's check phase, against the
    record's point and direction.
  - Give the nearest-plane rule a tie order, for example (1, 1, 0) → Right first.
- My judgement on D4: keep (a). The line is rigid, not fragile. It is part of the specified train, so it does not
  meet the user's objection to a datum plane. PLAN-WORKBOOK §4.2 puts arbitrary axes in W6. Refusing slants up front
  (b) gives up a feature that a full build can test cheaply. The plan's fallback to (b), sent to the user, is the
  right one.

**S8. One copy helper for W6 and W7.**
- W7-PLAN §7 describes a different protocol: the master is renamed aside and then back, and the copy's assembly is
  not saved.
- W6 builds first: pin `copy_built(master, section)` and its steps in W6-INTERFACES, and tell W7 to reuse it.
- Say what step 3's save of the copy's assembly is for. It is not needed for correctness, because the master stays
  renamed. It also changes the assembly's mtime before the section's first Update.

**S9. A file outside every package breaks at I.** I changes `Session.gear_mate_sense(handle, internal)` to
`(handle, same_sense, axes)`. `probe/workbook_assembly_check.py:2231` calls `s.gear_mate_sense("ring", True)`, and it
is E's file. Name it in I's "done" (left for E), or let I fix the call.

**S10. Sentences that need a rule.**
- The apex sentence names one gear's At. Say which one (Gear B of the Meshes row?).
- "Seen along the line from G5 to G6, turned −60°" needs its sign pinned as a right-hand turn about e.
- Crossed shafts whose lines meet (distance 0, e undefined) need their own sentence.
- On a turned shaft, a herringbone's `Hand` "names its half nearest the Front plane". Say it means the half nearest
  its own front face.

---

## Notes

- **D4/D5 with W5's mates and Update.**
  - The axis mate (coincident, closest alignment) works for any direction.
  - A point-distance mate to Top or Front was made by `nonparallel_mates` through `crossed_assembly_plan`. Right is
    the same call, untried.
  - Puts are general `Transform2` frames, read back in full.
  - No datum plane is added: the slant's 3D sketch carries a shaft's own line, not extra geometry.
  - The cost of D5 is more structural cases: fixture A's G1 sits on Right, so any At change on it is a Build again.
    This is the same trade the user accepted for Front, and the sentence names the plane.
- Fixture A's G1 blank starts at x 40.92 (its front bore and toe rim), not 42.1, which is the toe's pitch point.
  Nothing depends on it.
- 98 % per mesh is W3's convention. A crossed pair's real efficiency is far lower. A Notes line on the Results sheet
  would do.
- The 2024 confirming set (r1, r3, r5, m3, window) follows the rule of 2026-11-14 and covers every place a turned mate
  is made or remade.
- §7.1's one probe ahead, the copy open under the dialog watcher, is the right one. The others the plan leaves to the
  build (3D sketch, `InsertAxis2` on a 3D line, AddMate5 gear across an angle) carry no recorded hang or dialog.
- W7 needs from W6: schema 4 as the base for its 5 (D13 keeps it always 4, good); `MatePlan.plane` defaulted
  `"front"` (its `"Planet Face Z"` fits D5b); S4's kinematics form; S8's copy helper; M4's `MateEntry.sense`.

## D1–D16

| | View | Ask the user? |
|---|---|---|
| D1 facing along Axis | Sound and simple; it forbids two bevels facing apart on one shaft (S3). | **yes** |
| D2 At to the apex | Agree; PLAN-WORKBOOK §1 says it; teeth and face changes move nothing. | no |
| D3 two offset planes | Agree. | no |
| D4 slant as fixed line | Agree, with S7; fallback (b) to the user if r5 fails. | only on failure |
| D5 base plane, no datum | Agree; consistent with answer 3. | no |
| D5b `Face X/Y/Z`, `Apex Z` | Agree. | no |
| D6 build as test of H | Sound as a probe, but it bends a binding rule (M3), and the test needs M1 and M2. | **yes, before E** |
| D7 own-axis kinematics | Agree; pin S4. | no |
| D8 cylinders, warning | Agree in kind; the bound and the lines are wrong (M5). | no |
| D9 mate and Σ from rows | Agree (PLAN-WORKBOOK §1). | no |
| D10 no fixes | Agree. | no |
| D11 crossed scope | Agree. | no |
| D12 family + end | Agree; fix M6. | no |
| D13 schema 4 always | Agree; add M4's field. | no |
| D14 form change structural | Agree; record the strip's gap as a caveat. | no |
| D15 no new control | Agree. | no |
| D16 static before the finding | Allowed by PLAN-WORKBOOK §0; against W5's ring precedent (S2). | **yes, with D6** |

**Missing from the plan:**

- each mesh's sense on record (M4);
- the expected Checks panel per fixture (M5);
- the Results rows for turned meshes (S5);
- a read-back of the slant's line (S7);
- the entity matching (S1).
