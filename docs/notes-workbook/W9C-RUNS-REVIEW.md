# Review of W9c's demonstration runs on SolidWorks 2026

*Independent, 2026-11-17, at `6cdc709`. I started no SolidWorks and changed no code.*

- *What I read:*
  - runs 4, 5 and 6, by section and outcome lines first, then the result lines of every section the findings rest on,
    and the JSON where a claim needed it (`probe/results/w9c-demo-sw2026-20261117-{4,5,6}-*.log`, with their JSON);
  - the script's commits between them (`cdd3bbb`, `9efcb2c`, `30bf0e9`);
  - `W9C-DEMONSTRATION.md`, the interface note's rulings, the plan's §5 W9c, and my `W9C-REVIEW.md`.
- *App code* is `887916b` (with B's and A's fix rounds) throughout all three runs. Only the script moved.
- *Log citations* are `log 4:`, `log 5:` and `log 6:` with line numbers.
- *2024 is owed,* as an addendum at the end of this file.

**Verdict.**

- **Each section's "0 failed" stands on what the logs hold.** No check I traced is vacuous, no app fault is put down
  as the script's, and each loosening between runs is one that was ruled and is said in the log.
- **The plan's Done-when for W9c is shown on 2026**, item by item, with one honest caveat: Hub lands inside the
  user's Sprocket-4, and the app says so after the press rather than before.
- **Five findings may be set True for 2026:** `UPDATE_INSERTS_A_GEAR`, `UPDATE_BANDS_IN_PLACE`,
  `UPDATE_ADDS_A_MODE`, `UPDATE_REMOVES_A_MODE` and `UPDATE_MAKES_MATES_WITH_MODES`. I agree the other three stay
  None.
- **The runs show one more fault of the app's (must-fix 1).** The footer still foresees a false refusal after a
  mode is added and another later removed. The line sits in run 5's log unjudged, because a gate's foreseen stop
  displaced it.
- **Closing W9c with the ring fault open is defensible.** But the stopped Update's advice to "save them … to keep
  what it did" is wrong for a part left in error (should-fix 1). It should go with the ring fix.

---

## Must fix

**1. After a press that added a mode, the record's inventory does not have the new mode in the user's mates'
on-lists. The footer then foresees a refusal that the press does not make.**

- *Where it shows.* In run 5's `modes`, H2 was added. Before N's removal, the footer's W9a prediction (log 5:569,
  printed as *"not said beside a foreseen stop"*, so never judged) reads:

  > *"As read at 10:11, the next press would stop before changing anything: Your lock UserLock1 is on in H and L and
  > suppressed in H2, …"*

- *Why it is false.* UserLock1 is **on** in H2: H2 was copied from H, and the worker read the user's flags there
  (`took_active_state`). The press removing N then went through (*"Updated SolidWorks: deleted the mode N, …"*).
- *Cause.* The H2 press recorded the inventory it read at its start, before H2 existed. So the on-lists hold H, N
  and L. B's fix (`6d9e4af`) takes the removed modes out of each on-list, but nothing puts the added ones in. The
  footer then judges a lock "suppressed in H2".
- *When it bites.* Today the gate's foreseen stop hides the line. Once `UPDATE_ADDS_A_MODE` and
  `UPDATE_REMOVES_A_MODE` are set, any user who adds a mode and then removes or changes another sees a red, false
  footer.
- *Fix.* Do either, and test the add-then-remove footer:
  - when a press added modes, record each user mate's flag there as the worker read it (`took_active_state`); or
  - have the footer treat a mode on record that the inventory never read as a copy of the mode it was made from
    (`work_in_added_modes`).
- *Effect on the findings.* None: this is the footer, not a write. It should land before or with setting the mode
  findings.

## Should fix

**1. When an Update stops in a part left in error, it should not suggest saving.** This goes with the ring fix.

- *The status.* Run 5's stopped `remake` (log 5:942), and run 4's before it, said: *"It had already changed
  Gear_m1.25_N29, Gear_m1.25_N13 and Ring_m1.25_N55, not saved: press Update SolidWorks again once that is put
  right, or save them in SolidWorks to keep what it did."* (`ui_text.py:1921`).
- *Why the advice is wrong.* Run 6's `ring` shows the ring part, once in error, does **not** recover when set back to
  55 (*"54, then 55 again … clean at the end False"*). Run 4 shows the assembly left behind: Sun and the planets at
  their new teeth, nothing re-placed, and the planets interfering with the ring by about 31 mm³ in every mode (log 4,
  `remake, H/N/L shown`). The app's own status does not name that interference.
- *What saving would do.* It would keep a ring part SolidWorks cannot rebuild, and gears that clash.
- *Fix.* When the stop is a part in error, the sentence names it as in error and says to close it, and the parts
  changed with it, **without saving**, then press again once the fault is fixed. It must not offer saving.
- *Why this is not a W9c fault.* The sentence is W4's and the path exists without modes too. But W9c's
  `UPDATE_MAKES_MATES_WITH_MODES` opens tooth changes to every gearbox with modes, so the advice reaches more users.

