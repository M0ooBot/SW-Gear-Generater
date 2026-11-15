"""Probe tier 11, W8's last call probed ahead (W8-PLAN §4.2 item 1): a configuration whose mates fight, shown and
rebuilt; and the order in which ``IFeature.IsSuppressed2(3, names)`` and ``IDimension.GetSystemValue3(3, names)``
answer.

W8-PLAN §4.2 names this probe ``p9_modes.py``. Tiers 9 and 10 were taken by the time it was written
(``p9_turned.py``, ``p10_planetary.py``), so it is tier 11.

**The shape** is the W8 spike's and its follow-up's (``p8_motion``'s ``w8_`` items, reused, not copied): the app's
own spur (30 teeth, module 1.5, face 10) as anchor A and dog D, and its internal spur ring as sleeve S. A and D are
held as W5 holds an anchor, on one line along +Z; S sits on A's axis with the spline S-A and the coupling S-D as
1 : 1 gear mates settled by the read-back, and ONE slide, a distance from S's origin to the layout's Front. The
configurations X, Z and Y are added in that order, so the document's order (Default, X, Z, Y) is neither
alphabetical nor any order the reads pass the names in. The slide reads Default 10, X 15, Z 20, Y 30 mm, each set by
``SetSystemValue3`` one configuration per call; the coupling is on in Default, X and Z and off in Y.

**A. An over-defined configuration shown.**
- A second slide (a distance mate on the same two entities, 25 mm) is made while Y is shown, with the first slide
  suppressed in Y around the make so the make itself fights nothing; it is then turned on in Z only and the first
  slide turned back on in Y. Z now holds two slides that fight (20 against 25 mm).
- Z is shown (``ShowConfiguration2``) and rebuilt by the app's top-only route (``ForceRebuild3(True)``), each call
  under the spike's dialog watch, extended here (``ModesWatch``) to name the call, keep watching a moment after it
  returns, list what was already standing, and answer a box the spike's three answers leave standing. Read after:
  what the show answered, the active name, every mate's error code, every component's constrained status, the app's
  own ``mate_states`` and its mate check's sentences (``swbuild._mate_problems``), What's Wrong, every
  ``GetSaveFlag``, and where S stands.
- Y, then X, shown and rebuilt: each must read every code 0 and S at its value to 1e-6 mm.
- Z shown again, the second slide suppressed in Z, rebuilt: clean again, S at 20?
- The same for the other fight §4.2 names: a lock S-D made while Y is shown (the coupling is off there), turned on in
  Y only; then, with X shown, the coupling turned on in Y; Y shown and rebuilt; X shown; Y shown, the lock suppressed
  in Y, rebuilt.

**B. The read order.** At three moments (before the fight is made; after the second slide's flags are set; after
the lock's), each mate whose flags differ between configurations is read with ``IsSuppressed2(3, names)``: the full
list in the document's order, reversed, and shuffled; two-name lists both ways round; each name alone. The slide's
values are read the same way with ``GetSystemValue3(3, names)``. Each read is judged against the single-name reads
(``read_order``): does it answer in the document's configuration order filtered to the names asked, or in the order
passed? The flags and values each configuration holds are also read in that configuration while it is shown
(``IsSuppressed2`` this configuration, and where S stands), as a check on the single-name reads.

Nothing is saved after the shape is built: the assembly is never saved, and every document the probe opened is
closed by ``CloseDoc`` under the watch (``watched_close``, as the house's unsaved-close probe closes), its parts' file
times read before and after.
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence

from ..swcom import call
from . import scaffold as sc
from .harness import Px, probe
from .p8_motion import (TOP_ONLY, W8_A_Z, W8_AXIS_XY, W8_D_Z, W8_S_PHASE, Assembly, DialogWatch, _active_config,
                        _app_build, _bstr_array, _cfg_suppress, _config_names, _disk, _enums, _folder, _frames,
                        _mate_axes, _plane_names, _spike_mount, _sv_set, _w8_flags, _w8_gear_mate, _w8_refresh,
                        _w8_select, add_mate, constrained, delete_mate, error_code, is_suppressed, mate_feature,
                        mate_names, rebuild, select_components, unfix, w8_parts_spec, watched_close, whats_wrong, _W8)
from .p7_workbook import _rename, open_by_path, plain

TAG = "Probe W8 Over"
CONFIGS_ADDED = ("X", "Z", "Y")          # in this order: the document's order is then neither alphabetical nor passed
FIGHT, OTHER, ALSO = "Z", "Y", "X"       # Z holds the two slides; Y the lock and, later, the coupling beside it
SLIDE_VALUES = {"Default": 10.0, "X": 15.0, "Z": 20.0, "Y": 30.0}   # mm, the first slide in each configuration
SECOND_SLIDE = 25.0                      # mm, the second slide, in every configuration
SLIDE, SECOND, COUPLING, SPLINE, LOCK = "S slide", "S slide 2", "S engages D", "S splined to A", "S locked to D"
TOLERANCE_MM = 1e-6
SPECIFIED = 3                            # swInConfigurationOpts_e.swSpecifyConfiguration (findings.SPECIFY_CONFIGURATIONS)
DOCUMENT_ORDER, ORDER_PASSED, EITHER, NEITHER = "document order", "order passed", "either", "neither"


# -- pure -----------------------------------------------------------------------------------------------------------

def passed_lists(order: Sequence[str]) -> List[List[str]]:
    """The name lists each read passes, for configurations in the document's ``order`` (four or more): the full list
    in that order, reversed and shuffled; two two-name lists, each both ways round; each name alone."""
    d = list(order)
    if len(d) < 4:
        raise ValueError(f"four configurations or more are needed to tell the orders apart, not {d}")
    shuffled = [d[2], d[0], d[3], d[1]] + d[4:]
    return [d, d[::-1], shuffled, [d[1], d[3]], [d[3], d[1]], [d[0], d[2]], [d[2], d[0]]] + [[n] for n in d]


def read_order(answer: Any, passed: Sequence[str], order: Sequence[str], truth: Mapping[str, Any]) -> str:
    """How one read answered: ``DOCUMENT_ORDER`` when its items are each configuration's ``truth`` in the document's
    ``order`` filtered to the names ``passed``; ``ORDER_PASSED`` when they are in the order passed; ``EITHER`` when
    the two orders give the same items (the read cannot tell them apart) and it matches; ``NEITHER`` otherwise
    (also for a raise or a wrong count)."""
    if not isinstance(answer, (list, tuple)) or any(n not in truth for n in passed):
        return NEITHER
    got = list(answer)
    by_document = [truth[n] for n in order if n in passed]
    by_passed = [truth[n] for n in passed]
    if by_document == by_passed:
        return EITHER if got == by_document else NEITHER
    if got == by_document:
        return DOCUMENT_ORDER
    if got == by_passed:
        return ORDER_PASSED
    return NEITHER


def order_of(reads: Sequence[Mapping[str, Any]]) -> Optional[str]:
    """The order a call answers in over many reads: ``DOCUMENT_ORDER`` or ``ORDER_PASSED`` when at least one read
    could tell them apart, every such read says the same, and no read answered in neither; else None."""
    verdicts = [r.get("verdict") for r in reads]
    if not verdicts or NEITHER in verdicts:
        return None
    told = {v for v in verdicts if v != EITHER}
    return told.pop() if len(told) == 1 else None


def all_reads(facts: Mapping[str, Any], kind: str) -> List[Mapping[str, Any]]:
    """Every read of one kind (``"suppression"`` or ``"value"``) over every moment the probe read the order."""
    return [r for moment in (facts.get("read_order") or {}).values() for item in (moment.get(kind) or {}).values()
            for r in item.get("reads", ())]


def truths_agree(facts: Mapping[str, Any]) -> bool:
    """Whether every single-name read agrees with what was set, for flags and values, at every moment."""
    for moment in (facts.get("read_order") or {}).values():
        for kind in ("suppression", "value"):
            for item in (moment.get(kind) or {}).values():
                if not item.get("truth_as_set"):
                    return False
    return bool(facts.get("read_order"))


def clean(state: Mapping[str, Any], at_mm: float) -> bool:
    """A configuration shown and rebuilt reads clean: no code on any mate on in it, the app's mate check silent, no
    component over-defined (4), and S at ``at_mm`` to 1e-6 mm."""
    return (not state.get("errors_on") and state.get("app_problems") == [] and
            all(v != 4 for v in (state.get("constrained") or {}).values()) and
            isinstance(state.get("S_z"), (int, float)) and abs(state["S_z"] - at_mm) <= TOLERANCE_MM)


def windows_of(step: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    """Every window a watched step saw open: the show's and the rebuild's."""
    return [dict(w, call=c.get("call")) for c in (step.get("show"), step.get("rebuild")) if c
            for w in c.get("windows", ())]


def fight_reading(facts: Mapping[str, Any], key: str) -> Dict[str, Any]:
    """One fight's readings, as the finding states them: the show into the fighting configuration (its answer, the
    active name, the windows, the mates in error, the components over-defined, the app's mate check), the
    configuration shown after it, and the fighting configuration with the added mate suppressed."""
    fight = (facts.get(key) or {})
    into, after, back = fight.get("into") or {}, fight.get("after") or {}, fight.get("back") or {}
    target, other = fight.get("configuration"), fight.get("other")
    return {
        "show_returned": (into.get("show") or {}).get("returned"),
        "active_is_target": into.get("active") == target,
        "windows": [w.get("title") for s in (into, after, fight.get("again") or {}, back) for w in windows_of(s)],
        "mates_in_error": sorted((into.get("errors_on") or {}).keys()),
        "over_defined": sorted(k for k, v in (into.get("constrained") or {}).items() if v == 4),
        "app_problems": list(into.get("app_problems") or []),
        "other_clean": clean(after, fight.get("other_at", float("nan"))) and after.get("active") == other,
        "back_clean": clean(back, fight.get("back_at", float("nan"))) and back.get("active") == target,
    }


# -- the watch ------------------------------------------------------------------------------------------------------

class ModesWatch(DialogWatch):
    """The spike's ``DialogWatch`` for one named call, with four additions: the windows already standing when it
    starts (and not in ``baseline``) recorded with their texts; a short watch after the call returns, so a window
    that opens as it ends is seen; when each window first showed, in seconds from the call's start; and, for a box
    the spike's three answers (WM_CLOSE, Escape, Cancel / No / Don't Save) leave standing, a fourth (Close, OK or
    Continue) and then the first button whose text is not a Yes or a Save. Each watched call is appended to ``log``."""

    MORE = ("Close", "OK", "Continue")
    NEVER = ("Yes", "Yes to All", "Save", "Save All")

    def __init__(self, pid: int, label: str, log: List[Dict[str, Any]], baseline: Sequence[int] = (),
                 linger: float = 1.0, dismiss_after: float = 5.0) -> None:
        super().__init__(pid, dismiss_after)
        self.label, self.log, self.baseline, self.linger = label, log, set(baseline), linger
        self.standing: List[Dict[str, Any]] = []
        self._more = threading.Thread(target=self._answer_more, daemon=True)
        self._t0 = 0.0

    def describe(self, hwnd: int) -> Dict[str, Any]:
        title, cls = self._text(hwnd)
        return {"title": title, "class": cls, "children": [[c, t] for _h, t, c in self._children(hwnd) if t][:30]}

    def __enter__(self) -> "ModesWatch":
        super().__enter__()
        self._t0 = self._started
        try:
            self.standing = [self.describe(h) for h in self._before if h not in self.baseline]
        except Exception as exc:  # noqa: BLE001 - the watch failing is evidence
            self.error = repr(exc)
        self._more.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self._seconds = time.monotonic() - self._t0
        time.sleep(self.linger)
        super().__exit__(*exc)
        self._more.join(5.0)
        self.log.append({"call": self.label, "seconds": round(self._seconds, 3), "windows": self.report()["windows"],
                         "standing_at_entry": self.standing, "watch_error": self.error})

    def _answer_more(self) -> None:
        try:
            u = self._user32()
            while not self._stop.wait(0.25):
                now = time.monotonic()
                for hwnd, seen in list(self._seen.items()):
                    age = now - seen["first"]
                    if not u.IsWindow(hwnd) or len(seen["answered"]) < 3:
                        continue
                    children = self._children(hwnd)
                    if len(seen["answered"]) == 3 and age >= 4 * self.dismiss_after:
                        buttons = {t.replace("&", "").strip(): h for h, t, _c in children}
                        pick = next((n for n in self.MORE if n in buttons), None)
                        if pick:
                            u.PostMessageW(buttons[pick], 0x00F5, 0, 0)      # BM_CLICK
                        seen["answered"].append(f"{pick} clicked at {age:.1f} s" if pick else
                                                f"no Close, OK or Continue button at {age:.1f} s")
                    elif len(seen["answered"]) == 4 and age >= 5 * self.dismiss_after:
                        pick = next(((h, t) for h, t, c in children if c == "Button" and t and
                                     t.replace("&", "").strip() not in self.NEVER), None)
                        if pick:
                            u.PostMessageW(pick[0], 0x00F5, 0, 0)
                        seen["answered"].append(f"{pick[1]!r} clicked at {age:.1f} s" if pick else
                                                f"no button left to click at {age:.1f} s")
        except Exception as exc:  # noqa: BLE001
            self.error = repr(exc)

    def report(self) -> Dict[str, Any]:
        out = super().report()
        for w, s in zip(out["windows"], self._seen.values()):
            w["first_s"] = round(s["first"] - self._t0, 2)
        return out


def standing(pid: int, baseline: Sequence[int] = ()) -> List[Dict[str, Any]]:
    """Every visible top-level window of the process not in ``baseline``, with its title, class and child texts."""
    watch = ModesWatch(pid, "standing", [])
    try:
        return [watch.describe(h) for h in watch._windows() if h not in set(baseline)]  # noqa: SLF001
    except Exception as exc:  # noqa: BLE001
        return [{"error": repr(exc)}]


# -- the probe ------------------------------------------------------------------------------------------------------

@probe("w8_over_defined_show", needs=("motion_enums", "end_to_end", "layout_planes", "axis_through_named_planes",
                                      "layout_assembly_reopen"), tier=11,
       members=("IModelDoc2.ShowConfiguration2 over-defined", "IFeature.IsSuppressed2 listed order",
                "IDimension.GetSystemValue3 listed order", "IAssemblyDoc.AddMate5 lock per configuration"))
def w8_over_defined_show(px: Px) -> None:
    """W8-PLAN §4.2 item 1 and the read order; every reading kept in the fact ``w8_over_defined`` even when a step
    fails."""
    facts: Dict[str, Any] = {}
    try:
        _run(px, facts)
    finally:
        px.fact("w8_over_defined", facts)
    summary = {"slides": fight_reading(facts, "slides"), "coupling_and_lock": fight_reading(facts, "coupling_and_lock"),
               "suppression_order": order_of(all_reads(facts, "suppression")),
               "value_order": order_of(all_reads(facts, "value")), "truths_agree": truths_agree(facts),
               "saved_nothing": facts.get("saved_nothing")}
    px.fact("w8_over_defined_summary", summary)
    px.check(True, f"W8 over-defined show: {summary}")


class _Ctx:
    """What the run carries between steps: the document, the component handles (fetched again after every
    configuration change), the held names, the watch's log and baseline, and which mates are off where."""

    def __init__(self, px: Px, doc: Any, comps: Dict[str, Any], keys: Dict[str, str], layout: Any, layout_name: str,
                 pid: int, paths: Sequence[str], baseline: Sequence[int]) -> None:
        self.px, self.doc, self.comps, self.keys, self.layout, self.layout_name = px, doc, comps, keys, layout, layout_name
        self.pid, self.paths, self.baseline = pid, list(paths), list(baseline)
        self.log: List[Dict[str, Any]] = []
        self.off: Dict[str, set] = {}

    def watch(self, label: str) -> ModesWatch:
        return ModesWatch(self.pid, label, self.log, self.baseline)

    def on_in(self, configuration: str) -> List[str]:
        return [m for m in mate_names(self.doc) if m not in self.off.get(configuration, set())]


