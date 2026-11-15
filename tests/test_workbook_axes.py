"""W6's turned axes, the pieces written at its interface commit (W6-PLAN §2.1, W6-INTERFACES.md):
``geometry.axis_vector``, ``family``, ``base_frame``, ``Placed.origin``, ``layout.frame`` on the base frame — W4's
frames to the last bit on every committed Windows fixture — and ``motion.face_global`` and ``mesh_links``."""

import math
import os

import pytest

from gear_generator import swbuild
from gear_generator.workbook import assess, geometry, layout, link, motion
from gear_generator.workbook.geometry import axis_vector, base_frame, family

HERE = os.path.join(os.path.dirname(__file__), "fixtures", "excel-windows")
FIXTURES = ["Reducer_12to1.xlsx", "Arc_Move.xlsx", "Risky_Placements.xlsx"]


# -- axis_vector ----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("text, vector", [("Z+", (0, 0, 1)), ("Z-", (0, 0, -1)), ("X+", (1, 0, 0)), ("X-", (-1, 0, 0)),
                                          ("Y+", (0, 1, 0)), ("Y-", (0, -1, 0)), ("", (0, 0, 1)),
                                          ("0, 0, -2", (0, 0, -1)), ("3 0 0", (1, 0, 0)), ("0; −5; 0", (0, -1, 0)),
                                          ("1e-14, 0, 1", (0, 0, 1))])
def test_an_axis_cell_is_a_unit_vector_and_a_near_cardinal_one_is_the_word(text, vector):
    assert axis_vector(text) == tuple(float(v) for v in vector)


def test_a_slanted_axis_is_normalised():
    d = axis_vector("-1, 1.732050807569, 0")
    assert d == pytest.approx((-0.5, 0.8660254037844386, 0.0), abs=1e-12)
    assert math.isclose(sum(v * v for v in d), 1.0, abs_tol=1e-15)


@pytest.mark.parametrize("text", ["W+", "1, 2", "0, 0, 0", "1, nan, 0", "a, b, c"])
def test_an_axis_that_is_not_one_is_refused_with_a_sentence(text):
    with pytest.raises(ValueError, match=r"\.$"):
        axis_vector(text)


# -- family ---------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("word, plus, sign", [("Z+", (0, 0, 1), 1), ("Z-", (0, 0, 1), -1), ("X-", (1, 0, 0), -1),
                                              ("Y+", (0, 1, 0), 1), ("Y-", (0, 1, 0), -1)])
def test_a_family_has_the_words_plus_direction(word, plus, sign):
    assert family(axis_vector(word)) == (tuple(float(v) for v in plus), sign)


def test_a_slants_plus_direction_is_the_one_whose_first_component_is_positive():
    plus, sign = family(axis_vector("-1, 1.732050807569, 0"))
    assert sign == -1 and plus == pytest.approx((0.5, -0.8660254037844386, 0.0))
    assert family((0.0, -0.6, 0.8)) == ((0.0, 0.6, -0.8), -1)
    assert all(v != 0 or math.copysign(1, v) > 0 for v in family((0.0, -0.6, 0.8))[0])     # no -0.0


# -- base_frame -----------------------------------------------------------------------------------------------


def columns(rows):
    return [tuple(rows[i * 3 + j] for i in range(3)) for j in range(3)]


@pytest.mark.parametrize("word, u0, v0", [("Z+", (1, 0, 0), (0, 1, 0)), ("Z-", (1, 0, 0), (0, -1, 0)),
                                          ("X+", (0, 1, 0), (0, 0, 1)), ("X-", (0, 1, 0), (0, 0, -1)),
                                          ("Y+", (1, 0, 0), (0, 0, -1)), ("Y-", (1, 0, 0), (0, 0, 1))])
def test_the_base_frame_of_each_cardinal_axis_is_exact(word, u0, v0):
    rows = base_frame(axis_vector(word))
    assert columns(rows) == [tuple(float(v) for v in u0), tuple(float(v) for v in v0), axis_vector(word)]
    assert all(v != 0 or math.copysign(1, v) > 0 for v in rows)