**2. Hub is put into the user's Sprocket-4, and the footer does not foresee it.**

- *What happened.* The Done-when press inserted Hub where the user's Sprocket-4 stands: 1408 mm³ in every mode, plus
  RangeSlv against Sprocket-4 in H and N (log 5, `fixed`, post-checks and `Check:`).
- *The app named it in every mode after the press,* red, and the script checks exactly that under the coordinator's
  ruling (`cdd3bbb`).
- *But the footer before the press is green and silent.* The press does not refuse, which is the ruling. The user
  should still hear before the press, at least, that a new gear may meet their components.
- *Fix.* Say it as a footer line when an added gear's span along its shaft overlaps a user component's recorded
  frame, or rule that "after" is enough.
- *For the user.* An Update that adds a gear can place it into a component of theirs. It says so after, in red, and
  leaves both where they are.

**3. Note the unmeasured scope when the findings are set.** Two kinds are exercised only through the fake:

- a plain gear added (a lock to its anchor, or a new mesh), where on SolidWorks only Hub was added. Its spline is a
  gear-kind mate whose sense is read on the same route, so I allow `UPDATE_INSERTS_A_GEAR` for it, but the finding's
  comment should say it was measured on a hub;
- a removal **through Update** on a gearbox with modes. On SolidWorks the going-ahead removal was the 12 : 1, with no
  modes and no user work; with the user's work a removal always refuses (C4). The delete with modes is P1's, so no
  finding is missing. It is unmeasured end to end.

## Notes

- **N1 — which run each section rests on is sound.**
  - `remove` on run 4 (`cdd3bbb`): the later changes touched `fixed`'s save and reopen, `remake`, `ring`, and the
    refused press's record check. The last was loosened in `9efcb2c`, so run 4 judged `remove` under the stricter
    rule.
  - `fixed`, `modes` and `bands-off` on run 5 (`9efcb2c`), and `remake` on run 6 (`30bf0e9`).
  - The app code is the same throughout.
- **N2 — the three loosenings, each ruled and said.**
  - *Interference (`cdd3bbb`).* App-against-app interference is still a FAIL and a STOP, and run 4's planet-ring
    clash failed under it. A clash with a user component must be one the app named, in each mode it checked, both
    ways. That check could fail and did not: the volumes agree pair by pair (log 5, `fixed`).
  - *`gearbox.solidworks` (`9efcb2c`).* It allows exactly the field schema 9 writes on a refused press, said as a fact
    with its value (log 6, `remake`, *"wrote the SolidWorks it read onto a record that had none"*). Nothing else on
    the record may change, and the check names any other change.
  - *28/14/56 for 30/12/54 (`30bf0e9`).* The gate measures gear mates remade with modes, not the ring part's sketch.
    `ring` shows 55 → 54 fails on the part alone, with no assembly involved, and any one-tooth-down step fails
    (56 → 55 too). 28/14/56 keeps the centre distance and even planet spacing. The remake then read every mate's
    sense, every flag, no interference in any mode, and L at 3.0.
- **N3 — the removal path on SolidWorks.** `remove` measured G4 taken out (P1's route through the worker, each mate
  read gone by name, nothing moved, C6's part entry dropped), and both refusals on setup (C4, and C4 with the user's
  lock naming it), with nothing written by trace, file times and save flags.
- **N4 — `RangeSlv moved +nan mm from N`** in `modes` after N is gone is a script fact line only. The judgement no
  longer needs N (`cdd3bbb`).
- **N5 — turning.** "Each mode turning as §3" rests on the app's motion report: L 2.896552, then 3.0 after the
  remake. Every gear reads free, and the flags and senses are read in every mode. Nothing drives a gear on SolidWorks.
  That is as in W9b's runs.

## The Done-when (plan §5, W9c), on 2026

| Item | Shown? | Where |
|---|---|---|
| RangeBox with the user's work, edited to RangeBox_Fixed: one Update | **Yes** | log 5, `fixed`: classify in place, gates refused first, then one press |
| … adds Hub (built, inserted, mated, resolved in every mode, M5/M6) | **Yes** | `Hub_m1.25_N17-1`; three mates on in H, N and L; spline sense read; resolved 2 in each mode |
| … gives RangeSlv its bands in place, the user's groove kept (M8) | **Yes** | the relief's five features in no error; the bore exact; the groove before them, its dimensions and faces as before; the step faces by their edges to 1e-4 |
| … leaves every user item as it was | **Yes**, with should-fix 2's caveat | every component where it was, 8 user mates as before, the user's own files unwritten |
| … each mode as §3 | **Yes** | H, N and L to §3's table, Hub 1.0 from HighDog |
| A second press quiet, after save and reopen | **Yes** | nothing changed, every save flag False, no unsaved mark on record |
| A mode added (M10) | **Yes** | H2 from the mode showing, flags and slides read back, the user's items there said, judged as §3's H |
| A mode removed (M10) | **Yes** | N deleted unshown, UserAngle4's lost flag said exactly as read; the mode showing refused with nothing read; H (the first) removed with L first |
| A gear removed | **Yes** where nothing of the user's is; otherwise a refusal before any write, naming what is in the way | log 4, `remove` |
| Gear mates remade with modes | **Yes** | log 6, `remake`, with the user's work on setup |
| Confirmed on 2024 | owed | the addendum |

