"""Stage F3, package A: the bore as cut (PLAN-PRINTED §4.1, §4.2; docs/notes-printed/F3-INTERFACES.md §3, §9, §13).

Every figure here is computed from the geometry (R = (D + a) / 2, h = F - D/2 + a/2, the chord 2 sqrt(R^2 - h^2), the
arc's sweep read off its own start, end and direction), and compared with the plan's tables where the plan gives one.
The printed blank default is behind spur.PRINTED_DEFAULT_IN_PLANS, off as committed; the tests of the default turn it
on with monkeypatch.
"""

import math
import re

import pytest

from gear_generator import gears, swbuild
from gear_generator.gears import bevel, clutch, equations, spur
from gear_generator.gears.base import (
    ERROR, WARNING, AddGlobal, Arc, Circle, CloseSketch, Cut, Dimension, Line, LinkDimension, OpenSketch, Relation,
)
from gear_generator.gears.equations import DEGREES, RADIANS
from gear_generator.spec import GearSpec, as_built

from test_swbuild import FakeSolidWorks, never_exists

PATH = "C:\\Out\\Bore.SLDPRT"
D8 = dict(module="1.5", teeth="20", face_width="10", bore="8")

# PLAN-PRINTED §4.2: D 8, F 7 and a 0.2, then "the other cases A's tests owe": (D, F, a) -> (h, R, chord, sweep).
TABLE = [
    ((8.0, 7.0, 0.2), (3.1000, 4.1000, 5.3666, 278.24)),
    ((8.0, 7.0, 0.0), (3.0000, 4.0000, 5.2915, 277.18)),
    ((8.0, 7.0, 0.3), (3.1500, 4.1500, 5.4037, 278.76)),
    ((8.0, 7.2, 0.2), (3.3000, 4.1000, 4.8662, 287.20)),
    ((5.0, 4.5, 0.2), (2.1000, 2.6000, 3.0659, 287.74)),
    ((3.0, 2.5, 0.2), (1.1000, 1.6000, 2.3238, 266.87)),
]


def spec(**changes):
    values = dict(D8)
    values.update(changes)
    return GearSpec(**values)


def kind_of(s):
    return gears.kind_for(s)


def plan_of(s):
    k = kind_of(s)
    return k.plan(s, k.derive(s), "A", "", PATH)


def bore_ops(plan):
    """The bore sketch's ops, from its OpenSketch to its last link."""
    ops = list(plan.ops)
    start = next(i for i, op in enumerate(ops) if isinstance(op, OpenSketch) and op.id == "bore")
    end = max(i for i, op in enumerate(ops) if isinstance(op, LinkDimension) and op.dimension.endswith("@Bore Sketch"))
    return ops[start:end + 1]


def globals_of(plan):
    return {op.name: op.expression for op in plan.ops if isinstance(op, AddGlobal)}


def link(plan, dimension):
    return next(op for op in plan.ops if isinstance(op, LinkDimension) and op.dimension == dimension)


def messages(s, level=None):
    k = kind_of(s)
    return [(d.level, d.field, d.message) for d in k.validate(s) if level is None or d.level == level]


def sweep(arc):
    """An arc's sweep from its start to its end in its own direction, degrees, from its points alone."""
    a0 = math.atan2(arc.start[1] - arc.centre[1], arc.start[0] - arc.centre[0])
    a1 = math.atan2(arc.end[1] - arc.centre[1], arc.end[0] - arc.centre[0])
    turn = (a1 - a0) if arc.direction > 0 else (a0 - a1)
    return math.degrees(turn % (2.0 * math.pi))


def geometry(bore, flat, allowance):
    """h, R, the chord and the major arc's sweep, from the formulas of §4.2 alone."""
    r = (bore + allowance) / 2.0
    h = flat - bore / 2.0 + allowance / 2.0
    chord = 2.0 * math.sqrt(r * r - h * h)
    return h, r, chord, 360.0 - 2.0 * math.degrees(math.acos(h / r))


# -- the switch ---------------------------------------------------------------------------------------------------


def test_with_the_switch_off_a_printed_blank_plans_no_allowance(monkeypatch):
    """F3-INTERFACES §13: off as package A commits it (and whatever the committed value, these tests set it), a printed
    blank on a gear not on record plans 0, as every printed part F1 and F2 built holds."""
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", False)
    s = spec(process="printed")
    assert spur.bore_allowance_of(s) == 0.0
    plan = plan_of(s)
    assert "Bore Allowance" not in globals_of(plan)
    assert link(plan, "Bore@Bore Sketch").expression == '"Bore Diameter"'
    assert "bore_allowance" not in kind_of(s).derive(s).to_dict()


def test_with_the_switch_on_a_printed_blank_not_on_record_plans_the_default(monkeypatch):
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    s = spec(process="printed")
    g = kind_of(s).derive(s)
    assert g.bore_allowance == spur.BORE_ALLOWANCE_DEFAULT == 0.2
    assert g.bore_as_cut == pytest.approx(8.2)
    plan = plan_of(s)
    assert globals_of(plan)["Bore Allowance"] == "0.2"
    assert link(plan, "Bore@Bore Sketch").expression == '"Bore Diameter" + "Bore Allowance"'
    assert plan.values()["Bore Diameter"] + plan.values()["Bore Allowance"] == pytest.approx(8.2)


