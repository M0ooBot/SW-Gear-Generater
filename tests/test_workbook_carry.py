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


# -- the question (§9.1) ---------------------------------------------------------------------------------------------

SUN_FLANK = dict(Sun=dict(flank="arcs"))
OPEN_FIRST = ("open RangeBox.SLDASM in SolidWorks before you press, and it is read as it stands there.")


@pytest.fixture
def carrying(monkeypatch):
    """The W9d gates a plain carry of RangeBox's user work needs, as if M9 had set them on the fake's 2026."""
    for name, value in (("CARRY_INSERTS", True), ("CARRY_REMAKE_KINDS", ("lock", "coincident", "distance")),
                        ("REFERENCED_CONFIGURATION_READ", True), ("CARRY_INSERTS_IN_A_CONFIGURATION", True)):
        monkeypatch.setattr(findings, f"{name}_ON_2026", value)


def _fore(desk, spec_changes=SUN_FLANK, record=None, again=None, plan=None, spec=None):
    again = again or _again(desk, spec or gears(range_box(), **spec_changes))
    record = record or desk.record
    made = (lambda *a, **k: plan) if plan is not None else None
    return update.carry_foresight(record, again, plan_carry=made, read_sidecar=desk.disk.read_sidecar), again


def _said(desk, **kw):
    fore, again = _fore(desk, **kw)
    return ui_text.carry_sentence(fore, again)


def _at(desk):
    return ui_text.read_time(desk.record.gearbox.user_work.read_at)


def test_with_carry_inserts_unset_the_question_says_w9as_clause_led_by_that_finding(desk):
    said = _said(desk)
    assert said == ("Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 "
                    "(findings.CARRY_INSERTS_ON_2026), so as read at " + _at(desk) + ", your Sprocket-1, Housing-1 "
                    "and Lock3 stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part "
                    "replaces; RangeBox_r2 has none of them, nor anything added since. Your Groove in Sleeve_m1.25_N17 "
                    "comes with that part, which RangeBox_r2 reuses.")


def test_with_no_version_on_record_the_question_says_the_mixed_form(desk, monkeypatch):
    monkeypatch.setattr(findings, "CARRY_INSERTS_ON_2026", True)
    record = copy.deepcopy(desk.record)
    record.gearbox.solidworks, record.gearbox.user_work.revision = [], []
    said = _said(desk, record=record)
    assert said == ("Whether RangeBox_r2 takes your work depends on the SolidWorks in use: Gear Generator has been "
                    "shown to do so on SolidWorks 2026, not yet on SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024), "
                    "and the press reads which it runs on. The press reads RangeBox.SLDASM again first, and says "
                    "whatever it cannot carry.")


def test_the_question_says_what_is_carried_and_what_is_named_as_read_with_its_time(desk, carrying, monkeypatch):
    said = _said(desk)
    at = _at(desk)
    assert "carried only if" not in said                    # both configuration findings set: nothing to say
    assert said.startswith(
        f"As read at {at}, RangeBox_r2 takes your Sprocket-1 and Housing-1, each where it stands, against the gear it "
        "is mated to where it has one, and makes your Lock3 again on what it joins, on in the modes it was on in. "
        "Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed; "
        "RangeBox.SLDASM and that file keep it. Your Groove in Sleeve_m1.25_N17 comes with that part, which "
        "RangeBox_r2 reuses."), said
    assert said.endswith(
        "RangeBox_r2 is saved as built, and holds what it carries unsaved: save it in SolidWorks to keep them. The "
        "press reads RangeBox.SLDASM again first, and says whatever it cannot carry. " + ui_text.CARRY_STANDING)
    # A kind not yet shown: its mates named with the finding, grouped (§9.1's gate clause).
    monkeypatch.setattr(findings, "CARRY_REMAKE_KINDS_ON_2026", ("coincident",))
    said = _said(desk)
    assert ("Gear Generator has not yet been shown to make lock mates again in a new revision on SolidWorks 2026 "
            "(findings.CARRY_REMAKE_KINDS_ON_2026), so Lock3 is not made again.") in said
    assert "makes your Lock3" not in said