## The findings for 2026

| Finding | Set? | On |
|---|---|---|
| `UPDATE_INSERTS_A_GEAR_ON_2026` | **True** (measured on a hub; should-fix 3) | log 5, `fixed` (and log 4, `fixed`) |
| `UPDATE_BANDS_IN_PLACE_ON_2026` | **True** (giving bands, after a user feature) | log 5, `fixed` |
| `UPDATE_ADDS_A_MODE_ON_2026` | **True** | log 5, `modes` |
| `UPDATE_REMOVES_A_MODE_ON_2026` | **True** (the first mode included; the mode showing refused) | log 5, `modes` |
| `UPDATE_MAKES_MATES_WITH_MODES_ON_2026` | **True** | log 6, `remake` |
| `UPDATE_MAKES_A_NEW_COUPLING_ON_2026` | None | not reached by any legal edit |
| `UPDATE_SUPPRESSES_THE_RELIEF_ON_2026` | None | `bands-off` made the call script-side only; no Update reaches it |
| `EXTERNAL_REFERENCES_READ_ON_2026` | None | `m4` had no positive case |

I agree with the coordinator's intent on the last three. Must-fix 1 should land before or with the two mode findings
reach users, because those findings are what turn the hidden false footer into a shown one.

## The ring fault, and closing W9c with it open

- *What it is.* It is a fault of the ring part's sketch on a one-tooth-down value change, older than W9c.
  - It reproduces on the part alone, by the app's own `update_variables`.
  - The new flank start comes within 0.024 mm of where the short radial lines end, and SolidWorks solves them to the
    far side (code 72).
  - The other changes are clean: 56, 53, 50 and 60, two steps down, and a 54 built from scratch.
- *Closing W9c with it open is defensible:*
  - W9c's own behaviour around it was right. The press stopped in the part before the assembly, said what it had
    changed and what it did not get to, and wrote nothing to the assembly. The user's items were untouched (log 4,
    `remake`).
  - The fix is a part-level item in `swbuild.update_variables` / `gears/internal.py`.
- *What W9c's behaviour does need,* with that fix and not after it: should-fix 1's sentence.
- *The record after the stop.* The JSON does not hold the record after the stop beyond its schema. By the code path,
  it is W4's: the changed parts are named unsaved, and the next press reads them again under K11's unsaved rule. Run
  4 then closed the copy unsaved and judged nothing on it. A test pinning the next press after a part rebuild failure
  with modes would be cheap, and should come with the ring fix.

## Privacy

- No SolidWorks frame title, licence edition or document title of anyone's but the run's own appears in the three
  logs or the JSON. The titles and paths are the run's copies only.
- Two things remain:
  - the Windows account folder in paths, which is the known open question;
  - SolidWorks' own balloon-tip text, which is generic product text.

---

## Addendum: SolidWorks 2024

*(owed: the confirming run now in progress)*

---

## The final runs on SolidWorks 2026 (34.0.0), and 007b3aa

*Independent, 2026-11-17, at `d878105`. I started no SolidWorks and changed no code.*

- *What I read:*
  - run 10 (`…-10-final-whole-remake-script-fault.log`, `w9c-demo-20261117-143454.json`), every section;
  - run 11 (`…-11-final-remake-step2-assembly-flag.log`, `w9c-demo-20261117-153629.json`), `remake`;
  - checked against run 8 (`64bec58`, 34.0.0) and the morning's runs 5 and 6 (`9efcb2c`, `30bf0e9`, 34.1.1), section
    by section, by their check lines;
  - the note's dated section for runs 10 and 11, and `007b3aa`.
- *Citations:* `log 10:` and `log 11:` with line numbers.
- *Snapshot and version:*
  - Run 10 states snapshot `3a9e592` (log 10:2) and attaches 2026 revision 34.0.0 (log 10:4). Its JSON holds
    `revision [34, 0, 0]` and `snapshot 3a9e592`.
  - Run 11's snapshot is `3a9e592` with `probe/w9c_demonstration.py` from `eabf14e`.
- *Suite at `d878105`:* 3702 passed, 10 skipped, 2 failed (the `tkinter`-only pair).

**Verdict.**

- **Runs 10 and 11 are sound evidence for `3a9e592`'s `src`, and so for head's.** `007b3aa` is the only `src` change
  since, it is Tk-side, and it changes nothing any section does (below).
- **Seven sections are 0 failed with no STOP.** No check is vacuous and nothing is explained away. The four `noted`
  lines are SolidWorks' notification box, exempt by the standing ruling, as in run 8.
