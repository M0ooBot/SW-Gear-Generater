"""ISSUE-1-PLAN §3's RangeBox, the issue's two-speed planetary (``workbook_fixtures.range_box``), as the plan pins it
before W9: it assesses with four warnings and none about the clutch, and each mode engages and turns as §3 says. W9's
S0 builds it on SolidWorks, so a change here is a change to what S0 measured."""

from dataclasses import replace

import pytest

from gear_generator.workbook import assess, gearbox
from workbook_fixtures import range_box

BOOK = "C:\\B\\RangeBox.xlsx"


def assessed():
    return assess.assess(replace(range_box(), source_path=BOOK), [], "C:\\Out\\")


def test_range_box_assesses_with_the_four_warnings_none_about_the_clutch_and_plans_a_build():
    """Before W9 four warnings, none about the clutch; W9b adds §3's three (``test_workbook_sleeve_checks``), each
    about RangeSlv, and engagement and speeds are unchanged."""
    a = assessed()
    warnings = [d.message for d in a.diagnostics if d.level == "warning"]
    assert [d.message for d in a.diagnostics if d.level == "error"] == [] and a.lay_out_refusal() == ""
    assert len(warnings) == 4 + 3
    w9b = [w for w in warnings if "cannot reach" in w or "nothing keys" in w or "which it does not engage there" in w]
    before = [w for w in warnings if w not in w9b]
    assert len(w9b) == 3 and all("RangeSlv" in w for w in w9b)
    assert sum("Planet" in w for w in before) == 3 and sum("RangeSlv" in w for w in before) == 1
    assert not any("HighDog" in w or "LowDog" in w or "engage" in w or "bridg" in w for w in before)
    plan = gearbox.plan_gearbox(a, None, exists=lambda p: False, read_sidecar=lambda p: None)
    assert plan.refusal == "" and plan.motion is not None and plan.motion.modes


def test_range_box_engages_high_in_h_nothing_in_n_low_in_l_at_the_ratios_of_section_3():
    modes = {m.name: m for m in assessed().report.modes}
    assert list(modes) == ["H", "N", "L"]
    assert {n: m.positions["RangeSlv"] for n, m in modes.items()} == {"H": ("H", -5.0), "N": ("N", 0.0),
                                                                      "L": ("L", 5.0)}
    assert {n: m.engaged for n, m in modes.items()} == {"H": (("RangeSlv", "HighDog"),), "N": (),
                                                        "L": (("RangeSlv", "LowDog"),)}
    assert modes["H"].ratio == pytest.approx(1.0, abs=1e-9)
    assert modes["N"].ratio is None and modes["N"].ratio_why == "neutral"
    assert modes["L"].ratio == pytest.approx(1 + 55 / 29, abs=1e-9)
    assert round(modes["L"].ratio, 6) == 2.896552
    for m in modes.values():
        speeds = m.motion.speeds
        assert float(speeds["Carrier"]) == pytest.approx(517.857142857, abs=1e-6)
        assert float(speeds["Planet"]) == pytest.approx(-1673.076923077, abs=1e-6)
        assert float(speeds["Ring"]) == 0.0
    assert "Output" not in modes["N"].motion.speeds
