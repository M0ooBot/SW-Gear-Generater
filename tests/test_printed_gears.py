"""PLAN-PRINTED §2.2, §2.3 and §2.5, package A of F1: the printed gear maths.

Every check here is for a printed gear only; a machined gear's words, Solve rows and shifts are held as they were at
the cut by tests/test_printed_rule.py, and the machined side of each case below is asserted beside the printed one.
The figures are the plan's (§2.2), recomputed by its second review.
"""

import math
from types import SimpleNamespace

import pytest

from gear_generator.gears import __main__ as cli
from gear_generator.gears import bevel, kind_for, pair, spur
from gear_generator.spec import GearSpec, InputError, PairSpec
from gear_generator.workbook import fixes
from gear_generator.workbook.geometry import Placed


def _spec(**values):
    return GearSpec(**values)


def _printed(**values):
    return GearSpec(process="printed", **values)


def _said(spec):
    return [d.message for d in kind_for(spec).validate(spec)]


def _derive(spec):
    return kind_for(spec).derive(spec)


def _printed_words(messages):
    return [m for m in messages if "Printed" in m]


# -- the tip after backlash, against one nozzle line (§2.2) -----------------------------------------------------------

TIPS = [  # module, teeth, the tip after the printed default backlash (mm), whether a 0.4 mm nozzle warns
    ("1", 12, 0.271, True), ("1", 20, 0.365, True), ("1", 25, 0.396, True), ("1", 26, 0.401, False),
    ("1", 40, 0.446, False),
    ("1.25", 10, 0.375, True), ("1.25", 11, 0.402, False),
    ("1.5", 6, 0.305, True), ("1.5", 7, 0.379, True), ("1.5", 8, 0.437, False), ("1.5", 12, 0.581, False),
    ("1.5", 20, 0.712, False),
]


@pytest.mark.parametrize("module, teeth, tip, warns", TIPS)
def test_the_printed_tip_is_the_plans_figure_and_warns_under_one_nozzle_line(module, teeth, tip, warns):
    g = _derive(_printed(module=module, teeth=str(teeth), bore=""))
    assert g.tip_thickness == pytest.approx(tip, abs=5e-4)
    assert pair.printed_tip_thickness(float(module), teeth) == pytest.approx(g.tip_thickness, abs=1e-12)
    sentence = (f"Printed, the tooth tip is {spur._num(g.tip_thickness)} mm thick after backlash, under one 0.4 mm "
                "nozzle line, so the slicer will drop or round it; use a larger module or more teeth.")
    assert (sentence in _said(_printed(module=module, teeth=str(teeth), bore=""))) is warns
    assert not _printed_words(_said(_spec(module=module, teeth=str(teeth), bore="")))


def test_module_1_warns_below_26_teeth_only_and_module_1_25_passes_from_11():
    def warns(module, teeth):
        return any("tooth tip is" in m and "nozzle" in m
                   for m in _said(_printed(module=module, teeth=str(teeth), bore="")))
    assert [z for z in range(6, 60) if warns("1", z)] == list(range(6, 26))
    assert [z for z in range(6, 60) if warns("1.25", z)] == list(range(6, 11))


@pytest.mark.parametrize("beta, shift", [(15.0, 0.2), (30.0, 0.0), (8.0, -0.1)])
def test_the_printed_tip_of_a_helical_gear_is_its_transverse_section_after_its_transverse_backlash(beta, shift):
    spec = _printed(kind="helical", helix_angle=str(beta), module="1.5", teeth="15", profile_shift=str(shift))
    g = _derive(spec)
    assert pair.printed_tip_thickness(1.5, 15, 20.0, beta, shift, 0.4) == pytest.approx(g.section.tip_thickness,
                                                                                          abs=1e-12)