def _set(c: _Ctx, mate: str, suppressed: bool, configurations: Sequence[str]) -> Dict[str, Any]:
    """The house's ``SetSuppression2(action, 3, names)`` (``_cfg_suppress``), its answer kept and never trusted; each
    flag read back by a single-name ``IsSuppressed2``; the run's own record of what is off updated."""
    answer = _cfg_suppress(c.px, c.doc, mate, suppressed, list(configurations))
    for name in configurations:
        (c.off.setdefault(name, set()).add if suppressed else c.off.setdefault(name, set()).discard)(mate)
    read = {n: _single_flag(c, mate, n) for n in configurations}
    return {"answer": answer, "read": read, "took": all(v is suppressed for v in read.values())}


def _single_flag(c: _Ctx, mate: str, name: str) -> Any:
    got, value = c.px.attempt(f"IsSuppressed2(3, [{name!r}]) on {mate}",
                              lambda: call(mate_feature(c.doc, mate), "IsSuppressed2", SPECIFIED, _bstr_array([name])))
    items = _items(value) if got else None
    return bool(items[0]) if items and len(items) == 1 else (plain(value) if got else "raised")


def _items(value: Any) -> List[Any]:
    """One item per name: a bare item as one, an array wrapped once more unwrapped (swcom._per_name's rule)."""
    if isinstance(value, (list, tuple)):
        if len(value) == 1 and isinstance(value[0], (list, tuple)):
            value = value[0]
        return list(value)
    return [value]


