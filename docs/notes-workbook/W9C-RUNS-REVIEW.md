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

*Independent, 2026-11-18, at `f7c2f0d`. I started no SolidWorks and changed no code.*

- *What I read:* `06d5141`'s four logs and their JSON, every line, and the note's section "The confirming run on
  SolidWorks 2024"; checked against run 10 and run 11 (34.0.0) check line by check line, and against the rulings on
  What's Wrong (`ISSUE-1-PLAN.md`, its last two sections; `W9A-CLOSE-2024-REVIEW.md`).
- *Citations:*
  - `24-1:` `w9c-demo-sw2024-20261117-1-landing-fixed-modes-memory-stop.log` (JSON `…-171926.json`);
  - `24-2:` `…-2-remove.log` (`…-192454.json`);
  - `24-3:` `…-3-bands-off-m4.log` (`…-194351.json`);
  - `24-4:` `…-4-remake-whats-wrong-stop.log` (`…-195231.json`);
  - `log 10:` and `log 11:` as in the 2026 parts above.
- *Snapshot and version:* each log's line 2 states snapshot `4315774` and its line 4 attaches 2024 revision 32.5.0
  (PIDs 27368, 64480, 75080 and 66428, each 0.50 to 0.68 GB at attach). Each JSON holds `revision [32, 5, 0]` and
  `snapshot 4315774`. `open before: []` in every log.
- *Suite at `f7c2f0d`:* 4099 passed, 1 skipped, 1 failed (the known font-width test).
- *The script's self-check at `f7c2f0d`* (scratch copy): 88 ok, 1 failed (§2 below; the run itself is not touched by
  it).

**Verdict.**

- **The six sections that ran whole are sound evidence for `4315774`'s `src`, and for head's gated writes.**
  landing, fixed, modes, remove, bands-off and m4 are 0 failed with no STOP inside them. Every check line run 10
  printed is printed here too (numbers masked), and every traced press made the same calls by member as on 2026. The
  extra checks are the masters this run built. No check passes on nothing, and each proposal is printed from the
  checks' own results.
- **remake's first part is sound, and M3 stopped where the note says.** Its proposal stands. M3's step 1 is shown;
  steps 2, 2b and 3 are not measured on 2024.
- **The note says one thing the logs contradict, and it matters for the ruling: the What's Wrong box did not go
  after 60.11 s. It was still up then.** Smaller points follow in §1.
- **The 2024 evidence carries over to head for every gated write** (§2). The one SolidWorks-side change on an
  Update's path since `4315774` is a read: the inventory now also reads each user mate entity's kind. It has
  never run on 2024 inside an Update.
- **The five findings may be set True on 2024; the other three stay None** (§3).
- **Must-fix:**
  - before the 2024 findings commit cites the note: correct its What's Wrong sentence (§1);
  - before `remake` runs again on 2024: the script's step 2 check holds the ring to code 72, which 2024 never reads,
    so it would fail on a harmless fact (§4).

### 1. Section by section

- **`landing`** (24-1:11-910, 107 ok, 0 failed). It also built `rangebox.master`: 15 checks that run 10, reusing
  masters, did not run (24-1:14-750).
  - The fix is shown: every foreseen change routed clean, every unforeseen one set straight clean, the leftover
    clean (24-1:909, 812).
  - Routed one tooth down by way of 54 and 53 (24-1:799, 902): clean.
  - Set straight, 55 → 54 and 56 → 55 still fail (24-1:807, 814). The short line's solved end lies past the origin,
    as on 2026 (24-1:810, 817), so the cause reads the same. Only the code differs: Tooth Space and Teeth read 51 and
    51, where 2026 read 72 and 1 (log 10:70, 77).
  - **Case 10 differs too, and the note does not say so.** The user's cut reads code 51 before the set (24-1:905),
    where 2026 read 71 (log 10:166). The route and the outcome are as on 2026: both legs `[False, False]`, ending at
    54, the user's cut the only feature in error (24-1:902).
- **`fixed`** (24-1:911-1318, 122 ok, 0 failed). It also built the user parts and `setup.master` with its M1/M2
  reads and inventory (24-1:913-1035). The checks are run 10's, line for line:
  - the gates refuse first, with nothing written;
  - the Update ends ok (24-1:1243);
  - Hub is built, inserted and mated (24-1:1245), the bands are given (24-1:1246), and Hub reads resolved in every mode
    (24-1:1262);
  - the step faces land to 1e-4 on F0, with `GetArea` 114.303 and 114.295 kept as facts, as on 2026 (24-1:1255-1259);
  - each mode is §3's (24-1:1266-1274), and the second press is quiet with every save flag False (24-1:1308);
  - it proposes the two findings True (24-1:1316-1317).

  Its five traced presses made the same calls by member as run 10's.
- **`modes`** (24-1:1319-1854, 80 ok, 0 failed). The 80 check lines are run 10's 80.
  - H2 is added, and the inventory names H2 where SolidWorks reads each user mate on (24-1:1502-1503).
  - The footer after the add names no user mate suppressed in H2 (24-1:1554).
  - N is deleted with the lost flag said (24-1:1683), the mode showing is refused (24-1:1719), and H, the first mode,
    is removed (24-1:1836).
  - It proposes both findings True (24-1:1527, 1853).
  - *Memory, a fact for the rule.* The watch set its memory STOP at 24-1:1680 (1.90 GB free), between N's removal and
    the mode-showing refusal. The section ran on, by the script's rule ("before the next section",
    `w9a_demonstration.py:79`). H's removal started at 1.77 GB free and ended at 0.94 GB (24-1:1755-1758). Its
    checks all passed, and the run ended after the section (24-1:1855).
- **`remove`** (24-2, 58 ok, 0 failed). It built `reducer.master` (12 extra checks). G4 is taken out with each
  mate read gone by name (24-2:625), and C6's entry is dropped (24-2:626). The HighDog refusals are as in run 10.
- **`bands-off`, `m4`** (24-3, 13 and 7 ok). The check lines are identical to run 10's.
  - The relief call is made script-side only and reads clean (24-3:94).
  - The same five reference reads answer without error (24-3:153), and no positive case is made (24-3:154).
- **`remake`, the first part** (24-4:11-203, 0 failed).
  - The refusal and the change press made exactly run 11's calls by member (24-4:74, 103; log 11:74, 103).
  - The four gear mates are remade with modes (24-4:180), the user's items are kept (24-4:181), every flag is right
    (24-4:190), and L reads 3.0 (24-4:199).
  - The post-check's out-of-step and off-axis lines are run 11's (24-4:106-108).
  - It proposes the finding True (24-4:203).
- **`remake`, M3 step 1** (24-4:248-309) is as on 2026, with the same calls (24-4:256).
  - It stops in the ring, and the record marks it (24-4:308).
  - The stop names RangeBox and says to answer No (24-4:309).
- **What's Wrong before step 2** (24-4:310-318). The box came 0.47 s into the script's own `read_now` of the
  assembly, the worker in `ActivateDoc3`, owned by SolidWorks' frame.

**Is each "0 failed" real?** Yes.
- Every `ok` line of run 10's landing, fixed, modes, remove, bands-off and m4 has its twin in 24-1 to 24-3, with
  numbers masked. None is missing.
- Each `propose` is `proposed(...)` over the `clean` dict its checks built (`w9c_demonstration.py` 2027-2033, 2169,
  2306, 2497). Each 2024 evidence dict reads all True.
- The four sections' interference checks judge pairs read from SolidWorks after each press, in every mode.

**What the write-up says that the logs do not bear out:**

