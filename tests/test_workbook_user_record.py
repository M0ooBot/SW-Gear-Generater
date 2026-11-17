"""W9a package B (ISSUE-1-PLAN §2.1 items 6 and 8, K4, K5; W9A-INTERFACES.md): the link record's schema 7 keeps what
an Update read of the user's work, a refused press's problems with it; the footer says before the press what the
next press would do with that work, from the record and with its time, by the worker's own judgement; the Build
again? question names what stays behind with its time; and a Build again… reads the old assembly's user work first,
read-only, as it stands in the session. Against the fake SolidWorks of ``test_swbuild``."""

import copy
import json

import pytest

from gear_generator import findings, store, swbuild, ui_text
from gear_generator.swbuild import UserWorkRefused
from gear_generator.workbook import gearbox, update

from test_workbook_gearbox import settled_findings, static_w4, turning  # noqa: F401
from test_workbook_model import reducer
from test_workbook_update import FOLDER, WORKBOOK, assessed, fake_build, gears, name2, press, shafts  # noqa: F401


def _entry(**changes):
    entry = store.UserWorkEntry(
        read_at="2026-11-16T14:02:00Z", assembly=r"C:\P\R.SLDASM", digest="d1", revision=[34, 1, 1],
        components=[store.UserComponentEntry("Sprocket-1", "part", False, 0, 2),
                    store.UserComponentEntry("Housing-1", "assembly", True, 0, 2)],
        mates=[store.UserMateEntry("Lock3", "lock", 16, [["app", "G1"], ["user", "Sprocket-1"]], ["H", "L"], 0, True,
                                   True),
               store.UserMateEntry("Weird", "other", -1, [["unread", ""]], [], 0, True, False)],
        features=[store.UserFeatureEntry(r"C:\P\Gear_m1.5_N17.SLDPRT", "Keyway", "ICE", 0, True)],
        carried=[store.UserCarriedEntry("Sprocket-1", "G1", ["Lock3"])],
        problems=[store.UserProblemEntry("value", "Bore Diameter in Gear_m1.5_N17 is 12 in SolidWorks.", [],
                                         [store.ValueEditEntry("Gear_m1.5_N17.SLDPRT", "Bore Diameter", "12", "10",
                                                               "10", "", "Gears!J3")])])
    for key, value in changes.items():
        setattr(entry, key, value)
    return entry


def _record(entry=None):
    from test_store import modes_record
    record = modes_record(WORKBOOK)
    record.gearbox.user_work = entry
    if entry is not None:
        entry.assembly = record.gearbox.assembly
    return record


# -- schema 7 --------------------------------------------------------------------------------------------------------


def test_schema_7_keeps_the_users_work_and_round_trips_byte_for_byte(tmp_path):
    record = _record(_entry())
    text = store.link_record_to_json(record)
    raw = json.loads(text)
    assert raw["link_schema_version"] == store.LINK_SCHEMA_VERSION == 7 and raw["schema_version"] == 1
    assert raw["gearbox"]["user_work"]["mates"][0]["touches"] == [["app", "G1"], ["user", "Sprocket-1"]]
    back = store.link_record_from_json(text)
    again = store.link_record_to_json(back)
    assert back == record and store.link_record_from_json(again) == back
    assert store.link_record_to_json(store.link_record_from_json(again)) == again
    assert back.gearbox.user_work.refused and bool(back.gearbox.user_work)


@pytest.mark.parametrize("version", [3, 4, 5, 6])
def test_a_record_written_before_schema_7_reads_with_nothing_of_the_users_read(tmp_path, version):
    from test_store import _before_schema_6
    record = _record(None)
    raw = json.loads(store.link_record_to_json(record))
    del raw["gearbox"]["user_work"]
    if version < 6:
        raw = _before_schema_6(raw, version)
    raw["link_schema_version"] = version
    target = tmp_path / "R.workbook.json"
    target.write_text(json.dumps(raw))
    first = store.read_link_record(str(tmp_path / "R.xlsx"))
    assert first.schema_version == 7 and first.gearbox.user_work is None
    store.save_link_record(first, str(target))
    assert json.loads(target.read_text())["link_schema_version"] == 7
    assert store.read_link_record(str(tmp_path / "R.xlsx")) == first