@pytest.mark.parametrize("switch", [False, True])
@pytest.mark.parametrize("changes, allowance", [
    (dict(process="printed", bore_allowance="0.3"), 0.3),
    (dict(process="printed", bore_allowance="0"), 0.0),          # a typed 0 is honoured, and has no global
    (dict(process="printed", bore_allowance="-0.1"), -0.1),      # a press fit
    (dict(process="machined"), 0.0),
    (dict(process="machined", bore_allowance="0.25"), 0.25),
    (dict(process="printed", bore=""), 0.0),                       # no bore, no allowance
])
def test_a_typed_figure_plans_what_it_says_whatever_the_switch(monkeypatch, switch, changes, allowance):
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", switch)
    s = spec(**changes)
    assert spur.bore_allowance_of(s) == pytest.approx(allowance)
    plan = plan_of(s)
    assert ("Bore Allowance" in globals_of(plan)) == (allowance != 0.0)


@pytest.mark.parametrize("switch", [False, True])
@pytest.mark.parametrize("held, allowance", [([], 0.0), ([["Bore Allowance", "0.3"]], 0.3),
                                             ([["Bore Allowance", "0.2"]], 0.2)])
def test_an_as_built_figure_plans_what_the_part_holds_whatever_the_switch(monkeypatch, switch, held, allowance):
    """A part on record with no global plans none, with the default on: what every part F1 and F2 built reads."""
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", switch)
    s = as_built(spec(process="printed"), [["Bore Diameter", "8"], *held])
    assert spur.bore_allowance_of(s) == pytest.approx(allowance)
    assert ("Bore Allowance" in globals_of(plan_of(s))) == bool(allowance)


@pytest.mark.parametrize("kind_spec", [
    dict(kind="spur"), dict(kind="helical", helix_angle="15"), dict(kind="herringbone", helix_angle="30"),
    dict(kind="bevel", mate_teeth="40", face_width="8", module="2"), dict(kind="dog"), dict(kind="hub"),
])
def test_every_kind_reads_the_switch_at_call_time(monkeypatch, kind_spec):
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", False)
    s = spec(process="printed", **kind_spec)
    assert "Bore Allowance" not in globals_of(plan_of(s))
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)
    assert globals_of(plan_of(s))["Bore Allowance"] == "0.2"
    assert kind_of(s).derive(s).bore_as_cut == pytest.approx(8.2)


# -- the round bore with an allowance -----------------------------------------------------------------------------


def test_a_round_bore_with_an_allowance_op_by_op():
    s = spec(bore_allowance="0.3")
    plan = plan_of(s)
    names = [op.name for op in plan.ops if isinstance(op, AddGlobal)]
    assert names[names.index("Bore Diameter") + 1] == "Bore Allowance"
    ops = bore_ops(plan)
    assert [type(op) for op in ops] == [OpenSketch, Circle, Relation, Dimension, CloseSketch, Cut, LinkDimension]
    assert ops[0] == OpenSketch("bore", 1)
    assert ops[1].centre == (0.0, 0.0) and ops[1].radius == pytest.approx(8.3 / 2.0)
    assert ops[2] == Relation("coincident", ("bore_circle.centre", "origin"))
    assert ops[3].name == "Bore" and ops[3].refs == ("bore_circle",) and ops[3].value == pytest.approx(8.3)
    assert ops[-1] == LinkDimension("Bore@Bore Sketch", '"Bore Diameter" + "Bore Allowance"')
    assert equations.evaluate(ops[-1].expression, plan.values()) == pytest.approx(8.3)    # a circle's is a diameter
    assert plan.check() == []


def test_a_bore_with_no_allowance_and_a_round_is_the_ops_it_was():
    plan = plan_of(spec())
    ops = bore_ops(plan)
    assert ops == [
        OpenSketch("bore", 1),
        Circle("bore_circle", (0.0, 0.0), 4.0),
        Relation("coincident", ("bore_circle.centre", "origin")),
        Dimension("Bore", ("bore_circle",), spur._at(4.0 * 1.3, math.radians(-45.0)), 8.0),
        CloseSketch("bore", "Bore Sketch"),
        Cut("bore_cut", "bore", "Bore"),
        LinkDimension("Bore@Bore Sketch", '"Bore Diameter"'),
    ]
    assert not {"Bore Allowance", "Bore Flat"} & set(globals_of(plan))


# -- the D (§4.2) -------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("given, expected", TABLE)
def test_the_plans_table_from_the_geometry(given, expected):
    bore, flat, allowance = given
    h, r, chord, swept = geometry(bore, flat, allowance)
    assert (round(h, 4), round(r, 4), round(chord, 4), round(swept, 2)) == expected
    d = spur.d_flat(bore, allowance, flat)
    assert (d.h, d.radius, d.chord, d.sweep_deg) == pytest.approx((h, r, chord, swept), abs=1e-12)
    assert d.depth == pytest.approx(bore - flat)          # R - h is the shaft's own D - F, whatever the allowance
    assert flat + allowance == pytest.approx(d.h + d.radius)   # the hole is F + a across its flat


def _polygon_area(points):
    return 0.5 * abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1])))


def test_the_ds_area_for_the_plans_example():
    """49.1350 mm2 against the circle's 52.8102 (§4.2): the segment's formula, and a fine polygon of the arc as planned."""
    d = spur.d_flat(8.0, 0.2, 7.0)
    circle = math.pi * d.radius ** 2
    segment = d.radius ** 2 * math.acos(d.h / d.radius) - d.h * math.sqrt(d.radius ** 2 - d.h ** 2)
    assert round(circle, 4) == 52.8102 and round(circle - segment, 4) == 49.1350
    arc = next(op for op in bore_ops(plan_of(spec(bore_allowance="0.2", drive="flat", flat="7")))
               if isinstance(op, Arc))
    a0 = math.atan2(arc.start[1], arc.start[0])
    n = 20000
    points = [(d.radius * math.cos(a0 + math.radians(sweep(arc)) * i / n),
               d.radius * math.sin(a0 + math.radians(sweep(arc)) * i / n)) for i in range(n + 1)]
    assert _polygon_area(points) == pytest.approx(49.1350, abs=1e-3)   # the arc closed by the flat's chord


