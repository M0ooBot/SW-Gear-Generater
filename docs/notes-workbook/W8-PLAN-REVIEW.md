# W8 plan review (independent, before any code)

**Verdict: go with these changes.** The design holds together: sleeves and dogs as the strip's own ring and spur
plans, each slide position held by its own mate, one configuration per mode with every flag set explicitly and read
back, and only the configuration switch and the multi-configuration save probed ahead. That last choice is right under
the user's rule of 2026-11-14. The speeds are right in every mode of both fixtures. Six things must change before code:

- the 30° default makes a dog tooth that comes to a point;
- the torque rule and its answer key disagree;
- two phases in the answer key contradict the plan's own walk rule;
- the record's schema number collides with W6's and W7's;
- Update's puts in one mode leave the other modes out of step;
- the wrong-sense control repeats the control that failed in W5.

Three readings should go to the user beside J1 and J14: J2 (30°), J16 (it departs from PLAN-WORKBOOK §3.4) and a
cheaper J14.

**How the numbers were checked.** I solved both fixtures mode by mode in exact fractions with the app's own
`kinematics._reduce` (`scratchpad/w8r/kin.py`). I derived and validated the sleeve and the dog with the existing
`SpurGear` and `InternalSpurGear` (`scratchpad/w8r/parts*.py`). I read the canvas boards E4 and F4 from the canvas
itself.

---

## Must change before implementing

**M1. The 30° default (J2) makes a dog tooth that comes to a point, and the fit risk in §7 is aimed at the wrong
place.**

- *What the existing kinds make.* I ran `SpurGear` and `InternalSpurGear` at E4's values (30 teeth, module 1.5, 30°,
  backlash blank, which is the strip's 0.3 × module on each part):

  | Part | Tip thickness | Warnings |
  |---|---|---|
  | dog | **0.022 mm** | *"The tooth tip is 0.022 mm thick, under 0.3 × module"*, plus the form-diameter warning |
  | sleeve | 0.351 mm | *"The ring's tooth tips are 0.351 mm thick…"* |

  So each of E4's three dog rows and two sleeve rows carries a warning under Checks on every read. The dog's built
  tip is a land 0.022 mm wide, a sliver face for SolidWorks' interference check and for the part itself.
- *Why it happens.* A real 30° involute spline (ANSI B92.1, ISO 4156) has **stub** teeth: the addendum is 0.5 × module.
  The strip builds full-depth teeth (addendum 1 × module). At 30° and 30 teeth such a tooth is nearly pointed even with
  no backlash: typed backlash 0.05 mm still leaves the dog's tip at 0.449 mm, under the warning. This weakens §1.1's
  argument that "the teeth are the specified thing": what gets built is not what a spline is.
- *The fillets are not the risk.* Both parts carry the full backlash (0.45 mm each), so a sleeve over a dog has 0.9 mm
  of circumferential play at the pitch circle. That is about ±1.15° of turn, and 0.45 mm on each flank. The dog's
  0.57 mm root fillet rises only about 0.03 mm off the flank at the sleeve's tip radius (21 mm), so the fillets cannot
  touch. §7's "within a few tenths of a millimetre" is not where the fit is tight: the tip is.
