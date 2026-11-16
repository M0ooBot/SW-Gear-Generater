# Issue #1 plan, second review (the revision to the user's answers, `cf99dfa..48ed91f`)

**Verdict: approve with the listed changes.** The revision takes in the user's four answers and the window ruling.
The cost table adds up, and K2's corrected tie rule is the right idea. Three things in W9e (§2.5) must change before
its packages are written; none of them blocks W9a, W9b or W9c.

- §2.5 never says what happens to the user's features in an app part that the new revision makes new. That is the
  user's own case ("made edits to some of its parts").
- The fallback throws away mates that could be remade, against the binding answer.
- Two of W9e's steps act on the user's documents in ways the plan does not account for:
  - a second save of the new assembly, through a call the app has never made;
  - per-mode reads of the old assembly, which today can only be done by showing its modes.

K12 can be built in Tk and has a precedent in the strip. But "the footer always whole" cannot hold for a footer
taller than the room it has. The window check as written would also pass a footer hidden under the taskbar.

**How it was checked.** I read `git diff cf99dfa 48ed91f` against the whole plan at `48ed91f` and the first review
(`8ce7426`). I checked it against this code:

- `workbook/gearbox.py` (the revision and reuse docstring at lines 17-55, carriers at 696-783);
- `workbook/layout.py` (stems at 453-462 and 496, plane and axis names at 219 and 321-353, base planes by tree order
  at 76-77);
- `swbuild.build_gearbox` (2843-2960), `_free_to_turn` (1068-1083);
- `swcom.save_as` (1149-1166), `constrained_status` (2411-2424), `mate_suppression` (2962), the base-plane rule
  (1310);
- `workbook_gui.py` (`_build` at 365-470, `_fit` at 1160-1170, the left width at 931), `gui.py` (the strip's page at
  270-326, `_work_area` at 1836-1849, the start at 1990-2004);
- `tests/test_workbook_window.py:730-768`, `probe/workbook_window_check.py:620-694`,
  `probe/workbook_assembly_check.py` (`s7_put_job` at 7481-7531);
- the W8 closing-run logs (section times; the window failure at `w8-window-20261116-031412.log:283`);
- `~/SW-Macro-Database/API-LEDGER.md`.

The built W8 masters are on disk: `…\w8-close-sw2026-20261116-001758\out\s1.master` and
`…\w8-sw2024-20261115-223821\out\s1.master`. I did not run SolidWorks.

---

## Must change before W9e's packages

**M1. User features in an app part made new: §2.5 is silent (§2.5's table, §0.2 K5, §5 W9e *Done when*;
`workbook/gearbox.py:33-55`).**

- *Which parts the new revision makes new.* A Build again… makes an app part as a new file in three cases:
  - its plan or values changed (`<stem>_r<k>` when its own name is taken, `STALE`);
  - it is unsaved after an Update (`UNSAVED`);
  - the live check found one of its app globals changed (`MISMATCHED`), which after K11 is exactly a value the user
    typed in SolidWorks.
- *What the plan says about that part.* Tier 3 of §2.5 says only that a *face* of a user feature in such a part "is
  not found". It never says what happens to the feature itself (the Keyway, the fork groove) in the new revision.
  Read literally, after W9e the Build again… question loses W9a's sentence (*"your Keyway stays in Gear_m1.25_N17,
  which RangeSlv's new part replaces"*, §2.1 item 8, "until W9e"). The keyway is then left behind in silence, which
  is the user's own complaint.
- *Change:*
  - Add a row to §2.5's table: *"A feature of yours in an app part this revision makes new | — | Named, with why the
    part is new and that the old file keeps it: 'your Keyway is in Gear_m1.25_N17, not in Gear_m1.25_N17_r2, which
    is new because its Flank changed; RangeBox.SLDASM and that file keep it'"*.
  - Say it in the question before the press (from the inventory, with its time) and again in the result.
  - Name every mate on such a feature's faces together with the feature.
  - Where the only reason the part is new is `MISMATCHED` or `UNSAVED` and the part holds user features, say how to
    keep them. For `MISMATCHED`: *"type 12 in Gears!J5 and Build again… reuses the part with your Keyway"*. That is
    K11's sentence, carried to Build again….
  - Add to M9 and W9e's *Done when*: a keyway in Sun, whose Flank change makes its part new, named in the question and
    the result.

