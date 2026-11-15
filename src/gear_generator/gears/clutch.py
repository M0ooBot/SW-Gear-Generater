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

from .internal import InternalSpurGear
from .spur import SpurGear

SLEEVE, DOG = "sleeve", "dog"


class _Clutch:
    """What the two kinds share: the delegate's recipes, and the refusal until B writes the bodies."""

    kind = ""
    _delegate = SpurGear

    def __init__(self) -> None:
        base = self._delegate()
        self.recipes = base.recipes
        self.default_recipe = base.default_recipe

    def _refuse(self):
        raise ValueError(f"A {self.kind} is not built by this version of Gear Generator yet, so its part cannot be "
                         "worked out.")

    def recipe_for(self, spec) -> str:
        return self.default_recipe

    def derive(self, spec):
        """``SpurGear`` / ``InternalSpurGear``'s ``derive`` on the spec as a spur (B)."""
        self._refuse()

    def validate(self, spec, derived=None):
        """The delegate's diagnostics, and the clutch rules as errors at their cells (J3) (B)."""
        self._refuse()

    def variables(self, spec, derived, trig: str = "degrees"):
        """The delegate's globals (B)."""
        self._refuse()

    def outline(self, spec, derived, recipe: str = ""):
        """The delegate's outline (B)."""
        self._refuse()

    def plan(self, spec, derived, recipe: str, template: str, path: str):
        """The delegate's plan, its kind custom property saying this kind's word (B): so a sleeve or dog plan equals
        the internal spur or spur plan of the same values but for its stem and that one property."""
        self._refuse()


class SleeveKind(_Clutch):
    """An internal spline ring (``kind = "sleeve"``), delegating to ``InternalSpurGear``."""

    kind = SLEEVE
    _delegate = InternalSpurGear


class DogKind(_Clutch):
    """An external spline ring (``kind = "dog"``), delegating to ``SpurGear``."""

    kind = DOG
    _delegate = SpurGear