def test_a_file_whose_configurations_the_record_does_not_keep_is_said_as_may(desk, carrying, monkeypatch):
    monkeypatch.setattr(findings, "CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026", None)
    assert ("Sprocket-1 and Housing-1 are carried only if each one's file has a single configuration: Gear Generator "
            "has not yet been shown to insert a component in one of several on SolidWorks 2026 "
            "(findings.CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026), and the press reads which.") in _said(desk)


def _plan(components=(), mates=(), named=()):
    return swbuild.CarryPlan(tuple(components), tuple(mates), tuple(named), (), ())


def _item(name, anchor="Sun", kind="part"):
    frame = (layout.IDENTITY, (0.0, 0.0, 0.0))
    return swbuild.CarryPlanItem(swbuild.OldComponent(name, name + ".SLDPRT", kind, False, 0, 2, frame), anchor,
                                 frame, 0)


def _mate_item(name):
    return swbuild.CarryMateItem(swbuild.OldMate(name, 16, "MateLock", 0, False, (), ()), 0, ())


def test_the_question_names_each_item_by_its_reason_and_groups_a_finding_not_yet_set(desk, carrying):
    named = [swbuild.CarryNamed("Concentric5", "mate", swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "face",
                                                                              "bore")),
             swbuild.CarryNamed("Concentric8", "mate", swbuild.WHY_UNMEASURED,
                                ("concentric", "CARRY_REMAKE_KINDS_ON_2026", "2026")),
             swbuild.CarryNamed("Concentric9", "mate", swbuild.WHY_UNMEASURED,
                                ("concentric", "CARRY_REMAKE_KINDS_ON_2026", "2026")),
             swbuild.CarryNamed("Width1", "mate", swbuild.WHY_KIND, ("width",))]
    plan = _plan([_item("Sprocket-1"), _item("Sprocket-2"), _item("Chain-1"), _item("Housing-1")],
                 [_mate_item(f"Lock{k}") for k in range(8)], named)
    said = _said(desk, plan=plan)
    assert said.startswith(
        f"As read at {_at(desk)}, RangeBox_r2 takes your Sprocket-1, Sprocket-2, Chain-1 and 1 other component, each "
        "where it stands against the gear it is mated to, and makes your 8 mates again on what they join, each on in "
        "the modes it was on in. Gear Generator has not yet been shown to make concentric mates again in a new "
        "revision on SolidWorks 2026 (findings.CARRY_REMAKE_KINDS_ON_2026), so Concentric8 and Concentric9 are not "
        "made again. Concentric5 was on Sun's bore, and Sun's part is new because its Flank changed, so it is not "
        "made again. Width1 is a width mate, which Gear Generator does not make again. "), said


def test_a_part_made_new_only_because_of_the_user_says_how_to_reuse_it(desk, carrying):
    again = _again(desk, gears(range_box(), **SUN_FLANK))
    sun_part = next(p.path for p in desk.record.parts if "Sun" in p.gears)
    record = copy.deepcopy(desk.record)
    mismatched = replace(again, made_new=(gearbox.MadeNew(("Sun",), sun_part, again.part_of["Sun"],
                                                          gearbox.MISMATCHED),))
    fore = update.carry_foresight(record, mismatched, read_sidecar=desk.disk.read_sidecar)
    assert ("Gear_m1.25_N29 is new only because it does not hold what the record says: answer No, make the workbook "
            "ask what that part holds in SolidWorks, and Build again… reuses it with your Keyway."
            ) in ui_text.carry_sentence(fore, mismatched)
    record.gearbox.user_work.problems = [store.UserProblemEntry("value", "…", [], [store.ValueEditEntry(
        "Gear_m1.25_N29.SLDPRT", "Bore Diameter", "12", "10", "10", "", "Gears!J2")])]
    fore = update.carry_foresight(record, mismatched, read_sidecar=desk.disk.read_sidecar)
    said = ui_text.carry_sentence(fore, mismatched)
    assert ("Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because it did not hold what the "
            "record says, as the last job in SolidWorks found; RangeBox.SLDASM and that file keep it. "
            "Gear_m1.25_N29 is new only because it holds Bore Diameter 12 where the workbook asks 10: answer No, type "
            "12 in Gears!J2, and Build again… reuses that part with your Keyway.") in said, said
    unsaved = replace(again, made_new=(gearbox.MadeNew(("Sun",), sun_part, again.part_of["Sun"], gearbox.UNSAVED),))
    fore = update.carry_foresight(desk.record, unsaved, read_sidecar=desk.disk.read_sidecar)
    assert ("which Sun's new part replaces because it had changes from Update SolidWorks that were not saved; "
            "RangeBox.SLDASM and that file keep it. Gear_m1.25_N29 is new only because Update SolidWorks left it "
            "unsaved: answer No and save it in SolidWorks first, and Build again… reuses it with your Keyway."
            ) in ui_text.carry_sentence(fore, unsaved)


