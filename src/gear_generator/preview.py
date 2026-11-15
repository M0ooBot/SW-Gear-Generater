"""Where the Derived panel's gears go on its canvas, worked out without a window.

The panel draws one picture: in pair mode both gears at one scale, meshed at the
centre distance their teeth make, with that distance dimensioned below them; in
single mode the one gear with its pitch diameter dimensioned. Everything about
*where* — the scale, the two centres, how far gear B is turned, where the
dimension line and its label sit — is decided here, in millimetres and canvas
pixels, so it can be tested on a machine with no display. :mod:`gui` only
strokes what comes back.

Nothing here touches tkinter, and nothing here holds state.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from .gears import bevel, pair as pairs
from .gears.equations import literal

# The panel body is the strip less the panel border and its own padding; the
# design's 436 is that width rounded up. 210 px is deep enough for a 60-tooth
# wheel beside its pinion and the dimension under them.
WIDTH = 434
HEIGHT = 210

PAD = 14          # left and right of the gears
TOP = 8           # above them
DIM_ZONE = 46     # kept clear under them for the dimension and its label
DIM_DROP = 24     # from the lowest point of the larger gear down to the line
DIM_OVERRUN = 4   # how far an extension line passes the dimension line
LABEL_LIFT = 5    # the label's baseline above the dimension line


@dataclass(frozen=True)
class Placed:
    """One gear on the canvas: where its centre is, and how far it is turned."""

    label: str
    x: float              # canvas px
    y: float              # canvas px
    rotation: float       # radians, anticlockwise, the way the outline is given
    tip_radius: float     # mm
    pitch_radius: float   # mm
    bore_radius: float    # mm, 0 when there is no bore


@dataclass(frozen=True)
class Dimension:
    """The dimension under the gears: a line with arrowheads, and what it says."""

    x0: float
    x1: float
    y: float
    extensions: Tuple[Tuple[float, float, float], ...]   # (x, from y, to y)
    text: str
    text_x: float
    text_y: float                                        # the text's bottom edge


@dataclass(frozen=True)
class Layout:
    width: int
    height: int
    scale: float                  # canvas px per mm
    gears: Tuple[Placed, ...]
    centre_distance: float        # mm; 0 for a single gear
    dimension: Dimension
    # Drawn instead of each gear's own outline when given: canvas-pixel polylines
    # (a bevel gear's axial section), and faint reference lines (its pitch cone).
    polylines: Tuple[Tuple[Tuple[float, float], ...], ...] = ()
    guides: Tuple[Tuple[Tuple[float, float], ...], ...] = ()


def mesh_rotation(teeth: int) -> float:
    """How far the second gear is turned to face the first, in radians.

    Half a turn, so its far side is drawn towards the pinion, plus the mesh
    angle the assembly is actually mated at — half a tooth pitch for an even
    count, nothing for an odd one, which already has a tooth opposite a space
    (:func:`gears.pair.mesh_angle`). Turned any other way the two outlines
    would be drawn crossing, which is not what the pair does.
    """
    return math.pi + math.radians(pairs.mesh_angle(teeth))


def _is_bevel(g) -> bool:
    return type(g).__name__ == "BevelDerived"


def _is_ring(g) -> bool:
    return type(g).__name__ == "InternalDerived"


def layout(gears: Sequence, width: int = WIDTH, height: int = HEIGHT,
           labels: Sequence[str] = ("A", "B"), note: str = "") -> Layout:
    """Place one or two gears — ``SpurDerived``s — on a canvas that size.

    Two gears are placed at ``m (N_A + N_B) / 2`` apart — or, shifted, at their
    working centre distance — the distance their teeth make and the one the
    assembly is mated at, and the scale is whatever
    lets both of them and the gap between them fit; one gear fills the height.
    A ring and its pinion go to :func:`layout_internal`, bevel gears to
    :func:`layout_bevel`. ``note`` follows the dimension's text (a crossed
    pair's ``Σ 90°``).
    """
    if not gears or len(gears) > 2:
        raise ValueError(f"The preview draws one gear or two, not {len(gears)}.")
    if any(_is_bevel(g) for g in gears):
        return layout_bevel(gears, width, height, labels)
    if len(gears) == 2 and _is_ring(gears[1]):
        return layout_internal(gears[0], gears[1], width, height, labels)
    tips = [g.rim / 2.0 if _is_ring(g) else g.ra for g in gears]
    centre_distance = 0.0
    if len(gears) == 2:
        # Shifted gears sit at their working centre distance, a little off the pitch circles touching.
        shifted = getattr(gears[0], "shift", 0.0) or getattr(gears[1], "shift", 0.0)
        centre_distance = pairs.centre_of(gears[0], gears[1]) if shifted else (gears[0].d + gears[1].d) / 2.0
    extent = tips[0] + centre_distance + tips[-1] if centre_distance else 2 * tips[0]
    gear_height = height - DIM_ZONE - TOP
    scale = min((width - 2 * PAD) / extent, gear_height / (2 * max(tips)))
    y = TOP + gear_height / 2.0
    left = (width - extent * scale) / 2.0

    placed: List[Placed] = []
    for index, g in enumerate(gears):
        x = left + tips[0] * scale + (centre_distance * scale if index else 0.0)
        placed.append(Placed(
            label=labels[index] if len(gears) > 1 else "",
            x=x, y=y,
            rotation=mesh_rotation(g.teeth) if index else 0.0,
            tip_radius=tips[index], pitch_radius=g.rp,
            # A ring's rim is drawn where a bore would be: one plain circle.
            bore_radius=g.rim / 2.0 if _is_ring(g) else (g.bore / 2.0 if g.bore > 0 else 0.0),
        ))

    y_dim = y + max(tips) * scale + DIM_DROP
    if centre_distance:
        # Centre to centre: the extension lines start clear of the centre marks.
        x0, x1 = placed[0].x, placed[1].x
        top = y + 6
        text = f"C {_n(centre_distance)} mm" + (f" · {note}" if note else "")
    else:
        # The pitch diameter, which is what module × teeth comes to.
        x0 = placed[0].x - placed[0].pitch_radius * scale
        x1 = placed[0].x + placed[0].pitch_radius * scale
        top = y
        text = f"PD {_n(2 * placed[0].pitch_radius)} mm"
    dimension = Dimension(
        x0=x0, x1=x1, y=y_dim,
        extensions=((x0, top, y_dim + DIM_OVERRUN), (x1, top, y_dim + DIM_OVERRUN)),
        text=text, text_x=(x0 + x1) / 2.0, text_y=y_dim - LABEL_LIFT,
    )
    return Layout(width=width, height=height, scale=scale, gears=tuple(placed),
                  centre_distance=centre_distance, dimension=dimension)


def layout_internal(pinion, ring, width: int = WIDTH, height: int = HEIGHT,
                    labels: Sequence[str] = ("A", "B")) -> Layout:
    """A pinion inside its ring: the ring centred, the pinion ``m (N₂ − N₁) / 2`` to its right.

    The pinion is turned half its tooth pitch, as the assembly mates it
    (:func:`gears.pair.internal_mesh_angle`), so its tooth sits in the ring's
    space on +X; the ring is not turned.
    """
    centre_distance = (ring.d - pinion.d) / 2.0
    rim = ring.rim / 2.0
    gear_height = height - DIM_ZONE - TOP
    scale = min((width - 2 * PAD) / (2 * rim), gear_height / (2 * rim))
    y = TOP + gear_height / 2.0
    x_ring = width / 2.0
    placed = (
        Placed(label=labels[0], x=x_ring + centre_distance * scale, y=y,
               rotation=math.radians(pairs.internal_mesh_angle(pinion.teeth)), tip_radius=pinion.ra,
               pitch_radius=pinion.rp, bore_radius=pinion.bore / 2.0 if pinion.bore > 0 else 0.0),
        Placed(label=labels[1], x=x_ring, y=y, rotation=0.0, tip_radius=rim, pitch_radius=ring.rp,
               bore_radius=rim),
    )
    y_dim = y + rim * scale + DIM_DROP
    x0, x1 = placed[1].x, placed[0].x
    dimension = Dimension(
        x0=x0, x1=x1, y=y_dim,
        extensions=((x0, y + 6, y_dim + DIM_OVERRUN), (x1, y + 6, y_dim + DIM_OVERRUN)),
        text=f"C {_n(centre_distance)} mm", text_x=(x0 + x1) / 2.0, text_y=y_dim - LABEL_LIFT,
    )
    return Layout(width=width, height=height, scale=scale, gears=placed, centre_distance=centre_distance,
                  dimension=dimension)


def bevel_section(g) -> List[List[Tuple[float, float]]]:
    """A bevel gear's axial section in its own frame, mm: ``(x, z)``, the apex at the origin and the axis +z.

    Both halves of the revolved blank, each a closed loop, and the right half's
    pitch cone line from the apex to the heel.
    """
    right = [tuple(p) for p in bevel.outline(g)]
    left = [(-x, z) for x, z in right]
    return [right, left]


def _turned(points, angle_deg: float):
    """About the y axis by ``angle``, seen from +y: ``(x, z)`` → ``(x cos + z sin, −x sin + z cos)``."""
    c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    return [(x * c + z * s, -x * s + z * c) for x, z in points]


def layout_bevel(gears: Sequence, width: int = WIDTH, height: int = HEIGHT,
                 labels: Sequence[str] = ("A", "B")) -> Layout:
    """One bevel gear's axial section, or two meeting at their pitch apex with their axes Σ apart.

    Drawn in the assembly's XZ plane seen from +Y: gear A's axis up the canvas,
    gear B's turned Σ about the apex towards +X, so the two pitch cones lie
    along one line — the same frame :func:`gears.pair.bevel_assembly_plan`
    places gear B in.
    """
    loops: List[List[Tuple[float, float]]] = []
    guides: List[List[Tuple[float, float]]] = []
    for index, g in enumerate(gears):
        turn = g.shaft_angle if index else 0.0
        for loop in bevel_section(g):
            loops.append(_turned(loop, turn))
        # Gear B meets gear A along its own −X side, where the assembly turns a tooth to.
        side = -1.0 if index else 1.0
        pitch = (side * g.cone_distance * math.sin(math.radians(g.delta)),
                 g.cone_distance * math.cos(math.radians(g.delta)))
        guides.append(_turned([(0.0, 0.0), pitch], turn))
        guides.append(_turned([(0.0, 0.0), (0.0, g.crown_to_apex + g.face_width)], turn))
    xs = [x for loop in loops for x, _ in loop] + [0.0]
    zs = [z for loop in loops for _, z in loop] + [0.0]
    gear_height = height - DIM_ZONE - TOP
    span_x, span_z = max(xs) - min(xs), max(zs) - min(zs)
    scale = min((width - 2 * PAD) / span_x, gear_height / span_z)
    left = (width - span_x * scale) / 2.0
    top = TOP + (gear_height - span_z * scale) / 2.0

    def canvas(points) -> Tuple[Tuple[float, float], ...]:
        return tuple((left + (x - min(xs)) * scale, top + (max(zs) - z) * scale) for x, z in points)

    apex = canvas([(0.0, 0.0)])[0]
    placed = tuple(
        Placed(label=labels[index] if len(gears) > 1 else "", x=apex[0], y=apex[1],
               rotation=math.radians(g.shaft_angle if index else 0.0), tip_radius=g.da / 2.0, pitch_radius=0.0,
               bore_radius=0.0)
        for index, g in enumerate(gears)
    )
    first = gears[0]
    y_dim = top + span_z * scale + DIM_DROP
    if len(gears) == 2:
        pitch_x = apex[0] + first.cone_distance * math.sin(math.radians(first.delta)) * scale
        x0, x1 = apex[0], pitch_x
        text = f"R {_n(first.cone_distance)} mm · Σ {_n(first.shaft_angle, 2)}°"
    else:
        x0, x1 = apex[0] - first.da / 2.0 * scale, apex[0] + first.da / 2.0 * scale
        text = f"OD {_n(first.da)} mm"
    y_dim = min(y_dim, height - DIM_OVERRUN - 1)
    dimension = Dimension(
        x0=x0, x1=x1, y=y_dim,
        extensions=((x0, apex[1], y_dim + DIM_OVERRUN), (x1, apex[1], y_dim + DIM_OVERRUN)),
        text=text, text_x=(x0 + x1) / 2.0, text_y=y_dim - LABEL_LIFT,
    )
    return Layout(width=width, height=height, scale=scale, gears=placed,
                  centre_distance=first.cone_distance if len(gears) == 2 else 0.0, dimension=dimension,
                  polylines=tuple(canvas(loop) for loop in loops), guides=tuple(canvas(g) for g in guides))


def points_on(outline: Sequence[Tuple[float, float]], placed: Placed,
              scale: float) -> List[Tuple[float, float]]:
    """One gear's outline in canvas pixels: turned, scaled, and put at its centre.

    The canvas counts y downwards and the outline counts it upwards, so y is
    subtracted rather than added.
    """
    cos, sin = math.cos(placed.rotation), math.sin(placed.rotation)
    return [
        (placed.x + (x * cos - y * sin) * scale, placed.y - (x * sin + y * cos) * scale)
        for x, y in outline
    ]


def _n(value: float, places: int = 3) -> str:
    """The same number formatting the readouts use: 60.0 reads ``60``."""
    return literal(round(float(value), places))



# -- the Workbook window's end view (PLAN-WORKBOOK §5, W3) ---------------------------------


# The end view's marks, in design pixels (``unit`` grows them to the screen): the origin's X and Y arrows
# and their heads' half-width, and a shaft's name, set a gap off its cross in a mono face about this size.
ORIGIN_ARROW = 26
ARROW_HEAD = 3
LABEL_GAP = 6
LABEL_CHAR = 7            # a character's width at 11.5 px mono, a little over
LABEL_HEIGHT = 13
# Where a shaft's name goes, in order of preference: below right, then the other sides. Each is the corner of
# the text at the anchor point, as Tk names it (``nw``: the text's top left is at the point).
LABEL_SIDES = (("nw", 1, 1), ("ne", -1, 1), ("se", -1, -1), ("sw", 1, -1))


@dataclass
class EndView:
    """A workbook's gears seen from +Z, in canvas pixels: each gear's outline at its turn, the shafts, the origin.

    W6: a shaft off the Z family is a line (``lines``), not a cross, and its gears are their sections seen side-on.
    """

    scale: float = 1.0
    outlines: List[Tuple[str, int, List[Tuple[float, float]]]] = None   # (gear, plane index, points)
    rims: List[Tuple[str, int, float, float, float]] = None              # a ring's outside: (gear, plane, x, y, r)
    shafts: List[Tuple[str, float, float]] = None                        # (name, x, y): a shaft along Z, a cross
    origin: Optional[Tuple[float, float]] = None                         # None when it is off the picture
    planes: List[float] = None                                           # the face heights, in drawing order
    labels: List[Tuple[str, float, float, str]] = None                   # (name, x, y, Tk anchor), one per shaft
    lines: List[Tuple[str, float, float, float, float]] = None           # (name, x0, y0, x1, y1): a turned shaft
    carriers: List[Tuple[str, float, float, float]] = None               # (name, x, y, r): W7, through its planets


def _label_box(name: str, x: float, y: float, side, unit: float) -> Tuple[float, float, float, float]:
    """The box a shaft's name takes on ``side`` of its cross at (x, y): (left, top, right, bottom)."""
    _, sx, sy = side
    w, h, gap = len(name) * LABEL_CHAR * unit, LABEL_HEIGHT * unit, LABEL_GAP * unit
    ax, ay = x + sx * gap, y + sy * gap
    return (ax if sx > 0 else ax - w, ay if sy > 0 else ay - h, ax + w if sx > 0 else ax, ay + h if sy > 0 else ay)


