"""PLAN-PRINTED §3.0, package A of F2: the span over k teeth (``gears/span.py``).

Every figure of §3.0's table is held here to 1e-4 mm in both of the plan's forms: the transverse form, which
``span.span`` computes from the derived gear, and the closed form, which each test computes again below from the
row's numbers alone (module, teeth, pressure angle, helix, shift, the backlash drawn), not from the derived gear. The
spur rows and the helical sections are held besides against the app's own drawn outline (``SpurGear.outline``,
recipe A), read as an involute's base-circle origins, which tests the app's backlash and shift conventions as no
textbook example can (§3.0, the check owed by package A). k is held against the textbook k through
``d_M = d + 2 x m_n``, recomputed here.
"""

import math

import pytest

from gear_generator.gears import kind_for, spur
from gear_generator.gears import span as span_mod
from gear_generator.gears.span import (
    BACKLASH_FLOOR_MM,
    KIND_ARCS,
    KIND_NARROW_FACE,
    KIND_NO_CONTACT,
    KIND_NONE,
    KIND_SPAN,
    KINDS,
    NONE,
    Measured,
    SpanReading,
    choose,
    contact_bounds,
    measured,
    span,
    span_over,
)
from gear_generator.spec import GearSpec


def _printed(**values):
    return GearSpec(process="printed", bore="", **values)


def _machined(**values):
    return GearSpec(bore="", **values)


def _derive(spec):
    return kind_for(spec).derive(spec)


def _span(spec):
    kind = kind_for(spec)
    return span(kind.derive(spec), kind.recipe_for(spec))


def _inv(a):
    return math.tan(a) - a


def _closed_form(m_n, z, k, alpha_n_deg=20.0, beta_deg=0.0, x=0.0, j_n=0.3):
    """§3.0's closed form, from the row's numbers alone:
    W_n = m_n cos α_n [(k − 0.5) π + z inv α_t] + 2 x m_n sin α_n − j_n cos α_n."""
    alpha_n = math.radians(alpha_n_deg)
    alpha_t = math.atan(math.tan(alpha_n) / math.cos(math.radians(beta_deg)))
    return (m_n * math.cos(alpha_n) * ((k - 0.5) * math.pi + z * _inv(alpha_t))
            + 2.0 * x * m_n * math.sin(alpha_n) - j_n * math.cos(alpha_n))


def _beta_b(beta_deg, alpha_n_deg=20.0):
    return math.asin(math.sin(math.radians(beta_deg)) * math.cos(math.radians(alpha_n_deg)))


def _textbook_k(m_n, z, beta_deg=0.0, x=0.0, alpha_n_deg=20.0):
    """The textbook k through d_M = d + 2 x m_n (ISO 21771 / DIN 3960 as the plan's reviewer and this package know it;
    KHK's shifted spur rule is the same at β = 0): z / π · (tan α_M / cos² β_b − inv α_t − 2 x tan α_n / z) + 0.5,
    rounded to the nearest whole tooth."""
    alpha_n = math.radians(alpha_n_deg)
    beta = math.radians(beta_deg)
    alpha_t = math.atan(math.tan(alpha_n) / math.cos(beta))
    d = z * m_n / math.cos(beta)
    alpha_m = math.acos(d * math.cos(alpha_t) / (d + 2.0 * x * m_n))
    beta_b = _beta_b(beta_deg, alpha_n_deg)
    exact = z / math.pi * (math.tan(alpha_m) / math.cos(beta_b) ** 2 - _inv(alpha_t)
                           - 2.0 * x * math.tan(alpha_n) / z) + 0.5
    return round(exact), exact


# -- §3.0's table ------------------------------------------------------------------------------------------------------