def test_a_schema_9_inventory_says_may_for_a_mate_whose_entities_it_never_kept(desk, carrying):
    record = copy.deepcopy(desk.record)
    entry = record.gearbox.user_work
    entry.mates += [store.UserMateEntry("UserAxis4", "other", 0, [["app", "Sun"], ["user", "Sprocket-1"]], ["H"]),
                    store.UserMateEntry("Dist2", "other", 5, [["user", "Sprocket-1"], ["user", "Housing-1"]], ["H"])]
    said = _said(desk, record=record)
    assert ("Your UserAxis4 joins Sun, whose part is new: a mate on one of its faces or edges is not made again, and "
            "the press reads which it is.") in said, said
    assert ("The record does not say what your Dist2 is on, so the press reads it and makes it again where it can."
            ) in said
    assert "would not describe UserAxis4" not in said and "would not describe Dist2" not in said


def test_a_lightweight_or_suppressed_component_as_read_is_said_with_what_to_do(desk, carrying):
    record = copy.deepcopy(desk.record)
    record.gearbox.user_work.components[0].state = 1
    record.gearbox.user_work.components[1].state = 0
    said = _said(desk, record=record)
    assert ("Sprocket-1 was lightweight as read, so its mate cannot be read through it: set it resolved in SolidWorks "
            "before you press, or it is not made again.") in said, said
    assert ("Housing-1 was suppressed in the mode RangeBox.SLDASM showed, as read; if SolidWorks cannot say where it "
            "stands there, it is not carried: show a mode where it is resolved before you press.") in said


@pytest.mark.parametrize("settled, clause", [
    ((), "it is not read: Gear Generator has not yet been shown to read which SolidWorks last saved a file "
         "(findings.FILE_VERSION_READ_ON_2026), read which SolidWorks last saved each file it uses "
         "(findings.DEPENDENCIES_READ_ON_2026) and close it unchanged after reading it "
         "(findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026), so nothing of yours would be carried: "),
    (("FILE_VERSION_READ",), "it is not read: Gear Generator has not yet been shown to read which SolidWorks last "
                             "saved each file it uses (findings.DEPENDENCIES_READ_ON_2026) and close it unchanged "
                             "after reading it (findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026), so nothing of "
                             "yours would be carried: "),
    (("FILE_VERSION_READ", "DEPENDENCIES_READ"),
     "it is not read: Gear Generator has not yet been shown to close it unchanged after reading it "
     "(findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026), so nothing of yours would be carried: "),
    (("FILE_VERSION_READ", "DEPENDENCIES_READ", "OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN"),
     "Gear Generator reads it then only when it and every file it uses were last saved by this SolidWorks (a file "
     "saved since on another SolidWorks is not read) and nothing else is open in SolidWorks "
     "(findings.OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_2026); otherwise nothing of yours would be carried: "),
    (("FILE_VERSION_READ", "DEPENDENCIES_READ", "OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN", "OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS"),
     "Gear Generator reads it then only when it and every file it uses were last saved by this SolidWorks (a file "
     "saved since on another SolidWorks is not read) and nothing but Gear Generator's own files is open in "
     "SolidWorks; otherwise nothing of yours would be carried: "),
])
def test_the_not_open_clause_names_the_condition_that_holds_a_closed_old_assembly_unread(desk, carrying, monkeypatch,
                                                                                          settled, clause):
    for name in settled:
        monkeypatch.setattr(findings, f"{name}_ON_2026", "a route" if "READ" in name and "ONLY" not in name else True)
    assert f"If RangeBox.SLDASM is not open in SolidWorks when you press, {clause}{OPEN_FIRST}" in _said(desk)


