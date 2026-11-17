# Review of W9d package B: the question, the result's sentences, the record and the window

*Independent, 2026-11-17. I started no SolidWorks or Excel and changed no source, test or document; this file is the
only one I wrote.* Under review: package B's seven commits on `w9d` — `22c33dc` (schema 10), `6f2b33c` (`carry_for`,
`recorded_old_work`), `3e08560` (the question and the result's sentences), `220d4a2` (the finish, the footer, the lost
line), `e3cb8e6` (the window), `e2ab119` (the round trip, the marks sentence, UI-DESIGN §9) and `6f9c8cb` (the
pattern-instance sentence, the hand-back note). Line numbers are `6f9c8cb`'s; package A's later commits (`24aea8c`,
and the probe review `94fbebf`) touch none of B's files.

I read `W9D-INTERFACES.md` whole, its review, ISSUE-1-PLAN §0.2 K5, §2.1 item 8, §2.5 and §5 W9d, both packages'
hand-back notes, `W9D-PROBES.md` and the probe review's points that bear on B's words, the W9a and W9c sentences in
`ui_text.py`, UI-DESIGN §9 and the handoff's standing rules. Every sentence quoted below is real output. I made it
from scratchpad scripts on the repo's own fake: package A's worker end to end on Desk's RangeBox with W9a's user work,
in four states (every W9d finding None, which is today; the carrying gates patched; those plus the fake's entity kinds;
those plus every finding the 2026 probes proposed). For what the fake cannot make (the §15 fixture's clusters, a tie, a
stop, the not-open refusals, a mark, a document left open) I used hand-made `OldWork`s and `CarryResult`s, and A's own
`stopped` and `unread` texts.

**Suite.** Linux venv, at the tree's head `94fbebf`: **2 failed, 3824 passed, 10 skipped**. The two failures are the
known tkinter ones (`test_gears_clutch::test_the_strip_never_offers_them`, `test_ui_text::…end_view_readout…`).

On Windows (`python.exe` 3.13, pytest 9.1.1), I ran `tests/test_workbook_build.py`, `test_workbook_window.py` and
`test_workbook_carry.py` from a `git archive` of the head on `C:`, then deleted the copy. Result: **246 passed,
1 skipped, 4 deselected.** B reported 250, and the difference is the four I deselected. They are the K12 tests that
map a window on screen (`_shown`). The standing rule is not to put a window in front of the user unasked, and none of
the four touches W9d.

---

## Verdict

**The record, `carry_for` and the window are sound; the result's sentences are not yet.**

Sound:
- Schema 10 reads and writes exactly. The real W9c store (from `5e783a6`) refuses it with its sentence and leaves the
  file byte-identical.
- `unsaved_at` follows the file's own clock, and the lost line is said once.
- The window's two hooks follow the existing jobs' threading.
- The question is honest about what it cannot know, apart from one contradiction (M5).

Not yet: five points must be fixed before the demonstration is written. Three of them make today's real state, every
W9d finding None, worse than W9a:
- **M1.** With nothing carried, the result drops W9a's sentence: what stays in the old assembly, and the Keyway.
- **M2.** Even when things are carried, the result never says the feature left in a part made new. §9.2's own example
  says it.
- **M3.** An old assembly that was not read gets advice the app will not honour: *open it … before you press Build
  again… to carry it*. After this build the record's assembly is the new revision, and D11 rules out carrying again.
- **M4.** A carry that stopped before anything was made says *what was carried before it is in RangeBox_r2, unsaved*.
- **M5.** For a lightweight component, the question says one mate both "is not made again" and "is not made again
  unless you set it resolved".

Each fix is local to `ui_text.carried_status`, `carry_sentence` and the window's call. With them in, package B is fit
for the demonstration.

---

## Must-fix before the demonstration is written

### M1. With every W9d finding None (today), the result is worse than W9a's

`workbook_gui.py:1561-1565` says `carried_status` whenever `result.carry` is set. Package A sets it on every Build
again… the window gives a `Carry`, and the window gives one on every Build again… So with `CARRY_INSERTS` None on
both versions, the user no longer sees W9a's sentence.

Here is RangeBox with W9a's work, built on the fake with every finding None. After the build's own sentence, the result
says:

> *Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026
> (findings.CARRY_INSERTS_ON_2026), so Sprocket-1 and Housing-1 are not carried. Lock3 joins Sprocket-1, which is not
> carried.*

From the same result, W9a's `stayed_behind_status` says:

> *Your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, as read when this build began; RangeBox_r2 has none of
> them. As read at 14:29, your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of
> it, nor anything added since.*

Three things are lost:
- that they stay in RangeBox.SLDASM;
- the Keyway;
- the plain verdict on Lock3, which is told only that the component it joins is not carried.

On the §15 work, every mate gets a sentence of its own, ten times *Lock1 joins Sprocket-1, which is not carried.*

The question in the same state is right: W9a's clause, led by the finding. So the question and the result disagree on
what stays.

**Fix.** In `carried_status` (`ui_text.py:5442`), when nothing was inserted or remade and the work was read: say the
grouped gate sentence as the lead, then W9a's `stayed_behind_status(stays, result, again, old_path)`. Package A
already fills `old_user_work` and `old_read` for it. `_finish_build` passes `wb_update.stays_behind(job.record,
job.plan)`, as it does today. The result then reads: *Gear Generator has not yet been shown … (findings.CARRY_INSERTS_
ON_2026), so your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, as read when this build began; …*

Owed test: the window's (or the round trip's) result with every finding None ends with W9a's sentence, led.

### M2. The result never names a feature left in a part made new

§9.2's example includes *"Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed
(RangeBox.SLDASM and that file keep it)."* Today's W9a result says the Keyway too. `carried_status` has no feature
clause at all.

The full carrying result on the fake (gates patched, every 2026 probe finding set) names Sprocket-1, Housing-1 and
Lock3, and never says that the Keyway the question promised would stay did stay.