def _dimension(c: _Ctx, mate: str) -> Any:
    dims = sc.dimensions_of(mate_feature(c.doc, mate))
    c.px.require(len(dims) == 1, f"{mate} has one dimension: {len(dims)}")
    return dims[0]


def _order_reads(c: _Ctx, flags_as_set: Mapping[str, Mapping[str, bool]],
                 values_as_set: Mapping[str, Mapping[str, float]]) -> Dict[str, Any]:
    """B: each mate in ``flags_as_set`` read by ``IsSuppressed2(3, names)`` and each slide in ``values_as_set`` by
    ``GetSystemValue3(3, names)`` with every list of ``passed_lists``; the answer kept raw (in passing order is how it
    came back), the single-name reads taken as each configuration's truth (checked against what was set), and every
    read judged by ``read_order``."""
    order = _config_names(c.doc)
    lists = passed_lists(order)
    out: Dict[str, Any] = {"document_order": order, "active": _active_config(c.doc), "suppression": {}, "value": {}}
    for mate, as_set in flags_as_set.items():
        feature = mate_feature(c.doc, mate)
        reads = []
        for passed in lists:
            got, value = c.px.attempt(f"IsSuppressed2(3, {passed}) on {mate}",
                                      lambda p=passed: call(feature, "IsSuppressed2", SPECIFIED, _bstr_array(p)))
            reads.append({"passed": passed, "answer": [bool(v) for v in _items(value)] if got else "raised"})
        out["suppression"][mate] = _judged(reads, order, dict(as_set))
    for mate, as_set in values_as_set.items():
        dim = _dimension(c, mate)
        reads = []
        for passed in lists:
            got, value = c.px.attempt(f"GetSystemValue3(3, {passed}) on {mate}",
                                      lambda p=passed: call(dim, "GetSystemValue3", SPECIFIED, _bstr_array(p)))
            reads.append({"passed": passed,
                          "answer": [round(float(v) * 1000.0, 6) for v in _items(value)] if got else "raised"})
        out["value"][mate] = _judged(reads, order, {k: round(v, 6) for k, v in as_set.items()})
    out["flags_after"] = _w8_flags(c.px, c.doc, c.paths)
    return out


