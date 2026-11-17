# Review of W9c: packages A (the worker) and B (planning, sentences, footer)

*Independent, 2026-11-17, at `61766a9`. I started no SolidWorks or Excel and changed no source, test or document.*

- *The suite, run once:* 1 failed (the known Tk font-width test), 3725 passed, 1 skipped, 1 xfailed. That is B's
  count.
- *Scratch tests:* a handful, in the scratchpad, built on B's round-trip desk (`tests/test_workbook_in_place_round_trip.py`'s
  `Desk` on the suite's fake). They are deleted.
- *What I read:*
  - `W9C-INTERFACES.md` whole, §10's rulings and §11's rounds included;
  - the plan's §2.1 (W9c), §2.4 (*In place*), §4 (M4, M5, M6, M8, M10), §5 (W9c), K6 and §0.3;
  - the diff `0df56da..61766a9` over `src`, `tests`, `design` and the interface note;
  - the code around it: `swbuild._update_motion`'s check phase, `_user_check`, `_in_place_assembly`,
    `_in_place_bands`, `judge_user_work`, `update.user_work_ahead`, `in_place_ahead`, `bodies_put` and
    `record_user_work`;
  - the fake's new members;
  - `W9C-DEMONSTRATION.md`, skimmed.
- *What I wrote:* this file only.

**Verdict.**

- **The worker is sound where it matters most.** Everything it will do to the user's work is judged before the first
  write:
  - F2's fix makes every train put with modes count as judged;
  - an added mode is judged as the mode it copies;
  - without modes, the trains after an insert are judged.

  I found no path that writes and then refuses, beyond W9a's own safety net (`_bind`). Every gate refuses by name
  before any write. The two splits cover exactly what their names say, and a removal is judged by reads, not by
  `EditDelete`'s return.
- **Two must-fix points, both in what the user is told and what the record remembers, not in what SolidWorks is
  made to do:**
  1. The footer foresees a false refusal, with a broken sentence, for the ordinary mode removal on a gearbox with the
     user's lock.
  2. The app's own leftovers from a stopped press are forgotten after any later press that runs to its end. They are
     then refused as the user's, or said to be the user's.
- **Neither should stop the demonstration's next run on SolidWorks.** Nothing is written wrongly. But point 1 will
  show in its `modes` section's footer, so judge that footer there knowing this.
- **Schema:** I recommend schema 9 now (§ *The record*).

---

## Must fix

**1. A Modes row removed on a gearbox where the user's lock is on in every mode: the footer foresees a refusal the
press does not make, in a broken sentence.**

- *What the code does.*
  - `update.user_work_ahead` (`workbook/update.py:2759-2768`) hands `swbuild.judge_user_work` the **recorded**
    inventory, whose mates' `on` still lists the mode being removed. It passes the configurations **after** the
    Update as `modes`.
  - `judge_user_work` then sees a lock whose `set(on)` is not `every` (`swbuild.py`, the `PROBLEM_LOCK_BY_MODE`
    branch, `if set(mate.on) != every and reaches_put(mate)`). It refuses with an empty list in the sentence.
  - The worker reads the user's flags only over the configurations after the Update, so it never sees the removed
    mode. It goes ahead.
- *Reproduced* on B's own desk: `fixed_desk_with_work` (RangeBox_Fixed with the user's Lock3 on in H, N and L),
  then `_fixed_without_mode()`.
  - **The footer:** red, *"Update SolidWorks will delete the mode N. … As read at 08:05, the next press would stop
    before changing anything: Your lock Lock3 is on in H and L and suppressed in , and putting a component of yours
    with its gear has been settled only for a lock that is on in every mode, …"*
  - **The press:** ok, *"Updated SolidWorks: deleted the mode N, … Your Sprocket-1 went with Sun in every mode, which
    your locks hold it to."*
  - This is the plan's M10 case on the demonstration's own setup (`modes`, step 3).
- *Why the test missed it.* `test_a_mode_removed_on_the_result_is_one_update_and_a_second_press_quiet[True]` asserts
  nothing of `press.before`.
- *Fix.*
  - Before judging, take `in_place.modes_removed` out of each recorded mate's `on`. This is the mirror of
    `work_in_added_modes`: a pure `swbuild.work_without_modes`, used by the footer (the worker needs nothing).
  - Assert the footer in both parametrisations.
  - Make `PROBLEM_LOCK_BY_MODE`'s sentence impossible with an empty side: it should not arise, but `_and([])`
    should never reach a sentence.

**2. The app's leftovers from a stopped press are forgotten once any later press runs to its end. They are then
refused as the user's, or said to be the user's, and only the user's hand clears them.**

