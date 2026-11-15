"""Probe tier 10, W7's follow-up: how a turned planetary train is put back to its built frames, and a suppressed gear
mate's sense read on an unmodified document (W8's SUPPRESSED_GEAR_MATE_SENSE_READ).

Planetary_4to1 failed in W7's full build: p3 of probe/workbook_assembly_check.py (log in bf281b8). The train was
driven +37° on the sun, so the carrier stood at 9.25°. Then an Update had to put every body back to its built frame.
``swbuild._put_train`` put the carrier first, by ``place_component``, with the gear mates on, and the carrier read
back 6.2° off its built frame. The W7 spike drove a planetary; it never put one.

Every route here starts from a fresh copy of a built, saved, un-driven Planetary_4to1, its parts beside it. The source
is E's p1 folder (GG_W7_PUT_SOURCE overrides it). It is copied once into this run's scratch folder and again from
there for every route, so no route can contaminate another. Nothing is saved over a built file, and every route's
copy is closed without saving. Every SolidWorks call goes through the app's own ``swcom.Session`` members where one
exists (``px.session``), so what is measured is what package A can call. The exceptions are the raw puts of route D
and the deleting of a mate, which the scripts make the same way.

For each route the copy is opened and every component is checked to resolve inside the copy. Then the sun is driven
+37° (W5's temporary angle mate on a global "Drive", 90 -> 127, the drive deleted after), and the probe confirms
that the carrier stands 9.25° off and every planet copy off its built frame. Then the route runs, and is judged:
- every frame, through freshly fetched handles after a top-only rebuild, within ``place_component``'s tolerance
  (1e-6 per rotation entry, 1e-6 mm) of its wanted frame;
- every gear mate's sense read right (``gear_mate_sense``);
- no interference;
- a drive of the sun by +20° after the route turns the carrier +5°, each planet copy -10° and CarrierGear +5°, and
  leaves the ring still, with no interference.
A route that leaves the frames right but the train turning wrong or stuck fails.

The routes:
- A. As the app does today: the lock off, the carrier first, then every other gear, the gear mates on.
- B. The sun alone first (does the solver carry the rest back through the gear mates?), then the rest in
  W7-INTERFACES §6.13's order.
- C. Every gear mate (and the lock) suppressed around the puts, each put read back, the gear mates turned back on.
- D. Every put made with no rebuild or read-back between them, then one rebuild.
- E. Only if B, C and D all fail: C with the planet copies' axis mates also off around the puts.
The route that held is then run again on a train turned 37° whose copies must also move 2 mm along their axes
("Planet Face Z" 5 -> 7, as p3's Planet At edit), and on a train not turned at all.
"""

from __future__ import annotations

import json
import math
import os
import shutil
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from .harness import Px, probe

SOURCE = os.environ.get("GG_W7_PUT_SOURCE",
                        r"C:\Users\M0obo\Documents\GearGeneratorProbe\w7-full-20261115-000138\out\p1")
ASSEMBLY = "Planetary_4to1.SLDASM"
RECORD = "Planetary_4to1.workbook.json"
CARRIER = "C carrier"
SUN, RING, CARRIER_GEAR = "Sun", "Ring", "CarrierGear"
COPIES = ("Planet copy 1", "Planet copy 2", "Planet copy 3")
DRIVE, DRIVE_MATE, DRIVE_FROM = "Drive", "Drive the sun", 90.0
TURN, STEP = 37.0, 20.0
TOLERANCE = 1e-6                     # place_component's: per rotation entry, and mm
PLANET_FACE, PLANET_FACE_FROM, PLANET_FACE_TO = "Planet Face Z", 5.0, 7.0
ROUTES = ("A", "B", "C", "D")
FALLBACK = "E"
ROUTE_NAMES = {"A": "carrier first, gear mates on",
               "B": "input first",
               "C": "gear mates off around the puts",
               "D": "every put, then one rebuild",
               "E": "gear mates and planet axes off around the puts"}
