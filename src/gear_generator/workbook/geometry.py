"""Where each gear is, and how far it is turned (docs/PLAN-WORKBOOK.md §3.3; phase W3: parallel shafts).

Positions are in millimetres from the workbook's origin. Phase W3 works out
gearboxes whose shafts are all held by the frame with axes along Z+ or Z-;
anything else (a turned axis, a planet on a carrier) is a later phase's, and
:func:`layout` says so rather than guessing.

**Phase.** Every part is built with a tooth *space* centred on its own +X on
the plane its section is drawn on, its blank extruded from its front face
(local z = 0) along local +Z. A spur's space is on +X at every height. A
helical section turns ``s·360·(z − z_s)/L`` degrees about local +Z at height z
(``s`` +1 for a right hand, :data:`helical.RIGHT_HAND_TURN`; ``L`` the lead),
counted from where it is drawn, ``z_s``: for a helical gear or ring the Profile
Plane, one overrun (a normal module) *behind* the front face, ``z_s = −o``, so
even the front face is turned ``s·360·o/L``; for a herringbone the apex,
``z_s = w/2``, its far half the near half mirrored there
(:meth:`helical.HelicalDerived.turn_at`). A gear turned by θ about its own axis
has, at global height Z, a space centred on the global angle

    g(Z) = σ · (θ + s · 2π · (z_local(Z) − z_s) / L),   z_local = σ · (Z − Z_front)

where σ is +1 for an axis along Z+ and −1 for Z- (a part on a Z- axis is the
same part turned over, which mirrors its angles in the global view). Counting
from the front face instead is wrong by ``s·2π·o/L`` on every helical gear, the
same as sliding each part one overrun along its own axis: two gears facing the
same way slide together and their mesh is unchanged, but two facing opposite
ways slide apart, and that put the teeth into each other. Meshing is
a condition on these global angles at a plane both faces share:

- external, gear q at direction φ from gear p:  g_q = φ + π − π/z_q − (g_p − φ)·z_p/z_q
- a pinion p in a ring r, at direction φ from the ring's centre:
  g_p = φ − π/z_p + (g_r − φ)·z_r/z_p, and back, g_r = φ + (g_p − φ + π/z_p)·z_p/z_r

each modulo one pitch of the gear being placed. At θ_p = φ = 0 the first is
:func:`pair.mesh_angle` and the second :func:`pair.internal_mesh_angle`.
Profile shift is symmetric about the space centre and changes none of this.
The tests hold every formula to the outlines themselves, turned as the part's
build plan turns them (not by this module's own twist): placed meshed they do
not overlap, and turned half a pitch they do.
"""

from __future__ import annotations

import math
import re
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..gears import kind_for
from .model import Gear, GearboxSpec, Shaft
from .schema import FRAME

AXES = {"Z+": 1, "Z-": -1}

Vec3 = Tuple[float, float, float]

# -- W6: turned axes (docs/notes-workbook/W6-PLAN.md §2.1; W6-INTERFACES.md) -----------------------------------
#
# Written at W6's interface commit, because the layout part, the frames, the mates and the worker all rest on them:
# a shaft's direction from its Axis cell, its family (parallel and anti-parallel shafts) and the base frame a gear on
# it is turned from. Pure.

DIRECTIONS: Dict[str, Vec3] = {"X+": (1.0, 0.0, 0.0), "X-": (-1.0, 0.0, 0.0), "Y+": (0.0, 1.0, 0.0),
                               "Y-": (0.0, -1.0, 0.0), "Z+": (0.0, 0.0, 1.0), "Z-": (0.0, 0.0, -1.0)}
CARDINAL_SNAP = 1e-12        # a unit vector this close to a cardinal one, component by component, is that axis
FAMILY_TOLERANCE = 1e-9      # |a × b| below this: two directions are one family (parallel or anti-parallel)


def axis_vector(text: str) -> Vec3:
    """An Axis cell as a unit vector (W6-PLAN §2.1): one of the six words exactly (``Z+ -> (0, 0, 1)``; blank is
    ``Z+``, the column's blank), or three numbers ``"dx, dy, dz"`` (as ``model`` keeps a vector; commas, spaces or
    semicolons between, U+2212 read as minus) normalised. A vector within :data:`CARDINAL_SNAP` of a cardinal one is
    that axis exactly, so ``"0, 0, -2"`` is ``(0, 0, -1)``, ``Z-``'s. Anything else is a ValueError with a sentence."""
    word = (text or "Z+").strip()
    if word in DIRECTIONS:
        return DIRECTIONS[word]
    parts = [p for p in re.split(r"[,\s;]+", word) if p]
    try:
        values = [float(p.replace("\u2212", "-")) for p in parts]
    except ValueError:
        values = []
    if len(values) != 3 or not all(math.isfinite(v) for v in values):
        raise ValueError(f"An axis must be Z+, Z-, X+, X-, Y+, Y- or three numbers dx, dy, dz, not {text!r}.")
    length = math.sqrt(sum(v * v for v in values))
    if length < 1e-9:
        raise ValueError(f"The axis {text!r} has no length, so it points nowhere.")
    unit = (values[0] / length, values[1] / length, values[2] / length)
    for cardinal in DIRECTIONS.values():
        if all(abs(u - c) <= CARDINAL_SNAP for u, c in zip(unit, cardinal)):
            return cardinal
    return unit


