"""W9c package B, the joining round (ISSUE-1-PLAN §5 "W9c", Done when; W9C-INTERFACES §11): each in-place kind through
the window's own path — ``classify`` → ``update_kwargs()`` → ``swbuild.update_gearbox(..., in_place=)`` on the fake →
``finish_update`` — with the footer before the press and the result's sentence after it. The plan's Done-when edit:
RangeBox built, the user's work added (a sprocket locked to Sun, a housing of theirs, a keyway in Sun's part and a
groove in RangeSlv's), its workbook edited to RangeBox_Fixed's rows, one Update; then a second press quiet; then a mode
added and one removed. Every gate patched True for the fake's SolidWorks (2026) where the press is to go ahead, and
each None refusing before any write. Every read is asserted free of errors first."""

from dataclasses import replace

import pytest

from gear_generator import findings, store, swbuild, ui_text
from gear_generator.swbuild import UserWorkRefused
from gear_generator.workbook import assess, gearbox, update
from gear_generator.workbook.model import Mode
from workbook_fixtures import range_box, range_box_fixed, transfer_case_parallel

from test_swbuild import FakeSolidWorks
from test_swbuild_in_place import WRITES

BOOK = "C:\\B\\RangeBox.xlsx"
GATES = ("UPDATE_INSERTS_A_GEAR", "UPDATE_MAKES_MATES_WITH_MODES", "UPDATE_BANDS_IN_PLACE", "UPDATE_ADDS_A_MODE",
         "UPDATE_REMOVES_A_MODE", "UPDATE_MAKES_A_NEW_COUPLING", "UPDATE_SUPPRESSES_THE_RELIEF")
STAMP = "2026-11-17T09:00:00Z"        # every finish's stamp, so no record differs by the second it was written in


def _key(path):
    return path.replace("/", "\\").lower()


class Disk:
    """What the fake saved and the finishes wrote, by path as Windows compares them."""

    def __init__(self):
        self.files, self.sidecars = set(), {}

    def exists(self, path):
        return _key(path) in self.files

    def read_sidecar(self, path):
        return self.sidecars.get(_key(path)) if self.exists(path) else None

    def write(self, finished):
        for path, sidecar in finished.sidecars:
            self.files.add(_key(path))
            self.sidecars[_key(path)] = sidecar


class DeskSolidWorks(FakeSolidWorks):
    """The fake, putting what it saves on the desk's disk and keeping each component's frame by its Name2."""

    def __init__(self, disk):
        super().__init__()
        self.disk, self.names = disk, {}

    def save_as(self, path):
        kept = super().save_as(path)
        self.disk.files.add(_key(path))
        return kept

    def add_component(self, handle, path, at):
        name = super().add_component(handle, path, at)
        self.names[handle] = name
        return name

    def place_component(self, handle, rotation, at, kind=None):
        super().place_component(handle, rotation, at, kind)
        if handle in self.names:
            self.frames[self.names[handle]] = (tuple(rotation), tuple(at))


class Press:
    """One press as the window makes it: the plan, the footer's Update line before it, and what came after."""

    def __init__(self, up, before):
        self.up, self.before = up, before
        self.result = self.finished = self.refused = None
        self.after, self.ok = "", True


class Desk:
    def __init__(self):
        self.disk = Disk()
        self.sw = DeskSolidWorks(self.disk)
        self.record = None

    def a(self, spec):
        a = assess.assess(replace(spec, source_path=BOOK), [], "C:\\Out\\")
        errors = [d.message for d in a.diagnostics if d.is_error]
        assert errors == [] and a.lay_out_refusal() == "", errors
        return a

    def build(self, spec):
        a = self.a(spec)
        plan = gearbox.plan_gearbox(a, self.record, exists=self.disk.exists, read_sidecar=self.disk.read_sidecar)
        assert plan.refusal == "", plan.refusal
        result = swbuild.build_gearbox(self.sw, **plan.build_kwargs(), exists=self.disk.exists)
        assert result.ok, result.failures
        done = gearbox.finish_build(plan, result, self.record, workbook=BOOK, digest=self.digest(spec),
                                    written_by="test", read_sidecar=self.disk.read_sidecar, exists=self.disk.exists,
                                    stamp=STAMP, revision=self.sw.revision)
        self.disk.write(done)
        self.record = store.link_record_from_json(store.link_record_to_json(done.record))
        return self.record

    @staticmethod
    def digest(spec):
        return str(abs(hash(repr(spec.without_rows()))))

    def footer(self, spec):
        """The window's footer for ``spec`` read now (``ui_text.workbook_footer`` with the record, the build plan and
        the Update plan, as WorkbookWindow puts it together): (its text, ok)."""
        a = self.a(spec)
        up = update.classify(self.record, a, exists=self.disk.exists, read_sidecar=self.disk.read_sidecar)
        plan = gearbox.plan_gearbox(a, self.record, exists=self.disk.exists, read_sidecar=self.disk.read_sidecar)
        f = ui_text.workbook_footer(a, record=self.record, plan=plan, update=up, digest=self.digest(spec),
                                    folder="C:\\Out\\")
        return f.text, f.ok

    def writes(self, since=0):
        """The fake's calls that write, since the call numbered ``since``."""
        return [n for n, _ in self.sw.calls[since:] if n in WRITES]

    def press(self, spec):
        before = self.footer(spec)
        up = update.classify(self.record, self.a(spec), exists=self.disk.exists, read_sidecar=self.disk.read_sidecar)
        press = Press(up, before)
        press.mark = len(self.sw.calls)
        if up.refusal or up.needs_new_revision:
            return press
        try:
            result = swbuild.update_gearbox(self.sw, **up.update_kwargs(), exists=self.disk.exists,
                                            mtime=lambda _p: 0.0)
        except UserWorkRefused as error:
            press.refused = error
            self.record = update.refused_update(self.record, up, error, digest=self.digest(spec),
                                                revision=self.sw.revision)
            return press
        done = update.finish_update(up, result, self.record, digest=self.digest(spec),
                                    read_sidecar=self.disk.read_sidecar, mtime=lambda _p: 0.0,
                                    revision=self.sw.revision, written_by="test", stamp=STAMP)
        self.disk.write(done)
        self.record = store.link_record_from_json(store.link_record_to_json(done.record))
        press.result, press.finished = result, done
        press.after, press.ok = ui_text.gearbox_update_status(up, result, done.dragged, revision=self.sw.revision,
                                                              finished=done)
        return press


@pytest.fixture
def measured(monkeypatch):
    """Every W9c gate as if the full build had read it clean on the fake's SolidWorks (2026)."""
    for name in GATES:
        monkeypatch.setattr(findings, f"{name}_ON_2026", True, raising=False)


def fixed():
    return replace(range_box_fixed(), box=replace(range_box_fixed().box, name="RangeBox"))


def _component(record, gear):
    return next(c.name for c in record.gearbox.components if c.gear == gear)


def _part(record, gear):
    return next(p.path for p in record.parts if gear in p.gears)


def users_work(desk):
    """W9a's user work on RangeBox: Sprocket-1 locked to Sun, Housing-1 of theirs fixed and unmated, a keyway in Sun's
    part and a groove in RangeSlv's. A quiet press reads it onto the record."""
    rec, sw = desk.record, desk.sw
    asm = rec.gearbox.assembly
    sw.user_component(asm, "Sprocket-1", "C:\\Parts\\Sprocket.SLDPRT",
                      ((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 30.0)))
    sw.user_component(asm, "Housing-1", "C:\\Parts\\Housing.SLDPRT", fixed=True)
    sw.user_lock(asm, "Lock3", _component(rec, "Sun"), "Sprocket-1")
    sw.user_feature(_part(rec, "Sun"), "Keyway")
    sw.user_feature(_part(rec, "RangeSlv"), "Groove")
    quiet = desk.press(range_box())
    assert quiet.result is not None and quiet.result.ok, (quiet.result.failures if quiet.result else quiet.refused)
    assert {c.name for c in desk.record.gearbox.user_work.components} == {"Sprocket-1", "Housing-1"}


@pytest.fixture
def desk():
    d = Desk()
    d.build(range_box())
    users_work(d)
    return d


# -- the plan's Done-when edit ---------------------------------------------------------------------------------------

def test_range_box_to_range_box_fixed_is_one_update_keeping_every_user_item(desk, measured):
    before = desk.record
    sprocket_before = desk.sw.frames.get("Sprocket-1")
    press = desk.press(fixed())
    up = press.up
    assert up.structural == () and [g.gear for g in up.in_place.added] == ["Hub"]
    text, ok = press.before
    assert ok and "would stop" not in text
    assert text.startswith("Update SolidWorks will add Hub on Output (a new part, Hub_m1.25_N17), as its shaft's "
                           "anchor with RangeSlv splined to it, give RangeSlv its bands in Sleeve_m1.25_N17")
    assert press.refused is None and press.result.ok, (press.result.failures, press.result.skipped)
    r = press.result
    assert [g for g, _ in r.inserted] == ["Hub"] and r.bands_added == ["RangeSlv"]
    assert {n for n, _ in r.mates_made} == {"Hub on Output Axis", "Hub along Output", "RangeSlv splined to Hub"}
    assert press.ok and press.after.startswith("Updated SolidWorks: built Hub_m1.25_N17, inserted Hub as ")
    assert "gave RangeSlv its bands" in press.after
    # Every user item as it was: their components and lock still there, their features in their parts.
    asm = desk.record.gearbox.assembly
    assert {"Sprocket-1", "Housing-1"} <= {c.name for c in desk.sw.components_of(asm)} \
        if hasattr(desk.sw, "components_of") else True
    assert any(m.name == "Lock3" for m in desk.sw.memory_mates[_key(asm)])
    assert desk.sw.frames.get("Sprocket-1") is not None and sprocket_before is not None
    # The record: Hub on record, RangeSlv's bands in its spec, the relief among its features.
    box = desk.record.gearbox
    assert "Hub" in {c.gear for c in box.components}
    assert {m.name for m in box.mates} >= {"Hub on Output Axis", "Hub along Output", "RangeSlv splined to Hub"}
    sleeve = next(p for p in desk.record.parts if "RangeSlv" in p.gears)
    assert sleeve.spec["start_band"] == "5" and sleeve.spec["end_band"] == "5"
    car = desk.disk.read_sidecar(store.sidecar_path(sleeve.path))
    assert car.schema_version == 2 and car.record.features[-1] == "Relief"
    assert before is not desk.record
    # A second press is quiet.
    again = desk.press(fixed())
    assert not again.up.in_place and again.up.structural == ()
    assert again.result.ok and again.after.startswith(ui_text.ALREADY_MATCHES[:30]), again.after