def _judged(reads: List[Dict[str, Any]], order: Sequence[str], as_set: Mapping[str, Any]) -> Dict[str, Any]:
    truth = {r["passed"][0]: r["answer"][0] for r in reads
             if len(r["passed"]) == 1 and isinstance(r["answer"], list) and len(r["answer"]) == 1}
    for r in reads:
        r["verdict"] = read_order(r["answer"], r["passed"], order, truth)
    return {"as_set": dict(as_set), "truth": truth, "truth_as_set": truth == dict(as_set), "reads": reads,
            "order": order_of(reads)}


def _state(c: _Ctx, configuration: str) -> Dict[str, Any]:
    """What a shown, rebuilt configuration reads through fresh handles: where S stands; every mate's flag here
    (``IsSuppressed2`` this configuration) and error code; the codes of the mates on here; every component's
    constrained status; the app's own ``Session.mate_states`` and its mate check's sentences (``swbuild._mate_problems``
    on the mates on here, AddMate5 statuses not read); What's Wrong; every ``GetSaveFlag``."""
    from .. import swbuild  # noqa: PLC0415
    from .p8_motion import mate_errors  # noqa: PLC0415
    px, doc = c.px, c.doc
    out: Dict[str, Any] = {"active": _active_config(doc)}
    got, frames = px.attempt("frames through fresh handles", lambda: _frames(c.comps))
    out["S_z"] = round(frames["S"][1][2], 9) if got else "raised"
    out["this_configuration"] = {m: is_suppressed(px, mate_feature(doc, m)) for m in mate_names(doc)}
    out["codes"] = mate_errors(px, doc)
    out["errors_on"] = {m: e for m, e in out["codes"].items()
                        if (e.get("code") not in (0, None) or "error" in e) and not out["this_configuration"].get(m)}
    out["errors_suppressed"] = {m: e for m, e in out["codes"].items()
                                if e.get("code") not in (0, None) and out["this_configuration"].get(m)}
    out["constrained"] = {k: constrained(px, comp) for k, comp in c.comps.items()}
    got, states = px.attempt("swcom.Session.mate_states", lambda: [
        {"name": s.name, "code": s.code, "warning": s.warning, "suppressed": s.suppressed}
        for s in px.session.mate_states()])
    out["app_mate_states"] = states if got else "raised"
    on_here = c.on_in(configuration)
    out["on_here_by_the_run"] = on_here
    got, checked = px.attempt("swbuild._mate_problems on the mates on here",
                              lambda: swbuild._mate_problems(px.session, on_here, False)[0])  # noqa: SLF001
    out["app_problems"] = list(checked) if got else "raised"
    out["whats_wrong"] = whats_wrong(px, doc)
    out["flags"] = _w8_flags(px, doc, c.paths)
    return out