def family(direction: Vec3) -> Tuple[Vec3, int]:
    """``(plus direction, ±1)``: the direction of ``direction``'s family (every shaft parallel or anti-parallel to
    it) that counts as plus — the one whose first component of magnitude above 1e-12 is positive, which is the
    cardinal word's ``+`` (``+X``, ``+Y``, ``+Z``) — and +1 when ``direction`` is that one, −1 when it is its
    opposite (W6-PLAN §2.1, D12). ``direction`` is a unit vector (:func:`axis_vector`)."""
    first = next((v for v in direction if abs(v) > 1e-12), None)
    if first is None:
        raise ValueError(f"The direction {tuple(direction)!r} has no length, so it has no family.")
    sign = 1 if first > 0 else -1
    plus = tuple(sign * v + 0.0 for v in direction)
    return (plus[0], plus[1], plus[2]), sign


def base_frame(direction: Vec3) -> Tuple[float, ...]:
    """The rotation, 9 numbers by rows, that carries a gear's part from its own frame to a shaft along
    ``direction`` before any turn about its axis (W6-PLAN §2.1): columns ``[u₀ | a × u₀ | a]``, ``a`` the unit
    direction, ``u₀`` world +X projected onto the plane square to ``a`` and normalised — or world +Y when ``|a × X|``
    is below 1e-9. So ``Z+`` is the identity and ``Z-`` is ``diag(1, −1, −1)`` (W4's ``F₋``) exactly; ``X+`` has
    ``u₀ = +Y``, ``v₀ = +Z``; ``X-`` ``+Y``, ``−Z``; ``Y+`` ``+X``, ``−Z``; ``Y-`` ``+X``, ``+Z``. No ``-0.0`` comes
    back. A gear turned θ about its own axis is placed by ``base_frame(a) · rot_z(θ)`` (``layout.frame``)."""
    a = tuple(float(v) for v in direction)
    length = math.sqrt(sum(v * v for v in a))
    if len(a) != 3 or not math.isfinite(length) or length < 1e-12:
        raise ValueError(f"The direction {tuple(direction)!r} is not three numbers with a length, so no gear can be "
                         "turned onto it.")
    if abs(length - 1.0) > 1e-12:
        a = (a[0] / length, a[1] / length, a[2] / length)
    cross_x = math.hypot(a[1], a[2])                 # |a × X|
    seed = (0.0, 1.0, 0.0) if cross_x < 1e-9 else (1.0, 0.0, 0.0)
    along = sum(s_ * v for s_, v in zip(seed, a))
    u = tuple(s_ - along * v for s_, v in zip(seed, a))
    norm = math.sqrt(sum(v * v for v in u))
    u = tuple(v / norm for v in u)
    v0 = (a[1] * u[2] - a[2] * u[1], a[2] * u[0] - a[0] * u[2], a[0] * u[1] - a[1] * u[0])
    rows = (u[0], v0[0], a[0], u[1], v0[1], a[1], u[2], v0[2], a[2])
    return tuple(r + 0.0 for r in rows)


@dataclass(frozen=True)
class Placed:
    """One gear where the workbook puts it."""

    gear: str
    shaft: str
    x: float                 # the axis, from the origin, mm
    y: float
    z: float                 # the middle of the face, along global Z, mm
    sigma: int               # +1 for an axis along Z+, -1 for Z-
    face: float              # face width, mm
    teeth: int
    module: float
    internal: bool
    derived: object          # the strip's own derived gear (spur, helical, ring)
    hand_sign: int = 0       # +1 right, -1 left; 0 for a spur
    lead: float = 0.0        # mm per turn of the helix; 0 for a spur
    herringbone: bool = False
    spec: object = None      # the strip's GearSpec for this gear, for its outline
    # W6 (W6-PLAN §2.1; B fills them for every axis): ``axis`` the gear's own +Z in world (its shaft's Axis: D1);
    # ``centre`` the world point at its At (a bevel gear's pitch apex: D2); ``family`` its shaft family's plus
    # direction (:func:`family`); ``bevel`` whether it is a bevel gear. ``x, y, z, sigma`` are the At point's
    # coordinates in the family's plus frame and its sense against the plus direction — for the Z family, world
    # x, y, z and W3's σ, unchanged. Every constructor must give ``axis`` and ``centre`` (the defaults are the Z+
    # gear at the origin's).
    axis: Vec3 = (0.0, 0.0, 1.0)
    centre: Vec3 = (0.0, 0.0, 0.0)
    family: Vec3 = (0.0, 0.0, 1.0)
    bevel: bool = False
    # W7 (B fills them; W7-PLAN §2.2): ``row`` the Gears row id this gear is (a copy's row: ``"Planet"``), ``copy``
    # its k (``0`` when its shaft has Copies 1), ``carrier`` the carrier shaft its shaft is mounted on (``""`` on
    # the frame). ``gear`` and ``shaft`` are then the COPY's own ids (``"Planet copy 2"``, ``"P copy 2"``:
    # ``planetary.copy_id``), so every rule that groups by shaft treats each copy as its own shaft; a cell is named
    # through ``row``. For a frame gear ``row`` is ``gear`` once B fills it (``""`` until then means the same).
    row: str = ""
    copy: int = 0
    carrier: str = ""

    @property
    def origin(self) -> Vec3:
        """Where the part's origin sits in world (``layout.frame``'s ``at``): its front face centre, ``centre −
        axis·face/2``, or for a bevel gear its pitch apex, ``centre``. For a Z± gear exactly ``(x, y, z_front)``."""
        if self.bevel:
            return (self.centre[0], self.centre[1], self.centre[2])
        return tuple(c - a * self.face / 2.0 for c, a in zip(self.centre, self.axis))

    @property
    def z_front(self) -> float:
        """Where the part's front face (its origin plane) sits along global Z."""
        return self.z - self.sigma * self.face / 2.0

    @property
    def z_range(self) -> Tuple[float, float]:
        return (self.z - self.face / 2.0, self.z + self.face / 2.0)

    @property
    def tip_radius(self) -> float:
        return self.derived.da / 2.0

    @property
    def outer_radius(self) -> float:
        """The farthest the part reaches from its axis: a ring's rim, any other gear's tip."""
        return getattr(self.derived, "rim", self.derived.da) / 2.0 if self.internal else self.derived.da / 2.0

    def twist(self, z_global: float) -> float:
        """The helix's turn at a global height, about the part's own axis, radians (0 for a spur).

        Counted from where the part's section is drawn, as the part is built
        (:meth:`helical.HelicalDerived.turn_at`): a helical gear's or ring's
        Profile Plane one overrun behind its front face, a herringbone's apex.
        """
        if not self.lead:
            return 0.0
        return math.radians(self.derived.turn_at(self.sigma * (z_global - self.z_front)))

    def space_angle(self, theta: float, z_global: float) -> float:
        """Global angle of a tooth space's centre at a global height, for a part turned θ about its own axis."""
        return self.sigma * (theta + self.twist(z_global))

    def theta_for(self, space: float, z_global: float) -> float:
        """The turn θ that puts a space at a global angle at a global height (the inverse of :meth:`space_angle`)."""
        return self.sigma * space - self.twist(z_global)