1. **"The box went by itself after 60.11 s, against the ruling's 60 s."** It did not go.
   - The fact line reads "came at [0.47] s, stayed [] s; after the job it took 60.11 s to go (allowed 60); **1 up at
     the end**" (24-4:313). The JSON's `whats_wrong_lifetimes` holds `stayed []` and `still_up 1`.
   - `whats_wrong_end` waits while the box is up for at most 60 s, and then prints the time it waited as "took … to
     go" whether or not the box went (`w9a_demonstration.py:353-382`).
   - So the box outlived the read by more than 60 s. Nothing logged says it ever went. The commit message repeats
     the error and cannot be changed; the note can.
2. *"It was then killed, since it would not close with the copy's changed parts open"* is not in the log. The log
   says the worker was marked hung, nothing was closed, and SolidWorks was left as it stood (24-4:321). Say it as the
   operator's account.
3. *"§0.3's STOP":* the log names W8-PLAN §0.5 (24-4:315). Trivial.
4. *"Each section took 2.5 to 3.5 times as long as on 2026."*
   - landing: 987 s against 824 (1.2 times, and 2024's also built a master);
   - modes: 3886 s against 1115 (3.5);
   - bands-off: 405 s against 101 (4.0);
   - m4: 35 s against 17 (2.1);
   - fixed and remove also built masters on 2024.

   Say "1.2 to 4 times, three of them building their masters too".
5. *"14.69 GB at its peak":* 14.76 GB is logged (24-1:1758).
6. **remake's memory is understated.** The watch's STOP line came at 24-4:98, at 7.30 GB private and 1.94 GB free,
   during the change press.
   - remake was the session's only section, and the guard acts between sections, so M3 ran after it at 2.71 GB free
     (24-4:251).
   - The `done` line does not count that STOP (24-4:329).
   - The note says only that remake "reached 7.3 GB … and fell back to 2.0 GB".
7. *"code 51 twice (`swSketchErrorExtRefFail`)":* the name says a cause nobody measured. 51 is what 2024 has given
   for every feature error seen:
   - W5's over-defined mates (`findings.py:563-566`, "never reads meaning into the number");
   - W9a's Sprocket-1;
   - here, the ring and the user's cut.

   Say "51, the number 2024 gives for any feature in error".
8. **The interference volumes are described as SolidWorks against the app, but the difference is narrower.**
   - The app's own reads agree with SolidWorks' in every mode but one per press: N in fixed's press (374.463 against
     392.129, 24-1:1281) and H2 in modes' press (152.629 against 160.748, 24-1:1520). Both are the RangeSlv–Sprocket-4
     pair, 4.5 % and 5.1 % low.
   - modes' own press read N at 392.129 (24-1:1404). The pairs were right in every mode (24-1:1521, 1847).
   - Across versions, 1408.381 against 1408.364 is a kernel difference with both sides agreeing within each version.
   - The cause of the low reads is not known.

### 2. Does the evidence stand for today's head?

`git diff 4315774 f7c2f0d -- src` adds 4601 lines, almost all W9d's carry: Build again's read R and carry C, the
record's schema 10 and the sentences. On an Update's path, call by call:

