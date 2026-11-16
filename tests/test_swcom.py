"""The parts of the SolidWorks link that are decidable without SolidWorks.

The version gate and the session choice are pure functions over plain data
precisely so they can be tested here, on a machine with no CAD package at all.
"""

import math
import threading
import time

import pytest

from gear_generator import swcom
from gear_generator.swcom import (
    Candidate,
    NotRunning,
    SolidWorksError,
    WrongVersion,
    choose,
    is_solidworks_moniker,
    parse_revision,
    pid_from_moniker,
    release_year,
)


def session(major, minor=0, patch=0, pid=1000, has_doc=False):
    return Candidate(
        moniker=f"SolidWorks_PID_{pid}",
        pid=pid,
        revision=(major, minor, patch),
        has_active_doc=has_doc,
    )


# -- reading a version ------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [("34.0.0", (34, 0, 0)), ("34", (34,)), ("34.1.0", (34, 1, 0)), (" 33.3.0 ", (33, 3, 0))],
)
def test_parse_revision(text, expected):
    assert parse_revision(text) == expected


@pytest.mark.parametrize("text", ["", "   ", "twenty-six", "34.x.0"])
def test_parse_revision_refuses_what_is_not_a_version(text):
    with pytest.raises(SolidWorksError, match="Could not read a version"):
        parse_revision(text)


@pytest.mark.parametrize("major,year", [(32, 2024), (33, 2025), (34, 2026), (35, 2027)])
def test_release_year_follows_the_yearly_convention(major, year):
    assert release_year(major) == year


# -- recognising a session --------------------------------------------------


@pytest.mark.parametrize("name", ["SolidWorks_PID_31392", "solidworks_pid_7"])
def test_a_session_moniker_is_recognised(name):
    assert is_solidworks_moniker(name)


@pytest.mark.parametrize(
    "name", ["", "!SolidWorks", "SolidWorksDocMgr", "SolidWorks_PID_", "SolidWorks_PID_x"]
)
def test_anything_else_is_not_a_session(name):
    assert not is_solidworks_moniker(name)


def test_the_pid_comes_out_of_the_moniker():
    """No round-trip to a session we may be about to discard."""
    assert pid_from_moniker("SolidWorks_PID_31392") == 31392


# -- choosing which session to drive ----------------------------------------


def test_nothing_running_says_so():
    with pytest.raises(NotRunning, match="No running SolidWorks"):
        choose([])


def test_only_older_versions_are_refused_by_name():
    with pytest.raises(WrongVersion) as raised:
        choose([session(30), session(31)])
    message = str(raised.value)
    assert "SolidWorks 2022" in message
    assert "SolidWorks 2023" in message
    assert "2024" in message


def test_the_supported_versions_are_taken():
    assert choose([session(34)]).revision == (34, 0, 0)
    assert choose([session(32)]).revision == (32, 0, 0)
    assert choose([session(31), session(32)]).revision == (32, 0, 0)


def test_an_older_session_alongside_a_supported_one_is_ignored():
    assert choose([session(33), session(34)]).revision == (34, 0, 0)


def test_a_newer_release_is_used_not_refused():
    """The whole point of a floor rather than an equality: 2027 must just work."""
    assert choose([session(34), session(35)]).revision == (35, 0, 0)


def test_a_service_pack_beats_the_base_release():
    assert choose([session(34, 0, 0), session(34, 1, 0)]).revision == (34, 1, 0)


def test_a_session_with_a_document_open_wins_a_tie():
    """Almost certainly the window the user is looking at."""
    quiet = session(34, pid=100, has_doc=False)
    busy = session(34, pid=200, has_doc=True)
    assert choose([quiet, busy]).pid == 200


def test_the_choice_is_deterministic_when_nothing_separates_them():
    assert choose([session(34, pid=300), session(34, pid=100)]).pid == 100


def test_a_release_newer_than_tested_is_flagged_but_still_chosen():
    chosen = choose([session(36)])
    assert chosen.revision == (36, 0, 0)
    assert swcom.is_newer_than_tested(chosen.revision)
    assert not swcom.is_newer_than_tested((34, 0, 0))


@pytest.mark.parametrize("revision,ok", [((31, 9, 9), False), ((32, 0, 0), True), ((34, 0, 0), True), ((40, 0), True)])
def test_the_floor_is_a_floor(revision, ok):
    assert swcom.meets_minimum(revision) is ok


# -- degrading without pywin32 ----------------------------------------------


def test_finding_sessions_without_pywin32_says_why(monkeypatch):
    monkeypatch.setattr(swcom, "pythoncom", None)
    assert swcom.is_available() is False
    assert swcom.unavailable_reason()
    with pytest.raises(swcom.NotAvailable):
        swcom.find_candidates()


def test_the_diagnostic_reports_a_missing_pywin32_rather_than_crashing(monkeypatch, capsys):
    monkeypatch.setattr(swcom, "pythoncom", None)
    assert swcom.main([]) == swcom.EXIT_NOT_AVAILABLE
    assert "pip install pywin32" in capsys.readouterr().out


# -- the worker thread ------------------------------------------------------


class FakeSession:
    def __init__(self):
        self.calls = []


def test_the_worker_runs_work_on_its_own_thread_and_returns_plain_data():
    worker = swcom.Worker(connect_fn=FakeSession)
    try:
        call = worker.submit(lambda s: "answer")
        value, error = call.wait(timeout=5)
        assert (value, error) == ("answer", None)
    finally:
        worker.shutdown()


def test_a_failure_comes_back_as_a_value_not_a_dead_thread():
    def explode(_session):
        raise RuntimeError("SolidWorks said no")

    worker = swcom.Worker(connect_fn=FakeSession)
    try:
        value, error = worker.submit(explode).wait(timeout=5)
        assert value is None
        assert isinstance(error, RuntimeError)

        # The thread must still be alive and usable afterwards.
        assert worker.submit(lambda s: 1).wait(timeout=5) == (1, None)
    finally:
        worker.shutdown()


def test_a_failed_call_drops_the_session_so_the_next_one_reconnects():
    made = []

    def connect_fn():
        made.append(object())
        return made[-1]

    def explode(_session):
        raise RuntimeError("connection lost")

    worker = swcom.Worker(connect_fn=connect_fn)
    try:
        worker.submit(lambda s: None).wait(timeout=5)
        assert len(made) == 1
        worker.submit(explode).wait(timeout=5)
        worker.submit(lambda s: None).wait(timeout=5)
        assert len(made) == 2
    finally:
        worker.shutdown()


def test_a_connection_failure_is_reported_not_raised_on_the_thread():
    def refuse():
        raise swcom.NotRunning("nothing there")

    worker = swcom.Worker(connect_fn=refuse)
    try:
        value, error = worker.submit(lambda s: 1).wait(timeout=5)
        assert value is None
        assert isinstance(error, swcom.NotRunning)
    finally:
        worker.shutdown()


def test_polling_returns_at_once_whether_or_not_the_answer_is_ready():
    """The interface polls this on a timer, so it must never wait for anything."""
    started = threading.Event()
    release = threading.Event()

    def slow(_session):
        started.set()
        release.wait(5)
        return 42

    worker = swcom.Worker(connect_fn=FakeSession)
    try:
        call = worker.submit(slow)
        assert started.wait(5)

        # The job is definitely still running, so poll must say "not yet"
        # rather than block until it finishes.
        began = time.monotonic()
        assert call.poll() is None
        assert time.monotonic() - began < 0.5

        release.set()
        assert call.wait(timeout=5) == (42, None)
        assert call.poll() == (42, None)
    finally:
        release.set()
        worker.shutdown()


def test_the_worker_reports_being_busy_while_a_call_is_in_flight():
    """Two interleaved refresh sequences would corrupt a part, so the window
    disables Export on this rather than queueing a second one."""
    started = threading.Event()
    release = threading.Event()

    def slow(_session):
        started.set()
        release.wait(5)
        return None

    worker = swcom.Worker(connect_fn=FakeSession)
    try:
        call = worker.submit(slow)
        assert started.wait(5)
        assert worker.busy() is True
        release.set()
        call.wait(timeout=5)
        for _ in range(100):
            if not worker.busy():
                break
            time.sleep(0.01)
        assert worker.busy() is False
    finally:
        release.set()
        worker.shutdown()


# -- W4: the members a workbook's layout part and static assembly use, against a fake COM world ----------
#
# Late binding reaches a zero-argument member as an attribute and calls only members given arguments
# (swcom.call), so the fakes below expose GetTitle, ActiveDoc, FirstFeature … as attributes and OpenDoc6,
# Select2, AddComponent5 … as methods, as SolidWorks does through pywin32.

from gear_generator import findings  # noqa: E402

W = "C:\\W\\"


class Out:
    """A by-reference integer, as swcom._out_long makes one with pywin32."""

    def __init__(self):
        self.value = 0


@pytest.fixture
def com(monkeypatch):
    monkeypatch.setattr(swcom, "_out_long", Out)
    monkeypatch.setattr(swcom, "_null_dispatch", lambda: None)
    monkeypatch.setattr(swcom.time, "sleep", lambda _seconds: None)
    return App()


class Feature:
    def __init__(self, doc, name, type_name="RefPlane", specific=None):
        self.doc, self.Name, self.GetTypeName2 = doc, name, type_name
        self.GetFirstSubFeature = None
        self.GetSpecificFeature2 = specific

    @property
    def GetNextFeature(self):
        features = self.doc.features
        index = features.index(self)
        return features[index + 1] if index + 1 < len(features) else None

    def Select2(self, append, mark):
        self.doc.app.log.append(("Select2", self.Name, append))
        self.doc.selected.append(self.Name)
        return True


class Selection:
    def __init__(self, doc):
        self.doc = doc

    def GetSelectedObjectCount2(self, mark):
        return len(self.doc.selected)


class Extension:
    def __init__(self, doc):
        self.doc = doc

    def SelectByID2(self, name, kind, x, y, z, append, mark, callout, option):
        self.doc.app.log.append(("SelectByID2", name, kind, append))
        if kind == "PLANE" and any(f.Name == name for f in self.doc.features):
            self.doc.selected.append(name)
            return True
        return False


class Transform:
    def __init__(self, data):
        self.ArrayData = tuple(data)


class Component:
    def __init__(self, name, model=None, path="", state=2, data=None):
        self.Name2, self.GetModelDoc2, self.GetPathName = name, model, path
        self.GetSuppression2 = state
        self.Transform2 = Transform(data or (1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 0, 0, 0))


class Root:
    def __init__(self, doc):
        self.doc = doc

    @property
    def GetChildren(self):
        return tuple(self.doc.components)


class Configuration:
    def __init__(self, doc):
        self.doc = doc

    def GetRootComponent3(self, resolve):
        return Root(self.doc)


class Interference:
    def __init__(self, components, volume_m3):
        self.Components, self.Volume = components, volume_m3

    @property
    def GetComponents(self):
        return self.Components


class Manager:
    def __init__(self, items, fail=False):
        self.items, self.fail, self.done, self.options = items, fail, 0, {}

    def __setattr__(self, name, value):
        if name[0].isupper():
            self.options[name] = value
        object.__setattr__(self, name, value)

    @property
    def GetInterferences(self):
        if self.fail:
            raise RuntimeError("the manager went away")
        return tuple(self.items)

    def Done(self):
        object.__setattr__(self, "done", self.done + 1)


class Doc:
    def __init__(self, app, path, doc_type=1, title=None):
        self.app, self.GetPathName, self.GetType = app, path, doc_type
        self.GetTitle = title or path.rsplit("\\", 1)[-1]
        self.features = [Feature(self, n) for n in ("Front Plane", "Top Plane", "Right Plane")]
        self.features.append(Feature(self, "Origin", "OriginProfileFeature"))
        self.selected, self.components, self.manager = [], [], None
        self.SelectionManager, self.Extension = Selection(self), Extension(self)
        self.GetActiveConfiguration = Configuration(self)
        self.GetSaveFlag, self.fails = False, False

    def ForceRebuild3(self, top_only):
        """As probe assembly_rebuild_scope found it on 2026 and 2024: the document is marked modified; a FULL
        rebuild of an assembly marks every component's document too; a component in error fails it either way."""
        self.app.log.append(("ForceRebuild3", self.GetTitle, top_only))
        return self._rebuilt(full=not top_only)

    @property
    def EditRebuild3(self):                    # a zero-argument member: late binding reads it as an attribute
        self.app.log.append(("EditRebuild3", self.GetTitle))
        return self._rebuilt(full=False)

    def _rebuilt(self, full):
        self.GetSaveFlag = True
        models = [c.GetModelDoc2 for c in self.components if c.GetModelDoc2 is not None]
        if full:
            for model in models:
                model.GetSaveFlag = True
        return not (self.fails or any(model.fails for model in models))

    @property
    def GetNext(self):
        docs = self.app.docs
        index = docs.index(self)
        return docs[index + 1] if index + 1 < len(docs) else None

    @property
    def FirstFeature(self):
        return self.features[0] if self.features else None

    @property
    def InterferenceDetectionManager(self):
        return self.manager

    def ClearSelection2(self, everything):
        self.selected = []

    def InsertAxis2(self, auto):
        self.app.log.append(("InsertAxis2", tuple(self.selected)))
        if len(self.selected) != 2:
            return False
        self.features.append(Feature(self, f"Axis{len(self.features)}", "RefAxis"))
        return True

    def GetComponentByName(self, name):
        return next((c for c in self.components if c.Name2 == name), None)

    def GetComponents(self, top):
        return tuple(self.components)

    def FeatureByName(self, name):
        component = self.GetComponentByName(name)
        return None if component is None else Feature(self, name, "Reference", specific=component)

    def AddComponent5(self, path, option, configuration, use_name, name, x, y, z):
        model = self.app.inserts.get(path, self.app.find(path))
        if model is False:
            return None
        component = Component(path.rsplit("\\", 1)[-1].rsplit(".", 1)[0] + "-1", model=model,
                              path=getattr(model, "GetPathName", ""))
        self.components.append(component)
        return component


class Spec:
    def __init__(self, path):
        self.path, self.Silent, self.Error = path, False, 0


class App:
    def __init__(self):
        self.docs, self.disk, self.log, self.active = [], {}, [], None
        self.activates, self.errors, self.inserts = True, {}, {}

    def find(self, path):
        return next((d for d in self.docs if d.GetPathName.lower() == path.lower()), None)

    def saved(self, path, doc_type=1):
        self.disk[path.lower()] = Doc(self, path, doc_type)
        return self.disk[path.lower()]

    def opened(self, path, doc_type=1, active=True):
        doc = Doc(self, path, doc_type)
        self.docs.append(doc)
        if active:
            self.active = doc
        return doc

    @property
    def GetFirstDocument(self):
        return self.docs[0] if self.docs else None

    @property
    def ActiveDoc(self):
        return self.active

    def _open(self, path):
        open_doc = self.find(path)
        if open_doc is not None:
            return open_doc, 0, swcom.findings.OPEN_DOC_ALREADY_OPEN_WARNING
        if path in self.errors:
            return None, self.errors[path], 0
        doc = self.disk.get(path.lower())
        if doc is None:
            return None, 2, 0
        self.docs.append(doc)
        self.active = doc
        return doc, 0, 0

    def OpenDoc6(self, path, doc_type, options, configuration, errors, warnings):
        self.log.append(("OpenDoc6", path, doc_type, options, configuration))
        doc, errors.value, warnings.value = self._open(path)
        return doc

    def GetOpenDocSpec(self, path):
        self.log.append(("GetOpenDocSpec", path))
        return Spec(path)

    def OpenDoc7(self, spec):
        self.log.append(("OpenDoc7", spec.path, spec.Silent))
        doc, spec.Error, _ = self._open(spec.path)
        return doc

    def OpenDoc(self, path, doc_type):
        self.log.append(("OpenDoc", path, doc_type))
        return self._open(path)[0]

    def ActivateDoc3(self, title, use_user_preferences, option, errors):
        self.log.append(("ActivateDoc3", title))
        if self.activates:
            self.active = next(d for d in self.docs if d.GetTitle == title)
        return self.active

    def GetUserPreferenceToggle(self, which):
        return False

    def SetUserPreferenceToggle(self, which, value):
        pass


def _session(app):
    return swcom.Session(app, (34, 0, 0), 1)


def _calls(app, name):
    return [entry for entry in app.log if entry[0] == name]


# -- open_document


def test_a_closed_part_is_opened_silently_then_activated_and_becomes_the_build_document(com):
    com.opened(W + "Other.SLDPRT")
    part = com.saved(W + "Gear_m1.5_N68.SLDPRT")
    session = _session(com)
    info = session.open_document(W + "Gear_m1.5_N68.SLDPRT")
    assert info == swcom.DocInfo("Gear_m1.5_N68.SLDPRT", W + "Gear_m1.5_N68.SLDPRT", 1)
    assert _calls(com, "OpenDoc6") == [("OpenDoc6", W + "Gear_m1.5_N68.SLDPRT", 1, findings.OPEN_DOC_SILENT, "")]
    assert _calls(com, "ActivateDoc3") == [("ActivateDoc3", "Gear_m1.5_N68.SLDPRT")]
    assert session._doc() is part


def test_a_part_already_open_behind_another_is_still_brought_forward(com):
    part = com.opened(W + "Gear_m1.5_N68.SLDPRT")
    com.opened(W + "Other.SLDPRT")
    session = _session(com)
    session.open_document(W + "gear_m1.5_n68.sldprt")
    assert com.active is part and _calls(com, "ActivateDoc3") == [("ActivateDoc3", "Gear_m1.5_N68.SLDPRT")]


@pytest.mark.parametrize("route", ["OpenDoc6", "OpenDoc7", "OpenDoc"])
def test_an_assembly_opens_by_its_own_route(com, monkeypatch, route):
    monkeypatch.setattr(findings, "OPEN_ASSEMBLY_ROUTE", route, raising=False)
    com.saved(W + "R.SLDASM", doc_type=2)
    info = _session(com).open_document(W + "R.SLDASM")
    assert info.is_assembly
    assert [entry[0] for entry in com.log if entry[0] != "ActivateDoc3"] == (
        ["GetOpenDocSpec", "OpenDoc7"] if route == "OpenDoc7" else [route])
    if route == "OpenDoc7":
        assert _calls(com, "OpenDoc7") == [("OpenDoc7", W + "R.SLDASM", True)]
    else:
        assert com.log[0][2] == swcom.DOC_ASSEMBLY


