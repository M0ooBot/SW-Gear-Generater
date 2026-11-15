"""``swbuild.train_check`` with carriers and held gears (W7-PLAN §2.9, §5.3; review M1), written at W7's interface
commit because the worker (A) and Update's planning (B) both rest on it.

The 4 : 1 fixture of W7-PLAN §4.1: Sun 18 on S, three copies of Planet 18 on P (mounted on C, 18 mm out), Ring 54 on
R held, every axis Z+, every front face at z 5; the carrier part's origin at (0, 0, 0); CarrierGear 20 on C at z 27,
locked to the carrier. Driven +30° on the sun: carrier +7.5°, each copy −15° about its own axis (−22.5° relative to
the carrier), Ring 0. Frames are ``F_σ · rot_z(θ)`` by rows, as ``layout.frame`` gives them.
"""

import math

import pytest

from gear_generator.swbuild import CarrierLink, LockLink, MeshLink, TrainCheck, train_check, turn_between

COPIES = ("Planet copy 1", "Planet copy 2", "Planet copy 3")
PSI = (0.0, 120.0, 240.0)
PITCH = {"Sun": 20.0, "Ring": 360 / 54, "CarrierGear": 18.0, **{c: 20.0 for c in COPIES}}
CARRIER = "C carrier"


def rot(sigma, degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    if sigma > 0:
        return (c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0)
    return (c, -s, 0.0, -s, -c, 0.0, 0.0, 0.0, -1.0)


def about_z(point, degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return (c * point[0] - s * point[1], s * point[0] + c * point[1], point[2])


class Stage:
    """The fixture on Z+ (sigma +1) or on Z- (sigma -1, W7-PLAN §4.3): every shaft faces the carrier's way."""

    def __init__(self, sigma=1):
        self.sigma = sigma
        front = 5.0 * sigma
        # Copy k on the carrier at F_σ·rot_z(ψ_k)·(18, 0, 0): on Z- the y is negated.
        self.copy_at = {c: (18 * math.cos(math.radians(p)), sigma * 18 * math.sin(math.radians(p)), front)
                        for c, p in zip(COPIES, PSI)}
        self.at = {"Sun": (0.0, 0.0, front), "Ring": (0.0, 0.0, front), "CarrierGear": (0.0, 0.0, 27.0 * sigma),
                   CARRIER: (0.0, 0.0, 0.0), **self.copy_at}
        self.theta = {"Sun": 0.0, "Ring": 0.0, "CarrierGear": 0.0, CARRIER: 0.0, **{c: 10.0 for c in COPIES}}
        self.link = CarrierLink(CARRIER, COPIES, (0.0, 0.0, 0.0), (0.0, 0.0, float(sigma)))

    def wanted(self):
        return {g: (rot(self.sigma, self.theta[g]), self.at[g]) for g in self.at}

    def turned(self, own=None, carrier=0.0, moved=None):
        """Every gear turned ``own[g]`` degrees about its own +Z; the copies carried round the carrier's axis by
        ``carrier`` degrees about its own +Z (about world +Z by σ·carrier); ``moved`` overrides an origin."""
        own = dict(own or {})
        out = {}
        for g, at in self.at.items():
            if g in COPIES:
                at = about_z(at, self.sigma * carrier)
            turn = carrier if g == CARRIER else own.get(g, 0.0)
            out[g] = (rot(self.sigma, self.theta[g] + turn), (moved or {}).get(g, at))
        return out


def driven(sun):
    """The consistent turn of the ring-held stage for ``sun`` degrees on the sun, each about its own axis."""
    return {"Sun": sun, "CarrierGear": sun / 4, **{c: -sun / 2 for c in COPIES}}, sun / 4


MESHES = tuple(MeshLink("Sun", c, -1.0, 20.0, carrier=CARRIER) for c in COPIES) + (
    MeshLink("Planet copy 1", "Ring", 18 / 54, 360 / 54, carrier=CARRIER),)
UNMATED = tuple(MeshLink(c, "Ring", 18 / 54, 360 / 54, carrier=CARRIER) for c in COPIES[1:])
LOCKS = (LockLink(CARRIER, "CarrierGear", 18.0),)


def check(found, stage, meshes=MESHES, held=("Ring",)):
    return train_check(found, stage.wanted(), meshes, LOCKS, PITCH, carriers=(stage.link,), held=held)


@pytest.mark.parametrize("sigma", [1, -1])
def test_a_planetary_as_built_is_in_step_and_not_turned(sigma):
    stage = Stage(sigma)
    result = check(stage.wanted(), stage)
    assert result.in_step and not result.turned and result.off_axis == ()


@pytest.mark.parametrize("sigma", [1, -1])
@pytest.mark.parametrize("sun", [30.0, 37.0, -200.0])
def test_a_planetary_turned_consistently_is_in_step_and_turned(sigma, sun):
    """Its unmated ring meshes are in step too: (−22.5)·18 = −405 = (0 − 7.5)·54 at 30° (W7-PLAN §4.1)."""
    stage = Stage(sigma)
    own, carrier = driven(sun)
    result = check(stage.turned(own, carrier), stage, MESHES + UNMATED)
    assert result.in_step and result.turned, result
    assert max(r for _, _, r in result.residuals) < 1e-9


def test_the_carried_copy_is_where_the_spike_measured_it():
    """W7-PLAN §4.1: after +30° on the sun, copy origins at (17.846008, 2.349471), (−10.957706, 14.280360),
    (−6.888302, −16.629832); each copy's own turn −15°, −22.5° relative to the carrier."""
    stage = Stage(1)
    own, carrier = driven(30.0)
    found = stage.turned(own, carrier)
    assert [tuple(round(v, 6) for v in found[c][1][:2]) for c in COPIES] == [
        (17.846008, 2.349471), (-10.957706, 14.28036), (-6.888302, -16.629832)]
    assert math.degrees(turn_between(stage.wanted()["Planet copy 1"][0], found["Planet copy 1"][0])) == \
        pytest.approx(-15.0)


def test_one_copy_turned_alone_is_out_of_step_with_the_sun():
    stage = Stage(1)
    own, carrier = driven(30.0)
    own["Planet copy 2"] += 3.0
    result = check(stage.turned(own, carrier), stage)
    assert result.out_of_step == (("Sun", "Planet copy 2"),) and not result.turned


def test_a_copy_carried_round_but_not_turned_relative_to_the_carrier_is_out_of_step():
    """Copy 2 at its carried place, turned exactly as far as the carrier (0 relative to it): out of step."""
    stage = Stage(1)
    own, carrier = driven(30.0)
    own["Planet copy 2"] = carrier
    result = check(stage.turned(own, carrier), stage)
    assert result.out_of_step == (("Sun", "Planet copy 2"),)


def test_a_copy_off_its_carried_place_is_off_its_axis():
    """Copy 2 left where it was built while the carrier turned: not at its carried place."""
    stage = Stage(1)
    own, carrier = driven(30.0)
    result = check(stage.turned(own, carrier, moved={"Planet copy 2": stage.copy_at["Planet copy 2"]}), stage)
    assert result.off_axis == ("Planet copy 2",) and not result.in_step
    assert ("Sun", "Planet copy 2") not in [(a, b) for a, b, _ in result.residuals]


def test_a_carrier_off_its_willis_turn_is_out_of_step_through_the_held_ring():
    """Review M1's scenario 1: the carrier at 10° where the sun's 30° wants 7.5°, the copies turned to suit the sun
    relative to it (the sun mates still hold): only Planet copy 1 meshes Ring says so."""
    stage = Stage(1)
    own = {"Sun": 30.0, "CarrierGear": 10.0, **{c: 10.0 - 20.0 for c in COPIES}}
    result = check(stage.turned(own, 10.0), stage)
    assert result.out_of_step == (("Planet copy 1", "Ring"),)


def test_a_held_ring_is_judged_against_its_wanted_frame_but_for_whole_teeth():
    stage = Stage(1)
    whole = check(stage.turned({"Ring": 2 * PITCH["Ring"]}), stage)
    assert whole.in_step and not whole.turned
    off = check(stage.turned({"Ring": 1.0}), stage)
    assert off.off_axis == ("Ring",)
    moved = check(stage.turned(moved={"Ring": (0.0, 0.0, 6.0)}), stage)
    assert moved.off_axis == ("Ring",)


def test_the_carrier_gear_turns_with_the_carrier_or_is_out_of_step():
    stage = Stage(1)
    own, carrier = driven(30.0)
    own["CarrierGear"] = 0.0
    assert check(stage.turned(own, carrier), stage).out_of_step == ((CARRIER, "CarrierGear"),)


def test_a_carrier_off_its_axis_takes_its_planets_with_it():
    stage = Stage(1)
    found = stage.turned(moved={CARRIER: (0.5, 0.0, 0.0)})
    assert check(found, stage).off_axis == (CARRIER,) + COPIES


def test_a_held_carrier_must_not_turn():
    """A held carrier is given in both ``carriers`` and ``held`` (W7-INTERFACES.md §3)."""
    stage = Stage(1)
    still = {"Sun": 30.0, "Ring": -10.0, **{c: -30.0 for c in COPIES}}
    meshes = MESHES[:3] + (MeshLink("Planet copy 1", "Ring", 18 / 54, 360 / 54, carrier=CARRIER),)
    held = check(stage.turned(still, 0.0), stage, meshes, held=(CARRIER, "CarrierGear"))
    assert held.in_step and held.turned
    own, carrier = driven(30.0)
    assert check(stage.turned(own, carrier), stage, held=(CARRIER, "Ring")).off_axis == (CARRIER,) + COPIES


def test_with_no_carriers_and_no_held_gears_it_is_w5s_check():
    stage = Stage(1)
    plain = (MeshLink("Sun", "Planet copy 1", -1.0, 20.0),)
    found = stage.turned({"Sun": 30.0, "Planet copy 1": -30.0})
    assert train_check(found, stage.wanted(), plain, (), PITCH) == train_check(found, stage.wanted(), plain, (), PITCH,
                                                                                carriers=(), held=())
    assert train_check(found, stage.wanted(), plain, (), PITCH).in_step


def test_a_mesh_measured_against_a_carrier_not_given_is_refused():
    stage = Stage(1)
    with pytest.raises(ValueError, match="which the check was not given"):
        train_check(stage.wanted(), stage.wanted(), MESHES, (), PITCH)
    other = CarrierLink("D carrier", ("Planet copy 1",), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    with pytest.raises(ValueError, match="among the planets of both"):
        train_check(stage.wanted(), stage.wanted(), (), (), PITCH, carriers=(stage.link, other))


def test_a_check_result_keeps_its_shape():
    assert TrainCheck().in_step


# -- a remake inside a planetary's put that loses its mate (W8-REVIEW-LATE-A point 3) -------------------------------
#
# W7's path only. ``_remake`` deletes the gear mate and makes it again; if the make then stops, the mate is gone, and
# the put's restore must not tell the user it is "left suppressed … press Update SolidWorks again", since pressed
# again Update finds it gone. The fake is taught here, as the review's reproduction did: its second
# ``set_gear_ratio`` deletes the mate and raises, and ``set_mate_suppressed`` raises ``MateGone`` for a mate that is
# not there, as ``swcom.Session`` does (``_kept_mate``).

def test_a_remake_that_loses_its_mate_inside_the_planetary_put_is_said_gone_never_left_suppressed():
    from gear_generator import swbuild, swcom
    from gear_generator.workbook import update
    from test_workbook_planetary import direct, edited, fake_build, planetary_4to1

    sw, _, record = fake_build(planetary_4to1())
    spec = edited(planetary_4to1(), shafts={"P": dict(x="19.5")},
                  gears={"Sun": dict(teeth="21"), "Ring": dict(teeth="57")})
    real_ratio, real_supp, count, lost = sw.set_gear_ratio, sw.set_mate_suppressed, [0], []

    def lossy(handle, a, b, ratio):
        count[0] += 1
        if count[0] == 2:
            old = sw.mate(sw.mate_handles[handle])
            sw.mates.remove(old)
            lost.append(old.name)
            raise swbuild.SolidWorksError(f"The open Planetary_4to1.SLDASM has lost the gear mate {old.name}: close "
                                          "Planetary_4to1.SLDASM in SolidWorks without saving to bring it back.")
        return real_ratio(handle, a, b, ratio)

    def supp(handle, suppressed):
        name = sw.mate_handles[handle]
        if sw.mate(name) is None:
            raise swcom.MateGone(f'The mate "{name}" is not in Planetary_4to1.SLDASM any more: it was renamed or '
                                 "deleted in SolidWorks.")
        return real_supp(handle, suppressed)
    sw.set_gear_ratio, sw.set_mate_suppressed = lossy, supp
    up = update.classify(record, direct(spec), exists=lambda p: True)
    result = swbuild.update_gearbox(sw, **up.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    texts = [text for _, text in result.failures]
    assert lost and not any("left suppressed" in text for text in texts), texts
    assert any(f"has lost the gear mate {lost[0]}" in text for text in texts), texts
    assert not any(text.startswith(f'The mate "{lost[0]}" is not in') for text in texts), texts
    # every other gear mate and lock the put turned off is back on
    assert not [m.name for m in sw.mates if m.suppressed], [m.name for m in sw.mates if m.suppressed]


# The other path (W8-REVIEW-FIX-A point 5): a gear mate gone during the puts with nothing raised, so no error is on its
# way out. The restore's MateGone is then the error: every other lock and gear mate is still turned back on, and
# Update says the mate is gone, never "left suppressed".

def test_a_gear_mate_gone_during_the_puts_with_no_error_pending():
    from gear_generator import swbuild, swcom
    from gear_generator.workbook import update
    from test_workbook_planetary import direct, edited, fake_build, planetary_4to1

    sw, _, record = fake_build(planetary_4to1())
    spec = edited(planetary_4to1(), gears={"Planet": dict(at="12")})
    real_place, real_supp, lost = sw.place_component, sw.set_mate_suppressed, []

    def place(handle, rotation, at, kind=None):
        if not lost:                                   # gone during the puts, with nothing raised
            old = sw.mate("Sun meshes Planet copy 2")
            sw.mates.remove(old)
            lost.append(old.name)
        return real_place(handle, rotation, at, kind=kind)

    def supp(handle, suppressed):
        name = sw.mate_handles[handle]
        if sw.mate(name) is None:
            raise swcom.MateGone(f'The mate "{name}" is not in Planetary_4to1.SLDASM any more: it was renamed or '
                                 "deleted in SolidWorks.")
        return real_supp(handle, suppressed)
    sw.place_component, sw.set_mate_suppressed = place, supp
    up = update.classify(record, direct(spec), exists=lambda p: True)
    result = swbuild.update_gearbox(sw, **up.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    texts = [t for _, t in result.failures]
    assert lost and texts == ['The mate "Sun meshes Planet copy 2" is not in Planetary_4to1.SLDASM any more: it was '
                              'renamed or deleted in SolidWorks.'], texts
    assert not [m.name for m in sw.mates if m.suppressed]