- **`Session.mate_info`**, in the inventory read of every Update with user mates (`swbuild._read_user_work`). Each
  entity now also reads:
  - `IMateEntity2.ReferenceType2`;
  - for a feature, `Reference` then `Name`;
  - for a datum plane, the component's `GetModelDoc2` and a feature walk (`FirstFeature`, `GetTypeName2`,
    `GetNextFeature`, `Name`) to the third `RefPlane` (`swcom.py` `_entity_kind_read`, docstring "UNMEASURED as
    written here").

  Every failure becomes `("unread", "")`. The result goes only into `UserMate.entities` and the record (D5).
  `whole` and every judgement of the Update are computed as before, and `.entities` is read only by W9d's carry
  (`swbuild.py` 7098 onward).
  - *Fact:* the calls were measured one by one on 2024 by W9c's probes, marking nothing.
  - *Fact:* the combination ran inside an Update on 2026 only (W9d run 1's fixture, `w9d-demo-sw2026-20261117-1-…`
    line 90).
  - *Inference:* they cannot change a gate's outcome on 2024. Their side effects there (a mark, a box, time, memory)
    are unmeasured.
- **`swcom._read`** now calls a member that late binding hands back uncalled, under the COM-error guard.
  `GetSaveFlag`, `GetType`, `GetTypeName2` and `GetConfigurationNames` go through it. These are the same members in
  the same order; only the wording of a COM error changes.
- **`find_component`** gains `suppressed_ok`, False by default. No Update path passes it.
- **`finish_update`** calls `_follow_carry`, which returns at once on a record with no carry. Every W9c record has
  none.
- **The record is written at schema 10.** A W9c-era record of schema 9 (this run's masters) reads forward.
- **`build_gearbox(carry=None)`** is W9a's call for call. It is used here only to build masters.
- **`ui_text`** (`9cbfc08`, `0b7582f`): the close-without-saving parenthesis now says what closing the assembly
  costs. M3 steps 1 and 2 and the footer carry it.
  - I ran the script's predicates on head's sentence: `footer_says_close`, `status_alone`, `says_close_with_assembly`,
    "set nothing" and "still open in SolidWorks" each hold.
  - The self-check's one failure is its verbatim sample `apps == still` (`w9c_demonstration.py:1258`), which still
    holds the old parenthesis. `W9D-REVIEW-B` noted it.
- **No hunk touches `update_gearbox`, `_update_motion`, the in-place steps, `in_place_gates` or the finish of
  W9c's writes.** Nothing that W9d adds redefines a name the Update calls (no duplicate `def` in `swbuild` or
  `swcom`).

**So the 2024 evidence carries over to head for every gate:**
- inserts, bands, adds, removes and remakes make the same writes in the same order;
- the refusals and the held-in-error stop are unchanged.

What head adds on 2024 that no run has shown is the inventory's entity reads. A `remake` rerun from head (§5)
measures them on 2024 at no extra cost: its every press reads the inventory, and the script's flag brackets would
catch a mark.

### 3. The findings for 2024

| Finding | Set `_ON_2024` | Rests on |
|---|---|---|
| `UPDATE_INSERTS_A_GEAR` | **True** | 24-1:1243, 1245, 1262, 1308, 1316 |
| `UPDATE_BANDS_IN_PLACE` | **True** | 24-1:1246, 1259, 1317 |
| `UPDATE_ADDS_A_MODE` | **True** | 24-1:1502, 1503, 1515, 1527 (no user mate said suppressed in H2: 1554) |
| `UPDATE_REMOVES_A_MODE` | **True** | 24-1:1683, 1719, 1725, 1836, 1853 |
| `UPDATE_MAKES_MATES_WITH_MODES` | **True** | 24-4:103, 180, 181, 190, 199, 203 |
| `UPDATE_MAKES_A_NEW_COUPLING` | **stays None** | No legal edit reaches it; nothing measured on either version |
| `UPDATE_SUPPRESSES_THE_RELIEF` | **stays None** | The call was made script-side only, clean (24-3:94, JSON `…_facts`); no Update made it |
| `EXTERNAL_REFERENCES_READ` | **stays None** | No positive case (24-3:154); the five reads answered, as facts (24-3:153) |

**`UPDATE_MAKES_MATES_WITH_MODES_ON_2024` may be set without the M3 rerun.** M3 is not this gate's evidence:
- step 1 stops in a part before any mate is made;
- step 2 is the held-in-error stop of the check phase, version-free code shown on 2026;
- step 3's remake is the same write as the first part's.

The rerun is owed for the stop's behaviour on 2024 and for should-fix A's premise, not for the gate.

**Each 2024 comment should carry, beside the 2026 caveats it repeats:**
- **All five:**
  - measured at `4315774` on 32.5.0;
  - head's Update also reads each user mate entity's kind (W9d D5), which has not run inside an Update on 2024 and
    judges nothing (§2);
  - SolidWorks 2024's first press on a freshly opened RangeBox grew it by 3.3 to 4 GB, held until the assembly was
    closed (§4).
- **`UPDATE_INSERTS_A_GEAR`:**
  - a hub only;
  - the interference is said after the press;
  - on 2024 one pair's volume read 4.5 % low in one mode of the press (24-1:1281), with the pairs right.
- **`UPDATE_BANDS_IN_PLACE`:** giving only; the step faces as on 2026 (24-1:1255-1259).
- **`UPDATE_ADDS_A_MODE`:** H2's volume read 5.1 % low (24-1:1520), with the pairs right.
- **`UPDATE_REMOVES_A_MODE`:**
  - the first mode included, the mode showing refused by name;
  - H's removal ran under 2 GB free (24-1:1755-1758) and passed.
- **`UPDATE_MAKES_MATES_WITH_MODES`:**
  - measured on 28/14/56.
  - On 2024 M3 is shown to step 1 only: the set-straight press stops in the ring and names RangeBox (24-4:255,
    308-309).
  - The press made again without closing is not measured on 2024. What's Wrong came at the script's activation of the
    assembly with the ring in error and outlived it (24-4:310-314).
  - A removal with modes is fake-only.
- **`EXTERNAL_REFERENCES_READ`:** the five candidates of 24-3:153 as facts, as for 2026; no route finding.

**The pins** (`tests/test_findings.py`, through `_w9a_run` with snapshot `"4315774"` and `(32, 5, 0)`; line 4 of
each log reads `attach  SolidWorks 2024 (revision 32.5.0)`, which `_w9a_run` accepts):
- **24-1 with `…-171926.json`:**
  - `data["proposal"]` for the four True;
  - lines 909, 1243, 1245, 1246, 1262, 1308, 1316, 1317, 1502, 1527, 1554, 1683, 1719, 1836 and 1853 (each line's
    head);
  - 807 and 814 for the codes `[('Tooth Space', 51), ('Teeth', 51)]`, as a fact.
- **24-2 with `…-192454.json`:** line 625.
- **24-3 with `…-194351.json`:**
  - the proposal's two None;
  - lines 94, 153 and 154.
- **24-4 with `…-195231.json`:**
  - the proposal's True;
  - line 103's calls by member exactly;
  - lines 180, 181, 190, 199, 203, 255, 256, 308 and 309;
  - the JSON's `whats_wrong_lifetimes` (`stayed []`, `still_up 1`) beside line 313.
- **The gate list.** Add the re-check's test with no fixture, asserting the committed gate list. With the five set,
  `in_place_gates(every, Y24, modes=True, remakes=True)` and Y26's are each `[(STEP_COUPLING,
  "UPDATE_MAKES_A_NEW_COUPLING_ON_<year>")]`.

### 4. The measured differences from 2026

- **The straight one-tooth-down ring fails with 51 on 2024, 72 on 2026.**
  - *App:* nothing in `src` reads the number. The landing foresight works from the globals, the stop from the rebuild's
    result and the record's mark (`grep`: 72 appears only in `gears/landing.py`'s docstring, as run 6's fact).
  - *Sentences:* none says a code.
  - *Tests and the fake:* `tests/test_swbuild_landing.py:88-90, 234`, `tests/test_swbuild.py:503` and
    `tests/test_workbook_in_place_round_trip.py:1232-1361` make the fake answer 72, 2026's value. They pin the fake,
    not a decision.
  - *Note, low:* `landing.py`'s docstring should add "51 for both features on 2024".
  - **The script depends on it: a must-fix before the rerun.** `wrote_nothing` appends "the ring reads …, not Tooth
    Space at 72 and 54 teeth" whenever Tooth Space is not 72 (`w9c_demonstration.py:738-739`). On 2024 step 2 would
    therefore fail on the code alone.
    - *Fix:* hold the ring after against the ring before (`ring_before` is already read in `read_all`): the same codes
      and 54 teeth.
    - Say the codes as a fact.
- **The interference volumes.**
  - *Fact:* the app says the volume in its status and its CHECK lines, and W9d's carry says it in a clash sentence
    (`ui_text.py:5959`). Nothing compares a volume or acts on it. `Clash` sums per pair, and the demonstration and
    the app judge pairs.
  - *So nothing the app tells the user rests on the two reads agreeing,* beyond the number printed. On 2024 that
    number can be some 5 % off what SolidWorks' own Interference Detection shows the user afterwards.
  - The handoff should say so. It is not a W9c blocker.
- **14 GB private in `modes`.** The largest steps are the app's own presses.
  - The first press on a freshly opened copy grew SolidWorks 2024 by 3.3 to 4 GB, a refused press included, though it
    only reads:
    - setup's quiet press, 6.69 → 10.01 GB (24-1:990-991);
    - modes' refused H2 press, 8.46 → about 12.5 (24-1:1372, 1400);
    - remake's refused press, 3.59 → 7.09 (24-4:70, 97).
  - Later presses on the same open copy added 0.3 to 1 GB each, and the script's reads between them about as much.
  - All of it came back only when the copy was closed: remake, 7.35 → 2.03 GB (24-4:99, 251).
  - On 2026 the whole run stayed under 2.3 GB.
  - *So it is a path a real user's Update takes.* The 14 GB is the script's six presses and per-mode reads on one copy
    kept open, which a user doing several Updates in one sitting could repeat.
  - *The handoff should tell the user:* on SolidWorks 2024, an Update of a gearbox with modes can take SolidWorks
    3 to 4 GB more memory, kept until the assembly is closed. On a machine with little free memory, save and close
    the assembly between rounds of Updates, or restart SolidWorks. The app does not watch memory.
  - *For the script:* the guard acts only between sections, so on 2024 a section ran to 0.94 GB free. It could check
    before each press. That is the coordinator's call, and not needed for the rerun if it starts fresh with no other
    SolidWorks running (session 4 attached at only 3.70 GB free).

### 5. `remake`'s M3 on 2024: the ruling, the script, the rerun

**What the rules say.**
- The ruling (`ISSUE-1-PLAN.md`, 2026-11-17) makes the frame's box a fact during any job, provided it goes within 60
  s of the job's end with the frame enabled. It lists "a box that outlives its job (never seen)" as not measured and
  not relied on.
- `W9A-CLOSE-2024-REVIEW` §6 measured every box going while SolidWorks kept working. Its only script-step case,
  s4:115-118, showed the box at `ActivateDoc3` going 1.05 s later during the step's own `ForceRebuild3`.

**What happened here.**
- `read_now` activates and rebuilds nothing, so nothing came after the activation to take the box down.
- This is the first box to outlive its job.
- Raising the allowance would not help: nothing says this box goes by itself at all.

**The app may meet the same box (inference from the code, not measured).** `Session.open_document` always follows
`OpenDoc6` with `ActivateDoc3` (`swcom.py:3601`). The trace counts `OpenDoc6` and not `ActivateDoc3`, and step 2's
press opened 8 documents on 2026 (log 11:316), the assembly among them. So on 2024 the app's own step-2 press, made
with the ring held in error, may raise the same box and leave it standing after the press. A user who presses
again without closing would then see a What's Wrong that does not go by itself.
- No W9a sentence promises otherwise there: `WHATS_WRONG_AHEAD` is keyed on the user's work in error.
- Still, it is the case the ruling never measured. The rerun should be allowed to measure it rather than stop on it.

**Recommended ruling.** On a version where What's Wrong shows (2024):
- a What's Wrong owned by SolidWorks' frame, the frame enabled, that is still up 60 s after a job ends (the script's
  own step or the app's press) is logged as having outlived its job;
- for an app job, that is a fact the ruling and W9a's sentences must take;
- the script then closes it with the box's own Close button, as a person would, never FeatureXpert or the check box,
  and the box must be gone within 10 s with the frame still enabled;
- a box that blocks (frame disabled, or the 120 s stall), one not owned by the frame, one that will not close, and any
  other window stay the STOP.

Close repairs nothing and changes no setting. That makes it the one control in the box a person uses after an
activation.

**The exact script change** (reviewed before the run):
1. In `w9a_demonstration.py` `whats_wrong_end`, after the allowance loop, behind a flag that W9a's own script leaves
   off (`WW_CLOSE_LEFT = False` there; set True in `w9c_demonstration.main`):
   - when `up`, `enabled is not False` and no `unowned`, call `W.press_dont_save(h, ("&Close", "Close"))` for each
     box up;
   - poll `whats_wrong_boxes` for up to 10 s;
   - record `outlived: True`, `closed_by_script` and the seconds in `RESULT["whats_wrong_lifetimes"]`;
   - say the fact line;
   - re-read `up` and `enabled` before the existing STOP test.
2. In `w9c_demonstration.py`, `wrote_nothing` takes `ring_before` and checks the ring after against it (the same
   `in_error`, 54 teeth) in place of the literal 72.
3. The self-check: replace the stale `still` sample with head's sentence, and add a case with codes 51 and one for
   the close path's judgement.
4. *Optional, saves about 20 minutes and the first part's memory peak:* a section `remake-m3`, by name only, that
   runs `remake_again` alone (`FOLDERS["remake-m3"] = ["remake-again"]`). Its presses read the inventory too, so it
   still measures §2's reads.

**The rerun.**
- From a `git archive` of head once those land, in a fresh SolidWorks 2024 session with no other SolidWorks running,
  in a new run folder.
- The command line:

```
python.exe RUN\snap\probe\w9c_demonstration.py RUN\snap\src RUN\out --pid PID ^
    --log RUN\w9c-demo-sw2024-5-remake-m3.log --sections remake-m3 ^
    --user-master <probe folder>\w9c-confirm-sw2024-20261117-171854\out\setup.master