# (name, spec, module, teeth, helix, shift, backlash drawn, k, W_n, W_t, contact radius, pitch radius)
SPUR_ROWS = [
    ("m 1.5, z 20", _printed(module="1.5", teeth="20"), 1.5, 20, 0.0, 0.0, 0.3, 3, 11.2088, 11.2088, 15.169, 15.0),
    ("m 1, z 12", _printed(module="1", teeth="12"), 1.0, 12, 0.0, 0.0, 0.3, 2, 4.3144, 4.3144, 6.037, 6.0),
    ("m 2, z 30", _printed(module="2", teeth="30"), 2.0, 30, 0.0, 0.0, 0.3, 4, 21.2233, 21.2233, 30.122, 30.0),
    ("m 1.5, z 15, x +0.3", _printed(module="1.5", teeth="15", profile_shift="0.3"), 1.5, 15, 0.0, 0.3, 0.3, 3,
     11.4115, 11.4115, 12.013, 11.25),
    ("RangeBox Sun m 1.25, z 29", _printed(module="1.25", teeth="29"), 1.25, 29, 0.0, 0.0, 0.3, 4, 13.1414, 13.1414,
     18.255, 18.125),
    ("RangeBox Planet m 1.25, z 13", _printed(module="1.25", teeth="13"), 1.25, 13, 0.0, 0.0, 0.3, 2, 5.4809, 5.4809,
     8.112, 8.125),
]
HELICAL_ROWS = [
    ("m_n 2, z 20, beta 15", _printed(kind="helical", module="2", teeth="20", helix_angle="15"), 2.0, 20, 15.0, 0.0,
     0.3, 3, 15.0972, 15.5645, 20.713, 20.706),
    ("m_n 1.5, z 25, beta 20", _printed(kind="helical", module="1.5", teeth="25", helix_angle="20"), 1.5, 25, 20.0,
     0.0, 0.3, 4, 15.8438, 16.7315, 20.062, 19.953),
    # F2-INTERFACES §1: face 14, since at the default 10 it is under its 12.97 mm and reads narrow_face.
    ("m_n 2, z 20, beta 30, face 14", _printed(kind="helical", module="2", teeth="20", helix_angle="30",
                                               face_width="14"), 2.0, 20, 30.0, 0.0, 0.3, 4, 21.2255, 24.0448, 23.260,
     23.094),
]
ROWS = SPUR_ROWS + HELICAL_ROWS
ROW_IDS = [row[0] for row in ROWS]


@pytest.mark.parametrize("name, spec, m, z, beta, x, j, k, w_n, w_t, r_c, r", ROWS, ids=ROW_IDS)
def test_each_row_of_the_plans_table_in_both_forms(name, spec, m, z, beta, x, j, k, w_n, w_t, r_c, r):
    reading = _span(spec)
    assert reading.kind == KIND_SPAN
    assert reading.k == k
    assert reading.w_mm == pytest.approx(w_n, abs=1e-4)
    assert reading.w_t_mm == pytest.approx(w_t, abs=1e-4)
    assert reading.contact_d / 2.0 == pytest.approx(r_c, abs=5e-4)
    assert reading.needed_face_mm == 0.0
    # The closed form, from the row's numbers alone, to the plan's figure and to the transverse form.
    closed = _closed_form(m, z, k, beta_deg=beta, x=x, j_n=j)
    assert closed == pytest.approx(w_n, abs=1e-4)
    assert reading.w_mm == pytest.approx(closed, abs=1e-9)
    # W_n = W_t cos β_b, and the contact radius by M1's r_c = √(r_b² + (W_n cos β_b / 2)²).
    beta_b = _beta_b(beta)
    assert reading.w_mm == pytest.approx(reading.w_t_mm * math.cos(beta_b), abs=1e-12)
    g = _derive(spec)
    rb = getattr(g, "section", g).rb
    assert reading.contact_d / 2.0 == pytest.approx(math.hypot(rb, reading.w_mm * math.cos(beta_b) / 2.0), abs=1e-12)
    # The pitch radius the table sets the contact against.
    assert getattr(g, "section", g).d / 2.0 == pytest.approx(r, abs=5e-4)
    # The backlash the row says was drawn is the gear's own (D3: 0.3 mm printed from module 1 up).
    assert getattr(g, "section", g).backlash == pytest.approx(j, abs=1e-12)


