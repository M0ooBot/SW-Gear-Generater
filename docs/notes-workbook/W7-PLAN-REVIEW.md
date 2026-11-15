# W7 plan review (independent)

Reviewed: `docs/notes-workbook/W7-PLAN.md` at `8ebddb0`, against `PLAN-WORKBOOK.md`, `HANDOFF-WORKBOOK.md`,
`W5-DECISIONS.md`, `W5-PLAN-REVIEW.md`, `W6-PLAN.md` (as committed in `35b5ccd`) and the code at `8ebddb0`
(`workbook/{geometry,kinematics,checks,fixes,motion,layout,model,build}.py`, `swbuild.py`, `swcom.py`, `store.py`,
`findings.py`).

**Verdict: go, with these changes.** The mechanics are right: every number in §4 recomputes. The design follows the
user's skeleton answer and W5's rules, and the package split works. The gear-mate set is right exactly when SolidWorks
measures a gear mate's turns against the line between the two moving axes (see "The gear mate on a moving axis"
below). The plan names that as its main risk, and its first build will settle it. Six things must change before
code:

1. Update's train check never judges the planet–ring mesh.
2. The ring/shift reading is out of date.
3. The checks would offer a fix that breaks a planetary.
4. J4 contradicts PLAN-WORKBOOK for a Z- carrier.
5. The demonstration never puts back a carrier that has turned.
6. If the risky interpretation is the true one, p1 never reaches the drive that is meant to tell.

---

## The mechanics, recomputed

Done by hand and with `geometry.external_space` / `ring_space` / `pinion_space` as committed.

- **Teeth and condition.** 54 = 18 + 2·18. Both centre distances are 18: m(18+18)/2 and m(54−18)/2. The assembly
  condition (18+54)/3 = 24 is whole.
- **Neighbours.** Copies stand 2·18·sin(π/N) apart and need more than 20 + 0.5 = 20.5 mm. That gives 31.18 at
  N = 3, 25.46 at N = 4, 21.16 at N = 5 and 18.00 at N = 6. The counts that both divide 72 and fit are 2, 3 and 4.
- **Phases.** `external_space(0, 18, 18, ψ)` = 2ψ + 170° (mod 20°), which is 10° at ψ = 0°, 120° and 240°. The ring
  from copy k, `ring_space(10°, 18, 54, ψ)`, is 2ψ/3 + 6.667°, which is 0 (mod 6.667°) at every ψ. For the sun held,
  the copies from the ring by `pinion_space` are −2ψ − 10° = 10°, and the sun from every copy comes out at 0.
  For p4's four copies (ψ = 90°, 180°, 270°): θ is 10° and the ring is 0 from each.
- **Speeds, ring held.** ω_c = 1000/(1 + 54/18) = 250. ω_p − 250 = −(1000 − 250)·18/18, so ω_p = −500, which is −750
  relative to C. Check: −750·18 = −13500 = (0 − 250)·54. For a 30° drive: carrier 7.5°, planet's own turn −15°,
  −22.5° relative to C. The copy origins are 18·(cos, sin) of 7.5°, 127.5° and 247.5°, the plan's values to 1e-6.
- **Sun held.** ω_c = 1000·54/72 = 750. ω_p = 750 + (1000 − 750)·54/18 = 1500, which is +750 relative to C. The ratio
  is 1.333 : 1. For a 30° drive: carrier 22.5°, planet 45°.
- **Torques.** η₀ = 0.9604.
  - Ring held: the sun drives in the carrier's frame (2·750 > 0). T_r·(−250) = −0.9604·2·750 gives T_r = 5.7624, so
    T_c = 7.7624 and the stage efficiency is 7.7624·250/2000 = 97.03 %.
  - Sun held: the ring drives (2·250 > 0). T_s = 0.9604·500/750 = 0.6403 and T_c = 2.6403, giving 99.01 %.
  - Planets carry 0 about their own axes.
- **Mates and counts.** The count of 14 mates and 7 components is right. p3's copies at (−11.25, ±19.485571585) are
  right.
- **Also verified.** The mesh row `z_p ω̃_p ± z_q ω̃_q − (z_p ± z_q) ω̃_c = 0` is PLAN §3.5's equation expanded
  correctly. The relative speed `ω_p − σ_pσ_c ω_c` is right. §2.9's carried-frame `train_check` is Willis in the
  carrier's frame: the planet's own-axis turn is δ_rel + σ_pσ_cδ_c.
