# W9b's demonstration on SolidWorks: the sections, what each asserts, the times

The script is `probe/w9b_demonstration.py`. It covers ISSUE-1-PLAN §5's W9b *Done when* on SolidWorks 2026:
**RangeBox_Fixed built from scratch (M7) with every mode's engagement, slides and interference as §3**, and around it
the banded sleeve and the hub as parts, a band changed by Update, a structural edit answered with *Build again…*, and
RangeBox built as before W9b. It is written against W9b's public behaviour and the plan's numbers (W9B-INTERFACES,
§3), not its internals, so a reviewer's fixes to the code should not move it.

**How it runs.** It runs W9a's script's `main` (`w9a_demonstration.py`) with its own four sections. So everything W9a
does for a run is done here, unchanged:

- the attach and the PID check;
- the dialog watch, and the What's Wrong rule (on 2026, where the helper is False, any dialog during a job is the
  STOP at once);
- keep-awake;
- the JSON after every section (`w9b-demo-<time>.json`) and first in the `finally`;
- the guarded close;
- APPDATA in the run folder, asserted;
- `--sections` and `--redo`.

W9a's script gained only two names for this, `RUN_TITLE` and `JSON_STEM`, which W9b sets to its own; W9a's own runs
are as before. No document title but the run's own is logged, and SolidWorks' frame never is.

**Without SolidWorks:** `python probe/w9b_demonstration.py --self-check` computes §3's numbers from the fixture
(`tests/workbook_fixtures.range_box_fixed`) through the app's own `assess` and `modes.band_spans`, runs the same pure
judgement the live sections use (`judge_mode`, `section3_of`) on them, and checks the edits' legality. At this commit
it passes, 0 failed. `--help` prints the usage without importing anything of SolidWorks.

## Sections

Run in this order; each runs alone (`update` builds fixed.master first if this `<out>` has none). Times are estimates
for SolidWorks 2026, from W9a's and S0's measured runs: RangeBox built in 124 s on 2026 (S0's master), and an Update
that puts every mode took about 4 min there.

| # | Section | What it does and asserts | 2026 |
|---|---|---|---|
| 1 | `part` | RangeBox_Fixed's RangeSlv built unbanded and banded (face 26, bands 5/5) by the strip's own `plan_for` and `swbuild.build`, each closed before the next (they share a file name). Banded, read back from SolidWorks: the globals Start Band 5, End Band 5, Relief Diameter 25.0; Relief Start Plane and Relief End Plane offset 5 and 21, each offset's equation linking it to its globals; each relief sketch's circle Ø 25.0, linked to Relief Diameter; the Relief feature present by name, nothing in error. The bore over the relief from the part's faces, and the relief sketches under Relief in the tree (see below). Then Start Band 5 → 4 through the strip's value route (`swbuild.update_variables`), read back: Start Band 4, the planes 4 and 21, no error. **The volumes:** see below. Then Hub (17 teeth, face 20) built, no error. | 3 min |
| 2 | `build` | RangeBox_Fixed written by `write_new` and built from scratch by the app's own Build (W8's `build_turning`, as W9a's reducer). Kept as `fixed.master`. **Details below.** | 5 min |
| 3 | `update` | A copy of fixed.master, three steps. **Details below.** | 7 min |
| 4 | `old` | RangeBox as it is, written and built by today's app. **Details below.** | 4.5 min |

**About 20 minutes in all on 2026**, inside the plan's 30. Were it over, I would cut `old` to its read alone (the
warnings and engagement, which need no SolidWorks).

**`build`.**

- **The read's warnings** are the fixture's own: the four `assess` gives for the fixture in this process, compared
  without their cells. None comes from W9b's three checks (`reach_warnings`, `hub_warnings`, `clearance_warnings` give
  none), and there is no stroke warning.
- **The Build** ends ok, with no interference, no warning beyond those four after it, and the turning checks W8's
  `build_turning` makes.
- **Hub as Output's anchor:** the built plan's anchors give `Hub`, and the record holds Hub on Output Axis, Hub along
  Output, RangeSlv splined to Hub, RangeSlv along Output and both couplings.
- **The sleeve's sidecar** is at schema 2, with Relief among its features.
- **Per mode H, N, L**, each shown and rebuilt:
  - every body at its frame on record (1e-6 mm);
  - no mate in error;
  - every app gear but the fixed Ring free to turn;
  - no interference (`Session.interferences`);
  - the slide's value as on record by its size, and RangeSlv's Front plane at its signed value (below);
  - RangeSlv moved −7.5, 0 and +7.5 from N;
  - every mate's flag as on record: the couplings on in H, respectively L, only.
