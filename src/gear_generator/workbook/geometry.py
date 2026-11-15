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


# The kinds no phase before W6 lays out, as a few words for a list of what was left out.
LATER_KINDS = {"bevel": "a bevel gear, phase W6", "sleeve": "a sleeve, phase W8", "dog": "a dog ring, phase W8"}


def layout(spec: GearboxSpec, skip_gears=()) -> Layout:
    """Every gear placed, when every shaft is on the frame with an axis along Z+ or Z-."""
    out = Layout()
    shafts = {s.id: s for s in spec.shafts}
    for shaft in spec.shafts:
        if shaft.mount() != FRAME:
            out.later.append(f"{shaft.id} is mounted on {shaft.mount()}: carriers are laid out in phase W7.")
        elif (shaft.axis or "Z+") not in AXES:
            out.later.append(f"{shaft.id}'s axis is {shaft.axis}: axes other than Z+ and Z- are laid out in "
                             f"phase W6.")
    names = [g.id for g in spec.gears]

    def label(gear: Gear) -> str:
        if not gear.id:
            return f"Gears row {gear.row}"
        return f"{gear.id} on Gears row {gear.row}" if names.count(gear.id) > 1 else gear.id

    if out.later:
        out.left_out = {label(g): "not laid out until a later phase" for g in spec.gears}
        return out
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
        try:
            out.placed[gear.id] = _place(spec, gear, shaft)
        except (ValueError, TypeError) as exc:
            out.problems[gear.id] = str(exc)
            out.left_out[label(gear)] = "could not be placed"
    return out


def _place(spec: GearboxSpec, gear: Gear, shaft: Shaft) -> Placed:
    sigma = AXES[shaft.axis or "Z+"]
    gear_spec = gear.gear_spec(spec.box)
    kind = kind_for(gear_spec)
    derived = kind.derive(gear_spec)
    helical = gear_spec.kind in ("helical", "herringbone")
    z = float(shaft.z or 0) + sigma * float(gear.at or 0)
    x, y = float(shaft.x), float(shaft.y)
    return Placed(
        gear=gear.id, shaft=shaft.id, x=x, y=y, z=z, sigma=sigma,
        axis=(0.0, 0.0, float(sigma)), centre=(x, y, z), family=(0.0, 0.0, 1.0),
        face=float(gear.face_width), teeth=int(float(gear.teeth)), module=float(gear.module),
        internal=gear_spec.is_internal(), derived=derived,
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


def phases(spec: GearboxSpec, placed: Dict[str, Placed], with_conflicts: bool = False):
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
    return ((min(g.x - g.outer_radius for g in gears), max(g.x + g.outer_radius for g in gears)),
            (min(g.y - g.outer_radius for g in gears), max(g.y + g.outer_radius for g in gears)),
            (min(g.z_range[0] for g in gears), max(g.z_range[1] for g in gears)))


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


def mesh_geometry(a: Placed, b: Placed) -> MeshGeometry:
    """The mesh between two placed gears, classified and measured (W6-PLAN §2.3): PARALLEL by W3's formulas in the
    family's plus frame; BEVEL with the apexes within ``checks.CENTRE_TOLERANCE`` and the contact at the heel pitch
    point; CROSSED by the common perpendicular, its signed crossing against the hands and the contact inside both
    faces. A pair that cannot be laid out as its kind comes back with ``problem`` set, never a raise."""
    raise NotImplementedError("W6: Agent B, workbook.geometry.mesh_geometry")


def bevel_cuts(spec: GearboxSpec) -> Dict[str, BevelCut]:
    """Every bevel gear's mate teeth and shaft angle, from its Meshes rows and the two shafts' Axis cells, keyed by
    gear id (W6-PLAN §2.5.1). Pure and from the read alone, since ``build.plan_parts`` needs it before anything is
    laid out."""
    raise NotImplementedError("W6: Agent B, workbook.geometry.bevel_cuts")


def cylinder_gap(a: Placed, b: Placed) -> float:
    """The least distance, mm, between the two gears' true solid bounding cylinders (W6-PLAN §2.5, D8, review M5):
    each about its own axis, radius its outside radius (a ring's rim, a bevel's largest radial extent in
    ``bevel.blank_points``), axial span its face (a bevel's blank from its nearest to its farthest point along the
    axis, from the apex). Closed forms for side against side, each end disc against the other cylinder, and the
    rims; 0 when they overlap. Tested against dense sampling (the fixtures' clearances to 0.1 mm)."""
    raise NotImplementedError("W6: Agent B, workbook.geometry.cylinder_gap")
