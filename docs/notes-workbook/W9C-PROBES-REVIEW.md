# Review of W9c's probes (P1, M1's leftovers, S5, P2) on SolidWorks 2026

*Independent, 2026-11-17, at `529f939`. I started no SolidWorks.*

- *What I ran:* `python3 probe/w9c_probes.py --self-check` (0 failed). No suite run was needed, since no app code
  changed.
- *What I read:*
  - both 2026 logs (`w9c-probes-sw2026-20261117-1-p1-m1-p2.log`, `…-2.log`) and the second run's JSON;
  - the script and its note;
  - the plan's §0.3, §2.1 (W9c), §2.5, §4 (P1, M1, S5, P2), §5 (W9c, W9d) and its last two *Changes after* sections;
  - `swbuild.read_user_work` and `judge_user_work`, and `swcom.mate_info`;
  - the macro database's assemblies/06, /07, /12, /13, GOTCHAS §300 and its ledger.
- *What I changed:* this file is the only one I wrote.

Line numbers are the second log's (`…-2.log`) unless a file is named.

**Verdict.**

- **W9c's packages can start on 2026's readings.** The delete route is measured well enough for W9c (P1). Inserting
  and mating in a configured, reopened assembly needs no probe ahead: W9c's full build is that measurement (M5, M6),
  as the plan says.
- **One app fault was found by the probe and proposed by nobody (must-fix 1).** On 2026 a mate entity on the
  assembly's own plane names the root component, `'RangeBox'`. The app's `read_user_work` therefore reads it as a
  *user component* called RangeBox.
- **Two things W9d's packages need are not shown (must-fix 2, 3).** Neither stands in W9c's way:
  - a component's state per configuration, read without marking the user's assembly. The plan's own fallback cannot
    keep the save flag unchanged, since a show marks the assembly;
  - a persistent reference on a **face**, the commonest user mate entity.
- **Of the twelve proposals,** six stand as proposed, four should be set narrower, one is not shown as worded
  (`OPEN_READ_ONLY_ROUTE` for an assembly already open), and one is rightly None
  (`COMPONENT_STATE_PER_CONFIGURATION_ROUTE`). See the table.
- **The coordinator's reading of the one FAIL is right.** The flag was cleared before the reads (Save3), the first
  route left it clear, and the second route turned it on. One cheap candidate was not tried:
  `GetRootComponent3(False)`.
- **The script is trustworthy for what it proposes,** with four places where a reading claims more than it can show
  (should-fix). It logs no SolidWorks frame title and no foreign document title. The Windows account folder in every
  path is a privacy point for the coordinator (should-fix 5).

---

## Must fix

**1. Must fix before W9c's or W9d's packages rely on the user-work inventory: the assembly's own mate entity reads as
a user component named after the assembly.**

- *What SolidWorks gave.* s5 (a) read UserAsm6's second entity (a distance to the assembly's own Front Plane) with
  `ReferenceComponent` giving the root component: *"assembly: the assembly's own (the root component); tree order 1;
  component 'RangeBox'"* (log :260-262). The script found this because its first run crashed on it.
- *What the app does with it.* `swcom.mate_info` turns the entity's `ReferenceComponent` into its `Name2`, and `""`
  only when it is None (`swcom.py:2550-2551`). So `read_user_work`'s `owner` (`swbuild.py:5618-5628`) returns
  `(USER, "RangeBox")`, not `(ASSEMBLY, "")`.
- *Today, in W9a's code.* Such a mate touches a phantom user component with no path:
  - `as_subassembly` then takes it for a sub-assembly (`swbuild.py:5344-5347`);
  - the inventory and footer would name "RangeBox" as a component of the user's.
  The judgement's refusals (non-locks on put bodies, ties by SolidWorks' read) are not changed by it in any case I
  can build, so W9a's 2026 behaviour stays safe. But it is wrong.