- *What the code does.* `GearboxRecord.left` is set to `[]` "once a press runs to its end" (B, §11 second round),
  whether or not that press used what was left. The worker's F1 rule (`_globals_plan`, `swbuild.py:5954-5975`)
  takes a global at another value as the app's only when `left` names it. Anything else is the user's.
- *Reproduced, globals.* RangeBox → RangeBox_Fixed with `add_component` made to fail. The press built Hub's part,
  gave the bands and added `Hub Face Z` = 55.5, so `left` is `[…, "Hub Face Z"]`.
  - The user then sets the workbook back to RangeBox. The press goes through (the relief suppressed), and `left`
    becomes `[]`. `Hub Face Z` stays in the assembly, and Hub's `PartEntry` (`gears ["Hub"]`) stays on record with
    no component.
  - Later the user adds Hub again, 21 mm wide. The footer is green: *"Update SolidWorks will add Hub on Output
    (Hub_m1.25_N17) …"*.
  - The press refuses: *'RangeBox.SLDASM already holds a global "Hub Face Z" = 55.5 that Gear Generator did not
    add, … rename or delete "Hub Face Z" in SolidWorks …'*.
  - The sentence is false: the app added it. The footer promised the opposite. The user must repair by hand.
- *Reproduced, configurations.* A press that stopped after adding R leaves R in SolidWorks, and `left == ["R"]`.
  - The user takes R off the Modes sheet. Every later result then says *"RangeBox.SLDASM also has a configuration
    the app did not make (R); Update SolidWorks left it as it is."* That is false: the record's own `left` says the
    app made it.
- *Fix.*
  - Keep each name in `left` until a press consumes it, that is, uses it or takes it away. Do not clear it because
    a press ended.
  - Say leftovers no longer needed in the result, as the app's: *"… still holds Hub Face Z and the configuration R,
    which an Update that stopped added; Update SolidWorks leaves them; delete them in SolidWorks if you no longer
    want them."*
  - Drop or keep a new part's `PartEntry` whose gear has left the workbook, and say which.
  - Test the abandon-then-re-add path, for a global and for a configuration.

---

## Should fix

**1. On a record with no user-work inventory (any gearbox not Updated since its Build), the footer foresees every
gated step refused, even once the findings are set.**

- `in_place_ahead` passes the inventory's revision, or `()` with none (`update.py:2795-2799`).
- `in_place_gates` with no year marks every gate unsettled (`swbuild.py:5781-5784`).
- *Reproduced* on the transfer case just built, with the gates patched True: the footer is red, *"The next press
  would stop … has not yet been shown to do on the SolidWorks it runs on …"*, and the press went ahead. In my case it
  stopped later, only on a failure I injected.
- After the full build sets the findings, this is the footer of the first in-place edit after every Build.
- *Fix.* Record the SolidWorks revision a Build ran on (the build knows it) and use it when no inventory is on
  record. Or word the line as conditional on a version not yet known.

**2. "Will … would stop" in one footer.** B removed it for the gates (94a949a), but W9a's user-work foresight still
pairs *"Update SolidWorks will …"* with *"the next press would stop before changing anything"*. Must-fix 1's footer
is an instance, and so is the probe's m1 footer. One rule for both: "would" whenever the press is foreseen refused.

**3. The mode-showing refusal's record.**

- `record_user_work` (`update.py:2633-2641`) overwrites the kept inventory's `read_at` with the refusal's time. The
  footer then says *"As read at hh:mm"* for a time nothing was read.
- With no inventory on record, it stores an **empty** one. Later foresight takes that as "the user has no
  components": `judge_in_place(work=empty)` foresees no `PROBLEM_REFERENCES` (C4) for a removal. The press then
  refuses on the components it reads.
- *Fix.* Keep `read_at`, and keep the refusal's time beside it. Mark an inventory created by such a refusal as
  unread, so the foresight treats it as none.

**4. The footer and the press copy different modes for an added mode.**

- The footer judges an added mode as a copy of the record's first mode (`_copied_mode`, `update.py:2774-2778`). The
  worker copies the mode **showing** at the press (`_user_check`, `swbuild.py:6716-6718`).
- With the user showing L and their lock suppressed there, the footer and the press can disagree.
- *Fix.* Say it in the footer (*"the new mode starts as a copy of the mode showing when you press"*), or foresee
  from every mode the user could show.

**5. `root_component` is now on every Update, and it resolves.**

- `Session.root_component` calls `GetActiveConfiguration().GetRootComponent3(True)` (`swcom.py:2607`).
  `_read_user_work` calls it on every press (`swbuild.py:6461`), W9a's path included.
