r"""W9d's demonstration, M9 (ISSUE-1-PLAN §5 "W9d", §4 M9, §2.5; W9D-INTERFACES.md §15): Build again… carries the user's
work into the new revision, on SolidWorks, through the Workbook window's own path (W9a's Desk9, its build restated as
the window's ``_start_build`` now runs it: ``old_assembly`` as ``before`` and ``carry_for`` as ``carry``). The note is
``docs/notes-workbook/W9D-DEMONSTRATION.md``.

    python w9d_demonstration.py <src> <out> --pid PID [--log FILE] [--sections fixture,carry-gates,...] [--redo]
        [--master <S0's rangebox.master>] [--user-master <W9a's setup.master>]
        [--fixture-master <this script's w9d-fixture.master>] [--other-version-file <a file the other SolidWorks saved>]
    python w9d_demonstration.py --self-check      (no SolidWorks, no Excel)

It runs W9a's script's ``main`` with its own sections (as W9b's and W9c's do), so it inherits the attach and PID
check, the dialog watch with the What's Wrong rule per version, keep-awake, the JSON after every section, APPDATA in
the run folder, the guarded close, ``--sections`` and ``--redo``. Every edit is typed in Excel by W8's ``edit``; every
press goes through Desk9. No document title but the run's own is logged, and SolidWorks' frame never is.

Every W9d write gate is None in findings.py (``CARRY_INSERTS``, ``CARRY_INSERTS_IN_A_CONFIGURATION``,
``CARRY_REMAKE_KINDS``, ``CARRY_GEAR_MATE_ON_AN_APP_GEAR``) and so is the read ``REFERENCED_CONFIGURATION_READ``, each
``_ON_<year>``. ``carry-gates`` shows the app's refusal with them as they stand (the press carries nothing and names
everything), then each gate's own refusal on SolidWorks' own read; ``carry`` and ``carry-closed`` patch them in this
process only (``PATCH``, put back after) and measure; a section proposes (``propose``) and never sets.

Sections (each runs alone from a kept master; ``fixture`` keeps ``w9d-fixture.master`` for the other three):

- ``fixture``      W9a's setup.master (RangeBox, Sprocket-1..4, Housing-1, the User Keyway in Sun's part) with §15's
                   additions: Chain-1 on Input Axis by its axis and a distance to Sprocket-1 (cluster one, with the
                   setup's sprockets on Sun); Chain-2 by its bore (concentric) and an end face on Chain-1's (face
                   mates); Housing-2 on the layout's planes (coincident, distance, parallel: cluster two); Sprocket-5's
                   end face on Sun's end face; Sprocket-6 gear-mated on Sun's Gear Axis, and a distance to the
                   assembly's own Front plane; Sprocket-7 suppressed in L; Sprocket-8 locked to Sun and to the fixed
                   Housing-1 (the tie); Sprocket-9 suppressed in H, the mode showing; Sprocket-10 gear-mated on a root
                   cylinder of Sun, Sprocket-11 on a root fillet, a limit distance between them; SprocketLight-1 (a
                   file of its own, set lightweight later, in ``carry`` only); SprocketConf-1 in its file's second
                   configuration Z20. Saved with H showing, a quiet press records the inventory, kept. About 15 min.
- ``carry-gates``  the edit (Sun's Flank to arcs, a shaft Aux with a gear on it) typed in Excel; the question; Build
                   again… with every write gate as it stands: RangeBox_r2 built and saved as today, nothing carried,
                   everything named, nothing written to the old assembly or a user file; each gate's own refusal
                   shown by plan_carry on the read the press made. About 12 min.
- ``carry``        the Done-when, the old assembly open with H showing (SprocketLight-1 set lightweight first): the
                   gates patched; the question read and held to what happens; the press; both clusters carried and
                   placed against their anchors, every state per mode and every remade mate read back, the Sun
                   end-face mate and the root-fillet gear mate named as on a part made new, the keyway named, the tied
                   cluster fallen back alone, every app gear free in every mode, interference per mode, the carried
                   items unsaved and nothing saved after the first save; the record at schema 10; then the user saves
                   RangeBox_r2 and the footer's line goes. About 35 min.
- ``carry-closed`` the old assembly saved with L showing and nothing lightweight, then closed: the not-open read (R.2)
                   under its conditions, RangeSlv's train read in L and placed in H, the mate to the assembly's plane
                   and SprocketLight-1's mate made again; the R.2 refusals by closed-file reads (another version's file
                   with ``--other-version-file``); then RangeBox_r2 closed unsaved and a later Update says the carry
                   was lost. About 20 min.

About 1 h 20 min on 2026 (the plan's 1 h 15 min), 5 min more if setup.master must be built first.
"""

import dataclasses
import hashlib
import json
import os
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SELF_CHECK = "--self-check" in sys.argv

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    raise SystemExit(0)

# -- the plan's numbers ------------------------------------------------------------------------------------------------

MODES = ("H", "N", "L")
SHEETS = ("Shafts", "Gears", "Meshes", "Modes")       # the edit adds a shaft, so W9c's three sheets and Shafts
AUX_SHAFT = dict(id="Aux", mounted_on="frame", x="80", y="0", z="0", axis="Z+")
AUX_GEAR = ("Aux", "Aux", "10.5", "spur", "20", "1.25", "6")     # a gear on the new shaft, meshing nothing
SUN_FLANK = "arcs"                                    # D18: a mixed-flank mesh is legal; Sun's part is made new
CONF = "Z20"                                          # SprocketConf.SLDPRT's second configuration
KIND_WORDS = ("coincident", "concentric", "parallel", "perpendicular", "tangent", "distance", "angle",
              "limit distance", "limit angle", "lock", "gear")       # swbuild.CARRY_KIND_WORDS (pinned equal)
# The write gates M9 sets, and the read it sets (§8): patched to these in this process for the measurement only.
WRITE_GATES = {"CARRY_INSERTS": True, "CARRY_INSERTS_IN_A_CONFIGURATION": True, "REFERENCED_CONFIGURATION_READ": True,
               "CARRY_REMAKE_KINDS": KIND_WORDS, "CARRY_GEAR_MATE_ON_AN_APP_GEAR": True}
# The ones that stay None after M9, each with why (§8, §8.1).
STAY_NONE = {
    "CARRY_INSERTS_A_SUBASSEMBLY": "no user sub-assembly in M9's fixture; a sub-assembly would go in by "
                                   "open_document + add_component, not the measured read-only insert (W9D-REVIEW-A)",
    "CARRY_REMAKES_ON_A_LEAF": "no target grammar for a leaf is written (package A names every leaf mate)",
    "VIRTUAL_READ": "no virtual component in the fixture; IsVirtual is never read by the worker",
    "PATTERN_INSTANCE_READ": "no component pattern in the fixture; IsPatternInstance is never read by the worker",
    "ORIGIN_ENTITY_READ": "no mate on an origin in the fixture; no route for one is written",
    "PERSIST_REFERENCE_ROUTE_FOR_VERTICES": "no mate on a vertex in the fixture"}
SUPPRESSED, LIGHTWEIGHT, RESOLVED = 0, 1, 2          # swComponentSuppressionState_e
POSE_TOL = 1e-6                                       # mm and rotation entries: a pose against its anchor kept
VALUE_TOL = 1e-9                                      # m, rad: a remade mate's value against the old one
I9 = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

# The fixture: W9a's setup (u1..u4 Sprocket-1..4, uh Housing-1) and these, each inserted at an identity frame here (mm).
SETUP = {"u1": "Sprocket-1", "u2": "Sprocket-2", "u3": "Sprocket-3", "u4": "Sprocket-4", "uh": "Housing-1"}
INSERTS = (("c1", "Chain.SLDPRT", (0.0, 0.0, 180.0)), ("c2", "Chain.SLDPRT", (0.0, 0.0, 186.0)),
           ("h2", "Housing.SLDPRT", (0.0, 0.0, 420.0)), ("s5", "Sprocket.SLDPRT", (0.0, 0.0, 16.0)),
           ("s6", "Sprocket.SLDPRT", (0.0, 0.0, 230.0)), ("s7", "Sprocket.SLDPRT", (0.0, 0.0, 250.0)),
           ("s8", "Sprocket.SLDPRT", (0.0, 0.0, 270.0)), ("s9", "Sprocket.SLDPRT", (0.0, 0.0, 290.0)),
           ("s10", "Sprocket.SLDPRT", (0.0, 0.0, 310.0)), ("s11", "Sprocket.SLDPRT", (0.0, 0.0, 330.0)),
           ("lt", "SprocketLight.SLDPRT", (0.0, 0.0, 350.0)), ("cf", "SprocketConf.SLDPRT", (0.0, 0.0, 370.0)))
OWN_PARTS = ("Chain.SLDPRT", "SprocketLight.SLDPRT", "SprocketConf.SLDPRT")   # built by the strip, as S0's sprocket
SUPPRESS = (("s7", "L"), ("s9", "H"))               # suppressed in L only; in H (the mode showing) only
# (name, kind, a, b, value): an "app" mate by the app's own add_mate on named axes and planes or whole components; a
# "raw" one by AddMate5 on picks (the probes' raw_mate), its type swMateType_e. A pick is a reference in the session's
# grammar, or (what, handle): "bore", "low" / "high" (a part's end face of least / greatest z), "root" (a coaxial
# cylinder of Sun of the least radius), "fillet" (an off-axis cylinder of Sun of the least radius).
MATES = (("UserChainAxis", "app", "coincident", "c1:Gear Axis", "lay:Input Axis", 0.0),
         ("UserChainDist", "app", "distance", "c1:plane1", "u1:plane1", 150.0),
         ("UserFaceConc", "raw", 1, ("bore", "c2"), "lay:Input Axis", None),
         ("UserFaceCoin", "raw", 0, ("low", "c2"), ("high", "c1"), None),
         ("UserHousingRight", "app", "coincident", "h2:plane3", "lay:plane3", 0.0),
         ("UserHousingDist", "app", "distance", "h2:plane1", "lay:plane1", 420.0),
         ("UserHousingPar", "raw", 3, "h2:plane2", "lay:plane2", None),
         ("UserAxis5", "app", "coincident", "s5:Gear Axis", "lay:Input Axis", 0.0),
         ("UserSunFace", "raw", 0, ("low", "s5"), ("high", "sun"), None),
         ("UserAxis6", "app", "coincident", "s6:Gear Axis", "lay:Input Axis", 0.0),
         ("UserGear6", "app", "gear", "s6:Gear Axis", "sun:Gear Axis", (20.0, 29.0)),
         ("UserAsm6", "app", "distance", "s6:plane1", "asm:plane1", 230.0),
         ("UserAxis7", "app", "coincident", "s7:Gear Axis", "lay:Input Axis", 0.0),
         ("UserLock8a", "app", "lock", "sun", "s8", 0.0),
         ("UserLock8b", "app", "lock", "uh", "s8", 0.0),
         ("UserAxis9", "app", "coincident", "s9:Gear Axis", "lay:Input Axis", 0.0),
         ("UserAxis10", "app", "coincident", "s10:Gear Axis", "lay:Input Axis", 0.0),
         ("UserGearRoot", "raw", 10, "s10:Gear Axis", ("root", "sun"), None),
         ("UserAxis11", "app", "coincident", "s11:Gear Axis", "lay:Input Axis", 0.0),
         ("UserGearFillet", "raw", 10, "s11:Gear Axis", ("fillet", "sun"), None),
         ("UserLimit10", "raw", 5, "s10:plane1", "s11:plane1", (0.020, 0.030, 0.010)),
         ("UserAxisLight", "app", "coincident", "lt:Gear Axis", "lay:Input Axis", 0.0),
         ("UserAxisConf", "app", "coincident", "cf:Gear Axis", "lay:Input Axis", 0.0))
SETUP_MATES = ("UserAxis1", "UserAxis2", "UserLock1", "UserLock2", "UserLock3", "UserAxis4", "UserDist4", "UserAngle4")
CLUSTER_ONE = ("u1", "u3", "u4", "c1")               # the Done-when's first cluster: the sprockets on Sun and Chain-1
CLUSTER_TWO = ("h2",)                                # the housing on the layout
TIED = ("s8", "uh")                                  # falls back: UserLock8a deleted, UserLock8b kept, both fixed
FIXTURE_JSON = "w9d-fixture.json"


# -- pure: what each section must find (self-checked) ------------------------------------------------------------------


def expected_outcome(fs, made_mates, closed=False, light=False):
    """What the carry must do with the fixture's mates on this SolidWorks, by the findings ``fs`` as they stand (the
    probe reads: ``faces`` the face and edge route set, ``coaxial`` COAXIAL_FACE_READ, ``states`` the per-mode state
    route, ``reload`` PERSIST_REFERENCE_SURVIVES_RELOAD) with the write gates patched: ``closed`` the not-open path,
    ``light`` a component lightweight in the session (no root read, §4.2). ``{mate: set of acceptable outcomes}``,
    an outcome "remade", "fell" (made, then deleted by its cluster's fallback) or a ``WHY_*`` word."""
    out = {m: {"remade"} for m in made_mates}
    faces_ok = bool(fs.get("faces")) and (not closed or bool(fs.get("reload")))
    for m in ("UserFaceConc", "UserFaceCoin"):
        if not faces_ok:
            out[m] = {"unmeasured"}
    # Sun's part is new: a face of it is never found again (§4.4); whichever entity comes first names the mate.
    out["UserSunFace"] = {"part new"} if faces_ok else {"part new", "unmeasured"}
    out["UserGearFillet"] = {"part new"}             # off-axis (2026) or not read (None): never Gear Axis
    if not fs.get("coaxial"):
        out["UserGearRoot"] = {"part new"}
    if light:
        out["UserAsm6"] = {"unread"}                 # no root read beside a lightweight component (§4.2, §11.5)
        out["UserAxisLight"] = {"lightweight"}       # D10
    if not (fs.get("states") or closed):
        out["UserAxis9"] = {"unread"}                # D2: Sprocket-9 takes H's state (suppressed) in every mode
    out["UserLock8a"] = {"fell"}
    return {m: v for m, v in out.items() if m in made_mates}