@dataclass
class Layout:
    placed: Dict[str, Placed] = field(default_factory=dict)
    later: List[str] = field(default_factory=list)     # sentences: what this phase does not lay out, and why
    problems: Dict[str, str] = field(default_factory=dict)   # gear -> why it could not be placed
    # each gear not in ``placed`` -> why, a few words: every gear row is either placed or here. Keyed by its
    # name, or by its row when it has none (``Gears row 5``) or shares it (``G3 on Gears row 5``).
    left_out: Dict[str, str] = field(default_factory=dict)


# The kinds no phase before W8 lays out, as a few words for a list of what was left out.
LATER_KINDS = {"sleeve": "a sleeve, phase W8", "dog": "a dog ring, phase W8"}


def layout(spec: GearboxSpec, skip_gears=()) -> Layout:
    """Every gear placed, when every shaft is on the frame (W6: along any axis; carriers are W7's). A shaft whose
    Axis cell does not read is the read's error; its gears are left out as "could not be placed"."""
    out = Layout()
    shafts = {s.id: s for s in spec.shafts}
    for shaft in spec.shafts:
        if shaft.mount() != FRAME:
            out.later.append(f"{shaft.id} is mounted on {shaft.mount()}: carriers are laid out in phase W7.")
    names = [g.id for g in spec.gears]

    def label(gear: Gear) -> str:
        if not gear.id:
            return f"Gears row {gear.row}"
        return f"{gear.id} on Gears row {gear.row}" if names.count(gear.id) > 1 else gear.id

    if out.later:
        out.left_out = {label(g): "not laid out until a later phase" for g in spec.gears}
        return out
    cuts = bevel_cuts(spec)
    for gear in spec.gears:
        if gear.kind_word() in LATER_KINDS:
            out.left_out[label(gear)] = LATER_KINDS[gear.kind_word()]
            continue
        if gear.id in skip_gears or not gear.id or names.count(gear.id) > 1:
            out.left_out[label(gear)] = "an error of its own"     # a blank or shared name is the read's error
            continue
        shaft = shafts.get(gear.shaft)
        if shaft is None:
            out.left_out[label(gear)] = "no such shaft"
            continue
        cut = cuts.get(gear.id)
        if gear.kind_word() == "bevel" and (cut is None or cut.problem):
            out.left_out[label(gear)] = "an error of its own"     # its cut's problem is said at its cell
            continue
        try:
            out.placed[gear.id] = _place(spec, gear, shaft, cut)
        except (ValueError, TypeError, ArithmeticError) as exc:
            out.problems[gear.id] = str(exc)
            out.left_out[label(gear)] = "could not be placed"
    return out


def _num(text: str, what: str) -> float:
    value = float(str(text).strip() or "0")
    if not math.isfinite(value):
        raise ValueError(f"{what} is {text!r}, which is not a finite number.")
    return value


def cut_overrides(cut: Optional["BevelCut"]) -> Dict[str, str]:
    """The fields a bevel row's GearSpec takes from its cut (W6-PLAN §2.5.1): its mate's teeth and the shaft angle,
    to nine decimals (``model.Gear.gear_spec(box, **overrides)``); none without a cut."""
    if cut is None or cut.problem:
        return {}
    from ..gears import equations
    return {"mate_teeth": str(cut.mate_teeth), "shaft_angle": equations.literal(round(cut.shaft_angle, 9))}


def _matmul_t(rows: Tuple[float, ...], v: Vec3) -> Vec3:
    """``Bᵀ·v`` for a rotation given 9 numbers by rows: a world vector in that frame."""
    return tuple(rows[j] * v[0] + rows[3 + j] * v[1] + rows[6 + j] * v[2] for j in range(3))   # type: ignore


def _matmul(rows: Tuple[float, ...], v: Vec3) -> Vec3:
    return tuple(rows[3 * i] * v[0] + rows[3 * i + 1] * v[1] + rows[3 * i + 2] * v[2] for i in range(3))  # type: ignore