def test_the_d_op_by_op_exactly_as_section_4_2_states_it():
    plan = plan_of(spec(bore_allowance="0.2", drive="flat", flat="7"))
    ops = bore_ops(plan)
    c = 2.0 * math.sqrt(4.1 ** 2 - 3.1 ** 2)
    assert [type(op) for op in ops] == [OpenSketch, Arc, Line, Relation, Relation, Relation, Relation, Dimension,
                                        Dimension, CloseSketch, Cut, LinkDimension, LinkDimension]
    assert ops[0] == OpenSketch("bore", 1)
    arc, flat = ops[1], ops[2]
    assert arc.id == "bore_arc" and arc.centre == (0.0, 0.0) and arc.direction == 1 and not arc.construction
    assert arc.start == pytest.approx((3.1, c / 2.0)) and arc.end == pytest.approx((3.1, -c / 2.0))
    assert flat.id == "bore_flat" and not flat.construction
    assert flat.start == arc.end and flat.end == arc.start      # drawn from the arc's end, so it shares that point
    assert ops[3:7] == [
        Relation("coincident", ("bore_arc.centre", "origin")),
        Relation("coincident", ("bore_flat.start", "bore_arc.end")),
        Relation("coincident", ("bore_flat.end", "bore_arc.start")),
        Relation("vertical", ("bore_flat",)),
    ]
    assert (ops[7].name, ops[7].refs, ops[7].unit) == ("Bore", ("bore_arc",), "mm")
    assert ops[7].value == pytest.approx(4.1)                  # an arc's dimension is its radius (findings.ARC_DIMENSION)
    assert (ops[8].name, ops[8].refs) == ("Flat", ("bore_flat",)) and ops[8].value == pytest.approx(c)
    assert ops[9:11] == [CloseSketch("bore", "Bore Sketch"), Cut("bore_cut", "bore", "Bore")]
    assert ops[11] == LinkDimension("Bore@Bore Sketch", '( "Bore Diameter" + "Bore Allowance" ) / 2')
    assert ops[12].dimension == "Flat@Bore Sketch"
    g = globals_of(plan)
    assert (g["Bore Diameter"], g["Bore Allowance"], g["Bore Flat"]) == ("8", "0.2", "7")
    assert plan.check() == []


def test_the_chords_link_is_abs_to_the_half_power_and_never_sqr():
    plan = plan_of(spec(bore_allowance="0.2", drive="flat", flat="7"))
    text = link(plan, "Flat@Bore Sketch").expression
    r = '( "Bore Diameter" + "Bore Allowance" ) / 2'
    h = '"Bore Flat" - "Bore Diameter" / 2 + "Bore Allowance" / 2'
    assert text == f"2 * ( ( abs ( ( {r} ) * ( {r} ) - ( {h} ) * ( {h} ) ) ) ^ 0.5 )"
    assert text.startswith("2 * ( ( abs ( ") and text.endswith(" ) ) ^ 0.5 )") and "sqr" not in text
    for every in plan.ops:
        assert "sqr" not in getattr(every, "expression", "") and "sqr" not in getattr(every, "radian_expression", "")


def test_a_d_with_no_allowance_has_no_allowance_global_and_links_the_bore_alone():
    plan = plan_of(spec(drive="flat", flat="7"))
    assert "Bore Allowance" not in globals_of(plan) and globals_of(plan)["Bore Flat"] == "7"
    assert link(plan, "Bore@Bore Sketch").expression == '"Bore Diameter" / 2'
    text = link(plan, "Flat@Bore Sketch").expression
    assert text == ('2 * ( ( abs ( ( "Bore Diameter" / 2 ) * ( "Bore Diameter" / 2 ) - ( "Bore Flat" - "Bore Diameter" / 2 )'
                    ' * ( "Bore Flat" - "Bore Diameter" / 2 ) ) ) ^ 0.5 )')
    assert equations.evaluate(text, plan.values()) == pytest.approx(geometry(8.0, 7.0, 0.0)[2])


@pytest.mark.parametrize("bore, flat, allowance", [
    (8.0, 7.0, 0.2), (8.0, 7.0, 0.0), (8.0, 7.0, 0.3), (8.0, 7.2, 0.2), (5.0, 4.5, 0.2), (3.0, 2.5, 0.2),
    (8.0, 4.925, 0.2), (8.0, 7.7, 0.2), (8.0, 7.0, -0.2), (10.0, 9.0, 0.2), (2.0, 1.5, 0.2),
])
@pytest.mark.parametrize("trig", [DEGREES, RADIANS])
def test_the_drawn_points_satisfy_every_relation_and_dimension_its_links_drive(bore, flat, allowance, trig):
    """What the sketch is drawn at is what its relations and its linked dimensions solve to, so the first rebuild
    moves nothing: centre on the origin, the ends on one circle, the shared ends, the flat vertical on +X, the radius
    and the chord as the links evaluate them in either trig mode."""
    s = spec(module="2", teeth="30", bore=str(bore), flat=str(flat), drive="flat", bore_allowance=str(allowance))
    plan = plan_of(s)
    assert plan.check() == []
    values = plan.values(trig)
    ops = bore_ops(plan)
    arc = next(op for op in ops if isinstance(op, Arc))
    line = next(op for op in ops if isinstance(op, Line))
    dims = {op.name: op for op in ops if isinstance(op, Dimension)}
    h, r, chord, swept = geometry(bore, flat, allowance)
    assert arc.centre == (0.0, 0.0)
    assert math.hypot(*arc.start) == pytest.approx(r, abs=1e-12) == pytest.approx(math.hypot(*arc.end), abs=1e-12)
    assert line.start == arc.end and line.end == arc.start
    assert line.start[0] == line.end[0] == pytest.approx(h, abs=1e-12) and h > 0          # vertical, on +X
    assert line.start[1] + line.end[1] == pytest.approx(0.0, abs=1e-12)                    # centred on the X axis
    assert dims["Bore"].value == pytest.approx(r) and dims["Flat"].value == pytest.approx(chord)
    assert math.dist(line.start, line.end) == pytest.approx(chord, abs=1e-12)
    assert equations.evaluate(link(plan, "Bore@Bore Sketch").expression_for(trig), values, trig) == pytest.approx(r)
    assert equations.evaluate(link(plan, "Flat@Bore Sketch").expression_for(trig), values, trig) == pytest.approx(chord)
    assert sweep(arc) == pytest.approx(swept, abs=1e-9) and sweep(arc) > 180.0


