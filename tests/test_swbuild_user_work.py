"""W9a package A (ISSUE-1-PLAN §2.1, §5's tests against the fake; W9A-INTERFACES.md): Update leaves the user's work
in a built assembly alone, puts a component the user locked to a gear along with it (route (c1)), or refuses before
any write with a sentence naming what is in the way.

The fake is tests/test_swbuild.py's: ``user_component``, ``user_lock`` and ``user_mate`` add the user's work, and the
fake raises AssertionError on any write to it but a put of one of the user's components (``user_puts``), which only
route (c1) may make."""

from dataclasses import replace

import pytest

from gear_generator import findings, swbuild, swcom
from gear_generator.gears import kind_for, spur as spur_gears
from gear_generator.gears.base import GlobalVariable
from gear_generator.gears.equations import DEGREES, split_equation
from gear_generator.spec import GearSpec, as_built
from gear_generator.swbuild import (PROBLEM_LOCK_BY_MODE, PROBLEM_OTHER_KIND, PROBLEM_TIE, PROBLEM_TWO_BODIES,
                                    PROBLEM_UNSETTLED, PROBLEM_VALUE, UserWorkRefused)

from test_swbuild import (CHANGING, IDENTITY9, P17, P51, P68, S17, S51, S68, TC_DOG, TC_MODES, TC_SLEEVE, T_ASM, TC_ASM,
                          W, _close, _compose,
                          _frame_off, _inverse, _key, _motion, _rot_z, _tc_motion, _tc_update, _train_frames,
                          _train_layout_values, _train_placements, _train_routes_agree, _update_train, _values,
                          _built_train, mode_findings, names, plan, tc_built)  # noqa: F401

@pytest.fixture(autouse=True)
def no_carrier_measured(monkeypatch):
    """Route (c1) on a train with no carrier (the T train's, the TransferCase's, with modes) as if a run had read it
    clean on both versions (findings.USER_MATE_PUT_NO_CARRIER_ON_<year> and …_NO_CARRIER_MODES_ON_<year> True), so
    the tests below reach what they are about; the committed values, and the other branches, are tested where a test
    unsets or sets them itself."""
    for year in (2026, 2024):
        monkeypatch.setattr(findings, f"USER_MATE_PUT_NO_CARRIER_ON_{year}", True, raising=False)
        monkeypatch.setattr(findings, f"USER_MATE_PUT_NO_CARRIER_MODES_ON_{year}", True, raising=False)


SPROCKET = W + "Sprocket.SLDPRT"
HOUSING = W + "Housing.SLDPRT"
MODE_CHANGES = CHANGING + ("show_configuration", "set_mate_suppressed_in", "set_dimension_in")


def _moving(fake, **kwargs):
    """An Update that moves shaft S3, so every train of the T train is put back whole."""
    kwargs.setdefault("layout", _train_layout_values("64.5"))
    kwargs.setdefault("placements", _train_placements(_train_frames(s3=(64.5, 51.0))))
    return _update_train(fake, **kwargs)


def _turn_about_z(frame, degrees):
    """A frame turned about the world Z axis through the origin (a turn of the S1 shaft, which stands there)."""
    return _compose((_rot_z(degrees), (0.0, 0.0, 0.0)), frame)


def _sprocket_on_g1(fake, name="Sprocket-1", z=30.0, lock="UserLock1", axis="UserAxis1"):
    """The user's sprocket on S1's axis in front of G1, locked to G1, its axis on the layout's S1 Axis."""
    fake.user_component(T_ASM, name, SPROCKET, (IDENTITY9, (0.0, 0.0, z)))
    fake.user_lock(T_ASM, lock, "gear1-1", name)
    if axis:
        fake.user_mate(T_ASM, axis, kind="coincident", a=(name, "Gear Axis"), b=("layout-1", "S1 Axis"))


def _relative(fake, gear, component):
    return _compose(_inverse(fake.frames[gear]), fake.frames[component])


def _no_changes(fake):
    return not [n for n in names(fake) if n in MODE_CHANGES]


# -- the user's components and mates among themselves and to the layout never refuse ---------------------------------


def test_the_users_components_and_their_mates_to_each_other_and_the_layout_never_refuse_and_are_never_written():
    fake = _built_train()
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_component(T_ASM, "Chain-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 60.0)))
    fake.user_mate(T_ASM, "Coincident7", kind="coincident", a=("Chain-1", "plane1"), b=("Housing-1", "plane1"))
    fake.user_mate(T_ASM, "Concentric8", kind="coincident", a=("Chain-1", "Gear Axis"), b=("layout-1", "S1 Axis"))
    fake.user_mate(T_ASM, "Distance9", kind="distance", a=("Housing-1", "plane2"), b=("asm", "plane2"))
    result = _moving(fake)
    assert result.ok, result.log_lines()
    assert fake.user_puts == [] and result.carried == [] and result.extra_mates == []
    work = result.user_work
    assert [c.name for c in work.components] == ["Housing-1", "Chain-1"]
    assert [c.fixed for c in work.components] == [True, False]
    assert {m.name: m.touches for m in work.mates} == {
        "Coincident7": (("user", "Chain-1"), ("user", "Housing-1")),
        "Concentric8": (("user", "Chain-1"), ("layout", "")),
        "Distance9": (("user", "Housing-1"), ("assembly", ""))}
    assert all(m.on == ("",) and m.kind == swbuild.USER_OTHER for m in work.mates)
    assert work.read_at and work.carried == []
    assert not any(fake.mate(n, T_ASM).suppressed for n in ("Coincident7", "Concentric8", "Distance9"))
    lines = result.log_lines()
    assert "CHECK   your components, left as they are but where put with a gear: Housing-1, Chain-1" in lines
    assert "CHECK   your mates, left on as they are: Coincident7, Concentric8, Distance9" in lines


def test_a_mate_of_the_users_suppressed_everywhere_is_listed_as_before():
    fake = _built_train()
    fake.user_mate(T_ASM, "Angle1", suppressed=True)
    result = _moving(fake)
    assert result.ok and result.extra_mates == ["Angle1"]
    assert result.user_work.mates[0].on == ()


# -- the assembly's own entity (W9c probes' review, must-fix 1) -----------------------------------------------------


@pytest.mark.parametrize("answer", ["none", "root"])
def test_a_mate_to_the_assemblys_own_plane_reads_user_to_assembly_whichever_way_solidworks_names_it(answer):
    """SolidWorks 2024 gives the assembly's own entity no component; 2026 gives the active configuration's root
    component, named "T" here (findings.ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_2026). Either way the mate reads
    user-to-assembly, and the inventory never lists the assembly as a component of the user's."""
    fake = _built_train()
    fake.assembly_entity = answer
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_mate(T_ASM, "Distance9", kind="distance", a=("Housing-1", "plane2"), b=("asm", "plane2"))
    result = _moving(fake)
    assert result.ok, result.failures
    (mate,) = result.user_work.mates
    assert mate.touches == (("user", "Housing-1"), ("assembly", "")) and mate.whole
    assert [c.name for c in result.user_work.components] == ["Housing-1"]
    # The root is read only where an entity names no top-level component (2026's answer), resolved as measured.
    assert [a for n, a in fake.calls if n == "root_component"] == ([(True,)] if answer == "root" else [])


@pytest.mark.parametrize("answer", ["none", "root"])
def test_the_root_is_never_read_on_an_assembly_with_a_lightweight_component(answer):
    """The W9c review's should-fix 5: GetRootComponent3(True) was measured marking nothing only on an assembly all
    resolved; on one with a lightweight component it is not called, and an entity that needed it reads as not wholly
    read (it refuses only where something is put, as W9a refuses an unread mate)."""
    fake = _built_train()
    fake.assembly_entity = answer
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.lightweight.add("Housing-1")
    fake.user_mate(T_ASM, "Distance9", kind="distance", a=("Housing-1", "plane2"), b=("asm", "plane2"))
    result = _update_train(fake)                       # nothing moves: nothing is put
    assert result.ok, result.failures
    (mate,) = result.user_work.mates
    if answer == "root":
        assert mate.touches[1] == (swbuild.UNREAD_ENTITY, "") and not mate.whole
    else:
        assert mate.touches[1] == ("assembly", "") and mate.whole
    assert "root_component" not in names(fake) and "Housing-1" in fake.lightweight     # nothing resolved
    assert {c.name: c.state for c in result.user_work.components}["Housing-1"] == 1


def test_the_fake_resolves_and_marks_on_a_lightweight_assembly_as_the_measurement_suggests():
    fake = _built_train()
    fake.open_document(T_ASM)
    fake.user_component(T_ASM, "Housing-1", HOUSING)
    fake.lightweight.add("Housing-1")
    fake.touched.clear()
    assert fake.root_component(False) == "T" and "Housing-1" in fake.lightweight and not fake.touched
    assert fake.root_component(True) == "T" and "Housing-1" not in fake.lightweight and fake.touched


@pytest.mark.parametrize("answer", ["none", "root"])
def test_a_mate_to_a_leaf_inside_a_user_sub_assembly_maps_to_its_top_level_component(answer):
    """The coordinator's ruling on the read (2026-11-17): a leaf's Name2 comes as a path, "UserSub-1/P2Sprocket-1"
    (findings.M1_READS_SUBASSEMBLY_LEAF_ON_2026), and must read as the user's top-level component, never as not
    wholly read."""
    fake = _built_train()
    fake.assembly_entity = answer
    fake.user_component(T_ASM, "UserSub-1", W + "UserSub.SLDASM", (IDENTITY9, (0.0, 0.0, 60.0)))
    fake.user_mate(T_ASM, "Coincident1", kind="coincident", a=("layout-1", "S1 Axis"),
                   b=("UserSub-1/P2Sprocket-1", "Gear Axis"))
    result = _moving(fake)
    assert result.ok, result.failures
    (mate,) = result.user_work.mates
    assert mate.touches[1] == ("user", "UserSub-1") and mate.whole


def _refusals(answer, build):
    fake = _built_train()
    fake.assembly_entity = answer
    build(fake)
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    return [(p.kind, p.mates, p.sentence) for p in raised.value.problems], _no_changes(fake)


@pytest.mark.parametrize("build", ["other kind", "ground"])
def test_todays_refusals_over_the_assemblys_own_plane_are_the_same_whichever_way_it_is_named(build):
    """A user angle from G1 to the assembly's plane (another kind on a put gear), and a sprocket locked to G1 and
    held to the assembly's plane by a user lock (a chain to the ground): refused alike either way."""
    def other_kind(fake):
        fake.user_mate(T_ASM, "Angle1", kind="angle", a=("gear1-1", "plane2"), b=("asm", "plane2"))

    def ground(fake):
        fake.user_component(T_ASM, "Sprocket-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 30.0)))
        fake.user_lock(T_ASM, "UserLock1", "gear1-1", "Sprocket-1")
        fake.user_mate(T_ASM, "UserLock9", kind="lock", a=("Sprocket-1", ""), b=("asm", ""))
    made = {"other kind": other_kind, "ground": ground}[build]
    none, none_clean = _refusals("none", made)
    root, root_clean = _refusals("root", made)
    assert none == root and none and none_clean and root_clean
    assert "T is" not in " ".join(sentence for _, _, sentence in root)


def test_with_the_root_unread_a_name_that_is_no_component_is_said_as_unread_never_a_users_component():
    fake = _built_train()
    fake.assembly_entity, fake.root_unread = "root", True
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_mate(T_ASM, "Distance9", kind="distance", a=("Housing-1", "plane2"), b=("asm", "plane2"))
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (mate,) = raised.value.user_work.mates
    assert mate.touches == (("user", "Housing-1"), (swbuild.UNREAD_ENTITY, "")) and not mate.whole
    assert [c.name for c in raised.value.user_work.components] == ["Housing-1"]
    assert [p.kind for p in raised.value.problems] == [swbuild.PROBLEM_UNREAD]


# -- route (c1): a component the user locked to a gear Update puts goes with it ---------------------------------------


def test_a_sprocket_locked_to_a_gear_update_puts_is_put_by_the_gears_own_rigid_motion_after_the_apps_bodies():
    fake = _built_train()
    _sprocket_on_g1(fake)
    built_rel = _relative(fake, "gear1-1", "Sprocket-1")
    for gear, turn in (("gear1-1", 10.0), ("Sprocket-1", 10.0)):         # the user turned G1, the sprocket with it
        fake.frames[gear] = _turn_about_z(fake.frames[gear], turn)
    result = _moving(fake)
    assert result.ok, result.log_lines()
    assert result.carried == [("Sprocket-1", "G1", "")]
    assert [name for name, _, _ in fake.user_puts] == ["Sprocket-1"]
    assert _close(_relative(fake, "gear1-1", "Sprocket-1"), built_rel, 1e-9)
    assert _close(fake.frames["gear1-1"], _train_frames()["G1"], 1e-9)
    assert result.user_work.carried == [("Sprocket-1", "G1", ("UserLock1",))]
    # After every app body of the train, before the app's lock goes back on; the user's lock never touched.
    calls = fake.calls
    puts = [i for i, (n, a) in enumerate(calls) if n == "place_component"]
    sprocket = next(i for i, (n, a) in enumerate(calls) if n == "place_component" and fake.found.get(a[0]) ==
                    "Sprocket-1")
    lock_on = next(i for i, (n, a) in enumerate(calls) if n == "set_mate_suppressed" and a[1] is False)
    assert sprocket == max(i for i in puts if i < lock_on) and sprocket > min(puts)
    assert not fake.mate("UserLock1", T_ASM).suppressed and not fake.mate("UserAxis1", T_ASM).suppressed
    assert "ok      put Sprocket-1 with G1" in result.log_lines()


def test_a_chain_of_the_users_locks_is_put_whole_with_its_gear():
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.user_component(T_ASM, "Sprocket-3", SPROCKET, (IDENTITY9, (0.0, 0.0, 40.0)))
    fake.user_lock(T_ASM, "UserLock3", "Sprocket-1", "Sprocket-3")
    rel1, rel3 = _relative(fake, "gear1-1", "Sprocket-1"), _relative(fake, "gear1-1", "Sprocket-3")
    for body in ("gear1-1", "Sprocket-1", "Sprocket-3"):
        fake.frames[body] = _turn_about_z(fake.frames[body], 7.0)
    result = _moving(fake)
    assert result.ok, result.log_lines()
    assert sorted(result.carried) == [("Sprocket-1", "G1", ""), ("Sprocket-3", "G1", "")]
    assert _close(_relative(fake, "gear1-1", "Sprocket-1"), rel1, 1e-9)
    assert _close(_relative(fake, "gear1-1", "Sprocket-3"), rel3, 1e-9)


def test_a_sprocket_on_a_train_update_does_not_put_is_left_where_it_stands():
    fake = _built_train()
    _sprocket_on_g1(fake)
    before = fake.frames["Sprocket-1"]
    result = _update_train(fake)                         # nothing changes: nothing is put
    assert result.ok and result.carried == [] and fake.user_puts == []
    assert fake.frames["Sprocket-1"] == before
    assert result.user_work.carried == []


def test_without_the_route_finding_a_lock_on_a_put_gear_refuses_before_any_write(monkeypatch):
    monkeypatch.setattr(findings, "USER_MATE_PUT_ROUTE", None, raising=False)
    fake = _built_train()
    _sprocket_on_g1(fake)
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert [p.kind for p in raised.value.problems] == [PROBLEM_UNSETTLED]
    assert "(findings.USER_MATE_PUT_ROUTE is None)" in str(raised.value) and "UserLock1" in str(raised.value)
    assert _no_changes(fake)


# -- every other kind of the user's mate on a put gear refuses, every one named at once ---------------------------------


def test_a_user_gear_mate_and_a_mate_to_a_gears_plane_on_put_gears_refuse_together_before_any_write():
    fake = _built_train()
    fake.user_component(T_ASM, "Sprocket-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 30.0)))
    fake.user_mate(T_ASM, "Gear5", kind="gear", a=("Sprocket-1", "Gear Axis"), b=("gear1-1", "Gear Axis"))
    fake.user_mate(T_ASM, "Angle1")                      # gear1-1's plane to the layout's (the fake's default)
    marked = set(fake.touched)
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert [(p.kind, p.mates) for p in raised.value.problems] == [(PROBLEM_OTHER_KIND, ("Gear5",)),
                                                                  (PROBLEM_OTHER_KIND, ("Angle1",))]
    assert str(raised.value) == (
        "Gear5 is a mate in T.SLDASM that Gear Generator did not make, on G1, which Update SolidWorks puts back, and a "
        "mate of that kind is not moved with its gear, so nothing is changed; lock your component to G1 instead, and "
        "Update SolidWorks puts it with G1, or suppress Gear5 in SolidWorks, and press Update SolidWorks again. "
        "Angle1 is a mate in T.SLDASM that Gear Generator did not make, on G1, which Update SolidWorks puts back, and "
        "a mate of that kind is not moved with its gear, so nothing is changed; lock your component to G1 instead, "
        "and Update SolidWorks puts it with G1, or suppress Angle1 in SolidWorks, and press Update SolidWorks again.")
    assert raised.value.user_work is not None and [m.name for m in raised.value.user_work.mates] == ["Gear5", "Angle1"]
    assert _no_changes(fake) and fake.touched == marked


def test_a_user_gear_mate_on_a_component_route_c1_would_put_refuses():
    fake = _built_train()
    _sprocket_on_g1(fake, axis="")
    fake.user_component(T_ASM, "Idler-1", SPROCKET, (IDENTITY9, (30.0, 0.0, 30.0)))
    fake.user_mate(T_ASM, "Gear6", kind="gear", a=("Sprocket-1", "Gear Axis"), b=("Idler-1", "Gear Axis"))
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert [(p.kind, p.mates) for p in raised.value.problems] == [(PROBLEM_OTHER_KIND, ("Gear6",))]
    assert _no_changes(fake)


def test_a_mate_on_a_gear_update_does_not_put_is_left_alone():
    fake = _built_train()
    fake.user_mate(T_ASM, "Angle1")
    result = _update_train(fake)
    assert result.ok and fake.user_puts == [] and not fake.mate("Angle1", T_ASM).suppressed


# -- the two-train mate and the grounded tie --------------------------------------------------------------------------


def test_a_user_lock_holding_two_of_the_apps_gears_together_refuses_naming_it():
    fake = _built_train()
    fake.user_lock(T_ASM, "Lock5", "gear1-1", "gear4-1")
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert [(p.kind, p.mates) for p in raised.value.problems] == [(PROBLEM_TWO_BODIES, ("Lock5",))]
    assert str(raised.value) == ("Your Lock5 holds G1 and G4 together, and no put of Update SolidWorks can keep it, "
                                 "since it puts each of them back to its own built place, so nothing is changed; "
                                 "suppress Lock5 in SolidWorks and press Update SolidWorks again.")
    assert _no_changes(fake)


def test_two_gears_held_together_through_the_users_components_refuse_naming_every_lock():
    fake = _built_train()
    _sprocket_on_g1(fake, axis="")
    fake.user_lock(T_ASM, "UserLock2", "Sprocket-1", "gear2-1")
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_TWO_BODIES and problem.mates == ("UserLock1", "UserLock2")
    assert "together through Sprocket-1" in problem.sentence


def test_a_grounded_tie_refuses_before_any_write_naming_every_user_mate_on_the_train():
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, 60.0)), fixed=True)
    fake.user_mate(T_ASM, "UserTie", kind="coincident", a=("Sprocket-1", "plane2"), b=("Housing-1", "plane2"))
    fake.locks["UserTie"] = ["gear1-1", "gear2-1", "gear3-1", "gear4-1", "Sprocket-1"]
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_TIE and problem.mates == ("UserLock1", "UserAxis1", "UserTie")
    assert "SolidWorks reads it as unable to turn" in problem.sentence
    # Re-pinned at the coordinator's addendum: each mate named once, in what to suppress.
    assert problem.sentence == (
        "Update SolidWorks must turn G1's train back to its built place, and SolidWorks reads it as unable to turn "
        "with your mates on it, so nothing is changed; suppress UserLock1, UserAxis1 and UserTie in SolidWorks and "
        "press Update SolidWorks again.")
    assert [a[0] for n, a in fake.calls if n == "constrained_status"]          # read, the user's mates on
    assert _no_changes(fake)


