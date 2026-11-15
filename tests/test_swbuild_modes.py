"""W8's shapes on the worker's side, written at W8's interface commit (W8-INTERFACES.md §2-§3): ``ModesPlan.check``,
the one rule of which links are on in a configuration (``on_in`` / ``links_in``), the ``modes=`` gate of ``build`` and
``build_gearbox``, the swcom members' refusals until package A writes them, and the per-version positions switch.

The modes plan below is TransferCase_Parallel's (W8-PLAN §2.2, §2.3): the slides' values per configuration are the
answer key's (RangeSlv 46/46/56/66, ModeSlv 96/106/96/106 in 2H/4H/N/4L), and the couplings' on/off table its mate
table, each coupling made in the first mode it is on in.
"""

import math
from dataclasses import fields, replace

import pytest

from gear_generator import findings, swbuild, swcom
from gear_generator.gears import base
from gear_generator.gears.base import BuildPlan
from gear_generator.swbuild import (BuildError, GearboxResult, GearboxUpdate, LockLink, MateRef, MeshLink, ModeCheck,
                                    ModesPlan, ModeStep, links_in, on_in)

from test_swbuild import FakeSolidWorks, never_exists

MODES = ("2H", "4H", "N", "4L")
SLIDES = {"RangeSlv along Rear": (46.0, 46.0, 56.0, 66.0), "ModeSlv along Rear": (96.0, 106.0, 96.0, 106.0)}
COUPLES = {"RangeSlv engages InDog": ("gear7", "gear2", ("2H", "4H")),
           "ModeSlv engages FrontDog": ("gear8", "gear9", ("4H", "4L")),
           "RangeSlv engages LoDog": ("gear7", "gear6", ("4L",))}
ALWAYS = ("InPin on In Axis", "RangeSlv on Rear Axis", "ModeSlv on Rear Axis", "ModeSlv splined to RangeSlv",
          "RangeSlv along Rear", "ModeSlv along Rear")
EYE = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
ASM = r"C:\T\TransferCase.SLDASM"


def assembly_plan():
    """A cut-down assembly plan holding the always-on mates W8 adds (and one of W5's), as names and kinds."""
    return BuildPlan("workbook-assembly", "", (
        base.NewAssembly(""),
        base.AddComponent("layout", r"C:\T\TransferCase_Layout.SLDPRT"),
        base.AddComponent("gear1", r"C:\T\InPin.SLDPRT"),
        base.AddComponent("gear2", r"C:\T\Dog_m1.5_N30.SLDPRT", (0.0, 0.0, 47.0)),
        base.AddComponent("gear6", r"C:\T\Dog_m1.5_N30.SLDPRT", (0.0, 0.0, 67.0)),
        base.AddComponent("gear7", r"C:\T\Sleeve_m1.5_N30.SLDPRT", (0.0, 0.0, 46.0)),
        base.AddComponent("gear8", r"C:\T\Sleeve_m1.5_N30.SLDPRT", (0.0, 0.0, 96.0)),
        base.AddComponent("gear9", r"C:\T\Dog_m1.5_N30.SLDPRT", (0.0, 0.0, 107.0)),
        base.Fix("layout"),
        base.Mate("m1", "coincident", "gear1:Gear Axis", "layout:In Axis", name="InPin on In Axis"),
        base.Mate("m2", "coincident", "gear7:Gear Axis", "layout:Rear Axis", name="RangeSlv on Rear Axis"),
        base.Mate("m3", "point distance", "gear7:origin", "layout:plane1", 46.0, name="RangeSlv along Rear"),
        base.Mate("m4", "coincident", "gear8:Gear Axis", "layout:Rear Axis", name="ModeSlv on Rear Axis"),
        base.Mate("m5", "point distance", "gear8:origin", "layout:plane1", 96.0, name="ModeSlv along Rear"),
        base.Mate("m6", "gear", "gear7:Gear Axis", "gear8:Gear Axis", name="ModeSlv splined to RangeSlv"),
        base.Rebuild(),
        base.SaveAs(ASM),
    ), ASM)