def _place(spec: GearboxSpec, gear: Gear, shaft: Shaft, cut: Optional["BevelCut"] = None) -> Placed:
    axis = axis_vector(shaft.axis)
    plus, sigma = family(axis)
    gear_spec = gear.gear_spec(spec.box, **cut_overrides(cut))
    kind = kind_for(gear_spec)
    derived = kind.derive(gear_spec)
    helical = gear_spec.kind in ("helical", "herringbone")
    bevel = gear_spec.kind == "bevel"
    point = (_num(shaft.x, f"{shaft.id}'s X"), _num(shaft.y, f"{shaft.id}'s Y"), _num(shaft.z, f"{shaft.id}'s Z"))
    at = _num(gear.at, f"{gear.id}'s At")
    centre = tuple(p + at * a + 0.0 for p, a in zip(point, axis))
    x, y, z = _matmul_t(base_frame(plus), centre)      # the At point in the family's plus frame (Z family: world)
    return Placed(
        gear=gear.id, shaft=shaft.id, x=x + 0.0, y=y + 0.0, z=z + 0.0, sigma=sigma,
        axis=axis, centre=(centre[0], centre[1], centre[2]), family=plus, bevel=bevel,
        face=float(gear.face_width), teeth=int(float(gear.teeth)), module=float(gear.module),
        internal=False if bevel else gear_spec.is_internal(), derived=derived,
        hand_sign=getattr(derived, "hand_sign", 0) if helical else 0,
        lead=getattr(derived, "lead", 0.0) if helical else 0.0,
        herringbone=gear_spec.kind == "herringbone",
        spec=gear_spec,
    )


def _wrap(angle: float, pitch: float) -> float:
    return angle - pitch * math.floor(angle / pitch)


def external_space(g_p: float, z_p: int, z_q: int, phi: float) -> float:
    """Where gear q's space must be, globally, to mesh outside gear p seen at direction φ from p."""
    return _wrap(phi + math.pi - math.pi / z_q - (g_p - phi) * z_p / z_q, 2.0 * math.pi / z_q)


def pinion_space(g_ring: float, z_ring: int, z_pinion: int, phi: float) -> float:
    """Where a pinion's space must be, to mesh inside a ring whose centre sees it at direction φ."""
    return _wrap(phi - math.pi / z_pinion + (g_ring - phi) * z_ring / z_pinion, 2.0 * math.pi / z_pinion)


def ring_space(g_pinion: float, z_pinion: int, z_ring: int, phi: float) -> float:
    """Where a ring's space must be, to mesh with a pinion inside it at direction φ from the ring's centre."""
    return _wrap(phi + (g_pinion - phi + math.pi / z_pinion) * z_pinion / z_ring, 2.0 * math.pi / z_ring)


def mesh_plane(a: Placed, b: Placed) -> float:
    """The global height the two faces share: the middle of their overlap."""
    lo = max(a.z_range[0], b.z_range[0])
    hi = min(a.z_range[1], b.z_range[1])
    return (lo + hi) / 2.0


def phases(spec: GearboxSpec, placed: Dict[str, Placed], with_conflicts: bool = False,
           meshes_: Optional[Dict[Tuple[str, str], "MeshGeometry"]] = None):
    """θ for every gear reachable through the meshes, radians; with ``with_conflicts``, also the loops that
    do not close.

    Each train starts from a gear on an input shaft when it has one (θ = 0),
    else its first gear. Gears on one shaft turn together but each part keeps
    its own θ: a compound pair's second gear is placed by the mesh it is in,
    since nothing fixes one to the other until W5's lock. A gear reached a
    second way must agree, to a hundredth of its pitch; one that does not is
    a loop that does not close, reported as ``(gear, the gear asking otherwise)``.
    """
    meshes: Dict[str, List[str]] = {}
    for mesh in spec.meshes:
        if mesh.a in placed and mesh.b in placed:
            meshes.setdefault(mesh.a, []).append(mesh.b)
            meshes.setdefault(mesh.b, []).append(mesh.a)
    inputs = {s.id for s in spec.shafts if s.role == "input"}
    starts = [g for g in placed if placed[g].shaft in inputs] + list(placed)
    theta: Dict[str, float] = {}
    conflicts: List[Tuple[str, str]] = []
    for start in starts:
        if start in theta:
            continue
        theta[start] = 0.0
        queue = deque([start])
        while queue:
            p = queue.popleft()
            for q in meshes.get(p, []):
                turned = None
                if not parallel(placed[p], placed[q]):
                    turned = (meshes_ or {}).get((p, q)) or (meshes_ or {}).get((q, p))
                    if turned is None or turned.problem:
                        try:
                            turned = mesh_geometry(placed[p], placed[q])
                        except (ValueError, ArithmeticError, AttributeError):
                            continue
                    if turned.problem:
                        continue
                    # The contact is shared and the sense symmetric (c = ±1), so either orientation serves.
                    wanted = turned_against(placed[p], theta[p], placed[q], turned)
                else:
                    wanted = place_against(placed[p], theta[p], placed[q])
                if q in theta:
                    pitch = 2.0 * math.pi / placed[q].teeth
                    off = (wanted - theta[q]) % pitch
                    if min(off, pitch - off) > pitch / 100.0 and (q, p) not in conflicts and (p, q) not in conflicts:
                        conflicts.append((q, p))
                    continue
                theta[q] = wanted
                queue.append(q)
    return (theta, conflicts) if with_conflicts else theta