def test_z_plus_is_the_identity_and_z_minus_is_w4s_turned_over_frame():
    assert base_frame((0.0, 0.0, 1.0)) == (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
    assert base_frame((0.0, 0.0, -1.0)) == (1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0)


@pytest.mark.parametrize("direction", [(-0.5, 0.8660254037844386, 0.0), (0.6, 0.0, 0.8), (0.2, -0.3, 0.9327379053),
                                       (1e-10, 0.6, 0.8)])
def test_a_slants_base_frame_is_a_right_handed_rotation_with_its_z_along_the_axis(direction):
    rows = base_frame(direction)
    u, v, a = columns(rows)
    norm = math.sqrt(sum(x * x for x in direction))
    assert a == pytest.approx(tuple(x / norm for x in direction), abs=1e-12)
    for p in (u, v, a):
        assert sum(x * x for x in p) == pytest.approx(1.0, abs=1e-12)
    assert sum(x * y for x, y in zip(u, a)) == pytest.approx(0.0, abs=1e-12)
    cross = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    assert cross == pytest.approx(a, abs=1e-12)
    # u0 is world +X projected onto the plane square to the axis
    x_projected = tuple(e - a[0] * x for e, x in zip((1.0, 0.0, 0.0), a))
    length = math.sqrt(sum(x * x for x in x_projected))
    assert u == pytest.approx(tuple(x / length for x in x_projected), abs=1e-9)


def test_a_frame_with_no_length_is_refused():
    with pytest.raises(ValueError, match="no gear can be turned onto it"):
        base_frame((0.0, 0.0, 0.0))


# -- layout.frame: W4's frames to the last bit -------------------------------------------------------------------


def w4_frame(placed, theta):
    """W4's ``layout.frame`` as it was before W6 (``F_σ · rot_z(θ)`` at ``(x, y, z_front)``), the reference."""
    c, s = math.cos(theta), math.sin(theta)
    rows = (c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0) if placed.sigma > 0 else (c, -s, 0.0, -s, -c, 0.0, 0.0, 0.0, -1.0)
    return layout.Frame(tuple(v + 0.0 for v in rows), (placed.x, placed.y, placed.z_front))


def assessed(name):
    reading = link.Link(os.path.join(HERE, name)).read()
    assert reading.ok, reading.error
    return assess.assess(reading.spec, reading.diagnostics, reading.spec.box.output_folder,
                         reading.spec.box.part_template)


@pytest.mark.parametrize("name", FIXTURES)
def test_frames_on_the_base_frame_are_w4s_bit_for_bit_on_every_committed_fixture(name):
    report = assessed(name).report
    placed = report.layout.placed
    assert placed and any(p.sigma < 0 for n in FIXTURES for p in assessed(n).report.layout.placed.values())
    for gear, p in placed.items():
        for theta in (report.theta[gear], report.theta[gear] + 1.0, -2.5, 0.0, math.pi):
            assert layout.frame(p, theta) == w4_frame(p, theta), (gear, theta)
    assert layout.frames(report) == {g: w4_frame(p, report.theta[g]) for g, p in placed.items()}


def test_a_turned_gears_frame_is_its_base_frame_turned_and_its_origin_its_front_face():
    p = geometry.Placed(gear="G1", shaft="S1", x=0.0, y=0.0, z=0.0, sigma=0, face=20.0, teeth=20, module=3.0,
                        internal=False, derived=None, axis=(1.0, 0.0, 0.0), centre=(5.0, 0.0, 60.0),
                        family=(1.0, 0.0, 0.0))
    f = layout.frame(p, math.radians(30))
    assert f.at == (-5.0, 0.0, 60.0)
    assert columns(f.rotation)[2] == (1.0, 0.0, 0.0)          # its own +Z along its shaft (D1)
    assert swbuild.turn_between(layout.frame(p, 0.0).rotation, f.rotation) == pytest.approx(math.radians(30))
    bevel = geometry.Placed(**{**p.__dict__, "bevel": True})
    assert layout.frame(bevel, 0.0).at == (5.0, 0.0, 60.0)    # a bevel gear's origin is its apex (D2)


# -- motion.face_global and mesh_links ---------------------------------------------------------------------------


@pytest.mark.parametrize("plane, bevel, name", [("front", False, "G4 Face Z"), ("right", False, "G1 Face X"),
                                                ("top", False, "G2 Face Y"), ("front", True, "G2 Apex Z"),
                                                ("top", True, "G4 Apex Y"), ("right", True, "G1 Apex X")])
def test_an_anchors_global_names_its_plane_and_whether_it_is_a_cone_tip(plane, bevel, name):
    assert motion.face_global(name.split()[0], plane, bevel) == name


def test_a_face_global_on_no_plane_or_no_gear_is_refused():
    assert motion.face_global("G4") == "G4 Face Z"
    with pytest.raises(ValueError):
        motion.face_global("G4", "side")
    with pytest.raises(ValueError):
        motion.face_global("", "front")


def test_mesh_links_take_the_mesh_sense_for_any_kind():
    """k = −c·za/zb, pitch 360/zb (W6-PLAN §2.4): fixture A's bevel mesh (c = +1: G2 −0.5 × G1) and its spur mesh
    (c = a·a = +1 on two Z+ shafts), fixture B's crossed mesh (c = −1: G2 +0.5 × G1)."""
    teeth = {"G1": 20, "G2": 40, "G3": 17, "G4": 51}
    links = motion.mesh_links([("G1", "G2"), ("G3", "G4")], teeth, {("G1", "G2"): 1, ("G3", "G4"): 1})
    assert links == (swbuild.MeshLink("G1", "G2", -0.5, 9.0), swbuild.MeshLink("G3", "G4", -1 / 3, 360 / 51))
    (crossed,) = motion.mesh_links([("G1", "G2")], teeth, {("G1", "G2"): -1})
    assert crossed.k == 0.5


@pytest.mark.parametrize("sense, teeth, words", [({}, {"G1": 20, "G2": 40}, "has no sense"),
                                                 ({("G1", "G2"): 2}, {"G1": 20, "G2": 40}, r"not \+1 or -1"),
                                                 ({("G1", "G2"): 1}, {"G1": 20, "G2": 0}, "above 0")])
def test_a_mesh_link_without_a_sense_or_teeth_is_refused(sense, teeth, words):
    with pytest.raises(ValueError, match=words):
        motion.mesh_links([("G1", "G2")], teeth, sense)


def test_mesh_links_are_keyed_by_the_ordered_pair_and_agree_with_w5_on_parallel_meshes():
    """The parallel sense (c = a·a outside, −a·a inside) gives W5's k = −σa·σb·za/zb and +σa·σb·za/zb."""
    for sa, sb, internal in [(1, 1, False), (1, -1, False), (-1, -1, True), (1, -1, True)]:
        c = (-1 if internal else 1) * sa * sb
        (link_,) = motion.mesh_links([("A", "B")], {"A": 14, "B": 36}, {("A", "B"): c})
        assert link_.k == pytest.approx((1 if internal else -1) * sa * sb * 14 / 36)
    with pytest.raises(ValueError, match="has no sense"):
        motion.mesh_links([("B", "A")], {"A": 14, "B": 36}, {("A", "B"): 1})


# -- gears.base.LineAxis: a slanted shaft's axis on a one-line 3D sketch ------------------------------------------


def _layout_plan(*ops):
    from gear_generator.gears.base import BuildPlan, NewPart, Rebuild, SaveAs
    return BuildPlan("layout", "", (NewPart(""),) + tuple(ops) + (Rebuild(), SaveAs("C:\\P\\L.SLDPRT")),
                     path="C:\\P\\L.SLDPRT")


def test_a_line_axis_is_a_sound_op_named_for_its_shaft():
    from gear_generator.gears.base import LineAxis, describe
    op = LineAxis("axis3", "S3 Axis", (-110.0, 84.852814, 8.0), (-0.5, 0.8660254037844386, 0.0))
    assert op.sketch == "S3 Line" and op.length == 100.0
    assert _layout_plan(op).check() == []
    assert describe(op).startswith("axis    'S3 Axis' on the line of 'S3 Line' from (-110, 84.852814, 8)")


@pytest.mark.parametrize("changes, words", [({"direction": (1.0, 1.0, 0.0)}, "not a direction of unit length"),
                                            ({"length": 0.0}, "must be longer than 0"),
                                            ({"name": "S3 Line"}, "a line axis is named")])
def test_a_line_axis_that_cannot_be_drawn_is_refused(changes, words):
    from gear_generator.gears.base import LineAxis
    fields = dict(id="axis3", name="S3 Axis", point=(0.0, 0.0, 0.0), direction=(0.0, 0.6, 0.8))
    fields.update(changes)
    problems = _layout_plan(LineAxis(**fields)).check()
    assert any(words in p for p in problems), problems


def test_a_line_axis_is_run_through_the_sessions_line_axis():
    """The runner passes the op to ``Session.line_axis`` (Agent A's body); the fake has none yet, so a build that
    holds one fails with that, never skips it."""
    assert swbuild._RUNNERS[__import__("gear_generator.gears.base", fromlist=["LineAxis"]).LineAxis] is \
        swbuild._line_axis


# -- swbuild: W6's senses carried to W5's ring reading for parallel meshes (the interface commit's bridge) -------