#: For +1° of the sun, each body's own turn (W7-PLAN §4, P_DRIVE: sun 30 -> carrier 7.5, copies -15, ring 0).
RATIOS = dict({SUN: 1.0, CARRIER: 0.25, CARRIER_GEAR: 0.25, RING: 0.0}, **{c: -0.5 for c in COPIES})


# -- pure ---------------------------------------------------------------------------------------------------------

def wanted_frames(record: Mapping[str, Any], shift_copies: float = 0.0) -> Dict[str, Tuple[List[float], List[float]]]:
    """Each body's built frame from the record (rotation by rows, origin in mm): every gear component and the
    carrier; the planet copies moved ``shift_copies`` mm along their own +Z (the third column)."""
    box = record["gearbox"]
    out: Dict[str, Tuple[List[float], List[float]]] = {}
    for c in box["components"]:
        rot, at = [float(v) for v in c["rotation"]], [float(v) for v in c["at"]]
        if c["gear"] in COPIES and shift_copies:
            z = (rot[2], rot[5], rot[8])
            at = [a + shift_copies * d for a, d in zip(at, z)]
        out[c["gear"]] = (rot, at)
    for c in box["carriers"]:
        out[f"{c['shaft']} carrier"] = ([float(v) for v in c["rotation"]], [float(v) for v in c["at"]])
    return out


def component_names(record: Mapping[str, Any]) -> Dict[str, str]:
    """Each body's component name (``Name2``), the carrier's among them."""
    box = record["gearbox"]
    names = {c["gear"]: c["name"] for c in box["components"]}
    names.update({f"{c['shaft']} carrier": c["component"] for c in box["carriers"]})
    return names


def mates_of(record: Mapping[str, Any], kind: str) -> List[Mapping[str, Any]]:
    return [m for m in record["gearbox"]["mates"] if m["kind"] == kind]


def frame_off(got: Tuple[Sequence[float], Sequence[float]], wanted: Tuple[Sequence[float], Sequence[float]]
              ) -> Tuple[float, float]:
    """(largest rotation entry off, origin off in mm), as ``place_component`` judges a put."""
    rot = max(abs(float(a) - float(b)) for a, b in zip(got[0], wanted[0]))
    at = max(abs(float(a) - float(b)) for a, b in zip(got[1], wanted[1]))
    return round(rot, 12), round(at, 9)


def own_turn_deg(before: Sequence[float], after: Sequence[float]) -> Optional[float]:
    """The turn about a body's own Z from one rotation (rows) to another, in degrees; None when it tilted."""
    from ..swbuild import turn_between  # noqa: PLC0415 - pure
    turn = turn_between(before, after)
    return None if turn is None else round(math.degrees(turn), 9)


def own_axis(rotation: Sequence[float]) -> Tuple[float, float, float]:
    return (float(rotation[2]), float(rotation[5]), float(rotation[8]))


def drive_right(turns: Mapping[str, Optional[float]], step: float, tol: float = TOLERANCE) -> Dict[str, bool]:
    """Each body's measured turn against the plan's ratios for a sun turn of ``step``."""
    return {b: (turns.get(b) is not None and abs(float(turns[b]) - r * step) < tol) for b, r in RATIOS.items()}


def judge(case: Mapping[str, Any]) -> Dict[str, Any]:
    """A route held when every frame is within tolerance, every sense reads right, nothing interferes, and the
    +20° drive afterwards turns every body as the ratios say with nothing interfering."""
    offs = case.get("frames_off") or {}
    frames = bool(offs) and all(r <= TOLERANCE and a <= TOLERANCE for r, a in offs.values())
    senses = bool(case.get("senses")) and all(s.get("right") is True for s in case["senses"].values())
    clear = case.get("clashes") == []
    drive = case.get("drive") or {}
    driven = bool(drive.get("right")) and all(drive["right"].values()) and drive.get("clashes") == []
    return {"frames": frames, "senses": senses, "clear": clear, "drive": driven,
            "held": frames and senses and clear and driven and not case.get("errors")}


