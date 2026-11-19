"""Stage F4's maths (PLAN-PRINTED §5.1, §5.3, §5.6: F4-0 and package A): what one printed tooth is rated to take, and
the Box's Allowable stress.

Every worked row is held twice: the module's figure against the plan's (§5.3's table, with the three-decimal forces
F4's review reproduced), and the same figure worked out here, independently of `gears.strength`, from the app's own
drawn tooth and the formula's source. The independent working (:func:`beam`) finds the critical section by bisecting
along the drawn fillet for the point whose tangent makes 30° (60° on a ring) with the centreline, takes the tip corner
by bisecting the drawn flank for the outer diameter and its normal by differencing the flank, and gets YF from the
bending moment a unit normal force makes about the section's middle (beam statics), not from the expression for YF;
YS is the source's expression written out here. A helical gear's virtual spur gear is drawn here from ISO's zn.
"""

import itertools
import math
from dataclasses import replace

import pytest

from gear_generator.gears import internal, kind_for, spur, strength
from gear_generator.gears.helical import HelicalDerived
from gear_generator.gears.internal import InternalDerived
from gear_generator.spec import GearSpec
from gear_generator.workbook import model, schema

PRINTED = dict(process="printed")


# -- the gears of §5.3 ---------------------------------------------------------------------------------------------

GEARS = {
    "A1": dict(module="1.5", teeth="20", face_width="10", **PRINTED),
    "A2": dict(module="1.5", teeth="60", face_width="10", **PRINTED),
    "A3": dict(module="1.5", teeth="20", face_width="10", backlash="0", **PRINTED),
    "A4": dict(kind="helical", helix_angle="20", module="1.5", teeth="20", face_width="12", **PRINTED),
    "A5": dict(kind="herringbone", helix_angle="20", module="1.5", teeth="20", face_width="12", groove="4", **PRINTED),
    "A6": dict(module="1", teeth="54", face_width="10", teeth_side="internal", bore="", **PRINTED),
    "A7": dict(module="1.5", teeth="20", face_width="10", recipe="B", **PRINTED),
    "A8": dict(module="1", teeth="12", face_width="10", **PRINTED),
    "A9": dict(kind="helical", helix_angle="20", module="2", teeth="36", face_width="10", teeth_side="internal",
               bore="", **PRINTED),
    "A10": dict(module="1", teeth="33", face_width="10", teeth_side="internal", bore="", **PRINTED),
}

# §5.3's table at 17 MPa: Y_F, Y_S, q_s, past the range, holds (N, the table's two decimals), holds (N·m). The forces
# to three decimals are F4's review's (PLAN-PRINTED-REVIEW, *The worked rows, recomputed*, and A9 in its re-check).
ROWS = {
    "A1": (4.1931, 1.5749, 2.131, False, 38.61, 0.5792, 38.614),
    "A2": (3.2708, 1.6975, 2.458, False, 45.93, 2.0668, 45.929),
    "A3": (3.3258, 1.6685, 2.370, False, 45.95, 0.6893, 45.952),
    "A4": (3.8769, 1.6089, 2.226, False, 49.06, 0.7831, 49.058),
    "A5": (3.8769, 1.6089, 2.226, False, 32.71, 0.5221, 32.705),
    "A6": (2.2574, 2.5535, 8.341, True, 29.49, 0.7963, 29.492),
    "A7": (3.4536, 1.6274, 2.288, False, 45.37, 0.6805, 45.369),
    "A8": (6.8916, 1.4151, 1.701, False, 17.43, 0.1046, 17.432),
    "A9": (2.0408, 2.6948, 8.500, True, 61.82, 2.3685, 61.823),
}


def derived_of(spec: GearSpec):
    kind = kind_for(spec)
    return kind.derive(spec), kind.recipe_for(spec)


def rating_of(name: str, **changed: str) -> strength.ToothRating:
    spec = GearSpec(**{**GEARS[name], **changed})
    derived, recipe = derived_of(spec)
    return strength.rate(derived, recipe)


# -- the independent working ---------------------------------------------------------------------------------------

def _turned(p, angle):
    c, s = math.cos(angle), math.sin(angle)
    return (c * p[0] - s * p[1], s * p[0] + c * p[1])