def test_a_larger_nozzle_moves_every_floor_and_the_figure_says_it():
    said = _said(_printed(module="1.5", teeth="12", bore="", nozzle="0.6"))
    assert ("Printed, the tooth tip is 0.581 mm thick after backlash, under one 0.6 mm nozzle line, so the slicer "
            "will drop or round it; use a larger module or more teeth.") in said
    assert ("Printed, a module of 1.5 mm is under 2.5 nozzle widths (1.5 mm), below which a 0.6 mm nozzle rounds "
            "the profile off.") not in said                                   # at the floor is not under it
    assert ("Printed, a module of 1.25 mm is under 2.5 nozzle widths (1.5 mm), below which a 0.6 mm nozzle rounds "
            "the profile off.") in _said(_printed(module="1.25", teeth="40", bore="", nozzle="0.6"))


# -- the module floor, the rim and the helix (§2.2) -------------------------------------------------------------------

def test_a_printed_module_under_2_5_nozzle_widths_is_said_and_module_1_is_not():
    assert ("Printed, a module of 0.9 mm is under 2.5 nozzle widths (1 mm), below which a 0.4 mm nozzle rounds the "
            "profile off.") in _said(_printed(module="0.9", teeth="60", bore=""))
    assert not [m for m in _said(_printed(module="1", teeth="60", bore="")) if "nozzle widths" in m]
    assert not _printed_words(_said(_spec(module="0.9", teeth="60", bore="")))


def test_the_printed_rim_is_three_nozzle_widths_where_that_is_more_than_a_module():
    said = _said(_printed(module="0.8", teeth="30", bore="20"))
    assert "Printed, the bore leaves 0.88 mm of rim under the teeth, under three nozzle widths (1.2 mm)." in said
    assert not [m for m in _said(_spec(module="0.8", teeth="30", bore="20")) if "rim" in m]
    # Above module 1.2 today's one-module warning is the stricter, and a printed gear is told it as a machined one is.
    machined = [m for m in _said(_spec(module="2", teeth="20", bore="33")) if "rim" in m]
    assert machined == ["The bore leaves 1 mm of rim under the teeth, thinner than one module (2 mm)."]
    assert [m for m in _said(_printed(module="2", teeth="20", bore="33")) if "rim" in m] == machined
    # Under a module but over three nozzle widths does not happen above 1.2; at 0.8 the printed floor replaces it.
    assert [m for m in _said(_printed(module="0.8", teeth="30", bore="21")) if "rim" in m] == [
        "Printed, the bore leaves 0.38 mm of rim under the teeth, under three nozzle widths (1.2 mm)."]


@pytest.mark.parametrize("kind", ["helical", "herringbone"])
def test_a_printed_helix_over_45_degrees_is_an_overhang(kind):
    sentence = "Printed, a helix angle of 46° is over 45°, so the flanks print as an overhang."
    assert sentence in _said(_printed(kind=kind, helix_angle="46", module="2", teeth="20", face_width="20"))
    assert not [m for m in _said(_printed(kind=kind, helix_angle="45", module="2", teeth="20", face_width="20"))
                if "overhang" in m]
    assert not _printed_words(_said(_spec(kind=kind, helix_angle="46", module="2", teeth="20", face_width="20")))


def test_a_printed_helical_ring_over_45_degrees_is_told_too():
    spec = _printed(kind="helical", teeth_side="internal", teeth="60", helix_angle="50", bore="")
    assert "Printed, a helix angle of 50° is over 45°, so the flanks print as an overhang." in _said(spec)


# -- the ring: its tip, its fillet, its clearance -----------------------------------------------------------------------

def test_a_printed_rings_tips_are_judged_after_backlash_and_told_only_the_larger_module():
    spec = _printed(teeth_side="internal", teeth="40", module="0.5", bore="")
    g = _derive(spec)
    assert g.tip_thickness == pytest.approx(0.341, abs=5e-4)
    assert pair.printed_ring_tip_thickness(0.5, 40) == pytest.approx(g.tip_thickness, abs=1e-12)
    assert ("Printed, the ring's tooth tips are 0.341 mm thick after backlash, under one 0.4 mm nozzle line, so the "
            "slicer will drop or round them; use a larger module.") in _said(spec)
    # A ring's tips thin toward a rack's as its teeth grow: more teeth is no cure for it.
    assert _derive(_printed(teeth_side="internal", teeth="20", module="0.5", bore="")).tip_thickness > g.tip_thickness
    assert not _printed_words(_said(_spec(teeth_side="internal", teeth="40", module="0.5", bore="")))


