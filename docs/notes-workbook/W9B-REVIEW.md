# Review of W9b: the sleeve checks, the bands and the hub

*Independent, 2026-11-17. I started no SolidWorks or Excel and changed no source, test or document. I ran the whole
suite once (1 failed, 3561 passed, 1 skipped: the known Tk font-width test only), and a handful of throwaway scripts in
the scratchpad, outside the repo, against the repo's own `checks.check`, `update.classify` and fake. This file is the
only one I wrote.* Under review: `42dff4d..e8d8af9` (seven commits on `194664f`). Line numbers are `e8d8af9`'s.

I read ISSUE-1-PLAN §0 (K7–K10, §0.3), §2.2–§2.4, §3, §5 "W9b" and the four *Changes after …* sections (none of them
amends W9b); `W9B-INTERFACES.md`; HANDOFF-WORKBOOK's *Rules carried over*; the whole diff; and the code around it
(`modes.py` whole, `checks._check_clearances` and `_in_line`, `geometry.Placed`, `motion._sliding_shaft`,
`clutch.py`, `helical.py`'s planes and groove hub, `bevel.py`'s loft, `swcom.ref_plane` / `loft_cut` /
`feature_states`, `internal.section`, `spec.py`, `store.py`'s sidecar and link schema, `update._gear_cells`,
`gearbox`'s part naming, `swbuild.structural_change`).

**Verdict.**

- **The answer key held.** I worked §3 by hand from the fixtures' rows before reading the checks' arithmetic, and
  every number and every pinned sentence agrees with the plan and with what the code says (§ *The answer key*). The
  tests pin them word for word and can fail.
- **The checks follow K7, K8 and K9 as written.** A Z− shaft, unequal bands, a dog exactly at a band's edge, two
  sleeves on one shaft with a hub each, the open intervals and exactly-c all come out right. Two cases are wrong:
  - A band over a hub on another shaft is never an error, and the one sentence that names it gives wrong advice (1).
  - One hub carrying two sleeves keys only the first (3).
- **The part's plan is sound for SolidWorks.** Every op the relief adds has run in a built part, in the same form,
  and the plane sides are independent of the shaft's direction. I agree with no finding gate (§ *The relief*).
- **Records, columns and Update are as the plan says.** An unbanded part's sidecar and record entry are unchanged.
  Nothing reads or writes a Gears cell by a fixed letter. Bands given or taken, and a hub added, stay *Build again…*
  with a sentence each, and nothing is half-written.
- **Nothing here blocks the first build of `RangeBox_Fixed` on SolidWorks.** Point 1 is the one must-fix, and it
  touches no row of that fixture. It should land before W9b closes, not before the demonstration.

---

## Must fix

**1. A sleeve's band over a hub on another coaxial shaft is never an error. It is a coupling the app does not see,
and the one sentence said about it gives wrong advice.**

- *What the code does.*
  - `modes.engagement` looks at dogs only (`modes.py:230`), so a band over another shaft's hub is neither engaged
    nor a partial-cover error.
  - `clearance_warnings` then skips any dog or hub a band overlaps, on the assumption that engagement has said so
    (`modes.py:763-764`, comment *"over it: engaged, or engagement's own error"*). For a hub nothing has said so.
  - `checks._check_clearances` exempts only the {sleeve, dog} pair (`checks.py:553-558`). A {sleeve, hub} pair
    falls through to the ring logic, which says *"… sits where it would mesh inside …: list them on Meshes, or move
    one."* Listing a hub on Meshes is itself an error (`modes.py:309-313`).
- *Reproduced against `checks.check`.* Take three Z+ frame shafts on one line: In (input), Out and Aux. Every row is
  17 teeth, module 1.25.
  - In: InDog at 5, face 5.
  - Out: OutSlv at 20, face 30, Slides `A=-7.5, B=+3, C=+10`; OutHub at 21, face 5.
  - Aux: AuxHub at 41, face 4; AuxSlv at 41, face 4, Slides `Z=0, Y=+0.5`.
  - In mode C, OutSlv (15…45) covers AuxHub (39…43) whole, with the same teeth. Physically that joins Out to Aux.
  - The report has no error. C reads as neutral. The only words about it are *"Gears row 5: AuxHub sits where it would
    mesh inside OutSlv: list them on Meshes, or move one."*, plus *"B and C engage the same: they are one mode
    twice."*
  - A band that covers part of AuxHub gets the same treatment.
- *Why it matters.* K8 says a hub engages nothing. It has to stay true for every sleeve on the line, not only for
  the hub's own sleeve.
- *Fix.*
  - In `engagement`, treat a hub on another coaxial shaft that a band touches (by more than `COVER_TOLERANCE`) as an
    error at the mode's cell: *"in C OutSlv covers AuxHub, the hub on Aux: a sleeve engages dogs only; move the
    position off it."*
  - Add the hub to the exempt pair in `_check_clearances` (`{SLEEVE, HUB}`), so the Meshes advice is never given.
  - Pin both in a test.
- No fixture has such a row, so §3's key does not move.

## Should fix

**2. The reach sentence names one gear twice when a single gear spans the point on both sides.**

- `reach_warnings` builds *first* and *second* from a dict keyed by gear id, then appends `high` again when `low` is
  `high` (`modes.py:662-663`). The result reads *"from Hub at −45.5 to Hub at −45.5 … pass Hub toward Z− or Hub
  toward Z+"*.
- I got it by adding a second sleeve on Input with a hub at −48…−44, so that Output's 20 mm Hub is present across both
  of that sleeve's points. That layout also has a clash error, so the case is rare. But a single long gear on P under a
  sleeve gives the same sentence.
- *Fix.* When one gear blocks both ends, say *"… runs through ISlv's travel at Hub (−55.5 to −35.5), so Input would
  have to pass Hub, on Output"*.

**3. A hub belongs to one sleeve, so a hub that carries two sleeves leaves the second warned as unkeyed.**

- `hub_sleeve` returns the first sleeve on the shaft whose whole travel overlaps the hub (`modes.py:183-202`).
  `_hubs_of` and `hub_warnings` then count the hub for that sleeve only (`:613-615`, `:695`).
- *Reproduced.* On Out, take S1 at 20 and S2 at 40, each face 20 with bands 4 and 4. S1 slides `A=0, B=-7.5` and S2
  `A=0, B=+7.5`. One hub H sits at 30, face 23 (18.5…41.5).
  - H covers S1's end band and S2's start band in both modes. Engagement is right: B engages D1 and D2.
  - Yet *"Gears row 5: nothing keys S2 to Out: no hub row is under it; …"* is said, and S2's reach is judged by its
    bands instead of H.
- The plan does not forbid a shared hub, and a wide hub under two collars is a real layout.
- *Fix.* Two choices; I prefer the first.
  - A sleeve is keyed when any hub on its shaft is under one of its bands in every mode. `hub_errors` then judges each
    hub against the sleeves it is under.
  - Or a hub serves one sleeve, and a second sleeve over it is an error that says so. That is a ruling for the user.

**4. K11 names a user's edit to a band global without its cell.**

- `update._GLOBAL_COLUMN` (`update.py:582-584`) maps a part's globals to Gears columns. It has no `Start Band` or
  `End Band`. So a user who types a new Start Band in SolidWorks is told the two values and no cell, while K11 asks for
  *"the cell to change"*.
- *Fix.* Add `clutch.START_BAND: "start_band"` and `clutch.END_BAND: "end_band"`, with a test beside W9a's K11
  tests. `Relief Diameter` is a formula global and rightly has no cell.

**5. A banded sleeve shares its default file name with an unbanded sleeve of the same module and teeth.**

- `spec.default_stem` gives a shifted gear `_x…` and a grooved herringbone `_G…`, *"since it is a different part"*
  (`spec.py:285-317`). It gives bands nothing.
- *Reproduced.* In `TransferCase_Parallel`, give RangeSlv a 20 mm face with bands 4 and 4, and leave ModeSlv
  (also 30 teeth, module 1.5) plain. The read then says *"Gears row 10: ModeSlv and RangeSlv would both be
  Sleeve_m1.5_N30.SLDPRT, but they are not the same gear; give one of them a Part name."*
- That is safe: the build refuses, and a reused file is matched by its sidecar's spec, so a plain file is never taken
  for a banded one. But it is the first edit a user makes to W8's fixtures to fix them (§6 item 5).
- A band mark in the stem would clash with W9c's in-place bands, which keep the file's name (K6, §2.4). So this is a
  ruling more than a fix. Either:
  - add a mark without values (`Sleeve_m1.5_N30_Banded`), stable under a band value Update; or
  - keep today's sentence and add *"they differ in their bands"*, which is cheap.

**6. A hub on the shaft of a sleeve with no Slides is never checked.**

- `hub_errors` walks `reports` (`modes.py:498`). A sleeve without Slides and no Modes rows gives none.
- *Reproduced.* A hub 60 mm away from such a sleeve, on the sleeve's shaft, reads with no error.
- This mirrors W8, which judges no engagement there either. But K8's *"in every mode"* has one mode here: where the
  sleeve stands.
- *Fix.* Judge the hub against the sleeve's one place when there are no reports.

## Notes

- **N1 — a test gap: reach through the hub.** `test_reach_with_a_hub_runs_to_the_hubs_start…` asserts no warning on
  `RangeBox_Fixed`. The same box without the hub is also clean (the next test's first case). So nothing would fail if
  `reach_warnings` ignored the hub and tried the bands. A case where the hub's start is blocked and the start band's
  place is not, or the reverse, would pin K7's *"with a hub row, the hub's start"*.
- **N2 — the schema 6 and 7 test reads a W9b record.** `test_a_schema_6_or_7_record_reads_as_before` relabels a
  record built with bands. A real W9a-era record is read in `test_workbook_user_record.py`, so the claim holds. The
  bands test proves only that the label is accepted.
- **N3 — the nested-input test.** §5 asks for *"a nested input through a hollow carrier not warned"*. The test
  checks RangeBox's own nesting: Input through Carrier, with the sleeve on Output beyond both. The case where the
  rule's *"P runs inside whatever keys S"* could be false is not built: S on an inner shaft, riding inside a hollow
  P's bore. No workbook row can engage a dog from there, so I do not ask for it; the reading is noted.
- **N4 — a thin wall over the relief.** A typed Rim just over m(z + 3) passes. `test_a_typed_rim_just_clear…` uses
  25.5, which leaves a 0.25 mm wall over the relief. The ring's own thin-rim warning measures from the root, not the
  relief. A warning when the rim stands less than two modules outside the relief would match the ring's rule. Not
  required by the plan.
- **N5 — two band checks that disagree at the last digit.** `modes.bands` treats `b1 + b2 >= face` as no relief.
  `SleeveKind._band_errors` uses `>= face - 1e-9`. They disagree only inside 1e-9 mm, on a row that is already in
  error and left out.
- **N6 — the E4 sentence names the planet row.** It says *"from Pl at 20"*, where §3 paraphrases *"the planets at
  20"*. §3 gives that sentence only in summary, and naming the row is right. I count it as agreement.

## The rulings the implementer added beyond the plan

| Rule | Sound? | Tell the user? |
|---|---|---|
| One band typed and the other blank is an error | Yes. A single band (teeth at one end, relief open to the face) is a different part the plan never drew. | Yes, one line: a one-band sleeve is not built. |
| A hub's teeth, module and pressure angle must be its sleeve's | Yes. It carries the sleeve on those teeth (K8: "a dog's toothed ring"). | No: it follows from K8. |
| A hub on Meshes, with Slides, or on a shaft with no sleeve is an error | Yes. K8 says "on the sleeve's own shaft", "a non-sliding gear", "engages nothing". | No. |
| A hub held to c from a dog on another shaft, once, at the hub's cell, with the larger module | Yes. §2.3 asks for it ("a hub and a dog on different shafts are held to the same gap"). Neither moves, so once is right. | No: it is the plan's. |
| A hub on a carrier's, a turned or a fixed shaft is an error | Yes, as for a sleeve or a dog. | No. |
| `hub_sleeve`: one hub to one sleeve, the first whose travel overlaps it | Not quite: see point 3. | Yes, if the second choice of point 3 is taken. |

---

## The answer key, by hand

I worked these from `tests/workbook_fixtures.py`'s rows before reading `reach_warnings`, `hub_warnings` or
`clearance_warnings`.

- *Convention.* At is a face's middle, so a face spans At ± face/2. Slides add to At.
- *Clearance.* c = max(0.5, 0.5 m): 0.625 at module 1.25, 0.75 at module 1.5.

**RangeBox.**

- *Faces.* Sun, Planet and Ring 5.5…15.5. HighDog −34.5…−29.5. LowDog −19.5…−14.5.
- *RangeSlv's places.* H −34.5…−24.5, N −29.5…−19.5, L −24.5…−14.5, so p− = p+ = −24.5.
- *Reach.* Input is present over −34.5…15.5 and holds −24.5 with room on both sides. HighDog reaches below and Sun
  above, so both ends are blocked. Carrier (−19.5…15.5) and Ring do not hold −24.5. One warning, *from Sun at 10.5 to
  HighDog at −32* in sheet order.
- *Hub.* The places share no length (a point, −24.5), and the whole travel −34.5…−14.5 holds both dogs. So none can,
  *"its 10 mm face slides 10 mm (H −5 to L +5) and its places share no length."*
- *Clearance.*
  - In N the face touches both dogs at 0 mm: one warning at Modes row 3, 0.625 mm.
  - In H the face engages HighDog and is 5 mm from LowDog. In L it engages LowDog and is 5 mm from HighDog.
- *Total.* Three new warnings. The code's three are §3's sentences word for word, with U+2212 where the plan has it.
  Engagement H HighDog, N none, L LowDog, unchanged. **Agrees.**

**RangeBox_Fixed.** RangeSlv's face is −48…−22 at N, and Hub is −55.5…−35.5.

| Mode | Face | Start band | End band | Relief | Engaged | Least gap |
|---|---|---|---|---|---|---|
| H (−7.5) | −55.5…−29.5 | −55.5…−50.5 | −34.5…−29.5 = HighDog | −50.5…−34.5 | HighDog | end band to LowDog 10 |
| N (0) | −48…−22 | −48…−43 | −27…−22 | −43…−27 ⊃ HighDog | none | end band 2.5 to HighDog and 2.5 to LowDog |
| L (+7.5) | −40.5…−14.5 | −40.5…−35.5 | −19.5…−14.5 = LowDog | −35.5…−19.5 ⊃ HighDog | LowDog | start band to HighDog 1.0 |

- *Hub.* It covers the start band in H, N and L (in L to the edge, −35.5). It stands 1.0 from HighDog, over 0.625.
- *Reach.* p− = −55.5 and p+ = −35.5. Neither Input (−34.5…15.5) nor Carrier holds either point, so it is reached.
- *Stroke.* The end band's travel −34.5…−14.5 holds both dogs, 10 mm apart, which is more than 5. No stroke warning.
- §3's table (*"N … 2.5 each side"*), its *"Hub to HighDog: 1.0"* and *"p− = −55.5"* all hold.
- The code gives no warning from W9b's checks. The four pre-W9 warnings stay, and the mates are as §3 (`Hub` anchor,
  `RangeSlv splined to Hub`, slide values −55.5 / −48 / −40.5, couplings in H and L). **Agrees.**

**TransferCase_Parallel.**

- *RangeSlv's places* (8 mm, ±10): 46…54, 56…64, 66…74, so p− = 66 and p+ = 54.
- *Reach.* Lo is present over 25…73 (LoGear 25…35, LoDog 67…73). It holds both points, with LoGear below and LoDog
  above: blocked. In (5…53) holds neither point. One warning: *from LoGear at 30 to LoDog at 70*.
- *ModeSlv's places* (0 / +10): 96…104 and 106…114, so p− = 106 and p+ = 104. FrontDrv starts at 107 and holds
  neither point: reached.
- *Hubs.* RangeSlv's places share nothing and its travel holds InDog and LoDog. ModeSlv's share nothing and its
  travel holds FrontDog. So two *nothing keys* warnings, each with *as laid out none can*: *8 mm face slides 20 mm
  (H −10 to L +10)* and *8 mm face slides 10 mm (2WD 0 to 4WD +10)*.
- *Clearance.* RangeSlv in N is 3 from InDog and from LoDog; ModeSlv in 2WD is 3 from FrontDog. All are over 0.75: no
  warning. **Agrees.**

**E4.**

- Carrier is present over 15…73: the planets 15…25 count as its gears, and LoDog 67…73. It holds 66 and 54, so the
  reach is blocked toward Z− only because the planets count. The warning reads *from Pl at 20 to LoDog at 70*.
- In (15…53) and Ring (15…25) hold neither point.
- The hubs and the clearance come out as in TransferCase_Parallel. **Agrees** (N6 on the wording).

**Do the tests pin it, and can they fail?**

- RangeBox's three sentences are pinned exactly (`test_workbook_sleeve_checks.py:40-57`). So are the W8 fixtures'
  three each (`test_workbook_modes.py:194-213`, as the whole diagnostic list, so a fourth would fail).
- RangeBox_Fixed's spans, engagement, ratios and mates are pinned in `test_workbook_bands.py:186-248`, and its 2.5,
  1.0 and 10 gaps in `test_workbook_sleeve_checks.py:85-100`.
- Exactly c is pinned at N = −1.875. The arithmetic is exact in binary, so the test would catch `<=` in place of
  `<`. Just below c is pinned at −1.885.
- The open interval is pinned at 1e-6 ± half.
- Each of these fails if the rule changes. The one assertion that cannot fail is reach through the hub (N1).

## What I checked and found sound

- **Engagement per band.**
  - A band covering a dog whole engages it. A partial cover is an error naming the band.
  - A dog wholly under the relief touches no band and is free. A dog straddling a band edge is the partial error.
  - A dog exactly at an edge (share 0) is not engaged and has gap 0, so it gets the warning.
  - An unbanded sleeve is one band with word `""`, so W8's sentences are unchanged. Every old engagement and stroke
    sentence still pins.
- **A Z− shaft.** `band_spans` puts the start band at `z_front` (= z1 for σ = −1), where `Placed.origin` puts the
  part's origin. I checked this on a Z− box with bands 4 and 6: a hub under the start band is clean, and a dog half
  under the end band errs.
- **The hub's own rules.**
  - A band covers the hub whole, or the hub covers the band, in each mode. A hub engages nothing (only dogs are
    engaged).
  - A hub is its shaft's anchor. `_sliding_shaft`'s sort is stable and keyed only on *is a hub*, so a shaft with no hub
    keeps W8's anchor exactly: no workbook without a hub changes.
- **Clearance.** It is per mode and per sleeve, skips engaged pairs and the sleeve's own shaft, and is clean at
  exactly c. It is at the Modes cell, or the sleeve's Gears cell with no Modes rows. The floor's wording (*the least
  at any module*) is pinned.
- **The relief, as SolidWorks will take it.**
  - *The planes.* `RefPlane(plane 1, offset, _flip_for(EXTRUDE_Z_SIGN · offset))` and `LinkDimension("Offset@…")` are
    exactly the helical profile plane's and the herringbone mid-plane's form (`helical.py:539-545`). Both offsets are
    positive and the ring grows toward +Z, so neither plane is flipped.
  - *The sketches.* Each sketch is opened on its made plane by id, as the helical space sketch is. That sketch also
    relates its centres to `ORIGIN` (`spur.py:1184`, `:1209`). The circle, its centre-to-origin relation, its
    `Dimension` named per sketch and its link to a global are the groove hub's ops (`helical.py:568-580`).
  - *The loft.* `LoftCut` through two closed sketches is the bevel's `InsertCutBlend` route (`swcom.loft_cut`). A
    loft has no direction to get wrong.
  - *The diameter.* m(z + 3) clears the ring's root at either depth: `internal.section` gives df = m(z − 2) + 2h,
    which is m(z + 2.5) or m(z + 2.8). It clears the dog's tip m(z + 2) by 0.5 m a side. A typed Rim at or under it is
    an error.
  - *The globals.* `Relief Diameter` follows `No. of Teeth` and `Module`, and the end plane follows `Face Width` −
    `End Band`. So teeth, module, face and band changes are all value Updates.
  - *No gate.* No call is new and none can raise a dialog the build has not met, so I agree with no finding gate.
    M7 should also read that `Relief Start Sketch` and `Relief End Sketch` sit under `Relief`, not at the top of the
    tree, as the bevel's sketches do. If they sit at the top, the sidecar still lists them (the list comes from the
    same walk), so W9a's user-feature read is safe either way.