def _bisect(f, lo, hi, steps=200):
    f_lo = f(lo)
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)
        if (f_mid > 0) == (f_lo > 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def virtual_here(g: HelicalDerived):
    """ISO's virtual spur gear, worked here: zn = z / (cos² βb cos β), βb = asin (sin β cos αn), drawn by the app's
    own section routines with the normal module, pressure angle and backlash, the shift and the fillet."""
    s = g.section
    beta, alpha_n = math.radians(g.helix_angle_deg), math.radians(g.normal_pressure_angle_deg)
    beta_b = math.asin(math.sin(beta) * math.cos(alpha_n))
    zn = s.teeth / (math.cos(beta_b) ** 2 * math.cos(beta))
    if isinstance(s, InternalDerived):
        return internal.section(zn, s.module, g.normal_pressure_angle_deg, s.face_width, None, s.backlash, s.fillet)
    return spur.profile(zn, s.module, g.normal_pressure_angle_deg, s.face_width, s.bore, s.backlash, s.fillet,
                        shift=s.shift)


def section_here(spec: GearSpec):
    """The section rated, the pitch diameter the force is taken at, the toothed width, the recipe."""
    g, recipe = derived_of(spec)
    if isinstance(g, HelicalDerived):
        width = 2.0 * g.toothed_width if g.kind == "herringbone" else g.section.face_width
        return virtual_here(g), g.section.d, width, recipe
    return g, g.d, g.face_width, recipe


def drawn_tooth(g, recipe):
    """The loaded side of one tooth as the app draws it, turned so the tooth's centreline (polar angle π / z) is +u:
    the fillet's centre and its two drawn ends, its radius, the tip corner and the flank's unit normal there."""
    ring = isinstance(g, InternalDerived)
    side = internal if ring else spur
    if recipe == "B":
        flank = side.arc_flank(g)
        ends = (flank.flank_touch, flank.root_touch)
        centre, radius = flank.centre, flank.radius
        start = math.atan2(flank.flank_touch[1] - centre[1], flank.flank_touch[0] - centre[0])

        def on_arc(phi):
            return (centre[0] + radius * math.cos(phi), centre[1] + radius * math.sin(phi))

        def radius_at(phi):
            return math.hypot(*on_arc(phi)) - g.ra
        sweep = next(start + sign * 1.5 for sign in (1, -1) if (radius_at(start) > 0) != (radius_at(start + sign * 1.5) > 0))
        phi = _bisect(radius_at, start, sweep)
        tip, tangent = on_arc(phi), (-math.sin(phi), math.cos(phi))
    else:
        flank = side.involute_flank(g)
        ends = (flank.line_outer if ring else flank.line_inner, flank.root_touch)
        point = (lambda t: internal.flank_point(g, t)) if ring else (lambda t: spur.involute_point(g.rb, g.phi, t))
        t = _bisect(lambda t: math.hypot(*point(t)) - g.ra, 0.0, 5.0)
        tip = point(t)
        before, after = point(t - 1e-6), point(t + 1e-6)
        tangent = (after[0] - before[0], after[1] - before[1])
    turn = -math.pi / g.teeth
    tip, tangent = _turned(tip, turn), _turned(tangent, turn)
    length = math.hypot(*tangent)
    normal = (-tangent[1] / length, tangent[0] / length)
    if normal[1] < 0:
        normal = (-normal[0], -normal[1])
    return dict(ring=ring, centre=_turned(flank.fillet_centre, turn), ends=[_turned(e, turn) for e in ends],
                rho=g.fillet, tip=tip, normal=normal, flank=flank)


def section_point(tooth, tangent_deg):
    """The point of the drawn fillet whose tangent makes `tangent_deg` with the centreline, by bisection along it,
    with the tangent there."""
    c, rho = tooth["centre"], tooth["rho"]
    a0, a1 = (math.atan2(e[1] - c[1], e[0] - c[0]) for e in tooth["ends"])
    sweep = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi

    def tangent_angle(phi):
        return math.degrees(math.atan2(abs(math.cos(phi)), abs(math.sin(phi))))
    s = _bisect(lambda s: tangent_angle(a0 + sweep * s) - tangent_deg, 0.0, 1.0)
    phi = a0 + sweep * s
    return (c[0] + rho * math.cos(phi), c[1] + rho * math.sin(phi)), tangent_angle(phi), s


def beam(g, recipe, width, tangent_deg=None):
    """YF by beam statics: the bending moment of a unit normal force at the tip about the critical section's middle,
    σ = 6 M / (b s²), and YF = σ b m / Ft with Ft = cos αn for that unit normal force. YS by the source's expression."""
    tooth = drawn_tooth(g, recipe)
    if tangent_deg is None:
        tangent_deg = 60.0 if tooth["ring"] else 30.0
    q, _, _ = section_point(tooth, tangent_deg)
    s = 2.0 * abs(q[1])
    p, n = tooth["tip"], tooth["normal"]
    moment = abs((p[0] - q[0]) * n[1] - p[1] * n[0])
    m = g.module
    y_f = 6.0 * moment * m / (s * s * math.cos(g.alpha))
    h = abs(p[0] - p[1] * n[0] / n[1] - q[0])
    big_l, q_s = s / h, s / (2.0 * tooth["rho"])
    y_s = (1.2 + 0.13 * big_l) * max(q_s, 1.0) ** (1.0 / (1.21 + 2.3 / big_l))
    return dict(y_f=y_f, y_s=y_s, q_s=q_s, s=s, h=h, m=m, width=width)


def beam_of(name):
    g, d, width, recipe = section_here(GearSpec(**GEARS[name]))
    out = beam(g, recipe, width)
    force = 17.0 * width * out["m"] / (out["y_f"] * out["y_s"])
    return dict(out, force=force, torque=force * d / 2000.0, d=d)


# -- §5.3's rows ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(ROWS))
def test_each_worked_row_is_the_plans_figure(name):
    y_f, y_s, q_s, past, force_2, torque, force_3 = ROWS[name]
    r = rating_of(name)
    assert r.rated and r.why == ""
    assert r.y_f == pytest.approx(y_f, abs=1e-4) and r.y_s == pytest.approx(y_s, abs=1e-4)
    assert round(r.q_s, 3) == q_s and r.past_range is past
    held = strength.holds(r)
    assert held == pytest.approx(force_2, abs=1e-2) and held == pytest.approx(force_3, abs=1e-3)
    assert strength.torque_held(r, held) == pytest.approx(torque, abs=1e-4)


@pytest.mark.parametrize("name", sorted(ROWS))
def test_each_worked_row_by_beam_statics_on_the_drawn_tooth(name):
    """The same figures, worked out here independently of the module (above), to the plan's digit."""
    y_f, y_s, q_s, past, force_2, torque, force_3 = ROWS[name]
    here = beam_of(name)
    assert here["y_f"] == pytest.approx(y_f, abs=1e-4) and here["y_s"] == pytest.approx(y_s, abs=1e-4)
    assert round(here["q_s"], 3) == q_s and (here["q_s"] >= 8.0) is past
    assert here["force"] == pytest.approx(force_3, abs=1e-3) and here["torque"] == pytest.approx(torque, abs=1e-4)
    r = rating_of(name)
    assert r.s_fn == pytest.approx(here["s"], abs=1e-9) and r.h_f == pytest.approx(here["h"], abs=1e-9)
    assert r.y_f == pytest.approx(here["y_f"], rel=1e-9)


def test_a_helical_gears_force_and_torque_are_at_its_transverse_diameter_a_rings_included():
    """§5.1, M2: A4's d 31.9253 and zn 23.735; A9's d 76.6208 (z mn / cos β), never z mn = 72, and zn 42.723."""
    a4, a9 = rating_of("A4"), rating_of("A9")
    assert (round(a4.d, 4), round(a4.teeth, 3), a4.module, a4.width) == (31.9253, 23.735, 1.5, 12.0)
    assert (round(a9.d, 4), round(a9.teeth, 3), a9.module, a9.ring) == (76.6208, 42.723, 2.0, True)
    assert strength.torque_held(a9, strength.holds(a9)) == pytest.approx(61.823 * 76.6208 / 2000, abs=1e-4)
    assert strength.torque_held(a9, strength.holds(a9)) != pytest.approx(61.823 * 72 / 2000, abs=1e-2)


def test_a_ring_whose_tips_lie_inside_its_base_circle_is_not_rated_with_its_reason():
    """M1 (A10): m 1, z 33 at 20°, its tips 31.000 mm against the base circle's 31.010, is not rated; z 34 is."""
    r = rating_of("A10")
    assert (r.rated, r.short, r.ring) == (False, "tips inside the base circle", True)
    assert r.why == ("its tips lie inside its base circle (31.000 mm against 31.010), where its teeth cannot be "
                     "involute, and the rating needs an involute tip to load")
    with pytest.raises(ValueError, match="not rated: its tips lie inside its base circle"):
        strength.holds(r)
    z34 = rating_of("A10", teeth="34")
    assert z34.rated and (round(z34.y_f, 4), round(z34.y_s, 4), round(z34.q_s, 3)) == (2.1242, 2.6416, 8.756)


@pytest.mark.parametrize("teeth", range(20, 34))
def test_every_ring_of_33_teeth_or_fewer_at_20_degrees_is_not_rated(teeth):
    g, recipe = derived_of(GearSpec(**{**GEARS["A10"], "teeth": str(teeth)}))
    assert g.tip_below_base and not strength.rate(g, recipe).rated


def test_a_helical_ring_is_told_by_its_virtual_ring_which_never_disagrees_with_its_drawn_section():
    """§5.1, M1: the condition on a helical ring is its virtual ring's; in a sweep it agrees with the drawn section."""
    for beta, teeth, alpha in itertools.product((10, 20, 30, 45), (24, 30, 34, 38, 44, 60), ("14.5", "20", "25")):
        spec = GearSpec(kind="helical", helix_angle=str(beta), module="1", teeth=str(teeth), pressure_angle=alpha,
                        face_width="10", bore="", teeth_side="internal", **PRINTED)
        g, recipe = derived_of(spec)
        virtual = virtual_here(g)
        assert virtual.tip_below_base == g.section.tip_below_base
        assert strength.rate(g, recipe).rated is not virtual.tip_below_base
    g, recipe = derived_of(GearSpec(kind="helical", helix_angle="10", module="1", teeth="20", face_width="10", bore="",
                                    teeth_side="internal", **PRINTED))
    r = strength.rate(g, recipe)
    assert g.section.tip_below_base and not r.rated and r.short == "tips inside the base circle"
    assert r.why.startswith(f"its tips lie inside its base circle ({g.section.da:.3f} mm against {g.section.db:.3f}), ")


def test_a_pointed_tooth_is_not_rated():
    """The review's S6: a tooth whose flanks meet below the outer diameter (never built: a validation error) says
    *not rated* rather than load a point past its apex; outside and ring."""
    outside = spur.profile(10, 1.0, 20.0, 10.0, 0.0, 1.0, 0.38)
    ring = internal.section(60, 1.0, 20.0, 10.0, None, 1.6, 0.15)
    assert outside.tip_thickness < 0 and ring.tip_thickness < 0
    for g in (outside, ring):
        r = strength.rate(g, "A")
        assert (r.rated, r.short) == (False, "pointed teeth")
        assert r.why == ("its teeth come to a point below the outer diameter, so there is no tip corner to load (a "
                         "pointed tooth is never built)")
    spec = GearSpec(module="1", teeth="10", backlash="1", face_width="10", bore="")
    assert any("come to a point" in d.message for d in kind_for(spec).validate(spec))


def test_a_bevel_gear_is_not_rated_and_nothing_raises():
    g, recipe = derived_of(GearSpec(kind="bevel", module="1.5", teeth="20", mate_teeth="40", face_width="8", bore="3",
                                    **PRINTED))
    r = strength.rate(g, recipe)
    assert (r.rated, r.short) == (False, "a bevel gear")
    assert r.why == ("a bevel gear's tooth tapers along its face, and rating it needs ISO 10300's virtual gear at the "
                     "mean cone, which this check does not work out")
    for odd in (None, object(), 3.0):
        assert strength.rate(odd, "A").rated is False
    assert strength.rate(derived_of(GearSpec(**GEARS["A1"]))[0], "Z").rated is False


# -- the formula's pieces ------------------------------------------------------------------------------------------

def test_the_stress_correction_factor_at_a_hand_worked_point():
    """sFn 3, hF 2.4, ρF 0.6: L = 1.25, qs = 2.5, 1.2 + 0.13 L = 1.3625, exponent 1 / (1.21 + 1.84) = 0.327869, and
    2.5 ^ 0.327869 = 1.350430, so YS = 1.3625 × 1.350430 = 1.839961. A qs under 1 is taken at 1."""
    assert strength.stress_correction(3.0, 2.4, 2.5) == pytest.approx(1.839961, abs=1e-6)
    assert strength.stress_correction(3.0, 2.4, 0.5) == pytest.approx(1.3625, abs=1e-12)


@pytest.mark.parametrize("name", ["A1", "A3", "A6", "A7", "A8", "A9"])
def test_the_critical_section_is_on_the_drawn_fillet_where_its_tangent_is_at_30_degrees_or_60_on_a_ring(name):
    g, d, width, recipe = section_here(GearSpec(**GEARS[name]))
    tooth = drawn_tooth(g, recipe)
    tangent = 60.0 if tooth["ring"] else 30.0
    q, angle, along = section_point(tooth, tangent)
    c = tooth["centre"]
    assert angle == pytest.approx(tangent, abs=1e-9) and 0.0 < along < 1.0         # on the arc, between its ends
    assert math.hypot(q[0] - c[0], q[1] - c[1]) == pytest.approx(tooth["rho"], abs=1e-12)
    assert rating_of(name).s_fn == pytest.approx(2.0 * abs(q[1]), abs=1e-9)
    assert rating_of(name).rho_f == tooth["rho"]


@pytest.mark.parametrize("spec, ring", [
    (dict(module="1.5", teeth="20", face_width="10", backlash="0"), False),          # §5.1: α_a 31.32°, γ_a 1.810°
    (dict(module="1.5", teeth="20", face_width="10", **PRINTED), False),
    (dict(module="2", teeth="17", face_width="10", profile_shift="0.4"), False),
    (dict(module="1", teeth="54", face_width="10", teeth_side="internal", bore="", **PRINTED), True),
    (dict(module="2", teeth="80", face_width="10", teeth_side="internal", bore=""), True),
])
def test_alpha_f_is_alpha_a_less_gamma_a_outside_and_plus_it_on_a_ring_on_recipe_a(spec, ring):
    """ISO's own relation, on the tooth as drawn: α_a = arccos (rb / ra), γ_a the tooth's half-angle at its tip read
    from the drawn flank (its backlash in it)."""
    g, recipe = derived_of(GearSpec(**spec))
    alpha_a = math.acos(g.rb / g.ra)
    if ring:
        gamma_a = math.pi / g.teeth - internal.half_space_angle(g, g.ra)
        want = alpha_a + gamma_a
    else:
        gamma_a = math.pi / g.teeth - spur.involute_polar(g, g.ra)
        want = alpha_a - gamma_a
    assert strength.rate(g, recipe).alpha_f_deg == pytest.approx(math.degrees(want), abs=1e-9)
    if spec.get("backlash") == "0":
        assert (round(math.degrees(alpha_a), 2), round(math.degrees(gamma_a), 3)) == (31.32, 1.810)
        assert round(math.degrees(want), 3) == 29.512


def test_virtual_teeth_are_isos_and_not_rounded():
    """§5.1: zn = z / (cos² βb cos β); A4 gives 23.735, against 23.553 by z / cos³ βb and 24.103 by z / cos³ β."""
    zn = strength.virtual_teeth(20, 20.0, 20.0)
    assert round(zn, 3) == 23.735
    beta_b = math.asin(math.sin(math.radians(20)) * math.cos(math.radians(20)))
    assert round(20 / math.cos(beta_b) ** 3, 3) == 23.553 and round(20 / math.cos(math.radians(20)) ** 3, 3) == 24.103
    g, _ = derived_of(GearSpec(**GEARS["A4"]))
    assert strength.virtual_section(g).teeth == zn == virtual_here(g).teeth


def test_outside_gears_stay_in_the_stress_factors_range_and_rings_pass_it():
    """§5.1: over outside gears the app builds (modules 0.5 to 3, 6 to 300 teeth, 14.5° to 30°, printed and machined,
    both recipes) q_s is about 1.2 to 3.5 and the 30° point on the drawn fillet; a default ring with an involute tip
    passes 8 nearly always, and says so."""
    outside, rings = [], []
    for m, z, alpha, process, recipe in itertools.product(("0.5", "1", "1.5", "3"), ("6", "8", "12", "20", "40", "100",
                                                                                       "300"),
                                                        ("14.5", "20", "30"), ("printed", "machined"), ("A", "B")):
        spec = GearSpec(module=m, teeth=z, pressure_angle=alpha, face_width="10", bore="", process=process,
                        recipe=recipe)
        kind = kind_for(spec)
        if any(d.is_error for d in kind.validate(spec)):
            continue
        r = strength.rate(kind.derive(spec), recipe)
        assert r.rated, (m, z, alpha, process, recipe, r.why)
        outside.append(r.q_s)
    for m, z, recipe in itertools.product(("0.5", "1", "3"), ("34", "40", "54", "80", "150"), ("A", "B")):
        g, _ = derived_of(GearSpec(module=m, teeth=z, face_width="10", bore="", teeth_side="internal", recipe=recipe,
                                   **PRINTED))
        r = strength.rate(g, recipe)
        assert r.rated and r.past_range is (r.q_s >= 8.0)
        rings.append(r)
    assert len(outside) > 200 and 1.2 < min(outside) and max(outside) < 3.6
    assert 7.7 < min(r.q_s for r in rings) and sum(r.past_range for r in rings) >= 0.9 * len(rings)
    assert strength.QS_RANGE == (1.0, 8.0)


def test_a_herringbone_carries_on_its_face_less_its_groove():
    a4, a5 = rating_of("A4"), rating_of("A5")
    assert (a4.width, a5.width) == (12.0, 8.0)
    assert strength.holds(a5) == pytest.approx(strength.holds(a4) * 8.0 / 12.0, rel=1e-12)
    assert rating_of("A5", groove="").width == 12.0


def test_backlash_lowers_what_a_tooth_holds_and_face_width_raises_it_in_proportion():
    """§5.3: A1, thinned by its printed 0.3 mm, holds 38.61 N against A3's 45.95 with none; A1 machined (blank
    backlash 0.45 mm) 35.044 N. Twice the face holds twice the force."""
    a1, a3 = rating_of("A1"), rating_of("A3")
    assert strength.holds(a1) < strength.holds(a3)
    assert strength.holds(rating_of("A1", process="")) == pytest.approx(35.044, abs=1e-3)
    wide = rating_of("A1", face_width="20")
    assert strength.holds(wide) == pytest.approx(2.0 * strength.holds(a1), rel=1e-12)
    assert strength.holds(a1, width=5.0) == pytest.approx(0.5 * strength.holds(a1), rel=1e-12)


def test_holds_takes_the_allowable_and_the_two_way_allowance():
    a1 = rating_of("A1")
    assert strength.holds(a1, allowable=34.0) == pytest.approx(2.0 * strength.holds(a1), rel=1e-12)
    assert strength.holds(a1, two_way=True) == pytest.approx(0.7 * strength.holds(a1), rel=1e-12)
    assert strength.torque_held(a1, 100.0) == pytest.approx(100.0 * 30.0 / 2000.0, rel=1e-12)
    assert (strength.ALLOWABLE_DEFAULT, strength.TWO_WAY, strength.PLANET_SHARE) == (17.0, 0.7, 1.25)
    assert (strength.TANGENT_OUTSIDE, strength.TANGENT_RING) == (30.0, 60.0)


@pytest.mark.parametrize("text, mpa", [("", 17.0), ("  ", 17.0), ("34", 34.0), (" 12.5 ", 12.5), ("0", 17.0),
                                       ("-3", 17.0), ("−3", 17.0), ("x", 17.0), ("inf", 17.0), ("nan", 17.0)])
def test_allowable_mpa_reads_a_figure_above_zero_and_anything_else_is_the_provisional_17(text, mpa):
    assert strength.allowable_mpa(text) == mpa


# -- the app's tooth against the tables, and the 30° section against the beam's worst (F4-0's note, the review's S4) --

@pytest.mark.parametrize("module, teeth, y_f", [("2", "20", 3.326), ("2", "40", 2.755), ("2", "100", 2.546),
                                                 ("1", "20", 3.696)])
def test_the_apps_tooth_against_isos_generated_tooth(module, teeth, y_f):
    """§5.1: unshifted, no backlash, the app's YF is 3.326, 2.755 and 2.546 at module 2 and 3.696 at module 1 (depth
    2.4 m), against ISO's generated tooth's 2.800, 2.405, 2.195 and 2.800 (the review's own coding of Method B)."""
    r = strength.rate(*derived_of(GearSpec(module=module, teeth=teeth, face_width="10", backlash="0")))
    assert r.y_f == pytest.approx(y_f, abs=5.5e-4)      # m 2 z 100 is 2.54547: §5.1's 2.546 is 2.5455 rounded again


@pytest.mark.parametrize("name, spec, over, over_with_y_s", [
    ("A1", GEARS["A1"], 5.2, 3.9), ("A2", GEARS["A2"], 3.6, 2.6), ("A8", GEARS["A8"], 9.2, 7.4),
    ("m2_z100", dict(module="2", teeth="100", face_width="10", backlash="0"), 2.5, 1.7)])
def test_the_30_degree_section_reads_under_the_beams_worst_by_the_reviews_figures(name, spec, over, over_with_y_s):
    """The beam's worst section, scanning the drawn fillet's tangent from 1° to 89°, against the 30° one: up to about
    9 % in YF, about 7 % with YS taken at each point, on small pinions (F4-0's note)."""
    g, d, width, recipe = section_here(GearSpec(**spec))
    at_30 = beam(g, recipe, width)
    scan = [beam(g, recipe, width, tangent / 10.0) for tangent in range(10, 890, 5)]
    worst = max(r["y_f"] for r in scan)
    worst_with = max(r["y_f"] * r["y_s"] for r in scan)
    assert 100.0 * (worst / at_30["y_f"] - 1.0) == pytest.approx(over, abs=0.06)
    assert 100.0 * (worst_with / (at_30["y_f"] * at_30["y_s"]) - 1.0) == pytest.approx(over_with_y_s, abs=0.06)


@pytest.mark.parametrize("name", ["A1", "A6", "A7", "A8"])
def test_the_form_factor_is_the_beams_on_the_drawn_outline(name):
    """F4-0's cross-check: the tip corner and the fillet's two ends the working uses are vertices of the gear's own
    outline (kind.outline, what the preview draws and the sketch cuts), and YF from the bending moment about the
    critical section agrees with the module's expression for four gears: spur on recipe A and B, a small pinion and
    a ring."""
    spec = GearSpec(**GEARS[name])
    kind = kind_for(spec)
    g, recipe = derived_of(spec)
    outline = kind.outline(spec, g, recipe)
    tooth = drawn_tooth(g, recipe)
    back = math.pi / g.teeth

    def on_outline(p):
        return min(math.hypot(p[0] - o[0], p[1] - o[1]) for o in outline) < 1e-9
    assert on_outline(_turned(tooth["tip"], back))
    assert all(on_outline(_turned(e, back)) for e in tooth["ends"])
    here = beam(g, recipe, g.face_width)
    assert strength.rate(g, recipe).y_f == pytest.approx(here["y_f"], rel=1e-9)


# -- the Box's Allowable stress (§5.4) -----------------------------------------------------------------------------

def test_the_boxs_allowable_stress_follows_nozzle_with_its_note():
    keys = [s.key for s in schema.BOX_SETTINGS]
    assert keys.index("allowable") == keys.index("nozzle") + 1 and keys.index("units") == keys.index("allowable") + 1
    setting = {s.key: s for s in schema.BOX_SETTINGS}["allowable"]
    assert (setting.title, setting.default, setting.numeric, setting.required) == ("Allowable stress (MPa)", "17", True,
                                                                                   False)
    assert setting.note == ("printed teeth only: the root stress a tooth is rated to take once; blank: 17, provisional "
                            "(about half a printed PLA data sheet's 35 MPa within the layers) until you type your own "
                            "figure here")
    assert model.Box().allowable == "" and model.checked_allowable(model.Box()) == ""


def _written(tmp_path, spec):
    from test_workbook_model import write
    return write(tmp_path, spec)


@pytest.mark.parametrize("typed, said", [
    ("x", "Box!B11: Allowable stress must be a number (got 'x')."),
    ("0", "Box!B11: Allowable stress must be more than zero (got '0')."),
    ("-17", "Box!B11: Allowable stress must be more than zero (got '-17')."),
])
def test_an_allowable_that_does_not_read_is_an_error_at_its_cell_and_the_checks_use_17(tmp_path, typed, said):
    from test_workbook_model import edit, read, reducer
    path = _written(tmp_path, reducer())
    edit(path, "Box", {"B9": "Printed", "B11": typed})
    spec, diagnostics = read(path)
    assert [d.message for d in diagnostics] == [said]
    assert strength.allowable_mpa(model.checked_allowable(spec.box)) == 17.0


@pytest.mark.parametrize("typed, kept, mpa", [("34", "34", 34.0), (12.5, "12.5", 12.5), ("", "", 17.0)])
def test_an_allowable_that_reads_is_kept_as_typed_and_a_blank_is_17(tmp_path, typed, kept, mpa):
    from test_workbook_model import edit, read, reducer
    path = _written(tmp_path, reducer())
    edit(path, "Box", {"B9": "Printed", "B11": typed})
    spec, diagnostics = read(path)
    assert diagnostics == [] and spec.box.allowable == kept and model.checked_allowable(spec.box) == kept
    assert strength.allowable_mpa(model.checked_allowable(spec.box)) == mpa


def test_new_workbook_writes_17_and_reads_it_back(tmp_path):
    from test_workbook_model import read
    template = model.template("NewBox")
    rows = {row[0]: row[1:] for row in model.to_sheets(template)[0].rows[1:]}
    assert rows["Allowable stress (MPa)"] == [17, {s.key: s for s in schema.BOX_SETTINGS}["allowable"].note]
    spec, diagnostics = read(_written(tmp_path, template))
    assert diagnostics == [] and spec.box.allowable == "17" and spec.box == template.box
    assert strength.allowable_mpa(model.checked_allowable(spec.box)) == strength.ALLOWABLE_DEFAULT


def test_the_allowable_is_not_a_gears_field_and_a_gearbox_built_in_code_writes_it_blank():
    """§5.4, H9: GearSpec gains nothing, so no record, sidecar or plan sees it."""
    from test_workbook_model import reducer
    box = {row[0]: row[1] for row in model.to_sheets(reducer())[0].rows[1:]}
    assert box["Allowable stress (MPa)"] == ""
    typed = replace(reducer(), box=replace(reducer().box, process="printed", allowable="34"))
    plain = replace(reducer(), box=replace(reducer().box, process="printed"))
    for gear in reducer().gears:
        assert gear.gear_spec(typed.box) == gear.gear_spec(plain.box)
    assert "allowable" not in GearSpec().to_dict() and not hasattr(GearSpec(), "allowable")



# -- the rounding, and F4-0's stubs ----------------------------------------------------------------------------------

@pytest.mark.parametrize("force, said", [(38.614, "39"), (229.885, "230"), (16.851, "17"), (9.94, "9.9"),
                                         (9.96, "10"), (8.6, "8.6")])
def test_a_force_is_said_whole_from_10_n_and_to_a_tenth_under_it(force, said):
    assert strength.newtons(force) == said


@pytest.mark.parametrize("torque, said", [(0.5792, "0.58"), (2.0668, "2.07"), (12.34, "12.3"), (123.4, "123")])
def test_a_torque_is_said_to_a_hundredth_under_10_n_m(torque, said):
    assert strength.newton_metres(torque) == said
    assert strength.times(13.643) == "13.6" and strength.megapascals(17.0) == "17"
    assert strength.megapascals(12.5) == "12.5"


def test_the_names_b_and_c_meet_through_are_the_interfaces():
    """F4-INTERFACES §4, §5: the label and the two wordings F4-0 fixed. What B's mesh strengths and C's row return is
    held by their own tests (tests/test_strength_workbook.py, tests/test_strength_form.py), now the stubs are filled."""
    from gear_generator import ui_text
    from gear_generator.workbook import strength as mesh
    assert ui_text.HOLDS_LABEL == "Holds once"
    assert (mesh.TURNS_UNLOADED, mesh.NOT_SHARED_OUT) == (
        "turns unloaded here", "the torque past a shared output is not shared out (not worked out)")



# -- §5.3's mesh rows, worked here from the app's own kinematics and A's figures (package B pins them through its own
# -- workbook/strength.py; these hold that A's maths and checks.check's torques give them, row by row, by §5.2's rules)

def _printed_assessment(spec, diagnostics=()):
    from gear_generator.workbook import assess
    spec = replace(spec, box=replace(spec.box, process="printed"), source_path="C:\\B\\W.xlsx")
    return assess.assess(spec, list(diagnostics), "C:\\Out\\")


def idler_train(torque="1"):
    """§5.3's Idler_Train: In (input, 1000 rpm) at the origin, Idl at X 33.75, Out (output) at X 82.5, all Z+; spur
    gears of module 1.5 and face 10, G1 (z 20) on In, GI (z 25) on Idl, G3 (z 40) on Out; G1–GI and GI–G3."""
    from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Shaft
    return GearboxSpec(
        box=Box(name="Idler_Train", pressure_angle="20", efficiency="98", process="printed"),
        shafts=(Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1000", torque, row=2),
                Shaft("Idl", "frame", "33.75", "0", "0", "Z+", "", row=3),
                Shaft("Out", "frame", "82.5", "0", "0", "Z+", "output", row=4)),
        gears=(Gear("G1", "In", "0", "spur", "external", "20", "1.5", "", "10", "", row=2),
               Gear("GI", "Idl", "0", "spur", "external", "25", "1.5", "", "10", "", row=3),
               Gear("G3", "Out", "0", "spur", "external", "40", "1.5", "", "10", "", row=4)),
        meshes=(Mesh("G1", "GI", row=2), Mesh("GI", "G3", row=3)))


def _placed(a, gear):
    placed = a.report.layout.placed[gear]
    row = next(g for g in a.spec.gears if g.id == (placed.row or gear))
    spec = row.gear_spec(a.spec.box)
    return placed, strength.rate(placed.derived, kind_for(spec).recipe_for(spec))


def test_the_planetary_rows_b1_b2_and_b6_b7():
    """A planetary mesh: the member's torque over d N, × K_γ 1.25; the planet two-way (0.7)."""
    from test_workbook_planetary import planetary_4to1
    from workbook_fixtures import range_box
    a = _printed_assessment(planetary_4to1())
    m = a.report.motion
    (sun_p, sun), (_, planet), (ring_p, ring) = (_placed(a, g) for g in ("Sun", "Planet copy 1", "Ring"))
    assert (m.torques["S"], m.torques["P"], m.held["R"]) == (2.0, 0.0, pytest.approx(5.7624))
    sun_planet = 2000 * m.torques["S"] / (sun_p.derived.d * 3) * strength.PLANET_SHARE
    planet_ring = 2000 * m.held["R"] / (ring_p.derived.d * 3) * strength.PLANET_SHARE
    held = (strength.holds(sun, width=10), strength.holds(planet, width=10, two_way=True), strength.holds(ring, width=10))
    assert (round(sun_planet, 3), round(planet_ring, 3)) == (92.593, 88.926)
    assert tuple(round(h, 3) for h in held) == (20.620, 14.434, 29.492)
    assert round(100 * sun_planet / held[1], 1) == 641.5 and round(100 * planet_ring / held[1], 1) == 616.1

    a = _printed_assessment(range_box())
    low = next(mode for mode in a.report.modes if mode.name == "L").motion
    assert all("Planet" not in mode.motion.torques for mode in a.report.modes if mode.name in ("H", "N"))
    (sun_p, sun), (_, planet), (ring_p, ring) = (_placed(a, g) for g in ("Sun", "Planet copy 1", "Ring"))
    sun_planet = 2000 * low.torques["Input"] / (sun_p.derived.d * 3) * strength.PLANET_SHARE
    planet_ring = 2000 * low.held["Ring"] / (ring_p.derived.d * 3) * strength.PLANET_SHARE
    held = (strength.holds(sun, width=10), strength.holds(planet, width=10, two_way=True), strength.holds(ring, width=10))
    assert (round(sun_planet, 3), round(planet_ring, 3)) == (229.885, 220.782)
    assert tuple(round(h, 3) for h in held) == (32.982, 16.851, 37.989)
    assert round(strength.holds(planet, width=10), 3) == 24.072
    assert round(100 * sun_planet / held[1], 1) == 1364.3 and round(100 * planet_ring / held[1], 1) == 1310.2


@pytest.mark.parametrize("torque, force, share", [("1", 66.667, 230.0), ("0.25", 16.667, 57.5)])
def test_the_idler_rows_b3_to_b5(torque, force, share):
    """The idler (shaft torque exactly 0) passes on G1's force, the larger, and is two-way."""
    a = _printed_assessment(idler_train(torque))
    m = a.report.motion
    assert m.torques["Idl"] == 0.0 and m.torques["Out"] == pytest.approx(1.9208 * float(torque))
    (g1_p, g1), (_, gi), (g3_p, g3) = (_placed(a, g) for g in ("G1", "GI", "G3"))
    from_g1, from_g3 = 2000 * m.torques["In"] / g1_p.derived.d, 2000 * m.torques["Out"] / g3_p.derived.d
    assert round(from_g1, 3) == force and from_g3 < from_g1
    if torque == "1":
        assert round(from_g3, 3) == 64.027
    held = (strength.holds(g1, width=10), strength.holds(gi, width=10, two_way=True), strength.holds(g3, width=10))
    assert tuple(round(h, 3) for h in held) == (38.614, 28.984, 44.485) and round(strength.holds(gi, width=10), 3) == 41.406
    assert round(100 * from_g1 / min(held[:2]), 1) == share == round(100 * from_g1 / min(held[1:]), 1)
    if torque == "1":                                         # §5.3: a typed 34 MPa halves every share, B3 115.0 %
        assert round(100 * from_g1 / strength.holds(gi, allowable=34.0, width=10, two_way=True), 1) == 115.0


def test_risky_placements_rows_b8_at_the_helical_rings_transverse_diameter():
    """M2: G6, a helical ring, gives its force at d 76.6208, never z mn = 72; the herringbone at the faces' overlap."""
    from pathlib import Path
    from gear_generator.workbook import geometry, model, xlsx
    book = Path(__file__).resolve().parent / "fixtures" / "excel-windows" / "Risky_Placements.xlsx"
    spec, diagnostics = model.from_book(xlsx.read(str(book)))
    a = _printed_assessment(spec, diagnostics)
    m = a.report.motion
    want = {("G1", "G2"): (335.605, None, 10.0, 50.670, 56.971, 662.3),
            ("G3", "G4"): (453.154, None, 12.0, 62.836, 71.137, 721.2),
            ("G5", "G6"): (723.563, 709.092, 10.0, 50.670, 61.823, 1428.0)}
    for (ga, gb), (force, other, width, held_a, held_b, share) in want.items():
        (pa, ra), (pb, rb) = _placed(a, ga), _placed(a, gb)
        sides = (2000 * m.torques[pa.shaft] / pa.derived.d, 2000 * m.torques[pb.shaft] / pb.derived.d)
        b = min(geometry.faces_overlap(pa, pb), ra.width, rb.width)
        held = (strength.holds(ra, width=b), strength.holds(rb, width=b))
        assert round(max(sides), 3) == force and b == width
        assert (round(held[0], 3), round(held[1], 3)) == (held_a, held_b)
        assert round(100 * max(sides) / min(held), 1) == share
        if other is not None:
            assert round(min(sides), 3) == other and round(rb.d, 4) == 76.6208
            assert round(100 * 2000 * m.torques[pb.shaft] / 72.0 / held[0], 1) != share     # the slip M2 names



# -- rings drawn by recipe B (F4-0-REVIEW S1 and S2, the coordinator's rulings of 2026-11-18) -------------------------

@pytest.mark.parametrize("spec, y_f, y_s", [
    (dict(module="1", teeth="54", face_width="10", teeth_side="internal", bore="", recipe="B", **PRINTED), 2.01028,
     2.67363),
    (dict(module="2", teeth="80", face_width="10", teeth_side="internal", bore="", recipe="B"), 2.26901, 2.55098),
])
def test_a_ring_drawn_by_recipe_b_is_the_reviews_figure_by_the_module_and_by_beam_statics(spec, y_f, y_s):
    """F4-0-REVIEW S2's reference figures (z 54 m 1 printed, z 80 m 2 machined, both recipe B: the load along the flank
    arc's radius at the tip), held by the module and by the independent beam working on the drawn tooth."""
    g, recipe = derived_of(GearSpec(**spec))
    assert recipe == "B"
    r = strength.rate(g, recipe)
    here = beam(g, recipe, g.face_width)
    assert r.rated and r.ring and r.past_range is (r.q_s >= 8.0)
    assert r.y_f == pytest.approx(y_f, abs=1e-5) and r.y_s == pytest.approx(y_s, abs=1e-5)
    assert here["y_f"] == pytest.approx(y_f, abs=1e-5) and here["y_s"] == pytest.approx(y_s, abs=1e-5)
    assert r.s_fn == pytest.approx(here["s"], abs=1e-9) and r.h_f == pytest.approx(here["h"], abs=1e-9)


def test_a_recipe_b_ring_with_its_tips_inside_its_base_circle_is_not_rated_by_a_reason_true_of_both_recipes():
    """S1: on recipe B the ring's flank is an arc right up to its tip (internal.arc_flank draws it), so the reason
    names no radial line: no involute exists inside the base circle on either recipe. The ruling, not rated, stands."""
    spec = GearSpec(**{**GEARS["A10"], "teeth": "30", "recipe": "B"})
    g, recipe = derived_of(spec)
    internal.arc_flank(g)                                     # the arc is drawn: the tooth has a defined normal there
    for drawn in ("A", "B"):
        r = strength.rate(g, drawn)
        assert (r.rated, r.short) == (False, "tips inside the base circle")
        assert r.why == (f"its tips lie inside its base circle ({g.da:.3f} mm against {g.db:.3f}), where its teeth "
                         "cannot be involute, and the rating needs an involute tip to load")
        assert "radial line" not in r.why