def test_the_ring_fillet_sentence_is_for_a_printed_rings_default_fillet_only():
    sentence = ("Printed, the ring's 0.225 mm root fillet is 0.15 × module, under the 0.3 × module printed gears are "
                "given; it is kept small so the pinion's tips clear it.")
    assert sentence in _said(_printed(teeth_side="internal", teeth="60", bore=""))
    assert not [m for m in _said(_printed(teeth_side="internal", teeth="60", bore="", fillet="0.3")) if "fillet" in m]
    assert sentence not in _said(_spec(teeth_side="internal", teeth="60", bore=""))


@pytest.mark.parametrize("module, clearance", [(0.5, 0.2), (1.0, 0.4), (1.25, 0.5), (1.5, 0.375), (2.0, 0.5)])
def test_a_ring_pairs_clearance_is_the_depth_less_two_addenda_both_ways(module, clearance):
    """Pinion tip to ring root and ring tip to pinion root, h − 2m each unshifted: 0.4 × module to module 1.25 and
    0.25 × module above, as an outside pair's."""
    assert pair.ring_tip_clearance(module, 13, 55) == pytest.approx(clearance, abs=1e-9)
    assert pair.ring_tip_clearance(module, 20, 60, 20.0, 15.0) == pytest.approx(clearance, abs=1e-9)


def test_a_ring_pairs_clearance_with_a_shifted_pinion_is_at_its_working_centre_and_a_shifted_ring_is_refused():
    module, z1, z2, x = 1.25, 13, 55, 0.3
    alpha = math.radians(20.0)
    value = spur.inv(alpha) - 2.0 * math.tan(alpha) * x / (z2 - z1)
    centre = module * (z2 - z1) / 2.0 * math.cos(alpha) / math.cos(spur.inv_inverse(value))
    depth = spur.tooth_depth(module)
    ra1, ra2 = z1 * module / 2 + module * (1 + x), z2 * module / 2 - module
    want = min(ra2 + depth - centre - ra1, ra2 - (centre + ra1 - depth))
    assert pair.ring_tip_clearance(module, z1, z2, shift_1=x) == pytest.approx(want, abs=1e-12)
    with pytest.raises(ValueError, match="A ring is cut without profile shift here"):
        pair.ring_tip_clearance(module, z1, z2, shift_2=0.1)
    with pytest.raises(ValueError, match="too much for it to mesh"):
        pair.ring_tip_clearance(1.0, 20, 22, shift_1=1.0)


# -- the bevel gear's toe (§2.1, §2.2) ---------------------------------------------------------------------------------

def test_a_printed_bevel_gears_tip_is_judged_at_its_toe_not_its_heel():
    spec = _printed(kind="bevel", teeth="20", mate_teeth="40", module="1.5", face_width="10")
    g = _derive(spec)
    assert g.toe_scale == pytest.approx(0.70, abs=5e-3)                   # §2.1's 0.70 of the heel's
    assert bevel.toe_tip_thickness(g) == pytest.approx(g.section.tip_thickness * g.toe_scale)
    said = _said(spec)
    assert ("Printed, the tooth tip at the toe is 0.371 mm thick after backlash, under one 0.4 mm nozzle line, so "
            "the slicer will drop or round it; use a larger module, more teeth or a narrower face.") in said
    assert not [m for m in said if m.startswith("Printed, the tooth tip is")]       # the heel's (0.529) is not said
    assert not [m for m in _said(spec.with_values(face_width="5")) if "tooth tip" in m]   # 0.450 at the toe
    assert not _printed_words(_said(_spec(kind="bevel", teeth="20", mate_teeth="40", module="1.5", face_width="10")))