def _arc_holds(arc, angle):
    """Whether the arc, swept from its start in its direction, passes the given polar angle."""
    a0 = math.atan2(arc.start[1], arc.start[0])
    off = ((angle - a0) if arc.direction > 0 else (a0 - angle)) % (2.0 * math.pi)
    return off <= math.radians(sweep(arc)) + 1e-12


def test_the_arc_as_planned_is_the_major_d_and_never_the_sliver_across_a_sweep_of_shafts_flats_and_allowances():
    """For shafts from 2 to 30 mm, every Flat from the least to the most the bounds allow, and allowances from a
    press fit to a loose one: the arc as planned sweeps 360 - 2 acos(h / R), over 180 degrees, through +Y, -X and -Y,
    and the reflected and swapped arcs (the 81.76 degree sliver for the plan's example) are what it is not."""
    count = 0
    for bore in (2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 25.0, 30.0):
        for allowance in (-0.3, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.6):
            least = (5.0 * bore - 3.0 * allowance) / 8.0
            most = bore - spur.FLAT_LEAST_DEPTH
            if least > most:
                continue
            for i in range(9):
                flat = least + (most - least) * i / 8.0
                s = spec(module="2", teeth="40", bore=repr(bore), drive="flat", flat=repr(flat),
                         bore_allowance=repr(allowance))
                assert not [m for m in messages(s, ERROR) if m[1] in ("flat", "drive", "bore_allowance")], (bore, flat)
                arc = next(op for op in bore_ops(plan_of(s)) if isinstance(op, Arc))
                h, r, _chord, swept = geometry(bore, flat, allowance)
                assert arc.direction == 1 and arc.start[1] > 0 > arc.end[1]
                assert sweep(arc) == pytest.approx(swept, abs=1e-9)
                assert 180.0 < sweep(arc) < 360.0
                assert all(_arc_holds(arc, a) for a in (math.pi / 2.0, math.pi, -math.pi / 2.0))
                assert not _arc_holds(arc, 0.0)                          # the flat, not the arc, faces +X
                reflected = Arc("r", (0.0, 0.0), (-arc.start[0], arc.start[1]), (-arc.end[0], arc.end[1]), 1)
                swapped = Arc("s", (0.0, 0.0), arc.end, arc.start, 1)
                assert sweep(reflected) < 180.0 and sweep(swapped) < 180.0
                assert sweep(reflected) == pytest.approx(360.0 - swept) == pytest.approx(sweep(swapped))
                count += 1
    assert count > 600


def test_the_plans_example_sliver_is_81_76_degrees():
    d = spur.d_flat(8.0, 0.2, 7.0)
    swapped = Arc("s", (0.0, 0.0), d.end, d.start, 1)
    assert round(sweep(swapped), 2) == 81.76 and round(d.sweep_deg, 2) == 278.24


def test_the_flat_faces_the_middle_of_the_tooth_space_centred_on_plus_x():
    """Ruling 2: the flat on +X, square to X; a spur gear's tooth space is centred on +X (its centre line CL runs from
    the origin along +X), so the flat's middle faces that space's middle."""
    s = spec(bore_allowance="0.2", drive="flat", flat="7")
    k = kind_of(s)
    g = k.derive(s)
    outline = k.outline(s, g, "A")
    assert any(p == pytest.approx((g.rf, 0.0), abs=1e-9) for p in outline)        # the root of a space on +X
    assert not any(abs(p[1]) < 1e-9 and p[0] > g.rf + 1e-6 for p in outline)       # and no tooth there
    line = next(op for op in bore_ops(plan_of(s)) if isinstance(op, Line))
    middle = ((line.start[0] + line.end[0]) / 2.0, (line.start[1] + line.end[1]) / 2.0)
    assert middle == pytest.approx((3.1, 0.0))


# -- each kind's plan ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize("kind_spec", [
    dict(kind="spur"), dict(kind="helical", helix_angle="15"), dict(kind="herringbone", helix_angle="30"),
    dict(kind="herringbone", helix_angle="30", groove="4", module="2", teeth="30", face_width="20"),
    dict(kind="dog"), dict(kind="hub"),
])
@pytest.mark.parametrize("changes", [dict(bore_allowance="0.2"), dict(bore_allowance="0.2", drive="flat", flat="7"),
                                     dict(drive="flat", flat="7.2")])