@pytest.mark.parametrize("name, spec, m, z, beta, x, j, k, w_n, w_t, r_c, r", ROWS, ids=ROW_IDS)
def test_k_is_the_textbook_k_through_d_m(name, spec, m, z, beta, x, j, k, w_n, w_t, r_c, r):
    rounded, exact = _textbook_k(m, z, beta, x)
    assert abs(exact - round(exact)) < 0.4, "a row this near a half would not tell the rules apart"
    assert _span(spec).k == rounded == k


def test_the_textbook_k_figures_the_review_gives():
    """F2's review gives zα/180 + 0.5 and the helical rule's unrounded figures; they are the same rule."""
    figures = [((1.5, 20), 2.72), ((1.0, 12), 1.83), ((2.0, 30), 3.83), ((1.25, 29), 3.72), ((1.25, 13), 1.94)]
    for (m, z), exact in figures:
        assert _textbook_k(m, z)[1] == pytest.approx(exact, abs=5e-3)
        assert _textbook_k(m, z)[1] == pytest.approx(z * 20.0 / 180.0 + 0.5, abs=1e-12)
    assert _textbook_k(1.5, 15, x=0.3)[1] == pytest.approx(2.62, abs=5e-3)
    # The review rounded 2.9449 up to 2.95 (from 2.945), so these are held to its last digit, not half of it.
    for (m, z, beta), exact in [((2.0, 20, 15.0), 2.95), ((1.5, 25, 20.0), 3.80), ((2.0, 20, 30.0), 3.79)]:
        assert _textbook_k(m, z, beta)[1] == pytest.approx(exact, abs=1e-2)


def test_the_machined_row_is_the_formula_only_and_not_shown():
    spec = _machined(module="1.5", teeth="20")
    g = _derive(spec)
    assert g.backlash == pytest.approx(0.45, abs=1e-12)
    assert _span(spec) == NONE
    figure = span_over(g, 3)
    assert figure.kind == KIND_SPAN and figure.k == 3
    assert figure.w_mm == pytest.approx(11.0678, abs=1e-4)
    assert figure.w_mm == pytest.approx(_closed_form(1.5, 20, 3, j_n=0.45), abs=1e-9)
    assert figure.contact_d / 2.0 == pytest.approx(15.143, abs=5e-4)


def test_the_faces_each_helical_row_needs():
    """§3.0: W_n sin β_b + 3 is 6.67, 8.09 and 12.97 mm, β_b 14.076°, 18.747°, 28.024°."""
    for (_name, _spec, _m, _z, beta, *_rest), (face, beta_b) in zip(
            HELICAL_ROWS, [(6.67, 14.076), (8.09, 18.747), (12.97, 28.024)]):
        w_n = _rest[-4]
        assert math.degrees(_beta_b(beta)) == pytest.approx(beta_b, abs=5e-4)
        assert w_n * math.sin(_beta_b(beta)) + 3.0 == pytest.approx(face, abs=5e-3)


def test_m1_the_helical_contact_radius_uses_w_n_cos_beta_b():
    """M1: with the first revision's √(r_b² + (W_t / 2)²) the β 20° gear would take k 3 (11.4156, the review's figure);
    with W_n cos β_b it takes the textbook's 4."""
    g = _derive(HELICAL_ROWS[1][1])
    target = g.section.d / 2.0
    wrong = min(range(1, 8), key=lambda k: abs(math.hypot(g.section.rb, span_over(g, k).w_t_mm / 2.0) - target))
    assert wrong == 3
    assert span_over(g, 3).w_mm == pytest.approx(11.4156, abs=1e-4)
    assert _span(HELICAL_ROWS[1][1]).k == 4


# -- the check owed by package A: the drawn outline --------------------------------------------------------------------


