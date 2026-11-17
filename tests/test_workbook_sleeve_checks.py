"""W9b package A (ISSUE-1-PLAN §2.2, §2.3, §3; K7, K8, K9; W9B-INTERFACES.md §6): the sleeve checks — whether a sleeve's
shaft can reach it, whether anything keys it to its shaft, and its running clearance — as §3 works them by hand on
RangeBox, RangeBox_Fixed and W8's two fixtures (whose three each are pinned in ``test_workbook_modes``)."""

from dataclasses import replace

import pytest

from gear_generator.workbook import assess, checks, modes
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Shaft
from workbook_fixtures import range_box, range_box_fixed

BOOK = "C:\\B\\RangeBox.xlsx"
MINUS = "\u2212"


def assessed(spec):
    return assess.assess(replace(spec, source_path=BOOK), [], "C:\\Out\\")


def with_gear(spec, gid, **changes):
    return replace(spec, gears=tuple(replace(g, **changes) if g.id == gid else g for g in spec.gears))


def without(spec, gid):
    return replace(spec, gears=tuple(g for g in spec.gears if g.id != gid))


def warnings(spec):
    return [d.message for d in assessed(spec).diagnostics if d.level == "warning"]


def w9b(messages):
    return [m for m in messages if "cannot reach" in m or "nothing keys" in m or "which it does not engage there" in m
            or "on another shaft: leave at least" in m]


# -- §3's answers -----------------------------------------------------------------------------------------------------

RANGE_BOX = [
    f"Gears row 7: Output cannot reach RangeSlv: Input runs through RangeSlv's travel (from Sun at 10.5 to HighDog at "
    f"{MINUS}32), so Output would have to pass HighDog toward Z{MINUS} or Sun toward Z+, each on Input.",
    "Gears row 7: nothing keys RangeSlv to Output: its whole bore is teeth and no hub row is under it; add a hub on "
    f"Output that a band of RangeSlv covers in every mode; as laid out none can, since its 10 mm face slides 10 mm (H "
    f"{MINUS}5 to L +5) and its places share no length.",
    "Modes row 3: in N RangeSlv stands 0 mm from HighDog and 0 mm from LowDog, which it does not engage there: leave "
    "at least 0.625 mm (0.5 × module) each side.",
]


def test_range_box_gains_section_3s_three_warnings_word_for_word_and_nothing_else_changes():
    a = assessed(range_box())
    assert w9b([d.message for d in a.diagnostics]) == RANGE_BOX
    assert all(d.level == "warning" for d in a.diagnostics if d.message in RANGE_BOX)
    assert [d.message for d in a.diagnostics if d.is_error] == []
    assert {m.name: m.engaged for m in a.report.modes} == {"H": (("RangeSlv", "HighDog"),), "N": (),
                                                           "L": (("RangeSlv", "LowDog"),)}


def test_range_box_fixed_has_no_warning_from_w9bs_checks_and_no_stroke_warning():
    messages = warnings(range_box_fixed())
    assert w9b(messages) == [] and not any("would hold both at once" in m for m in messages)
    assert len(messages) == 4                        # the four RangeBox had before W9, none about the clutch
    assert not any("RangeSlv" in m and "Gears row 7: RangeSlv: The teeth's tips" not in m for m in messages)


def _least_gaps(spec):
    """Per mode, the least running gap §3's table gives: ``(what, mm)`` from a toothed band to a dog it neither
    engages nor overlaps there."""
    a = assessed(spec)
    sleeve = a.spec.gear("RangeSlv")
    dogs = {g: a.report.layout.placed[g] for g in ("HighDog", "LowDog")}
    out = {}
    for m in a.report.modes:
        gaps = []
        for word, lo, hi in modes.band_spans(sleeve, m.placed["RangeSlv"]):
            for name, p in dogs.items():
                if ("RangeSlv", name) in m.engaged:
                    continue
                gaps.append((round(max(p.z_range[0] - hi, lo - p.z_range[1]), 9), f"{word} band to {name}"))
        out[m.name] = sorted(gaps)[0]
    return out