- **`remake`'s one FAIL in run 11 is the script's expectation.** The app wrote nothing in step 2, and that is proven.
  No rerun is needed on 2026.
- **Run 11 measured something new: step 1's press leaves `RangeBox.SLDASM` modified.** The press changed only parts
  and wrote nothing to the assembly. This makes the stop's "close … without saving" advice incomplete (should-fix A
  below). It does not touch any finding.
- **The five findings this review allowed this morning may be set True for 2026,** on both revisions. The other three
  stay None.

### 1. Section by section

- **`landing`** (log 10:12-171, 0 failed). The fix is shown on the app as it stands (log 10:170).
  - Groups 1–5 read as in runs 7–9. Set straight, the ring fails only at 0.0379 and 0.0378 (codes 72, 1). The leftover
    reopens clean at 55.
  - Case 6, just above 0.2 and unrouted: clean at 0.2042, 0.2025 and 0.2390.
  - Case 7: 36 → 34 is clean set straight at 0.0564, with the old end beyond the new start, and clean routed by way
    of 33. 44 → 42 is clean.
  - Case 9: a module alone that lands is routed by way of 54 and back, the count reported unchanged
    (`changed ['Module']`).
  - Case 10: with the user's cut in error at code 71, the change is routed with both legs `[False, False]`. It ends at
    54, Tooth Space and Teeth clean, the user's cut the only feature in error before and after.
  - **Case 8 meets the condition set for N2's rule.** The dimension links as the app reads them on SolidWorks are
    `…@Tooth Space Sketch`, with no document suffix, for recipe B (`Base`, `Flank`, `HalfSpace` and `Pitch` among
    them) and for recipe A (none of them). Recipe B is set straight clean and never routed (log 10:145-157).
  - A fact for the threshold, not a fault: two short landings rebuilt clean set straight. They are the module-only
    0.0408 and 36 → 34's 0.0564. So the hazard is not the fraction alone, and 0.2 stays conservative.
- **`fixed`** (0 failed). Check for check, it matches run 8's, apart from run 8's master building. The gates refuse
  first, with nothing written by trace, by flags and file times, or on the record but the refusal. Then:
  - Hub is built, inserted, mated, resolved 2 in every mode, and its spline sense read (log 10:382-401).
  - The bands are given with the groove kept, and the step faces land to 1e-4.
  - Every user item is kept, and each mode reads §3's table.
  - The interference with Sprocket-4 is named exactly, in every mode.
  - The second press after save and reopen is quiet, every save flag False (log 10:446).
  - It proposes `UPDATE_INSERTS_A_GEAR` and `UPDATE_BANDS_IN_PLACE` True (log 10:453-454).
- **`modes`** (0 failed). Its check lines are identical to run 8's.
  - The runs review's must-fix 1 is now shown on SolidWorks. After H2 is added, the inventory names H2 in every user
    mate's on-list where SolidWorks reads it on (log 10:639). Before N's removal the footer gives W9a's line in green,
    not a false refusal (log 10:687).
  - N is deleted unshown, its lost flag said. The mode showing is refused. H, the first mode, is removed.
  - It proposes the two mode findings True (log 10:661, 983).
- **`remove`** (0 failed). G4 is taken out with each mate read gone by name, and C6's entry is dropped (log
  10:1067-1069). The HighDog removal is refused under C4, before any write.
- **`remake`, main part** (log 10:1189-1373; again log 11:11-200). 28/14/56 remakes the four gear mates.
  - Every flag and sense is read in every mode, and the user items are kept.
  - There is no interference beyond what is named, and L reads 3.0.
  - It proposes `UPDATE_MAKES_MATES_WITH_MODES` True in both runs.
  - Run 10's M3 then died on the script's `gear_entry(box, "Planet")`, which `eabf14e` fixed without changing a
    check. That is the script's fault, not the app's, and run 11 is the M3 evidence.
- **`bands-off`, `m4`, `w9b-part`.** 0 failed, with the same facts and None proposals as before.
- **The masters reused from run 8 are acceptable.** `git diff 64bec58 3a9e592 -- src/` touches only:
  - the Update path (`update_variables`, `update_gearbox`, `_update_motion` and the finish);
  - the landing foresight;
  - the status wording.

  Nothing in a plan, `swbuild.build` or `build_gearbox` changed, so a build from scratch at `3a9e592` makes what
  `64bec58` made. The files were byte-identical before and after, and `fixed-updated.master` was made afresh by run
  10.

### 2. `remake` M3 on SolidWorks (run 11)

**Step 1 is as specified.** It stops in the ring and marks it. Its status names the three parts, "close them all … without
saving" (JSON `again.first.status`).

**Step 2: the app wrote nothing. Proven.**
- The press's calls by member are `OpenDoc6` 8, `IsSuppressed2` 112 and `GetSystemValue3` 1, nothing else (log
  11:316).