def expected_states(fs, closed=False):
    """The new modes each state-carrying component reads suppressed in, by the route (§5.2): read per mode (the route
    set, or the job's own read-only show on the closed path) or the mode showing's in every mode (D2, open only)."""
    if fs.get("states") or closed:
        return {"s7": {"L"}, "s9": {"H"}}
    return {"s7": set(), "s9": set(MODES)}           # H showing: Sprocket-7 resolved there, Sprocket-9 suppressed


def outcome_problems(expected, got):
    """Each mate whose outcome is not among the expected ones: ``got`` {mate: outcome}; a mate expected and not
    accounted for at all is said too, and one accounted for that was not expected."""
    out = []
    for name, ways in sorted(expected.items()):
        if got.get(name) not in ways:
            out.append(f"{name}: {got.get(name, 'not accounted for')} where {sorted(ways)}")
    out += [f"{name}: {how} but not in the fixture" for name, how in sorted(got.items()) if name not in expected]
    return out


def outcome_of(remade, named, fallbacks):
    """{mate: outcome} from a CarryResult's fields (plain: ``remade`` names, ``named`` (item, what, why), ``fallbacks``
    each's deleted names)."""
    got = {n: "remade" for n in remade}
    for item, what, why in named:
        if what == "mate":
            got.setdefault(item, why)
    for deleted in fallbacks:
        for n in deleted:
            got[n] = "fell"
    return got


def fingerprint_diff(before, after):
    """Files whose (size, mtime, hash) changed, or that came or went: ``{name: (before, after)}``."""
    return {n: (before.get(n), after.get(n)) for n in sorted(set(before) | set(after)) if before.get(n) != after.get(n)}


WRITES = ("ShowConfiguration2", "ForceRebuild3", "EditRebuild3", "AddMate5", "AddComponent5", "EditDelete",
          "Save3", "SaveAs3", "QuitDoc", "CloseDoc")


def trace_problems(calls, old, users, new_asm, read_only_old=False, shows_ok=False):
    """A traced Build again…'s calls ``[(member, file name)]`` against §3's *Never written*: no write, show, rebuild,
    save or close of the old assembly or a user document (on the not-open path the job's own read-only open of the
    old assembly and its close are allowed, a show only where the per-mode states are read by showing it); nothing
    saved after the new assembly's first save. Returns sentences."""
    out, first_save = [], None
    mine = {n.lower() for n in users}
    for i, (member, target) in enumerate(calls):
        t = (target or "").lower()
        if member in ("SaveAs3", "Save3") and first_save is not None:
            out.append(f"#{i} {member} of {target} after {new_asm} was first saved")
        if member == "SaveAs3" and t == new_asm.lower() and first_save is None:
            first_save = i
        if t == old.lower():
            allowed = read_only_old and (member in ("QuitDoc",) or (member == "ShowConfiguration2" and shows_ok))
            if member in WRITES and not allowed:
                out.append(f"#{i} {member} of the old assembly {target}")
            if member in ("OpenDoc6", "ActivateDoc3") and not read_only_old:
                out.append(f"#{i} {member} of the old assembly {target}, which was open (never opened or activated)")
        elif t in mine and member in WRITES:
            out.append(f"#{i} {member} of the user's {target}")
    if first_save is None:
        out.append(f"{new_asm} was never saved by SaveAs3 in the traced calls")
    return out


def definition_problems(old, new, kind):
    """A remade mate's definition read in the new revision against the old one's (type, alignment, values; flipped
    except for a gear mate, whose sense the worker may have read right with the other Flip): sentences."""
    out = []
    if old["type"] != new["type"]:
        out.append(f"type {old['type']} -> {new['type']}")
    if old["alignment"] != new["alignment"]:
        out.append(f"alignment {old['alignment']} -> {new['alignment']}")
    if kind != "gear" and bool(old["flipped"]) != bool(new["flipped"]):
        out.append(f"flipped {old['flipped']} -> {new['flipped']}")
    a, b = dict(old["values"]), dict(new["values"])
    for key in sorted(set(a) | set(b)):
        if key in a and key in b and abs(float(a[key]) - float(b[key])) > VALUE_TOL:
            out.append(f"{key} {a[key]} -> {b[key]}")
        elif (key in a) != (key in b) and key not in ("Reverse", "FlipDimension"):
            out.append(f"{key} read {'before only' if key in a else 'after only'}")
    return out


def old_diff(before, after, mine):
    """What differs on the old assembly between two reads made where it stands: a frame (to 1e-9), a mate's code or
    flag per mode or entities, the mode showing, its rebuild state, a component's state, and the save flag of a
    document of ``mine`` (file names). Sentences."""
    out = []
    for g in sorted(set(before["frames"]) | set(after["frames"])):
        a, b = before["frames"].get(g), after["frames"].get(g)
        if (a is None) != (b is None) or (a is not None and pose_gap(a, b) > 1e-9):
            out.append(f"{g} moved")
    for key in ("mates", "by_mode", "entities", "states"):
        if before.get(key) != after.get(key):
            out.append(f"{key} {[(n, before[key].get(n), v) for n, v in after[key].items() if before[key].get(n) != v]}")
    if before["active"] != after["active"]:
        out.append(f"the mode showing {before['active']} -> {after['active']}")
    if before.get("needs_rebuild") != after.get("needs_rebuild"):
        out.append(f"rebuild state {before.get('needs_rebuild')} -> {after.get('needs_rebuild')}")
    flips = {n: (before["flags_after"].get(n), after["flags_after"].get(n)) for n in mine
             if before["flags_after"].get(n) != after["flags_after"].get(n)}
    if flips:
        out.append(f"save flags {flips}")
    return out


def kinds_clean(kind_of, outcome, unclean):
    """The kind words remade clean (D4): every mate of the kind in the fixture remade (or kept by a fallback's
    user–user rule) and none of them unclean (``unclean``: names whose re-read differed); a kind any of whose mates
    was made but named ``differs`` or ``refused`` is left out. ``kind_of`` {mate: kind word}."""
    good, bad = set(), set()
    for name, kind in kind_of.items():
        how = outcome.get(name)
        if how == "remade" and name not in unclean:
            good.add(kind)
        elif how in ("differs", "refused") or name in unclean:
            bad.add(kind)
    return tuple(k for k in KIND_WORDS if k in good and k not in bad)


def pose_gap(rel_a, rel_b):
    """The largest difference between two relative poses ((rotation 9), (origin mm))."""
    return max([abs(float(x) - float(y)) for x, y in zip(rel_a[0], rel_b[0])]
               + [abs(float(x) - float(y)) for x, y in zip(rel_a[1], rel_b[1])])


def propose(name, value, evidence):
    return f"propose {name} = {value!r}  # {evidence}"


class patched_values:
    """Named findings set to the given values in this process only, for one measurement, each said; put back on the
    way out. ``say`` the log's (print in the self-check)."""

    def __init__(self, values, year, say=print):
        from gear_generator import findings
        self.findings, self.say = findings, say
        self.values = {f"{k}_ON_{year}": v for k, v in values.items()}
        self.was = {}

    def __enter__(self):
        for name, value in self.values.items():
            self.was[name] = getattr(self.findings, name, None)
            setattr(self.findings, name, value)
            self.say(f"PATCH   findings.{name} = {value!r} in this process, for this measurement only "
                     f"(was {self.was[name]!r})")
        return self

    def __exit__(self, *_exc):
        for name, value in self.was.items():
            setattr(self.findings, name, value)
            self.say(f"PATCH   findings.{name} back to {value!r}")
        return False


def probe_reads(year):
    """The probe reads the expectations rest on, as findings.py holds them for ``year``."""
    from gear_generator import findings
    g = lambda n: getattr(findings, f"{n}_ON_{year}", None)         # noqa: E731
    return {"faces": g("PERSIST_REFERENCE_ROUTE_FOR_FACES") is not None, "coaxial": g("COAXIAL_FACE_READ") is True,
            "states": g("COMPONENT_STATE_PER_CONFIGURATION_ROUTE") is not None,
            "unsaved": g("COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED") is True,
            "reload": g("PERSIST_REFERENCE_SURVIVES_RELOAD") is True}


def edit_spec(rb):
    """RangeBox with §15's edit: Sun's Flank to arcs and a shaft Aux added with a gear on it."""
    from gear_generator.workbook.model import Gear, Shaft
    gid, shaft, at, kind, teeth, module, face = AUX_GEAR
    rows = max(g.row for g in rb.gears) + 1, max(s.row for s in rb.shafts) + 1
    gear = Gear(gid, shaft, at, kind, "", teeth, module, "", face, row=rows[0])
    gears = tuple(dataclasses.replace(g, flank=SUN_FLANK) if g.id == "Sun" else g for g in rb.gears) + (gear,)
    return dataclasses.replace(rb, shafts=rb.shafts + (Shaft(**AUX_SHAFT, row=rows[1]),), gears=gears)


def _head(name):
    """A probe script's pure part (its source up to its own self-check), run as a module: importing it would run its
    self-check, or its live part."""
    path = os.path.join(HERE, name)
    with open(path, encoding="utf-8") as handle:
        head = handle.read().split("\nif SELF_CHECK:\n", 1)[0]
    module = types.ModuleType(name[:-3] + "_pure")
    module.__file__ = path
    exec(compile(head, path, "exec"), module.__dict__)  # noqa: S102 - the repo's own script
    return module


# -- --self-check: the edit through the app's own writer, reader and classify; the carry on the fake ---------------------


def _fake_desk(c9, entity_kinds=True):
    """B's round trip desk (RangeBox on the fake, W9a's user work read by a quiet press) with M9's tie added: Sprocket-8
    locked to Sun and to the fixed Housing-1, and Chain-1 on the layout's Input Axis, read by a second quiet press."""
    c9._fake()
    import test_workbook_carry as twc
    from test_workbook_in_place_round_trip import _component
    from workbook_fixtures import range_box
    desk = twc._desk(entity_kinds)
    rec, sw = desk.record, desk.sw
    asm = rec.gearbox.assembly
    sw.user_component(asm, "Sprocket-8", "C:\\Parts\\Sprocket.SLDPRT", (I9, (0.0, 0.0, 270.0)))
    sw.user_component(asm, "Chain-1", "C:\\Parts\\Chain.SLDPRT", (I9, (0.0, 0.0, 180.0)))
    sw.user_lock(asm, "UserLock8a", _component(rec, "Sun"), "Sprocket-8")
    sw.user_lock(asm, "UserLock8b", "Housing-1", "Sprocket-8")
    sw.user_mate(asm, "UserChainAxis", kind="coincident", a=("Chain-1", "Gear Axis"),
                 b=(rec.gearbox.layout_component, "Input Axis"))
    desk.disk.files |= {"c:\\parts\\chain.sldprt"}
    quiet = desk.press(range_box())
    assert quiet.result is not None or quiet.refused is not None
    return desk, twc


def _closed_fake(desk):
    """The old assembly saved with the user's work in it and closed, on the fake (test_swbuild_carry's ``_closed``
    for RangeBox's desk)."""
    import copy
    from test_swbuild import _key
    sw = desk.sw._w9d()
    key = _key(desk.record.gearbox.assembly)
    sw.saved_mates[key] = copy.deepcopy(sw.memory_mates[key])
    sw.saved_configs[key] = (list(sw.configs), sw.config, copy.deepcopy(sw.frames_by))
    sw.open_docs = [d for d in sw.open_docs if _key(d.path) != key]
    for kept in (sw.memory, sw.memory_mates, sw.memory_configs):
        kept.pop(key, None)
    sw.touched.discard(key)
    return desk