def test_each_kind_with_a_bore_cuts_the_same_bore_on_the_front_plane(kind_spec, changes):
    """Spur, helical, herringbone (plain and grooved), dog and hub: one bore sketch on the Front plane (plane 1), op
    for op the spur gear's, with the globals after "Bore Diameter"; a helical gear's flat is so at the Front plane,
    its tooth space centred on +X at its section plane (F3-INTERFACES §3)."""
    s = spec(**{**kind_spec, **changes})
    reference = spec(**changes)
    plan = plan_of(s)
    assert bore_ops(plan) == bore_ops(plan_of(reference))
    assert bore_ops(plan)[0] == OpenSketch("bore", 1)
    names = [op.name for op in plan.ops if isinstance(op, AddGlobal)]
    wanted = ["Bore Allowance"] * ("bore_allowance" in changes) + ["Bore Flat"] * ("flat" in changes)
    at = names.index("Bore Diameter")
    assert names[at + 1:at + 1 + len(wanted)] == wanted
    assert plan.check() == []
    k = kind_of(s)
    assert not [d for d in k.validate(s, k.derive(s)) if d.is_error]


@pytest.mark.parametrize("kind_spec", [dict(kind="spur"), dict(kind="helical", helix_angle="15"),
                                       dict(kind="herringbone", helix_angle="30"), dict(kind="hub")])
def test_each_kind_builds_its_d_on_the_fake(kind_spec):
    s = spec(bore_allowance="0.2", drive="flat", flat="7", **kind_spec)
    fake = FakeSolidWorks()
    result = swbuild.build(fake, plan_of(s), never_exists)
    assert result.ok, result.failures
    assert result.dimensions["Bore@Bore Sketch"] == "Bore@Bore Sketch"
    assert result.dimensions["Flat@Bore Sketch"] == "Flat@Bore Sketch"


@pytest.mark.parametrize("kind_spec", [dict(kind="spur"), dict(kind="helical", helix_angle="15"), dict(kind="hub"),
                                       dict(kind="bevel", mate_teeth="40", face_width="8", module="2")])
def test_the_derived_values_are_the_plans_for_the_bores_globals(kind_spec):
    changes = dict(bore_allowance="0.2") if kind_spec["kind"] == "bevel" else dict(bore_allowance="0.2", drive="flat",
                                                                                   flat="7")
    s = spec(**kind_spec, **changes)
    g = kind_of(s).derive(s)
    planned = plan_of(s).values()
    for name in ("Bore Diameter", "Bore Allowance", "Bore Flat"):
        assert g.values().get(name) == (pytest.approx(planned[name]) if name in planned else None)


def test_the_derived_gear_carries_the_hole_as_cut_and_keeps_it_out_of_the_record_at_its_defaults():
    for kind_spec in (dict(kind="spur"), dict(kind="helical", helix_angle="15"), dict(kind="dog")):
        plain = kind_of(spec(**kind_spec)).derive(spec(**kind_spec))
        assert (plain.bore_allowance, plain.bore_flat, plain.bore_as_cut) == (0.0, None, 8.0)
        keys = str(plain.to_dict())
        assert "bore_allowance" not in keys and "bore_flat" not in keys
        s = spec(bore_allowance="0.2", drive="flat", flat="7", **kind_spec)
        g = kind_of(s).derive(s)
        assert (g.bore_allowance, g.bore_flat, g.bore_as_cut) == (0.2, 7.0, pytest.approx(8.2))
        data = g.to_dict()
        assert (data["bore_allowance"], data["bore_flat"]) == (0.2, 7.0)


# -- the bevel gear (G5) ------------------------------------------------------------------------------------------


BEVEL = dict(kind="bevel", module="3", teeth="20", mate_teeth="40", face_width="20", bore="10")


@pytest.mark.parametrize("teeth, mate", [("20", "40"), ("40", "20"), ("40", "1")])
def test_a_bevel_gears_allowance_is_in_its_blanks_two_links_and_its_global(teeth, mate):
    """The bevel's bore is its revolved blank's inner edge: with an allowance "Bore Diameter" becomes
    ( "Bore Diameter" + "Bore Allowance" ) in the Back and Front links, the points are drawn at the hole as cut, and
    the links evaluate to the drawn lengths."""
    shaft = "120" if mate == "1" else "90"
    mate = "40" if mate == "1" else mate          # with 120 degrees between the shafts, 40 on 40 is a crown gear
    base = GearSpec(**{**BEVEL, "teeth": teeth, "mate_teeth": mate, "shaft_angle": shaft})
    plain, cut = plan_of(base), plan_of(base.with_values(bore_allowance="0.4"))
    g = kind_of(base).derive(base.with_values(bore_allowance="0.4"))
    assert g.bore_allowance == 0.4 and g.bore_as_cut == pytest.approx(10.4) and g.bore_flat is None
    assert globals_of(cut)["Bore Allowance"] == "0.4" and "Bore Allowance" not in globals_of(plain)
    for name in ("Back@Blank Sketch", "Front@Blank Sketch"):
        before, after = link(plain, name), link(cut, name)
        assert after.expression == before.expression.replace(
            '"Bore Diameter" / 2', '( "Bore Diameter" + "Bore Allowance" ) / 2')
        assert after.radian_expression == before.radian_expression.replace(
            '"Bore Diameter" / 2', '( "Bore Diameter" + "Bore Allowance" ) / 2')
        drawn = next(op for op in cut.ops if isinstance(op, Dimension) and op.name == name.split("@")[0])
        for trig in (DEGREES, RADIANS):
            assert equations.evaluate(after.expression_for(trig), cut.values(trig), trig) == pytest.approx(drawn.value)
        assert drawn.value == pytest.approx(next(op for op in plain.ops if isinstance(op, Dimension)
                                                 and op.name == name.split("@")[0]).value - 0.2)
    assert bevel.blank_points(g).back_bore[0] == pytest.approx(5.2)
    assert cut.check() == []