def test_the_states_clause_goes_once_a_clean_route_reads_them(desk, carrying, monkeypatch):
    states = ("Your components take, in every mode of RangeBox_r2, the state they have in the mode RangeBox.SLDASM "
              "shows when you press: whether you suppressed one in another mode cannot be read without changing "
              "RangeBox.SLDASM.")
    assert states in _said(desk)
    monkeypatch.setattr(findings, "COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_2026", "GetComponentSuppressionState")
    assert states not in _said(desk)


def test_a_mode_renamed_says_what_stays_and_what_the_new_mode_takes(desk, carrying):
    from gear_generator.workbook.model import Mode
    spec = gears(range_box(), **SUN_FLANK)
    spec = replace(spec, modes=tuple(replace(m, name="Low") if m.name == "L" else m for m in spec.modes))
    said = _said(desk, spec=spec)
    assert ("RangeBox_r2 has no mode L: what your items were in L stays in RangeBox.SLDASM. Its new mode Low takes "
            "what they were in H.") in said, said
    assert Mode                                               # the Modes row is the model's


def test_with_nothing_of_the_users_on_record_the_question_says_the_press_reads_first(desk, carrying):
    record = copy.deepcopy(desk.record)
    record.gearbox.user_work = None
    said = _said(desk, record=record)
    assert said.startswith("Anything you added to RangeBox.SLDASM in SolidWorks the press reads first and carries "
                           "into RangeBox_r2 where it can, saying whatever it cannot. If RangeBox.SLDASM is not open "
                           "in SolidWorks when you press, it is not read:"), said


def test_a_foresight_that_raises_says_only_that_the_press_reads_and_carries_what_it_can(desk, carrying):
    def boom(*a, **k):
        raise RuntimeError("no")
    fore = update.carry_foresight(desk.record, _again(desk, gears(range_box(), **SUN_FLANK)), plan_carry=boom,
                                  read_sidecar=desk.disk.read_sidecar)
    assert fore.plan is None
    assert ui_text.carry_sentence(fore, _again(desk, gears(range_box(), **SUN_FLANK))).startswith(
        f"As read at {_at(desk)}, RangeBox.SLDASM held your Sprocket-1, Housing-1 and Lock3: the press reads it again "
        "first and carries into RangeBox_r2 what it can, saying whatever it cannot.")