def route_held(cases: Mapping[str, Mapping[str, Any]], route: str) -> bool:
    case = cases.get(route)
    return bool(case) and judge(case)["held"]


# -- SolidWorks ---------------------------------------------------------------------------------------------------

class _Copy:
    """One fresh copy of the master folder, opened through the Session, its bodies and mates kept as handles."""

    def __init__(self, px: Px, root: str, master: str, label: str) -> None:
        self.px, self.s = px, px.session
        self.folder = os.path.join(root, label)
        shutil.copytree(master, self.folder)               # copy2: mtimes kept
        with open(os.path.join(self.folder, RECORD), encoding="utf-8") as handle:
            self.record = json.load(handle)
        self.path = os.path.join(self.folder, ASSEMBLY)
        self.names = component_names(self.record)
        self.handle = {body: f"b{i}" for i, body in enumerate(self.names)}
        self.title = ""
        self.mate_handle: Dict[str, str] = {}
        self.opened = False

    def open(self) -> Dict[str, Any]:
        s = self.s
        s.begin_build()
        info = s.open_document(self.path)
        self.opened = True
        self.title = info.title
        out: Dict[str, Any] = {"title": info.title, "modified_on_open": s.has_unsaved_changes()}
        self.find()
        out["paths_outside"] = {b: s.component_path(h) for b, h in self.handle.items()
                                if not os.path.normcase(s.component_path(h)).startswith(os.path.normcase(self.folder))}
        s.find_component("lay", self.record["gearbox"]["layout_component"])
        for i, m in enumerate(self.record["gearbox"]["mates"]):
            self.mate_handle[m["name"]] = f"m{i}"
            s.find_mate(f"m{i}", m["name"])
        return out

    def find(self) -> None:
        for body, h in self.handle.items():
            self.s.find_component(h, self.names[body])

    def frames(self) -> Dict[str, Tuple[Tuple[float, ...], Tuple[float, float, float]]]:
        return {b: self.s.component_frame(h) for b, h in self.handle.items()}

    def rebuild(self) -> bool:
        from ..swcom import ASSEMBLY_TRAIN  # noqa: PLC0415
        return bool(self.s.rebuild(kind=ASSEMBLY_TRAIN))

    def close(self) -> None:
        if self.opened:
            try:
                self.s.close_document(self.title)
            finally:
                self.opened = False
                self.s.end_build()

    # -- the drive

    def _delete_mate(self, name: str) -> None:
        from .. import swcom  # noqa: PLC0415
        s = self.s
        feature = s._mate_feature(name)  # noqa: SLF001 - the scripts' delete, MATE_DELETE_ROUTE
        doc = s._doc()  # noqa: SLF001
        swcom.call(doc, "ClearSelection2", True)
        swcom.call(feature, "Select2", False, 0)
        swcom._guarded("EditDelete", lambda: doc.EditDelete())  # noqa: SLF001
        swcom.call(doc, "ClearSelection2", True)

    def _undrive(self, made: Mapping[str, Any]) -> None:
        from ..gears import equations  # noqa: PLC0415
        s = self.s
        if made.get("global"):
            texts = [text for text, _ in s.equations()]
            for index in range(len(texts) - 1, -1, -1):
                if equations.quote(DRIVE) in texts[index]:
                    s.delete_equation(index)
        if made.get("mate"):
            self._delete_mate(made["mate"])
        self.rebuild()

    def drive(self, by: float, keep: bool) -> Dict[str, Any]:
        """The sun driven ``by`` degrees by W5's temporary angle mate on the global "Drive" (its Top plane to the
        layout's Right at 90°); every body's own turn and the interference read at the driven place. ``keep``: the
        drive deleted at once, leaving the train turned (the user's turn); else read and left for the close."""
        from ..gears import equations  # noqa: PLC0415
        s = self.s
        made: Dict[str, Any] = {}
        out: Dict[str, Any] = {}
        try:
            s.add_global_variable(DRIVE, f"{DRIVE_FROM:g}")
            made["global"] = True
            name, dim = s.add_mate("ddrive", "angle", f"{self.handle[SUN]}:plane2", "lay:plane3", DRIVE_FROM,
                                   DRIVE_MATE)
            made["mate"] = name
            s.link_dimension(f"{dim}@{name}", equations.quote(DRIVE))
            self.rebuild()
            self.find()
            before = self.frames()
            s.set_global_variable(DRIVE, f"{DRIVE_FROM + by:g}")
            self.rebuild()
            self.find()
            after = self.frames()
            out["turns"] = {b: own_turn_deg(before[b][0], after[b][0]) for b in before}
            out["moved_mm"] = {b: round(math.dist(before[b][1], after[b][1]), 9) for b in before}
            out["right"] = drive_right(out["turns"], by)
            out["clashes"] = [[list(p), v] for p, v in s.interferences()]
        finally:
            if keep:
                self._undrive(made)
        return out

    # -- puts and reads

    def put(self, body: str, frame: Tuple[Sequence[float], Sequence[float]]) -> Dict[str, Any]:
        """``place_component`` (Transform2 put, the train's top-only rebuild, read back): what it raised, if
        anything, and the frame read after through a fresh fetch."""
        from ..swcom import ASSEMBLY_TRAIN  # noqa: PLC0415
        got, value = self.px.attempt(f"place_component {body}", lambda: self.s.place_component(
            self.handle[body], frame[0], tuple(frame[1]), kind=ASSEMBLY_TRAIN))
        self.find()
        return {"raised": None if got else str(value), "off": frame_off(self.frames()[body], frame)}

    def raw_put(self, body: str, frame: Tuple[Sequence[float], Sequence[float]]) -> None:
        """``place_component``'s Transform2 put alone: no rebuild, no read-back (route D)."""
        import pythoncom  # noqa: PLC0415
        from win32com.client import VARIANT, dynamic  # noqa: PLC0415
        from .. import swcom  # noqa: PLC0415
        s = self.s
        component = s.raw_component(self.handle[body])
        columns = [float(frame[0][i * 3 + j]) for j in range(3) for i in range(3)]
        data = columns + [v / 1000.0 for v in frame[1]] + [1.0, 0.0, 0.0, 0.0]
        utility = swcom.call(s._app, "GetMathUtility")  # noqa: SLF001
        ole = utility._oleobj_  # noqa: SLF001
        raw = ole.Invoke(ole.GetIDsOfNames("CreateTransform"), 0, pythoncom.DISPATCH_METHOD, True,
                         VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, data))
        transform = raw if hasattr(raw, "ArrayData") else dynamic.Dispatch(raw)
        swcom._put(component, "Transform2", transform)  # noqa: SLF001

    def suppress(self, names: Sequence[str], on: bool) -> Dict[str, Any]:
        out = {}
        for n in names:
            got, value = self.px.attempt(f"set_mate_suppressed {n} {on}",
                                         lambda n=n: self.s.set_mate_suppressed(self.mate_handle[n], on))
            out[n] = None if got else str(value)
        return out

    def senses(self) -> Dict[str, Any]:
        """Every gear mate's sense by the app's read (``gear_mate_sense``) against its gears' own axes as placed."""
        self.find()
        frames = self.frames()
        out = {}
        for m in mates_of(self.record, "mesh"):
            a, b = m["gears"]
            got, value = self.px.attempt(f"gear_mate_sense {m['name']}", lambda m=m, a=a, b=b: self.s.gear_mate_sense(
                self.mate_handle[m["name"]], m["sense"] > 0, (own_axis(frames[a][0]), own_axis(frames[b][0]))))
            out[m["name"]] = {"right": bool(value[0]), "tau": list(value[1])} if got else {"raised": str(value)}
        return out

    def ratios(self) -> Dict[str, Any]:
        return {m["name"]: list(self.s.gear_mate_ratio(self.mate_handle[m["name"]])) for m in mates_of(self.record, "mesh")}

    def flags(self) -> Dict[str, Optional[bool]]:
        """GetSaveFlag of the assembly (the Session's member) and of each part through its component."""
        from .. import swcom  # noqa: PLC0415
        out: Dict[str, Optional[bool]] = {"assembly": self.s.has_unsaved_changes()}
        for body, h in self.handle.items():
            doc = swcom.call(self.s.raw_component(h), "GetModelDoc2")
            out[body] = None if doc is None else bool(swcom.call(doc, "GetSaveFlag"))
        return out

    def state(self, wanted: Mapping[str, Tuple[Sequence[float], Sequence[float]]]) -> Dict[str, Any]:
        """After a top-only rebuild, through fresh handles: every frame against ``wanted``, every sense, the
        interference."""
        self.rebuild()
        self.find()
        frames = self.frames()
        return {"frames_off": {b: frame_off(frames[b], wanted[b]) for b in wanted},
                "senses": self.senses(),
                "clashes": [[list(p), v] for p, v in self.s.interferences()]}


