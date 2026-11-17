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

from gear_generator import findings, swbuild, swcom, ui_text  # noqa: E402
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
CLOSED_UNREAD = "If RangeBox.SLDASM is closed when you press, nothing is carried: open it in SolidWorks first."
CLOSED_FINDINGS = ("findings.FILE_VERSION_READ_ON_2026, findings.DEPENDENCIES_READ_ON_2026 and "
                   "findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026")
STATES = ("Each component takes, in every mode of RangeBox_r2, its state in the mode RangeBox.SLDASM shows; its other "
          "states cannot be read without changing it.")
FEATURES = ("Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes "
            "with Sleeve_m1.25_N17.")


# The reads the 2026 probes measured (W9D-INTERFACES §8.1), as the findings set them; each test says its own state.
PROBE_READS = {"COMPONENT_STATE_PER_CONFIGURATION_ROUTE": "IConfiguration.GetComponentSuppressionState(Name2)",
               "COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED": True, "FILE_VERSION_READ": "VersionHistory",
               "DEPENDENCIES_READ": "GetDocumentDependencies2", "OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS": True,
               "OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN": True, "SUBASSEMBLY_OPEN_MARKS": False,
               "SUBASSEMBLY_READ_ONLY_INSERT": True, "SUBASSEMBLY_OPEN_MARKS_WHEN_LOADED": False,
               "PERSIST_REFERENCE_ROUTE_FOR_FACES": swcom.PERSIST_ROUTE_R3,
               "PERSIST_REFERENCE_ROUTE_FOR_EDGES": swcom.PERSIST_ROUTE_R3,
               "PERSIST_REFERENCE_SURVIVES_RELOAD": True, "COAXIAL_FACE_READ": True,
               "CARRY_INSERT_MARKS_USER_DOCUMENTS": False}


def _reads(monkeypatch, value=None, **chosen):
    """Every probe read on 2026 at ``value`` (None: not yet measured), those in ``chosen`` at theirs."""
    for name, measured in PROBE_READS.items():
        monkeypatch.setattr(findings, f"{name}_ON_2026", chosen.get(name, measured if value == "measured" else value))


@pytest.fixture
def carrying(monkeypatch):
    """The W9d gates a plain carry of RangeBox's user work needs, as if M9 had set them on the fake's 2026, and every
    probe read None (the state these sentences are pinned in; a test sets the reads it needs)."""
    _reads(monkeypatch)
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


def test_the_question_says_what_is_carried_and_what_is_not_short_with_the_findings_once_at_the_end(desk, carrying,
                                                                                                   monkeypatch):
    said = _said(desk)
    assert said == (
        f"As read at {_at(desk)}, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the "
        f"modes it was on in. {FEATURES} RangeBox_r2 holds what it carries unsaved. {CLOSED_UNREAD} {STATES} "
        f"{ui_text.CARRY_STANDING} (Not yet shown on SolidWorks 2026: {CLOSED_FINDINGS}.)"), said
    assert len(said.split()) < 120                        # 180 words before the review's S3
    # A kind not yet shown: its mates named in one sentence, the finding said once at the end (S3).
    monkeypatch.setattr(findings, "CARRY_REMAKE_KINDS_ON_2026", ("coincident",))
    said = _said(desk)
    assert said.startswith(f"As read at {_at(desk)}, RangeBox_r2 takes your Sprocket-1 and Housing-1. Gear Generator "
                           "has not yet been shown to make lock mates again in a new revision on SolidWorks 2026, so "
                           "Lock3 is not made again. "), said
    assert said.endswith("(Not yet shown on SolidWorks 2026: findings.CARRY_REMAKE_KINDS_ON_2026, "
                         f"{CLOSED_FINDINGS}.)")
    assert said.count("findings.CARRY_REMAKE_KINDS_ON_2026") == 1


def test_with_every_2026_probe_finding_set_the_closed_clause_says_its_conditions(desk, carrying, monkeypatch):
    for name, value in (("FILE_VERSION_READ", "VersionHistory"), ("DEPENDENCIES_READ", "GetDocumentDependencies2"),
                        ("OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN", True),
                        ("COMPONENT_STATE_PER_CONFIGURATION_ROUTE", "GetComponentSuppressionState")):
        monkeypatch.setattr(findings, f"{name}_ON_2026", value)
    said = _said(desk)
    assert ("If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it and its files, those "
            "files are where it says, and nothing else is open.") in said, said
    assert said.endswith("(Not yet shown on SolidWorks 2026: findings.OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_2026.)")
    assert STATES not in said                              # the states route is clean: nothing to say (§9.1)
    monkeypatch.setattr(findings, "OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS_ON_2026", True)
    said = _said(desk)
    assert ("If RangeBox.SLDASM is closed, open it first unless this SolidWorks last saved it and its files, those "
            "files are where it says, and nothing of yours is open.") in said and "Not yet shown" not in said


def test_a_file_whose_configurations_the_record_does_not_keep_is_said_as_may(desk, carrying, monkeypatch):
    monkeypatch.setattr(findings, "CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026", None)
    said = _said(desk)
    assert "Sprocket-1 and Housing-1 are carried only if each file has one configuration." in said
    assert "findings.CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026" in said.rsplit("(Not yet shown", 1)[1]


def _plan(components=(), mates=(), named=()):
    return swbuild.CarryPlan(tuple(components), tuple(mates), tuple(named), (), ())


def _item(name, anchor="Sun", kind="part"):
    frame = (layout.IDENTITY, (0.0, 0.0, 0.0))
    return swbuild.CarryPlanItem(swbuild.OldComponent(name, name + ".SLDPRT", kind, False, 0, 2, frame), anchor,
                                 frame, 0)


def _mate_item(name):
    return swbuild.CarryMateItem(swbuild.OldMate(name, 16, "MateLock", 0, False, (), ()), 0, ())


