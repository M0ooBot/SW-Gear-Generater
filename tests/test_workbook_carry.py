"""W9d package B (ISSUE-1-PLAN §2.5, §2.1 item 8; W9D-INTERFACES.md §7, §9, §14.2): Build again… carries the user's
work. The record's schema 10 (the carry on the new revision's gearbox, a user mate's entities, ``unsaved_at``);
``workbook.update.carry_for`` and ``recorded_old_work``; the question from the record's inventory with its time,
through ``swbuild.plan_carry``'s foresight; the result's sentences on hand-made ``CarryResult``s; the finish's record
and the footer's lines; and the round trip through the window's path on the fake SolidWorks."""

import copy
import json

import pytest

from gear_generator import store


# -- schema 10 -------------------------------------------------------------------------------------------------------


def _carry_entry(**changes):
    entry = store.CarryEntry(
        assembly=r"C:\P\R.SLDASM", read_at="2026-11-17T14:02:00Z", how="open", carried_at="2026-11-17T14:05:00Z",
        revision=[34, 1, 1], states_read=False,
        components=[store.CarriedComponentEntry("Sprocket-1", "Sprocket-1", "part", "", False, ["4L"], "G1"),
                    store.CarriedComponentEntry("Housing-1", "Housing-1", "assembly", "Z20", True, [], "")],
        mates=[store.CarriedMateEntry("Lock3", "Lock3", 16, ["2H", "4H", "N", "4L"], 0, 0)],
        named=[store.CarryNamedEntry("Concentric5", "mate", "part new", ["G1", "its Flank changed", "face", "bore"],
                                     "Concentric5 was on G1's bore, and G1's part is new because its Flank changed")],
        fixed=[store.CarryFallbackEntry(["Sprocket-8"], ["Lock8", "Lock9"], ["Coincident7"], "tie", ["G1", "2H"])],
        stopped="", unsaved_at=1763400000.5)
    for key, value in changes.items():
        setattr(entry, key, value)
    return entry


def _record(carry=None, entities=True):
    from test_store import modes_record
    record = modes_record(r"C:\P\R.xlsx")
    record.gearbox.carry = carry
    record.gearbox.user_work = store.UserWorkEntry(
        read_at="2026-11-17T14:05:00Z", assembly=record.gearbox.assembly, revision=[34, 1, 1],
        components=[store.UserComponentEntry("Sprocket-1", "part", False, 0, 2)],
        mates=[store.UserMateEntry("Lock3", "lock", 16, [["app", "G1"], ["user", "Sprocket-1"]], ["2H"], 0, True,
                                   True, [["app", "G1", "whole", ""], ["user", "Sprocket-1", "whole", ""]]
                                   if entities else [])])
    return record


def test_schema_10_keeps_the_carry_and_each_mates_entities_and_round_trips_byte_for_byte():
    record = _record(_carry_entry())
    text = store.link_record_to_json(record)
    raw = json.loads(text)
    assert store._W9C_LINK_SCHEMA == 9 and raw["link_schema_version"] == store.LINK_SCHEMA_VERSION == 10
    assert raw["gearbox"]["carry"]["components"][0] == {"name": "Sprocket-1", "was": "Sprocket-1", "kind": "part",
                                                        "configuration": "", "fixed": False, "suppressed_in": ["4L"],
                                                        "anchor": "G1"}
    assert raw["gearbox"]["carry"]["unsaved_at"] == 1763400000.5
    assert raw["gearbox"]["user_work"]["mates"][0]["entities"][0] == ["app", "G1", "whole", ""]
    back = store.link_record_from_json(text)
    assert back == record and isinstance(back.gearbox.carry, store.CarryEntry)
    assert isinstance(back.gearbox.carry.named[0], store.CarryNamedEntry)
    assert isinstance(back.gearbox.carry.fixed[0], store.CarryFallbackEntry)
    again = store.link_record_to_json(back)               # numbers made floats once, then byte for byte
    assert store.link_record_to_json(store.link_record_from_json(again)) == again
    assert json.loads(again)["gearbox"]["carry"] == raw["gearbox"]["carry"]