def test_the_whole_question_carries_the_clause_after_the_builds_own(desk, carrying):
    spec = gears(range_box(), **SUN_FLANK)
    up = update.classify(desk.record, desk.a(spec), exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    again = _again(desk, spec)
    question = ui_text.build_again_question(up, again, record=desk.record)
    assert question.startswith("Gear_m1.25_N29 (Sun): Flank changed from involute to arcs")
    assert f" As read at {_at(desk)}, RangeBox_r2 takes your Sprocket-1 and Housing-1" in question
    assert question.endswith(ui_text.CARRY_STANDING)


# -- the result (§9.2) and each reason (§9.3) --------------------------------------------------------------------------

FRAME = (layout.IDENTITY, (0.0, 0.0, 0.0))
OLD = r"C:\Out\RangeBox.SLDASM"


def _work(components=("Sprocket-1", "Sprocket-2", "Chain-1", "Housing-1"), mates=8, **changes):
    comps = [swbuild.OldComponent(n, f"C:\\Parts\\{n.split('-')[0]}.SLDPRT", "part", n.startswith("Housing"), 0, 2,
                                  FRAME) for n in components]
    work = swbuild.OldWork("2026-11-17T14:02:00Z", OLD, swbuild.OLD_OPEN, "H", ("H", "N", "L"), comps,
                           [swbuild.OldMate(f"M{k}", 16, "MateLock", 0, False, (), ()) for k in range(mates)], ())
    for key, value in changes.items():
        setattr(work, key, value)
    return work


def _done(work=None, **changes):
    work = work if work is not None else _work()
    done = swbuild.CarryResult(work, inserted=[(c.name, c.name) for c in work.components],
                               remade=[(m.name, m.name, ("H", "N", "L")) for m in work.mates[:-1]], unsaved=True)
    for key, value in changes.items():
        setattr(done, key, value)
    return done


class _Again:
    name = "RangeBox_r2"

    class modes_plan:                                         # noqa: N801 - a stand-in for the plan's ModesPlan
        steps = tuple(type("Step", (), {"name": m})() for m in ("H", "N", "L"))


def _status(done, anchors=None):
    return ui_text.carried_status(type("R", (), {"carry": done})(), _Again(), OLD, anchors)


def test_the_result_says_what_was_carried_unsaved_and_to_save_it():
    anchors = {"Sprocket-1": "Sun", "Sprocket-2": "Sun", "Chain-1": "Sun", "Housing-1": "RangeSlv"}
    named = [swbuild.CarryNamed("M7", "mate", swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "face", "bore"))]
    said = _status(_done(named=named), anchors)
    assert said.startswith(
        "Carried into RangeBox_r2, unsaved: your Sprocket-1, Sprocket-2, Chain-1 and 1 other component, each where it "
        "stood against the gear it is mated to, and 7 of your 8 mates, each on in the modes it was on in. M7 was on "
        "Sun's bore, and Sun's part is new because its Flank changed, so it is not made again. Your components were "
        "placed where they stood in H, the mode RangeBox.SLDASM showed; a floating one that stood elsewhere in "
        "another mode stands, in RangeBox_r2, where it stood in H. Your components take in every mode the state they "
        "had in H, the mode RangeBox.SLDASM showed: their states in N and L could not be read without changing it. "
        + ui_text.CARRY_STANDING + " A part of yours made in context of RangeBox.SLDASM still refers to its parts."), said
    assert said.endswith(" Save RangeBox_r2 in SolidWorks to keep what was carried.")
    every = _done(remade=[(m.name, m.name, ("H",)) for m in _work().mates])
    assert "and your 8 mates, each on in the modes it was on in." in _status(every)
    assert _status(None) == ""


