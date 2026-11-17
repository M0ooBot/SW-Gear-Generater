"""W9c package B (ISSUE-1-PLAN §2.1 "W9c", K6, §2.4; W9C-INTERFACES.md): ``classify`` carries in place what Update can
now add, take out and re-mate — a gear on a shaft on record along Z±, a hub that becomes its shaft's anchor, a gear
that anchors none taken out, a coupling or sliding mesh newly needed, bands given or taken, a Modes row added or
removed — and leaves every other edit structural, each with its sentence; the footer foresees what would stop the
press; ``finish_update`` writes what the worker reports done; and the result's sentences. Every read is asserted free
of errors before it is classified, as the window never classifies one that is not."""

from dataclasses import replace

import pytest

from gear_generator import store, swbuild, ui_text
from gear_generator.swbuild import GearboxUpdate, UpdateResult
from gear_generator.workbook import assess, gearbox, update
from gear_generator.workbook.model import Gear, Mesh, Mode
from workbook_fixtures import range_box, range_box_fixed, transfer_case_parallel

BOOK = "C:\\B\\RangeBox.xlsx"


def assessed(spec):
    return assess.assess(replace(spec, source_path=BOOK), [], "C:\\Out\\")


def legal(spec):
    """The read as the window would classify it: no error anywhere, the gate open."""
    a = assessed(spec)
    errors = [d.message for d in a.diagnostics if d.is_error]
    assert errors == [] and a.lay_out_refusal() == "", errors
    return a


def built(spec):
    """A first Build of ``spec`` on the fake, its record read back from its JSON."""
    from test_swbuild import FakeSolidWorks
    sw = FakeSolidWorks()
    a = legal(spec)
    plan = gearbox.plan_gearbox(a, None, exists=sw.exists, read_sidecar=lambda p: None)
    assert plan.refusal == "", plan.refusal
    result = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    assert result.ok, result.failures
    done = gearbox.finish_build(plan, result, None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=lambda p: None, exists=sw.exists)
    return sw, store.link_record_from_json(store.link_record_to_json(done.record))


def classify(record, spec):
    return update.classify(record, legal(spec), exists=lambda p: p.lower() in _ON_DISK)


_ON_DISK: set = set()


@pytest.fixture(autouse=True)
def _nothing_new_on_disk():
    """A new part's file is not on disk before the Update builds it; everything on record is."""
    _ON_DISK.clear()
    yield
    _ON_DISK.clear()


def on_disk(record):
    _ON_DISK.update(p.lower() for p in [x.path for x in record.parts] + [c.path for c in record.gearbox.carriers]
                    + [record.gearbox.layout, record.gearbox.assembly])


def with_gear(spec, gid, **changes):
    return replace(spec, gears=tuple(replace(g, **changes) if g.id == gid else g for g in spec.gears))


def without_gear(spec, gid):
    return replace(spec, gears=tuple(g for g in spec.gears if g.id != gid),
                   meshes=tuple(m for m in spec.meshes if gid not in (m.a, m.b)))


def renamed(spec):
    return replace(spec, box=replace(spec.box, name="RangeBox"))


@pytest.fixture(scope="module")
def range_box_record():
    return built(range_box())


@pytest.fixture(scope="module")
def parallel_record():
    return built(transfer_case_parallel())


# -- the plan's Done-when edit: RangeBox to RangeBox_Fixed, one Update ---------------------------------------------

