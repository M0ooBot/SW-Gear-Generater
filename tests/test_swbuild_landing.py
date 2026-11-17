"""A ring's tooth change that lands a solved line on itself (W9c's demonstration, run 6 on SolidWorks 2026): the
foresight in ``gears.landing``, the route through a safe intermediate in ``swbuild.update_variables``, and the fake
taught the hazard (``FakeSolidWorks._ring_landing``, from the ring's own maths) so the suite would have caught it."""

import math

import pytest

from gear_generator import swbuild
from gear_generator.gears import internal, landing, spur
from gear_generator.gears.equations import DEGREES, evaluate_all
from gear_generator.spec import GearSpec

from test_swbuild import FakeSolidWorks, _key, never_exists

RING = internal.InternalSpurGear()
SPUR = spur.SpurGear()
RING_PATH = "C:\\W\\Ring_m1.25_N55.SLDPRT"
SUN_PATH = "C:\\W\\Gear_m1.25_N29.SLDPRT"


def _spec(kind, n, module="1.25"):
    return GearSpec().with_values(teeth=str(n), module=module,
                                  teeth_side="internal" if kind is RING else "external")


def _variables(kind, n, module="1.25"):
    spec = _spec(kind, n, module)
    return kind.variables(spec, kind.derive(spec))


def _values(kind, n, module="1.25"):
    return evaluate_all([(v.name, v.expression_for(DEGREES)) for v in _variables(kind, n, module)], DEGREES)


def _built(kind, n, path, module="1.25"):
    fake = FakeSolidWorks()
    spec = _spec(kind, n, module)
    result = swbuild.build(fake, kind.plan(spec, kind.derive(spec), "", "", path), never_exists)
    assert result.ok, result.log_lines()
    fake.open_document(path)
    fake.calls.clear()
    return fake


def _sets(fake):
    return [(a[0], a[1]) for n, a in fake.calls if n == "set_global_variable" and a[0] == spur.TEETH]


# -- the foresight, from the part's own globals ------------------------------------------------------------------------

@pytest.mark.parametrize("before, after, lands", [(55, 54, True), (56, 55, True), (55, 53, False), (55, 56, False),
                                                  (53, 54, False), (55, 50, False), (55, 60, False)])
def test_the_ring_landing_is_foreseen_as_run_6_measured_it(before, after, lands):
    found = landing.line_landings(_values(RING, before), _values(RING, after))
    assert bool(found) is lands
    every = landing.line_landings(_values(RING, before), _values(RING, after), fraction=float("inf"))
    old, new = (internal.involute_flank(RING.derive(_spec(RING, n))) for n in (before, after))
    assert every[0][0] == "Li+" and math.isclose(every[0][1], math.dist(old.cap, new.start), abs_tol=1e-9)
    assert math.isclose(every[0][2], math.dist(new.start, new.cap), abs_tol=1e-9)    # the sketch's own maths


def test_run_6s_numbers_one_tooth_down_land_0_024_mm_from_the_old_end_of_a_0_625_mm_line():
    (name, landed, length), = landing.line_landings(_values(RING, 55), _values(RING, 54))
    assert name == "Li+" and round(landed, 4) == 0.0237 and round(length, 4) == 0.625


def test_the_external_gears_line_is_read_from_its_own_sketch_maths():
    every = landing.line_landings(_values(SPUR, 29), _values(SPUR, 28), fraction=float("inf"))
    old, new = (spur.involute_flank(SPUR.derive(_spec(SPUR, n))) for n in (29, 28))
    assert every[0][0] == "L+" and math.isclose(every[0][1], math.dist(old.line_inner, new.start), abs_tol=1e-9)
    assert math.isclose(every[0][2], math.dist(new.start, new.line_inner), abs_tol=1e-9)
    assert not landing.line_landings(_values(SPUR, 29), _values(SPUR, 28))     # measured clean (run 5's remake)
    assert not landing.line_landings(_values(SPUR, 29), _values(SPUR, 30))


def test_globals_that_are_no_involute_tooth_space_foresee_nothing():
    assert landing.line_landings({"Module": 1.0}, {"Module": 2.0}) == []


# -- the fake, taught the hazard ---------------------------------------------------------------------------------------