def test_a_schema_9_record_reads_forward_with_no_carry_and_no_entities_and_is_written_as_10(tmp_path):
    raw = json.loads(store.link_record_to_json(_record(None, entities=False)))
    del raw["gearbox"]["carry"]
    for mate in raw["gearbox"]["user_work"]["mates"]:
        del mate["entities"]
    raw["link_schema_version"] = 9
    target = tmp_path / "R.workbook.json"
    target.write_text(json.dumps(raw))
    first = store.read_link_record(str(tmp_path / "R.xlsx"))
    assert first.schema_version == 10 and first.gearbox.carry is None
    assert all(m.entities == [] for m in first.gearbox.user_work.mates)
    first.workbook = str(tmp_path / "R.xlsx")
    store.save_link_record(first, str(target))
    assert json.loads(target.read_text())["link_schema_version"] == 10
    assert store.read_link_record(str(tmp_path / "R.xlsx")) == first


def test_a_w9c_era_reader_refuses_schema_10_with_its_sentence_and_leaves_the_file_byte_identical(tmp_path,
                                                                                                 monkeypatch):
    record = _record(_carry_entry())
    record.workbook = str(tmp_path / "RangeBox.xlsx")
    target = tmp_path / "RangeBox.workbook.json"
    target.write_text(store.link_record_to_json(record))
    before = target.read_bytes()
    monkeypatch.setattr(store, "LINK_SCHEMA_VERSION", 9)                 # a W9c-era reader
    for read in (store.read_link_record, store.open_link_record):
        with pytest.raises(store.UnknownSchema) as caught:
            read(str(tmp_path / "RangeBox.xlsx"))
        assert str(caught.value) == ("The record of what was built, RangeBox.workbook.json, cannot be read: it was "
                                     "written by a newer Gear Generator (schema 10, this one reads 9). It is left "
                                     "alone, so Build and Update SolidWorks wait.")
    with pytest.raises(store.UnknownSchema):
        store.save_link_record(record, str(target))
    assert target.read_bytes() == before and sorted(p.name for p in tmp_path.iterdir()) == ["RangeBox.workbook.json"]


@pytest.mark.parametrize("change, match", [
    (lambda c: c.__setitem__("how", "peeked"), r"gearbox\.carry\.how is 'peeked'"),
    (lambda c: c.__setitem__("components", [{"name": "S", "kind": "C:\\x.SLDPRT"}]), r"not part or assembly"),
    (lambda c: c.__setitem__("components", "Sprocket-1"), r"CarriedComponentEntry entries are not a list"),
    (lambda c: c.__setitem__("mates", [{"name": "M", "on": "2H"}]), r"CarriedMateEntry\.on is not List\[str\]"),
    (lambda c: c.__setitem__("named", [{"item": "M", "subjects": [1]}]), r"CarryNamedEntry\.subjects"),
    (lambda c: c.__setitem__("fixed", [{"why": 3}]), r"CarryFallbackEntry\.why"),
    (lambda c: c.__setitem__("unsaved_at", "soon"), r"CarryEntry\.unsaved_at is not float"),
])
def test_a_damaged_carry_is_refused_naming_it(change, match):
    raw = json.loads(store.link_record_to_json(_record(_carry_entry())))
    change(raw["gearbox"]["carry"])
    with pytest.raises(store.StoreError, match=match):
        store.link_record_from_json(json.dumps(raw))


@pytest.mark.parametrize("entity", [["app", "G1", "whole"], ["gear", "G1", "whole", ""], ["app", "G1", "solid", ""]])
def test_a_damaged_entity_is_refused_naming_its_mate(entity):
    raw = json.loads(store.link_record_to_json(_record(None)))
    raw["gearbox"]["user_work"]["mates"][0]["entities"] = [entity]
    with pytest.raises(store.StoreError, match=r"user_work\.mates\[0\] \('Lock3'\) has an entity"):
        store.link_record_from_json(json.dumps(raw))


def test_unsaved_at_goes_once_the_new_assembly_on_disk_is_newer_or_gone_and_stays_otherwise():
    for seen, kept in ((1763400000.5, True), (1763399000.0, True), (1763400001.0, False), (None, False)):
        record = _record(_carry_entry())
        record.unsaved = {r"C:\P\Gear_m1.5_N17.SLDPRT": 5.0}

        def mtime(path, seen=seen):
            if path == record.gearbox.assembly:
                if seen is None:
                    raise FileNotFoundError(path)
                return seen
            return 5.0
        dropped = store.clear_saved(record, mtime)
        assert (record.gearbox.carry.unsaved_at == 1763400000.5) is kept and dropped is (not kept)
        assert (store.carry_unsaved(record) is not None) is kept
        assert record.unsaved == {r"C:\P\Gear_m1.5_N17.SLDPRT": 5.0}     # LinkRecord.unsaved is not the carry's