- *Resolve = True* was measured marking nothing only on an assembly whose components were all resolved (s5 (a), both
  versions).
- The same call, per configuration, **marked the assembly** in s5 (e). The likeliest cause is the resolve.
- W9a's demonstration met a user whose assemblies load lightweight. On such an assembly the read could resolve the
  user's components and mark the document: §0.3's STOP class, on every Update, not only W9c's.
- *Fix.* Call it lazily, only when `owner` meets a name no top-level component has, so it runs only for a mate on
  the assembly's planes. Add a lightweight user component to the demonstration, with the save flag and the
  components' states read around the press.

**6. Failures half way, untested.**

- B's round trip pins failures at `add_component`, `add_mate`, `set_mate_suppressed_in` and `add_configuration`.
  A's tests pin a band part failing.
- Untested: a failure at `delete_configuration`, `delete_component`, `suppress_feature`, the remake
  (`set_gear_ratio`) and the post-check after in-place steps.
- I ran one, a mode and a gear removed in one press with `delete_component` failing. The result says *"Before it
  stopped it deleted the mode N. It did not get to taking FIdler out …"*. The record's modes lose N and keep FIdler,
  and the next press takes FIdler out and nothing more. That is right; pin it, and the others.

**7. The demonstration note is stale after the split (`957b7c0`).**

- `W9C-DEMONSTRATION.md`'s gate table and *What the packages could not be driven to* still say:
  - `UPDATE_MAKES_MATES_WITH_MODES` "covers both writes";
  - `UPDATE_BANDS_IN_PLACE` gates both directions.
- The script (`b987d7a`, before the split) patches only the old names. Since no legal edit of its fixtures reaches
  a `NewMate` or a bands-off Update, that is harmless. But its proposals must not be read as evidence for
  `UPDATE_MAKES_A_NEW_COUPLING` or `UPDATE_SUPPRESSES_THE_RELIEF`, which stay None.

**8. The fake is kinder than SolidWorks in three places.**

- `delete_component` raises no epoch (the Session does), so the refetch after a delete is not exercised.
- `root_component` never resolves or marks (should-fix 5).
- `delete_configuration` does not mark the assembly.

None of these hides a fault I found, but each is where the demonstration must look.

## Notes

- **N1 — the leaf mapping after `7e0d095`.** It refuses nothing wrongly in any case I could build. Each one I tried:
  - a leaf of a sub-assembly maps to its top level;
  - the root maps to the assembly;
  - any other unknown name is not wholly read. That refuses only when something is put, as W9a refuses an unread
    mate.

  If the root read fails, a mate on the assembly's planes becomes unread and refuses any put. That is conservative
  and acceptable.
- **N2 — `(Hub_m1.25_N17)` for a part already on record** (after a stopped press) is true. *"its part
  Hub_m1.25_N17, already built"* would say why there is no "a new part".
- **N3 — a leftover configuration copies an older mode.** It was copied from the mode showing when the stopped press
  ran. The press that goes on from it judges it as a copy of the mode showing now (`work_in_added_modes`). If the
  user changed flags there in between, the judgement is of a state that is not there. It is rare, and it ends with
  the post-check.
- **N4 — the record equals a fresh build's.** B's claim holds on the fake
  (`test_the_record_differs_from_a_fresh_builds_only_where_the_plan_says`): `gearbox.updated`, `gearbox.user_work`,
  `last_updated` and `unsaved`. It cannot speak for `Name2`s on SolidWorks.
- **N5 — the remake gate's `BuildError`** (A's pending change) is the one gate not recorded as a refusal. B's xfail
  is right to want it a `UserWorkRefused`.

## The record (schema)

- *What changed.* `GearboxRecord.left` and `UserProblemEntry.subjects` are additive at schema 8. An older reader
  (`store._known`) drops both silently on read, and on write-back.
- `subjects` is harmless: the sentence carries the meaning.
- `left` is not harmless. It decides whether a global or configuration in SolidWorks is the app's or the user's
  (must-fix 2). A W9b-era app that Updates a W9c record after a stopped press writes it back without `left`. The next
  W9c press then refuses the app's own leftover as the user's, or, at the value wanted, quietly takes it as done.
- A stopped W9c press also leaves something a W9b app cannot have met: a `PartEntry` whose gear has no component.
- **Recommendation: schema 9 for W9c, and 10 for W9d.**
  - That is the house rule W9a (7) and W9b (8) followed: an older app that would act wrongly on a record must refuse
    it.
  - The plan's "9 for W9d" is a label, and W9d has no code yet.
  - If the coordinator keeps 8, must-fix 2's fix should not rest on `left` alone. For example, count a global named
    `"<gear> Face Z"` for a gear the record holds as a `PartEntry` with no component as the app's.