def place_against(p: Placed, theta_p: float, q: Placed) -> float:
    """θ for gear q so it meshes with gear p, already turned θ_p."""
    plane = mesh_plane(p, q)
    g_p = p.space_angle(theta_p, plane)
    if q.internal and not p.internal:          # p is the pinion, q the ring around it
        phi = math.atan2(p.y - q.y, p.x - q.x)
        g_q = ring_space(g_p, p.teeth, q.teeth, phi)
    elif p.internal and not q.internal:        # q is the pinion inside ring p
        phi = math.atan2(q.y - p.y, q.x - p.x)
        g_q = pinion_space(g_p, p.teeth, q.teeth, phi)
    else:
        phi = math.atan2(q.y - p.y, q.x - p.x)
        g_q = external_space(g_p, p.teeth, q.teeth, phi)
    return q.theta_for(g_q, plane)


def centre_distance(a: Placed, b: Placed) -> float:
    return math.hypot(b.x - a.x, b.y - a.y)


def faces_overlap(a: Placed, b: Placed) -> float:
    """How much two faces share along Z, mm (negative: the gap between them)."""
    return min(a.z_range[1], b.z_range[1]) - max(a.z_range[0], b.z_range[0])


def extent(placed: Dict[str, Placed]) -> Optional[Tuple[Tuple[float, float], ...]]:
    """The box the placed gears fill, ``((x from, x to), (y from, y to), (z from, z to))`` in mm from the origin,
    or None.

    Across X and Y it is each gear's outside diameter — the tip circle, or a
    ring's rim — and along Z its face. Shafts, bores and a housing are not in it,
    nor any gear not placed (:attr:`Layout.left_out`): a caller saying it as the
    gearbox's size says what that leaves out.
    """
    if not placed:
        return None
    gears = list(placed.values())
    if all(g.axis[0] == 0.0 and g.axis[1] == 0.0 for g in gears):
        return ((min(g.x - g.outer_radius for g in gears), max(g.x + g.outer_radius for g in gears)),
                (min(g.y - g.outer_radius for g in gears), max(g.y + g.outer_radius for g in gears)),
                (min(g.z_range[0] for g in gears), max(g.z_range[1] for g in gears)))
    # W6: each gear's bounding cylinder in 3D (its two end circles), so a turned gear counts its true size.
    lows, highs = [math.inf] * 3, [-math.inf] * 3
    for g in gears:
        c = bounding_cylinder(g)
        u = _unit(_sub(c.end, c.start)) if _norm(_sub(c.end, c.start)) > 1e-12 else g.axis
        for i in range(3):
            reach = c.radius * math.sqrt(max(0.0, 1.0 - u[i] * u[i]))
            for end in (c.start, c.end):
                lows[i] = min(lows[i], end[i] - reach)
                highs[i] = max(highs[i], end[i] + reach)
    return tuple((lows[i], highs[i]) for i in range(3))    # type: ignore[return-value]


# -- W6: meshes across turned axes (W6-PLAN §2.3, §2.5, §2.5.1; Agent B writes the bodies) ------------------------

PARALLEL, BEVEL, CROSSED = "parallel", "bevel", "crossed"      # MeshGeometry.kind


@dataclass(frozen=True)
class MeshGeometry:
    """One listed mesh as laid out (:func:`mesh_geometry`; ``checks.Report.meshes``, keyed by the Meshes row's
    ordered pair ``(a, b)``).

    ``kind``: :data:`PARALLEL` (the two axes within 1e-9 rad of parallel), :data:`BEVEL` (both bevel gears),
    :data:`CROSSED` (both helical, on crossed shafts). ``sense``: ``c`` in ``z_a·ω_a + c·z_b·ω_b = 0``, ±1, speeds
    about each gear's own +Z (§2.4: PARALLEL ``a_a·a_b`` outside and ``−a_a·a_b`` inside a ring; BEVEL +1;
    CROSSED ``s_p·s_q``). ``shaft_angle``: degrees between the two gears' own +Z (0 or 180 for PARALLEL).
    ``needed``: PARALLEL / CROSSED the centre distance the teeth make, mm; BEVEL 0 (apexes together). ``placed``:
    PARALLEL the distance between the lines; CROSSED along the common perpendicular; BEVEL between the two apexes.
    ``contact``: a world point — PARALLEL the mid-overlap pitch point, BEVEL the heel pitch point on the common
    generatrix, CROSSED the pitch point on the common perpendicular. ``psi_a``/``psi_b``: the contact's azimuth
    about each gear's own +Z in its base frame (``base_frame``), radians. ``problem``: ``""``, or a sentence when the
    pair cannot be laid out as this kind (§2.5, §2.9)."""

    a: str
    b: str
    kind: str
    sense: int
    shaft_angle: float
    needed: float
    placed: float
    contact: Vec3
    psi_a: float
    psi_b: float
    problem: str = ""


@dataclass(frozen=True)
class BevelCut:
    """What a bevel gear is cut for, from the read alone (:func:`bevel_cuts`; W6-PLAN §2.5.1, D9): its partner's
    teeth, the shaft angle in degrees between the two shafts' Axis directions (exactly 90 for a cardinal pair),
    every bevel gear it is listed with, and ``problem``: ``""`` or the sentence (no mesh, two mates of different
    teeth, two shaft angles), an error at the gear's cell, which then is not planned."""

    mate_teeth: int
    shaft_angle: float
    partners: Tuple[str, ...]
    problem: str = ""