def test_range_box_fixeds_least_running_gaps_are_section_3s():
    gaps = _least_gaps(range_box_fixed())
    assert gaps["H"] == (10.0, "end band to LowDog")
    assert gaps["N"][0] == 2.5                       # each side: test_range_box_fixed_n_stands_2_5_mm_from_each_dog
    assert gaps["L"] == (1.0, "start band to HighDog")
    a = assessed(range_box_fixed())
    hub, high = a.report.layout.placed["Hub"].z_range, a.report.layout.placed["HighDog"].z_range
    assert high[0] - hub[1] == 1.0 >= modes.running_clearance(1.25) == 0.625          # Hub to HighDog


def test_range_box_fixed_n_stands_2_5_mm_from_each_dog():
    a = assessed(range_box_fixed())
    n = next(m for m in a.report.modes if m.name == "N")
    (_, s0, s1), (_, e0, e1) = modes.band_spans(a.spec.gear("RangeSlv"), n.placed["RangeSlv"])
    high, low = a.report.layout.placed["HighDog"].z_range, a.report.layout.placed["LowDog"].z_range
    assert (e0 - high[1], low[0] - e1) == (2.5, 2.5) and (s0, s1, e0, e1) == (-48.0, -43.0, -27.0, -22.0)


# -- reach (K7) -------------------------------------------------------------------------------------------------------

def test_reach_with_a_hub_runs_to_the_hubs_start_and_nothing_is_present_there():
    a = assessed(range_box_fixed())
    assert a.report.layout.placed["Hub"].z_range[0] == -55.5
    assert modes.reach_warnings(a.spec, a.report.layout.placed) == []


@pytest.mark.parametrize("spec", [
    without(range_box_fixed(), "Hub"),                       # bands, no hub: the start band reaches from Z−
    with_gear(range_box(), "RangeSlv", at="-35", face_width="26", slides="H=-7.5, N=0, L=+7.5"),  # the issue's long one
])
def test_a_nested_input_through_a_hollow_carrier_is_not_warned(spec):
    """Input runs through the hollow Carrier (its HighDog beyond Carrier's LowDog, both inside the sleeve's reach):
    the sleeve's places reach past both toward Z−, so Output reaches it from there."""
    assert not any("cannot reach" in m for m in warnings(spec))


def test_with_bands_and_no_hub_the_warning_stands_only_when_every_band_is_blocked_both_ways():
    open_box = without(range_box_fixed(), "Hub")
    extra = Gear("Extra", "Input", "-60", "spur", "", "17", "1.25", "", "5", "", row=8)
    blocked = replace(open_box, gears=open_box.gears + (extra,))         # Input now reaches −62.5: past the start band
    said = [m for m in warnings(blocked) if "cannot reach" in m]
    assert said == [f"Gears row 7: Output cannot reach RangeSlv: Input runs through RangeSlv's travel (from HighDog at "
                    f"{MINUS}32 to Extra at {MINUS}60), so Output would have to pass Extra toward Z{MINUS} or HighDog "
                    "toward Z+, each on Input."]                  # the two in Gears-sheet order, as §2.2's sentence
    assert not any("cannot reach" in m for m in warnings(open_box))


