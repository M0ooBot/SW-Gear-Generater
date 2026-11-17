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
    """W9b adds the hub (``test_workbook_bands``), a workbook kind as these two are."""
    assert set(gears.WORKBOOK_KINDS) == {SLEEVE, DOG, "hub"} == {"sleeve", "dog", "hub"}
    assert isinstance(gears.WORKBOOK_KINDS["sleeve"], SleeveKind) and isinstance(gears.WORKBOOK_KINDS["dog"], DogKind)
    assert not set(gears.KINDS) & {"sleeve", "dog", "hub"} and not set(gears.INTERNAL_KINDS) & {"sleeve", "dog", "hub"}


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


def strip(kind, side):
    return GearSpec(kind="spur", module=1.5, teeth=30, face_width=8.0, teeth_side=side)


@pytest.mark.parametrize("kind, side, delegate", [("sleeve", "internal", "internal spur"), ("dog", "external", "spur")])
def test_each_kind_is_its_delegates_part_but_for_its_stem_and_kind_word(kind, side, delegate):
    """W8-PLAN §1.1 (J1): the strip's own ring or spur plan at the row's values; only the stem and the kind custom
    property differ."""
    k = gears.WORKBOOK_KINDS[kind]
    base = gears.kind_for(strip(kind, side))
    spec, plain = clutch(kind, side), strip(kind, side)
    derived = k.derive(spec)
    assert derived == base.derive(plain) and k.variables(spec, derived) == base.variables(plain, derived)
    assert k.outline(spec, derived, "A") == base.outline(plain, derived, "A")
    ours, theirs = k.plan(spec, derived, "A", "", r"C:\T\x.SLDPRT"), base.plan(plain, derived, "A", "", r"C:\T\x.SLDPRT")
    assert ours.kind == theirs.kind == delegate and len(ours.ops) == len(theirs.ops)
    differ = [(a, b) for a, b in zip(ours.ops, theirs.ops) if a != b]
    assert {a.name for a, _ in differ} <= {"Description", "Gear Kind"}
    assert any(a.name == "Gear Kind" and a.value == kind for a, _ in differ) or not differ
    assert [d for d in k.validate(spec, derived) if d.is_error] == []


def test_the_review_s_tip_thicknesses_at_20_degrees():
    """W8-PLAN §1.1: at 20°, 30 teeth, module 1.5, the dog's tip is 0.626 mm thick and the sleeve's 1.153 mm; the
    dog's root ⌀41.25 and the sleeve's tip ⌀42, the dog's tip ⌀48 and the sleeve's root ⌀48.75."""
    dog = gears.WORKBOOK_KINDS["dog"].derive(GearSpec(kind="dog", module=1.5, teeth=30, face_width=6.0,
                                                      pressure_angle=20.0))
    sleeve = gears.WORKBOOK_KINDS["sleeve"].derive(GearSpec(kind="sleeve", module=1.5, teeth=30, face_width=8.0,
                                                            teeth_side="internal", pressure_angle=20.0))
    assert (dog.da, dog.df) == pytest.approx((48.0, 41.25)) and (sleeve.da, sleeve.df) == pytest.approx((42.0, 48.75))


@pytest.mark.parametrize("kind, change, field, sentence", [
    ("sleeve", dict(teeth_side="external"), "teeth_side", "A sleeve's teeth are inside: set its Side to internal."),
    ("dog", dict(teeth_side="internal"), "teeth_side", "A dog's teeth are outside: set its Side to external."),
    ("dog", dict(helix_angle="15"), "helix_angle", "A dog has straight teeth: clear its Helix angle."),
    ("sleeve", dict(profile_shift="0.2"), "profile_shift",
     "A sleeve is built unshifted, to fit the dog it engages: clear its Profile shift."),
])
def test_the_clutch_rules_are_errors_at_their_cells(kind, change, field, sentence):
    from dataclasses import replace
    k = gears.WORKBOOK_KINDS[kind]
    spec = replace(clutch(kind, "internal" if kind == "sleeve" else "external"), **change)
    errors = [d for d in k.validate(spec) if d.is_error]
    assert (errors[0].message, errors[0].field) == (sentence, field)