def test_a_lock_chain_to_a_fixed_component_of_the_users_is_a_tie_whatever_the_read_says():
    fake = _built_train()
    _sprocket_on_g1(fake, axis="")
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, 60.0)), fixed=True)
    fake.user_lock(T_ASM, "UserLock9", "Sprocket-1", "Housing-1")
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert [(p.kind, p.mates) for p in raised.value.problems] == [(PROBLEM_TIE, ("UserLock1", "UserLock9"))]
    assert str(raised.value) == ("Your UserLock1 and UserLock9 hold G1 to Housing-1, which does not move, and Update "
                                 "SolidWorks must put G1 back, so nothing is changed; suppress UserLock1 and UserLock9 "
                                 "in SolidWorks and press Update SolidWorks again.")
    assert not [n for n, _ in fake.calls if n == "constrained_status"]        # nothing read, nothing said read


def test_a_tie_on_a_train_nothing_puts_does_not_refuse():
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, 60.0)), fixed=True)
    fake.user_mate(T_ASM, "UserTie", kind="coincident", a=("Sprocket-1", "plane2"), b=("Housing-1", "plane2"))
    fake.locks["UserTie"] = ["gear1-1", "gear2-1", "gear3-1", "gear4-1"]
    result = _update_train(fake)
    assert result.ok and result.placed == [] and fake.user_puts == []


def test_without_the_tie_rule_a_train_with_the_users_mates_on_it_refuses(monkeypatch):
    monkeypatch.setattr(findings, "USER_TIE_RULE", None, raising=False)
    fake = _built_train()
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, 60.0)), fixed=True)
    fake.user_mate(T_ASM, "Touch1", kind="coincident", a=("Housing-1", "plane1"), b=("layout-1", "plane1"))
    assert _moving(fake).ok                                # no user mate on a train: no read, no refusal
    fake = _built_train()
    _sprocket_on_g1(fake)
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert [p.kind for p in raised.value.problems] == [PROBLEM_UNSETTLED]
    assert "(findings.USER_TIE_RULE is None)" in str(raised.value)


# -- errors read before and after; the post-check names the user's mates ---------------------------------------------


def test_a_user_mate_already_in_error_is_not_laid_to_the_update():
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.mate_codes = {"UserAxis1": (47, False)}
    result = _moving(fake)
    assert result.ok, result.failures
    assert result.user_work.in_error == ["UserAxis1"] and result.user_in_error == [("", "UserAxis1")]
    assert "CHECK   yours, in error before this Update: UserAxis1" in result.log_lines()


def test_a_user_mate_the_update_put_in_error_is_named_as_the_users():
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.codes_after_put = {"UserAxis1": (47, False)}
    result = _moving(fake)
    assert ("T.SLDASM", "Your mate UserAxis1 is in error in SolidWorks, and was not before this Update.") \
        in result.failures
    assert ("T.SLDASM", "The mate UserAxis1 is in error in SolidWorks.") not in result.failures


def test_a_component_of_the_users_the_update_put_in_error_is_named_and_one_already_in_error_is_not():
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.component_codes = {"Housing-1": 2}
    fake.codes_after_put = {}
    original = fake.place_component

    def put(handle, rotation, at, kind=None):
        original(handle, rotation, at, kind=kind)
        fake.component_codes["Sprocket-1"] = 2
    fake.place_component = put
    result = _moving(fake)
    assert ("T.SLDASM", "Your Sprocket-1 is in error in SolidWorks, and was not before this Update.") in result.failures
    assert not [f for f in result.failures if "Housing-1" in f[1]]
    assert sorted(result.user_in_error) == [("", "Housing-1"), ("", "Sprocket-1")]
    assert result.user_work.in_error == ["Housing-1"]


def test_a_failed_rebuild_says_what_of_the_users_was_already_in_error():
    sentence = swbuild._rebuild_sentence("T", "", swbuild._UserPlan(in_error=["UserAxis1", "Housing-1"]))
    assert sentence == ("SolidWorks reported an error rebuilding T. Your UserAxis1 and Housing-1 were already in error "
                        "before this Update.")
    assert swbuild._rebuild_sentence("T", " in 2H", None) == "SolidWorks reported an error rebuilding T in 2H."


def test_free_to_turn_names_the_users_mates_on_the_gears_train():
    fake = _built_train()
    fake.constrained = {"gear1-1": 3, "gear2-1": 4}
    for handle, name in (("placed1", "gear1-1"), ("placed2", "gear2-1")):
        fake.find_component(handle, name)
    said = swbuild._free_to_turn(fake, ["placed1", "placed2"], {"placed1": "G1", "placed2": "G2"}.get,
                                 {"G1": ("UserLock1", "UserTie"), "G2": ("UserLock1", "UserTie")})
    assert said == ["G1 cannot turn: SolidWorks reads it fully defined; your UserLock1 and UserTie are on its train.",
                    "G2 is over-defined in SolidWorks; your UserLock1 and UserTie are on its train."]
    assert swbuild._free_to_turn(fake, ["placed1"], {"placed1": "G1"}.get) == [
        "G1 cannot turn: SolidWorks reads it fully defined."]