```

- Without item 4, use `--sections remake` (about 26 minutes on 2024).
- `setup.master` was built at `4315774`. A build at head makes the same files (§2), and its schema 9 record reads
  forward as a user's would.

**Step 2b on 2026.**
- *What it decides:* whether the advice must name the assembly at all. That advice now tells the user it discards
  whatever else is unsaved in the assembly (`9cbfc08`).
- *Why it matters:* the premise, that a part closed alone stays loaded in error, is reasoned, not measured on either
  version, and it costs the user real work when they follow it.
- *The cost on 2026:* `--sections remake` took 697 s in run 11, and M3 alone would take about half that.
- *Recommendation:* run it on 2026 in the same session as the W9d run's end, before W9c closes. Carrying it as a
  caveat is acceptable only if the coordinator rules the wording stands either way.

### 6. What remains before W9c can close

Taking in part 5's list and the re-check, with what W9d's package B has since taken marked as taken.

1. **Correct the note's 2024 section** (§1, items 1 to 8): above all, the box did not go.
2. **Set the five 2024 findings** with the comments and pins of §3, and the no-fixture gate-list test (the re-check's
   note, not yet taken).
3. **Rule on a What's Wrong that outlives its job** (§5). Land the script's must-fix (the 72) and the close rule with
   the self-check, reviewed. Then rerun `remake` (or `remake-m3`) on 2024 from head. This measures steps 2, 2b and 3
   there, and head's inventory reads.
4. **Step 2b on 2026** (about 12 minutes), or the caveat by ruling (§5).
5. **Should-fix A** (part 5 item 2):
   - the wording landed in `f4eabf5`;
   - *taken by package B:* the re-check's low should-fix, that closing the assembly loses the user's own unsaved work,
     is now said inside the parenthesis (`9cbfc08`, `0b7582f`);
   - its premise is item 4.
6. **If the rerun shows the app's step-2 press leaving What's Wrong up on 2024:** the ruling's not-measured list, and
   W9a's sentences if they are said there, take it.
7. **The handoff:**
   - the 2024 memory advice (§4) and the interference-volume caveat;
   - part 5's item 3, caveat (i) in `W9C-INTERFACES.md` §11, still open and not taken by W9d;
   - item 4's standing items;
   - item 6: the stale "W9c at the session's close" bullet. It should name runs 10 and 11 and this 2024 run as the
     evidence, and the suites, now 4099 / 1 / 1 at `f7c2f0d`.
8. **Low:**
   - part 5 item 5's notes, unchanged;
   - the re-check's notes: a part in two gearboxes' assemblies, and `gated_refusal`'s "already True" branch not
     self-checked, which the 2026 gates now take in every 2026 run;
   - `landing.py`'s docstring on 51;
   - the 2026 run-10 section of `W9C-DEMONSTRATION.md` writes its run folder under the Windows account folder,
     where the house form is `<probe folder>\…`.

*Done already:* part 5's item 1 (`74024a1`, the 2026 findings).

### Re-check of `c5f113a`, `d0e32bb` and `b1230ab` (2026-11-18)

*Independent, 2026-11-18, at `b1230ab`. I started no SolidWorks and changed no code; values were flipped and the
close path driven only in a scratch copy (`git archive b1230ab`), deleted after.*

- *What I read:* the three diffs against this addendum; the four 2024 logs and their JSON again where a claim rests
  on them; `w9a_demonstration.py`'s What's Wrong harness and W8's `press_dont_save` and watch; `remake_again`;
  `ui_text`'s two What's Wrong sentences and where they are said.
- *Suite at `b1230ab`:* 4101 passed, 1 skipped, 1 failed (the known font-width test).
- *Self-checks at `b1230ab`:* W9c's 96 ok, 0 failed; W9d's 0 failed (it reads W9c's pure head).

**Verdict.** The three commits do what the addendum asked, and the script is **fit for the 2024 `remake-m3` run**
with `--close-outlived-whats-wrong`. I found no must-fix. Five should-fixes and two points for a ruling follow; the
first should-fix decides whether the close path can work at all, but if it cannot, the run only stops where 06d5141
stopped.

#### 1. `d0e32bb`: the five gates, their comments and pins

- **Values.** `UPDATE_INSERTS_A_GEAR`, `UPDATE_BANDS_IN_PLACE`, `UPDATE_ADDS_A_MODE`, `UPDATE_REMOVES_A_MODE` and
  `UPDATE_MAKES_MATES_WITH_MODES` are True on 2024; the coupling, the relief and the references read stay None with
  why. That is §3's table.
- **Comments.** Each carries §3's caveats with the lines §3 names: measured at `4315774`; the entity-kind reads not
  run inside an Update on 2024; the 3.3 to 4 GB first press (24-1:990-991, 1372, 1400; 24-4:70, 97); the two low
  volume reads with the pairs right (24-1:1281-1282, 1520-1521); H's removal under 2 GB free; M3 shown to step 1 only,
  the box having outlived its job, and M3 not the gate's evidence. I checked every number quoted there against its
  line. "14.7 GB private" for H's removal is 14.69 at its start and 14.76 at its end (24-1:1755, 1758).
- **Pins.** `test_w9c_gates_on_2024_rest_on_the_confirming_run_on_32_5_0` holds every line §3 asked for, the four
  JSON proposals, 24-4:103's calls by member equal to run 11's, and `whats_wrong_lifetimes` beside 24-4:313. In the
  scratch copy each of these failed the tests, one at a time: a gate set None (inserts, bands), the relief or the
  references read set True, 24-1:1245, 24-1:807's codes, one line dropped from 24-1 (every later number shifts),
  24-2:625, 24-3:94 and 153, 24-4:180 (inside its pinned prefix), 256's counts, 308, 313, 314, line 2's snapshot,
  and the JSON's proposal or snapshot. *Not pinned, though the comments cite them:* 24-1:1503, 1515, 1725, 1255,
  1259, 1282, 1521, 1755 and 1758 (each changed and the tests passed). §3 did not ask for them; they are the
  evidence column of the adds and removes gates, so pinning 1503, 1515 and 1725 would be cheap (should-fix 4).
- **No test asserts less.** The one test given `w9c_unmeasured`
  (`test_while_the_references_read_is_unmeasured_any_user_component_refuses_a_removal`) asserts exactly what it
  did; its last line needs a 2024 gate None and now says so. The self-check's patch of 2024's gates to None is
  harmless and also idle: every gate judgement in it uses `rev = (34, 1, 1)`, so no line of it reads a 2024 gate.
- **The no-fixture test's list is right, its words are not.** For its `every` (bands *given*), the committed gates
  leave only `UPDATE_MAKES_A_NEW_COUPLING_ON_<year>` on each version, as asserted. But its docstring says every
  step but a new coupling is measured; bands taken away or given back still meet `UPDATE_SUPPRESSES_THE_RELIEF`,
  None on both (should-fix 3).
- **The real 2024 configuration is not exercised end to end on the fake.** No committed test runs an in-place write
  on a fake at (32, 5, 0) with the committed values: the in-place write tests use `measured`, which patches 2026,
  and the one 2024 fake test is a removal, which reads no W9c gate. In the scratch copy I ran four such writes at
  (32, 5, 0) with nothing patched (a mode added and one removed on `tc_built`, Hub inserted, bands given on the
  train): all four passed (should-fix 4).

#### 2. `b1230ab`: the close path

- **How it finds the box.** `whats_wrong_boxes`: a visible `#32770` of the attached SolidWorks' PID titled exactly
  "What's Wrong", owned (`GW_OWNER`) by the frame read at the job's start. `close_outlived` refuses unless the
  version is 2024, every box up is owned by the frame and was read by this job's watch, none unowned came in the job,
  the frame reads enabled (True, not unread), nothing blocking was named, and W8's watch logged no other SolidWorks
  window since the last judgement.
