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
