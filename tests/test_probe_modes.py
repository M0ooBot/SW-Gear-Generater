"""The pure parts of probe tier 11 (W8-PLAN §4.2 item 1, an over-defined configuration shown, and the read order of
IsSuppressed2(3, names) and GetSystemValue3(3, names)), without SolidWorks."""

import copy
import json
from pathlib import Path

import pytest

from gear_generator.probe import __main__ as probe_main
from gear_generator.probe import harness
from gear_generator.probe import p11_modes as p11

ORDER = ["Default", "X", "Z", "Y"]
FLAGS = {"Default": False, "X": False, "Z": False, "Y": True}
VALUES = {"Default": 10.0, "X": 15.0, "Z": 20.0, "Y": 30.0}


def test_the_probe_is_registered_in_tier_11():
    probe_main.load_probes()
    found = [p for p in harness.REGISTRY if p.name == "w8_over_defined_show"]
    assert len(found) == 1 and found[0].tier == 11


def test_the_lists_passed_tell_the_orders_apart():
    lists = p11.passed_lists(ORDER)
    assert lists[:3] == [ORDER, ORDER[::-1], ["Z", "Default", "Y", "X"]]
    assert ["X", "Y"] in lists and ["Y", "X"] in lists and ["Default", "Z"] in lists and ["Z", "Default"] in lists
    assert [n for n in lists if len(n) == 1] == [[n] for n in ORDER]
    with pytest.raises(ValueError):
        p11.passed_lists(["Default", "X", "Y"])


def test_a_read_is_judged_against_the_single_name_truth():
    by_document = [FLAGS[n] for n in ORDER if n in ("Y", "X")]          # X then Y
    assert p11.read_order(by_document, ["Y", "X"], ORDER, FLAGS) == p11.DOCUMENT_ORDER
    assert p11.read_order([True, False], ["Y", "X"], ORDER, FLAGS) == p11.ORDER_PASSED
    assert p11.read_order([False, False], ["Default", "X"], ORDER, FLAGS) == p11.EITHER
    assert p11.read_order([True, True], ["Default", "X"], ORDER, FLAGS) == p11.NEITHER
    assert p11.read_order("raised", ["Y"], ORDER, FLAGS) == p11.NEITHER
    assert p11.read_order([False], ["W"], ORDER, FLAGS) == p11.NEITHER
    reversed_values = [VALUES[n] for n in ORDER[::-1]]
    assert p11.read_order(reversed_values, ORDER[::-1], ORDER, VALUES) == p11.ORDER_PASSED
    assert p11.read_order([VALUES[n] for n in ORDER], ORDER[::-1], ORDER, VALUES) == p11.DOCUMENT_ORDER


def test_the_order_over_many_reads_needs_one_that_tells_and_none_that_contradicts():
    assert p11.order_of([{"verdict": p11.EITHER}, {"verdict": p11.DOCUMENT_ORDER}]) == p11.DOCUMENT_ORDER
    assert p11.order_of([{"verdict": p11.EITHER}]) is None
    assert p11.order_of([{"verdict": p11.DOCUMENT_ORDER}, {"verdict": p11.ORDER_PASSED}]) is None
    assert p11.order_of([{"verdict": p11.ORDER_PASSED}, {"verdict": p11.NEITHER}]) is None
    assert p11.order_of([]) is None


def _moment(answer_flags, answer_values):
    sup = {"truth_as_set": True, "reads": [{"verdict": answer_flags}]}
    val = {"truth_as_set": True, "reads": [{"verdict": answer_values}]}
    return {"suppression": {"m": sup}, "value": {"s": val}}


def test_the_reads_are_gathered_over_every_moment():
    facts = {"read_order": {"a": _moment(p11.DOCUMENT_ORDER, p11.ORDER_PASSED),
                            "b": _moment(p11.EITHER, p11.ORDER_PASSED)}}
    assert p11.order_of(p11.all_reads(facts, "suppression")) == p11.DOCUMENT_ORDER
    assert p11.order_of(p11.all_reads(facts, "value")) == p11.ORDER_PASSED
    assert p11.truths_agree(facts)
    facts["read_order"]["b"]["value"]["s"]["truth_as_set"] = False
    assert not p11.truths_agree(facts) and not p11.truths_agree({})


def _state(active, s_z, errors=None, problems=(), constrained=None):
    return {"active": active, "S_z": s_z, "errors_on": errors or {}, "app_problems": list(problems),
            "constrained": constrained or {"A": 2, "D": 2, "S": 2}, "show": {"call": "show", "windows": []},
            "rebuild": {"call": "rebuild", "windows": []}}


def test_a_configuration_reads_clean_only_with_no_code_no_sentence_nothing_over_defined_and_s_in_place():
    assert p11.clean(_state("Y", 30.0 + 5e-7), 30.0)
    assert not p11.clean(_state("Y", 30.0 + 2e-6), 30.0)
    assert not p11.clean(_state("Y", 30.0, errors={"S slide": {"code": 46}}), 30.0)
    assert not p11.clean(_state("Y", 30.0, problems=["The mate S slide is in error in SolidWorks."]), 30.0)
    assert not p11.clean(_state("Y", 30.0, constrained={"S": 4}), 30.0)
    assert not p11.clean(dict(_state("Y", 30.0), app_problems="raised"), 30.0)