def _route(c: _Copy, route: str, wanted: Mapping[str, Tuple[Sequence[float], Sequence[float]]]) -> Dict[str, Any]:
    """The puts of one route; what each step read back."""
    locks = [m["name"] for m in mates_of(c.record, "lock")]
    gear_mates = [m["name"] for m in mates_of(c.record, "mesh")]
    axes = [m["name"] for m in mates_of(c.record, "axis") if m["gears"] and m["gears"][0] in COPIES]
    held = list(c.record["gearbox"]["fixed"])
    rest = [b for b in wanted if b not in held]
    order = [b for b in rest if b == CARRIER] + [b for b in rest if b != CARRIER]      # §6.13 after the held
    out: Dict[str, Any] = {"order": order, "puts": {}}
    c.find()
    live = c.frames()
    for body in held:                                    # a held body is put only when it is off (whole pitches aside)
        off = frame_off(live[body], wanted[body])
        out.setdefault("held_off", {})[body] = off
    off_names = list(locks)
    if route in ("C", "E"):
        off_names += gear_mates
    if route == "E":
        off_names += axes
    out["suppressed"] = c.suppress(off_names, True)
    c.rebuild()
    try:
        if route == "B":
            out["puts"][SUN] = c.put(SUN, wanted[SUN])
            out["after_sun_alone"] = c.state(wanted)
            for body in [b for b in order if b != SUN]:
                out["puts"][body] = c.put(body, wanted[body])
        elif route == "D":
            for body in [CARRIER] + [b for b in order if b in COPIES] + [b for b in order if b not in COPIES and
                                                                       b != CARRIER]:
                c.raw_put(body, wanted[body])
            c.rebuild()
            c.find()
            got = c.frames()
            out["after_one_rebuild"] = {b: frame_off(got[b], wanted[b]) for b in wanted}
        else:
            for body in order:
                out["puts"][body] = c.put(body, wanted[body])
        if route in ("C", "E"):
            c.rebuild()
            out["ratios_before_back_on"] = c.ratios()
            out["flags_before_back_on"] = c.flags()
    finally:
        out["back_on"] = c.suppress(list(reversed(off_names)), False)
        c.rebuild()
    if route in ("C", "E"):
        out["ratios_after_back_on"] = c.ratios()
        out["flags_after_back_on"] = c.flags()
    return out


