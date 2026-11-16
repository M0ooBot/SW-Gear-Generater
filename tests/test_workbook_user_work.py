"""W9a package A on the planning side it needs (ISSUE-1-PLAN K1, K11; W9A-INTERFACES.md): ``update.classify`` hands
the worker what the record says each document holds, the workbook cell of each value, the features the app's plans
made, the layout's Name2 and whether the record vouches for the assembly; ``finish_update`` records a component found
by its part. And the round trip on the fake: a value the user changed in SolidWorks refuses naming its cell, a
sprocket the user locked to a gear goes back with it."""

import pytest

from gear_generator import swbuild
from gear_generator.gears.equations import split_equation
from gear_generator.swbuild import PROBLEM_VALUE, UserWorkRefused
from gear_generator.workbook import update

from test_workbook_gearbox import settled_findings, static_w4, turning  # noqa: F401
from test_workbook_model import read, reducer, write
from test_workbook_update import (assessed, fake_build, gears, name2, press, shafts, turned,  # noqa: F401
                                  worker_answer)


def _classify(record, spec):
    return update.classify(record, assessed(spec), exists=lambda p: True)


def _read_reducer(tmp_path):
    spec, diagnostics = read(write(tmp_path, reducer()))
    assert diagnostics == []
    return spec


def test_classify_hands_the_worker_what_tells_the_users_work_from_the_apps(turned, tmp_path):
    disk, record = turned
    spec = _read_reducer(tmp_path)
    plan = update.classify(record, assessed(spec), exists=disk.exists)
    box = record.gearbox
    entries = {e.path: e for e in record.current_parts()}
    for part in plan.parts:
        assert part.recorded == tuple((n, x) for n, x in entries[part.path].variables)
        assert "Bore" in part.made and "Bore Sketch" in part.made, part.made
        assert dict(part.cells)["Bore Diameter"] == spec.cell("Gears", spec.gear(part.gear_ids[0]).row, "bore")
    kwargs = plan.update_kwargs()
    assert [d.recorded for d in kwargs["parts"]] == [p.recorded for p in plan.parts]
    assert [d.made for d in kwargs["parts"]] == [p.made for p in plan.parts]
    assert plan.layout.recorded == (("S2 X", "63.75"), ("S3 X", "131.75"))
    assert dict(plan.layout.cells)["S3 X"] == spec.cell("Shafts", spec.shaft("S3").row, "x")
    assert plan.layout.made == plan.layout.features
    m = plan.motion
    assert m.layout_component == box.layout_component and m.record_holds is True
    assert m.recorded_faces == (("G4", "17"),)
    assert dict(m.cells)["G4 Face Z"] == spec.cell("Gears", spec.gear("G4").row, "at")
    assert {p.gear: p.part for p in plan.placements} == {c.gear: c.part for c in box.components}


def test_an_unsaved_or_mismatched_mark_withdraws_the_records_word(turned):
    disk, record = turned
    part = record.current_parts()[1].path
    record.unsaved[part] = 1.0
    record.mismatched[record.gearbox.layout] = 1.0
    plan = update.classify(record, assessed(reducer()), exists=disk.exists)
    assert [p.recorded is None for p in plan.parts] == [p.path == part for p in plan.parts]
    assert plan.layout.recorded is None and plan.motion.record_holds is True
    record.unsaved[record.gearbox.assembly] = 1.0
    assert update.classify(record, assessed(reducer()), exists=disk.exists).motion.record_holds is False


def test_finish_update_records_a_component_found_by_its_part(turned):
    disk, record = turned
    plan = update.classify(record, assessed(reducer()), exists=disk.exists)
    result = worker_answer(plan, changed_parts=())
    g4 = name2(record, "G4")
    result.renamed = [("G4", g4, "OutputGear-7")]
    done = update.finish_update(plan, result, record, digest="d2", read_sidecar=disk.read_sidecar,
                                mtime=lambda p: 1.0)
    assert name2(done.record, "G4") == "OutputGear-7" and name2(record, "G4") == g4


# -- the round trip on the fake ------------------------------------------------------------------------------------


@pytest.fixture
def on_fake(turning):
    sw, plan, result, record = fake_build(reducer())
    return sw, record


def _edit(sw, path, name, expression):
    key = path.replace("/", "\\").lower()
    for texts in (sw.memory[key][0], sw.saved[key][0]):
        for i, text in enumerate(texts):
            if split_equation(text)[0] == name:
                texts[i] = f'"{name}"= {expression}'


def test_round_trip_a_bore_the_user_typed_in_solidworks_refuses_until_the_workbook_or_solidworks_agrees(on_fake):
    sw, record = on_fake
    part = next(p.path for p in record.current_parts() if "G2" in p.gears)
    _edit(sw, part, "Bore Diameter", "14")
    plan = _classify(record, reducer())
    with pytest.raises(UserWorkRefused) as raised:
        swbuild.update_gearbox(sw, **plan.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    (problem,) = raised.value.problems
    assert problem.kind == PROBLEM_VALUE and problem.values[0].name == "Bore Diameter"
    assert (problem.values[0].live, problem.values[0].wanted, problem.values[0].recorded) == ("14", "12", "12")
    _, result, _ = press(sw, record, gears(reducer(), G2=dict(bore="14")))
    assert result.ok, result.failures


def test_round_trip_a_sprocket_the_user_locked_to_the_input_goes_back_with_it_on_a_layout_move(on_fake):
    from test_swbuild import IDENTITY9, _compose, _frame_off, _inverse
    sw, record = on_fake
    asm, g1 = record.gearbox.assembly, name2(record, "G1")
    sw.user_component(asm, "Sprocket-1", r"C:\Parts\Sprocket.SLDPRT", (IDENTITY9, (0.0, 0.0, 40.0)))
    sw.user_lock(asm, "Lock3", g1, "Sprocket-1")
    rel = _compose(_inverse(sw.frames[g1]), sw.frames["Sprocket-1"])
    spec = shafts(reducer(), S2=dict(x="64.5"), S3=dict(x="132.5"))
    plan, result, finished = press(sw, record, spec)
    assert result.ok, result.failures
    assert result.carried == [("Sprocket-1", "G1", "")]
    assert max(_frame_off(_compose(_inverse(sw.frames[g1]), sw.frames["Sprocket-1"]), rel)) < 1e-9
    assert [m.name for m in result.user_work.mates] == ["Lock3"] and not sw.mate("Lock3", asm).suppressed
