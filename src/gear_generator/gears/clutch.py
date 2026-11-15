"""The workbook's sleeve and dog kinds (phase W8; W8-PLAN §1.1, J1-J3).

A dog is an external spline ring: the strip's spur plan at the row's teeth, module, pressure angle and face. A
sleeve is an internal spline ring: the strip's internal spur plan. Each kind delegates ``derive``, ``validate``,
``variables``, ``outline`` and ``plan`` to ``SpurGear`` / ``InternalSpurGear`` on the spec with ``kind="spur"``
(and ``teeth_side="internal"`` for the sleeve), writes its own kind word in the kind custom property, and adds the
clutch rules as errors at their cells (a sleeve with Side external, a dog with Side internal, a Helix angle or a
Profile shift on either). No fork groove, hub, chamfer or synchro cone (J1); no pressure angle of its own (J2).

Registered in ``gears.WORKBOOK_KINDS`` only, never in ``KINDS``, so the strip never offers them
(``gui.KIND_VALUES``). Pinned in W8's interface commit (``docs/notes-workbook/W8-INTERFACES.md``); Agent B writes
the bodies. Until then each refuses with a sentence, as a refused workbook row does.
"""

from __future__ import annotations

from dataclasses import replace
from typing import List

from .base import ERROR, CustomProperty, Diagnostic
from .internal import InternalSpurGear
from .properties import property_ops
from .spur import SpurGear

SLEEVE, DOG = "sleeve", "dog"


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
            out.append(Diagnostic(ERROR, f"A {self.kind} is built unshifted, to fit the {other} it engages: clear its "
                                         "Profile shift.", "profile_shift"))
        return out + list(self._base.validate(self._as_spur(spec), derived))

    def variables(self, spec, derived, trig: str = "degrees"):
        """The delegate's globals."""
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
    """An internal spline ring (``kind = "sleeve"``), delegating to ``InternalSpurGear``."""

    kind = SLEEVE
    _delegate = InternalSpurGear
    _side = "internal"


class DogKind(_Clutch):
    """An external spline ring (``kind = "dog"``), delegating to ``SpurGear``."""

    kind = DOG
    _delegate = SpurGear
