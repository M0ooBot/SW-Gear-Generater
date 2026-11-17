# Review of W9d's interface note and its probe script

*Independent, 2026-11-17, at `7e478b3` (branch `w9d`). I started no SolidWorks or Excel and changed no source, test or
document but this one.*

- *What I read:* `W9D-INTERFACES.md` whole; `probe/w9d_probes.py` whole and `W9D-PROBES.md`; the plan's §0.2 (K5),
  §0.3, §2.1 item 8 and its closing list, §2.5, §4 (S5, M9), §5 W9d and the four *Changes after…* sections; HANDOFF's
  *Rules carried over*; `W9C-PROBES.md`'s findings as `findings.py:1830-2007` holds them; the two committed S5 logs
  (`w9c-probes-sw2026-20261117-2.log`, `sw2024/w9c-probes-sw2024-20261117.log`) whole for m1 and s5; the API ledger's
  rows for `QuitDoc`, `AddConfiguration2`, `AddMate5`, `MateEntity` order and the gear ratio, and GOTCHAS §100; the
  installed API help (the decompiled 2024 `sldworksapi.chm` and `swconst.chm` already in the Windows temp folder) for
  `GetCorrespondingEntity2`, `GetComponentSuppressionState` and its example, `ISldWorks.IsSame`, `swObjectEquality`,
  `swPersistReferencedObjectStates_e`, `IEntity.GetComponent`, `GetRootComponent3`, `IsOpenedReadOnly`.
- *Code read against the note:* `swbuild.build_gearbox` (`:3311-3487`), `read_old_assembly`/`_read_before`
  (`:6681-6718`), `_read_user_work` (`:6587-6661`), `_carry_frame` (`:5384-5404`), `in_place_gates` (`:5880-5918`);
  `swcom._component_ref` (`:2120-2157`), `use_open_document`, `open_document` (`:3332-3413`), `component_frame`,
  `place_component`, `components`, `show_configuration`, `rebuild_call`; `store` (`:421-425`, `:589-618`,
  `:1300-1371`, `clear_saved`); `update._earlier_update` (`:2450-2470`), `_modes` (`:1486-1530`); `gearbox.Finished`,
  `PartReuse`, `MadeNew`; `ui_text` W9a's two functions and the `UPDATE_LOST` sentence (`:3545-3580`); the gear
  recipes' axis ops; the probe harness members the script calls (`w9c_probes`, `w9a_demonstration`,
  `workbook_assembly_check`).
- *Run:* `--self-check`, 30 checks, 0 failed. Every name the script reaches in `C`, `A`, `W` and `swcom.Session` exists.

**Verdict.**