def _span_off_the_outline(section, k):
    """W_t across k teeth read off ``SpurGear.outline``'s recipe-A points.

    Every point of a drawn involute flank at radius r and polar angle θ came from one base-circle origin: θ − inv α_r
    on a flank that rises counter-clockwise, θ + inv α_r on one that rises clockwise (cos α_r = r_b / r). The base
    tangent length across k teeth is r_b times the angle between the first tooth's clockwise flank's origin and the
    k-th tooth's counter-clockwise flank's origin. Tooth 0 is centred at π / z (the outline's half period starts in
    the middle of a space at angle 0); the points of each flank give one origin each, to 1e-12 rad.
    """
    points = spur.SpurGear().outline(GearSpec(), section, "A")
    z, rb = section.teeth, section.rb
    low, high = section.flank_start_d / 2.0 + 1e-6, section.ra - 1e-6
    pitch = 2.0 * math.pi / z

    def origins(window, sign):
        found = []
        for x, y in points:
            r = math.hypot(x, y)
            theta = math.atan2(y, x) % (2.0 * math.pi)
            if low < r < high and window[0] < theta < window[1]:
                found.append(theta - sign * _inv(math.acos(rb / r)))
        return found

    first = origins((0.0, pitch / 2.0), +1)
    last = origins(((k - 0.5) * pitch, k * pitch), -1)
    assert len(first) >= 5 and len(last) >= 5
    assert max(first) - min(first) < 1e-12 and max(last) - min(last) < 1e-12
    return rb * (sum(last) / len(last) - sum(first) / len(first))


@pytest.mark.parametrize("name, spec, m, z, beta, x, j, k, w_n, w_t, r_c, r", ROWS, ids=ROW_IDS)
def test_the_span_read_off_the_drawn_outline_is_the_formula(name, spec, m, z, beta, x, j, k, w_n, w_t, r_c, r):
    g = _derive(spec)
    section = getattr(g, "section", g)
    reading = _span(spec)
    drawn = _span_off_the_outline(section, k)
    assert drawn == pytest.approx(reading.w_t_mm, abs=1e-4)
    assert drawn * math.cos(_beta_b(beta)) == pytest.approx(w_n, abs=1e-4)


def test_the_outline_holds_every_k_not_only_the_one_taken():
    section = _derive(SPUR_ROWS[0][1])
    for k in range(1, 6):
        assert _span_off_the_outline(section, k) == pytest.approx(span_over(section, k).w_mm, abs=1e-9)


# -- which gears show it ------------------------------------------------------------------------------------------------


SHOWN = [
    ("spur", _printed(module="1.5", teeth="20")),
    ("helical", _printed(kind="helical", module="1.5", teeth="25", helix_angle="20")),
    ("herringbone", _printed(kind="herringbone", module="1.5", teeth="25", helix_angle="20", face_width="20")),
    ("dog", _printed(kind="dog", module="1.5", teeth="20")),
    ("hub", _printed(kind="hub", module="1.5", teeth="20")),
]


@pytest.mark.parametrize("name, spec", SHOWN, ids=[s[0] for s in SHOWN])
def test_a_printed_external_involute_gear_shows_the_span(name, spec):
    reading = _span(spec)
    assert reading.kind == KIND_SPAN and reading.k >= 1 and reading.w_mm > 0.0


def test_a_dog_and_a_hub_read_as_the_spur_gear_they_are():
    plain = _span(SHOWN[0][1])
    assert _span(SHOWN[3][1]) == plain
    assert _span(SHOWN[4][1]) == plain


def test_a_herringbone_reads_as_its_helical_gear():
    helical = _span(_printed(kind="helical", module="1.5", teeth="25", helix_angle="20", face_width="20"))
    assert _span(SHOWN[2][1]) == helical


NOT_SHOWN = [
    ("machined spur", _machined(module="1.5", teeth="20")),
    ("machined helical", _machined(kind="helical", module="1.5", teeth="25", helix_angle="20")),
    ("machined dog", _machined(kind="dog", module="1.5", teeth="20")),
    ("printed spur ring", _printed(teeth_side="internal", module="1.5", teeth="60")),
    ("printed helical ring", _printed(teeth_side="internal", kind="helical", module="1.5", teeth="60",
                                      helix_angle="20")),
    ("printed herringbone ring", _printed(teeth_side="internal", kind="herringbone", module="1.5", teeth="60",
                                          helix_angle="20", face_width="20")),
    ("printed sleeve", _printed(kind="sleeve", module="1.5", teeth="30")),
    ("printed bevel", _printed(kind="bevel", module="1.5", teeth="20", mate_teeth="30")),
    # a crown gear: cos Σ = −N_mate / N (bevel.crown_shaft_angle(40, 20) is 120°)
    ("printed bevel crown", _printed(kind="bevel", module="1.5", teeth="40", mate_teeth="20", shaft_angle="120")),
]