def _overlaps(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _place_label(name: str, x: float, y: float, origin, unit: float,
                 bounds: Optional[Tuple[float, float]] = None) -> Tuple[str, float, float, str]:
    """A shaft's name below right of its cross, unless that would sit on the origin's arrows: then the first
    side clear of them (below left, for a shaft at the origin, since the arrows point right and up). With no
    side clear, below right as ever. ``bounds`` (the canvas's width and height, given when a turned shaft is
    named at the end of its line, which may be the canvas's edge: W6): the sides that keep the name on the canvas
    are tried first, in the same order."""
    sides = LABEL_SIDES
    if bounds is not None:
        w, h = bounds

        def inside(side) -> bool:
            left, top, right, bottom = _label_box(name, x, y, side, unit)
            return left >= 0 and top >= 0 and right <= w and bottom <= h
        sides = tuple(s for s in LABEL_SIDES if inside(s)) or LABEL_SIDES
    if origin is not None:
        ox, oy = origin
        reach, head, gap = ORIGIN_ARROW * unit, ARROW_HEAD * unit, LABEL_GAP * unit
        # Each arrow from the origin out, with a gap round it, so a name never crowds a head or the shaft.
        arrows = ((ox, oy - head - gap, ox + reach + gap, oy + head + gap),       # X, to the right
                  (ox - head - gap, oy - reach - gap, ox + head + gap, oy))       # Y, up
        side = next((s for s in sides
                     if not any(_overlaps(_label_box(name, x, y, s, unit), a) for a in arrows)), sides[0])
    else:
        side = sides[0]
    anchor, sx, sy = side
    return name, x + sx * LABEL_GAP * unit, y + sy * LABEL_GAP * unit, anchor


# How far a turned shaft's line runs past the gears on it, mm, either end.
SHAFT_OVERRUN = 12.0
ALONG_Z = 1e-9            # a gear whose axis has no more than this across Z is seen end-on


def _seen_end_on(p) -> bool:
    """Whether a placed gear's own axis runs along Z (W3–W5's every gear), so it is seen end-on from +Z."""
    axis = getattr(p, "axis", (0.0, 0.0, 1.0))
    return abs(axis[0]) <= ALONG_Z and abs(axis[1]) <= ALONG_Z


def _across(axis) -> Tuple[float, float, float]:
    """A unit vector square to ``axis`` and to Z: the side a gear on a turned shaft is seen from +Z."""
    ax, ay, _ = axis
    length = math.hypot(ax, ay)
    return (-ay / length, ax / length, 0.0)


def _side_on(p) -> List[List[Tuple[float, float]]]:
    """A gear on a turned shaft seen side-on from +Z, world mm (x, y): its section in the plane through its axis
    and square to Z, projected onto XY — a bevel gear's blank (both halves, :func:`bevel_section`, the apex at its
    At), any other gear the rectangle of its face and outside diameter."""
    a, w, c = p.axis, _across(p.axis), p.centre
    if getattr(p, "bevel", False):
        loops = bevel_section(p.derived)
    else:
        r, half = p.outer_radius, p.face / 2.0
        loops = [[(-r, -half), (r, -half), (r, half), (-r, half), (-r, -half)]]

    def world(across: float, along: float) -> Tuple[float, float]:
        return (c[0] + along * a[0] + across * w[0], c[1] + along * a[1] + across * w[1])

    return [[world(x, z) for x, z in loop] for loop in loops]


def _circle(cx: float, cy: float, r: float, count: int = 96) -> List[Tuple[float, float]]:
    return [(cx + r * math.cos(2 * math.pi * i / count), cy + r * math.sin(2 * math.pi * i / count))
            for i in range(count + 1)]


def _bevel_end_on(p) -> List[List[Tuple[float, float]]]:
    """A bevel gear on a Z shaft seen end-on: the circles of its heel and toe tips (its teeth are on the cone)."""
    g = p.derived
    heel = max(x for x, _ in bevel_section(g)[0])
    toe = heel * (g.cone_distance - g.face_width) / g.cone_distance
    return [_circle(p.centre[0], p.centre[1], heel), _circle(p.centre[0], p.centre[1], toe)]


def layout_gearbox(placed, theta, width: int = 696, height: int = 300, pad: float = 16.0,
                   step: int = 1, unit: float = 1.0, carriers=None) -> EndView:
    """Every placed gear drawn as the strip draws one, turned to its phase, the whole fitted to the canvas.

    ``placed`` is ``{gear: workbook.geometry.Placed}`` and ``theta`` its turns.
    The view is from +Z, as SolidWorks' Front view: +X right, +Y up. A gear is
    drawn at the middle of its face, so a helical gear shows its section there.
    Gears are grouped by face height, a plane each, so the window can colour
    the stages apart; the planes are drawn nearest +Z last. Each shaft's name
    goes below right of its cross, or on a side clear of the origin's arrows
    when that would sit on them. ``unit`` is screen pixels per design pixel,
    for those fixed-size marks.

    W6 (W6-PLAN §2.10): a gear whose axis is not along Z is drawn as its
    section seen side-on (:func:`_side_on`), projected onto XY at its place,
    and its shaft as a line along the shaft through its gears' extent, a
    little past them; a bevel gear on a Z shaft is its heel and toe tip
    circles. Such a gear's plane is the height of its At point (a bevel's
    apex), so a right-angle stage takes one colour. A gearbox with no turned
    shaft is drawn exactly as before.

    W7 (W7-PLAN §2.12): every planet copy is drawn as any gear (``placed``
    holds each copy under its own shaft, ``P copy 2``), and each carrier as a
    circle through its planets' axes (``carriers``, dashed in the window) with
    a cross at its axis. ``carriers`` maps a carrier shaft to its axis's world
    (x, y) (``geometry.shaft_lines``); without it the centre of its copies is
    taken. Shafts on one line (a planetary's sun, carrier and ring) share a
    cross, named once with every name on it: ``S, R, C``.
    """
    from .gears import kind_for
    view = EndView(outlines=[], rims=[], shafts=[], planes=[], labels=[], lines=[], carriers=[])
    if not placed:
        return view
    shapes = []                          # (gear, p, [loop of world points], height for its plane)
    for gear, p in placed.items():
        if not _seen_end_on(p):
            shapes.append((gear, p, _side_on(p), p.centre[2]))
            continue
        if getattr(p, "bevel", False):
            shapes.append((gear, p, _bevel_end_on(p), p.z))
            continue
        kind = kind_for(p.spec)
        points = kind.outline(p.spec, p.derived)[::step]
        angle = p.space_angle(theta.get(gear, 0.0), p.z)
        c, s_ = math.cos(angle), math.sin(angle)
        world = []
        for x, y in points:
            if p.sigma < 0:
                y = -y
            world.append((p.x + x * c - y * s_, p.y + x * s_ + y * c))
        shapes.append((gear, p, [world], p.z))
    # A turned shaft's line: along its family's plus direction, through the extent of its gears seen from +Z
    # (measured from the first gear's At point), SHAFT_OVERRUN past either end.
    turned = {}
    for gear, p, loops, _ in shapes:
        if _seen_end_on(p):
            continue
        base, a = turned.get(p.shaft, (p.centre, p.family))[:2]
        along = [(x - base[0]) * a[0] + (y - base[1]) * a[1] for loop in loops for x, y in loop]
        lo, hi = min(along), max(along)
        if p.shaft in turned:
            lo, hi = min(lo, turned[p.shaft][2]), max(hi, turned[p.shaft][3])
        turned[p.shaft] = (base, a, lo, hi)
    lines = []
    for shaft, (base, a, lo, hi) in turned.items():
        flat = math.hypot(a[0], a[1])          # a shaft tilted out of XY is foreshortened, and so is its overrun
        lo, hi = lo - SHAFT_OVERRUN * flat, hi + SHAFT_OVERRUN * flat
        # along was measured in XY; per unit of along, the line moves (a_x, a_y) / flat² in XY
        k = 1.0 / (flat * flat)
        lines.append((shaft, base[0] + lo * a[0] * k, base[1] + lo * a[1] * k,
                      base[0] + hi * a[0] * k, base[1] + hi * a[1] * k))
    # A carrier's circle: through its planet copies' axes, about the carrier's own axis.
    rings = {}
    for _, p, _, _ in shapes:
        if getattr(p, "carrier", "") and _seen_end_on(p):
            rings.setdefault(p.carrier, []).append((p.x, p.y))
    circles = []
    for carrier, points in rings.items():
        given = (carriers or {}).get(carrier)
        cx, cy = given if given is not None else (sum(x for x, _ in points) / len(points),
                                                  sum(y for _, y in points) / len(points))
        r = sum(math.hypot(x - cx, y - cy) for x, y in points) / len(points)
        circles.append((carrier, cx, cy, r))
    xs = [x for _, _, loops, _ in shapes for loop in loops for x, _ in loop] + \
         [x for _, x0, _, x1, _ in lines for x in (x0, x1)] + \
         [x for _, cx, _, r in circles for x in (cx - r, cx + r)]
    ys = [y for _, _, loops, _ in shapes for loop in loops for _, y in loop] + \
         [y for _, _, y0, _, y1 in lines for y in (y0, y1)] + \
         [y for _, _, cy, r in circles for y in (cy - r, cy + r)]
    for _, p, _, _ in shapes:
        if _seen_end_on(p) and not getattr(p, "bevel", False):
            xs += [p.x + p.outer_radius, p.x - p.outer_radius]
            ys += [p.y + p.outer_radius, p.y - p.outer_radius]
    lo_x, hi_x, lo_y, hi_y = min(xs), max(xs), min(ys), max(ys)
    scale = min((width - 2 * pad) / max(hi_x - lo_x, 1e-9), (height - 2 * pad) / max(hi_y - lo_y, 1e-9))
    off_x = (width - (hi_x - lo_x) * scale) / 2.0 - lo_x * scale
    off_y = (height - (hi_y - lo_y) * scale) / 2.0 + hi_y * scale

    def to_canvas(x, y):
        return off_x + x * scale, off_y - y * scale

    view.scale = scale
    view.planes = sorted({round(h, 6) for _, _, _, h in shapes})
    plane_of = {z: i for i, z in enumerate(view.planes)}
    for gear, p, loops, h in sorted(shapes, key=lambda t: t[3]):
        plane = plane_of[round(h, 6)]
        for loop in loops:
            view.outlines.append((gear, plane, [to_canvas(x, y) for x, y in loop]))
        if p.internal and _seen_end_on(p):
            cx, cy = to_canvas(p.x, p.y)
            view.rims.append((gear, plane, cx, cy, p.outer_radius * scale))
    seen = set()
    ends = {}
    for shaft, x0, y0, x1, y1 in lines:
        a0, b0 = to_canvas(x0, y0)
        a1, b1 = to_canvas(x1, y1)
        view.lines.append((shaft, a0, b0, a1, b1))
        # Named at its family's + end, not the end its gears face (D1: they face the typed Axis, so an X- shaft, or
        # fixture B's S3 typed (-1, 1.732, 0), is named at the other end from the one its gears face).
        ends[shaft] = (a1, b1)
    for _, p, _, _ in shapes:
        if p.shaft in seen:
            continue
        seen.add(p.shaft)
        if p.shaft in ends:
            continue
        view.shafts.append((p.shaft,) + to_canvas(p.x, p.y))
    for carrier, cx, cy, r in circles:
        x, y = to_canvas(cx, cy)
        view.carriers.append((carrier, x, y, r * scale))
        if carrier not in seen:                    # a carrier with no gear of its own still has its cross
            seen.add(carrier)
            view.shafts.append((carrier, x, y))
    ox, oy = to_canvas(0.0, 0.0)
    if 0 <= ox <= width and 0 <= oy <= height:
        view.origin = (ox, oy)
    marks = [(name, x, y) for name, x, y in view.shafts] + [(name, x, y) for name, (x, y) in ends.items()]
    order = {name: i for i, name in enumerate(dict.fromkeys([p.shaft for _, p, _, _ in shapes]
                                                            + [c for c, *_ in circles]))}
    marks.sort(key=lambda m: order.get(m[0], len(order)))
    # Shafts on one line share a cross, and are named there once, every name in order.
    shared: dict = {}
    for name, x, y in marks:
        key = (round(x, 3), round(y, 3))
        if key in shared:
            shared[key][0].append(name)
        else:
            shared[key] = ([name], x, y)
    view.labels = [_place_label(", ".join(names), x, y, view.origin, unit, (width, height) if lines else None)
                   for names, x, y in shared.values()]
    return view