- **The bands, the relief, the dogs and the hub measured from the model**: each component's frame, and its part's own
  Face Width, Start Band and End Band as SolidWorks holds them. These are held to what the app's read places, and to
  §3's table, within 1e-4 mm:
  - **the end band** covers HighDog in H and LowDog in L;
  - **the relief** holds HighDog in N and L;
  - **the least running gaps:** H 10 (end band to LowDog); N 2.5 (end band to HighDog and to LowDog); L 1.0 (start
    band to HighDog); Hub to HighDog 1.0;
  - **the ratios:** 1.000 in H, 2.896552 in L, neutral in N, from the app's report.

**`update`.**

1. **A band changed.** Start band 5 → 4 in Excel (the self-check shows it legal: the same four warnings). Classify
   makes it a value Update of the sleeve's part alone, with no structural change. The Update is pressed through the
   window's gate and ends ok. The part then reads Start Band 4, planes 4 and 21, and nothing in error. Per mode, the
   same checks as `build` against the app's read of the edited workbook (start band now 4 long; L's least gap 2.0),
   and §3's end band and engagement unchanged.
2. **The bands taken off alone.** This is refused at the workbook (the 26 mm sleeve jams L, and Hub is uncovered in N
   and L), with neither Update nor Build offered.
3. **The bands taken off by the smallest legal edit**: RangeSlv as RangeBox has it (at −24.5, face 10, slides ±5, no
   bands) and Hub's row cleared. Classify sends it to *Build again…*, naming "Bands cannot be given to or taken from a
   built sleeve…". The footer offers Build again…, and its question says the same.

Steps 2 and 3 write nothing to SolidWorks: every SLDPRT and SLDASM in the copy has the same modification time, and no
document's save flag changes.

**`old`.** RangeBox, built by today's app, the "nothing of today changed" build.

- **The read:** seven warnings, W9b's three among them (reach, no hub, N's clearance); §3's engagement, ratios and
  speeds (Carrier 517.857 rpm, Planet −1673.077 rpm).
- **After the build:** RangeSlv still Output's anchor; the sleeve unbanded as before (no bands in its record, sidecar
  at schema 1, no Relief).
- **Per mode,** as `build` but without bands: frames, flags, gears free, no interference, the whole sleeve and the
  dogs where the app places them.
- **Why not S0's `rangebox.master`:** it was built by an app before W9b, which changed the anchor rule and engagement,
  so it cannot show that today's app builds RangeBox as before.

### The volumes (M7's measure of the relief)

**The section from the face (after the closing review, e5cbc98).** The unbanded sleeve is one section along its
whole face (Blank, Tooth Space, Teeth). F0 is now its front end face's area (`IFace2.GetArea`, read on the unbanded
and the banded part, and logged). On the final 2026 run it read 440.547728 mm², where the reviewer worked the section
from the app's geometry to 440.54751. V/26 reads 440.5978, 1.1e-4 high: SolidWorks' volume error. Where GetArea cannot
be read, F0 falls back to V/26, and the log says so.

**The volumes, a coarse guard.** Each band keeps the section F0. Over the relief the section is the ring between the
bore and the outside, π(Ro² − r²), with Ro (16.125) and r (12.5) taken from the cylinders the faces read. So

  V(banded) = F0 × (start band + end band) + π(Ro² − r²) × (26 − start band − end band),

checked for 5/5 and for 4/5 to 1e-4 of the part's volume, with the residual and the room left printed. **The room is
small:** against the face's section the final run's banded parts are 9.0e-5 (5/5) and 8.2e-5 (4/5) over, leaving 10%
and 18% of the 1e-4. The volume errs high by about 1e-4, as V/26 does. A relief 0.5 mm wider would miss by 3.3e-2, so
the guard still catches a wrong relief. Before the review the script took F0 = V/26, which carried most of that error
into the expected volumes and printed 3.8e-5 and 3.5e-5.

**The step faces.** The two planar faces at the relief's ends must read one area, to 2e-4. That holds a pair of
GetArea readings of one section: the final run's two end faces agree to 7.3e-5.