- **What it presses.** `press_dont_save(h, ("&Close", "Close"))`: a `BM_CLICK` posted to the first child of that
  box whose text is exactly `&Close` or `Close`. On 2024's box (24-4:311) only `&Close` matches;
  FeatureXpert, the check box and Help do not. It enumerates that box's own children only, so it cannot press a
  control of another window.
- **When anything is not as expected.** I drove `whats_wrong_end` with `close_outlived` in the scratch copy, the
  win32 calls stubbed: a box that closes goes on, with the fact line and the JSON's `outlived` record; a box that
  stays, no Close control found, 2026, another window logged, an unowned box, a disabled frame, and the close path
  raising each end in the STOP, the worker marked hung. After the hook `whats_wrong_end` reads the boxes again and
  stops on any still up, so nothing goes on past a box that did not close.
- **Off without its flag.** `WW_OUTLIVED` is None unless `main` finds the flag in `sys.argv`; W9d imports both
  scripts and calls neither `close_outlived_on` nor W9c's `main`. With the hook None the STOP and its text are as
  before (driven: same STOP, no `outlived` key). On 2026 `whats_wrong_shows_in_update` is False, so
  `whats_wrong_end` never runs and nothing differs at all.
- **The reworded end-of-job line.** Only its middle changes, and only where a box is up at the end or was closed: "it
  was still up after … s" for "it took … s to go", which is kept for a box that went. Nothing reads the live words:
  the only test quoting them pins 24-4:313 in the committed log. W9d behaves as before but for that wording, and only
  in a run that then stops.
- *Note:* `ww_poll` at the job's end adds every owned box to the job's seen list, so the "never read by the watch"
  refusal can only meet a box that came in the milliseconds between that poll and the close path's read. Its
  self-check case is theoretical; harmless.

#### 3. `b1230ab`: `remake-m3` and the ring

- **The same steps.** `section_remake_m3` calls `remake_again`, the function `remake` calls after its first
  part, on its own copy of `setup.master`, so steps 1, 2, 2b and 3 are measured as in `remake`. It omits only the
  first part and its proposal, which the gate no longer needs.
- **The master.** The W9c 2024 run's folder is not on this host (I listed it: absent); W9a's 2024
  `setup.master` is, with its 17 files. Fact: M3 has never run from a W9a-built master. W9c's 2026 runs 1 to 7 read
  W9a's 2026 `setup.master`, but they predate M3; runs 8 to 11 and the 2024 run used masters built by W9c's own
  harness. The note's "as W9c's 2026 runs read W9a's 2026 `setup.master`" is true of runs 1 to 7 only. *Inference:*
  `section_setup` is the same steps at `19651ee` and `4315774` (the diff only wraps W8's helpers in
  `w8_step`), and step 1's own check reads the premise (the ring stops and is marked), so a master that differs
  would fail loudly, not pass falsely.
- **The ring is held strictly enough.** The ring after the press must equal the ring before it, feature by feature
  and code by code, at 54 teeth, and before it must be in error at 54. That is stricter than the old check, which
  held Tooth Space alone. A write that leaves the ring's error the same would still show on the other legs of
  `wrote_nothing`: every part's globals (the ring's included), the traced calls (`ForceRebuild3`, `EditRebuild3`,
  `SetSuppression2` and the rest of `nothing_changed_calls`), the file times, and the result's own fields.
- **Self-check.** Each new judgement's failing ways are covered: the ring's codes or features changed, not in error
  before, not read, not at 54; for the close, each refusal and each failure. The glue (`close_outlived` and the
  hook in `whats_wrong_end`) has no self-check case; I drove it on stubs as above (should-fix 5).

#### 4. `c5f113a` and the ruling

- **The note now says what the logs bear out.** I checked every corrected figure against its line: the box still up
  at 24-4:313 with `stayed []`, `still_up 1`; the kill as the operator's account; §0.5 at 24-4:315; 14.19, 14.69
  and 14.76 GB (24-1:1680, 1755, 1758); 2026's runs 10 and 11 at 2.23 and 2.29 GB at most; remake's 3.59, 7.09, 7.30
  and 2.03 GB (24-4:70, 97, 98, 251); the times against run 10 (824, 1115, 101, 17 s); 51 and 51 (24-1:807, 814),
  case 10's 51 against 2026's 71 (24-1:905, log 10:166); the volumes and their percentages.
- *Two small things left (low):* the table's remake row says 1 FAIL where its own time line says "2 failed" (the FAIL
  and the cut, 24-4:317); and "a kernel difference" for 1408.381 against 1408.364 is an inference, written as a fact
  here and in §1 of this addendum.
