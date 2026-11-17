"""The workbook's sleeve and dog kinds (phase W8; W8-PLAN §1.1, J1-J3).

A dog is an external spline ring: the strip's spur plan at the row's teeth, module, pressure angle and face. A
sleeve is an internal spline ring: the strip's internal spur plan. Each kind delegates ``derive``, ``validate``,
``variables``, ``outline`` and ``plan`` to ``SpurGear`` / ``InternalSpurGear`` on the spec with ``kind="spur"``
(and ``teeth_side="internal"`` for the sleeve), writes its own kind word in the kind custom property, and adds the
clutch rules as errors at their cells (a sleeve with Side external, a dog with Side internal, a Helix angle or a
Profile shift on either). No fork groove, hub, chamfer or synchro cone (J1); no pressure angle of its own (J2).

W9b (ISSUE-1-PLAN §2.2, §2.4, K8, K10; W9B-INTERFACES §3, §4): a sleeve may have two toothed bands, one at each end of
its face, and between them a relief bore of diameter m(z + 3) — the internal ring's plan unchanged, then three
globals and a loft cut between two circles on two reference planes (:func:`relief_ops`); and a **hub** is a third
kind, an external spline ring as a dog is, which carries a sleeve on its shaft.

Registered in ``gears.WORKBOOK_KINDS`` only, never in ``KINDS``, so the strip never offers them
(``gui.KIND_VALUES``). Pinned in W8's interface commit (``docs/notes-workbook/W8-INTERFACES.md``); Agent B writes
the bodies. Until then each refuses with a sentence, as a refused workbook row does.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import List, Optional, Tuple

from .. import findings
from ..spec import InputError
from . import equations
from .base import (ERROR, ORIGIN, AddGlobal, Circle, CloseSketch, CustomProperty, Diagnostic, Dimension, GlobalVariable,
                   LinkDimension, LoftCut, Op, OpenSketch, RefPlane, Relation)
from .helical import _flip_for
from .internal import InternalSpurGear
from .properties import property_ops
from .spur import FACE_WIDTH, MODULE, TEETH, TEETH_PATTERN, SpurGear

SLEEVE, DOG, HUB = "sleeve", "dog", "hub"

# W9b: a banded sleeve's globals and relief features (W9B-INTERFACES §4).
START_BAND = "Start Band"
END_BAND = "End Band"
RELIEF_DIAMETER = "Relief Diameter"
RELIEF_TEETH = 3.0                       # the relief's diameter is m(z + 3): 0.5 m a side over a dog's tip m(z + 2)
RELIEF_START_PLANE = "Relief Start Plane"
RELIEF_END_PLANE = "Relief End Plane"
RELIEF_START_SKETCH = "Relief Start Sketch"
RELIEF_END_SKETCH = "Relief End Sketch"
RELIEF = "Relief"


def _q(name: str) -> str:
    return equations.quote(name)


def _num(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def relief_diameter(module: float, teeth: int) -> float:
    """m(z + 3): above the sleeve's root at either tooth depth (m(z + 2.8), m(z + 2.5)), 0.5 m a side over a dog's tip."""
    return module * (teeth + RELIEF_TEETH)


def relief_globals(bands: Tuple[float, float]) -> List[GlobalVariable]:
    """The banded sleeve's three globals, after the ring's: ``Start Band``, ``End Band``, ``Relief Diameter``."""
    return [GlobalVariable(START_BAND, equations.literal(bands[0])),
            GlobalVariable(END_BAND, equations.literal(bands[1])),
            GlobalVariable(RELIEF_DIAMETER, f"( {_q(TEETH)} + {_num(RELIEF_TEETH)} ) * {_q(MODULE)}")]


def relief_ops(face: float, bands: Tuple[float, float], diameter: float) -> List[Op]:
    """The relief, after the teeth's pattern: two planes parallel to the Front plane at the start band and at the face
    less the end band (each linked to its globals), a circle of the relief's diameter on each, and a loft cut
    through the two (W9B-INTERFACES §4)."""
    ez = findings.EXTRUDE_Z_SIGN
    r = diameter / 2.0
    lean = math.radians(-45.0)
    out: List[Op] = []
    ends = ((RELIEF_START_PLANE, bands[0], _q(START_BAND), "relief_start", RELIEF_START_SKETCH),
            (RELIEF_END_PLANE, face - bands[1], f"{_q(FACE_WIDTH)} - {_q(END_BAND)}", "relief_end", RELIEF_END_SKETCH))
    for name, offset, expression, ident, _sketch in ends:
        out.append(RefPlane(f"{ident}_plane", name, 1, offset, _flip_for(ez * offset)))
        out.append(LinkDimension(f"Offset@{name}", expression))
    for _name, _offset, _expression, ident, sketch in ends:
        circle = f"{ident}_circle"
        out += [
            OpenSketch(ident, f"{ident}_plane"),
            Circle(circle, (0.0, 0.0), r),
            Relation("coincident", (f"{circle}.centre", ORIGIN)),
            Dimension("Relief", (circle,), (r * 1.2 * math.cos(lean), r * 1.2 * math.sin(lean)), diameter),
            CloseSketch(ident, sketch),
            LinkDimension(f"Relief@{sketch}", _q(RELIEF_DIAMETER)),
        ]
    out.append(LoftCut("relief_cut", RELIEF, ("relief_start", "relief_end")))
    return out


class _Clutch:
    """What the two kinds share: the delegate on the spec as a spur, and the clutch rules (J3)."""

    kind = ""
    _delegate = SpurGear
    _side = "external"

    def __init__(self) -> None:
        self._base = self._delegate()
        self.recipes = self._base.recipes
        self.default_recipe = self._base.default_recipe

    def _as_spur(self, spec):
        """The spec as the delegate builds it: a spur, outside for a dog and inside for a sleeve, with no helix and
        no shift (each said as an error by :meth:`validate` when typed)."""
        return replace(spec, kind="spur", teeth_side=self._side, helix_angle="", profile_shift="0")

    def recipe_for(self, spec) -> str:
        return self._base.recipe_for(self._as_spur(spec))

    def derive(self, spec):
        """``SpurGear`` / ``InternalSpurGear``'s ``derive`` on the spec as a spur."""
        return self._base.derive(self._as_spur(spec))

    def validate(self, spec, derived=None) -> List[Diagnostic]:
        """The clutch rules as errors at their cells (J3) — the Side, a Helix angle, a Profile shift — then the
        delegate's diagnostics on the spec as a spur."""
        out: List[Diagnostic] = []
        side = str(getattr(spec, "teeth_side", "") or "external")
        if side != self._side:
            where = "inside" if self._side == "internal" else "outside"
            out.append(Diagnostic(ERROR, f"A {self.kind}'s teeth are {where}: set its Side to {self._side}.",
                                  "teeth_side"))
        if str(getattr(spec, "helix_angle", "") or "").strip() not in ("", "0"):
            out.append(Diagnostic(ERROR, f"A {self.kind} has straight teeth: clear its Helix angle.", "helix_angle"))
        try:
            shifted = float(str(getattr(spec, "profile_shift", "") or "0")) != 0.0
        except ValueError:
            shifted = True
        if shifted:
            other = "dog" if self.kind == SLEEVE else "sleeve"
            does = "carries" if self.kind == HUB else "engages"
            out.append(Diagnostic(ERROR, f"A {self.kind} is built unshifted, to fit the {other} it {does}: clear its "
                                         "Profile shift.", "profile_shift"))
        out += self._band_errors(spec)
        return out + list(self._base.validate(self._as_spur(spec), derived))

    def _band_errors(self, spec) -> List[Diagnostic]:
        """A sleeve's bands (W9b); another kind's are said at the workbook row (``workbook.modes.row_errors``)."""
        return []

    def variables(self, spec, derived, trig: str = "degrees"):
        """The delegate's globals (and a banded sleeve's three after them: :meth:`SleeveKind.variables`)."""
        return self._base.variables(self._as_spur(spec), derived)

    def outline(self, spec, derived, recipe: str = ""):
        """The delegate's outline."""
        return self._base.outline(self._as_spur(spec), derived, recipe)

    def plan(self, spec, derived, recipe: str, template: str, path: str):
        """The delegate's plan, its kind custom properties saying this kind's word: so a sleeve or dog plan equals
        the internal spur or spur plan of the same values but for its stem and those properties."""
        base = self._base.plan(self._as_spur(spec), derived, recipe, template, path)
        own = {p.name: p.value for p in property_ops(self.kind, base.recipe, False, [])}
        ops = tuple(CustomProperty(op.name, own[op.name]) if isinstance(op, CustomProperty) and op.name in
                    ("Description", "Gear Kind") and op.name in own else op for op in base.ops)
        return replace(base, ops=ops)


