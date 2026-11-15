"""The pure parts of probe tier 11 (W8-PLAN §4.2 item 1, an over-defined configuration shown, and the read order of
IsSuppressed2(3, names) and GetSystemValue3(3, names)), without SolidWorks."""

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
    into = _state("Z", 25.0, errors={"S slide": {"code": 46}, "S slide 2": {"code": 46}},
                  problems=["The mate S slide is in error in SolidWorks."], constrained={"A": 2, "S": 4})
    into["show"] = {"call": "show Z", "returned": True,
                    "windows": [{"title": "", "class": "#32770", "children": [], "answered": []}]}
    facts = {"slides": {"configuration": "Z", "other": "Y", "other_at": 30.0, "back_at": 20.0, "into": into,
                        "after": _state("Y", 30.0), "back": dict(_state("Z", 20.0), show=None)}}
    reading = p11.fight_reading(facts, "slides")
    assert reading == {"show_returned": True, "active_is_target": True, "windows": [("show Z", "#32770", "")],
                       "mates_in_error": ["S slide", "S slide 2"], "over_defined": ["S"],
                       "app_problems": ["The mate S slide is in error in SolidWorks."], "other_clean": True,
                       "back_clean": True, "windows_answered": []}
    assert p11.fight_reading({}, "slides")["show_returned"] is None
    assert p11.show_over_defined(reading) == p11.SHOWN_IN_ERROR
    into["show"]["windows"][0]["answered"] = ["WM_CLOSE at 5.0 s"]
    assert p11.fight_reading(facts, "slides")["windows_answered"] == [("show Z", "#32770", ["WM_CLOSE at 5.0 s"])]
    assert p11.show_over_defined(p11.fight_reading(facts, "slides")) is None
    assert p11.show_over_defined(dict(reading, mates_in_error=[])) is None
    assert p11.show_over_defined(dict(reading, other_clean=False)) is None
