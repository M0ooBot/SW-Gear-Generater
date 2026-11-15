# W6 (right-angle): the implementation plan

**Authority and reading order.** `docs/PLAN-WORKBOOK.md` is the authority (§1's Axis column, §3.3–§3.5, §4.2–§4.5,
§6's W6 row: *"Turned axes, bevel and crossed meshes. A bevel stage feeding a parallel stage builds; sub-plan and
questions at the time."*). W5's decisions stay in force (`W5-DECISIONS.md`, `W5-INTERFACES.md`, PLAN-WORKBOOK §4.5
*Readings chosen (W5)*): each shaft's anchor is mated coincident to its layout axis and along it, every other gear on
the shaft is held by a lock alone, every gear mate is read back and made again when it turns the wrong way (no Flip
is ever assumed), a refused mate stops the build, an Update that must put any gear puts the whole train back at its
built turn, there is no datum plane, and the Checks panel shows problems only. This plan builds on `workbook` as
committed at `37b9eb6` (W5 closed at `7e4a686`, the small-pinion merge `0f5a121`, the shifted-pinion ring checks
`d3f4dcf` and `9efde87`), and is revised to the review `W6-PLAN-REVIEW.md` (`8f872f3`) and the orchestrator's
rulings on it (*Changes after the review*, at the end).

**The testing rule of 2026-11-14** (HANDOFF, *Rules carried over*) shapes the whole plan: W6 is written against the
fake, then built end to end on SolidWorks 2026 early; only what that build gets wrong is probed step by step; a call
is probed ahead only when it is not used before and could hang, raise a dialog, or damage a file or a session (§7);
SolidWorks 2024 gets one confirming build at the end. Findings are still read from committed `findings.py` only, with
`getattr(findings, NAME, None)`, and a missing one still refuses with a sentence. Where those two halves of the rule
meet (the app needs a finding no committed probe gives), the orchestrator ruled: the one probe W6 needs (§7.2, tier
9) runs **first**, on SolidWorks 2026, while the packages are written against the fake, and the full build then
confirms its finding with real teeth.

House rules for every package: commits by explicit path, prose messages with the why, no Claude co-author or
attribution line, never `add -A` / `commit -a` / stash / reset / rebase; every raise a full sentence; the repo is
public (no user document titles in committed logs). The orchestrating session pushes; packages commit only.

---

## 1. Scope

### 1.1 What W6 adds, piece by piece, with what exists and what is missing

| Piece | Exists in the code | Missing |
|---|---|---|
| **Axes other than Z±** (`X+ X- Y+ Y-` and `dx, dy, dz`) | Read and validated: `schema.AXES`, `model._check_value` keeps a vector as `"dx, dy, dz"` text. Everything after the read refuses them: `geometry.layout` (*"axes other than Z+ and Z- are laid out in phase W6"*), `kinematics.solve` (*"Speeds through a turned axis (a right-angle stage) are worked out in phase W6."*), `checks.check` stops at `lay.later`, `build.later_rows` (*"S3's axis is X+: turned axes are laid out in phase W6, and the gearbox is not checked until then."*), `layout.shaft_layouts` raises. | A unit direction per shaft, a frame per gear for any axis, layout planes from the Front plane, a layout axis for a slanted direction, and every check, phase and speed for them. |
| **Bevel meshes** | Single bevel gears of every form (cone, crown, internal) are derived, validated and planned (`gears/bevel.py`), and built on SolidWorks 2026 by the strip (PLAN-BEVEL-INTERNAL, *As executed*: m3 20:40 at 90°, crown and internal pairs at `70e3e1b`); a pair's static assembly is `pair.bevel_assembly_plan` (apex at each part's origin, gear 2 at `rot_y(Σ)·rot_z(pair.mate_angle(z2))`, held by a point mate, an axis-in-plane mate and two angle mates). In the workbook, `build.LATER["bevel"]` refuses every bevel row (*"G5 is a bevel gear: right-angle stages are built in phase W6."*), `geometry.LATER_KINDS` leaves it out, and `model.Gear.spec_values` fills `shaft_angle="90"`, `mate_teeth=""`. | Each bevel gear's mate teeth and shaft angle from its Meshes row and the two axes; its place (apex at `At`); its phase against its partner; the apex check; its gear mate in a turning train (never made before anywhere: `pair.assembly_plan` refuses *"A gear mate is built only for gears on parallel shafts so far"*). |
| **Crossed helical meshes** | `gears/crossed.py`: centre distance, `placement` (gear 1 on Z at the origin, gear 2 at `x = C`, turned `−(s1β1 + s2β2)` about X, spun so a tooth faces gear 1), `tooth_direction`, `validate`; `pair.crossed_assembly_plan` builds a fixed or mated pair (built on 2026: mn 2, 20:40, β 45/45 R). | Crossed meshes between workbook shafts at any place and angle: the common perpendicular, the signed crossing angle against the hands, the contact inside both faces, the phase, the kinematic sense, and the gear mate. |
| **Gear mates on non-parallel axes** | `swcom.Session.gear_mate_sense` reads `Reverse` and the two entity directions and **refuses** axes that are not parallel (*"…holds two gear axes that are not parallel (their cosine is …)"*); `swbuild._planned_sigma`, `_sense_read`, `_internal_meshes` and the two Update sense loops take each gear's sense from `rotation[8]` (its Z component), which is meaningless for a gear on X or Y. The macro database says it plainly: *"Gear mates between non-parallel axes (bevel, crossed) were not tried"* (`SW-Macro-Database/entries/assemblies/10`). | A read-back rule for turned axes (§2.6), every `sigma`-from-`rotation[8]` site generalised to the gear's axis vector, and the build kwargs that carry each mesh's sense. |
| **Anchors along a turned shaft** | `motion.motion_plan` measures every anchor from the layout's Front plane (`"layout:plane1"`, `frames[anchor].at[2]`, global `"<Gear> Face Z"`). | The plane square to the shaft: Right for X, Top for Y, the nearest base plane for a slant (§2.6). |
| **The record** | Schema 3 (`store.LINK_SCHEMA_VERSION`); `ShaftEntry` has `x, y, sigma` and X/Y planes only; `MateEntry` has no plane. `store._entries` drops keys it does not know, so a W5 build reading a W6 record would drop the new fields silently. | Schema 4 (§2.8). |

### 1.2 What stays refused, and with which sentence

Unchanged, word for word (`build.later_rows`, `geometry.layout`, `kinematics.solve`): carriers and copies (*"…carriers
are laid out in phase W7, and the gearbox is not checked until then."*, *"Speeds through a carrier (a planetary) are
worked out in phase W7."*), sleeves and dog rings (*"…built in phase W8, with modes"*), sliding gears and the Modes
sheet. `build.LATER` loses `"bevel"`; `geometry.LATER_KINDS` loses `"bevel"`; the turned-axis branch of
`later_rows` and both W6 sentences above go.

New refusals inside W6, each an error at its cell (exact words in §2.9): a bevel gear that meshes nothing; a bevel
gear cut for two different mates or shaft angles; bevel gears on parallel shafts; spur, herringbone or ring gears on
shafts at an angle; crossed helical gears with profile shift, of different normal module or pressure angle, or whose
hands and helix angles do not make the angle their shafts cross at; a crossed contact outside either face.

---

## 2. The design

### 2.1 Axes, facing and frames

**The direction.** `geometry.axis_vector(text)` turns an Axis cell into a unit vector: the six words exactly
(`Z+ → (0, 0, 1)`, …), a vector normalised. A vector whose direction is within 1e-12 of a cardinal one is that
cardinal axis (so `0, 0, -2` lays out as `Z-` and builds with planes), and the record keeps the canonical word, so
retyping `1, 0, 0` as `X+` (or back) is no change at all.

**Facing (decision D1).** A gear's own +Z points along its shaft's Axis, always. This is what W4 already does for Z−
(`layout.frame`'s `F₋ = rot_x(180°)` puts the part's +Z on −Z, and `Placed.z_front = z − σ·face/2` puts the blank on
the +Axis side of its front face). For a bevel gear, whose part has its pitch apex at the origin and its body along
+Z for a pitch cone under 90° (`bevel.blank_points`: generatrix `(sin δ, cos δ)` in `(radial, axial)`), the body
therefore lies on the +Axis side of its apex, and the user says which way a bevel gear faces by the sign of its
shaft's Axis. The consequence, stated for the user (review S3): two bevel gears on one shaft always face the same way,
so a cross shaft with a bevel at each end facing apart (or back to back) cannot be written; a per-gear facing (a word
in `Side`, or the sign of a bevel's At) is the third option, left to the user. The shaft angle Σ of a bevel mesh is the angle between the two shafts' Axis directions; for a crossed
mesh only the lines matter (a helical gear turned end over end keeps its hand).

**`At` of a bevel gear (decision D2)** is the distance along the Axis from the shaft's point to the pitch apex, as
PLAN-WORKBOOK §1 and the schema's help text already say (`schema` Gears column `at`: *"…(a bevel gear: its cone
tip)"*). Every other kind keeps the middle of its face.

**The base frame.** `geometry.base_frame(direction)` gives the rotation `B = [u₀ | a × u₀ | a]` (columns), where
`u₀` is world +X projected onto the plane square to `a`, or world +Y when `|a × X| < 1e-9`. It reproduces W4 exactly:
`Z+ → I`, `Z- → diag(1, −1, −1)` (= `F₋`). For `X+`, `u₀ = +Y`, `v₀ = +Z`; `X-`: `+Y`, `−Z`; `Y+`: `+X`, `−Z`; `Y-`:
`+X`, `+Z`. A gear turned θ about its own axis is placed by `R = B · rot_z(θ)`, origin at its part origin: the front
face centre (`centre − a·face/2`), or for a bevel gear the apex (`centre`). `layout.frame` takes this form; for
every Z± gear it gives W4's numbers to the last bit (a test on every committed fixture's frames).