- **Records.**
  - `GearSpec.to_dict` pops both band keys while blank, after `asdict`, so key order and bytes are unchanged for a
    plain part.
  - `sidecar_schema` writes 1 for such a part, and `updated_sidecar` now recomputes it instead of copying it. That is
    the same for every existing (schema 1) sidecar.
  - Link schema 8 adds no field. Schema 1–7 records read as before. A reader at 7 refuses 8 and leaves it
    byte-identical. A reader at 1 refuses a schema 2 sidecar.
- **Columns.**
  - The two columns sit after Slides, so Part name and Notes move from T/U to V/W in a new workbook. Bore stays J, so
    W9a's *Gears!J2* sentences are untouched.
  - Every cell in a sentence comes from `spec.cell` by the read header.
  - Export adds a missing header at `max_col + 1` of the sheet as read, so an old workbook without the band columns
    is unaffected.
  - The only `Gears!T…`/`U…` letters in `src/` are in docstrings, as examples.
- **Update.**
  - A band value on a built banded sleeve is a value Update (pinned, through `update.classify`).
  - Bands given or taken is *Build again…* with its sentence (`swbuild.py:1315-1322`).
  - I ran RangeBox's record against RangeBox_Fixed's rows. `classify` gave `needs_new_revision` with *"Hub is new,
    and Update SolidWorks cannot add a part to what was built."* and the bands sentence, and no Update plan. So no half
    change can be written.