def _case(px: Px, root: str, master: str, route: str, scenario: str) -> Dict[str, Any]:
    """One route on one fresh copy: opened, driven (or not), edited (or not), the route, judged, driven +20°."""
    label = f"{route}-{scenario}"
    c = _Copy(px, root, master, label)
    case: Dict[str, Any] = {"route": route, "scenario": scenario, "errors": []}
    try:
        case["open"] = c.open()
        if case["open"]["paths_outside"]:
            raise RuntimeError(f"components resolve outside the copy: {case['open']['paths_outside']}")
        built = wanted_frames(c.record)
        c.find()
        case["at_open_off"] = {b: frame_off(f, built[b]) for b, f in c.frames().items()}
        if scenario in ("turned", "turned and moved"):
            case["turn"] = c.drive(TURN, keep=True)
            c.find()
            now = c.frames()
            case["turned_off"] = {b: frame_off(now[b], built[b]) for b in built}
            case["carrier_turned"] = own_turn_deg(built[CARRIER][0], now[CARRIER][0])
            px.require(case["carrier_turned"] is not None and abs(case["carrier_turned"] - TURN / 4) < 1e-6,
                       f"{label}: the carrier stands {TURN / 4}° off after the user's turn: {case['carrier_turned']}")
            px.require(all(case["turned_off"][b][0] > 1e-3 for b in COPIES),
                       f"{label}: every planet copy is off its built frame: {case['turned_off']}")
        wanted = built
        if scenario == "turned and moved":
            c.s.set_global_variable(PLANET_FACE, f"{PLANET_FACE_TO:g}")
            case["face_global"] = (PLANET_FACE, PLANET_FACE_FROM, PLANET_FACE_TO)
            wanted = wanted_frames(c.record, PLANET_FACE_TO - PLANET_FACE_FROM)
        case["flags_before"] = c.flags()
        case["steps"] = _route(c, route, wanted)
        case.update(c.state(wanted))
        case["flags_after"] = c.flags()
        case["drive"] = c.drive(STEP, keep=False)
    except Exception as exc:  # noqa: BLE001 - kept: a route that raised failed, and the next one starts afresh
        case["errors"].append(f"{type(exc).__name__}: {exc}")
    finally:
        try:
            c.close()
        except Exception as exc:  # noqa: BLE001
            case["errors"].append(f"close: {type(exc).__name__}: {exc}")
    case["verdict"] = judge(case)
    px.note(f"{label}: {case['verdict']}; errors {case['errors']}")
    return case