APEX_TOLERANCE = 0.005      # mm: two bevel apexes this close are together (checks.CENTRE_TOLERANCE)
MEET_TOLERANCE = 1e-6       # mm: two lines this close meet, so a crossed pair has no common perpendicular


def _dot(u: Vec3, v: Vec3) -> float:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def _cross(u: Vec3, v: Vec3) -> Vec3:
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def _sub(u: Vec3, v: Vec3) -> Vec3:
    return (u[0] - v[0], u[1] - v[1], u[2] - v[2])


def _add(u: Vec3, v: Vec3, k: float = 1.0) -> Vec3:
    return (u[0] + k * v[0], u[1] + k * v[1], u[2] + k * v[2])


def _norm(u: Vec3) -> float:
    return math.sqrt(_dot(u, u))


def _unit(u: Vec3) -> Vec3:
    n = _norm(u)
    return (u[0] / n, u[1] / n, u[2] / n)


def parallel(a: Placed, b: Placed) -> bool:
    """Whether two gears' axes are parallel or anti-parallel (one family), to :data:`FAMILY_TOLERANCE`."""
    return _norm(_cross(a.axis, b.axis)) < FAMILY_TOLERANCE


def angle_between_axes(a: Placed, b: Placed) -> float:
    """Degrees between the two gears' own +Z (their shafts' Axis directions)."""
    return math.degrees(math.acos(max(-1.0, min(1.0, _dot(a.axis, b.axis)))))


def azimuth(p: Placed, point: Vec3) -> float:
    """A world point's azimuth about gear ``p``'s own +Z in its base frame (``base_frame(p.axis)``), radians."""
    local = _matmul_t(base_frame(p.axis), _sub(point, p.origin))
    return math.atan2(local[1], local[0])


def local_height(p: Placed, point: Vec3) -> float:
    """How far along its own +Z from its part origin a world point is, mm."""
    return _dot(_sub(point, p.origin), p.axis)


def pitch_radius(p: Placed) -> float:
    d = getattr(p.derived, "d", None)
    return d / 2.0 if d is not None else p.teeth * p.module / 2.0


def lines_closest(pa: Vec3, da: Vec3, pb: Vec3, db: Vec3) -> Tuple[Vec3, Vec3]:
    """The feet of the common perpendicular of two non-parallel lines ``p + t·d``."""
    w = _sub(pa, pb)
    a, b, c = _dot(da, da), _dot(da, db), _dot(db, db)
    d, e = _dot(da, w), _dot(db, w)
    den = a * c - b * b
    ta = (b * e - c * d) / den
    tb = (a * e - b * d) / den
    return _add(pa, da, ta), _add(pb, db, tb)


def signed_crossing(a_dir: Vec3, b_dir: Vec3, e: Vec3) -> float:
    """The right-hand turn about ``e`` taking line ``a`` to line ``b``, degrees, reduced to (−90°, 90°]."""
    angle = math.degrees(math.atan2(_dot(_cross(a_dir, b_dir), e), _dot(a_dir, b_dir)))
    return _reduce_line(angle)


def _reduce_line(angle: float) -> float:
    out = math.fmod(angle, 180.0)
    if out <= -90.0:
        out += 180.0
    elif out > 90.0:
        out -= 180.0
    return out + 0.0


def mesh_geometry(a: Placed, b: Placed) -> MeshGeometry:
    """The mesh between two placed gears, classified and measured (W6-PLAN §2.3): PARALLEL by W3's formulas in the
    family's plus frame; BEVEL with the apexes within ``checks.CENTRE_TOLERANCE`` and the contact at the heel pitch
    point; CROSSED by the common perpendicular, its signed crossing against the hands and the contact inside both
    faces. A pair that cannot be laid out as its kind comes back with ``problem`` set, never a raise.

    PARALLEL's ``needed`` is left 0 here: ``checks`` works the centre distance out with the shifts (and a ring's
    working distance) as W3 and the ring checks do, and fills it in. Whether the apexes meet, the crossing angle
    against the hands and the contact inside the faces are measured here and judged in ``checks``."""
    if parallel(a, b):
        same = _dot(a.axis, b.axis) > 0
        ring = a.internal != b.internal
        sense = (1 if same else -1) * (-1 if ring else 1)
        placed_at = centre_distance(a, b)
        phi = math.atan2(b.y - a.y, b.x - a.x)
        r = pitch_radius(a)
        sign = -1.0 if (b.internal and not a.internal) else 1.0
        height = mesh_plane(a, b)
        local = (a.x + sign * r * math.cos(phi), a.y + sign * r * math.sin(phi), height)
        contact = _matmul(base_frame(a.family), local)
        return MeshGeometry(a.gear, b.gear, PARALLEL, sense, 0.0 if same else 180.0, 0.0, placed_at, contact,
                            azimuth(a, contact), azimuth(b, contact))
    shaft_angle = angle_between_axes(a, b)
    if a.bevel and b.bevel:
        w = _unit(_sub(b.axis, tuple(_dot(b.axis, a.axis) * v for v in a.axis)))
        delta = math.radians(a.derived.delta)
        radius = a.derived.cone_distance
        contact = _add(a.centre, _add(tuple(math.cos(delta) * v for v in a.axis), w, math.sin(delta)), radius)
        return MeshGeometry(a.gear, b.gear, BEVEL, 1, shaft_angle, 0.0, _norm(_sub(b.centre, a.centre)), contact,
                            azimuth(a, contact), azimuth(b, contact))
    helical = a.lead and b.lead and not a.herringbone and not b.herringbone
    if not helical or a.bevel or b.bevel:
        return MeshGeometry(a.gear, b.gear, BEVEL if (a.bevel or b.bevel) else CROSSED, 1, shaft_angle, 0.0, 0.0,
                            a.centre, 0.0, 0.0, problem="kind")
    n = _cross(a.axis, b.axis)
    foot_a, foot_b = lines_closest(a.centre, a.axis, b.centre, b.axis)
    gap = _sub(foot_b, foot_a)
    distance = _norm(gap)
    if distance < MEET_TOLERANCE:
        return MeshGeometry(a.gear, b.gear, CROSSED, 1, shaft_angle, pitch_radius(a) + pitch_radius(b), 0.0,
                            foot_a, 0.0, 0.0, problem="meet")
    e = _unit(gap)
    contact = _add(foot_a, e, pitch_radius(a))
    psi_a = azimuth(a, contact)
    t_local = _tooth_direction(a, psi_a)
    t = _matmul(base_frame(a.axis), t_local)
    s_b = 1 if _dot(b.axis, t) > 0 else -1
    del n
    return MeshGeometry(a.gear, b.gear, CROSSED, s_b, shaft_angle, pitch_radius(a) + pitch_radius(b), distance,
                        contact, psi_a, azimuth(b, contact))