- **The moved pins.** Each one moves for a reason the plan gives:
  - the three warnings on the W8 fixtures, and RangeBox's 4 → 7 (also in the S0 master check);
  - V/W for Part name and Notes;
  - schema 7 → 8 and the refused 8 → 9;
  - `hub` among the workbook kinds;
  - the bands as workbook-only spec fields.
  The jam test's third sentence is rewritten for its own fixture's `J=-30` place, which is the code saying the right
  thing about a different row, not a bent pin.

---

## Closing review: the fix round and the demonstration on SolidWorks 2026

*Independent, 2026-11-17, at `de0a470`. I started no SolidWorks. I ran the suite once (1 failed, the known Tk
font-width test; 3571 passed, 1 skipped), the script's `--self-check` (0 failed), and throwaway scripts in the
scratchpad against `checks.check` and the app's own section maths. I changed no code.*

Under review:

| what | where |
|---|---|
| the fix round | `172e47c` (checks), `ce712b4` (Update and parts), `7ce72dd` (the interface note's §7 rulings) |
| the demonstration | `probe/w9b_demonstration.py` and `W9B-DEMONSTRATION.md` (`5da5dbd`, `843e9e4`, `b15450f`) |
| the first run | `probe/results/w9b-demo-sw2026-20261117-1-script-faults.log` and its JSON (`2ed441b`) |
| the final run | `probe/results/w9b-demo-sw2026-20261117-2.log` and its JSON (`de0a470`) |

**Verdict.**

- **The fix round answers every point as I meant it.** Two new points remain, both should-fix (C1), plus a slip in
  the demonstration note (C2). Neither keeps W9b open.
- **The first run's eleven FAILs are the script's, as laid.** No fault of the app was explained away: in that run
  every body already stood at its frame on record, and the relief bore read r 12.5 between planes at 5 and 21.
- **The volume account is fair in substance but overstated in one figure.** Against the true section the residual
  is 9.0e-5, not 3.8e-5 (§2).
- **The final run meets W9b's Done-when on 2026, and no STOP fired.** The commit message overstates two things a
  little (§4).
- **Nothing unmeasured must be measured before W9b closes.** Two cheap reads should ride along in W9c's 2024 session
  (§5).

### 1. The review's points after the fix round

| Point | Answered? | How |
|---|---|---|
| 1 (must) a band over another shaft's hub | **Yes** | `engagement` errs at the mode's cell, whole or in part (`modes.py:251-268`), and `_check_clearances` exempts {sleeve, hub} (`checks.py:558-560`). The Meshes advice is gone. |
| 2 the reach sentence | **Yes** | One gear spanning both points is named once, with its span. |
| 3 a shared hub | **Yes, by ruling** | A hub keys one sleeve; a second riding it is an error, not also warned unkeyed. One owner choice is wrong: C1. |
| 4 K11's cell for the bands | **Yes** | `Start Band` and `End Band` are in `_GLOBAL_COLUMN`, with a test through `update_gearbox`. |
| 5 the shared file name | **Yes, by ruling** | No mark in the name; the error now says why: *(RangeSlv has bands and ModeSlv has none, …)*. |
| 6 a hub under a sleeve with no Slides | **Yes** | It is judged at the sleeve's one place. |
| N1 reach through the hub | **Yes** | `Extra` holds the band's points but not the hub's: with Hub it is reached, without it warned. That test can fail. |
| N5 the two band rules | **Yes** | Both now use `face - 1e-9`. |
| N2, N3, N4, N6 | Left | As I offered them. N4 (a thin wall over the relief) is the coordinator's to put to the user. |

**The new clash error.** I looked for wrong refusals and found none:

- A hub on a coaxial shaft that no band ever overlaps gets no error (a scratch case with a sleeve and hub on Aux at
  60 beside RangeSlv's box).
- A hub wholly under the relief is clean, and held to c as a dog is (`test_another_shafts_hub_under_the_relief…`).
- The band's own share is tested at `COVER_TOLERANCE`, so a hub touching a band edge (share 0) is not a clash. It
  gets the clearance warning at gap 0, as a dog does.
- Passing over a hub between two positions is not judged. That is the same as for a dog, where the stroke warning
  covers only dogs, so it is consistent and not new.

**C1 — should-fix: "a hub keys one sleeve" picks its sleeve from every Slides position, including positions no mode
picks.**

- `_rides` walks `sleeve.positions()` (`modes.py:189-200`). `hub_sleeve` then takes the first sleeve in sheet order
  that rides the hub at any position.
- *Reproduced against `checks.check`.* On Out:
  - S1 at 0, face 10, Slides `A=-7.5, N=0, X=+38`, with its hub H1 under it in A and N.
  - S2 at 40, face 10, Slides `B=0`, with its hub H2 at 40, face 6, under S2 in every mode.
  - The modes pick A/B and N/B only, so X is never used. Yet S1's place at X (33…43) rides H2, so H2 is keyed to S1.
- The read then says *"S2 rides H2, which keys S1: … give S2 a hub row of its own"*, though H2 is S2's own hub. It
  also says *"in M1 S1 and H2 do not cover one another"* in both modes.
- So a legal box is refused. It needs a position no mode uses, so it is rare.
- *Fix.* Key a hub to the sleeve that covers it in every mode (the mode picks, or the implicit place), and only then
  fall back to sheet order. A sleeve whose band covers it in one picked mode but not in every mode is then the
  second-sleeve error, as ruled.

**C2 — the note: `W9B-DEMONSTRATION.md`, *What the script does not measure*, says a Z− sleeve's "relief's planes'
flips take the other sign (`helical._flip_for`)".**

- They do not. `relief_ops` places both planes in the part's own frame. The flip depends only on
  `EXTRUDE_Z_SIGN × offset`, and the shaft's direction never reaches the part plan.
- On a Z− shaft only the assembly frame turns the part over, which W3's σ already does for every gear.
- A one-line correction to the note. It matters for §5 below.

### 2. The first run's eleven FAILs

There are 11: one bore, one volume and nine slides (`build`, `update` and `old`, three modes each). I read each
against the first log and its JSON.

- **The padded `GetBox` holds.**
  - The first run's bore check wanted a face whose box spanned the relief's length to a tight tolerance. It found
    none.
  - The final run reads the same part, with the same build ops and the same snapshot of the app's part code, and
    shows why: the cylinder's box runs z 4.759716…21.240284, padded 0.240284 mm at each end. The cylinder is
    exactly r 12.5, and the two step faces' `PlaneParams` give exactly 5 and 21 (4 and 21 after the change).
  - The self-check replays that on the first run's readings. Nothing of the app was at fault.
- **The slide's sign holds.**
  - The nine lines read 55.5, 48, 40.5 (and 34.5, 29.5, 24.5 in `old`) against the record's −55.5 … −24.5.
  - On the same lines, "every body at its frame on record" passed at 6.6e-10. The sleeve stood where the record
    says, and only the mate dimension's sign was missing.
  - The new check holds the size to the record and the sign by RangeSlv's own frame. A frame on the wrong side fails
    it (replayed). That is sound, and it does not compare the app with itself: the frame is SolidWorks' read.
- **The sixteen-fold amplification holds, and the account is fair, but the residual is understated.**
  - 16 × 114.638326 = 1834.213 against 1833.375 removed. The 0.838 is 16 × the 1 mm difference's own error, as laid.
  - The new check builds the expected banded volume from F0 = V(unbanded) / 26 over the bands, plus the ring
    π(Ro² − r²) over the relief (Ro 16.125 and r 12.5 from faces). It reads 3.8e-5 (5/5) and 3.5e-5 (4/5).
- **Weighing the "F0 two ways" line.** I computed the sleeve's section area from the app's own maths: π(Ro²) less
  the area inside the toothed edge (`internal.involute_flank`, `flank_point`), sampled 1, 4, 16 and 64 times as
  densely as the outline. It converges to **440.54751 mm²**.
  - SolidWorks' `GetArea` of the end face is **440.547728**, which is 5e-7 from the maths. So the model's section is
    right, and the face area is the truth.
  - V / 26 = 440.597841 is the mass-property volume reading 1.14e-4 high.
  - With the true section, the exact banded volumes are 9621.306 (5/5) and 9506.748 (4/5). SolidWorks reads 0.862
    and 0.782 mm³ over: **9.0e-5 and 8.2e-5**, not 3.8e-5 and 3.5e-5. The script's F0 absorbs most of the unbanded
    body's mass-property error into the "exact form".
  - The two banded readings imply the same toothed section, 440.6340 and 440.6347 (taking the ring as exact). So the
    banded bodies over-read about 0.086 mm³ per mm of toothed length, against the unbanded body's 0.050.
- **Is that a real geometric difference? Very likely not.**
  - The bands are untouched by the loft. Over the relief, every face that bounds the cut reads exact to 1e-6:
    r 12.5, both step planes, and Ro.
  - A geometric excess of 0.36 mm³ in the relief would need r small by 2.9e-4 mm or the planes 3e-3 mm apart, both
    hundreds of times what the reads allow.
  - What differs between the two bodies is their B-rep: each flank face is split at the step faces. Mass-property
    error depends on that. So "SolidWorks' mass-property accuracy" is a fair account.
  - But it is shown only indirectly, and "to 3.8e-5 of the exact form" overstates how exact the form is.
- **What would settle it at no cost.** Read the banded part's own end-face area and each step face's area. The step
  face should be F − π(Ro² − r²) = **114.558 mm²** exactly by the app's maths, against 114.638 from the two volumes.
  That compares the relief with the teeth directly, with no mass property in it.
- *My recommendation for the 2024 run:*
  - add those two `GetArea` reads, held to 1e-4 of the area;
  - take F from the end face, not from V / 26;
  - keep the volume check at 1e-4 as a coarse guard (9.0e-5 passes, with less room than the note claims).

### 3. The final run against the Done-when and the STOPs

- **Done-when** (plan §5: RangeBox_Fixed built from scratch on 2026, M7, every mode's engagement, slides and
  interference as §3): **met.**
  - `build` 0 failed.
  - In H, N and L the measured band, dog and hub spans equal §3's hard-coded table (`SECTION3`, `DOGS`, `HUB`, which
    are the plan's numbers, not the app's). The relief holds HighDog in N and L. The least gaps are 10, 2.5 and 1.0,
    with Hub 1.0 from HighDog.
  - No mate is in error, every app gear is free, and `Session.interferences` is empty in every mode. The couplings
    are on in H and L only.
  - **M7** for 2026: the relief built, its globals and links read back, its sketches under `Relief`, the bore a true
    cylinder between the planes, and the band changed and read back as plane offsets. 2024 is owed.
- **STOPs:** none fired.
  - The relief op did not fail, no mode read other than §3, and the read carried no warning but the fixture's four.
  - The *Post load updating* box during the Update (log :970) is the elapsed-time notification box. W9a's script
    exempts it by the coordinator's ruling, and it was seen in W9a's 2026 closing runs too. It is not a STOP.
- **Can each check fail?**
  - The measured spans come from SolidWorks frames and the parts' globals read live. They are held both to §3's
    constants and to the app's read, so they are not the app against itself.
  - Three things are the app's own:
    - the ratios. The *1.0 / neutral / 2.896552* on each mode line is the app's motion report, not a turn in
      SolidWorks;
    - the read's warnings, compared with `assess` of the fixture in the same process. That shows the Excel round
      trip, not a SolidWorks fact;
    - `old`'s "seven warnings, W9b's three among them". It checks the count and that W9b's three are present, not the
      text of the other four (the suite pins those).
  - None of the three is in the Done-when, so none weakens it.
- **The relief in the assembly is shown by its globals, its feature and the part section's geometry.**
  `no interference` in N and L cannot by itself prove the relief is there, since the unrelieved teeth would sit in
  phase over HighDog as built. The part section, through the same plan, is where the relief's geometry is measured,
  and that is adequate.
- **The corrected slide check** is sound (§2): size against the record, side by the frame, and either alone fails.
- **`update` shows what its lines claim.**
  - Start band 5 → 4 is classified as a value Update of `Sleeve_m1.25_N17` alone, pressed through the window's gate,
    and ends ok.
  - The part reads Start Band 4, with planes 4 and 21 and nothing in error.
  - Per mode, the start band reads −55.5…−51.5, −48…−44 and −40.5…−36.5 from SolidWorks. L's least gap is 2.0. The
    end band and engagement are as §3.
  - The bands taken off alone are refused at the workbook with the jam sentence, and nothing is offered.
  - RangeBox_Fixed made RangeBox again is sent to *Build again…* with both sentences (Hub removed; bands), the footer
    offers it, and its question carries the bands sentence.
  - Both refusals left every file's modification time and every save flag unchanged.
  - The value Update re-placed every gear in every mode (226 s). That is W8's rule for any changing press on a box
    with modes, not a W9b fault.
- **`old` shows RangeBox as before, with three more warnings.**
  - Seven warnings, W9b's three among them. Engagement, ratios and speeds as §3 (Carrier 517.857, Planet
    −1673.077).
  - RangeSlv is still Output's anchor, its sidecar is at schema 1, and there is no Relief.
  - Per mode, the whole sleeve reads −34.5…−24.5, −29.5…−19.5 and −24.5…−14.5 from SolidWorks, which are my hand
    numbers above, with N's gap 0 to both dogs. Frames, flags, freedom and interference are clean.