**M2. The fallback drops mates that can be remade, against the user's answer (§2.5 *Clusters, and the fallback*;
§0.2 K5).**

- *What the user asked.* The answer is "remakes their mates; a mate that cannot be remade is named". So every mate
  that can be remade is remade.
- *What the plan does instead.* §2.5 deletes every mate of a cluster when any one of them fails, and its own example
  names two mates "therefore not made either".
- *The plan's reason does not hold.* It is "half mated and floating would drift". SolidWorks leaves an under-defined
  component where it stands until it is dragged; users' assemblies are full of them. Dropping a mate cannot
  over-define anything. Only fixing a half-mated cluster can, and the plan's own fallback is what fixes it.
- *Some mates are always remakeable.*
  - User–user mates have both ends on files both revisions use, so they always come under tier 1.
  - A lock or gear mate on an app part made new references the *component*, which maps by the record's gear id. It is
    never "not found".
- *Change:*
  - Remake every mate whose entities are found. Name each one that is not, with why.
  - Leave the cluster's components floating where they stood (or fixed, as they were).
  - Fall back to "fixed, unmated" only for a cluster in one of three cases: a remade mate comes back in error that was
    not in error in the old assembly (see S3); the cluster over-defines; or it ties a gear (the post-check). Even
    then, delete only its mates to app parts, the layout and the assembly's planes, and keep its user–user mates.
  - Reword the example sentence.

**M3. W9e acts on the user's documents in two places §0.3 does not allow (§2.5 *When it runs*, *What is carried*).**

- *(a) "saves the new assembly again".* `swcom.save_as` refuses an existing path (`swcom.py:1155-1156`), so this
  second save is `Save3`.
  - Nothing under `src/` calls `Save3`. The ledger verifies it in place on 2026 only (`API-LEDGER.md:144`).
  - Whether saving an assembly in place also saves its modified referenced documents is unmeasured. Those include
    the user's sprocket part open with unsaved edits, and a reused app part with an unsaved keyway. If it does, the
    user's files are written.
  - Today's first save is safe: `SaveAs3` with option 1 left every part reading `GetSaveFlag` True afterwards
    (`swbuild.py:2898-2906`), so it saved no reference.
  - *Change, the lean way:* leave the carried items **unsaved**, as Update leaves everything
    (PLAN-WORKBOOK §4.5). The result ends *"… save in SolidWorks to keep them"*. That needs no new call and keeps
    "the app's own result never rests on the carried items".
  - *Otherwise:* put `Save3` on an assembly into S5, with `GetSaveFlag` and the file time of every referenced user
    file before and after, and add a STOP on any of them written.
- *(b) Reading the old assembly "in each mode".*
  - Frames per mode are readable only with that mode shown (J25, which §2.1 item 3 relies on).
  - The old assembly is most likely open in the user's session with unsaved work, which is what the user means by
    "my assembly".
  - Showing its configurations changes the user's active configuration, an un-allowed write under §0.3's first
    STOP.
  - *Change:*
    - Read the old assembly as it is in the session when open, and never close it. Open it read-only when it is not
      open (`OpenDoc6` with `swOpenDocOptions_ReadOnly`, new; put it in S5).
    - Read component state per mode without showing a mode. S5 must find the route, as `IsSuppressed2(3, names)` did
      for mates (`API-LEDGER.md:332`).
    - Read frames in the active mode only, and place a cluster by its pose relative to its app component (S1).
    - If S5 finds no unshown route, write show-and-restore into §0.3 as a third exception: the active configuration
      read back as it was, and `GetSaveFlag` unchanged.

---

## Should change

**S1. "Comes over at its frame": which mode's frame, and relative to what (§2.5 table row 1; §0.2 K5).**