def self_check():
    started = time.monotonic()
    c9 = _head("w9c_demonstration.py")        # W9c's pure part: row_edits, _offline, _assessed, the fake's stand-in
    c9.SHEETS = SHEETS                        # the edit adds a Shafts row
    c9._fake()
    from gear_generator import findings, store, swbuild, ui_text
    from gear_generator.workbook import update
    from workbook_fixtures import range_box
    bad = []

    def ok(cond, what):
        print(("ok      " if cond else "FAIL    ") + what)
        if not cond:
            bad.append(what)

    rb = range_box()
    edited = edit_spec(rb)
    year = 2026

    # 1. The edit, typed as W8's cell would, by the app's own write_cells; read back by the app's own reader.
    edits = c9.row_edits(rb, edited)
    print(f"fact    the edit's cells: {edits}")
    ok({s for s, _, _, _ in edits} == {"Shafts", "Gears"} and ("Gears", "Flank", "Sun", SUN_FLANK) in edits
       and sum(1 for s, _, k, _ in edits if k == "") == len([v for v in c9.sheet_rows(edited)["Shafts"][-1] if not c9._blank(v)])
       + len([v for v in c9.sheet_rows(edited)["Gears"][-1] if not c9._blank(v)]),
       "the edit: Sun's Flank typed arcs, the Aux shaft's row and the Aux gear's row typed in, nothing else")
    with tempfile.TemporaryDirectory() as folder:
        (spec, cells), = c9._offline(rb, [edits], folder)
    a = c9._assessed(spec)
    errors = [d.message for d in a.diagnostics if d.is_error]
    sun = next(g for g in spec.gears if g.id == "Sun")
    mesh = any({m.a, m.b} == {"Sun", "Planet"} for m in spec.meshes)
    ok(not errors and not a.lay_out_refusal() and sun.flank == SUN_FLANK and mesh
       and any("Arcs stand in for the involute" in d.message for d in a.diagnostics),
       f"the edit read back is legal: Sun's arcs mesh Planet's involute (D18), the note said: {errors[:2]}")

    # 2. classify on a record built on the fake: Build again…, for Sun's Flank and the new shaft.
    desk, twc = _fake_desk(c9)
    up = update.classify(desk.record, desk.a(spec), exists=desk.disk.exists, read_sidecar=desk.disk.read_sidecar)
    said = " ".join(up.structural)
    ok(up.needs_new_revision and "Flank" in said and "Aux" in said,
       f"classify: Build again…, because Sun's Flank changed and the shaft Aux is new: {list(up.structural)}")
    again = twc._again(desk, spec)
    carry = twc._carry(desk, again)
    by = {b.old: b for b in carry.bodies}
    ok(by["Sun"].why_new == "its Flank changed" and not by["Sun"].same_file
       and all(by[f"Planet copy {k}"].same_file for k in (1, 2, 3)) and by["Ring"].same_file,
       f"carry_for: Sun's part is new because its Flank changed, every other gear part reused: "
       f"{ {k: (b.same_file, b.why_new) for k, b in by.items()} }")
    question = ui_text.build_again_question(up, again, record=desk.record)
    print(f"question (gates as they stand) {question}")
    ok("findings.CARRY_INSERTS_ON_2026" in question and "Keyway" in question,
       "the question, every write gate None: W9a's clause led by CARRY_INSERTS, the Keyway named")

    # 3. The carry end to end on the fake: the gates as they stand; patched; the old assembly closed.
    gates_none = {k: None for k in WRITE_GATES}
    with patched_values(gates_none, year):
        _, carry, result, record = twc._carry_job(desk, spec)
    cr = result.carry
    named = {n.item: (n.why, n.subjects) for n in cr.named}
    ok(result.ok and cr.inserted == [] and cr.remade == [] and not cr.unsaved
       and all(w == swbuild.WHY_UNMEASURED and "CARRY_INSERTS_ON_2026" in s for n, (w, s) in named.items()
               if n in ("Sprocket-1", "Housing-1", "Sprocket-8", "Chain-1"))
       and record.gearbox.carry.unsaved_at == 0.0 and record.gearbox.user_work is None,
       f"carry-gates on the fake: RangeBox_r2 built, nothing carried, each component named with CARRY_INSERTS: {named}")
    status = twc._status_of(desk, again, carry, result)
    print(f"result  (gates as they stand) {status}")
    ok(status.startswith("Gear Generator has not yet been shown to carry your work") and "Keyway" in status,
       "carry-gates on the fake: the result is W9a's sentence led by CARRY_INSERTS, the Keyway named")
    for gate in WRITE_GATES:
        others = {k: v for k, v in WRITE_GATES.items() if k != gate}
        with patched_values(dict(others, **{gate: None}), year, say=lambda _t: None):
            plan = swbuild.plan_carry(cr.work, carry, desk.sw.revision)
        held = [n.item for n in plan.named if any(f"{gate}_ON_" in str(s) for s in n.subjects)]
        if gate in ("REFERENCED_CONFIGURATION_READ", "CARRY_INSERTS_IN_A_CONFIGURATION",
                    "CARRY_GEAR_MATE_ON_AN_APP_GEAR"):
            print(f"fact    {gate} as it stands names nothing on the fake desk (no file of two configurations, no "
                  f"user gear mate there; on SolidWorks SprocketConf-1 and UserGear6): {held}")
        else:
            ok(bool(held), f"each gate's own refusal: {gate} None, the others patched, names {held}")

    desk, twc = _fake_desk(c9)
    again = twc._again(desk, spec)
    sun_body = next(b for b in twc._carry(desk, again).bodies if b.old == "Sun")
    desk.sw.locks["UserLock8a"] = (sun_body.handle, f"{sun_body.handle}-1")     # made again, it ties Sun's train
    with patched_values(WRITE_GATES, year):
        _, carry, result, record = twc._carry_job(desk, spec)
        status = twc._status_of(desk, again, carry, result)
    cr = result.carry
    print(f"result  (carry) {status}")
    for line in cr.log_lines():
        print("        " + line)
    olds = [o for o, _ in cr.inserted]
    fell = cr.fixed[0] if cr.fixed else None
    ok(result.ok and cr.stopped == "" and {"Sprocket-1", "Housing-1", "Sprocket-8", "Chain-1"} <= set(olds)
       and {"Lock3", "UserChainAxis", "UserLock8b"} <= {r[0] for r in cr.remade} and fell is not None
       and fell.why == swbuild.FELL_TIE and fell.deleted == ("UserLock8a",) and fell.kept == ("UserLock8b",)
       and cr.unsaved,
       f"carry on the fake: every component carried, Lock3, UserChainAxis and UserLock8b made again, the tied cluster "
       f"fallen back alone (UserLock8a deleted, UserLock8b kept): {cr.fixed}")
    got = outcome_of([r[0] for r in cr.remade], [(n.item, n.what, n.why) for n in cr.named],
                     [f.deleted for f in cr.fixed])
    want = {"Lock3": {"remade"}, "UserChainAxis": {"remade"}, "UserLock8b": {"remade"}, "UserLock8a": {"fell"}}
    ok(outcome_problems(want, got) == [], f"carry on the fake: the outcomes as judged live: {got}")
    ok(status.startswith("Carried into RangeBox_r2, unsaved") and "fixed where" in status
       and "Keyway" in status, "carry on the fake: the result says what was carried unsaved, the fallback, the Keyway")
    on_disk = json.loads(store.link_record_to_json(record))
    ok(on_disk["link_schema_version"] == 10 and record.gearbox.carry.unsaved_at > 0
       and ui_text.carry_footer_line(record) != "",
       "carry on the fake: the record at schema 10 holds the carry, unsaved_at set, the footer's line said")

    desk, twc = _fake_desk(c9)
    _closed_fake(desk)
    with patched_values(WRITE_GATES, year):
        _, carry, result, record = twc._carry_job(desk, spec)
    cr = result.carry
    ok(result.ok and cr.work is not None and cr.work.how == swbuild.OLD_READ_ONLY and cr.work.left == []
       and cr.work.marked == [] and {"Sprocket-1", "Chain-1"} <= {o for o, _ in cr.inserted},
       f"carry-closed on the fake: read read-only, nothing left open or marked, carried: {cr.inserted}; unread "
       f"{cr.work.unread if cr.work else None}")
    refusal = swbuild._not_open_refusal(desk.sw, dataclasses.replace(carry, written_on=(32,)), [])  # noqa: SLF001
    ok("last written on this SolidWorks" in refusal, f"carry-closed: a record another version wrote is refused before "
                                                     f"any read: {refusal!r}")

    # 4. The pure judgements, on made-up readings, each failing way.
    made = [m[0] for m in MATES] + list(SETUP_MATES)
    fs26 = {"faces": True, "coaxial": True, "states": True, "reload": True}
    fs24 = {"faces": False, "coaxial": False, "states": False, "reload": False}
    e = expected_outcome(fs26, made, light=True)
    ok(e["UserFaceConc"] == {"remade"} and e["UserGearRoot"] == {"remade"} and e["UserAsm6"] == {"unread"}
       and e["UserAxisLight"] == {"lightweight"} and e["UserSunFace"] == {"part new"} and e["UserLock8a"] == {"fell"}
       and e["UserAxis9"] == {"remade"},
       "expected, 2026 open with SprocketLight lightweight: faces and the root gear made again, the asm-plane mate "
       "unread, the light one's mate named, Sun's face part new, the tie fallen back")
    e = expected_outcome(fs24, made)
    ok(e["UserFaceConc"] == {"unmeasured"} and e["UserGearRoot"] == {"part new"} and e["UserAxis9"] == {"unread"}
       and e["UserAsm6"] == {"remade"}, "expected, 2024 open: faces unmeasured, the root gear part new, D2's unread")
    e = expected_outcome(fs26, made, closed=True)
    ok(e["UserAsm6"] == {"remade"} and e["UserAxisLight"] == {"remade"} and e["UserAxis9"] == {"remade"},
       "expected, closed: no lightweight, every state read")
    ok(expected_outcome(dict(fs26, reload=False), made, closed=True)["UserFaceCoin"] == {"unmeasured"},
       "expected, closed without the reload finding: face mates unmeasured")
    ok(expected_states(fs26) == {"s7": {"L"}, "s9": {"H"}} and expected_states(fs24) == {"s7": set(), "s9": set(MODES)}
       and expected_states(fs24, closed=True) == {"s7": {"L"}, "s9": {"H"}}, "states expected per route (D2)")
    exp = {"A": {"remade"}, "B": {"part new"}, "C": {"fell"}}
    ok(outcome_problems(exp, {"A": "remade", "B": "part new", "C": "fell"}) == []
       and len(outcome_problems(exp, {"A": "differs", "B": "part new", "C": "fell", "D": "remade"})) == 2
       and len(outcome_problems(exp, {"A": "remade", "B": "part new"})) == 1,
       "outcomes: a mate otherwise, one not accounted for and one not in the fixture each said")
    ok(outcome_of(["A", "B"], [("B", "mate", "unread"), ("X", "component", "no frame"), ("C", "mate", "kind")],
                  [("A",)]) == {"A": "fell", "B": "remade", "C": "kind"}, "outcome_of: remade, named, fell")
    fp = {"a": (1, 2.0, "h"), "b": (1, 2.0, "h")}
    ok(fingerprint_diff(fp, dict(fp)) == {} and set(fingerprint_diff(fp, {"a": (1, 2.0, "x")})) == {"a", "b"},
       "fingerprints: a changed hash and a file gone each said")
    calls = [("OpenDoc6", "Sprocket.SLDPRT"), ("SaveAs3", "RangeBox_r2.SLDASM"), ("AddComponent5", "RangeBox_r2.SLDASM"),
             ("AddMate5", "RangeBox_r2.SLDASM"), ("ShowConfiguration2", "RangeBox_r2.SLDASM")]
    ok(trace_problems(calls, "RangeBox.SLDASM", ["Sprocket.SLDPRT"], "RangeBox_r2.SLDASM") == [],
       "trace: a carry into the new assembly after its save, a user part opened, is clean")
    worse = calls + [("ShowConfiguration2", "RangeBox.SLDASM"), ("Save3", "RangeBox_r2.SLDASM"),
                     ("ForceRebuild3", "Sprocket.SLDPRT"), ("OpenDoc6", "RangeBox.SLDASM"),
                     ("ActivateDoc3", "RangeBox.SLDASM")]
    ok(len(trace_problems(worse, "RangeBox.SLDASM", ["Sprocket.SLDPRT"], "RangeBox_r2.SLDASM")) == 5
       and len(trace_problems(calls[:1], "RangeBox.SLDASM", [], "RangeBox_r2.SLDASM")) == 1,
       "trace: a show of the old assembly, a save after the first, a user part rebuilt, the open old opened, and a "
       "build never saved are each said")
    closed_calls = [("OpenDoc6", "RangeBox.SLDASM"), ("ShowConfiguration2", "RangeBox.SLDASM"),
                    ("QuitDoc", "RangeBox.SLDASM")] + calls
    ok(trace_problems(closed_calls, "RangeBox.SLDASM", [], "RangeBox_r2.SLDASM", True, shows_ok=True) == []
       and len(trace_problems(closed_calls, "RangeBox.SLDASM", [], "RangeBox_r2.SLDASM", True)) == 1,
       "trace, closed: the job's read-only open, show (where the states are read by showing) and close allowed")
    old = {"type": 10, "alignment": 0, "flipped": False, "values": [("GearRatioNumerator", 29.0),
                                                                     ("GearRatioDenominator", 20.0)]}
    ok(definition_problems(old, dict(old, flipped=True), "gear") == []
       and len(definition_problems(old, dict(old, values=[("GearRatioNumerator", 20.0),
                                                          ("GearRatioDenominator", 29.0)]), "gear")) == 2
       and definition_problems(dict(old, type=0), dict(old, type=0, flipped=True), "coincident") != [],
       "definitions: a gear's other Flip passes, a swapped ratio and a coincident's flip are said")
    kinds = {"A": "lock", "B": "lock", "C": "gear", "D": "parallel", "E": "angle"}
    ok(kinds_clean(kinds, {"A": "remade", "B": "fell", "C": "remade", "D": "differs", "E": "remade"}, {"E"})
       == ("lock", "gear"), "kinds remade clean: a kind with a mate that differed, or re-read otherwise, left out")
    read = {"frames": {"Sun": (I9, (0.0, 0.0, 0.0)), "Sprocket-9": None}, "mates": {"L1": (0, False)},
            "by_mode": {"L1": {"H": False}}, "entities": {}, "states": {"Sprocket-9": 0}, "active": "H",
            "needs_rebuild": 0, "flags_after": {"RangeBox.SLDASM": False}}
    moved = dict(read, frames={"Sun": (I9, (0.0, 0.0, 1.0)), "Sprocket-9": None}, active="L",
                 flags_after={"RangeBox.SLDASM": True}, states={"Sprocket-9": 2})
    ok(old_diff(read, dict(read), {"RangeBox.SLDASM"}) == []
       and len(old_diff(read, moved, {"RangeBox.SLDASM"})) == 4,
       "the old assembly: a frame moved, the mode showing, a state and its save flag each said; a suppressed "
       "component's unread frame the same both times is no change")
    rel = (I9, (0.0, 0.0, 10.0))
    ok(pose_gap(rel, rel) == 0.0 and abs(pose_gap(rel, (I9, (0.0, 0.0, 10.5))) - 0.5) < 1e-12, "pose gap")
    ok(tuple(swbuild.CARRY_KIND_WORDS) == KIND_WORDS and set(WRITE_GATES) | set(STAY_NONE) <= {
        n[:-len("_ON_2026")] for n in dir(findings) if n.endswith("_ON_2026")},
       "the kind words are the worker's; every gate named here is a finding of findings.py")
    ok(all(getattr(findings, f"{g}_ON_{y}", "x") is None for g in WRITE_GATES for y in (2026, 2024)),
       "every gate this script patches is None in findings.py on both versions (so it proposes, never sets)")
    ok(propose("X", True, "e") == "propose X = True  # e", "propose's form")
    print(f"fact    the self-check took {time.monotonic() - started:.0f} s")
    print(f"done    {len(bad)} failed")
    return 0 if not bad else 1


