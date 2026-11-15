"""What every test shares: an exception raised in a Tk callback fails the test it was raised in.

Tk does not raise such an exception where the callback was set off (a variable's write, an ``after``, an event): it
hands it to the root's ``report_callback_exception``, which prints a traceback and carries on, so a test could pass
over one. Here every root's report is collected instead, and the test fails at teardown naming each. The Linux venv
has no tkinter, and so nothing to collect.
"""
import traceback

import pytest

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