class SleeveKind(_Clutch):
    """An internal spline ring (``kind = "sleeve"``), delegating to ``InternalSpurGear``; with two bands, a relief bore
    between them (W9b)."""

    kind = SLEEVE
    _delegate = InternalSpurGear
    _side = "internal"

    def _band_errors(self, spec) -> List[Diagnostic]:
        """The bands' errors at their cells (ISSUE-1-PLAN §2.4; W9B-INTERFACES §1): a band not more than 0, one band
        given and the other blank, a band as long as the face, two that leave no relief, a typed Rim that does not
        clear the relief's diameter m(z + 3)."""
        if not spec.has_bands():
            return []
        out: List[Diagnostic] = []
        texts = {"start_band": str(spec.start_band).strip(), "end_band": str(spec.end_band).strip()}
        words = {"start_band": "Start band", "end_band": "End band"}
        values = {}
        for key, text in texts.items():
            if not text:
                other = "end_band" if key == "start_band" else "start_band"
                out.append(Diagnostic(ERROR, f"A sleeve with bands has two, one at each end of its face: give "
                                             f"{words[key]} too, or clear {words[other]}.", key))
                continue
            try:
                value = float(text.replace("−", "-"))
            except ValueError:
                out.append(Diagnostic(ERROR, f"{words[key]} must be a number (got {text!r}).", key))
                continue
            if not math.isfinite(value) or value <= 0:
                out.append(Diagnostic(ERROR, f"{words[key]} must be more than 0 mm (got {text!r}).", key))
                continue
            values[key] = value
        try:
            face = spec.face_width_mm()
        except InputError:
            return out
        for key, value in values.items():
            if value >= face:
                out.append(Diagnostic(ERROR, f"{words[key]} of {_num(value)} mm takes the whole {_num(face)} mm face; "
                                             "a band is shorter than the face.", key))
        if out or len(values) < 2:
            return out
        b1, b2 = values["start_band"], values["end_band"]
        if b1 + b2 >= face - 1e-9:
            out.append(Diagnostic(ERROR, f"Bands of {_num(b1)} and {_num(b2)} mm leave no relief on a {_num(face)} mm "
                                         "face: together they must be shorter than the face.", "end_band"))
            return out
        try:
            rim = spec.rim_mm()
            diameter = relief_diameter(spec.module_mm(), spec.teeth_count())
        except InputError:
            return out
        if rim is not None and rim <= diameter + 1e-9:
            out.append(Diagnostic(ERROR, f"A rim of {_num(rim)} mm does not clear the relief bore between the bands, "
                                         f"{_num(diameter)} mm (module × (teeth + 3)); make it bigger.", "rim"))
        return out

    @staticmethod
    def _bands(spec) -> Optional[Tuple[float, float]]:
        try:
            return spec.bands_mm()
        except InputError:
            return None

    def variables(self, spec, derived, trig: str = "degrees"):
        """The ring's globals, and with bands ``Start Band``, ``End Band`` and ``Relief Diameter`` after them: the
        bands are values, so a band changed on a banded sleeve is a value Update."""
        out = list(self._base.variables(self._as_spur(spec), derived))
        bands = self._bands(spec)
        if bands is not None:
            out += relief_globals(bands)
        return out

    def plan(self, spec, derived, recipe: str, template: str, path: str):
        """The unbanded sleeve's plan, and with bands its three globals after the ring's and the relief
        (:func:`relief_ops`) after the teeth's pattern: nothing of the ring's plan changes (W9B-INTERFACES §4)."""
        base = super().plan(spec, derived, recipe, template, path)
        bands = self._bands(spec)
        if bands is None:
            return base
        ops = list(base.ops)
        last_global = max(i for i, op in enumerate(ops) if isinstance(op, AddGlobal))
        added = [AddGlobal(v.name, v.expression, v.radian_expression) for v in relief_globals(bands)]
        ops[last_global + 1:last_global + 1] = added
        count = f"Count@{TEETH_PATTERN}"
        after = next(i for i, op in enumerate(ops) if isinstance(op, LinkDimension) and op.dimension == count)
        ops[after + 1:after + 1] = relief_ops(derived.face_width, bands,
                                              relief_diameter(derived.module, derived.teeth))
        return replace(base, ops=tuple(ops))


class DogKind(_Clutch):
    """An external spline ring (``kind = "dog"``), delegating to ``SpurGear``."""

    kind = DOG
    _delegate = SpurGear


class HubKind(_Clutch):
    """W9b (ISSUE-1-PLAN K8): an external spline ring (``kind = "hub"``) with the row's Bore, as a dog is, on a sleeve's
    own shaft, carrying the sleeve; it engages nothing."""

    kind = HUB
    _delegate = SpurGear