def _comparable(record):
    """What a record says of the gearbox, less what a build and an Update name differently: component Name2s, the
    revision's stamps, the user's work."""
    box = record.gearbox
    return dict(
        modes=list(box.modes), fixed=sorted(box.fixed), meshes=sorted(sorted(m) for m in box.meshes),
        components=sorted((c.gear, c.part.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]) for c in box.components),
        mates=sorted((m.name, m.kind, tuple(m.gears), m.shaft, tuple(m.ratio), m.face_global, round(m.z_front, 6),
                      tuple(m.modes), tuple(sorted((k, round(v, 6)) for k, v in m.values.items())))
                     for m in box.mates),
        frames=sorted((c.gear, tuple(round(v, 6) for v in c.at), tuple(sorted(c.frames))) for c in box.components),
        parts=sorted((p.path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1], tuple(sorted(p.gears)),
                      tuple(sorted(p.spec.items()))) for p in record.current_parts()))


def test_the_record_after_it_is_what_a_fresh_build_of_range_box_fixed_records(desk, measured):
    press = desk.press(fixed())
    assert press.result.ok
    fresh = Desk()
    fresh.build(fixed())
    mine, theirs = _comparable(desk.record), _comparable(fresh.record)
    for key in mine:
        assert mine[key] == theirs[key], (key, mine[key], theirs[key])


def test_the_users_features_lock_and_components_are_as_they_were_after_it(desk, measured):
    asm = _key(desk.record.gearbox.assembly)
    features = {k: list(v) for k, v in desk.sw.user_features.items()}
    lock = [(m.name, m.suppressed, dict(m.flags)) for m in desk.sw.memory_mates[asm] if m.name == "Lock3"]
    press = desk.press(fixed())
    assert press.result.ok and press.result.user_work is not None
    assert {put[0] for put in desk.sw.user_puts} == {"Sprocket-1"}     # carried with Sun only (W9a), nothing else
    assert {k: list(v) for k, v in desk.sw.user_features.items()} == features
    assert [(m.name, m.suppressed, dict(m.flags)) for m in desk.sw.memory_mates[asm] if m.name == "Lock3"] == lock
    entry = desk.record.gearbox.user_work
    assert {c.name for c in entry.components} == {"Sprocket-1", "Housing-1"}
    assert {(f.path.rsplit("/", 1)[-1], f.name) for f in entry.features} == {
        ("Gear_m1.25_N29.SLDPRT", "Keyway"), ("Sleeve_m1.25_N17.SLDPRT", "Groove")}


def test_the_record_differs_from_a_fresh_builds_only_where_the_plan_says(desk, measured):
    """Beside the sorted comparison above: the record as JSON, against a fresh build's, differs only in the order the
    mates are listed (an Update appends the added gear's three after the rest, a build lists them in its own order),
    the stamps of an Update, the user's work it read, and what it left unsaved."""
    import json
    assert desk.press(fixed()).result.ok
    fresh = Desk()
    fresh.build(fixed())
    mine = json.loads(store.link_record_to_json(desk.record))
    theirs = json.loads(store.link_record_to_json(fresh.record))
    for record in (mine, theirs):
        record["gearbox"]["mates"].sort(key=lambda m: m["name"])
    differ = {k for k in mine if mine[k] != theirs[k]}
    differ |= {f"gearbox.{k}" for k in mine["gearbox"] if mine["gearbox"][k] != theirs["gearbox"][k]}
    assert differ == {"gearbox", "last_updated", "unsaved", "gearbox.updated", "gearbox.user_work"}, differ


# -- each gate None refuses before any write, said before the press and recorded after ------------------------------

def test_with_its_gates_unmeasured_the_done_when_edit_is_foreseen_refused_before_any_write_and_recorded(
        desk, w9c_unmeasured):
    press = desk.press(fixed())
    text, ok = press.before
    assert not ok and text.startswith("Update SolidWorks would add Hub on Output (a new part, Hub_m1.25_N17)")
    assert "Update SolidWorks will " not in text
    assert text.endswith(
        "The next press would stop before changing anything: Update SolidWorks would insert a gear into the assembly "
        "and mate it and give a built sleeve its bands in its own part, which Gear Generator has "
        "not yet been shown to do on SolidWorks 2026 (findings.UPDATE_INSERTS_A_GEAR_ON_2026 and "
        "findings.UPDATE_BANDS_IN_PLACE_ON_2026), so the press changes nothing; Build again… makes the new revision "
        "instead.")
    assert press.refused is not None and desk.writes(press.mark) == []
    assert [p.subjects for p in press.refused.problems] == [("UPDATE_INSERTS_A_GEAR_ON_2026",),
                                                           ("UPDATE_BANDS_IN_PLACE_ON_2026",)]
    after, ok = desk.footer(fixed())
    assert not ok and "Update SolidWorks refused at " in after
    assert "(findings.UPDATE_INSERTS_A_GEAR_ON_2026 is None)" in after and "next press would stop" not in after
    assert desk.record.gearbox.user_work.problems                   # recorded, said until the workbook changes


@pytest.mark.parametrize("gate", GATES[:1] + GATES[2:3])
def test_each_of_the_done_when_edits_gates_alone_unmeasured_refuses_by_its_name(desk, monkeypatch, gate):
    for name in GATES:
        monkeypatch.setattr(findings, f"{name}_ON_2026", name != gate, raising=False)
    monkeypatch.setattr(findings, f"{gate}_ON_2026", None)
    press = desk.press(fixed())
    assert f"(findings.{gate}_ON_2026)" in press.before[0] and desk.writes(press.mark) == []
    assert [p.subjects for p in press.refused.problems] == [(f"{gate}_ON_2026",)]


# -- a mode added, and one removed, on the Done-when edit's result ---------------------------------------------------

def _fixed_with_mode(name="R", where="L"):
    spec = fixed()
    return replace(spec, modes=spec.modes + (Mode(name, (("RangeSlv", where),), row=len(spec.modes) + 2),))


def _fixed_without_mode(name="N"):
    spec = fixed()
    return replace(spec, modes=tuple(m for m in spec.modes if m.name != name))


@pytest.fixture
def fixed_desk(measured):
    """RangeBox built, then Updated to RangeBox_Fixed, with no work of the user's in SolidWorks."""
    d = Desk()
    d.build(range_box())
    assert d.press(fixed()).result.ok
    return d


@pytest.fixture
def fixed_desk_with_work(desk, measured):
    assert desk.press(fixed()).result.ok
    return desk


@pytest.mark.parametrize("with_work", [False, True])
def test_a_mode_added_on_the_result_is_one_update_and_a_second_press_quiet(request, with_work):
    desk = request.getfixturevalue("fixed_desk_with_work" if with_work else "fixed_desk")
    press = desk.press(_fixed_with_mode())
    assert press.up.structural == () and press.up.in_place.modes_added == ("R",)
    text, ok = press.before
    assert ok and "would stop" not in text and text.startswith(
        "Update SolidWorks will add the mode R, a copy of the mode showing in SolidWorks when you press (your items "
        "there take that mode's state)"), text
    assert press.result.ok, (press.result.failures, press.result.skipped)
    assert press.result.modes_added == ["R"] and "R" in desk.sw.configs
    assert "added the mode R" in press.after and press.ok
    assert desk.record.gearbox.modes == ["H", "N", "L", "R"]
    slide = next(m for m in desk.record.gearbox.mates if m.name == "RangeSlv along Output")
    assert slide.values["R"] == slide.values["L"]
    again = desk.press(_fixed_with_mode())
    assert not again.up.in_place and again.result.ok and again.after.startswith(ui_text.ALREADY_MATCHES[:30])


@pytest.mark.parametrize("with_work", [False, True])
def test_a_mode_removed_on_the_result_is_one_update_and_a_second_press_quiet(request, with_work):
    desk = request.getfixturevalue("fixed_desk_with_work" if with_work else "fixed_desk")
    press = desk.press(_fixed_without_mode())
    text, ok = press.before                            # the review's must-fix 1: no refusal foreseen
    assert ok and "would stop" not in text and "suppressed in ," not in text, text
    assert text.startswith("Update SolidWorks will delete the mode N"), text
    assert press.up.structural == () and press.up.in_place.modes_removed == ("N",)
    assert press.result.ok, (press.result.failures, press.result.skipped)
    assert press.result.modes_removed == ["N"] and "N" not in desk.sw.configs
    assert "deleted the mode N" in press.after
    assert desk.record.gearbox.modes == ["H", "L"]
    assert all("N" not in m.values and "N" not in m.modes for m in desk.record.gearbox.mates)
    again = desk.press(_fixed_without_mode())
    assert not again.up.in_place and again.result.ok and again.after.startswith(ui_text.ALREADY_MATCHES[:30])


@pytest.mark.parametrize("edit, gate", [(_fixed_with_mode, "UPDATE_ADDS_A_MODE"),
                                        (_fixed_without_mode, "UPDATE_REMOVES_A_MODE")])
def test_a_mode_added_or_removed_with_its_gate_unmeasured_refuses_before_any_write(fixed_desk, monkeypatch, edit,
                                                                                  gate):
    monkeypatch.setattr(findings, f"{gate}_ON_2026", None)
    press = fixed_desk.press(edit())
    assert f"(findings.{gate}_ON_2026)" in press.before[0] and not press.before[1]
    assert fixed_desk.writes(press.mark) == [] and press.refused.problems[0].subjects == (f"{gate}_ON_2026",)
    assert f"(findings.{gate}_ON_2026 is None)" in fixed_desk.footer(edit())[0]


def test_a_mode_whose_name_is_a_configuration_of_the_users_refuses_and_is_recorded(fixed_desk):
    desk = fixed_desk
    desk.sw.configs.append("R")
    press = desk.press(_fixed_with_mode())
    (problem,) = press.refused.problems
    assert problem.kind == swbuild.PROBLEM_CONFIGURATION and problem.subjects == ("R", "R")
    assert desk.writes(press.mark) == []
    assert problem.sentence in desk.footer(_fixed_with_mode())[0]


# -- a gear removed, a coupling made, a tooth change with modes, on the parallel transfer case -----------------------