def test_a_same_named_document_from_another_folder_is_refused_before_anything_is_asked(com):
    com.opened(r"C:\Other\Gear_m1.5_N68.SLDPRT")
    com.saved(W + "Gear_m1.5_N68.SLDPRT")
    with pytest.raises(SolidWorksError) as raised:
        _session(com).open_document(W + "Gear_m1.5_N68.SLDPRT")
    assert str(raised.value) == (r"C:\Other\Gear_m1.5_N68.SLDPRT is open in SolidWorks, and it has the same file "
                                 r"name as C:\W\Gear_m1.5_N68.SLDPRT; SolidWorks keeps one document per file name, "
                                 "so close Gear_m1.5_N68.SLDPRT in SolidWorks and try again.")
    assert com.log == []


@pytest.mark.parametrize("error,sentence", [
    (65536, r"SolidWorks would not open C:\W\Gear.SLDPRT: a document of the same file name is open from another "
            "folder (error 65536); close it in SolidWorks and try again."),
    (2, r"SolidWorks would not open C:\W\Gear.SLDPRT (error 2)."),
])
def test_an_open_that_fails_says_what_solidworks_answered(com, error, sentence):
    com.errors[W + "Gear.SLDPRT"] = error
    with pytest.raises(SolidWorksError) as raised:
        _session(com).open_document(W + "Gear.SLDPRT")
    assert str(raised.value) == sentence
    assert _calls(com, "ActivateDoc3") == []


@pytest.mark.parametrize("name,value,sentence", [
    ("OPEN_DOC_ROUTE", None, "Opening Gear.SLDPRT by its path has not been settled on SolidWorks yet "
                             "(findings.OPEN_DOC_ROUTE is None); run probe tier 7 first."),
    ("OPEN_DOC_ROUTE", "OpenDoc9", "Opening Gear.SLDPRT by its path has not been settled on SolidWorks yet "
                                   "(findings.OPEN_DOC_ROUTE is 'OpenDoc9'); run probe tier 7 first."),
    ("OPEN_DOC_SILENT", None, "Opening Gear.SLDPRT by its path has not been settled on SolidWorks yet "
                              "(findings.OPEN_DOC_ROUTE is 'OpenDoc6'); run probe tier 7 first."),
    ("UPDATE_OPEN_ROUTE", None, "Opening Gear.SLDPRT by its path has not been settled on SolidWorks yet "
                                "(findings.UPDATE_OPEN_ROUTE is None); run probe tier 7 first."),
])
def test_an_unsettled_open_route_is_refused_not_guessed(com, monkeypatch, name, value, sentence):
    monkeypatch.setattr(findings, name, value, raising=False)
    com.saved(W + "Gear.SLDPRT")
    with pytest.raises(SolidWorksError) as raised:
        _session(com).open_document(W + "Gear.SLDPRT")
    assert str(raised.value) == sentence and com.log == []


def test_with_the_ask_route_an_open_document_is_activated_and_a_closed_one_is_asked_for(com, monkeypatch):
    monkeypatch.setattr(findings, "UPDATE_OPEN_ROUTE", "ask", raising=False)
    part = com.opened(W + "Gear.SLDPRT", active=False)
    com.opened(W + "Other.SLDPRT")
    com.saved(W + "Closed.SLDPRT")
    session = _session(com)
    session.open_document(W + "Gear.SLDPRT")
    assert com.active is part and _calls(com, "OpenDoc6") == []
    with pytest.raises(SolidWorksError) as raised:
        session.open_document(W + "Closed.SLDPRT")
    assert str(raised.value) == (r"Open C:\W\Closed.SLDPRT in SolidWorks, then try again: this SolidWorks cannot be "
                                 "asked to open a document by its path (findings.UPDATE_OPEN_ROUTE).")


def test_documents_walks_to_the_end_of_solidworks_list_however_long(com):
    """Third W4 review item 1 (w4x_documents_cap): the walk stopped at 200, and one large assembly loads more; a
    document holding Update's unsaved changes then missed the list and passed as loaded from its file."""
    for index in range(260):
        com.opened(W + f"Doc{index}.SLDPRT", active=False)
    listed = _session(com).documents()
    assert len(listed) == 260 and listed[-1].path == W + "Doc259.SLDPRT"
    # open_document's own same-name check walks the same way: a clash past the 200th document is still refused.
    com.saved(W + "Sub\\Doc250.SLDPRT")
    with pytest.raises(SolidWorksError, match="same file name"):
        _session(com).open_document(W + "Sub\\Doc250.SLDPRT")


def test_a_list_of_documents_that_never_ends_is_refused_with_a_sentence(com, monkeypatch):
    monkeypatch.setattr(swcom, "DOCUMENT_WALK_LIMIT", 5)
    for index in range(5):
        com.opened(W + f"Doc{index}.SLDPRT", active=False)
    assert len(_session(com).documents()) == 5                      # the end reached at the limit: all listed
    com.opened(W + "Doc5.SLDPRT", active=False)
    with pytest.raises(swcom.DocumentsUnknown) as raised:
        _session(com).documents()
    assert str(raised.value) == ("SolidWorks listed 5 open documents without coming to the end of its list, so which "
                                 "documents it holds open cannot be known here, and nothing that depends on it is "
                                 "started; restart SolidWorks and try again.")


def test_unsaved_changes_are_read_from_the_save_flag_of_the_document_just_opened(com):
    part = com.saved(W + "Gear.SLDPRT")
    other = com.opened(W + "Other.SLDPRT")
    other.GetSaveFlag = True                                         # what is on screen is not what is asked about
    part.GetSaveFlag = False
    session = _session(com)
    session.open_document(W + "Gear.SLDPRT")
    assert session.has_unsaved_changes() is False
    part.GetSaveFlag = True
    assert session.has_unsaved_changes() is True


def test_a_document_that_does_not_come_forward_is_refused(com):
    com.opened(W + "Other.SLDPRT")
    com.saved(W + "Gear.SLDPRT")
    com.activates = False
    com.disk[(W + "Gear.SLDPRT").lower()].app = com
    original = com._open

    def open_behind(path):                         # opened, but left behind the other document
        doc, error, warning = original(path)
        com.active = com.docs[0]
        return doc, error, warning

    com._open = open_behind
    with pytest.raises(SolidWorksError) as raised:
        _session(com).open_document(W + "Gear.SLDPRT")
    assert str(raised.value) == ("SolidWorks opened Gear.SLDPRT but left Other.SLDPRT active after ActivateDoc3, so "
                                 "it is not changed.")


@pytest.mark.parametrize("path,sentence", [
    (W + "Notes.txt", r"C:\W\Notes.txt is neither a SolidWorks part nor an assembly, so it is not opened."),
    (W + "Odd.SLDASM", r"C:\W\Odd.SLDASM opened as a document of type 1, not as an assembly."),
])
def test_what_is_not_the_document_asked_for_is_refused(com, path, sentence):
    com.saved(W + "Odd.SLDASM", doc_type=1)
    with pytest.raises(SolidWorksError) as raised:
        _session(com).open_document(path)
    assert str(raised.value) == sentence


# -- find_component, component_frame


def _assembly(com, *components):
    asm = com.opened(W + "R.SLDASM", doc_type=2)
    asm.components.extend(components)
    session = _session(com)
    session.begin_build()
    session.open_document(W + "R.SLDASM")
    return session, asm


@pytest.mark.parametrize("route", swcom.COMPONENT_FIND_ROUTES)
def test_a_component_is_found_by_its_recorded_name_by_every_route(com, monkeypatch, route):
    monkeypatch.setattr(findings, "COMPONENT_FIND_ROUTE", route, raising=False)
    model = com.opened(W + "Gear_m1.5_N68.SLDPRT", active=False)
    wanted = Component("Gear_m1.5_N68-1", model=model)
    session, _ = _assembly(com, Component("Gear_m1.5_N17-1"), wanted)
    assert session.find_component("placed2", "Gear_m1.5_N68-1") == "Gear_m1.5_N68-1"
    assert session._handles["placed2"] == {"component": wanted, "path": W + "Gear_m1.5_N68.SLDPRT",
                                           "name": "Gear_m1.5_N68-1", "epoch": session._epoch}


@pytest.mark.parametrize("route", swcom.COMPONENT_FIND_ROUTES)
def test_a_component_renamed_or_deleted_is_named_in_the_sentence(com, monkeypatch, route):
    monkeypatch.setattr(findings, "COMPONENT_FIND_ROUTE", route, raising=False)
    session, _ = _assembly(com, Component("Gear_m1.5_N17-1"))
    with pytest.raises(SolidWorksError) as raised:
        session.find_component("placed2", "Gear_m1.5_N68-1")
    assert str(raised.value) == "Gear_m1.5_N68-1 is not in R.SLDASM any more: it was renamed or deleted in SolidWorks."


def test_an_unsettled_find_route_is_refused(com, monkeypatch):
    monkeypatch.setattr(findings, "COMPONENT_FIND_ROUTE", None, raising=False)
    session, _ = _assembly(com, Component("G-1"))
    with pytest.raises(SolidWorksError, match=r"\(findings.COMPONENT_FIND_ROUTE is None\); run probe tier 7 first\."):
        session.find_component("placed1", "G-1")


def test_a_route_that_answers_with_another_component_is_refused(com, monkeypatch):
    monkeypatch.setattr(findings, "COMPONENT_FIND_ROUTE", "GetComponentByName", raising=False)
    session, asm = _assembly(com)
    asm.GetComponentByName = lambda name: Component("Other-1")
    with pytest.raises(SolidWorksError) as raised:
        session.find_component("placed1", "G-1")
    assert str(raised.value) == ("Asked for G-1 in R.SLDASM, SolidWorks gave Other-1, so which component is meant "
                                 "cannot be told.")


@pytest.mark.parametrize("state,resolved,sentence", [
    (0, True, "G-1 is suppressed in R.SLDASM, so it cannot be placed; unsuppress it in SolidWorks and try again."),
    (1, True, "G-1 is loaded lightweight in R.SLDASM, and resolving a component is not settled here; set it to "
              "Resolved in SolidWorks and try again."),
    (4, True, "G-1 is loaded lightweight in R.SLDASM, and resolving a component is not settled here; set it to "
              "Resolved in SolidWorks and try again."),
    ("unread", None, "G-1 is loaded lightweight in R.SLDASM, and resolving a component is not settled here; set it "
                     "to Resolved in SolidWorks and try again."),
    ("unread", True, ""),
    (3, False, ""),
])
def test_a_component_that_is_not_resolved_is_refused_with_what_to_do(com, monkeypatch, state, resolved, sentence):
    monkeypatch.setattr(findings, "COMPONENTS_RESOLVED_AFTER_REOPEN", resolved, raising=False)
    component = Component("G-1", state=None if state == "unread" else state)
    session, _ = _assembly(com, component)
    if not sentence:
        assert session.find_component("placed1", "G-1") == "G-1"
        return
    with pytest.raises(SolidWorksError) as raised:
        session.find_component("placed1", "G-1")
    assert str(raised.value) == sentence


def _rows_to_columns(rows):
    return [rows[i * 3 + j] for j in range(3) for i in range(3)]


ROWS = (0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)    # a quarter turn about Z, by rows


@pytest.mark.parametrize("order", ["columns", "rows"])
def test_a_component_frame_is_read_as_place_component_writes_it(com, monkeypatch, order):
    monkeypatch.setattr(findings, "TRANSFORM_ARRAY_ORDER", order, raising=False)
    data = (_rows_to_columns(ROWS) if order == "columns" else list(ROWS)) + [0.06375, -0.002, 0.005, 1.0, 0, 0, 0]
    session, _ = _assembly(com, Component("G-1", data=data))
    session.find_component("placed1", "G-1")
    rotation, at = session.component_frame("placed1")
    assert rotation == ROWS and at == pytest.approx((63.75, -2.0, 5.0))


def test_an_unsettled_frame_layout_is_refused(com, monkeypatch):
    monkeypatch.setattr(findings, "TRANSFORM_ARRAY_ORDER", None, raising=False)
    session, _ = _assembly(com, Component("G-1"))
    session.find_component("placed1", "G-1")
    with pytest.raises(SolidWorksError, match=r"TRANSFORM_ARRAY_ORDER is None"):
        session.component_frame("placed1")


# -- interferences


def _clash_world(com, items, fail=False):
    session, asm = _assembly(com)
    asm.manager = Manager(items, fail)
    return session, asm.manager


def test_each_interference_names_its_components_and_gives_its_volume_and_done_is_called(com):
    a, b = Component("Gear_m1.5_N17-1"), Component("Gear_m1.5_N68-1")
    session, manager = _clash_world(com, [Interference((a, b), 12.5e-9)])
    assert session.interferences() == [(("Gear_m1.5_N17-1", "Gear_m1.5_N68-1"), pytest.approx(12.5))]
    assert manager.done == 1 and manager.options == dict(findings.INTERFERENCE_OPTIONS)


@pytest.mark.parametrize("route,named", [("Components (property)", True), ("GetComponents()", True), (None, False),
                                         ("something else", False)])
def test_the_names_follow_the_route_and_are_empty_where_it_cannot_name_them(com, monkeypatch, route, named):
    monkeypatch.setattr(findings, "INTERFERENCE_NAMES_ROUTE", route, raising=False)
    session, _ = _clash_world(com, [Interference((Component("A-1"), Component("B-1")), 1e-9)])
    assert session.interferences()[0][0] == (("A-1", "B-1") if named else ())


def test_components_that_will_not_name_themselves_leave_the_volume(com):
    item = Interference((object(),), 2e-9)
    session, _ = _clash_world(com, [item])
    assert session.interferences() == [((), pytest.approx(2.0))]


def test_done_is_called_even_when_the_list_cannot_be_read(com):
    session, manager = _clash_world(com, [], fail=True)
    with pytest.raises(RuntimeError):
        session.interferences()
    assert manager.done == 1


# -- add_component reads back the file it took


def test_a_component_inserted_from_the_file_asked_for_is_kept(com):
    part = com.opened(W + "Gear_m1.5_N68.SLDPRT", active=False)
    session, asm = _assembly(com)
    assert session.add_component("gear2", W + "Gear_m1.5_N68.SLDPRT", (63.75, 0.0, 0.0)) == "Gear_m1.5_N68-1"
    assert asm.components[0].GetModelDoc2 is part and "gear2" in session._handles


def test_a_component_that_took_another_folders_file_is_refused(com):
    com.inserts[W + "Gear_m1.5_N68.SLDPRT"] = Doc(com, r"C:\Other\Gear_m1.5_N68.SLDPRT")
    session, _ = _assembly(com)
    with pytest.raises(SolidWorksError) as raised:
        session.add_component("gear2", W + "Gear_m1.5_N68.SLDPRT", (0.0, 0.0, 0.0))
    assert str(raised.value) == (r"AddComponent5 put Gear_m1.5_N68-1 into R.SLDASM from C:\Other\Gear_m1.5_N68.SLDPRT,"
                                 r" not from C:\W\Gear_m1.5_N68.SLDPRT; a document of the same file name may be open "
                                 "from another folder.")


def test_a_lightweight_component_is_checked_by_its_own_path(com):
    session, asm = _assembly(com)
    com.inserts[W + "G.SLDPRT"] = None
    original = asm.AddComponent5

    def lightweight(path, *args):
        component = original(path, *args)
        component.GetPathName = path
        return component

    asm.AddComponent5 = lightweight
    assert session.add_component("gear1", W + "G.SLDPRT", (0.0, 0.0, 0.0)) == "G-1"


def test_a_component_whose_file_cannot_be_read_back_is_refused(com):
    com.inserts[W + "G.SLDPRT"] = None
    session, _ = _assembly(com)
    with pytest.raises(SolidWorksError, match="from a file whose path could not be read, not from"):
        session.add_component("gear1", W + "G.SLDPRT", (0.0, 0.0, 0.0))


# -- insert_axis through planes this build made


def _layout(com):
    doc = com.opened(W + "Part1.SLDPRT")
    session = _session(com)
    session.begin_build()
    x1, y1 = Feature(doc, "S2 X Plane"), Feature(doc, "S2 Y Plane")
    doc.features += [x1, y1]
    session._handles.update({"x1": "S2 X Plane", "y1": "S2 Y Plane"})
    session._plane_objects.update({"x1": x1, "y1": y1})
    return session, doc


@pytest.mark.parametrize("route,how", [("Select2 on the feature found by name", "Select2"),
                                       ("SelectByID2 by name", "SelectByID2"),
                                       ("Select2 on what InsertRefPlane returned", "Select2")])
def test_an_axis_goes_through_planes_made_in_this_build_selected_by_the_settled_route(com, monkeypatch, route, how):
    monkeypatch.setattr(findings, "AXIS_PLANE_SELECT_ROUTE", route, raising=False)
    session, doc = _layout(com)
    assert session.insert_axis("axis2", "S2 Axis", ("y1", "x1")) == "S2 Axis"
    assert _calls(com, "InsertAxis2") == [("InsertAxis2", ("S2 Y Plane", "S2 X Plane"))]
    assert [entry[1] for entry in com.log if entry[0] == how] == ["S2 Y Plane", "S2 X Plane"]
    assert doc.features[-1].Name == "S2 Axis" and session._handles["axis2"] == "S2 Axis"


def test_an_axis_through_a_base_plane_and_a_made_one_selects_them_in_the_order_given(com):
    session, _ = _layout(com)
    session.insert_axis("axis2", "S2 Axis", (2, "x1"))
    assert _calls(com, "InsertAxis2") == [("InsertAxis2", ("Top Plane", "S2 X Plane"))]


@pytest.mark.parametrize("name,planes,sentence", [
    ("AXIS_PLANE_SELECT_ROUTE", ("y1", "x1"),
     "The axis S2 Axis goes through a plane made in this build, and how to select such a plane has not been settled "
     "on SolidWorks yet (findings.AXIS_PLANE_SELECT_ROUTE is None); run probe tier 7 first."),
    ("AXIS_THROUGH_BASE_PLANE", (2, "x1"),
     "The axis S2 Axis goes through a base plane and a plane made in this build, which has not been settled on "
     "SolidWorks yet (findings.AXIS_THROUGH_BASE_PLANE); run probe tier 7 first."),
])
def test_an_axis_through_made_planes_without_its_finding_is_refused(com, monkeypatch, name, planes, sentence):
    monkeypatch.setattr(findings, name, None, raising=False)
    session, _ = _layout(com)
    with pytest.raises(SolidWorksError) as raised:
        session.insert_axis("axis2", "S2 Axis", planes)
    assert str(raised.value) == sentence and com.log == []