def _tooth_direction(p: Placed, psi: float) -> Vec3:
    """The tooth line's direction on ``p``'s pitch cylinder at azimuth ``psi`` in its base frame, per mm of its own
    z (``crossed.tooth_direction``; a turn about the axis does not change it)."""
    from ..gears import crossed
    return crossed.tooth_direction(p.derived, math.degrees(psi))


def turned_against(p: Placed, theta_p: float, q: Placed, geometry_: MeshGeometry) -> float:
    """θ for gear q so it meshes with gear p across turned axes (W6-PLAN §2.3): with ``g`` each gear's tooth-space
    angle at the contact in its own frame (θ plus its helix twist there), ``ψ`` the contact's azimuth in its base
    frame and ``k = −c·z_p/z_q``, ``g_q = ψ_q + π/z_q + k·(g_p − ψ_p)`` modulo q's pitch."""
    contact = geometry_.contact
    psi_p, psi_q = azimuth(p, contact), azimuth(q, contact)
    g_p = theta_p + _twist_local(p, local_height(p, contact))
    k = -geometry_.sense * p.teeth / q.teeth
    g_q = _wrap(psi_q + math.pi / q.teeth + k * (g_p - psi_p), 2.0 * math.pi / q.teeth)
    return g_q - _twist_local(q, local_height(q, contact))


def _twist_local(p: Placed, local_z: float) -> float:
    if not p.lead:
        return 0.0
    return math.radians(p.derived.turn_at(local_z))


def bevel_cuts(spec: GearboxSpec) -> Dict[str, BevelCut]:
    """Every bevel gear's mate teeth and shaft angle, from its Meshes rows and the two shafts' Axis cells, keyed by
    gear id (W6-PLAN §2.5.1). Pure and from the read alone, since ``build.plan_parts`` needs it before anything is
    laid out.

    The partners are the gears it is listed with; the shaft angle is the angle between the two shafts' Axis
    directions (each gear's own +Z: D1), so a cardinal pair is exactly 90°. A gear listed with nothing, with two
    partners of different teeth, or across two shaft angles has a ``problem``; a partner whose shaft or teeth do not
    read is left out (its own error says why)."""
    gears = {g.id: g for g in spec.gears if g.id}
    shafts = {s.id: s for s in spec.shafts if s.id}

    def axis_of(gear: Gear) -> Optional[Vec3]:
        shaft = shafts.get(gear.shaft)
        if shaft is None:
            return None
        try:
            return axis_vector(shaft.axis)
        except ValueError:
            return None

    def teeth_of(gear: Gear) -> Optional[int]:
        try:
            value = float(str(gear.teeth).strip())
        except ValueError:
            return None
        return int(value) if value == int(value) and value > 0 else None

    out: Dict[str, BevelCut] = {}
    for gear in spec.gears:
        if gear.kind_word() != "bevel" or not gear.id:
            continue
        mine = axis_of(gear)
        partners: List[str] = []
        found: List[Tuple[str, int, float]] = []
        for mesh in spec.meshes:
            if gear.id not in (mesh.a, mesh.b) or mesh.a == mesh.b:
                continue
            other = gears.get(mesh.b if mesh.a == gear.id else mesh.a)
            if other is None:
                continue
            partners.append(other.id)
            theirs, teeth = axis_of(other), teeth_of(other)
            if mine is None or theirs is None or teeth is None:
                continue
            angle = math.degrees(math.acos(max(-1.0, min(1.0, _dot(mine, theirs)))))
            found.append((other.id, teeth, angle))
        if not partners:
            out[gear.id] = BevelCut(0, 0.0, (), problem=(
                f"{gear.id} is a bevel gear that meshes nothing; its shape depends on the gear it meshes with, so list "
                "its mesh on the Meshes sheet."))
            continue
        if not found:
            out[gear.id] = BevelCut(0, 0.0, tuple(partners))
            continue
        teeth = sorted({t for _, t, _ in found})
        angles: List[float] = []
        for _, _, angle in found:
            if not any(abs(angle - seen) <= 1e-9 for seen in angles):
                angles.append(angle)
        problem = ""
        if len(teeth) > 1:
            listed = [f"{g} ({t} teeth)" for g, t, _ in found]
            problem = (f"{gear.id} is a bevel gear listed with {_and(listed)}; a bevel gear is cut for one mate's tooth "
                       "count.")
        elif len(angles) > 1:
            problem = (f"{gear.id} is a bevel gear listed across shafts at {_and([_deg(x) + '°' for x in angles])}; a "
                       "bevel gear is cut for one shaft angle.")
        out[gear.id] = BevelCut(found[0][1], found[0][2], tuple(partners), problem)
    return out


