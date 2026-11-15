"""Gear kinds: the maths of each, and the SolidWorks recipe that builds it."""

from .bevel import BevelGear
from .clutch import DogKind, SleeveKind
from .helical import HelicalGear, HerringboneGear
from .internal import InternalHelicalGear, InternalHerringboneGear, InternalSpurGear
from .spur import SpurGear

KINDS = {"spur": SpurGear(), "helical": HelicalGear(), "herringbone": HerringboneGear(), "bevel": BevelGear()}

# A ring of each kind that can have one. Internal is not a kind of its own: it
# is which side of the rim a spur, helical or herringbone gear's teeth are on.
INTERNAL_KINDS = {"spur": InternalSpurGear(), "helical": InternalHelicalGear(),
                  "herringbone": InternalHerringboneGear()}

# Kinds the form shows, greyed, as coming in a later version.
PLANNED_KINDS: tuple = ()


# W8: the workbook's own kinds (W8-PLAN §1.1), never offered by the strip (``gui.KIND_VALUES`` reads ``KINDS``).
WORKBOOK_KINDS = {"sleeve": SleeveKind(), "dog": DogKind()}


def kind_for(spec):
    """The calculation for a form: its kind, and a ring's when its teeth are internal. None when there is none.

    A workbook kind (``WORKBOOK_KINDS``: a sleeve or dog) is found first, before the internal branch, since a
    sleeve is internal and ``INTERNAL_KINDS`` has none."""
    if getattr(spec, "kind", None) in WORKBOOK_KINDS:
        return WORKBOOK_KINDS[spec.kind]
    if str(getattr(spec, "teeth_side", "")).strip().lower() == "internal":
        return INTERNAL_KINDS.get(spec.kind)
    return KINDS.get(spec.kind)


def plan_for(spec, derived, template: str, path: str):
    """The build plan for one gear, exactly as the strip makes it: its kind, its recipe, the template, the path.

    The strip (``gui._plan_single``) and a workbook (``workbook.build``) both
    call this, so a workbook row and the strip build the same part from the
    same values by construction, not by two calls kept in step.
    """
    kind = kind_for(spec)
    return kind.plan(spec, derived, kind.recipe_for(spec), template, path)