def _two_shafts(lo_of_p1):
    """A sleeve S on Out over 15…25 (p− 15, p+ 25), and In along the same line with P1 from ``lo_of_p1`` to 25 and P2
    over 35…45: In is present across p− only when P1 starts more than COVER_TOLERANCE below it."""
    face = 25.0 - lo_of_p1
    shafts = (Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1500", "", row=2),
              Shaft("Out", "frame", "0", "0", "0", "Z+", "output", row=3))
    gears = (Gear("P1", "In", repr(lo_of_p1 + face / 2.0), "dog", "", "17", "1.25", "", repr(face), "", row=2),
             Gear("P2", "In", "40", "dog", "", "17", "1.25", "", "10", "", row=3),
             Gear("S", "Out", "20", "sleeve", "", "17", "1.25", "", "10", "", row=4))
    spec = GearboxSpec(box=Box(name="Reach", pressure_angle="20", efficiency="98"), shafts=shafts, gears=gears)
    report = checks.check(spec)
    return modes.reach_warnings(spec, report.layout.placed)


@pytest.mark.parametrize("lo, warned", [(15.0, False), (15.0 - 0.5e-6, False), (15.0 - 2e-6, True), (5.0, True)])
def test_presence_is_an_open_interval_held_to_cover_tolerance(lo, warned):
    assert modes.COVER_TOLERANCE == 1e-6
    said = _two_shafts(lo)
    assert bool(said) is warned
    if warned:
        assert [d.message for d in said] == [f"Gears row 4: Out cannot reach S: In runs through S's travel (from P1 at "
                                             f"{modes._n(lo + (25.0 - lo) / 2.0)} to P2 at 40), so Out would have to "
                                             f"pass P1 toward Z{MINUS} or P2 toward Z+, each on In."]


def test_a_sleeve_with_no_slides_whose_place_is_taken_says_so():
    shafts = (Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1500", "", row=2),
              Shaft("Out", "frame", "0", "0", "0", "Z+", "output", row=3))
    gears = (Gear("P1", "In", "20", "dog", "", "17", "1.25", "", "10", "", row=2),
             Gear("S", "Out", "20", "sleeve", "", "17", "1.25", "", "10", "", row=3))
    spec = GearboxSpec(box=Box(name="Taken", pressure_angle="20", efficiency="98"), shafts=shafts, gears=gears)
    said = modes.hub_warnings(spec, checks.check(spec).layout.placed)
    assert [d.message for d in said] == [
        "Gears row 3: nothing keys S to Out: its whole bore is teeth and no hub row is under it; add a hub on Out that a "
        "band of S covers in every mode; as laid out none can, since what it stands over is taken by another shaft's "
        "gear."]


# -- the hub warning (K8) ---------------------------------------------------------------------------------------------

def test_a_banded_sleeve_with_no_hub_is_warned_and_one_could_fit():
    said = [m for m in warnings(without(range_box_fixed(), "Hub")) if "nothing keys" in m]
    assert said == ["Gears row 7: nothing keys RangeSlv to Output: no hub row is under it; add a hub on Output that a "
                    "band of RangeSlv covers in every mode."]


def test_a_sleeve_with_its_hub_is_not_warned():
    assert not any("nothing keys" in m for m in warnings(range_box_fixed()))


def test_an_unbanded_sleeve_whose_places_share_length_could_have_a_hub():
    """RangeBox's sleeve moved to slide ±1 off the dogs (−34.5…−22.5 at 12 mm): its places share 10 mm with no dog."""
    spec = with_gear(range_box(), "RangeSlv", at="-50", face_width="12", slides="H=-1, N=0, L=+1")
    said = [m for m in warnings(spec) if "nothing keys" in m]
    assert said == ["Gears row 7: nothing keys RangeSlv to Output: its whole bore is teeth and no hub row is under it; "
                    "add a hub on Output that a band of RangeSlv covers in every mode."]


# -- running clearance (K9) -------------------------------------------------------------------------------------------

def test_running_clearance_is_half_a_module_at_least_half_a_millimetre():
    assert modes.running_clearance(1.25) == 0.625 and modes.running_clearance(1.5) == 0.75
    assert modes.running_clearance(0.8) == 0.5 and modes.running_clearance(1.0) == 0.5