def test_a_bevel_gear_refuses_a_d_flat_and_says_why():
    found = messages(GearSpec(**BEVEL, drive="flat", flat="9"), ERROR)
    assert (ERROR, "drive", "A bevel gear's bore is the edge of its revolved blank and takes no flat: use a round "
                            "bore, or a hub row.") in found


def test_a_bevel_gears_bore_check_is_on_the_hole_as_cut():
    g = kind_of(GearSpec(**BEVEL)).derive(GearSpec(**BEVEL))
    limit = 2.0 * (bevel.toe_root_radius(g) - g.module)        # the bore at which the check bites
    just = GearSpec(**{**BEVEL, "bore": repr(limit - 0.3)})
    assert not [m for m in messages(just, ERROR) if m[1] == "bore"]
    over = just.with_values(bore_allowance="0.4")
    said = [m for m in messages(over, ERROR) if m[1] == "bore"]
    assert said and said[0][2].startswith(f"Bore of {spur._num(limit - 0.3)} mm with its 0.4 mm allowance "
                                          f"({spur._num(limit + 0.1)} mm as cut) reaches within a module of the root")


def test_an_internal_bevel_gear_cuts_no_bore_so_its_allowance_is_a_warning():
    ring = GearSpec(**{**BEVEL, "teeth": "60", "mate_teeth": "20", "shaft_angle": "150", "bore_allowance": "0.2"})
    g = kind_of(ring).derive(ring)
    if not g.ring:
        pytest.skip("not an internal bevel gear at these figures")
    assert g.bore_allowance == 0.0 and g.bore_as_cut == 0.0
    assert (WARNING, "bore_allowance", "An internal bevel gear is a ring and has no bore, so the Bore allowance is "
                                       "not used.") in messages(ring)


# -- rings and sleeves (G9) ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("ring", [
    dict(kind="spur", teeth_side="internal", teeth="60"),
    dict(kind="helical", teeth_side="internal", teeth="60", helix_angle="15"),
    dict(kind="herringbone", teeth_side="internal", teeth="60", helix_angle="30"),
])
@pytest.mark.parametrize("field, changes", [("bore_allowance", dict(bore_allowance="0.2")),
                                            ("drive", dict(drive="flat")), ("flat", dict(flat="7"))])
def test_a_rings_typed_bore_field_is_an_error_at_its_cell(ring, field, changes):
    s = spec(**ring, **changes)
    assert (ERROR, field, "A ring has no bore to give an allowance or a flat.") in messages(s)
    assert not messages(spec(**ring, drive="round"), ERROR)       # a round Drive is no field typed


@pytest.mark.parametrize("field, changes", [("bore_allowance", dict(bore_allowance="0.2")),
                                            ("drive", dict(drive="flat")), ("flat", dict(flat="7"))])
def test_a_sleeves_typed_bore_field_is_an_error_at_its_cell_in_the_sleeves_words(field, changes):
    s = GearSpec(kind="sleeve", module="1.5", teeth="30", face_width="8", teeth_side="internal", **changes)
    found = messages(s)
    assert (ERROR, field, "A sleeve has no bore to give an allowance or a flat.") in found
    assert not [m for m in found if "A ring has no bore" in m[2]]
    k = kind_of(s)
    assert k.derive(s) is not None                                  # the ring it delegates to never sees the fields


def test_a_hub_takes_all_three_and_its_flats_checks_run_in_the_delegate():
    hub = spec(kind="hub", bore_allowance="0.2", drive="flat", flat="7")
    plan = plan_of(hub)
    g = globals_of(plan)
    assert (g["Bore Allowance"], g["Bore Flat"]) == ("0.2", "7")
    assert any(isinstance(op, Arc) and op.id == "bore_arc" for op in plan.ops)
    assert [m[1] for m in messages(spec(kind="hub", drive="flat", flat="7.9"), ERROR)] == ["flat"]


# -- the bounds, at their edges, and every sentence ---------------------------------------------------------------


@pytest.mark.parametrize("flat, allowance, refused", [
    ("4.925", "0.2", None), ("7.7", "0.2", None), ("7", "0.2", None),
    ("4.9", "0.2", "near"), ("4.925", "-0.2", "near"), ("5.075", "-0.2", None),
    ("7.71", "0.2", "shallow"), ("7.8", "0.2", "shallow"), ("7.71", "-0.2", "shallow"), ("7.7", "-0.2", None),
    ("1.5", "0.2", "near"), ("8", "0.2", "shallow"), ("9", "0.2", "shallow"),
])
def test_each_bound_at_its_edge_with_a_negative_allowance_too(flat, allowance, refused):
    """For D 8 and a 0.2 Flat may run from 4.925 to 7.7 (the plan's re-check, §3): h >= 0.25 R, and a flat 0.3 deep."""
    found = [m for m in messages(spec(drive="flat", flat=flat, bore_allowance=allowance), ERROR) if m[1] == "flat"]
    h, r = float(flat) - 4.0 + float(allowance) / 2.0, (8.0 + float(allowance)) / 2.0
    expected = ({"near"} if h < 0.25 * r - 1e-9 else set()) | ({"shallow"} if 8.0 - float(flat) < 0.3 - 1e-9 else set())
    assert expected == ({refused} if refused else set())                    # the table agrees with the geometry
    said = {"near" if m[2].startswith(f"The flat is {spur._num(h)} mm from the axis") else
            "shallow" if m[2].startswith(f"Your shaft's flat is {spur._num(8.0 - float(flat))} mm deep") else m[2]
            for m in found}
    assert said == expected


