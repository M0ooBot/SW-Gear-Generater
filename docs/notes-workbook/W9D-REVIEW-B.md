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