if SELF_CHECK:
    raise SystemExit(self_check())


# -- the live run: W9a's harness, W9b's per-mode judgement, W9c's press and patches, the probes' raw mates ---------------

sys.path.insert(0, HERE)
import w9a_demonstration as A  # noqa: E402  (W8's and S0's scripts, the watch, the What's Wrong rule, Desk9, main)
import w9b_demonstration as B  # noqa: E402  (§3's per-mode read and judgement)
import w9c_demonstration as C9  # noqa: E402  (press, edits typed in Excel, the footer's foresight held to the press)
import w9c_probes as CP  # noqa: E402  (raw_mate, select_face, part_faces_of)

W, S0 = A.W, A.S0
from gear_generator import findings, store, swbuild, swcom, ui_text, workbook_gui  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.workbook import update as wb_update  # noqa: E402

say, check = W.say, W.check
OUT = W.OUT
CTX, RESULT, run, job = A.CTX, A.RESULT, A.run, A.job
C9.SHEETS = SHEETS                           # the edit adds a Shafts row; same_sheets compares it too
MASTERS = {"fixture": A._arg("--fixture-master")}  # noqa: SLF001
OTHER_VERSION_FILE = A._arg("--other-version-file")  # noqa: SLF001
_RAW = W._RAW_CALL  # noqa: SLF001


def year():
    return swcom.release_year(int(W.TAG["revision"][0]))


def finding_name(stem):
    return f"{stem}_ON_{year()}"


def proposed(name, value, evidence):
    RESULT["proposal"][name] = value
    RESULT["proposal"][f"{name}_evidence"] = evidence
    say(propose(name, value, evidence))


# -- the document trace and the unmeasured calls, logged ---------------------------------------------------------------

DOC_TRACE = {"on": False, "calls": [], "count": {}}
DOC_MEMBERS = WRITES + ("OpenDoc6", "ActivateDoc3")
COUNTED = ("GetCorresponding", "IsSame", "GetArea", "CircleParams", "GetPersistReference3",
           "GetObjectByPersistReference3")
_PREV_CALL = swcom.call


def _target(obj, name, args):
    """The file a traced call is on, by its name only: the path argument of an application call and of SaveAs3, else
    the document's own path."""
    if name in ("OpenDoc6", "QuitDoc", "CloseDoc", "ActivateDoc3", "SaveAs3") and args:
        return os.path.basename(str(args[0]))
    try:
        return os.path.basename(str(_RAW(obj, "GetPathName") or "")) or "?"
    except Exception:  # noqa: BLE001 - the trace never changes what the job does
        return "?"


WALK = {"on": False, "resolves": [], "types": []}


def doc_traced(obj, name, *args):
    if DOC_TRACE["on"]:
        if name in DOC_MEMBERS:
            DOC_TRACE["calls"].append((name, _target(obj, name, args)))
        if name in COUNTED:
            DOC_TRACE["count"][name] = DOC_TRACE["count"].get(name, 0) + 1
    answer = _PREV_CALL(obj, name, *args)
    if WALK["on"] and name == "GetObjectByPersistReference3":
        # The re-check's item: whether SolidWorks writes the out code, and where pywin32 hands it back.
        written = getattr(args[1], "value", args[1]) if len(args) > 1 else None
        WALK["resolves"].append({"returned_tuple": isinstance(answer, tuple),
                                 "returned_second": answer[1] if isinstance(answer, tuple) and len(answer) > 1 else None,
                                 "out_parameter_after": written})
    if WALK["on"] and name == "GetType":
        WALK["types"].append(answer)           # IEntity.GetType on a resolved face or edge (the kind check)
    return answer


swcom.call = doc_traced
LOGGED = {"entity_references": [], "calls": []}


def _short(value):
    """A call's argument as logged: a path by its file name, a long string (a persistent reference) cut, a mate's
    definition by its name."""
    if isinstance(value, swbuild.OldMate):
        return f"<definition of {value.name}>"
    if isinstance(value, str) and ("\\" in value or "/" in value) and not value.startswith("ref:"):
        return os.path.basename(value)
    if isinstance(value, str) and len(value) > 60:
        return value[:40] + f"…({len(value)})"
    if isinstance(value, (list, tuple)):
        return type(value)(_short(v) for v in value) if not hasattr(value, "_fields") else value
    return value


def _logged(name):
    """``Session.<name>`` wrapped: each call said with its arguments (file names only), its answer and its seconds;
    ``entity_references`` with the calls it made by member (the walk's reads: GetArea the prefilter's, GetCorresponding
    each candidate carried) and whether a cap was reached (package A's "still shown only on the fake")."""
    original = getattr(swcom.Session, name)

    def wrapper(self, *args, **kwargs):
        counts = dict(DOC_TRACE["count"])
        on = DOC_TRACE["on"]
        DOC_TRACE["on"] = True
        walking = name in ("entity_references", "select_by_reference")
        if walking:
            WALK.update(on=True, resolves=[], types=[])
        began = time.monotonic()
        try:
            answer = original(self, *args, **kwargs)
        except Exception as exc:
            say(f"fact    {name}{_short(args)} raised {type(exc).__name__}: {exc} after "
                f"{time.monotonic() - began:.2f} s")
            raise
        finally:
            DOC_TRACE["on"] = on
            WALK["on"] = False
        if walking:
            say(f"fact    {name}: GetObjectByPersistReference3's out code as SolidWorks left it {WALK['resolves']}; "
                f"IEntity.GetType on what resolved {WALK['types']}")
        seconds = round(time.monotonic() - began, 3)
        made = {k: DOC_TRACE["count"].get(k, 0) - counts.get(k, 0) for k in COUNTED if DOC_TRACE["count"].get(k, 0)
                - counts.get(k, 0)}
        if name == "entity_references":
            component = self._component_name(args[0]) if args else "?"  # noqa: SLF001
            walk = dict(getattr(self, "last_walk", None) or {})
            carried = walk.get("carried") or made.get("GetCorresponding", 0)
            row = {"component": component, "items": len(args[1]) if len(args) > 1 else 0, "seconds": seconds,
                   "calls": made, "capped": [a[4] for a in answer if a[4]], "found": sum(1 for a in answer if a[1]),
                   "per_candidate": round(seconds / carried, 4) if carried else None,
                   "stats": [(k, listed, kept, str(key), matched) for k, listed, kept, key, matched
                             in walk.get("items", ())],
                   "caps": (swbuild.CARRY_WALK_CANDIDATES, swbuild.CARRY_WALK_SECONDS),
                   "answers": [(a[0], bool(a[1]), a[2], a[3], a[4], a[5]) for a in answer]}
            LOGGED["entity_references"].append(row)
            say(f"fact    r3 walk on {component}, grouped ({row['items']} face/edge item(s), each candidate carried at "
                f"most once): {seconds} s, {carried} carried, {row['per_candidate']} s per candidate; per item (kind, "
                f"listed, after the part-against-assembly prefilter, its key, matched) {row['stats']}; calls {made}; "
                f"found {row['found']}; capped {row['capped'] or 'none'} (caps {row['caps']}); {row['answers']}")
        else:
            LOGGED["calls"].append((name, seconds))
            say(f"fact    {name}{_short(args)} -> {_short(answer) if not isinstance(answer, dict) else answer} in "
                f"{seconds} s{f'; calls {made}' if made else ''}")
        return answer
    setattr(swcom.Session, name, wrapper)


for _name in ("entity_references", "entity_reference", "component_configurations", "component_states_in",
              "open_read_only", "close_unsaved", "file_version", "running_file_version", "dependencies",
              "add_component_in", "set_component_suppressed", "remake_mate", "select_by_reference", "delete_mate"):
    _logged(_name)


# -- the window's Build again… with the carry, traced ------------------------------------------------------------------


class DeskD(A.Desk9):
    """Desk9 with the window's ``_start_build`` as it now runs a Build again… (W9D-INTERFACES §2.1): ``old_assembly``
    as ``before`` and ``carry_for`` from that very object as ``carry``; ``job.revision`` taken in the job, as the
    window's work does; then the window's own ``_finish_build``. The calls are traced (W8's TRACE and the document
    trace)."""

    def build(self, plan=None):
        plan = plan or self.plan
        jb = workbook_gui.Job(workbook_gui.JOB_BUILD, self.reading.digest, plan=plan, record=self.record)
        kwargs = plan.build_kwargs()
        jb.before = self.before = wb_update.old_assembly(self.record, plan)
        self.carry = None
        if jb.before is not None:
            kwargs["before"] = jb.before
            try:
                jb.carry = wb_update.carry_for(self.record, plan, jb.before)
            except Exception as exc:  # noqa: BLE001 - as the window: the build goes ahead as W9a's
                say(f"fact    carry_for raised {type(exc).__name__}: {exc}; the build goes ahead as W9a's")
                jb.carry = None
            if jb.carry is not None:
                kwargs["carry"] = jb.carry
        self.carry = jb.carry
        jb.journaled = self.write_journal(plan)
        steps = self.steps = []

        def work(s):
            jb.revision = tuple(getattr(s, "revision", ()) or ())
            return swbuild.build_gearbox(s, **kwargs, progress=steps.append)
        W.TRACE["calls"].clear()
        DOC_TRACE["calls"].clear()
        W.TRACE["on"] = DOC_TRACE["on"] = True
        started = time.monotonic()
        try:
            result, self.error = A.watched_wait(self.worker.submit(work), 3600, "the build", app_job=True)
        finally:
            W.TRACE["on"] = DOC_TRACE["on"] = False
        self.seconds = time.monotonic() - started
        self.revision = jb.revision
        self.calls = list(DOC_TRACE["calls"])
        if self.error is not None:
            say(f"        raised {type(self.error).__name__}: {self.error}")
            self._note(ui_text.Note(ui_text.job_failed(self.error, False), False))
            self.plan_solidworks()
            return plan, None
        for line in result.log_lines():
            say("        " + line)
        say(f"        in {self.seconds:.1f} s; {W.memory()}; old read {result.old_read!r}")
        self._note(self._finish_build(jb, result))
        self.plan_solidworks()
        return plan, result


def copy_desk(master, section):
    """W9a's ``copy_desk`` (the window's W9a path, its workbook open in this run's Excel), its desk a DeskD."""
    folder, path, book, desk = A.copy_desk(master, section, "RangeBox.xlsx")
    desk.__class__ = DeskD           # the same object; only its build is the carrying window's
    return folder, path, book, desk


# -- reads ---------------------------------------------------------------------------------------------------------


def fingerprints(paths):
    out = {}
    for p in paths:
        if os.path.isfile(p):
            with open(p, "rb") as handle:
                digest = hashlib.sha256(handle.read()).hexdigest()
            out[os.path.basename(p)] = (os.path.getsize(p), os.path.getmtime(p), digest)
    return out


def flags_now(folder):
    """GetSaveFlag of every open document of the copy, nothing opened or activated."""
    return run("save flags", lambda s: W.folder_flags(s, folder), 300)


def comp_of(s, name):
    return swcom.Session._component_by(findings.COMPONENT_FIND_ROUTE, s._doc(), name)  # noqa: SLF001


def bare(asm, work):
    """A job on an assembly already open, made the document read without opening or activating it (the app's own
    ``use_open_document``), in the build bracket."""
    def wrapped(s):
        s.begin_build()
        try:
            if s.use_open_document(asm) is None:
                raise swcom.SolidWorksError(f"{os.path.basename(asm)} is not open")
            return work(s)
        finally:
            s.end_build()
    return wrapped


def raw_states(asm, names, open_already=True):
    """Each named component's GetSuppression2 in the mode showing (and SprocketConf's ReferencedConfiguration), by the
    script's own raw reads, nothing set."""
    def work(s):
        out = {}
        for n in names:
            c = comp_of(s, n)
            out[n] = None if c is None else int(swcom._read(c, "GetSuppression2"))  # noqa: SLF001
        return out
    return run("the components' states", bare(asm, work) if open_already else job(asm, work), 300)