- **The ruling is recorded faithfully** in `ISSUE-1-PLAN.md` (its 2026-11-18 paragraph), the script's docstring and
  the note: 2024 only, a demonstration run only, only with the flag, the frame's box with the frame enabled, still
  up 60 s after a job, said as having outlived it, closed by its own Close, gone within 10 s, anything else the STOP,
  the app unchanged. The code is stricter in two ways the ruling allows as "anything else": the frame must also read
  enabled after the close, and no other window may have been logged.

#### 5. `WHATS_WRONG_AHEAD` and the rerun

- **When each sentence is said.**
  - `WHATS_WRONG_AHEAD` ("leave it alone, it closes by itself"): in the footer's user-work line before a press
    (`ui_text._prediction`, `ui_text.py:4596-4601`), when the inventory last read holds a user mate, component
    or feature with an error code and the record's version shows the box.
  - `WHATS_WRONG_AFTER`: in the status after a press that changed a document or placed a gear, stopped
    (`ui_text.py:2053`) or not (`2117`), with something of the user's in error, on that version.
  - Neither is keyed on the app's own part being held in error.
- **So in M3 nothing is said.** Step 1 left only the ring in error, with nothing of the user's (24-4:253, "user in
  error []; user features in error []"). If the app's own press-again opens RangeBox and `ActivateDoc3` raises
  the box, as at the script's read (24-4:310), the user meets it with no sentence before or after. Step 2 stops in its
  check phase with no rebuild after the activation, which is the condition in which the one outliving box was seen.
  If it outlives the press, the user also has a box that does not go by itself. That is inference; the rerun
  measures it.
- **Where AHEAD is said, is it right?** Every box measured in an app Update was gone by the job's end, each with
  the user's work in error and the job rebuilding after it came (W9A-CLOSE-2024-REVIEW §6). AHEAD is also said before a press that will stop before any rebuild: a
  refusal over the user's work, a gate, or the held-in-error stop while the user's work is in error too. That is the
  same activation-without-rebuild condition, and it is not measured. Against the worry: the quiet presses of W9a's m3 on 2024, with the
  user's work in error, raised no box (W9A-CLOSE-2024-REVIEW §4). For it: a script step's activation raised one,
  gone 1.05 s later in that step's own `ForceRebuild3` (s4:115-118, as §5 above cites).
- **Recommendation: leave the wording until the rerun.** No measured case contradicts it where it is said. M3
  cannot test AHEAD itself, since nothing of the user's is in error there, but it tests the mechanism. In the rerun's
  log, for step 2's press and step 2b's, look in order after "remake, M3: pressed again without closing" (the job is
  logged as "Update SolidWorks", "as the app's Update shows it"):
  - whether "What's Wrong came up … into the job" appears, and the call in progress;
  - and then either "stayed [ … ]" with "it took … s to go" (it went by itself), or "it was still up after 60…"
    with the close path's "outlived its job" line (it outlived the press);
  - the JSON's `whats_wrong_lifetimes` entries of kind `app` say the same.
  - *If the press's box outlives it:* AHEAD should say the box goes by itself once SolidWorks rebuilds, and to close
    it if the Update stops first; the held-in-error stop on 2024 should gain a sentence; the ruling's not-measured
    list takes the case.
  - *If no box comes in the press,* that does not settle a user's own press-again (point for a ruling B).
- **Point for a ruling B.** The script's own read before step 2 activates RangeBox first, and its box is the one the
  close path will shut. The app's press is then the second activation with the ring in error, where a user's would be
  the first. A box in the press decides the question. No box in the press decides nothing. Either the coordinator
  accepts that, or the reads before step 2 are made without activating RangeBox (`read_now` has `activate=False`,
  but the ratios read goes through W8's `in_assembly` too), which would change a step measured on 2026.

#### Should-fix

1. **`BM_CLICK` on a box that is not active** (`probe/workbook_assembly_check.py:627-641`, called from
   `probe/w9c_demonstration.py:3789`). Microsoft documents that `BM_CLICK` to a button of a dialog that is not
   active may fail. What's Wrong is a popup owned by the frame, and on an unattended run Excel or the console may be
   in front. W8's earlier presses were on SolidWorks' modal question boxes. If it fails, the box stays, the close fails, and the run
   stops where `06d5141` did, safe but wasted. A fallback posts to the box the `WM_COMMAND` (the control's ID,
   `BN_CLICKED`) that the Close button itself sends when clicked. Whether that counts as "its own Close button" is
   for the coordinator (point for a ruling A).
2. **The control pressed is not checked** (same function): `found[0]` is taken whatever its class, visibility or
   enabled state. Pressing only a visible, enabled `Button` would match the ruling's words exactly. The box's
   template has hidden controls (W9A-CLOSE-2024-REVIEW §5); none is called Close today.
3. **The no-fixture test's docstring** (`tests/test_swbuild_in_place.py:61-63`): say that bands taken away or
   given back still meet the relief's gate, or add a band taken away to `every` and assert both gates.
4. **Pins and fake coverage** (`tests/test_findings.py:2619` onward, `tests/test_swbuild_in_place.py`): pin
   24-1:1503, 1515 and 1725, which the adds and removes gates rest on. Add one end-to-end in-place Update on a fake at
   (32, 5, 0) with nothing patched, as the four in my scratch copy.
5. **The close path's glue in the self-check** (`probe/w9c_demonstration.py:3766`): a case driving
   `whats_wrong_end` with stubbed `whats_wrong_boxes`, `frame_enabled` and `press_dont_save` (closes; stays;
   flag off), as I did, would hold it after this run.

*Low:* the note's "as W9c's 2026 runs read W9a's 2026 `setup.master`" (`W9C-DEMONSTRATION.md:653`) should say
runs 1 to 7, before M3; its time estimate counts about five closes, and a box at every activation with the ring in
error (step 2's two reads, 2b's reads and presses) could make it ten.

*Re-checked after `bf765b3` and `eee5ffe` (2026-11-18, at `eee5ffe`; no SolidWorks; scratch copy deleted).* Both
are fit for the 2024 `remake-m3` run, with no must-fix. The re-check covered the two diffs; W9c's self-check (0 failed,
the close path driven through its `io` in each way it closes or fails), W9d's self-check (0 failed) and
`tests/test_findings.py` with `tests/test_swbuild_in_place.py` (258 passed) were run in the scratch copy.
- **The pins and the fake.** `bf765b3` takes should-fixes 3 and 4: the docstring is right, the relief's gate is held
  on both versions, 24-1:1503, 1515 and 1725 are pinned, and one in-place Update runs on the fake at 32.5.0 with no
  W9c gate patched.
- **The second try.** It goes only to the box that was judged. Before each press `close_control` reads that box's
  children again and requires exactly one control named Close, a visible, enabled `Button`; otherwise the STOP.
  The `WM_COMMAND` is posted to that box's hwnd, with `BN_CLICKED` and that control's own id in its high and low
  words and the control's hwnd as lParam. A What's Wrong that was not the one judged, found up after the first
  press, is the STOP. So is any box still up 10 s after the last try, a frame not read as enabled after the close,
  and any exception (`win32con` names missing included).
- **Without the flag.** `w9a_demonstration.py`, W8's script and `src` are unchanged since `b1230ab`, so the run
  is as before. The second pass runs only inside `remake-m3`, which is by name only; `remake` and W9d do not
  call it.
- **The second pass cannot touch the first pass's evidence.** It starts after `remake_again` has returned: that
  pass's own step 3 and `end_copy` have closed its copy, and its checks and JSON entries are already written. A STOP
  or a raise there leaves the second pass unrun. The second pass works on its own folder (`remake-first`). It ends
  as the first pass's step 3 does: every document of its copy closed without saving (`W.quit_in`), then
  `end_copy`, under the same watched job and close path.