**Families.** Shafts whose directions are parallel or anti-parallel form a family, with a plus direction (the
cardinal word's `+`, or for a slant the direction whose first non-zero component is positive). Within a family the
W3 parallel maths is used unchanged by working in the family's plus frame `B₊`: a gear's `(x, y, z)` are its
At-point's coordinates in `B₊` and `σ` is ±1 against the plus direction. For the Z family `B₊ = I`, so `Placed.x, y,
z, sigma` keep their W3 meaning, and every W3–W5 test stands.

**`Placed`** (geometry.py) gains: `axis: Vec3` (the gear's own +Z in world), `centre: Vec3` (the world point at `At`),
`family: Vec3` (its family's plus direction), `bevel: bool`, and the property `origin: Vec3`. `x, y, z, sigma` are
the family-frame values above.

### 2.2 The layout part

**Cardinal axes (D3).** An axis is where two planes cross, each offset from a base plane, as W4 makes Z axes
(`layout.layout_plan`: `RefPlane` + `LinkDimension` + `Axis` through two plane refs). The two coordinates square to
the shaft's axis are used:

| Axis | Planes | Globals | Base planes when 0 |
|---|---|---|---|
| Z± | X from Right, Y from Top (W4) | `"S1 X"`, `"S1 Y"` | Right, Top |
| X± | Y from Top, Z from Front | `"S1 Y"`, `"S1 Z"` | Top, Front |
| Y± | X from Right, Z from Front | `"S1 X"`, `"S1 Z"` | Right, Front |

The along-axis coordinate of the shaft's point has no plane and no global (an axis has no end, as Z already has no
global in W4); it moves only the gears, through their places along the shaft (§2.6). A plane from Front takes the
flip `findings.REF_PLANE_UNFLIPPED_IS_PLUS_Z` settled (probe `ref_plane_offset`: unflipped is the plus side), read in
`layout.flip_for("front", value)` alongside `LAYOUT_PLUS_FLIP`'s `right` and `top`; a minus-side plane is linked
negated by `LAYOUT_NEGATED_LINK` as W4's are; a coordinate that changes side, or reaches or leaves 0, is structural
(`OFFSET_GLOBAL_CROSSES_ZERO` is False for any base plane). The plane pairs Top+Front and Right+Front are new
combinations of a probed call; the direction SolidWorks gives such an axis (`LAYOUT_AXIS_Z_SIGN` was read for
Right+Top only) is not used by anything: the axis mate is made with the closest alignment, which keeps each gear
the way it was placed whichever way the layout axis points (`AXIS_MATE_ROUTE`'s probe: aligned or anti-aligned given
explicitly turned a gear over, closest did not), so the demonstration logs it as a fact and asserts only that the axis
lies on the shaft's line.

**Slanted axes (D4).** No plane combination of the probed calls gives a line in a general direction. The layout
holds a slanted axis as a fixed line: a 3D sketch `"<Shaft> Line"` holding one line from the shaft's point, 100 mm
along its direction, and the axis `"<Shaft> Axis"` made on that line (`InsertAxis2(True)` with one sketch line
selected, which the macro database records as verified from a 2D sketch line: `API-LEDGER.md`, `InsertAxis2`). No
global drives it, so any change to a slanted shaft's point or direction is structural (Build again…). The two calls
not used before are `ISketchManager.Insert3DSketch2` (a toggle, like `InsertSketch`) and `CreateLine2` with three
coordinates per end (`entries/sketches/02`, *unverified*); §7 says why they are not probed ahead. New op in
`gears/base.py`:

```python
@dataclass(frozen=True)
class LineAxis:
    """A reference axis on a one-line 3D sketch: the sketch "<name without ' Axis'> Line" holding a line from
    ``point`` to ``point + length·direction`` (mm, model space), the axis named ``name`` made on it. Defines ``id``.
    ``check()``: ``direction`` of unit length to 1e-9, ``length`` > 0."""
    id: str
    name: str
    point: Tuple[float, float, float]
    direction: Tuple[float, float, float]
    length: float = 100.0
```

`ShaftLayout` (layout.py) gains `direction: Vec3`, `z_side`, `z_global`, `z_plane` (the Front-offset plane's
pieces, `""` when unused, as `x_*` and `y_*` are), and `line: str` (the 3D sketch's name for a slanted shaft, `""`
otherwise). `sigma` keeps its meaning (+1 Z+, −1 Z−) and is 0 for any other axis; nothing may branch on it without
reading `direction` first (B audits every reader). `layout_features` adds the Front-offset planes and the line
sketches, so a reused layout part is checked for them live.

### 2.3 Where each gear goes, and how far it is turned

`geometry.layout` places every gear of every frame shaft (carriers stay W7's). Meshes are classified by
`geometry.mesh_geometry(a, b) -> MeshGeometry`:

```python
PARALLEL, BEVEL, CROSSED = "parallel", "bevel", "crossed"

@dataclass(frozen=True)
class MeshGeometry:
    a: str; b: str
    kind: str                 # PARALLEL (axes within 1e-9 rad of parallel), BEVEL (both bevel), CROSSED (both helical)
    sense: int                # c in  z_a·ω_a + c·z_b·ω_b = 0, speeds about each gear's own +Z (§2.4); ±1
    shaft_angle: float        # degrees between the two gears' own +Z; 0 or 180 for PARALLEL
    needed: float             # PARALLEL / CROSSED: the centre distance the teeth make; BEVEL: 0 (apexes together)
    placed: float             # PARALLEL: distance between the lines; CROSSED: along the common perpendicular;
                              # BEVEL: distance between the two apexes
    contact: Tuple[float, float, float]   # world point: PARALLEL the mid-overlap pitch point, BEVEL the heel pitch
                              # point on the common generatrix, CROSSED the pitch point on the common perpendicular
    psi_a: float; psi_b: float            # the contact's azimuth about each gear's own +Z, radians, in its base frame
    problem: str = ""         # a sentence when the pair cannot be laid out as this kind (§2.5)
```

**Parallel meshes in any family** use W3's formulas (`external_space`, `pinion_space`, `ring_space`, the helical twist
through `Placed.twist`) in the family's plus frame. A test rotates each committed fixture so every shaft is X+ (and
X−, Y+, a slant) and requires the same θ for every gear and the same checks.

**The phase across turned axes.** For BEVEL and CROSSED meshes the two gears share no plane, so the condition is
written in each gear's own frame. With `g` a gear's tooth-space angle at the contact height in its own frame
(`θ + twist(height)`; a straight bevel has no twist), `ψ` the contact's azimuth in its own base frame, and `k = −c·z_p/z_q`
the ratio of own-axis turns (§2.4):

    g_q = ψ_q + π/z_q + k · (g_p − ψ_p)        (mod 2π/z_q)

At θ_p = 0 with the contact on gear p's +X it gives exactly what the pair plans use: for a bevel pair at
`rot_y(Σ)`, `ψ_p = 0`, `ψ_q = π`, and `g_q ≡ π + π/z_q ≡ pair.mate_angle(z_q)` modulo a pitch; for a crossed pair
it gives `crossed.placement`'s `spin`. On a parallel external Z+ pair it is W3's `external_space` modulo one pitch.
Each of those three is a test. A loop that does not close is reported by `geometry.phases` as today.

**Bevel geometry.** Apex = `centre`. `mesh_geometry` requires the two apexes within `checks.CENTRE_TOLERANCE`
(0.005 mm) and the axes not parallel; the contact is the heel pitch point `apex + R·(cos δ_p · a_p + sin δ_p · w)`,
`w` the unit vector square to `a_p` in the plane of the two axes, towards `a_q`; Σ from the axes, δ_p from
`bevel.pitch_cone_angle(z_p, z_q, Σ)`.

**Crossed geometry.** The common perpendicular between the two lines gives the feet `F_p`, `F_q` and the unit `e`
from p to q. The contact is the pitch point on it, `F_p + r_p·e`. The crossing angle is checked signed: seen along
`e`, gear q's line must be turned `tilt = −(s_p β_p + s_q β_q)` from gear p's, modulo 180° (`crossed.placement`'s
tilt, `s` +1 right, −1 left). The contact's height along each axis must lie inside that gear's face.

### 2.4 Speeds across turned axes

`kinematics.solve` is rewritten in **own-axis speeds**: the unknown is each shaft's ω about its own Axis (the
workbook's convention, PLAN-WORKBOOK §3.5), and each mesh is the exact row `z_a·ω_a + c·z_b·ω_b = 0` with `c = ±1`
from `MeshGeometry.sense`:

- PARALLEL: `c = a_a·a_b` outside, `−a_a·a_b` inside a ring. This is W3's projected system multiplied through by the
  shafts' signs, so every speed of every parallel workbook is unchanged (pinned: the 12 : 1's 1500 / −375 / 125, and
  Risky's M2 values +0.7, +0.636364, −0.388889 as own-axis ratios).
- BEVEL: `c = +1` for every form. Rolling at the pitch point, `ω_p (a_p × r_p) = ω_q (a_q × r_q)`, and with both
  gears' own +Z the way §2.1 sets them the two tangents are opposite for a cone, a crown and an internal bevel alike
  (as δ_q passes 90° the pitch point stays on the same side of q's axis, so nothing flips).
- CROSSED: `c = s_p·s_q`, `s = sign(a·t)` with `t` the common tooth direction at the contact
  (`crossed.tooth_direction` in each gear's frame, carried to world). Normal velocities at the contact agree:
  `ω_p r_p (a_p·t) + ω_q r_q (a_q·t) = 0`, and `r = m_n z / (2 cos β)`, `|a·t| = cos β`.

`solve(spec, skip_gears=(), senses=None)`: `senses` maps a listed mesh, keyed by the ordered pair `(a, b)` as its
Meshes row lists it, to `c`. **Every caller passes it**: `checks.check` passes the senses of every mesh
`mesh_geometry` could lay out, and Export, the window and Update read `report.motion`, never `solve` directly.
`senses=None` means W3's behaviour exactly: every mesh between parallel shafts takes `c` from its two axes and sides,
and a mesh between non-parallel shafts is left out. A mesh with no sense, or whose gears are not placed, is left out,
which leaves its far shafts "not settled", the error that gear already has. `Motion.later` is set only for carriers.
The system stays in `fractions.Fraction`, one unknown per shaft, `c ∈ {−1, +1}`. **The carrier-ready form** (for
W7, whose §2.4 is written in W3's projected ω̃, which W6 removes): with a mesh's axes riding a shaft `x` that is
carried by a turning shaft `cr`, each `ω_x` in its row becomes `ω_x − (a_x·a_cr)·ω_cr`; for the frame `ω_cr = 0` and
the row is W6's.

**Seen from (D12).** `Motion.turns(shaft)` says the way round seen from the tip of the shaft's family plus direction
(`+X`, `+Y`, `+Z`, or the slant's plus direction, the one whose first non-zero component is positive);
`Motion.seen_from: Dict[str, str]` holds that word (`"+X"`, or for fixture B's S3, typed `-1, 1.732050807569, 0`,
`"(0.5, −0.866, 0)"`: components to three decimals, shortest form, U+2212 for minus), and the Results sheet's column
becomes *"Turns"* with cells *"anticlockwise, seen from +X"*.
`checks._worked_out_as` names the stages (*"Bevel and parallel train · 2 meshes · 6.000 : 1 · output at 90° to the
input"*; for parallel input and output, W3's *"output turns the same way / the other way"*, judged in the shared
family frame).

Torque keeps W3's `T·z_q/z_p·η` per mesh along the power path.

**The Results sheet for turned meshes** (review S5; `export.py`, B): a PARALLEL row is W3's (ratio, centres needed,
placed, off by, contact ratio). A BEVEL row gives the ratio, *shaft angle*, *cone distance* and *apex distance* (the
two apexes apart, 0 when right) and the contact ratio from `bevel.pair_contact_ratio`; *centres* are left blank. A
CROSSED row gives the ratio, *shaft angle*, *centres needed* and *placed* along the common perpendicular, *off by*,
and `crossed.normal_contact_ratio`, with the sheet's note line saying the efficiency typed (98 % by default) is the
workbook's, and a crossed pair's real efficiency is far lower. `geometry.extent` takes each turned gear's bounding
cylinder (§2.5) into the box size in 3D.

`motion.mesh_links(meshes, teeth, sense)` (`sense` keyed by the ordered pair `(a, b)`, as `solve`'s; W7's planets
call it too) gives `MeshLink(a, b, k = −c·z_a/z_b, pitch = 360/z_b)` for any kind;
`k == ω_b/ω_a` with `solve`'s speeds (review M2 of W5, unchanged in meaning).

### 2.5 Checks

`checks.check` runs for every gearbox whose shafts are on the frame. Per mesh, by kind:

- **PARALLEL**: W3's `_check_mesh` in the family frame (module, pressure angle, rings, helix angle and hands, centres
  to 0.005 mm with the move and shift fixes, faces overlapping, herringbone middles, the shifted pinion in a ring of
  `d3f4dcf`).
- **BEVEL**: both bevel (else W3's kind sentence); same module and pressure angle; axes not parallel (*"bevel gears on
  parallel shafts"*); apexes together to 0.005 mm; each gear's own `bevel.validate` with the mate teeth and Σ worked
  out (§2.5.1), so Σ outside 10–170°, b ≥ R/2, the crown band and the rest come out at the gear's cells as the strip
  says them. The faces always overlap (both heels sit at the one cone distance R). **No fix** is offered (D10): the
  sentence names the At that would put the apex right when the axes meet, and the distance between the lines when
  they do not.
- **CROSSED**: both helical, external, unshifted (`crossed.validate`'s rules), same normal module and normal pressure
  angle; the signed crossing angle against the hands (§2.3); the centre distance along the common perpendicular
  against `(m_n/2)(z_p/cos β_p + z_q/cos β_q)` to 0.005 mm, no fix; the contact inside both faces.
- **Kinds that do not mesh across an angle**: spur, herringbone or a ring on non-parallel shafts is an error naming
  what does.

**Clearance between gears on non-parallel shafts (D8, review M5).** Each gear is bounded by a **true solid
cylinder** about its own axis: radius its outside radius (a ring's rim; a bevel's largest radial extent in
`bevel.blank_points`), axial span its face, or a bevel's blank from its nearest to its farthest point along the axis
(`bevel.blank_points`, from the apex). The distance between two such cylinders is computed exactly, not as a capsule
(a segment-to-segment distance less both radii reaches a radius past each end, and warned falsely on both fixtures):
`geometry.cylinder_gap(a, b) -> float`, the least distance between the two solids, by the closed forms for the side
against the side, each end disc against the other cylinder, and the rims, with a test against dense sampling. Two
gears on non-parallel shafts that do not mesh and come within `CLASH_GAP × module` get a **warning**, never an error
(the bound over-reaches a toothed blank; the build's interference check is the judge). **A shaft is the span of its
own gears**, not an infinite line: the segment of its axis from the nearest to the farthest point of its gears'
cylinders. A shaft span passing within a gear's cylinder, on a shaft not parallel to the gear's, gets the same
warning; a bevel gear's partner shaft is exempt from it (the partner's axis runs through every bevel blank's apex
region by design). This replaces W3's "passes over another shaft's axis" only for non-parallel pairs; parallel pairs
keep W3's rule.

#### 2.5.1 A bevel gear's mate teeth and shaft angle

`geometry.bevel_cuts(spec) -> Dict[str, BevelCut]`, pure and from the read alone (it must run before `plan_parts`):

```python
@dataclass(frozen=True)
class BevelCut:
    mate_teeth: int           # the partner's teeth
    shaft_angle: float        # degrees, from the two shafts' Axis directions
    partners: Tuple[str, ...] # every bevel gear it is listed with
    problem: str = ""         # a sentence: no mesh, two mates of different teeth, two shaft angles
```

`build.plan_parts` and `build.check_gear` give a bevel row's `GearSpec` `mate_teeth=str(cut.mate_teeth)` and
`shaft_angle=equations.literal(round(cut.shaft_angle, 9))` (`model.Gear.gear_spec(box, **overrides)` gains keyword
overrides); a cut with a problem is an error at the gear's cell and the gear is not planned. A cardinal pair is
always exactly 90°. Identical bevel gears still share one file (W1's judgement call); two cut for different Σ but
the same stem get W2's existing *"would both be …SLDPRT"* error.

### 2.6 Mates in a turning train with turned axes

**Anchors and locks** are W5's (`motion.motion_plan` steps 1–5), with the along mate measured from the base plane
square to the shaft (D5): `MatePlan` gains `plane: str = "front"` (`"front"`, `"top"`, `"right"`): Right for X±, Top
for Y±, Front for Z±, and for a slant the base plane whose normal makes the smallest angle with the axis (a tie,
`|a·n|` equal to 1e-9, goes Right, then Top, then Front). `z_front`
keeps its name and becomes the origin's signed distance from that plane (`frames[anchor].at[i]`, `i` the plane's
normal's index). The mate is `"point"` to `"layout:plane1|2|3"` at 0 and `"point distance"` otherwise, linked to the
global `motion.face_global(gear, plane, bevel)`: `"G1 Face X"`, `"G1 Face Y"`, `"G4 Face Z"`, and for a bevel anchor,
whose origin is its apex, `"G2 Apex Z"` (D5b). The W5 rule carries over to every plane: an anchor's origin reaching,
leaving or crossing its plane is structural, and the sentence names the edit and the plane.

**Gear mates** are made for BEVEL and CROSSED meshes exactly as for parallel ones (`Mate(kind="gear")` between the two
`Gear Axis`, ratio `(z_a, z_b)`, Flip `findings.GEAR_MATE_FLIP` first, renamed `"G1 meshes G2"`, under
`CommandInProgress`), read back straight after, and made again with the other Flip when wrong (W5's ring rulings).

**The riskiest point: what "right" means between non-parallel axes.** W5's read-back,
`(Reverse == the two entity directions point the same way) == internal` (`findings.GEAR_MATE_SENSE_READ_BACK`), has no
meaning when the directions are at 90°, and `swcom.Session.gear_mate_sense` refuses any pair whose cosine is under
0.99. W6 reads it as a statement about each entity's own direction:

> **H.** A gear mate's `Reverse` is True exactly when it turns its two gears the same way about its two entities' own
> directions.

With `d_a, d_b` the entity directions (`EntityParams[3:6]`), `g_a, g_b` the two gears' own +Z as placed (column 3 of
each frame), `τ_i = sign(d_i·g_i)` (refused, as a mate not holding the planned axes, when `|d_i·g_i| < 0.99`), and `k`
the mesh's own-axis ratio (§2.4), the mate turns right exactly when

    Reverse == (sign(k) · τ_a · τ_b > 0)

**On parallel axes this is W5's rule exactly**, so nothing W5 built or measured is at risk: with `g_b = ε g_a`, W5's
"parallel" is `τ_aτ_bε > 0`; outside a ring `sign k = −ε`, so the right side is *not parallel* and the mate is right
when `Reverse != parallel`, i.e. `(Reverse == parallel) == False`; inside a ring `sign k = ε` and it is right when
`Reverse == parallel`. W5's cross-check (the entities point the same way exactly when the shafts do) becomes the
stronger per-entity check above, which every W5 case passes since each entity is its gear's axis. The review adds
that W5's data already prefer H's reading on parallel axes: an external pair on opposite shafts was right with the
stored Reverse True, where a Reverse measured against SolidWorks' own closest alignment (the sign of `d_a·d_b`) would
have turned it wrong.

**On non-parallel axes H is a hypothesis.** It is the natural reading of a mate that couples two turns about two
lines, and the 52 + 13 parallel cases fit it, but no gear mate between non-parallel axes has ever been made by this
app or recorded in the macro database. If H is wrong, a turned gear mate the app keeps as right turns the train the
wrong way, silently as far as the app is concerned. So:

- **The probe first (D6, as the orchestrator ruled).** Probe tier 9, `turned_gear_mate_sense` (§7.2), runs on
  SolidWorks 2026 now, on cylinders, while the packages are written against the fake: meeting and skew axes at
  30°–150° between the gears' own axes, both hands of crossing, every facing, both Flips, and parallel and
  anti-parallel controls that must reproduce W5's rule. Its results give two findings, committed and reviewed before
  E runs: `TURNED_GEAR_MATE_SENSE_READ_BACK` (the rule, `"entity senses"` when H holds) and
  `TURNED_GEAR_MATE_SENSE_ANGLES` (the least and greatest angle between the own axes it was shown on). No run of the
  app ever uses an uncommitted finding.
- **The gate.** While `TURNED_GEAR_MATE_SENSE_READ_BACK` is not `"entity senses"`, or a turned mesh's angle between
  the own axes lies outside `TURNED_GEAR_MATE_SENSE_ANGLES`, a workbook with that mesh is **refused before Build**
  with a full sentence (§2.9), as W5 refused a ring train it could not read (`swbuild._sense_gate`); there is no
  static fallback (W5 answer 1, and the ring precedent; D16). The refusal is planning's,
  `motion.turned_refusal(report) -> str`, read by `assess.Assessment.lay_out_refusal` after its W4 reasons, so the
  footer says it before Build and Build parts still makes the parts; `swbuild`'s sense gate refuses a turned gear
  mate as the second guard.
- **Real teeth confirm it.** The full build (r1, r5) and its Updates (r3, r6) give every turned mesh the both-Flips
  control, and **after each control drive the interference check** (review M2): driven 30° off the built phase, the
  Flip the drive calls right must be clear and the other must clash (`WRONG_GEAR_MATE_SENSE_CLASHES` held on parallel
  axes). This is SolidWorks' own reading and does not come from the mesh sense `k`, which the read-back's verdict,
  the drive's expected turn and the speeds all share: a sign slip in `mesh_geometry` would pass the other controls
  and fails this one. A clash on the Flip the app kept STOPs the run (the finding or `k` is wrong).
- Every other assumption of this mate is tested first by the probe on cylinders and then by the build on teeth:
  that AddMate5 makes a gear mate between perpendicular and skew axes at all (in the build, a refusal stops it, W5
  answer 1), that no gear moves when it is made (frames before and after), and that the remake at a new ratio (`GEAR_MATE_RATIO_ROUTE = "remake"`) reads back the
  same way on a turned mate (r3, r6).

**Plumbing.** The pure rule is one function in `swcom` (it returns the reading; `swcom` cannot import `swbuild`),
used by `Session.gear_mate_sense` and by the fake. It **matches each entity to the gear whose axis it lies along**
(`|d·g| ≥ 0.99`), never by `MateEntity` order (review S1: W5 never needed the order, a dot product being symmetric);
an entity along neither gear, or both entities along one, is the refusal; at the finding's least angle (30°, cos
0.866) an entity along one gear cannot pass 0.99 against the other, so the matching is never ambiguous inside the
gate. On parallel axes either pairing gives the same `τ_aτ_b`, so nothing W5 built
changes:

```python
def sense_reading(reverse: bool, directions: Sequence[Vec3], axes: Sequence[Vec3], same_sense: bool) -> Tuple[bool, Tuple[int, int]]
    """(right, (τa, τb)) by the committed rule (H); ``directions`` in any order, matched to ``axes`` by alignment;
    raises SolidWorksError with a sentence when the entities are not along the two gears' axes."""

Session.gear_mate_sense(handle: str, same_sense: bool, axes: Tuple[Vec3, Vec3]) -> Tuple[bool, Tuple[int, int]]
```

`same_sense` is `k > 0`. The gate: axes parallel (|g_a·g_b| > 0.99) need W5's `SENSE_FINDINGS`; any other pair also
needs `TURNED_GEAR_MATE_SENSE_READ_BACK == "entity senses"` and its angle inside `TURNED_GEAR_MATE_SENSE_ANGLES`. In `swbuild`, `_planned_sigma` becomes `_planned_axes`
(each handle's last `Place` rotation's third column), `_sense_read` takes axes and `same_sense`, `_internal_meshes`
becomes `_mesh_senses(motion) -> Dict[mate name, bool]` from `MeshLink.k`, and the two Update sense loops read axes
from the placements' rotations. `build(..., internal=...)` and `build_gearbox(..., internal=...)` take `senses:
Optional[Mapping[str, bool]]` instead (gear mate name → same sense); `GearboxPlan.ring_meshes` gives way to
`mate_senses`, and `build_kwargs()` passes `"senses"` for a turning plan.

### 2.7 Update's classification

From the record against the new read (`update.classify`, `_turning`), in W5's order; what is new:

| Edit | Kind | Why |
|---|---|---|
| A cardinal shaft's coordinate square to its axis, same side of its base plane | **move** | the layout's global (`"S1 Z"` for an X shaft), then every gear of the train put back (W5 answer 2) |
| A shaft point's coordinate along its own axis; an At on any shaft | **move** | the anchor's Face/Apex global, or a follower's lock re-taking its offset (`LOCK_RETAKES_AN_OFFSET`) |
| A bevel apex moved with both gears' At (and the shafts) so the apexes stay together | **move** | as the two rows above; the checks refuse an Update whose apexes part |
| Teeth, module, face, bore… of any part, bevel included, the form unchanged | **value** | `update_variables`; a bevel's partner's tooth change reaches it as `"Mate Teeth"` |
| A tooth change that alters a gear mate's ratio, turned or not | **value** | the remake, read back by H (or W5's rule on parallel axes); gated as §2.6 |
| A crossed mesh's sense changing with a move (review M4: a 90° crossed shaft moved to the other side of its partner, same side of its base plane: the checks pass both sides, and `c = s_p·s_q` flips) | **value: a remake by Update** | as W5 remakes a gear mate at a new ratio: deleted, made again, read back against the new `k`, every gear put. Why not structural: the edit is a plain move, which is an Update; the remake route is the one W5 proved in an Update's shape on both versions (`GEAR_MATE_RATIO_ROUTE`, `IDLER_UPDATE_HOLDS`); a new revision for it would be the only move in W6 that needs one. Parallel and bevel senses cannot change without a structural edit (`c = ±a·a`, or +1). |
| A cardinal coordinate crossing, reaching or leaving its base plane | structural | W4 (`OFFSET_GLOBAL_CROSSES_ZERO`), now for the Front-offset Z too |
| An anchor's origin reaching, leaving or crossing its measuring plane | structural | W5 answer 3, for Right and Top as for Front |
| Any change of a shaft's direction (X+ → X−, X → Z, a word ↔ a vector, a slant's vector) | structural | the layout axis and the mates keep the direction they were made with |
| Any change of a slanted shaft's point | structural | its axis is a fixed line (D4) |
| A slanted line axis found moved in SolidWorks (its point or direction read back by `GetRefAxisParams` in Update's check phase, and when a layout part is reused, against the record to 1e-6; review S7) | refused | *"S3's axis in the layout part is not where the record has it (it was moved in SolidWorks), so Update SolidWorks cannot act on it; Build again… makes a new revision."*; a reused layout with a moved line is not reused |
| A bevel gear's form changing (cone ↔ crown ↔ internal) with its teeth | structural | the part's ops differ; `swbuild.structural_change` does not see it, so `update._part` checks `bevel.form_of` itself (D14) |
| A gear, shaft or mesh added or removed; a gear moved to another shaft; Role to or from `fixed` | structural | W4/W5, unchanged |

`MotionUpdate` keeps its shape. `meshes` come from `mesh_links` with the senses of the new read; `recorded_meshes`
come from the record's own senses (`MateEntry.sense`, §2.8), so `train_check` judges the user's turn against the mate
as built. A mesh whose sense differs is listed in `UpdatePlan.resensed: Tuple[str, ...]` (mate names, for the
sentence) and its remake goes into `MotionUpdate.ratios` with its tooth counts, new or not; the worker reads the
remade mate back against the new `k`, and `finish_update` writes the new sense with the new ratio. The check phase's
`sense_found_wrong` (a mate found turning wrong in SolidWorks) is never said for a planned remake. Update's check
phase also reads every slanted line axis back (`Session.axis_line(handle, name) -> (point, direction)`, A, a read of
`GetRefAxisParams` that marks nothing).

### 2.8 The record: schema 4 (D13)

`LINK_SCHEMA_VERSION = 4`, always (an all-Z gearbox too): a W5 build refuses a v4 record and leaves it byte-identical
(D11's mechanism), so it never drops the new fields by rewriting the file. A v1–v3 record reads as v4; a record of a
newer schema is refused untouched (the numbers after 4 are W7's and W8's to set).

- `ShaftEntry` mirrors `ShaftLayout` field for field: adds `direction: List[float]` (a v3 entry reads as `[0, 0,
  sigma]`), `z_side`, `z_global`, `z_plane` (`""`), `line` (`""`), and `axis: str` (the canonical word or `"dx, dy,
  dz"`, for sentences).
- `MateEntry` mirrors `MatePlan`: adds `plane: str = "front"` (a v3 entry reads as `"front"`) and `sense: int = 0`
  (review M4: a MESH entry's `c` as made or last remade, +1 or −1; 0 for every other kind, and for a v3 mesh entry,
  which `update._turning` then takes from the read, as W5 did, since every v3 mesh is parallel and its sense cannot
  have changed without a structural edit). The parse refuses a plane outside the three words, and a sense outside
  {−1, 0, +1} or 0 on a v4 mesh, with a `StoreError` sentence, and `update._bad_mates` likewise. `MatePlan` gains the
  same `sense` field (B sets it from `MeshGeometry.sense`). W7 may use it for its carrier-frame sense.
- Nothing else changes: frames are already 9 numbers and an origin; a turned gear mate is a `"mesh"` entry.

### 2.9 Sentences (exact; `{…}` from fields)

Checks (B, `checks.py`; each prefixed with its cell as today):

- *"{G1} and {G2} are bevel gears whose cone tips are {0.4} mm apart; they mesh only with their tips together. {G2}'s
  At would be {52.4} to put its tip on {G1}'s."* — the gear named is always the Meshes row's Gear B (review S10) — or,
  when the axes do not meet: *"… together, and their shafts do not meet: they pass {3.2} mm apart."*
- *"{G1} and {G2} are bevel gears on parallel shafts; bevel gears mesh across shafts at an angle."*
- *"{G3} and {G5} are {spur} gears on shafts at {90}°; across an angle only bevel gears (on shafts that meet) and
  helical gears (on crossed shafts) mesh."* (a ring: *"{G6} is a ring, and a ring meshes only on a parallel shaft."*)
- *"{G2} is a bevel gear listed with {G1} ({20} teeth) and {G5} ({18} teeth); a bevel gear is cut for one mate's tooth
  count."* · *"… listed across shafts at {90}° and {60}°; a bevel gear is cut for one shaft angle."* · *"{G7} is a
  bevel gear that meshes nothing; its shape depends on the gear it meshes with, so list its mesh on the Meshes
  sheet."*
- *"{G5} and {G6} are both right-handed at {30}° and {30}°, so their shafts must cross at {60}°; they cross at
  {90}°."* · *"… so, seen along the line from {G5} to {G6}, {G6}'s shaft must be turned {−60}° from {G5}'s; it is
  turned {60}°."* The signed angle is a right-hand turn about `e`, the unit vector from G5's axis to G6's along the
  common perpendicular, taking G5's axis direction to G6's, reduced to (−90°, 90°].
- *"{G5} and {G6} are helical gears on shafts that meet; across an angle helical gears mesh only on crossed shafts
  that pass apart, and gears on shafts that meet are bevel gears."* (the lines within 1e-6 mm: `e` is undefined)
- *"{G5} and {G6} are {84.9} mm apart where their shafts pass closest; their teeth make {84.853} (+0.047 mm). Check
  the place of {S2} (Shafts row {3}); a shaft at an angle is best placed by formula."*
- *"{G5}'s face does not reach where {G6} touches it: that point is {9.5} mm along {S3} from {G5}'s middle, and its
  face is {16} mm wide."*
- *"{G5} and {G6} are crossed helical gears with profile shift; crossed gears are built without it: set both shifts
  to 0."* · herringbone: *"…are herringbone gears on crossed shafts; only helical gears mesh on crossed shafts."*
- Warning: *"{G3} and {G1} may touch: on shafts at {90}°, their blanks come within {1.2} mm of each other; the build's
  interference check says for certain."*

On a turned shaft a herringbone's `Hand` names the half nearest its own front face (W3's rule, unchanged; the
helical hand check's *"…since one is turned over"* becomes *"…since one faces the other way along its axis"*).

The expected Checks panel of each fixture is pinned in §5.

Update structural (B, `update.py`; folded by `_reason` as W4's):

- *"{S1}'s axis is now {X-} where it was built {X+}: the layout's axis and the mates on it keep the direction they
  were made with, so the gearbox needs building again."*
- *"{S3}'s axis slants, and the layout holds a slanted axis as a fixed line: its {point moved (Z 8 → 10)} / {direction
  changed}, so the gearbox needs building again."*
- *"{G1}'s At (0 → 2) moves its cone tip off the Right plane (x 0 → 2): the mate {G1 along S1} holds it on that plane
  and cannot take a distance, so the gearbox needs building again."* (W5's three Front-plane sentences, with the
  plane and coordinate named, and *cone tip* for a bevel.)