def test_the_spelled_words_are_swbuilds():
    swbuild = pytest.importorskip("gear_generator.swbuild")
    if not hasattr(swbuild, "OLD_UNREAD"):
        pytest.skip("waiting on package A's shapes commit")
    assert store.CARRY_HOWS == (swbuild.OLD_OPEN, swbuild.OLD_READ_ONLY, swbuild.OLD_UNREAD)
    assert set(store._ENTITY_KINDS) == {swbuild.ENTITY_WHOLE, swbuild.ENTITY_FEATURE, swbuild.ENTITY_PLANE,
                                        swbuild.ENTITY_ORIGIN, swbuild.ENTITY_FACE, swbuild.ENTITY_EDGE,
                                        swbuild.ENTITY_VERTEX, swbuild.ENTITY_UNREAD}


# -- carry_for and recorded_old_work ---------------------------------------------------------------------------------

from dataclasses import replace  # noqa: E402

from gear_generator import findings, swbuild, ui_text  # noqa: E402
from gear_generator.workbook import gearbox, layout, update  # noqa: E402
from test_workbook_in_place_round_trip import Desk, users_work  # noqa: E402,F401
from test_workbook_update import gears  # noqa: E402
from workbook_fixtures import range_box  # noqa: E402


@pytest.fixture
def desk():
    """RangeBox built on the fake, W9a's user work on it read onto the record by a quiet press (Sprocket-1 locked to
    Sun, Housing-1 fixed, a Keyway in Sun's part and a Groove in RangeSlv's)."""
    d = Desk()
    d.build(range_box())
    users_work(d)
    return d