### 4. The commit message on `de0a470`

It claims nothing the log does not show, with two overstatements:

- *"its volume the exact form's to 3.8e-5"*: the form is calibrated by SolidWorks' own unbanded volume. Against the
  true section it is 9.0e-5 (§2). Still inside 1e-4, so the claim's substance stands.
- *"the ratios as ISSUE-1-PLAN §3's table"*: the ratios are the app's report on SolidWorks' build, not measured by
  turning.

The rest is in the log line for line: the one cylinder r 12.5 between 5 and 21, the sketches under Relief, Hub as
anchor with the spline, each mode's slide, bands, relief, engagement and gaps, no mate in error, every gear free, no
interference, the band Update read back in the part and per mode, the two refusals with nothing written, and RangeBox
with its seven warnings.

### 5. What stays unmeasured

| Unmeasured | Must it be measured before W9b closes? | Why |
|---|---|---|
| SolidWorks 2024 (M7's second version) | No | The plan puts it in W9c's 2024 session. It is the one item that is owed, not optional. |
| A banded sleeve on a Z− shaft | No | The part is identical whatever the shaft's direction (C2). Turning a part over on a Z− shaft is W3's σ, measured for every kind. `band_spans`' mapping to the part's origin is pure and agrees with `Placed.origin` (my first review). |
| Unequal bands from scratch | No | 4/5 was reached by the value route in `part` and `update` and read back exactly. From scratch differs only in the planes' first offsets, through the same `InsertRefPlane` with the same flip. |
| A hub with a bore | No | The hub's plan is a dog's with the spur's bore ops, measured in every bored gear since W1. |
| A typed Rim on a banded sleeve | No | Rim is the ring's own global, built before the relief and untouched by it. The error at or under m(z + 3) is pure. |
| The step faces' and the banded end face's areas | No, but cheap | Add them to the 2024 run (§2). They settle the volume question exactly. |

None of these is a reason to hold W9b open. I would not leave 2024 out of W9c's session. And I would add the two
area reads there, since they replace an indirect argument with a direct measurement at no SolidWorks cost.

### 6. In one line

**W9b is closed on SolidWorks 2026, with 2024 owed in W9c's session.** C1 (the hub's owner taken from unpicked
positions) and C2 (the note's Z− sentence) are should-fix and need not hold it.

---

## Addendum: W9b on SolidWorks 2024

*2026-11-17, from `probe/results/sw2024/w9b-demo-sw2024-20261117.log` and `w9b-demo-20261117-063302.json` (commit
`9e77303`). It ran in a fresh 2024 session from snapshot `529f939`, so the closing-review script `203ce86` and the
hub's sleeve choice `fca29a2` were both in it (both are ancestors of `529f939`).*

**The Done-when on 2024 is met.** RangeBox_Fixed was built from scratch by the app's Build:

- *The read.* It carries the fixture's four warnings only, with no warning from W9b's three checks and no stroke
  warning (:56-57).
- *The build.* It ends ok, with no interference (:893, :906). Hub is Output's anchor with `RangeSlv splined to Hub`
  (:909), and the sleeve's sidecar is at schema 2 with Relief (:910).
- *Each mode, measured from SolidWorks' frames and the parts' live globals.* In H, N and L the slide, the bands, the
  relief, the engagement, the least gaps (10, 2.5, 1.0) and Hub 1.0 from HighDog all match §3's own numbers. There is
  no mate in error, every gear is free, and there is no interference in any mode (:912-924).
- *`update`.* It is as on 2026: Start band 4 is a value Update, read back in the part and in every mode, with L's gap
  now 2.0 (:966-993). Both refusals wrote nothing (:1015-1016, :1068-1069).
- *`old`.* RangeBox carries seven warnings. W9b's three are now held to the plan's sentences word for word
  (:1086-1088). The sleeve is unbanded, at schema 1, and is Output's anchor (:1807).
- *What's Wrong* never showed (only the rule line, :7).
- *M7 on 2024 is met by its exact reads* (part :9-21): the globals and their links; the sketches under Relief; the
  bore one cylinder of r 12.5 between step planes at 5 and 21, to 1e-6; the band change read back as planes at 4
  and 21; no feature in error.

**Is the volume guard's failure a fault in the part?** No. The coordinator's reading is right.

- *The geometry reads the same on both versions.*
  - The end faces read 440.548068 and 440.556083 on 2024, against 440.547728 on 2026, and the app's own section
    maths converges to 440.54751.
  - The step faces read 114.302999694 and 114.294983996 on both versions, to nine figures.
  - The cylinder and the planes are exact on both versions.
- *Only the mass-property volumes differ between versions, by a constant per body.*
  - Unbanded: 11456.7366 on 2024 against 11455.5439 on 2026, +1.193.
  - Banded 5/5: 9622.5448 against 9622.1688, +0.376.
  - Banded 4/5: 9507.9065 against 9507.5305, +0.376.
  - The 5/5 − 4/5 difference is 114.638326 **on both versions**, to six decimals.
- *That pattern is a version's volume integration, not geometry.* A real difference in the part would move the face
  areas, or the difference that one millimetre of relief makes. It moves neither.
- *Against the true section,* 2024's volumes run 2.2e-4 high on the unbanded part and 1.3e-4 / 1.2e-4 on the banded
  ones. On 2026 they ran 1.1e-4 and 9.0e-5 / 8.2e-5. The banded body's residual is 0.55–0.79 of the control's on both
  versions.

**Taking the allowance from the control is sound, not bending the check, under three conditions:**

1. *Say what the guard is for.* The exact checks on the relief are the faces: r 12.5, the planes, the end-face
   section. The volume is a coarse guard against a gross fault, such as a relief not cut, a wrong diameter or a wrong
   span.
   - The smallest of those it must catch is a relief Ø off by 0.1 mm: 63 mm³, which is 6.5e-3 of the volume.
   - A relief 0.5 mm longer gives 3.3e-2.
   - So any allowance up to about 1e-3 still catches every fault it exists for.
2. *Calibrate on a control that differs only in the feature under test.* The unbanded sleeve from the same plan, built
   in the same session, is exactly that. It has more spline surface than the banded body, not less, so the control's
   residual is a fair upper scale for the banded one's.
3. *Use a factor of **1.0**, a floor of **1e-4** and a cap of **5e-4**.*
   - The allowance is max(1e-4, 1.0 × the control's residual against its own end face), and that value goes in the
     log.
   - A control residual over 5e-4 is itself a FAIL: the session's mass properties are not fit to judge by.
   - On the readings so far this passes with room: 2026 has 9.0e-5 against 1.1e-4, and 2024 has 1.3e-4 against
     2.2e-4.
   - I would accept a factor up to 1.5, not more. The evidence for anything larger is not there, and 1.0 already
     leaves 21 % room on 2026 and 41 % on 2024.

Replaying both versions' JSON against the new allowance is enough. No 2024 rerun is needed. For 2026, the final run's
JSON (from `b15450f`) predates the end-face reads. Its log has the front end face's area (`F0 two ways`, 440.547728),
which the replay should take, with the volumes from the same run.

**So W9b is closed on SolidWorks 2024** once that guard change and its replay are committed and pass. Nothing else in
the 2024 run stands in the way.

**The hub's sleeve choice (`fca29a2`) on SolidWorks.** It was in the snapshot, and this is its first run on
SolidWorks. The log bears it out as far as it can: every read of RangeBox_Fixed passes `hub_sleeve` through the row,
hub and shared-hub checks, and carries no hub error and no "nothing keys" warning (:56-57, :967-968). RangeBox's read
carries §3's own "nothing keys RangeSlv" word for word (:1087). The choice is pure, though: nothing about it depends
on SolidWorks, and the anchor in the assembly comes from `motion._sliding_shaft`, by kind. So the run shows that it
breaks nothing; the suite is what tests it.

**The step faces: 2.2e-3 under F − π(Ro² − r²) = 114.5587 on both versions.**

- *The volumes say the geometry is right and the cap's area is not the whole cap.* If 114.303 were the section inside
  r 12.5, then:
  - one millimetre of relief would remove 114.303 mm³. Both versions read 114.638, and the geometry says 114.559;
  - the 5/5 relief would remove 16 × 114.303 = 1828.85 mm³. 2026 reads 1833.38 and 2024 reads 1834.19, against
    1832.94 from the geometry.
- *The likeliest cause* is that each relief end's cap is more than one planar face (slivers at the roots, say). The
  script takes only the planar faces whose box spans the cylinder's diameter (`relief_bore`), and small faces would
  not. That the shortfall is identical to nine figures on two kernels fits a fixed B-rep better than an integration
  error, and `GetArea` reads the end face, with the same tooth edge, to 5e-7.
- *I would not leave it wholly unexplained, but it is worth little.* One read settles it: every planar face whose
  `PlaneParams` puts it at z = 5 (and 21), with its count and the sum of their areas.
  - If the sum is 114.559, it is explained, and the step-face check can sum them.
  - If one face reads 114.303 alone, then integrate its edges, as you suggest.
  - That is a part-only read of about a minute. Put it into the next SolidWorks session already planned (W9c's full
    build), not a session of its own.
- It does not bear on closing W9b: the relief's geometry is fixed by the cylinder, the planes and the end-face
  section, and the volumes agree with that geometry on both versions.

**What you must act on:**

- change the coarse volume guard as above (factor 1.0, floor 1e-4, cap 5e-4), and replay both versions' JSON;
- set the 2024 W9b status closed when the replay passes;
- optionally, add the step-plane face enumeration to W9c's full build.