- **One wording point (low).** The note says the second pass shows that the press wrote nothing "by every open
  document's save flag". After step 1 the ring, the two gears and RangeBox are already modified, so their flags
  cannot show a further write; for them only the traced calls, the file times and the result speak. The note
  already says the strict check is the first pass's.
- **What the second pass shows** is as the note says: whether What's Wrong comes in the app's press as the first
  activation since step 1, and what it does.

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


---

## `remake-m3` on SolidWorks 2024 (1dc9350), reviewed

*Independent, 2026-11-18, at `4623701`. I started no SolidWorks, changed no code and ran no tests; I read the log
`probe/results/sw2024/w9c-demo-sw2024-20261118-5-remake-m3-second-pass-assembly-flag.log` (cited `24-5:`) line by
line, its JSON `w9c-demo-20261118-045156.json`, and the note's new section.*

- *Snapshot and version:* the log's line 2 names snapshot `c2d95cc`, line 4 attaches SolidWorks 2024 32.5.0, PID 52980,
  10.73 GB free. `open before: []`. The rule lines say the close path was asked for and in force (24-5:7-8).
- *The note's figures* check against their lines: the times, the 6.86 GB peak (24-5:440), free memory never under 9.48
  GB (24-5:374, 432), the calls by member, the inventory lines and each box's lines. "About 23 minutes from
  SolidWorks' start to its exit" is the operator's: the log's section time is 1287 s (24-5:493).

**Verdict.** Steps 2, 2b and 3 stand as measured on 2024. The one FAIL is a fact of SolidWorks 2024, not a fault of
the app, and nothing needs to run again. Both boxes outlived their jobs. The sentences must change: exact words and
a finding are below. W9c's confirmation on 2024 is met for the five gates and for M3.

### 1. Steps 2, 2b and 3 of the first pass

- **Step 2 stands, under the strict check** (24-5:178).
  - No traced call changed or showed anything. The calls by member (24-5:133) are run 11's (log 11:316).
  - Every part's and the assembly's globals, every save flag and every file time read as before; the JSON's
    `second.flags` are the same before and after, RangeBox already marked before.
  - The ring read in error at 54 teeth with `[('Tooth Space', 51), ('Teeth', 51)]` before and after (24-5:125, 178).
  - The status and the footer were the still-in-error sentence alone (24-5:176-177, 181).
  - No box came in it. Its press was the second activation of RangeBox since step 1.
- **Step 2b stands, and it bears out the premise of `f4eabf5`'s advice.**
  - After `QuitDoc` of the three parts' windows, SolidWorks still held all three, and the ring still read in error
    at 54 with 51 and 51. The three parts' flags read False and only RangeBox read modified (24-5:182; JSON
    `parts_closed`).
  - The press then stopped again on the ring alone, wrote nothing and gave the same advice (24-5:190-191, 233-234).
  - So a part closed alone stays loaded, in error, holding the new value, and its save flag no longer says so. The
    advice must name the assembly, and its wording stands.
  - *Not measured:* SolidWorks' own save prompt. Step 3's close was the script's `QuitDoc`, without saving (24-5:235),
    so "answering No when SolidWorks asks to save them" was never put to a prompt. It is conditional as worded. Since the
    parts' flags read False there, SolidWorks may ask only for RangeBox.
  - *Low:* `_close_unsaved`'s docstring (`ui_text.py:1921`) gives the premise as "SolidWorks marks the open assembly
    modified when a part of it is changed". On 2024 that is not when it is marked (§2 below); the advice is unaffected.
- **Step 3 stands** (24-5:322).
  - The press was routed by way of 53, and the ring read at 54 with nothing in error.
  - The mark is gone, the four gear mates are remade with modes, and the footer is quiet.
  - The user's sprockets were carried with their gears in every mode (24-5:240), with no box (24-5:236-322).
- **Head's entity-kind reads ran inside every press on 2024** (`inventory read yes`, 24-5:62, 130, 188, 240, 375,
  441). Across step 2 they marked nothing of the user's: Sprocket and Housing read False before and after (JSON).
  This lifts §2's caveat on the five 2024 gates.

### 2. The FAIL: a fact of SolidWorks 2024, not a fault of the app

- *Fact (second pass):* RangeBox.SLDASM read False after step 1 and True after the app's press, read each time in a
  job that opens nothing (JSON `first_press.flags`). Across that press nothing else changed:
  - no traced call changed or showed anything, and no file time changed;
  - the result changed, made, remade and placed nothing (24-5:486, 488).
- *Fact (first pass, and this separates it).* `read_now` runs `begin_build`, then `open_document` (`OpenDoc6`
  and `ActivateDoc3` of RangeBox), then `active_document`, then reads every flag (`flags_before`). It stops on any
  flag newly set by the read (`dirtied`). Its `flags_after` held RangeBox marked (24-5:124), and no STOP came.
  So RangeBox was already marked when `flags_before` was read: straight after the open-and-activate, before any
  inventory or other read.
  - Both copies' step 1 made the same calls by member (24-5:65, 378). Together the two passes place the mark at
    RangeBox's first open-and-activate since step 1, whoever makes it. They place it neither at step 1 nor at
    anything later in the press.
- *What the log cannot separate:*
  - `OpenDoc6` (on a document already open) from `ActivateDoc3`, or from the box that came at that activation.
    Neither call is in the trace.
  - Whether 2026 behaves the same: every 2026 read of the flag before step 2 came after an activation (run 11).
  - Run 11's "it is step 1's press that leaves the assembly modified" is not shown on either version. On 2024 it is
    contradicted.
- *Fault or fact?* SolidWorks' mark: the app makes the activation (`open_document` always activates), but writes
  nothing and saves nothing.
  - For the user: after any stop that left a part changed, RangeBox reads modified once anything brings it
    forward.
  - The stop's sentence already says to close RangeBox without saving, answering No, which is the right answer to
    that mark.
  - The app reads no save flag of an assembly open before the press (`_close_costs`), so no sentence goes wrong
    on it.
- **Nothing must run again.** Every other leg of the failed check held (24-5:488 lists only the flag), and the first
  pass's step 2 measured the strict wrote-nothing check.
- **How the script's check should read from now on** (`probe/w9c_demonstration.py`, `remake_first_press`).
  - The record's assembly turning False to True is said as a fact: "SolidWorks marked RangeBox.SLDASM at the
    press's first activation since step 1". It passes only when it is the only flag that changed, no traced call
    changed anything and no file time changed.
  - Any other document newly marked, or the assembly's flag beside a changing call, stays the FAIL.
  - `read_now` should log `flags_before` for the read before step 2, so the separation above is a line in the log
    and not a deduction from the absence of a STOP.
  - The 2024 run's FAIL is then recorded as this fact by ruling, not rerun.

### 3. The boxes and the sentences

**What was measured on 2024 (facts).** Both boxes came at an `ActivateDoc3`, at the first activation since step 1
left an app part in error. Neither went by itself:
- the script's read: up at 0.41 s, still up 60.18 s after its job (24-5:119, 122);
- the app's press again in the second pass: up at 5.56 s, still up 60.24 s after the press (24-5:433, 438).