def test_a_printed_crown_gear_is_judged_at_its_toe_and_its_module():
    shaft = bevel.crown_shaft_angle(40, 20)
    spec = _printed(kind="bevel", teeth="40", mate_teeth="20", shaft_angle=repr(shaft), module="0.8", face_width="5")
    g = _derive(spec)
    assert g.crown
    said = _said(spec)
    assert ("Printed, a module of 0.8 mm is under 2.5 nozzle widths (1 mm), below which a 0.4 mm nozzle rounds the "
            "profile off.") in said
    toe = bevel.toe_tip_thickness(g)
    assert toe == pytest.approx(g.section.tip_thickness * g.toe_scale) and toe < 0.4
    assert (f"Printed, the tooth tip at the toe is {bevel._num(toe)} mm thick after backlash, under one 0.4 mm nozzle "
            "line, so the slicer will drop or round it; use a larger module, more teeth or a narrower face.") in said
    machined = _said(_spec(kind="bevel", teeth="40", mate_teeth="20", shaft_angle=repr(shaft), module="0.8",
                           face_width="5"))
    assert not _printed_words(machined)


@pytest.mark.parametrize("module, warns", [("1.25", True), ("1.5", True), ("1.6", False), ("2", False)])
def test_a_printed_bevel_pair_warns_under_module_1_6_by_gleasons_clearance(module, warns):
    a = _derive(_printed(kind="bevel", teeth="20", mate_teeth="40", module=module))
    b = _derive(_printed(kind="bevel", teeth="40", mate_teeth="20", module=module))
    said = pair.mesh_warnings(a, b)
    clearance = 0.188 * float(module)
    assert said == ([f"Printed, the tip clearance is {pair._num(clearance)} mm, under the 0.3 mm two printed "
                     "surfaces take; use a larger module."] if warns else [])


@pytest.mark.parametrize("shaft, teeth", [(90.0, ("20", "40")), (90.0, ("17", "17")), (60.0, ("18", "30")),
                                          (120.0, ("20", "25"))])
def test_a_bevel_pairs_clearance_is_one_figure_gleasons_0_188_module(shaft, teeth):
    """F1 review, S4: pair.bevel_tip_clearance is the figure the form and the workbook both judge a printed bevel pair
    by; for a cone pair it is Gleason's uniform clearance, 0.188 × module, whatever the shaft angle."""
    a = _derive(_printed(kind="bevel", teeth=teeth[0], mate_teeth=teeth[1], module="1.5", shaft_angle=repr(shaft),
                         face_width="6"))
    b = _derive(_printed(kind="bevel", teeth=teeth[1], mate_teeth=teeth[0], module="1.5", shaft_angle=repr(shaft),
                         face_width="6"))
    assert pair.bevel_tip_clearance(a, b) == pytest.approx(0.188 * 1.5) == pytest.approx(pair.bevel_tip_clearance(b, a))
    assert pair.mesh_warnings(a, b) == [pair.printed_clearance_sentence(pair.bevel_tip_clearance(a, b), False)]


# -- the pair's clearance on the form (§2.2) ---------------------------------------------------------------------------

@pytest.mark.parametrize("module, warns", [("0.5", True), ("0.7", True), ("0.75", False), ("1", False)])
def test_an_unshifted_printed_outside_pair_passes_from_module_0_75(module, warns):
    a, b = _derive(_printed(module=module, bore="")), _derive(_printed(module=module, teeth="40", bore=""))
    said = pair.mesh_warnings(a, b)
    assert bool(said) is warns
    if warns:
        assert said == [f"Printed, the tip clearance is {pair._num(0.4 * float(module))} mm, under the 0.3 mm two "
                        "printed surfaces take; use a larger module."]
    machined = pair.mesh_warnings(_derive(_spec(module=module, bore="")), _derive(_spec(module=module, teeth="40",
                                                                                        bore="")))
    assert machined == []