def _suppressed_read(px: Px, root: str, master: str) -> Dict[str, Any]:
    """W8's SUPPRESSED_GEAR_MATE_SENSE_READ on an unmodified document: one gear mate suppressed, the copy saved,
    closed and reopened; that mate's sense read as Update reads it (``swbuild._sense_read``) and the modified flag
    read before, after one read and after a second; then the same on a mate left on (the control)."""
    from .. import swbuild  # noqa: PLC0415
    from .p7_workbook import _save_in_place  # noqa: PLC0415
    c = _Copy(px, root, master, "suppressed-read")
    out: Dict[str, Any] = {"errors": []}
    target, control = "Planet copy 1 meshes Ring", "Sun meshes Planet copy 2"
    meshes = {m["name"]: m for m in mates_of(c.record, "mesh")}

    def read(name: str) -> Dict[str, Any]:
        m = meshes[name]
        a, b = m["gears"]
        c.find()
        frames = c.frames()
        raw = px.attempt(f"gear_mate_sense {name}", lambda: c.s.gear_mate_sense(
            c.mate_handle[name], m["sense"] > 0, (own_axis(frames[a][0]), own_axis(frames[b][0]))))
        app = px.attempt(f"swbuild._sense_read {name}", lambda: swbuild._sense_read(
            c.s, c.mate_handle[name], name, m["sense"] > 0, own_axis(frames[a][0]), own_axis(frames[b][0]), a, b,
            RuntimeError, (frames[a][1], frames[b][1])))
        return {"raw": [bool(raw[1][0]), list(raw[1][1])] if raw[0] else f"raised {raw[1]}",
                "app": bool(app[1]) if app[0] else f"raised {app[1]}"}

    try:
        out["open"] = c.open()
        out["before_suppressing"] = {n: read(n) for n in (target, control)}
        out["suppress"] = c.suppress([target], True)
        c.rebuild()
        out["saved"] = _save_in_place(px, c.s._doc(), c.path, "the suppressed-read copy")  # noqa: SLF001
        c.close()
        out["reopen"] = c.open()
        out["modified_on_reopen"] = out["reopen"]["modified_on_open"]
        out["suppressed_reads_suppressed"] = px.attempt("is the mate suppressed", lambda: c.s._is_suppressed(  # noqa: SLF001
            c.s._kept_mate(c.mate_handle[target])[1]))[1]  # noqa: SLF001
        for name, key in ((target, "suppressed"), (control, "control")):
            first = read(name)
            flag1 = c.s.has_unsaved_changes()
            second = read(name)
            flag2 = c.s.has_unsaved_changes()
            out[key] = {"mate": name, "first": first, "modified_after_first": flag1, "second": second,
                        "modified_after_second": flag2}
    except Exception as exc:  # noqa: BLE001
        out["errors"].append(f"{type(exc).__name__}: {exc}")
    finally:
        try:
            c.close()
        except Exception as exc:  # noqa: BLE001
            out["errors"].append(f"close: {type(exc).__name__}: {exc}")
    return out