- **Not wrong, just inexact.** In §2.3 item 2, the copies 2, 3 and 4 omit 1 from "divide 72".

## The gear mate on a moving axis (the question the plan rests on)

The fixed-frame angles about +Z are θ_s (sun), θ_c (carrier), θ_k (copy k's own turn) and θ_r = 0 (ring, fixed).
Physically, each mesh rolls about the line joining its two centres, and in the fixture that line turns with the
carrier.

- **Interpretation R: SolidWorks measures each gear's turn against the line of centres (relative to the carrier).**
  - Each sun–planet mate imposes (θ_s − θ_c)·18 = −(θ_k − θ_c)·18.
  - The single planet–ring mate imposes (θ_1 − θ_c)·18 = (0 − θ_c)·54.
  - So θ_1 − θ_c = −3θ_c and θ_s = 4θ_c. **The carrier turns at a quarter of the sun, the same way.** The planets
    turn −500 rpm absolute and −750 on C.
  - The four rows are independent (rank 4 over θ_s, θ_c, θ_1..θ_3). With N + 2 freedoms that leaves 1.
  - Copies 2 and 3 against the ring follow from the sun mates and the assembly condition.
  - The plan's set (N sun mates, one ring mate, N − 1 left unmated) is right. The carrier needs no mate of its own:
    its turn enters every mate through the moving line of centres.
- **Interpretation A: SolidWorks measures each turn about a fixed direction in the assembly.**
  - The ring mate gives 18·Δθ_1 = 54·Δθ_r = 0, so planet 1 cannot spin.
  - The mate Sun meshes Planet copy 1 then gives Δθ_s = 0, so **the sun is locked**. The sun mates lock copies 2
    and 3 as well.
  - No gear mate refers to the carrier, so **the carrier is left free**: one freedom, but the wrong one.
  - Dragging the sun does nothing, and the drive's angle mate over-defines.
  - The plan's §9 risk 1 ("the planet's ring mate … would hold the planet from spinning") is right, but it
    understates the effect. The sun jams, and the carrier free-wheels on its own.
- **What would be right under A.** N + 1 gear mates at the *solved absolute* ratios, with no mate to the held ring:
  - Sun → carrier at 1 : 4, same sense.
  - Sun → copy k at |ω_p/ω_s| = 1/2, opposite sense.
  - For the sun held, the equivalents are ring → carrier at 3 : 4 and ring → copy k at 3 : 2, both the same sense.

  This is §2.9's fallback. Note that **its senses come from the sign of the solved ratio, not from `internal`**
  (should-fix S9).
- **Carrier held.** Every axis is still, so the tooth-ratio mates are right under both interpretations. This makes a
  carrier-held build a control that cannot be confused with the question (S10).
- **How W5's sense read-back applies.** The rule `(Reverse == directions parallel) == internal` is a static read of
  the mate's own definition: whether it couples the two axes' turns in the same or the opposite sense.
  - With both axes along +Z, a sun–planet mate reads right with Reverse False (opposite sense), and a planet–ring
    mate reads right with Reverse True (same sense).
  - Under R those are the senses relative to the carrier, which are the right ones. So the read-back carries over
    unchanged, with copy handles added to the sense map's σ.
  - Whether Reverse means the same thing when one axis rides a carrier is shown only by a drive.
  - p1's control (the other Flip on Sun meshes Planet copy 1) gives θ_s = −2θ_c, a carrier at −15°, so it can fail.
    p5's control does the same for the ring mate. That is enough.
- **The carrier and the ring as held.**
  - The carrier: an axis coincident with layout `C Axis`, and its origin on the Front plane. That leaves one
    rotation, and it lives with W5's one anchor per shaft (the carrier is shaft C's anchor).
  - Each copy: coincident with `P copy k Axis`, plus a distance from the Front plane. That leaves its spin.
  - Fixing the held ring sits beside the layout part's own fix without conflict, as W5-PLAN D9 does.
  - What is new is a gear mate that touches a fixed component, and W5's Update does not handle that (M1).

---

## Must change before implementing

