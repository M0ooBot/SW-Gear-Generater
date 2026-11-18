"""The span over k teeth (PLAN-PRINTED §3.0): the base tangent length a person reads with flat caliper jaws.

**F2-0's interface stub. Package A owns this file and fills** :func:`span` (``docs/notes-printed/F2-INTERFACES.md`` §1).
Until then :func:`span` answers ``"none"`` for every gear, so the form shows no span row and the print list says no
span, and nothing reads as a figure that was never worked out.

Package B's ``printout`` calls :func:`span` for each part it plans; package C's ``ui_text.span_rows`` words what it
returns. Neither reads anything here but :class:`SpanReading` and the ``KIND_*`` words.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# What a reading is (SpanReading.kind). Each figure of a reading is 0 unless its kind is KIND_SPAN; needed_face_mm is set
# for KIND_NARROW_FACE alone.
KIND_SPAN = "span"                # a figure: k, W_n (W_t), the contact diameter
KIND_ARCS = "arcs"                # a printed external gear drawn with arcs (recipe B): not one figure (§3.0's ruling)
KIND_NARROW_FACE = "narrow_face"  # a helical gear whose face (a herringbone's half) is under W_n sin beta_b + 3 mm
KIND_NO_CONTACT = "no_contact"    # no k has its contact between the involute's start and 0.2 mm under the tip
KIND_NONE = "none"                # a ring, a sleeve, a bevel gear, a machined gear: no span row at all
KINDS = (KIND_SPAN, KIND_ARCS, KIND_NARROW_FACE, KIND_NO_CONTACT, KIND_NONE)


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


def span(derived: Any, recipe: str) -> SpanReading:
    """The span over k teeth of a derived gear drawn with ``recipe`` (``spec.RECIPE_INVOLUTE`` "A" or
    ``spec.RECIPE_ARCS`` "B"), as PLAN-PRINTED §3.0 gives it.

    ``derived`` is what the gear's kind derives (``gears.kind_for(spec).derive(spec)``): a ``SpurDerived`` (a spur
    gear, a dog, a hub), a ``HelicalDerived`` (helical or herringbone; a ring's section is an ``InternalDerived``), an
    ``InternalDerived`` (a spur ring, a sleeve) or a ``BevelDerived``. Printed is ``derived.printed`` (F1).

    F2-0's stub: answers ``"none"`` for every gear until package A fills it. Never raises.
    """
    return NONE