def test_an_axis_through_a_plane_not_made_is_refused(com):
    session, _ = _layout(com)
    with pytest.raises(SolidWorksError, match=r"^The plane 'x9' has not been made in this build\.$"):
        session.insert_axis("axis2", "S2 Axis", (2, "x9"))


def test_the_strips_axis_through_planes_2_and_3_is_unchanged(com, monkeypatch):
    monkeypatch.setattr(findings, "AXIS_PLANE_SELECT_ROUTE", None, raising=False)
    session, _ = _layout(com)
    session.insert_axis("axis", "Gear Axis", (2, 3))
    assert _calls(com, "InsertAxis2") == [("InsertAxis2", ("Top Plane", "Right Plane"))]


def test_a_refused_axis_names_the_planes_it_was_given(com, monkeypatch):
    session, doc = _layout(com)
    doc.InsertAxis2 = lambda auto: False
    with pytest.raises(SolidWorksError) as raised:
        session.insert_axis("axis2", "S2 Axis", (2, "x1"))
    assert str(raised.value) == "InsertAxis2 would not make S2 Axis from plane 2 and S2 X Plane."


def test_a_missing_template_is_named_as_typed(com, monkeypatch):
    sw = swcom.Session(com, (34, 0, 0), 1)
    with pytest.raises(swcom.SolidWorksError) as raised:
        sw.new_assembly("C:\\T\\No such template.asmdot")
    assert str(raised.value) == "There is no assembly template at C:\\T\\No such template.asmdot."
    monkeypatch.setattr(swcom.Session, "default_template", lambda self, kind="part": "")
    with pytest.raises(swcom.SolidWorksError) as raised:
        sw.new_part("")
    assert str(raised.value).startswith("SolidWorks names no default part template")
    monkeypatch.setattr(swcom.Session, "default_template", lambda self, kind="part": "C:\\SW\\Part.prtdot")
    with pytest.raises(swcom.SolidWorksError) as raised:
        sw.new_part("")
    assert str(raised.value) == "SolidWorks' default part template, C:\\SW\\Part.prtdot, is not there."


# -- COM errors as sentences (W4 review B1) ------------------------------------------------------------------


class com_error(Exception):  # noqa: N801 - pywin32's name, so probe.comerr reads it as it reads the real one
    pass


class Raising:
    def __init__(self, error):
        self.error = error

    def SaveAs3(self, *args):  # noqa: N802 - a COM member's name
        raise self.error


RPC_FAILED = com_error(-2147023170, "The remote procedure call failed.", None, None)


@pytest.fixture
def com_errors(monkeypatch):
    monkeypatch.setattr(swcom, "_COM_ERRORS", (com_error,))
    swcom.CONNECTION.lost = False
    yield
    swcom.CONNECTION.lost = False


def test_a_com_error_comes_out_of_call_as_a_solidworks_error_with_a_sentence(com_errors):
    from gear_generator.probe import comerr
    with pytest.raises(swcom.ComError) as raised:
        swcom.call(Raising(RPC_FAILED), "SaveAs3", "C:\\P\\Gear.SLDPRT")
    error = raised.value
    assert isinstance(error, SolidWorksError)
    assert str(error) == ("SolidWorks did not complete SaveAs3: The remote procedure call failed "
                          "(RPC_S_CALL_FAILED). SolidWorks may have closed or crashed; the next press connects to it "
                          "again.")
    assert error.lost and error.hresult == 0x800706BE and error.__cause__ is RPC_FAILED
    # a probe reads the same evidence from it as from the bare com_error
    assert comerr.describe_error(error)["hresult"] == "0x800706BE" and error.args == RPC_FAILED.args
    assert swcom.CONNECTION.lost


def test_a_rejected_call_and_a_failed_member_say_so(com_errors):
    rejected = com_error(-2147418111, "Call was rejected by callee.", None, None)
    with pytest.raises(swcom.ComError) as raised:
        swcom.call(Raising(rejected), "SaveAs3", 0)
    assert str(raised.value) == ("SolidWorks did not complete SaveAs3: Call was rejected by callee "
                                 "(RPC_E_CALL_REJECTED). SolidWorks was busy, perhaps with a dialog open; close it in "
                                 "SolidWorks and try again.")
    failed = com_error(-2147352567, "Exception occurred.", (0, "SolidWorks", "Bad argument", None, 0, -2147024809), 3)
    with pytest.raises(swcom.ComError) as raised:
        swcom.call(Raising(failed), "SaveAs3", 0)
    assert str(raised.value) == ("SolidWorks did not complete SaveAs3: Bad argument "
                                 "(DISP_E_EXCEPTION).")
    assert not raised.value.lost and not swcom.CONNECTION.lost


class _Ole:
    """A dispatch's ``_oleobj_`` whose Invoke raises what it is given."""

    def __init__(self, error):
        self.error = error

    def GetIDsOfNames(self, name):  # noqa: N802 - pywin32's name
        return 7

    def Invoke(self, *args):  # noqa: N802 - pywin32's name
        raise self.error


class _Raw:
    def __init__(self, error):
        self._oleobj_ = _Ole(error)


class _PyCom:
    DISPATCH_PROPERTYPUT, DISPATCH_METHOD, VT_ARRAY, VT_R8 = 4, 1, 0x2000, 5


def test_an_indexed_put_goes_through_the_same_wrapper_as_call(com_errors, monkeypatch):
    """W4 review N4.1: every global set is an indexed put through Invoke, which reached COM directly — a failure
    read "it stopped on an unexpected com_error" and never marked the session lost."""
    monkeypatch.setattr(swcom, "pythoncom", _PyCom)
    with pytest.raises(swcom.ComError) as raised:
        swcom._put_indexed(_Raw(RPC_FAILED), "Equation", 3, '"No. of Teeth"= 69')
    assert str(raised.value) == ("SolidWorks did not complete setting Equation(3): The remote procedure call failed "
                                 "(RPC_S_CALL_FAILED). SolidWorks may have closed or crashed; the next press connects "
                                 "to it again.")
    assert swcom.CONNECTION.lost


def test_placing_a_component_goes_through_the_same_wrapper_as_call(com_errors, monkeypatch):
    """W4 review N4.1: place_component's CreateTransform Invoke reached COM directly too."""
    monkeypatch.setattr(swcom, "pythoncom", _PyCom)
    monkeypatch.setattr(swcom, "VARIANT", lambda kind, value: value)

    class Assembly:
        GetType = swcom.DOC_ASSEMBLY

    class App:
        GetMathUtility = _Raw(RPC_FAILED)          # late binding reads a zero-argument member as a property
        ActiveDoc = Assembly()                     # place_component settles its rebuild before the put

    session = swcom.Session(App(), (34, 0, 0), 1)
    session._handles = {"gear1": {"component": object()}}
    with pytest.raises(swcom.ComError) as raised:
        session.place_component("gear1", (1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0), (0.0, 0.0, 0.0), kind=swcom.ASSEMBLY_STATIC)
    assert str(raised.value).startswith("SolidWorks did not complete CreateTransform: The remote procedure call failed")
    assert swcom.CONNECTION.lost


def test_a_property_put_goes_through_the_same_wrapper_as_call(com_errors):
    rejected = com_error(-2147418111, "Call was rejected by callee.", None, None)

    class Feature:
        def __setattr__(self, name, value):
            raise rejected

    with pytest.raises(swcom.ComError) as raised:
        swcom._put(Feature(), "Name", "Gear")
    assert str(raised.value).startswith("SolidWorks did not complete setting Name: Call was rejected by callee")
    assert not swcom.CONNECTION.lost


def test_anything_else_passes_through_call_untouched(com_errors):
    with pytest.raises(ZeroDivisionError):
        swcom.call(Raising(ZeroDivisionError("no")), "SaveAs3", 0)


def test_a_job_that_kept_a_lost_connection_as_a_failure_still_drops_the_session():
    """build_gearbox turns a lost connection into a failure on its result and returns: the worker drops the session
    anyway, so the next press attaches afresh instead of calling a dead SolidWorks."""
    made = []

    def connect_fn():
        made.append(object())
        return made[-1]

    def kept(_session):
        swcom.CONNECTION.lost = True          # what call() sets when it wraps an RPC failure
        return "a partial result"

    worker = swcom.Worker(connect_fn=connect_fn)
    try:
        assert worker.submit(kept).wait(timeout=5) == ("a partial result", None)
        worker.submit(lambda s: None).wait(timeout=5)
        assert len(made) == 2
        worker.submit(lambda s: None).wait(timeout=5)
        assert len(made) == 2
    finally:
        worker.shutdown()


# -- the one rebuild: a part as always, an assembly top-only (probe assembly_rebuild_scope)


def _gearbox_world(com):
    """An assembly open and active, its layout and two gears loaded as its components, nothing modified."""
    assembly = com.opened(W + "R.SLDASM", doc_type=2)
    parts = [com.opened(W + name, active=False) for name in ("R_Layout.SLDPRT", "Gear_m1.5_N17.SLDPRT",
                                                              "Gear_m1.5_N68.SLDPRT")]
    for part in parts:
        assembly.components.append(Component(part.GetTitle.rsplit(".", 1)[0] + "-1", model=part,
                                             path=part.GetPathName))
    com.active = assembly
    return assembly, parts


def _marked(com):
    return [d.GetTitle for d in com.docs if d.GetSaveFlag]


def test_an_assembly_rebuilds_top_only_and_marks_only_itself(com):
    """W4 rerun on 2026: ForceRebuild3(False) marked every part of the assembly modified, untouched ones too."""
    assembly, _parts = _gearbox_world(com)
    assert _session(com).rebuild(kind=swcom.ASSEMBLY_STATIC) is True
    assert _calls(com, "ForceRebuild3") == [("ForceRebuild3", "R.SLDASM", True)]
    assert _marked(com) == ["R.SLDASM"]


def test_a_part_rebuilds_as_it_always_did(com):
    part = com.opened(W + "Gear_m1.5_N68.SLDPRT")
    assert _session(com).rebuild() is True
    assert _calls(com, "ForceRebuild3") == [("ForceRebuild3", "Gear_m1.5_N68.SLDPRT", False)]
    assert part.GetSaveFlag


def test_a_part_rebuilds_as_always_even_while_the_assembly_route_is_unsettled(com, monkeypatch):
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_ROUTE", None)
    com.opened(W + "Gear_m1.5_N68.SLDPRT")
    assert _session(com).rebuild() is True
    assert swcom.rebuild_call(swcom.DOC_PART) == ("ForceRebuild3", (False,))


def test_a_component_in_error_still_fails_the_top_only_rebuild(com):
    _assembly, parts = _gearbox_world(com)
    parts[2].fails = True
    assert _session(com).rebuild(kind=swcom.ASSEMBLY_STATIC) is False
    assert _marked(com) == ["R.SLDASM"]


def test_the_edit_rebuild_route_is_taken_when_the_finding_names_it(com, monkeypatch):
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_ROUTE", "EditRebuild3")
    _gearbox_world(com)
    assert _session(com).rebuild(kind=swcom.ASSEMBLY_STATIC) is True
    assert _calls(com, "EditRebuild3") == [("EditRebuild3", "R.SLDASM")] and _calls(com, "ForceRebuild3") == []
    assert _marked(com) == ["R.SLDASM"]


class _Utility:
    """IMathUtility whose CreateTransform, invoked as a method, makes the transform from the 16 numbers."""

    class _Ole:
        def __init__(self, log):
            self.log = log

        def GetIDsOfNames(self, name):  # noqa: N802 - pywin32's name
            return 9

        def Invoke(self, dispid, lcid, flags, result, data):  # noqa: N802 - pywin32's name
            self.log.append(("CreateTransform",))
            return Transform(data)

    def __init__(self, log):
        self._oleobj_ = self._Ole(log)


class _Placeable(Component):
    """A component whose Transform2 put is logged."""

    def __setattr__(self, name, value):
        if name == "Transform2" and hasattr(self, "log"):
            self.log.append(("Transform2 put", self.Name2))
        object.__setattr__(self, name, value)


def _placing(com, monkeypatch):
    monkeypatch.setattr(swcom, "pythoncom", _PyCom)
    monkeypatch.setattr(swcom, "VARIANT", lambda kind, value: value)
    com.GetMathUtility = _Utility(com.log)
    assembly, parts = _gearbox_world(com)
    gear = _Placeable("Gear_m1.5_N68-1", model=parts[2], path=parts[2].GetPathName)
    gear.log = com.log
    assembly.components[2] = gear
    session = _session(com)
    session._handles = {"gear2": {"component": gear}}
    return session, gear


def test_a_put_is_rebuilt_top_only_and_still_read_back(com, monkeypatch):
    session, gear = _placing(com, monkeypatch)
    turned = (0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)
    session.place_component("gear2", turned, (64.5, 0.0, 0.0), kind=swcom.ASSEMBLY_STATIC)
    assert [e for e in com.log if e[0] in ("CreateTransform", "Transform2 put", "ForceRebuild3")] == [
        ("CreateTransform",), ("Transform2 put", "Gear_m1.5_N68-1"), ("ForceRebuild3", "R.SLDASM", True)]
    assert _marked(com) == ["R.SLDASM"]                         # the gear's own part is not marked
    assert gear.Transform2.ArrayData[9:12] == pytest.approx((0.0645, 0.0, 0.0))


@pytest.mark.parametrize("route, top_only, sentence", [
    (None, True, "How to rebuild an assembly has not been settled on SolidWorks yet "
                 "(findings.ASSEMBLY_REBUILD_ROUTE is None), so no assembly is changed; run probe tier 7 first."),
    ("none", True, "How to rebuild an assembly has not been settled on SolidWorks yet "
                   "(findings.ASSEMBLY_REBUILD_ROUTE is 'none'), so no assembly is changed; run probe tier 7 first."),
    ("ForceRebuild3(True)", None, "findings.ASSEMBLY_REBUILD_ROUTE is 'ForceRebuild3(True)' but "
                                  "findings.ASSEMBLY_REBUILD_TOP_ONLY is None, and the two disagree, so no assembly is "
                                  "changed; run probe tier 7 again."),
    ("ForceRebuild3(True)", False, "findings.ASSEMBLY_REBUILD_ROUTE is 'ForceRebuild3(True)' but "
                                   "findings.ASSEMBLY_REBUILD_TOP_ONLY is False, and the two disagree, so no assembly "
                                   "is changed; run probe tier 7 again."),
])
def test_an_unsettled_assembly_rebuild_is_refused_before_anything_is_changed(com, monkeypatch, route, top_only,
                                                                              sentence):
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_ROUTE", route)
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_TOP_ONLY", top_only)
    session, gear = _placing(com, monkeypatch)
    before = gear.Transform2.ArrayData
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.rebuild(kind=swcom.ASSEMBLY_STATIC)
    assert str(raised.value) == sentence
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.place_component("gear2", (1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0), (64.5, 0.0, 0.0), kind=swcom.ASSEMBLY_STATIC)
    assert str(raised.value) == sentence
    assert gear.Transform2.ArrayData == before                 # refused before the put, not after it
    assert not any(e[0] in ("CreateTransform", "Transform2 put", "ForceRebuild3", "EditRebuild3") for e in com.log)
    assert _marked(com) == []


# -- three kinds of assembly (the reviews of 9c39fb8 and 31d1ac9): the caller says which; a pair and a train full


@pytest.mark.parametrize("kind", [swcom.ASSEMBLY_PAIR, swcom.ASSEMBLY_TRAIN])
@pytest.mark.parametrize("workbook_route", ["ForceRebuild3(True)", None])
def test_a_pair_or_a_train_rebuilds_in_full_as_it_always_did(com, monkeypatch, workbook_route, kind):
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_ROUTE", workbook_route)
    monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", None, raising=False)     # until the W5 batch sets it
    monkeypatch.setattr(findings, "PAIR_ASSEMBLY_REBUILD_ROUTE", None, raising=False)
    _gearbox_world(com)
    assert _session(com).rebuild(kind=kind) is True
    assert _calls(com, "ForceRebuild3") == [("ForceRebuild3", "R.SLDASM", False)]
    assert swcom.rebuild_call(swcom.DOC_ASSEMBLY, kind) == ("ForceRebuild3", (False,))


def test_a_put_in_a_pair_is_rebuilt_in_full(com, monkeypatch):
    session, _gear = _placing(com, monkeypatch)
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_ROUTE", None)        # a pair never leans on the workbook finding
    monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", "ForceRebuild3(True)", raising=False)   # nor the train's
    session.place_component("gear2", (1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0), (64.5, 0.0, 0.0), kind=swcom.ASSEMBLY_PAIR)
    assert _calls(com, "ForceRebuild3") == [("ForceRebuild3", "R.SLDASM", False)]


def test_each_kind_reads_its_own_finding_and_refuses_an_unknown_one(com, monkeypatch):
    monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", "EditRebuild3", raising=False)
    monkeypatch.setattr(findings, "PAIR_ASSEMBLY_REBUILD_ROUTE", None, raising=False)
    assert swcom.rebuild_call(swcom.DOC_ASSEMBLY, swcom.ASSEMBLY_TRAIN) == ("EditRebuild3", ())
    assert swcom.rebuild_call(swcom.DOC_ASSEMBLY, swcom.ASSEMBLY_PAIR) == ("ForceRebuild3", (False,))
    monkeypatch.setattr(findings, "PAIR_ASSEMBLY_REBUILD_ROUTE", "ForceRebuild3(True)", raising=False)
    assert swcom.rebuild_call(swcom.DOC_ASSEMBLY, swcom.ASSEMBLY_PAIR) == ("ForceRebuild3", (True,))
    monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", "guess", raising=False)
    _gearbox_world(com)
    with pytest.raises(swcom.SolidWorksError) as raised:
        _session(com).rebuild(kind=swcom.ASSEMBLY_TRAIN)
    assert str(raised.value) == ("findings.MATED_ASSEMBLY_REBUILD_ROUTE is 'guess', which is not a rebuild this code "
                                 "knows, so no mated assembly is changed; run its probe again.")
    assert _calls(com, "ForceRebuild3") == [] and _marked(com) == []


