"""A solved line that lands on itself when a part's values change (W9c's demonstration, run 6 on SolidWorks 2026).

Both involute tooth-space sketches start a short radial line where the fixed involute starts (``I+.start``) and let
SolidWorks solve where it ends:

- the ring's (``internal._space_ops_involute``): ``Li+`` from the flank start to the tip-cap circle, held by "origin on
  Li+" and "Li+.end on cap", m/2 long;
- the external gear's (``spur._space_ops_involute``): ``L+`` from the flank start inward to where the root fillet
  meets it, its end held by the fillet's tangency.

Run 6 measured a ring m1.25 set 55 -> 54 (and 56 -> 55): the new flank start lands 0.024 mm from where ``Li+`` ends
now, 0.038 of its 0.625 mm length, the line starts near zero length, SolidWorks solves its end to the far side of the
origin, ``Tooth Space`` reads code 72 (a self-intersecting contour), and the part stays on that branch: a forced
rebuild does not mend it, nor does setting it back. 55 -> 53 (1.0 of the length), 55 -> 56 (2.0), 50 and 60, and the
routes 55 -> 56 -> 54 and 55 -> 53 -> 54, rebuilt clean; so did Sun 29 -> 30 and 29 -> 28 (external, 2.4 and 0.24).

:func:`line_landings` foresees it from the part's own globals before and after (no spec, no recipe: the sketch's
geometry is a function of ``Base Radius``, ``Flank Offset``, ``Involute t1``, and the tip cap or the root and fillet),
for the worker to route the change through a safe intermediate (``swbuild.update_variables``). Pure.
"""

from __future__ import annotations

import math
from typing import List, Mapping, Optional, Tuple

from .internal import INNER       # only a ring's globals hold it
from .spur import BASE_RADIUS, FILLET, FLANK_OFFSET, ROOT, T1, TIP_CAP

# A landing closer than this fraction of the line's new length is foreseen. Measured failing at 0.038 (the ring, one
# tooth down); measured clean at 0.24 (an external gear, Sun 29 -> 28) and at 1.0 and above (the ring). Conservative:
# a foreseen landing costs one more rebuild, an unforeseen one a part left broken.
LANDING_FRACTION = 0.2

Point = Tuple[float, float]


def _start(values: Mapping[str, float], lower: bool) -> Point:
    """``I+.start``: the involute at ``t = Involute t1``, as ``spur._curve_expressions`` draws it (radians)."""
    br, off, t = values[BASE_RADIUS], values[FLANK_OFFSET], values[T1]
    arg = t + off
    x = br * (math.cos(arg) + t * math.sin(arg))
    y = br * (t * math.cos(arg) - math.sin(arg)) if lower else br * (math.sin(arg) - t * math.cos(arg))
    return x, y


def _along(point: Point, radius: float) -> Point:
    angle = math.atan2(point[1], point[0])
    return radius * math.cos(angle), radius * math.sin(angle)


def _line(values: Mapping[str, float]) -> Optional[Tuple[str, Point, Point]]:
    """The sketch's short solved line ``(name, start, end)`` as the globals place it, or None for globals that are not
    an involute tooth space's."""
    if any(name not in values for name in (BASE_RADIUS, FLANK_OFFSET, T1)):
        return None
    if INNER in values and TIP_CAP in values:              # a ring: Li+ to the tip cap, on the start's radial
        start = _start(values, lower=True)
        return "Li+", start, _along(start, values[TIP_CAP] / 2.0)
    if ROOT in values and FILLET in values:                # an external gear: L+ to where the root fillet meets it
        rf, rho = values[ROOT] / 2.0, values[FILLET]
        if rf * rf + 2.0 * rf * rho < 0.0:
            return None
        start = _start(values, lower=False)
        return "L+", start, _along(start, math.sqrt(rf * rf + 2.0 * rf * rho))
    return None


def line_landings(before: Mapping[str, float], after: Mapping[str, float],
                  fraction: float = LANDING_FRACTION) -> List[Tuple[str, float, float]]:
    """``(line, how far its new start lands from where it ends now, its new length)`` (mm) for the sketch's short
    solved line when the new start lands within ``fraction`` of that length of the old end; else ``[]`` (also for
    globals that are not an involute tooth space's, or values that do not make one)."""
    try:
        old, new = _line(before), _line(after)
    except (KeyError, ValueError, ZeroDivisionError, OverflowError):
        return []
    if old is None or new is None or old[0] != new[0]:
        return []
    name, _, old_end = old
    _, new_start, new_end = new
    length = math.dist(new_start, new_end)
    landed = math.dist(old_end, new_start)
    if not math.isfinite(length) or length <= 0.0 or not math.isfinite(landed):
        return []
    return [(name, landed, length)] if landed < fraction * length else []