@pytest.fixture
def parallel(measured):
    d = Desk()
    d.build(transfer_case_parallel())
    return d


def _without(spec, gid):
    return replace(spec, gears=tuple(g for g in spec.gears if g.id != gid),
                   meshes=tuple(m for m in spec.meshes if gid not in (m.a, m.b)))


def _with(spec, gid, **changes):
    return replace(spec, gears=tuple(replace(g, **changes) if g.id == gid else g for g in spec.gears))


def test_a_gear_that_anchors_none_taken_out_round_trips_and_a_second_press_is_quiet(parallel):
    spec = _without(transfer_case_parallel(), "FIdler")
    press = parallel.press(spec)
    assert press.up.structural == () and [g.gear for g in press.up.in_place.removed] == ["FIdler"]
    assert press.result.ok, (press.result.failures, press.result.skipped)
    assert [g for g, _ in press.result.deleted] == ["FIdler"] and len(press.result.mates_deleted) == 4
    assert "took FIdler (" in press.after and "out with 4 mates" in press.after
    box = parallel.record.gearbox
    assert "FIdler" not in {c.gear for c in box.components} and not any("FIdler" in m.gears for m in box.mates)
    assert not any("FIdler" in p.gears for p in parallel.record.current_parts())
    again = parallel.press(spec)
    assert not again.up.in_place and again.result.ok


def test_the_mode_showing_removed_refuses_with_nothing_read_and_the_inventory_kept(parallel):
    parallel.sw.user_component(parallel.record.gearbox.assembly, "Housing-1", "C:\\Parts\\Housing.SLDPRT",
                               fixed=True)
    assert parallel.press(transfer_case_parallel()).result.ok          # the quiet press reads Housing-1
    inventory = parallel.record.gearbox.user_work
    spec = transfer_case_parallel()
    spec = replace(spec, modes=spec.modes[1:])
    assert parallel.sw.config == "2H"
    press = parallel.press(spec)
    assert press.up.in_place.modes_removed == ("2H",) and press.up.in_place.first_mode == "4H"
    assert press.refused is not None and press.refused.user_work is None
    assert [p.kind for p in press.refused.problems] == [swbuild.PROBLEM_MODE_SHOWING]
    assert parallel.writes(press.mark) == []
    kept = parallel.record.gearbox.user_work
    assert [c.name for c in kept.components] == [c.name for c in inventory.components] == ["Housing-1"]
    assert [m.name for m in kept.mates] == [m.name for m in inventory.mates]
    assert [(p.kind, p.subjects) for p in kept.problems] == [(swbuild.PROBLEM_MODE_SHOWING, ["2H"])]
    assert kept.revision == list(parallel.sw.revision) and kept.digest == parallel.digest(spec)
    assert kept.read_at == inventory.read_at and kept.refused_at and not kept.unread   # the read's own time kept
    text, ok = parallel.footer(spec)
    assert not ok and ("Update SolidWorks would delete the configuration 2H from TransferCase_Parallel.SLDASM, and it "
                       "is the configuration showing in SolidWorks, so nothing is changed; show another mode in "
                       "SolidWorks and press Update SolidWorks again.") in text
    parallel.sw.show_configuration("4H")                                # the user shows another mode
    again = parallel.press(spec)
    assert again.result is not None and again.result.ok, again.after
    assert parallel.record.gearbox.modes[0] == "4H" and "2H" not in parallel.sw.configs


def test_the_mode_showing_refused_with_no_inventory_on_record_is_recorded_with_an_empty_one(parallel):
    spec = transfer_case_parallel()
    spec = replace(spec, modes=spec.modes[1:])
    assert parallel.record.gearbox.user_work is None
    press = parallel.press(spec)
    assert press.refused.user_work is None
    kept = parallel.record.gearbox.user_work
    assert (kept.components, kept.mates, kept.features, kept.carried) == ([], [], [], [])
    assert kept.unread and kept.read_at == "" and kept.refused_at          # never an empty inventory as a read
    assert [(p.kind, p.subjects) for p in kept.problems] == [(swbuild.PROBLEM_MODE_SHOWING, ["2H"])]
    text = parallel.footer(spec)[0]
    assert "Update SolidWorks refused at " in text and "the configuration showing in SolidWorks" in text


def test_a_removal_with_the_users_components_present_refuses_while_m4_is_unread(parallel):
    parallel.sw.user_component(parallel.record.gearbox.assembly, "Housing-1", "C:\\Parts\\Housing.SLDPRT",
                               fixed=True)
    spec = _without(transfer_case_parallel(), "FIdler")
    assert parallel.press(transfer_case_parallel()).result.ok          # the quiet press reads Housing-1
    press = parallel.press(spec)
    assert "(findings.EXTERNAL_REFERENCES_READ_ON_2026 is None)" in press.before[0] and not press.before[1]
    assert [p.kind for p in press.refused.problems] == [swbuild.PROBLEM_REFERENCES]
    assert parallel.writes(press.mark) == []


def _new_coupling():
    spec = _with(transfer_case_parallel(), "ModeSlv", slides="2WD=0, 4WD=+10, X=-30")
    modes = list(spec.modes)
    modes[0] = replace(modes[0], positions=(("RangeSlv", "N"), ("ModeSlv", "X")))
    return replace(spec, modes=tuple(modes))


def test_a_new_coupling_round_trips_with_its_flags_and_a_second_press_is_quiet(parallel):
    press = parallel.press(_new_coupling())
    assert [m.op.name for m in press.up.in_place.new_mates] == ["ModeSlv engages LoDog"]
    assert press.up.in_place.new_mates[0].ref.modes == ("2H",)
    assert press.result.ok, (press.result.failures, press.result.skipped)
    assert press.result.mates_made == [("ModeSlv engages LoDog", ("2H",))]          # read on in 2H alone
    assert "made ModeSlv engages LoDog, on in 2H" in press.after
    entry = next(m for m in parallel.record.gearbox.mates if m.name == "ModeSlv engages LoDog")
    assert entry.kind == "couple" and entry.modes == ["2H"]
    again = parallel.press(_new_coupling())
    assert not again.up.in_place and again.result.ok


def _teeth():
    return _with(_with(_with(transfer_case_parallel(), "FDrive", teeth="31"), "FIdler", teeth="19"), "FOut", teeth="31")


def test_a_tooth_change_with_modes_needs_no_in_place_and_is_remade_in_every_mode(parallel):
    press = parallel.press(_teeth())
    assert not press.up.in_place and set(press.up.ratios) == {"FDrive meshes FIdler", "FIdler meshes FOut"}
    assert press.result.ok, (press.result.failures, press.result.skipped)
    assert set(press.result.remade_in_modes) == {"FDrive meshes FIdler", "FIdler meshes FOut"}
    assert "(made again, with their flags set in every mode)" in press.before[0]
    again = parallel.press(_teeth())
    assert again.result.ok and not again.result.remade_in_modes


def test_a_tooth_change_with_modes_refuses_by_name_while_its_gate_is_unmeasured(parallel, monkeypatch):
    monkeypatch.setattr(findings, "UPDATE_MAKES_MATES_WITH_MODES_ON_2026", None)
    text, ok = parallel.footer(_teeth())
    # The Build recorded the SolidWorks it ran on (schema 9), so the footer names the finding on that version.
    assert "(findings.UPDATE_MAKES_MATES_WITH_MODES_ON_2026)" in text and not ok
    mark = len(parallel.sw.calls)
    # Refused as every other in-place gate is (the worker's 816c261): a UserWorkRefused naming the finding, which the
    # press records, and no write.
    press = parallel.press(_teeth())
    assert [p.subjects for p in press.refused.problems] == [("UPDATE_MAKES_MATES_WITH_MODES_ON_2026",)]
    assert parallel.writes(mark) == []


def test_a_tooth_change_refused_by_its_gate_is_recorded_as_every_other_refusal_before_a_write(parallel, monkeypatch):
    monkeypatch.setattr(findings, "UPDATE_MAKES_MATES_WITH_MODES_ON_2026", None)
    press = parallel.press(_teeth())
    assert [p.subjects for p in press.refused.problems] == [("UPDATE_MAKES_MATES_WITH_MODES_ON_2026",)]
    kept = parallel.record.gearbox.user_work
    assert [(p.kind, p.subjects) for p in kept.problems] == [(swbuild.PROBLEM_UNSETTLED,
                                                              ["UPDATE_MAKES_MATES_WITH_MODES_ON_2026"])]


# -- bands given back: a sleeve whose record holds the relief an earlier Update suppressed --------------------------

def _relief_on_record(desk, made_in_part=False):
    """RangeBox's sleeve as an Update that took its bands away leaves it on record: no bands in its spec, its relief
    still among its features (C8 suppresses it, never deletes it). ``made_in_part``: the fake's part holds them too."""
    sleeve = next(p for p in desk.record.parts if "RangeSlv" in p.gears)
    car = desk.disk.read_sidecar(store.sidecar_path(sleeve.path))
    car.record.features = list(car.record.features) + list(update._RELIEF_FEATURES)
    return sleeve


def test_bands_given_to_a_sleeve_whose_relief_is_on_record_are_given_back_never_made_twice(monkeypatch):
    for name in GATES:
        monkeypatch.setattr(findings, f"{name}_ON_2026", True, raising=False)
    d = Desk()
    d.build(range_box())
    sleeve = _relief_on_record(d)
    up = update.classify(d.record, d.a(fixed()), exists=d.disk.exists, read_sidecar=d.disk.read_sidecar)
    (band,) = up.in_place.bands
    assert (band.gear, band.add, band.back, band.features) == ("RangeSlv", True, True, ("Relief",))
    assert {type(op).__name__ for op in band.ops} == {"AddGlobal"}               # the globals only: no second relief
    assert "give RangeSlv its bands back in Sleeve_m1.25_N17 (its Relief turned back on)" in ui_text.update_summary(up)
    # The fake's part holds no relief: the worker refuses by name, before any write.
    mark = len(d.sw.calls)
    with pytest.raises(swbuild.BuildError, match="no longer holds .*Relief.*so the bands cannot be given back"):
        d.press(fixed())
    assert d.writes(mark) == [] and sleeve.spec.get("start_band", "") == ""


