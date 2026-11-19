"""What a printed tooth can carry: the tooth-root stress of ISO 6336-3's Method B on the tooth as the app draws it.

Stage F4 of PLAN-PRINTED (§5.1, F4-0 and package A). Pure maths: millimetres, newtons, MPa and degrees at the
boundary, radians inside. Nothing here reaches a part, a record, a plan or SolidWorks.

**The stress** is ISO 6336-3's form factor and stress-correction factor by Method B, with the whole load at one
tooth's tip and every other factor 1 (Y_ε, Y_β, K_A, K_v, K_Fβ, K_Fα), so it is a static figure:

    σF = Ft / (b · mn) · YF · YS
    YF = 6 (hF / mn) cos αF / ( (sFn / mn)² cos αn )
    YS = (1.2 + 0.13 L) · qs ^ ( 1 / (1.21 + 2.3 / L) ),     L = sFn / hF,   qs = sFn / (2 ρF)

and what one tooth is rated to take at the allowable σFP is ``Ft,held = σFP · b · mn / (YF · YS)``, with
``T,held = Ft,held · d / 2000`` about its own axis (:func:`holds`, :func:`torque_held`).

**The tooth is the app's, not a hob's.** ISO works sFn, hF and ρF out from the generating rack's trochoid. The app
draws its root as a radial line and a circular fillet (``spur.involute_flank``, ``spur.arc_flank``, and the ring's
``internal.involute_flank`` and ``internal.arc_flank``), so this module takes them from that outline, backlash and
shift included:

* **the critical section** is where the fillet's tangent makes 30° with the tooth's centreline (60° on a ring). The
  fillet is a circle of radius ρ about a known centre C, so that point Q is exact. In a frame turned so the tooth's
  centreline (polar angle π / z: a tooth *space* is centred on +X) is the u axis, the flank below it and the tooth
  toward +v, ``Q = C + ρ (cos (90° + τ), sin (90° + τ))`` outside and ``C + ρ (cos (90° − τ), sin (90° − τ))`` on a
  ring, and ``sFn = 2 |v_Q|``. Q must lie on the drawn arc, or the gear is not rated;
* **ρF** is the drawn fillet's radius: 0.38 × module outside, 0.15 × module on a ring, or the typed Fillet;
* **the load** is the whole of Ft on one tooth's tip corner, at the outer diameter (a ring's tip circle), along the
  drawn flank's normal there: on recipe A the involute's, tangent to the base circle, so ``αF = αa − γa`` outside and
  ``αa + γa`` on a ring (ISO's own relation); on recipe B the flank arc's radius through its centre. αF is the
  normal's angle to the perpendicular of the centreline, and hF is measured along the centreline from the critical
  section to where the normal crosses it.

**A helical or herringbone gear** is rated on ISO's virtual spur gear, ``zn = z / (cos² βb · cos β)`` with
``βb = asin (sin β · cos αn)``, drawn by the app's own routines (``spur.profile``, or ``internal.section`` for a
ring) with the normal module, the normal pressure angle, the gear's normal backlash, its shift and its fillet radius.
Its force and pitch diameter stay transverse: ``d`` is the drawn section's, a helical ring's included (z · mn / cos β,
never z · mn). The fillet is drawn in the transverse section, so in the normal section its radius lies between
ρ cos² β and ρ / cos β; ρ is kept, which moves YS by at most about 3 % at β 20°.

**What is not rated**, with its reason in :attr:`ToothRating.why`: a bevel gear (ISO 10300's virtual gear at the mean
cone is another standard); a ring whose tips lie inside its base circle (``InternalDerived.tip_below_base``, on the
drawn section or a helical ring's virtual ring: its tip corner is on the radial line the app draws there, with no
involute normal to load along; the coordinator's ruling on F4's review, M1); a pointed tooth; a gear whose 30° or 60°
point falls off its drawn fillet; and a tooth that does not draw. :func:`rate` never raises.

**YS past its range.** ISO gives YS for 1 ≤ qs < 8. A ring's 0.15 × module fillet gives qs about 7.8 to 11.3, past it;
the formula is carried on (YS grows with qs, so stopping would understate the stress) and
:attr:`ToothRating.past_range` says so, for every reader of a ring's figure to say. A qs under 1 is taken at 1, on the
safe side.

**Sources.** ISO 6336-3:2006 and :2019, §6.2 (Method B) and the stress-correction factor, through secondary sources
only: MITcalc's ISO 6336 notes for the expressions, excerpts of the 2006 text quoted in search results for the 30° and
60° tangents and YS's range, and the virtual spur gear as ISO 6336-1 has it. The standard itself was not read
(docs/notes-printed/F4-0.md).

**Two known departures from ISO's own figure, both said in F4-0's note.** The 30° section is ISO's convention, not the
beam's worst section: on the app's root the worst reads up to about 7 % above it on small pinions (YS taken at each
point). And the app's tooth, its root a radial line and a fillet rather than a trochoid, reads 15 to 32 % weaker in YF
than ISO's own generated tooth: that is the tooth as drawn and printed, which is the point.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional, Tuple

from ..spec import KIND_HERRINGBONE, RECIPE_ARCS, RECIPE_INVOLUTE
from . import internal, spur
from .base import Point2
from .bevel import BevelDerived
from .helical import HelicalDerived
from .internal import InternalDerived
from .spur import SpurDerived

ALLOWABLE_DEFAULT = 17.0          # MPa: provisional, about half a printed PLA data sheet's 35 MPa within the layers (D7)
TWO_WAY = 0.7                     # the allowance for a tooth loaded in both directions as the gearbox runs (R1)
PLANET_SHARE = 1.25               # K_γ: one planet's load over an even share, two planets or more (H5)
TANGENT_OUTSIDE = 30.0            # degrees: the critical section's tangent to the centreline, an outside gear
TANGENT_RING = 60.0               # degrees: the same on a ring
QS_RANGE = (1.0, 8.0)             # ISO's range for qs, 1 ≤ qs < 8

ON_ARC_TOLERANCE = 1e-9           # radians: how near an end of the drawn fillet Q may fall and still be on it


@dataclass(frozen=True)
class ToothRating:
    """One gear's tooth, rated (or not) by §5.1. mm and degrees; ``y_f``, ``y_s`` and ``q_s`` bare.

    ``why`` is "" when rated, else the reason as a clause that names no gear, for the caller to put the gear's name
    before (*"Ring is not rated: " + why*): it starts in lower case and has no full stop. ``short`` is the same reason
    in a few words, for a row or a list (*tips inside the base circle*). ``teeth`` is z, or zn for a helical gear's
    virtual spur gear; ``module`` is the normal module; ``width`` the toothed width (a herringbone's face less its
    groove); ``d`` the pitch diameter the force is taken at, transverse; ``ring`` whether the teeth are a ring's. Past
    the plan's list (§5.6 item 2): ``short`` and ``ring`` (F4-0's decision 3)."""

    rated: bool
    why: str = ""
    y_f: float = 0.0
    y_s: float = 0.0
    s_fn: float = 0.0
    h_f: float = 0.0
    alpha_f_deg: float = 0.0
    rho_f: float = 0.0
    q_s: float = 0.0
    past_range: bool = False
    module: float = 0.0
    width: float = 0.0
    d: float = 0.0
    teeth: float = 0.0
    short: str = ""
    ring: bool = False


# -- the reasons a gear is not rated (each a clause: the caller names the gear) ---------------------------------------

SHORT_BEVEL = "a bevel gear"
SHORT_TIPS_INSIDE_BASE = "tips inside the base circle"
SHORT_POINTED = "pointed teeth"
SHORT_OFF_FILLET = "section off the fillet"
SHORT_NOT_DRAWN = "tooth not drawn"
SHORT_NOT_A_GEAR = "not a gear rated here"

WHY_BEVEL = ("a bevel gear's tooth tapers along its face, and rating it needs ISO 10300's virtual gear at the mean "
             "cone, which this check does not work out")
WHY_POINTED = ("its teeth come to a point below the outer diameter, so there is no tip corner to load (a pointed tooth "
               "is never built)")
WHY_TIP_ON_RADIAL_LINE = ("its involute starts outside its outer diameter, so its tip is on the radial line under the "
                          "involute and its tip load has no involute to act along")
WHY_NOT_A_GEAR = "only spur, helical and herringbone gears, outside and ring, are rated"


def _mm(value: float) -> str:
    return f"{value:.3f}"


def why_tips_inside_base(da: float, db: float, virtual: bool = False) -> str:
    """M1's clause: *its tips lie inside its base circle (31.000 mm against 31.010), so …* (§5.4's words)."""
    where = " on its virtual spur ring" if virtual else ""
    return (f"its tips lie inside its base circle{where} ({_mm(da)} mm against {_mm(db)}), so the last of each tooth is "
            "a straight radial line and its tip load has no involute to act along")


def why_off_fillet(tangent: float) -> str:
    return (f"the point where its root fillet's tangent makes {tangent:g}° with the tooth's centreline is not on the "
            "fillet as drawn, so its critical section is not defined")


def why_not_drawn(reason: str) -> str:
    reason = str(reason).strip().rstrip(".")
    return f"its tooth could not be drawn ({reason[:1].lower() + reason[1:]})" if reason else "its tooth could not be drawn"


def _not(why: str, short: str, **known: Any) -> ToothRating:
    return ToothRating(rated=False, why=why, short=short, **known)


# -- the plane geometry --------------------------------------------------------------------------------------------


def _turn(p: Point2, angle: float) -> Point2:
    c, s = math.cos(angle), math.sin(angle)
    return (c * p[0] - s * p[1], s * p[0] + c * p[1])


def _unit(p: Point2) -> Point2:
    length = math.hypot(p[0], p[1])
    return (p[0] / length, p[1] / length)


def _on_arc(centre: Point2, a: Point2, b: Point2, q: Point2) -> bool:
    """Whether ``q`` (on the circle about ``centre``) lies on the shorter arc from ``a`` to ``b``."""
    def angle(p: Point2) -> float:
        return math.atan2(p[1] - centre[1], p[0] - centre[0])

    def short(x: float) -> float:
        return (x + math.pi) % (2.0 * math.pi) - math.pi

    whole = short(angle(b) - angle(a))
    part = short(angle(q) - angle(a))
    if whole < 0.0:
        whole, part = -whole, -part
    return -ON_ARC_TOLERANCE <= part <= whole + ON_ARC_TOLERANCE


@dataclass(frozen=True)
class _Tooth:
    """One tooth's drawn root and loaded tip, in the frame of its centreline (u out along it, the flank toward −v)."""

    fillet_centre: Point2
    fillet_ends: Tuple[Point2, Point2]
    rho: float
    tip: Point2
    normal: Point2          # the flank's normal at the tip, unit, toward +v