def _shown(c: _Ctx, name: str, label: str) -> Dict[str, Any]:
    """``ShowConfiguration2(name)`` and the top-only rebuild, each under its own watch; the active name and the save
    flags between; every handle fetched again; then ``_state``; what is standing before and after."""
    px, doc = c.px, c.doc
    out: Dict[str, Any] = {"label": label, "standing_before": standing(c.pid, c.baseline)}
    with c.watch(f"{label}: ShowConfiguration2({name})") as w:
        got, value = px.attempt(f"ShowConfiguration2({name})", lambda: call(doc, "ShowConfiguration2", name))
    out["show"] = {"call": w.label, "returned": plain(value) if got else "raised", "windows": w.report()["windows"],
                   "standing_at_entry": w.standing}
    out["active_after_show"] = _active_config(doc)
    out["flags_after_show"] = _w8_flags(px, doc, c.paths)
    out["rebuild"] = _rebuild(c, f"{label}: ForceRebuild3({TOP_ONLY}) in {name}")
    c.layout, refreshed = _w8_refresh(px, doc, c.comps, c.keys, c.layout, c.layout_name)
    out["held_transform_none"] = refreshed.get("old_transform_none")
    out["fresh_transform_none"] = refreshed.get("new_transform_none")
    out.update(_state(c, name))
    out["standing_after"] = standing(c.pid, c.baseline)
    return out