def test_range_box_edited_to_range_box_fixed_is_one_update_not_build_again(range_box_record):
    """Hub added as Output's anchor, with RangeSlv splined to it; RangeSlv's bands given in place; its face, At and
    slides values. Nothing structural."""
    _, record = range_box_record
    on_disk(record)
    up = classify(record, renamed(range_box_fixed()))
    assert up.refusal == "" and up.structural == () and not up.needs_new_revision
    ip = up.in_place
    (hub,) = ip.added
    assert (hub.gear, hub.build is not None) == ("Hub", True) and hub.part.endswith("Hub_m1.25_N17.SLDPRT")
    names = [op.name for op in hub.ops if type(op).__name__ == "Mate"]
    assert names == ["Hub on Output Axis", "Hub along Output", "RangeSlv splined to Hub"]
    assert [type(op).__name__ for op in hub.ops][:2] == ["AddGlobal", "AddComponent"]
    sleeve = next(c.name for c in record.gearbox.components if c.gear == "RangeSlv")
    assert dict(hub.handles)[next(h for h, n in hub.handles if n == sleeve)] == sleeve
    assert dict(hub.senses) == {"RangeSlv splined to Hub": True}
    (band,) = ip.bands
    assert (band.gear, band.add) == ("RangeSlv", True) and band.features[-1] == "Relief"
    assert [type(op).__name__ for op in band.ops][:3] == ["AddGlobal"] * 3
    assert (ip.removed, ip.new_mates, ip.modes_added, ip.modes_removed) == ((), (), (), ())
    assert next(p for p in up.placements if p.gear == "Hub").component == ""            # C1: the worker's to fill
    sleeve_part = next(p for p in up.parts if "RangeSlv" in p.gear_ids)
    assert sleeve_part.changed and "Relief" in sleeve_part.made                          # C2
    assert not any(v.name in ("Start Band", "End Band") for v in sleeve_part.variables)  # given in the bands' step
    assert sleeve_part.spec.bands_mm() == (5.0, 5.0)
    assert up.update_kwargs()["in_place"] is ip
    assert ui_text.update_summary(up).startswith(
        "Update SolidWorks will add Hub on Output (a new part, Hub_m1.25_N17), as its shaft's anchor with RangeSlv "
        "splined to it, give RangeSlv its bands in Sleeve_m1.25_N17, change RangeSlv's values (Sleeve_m1.25_N17)")


def test_an_update_with_nothing_in_place_hands_the_worker_no_in_place(range_box_record):
    _, record = range_box_record
    on_disk(record)
    up = classify(record, with_gear(renamed(range_box()), "Sun", backlash="0.4"))
    assert not up.in_place and up.in_place_record is None and "in_place" not in up.update_kwargs()
    assert update.in_place_ahead(up, record) == ()


# -- a gear added and one taken out, on a gearbox with modes ------------------------------------------------------