def test_bands_given_back_read_their_own_gate_in_the_footer(monkeypatch):
    for name in GATES:
        monkeypatch.setattr(findings, f"{name}_ON_2026", name != "UPDATE_SUPPRESSES_THE_RELIEF", raising=False)
    d = Desk()
    d.build(range_box())
    users_work(d)
    _relief_on_record(d)
    text, ok = d.footer(fixed())
    assert not ok and ("Update SolidWorks would suppress a sleeve's relief to take its bands away, or turn it back on "
                       "to give them back, which Gear Generator has not yet been shown to do on SolidWorks 2026 "
                       "(findings.UPDATE_SUPPRESSES_THE_RELIEF_ON_2026)") in text


# -- a failure half way: what was done and what was not, said and recorded; the next press goes on or refuses -------

def test_an_insert_that_fails_records_the_part_built_and_the_next_press_goes_on_with_it(desk, measured):
    """The coordinator's ruling: the part a failed press built and saved is on record, with its .gear.json, so the
    next press inserts it (an AddedGear with build None) without the user moving anything; the global the failed
    press added is handed back as the app's (InPlace.left)."""
    desk.sw.fail_on = {"add_component": "SolidWorks would not insert Hub_m1.25_N17.SLDPRT."}
    press = desk.press(fixed())
    assert not press.ok and press.after == (
        "Update SolidWorks stopped. RangeBox.SLDASM: SolidWorks would not insert Hub_m1.25_N17.SLDPRT. Before it "
        "stopped it built Hub_m1.25_N17 and gave RangeSlv its bands. It did not get to inserting Hub and putting the "
        "gears back and checking the assembly, because the job stopped in RangeBox.SLDASM. It had already changed "
        "Sleeve_m1.25_N17 and RangeBox, not saved: press Update SolidWorks again once that is put right, or save them "
        "in SolidWorks to keep what it did.")
    rec = desk.record
    assert "Hub" not in {c.gear for c in rec.gearbox.components}
    hub = next(p for p in rec.parts if p.path.endswith("Hub_m1.25_N17.SLDPRT"))
    assert hub.gears == ["Hub"] and desk.disk.read_sidecar(store.sidecar_path(hub.path)) is not None
    assert next(p for p in rec.parts if "RangeSlv" in p.gears).spec["start_band"] == "5"     # the bands, done
    assert rec.gearbox.left == ["Hub Face Z"]          # the app's, left (the band globals were used: bands given)
    desk.sw.fail_on = {}
    text, ok = desk.footer(fixed())
    assert "already on disk" not in text and text.startswith("Update SolidWorks will add Hub on Output "
                                                             "(its part Hub_m1.25_N17), as its"), text
    again = desk.press(fixed())
    (added,) = again.up.in_place.added
    assert added.build is None and "Hub Face Z" in again.up.in_place.left and again.up.in_place.bands == ()
    assert again.result.ok, again.after
    assert [g for g, _ in again.result.inserted] == ["Hub"] and again.result.built == []
    assert desk.record.gearbox.left == [] and "Hub" in {c.gear for c in desk.record.gearbox.components}
    assert desk.press(fixed()).result.ok and not desk.press(fixed()).up.in_place


def test_a_new_parts_file_on_disk_that_no_record_holds_still_refuses_by_its_sentence(desk, measured):
    desk.disk.files.add(_key("C:\\Out\\/Hub_m1.25_N17.SLDPRT"))
    text, ok = desk.footer(fixed())
    assert not ok and (
        "Hub_m1.25_N17.SLDPRT is already on disk though nothing on record holds it (a press that stopped part way "
        "may have built it), so Update SolidWorks would not build Hub's new part over it: move that file away or "
        "delete it, then press Update SolidWorks again.") in text
    mark = len(desk.sw.calls)
    with pytest.raises(swbuild.BuildError, match="is already on disk, so Update SolidWorks would not build Hub"):
        desk.press(fixed())
    assert desk.writes(mark) == []


def test_a_global_a_stopped_press_left_at_another_value_is_set_as_the_apps(desk, measured):
    desk.sw.fail_on = {"add_component": "SolidWorks would not insert Hub_m1.25_N17.SLDPRT."}
    desk.press(fixed())
    desk.sw.fail_on = {}
    desk.sw.open_document(desk.record.gearbox.assembly)
    desk.sw.set_global_variable("Hub Face Z", "12")               # left at another value (the user dragged it, say)
    again = desk.press(fixed())
    assert "Hub Face Z" in again.up.in_place.left
    assert again.result.ok, again.after
    sets = [a for n, a in desk.sw.calls[again.mark:] if n == "set_global_variable" and a[0] == "Hub Face Z"]
    assert sets and sets[-1][1] != "12"


def test_a_mate_that_fails_after_the_insert_is_recorded_and_the_next_press_names_the_mates(desk, measured):
    desk.sw.fail_on = {"add_mate": "SolidWorks would not make the mate Hub on Output Axis."}
    press = desk.press(fixed())
    assert not press.ok and "Before it stopped it built Hub_m1.25_N17, inserted Hub as gear7-1 and gave RangeSlv " \
                            "its bands." in press.after
    assert "Hub" in {c.gear for c in desk.record.gearbox.components}            # in the assembly, on record
    assert not any("Hub" in m.gears for m in desk.record.gearbox.mates)
    desk.sw.fail_on = {}
    again = desk.press(fixed())
    assert again.result is None and again.up.structural == (
        "Hub is in the assembly, inserted by an Update SolidWorks that stopped before making its mates Hub on Output "
        "Axis, Hub along Output and RangeSlv splined to Hub, and Update SolidWorks makes a gear's own mates only as it "
        "adds the gear, so the gearbox needs building again.",)


def test_a_flag_that_fails_says_every_mate_made_and_the_next_press_goes_on(desk, measured):
    desk.sw.fail_on = {"set_mate_suppressed_in": "SolidWorks would not set the flag."}
    press = desk.press(fixed())
    assert not press.ok and ("Before it stopped it built Hub_m1.25_N17, inserted Hub as gear7-1 and mated it (Hub on "
                             "Output Axis, Hub along Output and RangeSlv splined to Hub) and gave RangeSlv its bands."
                             in press.after)
    assert {m.name for m in desk.record.gearbox.mates} >= {"Hub on Output Axis", "Hub along Output",
                                                           "RangeSlv splined to Hub"}
    desk.sw.fail_on = {}
    again = desk.press(fixed())
    assert not again.up.in_place and again.result.ok, again.after


def test_a_configuration_that_fails_to_add_says_so_and_the_next_press_adds_it(fixed_desk):
    desk = fixed_desk
    desk.sw.fail_on = {"add_configuration": "SolidWorks would not add the configuration R."}
    press = desk.press(_fixed_with_mode())
    assert not press.ok and "SolidWorks would not add the configuration R." in press.after
    assert "It did not get to adding the configuration R" in press.after
    assert desk.record.gearbox.modes == ["H", "N", "L"]
    desk.sw.fail_on = {}
    again = desk.press(_fixed_with_mode())
    assert again.up.in_place.modes_added == ("R",) and again.result.ok, again.after
    assert desk.record.gearbox.modes == ["H", "N", "L", "R"]


def test_a_gear_inserted_that_reads_lightweight_in_a_mode_is_said_by_name(desk, measured):
    desk.sw.component_states["gear7-1"] = 1
    press = desk.press(fixed())
    assert press.result.not_resolved and not press.ok
    assert press.after.startswith("Update SolidWorks stopped. RangeBox.SLDASM: Hub (gear7-1) reads lightweight in H "
                                  "once inserted, not resolved. Before it stopped it built Hub_m1.25_N17, inserted "
                                  "Hub as gear7-1 and mated it"), press.after


# -- what the worker is handed besides the ops: each mate made as the record will hold it, and the links after ------