def test_the_bounds_sentences_word_for_word():
    near = messages(spec(drive="flat", flat="4.9", bore_allowance="0.2"), ERROR)
    assert (ERROR, "flat", "The flat is 1 mm from the axis, under a quarter of the hole's radius (1.025 mm); type a "
                           "Flat of at least 4.925 mm, or use a round bore.") in near
    shallow = messages(spec(drive="flat", flat="7.8", bore_allowance="0.2"), ERROR)
    assert (ERROR, "flat", "Your shaft's flat is 0.2 mm deep (Bore 8 less Flat 7.8), under the 0.3 mm a printed D "
                           "needs to hold; type a Flat of at most 7.7 mm, which leaves the flat a little play, or use "
                           "a round bore.") in shallow


def _advised(message, words):
    """The figure a bound's sentence advises, read back off the sentence."""
    return re.search(words + r" (-?[0-9.]+) mm", message).group(1)


def test_the_advised_flat_typed_back_is_always_accepted():
    """F3-REVIEW S1: the least Flat is said rounded up and the most rounded down at the shown thousandth, so typing the
    figure a sentence advises clears that bound, for a sweep of shafts and allowances (at -0.1 the least is 5.0375,
    said 5.038, where rounding to nearest said 5.037, which is refused)."""
    checked = 0
    for bore in (2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.5, 10.0, 12.0, 15.0, 20.0, 25.0):
        for allowance in (-0.3, -0.25, -0.15, -0.1, -0.05, 0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4):
            base = dict(module="2", teeth="40", bore=repr(bore), drive="flat", bore_allowance=repr(allowance))
            near = [m[2] for m in messages(spec(**base, flat=repr(bore / 2.0)), ERROR) if "from the axis" in m[2]]
            least = _advised(near[0], "at least")
            assert float(least) >= (5.0 * bore - 3.0 * allowance) / 8.0 - 1e-9
            assert not [m for m in messages(spec(**base, flat=least), ERROR) if "from the axis" in m[2]], (bore, allowance)
            deep = [m[2] for m in messages(spec(**base, flat=repr(bore - 0.1)), ERROR) if "deep" in m[2]]
            most = _advised(deep[0], "at most")
            assert float(most) <= bore - 0.3 + 1e-9
            assert not [m for m in messages(spec(**base, flat=most), ERROR) if "deep" in m[2]], (bore, allowance)
            checked += 1
    assert checked == 13 * 14
    found = messages(spec(drive="flat", flat="5", bore_allowance="-0.1"), ERROR)
    assert any("type a Flat of at least 5.038 mm" in m[2] for m in found)
    assert not [m for m in messages(spec(drive="flat", flat="5.038", bore_allowance="-0.1"), ERROR) if m[1] == "flat"]
    assert [m for m in messages(spec(drive="flat", flat="5.037", bore_allowance="-0.1"), ERROR) if m[1] == "flat"]


def test_the_least_flat_is_where_h_is_a_quarter_of_r():
    for bore, allowance in ((8.0, 0.2), (8.0, -0.2), (5.0, 0.0), (20.0, 0.4)):
        d = spur.d_flat(bore, allowance, spur.d_flat(bore, allowance, 0.0).least_flat)
        assert d.h == pytest.approx(spur.FLAT_LEAST_H * d.radius)
        assert d.least_flat == pytest.approx((5.0 * bore - 3.0 * allowance) / 8.0)
        assert d.most_flat == pytest.approx(bore - spur.FLAT_LEAST_DEPTH)
        assert spur.d_flat(bore, allowance, d.most_flat).depth == pytest.approx(spur.FLAT_LEAST_DEPTH)


def test_the_least_chord_at_the_depth_bound():
    """At the depth bound the chord is 2 sqrt(0.6 R - 0.09): 3.08 mm at R 4.1, well clear of W9c's near-zero line."""
    d = spur.d_flat(8.0, 0.2, 7.7)
    assert d.chord == pytest.approx(2.0 * math.sqrt(0.6 * d.radius - 0.09)) and round(d.chord, 2) == 3.08


@pytest.mark.parametrize("changes, expected", [
    (dict(drive="flat", flat="7", bore=""),
     (ERROR, "drive", "Drive flat needs a Bore: type your shaft's diameter in Bore, or choose round.")),
    (dict(drive="flat"), (ERROR, "flat", "Drive flat needs a Flat: type your shaft's size across its flat.")),
    (dict(bore="", bore_allowance="0.2"),
     (WARNING, "bore_allowance", "There is no Bore, so the Bore allowance is not used.")),
    (dict(flat="7"), (WARNING, "flat", "Flat is read only with Drive flat, so with a round bore it is not used.")),
    (dict(bore="0.3", bore_allowance="-0.3"),
     (ERROR, "bore_allowance", "A Bore allowance of -0.3 mm closes the 0.3 mm bore (0 mm as cut); it must leave a hole.")),
    (dict(bore_allowance="x"), (ERROR, "bore_allowance", "Bore allowance must be a number (got 'x').")),
    (dict(drive="square"), (ERROR, "drive", "Drive must be round or flat (got 'square').")),
    (dict(drive="flat", flat="seven"), (ERROR, "flat", "Flat must be a number (got 'seven').")),
])
def test_each_checks_sentence_at_its_cell(changes, expected):
    assert expected in messages(spec(**changes))


def test_drive_is_read_in_any_case_and_a_blank_is_round():
    assert spec(drive="FLAT", flat="7").has_flat() and bore_ops(plan_of(spec(drive="FLAT", flat="7")))[1].id == "bore_arc"
    assert bore_ops(plan_of(spec(drive="")))[1].id == "bore_circle"