- *At 20° (the Box's angle)* the dog's tip is 0.626 mm and the sleeve's 1.153 mm. The warnings left are the strip's
  usual ones (the form diameter, and the ring's tips inside its base circle).
- *Change:*
  - Make a blank Pressure angle on a sleeve or dog take the Box's, as every other row does. Name canvas E4's 30° as a
    departure. Alternatively keep 30° with a per-kind default backlash, and say so; that changes "every sleeve and dog
    plan equal to the spur or ring plan of the same values but its stem".
  - Pin both parts' tip thicknesses in §1.1.
  - Put J2 to the user together with J1, since stub teeth would be new solid geometry and J1 promises none.
  - Rewrite §7's fit risk around the tip and the 0.9 mm play. §1.6's outline test (B, pure) decides the fit before
    SolidWorks does.

**M2. The torque rule (J17, §1.4) does not give the answer key's torques (§2.3).**

- *(a) The fixed shaft.* §1.4 prunes "a branch that reaches no output **and no fixed shaft**". E4's planetary branch
  (Sun → planets → Ring) reaches the fixed Ring, so in 2H it is not pruned. In then drives two onward links (the sun
  and InDog's coupling), which is W3's split, so nothing past In is given. The key says *"E4: 2H Rear 10.000 (the
  planetary idles)"*. The key is right physically: a planetary whose carrier drives nothing carries no torque. The
  rule's fixed-shaft clause is wrong.
- *(b) Parallel 4H.* The key says *"4H the power splits at Rear, so nothing past In"*. By the plan's own pruning, the
  In → Lay → Lo branch reaches no output (LoDog is not engaged) and is pruned. That leaves one onward link from In, so
  Rear is given 10. W3's own convention gives the shaft before a split its torque and stops after it (`_torques`:
  `torque[shaft] = gear_torque`, then the onward count).
- *(c) An output that also drives onward.* W3's `_torques` passes the whole torque on from an output shaft with one
  onward link: it has no notion of the output taking its share. Written from W3, 4H gives FrontDrv 10 and Front
  9.604. The plan's "split at Rear" needs a rule W3 does not have: **an output shaft that also drives onward is a
  split.**
- *Change:*
  - Drop "and no fixed shaft". A branch is pruned when it reaches no output in that mode; a fixed shaft is a reaction,
    not a load.
  - State (c) in J17.
  - Pin, for Parallel: 2H Rear 10.000; 4H Rear 10.000 and nothing past Rear; N nothing past In; 4L Lay 19.600,
    Lo 38.416, Rear 38.416 and nothing past Rear.
  - Pin E4 the same way, with W7's planetary rule giving the Carrier's torque in 4L.

**M3. Two phases in the answer key contradict the walk rule (§1.6 against §2.3).**

- §1.6: *"a gear no walk reaches starts a new walk at phase 0, in Gears-sheet order"*. A lock puts no condition on
  phase, so no mesh walk reaches any dog.
- In both Gears tables InDog comes before RangeSlv, and FrontDog before ModeSlv. So the walks go:
  - InDog starts at 0, RangeSlv gets 6°, LoDog gets 0;
  - then **FrontDog** starts at 0 and **ModeSlv** gets 6°.
- The key says ModeSlv 0 and FrontDog 6°. A test pinning the key fails against code that follows the rule, or the
  implementer bends the rule to fit.
- *Change:* fix the key (FrontDog 0, ModeSlv 6°), or say walks start from sleeves. Either is sound: the 30-tooth
  condition `g_S ≡ g_D + π/z (mod 2π/z)` holds whichever gear starts.

**M4. The record's schema number collides with W6 and W7 (§1.11).**

- W6-PLAN §2.8 sets `LINK_SCHEMA_VERSION = 4`. W7-PLAN §2.11 makes it "one more than W6 leaves it", so 5.
- W8 hard-codes 4, reads "a v3 file as v4", and refuses "a v5 file". As written, W8 would read W6's v4 records as its
  own and refuse every record W7 makes.
- The parse's "a kind outside the seven" also ignores whatever W6 and W7 add (W6's `MateEntry.plane`, W7's
  `MateEntry.on`, `CarrierEntry`, the carrier lock).
- *Change:* schema "one past W7's" (6 if both bump), reading every earlier version; the allowed kinds are W7's set plus
  `slide`, `spline` and `couple`; the shapes build on W7's `MateEntry`. Fix it at the interface commit, which already
  starts on W7's close (§0.2).