def test_a_record_newer_than_schema_7_is_refused_and_left_alone(tmp_path):
    raw = json.loads(store.link_record_to_json(_record(_entry())))
    raw["link_schema_version"] = 8
    target = tmp_path / "R.workbook.json"
    target.write_text(json.dumps(raw))
    before = target.read_bytes()
    with pytest.raises(store.UnknownSchema, match=r"schema 8, this one reads 7"):
        store.read_link_record(str(tmp_path / "R.xlsx"))
    assert target.read_bytes() == before


@pytest.mark.parametrize("change, match", [
    (lambda w: w.__setitem__("mates", [{"name": "M", "touches": [["gear", "G1"]]}]), r"user_work\.mates\[0\]"),
    (lambda w: w.__setitem__("mates", [{"name": "M", "touches": [["app"]]}]), r"not a pair"),
    (lambda w: w.__setitem__("components", [{"name": 3}]), r"UserComponentEntry\.name"),
    (lambda w: w.__setitem__("components", [{"name": "S", "kind": "C:\\x.SLDPRT"}]), r"not part or assembly"),
    (lambda w: w.__setitem__("problems", ["x"]), r"problems are not a list of objects"),
    (lambda w: w.__setitem__("revision", ["34"]), r"UserWorkEntry\.revision"),
])
def test_a_user_work_entry_of_the_wrong_shape_is_refused_with_a_sentence(change, match):
    raw = json.loads(store.link_record_to_json(_record(_entry())))
    change(raw["gearbox"]["user_work"])
    with pytest.raises(store.StoreError, match=match):
        store.link_record_from_json(json.dumps(raw))


def test_the_entity_words_are_the_workers():
    assert store._USER_WHAT == (swbuild.APP, swbuild.LAYOUT, swbuild.ASSEMBLY, swbuild.USER, swbuild.UNREAD_ENTITY)


def test_the_entry_and_the_workers_inventory_turn_into_each_other():
    entry = _entry()
    work = update.recorded_user_work(entry)
    again = update.user_work_entry(work, assembly=entry.assembly, digest="d1", revision=(34, 1, 1),
                                   problems=[swbuild.UserProblem(p.kind, p.sentence, tuple(p.mates),
                                                                 tuple(swbuild.ValueEdit(**v.__dict__)
                                                                       for v in p.values))
                                             for p in entry.problems])
    assert again == entry


# -- on the fake: the finish records it, a refusal records its problems ----------------------------------------------


@pytest.fixture
def on_fake(turning):
    sw, plan, result, record = fake_build(reducer())
    return sw, record


def _sprocket(sw, record, lock_to="G1"):
    from test_swbuild import IDENTITY9
    asm = record.gearbox.assembly
    sw.user_component(asm, "Sprocket-1", r"C:\Parts\Sprocket.SLDPRT", (IDENTITY9, (0.0, 0.0, 40.0)))
    sw.user_lock(asm, "Lock3", name2(record, lock_to), "Sprocket-1")
    sw.user_feature(next(p.path for p in record.current_parts() if "G1" in p.gears), "Keyway")


def _footer(record, spec, digest="d2"):
    plan = update.classify(record, assessed(spec), exists=lambda p: True)
    return ui_text.workbook_footer(assessed(spec), record=record, update=plan, folder=FOLDER, digest=digest), plan


def test_a_finished_update_records_what_it_read_with_its_read_and_its_solidworks(on_fake):
    sw, record = on_fake
    _sprocket(sw, record)
    plan, result, _ = press(sw, record, reducer())              # a quiet press: reads, puts nothing
    finished = update.finish_update(plan, result, record, digest="d2", read_sidecar=lambda p: None,
                                    mtime=lambda p: 5.0, revision=(34, 1, 1))
    entry = finished.record.gearbox.user_work
    assert entry.assembly == record.gearbox.assembly and (entry.digest, entry.revision) == ("d2", [34, 1, 1])
    assert [c.name for c in entry.components] == ["Sprocket-1"] and [m.name for m in entry.mates] == ["Lock3"]
    assert [m.touches for m in entry.mates] == [[["app", "G1"], ["user", "Sprocket-1"]]]
    assert [f.name for f in entry.features] == ["Keyway"] and entry.problems == [] and entry.read_at
    assert record.gearbox.user_work is None                     # the record given is never changed
    text = store.link_record_to_json(finished.record)
    assert store.link_record_from_json(text) == finished.record