def set_state_in(asm, name, state):
    """The user sets a component lightweight (1) or resolved (2) in the mode showing of ``asm`` (open)."""
    def work(s):
        c = comp_of(s, name)
        call(c, "SetSuppression2", state)
        return int(swcom._read(comp_of(s, name), "GetSuppression2"))  # noqa: SLF001
    got = run(f"{name} state {state}", bare(asm, work))
    say(f"person  {name} set to state {state} in {os.path.basename(asm)}: reads {got}")
    return got


def _frames(s, pairs, prefix):
    """Each body's frame and GetConstrainedStatus, a component suppressed where it is read found all the same
    (``suppressed_ok``) and its frame None where it will not read (W9a's reads would raise on it: M9 holds two)."""
    frames, status = {}, {}
    for i, (g, n) in enumerate(pairs):
        try:
            s.find_component(f"{prefix}{i}", n, lightweight_ok=True, suppressed_ok=True)
            frames[g] = s.component_frame(f"{prefix}{i}")
            status[g] = s.constrained_status(f"{prefix}{i}")
        except Exception as exc:  # noqa: BLE001 - a frame that does not read is said, as None
            frames[g], status[g] = None, f"unread: {type(exc).__name__}"
    return frames, status


def old_read(label, old, folder, pairs, modes, mates):
    """W9a's ``read_now`` of the old assembly where it stands (never opened or activated, nothing shown or rebuilt):
    frames, statuses, every mate's code and flag per mode and its entities (``mate_info``), the mode showing, the save
    flags before and after the read (a read that marks is §0.3's STOP); and every user component's state."""
    def work(s):
        out = {"flags_before": W.folder_flags(s, folder), "active": s.active_configuration(), "mates": {},
               "by_mode": {}, "entities": {}}
        try:
            out["needs_rebuild"] = int(swcom._read(call(s._doc(), "Extension"), "NeedsRebuild2"))  # noqa: SLF001
        except Exception as exc:  # noqa: BLE001
            out["needs_rebuild"] = f"unread: {type(exc).__name__}"
        out["frames"], out["status"] = _frames(s, pairs, "or")
        for i, m in enumerate(s.mate_states()):
            out["mates"][m.name] = (m.code, m.suppressed)
            s.find_mate(f"orm{i}", m.name)
            if modes:
                out["by_mode"][m.name] = s.mate_suppression(f"orm{i}", modes)
            if m.name in mates:
                info = s.mate_info(f"orm{i}")
                out["entities"][m.name] = (info.type, sorted(str(c) for c in info.components), info.whole)
        out["states"] = {n: (None if comp_of(s, n) is None else int(swcom._read(comp_of(s, n), "GetSuppression2")))  # noqa: SLF001
                         for g, n in pairs if g == n}
        out["flags_after"] = W.folder_flags(s, folder)
        return out
    got = run(f"read {label}", bare(old, work), 900)
    marked = sorted(n for n, v in got["flags_after"].items() if v and not got["flags_before"].get(n))
    if marked:
        A.stop(f"{label}: a read marked {marked} modified (ISSUE-1-PLAN §0.3)")
    say(f"read    {label}: {got['active']} showing; mates in error "
        f"{ {n: c for n, (c, sup) in got['mates'].items() if c and not sup} or 'none'}; marked "
        f"{W.marked(got['flags_after']) or 'none'}; rebuild state {got['needs_rebuild']}")
    return got


def every_mode(label, asm, pairs, modes):
    """W9a's every-mode read of the NEW assembly (each mode shown and rebuilt: frames, statuses, mate codes; then
    every mate's flag per mode), a component suppressed in a mode read as such (its frame None there)."""
    def work(s):
        out = {"frames": {}, "status": {}, "mates": {}, "by_mode": {}}
        for mode in modes:
            s.show_configuration(mode)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["frames"][mode], out["status"][mode] = _frames(s, pairs, f"em{mode}")
            out["mates"][mode] = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
        s.show_configuration(modes[0])
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        for i, m in enumerate(s.mate_states()):
            s.find_mate(f"emf{i}", m.name)
            out["by_mode"][m.name] = s.mate_suppression(f"emf{i}", modes)
        return out
    return run(f"every mode {label}", bare(asm, work), 1500)


def definitions_in(asm, names):
    """Each named mate's definition (``Session.mate_definition``) in ``asm`` (open), plain."""
    def work(s):
        out = {}
        for i, n in enumerate(names):
            try:
                s.find_mate(f"dm{i}", n)
                d = s.mate_definition(f"dm{i}")
                out[n] = {"type": d.type, "alignment": d.alignment, "flipped": d.flipped, "values": list(d.values),
                          "entities": [(e.component, e.kind, e.feature) for e in d.entities], "whole": d.whole}
            except Exception as exc:  # noqa: BLE001 - said, judged as not read
                out[n] = {"unread": f"{type(exc).__name__}: {exc}"}
        return out
    return run("the mates' definitions", bare(asm, work), 600)


def referenced_in(asm, name, modes):
    """``IComponent2.ReferencedConfiguration`` of ``name`` in each mode, shown in turn (raw gets; the first shown
    again): the new assembly only."""
    def work(s):
        first, out = s.active_configuration(), {}
        for mode in modes:
            s.show_configuration(mode)
            c = comp_of(s, name)
            out[mode] = None if c is None else str(swcom._read(c, "ReferencedConfiguration"))  # noqa: SLF001
        s.show_configuration(first)
        return out
    return run(f"{name}'s referenced configuration per mode", bare(asm, work), 300)


def frames_rel(frames, anchor_of):
    """Each component's pose relative to its anchor body, from one mode's frames ({body or Name2: frame})."""
    return {u: S0.relative(frames[a], frames[u]) for u, a in anchor_of.items() if u in frames and a in frames}


# -- the fixture -------------------------------------------------------------------------------------------------------


def extra_parts():
    """Chain, SprocketLight and SprocketConf: S0's sprocket's spec, each built by the strip into a file of its own (a
    file set lightweight sets every instance of it so, and a second configuration is the file's: neither may touch
    Sprocket.SLDPRT), once a run."""
    kept = os.path.join(OUT, "w9d-user-parts")
    if all(os.path.isfile(os.path.join(kept, n)) for n in OWN_PARTS):
        say("fact    the extra user parts built earlier into this <out> are used")
        return kept
    folder = W.fresh_folder("w9d-user-parts")
    for name in OWN_PARTS:
        path = os.path.join(folder, name)
        spec = S0.SPROCKET
        plan = S0.plan_for(spec, S0.kind_for(spec).derive(spec), "", path)
        result = run(f"build {name}", lambda s, p=plan: swbuild.build(s, p), 600)
        check(result.ok and bool(result.saved), f"fixture: {name} built and saved by the strip: {result.failures}")
    left = run("close", W.quit_in(folder))
    check(not left, f"fixture: the extra parts closed: left {left}")
    return folder


def second_configuration(path):
    """SprocketConf.SLDPRT given a second configuration, Z20 (the app's own add_configuration), its first shown again,
    so its document opens in Default while the component will reference Z20."""
    def work(s):
        names = list(s.configurations())
        s.add_configuration(CONF)
        s.show_configuration(names[0])
        return names, list(s.configurations()), s.active_configuration()
    got = run("SprocketConf's second configuration", job(path, work), 300)
    say(f"fact    fixture: SprocketConf.SLDPRT's configurations {got[0]} -> {got[1]}, showing {got[2]}")
    return got


def sun_cylinders(component):
    """Every cylindrical face of a component's part: (radius mm, coaxial with the part's Z axis, face)."""
    out = []
    for body in list(CP.raw(call(component, "GetModelDoc2"), "GetBodies2", 0, True) or []):
        for face in list(CP.raw(body, "GetFaces") or []):
            surface = CP.raw(face, "GetSurface")
            if CP.raw(surface, "IsCylinder"):
                p = [float(v) for v in CP.raw(surface, "CylinderParams")]
                axial = abs(abs(p[5]) - 1.0) < 1e-9 and abs(p[0]) < 1e-9 and abs(p[1]) < 1e-9
                out.append((round(p[6] * 1000.0, 6), axial, face))
    return out


def fixture_job(asm, folder, refs, modes):
    """The user's additions in one job: each component inserted (AddComponent5, the app's ``add_component``) at an
    identity frame, every mate made (the app's ``add_mate`` on named axes, planes and components; AddMate5 on faces,
    planes and a gear's face by the probes' ``raw_mate``), each set on in every mode and read back."""
    def work(s):
        out = {"components": {}, "mates": {}, "tries": {}, "faces": {}}
        for name in sorted({f for _, f, _ in INSERTS}):
            s.open_document(os.path.join(folder, name))
        s.open_document(asm)
        if s.active_configuration() != modes[0]:
            s.show_configuration(modes[0])
        for handle, name in refs.items():
            s.find_component(handle, name)
        for handle, file, at in INSERTS:
            out["components"][handle] = s.add_component(handle, os.path.join(folder, file), at)
            s.place_component(handle, I9, at, kind=swcom.ASSEMBLY_TRAIN)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        comps = {h: s._component(h) for h in ("c1", "c2", "s5", "sun")}  # noqa: SLF001
        faces = {h: CP.part_faces_of(c) for h, c in comps.items()}
        ends = {h: sorted((z, f) for k, z, f in fs if k == "plane" and z is not None) for h, fs in faces.items()}
        cyl = sun_cylinders(comps["sun"])
        coaxial = sorted(r for r, ax, _ in cyl if ax)
        off = sorted(r for r, ax, _ in cyl if not ax)
        out["faces"] = {"sun_coaxial_radii": sorted(set(coaxial)), "sun_off_axis_radii": sorted(set(off)),
                        "ends": {h: [z for z, _ in e] for h, e in ends.items()}}

        def pick(p, append):
            if isinstance(p, str):
                return lambda: s._component_ref(p, append)  # noqa: SLF001
            what, h = p
            if what == "bore":
                face = next(f for k, r, f in faces[h] if k == "cylinder" and abs(r - 5.0) < 1e-6)
            elif what in ("low", "high"):
                face = ends[h][0 if what == "low" else -1][1]
            elif what == "root":
                face = next(f for r, ax, f in cyl if ax and r == coaxial[0])
            else:
                face = next(f for r, ax, f in cyl if not ax and r == off[0])
            return lambda: CP.select_face(s, comps[h], face, append, 1)

        made = []
        for i, (name, how, kind, a, b, value) in enumerate(MATES):
            try:
                if how == "app":
                    if kind == "gear":
                        kept, _ = s.add_mate(f"fm{i}", "gear", a, b, 0.0, name, ratio=value)
                    elif kind == "lock":
                        kept, _ = s.add_mate(f"fm{i}", "lock", a, b, name=name)
                    else:
                        kept, _ = s.add_mate(f"fm{i}", kind, a, b, value, name)
                    status = s.mate_status(kept)
                else:
                    dist = value if isinstance(value, tuple) else (0.0, 0.0, 0.0)
                    kept, status = CP.raw_mate(s, name, kind, (pick(a, False), pick(b, True)), dist=dist)
                    s.find_mate(f"fm{i}", kept)
                made.append((f"fm{i}", kept))
                out["tries"][name] = f"made, status {status}"
            except Exception as exc:  # noqa: BLE001 - what SolidWorks answered; the item is then not shown
                out["tries"][name] = f"{type(exc).__name__}: {exc}"
                call(s._doc(), "ClearSelection2", True)  # noqa: SLF001
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        for handle, kept in made:
            s.set_mate_suppressed_in(handle, False, list(modes))
            out["mates"][kept] = s.mate_suppression(handle, list(modes))
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["codes"] = {m.name: (m.code, m.suppressed) for m in s.mate_states()}
        return out
    return work


