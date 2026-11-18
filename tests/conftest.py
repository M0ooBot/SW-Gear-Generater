"""What every test shares: an exception raised in a Tk callback fails the test it was raised in; and W9c's gates, and
W9d's demonstration findings, patched back to None for a test that wants their refusal, now that measured ones are set.

Tk does not raise such an exception where the callback was set off (a variable's write, an ``after``, an event): it
hands it to the root's ``report_callback_exception``, which prints a traceback and carries on, so a test could pass
over one. Here every root's report is collected instead, and the test fails at teardown naming each. The Linux venv
has no tkinter, and so nothing to collect.
"""
import traceback

import pytest

from gear_generator import findings

try:
    import tkinter
except ImportError:                     # no Tk here: no Tk callback can raise
    tkinter = None


@pytest.fixture(autouse=True)
def tk_callback_exceptions(monkeypatch):
    """The tracebacks of the exceptions Tk callbacks raised during the test; the test fails at teardown if any."""
    caught = []
    if tkinter is not None:
        def report(_root, kind, value, tb):
            caught.append("".join(traceback.format_exception(kind, value, tb)))
        monkeypatch.setattr(tkinter.Tk, "report_callback_exception", report)
    yield caught
    if caught:
        pytest.fail(f"{len(caught)} exception(s) raised in a Tk callback:\n\n" + "\n".join(caught), pytrace=False)


# W9c's gates (findings.py; W9C-INTERFACES.md §8): the five measured are True on 2026 since W9C-RUNS-REVIEW.md's
# addendum on the final runs; a test of what the app does while one is not measured patches it back to None.
W9C_GATES = ("UPDATE_INSERTS_A_GEAR", "UPDATE_MAKES_MATES_WITH_MODES", "UPDATE_BANDS_IN_PLACE", "UPDATE_ADDS_A_MODE",
             "UPDATE_REMOVES_A_MODE", "UPDATE_MAKES_A_NEW_COUPLING", "UPDATE_SUPPRESSES_THE_RELIEF",
             "EXTERNAL_REFERENCES_READ")


@pytest.fixture
def w9c_unmeasured(monkeypatch):
    """Every W9c gate None on both versions, as committed before 2026's were measured."""
    for name in W9C_GATES:
        for year in (2026, 2024):
            monkeypatch.setattr(findings, f"{name}_ON_{year}", None)


# W9d's demonstration findings (findings.py, M9's block; W9D-INTERFACES.md §8): CARRY_INSERTS,
# CARRY_INSERTS_IN_A_CONFIGURATION, REFERENCED_CONFIGURATION_READ, CARRY_REMAKE_KINDS and
# CARRY_GEAR_MATE_ON_AN_APP_GEAR are set on 2026 since the review of the second 2026 run (W9D-DEMONSTRATION-REVIEW.md,
# 7996089, §4), the rest None; a test of what the app does while one is not measured patches it back to None. The
# probes' reads (§8.1) are not here: test_swbuild_carry's none_on_2026 patches those.
W9D_M9_FINDINGS = ("CARRY_INSERTS", "CARRY_INSERTS_IN_A_CONFIGURATION", "REFERENCED_CONFIGURATION_READ",
                   "CARRY_REMAKE_KINDS", "CARRY_GEAR_MATE_ON_AN_APP_GEAR", "CARRY_INSERTS_A_SUBASSEMBLY",
                   "CARRY_REMAKES_ON_A_LEAF", "VIRTUAL_READ", "PATTERN_INSTANCE_READ", "ORIGIN_ENTITY_READ",
                   "PERSIST_REFERENCE_ROUTE_FOR_VERTICES")


@pytest.fixture
def w9d_unmeasured(monkeypatch):
    """Every finding W9d's demonstration sets None on both versions, as committed before 2026's were measured."""
    for name in W9D_M9_FINDINGS:
        for year in (2026, 2024):
            monkeypatch.setattr(findings, f"{name}_ON_{year}", None)