**Fix.** Pass the `StaysBehind` (and the carry's `why_new`, from `job.carry.bodies`) to `carried_status`, and reuse
`_parts_left` and `_reuse_advice` as `carry_sentence` does. The advice reads as past here: *answer No* has no place
after the press, so keep only the stays clause.

### M3. An old assembly not read: false advice, and W9a's sentence lost

`ui_text.py:5463-5466`. Here is the real case today: the old assembly closed, every finding None, A's `unread` text.

> *RangeBox.SLDASM was not read (RangeBox.SLDASM is not open in SolidWorks, and Gear Generator reads it then only when
> its close has been shown clean (findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026)), so nothing of yours was
> carried; it and your files are as they were. Open RangeBox.SLDASM in SolidWorks before you press Build again… to
> carry it.*

Three problems:
- **The last sentence promises what the app will not do.** After this build, `record.gearbox.assembly` is
  RangeBox_r2, so the next Build again… reads RangeBox_r2, not RangeBox.SLDASM. D11 rules that nothing offers to
  carry again.
- **W9a's sentence for this very case is gone.** It said *"RangeBox.SLDASM was not open in SolidWorks, so it was not
  read again; as read at 14:31, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, and your Keyway stays
  in Gear_m1.25_N29, …"*.
- **The parentheses nest, and the file name is said twice.**

The same holds once the gates are patched: a closed old assembly is unread until `FILE_VERSION_READ` and its siblings
are set.

**Fix.** Drop the *Open … to carry it* sentence. Say A's reason as the clause it is: *RangeBox.SLDASM is not open in
SolidWorks, and Gear Generator reads it then only when …, so nothing of yours was carried.* Follow it with
`stayed_behind_status`, which takes the `OLD_NOT_OPEN` path A sets: *as read at 14:02, your … stay in
RangeBox.SLDASM …*.

### M4. A stop that made nothing says something was carried, and A's sentence is wrapped twice

`ui_text.py:5538-5541`. The stop clause always says *what was carried before it is in RangeBox_r2, unsaved*.

A stop before anything was inserted reads:

> *Carrying your work stopped: SolidWorks would not read RangeBox_r2's frames (Sun not found), so it did not get to
> inserting your components; what was carried before it is in RangeBox_r2, unsaved, and RangeBox_r2 as built is
> saved.*

Nothing was carried, and `unsaved` is False, so the footer rightly says nothing. The two disagree.

A's own `stopped` texts are whole sentences, and some say *stopped* themselves, so the wrap doubles them:
- *"Carrying your work stopped: After the fallback, Sun still reads unable to turn in L, so the carry stopped, so it
  did not get to making Sprocket-9's mates again; …"*
- *"Carrying your work stopped: SolidWorks stopped the carry while reading the new revision: …"*

A's file-changed check runs after the carry has finished, and it is said as a stop:

> *Carrying your work stopped: Sprocket.SLDPRT changed on disk while Build again… carried your work, which Gear
> Generator never does; look at it in SolidWorks; what was carried before it is in RangeBox_r2, unsaved, …*

**Fix.**
- Say *what was carried before it is in …, unsaved* only when `done.unsaved`. Otherwise say *nothing of yours was
  carried; RangeBox_r2 as built is saved*.
- Agree with A, through the coordinator, on `stopped`'s grammar. Simplest: B says A's sentence as it stands, then B's
  tail (*It did not get to …*). Do not lead it with *Carrying your work stopped:*.
- Ask A to give the file-changed fact its own field, or a prefix, so it is not said as a stop.

### M5. The question contradicts itself for a lightweight component

`ui_text.py:5337` and `_component_states` (`:5400`). With Sprocket-1 lightweight as read:

> *Lock3 is on Sprocket-1, which was lightweight in RangeBox.SLDASM, so what it joins could not be read, and it is not
> made again. Sprocket-1 was lightweight as read, so its mate cannot be read through it: set it resolved in SolidWorks
> before you press, or it is not made again.*

The first sentence is plan_carry's `WHY_LIGHTWEIGHT`, said as if final. The second is B's advice, which says the
opposite is still in the user's hands. This is the W9c lesson of today: two sentences that cannot both be acted on.

The probe review adds a reason this will be met: setting one instance lightweight reads every instance of the file
lightweight (`W9D-PROBES-REVIEW.md`, the facts' (f)).

**Fix.** In `carry_sentence`, leave out of `_named_sentences` every `WHY_LIGHTWEIGHT` item whose component
`_component_states` speaks for. Its sentence already names the mates' fate, as a condition.

---

## Should-fix

**S1. A mate whose reason ends "which is not carried" is never told it is not made again, and each is its own
sentence.** `_VERDICTS` (`ui_text.py:5152`) matches *not carried* whatever the item is.
- So *"Lock6 joins Bracket-1, which is not carried."* and *"Coincident9 is on Plane1, a feature you made in
  RangeBox.SLDASM, which is not carried."* end there.
- Fix: match the verdict per `what` (a mate's clause needs *made again* / *make again* / *taken out again*).
- Group `WHY_NOT_CARRIED` by component: *Lock1 and Lock8 join Sprocket-1, which is not carried, so they are not made
  again.*

**S2. The question says the new revision "holds what it carries unsaved: save it" when it foresees carrying nothing.**
`:5360`. With only features on record:

> *As read at 14:33, nothing of yours in RangeBox.SLDASM would be carried into RangeBox_r2. … RangeBox_r2 is saved as
> built, and holds what it carries unsaved: save it in SolidWorks to keep them.*

Fix: say the save sentence (and the not-open clause, which is moot then) only when the plan has components or mates,
or when there is no plan.

**S3. Length.** The whole carrying question is 2,096 characters (326 words) in a yes/no dialog; W9a's was about 145
words. Of the carry's ~180 words:
- the not-open clause is ~75, naming three findings;
- the states clause is 45;
- the standing list is 40.

The result after a carry is ~190 words on top of the build's own ~165.

Trims that lose nothing true:
- In the not-open clause, name only the first finding unset.
- Drop *(a file saved since on another SolidWorks is not read)*. It repeats *last saved by this SolidWorks*, and "is
  not read" is wrong: the file's version is read closed, and only the open is refused.
- Merge *RangeBox_r2 is saved as built …* with *The press reads … again first …*.
- Group the per-mate sentences (S1).

**S4. `carry_anchors` can disagree with what the worker did.**
- `gearbox.carry_anchors` (`gearbox.py:1519`) runs `plan_carry` without `new_frames`.
- With `new_frames`, plan_carry passes over an anchor whose old or new frame is missing (`swbuild.py:7506-7512`,
  `framed`). Without them, it still names it.
- So when the worker placed a component in the world frame, the record's `CarriedComponentEntry.anchor` and the result's
  *against the gear it is mated to* can name a gear it was never placed against.

The re-derivation is not guaranteed to agree. Fix: shape request 1, below.

**S5. The result lacks §9.2's D14 sentence.**
- §9.2 asks for *"the D14 sentence of §9.1"*: a mode gone or renamed, and what a new mode took.
- `carried_status` never says it. The question does (*RangeBox_r2 has no mode L: … Its new mode Low takes what they
  were in H.*).
- Fix: say `_modes_said` in the result from `job.carry.modes` against `work.modes`.

**S6. The in-context sentence asserts what was never read.**
- *"A part of yours made in context of RangeBox.SLDASM still refers to its parts."* is said whenever a user part is
  carried. M4 (in-context references) is unmeasured, and nothing reads whether any part was made so.
- Fix: *"If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts."*
  This is also clearer than *its parts*.

**S7. A read that raised claims more than was checked.**

> *RangeBox.SLDASM was not read (SolidWorks stopped answering (RPC_E_CALL_FAILED)), so nothing of yours was carried; it
> and your files are as they were.*

When the read raises, the save flags are not read again, and the `finally` that closes a read-only open may itself
have failed.
- Say *"… are as they were on disk"*, as the marked case does.
- Say the reason as a clause, not in parentheses, since A's text carries its own.

**S8. Grammar, each a reproduced string.**
- The fallback's tail is plural for one deleted mate. Fix: *beside it* when one mate was deleted.
  > *Sprocket-8 is fixed where it stood in RangeBox_r2: with your Lock8 made again SolidWorks reads Sun unable to
  > turn, so it was not kept; Lock9 beside them was.*
- The grouped face and edge reason. Fix: *find a mate's face again* (`_unmeasured_verb`, `:5057`).
  > *Gear Generator has not yet been shown to find a face of a mate's again in a new revision …*
- The single `unmeasured` clause leaves *which* dangling. Fix: a colon, *"M1 is not made again: Gear Generator has
  not yet been shown to …"*.
  > *M1 is not made again, which Gear Generator has not yet been shown to make a gear mate on an app gear again …*
  > *Sprocket-1 is not carried, which Gear Generator has not yet been shown to carry your work into …*
- `moved` is said once per mode for the same component. Fix: group the modes. The anchor is in B's `anchors`, so say
  *off where it stood against Sun*.
  > *In N, SolidWorks moved Sprocket-2 30.0 mm … In L, SolidWorks moved Sprocket-2 30.0 mm …*

**S9. The round trip does not set `read_entity_kinds`.**
- A's note asks for it. `test_the_round_trip_…` (`test_workbook_carry.py:845`) leaves the fake's default (False).
- So the desk's inventory is a schema-9-shaped one (`entities` []), and the question takes the *lock means whole*
  path. The schema 10 entities never go through classify, the question and the finish together.
- In my runs, setting it changed none of the strings, but the path should be tested. Set it, or parametrize both.

**S10. "Bore" will be wrong once `COAXIAL_FACE_READ` is set.**
- The probe review (`94fbebf`) found Sun's 29 tip and 29 root cylinders read coaxial. A mate on a tooth tip would be
  said *"on Sun's bore"*.
- The contract is to change the `part new` slot (a radius). B's clause then needs its other wording, *"a face of Sun
  on its axis"*.
- Not reachable today (A never reads `coaxial`), but it will be by M9 if the finding is set.

---

## Notes

- **Existing behaviour.** B changed these existing tests, each as the contract requires:
  - `test_store` and `test_workbook_bands` pin schema 10, and the "newer schema" refusals move from 10 to 11
    (§7: W9d's is 10).
  - `test_workbook_user_record`'s question test and the window's `TIMELESS` now carry the `CARRY_INSERTS` lead
    (§9.1: *with `CARRY_INSERTS` not set, W9a's sentence follows, led by …*).
  - No other existing assertion moved.

  With every finding None, the **question** is W9a's plus an honest lead:

  > *Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026
  > (findings.CARRY_INSERTS_ON_2026), so as read at 14:29, your Sprocket-1, Housing-1 and Lock3 stay in
  > RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of
  > them, nor anything added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.*

  The **result** is not W9a's (M1). The footer afterwards is W9a's: no inventory, no line.
- **The record.**
  - Every field round-trips. My scratch round trip set the fields the test leaves at defaults (`stopped`,
    `states_read`, `code_before`/`code_after` 46), and all of them read back exactly.
  - Nested readers refuse a wrongly typed field by name (`CarriedComponentEntry.fixed`, `CarryEntry.revision`). They
    drop unknown keys, so a `path` someone added is never written back. A `None` list reads as empty.
  - A schema 9 inventory reads with `entities` [], and the question words its mates as *may*.
  - `UserMateEntry.entities` is written only from `swcom.entity_kind`'s closed list and W9a's `what`, so the reader's
    strict check cannot refuse a record the app wrote.
- **`unsaved_at`, scenario by scenario.**
  - It is the new assembly's own file time, compared with the same file's later time, so a clock behind affects
    nothing.
  - Saved in SolidWorks, on either version: the file is newer, and the mark goes silently.
  - Closed without saving, then a later Update: that Update finds it loaded from its file and not newer, and says the
    lost line once (`update._follow_carry`).
  - Closed without saving and nothing pressed: the footer goes on asking for the save, which it cannot know is moot.
    W9c's Update line has the same limit.
  - Update never saves the assembly (`update_gearbox`'s docstring: "Saves nothing and closes nothing"), so a lost carry cannot be hidden by an Update's own
    save.
  - A later Build again… from r2 is not told the carry was lost. The question's foresight is built from the carried
    inventory, with *as read at* the carry's time. Acceptable, since the press reads r2 live, but worth one line in
    UI-DESIGN.
- **Nothing personal is written by B's own code.**
  - Components keep Name2, kind and configuration, never a path.
  - Two reasons keep a user's file *name*, without its folder, in `CarryNamedEntry.subjects` and `sentence`
    (`WHY_NO_FILE`, `WHY_NOT_FOUND`, worded by A with `_file`).
  - A's `stopped` can carry an exception's text, which may hold a path (`_said(exc)`).
  - W9a's ruling was about paths, so this is the coordinator's call. If it should hold strictly, strip `stopped` of
    anything after *SolidWorks:* when it is recorded.
- **The foresight against the worker.**
  - `recorded_old_work` stands each file in by its Name2 and takes it as on disk and of one configuration. The question
    hedges the configuration (*carried only if each one's file has a single configuration … the press reads which*,
    while either finding is unset).
  - It cannot foresee a file not on disk. *Takes your …* stays definite there, carried by the closing *the press reads
    … again first, and says whatever it cannot carry*.
  - The states clause keys on the route finding alone. An open old assembly with unsaved changes and `…_READS_UNSAVED`
    None gets the mode showing's states unsaid. On 2026 both findings are proposed together, so this is moot there.
- **The window.**
  - `carry_for` and `carry_anchors` run on Tk as `old_assembly` and `finish_build` already do: pure, apart from
    sidecar reads and one `mtime`.
  - `job.carry` is set before the worker starts and read after it ends; `job.revision` is set in the worker as before.
  - The footer's line sits inside K12's scrolled ceiling, so it is always whole.
  - `_saved_since` looks at the assembly's time on each tick only while the mark stands. The planning read clears it in
    memory, so it does not re-plan every tick.
  - One house-pattern risk, now with more text: a raise in `carried_status` replaces the build's own sentence with
    `collect_failed` (`workbook_gui.py:1573`). Wrap the carry's sentence in its own `try`.
- **The window test gap.**
  - The Tk test drives `_start_build` / `_finish_build` with a hand-made `CarryResult`. The Linux round trip drives A's
    worker through `finish_build` and `carried_status` without the window.
  - Together they cover every line of the window's change, so the gap is acceptable.
  - Making the Tk test use the real worker is cheap: patch the carrying findings and drop the `build_gearbox`
    monkeypatch. It would have caught M1 if run with the findings None.
- **The question with every 2026 probe finding set** loses the states clause, and the not-open clause turns into its
  conditions (*… only when it and every file it uses were last saved by this SolidWorks … and nothing but Gear
  Generator's own files is open in SolidWorks; otherwise …*). The result loses its states sentence. The marks sentence
  then appears only if SolidWorks reads a document changed after the insert, which the probe found it does not. Every
  sentence stays true. Only S3's parenthesis and S10's bore need words.
- **The fallback sentences, the clash, the same error, the sub-assembly, the marks fact and the pattern instance** each
  read right for their case.
- **Placement words.** *against the gear it is mated to* is said for any anchor but the layout, so a component anchored
  to a carrier is said to stand against a gear. *the gear or carrier* would be exact.
- **`_yours`.** *"Sprocket-1, Sprocket-2, Chain-1 and 1 other component"* (W9a's cap of three) is odd when the fourth
  could be named.
- **A read that marked a document.** It says nothing is changed on disk, but not what to answer when SolidWorks asks
  to save Sprocket.SLDPRT on closing RangeBox.SLDASM. §9.2's wording; flagged for the contract, not for B.

---

## B's shape requests (W9D-PACKAGE-B.md, "Shape requests and deviations")

1. **Anchors on `CarryResult`: A should add them.** The re-derivation is not guaranteed to agree (S4). Use
   `CarryResult.anchors: List[Tuple[str, str]]` (old Name2, anchor as placed), or a third member of `inserted`.
   Should-fix, through the coordinator.
2. **`code_after`: B's work-around is sound.** A kept mate has no error but the one it had (`same_error`), since a new
   error falls its cluster back. No shape change.
3. **The owner slots of `unmeasured` (entity kind) and `gone` (feature): A should add them.** `OldEntity.owner` already
   holds the owner. Without the slot, the user reads *"M1 is on a face, which …"* and *"M1 was on Mid Plane in an app
   part, which that part in RangeBox_r2 does not have"*, and cannot tell which part. B's clauses already read the slot
   when given. A §2.3 table edit.
4. **The inventory's missing file and configurations: B's work-around is sound**, with the hedges above. No shape
   change. The record should not start keeping paths.
5. **The lost line said once, in the later Update's sentence: sound.** §9.4 has a later job say it, and the mark
   itself goes. No field needed.
6. **`exists` into the read's `isfile`: A should thread it.** The window's `exists` is `os.path.exists` either way, so
   nothing changes for the user. It lets the round trip stop patching `os.path.isfile` process-wide. Low priority.
7. **"Moved 30 mm in N and L": not reproduced.** At `6f9c8cb` (from a `git archive`) and at the head, with entity
   kinds off and on, the round trip's `result.carry.moved` is `[]`. Nothing for A to judge until B gives a
   reproduction.
8. **`CARRY_KIND_WORDS` duplicated and pinned:** fine.

A's shape changes that touch B are handled: `OldComponent.configurations` None from the record (B's *carried only
if*), and `read_entity_kinds`' default (S9).

---

## What I did not check

- The Tk window's four K12 mapping tests, deselected above.
- Any string on SolidWorks 2024's findings. Each finding there is None, so it is the "every finding None" state with
  2024 in place of 2026.

---

## Re-check of the fix round

*Independent, 2026-11-17, at `b6251b4`.* Under review:
- package B's `6441e34` (M1–M5, S1–S10, `bare_files`, `WHY_REFUSED` / `WHY_TOO_LONG`, the Tk tests on A's worker);
- `4b36095` (`CarryResult.anchors`, `bore_mm`, the findings patched explicitly);
- `b6251b4` (the window test's privacy check).

Read against the contract as edited at `d3bb9e7` and package A's fix round (`98ed62e`…`0c0e5be`, the 2026 probe reads
set in `findings.py` at `013c14c`). As before, every quoted sentence is real output: A's worker end to end on Desk's
RangeBox (W9a's work, Sun's Flank to arcs, entity kinds read), plus hand-made results for what the fake cannot make.
The script is in my scratchpad, not the repo.

**Suite.** Linux, at `b6251b4`: **2 failed, 3859 passed, 10 skipped**. The two failures are the known tkinter tests.
Windows (`python.exe` 3.13, pytest 9.1.1, a `git archive` of `b6251b4` on `C:`, deleted after):
`test_workbook_build.py`, `test_workbook_window.py` and `test_workbook_carry.py` gave **259 passed, 2 skipped,
4 deselected**. The four deselected are the K12 tests that put a window on screen, as before. B's 263 is the same run
with them included.

### Verdict

**Fit for the demonstration once one sentence is fixed (N1).**

All five must-fixes and all ten should-fixes are in:
- Today's state, on both versions, is W9a's sentence led by an honest finding, in the question and after the press.
- The carrying question fell from 326 to 169 words; B's part from about 180 to 85. That is a length a person reads,
  and I would cut nothing more.

N1 is new in the fix round. The result's compressed placement sentence now claims every component stands in every mode
where it stood in the mode showing. That is false for a component mated to a sliding gear, and the same result
contradicts it two sentences earlier.

### The first round's points, at head

| Point | At head | Evidence (real output) |
|---|---|---|
| M1 nothing carried | **fixed** | States 1, 2 and 2024 below: W9a's sentence, led by `CARRY_INSERTS`' finding |
| M2 feature in a part made new | **fixed** | *Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces because its Flank changed (RangeBox.SLDASM and that file keep it).* |
| M3 not read | **fixed** | *RangeBox.SLDASM is not open in SolidWorks, and Gear Generator reads it then only when its close has been shown clean (findings.OPEN_READ_ONLY_SHOWN_CLOSES_CLEAN_ON_2026), so nothing of yours was carried; as read at 15:09, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, …* — no "press again" |
| M4 stop | **fixed**, except one combination (N2) | *SolidWorks stopped the carry while reading the new revision: … It did not get to reading the new revision. Nothing of yours was carried, and RangeBox_r2 as built is saved. Your Sprocket-1, … stay in RangeBox.SLDASM, as read when this build began; …* |
| M5 lightweight | **fixed** | *Sprocket-1 was lightweight as read: its Lock3 is made again only if you set it resolved in SolidWorks before you press.*, said once |
| S1 verdicts, grouping | **fixed** | *Lock6 and Lock7 join Bracket-1, which is not carried, so they are not made again.* |
| S2 no save asked for nothing | **fixed** | *As read at 15:10, nothing of yours in RangeBox.SLDASM would be carried into RangeBox_r2. Your Keyway stays …* — and nothing more |
| S3 length | **fixed** | 169 words, 85 of them B's |
| S4 anchors | **fixed** | `carry_anchors` takes `CarryResult.anchors` only; the round trip reads `[('carried1-1', 'Sun'), ('carried2-1', '')]` |
| S5 D14 in the result | **fixed** | *RangeBox_r2 has no mode L: what your items were in L stays in RangeBox.SLDASM. Its new mode Low takes what they were in H.* |
| S6 in-context | **fixed** | *If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts.* |
| S7 a raised read | **fixed** | *SolidWorks stopped answering while reading RangeBox.SLDASM (RPC_E_CALL_FAILED), so nothing of yours was carried; RangeBox.SLDASM and your files are as they were on disk.* (the path in A's text reduced) |
| S8 grammar | **fixed** | *Lock9 beside it was*; *find a mate's face of Sprocket-1 again*; *M1 is not made again: Gear Generator has not yet been shown to …*; *SolidWorks moved Sprocket-2 off where it stood against RangeSlv when your mates were made again: 2.0 mm in N and L.* |
| S9 entity kinds | **fixed** | the round trip runs both ways |
| S10 bore | **fixed** | *M4 was on Sun's bore, …* / *M5 was on a face of Sun on its axis, …* by A's where slot |

### N1 (must-fix). The placement sentence says what the mates may not do

`ui_text.carried_status` says the sentence below whenever a floating component was carried and the gearbox has modes:

> *Your components stand in every mode of RangeBox_r2 where they stood in H, the mode RangeBox.SLDASM showed.*

The first round's sentence said this only of *"a floating one that stood elsewhere in another mode"*. §9.2 means one
no mate holds.

A component locked to a gear that moves between modes follows that gear. §15's Sprocket-2, locked to the sliding
RangeSlv, is one, and M9's `carry-closed` section is written to show it. In the same result, two sentences earlier:

> *SolidWorks moved Sprocket-2 off where it stood against RangeSlv when your mates were made again: 2.0 mm in N and L.
> Your components stand in every mode of RangeBox_r2 where they stood in H, the mode RangeBox.SLDASM showed.*

**Fix.** Say where they were placed, and claim the every-mode part only for a component no carried mate holds:

> *Your components were placed where they stood in H, the mode RangeBox.SLDASM showed; one no mate holds stands there
> in every mode.*

Say the second clause only when such a component was carried (one inserted with no entry in `remade` naming it).

### Today's real strings

**State 2: SolidWorks 2026, today.** The probe reads are set (`013c14c`) and every `CARRY_*` write gate is None.

The question, the carry's part after the build's own (whole question 145 words):

> *Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026
> (findings.CARRY_INSERTS_ON_2026), so as read at 15:09, your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM,
> and your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces; RangeBox_r2 has none of them, nor anything
> added since. Your Groove in Sleeve_m1.25_N17 comes with that part, which RangeBox_r2 reuses.*

After the press, the carry's part after the build's own 179 words (62 words):

> *Gear Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026
> (findings.CARRY_INSERTS_ON_2026), so your Sprocket-1, Housing-1 and Lock3 stay in RangeBox.SLDASM, as read when this
> build began; RangeBox_r2 has none of them. As read at 15:09, your Keyway stays in Gear_m1.25_N29, which Sun's new part
> replaces; RangeBox_r2 has none of it, nor anything added since.*

- **The footer** afterwards adds nothing: no carry, no inventory, as W9a.
- **The record** keeps the carry with `named` only. Its sentences are, for example, *Sprocket-1 is not carried: Gear
  Generator has not yet been shown to carry your work into a new revision on SolidWorks 2026
  (findings.CARRY_INSERTS_ON_2026)*.

This is W9a's sentence, word for word, behind one honest lead, so it is **honest and no worse than W9a**. The same
holds with the old assembly closed.

**One thing for package A, not B.** In state 2, with RangeBox.SLDASM closed, the worker now opens it read-only
(`open_read_only` in the fake's calls, `how` `read-only`), because the reads R.2 needs are set. It does so though
`CARRY_INSERTS` is None, so nothing can be carried.
- The user's sentence is then better than W9a's: *as read when this build began* instead of *was not open … so it was
  not read again*.
- But it is an open of the user's assembly made for nothing, on today's real path, where W9a made none.
- R.2's measured conditions make it safe as far as measured. Whether the read should run at all while `CARRY_INSERTS`
  is None is the coordinator's call.

**2024 (everything None)** is the same text with 2024 in it: *Gear Generator has not yet been shown to carry your
work into a new revision on SolidWorks 2024 (findings.CARRY_INSERTS_ON_2024), so …*, in the question and after the
press alike.

### The carrying states

The question with every gate set (B's part, 85 words):

> *As read at 15:09, RangeBox_r2 takes your Sprocket-1 and Housing-1 and makes your Lock3 again in the modes it was on
> in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part replaces (its Flank changed); your Groove comes with
> Sleeve_m1.25_N17. RangeBox_r2 holds what it carries unsaved. If RangeBox.SLDASM is closed, open it first unless this
> SolidWorks last saved it and its files and nothing of yours is open. Assembly features, display states and
> appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their own.*

This is true, short and not contradictory. Before M9 sets `REFERENCED_CONFIGURATION_READ`, it adds *Sprocket-1 and
Housing-1 are carried only if each file has one configuration.* and, at the end, *(Not yet shown on SolidWorks 2026:
findings.REFERENCED_CONFIGURATION_READ_ON_2026.)*. That is the right hedge.

The closed-assembly sentence is compressed past the point of saying what happens otherwise, but its advice, *open it
first*, is the right one, so I leave it.

The result (B's part, 133 words) is right, apart from N1:

> *Carried into RangeBox_r2, unsaved: your carried1-1 (was Sprocket-1) and carried2-1 (was Housing-1), each where it
> stood, and your Lock3, on in the modes it was on in. Your Keyway stays in Gear_m1.25_N29, which Sun's new part
> replaces because its Flank changed (RangeBox.SLDASM and that file keep it). Your components stand in every mode of
> RangeBox_r2 where they stood in H, the mode RangeBox.SLDASM showed. [the fake's marks sentence] Assembly features,
> display states and appearances stay behind; sub-assemblies come over rigid, pattern instances as components of their
> own. If a part of yours was made in context of RangeBox.SLDASM, it still refers to that assembly's parts. Save
> RangeBox_r2 in SolidWorks to keep what was carried.*

Two things in it are the fake's, not B's:
- the components' names (*carried1-1*);
- the marks sentence (the fake marks the parts; the 2026 probe found SolidWorks does not).

### New things

- **N2 (should-fix). `_split_stop` loses a stop that comes with the files-changed fact.**
  - `_AFTER_CARRY`'s `^` alternative, with its lazy `(?:\S+ )*?`, matches from the very start of the text whenever
    *changed on disk while Build again…* occurs anywhere. A's `_carry_after` runs after a stop too and appends its fact
    to `stopped` (`swbuild.py:8398-8400`).
  - So for a stop plus changed files, the stop comes back as part of the "after" text. `stop` is "". The *It did not
    get to …* tail and *What was carried before it is …, unsaved* are lost, and *Save RangeBox_r2 in SolidWorks to keep
    what was carried.* is said as if the carry had finished:

    > *… SolidWorks stopped the carry while making UserDist4 again: SolidWorks: AddMate5 answered 2 for
    > Sprocket.SLDPRT. Sprocket.SLDPRT changed on disk while Build again… carried your work, which Gear Generator never
    > does; look at it in SolidWorks. Save RangeBox_r2 in SolidWorks to keep what was carried.*

  - The user is never told that the assembly was not checked. The same happens when A's stop text has no final full
    stop before the fact.
  - **The field A should add**: `CarryResult.files_changed: List[str]`, the file **names** (never paths) of the old
    assembly's and user's files whose time differed after the carry. Add `CarryResult.after_unread: str`: why the
    times and flags could not be read after the carry (today's *Whether your files changed could not be read after the
    carry: …*), "" when read.
  - `stopped` is then a stop only. B words the fact from the field and keeps it on record (`CarryEntry` gains the same
    two, defaulted).
  - Until A adds it, the interim fix is to search from the last *. * before *changed on disk while* (`rfind`), not from
    `^`.
- **N3 (should-fix). The window's own `try` is not silent, but it says the wrong thing.**
  - A raise in `carry_anchors` or `carried_status` now leaves the build's own sentence standing. That is the point,
    and it is right.
  - But it appends `collect_failed(exc)`: *The build could not be collected — KeyError: …*. That follows *Built 1
    part, …*, so it reads as the build failing. It does not say that RangeBox_r2 holds the carry unsaved, though the
    footer will.
  - The exception's text is not passed through `bare_files`.
  - Fix: a sentence of its own, through `bare_files`: *What was carried into RangeBox_r2 could not be said (KeyError:
    …); it holds it unsaved: save it in SolidWorks to keep it.* Make the last clause conditional on `result.carry.unsaved`.
- **N4 (should-fix). `bare_files` can eat words that are not a path.**
  - Safe: ratios (*1:2*), times (*14:02*, *2026-11-17T14:02:00Z*), a mate's *SolidWorks:* prefix, leaf Name2s with
    `/`, a path with spaces, a UNC path, a forward-slash path, two paths in one sentence, and a path followed by a word.
  - It does go wrong when a path's file name is followed by a full stop or comma, and a `/` comes later in the same
    text. The folder group then runs across the sentence:
    - *Saved C:\R\RangeBox.SLDASM. Next/then* → *Saved then*;
    - *C:\A\x.SLDPRT, in folder D/E* → *E*.
  - And `_LEFT` cuts any token ending in a backslash: *mate A\B* → *mate B*.
  - The first is plausible in an exception's text.
  - Fix: let the lookahead end the file name on punctuation as well as space,
    `(?!\.[A-Za-z][A-Za-z0-9]{1,5}(?:[\s.,;:)\]]|$))`. Do not let a folder segment hold `. ` or `, `.
- **`WHY_REFUSED` and `WHY_TOO_LONG`: right.**
  - With A's real refusal: *M2 is not made again: SolidWorks refused it, saying AddMate5 would not make M2 again
    (status 1).*
  - The cap: *Coincident8 is on a face of Sprocket-5 that Gear Generator did not look for, since finding it among
    Sprocket.SLDPRT's faces would have taken too long* (an edge of an app gear: *an edge of Sun … among
    Gear_m1.25_N29.SLDPRT's edges*).
  - Both are §9.3's, and neither says the cap's name, as the contract wants.
- **`bore_mm` from the OLD part: right.**
  - The contract (`W9D-INTERFACES.md:69`) says the OLD gear part's bore, *what its Bore Diameter global was written
    from*. A compares it with the cylinder's radius read in the old part (`swbuild.py:7392`).
  - The new plan's bore would be wrong exactly when the Bore changed.
  - B reads it from the record's `PartEntry.spec`, not the sidecar the contract names. Both hold what was written.
  - A Bore that is an expression or carries a unit reads None, so the sentence falls back to *a face of Sun on its
    axis*, which is never false.
  - One residue: a part the user re-dimensioned in SolidWorks (K11 `MISMATCHED`) has a bore other than its spec. It
    then reads *on its axis*, not *bore*, which is still true.
- **Privacy: right.**
  - `CarryEntry.stopped`, every named entry's subjects and sentences, and every fallback's subjects go through
    `bare_files`.
  - Components keep Name2, kind and configuration.
  - `CarryEntry.assembly` is the old assembly, the app's own file.
  - Only N3's fallback sentence and N4's edge cases remain.

### Notes

- *your Sprocket-1, each where it stood*: *each* with one component. Drop it for one.
- The stop's tail repeats A's step: *… stopped the carry while reading the new revision: … It did not get to reading
  the new revision.* A's `skipped` starts with the step it stopped in; B could drop the first item when it is the step
  `stopped` names.
- A's not-open reason still carries *(a file saved since on another SolidWorks is not read)*. That is A's text, and
  the file's version is read; only the open is refused.
- The Tk tests now drive A's worker (two tests, a carry and today's state), which closes the first round's gap.

### What I did not check

As before: the four K12 window-mapping tests, deselected on Windows.

---

## Re-check of package B's round `5f52913` (after the first SolidWorks 2026 run), with A's fifth round at head

*Independent, 2026-11-17.* I read `5f52913`'s diff. The strings below come from scratch scripts on A's worker and the
fake at head, with hand-made inventories where the fixture holds no gear mate. **Suite: 2 failed (tkinter), 3904
passed, 10 skipped.**

### Verdict

**One must-fix before the run, a one-line fault in the new *may* code: the question says UserGearRoot twice, once as
not made again and once as made again if.** The demonstration's own fixture, with its gates patched on 2026, will
print it. The rest of the round is sound. Two sentences need words (B2, B3).

### B1 (must-fix). UserGearRoot is said both ways

`carry_sentence` drops from the definite reasons the items said as *may*:

```python
named = [n for n in plan.named if … and n.item not in silent_axis …]
```

`silent_axis` is a dict from **gear id** to mate names (`_foresight_silences`), so `n.item not in silent_axis` tests a
mate name against `"Sun"` and never drops anything.

With `COAXIAL_FACE_READ_ON_2026` True (set) and the write gates patched, a recorded gear mate on a face of Sun gives:

> *UserGearRoot was on a face of Sun, and Sun's part is new because its Flank changed, so it is not made again. … Your
> UserGearRoot is made again only if the face of Sun it is on proves to be on Sun's axis, since Sun's part is new.*

**Fix:** flatten the dict for the filter:

```python
axis_items = {m for ms in silent_axis.values() for m in ms}
```

then test `n.item not in axis_items`. Pin it by asserting that the *may* item's definite clause is absent.

### B2 (should-fix). Two *may* sentences say more than they know

- **The axis *may* is said even while a gate holds the mate back anyway.**
  - With `CARRY_GEAR_MATE_ON_AN_APP_GEAR` None, or `gear` not in `CARRY_REMAKE_KINDS`, the question still says *"Your
    UserGearRoot is made again only if the face of Sun it is on proves to be on Sun's axis"*.
  - Literally that is true (*only if*), but it implies the axis is all that stands in the way.
  - Say it only when both of those gates hold. Otherwise the plan's own reason is the one to say.
  - The ratio *may* is already safe: with the gear gate unset, `plan_carry` names UserGear6 `unmeasured` (by the gate),
    not `unread`, so no *may* is said.
- **The in-error clause's *only if* is false.**
  - It reads: *"Lock3 was in error in RangeBox.SLDASM as read; made again, it is carried only if it reads the same
    error, and it never keeps a gear from turning."*
  - A mate made again with **no** error is carried too: `_judge` passes a code of 0.
  - *it never keeps a gear from turning* reads as a claim about the mate, not the rule.
  - Fix: *"…; made again, it is carried if it reads no error or the one it had, and not if it keeps a gear from
    turning."*
  - With that wording the clause agrees with A's M3: a tie is never excused, whatever error the mate reads.

### B3 (should-fix, with A). The why for UserAxis9 and UserAsm6, end to end

UserAxis9 is a mate on a component suppressed in the mode showing. Results, printed from A's worker:

- **The fake as it is:** *"SolidWorks would not describe UserAxis9 wholly (its part is not loaded in SolidWorks
  (lightweight or suppressed)), so it is not made again."*
  - The why is there, but in nested parentheses.
  - It says *lightweight or suppressed* where R knows which.
- **The fake made to read as SolidWorks did in run 2** (the entity's kind `unread`):
  *"SolidWorks would not describe UserAxis9 wholly, so it is not made again."*
  - **No why.** A's new field is not reached on SolidWorks' read (`W9D-REVIEW-A.md`, re-check A1).

UserAsm6 is the assembly's own plane beside a lightweight component. On SolidWorks, A's new why is said through B's
clause as *"SolidWorks would not describe UserAsm6 wholly (the assembly's own plane is not told while a component of
it is lightweight), so it is not made again."* This is wrong twice:
- it is Gear Generator's rule, not SolidWorks declining;
- *"is not told"* is not English.

The fake never reaches it, since it names the assembly's own entity `""`.

**What B owes:** word `WHY_UNREAD` by where the why comes from. Once A hands a slot for each case:
- *"UserAxis9 is on Sprocket-9, which is suppressed in H, the mode RangeBox.SLDASM showed, so it is not made again"*;
- *"UserAsm6 is on the assembly's own plane, which Gear Generator does not read while a component of it is
  lightweight (SprocketLight-1), so it is not made again"*.

Until A changes the field, B can tell these two cases by the text A sends. Also use a colon rather than a second pair
of parentheses when the reason holds one.

### The footer (§9.4 after a job's sentence)

True in every state I traced:
- **Carry finished.** The build's sentence ends *"Save RangeBox_r2 in SolidWorks to keep what was carried."*, so
  `_asks_carry_save` holds the line back. It is said once.
- **Carry stopped with something carried.** The stop sentence asks no save, so the line follows it. That is true,
  since `unsaved_at` stands.
- **Nothing carried.** `unsaved_at` is 0, so there is no line.
- **Saved since.** The planning read's `clear_saved` drops the mark, so there is no line.
- **A later Update:** the line follows the Update's sentence while the mark stands. When that Update found the carry
  lost, the mark is gone, so there is no line.
- **Never twice.** For a `NOTE_JOB` the state's own block, which also adds the line, is not run. For a `NOTE_ANSWER`
  only that block adds it.

A copy's window shows the other workbook's record, and would say the line too. That is the same as W9c's Update line
(house behaviour), noted, not judged.

### The in-error clause against M3

With B2's wording the two agree. As written, *"carried only if it reads the same error"* is false for a mate that
comes back clean. It does not contradict M3, which only adds the tie.

### What only the record's silence names (the *may* sentences)

- **The ratio *may*.** It is said only for a gear mate the inventory holds whole, with every entity's kind known, that
  `plan_carry` names unread. That is the ratio and sense the inventory never keeps, so it never covers what the record
  does know. Both outcomes are true: if R reads the ratio, the mate is made again (other gates permitting); if not, it
  is named.
- **The axis *may*.** It needs B1 and B2's gate condition.
- **Grammar.** Both stay within §9.1's grammar.

---

## Last re-check before the second run: package B's `4b899e9` (B1, B2) and `b67cdc5` (B3), and the script against them

*Independent, 2026-11-17.* The strings below are from A's worker on the fake at head (`b67cdc5`), and from hand-made
inventories for the question. **Suite: 2 failed (tkinter), 3915 passed, 10 skipped.** I ran the script's
`--self-check`, which ends `done 0 failed`. Beyond it I read `question_problems`, the result checks and
`expected_outcome` against B's actual sentences.

### Verdict

**Package B is fit for the run, and the script holds against B's new sentences.** No fragment the script matches has
moved.

What stands between head and the run is package A's read-back fault (`W9D-REVIEW-A.md`, last re-check, N1). It will
make `carry-closed` FAIL UserAsm6, though the script's expectation there is right.

Two should-fixes for B:
- a tense that contradicts the D10 fact;
- *SolidWorks* twice in the no-cause sentence.

### B1 and B2: done

- **B1, as a test.** `test_the_demonstrations_question_names_each_mate_in_exactly_one_sentence` checks every mate of
  one realistic record. That record has a ratio *may*, an axis *may*, a face of a part made new, a mate in error and
  a lock, on 2026's reads with the gates patched.
  - It is general in its check, but it covers one shape: suppressed and beside-lightweight causes are not in it.
  - Its escape clause, *named nowhere if "mates again" is in the text*, is loose.
  - The fault itself is fixed: the filter is by mate (`axis_items`).
- **B2, the axis *may*.** It is now said only while `COAXIAL_FACE_READ`, `CARRY_GEAR_MATE_ON_AN_APP_GEAR` and `gear`
  in `CARRY_REMAKE_KINDS` all hold, which are the gates that would let the mate be made.
- **B2, the in-error wording.** *"…made again, it is carried if it reads no error or the one it had, and not if it
  keeps a gear from turning."* That is true by `_judge` (a code of 0 is carried) and in step with M3. The single-mate
  case is joined to the lead, so the mate is said once.

### B3: the sentences by cause

The result, printed from A's worker:
- **Suppressed in the mode showing (modes):** *"Lock1 and UserAxis9 are on Sprocket-1, which is suppressed in 2H, the
  mode TransferCase.SLDASM showed, so they could not be read and are not made again."* True.
- **Without modes:** *"… which is suppressed in T.SLDASM …"*.
- **Beside lightweight:** *"UserAsm6 is on a plane of T.SLDASM itself, which Gear Generator does not read while
  Sprocket-1 is lightweight in it, so it is not made again."* True as the rule.
  - But on the demonstration's open path the result also says D10's fact, *"SprocketLight-1 was lightweight in
    RangeBox.SLDASM and is resolved there now: SolidWorks loaded its part to carry it."* (run 2's measured case).
  - Together the two say *is lightweight* and *is resolved now* of the same component.
  - **Should-fix:** *"…while Sprocket-1 was lightweight in it, so it is not made again."*
- **No cause:** *"SolidWorks would not describe UserOdd wholly (SolidWorks would not say what kind of entity it is),
  so it is not made again."*
  - SolidWorks is said twice.
  - The inner clause can be untrue (A's S6).
  - **Should-fix (B):** with no cause, say the clause alone: *"UserOdd is not made again: SolidWorks would not say what
    kind of entity it is on."*

The question, from hand-made inventories on RangeBox (the gates patched):
- **Suppressed** (Sprocket-1 state 0, Lock3's entity on it unread):
  > *"As read at 18:00, RangeBox_r2 takes your Sprocket-1 and Housing-1. Sprocket-1 was suppressed in the mode
  > RangeBox.SLDASM showed, as read, so Lock3 on it could not be read: show a mode where Sprocket-1 is resolved before
  > you press, or Sprocket-1 may not be carried and Lock3 is not made again."*
  - True.
  - The empty mode never shows: the question names *the mode RangeBox.SLDASM showed*, not a mode by name.
  - It reads as one thought, not odd.
- **Beside lightweight** (Housing-1 lightweight, UserAsm6 to the assembly's plane):
  > *"UserAsm6 is on a plane of RangeBox.SLDASM itself, which Gear Generator does not read while Housing-1 is
  > lightweight in it: it is made again only if you set Housing-1 resolved in SolidWorks before you press."*
  - By the worker's code, a resolved Housing-1 lets R read the root, place the entity as `ASSEMBLY`, plan the mate on
    `asm:plane1` and make it.
  - On SolidWorks today it is then deleted again by A's N1. So the clause is true as a necessary condition, and it
    becomes true as a promise once N1 is fixed.
  - With two lightweight components it names only the first. It is still true (*only if*), but incomplete.

### The script against these rounds (`probe/w9d_demonstration.py` at `20080c3`)

**The question.** `question_problems` (`:530-542`) matches three things:
- *"UserGear6 … made again if the press reads"*;
- *"UserGearRoot … proves to be on Sun's axis"*;
- the absence of *"in error in RangeBox.SLDASM as read"*.

All three still hold for the fixture:
- UserGear6 is held whole, with its kinds known, and named for its unread ratio, so its *may* is said.
- UserGearRoot's *may* is said with the three gates patched, and is no longer also said as definite.
- No mate of the fixture is in error as read. The new lead clause names a single made mate only if it is in error, and
  UserAxis9's code, if any, does not count: it is not a mate made again.

**Sprocket-9's advice.** The script matches no fragment of it (`grep` finds none), so its new shape, joined with
UserAxis9, costs nothing.

Lines `:2286` (*Keyway*, *As read at*, *Flank*) and `:2216` (the finding and *Keyway* in `carry-gates`) still hold.

**The result.**
- `:2312` (*Carried into RangeBox_r2, unsaved*, *Keyway*, *UserSunFace*) holds. UserSunFace is named in its own
  part-new sentence.
- `:2237` (`carry-gates`: W9a's lead and *Keyway*) holds.
- `:2515`'s lost line is unchanged.

**`expected_outcome` against the worker.**
- The script compares by `why` word only, so the new trailing subjects do not matter.
- `carry-gates` reads the subjects only for gate names (`:2230`, `:2250`), which the cause subjects do not contain.
- UserAxis9 (`carry`, open) and UserAxis7 (`carry-closed`) are `{"unread"}`, and the worker names both `WHY_UNREAD`
  with `CAUSE_SUPPRESSED`.
- UserAsm6 (`carry`, lightweight) is `{"unread"}`: `CAUSE_BESIDE_LIGHTWEIGHT`.
- UserAxisLight is `{"lightweight"}`, which agrees.
- **One mismatch, and it is A's, not the script's:** UserAsm6 in `carry-closed` is expected `{"remade"}`, but the
  worker will name it `differs` (A's N1). Do not change the script for it; fix A.

**No must-fix for the script.**