**M1. Update never judges the planet–ring mesh, and it re-places a gear-mated fixed member after the train's puts.**
- **Where:** `swbuild._update_motion` (lines 2959–2963 and 3097–3130 at `8ebddb0`).
  - `mated` is every placement that is not fixed. `train_check` runs only over `mated`. Each train's meshes are
    `[m … if m.a in train and m.b in train]`.
  - The held Ring is fixed. So `Planet copy 1 meshes Ring` is a recorded gear mate that is never judged, in the check
    phase or in the post-check.
  - Fixed gears are re-placed (`REPLACE_FIXED_ROUTE` = "Transform2 put") *after* every train has been put.
- **Scenario 1: a false "in step".** The sun mates alone are satisfied by any carrier turn: (δ_s − δ_c)·18 =
  −(δ_k − δ_c)·18 holds for every δ_c.
  - Suppose the person suppresses the ring mate, or a put leaves the carrier off its Willis turn, and then turns the
    train. Every copy's teeth are then in the ring's teeth.
  - `train_check` says "in step, turned". Update puts nothing and says *"The gears stand where they were turned"*.
  - With R in a carrier mesh (§2.9's δ − σσδ_c rule), the relation is not judged at all, because Ring is not in
    `delta`.
- **Scenario 2: a tooth edit that keeps the assembly condition.** The phase walk gives Ring a new θ.
  1. Update puts the train first.
  2. Then it puts the fixed Ring to its new θ while it is gear-mated to Planet copy 1. Under R, that turns the train
     away from the frames it was just put to.
  3. The post-check compares only the put trains' meshes, which exclude the ring.
- **Change:**
  - Give train_check and `_trains` every still gear that a recorded gear mate touches, measured with δ (expected 0,
    or a whole pitch, against its wanted frame).
  - Re-place a gear-mated fixed member **before** the carrier and train puts.
  - Judge the post-check with it included.
  - Add fake tests for both scenarios.
  - Pin it in `W7-INTERFACES.md`: `MotionUpdate` must carry the held members of a carrier mesh.

**M2. §2.3 item 1 and J9 rest on code and a question that have moved on.**
- **Out of date.** The plan read the code at `0f5a121`. Since then:
  - `d3f4dcf`: *Catch a shifted pinion inside a ring that does not sit at its working centre distance*.
  - `9efde87`: *Never let a pinion's shift silence the ring checks*.
  - `1a850dd`: the SolidWorks sections for a shifted pinion inside a ring at its working centre.
  - HANDOFF question 2 is **answered Yes** (2026-11-14).
- **What the code does now.** `checks._check_mesh` computes `internal_working_centre` for a shifted pinion in a ring.
  So the plan's claims are now false: "a shifted pinion in a ring passes the checks silently" and "a ring mesh
  between frame shafts keeps today's behaviour until the user answers question 2".
- **Why the blanket error is wrong.** "A planet with profile shift meshing a ring is an error" is justified by the
  clash the probe saw at the *unshifted* centre distance. That is exactly the case the checks now catch.
- **Change:**
  - Rebase §2.3 item 1 and J9 on the current checks. A carried planet's ring mesh uses the same working-centre rule.
    The planet's single carrier distance must then satisfy both working centres: sun–planet with both shifts, and
    planet–ring with the planet's shift.
  - The simple-stage `z_ring` sentence applies only when nothing is shifted.
  - Drop the unconditional error, or justify it from a ring section of `1a850dd` that fails at the working distance.
  - Restate the base commit `W7-INTERFACES.md` reads from.

**M3. The checks would offer a "fix" that breaks the planetary.**
- **The plan's claim is false.** It says "PLAN §3.6 already withholds Move inside a loop". `fixes.move_fix` withholds
  it only when the **shaft graph** has a cycle (`_is_tree`). A planetary's shafts form a tree: S – P – R, with the
  loop closing through the carrier and the copies.
- **Scenario: Ring typed with 56 teeth.**
  1. Planet–Ring is 18 apart where the teeth make 19, an error.
  2. `move_fix` grows the tree from S, moves the far shaft R, and offers "R X 0 → −1".
  3. Applied, that takes the ring off the sun's and carrier's axis, which is "a mesh that fits no carrier".
- **Also wrong:** `shift_fix` would offer shifting the planet, and `unshift_fix` the ring. Both contradict §2.3.
- **Change:**
  - In `checks`, withhold every fix (`report.fixes[where]`) on a mesh whose `planetary.mesh_carrier` is a carrier,
    and say that no fix is offered.
  - Test it with Ring 56 (no fix) and a Sun–Planet centre error (no fix).

**M4. J4's default contradicts the authority for a Z- carrier.**
- **What PLAN-WORKBOOK says.** §1, Mounted on: "X Y Z are then measured on that shaft at its starting turn". §3.3:
  "`mounted on` composes frames". That is J4's reading (b): offsets in the carrier's own frame, F₋ = rot_x(180°) on
  Z-, so y and z are negated.
- **What the plan does.** J4 (a) uses the origin's axes, and `z = z_c + z_p + σ_p·At` in §2.2 follows (a). For Z+ the
  two readings agree. For a Z- carrier a typed Y lands on the other side, and a typed Z points the other way.
- **Why this matters.** The plan's own carrier part writes `(dx, −dy)` locally. So the app would read the cell one way
  and build the other way round from what the authority says.
- **Change:** either follow (b), which is composition as written, or refuse Z- carriers in this version with a §1.2
  sentence. Do not ship a default that overrules PLAN-WORKBOOK without the user's ruling; at most list (a) as an
  alternative for them.

**M5. The demonstration never puts back a carrier that has turned, and §9 risk 2 relies on it.**
- **Why each section misses it:**
  - p2's quiet Update puts nothing (the right answer).
  - p3 copies p1, which M12's hygiene leaves at the built frames, carrier at δ_c = 0. Its two edits do trigger puts:
    `moved` covers the Face Z edit and the copies carried by the carrier globals. But the carrier-first put is then a
    put to where the carrier already stands.
  - p4 and p5 are fresh builds.
- **What goes unshown.** The case the plan calls unprobed: a carrier at δ_c ≠ 0, put back while its copies are mated
  to its axes, the copies then put, with the gear mates on. No section shows it.
- **Change:**
  - In p3, drive the train (for example 37°) and delete the drive before each of its two edits. Assert that the
    log's put order is carrier first, and that every frame (carrier included) is at the built frame to 1e-6 after.
  - Add one edit that re-places the gear-mated fixed Ring after a turn (Ring At 10 → 12), which is M1's order.
  - Add the same steps to the fake tests A owns.

**M6. If interpretation A holds, p1 stops before the drive meant to tell, and nothing after p1 can run.**
- **Why p1 stops.** Under A the sun is locked, so the build's mate check can refuse:
  - `_free_to_turn` may read Sun fully defined.
  - The ring mate or the sun mates may read over-defined.
  - W5 answer 1 then stops the build: no assembly is saved, and the refused `Assem<n>` is left open.
- **What follows.** p1 never drives. p2–p5 all copy p1's folder, so none can run either. §8 step 4's "the follow-up
  probe compares the two routes" has no design, and §2.9's fallback has a sense rule that would be wrong (S9).
- **Change:**
  - **On a refused mate check, p1 keeps measuring.** It logs every component's constrained status and every AddMate5
    status (most of this is already read). Then, in the refused, unsaved assembly the script itself opened, it adds
    the temporary drive and reads which interpretation holds: the sun turns, or it does not and the carrier turns
    free. These are SolidWorks' own readings at no extra build. It then closes the document as the CAM-box protocol
    does.
  - **Write the follow-up probe's design into the plan now.** It builds the fixture through the app's plan with the
    mates swapped for the fallback set (S9), drives it, and measures the sun, carrier, copies and ring. It is the
    one follow-up round the rules allow, so it should not be designed after the failure.
  - **Add the carrier-held control (S10)** to that probe.

---

## Should fix (B, A, C or E can take these without a ruling)

**S1. Pin what `Placed.shaft` holds for a copy** (`"P"` or `"P copy 2"`). Several of the plan's statements depend on
it:
- §2.3 item 3 says "`_check_clearances` would also catch it pairwise", which is false if the copies share `"P"`.
  `a.shaft == b.shaft` skips the pair.
- The existing `motion_plan` would make one anchor of copy 1 and lock copies 2 and 3 to it.
- `_check_shafts` groups all copies under one axis.
- `preview` (D) reads it too.

I suggest the copy's own shaft id, with `row` and `carrier` beside it. Also say that `listed` in `_check_clearances`
is the **expanded** meshes; otherwise every Sun–Planet copy k and Planet copy k–Ring gets "sits where it would mesh:
list them on Meshes".

**S2. The `z_ring` sentence's condition contradicts its own example.**
- §2.3 item 1 says the sentence replaces the two centre errors "when both fail together". With Ring 56 only
  Planet–Ring fails: Sun–Planet is still 18 = 18.
- So the §4.2 test "Ring 56 (the z_r sentence)" fails against the rule as written.
- **Change:** say it when the stage is simple, unshifted, and `z_r ≠ z_s + 2z_p`, in place of whichever centre
  errors that causes.

**S3. The neighbour sentence's number is wrong.**
- Five copies fit: 21.16 mm apart, more than 20.5. So "6 copies … 4 is the most that fit" is false as a statement
  about clearance.
- **Change:** say *"5 is the most that fit round C; of those, 2, 3 and 4 also mesh with Sun and Ring"*, or compute the
  limit from both conditions and word it that way.

**S4. "C carries no gear."** `_check_shafts` warns of this for every shaft no gear names, which includes the
fixture's carrier. Exempt a carrier (§2.3 item 5 exempts only the axis-pass warning).

**S5. One shared Face Z global, made once.**
- `motion_assembly_plan` appends an `AddGlobal` per ALONG with a face global. With J7, `"Planet Face Z"` would be added
  three times.
- **Change:** de-duplicate it (and its `face_globals` in `MotionUpdate`), and make `plan.check()` refuse a duplicate
  global.

**S6. With J8, the carrier must be a node.**
- J5 says "the carrier never a node", yet J8 lets a gear on C mesh a frame gear, and that mesh then has no node to
  join. The fixture is unaffected.
- There is a deeper problem. Under R a sun or ring mate constrains three bodies, so a spanning tree over pairs can
  still over-count. Example: a ring-held stage whose carrier gear G7 meshes G8 on T, and T also meshes the sun's
  shaft. If the loop's ratios are consistent, the union-find makes N + 3 mates where N + 2 are independent: refused
  as over-defined.
- **Change:** choose the gear mates by **rank**. Add a mesh's mate iff its row (with the carrier column, interpretation
  R) is independent of those already chosen, using `kinematics._reduce` in `Fraction`s. It gives the plan's result on
  every §4 case.