def test_a_shifted_printed_pair_is_told_to_take_shift_off_and_a_pair_that_cannot_be_built_is_said_as_before():
    a = _derive(_printed(module="1", teeth="20", profile_shift="0.6", bore=""))
    b = _derive(_printed(module="1", teeth="30", profile_shift="0.4", bore=""))
    clearance = pair.tip_clearance(1, 20, 30, 20.0, 0.0, 0.6, 0.4)
    assert 0 < clearance < 0.3
    assert pair.mesh_warnings(a, b) == [f"Printed, the tip clearance is {pair._num(clearance)} mm, under the 0.3 mm "
                                        "two printed surfaces take; use a larger module or less profile shift."]
    a, b = _derive(_printed(module="2", teeth="20", profile_shift="1", bore="")), \
        _derive(_printed(module="2", teeth="20", profile_shift="1", bore=""))
    machined = pair.mesh_warnings(_derive(_spec(module="2", teeth="20", profile_shift="1", bore="")),
                                  _derive(_spec(module="2", teeth="20", profile_shift="1", bore="")))
    assert pair.mesh_warnings(a, b) == machined and "cannot be built" in machined[0]


def test_a_printed_pinion_in_a_ring_is_judged_by_the_rings_clearance_whichever_comes_first():
    pinion = _derive(_printed(module="0.5", teeth="13", bore=""))
    ring = _derive(_printed(module="0.5", teeth="55", teeth_side="internal", bore=""))
    said = ["Printed, the tip clearance is 0.2 mm, under the 0.3 mm two printed surfaces take; use a larger module."]
    assert pair.mesh_warnings(pinion, ring) == pair.mesh_warnings(ring, pinion) == said
    # RangeBox's 13 in 55 at module 1.25: 0.5 mm, clear; and no interference sentence of any kind (§2.3).
    assert pair.mesh_warnings(_derive(_printed(module="1.25", teeth="13", bore="")),
                              _derive(_printed(module="1.25", teeth="55", teeth_side="internal", bore=""))) == []
    machined = pair.mesh_warnings(_derive(_spec(module="0.5", teeth="13", bore="")),
                                  _derive(_spec(module="0.5", teeth="55", teeth_side="internal", bore="")))
    assert machined == []


def test_no_pair_interference_warning_is_said_printed_or_machined():
    """§2.3, by ruling: the pairs the third check swept (6 / 30 to 13 / 80, modules 1 and 1.5) say nothing of
    interference or undercut as pairs; a printed pair says at most its clearance."""
    for module in ("1", "1.5"):
        for z1, z2 in ((6, 30), (8, 40), (10, 40), (12, 60), (13, 80)):
            for make in (_spec, _printed):
                said = pair.mesh_warnings(_derive(make(module=module, teeth=str(z1), bore="")),
                                          _derive(make(module=module, teeth=str(z2), bore="")))
                assert not [m for m in said if "interfer" in m or "undercut" in m or "clash" in m]


# -- the single gear's undercut, printed (§2.3) ----------------------------------------------------------------------

def test_a_printed_undercut_gear_is_made_as_drawn_and_keeps_the_named_shift():
    printed = [m for m in _said(_printed(module="1", teeth="12", bore="")) if "undercut" in m]
    assert printed == [
        "12 teeth at 20° is below the undercut limit of 17. Printed, the gear is made as drawn, with no undercut; "
        "whether a mate's tip clears its flank below the base circle is not checked here, so turn the pair in "
        "SolidWorks. A profile shift of 0.3 or more would clear it."]
    machined = [m for m in _said(_spec(module="1", teeth="12", bore="")) if "undercut" in m]
    assert machined == [
        "12 teeth at 20° is below the undercut limit of 17: a generated gear would lose the bottom of its flanks, "
        "which this profile does not show. A profile shift of 0.3 or more would clear it."]


# -- every kind derives, checks and plans printed (§2.8, Done when) ---------------------------------------------------