def _framed(centre: Point2, ends: Tuple[Point2, Point2], rho: float, tip: Point2, normal: Point2,
            teeth: float) -> _Tooth:
    turn = -math.pi / teeth
    n = _turn(normal, turn)
    if n[1] < 0.0:
        n = (-n[0], -n[1])
    return _Tooth(fillet_centre=_turn(centre, turn), fillet_ends=(_turn(ends[0], turn), _turn(ends[1], turn)),
                  rho=rho, tip=_turn(tip, turn), normal=n)


def _outside_tooth(g: SpurDerived, recipe: str) -> Tuple[Optional[_Tooth], str, str]:
    if recipe == RECIPE_ARCS:
        flank = spur.arc_flank(g)
        tip = spur._arc_at_radius(flank.centre, flank.radius, g.ra)
        if tip is None:
            return None, why_not_drawn("its flank arc does not reach the outer diameter"), SHORT_NOT_DRAWN
        normal = _unit((flank.centre[0] - tip[0], flank.centre[1] - tip[1]))
        ends = (flank.flank_touch, flank.root_touch)
    else:
        flank = spur.involute_flank(g)
        if g.flank_start_d > g.da:
            return None, WHY_TIP_ON_RADIAL_LINE, SHORT_NOT_DRAWN
        t = spur.involute_t(g.rb, g.ra)
        tip = spur.involute_point(g.rb, g.phi, t)
        u = t + g.phi
        normal = (-math.sin(u), math.cos(u))          # toward where the involute leaves the base circle
        ends = (flank.line_inner, flank.root_touch)
    return _framed(flank.fillet_centre, ends, g.fillet, tip, normal, g.teeth), "", ""