def test_the_done_when_edit_hands_the_worker_the_records_mate_refs_and_the_links_after_the_update(desk):
    up = update.classify(desk.record, desk.a(fixed()), exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    (hub,) = up.in_place.added
    assert [(r.name, r.kind, r.gears, r.shaft) for r in hub.refs] == [
        ("Hub on Output Axis", "axis", ("Hub",), "Output"), ("Hub along Output", "along", ("Hub",), "Output"),
        ("RangeSlv splined to Hub", "spline", ("Hub", "RangeSlv"), "")]
    assert ("Hub", "RangeSlv") in {(k.anchor, k.follower) for k in up.motion.locks}
    assert not any(m.name.startswith("Hub") for m in up.motion.mates)       # on record only once made


def test_a_new_coupling_hands_its_ref_with_its_on_set_and_its_link_with_its_modes(parallel):
    up = update.classify(parallel.record, parallel.a(_new_coupling()), exists=parallel.disk.exists,
                         read_sidecar=parallel.disk.read_sidecar)
    (new,) = up.in_place.new_mates
    assert (new.ref.name, new.ref.kind, new.ref.gears, new.ref.modes) == ("ModeSlv engages LoDog", "couple",
                                                                          ("ModeSlv", "LoDog"), ("2H",))
    (link,) = [m for m in up.motion.meshes if (m.a, m.b) == ("ModeSlv", "LoDog")]
    assert link.modes == ("2H",)


def test_a_gear_added_behind_its_anchor_round_trips_and_a_second_press_is_quiet(parallel):
    from gear_generator.workbook.model import Gear
    spec = transfer_case_parallel()
    spec = replace(spec, gears=spec.gears + (Gear("FExtra", "FrontDrv", "150", "spur", "", "25", "2", "", "10", "",
                                                  row=14),))
    press = parallel.press(spec)
    (added,) = press.up.in_place.added
    assert added.gear == "FExtra" and [r.kind for r in added.refs] == ["lock"]
    assert press.result.ok, (press.result.failures, press.result.skipped)
    assert [g for g, _ in press.result.inserted] == ["FExtra"] and "inserted FExtra as " in press.after
    box = parallel.record.gearbox
    assert "FExtra" in {c.gear for c in box.components}
    assert any(m.kind == "lock" and "FExtra" in m.gears for m in box.mates)
    again = parallel.press(spec)
    assert not again.up.in_place and again.result.ok


def test_a_new_coupling_with_its_gate_unmeasured_refuses_before_any_write(parallel, monkeypatch):
    monkeypatch.setattr(findings, "UPDATE_MAKES_A_NEW_COUPLING_ON_2026", None)
    press = parallel.press(_new_coupling())
    assert not press.before[1] and "UPDATE_MAKES_A_NEW_COUPLING_ON_" in press.before[0]
    assert "make a coupling or sliding mesh between gears already in the assembly" in press.before[0]
    assert press.refused.problems[0].subjects == ("UPDATE_MAKES_A_NEW_COUPLING_ON_2026",)
    assert parallel.writes(press.mark) == []


def test_a_press_that_stopped_after_adding_a_configuration_leaves_it_to_the_next_which_goes_on(fixed_desk):
    desk = fixed_desk
    desk.sw.fail_on = {"set_mate_suppressed_in": "SolidWorks would not set the flag."}
    press = desk.press(_fixed_with_mode())
    assert not press.ok and press.result.modes_added == ["R"] and "R" in desk.sw.configs
    assert desk.record.gearbox.modes == ["H", "N", "L"] and desk.record.gearbox.left == ["R"]
    desk.sw.fail_on = {}
    again = desk.press(_fixed_with_mode())
    assert again.up.in_place.modes_added == ("R",) and again.up.in_place.left == ("R",)
    assert again.result.ok, again.after
    assert desk.record.gearbox.modes == ["H", "N", "L", "R"] and desk.record.gearbox.left == []
    assert desk.sw.configs.count("R") == 1


# -- no SolidWorks version on record yet: each gate judged over every version the findings know -------------------

def _route_on(monkeypatch, y2024, y2026, desk=None):
    monkeypatch.setattr(findings, "COMPONENT_DELETE_ROUTE_ON_2024", y2024)
    monkeypatch.setattr(findings, "COMPONENT_DELETE_ROUTE_ON_2026", y2026)
    if desk is not None:
        desk.record.gearbox.solidworks = []            # a record from before schema 9: no SolidWorks version on it


def test_with_no_version_on_record_a_gate_set_on_every_known_version_foresees_nothing(parallel, monkeypatch):
    """The demonstration's first contact: the 12 : 1's master, no inventory yet, a gear taken out. The delete findings
    are set on 2024 and 2026, so nothing is foreseen stopping it, and the press takes the gear out."""
    _route_on(monkeypatch, "select4-editdelete", "select4-editdelete", parallel)
    assert parallel.record.gearbox.user_work is None
    spec = _without(transfer_case_parallel(), "FIdler")
    text, ok = parallel.footer(spec)
    assert ok and "would stop" not in text and "depends on the SolidWorks" not in text
    assert text.startswith("Update SolidWorks will take FIdler out with its 4 mates.")
    assert parallel.press(spec).result.ok


def test_with_no_version_on_record_a_gate_none_on_every_known_version_foresees_the_refusal(parallel, monkeypatch):
    _route_on(monkeypatch, None, None, parallel)
    spec = _without(transfer_case_parallel(), "FIdler")
    text, ok = parallel.footer(spec)
    assert not ok and text.startswith("Update SolidWorks would take FIdler out with its 4 mates.")
    assert text.endswith(
        "The next press would stop before changing anything: Update SolidWorks would take a gear out of the assembly, "
        "which Gear Generator has not yet been shown to do on the SolidWorks it runs on "
        "(findings.COMPONENT_DELETE_ROUTE_ON_<year>), so the press changes nothing; Build again… makes the new "
        "revision instead.")


def test_with_no_version_on_record_a_gate_set_on_some_versions_says_it_depends_neither_red_nor_build_again(
        parallel, monkeypatch):
    _route_on(monkeypatch, None, "select4-editdelete", parallel)
    spec = _without(transfer_case_parallel(), "FIdler")
    text, ok = parallel.footer(spec)
    assert ok and "would stop" not in text and "Build again" not in text.split("4 mates.", 1)[1]
    assert text.endswith(
        "Whether Update SolidWorks can take a gear out of the assembly depends on the SolidWorks in use: Gear "
        "Generator has been shown to do so on SolidWorks 2026, not yet on SolidWorks 2024 "
        "(findings.COMPONENT_DELETE_ROUTE_ON_2024), and the press reads which it runs on before it changes anything.")
    assert parallel.press(spec).result.ok                                # the fake is 2026: it goes ahead


def test_the_build_records_the_solidworks_it_ran_on_and_a_gate_is_judged_on_it(parallel, monkeypatch):
    box = parallel.record.gearbox
    assert box.solidworks == list(parallel.sw.revision) and box.user_work is None
    _route_on(monkeypatch, None, "select4-editdelete")
    text, ok = parallel.footer(_without(transfer_case_parallel(), "FIdler"))
    assert ok and "depends on the SolidWorks" not in text and "would stop" not in text


def test_with_a_version_on_record_a_gate_is_judged_on_that_version_alone(parallel, monkeypatch):
    assert parallel.press(transfer_case_parallel()).result.ok          # a quiet press reads 2026 onto the record
    parallel.record.gearbox.solidworks = []                            # the inventory's alone
    _route_on(monkeypatch, None, "select4-editdelete")
    text, ok = parallel.footer(_without(transfer_case_parallel(), "FIdler"))
    assert ok and "depends on the SolidWorks" not in text and "would stop" not in text
    _route_on(monkeypatch, "select4-editdelete", None)
    text, ok = parallel.footer(_without(transfer_case_parallel(), "FIdler"))
    assert not ok and "(findings.COMPONENT_DELETE_ROUTE_ON_2026)" in text


# -- the review's must-fix 2: the app's leftovers kept until a press uses them or takes them away -------------------

def test_a_global_and_a_part_left_by_a_stopped_press_stay_the_apps_through_an_abandon_and_a_re_add(desk, measured):
    """RangeBox -> RangeBox_Fixed stops at the insert (Hub's part built, Hub Face Z added); the workbook goes back to
    RangeBox (a press that runs to its end, which does not use them); then Hub comes back. The leftovers are said as
    the app's while unused, and the re-add uses them: the part inserted, the global set though it was moved."""
    desk.sw.fail_on = {"add_component": "SolidWorks would not insert Hub_m1.25_N17.SLDPRT."}
    desk.press(fixed())
    desk.sw.fail_on = {}
    hub_part = next(p.path for p in desk.record.parts if "Hub" in p.gears)
    back = desk.press(range_box())
    assert back.result.ok, back.after
    said = ("An Update SolidWorks that stopped part way left the global Hub Face Z and the part Hub_m1.25_N17.SLDPRT, "
            "which the workbook no longer uses: Update SolidWorks leaves them as they are and keeps them on record as "
            "its own, so a later press can use them again; delete them in SolidWorks if you no longer want them.")
    assert said in back.before[0] and said in back.after
    assert desk.record.gearbox.left == ["Hub Face Z"]
    assert any(store.same_path(p.path, hub_part) and p.gears == ["Hub"] for p in desk.record.parts)
    desk.sw.open_document(desk.record.gearbox.assembly)
    desk.sw.set_global_variable("Hub Face Z", "12")
    again = desk.press(fixed())
    assert again.before[1] and "left" not in again.before[0].split(". It was built")[0]
    assert again.up.in_place.added[0].build is None and "Hub Face Z" in again.up.in_place.left
    assert again.result.ok, again.after
    assert "Gear Generator did not add" not in again.after and desk.record.gearbox.left == []


def test_a_configuration_left_by_a_stopped_press_is_never_called_the_users_and_a_re_add_uses_it(fixed_desk):
    desk = fixed_desk
    desk.sw.fail_on = {"set_mate_suppressed_in": "SolidWorks would not set the flag."}
    desk.press(_fixed_with_mode())
    desk.sw.fail_on = {}
    assert desk.record.gearbox.left_configurations == ["R"]
    back = desk.press(fixed())
    assert back.result.ok, back.after
    assert "the app did not make" not in back.after
    said = ("An Update SolidWorks that stopped part way left the configuration R, which the workbook no longer uses: "
            "Update SolidWorks leaves it as it is and keeps it on record as its own, so a later press can use it "
            "again; delete it in SolidWorks if you no longer want it.")
    assert said in back.before[0] and said in back.after
    assert desk.record.gearbox.left_configurations == ["R"]                # kept: not used, not taken away
    again = desk.press(_fixed_with_mode())
    assert again.up.in_place.left == ("R",) and again.result.ok, again.after
    assert desk.record.gearbox.modes == ["H", "N", "L", "R"] and desk.record.gearbox.left == []


# -- ruling C6: a removed gear's part entry leaves the record when no gear uses it; the file stays on disk ------------

def test_a_gear_taken_out_takes_its_part_entry_with_it_when_no_gear_uses_it_and_says_the_file_stays(parallel):
    part = next(p.path for p in parallel.record.parts if "FIdler" in p.gears)
    press = parallel.press(_without(transfer_case_parallel(), "FIdler"))
    assert press.result.ok, press.after
    assert not any(store.same_path(p.path, part) for p in parallel.record.parts)
    assert ", leaving its part Gear_m2_N20.SLDPRT on disk" in press.after
    assert parallel.disk.exists(part)


def test_a_gear_taken_out_that_shares_its_part_leaves_the_entry_to_the_gear_that_keeps_it(measured):
    d = Desk()
    d.build(range_box())
    part = next(p for p in d.record.parts if "LowDog" in p.gears)
    assert sorted(part.gears) == ["HighDog", "LowDog"]
    press = d.press(_without(range_box(), "LowDog"))
    assert press.result.ok, press.after
    kept = next(p for p in d.record.parts if store.same_path(p.path, part.path))
    assert kept.gears == ["HighDog"] and "leaving" not in press.after


def test_a_refusal_carried_with_nothing_read_never_hides_the_users_components_from_a_later_footer(parallel):
    """The review's should-fix 3: after the mode-showing refusal on a record with no inventory, a removal with the
    user's components in SolidWorks is foreseen as with no inventory (nothing claimed), and the press reads them."""
    from gear_generator.workbook import update as wb_update
    spec = transfer_case_parallel()
    parallel.press(replace(spec, modes=spec.modes[1:]))
    assert parallel.record.gearbox.user_work.unread
    up = update.classify(parallel.record, parallel.a(_without(spec, "FIdler")), exists=parallel.disk.exists,
                         read_sidecar=parallel.disk.read_sidecar)
    assert wb_update.user_work_ahead(up, parallel.record, parallel.digest(_without(spec, "FIdler"))) is None
    assert wb_update.recorded_user_work(parallel.record.gearbox.user_work).components == []
    parallel.sw.user_component(parallel.record.gearbox.assembly, "Housing-1", "C:\\Parts\\Housing.SLDPRT", fixed=True)
    press = parallel.press(_without(spec, "FIdler"))
    assert [p.kind for p in press.refused.problems] == [swbuild.PROBLEM_REFERENCES]


# -- the runs review's must-fix: the inventory after a press that added a mode holds the user's flags there --------

def _sun_backlash(spec, value="0.4"):
    return replace(spec, gears=tuple(replace(g, backlash=value) if g.id == "Sun" else g for g in spec.gears))


def test_after_a_mode_is_added_the_record_holds_the_users_flags_there_and_no_footer_foresees_a_false_refusal(
        fixed_desk_with_work):
    desk = fixed_desk_with_work
    assert desk.press(_fixed_with_mode()).result.ok
    entry = desk.record.gearbox.user_work
    assert entry.modes == ["H", "N", "L", "R"]
    lock = next(m for m in entry.mates if m.name == "Lock3")
    assert "R" in lock.on                                   # read there by the worker (took_active_state), recorded
    with_r = _fixed_with_mode()
    removal = replace(with_r, modes=tuple(m for m in with_r.modes if m.name != "N"))
    for edit in (removal, _sun_backlash(with_r)):
        text, ok = desk.footer(edit)
        assert ok and "would stop" not in text and "suppressed in R" not in text, text
    press = desk.press(removal)
    assert press.result.ok, press.after


def test_a_users_mate_suppressed_in_the_added_mode_afterwards_is_still_foreseen(fixed_desk_with_work):
    desk = fixed_desk_with_work
    assert desk.press(_fixed_with_mode()).result.ok
    asm = _key(desk.record.gearbox.assembly)
    lock = next(m for m in desk.sw.memory_mates[asm] if m.name == "Lock3")
    lock.flags["R"] = True                                  # the user suppresses their lock in R
    refused = desk.press(_sun_backlash(_fixed_with_mode()))
    assert refused.refused is not None                       # the press reads it (W9a's lock rule) and refuses
    entry = desk.record.gearbox.user_work
    assert "R" in entry.modes and "R" not in next(m for m in entry.mates if m.name == "Lock3").on
    text, ok = desk.footer(_sun_backlash(_fixed_with_mode(), "0.5"))       # the workbook changed since
    assert not ok and "Your lock Lock3 is on in H, N and L and suppressed in R" in text, text


def test_a_record_written_before_the_fix_reads_a_mode_its_inventory_never_read_as_a_copy(fixed_desk_with_work):
    """A record a press wrote before this fix: its inventory has no ``modes`` and its mates' on-lists never name the
    mode that press added. The footer takes that mode as a copy of a mode it did read, and foresees nothing false."""
    desk = fixed_desk_with_work
    assert desk.press(_fixed_with_mode()).result.ok
    entry = desk.record.gearbox.user_work
    entry.modes = []
    for mate in entry.mates:
        mate.on = [c for c in mate.on if c != "R"]
    with_r = _fixed_with_mode()
    removal = replace(with_r, modes=tuple(m for m in with_r.modes if m.name != "N"))
    for edit in (removal, _sun_backlash(with_r)):
        text, ok = desk.footer(edit)
        assert ok and "would stop" not in text and "suppressed in R" not in text, text


def test_run_5s_add_read_onto_its_inventory_puts_h2_in_every_users_mate_it_read_on():
    """Replay of the real add (run 5's ``modes``, ``probe/results/w9c-demo-20261117-094223.json``): the JSON keeps the
    worker's ``took_active_state`` and ``modes_added``, not the record, so its facts are put through the finish's own
    step onto an inventory of the same eight mates as read before H2 existed (on in H, N and L)."""
    import json
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "probe", "results", "w9c-demo-20261117-094223.json")
    if not os.path.exists(path):
        pytest.skip("run 5's results are not in this checkout")
    with open(path, encoding="utf-8") as handle:
        add = json.load(handle)["sections"]["modes"]["add"]
    mates = [name for mode, name, state in add["took_active_state"] if not name.startswith(("Sprocket", "Housing"))]
    entry = store.UserWorkEntry(read_at=STAMP, mates=[store.UserMateEntry(name, "lock", 16, [], ["H", "N", "L"])
                                                      for name in mates], modes=["H", "N", "L"])
    result = swbuild.GearboxUpdate(modes_added=list(add["modes_added"]),
                                   took_active_state=[tuple(t) for t in add["took_active_state"]])
    update.follow_modes_added(entry, result, ["H", "N", "L", "H2"])
    assert add["modes_added"] == ["H2"] and len(mates) == 8
    assert entry.modes == ["H", "N", "L", "H2"] and all(m.on == ["H", "N", "L", "H2"] for m in entry.mates)


