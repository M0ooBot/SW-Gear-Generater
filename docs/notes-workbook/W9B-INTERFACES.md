# W9b: the sleeve's bands, the hub and the sleeve checks — the interface

Stage W9b of `ISSUE-1-PLAN.md` (§2.2 to §2.4, §3, §5; K7 to K10), written against the fake. This note fixes the
words, shapes and op route the two packages share before any code; a change to one of them is a stop-and-ask, as at
W8 and W9a. Package B is the schema, model, engagement per band, the `hub` kind and its rules, the relief op, the
record and the board; package A the pure checks (reach, the hub warning, running clearance) and the W8 fixtures'
pins. Nothing here is W9c's (bands or a hub added to a built gearbox by Update): those stay *Build again…*.

## 1. The Gears sheet's two columns

| Key | Header | Unit | Blank | Help |
|---|---|---|---|---|
| `start_band` | **Start band** | mm | teeth over the whole face | A sleeve only: its toothed length at the start of its face, the end toward its shaft's Axis minus side. With End band, the span between is a relief bore. |
| `end_band` | **End band** | mm | teeth over the whole face | A sleeve only: its toothed length at the end of its face. |

Both numeric, after Slides and before Part name (`schema.GEARS`), as W8 put Slides before Part name. The workbook
stays at Format 1; a workbook without the columns reads as before (both blank). The words are the plan's working
names, kept: they say which end, and "band" is the plan's own word for a toothed length.

**Errors at the cell** (the strip's own check of a sleeve, `SleeveKind.validate`, so the row is left out as any row
with an error of its own): a band not more than 0; one band given and the other blank ("give both, or neither");
a band as long as the face or longer ("exceeds the face"); two bands whose sum leaves no relief (at End band); a
typed Rim not more than the relief's diameter m(z + 3) (at Rim). **Bands on a row that is not a sleeve** is an error
at each band's cell, from `modes.row_errors`. *More than two bands* cannot be written: each column holds one number,
and a cell such as `5, 5` is the read's own "must be a number" error, which names no phase.

## 2. Bands in the model and in a sleeve's spec

- `model.Gear` gains `start_band`, `end_band` (text as typed; the fields after `notes`, before `row`, so every
  positional use stays as it is). `Gear.spec_values` passes them on.
- `spec.GearSpec` gains `start_band`, `end_band` (`""` = none). **`GearSpec.to_dict` leaves both out when both are
  blank**, so an unbanded part's `.gear.json` and its record entry are byte for byte what they were, and an older
  app's `from_dict` sees no new key. `GearSpec.bands_mm()` → `None` or `(b1, b2)` in mm.
- Where the bands sit (`modes.band_spans(gear, placed)`): the start band is at the part's front face (its origin,
  the Axis minus end of the face), so in global z, on a Z+ shaft `[z0, z0 + b1]` and `[z1 − b2, z1]`, on a Z− shaft
  the other way round. Unbanded, the one span is the whole face (word `""`). A *band* below means a span of this
  list, so every per-band rule reads an unbanded sleeve exactly as W8 did.
- **Engagement per band** (`modes.engagement`): each band is judged as a sleeve is today; a dog under the relief
  overlaps no band and is not engaged. An unbanded sleeve's sentences are W8's word for word; a band's partial cover
  says *RangeSlv's start band covers …*. The stroke warning (`modes.mode_checks`) is per band: a band longer than
  the gap between two dogs within that band's travel.

## 3. The `hub` kind and its rules (K8)

- `schema.KINDS` gains `hub` (after `dog`); `gears.WORKBOOK_KINDS["hub"] = clutch.HubKind()`: an external spline ring
  as a dog is (the spur plan, the row's Bore), kind word `hub`; part stem `Hub_m1.25_N17`
  (`spec.CLUTCH_WORDS`); the strip refuses its part as it refuses a sleeve's or dog's.
- **A hub's sleeve** (`modes.hub_sleeve(spec, gear)`): the sleeve on the hub's shaft whose bands, over its
  positions, overlap the hub; the first sleeve on that shaft when none does.
- **Errors**, each at its cell (`modes.row_errors` for the rows, `modes.hub_errors` per mode): Slides on a hub (Slides);
  a hub on Meshes (Meshes); a hub on a shaft with no sleeve (Kind); a hub whose teeth, module or pressure angle are
  not its sleeve's (Teeth: it carries the sleeve on those teeth); a hub on a carrier's, a turned or a fixed shaft, as
  a sleeve or dog there; and **in every mode a band of its sleeve covers it whole, or it the band** (the narrower
  covered), else an error at that mode's Modes cell (the hub's Gears cell with no Modes rows).
- A hub engages nothing: engagement looks at dogs only, and a hub is not one.
- **Anchor (J9)**: on a shaft with sliders, `motion._sliding_shaft` takes a hub before any other gear that does not
  slide, so the hub is the shaft's anchor (`Hub on Output Axis`, `Hub along Output`) and the sleeve gets
  `RangeSlv splined to Hub`. A shaft with no hub keeps W8's anchor.

## 4. The relief op route

**Chosen: the internal ring's plan, unchanged, and then a loft cut between two circles of Ø m(z + 3) on two
reference planes** at `Start Band` and at `Face Width − End Band` from the Front plane:

