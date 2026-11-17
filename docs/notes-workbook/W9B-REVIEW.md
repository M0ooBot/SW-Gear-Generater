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