# -- K1: a component renamed in SolidWorks is found by its part --------------------------------------------------------


def _placements_with_parts(frames=None):
    parts = {"G1": P17, "G2": W + "Gear_m1.5_N68.SLDPRT", "G3": P17, "G4": P51}
    return [replace(p, part=parts[p.gear]) for p in _train_placements(frames)]


def test_a_component_renamed_in_solidworks_is_found_by_its_part_and_its_new_name_returned():
    fake = _built_train()
    fake.rename_component(T_ASM, "gear4-1", "Gear_m1.5_N51-7")
    result = _moving(fake, placements=_placements_with_parts(_train_frames(s3=(64.5, 51.0))))
    assert result.ok, result.log_lines()
    assert result.renamed == [("G4", "gear4-1", "Gear_m1.5_N51-7")]
    assert _close(fake.frames["Gear_m1.5_N51-7"], _train_frames(s3=(64.5, 51.0))["G4"], 1e-9)
    assert "ok      found G4's component by its part as Gear_m1.5_N51-7 (on record as gear4-1)" in result.log_lines()


def test_a_renamed_component_with_two_unclaimed_instances_of_its_part_is_not_as_built():
    fake = _built_train()
    fake.rename_component(T_ASM, "gear4-1", "Gear_m1.5_N51-7")
    fake.user_component(T_ASM, "Gear_m1.5_N51-8", P51, (IDENTITY9, (200.0, 0.0, 0.0)))
    with pytest.raises(swbuild.NotAsBuilt):
        _moving(fake, placements=_placements_with_parts(_train_frames(s3=(64.5, 51.0))))
    assert _no_changes(fake)


def test_a_renamed_component_without_its_part_on_record_is_not_as_built_as_before():
    fake = _built_train()
    fake.rename_component(T_ASM, "gear4-1", "Gear_m1.5_N51-7")
    with pytest.raises(swbuild.NotAsBuilt):
        _moving(fake)


# -- K11: a value the app owns that the user changed in SolidWorks ------------------------------------------------------


def _edit(fake, path, name, expression):
    """A global the user changed in SolidWorks, in the open document (and its file)."""
    for texts in (fake.memory[_key(path)][0], fake.saved[_key(path)][0]):
        for i, text in enumerate(texts):
            if split_equation(text)[0] == name:
                texts[i] = f'"{name}"= {expression}'


def _recorded(spec):
    return tuple((v.name, v.expression_for(DEGREES)) for v in _values(spec))


def test_a_part_global_the_user_changed_refuses_naming_both_values_and_the_cell():
    fake = _built_train()
    _edit(fake, P17, "Face Width", "14")
    wanted = _values(S17.with_values(face_width="12"))
    doc = swbuild.DocumentValues(P17, wanted, recorded=_recorded(S17), cells=(("Face Width", "Gears!I3"),))
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, parts=[doc])
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_VALUE
    assert problem.values == (swbuild.ValueEdit("Gear_m1.5_N17.SLDPRT", "Face Width", "14", "12", "10",
                                                cell="Gears!I3"),)
    assert str(raised.value) == ("Face Width in Gear_m1.5_N17 is 14 in SolidWorks and 12 in the workbook: type 14 in "
                                 "Gears!I3, or set it back to 12 in SolidWorks, and press Update SolidWorks again.")
    assert _no_changes(fake)


def test_a_blank_bore_in_the_workbook_is_said_as_no_bore_never_as_0():
    """The coordinator's addendum: the workbook's Bore cell blank stands for no bore (the global reads 0)."""
    fake = _built_train()
    _edit(fake, P17, "Bore Diameter", "12")
    doc = swbuild.DocumentValues(P17, _values(S17.with_values(bore="")), recorded=_recorded(S17),
                                 cells=(("Bore Diameter", "Gears!J2"),))
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, parts=[doc])
    (problem,) = raised.value.problems
    assert problem.values[0].wanted == "0" and problem.values[0].blank == "no bore"
    assert str(raised.value) == ("Bore Diameter in Gear_m1.5_N17 is 12 in SolidWorks and no bore (its Bore blank or 0) "
                                 "in the workbook: type 12 in Gears!J2, or set it back to 0 in SolidWorks, and press "
                                 "Update SolidWorks again.")


def test_a_blank_backlash_or_fillet_is_said_as_the_equation_it_stands_for():
    """A blank Backlash is the 0.3 × Module equation, a blank Fillet 0.38 × Module (spec backlash_mm / fillet_mm):
    said with its value, and what to set back is the equation, not the number."""
    fake = _built_train()
    _edit(fake, P17, "Backlash", "0.2")
    _edit(fake, P17, "Fillet Radius", "0.5")
    doc = swbuild.DocumentValues(P17, _values(S17), recorded=_recorded(S17),
                                 cells=(("Backlash", "Gears!P2"), ("Fillet Radius", "Gears!Q2")))
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, parts=[doc])
    said = [p.sentence for p in raised.value.problems]
    assert said == [
        "Backlash in Gear_m1.5_N17 is 0.2 in SolidWorks and 0.45 (from its blank cell, 0.3 × Module) in the workbook: "
        "type 0.2 in Gears!P2, or set it back to the equation 0.3 × Module in SolidWorks, and press Update SolidWorks "
        "again.",
        "Fillet Radius in Gear_m1.5_N17 is 0.5 in SolidWorks and 0.57 (from its blank cell, 0.38 × Module) in the "
        "workbook: type 0.5 in Gears!Q2, or set it back to the equation 0.38 × Module in SolidWorks, and press Update "
        "SolidWorks again."]
    assert swbuild._blank_meaning(GlobalVariable("Backlash", "0.2")) == ""          # typed: said as it is
    assert swbuild._blank_meaning(GlobalVariable("Bore Diameter", "10")) == ""


PRINTED_SET_BACK = 'the equation IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )'


def test_a_printed_gears_blank_backlash_is_said_as_the_printed_default_and_set_back_as_its_exact_iif():
    """F1 (PLAN-PRINTED §6, F1-INTERFACES §8): a printed gear's blank Backlash is the IIF, which in K11's usual words
    would read *IIF ( Module <= 1 , 0.3 × Module , 0.3 )*, an equation SolidWorks cannot take back as typed. The
    workbook's value is said in words, and the set-back is the exact text SolidWorks must hold for K11 to read it as
    the app's again. The machined words are test_printed_rule's pins."""
    fake = _built_train()
    _edit(fake, P17, "Backlash", "0.2")
    printed = replace(S17, process="printed")
    # F3 (F3-REVIEW §3, M3): what a real Update hands the worker for this part, built from S17 and typed Printed:
    # update._part plans it through as_built with its record's globals, so no "Bore Allowance" the part never held.
    doc = swbuild.DocumentValues(P17, _values(as_built(printed, _recorded(S17))), recorded=_recorded(S17),
                                 cells=(("Backlash", "Gears!P2"),))
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, parts=[doc])
    (problem,) = raised.value.problems
    assert problem.values[0].blank == "IIF ( Module <= 1 , 0.3 × Module , 0.3 )"     # ValueEdit.blank keeps its meaning
    assert problem.sentence == (
        "Backlash in Gear_m1.5_N17 is 0.2 in SolidWorks and 0.3 (from its blank cell, the printed default: 0.3 mm, or "
        f"0.3 × Module below module 1) in the workbook: type 0.2 in Gears!P2, or set it back to {PRINTED_SET_BACK} in "
        "SolidWorks, and press Update SolidWorks again.")
    assert PRINTED_SET_BACK == "the equation " + spur_gears.printed_backlash_expression()


@pytest.mark.parametrize("cell, unsaved, said", [
    ("", False, "Backlash in Gear_m0.5_N30_P is 0.2 in SolidWorks and 0.15 (from its blank cell, the printed default: "
                "0.3 mm, or 0.3 × Module below module 1) in the workbook, and no cell of the workbook sets it alone: "
                f"set it back to {PRINTED_SET_BACK} in SolidWorks and press Update SolidWorks again."),
    ("Gears!P2", True, "Backlash in Gear_m0.5_N30_P is 0.2 in SolidWorks and 0.15 (from its blank cell, the printed "
                       "default: 0.3 mm, or 0.3 × Module below module 1) in the workbook, where Update SolidWorks last "
                       "set 0.15 and left Gear_m0.5_N30_P unsaved: either it was changed in SolidWorks since, or "
                       "SolidWorks closed without saving that Update and Gear_m0.5_N30_P was changed after it was "
                       "opened again. If it was changed, type 0.2 in Gears!P2, or set it back to "
                       f"{PRINTED_SET_BACK} in SolidWorks; if that Update was lost, set it to {PRINTED_SET_BACK} in "
                       "SolidWorks. Then press Update SolidWorks again."),
])
def test_the_printed_defaults_words_with_no_cell_and_on_a_document_left_unsaved(cell, unsaved, said):
    """Below module 1 the printed default is 0.3 × module, the same value as machined; the words are the printed
    default's still, since the equation SolidWorks must hold is the IIF."""
    spec = GearSpec(process="printed", module="0.5", teeth="30")
    kind = kind_for(spec)
    variable = next(v for v in kind.variables(spec, kind.derive(spec)) if v.name == "Backlash")
    edit = swbuild.ValueEdit(spec.stem() + ".SLDPRT", "Backlash", "0.2", "0.15", "0.15", cell=cell, unsaved=unsaved,
                             blank=swbuild._blank_meaning(variable))
    assert swbuild._value_sentence(edit) == said


def test_a_printed_gears_typed_backlash_and_its_blank_fillet_are_said_as_before():
    """Only the printed default takes new words: a typed Backlash is said as typed, and a blank Fillet is still its
    0.38 × Module equation."""
    spec = GearSpec(process="printed", backlash="0.25")
    kind = kind_for(spec)
    variables = {v.name: v for v in kind.variables(spec, kind.derive(spec))}
    assert swbuild._blank_meaning(variables["Backlash"]) == ""
    fillet = swbuild.ValueEdit("G.SLDPRT", "Fillet Radius", "0.5", "0.57", "0.57", cell="Gears!Q2",
                               blank=swbuild._blank_meaning(variables["Fillet Radius"]))
    assert swbuild._value_sentence(fillet) == (
        "Fillet Radius in G is 0.5 in SolidWorks and 0.57 (from its blank cell, 0.38 × Module) in the workbook: type "
        "0.5 in Gears!Q2, or set it back to the equation 0.38 × Module in SolidWorks, and press Update SolidWorks "
        "again.")


def test_every_value_and_every_mate_in_the_way_is_named_at_once():
    fake = _built_train()
    _edit(fake, P17, "Face Width", "14")
    _edit(fake, P17, "Bore Diameter", "12")
    fake.user_lock(T_ASM, "Lock5", "gear1-1", "gear4-1")
    doc = swbuild.DocumentValues(P17, _values(S17), recorded=_recorded(S17))
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake, parts=[doc])
    assert [p.kind for p in raised.value.problems] == [PROBLEM_VALUE, PROBLEM_VALUE, PROBLEM_TWO_BODIES]
    assert [p.values[0].name for p in raised.value.problems[:2]] == ["Bore Diameter", "Face Width"]
    assert raised.value.problems[0].sentence == (
        "Bore Diameter in Gear_m1.5_N17 is 12 in SolidWorks and 10 in the workbook, and no cell of the workbook sets "
        "it alone: set it back to 10 in SolidWorks and press Update SolidWorks again.")


def test_a_value_the_record_cannot_vouch_for_is_set_back_as_before():
    """An Update left unsaved and lost (the record's unsaved or mismatched mark): ``recorded`` None, so the
    difference is not the user's and Update sets it, as W4 did."""
    fake = _built_train()
    _edit(fake, P17, "Face Width", "14")
    result = _update_train(fake, parts=[swbuild.DocumentValues(P17, _values(S17))])
    assert result.ok and result.parts[0].changed == ["Face Width"]


def test_a_part_value_the_user_set_to_what_the_workbook_now_asks_is_no_conflict():
    fake = _built_train()
    _edit(fake, P17, "Face Width", "12")
    doc = swbuild.DocumentValues(P17, _values(S17.with_values(face_width="12")), recorded=_recorded(S17))
    assert _update_train(fake, parts=[doc]).ok