- *"{G2}'s teeth (40 → 41) make it {a crown gear} where it was built {a cone}, which its values cannot carry; build it
  again as a new part."*

Planning and worker (A raises; C shows each whole, never embedded):

- `motion.turned_refusal` (the footer, before Build; Build parts still offered): *"{G1} and {G2} mesh across shafts
  at {90}°, and which way a gear mate turns gears on shafts at an angle is not settled by the probes for this version
  (findings.TURNED_GEAR_MATE_SENSE_READ_BACK), so the gearbox is not built; Build parts makes its parts."* · *"{G3}
  and {G4} mesh across shafts at {165}°, outside the {30}°–{150}° the probes showed a gear mate turning right at
  (findings.TURNED_GEAR_MATE_SENSE_ANGLES), so the gearbox is not built; Build parts makes its parts."*
- After an Update that remade a mesh for its sense (C, `gearbox_update_status`): *"remade the gear mate {G1 meshes
  G2}, since {S2} now meets {S1} on its other side and {G2} turns the other way"*.
- The sense gate (second guard): *"The gear mate {G1 meshes G2} joins gears on shafts at an angle, and which way such
  a gear mate turns cannot be told on SolidWorks yet (findings.TURNED_GEAR_MATE_SENSE_READ_BACK is None), so nothing
  is made or changed."*