def test_the_fake_leaves_a_ring_set_straight_across_the_landing_on_the_far_branch_for_good(monkeypatch):
    monkeypatch.setattr(swbuild, "LANDING_STEPS", ())          # no intermediate: the change as before this fix
    fake = _built(RING, 55, RING_PATH)
    result = swbuild.update_variables(fake, _variables(RING, 54), RING_PATH)
    assert not result.rebuilt and result.by_way_of == () and result.landing[0][0] == "Li+"
    assert fake.feature_codes[(_key(RING_PATH), "Tooth Space")] == 72
    again = swbuild.update_variables(fake, _variables(RING, 55), RING_PATH)          # run 6: 54 -> 55 does not mend
    assert not again.rebuilt and fake.feature_codes[(_key(RING_PATH), "Tooth Space")] == 72


# -- the route --------------------------------------------------------------------------------------------------------

def test_a_ring_set_one_tooth_down_goes_by_way_of_a_safe_count_and_rebuilds_clean():
    fake = _built(RING, 55, RING_PATH)
    result = swbuild.update_variables(fake, _variables(RING, 54), RING_PATH)
    assert result.ok and result.rebuilt, result
    assert result.by_way_of == (spur.TEETH, "53") and result.landing[0][0] == "Li+"
    assert _sets(fake) == [(spur.TEETH, "53"), (spur.TEETH, "54")]          # 55 -> 53 -> 54, measured clean
    assert [n for n, _ in fake.calls].count("rebuild") == 2
    assert not any(k == _key(RING_PATH) for k, _ in fake.feature_codes) and _key(RING_PATH) not in fake.wrong_branch
    assert result.changed == [spur.TEETH]


@pytest.mark.parametrize("after", [53, 56, 50, 60])
def test_a_change_that_lands_nothing_rebuilds_once_as_before(after):
    fake = _built(RING, 55, RING_PATH)
    result = swbuild.update_variables(fake, _variables(RING, after), RING_PATH)
    assert result.rebuilt and result.by_way_of == () and result.landing == ()
    assert _sets(fake) == [(spur.TEETH, str(after))] and [n for n, _ in fake.calls].count("rebuild") == 1


def test_an_external_gear_set_one_tooth_down_rebuilds_once():
    fake = _built(SPUR, 29, SUN_PATH)
    result = swbuild.update_variables(fake, _variables(SPUR, 28), SUN_PATH)
    assert result.rebuilt and result.by_way_of == () and [n for n, _ in fake.calls].count("rebuild") == 1


def test_with_no_safe_intermediate_the_change_goes_as_before_and_the_stop_names_the_part(monkeypatch):
    monkeypatch.setattr(swbuild, "LANDING_STEPS", (1,))        # 55 itself: the count held, so no intermediate
    fake = _built(RING, 55, RING_PATH)
    result = swbuild.update_variables(fake, _variables(RING, 54), RING_PATH)
    assert not result.rebuilt and result.by_way_of == () and result.landing
    assert _sets(fake) == [(spur.TEETH, "54")]


def test_a_route_whose_first_leg_fails_stops_there():
    fake = _built(RING, 55, RING_PATH)
    fake.breaks_on_set[_key(RING_PATH)] = [("Tooth Space", 72)]
    result = swbuild.update_variables(fake, _variables(RING, 54), RING_PATH)
    assert not result.rebuilt and result.by_way_of == (spur.TEETH, "53") and _sets(fake) == [(spur.TEETH, "53")]


def test_an_update_gives_the_route_through_its_part_step_and_says_it(monkeypatch):
    """The value step of an Update (``_update_document``) goes through update_variables: the route is taken there,
    the part reads rebuilt, and the log says the intermediate; nothing else in the step changes."""
    fake = _built(RING, 55, RING_PATH)
    doc = swbuild.DocumentValues(RING_PATH, tuple(_variables(RING, 54)))
    done, failures = swbuild._update_document(fake, doc)                    # noqa: SLF001
    assert failures == [] and done.rebuilt and done.by_way_of == (spur.TEETH, "53")
    lines = swbuild.GearboxUpdate(parts=[done]).log_lines()
    assert (f'ok      set "{spur.TEETH}" by way of 53 first, rebuilt there, then the workbook\'s value (a sketch line '
            "would have landed on itself)") in lines and "ok      rebuilt twice" in lines