def test_a_layout_global_the_user_changed_refuses_with_its_shafts_cell():
    fake = _built_train()
    _edit(fake, swbuild_layout(), "S3 X", "70")
    layout = replace(_train_layout_values("64.5"),
                     recorded=(("S2 X", "63.75"), ("S3 X", "63.75"), ("S3 Y", "51")), cells=(("S3 X", "Shafts!C4"),))
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake, layout=layout)
    assert str(raised.value) == ("S3 X in T_Layout is 70 in SolidWorks and 64.5 in the workbook: type 70 in "
                                 "Shafts!C4, or set it back to 64.5 in SolidWorks, and press Update SolidWorks again.")


def swbuild_layout():
    from test_swbuild import T_LAYOUT
    return T_LAYOUT


def test_a_face_z_the_user_changed_refuses_when_the_record_holds_and_is_set_when_it_does_not():
    fake = _built_train()
    _edit(fake, T_ASM, "G4 Face Z", "22")
    wanted = _train_frames(z4=25.0)
    motion = _motion(face_globals=(("G4", GlobalVariable("G4 Face Z", "25")),), record_holds=True,
                     recorded_faces=(("G4", "20"),), cells=(("G4 Face Z", "Gears!C6"),))
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, placements=_train_placements(wanted), motion=motion)
    assert str(raised.value) == (
        "G4 Face Z in T is 22 mm in SolidWorks, where Gear Generator set it to 20 mm and the workbook now asks 25 mm: "
        "set it back to 25 mm in SolidWorks, or change Gears!C6 so the workbook asks 22 mm, and press Update "
        "SolidWorks again.")
    assert _no_changes(fake)
    done = _update_train(fake, placements=_train_placements(wanted), motion=replace(motion, record_holds=False))
    assert done.ok and done.axial == ["G4"]


def test_a_recorded_mate_the_user_suppressed_refuses_when_the_record_holds_overturning_d10():
    fake = _built_train()
    fake.mate("G3 locked to G2", T_ASM).suppressed = True
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, motion=_motion(record_holds=True))
    assert str(raised.value) == ("The mate G3 locked to G2 is suppressed in SolidWorks, where Gear Generator made it "
                                 "on and the workbook has it on: in SolidWorks, turn it back on and press Update "
                                 "SolidWorks again.")
    assert _no_changes(fake)
    assert _update_train(fake).unsuppressed == ["G3 locked to G2"]          # no record to vouch: D10, as before


# -- K3: the user's features in an app part ---------------------------------------------------------------------------


def _p17_update(**changes):
    return swbuild.DocumentValues(P17, _values(S17.with_values(face_width="12")),
                                  made=swbuild.plan_features(plan(S17, path=P17)), **changes)


def test_the_users_features_in_a_part_are_read_kept_and_listed():
    fake = _built_train()
    fake.user_feature(P17, "Keyway")
    result = _update_train(fake, parts=[_p17_update()])
    assert result.ok, result.log_lines()
    assert [(f.name, f.code) for f in result.user_work.features] == [("Keyway", 0)]
    assert result.user_features_in_error == []
    assert "CHECK   your features in Gear_m1.5_N17.SLDPRT, kept: Keyway" in result.log_lines()


def test_a_user_feature_the_rebuild_put_in_error_is_named_as_theirs_and_does_not_stop_the_job():
    fake = _built_train()
    fake.user_feature(P17, "Keyway")
    fake.breaks_on_set[_key(P17)] = [("Keyway", 71)]
    # Every part passed (the demonstration's ruling): the assembly's rebuild then returns False too, and the review's
    # condition 2 reads every app part's features before laying it to the keyway.
    result = _update_train(fake, parts=_every_t_part())
    assert result.ok, result.failures
    assert [(f.name, f.code) for f in result.user_features_in_error] == [("Keyway", 71)]
    assert not result.parts[0].rebuilt and result.parts[0].changed == ["Face Width"]
    lines = result.log_lines()
    assert "CHECK   the rebuild reported an error, from your features alone: Keyway" in lines
    # The demonstration's ruling (k3): newly in error, said with the value set under it.
    assert "CHECK   your Keyway in Gear_m1.5_N17.SLDPRT is in error after the rebuild, which set Face Width 10 -> 12" \
        in lines


def test_a_rebuild_error_on_the_apps_own_feature_is_still_a_failure():
    fake = _built_train()
    fake.user_feature(P17, "Keyway")
    app_feature = swbuild.plan_features(plan(S17, path=P17))[-1]
    fake.breaks_on_set[_key(P17)] = [("Keyway", 71), (app_feature, 1)]
    result = _update_train(fake, parts=[_p17_update()])
    assert ("Gear_m1.5_N17.SLDPRT", "SolidWorks reported an error rebuilding Gear_m1.5_N17.") in result.failures


def test_without_the_part_rebuild_finding_a_rebuild_error_stays_a_failure(monkeypatch):
    monkeypatch.setattr(findings, "WHATS_WRONG_OPENS_ON_PART_REBUILD", None, raising=False)
    fake = _built_train()
    fake.user_feature(P17, "Keyway")
    fake.breaks_on_set[_key(P17)] = [("Keyway", 71)]
    result = _update_train(fake, parts=[_p17_update()])
    assert not result.ok and [f.name for f in result.user_features_in_error] == ["Keyway"]


# -- M3, measured on 2026 (the demonstration's ruling; W9A-INTERFACES §4, item 11) -------------------------------------


def _still(spec, path):
    """A part as the workbook asks it, holding its values already (so not written), its features read."""
    return swbuild.DocumentValues(path, _values(spec), made=swbuild.plan_features(plan(spec, path=path)))


def _every_t_part(first=None):
    """Every app part of the T train, as the workbook passes them all: G1's and G3's (changed by ``first``), G2's and
    G4's holding their values. The review's condition 2 reads every app part's features."""
    return [first or _p17_update(), _still(S68, P68), _still(S51, P51)]


def _tc_update_parts(fake, built, **changes):
    """The TransferCase's Update with both its parts passed, as the workbook does, holding their values."""
    motion, placements = _tc_motion(built, "2H", **changes)
    parts = [_still(GearSpec(), p) for p in (TC_SLEEVE, TC_DOG)]
    return swbuild.update_gearbox(fake, parts=parts, assembly=TC_ASM, placements=placements, motion=motion,
                                  exists=fake.exists, mtime=lambda _p: 0.0)


def _sprocket_part_in_error(fake, name="Sprocket-1"):
    """The user's Sprocket-1 in T, its own part holding a keyway in error (the demonstration's m3)."""
    fake.user_component(T_ASM, name, SPROCKET, (IDENTITY9, (0.0, 0.0, 30.0)))
    fake.feature_codes[(_key(SPROCKET), "User Keyway")] = 71


def test_with_the_finding_the_fakes_assembly_rebuild_fails_on_a_feature_in_error_in_a_part(monkeypatch):
    fake = _built_train()
    fake.open_document(T_ASM)
    assert fake.rebuild(kind=swcom.ASSEMBLY_TRAIN) is True
    _sprocket_part_in_error(fake)
    assert fake.rebuild(kind=swcom.ASSEMBLY_TRAIN) is False
    assert {c.name: c.code for c in fake.components()}["Sprocket-1"] == 1
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2026", None, raising=False)
    assert fake.rebuild(kind=swcom.ASSEMBLY_TRAIN) is True                  # nothing modelled where unmeasured
    assert {c.name: c.code for c in fake.components()}["Sprocket-1"] == 0


def test_the_assembly_rebuild_findings_settle_2026_and_2024(monkeypatch):
    """Re-pinned at the coordinator's ruling on 2024's What's Wrong box: the gate turns on the box not blocking
    (WHATS_WRONG_IN_UPDATE_BLOCKS_ON_<year> False), not on no window opening, so 2024 is settled as 2026 is."""
    settled = {"mate": True, "feature": False, "blocks": False}
    assert swbuild.assembly_rebuild_settled((34, 1, 1)) == settled
    assert swbuild.assembly_rebuild_settled((32, 5, 0)) == settled
    assert swbuild.assembly_rebuild_settled(()) is None
    for value in (None, True):
        monkeypatch.setattr(findings, "WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2024", value)
        assert swbuild.assembly_rebuild_settled((32, 5, 0)) is None
    monkeypatch.setattr(findings, "WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2024", False)
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_2024", None)
    assert swbuild.assembly_rebuild_settled((32, 5, 0)) is None


def test_whats_wrong_shows_in_update_answers_true_false_or_unmeasured(monkeypatch):
    """The helper for package B's sentence."""
    assert swbuild.whats_wrong_shows_in_update((32, 5, 0)) is True
    assert swbuild.whats_wrong_shows_in_update((34, 1, 1)) is False
    assert swbuild.whats_wrong_shows_in_update(()) is None
    monkeypatch.setattr(findings, "WHATS_WRONG_OPENS_IN_UPDATE_WITH_PART_FEATURE_IN_ERROR_ON_2026", None)
    assert swbuild.whats_wrong_shows_in_update((34, 1, 1)) is None              # one False, one unmeasured
    monkeypatch.setattr(findings, "WHATS_WRONG_OPENS_IN_UPDATE_WITH_USER_MATE_IN_ERROR_ON_2024", None)
    assert swbuild.whats_wrong_shows_in_update((32, 5, 0)) is True              # either True is enough
    assert swbuild.whats_wrong_shows_in_update((30, 0, 0)) is None              # a version with no findings


def test_an_update_with_only_the_users_own_part_in_error_goes_on_and_names_it_as_already_in_error():
    """m3 on the fake: the user's Sprocket-1 in error from its own part before the press; the assembly's rebuild
    returns False, nothing of the app's is in error, so the Update finishes and says Sprocket-1 was already in
    error (nothing saved, as any Update)."""
    fake = _built_train()
    _sprocket_part_in_error(fake)
    result = _update_train(fake, parts=_every_t_part())
    assert result.ok, result.failures
    assert not result.rebuilt and result.rebuild_from_user_alone == ["Sprocket-1"]
    assert result.user_work.in_error == ["Sprocket-1"] and result.user_in_error == [("", "Sprocket-1")]
    assert result.user_features_in_error == []
    lines = result.log_lines()
    assert "CHECK   the assembly's rebuild reported an error, from your work alone: Sprocket-1" in lines
    assert "CHECK   yours, in error before this Update: Sprocket-1" in lines
    assert not [n for n, _ in fake.calls if n == "save_as"]


def test_an_update_that_rebuilds_a_users_keyway_in_an_app_part_into_error_goes_on_and_says_the_value_set_under_it():
    """k3 on the fake: the user's keyway in G1's part, fine before; the Update sets the part's Face Width, the part's
    rebuild and the assembly's both return False, only the keyway in error: the Update goes on, naming the keyway as
    the user's, newly in error, and what was set under it."""
    fake = _built_train()
    fake.user_feature(P17, "User Keyway")
    fake.breaks_on_set[_key(P17)] = [("User Keyway", 71)]
    doc = _p17_update(cells=(("Face Width", "Gears!I2"),))
    result = _update_train(fake, parts=_every_t_part(doc))
    assert result.ok, result.failures
    assert not result.rebuilt and result.rebuild_from_user_alone == ["User Keyway in Gear_m1.5_N17.SLDPRT"]
    (keyway,) = result.user_features_in_error
    assert (keyway.name, keyway.code) == ("User Keyway", 71)
    assert result.user_feature_was_in_error(keyway) is False
    assert result.values_under(keyway) == [swbuild.ValueSet(P17, "Face Width", "10", "12", "Gears!I2")]
    assert [(f.name, f.code) for f in result.user_work.features] == [("User Keyway", 0)]
    assert "CHECK   your User Keyway in Gear_m1.5_N17.SLDPRT is in error after the rebuild, which set Face Width " \
           "10 -> 12 (Gears!I2)" in result.log_lines()
    # The review's condition 3: G1's and G3's components read in error from the keyway in their part, and that
    # code is not laid to the app.
    fake.open_document(T_ASM)
    assert {c.name: c.code for c in fake.components()}["gear1-1"] == 1


def test_a_users_feature_already_in_error_in_an_app_part_is_said_as_before_and_still():
    fake = _built_train()
    fake.user_feature(P17, "User Keyway", code=71)
    result = _update_train(fake, parts=_every_t_part())
    assert result.ok, result.failures
    (keyway,) = result.user_features_in_error
    assert result.user_feature_was_in_error(keyway) is True
    assert result.rebuild_from_user_alone == ["User Keyway in Gear_m1.5_N17.SLDPRT"]
    assert "CHECK   your User Keyway in Gear_m1.5_N17.SLDPRT was in error before this Update, and still is" \
        in result.log_lines()