- *In W9d, which rests on it.* Tier 2 (the assembly's planes by tree order) is unreachable through the app's own
  read, and the phantom component would go into the component map as a user component to insert.
- *Fix.* In W9c package A, `owner` maps the active configuration's root component's `Name2` to `ASSEMBLY`. Read it
  once per inventory, as s5 (a) did (`GetActiveConfiguration().GetRootComponent3(True).Name2`; that read marked
  nothing there). Also propose the finding the run bears out: `ASSEMBLY_ENTITY_COMPONENT_IS_ROOT_ON_2026 = True`. On
  2024 it is open: the 2024 run's s5 (a) answers it.

**2. Must fix before W9d's packages (not W9c's): no route reads a component's state per configuration without marking
the assembly, and the plan's fallback cannot keep the save flag unchanged.**

- *The FAIL is a finding, as the coordinator read it.* In `s5_states` (`probe/w9c_probes.py:1064-1124`), Sprocket-4
  is suppressed in L, shown back to H and rebuilt, then saved with `Save3`. Then:
  - `IsSuppressed2` runs, with the flags read around it;
  - `GetRootComponent3` runs, with the flags read around it;
  - the truth is read with each mode shown.
- *What `flags_changed` shows.* It reports a document only when its flag went False → True (`:162-164`). Route 2's
  report of `RangeBox.SLDASM` (log :282) therefore proves the flag was False just before route 2, so Save3 had
  cleared it and route 1 left it clear, and that route 2 turned it on.
- *The two routes.*
  - Route 1 (`IsSuppressed2(3, names)` on the component's feature) read False in L, where the truth is suppressed.
    Wrong.
  - Route 2 (each configuration's `GetRootComponent3(True)`, its child's `GetSuppression2`) read 2, 2, 0, against
    a truth of 2, 2, 0. Right, including the configuration not shown (L), but it marked the assembly.
- *Not tried.*
  - `GetRootComponent3(False)`. The argument is *Resolve*, and resolving a configuration's lightweight or unloaded
    components is the likeliest thing in route 2 to mark a document. It is the one-line candidate.
  - Route 2's calls flagged one at a time (`GetConfigurationByName`, `GetRootComponent3`, `GetChildren`, `Name2`,
    `GetSuppression2`), to name the call that marks.
  - The macro database names no other route. assemblies/13 and the ledger have `GetRootComponent3(True)` on the
    active configuration only.
- *The plan's fallback (§0.3's fourth exception, §2.5) asks to show the old assembly's modes and restore its active
  one "with `GetSaveFlag` unchanged".* That cannot hold when the old assembly starts unmodified. The macro database
  measured on 2026 and 2024 that `ShowConfiguration2` turns the assembly's flag False → True before any rebuild
  (assemblies/13 :49-52; GOTCHAS :300). `IModelDoc2` has no call that clears the flag short of saving, which the app
  never does.
- *So the fallback needs, besides a ruling:*
  - (a) whether a read-only open of the old assembly when it is **not** open (measured here: read-only, flag False,
    log :291) can be shown mode by mode and closed unsaved with no question. That covers the case where it is not
    open;
  - (b) for the case where it is open, the user's word on one of these:
    - its flag left True, said ("RangeBox.SLDASM shows as changed: nothing in it was");
    - the per-mode state not carried (each component carried in its active-mode state, said);
    - Build again… refused until the user saves or closes it.
- *Re-measure first.* Run `GetRootComponent3(False)`, and route 2's calls one at a time, on 2026 and 2024, in W9c's
  session beside S5's other owed items (must-fix 3).

**3. Must fix before W9d's packages (not W9c's): a face's persistent reference is not measured.**