- `wrote_nothing` reports only "modified beyond step 1's parts ['RangeBox.SLDASM']" (log 11:361; JSON
  `second.wrote`). So every other item was equal before and after: every part's globals, every document's save flag
  *and* file time, `read_now`'s frames, mates and per-mode flags, and the four gear mates' ratios (29 : 13 and
  13 : 55). The flags themselves are equal before and after (JSON `second.flags`).
- The result's `changed`, `mates_made`, `remade_in_modes` and `placed` are empty. `skipped` reads "the assembly,
  because Ring_m1.25_N55.SLDPRT is in error", and the one failure names the ring's file (log 11:359).
- The ring reads Tooth Space 72 and Teeth 1 at 54 before and after.
- The status and the footer are the still-in-error sentence alone (log 11:359-364).

**The one gap the bracket leaves is closed by the code path.**
- With `RangeBox.SLDASM` already modified, its flag cannot show an untraced write such as the assembly's own globals.
- But `skipped`'s sentence is written only by `_held_in_error`, which returns before the change phase.
- The check phase before it writes nothing. `fixed`'s quiet press, which runs the same check phase, read every flag
  False before and after (log 10:446).

**What run 11 measured new: step 1's press leaves the assembly modified.** The fact line before step 2 lists
`RangeBox.SLDASM` among the modified documents, and so does `read_now`'s own read (log 11:308-309).
- No SolidWorks call came between step 1's press and that read.
- Step 1's traced calls are `OpenDoc6`, `IsSuppressed2`, `GetSystemValue3` and three `ForceRebuild3`, the parts' own
  rebuilds (log 11:255).
- The same check phase marks nothing in a quiet press.

So it is SolidWorks marking an open assembly modified when a component part of it is changed and rebuilt in its own
window. The app made no write to the assembly. This is a fact of 34.0.0. 34.1.1's runs did not read flags there.

**What it means for the app's advice: should-fix A.** The advice is incomplete. This is reasoned from SolidWorks'
behaviour, not measured here.
- After step 1 the status and the footer name only the parts the press changed: "close them all … without saving".
  The record's `unsaved` holds the parts, not the assembly.
- On SolidWorks:
  - **The assembly reads modified,** so closing it asks to save. SolidWorks' prompt there offers to save the
    referenced documents too, the ring in error among them.
  - **Closing a part's window while the assembly that uses it stays open leaves that part loaded, with its unsaved
    changes.** `documents()` lists every document in memory (`W4-RERUN-2026.md:52`). So a user who closes only the
    named parts finds the next press stopping on the same ring, still held in error, with the same sentence.
- The run could not see this: the script closes everything (`W.quit_in`).

*Fix, Tk-side:* whenever a part left in error is a component of the record's assembly, the stop and the still-in-error
sentence name the assembly too. For example: *close RangeBox and them all in SolidWorks without saving (answer No when
SolidWorks asks to save)*. Measure the premise in the 2024 run (§6).

This is not a must-fix for the findings: they rest on the writes, which are proven. It should land before W9c closes.

**Step 3 is as specified.**
- Every document is closed unsaved. The ring loads from its file at 55, against 54 asked, so it is not held and not
  stopped.
- It is routed by way of 53 and rebuilt twice, and ends at 54 with nothing in error.
- The mark is gone, the four gear mates are remade, and the footer is quiet (log 11:452).
- Whether the mark went by `read_clean` or by the change does not matter; both are right here.

**Rerun? No.** Run 11 stands for M3 on 2026. For the 2024 run, correct the script first:
- make "modified beyond step 1's parts" a printed fact;
- compare the assembly's own globals across step 2;
- add the measurement in §6.

### 3. `007b3aa`: right

- **The change.** `finish_update` drops a `read_clean` mark only when no failure of the same press names that
  document (`update.py:2266-2269`).
- **The builder's scenario is the right one, and mine was wrong.** In my setup the ring was closed first, so it loses
  its mark with its unsaved entry through the `open_before` path. That happens before (ii) as after it, so my repro
  showed an older loss, not (ii)'s. The builder's ring is left open and repaired, then set again with its rebuild
  raising. That is the real window.
- **Its test fails** on `007b3aa^`'s `update.py`.
- **It changes no section.** It acts only where a marked document is read clean and a failure names it.
  - In M3, step 2's ring is not read clean.
  - Step 3's ring is read clean, and that press has no failure.
- **The 2026 evidence stands for head with it.**

### 4. The findings for 2026