---

## What I checked and found sound

- **Before the first write, every in-place kind:**

  | Kind | What is judged before the first write |
  |---|---|
  | A gear added | Its faults (`_in_place_faults`); a new part already on disk; its gate; with modes every mated body judged put; without, the trains after the insert (`after`) |
  | Hub as anchor | Its spline in `AddedGear.ops`, under `UPDATE_INSERTS_A_GEAR` by ruling, judged as above |
  | A gear removed | C4, `PROBLEM_REMOVED` and unread mates, from the live read |
  | A new coupling | Its own gate |
  | A remake with modes | Its gate (as `BuildError`, N5) |
  | Bands given | Their gate; F1's globals and an existing relief, in the check |
  | Bands back | A missing relief refused in the check |
  | Bands taken away | `UPDATE_SUPPRESSES_THE_RELIEF` |
  | A mode added | Judged as its copy; a name taken refused |
  | A mode removed | The mode showing refused before anything is read; the user's flags there read unshown and said (C5) |

  Combinations work too. A mode added and a gear added in one press: the modes come first, then the insert, then
  every flag set over the final configurations. My scratch press of a mode and a gear removed together behaved as
  the order says.
- **No write, then a refusal.** `_bind`'s safety net stays. With modes, `changing` is True for any `InPlace`, so
  every put is judged. No path I traced reaches a gated write around its gate:
  - an added gear's own mates sit under its insert gate by ruling;
  - a `NewMate` sits under its own gate;
  - bands back sit under the relief gate, with their globals set or added in the sleeve's own part;
  - a configuration in `left` is still under `UPDATE_ADDS_A_MODE`;
  - remakes without modes stay W5's, which was measured.
- **The calls (§9).** No call is new and unmeasured beyond `delete_component` (P1's route, gated by its finding in
  the Session itself) and `suppress_feature` (the member used on mates, now on a part feature, gated). There is also
  `root_component`, measured as a read (should-fix 5).
  - `delete_component` judges by the components read after.
  - The worker then requires each `RemovedGear.mates` gone and every other app mate present
    (`swbuild.py:6210-6228`). It never trusts `EditDelete`'s return, as the probes' review asked.
- **Findings.** `c8da5bb` and `6ca42da` set what the probes' review marked, at the scopes it gave. The narrower names
  are `…_IN_EVERY_CONFIGURATION`, `…_FOR_REFERENCE_FEATURES`, `…_ON_AXES_PLANES_AND_LOCKS_…` and
  `…_WHEN_NOT_OPEN`. `COMPONENT_STATE_PER_CONFIGURATION_ROUTE` is None on both versions, and the six W9c gates (eight
  after the split) are None.
- **Classification.**
  - Every row of §3's table is moved, and nothing else.
  - "Still Build again… after W9c" stays structural, each with its own sentence. The tests cover: a new shaft, an
    anchor removed, a mode renamed (or one removed and another added), a coupling on in no mode, and a gear added
    before its anchor.
  - A mixed edit writes nothing.
  - The Done-when edit is one Update, and its record matches a fresh build's but for the four things B names.
  - W9a's and W9b's records and pins pass unchanged in the suite.
- **The result after a failure.** `skipped` names only what was not done (F3). The active mode is shown again. A mate
  made before its flags were set is listed. B's record of a stopped press holds what was done: parts built, the
  component inserted, mates made with their on-sets. The next press goes on from it, as B's round trip shows for
  each failure it injects; must-fix 2 is the exception.
- **The tests can fail.** The xfail is strict, and each gate's refusal asserts no write.

## What the demonstration on SolidWorks must show that the fake cannot

Beyond the interface note's per-gate list:

1. **The footer before each press, asserted.** It must be green where the press goes through: the N removal with
   the user's locks (must-fix 1), and the first Update after a build (should-fix 1). That needs at least a log line
   per press comparing `before` with the outcome.
2. **`root_component` on an assembly with a lightweight user component,** with the save flag and every user
   component's state read around the press (should-fix 5).
3. **After `delete_component`,** every held handle refetched and every mode shown with the deleted component absent
   and its mates gone, read per mode. The worker reads the active mode only and relies on the finding for the rest.
4. **Hub's `Name2`** as SolidWorks keeps it, against `inserted` and the record. The fake names it `gear7-1`.
5. **The relief made after the user's groove,** with K3 reading the groove as the user's and the relief as the app's
   (C2), and the groove's cut faces unchanged. The note already plans this; keep it as a STOP, not a fact.
6. **Each step's GetSaveFlag on the user's own documents,** not only the app's. The note's `users_unchanged` covers
   this if it reads the flag.
