"""The sleeve and dog kinds as W8's interface commit registers them (W8-PLAN §1.1, W8-INTERFACES.md §4): found by
``kind_for`` for every caller, never offered by the strip, named ``Sleeve_…`` and ``Dog_…``; their bodies are package
B's, and until then each refuses with a sentence."""

import pytest

from gear_generator import gears, spec as spec_mod
from gear_generator.gears.clutch import DOG, SLEEVE, DogKind, SleeveKind
from gear_generator.spec import GearSpec


def clutch(kind, side="external"):
    return GearSpec(kind=kind, module=1.5, teeth=30, face_width=8.0, teeth_side=side)


def test_the_two_kinds_are_the_workbooks_only():
    assert set(gears.WORKBOOK_KINDS) == {SLEEVE, DOG} == {"sleeve", "dog"}
    assert isinstance(gears.WORKBOOK_KINDS["sleeve"], SleeveKind) and isinstance(gears.WORKBOOK_KINDS["dog"], DogKind)
    assert not set(gears.KINDS) & {"sleeve", "dog"} and not set(gears.INTERNAL_KINDS) & {"sleeve", "dog"}


def test_kind_for_finds_them_first_an_internal_sleeve_included():
    assert gears.kind_for(clutch("sleeve", "internal")) is gears.WORKBOOK_KINDS["sleeve"]
    assert gears.kind_for(clutch("dog")) is gears.WORKBOOK_KINDS["dog"]
    assert gears.kind_for(clutch("spur")) is gears.KINDS["spur"]
    assert gears.kind_for(clutch("spur", "internal")) is gears.INTERNAL_KINDS["spur"]


def test_the_strip_never_offers_them():
    from gear_generator import gui
    assert "sleeve" not in gui.KIND_VALUES and "dog" not in gui.KIND_VALUES
    assert gui.KIND_VALUES == tuple(gears.KINDS) + tuple(gears.PLANNED_KINDS)


def test_their_stems_are_sleeve_and_dog_never_a_spur_gears_or_rings():
    assert spec_mod.default_stem(clutch("sleeve", "internal")) == "Sleeve_m1.5_N30"
    assert spec_mod.default_stem(clutch("dog")) == "Dog_m1.5_N30"
    assert spec_mod.default_stem(clutch("spur")) == "Gear_m1.5_N30"
    assert spec_mod.default_stem(clutch("spur", "internal")) == "Ring_m1.5_N30"


def test_each_kind_takes_its_delegates_recipes():
    assert gears.WORKBOOK_KINDS["dog"].recipes == gears.KINDS["spur"].recipes
    assert gears.WORKBOOK_KINDS["sleeve"].recipes == gears.INTERNAL_KINDS["spur"].recipes
    dog = gears.WORKBOOK_KINDS["dog"]
    assert dog.recipe_for(clutch("dog")) == dog.default_recipe == gears.KINDS["spur"].default_recipe


@pytest.mark.parametrize("kind", ["sleeve", "dog"])
@pytest.mark.parametrize("call", [
    lambda k, s: k.derive(s), lambda k, s: k.validate(s), lambda k, s: k.variables(s, {}),
    lambda k, s: k.outline(s, {}), lambda k, s: k.plan(s, {}, "A", "", r"C:\T\x.SLDPRT"),
])
def test_until_b_writes_them_each_refuses_with_a_sentence(kind, call):
    with pytest.raises(ValueError, match=rf"^A {kind} is not built by this version of Gear Generator yet, so its part "
                                         r"cannot be worked out\.$"):
        call(gears.WORKBOOK_KINDS[kind], clutch(kind, "internal" if kind == "sleeve" else "external"))