# -- the runs review's should-fix: a stop in a part left in error never offers to save ------------------------------

def test_a_stop_in_a_part_left_in_error_says_close_it_without_saving_never_save_it():
    d = Desk()
    d.build(range_box())
    d.sw.rebuild_ok = False
    press = d.press(_sun_backlash(range_box()))
    assert press.after == (
        "Update SolidWorks stopped. Gear_m1.25_N29.SLDPRT: SolidWorks reported an error rebuilding Gear_m1.25_N29. It "
        "had already changed Gear_m1.25_N29, not saved, and Gear_m1.25_N29 is left in error: close it and RangeBox "
        "in SolidWorks without saving, answering No when SolidWorks asks to save them (the files on disk are as "
        "before this Update), then press Update SolidWorks again.")
    assert "save it in SolidWorks to keep" not in press.after and "put right" not in press.after


def test_a_stop_in_one_part_in_error_among_several_changed_closes_them_all_without_saving():
    """Run 5's remake: Sun, the planets and the ring changed, the ring left in error. Saving the good ones beside it
    closed would leave gears at their new teeth against the old ring, so all are closed unsaved."""
    from gear_generator.ui_text import gearbox_update_status
    result = swbuild.GearboxUpdate(
        parts=[swbuild.UpdateResult("Gear_m1.25_N29.SLDPRT", ["No. of Teeth"], rebuilt=True),
               swbuild.UpdateResult("Gear_m1.25_N13.SLDPRT", ["No. of Teeth"], rebuilt=True),
               swbuild.UpdateResult("Ring_m1.25_N55.SLDPRT", ["No. of Teeth"], rebuilt=False)],
        failures=[("Ring_m1.25_N55.SLDPRT", "SolidWorks reported an error rebuilding Ring_m1.25_N55.")],
        changed=["C:\\Out\\Gear_m1.25_N29.SLDPRT", "C:\\Out\\Gear_m1.25_N13.SLDPRT",
                 "C:\\Out\\Ring_m1.25_N55.SLDPRT"])
    up = update.UpdatePlan()
    text, ok = gearbox_update_status(up, result, [])
    assert not ok and text.endswith(
        "It had already changed Gear_m1.25_N29, Gear_m1.25_N13 and Ring_m1.25_N55, not saved, and Ring_m1.25_N55 is "
        "left in error: close them all in SolidWorks without saving (the files on disk are as before this Update), "
        "then press Update SolidWorks again."), text


def test_a_stop_with_nothing_changed_in_error_still_offers_to_save(fixed_desk):
    desk = fixed_desk
    desk.sw.fail_on = {"add_configuration": "SolidWorks would not add the configuration R."}
    press = desk.press(_fixed_with_mode())
    assert "or save it in SolidWorks to keep what it did." in press.after and "left in error" not in press.after


def test_the_footer_after_a_stop_in_a_part_left_in_error_says_close_without_saving_until_the_next_press_goes_through():
    """The mark rides on the record (``LinkRecord.unsaved_in_error``): the footer says what the stop said, never to
    save, until the documents are found closed; closed without saving, the next press goes through and the mark goes."""
    d = Desk()
    d.build(range_box())
    d.sw.rebuild_ok = False
    stopped = d.press(_sun_backlash(range_box()))
    assert "left in error" in stopped.after
    part = next(p.path for p in d.record.parts if "Sun" in p.gears)
    assert [store.same_path(p, part) for p in d.record.unsaved_in_error] == [True]
    text, _ = d.footer(_sun_backlash(range_box()))
    assert text.endswith(
        "Gear_m1.25_N29 has changes from Update SolidWorks that are not saved, and Gear_m1.25_N29 was left in error "
        "when it stopped: close it and RangeBox in SolidWorks without saving, answering No when SolidWorks asks to "
        "save them (the files on disk are as before that Update), then press Update SolidWorks again."), text
    assert "save them in SolidWorks to keep" not in text and "save it in SolidWorks to keep" not in text
    back = store.link_record_from_json(store.link_record_to_json(d.record))
    assert back.unsaved_in_error == d.record.unsaved_in_error                  # written and read back
    d.sw.close_all()                                          # the user closes it without saving
    d.sw.rebuild_ok = True                                    # and the fault is gone (A's routed change, say)
    again = d.press(_sun_backlash(range_box()))
    assert again.result.ok, again.after
    assert d.record.unsaved_in_error == []
    assert "left in error" not in d.footer(_sun_backlash(range_box()))[0]


def test_a_record_without_the_mark_reads_its_unsaved_line_as_before():
    d = Desk()
    d.build(range_box())
    d.press(_sun_backlash(range_box()))
    assert d.record.unsaved and d.record.unsaved_in_error == []
    text, _ = d.footer(_sun_backlash(range_box()))
    assert "in SolidWorks to keep" in text and "left in error" not in text


# -- the fixes review: M3 (a press that sets nothing proves nothing), S6 (modes read), S7 (one name rule) ------------

def test_pressing_again_without_closing_keeps_the_mark_and_says_close_without_saving_not_already_matches():
    """The part is put in error as SolidWorks shows one (P0: a feature of the app's with an error code; the fake's
    rebuild_ok alone, which this test used before the review of the M3 fix, is an error no feature read can see, and
    a part read clean now sheds its mark). Pressed again without closing, the press stops on it before any write."""
    d = Desk()
    d.build(range_box())
    part = next(p.path for p in d.record.parts if "Sun" in p.gears)
    d.sw.breaks_on_set[_key(part)] = [("Teeth", 1)]
    d.press(_sun_backlash(range_box()))
    mark = len(d.sw.calls)
    again = d.press(_sun_backlash(range_box()))              # not closed: the part holds the new value, in error
    assert d.writes(mark) == [] and [w for w, _ in again.result.failures] == ["Gear_m1.25_N29.SLDPRT"]
    assert [store.same_path(p, part) for p in d.record.unsaved_in_error] == [True]
    assert not again.ok and again.after == (
        "Gear_m1.25_N29 is still open in SolidWorks as an earlier Update SolidWorks left it, in error and holding the "
        "new values, so this press set nothing in it: close it and RangeBox in SolidWorks without saving, answering "
        "No when SolidWorks asks to save them (the files on disk are as before that Update), then press Update "
        "SolidWorks again.")
    text, _ = d.footer(_sun_backlash(range_box()))
    assert "was left in error when it stopped: close it and RangeBox in SolidWorks without saving, answering No" in text
    assert "in SolidWorks to keep" not in text
    d.sw.close_all()
    d.sw.feature_codes.pop((_key(part), "Teeth"))            # reopened from its file, as it was before: clean
    clean = d.press(_sun_backlash(range_box()))              # rebuilt that very document clean: the mark goes
    assert clean.result.ok and clean.ok and d.record.unsaved_in_error == []