@pytest.mark.parametrize("name, spec", NOT_SHOWN, ids=[s[0] for s in NOT_SHOWN])
def test_a_machined_gear_a_ring_a_sleeve_and_a_bevel_gear_show_none(name, spec):
    kind = kind_for(spec)
    g = kind.derive(spec)
    for recipe in ("A", "B"):
        assert span(g, recipe) == NONE
    assert span(g, kind.recipe_for(spec)).kind == KIND_NONE


def test_an_unknown_recipe_or_anything_else_is_none_and_never_raises():
    g = _derive(SHOWN[0][1])
    assert span(g, "") == NONE
    assert span(g, "C") == NONE
    for thing in (None, 0, "spur", object()):
        assert span(thing, "A") == NONE
        assert span_over(thing, 3) == NONE


def test_the_kinds_and_none():
    assert KINDS == ("span", "arcs", "narrow_face", "no_contact", "none")
    assert NONE == SpanReading("none", 0, 0.0, 0.0, 0.0, 0.0)


# -- a gear drawn with arcs ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize("name, spec", SHOWN, ids=[s[0] for s in SHOWN])
def test_a_printed_gear_drawn_with_arcs_reads_arcs_with_no_figure(name, spec):
    from dataclasses import replace
    arcs = replace(spec, recipe="B")
    assert kind_for(arcs).recipe_for(arcs) == "B"
    assert _span(arcs) == SpanReading(KIND_ARCS)


def test_a_machined_gear_drawn_with_arcs_is_none_not_arcs():
    spec = _machined(module="1.5", teeth="20", recipe="B")
    assert _span(spec) == NONE


# -- the contact bound --------------------------------------------------------------------------------------------------


def test_a_z_6_pinion_takes_k_1_with_its_contact_on_the_drawn_involute():
    spec = _printed(module="1", teeth="6")
    g = _derive(spec)
    reading = _span(spec)
    low, high = contact_bounds(g)
    assert reading.kind == KIND_SPAN and reading.k == 1
    assert low <= reading.contact_d / 2.0 <= high
    assert reading.w_mm == pytest.approx(_closed_form(1.0, 6, 1), abs=1e-9)
    assert reading.w_mm == pytest.approx(1.27819, abs=1e-5)


def test_a_z_6_pinion_shifted_minus_1_has_no_k_with_its_contact_under_the_tip():
    """x −1: the tip comes down a module, and even k 1's contact (2.835) is within 0.2 mm of it (2.8 is the bound)."""
    spec = _printed(module="1", teeth="6", profile_shift="-1")
    g = _derive(spec)
    low, high = contact_bounds(g)
    assert high == pytest.approx(g.da / 2.0 - 0.2, abs=1e-12)
    assert high == pytest.approx(2.8, abs=1e-9)
    assert span_over(g, 1).contact_d / 2.0 == pytest.approx(2.835, abs=5e-4)
    assert all(span_over(g, k).contact_d / 2.0 > high for k in range(1, 6))
    assert _span(spec) == SpanReading(KIND_NO_CONTACT)


def test_a_negative_shift_lowers_k_with_the_working_flank():
    """x −0.5 on m 1.5, z 20: the middle of the working flank, r + x m 14.25, is nearest k 1's contact (14.125) and
    above the involute's start (14.095); the textbook gives 1.47, also 1."""
    spec = _printed(module="1.5", teeth="20", profile_shift="-0.5")
    g = _derive(spec)
    reading = _span(spec)
    low, high = contact_bounds(g)
    assert reading.k == 1 == _textbook_k(1.5, 20, x=-0.5)[0]
    assert low == pytest.approx(14.0954, abs=5e-4)
    assert low <= reading.contact_d / 2.0 <= high
    assert reading.w_mm == pytest.approx(_closed_form(1.5, 20, 1, x=-0.5), abs=1e-9)