@pytest.mark.parametrize("values", [
    dict(), dict(kind="helical", helix_angle="20"), dict(kind="herringbone", helix_angle="30", module="2", teeth="20"),
    dict(teeth_side="internal", teeth="60", bore=""), dict(kind="bevel", teeth="20", mate_teeth="40"),
    dict(kind="sleeve", teeth_side="internal", teeth="20", module="2", bore=""),
    dict(kind="dog", teeth="20", module="2", bore="10"), dict(kind="hub", teeth="20", module="2", bore="10"),
], ids=["spur", "helical", "herringbone", "ring", "bevel", "sleeve", "dog", "hub"])
def test_every_kind_derives_checks_and_plans_printed(values):
    spec = _printed(**values)
    kind = kind_for(spec)
    g = kind.derive(spec)
    assert g.printed and not any(d.is_error for d in kind.validate(spec, g))
    plan = kind.plan(spec, g, kind.recipe_for(spec), "C:\\T\\Part.prtdot", "C:\\Out\\" + spec.stem() + ".SLDPRT")
    assert plan.check() == [] and plan.path.endswith("_P.SLDPRT")


# -- Solve (§2.5) -------------------------------------------------------------------------------------------------

def test_a_printed_solve_marks_and_ranks_thin_rows_after_the_clean_ones():
    machined = pair.solve(60, 3)
    printed = pair.solve(60, 3, process="Printed")
    assert {(r.module, r.teeth_driver, r.teeth_driven) for r in printed} == \
        {(r.module, r.teeth_driver, r.teeth_driven) for r in machined}
    marked = [r for r in printed if r.mark]
    assert marked and all(r.mark == "thin for a 0.4 nozzle" for r in marked)
    for r in printed:
        floor = r.module < 1.0 - 1e-9
        thin = min(pair.printed_tip_thickness(r.module, r.teeth_driver, shift=r.shift_1),
                   pair.printed_tip_thickness(r.module, r.teeth_driven, shift=r.shift_2)) < 0.4 - 1e-9
        assert bool(r.mark) is (floor or thin)
    # Among the rows that meet the centre exactly at a standard module, every clean one comes before every marked.
    exact = [r for r in printed if r.exact and r.standard]
    assert [bool(r.mark) for r in exact] == sorted(bool(r.mark) for r in exact)
    assert all(r.mark == "" for r in machined)
    assert repr(machined) == repr(pair.solve(60, 3, process="machined")) == repr(pair.solve(60, 3, process=""))


def test_a_printed_solve_says_its_nozzle_and_offers_no_row_whose_tip_comes_to_a_point():
    assert {r.mark for r in pair.solve(60, 3, process="printed", nozzle=0.6) if r.mark} == {"thin for a 0.6 nozzle"}
    args = dict(centre=4.5, ratio=2, module=0.5, min_teeth=6, pressure_angle=30)
    assert [(r.teeth_driver, r.teeth_driven) for r in pair.solve(**args)] == [(6, 12), (7, 11)]
    assert pair.printed_tip_thickness(0.5, 7, 30.0) < 0
    assert pair.solve(**args, process="printed") == []


def test_a_printed_ring_solve_judges_the_pinion_and_the_ring():
    rows = pair.solve(30, 4, mesh="internal", process="printed")
    for r in rows:
        tips = (pair.printed_tip_thickness(r.module, r.teeth_driver, 20.0, r.helix_angle),
                pair.printed_ring_tip_thickness(r.module, r.teeth_driven, 20.0, r.helix_angle))
        assert r.mark == pair.printed_mark(r.module, 0.4, tips)
    assert any(r.mark for r in rows) and not rows[0].mark