@pytest.mark.parametrize("n, said", [
    ("-1.875", None),                                         # the end band 0.625 mm from HighDog: exactly c, clean
    ("-1.885", "Modes row 3: in N RangeSlv's end band stands 0.615 mm from HighDog, which it does not engage there: "
               "leave at least 0.625 mm (0.5 × module) each side."),
])
def test_clearance_at_exactly_c_is_clean_and_just_below_it_is_warned(n, said):
    spec = with_gear(range_box_fixed(), "RangeSlv", slides=f"H=-7.5, N={n}, L=+7.5")
    found = [m for m in warnings(spec) if "which it does not engage there" in m]
    assert found == ([] if said is None else [said])


def test_the_floor_is_said_as_the_least_at_any_module():
    spec = range_box()
    small = replace(spec, gears=tuple(replace(g, module="0.8") if g.id in ("HighDog", "LowDog", "RangeSlv") else g
                                      for g in spec.gears))
    found = [m for m in warnings(small) if "which it does not engage there" in m]
    assert found == ["Modes row 3: in N RangeSlv stands 0 mm from HighDog and 0 mm from LowDog, which it does not "
                     "engage there: leave at least 0.5 mm (the least at any module) each side."]


def test_a_hub_and_a_dog_on_different_shafts_are_held_to_the_same_gap():
    near = with_gear(range_box_fixed(), "Hub", at="-45.25", face_width="20.5")         # −55.5…−35: 0.5 mm to HighDog
    found = [m for m in warnings(near) if "on another shaft" in m]
    assert found == ["Gears row 8: Hub stands 0.5 mm from HighDog, on another shaft: leave at least 0.625 mm (0.5 × "
                     "module) between them."]


def test_with_no_modes_rows_the_clearance_warning_is_at_the_sleeves_cell():
    one = replace(range_box(), modes=(), sliders=())
    one = with_gear(one, "RangeSlv", slides="N=0")
    found = [m for m in warnings(one) if "which it does not engage there" in m]
    assert found == ["Gears row 7: RangeSlv stands 0 mm from HighDog and 0 mm from LowDog, which it does not engage "
                     "there: leave at least 0.625 mm (0.5 × module) each side."]


def test_one_gear_that_spans_both_points_is_named_once():
    """The review's should-fix 2: P, one 40 mm dog on In over 0…40, is present across both of S's points (15 and 25)
    and reaches past each: one gear, said once with its span."""
    shafts = (Shaft("In", "frame", "0", "0", "0", "Z+", "input", "", "1500", "", row=2),
              Shaft("Out", "frame", "0", "0", "0", "Z+", "output", row=3))
    gears = (Gear("P", "In", "20", "dog", "", "17", "1.25", "", "40", "", row=2),
             Gear("S", "Out", "20", "sleeve", "", "17", "1.25", "", "10", "", row=3))
    spec = GearboxSpec(box=Box(name="Long", pressure_angle="20", efficiency="98"), shafts=shafts, gears=gears)
    said = modes.reach_warnings(spec, checks.check(spec).layout.placed)
    assert [d.message for d in said] == ["Gears row 3: Out cannot reach S: In runs through S's travel at P (0 to 40), "
                                         "so Out would have to pass P, on In."]


def test_reach_with_a_hub_is_judged_at_the_hubs_points_not_the_bands():
    """The review's N1. Extra, a gear on Input over −55…−51, holds both of the start band's points (−40.5 and
    −50.5) but not the hub's start (−55.5): with Hub the sleeve is reached from Z−; without it every band is blocked."""
    extra = Gear("Extra", "Input", "-53", "dog", "", "17", "1.25", "", "4", "", row=9)
    with_hub = replace(range_box_fixed(), gears=range_box_fixed().gears + (extra,))
    no_hub = without(with_hub, "Hub")
    for spec, warned in ((with_hub, False), (no_hub, True)):
        report = checks.check(spec)
        said = [d.message for d in modes.reach_warnings(spec, report.layout.placed)]
        assert bool(said) is warned, said