def modes_plan(**changes):
    """The fixture's ModesPlan, each coupling made in the first mode it is on in (N makes none)."""
    made = set()
    steps = []
    for index, mode in enumerate(MODES):
        ops = []
        for name, (sleeve, dog, on) in COUPLES.items():
            if mode in on and name not in made:
                made.add(name)
                ops.append(base.Mate(f"c{len(made)}", "gear", f"{sleeve}:Gear Axis", f"{dog}:Gear Axis", name=name))
        on = ALWAYS + tuple(n for n, (_, _, modes) in COUPLES.items() if mode in modes)
        off = tuple(n for n, (_, _, modes) in COUPLES.items() if mode not in modes)
        values = {name: v[index] for name, v in SLIDES.items()}
        frames = {"gear7": (EYE, (0.0, 0.0, values["RangeSlv along Rear"])),
                  "gear8": (EYE, (0.0, 0.0, values["ModeSlv along Rear"]))}
        steps.append(ModeStep(mode, tuple(ops), on, off, values, frames))
    plan = ModesPlan(tuple(steps), same_way=tuple(COUPLES))
    return replace(plan, **changes) if changes else plan


def with_step(plan, index, **changes):
    steps = list(plan.steps)
    steps[index] = replace(steps[index], **changes)
    return replace(plan, steps=tuple(steps))


# -- the fixture's plan is sound, and pins §2.3 -------------------------------------------------------------------

def test_the_fixtures_modes_plan_is_sound_alone_and_against_its_assembly_plan():
    assert assembly_plan().check() == []
    assert modes_plan().check() == [] and modes_plan().check(assembly_plan()) == []


def test_the_fixtures_slide_values_and_couplings_are_the_answer_keys():
    plan = modes_plan()
    assert [s.name for s in plan.steps] == list(MODES)
    assert {n: tuple(s.values[n] for s in plan.steps) for n in SLIDES} == {
        "RangeSlv along Rear": (46.0, 46.0, 56.0, 66.0), "ModeSlv along Rear": (96.0, 106.0, 96.0, 106.0)}
    assert [[op.name for op in s.ops] for s in plan.steps] == [
        ["RangeSlv engages InDog"], ["ModeSlv engages FrontDog"], [], ["RangeSlv engages LoDog"]]
    table = {n: tuple("on" if n in s.on else "off" for s in plan.steps) for n in COUPLES}
    assert table == {"RangeSlv engages InDog": ("on", "on", "off", "off"),
                     "RangeSlv engages LoDog": ("off", "off", "off", "on"),
                     "ModeSlv engages FrontDog": ("off", "on", "off", "on")}


# -- each rule of ModesPlan.check -----------------------------------------------------------------------------------