def test_the_question_says_each_kind_of_reason_once(desk, carrying):
    named = [swbuild.CarryNamed("Concentric5", "mate", swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "face",
                                                                              "bore")),
             swbuild.CarryNamed("Concentric8", "mate", swbuild.WHY_UNMEASURED,
                                ("concentric", "CARRY_REMAKE_KINDS_ON_2026", "2026")),
             swbuild.CarryNamed("Concentric9", "mate", swbuild.WHY_UNMEASURED,
                                ("concentric", "CARRY_REMAKE_KINDS_ON_2026", "2026")),
             swbuild.CarryNamed("Width1", "mate", swbuild.WHY_KIND, ("width",)),
             swbuild.CarryNamed("Lock6", "mate", swbuild.WHY_NOT_CARRIED, ("Bracket-1",)),
             swbuild.CarryNamed("Lock7", "mate", swbuild.WHY_NOT_CARRIED, ("Bracket-1",))]
    plan = _plan([_item("Sprocket-1"), _item("Sprocket-2"), _item("Chain-1"), _item("Housing-1")],
                 [_mate_item(f"Lock{k}") for k in range(8)], named)
    said = _said(desk, plan=plan)
    assert said.startswith(
        f"As read at {_at(desk)}, RangeBox_r2 takes your Sprocket-1, Sprocket-2, Chain-1 and Housing-1 and makes your "
        "8 mates again in the modes each was on in. Gear Generator has not yet been shown to make concentric mates "
        "again in a new revision on SolidWorks 2026, so Concentric8 and Concentric9 are not made again. Lock6 and "
        "Lock7 join Bracket-1, which is not carried, so they are not made again. Concentric5 was on Sun's bore, and "
        "Sun's part is new because its Flank changed, so it is not made again. Width1 is a width mate, which Gear "
        "Generator does not make again. "), said
    five = _plan([_item(n) for n in ("A-1", "B-1", "C-1", "D-1", "E-1")])
    assert "takes your A-1, B-1, C-1 and 2 other components." in _said(desk, plan=five)
    # Foreseeing nothing carried: no save to ask for, no closed-assembly clause (S2).
    nothing = _said(desk, plan=_plan(named=named[:1]))
    assert nothing.startswith(f"As read at {_at(desk)}, nothing of yours in RangeBox.SLDASM would be carried into "
                              "RangeBox_r2.")
    assert "unsaved" not in nothing and "closed" not in nothing and ui_text.CARRY_STANDING not in nothing


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
    assert ("Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (it did not hold what the record says, "
            "as the last job in SolidWorks found); your Groove comes with Sleeve_m1.25_N17. Gear_m1.25_N29 is new only "
            "because it holds Bore Diameter 12 where the workbook asks 10: answer No, type 12 in Gears!J2, and Build "
            "again… reuses that part with your Keyway.") in said, said
    unsaved = replace(again, made_new=(gearbox.MadeNew(("Sun",), sun_part, again.part_of["Sun"], gearbox.UNSAVED),))
    fore = update.carry_foresight(desk.record, unsaved, read_sidecar=desk.disk.read_sidecar)
    assert ("which Sun's new part replaces (it had changes from Update SolidWorks that were not saved); your Groove "
            "comes with Sleeve_m1.25_N17. Gear_m1.25_N29 is new only because Update SolidWorks left it unsaved: answer "
            "No and save it in SolidWorks first, and Build again… reuses it with your Keyway."
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


def test_a_lightweight_component_is_said_once_as_the_condition_it_is(desk, carrying):
    """M5: plan_carry names the lightweight component's mate WHY_LIGHTWEIGHT; the question says it once, as what the
    user can still change, never also as final."""
    record = copy.deepcopy(desk.record)
    record.gearbox.user_work.components[0].state = 1
    record.gearbox.user_work.components[1].state = 0
    said = _said(desk, record=record)
    assert ("Sprocket-1 was lightweight as read: carrying it resolves it in RangeBox.SLDASM too, if that is open, and "
            "its Lock3 is made again only if you set it resolved in SolidWorks before you press.") in said, said
    assert said.count("Sprocket-1 was lightweight") == 1
    assert "Lock3 is on Sprocket-1" not in said and said.count("Lock3") == 1
    assert ("Housing-1 was suppressed in the mode RangeBox.SLDASM showed, as read: show a mode where it is resolved "
            "before you press, or it may not be carried.") in said


def test_the_states_clause_goes_once_a_clean_route_reads_them(desk, carrying, monkeypatch):
    assert STATES in _said(desk)
    monkeypatch.setattr(findings, "COMPONENT_STATE_PER_CONFIGURATION_ROUTE_ON_2026", "GetComponentSuppressionState")
    assert STATES not in _said(desk)


def test_a_mode_renamed_says_what_stays_and_what_the_new_mode_takes(desk, carrying):
    spec = gears(range_box(), **SUN_FLANK)
    spec = replace(spec, modes=tuple(replace(m, name="Low") if m.name == "L" else m for m in spec.modes))
    said = _said(desk, spec=spec)
    assert ("RangeBox_r2 has no mode L: what your items were in L stays in RangeBox.SLDASM. Its new mode Low takes "
            "what they were in H.") in said, said


def test_with_nothing_of_the_users_on_record_the_question_says_the_press_reads_first(desk, carrying):
    record = copy.deepcopy(desk.record)
    record.gearbox.user_work = None
    assert _said(desk, record=record) == (
        "Anything you added to RangeBox.SLDASM in SolidWorks the press reads first and carries into RangeBox_r2 where "
        f"it can, saying whatever it cannot. {CLOSED_UNREAD} (Not yet shown on SolidWorks 2026: {CLOSED_FINDINGS}.)")


def test_a_foresight_that_raises_says_only_that_the_press_reads_and_carries_what_it_can(desk, carrying):
    def boom(*a, **k):
        raise RuntimeError("no")
    again = _again(desk, gears(range_box(), **SUN_FLANK))
    fore = update.carry_foresight(desk.record, again, plan_carry=boom, read_sidecar=desk.disk.read_sidecar)
    assert fore.plan is None
    assert ui_text.carry_sentence(fore, again).startswith(
        f"As read at {_at(desk)}, RangeBox.SLDASM held your Sprocket-1, Housing-1 and Lock3: the press reads it again "
        "first and carries into RangeBox_r2 what it can, saying whatever it cannot.")


def test_the_whole_question_is_a_length_a_person_reads(desk, carrying):
    spec = gears(range_box(), **SUN_FLANK)
    up = update.classify(desk.record, desk.a(spec), exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    again = _again(desk, spec)
    question = ui_text.build_again_question(up, again, record=desk.record)
    assert question.startswith("Gear_m1.25_N29 (Sun): Flank changed from involute to arcs")
    assert f" As read at {_at(desk)}, RangeBox_r2 takes your Sprocket-1 and Housing-1" in question
    assert len(question.split()) < 200, len(question.split())       # 326 words before the review's S3


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


def _stays(left=(), kept=(), assembly=OLD):
    from gear_generator.workbook.update import StaysBehind
    entry = store.UserWorkEntry(read_at="2026-11-17T14:02:00Z", assembly=assembly,
                                components=[store.UserComponentEntry("Sprocket-1", "part")])
    return StaysBehind(entry, assembly, ("Sprocket-1",), ("M0",), tuple(left), tuple(kept))


def _status(done, anchors=None, revision=(), carry=None, stays=None, result=None):
    result = result or type("R", (), {"carry": done, "old_user_work": None, "old_read": ""})()
    return ui_text.carried_status(result, _Again(), OLD, anchors, revision, carry=carry, stays=stays)


def _carry_stub(why_new=None, modes=("H", "N", "L"), first="H"):
    bodies = tuple(swbuild.CarryBody(g, f"{g}-1", "gear1", False, why) for g, why in (why_new or {}).items())
    return swbuild.Carry(swbuild.OldAssembly(OLD), bodies, modes, first)


def test_the_result_says_what_was_carried_unsaved_and_the_feature_left_and_to_save_it():
    anchors = {"Sprocket-1": "Sun", "Sprocket-2": "Sun", "Chain-1": "Sun", "Housing-1": "RangeSlv"}
    named = [swbuild.CarryNamed("M7", "mate", swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "face", "bore"))]
    stays = _stays(left=[("Keyway", r"C:\Out\Gear_m1.25_N29.SLDPRT", ("Sun",))])
    said = _status(_done(named=named), anchors, carry=_carry_stub({"Sun": "its Flank changed"}), stays=stays)
    assert said == (
        "Carried into RangeBox_r2, unsaved: your Sprocket-1, Sprocket-2, Chain-1 and Housing-1, each where it stood "
        "against its gear, and 7 of your 8 mates, each on in the modes it was on in. M7 was on Sun's bore, and Sun's "
        "part is new because its Flank changed, so it is not made again. Your Keyway stays in Gear_m1.25_N29, which "
        "Sun's new part replaces because its Flank changed (RangeBox.SLDASM and that file keep it). Your components "
        "were placed where they stood in H, the mode RangeBox.SLDASM showed; one no mate holds stands there in every "
        "mode. Your components take in every mode the state they had in H, the mode RangeBox.SLDASM showed: their states in N and L could "
        f"not be read without changing it. {ui_text.CARRY_STANDING} If a part of yours was made in context of "
        "RangeBox.SLDASM, it still refers to that assembly's parts. Save RangeBox_r2 in SolidWorks to keep what was "
        "carried."), said
    every = _done(remade=[(m.name, m.name, ("H",)) for m in _work().mates])
    assert "and your 8 mates, each on in the modes it was on in." in _status(every)
    assert "against its gear or carrier" in _status(_done(), {"Sprocket-1": "Sun", "Sprocket-2": "Carrier carrier",
                                                              "Chain-1": "Sun", "Housing-1": "Sun"})
    one = _work(components=("Sprocket-1",), mates=1)
    assert _status(_done(one), {"Sprocket-1": "Sun"}).startswith(
        "Carried into RangeBox_r2, unsaved: your Sprocket-1, where it stood against its gear.")    # one: no "each"
    assert _status(None) == ""


def test_the_result_says_a_mode_gone_and_what_a_new_mode_took():
    said = _status(_done(), carry=_carry_stub(modes=("H", "N", "Low")))
    assert ("RangeBox_r2 has no mode L: what your items were in L stays in RangeBox.SLDASM. Its new mode Low takes "
            "what they were in H.") in said, said


@pytest.mark.parametrize("why, subjects, clause", [
    (swbuild.WHY_KIND, ("width",), "M1 is a width mate, which Gear Generator does not make again"),
    (swbuild.WHY_UNMEASURED, ("concentric", "CARRY_REMAKE_KINDS_ON_2024", "2024"),
     "M1 is not made again: Gear Generator has not yet been shown to make concentric mates again in a new revision on "
     "SolidWorks 2024 (findings.CARRY_REMAKE_KINDS_ON_2024)"),
    (swbuild.WHY_UNMEASURED, ("face", "PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024", "2024"),
     "M1 is not made again: Gear Generator has not yet been shown to find a mate's face again in a new revision on "
     "SolidWorks 2024 (findings.PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024)"),
    (swbuild.WHY_UNMEASURED, ("face", "PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024", "2024", "Sprocket-1"),
     "M1 is not made again: Gear Generator has not yet been shown to find a mate's face of Sprocket-1 again in a new "
     "revision on SolidWorks 2024 (findings.PERSIST_REFERENCE_ROUTE_FOR_FACES_ON_2024)"),
    (swbuild.WHY_UNMEASURED, ("edge", "PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026", "2026"),
     "M1 is not made again: Gear Generator has not yet been shown to find a mate's edge again after its part is "
     "closed and opened again on SolidWorks 2026 (findings.PERSIST_REFERENCE_SURVIVES_RELOAD_ON_2026)"),
    (swbuild.WHY_UNMEASURED, ("origin", "ORIGIN_ENTITY_READ_ON_2026", "2026"),
     "M1 is not made again: Gear Generator has not yet been shown to read an origin as a mate's entity on SolidWorks "
     "2026 (findings.ORIGIN_ENTITY_READ_ON_2026)"),
    (swbuild.WHY_UNMEASURED, ("gear mate on an app gear", "CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2026", ""),
     "M1 is not made again: Gear Generator has not yet been shown to make a gear mate on an app gear again in a new "
     "revision on the SolidWorks it runs on (findings.CARRY_GEAR_MATE_ON_AN_APP_GEAR_ON_2026)"),
    (swbuild.WHY_UNMEASURED, ("leaf", "CARRY_REMAKES_ON_A_LEAF_ON_2026", "2026"),
     "M1 is not made again: Gear Generator has not yet been shown to make a mate on a part inside a sub-assembly of "
     "yours again on SolidWorks 2026 (findings.CARRY_REMAKES_ON_A_LEAF_ON_2026)"),
    (swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "face", "bore"),
     "M1 was on Sun's bore, and Sun's part is new because its Flank changed"),
    (swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "face", "axis"),
     "M1 was on a face of Sun on its axis, and Sun's part is new because its Flank changed"),
    (swbuild.WHY_PART_NEW, ("Sun", "its Flank changed", "edge", ""),
     "M1 was on an edge of Sun, and Sun's part is new because its Flank changed"),
    (swbuild.WHY_GONE, ("gear", "G5"), "M1 was on G5, which RangeBox_r2 does not have"),
    (swbuild.WHY_GONE, ("shaft", "Output"), "M1 was on the layout's Output Axis, and RangeBox_r2 has no shaft Output"),
    (swbuild.WHY_GONE, ("feature", "Mid Plane"),
     "M1 was on Mid Plane in an app part, which that part in RangeBox_r2 does not have"),
    (swbuild.WHY_GONE, ("feature", "Mid Plane", "Sun"), "M1 was on Sun's Mid Plane, which Sun's new part does not have"),
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
    ("too long", ("face", "Sprocket-5", "Sprocket.SLDPRT", "candidates"),
     "M1 is on a face of Sprocket-5 that Gear Generator did not look for, since finding it among Sprocket.SLDPRT's "
     "faces would have taken too long"),
    ("too long", ("edge", "Sun", "Gear_m1.25_N29.SLDPRT", "seconds"),
     "M1 is on an edge of Sun that Gear Generator did not look for, since finding it among Gear_m1.25_N29.SLDPRT's "
     "edges would have taken too long"),
    (swbuild.WHY_DIFFERS, ("entities",), "M1 made again read otherwise than it was (its entities), so it was taken out "
                                         "again"),
    (swbuild.WHY_OLD_UNREAD, ("it was not open in SolidWorks",),
     "RangeBox.SLDASM was not read: it was not open in SolidWorks"),
])
def test_each_reason_a_mate_is_not_carried_has_its_clause(why, subjects, clause):
    named = swbuild.CarryNamed("M1", "mate", why, subjects)
    assert ui_text.carry_named_clause(named, name="RangeBox_r2", old="RangeBox.SLDASM") == clause