@pytest.mark.parametrize("why, subjects, clause", [
    (swbuild.WHY_KIND, ("width",), "M1 is a width mate, which Gear Generator does not make again"),
    (swbuild.WHY_UNMEASURED, ("concentric", "CARRY_REMAKE_KINDS_ON_2024", "2024"),
     "M1 is a concentric mate, which Gear Generator has not yet been shown to make again in a new revision on "
     "SolidWorks 2024 (findings.CARRY_REMAKE_KINDS_ON_2024)"),
    (swbuild.WHY_UNMEASURED, ("face", "PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024", "2024"),
     "M1 is on a face, which Gear Generator has not yet been shown to find again in a new revision on SolidWorks "
     "2024 (findings.PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024)"),
    (swbuild.WHY_UNMEASURED, ("edge", "PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026", "2026"),
     "M1 is on an edge, which Gear Generator has not yet been shown to find again in a new revision, after its part "
     "is closed and opened again, on SolidWorks 2026 "
     "(findings.PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026)"),
    (swbuild.WHY_UNMEASURED, ("origin", "ORIGIN_ENTITY_READ_ON_2026", "2026"),
     "M1 is on an origin, which Gear Generator has not yet been shown to read an origin as a mate's entity on "
     "SolidWorks 2026 (findings.ORIGIN_ENTITY_READ_ON_2026)"),
    (swbuild.WHY_UNMEASURED, ("gear mate on an app gear", "CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2026", ""),
     "M1 is not made again, which Gear Generator has not yet been shown to make a gear mate on an app gear again in "
     "a new revision on the SolidWorks it runs on (findings.CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2026)"),
    (swbuild.WHY_UNMEASURED, ("leaf", "CARRY_REMAKES_ON_A_LEAF_ON_2026", "2026"),
     "M1 is not made again, which Gear Generator has not yet been shown to make a mate on a part inside a "
     "sub-assembly of yours again on SolidWorks 2026 (findings.CARRY_REMAKES_ON_A_LEAF_ON_2026)"),
    (swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "face", "bore"),
     "M1 was on Sun's bore, and Sun's part is new because its Flank changed"),
    (swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "edge", ""),
     "M1 was on an edge of Sun, and Sun's part is new because its Flank changed"),
    (swbuild.WHY_GONE, ("gear", "G5"), "M1 was on G5, which RangeBox_r2 does not have"),
    (swbuild.WHY_GONE, ("shaft", "Output"), "M1 was on the layout's Output Axis, and RangeBox_r2 has no shaft Output"),
    (swbuild.WHY_GONE, ("feature", "Mid Plane"),
     "M1 was on Mid Plane in an app part, which that part in RangeBox_r2 does not have"),
    (swbuild.WHY_ASSEMBLY_FEATURE, ("Plane1",),
     "M1 is on Plane1, a feature you made in RangeBox.SLDASM, which is not carried"),
    (swbuild.WHY_NOT_CARRIED, ("Bracket-1",), "M1 joins Bracket-1, which is not carried"),
    (swbuild.WHY_UNREAD, ("",), "SolidWorks would not describe M1 wholly"),
    (swbuild.WHY_LIGHTWEIGHT, ("Sprocket-4",),
     "M1 is on Sprocket-4, which was lightweight in RangeBox.SLDASM, so what it joins could not be read"),
    (swbuild.WHY_LEAF, ("Drive-1",),
     "M1 is on a part inside your sub-assembly Drive-1, which Gear Generator does not make again"),
    (swbuild.WHY_NOT_FOUND, ("face", "Sprocket-1", "Sprocket.SLDPRT"),
     "M1's face of Sprocket-1 could not be found again in Sprocket.SLDPRT"),
    (swbuild.WHY_DIFFERS, ("entities",), "M1 made again read otherwise than it was (its entities), so it was taken out "
                                         "again"),
    (swbuild.WHY_OLD_UNREAD, ("it was not open in SolidWorks",),
     "RangeBox.SLDASM was not read (it was not open in SolidWorks)"),
])
def test_each_reason_a_mate_is_not_carried_has_its_clause(why, subjects, clause):
    named = swbuild.CarryNamed("M1", "mate", why, subjects)
    assert ui_text.carry_named_clause(named, name="RangeBox_r2", old="RangeBox.SLDASM") == clause