def test_the_same_with_an_app_feature_in_error_in_another_part_stays_a_failure_naming_the_users_before():
    """An app feature in error, read in the check phase in a part this Update leaves alone: something of the app's
    is in error, so the False rebuild is the failure it was, its sentence naming what of the user's was in error."""
    fake = _built_train()
    _sprocket_part_in_error(fake)
    fake.user_feature(P17, "User Keyway")
    fake.breaks_on_set[_key(P17)] = [("User Keyway", 71)]
    app51 = swbuild.plan_features(plan(S51, path=P51))[-1]
    fake.feature_codes[(_key(P51), app51)] = 1
    result = _update_train(fake, parts=_every_t_part())
    assert ("T.SLDASM", "SolidWorks reported an error rebuilding T. Your Sprocket-1 was already in error before this "
                        "Update.") in result.failures
    assert result.rebuild_from_user_alone == []
    # The close review's must-fix 2: the failed result still says what B names of the user's newly broken feature.
    (keyway,) = result.user_features_in_error
    assert keyway.name == "User Keyway" and result.user_feature_was_in_error(keyway) is False
    assert [(v.name, v.was, v.now) for v in result.values_under(keyway)] == [("Face Width", "10", "12")]


# -- SolidWorks 2024, after the ruling on its What's Wrong box: it goes ahead as on 2026 ------------------------------


def test_on_2024_an_update_with_only_the_users_own_part_in_error_goes_ahead_as_on_2026():
    fake = _built_train()
    fake.revision = (32, 5, 0)
    _sprocket_part_in_error(fake)
    result = _update_train(fake, parts=_every_t_part())
    assert result.ok, result.failures
    assert not result.rebuilt and result.rebuild_from_user_alone == ["Sprocket-1"]


def test_on_2024_k3_goes_ahead_naming_the_keyway_newly_in_error_as_on_2026():
    fake = _built_train()
    fake.revision = (32, 5, 0)
    fake.user_feature(P17, "User Keyway")
    fake.breaks_on_set[_key(P17)] = [("User Keyway", 71)]
    result = _update_train(fake, parts=_every_t_part(_p17_update(cells=(("Face Width", "Gears!I2"),))))
    assert result.ok, result.failures
    assert result.rebuild_from_user_alone == ["User Keyway in Gear_m1.5_N17.SLDPRT"]
    (keyway,) = result.user_features_in_error
    assert result.user_feature_was_in_error(keyway) is False
    assert result.values_under(keyway) == [swbuild.ValueSet(P17, "Face Width", "10", "12", "Gears!I2")]


@pytest.mark.parametrize("value", [None, True])
def test_on_2024_with_the_box_not_known_not_to_block_the_failure_stands(monkeypatch, value):
    monkeypatch.setattr(findings, "WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2024", value)
    fake = _built_train()
    fake.revision = (32, 5, 0)
    fake.user_feature(P17, "User Keyway")
    fake.breaks_on_set[_key(P17)] = [("User Keyway", 71)]
    result = _update_train(fake, parts=_every_t_part())
    assert ("T.SLDASM", "SolidWorks reported an error rebuilding T.") in result.failures
    assert result.rebuild_from_user_alone == [] and [f.name for f in result.user_features_in_error] == ["User Keyway"]