def test_an_assembly_whose_kind_is_not_said_is_refused_before_anything_is_changed(com, monkeypatch):
    """The review of 31d1ac9: with mated defaulting to False, a caller that forgot it put a mated assembly on the
    unprobed top-only route. Now an assembly's kind must be said; a part's need not."""
    session, gear = _placing(com, monkeypatch)
    before = gear.Transform2.ArrayData
    sentence = ("This assembly was to be rebuilt without saying what kind of assembly it is (fixed, a mated train "
                "or a pair), so which rebuild it takes cannot be chosen and nothing is changed; that is a fault in "
                "Gear Generator, not in SolidWorks.")
    for act in (lambda: session.rebuild(),
                lambda: session.place_component("gear2", (1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0), (64.5, 0.0, 0.0))):
        with pytest.raises(swcom.SolidWorksError) as raised:
            act()
        assert str(raised.value) == sentence
    with pytest.raises(swcom.SolidWorksError, match="'mated' is not a kind of assembly Gear Generator rebuilds"):
        session.rebuild(kind="mated")
    assert gear.Transform2.ArrayData == before and _marked(com) == []
    assert not any(e[0] in ("CreateTransform", "Transform2 put", "ForceRebuild3", "EditRebuild3") for e in com.log)
    assert swcom.rebuild_call(swcom.DOC_PART) == ("ForceRebuild3", (False,))


# -- W5: the train's mates (findings.py, "the workbook gearbox that turns (tier 8)" and "tier 8 items 7-13") -------
#
# A mocked assembly whose MateGroup holds the mates: each answers GetErrorCode2 and IsSuppressed2 as probe tier 8 read
# them (a tuple back, or an out parameter), SetSuppression2 takes or not, and AddMate5 makes one new mate (or none).


class OutBool:
    """A by-reference boolean, as swcom._out_bool makes one with pywin32."""

    def __init__(self):
        self.value = False


class SelectData:
    def __init__(self):
        self.Mark = 0


class MateFeature:
    def __init__(self, doc, name, type_name="MateCoincident", code=0, warning=True, suppressed=False):
        self.doc, self.Name, self.GetTypeName2 = doc, name, type_name
        self.code, self.warning, self.suppressed = code, warning, suppressed

    @property
    def GetNextSubFeature(self):
        mates = self.doc.mates
        index = mates.index(self)
        return mates[index + 1] if index + 1 < len(mates) else None

    @property
    def GetFirstSubFeature(self):
        return None

    def GetErrorCode2(self, flag):
        self.doc.log.append(("GetErrorCode2", self.Name))
        if self.doc.tuple_answers:
            return self.code, self.warning
        flag.value = self.warning
        return self.code

    def IsSuppressed2(self, configuration, names):
        self.doc.log.append(("IsSuppressed2", self.Name, configuration))
        return ((self.suppressed,),) if self.doc.tuple_answers else [self.suppressed]

    def SetSuppression2(self, action, configuration, names):
        self.doc.log.append(("SetSuppression2", self.Name, action, configuration, names))
        if self.doc.suppression_takes:
            self.suppressed = action == findings.FEATURE_SUPPRESS
        return True

    def Select2(self, append, mark):
        self.doc.log.append(("Select2", self.Name, append, mark))
        self.doc.selected.append(self)
        return True


class MateGroup:
    Name, GetTypeName2, GetNextFeature = "Mates", "MateGroup", None

    def __init__(self, doc):
        self.doc = doc

    @property
    def GetFirstSubFeature(self):
        return self.doc.mates[0] if self.doc.mates else None


class Origin:
    Name, GetTypeName2 = "Origin", "OriginProfileFeature"

    def __init__(self, doc):
        self.doc = doc

    @property
    def GetNextFeature(self):
        return self.doc.group

    @property
    def GetFirstSubFeature(self):
        return None


class AxisFeature:
    def __init__(self, component, name):
        self.component, self.Name = component, name

    def Select2(self, append, mark):
        doc = self.component.doc
        doc.log.append(("Select2", f"{self.Name}@{self.component.Name2}", append, mark))
        doc.selected.append(self)
        return True


class MatedComponent:
    def __init__(self, doc, name, status=2, as_method=False):
        self.doc, self.Name2, self.status, self.as_method = doc, name, status, as_method

    def Select4(self, append, data, mark):
        self.doc.log.append(("Select4", self.Name2, append, getattr(data, "Mark", None), mark))
        if self.doc.select_takes:
            self.doc.selected.append(self)
        return self.doc.select_takes

    def FeatureByName(self, name):
        return AxisFeature(self, name)

    @property
    def GetConstrainedStatus(self):
        return (lambda: self.status) if self.as_method else self.status


class MatedSelection:
    def __init__(self, doc):
        self.doc = doc

    @property
    def CreateSelectData(self):
        return SelectData()

    def GetSelectedObjectCount2(self, mark):
        return len(self.doc.selected)


class MatedDoc:
    GetType, GetTitle, GetPathName = swcom.DOC_ASSEMBLY, "R.SLDASM", W + "R.SLDASM"

    def __init__(self, with_group=True):
        self.log, self.selected, self.mates = [], [], []
        self.tuple_answers, self.suppression_takes, self.select_takes = False, True, True
        self.refuse, self.status, self.made = False, 1, 0
        self.components = {}
        self.group = MateGroup(self) if with_group else None
        self.SelectionManager = MatedSelection(self)

    @property
    def FirstFeature(self):
        return Origin(self)

    def ClearSelection2(self, everything):
        self.selected = []

    def AddMate5(self, *args):
        self.log.append(("AddMate5",) + tuple(args[:-1]))
        if self.refuse:
            return None
        self.made += 1
        mate = MateFeature(self, f"Mate{self.made}", "MateLock" if args[0] == findings.MATE_LOCK else "MateGearDim")
        self.mates.append(mate)
        args[-1].value = self.status
        return mate

    def GetComponentByName(self, name):
        self.log.append(("GetComponentByName", name))
        return self.components.get(name)

    def EditDelete(self):
        self.log.append(("EditDelete",))
        for feature in self.selected:
            if feature in self.mates:
                self.mates.remove(feature)
        return True


class MatedApp:
    def __init__(self, doc):
        self.ActiveDoc = doc

    def GetUserPreferenceToggle(self, which):
        return False

    def SetUserPreferenceToggle(self, which, value):
        pass


@pytest.fixture
def mated(monkeypatch):
    monkeypatch.setattr(swcom, "_out_long", Out)
    monkeypatch.setattr(swcom, "_out_bool", OutBool)
    monkeypatch.setattr(swcom, "_null_dispatch", lambda: None)
    monkeypatch.setattr(swcom.time, "sleep", lambda _seconds: None)
    doc = MatedDoc()
    session = swcom.Session(MatedApp(doc), (34, 0, 0), 1)
    session.begin_build()
    session._handles = {"gear2": {"component": MatedComponent(doc, "Gear_m1.5_N68-1")},
                        "gear3": {"component": MatedComponent(doc, "Gear_m1.5_N17-2")}}
    return session, doc


def test_a_lock_selects_the_anchor_then_the_follower_with_mark_one_and_is_made_named_and_kept(mated):
    session, doc = mated
    assert session.add_mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2") == ("G3 locked to G2", "")
    selects = [e for e in doc.log if e[0] == "Select4"]
    assert selects == [("Select4", "Gear_m1.5_N68-1", False, 1, False), ("Select4", "Gear_m1.5_N17-2", True, 1, False)]
    (made,) = [e for e in doc.log if e[0] == "AddMate5"]
    assert made == ("AddMate5", findings.MATE_LOCK, findings.MATE_ALIGN_CLOSEST, False, 0.0, 0.0, 0.0, 1, 1, 0.0,
                    0.0, 0.0, False, False, 0)
    assert [m.Name for m in doc.mates] == ["G3 locked to G2"]
    assert session.mate_status("G3 locked to G2") == findings.ADD_MATE_NO_ERROR
    assert session.mate_status("G1 meshes G2") is None                 # not made by this session
    assert session._handles["lock1"] == {"mate": "G3 locked to G2"}


def test_a_lock_made_over_defining_keeps_its_status_and_does_not_raise(mated):
    session, doc = mated
    doc.status = findings.ADD_MATE_OVER_DEFINED
    session.add_mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2")
    assert session.mate_status("G3 locked to G2") == findings.ADD_MATE_OVER_DEFINED


def test_a_lock_the_answer_comes_back_as_a_tuple_is_read_the_same_way(mated):
    session, doc = mated
    original = doc.AddMate5

    def as_tuple(*args):
        mate = original(*args)
        return mate, 5
    doc.AddMate5 = as_tuple
    session.add_mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2")
    assert session.mate_status("G3 locked to G2") == 5


def test_a_lock_solidworks_will_not_make_is_mate_refused(mated):
    session, doc = mated
    doc.refuse = True
    with pytest.raises(swcom.MateRefused) as raised:
        session.add_mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2")
    assert str(raised.value) == "AddMate5 would not make a lock mate between gear2 and gear3."


def test_a_component_that_will_not_select_for_a_lock_is_an_ordinary_refusal_not_mate_refused(mated):
    session, doc = mated
    doc.select_takes = False
    with pytest.raises(SolidWorksError) as raised:
        session.add_mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2")
    assert not isinstance(raised.value, swcom.MateRefused)
    assert str(raised.value).startswith("Gear_m1.5_N68-1 could not be selected for the lock mate G3 locked to G2 ")
    assert not any(e[0] == "AddMate5" for e in doc.log)


@pytest.mark.parametrize("name, value", [("COMPOUND_LOCK_ROUTE", None), ("COMPOUND_LOCK_ROUTE", "lock and axis"),
                                         ("LOCK_SELECT_ROUTE", None), ("MATE_LOCK", None), ("MATE_RENAME_ROUTE", None)])
def test_a_lock_without_its_findings_is_refused_before_anything_is_selected(mated, monkeypatch, name, value):
    session, doc = mated
    monkeypatch.setattr(findings, name, value, raising=False)
    with pytest.raises(SolidWorksError) as raised:
        session.add_mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2")
    assert f"(findings.{name} is {value!r}), so nothing is changed; run probe tier 8 first." in str(raised.value)
    assert doc.log == [] and doc.mates == []


def test_every_mate_is_read_in_tree_order_with_its_code_warning_and_suppression_and_folders_are_left_out(mated):
    session, doc = mated
    doc.mates = [MateFeature(doc, "G1 on S1 Axis"), MateFeature(doc, "My mates", "FtrFolder"),
                 MateFeature(doc, "G3 locked to G2", "MateLock", code=46, warning=True),
                 MateFeature(doc, "Angle1", "MatePlanarAngleDim", code=47, warning=False, suppressed=True)]
    wanted = [swcom.MateState("G1 on S1 Axis"), swcom.MateState("G3 locked to G2", 46, True, False),
              swcom.MateState("Angle1", 47, False, True)]
    assert session.mate_states() == wanted
    doc.tuple_answers = True
    assert session.mate_states() == wanted
    assert ("IsSuppressed2", "Angle1", findings.THIS_CONFIGURATION) in doc.log


def test_an_assembly_with_no_mate_group_has_no_mates(monkeypatch):
    monkeypatch.setattr(swcom, "_out_bool", OutBool)
    session = swcom.Session(MatedApp(MatedDoc(with_group=False)), (34, 0, 0), 1)
    assert session.mate_states() == []


def test_without_the_mate_group_route_mates_are_not_read(mated, monkeypatch):
    session, _doc = mated
    monkeypatch.setattr(findings, "MATE_FIND_ROUTE", None)
    with pytest.raises(SolidWorksError, match=r"\(findings.MATE_FIND_ROUTE is None\)"):
        session.mate_states()


@pytest.mark.parametrize("as_method", [False, True])
def test_a_components_constrained_status_is_read_as_a_property_or_called(mated, as_method):
    session, doc = mated
    session._handles["placed2"] = {"component": MatedComponent(doc, "Gear_m1.5_N68-1", 3, as_method)}
    assert session.constrained_status("placed2") == findings.COMPONENT_FULLY_DEFINED
    assert session.constrained_status("gear2") == findings.COMPONENT_UNDER_DEFINED


# -- W9a: the reads of the user's work (ISSUE-1-PLAN §2.1 item 2), read only


class UserComponent:
    def __init__(self, name, path, fixed=False, state=2):
        self.Name2, self.GetPathName, self.IsFixed, self.GetSuppression2 = name, path, fixed, state
        self.GetModelDoc2 = None


class TreeFeature:
    def __init__(self, log, name, code=0, warning=True, type_name="ICE", raises=False):
        self.log, self.Name, self.code, self.warning, self.GetTypeName2 = log, name, code, warning, type_name
        self.raises, self.next = raises, None

    def GetErrorCode2(self, flag):
        self.log.append(("GetErrorCode2", self.Name))
        if self.raises:
            raise RuntimeError("no answer")
        flag.value = self.warning
        return self.code

    @property
    def GetNextFeature(self):
        return self.next


class UserEntity:
    def __init__(self, component):
        self.ReferenceComponent = component


class UserSpecific:
    def __init__(self, kind, components):
        self.Type, self.entities = kind, [UserEntity(c) for c in components]
        self.GetMateEntityCount = len(self.entities)

    def MateEntity(self, index):
        return self.entities[index]


def test_components_lists_each_top_level_component_with_its_file_fixed_state_and_error_code(mated):
    session, doc = mated
    housing = UserComponent("Housing-1", W + "Housing.SLDPRT", fixed=True)
    sprocket = UserComponent("Sprocket-1", W + "Sprocket.SLDPRT", state=1)
    doc.GetComponents = lambda top_level: (housing, sprocket)
    features = {"Housing-1": TreeFeature(doc.log, "Housing-1", 0), "Sprocket-1": TreeFeature(doc.log, "Sprocket-1", 51)}
    doc.FeatureByName = lambda name: features.get(name)
    assert session.components() == [swcom.ComponentInfo("Housing-1", W + "Housing.SLDPRT", True, 2, 0),
                                    swcom.ComponentInfo("Sprocket-1", W + "Sprocket.SLDPRT", False, 1, 51)]
    doc.FeatureByName = lambda name: None
    assert [c.code for c in session.components()] == [swcom.UNREAD, swcom.UNREAD]
    assert not any(e[0].startswith(("SetSuppression2", "Select", "ForceRebuild")) for e in doc.log)


def test_mate_info_reads_the_type_and_each_entitys_component_the_assemblys_own_as_blank(mated):
    session, doc = mated
    mate = MateFeature(doc, "Lock3", "MateLock")
    mate.GetSpecificFeature2 = UserSpecific(findings.MATE_LOCK, [MatedComponent(doc, "Gear_m1.5_N17-1"),
                                                                 MatedComponent(doc, "Sub-1/Sprocket-1")])
    plane = MateFeature(doc, "Coincident7")
    plane.GetSpecificFeature2 = UserSpecific(0, [MatedComponent(doc, "Housing-1"), None])
    doc.mates = [mate, plane]
    session.find_mate("other1", "Lock3")
    session.find_mate("other2", "Coincident7")
    assert session.mate_info("other1") == swcom.MateInfo("Lock3", findings.MATE_LOCK,
                                                         ("Gear_m1.5_N17-1", "Sub-1/Sprocket-1"))
    assert session.mate_info("other2") == swcom.MateInfo("Coincident7", 0, ("Housing-1", ""))
    assert not any(e[0] in ("SetSuppression2", "Select2", "AddMate5") for e in doc.log)


def test_feature_states_walks_the_top_level_tree_with_each_error_code(mated):
    session, doc = mated
    walk = [TreeFeature(doc.log, "Origin", type_name="OriginProfileFeature"), TreeFeature(doc.log, "Bore"),
            TreeFeature(doc.log, "Keyway", 71, False), TreeFeature(doc.log, "Odd", raises=True)]
    for one, after in zip(walk, walk[1:]):
        one.next = after
    type(doc).FirstFeature = property(lambda self: walk[0])
    try:
        assert session.feature_states() == [
            swcom.FeatureState("Origin", "OriginProfileFeature"), swcom.FeatureState("Bore", "ICE"),
            swcom.FeatureState("Keyway", "ICE", 71, False), swcom.FeatureState("Odd", "ICE", swcom.UNREAD, True)]
    finally:
        type(doc).FirstFeature = property(lambda self: Origin(self))


def test_a_mate_is_found_by_its_name_and_kept_and_a_folder_of_that_name_is_not_a_mate(mated):
    session, doc = mated
    doc.mates = [MateFeature(doc, "G4 along S3", "FtrFolder"), MateFeature(doc, "G1 meshes G2", "MateGearDim")]
    assert session.find_mate("mate9", "G1 meshes G2") == "G1 meshes G2"
    assert session._handles["mate9"] == {"mate": "G1 meshes G2"}
    with pytest.raises(swcom.MateGone) as raised:
        session.find_mate("mate4", "G4 along S3")
    assert str(raised.value) == ('The mate "G4 along S3" is not in R.SLDASM any more: it was renamed or deleted in '
                                 "SolidWorks.")
    assert isinstance(raised.value, swcom.ComponentGone)


def test_a_kept_mate_is_suppressed_and_turned_back_on_by_set_suppression_and_read_back(mated):
    session, doc = mated
    doc.mates = [MateFeature(doc, "G3 locked to G2", "MateLock")]
    session.find_mate("lock", "G3 locked to G2")
    session.set_mate_suppressed("lock", True)
    assert doc.mates[0].suppressed
    session.set_mate_suppressed("lock", False)
    assert not doc.mates[0].suppressed
    assert [e for e in doc.log if e[0] == "SetSuppression2"] == [
        ("SetSuppression2", "G3 locked to G2", findings.FEATURE_SUPPRESS, findings.THIS_CONFIGURATION, None),
        ("SetSuppression2", "G3 locked to G2", findings.FEATURE_UNSUPPRESS, findings.THIS_CONFIGURATION, None)]
    assert not any(e[0].startswith("ForceRebuild") for e in doc.log)