def test_the_lower_bound_is_where_the_apps_involute_starts():
    """The Planet's, the closest of the table to a bound: 8.112 against 7.635 (§3.0)."""
    g = _derive(SPUR_ROWS[5][1])
    low, high = contact_bounds(g)
    assert low == pytest.approx(max(g.flank_start_d, g.form_d) / 2.0, abs=1e-12)
    assert low == pytest.approx(7.635, abs=5e-4)
    assert high == pytest.approx(g.da / 2.0 - 0.2, abs=1e-12)


def test_choose_takes_the_nearest_inside_else_the_next_inward_or_outward():
    radii = [(1, 10.0), (2, 11.0), (3, 12.0), (4, 13.0)]
    assert choose(radii, 11.9, 9.0, 14.0) == 3
    # the nearest (2) under the involute's start: the next outward
    assert choose(radii, 11.1, 11.5, 14.0) == 3
    # the nearest (4) at the tip: the next inward
    assert choose(radii, 12.9, 9.0, 12.5) == 3
    # none inside
    assert choose(radii, 12.0, 12.2, 12.8) is None
    # a tie goes to the smaller k
    assert choose(radii, 11.5, 9.0, 14.0) == 2
    # on a bound is inside
    assert choose(radii, 12.0, 12.0, 12.0) == 3


# -- a helical face too narrow -------------------------------------------------------------------------------------------


def test_the_beta_30_row_at_face_12_reads_narrow_face_with_the_face_it_needs():
    """F2-INTERFACES §1: the β 30° row's narrow-face test is the same gear at 12 mm; it needs 12.97."""
    needed = 21.2255 * math.sin(_beta_b(30.0)) + 3.0
    for face in ("12", "10", "12.97"):
        reading = _span(_printed(kind="helical", module="2", teeth="20", helix_angle="30", face_width=face))
        assert reading.kind == KIND_NARROW_FACE
        assert (reading.k, reading.w_mm, reading.w_t_mm, reading.contact_d) == (0, 0.0, 0.0, 0.0)
        assert reading.needed_face_mm == pytest.approx(needed, abs=1e-4)
        assert reading.needed_face_mm == pytest.approx(12.9727, abs=1e-4)
    assert _span(_printed(kind="helical", module="2", teeth="20", helix_angle="30", face_width="12.98")).k == 4


@pytest.mark.parametrize("name, spec, m, z, beta, x, j, k, w_n, w_t, r_c, r", HELICAL_ROWS,
                         ids=[row[0] for row in HELICAL_ROWS])
def test_the_narrow_face_is_at_w_n_sin_beta_b_plus_3(name, spec, m, z, beta, x, j, k, w_n, w_t, r_c, r):
    from dataclasses import replace
    needed = _closed_form(m, z, k, beta_deg=beta) * math.sin(_beta_b(beta)) + 3.0
    under = _span(replace(spec, face_width=f"{needed - 0.005:.4f}"))
    over = _span(replace(spec, face_width=f"{needed + 0.005:.4f}"))
    assert under.kind == KIND_NARROW_FACE and under.needed_face_mm == pytest.approx(needed, abs=1e-9)
    assert over.kind == KIND_SPAN and over.k == k


def test_a_herringbone_is_measured_on_one_toothed_half():
    """§3.0: for a herringbone b is HelicalDerived.toothed_width, the face less the groove, halved."""
    base = dict(kind="herringbone", module="2", teeth="20", helix_angle="30")
    needed = 21.2255 * math.sin(_beta_b(30.0)) + 3.0          # 12.97: a whole face of 14 is not enough
    cases = [("14", "", KIND_NARROW_FACE), ("25.9", "", KIND_NARROW_FACE), ("26", "", KIND_SPAN),
             ("27.9", "2", KIND_NARROW_FACE), ("28", "2", KIND_SPAN)]
    for face, groove, kind in cases:
        spec = _printed(face_width=face, groove=groove, **base)
        g = _derive(spec)
        assert g.toothed_width == pytest.approx(float(face) / 2.0 - float(groove or 0) / 2.0, abs=1e-12)
        reading = _span(spec)
        assert reading.kind == kind, (face, groove)
        if kind == KIND_NARROW_FACE:
            assert reading.needed_face_mm == pytest.approx(needed, abs=1e-4)
        else:
            assert (reading.k, round(reading.w_mm, 4)) == (4, 21.2255)