- **The contract is close to buildable and honest about what is measured.** Its citations of the S5 logs hold
  (`-2.log:156`, `:265-279`, `:281-284`; `w9c24` the same, one line on). Its order of the job matches today's code
  (W9a's read already sits before anything is made, `swbuild.py:3439`). The placement formula is right and the code
  already has it (`_carry_frame`). Schema 10 is right: `link_record_from_json` refuses a newer schema with its
  sentence before reading anything (`store.py:1323-1325`, worded at `:1366-1371`), and a schema 9 file reads forward
  with defaults.
- **Five must-fix points before the packages start.** Two are in what the user was promised: the tie rule (D6) and the
  referenced configuration (D13). One is a hang in the user's session (the read-only close). One is a crossing shape
  the packages would each guess. One is a pair of probe brackets that cannot see what they claim to measure.
- **Three choices are the user's, not the coordinator's.** D2, D12 and the gear-mate consequence of the note's
  contradiction 1 each change what K5 or §2.5 told the user. D6 as written would too, but it should simply be fixed.
- **The probes may run once their two must-fixes are in** (§Probe, P1 and P2). P8 is strongly advised in the same
  edit: it is the one unwatched save of a document the script has just opened.

## Must fix

**1. The tie is laid on every cluster on the train (D6), which contradicts the plan and the note's own M9.**
§6 case 3 makes a cluster fall back when "the cluster has a mate on in that mode with an entity on a body of that
mode's train". RangeBox has one train: the S5 log's footer line names it as Carrier, Sun, the planets, HighDog, LowDog
and RangeSlv (`w9c…-2.log:188`).

*Scenario:* the M9 fixture of §15. Cluster one (Sprocket-1 and -3, Chain-1, Sprocket-4 through `UserDist4`) is locked to
Sun. Sprocket-2 is locked to RangeSlv. Sprocket-6 has its gear mate on Sun. The tied cluster is Sprocket-8 locked to Sun
and to Housing-1. The tie reads in every mode, and every one of those clusters has a mate on Sun's train. So every one
of them falls back, fixed, its locks deleted. That breaks the plan's Done-when ("both clusters carried and their mates
remade") and §15's own judged list. It also breaks K5: a cluster falls back only when *it* ties a gear.

*Smallest change:* make and judge cluster by cluster, which costs no show. After each cluster's mates, do a top-only
rebuild and read `constrained_status` on its train in the mode showing (the new revision's first mode). When every one
of the cluster's mates has the same flag in every mode, that read decides every mode. That is K2's rule, measured by
S0 and used by `_free_to_turn`'s judgement. A tie there makes that cluster fall back at once. Only a cluster whose
mates' flags differ by mode is read again in those modes, in the post-check's shows, which run anyway. Keep §6's
three cases as the plan words them.

**2. The not-open read can hang the user's session, and its "documents open" rule cannot be evaluated (§3 R.2, R.7;
§11.2; D2's not-open branch).**

- *The hang.* GOTCHAS §100 and API-LEDGER `QuitDoc`: on 2026, `QuitDoc` of an assembly **saved by 2024** raised the
  SOLIDWORKS CAM add-in's modal "Save changes to <assembly>?". It ignored `WM_CLOSE` and Escape, and it follows the
  file's version, not the close call. R.7 closes the job's read-only document by `QuitDoc`. Scenario: a RangeBox last
  saved on 2024 (this project uses both versions), a Build again… on 2026 with it closed. The worker never returns; the
  app has no dialog watch.
- *The rule that cannot be evaluated.* §11.2 lets the not-open read run "only when none of the old assembly's user
  documents is open". The record does not keep the user's component files (`UserComponentEntry` has no path,
  `store.py:589-599`: "the file is the user's own and is not kept"). So before the open the app cannot know which open
  documents are the old assembly's.

*Smallest change:* the not-open read is `OLD_UNREAD`, said, unless all of these hold:

- the record says the old assembly was last written by a job on the running major version, and the question says so
  ("a file saved since on another SolidWorks is not read");
- no document is open in the session except ones the record names as the app's;
- `OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN` is True.

Probe P12 can widen this later.

**3. `CarryNamed.subjects` and `CarryFallback.subjects` have no layout (§2.3, §2.4), and §9.3's clauses cannot be
written from them without guessing.**

Each `why` needs different words, and the note gives only an unordered list ("the gear, the part, its why_new, the
finding, the kind word, the entity kind"):

- `part new`: the gear, its `why_new` phrase, the entity kind and whether it is a bore;
- `gone`: the body or the shaft, and which;
- `unmeasured`: the kind word *or* the entity kind, the finding's full name, the version;
- `no file`: the file name, and virtual or not;
- `not found`: the entity kind, the component, the file;
- `assembly feature`: the feature's name;
- `leaf`: the sub-assembly.

"Bore" is promised (§4.4: "only where the read can say so") but nothing in `OldEntity` carries it. The read it needs (a
cylinder whose axis is the gear's: `GetSurface`, `CylinderParams`) is not in §8 and has not been measured marking
nothing.

*Smallest change:*

- A table in §2.3: `why` → the ordered meaning of each `subjects` slot. The same for `FELL_*`.
- Either `OldEntity.role: str = ""` (`"bore"` or `""`), with the read named and bracketed, or drop "bore" and always say
  "a face of Sun".
- Also add `swbuild.UserMate.entities` to §2. §7 has every Update's inventory filling `UserMateEntry.entities`, so A's
  `_read_user_work` and B's finish both touch that shape, and the note never states it.

**4. The referenced configuration is dropped silently (D13), against §2.5's first row.**

The plan's row carries "its file and referenced configuration". D13 inserts "as inserted by default", which is the
part's active configuration in its open document, and says nothing. Scenario: the user's sprocket file has
configurations Z15 and Z20, and the component references Z20. The carry inserts Z15, a different body, places it at
Z20's frame and remakes its mates on Z15's faces (a persistent reference may even resolve). Nothing says the shape
changed. That is worse than naming it, and it is not something the coordinator can rule away.

*Smallest change:* read `IComponent2.ReferencedConfiguration`, a get, bracketed by `GetSaveFlag` and added to the
`faces` probe's (b). Name the component (*"Sprocket-1 uses its configuration Z20, which Gear Generator does not carry
yet"*) whenever that differs from the active configuration of its document as opened. Carrying it properly needs
`AddComponent5`'s configuration arguments, which are new: defer it, said, or put it to the user.

**5. Two probe brackets measure nothing (probe P1, P2 below).** The `faces` reads run on a copy already marked by (a).
The read-only open is judged only beside a part already marked. Each finding they propose gates a read of the user's
own documents. Fix before the run.

## Needs the user's word (each changes what K5 or §2.5 promised)

- **D2.** K5 promises "its state in each mode" and "the user's open documents are never shown in another mode". With no
  clean route, the note's recommendation drops the first for an open old assembly. Every alternative breaks one of the
  two. This is what §0.3's "(a third exception, to be confirmed)" left open. Put the three options to the user
  (mode-showing state said; show and restore, leaving the flag set; refuse until saved or closed). It is moot if
  candidate 1 comes back clean on both versions. A can code both branches now.
- **Contradiction 1, its consequence for gear mates.** The log does show the m1 user gear mate reading two axes,
  ReferenceType2 5, `Gear Axis` (`w9c…-2.log:156`, `w9c24:157`). But that mate was made *by the probe* on axes
  (`raw_mate` in m1). So the log shows only that a gear mate made on axes reads axes. That a gear mate can never take
  whole components is SolidWorks' rule for gear mates (rotational entities only). That is my knowledge of the UI, not a
  log. The conclusion stands.

  The consequence the note does not state: a user who picks Sun's bore face for a gear mate in the UI (the common pick)
  gets it *named* when Sun's part is new. K5 promised it would be found "by component".

  There is an option that keeps the promise without finding by geometric role. A gear mate depends only on its
  rotation axis, and every rotational face of an app gear is coaxial with its `Gear Axis` by construction. So a gear
  mate's entity on an app gear can be taken as that gear's `Gear Axis`. Put "named" or "Gear Axis" to the user.
- **D12.** §2.5's pattern row carries the seed and *names* the instances. D12 carries every instance as a component of
  its own and says so generically, so the user is told something else. It is low stakes, but it is a change to a row
  the user approved. One line to the user. Also say when the generic sentence is said (on every carry is noise).

## Should fix

1. **`moved` is judged against the first mode's placement in every mode (§6, D7).** Sprocket-2 is locked to RangeSlv,
   which slides 10 mm between H and L (setup.master, W9a). It reads "moved 10 mm" in L on every RangeBox carry.
   Compare each carried component's pose in its anchor's frame (`_relative`, `swbuild.py:5407`) per mode, or judge
   `moved` in the first mode only.
2. **The anchor is per cluster (§5.3, D20).** Take a cluster joining Sprocket-1 (locked to Sun) and Sprocket-2 (locked
   to RangeSlv) by a user–user mate. Sprocket-2 is placed by Sun's motion, not RangeSlv's. When the old train stood
   turned, the solver then moves it, said as moved. *Change:* each component takes its own lock to an app body first,
   then the cluster's anchor. `CarryPlanItem.anchor` is already per component.
3. **A component suppressed in the mode showing has `frame` None (§2.2), and `plan_carry` has no rule for it.**
   `CarryPlanItem.frame` is required. Say what happens: placed at its anchor's frame, the world, or named.
4. **The states write sets only "suppressed" (§3 C.5).** A component inserted while the first mode is active may come
   out suppressed in other configurations by the configuration's options. The ledger saw exactly that for a mate made
   while a mode was active (`API-LEDGER.md`, the `AddConfiguration2` row, assemblies/13). *Change:* set the wanted
   state in **every** mode and read it back, as J10 does for flags.
5. **The remake's selection order and the gear ratio are not stated (§10 `remake_mate`).**
   - The ledger: for axis–axis coincident and face–axis concentric, `MateEntity(0)` is the *second* selection
     (`API-LEDGER.md:579`).
   - `GearRatioNumerator` reads the second selection's count, while `AddMate5` takes the first's (`:587`).
   - `Reverse` follows the directions (`:590`).

   S5 (c) remade only symmetric kinds. Write the per-kind order and the ratio swap into §10 and the fake, or the fake
   will agree with a wrong remake.
6. **An origin entity is in tier 2 (§4.2, `ENTITY_ORIGIN`) but no run has read one as a mate entity.** Neither its
   ReferenceType2 nor its feature is known. Classify it `WHY_UNMEASURED` until M9 reads one, or drop it.
7. **Virtual components (§5.1).** I have not checked this on SolidWorks. My understanding is that SolidWorks keeps a
   virtual component's document in a temp folder while the assembly is open. If so, `os.path.isfile` reads True and
   the carry would try to insert the temp file. *Change:* test the `^` in the file name before `on_disk`, or read
   `IComponent2.IsVirtual`, bracketed.
8. **Where R sits against the pre-flight (§3 step 2; D1).** In code, `_read_before` runs before the plans' checks and
   `_refuse_paths`, which reads `open_before` (`swbuild.py:3439`, `:3457`). Suppose R's read-only open leaves a
   document loaded after its close. That document then counts as "open before", and the finish's `opened` and unsaved
   logic misjudges it. *Change:* snapshot `open_before` before R, and have R.7 check the session's document list equals
   what it was before R (else the carry does nothing, said). Probe P3 measures it.
9. **§4.1's "the same document is in fact used twice" is false on the not-open path.** There R reads the reference in
   the read-only load, closes it, and the carry resolves it in a fresh load. Persistent references exist to survive a
   reload, but no run has resolved one after a reload (S5 and the `faces` probe resolve in-session only). Add probe
   P12's reload check, or say the not-open path rests on it.
10. **D16 reuses `LinkRecord.unsaved` for the new assembly.** That field means "an Update's changes not saved", and its
    readers say so:
    - `update._earlier_update` (`:2450-2470`) returns `UPDATE_LOST` / `UPDATE_NOT_SAVED`;
    - `ui_text` then says *"The last Update SolidWorks was not saved before RangeBox_r2.SLDASM was closed, so its
      changes were made again"* (`:3565-3577`);
    - `Finished.off_after_update` stops laying gears found off to the user;
    - `workbook_built_tag` says *"updated from this version, not yet saved"*.

    None is true after a carry. *Change:* `CarryEntry.unsaved_at: float` (the assembly's time after its save), read by
    §9.4's two lines only, and dropped by the same newer-file rule as `clear_saved`.
11. **§8 lacks the value that opens each gate.** `in_place_gates` takes "the delete route its route, a dialog False,
    every other True" (`swbuild.py:5889`). For W9d, `SUBASSEMBLY_OPEN_MARKS` opens on **False**, the persist routes on
    a route string, `CARRY_REMAKE_KINDS` on membership, and `CARRY_INSERT_MARKS_USER_DOCUMENTS` is a fact. Add a
    "settled when" column.
    - The probe proposes `MATE_REMAKE_ON_FACES_AND_EDGES_ROUTE`, which §8 does not read. Either give it a gate (the
      face and edge remake, beside `CARRY_REMAKE_KINDS`) or drop the proposal.
    - "Patched True" (§8's lead) cannot apply to a tuple. Say M9 patches `CARRY_REMAKE_KINDS` to every carried kind
      word.
12. **`ROOT_COMPONENT_UNRESOLVED_READ` cannot license the read it gates.** The probe says outright it cannot tell
    whether `GetRootComponent3(False)` marks (the copy is marked by then). A read found marking is §0.3's STOP, and R.6
    would only catch it after the user's assembly was marked. Keep `_read_user_work`'s rule (no root read with a
    lightweight component, `swbuild.py:6608-6617`) and drop this finding. Or measure it on an assembly *opened* with
    the component lightweight, which is a new open option, so do not.
13. **Sentences the plan asks for that §9 lacks.**
    - §2.5: "a floating component that stood differently per mode stands … where it stood in the old assembly's active
      mode, **said**". There is no sentence, and with modes it applies to every floating carried component.
    - Display states and appearances: §5.1 says "said", and §9.2 has no clause for them.
    - The keyway clause of §9.1 carries the part's why only through a mate clause before it. With no such mate the
      question says "which Sun's new part replaces" with no why, against §2.5's row.
14. **Shapes an implementer would guess.**
    - `plan_carry(new_frames=…)`: keyed by `CarryBody.old` or by handle?
    - `CarryResult.work` None versus `OldWork.how == OLD_UNREAD`: which does A use when? Say None only when the read
      raised.
    - Whether `stopped` is set when R.6 finds a mark.
    - `CarryBody.names` per body kind: `swbuild.plan_features(plan)` for a part made new, the sidecar's `features` for a
      reused one, `layout_features` for the layout and carriers.
    - `Carry.old` must be the same object as `before`.
    - The new revision's `user_work` when nothing was carried: None, as W9a, or an empty inventory?
15. **M9's outline.**
    - "Sprocket-7 suppressed in L alone" holds only if the states route is clean. On D2's open-case fallback it is
      resolved everywhere, said. Write both outcomes.
    - Chain-1's two mates rest on `PERSIST_REFERENCE_ROUTE_FOR_FACES`. If that comes back None, cluster one is
      "carried" without them, and the Done-when must say which mates it relies on. Better, use feature mates for the
      Done-when's clusters and face mates as a further item.
    - Run `carry-closed` from a file saved with L active, so "read in L, placed in H" (contradiction 6) is exercised on
      SolidWorks with the sliding RangeSlv.
    - Add one lightweight component (D10) and one component suppressed in the mode showing, with a mate (should-fix
      3; what R reads of a mate whose component is suppressed there is not measured).
    - With D6 fixed, the tied cluster is the only fallback M9 shows. `FELL_NEW_ERROR` and `FELL_OVER_DEFINED` are
      shown on the fake only. Say so.

## Notes

- **The 37° example (§5.3) and its test (§14.1) are worded wrongly.** The frame `new(Sun) · old(Sun)⁻¹ · old(sprocket)`
  keeps the sprocket's angle *relative to Sun*. Worked by hand: old Sun is Rz(37°) at (0, 0, 10) and the sprocket
  Rz(37° + θ) at (0, 0, 20); the new Sun is Rz(0) at (0, 0, 10.5). Then the motion is Rz(−37°), the shift (0, 0, 0.5),
  and the sprocket goes in at Rz(θ), (0, 0, 20.5). That is θ to the new Sun, 37° less in the world than it stood, not
  "at 37° to Sun's new frame". Reword the test as "at the angle to Sun it stood at", or A writes a test that asserts the
  wrong pose. The code to use is `_carry_frame(old anchor, new anchor, old component)`; the note should cite it.
- Contradiction 6's reasoning is right (worked with RangeSlv: placed relative to its H frame from its L frame, then the
  lock carries it per mode). Only `moved` needs should-fix 1.
- `FELL_NEW_ERROR` compares against an old code read in one mode only. A mate in error in another mode before the
  carry falls back as "new". It is conservative and said; note it in §6.
- If `CARRY_INSERT_MARKS_USER_DOCUMENTS` reads True, the user's later save of RangeBox_r2 will also save their marked
  part. The sentence should say that, not only "nothing in it changed".
- D5 should classify entities by `ReferenceType2` (m1's measured read), not by `GetSurface`/`GetCurve`, which §11.4
  uses and the inventory's read has not been shown to mark nothing.
- Renaming a Modes row is one of the edits that reach Build again… (`update.py:1508-1512`), so D14's "old mode's
  states dropped" is a central case, not an edge. The rule is defensible and matches what the question already says.
  Make the sentence plain.
- `store.py:1372-1376` in §7 is `:1366-1371` at this commit.
- §7's "schema 9 read forward: `carry` None" needs B to add a nested reader. `GearboxRecord(**_known(...))` would leave a
  dict there. That is B's to do, not a contract gap.
- `moved`'s 1e-6 mm tolerance will say solver noise after a rebuild with new mates. Use the build's own frame
  tolerance.

## The plan, row by row

- *Components.*
  - The file: carried.
  - The referenced configuration: **dropped** (must-fix 4).
  - Fixed or floating: carried.
  - State per mode: carried, or the mode showing's (D2, the user's word).
  - Placement relative to the app component: right, with should-fix 1 and 2.
  - Placed once, said: **the sentence is missing** (should-fix 13).
  - Virtual named: should-fix 7.
  - Flexible carried rigid, said: yes.
  - Display states: sentence missing.
- *Mate kinds:* the carried list and the named list match §2.5 exactly. "With alignment, flip, values and flag in each
  mode": yes, gated by `CARRY_REMAKE_KINDS`.
- *A feature in a part made new:* named before and after, with the `MISMATCHED` and `UNSAVED` advice (D17 sound). The
  keyway clause needs its why (should-fix 13).
- *Pattern:* D12 (the user's word).
- *Assembly features, in-context references:* as the plan says.
- *Tiers:*
  - Tier 1 as the plan says.
  - Tier 2 as the plan says, widened by D3.
  - Tier 3 narrowed to locks, with the gear-mate consequence put to the user.
  - Tier 4 as ruled.
- *Fallback:* three cases kept; D6 must be fixed.
- *Never written:*
  - The old assembly: never written on the open path. On the not-open path, read only in the job's own read-only
    document, but must-fix 2.
  - User files: never saved.
  - After the first save: no `Save3` or `SaveAs3` anywhere in §3.

## The designer's choices

- **D1** (read before build): **agree**. It is W9a's place, and it keeps the reused parts from being open under the
  read. Two conditions: should-fix 8, and R.7 checking the session is left as found.
- **D2:** **the user's word.**
- **D3** (an app gear's own names on a part made new): **agree**.
  - `Gear Axis` is made unconditionally by every recipe (`spur.py:804`, `internal.py:922`, `helical.py:522`,
    `bevel.py:1131`; clutch parts come through internal and spur).
  - The names are set by the app itself, so they do not depend on the install's language. Base planes go by tree
    order (`_component_ref`, `swcom.py:2136-2138`, reads the name from the part, never assumes it).
  - `Mid Plane` and `Profile Plane` exist only on herringbone and helical parts. Their absence is `WHY_GONE`, which is
    right.
  - B must take the list from `plan_features`, not from a fixed tuple.
- **D4** (one tuple of kinds): **agree**. Say "settled" means the kind is in the tuple, and what M9 patches it to.
- **D5** (entity kinds in the inventory): **agree**, read by `ReferenceType2`.
- **D6:** **disagree** (must-fix 1).
- **D7** (moved said, not a fourth case): **agree**, compared per mode in the anchor's frame (should-fix 1).
- **D8** (interference again): **agree**. Fold it into the post-check's shows.
- **D9** (no gate on the fallback's writes): **agree**. `MATE_DELETE_ROUTE` and `fix_component` are verified. M9's tied
  cluster exercises it.
- **D10** (lightweight: carried, its mates named): **agree**. This is within K5's "named with why", and the advice to
  resolve first is the right sentence.
- **D11** (no carry again): **agree**.
- **D12:** **the user's word.**
- **D13:** sub-assemblies by measured open only, **agree**. The referenced configuration, **disagree** (must-fix 4).
- **D14** (modes by name, the old first mode for a new mode): **agree** (note on renames).
- **D15** (old names kept): **agree**.
- **D16** (`unsaved` reused): **disagree** as written (should-fix 10).
- **D17**, **D18**, **D19**, **D21:** **agree**.
- **D20** (anchor order): **agree** on the order, **disagree** on per cluster (should-fix 2).

On §13: items 2–5 and 7 are right as stated. On item 1 see "the user's word". On item 6 see should-fix 1.

## The probe script

It runs W9a's harness through W9c's probes unchanged. Attach and the PID check, keep-awake, APPDATA in the run folder
and the guarded close come from `A.main`. Every call that may raise a dialog in `state` (g), (h) and `sub` goes through
`C.watched`, whose exemptions cover the open-progress box (`w9a_demonstration.py:2509-2510`). It logs only file names
under the run's folders (`doc_states`, `W.folder_flags`) and never SolidWorks' frame title. The out-parameters are as
W9c's measured calls had them: `GetObjectByPersistReference3(bytes, _out_long())` and `OpenDoc6` through `open_doc6`.
The members exist in the 2024 help: `GetCorrespondingEntity2` (2018 on, "Dispatch pointer to a vertex, face, or edge
entity in this … assembly"), `GetComponentSuppressionState(CompName) As Boolean`, `IsSame`, which returns
`swObjectEquality`, where `swObjectSame` is 1, `swObjectNotSame` 0 and `swObjectUnsupported` 2, and
`IEntity.GetComponent`. `GetComponentSuppressionState`'s example passes `IComponent2.Name`, as the note says. About 13
minutes on 2026 is credible from S5's 86 s and m1's 318 s.

**P1 (must). `faces` (b) and (c) bracket reads on a copy already marked.** (a) makes four mates in the copy and saves
nothing, so `RangeBox.SLDASM` reads modified when (b) begins. `flags_changed` sees only a turn from False to True. The
assembly-side reads (`GetCorrespondingEntity2` and `GetPersistReference3` on the assembly's extension) are therefore
judged "marked nothing" whatever they do. *Fix:* at the end of `faces_make`, `Save3(1, …)` the probe's own copy, as
`state_prepare` does and W9c's s5 (e) did on both versions. Check its flag reads False. In `persist_proposal`, propose
None when any document of the bracket read True before it. The same save makes (c)'s
`CARRY_INSERT_MARKS_USER_DOCUMENTS` readable (P11).

**P2 (must). (g) and (h) judge the read-only open, the shows and the close beside one part that is already modified.**
`Sprocket.SLDPRT` gets a global and reads True before the open. A mark by the open, by `ShowConfiguration2` in the
read-only document or by `QuitDoc` cannot show on it. Those three are exactly what `OPEN_READ_ONLY_KEEPS_OPEN_DOCUMENTS`
and `_SHOWN_CLOSES_CLEAN` license for the user's documents. *Fix:* also open `Housing.SLDPRT` from the copy, unchanged.
Require its flag False before, and still False and not read-only after (g)'s open, after the shows and after (h)'s
close. Optionally, read back the sprocket's added global, so "kept its change" is read, not inferred from the flag.

**P3 (should).** `read_only_close_verdict` checks only the assembly and the documents open before. Add: every other
document under the folder that the read-only open loaded is gone after `QuitDoc`. D1 and should-fix 8 rest on it.

**P4 (should).** `state_candidates` passes a candidate whose bracket started with the copy already marked. `job` opens
and activates the copy again before (b). *Fix:* keep `before`, and propose a candidate only if `RangeBox.SLDASM` read
False at its start.

**P5 (should).** `out.setdefault("first_marking", first_marking(steps))` keeps the first mode's answer even when it is
None. A mark first made while reading the second mode is then lost. Set it only while it is None.

**P6 (should).** (e) proposes `COMPONENT_STATE_PER_CONFIGURATION_READS_UNSAVED` whatever (b–d) found. If candidate 1
reads wrong anyway, (e) proposes False with a meaning it does not have. Propose only when (b–d) chose candidate 1.

**P7 (should).** `ROOT_COMPONENT_UNRESOLVED_READ`: see should-fix 12. Keep the read as a fact. Propose nothing that
gates.

**P8 (should, advised before the run).** `sub_make_host` opens the sub-assembly (whose open may mark it; that is (a)'s
question) and then `Save3`s the host. `Save3` on an assembly with a modified component is the case of GOTCHAS §100's
"Save Modified Documents". It runs under `run`, not `watched`. *Fix:* order it as `p2_make_sub` does: `open_document`
the sub-assembly, `new_assembly`, `add_component`, then `save_as(host)`. That is the app's measured `SaveAs3`, option 1,
and it saves no referenced document. Drop the `Save3`.

**P9 (should).** The `sub` parts do not catch `C.CaseStop`, so a dialog that comes and goes is a FAIL with no STOP
line and no proposal. `W9D-PROBES.md` says otherwise ("ends that case with a STOP line and its finding proposed
accordingly"). Catch it as `state` (g) does, and propose `SUBASSEMBLY_OPEN_MARKS`, `_WHEN_LOADED` and
`SUBASSEMBLY_READ_ONLY_INSERT` as unmeasured (None) with the dialog said.

**P10 (should).** `remake_part` takes one route for every entity: the face route, else the edge route. If faces come
back clean by r1 and the edge only by r2, `UserEdgeConc` fails with "no r1 reference". Pick the route per entity kind.

**P11 (should).** `CARRY_INSERT_MARKS_USER_DOCUMENTS` is proposed False when a user part was already marked before the
inserts. Return None then, as `sub_marks` does. P1's save makes this rare.

**P12 (should).**
- *A reload.* After (b), close the copy, open `Sprocket.SLDPRT` alone, and resolve each face and edge hex (kind, area
  against (b)'s). That is the not-open path's resolve (should-fix 9).
- *The referenced configuration.* Read `ReferencedConfiguration` of each user component in (b), bracketed (must-fix
  4).
- *Another version's file.* Only if the coordinator wants the not-open path for a file saved on another version: open
  the other version's RangeBox master read-only under the watch and `QuitDoc` it (must-fix 2). Expect the CAM box on
  2026. It ends the session, so run it last.

**P13 (note).** `MATE_REMAKE_ON_FACES_AND_EDGES_ROUTE` is proposed but not read by the contract (should-fix 11).

*Not probed, and need not be under the rule:* the definition read of a mate whose component is suppressed in the mode
showing. It is a read, so M9 should hold one (should-fix 15). *Probed, and could go:* candidate 3 taken apart only
names which call marks, which is already known to mark. It is cheap and it was the W9c review's ask, so keep it.

**May the probes run as they stand once P1 and P2 are in?** Yes, on 2026 first, with P8 in the same edit. The rest
make the proposals sharper, but none gives a wrong answer that a reviewer reading the log would miss: each FAIL or
None shows. Nothing in the script saves a file outside the run's folders, closes a document it did not open, or logs a
title but its own.