**M5. Update puts trains of the active mode only, so the other modes are left out of step and the post-check fails
falsely (§1.10, J13, W5's M1).**

- *Scenario (E4 or Parallel), with nothing changed in the workbook:*
  - The user turns the input in 4L. Everything is one train there, so In, the low range, Rear and FrontDrv's train
    all turn.
  - The user switches to 2H and presses Update.
  - `train_check` in 2H finds RangeSlv–InDog out of step: RangeSlv turned with the carrier at ¼ of In's angle. So the
    2H train {In, low range, Rear} is put back to its built turn, whole.
  - FrontDrv's train is a train of its own in 2H and is in step with itself, so it is not put. It stays at the turn
    the 4L drag left it.
  - Something changed, so the post-check visits 4H and 4L. There ModeSlv (back at its built turn) and FrontDog (still
    turned) are out of step, and FrontDrv's gears are off their "wanted frame".
  - The Update reports a problem in modes it was meant to have put right. Pressing again in 4L puts everything, after
    a false failure sentence.
- s2 runs only the opposite case (turn in 2H, Update in 4L, where 4L joins everything), so the demonstration would not
  show this. §3.5's A list does not test it either.
- *Change:*
  - In a gearbox with modes, the set Update puts is the connected set over **every mode's** relations. For both
    fixtures that is the whole gearbox. Only in a mode-free part of a box does W5's per-train rule stay as it is.
  - The post-check in the other modes judges a train that was not put by `train_check` (in step), never by absolute
    built frames: by W5's answer 2 a train Update did not have to move keeps the user's turn.
  - Add a fake test: turn in 4L, Update in 2H, every mode clean afterwards.

**M6. The wrong-sense control repeats W5's broken control, and the driven proof does not read every gear (§5).**

- *"A temporary 1 : 1 gear mate with the other Flip in its place"*: W5 established that the Flip passed to `AddMate5`
  does not decide `Reverse`. Which Flip a mate needs depends on the version and the ring, and once on the remake after
  a move. W5's first full run on 2026 had two FAILs from exactly this assumption, and m3 and m7 had to be rerun with a
  control that drives both Flips. On a collinear mate, where nothing is known about Flip at all, "the other Flip" can
  make a second right-sense mate, and the control then fails for the wrong reason.
- *Change:* make the control the way the app reads a mate. Make it, read `gear_mate_sense`, and keep it only when it
  reads **wrong** (remake with the other Flip otherwise). Or drive both Flips as W5's m3 and m7 do.
- *Also:* "every member's turn against §2.3's 30° row" lists shafts. Read **every gear's** turn, sliders included. A
  wrong SPLINE (ModeSlv against RangeSlv) and a wrong `ModeSlv engages FrontDog` cancel at the Front in 4H and 4L, and
  only ModeSlv's own turn shows them.

---

## Should change

**S1. J16 departs from PLAN-WORKBOOK §3.4 without saying so, and W3's free-shaft error is not dealt with.**

- §3.4 asks for a warning on *"a gear on an `output` shaft that nothing drives in some mode"*. J16 and §1.5 warn only
  on an output that turns in **no** mode.
- That is the better reading, since §3.4's rule would warn on both of E4's outputs every time. But PLAN-WORKBOOK's
  Context says to raise such a departure rather than choose it. Name it in §0.4 beside J1 and J14.
- `checks._check_motion` raises an **error** for a meshed shaft no input settles (*"nothing settles FrontDrv's
  speed…"*). FrontDrv meshes FIdler and is free in 2H and N, so per mode that error fires unless it is replaced.
- Say:
  - per mode, a free shaft is not a problem;
  - a meshed shaft free in every mode stays W3's error;
  - what the top-level `Report.motion` is in a box with modes (the first mode's), since the Speeds panel and Export
    read it today.

**S2. §1.8 step 6 (interference per mode) has no rebuild after each show.** The ledger says `EditRebuild3` is needed
after `ShowConfiguration2` before measuring. Without one, the sliders may still stand at the previous mode's
positions, which gives false clashes or misses. Steps 3 and 4 and the Update post-check say "show, rebuild"; step 6
should too.

**S3. A component's fixed state is per configuration in SolidWorks.** The layout part and the fixed gears (E4's Ring)
are fixed with `FixComponent` while only `Default` exists. Whether a configuration made by `AddConfiguration2` keeps
them fixed is not in the macro database. If it does not, a floating layout part in 2H moves the whole gearbox. Read
`IsFixed` for the layout and every fixed gear in each configuration, as a read-along in the probe and in §1.8 step 4's
check per mode.

**S4. The probe ahead (§4.2) should make what the app makes.**

- Link each slide mate's D1 to an assembly global as §1.7 does. A global driving a dimension of a mate that is
  suppressed in the active configuration is new to the app. If it makes rebuild errors, it raises "What's Wrong"
  dialogs exactly where §1.8 and the post-check show configurations.
- Turn a mate back on in a listed, **inactive** configuration (`SetSuppression2(1, 3, names)`). §4.1 cites
  assemblies/07 for "0 / 1", but that entry shows only suppressing (action 0). Unsuppressing is D10's route per
  configuration, so it is worth a read-along even though nothing suggests it could hang.
- Read `GetSaveFlag` of **every** document (the parts and the layout part too) around each show.
- Say whether `CommandInProgress` is off around `ShowConfiguration2`, and probe it the way the app will call it.
- P starts beside I and cannot call package A's swcom members, which do not exist yet. Say that P makes the raw calls
  in the shapes §3.2 pins, and that A's members copy the probe's calls.
- Step 1 already makes a collinear coupling. Driving it (no hang risk) makes s0 the second sight of J8, not the
  first.

**S5. Sliding gears are designed but in no fixture.** No row of either fixture slides into or out of mesh. So
sliding meshes (§1.3), their gear mates turned on per mode, and §5's "half-pitch control … on each sliding mesh" have
nothing to run on, on SolidWorks or in the pure tests beyond made-up workbooks. Either add one sliding spur gear to
TransferCase_Parallel, or say in §0.1, the readings and the caveats that sliding meshes are shown against the fake
only.

**S6. Offer the user a cheaper J14.**

- A Modes pick changed between existing positions, where every mate the new modes need is already on record, changes
  nothing but suppression flags. That is the call D10 per configuration already makes.
- The user's W5 answers chose an Update wherever the route was proven (a follower's At, a tooth change by the remake).
- Put the alternative beside J14: a pick change whose mates all exist is an Update; rows added, removed or renamed,
  and any change needing a mate that does not exist, stay structural.

**S7. The copy of a built folder can raise a dialog the scripts have not met (J24).**

- `OpenDoc6` on a copy whose stored references point at a folder moved aside makes SolidWorks search for them. If it
  does not find one, it can ask. Closing every document first is right, since SolidWorks looks in memory first.
- Run the scheme once on the probe's scratch assembly before E depends on it.
- Check that the original folder actually renamed: Windows refuses to rename a folder while a handle in it is still
  open.
- `ISldWorks.ReplaceReferencedDocument` (closed documents only, GOTCHAS §16; unverified) is the other route. Pack and
  Go is a third.

**S8. A quiet Update no longer reads every gear mate's sense.** §1.10 reads senses only for gear mates on in the active
configuration. That narrows W5's ruling that the check phase reads every gear mate's sense, which closed package B's
must-fix: a couple wrong in another mode (flipped by a user, or saved by the other version) goes unseen until a
changed Update visits that mode. Say so in the sentences, so that no sentence claims every gear mate reads right in a
configuration not visited. Record it as a limitation, unless the probe shows that reading `Reverse` and `EntityParams`
of a suppressed gear mate marks nothing and answers.

**S9. A sleeve's or dog's `.gear.json` outside the workbook.** `kind_for` looks in `WORKBOOK_KINDS` for every caller,
the strip included, while `gui.KIND_VALUES` does not list them. Say what the strip does when it meets one (refuse with
a sentence). Also say what kind custom property a delegated plan writes (`property_ops(self.kind…)` gives "spur").

**S10. §0.1's claims about the code are against `0f5a121`.** W6 and W7 change motion (bodies, the carrier as an
anchor), the layout (coaxial axes), checks (the coaxial exemption) and the record. The interface commit should check
§0.1 again on W7's close and name what moved.