| Finding | Set `_ON_2026` | Rests on |
|---|---|---|
| `UPDATE_INSERTS_A_GEAR` | **True** | 34.1.1: log 5:344 (`9efcb2c`, JSON 094223). 34.0.0: log 8:1311, log 10:453 |
| `UPDATE_BANDS_IN_PLACE` | **True** | 34.1.1: log 5:345. 34.0.0: log 8:1312, log 10:454 |
| `UPDATE_ADDS_A_MODE` | **True** | 34.1.1: log 5:546. 34.0.0: log 8:1518, log 10:661 (inventory follows the add: log 10:639) |
| `UPDATE_REMOVES_A_MODE` | **True** | 34.1.1: log 5:852. 34.0.0: log 8:1840, log 10:983 |
| `UPDATE_MAKES_MATES_WITH_MODES` | **True** | 34.1.1: log 6:280 (`30bf0e9`, JSON 111036). 34.0.0: log 8:2761, log 10:1373, log 11:200 |
| `UPDATE_MAKES_A_NEW_COUPLING` | **stays None** | No legal edit of the fixtures reaches it; nothing was measured |
| `UPDATE_SUPPRESSES_THE_RELIEF` | **stays None** | The call was made script-side only, clean (log 10:1572, JSON `…_facts`); no Update made it |
| `EXTERNAL_REFERENCES_READ` | **stays None** | No positive case could be made (log 10:1633); C4's refusal stands |

**Each comment should carry its caveats:**
- **`UPDATE_INSERTS_A_GEAR`:**
  - It was measured on a hub (a spline to its sleeve). A plain gear added, with a lock or a new mesh, is measured on
    the fake only.
  - An added gear can land in a user component. The app names it after the press, in red; the footer before is
    silent.
- **`UPDATE_BANDS_IN_PLACE`:** giving bands only, after a user feature (the groove). Taking them away is
  `UPDATE_SUPPRESSES_THE_RELIEF`.
- **`UPDATE_REMOVES_A_MODE`:** the first mode included, and the mode showing refused by name.
- **`UPDATE_MAKES_MATES_WITH_MODES`:**
  - It was measured on 28/14/56.
  - A one-tooth-down ring is routed (`landing`). If it is set straight, it stops in the part, and the next press
    stops before any write (M3, log 11).
  - A removal through Update on a gearbox with modes is measured end to end on the fake only.
- **The route candidates.** Log 10:1632 proposes `EXTERNAL_REFERENCES_READ_ROUTE_CANDIDATES_2026`. `findings.py` has
  no such name. Since no positive case was made, add no route finding: write the five candidates that answered
  without error into `EXTERNAL_REFERENCES_READ`'s comment as facts.

**Both revisions.** Nothing differs between 34.1.1 and 34.0.0 in anything measured:
- the interference volumes 1408.364, 160.785 and 392.233;
- the step faces;
- `landing`'s straight facts (run 7 on 34.1.1, runs 8–10 on 34.0.0);
- m4's answers;
- the post-check's off-axis and out-of-step lines.

Only the time differs: `modes` took 20 min on 34.0.0 against 48 on 34.1.1. Cite both in each comment. The app code
differs between them: `887916b` in the morning, `64bec58` and `3a9e592` now. The findings gate writes that are the
same at all three.