@pytest.mark.parametrize("doctor,sentence", [
    (lambda p: replace(p, steps=()), "The modes plan has no modes."),
    (lambda p: with_step(p, 2, name="4h"), "The modes 4H and 4h have one name, ignoring case"),
    (lambda p: with_step(p, 2, name="N mode"), "The mode name 'N mode' is not letters, digits, _ and - only."),
    (lambda p: with_step(p, 2, ops=(base.LinkDimension("D1@RangeSlv along Rear", '"x"'),)), "is not a gear mate"),
    (lambda p: with_step(p, 2, ops=(base.Mate("c9", "lock", "gear6", "gear7", name="x"),)), "is not a gear mate"),
    (lambda p: with_step(p, 0, ops=(replace(p.steps[0].ops[0], name=""),)), "the gear mate c1 has no name"),
    (lambda p: with_step(p, 1, ops=(replace(p.steps[1].ops[0], id="c1"),)), "the id c1 is used twice"),
    (lambda p: with_step(p, 1, ops=p.steps[1].ops + p.steps[0].ops[:1]), "RangeSlv engages InDog is made a second"),
    (lambda p: with_step(p, 2, on=p.steps[2].on + ("RangeSlv engages InDog",)), "RangeSlv engages InDog is both on"),
    (lambda p: with_step(p, 2, off=p.steps[2].off[1:]), "Mode N does not say on or off for the same mates as mode 2H"),
    (lambda p: with_step(with_step(p, 0, ops=()), 1, ops=p.steps[1].ops + p.steps[0].ops),
     "RangeSlv engages InDog is made in mode 4H, not in 2H, the first mode it is on in."),
    (lambda p: with_step(p, 3, ops=()), "The mate RangeSlv engages LoDog is switched per mode but no mode makes it."),
    (lambda p: replace(p, steps=tuple(replace(s, on=tuple(n for n in s.on if n != "RangeSlv engages LoDog"),
                                              off=tuple(sorted(set(s.off) | {"RangeSlv engages LoDog"})))
                                      for s in p.steps)),
     "The mate RangeSlv engages LoDog is on in no mode."),
    (lambda p: replace(p, same_way=("ModeSlv splined to RangeSlv",)),
     "ModeSlv splined to RangeSlv is said to turn its gears the same way, and no mode makes it."),
    (lambda p: with_step(p, 1, values={"RangeSlv along Rear": 46.0}),
     "Mode 4H does not give a value for the same slides as mode 2H: ModeSlv along Rear."),
    (lambda p: with_step(p, 2, values=dict(p.steps[2].values, **{"RangeSlv along Rear": 0.0})),
     "In mode N, the slide RangeSlv along Rear is given 0.0 mm, where it holds a distance from the Front plane "
     "above 0."),
    (lambda p: with_step(p, 2, values=dict(p.steps[2].values, **{"RangeSlv along Rear": -56.0})), "is given -56.0 mm"),
    (lambda p: with_step(p, 2, values=dict(p.steps[2].values, **{"RangeSlv along Rear": math.nan})), "is given nan mm"),
    (lambda p: with_step(p, 2, frames={"gear7": (EYE[:6], (0.0, 0.0, 56.0))}),
     "In mode N, the frame of gear7 is not nine and three numbers."),
])
def test_an_unsound_modes_plan_is_named_whole(doctor, sentence):
    problems = doctor(modes_plan()).check()
    assert any(sentence in p for p in problems), problems


@pytest.mark.parametrize("doctor,sentence", [
    (lambda p: replace(p, steps=tuple(replace(s, on=tuple(n for n in s.on if n != "InPin on In Axis"))
                                      for s in p.steps)),
     "The modes do not say on or off for exactly the assembly's mates: InPin on In Axis."),
    (lambda p: replace(p, steps=tuple(replace(s, values=dict(s.values, **{"InPin on In Axis": 5.0}))
                                      for s in p.steps)),
     "The slide InPin on In Axis is not a distance mate of the assembly."),
    (lambda p: with_step(p, 3, frames={"gear99": (EYE, (0.0, 0.0, 1.0))}),
     "In mode 4L, gear99 is not a component of the assembly."),
    (lambda p: with_step(p, 1, ops=(replace(p.steps[1].ops[0], id="m6"),)), "the id m6 is used twice"),
    (lambda p: with_step(p, 1, ops=p.steps[1].ops + (base.Mate("c7", "gear", "a:Gear Axis", "b:Gear Axis",
                                                               name="ModeSlv splined to RangeSlv"),)),
     "the mate ModeSlv splined to RangeSlv is made a second time"),
])
def test_a_modes_plan_is_checked_against_its_assembly_plan_when_given(doctor, sentence):
    doctored = doctor(modes_plan())
    problems = doctored.check(assembly_plan())
    assert any(sentence in p for p in problems), problems


# -- on_in / links_in: the one rule of "which mates are on in mode M" ------------------------------------------------

def test_a_link_with_no_modes_is_on_in_every_configuration_and_names_compare_ignoring_case():
    assert on_in((), "4L") and on_in((), "Default")
    assert on_in(("2H", "4H"), "4H") and on_in(("2H", "4H"), "4h") and not on_in(("2H", "4H"), "N")