**S11. Clean up after the half-pitch control as M12 did.** Putting a dog with its lock on moves the dog alone, and the
lock then takes the new angle (P0, P0b). After the dog is put back, check every frame against the built frame to
1e-6, and assert no lock is left suppressed.

---

## Notes

- **Speeds recomputed, all as pinned.** E4 and Parallel, in rpm:

  | Mode | Rear | FrontDrv | Idler | Front |
  |---|---|---|---|---|
  | 2H | 1500 | free | free | free |
  | 4H | 1500 | 1500 | −2250 | 1500 |
  | N | free | free | free | free |
  | 4L | 375 | 375 | −562.5 | 375 |

  In every mode: E4 Carrier +375, planets −750 absolute (−1125 about the carrier), Ring 0; Parallel Lay −750,
  Lo +375. A sleeve over InDog and LoDog at once jams both fixtures. No mode locks the train solid, and no member the
  plan calls driven is free.
- **The rest of the answer key checks:** the 30° drive row, the SLIDE globals (46, 56, 66, 96, 106), W5's ALONG
  globals, the dog faces and the 3 mm clearances, the 14 mm gap against the 8 mm sleeve, the mate table, the build
  order, s2's 27.75° ≡ 3.75° (mod 12°), and s4's edits. The centres of both fixtures check.