def test_the_inventory_reaches_the_footer_before_the_press_with_its_time(on_fake, monkeypatch):
    """K4: after a press read a sprocket locked to G1, the footer for a layout move says, before the next press,
    that it moves the sprocket with G1 and rebuilds the user's keyway — by the worker's own judgement, every
    branch of route (c1) given: the reducer's train has no carrier, so until that branch is measured on the
    SolidWorks the inventory was read on, the footer foresees the refusal instead."""
    monkeypatch.setattr(findings, "USER_MATE_PUT_NO_CARRIER_ON_2026", True)
    sw, record = on_fake
    _sprocket(sw, record)
    plan, result, finished = press(sw, record, reducer())
    record = update.finish_update(plan, result, record, digest="d2", read_sidecar=lambda p: None,
                                  mtime=lambda p: 5.0, revision=(34, 1, 1)).record
    at = ui_text.read_time(record.gearbox.user_work.read_at)
    moved = gears(reducer(), G1=dict(backlash="0.1"), G4=dict(at="30"))
    footer, upd = _footer(record, moved)
    assert footer.update_enabled and footer.ok, footer.text
    assert f"As read at {at}, Update SolidWorks rebuilds your Keyway in Gear_m1.5_N17 after the app's features, " \
           "moves your Sprocket-1 with G1, which your Lock3 holds it to" in footer.text, footer.text
    assert "G1" in update.bodies_put(upd)
    # The same press on a SolidWorks where that branch is not measured: the footer foresees the worker's refusal.
    monkeypatch.setattr(findings, "USER_MATE_PUT_NO_CARRIER_ON_2026", None)
    footer, _ = _footer(record, moved)
    assert f"As read at {at}, Update SolidWorks would stop before changing anything: Update SolidWorks would put " \
           "your Sprocket-1 with G1" in footer.text and not footer.ok and footer.update_enabled
    # A quiet press puts nothing: the user's work is left as it is.
    footer, upd = _footer(record, reducer())
    assert update.bodies_put(upd) == set()
    assert f"As read at {at}, Update SolidWorks leaves your Sprocket-1, Lock3 and Keyway in Gear_m1.5_N17 as they " \
           "are." in footer.text, footer.text