def _ring_tooth(g: InternalDerived, recipe: str) -> Tuple[Optional[_Tooth], str, str]:
    if recipe == RECIPE_ARCS:
        flank = internal.arc_flank(g)
        tip = internal._arc_at_radius(flank.centre, flank.radius, g.ra)
        if tip is None:
            return None, why_not_drawn("its flank arc does not reach the tip circle"), SHORT_NOT_DRAWN
        normal = _unit((flank.centre[0] - tip[0], flank.centre[1] - tip[1]))
        ends = (flank.flank_touch, flank.root_touch)
    else:
        flank = internal.involute_flank(g)
        t = spur.involute_t(g.rb, g.ra)
        tip = internal.flank_point(g, t)
        u = t + g.phi
        normal = (-math.sin(u), -math.cos(u))          # spur's involute normal, mirrored as the ring's flank is
        ends = (flank.line_outer, flank.root_touch)
    return _framed(flank.fillet_centre, ends, g.fillet, tip, normal, g.teeth), "", ""


def stress_correction(s_fn: float, h_f: float, q_s: float) -> float:
    """ISO 6336-3's YS, ``(1.2 + 0.13 L) · qs ^ (1 / (1.21 + 2.3 / L))`` with ``L = sFn / hF``. A qs under 1 is taken
    at 1, on the safe side; one at 8 or past it is carried on, and the caller says so (:attr:`ToothRating.past_range`)."""
    big_l = s_fn / h_f
    return (1.2 + 0.13 * big_l) * max(q_s, QS_RANGE[0]) ** (1.0 / (1.21 + 2.3 / big_l))