def test_a_gear_with_no_allowance_and_a_round_bore_says_what_it_said():
    assert spur.bore_checks(spec()) == [] and spur.bore_checks(spec(process="printed")) == []


# -- the checks on the hole as cut --------------------------------------------------------------------------------


def test_the_bore_against_the_root_is_on_the_hole_as_cut_and_names_both():
    g = kind_of(spec()).derive(spec())
    near = repr(round(g.df - 0.1, 6))
    assert not [m for m in messages(spec(bore=near), ERROR) if m[1] == "bore"]
    said = [m for m in messages(spec(bore=near, bore_allowance="0.2"), ERROR) if m[1] == "bore"]
    assert said == [(ERROR, "bore", f"Bore of {spur._num(g.df - 0.1)} mm with its 0.2 mm allowance "
                                    f"({spur._num(g.df + 0.1)} mm as cut) reaches the root diameter of "
                                    f"{spur._num(g.df)} mm; it must be smaller.")]
    plain = [m for m in messages(spec(bore=repr(round(g.df + 1, 6))), ERROR) if m[1] == "bore"]
    assert plain[0][2].startswith(f"Bore of {spur._num(g.df + 1)} mm reaches the root diameter")   # as before F3


def test_the_rim_is_measured_from_the_hole_as_cut():
    g = kind_of(spec()).derive(spec())
    bore = g.df - 2.0 * g.module + 0.1            # a rim 0.05 under one module once a 0.2 allowance is cut
    assert not [m for m in messages(spec(bore=repr(round(bore - 0.2, 9)))) if "rim" in m[2]]
    rims = [m for m in messages(spec(bore=repr(round(bore - 0.2, 9)), bore_allowance="0.2")) if "rim" in m[2]]
    shaft = round(bore - 0.2, 9)
    assert rims and rims[0][2] == (f"The bore, {spur._num(shaft)} mm with its 0.2 mm allowance ({spur._num(bore)} mm "
                                   f"as cut), leaves {spur._num((g.df - bore) / 2.0)} mm of rim under the teeth, "
                                   f"thinner than one module ({spur._num(g.module)} mm).")
    # With no allowance the sentence is the one a gear said before F3 (F3-REVIEW S2 names the hole only when cut so).
    plain = [m for m in messages(spec(bore=repr(round(bore, 9)))) if "rim" in m[2]]
    assert plain[0][2].startswith(f"The bore leaves {spur._num((g.df - bore) / 2.0)} mm of rim under the teeth")


def test_the_printed_rim_is_measured_from_the_hole_as_cut(monkeypatch):
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", False)
    s = spec(process="printed", module="1", teeth="20")
    g = kind_of(s).derive(s)
    bore = g.df - 2.0 * 3.0 * 0.4 + 0.1                 # 1.15 mm of wall at the bore, 1.05 once 0.2 is cut
    base = s.with_values(bore=repr(round(bore - 0.2, 9)))
    assert not [m for m in messages(base) if "three nozzle widths" in m[2]]
    monkeypatch.setattr(spur, "PRINTED_DEFAULT_IN_PLANS", True)       # the printed default is cut
    said = [m for m in messages(base) if "three nozzle widths" in m[2]]
    assert said and said[0][2] == (f"Printed, the bore, {spur._num(bore - 0.2)} mm with its 0.2 mm allowance "
                                   f"({spur._num(bore)} mm as cut), leaves {spur._num((g.df - bore) / 2.0)} mm of rim "
                                   "under the teeth, under three nozzle widths (1.2 mm).")
    typed_0 = [m for m in messages(base.with_values(bore_allowance="0")) if "three nozzle widths" in m[2]]
    assert not typed_0                                                  # F1's figure, 1.15 mm, passes


def test_a_printed_bevels_rim_names_the_hole_as_cut():
    s = GearSpec(**{**BEVEL, "process": "printed", "module": "1", "face_width": "6"})
    g = kind_of(s).derive(s)
    bore = 2.0 * (bevel.toe_root_radius(g) - 1.0) - 0.4         # rim 1.2 mm before the cut, 1.1 once 0.2 is cut
    cut = s.with_values(bore=repr(round(bore, 9)), bore_allowance="0.2")
    said = [m[2] for m in messages(cut) if "three nozzle widths" in m[2]]
    assert said == [f"Printed, the bore, {spur._num(bore)} mm with its 0.2 mm allowance ({spur._num(bore + 0.2)} mm as "
                    f"cut), leaves {spur._num(bevel.toe_root_radius(g) - (bore + 0.2) / 2.0)} mm of rim under the teeth, "
                    "under three nozzle widths (1.2 mm)."]


def test_the_herringbones_groove_floor_is_against_the_hole_as_cut():
    grooved = dict(kind="herringbone", helix_angle="30", module="2", teeth="20", face_width="20", groove="4")
    g = kind_of(spec(**grooved)).derive(spec(**grooved))
    bore = repr(round(g.groove_d - 0.1, 9))
    assert not [m for m in messages(spec(bore=bore, **grooved), ERROR) if m[1] == "groove"]
    said = [m for m in messages(spec(bore=bore, bore_allowance="0.2", **grooved), ERROR) if m[1] == "groove"]
    assert said == [(ERROR, "groove", f"The groove's floor, at {spur._num(g.groove_d)} mm, reaches the bore of "
                                      f"{spur._num(g.groove_d - 0.1)} mm with its 0.2 mm allowance "
                                      f"({spur._num(g.groove_d + 0.1)} mm as cut); make the bore smaller.")]