def test_a_refused_press_is_recorded_and_the_footer_says_it_until_the_workbook_changes(on_fake):
    sw, record = on_fake
    part = next(p.path for p in record.current_parts() if "G2" in p.gears)
    from test_workbook_user_work import _edit
    _edit(sw, part, "Bore Diameter", "14")
    plan = update.classify(record, assessed(reducer()), exists=lambda p: True)
    with pytest.raises(UserWorkRefused) as raised:
        swbuild.update_gearbox(sw, **plan.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    refused = update.refused_update(record, plan, raised.value, digest="d2", revision=(34, 1, 1))
    assert record.gearbox.user_work is None
    entry = refused.gearbox.user_work
    assert [p.kind for p in entry.problems] == [swbuild.PROBLEM_VALUE]
    assert entry.problems[0].values[0].name == "Bore Diameter" and entry.problems[0].sentence
    assert store.link_record_from_json(store.link_record_to_json(refused)) == refused
    at = ui_text.read_time(entry.read_at)
    footer, _ = _footer(refused, reducer(), digest="d2")
    assert f"Update SolidWorks refused at {at}, before changing anything: {entry.problems[0].sentence}" in footer.text
    assert footer.text.endswith("The next press reads your work in SolidWorks again, and refuses again unless that "
                                "has been dealt with.") and not footer.ok and footer.update_enabled
    footer, _ = _footer(refused, gears(reducer(), G2=dict(bore="14")), digest="d3")
    assert "The workbook has changed since, and the next press reads your work in SolidWorks again." in footer.text
    assert footer.ok
    # A later press that goes ahead replaces the refusal with what it read.
    plan2, result, finished = press(sw, refused, gears(reducer(), G2=dict(bore="14")))
    assert result.ok and finished.record.gearbox.user_work.problems == []


def test_nothing_of_the_users_read_says_nothing_and_a_static_gearbox_says_its_features_only(on_fake):
    sw, record = on_fake
    plan, result, finished = press(sw, record, reducer())
    record = finished.record
    assert record.gearbox.user_work is not None and not record.gearbox.user_work
    footer, _ = _footer(record, reducer())
    assert "As read at" not in footer.text and "your" not in footer.text


# -- Build again…: the question, and the build job's read of the old assembly -------------------------------------


def _again(record, spec, exists):
    a = assessed(spec)
    upd = update.classify(record, a, exists=lambda p: True)
    again = gearbox.plan_gearbox(a, record, exists=exists, read_sidecar=lambda p: None)
    return upd, again


def test_the_build_again_question_names_what_stays_behind_with_its_time(on_fake):
    sw, record = on_fake
    _sprocket(sw, record)
    sw.user_feature(next(p.path for p in record.current_parts() if "G4" in p.gears), "Groove")
    plan, result, finished = press(sw, record, reducer())
    record = finished.record
    at = ui_text.read_time(record.gearbox.user_work.read_at)
    upd, again = _again(record, gears(reducer(), G1=dict(flank="arcs")), sw.exists)
    assert upd.needs_new_revision and again.refusal == ""
    question = ui_text.build_again_question(upd, again, record=record)
    assert question.endswith(
        f" As read at {at}, your Sprocket-1 and Lock3 stay in Reducer_12to1.SLDASM, and your Keyway stays in "
        f"Gear_m1.5_N17, which G1's new part replaces; {again.name} has none of them, nor anything added since. Your "
        f"Groove in OutputGear comes with that part, which {again.name} reuses."), question
    # With nothing on record (or nothing of the user's read), a clause with no time (the coordinator's ruling 4).
    timeless = (" Anything you added to Reducer_12to1.SLDASM in SolidWorks (components, mates, and features in parts "
                f"this revision makes new) stays there, and {again.name} has none of it.")
    for empty in (None, store.UserWorkEntry(read_at="2026-11-16T14:02:00Z", assembly=record.gearbox.assembly)):
        bare = copy.deepcopy(record)
        bare.gearbox.user_work = empty
        assert ui_text.build_again_question(upd, again, record=bare) == \
            question[:question.index(" As read at")] + timeless


def _calls_from(sw, start):
    return [name for name, *_ in sw.calls[start:]]


READS = {"documents", "begin_build", "end_build", "use_open_document", "mate_states", "configurations", "components",
         "find_mate", "mate_info", "mate_suppression"}


def test_the_build_job_reads_the_old_assemblys_user_work_first_and_writes_nothing_to_it(on_fake):
    sw, record = on_fake
    _sprocket(sw, record)
    asm = record.gearbox.assembly
    old = update.old_assembly(record, _again(record, gears(reducer(), G1=dict(flank="arcs")), sw.exists)[1])
    assert old is not None and old.path == asm and ("G1", name2(record, "G1")) in old.components
    key = asm.replace("/", "\\").lower()
    mates_before = copy.deepcopy(sw.memory_mates[key])
    frames_before = copy.deepcopy(sw.frames)
    active, config, configs, touched = sw.active, sw.config, list(sw.configs), set(sw.touched)
    start = len(sw.calls)
    work = swbuild.read_old_assembly(sw, old)
    assert set(_calls_from(sw, start)) <= READS, _calls_from(sw, start)     # never opened nor activated
    assert sw.memory_mates[key] == mates_before and sw.frames == frames_before
    assert (sw.active, sw.config, sw.configs, sw.touched) == (active, config, configs, touched)
    assert [c.name for c in work.components] == ["Sprocket-1"]
    assert [(m.name, m.touches) for m in work.mates] == [("Lock3", (("app", "G1"), ("user", "Sprocket-1")))]
    # Not open in the session: not read, not opened.
    sw.open_docs = [d for d in sw.open_docs if d.path.lower() != asm.lower()]
    start = len(sw.calls)
    assert swbuild.read_old_assembly(sw, old) is None
    assert set(_calls_from(sw, start)) <= {"begin_build", "end_build", "use_open_document"}


def test_a_build_again_reads_what_stays_behind_first_and_says_it_after(on_fake):
    sw, record = on_fake
    _sprocket(sw, record)
    plan, result, finished = press(sw, record, reducer())
    record = finished.record
    spec = gears(reducer(), G1=dict(flank="arcs"))
    a = assessed(spec)
    again = gearbox.plan_gearbox(a, record, exists=sw.exists, read_sidecar=lambda p: None)
    old = update.old_assembly(record, again)
    start = len(sw.calls)
    built = swbuild.build_gearbox(sw, **again.build_kwargs(), exists=sw.exists, before=old)
    names = _calls_from(sw, start)
    first_write = next(i for i, n in enumerate(names) if n not in READS)
    assert "mate_info" in names[:first_write]               # the read came first, before anything was made
    assert built.old_read == "" and [c.name for c in built.old_user_work.components] == ["Sprocket-1"]
    stays = update.stays_behind(record, again)
    said = ui_text.stayed_behind_status(stays, built, again, old.path)
    at = ui_text.read_time(record.gearbox.user_work.read_at)
    assert said == (f"Your Sprocket-1 and Lock3 stay in Reducer_12to1.SLDASM, as read when this build began; "
                    f"{again.name} has none of them. As read at {at}, your Keyway stays in Gear_m1.5_N17, which G1's "
                    f"new part replaces; {again.name} has none of it, nor anything added since."), said
    # The old assembly closed: the record's inventory, with its time.
    gone = copy.deepcopy(built)
    gone.old_user_work, gone.old_read = None, swbuild.OLD_NOT_OPEN
    said = ui_text.stayed_behind_status(stays, gone, again, old.path)
    assert said.startswith("Reducer_12to1.SLDASM was not open in SolidWorks, so it was not read again; as read at "
                           f"{at}, your Sprocket-1 and Lock3 stay in Reducer_12to1.SLDASM"), said
    # Closed, and nothing on record: the old assembly named, no time.
    assert ui_text.stayed_behind_status(None, gone, again, old.path) == (
        "Reducer_12to1.SLDASM was not open in SolidWorks, so it was not read again; anything you added to "
        "Reducer_12to1.SLDASM in SolidWorks (components, mates, and features in parts this revision makes new) "
        f"stays there, and {again.name} has none of it.")


def test_an_old_assembly_read_that_raises_never_stops_the_build_and_is_said(on_fake, monkeypatch):
    """Package B's review, point 6: the build job's read of the old assembly meets SolidWorks failing; the build goes
    ahead whole, and its sentence says why it was not read, then what the record holds with its time."""
    sw, record = on_fake
    _sprocket(sw, record)
    plan, result, finished = press(sw, record, reducer())
    record = finished.record
    again = gearbox.plan_gearbox(assessed(gears(reducer(), G1=dict(flank="arcs"))), record, exists=sw.exists,
                                 read_sidecar=lambda p: None)
    old = update.old_assembly(record, again)

    def boom(handle):
        raise swbuild.SolidWorksError("SolidWorks stopped answering.")
    monkeypatch.setattr(sw, "mate_info", boom)
    built = swbuild.build_gearbox(sw, **again.build_kwargs(), exists=sw.exists, before=old)
    assert built.ok and built.old_user_work is None
    assert built.old_read == "SolidWorks did not answer the read of Reducer_12to1.SLDASM: SolidWorks stopped answering."
    said = ui_text.stayed_behind_status(update.stays_behind(record, again), built, again, old.path)
    assert said.startswith("SolidWorks did not answer the read of Reducer_12to1.SLDASM: SolidWorks stopped "
                           f"answering. As read at {ui_text.read_time(record.gearbox.user_work.read_at)}, your "
                           "Sprocket-1 and Lock3 stay in Reducer_12to1.SLDASM"), said


def test_after_update_the_sentence_says_what_went_with_its_gear_and_what_of_the_users_is_in_error(on_fake,
                                                                                                    monkeypatch):
    monkeypatch.setattr(findings, "USER_MATE_PUT_NO_CARRIER_ON_2026", True)
    sw, record = on_fake
    _sprocket(sw, record)
    spec = shafts(reducer(), S2=dict(x="64.5"), S3=dict(x="132.5"))
    plan, result, finished = press(sw, record, spec)
    assert result.ok and result.carried == [("Sprocket-1", "G1", "")]
    result.user_features_in_error = [swbuild.UserFeature(next(p.path for p in record.current_parts()
                                                              if "G1" in p.gears), "Keyway")]
    result.user_in_error = [("", "Lock3")]
    text, ok = ui_text.gearbox_update_status(plan, result, finished.dragged, finished=finished)
    assert "Your Sprocket-1 went with G1, which your locks hold it to." in text
    assert "SolidWorks rebuilt your Keyway in Gear_m1.5_N17 after the app's features, and it is in error." in text
    assert "Your Lock3 is in error in SolidWorks now." in text
    result.user_work.mates = [swbuild.UserMate(m.name, m.kind, m.type, m.touches, m.on, 7, True, m.whole)
                              for m in result.user_work.mates]          # Lock3 in error before anything changed
    text, ok = ui_text.gearbox_update_status(plan, result, finished.dragged, finished=finished)
    assert "Your Lock3 was in error in SolidWorks before this Update changed anything, and still is." in text


def test_a_carried_component_loaded_lightweight_is_foreseen_refused_as_the_press_refuses_it(on_fake, monkeypatch):
    """Package B's review, point 3: the check of a carried component suppressed or lightweight is in the shared pure
    judgement, so the footer foresees the refusal the press makes, from the state recorded."""
    monkeypatch.setattr(findings, "USER_MATE_PUT_NO_CARRIER_ON_2026", True)
    sw, record = on_fake
    _sprocket(sw, record)
    sw.component_states["Sprocket-1"] = 1                       # loaded lightweight
    plan, result, finished = press(sw, record, reducer())
    record = update.finish_update(plan, result, record, digest="d2", read_sidecar=lambda p: None,
                                  mtime=lambda p: 5.0, revision=(34, 1, 1)).record
    assert [(c.name, c.kind, c.state) for c in record.gearbox.user_work.components] == [("Sprocket-1", "part", 1)]
    moved = gears(reducer(), G4=dict(at="30"))
    footer, upd = _footer(record, moved)
    assert "would stop before changing anything: Update SolidWorks would put your Sprocket-1 with G1, which your " \
           "mates hold it to, and Sprocket-1 is loaded lightweight" in footer.text and not footer.ok, footer.text
    with pytest.raises(UserWorkRefused) as raised:
        swbuild.update_gearbox(sw, **upd.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    assert swbuild.PROBLEM_COMPONENT in [p.kind for p in raised.value.problems]


def test_after_a_refusal_the_workbook_changed_runs_the_prediction_too(on_fake):
    """The coordinator's ruling on package B's review, point 5: a quiet press refuses on a Bore the user typed alone
    (nothing is put, so the user's coincident mate on G1 is not judged); the workbook then takes the Bore and moves
    G4, and the footer says the old refusal, that the workbook has changed, and what the next press would do: stop
    over the mate on G1, which it now puts."""
    from test_workbook_user_work import _edit
    sw, record = on_fake
    asm = record.gearbox.assembly
    sw.user_component(asm, "Sprocket-1", r"C:\Parts\Sprocket.SLDPRT")
    sw.user_mate(asm, "Coinc7", kind="coincident", a=(name2(record, "G1"), "plane2"), b=("Sprocket-1", "plane1"))
    _edit(sw, next(p.path for p in record.current_parts() if "G2" in p.gears), "Bore Diameter", "14")
    plan = update.classify(record, assessed(reducer()), exists=lambda p: True)
    with pytest.raises(UserWorkRefused) as raised:
        swbuild.update_gearbox(sw, **plan.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    assert [p.kind for p in raised.value.problems] == [swbuild.PROBLEM_VALUE]
    refused = update.refused_update(record, plan, raised.value, digest="d2", revision=(34, 1, 1))
    footer, _ = _footer(refused, gears(reducer(), G2=dict(bore="14"), G4=dict(at="30")), digest="d3")
    at = ui_text.read_time(refused.gearbox.user_work.read_at)
    assert "The workbook has changed since, and the next press reads your work in SolidWorks again. As read at " \
           f"{at}, Update SolidWorks would stop before changing anything: Coinc7 is a mate" in footer.text, footer.text
    assert not footer.ok and footer.update_enabled