def _section_rating(g: Any, recipe: str, ring: bool, **known: Any) -> ToothRating:
    """§5.1 on one drawn section, outside or ring: a real one, or a helical gear's virtual one."""
    if g.tip_thickness <= 0.0:
        return _not(WHY_POINTED, SHORT_POINTED, ring=ring, **known)
    tooth, why, short = (_ring_tooth if ring else _outside_tooth)(g, recipe)
    if tooth is None:
        return _not(why, short, ring=ring, **known)
    tangent = TANGENT_RING if ring else TANGENT_OUTSIDE
    tau = math.radians(tangent)
    c, rho = tooth.fillet_centre, tooth.rho
    if ring:
        q = (c[0] + rho * math.sin(tau), c[1] + rho * math.cos(tau))      # C + ρ (cos (90° − τ), sin (90° − τ))
    else:
        q = (c[0] - rho * math.sin(tau), c[1] + rho * math.cos(tau))      # C + ρ (cos (90° + τ), sin (90° + τ))
    if not _on_arc(c, tooth.fillet_ends[0], tooth.fillet_ends[1], q):
        return _not(why_off_fillet(tangent), SHORT_OFF_FILLET, ring=ring, **known)
    s_fn = 2.0 * abs(q[1])
    p, n = tooth.tip, tooth.normal
    u_cross = p[0] - p[1] * n[0] / n[1]                  # where the load's line crosses the centreline
    h_f = (q[0] - u_cross) if ring else (u_cross - q[0])
    # αF, the normal's angle to the perpendicular of the centreline: positive as it leans toward the root.
    alpha_f = math.atan2(n[0] if ring else -n[0], n[1])
    if h_f <= 0.0 or s_fn <= 0.0:
        return _not(why_off_fillet(tangent), SHORT_OFF_FILLET, ring=ring, **known)
    m = g.module
    y_f = 6.0 * (h_f / m) * math.cos(alpha_f) / ((s_fn / m) ** 2 * math.cos(g.alpha))
    q_s = s_fn / (2.0 * rho)
    return ToothRating(rated=True, y_f=y_f, y_s=stress_correction(s_fn, h_f, q_s), s_fn=s_fn, h_f=h_f,
                       alpha_f_deg=math.degrees(alpha_f), rho_f=rho, q_s=q_s, past_range=q_s >= QS_RANGE[1],
                       ring=ring, **known)