- The read-back's refusal: *"SolidWorks reads an axis of the gear mate {G1 meshes G2} as pointing {(0.0, 0.0, 1.0)},
  which is not along {G1}'s axis {(1, 0, 0)}, so the mate does not hold the axes the gears were placed on, and nothing
  is guessed."*

Speeds (C, `ui_text.workbook_speed_lines`): *"S1    1500.0 rpm anticlockwise seen from +X · 10.00 N·m"*, and for
fixture B's slanted S3 (−333.33 rpm about its Axis as typed, +333.33 about its plus direction) *"S3    333.3 rpm
anticlockwise seen from (0.5, −0.866, 0) · 14.41 N·m"*; the panel's readout is W3's *"seen from +Z"* when every shaft
is in the Z family, else *"seen from each shaft's + end"*.

### 2.10 The window

No new control (D15). What changes is read-only: the Speeds lines and readout above; the header's worked-out text;
and the end view (`preview.layout_gearbox`, headless and tested), which today draws every gear seen from +Z: a gear
on a non-Z shaft is drawn as its section seen side-on (`preview.bevel_section` for a bevel, the face rectangle for a
cylinder), projected onto the XY plane at its place, with its shaft drawn as a line, so a right-angle box reads as
one at a glance. Boards: `WorkbookRightAngle` (fixture A built, footer with the drag instruction) and
`WorkbookCrossed` (fixture B read, the end view with the crossed and slanted stages); `UI-DESIGN.md` §9 gains both and
the new sentences.

---

## 3. Decisions

Each is taken at the reading marked **default**; they go to the user afterwards as readings to overrule.

| # | Question | Options | Default and why |
|---|---|---|---|
| D1 | Which way does a gear face on its shaft? | (a) its own +Z along the Axis, always; (b) inferred from its partner | **(a).** It is what W4 does for Z−, it is one rule for every kind, and it makes Σ the angle between Axis cells; (b) is ambiguous at 90° (either side meshes). |
| D2 | A bevel gear's At | (a) to the apex; (b) to mid-face like the others | **(a).** PLAN-WORKBOOK §1 and the schema's help already say it; the apex is the part's origin and the point two bevels share, so the apex check is one subtraction and a tooth change moves nothing. |
| D3 | Cardinal axes in the layout | (a) two offset planes from the base planes square to the axis, globals as W4; (b) a 3D sketch for every turned axis | **(a).** Probed calls in new combinations; moves stay Updates. |
| D4 | Slanted axes | (a) built as a fixed 3D-sketch line, any change structural; (b) refused at Build in W6 with a sentence (checked and solved only); (c) angled planes driven by globals | **(a).** PLAN-WORKBOOK puts slanted axes in W6 (§1, §4.2); (a) needs two unverified calls and no plane maths; (c) needs several. If the full build shows the 3D sketch failing, the fallback is (b) with the sentence *"{S3}'s axis slants: the app checks it and works out its speeds, but builds axes along X, Y or Z only so far."* — and that change goes to the user. |
| D5 | An anchor's place along a turned shaft | (a) from the base plane square to it (nearest for a slant); (b) a datum plane per shaft | **(a).** The user declined a datum plane in W5 (answer 3); (a) adds none. |
| D5b | The global's name | (a) `"<Gear> Face X/Y/Z"`, and `"<Gear> Apex Z"` for a bevel; (b) `"Face Z"` everywhere | **(a)**: it names the coordinate the person sees change in the Equations. |
| D6 | How the turned read-back H is established | (a) the first full build tests it with the finding set in memory; (b) a cylinder probe first | **(b), ruled by the orchestrator after the review (M3).** (a) bent "findings only from committed `findings.py`"; the probe (§7.2) runs on 2026 while the packages are written, so it costs no time, and the full build confirms its finding with real teeth and the interference control (M2). |
| D7 | Kinematics | (a) own-axis unknowns with a per-mesh sign from geometry; (b) keep W3's projection and special-case turned meshes | **(a).** One system for every kind; parallel results provably unchanged, and pinned. |
| D8 | Clearance across non-parallel shafts | (a) true bounding cylinders and shaft spans, a warning; (b) the same, an error; (c) not checked before Build | **(a)** (review M5: true cylinders, not capsules; a shaft as the span of its gears; a bevel's partner shaft exempt). The cylinders over-reach a toothed blank, so an error would refuse good gearboxes; the build's interference check is exact. |
| D9 | A bevel gear's mate and Σ | (a) from its Meshes rows and axes, one mate per gear, an error otherwise; (b) new columns | **(a).** PLAN-WORKBOOK §1: *"Not columns: … a bevel gear's shaft_angle and mate_teeth (from its partner and the two axes)."* |
| D10 | Fixes for an apex or crossed centre off | (a) none, the sentence gives the number; (b) a new At fix kind | **(a)**: a fix kind touches Export and the window for a case a formula in the workbook serves better. |
| D11 | Crossed scope | helical only, external, unshifted, either hands as `crossed.validate` | as `crossed.validate` and `pair.crossed_assembly_plan` already rule. |
| D12 | "Seen from" | (a) each shaft's family + end; (b) the input's axis | **(a)**: a speed's sign is about its own axis, and the + end of X, Y or Z is what a person can find. |
| D13 | Schema 4 for every record | (a) always; (b) only when a new field is used | **(a)**: one rule, as D11 of W5. |
| D14 | A bevel's form change | structural, checked in `update._part` | the ops differ; `structural_change` (the strip's) is left alone. |
| D15 | The window | no new control | as W5. |
| D16 | Turned meshes before the finding, or outside its angles | refused before Build with a full sentence, Build parts still offered | **Ruled by the orchestrator** (review S2): no static fallback, as the user's W5 answer 1 and the ring precedent (`_sense_gate`) have it. |
| D17 | A crossed mesh's sense changing with a move (M4) | (a) a remake by Update; (b) structural | **(a)**: a move is an Update, and the remake is W5's proven route (§2.7). |
| D18 | The turned finding's coverage (M1) | (a) limited to the own-axis angles the probe showed, others refused; (b) every angle | **(a)**, and fixture B's bevel stage is re-laid at 120° so real teeth confirm it past 90° too. |