@pytest.mark.parametrize("why, subjects, sentence", [
    (swbuild.WHY_NOT_CARRIED, ("Bracket-1",), "M1 joins Bracket-1, which is not carried, so it is not made again."),
    (swbuild.WHY_ASSEMBLY_FEATURE, ("Plane1",),
     "M1 is on Plane1, a feature you made in RangeBox.SLDASM, which is not carried, so it is not made again."),
    (swbuild.WHY_LIGHTWEIGHT, ("Sprocket-4",), "M1 is on Sprocket-4, which was lightweight in RangeBox.SLDASM, so what "
                                               "it joins could not be read, and it is not made again."),
    (swbuild.WHY_UNMEASURED, ("leaf", "CARRY_REMAKES_ON_A_LEAF_ON_2026", "2026"),
     "Gear Generator has not yet been shown to make a mate on a part inside a sub-assembly of yours again on "
     "SolidWorks 2026 (findings.CARRY_REMAKES_ON_A_LEAF_ON_2026), so M1 is not made again."),
    ("too long", ("face", "Sprocket-5", "Sprocket.SLDPRT", "candidates"),
     "M1 is on a face of Sprocket-5 that Gear Generator did not look for, since finding it among Sprocket.SLDPRT's "
     "faces would have taken too long."),
])
def test_a_mate_is_always_told_it_is_not_made_again(why, subjects, sentence):
    """S1: the verdict follows what the item is: a mate whose clause ends *which is not carried* (its component, or
    its feature) is still told it is not made again."""
    named = swbuild.CarryNamed("M1", "mate", why, subjects)
    assert ui_text._named_sentences([named], name="RangeBox_r2", old="RangeBox.SLDASM") == [sentence]


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
     "Part1^RangeBox-1 is not carried: Gear Generator has not yet been shown to carry your work into a new revision "
     "on SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024)"),
    (swbuild.WHY_UNMEASURED, ("sub-assembly", "SUBASSEMBLY_READ_ONLY_INSERT_ON_2026", "2026"),
     "Part1^RangeBox-1 is not carried: Gear Generator has not yet been shown to insert a sub-assembly of yours into a "
     "new revision on SolidWorks 2026 (findings.SUBASSEMBLY_READ_ONLY_INSERT_ON_2026)"),
    (swbuild.WHY_UNMEASURED, ("configuration", "CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026", "2026"),
     "Part1^RangeBox-1 is not carried: Gear Generator has not yet been shown to insert a component in one of its "
     "file's several configurations on SolidWorks 2026 (findings.CARRY_INSERTS_IN_A_CONFIGURATION_ON_2026)"),
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
    (swbuild.CarryFallback(("Sprocket-8",), ("Lock8",), ("Lock9",), swbuild.FELL_TIE, ("Sun", "L")),
     "Sprocket-8 is fixed where it stood in RangeBox_r2: with your Lock8 made again SolidWorks reads Sun unable to "
     "turn in L, so it was not kept; Lock9 beside it was."),
    (swbuild.CarryFallback(("Sprocket-3", "Chain-1"), ("Lock3",), ("Dist1", "Dist2"), swbuild.FELL_NEW_ERROR,
                           ("Lock3", "46", "0", "L")),
     "Sprocket-3 and Chain-1 are fixed where they stood in RangeBox_r2: with your Lock3 made again it reads error 46 "
     "in L, which it did not in H, the mode RangeBox.SLDASM showed, so it was not kept; Dist1 and Dist2 beside it "
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


def test_the_results_other_sentences_each_as_they_apply(monkeypatch):
    work = _work(components=("Sprocket-2", "Drive-1"), mates=2)
    work.components[1] = replace(work.components[1], kind="assembly", path="C:\\Parts\\Drive.SLDASM")
    clash = swbuild.Clash(("Sprocket-2", "gear6-1"), ("Sprocket-2", "RangeSlv"), 12.3)
    done = _done(work, same_error=[("M0", 46)], moved=[("Sprocket-2", "N", 2.04), ("Sprocket-2", "L", 2.04)],
                 clashes=[("L", clash)], marked_user=[r"C:\Parts\Sprocket.SLDPRT"])
    monkeypatch.setattr(findings, "CARRY_INSERT_MARKS_USER_DOCUMENTS_ON_2026", True)
    said = _status(done, anchors={"Sprocket-2": "Sun"}, revision=(34, 0, 0))
    for sentence in ("Your M0 was in error in RangeBox.SLDASM and is in RangeBox_r2 too, as it was.",
                     "SolidWorks moved Sprocket-2 off where it stood against Sun when your mates were made again: "
                     "2.0 mm in N and L.",
                     "In mode L, your Sprocket-2 interferes with RangeSlv (12.3 mm³).",
                     "Your sub-assembly Drive-1 comes over rigid: set it flexible in SolidWorks again if it was.",
                     "SolidWorks reads Sprocket.SLDPRT as changed since it was inserted into RangeBox_r2, though "
                     "nothing in it changed: saving RangeBox_r2 with its parts saves that file again too."):
        assert sentence in said, (sentence, said)
    # The fact not set: only what SolidWorks reads is said.
    monkeypatch.setattr(findings, "CARRY_INSERT_MARKS_USER_DOCUMENTS_ON_2026", None)
    assert ("SolidWorks reads Sprocket.SLDPRT as changed since it was inserted into RangeBox_r2: saving RangeBox_r2 "
            "with its parts saves that file again too.") in _status(done, revision=(34, 0, 0))
    # With the states read per mode, nothing is said of them; a fixed component is not said to float.
    read = _work(components=("Housing-1",), mates=0, states_route="GetComponentSuppressionState")
    said = _status(_done(read))
    assert "could not be read without changing it" not in said and "stand in every mode" not in said


def test_a_carry_that_stopped_says_the_workers_sentence_and_what_it_did_not_get_to():
    stopped = "SolidWorks stopped the carry while making UserDist4 again: AddMate5 answered 2."
    done = _done(stopped=stopped, skipped="making Sprocket-4's other mates again and checking the assembly")
    said = _status(done)
    assert (f"{stopped} It did not get to making Sprocket-4's other mates again and checking the assembly. What was "
            "carried before it is in RangeBox_r2, unsaved, and RangeBox_r2 as built is saved.") in said, said
    assert "Carrying your work stopped" not in said and "Save RangeBox_r2 in SolidWorks" not in said
    # M4: a stop before anything was made says nothing was carried, and W9a's sentence of what stays.
    early = swbuild.CarryResult(_work(), stopped="SolidWorks would not read RangeBox_r2's frames (Sun not found).",
                                skipped="inserting your components")
    result = type("R", (), {"carry": early, "old_user_work": swbuild.UserWork(
        components=[swbuild.UserComponent("Sprocket-1")]), "old_read": ""})()
    said = _status(early, result=result, stays=_stays())
    assert said == ("SolidWorks would not read RangeBox_r2's frames (Sun not found). It did not get to inserting your "
                    "components. Nothing of yours was carried, and RangeBox_r2 as built is saved. Your Sprocket-1 stays "
                    "in RangeBox.SLDASM, as read when this build began; RangeBox_r2 has none of it."), said


def test_a_files_change_found_after_the_carry_is_said_as_what_it_is_not_as_a_stop():
    after = ("Sprocket.SLDPRT changed on disk while Build again… carried your work, which Gear Generator never does; "
             "look at it in SolidWorks.")
    said = _status(_done(stopped=after, changed_files=["Sprocket.SLDPRT"]))
    assert said.endswith(f"{after} Save RangeBox_r2 in SolidWorks to keep what was carried."), said
    assert "did not get to" not in said and "What was carried before it" not in said
    # N2: a stop with the fact after it keeps its tail and what was carried before it, and the fact apart.
    stop = "SolidWorks stopped the carry while making UserDist4 again: SolidWorks: AddMate5 answered 2"
    both = _done(stopped=f"{stop} {after}", changed_files=["Sprocket.SLDPRT"],
                 skipped="making UserDist4 again and checking the assembly in every mode")
    said = _status(both)
    assert (f"{stop}. It did not get to checking the assembly in every mode. What was carried before it is in "
            f"RangeBox_r2, unsaved, and RangeBox_r2 as built is saved.") in said, said
    assert said.endswith(after) and "Save RangeBox_r2" not in said


def test_nothing_carried_today_leads_w9as_sentence_with_the_finding(desk):
    """M1: every finding None, the result is W9a's sentence led by the finding, as the question is."""
    done = swbuild.CarryResult(_work(components=("Sprocket-1", "Housing-1"), mates=1), named=[
        swbuild.CarryNamed("Sprocket-1", "component", swbuild.WHY_UNMEASURED, ("insert", "CARRY_INSERTS_ON_2026",
                                                                               "2026")),
        swbuild.CarryNamed("Housing-1", "component", swbuild.WHY_UNMEASURED, ("insert", "CARRY_INSERTS_ON_2026",
                                                                              "2026")),
        swbuild.CarryNamed("M0", "mate", swbuild.WHY_NOT_CARRIED, ("Sprocket-1",))])
    work = swbuild.UserWork(components=[swbuild.UserComponent("Sprocket-1"), swbuild.UserComponent("Housing-1")],
                            mates=[swbuild.UserMate("Lock3")])
    result = type("R", (), {"carry": done, "old_user_work": work, "old_read": ""})()
    stays = _stays(left=[("Keyway", r"C:\Out\Gear_m1.25_N29.SLDPRT", ("Sun",))])
    said = _status(done, result=result, stays=stays)
    at = ui_text.read_time("2026-11-17T14:02:00Z")
    assert said == ("Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 "
                    "(findings.CARRY_INSERTS_ON_2026), so your Sprocket-1, Housing-1 and Lock3 stay in "
                    "RangeBox.SLDASM, as read when this build began; RangeBox_r2 has none of them. As read at "
                    f"{at}, your Keyway stays in Gear_m1.25_N29, which RangeBox_r2 does not use; RangeBox_r2 has none "
                    "of it, nor anything added since."), said


def test_an_old_assembly_not_read_says_why_and_what_the_record_holds_and_no_press_again():
    """M3: A's reason as a clause, then the record's sentence; never advice to press again (D11)."""
    unread = _work(how=swbuild.OLD_UNREAD, unread=[
        "RangeBox.SLDASM is not open in SolidWorks, and Gear Generator reads it then only when its close has been "
        "shown clean (findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026)."])
    said = _status(swbuild.CarryResult(unread), stays=_stays())
    at = ui_text.read_time("2026-11-17T14:02:00Z")
    assert said == ("RangeBox.SLDASM is not open in SolidWorks, and Gear Generator reads it then only when its close "
                    "has been shown clean (findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026), so nothing of yours "
                    f"was carried; as read at {at}, your Sprocket-1 and M0 stay in RangeBox.SLDASM; RangeBox_r2 has "
                    "none of them, nor anything added since."), said
    assert "press" not in said and "((" not in said and "))" not in said


def test_a_read_that_raised_a_read_that_marked_and_a_document_left_open_each_say_nothing_was_carried():
    said = _status(swbuild.CarryResult(None, stopped=r"SolidWorks did not answer the read of RangeBox.SLDASM: "
                                                     r"C:\Users\Mo Zhou\RPC_E_CALL_FAILED."), stays=_stays())
    assert said.startswith("SolidWorks did not answer the read of RangeBox.SLDASM: RPC_E_CALL_FAILED, so nothing of "
                           "yours was carried; RangeBox.SLDASM and your files are as they were on disk. As read at"), said
    assert "Mo Zhou" not in said
    marked = _work(marked=[r"C:\Parts\Sprocket.SLDPRT"])
    assert _status(swbuild.CarryResult(marked, stopped="x")) == (
        "Reading RangeBox.SLDASM marked Sprocket.SLDPRT as changed in SolidWorks, which Gear Generator never does on "
        "purpose, so nothing of yours was carried; nothing in it changed, and RangeBox.SLDASM and your files are as "
        "they were on disk.")
    left = _work(left=[r"C:\Parts\Sprocket.SLDPRT"])
    assert _status(swbuild.CarryResult(left, stopped="x")) == (
        "Reading RangeBox.SLDASM left Sprocket.SLDPRT open in SolidWorks, so nothing of yours was carried; close it "
        "without saving.")


def test_a_path_in_the_workers_words_is_said_and_kept_by_its_file_name_only():
    text = (r"SolidWorks stopped the carry while inserting C:\Users\Mo Zhou\Parts\Sprocket.SLDPRT: "
            r"\\server\share\x\Housing.SLDPRT is read-only.")
    assert ui_text.bare_files(text) == ("SolidWorks stopped the carry while inserting Sprocket.SLDPRT: Housing.SLDPRT "
                                        "is read-only.")
    said = _status(_done(stopped=text))
    assert "Users" not in said and "Mo Zhou" not in said and "server" not in said


def test_the_carry_kind_words_are_the_workers():
    assert ui_text.CARRY_KIND_WORDS == swbuild.CARRY_KIND_WORDS


# -- the finish's record (§7) and the footer's lines (§9.4) ------------------------------------------------------------

def _carried_build(desk, done_for, spec=None, mtime=lambda p: 1763400000.5):
    """A Build again… of ``spec`` (Sun's Flank to arcs) on the desk's fake, with ``done_for(work)`` its hand-made
    CarryResult, finished as the window finishes it; (again, result, finished, carry)."""
    spec = spec or gears(range_box(), **SUN_FLANK)
    again = _again(desk, spec)
    old = update.old_assembly(desk.record, again)
    carry = update.carry_for(desk.record, again, old, read_sidecar=desk.disk.read_sidecar)
    result = swbuild.build_gearbox(desk.sw, **again.build_kwargs(), exists=desk.disk.exists, before=old)
    assert result.ok and result.assembly.saved
    work = update.recorded_old_work(desk.record)
    work.read_at = "2026-11-17T14:10:00Z"
    work.components = [replace(c, configurations=("Default",)) for c in work.components]    # as the worker reads
    result.carry = done_for(work)
    finished = gearbox.finish_build(again, result, desk.record, workbook=r"C:\B\RangeBox.xlsx", digest="d9",
                                    written_by="test", read_sidecar=desk.disk.read_sidecar, exists=desk.disk.exists,
                                    stamp="2026-11-17T14:12:00Z", revision=(34, 0, 0), mtime=mtime, carry=carry)
    return again, result, finished, carry


def _all_carried(work):
    return swbuild.CarryResult(
        work, inserted=[("Sprocket-1", "Sprocket-1"), ("Housing-1", "Housing-2")],
        states=[("Sprocket-1", ("L",)), ("Housing-2", ())], remade=[("Lock3", "Lock3", ("H", "N"))],
        named=[swbuild.CarryNamed("Concentric5", "mate", swbuild.WHY_PART_NEW,
                                  ("Sun", "its Flank changed", "face", "bore"))],
        fixed=[swbuild.CarryFallback(("Housing-2",), ("Lock9",), (), swbuild.FELL_TIE, ("Sun", "H"))], unsaved=True,
        anchors=[("Sprocket-1", "Sun"), ("Housing-2", "")])


def test_the_finish_keeps_the_carry_on_the_new_revision_and_its_inventory_from_what_was_carried(desk, carrying):
    again, result, finished, carry = _carried_build(desk, _all_carried)
    box = finished.record.gearbox
    assert box.name == "RangeBox_r2" and finished.record.unsaved == {}          # never LinkRecord.unsaved (D16)
    entry = box.carry
    assert (entry.assembly, entry.read_at, entry.how, entry.carried_at, entry.revision, entry.states_read) == (
        desk.record.gearbox.assembly, "2026-11-17T14:10:00Z", "open", "2026-11-17T14:12:00Z", [34, 0, 0], False)
    assert [(c.name, c.was, c.kind, c.fixed, c.suppressed_in, c.anchor) for c in entry.components] == [
        ("Sprocket-1", "Sprocket-1", "part", False, ["L"], "Sun"), ("Housing-2", "Housing-1", "part", True, [], "")]
    assert [(m.name, m.was, m.type, m.on, m.code_before, m.code_after) for m in entry.mates] == [
        ("Lock3", "Lock3", 16, ["H", "N"], 0, 0)]
    assert entry.named[0].sentence == "Concentric5 was on Sun's bore, and Sun's part is new because its Flank changed"
    assert (entry.fixed[0].components, entry.fixed[0].why) == (["Housing-2"], "tie")
    assert entry.unsaved_at == 1763400000.5
    inventory = box.user_work
    assert (inventory.read_at, inventory.assembly, inventory.revision, inventory.modes) == (
        "2026-11-17T14:12:00Z", box.assembly, [34, 0, 0], ["H", "N", "L"])
    assert [(c.name, c.fixed, c.state) for c in inventory.components] == [("Sprocket-1", False, 2),
                                                                           ("Housing-2", True, 2)]
    assert [(m.name, m.touches, m.on) for m in inventory.mates] == [
        ("Lock3", [["app", "Sun"], ["user", "Sprocket-1"]], ["H", "N"])]
    assert [(f.name, ui_text._stem(f.path)) for f in inventory.features] == [("Groove", "Sleeve_m1.25_N17")]
    again_text = store.link_record_to_json(finished.record)
    assert store.link_record_from_json(again_text).gearbox.carry == entry


def test_with_nothing_carried_the_new_revision_holds_no_inventory_and_nothing_unsaved(desk):
    def none_carried(work):
        return swbuild.CarryResult(work, named=[swbuild.CarryNamed("Lock3", "mate", swbuild.WHY_UNMEASURED,
                                                                   ("lock", "CARRY_REMAKE_KINDS_ON_2026", "2026"))])
    _, _, finished, _ = _carried_build(desk, none_carried)
    box = finished.record.gearbox
    assert box.user_work is None and box.carry.unsaved_at == 0.0 and box.carry.components == []
    assert box.carry.named[0].sentence == ("Lock3 is not made again: Gear Generator has not yet been shown to make lock "
                                           "mates again in a new revision on SolidWorks 2026 "
                                           "(findings.CARRY_REMAKE_KINDS_ON_2026)")
    assert store.carry_unsaved(finished.record) is None and ui_text.carry_footer_line(finished.record) == ""


def test_the_footer_says_the_carry_is_unsaved_until_the_file_is_newer(desk):
    _, _, finished, _ = _carried_build(desk, _all_carried)
    record = store.link_record_from_json(store.link_record_to_json(finished.record))
    line = ("RangeBox_r2 holds what Build again… carried of yours, not saved: save it in SolidWorks to keep it.")
    assert ui_text.carry_footer_line(record) == line
    a = desk.a(gears(range_box(), **SUN_FLANK))
    footer = ui_text.workbook_footer(a, record=record, plan=None, update=None, digest="d9", folder="C:\\Out\\")
    assert line in footer.text, footer.text
    store.clear_saved(record, mtime=lambda p: 1763400000.5)                   # the same time: still unsaved
    assert ui_text.carry_footer_line(record) == line
    store.clear_saved(record, mtime=lambda p: 1763400100.0)                   # saved in SolidWorks since
    assert ui_text.carry_footer_line(record) == "" and record.gearbox.carry.unsaved_at == 0.0
    assert record.gearbox.carry.components                                    # what was carried stays on record


def test_a_later_update_that_finds_the_new_assembly_loaded_from_its_file_says_the_carry_was_lost(desk):
    again, result, finished, carry = _carried_build(desk, _all_carried)
    desk.record = store.link_record_from_json(store.link_record_to_json(finished.record))
    desk.disk.write(finished)
    up = update.classify(desk.record, desk.a(gears(range_box(), **SUN_FLANK)), exists=desk.disk.exists,
                         read_sidecar=desk.disk.read_sidecar)
    assert not up.needs_new_revision and up.refusal == "", (up.refusal, up.structural)
    later = swbuild.GearboxUpdate()
    later.opened = [desk.record.gearbox.assembly]
    out = gearbox.Finished()
    update._follow_carry(desk.record, up, later, out, mtime=lambda p: 1763400000.5)
    assert out.notes == ["RangeBox_r2 was closed without saving after Build again… carried your work into it, so it "
                         "does not hold it; RangeBox.SLDASM still does."]
    assert store.carry_unsaved(desk.record) is None and desk.record.unsaved == {}
    # Still open (in the session when the job began, not loaded): nothing said, the mark stands.
    desk.record.gearbox.carry.unsaved_at = 1763400000.5
    still = swbuild.GearboxUpdate()
    still.open_before = [desk.record.gearbox.assembly]
    out = gearbox.Finished()
    update._follow_carry(desk.record, up, still, out, mtime=lambda p: 1763400000.5)
    assert out.notes == [] and store.carry_unsaved(desk.record) is not None
    # Saved since: the mark goes silently.
    update._follow_carry(desk.record, up, still, out, mtime=lambda p: 1763400500.0)
    assert out.notes == [] and store.carry_unsaved(desk.record) is None


# -- the round trip on the fake (A's worker) ---------------------------------------------------------------------------

def _desk(entity_kinds):
    """RangeBox on the fake with W9a's user work read by a quiet press, the fake reading each mate's entity kinds
    (schema 10's inventory) or not (a schema 9 one); the user's files on the fake's disk."""
    d = Desk()
    d.sw.read_entity_kinds = entity_kinds
    d.build(range_box())
    users_work(d)
    d.disk.files |= {"c:\\parts\\sprocket.sldprt", "c:\\parts\\housing.sldprt"}
    return d


def _carry_job(desk, spec):
    """A Build again… of ``spec`` as the window runs it: carry_for from the old assembly passed as before, A's worker
    on the fake, the finish (its mtime the new assembly's, once); (again, carry, result, the record read back)."""
    again = _again(desk, spec)
    old = update.old_assembly(desk.record, again)
    carry = update.carry_for(desk.record, again, old, read_sidecar=desk.disk.read_sidecar)
    result = swbuild.build_gearbox(desk.sw, **again.build_kwargs(), exists=desk.disk.exists, before=old, carry=carry)
    times = {}
    finished = gearbox.finish_build(again, result, desk.record, workbook=r"C:\B\RangeBox.xlsx", digest="d9",
                                    written_by="test", read_sidecar=desk.disk.read_sidecar, exists=desk.disk.exists,
                                    stamp="2026-11-17T14:12:00Z", revision=desk.sw.revision,
                                    mtime=lambda p: times.setdefault(p, 1763400000.5), carry=carry)
    return again, carry, result, store.link_record_from_json(store.link_record_to_json(finished.record))


def _status_of(desk, again, carry, result):
    return ui_text.carried_status(result, again, carry.old.path, gearbox.carry_anchors(carry, result.carry,
                                                                                         desk.sw.revision),
                                  desk.sw.revision, carry=carry, stays=update.stays_behind(desk.record, again))


@pytest.mark.parametrize("entity_kinds", [False, True])
def test_the_round_trip_classify_question_build_with_carry_finish_record_footer(carrying, entity_kinds):
    """The window's path, without the window (its own test drives ``_start_build`` / ``_finish_build`` under Tk):
    classify needs a new revision; the question foresees the carry from the record's inventory with its time; the
    job is given ``carry`` from the very old assembly it passes as ``before``; the worker (package A's, on the fake)
    reads the old assembly first and carries; the finish records it at schema 10 with the new revision's inventory
    and ``unsaved_at``; the footer asks for the save until the new assembly's file is newer. With the fake reading
    entity kinds (S9) the inventory is schema 10's, its mates' entities through classify, the question and the
    finish."""
    desk = _desk(entity_kinds)
    entities = desk.record.gearbox.user_work.mates[0].entities
    assert bool(entities) is entity_kinds and all(e[2] == "whole" for e in entities)
    spec = gears(range_box(), **SUN_FLANK)
    up = update.classify(desk.record, desk.a(spec), exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    assert up.needs_new_revision
    question = ui_text.build_again_question(up, _again(desk, spec), record=desk.record)
    assert (f"As read at {_at(desk)}, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in "
            "the modes it was on in.") in question, question
    old_mates = {k: copy.deepcopy(v) for k, v in desk.sw.memory_mates.items()}
    again, carry, result, record = _carry_job(desk, spec)
    assert result.ok and result.carry is not None and result.carry.work.how == swbuild.OLD_OPEN
    key = carry.old.path.replace("/", "\\").lower()
    assert desk.sw.memory_mates[key] == old_mates[key]           # nothing written to the old assembly's mates
    done = result.carry
    assert [o for o, _ in done.inserted] == ["Sprocket-1", "Housing-1"] and [m for m, _, _ in done.remade] == ["Lock3"]
    assert done.moved == [] and done.anchors                  # nothing reads as moved (the fake's fix, A's note)
    said = _status_of(desk, again, carry, result)
    assert said.startswith("Carried into RangeBox_r2, unsaved: your ") and "and your Lock3, on in the modes it was " \
        "on in." in said, said
    assert ("Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed "
            "(RangeBox.SLDASM and that file keep it).") in said                # M2
    assert said.endswith("Save RangeBox_r2 in SolidWorks to keep what was carried.")
    assert json.loads(store.link_record_to_json(record))["link_schema_version"] == 10
    box = record.gearbox
    assert box.carry.how == "open" and [c.was for c in box.carry.components] == ["Sprocket-1", "Housing-1"]
    assert {c.was: c.anchor for c in box.carry.components} == dict(gearbox.carry_anchors(carry, done, ()))
    assert box.carry.components[0].anchor == "Sun"
    assert [m.was for m in box.carry.mates] == ["Lock3"] and box.carry.unsaved_at == 1763400000.5
    assert [c.name for c in box.user_work.components] == [n for _, n in done.inserted]
    assert [len(m.entities) for m in box.user_work.mates] == [2]   # the carry's own read keeps them either way
    assert record.unsaved == {}
    line = "RangeBox_r2 holds what Build again… carried of yours, not saved: save it in SolidWorks to keep it."
    a = desk.a(spec)
    footer = ui_text.workbook_footer(a, record=record, digest="d9", folder="C:\\Out\\")
    assert line in footer.text, footer.text
    store.clear_saved(record, mtime=lambda p: 1763400900.0)
    assert line not in ui_text.workbook_footer(a, record=record, digest="d9", folder="C:\\Out\\").text


def test_the_round_trip_today_with_every_w9d_finding_unset_says_w9as_sentence_led(monkeypatch):
    """M1, end to end: every W9d finding None (today, but for the probe reads the tree may hold), A's worker on the
    fake reads and carries nothing; the result is W9a's sentence led by the finding, as the question is."""
    _reads(monkeypatch)
    desk = _desk(True)
    spec = gears(range_box(), **SUN_FLANK)
    again, carry, result, record = _carry_job(desk, spec)
    said = _status_of(desk, again, carry, result)
    at = _at(desk)
    assert said == ("Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 "
                    "(findings.CARRY_INSERTS_ON_2026), so your Sprocket-1, Housing-1 and Lock3 stay in "
                    "RangeBox.SLDASM, as read when this build began; RangeBox_r2 has none of them. As read at "
                    f"{at}, your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none "
                    "of it, nor anything added since."), said
    assert record.gearbox.user_work is None and record.gearbox.carry.unsaved_at == 0.0
    assert ui_text.carry_footer_line(record) == ""


def test_once_pattern_instances_are_read_the_result_says_each_and_the_standing_list_drops_the_clause(monkeypatch):
    monkeypatch.setattr(findings, "PATTERN_INSTANCE_READ_ON_2026", True)
    work = _work(components=("Sprocket-1", "Sprocket-2"), mates=1)
    work.components[1] = replace(work.components[1], pattern_instance=True)
    said = _status(_done(work), revision=(34, 0, 0))
    assert ui_text.CARRY_STANDING_NO_PATTERN in said and ui_text.CARRY_STANDING not in said
    assert "Your Sprocket-2 was an instance of a pattern of yours, and comes over as a component of its own." in said
    assert ui_text.CARRY_STANDING in _status(_done(work))          # the version not known: the clause stays


# -- the re-check of the fix round (W9D-REVIEW-B.md, 56ca105) -------------------------------------------------------

def test_a_component_a_carried_mate_holds_is_not_said_to_stand_still_in_every_mode():
    """N1: Sprocket-2 locked to the sliding RangeSlv follows it, so only one no carried mate holds stands where it was
    placed in every mode."""
    lock = swbuild.OldMate("Lock5", 16, "MateLock", 0, False, (), (swbuild.OldEntity("app", "RangeSlv", "whole"),
                                                                  swbuild.OldEntity("user", "Sprocket-2", "whole")))
    work = _work(components=("Sprocket-2",), mates=0)
    work.mates = [lock]
    done = _done(work, remade=[("Lock5", "Lock5", ("H", "N", "L"))], moved=[("Sprocket-2", "N", 2.0)])
    said = _status(done, {"Sprocket-2": "RangeSlv"})
    assert ("Your components were placed where they stood in H, the mode RangeBox.SLDASM showed." in said
            and "one no mate holds" not in said), said
    free = _work(components=("Sprocket-2", "Chain-1"), mates=0)
    free.mates = [lock]
    said = _status(_done(free, remade=[("Lock5", "Lock5", ("H",))]))
    assert ("Your components were placed where they stood in H, the mode RangeBox.SLDASM showed; one no mate holds "
            "stands there in every mode.") in said
    fell = _done(free, remade=[("Lock5", "Lock5", ("H",))], fixed=[swbuild.CarryFallback(("Chain-1",), (), (),
                                                                                         swbuild.FELL_TIE, ("Sun",))])
    assert "one no mate holds" not in _status(fell)                   # fixed by its fallback: not floating


def test_the_files_changed_are_kept_by_name_and_the_stop_alone_is_the_stop():
    """N2, the record: ``CarryEntry.changed_files`` from the worker's field, ``stopped`` the stop only."""
    work = _work(components=("Sprocket-1",), mates=0)
    done = _done(work, stopped=(r"SolidWorks stopped the carry while checking: C:\Users\x\Lock.SLDPRT. "
                                "Sprocket.SLDPRT changed on disk while Build again… carried your work, which Gear "
                                "Generator never does; look at it in SolidWorks."), changed_files=["Sprocket.SLDPRT"])
    entry = gearbox.carry_entry(_Again(), done, None, stamp="s", revision=(34, 0, 0), assembly=OLD,
                                mtime=lambda p: 1.0)
    assert entry.stopped == "SolidWorks stopped the carry while checking: Lock.SLDPRT."
    assert entry.changed_files == ["Sprocket.SLDPRT"]
    raw = json.loads(store.link_record_to_json(_record(entry)))
    assert store.link_record_from_json(json.dumps(raw)).gearbox.carry.changed_files == ["Sprocket.SLDPRT"]


def test_a_carry_sentence_that_raises_is_said_as_its_own_and_through_bare_files():
    """N3: never *The build could not be collected*: what was carried could not be said, and it is unsaved."""
    exc = KeyError(r"C:\Users\Mo Zhou\Parts\Sprocket.SLDPRT")
    said = ui_text.carry_unsaid(_Again(), type("R", (), {"carry": _done()})(), exc)
    assert said == ("What was carried into RangeBox_r2 could not be said (KeyError: 'Sprocket.SLDPRT'); it holds it "
                    "unsaved: save it in SolidWorks to keep it."), said
    nothing = swbuild.CarryResult(_work())
    assert ui_text.carry_unsaid(_Again(), type("R", (), {"carry": nothing})(), exc).endswith("could not be said "
                                                                                             "(KeyError: 'Sprocket.SLDPRT').")


@pytest.mark.parametrize("text, kept", [
    (r"Saved C:\R\RangeBox.SLDASM. Next/then", "Saved RangeBox.SLDASM. Next/then"),
    (r"C:\A\x.SLDPRT, in folder D/E", "x.SLDPRT, in folder D/E"),
    (r"mate A\B", r"mate A\B"),
    (r"ratio 1:2 at 14:02, H/N", r"ratio 1:2 at 14:02, H/N"),
    (r"opening C:\Users\Mo Zhou\v1.25 parts\Sprocket.SLDPRT (RPC_E_CALL_FAILED).",
     "opening Sprocket.SLDPRT (RPC_E_CALL_FAILED)."),
    (r"(C:\x\y.SLDPRT)", "(y.SLDPRT)"),
])
def test_bare_files_ends_a_file_name_on_punctuation_and_leaves_what_is_no_path(text, kept):
    """N4."""
    assert ui_text.bare_files(text) == kept


def test_a_mate_left_in_the_new_assembly_says_where_and_what_to_do():
    named = swbuild.CarryNamed("Lock4", "mate", swbuild.WHY_DIFFERS, ("left", "Lock4-2"))
    assert ui_text._named_sentences([named], name="RangeBox_r2", old="RangeBox.SLDASM") == [
        "Lock4 made again read otherwise than it was and could not be taken out again: it is left in RangeBox_r2 as "
        "Lock4-2; delete it there in SolidWorks."]


def test_a_fallback_for_an_app_mate_put_in_error_names_it_as_the_apps():
    fallback = swbuild.CarryFallback(("Sprocket-3",), ("Lock3",), (), swbuild.FELL_NEW_ERROR,
                                     ("G1 meshes G2", "46", "0", "L"))
    assert ("Sprocket-3 is fixed where it stood in RangeBox_r2: with your Lock3 made again the app's G1 meshes G2 "
            "reads error 46 in L, which it did not before your mates were made again in H, the mode RangeBox.SLDASM "
            "showed, so it was not kept.") in _status(_done(fixed=[fallback]))


def test_an_old_assembly_unread_because_nothing_can_be_carried_is_w9as_sentence_behind_the_lead():
    """A's N3: with CARRY_INSERTS None a closed old assembly is never opened; the result is W9a's own sentence for
    it, behind the one honest lead."""
    unread = _work(how=swbuild.OLD_UNREAD, unread=[
        "RangeBox.SLDASM is not open in SolidWorks, and Gear Generator reads it then only when it can carry your work "
        "(findings.CARRY_INSERTS_ON_2026)"])
    done = swbuild.CarryResult(unread, gates=[("insert a component", "CARRY_INSERTS_ON_2026")])
    result = type("R", (), {"carry": done, "old_user_work": None, "old_read": swbuild.OLD_NOT_OPEN})()
    said = _status(done, result=result, stays=_stays())
    at = ui_text.read_time("2026-11-17T14:02:00Z")
    assert said == ("Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026 "
                    "(findings.CARRY_INSERTS_ON_2026). RangeBox.SLDASM was not open in SolidWorks, so it was not read "
                    f"again; as read at {at}, your Sprocket-1 and M0 stay in RangeBox.SLDASM; RangeBox_r2 has none of "
                    "them, nor anything added since."), said


# -- package A's third round (9837c73) -------------------------------------------------------------------------------

def test_files_unread_after_the_carry_are_said_as_the_fact_they_are_and_kept():
    text = r"Whether your files changed could not be read after the carry: C:\Users\x\Parts\Sprocket.SLDPRT is locked"
    done = _done(after_unread=text)
    said = _status(done)
    assert said.endswith("Whether your files changed could not be read after the carry: Sprocket.SLDPRT is locked. "
                         "Save RangeBox_r2 in SolidWorks to keep what was carried."), said
    assert "did not get to" not in said and "What was carried before it" not in said
    entry = gearbox.carry_entry(_Again(), done, None, stamp="s", revision=(34, 0, 0), assembly=OLD, mtime=lambda p: 1.0)
    assert entry.after_unread == "Whether your files changed could not be read after the carry: Sprocket.SLDPRT is locked"
    assert entry.stopped == ""
    back = store.link_record_from_json(store.link_record_to_json(_record(entry)))
    assert back.gearbox.carry.after_unread == entry.after_unread


def test_a_component_resolved_in_the_old_assembly_by_the_carry_is_said_grouped():
    said = _status(_done(resolved_in_old=("Sprocket-9",)))
    assert ("Sprocket-9 was lightweight in RangeBox.SLDASM and is resolved there now: SolidWorks loaded its part to "
            "carry it.") in said, said
    two = _status(_done(resolved_in_old=("Sprocket-9", "Sprocket-10")))
    assert ("Sprocket-9 and Sprocket-10 were lightweight in RangeBox.SLDASM and are resolved there now: SolidWorks "
            "loaded their parts to carry them.") in two
    assert "resolved there now" not in _status(_done())


def test_a_fixed_component_placed_by_its_world_frame_is_never_said_to_stand_against_a_gear():
    work = _work(components=("Sprocket-1", "Housing-1"), mates=2)
    said = _status(_done(work), {"Sprocket-1": "Sun", "Housing-1": ""})
    assert said.startswith("Carried into RangeBox_r2, unsaved: your Sprocket-1 and Housing-1, each where it stood, "), said
    assert "against" not in said.split(".")[0]


def test_an_old_assembly_whose_files_were_moved_is_said_with_the_workers_reason_and_no_advice():
    """R.2's third-round refusal (a stored dependency outside the assembly's folder with a same-named file beside it):
    the result says A's clause and the record's sentence, never what to do; the question's clause keeps its advice."""
    reason = ("RangeBox.SLDASM is not open in SolidWorks, and Gear Generator reads it then only when the files it uses "
              "are where it says they are (Sprocket.SLDPRT is stored in another folder, and a file of the same name "
              "sits beside RangeBox.SLDASM)")
    done = swbuild.CarryResult(_work(how=swbuild.OLD_UNREAD, unread=[reason]))
    said = _status(done, stays=_stays())
    assert said.startswith(reason + ", so nothing of yours was carried; as read at "), said
    assert "open it" not in said.lower() and "press" not in said