Each was owned by the frame, with the frame enabled before and after, and each was closed by the script's `BM_CLICK`
on its own Close, gone 0.25 s later (24-5:123, 439; JSON `whats_wrong_lifetimes`, the second of kind `app`). The
app's press returned its result while the box was up (24-5:440-443), so the box blocked nothing. No box came at a
second activation (step 2, 24-5:127-178), in 2b's press, or in step 3, which rebuilt. In `06d5141` the same box at
the same read also outlived it (24-4:310-314). Every box seen in an app Update with the user's work in error went
while the job rebuilt (`findings.py`, `WHATS_WRONG_IN_UPDATE_BLOCKS`). *Inference:* the box comes at the first
activation with a feature in error and goes only when SolidWorks rebuilds after it. A person bringing RangeBox
forward is not measured.

**So by §5 of my re-check:** `WHATS_WRONG_AHEAD`'s "it closes by itself" is untrue for a press that stops before
rebuilding, and the held-in-error stop now has a measured box with no sentence. The app still never closes the box,
changes no setting and refuses for none; the sentences tell the user to close it. Exact words for
`src/gear_generator/ui_text.py`:

1. **`WHATS_WRONG_AHEAD`** (`ui_text.py:4512`), said as now: in the footer's user-work line when the inventory
   last read holds the user's work in error, on a version where `whats_wrong_shows` is True:

   > SolidWorks may show its What's Wrong box during the Update: leave it alone while the Update runs. It closes by
   > itself once SolidWorks rebuilds; if the Update stops before that, it stays until you close it with its Close
   > button.

2. **New `WHATS_WRONG_STAYS`**, said once after `still_in_error_sentence` wherever `gearbox_update_status` says
   that sentence (`ui_text.py:1891-1906`: the held-in-error stop alone, beside another failure, or in place of
   "already matches"). It is said only where the new finding below is True for the job's `revision` (passed in, as
   `_gearbox_update_status` already takes it):

   > SolidWorks may show its What's Wrong box for that part when this press brings the assembly forward; it does not
   > close by itself: close it with its Close button, then close the documents as above.

3. **New `WHATS_WRONG_NEXT`**, said once in a stop that leaves a part in error (`ui_text.py:2027-2038`, when
   `in_error` is not empty), on the same finding. Where it is said, `WHATS_WRONG_AFTER` (`ui_text.py:2053-2054`) is
   not:

   > SolidWorks may show its What's Wrong box for the part left in error when the assembly is next brought forward;
   > it does not close by itself: close it with its Close button.

   This rests on the two programmatic activations. A person's own is an inference, hence "may".

`WHATS_WRONG_AFTER` is unchanged elsewhere: after an Update that rebuilt, every box measured went.

**Findings for `src/gear_generator/findings.py`**, beside the What's Wrong trio:
- `WHATS_WRONG_STAYS_WITHOUT_A_REBUILD_ON_2024 = True`:
  - *Meaning:* the What's Wrong box SolidWorks raises at the first activation after an Update left a part in error
    stays when nothing rebuilds after it.
  - *Lines:* 24-5:433, 438-440 and 443, the app's press; 24-5:119, 122-123, the script's read; 24-4:310-314, and
    the JSON's two `whats_wrong_lifetimes` entries.
  - *Not raised:* at a second activation (24-5:127-178) or in a press that rebuilt (24-5:236-322).
  - *Caveats:* which document's `ActivateDoc3` raised it in the press is not logged; a person's activation was not
    run; how long it stays past 60 s, and closing the documents with it up, were not run; a press that stops before
    rebuilding with the user's own work in error was not run; "Display What's Wrong during rebuild" was on.
- `WHATS_WRONG_STAYS_WITHOUT_A_REBUILD_ON_2026 = False`: no box at all on 2026. In run 11's M3 the script's
  first activation after step 1 and step 2's press were both under the any-dialog STOP, and no window came (log
  11:309-361). Caveat: run 11's press was the second activation.
- A helper `swbuild.whats_wrong_stays(revision)`, True only where the finding is True, read by the two new sentences.
- `WHATS_WRONG_IN_UPDATE_BLOCKS_ON_2024` stays False. Its comment's "a box that outlives its job (none did)" becomes
  the measured case: the box outlived the press, the frame stayed enabled and the press returned its result
  (24-5:433-443).
- Comments only, nothing reads them:
  - 2024 marks an open assembly at its first open-and-activate after its parts were changed by a press that did not
    reach it, not at the change (§2);
  - on each 2024 gate, the entity-kind reads have now run inside Updates (24-5:62 … 441), and the caveat goes;
  - `UPDATE_MAKES_MATES_WITH_MODES_ON_2024`: M3 is now shown to step 3 (24-5:178, 182, 234, 322).

**Tests owed:**
- In `tests/test_workbook_user_record.py`:
  - the new `WHATS_WRONG_AHEAD` pinned word for word;
  - `WHATS_WRONG_STAYS` once after the still-in-error sentence at (32, 5, 0), in each of the three forms of
    `gearbox_update_status`; absent at (34, 1, 1), at `()`, and with the finding patched None;
  - `WHATS_WRONG_NEXT` once in a stop leaving a part in error at (32, 5, 0), with `WHATS_WRONG_AFTER` absent there;
  - `WHATS_WRONG_AFTER` still said, once, where the user's work is in error and no part is left in error;
  - one footer test that the two never stand together.
- `tests/test_findings.py`: the new pair pinned to 24-5's lines and JSON (both entries, `closed_by` `BM_CLICK`, the
  second of kind `app`) and to run 11's lines for 2026; the 24-5 lines for M3's steps 2 to 3.
- The scripts:
  - W9c's `status_alone` and the still-in-error checks, and any W9d check that matches that status whole, must
    accept the 2024 tail;
  - W9c's `whats_wrong_showed`-style assertions stay as they are.

### 4. W9c on 2024, and what remains

- **The evidence stands at head.**
  - `git diff 4315774 4623701 -- src` adds, beyond what my addendum's §2 traced, only `d0e32bb`'s findings, W9d's
    2026 findings (`225e3d7`) and Build again's standing-list sentences (`891a707`). Nothing is on an Update's path.
  - So the five gates set True on 2024 rest on 4315774's runs, whose writes are head's, with M3 now measured at
    `c2d95cc` to step 3.
  - `UPDATE_MAKES_A_NEW_COUPLING`, `UPDATE_SUPPRESSES_THE_RELIEF` and `EXTERNAL_REFERENCES_READ` stay None on both
    versions, as ruled.
  - **W9c's "confirmed on 2024" is met**, once the FAIL is ruled the fact §2 shows.

**What remains before W9c closes, in order:**
1. Rule the second pass's FAIL the SolidWorks 2024 fact of §2 and record it so; amend `remake_first_press`'s flags leg
   and log `read_now`'s `flags_before` (§2). No rerun.
2. The sentences of §3 in `ui_text.py`, the finding pair and helper, the `BLOCKS` comment, and their tests and
   script predicates, reviewed.
3. `findings.py`'s 2024 comments: the entity-kind caveat lifted, M3 to step 3, the assembly-marking fact; pinned.
4. `ISSUE-1-PLAN.md`'s What's Wrong section: a box outliving an app press is now measured. The app leaves it alone
   and says so; the not-measured list keeps a person's own activation and a press stopping before rebuild with the
   user's work in error.
5. Step 2b on 2026, or the coordinator's ruling that 2024's measurement carries the version-free advice (it now
   holds there).
6. *Low:* `_close_unsaved`'s docstring premise (§1); `gears/landing.py`'s docstring on code 51 (still not taken).
7. The handoff: the 2024 memory advice and the interference-volume caveat (addendum §4); the stale "W9c at the
   session's close" bullet with runs 10, 11, the 2024 run and this one as the evidence; item 10 and the phase table.
8. The whole suite at the commit that closes W9c, with the known font-width failure only.