- Also pin `trains`/`drag` with a carrier gear (otherwise {C, T} becomes a second "train").

**S7. Say what `CarrierLink.planets` includes.** It should hold every gear on the carrier's planet shafts: a compound
planet's locked follower and J8's carrier gear as well as the anchors. Their wanted frames must be carried too, or the
lock test sees a follower "off axis".

**S8. Unequal sun and planet teeth somewhere on SolidWorks.**
- A 4 : 1 forces z_s = z_p (z_r = 3z_s = z_s + 2z_p). The fixture therefore cannot catch a sun–planet ratio given the
  wrong way round (18 : 18), or a k inverted in `mesh_links` (−1 either way).
- **Change:** p3's value edit could be teeth instead of, or as well as, module: Sun 18 → 21, Ring 54 → 57, P X
  18 → 19.5.
  - Centres 19.5 / 19.5; assembly (21+57)/3 = 26; neighbours 33.8 mm.
  - All four gear mates are remade under `IDLER_UPDATE_HOLDS`, and the drive must read 3.714 : 1.

**S9. The fallback (§2.9) as written would read its own mates as wrong.**
- **Sense.** Under A, the senses wanted come from the sign of the solved ratio: sun → copy is opposite (−1/2) and
  sun → carrier is the same (+1/4). The `internal` argument of `gear_mate_sense` must become "same sense wanted".