def test_on_2024_with_modes_the_users_part_in_error_is_laid_to_them_as_on_2026(tc_built):
    fake, built = tc_built
    fake.revision = (32, 5, 0)
    fake.user_component(TC_ASM, "Sprocket-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 400.0)))
    fake.feature_codes[(_key(SPROCKET), "User Keyway")] = 71
    done = _tc_update_parts(fake, built, wanted_turn=6.0)
    assert done.ok, done.log_lines()
    assert done.rebuild_from_user_alone == ["Sprocket-1"]


def test_on_2024_with_modes_and_the_box_not_known_not_to_block_the_failure_stands(tc_built, monkeypatch):
    monkeypatch.setattr(findings, "WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2024", None)
    fake, built = tc_built
    fake.revision = (32, 5, 0)
    fake.user_component(TC_ASM, "Sprocket-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 400.0)))
    fake.feature_codes[(_key(SPROCKET), "User Keyway")] = 71
    done = _tc_update_parts(fake, built, wanted_turn=6.0)
    assert any(why.startswith("SolidWorks reported an error rebuilding TransferCase in ") and
               why.endswith(". Your Sprocket-1 was already in error before this Update.") for _, why in done.failures)


def test_a_false_rebuild_with_nothing_of_the_users_in_error_stays_a_failure():
    """The review's condition 1: the assembly's rebuild returns False and nothing at all reads in error."""
    fake = _built_train()
    fake.failed_documents = {_key(P51)}
    result = _update_train(fake, parts=_every_t_part())
    assert ("T.SLDASM", "SolidWorks reported an error rebuilding T.") in result.failures
    assert result.rebuild_from_user_alone == []


def test_an_app_feature_that_cannot_be_read_counts_as_in_error():
    """The review's condition 2: an app feature whose error code is unread, in a part read whole."""
    fake = _built_train()
    _sprocket_part_in_error(fake)
    fake.feature_codes[(_key(P51), swbuild.plan_features(plan(S51, path=P51))[-1])] = swcom.UNREAD
    result = _update_train(fake, parts=_every_t_part())
    assert any(why.startswith("SolidWorks reported an error rebuilding T.") for _, why in result.failures)
    assert result.rebuild_from_user_alone == []


def test_a_press_that_would_carry_a_component_in_error_refuses_before_any_write():
    """Not measured (the run's review, finding 1): putting by route (c1) a component of the user's that reads in
    error, its own part holding a feature in error. Refused with the other component problems, nothing written."""
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.feature_codes[(_key(SPROCKET), "User Keyway")] = 71
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (problem,) = raised.value.problems
    assert problem.kind == swbuild.PROBLEM_COMPONENT and problem.mates == ("UserLock1",)
    assert problem.sentence == (
        "Update SolidWorks would put your Sprocket-1 with G1, which your UserLock1 holds it to, and Sprocket-1 is in "
        "error in T.SLDASM; putting a component of yours that is in error with its gear has not been measured, so "
        "nothing is changed; in SolidWorks, put right what is in error in Sprocket-1, or suppress UserLock1, and press "
        "Update SolidWorks again.")
    assert _no_changes(fake) and fake.user_puts == []


def test_a_press_that_would_carry_a_component_whose_error_code_is_unread_refuses_before_any_write():
    """The close review's finding 5: unread counts as in error, as in the rebuild's rule."""
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.component_codes["Sprocket-1"] = swcom.UNREAD
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (problem,) = raised.value.problems
    assert problem.kind == swbuild.PROBLEM_COMPONENT and problem.mates == ("UserLock1",)
    assert problem.sentence == (
        "Update SolidWorks would put your Sprocket-1 with G1, which your UserLock1 holds it to, and SolidWorks would "
        "not say whether Sprocket-1 is in error in T.SLDASM; putting a component of yours that may be in error with "
        "its gear has not been measured, so nothing is changed; in SolidWorks, suppress UserLock1, and press Update "
        "SolidWorks again.")
    assert _no_changes(fake) and fake.user_puts == []


def test_a_failed_update_without_modes_still_carries_the_users_feature_newly_in_error_and_the_value_under_it(
        monkeypatch):
    """The close review's must-fix 2, the worker's half: k3 on a version whose findings are None (2024 until the box
    ruling) stays a failure, and its result still holds what package B names — the keyway newly in error, and what
    was set under it."""
    monkeypatch.setattr(findings, "WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2026", None, raising=False)
    fake = _built_train()
    fake.user_feature(P17, "User Keyway")
    fake.breaks_on_set[_key(P17)] = [("User Keyway", 71)]
    result = _update_train(fake, parts=_every_t_part(_p17_update(cells=(("Face Width", "Gears!I2"),))))
    assert ("T.SLDASM", "SolidWorks reported an error rebuilding T.") in result.failures
    (keyway,) = result.user_features_in_error
    assert (keyway.name, keyway.code) == ("User Keyway", 71)
    assert result.user_feature_was_in_error(keyway) is False
    assert result.values_under(keyway) == [swbuild.ValueSet(P17, "Face Width", "10", "12", "Gears!I2")]
    assert result.rebuild_from_user_alone == []


def test_a_failed_update_with_modes_still_carries_the_users_feature_newly_in_error_and_the_value_under_it(
        tc_built, monkeypatch):
    """The same on the path with modes: the TransferCase's Sleeve part set (Face Width 10 -> 12), the user's keyway in
    it rebuilt into error, the finding unset, so the first rebuild in the active mode stops the Update."""
    monkeypatch.setattr(findings, "WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2026", None, raising=False)
    fake, built = tc_built
    fake.user_feature(TC_SLEEVE, "User Keyway")
    fake.breaks_on_set[_key(TC_SLEEVE)] = [("User Keyway", 71)]
    motion, placements = _tc_motion(built, "2H")
    sleeve = swbuild.DocumentValues(TC_SLEEVE, _values(GearSpec().with_values(face_width="12")),
                                    made=swbuild.plan_features(plan(path=TC_SLEEVE)),
                                    cells=(("Face Width", "Gears!I4"),))
    result = swbuild.update_gearbox(fake, parts=[sleeve, _still(GearSpec(), TC_DOG)], assembly=TC_ASM,
                                    placements=placements, motion=motion, exists=fake.exists, mtime=lambda _p: 0.0)
    assert any(why.startswith("SolidWorks reported an error rebuilding TransferCase in ") for _, why in result.failures)
    (keyway,) = result.user_features_in_error
    assert result.user_feature_was_in_error(keyway) is False
    assert result.values_under(keyway) == [swbuild.ValueSet(TC_SLEEVE, "Face Width", "10", "12", "Gears!I4")]


def test_an_app_component_in_error_whose_part_was_not_read_stays_a_failure():
    fake = _built_train()
    fake.user_feature(P17, "User Keyway")
    fake.breaks_on_set[_key(P17)] = [("User Keyway", 71)]
    fake.feature_codes[(_key(P51), "Extrude9")] = 1                      # G4's part, not read by this press
    result = _update_train(fake, parts=[_p17_update()])
    assert ("T.SLDASM", "SolidWorks reported an error rebuilding T.") in result.failures
    assert result.rebuild_from_user_alone == []


def test_an_app_mate_in_error_after_the_rebuild_keeps_it_a_failure():
    fake = _built_train()
    _sprocket_part_in_error(fake)
    fake.mate_codes["G1 meshes G2"] = (47, False)
    result = _update_train(fake, parts=_every_t_part())
    assert any(why.startswith("SolidWorks reported an error rebuilding T.") for _, why in result.failures)
    assert result.rebuild_from_user_alone == []


def test_errors_that_cannot_be_read_keep_it_a_failure():
    fake = _built_train()
    _sprocket_part_in_error(fake)
    fake.component_codes["Sprocket-1"] = swcom.UNREAD
    result = _update_train(fake, parts=_every_t_part())
    assert any(why.startswith("SolidWorks reported an error rebuilding T.") for _, why in result.failures)


@pytest.mark.parametrize("name, value", [("ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2026", None),
                                         ("WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2026", None),
                                         ("WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2026", True)])
def test_on_a_version_whose_finding_is_none_a_failed_assembly_rebuild_stays_todays_failure(monkeypatch, name, value):
    """Re-pinned at the ruling on 2024's box: the gate's What's Wrong finding is now whether the box blocks; unset or
    True, the failure stands."""
    monkeypatch.setattr(findings, name, value, raising=False)
    fake = _built_train()
    _sprocket_part_in_error(fake)
    result = _update_train(fake, parts=_every_t_part())
    assert ("T.SLDASM", "SolidWorks reported an error rebuilding T. Your Sprocket-1 was already in error before this "
                        "Update.") in result.failures
    assert result.rebuild_from_user_alone == []


def test_a_user_mate_in_error_alone_does_not_make_a_failure():
    """m3's first half on the fake: the user's mate in error before the press, the assembly's rebuild True (as on
    2026): the Update goes on and lists the mate as the user's."""
    fake = _built_train()
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_component(T_ASM, "Chain-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 60.0)))
    fake.user_mate(T_ASM, "UserGap", kind="distance", a=("Chain-1", "plane1"), b=("Housing-1", "plane1"))
    fake.mate_codes["UserGap"] = (47, False)
    result = _update_train(fake, parts=_every_t_part())
    assert result.ok, result.failures
    assert result.rebuilt and result.rebuild_from_user_alone == []
    assert result.user_in_error == [("", "UserGap")] and result.user_work.in_error == ["UserGap"]


def test_a_false_rebuild_with_only_a_user_mate_in_error_is_not_laid_to_it_on_2026():
    """On 2026 a mate in error alone leaves the rebuild True
    (findings.ASSEMBLY_REBUILD_WITH_USER_MATE_IN_ERROR_ON_2026), so a False with nothing but a user mate in error is
    unexplained, and stays a failure."""
    fake = _built_train()
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_component(T_ASM, "Chain-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 60.0)))
    fake.user_mate(T_ASM, "UserGap", kind="distance", a=("Chain-1", "plane1"), b=("Housing-1", "plane1"))
    fake.mate_codes["UserGap"] = (47, False)
    fake.failed_documents = {_key(P51)}            # the assembly's rebuild False, with no component read in error
    result = _update_train(fake, parts=_every_t_part())
    assert ("T.SLDASM", "SolidWorks reported an error rebuilding T. Your UserGap was already in error before this "
                        "Update.") in result.failures
    assert result.rebuild_from_user_alone == []


def test_with_modes_the_users_part_in_error_is_laid_to_them_in_every_mode_shown(tc_built):
    """m3's second half on the fake, with modes: every mode's rebuild returns False from the user's part alone."""
    fake, built = tc_built
    fake.user_component(TC_ASM, "Sprocket-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 400.0)))
    fake.feature_codes[(_key(SPROCKET), "User Keyway")] = 71
    done = _tc_update_parts(fake, built, wanted_turn=6.0)
    assert done.ok, done.log_lines()
    assert done.rebuild_from_user_alone == ["Sprocket-1"]
    assert {mode for mode, name in done.user_in_error if name == "Sprocket-1"} == set(TC_MODES)


def test_with_modes_and_the_finding_unset_the_failure_names_the_mode_and_the_users_part(tc_built, monkeypatch):
    monkeypatch.setattr(findings, "WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2026", None, raising=False)
    fake, built = tc_built
    fake.user_component(TC_ASM, "Sprocket-1", SPROCKET, (IDENTITY9, (0.0, 0.0, 400.0)))
    fake.feature_codes[(_key(SPROCKET), "User Keyway")] = 71
    done = _tc_update_parts(fake, built, wanted_turn=6.0)
    assert any(why.startswith("SolidWorks reported an error rebuilding TransferCase in ") and
               why.endswith(". Your Sprocket-1 was already in error before this Update.") for _, why in done.failures)


def test_a_feature_before_the_apps_first_is_the_templates_and_nobodys():
    states = [swcom.FeatureState("Front Plane"), swcom.FeatureState("Origin"), swcom.FeatureState("Sketch1"),
              swcom.FeatureState("Extrude1"), swcom.FeatureState("Keyway", "ICE", 71, False),
              swcom.FeatureState("Fillet9")]
    found = swbuild._user_features(P17, states, {"Sketch1", "Extrude1"})
    assert [(f.name, f.code) for f in found] == [("Keyway", 71), ("Fillet9", 0)]


def test_plan_features_are_every_feature_the_plan_keeps_by_name():
    made = swbuild.plan_features(plan(S17, path=P17))
    fake = _built_train()
    fake.open_document(P17)
    assert set(made) == set(fake.made) and len(made) == len(set(made))


def test_the_carry_is_the_gears_own_rigid_motion():
    before_gear = (_rot_z(30.0), (10.0, 0.0, 5.0))
    target = (_rot_z(-15.0), (12.0, 1.0, 5.0))
    user = (_rot_z(80.0), (14.0, 3.0, 40.0))
    carried = swbuild._carry_frame(before_gear, target, user)
    want = _compose(target, _compose(_inverse(before_gear), user))
    assert max(_frame_off(carried, want)) < 1e-12


# -- a gearbox with modes ----------------------------------------------------------------------------------------------


def _tc_sprocket(fake, flags=None, z_off=150.0):
    """The user's sprocket locked to RangeSlv (gear7-1), which slides by mode, standing ``z_off`` in front of it in
    every configuration."""
    sleeve = fake.frames["gear7-1"]
    fake.user_component(TC_ASM, "Sprocket-2", SPROCKET, (IDENTITY9, (0.0, 0.0, sleeve[1][2] + z_off)))
    for frames in fake.frames_by.values():
        if "gear7-1" in frames:
            frames["Sprocket-2"] = (IDENTITY9, (0.0, 0.0, frames["gear7-1"][1][2] + z_off))
    return fake.user_lock(TC_ASM, "UserLock2", "gear7-1", "Sprocket-2", flags=flags)


def test_with_modes_a_sprocket_locked_to_the_slider_goes_with_it_in_every_mode_put(tc_built):
    fake, built = tc_built
    _tc_sprocket(fake)
    done = _tc_update(fake, built, wanted_turn=6.0)
    assert done.ok, done.log_lines()
    assert [(c, g) for c, g, _ in done.carried] == [("Sprocket-2", "RangeSlv")] * 4
    assert [m for _, _, m in done.carried] == ["4H", "N", "4L", "2H"]
    assert [m for _, _, m in fake.user_puts] == ["4H", "N", "4L", "2H"]
    for mode in ("2H", "4H", "N", "4L"):
        fake.show_configuration(mode)
        rel = _relative(fake, "gear7-1", "Sprocket-2")
        assert _close(rel, (IDENTITY9, (0.0, 0.0, 150.0)), 1e-9), (mode, rel)
    assert all(not f for f in fake.mate("UserLock2", TC_ASM).flags.values())


def test_with_modes_a_user_lock_on_in_some_modes_only_refuses_before_anything_is_shown(tc_built):
    fake, built = tc_built
    _tc_sprocket(fake, flags={"2H": False, "4H": False, "N": True, "4L": True})
    with pytest.raises(UserWorkRefused) as raised:
        _tc_update(fake, built, wanted_turn=6.0)
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_LOCK_BY_MODE and problem.mates == ("UserLock2",)
    assert problem.sentence == ("Your lock UserLock2 is on in 2H and 4H and suppressed in N and 4L, and putting a "
                                "component of yours with its gear has been settled only for a lock that is on in every "
                                "mode, so nothing is changed; turn UserLock2 on in every mode, or suppress it in every "
                                "mode, in SolidWorks and press Update SolidWorks again.")
    assert _no_changes(fake) and fake.config == "2H"


def test_with_modes_a_tie_on_only_in_another_mode_stops_the_job_when_that_mode_is_shown_before_its_put(tc_built):
    """Case C′ (S0's C2): the tie is suppressed in the mode showing, so the check reads the train free; 4L, where the
    tie is on, is read when shown and before its put, and the job stops there, what was changed said."""
    fake, built = tc_built
    _tc_sprocket(fake)
    fake.user_component(TC_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, 400.0)), fixed=True)
    tie = fake.user_mate(TC_ASM, "UserTie", kind="coincident", a=("Sprocket-2", "plane2"),
                         b=("Housing-1", "plane2"))
    tie.flags = {"2H": True, "4H": True, "N": True, "4L": False}
    tie.suppressed = True
    fake.locks["UserTie"] = ["gear7-1", "gear8-1", "gear2-1", "gear6-1", "gear9-1"]
    done = _tc_update(fake, built, wanted_turn=6.0)
    assert not done.ok
    (failure,) = done.failures
    assert failure[1].startswith("In mode 4L, Update SolidWorks must turn ")
    assert "SolidWorks reads it as unable to turn with your mates on it, so nothing is changed; suppress UserLock2 " \
           "and UserTie in 4L and press Update SolidWorks again." in failure[1]
    assert failure[1].count("UserTie") == 1
    assert "4L" not in done.put_in and "4H" in done.put_in and fake.config == "2H"
    assert TC_ASM in done.changed


def test_with_modes_a_tie_on_in_the_mode_showing_refuses_before_anything_is_shown(tc_built):
    fake, built = tc_built
    _tc_sprocket(fake)
    fake.user_component(TC_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, 400.0)), fixed=True)
    fake.user_mate(TC_ASM, "UserTie", kind="coincident", a=("Sprocket-2", "plane2"), b=("Housing-1", "plane2"))
    fake.locks["UserTie"] = ["gear7-1", "gear8-1"]
    with pytest.raises(UserWorkRefused) as raised:
        _tc_update(fake, built, wanted_turn=6.0)
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_TIE and problem.mates == ("UserLock2", "UserTie")
    assert "suppress UserLock2 and UserTie in 2H, 4H, N and 4L" in problem.sentence
    assert _no_changes(fake)


def test_with_modes_a_slide_value_the_user_changed_refuses_when_the_record_holds(tc_built):
    fake, built = tc_built
    fake.mate("RangeSlv along Rear", TC_ASM).own["4H"] = 50.0
    with pytest.raises(UserWorkRefused) as raised:
        _tc_update(fake, built, record_holds=True, cells=(("RangeSlv along Rear", "Gears!T7"),))
    assert str(raised.value) == (
        "RangeSlv along Rear in TransferCase in 4H is 50 mm in SolidWorks, where Gear Generator set it to 46 mm and "
        "the workbook now asks 46 mm: set it back to 46 mm in SolidWorks, or change Gears!T7 so the workbook asks 50 "
        "mm, and press Update SolidWorks again.")
    assert _no_changes(fake)
    assert _tc_update(fake, built).values_restored == [("RangeSlv along Rear", "4H")]     # W8's, without the record


def test_with_modes_a_recorded_flag_the_user_changed_refuses_when_the_record_holds(tc_built):
    fake, built = tc_built
    fake.mate("ModeSlv engages FrontDog", TC_ASM).flags["4H"] = True
    with pytest.raises(UserWorkRefused) as raised:
        _tc_update(fake, built, record_holds=True)
    (problem,) = raised.value.problems
    assert problem.values == (swbuild.ValueEdit("TransferCase.SLDASM", "ModeSlv engages FrontDog", "suppressed", "on",
                                                "on", mode="4H"),)
    assert problem.sentence == ("The mate ModeSlv engages FrontDog is suppressed in 4H in SolidWorks, where Gear "
                                "Generator made it on and the workbook has it on: in SolidWorks, turn it back on in 4H "
                                "and press Update SolidWorks again.")
    assert _no_changes(fake)


def test_with_modes_a_quiet_press_reads_the_users_work_and_refuses_nothing(tc_built):
    fake, built = tc_built
    _tc_sprocket(fake)
    fake.user_mate(TC_ASM, "Angle1")                       # on a sleeve's plane: nothing is put, so no matter
    done = _tc_update(fake, built)
    assert done.ok and done.put_in == [] and fake.user_puts == []
    assert [m.name for m in done.user_work.mates] == ["UserLock2", "Angle1"]
    assert done.user_work.mates[0].on == ("2H", "4H", "N", "4L")


# -- the fake's own guard: no write to the user's work but route (c1)'s puts --------------------------------------------


def test_the_fake_fails_a_test_on_any_write_to_the_users_work_but_a_put():
    fake = _built_train()
    fake.open_document(T_ASM)
    _sprocket_on_g1(fake)
    fake.find_component("user1", "Sprocket-1")
    fake.find_mate("other1", "UserLock1")
    fake.user_mate(T_ASM, "Gear5", kind="gear", a=("Sprocket-1", "Gear Axis"), b=("gear2-1", "Gear Axis"))
    fake.user_mate(T_ASM, "Distance9", kind="distance", a=("Sprocket-1", "plane1"), b=("layout-1", "plane1"))
    fake.find_mate("other2", "Gear5")
    fake.find_mate("other3", "Distance9")
    for call in (lambda: fake.fix_component("user1"), lambda: fake.unfix_component("user1"),
                 lambda: fake.set_mate_suppressed("other1", True),
                 lambda: fake.set_mate_suppressed_in("other1", True, ["Default"]),
                 lambda: fake.set_dimension_in("other3", 12.0, ["Default"]),
                 lambda: fake.set_gear_ratio("other2", "user1:Gear Axis", "gear2:Gear Axis", (20, 68)),
                 lambda: fake.remake_gear_mate("other2", "user1:Gear Axis", "gear2:Gear Axis", (20, 68), True)):
        with pytest.raises(AssertionError, match=r"of the user's \(W9a §0.3\)"):
            call()
    with pytest.raises(AssertionError, match=r"route \(c1\) only"):                # no gear put with it
        fake.place_component("user1", IDENTITY9, (0.0, 0.0, 31.0), kind=swcom.ASSEMBLY_TRAIN)
    fake.find_component("placed1", "gear1-1")
    fake.place_component("placed1", *fake.frames["gear1-1"], kind=swcom.ASSEMBLY_TRAIN)
    fake.place_component("user1", IDENTITY9, (0.0, 0.0, 31.0), kind=swcom.ASSEMBLY_TRAIN)
    assert [n for n, _, _ in fake.user_puts] == ["Sprocket-1"]
    fake.find_component("placed2", "gear2-1")
    fake.mate("UserLock1", T_ASM).suppressed = True                            # the lock off: no longer with G1
    with pytest.raises(AssertionError, match=r"route \(c1\) only"):
        fake.place_component("user1", IDENTITY9, (0.0, 0.0, 32.0), kind=swcom.ASSEMBLY_TRAIN)


def test_a_carrier_or_layout_global_is_judged_as_a_parts_is():
    doc = swbuild.DocumentValues(W + "P_C_Carrier.SLDPRT", (GlobalVariable("P X", "26.25"),),
                                 recorded=(("P X", "26.25"),))
    assert swbuild._value_edits(doc, [('"P X"= 30', 30.0)], {"P X": 30.0}) == [
        swbuild.ValueEdit("P_C_Carrier.SLDPRT", "P X", "30", "26.25", "26.25")]
    assert swbuild._value_edits(doc, [('"P X"= 26.25', 26.25)], {"P X": 26.25}) == []
    assert swbuild._value_edits(replace(doc, recorded=None), [('"P X"= 30', 30.0)], {"P X": 30.0}) == []


def test_two_sprockets_locked_to_one_fixed_housing_are_two_ties_not_one_two_body_cluster():
    fake = _built_train()
    _sprocket_on_g1(fake, axis="")
    fake.user_component(T_ASM, "Sprocket-4", SPROCKET, (IDENTITY9, (64.5, 51.0, 60.0)))
    fake.user_lock(T_ASM, "UserLock4", "gear4-1", "Sprocket-4")
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, 90.0)), fixed=True)
    fake.user_lock(T_ASM, "UserLockA", "Sprocket-1", "Housing-1")
    fake.user_lock(T_ASM, "UserLockB", "Sprocket-4", "Housing-1")
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert [(p.kind, p.mates) for p in raised.value.problems] == [(PROBLEM_TIE, ("UserLock1", "UserLockA")),
                                                                  (PROBLEM_TIE, ("UserLock4", "UserLockB"))]