def test_links_in_keeps_the_links_on_in_a_configuration_in_order():
    couple = MeshLink("RangeSlv", "InDog", 1.0, 12.0, modes=("2H", "4H"))
    mesh = MeshLink("FDrive", "FIdler", -1.5, 18.0)
    spline = LockLink("RangeSlv", "ModeSlv", 12.0)
    carrier = swbuild.CarrierLink("C carrier", (), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    ref = MateRef("ModeSlv engages FrontDog", "couple", ("ModeSlv", "FrontDog"), modes=("4H", "4L"))
    links = (couple, mesh, spline, carrier, ref)
    assert links_in(links, "2H") == (couple, mesh, spline, carrier)
    assert links_in(links, "N") == (mesh, spline, carrier)
    assert links_in(links, "4L") == (mesh, spline, carrier, ref)


# -- the shapes' defaults keep every earlier call as it was --------------------------------------------------------

def test_every_w8_field_defaults_to_what_a_gearbox_with_no_modes_holds():
    assert MeshLink("a", "b", -1.0, 20.0).modes == () and LockLink("a", "b", 20.0).modes == ()
    ref = MateRef("G1 meshes G2", "mesh", ("G1", "G2"))
    assert (ref.values, ref.modes) == ((), ())
    update = swbuild.MotionUpdate()
    assert (update.configurations, update.mode_placements, update.recorded_by_mode, update.slide_values,
            update.on_sets) == ((), (), (), (), ())
    result = GearboxResult()
    assert result.modes == [] and result.positions_per_configuration is None
    done = GearboxUpdate()
    assert (done.configuration, done.visited, done.unsuppressed_in, done.suppressed_in, done.slid,
            done.values_restored, done.put_in, done.extra_configurations, done.modes,
            done.positions_per_configuration) == ("", [], [], [], [], [], [], [], [], None)
    assert [f.name for f in fields(ModeCheck)] == ["name", "mates", "suppressed", "values", "clashes",
                                                   "interference_error", "out_of_step", "off_axis", "turned"]
    assert swbuild.STAGE_MODE == "mode" and swbuild.STAGES[-1] == swbuild.STAGE_MODE


def test_the_protocol_and_the_session_both_have_the_configuration_members():
    members = ("configurations", "active_configuration", "add_configuration", "show_configuration",
               "delete_configuration", "set_mate_suppressed_in", "mate_suppression", "set_dimension_in",
               "dimension_values")
    for name in members:
        assert hasattr(swbuild.SolidWorks, name) and callable(getattr(swcom.Session, name)), name


# -- the modes= gate: refused before anything is made --------------------------------------------------------------

def test_an_unsound_modes_plan_is_refused_with_every_problem_before_anything_is_made():
    fake = FakeSolidWorks()
    bad = with_step(modes_plan(), 2, name="4h")
    with pytest.raises(BuildError, match=r"^The modes plan is not sound, so nothing is made: The modes 4H and 4h"):
        swbuild.build(fake, assembly_plan(), never_exists, modes=bad)
    assert not [name for name, _ in fake.calls if name.startswith("new_")]


def test_modes_with_no_assembly_are_refused_as_a_fault():
    with pytest.raises(BuildError, match="Modes were given with no assembly to make their configurations in"):
        swbuild._modes_gate(None, modes_plan())
    swbuild._modes_gate(None, None)
    swbuild._modes_gate(assembly_plan(), None)


# -- swcom: the members refuse with a sentence until A writes them; the epoch; the positions switch -------------------

def test_the_configuration_epoch_starts_at_0_and_each_raise_starts_a_new_one():
    session = swcom.Session(None, (34, 1, 1), 1)
    assert session._epoch == 0
    session._raise_epoch()
    session._raise_epoch()
    assert session._epoch == 2


def test_a_configuration_gone_is_a_component_gone_so_update_turns_it_into_not_as_built():
    assert issubclass(swcom.ConfigurationGone, swcom.ComponentGone)


@pytest.mark.parametrize("on_2026,on_2024,revision,wanted", [
    (True, None, (34, 1, 1), True),
    (True, None, (32, 5, 0), None),                 # 2024 unsettled: neither claim
    (True, False, (32, 5, 0), False),
    (True, False, (33, 0, 0), None),                # 2025 has no finding of its own
    ("unsettled", None, (34, 1, 1), None),          # not a bool: neither claim
    (True, True, (), None),
])
def test_the_positions_switch_reads_the_running_versions_finding(monkeypatch, on_2026, on_2024, revision, wanted):
    for year, value in ((2026, on_2026), (2024, on_2024)):
        name = f"POSITIONS_PER_CONFIGURATION_ON_{year}"
        if value is None:
            monkeypatch.delattr(findings, name, raising=False)
        else:
            monkeypatch.setattr(findings, name, value, raising=False)
    assert swcom.positions_per_configuration(revision) is wanted