def test_the_record_mark_and_the_stop_sentence_name_a_document_the_same_way_with_or_without_its_extension():
    from gear_generator.ui_text import _parts_left_in_error
    for title in ("Gear_m1.25_N29.SLDPRT", "Gear_m1.25_N29", "gear_m1.25_n29.sldprt"):
        result = swbuild.GearboxUpdate(
            parts=[swbuild.UpdateResult(title, ["Backlash"], rebuilt=False),
                   swbuild.UpdateResult("Gear_m1.25_N2", ["Backlash"], rebuilt=False)],
            failures=[(title, "SolidWorks reported an error rebuilding Gear_m1.25_N29.")])
        plan = update.UpdatePlan(parts=(
            update.PartUpdate("C:\\Out\\Gear_m1.25_N29.SLDPRT", ("Sun",), None, None, ()),
            update.PartUpdate("C:\\Out\\Gear_m1.25_N2.SLDPRT", ("X",), None, None, ())))
        assert update._documents_left_in_error(plan, result) == ["C:\\Out\\Gear_m1.25_N29.SLDPRT"], title
        assert [s.casefold() for s in _parts_left_in_error(result)] == ["gear_m1.25_n29"], title
    assert not update.names_document("Gear_m1.25_N29 Backlash", "Gear_m1.25_N2.SLDPRT")
    assert update.names_document("Gear_m1.25_N29 Backlash", "C:\\Out\\Gear_m1.25_N29.SLDPRT")


def test_a_press_that_stops_before_deleting_a_mode_records_only_the_modes_its_read_covered(fixed_desk_with_work):
    desk = fixed_desk_with_work
    desk.sw.fail_on = {"delete_configuration": "SolidWorks would not delete the configuration N."}
    stopped = desk.press(_fixed_without_mode())
    assert not stopped.ok and "N" in desk.record.gearbox.modes
    entry = desk.record.gearbox.user_work
    assert entry.modes == ["H", "L"]                       # the worker read the modes left after the Update only
    desk.sw.fail_on = {}
    text, ok = desk.footer(_sun_backlash(fixed()))          # N back in the workbook: judged as a copy, not as read
    assert ok and "suppressed in N" not in text, text


# -- the fixes review's second reading: N1 (a part put right beside the user's own feature in error sheds its mark) --

def test_a_part_left_in_error_then_put_right_beside_the_users_own_feature_in_error_sheds_its_mark():
    """Closed without saving as told, the part is changed again; its rebuild reads false from the user's Keyway alone
    (P0), which is no failure. The mark goes: the press says to save it, never also to close it without saving, and
    the footer no longer says it was left in error."""
    d = Desk()
    d.build(range_box())
    d.sw.rebuild_ok = False
    d.press(_sun_backlash(range_box()))
    part = next(p.path for p in d.record.parts if "Sun" in p.gears)
    assert [store.same_path(p, part) for p in d.record.unsaved_in_error] == [True]
    d.sw.close_all()
    d.sw.rebuild_ok = True
    d.sw.user_feature(part, "Keyway", code=41)
    again = d.press(_sun_backlash(range_box()))
    sun = next(p for p in again.result.parts if p.document == "Gear_m1.25_N29.SLDPRT")
    assert again.result.failures == [] and sun.changed == ["Backlash"] and not sun.rebuilt
    assert d.record.unsaved_in_error == [] and again.finished.still_in_error == []
    assert "Save Gear_m1.25_N29 and RangeBox in SolidWorks to keep them." in again.after, again.after
    assert "without saving" not in again.after and "still open in SolidWorks" not in again.after, again.after
    text, _ = d.footer(_sun_backlash(range_box()))
    assert "was left in error when it stopped" not in text and "save them in SolidWorks to keep them" in text, text


def test_a_sleeve_left_in_error_then_given_only_its_bands_clean_sheds_its_mark(measured):
    """The re-check's note under N1: the sleeve holds its new face width from the stopped press, so the next press
    sets no value in it and changes it only by its bands, which read clean. The status says to save it; the footer
    must not still say it was left in error and to close it without saving."""
    d = Desk()
    d.build(range_box())
    d.sw.rebuild_ok = False
    stopped = d.press(fixed())
    sleeve = _part(d.record, "RangeSlv")
    assert "Sleeve_m1.25_N17 is left in error" in stopped.after
    assert [store.same_path(p, sleeve) for p in d.record.unsaved_in_error] == [True]
    d.sw.rebuild_ok = True
    again = d.press(fixed())                                  # not closed: only the bands are left to give
    assert again.result.ok and again.result.bands_added == ["RangeSlv"]
    assert not next(p for p in again.result.parts if p.document == "Sleeve_m1.25_N17.SLDPRT").changed
    assert "Save Sleeve_m1.25_N17 and RangeBox in SolidWorks to keep them." in again.after, again.after
    assert d.record.unsaved_in_error == []
    text, _ = d.footer(fixed())
    assert "left in error" not in text and "save them in SolidWorks to keep them" in text, text


# -- the third re-check: a sleeve's band step that fails on the app's own feature is left in error -------------------

def _relief_comes_out_in_error(desk, sleeve):
    """The fake makes the sleeve's relief, then reads it in error (an app feature: the band step raises)."""
    made = desk.sw.loft_cut

    def loft_cut(handle, name, profiles):
        out = made(handle, name, profiles)
        desk.sw.feature_codes[(_key(sleeve), name)] = 41
        return out

    desk.sw.loft_cut = loft_cut


def _says_close_without_saving(press, footer):
    assert "Sleeve_m1.25_N17 is left in error: close it and RangeBox in SolidWorks without saving, answering No when " \
        "SolidWorks asks to save them" in press.after, press.after
    assert "save it in SolidWorks to keep" not in press.after, press.after
    assert "Sleeve_m1.25_N17 was left in error when it stopped: close it and RangeBox in SolidWorks without saving, " \
        "answering No when SolidWorks asks to save them" in footer, footer
    assert "save it in SolidWorks to keep" not in footer, footer


def test_a_relief_in_error_the_first_time_bands_are_given_leaves_the_sleeve_in_error_never_offered_for_saving(
        measured):
    """Its values (the face width) rebuilt clean, then its band step fails on the relief: the stop and the footer
    both say to close it without saving, and the mark is written."""
    d = Desk()
    d.build(range_box())
    sleeve = _part(d.record, "RangeSlv")
    _relief_comes_out_in_error(d, sleeve)
    press = d.press(fixed())
    assert press.result.failures == [("Sleeve_m1.25_N17.SLDPRT", "SolidWorks reported Relief in error in "
                                                                 "Sleeve_m1.25_N17.")]
    assert [store.same_path(p, sleeve) for p in d.record.unsaved_in_error] == [True]
    _says_close_without_saving(press, d.footer(fixed())[0])


def test_a_sleeve_marked_earlier_whose_bands_alone_fail_on_the_relief_keeps_its_mark_and_no_save_offer(measured):
    """Stopped in the sleeve's values, pressed again without closing: no value is set in it, its band step fails on
    the relief. The status no longer offers to save it while the footer says to close it without saving."""
    d = Desk()
    d.build(range_box())
    sleeve = _part(d.record, "RangeSlv")
    d.sw.rebuild_ok = False
    d.press(fixed())
    d.sw.rebuild_ok = True
    _relief_comes_out_in_error(d, sleeve)
    press = d.press(fixed())
    assert not next(p for p in press.result.parts if p.document == "Sleeve_m1.25_N17.SLDPRT").changed
    assert [what for what, _ in press.result.failures] == ["Sleeve_m1.25_N17.SLDPRT"]
    assert [store.same_path(p, sleeve) for p in d.record.unsaved_in_error] == [True]
    _says_close_without_saving(press, d.footer(fixed())[0])


# -- the eighth run on SolidWorks 2026, remake's M3: pressed again without closing, the ring still open in error ------

def _m3_stage():
    """remake's M3 stage on RangeBox: Sun 30, Planet 12, Ring 55 -> 54 (a landing), its gear mates remade."""
    return _with(_with(_with(range_box(), "Sun", teeth="30"), "Planet", teeth="12"), "Ring", teeth="54")


def test_pressed_again_with_the_ring_still_open_in_error_the_press_writes_nothing_and_says_close_without_saving(
        measured):
    """The fake as SolidWorks: the ring set straight lands on the far branch (Tooth Space 72), and an assembly's
    rebuild reads false while a part of it has a feature in error (ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR). The
    second press, without closing, used to go on into the assembly, remake a gear mate and stop on the assembly's
    rebuild, offering to save RangeBox. Now it stops before any write, on the ring, and says what step 2 says."""
    d = Desk()
    d.build(range_box())
    ring = _part(d.record, "Ring")
    steps, swbuild.LANDING_STEPS = swbuild.LANDING_STEPS, ()
    try:
        first = d.press(_m3_stage())                         # set straight: stops in the ring
    finally:
        swbuild.LANDING_STEPS = steps
    assert [w for w, _ in first.result.failures] == ["Ring_m1.25_N55.SLDPRT"]
    assert "Ring_m1.25_N55 is left in error" in first.after
    mark = len(d.sw.calls)
    again = d.press(_m3_stage())                             # not closed: the ring holds 54, in error
    assert d.writes(mark) == [], d.writes(mark)
    assert [w for w, _ in again.result.failures] == ["Ring_m1.25_N55.SLDPRT"]
    assert not again.result.changed and not again.result.remade_in_modes
    assert [store.same_path(p, ring) for p in d.record.unsaved_in_error] == [True]
    assert not again.ok and again.after == (
        "Ring_m1.25_N55 is still open in SolidWorks as an earlier Update SolidWorks left it, in error and holding the "
        "new values, so this press set nothing in it: close it and RangeBox in SolidWorks without saving, answering "
        "No when SolidWorks asks to save them (the files on disk are as before that Update), then press Update "
        "SolidWorks again."), again.after
    text, _ = d.footer(_m3_stage())
    assert text.endswith(
        "Gear_m1.25_N13, Gear_m1.25_N29 and Ring_m1.25_N55 have changes from Update SolidWorks that are not saved, and "
        "Ring_m1.25_N55 was left in error when it stopped: close them all and RangeBox in SolidWorks without saving, "
        "answering No when SolidWorks asks to save them (the files on disk are as before that Update), then press "
        "Update SolidWorks again."), text
    assert "to keep" not in text and "already matches" not in text, text
    d.sw.close_all()                                         # closed without saving, as told: the third press goes
    third = d.press(_m3_stage())
    # The ring is loaded from its file at 55, so it does not hold the workbook's values and is never stopped on: it
    # goes by way of 53 and rebuilds clean, and its mark goes. (The fake then fails this stage's put of a planet,
    # "did not take its frame", which SolidWorks did not: a limit of the fake's planetary put, not of this rule.)
    ring_done = next(p for p in third.result.parts if p.document == "Ring_m1.25_N55.SLDPRT")
    assert ring_done.by_way_of == ("No. of Teeth", "53") and ring_done.rebuilt
    assert not [w for w, _ in third.result.failures if update.names_document(w, ring)], third.result.failures
    assert d.record.unsaved_in_error == []