- **No ring mate.** The held member gets no mate.
- **Selection.** The carrier needs a gear mate on `carrier1:C Axis`, a reference axis: `_component_ref` already
  selects it.
- **Write this into §2.9,** so the follow-up probe (M6) tests what the app would build.

**S10. Add a carrier-held control.** A Role edit makes C fixed, R the output. With every axis still, the tooth mates
are right under either interpretation. Run it as a demonstration section, or in the follow-up probe; it tells "gear
mate on a moving axis" apart from everything else new (a mate to a skeleton, a part inserted four times, three
coaxial layout axes).

**S11. Interference at the driven position.** §4.2 judges the loop-closing meshes at the drive by arithmetic on frames.
Run `interferences()` with Drive at 120 as well. It is SolidWorks' own reading that the unmated copies 2 and 3 still
clear the ring, and it fails if SolidWorks turns them otherwise.

**S12. The fake should not mirror the rule it tests.**
- §2.9 makes the fake call a gear mate over-defined exactly when it closes a cycle in the same bodies-with-ground
  graph that J5's union-find uses. A test written against it can never find a wrong count rule.
- **Change:** have the fake judge over-definition by the rank of the R rows, including the carrier column (S6).

**S13. Copy protocol, in detail.**
- **Rewrite every path the record holds, not only "the paths":**
  - `workbook`, `parts`, `gearbox.{layout,assembly,parts}`;
  - every `PartEntry`, `CarrierEntry.path`, `earlier`, `moved_from`;
  - `pending`/`pending_for`, and the keys of `unsaved`/`mismatched`;
  - each `.gear.json`'s workbook.
