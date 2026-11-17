"""The build's order, against a fake SolidWorks that records every call."""

import copy
import math
from dataclasses import dataclass, field, replace

import pytest

from gear_generator import findings, swbuild, swcom
from gear_generator.gears import KINDS
from gear_generator.gears.base import BuildPlan, CloseSketch, Dimension, LinkDimension, SaveAs
from gear_generator.gears.equations import DEGREES, RADIANS, split_equation
from gear_generator.spec import GearSpec
from gear_generator.swcom import ComponentGone, DocInfo, SolidWorksError

SPUR = KINDS["spur"]
PATH = r"C:\Gears\Gear_m1.5_N25.SLDPRT"


def _key(path):
    return path.replace("/", "\\").lower()


@dataclass
class FakeMate:
    """One mate the fake holds (W5-PLAN §3.1): ``a`` and ``b`` are ``(component Name2, target)`` — ``("asm",
    "plane2")`` for the assembly's own plane, target ``""`` for a lock's bare component — ``link`` the global its
    D1 is linked to, ``status`` what AddMate5 answered, ``code``/``warning`` what GetErrorCode2 reads."""

    name: str
    kind: str
    a: tuple
    b: tuple
    value: float = 0.0
    ratio: tuple = (1.0, 1.0)
    flip: bool = False
    link: str = ""
    suppressed: bool = False
    status: int = 1
    code: int = 0
    warning: bool = True
    # W8: the flag in every configuration (``suppressed`` is always the active one's), and a distance mate's value
    # set in a configuration of its own (mm, a magnitude; a configuration with none stands at ``value``)
    flags: dict = field(default_factory=dict)
    own: dict = field(default_factory=dict)
    # W9a: a mate the user made in SolidWorks (``FakeSolidWorks.user_mate`` / ``user_lock``): the fake fails a test on
    # any write to it (W9a's §0.3 STOP: nothing not on record is written but route (c1)'s puts)
    user: bool = False
    # W9d: IMate2.Alignment as made, and a limit mate's range (MaximumDistance … as the definition reads them)
    alignment: int = 0
    limits: tuple = ()

    @property
    def axis(self):
        """An anchor's axis mate: a coincident between two axes of two components (the gear's, the layout's)."""
        return (self.kind == "coincident" and "asm" not in (self.a[0], self.b[0])
                and self.a[1].endswith("Axis") and self.b[1].endswith("Axis"))

    @property
    def along(self):
        """An anchor's place along its shaft: its origin on, or at a distance from, a component's plane."""
        return self.kind in ("point", "point distance") and self.a[1] == "origin" and self.b[0] != "asm"


IDENTITY9 = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

# The Flip each app-built pair needed on each version (probe ring_mate_sense, findings.GEAR_MATE_FLIP_NEEDED_ON_2026
# and _2024), copied here so the fake does not lean on findings.py: keyed by the gear kind, then the pinion's and the
# ring's shaft sense; an outside pair needed False everywhere.
FLIP_NEEDED_2026 = {
    "spur ring ++": True, "spur ring +-": False, "spur ring -+": False, "spur ring --": True,
    "helical ring ++": True, "helical ring +-": True, "helical ring -+": True, "helical ring --": True,
    "plain annulus": False, "external +-": False,
    # W8 spike, 2026: a collinear spline (spur to spur) and coupling (to a ring) each right with Flip False
    "collinear ++": False, "collinear ring ++": False}
FLIP_NEEDED_2024 = {
    "spur ring ++": False, "spur ring +-": True, "spur ring -+": True, "spur ring --": False,
    "helical ring ++": False, "helical ring +-": False, "helical ring -+": False, "helical ring --": False,
    "plain annulus": False, "external +-": False,
    # W8 spike, 2024: the collinear spline right with Flip True, the coupling to a ring with Flip False
    "collinear ++": True, "collinear ring ++": False}


def _rot_z(degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return (c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0)


def _mul(r1, r2):
    return tuple(sum(r1[i * 3 + k] * r2[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3))


def _apply(r, v):
    return tuple(sum(r[i * 3 + k] * v[k] for k in range(3)) for i in range(3))


def _compose(f1, f2):
    """``f1 ∘ f2`` for frames (rotation by rows, origin): ``v ↦ R1 (R2 v + t2) + t1``."""
    (r1, t1), (r2, t2) = f1, f2
    moved = _apply(r1, t2)
    return _mul(r1, r2), tuple(moved[i] + t1[i] for i in range(3))


def _inverse(f):
    r, t = f
    rt = tuple(r[j * 3 + i] for i in range(3) for j in range(3))
    back = _apply(rt, t)
    return rt, tuple(-x for x in back)


def _frame_off(f1, f2):
    """(largest rotation-entry difference, largest origin difference in mm) between two frames."""
    return (max(abs(a - b) for a, b in zip(f1[0], f2[0])), max(abs(a - b) for a, b in zip(f1[1], f2[1])))


class FakeSolidWorks:
    """Records every call. ``fail_on`` maps a call's name to a sentence it raises (or ``(arg, sentence)`` to
    raise only when that argument is passed).

    W4's members are configurable from the start: ``open_docs`` are the
    documents open before the job (``documents()``), and a document saved or
    opened joins them (``close_all`` empties them, as closing SolidWorks
    without saving would); ``saved`` is each file as saved and ``memory``
    each open document as it is now, so a change not saved is lost when it
    is closed, and ``has_unsaved_changes`` (``GetSaveFlag``) reads whether
    the document just opened differs from its file; a saved document keeps
    its globals and the planes and axes it made, and ``open_document`` brings
    them back, so ``planned_changes`` and ``feature_names`` see what a build
    left; ``missing_components`` are Name2s ``find_component`` will not find;
    ``frames`` maps a handle to the (rotation, at) ``component_frame`` reads,
    and ``place_component`` writes it; ``clashes`` is what ``interferences()``
    returns.

    For W4's own tests: ``frames`` may also be keyed by a component's Name2
    (what ``find_component`` was asked for), and ``place_component`` writes
    both; ``exists`` answers "is it on disk" from what was saved (or put in
    ``saved`` by a test), so a job's pre-flight sees what an earlier job left.

    For the W4 review's: ``raises`` maps a call's name to ``(n, exception)``:
    the n-th call of that name raises that exception, whatever its type (a
    stand-in for ``pywintypes.com_error`` or anything unexpected, part-way
    through a job). ``touched`` collects the saved documents (lower-cased
    paths) a call has modified since they were opened — an equation added or
    deleted (the trig check), a global set, a component moved, a rebuild —
    so a test can see which documents SolidWorks would now mark modified.
    Every feature a build makes (not only planes and axes) is kept with the
    saved document, so ``feature_names`` on a reopened part lists them.

    Rebuilding, as probe assembly_rebuild_scope found it on SolidWorks 2026
    and 2024: ``rebuild`` (and the rebuild ``place_component`` makes of its
    own) asks :func:`swcom.rebuild_call` for the member, as ``Session`` does,
    and acts as SolidWorks did. On a part it marks the part. On an assembly
    (a new one, or a saved ``.sldasm``) it marks the assembly, and a FULL
    rebuild (``ForceRebuild3(False)``) marks every component document too
    (``assembly_components`` keeps each saved assembly's inserted paths); any
    component in ``failed_documents`` makes it return False, top-only or not,
    and so does a part of it with a feature in error (``feature_codes``),
    where findings.ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_<year> is
    False for the fake's revision (W9a's m3 and k3 on 2026); there such a
    part's components read code 1 (m3's Sprocket-1).
    A put alone marks nothing (``findings.PUT_MARKS_ASSEMBLY_MODIFIED``).
    Running interference detection marks the assembly (the probe saw the
    reads after a put mark it, frame reads and the check together; which of
    them is not isolated, and the fake pins it on the check). The kind each rebuild
    was asked for (``kind``) and the member it took are kept in
    ``rebuild_kinds`` and ``rebuild_members``. Nothing unprobed is modelled:
    not a rebuild under ``CommandInProgress``, not what a top-only rebuild
    does to mates.

    W5, the train's mates (W5-PLAN §3.1 as W5-DECISIONS rules it). ``add_mate`` keeps a :class:`FakeMate` per
    mate in the document it is made in — saved with it, back on ``open_document``, lost by ``close_all`` unless
    saved — keyed by the components' Name2s. Its AddMate5 status is always 1. The one over-definition tier 8
    recorded is modelled as it was recorded (``compound_lock``, "lock, both on the shaft", probe/results/latest.json):
    a lock whose follower is also mated to its shaft — every AddMate5 still answered 1 and the lock itself was not
    flagged, but the along mates of both gears read error code 46 as warnings — so here, while such a lock and such
    a mate are both unsuppressed, the along mates of its anchor and follower read code 46, warning True. Nothing
    else is flagged by default: a second axis mate or a loop of gear mates was never probed, so a test that wants
    one says so through the override knobs (made up, and named so there). ``mate_status``,
    ``mate_states``, ``constrained_status`` (4 for a component in a flagged mate, 3 if fixed, else 2),
    ``find_mate`` (``MateGone`` when the mate is not there), ``set_mate_suppressed`` and ``set_gear_ratio`` (the
    remake: the mate goes to the end of the tree under its old name; any other route refused as swcom refuses
    it) answer from those. Overrides doctor them per test: ``mate_statuses={name: n}``, ``mate_codes={name:
    (code, warning)}``, ``constrained={Name2 or handle: n}``. So a default ``FakeSolidWorks()`` answers clean
    mate states for an undoctored plan. ``link_dimension`` remembers which global a mate's D1 is linked to.
    ``mate_states(others=[...])`` also names the document's ``user_folder``s (sub-features of the MateGroup that
    are not mates: a folder's two "FtrFolder" entries, skipped by ``findings.MATE_FOLDER_TYPE_NAME`` as swcom skips
    them, and ``user_entry``s of any other type); ``raises_after`` is ``raises`` for ``set_mate_suppressed``,
    raised once the suppression took.

    A rebuild of an assembly holding mates (``rebuild`` and every put's own) solves them as far as the fake can:
    each anchor with an unsuppressed axis mate goes to its shaft's axis as the layout document's ``"<Shaft> X"``
    / ``"<Shaft> Y"`` globals now say (0 where there is none: a base-side shaft), and along it to its Face Z
    global (or the mate's value) — signed as the mate was made — turned 13° the wrong way about its own axis if
    its X/Y moved (standing in for SolidWorks' swing); a follower under an unsuppressed lock keeps its frame
    relative to its anchor through that. ``place_component`` reads the frame back after its rebuild and raises
    as ``swcom.place_component`` would when a mate pulled the gear off it. A put on a gear held by an
    unsuppressed lock moves that gear alone, leaves its partner where it was and reports nothing, as SolidWorks
    did (W5-DECISIONS, "a lock does not hold against a put"); ``locked_puts`` lists each such put, so a test
    catches app code that puts with a lock on. ``slips`` (Name2s) turns those gears 5° on every later
    ``rebuild()`` of the assembly: a put that does not hold. Nothing else is solved: a gear mate turns nothing
    (no solver, no drive, no drag).

    W6, turned axes (W6-PLAN §4.2, row A). Components stand on any frame. The layout part's axes are read from its
    plan's ops as it is built, never from the planning code: an axis through two planes lies where they cross,
    each plane a base plane (Front plane1 holds z = 0, Top plane2 y = 0, Right plane3 x = 0) or a plane made from
    one, whose coordinate is the layout's ``"<Shaft> X/Y/Z"`` global (0 when there is none), the axis running along
    the remaining coordinate; a ``line_axis`` is a fixed line. Both are saved with the layout document.
    ``axis_line`` reads one back; ``moved_lines={axis name: (point, direction)}`` stands for a line axis moved in
    SolidWorks. A rebuild carries each anchor onto its layout axis wherever it points, and along it to the
    coordinate its along mate holds along that mate's plane's normal (plane1 z, plane2 y, plane3 x), signed as the
    mate was made (W6-INTERFACES §7.6). ``gear_mate_sense`` answers by rule H (``swcom.sense_reading``) from a
    Reverse and two entity directions that tell the mate's TRUE sense: on parallel axes W5's, from the ring tables;
    on turned axes the fake works the mesh's true sense out itself from where the gears stand (``_true_same``;
    ``turned_senses[name]``, ``k > 0``, overrides it), never from the caller, and a turned mate turns right when its Flip is ``turned_flip_needed`` (made up: no probe ties a
    turned Flip to anything). It gates a turned mate as ``Session`` does (the turned finding, the angles for axes
    that meet or pass each other). Overrides: ``turned_reverse={name: bool}`` fixes the Reverse SolidWorks reads,
    whatever the mate does (the rule failing); ``entity_senses={name: (±1, ±1)}`` points an entity against its
    gear's axis (tier 9 never saw it, W6-INTERFACES §7.12); ``entity_swapped`` (names) gives the entities in the
    other order; ``entity_stray={name: direction}`` reads the first entity along something else.
    """

    def __init__(self, trig=DEGREES, fail_on=None, rename=None, rebuild_ok=True, statuses=None, values=None,
                 interference=(0, 0.0), open_docs=(), missing_components=(), frames=None, clashes=(), raises=None,
                 failed_documents=(), mate_statuses=None, mate_codes=None, constrained=None):
        self.interference = interference
        self.revision = (34, 0, 0)
        self.calls = []
        self.trig = trig
        self.fail_on = fail_on or {}
        self.rename = rename or {}
        self.rebuild_ok = rebuild_ok
        self.statuses = statuses or {}
        self.values_override = values or {}
        self.suppressed = False
        self.equations_text = []
        self.active = None
        self.handles = set()
        self.open_docs = list(open_docs)
        self.missing_components = set(missing_components)
        self.frames = dict(frames or {})
        self.clashes = list(clashes)
        self.made = []                 # planes and axes made in the current document, by kept name
        self.saved = {}                # lower-cased path -> (equations_text, made) as saved: the file
        self.memory = {}               # lower-cased path -> (equations_text, made) as open in SolidWorks now
        self.found = {}                # handle -> the Name2 find_component found it by
        self.raises = dict(raises or {})
        self.counts = {}
        self.current = ""              # the document calls act on: an opened or saved path, "" for a new one
        self.touched = set()
        self.kind = 1                  # the GetType of a new document: 1 part, 2 assembly
        self.adding = []               # the paths inserted into the new assembly so far
        self.assembly_components = {}  # lower-cased .sldasm path -> the paths it was saved with
        self.failed_documents = {_key(p) for p in failed_documents}
        self.rebuild_kinds = []        # the ``kind`` each rebuild was asked with
        self.rebuild_members = []      # what rebuild_call gave each rebuild, a put's own included
        self.assembly_kinds = []       # the ``kind`` each assembly rebuild (a put's own included) was asked with
        # W5
        self.mates = []                # the current document's FakeMates, in tree order
        self.saved_mates = {}          # lower-cased path -> its mates as saved
        self.memory_mates = {}         # lower-cased path -> its mates as open in SolidWorks now
        self.component_names = {}      # handle -> the Name2 add_component gave or find_component found
        self.component_paths = {}      # Name2 -> the file it was inserted from
        self.fixed = set()             # Name2s fixed in place
        self.mate_handles = {}         # handle -> the mate name add_mate made or find_mate found under it
        self.mate_statuses = dict(mate_statuses or {})
        self.mate_codes = dict(mate_codes or {})
        self.constrained = dict(constrained or {})
        self.locked_puts = []          # Name2s put while an unsuppressed lock held them
        self.slips = set()
        self.mate_folders = {}         # lower-cased path -> names of MateGroup sub-features that are not mates
        self.raises_after = {}         # call name -> (n, exception): raised by the n-th call, after its effect
        self.counts_after = {}
        self.lightweight = set()       # Name2s loaded lightweight (component_resolved reads False for them)
        self.held_suppressed = set()   # mate names an unsuppress does not take on (in a suppressed folder, say)
        self.flip_needed = dict(FLIP_NEEDED_2026)      # this fake's version: the Flip each case needs
        self.ring_parts = set()        # part paths that are rings (also: a file named "Ring…", as the app names one)
        self.helical_parts = set()     # part paths that are helical (also: a stem ending "_20L", as the app names one)
        self.never_right = set()       # gear mate names SolidWorks turns the wrong way whatever the Flip (made up)
        # W6
        self.plane_defs = {}           # plane handle and name -> its base plane (1 Front, 2 Top, 3 Right), this document
        self.axis_defs = {}            # axis name -> ("planes", (index, index)) or ("line", point, direction)
        self.saved_axes = {}           # lower-cased path -> axis_defs as saved
        self.memory_axes = {}          # lower-cased path -> axis_defs as open now
        self.moved_lines = {}          # axis name -> (point, direction): a line axis moved in SolidWorks
        self.turned_senses = {}        # turned gear mate name -> its mesh's true same sense (k > 0)
        self.turned_flip_needed = False
        self.turned_reverse = {}       # gear mate name -> the Reverse SolidWorks reads whatever the mate does
        self.entity_senses = {}        # gear mate name -> (±1, ±1): each entity along or against its gear's axis
        self.entity_swapped = set()    # gear mate names whose entities come back in the other order
        self.entity_stray = {}         # gear mate name -> a direction its first entity reads along instead
        # W7
        self.judge_rank = True         # a gear mate adding nothing to the turn rows over-defines (W7-PLAN §2.9)
        # W8 (W8-PLAN §3.5, the W8 spike on SolidWorks 2026)
        self.configs = ["Default"]     # the current document's configurations, the template's first
        self.config = "Default"        # the active one
        self.template_config = "Default"
        self.frames_by = {}            # configuration -> its frames, for every configuration not active
        self.saved_configs = {}        # lower-cased path -> (configs, active, frames_by) as saved
        self.epoch = 0                 # raised by every add, show and open, as the Session's
        self.unsettled = 0             # flag calls left misbehaving after an add, until the next rebuild
        self.new_mate_elsewhere = "suppressed"   # or "on": a mate made outside the template's configuration
        self.shared_positions = False  # True: one set of frames for every configuration (GOTCHAS §83, made up here)
        # None: as above. A set (the configurations put in so far, empty to start): a put made in a configuration
        # stays in that configuration, while a turn given before any put there (turn, drive) shows in every
        # configuration not yet put in. Read twice on SolidWorks 2026 34.0.0 (W8 s2: probe/results/
        # w8-workbook-assembly-20261115-111951-s2-turn-carried-per-body.log and …-132348-s2-put-kept-per-
        # configuration.log) and not yet probed; modelled only as far as the fault it pins.
        self.put_splits = None
        self.clashes_in = {}           # configuration -> what interferences() returns there
        # configuration -> {mate name: (code, warning)} read by mate_states while that configuration is active, and
        # nowhere else (tier 11, SolidWorks 2026: two slides on in one configuration each read code 47, warning False,
        # there; every other configuration read 0). Empty: ``mate_codes`` and each mate's own, as before.
        self.mate_codes_in = {}
        # mate name -> the handles or Name2s it locks while on in the active configuration: they read fully defined
        # there, the mate itself made with status 1 and no error code (W8 s5 (ii), SolidWorks 2026: a 1 : 1 Sun-LoDog
        # coupling on in N alone locked N's rear train, seven bodies read fully defined, 140811-s5.log 894-900)
        self.locks = {}
        # W9a (ISSUE-1-PLAN §2.1; W9A-INTERFACES.md): the user's work. ``adding_names`` / ``assembly_names``: the
        # Name2s a new assembly was given / each saved assembly holds, so ``components()`` lists them; ``user_parts``:
        # lower-cased assembly path -> the user's components put in it by ``user_component``; ``component_codes``
        # and ``component_states``: Name2 -> its tree feature's error code / GetSuppression2 (else 0 / 2);
        # ``feature_codes``: (lower-cased path, feature) -> its error code (a part with one in error rebuilds False,
        # as P0 read on 2026 and 2024); ``user_features``: lower-cased path -> the user's features after the app's;
        # ``user_puts``: (Name2, frame, configuration) for each put of a user component — the only write to a user
        # item the fake allows (route (c1)); any other write to one raises AssertionError.
        self.adding_names = []
        self.assembly_names = {}
        self.user_parts = {}
        self.component_codes = {}
        self.component_states = {}
        self.feature_codes = {}
        self.user_features = {}
        self.user_puts = []
        # (lower-cased path) -> [(feature, code)] put in error by the next set_global_variable in that document, and
        # {mate: (code, warning)} given to mate_codes at the first put: a rebuild that breaks the user's work
        self.breaks_on_set = {}
        self.codes_after_put = {}
        # W9a review point 6: the app bodies put since the app's mates last went back on (or a configuration was
        # shown); a put of a user component is let through only when its user locks (on here) reach one of them.
        # ``unread_mates``: mate name -> "type", "count" or "entity", what mate_info will not give for it.
        self.step_puts = set()
        self.unread_mates = {}
        # W9c (the probes' review, must-fix 1): what a mate entity on the assembly's own plane names. "none": no
        # component, "" (SolidWorks 2024, the macro database); "root": the active configuration's root component,
        # named as the assembly (2026, findings.ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_2026). ``root_unread``: the
        # session's root read (root_component) answers nothing.
        self.assembly_entity = "none"
        self.root_unread = False
        # W9d (D5): mate_info gives each entity's kind and feature (Session.mate_info reads ReferenceType2); False, the
        # read before W9d (no kinds), which the suites before W9d were written against.
        self.read_entity_kinds = False
        # W9c (W9C-INTERFACES §4): each open document keeps its own configurations, as SolidWorks does, so a part built
        # or opened in the middle of an Update leaves the assembly's as they were (``memory_configs``, lower-cased
        # path -> (configs, active, template's, frames_by)). ``suppressed_features``: (lower-cased path, feature) ->
        # suppressed, as suppress_feature left it. ``deleted``: the Name2s delete_component took out.
        self.memory_configs = {}
        self.suppressed_features = {}
        self.deleted = []
        # swInputDimValOnCreate (findings.INPUT_DIM_VAL_ON_CREATE): on, as the user's SolidWorks had it in W9c's
        # demonstration; begin_build turns it off and end_build puts back what it found.
        self.dim_dialog_on = True
        self.dim_dialog_kept = None
        # W9c's demonstration, run 6 on 2026: a ring whose globals are set so its new flank start lands on where Li+
        # ends now (0.038 of its length measured failing, one tooth down) rebuilds with Tooth Space at code 72 and
        # Teeth at 1, and stays so in this session whatever is set after (a forced rebuild, the old count again).
        # Modelled from the ring's own geometry (gears.internal), not from gears.landing's foresight.
        self.values_before_set = {}        # lower-cased path -> its globals before the first set since a rebuild
        self.wrong_branch = set()          # lower-cased paths of rings left on the far branch

    def _log(self, name, *args):
        self.calls.append((name, args))
        self.counts[name] = self.counts.get(name, 0) + 1
        planned = self.raises.get(name)
        if planned is not None and planned[0] == self.counts[name]:
            raise planned[1]
        reason = self.fail_on.get(name)
        if reason and (not isinstance(reason, tuple) or reason[0] in args):
            raise SolidWorksError(reason if isinstance(reason, str) else reason[1])

    def active_document(self):
        return self.active

    def begin_build(self):
        """As ``Session.begin_build``: swInputDimValOnCreate read and turned off for the build's dimensions."""
        self._log("begin_build")
        if getattr(self, "begin_drops_document", False):
            self.current = ""                  # W9d (S4): as the Session's, the build document falls back to none
        self.dim_dialog_kept = self.dim_dialog_on
        self.dim_dialog_on = False

    def end_build(self):
        """As ``Session.end_build``: the user's swInputDimValOnCreate put back."""
        self._log("end_build")
        if self.dim_dialog_kept is not None:
            self.dim_dialog_on, self.dim_dialog_kept = self.dim_dialog_kept, None

    def _touch(self):
        if self.current:
            if _key(self.current) in getattr(self, "protected", ()) and \
                    _key(self.current) not in getattr(self, "read_only_opened", ()):
                raise AssertionError(f"the app wrote to {self.current}, the old assembly or a file of the user's "
                                     "(W9D §3: never written)")
            self.touched.add(_key(self.current))

    def _fresh_configurations(self):
        self.configs, self.config, self.template_config, self.frames_by = ["Default"], "Default", "Default", {}

    def _stash(self):
        """The document left keeps its configurations (W9c)."""
        if self.current:
            self.memory_configs[_key(self.current)] = (self.configs, self.config, self.template_config, self.frames_by)

    def new_part(self, template=""):
        self._log("new_part", template)
        self._stash()
        self._fresh_configurations()
        self.equations_text, self.made, self.current = [], [], ""
        self.plane_defs, self.axis_defs = {}, {}
        self.kind, self.mates = 1, []
        return DocInfo(title="Part1", path="", doc_type=1)

    def new_assembly(self, template=""):
        self._log("new_assembly", template)
        self._stash()
        self._fresh_configurations()
        self.equations_text, self.made, self.current = [], [], ""
        self.kind, self.adding, self.mates = 2, [], []
        self.adding_names = []
        return DocInfo(title="Assem1", path="", doc_type=2)

    def document_path(self):
        return ""

    def set_rebuild_suppressed(self, suppressed):
        self._log("suppress", suppressed)
        self.suppressed = suppressed

    def rebuild(self, kind=None):
        self._log("rebuild", self.suppressed)
        self.rebuild_kinds.append(kind)
        rebuilt = self._rebuilt(kind)
        if self.slips and self._is_assembly() and self.mates:
            for name in sorted(self.slips):
                self.turn(name, 5.0)
        return rebuilt

    def _is_assembly(self):
        return self.current.lower().endswith(".sldasm") if self.current else self.kind == 2

    def _rebuilt(self, kind=None):
        """What a rebuild of the current document does to the marks, and what it returns (see the class)."""
        from gear_generator import swcom
        member, args = swcom.rebuild_call(swcom.DOC_ASSEMBLY if self._is_assembly() else swcom.DOC_PART, kind)
        self.rebuild_members.append((member, args))
        self.unsettled = 0                 # the W8 spike: after a rebuild every flag call behaved
        if self._is_assembly():
            self.assembly_kinds.append(kind)
        self._touch()
        if not self._is_assembly():
            self._ring_landing()
            # W9a, P0 (2026 and 2024): a part's rebuild with a feature in error returns False.
            return self.rebuild_ok and not any(code for (key, _), code in self.feature_codes.items()
                                               if self.current and key == _key(self.current))
        components = self.assembly_components.get(_key(self.current), []) if self.current else self.adding
        if (member, args) == ("ForceRebuild3", (False,)):
            self.touched.update(_key(p) for p in components)
        if self.mates:
            self._solve()
        if any(_key(p) in self.failed_documents for p in components):
            return False
        if self._feature_rule() is False and any(self._part_in_error(p) for p in self._parts_in(components)):
            # W9a, M3 (2026, the demonstration's m3 and k3): an assembly's rebuild with a feature in error in a part
            # of it returns False, where findings.ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_<year> says so.
            return False
        return self.rebuild_ok

    def _evaluated(self):
        """Each global's value, as the worker's foresight reads them: a dimension's equation passed by, and one that
        will not evaluate left out with nothing else lost (the fixes' review, S1)."""
        from gear_generator.gears.equations import evaluate
        scope = {}
        for text in self.equations_text:
            try:
                name, expression = split_equation(text)
                if "@" not in name:
                    value = evaluate(expression, scope, self.trig)
                    if not isinstance(value, complex) and math.isfinite(float(value)):
                        scope[name] = float(value)
            except Exception:  # noqa: BLE001 - see the docstring
                continue
        return scope

    def _ring_landing(self):
        """At a part's rebuild: a ring set across the landing goes to the far branch, and stays there."""
        key = _key(self.current) if self.current else ""
        before = self.values_before_set.pop(key, None)
        if key and key not in self.wrong_branch and before:
            after = self._evaluated()
            if _ring_lands(before, after):
                self.wrong_branch.add(key)
        if key in self.wrong_branch:
            self.feature_codes[(key, "Tooth Space")] = 72
            self.feature_codes[(key, "Teeth")] = 1

    def _feature_rule(self):
        """findings.ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_<year> for the fake's revision."""
        year = swcom.release_year(self.revision[0])
        return getattr(findings, f"ASSEMBLY_REBUILD_WITH_PART_FEATURE_IN_ERROR_ON_{year}", None)

    def _part_in_error(self, path):
        return bool(path) and any(code for (key, _), code in self.feature_codes.items() if key == _key(path))

    def _parts_in(self, components):
        """Every part of the open assembly: its saved components and the user's put in it."""
        names = self._assembly_names(self.current) if self.current else list(self.adding_names)
        return list(components) + [self.component_paths.get(n, "") for n in names]

    def save_as(self, path):
        self._log("save_as", path)
        if getattr(self, "saved_after", False):
            raise AssertionError(f"the app saved {path} after the new assembly's first save (W9D §3: never)")
        if _key(path) in getattr(self, "protected", ()):
            raise AssertionError(f"the app saved {path}, the old assembly or a file of the user's (W9D §3)")
        if getattr(self, "no_save_after", "") and _key(path) == self.no_save_after:
            self.saved_after = True
        self.saved[_key(path)] = (list(self.equations_text), list(self.made))
        self.memory[_key(path)] = (self.equations_text, self.made)
        self.saved_mates[_key(path)] = copy.deepcopy(self.mates)
        self.memory_mates[_key(path)] = self.mates
        self.saved_axes[_key(path)] = dict(self.axis_defs)
        self.memory_axes[_key(path)] = self.axis_defs
        if path.lower().endswith(".sldasm"):
            self.saved_frames = dict(self.frames)        # where the components are in the file
            self.saved_configs[_key(path)] = (list(self.configs), self.config, copy.deepcopy(self.frames_by))
            if not self.current:
                self.assembly_components[_key(path)] = list(self.adding)
                self.assembly_names[_key(path)] = list(self.adding_names)
        self.current = path
        self.touched.discard(_key(path))
        if not any(_key(d.path) == _key(path) for d in self.open_docs):
            # A document a build saves stays open in SolidWorks (nothing is closed), as on 2026 and 2024.
            self.open_docs.append(DocInfo(title=path.replace("/", "\\").rsplit("\\", 1)[-1], path=path,
                                          doc_type=2 if path.lower().endswith(".sldasm") else 1))
        return path

    def close_all(self):
        """SolidWorks closed without saving (or every document closed): nothing is open, and what a document held
        in memory since its last save is gone — reopened, it holds its file again."""
        self.open_docs = []
        self.memory = {}
        self.memory_mates = {}
        self.memory_axes = {}
        self.touched.clear()
        self.frames = dict(getattr(self, "saved_frames", self.frames))

    def detect_trig_units(self):
        self._log("detect_trig_units")
        self._touch()                  # it adds an equation and deletes it: SolidWorks marks the document modified
        return self.trig

    def add_global_variable(self, name, expression):
        self._log("add_global_variable", name, expression)
        self.equations_text.append(f'"{name}"= {expression}')
        return len(self.equations_text) - 1

    def set_global_variable(self, name, expression):
        self._log("set_global_variable", name, expression)
        self._touch()
        if self.current and _key(self.current) not in self.values_before_set:
            self.values_before_set[_key(self.current)] = self._evaluated()
        for feature, code in self.breaks_on_set.pop(_key(self.current), []) if self.current else []:
            self.feature_codes[(_key(self.current), feature)] = code
        for i, text in enumerate(self.equations_text):
            if split_equation(text)[0] == name:
                self.equations_text[i] = f'"{name}"= {expression}'

    def link_dimension(self, dimension, expression):
        self._log("link_dimension", dimension, expression)
        owner = dimension.partition("@")[2]
        for mate in self.mates:
            if mate.name == owner:
                mate.link = expression.replace('"', "").strip()
        return 0

    def equations(self):
        return [(text, 0.0) for text in self.equations_text]

    def equation_values(self):
        from gear_generator.gears.equations import evaluate_all
        values = evaluate_all([split_equation(t) for t in self.equations_text], self.trig)
        values.update(self.values_override)
        return values

    def insert_axis(self, handle, name, planes):
        self._log("insert_axis", handle, name, tuple(planes))
        kept = self.rename.get(name, name)
        self.made.append(kept)
        bases = [p if isinstance(p, int) else self.plane_defs.get(p) for p in planes]
        if all(b in (1, 2, 3) for b in bases):
            self.axis_defs[kept] = ("planes", tuple(3 - b for b in bases))      # plane1 holds z, 2 y, 3 x
        return kept

    def line_axis(self, handle, name, point, direction, length):
        """As swcom.Session.line_axis: a one-line 3D sketch and the axis on it, fixed (no global drives it)."""
        self._log("line_axis", handle, name, tuple(point), tuple(direction), length)
        sketch = name[:-len(" Axis")] + " Line" if name.endswith(" Axis") else name + " Line"
        self.made.append(sketch)
        kept = self.rename.get(name, name)
        self.made.append(kept)
        size = math.sqrt(sum(float(v) ** 2 for v in direction))
        self.axis_defs[kept] = ("line", tuple(float(v) for v in point), tuple(float(v) / size for v in direction))
        return kept

    def _line_of(self, defs, name, values):
        """A layout axis as (point, unit direction) from its definition and the layout's globals; None if unknown."""
        if name in self.moved_lines:
            return self.moved_lines[name]
        held = defs.get(name)
        if held is None:
            return None
        if held[0] == "line":
            return held[1], held[2]
        shaft = name[:-len(" Axis")] if name.endswith(" Axis") else name
        point = [0.0, 0.0, 0.0]
        for index in held[1]:
            point[index] = float(values.get(f"{shaft} {'XYZ'[index]}", 0.0))
        free = ({0, 1, 2} - set(held[1])).pop()
        return tuple(point), tuple(1.0 if i == free else 0.0 for i in range(3))

    def axis_line(self, handle, name):
        """As swcom.Session.axis_line: the axis ``name`` of the document open now, read back (moved_lines first)."""
        self._log("axis_line", handle, name)
        line = self._line_of(self.axis_defs, name, self._values_of(self.current) if self.current else {})
        if line is None:
            raise SolidWorksError(f"No feature called {name!r} is in {self.active.title if self.active else 'it'}.")
        return line

    def open_sketch(self, handle, plane):
        self._log("open_sketch", handle, plane)

    def _made(self, name):
        kept = self.rename.get(name, name)
        self.made.append(kept)
        return kept

    def close_sketch(self, handle, name):
        self._log("close_sketch", handle, name)
        return self._made(name)

    def sketch_status(self, name):
        return self.statuses.get(name, 3)

    def sketch_circle(self, handle, centre, radius, construction=False):
        self._log("sketch_circle", handle)

    def sketch_arc(self, handle, centre, start, end, direction=1, construction=False):
        self._log("sketch_arc", handle)

    def sketch_line(self, handle, start, end, construction=False):
        self._log("sketch_line", handle)

    def sketch_point(self, handle, at):
        self._log("sketch_point", handle)

    def sketch_equation_curve(self, handle, x, y, t1, t2, start, end):
        self._log("sketch_equation_curve", handle)

    def add_relation(self, kind, refs):
        self._log("add_relation", kind, *refs)
        return "already one point" if refs == ("L+.start", "I+.start") else ""

    def dimension(self, name, refs, at):
        self._log("dimension", name)
        if self.dim_dialog_on:
            # The W9c demonstration's second run on 2026 (2966516): AddDimension2 with swInputDimValOnCreate on, as
            # the user's SolidWorks had it, raised SolidWorks' modal 'Modify' box, a §0.3 STOP.
            raise AssertionError(f"SolidWorks' Modify box came up while AddDimension2 dimensioned {name}: "
                                 "swInputDimValOnCreate is on outside begin_build/end_build")
        return self.rename.get(name, name)

    def extrude(self, handle, sketch, name, depth, depth_dim):
        self._log("extrude", name)
        return self._made(name), depth_dim

    def cut_extrude(self, handle, sketch, name):
        self._log("cut_extrude", name)
        return self._made(name)

    def circular_pattern(self, handle, name, axis, feature, count, count_dim):
        self._log("circular_pattern", name, count)
        return self._made(name), count_dim

    def ref_plane(self, handle, name, plane, offset, flip, offset_dim):
        self._log("ref_plane", name, round(offset, 6), flip)
        kept = self.rename.get(name, name)
        self.made.append(kept)
        base = plane if isinstance(plane, int) else self.plane_defs.get(plane)
        self.plane_defs[handle] = self.plane_defs[kept] = base
        return kept, offset_dim

    def sweep_cut(self, handle, profile, path, name, twist, reverse, twist_dim):
        self._log("sweep_cut", name, round(twist, 6), reverse)
        return self._made(name), twist_dim

    def mirror_body(self, handle, name, plane):
        self._log("mirror_body", name, plane)
        return self._made(name)

    def ref_plane_normal(self, handle, name, line, point):
        self._log("ref_plane_normal", name, line, point)
        return self._made(name)

    def revolve(self, handle, sketch, name, axis):
        self._log("revolve", name, axis)
        return self._made(name)

    def loft_cut(self, handle, name, profiles):
        self._log("loft_cut", name, *profiles)
        return self._made(name)

    def add_component(self, handle, path, at):
        self._log("add_component", handle, path)
        self.adding.append(path)
        self.adding_names.append(f"{handle}-1")
        if self.current and _key(self.current) in self.assembly_names:      # W9c: inserted into a saved assembly
            self.assembly_names[_key(self.current)].append(f"{handle}-1")
            self.assembly_components.setdefault(_key(self.current), []).append(path)
        self.component_names[handle] = f"{handle}-1"
        self.component_paths[f"{handle}-1"] = path
        return f"{handle}-1"

    def fix_component(self, handle):
        self._log("fix_component", handle)
        self._not_users(self._name2(handle), "fixed")
        self.fixed.add(self._name2(handle))

    def unfix_component(self, handle):
        self._log("unfix_component", handle)
        self._not_users(self._name2(handle), "unfixed")
        self.fixed.discard(self._name2(handle))

    def add_mate(self, handle, kind, a, b, value=0.0, name="", ratio=(1.0, 1.0), flip=False):
        self._log("add_mate", kind, a, b, *((ratio, flip) if kind == "gear" else ()))
        kept = name or f"Mate{len(self.calls)}"
        self._keep_mate(handle, kept, kind, a, b, value, ratio, flip)
        return kept, ("D7" if kind in ("distance", "angle", "axis angle", "point distance") else "")

    def place_component(self, handle, rotation, at, kind=None):
        self._log("place_component", handle)
        if getattr(findings, "PUT_MARKS_ASSEMBLY_MODIFIED", False):
            self._touch()
        put = asked = (tuple(rotation), tuple(at))
        name = self._name2(handle)
        if self._is_users(name):
            if not self._locked_to_a_put(name):
                raise AssertionError(f"the app put {name}, a component of the user's, not with a gear it put in the "
                                     "same step through the user's locks (W9a §0.3: route (c1) only)")
            self.user_puts.append((name, asked, self.config))
        else:
            self.step_puts.add(name)
        if self.codes_after_put:
            self.mate_codes.update(self.codes_after_put)
            self.codes_after_put = {}
        bodies, geared = self._planetary()
        if name in bodies and geared:
            # Probe planetary_put_back (SolidWorks 2026): a put of a member of a train with a carrier, while that
            # train's gear mates are on, does not hold: the solver pulls it back (the carrier read 6.2° short).
            put = (_mul(put[0], _rot_z(-6.2)), put[1])
        if any(m.kind == "lock" and not m.suppressed and name in (m.a[0], m.b[0]) for m in self.mates):
            self.locked_puts.append(name)          # held, its partner left where it was, nothing reported
        if self.put_splits is not None:
            self.put_splits.add(self.config)       # from now on this configuration keeps its own places
        self.frames[handle] = put
        self.frames[name] = put
        if handle in self.found:
            self.frames[self.found[handle]] = put
        for frames in self.frames_by.values():         # W9d: a component new to the assembly stands in every
            frames.setdefault(name, put)               # configuration where it was put, until put there itself
        self._rebuilt(kind)            # Session.place_component's rebuild of its own, after the put
        if self.mates:
            # Session.place_component reads the frame back after that rebuild.
            rotation_off, origin_off = _frame_off(self.frames[name], asked)
            if rotation_off > 1e-6 or origin_off > 1e-6:
                raise SolidWorksError(f"{name} did not take its frame (rotation off {rotation_off:.1e}, origin "
                                      f"{origin_off:.1e} mm).")

    def _planetary(self):
        """(every body of a train with a carrier — the carriers, their riders and all gear- or lock-mated to them,
        whatever is suppressed — and whether any gear mate among them is on)."""
        carriers = {self._carrier_target(m) for m in self.mates if m.axis and self._carrier_target(m)}
        if not carriers:
            return set(), False
        bodies = set(carriers) | {m.a[0] for m in self.mates if m.axis and self._carrier_target(m)}
        grown = True
        while grown:
            grown = False
            for m in self.mates:
                if m.kind in ("gear", "lock") and (m.a[0] in bodies) != (m.b[0] in bodies):
                    bodies |= {m.a[0], m.b[0]}
                    grown = True
        geared = any(m.kind == "gear" and not m.suppressed and m.a[0] in bodies for m in self.mates)
        return bodies, geared

    def interference_count(self):
        self._log("interference_count")
        self._touch()                  # interference detection marks the assembly (see interferences)
        return self.interference

    def set_custom_property(self, name, value):
        self._log("set_custom_property", name, value)

    # -- W4

    def documents(self):
        return list(self.open_docs)

    def feature_names(self):
        return list(self.made)

    def open_document(self, path):
        self._log("open_document", path)
        self._stash()
        self.step_puts = set()
        doc_type = 2 if path.lower().endswith(".sldasm") else 1
        info = DocInfo(title=path.replace("/", "\\").rsplit("\\", 1)[-1], path=path, doc_type=doc_type)
        is_open = any(_key(d.path) == _key(path) for d in self.open_docs)
        if not (is_open and _key(path) in self.memory):
            # Loaded from its file: what it holds in memory is what was saved.
            eq, made = self.saved.get(_key(path), ([], []))
            self.memory[_key(path)] = (list(eq), list(made))
        self.equations_text, self.made = self.memory[_key(path)]
        if not (is_open and _key(path) in self.memory_mates):
            self.memory_mates[_key(path)] = copy.deepcopy(self.saved_mates.get(_key(path), []))
        self.mates = self.memory_mates[_key(path)]
        if not (is_open and _key(path) in self.memory_axes):
            self.memory_axes[_key(path)] = dict(self.saved_axes.get(_key(path), {}))
        self.axis_defs = self.memory_axes[_key(path)]
        self.current = path
        if not is_open:
            self.open_docs.append(info)
            configs, config, frames_by = self.saved_configs.get(_key(path), (["Default"], "Default", {}))
            self.configs, self.config, self.frames_by = list(configs), config, copy.deepcopy(frames_by)
        elif _key(path) in self.memory_configs:
            self.configs, self.config, self.template_config, self.frames_by = self.memory_configs[_key(path)]
        self.epoch += 1                    # as the Session's: an open may change the active configuration
        self.active = info
        return info

    def use_open_document(self, path):
        """``Session.use_open_document``: a document already open made the one read, nothing loaded, nothing
        activated (``active`` unchanged); None when it is not open."""
        self._log("use_open_document", path)
        info = next((d for d in self.open_docs if _key(d.path) == _key(path)), None)
        if info is None or _key(path) not in self.memory:
            return None
        if _key(path) in self.memory_configs and _key(path) != _key(self.current or ""):
            # W9d: the document's own configurations, as SolidWorks keeps them per document (W9c's memory_configs).
            self._stash()
            self.configs, self.config, self.template_config, self.frames_by = self.memory_configs[_key(path)]
        self.equations_text, self.made = self.memory[_key(path)]
        self.mates = self.memory_mates.setdefault(_key(path), copy.deepcopy(self.saved_mates.get(_key(path), [])))
        self.axis_defs = self.memory_axes.setdefault(_key(path), dict(self.saved_axes.get(_key(path), {})))
        self.current = path
        self.epoch += 1
        return info

    def has_unsaved_changes(self):
        """``GetSaveFlag`` on the document just opened: True when what it holds in memory is not what was saved,
        or a call has modified it since (``touched``)."""
        self._log("has_unsaved_changes")
        key = _key(self.current)
        return key in self.touched or self.memory.get(key) != self.saved.get(key)

    def find_component(self, handle, name, lightweight_ok=False, suppressed_ok=False):
        self._log("find_component", handle, name)
        title = self.active.title if self.active else "the assembly"
        if name in self.missing_components:
            raise ComponentGone(f"{name} is not in {title} any more: it was renamed or deleted in SolidWorks.")
        if not suppressed_ok and self._state_in(name, self.config) == 0:   # as swcom.Session.find_component
            raise SolidWorksError(f"{name} is suppressed in {title}, so it cannot be placed; unsuppress it in "
                                  "SolidWorks and try again.")
        if name in self.lightweight and not lightweight_ok:          # as swcom.Session.find_component refuses it
            raise SolidWorksError(f"{name} is loaded lightweight in {title}, and resolving a component is not "
                                  "settled here; set it to Resolved in SolidWorks and try again.")
        self.found[handle] = name
        self.component_names[handle] = name
        return name

    def is_fixed(self, handle):
        """``Session.is_fixed``: the component's fixed state as fix and unfix left it (the layout and a held member
        fixed, every other gear not). The W8 spike kept a fixed component fixed in every configuration made after it
        was fixed (``FIXED_KEPT_IN_NEW_CONFIGURATION``), so one set serves every configuration."""
        self._log("is_fixed", handle)
        return self._name2(handle) in self.fixed

    def component_path(self, handle):
        """``Session.component_path``: the file the component was inserted from; in an assembly opened from a
        copied folder whose stored folder is gone, the same file beside the assembly, as SolidWorks resolves it."""
        self._log("component_path", handle)
        name = self._name2(handle)
        stored = self.component_paths.get(name)
        if stored is None:
            raise SolidWorksError(f"SolidWorks gave no file for {name}, so where it comes from cannot be read.")
        if _key(stored) in self.saved or not self.current:
            return stored
        folder = self.current.replace("/", "\\").rsplit("\\", 1)[0]
        beside = folder + "\\" + stored.replace("/", "\\").rsplit("\\", 1)[-1]
        return beside if _key(beside) in self.saved else stored

    def copied(self, folder, to):
        """A built folder copied to ``to`` and the master folder gone (the demonstration's copy_built): every saved
        file under ``folder`` is now under ``to``, its stored references (``component_paths``) unchanged."""
        for kept in (self.saved, self.saved_mates, self.saved_axes, self.assembly_components):
            for key in [k for k in kept if k.startswith(_key(folder))]:
                kept[_key(to) + key[len(_key(folder)):]] = kept.pop(key)

    def component_frame(self, handle):
        self._log("component_frame", handle)
        identity = ((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0))
        name = self.found.get(handle) or self.component_names.get(handle)
        drift = getattr(self, "drift_in", {}).get(self.config, {}).get(name)
        if drift is not None and name in self.frames:   # W9d: SolidWorks moved it in this configuration (made up)
            rotation, at = self.frames[name]
            return rotation, tuple(a + d for a, d in zip(at, drift))
        if name in self.frames:                    # a component's frame by its Name2 first: the solve moves those
            return self.frames[name]
        return self.frames.get(handle, identity)

    def interferences(self):
        """Marks the assembly modified. Probe assembly_rebuild_scope saw the assembly marked after a put by the reads
        that followed it (``flags_after_reads``: the frame reads and interferences() together), without isolating
        which; the fake pins it here, on the interference check. W8: ``clashes_in`` per configuration."""
        self._log("interferences")
        self._touch()
        return list(self.clashes_in.get(self.config, self.clashes))

    def exists(self, path):
        return _key(path) in self.saved

    # -- W5: the train's mates (see the class)

    def _name2(self, handle):
        if handle in self.component_paths:         # already a Name2
            return handle
        return self.found.get(handle) or self.component_names.get(handle) or f"{handle}-1"

    def _ref(self, ref, bare):
        if bare:
            return self._name2(ref), ""
        handle, _, target = ref.partition(":")
        return ("asm" if handle == "asm" else self._name2(handle)), target

    def _keep_mate(self, handle, kept, kind, a, b, value, ratio, flip):
        mate = FakeMate(kept, kind, self._ref(a, kind == "lock"), self._ref(b, kind == "lock"), value,
                        tuple(ratio), flip)
        if len(self.configs) > 1 and self.config != self.template_config:
            # The W8 spike: a mate made while another configuration is shown comes out suppressed in the template's
            # and on in every other (``new_mate_elsewhere="on"`` for the other plausible default).
            off = self.new_mate_elsewhere != "on"
            mate.flags = {c: off and c == self.template_config for c in self.configs}
        else:
            mate.flags = {c: False for c in self.configs}
        mate.suppressed = mate.flags[self.config]
        if kind == "gear" and self.judge_rank and not {mate.a[0], mate.b[0]} <= self.fixed and \
                self._over_defines(mate):
            # W7-PLAN §2.9 (review S12): a gear mate whose turn row adds nothing to those of the free bodies already
            # mated over-defines the assembly (a loop's last mesh, say), as AddMate5 answers for one.
            mate.status = findings.ADD_MATE_OVER_DEFINED
        self.mates.append(mate)
        self.mate_handles[handle] = kept
        # compound_lock, "lock, both on the shaft" (latest.json): status 1 throughout, the lock unflagged, the along
        # mates of both gears at code 46 as warnings.
        live = [m for m in self.mates if not m.suppressed]
        for lock in (m for m in live if m.kind == "lock"):
            anchor, follower = lock.a[0], lock.b[0]
            if any((m.axis or m.along) and m.a[0] == follower for m in live):
                for along in (m for m in live if m.along and m.a[0] in (anchor, follower)):
                    along.code, along.warning = 46, True

    def mate(self, name, path=None):
        """A test's look at one mate: in the document at ``path`` (as open now), else in the current one."""
        mates = self.memory_mates.get(_key(path), []) if path else self.mates
        return next((m for m in mates if m.name == name), None)

    def user_mate(self, path, name, suppressed=False, kind="angle", a=None, b=("layout-1", "plane3")):
        """A mate the user added by hand in SolidWorks (an angle mate driving a gear, say), in the open document:
        ``a`` and ``b`` as a FakeMate's, ``a`` by default a gear's plane — ``gear1-1``'s where the assembly has it,
        else its first component that is not the layout. Returns the mate."""
        if a is None:
            names = self._assembly_names(path)
            first = "gear1-1" if "gear1-1" in names or not names else \
                next((n for n in names if not n.startswith("layout")), "gear1-1")
            a = (first, "plane2")
        mate = FakeMate(name, kind, tuple(a), tuple(b), suppressed=suppressed, user=True)
        mate.flags = {c: bool(suppressed) for c in self.configs}
        self.memory_mates[_key(path)].append(mate)
        return mate

    def user_lock(self, path, name, a, b, flags=None):
        """A lock the user made between two components (Name2s; ``a`` first), on in every configuration unless
        ``flags`` (configuration -> suppressed) says otherwise. Returns the mate."""
        mate = FakeMate(name, "lock", (a, ""), (b, ""), user=True)
        mate.flags = dict(flags) if flags else {c: False for c in self.configs}
        mate.suppressed = mate.flags.get(self.config, False)
        self.memory_mates[_key(path)].append(mate)
        return mate

    def user_component(self, path, name, part, frame=None, fixed=False):
        """A component the user inserted into the assembly at ``path`` (in memory, as an open document holds it):
        its Name2, the part it stands for, its frame (identity at the origin by default; in every configuration),
        fixed or floating."""
        self.user_parts.setdefault(_key(path), []).append(name)
        self.component_paths[name] = part
        self.frames[name] = frame or (IDENTITY9, (0.0, 0.0, 0.0))
        for frames in self.frames_by.values():
            frames[name] = self.frames[name]
        if fixed:
            self.fixed.add(name)

    def rename_component(self, path, old, new):
        """A component renamed in SolidWorks (its Name2 ``old`` now ``new``), in the assembly at ``path``: found by
        the new name only, its mates and frames following it."""
        names = self.assembly_names.get(_key(path), [])
        names[names.index(old)] = new
        self.component_paths[new] = self.component_paths[old]
        for frames in [self.frames] + list(self.frames_by.values()):
            if old in frames:
                frames[new] = frames[old]
        if old in self.fixed:
            self.fixed.add(new)
        for mate in self.memory_mates.get(_key(path), []):
            mate.a = (new, mate.a[1]) if mate.a[0] == old else mate.a
            mate.b = (new, mate.b[1]) if mate.b[0] == old else mate.b
        self.missing_components.add(old)

    def user_feature(self, path, name, code=0, type_name="ICE"):
        """A feature the user added to the document at ``path``, after the app's; ``code`` its error code."""
        self.user_features.setdefault(_key(path), []).append((name, type_name))
        if code:
            self.feature_codes[(_key(path), name)] = code

    def _assembly_names(self, path):
        key = _key(path)
        return list(self.assembly_names.get(key, [])) + list(self.user_parts.get(key, []))

    def _is_users(self, name):
        return any(name in names for names in self.user_parts.values())

    def _locked_to_a_put(self, name):
        """Whether the user's component ``name`` is held, through locks on in the configuration shown (a leaf of a
        sub-assembly counting as its top level), to an app body put in this step."""
        top = lambda n: n.split("/")[0]                                   # noqa: E731
        reached, grown = {name}, True
        while grown:
            grown = False
            for m in self.mates:
                if m.kind != "lock" or m.suppressed:
                    continue
                ends = {top(m.a[0]), top(m.b[0])}
                if ends & reached and not ends <= reached:
                    reached |= ends
                    grown = True
        return bool(reached & self.step_puts)

    def _not_users(self, name, what):
        if self._is_users(name):
            raise AssertionError(f"the app {what} {name}, a component of the user's (W9a §0.3)")

    def _not_users_mate(self, name, what):
        mate = self.mate(name)
        if mate is not None and mate.user:
            raise AssertionError(f"the app {what} {name}, a mate of the user's (W9a §0.3)")

    def components(self):
        """``Session.components``: the open assembly's top-level components, the app's in insertion order then the
        user's, each with its file, fixed state, ``GetSuppression2`` and error code."""
        self._log("components")
        names = self._assembly_names(self.current) if self.current else list(self.adding_names)
        # W9a, M3: a component whose part has a feature in error reads in error (code 1, as m3's Sprocket-1 read on
        # 2026), where the finding says such a part fails the assembly's rebuild; ``component_codes`` overrides.
        derived = self._feature_rule() is False
        by = getattr(self, "states_by", {}).get(self.config, {})          # W9d: a state set per configuration
        return [swcom.ComponentInfo(n, self.component_paths.get(n, ""), n in self.fixed,
                                    by.get(n, self.component_states.get(n, 1 if n in self.lightweight else 2)),
                                    self.component_codes.get(n, 1 if derived and self._part_in_error(
                                        self.component_paths.get(n, "")) else 0)) for n in names]

    MATE_TYPES = {"coincident": 0, "point": 0, "distance": 5, "point distance": 5, "angle": 6, "axis angle": 6,
                  "gear": 10, "lock": 16, "rack and pinion": 13, "screw": 17}

    def mate_info(self, handle):
        """``Session.mate_info``: the mate's swMateType_e and the Name2 its entities are on ("" for the assembly's)."""
        self._log("mate_info", handle)
        mate = self.mate(self.mate_handles[handle])
        unread = self.unread_mates.get(mate.name)
        if unread == "count":
            return swcom.MateInfo(mate.name, self.MATE_TYPES.get(mate.kind, 7), (), counted=False)
        own = self._root_name() if self.assembly_entity == "root" else ""
        ends = tuple(own if end[0] == "asm" else end[0] for end in (mate.a, mate.b))
        if unread == "entity":
            ends = (ends[0], None)
        kind = swcom.UNREAD if unread == "type" else self.MATE_TYPES.get(mate.kind, 7)
        kinds = tuple(self._entity_kind(mate, end) for end in (mate.a, mate.b))
        return swcom.MateInfo(mate.name, kind, ends, entities=kinds if self.read_entity_kinds else ())

    def _entity_kind(self, mate, end):
        """W9d: an entity's (kind, feature) as ``Session.mate_info`` reads it from ReferenceType2: a lock's end whole,
        ``planeN`` a base plane by order, ``origin``, ``face:<id>`` / ``edge:<id>`` / ``vertex:<id>``, else a reference
        feature by name."""
        target = end[1]
        if mate.kind == "lock" or not target:
            return ("whole", "")
        if target.startswith("plane") and target[5:].isdigit():
            return ("plane", target)
        if target == "origin":
            return ("origin", "origin")
        kind, _, _ = target.partition(":")
        if kind in ("face", "edge", "vertex"):
            return (kind, "")
        return ("feature", target)

    def _root_name(self):
        """The root component's Name2 as SolidWorks gives it: the open assembly's title, without its extension."""
        path = self.current or ""
        return path.replace("/", "\\").rsplit("\\", 1)[-1].rsplit(".", 1)[0]

    def root_component(self, resolve=True):
        """``Session.root_component``: the active configuration's root component's Name2, or None unread. As strict
        as measured (the W9c review's should-fix 8): with ``resolve`` on an assembly holding a lightweight component
        it resolves them and marks the assembly (what s5 (e)'s marking most likely was; only an all-resolved assembly
        was measured marking nothing); ``resolve=False`` (never measured) answers the name and marks nothing."""
        self._log("root_component", resolve)
        if resolve:
            names = self._assembly_names(self.current) if self.current else list(self.adding_names)
            heavy = [n for n in names if n in self.lightweight or self.component_states.get(n) in (1, 4)]
            if heavy:
                for name in heavy:
                    self.lightweight.discard(name)
                    self.component_states[name] = 2
                self._touch()
        return None if self.root_unread else self._root_name()

    def delete_component(self, handle):
        """``Session.delete_component`` (W9c, P1 on 2026 and 2024): the component out of the open assembly in every
        configuration, every mate touching it with it, other handles kept; refused, as the Session refuses, where
        ``findings.COMPONENT_DELETE_ROUTE_ON_<year>`` is not the route. A component of the user's, or one a user mate
        touches, fails the test (W9a §0.3: that would write the user's work)."""
        self._log("delete_component", handle)
        year = swcom.release_year(self.revision[0])
        if getattr(findings, f"COMPONENT_DELETE_ROUTE_ON_{year}", None) != "select4-editdelete":
            raise SolidWorksError("Deleting a component has not been settled on this SolidWorks.")
        name = self._name2(handle)
        self._not_users(name, "deleted")
        top = lambda n: n.split("/")[0]                                   # noqa: E731
        theirs = [m.name for m in self.mates if m.user and name in (top(m.a[0]), top(m.b[0]))]
        if theirs:
            raise AssertionError(f"the app deleted {name} and with it {theirs}, mates of the user's (W9a §0.3)")
        self.assembly_names[_key(self.current)].remove(name)
        self.mates[:] = [m for m in self.mates if name not in (m.a[0], m.b[0])]
        for frames in [self.frames] + list(self.frames_by.values()):
            frames.pop(name, None)
        self.fixed.discard(name)
        self.deleted.append(name)
        # As the Session: the epoch raised (P1: other handles held only within one epoch), and a handle to the
        # component deleted answers no more (found again by name, nothing answers).
        self.epoch += 1
        for kept in (self.found, self.component_names):
            for h in [h for h, n in kept.items() if n == name]:
                del kept[h]
        self.missing_components.add(name)
        self._touch()

    def suppress_feature(self, name, suppressed):
        """``Session.suppress_feature`` (W9c): a feature of the open part suppressed or turned back on, read back. A
        feature of the user's fails the test."""
        self._log("suppress_feature", name, suppressed)
        key = _key(self.current)
        if any(n == name for n, _ in self.user_features.get(key, [])):
            raise AssertionError(f"the app suppressed {name}, a feature of the user's (W9a §0.3)")
        if name not in self.made:
            raise SolidWorksError(f"{self.current} has no feature {name} to suppress.")
        self.suppressed_features[(key, name)] = bool(suppressed)
        self._touch()

    def feature_states(self):
        """``Session.feature_states``: the template's planes and origin, then every feature the app made in the
        document, then the user's, each with its error code."""
        self._log("feature_states")
        key = _key(self.current) if self.current else ""
        names = [("Front Plane", "RefPlane"), ("Top Plane", "RefPlane"), ("Right Plane", "RefPlane"),
                 ("Origin", "OriginProfileFeature")] + [(n, "?") for n in self.made] + self.user_features.get(key, [])
        return [swcom.FeatureState(n, t, self.feature_codes.get((key, n), 0), False if self.feature_codes.get(
            (key, n), 0) else True) for n, t in names]

    def user_folder(self, path, name):
        """A folder the user made among the mates in SolidWorks, in the open document, as probe round P0c saw one in
        the MateGroup walk: two entries of type "FtrFolder" (the folder and its "…___EndTag___" marker), the mates
        it holds left in place as ordinary siblings (the fake does not model where in the walk they sit)."""
        self.mate_folders.setdefault(_key(path), []).extend([(name, "FtrFolder"), (f"{name}___EndTag___", "FtrFolder")])

    def user_entry(self, path, name, type_name):
        """Anything else in the mate group that is not a mate, of a type no probe has met."""
        self.mate_folders.setdefault(_key(path), []).append((name, type_name))

    def drop_mate(self, path, name):
        """A mate deleted (or renamed) by the user in SolidWorks, in the open document."""
        mates = self.memory_mates[_key(path)]
        mates.remove(next(m for m in mates if m.name == name))

    def turn(self, name, degrees):
        """A component turned about its own axis (``R · rot_z``), as a drag in SolidWorks would leave it."""
        rotation, at = self.frames[name]
        self._moved_by_hand({name: (_mul(rotation, _rot_z(degrees)), at)})

    def _moved_by_hand(self, new):
        """Bodies moved by a turn (not a put) in the active configuration; with ``put_splits`` set and the active
        configuration not yet put in, the same motion of each body is given to it in every other configuration not
        yet put in (each keeps its own slide place: the motion is the body's, about its own axis or its carrier's)."""
        if self.put_splits is not None and self.config not in self.put_splits:
            for config, frames in self.frames_by.items():
                if config == self.config or config in self.put_splits:
                    continue
                for body, (r1, p1) in new.items():
                    if body not in frames or body not in self.frames:
                        continue
                    r0, p0 = self.frames[body]
                    move = _mul(r1, tuple(r0[j * 3 + i] for i in range(3) for j in range(3)))
                    shift = tuple(a - b for a, b in zip(p1, _apply(move, p0)))
                    q_r, q_p = frames[body]
                    frames[body] = (_mul(move, q_r), tuple(a + b for a, b in zip(_apply(move, q_p), shift)))
        self.frames.update(new)

    def _values_of(self, path):
        from gear_generator.gears.equations import evaluate_all
        if not path:
            return {}
        texts = self.memory[_key(path)][0] if _key(path) in self.memory else self.saved.get(_key(path), ([], []))[0]
        return evaluate_all([split_equation(t) for t in texts], self.trig)

    def _solve(self):
        live = [m for m in self.mates if not m.suppressed]
        own = self.equation_values() if self.equations_text else {}
        # W7: an axis held in a component other than the layout (a carrier's planet axis) is solved after the
        # component holding it, so a carrier goes to its shaft first and then carries its planets.
        axes = [m for m in live if m.axis]
        axes = [m for m in axes if not self._carrier_target(m)] + [m for m in axes if self._carrier_target(m)]
        for axis in axes:
            gear, (layout, target) = axis.a[0], axis.b
            path = self.component_paths.get(layout)
            values = self._values_of(path)
            key = _key(path) if path else ""
            defs = self.memory_axes.get(key, self.saved_axes.get(key, {}))
            line = self._line_of(defs, target, values)
            if line is None:                                   # a layout the fake never saw built: a Z axis by globals
                shaft = target[:-len("Axis")].strip()
                line = ((values.get(f"{shaft} X", 0.0), values.get(f"{shaft} Y", 0.0), 0.0), (0.0, 0.0, 1.0))
            point, direction = line
            if self._carrier_target(axis):                     # in the carrier part's own coordinates: carried
                frame = self.frames.get(layout, (IDENTITY9, (0.0, 0.0, 0.0)))
                moved = _apply(frame[0], point)
                point = tuple(moved[i] + frame[1][i] for i in range(3))
                direction = _apply(frame[0], direction)
            old = self.frames.get(gear, (IDENTITY9, (0.0, 0.0, 0.0)))
            off = tuple(old[1][i] - point[i] for i in range(3))
            t = sum(off[i] * direction[i] for i in range(3))
            for along in (m for m in live if m.along and m.a[0] == gear):
                index = {"plane1": 2, "plane2": 1, "plane3": 0}.get(along.b[1])
                sign = -1.0 if along.value < 0 else 1.0
                if along.link in own:
                    value = sign * own[along.link]
                elif self.config in along.own:         # W8: a slide's value in this configuration
                    value = sign * along.own[self.config]
                else:
                    value = along.value
                if index is not None and abs(direction[index]) > 1e-12:
                    t = (value - point[index]) / direction[index]
            origin = tuple(point[i] + t * direction[i] for i in range(3))
            gap = math.sqrt(max(0.0, sum(v * v for v in off) - (sum(off[i] * direction[i] for i in range(3))) ** 2))
            moved = gap > 1e-9
            new = (_mul(old[0], _rot_z(-13.0)) if moved else old[0], origin)
            if _frame_off(new, old) == (0.0, 0.0):
                continue
            for lock in (m for m in live if m.kind == "lock" and m.a[0] == gear):
                follower = self.frames.get(lock.b[0], (IDENTITY9, (0.0, 0.0, 0.0)))
                self.frames[lock.b[0]] = _compose(new, _compose(_inverse(old), follower))
            self.frames[gear] = new

    def mate_status(self, name):
        if name in self.mate_statuses:
            return self.mate_statuses[name]
        mate = self.mate(name)
        return None if mate is None else mate.status

    def mate_states(self, *, others=None):
        self._log("mate_states")
        if others is not None and self.current:
            # As swcom.Session.mate_states: a folder's entries are skipped by findings.MATE_FOLDER_TYPE_NAME.
            folder = swcom.mate_folder_type()
            others.extend(name for name, type_name in self.mate_folders.get(_key(self.current), [])
                          if not (folder is not None and type_name == folder))
        out = []
        for m in self.mates:
            code, warning = self.mate_codes_in.get(self.config, {}).get(m.name) or \
                self.mate_codes.get(m.name, (m.code, m.warning))
            out.append(swcom.MateState(m.name, code, warning if code else True, m.suppressed))
        return out

    def constrained_status(self, handle):
        self._log("constrained_status", handle)
        name = self._name2(handle)
        if getattr(self, "saved_after", False) and name in getattr(self, "held_after_save", ()):
            return findings.COMPONENT_FULLY_DEFINED      # W9d: held once the new assembly is saved (a held gear)
        for key in (name, handle):
            if key in self.constrained:
                return self.constrained[key]
        if any(m.code and not m.suppressed and name in (m.a[0], m.b[0]) for m in self.mates):
            return findings.COMPONENT_OVER_DEFINED
        if any(not m.suppressed and {name, handle} & set(self.locks.get(m.name, ())) for m in self.mates):
            return findings.COMPONENT_FULLY_DEFINED
        return findings.COMPONENT_FULLY_DEFINED if name in self.fixed else findings.COMPONENT_UNDER_DEFINED

    def find_mate(self, handle, name):
        self._log("find_mate", handle, name)
        if self.mate(name) is None:
            title = self.active.title if self.active else "the assembly"
            raise swcom.MateGone(f'The mate "{name}" is not in {title} any more: it was renamed or deleted in '
                                 "SolidWorks.")
        self.mate_handles[handle] = name
        return name

    def set_mate_suppressed(self, handle, suppressed):
        self._log("set_mate_suppressed", handle, suppressed)
        name = self.mate_handles[handle]
        self._not_users_mate(name, "suppressed or turned on")
        if not suppressed:
            self.step_puts = set()
        if not suppressed and name in self.held_suppressed:
            # As swcom.Session.set_mate_suppressed's read-back: the call returned, the mate still reads suppressed.
            title = self.active.title if self.active else "the assembly"
            raise SolidWorksError(f"SolidWorks would not turn the mate {name} back on in {title}: it still reads it "
                                  "suppressed; if it sits in a suppressed folder, unsuppress the folder in SolidWorks "
                                  "and press Update SolidWorks again.")
        self.mate(name).suppressed = bool(suppressed)
        self.counts_after["set_mate_suppressed"] = self.counts_after.get("set_mate_suppressed", 0) + 1
        planned = self.raises_after.get("set_mate_suppressed")
        if planned is not None and planned[0] == self.counts_after["set_mate_suppressed"]:
            raise planned[1]

    def definition(self, name, path=None):
        """A gear mate's IGearMateFeatureData as SolidWorks reads it: (GearRatioNumerator, GearRatioDenominator), the
        counts the other way round from AddMate5 (findings.GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND)."""
        first, second = self.mate(name, path).ratio
        return float(second), float(first)

    def component_resolved(self, handle):
        """As swcom.Session.component_resolved: False for a component loaded lightweight (``lightweight``)."""
        self._log("component_resolved", handle)
        return self._name2(handle) not in self.lightweight

    def gear_mate_ratio(self, handle):
        """As swcom.Session.gear_mate_ratio: the definition read, and turned back into the mate's own order by the
        finding (refused while it is missing). The ratio is the mate's as this document holds it: saved with it,
        and lost with an unsaved close (a remake included)."""
        self._log("gear_mate_ratio", handle)
        order = getattr(findings, "GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", None)
        if order is None:
            raise SolidWorksError("Reading a gear mate's ratio has not been settled on SolidWorks yet.")
        numerator, denominator = self.definition(self.mate_handles[handle])
        return (denominator, numerator) if order else (numerator, denominator)

    def set_gear_ratio(self, handle, a, b, ratio):
        self._log("set_gear_ratio", handle, a, b, tuple(ratio))
        self._not_users_mate(self.mate_handles[handle], "made again")
        route = getattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
        if route != "remake":
            raise SolidWorksError(f"findings.GEAR_MATE_RATIO_ROUTE is {route!r}, so the gear mate keeps its ratio.")
        old = self.mate(self.mate_handles[handle])
        self.mates.remove(old)                     # deleted, and made again at the end of the tree, its name kept
        # As swcom: made again with findings.GEAR_MATE_FLIP, whatever Flip the old one had.
        self._keep_mate(handle, old.name, "gear", a, b, 0.0, tuple(float(n) for n in ratio),
                        bool(getattr(findings, "GEAR_MATE_FLIP", False)))

    # -- which way a gear mate turns (probe ring_mate_sense): the Flip each case needs, per version

    def remake_gear_mate(self, handle, a, b, ratio, flip, saved=True):
        """As swcom.Session.remake_gear_mate: deleted and made again with ``flip``, at the end of the tree."""
        self._log("remake_gear_mate", handle, a, b, tuple(ratio), flip)
        self._not_users_mate(self.mate_handles[handle], "made again")
        old = self.mate(self.mate_handles[handle])
        self.mates.remove(old)
        self._keep_mate(handle, old.name, "gear", a, b, 0.0, tuple(float(n) for n in ratio), bool(flip))

    def _axis(self, name):
        """A component's own +Z as it stands: its frame's third column."""
        rotation, _ = self.frames.get(name, (IDENTITY9, (0.0, 0.0, 0.0)))
        return (rotation[2], rotation[5], rotation[8])

    def _origin(self, name):
        return self.frames.get(name, (IDENTITY9, (0.0, 0.0, 0.0)))[1]

    def _sigma(self, name):
        """A component's axis sense within its family: the sign of its axis's first component that is not 0 (+1 on
        +Z, as W5's rotation[8] was)."""
        axis = self._axis(name)
        first = next((v for v in axis if abs(v) > 1e-12), 1.0)
        return 1 if first > 0 else -1

    def _turned(self, mate):
        return not swcom.axes_parallel(self._axis(mate.a[0]), self._axis(mate.b[0]))

    def _is_ring(self, name):
        path = self.component_paths.get(name, "")
        stem = path.replace("/", "\\").rsplit("\\", 1)[-1]
        return path in self.ring_parts or stem.lower().startswith("ring")

    def _is_helical(self, name):
        import re
        path = self.component_paths.get(name, "")
        stem = path.replace("/", "\\").rsplit("\\", 1)[-1].rsplit(".", 1)[0]
        return path in self.helical_parts or bool(re.search(r"_\d+(\.\d+)?[LR]$", stem))

    def _collinear(self, mate):
        """W8: a gear mate at 1 : 1 between two gears on one axis line (a spline or a coupling), as they stand; W7's
        abandoned coaxial fallback (a sun mated to its carrier at the absolute ratio) keeps the external rule."""
        a, b = mate.a[0], mate.b[0]
        if self._turned(mate) or abs(mate.ratio[0] - mate.ratio[1]) > 1e-9:
            return False
        axis, off = self._axis(a), [q - p for p, q in zip(self._origin(a), self._origin(b))]
        along = sum(o * w for o, w in zip(off, axis))
        return sum(o * o for o in off) - along * along <= 1e-12

    def mesh_case(self, mate):
        """(internal, the key of the probe's tables for this pair, the Flip it needs on this fake's version)."""
        a, b = mate.a[0], mate.b[0]
        if self._turned(mate):
            return False, "turned", bool(self.turned_flip_needed)
        if self._collinear(mate):
            # W8 spike: one Flip right per version for a spline (spur to spur) and for a coupling (to a dog, which
            # is a ring part); "+-" (the shafts facing opposite ways) was never shown, so it is not in the tables.
            ring = any(self._is_ring(n) or self.component_paths.get(n, "").replace("/", "\\").rsplit("\\", 1)[-1]
                       .lower().startswith("dog") for n in (a, b))
            key = f"collinear {'ring ' if ring else ''}{'++' if self._sigma(a) == self._sigma(b) else '+-'}"
            if key not in self.flip_needed:
                raise AssertionError(f"the fake does not know which Flip turns {mate.name} right ({key})")
            return False, key, bool(self.flip_needed[key])
        internal = self._is_ring(a) or self._is_ring(b)
        if internal:
            pinion, ring = (b, a) if self._is_ring(a) else (a, b)
            sign = lambda n: "+" if self._sigma(n) > 0 else "-"              # noqa: E731
            key = f"{'helical' if self._is_helical(ring) else 'spur'} ring {sign(pinion)}{sign(ring)}"
        else:
            key = "external +-" if self._sigma(a) != self._sigma(b) else "external ++"
        return internal, key, bool(self.flip_needed.get(key, False))

    def turns_right(self, name, path=None):
        """Whether a gear mate, as made, turns its gears as they mesh (its Flip the one its case needs)."""
        mate = self.mate(name, path)
        if mate.name in self.never_right:
            return False
        return mate.flip == self.mesh_case(mate)[2]

    def _helix(self, name):
        """(β in degrees, +1 right / -1 left) from a helical part's file name as the app names one (``…_45R``)."""
        import re
        path = self.component_paths.get(name, "")
        stem = path.replace("/", "\\").rsplit("\\", 1)[-1].rsplit(".", 1)[0]
        found = re.search(r"_(\d+(?:\.\d+)?)([LR])$", stem)
        return None if found is None else (float(found.group(1)), 1 if found.group(2) == "R" else -1)

    def _true_same(self, mate):
        """Whether the mesh truly turns its gears the same way about their own axes (k > 0), worked out by the fake
        from where the gears stand, never taken from the caller (W6-INTERFACES §7.18): ``turned_senses`` when a test
        sets it; else, on axes that meet (a bevel pair, each body on its own +Z side of the apex, D1), always False:
        at the pitch point both gears' surface speeds are ``ω·a × r``, and with each own axis pointing away from the
        apex the two cross products point opposite ways for any shaft angle and any cone (worked for fixture A in
        :func:`test_fixture_a_bevel_stage_turns_its_gears_opposite_ways_by_hand`); on axes that pass each other (a
        crossed pair), from the first gear's helix (its part's ``…_45R``) at the contact: with ``e`` the common
        perpendicular from gear a's line to gear b's, gear a's tooth there runs ``t = cos β·a_a + s·sin β·(a_a × e)``;
        the pitch-point speeds ``ω_a r_a (a_a × e)`` and ``−ω_b r_b (a_b × e)`` agree across the tooth (along
        ``n = t × e``), so the turns are the same way exactly when ``(a_a × e)·n`` and ``(a_b × e)·n`` differ in
        sign. Parallel axes: W5's, from the ring tables."""
        if self._turned(mate):
            if mate.name in self.turned_senses:
                return self.turned_senses[mate.name]
            a, b = mate.a[0], mate.b[0]
            pa, ga, pb, gb = self._origin(a), self._axis(a), self._origin(b), self._axis(b)
            if swcom.lines_meet(pa, ga, pb, gb):
                return False
            helix = self._helix(a)
            if helix is None:
                raise AssertionError(f"the fake cannot tell which way the crossed mesh {mate.name} turns: set "
                                     "turned_senses or name the part as the app names a helical one")
            cross = lambda u, v: (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],    # noqa: E731
                                  u[0] * v[1] - u[1] * v[0])
            dot = lambda u, v: sum(x * y for x, y in zip(u, v))                              # noqa: E731
            normal = cross(ga, gb)
            size = math.sqrt(dot(normal, normal))
            e = tuple(v / size for v in normal)
            if dot(tuple(pb[i] - pa[i] for i in range(3)), e) < 0:
                e = tuple(-v for v in e)
            beta, hand = math.radians(helix[0]), helix[1]
            ta = cross(ga, e)
            t = tuple(math.cos(beta) * ga[i] + hand * math.sin(beta) * ta[i] for i in range(3))
            n = cross(t, e)
            return dot(ta, n) * dot(cross(gb, e), n) < 0
        alike = sum(p * q for p, q in zip(self._axis(mate.a[0]), self._axis(mate.b[0]))) > 0
        if self._collinear(mate):
            return alike                   # W8-INTERFACES §9.3: both turn the same way about the world
        return self.mesh_case(mate)[0] == alike

    def gear_mate_sense(self, handle, same_sense, axes, meet=None):
        """As swcom.Session.gear_mate_sense: the turned gate, then a Reverse and two entity directions such that rule
        H tells the mate's TRUE sense (see the class), judged by ``swcom.sense_reading`` for the mesh and the axes
        the caller says."""
        self._log("gear_mate_sense", handle, same_sense)
        mate = self.mate(self.mate_handles[handle])
        title = self.active.title if self.active else "the assembly"
        if mate.suppressed and getattr(findings, "SUPPRESSED_GEAR_MATE_SENSE_READ", None) != "answers, marks nothing":
            # Until the W8 spike read a suppressed coupling's sense cleanly (SUPPRESSED_GEAR_MATE_SENSE_READ), no probe
            # had read Reverse or a suppressed mate's axes: the fake refuses, so a read made too early fails.
            raise SolidWorksError(f"The fake will not read which way the suppressed gear mate {mate.name} turns.")
        a, b = mate.a[0], mate.b[0]
        if self._turned(mate):
            if meet is None:
                meet = swcom.lines_meet(self._origin(a), self._axis(a), self._origin(b), self._axis(b))
            refusal = swcom.turned_refusal(f"{mate.name} in {title}", swcom.own_axes_angle(*axes),
                                           "so which way it turns is not read.", meet=bool(meet))
            if refusal is not None:
                raise SolidWorksError(refusal)
        taus = self.entity_senses.get(mate.name, (1, 1))
        directions = [tuple(taus[0] * v for v in self._axis(a)), tuple(taus[1] * v for v in self._axis(b))]
        product = (1 if self._true_same(mate) else -1) * taus[0] * taus[1]
        reverse = (product > 0) if self.turns_right(mate.name) else not (product > 0)
        reverse = self.turned_reverse.get(mate.name, reverse)
        if mate.name in self.entity_stray:
            directions[0] = tuple(self.entity_stray[mate.name])
        if mate.name in self.entity_swapped:
            directions.reverse()
        return swcom.sense_reading(reverse, directions, axes, same_sense, mate=f"{mate.name} in {title}")

    # -- W8: configurations (W8-PLAN §3.5), as the W8 spike measured SolidWorks 2026

    def _configuration_gate(self, *names):
        """As ``Session``: a configuration member refuses with its sentence while a finding it rests on is not
        settled (``swcom.configuration_finding``)."""
        for name in names:
            problem = swcom.configuration_finding(name)
            if problem is not None:
                raise SolidWorksError(f"Working with an assembly's configurations has not been settled on this "
                                      f"SolidWorks ({problem}), so nothing was read or changed.")

    def _named(self, name):
        return next((c for c in self.configs if c.casefold() == str(name).casefold()), None)

    def _leave(self):
        """The active configuration's flags and frames kept, before another is shown or added."""
        for mate in self.mates:
            mate.flags[self.config] = mate.suppressed
        if not self.shared_positions:
            self.frames_by[self.config] = self.frames

    def _enter(self, name):
        self.config = name
        for mate in self.mates:
            mate.suppressed = mate.flags.get(name, mate.suppressed)
        if not self.shared_positions:
            self.frames = self.frames_by.pop(name, None) or dict(self.frames)
        self.epoch += 1

    def configurations(self):
        self._log("configurations")
        return list(self.configs)

    def active_configuration(self):
        self._log("active_configuration")
        return self.config

    def add_configuration(self, name):
        """Adds and activates a copy of the active configuration: its flags, values and frames (the spike). Until
        the next rebuild, flag calls misbehave (``unsettled``)."""
        self._log("add_configuration", name)
        self._configuration_gate("CONFIGURATION_ADD_ROUTE")
        self._leave()
        self.configs.append(str(name))
        for mate in self.mates:
            mate.flags[str(name)] = mate.suppressed
        frames = dict(self.frames)
        self._enter(str(name))
        self.frames = frames
        self.unsettled = 2

    def show_configuration(self, name):
        """As ``ShowConfiguration2`` through ``Session``: already active, nothing changes (SolidWorks answered False,
        judged by the name); otherwise it is shown and marks the assembly modified, never a part (the spike). Every
        handle from before goes stale either way, as the Session raises its epoch."""
        self._log("show_configuration", name)
        self._configuration_gate("CONFIGURATION_SHOW_ROUTE")
        if self.current and _key(self.current) in getattr(self, "protected", ()) and \
                _key(self.current) not in getattr(self, "read_only_opened", ()):
            raise AssertionError(f"the app showed {name} in {self.current}, the old assembly open in the user's session "
                                 "(W9D D2: never shown)")
        found = self._named(name)
        self.step_puts = set()
        if found is None:
            self.epoch += 1
            raise SolidWorksError(f"SolidWorks would not show the configuration {name}.")
        if found == self.config:
            self.epoch += 1
            return
        self._leave()
        self._enter(found)
        self._touch()

    def delete_configuration(self, name):
        self._log("delete_configuration", name)
        self._configuration_gate("CONFIGURATION_DELETE_ROUTE")
        found = self._named(name)
        title = self.active.title if self.active else "the assembly"
        if found == self.config:
            raise SolidWorksError(f"The configuration {name} is the active one in {title}, and the active "
                                  "configuration is never deleted.")
        if found is not None:
            self._touch()                  # as SolidWorks: a configuration deleted marks the assembly modified
            self.configs.remove(found)
            self.frames_by.pop(found, None)
            for mate in self.mates:
                mate.flags.pop(found, None)
                mate.own.pop(found, None)

    def set_mate_suppressed_in(self, handle, suppressed, configurations):
        """As ``Session.set_mate_suppressed_in``: every named configuration's flag set, read back. Until the first
        rebuild after an add, the spike's misbehaviour: the first call takes (it raised, and the Session judges by
        the read-back), the second does nothing, so the Session's read-back raises."""
        self._log("set_mate_suppressed_in", handle, suppressed, tuple(configurations))
        self._configuration_gate("MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE", "SPECIFY_CONFIGURATIONS")
        if not configurations:
            return
        name = self.mate_handles[handle]
        mate = self.mate(name)
        self._not_users_mate(name, "suppressed or turned on")
        if not suppressed:
            self.step_puts = set()
        if self.unsettled == 1:
            self.unsettled = 0
            state = "suppressed" if not suppressed else "on"
            raise SolidWorksError(f"SolidWorks would not {'suppress' if suppressed else 'turn on'} the mate {name} "
                                  f"in {', '.join(configurations)}: it still reads {state} there.")
        if self.unsettled == 2:
            self.unsettled = 1
        for config in configurations:
            found = self._named(config)
            if found is None:
                raise SolidWorksError(f"There is no configuration {config} to set the mate {name} in.")
            mate.flags[found] = bool(suppressed)
            if found == self.config:
                mate.suppressed = bool(suppressed)

    def mate_suppression(self, handle, configurations):
        self._log("mate_suppression", handle, tuple(configurations))
        self._configuration_gate("MATE_SUPPRESSION_PER_CONFIGURATION_ROUTE", "SPECIFY_CONFIGURATIONS")
        mate = self.mate(self.mate_handles[handle])
        mate.flags[self.config] = mate.suppressed
        return {str(c): bool(mate.flags.get(self._named(c), False)) for c in configurations}

    def set_dimension_in(self, mate_handle, value_mm, configurations):
        """A distance mate's value in the named configurations only, whichever is active (follow-up A)."""
        self._log("set_dimension_in", mate_handle, float(value_mm), tuple(configurations))
        self._configuration_gate("SLIDE_VALUE_ROUTE", "SET_VALUE_IN_SPECIFIC_CONFIGURATIONS")
        mate = self.mate(self.mate_handles[mate_handle])
        self._not_users_mate(mate.name, "given a value")
        for config in configurations:
            mate.own[self._named(config) or str(config)] = abs(float(value_mm))

    def dimension_values(self, mate_handle, configurations):
        """Each named configuration's own value; one with none of its own reads 0, but for the active one, which
        reads where it stands (follow-up A)."""
        self._log("dimension_values", mate_handle, tuple(configurations))
        self._configuration_gate("SLIDE_VALUE_ROUTE", "SPECIFY_CONFIGURATIONS")
        mate = self.mate(self.mate_handles[mate_handle])
        out = {}
        for config in configurations:
            found = self._named(config)
            out[str(config)] = mate.own.get(found, abs(mate.value) if found == self.config else 0.0)
        return out

    # -- W7: carriers (W7-PLAN §2.9), as the spike measured SolidWorks 2026 (W7-SPIKE.md)

    def _carrier_target(self, mate):
        """The component an axis mate holds its gear to, when that is not the layout (a carrier): else None."""
        if mate.axis and not mate.b[0].startswith("layout"):
            return mate.b[0]
        return None

    def _rides(self, name):
        """The carrier a component's axis is mated to (its unsuppressed axis mate's target, not the layout)."""
        for m in self.mates:
            if not m.suppressed and m.axis and m.a[0] == name and self._carrier_target(m):
                return m.b[0]
        return None

    def _turn_rows(self, mates):
        """Each gear mate and lock of ``mates`` as a row over the bodies' own-axis turns (a dict body → coefficient,
        the row summing to 0), as SolidWorks 2026 holds them (W7-SPIKE.md): a lock keeps two turns equal; a gear
        mate relates its two gears' turns RELATIVE TO the carrier either rides (the line joining their axes), or
        absolutely when neither rides one: ``rel_b = k·rel_a``, ``rel = δ − s·δ_c``, ``s`` the sign of the gear's
        axis against the carrier's, ``k = ±za/zb`` by the mesh's TRUE sense (``_true_same``), the other sign when
        the mate is made the wrong way round (``turns_right``)."""
        rows = []
        for m in mates:
            if m.kind == "lock":
                rows.append({m.a[0]: 1.0, m.b[0]: -1.0})
                continue
            x, y = m.a[0], m.b[0]
            k = (1.0 if self._true_same(m) else -1.0) * m.ratio[0] / m.ratio[1]
            if m.name in self.never_right or m.flip != self.mesh_case(m)[2]:     # as turns_right, for any mate
                k = -k
            row = {}

            def add(body, coef):
                row[body] = row.get(body, 0.0) + coef

            add(y, 1.0)
            add(x, -k)
            c = self._rides(x) or self._rides(y)
            if c is not None and c not in (x, y):
                sign = lambda g: 1.0 if sum(p * q for p, q in zip(self._axis(g), self._axis(c))) > 0 else -1.0  # noqa: E731
                add(c, -sign(y))
                add(c, k * sign(x))
            rows.append(row)
        return rows

    @staticmethod
    def _solve_rows(rows, known):
        """Gaussian elimination of ``rows`` (dicts body → coefficient, each summing to 0) with ``known`` turns:
        (the turns, the rank of the rows over the unknown bodies). A body the rows leave free turns 0."""
        bodies = sorted({b for row in rows for b in row if b not in known})
        index = {b: i for i, b in enumerate(bodies)}
        matrix = []
        for row in rows:
            line = [0.0] * (len(bodies) + 1)
            for body, coef in row.items():
                if body in known:
                    line[-1] -= coef * known[body]
                else:
                    line[index[body]] += coef
            matrix.append(line)
        rank, pivots = 0, []
        for col in range(len(bodies)):
            pivot = max(range(rank, len(matrix)), key=lambda r: abs(matrix[r][col]), default=None)
            if pivot is None or abs(matrix[pivot][col]) < 1e-9:
                continue
            matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
            lead = matrix[rank][col]
            matrix[rank] = [v / lead for v in matrix[rank]]
            for r in range(len(matrix)):
                if r != rank and abs(matrix[r][col]) > 0:
                    factor = matrix[r][col]
                    matrix[r] = [a - factor * b for a, b in zip(matrix[r], matrix[rank])]
            pivots.append(col)
            rank += 1
        turns = dict(known)
        for b in bodies:
            turns[b] = 0.0
        for r, col in enumerate(pivots):
            turns[bodies[col]] = matrix[r][-1]
        return turns, rank

    def _over_defines(self, mate):
        """Whether ``mate`` adds nothing to the turn rows of the free bodies already mated (W7-PLAN §2.9, review
        S12: judged by the rank of the rows with the carrier's column, not by the planner's rule)."""
        live = [m for m in self.mates if not m.suppressed and m.kind in ("gear", "lock") and m is not mate]
        held = {b: 0.0 for b in self.fixed}
        _, before = self._solve_rows(self._turn_rows(live), held)
        _, after = self._solve_rows(self._turn_rows(live + [mate]), held)
        return after == before

    def _carry(self, frame, carrier, degrees):
        """``frame`` carried round ``carrier``'s own axis line (its origin, its third column) by ``degrees``."""
        rotation, at = self.frames[carrier]
        axis = (rotation[2], rotation[5], rotation[8])
        x, y, z = axis
        a = math.radians(degrees)
        c, s_, t = math.cos(a), math.sin(a), 1.0 - math.cos(a)
        rows = (t * x * x + c, t * x * y - s_ * z, t * x * z + s_ * y,
                t * x * y + s_ * z, t * y * y + c, t * y * z - s_ * x,
                t * x * z - s_ * y, t * y * z + s_ * x, t * z * z + c)
        off = tuple(frame[1][i] - at[i] for i in range(3))
        moved = _apply(rows, off)
        return _mul(rows, frame[0]), tuple(at[i] + moved[i] for i in range(3))

    def drive(self, name, degrees):
        """Turn one gear about its own axis and every body its unsuppressed gear mates and locks carry, as the
        SOLVER would: the rows of :meth:`_turn_rows` solved with the driven gear's turn and every fixed component
        at 0 (a loop, the planetary's, is one linear system); a wrong-sense gear mate turns its partner the wrong
        way (ring_mate_sense: such a pair clashed when driven; the spike: the ring mate made the wrong way round
        turned the carrier −15° and the planets −60° for +30° on the sun). A planet riding a carrier is carried
        round the carrier's axis by the carrier's turn and turns on its own axis by the rest. Returns each body's
        own-axis turn, for the bodies joined to the driven one; a body the mates leave free stays put."""
        mates = [m for m in self.mates if not m.suppressed and m.kind in ("gear", "lock")]
        joined, queue = {name}, [name]
        while queue:
            x = queue.pop()
            for m in mates:
                ends = {m.a[0], m.b[0]}
                if x in ends:
                    ends |= {c for c in (self._rides(m.a[0]), self._rides(m.b[0])) if c}
                elif x in {self._rides(m.a[0]), self._rides(m.b[0])}:
                    pass
                else:
                    continue
                for y in ends - joined:
                    joined.add(y)
                    queue.append(y)
        known = {b: 0.0 for b in self.fixed}
        known[name] = float(degrees)
        solved, _ = self._solve_rows(self._turn_rows(mates), known)
        turns = {b: solved.get(b, 0.0) for b in joined if b not in self.fixed or b == name}
        new = {}
        for body, turn in turns.items():
            carrier = self._rides(body)
            if carrier is not None and turns.get(carrier):
                sign = 1.0 if sum(p * q for p, q in zip(self._axis(body), self._axis(carrier))) > 0 else -1.0
                carried = self._carry(self.frames[body], carrier, turns[carrier])
                new[body] = (_mul(carried[0], _rot_z(turn - sign * turns[carrier])), carried[1])
            else:
                rotation, at = self.frames[body]
                new[body] = (_mul(rotation, _rot_z(turn)), at)
        self._moved_by_hand(new)
        return turns

    # -- W9d: Build again… carries the user's work (W9D-INTERFACES §10, §14.1's "what the fake gains")
    #
    # Knobs: ``protected`` (lower-cased paths: the old assembly and the user's files) — any write while one is the
    # current document fails the test, and so does a show of one the job did not open read-only; ``no_save_after``
    # (a lower-cased path): once it is saved, any later save fails the test; ``component_configs`` (Name2 -> (referenced,
    # its document's active, its file's configurations)); ``states_by`` (configuration -> {Name2: GetSuppression2});
    # ``states_mark`` (the unshown state read marks the assembly) and ``states_read_unsaved``; ``file_versions`` (lower-
    # cased path -> the version that last saved it; else the running one) and ``dependencies_of``; ``read_only_left``
    # (a read-only close leaves the document open); ``read_marks`` (lower-cased paths a definition read marks);
    # ``reload_ok`` (a reference read in a read-only load resolves after it was closed); ``coaxial`` ((path, target) ->
    # bool, read once findings.COAXIAL_FACE_READ is set); ``remake_status`` / ``remake_codes`` (old mate name -> AddMate5's
    # status / (code, warning) after the remake); ``insert_config_kept`` False: an insert in a configuration reads back
    # the document's active one; ``kind_swap`` (old mate names a remake reads back with its entities the other way).

    DEF_TYPES = dict(MATE_TYPES, concentric=1, perpendicular=2, parallel=3, tangent=4, width=11, slot=21)
    _TYPE_WORDS = {0: "coincident", 1: "concentric", 2: "perpendicular", 3: "parallel", 4: "tangent", 5: "distance",
                   6: "angle", 10: "gear", 16: "lock"}

    def _w9d(self):
        for name, value in (("protected", set()), ("no_save_after", ""), ("component_configs", {}), ("states_by", {}),
                            ("states_mark", False), ("states_read_unsaved", True), ("file_versions", {}),
                            ("dependencies_of", {}), ("read_only_opened", set()), ("read_only_left", False),
                            ("read_marks", set()), ("reload_ok", False), ("coaxial", {}), ("remake_status", {}),
                            ("remake_codes", {}), ("insert_config_kept", True), ("kind_swap", set()),
                            ("refs_read_only", set()), ("saved_after", False)):
            if not hasattr(self, name):
                setattr(self, name, value)
        return self

    def _finding(self, name):
        return getattr(findings, f"{name}_ON_{swcom.release_year(self.revision[0])}", None)

    def _gate(self, name, what, wanted=None):
        value = self._finding(name)
        if value is None or (wanted is not None and value != wanted):
            raise SolidWorksError(f"{what} has not been measured on this SolidWorks.")

    def save_flags(self):
        self._log("save_flags")
        return {d.path: (_key(d.path) in self.touched or self.memory.get(_key(d.path)) != self.saved.get(_key(d.path)))
                for d in self.open_docs}

    def file_version(self, path):
        self._log("file_version", path)
        self._gate("FILE_VERSION_READ", "Reading a file's version")
        return self._w9d().file_versions.get(_key(path), self.revision[0])

    def running_file_version(self):
        return self.revision[0]

    def dependencies(self, path):
        self._log("dependencies", path)
        self._gate("DEPENDENCIES_READ", "Reading a file's dependencies")
        return list(self._w9d().dependencies_of.get(_key(path), []))

    def open_read_only(self, path):
        self._log("open_read_only", path)
        self._gate("OPEN_READ_ONLY_ROUTE_WHEN_NOT_OPEN", "Opening read-only")
        self._w9d()
        if any(_key(d.path) == _key(path) for d in self.open_docs):
            raise AssertionError(f"the job opened {path} read-only while it was open (W9D §3 R.2)")
        self._stash()
        info = DocInfo(title=path.replace("/", "\\").rsplit("\\", 1)[-1], path=path, doc_type=2)
        self.memory[_key(path)] = copy.deepcopy(self.saved.get(_key(path), ([], [])))
        self.equations_text, self.made = self.memory[_key(path)]
        self.memory_mates[_key(path)] = copy.deepcopy(self.saved_mates.get(_key(path), []))
        self.mates = self.memory_mates[_key(path)]
        configs, config, frames_by = self.saved_configs.get(_key(path), (["Default"], "Default", {}))
        self.configs, self.config, self.frames_by = list(configs), config, copy.deepcopy(frames_by)
        self.current = path
        self.open_docs.append(info)
        self.read_only_opened.add(_key(path))
        if getattr(self, "read_only_needs_regen", False):
            self.touched.add(_key(path))          # as 2026 read it: modified straight after the open (NeedsRegen)
        self.epoch += 1
        return info

    def close_unsaved(self, path):
        self._log("close_unsaved", path)
        if _key(path) not in self._w9d().read_only_opened:
            raise AssertionError(f"the job closed {path}, which it did not open (W9D §10)")
        self.read_only_opened.discard(_key(path))
        if not self.read_only_left:
            self.open_docs = [d for d in self.open_docs if _key(d.path) != _key(path)]
            for kept in (self.memory, self.memory_mates, self.memory_configs):
                kept.pop(_key(path), None)
            self.touched.discard(_key(path))
        self.current = ""
        self.epoch += 1

    def component_configurations(self, handle):
        self._log("component_configurations", handle)
        name = self._name2(handle)
        referenced, active, names = self._w9d().component_configs.get(name, ("Default", "Default", ("Default",)))
        if name in self.lightweight or self._state_in(name, self.config) in (0, 1, 4):
            # As the Session: no document (GetModelDoc2 None), so the file's names read closed, no active one.
            self._log("file_configurations", self.component_paths.get(name, ""))
            active = ""
        return (referenced if self._finding("REFERENCED_CONFIGURATION_READ") is True else ""), active, tuple(names)

    def component_states_in(self, names, configurations):
        self._log("component_states_in", tuple(names), tuple(configurations))
        self._gate("COMPONENT_STATE_PER_CONFIGURATION_ROUTE", "Reading states per mode")
        if self._w9d().states_mark:
            self._touch()
        out = {}
        for name in names:
            out[name] = {c: self._state_in(name, self._named(c) or c) == 0 for c in configurations}
        return out

    def _state_in(self, name, config):
        return self._w9d().states_by.get(config, {}).get(name, self.component_states.get(name, 2))

    def set_component_suppressed(self, handle, suppressed):
        self._log("set_component_suppressed", handle, suppressed)
        self._gate("CARRY_INSERTS", "Setting a carried component's state")
        name = self._name2(handle)
        self._not_users(name, "suppressed or resolved")
        self._touch()
        self._w9d().states_by.setdefault(self.config, {})[name] = 0 if suppressed else 2

    def add_component_in(self, handle, path, at, configuration):
        self._log("add_component_in", handle, path, configuration)
        self._gate("CARRY_INSERTS_IN_A_CONFIGURATION", "Inserting in a configuration", True)
        name = self.add_component(handle, path, at)
        source = next((v for k, v in self._w9d().component_configs.items() if self.component_paths.get(k) == path),
                      ("Default", "Default", ("Default",)))
        kept = configuration if self.insert_config_kept else source[1]
        self.component_configs[name] = (kept, source[1], tuple(source[2]))
        return name

    def _entity_target(self, end):
        return end[1]

    def mate_definition(self, handle):
        self._log("mate_definition", handle)
        self._w9d()
        if self.current and _key(self.current) in self.read_marks:
            self.touched.add(_key(self.current))            # a read that marks (doctored)
        mate = self.mate(self.mate_handles[handle])
        info = self.mate_info(handle)
        kinds = info.entities or tuple(self._entity_kind(mate, e) for e in (mate.a, mate.b))
        values = []
        if mate.kind in ("distance", "point distance", "limit distance"):
            values.append(("Distance", abs(mate.value) / 1000.0))
        if mate.kind in ("angle", "axis angle", "limit angle"):
            values.append(("Angle", math.radians(mate.value)))
        if mate.kind in ("limit distance", "limit angle"):
            values += list(getattr(mate, "limits", ()))
        if mate.kind == "gear":
            values += [("GearRatioNumerator", float(mate.ratio[1])), ("GearRatioDenominator", float(mate.ratio[0])),
                       ("Reverse", 1.0 if mate.flip else 0.0)]
        select = {"face": 2, "edge": 1, "vertex": 3, "plane": 4, "whole": 20, "origin": 6}
        entities = tuple(swcom.MateEntityRead(c, 5 if k == "feature" and f.endswith("Axis") else
                                              select.get(k, 4 if k == "feature" else -1), k, f, (0, 0, 0, 0, 0, 1))
                         for c, (k, f) in zip(info.components, kinds))
        alignment = mate.alignment if mate.user else getattr(self, "readback_alignment", {}).get(mate.name,
                                                                                                  mate.alignment)
        return swcom.MateDefinition(mate.name, self.DEF_TYPES.get(mate.kind, info.type), mate.kind, alignment,
                                    bool(mate.flip and mate.kind != "gear"), tuple(values), entities, info.whole)

    def entity_reference(self, mate_handle, index):
        self._log("entity_reference", mate_handle, index)
        mate = self.mate(self.mate_handles[mate_handle])
        end = (mate.a, mate.b)[index]
        kind, _ = self._entity_kind(mate, end)
        finding = {"feature": "PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES",
                   "plane": "PERSIST_REFERENCE_ROUTE_FOR_REFERENCE_FEATURES", "face": "PERSIST_REFERENCE_ROUTE_FOR_FACES",
                   "edge": "PERSIST_REFERENCE_ROUTE_FOR_EDGES", "vertex": "PERSIST_REFERENCE_ROUTE_FOR_VERTICES"}
        coaxial = None
        if kind == "face" and self._finding("COAXIAL_FACE_READ") is True:
            coaxial = self._w9d().coaxial.get((_key(self.component_paths.get(end[0], "")), end[1]))
        if kind not in ("feature", "plane") or self._finding(finding[kind]) is None:
            return kind, "", coaxial, "no measured route"           # a face or an edge is entity_references'

        part = self.component_paths.get(end[0], "")
        hexed = f"{_key(part)}|{end[1]}".encode().hex()
        if self.current and _key(self.current) in self._w9d().read_only_opened:
            self.refs_read_only.add(hexed)
        return kind, hexed, coaxial, ""

    def entity_references(self, component, items, candidates=200, seconds=20.0):
        """§10's walk, as Session.entity_references: the finding must be swcom.PERSIST_ROUTE_R3 exactly. Knobs (by
        (lower-cased part path, target)): ``r3_filtered`` the candidates left by the prefilter (default 2: a sprocket's
        equal end faces), ``r3_matches`` how many of them read IsSame (default 1), ``r3_resolve`` the resolve's code
        (default 0, Ok), ``r3_seconds`` the seconds each candidate takes (default 0), ``radius`` a cylinder's or
        circle's radius in mm; ``coaxial`` as before. ``walks`` logs (component, items) per call."""
        self._log("entity_references", component, tuple(items))
        self._w9d()
        for name in ("r3_filtered", "r3_matches", "r3_resolve", "r3_seconds", "radius", "walks"):
            if not hasattr(self, name):
                setattr(self, name, [] if name == "walks" else {})
        self.walks.append((component, tuple(items)))
        out, carried, clock, capped = [], set(), 0.0, ""
        name = self._name2(component)
        stats = []
        self.last_walk = {"component": name, "items": stats}
        part = _key(self.component_paths.get(name, ""))
        for mate_handle, index, kind in items:
            finding = "PERSIST_REFERENCE_ROUTE_FOR_FACES" if kind == "face" else "PERSIST_REFERENCE_ROUTE_FOR_EDGES"
            if self._finding(finding) != swcom.PERSIST_ROUTE_R3:
                out.append((kind, "", None, None, "", f"no measured route for a {kind} here"))
                continue
            mate = self.mate(self.mate_handles[mate_handle])
            end = (mate.a, mate.b)[index]
            key = (part, end[1])
            filtered = [(key, i) for i in range(self.r3_filtered.get(key, 2))]
            stats.append((kind, len(filtered), len(filtered), ("area", None), self.r3_matches.get(key, 1)))
            fresh = [f for f in filtered if f not in carried]
            if not capped and len(carried) + len(fresh) > candidates:
                capped = "candidates"
            if not capped and clock > seconds:
                capped = "seconds"
            if not capped:
                for f in fresh:
                    clock += self.r3_seconds.get(key, 0.0)
                    if clock > seconds:
                        capped = "seconds"
                        break
                    carried.add(f)
            if capped:
                out.append((kind, "", None, None, capped, ""))
                continue
            if self.r3_matches.get(key, 1) != 1:
                out.append((kind, "", None, None, "", f"SolidWorks did not say which one {kind} of {name} it is on"))
                continue
            if self.r3_resolve.get(key, 0) != 0:
                out.append((kind, "", None, None, "", f"its reference resolved {self.r3_resolve[key]}, not Ok"))
                continue
            coaxial = radius = None
            if self._finding("COAXIAL_FACE_READ") is True:
                coaxial, radius = self.coaxial.get(key), self.radius.get(key)
            out.append((kind, f"{part}|{end[1]}".encode().hex(), coaxial, radius, "", ""))
            if self.current and _key(self.current) in self.read_only_opened:
                self.refs_read_only.add(out[-1][1])
        self.last_walk.update(carried=len(carried), seconds=clock, capped=capped)
        return out

    def _resolve(self, target):
        if target.startswith("ref:"):
            _, handle, kind, hexed = target.split(":", 3)
            part, _, entity = bytes.fromhex(hexed).decode().partition("|")
            name = self._name2(handle)
            if _key(self.component_paths.get(name, "")) != part:
                raise SolidWorksError(f"The {kind} could not be found again in {name}.")
            if hexed in self._w9d().refs_read_only and not self.reload_ok:
                raise SolidWorksError(f"The {kind} could not be found again in {name} after its part was reloaded.")
            if entity in getattr(self, "resolve_other_kind", set()):        # S8: resolved to another kind
                raise swcom.ReferenceKindError(f"The {kind} of {name} found again is a face, which Gear Generator "
                                               "never takes for it.")
            return name, entity
        if ":" in target:
            handle, _, feature = target.partition(":")
            return ("asm" if handle == "asm" else self._name2(handle)), feature
        return self._name2(target), ""

    def remake_mate(self, handle, definition, targets, name, ratio=(1.0, 1.0), flip=None):
        self._log("remake_mate", handle, tuple(targets), name, flip)
        if not self._finding("CARRY_REMAKE_KINDS"):
            raise SolidWorksError("Making a mate again has not been measured on this SolidWorks.")
        self._w9d()
        ends = [self._resolve(t) for t in targets]
        for end, target in zip(ends, targets):
            if end[0] != "asm" and self._state_in(end[0], self.config) == 0:
                # Inferred (W9c's probes: a suppressed component has no document): nothing of it can be selected.
                raise SolidWorksError(f"{target} could not be selected for a mate: {end[0]} is suppressed in "
                                      f"{self.config}.")
        word = self._TYPE_WORDS.get(definition.type, "other")
        values = dict(definition.values)
        if word in ("distance", "angle") and any(k.startswith(("Maximum", "Minimum")) for k in values):
            word = f"limit {word}"
        # The ledger (API-LEDGER.md:612): MateEntity(0) is the SECOND selection for an axis–axis coincident, a
        # face–axis concentric and a point–plane coincident; the first otherwise. Kept here as MateEntity order.
        kinds = [self._entity_kind(FakeMate("", word, e, e), e) for e in ends]
        axis = [k == ("feature", f) and f.endswith("Axis") for k, (_, f) in zip(kinds, ends)]
        point = [k[0] in ("origin", "vertex") for k in kinds]
        plane = [k[0] == "plane" or (k[0] == "feature" and k[1].endswith("Plane")) for k in kinds]
        face = [k[0] == "face" for k in kinds]
        second_first = (word == "coincident" and all(axis)) or (word == "concentric" and any(face) and any(axis)) or \
            (word == "coincident" and any(point) and any(plane))
        if second_first:
            ends.reverse()
        if definition.name in self.kind_swap:
            ends.reverse()
        if word == "gear":
            value = 0.0
        elif "Distance" in values:
            value = values["Distance"] * 1000.0
        else:
            value = math.degrees(values.get("Angle", 0.0))
        taken = {m.name for m in self.mates}
        kept = name if name not in taken else f"Mate{len(self.calls)}"
        flipped = bool(definition.flipped) if flip is None else bool(flip)
        self._keep_mate(handle, kept, word, "x", "x", value, tuple(ratio), flipped)
        mate = self.mates[-1]
        mate.a, mate.b = ends[0], ends[1]
        mate.alignment = definition.alignment
        if word.startswith("limit"):
            mate.limits = tuple((k, v) for k, v in values.items() if k.startswith(("Maximum", "Minimum")))
        if word == "gear":
            # The Reverse SolidWorks reads follows the Flip given, the other way for a mate in ``flip_inverts``: a
            # remake with the old Flip may read the wrong sense, and the other Flip the right one (§10, W5's remake).
            mate.flip = flipped != (definition.name in getattr(self, "flip_inverts", set()))
        mate.status = self.remake_status.get(definition.name, 1)
        if definition.name in self.remake_codes:
            mate.code, mate.warning = self.remake_codes[definition.name]
        for config, code in getattr(self, "remake_codes_in", {}).get(definition.name, {}).items():
            self.mate_codes_in.setdefault(config, {})[kept] = code          # a code in one configuration only
        if word == "lock" and ends[0][0] != "asm":
            # A lock carries its follower with its anchor in every configuration (the fake solves nothing on a show).
            anchor, follower = ends[0][0], ends[1][0]
            if anchor in self.frames and follower in self.frames:
                rel = _compose(_inverse(self.frames[anchor]), self.frames[follower])
                for frames in self.frames_by.values():
                    if anchor in frames:
                        frames[follower] = _compose(frames[anchor], rel)
        self._touch()
        return kept, mate.status

    def delete_mate(self, handle):
        self._log("delete_mate", handle)
        name = self.mate_handles[handle]
        self._not_users_mate(name, "deleted")
        self.mates[:] = [m for m in self.mates if m.name != name]
        self._touch()


@pytest.fixture(autouse=True)
def _train_routes_agree(monkeypatch):
    """Every test here builds a train under the route it re-solves under, and reads a gear mate's ratio as probe
    gear_mate_ratio did, set here rather than read from findings.py, so a probe round moving a finding never turns a
    test red (a test about one of them sets its own)."""
    monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", "ForceRebuild3(True)", raising=False)
    monkeypatch.setattr(findings, "MATED_BUILD_REBUILD_ROUTE", "ForceRebuild3(True)", raising=False)
    monkeypatch.setattr(findings, "GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", True, raising=False)
    for name, value in (("GEAR_MATE_DEFINITION_READ_MARKS", "nothing"), ("MATES_UNDER_COMMAND_IN_PROGRESS", True),
                        ("MATE_RENAME_AT_ONCE", True),
                        ("GEAR_MATE_SENSE_READ_BACK", "(Reverse == entities parallel) == internal"),
                        ("GEAR_MATE_READ_BACK_TELLS_SENSE", True), ("GEAR_MATE_CHECK_AND_REMAKE_HOLDS", True),
                        ("GEAR_MATE_FLIP", False), ("GEAR_MATE_SENSE_READ_MARKS", "nothing"),
                        ("GEAR_MATE_SENSE_READ_POINTS_AGREE", True), ("CROSS_VERSION_READ_BACK_TELLS_SENSE", True),
                        ("GEAR_MATE_SENSE_READ_UNDER_COMMAND_IN_PROGRESS", True),
                        ("GEAR_MATE_REMAKE_UNDER_COMMAND_IN_PROGRESS", True),
                        ("GEAR_MATE_READ_BACK_HOLDS_AFTER_A_RATIO_REMAKE", True)):
        monkeypatch.setattr(findings, name, value, raising=False)


def plan(spec=None, recipe="A", path=PATH):
    spec = spec or GearSpec()
    return SPUR.plan(spec, SPUR.derive(spec), recipe, "", path)


def names(fake):
    return [name for name, _ in fake.calls]


def _ring_lands(before, after, measured=0.05):
    """Whether a ring's globals set from ``before`` to ``after`` land its new flank start on where Li+ ends now, by
    the ring's own maths (``internal.section`` and ``involute_flank``): closer than ``measured`` of Li+'s length (run 6
    failed at 0.038 and rebuilt at 1.0 and above)."""
    from gear_generator.gears import internal

    def flank(values):
        g = internal.section(int(round(values["No. of Teeth"])), values["Module"], values["Pressure Angle"],
                             values.get("Face Width", 10.0), None, values["Backlash"], values["Fillet Radius"])
        return internal.involute_flank(g)
    if "Inner Diameter" not in before or "Inner Diameter" not in after:
        return False
    try:
        old, new = flank(before), flank(after)
    except Exception:  # noqa: BLE001 - not a ring the maths makes: nothing modelled
        return False
    import math
    return math.dist(old.cap, new.start) < measured * math.dist(new.start, new.cap)


def never_exists(_path):
    return False


# -- order ------------------------------------------------------------------


@pytest.mark.parametrize("recipe", ["A", "B"])
def test_a_clean_build_suppresses_first_rebuilds_once_then_saves(recipe):
    fake = FakeSolidWorks()
    result = swbuild.build(fake, plan(recipe=recipe), never_exists)
    called = names(fake)
    assert result.ok, result.failures
    assert called[:3] == ["begin_build", "new_part", "detect_trig_units"]
    first_geometry = next(i for i, n in enumerate(called) if n in ("insert_axis", "open_sketch"))
    assert called.index("suppress") < first_geometry
    assert called.count("rebuild") == 1
    assert fake.calls[called.index("rebuild")] == ("rebuild", (False,))
    assert called[-1] == "save_as" and called.index("rebuild") < called.index("save_as")
    assert result.saved == PATH
    assert "ok      rebuilt once" in result.log_lines()


def test_every_global_is_added_before_any_link():
    fake = FakeSolidWorks()
    swbuild.build(fake, plan(), never_exists)
    called = names(fake)
    last_global = max(i for i, n in enumerate(called) if n == "add_global_variable")
    first_link = called.index("link_dimension")
    assert last_global < first_link
    assert called.count("add_global_variable") == 24


def test_the_measured_trig_units_choose_the_expressions():
    fake = FakeSolidWorks(trig=RADIANS)
    result = swbuild.build(fake, plan(), never_exists)
    base = next(args for name, args in fake.calls if name == "add_global_variable" and args[0] == "Base Diameter")
    assert "180" in base[1] and result.ok and result.trig == RADIANS


def test_manual_steps_are_counted_in_the_log():
    result = swbuild.build(FakeSolidWorks(), plan(), never_exists)
    lines = result.log_lines()
    assert "MANUAL  1 step(s) to do by hand" in lines
    assert any(line.startswith("MANUAL  Assign a material") for line in lines)


# -- failures ----------------------------------------------------------------


def test_the_flag_is_restored_and_the_build_stops_at_the_failing_op():
    fake = FakeSolidWorks(fail_on={"cut_extrude": "FeatureCut4 would not cut the tooth space."})
    result = swbuild.build(fake, plan(), never_exists)
    called = names(fake)
    assert not result.ok
    assert result.stopped_at.startswith("cut ")
    assert result.failures[0][1] == "FeatureCut4 would not cut the tooth space."
    assert "circular_pattern" not in called
    assert fake.suppressed is False
    assert called.count("rebuild") == 1
    assert "save_as" not in called
    assert called[-1] == "end_build"
    assert any(line.startswith("FAIL    cut") for line in result.log_lines())


def test_a_raise_that_is_not_a_solidworks_error_is_a_failure_and_still_restores_the_flag():
    """W4 review B1: once the document is made, build() keeps its word that every problem is a failure."""
    fake = FakeSolidWorks()

    def boom(*_args):
        raise RuntimeError("the COM server went away")

    fake.sketch_circle = boom
    result = swbuild.build(fake, plan(), never_exists)
    assert not result.ok and result.document == "Part1" and not result.saved
    assert result.failures == [("the build", "it stopped on an unexpected RuntimeError: the COM server went away.")]
    assert fake.suppressed is False
    assert names(fake)[-1] == "end_build" and "save_as" not in names(fake)


def test_a_save_that_raises_anything_is_the_saves_failure():
    fake = FakeSolidWorks()

    def gone(_path):
        raise RuntimeError("(-2147023170, 'The remote procedure call failed.', None, None)")

    fake.save_as = gone
    result = swbuild.build(fake, plan(), never_exists)
    assert not result.saved and result.failures[0][0] == "save"
    assert result.failures[0][1].startswith("it stopped on an unexpected RuntimeError: ")


def test_a_name_solidworks_did_not_keep_stops_before_the_link_that_uses_it():
    fake = FakeSolidWorks(rename={"Blank Sketch": "Sketch1"})
    result = swbuild.build(fake, plan(), never_exists)
    assert not result.ok
    assert "'Sketch1' instead of 'Blank Sketch'" in result.failures[0][1]
    assert "link_dimension" not in names(fake)
    assert "save_as" not in names(fake)


def test_a_global_that_disagrees_with_the_maths_fails_and_is_not_saved():
    fake = FakeSolidWorks(values={"Base Diameter": 12.0})
    result = swbuild.build(fake, plan(), never_exists)
    assert not result.ok and "Base Diameter" in result.failures[0][0]
    assert "save_as" not in names(fake)


def test_a_failed_rebuild_is_not_saved():
    fake = FakeSolidWorks(rebuild_ok=False)
    result = swbuild.build(fake, plan(), never_exists)
    assert "save_as" not in names(fake)
    assert "FAIL    the rebuild reported an error" in result.log_lines()


def test_an_under_defined_sketch_is_a_check_not_a_failure():
    fake = FakeSolidWorks(statuses={"Tooth Space Sketch": 2})
    result = swbuild.build(fake, plan(), never_exists)
    assert result.ok and result.saved
    assert "CHECK   Tooth Space Sketch is under-defined, not fully defined" in result.log_lines()


def test_an_existing_file_is_refused_before_anything_is_made():
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError, match="already exists"):
        swbuild.build(fake, plan(), lambda path: True)
    assert fake.calls == []


def test_an_old_solidworks_is_refused():
    fake = FakeSolidWorks()
    fake.revision = (31, 5, 0)
    with pytest.raises(swbuild.BuildError, match="2024"):
        swbuild.build(fake, plan(), never_exists)


def test_an_unsound_plan_is_refused():
    good = plan()
    broken = BuildPlan(good.kind, good.recipe, good.ops[:-2] + (SaveAs(PATH),), good.path)
    with pytest.raises(swbuild.BuildError, match="not sound"):
        swbuild.build(FakeSolidWorks(), broken, never_exists)


# -- kept names ---------------------------------------------------------------


def test_the_reported_features_and_dimensions_are_the_kept_ones():
    result = swbuild.build(FakeSolidWorks(), plan(), never_exists)
    assert result.features[:3] == ["Gear Axis", "Blank Sketch", "Blank"]
    assert result.dimensions["OD@Blank Sketch"] == "OD@Blank Sketch"
    assert result.dimensions["Width@Blank"] == "Width@Blank"
    assert result.dimensions["Count@Teeth"] == "Count@Teeth"


# -- pairs ---------------------------------------------------------------------


def _assembly_plan():
    from gear_generator.gears import base
    return BuildPlan("pair", "", (
        base.NewAssembly(""),
        base.AddGlobal("Centre Distance", "60"),
        base.AddComponent("gear1", r"C:\g\a.SLDPRT"),
        base.AddComponent("gear2", r"C:\g\b.SLDPRT", (60.0, 0.0, 0.0)),
        base.Fix("gear1"),
        base.Mate("dist", "distance", "gear2:Gear Axis", "gear1:plane3", 60.0, "Centre Distance"),
        base.LinkDimension("D1@Centre Distance", '"Centre Distance"'),
        base.Rebuild(),
        base.SaveAs(r"C:\g\Pair.SLDASM"),
    ), r"C:\g\Pair.SLDASM")


def test_a_pair_builds_both_parts_then_the_assembly_linking_the_kept_dimension():
    fake = FakeSolidWorks()
    result = swbuild.build_pair(fake, plan(path=r"C:\g\a.SLDPRT"), plan(path=r"C:\g\b.SLDPRT"),
                                _assembly_plan(), never_exists)
    assert result.ok, result.log_lines()
    assert names(fake).count("new_part") == 2 and names(fake).count("new_assembly") == 1
    link = [args for name, args in fake.calls if name == "link_dimension"][-1]
    assert link == ("D7@Centre Distance", '"Centre Distance"')


def test_a_clean_pair_is_checked_for_interference_after_the_assembly():
    fake = FakeSolidWorks()
    result = swbuild.build_pair(fake, plan(path=r"C:\g\a.SLDPRT"), plan(path=r"C:\g\b.SLDPRT"),
                                _assembly_plan(), never_exists)
    assert result.ok and names(fake)[-1] == "interference_count"
    assert "no interference between the gears" in result.assembly.done
    assert not result.assembly.checks


def test_interfering_teeth_are_a_check_not_a_failure():
    fake = FakeSolidWorks(interference=(3, 12.5))
    result = swbuild.build_pair(fake, plan(path=r"C:\g\a.SLDPRT"), plan(path=r"C:\g\b.SLDPRT"),
                                _assembly_plan(), never_exists)
    assert result.ok
    assert result.assembly.checks == ["the gears interfere in 3 places, 12.500 mm³; look along the gear axis at the mesh"]
    assert "CHECK   the gears interfere in 3 places, 12.500 mm³; look along the gear axis at the mesh" \
        in result.log_lines()


def test_an_interference_check_that_raises_is_reported_and_the_pair_still_stands():
    fake = FakeSolidWorks(fail_on={"interference_count": "no manager"})
    result = swbuild.build_pair(fake, plan(path=r"C:\g\a.SLDPRT"), plan(path=r"C:\g\b.SLDPRT"),
                                _assembly_plan(), never_exists)
    assert result.ok and result.assembly.checks == ["interference could not be checked: no manager"]


def test_a_pair_skips_the_assembly_when_a_part_fails():
    fake = FakeSolidWorks(fail_on={"circular_pattern": "no pattern"})
    result = swbuild.build_pair(fake, plan(path=r"C:\g\a.SLDPRT"), plan(path=r"C:\g\b.SLDPRT"),
                                _assembly_plan(), never_exists)
    assert not result.ok
    assert result.gear_b is None and result.assembly is None
    assert "new_assembly" not in names(fake) and "interference_count" not in names(fake)
    assert "SKIPPED" in result.log_lines()[-1]


# -- update values ---------------------------------------------------------------


def _built_fake(spec):
    fake = FakeSolidWorks()
    swbuild.build(fake, plan(spec), never_exists)
    fake.calls.clear()
    fake.active = DocInfo(title="Gear_m1.5_N25.SLDPRT", path=PATH, doc_type=1)
    return fake


def test_update_values_changes_only_what_differs_in_one_rebuild():
    spec = GearSpec()
    fake = _built_fake(spec)
    wanted = spec.with_values(teeth="40")
    variables = SPUR.variables(wanted, SPUR.derive(wanted))
    result = swbuild.update_variables(fake, variables, PATH.lower())
    assert result.ok and result.changed == ["No. of Teeth"]
    assert names(fake).count("rebuild") == 1
    assert names(fake).index("suppress") < names(fake).index("set_global_variable")
    assert fake.suppressed is False


def test_update_values_refuses_the_wrong_document():
    fake = _built_fake(GearSpec())
    fake.active = DocInfo(title="Other.SLDPRT", path=r"C:\Other.SLDPRT", doc_type=1)
    with pytest.raises(swbuild.BuildError, match="Other.SLDPRT"):
        swbuild.update_variables(fake, SPUR.variables(GearSpec(), SPUR.derive(GearSpec())), PATH)
    assert "set_global_variable" not in names(fake)


def test_update_values_refuses_a_part_without_the_globals():
    fake = FakeSolidWorks()
    fake.active = DocInfo(title="Gear.SLDPRT", path=PATH, doc_type=1)
    with pytest.raises(swbuild.BuildError, match="not in this part"):
        swbuild.update_variables(fake, SPUR.variables(GearSpec(), SPUR.derive(GearSpec())), PATH)


def test_nothing_to_change_means_no_rebuild():
    spec = GearSpec()
    fake = _built_fake(spec)
    result = swbuild.update_variables(fake, SPUR.variables(spec, SPUR.derive(spec)), PATH)
    assert result.changed == [] and "rebuild" not in names(fake)


@pytest.mark.parametrize("built,wanted,word", [
    ({"kind": "spur", "recipe": "A", "bore": "10"}, {"kind": "spur", "recipe": "B", "bore": "10"}, "recipe"),
    ({"kind": "spur", "recipe": "A", "bore": "10"}, {"kind": "spur", "recipe": "A", "bore": ""}, "bore"),
    ({"kind": "spur", "recipe": "A", "bore": ""}, {"kind": "spur", "recipe": "A", "bore": "0"}, ""),
    ({"kind": "spur", "recipe": "A", "bore": "8"}, {"kind": "spur", "recipe": "A", "bore": "12"}, ""),
])
def test_structural_changes_are_named(built, wanted, word):
    text = swbuild.structural_change(built, wanted)
    assert (word in text.lower()) if word else text == ""


def test_a_relation_that_already_holds_is_logged_as_such():
    result = swbuild.build(FakeSolidWorks(), plan(recipe="A"), never_exists)
    assert "ok      coincident L+.start I+.start (already one point)" in result.log_lines()


# -- W4 interfaces: an axis through planes made in the plan ---------------------------------


def _layout_like(axis_planes):
    from gear_generator.gears import base
    return BuildPlan("layout", "", (
        base.NewPart(""),
        base.RefPlane("x1", "S2 X Plane", 3, 63.75),
        base.Axis("axis1", "S2 Axis", axis_planes),
        base.Rebuild(),
        base.SaveAs(r"C:\g\R_Layout.SLDPRT"),
    ), r"C:\g\R_Layout.SLDPRT")


def test_an_axis_may_go_through_a_plane_made_earlier_by_its_id():
    assert _layout_like((2, "x1")).check() == []


def test_an_axis_through_a_plane_not_made_is_refused_with_a_sentence():
    problems = _layout_like((2, "x9")).check()
    assert "Axis 'axis1' is through 'x9', which is not a plane made earlier." in problems


def test_an_axis_is_described_by_plane_ids_and_tree_order_alike():
    from gear_generator.gears import base
    assert base.describe(base.Axis("a", "Gear Axis", (2, 3))) == "axis    'Gear Axis' through planes 2 and 3"
    assert base.describe(base.Axis("a", "S2 Axis", (2, "x1"))) == "axis    'S2 Axis' through plane 2 and x1"
    assert base.describe(base.Axis("a", "S2 Axis", ("y1", "x1"))) == "axis    'S2 Axis' through y1 and x1"


def test_the_runner_hands_the_axis_its_planes_as_planned():
    fake = FakeSolidWorks()
    result = swbuild.build(fake, _layout_like((2, "x1")), never_exists)
    assert result.ok, result.log_lines()
    assert ("insert_axis", ("axis1", "S2 Axis", (2, "x1"))) in fake.calls


def test_the_strips_own_axis_still_goes_through_planes_2_and_3():
    fake = FakeSolidWorks()
    swbuild.build(fake, plan(), never_exists)
    assert ("insert_axis", ("axis", "Gear Axis", (2, 3))) in fake.calls


# -- W4 interfaces: what an assembly kept, frames, same-named documents, progress ----------------


def test_an_assembly_build_records_the_name_each_component_kept():
    result = swbuild.build(FakeSolidWorks(), _assembly_plan(), never_exists)
    assert result.components == {"gear1": "gear1-1", "gear2": "gear2-1"}


IDENTITY = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)


def _turned(degrees, flipped=False):
    import math
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    rows = ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))
    if flipped:                                  # rot_x(180) · rot_z: a part on a Z- shaft
        rows = (rows[0], tuple(-v for v in rows[1]), tuple(-v for v in rows[2]))
    return tuple(v for row in rows for v in row)


@pytest.mark.parametrize("flipped", [False, True])
def test_a_gear_turned_whole_pitches_is_the_same_placement(flipped):
    at = (63.75, 0.0, 5.0)
    pitch = 360.0 / 68
    assert swbuild.same_frame(_turned(10, flipped), at, _turned(10 + 3 * pitch, flipped), at, pitch)
    assert swbuild.same_frame(_turned(10, flipped), at, _turned(10 - pitch, flipped), at, pitch)
    assert not swbuild.same_frame(_turned(10, flipped), at, _turned(10 + pitch / 2, flipped), at, pitch)
    assert not swbuild.same_frame(_turned(10, flipped), at, _turned(10 + pitch, flipped), at)   # no pitch: exact


def test_a_frame_moved_or_tipped_is_not_the_same_placement():
    assert swbuild.same_frame(IDENTITY, (0.0, 0.0, 0.0), IDENTITY, (0.0, 0.0, 5e-7))
    assert not swbuild.same_frame(IDENTITY, (0.0, 0.0, 0.0), IDENTITY, (0.0, 2e-6, 0.0))
    assert not swbuild.same_frame(_turned(0), (0, 0, 0), _turned(0, flipped=True), (0, 0, 0), 360.0 / 17)


def test_a_document_of_the_same_name_open_from_another_folder_is_found():
    docs = [DocInfo("Gear_m1.5_N17.SLDPRT", r"C:\Other\Gear_m1.5_N17.SLDPRT", 1),
            DocInfo("Gear_m1.5_N68.SLDPRT", r"C:\Parts\R\Gear_m1.5_N68.SLDPRT", 1),
            DocInfo("Part1", "", 1)]
    wanted = [r"C:\Parts\R\gear_m1.5_n17.SLDPRT", r"c:\parts\r\Gear_m1.5_N68.SLDPRT"]
    assert swbuild.same_named_elsewhere(docs, wanted) == [(docs[0].path, wanted[0])]


def test_progress_is_one_step_per_job_never_a_shared_default():
    first, second = swbuild.Progress(), swbuild.Progress()
    first.say(swbuild.Step(swbuild.STAGE_PART, "Gear_m1.5_N68", 2, 4))
    assert first.step == swbuild.Step("part", "Gear_m1.5_N68", 2, 4) and second.step is None


def test_the_fake_reopens_a_saved_document_holding_what_it_was_saved_with():
    fake = FakeSolidWorks()
    swbuild.build(fake, plan(), never_exists)
    swbuild.build(fake, _layout_like((2, "x1")), never_exists)
    fake.open_document(PATH)
    assert swbuild.planned_changes(fake.equations(), SPUR.variables(GearSpec(), SPUR.derive(GearSpec())),
                                   DEGREES) == []
    assert fake.active.path == PATH and "Gear_m1.5_N25.SLDPRT" in [d.title for d in fake.documents()]
    fake.open_document(r"C:\g\R_Layout.SLDPRT")
    assert fake.feature_names() == ["S2 X Plane", "S2 Axis"]


# -- W4: build_gearbox ----------------------------------------------------------------------------


from gear_generator import findings  # noqa: E402
from gear_generator.gears import base as ops  # noqa: E402
from gear_generator.gears.base import GlobalVariable  # noqa: E402

W = "C:\\W\\"
P17, P68, P68B = W + "Gear_m1.5_N17.SLDPRT", W + "Gear_m1.5_N68.SLDPRT", W + "Gear_m1.5_N68_r2.SLDPRT"
LAYOUT, ASM = W + "R_Layout.SLDPRT", W + "R.SLDASM"
S17, S68 = GearSpec().with_values(teeth="17"), GearSpec().with_values(teeth="68")
AT2 = (63.75, 0.0, 0.0)
TURNED2 = _turned(180.0 / 68)


def _layout_plan(path=LAYOUT):
    return BuildPlan("layout", "", (
        ops.NewPart(""),
        ops.AddGlobal("S2 X", "63.75"),
        ops.RefPlane("x1", "S2 X Plane", 3, 63.75),
        ops.Axis("axis1", "S1 Axis", (2, 3)),
        ops.Axis("axis2", "S2 Axis", (2, "x1")),
        ops.Rebuild(),
        ops.SaveAs(path),
    ), path)


LAYOUT_VALUES = (GlobalVariable("S2 X", "63.75"),)
LAYOUT_FEATURES = ("S2 X Plane", "S1 Axis", "S2 Axis")


def _gearbox_assembly(parts=(P17, P68), layout=LAYOUT, path=ASM):
    steps = [ops.NewAssembly(""), ops.AddComponent("layout", layout), ops.Place("layout", IDENTITY, (0.0, 0.0, 0.0)),
             ops.Fix("layout")]
    frames = [(IDENTITY, (0.0, 0.0, 0.0)), (TURNED2, AT2)]
    for index, part in enumerate(parts, 1):
        rotation, at = frames[(index - 1) % 2]
        steps += [ops.AddComponent(f"gear{index}", part, at), ops.Place(f"gear{index}", rotation, at),
                  ops.Fix(f"gear{index}")]
    return BuildPlan("gearbox", "", tuple(steps) + (ops.Rebuild(), ops.SaveAs(path)), path)


def _values(spec):
    return tuple(SPUR.variables(spec, SPUR.derive(spec)))


def _record_steps():
    steps = []
    return steps, steps.append


GEARS = {"gear1": "G1", "gear2": "G2"}


def _build(fake=None, **kwargs):
    fake = fake or FakeSolidWorks()
    kwargs.setdefault("parts", [plan(S17, path=P17), plan(S68, path=P68)])
    kwargs.setdefault("layout", _layout_plan())
    kwargs.setdefault("assembly", _gearbox_assembly())
    kwargs.setdefault("gears", GEARS)
    kwargs.setdefault("exists", fake.exists)
    return fake, swbuild.build_gearbox(fake, **kwargs)


def _saved_part(fake, spec, path):
    """A part as an earlier build left it: built and saved, so the fake reopens it holding its globals."""
    swbuild.build(fake, plan(spec, path=path), fake.exists)
    fake.calls.clear()


def test_a_gearbox_builds_parts_then_layout_then_assembly_then_checks_interference():
    fake, result = _build()
    assert result.ok, result.log_lines()
    order = [n for n in names(fake) if n in ("new_part", "new_assembly", "interferences")]
    assert order == ["new_part", "new_part", "new_part", "new_assembly", "interferences"]
    assert [r.saved for r in result.parts.built] == [P17, P68]
    assert result.layout.saved == LAYOUT and result.assembly.saved == ASM
    assert result.components == {"layout": "layout-1", "gear1": "gear1-1", "gear2": "gear2-1"}
    lines = result.log_lines()
    assert lines[-1] == "ok      no interference between the gears"
    assert "open_document" not in names(fake) and "close_document" not in names(fake)


def test_the_progress_steps_come_in_the_pinned_order_with_stems_not_paths():
    fake = FakeSolidWorks()
    _saved_part(fake, S17, P17)
    steps, say = _record_steps()
    _build(fake, parts=[plan(S68, path=P68)], reuse=[swbuild.DocumentValues(P17, _values(S17))], progress=say)
    assert steps == [swbuild.Step("check", "Gear_m1.5_N17", 1, 1), swbuild.Step("part", "Gear_m1.5_N68", 1, 1),
                     swbuild.Step("layout", "R_Layout"), swbuild.Step("assembly", "R"),
                     swbuild.Step("interference", "R")]


def test_a_progress_object_records_the_last_step_of_its_own_job():
    progress = swbuild.Progress()
    _build(progress=progress.say)
    assert progress.step == swbuild.Step("interference", "R")


@pytest.mark.parametrize("case,sentence", [
    ("new path exists", r"C:\W\Gear_m1.5_N68.SLDPRT already exists, and a build never overwrites a file."),
    ("two new paths", r"C:\W\Gear_m1.5_N17.SLDPRT is named twice in this job, so one document would take the "
                      "place of the other."),
    ("reused missing", r"C:\W\Old.SLDPRT is no longer there, so it cannot be reused: it was moved, renamed or "
                       "deleted since it was built."),
    ("same name, two folders", r"C:\W\Gear_m1.5_N17.SLDPRT and C:\Other\Gear_m1.5_N17.SLDPRT have the same file "
                               "name, and SolidWorks keeps one document per file name, so they cannot both be in "
                               "one job."),
    ("open elsewhere", r"C:\Other\Gear_m1.5_N68.SLDPRT is open in SolidWorks, and it has the same file name as "
                       r"C:\W\Gear_m1.5_N68.SLDPRT, which this job would make; SolidWorks keeps one document per "
                       "file name, so close Gear_m1.5_N68.SLDPRT in SolidWorks and try again."),
    ("assembly without layout", "The assembly is built around its layout part, and this build has neither a "
                                "layout part to make nor one to reuse."),
    ("stray insert", r"The assembly would insert C:\W\Stray.SLDPRT, which this build neither makes nor reuses."),
    ("unsound plan", "The build plan for R_Layout.SLDPRT is not sound: Axis 'axis2' is through 'x9', which is not "
                     "a plane made earlier."),
])
def test_every_preflight_refusal_is_a_sentence_and_nothing_is_touched(case, sentence):
    fake = FakeSolidWorks()
    kwargs = {}
    if case == "new path exists":
        fake.saved[_key(P68)] = ([], [])
    elif case == "two new paths":
        kwargs["parts"] = [plan(S17, path=P17), plan(S68, path=P17)]
    elif case == "reused missing":
        kwargs["reuse"] = [swbuild.DocumentValues(W + "Old.SLDPRT", ())]
    elif case == "same name, two folders":
        fake.saved[_key(r"C:\Other\Gear_m1.5_N17.SLDPRT")] = ([], [])
        kwargs["reuse"] = [swbuild.DocumentValues(r"C:\Other\Gear_m1.5_N17.SLDPRT", ())]
    elif case == "open elsewhere":
        fake.open_docs = [DocInfo("Gear_m1.5_N68.SLDPRT", r"C:\Other\Gear_m1.5_N68.SLDPRT", 1)]
    elif case == "assembly without layout":
        kwargs["layout"] = None
    elif case == "stray insert":
        kwargs["assembly"] = _gearbox_assembly(parts=(P17, W + "Stray.SLDPRT"))
    elif case == "unsound plan":
        broken = _layout_plan()
        kwargs["layout"] = BuildPlan("layout", "", tuple(
            ops.Axis("axis2", "S2 Axis", (2, "x9")) if isinstance(op, ops.Axis) and op.id == "axis2" else op
            for op in broken.ops), LAYOUT)
    with pytest.raises(swbuild.BuildError) as raised:
        _build(fake, **kwargs)
    assert str(raised.value) == sentence
    assert fake.calls == []


def test_a_reused_part_that_holds_other_values_is_named_and_nothing_is_made():
    """W4 review B2's last corner: not a refusal any more but a result naming the part, with its file's time, so
    the finish records it and the next plan makes the part new rather than fail this check on every press."""
    fake = FakeSolidWorks()
    _saved_part(fake, S68.with_values(teeth="69"), P68)
    _, result = _build(fake, parts=[plan(S17, path=P17)], reuse=[swbuild.DocumentValues(P68, _values(S68))],
                       mtime=lambda path: 1234.5)
    ((path, why),) = result.mismatched
    assert path == P68 and why.startswith("Gear_m1.5_N68.SLDPRT does not hold what the workbook asks of it, so it "
                                          'cannot be reused: "No. of Teeth" is 69 there and 68 here')
    assert result.mtimes == {P68: 1234.5} and not result.ok and result.checked == []
    assert "new_part" not in names(fake) and "save_as" not in names(fake)
    assert "set_global_variable" not in names(fake)
    assert f"FAIL    checked Gear_m1.5_N68.SLDPRT: {why}" in result.log_lines()


def test_a_reused_part_missing_a_global_is_named_with_the_global_in_the_sentence():
    fake = FakeSolidWorks()
    fake.saved[_key(P68)] = (['"Module"= 1.5'], [])
    _saved_part(fake, S17, P17)
    _, result = _build(fake, parts=[], reuse=[swbuild.DocumentValues(P68, _values(S68)),
                                             swbuild.DocumentValues(P17, _values(S17))])
    ((path, why),) = result.mismatched
    assert path == P68 and why.startswith('Gear_m1.5_N68.SLDPRT cannot be reused: "')
    assert "is not in this part, so it was not built by this tool or its equations were edited." in why
    assert result.checked == [P17]                          # every document is still checked, so one press finds all
    assert "new_part" not in names(fake)


def test_a_reused_layout_that_lost_a_plane_is_named():
    fake = FakeSolidWorks()
    fake.saved[_key(LAYOUT)] = (['"S2 X"= 63.75'], ["S1 Axis", "S2 Axis"])
    for path, spec in ((P17, S17), (P68, S68)):
        _saved_part(fake, spec, path)
    _, result = _build(fake, parts=[], reuse=[swbuild.DocumentValues(P17, _values(S17)),
                                              swbuild.DocumentValues(P68, _values(S68))],
                       layout=swbuild.DocumentValues(LAYOUT, LAYOUT_VALUES, LAYOUT_FEATURES))
    assert result.mismatched == [(LAYOUT, 'R_Layout.SLDPRT cannot be reused: "S2 X Plane" is no longer in it; it was '
                                          "renamed or deleted in SolidWorks.")]
    assert "new_assembly" not in names(fake) and result.layout_reused == ""


def test_a_reused_document_solidworks_will_not_open_is_refused_with_its_sentence():
    fake = FakeSolidWorks(fail_on={"open_document": r"SolidWorks would not open C:\W\Gear_m1.5_N68.SLDPRT (error 2)."})
    _saved_part(fake, S68, P68)
    with pytest.raises(swbuild.BuildError, match=r"would not open C:\\W\\Gear_m1.5_N68.SLDPRT \(error 2\)\."):
        _build(fake, parts=[plan(S17, path=P17)], reuse=[swbuild.DocumentValues(P68, _values(S68))])
    assert "new_part" not in names(fake)


def test_reused_parts_and_layout_are_opened_and_checked_before_anything_is_built_and_inserted_after():
    fake = FakeSolidWorks()
    for path, spec in ((P17, S17), (P68, S68)):
        _saved_part(fake, spec, path)
    swbuild.build(fake, _layout_plan(), fake.exists)
    fake.calls.clear()
    _, result = _build(fake, parts=[], reuse=[swbuild.DocumentValues(P17, _values(S17)),
                                              swbuild.DocumentValues(P68, _values(S68))],
                       layout=swbuild.DocumentValues(LAYOUT, LAYOUT_VALUES, LAYOUT_FEATURES))
    assert result.ok, result.log_lines()
    assert result.checked == [P17, P68, LAYOUT] and result.layout_reused == LAYOUT and result.layout is None
    called = names(fake)
    assert called.count("open_document") == 3 and called.index("new_assembly") > max(
        i for i, n in enumerate(called) if n == "open_document")
    assert called.count("new_part") == 0 and "set_global_variable" not in called
    assert not result.parts.ok          # an empty batch, as pinned; the gearbox is still ok
    assert "ok      layout R_Layout.SLDPRT reused" in result.log_lines()
    assert "ok      checked Gear_m1.5_N17.SLDPRT: it holds what the workbook asks, so it is reused" in result.log_lines()


@pytest.mark.parametrize("route,ok", [("opened", True), ("closed", True), (None, False), ("neither", False)])
def test_inserting_reused_parts_follows_the_reuse_route(monkeypatch, route, ok):
    monkeypatch.setattr(findings, "REUSE_ADD_ROUTE", route, raising=False)
    fake = FakeSolidWorks()
    _saved_part(fake, S17, P17)
    if ok:
        _, result = _build(fake, parts=[plan(S68, path=P68)], reuse=[swbuild.DocumentValues(P17, _values(S17))])
        assert result.ok and "open_document" in names(fake)      # "closed" is opened anyway, by the live check
        return
    with pytest.raises(swbuild.BuildError) as raised:
        _build(fake, parts=[plan(S68, path=P68)], reuse=[swbuild.DocumentValues(P17, _values(S17))])
    assert str(raised.value) == ("Putting a document built earlier into a new assembly has not been settled on "
                                 f"SolidWorks yet (findings.REUSE_ADD_ROUTE is {route!r}), so this build, which "
                                 "reuses Gear_m1.5_N17.SLDPRT, cannot start; run probe tier 7 first.")
    assert fake.calls == []


def test_a_reused_part_needs_no_reuse_route_when_no_assembly_is_built(monkeypatch):
    monkeypatch.setattr(findings, "REUSE_ADD_ROUTE", None, raising=False)
    fake = FakeSolidWorks()
    _saved_part(fake, S17, P17)
    _, result = _build(fake, parts=[plan(S68, path=P68)], reuse=[swbuild.DocumentValues(P17, _values(S17))],
                       layout=None, assembly=None)
    assert result.ok and result.checked == [P17]


def test_a_part_that_fails_skips_the_layout_and_the_assembly():
    fake = FakeSolidWorks(fail_on={"circular_pattern": "FeatureCircularPattern5 would not pattern the cut."})
    _, result = _build(fake)
    assert not result.ok
    assert len(result.parts.built) == 1 and result.parts.skipped == [P68]
    assert result.layout is None and result.assembly is None
    assert result.skipped == "the layout part and the assembly, because a part failed"
    assert result.log_lines()[-1] == "SKIPPED the layout part and the assembly, because a part failed"
    assert names(fake).count("new_part") == 1 and "new_assembly" not in names(fake)


def test_a_layout_that_fails_keeps_the_parts_and_skips_the_assembly():
    fake = FakeSolidWorks(fail_on={"insert_axis": ("S2 Axis", "InsertAxis2 would not make S2 Axis.")})
    _, result = _build(fake)
    assert not result.ok and [r.saved for r in result.parts.built] == [P17, P68]
    assert result.layout is not None and not result.layout.ok and not result.layout.saved
    assert result.assembly is None and result.skipped == "the assembly, because the layout part failed"
    assert "new_assembly" not in names(fake)


def test_an_assembly_that_fails_keeps_the_parts_and_the_layout_and_checks_no_interference():
    fake = FakeSolidWorks(fail_on={"place_component": ("gear2", "gear2-1 did not take its frame.")})
    _, result = _build(fake)
    assert not result.ok
    assert [r.saved for r in result.parts.built] == [P17, P68] and result.layout.saved == LAYOUT
    assert not result.assembly.ok and not result.assembly.saved and result.skipped == ""
    assert "interferences" not in names(fake) and result.clashes == []
    assert not any("interference" in line for line in result.log_lines())


def test_an_assembly_that_cannot_even_be_made_keeps_the_parts_and_the_layout_on_the_result():
    """SolidWorks 2026, probe/workbook_assembly_check.py 2026-11-13: an assembly template that was not there
    raised out of build_gearbox after the parts and the layout had saved, so nothing reached the record."""
    fake = FakeSolidWorks(fail_on={"new_assembly": "There is no assembly template at 'C:\\T\\No.asmdot'."})
    _, result = _build(fake)
    assert not result.ok and [r.saved for r in result.parts.built] == [P17, P68] and result.layout.saved == LAYOUT
    assembly = result.assembly
    assert assembly is not None and not assembly.saved and assembly.document == ""
    assert assembly.failures == [("new assembly", "There is no assembly template at 'C:\\T\\No.asmdot'.")]
    assert "FAIL    new assembly: There is no assembly template at 'C:\\T\\No.asmdot'." in result.log_lines()
    assert "interferences" not in names(fake)
    assert "FAIL    the rebuild reported an error" not in assembly.log_lines()   # nothing was made to rebuild


def test_a_later_part_that_cannot_be_made_keeps_the_parts_before_it():
    fake = FakeSolidWorks()
    calls = {"n": 0}
    real = fake.new_part

    def second_fails(template=""):
        calls["n"] += 1
        if calls["n"] == 2:
            raise swbuild.SolidWorksError("SolidWorks would not make a new part from C:\\T\\Part.prtdot.")
        return real(template)
    fake.new_part = second_fails
    _, result = _build(fake)
    assert [r.saved for r in result.parts.built] == [P17, ""] and result.parts.built[1].failures[0][0] == "new part"
    assert result.skipped == "the layout part and the assembly, because a part failed"


def test_a_layout_that_cannot_be_made_is_a_failed_layout():
    fake = FakeSolidWorks()
    calls = {"n": 0}
    real = fake.new_part

    def third_fails(template=""):
        calls["n"] += 1
        if calls["n"] == 3:
            raise swbuild.SolidWorksError("There is no part template at 'C:\\T\\No.prtdot'.")
        return real(template)
    fake.new_part = third_fails
    _, result = _build(fake)
    assert result.layout is not None and result.layout.failures[0][0] == "new part" and not result.layout.saved
    assert result.skipped == "the assembly, because the layout part failed"


def test_a_clash_names_the_gears_and_leaves_the_build_ok():
    fake = FakeSolidWorks(clashes=[(("gear1-1", "gear2-1"), 12.3454), ((), 1.5), (("layout-1", "gear2-1"), 0.25)])
    _, result = _build(fake)
    assert result.ok
    assert result.clashes[0] == swbuild.Clash(("gear1-1", "gear2-1"), ("G1", "G2"), 12.3454)
    assert result.clashes[2].gears == ("layout-1", "G2")
    lines = result.log_lines()
    assert "CHECK   G1 and G2 interfere, 12.345 mm³; look where they meet" in lines
    assert ("CHECK   an interference of 1.500 mm³ between components SolidWorks did not name; look at each mesh"
            in lines)
    assert "ok      no interference between the gears" not in lines


def test_an_interference_check_that_raises_is_kept_and_the_build_still_stands():
    fake = FakeSolidWorks(fail_on={"interferences": "Assem1 has no interference detection manager."})
    _, result = _build(fake)
    assert result.ok and result.interference_error == "Assem1 has no interference detection manager."
    assert "CHECK   interference could not be checked: Assem1 has no interference detection manager." \
        in result.log_lines()


def test_build_parts_alone_makes_no_layout_and_no_assembly():
    fake, result = _build(layout=None, assembly=None)
    assert result.ok and result.layout is None and result.assembly is None and result.skipped == ""
    assert "new_assembly" not in names(fake) and "interferences" not in names(fake)


def test_a_gearbox_build_refuses_an_old_solidworks():
    fake = FakeSolidWorks()
    fake.revision = (31, 0, 0)
    with pytest.raises(swbuild.BuildError, match="2024"):
        _build(fake)


# -- W4: update_gearbox ---------------------------------------------------------------------------


def _built_gearbox(**fake_kwargs):
    """A fake SolidWorks after a clean gearbox build: every file saved, the gears where the build put them."""
    fake, result = _build(FakeSolidWorks(**fake_kwargs))
    assert result.ok, result.log_lines()
    fake.calls.clear()
    fake.frames = {"layout-1": (IDENTITY, (0.0, 0.0, 0.0)), "gear1-1": (IDENTITY, (0.0, 0.0, 0.0)),
                   "gear2-1": (TURNED2, AT2)}
    return fake


def _placements(g2=(TURNED2, AT2), teeth2=68):
    return [swbuild.Placement("G1", "gear1-1", IDENTITY, (0.0, 0.0, 0.0), 360.0 / 17),
            swbuild.Placement("G2", "gear2-1", g2[0], g2[1], 360.0 / teeth2)]


S69 = S68.with_values(teeth="69")
MOVED2 = (_turned(0.0), (64.5, 0.0, 0.0))


def _update(fake, **kwargs):
    kwargs.setdefault("parts", [swbuild.DocumentValues(P17, _values(S17)), swbuild.DocumentValues(P68, _values(S69))])
    kwargs.setdefault("layout", swbuild.DocumentValues(LAYOUT, (GlobalVariable("S2 X", "64.5"),), LAYOUT_FEATURES))
    kwargs.setdefault("assembly", ASM)
    kwargs.setdefault("placements", _placements(MOVED2, 69))
    kwargs.setdefault("exists", fake.exists)
    return swbuild.update_gearbox(fake, **kwargs)


def _after_last_open(fake, path):
    called = fake.calls
    start = max(i for i, (n, a) in enumerate(called) if n == "open_document" and a == (path,))
    return [n for n, _ in called[start:]]


def test_update_sets_values_then_re_places_only_what_differs_and_rebuilds_the_assembly_once():
    fake = _built_gearbox()
    result = _update(fake)
    assert result.ok, result.log_lines()
    sets = [a for n, a in fake.calls if n == "set_global_variable"]
    assert ("No. of Teeth", "69") in sets and ("S2 X", "64.5") in sets
    assert [r.changed for r in result.parts] == [[], ["No. of Teeth"]] and result.layout.changed == ["S2 X"]
    assert result.placed == ["G2"] and [a for n, a in fake.calls if n == "place_component"] == [("placed2",)]
    assert result.found == {"G1": (IDENTITY, (0.0, 0.0, 0.0)), "G2": (TURNED2, AT2)}
    assert _after_last_open(fake, ASM).count("rebuild") == 1 and result.rebuilt
    assert result.changed == [P68, LAYOUT, ASM]
    assert "save_as" not in names(fake) and "close_document" not in names(fake)
    assert fake.frames["gear2-1"] == MOVED2
    lines = result.log_lines()
    assert "ok      re-placed G2" in lines and "ok      no interference between the gears" in lines
    assert lines[-1] == ("not saved: Gear_m1.5_N68.SLDPRT, R_Layout.SLDPRT, R.SLDASM changed in SolidWorks; save "
                         "there to keep it")


def test_update_steps_check_every_document_then_values_then_place_then_interference():
    fake = _built_gearbox()
    steps, say = _record_steps()
    _update(fake, progress=say)
    assert steps == [swbuild.Step("check", "Gear_m1.5_N17", 1, 4), swbuild.Step("check", "Gear_m1.5_N68", 2, 4),
                     swbuild.Step("check", "R_Layout", 3, 4), swbuild.Step("check", "R", 4, 4),
                     swbuild.Step("values", "Gear_m1.5_N68"),     # N17 holds its values already: not touched
                     swbuild.Step("values", "R_Layout"), swbuild.Step("place", "R"),
                     swbuild.Step("interference", "R")]


def test_a_gear_turned_whole_pitches_is_left_where_it_is():
    fake = _built_gearbox()
    fake.frames["gear2-1"] = (_turned(180.0 / 68 + 5 * 360.0 / 68), AT2)
    result = _update(fake, parts=[], layout=None, placements=_placements())
    assert result.ok and result.placed == [] and "place_component" not in names(fake)
    # nothing changed and nothing moved: the assembly is only read, not rebuilt (W4 review S2)
    assert result.changed == [] and not result.rebuilt and "rebuild" not in names(fake)
    assert "interferences" not in names(fake)
    assert "ok      every gear is where the workbook puts it" in result.log_lines()
    assert result.log_lines()[-1] == "nothing changed in SolidWorks"


def test_a_gear_dragged_in_solidworks_is_found_where_it_was_and_put_back():
    fake = _built_gearbox()
    fake.frames["gear1-1"] = (_turned(7.0), (1.0, 2.0, 0.0))
    result = _update(fake, parts=[], layout=None, placements=_placements())
    assert result.placed == ["G1"] and result.found["G1"] == (_turned(7.0), (1.0, 2.0, 0.0))
    assert fake.frames["gear1-1"] == (IDENTITY, (0.0, 0.0, 0.0))


@pytest.mark.parametrize("case,sentence", [
    ("missing path", r"C:\W\Gear_m1.5_N68.SLDPRT is no longer there, so Update SolidWorks cannot change it: it was "
                     "moved, renamed or deleted since it was built."),
    ("missing global", 'R_Layout.SLDPRT cannot be updated: "S3 X" is not in this part, so it was not built by this '
                       "tool or its equations were edited."),
    ("lost plane", 'R_Layout.SLDPRT cannot be updated: "S2 X Plane" is no longer in it; it was renamed or deleted '
                   "in SolidWorks."),
    ("missing component", "gear2-1 is not in R.SLDASM any more: it was renamed or deleted in SolidWorks."),
    ("does not evaluate", "Gear_m1.5_N68.SLDPRT cannot be updated: the new values do not evaluate: "),
    ("open elsewhere", r"C:\Old\R.SLDASM is open in SolidWorks, and it has the same file name as C:\W\R.SLDASM, "
                       "which this job would change; SolidWorks keeps one document per file name, so close R.SLDASM "
                       "in SolidWorks and try again."),
    ("no assembly", "Gears can only be re-placed in an assembly, and Update SolidWorks was given none."),
    ("one component twice", "gear2-1 is recorded for both G1 and G2, so one of them would be placed twice."),
])
def test_every_check_refusal_changes_nothing(case, sentence):
    fake = _built_gearbox()
    kwargs = {}
    if case == "missing path":
        del fake.saved[_key(P68)]
    elif case == "missing global":
        kwargs["layout"] = swbuild.DocumentValues(LAYOUT, (GlobalVariable("S2 X", "64.5"),
                                                           GlobalVariable("S3 X", "132.5")), LAYOUT_FEATURES)
    elif case == "lost plane":
        fake.memory[_key(LAYOUT)][1].remove("S2 X Plane")            # deleted in SolidWorks, the layout still open
    elif case == "missing component":
        fake.missing_components = {"gear2-1"}
    elif case == "does not evaluate":
        kwargs["parts"] = [swbuild.DocumentValues(P68, (GlobalVariable("No. of Teeth", '"Nowhere" * 2'),))]
    elif case == "open elsewhere":
        fake.open_docs = [DocInfo("R.SLDASM", r"C:\Old\R.SLDASM", 2)]
    elif case == "no assembly":
        kwargs["assembly"] = ""
    elif case == "one component twice":
        kwargs["placements"] = [swbuild.Placement("G1", "gear2-1", IDENTITY, (0.0, 0.0, 0.0)),
                                swbuild.Placement("G2", "gear2-1", IDENTITY, (0.0, 0.0, 0.0))]
    with pytest.raises(swbuild.BuildError) as raised:
        _update(fake, **kwargs)
    assert str(raised.value).startswith(sentence) if case == "does not evaluate" else str(raised.value) == sentence
    called = names(fake)
    assert "set_global_variable" not in called and "place_component" not in called and "rebuild" not in called
    assert "save_as" not in called
    # What only a new revision gets past (W4 review S4.6) is told apart by its type, naming the document.
    not_as_built = {"missing global": LAYOUT, "lost plane": LAYOUT, "missing component": ASM}
    assert isinstance(raised.value, swbuild.NotAsBuilt) == (case in not_as_built)
    if case in not_as_built:
        assert raised.value.path == not_as_built[case]


@pytest.mark.parametrize("route", [None, "something else"])
def test_re_placing_without_a_settled_route_is_refused_before_anything_changes(monkeypatch, route):
    monkeypatch.setattr(findings, "REPLACE_FIXED_ROUTE", route, raising=False)
    fake = _built_gearbox()
    with pytest.raises(swbuild.BuildError) as raised:
        _update(fake)
    assert str(raised.value) == ("Moving a fixed component has not been settled on SolidWorks yet "
                                 f"(findings.REPLACE_FIXED_ROUTE is {route!r}), so Update SolidWorks cannot re-place "
                                 "the gears; run probe tier 7 first.")
    assert fake.calls == []


def test_values_alone_need_no_re_placing_route(monkeypatch):
    monkeypatch.setattr(findings, "REPLACE_FIXED_ROUTE", None, raising=False)
    fake = _built_gearbox()
    result = _update(fake, layout=None, assembly="", placements=[])
    assert result.ok and result.changed == [P68]


def test_the_unfix_route_unfixes_places_and_fixes_each_moved_gear(monkeypatch):
    monkeypatch.setattr(findings, "REPLACE_FIXED_ROUTE", "UnfixComponent, Transform2 put, FixComponent",
                        raising=False)
    fake = _built_gearbox()
    result = _update(fake)
    assert result.ok
    moves = [(n, a) for n, a in fake.calls if n in ("unfix_component", "place_component", "fix_component")]
    assert moves == [("unfix_component", ("placed2",)), ("place_component", ("placed2",)),
                     ("fix_component", ("placed2",))]


def test_the_transform_route_places_a_fixed_gear_without_unfixing_it():
    assert findings.REPLACE_FIXED_ROUTE == "Transform2 put"
    fake = _built_gearbox()
    _update(fake)
    assert "unfix_component" not in names(fake) and "fix_component" not in names(fake)


def test_re_placing_restores_the_rebuild_flag_before_the_one_rebuild():
    fake = _built_gearbox()
    _update(fake)
    tail = [(n, a) for n, a in fake.calls[[n for n, _ in fake.calls].index("place_component") - 1:]]
    assert tail[0] == ("suppress", (True,)) and ("suppress", (False,)) in tail
    assert tail.index(("suppress", (False,))) < tail.index(("rebuild", (False,)))
    assert fake.suppressed is False


def test_a_part_that_fails_stops_the_update_and_says_what_changed_and_what_was_left():
    fake = _built_gearbox(fail_on={"set_global_variable": ("No. of Teeth", "\"No. of Teeth\" reads '68'.")})
    result = _update(fake, parts=[swbuild.DocumentValues(P17, _values(S17.with_values(teeth="18"))),
                                  swbuild.DocumentValues(P68, _values(S69))])
    assert not result.ok and len(result.parts) == 1 and result.layout is None
    assert result.failures[0][0] == 'Gear_m1.5_N17.SLDPRT "No. of Teeth"'
    assert result.skipped == "1 more part, the layout part and the assembly, because Gear_m1.5_N17.SLDPRT failed"
    assert "place_component" not in names(fake) and "open_document" not in _after_last_open(fake, P17)[1:]
    assert result.log_lines()[-1].startswith("SKIPPED 1 more part")


def test_a_layout_that_fails_stops_before_the_assembly():
    fake = _built_gearbox(fail_on={"set_global_variable": ("S2 X", '"S2 X" reads 63.75.')})
    result = _update(fake)
    assert not result.ok and result.changed == [P68] and result.layout is not None
    assert result.skipped == "the assembly, because R_Layout.SLDPRT failed"
    assert "place_component" not in names(fake)


def test_a_failed_assembly_rebuild_is_a_failure_and_no_interference_is_checked():
    fake = _built_gearbox()
    fake.rebuild_ok = False
    result = _update(fake, parts=[], layout=None)          # G2 is re-placed, so the assembly is rebuilt
    assert not result.ok and result.failures == [("R.SLDASM", "SolidWorks reported an error rebuilding R.")]
    assert "interferences" not in names(fake)


def test_an_update_clash_names_the_gears_from_the_placements():
    fake = _built_gearbox(clashes=[(("gear1-1", "gear2-1"), 3.0)])
    result = _update(fake)
    assert result.ok and result.clashes == [swbuild.Clash(("gear1-1", "gear2-1"), ("G1", "G2"), 3.0)]
    assert "CHECK   G1 and G2 interfere, 3.000 mm³; look where they meet" in result.log_lines()


def test_with_parts_not_settled_beside_their_assembly_an_open_assembly_must_be_closed_first(monkeypatch):
    monkeypatch.setattr(findings, "OPEN_PART_BESIDE_ASSEMBLY", False, raising=False)
    fake = _built_gearbox()
    fake.open_docs = [DocInfo("R.SLDASM", ASM, 2)]
    with pytest.raises(swbuild.BuildError) as raised:
        _update(fake)
    assert str(raised.value) == ("Close R.SLDASM in SolidWorks, then press Update SolidWorks again: changing a part "
                                 "while its assembly is open has not been settled on this SolidWorks "
                                 "(findings.OPEN_PART_BESIDE_ASSEMBLY).")
    assert fake.calls == []


@pytest.mark.parametrize("beside", [False, None])
def test_with_parts_not_settled_beside_their_assembly_the_assembly_opens_after_the_values(monkeypatch, beside):
    monkeypatch.setattr(findings, "OPEN_PART_BESIDE_ASSEMBLY", beside, raising=False)
    fake = _built_gearbox()
    fake.close_all()                       # the assembly is not open: Update may go ahead, values first
    fake.missing_components = {"gear2-1"}
    result = _update(fake)
    called = names(fake)
    assert called.index("open_document") < called.index("set_global_variable")
    first_asm = next(i for i, (n, a) in enumerate(fake.calls) if n == "open_document" and a == (ASM,))
    assert first_asm > max(i for i, n in enumerate(called) if n == "set_global_variable")
    assert not result.ok and result.failures[0] == (
        "R.SLDASM", "gear2-1 is not in R.SLDASM any more: it was renamed or deleted in SolidWorks.")
    assert result.changed == [P68, LAYOUT]


def test_an_update_with_nothing_given_changes_nothing():
    fake = FakeSolidWorks()
    result = swbuild.update_gearbox(fake, exists=fake.exists)
    assert result.ok and fake.calls == [] and result.log_lines() == ["nothing changed in SolidWorks"]


def test_an_update_refuses_an_old_solidworks():
    fake = FakeSolidWorks()
    fake.revision = (31, 0, 0)
    with pytest.raises(swbuild.BuildError, match="2024"):
        swbuild.update_gearbox(fake, exists=fake.exists)


# -- W4: what the first run on SolidWorks 2026 found (probe/gearbox_smoke.py, 2026-11-13) -----------------


@pytest.mark.parametrize("trig", [DEGREES, RADIANS])
def test_the_reuse_check_writes_nothing_and_reads_the_trig_units_from_the_text(trig):
    fake = FakeSolidWorks(trig=trig)
    _saved_part(fake, S17, P17)
    _, result = _build(fake, parts=[plan(S68, path=P68)], reuse=[swbuild.DocumentValues(P17, _values(S17))])
    assert result.ok, result.log_lines()
    called = names(fake)
    assert "detect_trig_units" not in called[:called.index("new_part")]
    assert "add_global_variable" not in called[:called.index("new_part")]


def test_a_document_update_changes_still_has_its_trig_units_measured_before_its_values_are_set():
    fake = _built_gearbox()
    _update(fake)
    called = names(fake)
    assert "detect_trig_units" in called[:called.index("set_global_variable")]


def test_interferences_between_the_same_components_are_one_clash_with_their_volumes_summed():
    fake = FakeSolidWorks(clashes=[(("gear1-1", "gear2-1"), 54.0), (("gear2-1", "gear1-1"), 27.0),
                                   (("gear1-1", "gear2-1"), 10.5), ((), 0.5), ((), 0.25)])
    _, result = _build(fake)
    assert result.clashes == [swbuild.Clash(("gear1-1", "gear2-1"), ("G1", "G2"), 91.5),
                              swbuild.Clash((), (), 0.5), swbuild.Clash((), (), 0.25)]
    assert "CHECK   G1 and G2 interfere, 91.500 mm³; look where they meet" in result.log_lines()


# -- W4 review: nothing escapes a job once it has saved something (B1) ----------------------------------------


class ComErrorLookAlike(Exception):
    """Stands in for ``pywintypes.com_error`` reaching swbuild unwrapped (or anything else unexpected)."""


RPC = ComErrorLookAlike(-2147023170, "The remote procedure call failed.", None, None)


def test_a_raise_on_the_third_save_keeps_the_two_parts_saved_before_it_on_the_result():
    """The review's w4r_crash: the third save_as raised a non-SolidWorksError and build_gearbox raised with it, so
    the two parts SolidWorks had saved never reached the record."""
    fake = FakeSolidWorks(raises={"save_as": (2, RPC)})
    _, result = _build(fake)
    assert [r.saved for r in result.parts.built] == [P17, ""] and not result.ok
    assert result.parts.built[1].failures[0][0] == "save"
    assert result.parts.built[1].failures[0][1].startswith("it stopped on an unexpected ComErrorLookAlike: ")
    assert result.skipped == "the layout part and the assembly, because a part failed"
    assert "new_assembly" not in names(fake)


def test_a_raise_making_the_first_part_is_a_failed_part_not_a_raise():
    fake = FakeSolidWorks(raises={"new_part": (1, RPC)})
    _, result = _build(fake)
    assert len(result.parts.built) == 1 and result.parts.built[0].failures[0][0] == "new part"
    assert result.parts.skipped == [P68] and not result.ok


def test_a_raise_between_documents_is_a_failure_on_the_result_and_what_saved_stays():
    def say(step):
        if step.stage == "layout":
            raise RPC
    fake = FakeSolidWorks()
    _, result = _build(fake, progress=say)
    assert [r.saved for r in result.parts.built] == [P17, P68] and result.layout is None
    assert result.failures == [("the layout part", "it stopped on an unexpected ComErrorLookAlike: (-2147023170, "
                                                   "'The remote procedure call failed.', None, None).")]
    assert result.skipped == "the assembly, because the job stopped during the layout part"
    assert not result.ok
    assert result.log_lines()[-2:] == ["FAIL    the layout part: " + result.failures[0][1],
                                       "SKIPPED the assembly, because the job stopped during the layout part"]


def test_a_raise_in_the_interference_check_is_said_and_the_build_stands():
    fake = FakeSolidWorks(raises={"interferences": (1, RPC)})
    _, result = _build(fake)
    assert result.ok and result.interference_error.startswith("it stopped on an unexpected ComErrorLookAlike")


def test_the_reuse_check_still_refuses_before_anything_is_made():
    """The pre-flight (paths, the reused documents checked live) may still raise: nothing is made by then."""
    fake = FakeSolidWorks(raises={"open_document": (1, RPC)})
    _saved_part(fake, S17, P17)
    with pytest.raises(ComErrorLookAlike):
        _build(fake, parts=[plan(S68, path=P68)], reuse=[swbuild.DocumentValues(P17, _values(S17))])
    assert "new_part" not in names(fake)


def test_an_update_that_raises_part_way_keeps_what_it_changed_on_the_result():
    fake = _built_gearbox()
    fake.raises = {"set_global_variable": (fake.counts.get("set_global_variable", 0) + 2, RPC)}   # S2 X
    result = _update(fake)
    assert result.changed == [P68] and result.layout is not None and result.layout.changed == []
    assert result.failures[0][0] == 'R_Layout.SLDPRT "S2 X"'
    assert result.skipped == "the assembly, because R_Layout.SLDPRT failed" and "place_component" not in names(fake)


def test_an_update_whose_assembly_raises_keeps_the_values_it_set():
    fake = _built_gearbox()
    fake.raises = {"component_frame": (fake.counts.get("component_frame", 0) + 1, RPC)}
    result = _update(fake)
    assert result.changed == [P68, LAYOUT] and result.placed == []
    assert result.failures[0][0] == "R.SLDASM" and "ComErrorLookAlike" in result.failures[0][1]
    assert result.rebuilt                                 # the values changed, so the assembly is still rebuilt


def test_an_update_raise_between_documents_is_a_failure_on_the_result():
    def say(step):
        if step.stage == "place":
            raise RPC
    fake = _built_gearbox()
    result = _update(fake, progress=say)
    assert result.changed == [P68, LAYOUT] and not result.ok
    assert result.failures[0][0] == "R.SLDASM" and result.failures[0][1].startswith("it stopped on an unexpected")


# -- W4 review: Update touches only the documents it changes (S2) ---------------------------------------------


def test_an_update_leaves_a_part_that_holds_its_values_untouched_and_unmeasured():
    """W4 review S2: on SolidWorks 2026 every Update marked every part modified, because the check measured each
    part's trig units (an equation added and deleted)."""
    fake = _built_gearbox()
    fake.touched.clear()
    result = _update(fake)
    assert result.ok and result.changed == [P68, LAYOUT, ASM]
    assert fake.touched == {_key(P68), _key(LAYOUT), _key(ASM)}           # not Gear_m1.5_N17
    assert result.parts[0].changed == [] and result.parts[0].trig == DEGREES and result.parts[0].unchanged
    measured = [i for i, (n, _) in enumerate(fake.calls) if n == "detect_trig_units"]
    assert len(measured) == 2                         # once in each document Update changes, by update_variables
    opened = [a[0] for n, a in fake.calls if n == "open_document"]
    assert opened.count(P17) == 1                     # read in the check, and never opened again to change it


@pytest.mark.parametrize("trig", [DEGREES, RADIANS])
def test_an_update_that_changes_nothing_touches_nothing(trig):
    fake = _built_gearbox(trig=trig)
    fake.touched.clear()
    result = _update(fake, parts=[swbuild.DocumentValues(P17, _values(S17)), swbuild.DocumentValues(P68, _values(S68))],
                     layout=swbuild.DocumentValues(LAYOUT, LAYOUT_VALUES, LAYOUT_FEATURES), placements=_placements())
    assert result.ok and result.changed == [] and fake.touched == set()
    assert "detect_trig_units" not in names(fake) and "rebuild" not in names(fake)
    assert [r.trig for r in result.parts] == [trig, trig]
    assert result.log_lines()[-1] == "nothing changed in SolidWorks"


def test_a_part_whose_text_is_the_degree_form_but_whose_unit_is_radians_does_not_hold_its_values():
    """W4 review N5: the read-only decision took the text alone, so a part holding the degree form of its trig
    globals whose angle unit was later set to radians — its geometry evaluating cos(20 rad) — was called correct,
    reused, and left alone by Update. The values SolidWorks evaluates now decide too."""
    fake = FakeSolidWorks(trig=DEGREES)
    _saved_part(fake, S17, P17)
    fake.trig = RADIANS                                    # the document's unit set to radians since it was built
    trig_globals = [v.name for v in _values(S17) if v.expression_for(DEGREES) != v.expression_for(RADIANS)]
    assert trig_globals                                    # a spur part has some: the case is real
    _, result = _build(fake, parts=[], reuse=[swbuild.DocumentValues(P17, _values(S17))], layout=None, assembly=None)
    ((path, why),) = result.mismatched
    assert path == P17 and why.startswith(
        "Gear_m1.5_N17.SLDPRT does not hold what the workbook asks of it, so it cannot be reused: its equations are "
        f'written for degrees, but SolidWorks evaluates them otherwise ("{trig_globals[0]}" is ')
    assert why.endswith("here), so its angle unit was changed since they were written.")
    # Update no longer leaves it alone: it measures the unit and writes the radian forms.
    fake.calls.clear()
    result = _update(fake, parts=[swbuild.DocumentValues(P17, _values(S17))], layout=None, assembly="",
                     placements=[])
    assert result.ok and result.changed == [P17] and result.parts[0].trig == RADIANS
    assert "detect_trig_units" in names(fake)
    held = dict(split_equation(t) for t in fake.memory[_key(P17)][0])
    assert all(held[v.name].replace(" ", "") == v.expression_for(RADIANS).replace(" ", "") for v in _values(S17))


def test_a_part_whose_unit_and_text_agree_is_still_left_alone_in_either_unit():
    for trig in (DEGREES, RADIANS):
        fake = FakeSolidWorks(trig=trig)
        _saved_part(fake, S17, P17)
        result = _update(fake, parts=[swbuild.DocumentValues(P17, _values(S17))], layout=None, assembly="",
                         placements=[])
        assert result.ok and result.changed == [] and "detect_trig_units" not in names(fake)


def test_new_values_that_evaluate_in_one_trig_unit_only_are_measured_to_decide():
    odd = (GlobalVariable("No. of Teeth", "69", radian_expression='"Nowhere" * 2'),)
    fake = _built_gearbox(trig=DEGREES)
    result = _update(fake, parts=[swbuild.DocumentValues(P68, odd)], layout=None, assembly="", placements=[])
    assert result.ok and result.changed == [P68]
    fake = _built_gearbox(trig=RADIANS)
    with pytest.raises(swbuild.BuildError, match="Gear_m1.5_N68.SLDPRT cannot be updated: the new values do not "
                                                 "evaluate: "):
        _update(fake, parts=[swbuild.DocumentValues(P68, odd)], layout=None, assembly="", placements=[])
    assert "set_global_variable" not in names(fake)


def test_an_update_notes_each_files_time_before_it_changes_anything():
    fake = _built_gearbox()
    times = {_key(P17): 1.0, _key(P68): 2.0, _key(LAYOUT): 3.0}

    def mtime(path):
        if _key(path) not in times:
            raise OSError("not there")
        return times[_key(path)]
    result = _update(fake, mtime=mtime)
    assert result.mtimes == {P17: 1.0, P68: 2.0, LAYOUT: 3.0}         # the assembly's time could not be read


def test_every_same_named_document_open_elsewhere_is_named_in_one_refusal():
    """Review S3: a refusal that concerns several files names all of them."""
    fake = FakeSolidWorks(open_docs=[DocInfo("Gear_m1.5_N17.SLDPRT", r"C:\Other\Gear_m1.5_N17.SLDPRT", 1),
                                     DocInfo("R.SLDASM", r"C:\Other\R.SLDASM", 2)])
    with pytest.raises(swbuild.BuildError) as raised:
        _build(fake)
    assert str(raised.value) == (r"C:\Other\Gear_m1.5_N17.SLDPRT is open in SolidWorks, and it has the same file name "
                                 r"as C:\W\Gear_m1.5_N17.SLDPRT, which this job would make; C:\Other\R.SLDASM is open "
                                 r"in SolidWorks, and it has the same file name as C:\W\R.SLDASM, which this job would "
                                 "make; SolidWorks keeps one document per file name, so close Gear_m1.5_N17.SLDPRT and "
                                 "R.SLDASM in SolidWorks and try again.")
    assert fake.calls == []


# -- probe assembly_rebuild_scope: an assembly rebuild marks the assembly, never parts it did not change ---------
#
# The W4 rerun on SolidWorks 2026 failed three checks for one fault: the app rebuilt assemblies with
# ForceRebuild3(False), which marks every component modified, so SolidWorks asked to save parts no job had changed
# (parts earlier revisions share among them). The fake marks what probe assembly_rebuild_scope saw each rebuild
# mark (its docstring), choosing the member through swcom.rebuild_call as Session does; FULL is the route the app
# used to take for the static gearbox, to show the fault.

FULL = {"ASSEMBLY_REBUILD_ROUTE": "ForceRebuild3(False)", "ASSEMBLY_REBUILD_TOP_ONLY": False}
R1_LAYOUT, R1_ASM = W + "R_r1_Layout.SLDPRT", W + "R_r1.SLDASM"


def _full_rebuild(monkeypatch):
    for name, value in FULL.items():
        monkeypatch.setattr(findings, name, value)


def _build_again(fake):
    """Revision 1 of the gearbox: G1's part reused from revision 0 (shared by both assemblies), G2 a new part."""
    _, result = _build(fake, parts=[plan(S68, path=P68B)], reuse=[swbuild.DocumentValues(P17, _values(S17))],
                       layout=_layout_plan(R1_LAYOUT), assembly=_gearbox_assembly((P17, P68B), R1_LAYOUT, R1_ASM))
    assert result.ok, result.log_lines()
    return result


def test_a_fresh_build_leaves_every_part_and_the_layout_as_saved():
    fake, result = _build()
    assert result.ok and result.assembly.rebuilt
    # Every part and the layout read as saved; the assembly reads modified, because a read after its save marks it
    # (probe assembly_rebuild_scope's flags_after_reads; the fake pins it on the interference check), with nothing
    # lost by not saving it.
    assert fake.touched == {_key(ASM)}


def test_a_fresh_build_with_the_old_full_rebuild_left_every_part_marked(monkeypatch):
    _full_rebuild(monkeypatch)
    fake, result = _build()
    assert result.ok and fake.touched == {_key(P17), _key(P68), _key(LAYOUT), _key(ASM)}   # the rerun's fault


def test_a_build_again_leaves_the_part_it_reuses_as_saved():
    """W4 rerun failure 2: the superseded G1 part, which nothing changed, read modified after _r2."""
    fake = _built_gearbox()
    fake.touched.clear()
    _build_again(fake)
    assert fake.touched == {_key(R1_ASM)}            # the mark of the reads after its save alone


def test_a_build_again_with_the_old_full_rebuild_marked_the_shared_part(monkeypatch):
    fake = _built_gearbox()
    fake.touched.clear()
    _full_rebuild(monkeypatch)
    _build_again(fake)
    assert _key(P17) in fake.touched


def _update_r1(fake, **kwargs):
    kwargs.setdefault("parts", [swbuild.DocumentValues(P17, _values(S17)), swbuild.DocumentValues(P68B, _values(S69))])
    kwargs.setdefault("layout", swbuild.DocumentValues(R1_LAYOUT, (GlobalVariable("S2 X", "64.5"),), LAYOUT_FEATURES))
    kwargs.setdefault("assembly", R1_ASM)
    return _update(fake, **kwargs)


def test_an_update_marks_only_the_part_it_changed_the_layout_and_the_assembly():
    """W4 rerun failure 1: after an Update that gave G2 69 teeth and moved S2, all six documents read modified."""
    fake = _built_gearbox()
    _build_again(fake)
    fake.touched.clear()
    result = _update_r1(fake)
    assert result.ok, result.log_lines()
    assert result.changed == [P68B, R1_LAYOUT, R1_ASM] and result.placed == ["G2"]
    # G1's part, shared with revision 0, and every document of revision 0 read as saved.
    assert fake.touched == {_key(P68B), _key(R1_LAYOUT), _key(R1_ASM)}


def test_an_update_with_the_old_full_rebuild_marked_every_part(monkeypatch):
    fake = _built_gearbox()
    _build_again(fake)
    fake.touched.clear()
    _full_rebuild(monkeypatch)
    _update_r1(fake)
    assert {_key(P17), _key(P68B), _key(R1_LAYOUT), _key(R1_ASM)} <= fake.touched


def test_a_pure_move_marks_only_the_layout_and_the_assembly():
    """W4 rerun failure 3 (demonstration b): a move that changed no part marked all four gear parts modified."""
    fake = _built_gearbox()
    fake.touched.clear()
    result = _update(fake, parts=[swbuild.DocumentValues(P17, _values(S17)), swbuild.DocumentValues(P68, _values(S68))],
                     placements=_placements((TURNED2, (64.5, 0.0, 0.0))))
    assert result.ok, result.log_lines()
    assert result.changed == [LAYOUT, ASM] and result.placed == ["G2"]
    assert fake.touched == {_key(LAYOUT), _key(ASM)}


def test_a_put_alone_marks_nothing_its_rebuild_marks_the_assembly():
    assert findings.PUT_MARKS_ASSEMBLY_MODIFIED is False
    fake = _built_gearbox()
    fake.open_document(ASM)
    fake.touched.clear()
    fake.find_component("g2", "gear2-1")
    fake.place_component("g2", TURNED2, (64.5, 0.0, 0.0), kind=swcom.ASSEMBLY_STATIC)
    assert fake.touched == {_key(ASM)}


def test_a_component_that_fails_still_fails_the_assemblys_top_only_rebuild():
    fake = _built_gearbox()
    fake.failed_documents = {_key(P68)}
    result = _update(fake)
    assert not result.rebuilt and ("R.SLDASM", "SolidWorks reported an error rebuilding R.") in result.failures


UNSETTLED = [({"ASSEMBLY_REBUILD_ROUTE": None}, "How to rebuild an assembly has not been settled on SolidWorks yet "
              "(findings.ASSEMBLY_REBUILD_ROUTE is None), so no assembly is changed; run probe tier 7 first."),
             ({"ASSEMBLY_REBUILD_ROUTE": "ForceRebuild3(maybe)"},
              "How to rebuild an assembly has not been settled on SolidWorks yet (findings.ASSEMBLY_REBUILD_ROUTE is "
              "'ForceRebuild3(maybe)'), so no assembly is changed; run probe tier 7 first."),
             ({"ASSEMBLY_REBUILD_TOP_ONLY": None},
              "findings.ASSEMBLY_REBUILD_ROUTE is 'ForceRebuild3(True)' but findings.ASSEMBLY_REBUILD_TOP_ONLY is None, "
              "and the two disagree, so no assembly is changed; run probe tier 7 again.")]
CHANGES = ("new_part", "new_assembly", "set_global_variable", "add_global_variable", "place_component", "rebuild",
           "save_as", "detect_trig_units")


@pytest.mark.parametrize("unsettled, sentence", UNSETTLED)
def test_an_update_refuses_an_unsettled_assembly_rebuild_before_changing_anything(monkeypatch, unsettled, sentence):
    fake = _built_gearbox()
    for name, value in unsettled.items():
        monkeypatch.setattr(findings, name, value)
    fake.touched.clear()
    with pytest.raises(swbuild.BuildError) as raised:
        _update(fake)
    assert str(raised.value) == sentence
    assert not any(n in CHANGES for n in names(fake)) and fake.touched == set()


@pytest.mark.parametrize("unsettled, sentence", UNSETTLED)
def test_a_static_build_refuses_an_unsettled_assembly_rebuild_before_making_anything(monkeypatch, unsettled,
                                                                                    sentence):
    for name, value in unsettled.items():
        monkeypatch.setattr(findings, name, value)
    for make in (lambda fake: _build(fake),
                 lambda fake: swbuild.build(fake, _gearbox_assembly(), never_exists)):
        fake = FakeSolidWorks()
        with pytest.raises(swbuild.BuildError) as raised:
            make(fake)
        assert str(raised.value) == sentence
        assert not any(n in CHANGES for n in names(fake))


def test_parts_alone_are_built_whatever_the_assembly_route_says(monkeypatch):
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_ROUTE", None)
    fake, result = _build(layout=None, assembly=None)
    assert result.ok and [r.saved for r in result.parts.built] == [P17, P68]


# -- three kinds of assembly (the reviews of 9c39fb8 and 31d1ac9): a pair keeps the full rebuild tiers 4 and 5 ran,
# a mated workbook train takes MATED_ASSEMBLY_REBUILD_ROUTE (full while None), the static gearbox top-only.
#
# Probe assembly_rebuild_scope tried fixed components only. The train's finding is measured on the workbook train's
# mates (axis coincident, an axial distance linked to a global, locks, gear mates); a pair has other mates (its
# centre-distance equation, mesh, shaft and point mates), so a pair never reads it, and PLAN-GEARBOX keeps
# build_pair as it is. A pair build does not depend on the tier-7 workbook finding either.

FULL_CALL = ("ForceRebuild3", (False,))
TOP_CALL = ("ForceRebuild3", (True,))
PAIR_PATHS = (r"C:\g\a.SLDPRT", r"C:\g\b.SLDPRT", "", r"C:\g\Pair.SLDASM")
PAIR, TRAIN, STATIC = swcom.ASSEMBLY_PAIR, swcom.ASSEMBLY_TRAIN, swcom.ASSEMBLY_STATIC


def _pair_kinds():
    """Every kind of pair assembly the app builds, by its own planners."""
    from gear_generator.gears import pair
    from test_gears_bevel import spec as bevel_spec
    from test_gears_crossed import gears as crossed_gears

    spur_a, spur_b = GearSpec(module="1.5", teeth="20"), GearSpec(module="1.5", teeth="60")
    hel_a = GearSpec(kind="helical", module="2", teeth="20", helix_angle="15")
    hel_b = hel_a.with_values(teeth="40", hand="left")
    her_a = GearSpec(kind="herringbone", module="2", teeth="20", helix_angle="30", face_width="20")
    her_b = her_a.with_values(teeth="40", hand="left", face_width="16")
    pinion, ring = GearSpec(module="2", teeth="20"), GearSpec(module="2", teeth="60", teeth_side="internal")
    cross_a, cross_b = crossed_gears()
    out = {}
    for name, (a, b) in (("spur", (spur_a, spur_b)), ("helical", (hel_a, hel_b)), ("herringbone", (her_a, her_b)),
                         ("ring", (pinion, ring))):
        out[f"{name}, fixed"] = pair.assembly_plan(a, b, *PAIR_PATHS)
        out[f"{name}, gear mate"] = pair.assembly_plan(a, b, *PAIR_PATHS, motion="gear mate")
    for route in (pair.ROUTE_MATES, pair.ROUTE_FIXED):
        out[f"crossed, {route}"] = pair.crossed_assembly_plan(cross_a, cross_b, *PAIR_PATHS, 90.0, route)
    out["bevel"] = pair.assembly_plan(bevel_spec(), bevel_spec("40", "20"), *PAIR_PATHS)
    return out


@pytest.fixture
def gear_mates_settled(monkeypatch):
    """The gear-mate findings, no pair rebuild finding, and the train built and re-solved by the full rebuild
    (``"ForceRebuild3(False)"`` for both of its findings, which agree as a train Build requires): what the full
    route is pinned under, whatever a probe round later sets the train's to (a test that wants another sets it)."""
    for name, value in (("GEAR_MATE_ROUTE", "mates"), ("MATE_GEAR", 10), ("GEAR_MATE_NUMERATOR_FIRST", True),
                        ("GEAR_MATE_EXTERNAL_FLIP", False)):
        monkeypatch.setattr(findings, name, value)
    monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", "ForceRebuild3(False)", raising=False)
    monkeypatch.setattr(findings, "MATED_BUILD_REBUILD_ROUTE", "ForceRebuild3(False)", raising=False)
    monkeypatch.setattr(findings, "PAIR_ASSEMBLY_REBUILD_ROUTE", None, raising=False)


def _build_pair(fake, assembly):
    return swbuild.build_pair(fake, plan(S17, path=PAIR_PATHS[0]), plan(S68, path=PAIR_PATHS[1]), assembly,
                              never_exists)


@pytest.mark.parametrize("findings_set", [{}, {"ASSEMBLY_REBUILD_ROUTE": None}, {"ASSEMBLY_REBUILD_ROUTE": "guess"},
                                          {"MATED_ASSEMBLY_REBUILD_ROUTE": "ForceRebuild3(True)"},
                                          {"MATED_ASSEMBLY_REBUILD_ROUTE": "ForceRebuild3(True)",
                                           "ASSEMBLY_REBUILD_ROUTE": None}])
def test_every_pair_kind_rebuilds_and_puts_in_full_whatever_the_workbook_findings(monkeypatch, gear_mates_settled,
                                                                                  findings_set):
    """The same COM members as at e57aca7 for all eleven: neither the tier-7 finding nor the train's moves a pair."""
    for name, value in findings_set.items():
        monkeypatch.setattr(findings, name, value, raising=False)
    kinds = _pair_kinds()
    assert len(kinds) == 11
    for name, assembly in kinds.items():
        assert assembly.check() == [], name
        fake = FakeSolidWorks()
        result = _build_pair(fake, assembly)
        assert result.ok and result.assembly.ok, (name, result.log_lines())
        start = names(fake).index("new_assembly")
        puts = names(fake)[start:].count("place_component")
        # The assembly's members: one per put (its own rebuild) and its one rebuild, every one the full rebuild.
        assert fake.rebuild_members[-(puts + 1):] == [FULL_CALL] * (puts + 1), name
        assert fake.assembly_kinds == [PAIR] * (puts + 1), name


def test_a_crossed_pair_placed_fixed_has_no_mate_and_is_still_built_as_a_pair(gear_mates_settled):
    fixed = _pair_kinds()["crossed, fixed"]
    assert not swbuild.is_mated(fixed) and swbuild.workbook_assembly_kind(fixed) == STATIC   # alone: static
    fake = FakeSolidWorks()
    _build_pair(fake, fixed)
    assert set(fake.assembly_kinds) == {PAIR} and fake.rebuild_members[-1] == FULL_CALL


@pytest.mark.parametrize("train_route, wanted", [(None, FULL_CALL), ("ForceRebuild3(True)", TOP_CALL)])
def test_a_plan_with_mates_built_outside_build_pair_is_a_train(gear_mates_settled, monkeypatch, train_route, wanted):
    monkeypatch.setattr(findings, "ASSEMBLY_REBUILD_ROUTE", None)            # a train does not lean on tier 7
    monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", train_route, raising=False)
    monkeypatch.setattr(findings, "MATED_BUILD_REBUILD_ROUTE", train_route, raising=False)
    mated = _pair_kinds()["spur, gear mate"]
    assert swbuild.workbook_assembly_kind(mated) == TRAIN
    assert swcom.rebuild_call(swcom.DOC_ASSEMBLY, TRAIN) == wanted
    fake = FakeSolidWorks()
    if train_route is None:                  # a train Build waits for the route it may be built under (probe P0b)
        with pytest.raises(swbuild.BuildError, match="MATED_BUILD_REBUILD_ROUTE is None"):
            swbuild.build(fake, mated, never_exists)
        assert fake.calls == []
        return
    result = swbuild.build(fake, mated, never_exists)
    assert result.ok and fake.rebuild_kinds == [TRAIN] and set(fake.rebuild_members) == {wanted}


def test_with_the_trains_route_set_a_train_is_top_only_and_a_pair_still_full(monkeypatch, gear_mates_settled):
    monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", "ForceRebuild3(True)", raising=False)
    monkeypatch.setattr(findings, "MATED_BUILD_REBUILD_ROUTE", "ForceRebuild3(True)", raising=False)
    mated = _pair_kinds()["spur, gear mate"]
    train = FakeSolidWorks()
    swbuild.build(train, mated, never_exists)
    pair_fake = FakeSolidWorks()
    _build_pair(pair_fake, mated)
    assert set(train.rebuild_members) == {TOP_CALL}
    assert pair_fake.rebuild_members[-1] == FULL_CALL and set(pair_fake.assembly_kinds) == {PAIR}


def test_a_pair_route_once_set_is_taken_by_pairs_alone(monkeypatch, gear_mates_settled):
    monkeypatch.setattr(findings, "PAIR_ASSEMBLY_REBUILD_ROUTE", "ForceRebuild3(True)", raising=False)
    mated = _pair_kinds()["spur, gear mate"]
    pair_fake, train = FakeSolidWorks(), FakeSolidWorks()
    _build_pair(pair_fake, mated)
    swbuild.build(train, mated, never_exists)
    assert pair_fake.rebuild_members[-1] == TOP_CALL and set(train.rebuild_members) == {FULL_CALL}


def test_the_static_gearbox_still_rebuilds_and_puts_top_only():
    fake, result = _build()
    assert result.ok
    start = names(fake).index("new_assembly")
    puts = names(fake)[start:].count("place_component")
    assert puts == 3 and fake.rebuild_members[-(puts + 1):] == [TOP_CALL] * (puts + 1)
    assert fake.assembly_kinds == [STATIC] * (puts + 1)


@pytest.mark.parametrize("name, sentence", [
    ("PAIR_ASSEMBLY_REBUILD_ROUTE", "findings.PAIR_ASSEMBLY_REBUILD_ROUTE is 'guess', which is not a rebuild this "
                                    "code knows, so no pair assembly is changed; run its probe again."),
    ("MATED_ASSEMBLY_REBUILD_ROUTE", "findings.MATED_ASSEMBLY_REBUILD_ROUTE is 'guess', which is not a rebuild this "
                                     "code knows, so no mated assembly is changed; run its probe again."),
])
def test_an_unknown_route_refuses_its_own_kind_before_anything_is_made(monkeypatch, gear_mates_settled, name,
                                                                       sentence):
    """The review of 31d1ac9: the refusal came after both gears were saved (new_part, save_as, new_part, save_as),
    leaving files with no sidecars that the next Build refused to overwrite. Each finding refuses its own kind."""
    monkeypatch.setattr(findings, name, "guess", raising=False)
    mated = _pair_kinds()["spur, gear mate"]
    refused = (lambda fake: _build_pair(fake, mated)) if name.startswith("PAIR") else \
        (lambda fake: swbuild.build(fake, mated, never_exists))
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        refused(fake)
    assert str(raised.value) == sentence
    assert not any(n in CHANGES for n in names(fake)) and fake.saved == {}
    built = (lambda fake: swbuild.build(fake, mated, never_exists)) if name.startswith("PAIR") else \
        (lambda fake: _build_pair(fake, mated))
    other = FakeSolidWorks()
    assert built(other).ok                                    # the other kind does not read it


def test_no_rebuild_member_is_called_but_through_the_one_decision():
    """The review of 9c39fb8: every ForceRebuild3 / EditRebuild3 the app makes goes through swcom.rebuild_call and
    its table, so the route is decided in one place (the probes call COM raw on purpose and are left out)."""
    import ast
    import pathlib

    import gear_generator

    root = pathlib.Path(gear_generator.__file__).parent
    members = {"ForceRebuild3", "EditRebuild3"}
    found = []
    for path in sorted(root.rglob("*.py")):
        if "probe" in path.relative_to(root).parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        allowed = set()
        for node in ast.walk(tree):
            inside = (isinstance(node, ast.FunctionDef) and node.name == "rebuild_call") or (
                isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "ASSEMBLY_REBUILD_CALLS"
                                                     for t in node.targets))
            if inside:
                allowed.update(id(n) for n in ast.walk(node))
        for node in ast.walk(tree):
            named = (isinstance(node, ast.Constant) and node.value in members) or (
                isinstance(node, ast.Attribute) and node.attr in members)
            if named and id(node) not in allowed:
                found.append(f"{path.relative_to(root)}:{node.lineno}")
    assert found == []


# -- the review of 31d1ac9: an assembly's kind is always said; one that is not is refused ---------------------

UNSAID = ("This assembly was to be rebuilt without saying what kind of assembly it is (fixed, a mated train or a "
          "pair), so which rebuild it takes cannot be chosen and nothing is changed; that is a fault in Gear "
          "Generator, not in SolidWorks.")


def test_an_assembly_rebuild_or_put_whose_kind_is_not_said_is_refused():
    fake = _built_gearbox()
    fake.open_document(ASM)
    fake.touched.clear()
    with pytest.raises(SolidWorksError) as raised:
        fake.rebuild()
    assert str(raised.value) == UNSAID
    fake.find_component("g2", "gear2-1")
    with pytest.raises(SolidWorksError) as raised:
        fake.place_component("g2", TURNED2, (64.5, 0.0, 0.0))
    assert str(raised.value) == UNSAID
    with pytest.raises(SolidWorksError, match="'mated' is not a kind of assembly Gear Generator rebuilds"):
        fake.rebuild(kind="mated")


def test_a_part_rebuilds_whether_or_not_a_kind_is_said():
    fake = FakeSolidWorks()
    fake.new_part()
    assert fake.rebuild() is True and fake.rebuild_members == [FULL_CALL]


def test_every_static_site_says_its_kind():
    fake, result = _build()
    assert result.ok and fake.assembly_kinds and set(fake.assembly_kinds) == {STATIC}   # build_gearbox: 3 puts, 1 rebuild
    fake.calls.clear()
    fake.assembly_kinds.clear()
    fake.frames = {"layout-1": (IDENTITY, (0.0, 0.0, 0.0)), "gear1-1": (IDENTITY, (0.0, 0.0, 0.0)),
                   "gear2-1": (TURNED2, AT2)}
    update = _update(fake)
    assert update.ok and update.placed == ["G2"]
    assert fake.assembly_kinds == [STATIC, STATIC]               # update_gearbox: its put, then its one rebuild


def test_every_put_in_the_app_and_its_scripts_names_its_kind():
    """A put is always on an assembly, so every place_component call says kind=… (a rebuild's document is known
    only at run time: the fake refuses an assembly rebuild with no kind, which the build and update tests meet)."""
    import ast
    import pathlib

    import gear_generator

    root = pathlib.Path(gear_generator.__file__).parent
    scripts = pathlib.Path(__file__).resolve().parents[1] / "probe"
    missing = []
    for path in sorted(list(root.rglob("*.py")) + list(scripts.glob("*.py"))):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "place_component" and \
                    not any(k.arg == "kind" for k in node.keywords):
                missing.append(f"{path.name}:{node.lineno}")
    assert missing == []


# -- W5: the train (W5-PLAN §1.4, §3.1; W5-INTERFACES.md; W5-DECISIONS.md) --------------------------------------------
#
# A 12 : 1 reducer as workbook.motion.motion_assembly_plan's docstring orders it, written by hand here (package B
# writes the planner): G1 (17) on S1 at the origin, G2 (68) and G3 (17) on S2 — G3 locked to G2 — and G4 (51) on S3,
# every shaft Z+; G1 and G2 coincident with the Front plane, G4 20 mm along S3 on the global "G4 Face Z".

P51 = W + "Gear_m1.5_N51.SLDPRT"
S51 = GearSpec().with_values(teeth="51")
T_LAYOUT, T_ASM = W + "T_Layout.SLDPRT", W + "T.SLDASM"
TEETH = {"G1": 17, "G2": 68, "G3": 17, "G4": 51}
TRAIN_GEARS = {"gear1": "G1", "gear2": "G2", "gear3": "G3", "gear4": "G4"}
TRAIN_PARTS = {"gear1": P17, "gear2": P68, "gear3": P17, "gear4": P51}


def _train_frames(s3=(63.75, 51.0), z4=20.0):
    return {"G1": (_rot_z(0.0), (0.0, 0.0, 0.0)), "G2": (_rot_z(180.0 / 68), (63.75, 0.0, 0.0)),
            "G3": (_rot_z(0.0), (63.75, 0.0, 20.0)), "G4": (_rot_z(180.0 / 51), (s3[0], s3[1], z4))}


def _train_layout_plan(path=T_LAYOUT):
    return BuildPlan("layout", "", (
        ops.NewPart(""),
        ops.AddGlobal("S2 X", "63.75"), ops.AddGlobal("S3 X", "63.75"), ops.AddGlobal("S3 Y", "51"),
        ops.RefPlane("x2", "S2 X Plane", 3, 63.75), ops.RefPlane("x3", "S3 X Plane", 3, 63.75),
        ops.RefPlane("y3", "S3 Y Plane", 2, 51.0),
        ops.Axis("axis1", "S1 Axis", (2, 3)), ops.Axis("axis2", "S2 Axis", (2, "x2")),
        ops.Axis("axis3", "S3 Axis", ("x3", "y3")),
        ops.Rebuild(), ops.SaveAs(path),
    ), path)


T_LAYOUT_FEATURES = ("S2 X Plane", "S3 X Plane", "S3 Y Plane", "S1 Axis", "S2 Axis", "S3 Axis")


def _train_layout_values(s3x="63.75"):
    return swbuild.DocumentValues(T_LAYOUT, (GlobalVariable("S2 X", "63.75"), GlobalVariable("S3 X", s3x),
                                             GlobalVariable("S3 Y", "51")), T_LAYOUT_FEATURES)


P51R = W + "Ring_m1.5_N51.SLDPRT"        # a ring, as the app names one (the fake reads a "Ring…" file as a ring)


def _train_plan(path=T_ASM, follower_on_axis=False, idler=False, ring=False):
    frames = _train_frames()
    steps = [ops.NewAssembly(""), ops.AddGlobal("G4 Face Z", "20"),
             ops.AddComponent("layout", T_LAYOUT), ops.Place("layout", IDENTITY, (0.0, 0.0, 0.0)), ops.Fix("layout")]
    for handle, gear in TRAIN_GEARS.items():
        rotation, at = frames[gear]
        part = P51R if ring and handle == "gear4" else TRAIN_PARTS[handle]
        steps += [ops.AddComponent(handle, part, at), ops.Place(handle, rotation, at), ops.Fix(handle)]
    steps += [ops.Unfix("gear1"),
              ops.Mate("axis1", "coincident", "gear1:Gear Axis", "layout:S1 Axis", name="G1 on S1 Axis"),
              ops.Mate("along1", "point", "gear1:origin", "layout:plane1", name="G1 along S1"),
              ops.Unfix("gear2"),
              ops.Mate("axis2", "coincident", "gear2:Gear Axis", "layout:S2 Axis", name="G2 on S2 Axis"),
              ops.Mate("along2", "point", "gear2:origin", "layout:plane1", name="G2 along S2"),
              ops.Unfix("gear3"),
              ops.Mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2")]
    if follower_on_axis:                    # as compound_lock's "lock, both on the shaft" made it
        steps += [ops.Mate("axis9", "coincident", "gear3:Gear Axis", "layout:S2 Axis", name="G3 on S2 Axis"),
                  ops.Mate("along9", "point distance", "gear3:origin", "layout:plane1", 20.0, name="G3 along S2")]
    steps += [ops.Unfix("gear4"),
              ops.Mate("axis3", "coincident", "gear4:Gear Axis", "layout:S3 Axis", name="G4 on S3 Axis"),
              ops.Mate("along3", "point distance", "gear4:origin", "layout:plane1", 20.0, name="G4 along S3"),
              ops.LinkDimension("D1@G4 along S3", '"G4 Face Z"'),
              ops.Mate("mesh1", "gear", "gear1:Gear Axis", "gear2:Gear Axis", name="G1 meshes G2", ratio=(17.0, 68.0)),
              ops.Mate("mesh2", "gear", "gear3:Gear Axis", "gear4:Gear Axis", name="G3 meshes G4", ratio=(17.0, 51.0))]
    if idler:                               # G4 carries two gear mates, as an idler does (made up: no geometry here)
        steps.append(ops.Mate("mesh3", "gear", "gear2:Gear Axis", "gear4:Gear Axis", name="G2 meshes G4",
                              ratio=(68.0, 51.0)))
    return BuildPlan("gearbox", "", tuple(steps) + (ops.Rebuild(), ops.SaveAs(path)), path)


TRAIN_MATES = ["G1 on S1 Axis", "G1 along S1", "G2 on S2 Axis", "G2 along S2", "G3 locked to G2", "G4 on S3 Axis",
               "G4 along S3", "G1 meshes G2", "G3 meshes G4"]


def _build_train(fake=None, **kwargs):
    fake = fake or FakeSolidWorks()
    kwargs.setdefault("parts", [plan(S17, path=P17), plan(S68, path=P68), plan(S51, path=P51)])
    kwargs.setdefault("layout", _train_layout_plan())
    kwargs.setdefault("assembly", _train_plan())
    kwargs.setdefault("gears", TRAIN_GEARS)
    kwargs.setdefault("exists", fake.exists)
    return fake, swbuild.build_gearbox(fake, **kwargs)


def _close(f1, f2, tolerance=1e-9):
    rotation_off, origin_off = _frame_off(f1, f2)
    return rotation_off <= tolerance and origin_off <= tolerance


def test_the_train_plans_here_are_sound():
    for doctored in ({}, {"follower_on_axis": True}):
        assert _train_plan(**doctored).check() == [], doctored
    assert _train_layout_plan().check() == []


# -- the fake's own model of mates


def test_the_fake_keeps_a_trains_mates_with_its_document_and_reopens_them():
    fake, result = _build_train()
    assert result.ok, result.log_lines()
    assert [m.name for m in fake.saved_mates[_key(T_ASM)]] == TRAIN_MATES
    assert fake.mate("G4 along S3").link == "G4 Face Z"
    assert fake.mate("G3 locked to G2").a == ("gear2-1", "") and fake.mate("G3 locked to G2").b == ("gear3-1", "")
    fake.close_all()
    fake.open_document(T_ASM)
    assert [m.name for m in fake.mates] == TRAIN_MATES and fake.mate("G4 along S3").link == "G4 Face Z"


def test_an_undoctored_train_reads_clean_in_the_fake():
    fake, result = _build_train()
    assert all(fake.mate_status(name) == findings.ADD_MATE_NO_ERROR for name in TRAIN_MATES)
    assert fake.mate_states() == [swcom.MateState(name) for name in TRAIN_MATES]
    assert [fake.constrained_status(n) for n in ("gear1-1", "gear2-1", "gear3-1", "gear4-1")] == [2, 2, 2, 2]
    assert fake.constrained_status("layout-1") == findings.COMPONENT_FULLY_DEFINED      # the layout stays fixed
    for gear, frame in _train_frames().items():                          # mated where W4 placed them: nothing moved
        assert _close(fake.frames[f"gear{gear[1]}-1"], frame)


def test_the_fake_flags_a_follower_mated_to_its_shaft_as_tier_eight_recorded_it():
    """compound_lock, "lock, both on the shaft" (probe/results/latest.json): every AddMate5 answered 1, the lock was
    not flagged, and the along mates of both gears read code 46 as warnings. (A second axis mate or a loop of gear
    mates was never probed, so the fake flags neither unless a test says so through its knobs.)"""
    fake = FakeSolidWorks()
    swbuild.build(fake, _train_plan(follower_on_axis=True), never_exists)
    assert all(fake.mate_status(m.name) == findings.ADD_MATE_NO_ERROR for m in fake.mates)
    states = {s.name: s for s in fake.mate_states()}
    assert {n: (s.code, s.warning) for n, s in states.items() if s.code} == {"G2 along S2": (46, True),
                                                                          "G3 along S2": (46, True)}
    assert fake.constrained_status("gear3-1") == findings.COMPONENT_OVER_DEFINED


def _reopened_train(fake):
    fake.open_document(T_LAYOUT)
    fake.open_document(T_ASM)
    for index in range(1, 5):
        fake.find_component(f"placed{index}", f"gear{index}-1")


def test_a_layout_move_carries_the_anchor_to_its_new_axis_swung_the_wrong_way_and_its_follower_with_it():
    fake, _ = _build_train()
    fake.open_document(T_LAYOUT)
    fake.set_global_variable("S2 X", "64.5")
    _reopened_train(fake)
    g3_before = fake.frames["gear3-1"]
    fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    rotation, at = fake.frames["gear2-1"]
    assert at == (64.5, 0.0, 0.0)
    assert swbuild.turn_between(_train_frames()["G2"][0], rotation) == pytest.approx(math.radians(-13.0))
    relative = _compose(_inverse(fake.frames["gear2-1"]), fake.frames["gear3-1"])
    assert _close(relative, _compose(_inverse(_train_frames()["G2"]), g3_before))     # the lock held it
    assert _close(fake.frames["gear4-1"], _train_frames()["G4"])                      # S3 did not move


def test_a_face_z_global_moves_its_anchor_along_its_shaft_and_nothing_else():
    fake, _ = _build_train()
    _reopened_train(fake)
    fake.set_global_variable("G4 Face Z", "25")
    fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    assert fake.frames["gear4-1"] == (_train_frames()["G4"][0], (63.75, 51.0, 25.0))
    assert _close(fake.frames["gear3-1"], _train_frames()["G3"])


def test_a_put_on_a_gear_held_by_a_lock_moves_it_alone_and_says_nothing_as_solidworks_did():
    """W5-DECISIONS, on P0's lock_on_put_turns: with the lock on, a Transform2 put moved one gear, its locked partner
    did not follow, and SolidWorks reported nothing."""
    fake, _ = _build_train()
    _reopened_train(fake)
    turned = (_mul(_train_frames()["G2"][0], _rot_z(7.0)), _train_frames()["G2"][1])
    fake.place_component("placed2", *turned, kind=swcom.ASSEMBLY_TRAIN)          # no raise
    assert _close(fake.frames["gear2-1"], turned) and _close(fake.frames["gear3-1"], _train_frames()["G3"])
    assert fake.locked_puts == ["gear2-1"]
    fake.find_mate("lock", "G3 locked to G2")
    fake.set_mate_suppressed("lock", True)
    fake.place_component("placed3", *_train_frames()["G3"], kind=swcom.ASSEMBLY_TRAIN)
    assert fake.locked_puts == ["gear2-1"]                                         # suppressed: an honest put


def test_a_put_an_anchors_mates_pull_back_raises_as_place_component_would():
    fake, _ = _build_train()
    _reopened_train(fake)
    with pytest.raises(SolidWorksError, match=r"^gear4-1 did not take its frame \(rotation off .*, origin .* mm\)\.$"):
        fake.place_component("placed4", _train_frames()["G4"][0], (70.0, 51.0, 20.0), kind=swcom.ASSEMBLY_TRAIN)
    with pytest.raises(SolidWorksError, match="did not take its frame"):
        fake.place_component("placed4", _train_frames()["G4"][0], (63.75, 51.0, 30.0), kind=swcom.ASSEMBLY_TRAIN)


def test_the_fake_finds_suppresses_and_remakes_mates_by_name(monkeypatch):
    fake, _ = _build_train()
    _reopened_train(fake)
    with pytest.raises(swcom.MateGone, match='^The mate "Angle1" is not in T.SLDASM any more'):
        fake.find_mate("m", "Angle1")
    fake.find_mate("m", "G3 meshes G4")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
    with pytest.raises(SolidWorksError):
        fake.set_gear_ratio("m", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    fake.set_gear_ratio("m", "placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    assert fake.mate("G3 meshes G4").ratio == (18.0, 50.0) and fake.mates[-1].name == "G3 meshes G4"


# -- a train's build: the mate check before the save; a refused mate stops it (W5-DECISIONS, answer 1)


def test_a_turning_build_makes_its_mates_in_order_checks_them_before_the_save_and_saves_once():
    fake, result = _build_train()
    assert result.ok, result.log_lines()
    assert result.kind == swbuild.GEARBOX_MOTION == "motion"
    called = names(fake)
    start = called.index("new_assembly")
    tail = called[start:]
    made = [a[0] for n, a in fake.calls[start:] if n == "add_mate"]
    assert made == ["coincident", "point", "coincident", "point", "lock", "coincident", "point distance", "gear", "gear"]
    assert tail.count("rebuild") == 1 and fake.assembly_kinds[-1] == swcom.ASSEMBLY_TRAIN
    assert tail.index("rebuild") < tail.index("mate_states") < tail.index("save_as")
    checked = [a[0] for n, a in fake.calls[start:] if n == "constrained_status"]
    assert checked == ["gear1", "gear2", "gear3", "gear4"]                  # every turning gear, never the layout
    assert max(i for i, n in enumerate(tail) if n == "constrained_status") < tail.index("save_as")
    assert tail.count("save_as") == 1 and tail.index("save_as") < tail.index("interferences")
    assert result.assembly.mate_problems == [] and [m.name for m in result.assembly.mates] == TRAIN_MATES
    lines = result.assembly.log_lines()
    assert "ok      every mate sound, every gear free to turn" in lines
    assert "mate    G3 locked to G2" in lines and "mate    G4 along S3" in lines
    assert tail.index("link_dimension") < tail.index("rebuild")


def test_a_static_gearbox_is_never_mate_checked_and_says_static():
    fake, result = _build()
    assert result.ok and result.kind == swbuild.GEARBOX_STATIC == "static"
    assert not any(n in ("mate_states", "constrained_status") for n in names(fake))
    assert result.assembly.mates == [] and result.assembly.mate_problems == []


def test_a_pair_is_never_mate_checked(gear_mates_settled):
    fake = FakeSolidWorks()
    result = _build_pair(fake, _pair_kinds()["spur, gear mate"])
    assert result.ok and not any(n in ("mate_states", "constrained_status") for n in names(fake))
    assert result.assembly.mate_problems == []


def _refused(result):
    """What answer 1 promises for a refused train: the parts and the layout saved, no assembly saved, nothing in its
    place, the refused document named, and no interference check."""
    assert not result.ok and result.kind == ""
    assert [r.saved for r in result.parts.built] == [P17, P68, P51] and result.layout.saved == T_LAYOUT
    assert result.assembly is not None and not result.assembly.saved and result.assembly.document == "Assem1"
    assert result.assembly.mate_problems
    assert all(p[0].isupper() and p.endswith(".") for p in result.assembly.mate_problems)
    assert all(("the mate check", p) in result.assembly.failures or "would not make" in p
               for p in result.assembly.mate_problems)
    assert result.clashes == [] and result.skipped == ""
    assert any(line.startswith("STOPPED SolidWorks refused or flagged a mate, so Assem1 is left open")
               for line in result.log_lines())


def test_a_follower_also_mated_to_its_axis_stops_the_build_and_nothing_is_built_in_its_place():
    fake, result = _build_train(assembly=_train_plan(follower_on_axis=True))
    _refused(result)
    # No mate is marked at fault (every flag a warning, as recorded), so every flagged one is named.
    assert result.assembly.mate_problems == ["The mate G2 along S2 is in error in SolidWorks.",
                                             "The mate G3 along S2 is in error in SolidWorks.",
                                             "G2 is over-defined in SolidWorks.", "G3 is over-defined in SolidWorks."]
    called = names(fake)
    assert called.count("new_assembly") == 1 and "interferences" not in called
    assert _key(T_ASM) not in fake.saved and "close_document" not in called
    assert fake.suppressed is False                              # CommandInProgress back off after the refusal
    assert "mate    G3 along S2 · error code 46, a warning" in result.log_lines()
    assert "mate    G3 locked to G2" in result.log_lines()


def test_a_mate_in_error_though_made_with_status_one_stops_the_build_naming_the_mate_at_fault():
    fake = FakeSolidWorks(mate_codes={"G1 meshes G2": (51, True), "G3 meshes G4": (51, False)})
    _, result = _build_train(fake)
    _refused(result)
    assert result.assembly.mate_problems == ["The mate G3 meshes G4 is in error in SolidWorks."]


def test_every_flagged_mate_is_named_when_none_is_marked_at_fault():
    fake = FakeSolidWorks(mate_codes={"G1 meshes G2": (51, True), "G3 meshes G4": (51, True)})
    _, result = _build_train(fake)
    assert result.assembly.mate_problems == ["The mate G1 meshes G2 is in error in SolidWorks.",
                                             "The mate G3 meshes G4 is in error in SolidWorks."]


@pytest.mark.parametrize("status, sentence", [(3, "G2 cannot turn: SolidWorks reads it fully defined."),
                                              (4, "G2 is over-defined in SolidWorks."),
                                              (0, "G2 reads 0 in SolidWorks, not free to turn.")])
def test_a_gear_not_free_to_turn_stops_the_build_named_by_its_workbook_id(status, sentence):
    fake = FakeSolidWorks(constrained={"gear2-1": status})
    _, result = _build_train(fake)
    _refused(result)
    assert result.assembly.mate_problems == [sentence]


def test_without_the_gears_map_a_gear_is_named_by_the_name_solidworks_kept():
    fake = FakeSolidWorks(constrained={"gear2": 3})
    result = swbuild.build(fake, _train_plan(), never_exists)
    assert result.mate_problems == ["gear2-1 cannot turn: SolidWorks reads it fully defined."] and not result.saved


@pytest.mark.parametrize("status, sentence", [(5, "The mate G1 meshes G2 over-defines the assembly."),
                                              (3, "SolidWorks answered 3 when making the mate G1 meshes G2."),
                                              (None, "SolidWorks gave no answer when making the mate G1 meshes G2.")])
def test_an_add_mate_status_other_than_one_stops_the_build(status, sentence):
    fake = FakeSolidWorks(mate_statuses={"G1 meshes G2": status})
    _, result = _build_train(fake)
    _refused(result)
    assert result.assembly.mate_problems == [sentence]


@pytest.mark.parametrize("doctor, sentence", [
    (lambda states: [s for s in states if s.name != "G4 along S3"], "The mate G4 along S3 is missing from the assembly."),
    (lambda states: [swcom.MateState(s.name, suppressed=s.name == "G4 along S3") for s in states],
     "The mate G4 along S3 is suppressed in SolidWorks."),
])
def test_a_planned_mate_missing_or_suppressed_stops_the_build(doctor, sentence):
    fake = FakeSolidWorks()
    real = fake.mate_states
    fake.mate_states = lambda: doctor(real())
    _, result = _build_train(fake)
    _refused(result)
    assert result.assembly.mate_problems == [sentence]


def test_a_mate_solidworks_would_not_make_is_a_mate_problem_and_the_build_stops_there():
    refused = swcom.MateRefused("AddMate5 would not make a lock mate between gear2 and gear3.")
    fake = FakeSolidWorks(raises={"add_mate": (5, refused)})
    _, result = _build_train(fake)
    _refused(result)
    assert result.assembly.mate_problems == ["SolidWorks would not make the mate G3 locked to G2."]
    assert result.assembly.failures == [("mate    lock gear2 ~ gear3 as 'G3 locked to G2'",
                                         "AddMate5 would not make a lock mate between gear2 and gear3.")]
    assert "mate_states" not in names(fake)                     # a build stopped part-way is not checked


@pytest.mark.parametrize("raised", [RPC, SolidWorksError("gear3-1 could not be selected for the lock mate."),
                                    swcom.ComError("AddMate5", RPC)])
def test_any_other_raise_during_a_mate_is_an_ordinary_failed_build_with_no_mate_problem(raised):
    """W5-INTERFACES: only real refusals hold Build back; a COM or RPC failure, or a selection that did not take,
    fails the build as in W4 and records nothing that would grey Build out."""
    fake = FakeSolidWorks(raises={"add_mate": (5, raised)})
    _, result = _build_train(fake)
    assert not result.ok and result.kind == "" and not result.assembly.saved
    assert result.assembly.mate_problems == [] and result.assembly.failures


def test_a_mate_check_that_cannot_read_solidworks_is_an_ordinary_failure_with_no_mate_problem():
    fake = FakeSolidWorks(raises={"mate_states": (1, RPC)})
    _, result = _build_train(fake)
    assert not result.ok and not result.assembly.saved and result.assembly.mate_problems == []
    assert result.assembly.failures[0][0] == "the build"


def test_a_train_whose_template_is_missing_fails_as_in_w4_with_no_mate_problem():
    fake = FakeSolidWorks(fail_on={"new_assembly": "There is no assembly template at 'C:\\T\\No.asmdot'."})
    _, result = _build_train(fake)
    assert result.assembly.failures == [("new assembly", "There is no assembly template at 'C:\\T\\No.asmdot'.")]
    assert result.assembly.mate_problems == [] and result.kind == ""


@pytest.mark.parametrize("name", ["ADD_MATE_NO_ERROR", "COMPONENT_UNDER_DEFINED", "MATE_FIND_ROUTE", "THIS_CONFIGURATION",
                                  "COMPOUND_LOCK_ROUTE", "LOCK_SELECT_ROUTE", "MATE_LOCK", "MATE_RENAME_ROUTE",
                                  "MATE_COINCIDENT", "MATE_DISTANCE", "MATE_GEAR", "GEAR_MATE_ROUTE",
                                  "GEAR_MATE_NUMERATOR_FIRST", "ORIGIN_POINT", "MATES_UNDER_COMMAND_IN_PROGRESS",
                                  "MATE_RENAME_AT_ONCE"])
def test_a_train_is_refused_before_anything_is_made_while_a_finding_it_needs_is_not_settled(monkeypatch, name):
    """Every finding the build's SolidWorks calls rest on is read before anything is made: the check's, and the
    lock's and the rename's for a plan that locks a gear and names its mates (the review of package A)."""
    monkeypatch.setattr(findings, name, None)
    for make in (lambda fake: _build_train(fake), lambda fake: swbuild.build(fake, _train_plan(), never_exists)):
        fake = FakeSolidWorks()
        with pytest.raises(swbuild.BuildError) as raised:
            make(fake)
        assert str(raised.value) == (f"A gearbox built to turn needs findings.{name} settled on SolidWorks (it is "
                                     "None), so nothing is made or changed; run probe tier 8 first.")
        assert fake.calls == []


def test_a_train_failing_its_rebuild_is_an_ordinary_failure_and_its_mates_are_not_read():
    """The review of package A: a component that failed to rebuild could be read as a mate problem and grey Build."""
    fake = FakeSolidWorks(failed_documents=[P68])
    _, result = _build_train(fake)
    assert not result.assembly.rebuilt and not result.assembly.saved and result.kind == ""
    assert result.assembly.mate_problems == [] and "mate_states" not in names(fake)
    assert "FAIL    the rebuild reported an error" in result.assembly.log_lines()


def test_the_refused_document_left_open_does_not_trip_the_next_builds_checks():
    """W5-INTERFACES §7 A: the unsaved Assem1 a refused train leaves open has no path, so the same-name check never
    compares it, and the next Build (a new revision's paths) goes ahead."""
    fake, result = _build_train(assembly=_train_plan(follower_on_axis=True))
    assert not result.ok
    fake.open_docs.append(DocInfo("Assem1", "", 2))             # as SolidWorks lists it: open, never saved
    again = W + "T_r1.SLDASM"
    _, result = _build_train(fake, parts=[], reuse=[swbuild.DocumentValues(P17, _values(S17)),
                                                    swbuild.DocumentValues(P68, _values(S68)),
                                                    swbuild.DocumentValues(P51, _values(S51))],
                             layout=swbuild.DocumentValues(T_LAYOUT, _train_layout_values().variables,
                                                           T_LAYOUT_FEATURES),
                             assembly=_train_plan(path=again))
    assert result.ok, result.log_lines()
    assert result.assembly.saved == again and result.kind == "motion"


# -- a train's Update (W5-PLAN §1.6 as W5-INTERFACES.md §3 orders it, with review M1, M7, M8 and W5-DECISIONS)

from gear_generator.swbuild import CarrierLink, LockLink, MateRef, MeshLink  # noqa: E402

TRAIN_ORDER = ("G1", "G2", "G3", "G4")
MESHES = (MeshLink("G1", "G2", -17.0 / 68, 360.0 / 68), MeshLink("G3", "G4", -17.0 / 51, 360.0 / 51))
LOCKS = (LockLink("G2", "G3", 360.0 / 17),)
MATE_REFS = (MateRef("G1 on S1 Axis", "axis", ("G1",), "S1"), MateRef("G1 along S1", "along", ("G1",), "S1"),
             MateRef("G2 on S2 Axis", "axis", ("G2",), "S2"), MateRef("G2 along S2", "along", ("G2",), "S2"),
             MateRef("G3 locked to G2", "lock", ("G2", "G3")), MateRef("G4 on S3 Axis", "axis", ("G4",), "S3"),
             MateRef("G4 along S3", "along", ("G4",), "S3"), MateRef("G1 meshes G2", "mesh", ("G1", "G2")),
             MateRef("G3 meshes G4", "mesh", ("G3", "G4")))
W5_CALLS = ("find_mate", "mate_states", "constrained_status", "set_mate_suppressed", "set_gear_ratio")
CHANGING = ("set_global_variable", "place_component", "rebuild", "set_mate_suppressed", "set_gear_ratio", "save_as")


def _built_train(**fake_kwargs):
    """A fake SolidWorks after a clean turning build: every file saved, the gears where the build put them."""
    fake, result = _build_train(FakeSolidWorks(**fake_kwargs))
    assert result.ok, result.log_lines()
    fake.calls.clear()
    return fake


def _train_placements(frames=None):
    frames = frames or _train_frames()
    return [swbuild.Placement(g, f"gear{g[1]}-1", frames[g][0], frames[g][1], 360.0 / TEETH[g]) for g in TRAIN_ORDER]


def _motion(**kwargs):
    kwargs.setdefault("mates", MATE_REFS)
    kwargs.setdefault("meshes", MESHES)
    kwargs.setdefault("locks", LOCKS)
    kwargs.setdefault("recorded", tuple(_train_placements()))
    kwargs.setdefault("recorded_meshes", MESHES)
    kwargs.setdefault("face_globals", (("G4", GlobalVariable("G4 Face Z", "20")),))
    return swbuild.MotionUpdate(**kwargs)


def _update_train(fake, **kwargs):
    kwargs.setdefault("parts", [])
    kwargs.setdefault("layout", None)
    kwargs.setdefault("assembly", T_ASM)
    kwargs.setdefault("placements", _train_placements())
    kwargs.setdefault("motion", _motion())
    kwargs.setdefault("exists", fake.exists)
    return swbuild.update_gearbox(fake, **kwargs)


def _drag(fake, degrees):
    """The input turned ``degrees`` by a person in SolidWorks, the solver turning the rest of the train with it:
    each gear about its own +Z by its speed (k = -za/zb across an outside mesh, the same across a lock)."""
    turns = {"G1": degrees, "G2": -17.0 / 68 * degrees}
    turns["G3"] = turns["G2"]
    turns["G4"] = -17.0 / 51 * turns["G3"]
    for gear, turn in turns.items():
        fake.turn(f"gear{gear[1]}-1", turn)
    return turns


def _at_built(fake, frames=None):
    frames = frames or _train_frames()
    return all(_close(fake.frames[f"gear{g[1]}-1"], frames[g], 1e-9) for g in TRAIN_ORDER)


def test_a_train_turned_in_step_with_nothing_to_change_is_left_turned_and_nothing_is_touched():
    fake = _built_train()
    _drag(fake, 10.0)
    fake.touched.clear()
    result = _update_train(fake)
    assert result.ok, result.log_lines()
    assert result.turned and result.out_of_step == [] and result.off_axis == [] and result.restored == []
    assert result.placed == [] and result.changed == [] and not result.rebuilt and fake.touched == set()
    assert not any(n in CHANGING or n == "interferences" for n in names(fake))
    assert len(result.residuals) == 3 and all(r < 1e-9 for _, _, r in result.residuals)
    assert "ok      nothing needed putting: the gears stay turned where they stand, in step" in result.log_lines()
    assert "ok      found turned in SolidWorks, in step" in result.log_lines()


def test_a_gear_turned_out_of_step_puts_its_whole_train_back_with_its_locks_off_around_the_puts():
    fake = _built_train()
    fake.turn("gear4-1", 3.0)                          # G4 alone: out of step with G3
    result = _update_train(fake)
    assert result.ok, result.log_lines()
    assert result.out_of_step == [("G3", "G4")] and not result.turned
    assert result.placed == list(TRAIN_ORDER) and result.restored == [("G4",)]
    assert _at_built(fake) and fake.locked_puts == []
    calls = [(n, a) for n, a in fake.calls if n in ("set_mate_suppressed", "rebuild", "place_component")]
    lock = next(a[0] for n, a in fake.calls if n == "find_mate" and a[1] == "G3 locked to G2")
    assert calls[0] == ("set_mate_suppressed", (lock, True)) and calls[1][0] == "rebuild"
    assert [a[0] for n, a in calls[2:6]] == ["placed1", "placed2", "placed3", "placed4"]
    assert calls[6] == ("set_mate_suppressed", (lock, False)) and calls[7][0] == "rebuild"
    assert result.changed == [T_ASM] and not fake.mate("G3 locked to G2").suppressed
    assert "interferences" in names(fake) and set(fake.assembly_kinds) == {swcom.ASSEMBLY_TRAIN}
    assert "ok      turned back to where they were built: G4" in result.log_lines()


def test_the_one_tooth_turn_review_m1_describes_is_put_back_exactly_and_the_next_update_finds_nothing():
    """Review M1: G1 turned one tooth turns G2 exactly one of its own; G3 turns with G2, which is not a G3 pitch,
    and G4 too. When a put is needed (here S3 moves), every mated gear of the train is put — G1 and G2 too, though
    each stands a whole tooth off — so the lock holds G3 exactly where it was built against G2, and the next Update
    finds nothing out of step."""
    fake = _built_train()
    turns = _drag(fake, 360.0 / 17)
    assert turns["G2"] == pytest.approx(-360.0 / 68)
    moved = _train_frames(s3=(64.5, 51.0))
    result = _update_train(fake, layout=_train_layout_values("64.5"), placements=_train_placements(moved))
    assert result.ok, result.log_lines()
    assert result.turned and result.placed == list(TRAIN_ORDER) and result.restored == [("G3", "G4")]
    assert _at_built(fake, moved) and fake.locked_puts == []
    relative = _compose(_inverse(fake.frames["gear2-1"]), fake.frames["gear3-1"])
    assert _close(relative, _compose(_inverse(moved["G2"]), moved["G3"]))
    fake.calls.clear()
    again = _update_train(fake, layout=_train_layout_values("64.5"), placements=_train_placements(moved),
                          motion=_motion(recorded=tuple(_train_placements(moved))))
    assert again.ok and not again.turned and again.out_of_step == [] and again.placed == []
    assert "place_component" not in names(fake) and again.changed == []


def test_a_layout_move_rebuilds_then_puts_the_wrong_swing_right_and_the_post_check_is_clean():
    fake = _built_train()
    moved = _train_frames(s3=(64.5, 51.0))
    result = _update_train(fake, layout=_train_layout_values("64.5"), placements=_train_placements(moved))
    assert result.ok, result.log_lines()
    assert result.layout.changed == ["S3 X"] and result.changed == [T_LAYOUT, T_ASM]
    assert result.off_axis == [] and result.out_of_step == [] and not result.turned    # as found, before the move
    assert result.placed == list(TRAIN_ORDER) and result.restored == []
    assert _at_built(fake, moved) and fake.locked_puts == []
    called = names(fake)
    start = called.index("set_global_variable")
    assert called.index("rebuild", called.index("find_mate", start)) < called.index("place_component")
    assert [m.code for m in result.mates] == [0] * 9 and not any(m.suppressed for m in result.mates)
    assert "ok      no interference between the gears" in result.log_lines()


def test_a_face_z_change_is_set_and_rebuilt_before_any_put():
    fake = _built_train()
    fake.turn("gear4-1", 3.0)                          # so a put is needed too
    wanted = _train_frames(z4=25.0)
    result = _update_train(fake, placements=_train_placements(wanted),
                           motion=_motion(face_globals=(("G4", GlobalVariable("G4 Face Z", "25")),)))
    assert result.ok, result.log_lines()
    assert result.axial == ["G4"] and _at_built(fake, wanted)
    called = [(n, a) for n, a in fake.calls]
    set_at = called.index(("set_global_variable", ("G4 Face Z", "25")))
    first_put = next(i for i, (n, _) in enumerate(called) if n == "place_component")
    assert set_at < next(i for i, (n, _) in enumerate(called) if n == "rebuild") < first_put


def test_a_face_z_change_alone_moves_the_anchor_and_puts_its_train_back_whole():
    """The user's answer 2 (W5-DECISIONS): whenever Update moves a gear of a train — a Face Z set moves its anchor —
    the train goes back to its built turn, every mated gear of it put; nothing was turned, so nothing is restored."""
    fake = _built_train()
    wanted = _train_frames(z4=25.0)
    result = _update_train(fake, placements=_train_placements(wanted),
                           motion=_motion(face_globals=(("G4", GlobalVariable("G4 Face Z", "25")),)))
    assert result.ok and result.axial == ["G4"] and result.placed == list(TRAIN_ORDER) and result.changed == [T_ASM]
    assert result.restored == [] and _at_built(fake, wanted) and result.rebuilt and fake.locked_puts == []
    assert "ok      moved along their shafts: G4" in result.log_lines()


def test_a_turned_train_whose_anchor_update_moves_along_its_shaft_is_put_back_at_its_built_turn():
    """The demonstration's dry run (package E): the train turned in step, then G4's At changed. The Face Z set moved
    G4 and the post-check found the train in step, so nothing was put; the train must go back whole."""
    fake = _built_train()
    _drag(fake, 10.0)
    wanted = _train_frames(z4=25.0)
    result = _update_train(fake, placements=_train_placements(wanted),
                           motion=_motion(face_globals=(("G4", GlobalVariable("G4 Face Z", "25")),)))
    assert result.ok, result.log_lines()
    assert result.turned and result.axial == ["G4"] and result.placed == list(TRAIN_ORDER)
    assert result.restored == [("G1", "G2", "G3", "G4")]
    assert _at_built(fake, wanted) and fake.locked_puts == [] and not fake.mate("G3 locked to G2", T_ASM).suppressed


def test_a_mate_renamed_or_deleted_in_solidworks_is_not_as_built_and_nothing_changes():
    fake = _built_train()
    fake.drop_mate(T_ASM, "G3 meshes G4")
    with pytest.raises(swbuild.NotAsBuilt) as raised:
        _update_train(fake, layout=_train_layout_values("64.5"),
                      placements=_train_placements(_train_frames(s3=(64.5, 51.0))))
    assert str(raised.value) == ('The mate "G3 meshes G4" is not in T.SLDASM any more: it was renamed or deleted in '
                                 "SolidWorks.") and raised.value.path == T_ASM
    assert not any(n in CHANGING for n in names(fake))


def test_a_face_z_global_deleted_in_solidworks_is_not_as_built():
    fake = _built_train()
    fake.memory[_key(T_ASM)][0].clear()
    with pytest.raises(swbuild.NotAsBuilt, match='^T.SLDASM cannot be updated: "G4 Face Z" is no longer in it'):
        _update_train(fake)
    assert not any(n in CHANGING for n in names(fake))


def test_a_recorded_mate_found_suppressed_is_turned_back_on_and_listed():
    fake = _built_train()
    fake.mate("G3 locked to G2", T_ASM).suppressed = True
    result = _update_train(fake)
    assert result.ok, result.log_lines()
    assert result.unsuppressed == ["G3 locked to G2"] and not fake.mate("G3 locked to G2", T_ASM).suppressed
    assert result.changed == [T_ASM] and result.rebuilt and result.placed == []
    assert "ok      turned back on: G3 locked to G2" in result.log_lines()


def test_a_suppressed_mate_the_record_does_not_know_is_listed_and_left_alone():
    fake = _built_train()
    fake.user_mate(T_ASM, "Angle1", suppressed=True)
    result = _update_train(fake)
    assert result.ok and result.extra_mates == ["Angle1"] and fake.mate("Angle1", T_ASM).suppressed
    assert not any(n in CHANGING for n in names(fake))
    assert "CHECK   suppressed mates Gear Generator did not make, left as they are: Angle1" in result.log_lines()


def test_an_unsuppressed_mate_the_record_does_not_know_refuses_the_update_naming_it():
    """Review M7: a mate added by hand (an angle mate driving the train, say) would make every turning gear read
    fully defined and a put on it is unprobed, so the Update refuses before anything changes, naming the mate."""
    fake = _built_train()
    fake.user_mate(T_ASM, "Angle1")
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, layout=_train_layout_values("64.5"),
                      placements=_train_placements(_train_frames(s3=(64.5, 51.0))))
    assert not isinstance(raised.value, swbuild.NotAsBuilt)
    # Re-pinned at W9a's fix round (ruling 5): the sentence names the gear and the way through, a lock, which on a
    # train with no carrier goes with its gear once that branch of route (c1) is measured; re-pinned again at the
    # demonstration's ruling, which measured that branch on 2026 (findings.USER_MATE_PUT_NO_CARRIER_ON_2026 True).
    assert str(raised.value) == ("Angle1 is a mate in T.SLDASM that Gear Generator did not make, on G1, which Update "
                                 "SolidWorks puts back, and a mate of that kind is not moved with its gear, so nothing "
                                 "is changed; lock your component to G1 instead, and Update SolidWorks puts it with "
                                 "G1, or suppress Angle1 in SolidWorks, and press Update SolidWorks again.")
    assert not any(n in CHANGING for n in names(fake))


def test_a_put_that_does_not_hold_is_a_post_check_failure_sentence():
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    fake.slips = {"gear4-1"}
    result = _update_train(fake)
    assert not result.ok
    assert ("T.SLDASM", "G4 is not where Update SolidWorks put it once the assembly rebuilt: a mate holds it "
                        "elsewhere.") in result.failures
    assert ("T.SLDASM", "G3 and G4 are out of step once the assembly rebuilt.") in result.failures
    assert "interferences" not in names(fake) and result.changed == [T_ASM]


def test_a_mate_in_error_or_a_gear_not_free_after_the_update_is_a_failure_sentence():
    fake = _built_train()
    fake.mate_codes, fake.constrained = {"G1 meshes G2": (47, False)}, {"gear2-1": 3}
    fake.turn("gear4-1", 3.0)
    result = _update_train(fake)
    assert ("T.SLDASM", "The mate G1 meshes G2 is in error in SolidWorks.") in result.failures
    assert ("T.SLDASM", "G2 cannot turn: SolidWorks reads it fully defined.") in result.failures


def test_a_lone_mated_gear_is_put_only_when_off_its_axis():
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    for name in ("G1 meshes G2", "G3 meshes G4"):            # no gear mate on record: each gear turns alone
        fake.mate(name, T_ASM).suppressed = True
    unlinked = _motion(mates=tuple(m for m in MATE_REFS if m.kind != "mesh"), meshes=(), locks=(), recorded_meshes=())
    result = _update_train(fake, motion=unlinked)
    assert result.ok and result.placed == [] and "place_component" not in names(fake)


def test_a_fixed_gear_is_re_placed_as_w4_re_places_it_modulo_its_pitch():
    fake = _built_train()
    fake.turn("gear4-1", 360.0 / 51)                   # a whole tooth: the same placement
    fake.mate("G3 meshes G4", T_ASM).suppressed = True       # G4 fixed: its gear mate is not on record
    motion = _motion(mates=tuple(m for m in MATE_REFS if m.name != "G3 meshes G4"), fixed=("G4",),
                     meshes=MESHES[:1], recorded_meshes=MESHES[:1])
    result = _update_train(fake, motion=motion)
    assert result.ok and result.placed == []
    fake.turn("gear4-1", 2.0)
    result = _update_train(fake, motion=motion)
    assert result.ok and result.placed == ["G4"]
    assert [a[0] for n, a in fake.calls if n == "place_component"] == ["placed4"]


def test_a_static_gearbox_update_never_reaches_a_w5_member():
    fake = _built_gearbox()
    result = _update(fake)
    assert result.ok and not any(n in W5_CALLS for n in names(fake))
    assert result.turned is False and result.restored == [] and result.mates == []


@pytest.mark.parametrize("name, value, sentence", [
    ("MESH_PHASE_ROUTE", None, "Update SolidWorks on a gearbox built to turn needs putting a gear with its gear mate "
                               "on settled on SolidWorks (findings.MESH_PHASE_ROUTE is None), so nothing is changed; "
                               "run probe tier 8 first."),
    ("LOCK_UNSUPPRESS_KEEPS_THE_NEW_ANGLE", False, "Update SolidWorks on a gearbox built to turn needs a lock keeping "
                                                   "the angle a gear was put at settled on SolidWorks (findings."
                                                   "LOCK_UNSUPPRESS_KEEPS_THE_NEW_ANGLE is False), so nothing is "
                                                   "changed; run probe tier 8 first."),
])
def test_a_motion_update_without_its_findings_is_refused_before_anything_is_read(monkeypatch, name, value, sentence):
    monkeypatch.setattr(findings, name, value)
    fake = _built_train()
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake)
    assert str(raised.value) == sentence and fake.calls == []


@pytest.mark.parametrize("name, ratios", [("FEATURE_SUPPRESS", False), ("FEATURE_UNSUPPRESS", False),
                                          ("THIS_CONFIGURATION", False), ("GEAR_MATE_RATIO_REMAKE_WORKS", True),
                                          ("MATE_DELETE_ROUTE", True), ("MATE_RENAME_ROUTE", True),
                                          ("GEAR_MATE_FLIP", True), ("GEAR_MATE_ROUTE", True), ("MATE_GEAR", True),
                                          ("GEAR_MATE_NUMERATOR_FIRST", True)])
def test_every_finding_the_motion_update_calls_need_is_read_before_anything_is_read(monkeypatch, name, ratios):
    """A missing FEATURE_UNSUPPRESS would suppress the locks and then refuse to turn them back on: read first."""
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    fake = _built_train()
    monkeypatch.setattr(findings, name, None)
    with pytest.raises(swbuild.BuildError, match=rf"findings.{name} .*None\), so nothing is (made or )?changed; run "
                                                 "probe tier 8 first"):
        _update_train(fake, motion=_motion(ratios=(("G3 meshes G4", 18, 50),) if ratios else ()))
    assert fake.calls == []


def test_a_new_ratio_is_refused_before_anything_changes_while_the_route_is_not_the_remake(monkeypatch):
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
    fake = _built_train()
    with pytest.raises(swbuild.BuildError, match=r"findings.GEAR_MATE_RATIO_ROUTE is None\), so nothing is changed"):
        _update_train(fake, motion=_motion(ratios=(("G3 meshes G4", 18, 50),)))
    assert fake.calls == []


def test_with_the_remake_a_new_ratio_is_set_with_the_locks_off_before_the_train_is_put(monkeypatch):
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    fake = _built_train()
    result = _update_train(fake, motion=_motion(ratios=(("G3 meshes G4", 18, 50),)))
    assert result.ok, result.log_lines()
    assert result.ratios == ["G3 meshes G4"] and result.placed == list(TRAIN_ORDER)
    assert result.ratios_read == [("G3 meshes G4", 17, 51, 18, 50)] and result.ratios_found == []
    called = [(n, a) for n, a in fake.calls]
    ratio_at = next(i for i, (n, _) in enumerate(called) if n == "set_gear_ratio")
    assert called[ratio_at][1][1:] == ("placed3:Gear Axis", "placed4:Gear Axis", (18, 50))
    suppress_at = next(i for i, (n, a) in enumerate(called) if n == "set_mate_suppressed" and a[1] is True)
    assert suppress_at < ratio_at < next(i for i, (n, _) in enumerate(called) if n == "place_component")
    assert fake.mate("G3 meshes G4", T_ASM).ratio == (18.0, 50.0) and fake.locked_puts == []


def test_a_lock_that_will_not_come_back_on_names_the_compound_gears_and_stops():
    """Review M8: the locks are turned back on whatever happened; one that will not is a failure saying which
    compound gears are not locked, and the next Update turns it back on (D10)."""
    fake = _built_train(fail_on={"set_mate_suppressed": (False, "SolidWorks would not turn the mate G3 locked to G2 "
                                                                "back on in T.SLDASM: it still reads it suppressed.")})
    fake.turn("gear4-1", 3.0)
    result = _update_train(fake)
    assert not result.ok
    assert result.failures == [("T.SLDASM", "The compound gears G2 and G3 are not locked: SolidWorks would not turn "
                                            "G3 locked to G2 back on (SolidWorks would not turn the mate G3 locked to "
                                            "G2 back on in T.SLDASM: it still reads it suppressed); press Update "
                                            "SolidWorks again, which turns it back on.")]
    assert result.placed == list(TRAIN_ORDER) and result.changed == [T_ASM]
    assert "interferences" not in names(fake) and fake.mate("G3 locked to G2", T_ASM).suppressed
    fake.fail_on = {}
    fake.calls.clear()
    healed = _update_train(fake)
    assert healed.ok and healed.unsuppressed == ["G3 locked to G2"]


def test_a_put_that_raises_still_turns_the_locks_back_on_and_is_a_failure():
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    fake.raises = {"place_component": (fake.counts["place_component"] + 2, RPC)}
    result = _update_train(fake)
    assert not result.ok and result.failures[0][0] == "T.SLDASM"
    assert result.failures[0][1].startswith("it stopped on an unexpected ComErrorLookAlike")
    assert result.placed == ["G1"] and not fake.mate("G3 locked to G2", T_ASM).suppressed
    called = [(n, a) for n, a in fake.calls]
    assert called.index(("set_mate_suppressed", ("mate5", False))) > next(
        i for i, (n, _) in enumerate(called) if n == "place_component")
    assert result.changed == [T_ASM]


@pytest.mark.parametrize("call", ["set_mate_suppressed", "set_global_variable", "rebuild", "component_frame"])
def test_every_raise_after_the_check_phase_is_a_failure_on_the_result(call):
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    fake.mate("G4 along S3", T_ASM).suppressed = True
    before = fake.counts.get(call, 0)
    fake.raises = {call: (before + (1 if call != "component_frame" else 5), RPC)}
    result = _update_train(fake, motion=_motion(face_globals=(("G4", GlobalVariable("G4 Face Z", "20.5")),)),
                           placements=_train_placements(_train_frames(z4=20.5)))
    assert not result.ok and any("ComErrorLookAlike" in why for _, why in result.failures)
    assert not any(m.suppressed and m.kind == "lock" for m in fake.memory_mates[_key(T_ASM)])


def test_app_code_never_puts_a_gear_while_its_lock_is_on():
    """W5-DECISIONS: a lock does not hold against a put, and SolidWorks says nothing, so the fake records every put
    made with a lock on (it would catch one: the first half) and no Update makes one (the second)."""
    fake = _built_train()
    _reopened_train(fake)
    fake.place_component("placed3", *_train_frames()["G3"], kind=swcom.ASSEMBLY_TRAIN)
    assert fake.locked_puts == ["gear3-1"]
    for doctor, kwargs in ((lambda f: f.turn("gear4-1", 3.0), {}),
                           (lambda f: _drag(f, 360.0 / 17), {"layout": _train_layout_values("64.5"),
                                                             "placements": _train_placements(
                                                                 _train_frames(s3=(64.5, 51.0)))}),
                           (lambda f: f.turn("gear3-1", 4.0), {})):
        fake = _built_train()
        doctor(fake)
        result = _update_train(fake, **kwargs)
        assert result.ok and result.placed == list(TRAIN_ORDER), result.log_lines()
        assert fake.locked_puts == []


# -- the review of package A: locks never left off unsaid, the assembly always listed once asked to change, folders


def test_a_lock_whose_suppression_took_before_the_call_raised_is_turned_back_on():
    """Must-fix 1: SetSuppression2 took and the read-back raised, so the lock was off without being counted."""
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    fake.raises_after = {"set_mate_suppressed": (1, RPC)}
    result = _update_train(fake)
    assert not result.ok and result.failures[0][1].startswith("it stopped on an unexpected ComErrorLookAlike")
    assert not fake.mate("G3 locked to G2", T_ASM).suppressed and result.placed == []
    assert ("set_mate_suppressed", ("mate5", False)) in fake.calls and result.changed == [T_ASM]


def test_a_lock_that_reads_not_suppressed_is_never_unsuppressed():
    """Unsuppressing a lock that is on is not probed: a lock whose suppression never took is read, and skipped."""
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    fake.raises = {"set_mate_suppressed": (fake.counts.get("set_mate_suppressed", 0) + 1, RPC)}   # before it took
    result = _update_train(fake)
    assert not result.ok and not fake.mate("G3 locked to G2", T_ASM).suppressed
    assert [a for n, a in fake.calls if n == "set_mate_suppressed"] == [("mate5", True)]
    assert result.changed == [T_ASM]                  # a suppression was asked of it: SolidWorks marks it


def _fail_rebuild(fake, nth):
    """The nth rebuild() from now returns False."""
    real, count = fake.rebuild, [0]

    def rebuild(kind=None):
        count[0] += 1
        done = real(kind)
        return False if count[0] == nth else done
    fake.rebuild = rebuild


def test_a_rebuild_failing_right_after_the_locks_are_suppressed_turns_them_back_on_and_lists_the_assembly():
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    _fail_rebuild(fake, 1)
    result = _update_train(fake)
    assert result.failures == [("T.SLDASM", "SolidWorks reported an error rebuilding T.")]
    assert result.placed == [] and not fake.mate("G3 locked to G2", T_ASM).suppressed
    assert result.changed == [T_ASM] and fake.locked_puts == []


def test_a_rebuild_failing_after_the_suppression_with_a_lock_that_will_not_come_back_says_so():
    fake = _built_train(fail_on={"set_mate_suppressed": (False, "SolidWorks would not turn the mate G3 locked to G2 "
                                                                "back on in T.SLDASM: it still reads it suppressed.")})
    fake.turn("gear4-1", 3.0)
    _fail_rebuild(fake, 1)
    result = _update_train(fake)
    assert result.failures[0] == ("T.SLDASM", "The compound gears G2 and G3 are not locked: SolidWorks would not turn "
                                              "G3 locked to G2 back on (SolidWorks would not turn the mate G3 locked "
                                              "to G2 back on in T.SLDASM: it still reads it suppressed); press Update "
                                              "SolidWorks again, which turns it back on.")
    assert ("T.SLDASM", "SolidWorks reported an error rebuilding T.") in result.failures
    assert result.changed == [T_ASM]


def test_a_first_put_that_raises_still_lists_the_assembly_as_changed():
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    fake.raises = {"place_component": (fake.counts["place_component"] + 1, RPC)}
    result = _update_train(fake)
    assert not result.ok and result.placed == [] and result.changed == [T_ASM]
    assert not fake.mate("G3 locked to G2", T_ASM).suppressed


@pytest.mark.parametrize("refused", [True, False])
def test_a_remake_that_fails_still_lists_the_assembly_as_changed(monkeypatch, refused):
    """A refusal is a MateRefused, a COM or selection failure an ordinary one (Build stays enabled): either way the
    gear mate was deleted, so the assembly is changed and listed."""
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", "remake")
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_REMAKE_WORKS", True)
    fake = _built_train()
    lost = (swcom.MateRefused if refused else SolidWorksError)(
        "The open T.SLDASM has lost the gear mate G3 meshes G4: it was deleted to give it its new ratio, and making "
        "it again stopped. The saved T.SLDASM still has it: close T.SLDASM in SolidWorks without saving to bring it "
        "back. SolidWorks did not complete AddMate5: The remote procedure call failed (RPC_S_CALL_FAILED).")
    fake.raises = {"set_gear_ratio": (1, lost)}
    result = _update_train(fake, motion=_motion(ratios=(("G3 meshes G4", 18, 50),)))
    assert result.failures[0] == ("T.SLDASM", str(lost)) and result.ratios == [] and result.changed == [T_ASM]
    assert not fake.mate("G3 locked to G2", T_ASM).suppressed


def test_an_entry_among_the_mates_that_is_neither_a_mate_nor_a_folder_refuses_the_update(monkeypatch):
    monkeypatch.setattr(findings, "MATE_FOLDER_TYPE_NAME", "FtrFolder")
    monkeypatch.setattr(findings, "MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER", True)
    fake = _built_train()
    fake.user_entry(T_ASM, "Train mates", "SomethingNew")
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, layout=_train_layout_values("64.5"),
                      placements=_train_placements(_train_frames(s3=(64.5, 51.0))))
    assert not isinstance(raised.value, swbuild.NotAsBuilt)
    assert str(raised.value) == ('T.SLDASM holds "Train mates" among its mates, which is not a mate, and how Update '
                                 "SolidWorks would read it (a folder of mates, say) has not been settled, so nothing is "
                                 'changed; move the mates out of "Train mates" in SolidWorks (or delete it if empty) '
                                 "and press Update SolidWorks again.")
    assert not any(n in CHANGING for n in names(fake))


@pytest.mark.parametrize("missing", ["MATE_FOLDER_TYPE_NAME", "MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER"])
def test_without_a_folder_finding_a_folder_among_the_mates_refuses_as_before(monkeypatch, missing):
    """Skipping a folder is safe only because the walk still sees the mates in it: either finding missing, refused."""
    monkeypatch.setattr(findings, "MATE_FOLDER_TYPE_NAME", "FtrFolder")
    monkeypatch.setattr(findings, "MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER", True)
    monkeypatch.setattr(findings, missing, None)
    fake = _built_train()
    fake.user_folder(T_ASM, "Folder1")
    with pytest.raises(swbuild.BuildError, match='^T.SLDASM holds "Folder1", "Folder1___EndTag___" among its mates, '
                                                 "which are not mates"):
        _update_train(fake)
    assert not any(n in CHANGING for n in names(fake))


def test_gear_mates_in_a_folder_are_found_read_and_remade_and_the_update_goes_ahead(monkeypatch, remake_route):
    """Probe round P0c, mate_folders: a folder's two "FtrFolder" entries are skipped and the mates in it are read and
    found as any other. A gear mate remade lands at the end of the mate group, outside the folder: left so, since no
    probe covers putting it back."""
    monkeypatch.setattr(findings, "MATE_FOLDER_TYPE_NAME", "FtrFolder")
    monkeypatch.setattr(findings, "MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER", True)
    fake = _built_train()
    fake.user_folder(T_ASM, "Folder1")
    _drag(fake, 10.0)
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=(("G1 meshes G2", 17, 69),)))
    assert result.ok, result.log_lines()
    assert result.ratios == ["G1 meshes G2"] and result.placed == list(TRAIN_ORDER) and result.extra_mates == []
    assert fake.mate("G1 meshes G2", T_ASM).ratio == (17.0, 69.0) and fake.mates[-1].name == "G1 meshes G2"
    assert fake.locked_puts == [] and not fake.mate("G3 locked to G2", T_ASM).suppressed


def test_a_recorded_mate_deleted_beside_a_folder_still_reads_renamed_or_deleted():
    fake = _built_train()
    fake.drop_mate(T_ASM, "G1 meshes G2")
    fake.user_folder(T_ASM, "Train mates")
    with pytest.raises(swbuild.NotAsBuilt, match='^The mate "G1 meshes G2" is not in T.SLDASM any more: it was '
                                                 "renamed or deleted in SolidWorks.$"):
        _update_train(fake)


# Two trains: the 12 : 1 reducer above, and a second one like it on S4–S6, 100 mm below.

def _two_train_layout(path=T_LAYOUT):
    steps = list(_train_layout_plan(path).ops[:-2])
    steps[4:4] = [ops.AddGlobal("S4 Y", "-100"), ops.AddGlobal("S5 X", "63.75"), ops.AddGlobal("S5 Y", "-100"),
                  ops.AddGlobal("S6 X", "63.75"), ops.AddGlobal("S6 Y", "-49")]
    steps += [ops.RefPlane("y4", "S4 Y Plane", 2, -100.0), ops.RefPlane("y6", "S6 Y Plane", 2, -49.0),
              ops.Axis("axis4", "S4 Axis", (3, "y4")), ops.Axis("axis5", "S5 Axis", ("x2", "y4")),
              ops.Axis("axis6", "S6 Axis", ("x3", "y6")), ops.Rebuild(), ops.SaveAs(path)]
    return BuildPlan("layout", "", tuple(steps), path)


SECOND = {"G5": ("gear5", P17, "S4", (0.0, -100.0, 0.0), 0.0), "G6": ("gear6", P68, "S5", (63.75, -100.0, 0.0),
                                                                       180.0 / 68),
          "G7": ("gear7", P17, "S5", (63.75, -100.0, 20.0), 0.0), "G8": ("gear8", P51, "S6", (63.75, -49.0, 0.0),
                                                                          180.0 / 51)}


def _two_train_plan(path=T_ASM):
    first = list(_train_plan(path).ops[:-2])
    adds, mates = [], []
    for gear, (h, part, shaft, at, theta) in SECOND.items():
        adds += [ops.AddComponent(h, part, at), ops.Place(h, _rot_z(theta), at), ops.Fix(h)]
    for gear in ("G5", "G6", "G8"):
        h, _, shaft, _, _ = SECOND[gear]
        mates += [ops.Unfix(h), ops.Mate(f"axis{gear}", "coincident", f"{h}:Gear Axis", f"layout:{shaft} Axis",
                                         name=f"{gear} on {shaft} Axis"),
                  ops.Mate(f"along{gear}", "point", f"{h}:origin", "layout:plane1", name=f"{gear} along {shaft}")]
    mates += [ops.Unfix("gear7"), ops.Mate("lock2", "lock", "gear6", "gear7", name="G7 locked to G6"),
              ops.Mate("mesh5", "gear", "gear5:Gear Axis", "gear6:Gear Axis", name="G5 meshes G6", ratio=(17.0, 68.0)),
              ops.Mate("mesh7", "gear", "gear7:Gear Axis", "gear8:Gear Axis", name="G7 meshes G8", ratio=(17.0, 51.0))]
    cut = next(i for i, op in enumerate(first) if isinstance(op, ops.Unfix))
    steps = first[:cut] + adds + first[cut:] + mates + [ops.Rebuild(), ops.SaveAs(path)]
    return BuildPlan("gearbox", "", tuple(steps), path)


def test_with_two_trains_only_the_one_that_needs_a_put_is_touched():
    gears = dict(TRAIN_GEARS, **{h: g for g, (h, *_rest) in SECOND.items()})
    fake, result = _build_train(layout=_two_train_layout(), assembly=_two_train_plan(), gears=gears)
    assert result.ok, result.log_lines()
    fake.calls.clear()
    frames = dict(_train_frames(), **{g: (_rot_z(theta), at) for g, (_, _, _, at, theta) in SECOND.items()})
    placements = [swbuild.Placement(g, f"gear{g[1]}-1", frames[g][0], frames[g][1], 360.0 / t)
                  for g, t in dict(TEETH, G5=17, G6=68, G7=17, G8=51).items()]
    second_meshes = (MeshLink("G5", "G6", -17.0 / 68, 360.0 / 68), MeshLink("G7", "G8", -17.0 / 51, 360.0 / 51))
    second_mates = tuple(MateRef(f"{g} {how} {SECOND[g][2]}{' Axis' if how == 'on' else ''}",
                                 "axis" if how == "on" else "along", (g,), SECOND[g][2])
                         for g in ("G5", "G6", "G8") for how in ("on", "along")) + (
                    MateRef("G7 locked to G6", "lock", ("G6", "G7")), MateRef("G5 meshes G6", "mesh", ("G5", "G6")),
                    MateRef("G7 meshes G8", "mesh", ("G7", "G8")))
    motion = _motion(mates=MATE_REFS + second_mates, meshes=MESHES + second_meshes,
                     locks=LOCKS + (LockLink("G6", "G7", 360.0 / 17),), recorded=tuple(placements),
                     recorded_meshes=MESHES + second_meshes)
    _drag(fake, 10.0)                                  # the first train turned in step: left alone
    fake.turn("gear8-1", 3.0)                          # the second out of step: put back
    second_before = {g: fake.frames[f"gear{g[1]}-1"] for g in TRAIN_ORDER}
    result = _update_train(fake, placements=placements, motion=motion)
    assert result.ok, result.log_lines()
    assert result.placed == ["G5", "G6", "G7", "G8"] and result.restored == [("G8",)]
    lock = next(a[0] for n, a in fake.calls if n == "find_mate" and a[1] == "G7 locked to G6")
    assert [a[0] for n, a in fake.calls if n == "set_mate_suppressed"] == [lock, lock]      # only the second's lock
    assert {g: fake.frames[f"gear{g[1]}-1"] for g in TRAIN_ORDER} == second_before          # the first untouched
    assert all(_close(fake.frames[f"gear{g[1]}-1"], frames[g]) for g in ("G5", "G6", "G7", "G8"))
    assert fake.locked_puts == []



# -- probe round P0b: the route a train may be BUILT under, beside the one a built train re-solves under -------------

@pytest.fixture
def train_routes(monkeypatch):
    """Both of a train's rebuild findings set here, whatever findings.py holds."""
    def set_routes(built, solved):
        monkeypatch.setattr(findings, "MATED_BUILD_REBUILD_ROUTE", built, raising=False)
        monkeypatch.setattr(findings, "MATED_ASSEMBLY_REBUILD_ROUTE", solved, raising=False)
    return set_routes


@pytest.mark.parametrize("route, call", [("ForceRebuild3(True)", TOP_CALL), ("ForceRebuild3(False)", FULL_CALL)])
def test_a_train_builds_when_its_build_route_is_the_one_it_rebuilds_under(train_routes, route, call):
    train_routes(route, route)
    fake, result = _build_train()
    assert result.ok and result.kind == "motion", result.log_lines()
    assert fake.assembly_kinds and set(fake.assembly_kinds) == {TRAIN}
    assert fake.rebuild_members[-1] == call


@pytest.mark.parametrize("built, solved, sentence", [
    (None, "ForceRebuild3(True)",
     "How a gearbox built to turn may be rebuilt while it is built has not been settled on SolidWorks "
     "(findings.MATED_BUILD_REBUILD_ROUTE is None, and findings.MATED_ASSEMBLY_REBUILD_ROUTE is 'ForceRebuild3(True)'), "
     "so nothing is made or changed; run probe tier 8 first."),
    ("ForceRebuild3(True)", "ForceRebuild3(False)",
     "A gearbox built to turn would be built under findings.MATED_BUILD_REBUILD_ROUTE 'ForceRebuild3(True)', but Gear "
     "Generator rebuilds a train under findings.MATED_ASSEMBLY_REBUILD_ROUTE 'ForceRebuild3(False)', and the two "
     "differ, so nothing is made or changed; run probe tier 8 again."),
])
def test_a_train_build_is_refused_before_anything_is_made_while_its_build_route_is_unsettled_or_differs(
        train_routes, built, solved, sentence):
    train_routes(built, solved)
    for make in (lambda fake: _build_train(fake), lambda fake: swbuild.build(fake, _train_plan(), never_exists)):
        fake = FakeSolidWorks()
        with pytest.raises(swbuild.BuildError) as raised:
            make(fake)
        assert str(raised.value) == sentence
        assert fake.calls == [] and fake.saved == {}


def test_an_update_is_not_gated_on_the_build_route(train_routes):
    train_routes("ForceRebuild3(True)", "ForceRebuild3(True)")
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    train_routes(None, "ForceRebuild3(True)")
    result = _update_train(fake)
    assert result.ok and result.placed == list(TRAIN_ORDER), result.log_lines()


def test_a_static_gearbox_is_not_gated_on_the_build_route(train_routes):
    train_routes(None, None)
    _, result = _build()
    assert result.ok and result.kind == "static"


# -- the gear mates judged live (the demonstration's dry runs m5 and a3, package E)

MESHES_69 = (MeshLink("G1", "G2", -17.0 / 69, 360.0 / 69), MESHES[1])


@pytest.fixture
def remake_route(monkeypatch):
    for name, value in (("GEAR_MATE_RATIO_ROUTE", "remake"), ("GEAR_MATE_RATIO_REMAKE_WORKS", True),
                        ("GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", True)):
        monkeypatch.setattr(findings, name, value)


def _remade_then_lost(fake):
    """G2 68 → 69 carried by Update (the remake to 17 : 69), then SolidWorks closed without saving: the reopened
    assembly holds 17 : 68 again whatever the record says."""
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=(("G1 meshes G2", 17, 69),)))
    assert result.ok and result.ratios == ["G1 meshes G2"], result.log_lines()
    assert fake.mate("G1 meshes G2", T_ASM).ratio == (17.0, 69.0) and fake.definition("G1 meshes G2", T_ASM) == (69, 17)
    fake.close_all()
    fake.calls.clear()
    fake.open_document(T_ASM)
    assert fake.mate("G1 meshes G2").ratio == (17.0, 68.0)                     # the remake was not saved


def test_a_gear_mate_found_at_another_ratio_though_none_was_asked_is_remade_once_and_its_train_put(remake_route):
    """m5: the record already says 17 : 69, so the plan asks no ratio; the live gear mate is 17 : 68."""
    fake = _built_train()
    _remade_then_lost(fake)
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, recorded_meshes=MESHES_69))
    assert result.ok, result.log_lines()
    assert result.ratios == ["G1 meshes G2"] and result.ratios_found == ["G1 meshes G2"] and result.ratios_already == []
    assert result.ratios_read == [("G1 meshes G2", 17, 68, 17, 69)]
    assert [a[0] for n, a in fake.calls if n == "set_gear_ratio"] == ["mate8"]       # exactly one remake
    assert fake.mate("G1 meshes G2", T_ASM).ratio == (17.0, 69.0)
    assert result.placed == list(TRAIN_ORDER) and fake.locked_puts == []
    assert not fake.mate("G3 locked to G2", T_ASM).suppressed and result.changed == [T_ASM]
    assert ("ok      found in SolidWorks at another ratio than the workbook's, and remade: G1 meshes G2"
            in result.log_lines())


def test_a_gear_mate_asked_to_change_but_already_at_the_wanted_ratio_is_not_remade(remake_route):
    """a3: after the same loss the user types the edit back (69 → 68); the record says 17 : 69 so the plan asks for
    17 : 68, which the reopened gear mate already is."""
    fake = _built_train()
    _remade_then_lost(fake)
    result = _update_train(fake, motion=_motion(meshes=MESHES, recorded_meshes=MESHES_69,
                                                ratios=(("G1 meshes G2", 17, 68),)))
    assert result.ok, result.log_lines()
    assert result.ratios == [] and result.ratios_found == [] and result.ratios_already == ["G1 meshes G2"]
    assert result.ratios_read == [("G1 meshes G2", 17, 68, 17, 68)]
    assert "set_gear_ratio" not in names(fake) and fake.mate("G1 meshes G2", T_ASM).ratio == (17.0, 68.0)
    assert result.placed == [] and fake.locked_puts == []
    assert "ok      already at the ratio the workbook asks, so not remade: G1 meshes G2" in result.log_lines()


def test_a_gear_mate_at_another_ratio_is_refused_before_anything_changes_while_the_route_is_not_the_remake(
        remake_route, monkeypatch):
    fake = _built_train()
    _remade_then_lost(fake)
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, motion=_motion(meshes=MESHES_69, recorded_meshes=MESHES_69))
    assert str(raised.value) == ("The gear mate G1 meshes G2 in T.SLDASM is at 17 : 68 and the workbook wants 17 : 69, "
                                 "and giving a gear mate a new ratio has not been settled on SolidWorks "
                                 "(findings.GEAR_MATE_RATIO_ROUTE is None), so nothing is changed; build the gearbox "
                                 "again.")
    assert not any(n in CHANGING for n in names(fake))


def test_every_gear_mate_is_read_live_in_the_check_phase_before_anything_changes(remake_route):
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    _update_train(fake)
    called = names(fake)
    reads = [i for i, n in enumerate(called) if n == "gear_mate_ratio"]
    assert len(reads) == 2 and max(reads) < min(i for i, n in enumerate(called) if n in CHANGING)


def test_without_the_definition_finding_a_motion_update_is_refused_before_anything_is_read(remake_route, monkeypatch):
    fake = _built_train()
    monkeypatch.setattr(findings, "GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND", None)
    with pytest.raises(swbuild.BuildError, match=r"GEAR_MATE_DEFINITION_READS_NUMERATOR_SECOND is None\), so nothing"):
        _update_train(fake)
    assert fake.calls == []


def test_a_gear_mate_on_record_with_no_mesh_in_the_plan_is_refused_before_anything_is_read():
    fake = _built_train()
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, motion=_motion(meshes=MESHES[:1], recorded_meshes=MESHES[:1]))
    assert str(raised.value) == ("Update SolidWorks was given the gear mate G3 meshes G4 on record with no mesh between "
                                 "G3 and G4 to say the ratio the workbook wants, so the record and the plan disagree "
                                 "about it and nothing is changed; that is a fault in Gear Generator, not in "
                                 "SolidWorks.")
    assert fake.calls == []


@pytest.mark.parametrize("name", ["GEAR_MATE_RATIO_REMAKE_WORKS", "MATE_DELETE_ROUTE", "GEAR_MATE_FLIP"])
def test_a_remake_found_live_is_refused_before_anything_changes_while_a_remake_finding_is_missing(
        remake_route, monkeypatch, name):
    """The m5 path: the plan asks no ratio, so the early gate reads no remake finding; the live mismatch found in the
    check phase reads them all (_remake_gate) before anything changes."""
    fake = _built_train()
    _remade_then_lost(fake)
    monkeypatch.setattr(findings, name, None)
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, motion=_motion(meshes=MESHES_69, recorded_meshes=MESHES_69))
    assert f"(findings.{name} is None), so nothing is changed; run probe tier 8 first." in str(raised.value)
    assert "gear_mate_ratio" in names(fake) and not any(n in CHANGING for n in names(fake))
    assert fake.mate("G1 meshes G2", T_ASM).ratio == (17.0, 68.0)



# -- probe round P0c's findings in the gates

def test_an_update_does_not_need_the_build_only_findings(monkeypatch):
    """Mates made under CommandInProgress and renamed at once in an unsaved assembly are a Build's doing."""
    fake = _built_train()
    for name in ("MATES_UNDER_COMMAND_IN_PROGRESS", "MATE_RENAME_AT_ONCE"):
        monkeypatch.setattr(findings, name, None)
    fake.turn("gear4-1", 3.0)
    assert _update_train(fake).ok


@pytest.mark.parametrize("value", [None, "the assembly"])
def test_an_update_whose_ratio_read_may_mark_the_assembly_is_refused_before_anything_is_read(monkeypatch, value):
    fake = _built_train()
    monkeypatch.setattr(findings, "GEAR_MATE_DEFINITION_READ_MARKS", value)
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake)
    assert str(raised.value) == ("Update SolidWorks on a gearbox built to turn needs reading a gear mate's ratio without "
                                 "marking the assembly settled on SolidWorks (findings.GEAR_MATE_DEFINITION_READ_MARKS "
                                 f"is {value!r}), so nothing is changed; run probe tier 8 first.")
    assert fake.calls == []


def test_a_remake_on_a_gear_carrying_two_gear_mates_needs_the_idler_finding(monkeypatch):
    idler = _motion(mates=MATE_REFS + (MateRef("G2 meshes G4", "mesh", ("G2", "G4")),))
    monkeypatch.setattr(findings, "IDLER_UPDATE_HOLDS", None)
    with pytest.raises(swbuild.BuildError) as raised:
        swbuild._idler_gate(idler, [("G1 meshes G2", 17, 69)])
    assert str(raised.value) == ("Giving a new ratio to a gear mate of G2, which carries two gear mates, has not been "
                                 "settled on SolidWorks (findings.IDLER_UPDATE_HOLDS is None), so nothing is changed; "
                                 "run probe tier 8 first, or build the gearbox again.")
    swbuild._idler_gate(_motion(), [("G1 meshes G2", 17, 69)])            # the 12 : 1: no gear carries two
    monkeypatch.setattr(findings, "IDLER_UPDATE_HOLDS", True)
    swbuild._idler_gate(idler, [("G1 meshes G2", 17, 69)])


def test_the_twelve_to_one_remake_does_not_read_the_idler_finding(monkeypatch, remake_route):
    monkeypatch.setattr(findings, "IDLER_UPDATE_HOLDS", None)
    fake = _built_train()
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=(("G1 meshes G2", 17, 69),)))
    assert result.ok and result.ratios == ["G1 meshes G2"], result.log_lines()



# -- lightweight gears (P0c drove a lightweight train and a gear turned wrongly; the read is probe round P0d's)

@pytest.fixture
def resolved_read(monkeypatch):
    """The read P0d settles, set here under swcom's placeholder names (renamed in one place once it is committed)."""
    monkeypatch.setattr(findings, swcom.RESOLVED_ROUTE_FINDING, "GetSuppression2", raising=False)
    monkeypatch.setattr(findings, swcom.RESOLVED_VALUES_FINDING, (2,), raising=False)


def test_a_lightweight_gear_refuses_a_turning_update_before_anything_changes(resolved_read):
    fake = _built_train()
    fake.lightweight = {"gear3-1"}
    fake.turn("gear4-1", 3.0)
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake)
    assert not isinstance(raised.value, swbuild.NotAsBuilt)
    assert str(raised.value) == ("G3 (gear3-1) is not fully resolved in T.SLDASM: SolidWorks loaded it lightweight, and "
                                 "a train with a lightweight gear does not turn as it was built, so nothing is changed; "
                                 "in SolidWorks, right-click T.SLDASM and choose Set Lightweight to Resolved, then press "
                                 "Update SolidWorks again.")
    assert not any(n in CHANGING for n in names(fake))


def test_every_gear_resolved_the_turning_update_goes_on_as_before(resolved_read):
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    result = _update_train(fake)
    assert result.ok and result.placed == list(TRAIN_ORDER), result.log_lines()
    assert [a[0] for n, a in fake.calls if n == "component_resolved"] == ["placed1", "placed2", "placed3", "placed4"]


def test_without_the_resolved_read_the_update_reads_nothing_new_and_goes_on_as_today(monkeypatch):
    monkeypatch.setattr(findings, swcom.RESOLVED_ROUTE_FINDING, None, raising=False)
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    assert _update_train(fake).ok and "component_resolved" not in names(fake)
    fake.lightweight = {"gear3-1"}                        # find_component's own check, as today
    with pytest.raises(swbuild.BuildError, match="^gear3-1 is loaded lightweight in T.SLDASM"):
        _update_train(fake)



# -- an idler through Update: a gear carrying two recorded gear mates (probe round P0c, idler_update)

IDLER_REF = MateRef("G2 meshes G4", "mesh", ("G2", "G4"))


def _idler_motion(teeth4, ratios):
    meshes = (MESHES[0], MeshLink("G3", "G4", -17.0 / teeth4, 360.0 / teeth4),
              MeshLink("G2", "G4", -68.0 / teeth4, 360.0 / teeth4))
    recorded = (MESHES[0], MESHES[1], MeshLink("G2", "G4", -68.0 / 51, 360.0 / 51))
    return _motion(mates=MATE_REFS + (IDLER_REF,), meshes=meshes, recorded_meshes=recorded, ratios=ratios)


def _built_idler():
    fake, result = _build_train(assembly=_train_plan(idler=True))
    assert result.ok, result.log_lines()
    fake.calls.clear()
    return fake


def test_a_remake_on_an_idler_is_refused_through_update_while_its_finding_is_missing(remake_route, monkeypatch):
    monkeypatch.setattr(findings, "IDLER_UPDATE_HOLDS", None)
    fake = _built_idler()
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, motion=_idler_motion(51, (("G3 meshes G4", 17, 50),)))
    assert str(raised.value) == ("Giving a new ratio to a gear mate of G4, which carries two gear mates, has not been "
                                 "settled on SolidWorks (findings.IDLER_UPDATE_HOLDS is None), so nothing is changed; "
                                 "run probe tier 8 first, or build the gearbox again.")
    assert not any(n in CHANGING for n in names(fake))         # nothing suppressed, set, remade or put
    assert fake.mate("G3 meshes G4", T_ASM).ratio == (17.0, 51.0)


def test_with_the_idler_finding_both_of_an_idlers_gear_mates_are_remade(remake_route, monkeypatch):
    monkeypatch.setattr(findings, "IDLER_UPDATE_HOLDS", True)
    fake = _built_idler()
    result = _update_train(fake, motion=_idler_motion(50, (("G3 meshes G4", 17, 50), ("G2 meshes G4", 68, 50))))
    assert result.ok, result.log_lines()
    assert sorted(result.ratios) == ["G2 meshes G4", "G3 meshes G4"]
    assert len([n for n in names(fake) if n == "set_gear_ratio"]) == 2
    assert fake.mate("G3 meshes G4", T_ASM).ratio == (17.0, 50.0)
    assert fake.mate("G2 meshes G4", T_ASM).ratio == (68.0, 50.0)
    assert result.placed == list(TRAIN_ORDER) and fake.locked_puts == []
    assert not fake.mate("G3 locked to G2", T_ASM).suppressed



def test_a_recorded_mate_that_stays_suppressed_after_it_is_turned_back_on_stops_the_update_naming_it():
    """D10 on a mate inside a suppressed folder (probe round P0d: suppressing a folder suppresses its mates; turning
    the mate itself back on there is not probed): the read-back finds it still suppressed and the Update stops with
    a sentence naming it, before any lock is suppressed or any gear put."""
    fake = _built_train()
    fake.turn("gear4-1", 3.0)
    fake.mate("G4 along S3", T_ASM).suppressed = True
    fake.held_suppressed = {"G4 along S3"}
    result = _update_train(fake)
    assert result.failures == [("T.SLDASM", "SolidWorks would not turn the mate G4 along S3 back on in T.SLDASM: it "
                                            "still reads it suppressed; if it sits in a suppressed folder, unsuppress "
                                            "the folder in SolidWorks and press Update SolidWorks again.")]
    assert result.unsuppressed == [] and result.placed == [] and fake.locked_puts == []
    assert not fake.mate("G3 locked to G2", T_ASM).suppressed and result.changed == [T_ASM]
    assert "interferences" not in names(fake)



# -- which way a gear mate turns a ring (probe ring_mate_sense): read back, and made again with the other Flip

RING_MESHES = (MESHES[0], MeshLink("G3", "G4", 17.0 / 51, 360.0 / 51))   # G4 a ring round G3: same sense, both Z+


# Each gear mate's mesh sense as planning gives it (``k > 0``): outside on alike shafts turns the gears opposite
# ways (False); G4 a ring round G3 on alike shafts turns them the same way (True).
TRAIN_SENSES = {"G1 meshes G2": False, "G3 meshes G4": False}
RING_SENSES = {"G1 meshes G2": False, "G3 meshes G4": True}


def _build_ring(fake=None, senses=RING_SENSES, **kwargs):
    fake = fake or FakeSolidWorks()
    return _build_train(fake, parts=[plan(S17, path=P17), plan(S68, path=P68), plan(S51, path=P51R)],
                        assembly=_train_plan(ring=True), senses=senses, **kwargs)


def _turns_as_it_meshes(fake, meshes=RING_MESHES, frames=None):
    """Drive the input 10° as the solver would and judge every relation against the built frames."""
    built = {g: fake.frames[f"gear{g[1]}-1"] for g in TRAIN_ORDER}
    fake.drive("gear1-1", 10.0)
    after = {g: fake.frames[f"gear{g[1]}-1"] for g in TRAIN_ORDER}
    pitch = {g: 360.0 / TEETH[g] for g in TRAIN_ORDER}
    return swbuild.train_check(after, built, meshes, LOCKS, pitch).in_step


def test_a_ring_mate_wrong_first_is_made_again_with_the_other_flip_and_the_train_turns_as_it_meshes():
    """SolidWorks 2026 (the fake's default table): a spur ring on a same-sense shaft needs Flip True, so the mate made
    with Flip False reads wrong and is made again turned round, under its name, before any rebuild."""
    fake, result = _build_ring()
    assert result.ok and result.kind == "motion", result.log_lines()
    assert result.assembly.turned_round == ["G3 meshes G4"]
    called = names(fake)
    assert called.index("remake_gear_mate") < called.index("rebuild", called.index("new_assembly"))
    assert fake.turns_right("G3 meshes G4") and fake.mate("G3 meshes G4").flip is True
    assert "ok      read turning against their mesh, so made again with the other Flip: G3 meshes G4" in \
        result.assembly.log_lines()
    assert _turns_as_it_meshes(fake)


def test_a_ring_mate_right_first_time_is_left_as_made():
    fake = FakeSolidWorks()
    fake.flip_needed = dict(FLIP_NEEDED_2024)                  # SolidWorks 2024: Flip False is right here
    fake, result = _build_ring(fake)
    assert result.ok and result.assembly.turned_round == [] and "remake_gear_mate" not in names(fake)
    assert [a[1] for n, a in fake.calls if n == "gear_mate_sense"] == [False, True]   # both gear mates read
    assert _turns_as_it_meshes(fake)


def test_a_spur_ring_on_opposite_shafts_on_2024_is_turned_round_too():
    """The 2024 table: a spur ring on opposite shafts needs Flip True (and so does every same-sense one on 2026)."""
    fake = FakeSolidWorks()
    fake.flip_needed = dict(FLIP_NEEDED_2024)
    fake.flip_needed["spur ring ++"] = True                    # as the 2024 table has it for "+-" and "-+"
    _, result = _build_ring(fake)
    assert result.ok and result.assembly.turned_round == ["G3 meshes G4"]


def test_a_mate_solidworks_turns_wrong_with_either_flip_stops_the_build_as_a_refused_mate():
    fake = FakeSolidWorks()
    fake.never_right = {"G3 meshes G4"}
    fake, result = _build_ring(fake)
    _refused_ring = result
    assert not _refused_ring.ok and _refused_ring.kind == "" and not _refused_ring.assembly.saved
    assert _refused_ring.assembly.mate_problems == ["SolidWorks turns the gears of the mate G3 meshes G4 against the "
                                                    "way they mesh, whichever way round the mate is made."]
    assert [r.saved for r in result.parts.built] == [P17, P68, P51R] and result.layout.saved == T_LAYOUT
    assert names(fake).count("remake_gear_mate") == 1 and fake.suppressed is False


def test_axes_read_otherwise_than_the_plan_placed_them_stop_the_build_without_a_guess():
    fake = FakeSolidWorks()
    fake.entity_stray = {"G1 meshes G2": (1.0, 0.0, 0.0)}
    _, result = _build_ring(fake)
    assert not result.ok and result.assembly.mate_problems == [
        "SolidWorks reads an axis of the gear mate G1 meshes G2 as pointing (1, 0, 0), which is not along G1's axis "
        "(0, 0, 1) or G2's (0, 0, 1), so the mate does not hold the axes the gears were placed on, and nothing is "
        "guessed."]


def test_an_external_train_reads_every_gear_mate_and_turns_none_round():
    fake, result = _build_train(senses=TRAIN_SENSES)
    assert result.ok and result.assembly.turned_round == []
    assert [n for n in names(fake) if n == "gear_mate_sense"] == ["gear_mate_sense"] * 2


def test_without_saying_which_meshes_are_inside_a_ring_no_sense_is_read_as_before():
    fake, result = _build_ring(senses=None)
    assert result.ok and "gear_mate_sense" not in names(fake)
    assert not fake.turns_right("G3 meshes G4") and not _turns_as_it_meshes(fake)   # what the demonstration met


@pytest.mark.parametrize("name", ["GEAR_MATE_SENSE_READ_BACK", "GEAR_MATE_READ_BACK_TELLS_SENSE"])
def test_without_the_read_back_a_ring_train_is_refused_before_anything_is_made_and_an_external_one_builds(
        monkeypatch, name):
    monkeypatch.setattr(findings, name, None)
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        _build_ring(fake)
    assert str(raised.value) == ("The gear mate G3 meshes G4 meshes inside a ring, and which way a gear mate turns a "
                                 f"ring cannot be told on SolidWorks yet (findings.{name} is None), so nothing is made "
                                 "or changed; run probe ring_mate_sense first.")
    assert fake.calls == []
    fake, result = _build_train(senses=TRAIN_SENSES)
    assert result.ok and "gear_mate_sense" not in names(fake)


def test_with_the_read_back_but_not_the_remake_with_the_other_flip_a_train_is_refused_first(monkeypatch):
    monkeypatch.setattr(findings, "GEAR_MATE_CHECK_AND_REMAKE_HOLDS", None)
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError, match=r"findings.GEAR_MATE_CHECK_AND_REMAKE_HOLDS settled on SolidWorks "
                                                 r"\(it is None\), so nothing is made or changed"):
        _build_ring(fake)
    assert fake.calls == []


# The Update's remake, and the check phase's read (behind its placeholder finding)

RING_MESHES_18 = (MESHES[0], MeshLink("G3", "G4", 18.0 / 50, 360.0 / 50))


def _built_ring(table=None, senses=RING_SENSES):
    fake = FakeSolidWorks()
    if table is not None:
        fake.flip_needed = dict(table)
    fake, result = _build_ring(fake, senses=senses)
    assert result.ok, result.log_lines()
    fake.calls.clear()
    return fake


def _ring_motion(**kwargs):
    kwargs.setdefault("meshes", RING_MESHES)
    kwargs.setdefault("recorded_meshes", RING_MESHES)
    return _motion(**kwargs)


def test_an_update_remake_on_a_ring_comes_out_turning_as_it_meshes(remake_route):
    fake = _built_ring()
    result = _update_train(fake, motion=_ring_motion(meshes=RING_MESHES_18, ratios=(("G3 meshes G4", 18, 50),)))
    assert result.ok, result.log_lines()
    assert result.ratios == ["G3 meshes G4"] and result.turned_round == ["G3 meshes G4"]
    assert fake.mate("G3 meshes G4", T_ASM).ratio == (18.0, 50.0) and fake.turns_right("G3 meshes G4", T_ASM)
    called = names(fake)
    assert called.index("set_gear_ratio") < called.index("remake_gear_mate") < called.index("place_component")
    assert fake.locked_puts == [] and not fake.mate("G3 locked to G2", T_ASM).suppressed
    assert "ok      made again with the other Flip: G3 meshes G4" in result.log_lines()


def test_an_update_remake_on_a_ring_right_first_time_is_not_turned_round(remake_route):
    fake = _built_ring(FLIP_NEEDED_2024)
    result = _update_train(fake, motion=_ring_motion(meshes=RING_MESHES_18, ratios=(("G3 meshes G4", 18, 50),)))
    assert result.ok and result.turned_round == [] and "remake_gear_mate" not in names(fake)


def test_an_update_remake_wrong_with_either_flip_stops_with_the_locks_back_on(remake_route):
    fake = _built_ring()
    fake.never_right = {"G3 meshes G4"}
    result = _update_train(fake, motion=_ring_motion(meshes=RING_MESHES_18, ratios=(("G3 meshes G4", 18, 50),)))
    assert result.failures == [("T.SLDASM", "SolidWorks turns the gears of the mate G3 meshes G4 against the way they "
                                            "mesh, whichever way round it is made; the saved T.SLDASM "
                                            "still has it as it was: close T.SLDASM in SolidWorks without saving to "
                                            "bring it back.")]
    assert not fake.mate("G3 locked to G2", T_ASM).suppressed and result.placed == [] and result.changed == [T_ASM]


def test_without_the_read_back_an_update_remake_inside_a_ring_is_refused_before_anything_changes(remake_route,
                                                                                                 monkeypatch):
    fake = _built_ring()
    monkeypatch.setattr(findings, "GEAR_MATE_SENSE_READ_BACK", None)
    with pytest.raises(swbuild.BuildError, match="^The gear mate G3 meshes G4 meshes inside a ring"):
        _update_train(fake, motion=_ring_motion(meshes=RING_MESHES_18, ratios=(("G3 meshes G4", 18, 50),)))
    assert not any(n in CHANGING for n in names(fake))


@pytest.mark.parametrize("name", [n for n, _ in swbuild.SENSE_CHECK_FINDINGS])
def test_the_check_phase_reads_no_sense_while_a_finding_it_rests_on_is_missing(monkeypatch, name):
    """Not a refusal: without the read's findings the check phase does not read the sense, as before."""
    monkeypatch.setattr(findings, name, None)
    fake = _built_ring(senses=None)                          # built before the check: G3 meshes G4 turns wrong
    fake.turn("gear4-1", 3.0)
    result = _update_train(fake, motion=_ring_motion())
    assert result.ok and result.sense_found_wrong == [] and "gear_mate_sense" not in names(fake)


def test_with_its_finding_the_check_phase_finds_a_ring_turning_wrong_and_remakes_it(remake_route, monkeypatch):
    monkeypatch.setattr(findings, swbuild.SENSE_CHECK_FINDINGS[0][0], swbuild.SENSE_CHECK_FINDINGS[0][1])
    fake = _built_ring(senses=None)
    result = _update_train(fake, motion=_ring_motion())
    assert result.ok, result.log_lines()
    assert result.sense_found_wrong == ["G3 meshes G4"] and result.turned_round == ["G3 meshes G4"]
    assert fake.turns_right("G3 meshes G4", T_ASM) and result.placed == list(TRAIN_ORDER)
    assert fake.locked_puts == []



# -- the review of package B: an Update stopped after a remake that read wrong either way round, then pressed again

@pytest.fixture
def sense_check(monkeypatch):
    """The check phase's read of every recorded gear mate, switched on (its findings are still placeholders)."""
    for name, value in swbuild.SENSE_CHECK_FINDINGS:
        monkeypatch.setattr(findings, name, value, raising=False)


def _stopped_remake(fake, wrong, ratios, meshes):
    """An Update whose remake of ``wrong`` reads wrong with both Flips stops (the open assembly left holding it at
    the new ratio, made the second way round); then the user presses Update again without closing."""
    fake.never_right = {wrong}
    result = _update_train(fake, motion=_motion(meshes=meshes, ratios=ratios))
    assert not result.ok and result.failures[-1][1].startswith(f"SolidWorks turns the gears of the mate {wrong} "), \
        result.log_lines()
    assert not fake.turns_right(wrong, T_ASM)
    fake.never_right = set()                       # nothing in the open assembly changes with it
    assert not fake.turns_right(wrong, T_ASM)
    fake.calls.clear()


def test_a_second_press_after_a_remake_stopped_turning_wrong_finds_it_and_remakes_it(remake_route, sense_check):
    fake = _built_train()
    asked = (("G1 meshes G2", 17, 69),)
    _stopped_remake(fake, "G1 meshes G2", asked, MESHES_69)
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=asked))     # the record kept 17 : 68
    assert result.ok, result.log_lines()
    assert result.sense_found_wrong == ["G1 meshes G2"] and result.ratios_already == []
    assert result.ratios == ["G1 meshes G2"] and result.placed == list(TRAIN_ORDER)
    assert fake.turns_right("G1 meshes G2", T_ASM) and fake.mate("G1 meshes G2", T_ASM).ratio == (17.0, 69.0)
    assert fake.locked_puts == []


def test_a_second_press_with_two_gear_mates_remakes_only_the_one_left_turning_wrong(remake_route, sense_check):
    fake = _built_train()
    meshes = (MeshLink("G1", "G2", -17.0 / 69, 360.0 / 69), MeshLink("G3", "G4", -18.0 / 50, 360.0 / 50))
    asked = (("G1 meshes G2", 17, 69), ("G3 meshes G4", 18, 50))
    _stopped_remake(fake, "G3 meshes G4", asked, meshes)
    assert fake.turns_right("G1 meshes G2", T_ASM)               # the first was remade right before the stop
    result = _update_train(fake, motion=_motion(meshes=meshes, ratios=asked))
    assert result.ok, result.log_lines()
    assert result.ratios_already == ["G1 meshes G2"] and result.sense_found_wrong == ["G3 meshes G4"]
    assert result.ratios == ["G3 meshes G4"]
    assert fake.turns_right("G1 meshes G2", T_ASM) and fake.turns_right("G3 meshes G4", T_ASM)


def test_a_second_press_still_wrong_either_way_round_stops_again_with_the_same_sentence(remake_route, sense_check):
    fake = _built_train()
    asked = (("G1 meshes G2", 17, 69),)
    _stopped_remake(fake, "G1 meshes G2", asked, MESHES_69)
    fake.never_right = {"G1 meshes G2"}
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=asked))
    assert result.failures == [("T.SLDASM", "SolidWorks turns the gears of the mate G1 meshes G2 against the way they "
                                            "mesh, whichever way round it is made; the saved T.SLDASM still has it as "
                                            "it was: close T.SLDASM in SolidWorks without saving to bring it back.")]
    assert result.ratios_already == [] and not fake.mate("G3 locked to G2", T_ASM).suppressed


def test_without_the_check_phase_read_the_second_press_still_trusts_the_live_ratio(remake_route, monkeypatch):
    """What the review found, kept visible for a SolidWorks whose check-phase read is not settled: nobody reads it."""
    monkeypatch.setattr(findings, "GEAR_MATE_SENSE_READ_MARKS", None)
    fake = _built_train()
    asked = (("G1 meshes G2", 17, 69),)
    _stopped_remake(fake, "G1 meshes G2", asked, MESHES_69)
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=asked))
    assert result.ok and result.ratios_already == ["G1 meshes G2"]
    assert not fake.turns_right("G1 meshes G2", T_ASM)



# -- probe ring_trains_saved's findings in the gates

def test_the_check_phase_read_is_on_with_the_committed_findings_and_closes_the_stopped_remake_case(remake_route):
    """The must-fix from the review of package B, closed now that the check phase reads every gear mate's sense:
    an Update stops on a remake wrong either way round; the cause goes; pressed again, the wrong mate is not taken
    as already there — it is read wrong, remade, and turns right."""
    for name, value in swbuild.SENSE_CHECK_FINDINGS:
        assert getattr(findings, name) == value              # the autouse fixture pins them as committed
    fake = _built_train()
    asked = (("G1 meshes G2", 17, 69),)
    _stopped_remake(fake, "G1 meshes G2", asked, MESHES_69)
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=asked))
    assert result.ok, result.log_lines()
    assert "G1 meshes G2" not in result.ratios_already and result.sense_found_wrong == ["G1 meshes G2"]
    assert result.ratios == ["G1 meshes G2"] and fake.turns_right("G1 meshes G2", T_ASM)


@pytest.mark.parametrize("name", ["GEAR_MATE_SENSE_READ_UNDER_COMMAND_IN_PROGRESS",
                                  "GEAR_MATE_REMAKE_UNDER_COMMAND_IN_PROGRESS"])
def test_a_train_with_a_gear_mate_is_refused_before_anything_is_made_without_the_command_in_progress_findings(
        monkeypatch, name):
    monkeypatch.setattr(findings, name, None)
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        _build_train(fake)
    assert str(raised.value) == ("A gearbox built to turn checks which way each gear mate turns its gears as it makes "
                                 f"them, and that has not been settled on SolidWorks (findings.{name} is None), so "
                                 "nothing is made or changed; run probe ring_trains_saved first.")
    assert fake.calls == []


def test_an_update_remake_without_the_read_back_after_a_ratio_remake_is_refused_before_anything_changes(
        remake_route, monkeypatch):
    monkeypatch.setattr(findings, "GEAR_MATE_READ_BACK_HOLDS_AFTER_A_RATIO_REMAKE", None)
    fake = _built_train()
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=(("G1 meshes G2", 17, 69),)))
    assert str(raised.value) == ("Update SolidWorks on a gearbox built to turn needs "
                                 "findings.GEAR_MATE_READ_BACK_HOLDS_AFTER_A_RATIO_REMAKE settled on SolidWorks (it is "
                                 "None), so nothing is changed; run probe tier 8 first.")
    assert not any(n in CHANGING for n in names(fake))



# -- the review of 980f10b: a suppressed gear mate is read only once turned back on; a sense-only remake

def test_a_suppressed_gear_mate_that_turns_right_is_healed_as_before(remake_route):
    fake = _built_train()
    fake.mate("G1 meshes G2", T_ASM).suppressed = True
    result = _update_train(fake)
    assert result.ok, result.log_lines()
    assert result.unsuppressed == ["G1 meshes G2"] and result.sense_found_wrong == [] and result.placed == []
    reads = [a[0] for n, a in fake.calls if n == "gear_mate_sense"]
    assert reads.count("mate8") == 1                                  # once, after it was turned back on
    called = names(fake)
    assert called.index("set_mate_suppressed") < max(i for i, n in enumerate(called) if n == "gear_mate_sense")


def test_a_gear_mate_suppressed_with_its_folder_and_right_is_healed_as_before(monkeypatch, remake_route):
    monkeypatch.setattr(findings, "MATE_FOLDER_TYPE_NAME", "FtrFolder")
    monkeypatch.setattr(findings, "MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER", True)
    fake = _built_train()
    fake.user_folder(T_ASM, "Folder1")
    fake.mate("G3 meshes G4", T_ASM).suppressed = True          # suppressed with the folder it sits in
    result = _update_train(fake)
    assert result.ok and result.unsuppressed == ["G3 meshes G4"] and result.sense_found_wrong == []


def test_a_suppressed_gear_mate_that_turns_wrong_is_turned_on_read_remade_and_its_train_put(remake_route):
    fake = _built_ring(senses=None)                          # built without the read: G3 meshes G4 turns wrong
    fake.mate("G3 meshes G4", T_ASM).suppressed = True
    result = _update_train(fake, motion=_ring_motion())
    assert result.ok, result.log_lines()
    assert result.unsuppressed == ["G3 meshes G4"] and result.sense_found_wrong == ["G3 meshes G4"]
    assert result.ratios == [] and result.placed == list(TRAIN_ORDER)       # its ratio did not change
    assert fake.turns_right("G3 meshes G4", T_ASM) and fake.locked_puts == []


def test_a_sense_only_remake_is_not_said_to_be_a_new_ratio(remake_route):
    fake = _built_ring(senses=None)
    result = _update_train(fake, motion=_ring_motion())
    assert result.ok and result.sense_found_wrong == ["G3 meshes G4"] and result.ratios == []
    assert not any(line.startswith("ok      given their new ratio") for line in result.log_lines())
    assert "ok      found turning against their mesh, so made again: G3 meshes G4" in result.log_lines()


def test_a_wrong_sense_mate_is_refused_before_anything_changes_while_the_remake_route_is_missing(monkeypatch):
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
    fake = _built_ring(senses=None)
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, motion=_ring_motion())
    assert str(raised.value) == ("The gear mate G3 meshes G4 in T.SLDASM turns its gears against the way they mesh, "
                                 "and making a gear mate again has not been settled on SolidWorks "
                                 "(findings.GEAR_MATE_RATIO_ROUTE is None), so nothing is changed; build the gearbox "
                                 "again.")
    assert not any(n in CHANGING for n in names(fake))


def test_a_fixed_gear_takes_the_unfix_route_when_the_finding_says_so(monkeypatch, remake_route):
    """A check-phase variable once shadowed REPLACE_FIXED_ROUTE with the ratio route, so the unfix route was lost."""
    monkeypatch.setattr(findings, "REPLACE_FIXED_ROUTE", "UnfixComponent, Transform2 put, FixComponent")
    fake = _built_train()
    fake.mate("G3 meshes G4", T_ASM).suppressed = True
    motion = _motion(mates=tuple(m for m in MATE_REFS if m.name != "G3 meshes G4"), fixed=("G4",),
                     meshes=MESHES[:1], recorded_meshes=MESHES[:1])
    fake.turn("gear4-1", 2.0)
    result = _update_train(fake, motion=motion)
    assert result.ok and result.placed == ["G4"], result.log_lines()
    moves = [n for n, a in fake.calls if n in ("unfix_component", "place_component", "fix_component")]
    assert moves == ["unfix_component", "place_component", "fix_component"]



# -- the review of b4d4bdd: the deferred read of a suppressed gear mate

@pytest.mark.parametrize("in_folder", [False, True])
def test_a_stopped_remake_then_suppressed_and_pressed_again_is_remade_and_never_said_already_there(
        remake_route, sense_check, monkeypatch, in_folder):
    """An Update stops on a remake wrong either way round, leaving the mate at 17 : 69 turning wrong; the user
    suppresses it (or the folder it sits in) and presses again with the plan still asking 17 : 69. It is turned back
    on, read wrong, remade and its train put: in ``ratios`` (the plan asked that ratio, and the record takes it from
    there) and ``sense_found_wrong``, never in ``ratios_already``."""
    fake = _built_train()
    asked = (("G1 meshes G2", 17, 69),)
    _stopped_remake(fake, "G1 meshes G2", asked, MESHES_69)
    if in_folder:
        monkeypatch.setattr(findings, "MATE_FOLDER_TYPE_NAME", "FtrFolder")
        monkeypatch.setattr(findings, "MATE_GROUP_WALK_SEES_MATES_IN_A_FOLDER", True)
        fake.user_folder(T_ASM, "Folder1")
    fake.mate("G1 meshes G2", T_ASM).suppressed = True
    result = _update_train(fake, motion=_motion(meshes=MESHES_69, ratios=asked))
    assert result.ok, result.log_lines()
    assert result.unsuppressed == ["G1 meshes G2"]
    assert result.ratios_already == [] and result.ratios == ["G1 meshes G2"]
    assert result.sense_found_wrong == ["G1 meshes G2"] and result.placed == list(TRAIN_ORDER)
    assert result.ratios_read == [("G1 meshes G2", 17, 69, 17, 69)]
    lines = result.log_lines()
    assert "ok      given their new ratio: G1 meshes G2" in lines
    assert "ok      found turning against their mesh, so made again: G1 meshes G2" in lines
    assert not any(line.startswith("ok      already at the ratio") for line in lines)
    assert fake.turns_right("G1 meshes G2", T_ASM) and fake.mate("G1 meshes G2", T_ASM).ratio == (17.0, 69.0)
    assert not fake.mate("G1 meshes G2", T_ASM).suppressed and fake.locked_puts == []


@pytest.mark.parametrize("name, said", [
    ("GEAR_MATE_CHECK_AND_REMAKE_HOLDS",
     "Update SolidWorks on a gearbox built to turn needs findings.GEAR_MATE_CHECK_AND_REMAKE_HOLDS settled on "
     "SolidWorks (it is None), so nothing is changed; run probe tier 8 first."),
    ("GEAR_MATE_RATIO_REMAKE_WORKS",
     "Update SolidWorks on a gearbox built to turn needs making a gear mate again at a new ratio settled on "
     "SolidWorks (findings.GEAR_MATE_RATIO_REMAKE_WORKS is None), so nothing is changed; run probe tier 8 first."),
])
def test_a_suppressed_gear_mate_counts_as_a_possible_remake_and_its_gates_refuse_before_anything_changes(
        remake_route, monkeypatch, name, said):
    """Even one that would turn right once turned back on: which way it turns is read only after a change, so the
    remake's gates are read before any."""
    fake = _built_train()
    fake.mate("G1 meshes G2", T_ASM).suppressed = True
    monkeypatch.setattr(findings, name, None)
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake)
    assert str(raised.value) == said
    assert not any(n in CHANGING + ("remake_gear_mate",) for n in names(fake))
    assert "mate8" not in [a[0] for n, a in fake.calls if n == "gear_mate_sense"]     # never read while suppressed
    assert fake.mate("G1 meshes G2", T_ASM).suppressed


def test_a_suppressed_gear_mate_is_refused_before_anything_changes_while_the_remake_route_is_missing(monkeypatch):
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
    fake = _built_train()
    fake.mate("G1 meshes G2", T_ASM).suppressed = True
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake)
    assert str(raised.value) == ("The gear mate G1 meshes G2 in T.SLDASM is suppressed, so which way it turns can be "
                                 "read only once Update SolidWorks has turned it back on, and making it again should "
                                 "it turn against the way its gears mesh has not been settled on SolidWorks "
                                 "(findings.GEAR_MATE_RATIO_ROUTE is None), so nothing is changed; unsuppress G1 "
                                 "meshes G2 in SolidWorks and press Update SolidWorks again.")
    assert not any(n in CHANGING + ("remake_gear_mate",) for n in names(fake))


def test_a_suppressed_idler_gear_mate_needs_the_idler_finding_before_anything_changes(remake_route, monkeypatch):
    monkeypatch.setattr(findings, "IDLER_UPDATE_HOLDS", None)
    fake = _built_idler()
    fake.mate("G3 meshes G4", T_ASM).suppressed = True
    with pytest.raises(swbuild.BuildError) as raised:
        _update_train(fake, motion=_idler_motion(51, ()))
    assert str(raised.value) == ("Giving a new ratio to a gear mate of G4, which carries two gear mates, has not been "
                                 "settled on SolidWorks (findings.IDLER_UPDATE_HOLDS is None), so nothing is changed; "
                                 "run probe tier 8 first, or build the gearbox again.")
    assert not any(n in CHANGING + ("remake_gear_mate",) for n in names(fake))



# -- W6: turned axes (W6-PLAN §2.6, §4.2 row A), on the fake: fixture A's bevel stage and fixture B's crossed one,
# planned here by hand from §5's numbers (the fake never reads the planning code)

@pytest.fixture
def turned_findings(monkeypatch):
    """Tier 9's findings (11ee1e2) and the skew range the probe agent adds (W6-INTERFACES §7.12), pinned here, with
    the planetary put route probe planetary_put_back found on SolidWorks 2026 (the planetary Updates below take their
    findings here, and one of a train with a carrier refuses without it; a test of the refusal sets it after)."""
    for name, value in (("TURNED_GEAR_MATE_SENSE_READ_BACK", "entity senses"),
                        ("TURNED_GEAR_MATE_SENSE_ANGLES", (30.0, 150.0)),
                        ("TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", (60.0, 120.0)),
                        ("PLANETARY_PUT_ROUTE", "gear mates off around the puts")):
        monkeypatch.setattr(findings, name, value, raising=False)


X_FRAME = (0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0)       # geometry.base_frame(X+): [+Y | +Z | +X] by rows
A_LAYOUT, A_ASM = W + "Bevel_Reducer_Layout.SLDPRT", W + "Bevel_Reducer.SLDASM"
B20, B40 = W + "Bevel_m3_N20.SLDPRT", W + "Bevel_m3_N40.SLDPRT"
A_PARTS = {"gear1": B20, "gear2": B40, "gear3": P17, "gear4": P51}
# Each turned mesh's sense worked out by hand from the contact, not from the planning code (W6-INTERFACES §7.18).
#
# Fixture A, G1 meshes G2 (bevel, §5.1). Own axes a1 = +X, a2 = +Z, both pointing away from the shared apex
# (0, 0, 60), each body on its own +Z side (D1). The pitch point is P = apex + R(cos δ1, 0, sin δ1), on +X and +Z of
# the apex. G1's speed there is ω1·(+X) × (0, 0, R sin δ1) = −ω1·R sin δ1·Y; G2's is ω2·(+Z) × (R sin δ2, 0, 0) =
# +ω2·R sin δ2·Y (δ1 + δ2 = 90°, so G2's radius to P is R cos δ1 = R sin δ2). Rolling, they are equal:
# ω2 = −ω1·sin δ1 / sin δ2 = −ω1·20/40. Opposite turns about the own axes: k < 0, False.
#
# Fixture B, G1 meshes G2 (crossed, §5.2). a1 = +Z through the origin, a2 = +X along y 84.852814, z 8: the common
# perpendicular from G1's line to G2's is e = +Y, the contact (0, 28.284271, 8). G1 is right-handed at 45°: a right
# helix (r cos θ, r sin θ, pθ) runs (−r sin θ, r cos θ, p) at θ = 90°, so its tooth there is t ∝ (−1, 0, 1). The
# surface speeds are G1's ω1·Z × (r1·Y) = −ω1 r1·X and G2's ω2·X × (−r2·Y) = −ω2 r2·Z; they agree across the tooth,
# along n = t × e ∝ (−1, 0, −1): ω1 r1 = ω2 r2, so ω2 = +ω1·r1/r2 = +ω1·20/40. The same way: k > 0, True.
#
# Fixture B, G3 meshes G4 (bevel at 120°). a3 = +X, a4 = d̂ = (−0.5, 0.866, 0), apex (−110, 84.852814, 8). The
# pitch point lies at δ3 from a3 towards a4, at R(cos δ3, sin δ3, 0) from the apex. G3's speed there is
# ω3·X × (0, R sin δ3, 0) = +ω3·R sin δ3·Z; G4's radius to it points at 30° in the XY plane, (0.866, 0.5, 0), and
# d̂ × (0.866, 0.5, 0) = −Z, so G4's speed is −ω4·R sin δ4·Z. Equal: ω4 = −ω3·sin δ3 / sin δ4 = −ω3·20/30.
# Opposite turns: k < 0, False. (The spur G3 meshes G4 of fixture A is parallel: W5's rule, outside, False.)
A_TRUE = {"G1 meshes G2": False}
B_TRUE = {"G1 meshes G2": True, "G3 meshes G4": False}
A_SENSES = {"G1 meshes G2": A_TRUE["G1 meshes G2"], "G3 meshes G4": False}
B_SENSES = dict(B_TRUE)


def _a_layout_plan(path=A_LAYOUT):
    """Fixture A's layout (§5.1): S1 on X+ through Top and "S1 Z Plane" (60 from Front); S2 on Z through Top and
    Right; S3 on Z through "S3 X Plane" (68 on Right's minus side) and Top."""
    return BuildPlan("layout", "", (
        ops.NewPart(""), ops.AddGlobal("S1 Z", "60"), ops.AddGlobal("S3 X", "-68"),
        ops.RefPlane("z1", "S1 Z Plane", 1, 60.0), ops.RefPlane("x3", "S3 X Plane", 3, 68.0, True),
        ops.Axis("axis1", "S1 Axis", (2, "z1")), ops.Axis("axis2", "S2 Axis", (2, 3)),
        ops.Axis("axis3", "S3 Axis", (2, "x3")), ops.Rebuild(), ops.SaveAs(path)), path)


def _a_frames(z1=60.0):
    return {"G1": (X_FRAME, (0.0, 0.0, z1)), "G2": (IDENTITY, (0.0, 0.0, z1)),
            "G3": (_rot_z(0.0), (0.0, 0.0, 0.0)), "G4": (_rot_z(180.0 / 51), (-68.0, 0.0, 0.0))}


def _a_plan(path=A_ASM, frames=None):
    """Fixture A's turning assembly: G1's apex on the Right plane, G2's apex 60 from Front ("G2 Apex Z"), G3 locked
    to G2, G4's face on Front; the bevel gear mate across 90°."""
    frames = frames or _a_frames()
    steps = [ops.NewAssembly(""), ops.AddGlobal("G2 Apex Z", "60"),
             ops.AddComponent("layout", A_LAYOUT), ops.Place("layout", IDENTITY, (0.0, 0.0, 0.0)), ops.Fix("layout")]
    for handle, gear in TRAIN_GEARS.items():
        rotation, at = frames[gear]
        steps += [ops.AddComponent(handle, A_PARTS[handle], at), ops.Place(handle, rotation, at), ops.Fix(handle)]
    steps += [ops.Unfix("gear1"),
              ops.Mate("axis1", "coincident", "gear1:Gear Axis", "layout:S1 Axis", name="G1 on S1 Axis"),
              ops.Mate("along1", "point", "gear1:origin", "layout:plane3", name="G1 along S1"),
              ops.Unfix("gear2"),
              ops.Mate("axis2", "coincident", "gear2:Gear Axis", "layout:S2 Axis", name="G2 on S2 Axis"),
              ops.Mate("along2", "point distance", "gear2:origin", "layout:plane1", 60.0, name="G2 along S2"),
              ops.LinkDimension("D1@G2 along S2", '"G2 Apex Z"'),
              ops.Unfix("gear3"), ops.Mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2"),
              ops.Unfix("gear4"),
              ops.Mate("axis3", "coincident", "gear4:Gear Axis", "layout:S3 Axis", name="G4 on S3 Axis"),
              ops.Mate("along3", "point", "gear4:origin", "layout:plane1", name="G4 along S3"),
              ops.Mate("mesh1", "gear", "gear1:Gear Axis", "gear2:Gear Axis", name="G1 meshes G2", ratio=(20.0, 40.0)),
              ops.Mate("mesh2", "gear", "gear3:Gear Axis", "gear4:Gear Axis", name="G3 meshes G4", ratio=(17.0, 51.0))]
    return BuildPlan("gearbox", "", tuple(steps) + (ops.Rebuild(), ops.SaveAs(path)), path)


def _build_a(fake=None, **kwargs):
    fake = fake or FakeSolidWorks()
    kwargs.setdefault("parts", [plan(S17, path=B20), plan(S17, path=B40), plan(S17, path=P17), plan(S51, path=P51)])
    kwargs.setdefault("layout", _a_layout_plan())
    kwargs.setdefault("assembly", _a_plan())
    kwargs.setdefault("gears", TRAIN_GEARS)
    kwargs.setdefault("exists", fake.exists)
    kwargs.setdefault("senses", dict(A_SENSES))
    return fake, swbuild.build_gearbox(fake, **kwargs)


def test_fixture_a_plans_are_sound_and_its_bevel_mesh_meets_at_ninety_degrees():
    assert _a_plan().check() == [] and _a_layout_plan().check() == []
    axes, origins = swbuild._planned_axes(_a_plan()), swbuild._planned_origins(_a_plan())
    assert axes["gear1"] == (1.0, 0.0, 0.0) and swcom.own_axes_angle(axes["gear1"], axes["gear2"]) == 90.0
    assert swcom.lines_meet(origins["gear1"], axes["gear1"], origins["gear2"], axes["gear2"])


def test_a_bevel_train_builds_with_every_gear_mate_read_against_its_planned_axes(turned_findings):
    fake, result = _build_a()
    assert result.ok and result.kind == swbuild.GEARBOX_MOTION, result.log_lines()
    reads = [a for n, a in fake.calls if n == "gear_mate_sense"]
    assert [same for _, same in reads] == [False, False]                    # both meshes: k < 0
    assert result.assembly.turned_round == [] and result.assembly.mate_problems == []
    assert fake.turns_right("G1 meshes G2", A_ASM) and fake.turns_right("G3 meshes G4", A_ASM)
    for gear, frame in _a_frames().items():                                 # the rebuild left every gear placed
        assert _close(fake.frames[f"gear{gear[1]}-1"], frame), gear


def test_the_fake_layout_puts_a_turned_axis_where_its_planes_cross():
    fake = FakeSolidWorks()
    swbuild.build(fake, _a_layout_plan(), fake.exists)
    assert fake.axis_line("a1", "S1 Axis") == ((0.0, 0.0, 60.0), (1.0, 0.0, 0.0))
    assert fake.axis_line("a3", "S3 Axis") == ((-68.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    fake.set_global_variable("S1 Z", "64")
    assert fake.axis_line("a1", "S1 Axis") == ((0.0, 0.0, 64.0), (1.0, 0.0, 0.0))


@pytest.mark.parametrize("given", ["senses", "neither"])
def test_a_turned_mesh_is_refused_before_anything_is_made_while_the_turned_finding_is_missing(
        turned_findings, monkeypatch, given):
    """W6-INTERFACES §7.3: whatever the caller gives, no turned gear mate reaches AddMate5 unread (D16)."""
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", None)
    fake = FakeSolidWorks()
    kwargs = {"senses": dict(A_SENSES)} if given == "senses" else {"senses": None}
    with pytest.raises(swbuild.BuildError) as raised:
        _build_a(fake, **kwargs)
    assert str(raised.value) == ("The gear mate G1 meshes G2 joins gears on shafts that meet at an angle, and which way "
                                 "such a gear mate turns cannot be told on SolidWorks yet "
                                 "(findings.TURNED_GEAR_MATE_SENSE_READ_BACK is None), so nothing is made or changed.")
    assert fake.calls == []


def test_a_turned_mesh_outside_the_angles_the_finding_covers_is_refused_before_anything_is_made(
        turned_findings, monkeypatch):
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_ANGLES", (100.0, 150.0))
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        _build_a(fake)
    assert str(raised.value) == ("The gear mate G1 meshes G2 joins gears on shafts that meet at 90°, outside the "
                                 "100°–150° the probes showed such a gear mate turning right at "
                                 "(findings.TURNED_GEAR_MATE_SENSE_ANGLES), so nothing is made or changed.")
    assert fake.calls == []


def test_a_turned_mesh_needs_the_build_told_its_sense(turned_findings):
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        _build_a(fake, senses=None)
    assert str(raised.value) == ("The gear mate G1 meshes G2 joins gears on shafts at an angle, and the build was not "
                                 "told which way it turns them, so nothing is made; that is a fault in Gear Generator.")
    assert fake.calls == []
    with pytest.raises(swbuild.BuildError, match="not told which way the gear mate G3 meshes G4"):
        _build_a(senses={"G1 meshes G2": False})


def test_a_turned_mate_read_wrong_is_made_again_with_the_other_flip(turned_findings):
    fake = FakeSolidWorks()
    fake.turned_flip_needed = True                               # made up: this SolidWorks wants the other Flip
    fake, result = _build_a(fake)
    assert result.ok and result.assembly.turned_round == ["G1 meshes G2"], result.log_lines()
    assert fake.mate("G1 meshes G2", A_ASM).flip is True and fake.turns_right("G1 meshes G2", A_ASM)


def test_a_turned_mate_read_wrong_either_way_round_stops_the_build_as_a_mate_problem(turned_findings):
    fake = FakeSolidWorks()
    fake.turned_reverse = {"G1 meshes G2": True}                 # SolidWorks' Reverse not as rule H says
    fake, result = _build_a(fake)
    assert not result.ok and result.assembly.mate_problems == [
        "SolidWorks turns the gears of the mate G1 meshes G2 against the way they mesh, whichever way round the mate "
        "is made."]
    assert not result.assembly.saved


@pytest.mark.parametrize("override", [{"entity_swapped": {"G1 meshes G2"}},
                                      {"entity_senses": {"G1 meshes G2": (-1, 1)}},
                                      {"entity_senses": {"G1 meshes G2": (-1, -1)}, "entity_swapped": {"G1 meshes G2"}}])
def test_a_turned_mates_entities_in_either_order_and_either_direction_are_judged_by_rule_h(turned_findings, override):
    """Tier 9 saw every entity along its own gear's +Z, first selection first (W6-INTERFACES §7.12); the fake's
    overrides keep the other cases tested: H matches each entity to its gear by alignment, and its sense counts."""
    fake = FakeSolidWorks()
    for name, value in override.items():
        setattr(fake, name, value)
    fake, result = _build_a(fake)
    assert result.ok and result.assembly.turned_round == [], result.log_lines()
    assert fake.turns_right("G1 meshes G2", A_ASM)


def test_a_turned_mate_holding_an_axis_along_neither_gear_stops_the_build_naming_both(turned_findings):
    fake = FakeSolidWorks()
    fake.entity_stray = {"G1 meshes G2": (0.0, 1.0, 0.0)}
    fake, result = _build_a(fake)
    assert result.assembly.mate_problems == [
        "SolidWorks reads an axis of the gear mate G1 meshes G2 as pointing (0, 1, 0), which is not along G1's axis "
        "(1, 0, 0) or G2's (0, 0, 1), so the mate does not hold the axes the gears were placed on, and nothing is "
        "guessed."]


def test_the_drive_turns_a_bevel_train_as_section_five_says(turned_findings):
    fake, result = _build_a()
    assert result.ok
    turns = fake.drive("gear1-1", 30.0)
    assert turns["gear2-1"] == pytest.approx(-15.0) and turns["gear3-1"] == pytest.approx(-15.0)
    assert turns["gear4-1"] == pytest.approx(5.0)


# fixture B's crossed stage alone (§5.2): S1 on Z, S2 on X+ at y 84.852814, z 8; G2's origin on Right's minus side
C_SHAFT = 84.852814
H20, H40 = W + "Helical_m2_N20_45R.SLDPRT", W + "Helical_m2_N40_45R.SLDPRT"


B_BEVEL20, B_BEVEL30 = W + "Bevel_m2.5_N20.SLDPRT", W + "Bevel_m2.5_N30.SLDPRT"
SLANT_D = (-0.5, math.sqrt(3) / 2, 0.0)
# geometry.base_frame(SLANT_D) by rows: u0 = +X projected square to d̂ = (√3/2, 1/2, 0), v0 = d̂ × u0 = (0, 0, −1)
D_FRAME = (math.sqrt(3) / 2, 0.0, -0.5, 0.5, 0.0, math.sqrt(3) / 2, 0.0, -1.0, 0.0)
B_APEX = (-110.0, C_SHAFT, 8.0)


def _b_layout_plan(path=A_LAYOUT, slant=True):
    steps = [ops.NewPart(""), ops.AddGlobal("S2 Y", repr(C_SHAFT)), ops.AddGlobal("S2 Z", "8"),
             ops.RefPlane("y2", "S2 Y Plane", 2, C_SHAFT), ops.RefPlane("z2", "S2 Z Plane", 1, 8.0),
             ops.Axis("axis1", "S1 Axis", (2, 3)), ops.Axis("axis2", "S2 Axis", ("y2", "z2"))]
    if slant:
        steps.append(ops.LineAxis("line3", "S3 Axis", B_APEX, SLANT_D))
    return BuildPlan("layout", "", tuple(steps) + (ops.Rebuild(), ops.SaveAs(path)), path)


def _b_plan(path=A_ASM, slant=False):
    """Fixture B (§5.2): the crossed pair G1 (S1, Z+) – G2 (S2, X+); with ``slant``, also G3 (bevel on S2, At −110,
    locked to G2) meshing G4 (bevel on the slanted S3, its apex held from Top by "G4 Apex Y") at 120°."""
    steps = [ops.NewAssembly(""), ops.AddGlobal("G1 Face Z", "2"), ops.AddGlobal("G2 Face X", "8")]
    if slant:
        steps.append(ops.AddGlobal("G4 Apex Y", repr(C_SHAFT)))
    steps += [ops.AddComponent("layout", A_LAYOUT), ops.Place("layout", IDENTITY, (0.0, 0.0, 0.0)), ops.Fix("layout"),
              ops.AddComponent("gear1", H20, (0.0, 0.0, 2.0)), ops.Place("gear1", IDENTITY, (0.0, 0.0, 2.0)),
              ops.Fix("gear1"),
              ops.AddComponent("gear2", H40, (-8.0, C_SHAFT, 8.0)), ops.Place("gear2", X_FRAME, (-8.0, C_SHAFT, 8.0)),
              ops.Fix("gear2")]
    if slant:
        steps += [ops.AddComponent("gear3", B_BEVEL20, B_APEX), ops.Place("gear3", X_FRAME, B_APEX), ops.Fix("gear3"),
                  ops.AddComponent("gear4", B_BEVEL30, B_APEX), ops.Place("gear4", D_FRAME, B_APEX), ops.Fix("gear4")]
    steps += [ops.Unfix("gear1"),
              ops.Mate("axis1", "coincident", "gear1:Gear Axis", "layout:S1 Axis", name="G1 on S1 Axis"),
              ops.Mate("along1", "point distance", "gear1:origin", "layout:plane1", 2.0, name="G1 along S1"),
              ops.LinkDimension("D1@G1 along S1", '"G1 Face Z"'),
              ops.Unfix("gear2"),
              ops.Mate("axis2", "coincident", "gear2:Gear Axis", "layout:S2 Axis", name="G2 on S2 Axis"),
              ops.Mate("along2", "point distance", "gear2:origin", "layout:plane3", -8.0, name="G2 along S2"),
              ops.LinkDimension("D1@G2 along S2", '"G2 Face X"')]
    if slant:
        steps += [ops.Unfix("gear3"), ops.Mate("lock1", "lock", "gear2", "gear3", name="G3 locked to G2"),
                  ops.Unfix("gear4"),
                  ops.Mate("axis4", "coincident", "gear4:Gear Axis", "layout:S3 Axis", name="G4 on S3 Axis"),
                  ops.Mate("along4", "point distance", "gear4:origin", "layout:plane2", C_SHAFT, name="G4 along S3"),
                  ops.LinkDimension("D1@G4 along S3", '"G4 Apex Y"')]
    steps.append(ops.Mate("mesh1", "gear", "gear1:Gear Axis", "gear2:Gear Axis", name="G1 meshes G2",
                          ratio=(20.0, 40.0)))
    if slant:
        steps.append(ops.Mate("mesh2", "gear", "gear3:Gear Axis", "gear4:Gear Axis", name="G3 meshes G4",
                              ratio=(20.0, 30.0)))
    return BuildPlan("gearbox", "", tuple(steps) + (ops.Rebuild(), ops.SaveAs(path)), path)


def _build_b(fake=None, **kwargs):
    fake = fake or FakeSolidWorks()
    kwargs.setdefault("parts", [plan(S17, path=H20), plan(S68, path=H40)])
    kwargs.setdefault("layout", _b_layout_plan(slant=False))
    kwargs.setdefault("assembly", _b_plan())
    kwargs.setdefault("gears", {"gear1": "G1", "gear2": "G2"})
    kwargs.setdefault("exists", fake.exists)
    kwargs.setdefault("senses", {"G1 meshes G2": B_TRUE["G1 meshes G2"]})
    return fake, swbuild.build_gearbox(fake, **kwargs)


def test_a_crossed_mesh_reads_the_skew_range_and_builds_inside_it(turned_findings):
    fake, result = _build_b()
    assert result.ok, result.log_lines()
    assert fake.turns_right("G1 meshes G2", A_ASM)
    assert _close(fake.frames["gear2-1"], (X_FRAME, (-8.0, C_SHAFT, 8.0)))   # held on Right's minus side, flipped
    assert fake.drive("gear1-1", 30.0)["gear2-1"] == pytest.approx(15.0)     # §5.2: G2 +15°


def test_a_crossed_mesh_is_refused_while_the_skew_finding_is_missing(turned_findings, monkeypatch):
    monkeypatch.delattr(findings, "TURNED_GEAR_MATE_SENSE_ANGLES_SKEW", raising=False)
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        _build_b(fake)
    assert str(raised.value) == ("The gear mate G1 meshes G2 joins gears on shafts that pass each other at an angle, "
                                 "and which way such a gear mate turns cannot be told on SolidWorks yet "
                                 "(findings.TURNED_GEAR_MATE_SENSE_ANGLES_SKEW is None), so nothing is made or "
                                 "changed.")
    assert fake.calls == []


# -- W6 Update on fixture A (W6-PLAN §2.7): the check phase reads a turned gear mate, a remake reads it back by rule H

A_TEETH = {"G1": 20, "G2": 40, "G3": 17, "G4": 51}
A_MESHES = (MeshLink("G1", "G2", -20.0 / 40, 360.0 / 40), MeshLink("G3", "G4", -17.0 / 51, 360.0 / 51))
A_LOCKS = (LockLink("G2", "G3", 360.0 / 17),)
A_MATE_REFS = (MateRef("G1 on S1 Axis", "axis", ("G1",), "S1"), MateRef("G1 along S1", "along", ("G1",), "S1"),
               MateRef("G2 on S2 Axis", "axis", ("G2",), "S2"), MateRef("G2 along S2", "along", ("G2",), "S2"),
               MateRef("G3 locked to G2", "lock", ("G2", "G3")), MateRef("G4 on S3 Axis", "axis", ("G4",), "S3"),
               MateRef("G4 along S3", "along", ("G4",), "S3"), MateRef("G1 meshes G2", "mesh", ("G1", "G2")),
               MateRef("G3 meshes G4", "mesh", ("G3", "G4")))
A_LAYOUT_VALUES = swbuild.DocumentValues(A_LAYOUT, (GlobalVariable("S1 Z", "60"), GlobalVariable("S3 X", "-68")),
                                         ("S1 Z Plane", "S3 X Plane", "S1 Axis", "S2 Axis", "S3 Axis"))


def _a_placements(teeth=None):
    teeth = teeth or A_TEETH
    frames = _a_frames()
    return [swbuild.Placement(g, f"gear{g[1]}-1", frames[g][0], frames[g][1], 360.0 / teeth[g]) for g in TRAIN_ORDER]


def _a_motion(**kwargs):
    kwargs.setdefault("mates", A_MATE_REFS)
    kwargs.setdefault("meshes", A_MESHES)
    kwargs.setdefault("locks", A_LOCKS)
    kwargs.setdefault("recorded", tuple(_a_placements()))
    kwargs.setdefault("recorded_meshes", A_MESHES)
    kwargs.setdefault("face_globals", (("G2", GlobalVariable("G2 Apex Z", "60")),))
    return swbuild.MotionUpdate(**kwargs)


def _built_a(fake=None):
    fake, result = _build_a(fake)
    assert result.ok, result.log_lines()
    fake.calls.clear()
    return fake


def _update_a(fake, **kwargs):
    kwargs.setdefault("assembly", A_ASM)
    kwargs.setdefault("placements", _a_placements())
    kwargs.setdefault("motion", _a_motion())
    kwargs.setdefault("exists", fake.exists)
    return swbuild.update_gearbox(fake, **kwargs)


def test_an_update_with_nothing_changed_reads_the_turned_gear_mate_and_puts_nothing(turned_findings):
    fake = _built_a()
    result = _update_a(fake)
    assert result.ok and result.placed == [] and result.sense_found_wrong == [], result.log_lines()
    assert [a[1] for n, a in fake.calls if n == "gear_mate_sense"] == [False, False]


def test_a_tooth_change_remakes_the_turned_gear_mate_and_reads_it_back_by_rule_h(turned_findings):
    fake = FakeSolidWorks()
    fake.turned_flip_needed = True               # made up: the remade mate (GEAR_MATE_FLIP False first) reads wrong
    fake = _built_a(fake)
    teeth = dict(A_TEETH, G1=21)
    meshes = (MeshLink("G1", "G2", -21.0 / 40, 360.0 / 40), A_MESHES[1])
    result = _update_a(fake, placements=_a_placements(teeth),
                       motion=_a_motion(meshes=meshes, ratios=(("G1 meshes G2", 21, 40),)))
    assert result.ok, result.log_lines()
    assert result.ratios == ["G1 meshes G2"] and result.turned_round == ["G1 meshes G2"]
    assert result.ratios_read == [("G1 meshes G2", 20, 40, 21, 40)] and result.placed == list(TRAIN_ORDER)
    assert fake.mate("G1 meshes G2", A_ASM).ratio == (21.0, 40.0) and fake.turns_right("G1 meshes G2", A_ASM)
    assert fake.locked_puts == []


def test_an_update_of_a_turned_gearbox_is_refused_before_anything_is_read_while_the_finding_is_missing(
        turned_findings, monkeypatch):
    fake = _built_a()
    monkeypatch.setattr(findings, "TURNED_GEAR_MATE_SENSE_READ_BACK", None)
    with pytest.raises(swbuild.BuildError) as raised:
        _update_a(fake)
    assert str(raised.value).startswith("The gear mate G1 meshes G2 joins gears on shafts that meet at an angle")
    assert not any(n in ("open_document", "gear_mate_sense") + CHANGING for n in names(fake))


@pytest.mark.parametrize("teeth2, counts", [(40, None), (41, ("G1 meshes G2", 20, 40, 20, 41))])
def test_a_crossed_mesh_whose_sense_the_workbook_changes_is_remade_and_listed_as_resensed(
        turned_findings, teeth2, counts):
    """Review M4: S2 moved to the other side of S1 turns G2 the other way (c = s1·s2 flips). The mate is remade,
    read back against the new k, listed in ``resensed``; in ``ratios`` (with its counts read) only when its ratio
    changed too; never ``sense_found_wrong``: it was not found wrong, the workbook moved."""
    fake, result = _build_b()
    assert result.ok, result.log_lines()
    fake.calls.clear()
    fake.turned_senses["G1 meshes G2"] = False                 # the truth after the move: k < 0
    mates = (MateRef("G1 on S1 Axis", "axis", ("G1",), "S1"), MateRef("G1 along S1", "along", ("G1",), "S1"),
             MateRef("G2 on S2 Axis", "axis", ("G2",), "S2"), MateRef("G2 along S2", "along", ("G2",), "S2"),
             MateRef("G1 meshes G2", "mesh", ("G1", "G2")))
    placements = [swbuild.Placement("G1", "gear1-1", IDENTITY, (0.0, 0.0, 2.0), 360.0 / 20),
                  swbuild.Placement("G2", "gear2-1", X_FRAME, (-8.0, C_SHAFT, 8.0), 360.0 / teeth2)]
    motion = swbuild.MotionUpdate(
        mates=mates, meshes=(MeshLink("G1", "G2", -20.0 / teeth2, 360.0 / teeth2),),
        recorded=tuple(swbuild.Placement(p.gear, p.component, p.rotation, p.at, 360.0 / (20 if p.gear == "G1" else 40))
                       for p in placements),
        recorded_meshes=(MeshLink("G1", "G2", 20.0 / 40, 360.0 / 40),),
        face_globals=(("G1", GlobalVariable("G1 Face Z", "2")), ("G2", GlobalVariable("G2 Face X", "8"))),
        ratios=(("G1 meshes G2", 20, teeth2),))
    result = swbuild.update_gearbox(fake, assembly=A_ASM, placements=placements, motion=motion, exists=fake.exists)
    assert result.ok, result.log_lines()
    assert result.resensed == ["G1 meshes G2"] and result.sense_found_wrong == []
    assert result.ratios == ([] if counts is None else ["G1 meshes G2"]) and result.ratios_already == []
    assert result.ratios_read == ([] if counts is None else [counts]) and result.ratios_found == []
    called = names(fake)
    assert called.index("set_gear_ratio") < called.index("gear_mate_sense")          # never read before the remake
    assert [a[1] for n, a in fake.calls if n == "gear_mate_sense"] == [False]        # read against the new k
    assert ("ok      made again to turn their gears the other way, as the workbook now has them: G1 meshes G2"
            in result.log_lines())


def test_a_sense_change_is_refused_before_anything_changes_without_the_remake_route(turned_findings, monkeypatch):
    fake, result = _build_b()
    fake.calls.clear()
    monkeypatch.setattr(findings, "GEAR_MATE_RATIO_ROUTE", None)
    mates = (MateRef("G1 on S1 Axis", "axis", ("G1",), "S1"), MateRef("G1 along S1", "along", ("G1",), "S1"),
             MateRef("G2 on S2 Axis", "axis", ("G2",), "S2"), MateRef("G2 along S2", "along", ("G2",), "S2"),
             MateRef("G1 meshes G2", "mesh", ("G1", "G2")))
    placements = [swbuild.Placement("G1", "gear1-1", IDENTITY, (0.0, 0.0, 2.0), 18.0),
                  swbuild.Placement("G2", "gear2-1", X_FRAME, (-8.0, C_SHAFT, 8.0), 9.0)]
    motion = swbuild.MotionUpdate(mates=mates, meshes=(MeshLink("G1", "G2", -0.5, 9.0),), recorded=tuple(placements),
                                  recorded_meshes=(MeshLink("G1", "G2", 0.5, 9.0),))
    # Planning lists the remake in ``ratios`` too, and the motion gate refuses it first; this is the worker's own
    # guard for a sense change it finds without one.
    with pytest.raises(swbuild.BuildError) as raised:
        swbuild.update_gearbox(fake, assembly=A_ASM, placements=placements, motion=motion, exists=fake.exists)
    assert str(raised.value) == ("The gear mate G1 meshes G2 in Bevel_Reducer.SLDASM must be made again, since the "
                                 "workbook now has it turn its gears the other way about their axes, and making a gear "
                                 "mate again has not been settled on SolidWorks (findings.GEAR_MATE_RATIO_ROUTE is "
                                 "None), so nothing is changed; build the gearbox again.")
    assert not any(n in CHANGING for n in names(fake))


# -- W6 line axes (D4, review S7): made by line_axis, read back by axis_line in Update's check phase and on reuse

def _slant_layout_plan(path=A_LAYOUT):
    return BuildPlan("layout", "", (
        ops.NewPart(""), ops.AddGlobal("S1 Z", "60"),
        ops.RefPlane("z1", "S1 Z Plane", 1, 60.0), ops.Axis("axis1", "S1 Axis", (2, "z1")),
        ops.LineAxis("line3", "S3 Axis", (-110.0, C_SHAFT, 8.0), (-0.5, math.sqrt(3) / 2, 0.0)),
        ops.Rebuild(), ops.SaveAs(path)), path)


SLANT = (-110.0, C_SHAFT, 8.0), (-0.5, math.sqrt(3) / 2, 0.0)


def test_a_slanted_axis_is_made_on_its_line_and_read_back_there():
    fake = FakeSolidWorks()
    result = swbuild.build(fake, _slant_layout_plan(), fake.exists)
    assert result.ok and "axis S3 Axis on S3 Line" in result.done, result.done
    assert [a for n, a in fake.calls if n == "line_axis"] == [("line3", "S3 Axis") + SLANT + (100.0,)]
    assert "S3 Line" in fake.made and "S3 Axis" in fake.made
    point, direction = fake.axis_line("l", "S3 Axis")
    assert swbuild._on_line((point, direction), *SLANT)
    assert swbuild._on_line((point, tuple(-v for v in direction)), *SLANT)          # either way along it
    assert not swbuild._on_line(((-110.0, C_SHAFT, 8.001), direction), *SLANT)
    assert not swbuild._on_line((point, (-0.5, 0.866, 0.0)), *SLANT)


def test_an_update_refuses_a_line_axis_moved_in_solidworks_before_anything_changes(turned_findings):
    fake = _built_a()
    values = swbuild.DocumentValues(A_LAYOUT, A_LAYOUT_VALUES.variables, A_LAYOUT_VALUES.features)
    lines = {"S1 Axis": ((0.0, 0.0, 60.0), (1.0, 0.0, 0.0))}
    assert _update_a(fake, layout=values, lines=lines).ok                  # where the record has it: nothing said
    assert [a[1] for n, a in fake.calls if n == "axis_line"] == ["S1 Axis"]
    fake.calls.clear()
    fake.moved_lines = {"S1 Axis": ((0.0, 0.0, 61.0), (1.0, 0.0, 0.0))}
    with pytest.raises(swbuild.NotAsBuilt) as raised:
        _update_a(fake, layout=values, lines=lines)
    assert str(raised.value) == ("S1's axis in the layout part is not where the record has it (it was moved in "
                                 "SolidWorks), so Update SolidWorks cannot act on it; Build again… makes a new "
                                 "revision.")
    assert not any(n in CHANGING for n in names(fake))


def test_line_axes_without_a_layout_part_are_a_fault():
    with pytest.raises(swbuild.BuildError, match="no layout part to find them in"):
        swbuild.update_gearbox(FakeSolidWorks(), assembly=A_ASM, lines={"S3 Axis": SLANT})


def test_a_reused_layout_whose_line_axis_moved_is_mismatched_not_reused():
    fake = FakeSolidWorks()
    swbuild.build(fake, _slant_layout_plan(), fake.exists)
    fake.calls.clear()
    values = swbuild.DocumentValues(A_LAYOUT, (GlobalVariable("S1 Z", "60"),), ("S1 Z Plane", "S1 Axis", "S3 Axis"))
    fake.moved_lines = {"S3 Axis": ((-110.0, C_SHAFT, 9.0), SLANT[1])}
    result = swbuild.build_gearbox(fake, [], layout=values, exists=fake.exists, lines={"S3 Axis": SLANT})
    assert result.mismatched == [(A_LAYOUT, "S3's axis in the layout part is not where the record has it (it was "
                                            "moved in SolidWorks), so Bevel_Reducer_Layout.SLDPRT cannot be reused.")]


def test_the_fakes_rebuild_carries_anchors_along_turned_axes_and_planes_as_its_globals_say(turned_findings):
    """S1 Z 60 → 64 and G2 Apex Z 60 → 64 (r2): G1 rides its X axis up (and swings, as SolidWorks may), G2 rides
    S2 up to 64 measured from Front, G3 follows G2 through its lock; G4, on Front, stays."""
    fake = _built_a()
    fake.open_document(A_LAYOUT)
    fake.set_global_variable("S1 Z", "64")
    fake.open_document(A_ASM)
    fake.set_global_variable("G2 Apex Z", "64")
    fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    g1, g2, g3, g4 = (fake.frames[f"gear{i}-1"] for i in range(1, 5))
    assert g1[1] == pytest.approx((0.0, 0.0, 64.0)) and (g1[0][2], g1[0][5], g1[0][8]) == pytest.approx((1, 0, 0))
    assert g2[1] == pytest.approx((0.0, 0.0, 64.0)) and g3[1] == pytest.approx((0.0, 0.0, 4.0))
    assert _close(g4, _a_frames()["G4"])



# -- W6: the truth by hand (W6-INTERFACES §7.18): the fake's own sense, a slip in the plan's, and fixture B driven

def test_the_fake_works_each_turned_mesh_out_as_the_hand_derivation_says(turned_findings):
    fake, result = _build_a()
    assert result.ok
    assert {n: fake._true_same(fake.mate(n, A_ASM)) for n in A_TRUE} == A_TRUE
    fake, result = _build_b(assembly=_b_plan(slant=True), layout=_b_layout_plan(),
                            parts=[plan(S17, path=p) for p in (H20, H40, B_BEVEL20, B_BEVEL30)],
                            gears=dict(TRAIN_GEARS), senses=dict(B_SENSES))
    assert result.ok, result.log_lines()
    assert {n: fake._true_same(fake.mate(n, A_ASM)) for n in B_TRUE} == B_TRUE
    assert fake.turned_senses == {}                              # worked out, never taken from the build's call


@pytest.mark.parametrize("which, wrong", [("A", "G1 meshes G2"), ("B", "G1 meshes G2"), ("B", "G3 meshes G4")])
def test_a_slip_in_a_planned_turned_sense_is_built_the_wrong_way_and_only_the_drive_shows_it(
        turned_findings, which, wrong):
    """A sense given the wrong way round, as a sign slip in planning would give it (W6-INTERFACES §7.2): the read-back
    calls the right mate wrong and "corrects" it to the other Flip, and the build reads clean. The fake, working the
    truth out itself, holds that mate turning its gears the wrong way, so the drive pinned from §5 fails — the check
    E's interference control makes on SolidWorks (review M2)."""
    if which == "A":
        senses = dict(A_SENSES, **{wrong: not A_TRUE[wrong]})
        fake, result = _build_a(senses=senses)
    else:
        senses = dict(B_SENSES, **{wrong: not B_TRUE[wrong]})
        fake, result = _build_b(assembly=_b_plan(slant=True), layout=_b_layout_plan(),
                                parts=[plan(S17, path=p) for p in (H20, H40, B_BEVEL20, B_BEVEL30)],
                                gears=dict(TRAIN_GEARS), senses=senses)
    assert result.ok and result.assembly.turned_round == [wrong], result.log_lines()
    assert not fake.turns_right(wrong, A_ASM)
    turns = fake.drive("gear1-1", 30.0)
    expected = {"A": {"gear2-1": -15.0, "gear4-1": 5.0}, "B": {"gear2-1": 15.0, "gear4-1": -10.0}}[which]
    assert any(turns[g] != pytest.approx(v) for g, v in expected.items())


def test_fixture_b_built_whole_drives_as_section_five_says(turned_findings):
    fake, result = _build_b(assembly=_b_plan(slant=True), layout=_b_layout_plan(),
                            parts=[plan(S17, path=p) for p in (H20, H40, B_BEVEL20, B_BEVEL30)],
                            gears=dict(TRAIN_GEARS), senses=dict(B_SENSES))
    assert result.ok and result.assembly.turned_round == [], result.log_lines()
    assert _close(fake.frames["gear4-1"], (D_FRAME, B_APEX))      # the slanted line holds G4 at its apex
    turns = fake.drive("gear1-1", 30.0)                          # §5.2: G2 +15, G3 +15, G4 −10
    assert turns["gear2-1"] == pytest.approx(15.0) and turns["gear3-1"] == pytest.approx(15.0)
    assert turns["gear4-1"] == pytest.approx(-10.0)



# -- W7: a planetary stage (W7-PLAN §2.6-§2.9, §4.1), planned here by hand from §4's numbers

PL = "C:\\P\\"
PL_LAYOUT, PL_CARRIER, PL_ASM = PL + "Planetary_4to1_Layout.SLDPRT", PL + "Planetary_4to1_C_Carrier.SLDPRT", \
    PL + "Planetary_4to1.SLDASM"
SUN18, PLANET18, RING54, CGEAR20 = (PL + "Sun_m1_N18.SLDPRT", PL + "Planet_m1_N18.SLDPRT", PL + "Ring_m1_N54.SLDPRT",
                                     PL + "CarrierGear_m1_N20.SLDPRT")
C_ID = "C carrier"
COPY_IDS = ("Planet copy 1", "Planet copy 2", "Planet copy 3")
Y_COPY = 15.588457268
COPY_AT = {"Planet copy 1": (18.0, 0.0), "Planet copy 2": (-9.0, Y_COPY), "Planet copy 3": (-9.0, -Y_COPY)}
PL_HANDLES = {"gear1": "Sun", "gear2c1": "Planet copy 1", "gear2c2": "Planet copy 2", "gear2c3": "Planet copy 3",
              "gear3": "Ring", "gear4": "CarrierGear"}
PL_GEARS = dict(PL_HANDLES, carrier1=C_ID)            # W7-INTERFACES §6.2: the carrier's handle names its id
# The fixture's true senses, worked out by hand (W7-INTERFACES §6.10, §7.18 of W6): Sun–Planet copy k is an outside
# mesh on alike axes, so in the carrier's frame the two turn opposite ways (k = −18/18 < 0): False; Planet copy 1–
# Ring is inside a ring on alike axes, both turning the same way relative to the carrier (k = +18/54 > 0): True.
# By Willis, (ω_s − ω_c)/(ω_r − ω_c) = −54/18 with the ring held: +30° on the sun is +7.5° on the carrier, and
# each copy turns −22.5° relative to it (−30·... ·(18/18) on 22.5 relative to the sun), −15° in the world.
PL_TRUE = {"Sun meshes Planet copy 1": False, "Sun meshes Planet copy 2": False, "Sun meshes Planet copy 3": False,
           "Planet copy 1 meshes Ring": True}
PL_SENSES = dict(PL_TRUE)


def _pl_layout_plan():
    return BuildPlan("layout", "", (
        ops.NewPart(""), ops.Axis("axis1", "S Axis", (2, 3)), ops.Axis("axis2", "C Axis", (2, 3)),
        ops.Axis("axis3", "R Axis", (2, 3)), ops.Rebuild(), ops.SaveAs(PL_LAYOUT)), PL_LAYOUT)


def _pl_carrier_plan(path=PL_CARRIER, at=None):
    """The carrier part (W7-PLAN §2.6): its own axis and one axis per copy where two offset planes cross, driven by
    the copies' literal globals; no solid."""
    at = at or COPY_AT
    steps = [ops.NewPart("")]
    for copy, (x, y) in at.items():
        stem = "P copy " + copy[-1]
        steps.append(ops.AddGlobal(f"{stem} X", repr(x)))
        if y:
            steps.append(ops.AddGlobal(f"{stem} Y", repr(y)))
    steps.append(ops.Axis("axisC", "C Axis", (2, 3)))
    for copy, (x, y) in at.items():
        k = copy[-1]
        steps.append(ops.RefPlane(f"x{k}", f"P copy {k} X Plane", 3, abs(x), x < 0))
        planes = [f"x{k}"]
        if y:
            steps.append(ops.RefPlane(f"y{k}", f"P copy {k} Y Plane", 2, abs(y), y < 0))
            planes.insert(0, f"y{k}")
        else:
            planes.insert(0, 2)
        steps.append(ops.Axis(f"axis{k}", f"P copy {k} Axis", tuple(planes)))
    return BuildPlan("carrier", "", tuple(steps) + (ops.Rebuild(), ops.SaveAs(path)), path)


def _pl_frames():
    out = {"Sun": (IDENTITY, (0.0, 0.0, 5.0)), "Ring": (IDENTITY, (0.0, 0.0, 5.0)),
           "CarrierGear": (IDENTITY, (0.0, 0.0, 27.0)), C_ID: (IDENTITY, (0.0, 0.0, 0.0))}
    for copy, (x, y) in COPY_AT.items():
        out[copy] = (_rot_z(10.0), (x, y, 5.0))
    return out


def _pl_plan(path=PL_ASM, extra_ring=(), fallback=False):
    """The 4 : 1 with the ring held (W7-PLAN §4.1, §2.7's mates): ``extra_ring`` adds gear mates between those copies
    and the ring (a doctored plan); ``fallback`` makes the spike's abandoned set instead (each body gear-mated to the
    sun at its absolute ratio: sun–carrier 18 : 72, sun–copy 18 : 36, the ring unmated)."""
    frames = _pl_frames()
    steps = [ops.NewAssembly(""), ops.AddGlobal("Sun Face Z", "5"), ops.AddGlobal("Planet Face Z", "5"),
             ops.AddComponent("layout", PL_LAYOUT), ops.Place("layout", IDENTITY, (0.0, 0.0, 0.0)), ops.Fix("layout"),
             ops.AddComponent("carrier1", PL_CARRIER), ops.Place("carrier1", *frames[C_ID]), ops.Fix("carrier1")]
    parts = {"gear1": SUN18, "gear3": RING54, "gear4": CGEAR20, **{f"gear2c{k}": PLANET18 for k in (1, 2, 3)}}
    for handle in ("gear1", "gear2c1", "gear2c2", "gear2c3", "gear3", "gear4"):
        rotation, at = frames[PL_HANDLES[handle]]
        steps += [ops.AddComponent(handle, parts[handle], at), ops.Place(handle, rotation, at), ops.Fix(handle)]
    steps += [ops.Unfix("gear1"),
              ops.Mate("axis1", "coincident", "gear1:Gear Axis", "layout:S Axis", name="Sun on S Axis"),
              ops.Mate("along1", "point distance", "gear1:origin", "layout:plane1", 5.0, name="Sun along S"),
              ops.LinkDimension("D1@Sun along S", '"Sun Face Z"'),
              ops.Unfix("carrier1"),
              ops.Mate("axis2", "coincident", "carrier1:C Axis", "layout:C Axis", name="C carrier on C Axis"),
              ops.Mate("along2", "point", "carrier1:origin", "layout:plane1", name="C carrier along C"),
              ops.Unfix("gear4"), ops.Mate("lock1", "lock", "carrier1", "gear4", name="CarrierGear locked to C carrier")]
    for k in (1, 2, 3):
        steps += [ops.Unfix(f"gear2c{k}"),
                  ops.Mate(f"axis{k + 2}", "coincident", f"gear2c{k}:Gear Axis", f"carrier1:P copy {k} Axis",
                           name=f"Planet copy {k} on P copy {k} Axis"),
                  ops.Mate(f"along{k + 2}", "point distance", f"gear2c{k}:origin", "layout:plane1", 5.0,
                           name=f"Planet copy {k} along P copy {k}"),
                  ops.LinkDimension(f"D1@Planet copy {k} along P copy {k}", '"Planet Face Z"')]
    if fallback:
        steps.append(ops.Mate("mesh0", "gear", "gear1:Gear Axis", "carrier1:C Axis", name="Sun meshes C carrier",
                              ratio=(18.0, 72.0)))
        for k in (1, 2, 3):
            steps.append(ops.Mate(f"mesh{k}", "gear", "gear1:Gear Axis", f"gear2c{k}:Gear Axis",
                                  name=f"Sun meshes Planet copy {k}", ratio=(18.0, 36.0)))
    else:
        for k in (1, 2, 3):
            steps.append(ops.Mate(f"mesh{k}", "gear", "gear1:Gear Axis", f"gear2c{k}:Gear Axis",
                                  name=f"Sun meshes Planet copy {k}", ratio=(18.0, 18.0)))
        for k in (1,) + tuple(extra_ring):
            steps.append(ops.Mate(f"ring{k}", "gear", f"gear2c{k}:Gear Axis", "gear3:Gear Axis",
                                  name=f"Planet copy {k} meshes Ring", ratio=(18.0, 54.0)))
    return BuildPlan("gearbox", "", tuple(steps) + (ops.Rebuild(), ops.SaveAs(path)), path)


def _build_pl(fake=None, **kwargs):
    fake = fake or FakeSolidWorks()
    kwargs.setdefault("parts", [plan(S17, path=p) for p in (SUN18, PLANET18, RING54, CGEAR20)])
    kwargs.setdefault("layout", _pl_layout_plan())
    kwargs.setdefault("assembly", _pl_plan())
    kwargs.setdefault("gears", dict(PL_GEARS))
    kwargs.setdefault("exists", fake.exists)
    kwargs.setdefault("senses", dict(PL_SENSES))
    kwargs.setdefault("carriers", [_pl_carrier_plan()])
    return fake, swbuild.build_gearbox(fake, **kwargs)


def test_the_planetary_plans_here_are_sound():
    assert _pl_plan().check() == [] and _pl_carrier_plan().check() == [] and _pl_layout_plan().check() == []


def test_a_planetary_builds_its_carrier_part_after_the_layout_and_before_the_assembly(turned_findings):
    fake, steps = FakeSolidWorks(), []
    fake, result = _build_pl(fake, progress=steps.append)
    assert result.ok and result.kind == swbuild.GEARBOX_MOTION, result.log_lines()
    order = [step.stage for step in steps]
    assert order.index(swbuild.STAGE_LAYOUT) < order.index(swbuild.STAGE_CARRIER) < order.index(swbuild.STAGE_ASSEMBLY)
    assert [s.name for s in steps if s.stage == swbuild.STAGE_CARRIER] == ["Planetary_4to1_C_Carrier"]
    assert len(result.carriers) == 1 and result.carriers[0].saved == PL_CARRIER
    assert result.components["carrier1"] == "carrier1-1"                         # W7-INTERFACES §6.2
    assert any(line.startswith("build   ") and "carrier" in line for line in result.log_lines())


def test_a_planetary_is_mated_as_section_two_seven_says_and_its_ring_mate_turned_round(turned_findings):
    fake, result = _build_pl()
    assert result.ok, result.log_lines()
    # The spike, 2026: the ring mate made with the first Flip read wrong and was remade the other way round.
    assert result.assembly.turned_round == ["Planet copy 1 meshes Ring"]
    assert result.assembly.mate_problems == []
    statuses = {h: fake.constrained_status(h) for h in ("gear1", "carrier1", "gear2c1", "gear2c2", "gear2c3", "gear4")}
    assert set(statuses.values()) == {findings.COMPONENT_UNDER_DEFINED}, statuses
    assert fake.constrained_status("gear3") == findings.COMPONENT_FULLY_DEFINED          # the ring stays fixed
    (lock,) = [a for n, a in fake.calls if n == "add_mate" and a[0] == "lock"]
    assert lock[1:3] == ("carrier1", "gear4")                                        # the carrier first, as anchor
    assert {n: fake._true_same(fake.mate(n, PL_ASM)) for n in PL_TRUE} == PL_TRUE       # the truth by hand
    for gear, frame in _pl_frames().items():
        handle = next(h for h, g in PL_GEARS.items() if g == gear)
        assert _close(fake.frames[f"{handle}-1"], frame), gear


def _pl_drive_check(turns, carrier, copy, ring=0.0):
    assert turns["carrier1-1"] == pytest.approx(carrier) and turns["gear4-1"] == pytest.approx(carrier)
    for k in (1, 2, 3):
        assert turns[f"gear2c{k}-1"] == pytest.approx(copy)
    assert turns.get("gear3-1", 0.0) == pytest.approx(ring)


def test_the_fake_drives_the_planetary_as_the_spike_measured_the_right_mates(turned_findings):
    """W7-SPIKE.md, J5's set: sun +30° → carrier +7.5°, each copy −15° (−22.5° on C), ring 0, the copies carried to
    (17.846008, 2.349471), (−10.957706, 14.280360), (−6.888302, −16.629832)."""
    fake, result = _build_pl()
    assert result.ok
    _pl_drive_check(fake.drive("gear1-1", 30.0), 7.5, -15.0)
    spots = [(17.846008, 2.349471), (-10.957706, 14.280360), (-6.888302, -16.629832)]
    for k, spot in zip((1, 2, 3), spots):
        assert fake.frames[f"gear2c{k}-1"][1][:2] == pytest.approx(spot, abs=1e-6)
        assert fake.frames[f"gear2c{k}-1"][1][2] == pytest.approx(5.0)
    assert fake.frames["gear4-1"][1] == pytest.approx((0.0, 0.0, 27.0))             # turned on its axis, unmoved


def test_the_fake_drives_the_ring_mate_made_the_first_way_round_as_the_spike_did(turned_findings):
    """W7-SPIKE.md: the same set with the ring mate left at Flip False turned the carrier −15° and the planets −60°."""
    fake, result = _build_pl(senses=None)                      # nothing read back: every mate as first made
    assert result.ok and result.assembly.turned_round == []
    assert not fake.turns_right("Planet copy 1 meshes Ring", PL_ASM)
    _pl_drive_check(fake.drive("gear1-1", 30.0), -15.0, -60.0)


def test_the_fake_drives_the_abandoned_fallback_as_wrongly_as_the_spike_did(turned_findings):
    """W7-SPIKE.md: each body gear-mated to the sun at its absolute ratio turned the carrier +7.5° but the planets
    −3.75° where −15° is right. The coaxial sun–carrier mate's Flip as the spike made it was not recorded: the fake
    is told it turned the carrier the sun's way."""
    fake = FakeSolidWorks()
    fake.never_right = {"Sun meshes C carrier"}
    fake, result = _build_pl(fake, assembly=_pl_plan(fallback=True), senses=None)
    assert result.ok, result.log_lines()
    turns = fake.drive("gear1-1", 30.0)
    assert turns["carrier1-1"] == pytest.approx(7.5)
    assert all(turns[f"gear2c{k}-1"] == pytest.approx(-3.75) for k in (1, 2, 3))


def test_a_slip_in_the_planned_ring_sense_builds_the_wrong_way_and_the_drive_shows_it(turned_findings):
    senses = dict(PL_SENSES, **{"Planet copy 1 meshes Ring": not PL_TRUE["Planet copy 1 meshes Ring"]})
    fake, result = _build_pl(senses=senses)
    assert result.ok and result.assembly.turned_round == []    # read "right" against the wrong sense, left as made
    turns = fake.drive("gear1-1", 30.0)
    assert turns["carrier1-1"] != pytest.approx(7.5)


def test_a_second_ring_mate_over_defines_the_planetary_and_the_build_stops_keeping_its_parts(turned_findings):
    """Judged by the rank of the carrier-frame rows (W7-PLAN §2.9, S12): Planet copy 2 meshes Ring adds nothing."""
    senses = dict(PL_SENSES, **{"Planet copy 2 meshes Ring": True})
    fake, result = _build_pl(assembly=_pl_plan(extra_ring=(2,)), senses=senses)
    assert not result.ok and result.assembly.mate_problems == ["The mate Planet copy 2 meshes Ring over-defines the "
                                                               "assembly."]
    assert result.layout.saved and result.carriers[0].saved and not result.assembly.saved
    assert any(line.startswith("STOPPED") and "the carrier part" in line for line in result.log_lines())


def test_a_carrier_part_that_fails_skips_the_assembly(turned_findings):
    fake = FakeSolidWorks(fail_on={"ref_plane": ("P copy 2 X Plane", "SolidWorks would not make the plane.")})
    fake, result = _build_pl(fake)
    assert not result.ok and result.assembly is None and result.layout.saved
    assert result.skipped == "the assembly, because the carrier part Planetary_4to1_C_Carrier.SLDPRT failed"
    assert not any(n == "new_assembly" for n in names(fake))


def test_a_reused_carrier_part_is_checked_live_and_a_changed_one_is_mismatched(turned_findings):
    fake = FakeSolidWorks()
    swbuild.build(fake, _pl_carrier_plan(), fake.exists)
    values = (GlobalVariable("P copy 1 X", "18.0"), GlobalVariable("P copy 2 X", "-9.0"),
              GlobalVariable("P copy 2 Y", repr(Y_COPY)), GlobalVariable("P copy 3 X", "-9.0"),
              GlobalVariable("P copy 3 Y", repr(-Y_COPY)))
    features = ("C Axis",) + tuple(f"P copy {k} Axis" for k in (1, 2, 3))
    reuse = swbuild.DocumentValues(PL_CARRIER, values, features)
    fake2, result = _build_pl(fake, carriers=[reuse])
    assert result.ok and result.carriers_reused == [PL_CARRIER] and PL_CARRIER in result.checked, result.log_lines()
    assert "ok      carrier part Planetary_4to1_C_Carrier.SLDPRT reused" in result.log_lines()
    moved = swbuild.DocumentValues(PL_CARRIER, (GlobalVariable("P copy 1 X", "19.5"),) + values[1:], features)
    fake = FakeSolidWorks()
    swbuild.build(fake, _pl_carrier_plan(), fake.exists)
    _, result = _build_pl(fake, carriers=[moved], assembly=_pl_plan(path=PL + "Other.SLDASM"))
    assert [p for p, _ in result.mismatched] == [PL_CARRIER] and result.assembly is None


# -- W7 Update on the 4 : 1 (W7-PLAN §2.9, §5.4)

PL_TEETH = {"Sun": 18, "Ring": 54, "CarrierGear": 20, **{c: 18 for c in COPY_IDS}}
PL_ORDER = ("Sun",) + COPY_IDS + ("Ring", "CarrierGear", C_ID)
PL_COMPONENT = {g: f"{h}-1" for h, g in PL_GEARS.items()}


def _pl_placements(frames=None):
    frames = frames or _pl_frames()
    return [swbuild.Placement(g, PL_COMPONENT[g], frames[g][0], frames[g][1],
                              0.0 if g == C_ID else 360.0 / PL_TEETH[g]) for g in PL_ORDER]


PL_MESHES = tuple(MeshLink("Sun", c, -1.0, 20.0, carrier=C_ID) for c in COPY_IDS) + \
    tuple(MeshLink(c, "Ring", 18 / 54, 360 / 54, carrier=C_ID) for c in COPY_IDS)     # the unmated ones judged too
PL_REFS = (MateRef("Sun on S Axis", "axis", ("Sun",), "S"), MateRef("Sun along S", "along", ("Sun",), "S"),
           MateRef("C carrier on C Axis", "axis", (C_ID,), "C"), MateRef("C carrier along C", "along", (C_ID,), "C"),
           MateRef("CarrierGear locked to C carrier", "lock", (C_ID, "CarrierGear"))) + \
    tuple(r for k in (1, 2, 3) for r in (MateRef(f"Planet copy {k} on P copy {k} Axis", "axis",
                                                 (f"Planet copy {k}",), f"P copy {k}"),
                                         MateRef(f"Planet copy {k} along P copy {k}", "along",
                                                 (f"Planet copy {k}",), f"P copy {k}"))) + \
    tuple(MateRef(f"Sun meshes Planet copy {k}", "mesh", ("Sun", f"Planet copy {k}")) for k in (1, 2, 3)) + \
    (MateRef("Planet copy 1 meshes Ring", "mesh", ("Planet copy 1", "Ring")),)
PL_LINK = CarrierLink(C_ID, COPY_IDS, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
PL_CARRIER_VALUES = swbuild.DocumentValues(PL_CARRIER, (
    GlobalVariable("P copy 1 X", "18.0"), GlobalVariable("P copy 2 X", "-9.0"),
    GlobalVariable("P copy 2 Y", repr(Y_COPY)), GlobalVariable("P copy 3 X", "-9.0"),
    GlobalVariable("P copy 3 Y", repr(-Y_COPY))))


def _pl_motion(**kwargs):
    kwargs.setdefault("mates", PL_REFS)
    kwargs.setdefault("meshes", PL_MESHES)
    kwargs.setdefault("locks", (LockLink(C_ID, "CarrierGear", 0.0),))
    kwargs.setdefault("recorded", tuple(_pl_placements()))
    kwargs.setdefault("recorded_meshes", PL_MESHES)
    kwargs.setdefault("face_globals", (("Sun", GlobalVariable("Sun Face Z", "5")),
                                       ("Planet", GlobalVariable("Planet Face Z", "5"))))
    kwargs.setdefault("fixed", ("Ring",))
    kwargs.setdefault("carriers", (PL_LINK,))
    kwargs.setdefault("held", ("Ring",))
    return swbuild.MotionUpdate(**kwargs)


def _built_pl():
    fake, result = _build_pl()
    assert result.ok, result.log_lines()
    fake.calls.clear()
    return fake


def _update_pl(fake, **kwargs):
    kwargs.setdefault("assembly", PL_ASM)
    kwargs.setdefault("placements", _pl_placements())
    kwargs.setdefault("motion", _pl_motion())
    kwargs.setdefault("carriers", [PL_CARRIER_VALUES])
    kwargs.setdefault("exists", fake.exists)
    return swbuild.update_gearbox(fake, **kwargs)


def _puts(fake):
    return [a[0] for n, a in fake.calls if n == "place_component"]


def test_a_planetary_turned_consistently_is_left_where_it_stands(turned_findings):
    fake = _built_pl()
    fake.drive("gear1-1", 37.0)
    fake.calls.clear()
    result = _update_pl(fake)
    assert result.ok and result.turned and result.out_of_step == [] and result.off_axis == [], result.log_lines()
    assert result.placed == [] and _puts(fake) == []
    assert result.carriers and result.carriers[0].unchanged                       # its values read and held


def test_the_carrier_turned_off_willis_with_the_ring_mate_suppressed_is_out_of_step_and_put_back(turned_findings):
    """Review M1 scenario 1: with the ring mate off, the sun mates still hold, so a carrier turn the ring mesh
    forbids shows only through the held ring; Update turns the mate back on and puts the train back, carrier
    first."""
    fake = _built_pl()
    fake.mate("Planet copy 1 meshes Ring", PL_ASM).suppressed = True
    fake.drive("gear1-1", 30.0)                                   # the carrier is free now: it stays, the copies turn
    fake.calls.clear()
    result = _update_pl(fake)
    assert ("Planet copy 1", "Ring") in result.out_of_step, result.log_lines()
    assert result.ok and result.unsuppressed == ["Planet copy 1 meshes Ring"], result.log_lines()
    puts = _puts(fake)
    assert puts.index("placed7") < min(puts.index(f"placed{i}") for i in (1, 2, 3, 4)) and "placed5" not in puts
    for gear, frame in _pl_frames().items():
        assert _close(fake.frames[PL_COMPONENT[gear]], frame), gear


def test_a_held_ring_put_back_goes_first_then_the_carrier_then_the_train(turned_findings, monkeypatch):
    """Review M1 scenario 2 and M5: the train turned by the user, then the ring knocked off its place; Update
    re-places the held ring first (the fixed route), then the carrier, then every gear, and the post-check is
    clean."""
    monkeypatch.setattr(findings, "REPLACE_FIXED_ROUTE", "Transform2 put")
    fake = _built_pl()
    fake.drive("gear1-1", 37.0)
    fake.turn("gear3-1", 2.0)                                     # not a whole pitch: off its place
    fake.calls.clear()
    result = _update_pl(fake)
    assert result.ok and "Ring" in result.off_axis, result.log_lines()
    puts = _puts(fake)
    assert puts[0] == "placed5" and puts[1] == "placed7" and set(puts[2:]) == {f"placed{i}" for i in (1, 2, 3, 4, 6)}
    assert "CarrierGear locked to C carrier" in [fake.mate_handles[a[0]] for n, a in fake.calls
                                                 if n == "set_mate_suppressed" and a[1] is True]
    assert not fake.mate("CarrierGear locked to C carrier", PL_ASM).suppressed and fake.locked_puts == []
    for gear, frame in _pl_frames().items():
        assert _close(fake.frames[PL_COMPONENT[gear]], frame), gear


def test_a_carrier_globals_change_updates_the_carrier_part_and_puts_the_swung_train_back(turned_findings):
    fake = _built_pl()
    at = {"Planet copy 1": (19.5, 0.0), "Planet copy 2": (-9.75, 16.887495374),
          "Planet copy 3": (-9.75, -16.887495374)}
    values = swbuild.DocumentValues(PL_CARRIER, (
        GlobalVariable("P copy 1 X", "19.5"), GlobalVariable("P copy 2 X", "-9.75"),
        GlobalVariable("P copy 2 Y", "16.887495374"), GlobalVariable("P copy 3 X", "-9.75"),
        GlobalVariable("P copy 3 Y", "-16.887495374")))
    frames = dict(_pl_frames(), **{c: (_rot_z(10.0), (x, y, 5.0)) for c, (x, y) in at.items()})
    result = _update_pl(fake, carriers=[values], placements=_pl_placements(frames))
    assert result.ok, result.log_lines()
    assert result.carriers[0].changed and PL_CARRIER in result.changed
    for copy in COPY_IDS:
        assert _close(fake.frames[PL_COMPONENT[copy]], frames[copy]), copy


def test_a_planetary_update_without_its_carrier_parts_is_refused_before_anything_is_read(turned_findings):
    fake = _built_pl()
    with pytest.raises(swbuild.BuildError) as raised:
        _update_pl(fake, carriers=[])
    assert str(raised.value) == ("Update SolidWorks was given a planetary stage without its carrier part, so nothing "
                                 "is changed; that is a fault in Gear Generator.")
    assert fake.calls == []


def test_a_planetary_record_the_check_cannot_judge_is_refused_with_a_sentence(turned_findings):
    fake = _built_pl()
    stray = (MeshLink("Sun", "Planet copy 1", -1.0, 20.0, carrier="D carrier"),)
    with pytest.raises(swbuild.BuildError) as raised:
        _update_pl(fake, motion=_pl_motion(recorded_meshes=stray))
    assert str(raised.value).startswith("Update SolidWorks cannot judge the gears on record: The mesh Sun–Planet copy 1 "
                                        "is measured against D carrier")
    assert str(raised.value).endswith("So nothing is changed; that is a fault in Gear Generator.")
    assert not any(n in CHANGING for n in names(fake))


# -- W7: the cases the spike did not build (W7-PLAN §4.2-§4.4), planned here by hand; each drive is Willis worked out
# by hand for sun 18, planet 18, ring 54: in the carrier's frame (ω_s − ω_c)·18 = −(ω_p − ω_c)·18 (an outside mesh)
# and (ω_p − ω_c)·18 = (ω_r − ω_c)·54 (inside the ring), every turn about the gear's own axis.

F_MINUS = (1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0)      # base_frame(Z-): rot_x(180°)


def _pl_case(held="ring", minus=False, path=PL_ASM):
    """The 4 : 1's mates with ``held`` the member that stays fixed (W7-PLAN §2.7, §4.2, §4.4): a held sun or ring
    never unfixed and never mated to its shaft; a held carrier fixed with CarrierGear, neither mated, its copies still
    mated to its axes. ``minus``: the stage on Z− (§4.3): every frame F₋·rot_z(θ), the copies where F₋ puts the
    offsets (y negated), the front faces at z −5, held there by flipped point distances."""
    f = F_MINUS if minus else IDENTITY
    z_face, z_gear = (-5.0, -27.0) if minus else (5.0, 27.0)
    copies = {c: (x, -y if minus else y) for c, (x, y) in COPY_AT.items()}
    frames = {"Sun": (f, (0.0, 0.0, z_face)), "Ring": (f, (0.0, 0.0, z_face)), "CarrierGear": (f, (0.0, 0.0, z_gear)),
              C_ID: (f, (0.0, 0.0, 0.0)), **{c: (_mul(f, _rot_z(10.0)), (x, y, z_face)) for c, (x, y) in copies.items()}}
    steps = [ops.NewAssembly(""), ops.AddGlobal("Sun Face Z", "5"), ops.AddGlobal("Ring Face Z", "5"),
             ops.AddGlobal("Planet Face Z", "5"),
             ops.AddComponent("layout", PL_LAYOUT), ops.Place("layout", IDENTITY, (0.0, 0.0, 0.0)), ops.Fix("layout"),
             ops.AddComponent("carrier1", PL_CARRIER), ops.Place("carrier1", *frames[C_ID]), ops.Fix("carrier1")]
    parts = {"gear1": SUN18, "gear3": RING54, "gear4": CGEAR20, **{f"gear2c{k}": PLANET18 for k in (1, 2, 3)}}
    for handle in ("gear1", "gear2c1", "gear2c2", "gear2c3", "gear3", "gear4"):
        rotation, at = frames[PL_HANDLES[handle]]
        steps += [ops.AddComponent(handle, parts[handle], at), ops.Place(handle, rotation, at), ops.Fix(handle)]
    sign = -1.0 if minus else 1.0
    for handle, gear, shaft in (("gear1", "Sun", "S"), ("gear3", "Ring", "R")):
        if held == gear.lower():
            continue
        steps += [ops.Unfix(handle),
                  ops.Mate(f"axis{gear}", "coincident", f"{handle}:Gear Axis", f"layout:{shaft} Axis",
                           name=f"{gear} on {shaft} Axis"),
                  ops.Mate(f"along{gear}", "point distance", f"{handle}:origin", "layout:plane1", sign * 5.0,
                           name=f"{gear} along {shaft}"),
                  ops.LinkDimension(f"D1@{gear} along {shaft}", f'"{gear} Face Z"')]
    if held != "carrier":
        steps += [ops.Unfix("carrier1"),
                  ops.Mate("axisC", "coincident", "carrier1:C Axis", "layout:C Axis", name="C carrier on C Axis"),
                  ops.Mate("alongC", "point", "carrier1:origin", "layout:plane1", name="C carrier along C"),
                  ops.Unfix("gear4"),
                  ops.Mate("lock1", "lock", "carrier1", "gear4", name="CarrierGear locked to C carrier")]
    for k in (1, 2, 3):
        steps += [ops.Unfix(f"gear2c{k}"),
                  ops.Mate(f"axis{k}", "coincident", f"gear2c{k}:Gear Axis", f"carrier1:P copy {k} Axis",
                           name=f"Planet copy {k} on P copy {k} Axis"),
                  ops.Mate(f"along{k}", "point distance", f"gear2c{k}:origin", "layout:plane1", sign * 5.0,
                           name=f"Planet copy {k} along P copy {k}"),
                  ops.LinkDimension(f"D1@Planet copy {k} along P copy {k}", '"Planet Face Z"')]
    for k in (1, 2, 3):
        steps.append(ops.Mate(f"mesh{k}", "gear", "gear1:Gear Axis", f"gear2c{k}:Gear Axis",
                              name=f"Sun meshes Planet copy {k}", ratio=(18.0, 18.0)))
    steps.append(ops.Mate("ring1", "gear", "gear2c1:Gear Axis", "gear3:Gear Axis", name="Planet copy 1 meshes Ring",
                          ratio=(18.0, 54.0)))
    return BuildPlan("gearbox", "", tuple(steps) + (ops.Rebuild(), ops.SaveAs(path)), path), frames


def _built_case(held="ring", minus=False):
    assembly, frames = _pl_case(held, minus)
    fake, result = _build_pl(assembly=assembly)
    assert result.ok and result.assembly.turned_round == ["Planet copy 1 meshes Ring"], result.log_lines()
    for gear, frame in frames.items():
        assert _close(fake.frames[PL_COMPONENT[gear]], frame), gear      # the rebuild left every body placed
    return fake


def test_the_fake_says_which_components_are_fixed_and_where_each_comes_from_even_from_a_copy(turned_findings):
    """The fake's ``is_fixed`` and ``component_path`` on the 4 : 1 with the ring held: the layout and the ring stay
    fixed, a planet copy floats; every component comes from the build folder, and from the copy once the folder is
    copied and the master gone."""
    fake = _built_case(held="ring")
    assert fake.is_fixed("layout") and fake.is_fixed("gear3")
    assert not fake.is_fixed("gear2c1") and not fake.is_fixed("gear1")
    handles = ("layout", "carrier1", "gear1", "gear2c1", "gear2c2", "gear2c3", "gear3", "gear4")
    assert all(fake.component_path(h).startswith(PL) for h in handles)
    assert fake.component_path("gear2c2") == PLANET18
    fake.copied(PL, "C:\\Copy\\")
    fake.open_document("C:\\Copy\\Planetary_4to1.SLDASM")
    for index, handle in enumerate(handles):
        fake.find_component(f"copy{index}", f"{handle}-1")
        assert fake.component_path(f"copy{index}") == "C:\\Copy\\" + fake.component_paths[f"{handle}-1"][len(PL):]
    assert fake.is_fixed("copy6") and not fake.is_fixed("copy3")


def test_the_sun_held_drives_from_the_ring_at_four_to_three(turned_findings):
    """§4.2. ω_s = 0, ring +30°: (0 − ω_c)·18 = −(ω_p − ω_c)·18 gives ω_p − ω_c = ω_c; (ω_p − ω_c)·18 = (30 −
    ω_c)·54 gives ω_c = 3·(30 − ω_c), so ω_c = +22.5° (ring : carrier = 30 : 22.5 = 4 : 3, the same way), each copy
    +22.5° on the carrier, +45° about its own axis; the sun stays."""
    fake = _built_case(held="sun")
    assert fake.constrained_status("gear1") == findings.COMPONENT_FULLY_DEFINED
    turns = fake.drive("gear3-1", 30.0)
    assert turns["carrier1-1"] == pytest.approx(22.5) and turns["gear4-1"] == pytest.approx(22.5)
    assert all(turns[f"gear2c{k}-1"] == pytest.approx(45.0) for k in (1, 2, 3)) and "gear1-1" not in turns
    assert _close(fake.frames["gear1-1"], (IDENTITY, (0.0, 0.0, 5.0)))


def test_the_carrier_held_is_a_plain_train_turning_the_ring_back_at_a_third(turned_findings):
    """§4.4. ω_c = 0, sun +30°: 30·18 = −ω_p·18 gives each copy −30°; ω_p·18 = ω_r·54 gives the ring −10° (−1/3 of
    the sun: 3 : 1 the other way); the carrier, CarrierGear and the copies' places stay."""
    fake = _built_case(held="carrier")
    assert fake.constrained_status("carrier1") == findings.COMPONENT_FULLY_DEFINED
    assert fake.constrained_status("gear4") == findings.COMPONENT_FULLY_DEFINED
    assert not any(a[0] == "lock" for n, a in fake.calls if n == "add_mate")       # nothing locks a held carrier
    turns = fake.drive("gear1-1", 30.0)
    assert turns["gear3-1"] == pytest.approx(-10.0)
    assert all(turns[f"gear2c{k}-1"] == pytest.approx(-30.0) for k in (1, 2, 3)) and "carrier1-1" not in turns
    for copy, (x, y) in COPY_AT.items():
        assert fake.frames[PL_COMPONENT[copy]][1] == pytest.approx((x, y, 5.0))


def test_the_stage_on_z_minus_turns_as_the_z_plus_one_about_each_gears_own_axis(turned_findings):
    """§4.3. Every axis points −Z, so every gear's own-axis turn is the Z+ stage's (the rows hold own-axis turns,
    and every axis against the carrier's is +1): sun +30° → carrier +7.5°, each copy −15°. Seen from +Z every turn
    is reversed, so copy 1 at (18, 0) is carried round −7.5° about +Z, to (17.846008, −2.349471): what flips is the
    world's view of the turns and of the copies' places (y negated by F₋), not the speeds."""
    fake = _built_case(minus=True)
    turns = fake.drive("gear1-1", 30.0)
    assert turns["carrier1-1"] == pytest.approx(7.5)
    assert all(turns[f"gear2c{k}-1"] == pytest.approx(-15.0) for k in (1, 2, 3))
    assert fake.frames["gear2c1-1"][1] == pytest.approx((17.846008, -2.349471, -5.0), abs=1e-6)
    assert fake.frames["gear2c2-1"][1][:2] == pytest.approx((-10.957706, -14.280360), abs=1e-6)


def test_a_mesh_the_change_phase_cannot_judge_is_a_failure_sentence_not_a_bare_error(turned_findings):
    fake = _built_pl()
    stray = PL_MESHES + (MeshLink("Sun", "Planet copy 1", -1.0, 20.0, carrier="D carrier"),)
    result = _update_pl(fake, motion=_pl_motion(meshes=stray))
    assert not result.ok
    (failure,) = [why for _, why in result.failures]
    assert failure.startswith("Update SolidWorks cannot judge the gears on record: The mesh Sun–Planet copy 1 is "
                              "measured against D carrier") and failure.endswith("That is a fault in Gear Generator.")
    assert not any(m.suppressed for m in fake.memory_mates[_key(PL_ASM)])


def test_a_held_ring_joins_a_train_through_its_gear_mate_only(turned_findings):
    """W7-PLAN §2.9: the unmated ring meshes do not join trains; they are judged inside the train the ring mate
    makes, so one copy turned alone shows as out of step through them."""
    fake = _built_pl()
    fake.turn("gear2c2-1", 3.0)                     # copy 2 alone: its sun mate and its unmated ring mesh both see it
    fake.calls.clear()
    result = _update_pl(fake)
    assert ("Sun", "Planet copy 2") in result.out_of_step and ("Planet copy 2", "Ring") in result.out_of_step
    assert result.ok and set(_puts(fake)) == {f"placed{i}" for i in (1, 2, 3, 4, 6, 7)}, result.log_lines()


def test_placed_lists_a_planetary_trains_puts_in_the_order_they_were_made(turned_findings, monkeypatch):
    """W7-INTERFACES §6.13 as the result says it: ``placed`` is appended straight after each put, so it is the order
    made — a held member off its place first, then the carrier, then every other gear in the train's order."""
    monkeypatch.setattr(findings, "REPLACE_FIXED_ROUTE", "Transform2 put")
    fake = _built_pl()
    frames = dict(_pl_frames(), Ring=(IDENTITY, (0.0, 0.0, 7.0)))           # Ring At 10 → 12
    result = _update_pl(fake, placements=_pl_placements(frames))
    assert result.ok, result.log_lines()
    assert result.placed == ["Ring", C_ID, "Sun"] + list(COPY_IDS) + ["CarrierGear"]
    assert result.placed == [next(p.gear for p in _pl_placements() if p.component == fake._name2(h))
                             for h in _puts(fake)]                          # the same order as the calls made
    fake = _built_pl()
    frames = dict(_pl_frames(), **{c: (_rot_z(10.0), (x, y, 7.0)) for c, (x, y) in COPY_AT.items()})
    motion = _pl_motion(face_globals=(("Sun", GlobalVariable("Sun Face Z", "5")),
                                      ("Planet", GlobalVariable("Planet Face Z", "7"))))
    result = _update_pl(fake, placements=_pl_placements(frames), motion=motion)    # Planet At 10 → 12
    assert result.ok, result.log_lines()
    assert result.placed == [C_ID, "Sun"] + list(COPY_IDS) + ["CarrierGear"]


# -- W8-INTERFACES §9.2: a record carrying modes never goes down W7's path. Since the Update across configurations
# is written, a record with its configurations takes that path; one carrying anything of modes without them is a fault

_MESH = swbuild.MateRef("G1 meshes G2", "mesh", ("G1", "G2"))
_W7 = swbuild.MotionUpdate(mates=(_MESH,), meshes=(swbuild.MeshLink("G1", "G2", -0.5, 10.0),),
                           locks=(swbuild.LockLink("G2", "G3", 10.0),))


@pytest.mark.parametrize("motion", [
    replace(_W7, slide_values=(("RangeSlv along Rear", "4L", 46.0),)),
    replace(_W7, on_sets=(("RangeSlv engages LoDog", ("4L",)),)),
    replace(_W7, mode_placements=(("4L", ()),)),
    replace(_W7, recorded_by_mode=(("4L", ()),)),
    replace(_W7, mates=(replace(_MESH, modes=("4L",)),)),
    replace(_W7, mates=(replace(_MESH, values=(("4L", 46.0),)),)),
    replace(_W7, mates=(swbuild.MateRef("RangeSlv along Rear", "slide", ("RangeSlv",)),)),
    replace(_W7, mates=(swbuild.MateRef("ModeSlv splined to RangeSlv", "spline", ("RangeSlv", "ModeSlv")),)),
    replace(_W7, mates=(swbuild.MateRef("RangeSlv engages InDog", "couple", ("RangeSlv", "InDog")),)),
    replace(_W7, meshes=(swbuild.MeshLink("G1", "G2", -0.5, 10.0, modes=("4L",)),)),
    replace(_W7, recorded_meshes=(swbuild.MeshLink("G1", "G2", -0.5, 10.0, modes=("4L",)),)),
    replace(_W7, locks=(swbuild.LockLink("G2", "G3", 10.0, modes=("4L",)),)),
])
def test_a_record_carrying_modes_without_its_configurations_is_refused_before_anything_is_read(motion):
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        swbuild.update_gearbox(fake, assembly=r"C:\T\R.SLDASM", motion=motion, exists=lambda _p: True)
    assert str(raised.value) == ("Update SolidWorks was given a gearbox with modes but not its configurations, so "
                                 "nothing was read or changed; that is a fault in Gear Generator.")
    assert fake.calls == []


def test_an_update_of_a_gearbox_with_modes_is_refused_before_anything_is_read_while_a_finding_is_unsettled(
        mode_findings, monkeypatch):
    monkeypatch.setattr(findings, "CONFIGURATION_SHOW_ROUTE", None, raising=False)
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        swbuild.update_gearbox(fake, assembly=r"C:\T\R.SLDASM", motion=replace(_W7, configurations=("2H", "4H")),
                               exists=lambda _p: True)
    assert str(raised.value) == ("Working with an assembly's configurations has not been settled on SolidWorks "
                                 "(findings.CONFIGURATION_SHOW_ROUTE is None), so a gearbox with modes is not updated "
                                 "and nothing was read or changed.")
    assert fake.calls == []


@pytest.mark.parametrize("finding, value", [("VALUE_READ_ORDER", None),
                                            ("VALUE_READ_ORDER", "the document's configuration order"),
                                            ("CONFIGURATION_SHOW_OVER_DEFINED", None),
                                            ("CONFIGURATION_SHOW_OVER_DEFINED", "a window asks")])
def test_an_update_of_a_gearbox_with_modes_is_refused_before_anything_is_read_while_a_tier_11_finding_is_unsettled(
        mode_findings, monkeypatch, finding, value):
    """swcom.dimension_values pairs GetSystemValue3(3, names)' answers with the names in the order passed, and a
    changed Update shows every mode: the gate reads findings.VALUE_READ_ORDER and CONFIGURATION_SHOW_OVER_DEFINED
    (tier 11)."""
    monkeypatch.setattr(findings, finding, value, raising=False)
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        swbuild.update_gearbox(fake, assembly=r"C:\T\R.SLDASM", motion=replace(_W7, configurations=("2H", "4H")),
                               exists=lambda _p: True)
    assert str(raised.value) == (f"Update SolidWorks on a gearbox with modes needs findings.{finding} settled on "
                                 f"SolidWorks (it is {value!r}), so nothing was read or changed.")
    assert fake.calls == []


def test_an_update_of_a_gearbox_without_modes_passes_the_modes_gate():
    swbuild._update_modes_gate(None)
    swbuild._update_modes_gate(_W7)


# -- W8: a gearbox with modes, built against the fake (W8-PLAN §1.8, §3.5) ------------------------------------------
#
# A cut-down TransferCase_Parallel (§2.2): two sleeves on the Rear axis splined together, three dogs on it, the
# couplings' on/off table and the slides' values per mode the answer key's (§2.3). Planned here by hand.

TC = "C:\\TC\\"
TC_ASM = TC + "TransferCase.SLDASM"
TC_LAYOUT = TC + "TransferCase_Layout.SLDPRT"
TC_SLEEVE, TC_DOG = TC + "Sleeve_m1.5_N30.SLDPRT", TC + "Dog_m1.5_N30.SLDPRT"
TC_MODES = ("2H", "4H", "N", "4L")
TC_SLIDES = {"RangeSlv along Rear": (46.0, 46.0, 56.0, 66.0), "ModeSlv along Rear": (96.0, 106.0, 96.0, 106.0)}
TC_COUPLES = {"RangeSlv engages InDog": ("gear7", "gear2", ("2H", "4H")),
              "ModeSlv engages FrontDog": ("gear8", "gear9", ("4H", "4L")),
              "RangeSlv engages LoDog": ("gear7", "gear6", ("4L",))}
TC_AT = {"gear2": 47.0, "gear6": 67.0, "gear9": 107.0, "gear7": 46.0, "gear8": 96.0}
TC_NAMES = {"gear2": "InDog", "gear6": "LoDog", "gear9": "FrontDog", "gear7": "RangeSlv", "gear8": "ModeSlv"}
TC_SENSES = {"ModeSlv splined to RangeSlv": True}


def _tc_plan():
    out = [ops.NewAssembly(""), ops.AddComponent("layout", TC_LAYOUT), ops.Place("layout", IDENTITY9, (0.0, 0.0, 0.0)),
           ops.Fix("layout")]
    for handle, z in TC_AT.items():
        path = TC_SLEEVE if handle in ("gear7", "gear8") else TC_DOG
        out += [ops.AddComponent(handle, path, (0.0, 0.0, z)), ops.Place(handle, IDENTITY9, (0.0, 0.0, z)),
                ops.Fix(handle)]
    for handle, z in TC_AT.items():
        name = TC_NAMES[handle]
        out += [ops.Unfix(handle),
                ops.Mate(f"axis_{handle}", "coincident", f"{handle}:Gear Axis", "layout:Rear Axis",
                          name=f"{name} on Rear Axis"),
                ops.Mate(f"along_{handle}", "point distance", f"{handle}:origin", "layout:plane1", z,
                          name=f"{name} along Rear")]
    out += [ops.Mate("spline", "gear", "gear7:Gear Axis", "gear8:Gear Axis", name="ModeSlv splined to RangeSlv"),
            ops.Rebuild(), ops.SaveAs(TC_ASM)]
    return BuildPlan("workbook-assembly", "", tuple(out), TC_ASM)


def _tc_modes(couples=TC_COUPLES):
    always = tuple(op.name for op in _tc_plan().ops if isinstance(op, ops.Mate))
    made, steps = set(), []
    for index, mode in enumerate(TC_MODES):
        made_ops = []
        for name, (sleeve, dog, on) in couples.items():
            if mode in on and name not in made:
                made.add(name)
                made_ops.append(ops.Mate(f"c{len(made)}", "gear", f"{sleeve}:Gear Axis", f"{dog}:Gear Axis", name=name))
        values = {name: v[index] for name, v in TC_SLIDES.items()}
        frames = {"gear7": (IDENTITY9, (0.0, 0.0, values["RangeSlv along Rear"])),
                  "gear8": (IDENTITY9, (0.0, 0.0, values["ModeSlv along Rear"]))}
        steps.append(swbuild.ModeStep(mode, tuple(made_ops), always + tuple(n for n, c in couples.items() if mode in c[2]),
                                      tuple(n for n, c in couples.items() if mode not in c[2]), values, frames))
    return swbuild.ModesPlan(tuple(steps), same_way=tuple(couples))


# The dogs and sleeves are not geometry here; the plan's slides use the dogs' along mates as distance mates too, so
# only the two sleeves' along mates are SLIDEs (their values per mode); the dogs' stand where they were made.
TC_GEARS = {h: TC_NAMES[h] for h in TC_AT} | {"layout": "layout"}


@pytest.fixture
def mode_findings(monkeypatch):
    """Every finding a build with modes reads, pinned here at what the W8 spike found on SolidWorks 2026 (never the
    committed values), with the read-back's and the remake's, a suppressed gear mate's sense read as probe
    planetary_put_back found it on 2026 (an Update with modes reads every sense; a test of the unread sentence sets
    it to None), the planetary put route that probe found there (an Update of a train with a carrier refuses
    without it), and, from tier 11 on 2026, the order GetSystemValue3(3, names) answers in, VALUE_READ_ORDER (the
    slide values are paired with the names in that order), and what showing an over-defined configuration does,
    CONFIGURATION_SHOW_OVER_DEFINED (a build or Update with modes shows every mode): a build or Update with modes
    refuses without either.

    The sentences about a turn read TURN_PER_CONFIGURATION_ON_<year> (W8-INTERFACES §9.18). It is pinned True for
    both years, as POSITIONS_PER_CONFIGURATION_ON_<year> was before the split, so these tests go on exercising the
    sentences they were written for; the committed 2026 value is False (W8 s2), and the False and unsettled
    sentences are tested where a test sets the switch itself."""
    for name, value in tuple(swcom.CONFIGURATION_FINDINGS) + (
            ("CONFIGURATION_SHOW_RAISES_DIALOG", False), ("MULTI_CONFIGURATION_SAVE_ASKS", False),
            ("COLLINEAR_GEAR_MATE_SENSE_READ_BACK", True), ("SLIDE_VALUE_PER_CONFIGURATION_ON_2026", True),
            ("SLIDE_VALUE_PER_CONFIGURATION_ON_2024", True), ("TURN_PER_CONFIGURATION_ON_2026", True),
            ("FEATURE_SUPPRESS", 0), ("FEATURE_UNSUPPRESS", 1), ("MATE_FIND_ROUTE", "mate group"),
            ("COMPONENT_FIND_ROUTE", "GetComponentByName"),
            ("GEAR_MATE_SENSE_READ_BACK", "(Reverse == entities parallel) == internal"),
            ("GEAR_MATE_READ_BACK_TELLS_SENSE", True), ("GEAR_MATE_CHECK_AND_REMAKE_HOLDS", True),
            ("MATE_DELETE_ROUTE", "Select2 then EditDelete()"), ("MATE_RENAME_ROUTE", "IFeature.Name put"),
            ("TURN_PER_CONFIGURATION_ON_2024", True),
            ("SUPPRESSED_GEAR_MATE_SENSE_READ", "answers, marks nothing"),
            ("PLANETARY_PUT_ROUTE", "gear mates off around the puts"), ("VALUE_READ_ORDER", "the order passed"),
            ("CONFIGURATION_SHOW_OVER_DEFINED", "shown; no window asks; its mates read in error; others solve after")):
        monkeypatch.setattr(findings, name, value, raising=False)


def _tc_build(fake=None, modes=None, **kwargs):
    fake = fake or FakeSolidWorks()
    checks = []
    steps = []
    result = swbuild.build(fake, _tc_plan(), never_exists, gears=TC_GEARS, senses=TC_SENSES,
                           modes=modes or _tc_modes(), mode_checks=checks, progress=steps.append, **kwargs)
    return fake, result, checks, steps


def _first(fake, name, *args):
    return next(i for i, (n, a) in enumerate(fake.calls) if n == name and (not args or a[:len(args)] == args))


@pytest.mark.parametrize("elsewhere", ["suppressed", "on"])
def test_a_build_with_modes_sets_up_every_configuration_in_the_planned_order(mode_findings, elsewhere):
    fake = FakeSolidWorks()
    fake.new_mate_elsewhere = elsewhere
    fake, result, checks, steps = _tc_build(fake)
    assert result.ok and result.saved == TC_ASM, result.log_lines()
    calls = names(fake)
    # the always-on mates and the slides made with only Default; then every configuration added
    plan_mates = [op for op in _tc_plan().ops if isinstance(op, ops.Mate)]
    assert calls[:calls.index("add_configuration")].count("add_mate") == len(plan_mates)
    assert "save_as" not in calls[:calls.index("add_configuration")]
    adds = [a[0] for n, a in fake.calls if n == "add_configuration"]
    assert adds == list(TC_MODES)
    # a rebuild between the last add and the first value or flag
    last_add = max(i for i, n in enumerate(calls) if n == "add_configuration")
    first_set = min(i for i, n in enumerate(calls) if n in ("set_dimension_in", "set_mate_suppressed_in"))
    assert "rebuild" in calls[last_add:first_set]
    # every slide's value set in every configuration, the first's included, then read back
    sets = [(a[0], a[1], a[2]) for n, a in fake.calls if n == "set_dimension_in"]
    assert sets == [(f"along_{h}", v, (m,)) for h, slide in (("gear7", "RangeSlv along Rear"),
                                                             ("gear8", "ModeSlv along Rear"))
                    for m, v in zip(TC_MODES, TC_SLIDES[slide])]
    # each coupling made with the first configuration using it shown
    for name, (sleeve, dog, on) in TC_COUPLES.items():
        made = _first(fake, "add_mate", "gear", f"{sleeve}:Gear Axis", f"{dog}:Gear Axis")
        shown = [a[0] for n, a in fake.calls[:made] if n == "show_configuration"]
        assert shown[-1] == on[0], name
    # every flag as the table has it, in every configuration; Default deleted; saved in the first mode
    assert fake.configs == list(TC_MODES) and fake.config == "2H"
    for name, (_, _, on) in TC_COUPLES.items():
        assert fake.mate(name).flags == {m: m not in on for m in TC_MODES}, name
    for name, values in TC_SLIDES.items():
        assert fake.mate(name).own == dict(zip(TC_MODES, values))
    assert calls.index("delete_configuration") < calls.index("save_as")
    assert [a[0] for n, a in fake.calls if n == "delete_configuration"] == ["Default"]
    assert [a[0] for n, a in fake.calls if n == "show_configuration"][-1] == "2H"
    # the per-mode check, each mode through fresh handles, every slider at its value
    assert [c.name for c in checks] == list(TC_MODES)
    for check, index in zip(checks, range(4)):
        assert check.values == {n: v[index] for n, v in TC_SLIDES.items()}
        assert check.suppressed == {n: TC_MODES[index] not in c[2] for n, c in sorted(TC_COUPLES.items())}
    assert [(s.stage, s.name, s.index, s.count) for s in steps] == \
        [(swbuild.STAGE_MODE, m, i, 4) for _ in range(2) for i, m in enumerate(TC_MODES, 1)]
    assert "configuration 2H made" in result.done and "configuration Default deleted" in result.done


def test_each_mode_stands_its_sliders_at_its_own_values(mode_findings):
    fake, result, _, _ = _tc_build()
    assert result.ok, result.log_lines()
    for index, mode in enumerate(TC_MODES):
        fake.show_configuration(mode)
        fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        assert fake.frames["gear7-1"][1][2] == pytest.approx(TC_SLIDES["RangeSlv along Rear"][index])
        assert fake.frames["gear8-1"][1][2] == pytest.approx(TC_SLIDES["ModeSlv along Rear"][index])


def test_on_2024_the_spline_is_read_wrong_and_made_again_and_the_couplings_read_right(mode_findings):
    fake = FakeSolidWorks()
    fake.flip_needed = dict(FLIP_NEEDED_2024)
    fake, result, _, _ = _tc_build(fake)
    assert result.ok and result.turned_round == ["ModeSlv splined to RangeSlv"], result.log_lines()


def test_a_mode_whose_coupling_over_defines_stops_the_build_naming_the_mode_and_nothing_is_saved(mode_findings):
    couples = dict(TC_COUPLES, **{"ModeSlv engages InDog": ("gear8", "gear2", ("N",)),
                                  "RangeSlv engages InDog": ("gear7", "gear2", ("2H", "4H", "N"))})
    fake, result, _, _ = _tc_build(modes=_tc_modes(couples))
    assert not result.ok and not result.saved
    assert result.mate_problems == ["In mode N, the mate ModeSlv engages InDog over-defines the assembly."]
    assert "save_as" not in names(fake)


def test_a_flag_set_straight_after_an_add_fails_its_read_back_on_the_second_call(mode_findings):
    """The fake's fault (§3.5): a build that set flags before the rebuild after the adds would fail here."""
    fake, result, _, _ = _tc_build()
    fake.add_configuration("X")
    fake.set_mate_suppressed_in("c1", True, ["X"])
    with pytest.raises(SolidWorksError, match="would not turn on the mate RangeSlv engages InDog in X"):
        fake.set_mate_suppressed_in("c1", False, ["X"])
    fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    fake.set_mate_suppressed_in("c1", False, ["X"])
    assert fake.mate_suppression("c1", ["X"]) == {"X": False}


def test_the_fake_hands_back_plain_names_as_the_session_does(mode_findings):
    """``Session.add_component`` and ``find_component`` return the Name2 as a plain ``str`` and keep every COM
    handle to themselves (the handle rule; a held one is caught by test_swcom's COM-level StaleHandle), so the
    fake returns plain names too: they travel in results, which callers copy and write."""
    fake = FakeSolidWorks()
    fake.new_assembly()
    assert type(fake.add_component("gear1", TC_DOG, (0.0, 0.0, 0.0))) is str
    fake.add_configuration("X")
    assert type(fake.find_component("gear2", "gear1-1")) is str and fake.is_fixed("gear1") is False


def test_a_result_of_a_build_with_modes_survives_a_copy_and_a_deep_copy(mode_findings):
    fake, result, _ = _tc_gearbox()
    assert result.ok, result.log_lines()
    for copied in (copy.copy(result), copy.deepcopy(result)):
        assert copied.components == result.components and copied.modes == result.modes
        assert all(type(name) is str for name in copied.components.values())
        assert copied.log_lines() == result.log_lines()


def test_a_build_with_modes_on_the_fake_is_finished_and_its_record_written_and_read_back(mode_findings,
                                                                                         monkeypatch):
    """End to end (package D's fault at f9a8cae): TransferCase_Parallel planned, built on the fake with its modes,
    finished, and the record written and read back with the modes as built."""
    from gear_generator import store
    from gear_generator.workbook import assess, gearbox
    from workbook_fixtures import transfer_case_parallel
    monkeypatch.setattr(findings, "INTERFERENCE_CHECKED", True, raising=False)
    book = "C:\\Books\\TransferCase.xlsx"
    assessed = assess.assess(replace(transfer_case_parallel(), source_path=book), [], "C:\\Out\\")
    fake = FakeSolidWorks()
    planned = gearbox.plan_gearbox(assessed, None, exists=fake.exists, read_sidecar=lambda _path: None)
    assert planned.refusal == "" and planned.modes_plan is not None
    result = swbuild.build_gearbox(fake, **planned.build_kwargs(), exists=fake.exists, mtime=lambda _path: 0.0)
    assert result.ok and [c.name for c in result.modes] == ["2H", "4H", "N", "4L"], result.log_lines()
    done = gearbox.finish_build(planned, result, None, workbook=book, digest="d1", written_by="test",
                                read_sidecar=lambda _path: None, exists=fake.exists, mtime=lambda _path: 0.0,
                                stamp="2026-11-14T00:00:00Z")
    record = store.link_record_from_json(store.link_record_to_json(done.record))
    assert record.gearbox.modes == ["2H", "4H", "N", "4L"]
    assert {c.name for c in record.gearbox.components} == set(result.components.values()) - {
        result.components.get("layout")}


@pytest.mark.parametrize("finding, value, sentence", [
    ("CONFIGURATION_ADD_ROUTE", None, "Working with an assembly's configurations has not been settled on SolidWorks "
                                      "(findings.CONFIGURATION_ADD_ROUTE is None), so a gearbox with modes is not "
                                      "built and nothing is made."),
    ("MULTI_CONFIGURATION_SAVE_ASKS", True, "A gearbox with modes needs findings.MULTI_CONFIGURATION_SAVE_ASKS "
                                            "settled on SolidWorks (it is True), so it is not built and nothing is "
                                            "made."),
    ("COLLINEAR_GEAR_MATE_SENSE_READ_BACK", None, "A gearbox with modes needs findings."
                                                  "COLLINEAR_GEAR_MATE_SENSE_READ_BACK settled on SolidWorks (it is "
                                                  "None), so it is not built and nothing is made."),
    ("COMPONENT_FIND_ROUTE", None, "Finding a component again after a configuration change has not been settled on "
                                   "SolidWorks (findings.COMPONENT_FIND_ROUTE is None), so a gearbox with modes is "
                                   "not built and nothing is made."),
    ("VALUE_READ_ORDER", "the document's configuration order", "A gearbox with modes needs findings.VALUE_READ_ORDER "
                                                               "settled on SolidWorks (it is \"the document's "
                                                               "configuration order\"), so it is not built and "
                                                               "nothing is made."),
    ("VALUE_READ_ORDER", None, "A gearbox with modes needs findings.VALUE_READ_ORDER settled on SolidWorks (it is "
                               "None), so it is not built and nothing is made."),
    ("CONFIGURATION_SHOW_OVER_DEFINED", None, "A gearbox with modes needs findings.CONFIGURATION_SHOW_OVER_DEFINED "
                                              "settled on SolidWorks (it is None), so it is not built and nothing is "
                                              "made."),
    ("CONFIGURATION_SHOW_OVER_DEFINED", "a window asks", "A gearbox with modes needs findings."
                                                         "CONFIGURATION_SHOW_OVER_DEFINED settled on SolidWorks (it is "
                                                         "'a window asks'), so it is not built and nothing is made."),
    ("SLIDE_VALUE_PER_CONFIGURATION_ON_2026", None, "SolidWorks 2026 has not been shown to hold a slide's value per "
                                                    "configuration, so a gearbox with modes is not built there and "
                                                    "nothing is made."),
])
def test_a_build_with_modes_is_refused_before_anything_is_made_while_a_finding_is_unsettled(
        mode_findings, monkeypatch, finding, value, sentence):
    monkeypatch.setattr(findings, finding, value, raising=False)
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError) as raised:
        _tc_build(fake)
    assert str(raised.value) == sentence
    assert not [n for n, _ in fake.calls if n.startswith("new_")]


def test_the_version_refusal_is_read_from_the_running_solidworks(mode_findings, monkeypatch):
    monkeypatch.setattr(findings, "SLIDE_VALUE_PER_CONFIGURATION_ON_2024", None, raising=False)
    fake = FakeSolidWorks()
    fake.revision = (32, 5, 0)
    with pytest.raises(swbuild.BuildError) as raised:
        _tc_build(fake)
    assert str(raised.value) == ("SolidWorks 2024 has not been shown to hold a slide's value per configuration, so a "
                                 "gearbox with modes is not built there and nothing is made.")
    assert fake.calls == []
    assert swbuild._modes_version_refusal(()) == (
        "The running SolidWorks' version could not be read, so whether it holds a slide's value per configuration "
        "cannot be told; a gearbox with modes is not built and nothing is made.")


def test_modes_never_reach_solidworks_by_a_path_that_ignores_them(mode_findings):
    """The two paths left once the gate is lifted: modes with no assembly, or with no senses to read back by,
    or for an assembly that does not turn, are refused before anything is made."""
    fake = FakeSolidWorks()
    with pytest.raises(swbuild.BuildError, match="^Modes were given with no assembly"):
        swbuild.build_gearbox(fake, [plan(path=TC + "Gear.SLDPRT")], modes=_tc_modes(), exists=never_exists)
    with pytest.raises(swbuild.BuildError, match="^A gearbox with modes was not told which way its gear mates turn"):
        swbuild.build(fake, _tc_plan(), never_exists, modes=_tc_modes())
    static = BuildPlan("workbook-assembly", "", tuple(op for op in _tc_plan().ops if not isinstance(op, ops.Mate)),
                       TC_ASM)
    with pytest.raises(swbuild.BuildError, match="^Modes were given for an assembly that does not turn"):
        swbuild.build(fake, static, never_exists, senses={}, modes=_tc_modes())
    with pytest.raises(swbuild.BuildError, match="^Modes were given for an assembly that is not built to turn"):
        swbuild.build(fake, _tc_plan(), never_exists, kind=swcom.ASSEMBLY_STATIC, senses=TC_SENSES,
                      modes=_tc_modes())
    assert not [n for n, _ in fake.calls if n.startswith("new_")]


def test_a_modes_plan_names_a_coupling_that_turns_its_gears_alike_and_joins_plan_components():
    modes = _tc_modes()
    assert modes.check(_tc_plan()) == []
    unlisted = replace(modes, same_way=("RangeSlv engages InDog", "RangeSlv engages LoDog"))
    assert unlisted.check(_tc_plan()) == ["In mode 4H, the coupling ModeSlv engages FrontDog turns its two gears the "
                                          "same way, and it is not listed as doing so."]
    steps = list(modes.steps)
    steps[3] = replace(steps[3], ops=(ops.Mate("c3", "gear", "gear7:Gear Axis", "gear99:Gear Axis",
                                                name="RangeSlv engages LoDog"),))
    assert replace(modes, steps=tuple(steps)).check(_tc_plan()) == [
        "In mode 4L, the gear mate RangeSlv engages LoDog joins gear99, which is not a component of the assembly."]


def _tc_gearbox(fake=None, **kwargs):
    fake = fake or FakeSolidWorks()
    steps = []
    parts = [plan(path=p) for p in (TC_SLEEVE, TC_DOG)]
    layout = BuildPlan("layout", "", (ops.NewPart(""), ops.Rebuild(), ops.SaveAs(TC_LAYOUT)), TC_LAYOUT)
    result = swbuild.build_gearbox(fake, parts, layout=layout, assembly=_tc_plan(), gears=TC_GEARS, senses=TC_SENSES,
                                   modes=_tc_modes(), exists=fake.exists, progress=steps.append, **kwargs)
    return fake, result, steps


def test_a_gearbox_with_modes_checks_interference_in_every_mode_and_ends_in_the_first(mode_findings, monkeypatch):
    monkeypatch.setattr(findings, "INTERFERENCE_CHECKED", True, raising=False)
    fake = FakeSolidWorks()
    clash = (("gear7-1", "gear6-1"), 12.0)
    fake.clashes_in = {"4L": [clash]}
    fake, result, steps = _tc_gearbox(fake)
    assert result.ok, result.log_lines()
    assert [c.name for c in result.modes] == list(TC_MODES)
    assert [len(c.clashes) for c in result.modes] == [0, 0, 0, 1] and result.clashes == []
    assert result.positions_per_configuration is True
    assert fake.config == "2H"
    after_save = [a[0] for n, a in fake.calls[names(fake).index("save_as", names(fake).index("add_configuration")):]
                  if n == "show_configuration"]
    assert after_save == list(TC_MODES) + ["2H"]
    lines = result.log_lines()
    assert "mode    2H: every mate sound, every gear free to turn, no interference" in lines
    assert "mode    4L: every mate sound, every gear free to turn" in lines
    assert any(line.startswith("CHECK   in mode 4L, RangeSlv and LoDog interfere") for line in lines), lines
    assert any(line.startswith("config  4L: ") for line in lines)
    assert [s.name for s in steps if s.stage == swbuild.STAGE_MODE][-4:] == list(TC_MODES)


# -- W8: Update SolidWorks across configurations, against the fake (W8-PLAN §1.10, §3.5) ----------------------------

def _tc_place(result, mode, turn=0.0):
    index = TC_MODES.index(mode)
    out = []
    for handle, z in TC_AT.items():
        if handle == "gear7":
            z = TC_SLIDES["RangeSlv along Rear"][index]
        elif handle == "gear8":
            z = TC_SLIDES["ModeSlv along Rear"][index]
        out.append(swbuild.Placement(TC_NAMES[handle], result.components[handle], _rot_z(turn), (0.0, 0.0, z), 12.0))
    return tuple(out)


def _tc_motion(result, active="2H", wanted_turn=0.0, **changes):
    """The TransferCase's record as Update is given it: every mate with its kind, gears and modes, the couplings as
    MeshLinks (k = +1, both on +Z) and the spline as a LockLink, the frames per mode."""
    mates = []
    for op in _tc_plan().ops:
        if not isinstance(op, ops.Mate):
            continue
        handle = op.a.partition(":")[0]
        gear = TC_NAMES[handle]
        if op.kind == "gear":
            mates.append(swbuild.MateRef(op.name, "spline", ("RangeSlv", "ModeSlv")))
        elif op.kind == "coincident":
            mates.append(swbuild.MateRef(op.name, "axis", (gear,), "Rear"))
        elif handle in ("gear7", "gear8"):
            values = tuple(zip(TC_MODES, TC_SLIDES[op.name]))
            mates.append(swbuild.MateRef(op.name, "slide", (gear,), "Rear", values=values))
        else:
            mates.append(swbuild.MateRef(op.name, "along", (gear,), "Rear"))
    for name, (sleeve, dog, on) in TC_COUPLES.items():
        mates.append(swbuild.MateRef(name, "couple", (TC_NAMES[sleeve], TC_NAMES[dog]), modes=on))
    meshes = tuple(swbuild.MeshLink(TC_NAMES[s], TC_NAMES[d], 1.0, 12.0, modes=on) for s, d, on in TC_COUPLES.values())
    motion = swbuild.MotionUpdate(
        mates=tuple(mates), meshes=meshes, locks=(swbuild.LockLink("RangeSlv", "ModeSlv", 12.0),),
        recorded=_tc_place(result, active), recorded_meshes=meshes, configurations=TC_MODES,
        mode_placements=tuple((m, _tc_place(result, m, wanted_turn)) for m in TC_MODES),
        recorded_by_mode=tuple((m, _tc_place(result, m)) for m in TC_MODES))
    return replace(motion, **changes), _tc_place(result, active, wanted_turn)


@pytest.fixture(params=[False, True], ids=["positions per configuration", "shared positions"])
def tc_built(request, mode_findings, monkeypatch):
    monkeypatch.setattr(findings, "INTERFERENCE_CHECKED", True, raising=False)
    fake = FakeSolidWorks()
    fake.shared_positions = request.param
    fake, result, _ = _tc_gearbox(fake)
    assert result.ok, result.log_lines()
    fake.calls.clear()
    return fake, result


def _tc_update(fake, result, active="2H", **changes):
    motion, placements = _tc_motion(result, active, **changes)
    return swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                                  mtime=lambda _p: 0.0)


def _shown(fake):
    return [a[0] for n, a in fake.calls if n == "show_configuration"]


def test_a_quiet_update_shows_nothing_reads_every_flag_and_value_and_says_where_it_worked(tc_built):
    fake, built = tc_built
    done = _tc_update(fake, built)
    assert done.ok, done.log_lines()
    assert _shown(fake) == [] and done.changed == [] and done.put_in == [] and done.modes == []
    assert done.configuration == "2H" and done.visited == [] and done.extra_configurations == []
    read = {a[0] for n, a in fake.calls if n == "mate_suppression"}
    assert len(read) == len(_tc_motion(built)[0].mates)
    assert all(a[1] == TC_MODES for n, a in fake.calls if n == "mate_suppression")
    assert sorted(a[0] for n, a in fake.calls if n == "dimension_values") == sorted(
        f"mate{i}" for i, m in enumerate(_tc_motion(built)[0].mates, 1) if m.kind == "slide")
    assert not [n for n, _ in fake.calls if n in ("set_mate_suppressed_in", "set_dimension_in", "place_component",
                                                 "set_mate_suppressed")]
    assert done.positions_per_configuration is True
    assert "ok      worked in 2H, the configuration that was active; did not show the other modes" in done.log_lines()


def test_the_configuration_is_always_set_for_a_gearbox_with_modes_and_in_the_spelling_solidworks_has(tc_built):
    fake, built = tc_built
    fake.show_configuration("4L")
    done = _tc_update(fake, built, active="4L")
    assert done.ok and done.configuration == "4L", done.log_lines()


def test_d10_per_configuration_both_ways_in_a_mode_not_active_never_calls_a_mate_already_right(tc_built):
    fake, built = tc_built
    fake.mate("RangeSlv engages LoDog").flags["4L"] = True           # suppressed where the record has it on
    fake.mate("RangeSlv engages InDog").flags["4L"] = False          # on where the record has it off
    done = _tc_update(fake, built)
    assert done.ok, done.log_lines()
    assert done.unsuppressed_in == [("RangeSlv engages LoDog", "4L")]
    assert done.suppressed_in == [("RangeSlv engages InDog", "4L")]
    sets = [a[:3] for n, a in fake.calls if n == "set_mate_suppressed_in"]
    assert sorted(sets) == sorted([(_handle_of(built, "RangeSlv engages LoDog"), False, ("4L",)),
                                   (_handle_of(built, "RangeSlv engages InDog"), True, ("4L",))])
    assert fake.mate("RangeSlv engages LoDog").flags["4L"] is False
    assert fake.mate("RangeSlv engages InDog").flags["4L"] is True
    assert fake.config == "2H" and _shown(fake)[-1] == "2H" and TC_ASM in done.changed
    assert [c.name for c in done.modes] == ["4H", "N", "4L", "2H"] and done.visited == ["4H", "N", "4L"]
    assert "ok      worked in 2H, the configuration that was active, and showed 4H, N, 4L too" in done.log_lines()


def _handle_of(built, name):
    return next(f"mate{i}" for i, m in enumerate(_tc_motion(built)[0].mates, 1) if m.name == name)


def test_a_slide_value_changed_in_a_mode_not_active_is_set_back_without_showing_it_first(tc_built):
    fake, built = tc_built
    fake.mate("RangeSlv along Rear").own["4L"] = 60.0
    done = _tc_update(fake, built)
    assert done.ok, done.log_lines()
    assert done.values_restored == [("RangeSlv along Rear", "4L")] and done.slid == []
    first_set = names(fake).index("set_dimension_in")
    assert "show_configuration" not in names(fake)[:first_set]
    assert fake.mate("RangeSlv along Rear").own["4L"] == 66.0


def test_a_j14_edit_sets_the_new_value_and_exactly_the_changed_flags(tc_built):
    fake, built = tc_built
    edit = dict(slide_values=tuple((n, m, v + (10.0 if (n, m) == ("ModeSlv along Rear", "4H") else 0.0))
                                   for n, values in TC_SLIDES.items() for m, v in zip(TC_MODES, values)),
                on_sets=(("ModeSlv engages FrontDog", ("4L",)),))
    motion, placements = _tc_motion(built, **edit)
    done = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                                  mtime=lambda _p: 0.0)
    assert done.slid == [("ModeSlv along Rear", "4H", 116.0)]
    assert done.suppressed_in == [("ModeSlv engages FrontDog", "4H")] and done.unsuppressed_in == []
    assert fake.mate("ModeSlv engages FrontDog").flags["4H"] is True


def test_a_workbook_change_shows_and_puts_every_mode_the_active_one_last_and_ends_where_it_began(tc_built):
    fake, built = tc_built
    motion, placements = _tc_motion(built, wanted_turn=6.0)        # every gear wanted a 6° turn: half a tooth
    done = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                                  mtime=lambda _p: 0.0)
    assert done.ok, done.log_lines()
    assert done.put_in == ["4H", "N", "4L", "2H"] and _shown(fake) == ["4H", "N", "4L", "2H"]
    assert fake.config == "2H"
    for index, check in enumerate(done.modes):  # found on showing, before its put: in step, half a tooth off
        assert check.off_axis == [] and check.out_of_step == []
        # with shared positions the first mode's put already stands every later mode at the wanted turn
        assert check.turned is (index == 0 or not fake.shared_positions)


COMMITTED_TURN_2026 = findings.TURN_PER_CONFIGURATION_ON_2026      # read at import, before any fixture pins it


def _status_sentences(built, done):
    """An Update's sentences after the pieces, as the status gives them: the motion path's, then the modes'."""
    from types import SimpleNamespace
    from gear_generator import ui_text
    update = SimpleNamespace(motion=_tc_motion(built)[0], assembly=TC_ASM)
    return ui_text.motion_update_lines(update, done) + ui_text.mode_update_lines(update, done)


def test_a_turn_in_step_in_the_mode_showing_is_left_and_the_status_warns_of_the_other_modes(mode_findings,
                                                                                          monkeypatch):
    """W8-INTERFACES §9.18 (the review of its commits, point 1), end to end on the fake's shared variant with the
    turn finding as committed (2026: a turn can show in other modes). The 2H train turned 37°, in step in 2H; Update in
    2H puts nothing and shows nothing, so the footer shows its status alone; the status says another mode may stand
    with a dog across its sleeve, and on this fake 4L does."""
    monkeypatch.setattr(findings, "INTERFERENCE_CHECKED", True, raising=False)
    fake = FakeSolidWorks()
    fake.shared_positions = True
    fake, built, _ = _tc_gearbox(fake)
    monkeypatch.setattr(findings, "TURN_PER_CONFIGURATION_ON_2026", COMMITTED_TURN_2026)
    for gear in ("gear7-1", "gear8-1", "gear2-1"):                 # RangeSlv, ModeSlv and InDog: in step in 2H
        fake.turn(gear, 37.0)
    fake.calls.clear()
    done = _tc_update(fake, built)
    assert done.ok and done.turned and done.put_in == [] and _shown(fake) == [] and done.visited == []
    assert done.positions_per_configuration is False
    assert _status_sentences(built, done) == [
        "The gears stand where they were turned in SolidWorks.",
        "This version of SolidWorks can show that turn in other modes, so a dog may stand across its sleeve in "
        "another; to put the gears back there, press Update SolidWorks with that mode showing.",
        "It worked in 2H, the configuration that was active; it did not show the other modes, since nothing in 2H "
        "needed changing."]
    fake.show_configuration("4L")                  # the hazard the sentence names: in 4L, where RangeSlv engages
    placements = _tc_motion(built, active="4L")[1]  # LoDog, the sleeve stands turned 37° and the dog does not
    turned = {p.gear: math.degrees(swbuild.turn_between(p.rotation, fake.component_frame(f"placed{i}")[0]))
              for i, p in enumerate(placements, 1) if p.gear in ("RangeSlv", "LoDog")}
    assert turned == pytest.approx({"RangeSlv": 37.0, "LoDog": 0.0}, abs=1e-6)


def test_a_build_with_modes_on_2026_says_a_turn_shows_in_every_mode_from_the_finding_as_committed(mode_findings,
                                                                                                 monkeypatch):
    """The review of ruling 9.18's commits, point 3: with TURN_PER_CONFIGURATION_ON_2026 as committed (False, W8 s2),
    a build on the fake's 2026 revision carries False, and its status says the shared sentence and neither claim of
    the old one. Hard-wiring True into the build's result fails here."""
    from gear_generator import ui_text
    from gear_generator.workbook import gearbox
    from test_workbook_modes import assessed
    from workbook_fixtures import transfer_case_parallel
    monkeypatch.setattr(findings, "TURN_PER_CONFIGURATION_ON_2026", COMMITTED_TURN_2026)
    fake = FakeSolidWorks()
    assert fake.revision[0] == 34
    plan = gearbox.plan_gearbox(assessed(transfer_case_parallel()), None, exists=fake.exists,
                                read_sidecar=lambda p: None)
    result = swbuild.build_gearbox(fake, **plan.build_kwargs(), exists=fake.exists)
    assert result.ok and result.positions_per_configuration is False, result.log_lines()
    text = ui_text.gearbox_status(plan, result)[0]
    assert ("RangeSlv and ModeSlv slide along Rear, each to its place in each mode. A turn you give the gears in one "
            "mode can show in other modes, so a dog can stand across its sleeve in another; to put the gears back "
            "there, press Update SolidWorks with that mode showing.") in text
    assert ui_text.TURN_STAYS not in text and ui_text.SWITCH_IN_STEP not in text


def test_a_quiet_update_that_puts_on_2026_says_so_from_the_finding_as_committed(mode_findings, monkeypatch):
    """The same for an Update: the fake's shared variant, a turn in 4L seen in 2H, so every mode shown and put
    (§9.18). Hard-wiring True into the Update's result fails here."""
    monkeypatch.setattr(findings, "INTERFERENCE_CHECKED", True, raising=False)
    fake = FakeSolidWorks()
    fake.shared_positions = True
    fake, built, _ = _tc_gearbox(fake)
    monkeypatch.setattr(findings, "TURN_PER_CONFIGURATION_ON_2026", COMMITTED_TURN_2026)
    fake.show_configuration("4L")
    for gear in ("gear7-1", "gear8-1", "gear6-1", "gear9-1"):
        fake.turn(gear, 30.0)
    fake.show_configuration("2H")
    done = _tc_update(fake, built)
    assert done.ok and done.positions_per_configuration is False, done.log_lines()
    assert done.put_in == ["4H", "N", "4L", "2H"]
    assert _status_sentences(built, done) == [          # the crossed coupling said once, in the per-mode form
        "In 2H, RangeSlv's teeth stood across InDog's; the gears of 2H are back at the turn they were built at.",
        "This version of SolidWorks can show a turn given in one mode in the others, so the turn may have been given "
        "in another.",
        "It worked in 2H, the configuration that was active, then showed and checked 4H, N and 4L and left the "
        "assembly in 2H."]


def _mode_sentences(built, done):
    from types import SimpleNamespace
    from gear_generator import ui_text
    return ui_text.mode_update_lines(SimpleNamespace(motion=_tc_motion(built)[0], assembly=TC_ASM), done)


def test_a_turn_in_another_mode_is_unseen_by_a_quiet_update_or_if_shared_put_back_with_every_mode_visited(tc_built):
    fake, built = tc_built
    fake.show_configuration("4L")
    for gear in ("gear7-1", "gear8-1", "gear6-1", "gear9-1"):
        fake.turn(gear, 30.0)
    fake.show_configuration("2H")
    fake.calls.clear()
    done = _tc_update(fake, built)
    assert done.ok, done.log_lines()
    if not fake.shared_positions:
        # 2H stands as built: the turn stayed in 4L, unseen, nothing put, nothing shown (J25)
        assert _shown(fake) == [] and done.modes == [] and done.visited == []
        assert done.put_in == [] and done.turned is False and done.out_of_step == []
        assert not [n for n, _ in fake.calls if n in ("place_component", "rebuild", "set_mate_suppressed_in")]
    else:
        # Shared positions: the turn is seen in 2H, where InDog (not turned) is coupled to RangeSlv: out of step.
        # Something to put, so (W5's answer 2, J13, §1.10, ruling 9.18 after W8 s2's rerun) it is a changed Update:
        # every mode shown and every train put whole to its built frames, 2H last and left active. 4H is found
        # crossed too on showing (the shared turn), N and 4L not.
        assert done.out_of_step == [("RangeSlv", "InDog")] and done.put_in == ["4H", "N", "4L", "2H"]
        assert _shown(fake) == ["4H", "N", "4L", "2H"] and done.visited == ["4H", "N", "4L"]
        assert [(c.name, c.out_of_step, c.off_axis) for c in done.modes] == [
            ("4H", [("RangeSlv", "InDog")], []), ("N", [], []), ("4L", [], []), ("2H", [("RangeSlv", "InDog")], [])]
        puts = [(n, a[0]) for n, a in fake.calls if n in ("show_configuration", "place_component")]
        assert puts == [x for m in ("4H", "N", "4L", "2H")
                        for x in [("show_configuration", m)] + [("place_component", f"placed{i}") for i in range(1, 6)]]
        assert fake.config == "2H" and done.failures == []
        assert _mode_sentences(built, done) == [
            "In 2H, RangeSlv's teeth stood across InDog's; the gears of 2H are back at the turn they were built at.",
            "It worked in 2H, the configuration that was active, then showed and checked 4H, N and 4L and left the "
            "assembly in 2H."]


def test_a_put_in_the_active_mode_on_a_quiet_update_visits_every_other_mode_and_reads_every_flag_after(tc_built):
    """J13, §1.10, W5's answer 2: an Update with nothing changed in the workbook that finds the active mode out of
    step has something to put, so it is a changed Update: every mode shown and every train put whole, the active one
    last, and then every per-mode flag read in every configuration. On either reading of positions: here the two
    sleeves are turned in 2H without the gears they engage."""
    fake, built = tc_built
    for gear in ("gear7-1", "gear8-1"):                            # RangeSlv and ModeSlv, splined: out of step with
        fake.turn(gear, 30.0)                                      # InDog in 2H
    fake.calls.clear()
    done = _tc_update(fake, built)
    assert done.ok, done.log_lines()
    assert done.put_in == ["4H", "N", "4L", "2H"] and done.out_of_step == [("RangeSlv", "InDog")]
    assert _shown(fake) == ["4H", "N", "4L", "2H"] and done.visited == ["4H", "N", "4L"] and fake.config == "2H"
    assert sum(1 for n, _ in fake.calls if n == "place_component") == 4 * 5     # every train, every mode
    assert [c.name for c in done.modes] == ["4H", "N", "4L", "2H"]
    assert done.modes[-1].out_of_step == [("RangeSlv", "InDog")]  # found in 2H before its put
    last_put = max(i for i, (n, _) in enumerate(fake.calls) if n == "place_component")
    after = [fake.mate_handles[a[0]] for i, (n, a) in enumerate(fake.calls)
             if n == "mate_suppression" and i > last_put and a[1] == TC_MODES]
    assert sorted(after) == sorted(TC_COUPLES)
    for name, (_, _, on) in TC_COUPLES.items():
        assert fake.mate(name).flags == {m: m not in on for m in TC_MODES}, name


def test_an_update_in_a_configuration_that_is_no_mode_is_refused_before_anything_changes(tc_built):
    fake, built = tc_built
    fake.add_configuration("Exploded")
    fake.calls.clear()
    with pytest.raises(swbuild.BuildError) as raised:
        _tc_update(fake, built)
    assert str(raised.value) == ("Update SolidWorks works in one of the gearbox's own configurations (2H, 4H, N and "
                                 "4L), and Exploded is active in SolidWorks: pick one of them and press Update "
                                 "SolidWorks again.")
    assert not [n for n, _ in fake.calls if n.startswith("set_") or n in ("place_component", "show_configuration")]


def test_a_configuration_gone_is_not_as_built(tc_built):
    fake, built = tc_built
    fake.configs.remove("N")
    with pytest.raises(swbuild.NotAsBuilt) as raised:
        _tc_update(fake, built)
    assert str(raised.value) == ("The configuration N is not in TransferCase.SLDASM any more: it was renamed or "
                                 "deleted in SolidWorks.")


def test_an_extra_configuration_is_listed_and_left(tc_built):
    fake, built = tc_built
    fake.add_configuration("Exploded")
    fake.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    fake.show_configuration("2H")
    done = _tc_update(fake, built)
    assert done.ok and done.extra_configurations == ["Exploded"] and "Exploded" in fake.configs


def test_an_update_that_fails_in_another_mode_shows_the_one_that_was_active_again(tc_built):
    fake, built = tc_built
    fake.raises["place_component"] = (fake.counts["place_component"] + 7,
                                      SolidWorksError("SolidWorks would not move the gear."))
    motion, placements = _tc_motion(built, wanted_turn=6.0)
    done = swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                                  mtime=lambda _p: 0.0)
    assert not done.ok and fake.config == "2H" and _shown(fake)[-1] == "2H"
    assert TC_ASM in done.changed


@pytest.mark.parametrize("sentence, said", [
    ("RangeSlv stands at (0, 0, 66) where the mode places it at (0, 0, 46).",
     "In mode 2H, RangeSlv stands at (0, 0, 66) where the mode places it at (0, 0, 46)."),
    ("N reads not fixed in SolidWorks, where it was fixed.", "In mode 2H, N reads not fixed in SolidWorks, where it was fixed."),
    ("SolidWorks would not make the mate X.", "In mode 2H, SolidWorks would not make the mate X."),
    ("The mate X is missing from the assembly.", "In mode 2H, the mate X is missing from the assembly."),
    ("A gear is off.", "In mode 2H, a gear is off."),
])
def test_a_sentence_after_its_mode_keeps_every_name_as_written(sentence, said):
    assert swbuild._in_mode("2H", sentence) == said


def test_a_slider_off_its_place_in_a_mode_is_named_as_the_workbook_spells_it(mode_findings):
    fake = FakeSolidWorks()
    fake, result, _, _ = _tc_build(fake, modes=_tc_modes())
    assert result.ok
    steps = list(_tc_modes().steps)
    steps[0] = replace(steps[0], frames={"gear7": (IDENTITY9, (0.0, 0.0, 66.0))})
    fake = FakeSolidWorks()
    fake, result, _, _ = _tc_build(fake, modes=replace(_tc_modes(), steps=tuple(steps)))
    assert result.mate_problems == ["In mode 2H, RangeSlv stands at (0, 0, 46) where the mode places it at (0, 0, 66)."]


# -- W8-INTERFACES §9.16: every gear mate's sense read in some mode, or said unread

def test_a_quiet_update_lists_the_senses_it_could_not_read_without_a_show(tc_built, monkeypatch):
    monkeypatch.setattr(findings, "SUPPRESSED_GEAR_MATE_SENSE_READ", None, raising=False)
    fake, built = tc_built
    done = _tc_update(fake, built)
    assert done.ok, done.log_lines()
    assert done.senses_unread == ["ModeSlv engages FrontDog", "RangeSlv engages LoDog"]   # off in 2H, the record's order
    assert ("CHECK   which way these gear mates turn was not read, since no mode shown had them on: "
            "ModeSlv engages FrontDog, RangeSlv engages LoDog") in done.log_lines()


def test_with_suppressed_senses_readable_a_quiet_update_reads_every_sense(tc_built, monkeypatch):
    monkeypatch.setattr(findings, "SUPPRESSED_GEAR_MATE_SENSE_READ", "answers, marks nothing", raising=False)
    fake, built = tc_built
    done = _tc_update(fake, built)
    assert done.ok and done.senses_unread == [] and _shown(fake) == []
    read = [a[0] for n, a in fake.calls if n == "gear_mate_sense"]
    assert {_handle_of(built, n) for n in ("ModeSlv engages FrontDog", "RangeSlv engages LoDog")} <= set(read)


def test_an_update_that_shows_every_mode_reads_every_sense_there(tc_built):
    fake, built = tc_built
    fake.mate("ModeSlv engages FrontDog").flags["4H"] = True        # off where the record has it on: D10 in 4H
    done = _tc_update(fake, built)
    assert done.ok and done.senses_unread == [], done.log_lines()


def test_a_sense_read_wrong_in_a_mode_shown_is_a_failure_naming_the_mate_and_the_mode(tc_built, monkeypatch):
    monkeypatch.setattr(findings, "SUPPRESSED_GEAR_MATE_SENSE_READ", None, raising=False)
    fake, built = tc_built
    fake.never_right = {"RangeSlv engages LoDog"}
    fake.mate("ModeSlv engages FrontDog").flags["4H"] = True
    done = _tc_update(fake, built)
    assert (TC_ASM.rsplit("\\", 1)[-1], "In mode 4L, the gear mate RangeSlv engages LoDog turns its gears against the "
                                       "way they mesh.") in done.failures
    assert "remake_gear_mate" not in names(fake) and fake.config == "2H"


def test_with_suppressed_senses_readable_a_sense_read_wrong_off_here_refuses_before_anything_changes(tc_built,
                                                                                                    monkeypatch):
    monkeypatch.setattr(findings, "SUPPRESSED_GEAR_MATE_SENSE_READ", "answers, marks nothing", raising=False)
    fake, built = tc_built
    fake.never_right = {"RangeSlv engages LoDog"}
    with pytest.raises(swbuild.BuildError) as raised:
        _tc_update(fake, built)
    assert str(raised.value) == ("The gear mate RangeSlv engages LoDog in TransferCase.SLDASM turns its gears against "
                                 "each other, and making a gear mate of a gearbox with modes again is not in this "
                                 "version of Gear Generator, so nothing is changed; build the gearbox again.")
    assert not [n for n, _ in fake.calls if n.startswith("set_") or n == "show_configuration"]


def test_a_coupling_on_record_with_no_mesh_is_a_fault_refused_before_anything_changes(tc_built):
    fake, built = tc_built
    motion, placements = _tc_motion(built)
    motion = replace(motion, meshes=motion.meshes[1:], recorded_meshes=motion.recorded_meshes[1:])
    with pytest.raises(swbuild.BuildError) as raised:
        swbuild.update_gearbox(fake, assembly=TC_ASM, placements=placements, motion=motion, exists=fake.exists,
                               mtime=lambda _p: 0.0)
    assert str(raised.value) == ("Update SolidWorks was given the gear mate RangeSlv engages InDog on record with no "
                                 "mesh between RangeSlv and InDog to say which way it turns them, so nothing is "
                                 "changed; that is a fault in Gear Generator, not in SolidWorks.")
    assert not [n for n, _ in fake.calls if n.startswith("set_") or n == "show_configuration"]


def test_a_show_that_switches_and_then_raises_still_ends_in_the_configuration_that_was_active(tc_built):
    fake, built = tc_built
    fake.mate("ModeSlv engages FrontDog").flags["4H"] = True
    show = fake.show_configuration

    def switch_then_raise(name):
        show(name)
        if name == "N":
            raise SolidWorksError("SolidWorks would not show the configuration N.")
    fake.show_configuration = switch_then_raise
    done = _tc_update(fake, built)
    assert not done.ok and fake.config == "2H"
    assert _shown(fake)[-1] == "2H"


def test_an_update_with_modes_needs_the_collinear_read_back_settled(mode_findings, monkeypatch):
    monkeypatch.setattr(findings, "COLLINEAR_GEAR_MATE_SENSE_READ_BACK", None, raising=False)
    with pytest.raises(swbuild.BuildError) as raised:
        swbuild._update_modes_gate(replace(_W7, configurations=("2H",)), (34, 0, 0))
    assert str(raised.value) == ("Update SolidWorks on a gearbox with modes needs findings."
                                 "COLLINEAR_GEAR_MATE_SENSE_READ_BACK settled on SolidWorks (it is None), so nothing "
                                 "was read or changed.")


# -- W7: a turned planetary put back with its gear mates off (probe planetary_put_back, PLANETARY_PUT_ROUTE) ----------

def _planetary_turned_and_pressed(monkeypatch, route):
    """E's failing case: Planetary_4to1 planned, built on the fake and recorded; the sun driven +37°; Update pressed
    with the Planet's At changed."""
    from gear_generator import store
    from gear_generator.workbook import gearbox, update
    from test_workbook_planetary import BOOK, direct, edited, planetary_4to1
    monkeypatch.setattr(findings, "PLANETARY_PUT_ROUTE", route, raising=False)
    sw = FakeSolidWorks()
    plan = gearbox.plan_gearbox(direct(planetary_4to1()), None, exists=sw.exists, read_sidecar=lambda _p: None)
    built = swbuild.build_gearbox(sw, **plan.build_kwargs(), exists=sw.exists)
    assert built.ok, built.log_lines()
    done = gearbox.finish_build(plan, built, None, workbook=BOOK, digest="d1", written_by="test",
                                read_sidecar=lambda _p: None, exists=sw.exists)
    record = store.link_record_from_json(store.link_record_to_json(done.record))
    names = {c.gear: c.name for c in record.gearbox.components}
    sw.drive(names["Sun"], 37.0)
    pressed = update.classify(record, direct(edited(planetary_4to1(), gears={"Planet": dict(at="12")})),
                              exists=lambda _p: True)
    assert pressed.refusal == "" and not pressed.needs_new_revision, (pressed.refusal, pressed.structural)
    sw.calls.clear()
    return sw, pressed, names


def test_a_turned_planetary_is_put_back_with_its_gear_mates_off_and_every_frame_holds(turned_findings, monkeypatch):
    sw, pressed, names = _planetary_turned_and_pressed(monkeypatch, "gear mates off around the puts")
    result = swbuild.update_gearbox(sw, **pressed.update_kwargs(), exists=lambda _p: True, mtime=lambda _p: 5.0)
    assert result.failures == [], result.failures
    assert result.restored and result.placed[0] == "C carrier", (result.restored, result.placed)
    kwargs = pressed.update_kwargs()
    for placement in kwargs["placements"]:
        rotation, at = sw.frames[placement.component]
        assert swbuild.same_frame(rotation, at, placement.rotation, placement.at, placement.pitch), placement.gear
    off = [a[0] for n, a in sw.calls if n == "set_mate_suppressed" and a[1] is True]
    first_put = [n for n, _ in sw.calls].index("place_component")
    assert off and all(i < first_put for i, (n, a) in enumerate(sw.calls) if n == "set_mate_suppressed" and a[1])
    assert all(not m.suppressed for m in sw.mates)                       # every gear mate and lock back on


def test_a_turned_planetary_is_refused_before_anything_changes_while_the_put_route_is_unset(turned_findings,
                                                                                            monkeypatch):
    sw, pressed, _ = _planetary_turned_and_pressed(monkeypatch, None)
    with pytest.raises(swbuild.BuildError) as raised:
        swbuild.update_gearbox(sw, **pressed.update_kwargs(), exists=lambda _p: True, mtime=lambda _p: 5.0)
    assert str(raised.value) == ("Putting a turned planetary stage back has not been settled on SolidWorks (findings."
                                 "PLANETARY_PUT_ROUTE is None), so nothing is changed; run probe planetary_put_back "
                                 "first.")
    assert not [n for n, _ in sw.calls if n in ("place_component", "set_mate_suppressed", "set_global_variable",
                                                "open_document")]


def test_with_its_gear_mates_on_a_planetary_put_does_not_hold_in_the_fake(turned_findings, monkeypatch):
    """The fake as SolidWorks was: the app's earlier route (carrier first, gear mates on) reads back short."""
    sw, pressed, names = _planetary_turned_and_pressed(monkeypatch, "gear mates off around the puts")
    carrier = "carrier1-1"
    with pytest.raises(SolidWorksError, match="did not take its frame"):
        sw.place_component(carrier, IDENTITY9, sw.frames[carrier][1], kind=swcom.ASSEMBLY_TRAIN)


W7_PUT_BACK_LOG = "c0e98c21b97164fb77e9963594dee9ea91eb0b63d8aa4e9b5684a47534676cd1"
# W9a (re-pinned at package A's fix round): the same log with W9a's reads of the user's work in it — one
# feature_states per part document read with its features, one components for the assembly. With those reads taken
# out, the log still hashes to W7_PUT_BACK_LOG. Re-pinned at W9c (the probes' review, must-fix 1): the user-work read
# also reads the active configuration's root component once (root_component), to tell the assembly's own entity.
# Back to W9a's own log (before 7e0d095): the root is read only when a mate entity names no top-level component
# (the W9c review's should-fix 5), and this press has no mate of the user's.
W9A_PUT_BACK_LOG = "69d45d4cb956703b5bfa9cd4555b284fbf4f093d487794bdee8fa7d0ec3be5b4"
W9A_READS = ("components", "mate_info", "feature_states", "root_component")


def test_the_w7_put_back_calls_are_pinned_whole(turned_findings, monkeypatch):
    """E's case, the call log on the fake exactly as 9f21d99 made it (W7 closes on p3 run against that sequence):
    any later change to it is seen here."""
    import hashlib
    sw, pressed, _ = _planetary_turned_and_pressed(monkeypatch, "gear mates off around the puts")
    swbuild.update_gearbox(sw, **pressed.update_kwargs(), exists=lambda _p: True, mtime=lambda _p: 5.0)
    every = [(n, a) for n, a in sw.calls]
    assert len(every) == 149 and hashlib.sha256(repr(every).encode()).hexdigest() == W9A_PUT_BACK_LOG
    assert [n for n, _ in every if n in W9A_READS] == ["feature_states"] * 6 + ["components"]
    calls = [(n, a) for n, a in every if n not in W9A_READS]
    assert len(calls) == 142
    put = [n for n, _ in calls[calls.index(("set_global_variable", calls[[n for n, _ in calls].index(
        "set_global_variable")][1])):]]
    assert put[:24] == (["set_global_variable", "rebuild"] + ["component_frame"] * 7 + ["set_mate_suppressed"] * 5
                        + ["rebuild"] + ["place_component"] * 6 + ["mate_states", "set_mate_suppressed",
                                                                   "set_mate_suppressed"])
    assert hashlib.sha256(repr(calls).encode()).hexdigest() == W7_PUT_BACK_LOG


def _carrier_train_put(monkeypatch, gear_mates, already_off):
    """_put_train on the built, turned Planetary_4to1 with ``already_off`` suppressed before the put (as a per-mode
    gear mate off in the configuration shown would be) and ``gear_mates`` the ones on there (None: W7's call)."""
    sw, pressed, names = _planetary_turned_and_pressed(monkeypatch, "gear mates off around the puts")
    kwargs = pressed.update_kwargs()
    motion, placements = kwargs["motion"], kwargs["placements"]
    sw.open_document(kwargs["assembly"])
    handle = {}
    for index, p in enumerate(placements, 1):
        sw.find_component(f"placed{index}", p.component)
        handle[p.gear] = f"placed{index}"
    mate_handle = {}
    for index, m in enumerate(motion.mates, 1):
        sw.find_mate(f"mate{index}", m.name)
        mate_handle[m.name] = f"mate{index}"
    sw.mate(already_off).suppressed = True
    result = swbuild.GearboxUpdate()
    train = [p.gear for p in placements if p.gear not in motion.fixed]
    train += [g for g in motion.held if g not in train]          # as the Update judges a train: its held gears too
    locks = [lock for lock in motion.locks if lock.anchor in train and lock.follower in train]
    live = {p.gear: sw.component_frame(handle[p.gear]) for p in placements}
    # back to the frames on record (the Face Z the press would set first is not set here)
    swbuild._put_train(sw, result, motion, train, locks, [], handle, mate_handle,
                       {p.gear: (p.rotation, p.at) for p in motion.recorded},
                       lambda: sw.rebuild(kind=swcom.ASSEMBLY_TRAIN), "Planetary_4to1.SLDASM", [False],
                       held=list(motion.held), carriers=[link.carrier for link in motion.carriers], live=live,
                       pitch={p.gear: p.pitch for p in placements}, gear_mates=gear_mates)
    return sw, motion, result


def test_a_gear_mate_off_in_the_mode_shown_stays_off_through_a_carrier_trains_put(turned_findings, monkeypatch):
    """The review's input (9.1): a per-mode gear mate in a carrier train, off in the configuration shown, is neither
    suppressed nor turned back on by the put; the gear mates on there are, and the put holds."""
    off = "Sun meshes Planet copy 1"
    sw, motion, result = _carrier_train_put(monkeypatch, None, off)
    assert sw.mate(off).suppressed is False                         # W7's call: every gear mate, all back on
    on_here = [m.name for m in motion.mates if m.kind == "mesh" and m.name != off]
    sw, motion, result = _carrier_train_put(monkeypatch, on_here, off)
    assert sw.mate(off).suppressed is True                          # off in this mode, and still off
    assert all(not sw.mate(n).suppressed for n in on_here)
    assert result.placed[0] == "C carrier" and not result.failures


def test_a_modes_put_hands_the_carrier_train_only_the_gear_mates_on_in_the_mode_shown(monkeypatch):
    seen = []
    monkeypatch.setattr(swbuild, "_put_train", lambda *a, **k: seen.append(k.get("gear_mates")))
    couple = swbuild.MateRef("RangeSlv engages Sun", "couple", ("RangeSlv", "Sun"), modes=("4L",))
    mesh = swbuild.MateRef("Sun meshes Planet", "mesh", ("Sun", "Planet"))
    motion = swbuild.MotionUpdate(mates=(couple, mesh),
                                  meshes=(swbuild.MeshLink("RangeSlv", "Sun", 1.0, 12.0, modes=("4L",)),
                                          swbuild.MeshLink("Sun", "Planet", -1.0, 20.0)),
                                  configurations=("4H", "4L"))
    placements = [swbuild.Placement(g, f"{g}-1", IDENTITY9, (0.0, 0.0, 0.0), 20.0) for g in ("RangeSlv", "Sun", "Planet")]

    class Frames:
        def component_frame(self, handle):
            return (IDENTITY9, (0.0, 0.0, 0.0))
    for mode in ("4H", "4L"):
        swbuild._modes_put(Frames(), swbuild.GearboxUpdate(), motion, mode, mode, placements, ["RangeSlv", "Sun",
                           "Planet"], {p.gear: (p.rotation, p.at) for p in placements}, {p.gear: p.gear for p in placements},
                           {}, None, lambda: None, "X.SLDASM", [False], moved=True, check=None)
    assert seen == [["Sun meshes Planet"], ["RangeSlv engages Sun", "Sun meshes Planet"]]