def states_job(asm, names, modes):
    """Sprocket-7 suppressed in L and Sprocket-9 in H (each shown, SetSuppression2 there, as the probes did);
    SprocketConf-1 set to reference Z20 in every mode (``IComponent2.ReferencedConfiguration``, a put NEW to the
    repo); H shown again; then each mode shown and every user component's state and SprocketConf's referenced
    configuration read (the truth)."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        out = {"set": {}, "truth": {}, "referenced": {}}
        for handle, mode in SUPPRESS:
            s.show_configuration(mode)
            call(comp_of(s, names[handle]), "SetSuppression2", SUPPRESSED)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        for mode in modes:
            s.show_configuration(mode)
            c = comp_of(s, names["cf"])
            try:
                swcom._put(c, "ReferencedConfiguration", CONF)  # noqa: SLF001
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
                out["set"][mode] = "put"
            except Exception as exc:  # noqa: BLE001
                out["set"][mode] = f"{type(exc).__name__}: {exc}"
        for mode in modes:
            s.show_configuration(mode)
            out["truth"][mode] = {n: int(swcom._read(comp_of(s, n), "GetSuppression2"))  # noqa: SLF001
                                  for n in names.values()}
            out["referenced"][mode] = str(swcom._read(comp_of(s, names["cf"]), "ReferencedConfiguration"))  # noqa: SLF001
        s.show_configuration(modes[0])
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["shown"] = s.active_configuration()
        del doc
        return out
    return work


def section_fixture(out):
    say("== fixture  W9a's setup.master with §15's additions (W9D-INTERFACES §15): two clusters on feature mates, face "
        "mates, a face of Sun, a gear mate on Sun's Gear Axis, on a root cylinder and on a root fillet, a parallel and "
        "a limit distance, a component suppressed in L and one in H, a file of its own to be set lightweight, one in a "
        "second configuration, the tie, a mate to the assembly's own Front plane; saved with H showing; a quiet press "
        "records the inventory; kept as w9d-fixture.master")
    rb = C9.specs()[0]
    parts = extra_parts()
    folder, path, book, desk = copy_desk(A.user_master(), "w9d-fixture")
    kept = ""
    try:
        C9.same_sheets("fixture", desk, rb)
        box = desk.record.gearbox
        asm, modes = box.assembly, list(box.modes)
        for name in OWN_PARTS:
            import shutil
            shutil.copy2(os.path.join(parts, name), os.path.join(folder, name))
        out["configurations"] = second_configuration(os.path.join(folder, "SprocketConf.SLDPRT"))
        A.save_user(folder, "SprocketConf's second configuration")
        names = dict(W.bodies(box))
        refs = dict(SETUP, lay=box.layout_component, sun=names["Sun"])
        got = out["made"] = run("fixture: the user's additions", job(asm, fixture_job(asm, folder, refs, modes)), 1500)
        say(f"fact    fixture: inserted {got['components']}; Sun's cylinders: coaxial radii "
            f"{got['faces']['sun_coaxial_radii']}, off-axis {got['faces']['sun_off_axis_radii']}; end faces (z, part) "
            f"{got['faces']['ends']}")
        for name, said in got["tries"].items():
            say(f"        {name}: {said}")
        missing = [m for m, *_ in MATES if not got["tries"].get(m, "").startswith("made")]
        check(not missing, f"fixture: every mate made: not made {missing or 'none'} (an item not made is not shown)")
        wrong = {n: f for n, f in got["mates"].items() if any(f.values())}
        if wrong:
            A.stop(f"fixture: a new mate's flag did not read back on in every mode: {wrong} (§0.3)")
        bad = {n: c for n, (c, sup) in got["codes"].items() if c and not sup}
        check(not bad, f"fixture: every mate on in {modes[0]} reads code 0: {bad or 'none'}")
        comp_names = dict(SETUP, **got["components"])
        st = out["states"] = run("fixture: states and configuration", job(asm, states_job(
            asm, comp_names, modes)), 900)
        truth = st["truth"]
        off = {h: {m for m in modes if truth[m].get(comp_names[h]) == SUPPRESSED} for h, _ in SUPPRESS}
        check(off == {h: {m} for h, m in SUPPRESS} and st["shown"] == modes[0],
              f"fixture: Sprocket-7 suppressed in L alone, Sprocket-9 in H alone, H showing: {off}, {st['shown']}")
        check(all(v == CONF for v in st["referenced"].values()), f"fixture: SprocketConf-1 references {CONF} in every "
                                                                f"mode (the put: {st['set']}): {st['referenced']}")
        clashes = run("fixture: interference", lambda s: W.live_interferences(s, asm))
        say(f"fact    fixture: interferences with the user's components (facts): "
            f"{[(n, round(v, 3)) for n, v in clashes if set(n) & set(comp_names.values())]}")
        A.save_user(folder, "the fixture")
        left = run("close", W.quit_in(folder))
        check(not left, f"fixture: closed after the save: left {left}")
        say("-- fixture  a quiet press reads the inventory (W9d's entity kinds in it); it may refuse over the tie "
            "(K2), which records the inventory as read all the same")
        desk.plan_solidworks()
        result, _ = A.press(desk, "fixture: a quiet press")
        entry = desk.record.gearbox.user_work
        said = {c.name for c in entry.components} if entry is not None else set()
        mates = {m.name for m in entry.mates} if entry is not None else set()
        made_mates = [m for m, *_ in MATES if m not in missing]
        say(f"fact    fixture: the quiet press {'went through' if result is not None else 'refused: ' + str(desk.error)}"
            f"; problems on record {[(p.kind, list(p.mates)) for p in (entry.problems if entry else [])]}")
        check(entry is not None and set(comp_names.values()) <= said and set(made_mates + list(SETUP_MATES)) <= mates
              and all(m.entities for m in entry.mates),
              f"fixture: the record's inventory holds every component and mate, each mate's entities: missing "
              f"{sorted(set(comp_names.values()) - said)}, {sorted(set(made_mates) - mates)}")
        with open(os.path.join(folder, FIXTURE_JSON), "w", encoding="utf-8") as handle:
            json.dump({"names": comp_names, "mates": made_mates + list(SETUP_MATES), "made": got["tries"]}, handle,
                      indent=1)
        kept = A.w8_step(W.keep_master, CTX["worker"], folder, "w9d-fixture")
        MASTERS["fixture"] = kept
        check(bool(kept), f"fixture: kept as w9d-fixture.master: {kept}")
    finally:
        if not kept and not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "w9d-fixture", save=False)


def fixture_master():
    return _master_of("fixture", "w9d-fixture", section_fixture)


def _master_of(key, section, builder):
    """W9c's ``master_of`` for this script's master (its MASTERS dict is W9c's own)."""
    if MASTERS.get(key):
        return MASTERS[key]
    here = os.path.join(OUT, section + W.MASTER_SUFFIX)
    if not os.path.isdir(here):
        if os.path.exists(os.path.join(OUT, section)):
            raise AssertionError(f"{section} ran earlier in this <out> and kept no master")
        say(f"fresh   no {section}{W.MASTER_SUFFIX} in this <out>: {key} runs first")
        builder(RESULT["sections"].setdefault(key, {}))
    if not os.path.isdir(here):
        raise AssertionError(f"{key} kept no {section}{W.MASTER_SUFFIX}")
    MASTERS[key] = here
    return here


def load_fixture(folder):
    with open(os.path.join(folder, FIXTURE_JSON), encoding="utf-8") as handle:
        return json.load(handle)


# -- the press, and what it must leave alone ---------------------------------------------------------------------------


def the_edit(label, desk, book):
    """§15's edit typed in Excel (W8's ``edit``, from the fixture's own rows): Build again…, for Sun's Flank and the
    new shaft; the question printed in full."""
    rb = C9.specs()[0]
    C9.edit_live(desk, book, C9.row_edits(rb, edit_spec(rb)), f"{label}: Sun's Flank to arcs, a shaft Aux added")
    u, plan = desk.update, desk.plan
    said = " ".join(u.structural) if u is not None else ""
    check(u is not None and u.needs_new_revision and "Flank" in said and "Aux" in said and plan is not None
          and not plan.refusal and plan.revision == 2,
          f"{label}: classify sends it to Build again… as RangeBox_r2, for Sun's Flank and the shaft Aux: "
          f"{u and list(u.structural)}")
    question = ui_text.build_again_question(u, plan, record=desk.record)
    say(f"question {question}")
    return u, plan, question


def press_build(label, desk, folder, fx, old_open=True, shows_ok=False):
    """Build again… pressed as the window runs it (the footer must offer it), bracketed: every user file's and the
    old assembly's fingerprint (size, time, hash) and every open document's GetSaveFlag before and after; the old
    assembly, where open, read where it stands before and after (frames, codes, flags per mode, entities, states, the
    mode showing); the traced calls held to §3's *Never written*; no window. A change is §0.3's STOP."""
    box = desk.record.gearbox
    old, modes = box.assembly, list(box.modes)
    users = [os.path.join(folder, n) for n in ("Sprocket.SLDPRT", "Housing.SLDPRT") + OWN_PARTS]
    pairs = W.bodies(box) + [("layout", box.layout_component)] + [(n, n) for n in fx["names"].values()]
    f = desk.say_footer(f"{label}, before the build")
    check(f.build_enabled and f.build_action == ui_text.BUILD_AGAIN,
          f"{label}: the footer offers Build again… ({f.build_label!r}, enabled {f.build_enabled})")
    prints = fingerprints([old] + users)
    before = old_read(f"{label}: the old assembly before", old, folder, pairs, modes, fx["mates"]) if old_open else None
    flags = flags_now(folder)
    windows = S0.sw_windows()
    _, result = desk.build()
    new, counted = A.windows_new(windows)
    A.watch_check(f"{label} build")
    if counted:
        A.stop(f"{label}: a window came up during the Build again…: {counted} (§0.3: any dialog)")
    if result is None:
        raise AssertionError(f"{label}: the build raised: {desk.error}")
    out = {"seconds": round(desk.seconds), "calls": desk.calls, "flags_before": flags, "flags_after": flags_now(folder)}
    say(f"fact    {label}: the build took {desk.seconds:.0f} s; GetSaveFlag before {W.marked(flags) or 'none'}, after "
        f"{W.marked(out['flags_after']) or 'none'}")
    mine = {os.path.basename(p) for p in [old] + users}
    turned = [n for n in mine if out["flags_after"].get(n) and not flags.get(n)]
    if turned and old_open:
        A.stop(f"{label}: the Build again… marked {turned} modified (§0.3)")
    if old_open:
        after = old_read(f"{label}: the old assembly after", old, folder, pairs, modes, fx["mates"])
        changes = old_diff(before, after, mine)
        if changes:
            A.stop(f"{label}: the Build again… changed the old assembly: {changes} (§0.3)")
        check(True, f"{label}: the old assembly's save flag, mode showing ({after['active']}), every component's frame "
                    "and state, every mate's code, flag per mode and entities as before")
    changed = fingerprint_diff(prints, fingerprints([old] + users))
    if changed:
        A.stop(f"{label}: a user document's or the old assembly's file changed on disk: {list(changed)} (§0.3, W9d)")
    check(True, f"{label}: the old assembly and every user file unchanged on disk (size, time, hash): {sorted(prints)}")
    new_asm = os.path.basename(desk.record.gearbox.assembly)
    problems = trace_problems(desk.calls, os.path.basename(old), [os.path.basename(p) for p in users], new_asm,
                              read_only_old=not old_open, shows_ok=shows_ok)
    say(f"fact    {label}: traced calls on the old assembly and the user's files "
        f"{[c for c in desk.calls if c[1] in mine] or 'none'}; saves {[c for c in desk.calls if c[0] in ('SaveAs3', 'Save3')]}")
    if problems:
        A.stop(f"{label}: the traced calls break §3's Never written: {problems}")
    check(True, f"{label}: no write, show, rebuild, save or close of the old assembly or a user document in the traced "
                f"calls, and nothing saved after {new_asm}'s first save")
    out["status"] = desk.note[0] if desk.note else ""
    say(f"status  ({label}, after the build) {out['status']}")
    return result, out


def carry_facts(label, cr, out):
    """What R read that only the fake had shown (W9D-PACKAGE-A.md "still shown only on the fake"), as facts."""
    w = cr.work
    out["facts"], out["changed_files"] = list(cr.facts), list(cr.changed_files)
    for line in cr.facts:
        say(f"fact    {label}: {line}")
    check(not cr.changed_files, f"{label}: no file changed on disk after the carry (CarryResult.changed_files): "
                                f"{cr.changed_files or 'none'}")
    out["work"] = None if w is None else {
        "how": w.how, "active": w.active, "modes": list(w.modes), "states_route": w.states_route, "marked": w.marked,
        "left": w.left, "unread": w.unread, "walks": list(w.walks),
        "components": {c.name: {"kind": c.kind, "fixed": c.fixed, "state": c.state, "frame": c.frame is not None,
                                "configuration": c.configuration, "active": c.active_configuration,
                                "configurations": c.configurations, "suppressed_in": c.suppressed_in}
                       for c in w.components},
        "mates": {m.name: {"type": m.type, "type_name": m.type_name, "alignment": m.alignment, "flipped": m.flipped,
                           "values": list(m.values), "on": list(m.on), "code": m.code, "whole": m.whole,
                           "entities": [(e.what, e.owner, e.kind, e.feature, bool(e.reference), e.coaxial,
                                         e.radius_mm, e.capped, e.unread) for e in m.entities]}
                  for m in w.mates}}
    if w is None:
        say(f"fact    {label}: nothing was read: {cr.stopped}")
        return
    say(f"fact    {label}: R read the old assembly {w.how}, {w.active} showing, modes {list(w.modes)}, states by "
        f"{w.states_route or 'nothing (D2)'}; marked {w.marked or 'none'}, left {w.left or 'none'}, unread "
        f"{w.unread or 'none'}")
    for name, c in out["work"]["components"].items():
        say(f"        {name}: state {c['state']}, frame {'read' if c['frame'] else 'NOT read'}, configuration "
            f"{c['configuration']!r} of {c['configurations']} (its document's {c['active']!r}), suppressed in "
            f"{c['suppressed_in']}")
    for name, m in out["work"]["mates"].items():
        say(f"        {name}: {m['type_name']} type {m['type']}, alignment {m['alignment']}, flipped {m['flipped']}, "
            f"values {m['values']}, on {m['on']}, code {m['code']}, entities {m['entities']}")


def judge_carry(label, desk, fx, result, closed, light, out):
    """The carry's outcome against what the findings as they stand say it must be (``expected_outcome``), and the
    new revision read again by the script in every mode: each remade mate's definition and flags per mode as the
    old one's, each carried component's state per mode and pose against its anchor, every app gear free, the
    interference with a carried component said. Returns what the proposals rest on."""
    cr = result.carry
    fs = probe_reads(year())
    names = fx["names"]
    old_of = dict(cr.inserted)                       # old Name2 -> new Name2
    named = [(n.item, n.what, n.why) for n in cr.named]
    for n in cr.named:
        say(f"        named {n.item} ({n.what}): {n.why} {list(n.subjects)}")
    got = outcome_of([r[0] for r in cr.remade], named, [f.deleted for f in cr.fixed])
    want = expected_outcome(fs, fx["mates"], closed=closed, light=light)
    wrong = outcome_problems(want, got)
    out["outcome"], out["expected"] = got, {k: sorted(v) for k, v in want.items()}
    clean = {"outcome": check(not wrong, f"{label}: every mate made again, named or fallen back as the findings say "
                                         f"({fs}): {wrong or 'as expected'}")}
    comps = {c: n for c, n in ((names[h], h) for h in names)}
    not_carried = {n.item: n.why for n in cr.named if n.what == "component"}
    allowed = {"s9": {swbuild.WHY_NO_FRAME}} if not closed else {"s7": {swbuild.WHY_NO_FRAME}}
    bad = {c: w for c, w in not_carried.items() if w not in allowed.get(comps.get(c), set())}
    clean["components"] = check(not bad and set(old_of) | set(not_carried) == set(names.values()),
                                f"{label}: every component carried ({len(old_of)}), or named only as a component "
                                f"suppressed in the mode showing may be: {not_carried or 'none'}; wrongly {bad or 'none'}")
    for c in [names[h] for h, _ in SUPPRESS]:
        say(f"fact    {label}: {c}, suppressed in {dict(SUPPRESS)} ... in the mode showing it was "
            f"{'carried as ' + old_of[c] if c in old_of else 'named ' + not_carried.get(c, '?')}")
    fell = [f for f in cr.fixed]
    tied = {names[h] for h in TIED}
    clean["fallback"] = check(len(fell) == 1 and fell[0].why == swbuild.FELL_TIE
                              and set(fell[0].deleted) == {"UserLock8a"} and set(fell[0].kept) == {"UserLock8b"}
                              and set(fell[0].components) == {old_of.get(t, t) for t in tied},
                              f"{label}: the tied cluster alone fell back, UserLock8a deleted, UserLock8b kept, "
                              f"{sorted(tied)} fixed: {fell}")
    clean["same_error"] = check(not cr.same_error and not cr.moved and not cr.stopped and cr.unsaved,
                                f"{label}: no mate back in an old error {cr.same_error}, nothing moved {cr.moved}, no "
                                f"stop {cr.stopped!r} {cr.skipped!r}, the new assembly unsaved {cr.unsaved}")
    states = dict(cr.states)
    want_states = expected_states(fs, closed)
    got_states = {h: set(states.get(old_of.get(names[h], ""), ())) for h in want_states if names[h] in old_of}
    clean["states"] = check(all(got_states[h] == want_states[h] for h in got_states),
                            f"{label}: Sprocket-7 and Sprocket-9 read suppressed in {got_states}, as the route says "
                            f"{want_states}")
    remade_on = {r[0]: set(r[2]) for r in cr.remade}
    old_on = {m.name: set(m.on) for m in cr.work.mates}
    flags_wrong = {n: (old_on.get(n), on) for n, on in remade_on.items() if on != old_on.get(n)}
    clean["flags"] = check(not flags_wrong, f"{label}: every remade mate on in the modes it was on in: "
                                            f"{flags_wrong or 'all'}")

    new_asm = desk.record.gearbox.assembly
    box = desk.record.gearbox
    modes = list(box.modes)
    carried = [n for n in old_of.values()]
    defs = out["definitions"] = definitions_in(new_asm, [r[1] for r in cr.remade])
    kind_of = {m.name: swbuild.carry_kind(m) for m in cr.work.mates}
    olds = {m.name: {"type": m.type, "alignment": m.alignment, "flipped": m.flipped, "values": list(m.values)}
            for m in cr.work.mates}
    unclean = {}
    for old_name, kept, _ in cr.remade:
        d = defs.get(kept, {})
        diff = ["not read: " + d["unread"]] if "unread" in d else definition_problems(olds[old_name], d,
                                                                                         kind_of[old_name])
        if diff:
            unclean[old_name] = diff
    clean["definitions"] = check(not unclean, f"{label}: every remade mate's definition in RangeBox_r2 as the old "
                                              f"one's: {unclean or 'all'}")
    pairs = W.bodies(box) + [("layout", box.layout_component)] + [(n, n) for n in carried]
    every = out["every"] = every_mode(f"{label}: RangeBox_r2 in every mode", new_asm, pairs, modes)
    by_mode = every["by_mode"]
    flags_read = {r[1]: {m for m in modes if not by_mode.get(r[1], {}).get(m, True)} for r in cr.remade}
    differ = {n: (sorted(remade_on[o]), sorted(flags_read.get(k, set()))) for o, k, _ in cr.remade
              for n in [k] if flags_read.get(k) != remade_on[o]}
    clean["flags_read"] = check(not differ, f"{label}: each remade mate's flag read again per mode as the carry said: "
                                            f"{differ or 'all'}")
    gear_ids = {g for g, _ in W.bodies(box)}
    status = every["status"]
    not_free = {m: {g: v for g, v in status[m].items() if g in gear_ids and v != findings.COMPONENT_UNDER_DEFINED
                    and g not in set(box.fixed)} for m in modes}
    not_free = {m: v for m, v in not_free.items() if v}
    say(f"fact    {label}: GetConstrainedStatus per mode of the app's bodies {status}")
    clean["free"] = check(not not_free, f"{label}: every app gear free to turn in every mode with the carried mates "
                                        f"on: {not_free or 'all'}")
    globals_ = B.part_globals(desk, ("RangeSlv", "HighDog", "LowDog"))
    every_b = B.mode_read(f"{label}: W9b's read", desk)
    B.judge_every(label, desk, every_b, globals_, banded=False, against_section3=False, out=out.setdefault("w9b", {}),
                  users=carried)
    gear_of = {n: g for g, n in W.bodies(box)}
    named_clashes = {}
    for mode, clash in cr.clashes:
        named_clashes.setdefault(mode, []).append((tuple(clash.gears), float(clash.volume)))
    judged = C9.interference_judged(every_b["interferences"], named_clashes, gear_of, carried)
    out["interference"] = judged
    say(f"fact    {label}: interference with the carried components per mode: SolidWorks {judged['volumes']}; the "
        f"carry named {named_clashes or 'none'}")
    check(not judged["unnamed"] and not judged["unseen"], f"{label}: every interference SolidWorks reports with a "
                                                          f"carried component the carry named, and none other: "
                                                          f"unnamed {judged['unnamed'] or 'none'}, unseen "
                                                          f"{judged['unseen'] or 'none'}")
    return clean, unclean, kind_of, got


def poses_judged(label, before, every_new, anchors, old_mode, out):
    """Each carried component's pose against its anchor in the new revision's every mode against its pose against
    that anchor in the old assembly's mode showing (§5.3; contradiction 6 on the closed path: read in L, placed in
    H). ``anchors`` {new Name2: (old Name2, anchor body id)}."""
    gaps = {}

    def rel(frames, anchor, name):
        if frames.get(name) is None or (anchor and frames.get(anchor) is None):
            return None
        return S0.relative(frames[anchor], frames[name]) if anchor else frames[name]   # "" the world frame
    old_rel = {old: rel(before, anchor, old) for new, (old, anchor) in anchors.items()}
    for mode, frames in every_new["frames"].items():
        for new, (old, anchor) in anchors.items():
            now = rel(frames, anchor, new)
            if old_rel.get(old) is not None and now is not None:
                gaps[(new, mode)] = pose_gap(old_rel[old], now)
    off = {f"{n} in {m}": round(g, 9) for (n, m), g in gaps.items() if g > POSE_TOL}
    out["poses"] = {f"{n} in {m}": g for (n, m), g in gaps.items()}
    return check(bool(gaps) and not off, f"{label}: each carried component at its pose against its anchor, as it stood "
                                         f"in {old_mode} of the old assembly, in every mode of RangeBox_r2 "
                                         f"({len(gaps)} reads): off {off or 'none'}")


def record_judged(label, desk, result):
    """Schema 10 on disk after the finish; the carry on the new revision's gearbox block; ``unsaved_at`` the new
    assembly's file time; the footer's line while it stands."""
    on_disk = C9.record_on_disk(desk)
    box = desk.record.gearbox
    carry = box.carry
    mtime = os.path.getmtime(box.assembly)
    line = ui_text.carry_footer_line(desk.record)
    f = desk.say_footer(f"{label}, after the build")
    ok = check(on_disk.get(store.LINK_SCHEMA_KEY) == 10 and carry is not None
               and (not result.carry.unsaved or abs(carry.unsaved_at - mtime) < 1e-6)
               and (not result.carry.unsaved or (line and line in f.text)),
               f"{label}: the record on disk at schema {on_disk.get(store.LINK_SCHEMA_KEY)} holds the carry (how "
               f"{carry and carry.how}, {len(carry.components) if carry else 0} components, "
               f"{len(carry.mates) if carry else 0} mates, {len(carry.named) if carry else 0} named), unsaved_at "
               f"{carry and carry.unsaved_at} against the file's {mtime}; the footer says {line!r}")
    return ok


# -- carry-gates ---------------------------------------------------------------------------------------------------


def section_gates(out):
    say("== carry-gates  every W9d write gate as it stands: the question says W9a's clause led by its finding, the press "
        "builds RangeBox_r2 as today and carries nothing, names everything, writes nothing to the old assembly or a "
        "user file; then each gate's own refusal by plan_carry on the read the press made")
    standing = {finding_name(g): getattr(findings, finding_name(g), None) for g in WRITE_GATES}
    say(f"findings {standing}; probe reads {probe_reads(year())}")
    folder, path, book, desk = copy_desk(fixture_master(), "carry-gates")
    try:
        fx = load_fixture(folder)
        C9.same_sheets("carry-gates", desk, C9.specs()[0])
        old = desk.record.gearbox.assembly
        run("carry-gates: the old assembly opened (the user's)", job(old, lambda s: s.active_configuration()))
        _, _, question = the_edit("carry-gates", desk, book)
        unset = [n for n, v in standing.items() if v is None and n.startswith("CARRY_INSERTS_ON")]
        check(not unset or (f"findings.{unset[0]}" in question and "Keyway" in question),
              f"carry-gates: the question leads W9a's clause with {unset or 'nothing (CARRY_INSERTS set)'} and names the "
              "Keyway")
        walks_before = len(LOGGED["entity_references"])
        result, facts = press_build("carry-gates", desk, folder, fx)
        out.update(facts)
        cr = result.carry
        check(result.ok and desk.record.gearbox.revision == 2 and cr is not None,
              f"carry-gates: RangeBox_r2 built and saved as today: ok {result.ok}")
        carry_facts("carry-gates", cr, out)
        walked = [r for r in LOGGED["entity_references"][walks_before:]]
        check(not cr.work.walks and not walked or getattr(findings, finding_name("CARRY_INSERTS"), None) is not None,
              f"carry-gates: no r3 walk while CARRY_INSERTS is None (N3, ruled): {cr.work.walks or walked or 'none'}")
        named = {n.item: (n.why, list(n.subjects)) for n in cr.named}
        comps = set(fx["names"].values())
        held = all(named.get(c, ("",))[0] == swbuild.WHY_UNMEASURED and any("CARRY_INSERTS_ON" in s for s in named[c][1])
                   for c in comps) if unset else True
        check(cr.inserted == [] and cr.remade == [] and not cr.unsaved and held and cr.work.how == swbuild.OLD_OPEN,
              f"carry-gates: nothing carried, every component named with CARRY_INSERTS, every mate named: "
              f"{len(named)} named")
        status = out["status"]
        check(not unset or (status.find("has not yet been shown to carry your work") > 0 and "Keyway" in status),
              "carry-gates: the result says W9a's sentence led by CARRY_INSERTS, and the Keyway")
        record_judged("carry-gates", desk, result)
        check(desk.record.gearbox.user_work is None and ui_text.carry_footer_line(desk.record) == "",
              "carry-gates: with nothing carried the new revision holds no inventory and the footer no carry line")

        say("-- carry-gates  each gate's own refusal, on what the press read: plan_carry (pure) with that gate as it "
            "stands and every other patched")
        refusals = out["refusals"] = {}
        for gate in WRITE_GATES:
            others = {k: v for k, v in WRITE_GATES.items() if k != gate}
            with patched_values(dict(others, **{gate: getattr(findings, finding_name(gate), None)}), year(), say=say):
                plan = swbuild.plan_carry(cr.work, desk.carry, tuple(W.TAG["revision"]))
            items = [(n.item, n.why) for n in plan.named if any(finding_name(gate) in str(s) for s in n.subjects)]
            refusals[gate] = items
            check(bool(items) or getattr(findings, finding_name(gate), None) is not None,
                  f"carry-gates: {finding_name(gate)} as it stands keeps back {items}")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "carry-gates", save=False)