def virtual_teeth(teeth: float, helix_deg: float, normal_pressure_angle_deg: float) -> float:
    """ISO's virtual spur gear: ``zn = z / (cos² βb · cos β)``, ``βb = asin (sin β · cos αn)``; not rounded."""
    beta = math.radians(helix_deg)
    beta_b = math.asin(math.sin(beta) * math.cos(math.radians(normal_pressure_angle_deg)))
    return teeth / (math.cos(beta_b) ** 2 * math.cos(beta))


def virtual_section(g: HelicalDerived) -> Any:
    """A helical or herringbone gear's (or ring's) virtual spur section, drawn by the app's own routines with zn
    teeth, the normal module, the normal pressure angle, the gear's normal backlash, its shift and its fillet as
    drawn. Its ``d`` is zn · mn, the virtual gear's: the force is never taken there (:attr:`ToothRating.d`)."""
    s = g.section
    zn = virtual_teeth(s.teeth, g.helix_angle_deg, g.normal_pressure_angle_deg)
    if isinstance(s, InternalDerived):
        return internal.section(zn, s.module, g.normal_pressure_angle_deg, s.face_width, None, s.backlash, s.fillet,
                                backlash_typed=s.backlash_typed, fillet_typed=s.fillet_typed, nozzle=s.nozzle)
    return spur.profile(zn, s.module, g.normal_pressure_angle_deg, s.face_width, s.bore, s.backlash, s.fillet,
                        backlash_typed=s.backlash_typed, fillet_typed=s.fillet_typed, shift=s.shift,
                        nozzle=s.nozzle)


def toothed_width(derived: Any) -> float:
    """The width the teeth carry the load over, mm: the face, or a herringbone's face less its groove
    (2 × ``HelicalDerived.toothed_width``)."""
    if isinstance(derived, HelicalDerived) and derived.kind == KIND_HERRINGBONE:
        return 2.0 * derived.toothed_width
    return derived.face_width


def rate(derived: Any, recipe: str = RECIPE_INVOLUTE) -> ToothRating:
    """One derived gear's tooth rated by §5.1, or not rated with its reason. Never raises.

    ``derived`` is what a gear kind's ``derive`` gives (``SpurDerived``, ``InternalDerived``, ``HelicalDerived``,
    ``BevelDerived``); ``recipe`` the recipe it is drawn by, ``"A"`` or ``"B"`` (blank: A). A dog or a hub derives a
    ``SpurDerived`` and would read as a spur gear: their couplings are not meshes, and the callers leave them out
    (§5.1). A crossed pair's gears are helical gears and rate as such: their mesh is not rated (§5.1), which is the
    caller's to say."""
    try:
        return _rate(derived, recipe or RECIPE_INVOLUTE)
    except Exception as exc:      # noqa: BLE001 — never raises (§5.6): a tooth that does not draw is not rated
        return _not(why_not_drawn(str(exc)), SHORT_NOT_DRAWN)