def test_a_printed_bevel_solve_judges_its_toes_with_the_forms_face_width():
    form = PairSpec(mode="pair", cone_distance="30", ratio="2", gear_a=_printed(kind="bevel", face_width="9"),
                    gear_b=_printed(kind="bevel", face_width="9"))
    rows = pair.solve_spec(form)
    assert rows and any(r.mark for r in rows)
    for r in rows[:5]:
        g = _derive(_printed(kind="bevel", module=repr(r.module), teeth=str(r.teeth_driver),
                             mate_teeth=str(r.teeth_driven), face_width="9"))
        h = _derive(_printed(kind="bevel", module=repr(r.module), teeth=str(r.teeth_driven),
                             mate_teeth=str(r.teeth_driver), face_width="9"))
        assert r.mark == pair.printed_mark(r.module, 0.4, (bevel.toe_tip_thickness(g), bevel.toe_tip_thickness(h)))
    machined = PairSpec(mode="pair", cone_distance="30", ratio="2", gear_a=_spec(kind="bevel", face_width="9"),
                        gear_b=_spec(kind="bevel", face_width="9"))
    assert repr(pair.solve_spec(machined)) == repr(pair.solve(30, 2, kind="bevel", shaft_angle=90.0))


def test_a_printed_bevel_row_whose_gear_does_not_derive_is_not_offered():
    """F1 review, S7: a printed bevel row is judged at its toes, which needs each gear derived with the form's face
    width. A row whose gear does not derive (here a face width of 0) was offered unmarked, as if clean; it is now not
    offered, as a row whose tip comes to a point is not. A machined Solve is as before."""
    machined = pair.solve(40, 2, kind="bevel", shaft_angle=90.0, face_width=0.0)
    assert machined and all(r.mark == "" for r in machined)
    assert all(pair._bevel_toe_tips(r.module, r.teeth_driver, r.teeth_driven, r.shaft_angle, 20.0, 0.0) is None
               for r in machined)
    assert pair.solve(40, 2, kind="bevel", shaft_angle=90.0, face_width=0.0, process="printed") == []
    assert repr(machined) == repr(pair.solve(40, 2, kind="bevel", shaft_angle=90.0, face_width=0.0,
                                             process="machined"))
    assert pair.solve(40, 2, kind="bevel", shaft_angle=90.0, face_width=9.0, process="printed")


def test_a_printed_crossed_solve_marks_each_row_by_each_gears_own_helix():
    """F1 review, S6: a crossed pair's two gears have their own helix angles (6 and 9 teeth at 32.15° and 57.85°, ...),
    and a printed row's tips are each judged at its own gear's helix. Some rows are marked, and for at least one the
    mark would differ were both gears judged at one helix (the 6-tooth pinion's tip is 0.31 mm at its own 32.15°, thin,
    and would be 0.96 mm at its mate's 57.85°)."""
    args = dict(centre=12, ratio=1.5, kind="helical", shafts="crossed", shaft_angle=90.0, min_teeth=6)
    machined = pair.solve(**args)
    printed = pair.solve(**args, process="printed")
    assert printed and any(r.mark for r in printed) and all(r.mark == "" for r in machined)
    assert {(r.module, r.teeth_driver, r.teeth_driven) for r in printed} <=         {(r.module, r.teeth_driver, r.teeth_driven) for r in machined}
    one_helix = []
    for r in printed:
        assert abs(r.helix_angle - r.helix_angle_b) > 1.0
        own = (pair.printed_tip_thickness(r.module, r.teeth_driver, 20.0, r.helix_angle),
               pair.printed_tip_thickness(r.module, r.teeth_driven, 20.0, r.helix_angle_b))
        assert r.mark == pair.printed_mark(r.module, 0.4, own)
        at_a = (own[0], pair.printed_tip_thickness(r.module, r.teeth_driven, 20.0, r.helix_angle))
        at_b = (pair.printed_tip_thickness(r.module, r.teeth_driver, 20.0, r.helix_angle_b), own[1])
        one_helix.append(any(pair.printed_mark(r.module, 0.4, tips) != r.mark for tips in (at_a, at_b)))
    assert any(one_helix)


def test_solve_spec_takes_the_forms_process_and_nozzle():
    printed = PairSpec(mode="pair", centre_distance="60", ratio="3", gear_a=_printed(nozzle="0.6"),
                       gear_b=_printed(nozzle="0.6"))
    assert pair.solve_spec(printed) == pair.solve(60, 3, process="printed", nozzle=0.6)
    plain = PairSpec(mode="pair", centre_distance="60", ratio="3")
    assert pair.solve_spec(plain) == pair.solve(60, 3)
    with pytest.raises(InputError, match="Nozzle"):
        pair.solve_spec(PairSpec(mode="pair", centre_distance="60", ratio="3", gear_a=_printed(nozzle="x")))


