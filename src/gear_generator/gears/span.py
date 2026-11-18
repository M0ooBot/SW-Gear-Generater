"""The span over k teeth (PLAN-PRINTED §3.0): the base tangent length a person reads with flat caliper jaws.

Package A of F2 (``docs/notes-printed/F2-INTERFACES.md`` §1). :func:`span` gives one derived gear's reading: k, the
span W_n square to the teeth (W_t in the transverse plane) and the jaws' contact diameter, or why there is no figure.
:func:`measured` is the arithmetic back from a user's caliper reading to what their printer adds to each flank and the
backlash per gear that would keep D3's running play. Both are pure: no SolidWorks, no words a user reads.

Package B's ``printout`` calls :func:`span` for each part it plans; package C's ``ui_text.span_rows`` words what it
returns. Neither reads anything here but :class:`SpanReading`, the ``KIND_*`` words and, for the Measured line,
:class:`Measured`.

**The maths** (§3.0; KHK's *Gear Technical Reference*, span measurement, Tables 5.10 and 5.11, with the backlash term
``A_Wk = A_sn cos α_n``; DIN 3960 and ISO 21771 give the same, not checked here). In the transverse plane, from the
app's own drawn sizes::

    W_t = (k − 1) · p_bt + s_bt,   p_bt = π d cos α_t / z,   s_bt = d_b (s_t / d + inv α_t),   inv α = tan α − α
    W_n = W_t · cos β_b,           sin β_b = sin β · cos α_n

``s_t`` is the drawn tooth's transverse thickness at the pitch circle, after backlash and shift
(``SpurDerived.s``; a helical gear's ``section.s``, which ``helical.derive`` thins by ``j / cos β``, so the
app's backlash is a normal one). The same in closed form, which ``tests/test_span.py`` holds this to::

    W_n = m_n cos α_n [ (k − 0.5) π + z inv α_t ] + 2 x m_n sin α_n − j_n cos α_n

**Which k** (§3.0, M1). The jaws' common normal is the base-cylinder tangent, inclined at β_b; the jaws lie ±W_n / 2
along it, so in the transverse plane they touch at ``r_c = √(r_b² + (W_n cos β_b / 2)²)``. The k taken is the one
whose r_c is nearest ``r + x m_n``, the middle of the working flank, among the k whose contact lies on the drawn
involute: not under ``max(flank_start_d, form_d) / 2`` (below it the app draws a radial flank) and not within
:data:`TIP_MARGIN_MM` of the tip radius (a printed tip rounds by about half a line). When the nearest k is outside,
this takes the next one inward or outward that is inside, as §3.0 says; when no k is, there is no figure.

**A helical face too narrow** (§3.0, KHK's "Δb > 3 mm to make a stable measurement"): both jaws must lie whole on the
flanks, so the face (a herringbone's toothed half, ``HelicalDerived.toothed_width``) must be at least
``W_n sin β_b +`` :data:`FACE_MARGIN_MM`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from ..spec import KIND_HERRINGBONE, RECIPE_ARCS, RECIPE_INVOLUTE
from .helical import HelicalDerived
from .spur import BACKLASH_FACTOR, SpurDerived

# What a reading is (SpanReading.kind). Each figure of a reading is 0 unless its kind is KIND_SPAN; needed_face_mm is set
# for KIND_NARROW_FACE alone.
KIND_SPAN = "span"                # a figure: k, W_n (W_t), the contact diameter
KIND_ARCS = "arcs"                # a printed external gear drawn with arcs (recipe B): not one figure (§3.0's ruling)
KIND_NARROW_FACE = "narrow_face"  # a helical gear whose face (a herringbone's half) is under W_n sin beta_b + 3 mm
KIND_NO_CONTACT = "no_contact"    # no k has its contact between the involute's start and 0.2 mm under the tip
KIND_NONE = "none"                # a ring, a sleeve, a bevel gear, a machined gear: no span row at all
KINDS = (KIND_SPAN, KIND_ARCS, KIND_NARROW_FACE, KIND_NO_CONTACT, KIND_NONE)

TIP_MARGIN_MM = 0.2      # §3.0: a contact within this of the tip radius is not on the printed flank
FACE_MARGIN_MM = 3.0     # §3.0, KHK's Δb: a helical face must exceed W_n sin β_b by this to measure
KEPT_PLAY_MM = 0.04      # §3.0, §3.2: the play a flank keeps; D3's 0.3 mm less a printer's 0.10 mm a flank
BACKLASH_FLOOR_MM = 0.1  # §3.0: the Measured line never proposes less a gear (§2.3 found parts overlapping under 0.04)
_EPS = 1e-9              # mm; a figure this near its bound counts as on it


@dataclass(frozen=True)
class SpanReading:
    """What the span over k teeth is for one derived gear (PLAN-PRINTED §3.3).

    - ``kind``: one of :data:`KINDS`.
    - ``k``: the number of teeth spanned (0 unless ``kind`` is ``"span"``).
    - ``w_mm``: the span as the calipers read it, square to the teeth (W_n; a spur gear's W), mm.
    - ``w_t_mm``: the same in the transverse plane (W_t; equal to ``w_mm`` on a spur gear), mm.
    - ``contact_d``: twice the contact radius r_c = sqrt(r_b^2 + (W_n cos beta_b / 2)^2), mm (§3.0, M1).
    - ``needed_face_mm``: for ``"narrow_face"``, the face a measurement needs, W_n sin beta_b + 3 mm (a herringbone
      held to one toothed half, ``HelicalDerived.toothed_width``); 0 otherwise.
    """

    kind: str
    k: int = 0
    w_mm: float = 0.0
    w_t_mm: float = 0.0
    contact_d: float = 0.0
    needed_face_mm: float = 0.0


NONE = SpanReading(KIND_NONE)


# -- the formula ------------------------------------------------------------------------------------------------------


def _inv(angle: float) -> float:
    return math.tan(angle) - angle


def _external_involute(derived: Any) -> Optional[Tuple[SpurDerived, float, float, Optional[float]]]:
    """The transverse section of a gear whose span is taken with jaws, with its helix angle and normal pressure angle
    in radians and the face the jaws have (None on a spur gear); None for any other gear.

    A ``SpurDerived`` is a spur gear, a dog or a hub (``clutch._as_spur``); a ``HelicalDerived`` whose section is
    a ``SpurDerived`` is a helical or herringbone gear. A ring (an ``InternalDerived`` section), a spur ring or a
    sleeve (an ``InternalDerived``) and a bevel gear (a ``BevelDerived``) are not: their span is taken over pins or
    is not of one size (§3.0).
    """
    if isinstance(derived, SpurDerived):
        return derived, 0.0, math.radians(derived.pressure_angle_deg), None
    if isinstance(derived, HelicalDerived) and isinstance(derived.section, SpurDerived):
        face = derived.toothed_width if derived.kind == KIND_HERRINGBONE else derived.section.face_width
        return (derived.section, math.radians(derived.helix_angle_deg),
                math.radians(derived.normal_pressure_angle_deg), face)
    return None


def base_helix_angle(beta: float, alpha_n: float) -> float:
    """β_b, radians, from the helix angle and the normal pressure angle (radians): sin β_b = sin β cos α_n."""
    return math.asin(math.sin(beta) * math.cos(alpha_n))


def span_over(derived: Any, k: int) -> SpanReading:
    """The span over ``k`` teeth of an external involute gear by §3.0's transverse form, whatever its process and
    with no bound applied: the formula alone, as the plan's machined row asks. Its ``kind`` is ``"span"``.

    :func:`span` is what the window and the print list show; this is the figure for any k. ``NONE`` for a gear
    whose span is not taken with jaws (a ring, a sleeve, a bevel gear).
    """
    found = _external_involute(derived)
    if found is None:
        return NONE
    section, beta, alpha_n, _face = found
    return _reading(section, base_helix_angle(beta, alpha_n), k)


def _reading(g: SpurDerived, beta_b: float, k: int) -> SpanReading:
    alpha_t = g.alpha
    base_pitch = math.pi * g.d * math.cos(alpha_t) / g.teeth
    base_thickness = g.db * (g.s / g.d + _inv(alpha_t))
    w_t = (k - 1) * base_pitch + base_thickness
    w_n = w_t * math.cos(beta_b)
    r_c = math.sqrt(g.rb ** 2 + (w_n * math.cos(beta_b) / 2.0) ** 2)
    return SpanReading(KIND_SPAN, k=k, w_mm=w_n, w_t_mm=w_t, contact_d=2.0 * r_c)


def contact_bounds(g: SpurDerived) -> Tuple[float, float]:
    """The radii between which a jaw's contact is on the drawn, printable involute (§3.0): from where the app's
    involute starts, ``max(flank_start_d, form_d) / 2``, to :data:`TIP_MARGIN_MM` under the tip radius."""
    return max(g.flank_start_d, g.form_d) / 2.0, g.da / 2.0 - TIP_MARGIN_MM


def choose(contact_radii: List[Tuple[int, float]], target: float, low: float, high: float) -> Optional[int]:
    """The k whose contact radius is nearest ``target`` among those between ``low`` and ``high``, or None.

    ``contact_radii`` is (k, r_c) for each k tried. The nearest k when it is inside; else, since r_c grows with k,
    the next one outward (if the nearest is under the involute's start) or inward (if it is at the tip) that is
    inside, which is the nearest of those inside. A tie goes to the smaller k.
    """
    inside = [(k, r) for k, r in contact_radii if low - _EPS <= r <= high + _EPS]
    if not inside:
        return None
    return min(inside, key=lambda kr: (abs(kr[1] - target), kr[0]))[0]


# -- what the window and the print list show --------------------------------------------------------------------------


def span(derived: Any, recipe: str) -> SpanReading:
    """The span over k teeth of a derived gear drawn with ``recipe`` (``spec.RECIPE_INVOLUTE`` "A" or
    ``spec.RECIPE_ARCS`` "B"), as PLAN-PRINTED §3.0 gives it.

    ``derived`` is what the gear's kind derives (``gears.kind_for(spec).derive(spec)``): a ``SpurDerived`` (a spur
    gear, a dog, a hub), a ``HelicalDerived`` (helical or herringbone; a ring's section is an ``InternalDerived``), an
    ``InternalDerived`` (a spur ring, a sleeve) or a ``BevelDerived``. Printed is ``derived.printed`` (F1).

    In this order:

    - ``"none"`` for a ring, a sleeve, a bevel gear, anything else that is not an external spur or helical section,
      a machined gear (its Derived panel is unchanged, ``tests/test_printed_rule.py``), and a recipe that is
      neither "A" nor "B";
    - ``"arcs"`` on recipe B: the span is not one figure on arcs (§3.0's ruling);
    - ``"no_contact"`` when no k from 1 to z − 1 has its contact on the drawn involute (:func:`contact_bounds`);
    - ``"narrow_face"`` for a helical or herringbone gear whose face (its toothed half) is under
      ``W_n sin β_b + 3`` mm at the k chosen, with that figure in ``needed_face_mm``;
    - else ``"span"`` with k, W_n, W_t and the contact diameter.

    Pure; raises nothing for a gear any kind derives.
    """
    found = _external_involute(derived)
    if found is None or not derived.printed:
        return NONE
    if recipe == RECIPE_ARCS:
        return SpanReading(KIND_ARCS)
    if recipe != RECIPE_INVOLUTE:
        return NONE
    section, beta, alpha_n, face = found
    beta_b = base_helix_angle(beta, alpha_n)
    readings = {k: _reading(section, beta_b, k) for k in range(1, section.teeth)}
    low, high = contact_bounds(section)
    k = choose([(k, r.contact_d / 2.0) for k, r in readings.items()],
               section.d / 2.0 + section.shift * section.module, low, high)
    if k is None:
        return SpanReading(KIND_NO_CONTACT)
    reading = readings[k]
    if face is not None:
        needed = reading.w_mm * math.sin(beta_b) + FACE_MARGIN_MM
        if face < needed - _EPS:
            return SpanReading(KIND_NARROW_FACE, needed_face_mm=needed)
    return reading


# -- the arithmetic back from a measured span -------------------------------------------------------------------------


@dataclass(frozen=True)
class Measured:
    """What a span read with calipers says (§3.0, the Measured line; §3.2's backlash), for package C to word.

    - ``flank_mm``: e = (reading − W_n) / 2, what the printer added to each flank, square to it; negative when the
      print came out thinner than drawn.
    - ``backlash_mm``: the backlash per gear that keeps :data:`KEPT_PLAY_MM` a flank, j = 2 (e + 0.04) / cos α_n with
      the gear's own normal pressure angle, never under :data:`BACKLASH_FLOOR_MM`.
    - ``floored``: True when the formula gave less than the floor and the floor is proposed instead.
    - ``over_default``: True when the proposed backlash exceeds 0.3 × module for this gear, the case of D3's "never
      more than today's" that is the user's to decide (U4, §3.2).
    """

    flank_mm: float
    backlash_mm: float
    floored: bool
    over_default: bool


def measured(reading: SpanReading, measured_mm: Optional[float], alpha_n_deg: float, module: float) -> Optional[Measured]:
    """The Measured line's figures for a caliper reading of ``measured_mm`` against ``reading``, or None when there
    is nothing to work out (no reading typed, or no span figure to measure against).

    ``alpha_n_deg`` is the gear's normal pressure angle in degrees (a spur gear's own), ``module`` its (normal)
    module in mm. §3.0: ``e = (reading − W) / 2``, ``j = 2 (e + 0.04) / cos α_n``, never under 0.1 mm, said when it
    passes ``0.3 × module``.
    """
    if measured_mm is None or reading.kind != KIND_SPAN:
        return None
    flank = (measured_mm - reading.w_mm) / 2.0
    raw = 2.0 * (flank + KEPT_PLAY_MM) / math.cos(math.radians(alpha_n_deg))
    floored = raw < BACKLASH_FLOOR_MM - _EPS
    backlash = BACKLASH_FLOOR_MM if floored else raw
    return Measured(flank_mm=flank, backlash_mm=backlash, floored=floored,
                    over_default=backlash > BACKLASH_FACTOR * module + _EPS)