- **Equal teeth at centre distance 0 is not a mesh, and the plan routes around it correctly** as long as a coupling
  never goes through `_check_mesh`:
  - `_check_mesh` would refuse it: a ring needs more teeth than its pinion.
  - `internal.tip_clash` would raise *"A ring of 30 teeth cannot hold a pinion of 30"*.
  - `internal_working_centre` would return 0 (no shift).
  - Sleeves and dogs on Meshes are errors, so none of these is ever called.
  - Two existing checks would still fire:
    - `_check_clearances`' ring branch, for a coaxial sleeve and dog with equal teeth, warns *"InDog sits where it
      would mesh inside RangeSlv: list them on Meshes"* (`near` = |0 − 0| < 0.1 m). §1.5's exemption must come before
      that branch.
    - `_check_shafts` warns on dogs (not sleeves) passing over coaxial axes. W7's exemption (W7-PLAN §2.3 item 5)
      covers it.
  - The coupling's teeth-match check must read `spec_values` (with J2's default), not `ga.pressure_angle or box`
    as `_check_mesh` does.
- **Parallel's 15-tooth pinions at 20° carry the strip's undercut warning** (InPin, LayPin). Either "both fixtures check
  clean" means no errors, or use 17 and 34 teeth at 51 mm.
- **Lightweight:** a configuration switch does not unload components. W5's check that every gear is resolved, made in
  the active configuration, suffices; reading it after each show in the probe costs nothing.
- **The citations check against the macro database:** assemblies/07 (2024 SP5: `AddConfiguration2`,
  `SetSuppression2(0, 3, names)`, `IsSuppressed2(3, names)`, the inverse default seen once by hand); GOTCHAS §23, §26,
  §73, §83 and §103; and the ledger (`ShowConfiguration2` and `DeleteConfiguration2` verified on 2026 SP1.1 on
  **parts**; `EditRebuild3` needed after a show). The one miscitation is "0 / 1" (S4).
- **The probe list is right under the rule.** `ShowConfiguration2` on a mated train and the multi-configuration save
  and reopen are the calls that could raise a dialog. Delete, per-configuration suppression, `AddConfiguration2` on
  2026 and the collinear gear mate are read along in the same scratch assembly. Only S4's additions and S7's copy are
  missing.
- **On J8, the collinear gear mate.**
  - *What it holds.* A gear mate relates only the two components' turns about the selected axes. Nothing in it is
    positional, so it coexists with each slider's AXIS mate and its one SLIDE per mode, which a lock cannot (tier 8:
    a locked gear also mated to its axis over-defines).
  - *The read-back.* Both "Gear Axis" entities point along +Z on Z+ shafts, so `parallel` is always True and a
    same-way couple reads right exactly when `Reverse` is True. Whether `Reverse` means the same for collinear axes as
    it did in the 52 offset cases is unproven.
  - *If the rule is wrong for collinear axes,* every couple and spline will be made wrong in the same way. s0's driven
    proof in 2H (Rear against In) catches it, once M6's control is real.
  - *The alternatives are worse.* An angle mate at half a pitch removes the 0° degeneracy, and −π/z ≡ π/z modulo the
    pitch, but its 180° solution still lands an odd-toothed sleeve tooth on tooth. A parallel mate needs a phase plane
    the parts do not have. A lock fights the slide.
  - *Judgement:* the gear mate is the right tool, and the plan's fallback order (§7) is sensible. Nothing in the macro
    database says SolidWorks refuses one, and nothing proves that it accepts one either.
- **J1 is the user's to decide.** Canvas E4 also names a hub (*"sleeve, hub and dog teeth match"*, and the half
  section labels each sleeve *"splined to Rear"*). M1 makes the teeth less of a specified thing than §1.1 argues.
- **J5 does not cover sliders with no Modes rows.** It does not say what happens when such a slider has no position
  at 0, since there is no cell to name; say it.