def _rate(derived: Any, recipe: str) -> ToothRating:
    if isinstance(derived, BevelDerived):
        return _not(WHY_BEVEL, SHORT_BEVEL)
    if recipe not in (RECIPE_INVOLUTE, RECIPE_ARCS):
        return _not(why_not_drawn(f"its recipe {recipe!r} is not one the app draws"), SHORT_NOT_DRAWN)
    if isinstance(derived, HelicalDerived):
        section = derived.section
        ring = isinstance(section, InternalDerived)
        virtual = virtual_section(derived)
        known = dict(module=section.module, width=toothed_width(derived), d=section.d, teeth=virtual.teeth)
        if ring and (section.tip_below_base or virtual.tip_below_base):
            on = section if section.tip_below_base else virtual
            return _not(why_tips_inside_base(on.da, on.db, virtual=on is virtual), SHORT_TIPS_INSIDE_BASE,
                        ring=True, **known)
        return _section_rating(virtual, recipe, ring, **known)
    if isinstance(derived, InternalDerived):
        known = dict(module=derived.module, width=derived.face_width, d=derived.d, teeth=derived.teeth)
        if derived.tip_below_base:
            return _not(why_tips_inside_base(derived.da, derived.db), SHORT_TIPS_INSIDE_BASE, ring=True, **known)
        return _section_rating(derived, recipe, True, **known)
    if isinstance(derived, SpurDerived):
        known = dict(module=derived.module, width=derived.face_width, d=derived.d, teeth=derived.teeth)
        return _section_rating(derived, recipe, False, **known)
    return _not(WHY_NOT_A_GEAR, SHORT_NOT_A_GEAR)


def holds(rating: ToothRating, allowable: float = ALLOWABLE_DEFAULT, width: Optional[float] = None,
          two_way: bool = False) -> float:
    """The force one tooth is rated to take at the pitch circle, N: ``σFP · b · mn / (YF · YS)``, at ``width`` (a
    mesh's, no more than the two faces' overlap) or the gear's own toothed width, × :data:`TWO_WAY` when its teeth
    are loaded in both directions as the gearbox runs (an idler or a planet: an allowance for running, never part of a
    figure called *once*, R1). Raises :class:`ValueError` for a gear not rated, which shows *not rated* instead."""
    if not rating.rated:
        raise ValueError(f"This gear is not rated: {rating.why}.")
    b = rating.width if width is None else width
    force = allowable * b * rating.module / (rating.y_f * rating.y_s)
    return force * TWO_WAY if two_way else force


def torque_held(rating: ToothRating, force: float) -> float:
    """The torque a force at the gear's pitch circle makes about its own axis, N·m: ``F · d / 2000``, ``d`` transverse."""
    return force * rating.d / 2000.0


# -- the rounding every reader of a figure shows it with (§5.4: F4-0's to fix) ---------------------------------------


def newtons(force: float) -> str:
    """A force as shown, without its unit: whole newtons from 10 N, to 0.1 N under that (*39*, *230*, *8.6*)."""
    return f"{force:.0f}" if force >= 9.95 else f"{force:.1f}"


def newton_metres(torque: float) -> str:
    """A torque as shown, without its unit: to 0.01 N·m under 10, to 0.1 under 100, whole from 100 (*0.58*, *2.07*,
    *12.3*)."""
    if torque < 9.995:
        return f"{torque:.2f}"
    return f"{torque:.1f}" if torque < 99.95 else f"{torque:.0f}"


def times(ratio: float) -> str:
    """How many times over, to 0.1 (*13.6*)."""
    return f"{ratio:.1f}"


def megapascals(stress: float) -> str:
    """An allowable as shown, without its unit: as few figures as it needs (*17*, *12.5*)."""
    return f"{stress:g}"


def allowable_mpa(text: str) -> float:
    """The Box's Allowable stress as the checks use it, MPa: the figure when it reads as a number above zero, else
    :data:`ALLOWABLE_DEFAULT`: a blank, and a figure that does not read, which ``model._read_box`` says at its cell."""
    raw = str(text or "").strip().replace("−", "-")
    try:
        value = float(raw)
    except ValueError:
        return ALLOWABLE_DEFAULT
    return value if math.isfinite(value) and value > 0.0 else ALLOWABLE_DEFAULT


__all__ = [
    "ALLOWABLE_DEFAULT", "PLANET_SHARE", "QS_RANGE", "TANGENT_OUTSIDE", "TANGENT_RING", "TWO_WAY", "ToothRating",
    "allowable_mpa", "holds", "megapascals", "newton_metres", "newtons", "rate", "stress_correction", "times",
    "torque_held", "toothed_width", "virtual_section", "virtual_teeth",
]