def _deg(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _and(items: List[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


# -- bounding cylinders (W6-PLAN §2.5, D8, review M5) ----------------------------------------------------------


@dataclass(frozen=True)
class Cylinder:
    """A gear's true solid bounding cylinder: its own axis from ``start`` to ``end`` (world), and ``radius``."""

    start: Vec3
    end: Vec3
    radius: float


def bounding_cylinder(p: Placed) -> Cylinder:
    """Radius the outside radius (a ring's rim; a bevel's largest radial extent in ``bevel.blank_points``), span the
    face, or a bevel's blank from its nearest to its farthest point along the axis, from the apex."""
    if p.bevel:
        from ..gears import bevel as bevel_gears
        points = bevel_gears.blank_points(p.derived).loop()
        axial = [pt[1] for pt in points]
        radius = max(abs(pt[0]) for pt in points)
        return Cylinder(_add(p.centre, p.axis, min(axial)), _add(p.centre, p.axis, max(axial)), radius)
    return Cylinder(p.origin, _add(p.origin, p.axis, p.face), p.outer_radius)


def _project_cylinder(c: Cylinder, point: Vec3) -> Vec3:
    """The point of the solid cylinder nearest ``point``."""
    axis = _sub(c.end, c.start)
    length = _norm(axis)
    if length < 1e-12:
        u = (0.0, 0.0, 1.0)
        t = 0.0
    else:
        u = (axis[0] / length, axis[1] / length, axis[2] / length)
        t = max(0.0, min(length, _dot(_sub(point, c.start), u)))
    foot = _add(c.start, u, t)
    radial = _sub(_sub(point, c.start), tuple(_dot(_sub(point, c.start), u) * v for v in u))
    r = _norm(radial)
    if r <= c.radius or r < 1e-15:
        return _add(foot, radial)
    return _add(foot, radial, c.radius / r)


def solid_gap(a: Cylinder, b: Cylinder, iterations: int = 20000) -> float:
    """The least distance between two solid cylinders (a segment is one of radius 0), mm; 0 when they overlap.

    Alternating projections between the two convex solids (each step the nearest point of one to the other's
    last point), started from the pair of their axes' closest points: it converges to a pair of nearest points,
    which the tests hold against dense sampling."""
    mid_a = _add(a.start, _sub(a.end, a.start), 0.5)
    mid_b = _add(b.start, _sub(b.end, b.start), 0.5)
    pb = _project_cylinder(b, mid_a)
    pa = _project_cylinder(a, pb)
    last = math.inf
    for _ in range(iterations):
        pb = _project_cylinder(b, pa)
        pa = _project_cylinder(a, pb)
        gap = _norm(_sub(pa, pb))
        if gap < 1e-12 or last - gap < 1e-13:
            break
        last = gap
    del mid_b
    return _norm(_sub(pa, pb))


def cylinder_gap(a: Placed, b: Placed) -> float:
    """The least distance, mm, between the two gears' true solid bounding cylinders (W6-PLAN §2.5, D8, review M5):
    each about its own axis, radius its outside radius (a ring's rim, a bevel's largest radial extent in
    ``bevel.blank_points``), axial span its face (a bevel's blank from its nearest to its farthest point along the
    axis, from the apex). 0 when they overlap.

    Worked out numerically, by alternating projections between the two convex solids (:func:`solid_gap`), not by
    closed forms; the tests hold it to dense sampling and to the plan's fixture clearances (to 0.1 mm)."""
    return solid_gap(bounding_cylinder(a), bounding_cylinder(b))


def shaft_span(placed: Dict[str, Placed], shaft: str) -> Optional[Cylinder]:
    """A shaft as the span of its own gears (W6-PLAN §2.5): the segment of its axis from the nearest to the farthest
    point of its gears' bounding cylinders, as a cylinder of radius 0; None for a shaft with no placed gear."""
    gears = [p for p in placed.values() if p.shaft == shaft]
    if not gears:
        return None
    axis, point = gears[0].axis, gears[0].centre
    ts: List[float] = []
    for g in gears:
        c = bounding_cylinder(g)
        for end in (c.start, c.end):
            ts.append(_dot(_sub(end, point), axis))
    return Cylinder(_add(point, axis, min(ts)), _add(point, axis, max(ts)), 0.0)


def expand_meshes(spec: GearboxSpec, placed: Dict[str, Placed]) -> Tuple[Tuple[str, str], ...]:
    """The listed meshes at copy level (W7-PLAN §2.2), in Meshes-sheet order and copy order within a row: ``Sun–
    Planet`` with three copies becomes ``(Sun, Planet copy 1)``, ``(Sun, Planet copy 2)``, ``(Sun, Planet copy 3)``,
    each pair in its Meshes row's order. Everything that takes "the listed meshes" takes this list. Agent B writes
    it."""
    raise ValueError("Meshes with planet copies are not listed copy by copy by this version of Gear Generator yet, so "
                     "this workbook is not laid out.")