def _rebuild(c: _Ctx, label: str) -> Dict[str, Any]:
    with c.watch(label) as w:
        r = rebuild(c.px, c.doc, label, top_only=TOP_ONLY)
    return dict(r, call=w.label, windows=w.report()["windows"], standing_at_entry=w.standing)


def _select_component(c: _Ctx, key: str, append: bool) -> bool:
    """``SelectByID2("<component>@<assembly>", "COMPONENT")`` by the name held from before any configuration change,
    mark 1 (a lock's), judged by the selection count."""
    asm = os.path.splitext(str(call(c.doc, "GetTitle")))[0]
    if not append:
        call(c.doc, "ClearSelection2", True)
    before = sc.selected_count(c.doc)
    c.px.attempt(f"SelectByID2 {c.keys[key]}@{asm} COMPONENT",
                 lambda: call(sc.extension(c.doc), "SelectByID2", f"{c.keys[key]}@{asm}", "COMPONENT", 0.0, 0.0, 0.0,
                              append, 1, sc.null(), 0))
    return sc.selected_count(c.doc) > before


def _run(px: Px, facts: Dict[str, Any]) -> None:
    from .. import swbuild  # noqa: PLC0415
    from ..workbook import assess as wb_assess  # noqa: PLC0415
    from .p4_nonparallel import origin_name  # noqa: PLC0415
    from .p7_workbook import _doc_at  # noqa: PLC0415
    from .p8_motion import layout_part  # noqa: PLC0415

    started = time.monotonic()
    root = os.path.join(_folder(px), "w8modes")
    px.require(not os.path.exists(root), f"{root} does not exist yet")
    os.makedirs(root)
    got, pid = px.attempt("ISldWorks.GetProcessID", lambda: call(sc.app(px), "GetProcessID"))
    px.require(got and isinstance(pid, int), "GetProcessID answers")
    baseline_windows = ModesWatch(pid, "baseline", [])._windows()  # noqa: SLF001
    facts["standing_at_start"] = standing(pid)
    built = _app_build(px, w8_parts_spec(root), swbuild, wb_assess)
    gear_path, sleeve_path = built["part_of"]["Anchor"], built["part_of"]["Sleeve"]
    x, y = W8_AXIS_XY
    layout_path = layout_part(px, root, f"{TAG} Layout", [("A", x, y), ("D", x, y)])
    paths = [layout_path, gear_path, sleeve_path]
    facts["standing_after_the_parts"] = standing(pid, baseline_windows)
    disk_before = _disk(paths)
    asm_doc: List[Any] = [None]
    c: Optional[_Ctx] = None
    try:
        for p in (gear_path, sleeve_path):
            open_by_path(px, p, prefer="OpenDoc6")
        asm = Assembly(px, layout_path, {"gear": gear_path, "sleeve": sleeve_path})
        asm.open()
        doc, layout = asm.doc, asm.layout
        asm_doc[0] = doc
        asm.add("A", "gear", 1, 0.0, (x, y, W8_A_Z))
        asm.add("D", "gear", 1, 0.0, (x, y, W8_D_Z))
        asm.add("S", "sleeve", 1, W8_S_PHASE, (x, y, W8_A_Z))
        comps = asm.gears
        _spike_mount(px, doc, comps["A"], layout, "A Axis", layout, W8_A_Z, "A")
        _spike_mount(px, doc, comps["D"], layout, "D Axis", layout, W8_D_Z, "D")
        px.require(unfix(px, doc, comps["S"]), "S floats")
        px.require(bool(_mate_axes(px, doc, comps["S"], "Gear Axis", layout, "A Axis", "S on A Axis").get("name")),
                   "S is on A Axis")
        keys = asm.names()
        layout_name = str(call(layout, "Name2"))
        _W8.clear()
        _W8.update(gear=_plane_names(comps["A"])[1], layout=_plane_names(layout)[2], front=_plane_names(layout)[0],
                   origin=origin_name(_doc_at(px, sleeve_path)), names=dict(keys), layout_name=layout_name)
        rebuild(px, doc, "mounted", top_only=TOP_ONLY)
        for a, b, name in (("S", "A", SPLINE), ("S", "D", COUPLING)):
            made = _w8_gear_mate(px, doc, comps, a, b, name, False)
            if made.get("read", {}).get("w5_says_same_way") is False:
                delete_mate(px, doc, name)
                made = _w8_gear_mate(px, doc, comps, a, b, name, True)
            facts[f"{name}: flip"] = made.get("flip")
            px.require(made.get("read", {}).get("w5_says_same_way") is True, f"{name} reads right: {made}")

        def s_origin_and_front() -> bool:
            return _w8_select(px, doc, f"Point1@{_W8['origin']}", keys["S"], "EXTSKETCHPOINT", False) and \
                _w8_select(px, doc, _W8["front"], layout_name, "PLANE", True)

        px.require(s_origin_and_front(), "S's origin and Front select")
        made = add_mate(px, doc, SLIDE, _enums(px)["distance"], _enums(px)["closest"], distance=SLIDE_VALUES["Default"])
        px.require(bool(made.get("name")), f"the slide is made: {made}")
        _rename(px, mate_feature(doc, made["name"]), SLIDE)
        rebuild(px, doc, "built", top_only=TOP_ONLY)
        facts["built"] = {"S_z": round(_frames(comps)["S"][1][2], 9), "mates": mate_names(doc),
                          "codes": {m: error_code(px, mate_feature(doc, m)) for m in mate_names(doc)},
                          "flags": _w8_flags(px, doc, paths)}
        c = _Ctx(px, doc, comps, keys, layout, layout_name, pid, paths, baseline_windows)

        # The configurations, X, Z, Y in that order, each add watched; one rebuild before any flag (SUPPRESSION_RIGHT_AFTER_ADD).
        cm = call(doc, "ConfigurationManager")
        template = _active_config(doc)
        facts["template"] = template
        for name in CONFIGS_ADDED:
            with c.watch(f"AddConfiguration2({name})") as w:
                px.attempt(f"AddConfiguration2({name})",
                           lambda n=name: call(cm, "AddConfiguration2", n, "", "", 0, "", "", True))
            facts[f"add {name}"] = {"active": _active_config(doc), "windows": w.report()["windows"]}
            c.layout, _h = _w8_refresh(px, doc, c.comps, keys, c.layout, layout_name)
        rebuild(px, doc, "configurations added", top_only=TOP_ONLY)
        order = _config_names(doc)
        facts["document_order"] = order
        px.require(sorted(order) == sorted([template, *CONFIGS_ADDED]), f"four configurations: {order}")
        coupling_on = [n for n in order if n != OTHER]
        facts["coupling set"] = {"on": _set(c, COUPLING, False, coupling_on), "off": _set(c, COUPLING, True, [OTHER])}
        slide_dim = _dimension(c, SLIDE)
        facts["slide set"] = {n: _sv_set(px, slide_dim, SLIDE_VALUES[n], [n]) for n in order}
        rebuild(px, doc, "flags and values set", top_only=TOP_ONLY)
        coupling_flags = {n: n == OTHER for n in order}
        slide_values = {n: SLIDE_VALUES[n] for n in order}
        reads: Dict[str, Any] = {}
        facts["read_order"] = reads
        reads["before the fight"] = _order_reads(c, {COUPLING: coupling_flags}, {SLIDE: slide_values})

        # A, the slides: the second made in Y with the first off there around the make; then on in Z only.
        slides: Dict[str, Any] = {"configuration": FIGHT, "other": OTHER, "other_at": SLIDE_VALUES[OTHER],
                                  "back_at": SLIDE_VALUES[FIGHT]}
        facts["slides"] = slides
        slides["made_in"] = _active_config(doc)
        slides["first off in Y for the make"] = _set(c, SLIDE, True, [OTHER])
        rebuild(px, doc, "first slide off in Y", top_only=TOP_ONLY)
        px.require(s_origin_and_front(), "S's origin and Front select for the second slide")
        with c.watch("AddMate5 the second slide") as w:
            second = add_mate(px, doc, SECOND, _enums(px)["distance"], _enums(px)["closest"], distance=SECOND_SLIDE)
        slides["second made"] = dict(second, windows=w.report()["windows"])
        px.require(bool(second.get("name")), f"the second slide is made: {second}")
        _rename(px, mate_feature(doc, second["name"]), SECOND)
        slides["second's flags as made"] = {n: _single_flag(c, SECOND, n) for n in order}
        for n in order:
            c.off.setdefault(n, set())
        slides["second off but in Z"] = _set(c, SECOND, True, [n for n in order if n != FIGHT])
        slides["second on in Z"] = _set(c, SECOND, False, [FIGHT])
        slides["first back on in Y"] = _set(c, SLIDE, False, [OTHER])
        second_dim = _dimension(c, SECOND)
        slides["second's value set"] = {n: _sv_set(px, second_dim, SECOND_SLIDE, [n]) for n in order}
        slides["Y after the make"] = {"rebuild": _rebuild(c, "Y after the second slide's make")}
        slides["Y after the make"].update(_state(c, OTHER))
        second_flags = {n: n != FIGHT for n in order}
        reads["second slide set"] = _order_reads(c, {COUPLING: coupling_flags, SECOND: second_flags},
                                                 {SLIDE: slide_values})
        slides["into"] = _shown(c, FIGHT, "into the fight")
        slides["after"] = _shown(c, OTHER, "the other configuration after it")
        slides["also"] = _shown(c, ALSO, "a third configuration")
        slides["again"] = _shown(c, FIGHT, "into the fight again")
        slides["second off in Z"] = _set(c, SECOND, True, [FIGHT])
        back = {"rebuild": _rebuild(c, "Z with the second slide off")}
        c.layout, _h = _w8_refresh(px, doc, c.comps, keys, c.layout, layout_name)
        back.update(_state(c, FIGHT))
        back["show"] = None
        slides["back"] = back

        # A, the coupling and a lock across the same pair: the lock made in Y (the coupling off there), on in Y only;
        # the coupling turned on in Y from X; Y shown.
        lock: Dict[str, Any] = {"configuration": OTHER, "other": ALSO, "other_at": SLIDE_VALUES[ALSO],
                                "back_at": SLIDE_VALUES[OTHER]}
        facts["coupling_and_lock"] = lock
        lock["to Y"] = _shown(c, OTHER, "Y, for the lock's make")
        selected = _select_component(c, "S", False) and _select_component(c, "D", True)
        lock["selected by name"] = selected
        if not selected:
            lock["selected by fresh handles"] = select_components(px, doc, [c.comps["S"], c.comps["D"]])
        with c.watch("AddMate5 the lock") as w:
            made = add_mate(px, doc, LOCK, _enums(px)["lock"], _enums(px)["closest"])
        lock["made"] = dict(made, windows=w.report()["windows"])
        if made.get("name"):
            _rename(px, mate_feature(doc, made["name"]), LOCK)
            lock["flags as made"] = {n: _single_flag(c, LOCK, n) for n in order}
            lock["off but in Y"] = _set(c, LOCK, True, [n for n in order if n != OTHER])
            lock["on in Y"] = _set(c, LOCK, False, [OTHER])
            lock["Y with the lock alone"] = {"rebuild": _rebuild(c, "Y with the lock alone")}
            lock["Y with the lock alone"].update(_state(c, OTHER))
            lock_flags = {n: n != OTHER for n in order}
            reads["lock set"] = _order_reads(c, {COUPLING: coupling_flags, SECOND: {n: True for n in order},
                                                 LOCK: lock_flags}, {SLIDE: slide_values})
            lock["to X"] = _shown(c, ALSO, "X, to turn the coupling on in Y")
            lock["coupling on in Y"] = _set(c, COUPLING, False, [OTHER])
            lock["into"] = _shown(c, OTHER, "into the coupling beside the lock")
            lock["after"] = _shown(c, ALSO, "X after it")
            lock["again"] = _shown(c, OTHER, "into the coupling beside the lock again")
            lock["lock off in Y"] = _set(c, LOCK, True, [OTHER])
            back = {"rebuild": _rebuild(c, "Y with the lock off")}
            c.layout, _h = _w8_refresh(px, doc, c.comps, keys, c.layout, layout_name)
            back.update(_state(c, OTHER))
            back["show"] = None
            lock["back"] = back
        else:
            lock["not tried"] = "the lock would not make"
    finally:
        if c is not None:
            facts["watched_calls"] = c.log
        facts["standing_before_close"] = standing(pid, baseline_windows)
        facts["closes"] = _close_all(px, asm_doc[0], paths, pid)
        facts["disk_before"], facts["disk_after"] = disk_before, _disk(paths)
        facts["saved_nothing"] = facts["disk_before"] == facts["disk_after"]
        facts["standing_at_end"] = standing(pid, baseline_windows)
        facts["seconds"] = round(time.monotonic() - started, 1)