# -- carry: the Done-when ------------------------------------------------------------------------------------------


def section_carry(out):
    say("== carry  the Done-when (§5 W9d, M9): the old assembly open with H showing, SprocketLight-1 set lightweight "
        "in the session; the edit; the question; the gates patched in this process; Build again…")
    folder, path, book, desk = copy_desk(fixture_master(), "carry")
    fx = load_fixture(folder)
    names = fx["names"]
    clean, light = {}, False
    unclean, kind_of, got = {}, {}, {}
    old = ""
    try:
        C9.same_sheets("carry", desk, C9.specs()[0])
        box = desk.record.gearbox
        old, modes = box.assembly, list(box.modes)
        shown = run("carry: the old assembly opened (the user's)", job(old, lambda s: s.active_configuration()))
        check(shown == modes[0], f"carry: the old assembly shows {shown} ({modes[0]} expected, as saved)")
        old_frames = old_frames_now("carry", old, folder, box, names)
        state = set_state_in(old, names["lt"], LIGHTWEIGHT)
        light = state in (1, 4)
        states = raw_states(old, list(names.values()))
        lit = [n for n, v in states.items() if v in (1, 4)]
        check(lit == [names["lt"]], f"carry: SprocketLight-1 alone reads lightweight (a file of its own): {lit}")
        _, plan, question = the_edit("carry", desk, book)
        with patched_values(WRITE_GATES, year(), say=say):
            q = ui_text.build_again_question(desk.update, plan, record=desk.record)
            say(f"question (the gates patched) {q}")
            check("Keyway" in q and "As read at" in q and "Flank" in q,
                  "carry: the question, gates patched, names the Keyway in Sun's part made new because its Flank "
                  "changed, with the time read")
            say(f"fact    carry: the question names UserSunFace (on Sun's face, not made again) "
                f"{'by name' if 'UserSunFace' in q else 'only within a count'}")
            out["question"] = q
            result, facts = press_build("carry", desk, folder, fx)
            out.update(facts)
            cr = result.carry
            check(result.ok and desk.record.gearbox.revision == 2 and cr is not None and cr.work.how == swbuild.OLD_OPEN,
                  f"carry: RangeBox_r2 built, checked and saved as today; the old assembly read open: "
                  f"{result.failures}")
            carry_facts("carry", cr, out)
            status = out["status"]
            check("Carried into RangeBox_r2, unsaved" in status and "Keyway" in status and "UserSunFace" in status,
                  "carry: the result says what was carried unsaved, the Keyway with why, the mate on Sun's face")
            clean, unclean, kind_of, got = judge_carry("carry", desk, fx, result, False, light, out)
            anchors = {new: (o, dict(cr.anchors).get(new, "")) for o, new in cr.inserted}
            clean["poses"] = poses_judged("carry", old_frames, out["every"], anchors, modes[0], out)
            conf = referenced_in(desk.record.gearbox.assembly, dict(cr.inserted).get(names["cf"], ""), modes)
            w = {c.name: c for c in cr.work.components}
            cf = w.get(names["cf"])
            clean["configuration"] = check(names["cf"] in dict(cr.inserted) and set(conf.values()) == {CONF},
                                           f"carry: SprocketConf-1 inserted in {CONF}, read back in every mode: {conf}")
            clean["referenced_read"] = check(cf is not None and cf.configuration == CONF
                                             and cf.active_configuration not in ("", CONF),
                                             f"carry: R read SprocketConf-1's referenced configuration "
                                             f"{cf and cf.configuration!r} beside its document's "
                                             f"{cf and cf.active_configuration!r} (REFERENCED_CONFIGURATION_READ)")
            lt = w.get(names["lt"])
            say(f"fact    carry: SprocketLight-1, lightweight, read its file's configurations closed "
                f"(ISldWorks.GetConfigurationNames(path)): {lt and lt.configurations}; carried "
                f"{names['lt'] in dict(cr.inserted)}")
            unsaved = run("carry: RangeBox_r2's save flag", lambda s: W.folder_flags(s, folder), 300)
            r2 = os.path.basename(desk.record.gearbox.assembly)
            clean["unsaved"] = check(unsaved.get(r2) is True and cr.unsaved,
                                     f"carry: RangeBox_r2 holds the carried items unsaved (GetSaveFlag {unsaved.get(r2)})")
            record_judged("carry", desk, result)
        out["clean"] = clean

        say("-- carry  the user saves RangeBox_r2 (and nothing else): the footer's line goes")
        if light:
            set_state_in(old, names["lt"], RESOLVED)
            light = False
        r2 = desk.record.gearbox.assembly
        run("carry: the user saves RangeBox_r2", save_one(r2), 600)
        desk.read()
        check(ui_text.carry_footer_line(desk.record) == "", f"carry: after the save the footer's carry line is gone: "
                                                           f"{ui_text.carry_footer_line(desk.record)!r}")
    finally:
        _propose(clean, unclean, kind_of, got, fx)
        if light and old and not W.HUNG["on"]:
            try:
                set_state_in(old, names["lt"], RESOLVED)
            except Exception as exc:  # noqa: BLE001 - said; the copy is closed unsaved
                say(f"fact    carry: SprocketLight-1 not resolved again: {exc}")
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "carry", save=False)