**Needs the user, and cannot proceed without:** nothing. The readings most worth putting to the user afterwards: D1
(one facing per shaft: two bevels on one shaft cannot face apart; review S3), D4 (if the 3D sketch fails, slanted axes
are refused in W6 and no later phase owns them), and D16 (refused, not static, before the finding).

---

## 4. Work packages

### 4.1 The interface commit (I, one agent, first)

Starts on the commit of this revised plan. Writes the shapes of §4.3 and pins them, with the ownership table below, in
`docs/notes-workbook/W6-INTERFACES.md`. Written in full with tests at I, because A and B both rest on them:
`geometry.axis_vector`, `base_frame`, `family`; `layout.frame` on `base_frame`; `motion.face_global`, `mesh_links`;
`swcom.sense_reading`, with the parametrised proof that it equals W5's rule on every parallel case of
`findings.GEAR_MATE_FLIP_NEEDED_*` and `GEAR_MATE_FLIP_NEEDED_MORE_*`, in either entity order. Everything else is a
signature and a docstring. I also fixes the one call outside every package that its signature change breaks:
`probe/workbook_assembly_check.py`'s `gear_mate_sense("ring", True)` (section m8, about line 2231), mechanically, to
the new arguments (review S9); E owns the file from then on.

**Done:** suite green apart from stubs nobody calls; `sense_reading` equals W5's rule on every recorded parallel case;
`frame` gives W4's frames bit for bit on the three Windows fixtures; a v3 record reads as v4 and a record of a newer
schema is refused untouched; `copy_built`'s steps (§6.2) pinned in W6-INTERFACES for E and for W7 to reuse.

### 4.2 The packages (in parallel after I, against the fake; P alongside on SolidWorks 2026)