```
globals (after the ring's):  "Start Band" = b1,  "End Band" = b2,  "Relief Diameter" = ( "No. of Teeth" + 3 ) * "Module"
after the teeth pattern:     RefPlane Relief Start Plane (plane 1, b1)         Offset@ = "Start Band"
                             RefPlane Relief End Plane (plane 1, face − b2)     Offset@ = "Face Width" - "End Band"
                             sketch on each: one circle, centre on the origin, Ø "Relief Diameter"
                                                                               (Relief Start Sketch, Relief End Sketch)
                             LoftCut Relief through the two sketches
```

Each plane's flip is `helical._flip_for` of its side, `findings.EXTRUDE_Z_SIGN` × offset, as the herringbone's
mid-plane and the helical gear's profile plane are made. So **the banded plan equals the sleeve's unbanded plan
plus those three globals and those relief ops**, and the bands are globals: a band changed on a banded sleeve is a
value Update; bands given to or taken from a built sleeve are a structural change (`swbuild.structural_change`
says so: *Build again…*, until W9c adds them in place).

*Why this route.* Every call it makes has run on SolidWorks 2026 and 2024 in a built part: `InsertRefPlane` offset
from the Front plane with the flip finding (the helical and herringbone gears, the layout part); a sketch opened on
a plane the build made, with a coincident to the origin (the helical space sketch); a circle with its diameter
linked to a global (every blank and bore); `InsertCutBlend` through closed sketches on made planes (the bevel gear's
teeth, `findings.LOFT_CUT_TYPE`). The alternatives each need something never run: `Cut` is through all in both
directions (`swcom.cut_extrude`) and cannot stop at a band; the herringbone groove's blind extrudes and a plain ring
between build from the Front plane, so the far band needs either an extrude of a sketch on an offset plane
(`FeatureExtrusion3` there never run) or the mirror, which makes the bands equal; a `SweepCut` names its twist by
value, and a twist of 0 has never been made or named. The loft keeps the ring's ops as they are, which is what the
plan's test asks.

*No finding gate.* No SolidWorks call is new, none can open a dialog the build has not met, and a failure of any
op is a `SolidWorksError` naming it, as for every part. So nothing new refuses before M7: M7's build of
`RangeBox_Fixed` (plan §4) is the measurement. What it should read on SolidWorks, beyond §3's engagement, slides and
interference in every mode: the sleeve part rebuilt with no error and its `Relief` feature named; the part's volume
the unbanded sleeve's less, over the relief's length face − b1 − b2, the sleeve's section inside Ø m(z + 3) (its teeth
and the metal between its root and that diameter); a band changed in the workbook and Updated, read back as the
planes' offsets. If any of these fail, it is §5's STOP.

## 5. The record and the sidecar

- **Link record schema 8** (`store.LINK_SCHEMA_VERSION`, `_W9A_LINK_SCHEMA = 7` kept beside it): no new field. A
  sleeve's bands ride in its part entry's `spec` (by `GearSpec.to_dict`), and a W9a-era app refuses a schema 8
  record and leaves it byte-identical, as `store` refuses any newer one, so it never rebuilds a banded sleeve as an
  unbanded one. Schema 6 and 7 records read as before.
- **Sidecar schema 2 for a banded part.** `store.SCHEMA_VERSION` (the newest this app reads) becomes 2;
  `store.sidecar_schema(spec)` is 2 when the spec has a band, else 1 (`PLAIN_SCHEMA`), and `new_sidecar` and
  `updated_sidecar` write that. A part without bands stays at 1, byte for byte; an older app refuses a schema 2
  `.gear.json` and leaves it alone (`UnknownSchema`).

## 6. Package A's checks (pure, `workbook/modes.py`, called by `checks.check` after `mode_checks`)

- `running_clearance(module: float) -> float`: c = max(0.5, 0.5 × module).
- `reach_warnings(spec: GearboxSpec, placed: Dict[str, Placed]) -> List[Diagnostic]` (K7, §2.2): per sleeve, a
  warning at its Gears cell when both ends are blocked; presence and cover by `COVER_TOLERANCE`, open intervals; a
  carrier's planets count as its gears; with a hub, p− and p+ are the hub's; with bands and no hub, each band is
  tried for the whole face and the warning stands only if every band is blocked both ways. The shaft named in the
  sentence and the gears it passes: *Output cannot reach RangeSlv: Input runs through RangeSlv's travel (from Sun at
  10.5 to HighDog at −32), so Output would have to pass HighDog toward Z− or Sun toward Z+, each on Input.* The two
  gears in Gears-sheet order after *from*; for each end the blocking gear nearest the point.
- `hub_warnings(spec, placed) -> List[Diagnostic]` (K8): a sleeve with no hub of its own, at its Gears cell, §2.2's
  sentence; *"; as laid out none can, since …"* when no hub could fit: none inside what every place of one band
  shares, clear of the gears of the other shafts on its line, and none covering one band's whole travel clear of
  them.
- `clearance_warnings(spec, placed, reports) -> List[Diagnostic]` (K9, §2.3): per mode, per sleeve, every dog or hub
  on another shaft on its line that no band engages there, standing less than c from a band (0 ≤ gap < c), one
  warning at the mode's Modes cell; and once, at the hub's Gears cell, a hub less than c from a dog on another shaft.
  The gap exactly c is clean.

The W8 fixtures each gain exactly three warnings (§3): reach on RangeSlv, the hub on RangeSlv and on ModeSlv. Their
pins move by three.