def test_a_spur_gear_has_no_face_condition():
    assert _span(_printed(module="1.5", teeth="20", face_width="1")).kind == KIND_SPAN


# -- the Measured line's arithmetic ----------------------------------------------------------------------------------


SPUR_20 = SPUR_ROWS[0][1]


def test_measured_above_the_span():
    """§3.0 and F2-INTERFACES §6 (corrected by F2-0-REVIEW's S6): 0.041 mm a flank gives 2 (0.041 + 0.04) / cos 20°,
    0.172 mm a gear."""
    reading = _span(SPUR_20)
    line = measured(reading, reading.w_mm + 0.082, 20.0, 1.5)
    assert line.flank_mm == pytest.approx(0.041, abs=1e-12)
    assert line.backlash_mm == pytest.approx(2.0 * 0.081 / math.cos(math.radians(20.0)), abs=1e-12)
    assert line.backlash_mm == pytest.approx(0.172, abs=5e-4)
    assert not line.floored and not line.over_default


def test_measured_a_printer_adding_a_tenth_keeps_todays_three_tenths():
    """§3.2 / the review: e = 0.10 gives 0.298, so D3's 0.3 stays."""
    reading = _span(SPUR_20)
    line = measured(reading, reading.w_mm + 0.2, 20.0, 1.5)
    assert line.flank_mm == pytest.approx(0.1, abs=1e-12)
    assert line.backlash_mm == pytest.approx(0.298, abs=5e-4)


def test_measured_at_the_span_is_held_at_the_floor():
    reading = _span(SPUR_20)
    line = measured(reading, reading.w_mm, 20.0, 1.5)
    assert line.flank_mm == 0.0
    # 2 × 0.04 / cos 20° = 0.085, under the floor
    assert 2.0 * 0.04 / math.cos(math.radians(20.0)) < BACKLASH_FLOOR_MM
    assert line == Measured(flank_mm=0.0, backlash_mm=0.1, floored=True, over_default=False, default_mm=0.3)


def test_measured_below_the_span_is_held_at_the_floor():
    reading = _span(SPUR_20)
    for under in (0.02, 0.1, 0.5):
        line = measured(reading, reading.w_mm - under, 20.0, 1.5)
        assert line.flank_mm == pytest.approx(-under / 2.0, abs=1e-12)
        assert line.backlash_mm == BACKLASH_FLOOR_MM and line.floored


def test_measured_just_over_the_floor_is_not_floored():
    reading = _span(SPUR_20)
    # e where 2 (e + 0.04) / cos 20° = 0.1 exactly, and a hair over it
    e = 0.05 * math.cos(math.radians(20.0)) - 0.04
    line = measured(reading, reading.w_mm + 2.0 * (e + 1e-6), 20.0, 1.5)
    assert not line.floored and line.backlash_mm == pytest.approx(0.1, abs=1e-5) and line.backlash_mm > 0.1


def test_measured_uses_the_gears_own_normal_pressure_angle():
    """cos α_n of the gear, not cos 20°: a 25° spur gear, and a helical gear's normal (not transverse) angle."""
    spec_25 = _printed(module="1.5", teeth="20", pressure_angle="25")
    reading = _span(spec_25)
    line = measured(reading, reading.w_mm + 0.2, 25.0, 1.5)
    assert line.backlash_mm == pytest.approx(2.0 * 0.14 / math.cos(math.radians(25.0)), abs=1e-12)
    assert line.backlash_mm != pytest.approx(2.0 * 0.14 / math.cos(math.radians(20.0)), abs=1e-4)
    helical = _derive(HELICAL_ROWS[2][1])
    reading = _span(HELICAL_ROWS[2][1])
    line = measured(reading, reading.w_mm + 0.2, helical.normal_pressure_angle_deg, 2.0)
    assert line.backlash_mm == pytest.approx(2.0 * 0.14 / math.cos(math.radians(20.0)), abs=1e-12)