@pytest.mark.parametrize("why, subjects, clause", [
    (swbuild.WHY_NO_FILE, ("Part1^RangeBox.SLDPRT", "virtual"),
     "Part1^RangeBox-1 is a virtual component, with no file of its own, so it is not carried"),
    (swbuild.WHY_NO_FILE, ("Bracket.SLDPRT", ""), "Part1^RangeBox-1's file Bracket.SLDPRT is not on disk, so it is not "
                                                 "carried"),
    (swbuild.WHY_NO_FILE, ("", ""), "Part1^RangeBox-1 has no file SolidWorks would name, so it is not carried"),
    (swbuild.WHY_CONFIGURATION, ("Sprocket-1", "Z20", "Z15"),
     "Sprocket-1 uses its configuration Z20, not Z15 which its file opens in, and Gear Generator cannot carry it in "
     "Z20 here, so it is not carried"),
    (swbuild.WHY_CONFIGURATION, ("Sprocket-1", "", ""), "Sprocket-1's configuration could not be read, so it is not "
                                                       "carried"),
    (swbuild.WHY_NO_FRAME, ("Sprocket-7", "H"),
     "Sprocket-7 is suppressed in H, the mode RangeBox.SLDASM showed, and SolidWorks would not say where it stands, so "
     "it is not carried"),
    (swbuild.WHY_UNMEASURED, ("insert", "CARRY_INSERTS_ON_2024", "2024"),
     "Part1^RangeBox-1 is not carried, which Gear Generator has not yet been shown to carry your work into a new "
     "revision on SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024)"),
    (swbuild.WHY_UNMEASURED, ("sub-assembly", "SUBASSEMBLY_READ_ONLY_INSERT_ON_2026", "2026"),
     "Part1^RangeBox-1 is not carried, which Gear Generator has not yet been shown to insert a sub-assembly of yours "
     "into a new revision on SolidWorks 2026 (findings.SUBASSEMBLY_READ_ONLY_INSERT_ON_2026)"),
    (swbuild.WHY_UNMEASURED, ("configuration", "CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026", "2026"),
     "Part1^RangeBox-1 is not carried, which Gear Generator has not yet been shown to insert a component in a "
     "configuration of its file's several on SolidWorks 2026 (findings.CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026)"),
])
def test_each_reason_a_component_is_not_carried_has_its_clause(why, subjects, clause):
    named = swbuild.CarryNamed("Part1^RangeBox-1", "component", why, subjects)
    assert ui_text.carry_named_clause(named, name="RangeBox_r2", old="RangeBox.SLDASM") == clause


def test_a_sub_assembly_whose_open_marks_it_is_said_so(monkeypatch):
    monkeypatch.setattr(findings, "SUBASSEMBLY_OPEN_MARKS_ON_2026", True)
    named = swbuild.CarryNamed("Drive-1", "component", swbuild.WHY_UNMEASURED,
                               ("sub-assembly", "SUBASSEMBLY_OPEN_MARKS_ON_2026", "2026"))
    assert ui_text.carry_named_clause(named) == (
        "your sub-assembly Drive-1 is not carried: opening it to insert it marks it as changed in SolidWorks, and Gear "
        "Generator never changes a file of yours")


@pytest.mark.parametrize("fallback, said", [
    (swbuild.CarryFallback(("Sprocket-8",), ("Lock8", "Lock9"), ("Coincident7",), swbuild.FELL_TIE, ("Sun", "H")),
     "Sprocket-8 is fixed where it stood in RangeBox_r2: with your Lock8 and Lock9 made again SolidWorks reads Sun "
     "unable to turn, so those two were not kept; Coincident7 beside them was."),
    (swbuild.CarryFallback(("Sprocket-8",), ("Lock8",), (), swbuild.FELL_TIE, ("Sun", "L")),
     "Sprocket-8 is fixed where it stood in RangeBox_r2: with your Lock8 made again SolidWorks reads Sun unable to "
     "turn in L, so it was not kept."),
    (swbuild.CarryFallback(("Sprocket-3", "Chain-1"), ("Lock3",), ("Dist1", "Dist2"), swbuild.FELL_NEW_ERROR,
                           ("Lock3", "46", "0", "L")),
     "Sprocket-3 and Chain-1 are fixed where they stood in RangeBox_r2: with your Lock3 made again it reads error 46 "
     "in L, which it did not in H, the mode RangeBox.SLDASM showed, so it was not kept; Dist1 and Dist2 beside them "
     "were."),
    (swbuild.CarryFallback(("Sprocket-3",), ("Lock3", "Lock4", "Lock5"), (), swbuild.FELL_OVER_DEFINED, ("Lock3",)),
     "Sprocket-3 is fixed where it stood in RangeBox_r2: your Lock3 made again over-defines it, so those 3 were not "
     "kept."),
    (swbuild.CarryFallback(("Sprocket-3",), ("Lock3",), (), swbuild.FELL_OVER_DEFINED, ("",)),
     "Sprocket-3 is fixed where it stood in RangeBox_r2: with your mates made again SolidWorks reads it over-defined, "
     "so it was not kept."),
])
def test_each_cluster_that_fell_back_is_said_with_why(fallback, said):
    assert said in _status(_done(fixed=[fallback]))