def test_a_suppression_that_does_not_take_names_the_mate(mated):
    session, doc = mated
    doc.mates = [MateFeature(doc, "G3 locked to G2", "MateLock", suppressed=True)]
    doc.suppression_takes = False
    session.find_mate("lock", "G3 locked to G2")
    with pytest.raises(SolidWorksError) as raised:
        session.set_mate_suppressed("lock", False)
    assert str(raised.value) == ("SolidWorks would not turn the mate G3 locked to G2 back on in R.SLDASM: it still "
                                 "reads it suppressed; if it sits in a suppressed folder, unsuppress the folder in "
                                 "SolidWorks and press Update SolidWorks again.")


def test_a_mate_renamed_since_it_was_found_is_gone_when_it_is_suppressed(mated):
    session, doc = mated
    doc.mates = [MateFeature(doc, "G3 locked to G2", "MateLock")]
    session.find_mate("lock", "G3 locked to G2")
    doc.mates[0].Name = "Lock1"
    with pytest.raises(swcom.MateGone):
        session.set_mate_suppressed("lock", True)


def _ratio_world(session, doc):
    doc.mates = [MateFeature(doc, "G3 meshes G4", "MateGearDim")]
    doc.components = {n: MatedComponent(doc, n) for n in ("Gear_m1.5_N17-2", "Gear_m1.5_N51-1")}
    session._handles.update({"placed3": {"component": doc.components["Gear_m1.5_N17-2"]},
                             "placed4": {"component": doc.components["Gear_m1.5_N51-1"]}})
    session.find_mate("mesh2", "G3 meshes G4")