# -- the fix round of W9a package A's review (W9A-REVIEW-A.md; the coordinator's rulings) -----------------------------

from test_swbuild import _planetary_turned_and_pressed, turned_findings  # noqa: E402,F401


def _planetary(monkeypatch):
    sw, pressed, names = _planetary_turned_and_pressed(monkeypatch, "gear mates off around the puts")
    return sw, pressed, names, pressed.assembly


def _press(sw, pressed):
    return swbuild.update_gearbox(sw, **pressed.update_kwargs(), exists=lambda _p: True, mtime=lambda _p: 5.0)


@pytest.mark.parametrize("kind", ["lock", "coincident"])
def test_a_housing_on_a_planetarys_held_ring_nothing_puts_never_refuses(turned_findings, monkeypatch, kind):
    """Review point 1 (ruling 1): the Ring is held and stands where it belongs, so the press does not put it, and
    the user's housing locked or mated to it is no tie and no other kind on a put gear."""
    sw, pressed, names, asm = _planetary(monkeypatch)
    sw.user_component(asm, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -30.0)), fixed=True)
    if kind == "lock":
        sw.user_lock(asm, "Lock9", names["Ring"], "Housing-1")
    else:
        sw.user_mate(asm, "Concentric9", kind="coincident", a=("Housing-1", "Gear Axis"), b=(names["Ring"], "Gear Axis"))
    result = _press(sw, pressed)
    assert result.ok, result.failures
    assert "Ring" not in result.placed and sw.user_puts == []


def _ring_off_its_frame(sw, names):
    sw.frames[names["Ring"]] = _turn_about_z(sw.frames[names["Ring"]], 1.0)       # not a whole pitch


def test_a_held_gear_update_re_places_carries_the_users_locked_component_only_once_measured(turned_findings,
                                                                                            monkeypatch):
    sw, pressed, names, asm = _planetary(monkeypatch)
    _ring_off_its_frame(sw, names)
    sw.user_component(asm, "Sprocket-9", SPROCKET, (IDENTITY9, (0.0, 0.0, -40.0)))
    sw.user_lock(asm, "Lock9", names["Ring"], "Sprocket-9")
    with pytest.raises(UserWorkRefused) as raised:
        _press(sw, pressed)
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_UNSETTLED and problem.mates == ("Lock9",)
    assert problem.sentence == (
        "Update SolidWorks would put your Sprocket-9 with Ring, which your Lock9 holds to it, and putting a component "
        "of yours with a gear held still and put back first has not been measured on this SolidWorks "
        "(findings.USER_MATE_PUT_HELD_GEAR_ON_2026 is None), so nothing is changed; suppress Lock9 in SolidWorks and "
        "press Update SolidWorks again.")
    assert _no_changes(sw)
    monkeypatch.setattr(findings, "USER_MATE_PUT_HELD_GEAR_ON_2026", True)
    rel = _relative(sw, names["Ring"], "Sprocket-9")
    result = _press(sw, pressed)
    assert result.ok, result.failures
    assert ("Sprocket-9", "Ring", "") in result.carried and "Ring" in result.placed
    assert _close(_relative(sw, names["Ring"], "Sprocket-9"), rel, 1e-9)


def test_a_lock_chain_from_a_held_gear_update_re_places_to_the_ground_refuses_without_a_read(turned_findings,
                                                                                             monkeypatch):
    sw, pressed, names, asm = _planetary(monkeypatch)
    _ring_off_its_frame(sw, names)
    sw.user_component(asm, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -30.0)), fixed=True)
    sw.user_lock(asm, "Lock9", names["Ring"], "Housing-1")
    with pytest.raises(UserWorkRefused) as raised:
        _press(sw, pressed)
    assert str(raised.value) == ("Your Lock9 holds Ring to Housing-1, which does not move, and Update SolidWorks must "
                                 "put Ring back, so nothing is changed; suppress Lock9 in SolidWorks and press Update "
                                 "SolidWorks again.")


def test_a_fixed_gear_update_re_places_w4s_way_carries_the_users_component_only_once_measured(monkeypatch):
    fake = _built_train()
    _sprocket_on_g1(fake, axis="")
    for body in ("gear1-1", "Sprocket-1"):
        fake.frames[body] = _turn_about_z(fake.frames[body], 10.0)
    rel = _relative(fake, "gear1-1", "Sprocket-1")
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, motion=_motion(fixed=("G1",)))
    assert "putting a component of yours with a fixed gear, unfixed, put and fixed again has not been measured" in \
        str(raised.value) and "(findings.USER_MATE_PUT_FIXED_GEAR_ON_2026 is None)" in str(raised.value)
    assert _no_changes(fake)
    monkeypatch.setattr(findings, "USER_MATE_PUT_FIXED_GEAR_ON_2026", True)
    result = _update_train(fake, motion=_motion(fixed=("G1",)))
    assert result.ok, result.failures
    assert result.carried == [("Sprocket-1", "G1", "")] and "G1" in result.placed
    assert _close(_relative(fake, "gear1-1", "Sprocket-1"), rel, 1e-9)


def test_a_train_with_no_carrier_carries_the_users_component_only_once_measured(monkeypatch):
    for year in (2026, 2024):
        monkeypatch.setattr(findings, f"USER_MATE_PUT_NO_CARRIER_ON_{year}", None)
    fake = _built_train()
    _sprocket_on_g1(fake)
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert str(raised.value) == (
        "Update SolidWorks would put your Sprocket-1 with G1, which your UserLock1 holds to it, and putting a "
        "component of yours with a gear on a train with no carrier, its gear mates left on around the put has not been "
        "measured on this SolidWorks (findings.USER_MATE_PUT_NO_CARRIER_ON_2026 is None), so nothing is changed; "
        "suppress UserLock1 in SolidWorks and press Update SolidWorks again.")
    fake.revision = (32, 5, 0)
    monkeypatch.setattr(findings, "USER_MATE_PUT_NO_CARRIER_ON_2026", True)      # measured on 2026 only: 2024 refuses
    with pytest.raises(UserWorkRefused, match=r"USER_MATE_PUT_NO_CARRIER_ON_2024 is None"):
        _moving(fake)


def test_a_train_with_no_carrier_on_a_gearbox_with_modes_is_its_own_branch_unmeasured_as_committed(tc_built,
                                                                                                    monkeypatch):
    """The demonstration measured NO_CARRIER on a gearbox with no modes (the 12 : 1) only: with modes, the committed
    NO_CARRIER_MODES (None on both versions) refuses a carry, whatever NO_CARRIER says."""
    fake, built = tc_built
    for year in (2026, 2024):
        monkeypatch.setattr(findings, f"USER_MATE_PUT_NO_CARRIER_MODES_ON_{year}", None)
    assert findings.USER_MATE_PUT_NO_CARRIER_ON_2026 is True
    _tc_sprocket(fake)
    with pytest.raises(UserWorkRefused) as raised:
        _tc_update(fake, built, wanted_turn=6.0)
    assert "with a gear on a train with no carrier, in each mode of a gearbox with modes, its gear mates left on " \
           "around the put has not been measured on this SolidWorks (findings.USER_MATE_PUT_NO_CARRIER_MODES_ON_2026 " \
           "is None)" in str(raised.value)
    motion, placements = _tc_motion(built)
    assert swbuild.user_carry_branches(motion, placements)["InDog"] == swbuild.BRANCH_NO_CARRIER_MODES


def test_a_user_sub_assembly_is_carried_only_once_measured_its_leaf_naming_its_top_level(monkeypatch):
    fake = _built_train()
    fake.user_component(T_ASM, "Sub-1", W + "Drive.SLDASM", (IDENTITY9, (0.0, 0.0, 30.0)))
    fake.user_lock(T_ASM, "UserLock1", "gear1-1", "Sub-1/Sprocket-1")
    with pytest.raises(UserWorkRefused, match=r"putting a sub-assembly of yours with a gear when the component is a "
                                              r"sub-assembly has not been measured"):
        _moving(fake)
    monkeypatch.setattr(findings, "USER_MATE_PUT_SUBASSEMBLY_ON_2026", True)
    result = _moving(fake)
    assert result.ok and result.carried == [("Sub-1", "G1", "")]
    assert result.user_work.mates[0].touches == (("app", "G1"), ("user", "Sub-1"))


@pytest.mark.parametrize("unread", ["type", "count", "entity"])
def test_a_user_mate_solidworks_will_not_describe_refuses_whenever_anything_is_put(unread):
    """Review point 2 (ruling 2): never judged harmless, never read as the assembly's own plane."""
    fake = _built_train()
    _sprocket_on_g1(fake, axis="")
    fake.unread_mates = {"UserLock1": unread}
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (problem,) = raised.value.problems
    assert problem.kind == swbuild.PROBLEM_UNREAD and problem.mates == ("UserLock1",)
    assert problem.sentence == (
        "SolidWorks would not say what UserLock1 in T.SLDASM holds, a mate Gear Generator did not make, so Update "
        "SolidWorks cannot tell whether putting the gears back would leave something of yours behind, and nothing is "
        "changed; suppress UserLock1 in SolidWorks and press Update SolidWorks again.")
    mate = raised.value.user_work.mates[0]
    assert not mate.whole and ("assembly", "") not in mate.touches
    assert _no_changes(fake)
    assert _update_train(fake).ok                         # a quiet press puts nothing: nothing to judge it against


@pytest.mark.parametrize("kind", ["rack and pinion", "screw"])
def test_a_motion_mate_on_a_component_route_c1_would_put_refuses_as_a_gear_mate_does(kind):
    fake = _built_train()
    _sprocket_on_g1(fake, axis="")
    fake.user_component(T_ASM, "Rack-1", SPROCKET, (IDENTITY9, (30.0, 0.0, 30.0)))
    fake.user_mate(T_ASM, "Motion7", kind=kind, a=("Sprocket-1", "Gear Axis"), b=("Rack-1", "plane1"))
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    assert [(p.kind, p.mates) for p in raised.value.problems] == [(PROBLEM_OTHER_KIND, ("Motion7",))]
    assert raised.value.user_work.mates[1].kind == swbuild.USER_GEAR


@pytest.mark.parametrize("state, said", [(0, "suppressed in T.SLDASM, so nothing is changed; in SolidWorks, "
                                             "unsuppress it"),
                                         (1, "loaded lightweight in T.SLDASM, so nothing is changed; in SolidWorks, "
                                             "set it to Resolved")])