def _close_all(px: Px, doc: Any, paths: Sequence[str], pid: int) -> List[Dict[str, Any]]:
    """The never-saved assembly, then each part this probe opened, by ``CloseDoc`` under the watch (``watched_close``,
    which refuses a title the probe did not create); none saved. Whatever is still open after that is left to the
    house's close (``_close_quietly``, which saves the probe's own modified parts first) and noted."""
    from .p7_workbook import _doc_at  # noqa: PLC0415
    from .p8_motion import _close_quietly  # noqa: PLC0415
    out: List[Dict[str, Any]] = []
    titles = []
    if doc is not None:
        try:
            titles.append(str(call(doc, "GetTitle")))
        except Exception as exc:  # noqa: BLE001
            out.append({"error": f"the assembly's title: {exc}"})
    for p in paths:
        d = _doc_at(px, p)
        if d is not None:
            titles.append(str(call(d, "GetTitle")))
    for title in titles:
        try:
            out.append(watched_close(px, "CloseDoc", title, pid))
        except Exception as exc:  # noqa: BLE001 - recorded; the house close below is the fallback
            out.append({"title": title, "error": repr(exc)})
    left = [os.path.basename(p) for p in paths if _doc_at(px, p) is not None]
    if left:
        px.note(f"CLEANUP still open after CloseDoc: {left}; closing by the house's close")
        out.append({"house_close_left": _close_quietly(px, paths)})
    return out