@pytest.mark.parametrize("route, sentence", [
    (None, "Changing a gear mate's ratio has not been settled on SolidWorks yet (findings.GEAR_MATE_RATIO_ROUTE is "
           "None), so G3 meshes G4 keeps its ratio; build the gearbox again for a new tooth count."),
    ("modify definition", "G3 meshes G4 is not given its new ratio through its definition: on SolidWorks 2024 that "
                          "leaves an assembly that cannot be closed (findings.MODIFIED_GEAR_MATE_CLOSES_ON_2024), so "
                          "Gear Generator never does it; build the gearbox again for a new tooth count."),
    ("guess", "findings.GEAR_MATE_RATIO_ROUTE is 'guess', which is not a way of changing a gear mate's ratio this "
              "code knows, so G3 meshes G4 keeps its ratio; run its probe again."),
])
def test_a_ratio_is_changed_only_by_the_remake_and_refused_otherwise_before_anything_is_touched(mated, monkeypatch,
                                                                                               route, sentence):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", route)
    with pytest.raises(SolidWorksError) as raised:
        session.set_gear_ratio("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    assert str(raised.value) == sentence
    assert [m.Name for m in doc.mates] == ["G3 meshes G4"] and not any(e[0] in ("EditDelete", "AddMate5")
                                                                       for e in doc.log)


def test_the_remake_deletes_the_gear_mate_makes_it_again_at_the_ratio_and_gives_it_its_old_name(mated, monkeypatch):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    session.set_gear_ratio("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    steps = [e[:2] for e in doc.log if e[0] in ("Select2", "EditDelete", "GetComponentByName", "AddMate5")]
    assert steps == [("Select2", "G3 meshes G4"), ("EditDelete",), ("GetComponentByName", "Gear_m1.5_N17-2"),
                     ("GetComponentByName", "Gear_m1.5_N51-1"), ("Select2", "Gear Axis@Gear_m1.5_N17-2"),
                     ("Select2", "Gear Axis@Gear_m1.5_N51-1"), ("AddMate5", findings.MATE_GEAR)]
    (made,) = [e for e in doc.log if e[0] == "AddMate5"]
    assert made[3] is findings.GEAR_MATE_FLIP and made[7:9] == (18.0, 50.0)      # numerator with the first selection
    assert [m.Name for m in doc.mates] == ["G3 meshes G4"]
    assert session.mate_status("G3 meshes G4") == findings.ADD_MATE_NO_ERROR
    assert session._handles["mesh2"] == {"mate": "G3 meshes G4"}
    assert not any(e[0].startswith("ForceRebuild") for e in doc.log)


def test_a_remake_solidworks_will_not_make_again_says_the_mate_was_deleted(mated, monkeypatch):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    doc.refuse = True
    with pytest.raises(swcom.MateRefused) as raised:
        session.set_gear_ratio("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    assert str(raised.value) == ("The open R.SLDASM has lost the gear mate G3 meshes G4: it was deleted to give it its "
                                 "new ratio, and SolidWorks would not make it again. The saved R.SLDASM still has it: "
                                 "close R.SLDASM in SolidWorks without saving to bring it back. AddMate5 would not make "
                                 "a gear mate between placed3:Gear Axis and placed4:Gear Axis.")


def test_a_remake_whose_selection_fails_is_an_ordinary_failure_not_mate_refused(mated, monkeypatch):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    doc.components["Gear_m1.5_N51-1"].FeatureByName = lambda name: None
    doc.Extension = type("NoSelect", (), {"SelectByID2": lambda self, *args: False})()
    with pytest.raises(SolidWorksError) as raised:
        session.set_gear_ratio("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    assert not isinstance(raised.value, swcom.MateRefused)          # an ordinary failure: Build is not greyed
    assert str(raised.value) == ("The open R.SLDASM has lost the gear mate G3 meshes G4: it was deleted to give it its "
                                 "new ratio, and making it again stopped. The saved R.SLDASM still has it: close "
                                 "R.SLDASM in SolidWorks without saving to bring it back. Gear Axis@Gear_m1.5_N51-1@R "
                                 "could not be selected for a mate.")


@pytest.mark.parametrize("error, said", [
    (swcom.ComError("AddMate5", RPC_FAILED), "SolidWorks did not complete AddMate5: The remote procedure call failed "
                                             "(RPC_S_CALL_FAILED). SolidWorks may have closed or crashed; the next "
                                             "press connects to it again."),
    (RuntimeError("the selection manager went away"), "It stopped on an unexpected RuntimeError: the selection "
                                                      "manager went away."),
])
def test_any_failure_after_the_delete_says_the_open_assembly_lost_the_gear_mate(mated, monkeypatch, error, said):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)

    def fails(*args):
        raise error
    doc.AddMate5 = fails
    with pytest.raises(SolidWorksError) as raised:
        session.set_gear_ratio("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    assert not isinstance(raised.value, swcom.MateRefused)
    assert str(raised.value) == ("The open R.SLDASM has lost the gear mate G3 meshes G4: it was deleted to give it its "
                                 "new ratio, and making it again stopped. The saved R.SLDASM still has it: close "
                                 f"R.SLDASM in SolidWorks without saving to bring it back. {said}")


def test_a_remake_solidworks_names_otherwise_says_the_open_assembly_lost_the_mate(mated, monkeypatch):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    monkeypatch.setattr(swcom.Session, "_rename", staticmethod(lambda feature, name: "G3 meshes G4 1"))
    with pytest.raises(SolidWorksError) as raised:
        session.set_gear_ratio("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    assert str(raised.value) == ("The open R.SLDASM has lost the gear mate G3 meshes G4 by that name: it was made again "
                                 "with its new ratio, and SolidWorks named it G3 meshes G4 1. The saved R.SLDASM still "
                                 "has it: close R.SLDASM in SolidWorks without saving to bring it back.")


def test_statuses_are_this_builds_only(mated):
    session, doc = mated
    session.add_mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2")
    session.begin_build()
    assert session.mate_status("G3 locked to G2") is None


@pytest.mark.parametrize("folder, sees, listed", [
    ("FtrFolder", True, ["Mystery1"]),
    (None, True, ["Folder1", "Mystery1", "Folder1___EndTag___"]),
    ("FtrFolder", None, ["Folder1", "Mystery1", "Folder1___EndTag___"]),
])
def test_what_in_the_mate_group_is_not_a_mate_is_named_when_asked_but_a_folders_two_entries(mated, monkeypatch,
                                                                                           folder, sees, listed):
    """Probe round P0c, mate_folders: a folder shows in the MateGroup walk as two "FtrFolder" entries around the mates
    it holds, which follow as ordinary siblings. With the finding, both are skipped and every mate is still read;
    without it they are listed as anything else that is not a mate is."""
    session, doc = mated
    monkeypatch.setattr(findings, "MATE_FOLDER_TYPE_NAME", folder)
    monkeypatch.setattr(findings, "MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER", sees)
    doc.mates = [MateFeature(doc, "G1 on S1 Axis"), MateFeature(doc, "Folder1", "FtrFolder"),
                 MateFeature(doc, "G1 meshes G2", "MateGearDim"), MateFeature(doc, "Mystery1", "SomethingElse"),
                 MateFeature(doc, "Folder1___EndTag___", "FtrFolder")]
    others = []
    assert [m.name for m in session.mate_states(others=others)] == ["G1 on S1 Axis", "G1 meshes G2"]
    assert others == listed
    assert session.find_mate("mesh1", "G1 meshes G2") == "G1 meshes G2"          # a mate inside the folder is found


def test_a_remake_without_the_delete_route_is_refused_before_the_mate_is_touched(mated, monkeypatch):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    monkeypatch.setattr(findings, "MATE_DELETE_ROUTE", "Select2 then DeleteSelection2(0)")
    with pytest.raises(SolidWorksError, match="findings.MATE_DELETE_ROUTE is 'Select2 then DeleteSelection2"):
        session.set_gear_ratio("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    assert [m.Name for m in doc.mates] == ["G3 meshes G4"] and not any(e[0] == "EditDelete" for e in doc.log)


def test_a_gear_mate_keeps_its_status_and_a_refused_one_is_mate_refused(mated):
    session, doc = mated
    session._handles["gear1"] = {"component": MatedComponent(doc, "Gear_m1.5_N17-1")}
    doc.status = findings.ADD_MATE_OVER_DEFINED
    assert session.add_mate("mesh1", "gear", "gear1:Gear Axis", "gear2:Gear Axis", name="G1 meshes G2",
                            ratio=(17.0, 68.0)) == ("G1 meshes G2", "")
    assert session.mate_status("G1 meshes G2") == findings.ADD_MATE_OVER_DEFINED      # kept, never raised on
    doc.refuse = True
    with pytest.raises(swcom.MateRefused, match="AddMate5 would not make a gear mate between gear1:Gear Axis and "):
        session.add_mate("mesh2", "gear", "gear1:Gear Axis", "gear2:Gear Axis", ratio=(17.0, 68.0))


def test_a_component_not_found_again_after_the_delete_says_the_open_assembly_lost_the_gear_mate(mated, monkeypatch):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    del doc.components["Gear_m1.5_N51-1"]
    with pytest.raises(SolidWorksError) as raised:
        session.set_gear_ratio("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    assert not isinstance(raised.value, swcom.MateRefused)
    assert str(raised.value) == ("The open R.SLDASM has lost the gear mate G3 meshes G4: it was deleted to give it its "
                                 "new ratio, and making it again stopped. The saved R.SLDASM still has it: close "
                                 "R.SLDASM in SolidWorks without saving to bring it back. Gear_m1.5_N51-1 could not be "
                                 "found again in R.SLDASM after the delete.")


class GearMateData:
    """IGearMateFeatureData as probe gear_mate_ratio read it: the counts the other way round from AddMate5."""

    def __init__(self, log, first, second, as_method=False):
        self.log, self.first, self.second, self.as_method = log, first, second, as_method

    @property
    def GearRatioNumerator(self):
        value = float(self.second)
        return (lambda: value) if self.as_method else value

    @property
    def GearRatioDenominator(self):
        value = float(self.first)
        return (lambda: value) if self.as_method else value

    def __getattr__(self, name):
        if name == "ModifyDefinition":
            self.log.append(("ModifyDefinition",))
        raise AttributeError(name)


@pytest.mark.parametrize("as_method", [False, True])
def test_a_gear_mates_ratio_is_read_from_its_definition_in_its_own_selection_order_and_never_modified(
        mated, monkeypatch, as_method):
    session, doc = mated
    monkeypatch.setattr(findings, "GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", True)
    mate = MateFeature(doc, "G1 meshes G2", "MateGearDim")
    mate.GetDefinition = GearMateData(doc.log, 17, 68, as_method)
    doc.mates = [mate]
    session.find_mate("mesh1", "G1 meshes G2")
    assert session.gear_mate_ratio("mesh1") == (17.0, 68.0)
    assert ("ModifyDefinition",) not in doc.log
    monkeypatch.setattr(findings, "GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", False)
    assert session.gear_mate_ratio("mesh1") == (68.0, 17.0)       # a version reading it the AddMate5 way round


def test_a_gear_mates_ratio_is_not_read_without_its_finding_or_its_definition(mated, monkeypatch):
    session, doc = mated
    mate = MateFeature(doc, "G1 meshes G2", "MateGearDim")
    mate.GetDefinition = None
    doc.mates = [mate]
    session.find_mate("mesh1", "G1 meshes G2")
    monkeypatch.setattr(findings, "GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", True)
    with pytest.raises(SolidWorksError, match="^SolidWorks gave no definition for the gear mate G1 meshes G2 in "
                                              "R.SLDASM, so its ratio cannot be read.$"):
        session.gear_mate_ratio("mesh1")
    monkeypatch.setattr(findings, "GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", None)
    with pytest.raises(SolidWorksError, match=r"GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND is None\), so nothing"):
        session.gear_mate_ratio("mesh1")



@pytest.mark.parametrize("state, resolved", [(2, True), (3, False), (1, False), (4, False)])
def test_a_components_resolved_state_is_read_by_the_settled_route(mated, monkeypatch, state, resolved):
    session, doc = mated
    monkeypatch.setattr(findings, swcom.RESOLVED_ROUTE_FINDING, "GetSuppression2", raising=False)
    monkeypatch.setattr(findings, swcom.RESOLVED_VALUES_FINDING, (2,), raising=False)
    component = session._handles["gear2"]["component"]
    component.GetSuppression2 = state
    assert session.component_resolved("gear2") is resolved


@pytest.mark.parametrize("route, values", [(None, (2,)), ("GetSomethingElse", (2,)), ("GetSuppression2", None)])
def test_a_resolved_read_not_settled_is_refused(mated, monkeypatch, route, values):
    session, _doc = mated
    monkeypatch.setattr(findings, swcom.RESOLVED_ROUTE_FINDING, route, raising=False)
    monkeypatch.setattr(findings, swcom.RESOLVED_VALUES_FINDING, values, raising=False)
    with pytest.raises(SolidWorksError, match="Reading whether a component is fully resolved has not been settled"):
        session.component_resolved("gear2")


def test_find_component_leaves_a_lightweight_component_to_its_caller_when_asked(com, monkeypatch):
    monkeypatch.setattr(findings, "COMPONENT_FIND_ROUTE", "GetComponentByName")
    doc = com.opened(W + "R.SLDASM", doc_type=2)
    doc.components.append(Component("gear2-1", state=1))
    session = _session(com)
    session.begin_build()
    with pytest.raises(SolidWorksError, match="is loaded lightweight in R.SLDASM"):
        session.find_component("g", "gear2-1")
    assert session.find_component("g", "gear2-1", lightweight_ok=True) == "gear2-1"
    doc.components[0].GetSuppression2 = swcom.COMPONENT_SUPPRESSED
    with pytest.raises(SolidWorksError, match="is suppressed in R.SLDASM"):
        session.find_component("g", "gear2-1", lightweight_ok=True)


# -- which way a gear mate turns (probe ring_mate_sense): Reverse and the two entity directions, read only


class SenseData:
    def __init__(self, log, reverse):
        self.log, self.Reverse = log, reverse

    def __getattr__(self, name):
        if name in ("ModifyDefinition", "AccessSelections"):
            self.log.append((name,))
        raise AttributeError(name)


class MateEntity:
    def __init__(self, direction):
        self.EntityParams = (0.01, 0.02, 0.03) + tuple(direction) + (0.0, 0.0)


class SpecificMate:
    def __init__(self, directions):
        self.entities = [MateEntity(d) for d in directions]
        self.GetMateEntityCount = len(self.entities)

    def MateEntity(self, index):
        return self.entities[index]


def _sense_world(session, doc, reverse, directions):
    mate = MateFeature(doc, "G5 meshes G6", "MateGearDim")
    mate.GetDefinition = SenseData(doc.log, reverse)
    mate.GetSpecificFeature2 = SpecificMate(directions)
    doc.mates = [mate]
    session.find_mate("mesh", "G5 meshes G6")


Z_UP, Z_DOWN = (0, 0, 1.0), (0, 0, -1.0)


# W6's form (W6-INTERFACES.md): the two gears' axes as placed and whether the mesh turns them the same way (k > 0)
# take the place of W5's ``internal``; the answer carries each entity's sense instead of "parallel". The W5 cases,
# each as W5 read it: a ring mesh on opposite shafts turns its gears opposite ways about their own axes (k < 0).
@pytest.mark.parametrize("reverse, directions, axes, same_sense, right, taus", [
    (True, (Z_UP, Z_DOWN), (Z_UP, Z_DOWN), False, False, (1, 1)),    # the Risky ring pair on 2026: Reverse True
    (False, (Z_UP, Z_DOWN), (Z_UP, Z_DOWN), False, True, (1, 1)),    # the same pair on 2024: Reverse False
    (True, (Z_UP, Z_UP), (Z_UP, Z_UP), True, True, (1, 1)),          # a ring on same-sense shafts
    (False, (Z_UP, Z_DOWN), (Z_UP, Z_DOWN), True, False, (1, 1)),    # an outside pair on opposite shafts (k > 0)
    (True, (Z_UP, Z_DOWN), (Z_UP, Z_DOWN), True, True, (1, 1)),
    (True, (Z_DOWN, Z_UP), (Z_UP, Z_UP), True, False, (-1, 1)),      # an entity against its gear's axis
])
def test_a_gear_mates_sense_is_read_back_by_reverse_and_its_entity_directions(mated, reverse, directions, axes,
                                                                              same_sense, right, taus):
    session, doc = mated
    _sense_world(session, doc, reverse, directions)
    assert session.gear_mate_sense("mesh", same_sense, axes) == (right, taus)
    assert ("ModifyDefinition",) not in doc.log and ("AccessSelections",) not in doc.log


X_ON = (1.0, 0.0, 0.0)


@pytest.fixture
def turned_read(monkeypatch):
    """Tier 9's findings as committed (11ee1e2) and the skew range the probe agent adds, pinned here."""
    for name, value in (("TURNED_GEAR_MATE_SENSE_READ_BACK", "entity senses"),
                        ("TURNED_GEAR_MATE_SENSE_ANGLES", (30.0, 150.0)),
                        ("TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", (60.0, 120.0))):
        monkeypatch.setattr(findings, name, value, raising=False)


def _turned_world(session, doc, reverse, directions, points=((0.0, 0.0, 0.06), (0.0, 0.0, 0.06))):
    """A gear mate whose two entities are the lines through ``points`` (metres) along ``directions``."""
    _sense_world(session, doc, reverse, directions)
    for entity, point in zip(doc.mates[0].GetSpecificFeature2.entities, points):
        entity.EntityParams = tuple(point) + tuple(entity.EntityParams[3:6]) + (0.0, 0.0)


def test_a_gear_mate_on_axes_that_meet_is_read_by_rule_h(mated, turned_read):
    session, doc = mated
    _turned_world(session, doc, True, (Z_UP, X_ON))
    # Fixture A's bevel mesh turns its gears opposite ways about their own axes (k < 0): Reverse True reads wrong.
    assert session.gear_mate_sense("mesh", False, (Z_UP, X_ON)) == (False, (1, 1))
    assert session.gear_mate_sense("mesh", False, (X_ON, Z_UP)) == (False, (1, 1))     # entities in either order
    _turned_world(session, doc, False, (Z_UP, X_ON))
    assert session.gear_mate_sense("mesh", False, (Z_UP, X_ON))[0] is True


@pytest.mark.parametrize("name, meet, sentence", [
    ("TURNED_GEAR_MATE_SENSE_READ_BACK", True,
     "The gear mate G5 meshes G6 in R.SLDASM joins gears on shafts that meet at an angle, and which way such a gear "
     "mate turns cannot be told on SolidWorks yet (findings.TURNED_GEAR_MATE_SENSE_READ_BACK is None), so which way "
     "it turns is not read."),
    ("TURNED_GEAR_MATE_SENSE_ANGLES", True,
     "The gear mate G5 meshes G6 in R.SLDASM joins gears on shafts that meet at an angle, and which way such a gear "
     "mate turns cannot be told on SolidWorks yet (findings.TURNED_GEAR_MATE_SENSE_ANGLES is None), so which way it "
     "turns is not read."),
    ("TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", False,
     "The gear mate G5 meshes G6 in R.SLDASM joins gears on shafts that pass each other at an angle, and which way "
     "such a gear mate turns cannot be told on SolidWorks yet (findings.TURNED_GEAR_MATE_SENSE_ANGLES_SKEW is None), "
     "so which way it turns is not read."),
])
def test_a_turned_gear_mate_is_not_read_while_its_finding_is_missing(mated, turned_read, monkeypatch, name, meet,
                                                                     sentence):
    session, doc = mated
    _turned_world(session, doc, True, (Z_UP, X_ON))
    monkeypatch.setattr(findings, name, None, raising=False)
    with pytest.raises(SolidWorksError) as raised:
        session.gear_mate_sense("mesh", False, (Z_UP, X_ON), meet=meet)
    assert str(raised.value) == sentence


def test_the_angle_a_turned_gear_mate_is_read_at_is_the_range_for_its_class(mated, turned_read):
    session, doc = mated
    tipped = (math.sin(math.radians(135.0)), 0.0, math.cos(math.radians(135.0)))       # 135° from +Z
    _turned_world(session, doc, False, (Z_UP, tipped))
    assert session.gear_mate_sense("mesh", False, (Z_UP, tipped), meet=True)[0] is True   # 135° meeting: inside
    with pytest.raises(SolidWorksError) as raised:
        session.gear_mate_sense("mesh", False, (Z_UP, tipped), meet=False)
    assert str(raised.value) == ("The gear mate G5 meshes G6 in R.SLDASM joins gears on shafts that pass each other at "
                                 "135°, outside the 60°–120° the probes showed such a gear mate turning right at "
                                 "(findings.TURNED_GEAR_MATE_SENSE_ANGLES_SKEW), so which way it turns is not read.")
    steep = (math.sin(math.radians(165.0)), 0.0, math.cos(math.radians(165.0)))
    _turned_world(session, doc, False, (Z_UP, steep))
    with pytest.raises(SolidWorksError, match="at 165°, outside the 30°–150°"):
        session.gear_mate_sense("mesh", False, (Z_UP, steep), meet=True)
    slight = (math.sin(math.radians(5.0)), 0.0, math.cos(math.radians(5.0)))        # W5's 0.99 called this parallel
    _turned_world(session, doc, False, (Z_UP, slight))
    with pytest.raises(SolidWorksError, match="at 5°, outside the 30°–150°"):
        session.gear_mate_sense("mesh", False, (Z_UP, slight), meet=True)


def test_without_the_callers_word_the_class_is_read_from_the_entities_lines(mated, turned_read):
    session, doc = mated
    tipped = (math.sin(math.radians(135.0)), 0.0, math.cos(math.radians(135.0)))
    _turned_world(session, doc, False, (Z_UP, tipped))                                   # one point: they meet
    assert session.gear_mate_sense("mesh", False, (Z_UP, tipped))[0] is True
    _turned_world(session, doc, False, (Z_UP, tipped), points=((0, 0, 0), (0, 0.03, 0)))    # 30 mm apart: skew
    with pytest.raises(SolidWorksError, match="shafts that pass each other at 135°"):
        session.gear_mate_sense("mesh", False, (Z_UP, tipped))


def test_a_turned_mate_whose_entity_lies_along_neither_gear_is_refused_as_unreadable(mated, turned_read):
    session, doc = mated
    _turned_world(session, doc, False, (Z_UP, (0.0, 1.0, 0.0)))
    with pytest.raises(swcom.SenseUnreadable) as raised:
        session.gear_mate_sense("mesh", False, (Z_UP, X_ON))
    assert raised.value.axes == (Z_UP, X_ON) and "nothing is guessed" in str(raised.value)


@pytest.mark.parametrize("name, value", [("GEAR_MATE_SENSE_READ_BACK", None), ("GEAR_MATE_SENSE_READ_BACK", "guess"),
                                         ("GEAR_MATE_READ_BACK_TELLS_SENSE", None)])
def test_a_gear_mates_sense_is_not_read_by_a_route_this_code_does_not_know(mated, monkeypatch, name, value):
    session, doc = mated
    _sense_world(session, doc, True, ((0, 0, 1.0), (0, 0, 1.0)))
    monkeypatch.setattr(findings, name, value)
    with pytest.raises(SolidWorksError, match="Reading which way a gear mate turns has not been settled"):
        session.gear_mate_sense("mesh", True, (Z_UP, Z_UP))


def test_a_gear_mate_without_two_entities_is_not_judged(mated):
    session, doc = mated
    _sense_world(session, doc, True, ((0, 0, 1.0),))
    with pytest.raises(SolidWorksError, match="did not say how it holds its two gear axes"):
        session.gear_mate_sense("mesh", True, (Z_UP, Z_UP))


def test_a_gear_mate_is_made_again_with_the_flip_asked(mated, monkeypatch):
    session, doc = mated
    _ratio_world(session, doc)
    monkeypatch.setattr(findings, "GEAR_MATE_CHECK_AND_REMAKE_HOLDS", True)
    session.remake_gear_mate("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (17.0, 51.0), True)
    (made,) = [e for e in doc.log if e[0] == "AddMate5"]
    assert made[1] == findings.MATE_GEAR and made[3] is True and made[7:9] == (17.0, 51.0)
    assert [m.Name for m in doc.mates] == ["G3 meshes G4"]
    monkeypatch.setattr(findings, "GEAR_MATE_CHECK_AND_REMAKE_HOLDS", None)
    with pytest.raises(SolidWorksError, match=r"GEAR_MATE_CHECK_AND_REMAKE_HOLDS is None\), so nothing is changed"):
        session.remake_gear_mate("mesh2", "placed3:Gear Axis", "placed4:Gear Axis", (17.0, 51.0), False)


@pytest.mark.parametrize("directions, sentence", [
    (((0, 0, 0.0), (0, 0, 1.0)), "The gear mate G5 meshes G6 in R.SLDASM holds a gear axis with no direction"),
    (((0, 0, 1.0), (0, 0.5, 0.5)), "SolidWorks reads the axes of the gear mate G5 meshes G6 in R.SLDASM as pointing "
                                   "(0, 0.707, 0.707), which is not along either gear's axis ((0, 0, 1) or (0, 0, "
                                   "1)), so the mate does not hold the axes the gears were placed on"),
    (((1.0, 0, 0), (0, 0, 1.0)), "SolidWorks reads the axes of the gear mate G5 meshes G6 in R.SLDASM as pointing "
                                 "(1, 0, 0), which is not along either gear's axis"),
])
def test_a_gear_mates_entity_directions_that_are_not_along_the_gears_are_not_judged(mated, directions, sentence):
    session, doc = mated
    _sense_world(session, doc, True, directions)
    with pytest.raises(SolidWorksError) as raised:
        session.gear_mate_sense("mesh", True, (Z_UP, Z_UP))
    assert str(raised.value).startswith(sentence)


def test_entity_directions_of_any_length_along_one_line_are_judged(mated):
    session, doc = mated
    _sense_world(session, doc, False, ((0, 0, 3.0), (0, 0.001, -0.5)))
    assert session.gear_mate_sense("mesh", True, (Z_UP, Z_UP)) == (True, (1, -1))


# -- W6: whether two turned axes meet, and the angles tier 9 covered for each class (W6-INTERFACES §7.12, §7.13)

def test_the_meet_tolerance_is_the_checks_centre_tolerance_and_the_family_rule_is_planning_s():
    from gear_generator.workbook import checks, geometry
    assert swcom.MEET_TOLERANCE == checks.CENTRE_TOLERANCE
    assert swcom.PARALLEL_TOLERANCE == geometry.FAMILY_TOLERANCE


def test_axes_that_meet_and_axes_that_pass_each_other_are_told_from_the_lines():
    # Fixture A's bevel pair: G1 on S1 (X+) with its apex at (0, 0, 60), G2 on S2 (Z+) with its apex there too.
    assert swcom.lines_meet((0.0, 0.0, 60.0), (1, 0, 0), (0.0, 0.0, 60.0), (0, 0, 1))
    assert swcom.lines_meet((0.0, 0.0, 60.0), (1, 0, 0), (0.0, 0.0, 0.0), (0, 0, 1))      # any point on each line
    # Fixture B's crossed pair: S1 the Z axis, S2 along X at y 84.852814, z 8.
    assert not swcom.lines_meet((0.0, 0.0, 2.0), (0, 0, 1), (-8.0, 84.852814, 8.0), (1, 0, 0))
    # 0.005 mm apart still meet (the checks pass a bevel pair's apexes that close); 0.006 do not.
    assert swcom.lines_meet((0, 0, 0), (1, 0, 0), (0, 0.005, 0), (0, 0, 1))
    assert not swcom.lines_meet((0, 0, 0), (1, 0, 0), (0, 0.006, 0), (0, 0, 1))
    # A slant: fixture B's bevel pair at 120°, the apexes together at (-110, 84.852814, 8).
    apex = (-110.0, 84.852814, 8.0)
    assert swcom.lines_meet(apex, (1, 0, 0), apex, (-0.5, 0.8660254037844386, 0.0))


def test_parallel_axes_are_refused_by_the_meet_test_not_answered():
    for b in ((0, 0, 1), (0, 0, -2)):
        with pytest.raises(SolidWorksError) as raised:
            swcom.lines_meet((0, 0, 0), (0, 0, 1), (30, 0, 0), b)
        assert "of one family" in str(raised.value) and str(raised.value).endswith("a fault in Gear Generator.")
    with pytest.raises(SolidWorksError):
        swcom.lines_meet((0, 0, 0), (0, 0, 0), (30, 0, 0), (1, 0, 0))


def test_axes_of_one_family_are_parallel_by_planning_s_rule_and_any_other_pair_is_turned():
    assert swcom.axes_parallel((0, 0, 1), (0, 0, -1)) and swcom.axes_parallel((0, 3, 0), (0, 1, 0))
    assert not swcom.axes_parallel((0, 0, 1), (0.0, 0.05, 0.99875))       # 2.9°: W5's 0.99 would call it parallel
    assert not swcom.axes_parallel((1, 0, 0), (0, 0, 1))


def test_the_turned_angles_are_read_per_class(monkeypatch):
    monkeypatch.setattr(swcom.findings, "TURNED_GEAR_MATE_SENSE_ANGLES", (30.0, 150.0), raising=False)
    monkeypatch.setattr(swcom.findings, "TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", (60.0, 120.0), raising=False)
    assert swcom.turned_angles(True) == (30.0, 150.0) and swcom.turned_angles(False) == (60.0, 120.0)
    for bad in (None, (150.0, 30.0), (30.0,), ("x", 2), (10.0, 190.0), (float("nan"), 90.0)):
        monkeypatch.setattr(swcom.findings, "TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", bad, raising=False)
        assert swcom.turned_angles(False) is None
    assert swcom.turned_angles(True) == (30.0, 150.0)
    monkeypatch.delattr(swcom.findings, "TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", raising=False)
    assert swcom.turned_angles(False) is None


# -- W6: a slanted shaft's axis on a one-line 3D sketch (line_axis), and any axis read back (axis_line)

class AxisParams:
    def __init__(self, a, b):
        self.GetRefAxisParams = tuple(v / 1000.0 for v in tuple(a) + tuple(b))       # two points, metres


class Line3D:
    def __init__(self, name):
        self.GetName = name


class Sketch3DManager:
    """An ISketchManager with only the members the real one has that line_axis may use (W6's first full build:
    SolidWorks 2026 refused ``SketchManager.Insert3DSketch2`` with an AttributeError; the manager's member is
    ``Insert3DSketch``, the document's ``Insert3DSketch2``). Anything else raises AttributeError, as late binding
    did, so a call on the wrong owner fails here. The line is named "Line7", so no "Line1" can be assumed."""

    __slots__ = ("doc", "open", "line", "AddToDB", "DisplayWhenAdded")

    def __init__(self, doc):
        self.doc, self.open, self.line = doc, False, Line3D("Line7")

    def Insert3DSketch(self, rebuild):
        self.doc.app.log.append(("Insert3DSketch", rebuild))
        if self.open:
            self.doc.features.append(Feature(self.doc, "3DSketch1", "3DProfileFeature"))
        self.open = not self.open

    @property
    def ActiveSketch(self):
        return object() if self.open else None

    def CreateLine(self, *coordinates):
        self.doc.app.log.append(("CreateLine",) + tuple(round(c, 9) for c in coordinates))
        self.doc.ends = (tuple(c * 1000.0 for c in coordinates[:3]), tuple(c * 1000.0 for c in coordinates[3:]))
        return self.line


class SegmentExtension(Extension):
    def SelectByID2(self, name, kind, x, y, z, append, mark, callout, option):
        self.doc.app.log.append(("SelectByID2", name, kind, append, mark))
        if kind == "EXTSKETCHSEGMENT" and name == "Line7@S3 Line":
            self.doc.selected.append(name)
            return True
        return False


def _line_doc(com, read=None):
    """A layout part whose 3D sketch and axis behave as the macro database and tier 9 say; ``read`` overrides where
    the made axis is read back (two points, mm)."""
    doc = com.opened(W + "Part1.SLDPRT")
    doc.SketchManager, doc.Extension = Sketch3DManager(doc), SegmentExtension(doc)

    def insert_axis(auto):
        com.log.append(("InsertAxis2", tuple(doc.selected)))
        if doc.selected != ["Line7@S3 Line"]:
            return False
        doc.features.append(Feature(doc, "Axis1", "RefAxis", specific=AxisParams(*(read or doc.ends))))
        return True

    doc.InsertAxis2 = insert_axis
    session = _session(com)
    session.begin_build()
    return session, doc


SLANT_POINT, SLANT_DIRECTION = (-110.0, 84.852814, 8.0), (-0.5, 0.8660254037844386, 0.0)


def test_a_slanted_axis_is_drawn_in_a_3d_sketch_made_on_its_line_named_and_read_back(com):
    session, doc = _line_doc(com)
    assert session.line_axis("line3", "S3 Axis", SLANT_POINT, SLANT_DIRECTION, 100.0) == "S3 Axis"
    assert _calls(com, "Insert3DSketch") == [("Insert3DSketch", True), ("Insert3DSketch", True)]
    assert not hasattr(doc, "Insert3DSketch2") and not hasattr(doc.SketchManager, "Insert3DSketch2")
    (line,) = _calls(com, "CreateLine")
    end = tuple(SLANT_POINT[i] + 100.0 * SLANT_DIRECTION[i] for i in range(3))
    assert line[1:] == tuple(round(v / 1000.0, 9) for v in SLANT_POINT + end)          # metres, three per end
    assert ("SelectByID2", "Line7@S3 Line", "EXTSKETCHSEGMENT", False, 0) in com.log
    assert [f.Name for f in doc.features[-2:]] == ["S3 Line", "S3 Axis"] and session._handles["line3"] == "S3 Axis"
    point, direction = session.axis_line("read3", "S3 Axis")
    assert point == pytest.approx(SLANT_POINT) and direction == pytest.approx(SLANT_DIRECTION)


def test_an_axis_solidworks_made_off_its_line_is_refused(com):
    session, _ = _line_doc(com, read=((-110.0, 84.852814, 8.5), (-160.0, 171.455354, 8.5)))
    with pytest.raises(SolidWorksError) as raised:
        session.line_axis("line3", "S3 Axis", SLANT_POINT, SLANT_DIRECTION, 100.0)
    assert str(raised.value).startswith("SolidWorks made the axis S3 Axis 0.5 mm off its line") and \
        str(raised.value).endswith("so the shaft would not be where the workbook puts it.")


class NoLineManager(Sketch3DManager):
    __slots__ = ()

    def CreateLine(self, *coordinates):
        return None


def test_the_3d_sketch_is_closed_even_when_its_line_is_not_drawn(com):
    session, doc = _line_doc(com)
    doc.SketchManager = NoLineManager(doc)
    with pytest.raises(SolidWorksError) as raised:
        session.line_axis("line3", "S3 Axis", SLANT_POINT, SLANT_DIRECTION, 100.0)
    assert str(raised.value) == ("SolidWorks would not draw the line of the axis of S3 in its 3D sketch, so the "
                                 "slanted shaft S3 is not laid out.")
    assert len(_calls(com, "Insert3DSketch")) == 2 and not doc.SketchManager.open


class OldManager:
    """A sketch manager without ``Insert3DSketch``, as the wrong owner was without the member asked of it."""

    def __init__(self, doc):
        self.doc = doc


def test_a_3d_sketch_that_will_not_open_is_a_sentence_and_nothing_is_closed(com):
    session, doc = _line_doc(com)
    doc.SketchManager = OldManager(doc)
    with pytest.raises(SolidWorksError) as raised:
        session.line_axis("line3", "S3 Axis", SLANT_POINT, SLANT_DIRECTION, 100.0)
    assert str(raised.value) == ("SolidWorks would not open a 3D sketch for the axis of S3, so the slanted shaft S3 "
                                 "is not laid out.")


def test_an_axis_solidworks_would_not_make_on_the_line_is_a_sentence(com):
    session, doc = _line_doc(com)
    doc.InsertAxis2 = lambda auto: False
    with pytest.raises(SolidWorksError) as raised:
        session.line_axis("line3", "S3 Axis", SLANT_POINT, SLANT_DIRECTION, 100.0)
    assert str(raised.value) == ("SolidWorks would not make the axis of S3 on its line, so the slanted shaft S3 is "
                                 "not laid out.")


def test_a_line_axis_with_no_direction_is_a_fault_and_nothing_is_drawn(com):
    session, _ = _line_doc(com)
    with pytest.raises(SolidWorksError, match="no direction or no length"):
        session.line_axis("line3", "S3 Axis", SLANT_POINT, (0.0, 0.0, 0.0), 100.0)
    assert com.log == []


def test_axis_line_refuses_a_feature_that_is_not_an_axis(com):
    session, _ = _line_doc(com)
    with pytest.raises(SolidWorksError, match="Top Plane in Part1.SLDPRT is not an axis"):
        session.axis_line("read", "Top Plane")


class UnreadManager(Sketch3DManager):
    """Opens the sketch, then will not say so: ActiveSketch raises while it is open."""
    __slots__ = ()

    @property
    def ActiveSketch(self):
        if self.open:
            raise SolidWorksError("ActiveSketch failed.")
        return None


class StuckManager(Sketch3DManager):
    """Opens the sketch and draws, then refuses to close it."""
    __slots__ = ()

    def Insert3DSketch(self, rebuild):
        if self.open:
            self.doc.app.log.append(("Insert3DSketch", rebuild))
            raise SolidWorksError("Insert3DSketch failed.")
        Sketch3DManager.Insert3DSketch(self, rebuild)


def test_a_sketch_opened_whose_read_fails_is_counted_open_and_closed(com):
    """The open call returned, so the sketch counts as open even though the read of it failed: it is drawn in and
    closed, never left open."""
    session, doc = _line_doc(com)
    doc.SketchManager = UnreadManager(doc)
    assert session.line_axis("line3", "S3 Axis", SLANT_POINT, SLANT_DIRECTION, 100.0) == "S3 Axis"
    assert len(_calls(com, "Insert3DSketch")) == 2 and not doc.SketchManager.open


class UnreadNoLineManager(UnreadManager):
    __slots__ = ()

    def CreateLine(self, *coordinates):
        return None


def test_a_sketch_opened_whose_read_fails_is_closed_when_the_line_fails(com):
    session, doc = _line_doc(com)
    doc.SketchManager = UnreadNoLineManager(doc)
    with pytest.raises(SolidWorksError, match="would not draw the line of the axis of S3"):
        session.line_axis("line3", "S3 Axis", SLANT_POINT, SLANT_DIRECTION, 100.0)
    assert len(_calls(com, "Insert3DSketch")) == 2 and not doc.SketchManager.open


def test_the_flags_are_restored_even_when_the_sketch_will_not_close(com):
    session, doc = _line_doc(com)
    doc.SketchManager = StuckManager(doc)
    with pytest.raises(SolidWorksError):
        session.line_axis("line3", "S3 Axis", SLANT_POINT, SLANT_DIRECTION, 100.0)
    assert doc.SketchManager.AddToDB is False and doc.SketchManager.DisplayWhenAdded is True


# -- W8: an assembly's configurations, and the handle rule (W8-PLAN §1.8, §4.2; W8-SPIKE; W8-INTERFACES §9.4) -------
#
# A COM-level fake of one assembly with configurations. Each mock is slotted and has only the members the real object
# has that the Session uses, so a call on the wrong owner (the line-axis lesson) fails as AttributeError. A component
# handle belongs to the epoch it was handed out in: AddConfiguration2 and ShowConfiguration2 start a new one, and any
# member read through an older handle raises StaleHandle (SolidWorks answers Transform2 None and IsFixed False there,
# silently; the fake makes that loud).

CONFIGURATION_FINDING_VALUES = dict(swcom.CONFIGURATION_FINDINGS)
SERVER_FAULT = com_error(-2147417851, "The server threw an exception.", None, None)     # 0x80010105, the spike's
EYE16 = (1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 0.0, 0.0, 0.0, 1.0, 0, 0, 0)


class StaleHandle(AssertionError):
    """A component handle used after AddConfiguration2 or ShowConfiguration2 without being fetched again."""


class _PartState:
    """What one component is in every configuration (shared by every handle to it)."""

    def __init__(self, name, path, fixed=False):
        self.name, self.path = name, path
        self.fixed = {"Default": fixed}
        self.frames = {"Default": EYE16}


class ConfigComponent:
    """``IComponent2``, handed out in one epoch of its assembly."""
    __slots__ = ("_doc", "_born", "_state")

    def __init__(self, doc, state):
        self._doc, self._born, self._state = doc, doc.epoch, state

    def _live(self):
        if self._born != self._doc.epoch:
            raise StaleHandle(f"{self._state.name} was used through a handle held across a configuration change")
        return self._state

    @property
    def Name2(self):
        return self._live().name

    @property
    def IsFixed(self):
        return self._live().fixed[self._doc.active]

    @property
    def Transform2(self):
        return Transform(self._live().frames[self._doc.active])

    @Transform2.setter
    def Transform2(self, transform):
        self._live().frames[self._doc.active] = tuple(transform.ArrayData)
        self._doc.log.append(("Transform2 put", self._state.name, self._doc.active))

    @property
    def GetModelDoc2(self):
        self._live()
        return None                                  # as a component with no model loaded: its own path is read

    @property
    def GetPathName(self):
        return self._live().path

    @property
    def GetSuppression2(self):
        self._live()
        return 2

    @property
    def GetConstrainedStatus(self):
        self._live()
        return 2

    def Select4(self, append, data, mark):
        self._doc.log.append(("Select4", self._live().name, append))
        self._doc.selected.append(self._state.name)
        return True

    def FeatureByName(self, name):
        self._live()
        raise AssertionError("a feature of a component is selected by its held names after a configuration change")


class ConfigDimension:
    """``IDimension``: a value per configuration, an unset one reading 0 (the spike)."""
    __slots__ = ("_doc", "values")

    def __init__(self, doc, values):
        self._doc, self.values = doc, values

    def SetSystemValue3(self, value_m, which, names):
        self._doc.log.append(("SetSystemValue3", value_m, which, tuple(names)))
        if self._doc.set_answer == 0 and not self._doc.set_ignored:
            for name in names:
                self.values[name] = value_m
        return self._doc.set_answer

    def GetSystemValue3(self, which, names):
        self._doc.log.append(("GetSystemValue3", which, tuple(names)))
        return tuple(self.values.get(name, 0.0) for name in names)[:-1 if self._doc.short_answers else None]


class ConfigDisplayDimension:
    """``IDisplayDimension``."""
    __slots__ = ("_dimension",)

    def __init__(self, dimension):
        self._dimension = dimension

    def GetDimension2(self, which):
        """``IDisplayDimension.GetDimension2(0)``, as the probes reached a dimension: the only member here."""
        assert which == 0
        return self._dimension


class ConfigMate:
    """A mate ``IFeature`` in the MateGroup, its flag per configuration, a distance mate with its D1."""
    __slots__ = ("_doc", "Name", "GetTypeName2", "flags", "_dimension")

    def __init__(self, doc, name, type_name="MateGearDim", values=None):
        self._doc, self.Name, self.GetTypeName2 = doc, name, type_name
        self.flags = {c: False for c in doc.configs}
        self._dimension = None if values is None else ConfigDimension(doc, values)

    @property
    def GetNextSubFeature(self):
        mates = self._doc.mates
        index = mates.index(self)
        return mates[index + 1] if index + 1 < len(mates) else None

    @property
    def GetFirstSubFeature(self):
        return None

    @property
    def GetFirstDisplayDimension(self):
        return None if self._dimension is None else ConfigDisplayDimension(self._dimension)

    def IsSuppressed2(self, which, names):
        # As SolidWorks 2026 answered (probe/results/w8-configuration-order-20261115-092100.txt): one flag per name
        # asked, but in the document's configuration order (GetConfigurationNames), whatever order they are passed in.
        self._doc.log.append(("IsSuppressed2", self.Name, which, tuple(names)))
        asked = set(names)
        flags = tuple(self._doc.flag_answers.get(c, self.flags[c]) for c in self._doc.configs
                      if c in asked)[:-1 if self._doc.short_answers else None]
        return (flags,) if self._doc.wrapped_flags else flags

    def SetSuppression2(self, action, which, names):
        self._doc.log.append(("SetSuppression2", self.Name, action, which, tuple(names)))
        behaviour = self._doc.suppression
        if behaviour == "ignored":
            return False
        for name in names:
            self.flags[name] = action == findings.FEATURE_SUPPRESS
        if behaviour == "raises and takes":
            raise SERVER_FAULT
        if behaviour == "connection lost":
            raise RPC_FAILED
        return True


class ConfigMateGroup:
    __slots__ = ("_doc",)
    Name, GetTypeName2, GetNextFeature = "Mates", "MateGroup", None

    def __init__(self, doc):
        self._doc = doc

    @property
    def GetFirstSubFeature(self):
        return self._doc.mates[0] if self._doc.mates else None


class ConfigOrigin:
    __slots__ = ("_doc",)
    Name, GetTypeName2 = "Origin", "OriginProfileFeature"

    def __init__(self, doc):
        self._doc = doc

    @property
    def GetNextFeature(self):
        return ConfigMateGroup(self._doc)


class ConfigActive:
    """``IConfiguration``, only its name."""
    __slots__ = ("Name",)

    def __init__(self, name):
        self.Name = name


class ConfigManager:
    """``IConfigurationManager``: AddConfiguration2 and ActiveConfiguration only."""
    __slots__ = ("_doc",)

    def __init__(self, doc):
        self._doc = doc

    def AddConfiguration2(self, name, comment, alternate, options, parent, description, rebuild):
        doc = self._doc
        doc.log.append(("AddConfiguration2", name, comment, alternate, options, parent, description, rebuild))
        if doc.refuse_add:
            return None
        doc.configs.append(name)
        for part in doc.parts.values():                      # a new configuration starts as the active one stands
            part.fixed[name] = part.fixed[doc.active]
            part.frames[name] = part.frames[doc.active]
        for mate in doc.mates:
            mate.flags[name] = mate.flags[doc.active]
        doc.active = name
        doc.epoch += 1
        return ConfigActive(name)

    @property
    def ActiveConfiguration(self):
        return ConfigActive(self._doc.active)


class ConfigSelection:
    __slots__ = ("_doc",)

    def __init__(self, doc):
        self._doc = doc

    def GetSelectedObjectCount2(self, mark):
        return len(self._doc.selected)


class ConfigExtension:
    __slots__ = ("_doc",)

    def __init__(self, doc):
        self._doc = doc

    def SelectByID2(self, name, kind, x, y, z, append, mark, callout, option):
        self._doc.log.append(("SelectByID2", name, kind, append))
        self._doc.selected.append(name)
        return True


class ConfigDoc:
    """The assembly (``IModelDoc2`` / ``IAssemblyDoc``) with configurations."""
    __slots__ = ("log", "configs", "active", "epoch", "parts", "mates", "selected", "refuse_add", "refuse_show",
                 "refuse_delete", "suppression", "wrapped_flags", "set_answer", "set_ignored", "GetSaveFlag",
                 "short_answers", "flag_answers")
    GetTitle, GetPathName, GetType = "R.SLDASM", W + "R.SLDASM", swcom.DOC_ASSEMBLY

    def __init__(self):
        self.log, self.configs, self.active, self.epoch = [], ["Default"], "Default", 0
        self.parts, self.mates, self.selected = {}, [], []
        self.refuse_add = self.refuse_show = self.refuse_delete = False
        self.suppression, self.wrapped_flags, self.set_answer, self.set_ignored = "takes", False, 0, False
        self.GetSaveFlag, self.short_answers = False, False
        self.flag_answers = {}              # configuration -> what IsSuppressed2 answers there in place of its flag

    def part(self, name, fixed=False):
        self.parts[name] = _PartState(name, W + name.rsplit("-", 1)[0] + ".SLDPRT", fixed)
        return self.parts[name]

    @property
    def ConfigurationManager(self):
        return ConfigManager(self)

    @property
    def GetConfigurationNames(self):
        return tuple(self.configs)

    def ShowConfiguration2(self, name):
        self.log.append(("ShowConfiguration2", name))
        if name == self.active or name not in self.configs or self.refuse_show:
            return False
        self.active, self.GetSaveFlag = name, True               # a show marks the assembly (the spike)
        self.epoch += 1
        return True

    def DeleteConfiguration2(self, name):
        self.log.append(("DeleteConfiguration2", name))
        if name == self.active or self.refuse_delete:
            return False
        self.configs.remove(name)
        return True

    def GetComponentByName(self, name):
        self.log.append(("GetComponentByName", name))
        state = self.parts.get(name)
        return None if state is None else ConfigComponent(self, state)

    @property
    def FirstFeature(self):
        return ConfigOrigin(self)

    @property
    def SelectionManager(self):
        return ConfigSelection(self)

    @property
    def Extension(self):
        return ConfigExtension(self)

    def ClearSelection2(self, everything):
        self.selected = []

    def FixComponent(self):
        for name in self.selected:
            self.parts[name].fixed[self.active] = True

    def UnfixComponent(self):
        for name in self.selected:
            self.parts[name].fixed[self.active] = False

    def ForceRebuild3(self, top_only):
        self.log.append(("ForceRebuild3", top_only))
        self.GetSaveFlag = True
        return True


class ConfigApp:
    __slots__ = ("ActiveDoc", "GetMathUtility")

    def __init__(self, doc, log):
        self.ActiveDoc, self.GetMathUtility = doc, _Utility(log)

    def GetUserPreferenceToggle(self, which):
        return False

    def SetUserPreferenceToggle(self, which, value):
        pass


@pytest.fixture
def configured(monkeypatch):
    """A Session on a two-gear assembly in its Default configuration, both gears found by name, a gear mate and a
    slide's distance mate kept, every finding the members read pinned here (never the committed values)."""
    for name, value in swcom.CONFIGURATION_FINDINGS:
        monkeypatch.setattr(findings, name, value, raising=False)
    for name, value in (("COMPONENT_FIND_ROUTE", "GetComponentByName"), ("MATE_FIND_ROUTE", "mate group"),
                        ("FEATURE_SUPPRESS", 0), ("FEATURE_UNSUPPRESS", 1), ("TRANSFORM_ARRAY_ORDER", "columns"),
                        ("COMPONENT_UNDER_DEFINED", 2), ("ASSEMBLY_REBUILD_ROUTE", "ForceRebuild3(True)"),
                        ("ASSEMBLY_REBUILD_TOP_ONLY", True), ("COMPONENT_RESOLVED_ROUTE", "GetSuppression2"),
                        ("COMPONENT_FULLY_RESOLVED_STATES", (2,))):
        monkeypatch.setattr(findings, name, value, raising=False)
    monkeypatch.setattr(swcom, "_out_long", Out)
    monkeypatch.setattr(swcom, "_null_dispatch", lambda: None)
    monkeypatch.setattr(swcom, "pythoncom", _PyCom)
    monkeypatch.setattr(_PyCom, "VT_BSTR", 8, raising=False)
    monkeypatch.setattr(swcom, "VARIANT", lambda kind, value: list(value) if isinstance(value, (list, tuple))
                        else value)
    monkeypatch.setattr(swcom.time, "sleep", lambda _seconds: None)
    doc = ConfigDoc()
    doc.part("Layout-1", fixed=True)
    doc.part("Gear_m1.5_N68-1")
    doc.part("Gear_m1.5_N17-1")
    doc.mates.append(ConfigMate(doc, "G1 meshes G2"))
    doc.mates.append(ConfigMate(doc, "RangeSlv along Rear", "MateDistanceDim", values={"Default": 0.010}))
    session = swcom.Session(ConfigApp(doc, doc.log), (34, 0, 0), 1)
    session.begin_build()
    for handle, name in (("layout", "Layout-1"), ("gear1", "Gear_m1.5_N68-1"), ("gear2", "Gear_m1.5_N17-1")):
        session.find_component(handle, name)
    session.find_mate("mesh1", "G1 meshes G2")
    session.find_mate("slide1", "RangeSlv along Rear")
    doc.log.clear()
    return session, doc


CONFIGURATION_MEMBER_CALLS = [
    ("CONFIGURATION_ADD_ROUTE", lambda s: s.add_configuration("4L")),
    ("CONFIGURATION_SHOW_ROUTE", lambda s: s.show_configuration("4L")),
    ("CONFIGURATION_DELETE_ROUTE", lambda s: s.delete_configuration("Default")),
    ("MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE", lambda s: s.set_mate_suppressed_in("mesh1", True, ["Default"])),
    ("SPECIFY_CONFIGURATIONS", lambda s: s.set_mate_suppressed_in("mesh1", True, ["Default"])),
    ("MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE", lambda s: s.mate_suppression("mesh1", ["Default"])),
    ("SPECIFY_CONFIGURATIONS", lambda s: s.mate_suppression("mesh1", ["Default"])),
    ("SLIDE_VALUE_ROUTE", lambda s: s.set_dimension_in("slide1", 66.0, ["Default"])),
    ("SET_VALUE_IN_SPECIFIC_CONFIGURATIONS", lambda s: s.set_dimension_in("slide1", 66.0, ["Default"])),
    ("SLIDE_VALUE_ROUTE", lambda s: s.dimension_values("slide1", ["Default"])),
    ("SPECIFY_CONFIGURATIONS", lambda s: s.dimension_values("slide1", ["Default"])),
]


@pytest.mark.parametrize("finding, member", CONFIGURATION_MEMBER_CALLS)
@pytest.mark.parametrize("value", [None, "something else"])
def test_each_configuration_member_refuses_with_a_sentence_before_any_call_when_its_finding_is_unsettled(
        configured, monkeypatch, finding, member, value):
    session, doc = configured
    monkeypatch.setattr(findings, finding, value, raising=False)
    with pytest.raises(swcom.SolidWorksError) as raised:
        member(session)
    assert str(raised.value) == (f"Working with an assembly's configurations has not been settled on this SolidWorks "
                                 f"(findings.{finding} is {value!r}), so nothing was read or changed.")
    assert doc.log == []


def test_the_configurations_and_the_active_one_are_read_from_the_document_and_its_manager(configured):
    session, doc = configured
    doc.configs.append("4L")
    assert session.configurations() == ["Default", "4L"]
    assert session.active_configuration() == "Default"


def test_a_configuration_is_added_by_the_spikes_call_on_the_manager_and_judged_by_the_active_name(configured):
    session, doc = configured
    session.add_configuration("4L")
    assert doc.log == [("AddConfiguration2", "4L", "", "", 0, "", "", True)]
    assert doc.active == "4L" and session._epoch == 1


def test_a_configuration_solidworks_will_not_add_is_a_sentence_and_still_starts_a_new_epoch(configured):
    session, doc = configured
    doc.refuse_add = True
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.add_configuration("4L")
    assert str(raised.value) == "SolidWorks would not make the configuration 4L."
    assert session._epoch == 1


def test_a_show_is_judged_by_the_active_name_never_by_what_it_returns(configured):
    session, doc = configured
    session.add_configuration("4L")
    session.show_configuration("4l")                   # already active: SolidWorks returns False, and that is right
    assert doc.active == "4L" and not doc.GetSaveFlag
    session.show_configuration("Default")
    assert doc.active == "Default" and doc.GetSaveFlag
    assert [e for e in doc.log if e[0] == "ShowConfiguration2"] == [("ShowConfiguration2", "4l"),
                                                                    ("ShowConfiguration2", "Default")]
    doc.refuse_show = True
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.show_configuration("4L")
    assert str(raised.value) == "SolidWorks would not show the configuration 4L."
    assert session._epoch == 4                          # every show starts one, whatever it answered


def test_the_active_configuration_is_never_deleted_and_a_delete_is_read_back(configured):
    session, doc = configured
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.delete_configuration("DEFAULT")
    assert str(raised.value) == ("The configuration DEFAULT is the active one in R.SLDASM, and the active "
                                 "configuration is never deleted.")
    assert not [e for e in doc.log if e[0] == "DeleteConfiguration2"]
    session.add_configuration("4L")
    session.delete_configuration("Default")
    assert doc.configs == ["4L"] and session._epoch == 1            # a delete starts no epoch (the spike)
    doc.configs.append("N")
    doc.refuse_delete = True
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.delete_configuration("N")
    assert str(raised.value) == "SolidWorks would not delete the configuration N from R.SLDASM."


def test_a_flag_is_set_for_the_named_configurations_as_a_string_array_and_every_one_read_back(configured):
    session, doc = configured
    for name in ("4L", "4H"):
        session.add_configuration(name)
    session.set_mate_suppressed_in("mesh1", True, ["Default", "4H"])
    assert ("SetSuppression2", "G1 meshes G2", 0, 3, ("Default", "4H")) in doc.log
    reads = [e for e in doc.log if e[0] == "IsSuppressed2"]
    assert reads == [("IsSuppressed2", "G1 meshes G2", 3, ("Default",)), ("IsSuppressed2", "G1 meshes G2", 3, ("4H",))]
    assert doc.mates[0].flags == {"Default": True, "4L": False, "4H": True}
    assert session.mate_suppression("mesh1", ["Default", "4L", "4H"]) == {"Default": True, "4L": False, "4H": True}
    session.set_mate_suppressed_in("mesh1", False, ["4H"])
    assert ("SetSuppression2", "G1 meshes G2", 1, 3, ("4H",)) in doc.log
    assert doc.mates[0].flags["4H"] is False


def test_flags_are_read_one_configuration_at_a_time_so_any_order_asked_gives_each_its_own_flag(configured):
    """SolidWorks 2026 answers IsSuppressed2(3, names) in the document's configuration order, whatever order the
    names are passed in (W8 s0's first run, probe/results/w8-configuration-order-20261115-092100.txt; the fake
    answers so). Read as there: Default, 2H, 4H, N, 4L on the document, RangeSlv engages InDog on in 2H and 4H."""
    session, doc = configured
    for name in ("2H", "4H", "N", "4L"):
        session.add_configuration(name)
    assert doc.configs == ["Default", "2H", "4H", "N", "4L"]
    doc.mates[0].flags = {"Default": True, "2H": False, "4H": False, "N": True, "4L": True}
    want = dict(doc.mates[0].flags)
    for order in (["2H", "4H", "N", "4L", "Default"], ["4L", "N", "4H", "2H", "Default"],
                  ["2H", "4H", "4L", "Default", "N"], ["N", "2H"], ["2H", "N"]):
        doc.log.clear()
        assert session.mate_suppression("mesh1", order) == {c: want[c] for c in order}, order
        assert [e[3] for e in doc.log if e[0] == "IsSuppressed2"] == [(c,) for c in order]
    # the document's configuration order not the record's mode order: 4L made before 2H
    doc.configs[:] = ["Default", "4L", "N", "4H", "2H"]
    assert session.mate_suppression("mesh1", ["2H", "4H", "N", "4L"]) == {"2H": False, "4H": False, "N": True,
                                                                          "4L": True}
    # and the read-back of a flag set in several configurations at once judges each by its own flag
    session.set_mate_suppressed_in("mesh1", False, ["N", "2H", "4L"])
    assert doc.mates[0].flags == {"Default": True, "2H": False, "4H": False, "N": False, "4L": False}
    session.set_mate_suppressed_in("mesh1", True, ["4L", "Default"])
    assert session.mate_suppression("mesh1", ["4L", "N", "Default", "2H"]) == {"4L": True, "N": False,
                                                                               "Default": True, "2H": False}


def test_a_flag_call_that_raises_yet_takes_effect_is_judged_by_the_read_back(configured, com_errors):
    session, doc = configured
    doc.suppression = "raises and takes"
    session.set_mate_suppressed_in("mesh1", True, ["Default"])
    assert doc.mates[0].flags["Default"] is True and not swcom.CONNECTION.lost


def test_a_flag_call_that_does_nothing_is_a_sentence_naming_where_it_did_not_take(configured):
    session, doc = configured
    session.add_configuration("4L")
    doc.suppression = "ignored"
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.set_mate_suppressed_in("mesh1", True, ["Default", "4L"])
    assert str(raised.value) == ("SolidWorks would not suppress the mate G1 meshes G2 in Default, 4L: it still reads "
                                 "on there.")
    doc.mates[0].flags["4L"] = True
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.set_mate_suppressed_in("mesh1", False, ["4L"])
    assert str(raised.value) == "SolidWorks would not turn on the mate G1 meshes G2 in 4L: it still reads suppressed there."


def test_a_lost_connection_during_a_flag_call_is_not_swallowed(configured, com_errors):
    session, doc = configured
    doc.suppression = "connection lost"
    with pytest.raises(swcom.ComError):
        session.set_mate_suppressed_in("mesh1", True, ["Default"])
    assert swcom.CONNECTION.lost


def test_flags_read_one_per_name_even_wrapped_once_more_and_a_count_that_disagrees_is_a_sentence(configured):
    session, doc = configured
    doc.wrapped_flags = True
    assert session.mate_suppression("mesh1", ["Default"]) == {"Default": False}
    doc.configs.append("X")
    doc.mates[0].flags["X"] = True
    assert session.mate_suppression("mesh1", ["Default", "X"]) == {"Default": False, "X": True}
    doc.wrapped_flags, doc.short_answers = False, True
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.mate_suppression("mesh1", ["Default", "X"])
    assert str(raised.value) == ("Asked whether the mate G1 meshes G2 is suppressed in Default, SolidWorks gave 0 "
                                 "answers, so its flag there cannot be told.")
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.dimension_values("slide1", ["Default", "X"])
    assert str(raised.value) == ("Asked for the distance of the mate RangeSlv along Rear in 2 configurations, "
                                 "SolidWorks gave 1 answer, so which is which cannot be told.")


def test_a_flag_answered_as_none_or_not_a_flag_is_a_sentence_never_on(configured):
    """Every read asks one name, so a None answer is one item and the count cannot catch it; bool(None) would read
    on. No probe has seen IsSuppressed2 answer None, but a flag never comes from it (W8-REVIEW-FIX-A point 3)."""
    session, doc = configured
    doc.configs.append("X")
    doc.mates[0].flags["X"] = False
    for answer in (None, (None,), "yes", 1.0):
        doc.flag_answers = {"X": answer[0] if isinstance(answer, tuple) else answer}
        doc.wrapped_flags = isinstance(answer, tuple)
        with pytest.raises(swcom.SolidWorksError) as raised:
            session.mate_suppression("mesh1", ["Default", "X"])
        shown = repr(doc.flag_answers["X"])
        assert str(raised.value) == (f"Asked whether the mate G1 meshes G2 is suppressed in X, SolidWorks gave "
                                     f"{shown}, not a flag, so its flag there cannot be told."), answer
    doc.flag_answers, doc.wrapped_flags = {"X": None}, False
    with pytest.raises(swcom.SolidWorksError) as raised:              # nor does a read-back take it as turned on
        session.set_mate_suppressed_in("mesh1", False, ["X"])
    assert str(raised.value) == ("Asked whether the mate G1 meshes G2 is suppressed in X, SolidWorks gave None, not "
                                 "a flag, so its flag there cannot be told.")
    # a real flag still reads as it is, as a bool or as an int
    for answer, want in ((False, False), (True, True), (0, False), (1, True)):
        doc.flag_answers = {"X": answer}
        assert session.mate_suppression("mesh1", ["X", "Default"]) == {"X": want, "Default": False}, answer


def test_a_slide_is_set_in_the_named_configurations_in_metres_and_read_back_in_millimetres(configured):
    session, doc = configured
    for name in ("4L", "4H"):
        session.add_configuration(name)
    session.set_dimension_in("slide1", 30.0, ["4L"])
    assert ("SetSystemValue3", 0.030, 3, ("4L",)) in doc.log
    assert session.dimension_values("slide1", ["Default", "4L", "4H"]) == pytest.approx(
        {"Default": 10.0, "4L": 30.0, "4H": 0.0})                    # an unset configuration reads 0 (the spike)


def test_a_slide_solidworks_answers_other_than_success_for_or_does_not_hold_is_a_sentence(configured):
    session, doc = configured
    doc.set_answer = 2
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.set_dimension_in("slide1", 30.0, ["Default"])
    assert str(raised.value) == ("SolidWorks would not set the mate RangeSlv along Rear to 30 mm in Default (it "
                                 "answered 2).")
    doc.set_answer, doc.set_ignored = 0, True
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.set_dimension_in("slide1", 30.0, ["Default"])
    assert str(raised.value) == "SolidWorks set the mate RangeSlv along Rear to 30 mm, but it reads 10 mm in Default."


def test_a_mate_with_no_distance_cannot_take_a_slide_value(configured):
    session, doc = configured
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.dimension_values("mesh1", ["Default"])
    assert str(raised.value) == "The mate G1 meshes G2 has no distance to set, so the slide cannot be placed."


def test_the_names_go_to_solidworks_as_a_string_array(monkeypatch):
    made = []
    monkeypatch.setattr(swcom, "pythoncom", _PyCom)
    monkeypatch.setattr(_PyCom, "VT_BSTR", 8, raising=False)
    monkeypatch.setattr(swcom, "VARIANT", lambda kind, value: made.append((kind, value)) or "array")
    assert swcom.Session._names(("4L", "4H")) == "array"
    assert made == [(0x2000 | 8, ["4L", "4H"])]


# -- the handle rule: every member that touches a component, after an add and after a show

def _change(session, doc, how):
    """A configuration added (and left active), or added and Default shown again: either leaves every handle held
    from before stale."""
    session.add_configuration("4L")
    if how == "show":
        session.show_configuration("Default")


def _turned_frame():
    return (0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)


COMPONENT_MEMBERS = {
    "is_fixed": lambda s: s.is_fixed("layout"),
    "component_path": lambda s: s.component_path("gear1"),
    "component_frame": lambda s: s.component_frame("gear1"),
    "component_translation": lambda s: s.component_translation("gear1"),
    "constrained_status": lambda s: s.constrained_status("gear1"),
    "component_resolved": lambda s: s.component_resolved("gear1"),
    "fix_component": lambda s: s.fix_component("gear1"),
    "unfix_component": lambda s: s.unfix_component("layout"),
    "place_component": lambda s: s.place_component("gear1", _turned_frame(), (64.5, 0.0, 0.0),
                                                   kind=swcom.ASSEMBLY_STATIC),
    "_component_ref": lambda s: s._component_ref("gear1:Gear Axis", False),
}


@pytest.mark.parametrize("member", sorted(COMPONENT_MEMBERS))
@pytest.mark.parametrize("how", ["add", "show"])
def test_every_member_that_touches_a_component_fetches_it_again_after_a_configuration_change(configured, member,
                                                                                            how):
    """W8-INTERFACES §9.4: held handles answer wrongly after AddConfiguration2 and ShowConfiguration2; every member
    goes through ``_component``, which fetches by the held name in the new epoch. The fake's StaleHandle fails the
    test if any member touches a handle from before."""
    session, doc = configured
    _change(session, doc, how)
    doc.log.clear()
    COMPONENT_MEMBERS[member](session)
    fetched = [e[1] for e in doc.log if e[0] == "GetComponentByName"]
    assert len(fetched) == 1 and fetched[0] in ("Layout-1", "Gear_m1.5_N68-1")
    COMPONENT_MEMBERS[member](session) if member not in ("fix_component", "unfix_component") else None
    assert len([e for e in doc.log if e[0] == "GetComponentByName"]) == 1        # once per epoch, then kept


def test_the_fixed_layout_reads_fixed_after_a_change_and_a_put_holds_in_the_active_configuration_only(configured):
    session, doc = configured
    assert session.is_fixed("layout")
    session.add_configuration("4L")
    assert session.is_fixed("layout")                  # a held handle would have read False (the spike)
    session.place_component("gear1", _turned_frame(), (64.5, 0.0, 0.0), kind=swcom.ASSEMBLY_STATIC)
    assert session.component_translation("gear1") == pytest.approx((64.5, 0.0, 0.0))
    session.show_configuration("Default")
    assert session.component_translation("gear1") == pytest.approx((0.0, 0.0, 0.0))


def test_a_component_gone_after_a_change_is_component_gone_with_the_sentence_of_the_open(configured):
    session, doc = configured
    session.add_configuration("4L")
    del doc.parts["Gear_m1.5_N68-1"]
    with pytest.raises(swcom.ComponentGone) as raised:
        session.component_frame("gear1")
    assert str(raised.value) == ("Gear_m1.5_N68-1 is not in R.SLDASM any more: it was renamed or deleted in "
                                 "SolidWorks.")


def test_fetching_again_refuses_with_a_sentence_when_the_find_route_is_unsettled(configured, monkeypatch):
    session, doc = configured
    session.add_configuration("4L")
    monkeypatch.setattr(findings, "COMPONENT_FIND_ROUTE", None, raising=False)
    doc.log.clear()
    with pytest.raises(swcom.SolidWorksError) as raised:
        session.is_fixed("gear1")
    assert str(raised.value) == ("Finding a component again after a configuration change has not been settled on "
                                 "SolidWorks yet (findings.COMPONENT_FIND_ROUTE is None), so nothing was read or "
                                 "changed.")
    assert doc.log == []


def test_a_handle_nothing_was_kept_as_is_a_sentence(configured):
    session, _ = configured
    with pytest.raises(swcom.SolidWorksError) as raised:
        session._component("gear9")
    assert str(raised.value) == ("No component is kept as 'gear9', so it cannot be read or changed; that is a fault "
                                 "in Gear Generator, not in SolidWorks.")


def test_a_selection_after_a_change_goes_by_the_held_names_never_through_the_fresh_handle(configured):
    session, doc = configured
    session.add_configuration("4L")
    session._component_ref("gear1:Gear Axis", False)
    assert [e for e in doc.log if e[0] == "SelectByID2"] == [
        ("SelectByID2", "Gear Axis@Gear_m1.5_N68-1@R", "AXIS", False)]


def test_activating_and_opening_start_a_new_epoch(configured, com):
    session, doc = configured
    before = session._epoch
    session._raise_epoch()
    assert session._epoch == before + 1
    part = com.saved(W + "Gear_m1.5_N68.SLDPRT")
    opened = _session(com)
    opened.begin_build()
    opened.open_document(W + "Gear_m1.5_N68.SLDPRT")
    assert opened._epoch >= 1 and part is com.active


def test_the_fake_fails_loudly_when_a_handle_from_before_a_change_is_used(configured):
    session, doc = configured
    held = session._handles["layout"]["component"]
    session.add_configuration("4L")
    with pytest.raises(StaleHandle):
        held.IsFixed  # noqa: B018 - the read is the test


@pytest.mark.parametrize("how", ["add", "show"])
def test_the_raw_component_a_probe_touches_is_fetched_in_the_current_epoch(configured, how):
    session, doc = configured
    _change(session, doc, how)
    assert session.raw_component("layout").IsFixed is True       # a held handle would raise StaleHandle here


def test_no_code_but_swcom_reads_the_sessions_component_registry():
    """W8-INTERFACES §9.4: only the Session holds COM handles, so ``._handles[`` is read in swcom.py alone, across
    src/ and probe/ (``carrier_handles[`` and other names of one's own are not the Session's)."""
    import pathlib
    import re
    root = pathlib.Path(__file__).resolve().parent.parent
    pattern = re.compile(r"\._handles\[")
    offenders = [str(p.relative_to(root)) for folder in ("src", "probe") for p in sorted((root / folder).rglob("*.py"))
                 if p.name != "swcom.py" and pattern.search(p.read_text("utf-8"))]
    assert offenders == []