def test_the_results_other_sentences_each_as_they_apply():
    work = _work(components=("Sprocket-2", "Drive-1"), mates=2)
    work.components[1] = replace(work.components[1], kind="assembly", path="C:\\Parts\\Drive.SLDASM")
    clash = swbuild.Clash(("Sprocket-2", "gear6-1"), ("Sprocket-2", "RangeSlv"), 12.3)
    done = _done(work, same_error=[("M0", 46)], moved=[("Sprocket-2", "L", 2.04)], clashes=[("L", clash)],
                 marked_user=[r"C:\Parts\Sprocket.SLDPRT"])
    said = _status(done)
    for sentence in ("Your M0 was in error in RangeBox.SLDASM and is in RangeBox_r2 too, as it was.",
                     "In L, SolidWorks moved Sprocket-2 2.0 mm from where it was placed when your mates were made "
                     "again.",
                     "In mode L, your Sprocket-2 interferes with RangeSlv (12.3 mm³).",
                     "Your sub-assembly Drive-1 comes over rigid: set it flexible in SolidWorks again if it was.",
                     "SolidWorks reads Sprocket.SLDPRT as changed since it was inserted into RangeBox_r2, though "
                     "nothing in it changed: saving RangeBox_r2 with its parts saves that file again too."):
        assert sentence in said, (sentence, said)
    # With the states read per mode, nothing is said of them; a fixed component is not said to float.
    read = _work(components=("Housing-1",), mates=0, states_route="GetComponentSuppressionState")
    said = _status(_done(read))
    assert "could not be read without changing it" not in said and "a floating one" not in said


def test_a_carry_that_stopped_says_what_it_did_not_get_to():
    done = _done(stopped="SolidWorks would not make UserDist4 again (SolidWorks: AddMate5 answered 2)",
                 skipped="making Sprocket-4's other mates again and checking the assembly")
    said = _status(done)
    assert ("Carrying your work stopped: SolidWorks would not make UserDist4 again (SolidWorks: AddMate5 answered 2), "
            "so it did not get to making Sprocket-4's other mates again and checking the assembly; what was carried "
            "before it is in RangeBox_r2, unsaved, and RangeBox_r2 as built is saved.") in said
    assert "Save RangeBox_r2 in SolidWorks" not in said


def test_nothing_read_a_read_that_marked_and_a_document_left_open_each_say_nothing_was_carried():
    unread = _work(how=swbuild.OLD_UNREAD, unread=["it was not open in SolidWorks, and FILE_VERSION_READ is not set"])
    assert _status(swbuild.CarryResult(unread)) == (
        "RangeBox.SLDASM was not read (it was not open in SolidWorks, and FILE_VERSION_READ is not set), so nothing of "
        "yours was carried; it and your files are as they were. Open RangeBox.SLDASM in SolidWorks before you press "
        "Build again… to carry it.")
    assert _status(swbuild.CarryResult(None, stopped="SolidWorks stopped answering.")) == (
        "RangeBox.SLDASM was not read (SolidWorks stopped answering), so nothing of yours was carried; it and your "
        "files are as they were.")
    marked = _work(marked=[r"C:\Parts\Sprocket.SLDPRT"])
    assert _status(swbuild.CarryResult(marked, stopped="x")) == (
        "Reading RangeBox.SLDASM marked Sprocket.SLDPRT as changed in SolidWorks, which Gear Generator never does on "
        "purpose, so nothing of yours was carried; nothing in it changed, and RangeBox.SLDASM and your files are as "
        "they were on disk.")
    left = _work(left=[r"C:\Parts\Sprocket.SLDPRT"])
    assert _status(swbuild.CarryResult(left, stopped="x")) == (
        "Reading RangeBox.SLDASM left Sprocket.SLDPRT open in SolidWorks, so nothing of yours was carried; close it "
        "without saving.")


def test_the_carry_kind_words_are_the_workers():
    assert ui_text.CARRY_KIND_WORDS == swbuild.CARRY_KIND_WORDS