def test_a_gear_added_on_a_shaft_on_record_after_its_anchor_is_locked_to_it_in_place(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = transfer_case_parallel()
    extra = Gear("FExtra", "FrontDrv", "150", "spur", "", "25", "2", "", "10", "", row=14)
    up = classify(record, replace(spec, gears=spec.gears + (extra,)))
    assert up.structural == ()
    (added,) = up.in_place.added
    assert [op.name for op in added.ops if type(op).__name__ == "Mate"] == ["FExtra locked to FrontDog"]
    assert dict(added.handles).values() and all(n in {c.name for c in record.gearbox.components}
                                                for _, n in added.handles)


def test_a_gear_added_before_its_shafts_anchor_would_change_a_mate_on_record_so_it_is_build_again(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = transfer_case_parallel()
    first = Gear("FFirst", "FrontDrv", "150", "spur", "", "25", "2", "", "10", "", row=1)
    up = classify(record, replace(spec, gears=(first,) + spec.gears))
    assert up.needs_new_revision
    assert ("With the gears added or taken out, the mate FrontDog on FrontDrv Axis on record would not be made as it "
            "was, and Update SolidWorks does not make a gear's own mates again in place, so the gearbox needs "
            "building again.") in up.structural


def test_a_gear_on_a_new_shaft_stays_build_again_with_its_own_sentence(parallel_record):
    from gear_generator.workbook.model import Shaft
    _, record = parallel_record
    on_disk(record)
    spec = transfer_case_parallel()
    shaft = Shaft("Aux", "frame", "0", "60", "0", "Z+", "", row=9)
    gear = Gear("AuxG", "Aux", "200", "spur", "", "20", "2", "", "10", "", row=14)
    up = classify(record, replace(spec, shafts=spec.shafts + (shaft,), gears=spec.gears + (gear,)))
    assert ("AuxG is new on Aux, which is new too, and Update SolidWorks adds a gear only on a shaft the layout part "
            "has, so the gearbox needs building again.") in up.structural
    assert "Shaft Aux is new, and the layout part has no axis for it." in up.structural


def test_a_gear_that_anchors_none_is_taken_out_with_its_mates_in_place(parallel_record):
    _, record = parallel_record
    on_disk(record)
    up = classify(record, without_gear(transfer_case_parallel(), "FIdler"))
    assert up.structural == ()
    (gone,) = up.in_place.removed
    component = next(c.name for c in record.gearbox.components if c.gear == "FIdler")
    assert (gone.gear, gone.component) == ("FIdler", component)
    assert set(gone.mates) == {"FIdler on Idler Axis", "FIdler along Idler", "FDrive meshes FIdler",
                               "FIdler meshes FOut"}
    assert all(m.name not in gone.mates for m in up.motion.mates)                     # §1: what stays
    assert all(p.gear != "FIdler" for p in up.placements)
    assert ui_text.update_summary(up).startswith("Update SolidWorks will take FIdler out with its 4 mates")


def test_a_gear_that_anchors_another_stays_build_again_naming_the_mate(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = without_gear(transfer_case_parallel(), "FrontDog")
    spec = replace(spec, modes=tuple(replace(m, positions=tuple((s, "2WD") if s == "ModeSlv" else (s, p)
                                                                for s, p in m.positions)) for m in spec.modes))
    spec = with_gear(spec, "ModeSlv", slides="2WD=0")
    up = update.classify(record, assessed(spec), exists=lambda p: True)
    assert ("FrontDog is no longer in the workbook, and it anchors FDrive (the mate FDrive locked to FrontDog): "
            "Update SolidWorks takes out only a gear that anchors none, so the gearbox needs building again."
            in up.structural)


# -- couplings and modes ---------------------------------------------------------------------------------------

def _add_mode(spec):
    return replace(spec, modes=spec.modes + (Mode("4X", (("RangeSlv", "L"), ("ModeSlv", "2WD")), row=6),))


def test_a_modes_row_added_is_a_configuration_added_in_place(parallel_record):
    _, record = parallel_record
    on_disk(record)
    up = classify(record, _add_mode(transfer_case_parallel()))
    assert up.structural == () and up.in_place.modes_added == ("4X",) and up.in_place.modes_removed == ()
    assert up.motion.configurations == ("2H", "4H", "N", "4L", "4X")
    assert ("RangeSlv along Rear", "4X", 66.0) in up.motion.slide_values
    assert dict(up.motion.on_sets)["RangeSlv engages LoDog"] == ("4L", "4X")
    assert [c for c, _ in up.motion.mode_placements] == ["2H", "4H", "N", "4L", "4X"]
    assert ui_text.update_summary(up).startswith("Update SolidWorks will add the mode 4X")


def test_a_modes_row_removed_is_a_configuration_deleted_in_place(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = transfer_case_parallel()
    up = classify(record, replace(spec, modes=tuple(m for m in spec.modes if m.name != "4H")))
    assert up.structural == () and up.in_place.modes_removed == ("4H",) and up.in_place.first_mode == ""
    assert up.motion.configurations == ("2H", "N", "4L")
    assert dict(up.motion.on_sets)["ModeSlv engages FrontDog"] == ("4L",)


def test_the_first_mode_removed_makes_the_next_the_records_first(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = transfer_case_parallel()
    up = classify(record, replace(spec, modes=spec.modes[1:]))
    assert up.in_place.modes_removed == ("2H",) and up.in_place.first_mode == "4H"
    assert "delete the mode 2H, so 4H becomes the first mode on record" in ui_text.update_summary(up)


def test_a_mode_renamed_stays_build_again(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = transfer_case_parallel()
    up = classify(record, replace(spec, modes=tuple(replace(m, name="4X") if m.name == "4H" else m
                                                    for m in spec.modes)))
    assert up.structural == (
        "The Modes sheet has 4X where the assembly has 4H: a mode renamed, or one taken out and another added in one "
        "edit, keeps nothing of the user's own states in that configuration when it is deleted and made again, and a "
        "configuration is not renamed in place, so it needs a new revision.",)


def test_a_mode_removed_that_leaves_a_coupling_on_in_no_mode_stays_build_again(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = transfer_case_parallel()
    up = update.classify(record, assessed(replace(spec, modes=spec.modes[:3])), exists=lambda p: True)
    assert ("The mode 4L is no longer on the Modes sheet, and the mate RangeSlv engages LoDog is on there alone: a mate "
            "made to be on in some modes is never left on in none, so it needs a new revision." in up.structural)


def test_a_coupling_newly_needed_between_gears_on_record_is_made_in_place(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = with_gear(transfer_case_parallel(), "ModeSlv", slides="2WD=0, 4WD=+10, X=-30")
    modes = list(spec.modes)
    modes[0] = replace(modes[0], positions=(("RangeSlv", "N"), ("ModeSlv", "X")))
    up = classify(record, replace(spec, modes=tuple(modes)))
    assert up.structural == ()
    (new,) = up.in_place.new_mates
    assert (new.op.name, new.on, new.same_way) == ("ModeSlv engages LoDog", ("2H",), True)
    names = {c.gear: c.name for c in record.gearbox.components}
    assert sorted(n for _, n in new.handles) == sorted([names["ModeSlv"], names["LoDog"]])
    assert "make ModeSlv engages LoDog, on in 2H" in ui_text.update_summary(up)


def test_a_tooth_change_on_a_gearbox_with_modes_is_a_remake_gated_before_the_press(parallel_record):
    _, record = parallel_record
    on_disk(record)
    spec = with_gear(with_gear(with_gear(transfer_case_parallel(), "FDrive", teeth="31"), "FIdler", teeth="19"),
                     "FOut", teeth="31")
    up = classify(record, spec)
    assert up.structural == () and set(up.ratios) == {"FDrive meshes FIdler", "FIdler meshes FOut"}
    (problem,) = update.in_place_ahead(up, record)
    assert problem.kind == swbuild.PROBLEM_UNSETTLED
    text, ok = ui_text.in_place_line((problem,), record)
    assert not ok and text == (
        "The next press would stop before changing anything: Update SolidWorks would make a gear mate in an assembly "
        "with modes again and set its flag in each mode, which Gear Generator has not yet been shown to do on the "
        "SolidWorks it runs on (findings.UPDATE_MAKES_MATES_WITH_MODES_ON_<year>), so the press changes nothing; Build "
        "again… makes the new revision instead.")


# -- still Build again…, and a mixed edit ----------------------------------------------------------------------------

def test_a_mixed_edit_is_build_again_and_writes_nothing(range_box_record):
    from gear_generator.workbook.model import Shaft
    _, record = range_box_record
    on_disk(record)
    spec = renamed(range_box_fixed())
    shaft = Shaft("Aux", "frame", "40", "40", "0", "Z+", "", row=7)
    gear = Gear("AuxG", "Aux", "60", "spur", "", "20", "2", "", "10", "", row=9)
    up = classify(record, replace(spec, shafts=spec.shafts + (shaft,), gears=spec.gears + (gear,)))
    assert up.needs_new_revision and any("AuxG is new on Aux" in s for s in up.structural)
    with pytest.raises(ValueError):
        up.update_kwargs()
    assert ui_text.update_summary(up).startswith(ui_text._again_sentence(up)[:20])


# -- the footer before the press ---------------------------------------------------------------------------------

def _work(**changes):
    values = dict(read_at="2026-11-18T14:02:00Z", components=[swbuild.UserComponent("Sprocket-1", "C:\\P\\S.SLDPRT")],
                  mates=[swbuild.UserMate("UserLock2", swbuild.USER_LOCK, touches=(("app", "FIdler"),
                                                                                   ("user", "Sprocket-1")),
                                          on=("2H", "4H", "N", "4L"), whole=True)])
    values.update(changes)
    return swbuild.UserWork(**values)


def test_the_footer_foresees_a_removal_refused_over_the_users_mate_and_the_unmeasured_reference_read(parallel_record):
    _, record = parallel_record
    on_disk(record)
    up = classify(record, without_gear(transfer_case_parallel(), "FIdler"))
    rec = store.link_record_from_json(store.link_record_to_json(record))
    rec.gearbox.user_work = update.user_work_entry(_work(), assembly=rec.gearbox.assembly, revision=(34, 1, 1))
    problems = update.in_place_ahead(up, rec)
    kinds = [p.kind for p in problems]
    assert swbuild.PROBLEM_REMOVED in kinds and swbuild.PROBLEM_REFERENCES in kinds
    text, ok = ui_text.in_place_line(problems, rec)
    assert not ok and text.startswith("As read at ") and "your UserLock2 is on it" in text
    assert "Sprocket-1" in text


def test_the_footer_says_each_gate_not_settled_with_the_version_on_record(range_box_record):
    _, record = range_box_record
    on_disk(record)
    up = classify(record, renamed(range_box_fixed()))
    rec = store.link_record_from_json(store.link_record_to_json(record))
    rec.gearbox.user_work = update.user_work_entry(_work(components=[], mates=[]), assembly=rec.gearbox.assembly,
                                                   revision=(34, 1, 1))
    text, ok = ui_text.in_place_line(update.in_place_ahead(up, rec), rec)
    assert not ok and text == (
        "The next press would stop before changing anything: Update SolidWorks would insert a gear into the assembly "
        "and mate it and give a built sleeve its bands in its own part, which Gear Generator has "
        "not yet been shown to do on SolidWorks 2026 (findings.UPDATE_INSERTS_A_GEAR_ON_2026 and "
        "findings.UPDATE_BANDS_IN_PLACE_ON_2026), so the press changes nothing; Build again… makes the new revision "
        "instead.")


# -- the record after the press, and the result's sentences -----------------------------------------------------------

def _finished(up, record, **result):
    base = dict(parts=[UpdateResult(unchanged=["x"]) for _ in up.parts], layout=UpdateResult(unchanged=["x"]),
                carriers=[UpdateResult(unchanged=["x"]) for _ in up.carriers])
    base.update(result)
    result_ = GearboxUpdate(**base)
    sidecars = {}

    def read_sidecar(path):
        return sidecars.get(path) or store.Sidecar(part_path=path, record=store.GearRecord(features=["Teeth"]))
    done = update.finish_update(up, result_, record, digest="d2", read_sidecar=read_sidecar, mtime=lambda p: 5.0,
                                written_by="test")
    return result_, done, store.link_record_from_json(store.link_record_to_json(done.record))


def test_finish_writes_the_hub_inserted_its_mates_and_the_bands_given(range_box_record):
    _, record = range_box_record
    on_disk(record)
    up = classify(record, renamed(range_box_fixed()))
    made = [("Hub on Output Axis", ()), ("Hub along Output", ()), ("RangeSlv splined to Hub", ())]
    hub_build = swbuild.BuildResult(saved=up.in_place.added[0].part, features=["Blank", "Teeth"], trig="degrees")
    result, done, rec = _finished(up, record, inserted=[("Hub", "Hub_m1.25_N17-1")], mates_made=made,
                                  bands_added=["RangeSlv"], built=[hub_build])
    box = rec.gearbox
    hub = next(c for c in box.components if c.gear == "Hub")
    assert hub.name == "Hub_m1.25_N17-1" and set(hub.frames) == {"H", "N", "L"}
    assert {m.name for m in box.mates} >= {n for n, _ in made}
    assert any(p.gears == ["Hub"] and p.path == up.in_place.added[0].part for p in rec.parts)
    sleeve = next(p for p in rec.parts if "RangeSlv" in p.gears)
    assert sleeve.spec["start_band"] == "5" and ["Start Band", "5"] in sleeve.variables
    renewed = dict(done.sidecars)
    sleeve_car = next(s for path, s in renewed.items() if "Sleeve" in path)
    assert sleeve_car.schema_version == 2 and sleeve_car.record.features[-1] == "Relief"
    assert any(path.endswith("Hub_m1.25_N17.gear.json") for path in renewed)
    text = ui_text.in_place_done_pieces(up, result)
    assert text == ["built Hub_m1.25_N17", "inserted Hub as Hub_m1.25_N17-1 and mated it (Hub on Output Axis, Hub "
                                           "along Output and RangeSlv splined to Hub)", "gave RangeSlv its bands"]


def test_finish_keeps_the_bands_off_record_when_the_worker_did_not_give_them(range_box_record):
    _, record = range_box_record
    on_disk(record)
    up = classify(record, renamed(range_box_fixed()))
    _, _, rec = _finished(up, record)
    sleeve = next(p for p in rec.parts if "RangeSlv" in p.gears)
    assert "start_band" not in sleeve.spec


def test_finish_takes_a_gear_out_with_its_mates_and_its_part_entry(parallel_record):
    _, record = parallel_record
    on_disk(record)
    up = classify(record, without_gear(transfer_case_parallel(), "FIdler"))
    name = up.in_place.removed[0].component
    result, _, rec = _finished(up, record, deleted=[("FIdler", name)], mates_deleted=list(up.in_place.removed[0].mates))
    box = rec.gearbox
    assert all(c.gear != "FIdler" for c in box.components) and all("FIdler" not in m.gears for m in box.mates)
    part = up.in_place.removed[0].part
    assert all("FIdler" not in p.gears for p in rec.parts)                 # ruling C6: no entry names it
    assert not any(store.same_path(p.path, part) for p in rec.parts)      # the part no gear uses leaves the record
    assert all("FIdler" not in pair for pair in box.meshes)
    assert ui_text.in_place_done_pieces(up, result) == [
        f"took FIdler ({name}) out with 4 mates, leaving its part Gear_m2_N20.SLDPRT on disk"]


def test_finish_adds_and_deletes_modes_and_says_what_the_users_states_did(parallel_record):
    _, record = parallel_record
    on_disk(record)
    up = classify(record, _add_mode(transfer_case_parallel()))
    result, _, rec = _finished(up, record, modes_added=["4X"],
                               took_active_state=[("4X", "UserLock2", "is on"), ("4X", "Sprocket-1", "is resolved")])
    box = rec.gearbox
    assert box.modes == ["2H", "4H", "N", "4L", "4X"]
    assert {m.name: m.modes for m in box.mates}["RangeSlv engages LoDog"] == ["4L", "4X"]
    assert {m.name: m.values for m in box.mates}["RangeSlv along Rear"]["4X"] == 66.0
    assert ui_text.in_place_after(up, result) == [
        "The new mode 4X copied the mode showing, so your UserLock2 is on and your Sprocket-1 is resolved there, as in "
        "the mode showing; change them in 4X if they should differ."]
    spec = transfer_case_parallel()
    up = classify(record, replace(spec, modes=spec.modes[1:]))
    result, _, rec = _finished(up, record, modes_removed=["2H"], flags_lost=[("2H", "UserLock2", "suppressed")])
    assert rec.gearbox.modes == ["4H", "N", "4L"]
    assert all("2H" not in m.values and "2H" not in m.modes for m in rec.gearbox.mates)
    assert ui_text.in_place_after(up, result) == [
        "Your own states in 2H went with it: your UserLock2 was suppressed there, and so was any state of your "
        "components particular to it.", "2H was the first mode on record; 4H is now."]
    assert ui_text.in_place_done_pieces(up, result) == ["deleted the mode 2H"]