def save_one(path):
    """The person saves one document in SolidWorks (W8's ``save_modified_in``'s call, on that one)."""
    def work(s):
        for doc in W.documents(s._app):  # noqa: SLF001
            if os.path.normcase(str(call(doc, "GetPathName") or "")) == os.path.normcase(path):
                call(call(doc, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(),  # noqa: SLF001
                     swcom._null_dispatch(), swcom._out_long(), swcom._out_long())  # noqa: SLF001
                return True
        return False
    return work


def old_frames_now(label, old, folder, box, names):
    """The old assembly's app bodies' and user components' frames in the mode it shows, read where it stands."""
    pairs = W.bodies(box) + [("layout", box.layout_component)] + [(n, n) for n in names.values()]
    return old_read(f"{label}: the old assembly's frames", old, folder, pairs, [], [])["frames"]


def _propose(clean, unclean, kind_of, outcome, fx):
    inserts = bool(clean) and all(clean.get(k) for k in ("components", "states", "poses", "unsaved", "fallback",
                                                         "same_error", "free"))
    proposed(finding_name("CARRY_INSERTS"), True if inserts else None,
             f"carry: every user part inserted, placed against its anchor in every mode, fixed or floating, its state "
             f"set and read back per mode, the tied cluster fixed, nothing written to the old: {clean}")
    proposed(finding_name("CARRY_INSERTS_IN_A_CONFIGURATION"), True if clean.get("configuration") else None,
             "carry: SprocketConf-1 inserted in Z20 by AddComponent5 with its configuration, read back in every mode")
    proposed(finding_name("REFERENCED_CONFIGURATION_READ"), True if clean.get("referenced_read") else None,
             "carry: ReferencedConfiguration read Z20 on SprocketConf-1 beside its document's Default (R2)")
    kinds = kinds_clean({n: kind_of.get(n, "") for n in fx["mates"] if n in kind_of}, outcome, set(unclean))
    proposed(finding_name("CARRY_REMAKE_KINDS"), kinds or None,
             "carry: the kinds whose every mate was made again, read back equal and on in the modes it was on in "
             "(perpendicular, tangent and limit angle are not in the fixture)")
    gear_ok = outcome.get("UserGear6") == "remade" and "UserGear6" not in unclean
    proposed(finding_name("CARRY_GEAR_MATE_ON_AN_APP_GEAR"), True if gear_ok else None,
             f"carry: UserGear6 made again on the new Sun's Gear Axis with its ratio and sense read back "
             f"({outcome.get('UserGear6')}); UserGearRoot on a root cylinder {outcome.get('UserGearRoot')}")
    for name, why in STAY_NONE.items():
        proposed(finding_name(name), None, why)


# -- carry-closed ------------------------------------------------------------------------------------------------------


def section_closed(out):
    say("== carry-closed  the old assembly saved with L showing and nothing lightweight, then closed: the not-open "
        "read under R.2's conditions; RangeSlv's train read in L and placed in H; the R.2 refusals by closed-file "
        "reads; RangeBox_r2 closed unsaved and a later Update says the carry was lost")
    folder, path, book, desk = copy_desk(fixture_master(), "carry-closed")
    fx = load_fixture(folder)
    names = fx["names"]
    try:
        C9.same_sheets("carry-closed", desk, C9.specs()[0])
        box = desk.record.gearbox
        old, modes = box.assembly, list(box.modes)
        run("carry-closed: the user shows L", job(old, lambda s: s.show_configuration(modes[-1])), 300)
        A.save_user(folder, "L showing (the save also writes the assembly's references to this copy's files)")
        old_frames = old_frames_now("carry-closed", old, folder, box, names)
        left = run("carry-closed: closed", W.quit_in(folder))
        check(not left, f"carry-closed: everything of the copy closed: left {left}")
        _, plan, question = the_edit("carry-closed", desk, book)
        with patched_values(WRITE_GATES, year(), say=say):
            q = ui_text.build_again_question(desk.update, plan, record=desk.record)
            say(f"question (the gates patched) {q}")
            out["question"] = q
            route = findings.__dict__.get(finding_name("COMPONENT_STATE_PER_CONFIGURATION_ROUTE"))
            result, facts = press_build("carry-closed", desk, folder, fx, old_open=False, shows_ok=route is None)
            out.update(facts)
            cr = result.carry
            carry_facts("carry-closed", cr, out)
            w = cr.work
            check(result.ok and w is not None and w.how == swbuild.OLD_READ_ONLY and not w.left and not w.marked
                  and w.active == modes[-1],
                  f"carry-closed: read read-only ({w and w.how}), {w and w.active} showing as saved, nothing left open "
                  f"{w and w.left} or marked {w and w.marked}; unread {w and w.unread}")
            still = run("carry-closed: open names", W.open_names)
            check(os.path.basename(old) not in still, "carry-closed: the old assembly closed again by the job")
            clean, unclean, kind_of, got = judge_carry("carry-closed", desk, fx, result, True, False, out)
            anchors = {new: (o, dict(cr.anchors).get(new, "")) for o, new in cr.inserted}
            clean["poses"] = poses_judged("carry-closed", old_frames, out["every"], anchors, modes[-1], out)
            s2 = names["u2"]
            check(dict(cr.anchors).get(dict(cr.inserted).get(s2, ""), "") == "RangeSlv",
                  "carry-closed: Sprocket-2 placed against RangeSlv, read in L and placed in H (contradiction 6)")
            record_judged("carry-closed", desk, result)
            out["clean"] = clean

        say("-- carry-closed  R.2's refusals, by closed-file reads only (nothing opened)")
        carry = desk.carry
        refusals = out["refusals"] = {}

        def refusal(c):
            return lambda s: swbuild._not_open_refusal(s, c, list(s.documents()))  # noqa: SLF001
        other = dataclasses.replace(carry, written_on=(int(W.TAG["revision"][0]) - 2,))
        refusals["written"] = run("R.2 with a record written on another version", refusal(other), 120)
        check(bool(refusals["written"]), f"carry-closed: a record another version wrote is refused, nothing opened "
                                         f"(on 2026: before any read): {refusals['written']!r}")
        if OTHER_VERSION_FILE and os.path.isfile(OTHER_VERSION_FILE):
            alien = dataclasses.replace(carry, old=dataclasses.replace(carry.old, path=OTHER_VERSION_FILE))
            refusals["other_file"] = run("R.2 on a file the other version saved", refusal(alien), 300)
            check(bool(refusals["other_file"]) and "open_read_only" not in [n for n, _ in LOGGED["calls"][-3:]],
                  f"carry-closed: a file the other SolidWorks saved is refused, read closed only: "
                  f"{refusals['other_file']!r}")
        else:
            say("fact    carry-closed: no --other-version-file given (or not on disk): the other version's file's "
                "refusal is the fake's only here")

        say("-- carry-closed  RangeBox_r2 closed without saving; a later Update says the carry was lost")
        left = run("carry-closed: closed unsaved", W.quit_in(folder))
        check(not left, f"carry-closed: RangeBox_r2 and its parts closed without saving: left {left}")
        desk.plan_solidworks()
        f = desk.footer()
        if f.update_shown and f.update_enabled:
            result2, _ = C9.press(desk, "carry-closed: a later Update")
            said = desk.note[0] if desk.note else ""
            check("was closed without saving after Build again… carried your work into it" in said
                  and ui_text.carry_footer_line(desk.record) == "",
                  f"carry-closed: the later Update says the carry was lost and the mark goes: {said[-220:]!r}")
        else:
            say(f"fact    carry-closed: the footer offers no Update after the build (shown {f.update_shown}, enabled "
                f"{f.update_enabled}): the lost line is the fake's only here")
    finally:
        if not W.HUNG["on"]:
            A.w8_step(W.end_copy, CTX["worker"], folder, "carry-closed", save=False)


# -- the run -------------------------------------------------------------------------------------------------------------

ORDER = ["fixture", "carry-gates", "carry", "carry-closed"]
SECTIONS = {"fixture": section_fixture, "carry-gates": section_gates, "carry": section_carry,
            "carry-closed": section_closed}
FOLDERS = {"fixture": ["w9d-fixture", "w9d-fixture" + W.MASTER_SUFFIX], "carry-gates": ["carry-gates"],
           "carry": ["carry"], "carry-closed": ["carry-closed"]}


def done_here(name):
    return [p for p in (os.path.join(OUT, f) for f in FOLDERS.get(name, [name])) if os.path.exists(p)]


def main():
    A.SECTIONS.clear()
    A.SECTIONS.update(SECTIONS)
    if A._given in ("", "all"):                    # noqa: SLF001
        A.CHOSEN = list(ORDER)
    A.done_here = done_here
    A.RUN_TITLE, A.JSON_STEM = "W9d demonstration", "w9d-demo"
    return A.main()


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(W.LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(W.LOG) + "\n")
    raise SystemExit(code)