def test_a_component_route_c1_would_put_that_is_suppressed_or_lightweight_refuses(state, said):
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.component_states = {"Sprocket-1": state}
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (problem,) = raised.value.problems
    assert problem.kind == swbuild.PROBLEM_COMPONENT
    assert problem.sentence == ("Update SolidWorks would put your Sprocket-1 with G1, which your mates hold it to, and "
                                f"Sprocket-1 is {said} and press Update SolidWorks again.")


def test_with_modes_a_user_lock_joining_two_trains_refuses_naming_it(tc_built):
    """The plan's two-train mate: LoDog and FrontDog are on two trains in 2H (neither engaged there)."""
    fake, built = tc_built
    fake.user_lock(TC_ASM, "Lock5", "gear6-1", "gear9-1")
    with pytest.raises(UserWorkRefused) as raised:
        _tc_update(fake, built, wanted_turn=6.0)
    assert [(p.kind, p.mates) for p in raised.value.problems] == [(PROBLEM_TWO_BODIES, ("Lock5",))]
    assert "holds FrontDog and LoDog together" in str(raised.value)


def test_a_put_the_check_did_not_judge_stops_the_job_before_it_where_the_users_work_is(monkeypatch):
    """Review point 7: what the change phase puts is bound to what the check judged; here the check is made to
    judge nothing put, and the change phase finds the train to put, with the user's lock on it."""
    fake = _built_train()
    _sprocket_on_g1(fake)
    monkeypatch.setattr(swbuild, "_may_put", lambda *args, **kwargs: set())
    result = _moving(fake)
    assert not result.ok and fake.user_puts == [] and "G1" not in result.placed
    assert any("which its check before any change found it would not put, and your work is on" in text
               for _, text in result.failures), result.failures


def test_a_carried_component_found_off_its_gear_after_the_rebuild_is_a_failure_said_as_the_users():
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.slips = {"Sprocket-1"}                          # turned 5° on every later rebuild: the put does not hold
    result = _moving(fake)
    assert ("T.SLDASM", "Your Sprocket-1 did not stay with G1 where Update SolidWorks put it: once the assembly "
                        "rebuilt it stood elsewhere against G1.") in result.failures


def test_a_marked_part_open_and_modified_since_the_update_is_vouched_for_and_one_loaded_from_its_file_is_not():
    """Ruling 3: an Update left the part unsaved (the record's mark); while it stays open, modified, the record's word
    holds and the user's edit refuses; closed and loaded from its file, the Update is lost and W8's set-back stands."""
    fake = _built_train()
    key = _key(P17)
    fake.memory[key] = (list(fake.memory[key][0]), fake.memory[key][1])
    for i, text in enumerate(fake.memory[key][0]):
        if split_equation(text)[0] == "Face Width":
            fake.memory[key][0][i] = '"Face Width"= 14'
    doc = swbuild.DocumentValues(P17, _values(S17.with_values(face_width="12")), recorded=_recorded(S17),
                                 mark=swbuild.MARK_UNSAVED)
    with pytest.raises(UserWorkRefused, match="^Face Width in Gear_m1.5_N17 is 14 in SolidWorks"):
        _update_train(fake, parts=[doc])
    fake.saved[key] = (list(fake.memory[key][0]), list(fake.memory[key][1]))
    fake.open_docs = [d for d in fake.open_docs if _key(d.path) != key]
    done = _update_train(fake, parts=[doc])
    assert done.ok and done.parts[0].changed == ["Face Width"]
    assert _update_train(fake, parts=[replace(doc, mark=swbuild.MARK_MISMATCHED)]).ok


def test_k11_compares_a_radians_document_in_its_own_unit():
    variable = GlobalVariable("Base Diameter", '"Pitch Diameter" * cos ( 20 )', '"Pitch Diameter" * cos ( 0.349066 )')
    doc = swbuild.DocumentValues(P17, (variable,), recorded=(("Base Diameter", '"Pitch Diameter" * cos ( 0.349066 )'),))
    held = [('"Base Diameter"= "Pitch Diameter" * cos ( 0.349066 )', 23.9)]
    assert swbuild._value_edits(doc, held, {"Base Diameter": 23.9}) == []
    edited = [('"Base Diameter"= "Pitch Diameter" * cos ( 0.4 )', 23.4)]
    (edit,) = swbuild._value_edits(doc, edited, {"Base Diameter": 23.4})
    assert (edit.name, edit.live, edit.cell) == ("Base Diameter", "23.4", "")


def test_a_layout_renamed_in_solidworks_is_still_the_apps_by_its_part():
    fake = _built_train()
    fake.rename_component(T_ASM, "layout-1", "T_Layout-3")
    result = _update_train(fake, motion=_motion(layout_component="layout-1"),
                           layout=_train_layout_values())
    assert result.ok and result.user_work.components == []


def test_the_judgement_is_pure_and_predicts_what_a_press_would_carry_without_a_read():
    """Review point 5: package B says before the press what a press would put with its gears, from the inventory."""
    work = swbuild.UserWork(
        components=[swbuild.UserComponent("Sprocket-1", SPROCKET)],
        mates=[swbuild.UserMate("Lock3", swbuild.USER_LOCK, 16, (("app", "Sun"), ("user", "Sprocket-1")), ("",)),
               swbuild.UserMate("Axis3", swbuild.USER_OTHER, 0, (("user", "Sprocket-1"), ("layout", "")), ("",))])
    told = swbuild.judge_user_work(work, ("",), {"Sun", "Planet"}, trains=[("Sun", "Planet")], mated=("Sun", "Planet"),
                                   branches={})                      # every body on S0's measured branch
    assert told.problems == [] and told.carried == {"Sun": [("Sprocket-1", ("Lock3",))]}
    assert told.unread_ties == [(("Sun", "Planet"), ("Lock3", "Axis3"))] and told.on_train["Planet"] == ("Lock3", "Axis3")
    nothing = swbuild.judge_user_work(work, ("",), set())
    assert nothing.carried == {} and nothing.problems == []



# -- the re-check of the fix round (W9A-REVIEW-A.md, "The fix round, re-checked"; the coordinator's rulings) ----------


def _work_with(*mates, components=()):
    return swbuild.UserWork(components=list(components) or [swbuild.UserComponent("Sprocket-1", SPROCKET)],
                            mates=list(mates))


def test_the_judgement_given_no_branches_takes_nothing_as_measured():
    """N6: a caller that gives no ``branches`` is never told a carry goes through."""
    work = _work_with(swbuild.UserMate("Lock3", swbuild.USER_LOCK, 16, (("app", "Sun"), ("user", "Sprocket-1")),
                                       ("",)))
    told = swbuild.judge_user_work(work, ("",), {"Sun"})
    assert told.carried == {} and [(p.kind, p.mates) for p in told.problems] == [(PROBLEM_UNSETTLED, ("Lock3",))]
    assert "how Sun is put was not said to this judgement" in told.problems[0].sentence
    other = _work_with(swbuild.UserMate("Angle1", swbuild.USER_OTHER, 6, (("app", "Sun"), ("layout", "")), ("",)))
    (said,) = swbuild.judge_user_work(other, ("",), {"Sun"}).problems
    assert "lock your component to Sun instead" not in said.sentence                 # no lock promised either
    assert swbuild.judge_user_work(work, ("",), {"Sun"}, branches={}).carried == {"Sun": [("Sprocket-1", ("Lock3",))]}


@pytest.mark.parametrize("entities", [(), ("gear1-1",)])
def test_a_mate_read_whole_with_fewer_than_two_entities_is_not_described_and_refuses(entities):
    """N2: a lock that read its type and a count of 0 or 1 is not taken as described: it refuses as an unreadable
    mate does when anything is put, with no garbled sentence."""
    assert not swcom.MateInfo("Lock1", 16, entities).whole
    fake = _built_train()
    _sprocket_on_g1(fake, axis="")
    real = fake.mate_info
    fake.mate_info = lambda handle: swcom.MateInfo("UserLock1", 16, entities) if fake.mate_handles[handle] == \
        "UserLock1" else real(handle)
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (problem,) = raised.value.problems
    assert problem.kind == swbuild.PROBLEM_UNREAD and problem.sentence.startswith(
        "SolidWorks would not say what UserLock1 in T.SLDASM holds")
    assert "your  with" not in str(raised.value)


def test_with_a_mate_not_wholly_read_every_body_counts_as_the_users_for_the_bind(monkeypatch):
    """N3: on a quiet press an unreadable mate is not refused (nothing is put); should the change phase then put a
    body after all, the bind stops it, since the unread mate could be on any body."""
    fake = _built_train()
    fake.user_component(T_ASM, "Housing-1", HOUSING, (IDENTITY9, (0.0, 0.0, -40.0)), fixed=True)
    fake.user_mate(T_ASM, "Mystery1", kind="coincident", a=("Housing-1", "plane1"), b=("gear4-1", "plane1"))
    fake.unread_mates = {"Mystery1": "type"}
    monkeypatch.setattr(swbuild, "_may_put", lambda *args, **kwargs: set())
    result = _moving(fake)
    assert not result.ok and result.placed == []
    assert any("which its check before any change found it would not put, and your work is on" in text
               for _, text in result.failures), result.failures


def test_a_carried_component_whose_file_did_not_read_takes_the_sub_assembly_branch():
    """N4: a component whose path SolidWorks would not name is not assumed to be a part: it is gated as a
    sub-assembly, not measured."""
    fake = _built_train()
    _sprocket_on_g1(fake)
    fake.component_paths["Sprocket-1"] = ""
    with pytest.raises(UserWorkRefused) as raised:
        _moving(fake)
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_UNSETTLED and "(findings.USER_MATE_PUT_SUBASSEMBLY_ON_2026 is None)" in \
        problem.sentence
    assert "putting a component of yours whose file SolidWorks would not name, taken for a sub-assembly, with" in \
        problem.sentence


def test_a_value_on_a_document_marked_unsaved_is_refused_saying_both_readings():
    """N1 (the coordinator's ruling): Update 1 left the part unsaved; it was reopened from its file and touched, so it
    reads modified; the refusal stands, and says it may be the user's edit or that Update lost."""
    fake = _built_train()
    key = _key(P17)
    fake.touched.add(key)              # the file's own Face Width 10, reopened and then touched: it reads modified
    recorded = tuple((n, "12" if n == "Face Width" else x) for n, x in _recorded(S17))     # Update 1 set 12
    doc = swbuild.DocumentValues(P17, _values(S17.with_values(face_width="12")), recorded=recorded,
                                 cells=(("Face Width", "Gears!I3"),), mark=swbuild.MARK_UNSAVED)
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, parts=[doc])
    (problem,) = raised.value.problems
    assert problem.values[0].unsaved and problem.values[0].recorded == "12"
    assert problem.sentence == (
        "Face Width in Gear_m1.5_N17 is 10 in SolidWorks and 12 in the workbook, where Update SolidWorks last set 12 "
        "and left Gear_m1.5_N17 unsaved: either it was changed in SolidWorks since, or SolidWorks closed without "
        "saving that Update and Gear_m1.5_N17 was changed after it was opened again. If it was changed, type 10 in "
        "Gears!I3, or set it back to 12 in SolidWorks; if that Update was lost, set it to 12 in SolidWorks. Then press "
        "Update SolidWorks again.")
    unmarked = replace(doc, mark="")
    with pytest.raises(UserWorkRefused, match=r"^Face Width in Gear_m1.5_N17 is 10 in SolidWorks and 12 in the "
                                              r"workbook: type 10 in Gears!I3"):
        _update_train(fake, parts=[unmarked])


def test_a_face_z_on_an_assembly_marked_unsaved_is_refused_saying_both_readings():
    fake = _built_train()
    _edit(fake, T_ASM, "G4 Face Z", "22")
    motion = _motion(face_globals=(("G4", GlobalVariable("G4 Face Z", "25")),), record_holds=True,
                     recorded_faces=(("G4", "20"),), assembly_mark=swbuild.MARK_UNSAVED)
    fake.touched.add(_key(T_ASM))                                           # open and modified since that Update
    with pytest.raises(UserWorkRefused) as raised:
        _update_train(fake, placements=_train_placements(_train_frames(z4=25.0)), motion=motion)
    assert str(raised.value).startswith("G4 Face Z in T is 22 mm in SolidWorks, where Update SolidWorks last set it "
                                        "to 20 mm and left T unsaved, and the workbook now asks 25 mm: either it was "
                                        "changed in SolidWorks since, or SolidWorks closed without saving that Update")