# -- the shift for a centre distance, and the workbook's fix (§2.5) -----------------------------------------------

def test_a_printed_shift_tests_the_tip_after_backlash_against_the_nozzle():
    assert pair.shift_for_centre(1, 12, 30, 21.6) == pytest.approx((0.3295525, 0.3295525), abs=1e-6)
    with pytest.raises(ValueError) as raised:
        pair.shift_for_centre(1, 12, 30, 21.6, printed=True)
    assert str(raised.value) == ("The shifts that meet 21.6 mm leave a printed tooth tip under one 0.4 mm nozzle line "
                                 "after backlash; move the shaft instead.")
    assert pair.shift_for_centre(2, 15, 30, 46, printed=True) == pair.shift_for_centre(2, 15, 30, 46)


def test_a_printed_shift_wants_the_larger_of_a_tenth_module_and_0_3_mm_of_clearance():
    # At module 2 a machined pair wants 0.2 mm (a tenth of a module), a printed one 0.3 mm.
    x1, x2 = pair.shift_for_centre(2, 20, 30, 51.72)
    assert 0.2 < pair.tip_clearance(2, 20, 30, 20.0, 0.0, x1, x2) < 0.3
    assert min(pair.printed_tip_thickness(2, 20, shift=x1), pair.printed_tip_thickness(2, 30, shift=x2)) > 0.4
    with pytest.raises(ValueError) as raised:
        pair.shift_for_centre(2, 20, 30, 51.72, printed=True)
    assert str(raised.value) == ("The shifts that meet 51.72 mm bring the tips nearer the other gear's root than the "
                                 "0.3 mm a print takes; move the shaft instead.")


def _placed(name, x, spec):
    g = _derive(spec)
    return Placed(gear=name, shaft="S" + name, x=x, y=0.0, z=0.0, sigma=1, face=10.0, teeth=g.teeth,
                  module=g.module, internal=False, derived=g, spec=spec)


def test_the_workbooks_shift_fix_tests_a_printed_pair_as_a_print():
    gearbox = SimpleNamespace(meshes=[SimpleNamespace(a="A", b="B")])
    machined = fixes.shift_fix(gearbox, _placed("A", 0.0, _spec(module="1", teeth="12", bore="")),
                               _placed("B", 21.6, _spec(module="1", teeth="30", bore="")))
    assert machined is not None and machined.title == "Keep your positions: profile-shift A and B"
    printed = fixes.shift_fix(gearbox, _placed("A", 0.0, _printed(module="1", teeth="12", bore="")),
                              _placed("B", 21.6, _printed(module="1", teeth="30", bore="")))
    assert printed is None
    clean = fixes.shift_fix(gearbox, _placed("A", 0.0, _printed(module="2", teeth="15", bore="")),
                            _placed("B", 46.0, _printed(module="2", teeth="30", bore="")))
    assert clean is not None and clean.edits == fixes.shift_fix(
        gearbox, _placed("A", 0.0, _spec(module="2", teeth="15", bore="")),
        _placed("B", 46.0, _spec(module="2", teeth="30", bore=""))).edits


# -- the command line (§1.3) ---------------------------------------------------------------------------------------

def test_the_command_line_takes_a_process_and_a_nozzle(capsys):
    assert cli.parse_spec("m=1,z=20,process=printed,nozzle=0.6") == GearSpec(module="1", teeth="20",
                                                                                process="printed", nozzle="0.6")
    assert cli.main(["--spec", "m=1,z=20,bore=5,process=printed"]) == 0
    out = capsys.readouterr().out
    assert "warn    Printed, the tooth tip is 0.365 mm thick after backlash" in out
    assert cli.main(["--spec", "m=1,z=20,bore=5"]) == 0
    assert "Printed" not in capsys.readouterr().out