Each step face against the same geometry, F0 − π(Ro² − r²) = 114.558 mm², is logged and **not judged**. On the final
run they read 114.303 and 114.295, 2.2e-3 under it. The same reading's end faces match the worked section to 5e-7,
and the volumes match the section to 1e-4. A step area of 114.30 would put the 5/5 volume 3.4e-4 off, against 9.0e-5
with 114.558. So GetArea on the step faces, whose boundary is the bore's circle and the 17 tooth spaces, reads low
here, and does not settle the relief to better than that. Why it does is open.

**What it replaced.** The first run took the area per mm from the 1 mm difference of two volumes and multiplied it by
16. That multiplied the mass-property error by 16 and failed (1833.375 against 1834.213). The difference stays, as a
fact line and in the bounds check: it must lie strictly between π(12.5² − 12.375²) = 9.768 mm² (no tooth at all) and
π(12.5² − 9.375²) = 214.757 mm² (a full ring of teeth to the tips). The runs read 114.638.

All volumes are `Session.volume_mm3` of the part, active.

### The bore over the relief

`IFace2.GetBox` is padded: the first run's bore read box z 4.76…21.24. So the bore is found by its surface, exactly
one cylinder of r 12.5 (to 1e-6 mm) with its axis along the part's z. Its ends are the two planar step faces whose box
is the cylinder's across, each plane's z from `PlaneParams` at 5 and 21 (4 and 21 after the change), to 1e-6 mm. The
log says how much SolidWorks padded the box: 0.240284 mm at each end in the first run. The two relief sketches must
sit under Relief in the feature tree (`GetFirstSubFeature`), absorbed by the loft cut; if that read raises, it is
said as a fact.

### The slide's value

SolidWorks gives a distance mate's dimension without a sign (the first run read 55.5 where the record holds −55.5).
The app sets |z_front| and lets the mate's Flip carry the side. So the read's size is held to the record's, and the
sign to the slider's own frame: RangeSlv's origin, its Front plane, must stand at the record's signed value to 1e-6 mm.
Either sign does not pass on its own: a frame on the other side fails.

**Replayed without SolidWorks.** `--self-check` replays all three on the first run's committed readings
(`probe/results/w9b-demo-20261117-045137.json` and its log). That run kept no `PlaneParams`, so its thin planar faces
are given the z their padded boxes centre on. At this commit it passes: the bore and its ends, both volumes, and the
nine slides, with a wrong relief and a wrong-side frame each failing. From now on each mode's readings go into the
JSON too (`modes`). It also replays the closing review's points on the final run's readings
(`probe/results/w9b-demo-20261117-051122.json`, whose faces carry `PlaneParams` and `GetArea`): F0 from the front face,
both end faces as one, the bore, the volumes against the face's section (9.0e-5 and 8.2e-5), and the two step faces as
one. The step faces against 114.558 are printed, not judged.

## STOPs

As W9a's:

- any dialog during a job (§0.3);
- a read that marks a document;
- a hung worker;
- under 2 GB free.

W9b's own (plan §5):

- **the relief op failing**: a part that does not build is the STOP at once;
- **a mode reading other than §3**: a failed check in `build`'s per-mode lines, read by the coordinator;
- **a warning on the fixture other than §3's**: a failed check in `build`'s read.

## What rests on the app's own word, not on a SolidWorks measurement

- **The ratios** (1.000 in H, 2.896552 in L, neutral in N) are the app's motion report; nothing turns the gears to
  measure them.
- **The warnings** are compared with the app's own read of the fixture (`assess` in this process) and with W9b's
  three checks run on it, not with an independent list. `build` holds RangeBox_Fixed's four to that read.
- **`old`** checks its seven warnings by count. Since the closing review it also checks W9b's three by text against
  §2.2's and §2.3's sentences, word for word without their cells; `--self-check` holds the app's sentences to the same
  text.

## What the script does not measure

- **A banded sleeve on a Z− shaft.** The bands then run the other way round in global z; the relief's planes are
  the same, since they sit in the part's own frame (the part is turned in the assembly, not rebuilt).
- **Unequal bands built from scratch.** Start 4 / End 5 is reached only by the value change, in `part` and in
  `update`.
- **SolidWorks 2024.** Plan §5 puts that in W9c's 2024 session, about 50 min.
- **A hub with a bore** (RangeBox_Fixed's Hub has none), and a hub on a Z− shaft.
- **A typed Rim on a banded sleeve.**
- **Bands added to or taken from a built sleeve in place.** That is W9c (M8); here it is *Build again…* only.
- **W9b's checks on SolidWorks:** they are pure, and `build` and `old` only show which warnings the reads carry.