- **Assert that no string** in the copied record or sidecars still names the master folder.
- **Before opening a copy, assert that `documents()` holds no document with any of the copy's file names.** That
  covers the previous section's copy as well as the master, because SolidWorks resolves by the name of a document in
  memory first. The component-path assertion catches a mis-bind after the fact; this prevents it.
- **E0 has to build its 12 : 1:** committed runs keep logs, not SolidWorks files.

**S14. §2.10's table needs three more rows.**
- A tooth or Copies edit that breaks the assembly condition, or leaves the neighbours too close, is a Checks error:
  Build and Update are not offered.
- A carrier Z edit that brings a planet's front face to the Front plane is structural (W5 answer 3; the table says
  only "move").
- A planet's X/Y edit is valid only with a teeth or module edit that keeps both centres. Say so, so the summary
  sentence is not written for an edit that cannot pass.

**S15. Restate in `W7-INTERFACES.md` what W6 will have changed.** `W6-PLAN.md` (D7, D13, §2.8):
- rewrites `kinematics.solve` in own-axis unknowns with a per-mesh sense;
- adds `Placed.axis`/`centre` and a base frame per gear;
- sets the schema to 4, so W7's is **5**, not "4 if W6 does not change it";
- adds `MateEntry.plane` for the along mate;
- judges the sense read-back against the gears' own +Z as placed.

W7's interface commit should:
- write the carrier row in W6's form: z_p(ω_p − s_p ω_c) + c·z_q(ω_q − s_q ω_c) = 0, with s = ±1 each shaft against
  the carrier;
- give each copy its carried `axis`/`centre`;
- name the along plane for copies.

**S16. J11 and J12 are the user's to decide.** Differentials and compound or double planets would ship built on rules
no SolidWorks build has run. The testing rule of 2026-11-14 ("written against the fake and then built end to end")
implies refusing them at Build, with a sentence, until a fixture is built. Make refusal the default and offer
"build them" to the user.

---

## Notes

- **§1.3's claims about the code, checked.** These hold: `_component_ref` resolves `carrier1:P copy 2 Axis` by
  `FeatureByName`; `later_rows`, `layout`, `solve`, `check` and `shaft_layouts` refuse or raise on a mounted shaft;
  `motion_plan` is union-find over shafts with fixed meshes skipped; `_mated_handles` includes a carrier whose last
  op is `Unfix`; `layout.side` makes `cos 90°·18 ≈ 1e-15` the base plane, so p4's copies at 90° and 270° get no
  spurious plane. Two claims are false: the "shifted pinion passes silently" (M2) and "Move is withheld in a loop"
  (M3).
- **`still_shafts`.** It joins by meshes and tests the solved speed. It must never name a mounted shaft, whose axis
  orbits even at 0 rpm about its own axis. No held-member case gives a planet 0 rpm, but a differential can; say it.
- **The ring's θ.** It may come out as ≈6.6666° instead of 0, through `_wrap`'s floor at a whole multiple. That is
  harmless modulo the pitch, but a test pinning the frame "Ring I" should compare modulo the pitch.
- **Helical and herringbone planetaries.** They go through the same walk and kinematics, and no test pins one. Add
  one spec test: the twist term per copy, and the ring's same-hand rule.
- **A gear on C meshing its own planets.** The carrier rule ("a frame shaft coaxial with C", which includes C
  itself) accepts it. Its relative speed is 0, so it locks the planets to the carrier. Make it an error with a
  sentence, or pin what happens.
- **The demonstration controls are sound.** The interference controls per copy cover the unmated meshes. The
  wrong-sense control can fail (carrier −15° for +30°). Measuring the copies' own turn as well as the carrier's
  separates every mixed interpretation I tried; with equal teeth the carrier alone does not. The person's step is
  well worded.
- **Readings that need no change.** J1, J2, J3, J6, J7, J10, J13–J15, J17–J20 are sound defaults. J5 (c) is rightly
  offered to the user.