def test_a_fights_reading_names_what_the_show_into_it_and_after_it_read():
    named = ["The mate S slide is in error in SolidWorks.", "The mate S slide 2 is in error in SolidWorks."]
    into = _state("Z", 25.0, errors={"S slide": {"code": 47}, "S slide 2": {"code": 47}}, problems=named,
                  constrained={"A": 2, "S": 4})
    into["show"] = {"call": "show Z", "returned": True,
                    "windows": [{"title": "", "class": "#32770", "children": [], "answered": []}]}
    facts = {"slides": {"configuration": "Z", "other": "Y", "other_at": 30.0, "back_at": 20.0, "into": into,
                        "after": _state("Y", 30.0), "also": _state("X", 15.0),
                        "back": dict(_state("Z", 20.0), show=None)}}
    reading = p11.fight_reading(facts, "slides")
    assert reading == {"show_returned": True, "active_is_target": True, "windows": [("show Z", "#32770", "")],
                       "windows_answered": [], "watch_errors": [], "mates_in_error": ["S slide", "S slide 2"],
                       "over_defined": ["S"], "app_problems": named, "app_names": ["S slide", "S slide 2"],
                       "named_exactly": True, "others_clean": {"Y": True, "X": True}, "other_clean": True,
                       "back_clean": True}
    assert p11.fight_reading({}, "slides")["show_returned"] is None
    assert p11.show_over_defined(reading) == p11.SHOWN_IN_ERROR
    into["show"]["windows"][0]["answered"] = ["WM_CLOSE at 5.0 s"]
    assert p11.fight_reading(facts, "slides")["windows_answered"] == [("show Z", "#32770", ("WM_CLOSE at 5.0 s",))]
    assert p11.show_over_defined(p11.fight_reading(facts, "slides")) is None
    assert p11.show_over_defined(dict(reading, named_exactly=False)) is None
    assert p11.show_over_defined(dict(reading, other_clean=False)) is None
    assert p11.show_over_defined(dict(reading, watch_errors=[("show Z", "OSError()")])) is None


# -- doctored copies of tier 11's result file (built here, never committed) ---------------------------------------

RESULT = Path(__file__).resolve().parents[1] / "probe" / "results" / "w8-over-defined-20261115-100312.json"
X_SHOW = "a third configuration: ShowConfiguration2(X)"
BOX = {"title": "", "class": "#32770", "children": [["Button", "OK"]], "stood_s": 5.0, "first_s": 0.1,
       "answered": ["WM_CLOSE at 5.0 s"]}


@pytest.fixture(scope="module")
def result_facts():
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    return {r["name"]: r for r in data["records"]}["w8_over_defined_show"]["facts"]["w8_over_defined"]


def _finding(facts):
    return p11.show_over_defined(p11.fight_reading(facts, "slides"))


def test_the_result_file_as_committed_gives_the_finding(result_facts):
    reading = p11.fight_reading(result_facts, "slides")
    assert _finding(result_facts) == p11.SHOWN_IN_ERROR
    assert reading["others_clean"] == {"Y": True, "X": True} and reading["watch_errors"] == []
    assert reading["app_names"] == ["S slide", "S slide 2"] and reading["named_exactly"]


def test_x_reading_in_error_after_the_fight_gives_no_finding(result_facts):
    f = copy.deepcopy(result_facts)
    also = f["slides"]["also"]
    also["errors_on"] = {"S slide": {"code": 47, "warning": False}}
    also["app_problems"] = ["The mate S slide is in error in SolidWorks."]
    also["constrained"]["S"] = 4
    assert also["S_z"] == 15.0                       # the place alone would have passed
    assert p11.fight_reading(f, "slides")["others_clean"] == {"Y": True, "X": False}
    assert _finding(f) is None


def test_a_box_answered_during_xs_show_gives_no_finding(result_facts):
    f = copy.deepcopy(result_facts)
    f["slides"]["also"]["show"]["windows"].append(dict(BOX))
    assert _finding(f) is None
    g = copy.deepcopy(result_facts)                  # the same box, in the run's log of watched calls only
    next(c for c in g["watched_calls"] if c["call"] == X_SHOW)["windows"].append(dict(BOX))
    assert p11.fight_reading(g, "slides")["windows_answered"] == [(X_SHOW, "#32770", ("WM_CLOSE at 5.0 s",))]
    assert _finding(g) is None


def test_a_dead_watch_gives_no_finding(result_facts):
    f = copy.deepcopy(result_facts)
    call = next(c for c in f["watched_calls"] if c["call"] == X_SHOW)
    call["watch_error"], call["windows"] = "OSError(22, 'EnumWindows')", []
    assert p11.fight_reading(f, "slides")["watch_errors"] == [(X_SHOW, "OSError(22, 'EnumWindows')")]
    assert _finding(f) is None
    g = copy.deepcopy(result_facts)                  # recorded on the step itself, as runs from now on record it
    g["slides"]["into"]["rebuild"]["watch_error"] = "OSError()"
    assert _finding(g) is None


def test_the_app_naming_another_mate_gives_no_finding(result_facts):
    f = copy.deepcopy(result_facts)
    f["slides"]["into"]["app_problems"][1] = "The mate Distance1 is in error in SolidWorks."
    assert p11.fight_reading(f, "slides")["app_names"] == ["Distance1", "S slide"]
    assert _finding(f) is None
    g = copy.deepcopy(result_facts)
    g["slides"]["into"]["app_problems"].append("The mate Coincident1 is in error in SolidWorks.")
    assert _finding(g) is None
    h = copy.deepcopy(result_facts)
    h["slides"]["into"]["app_problems"] = "raised"
    assert _finding(h) is None