- *What is shown.* `PERSIST_REFERENCE_ROUTE`'s thirteen entities were reference axes and planes: Gear Axis, Input
  Axis, Output Axis, and the Front, Top and Right Planes of parts and the layout (log :265). The note says so
  (*What the plan's S5 row asks that this does not measure*).
- *What W9d's tier 1 rests on.* It finds every user-to-user mate, and every mate on a reused app part, by this route:
  "on a file both revisions use … its persistent reference" (§2.5). A user's mates are mostly on faces: a concentric
  to a bore, a coincident between end faces.
- *Owed.* A face and an edge, read through the component and resolved in the second assembly, on 2026 and 2024. The
  setup is there: m1's concentric (a face, `reference_type 2`, log :152) and its width (four faces). It needs no new
  call; only the entity kind is new.

---

## Should fix

**1. `OPEN_READ_ONLY_*`: the already-open case's flag was not caused by the call.**

- s5 (d)'s first open (log :288) ran after (e). That is after route 2 marked the copy, and after the truth read showed
  every mode, which marks it too (must-fix 2). So its `save_flag: True` was True before `OpenDoc6`, and the script
  read no flag before the call.
- What it does show: on a document already open, `OpenDoc6(…, Silent | ReadOnly)` returns the open document with
  warning 128 (already open) and **does not make it read-only**.
- *Fix.* For the record, read the flag before and after the call on a clean open copy. For W9d the conclusion stands
  either way: the plan already reads an open old assembly "as it is in the session", so the read-only open serves only
  the not-open case.

**2. p1 reads the mates' error codes in the active configuration only.**

- `p1_delete` reads `mates_after` once, after the rebuild, with the active mode shown. The per-configuration loop
  then lists components only (`probe/w9c_probes.py:443-458`). So "no mate in error after the delete" is H's, not N's
  or L's.
- For HighDog, the deleted coupling was on in H only, and nothing else on Output depended on it. So I expect nothing
  else to differ, but it is not read.
- *Fix.* Read `mate_states` per configuration in the 2024 run, or let W9c's full build carry it (it reads every mate
  in every mode after an Update anyway).

**3. m1's "named by the footer's judgement: no" cannot fail for four of the five kinds.**

- Concentric, both limits and width touch only the layout and user components (log :190-193). No put body is
  involved, so W9a's judgement could never name them, whatever their kind.
- Only the gear mate on Sun tests the judgement, and it is refused by name (log :187), as W9a's rule requires.
- So m1 shows that `mate_info` reads each kind wholly without marking anything. It does not show how any kind on a
  put body is judged. That is said under the findings table, so nobody reads more into the four "no" lines.

**4. `COMPONENT_DELETE_IN_EVERY_CONFIGURATION` rests on one route.**

- Only route 1 ran on RangeBox (`P1_CASES`, `probe/w9c_probes.py:390`). The reducer has one configuration, so its
  three routes say nothing about configurations.
- Set it for route 1, which is the proposed route. Nothing more is needed.

**5. The logs and JSON carry the Windows account's folder name in every path.**