| Package | May edit | Does |
|---|---|---|
| **P — probe tier 9** (starts at once, before I) | `src/gear_generator/probe/p9_turned.py` (new) and its registry entry, `probe/decide.py`, `findings.py`, `tests/test_findings.py`, `tests/test_probe_turned.py` (new), `probe/results/**` | §7.2 on SolidWorks 2026; commits the two findings with `decide.py` entries and pins; reviewed before E. |
| **A — SolidWorks** | `swcom.py`, `swbuild.py`, `tests/test_swbuild.py` (the fake), `tests/test_swcom.py`, `tests/test_swbuild_train.py` (add only) | `line_axis` (`Insert3DSketch2(True)`, `CreateLine2` with z, `Insert3DSketch2` to close, the line selected `"Line1@<Shaft> Line"` as `EXTSKETCHSEGMENT`, `InsertAxis2(True)`, the axis renamed and read back); `axis_line` (a read of `GetRefAxisParams`) for the slant's read-back in Update's check phase and on reuse; `gear_mate_sense` on `sense_reading`; the gate (§2.6, angles included); `_planned_axes`, `_mesh_senses` and the three sigma sites; remakes listed for a sense change read back against the new `k`; the fake: components on any frame, layout axes from X/Y/Z globals and line axes, rebuild carrying anchors on turned axes and along Right/Top planes, `gear_mate_sense` by the rule with an override `turned_reverse={name: bool}` to model it failing, entity order shuffled by an override, `line_axis`, `axis_line` with an override for a moved line. |
| **B — planning** | `workbook/{geometry,kinematics,checks,fixes,layout,motion,gearbox,update,build,model,schema,export,assess}.py`, `tests/test_workbook_{geometry,checks,layout,motion,gearbox,update,model,export,demo_fixtures}.py` (kinematics and fixes are tested in `test_workbook_checks.py` today), new `tests/test_workbook_turned.py`, and new `tests/test_workbook_parts.py` for the bevel rows of `plan_parts` (its W2 tests sit in D's `test_workbook_build.py`, which B leaves alone) | §2.1–§2.7: placement, phases, kinematics, checks and sentences, `cylinder_gap` and shaft spans, `bevel_cuts` into the parts, the layout plan with Front planes and `LineAxis`, the along plane and global, `MatePlan.sense`, `mate_senses`, `turned_refusal` into `lay_out_refusal`, classification (the sense-change remake, `resensed`), the Results rows, `finish_build`/`finish_update` for the new fields; the move fix in any parallel family (offered in the family's plane, written to that family's two coordinate cells); the two fixtures' Checks panels pinned as §5 gives them. |
| **C — record and words** | `store.py`, `ui_text.py`, `tests/test_store.py`, `tests/test_ui_text.py` | schema 4 complete (refusals for a bad `plane`, a bad `sense`, a `direction` that is not three finite numbers of unit length); the Speeds lines and readout; the refusal and remade-for-sense sentences; every §2.9 sentence C shows, filled from fields in a test. |
| **D — window, boards, docs** (after A–C) | `workbook_gui.py`, `preview.py`, `tests/test_workbook_{build,window}.py`, `tests/test_preview.py`, `design/**`, `docs/**`, `README.md` | the end view (§2.10); the two boards; UI-DESIGN §9; PLAN-WORKBOOK dated notes (*Readings chosen (W6)*: D1–D18, and §4.2's paragraph on turned axes); HANDOFF. |
| **E — demonstration** (after D and P's review) | `probe/workbook_assembly_check.py`, `probe/workbook_window_check.py`, `probe/results/**` | §6, on the committed findings only. |
| nobody | `gears/*.py` but `base.py` (I only), `gui.py` | |

The turning round trip on the fake (plan → build → finish → classify → update → finish), for fixtures A and B, is B's
second pass once A lands, as in W5.

### 4.3 Shapes the packages share (pinned at I; a change is a stop-and-ask)

```python
# gears/base.py
@dataclass(frozen=True)
class LineAxis: id: str; name: str; point: Vec3; direction: Vec3; length: float = 100.0      # §2.2

# workbook/geometry.py
def axis_vector(text: str) -> Vec3                    # unit; a near-cardinal vector snaps to the word's
def family(direction: Vec3) -> Tuple[Vec3, int]       # (plus direction, ±1)
def base_frame(direction: Vec3) -> Tuple[float, ...]  # 9 by rows, [u0 | a×u0 | a]
Placed += axis: Vec3 = (0, 0, 1); centre: Vec3 = (0, 0, 0); family: Vec3 = (0, 0, 1); bevel: bool = False; origin (property)
PARALLEL, BEVEL, CROSSED = "parallel", "bevel", "crossed"
MeshGeometry(a, b, kind, sense, shaft_angle, needed, placed, contact, psi_a, psi_b, problem="")   # §2.3
BevelCut(mate_teeth, shaft_angle, partners, problem="")                                          # §2.5.1
def mesh_geometry(a: Placed, b: Placed) -> MeshGeometry
def bevel_cuts(spec: GearboxSpec) -> Dict[str, BevelCut]
def cylinder_gap(a: Placed, b: Placed) -> float

# workbook/kinematics.py
def solve(spec, skip_gears=(), senses: Optional[Mapping[Tuple[str, str], int]] = None) -> Motion   # §2.4
Motion += seen_from: Dict[str, str]

# workbook/checks.py
Report += meshes: Dict[Tuple[str, str], MeshGeometry]

# workbook/layout.py
ShaftLayout += direction: Vec3; z_side: str; z_global: str; z_plane: str; line: str     # sigma 0 off the Z family
def frame(placed: Placed, theta: float) -> Frame                                       # B·rot_z(θ), at = origin

# workbook/motion.py
MatePlan += plane: str = "front"; sense: int = 0
def face_global(gear: str, plane: str = "front", bevel: bool = False) -> str   # "G1 Face X", "G2 Apex Z"
def mesh_links(meshes, teeth, sense: Mapping[Tuple[str, str], int]) -> Tuple[MeshLink, ...]   # k = −c·za/zb
def turned_refusal(report: Report) -> str                                      # "" or the §2.9 sentence

# workbook/gearbox.py, update.py
GearboxPlan += mate_senses: Mapping[str, bool] = {}       # gear mate name -> k > 0; replaces ring_meshes in build_kwargs
UpdatePlan += resensed: Tuple[str, ...] = ()

# swcom.py
def sense_reading(reverse, directions, axes, same_sense) -> Tuple[bool, Tuple[int, int]]   # §2.6, any entity order
Session.gear_mate_sense(handle, same_sense: bool, axes: Tuple[Vec3, Vec3]) -> Tuple[bool, Tuple[int, int]]
Session.line_axis(handle, name, point, direction, length) -> str
Session.axis_line(handle, name) -> Tuple[Vec3, Vec3]

# swbuild.py
build(sw, plan, exists, kind=None, *, gears=None, senses: Optional[Mapping[str, bool]] = None)
build_gearbox(..., senses: Optional[Mapping[str, bool]] = None)      # `internal` is gone
protocol += gear_mate_sense (new form), line_axis, axis_line

# store.py (schema 4)
ShaftEntry += direction: List[float]; z_side; z_global; z_plane; line; axis: str
MateEntry  += plane: str = "front"; sense: int = 0
```

And by convention: a gear's axis is its frame's third column (`rotation[2], rotation[5], rotation[8]`) in every
`Place` and `Placement`; along mates name `"layout:plane1|2|3"`, axis mates `"layout:<Shaft> Axis"`; the `sense`
maps are keyed by the Meshes row's ordered pair `(a, b)`; A's fake reads the layout from the plan's ops, never from
B's code.

**Suite**: `PYTHONPATH=src .venv/bin/python -m pytest -q` on a clean `git archive` (baseline at `37b9eb6` to be
measured by I), and `python.exe -m pytest tests/test_workbook_build.py tests/test_workbook_window.py -q` under Windows.

---

## 5. The fixtures

Both are written by `xlsx.write_new` from a `GearboxSpec` in the script (as sections b and c write theirs), saved
once by Excel, and committed to `tests/fixtures/excel-windows/` as Excel saved them (`--fixtures`). **Output folder
is blank** in both: the script passes the section's folder as the strip's (as `WorkbookWindow._folder` does), so a
copied folder needs no cell changed (§6.2). Box: pressure angle 20°, efficiency 98 %. Every clearance below is the
least distance between the true bounding cylinders and shaft spans of §2.5 (worked out for this revision by dense
sampling of `bevel.blank_points` blanks and tip cylinders; B's `cylinder_gap` must agree to 0.1 mm).

### 5.1 Fixture A — `Bevel_Reducer` (the W6 row: a bevel stage feeding a parallel stage)

| Shaft | X | Y | Z | Axis | Role | Speed, torque |
|---|---|---|---|---|---|---|
| S1 | 0 | 0 | 60 | X+ | input | 1500 rpm, 10 N·m |
| S2 | 0 | 0 | 0 | Z+ | | |
| S3 | −68 | 0 | 0 | Z+ | output | |

| Gear | Shaft | At | Kind | Teeth | Module | Face | Bore |
|---|---|---|---|---|---|---|---|
| G1 | S1 | 0 | bevel | 20 | 3 | 20 | 10 |
| G2 | S2 | 60 | bevel | 40 | 3 | 20 | 10 |
| G3 | S2 | 5 | spur | 17 | 2 | 10 | 8 |
| G4 | S3 | 5 | spur | 51 | 2 | 10 | 8 |

Meshes G1–G2, G3–G4. The bevel pair is exactly probe `bevel_end_to_end`'s (m 3, 20 : 40, Σ 90°, face 20, bore 10),
already built on SolidWorks: δ 26.565051° / 63.434949°, R 67.082039, outside diameters 67.218027 / 121.757549.
G1's apex = (0, 0, 60) + 0·X; G2's = (0, 0, 0) + 60·Z: together at (0, 0, 60); the heel pitch point (60, 0, 90) from
either gear. The layout: S1 on the Top plane and `"S1 Z Plane"` (`"S1 Z"` = 60, from Front); S2 on the Right and Top
planes; S3 on `"S3 X Plane"` (minus side, linked negated, `"S3 X"` = −68) and Top. G3–G4: 2·(17 + 51)/2 = 68 ✓.
Anchors: S1 G1 (apex on the Right plane: coincident), S2 G2 (`"G2 Apex Z"` = 60; G3 locked to G2), S3 G4 (front face
on Front: coincident).

Clearances: G1's blank spans 40.92 → 62.63 along its axis (x) and reaches 33.609 from it; G1–G3 27.37 mm, G1–G4
58.27; S1's span (x 40.9 → 62.6 at z 60) is 54.59 from G3 and 75.01 from G4; S3's span (z 0 → 10) 110.15 from G1
and 70.33 from G2; S1 against G2 and S2 against G1 are bevel partners, exempt. No clearance warning.

**The expected Checks panel** (pinned by B with the cells W6-INTERFACES gives): three warnings, all the strip's own,
no error, nothing gearbox-level — G1: *"The tooth tip is 0.722 mm thick, under 0.3 × module (0.9 mm)."* and *"The
involute starts at 65.444 mm, above the form diameter of 63.267 mm, so the bottom of the working flank is a straight
line."*; G4: *"The involute starts at 99.28 mm, above the form diameter of 98.614 mm, so the bottom of the working
flank is a straight line."* The header: *"Bevel and parallel train · 2 meshes · 6.000 : 1 · output at 90° to the
input"*.

Expected, own-axis speeds (c = +1 for the bevel mesh, `+1 = a·a` for G3–G4):

- 20·ω1 + 40·ω2 = 0 → **ω2 = −750** rpm about +Z; 17·ω2 + 51·ω3 = 0 → **ω3 = +250** about +Z; **6.000 : 1**, output at 90°
  to the input. Torques: S2 = 10 · 40/20 · 0.98 = **19.60**, S3 = 19.60 · 51/17 · 0.98 = **57.624** N·m. Speeds panel:
  S1 *1500.0 rpm anticlockwise seen from +X*, S2 *750.0 rpm clockwise seen from +Z*, S3 *250.0 rpm anticlockwise seen
  from +Z*.
- Drive of +30° on G1 (about its own +Z = +X): G2 **−15°**, G3 **−15°**, G4 **+5°**.
- After G1 20 → 21 (r3): ω2 = −787.5, ω3 = +262.5; drive: G2 **−15.75°**, G3 −15.75°, G4 **+5.25°**; 21 : 40 at 90° is
  still two cones (δ 27.699473°, R 67.766142).
- After S1 Axis X+ → X− (r4): G1 now faces −X; the contact moves to (−60, 0, 90), c stays +1, so ω2 = −750 and the
  drive signs are unchanged.

Physical check of the sign: at the pitch point `P = apex + R(cos δ1, 0, sin δ1)`, G1's velocity is `ω1·X × (0, 0, R
sin δ1) = −ω1 R sin δ1 Y` and G2's is `ω2·Z × (R sin δ2, 0, 0) = ω2 R sin δ2 Y`; equal, so `ω2 = −ω1 z1/z2`.

### 5.2 Fixture B — `Crossed_Slant` (a crossed helical stage, then a bevel stage at 120° onto a slanted shaft)

Re-laid after the review (M1, M5): the bevel stage now meets at **120°** between the own axes, so real teeth confirm
the turned read-back past 90°, and S3's span no longer passes near S1 or through G2.

| Shaft | X | Y | Z | Axis | Role | Speed, torque |
|---|---|---|---|---|---|---|
| S1 | 0 | 0 | 0 | Z+ | input | 1000 rpm, 5 N·m |
| S2 | 0 | 84.852814 | 8 | X+ | | |
| S3 | −110 | 84.852814 | 8 | −1, 1.732050807569, 0 | output | |

| Gear | Shaft | At | Kind | Teeth | Module | Face | Helix, hand | Bore |
|---|---|---|---|---|---|---|---|---|
| G1 | S1 | 10 | helical | 20 | 2 | 16 | 45°, right | 6 |
| G2 | S2 | 0 | helical | 40 | 2 | 16 | 45°, right | 8 |
| G3 | S2 | −110 | bevel | 20 | 2.5 | 10 | | 8 |
| G4 | S3 | 0 | bevel | 30 | 2.5 | 10 | | 8 |

Meshes G1–G2, G3–G4. **The crossed pair** is `crossed_end_to_end`'s (m_n 2, 20 : 40, β 45/45 right, Σ 90°; faces 16
here), built on 2026: C = (2/2)(20 + 40)/cos 45° = **84.852814**; the common perpendicular from S1 (the Z axis) to S2
(the line along X at y 84.852814, z 8) is +Y; the contact (0, 28.284271, 8) lies inside G1's face (z 2 → 18; its
middle is at 10, so the contact is 2 mm off it, which exercises the helix twist in the phase) and G2's (x −8 → 8). In
world `t ∝ (−1, 0, 1)` at the contact, so `s1 = sign(Z·t) = +1` and, with S2 on X+, `s2 = sign(X·t) = −1`: **c = −1**
(S2 on X− would give +1 and the same physical turn; X+ is chosen so G3's apex can lie beyond G3's body, away from G2).
**The bevel pair**: own axes X+ and d̂ = (−0.5, 0.866025, 0), Σ = acos(−0.5) = **120°**; δ 40.893395° / 79.106605°,
R 38.188131, both cones (G4 nearly flat). G3's apex = (0, 84.852814, 8) + (−110)·X = (−110, 84.852814, 8) = S3's point
= G4's apex; G3's body lies on +X of it, x −90.3 → −77.6, between its apex and G2. G3 is a follower (locked to G2); S3
is a slanted line axis (`"S3 Line"`, `"S3 Axis"`). Anchors: S1 G1 (`"G1 Face Z"` = 2); S2 G2 (its origin, the front
face centre, at x = −8, on the minus side of Right: `"G2 Face X"` = 8, a flipped point distance as `AXIAL_MATE_ROUTE`
makes one below a plane); S3 G4 (apex measured from Top, the base plane nearest d̂ (|d̂·Y| 0.866 > |d̂·X| 0.5):
`"G4 Apex Y"` = 84.852814).

Clearances: G1–G3 66.18, G1–G4 103.38, G2–G3 69.65, G2–G4 71.44 mm; S1's span (z 2 → 18) is 26.28 from G2, 96.47
from G3 and 133.66 from G4; S2's span (x −90.3 → 8) is 54.57 from G1; S3's span (G4's own blank, about 20 mm along d̂
from the apex) is 112.65 from G1 and 104.17 from G2; S2 against G4 and S3 against G3 are bevel partners, exempt. No
clearance warning.

**The expected Checks panel**: six warnings, all the strip's own, no error, nothing gearbox-level — G1 and G2 each
*"A helix angle of 45° is outside the usual 8–30° for a helical gear."* and the involute-start warning (G1: *"…starts
at 53.849 mm, above the form diameter of 53.14 mm…"*, G2: *"…at 110.417 mm, above the form diameter of 109.413
mm…"*); G3 *"The tooth tip is 0.664 mm thick, under 0.3 × module (0.75 mm)."* and *"The involute starts at 64.97 mm,
above the form diameter of 62.668 mm, so the bottom of the working flank is a straight line."*; G4 none. The header:
*"Crossed and bevel train · 2 meshes · 3.000 : 1 · output at 90° to the input"*.

Expected, own-axis speeds: 20·1000 + (−1)·40·ω2 = 0 → **ω2 = +500** about +X; 20·ω2 + 30·ω3 = 0 → **ω3 = −333.333…**
(−1000/3) about S3's Axis as typed, which is +333.33 about its plus direction (0.5, −0.866, 0); **3.000 : 1**. Speeds
panel: S1 *1000.0 rpm anticlockwise seen from +Z*, S2 *500.0 rpm anticlockwise seen from +X*, S3 *333.3 rpm
anticlockwise seen from (0.5, −0.866, 0)*. Torques S2 = 5 · 2 · 0.98 = **9.80**, S3 = 9.80 · 1.5 · 0.98 = **14.406**
N·m. Drive +30° on G1: G2 **+15°**, G3 **+15°**, G4 **−10°**. After G4 30 → 31 (r6): still two cones (δ 39.515338° /
80.484662°, R 39.290584), G4 **−9.677419°** (−15·20/31).

---

## 6. The demonstration (package E), full build first

### 6.1 Sections

New sections in `probe/workbook_assembly_check.py`, prefix `r`, through the app's own code as W5's are (`plan_gearbox`
→ `build_gearbox` → `finish_build`; `classify` → `update_gearbox` → `finish_update`; every footer sentence logged),
**on the committed findings only** (no finding is set by the script). §4.1 and §4.2 of W5-PLAN apply with these
changes: **frames** against `layout.frames` to 1e-6 for any axis; **layout axes** by `GetRefAxisParams`, each on its
shaft's line to 1e-6 with its direction ±, the sign logged; **the drive** mates the input anchor's Top plane
(`gearN:plane2`) to the layout's base plane square to the input's `u₀` (Right for a Z or Y input, **Top for an X
input**: the input's Top plane contains its axis, so against a plane square to the axis no angle changes), and the
input's turn is **measured**, not assumed from `DEMONSTRATION_DRIVE_SENSE` (Z inputs only), with |δ_in| = 30°
asserted and every other gear judged as `δ_i = δ_in·ω_i/ω_in` to 1e-6 relative; **every turned gear mate's read**
(Reverse, both entity directions, which gear each matched, both τ, the app's verdict) is logged straight after the
build, after each Flip of the control, and after a reopen; **after every control drive on a turned mesh, the
interference check** (review M2): at the driven position (30° off the built phase), the Flip the drive calls right
must show no interference and the other must clash with the mesh's partner — a clash on the Flip the app kept, or
none on the wrong one, STOPs the run.

| Section | Start | Steps and assertions |
|---|---|---|
| **r1** | fresh build of A | Build turning; §4.1 (frames, axes, mates exactly the record's, codes 0, under-defined 2, no interference, half-pitch control on both meshes — the bevel's G1 turned half a pitch must interfere with G2 only); §4.2 drive (+30 → G2 −15, G3 −15, G4 +5); both-Flips control on **G1 meshes G2** with the interference check after each drive; save, close, reopen, the same. Then close every document of the folder and rename it `r1.master`. |
| **r5** | fresh build of B | As r1; the slanted axis on its line; drive from S1 (Right plane, as W5): G2 +15, G3 +15, G4 −10; both-Flips controls with interference on **G1 meshes G2** (skew, 90°) and **G3 meshes G4** (meeting, 120°). Rename to `r5.master`. |
| **r2** | copy of `r1.master` | The user's turn simulated (drive 37°, delete) → Update with nothing changed: nothing put, *"…stand where they were turned"*, frames and flags unchanged. Excel **S1 Z 60 → 64 and G2 At 60 → 64** → Update: `"S1 Z"` 64, `"G2 Apex Z"` 64, every gear put (`restored`), frames to 1e-6, the bevel apexes together in SolidWorks (G1's and G2's origins 1e-6 apart), drive (same ratios), half-pitch control on G1–G2, reopen. |
| **r3** | copy of `r1.master` | Excel **G1 Teeth 20 → 21** → Update: G1's values (21), G2's (`"Mate Teeth"` 21), the remake of G1 meshes G2 at 21 : 40 read back by the committed rule (turned round or not, logged), every gear put; frames; drive (G2 −15.75, G4 +5.25); both-Flips control with interference on the remade mate; reopen and drive again. |
| **r4** | copy of `r1.master` | Excel **S1 Axis X+ → X−** → classify: the structural sentence of §2.9; Build again… → `Bevel_Reducer_r2` turning; earlier files' sha256 and mtime unchanged; §4.1; §4.2 (input turn measured about −X; G2 −15, G4 +5); both-Flips control with interference on G1 meshes G2. |
| **r6** | copy of `r5.master` | Excel **G1 At 10 → 11** → Update: `"G1 Face Z"` 2 → 3, every gear put (G2's phase follows G1's helix at the contact), drive, half-pitch control on G1–G2. Then **G4 Teeth 30 → 31** → Update with the remake of G3 meshes G4 at 20 : 31 on the 120° mate; drive (G4 −9.677419); both-Flips control with interference. Then **S3's direction changed** (`-1, 1.8, 0`) → classify only: the slanted structural sentence; nothing built. Then the sense change of M4, on the classify path only (the fake's round trip covers the worker): a made-up copy of B's crossed stage alone, its S2 moved to the other side of S1 → `resensed` names G1 meshes G2 and the plan's remake carries the new sense. |
| **rw** | `workbook_window_check.py` | Screenshots: A built (the footer with *"drag G1"*, the Speeds lines of §5.1), B read (the end view with the crossed and slanted stages, the Speeds lines of §5.2: *"…500.0 rpm anticlockwise seen from +X…"* and *"…333.3 rpm anticlockwise seen from (0.5, −0.866, 0)…"*). |

r1 and r5 run first (the full build); the copy sections follow. **The close**: one full run of the whole script on
2026 (r sections and W4/W5's m1–m8, a–c, since W6 rewrites kinematics, frames and the sense read under them).
**SolidWorks 2024's confirming build**: r1, r3, r5 (every section that makes or remakes a turned gear mate, the place
W5 saw the versions differ) and m3 (the ring, whose sense read moved onto `sense_reading`), plus the window check.

**The person's step** (2026, then 2024): *Open `Bevel_Reducer.SLDASM` from the r1 log's folder. Drag G1 — the small
bevel gear on the horizontal shaft S1 — round its axis by about a quarter turn. G2, the large bevel gear on the upright
shaft, turns half as far, and G3 under it with it; G4, the large spur gear on S3, turns a sixth as far as G1 and the
other way round from G2. Nothing leaves its axis or passes through another gear. Then press Update SolidWorks with
nothing changed: the footer says the gears stand where they were turned.*

### 6.2 Building once and starting later sections from a copy

The records hold absolute paths, and SolidWorks keeps a document by its file name and an assembly holds absolute
references, so a copy is made valid in four steps by one helper, `copy_built(master, section)`, pinned in
W6-INTERFACES; W7's demonstration reuses it rather than its own protocol (review S8):

1. **The builder section ends clean.** Every document of its folder is closed (`quit_in(folder)`; W5's `close_ours`
   saving this run's modified parts first on 2024), Excel's workbook is closed (`close_books`), no open SolidWorks
   document has a file name the folder holds (`open_titles`), and the folder is renamed `<section>.master` and stays
   so for the rest of the run. From then on the absolute paths stored in its files point at nothing.
2. **The copy.** `shutil.copytree(master, OUT/section)` (`copy2` keeps the mtimes). In the copy, every
   `<Name>.workbook.json` is read with `store.read_link_record`, every string field that starts with the original
   folder (normcase) is rewritten onto the copy's folder — `workbook`, every part's `path`, the gearbox's `layout`,
   `assembly` and each component's `part`, the journal, earlier revisions, `moved_from`, the keys of `unsaved` and
   `mismatched` — and written back with `store.save_link_record`; every `.gear.json` likewise through `store`'s own
   reader and writer, so the bytes are the app's format. Asserted after: `store.record_owner(record, workbook)` is
   OURS; every path in the record exists and lies in the copy; `store.clear_saved` drops nothing; the read's digest
   equals the record's (the Output folder is blank, so no cell changed).
3. **SolidWorks finds the copy's files.** The script opens the copy's assembly once (`OpenDoc6`, silent), reads every
   component's `GetPathName` and the layout component's: each must lie in the copy, or the section STOPs (*a copy
   loaded the master's files*) and falls back to a fresh build of its own. The flags read straight after the open are
   logged as facts, and the assembly is closed **without saving** (`QuitDoc`): with the master renamed for the whole
   run, every later open resolves the same way, so a save is not needed, and not saving keeps the assembly's mtime as
   the build left it before the section's first Update. The first time this runs, it runs under a dialog watcher
   (§7.1).
4. **Two copies are never open together**: each copy section ends as step 1 does (without the rename), since a second
   copy's documents share the first's file names.

---

## 7. What is probed, and what is left to the build

### 7.1 Probed ahead in the demonstration's harness

**Opening a copied assembly whose stored references point at a folder that is gone** (§6.2 step 3). It is the
demonstration's, not the app's, but it is the one step that can raise a modal dialog (a missing-reference or
references-moved prompt) and hang the run. Run once, on the first copy of `r1.master`, before r2 depends on it:
`OpenDoc6` silent under the dialog watcher the scripts already have (`press_dont_save`'s window search), a 120 s
timeout, and the component paths read. On 2024 likewise before its r3. If a dialog appears, the copy route is dropped
and every section builds its fixture fresh (as W5 did); nothing in the app changes.

Not probed ahead, each found by the full build instead: `Insert3DSketch2`/`CreateLine2` in 3D (a toggle that at worst
leaves the part in sketch mode; the build's next op fails with a sentence, no dialog); `InsertAxis2` on a 3D line;
the new plane pairs; the drive against the Top plane. None is a hang, a dialog or a damaged file by anything recorded.
A gear mate between non-parallel axes and a point-distance mate to the Right plane are made first by §7.2.

### 7.2 Probe tier 9, `turned_gear_mate_sense`: the gear mate's sense between non-parallel axes (run first, on SolidWorks 2026)

*For the probe agent, as it stands.* Package P; file `src/gear_generator/probe/p9_turned.py`, registered as tier 9 in
the probe harness like `p8_motion`; results under `probe/results/`, decisions in `probe/decide.py`, findings in
`findings.py`, pins in `tests/test_findings.py`, the decision logic tested in `tests/test_probe_turned.py` on canned
records. **SolidWorks 2026 only**, started for the run and exited after it, one SolidWorks running; 2024 gets its
confirmation at W6's end through r1, r3 and r5. Every call it makes is one the app or an earlier probe has made (the
mates of tier 8, `InsertAxis2` from one sketch line as the macro database records it, `RefPlane` from Top) except the
point-distance mate to a **Right** plane (the same call as to Top and Front) and AddMate5 gear between non-parallel
axes (the question). It does not depend on any W6 code: it carries its own few lines of the rule and the matching
below, and package I's `swcom.sense_reading` is later tested against this probe's recorded cases.

**Why.** W5's read-back (`findings.GEAR_MATE_SENSE_READ_BACK`) compares the two entity directions with each other,
which means nothing when they are at an angle; no gear mate between non-parallel axes has been made by this app or
recorded in the macro database. W6 proposes H (§2.6): *Reverse is True exactly when the mate turns its two gears the
same way about its two entities' own directions.* This probe decides whether H holds, on which angles, and confirms
on the same rig that it reproduces W5's rule on parallel and anti-parallel axes.

**Parts** (scratch, made by the probe in its own folder):
- `SenseA.SLDPRT`: a solid cylinder, radius 10 mm, length 10 mm, extruded from the Front plane along +Z
  (`EXTRUDE_Z_SIGN`), its `"Gear Axis"` made as every gear part makes it (`swcom.insert_axis`, Top then Right, reading
  +Z). It stands for a 20-tooth gear of module 1.
- `SenseB.SLDPRT`: the same at radius 20 mm, a 40-tooth gear. The ratio 20 : 40 tells a right ratio from its inverse.
- One frame part per geometry, `SenseFrame_<case>.SLDPRT`: `"A Axis"` through the Top and Right base planes (the Z
  axis, `AXIS_THROUGH_BASE_PLANE`), and `"B Axis"` made by `InsertAxis2(True)` on the one line of a 2D sketch, the line
  fixed by its end points in model coordinates (the Top plane's sketch y is −Z, `TOP_SKETCH_Y_IS_MINUS_Z`; no
  dimension is needed):
  - *meeting* (`M`): on the Top plane, through the origin, direction `(sin Σf, 0, cos Σf)`;
  - *skew* (`K`): on a plane offset from Top by 30 mm (the sum of the radii) to +Y, or with the flip to −Y, the line
    through `(0, ±30, 0)` with direction `(sin Σf, 0, cos Σf)`; the common perpendicular is the Y axis, `e = ±Y` from A
    to B, and the crossing seen along `e` is a right-hand turn of `+Σf` on one side and `−Σf` on the other: the two
    hands of crossing;
  - *parallel* (`P`): on the Top plane, the line `x = 30` along Z.

**Each geometry's assembly**: the frame inserted, placed on the identity and fixed. Each cylinder inserted, placed by
a `Transform2` put with its own +Z along (`σ = +1`) or against (`σ = −1`) its frame axis's direction, its origin 30 mm
(A) or 50 mm (B) along its own +Z from the meeting point (for `K` and `P`, from its foot of the common perpendicular),
so each body lies on its own +Z side as a bevel's does from its apex (§2.1); then unfixed and held by W5's anchor
mates: its `Gear Axis` coincident with its frame axis (closest alignment), and its origin at a point distance from
the frame base plane whose normal is nearest its axis (Front for A; for B, Right or Front, ties to Right), linked to
nothing. The bodies may overlap; no interference is read in this probe.

**The cases** (44 gear mates in 22 assemblies; the angle between the own axes is Σf for `σAσB = +1` and 180° − Σf
otherwise):

| Class | Σf | Sides | Facings (σA, σB) | Own-axis angles | Mates |
|---|---|---|---|---|---|
| M | 30°, 60°, 90° | — | (+,+), (+,−), (−,+), (−,−) | 30/150, 60/120, 90 | 3 × 4 × 2 Flips = 24 |
| K | 60°, 90° | +Y, −Y | (+,+), (+,−) | 60/120, 90 | 2 × 2 × 2 × 2 = 16 |
| P (controls) | 0° | +X | (+,+) parallel, (+,−) anti-parallel | 0, 180 | 2 × 2 = 4 |

**Per geometry, the steps** (with `CommandInProgress` on for the mate's making, as the app makes mates):
1. Read both cylinders' frames.
2. AddMate5 gear between `A:Gear Axis` (first) and `B:Gear Axis`, ratio (20, 40) numerator first
   (`GEAR_MATE_NUMERATOR_FIRST`), **Flip False**, renamed `"A meshes B"`; keep its status.
3. Read straight after: `IGearMateFeatureData.Reverse` (`GetDefinition`, read only, released); `MateEntity(0)` and
   `MateEntity(1)` → `EntityParams[3:6]`, in assembly space; match each entity to the cylinder whose own +Z (its
   frame's third column) it lies along, `|d·g| ≥ 0.99`, and record the order found (is `MateEntity(0)` the first
   selection?); `τA = sign(dA·gA)`, `τB = sign(dB·gB)`.
4. Read both frames again: neither may have moved (1e-6 mm, 1e-6 per rotation entry).
5. Top-only rebuild (`MATED_ASSEMBLY_REBUILD_ROUTE`); the drive: a temporary angle mate from `A:plane2` to the frame's
   Right plane at 90°, its D1 linked to an assembly global `"Drive"`; `"Drive"` 90 → 120, rebuild; read both frames;
   `δA`, `δB` = each cylinder's turn about **its own +Z** (`swbuild.turn_between`, the third column); `"Drive"` back to
   90, rebuild; the drive's link, global and angle mate deleted (W5's demonstration order).
6. Delete the gear mate (`MATE_DELETE_ROUTE`), make it again with **Flip True**, and repeat steps 3–5.
7. For M90 (+,+), M60 (+,−), K90 +Y and K60 −Y: with the Flip H calls right, save, close, reopen, read (step 3) and
   drive (step 5) again.

**What is measured and how "right" is judged without teeth.** Measured: the turn ratio `δB/δA` (must be −0.5 or +0.5
to 1e-6, else the ratio is wrong) and its sign `m` = +1 when the two cylinders turned the same way about their own +Z,
−1 when opposite. H predicts `m` from the read: the turns are the same way about the entities' directions exactly when
`Reverse`, so `m_H = (+1 if Reverse else −1) · τA · τB`. **Right**, in W6's convention (each own +Z along the gear's
facing, its body on its own +Z side), is what a real pair placed so would need:
- *meeting* (a bevel-like contact, every own-axis angle 30°–150°): **opposite turns** about the own axes, `m = −1`
  (`c = +1`, `k = −zA/zB = −0.5`; §2.4);
- *skew* (a crossed contact): `m = −sA·sB`, where `s = sign(a·t)` and `t` is the common tooth direction at the contact
  of a virtual crossed pair on the case — m_n 1, 20 and 40 teeth, the same hand, `βA = βB = Σl/2` with `Σl` the angle
  between the lines in (0°, 90°], the hand whose `crossed.placement` tilt `−(s_hand(βA + βB))` equals the case's signed
  crossing modulo 180° (right for `−Σf`, left for `+Σf`; at 90° either fits and right is taken) — computed in
  `decide.py` with `gears/crossed.py` (`tooth_direction`, carried to world by the cylinder's frame) and logged;
- *parallel controls*: W5's — opposite turns about +Z for the parallel pair (`m = −1`), the same about own axes for the
  anti-parallel one (`m = +1`), and W5's rule `(Reverse == entities parallel) == internal` (internal False) must call
  right exactly the Flip that turned so.

**The both-Flips control**: in every geometry exactly one of the two Flips must turn right by that criterion, and H's
read must call that one right and the other wrong (`right_H = (m_H == right m)`).

**The decision** (`decide.py`, new entries `turned_sense_read_back`, `turned_sense_angles`):
- `TURNED_GEAR_MATE_SENSE_READ_BACK = "entity senses"` when, for all 40 turned mates: AddMate5's status is
  `ADD_MATE_NO_ERROR`, nothing moved on making, the ratio holds to 1e-6, `m_H == m` (H tells the measured sense), the
  both-Flips control holds in every geometry, and the reads after a reopen agree with the first; and the 4 parallel
  controls agree with W5's rule and with H. Otherwise `decide.py` tries, on the same records, the readings that differ
  from H on non-parallel axes — Reverse against the sign of `dA·dB` (SolidWorks' closest alignment); Reverse against
  the sign of `(dA × dB)·e` for skew axes — and names the one that tells all 40, which becomes the value, and
  `sense_reading`'s contract changes through a stop-and-ask on §4.3; if none tells them all the value is None, W6's
  turned meshes stay refused (§2.6's gate), and the orchestrator asks the user.
- `TURNED_GEAR_MATE_SENSE_ANGLES = (30.0, 150.0)`: the least and greatest angle between the own axes over which every
  case held (meeting 30–150, skew 60–120); narrower if a class fails only at its ends. The app refuses a turned mesh
  outside it with the §2.9 sentence; bevel validation itself allows 10°–170°, so the edges stay refused until probed.
- Recorded as facts, nothing branching on them: `TURNED_GEAR_MATE_MOVES_ON_MAKE` (False expected),
  `GEAR_MATE_ENTITY_ORDER` (whether `MateEntity(0)` is the first selection; the app matches by axis either way, S1).
- The pins in `tests/test_findings.py` name the angles and classes tested, and the result file. The findings are
  reviewed independently before E runs; E's interference controls (M2) then confirm them with teeth.

**Done:** results committed, the decision and findings committed and reviewed, one round (the rule of 2026-11-14); a
failure of AddMate5 or a moved cylinder is a finding, not a retry.

---

## 8. Definition of done, and the order of work

```
review of this plan ─► P: probe tier 9 on 2026 ─► findings, reviewed ──────────────────┐
                    └► I (interface) ─► A ─┐                                            │
                                         B ─┼─► D ─────────────────────────────────────► E: r1, r5 ─► r2, r3, r4, r6, rw
                                         C ─┘                                                └─► 2024: r1, r3, r5, m3, rw
```

An independent review after P, after I, after each of A–D, and after E, as before (Opus subagents). After a fix only
the affected sections rerun; one full run at the close.

**W6 is done when:**

1. The suite is green on a clean archive, with: the golden pins (every committed fixture's frames, θ, speeds and
   checks unchanged); `sense_reading` equal to W5's rule on every parallel case and to H on every tier-9 case, in
   either entity order; the bevel phase equal to `pair.mate_angle` and the crossed phase to `crossed.placement`;
   kinematics, Checks panels and Speeds lines of A and B as §5; `cylinder_gap` against sampling; every §2.9 sentence
   filled from fields; schema 4 reads v1–v3 and refuses a newer schema untouched; the turning round trip on the fake
   for both fixtures, the sense-change remake among it. Windows Tk tests green.
2. `TURNED_GEAR_MATE_SENSE_READ_BACK` and `TURNED_GEAR_MATE_SENSE_ANGLES` are committed from tier 9 and reviewed,
   pinned.
3. r1–r6 and rw pass on SolidWorks 2026 with 0 failed, every turned both-Flips control clear on the right Flip and
   clashing on the wrong one, logs committed; the confirming build passes on 2024; the close's full run passes on
   2026.
4. The person's step is handed to the user (§6.1).
5. PLAN-WORKBOOK carries *Readings chosen (W6)* (D1–D18), §4.2's turned-axes paragraph and the W6 row marked done;
   UI-DESIGN §9 and the boards; HANDOFF updated; the readings to overrule listed for the user.

---

## 9. Risks, and what reading could not settle

- **H (§2.6) — the riskiest point.** Tier 9 decides it on cylinders before anything depends on it. What cylinders
  cannot show is a behaviour tied to teeth; the interference control after every turned control drive (M2) is the
  real-teeth check, and it is also what catches a sign slip in the app's own mesh sense `k`, which the read-back,
  the drive's expectation and the speeds share. What reading could not settle: whether AddMate5 accepts a gear mate
  between perpendicular or skew axes at all (the macro database has no case), whether making one moves a gear (W5
  saw no movement on parallel axes), and the order of `MateEntity` (matched by axis, so it does not matter).
- **Versions.** W5 found toothed rings needing opposite Flips on 2026 and 2024; a turned mesh may too. The read-back
  makes the app indifferent to it, provided the rule holds on both: tier 9 runs on 2026 only, so r1, r3 and r5 on
  2024 are the rule's confirmation there; if 2024 disagrees, that is the phase's one follow-up round.
- **The 3D sketch** (D4) uses two calls the macro database marks unverified. A failure shows in r5's build; the
  fallback is D4 (b), which leaves slanted axes with no phase that builds them — that would go to the user.
- **The copy route** (§6.2) rests on SolidWorks finding references beside the assembly when the stored folder is gone;
  the search order was not read anywhere here. The component-path check and the dialog watcher make a failure visible;
  the fallback is fresh builds.
- **Bevel parts at Σ = 120°** have not been built on SolidWorks (the strip's builds were at 90°, plus crown and
  internal on 2026). Fixture B's G3 and G4 are the first, G4 nearly flat (δ 79.1°).
- **Crown and internal bevel gears** in a workbook are planned like any bevel (their sections were probed on both
  versions, `bevel_planes_beyond_90`), and tier 9 covers the angles they need up to 150°, but no fixture has one and
  they were never built on 2024; a fake test covers the kinematic sense (c = +1).
- **`swbuild.structural_change` does not see a bevel's form change** (an existing gap of the strip's Update values
  too; the small-pinion merge's new refusal, an arc-capped part taken below its tooth count, is unrelated); W6 guards
  the workbook in `update._part` (D14) and leaves the strip alone, as a caveat to write down.
- **The bounding-cylinder clearance** (D8) can warn about gears that do not touch and, being a bound, cannot miss a
  clash between cylinders it bounds; it does not model a bore or a hub. The build's interference check is the judge.
- **Phase tests for turned meshes** cannot use W3's outline-overlap test (the gears share no plane). They rest on the
  reductions to `pair.mate_angle` and `crossed.placement`, a whole-pitch invariance test (turning p by one tooth turns
  q by one tooth), and SolidWorks' half-pitch interference control in every r section.
- **Kinematics rewrite.** Own-axis unknowns change every row of a parallel system by a sign; the golden pins on the
  12 : 1, Risky and Arc_Move speeds (and the Results sheet's numbers) are the guard.
- **The drive for an X input** (Top plane against the layout's Top) is a new pairing of the W5 drive; its sense is
  measured, and a drive that moves a gear when added still STOPs the run as in W5.
- **Not determined by reading:** the direction SolidWorks gives an axis through Top+Front or Right+Front planes (logged,
  not used); whether a Front-offset plane's negated link behaves as Right's and Top's (`LAYOUT_NEGATED_LINK` was read
  on those two; no fixture puts a shaft on the minus side of Front, so a fake test covers it and the first workbook
  with one is its test); and whether the bevel's `"Shaft Angle"` global, typed to nine decimals from a slanted axis,
  rebuilds the part exactly as the plan's value (B's equations test covers the evaluation; r5 measures the frames).
- **The code since the first draft.** The small-pinion merge (`0f5a121`: 6- and 7-tooth pinions validate with recipe A;
  `swbuild.structural_change` refuses an arc-capped part taken back below its count) and the ring checks (`d3f4dcf`,
  `9efde87`: a shifted pinion in a ring at its working centre, and a tip-clash warning no shift silences) touch no part
  of this plan: no fixture has a small pinion or a ring, W6's parallel meshes run W3's `_check_mesh` with those
  checks unchanged in the family frame, and D14 adds to `update._part`, not to `structural_change`.

---

## Changes after the review

Against `W6-PLAN-REVIEW.md` (`8f872f3`) and the orchestrator's rulings, item by item.

- **M1** (the test covered only 90° and 60°). Tier 9 covers 30°–150° between the own axes, meeting and skew (§7.2);
  the finding is limited to the angles shown (`TURNED_GEAR_MATE_SENSE_ANGLES`) and the gate refuses others with a
  sentence (§2.6, §2.9; D18); and fixture B's bevel stage is re-laid at 120° (S2 on X+, G3 at At −110, S3 through
  (−110, 84.852814, 8) along (−1, 1.732, 0)), so real teeth confirm the rule past 90° (§5.2). Both, because the
  re-lay was cheap once M5 forced a re-lay anyway, and the gate keeps an untested angle from building.
- **M2** (one source, k, for verdict, drive and speeds). An interference check after every control drive on a turned
  mesh in r1, r3, r4, r5 and r6: the right Flip clear, the wrong one clashing; a failure STOPs the run (§2.6, §6.1,
  done item 3).
- **M3** (D6 bent the committed-findings rule). Ruled by the orchestrator: the cylinder probe runs first, now, on 2026
  (§7.2, written to be handed over as it stands); D6's in-memory finding and `--assume-turned-sense` are gone; E runs
  on committed findings only; package P added (§4.2); D6 rewritten.
- **M4** (a crossed sense can change on an Update). `MateEntry.sense` and `MatePlan.sense` (§2.8, §4.3);
  `recorded_meshes` from the record's sense; a change is **a remake by Update** (D17, with its reason, §2.7),
  listed in `UpdatePlan.resensed`, with its own sentence (§2.9); r6 shows the classify path.
- **M5** (D8's capsule; fixture B's real clash). True cylinders with `cylinder_gap`, shafts as the spans of their
  gears, a bevel's partner shaft exempt (§2.5, D8); fixture B re-laid (§5.2); each fixture's clearances and expected
  Checks panel pinned (§5.1, §5.2). Also the review's note: G1's blank starts at x 40.92, now in §5.1.
- **M6** (the slant's "seen from"). The plus direction is the one whose first non-zero component is positive; fixture
  B's S3 reads *"seen from (0.5, −0.866, 0)"*, with the format pinned (§2.4, §2.9, §5.2, rw).
- **S1** (entity order). `sense_reading` matches each entity to its gear by axis (§2.6, §4.3); the fake shuffles the
  order in a test; tier 9 records the order as a fact.
- **S2 / D16.** Ruled by the orchestrator: no static fallback; a workbook with a turned mesh is refused before Build
  while the finding is missing or its angle is outside the finding's range, with a full sentence, Build parts still
  offered (`motion.turned_refusal`, §2.6, §2.9); `motion_reason(report)` dropped.
- **S3** (D1 is a user question). The consequence is stated in §2.1 and D1 is first among the readings for the user
  (§3).
- **S4** (kinematics pins). Every caller passes `senses`, `None` meaning W3's behaviour; keys are the Meshes row's
  ordered pair; Fractions with c ∈ {−1, +1}; the carrier-ready own-axis form written for W7 (§2.4).
- **S5** (Results rows). Bevel rows: shaft angle, cone distance, apex distance, contact ratio; crossed rows: shaft
  angle, centres along the common perpendicular, normal contact ratio, and a note on efficiency; 3D extent (§2.4).
- **S6** (word and vector). Retyping the same direction is no change (§2.1); §2.7's row reads "any change of a
  shaft's direction".
- **S7** (slanted axes). The line axis is read back in Update's check phase and on reuse (`Session.axis_line`), a
  moved line refused with a sentence (§2.7); the nearest-plane tie order Right, Top, Front (§2.6).
- **S8** (one copy helper). `copy_built` pinned in W6-INTERFACES for W7 to reuse; the copy's assembly is no longer
  saved, and why (§6.2).
- **S9** (the probe script's call). I fixes the one `gear_mate_sense` call in `probe/workbook_assembly_check.py`
  (§4.1).
- **S10** (sentence rules). The apex sentence names Gear B; the signed crossing is a right-hand turn about `e`,
  reduced to (−90°, 90°]; shafts that meet get their own sentence; a herringbone's hand on a turned shaft names the
  half nearest its own front face (§2.9).
- **Schema numbers.** W6 sets 4 and nothing after it: "a v5 one" became "a record of a newer schema" (§2.8, §4.1,
  done item 1).
- **The code since the first draft** (the small-pinion merge, the ring checks `d3f4dcf` and `9efde87`): checked,
  nothing contradicts the plan (§9's last item).
- **The shared shapes** for the interface commit now have their own section, §4.3.