def test_measured_past_the_printed_default_is_said():
    """F2-REVIEW M2, ruled: the flag is against D3's printed default, the smaller of 0.3 mm and 0.3 × module (§3.2,
    U4), not 0.3 × module alone. A printer adding 0.12 mm a flank proposes 0.34 mm: flagged on a module 1 gear and,
    as the README says, on the module 1.5 coupon (0.3 × module there is 0.45, which alone would not flag it)."""
    for spec, module in ((SPUR_ROWS[1][1], 1.0), (SPUR_20, 1.5)):
        reading = _span(spec)
        line = measured(reading, reading.w_mm + 0.24, 20.0, module)
        assert line.backlash_mm == pytest.approx(2.0 * 0.16 / math.cos(math.radians(20.0)), abs=1e-12)
        assert line.backlash_mm == pytest.approx(0.3405, abs=5e-4)
        assert line.over_default is True
        assert line.default_mm == pytest.approx(0.3, abs=1e-12)


# (spec, module, D3's printed default): a module under 1, at 1 and above it
THRESHOLDS = [
    (_printed(module="0.8", teeth="30"), 0.8, 0.24),
    (_printed(module="1", teeth="12"), 1.0, 0.3),
    (_printed(module="1.5", teeth="20"), 1.5, 0.3),
]


@pytest.mark.parametrize("spec, module, default", THRESHOLDS, ids=["module 0.8", "module 1", "module 1.5"])
def test_the_flag_is_at_the_printed_default_each_side(spec, module, default):
    """j = 2 (e + 0.04) / cos 20° equal to the default at e = default cos 20° / 2 − 0.04; a micron of flank either
    side of it is one side of the flag or the other, and on it is not over."""
    reading = _span(spec)
    assert reading.kind == KIND_SPAN
    assert spur.printed_backlash(module) == pytest.approx(default, abs=1e-12)
    e = default * math.cos(math.radians(20.0)) / 2.0 - 0.04
    for step, over in ((-1e-3, False), (-1e-6, False), (0.0, False), (1e-6, True), (1e-3, True)):
        line = measured(reading, reading.w_mm + 2.0 * (e + step), 20.0, module)
        assert not line.floored
        assert line.default_mm == pytest.approx(default, abs=1e-12)
        assert line.over_default is over, (module, step)
    if module < 1.0:
        # under module 1 the default is 0.3 × module, so 0.3 mm itself is past it
        assert measured(reading, reading.w_mm + 2.0 * (0.15 * math.cos(math.radians(20.0)) - 0.04), 20.0,
                        module).over_default is True


def test_the_floor_is_flagged_where_it_passes_the_default():
    """At module 0.3 the default is 0.09, under the floor of 0.1: the floored proposal is itself past it, and said."""
    reading = _span(SPUR_20)
    line = measured(reading, reading.w_mm, 20.0, 0.3)
    assert line.floored and line.backlash_mm == 0.1 and line.default_mm == pytest.approx(0.09, abs=1e-12)
    assert line.over_default is True


def test_measured_is_none_with_no_reading_typed_or_no_figure():
    reading = _span(SPUR_20)
    assert measured(reading, None, 20.0, 1.5) is None
    for kind in (NONE, SpanReading(KIND_ARCS), SpanReading(KIND_NO_CONTACT),
                 SpanReading(KIND_NARROW_FACE, needed_face_mm=13.0)):
        assert measured(kind, 11.2, 20.0, 1.5) is None


def test_the_constants_are_the_plans():
    assert span_mod.TIP_MARGIN_MM == 0.2
    assert span_mod.FACE_MARGIN_MM == 3.0
    assert span_mod.KEPT_PLAY_MM == 0.04
    assert span_mod.BACKLASH_FLOOR_MM == 0.1
