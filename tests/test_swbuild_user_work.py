"""W9a package A (ISSUE-1-PLAN §2.1, §5's tests against the fake; W9A-INTERFACES.md): Update leaves the user's work
in a built assembly alone, puts a component the user locked to a gear along with it (route (c1)), or refuses before
any write with a sentence naming what is in the way.

The fake is tests/test_swbuild.py's: ``user_component``, ``user_lock`` and ``user_mate`` add the user's work, and the
fake raises AssertionError on any write to it but a put of one of the user's components (``user_puts``), which only
route (c1) may make."""

from dataclasses import replace

import pytest

from gear_generator import findings, swbuild, swcom
from gear_generator.gears.base import GlobalVariable
from gear_generator.gears.equations import DEGREES, split_equation
from gear_generator.swbuild import (PROBLEM_LOCK_BY_MODE, PROBLEM_OTHER_KIND, PROBLEM_TIE, PROBLEM_TWO_BODIES,
                                    PROBLEM_UNSETTLED, PROBLEM_VALUE, UserWorkRefused)

from test_swbuild import (CHANGING, IDENTITY9, P17, P51, S17, T_ASM, TC_ASM, W, _close, _compose, _frame_off,
                          _inverse, _key, _motion, _rot_z, _tc_update, _train_frames, _train_layout_values,
                          _train_placements, _train_routes_agree, _update_train, _values, _built_train, mode_findings,
                          names, plan, tc_built)  # noqa: F401

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
        "Gear5 is a mate in T.SLDASM that Gear Generator did not make, and it may hold the gears where Update "
        "SolidWorks would put them, so nothing is changed; suppress Gear5 in SolidWorks and press Update SolidWorks "
        "again. Angle1 is a mate in T.SLDASM that Gear Generator did not make, and it may hold the gears where Update "
        "SolidWorks would put them, so nothing is changed; suppress Angle1 in SolidWorks and press Update SolidWorks "
        "again.")
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
    assert problem.sentence == (
        "Update SolidWorks must turn G1's train back to its built place, and with your mates on SolidWorks reads it as "
        "unable to turn: your UserLock1, UserAxis1 and UserTie are on that train, so nothing is changed; suppress "
        "UserLock1, UserAxis1 and UserTie in SolidWorks and press Update SolidWorks again.")
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
    assert "change the workbook to 12" in raised.value.problems[0].sentence


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
    result = _update_train(fake, parts=[_p17_update()])
    assert result.ok, result.failures
    assert [(f.name, f.code) for f in result.user_features_in_error] == [("Keyway", 71)]
    assert not result.parts[0].rebuilt and result.parts[0].changed == ["Face Width"]
    lines = result.log_lines()
    assert "CHECK   the rebuild reported an error, from your features alone: Keyway" in lines
    assert "CHECK   your Keyway in Gear_m1.5_N17.SLDPRT is in error after the rebuild" in lines


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
    assert "your UserLock2 and UserTie are on that train" in failure[1]
    assert "suppress UserLock2 and UserTie in 4L" in failure[1]
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
    for call in (lambda: fake.fix_component("user1"), lambda: fake.unfix_component("user1"),
                 lambda: fake.set_mate_suppressed("other1", True)):
        with pytest.raises(AssertionError, match=r"of the user's \(W9a §0.3\)"):
            call()
    fake.place_component("user1", IDENTITY9, (0.0, 0.0, 31.0), kind=swcom.ASSEMBLY_TRAIN)
    assert [n for n, _, _ in fake.user_puts] == ["Sprocket-1"]


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
    assert [p.kind for p in raised.value.problems] == [PROBLEM_TIE]           # one train: G1 to G4 through G2-G3
    assert raised.value.problems[0].mates == ("UserLock1", "UserLock4", "UserLockA", "UserLockB")