**`tests/test_findings.py` should pin, through `_w9a_run`, each of these runs' JSON and log:**
- **Run 10** (`w9c-demo-20261117-143454.json`, snapshot `3a9e592`, `(34, 0, 0)`):
  - `data["proposal"]` for the five True and three None findings;
  - log 10:453, 454, 661, 983, 1373, 1572 and 1633 (each `propose` line's head);
  - log 10:382, 384, 385 and 401 (`fixed`'s result, Hub, bands, resolved);
  - log 10:446 (the quiet second press);
  - log 10:639 and 687 (the inventory after the add, and the footer before N's removal);
  - log 10:1067 (G4 taken out);
  - log 10:170 (landing's fix shown).
- **Run 11** (`…153629.json`, its snapshot string as written, `(34, 0, 0)`):
  - log 11:200;
  - log 11:316, the calls by member exactly;
  - log 11:359, the status and the result;
  - log 11:361 (the FAIL, its `wrote` list exactly `["modified beyond step 1's parts ['RangeBox.SLDASM']"]`) beside
    log 11:309 (the flags before);
  - log 11:452 (step 3).
- **Runs 5 and 6 for 34.1.1** (`…094223.json` `9efcb2c`, `…111036.json` `30bf0e9`, `(34, 1, 1)`): log 5:344, 345,
  546, 852 and 1081, and log 6:280.

### 5. W9c's Done-when on 2026, and what remains

**The Done-when is met on 2026, on the final app code.** Every row of the table above is shown again in run 10 at
`3a9e592`, with gear mates remade with modes in runs 10 and 11. One row is still owed: "confirmed on 2024".

**Before W9c can close, besides the 2024 run:**
1. Set the five findings for 2026, with the comments and pins in §4.
2. Should-fix A (the assembly in the close-without-saving advice), measured in the 2024 run.
3. The known caveat (i) in `W9C-INTERFACES.md` §11. An *unmarked* part with an app feature in error, which the press
   leaves alone, still lets the press write into the assembly and then offers saving. It is pinned as today's
   behaviour. The handoff should carry it as a known limit with its fix, or W9d takes it.
4. The handoff's standing items: Hub landing in a user component is said after the press only; a plain gear added,
   and a removal with modes, are fake-only; M4 is unmeasured, so a removal refuses while any user component is
   present.
5. My notes not taken, all low:
   - the external bevel foreseen in the virtual frame (the second reading's note 3);
   - a recipe A part with a user's `Pitch` dimension inside the app's own tooth-space sketch;
   - `_evaluates` measuring trig units before the M3 stop;
   - a relief op failing before the sleeve is listed as changed;
   - the raise path in `_update_document` dropping what was set (the first review's last note). `007b3aa` covers its
     effect on marks only.
6. The handoff's "W9c at the session's close" bullet:
   - It is stale (it still says `c997e85` and `ff98d5a` are unread, and gives the last whole suite at `0eb0768`).
   - It should name runs 10 and 11 as the 2026 evidence, this addendum, and the 2026 suite (3702 / 10 / 2,
     `tkinter`-only on Linux).

### 6. The 2024 confirming run

**Run the whole of it except `w9b-part`:**
- `landing`, `fixed`, `modes`, `remove`, `remake`, `bands-off` and `m4`, in that order. At about twice 2026's
  per-press time that is roughly 2 h 20.
- `w9b-part` is W9b's, already closed on 2024.
- `fixed` is the one full turning build with its edits. `modes` and `remake` each carry a 2024 finding, and every W9c
  gate is per version, so they cannot be skipped.
- `landing` must run: the ring fault and the route have never been seen on 2024, and the part's sketch solve is
  exactly where versions could differ.
- `remove`, `bands-off` and `m4` are cheap. `remove` is a Done-when row; `m4` records 2024's answers for C4.
- The What's Wrong rules differ on 2024: `WHATS_WRONG_OPENS_IN_UPDATE_WITH_PART_FEATURE_IN_ERROR_ON_2024` is True. So
  the sections where a part is in error during a press must run on 2024: `landing` cases 1, 2 and 10, and `remake`
  M3. Note that the app now stops M3's step 2 before the assembly's rebuild, so the box run 8's path would have shown
  on 2024 should not come.

**Change the script first:**
1. **M3 step 2:**
   - make "modified beyond step 1's parts" a printed fact (assert only that the flags are equal across the press);
   - compare the assembly's own globals (`W.live_globals` on `box.assembly`) before and after.
2. **Measure should-fix A's premise.** Add a step between step 2 and step 3:
   - close only the three part windows (Sun, Planet and Ring), leaving `RangeBox.SLDASM` open, as a user following
     the sentence would;
   - read `documents()`: is the ring still listed? Read its teeth and codes, and every save flag;
   - press once more: does it stop again on the ring held in error?

   Then close everything as now. This decides the wording, and costs one press.
3. Keep the run awake, as the scripts now do. Expect the 2024 What's Wrong box under its standing STOP rule in any
   path not listed above, and treat it as a finding to read, not a script fault.

**Must-fix:** none, for setting the 2026 findings or for the 2024 run, once the script changes in 1 are made.
Should-fix A should land before W9c closes.

### Re-check of `74024a1`, `f4eabf5` and `15bd445` (2026-11-17)

*Read at head `15bd445`. I started no SolidWorks and changed no code.*

- **Suite:** 3705 passed, 10 skipped, 2 failed (the `tkinter`-only pair).
- **The script's self-check:** `probe/w9c_demonstration.py --self-check` reads "0 failed" in a scratch copy.

**`74024a1`: right.**
- *Values:* the five gates are True `_ON_2026`, as my table has them. `UPDATE_MAKES_A_NEW_COUPLING`,
  `UPDATE_SUPPRESSES_THE_RELIEF` and `EXTERNAL_REFERENCES_READ` stay None on 2026, with why. Every `_ON_2024` is
  None.
- *Comments:* each names its log lines on both revisions and carries the caveats from §4: a hub only; Hub's
  interference said after the press; giving bands only; the first mode included; 28/14/56, with M3; removal with
  modes fake-only. The five external-reference calls are recorded as facts, not as a route.
- *The pins really pin.* In a scratch copy I flipped two things:
  - `UPDATE_ADDS_A_MODE_ON_2026` to None: three tests fail, the values test and both log tests;
  - one byte of log 11:316 (`'OpenDoc6': 8` → 9): the 34.0.0 test fails.
- *The `w9c_unmeasured` fixture.* In the eleven tests only the signature changed; every body is as it was, so none
  asserts less about what it tests. The one renamed (`test_each_step_reads_its_own_gate_…`) used to pin "None as
  committed". That pin now lives in `test_findings.py`, against the new values.
- *The open-gate path on 2026, as committed.*
  - The round trips take the `measured` fixture, which patches the 2026 gates True. That is now exactly the committed
    state, so those tests run the real 2026 configuration.
  - Nothing yet asserts the committed gate list itself. Note: add one test, without any fixture, that
    `swbuild.in_place_gates(every, Y26, modes=True, remakes=True)` is `[(STEP_COUPLING,
    "UPDATE_MAKES_A_NEW_COUPLING_ON_2026")]` and Y24's is the six. I ran it: it is so today.

**`f4eabf5`: right, Tk-side only.** The diff touches `ui_text.py` (`_close_unsaved`, `still_in_error_sentence`, the
stop's and the footer's wording) and adds `update.assembly_holding`. No worker call changes. The sentences read
correctly in the states that make them:
- step 1's stop: "close them all and RangeBox … answering No …";
- step 2's still-in-error sentence: "close it and RangeBox …";
- the footer's unsaved line.

The assembly is not named twice when it is among the documents changed. A part outside the record's assembly is told
as before. The edge states:
- *The assembly not open in SolidWorks.* Telling the user to close it is harmless ("when SolidWorks asks" is
  conditional), so nothing is untrue.
- *A part in two gearboxes' assemblies.* Only the record's own assembly is named. If the other assembly is also open,
  it too keeps the part loaded. Note: rare, and the next press would stop again and say so.
- *The user's own unsaved work in the assembly (or a part) from before the Update.* Closing without saving loses it,
  and nothing says so. "The files on disk are as before this Update" is true but does not warn. Nothing elsewhere
  warns either: the app reads no save flag of an unmarked document at a press's start.
  - This is older: the parts' sentence always had it. `f4eabf5` widens it to the assembly, where a user's unsaved
    mates are more likely.
  - *Should-fix, low:* add "(anything you changed there yourself and did not save is lost too)". Or, better, read
    the assembly's `GetSaveFlag` in the check phase and say it only when the assembly was already modified before the
    press. It is not needed for the 2024 run.

**`15bd445`: right, with one ordering advice for the 2024 run.**
- **"Beyond step 1"** is now a printed fact (`beyond_step_1`). The strict check is the comparison across the press
  (`wrote_in_press`), which now includes the assembly's own globals. That closes the one gap I named.
- **Step 2b:**
  - *How it closes.* `quit_named_in` closes exactly Sun's, Planet's and Ring's documents, by file name under the
    copy's folder, with `QuitDoc` by title. It cannot close the assembly or the user's parts.
  - *The macro database's record:* `QuitDoc` closed modified parts and assemblies with no dialog on 2026 and 2024
    (`documents/02`). The CAM add-in's Yes/No box came only for 2024-saved assemblies opened in 2026, which 2024's run
    does not do.
  - *What is unmeasured.* `QuitDoc` on a part loaded as a component of an open assembly is not measured anywhere,
    which is the point of the step. It runs as a worker job under the run's dialog watch. A box there would be the
    §0.3 STOP, and that would end the run there.
  - *Ordering advice:* in the 2024 run, put `remake` last, after `bands-off` and `m4`. A STOP in 2b then costs only
    step 3, which is not gate evidence.
- **The step tells the outcomes apart.** It records three things before its press:
  - `held` (`documents()` under the folder);
  - every save flag;
  - the ring's codes and teeth, where it is still held.

  Then its press is either `stopped_again` (failures naming the ring alone, `skipped` said), in which case it must
  have written nothing (`wrote_in_press`), or it is a fact. So "the part stayed loaded in error and the press stopped
  again" and "SolidWorks dropped the part's changes" read differently: in the first, `held` lists the ring at 72/54;
  in the second, it does not, or the ring reads 55 and clean.
- **It cannot spoil steps 2 and 3.**
  - Step 2's data and checks are taken before it.
  - If its press goes through, because the ring was dropped, it routes and remakes in memory. Step 3 then closes
    everything unsaved and presses again on the files at their old values, as before, so step 3's checks hold either
    way.
- **The self-check** patches the 2026 gates to None in its own process to judge the refusal steps as 2024 meets them.
  That is right. The run itself handles a gate already True: `gated_refusal` prints "already True in findings.py, so
  the app refuses nothing here" as a fact. Note: that branch is not self-checked; a one-line case would cover it.

**4. Does the 2026 evidence stand for head `15bd445`? Yes.**
- `src` changed since the runs only in:
  - `findings.py` values;
  - Tk-side wording (`f4eabf5`);
  - `007b3aa` (Tk-side, reviewed).

  No worker call changed.
- **"Patched True in the script's process" and "set True in `findings.py`" behave the same for every reader.** Every
  reader of these gates (`swbuild.in_place_gates`, the ruling 9.16 lift, the footer's `in_place_ahead`, and
  `ui_text`'s step names) reads `getattr(findings, f"{name}_ON_{year}")` at the time of the call. None copies a value
  at import, so a patch is seen exactly as a committed value would be. The years map from the revision, 34.x to 2026,
  so 34.0.0 and 34.1.1 alike.
- **What the runs did differently from a real user:**
  - Each measured press ran with only its own step's gates patched. A real 2026 press has all five open at once. No
    measured press needed a gate it did not have patched, so the same writes run. The footer's foresight with all
    five open is what the round trips' `measured` fixture exercises on the fake.
  - Each measured press followed a recorded refusal (the gates as they stood) on the same record. A real user's
    record has none, which is a simpler state: the refusal on record is said only until the workbook changes, and the
    press replaces it.

  Neither difference is a code path the runs missed.

**No must-fix before the 2024 run.** Run `remake` last there.
