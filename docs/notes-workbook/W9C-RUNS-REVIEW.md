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