- *Relative to the app gear.* A component mated to an app gear should go in at its pose relative to that gear in the
  new revision: new gear frame · old gear frame⁻¹ · old component frame. W5 leaves the user's turns in place (s2),
  so the old Sun may stand turned. A sprocket placed at its world frame and then locked to the new, unturned Sun is
  locked at the wrong angle to it: a keyed part off its key. A lock re-takes the current relative frame
  (`API-LEDGER.md:338`).
- *Per mode.* A floating, unmated user component can stand differently per configuration (ruling 9.18). Say it is
  placed in each mode, or only in the first.

**S2. How entities are named and mapped (§2.5 *How each mate's entities are found*, items 2-3).**

- *Base planes.* The assembly's and every part's base planes are taken by tree order, "never by its English name"
  (`swcom.py:1310`, `layout.FRONT/TOP/RIGHT`). On a non-English install "Front Plane" is not its name. Use the same
  rule, and the origin likewise.
- *Carrier parts.* Carrier parts are new files per revision as well (`layout.carrier_stem`,
  `<Name>_r<n>_<C>_Carrier`; `gearbox.py:763`), with named axes and planes. Add them to tier 2.
- *Mapping components.* Say how an old app component maps to the new one: by the record's gear id, planet copy *k*
  to copy *k*; a copy that is gone means not found.

**S3. A mate already in error in the old assembly (§2.5 *Clusters*).** W9a reads every user mate's error code. A
remade mate that comes back with the error it already had should be carried as it was and said, not treated as a
failure of the cluster.

**S4. The grounded-tie rule (K2, §2.1 item 3).**

- *It agrees with the app.* It is the same read as `_free_to_turn` (`COMPONENT_UNDER_DEFINED` = 2 is free;
  `swbuild.py:1068-1083`). It is defined before any change in the mode showing, by a SolidWorks read in the check
  phase. It is not known before the press, which K4's record-then-refuse already handles.
- *It lets the ordinary case through* if SolidWorks reads Sun under-defined with a floating sprocket that is locked to
  Sun and concentric to the layout's axis. That is expected, and S0 case A reads it, with C as the control. Four
  gaps:
  1. *Naming.* A tie on one gear makes the whole train read fully defined, through its gear mates and the couplings
     engaged in that mode. A gear that reads not free may carry no user mate at all. Name the user mates on **the
     train** in that mode, not "on that gear".
  2. *"Where the app's own mates leave it free".* This comes from the record (the build's or last Update's
     post-check passed). Say so, so that no one suppresses the user's mates to read it.
  3. *The stop part way through.* It departs from K4's "before any change". When every user mate on the train has
     the same flag in every mode (readable without showing, `mate_suppression`), the read in the showing mode decides
     every mode, because user mates that ground a gear ground it whatever the app's per-mode mates do. The stop part
     way through is needed only when a user mate's flags differ by mode. Say so, and add that case to S0 (C with the
     housing's coincident on in L only).
  4. *A user mate joining two app gears of different trains* (a lock from Sun to RangeSlv). It reads under-defined,
     so it is not a tie, but no put can satisfy it. Say what happens: a graph check on the inventory that refuses,
     named.

**S5. S0 (§4, *S0, W9a's first step, precisely*).**

- *Time.* It is about half what W8 measured.
  - W8's s1 took 946 s to build E4, and s7 about 165 s for each of its seven cases.
  - S0 builds RangeBox, builds and inserts a sprocket and a housing, then runs six fresh copies (three cases × two
    routes), each turned and put in two modes, plus P0.
  - So about 40 min on 2026 and 70 min on 2024, not 20 and 35. Keep S0's built master for W9a's demonstration on
    each version, or RangeBox is built twice.
- *Calls new to the app.*
  - Mate the sprocket and housing by their parts' named axes and planes through `GetCorresponding`, as the app does
    (`API-LEDGER.md:552`), not by faces picked by coordinate.
  - Save each case's setup by `save_as` to a new name. The proven route refuses the existing path, and `Save3` is new.
  - `AddComponent5` into a reopened assembly with configurations is first used here, ahead of M5. That is
    acceptable, but say so.
  - Run P0 (What's Wrong) **first** in the session, so a dialog costs nothing of S0.
- *A control for route (a).* After the last put, show every mode, rebuild, and read every body (s7's discipline). A
  put that holds only until the solver next runs would otherwise read as success.

**S6. K12, the window on a short screen (§2.6).**

- *It can be built.* It is a constructor change, not a rebuild of the window at run time. Rows 1-5 of `body`
  (`workbook_gui.py:390-452`) are built into a frame inside a canvas, and the head and foot stay outside it. The
  strip's page is the precedent: `create_window` with a width, then `<Configure>` setting the scroll region
  (`gui.py:270-316`). Five gaps:
  1. *A footer taller than the room.* "The footer and its buttons are always whole" cannot hold for such a footer.
     The built E4 footer is already 281 px at 150 % (`w8-window-…log:283`). W9a adds the inventory sentence and
     K11's "every such value named at once". Give the footer a ceiling (say a third of the work area), above which
     its sentence scrolls in itself or its lists move to Checks with a count, and give the body a least height.
  2. *The work area.* `SPI_GETWORKAREA` is the primary monitor's, not "the window's monitor". Reuse
     `gui._work_area` and say "primary", or use `MonitorFromWindow`. Subtract the window's frame (title bar,
     borders) from the height cap, as the strip subtracts 40 px (`gui.py:1999`).
  3. *The window check.* `w8_footer_whole` (`probe/workbook_window_check.py:630-639`) compares only with the
     window's inside height. A window held to the screen but running under the taskbar passes it. Add two
     assertions: the frame's bottom (`GetWindowRect`) is inside the work area, and the body's last line can be
     scrolled into view.
  4. *The scroll bar's width.* Reserve it always, or count it in the left column's width (`workbook_gui.py:931`).
     Otherwise a bar that appears narrows the left column, which re-wraps, changes the height, and can hide the bar
     again.
  5. *The mouse wheel.* The strip binds `<MouseWheel>` app-wide (`gui.py:285`). Its `_on_wheel` (`gui.py:318-326`)
     scrolls the strip's page wherever the pointer is except over the flyout, so it scrolls with the pointer over
     the Workbook window too. Both handlers must act only for their own toplevel.
- *What it contradicts.* `test_the_window_keeps_its_width_with_update_shown_and_a_long_sentence`
  (`tests/test_workbook_window.py:751-768`) pins `height == winfo_reqheight()`. UI-DESIGN §9 says "grows taller"
  three times: lines 397-399, 557, and 1128, which adds "(a test pins it)". Name all of these for rewriting, not
  "the layout paragraph" alone. §2.6's "wants about 1690" should cite what was measured: the footer's bottom at 1657
  in a window 1570 tall inside.

**S7. The record's schema (§2.5 *The record*).** "Schema 7" is stale. W9c's record is 8, and W9e's new fields (which
mates were remade) make it 9, by the rule the first review's S6 set.

**S8. Costs (§5).**

- *W9a on 2024.* The confirming build at 2 h against 1.5 h on 2026 is 1.33×. W8 measured 1.6-2.2× (s2 took 27 min on
  2026 and 43 on 2024; putting every mode took 238 s and 515 s), so about 2.5-3 h.
- *The window check.* W8's took 12 min (03:14-03:26), not 30. K12 is Tk alone, so a 2024 window check adds nothing
  to it. Run it once, on 2026.

---

## Notes

- **The code agrees with §2.5's premises.**
  - A Build again… always makes a new layout part, `<Name>_r<n>_Layout`. The layout is reused only when continuing a
    revision whose assembly failed (`gearbox.py:21-31`).
  - It makes new carrier parts too.
  - It reuses an unchanged gear part as the same file, the user's features with it (`PartReuse`, `build_gearbox`
    step 1, which checks only the app's globals and named features).
  - The first save does not save references.
  - So tier 1 (persistent reference) is possible for user parts and reused gear parts, and tier 2 (by name) for the
    layout's `"<Shaft> Axis"` and `"<Shaft> X Plane"` (`layout.py:219`, `:512`). A shaft's plane exists only off its
    base plane; every RangeBox shaft uses the base planes, so S2's tree-order rule matters there.
  - The new revision never writes the old assembly or a user file, except as M3 says.
- **Q2: what W9e buys, and whether a cheaper design exists.**
  - *The edits it serves.* After W9a and W9d, Build again… is reached by §2.1's closing list. The edits the user is
    likely to make once they have work in the assembly:
    - adding or removing a shaft;
    - adding, removing or renaming a Modes row;
    - the number of planet copies;
    - a Part name or Flank change.

    The rest are rare. For every one of these but the last, every existing gear part is reused as the same file. So
    tiers 1 and 2 carry nearly all the user's mates, and tier 3 (finding a face by its role on a new file) serves
    only a part whose file changes.
  - *Copying the old assembly and updating the copy in place is not cheaper.* Three things stop it:
    - `SaveAs3` on the user's open old assembly would re-point their open document to the new path. A copy needs
      `swSaveAsOptions_Copy`, which is new, or a disk copy, which loses their unsaved work.
    - The copy still references the old layout and carrier files, which the old assembly shares. Changing them in
      place changes the old assembly. Avoiding that needs `ReplaceComponents2` or `ReplaceReferencedDocument`,
      unverified in `API-LEDGER.md:93` and dialog-prone.
    - The edits that reach Build again… are, by definition, the ones Update cannot make in place.
  - *Cheaper options that still meet the answer.*
    - Drop tier 3 and name those mates instead. That shrinks S5 and M9.
    - Or move adding and removing Modes rows (the likeliest remaining edit on a box with modes) into W9d's Update. It
      uses the build's `AddConfiguration2` and the per-configuration flags W9d already writes, and keeps the user's
      work in its own assembly.
- **Q6: savings in agent runs, each with what it costs.**
  - Merge W9b into W9c (about −2 runs). W9b's tests already need RangeBox_Fixed's checks, which need W9c's hub kind
    and bands: §5 W9b *Tests*, a slip from before this revision. *Cost:* the sleeve warnings ship later.
  - Put K12 into W9a package B, which already redraws the boards and UI-DESIGN §9 (about −1 to −2 runs). *Cost:* a
    review with a narrower focus.
  - Run S5 and P2 inside W9d's 2026 and 2024 sessions, beside P1, M5 and M6 (about −2 runs and two SolidWorks
    start-ups). *Cost:* W9e's spike is reviewed later, which does not matter since W9e is last.
  - Fold W9c's 2024 build into W9d's 2024 session (about −1 run).
  - Run the window check on 2026 only (−30 min on 2024).

  Together these come to about 40 runs instead of 47. S5's fix (+20 min on 2026, +35 on 2024) and S8 (+30-60 min on
  2024) roughly cancel the hours saved.
- **Q7: nothing else is stale.**
  - §0.2's bound rows, §6's "Answered" and "Still open" lists, the stage table and its totals (7 h 15 min, 10 h 50
    min, 47 runs) agree with each other.
  - K1, K3, K4, K6 and K7 are marked "for the user to overrule" but were never put in §6. Say they stand approved
    with the stages.
  - Beyond the plan's text: the coordinator's brief has 1657 as what the window *asks*. It is where the footer label
    ends. See S6.
- **Not verified (no SolidWorks run):**
  - the route from a mate's assembly-context entity to its part-level entity for `GetPersistReference3`, which is
    the crux of tier 1 (the ledger verifies only a part's feature, `:186`, and part-to-assembly `GetCorresponding`,
    `:552`);
  - whether `Save3` on an assembly saves modified references;
  - whether `GetConstrainedStatus` reads Sun free with a floating sprocket locked to it;
  - an unshown per-configuration read of a component's state.