@probe("planetary_put_back", needs=("motion_enums",), tier=10,
       members=("swcom.Session.place_component planetary", "swcom.Session.set_mate_suppressed gear mates",
                "swcom.Session.gear_mate_sense suppressed"))
def planetary_put_back(px: Px) -> None:
    """W7's follow-up: which route puts a turned planetary back to its built frames (A, B, C, D, then E only if B,
    C and D all fail), the route that held run again with the copies moved along their axes and with the train not
    turned; and a suppressed gear mate's sense read on an unmodified document."""
    from .p8_motion import _folder  # noqa: PLC0415
    px.require(os.path.isfile(os.path.join(SOURCE, ASSEMBLY)) and os.path.isfile(os.path.join(SOURCE, RECORD)),
               f"the built gearbox to copy is there: {SOURCE}")
    open_paths = [d.path for d in px.session.documents()]
    px.require(not any(os.path.normcase(p).startswith(os.path.normcase(SOURCE)) for p in open_paths if p),
               f"nothing of the source folder is open in SolidWorks: {open_paths}")
    root = os.path.join(_folder(px), "w7put")
    px.require(not os.path.exists(root), f"{root} does not exist yet")
    os.makedirs(root)
    master = os.path.join(root, "master")
    shutil.copytree(SOURCE, master)
    facts: Dict[str, Any] = {"source": SOURCE, "cases": {}}
    try:
        for route in ROUTES:
            facts["cases"][f"{route} turned"] = _case(px, root, master, route, "turned")
        turned = {r: facts["cases"][f"{r} turned"] for r in ROUTES}
        if not any(route_held(turned, r) for r in ("B", "C", "D")):
            facts["cases"][f"{FALLBACK} turned"] = _case(px, root, master, FALLBACK, "turned")
            turned[FALLBACK] = facts["cases"][f"{FALLBACK} turned"]
        held = next((r for r in ("B", "C", "D", FALLBACK, "A") if route_held(turned, r)), None)
        facts["held_turned"] = held
        if held:
            for scenario in ("turned and moved", "not turned"):
                facts["cases"][f"{held} {scenario}"] = _case(px, root, master, held, scenario)
        facts["suppressed_read"] = _suppressed_read(px, root, master)
    finally:
        px.fact("planetary_put_back", facts)
    px.check(True, f"planetary put-back: held when turned {facts.get('held_turned')}; "
                   f"{ {k: v['verdict'] for k, v in facts['cases'].items()} }")