def _again(desk, spec):
    a = desk.a(spec)
    again = gearbox.plan_gearbox(a, desk.record, exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    assert again.refusal == "" and again.name == "RangeBox_r2", again.refusal
    return again


def _carry(desk, again):
    return update.carry_for(desk.record, again, update.old_assembly(desk.record, again),
                            read_sidecar=desk.disk.read_sidecar)


def test_carry_for_maps_every_body_on_record_to_the_new_plan(desk):
    again = _again(desk, gears(range_box(), Sun=dict(flank="arcs")))
    carry = _carry(desk, again)
    box = desk.record.gearbox
    assert carry.old is not None and carry.old.path == box.assembly
    assert [b.old for b in carry.bodies] == ["layout", "Carrier carrier", "Sun", "Planet copy 1", "Planet copy 2",
                                            "Planet copy 3", "Ring", "HighDog", "LowDog", "RangeSlv"]
    by = {b.old: b for b in carry.bodies}
    lay = by["layout"]
    assert (lay.old_name, lay.handle, lay.same_file, lay.why_new) == (
        box.layout_component, "layout", False, "its layout part is new with every revision")
    assert lay.names == lay.old_names == ("Input Axis", "Carrier Axis", "Ring Axis", "Output Axis")
    carrier = by["Carrier carrier"]
    assert (carrier.handle, carrier.same_file, carrier.why_new) == ("carrier1", False,
                                                                    "its carrier part is new with this revision")
    assert carrier.names[0] == "Carrier Axis" and "Planet copy 2 Axis" in carrier.names
    assert carrier.old_names == carrier.names
    sun = by["Sun"]
    assert (sun.handle, sun.same_file, sun.why_new) == ("gear1", False, "its Flank changed")
    sun_job = next(j for j in again.build if "Sun" in j.gear_ids)
    assert sun.names == swbuild.plan_features(sun_job.plan) and "Gear Axis" in sun.old_names
    for k in (1, 2, 3):                                  # planet copy k to copy k, the very file reused
        planet = by[f"Planet copy {k}"]
        assert (planet.old_name, planet.handle, planet.same_file, planet.why_new) == (
            f"gear2c{k}-1", f"gear2c{k}", True, "")
    assert carry.modes == ("H", "N", "L") and carry.first == "H" and carry.written_on == tuple(box.solidworks)
    assert box.assembly in carry.app_files and box.layout in carry.app_files
    assert all(any(store.same_path(p.path, f) for f in carry.app_files) for p in desk.record.parts)
    assert box.carriers[0].path in carry.app_files


def test_carry_for_says_why_each_new_part_is_new_and_names_a_body_the_revision_lacks(desk):
    again = _again(desk, gears(range_box(), Sun=dict(face_width="12", bore="8"), Ring=dict(face_width="12")))
    by = {b.old: b for b in _carry(desk, again).bodies}
    assert by["Sun"].why_new == "its Face width and Bore changed" and by["Ring"].why_new == "its Face width changed"
    renamed = _again(desk, gears(range_box(), Sun=dict(flank="arcs", part_name="SunX")))
    assert {b.old: b for b in _carry(desk, renamed).bodies}["Sun"].why_new == "its Part name and Flank changed"
    sun_part = next(p.path for p in desk.record.parts if "Sun" in p.gears)
    for why, said in ((gearbox.UNSAVED, "it had changes from Update SolidWorks that were not saved"),
                      (gearbox.MISMATCHED, "it did not hold what the record says, as the last job in SolidWorks found")):
        made = replace(again, made_new=(gearbox.MadeNew(("Sun",), sun_part, again.part_of["Sun"], why),))
        assert {b.old: b for b in _carry(desk, made).bodies}["Sun"].why_new == said
    # A gear the new plan has no handle for: on record still, handle "" and no reason.
    gone = replace(again, handles={h: g for h, g in again.handles.items() if g != "HighDog"})
    high = {b.old: b for b in _carry(desk, gone).bodies}["HighDog"]
    assert (high.handle, high.same_file, high.why_new, high.names) == ("", False, "", ())


def test_carry_for_is_none_for_any_other_build(desk):
    again = _again(desk, gears(range_box(), Sun=dict(flank="arcs")))
    assert update.carry_for(desk.record, again, None) is None
    assert update.carry_for(None, again, update.old_assembly(desk.record, again)) is None


def test_recorded_old_work_is_the_inventory_with_its_time_and_says_what_it_cannot_know(desk):
    entry = desk.record.gearbox.user_work
    work = update.recorded_old_work(desk.record)
    assert (work.read_at, work.assembly, work.how, work.active) == (entry.read_at, desk.record.gearbox.assembly,
                                                                    swbuild.OLD_OPEN, "")
    assert work.modes == ("H", "N", "L") and work.app_frames == ()
    assert [(c.name, c.kind, c.fixed, c.state) for c in work.components] == [("Sprocket-1", "part", False, 2),
                                                                             ("Housing-1", "part", True, 2)]
    assert all(c.configurations is None and c.frame is not None for c in work.components)
    lock = work.mates[0]
    assert (lock.name, lock.on) == ("Lock3", ("H", "N", "L"))
    # A schema 9 inventory (no entities): a lock's are whole components by what a lock is.
    assert [(e.what, e.owner, e.kind) for e in lock.entities] == [("app", "Sun", "whole"), ("user", "Sprocket-1", "whole")]
    rec = copy.deepcopy(desk.record)
    rec.gearbox.user_work.mates[0].kind = "other"
    assert {e.kind for e in update.recorded_old_work(rec).mates[0].entities} == {swbuild.ENTITY_UNREAD}
    assert {e.unread for e in update.recorded_old_work(rec).mates[0].entities} == {update.UNKNOWN_ENTITY}
    # A schema 10 inventory keeps them as read.
    rec.gearbox.user_work.mates[0].entities = [["app", "Sun", "face", ""], ["user", "Sprocket-1", "feature", "Axis1"]]
    assert [(e.what, e.owner, e.kind, e.feature) for e in update.recorded_old_work(rec).mates[0].entities] == [
        ("app", "Sun", "face", ""), ("user", "Sprocket-1", "feature", "Axis1")]
    rec.gearbox.user_work = None
    assert update.recorded_old_work(rec) is None


def test_an_updates_inventory_keeps_each_mates_entities():
    mate = swbuild.UserMate("Lock3", swbuild.USER_LOCK, 16, (("app", "Sun"), ("user", "Sprocket-1")), ("H",),
                            entities=(("app", "Sun", "whole", ""), ("user", "Sprocket-1", "whole", "")))
    entry = update.user_work_entry(swbuild.UserWork(read_at="2026-11-17T14:02:00Z", mates=[mate]), assembly="R.SLDASM")
    assert entry.mates[0].entities == [["app", "Sun", "whole", ""], ["user", "Sprocket-1", "whole", ""]]