- Every path under the probe folder begins with `C:\Users\<account>\`. That is in this run's two logs and its JSON,
  as in W9a's and W9b's logs before them.
- The script keeps its other promise: no SolidWorks frame title, no document title but the run's own
  (`title_is_the_runs: True`). The dialog texts show only the run's own file names, truncated by SolidWorks.
- The repo is public, so this is the coordinator's call: redact the account folder in `say()` from now on (W9a's
  script owns `say`), and decide whether to rewrite the committed logs. I have not repeated the name here.

---

## The findings, one by one

| Proposed | Verdict | What the run bears out, and its scope |
|---|---|---|
| `COMPONENT_DELETE_ROUTE = 'select4-editdelete'` | **Set as proposed** | `Select4(False, null, False)` + `EditDelete()` (its return is None; judge by the reads, as the script did). Shown on a gear with app mates only, alone in its part file (G4) and sharing a file with another instance (HighDog beside LowDog, whose mates all stayed: `other_mates_lost []`, log :101). The other two routes are equally clean on the reducer. Not shown: a component with a user mate or an in-context reference on it. W9c refuses those before any delete, by the plan (§2.1), so nothing rests on it. |
| `COMPONENT_DELETE_IN_EVERY_CONFIGURATION = True` | **Set narrower** | Route 1 only, on RangeBox's three modes, an assembly reopened from disk, each mode shown and its components listed. The others were not run with configurations (should-fix 4). Mate errors per mode were not read (should-fix 2). |
| `COMPONENT_DELETE_TAKES_ITS_MATES = True` | **Set as proposed** | Every touching mate is gone from the MateGroup walk and from `FeatureByName`, and every other mate is still there, in all four cases. Covered: a coupling on in one mode only (`RangeSlv engages HighDog`), a lock, a mesh, an axis and an along. |
| `COMPONENT_DELETE_KEEPS_OTHER_HANDLES = True` | **Set as proposed**, scoped | Within one epoch: no configuration shown and no open between the keep and the use (`epoch_kept == epoch_held_read`). After a show, handles go stale anyway (GOTCHAS §108). |
| `COMPONENT_DELETE_DIALOG = False` | **Set as proposed** | None of the three routes raised a dialog, and the watch ran through each delete. 2024 is owed (running). |
| `M1_READS_CONCENTRIC`, `_LIMIT_DISTANCE`, `_LIMIT_ANGLE`, `_WIDTH`, `_GEAR_ON_AN_APP_GEAR = True` | **Set as proposed**, scoped | `mate_info` gives each one's type (1, 5, 6, 11, 10) and every entity's component, `whole` True, with no document marked (log :152-156). Checked by hand: the components match what was made. Entity kinds covered: face–axis (concentric, the face on a user part), plane–plane (both limits), four faces (width), axis–axis (gear). Limits read their range in the definition's `MaximumDistance`/`MinimumDistance` and `MaximumAngle`/`MinimumAngle`. Width was made only with the tab at mark 16 (log :147-149), a fact for the macro database. **What this lets through:** the app has no list of kinds, and judges by `whole` and by what a mate touches (`judge_user_work`). Before m1, a user's concentric, limit or width mate among the user's components and the layout passed on `whole` True, unmeasured; now it is measured on 2026. **What stays refused:** any of these kinds with an entity on a body Update puts (only a lock is carried); the user's gear mate on Sun (refused by name, log :187); path, not made (it passes or refuses on `whole`); a sub-assembly locked to a put gear (`USER_MATE_PUT_SUBASSEMBLY_*` None). |
| `M1_READS_SUBASSEMBLY_LEAF = True` | **Set as proposed** | The leaf's `Name2` is the path `UserSub-1/P2Sprocket-1` (log :322), which `owner` already splits to the top-level component. One leaf, one coincident, the sub-assembly with no configurations of its own. |
| `PERSIST_REFERENCE_ROUTE` | **Set narrower** | Reference features only (axes and planes of user parts and the layout), resolved in the same part document the second assembly's instance uses. Faces, edges and vertices are not shown (must-fix 3). Neither is the assembly-context route (read only, length 74/88) or 2024. |
| `MATE_REMAKE_FROM_DEFINITION_ROUTE` | **Set narrower** | Ten mates remade with equal definitions and frames: coincident ×5 (axis–axis), lock ×3 (whole components), distance ×2 (plane–plane, one to the assembly's own Front Plane by tree order) and angle ×1. All at alignment 0 or 2, none flipped, into a one-configuration assembly. **Not covered**, against §2.5's carried kinds: concentric, parallel, perpendicular, tangent, limit distance and angle, gear, any face, edge or vertex entity, a flipped mate, a leaf inside a sub-assembly, and a mate's flag set per configuration. Their definitions are read in m1, but none is remade. W9d's own probe or full build owes them before it claims them. |
| `COMPONENT_STATE_PER_CONFIGURATION_ROUTE = None` | **Rightly None** | Must-fix 2. Re-measure `GetRootComponent3(False)`. |
| `OPEN_READ_ONLY_DIALOG = False` | **Set as proposed** | Both opens, with no dialog. |
| `OPEN_READ_ONLY_ROUTE` | **Set narrower** | For an assembly not open: read-only, flag False, errors 0, components opened (a progress box only). For one already open: it returns that document, not read-only (warning 128), and its effect on the flag is not shown (should-fix 1). So: "the not-open case only". |
| `SUBASSEMBLY_INSERT_ROUTE` | **Set as proposed**, scoped | Open the sub-assembly first, then `AddComponent5`, into an assembly with modes. The leaf mate's flags read off in every mode (log :322). Not read: the opened healthy sub-assembly's own save flag, or the inserted sub-assembly's state per mode. |
| `SUBASSEMBLY_MISSING_REFERENCE_DIALOG = False` | **Set as proposed**, scoped to a **Silent** open | No dialog in the open, the insert, or 10 s after each (log :326-327). See below for what it reads. |

**What a missing part reads as, and what W9d should do with it.**

- *The open.* `OpenDoc6(…, Silent)` of the sub-assembly returned the document with errors 2 and warnings 0.
- *The missing child.* It reads `GetSuppression2` 0, which is suppressed. It keeps its stored path, and has no
  document.
- *The sub-assembly.* It reads **modified** (save flag True) straight after the open and after the settle.
- *Inserted into the host,* the child reads the same, under the path `UserSubMissing-1/P2Missing-1`. The host's flag
  was already True from the first insert, so it says nothing.

So W9d must:

- tell a missing part from a part the user suppressed. Suppression 0 *and* no document *and* its file absent on disk
  is missing;
- carry the sub-assembly by its file, as it is, its child coming over missing;
- name it: *"UserSubMissing's part P2Missing.SLDPRT is not on disk; it comes over missing, as it was"*;
- reckon with the open marking the user's own sub-assembly document. If W9d has to open a user sub-assembly that is
  not already open (§2.5, P2), that open is a write to a user document's state under §0.3's STOP on "a read … marking
  a document". W9d's plan must rule on it: say it, or refuse to carry that sub-assembly.

Whether a healthy sub-assembly's open marks it was not read. Add that to the 2024 run, or to S5's owed items.

---

## What W9c's packages may rely on (2026; each finding None on 2024 until its run confirms it)

**May rely on:**

- **Removing a gear:** `Select4` + `EditDelete`. The component goes from every mode with its app mates, couplings on in
  one mode only included, and no dialog. Other components' handles held in the same epoch still answer. The assembly
  ends marked, which is expected, and Update leaves it unsaved.
  - Judge success by the reads (the component gone, the touching mates gone by name, every other mate still there),
    not by `EditDelete`'s return.
  - Refuse before the delete, as planned, when a user mate is on the gear (from W9a's inventory, no new read).
- **Inserting a component into a reopened assembly with modes, and mating it:** `AddComponent5` and `AddMate5` there
  were run in S0, W9a's demonstration, m1 and s5 with no dialog.
  - m1 and s5 made user mates with H active, and every one's flags read back as set in every mode (log :142, :230).
  - s5 logged the two it made as they came: **on in every mode** (log :227-228). m1 logged its mates only after
    setting them.
  - A component inserted earlier read resolved in a mode not active (s5 (e)'s truth before the suppression, H and N
    2).
  - So M5 and M6 need no probe ahead: no call is new to the app, and none raised a dialog. W9c's full build is their
    measurement, setting and reading every flag as planned. One adjustment: the component's state per mode is read
    by showing each mode, which Update does anyway. Must-fix 2's unshown read is W9d's need, not W9c's.
- **The user-mate inventory** reads every standard kind wholly on 2026 (m1), and a sub-assembly leaf by its path
  (p2), once must-fix 1 is in.

**May not rely on, or must measure in W9c's full build:**

- **M4, the external-references read** (an in-context reference to a gear W9c would remove). It is a read, with no
  dialog risk known, so it is safe to leave to the full build under the rule: a probe ahead is only for a call that
  could hang, raise a dialog or damage a file or session. W9a's discipline applies: `GetSaveFlag` around it, and any
  marking is the §0.3 STOP. Until it is read on both versions, a removal with a user part present should refuse as
  unmeasured rather than pass.
- **M8, bands added to a built part in place.** Every call is the build's own (W9b's relief route, measured on 2026),
  and the context is new: features appended after the user's features in a part reopened under an assembly. The risk
  is a rebuild error in the user's feature, which on 2024 shows What's Wrong. That box is measured as non-blocking and
  ruled to be left alone. So the full build can measure it. The removal side (*"bands taken away suppress the app's
  relief features"*, §2.4) is `SetSuppression2` on part features, as for mates. Also the full build's.
- **M10, a mode added and one removed** in a saved, reopened assembly with the user's items. `AddConfiguration2` and
  `DeleteConfiguration2` are the build's own on both versions, so the full build can measure it, as planned.
  Re-fetch handles after the add (ruling 9.4).
- **W9b's 2024 build, and every finding above on 2024.** The 2024 run is going now. Until the addendum, each W9c
  path gated on these findings must read None on 2024 and refuse, as W9a's did.

**For W9d only, owed before its packages:**

- must-fix 2: the per-configuration state, the fallback ruled;
- must-fix 3: a face's persistent reference;
- the remake of the §2.5 kinds not yet covered (table);
- whether opening a user's sub-assembly marks it.