def test_only_a_part_marked_left_in_error_holding_its_values_with_the_apps_own_feature_in_error_stops_a_press():
    """swbuild._held_in_error, the rule alone: the mark, the values held (this press would set nothing there) and a
    feature the app made read in error, all three. The user's own features in error, and a code SolidWorks would not
    give, never count (K3: theirs alone never stop an Update)."""
    from gear_generator import swcom
    doc = swbuild.DocumentValues("C:\\Out\\Ring_m1.25_N55.SLDPRT", made=("Tooth Space", "Teeth"), left_in_error=True)
    states = [swcom.FeatureState("Tooth Space", "Cut", 72, False), swcom.FeatureState("Teeth", "?", swcom.UNREAD, False),
              swcom.FeatureState("Keyway", "ICE", 41, False)]
    assert swbuild._app_features_in_error(doc, states) == ["Tooth Space"]                   # noqa: SLF001
    for document, held, names, stops in ((doc, "degrees", ["Tooth Space"], True),
                                         (replace(doc, left_in_error=False), "degrees", ["Tooth Space"], False),
                                         (doc, "", ["Tooth Space"], False),
                                         (doc, "degrees", [], False)):
        result = swbuild.GearboxUpdate()
        assert swbuild._held_in_error([document], [held], {document.path: names}, result,       # noqa: SLF001
                                      ["the assembly"]) is stops
        assert [w for w, _ in result.failures] == (["Ring_m1.25_N55.SLDPRT"] if stops else [])
        assert result.skipped == ("the assembly, because Ring_m1.25_N55.SLDPRT is in error" if stops else "")


# -- the review of the M3 fix: (ii) a marked part read clean, (iii) a part still in error beside another failure -----

def _m3_stopped():
    """remake's M3 step 1 on the fake: the stage set straight stops in the ring, which the record marks. The desk and
    the ring's path."""
    d = Desk()
    d.build(range_box())
    steps, swbuild.LANDING_STEPS = swbuild.LANDING_STEPS, ()
    try:
        first = d.press(_m3_stage())
    finally:
        swbuild.LANDING_STEPS = steps
    ring = _part(d.record, "Ring")
    assert [store.same_path(p, ring) for p in d.record.unsaved_in_error] == [True], first.after
    return d, ring


def _ring_codes(d, ring, tooth_space):
    """The ring's landing in the fake set aside, its Tooth Space then reading ``tooth_space`` (0: clean, as a repair
    in SolidWorks leaves it)."""
    d.sw.wrong_branch.discard(_key(ring))
    d.sw.feature_codes.pop((_key(ring), "Teeth"), None)
    d.sw.feature_codes[(_key(ring), "Tooth Space")] = tooth_space
    if not tooth_space:
        del d.sw.feature_codes[(_key(ring), "Tooth Space")]


def test_a_marked_part_repaired_in_solidworks_sheds_its_mark_and_is_never_called_still_in_error(measured):
    """(ii): the ring, left in error, is repaired by hand and reads clean at 54. The press is not stopped on it, and
    neither the status nor the footer may call it still in error or tell the user to throw it away."""
    d, ring = _m3_stopped()
    _ring_codes(d, ring, 0)
    again = d.press(_m3_stage())
    assert "still open in SolidWorks" not in again.after, again.after
    assert d.record.unsaved_in_error == [] and again.finished.still_in_error == []
    text, _ = d.footer(_m3_stage())
    assert "left in error" not in text, text
    assert [store.same_path(p, ring) for p in again.result.read_clean] == [True]


def test_a_marked_part_whose_read_has_a_code_unread_keeps_its_mark_and_the_stop_never_offers_to_save(measured):
    """(ii)'s other side, and (iii): a code SolidWorks would not give is no repair, so the mark stays and the part is
    still said in error; the press is not stopped on it and fails further on, and its stop then tells the user to
    close everything without saving, never to save what it changed beside a part to be closed unsaved."""
    d, ring = _m3_stopped()
    _ring_codes(d, ring, swbuild.UNREAD)
    again = d.press(_m3_stage())
    assert "It had already changed RangeBox, not saved, and Ring_m1.25_N55 is left in error: close them all in " \
        "SolidWorks without saving, answering No when SolidWorks asks to save them" in again.after, again.after
    assert "to keep" not in again.after and "Ring_m1.25_N55 is still open in SolidWorks" in again.after, again.after
    assert again.result.failures and again.result.changed
    assert [store.same_path(p, ring) for p in d.record.unsaved_in_error] == [True]
    assert again.result.read_clean == []


def test_a_mark_goes_on_a_read_only_when_it_was_made_whole():
    """swbuild._read_clean: marked, read, nothing of the app's in error or unread. Not read (no ``made``: an empty
    read), unread, in error, or not marked: the mark stays."""
    from gear_generator import swcom
    doc = swbuild.DocumentValues("C:\\\\Out\\\\Ring_m1.25_N55.SLDPRT", made=("Tooth Space", "Teeth"), left_in_error=True)
    clean = [swcom.FeatureState("Tooth Space", "Cut", 0, True), swcom.FeatureState("Keyway", "ICE", 41, False)]
    for document, states, noted in ((doc, clean, True),
                                    (doc, [], False),
                                    (doc, [swcom.FeatureState("Tooth Space", "Cut", swcom.UNREAD, False)], False),
                                    (doc, [swcom.FeatureState("Tooth Space", "Cut", 72, False)], False),
                                    (replace(doc, left_in_error=False), clean, False)):
        result = swbuild.GearboxUpdate()
        swbuild._read_clean(document, states, result)                                           # noqa: SLF001
        assert result.read_clean == ([document.path] if noted else []), (states, document.left_in_error)


def test_a_marked_part_read_clean_whose_rebuild_then_raises_keeps_its_mark_and_no_save_offer(measured):
    """The re-check of (ii): the ring left in error is repaired in SolidWorks but not closed, so it reads clean ((ii)
    would drop its mark), and the workbook then asks another count (Sun 28, Planet 14, Ring 56). The ring is set to
    56 and its rebuild raises; the raise path returns a fresh result with nothing changed, so nothing marks it again.
    Its mark must stay, and the stop must not offer to save the parts beside it. (Closed instead, the ring is found
    closed and its mark goes with its unsaved mark, as before (ii): the file holds what it did before that Update.)"""
    d, ring = _m3_stopped()
    _ring_codes(d, ring, 0)
    real = d.sw.rebuild

    def rebuild(kind=None):
        if d.sw.current and _key(d.sw.current) == _key(ring):
            raise RuntimeError("SolidWorks stopped responding.")
        return real(kind)

    d.sw.rebuild = rebuild
    stage = _with(_with(_with(range_box(), "Sun", teeth="28"), "Planet", teeth="14"), "Ring", teeth="56")
    again = d.press(stage)
    assert [store.same_path(p, ring) for p in again.result.read_clean] == [True]
    assert [w for w, _ in again.result.failures] == ["Ring_m1.25_N55.SLDPRT"], again.result.failures
    assert [store.same_path(p, ring) for p in d.record.unsaved_in_error] == [True]
    assert "to keep" not in again.after, again.after
    assert "Ring_m1.25_N55 is left in error: close them all and RangeBox in SolidWorks without saving, answering No " \
        "when SolidWorks asks to save them" in again.after, again.after


def test_the_close_without_saving_advice_names_the_assembly_that_holds_the_part_and_says_to_answer_no():
    """W9C-RUNS-REVIEW.md's addendum on the final runs, should-fix A: SolidWorks marks the open assembly modified when
    a part of it is changed and rebuilt (run 11 on 34.0.0), and a part closed while its assembly stays open stays
    loaded with its changes. Only a document the record's assembly holds brings the assembly into the advice."""
    d = Desk()
    d.build(range_box())
    ring, asm = _part(d.record, "Ring"), d.record.gearbox.assembly
    assert update.assembly_holding(d.record, [ring]) == asm
    assert update.assembly_holding(d.record, ["Ring_m1.25_N55"]) == asm                 # by stem, as the stop names it
    assert update.assembly_holding(d.record, [d.record.gearbox.layout]) == asm
    assert update.assembly_holding(d.record, ["C:\\\\Elsewhere\\\\Other.SLDPRT"]) == ""
    assert update.assembly_holding(update.UpdatePlan(), [ring]) == ""                    # no assembly on the plan
    assert ui_text.still_in_error_sentence([ring], asm) == (
        "Ring_m1.25_N55 is still open in SolidWorks as an earlier Update SolidWorks left it, in error and holding the "
        "new values, so this press set nothing in it: close it and RangeBox in SolidWorks without saving, answering No "
        "when SolidWorks asks to save them (the files on disk are as before that Update), then press Update SolidWorks "
        "again.")
    assert ui_text.still_in_error_sentence([ring]) == (
        "Ring_m1.25_N55 is still open in SolidWorks as an earlier Update SolidWorks left it, in error and holding the "
        "new values, so this press set nothing in it: close it in SolidWorks without saving (the file on disk is as "
        "before that Update), then press Update SolidWorks again.")
