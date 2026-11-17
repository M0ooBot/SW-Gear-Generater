# W9 (issue #1: the user's work in a built assembly, and dog-clutch sleeves): the plan

**Authority and reading order.** `docs/PLAN-WORKBOOK.md` stays the authority. This plan says where W9 departs from it
and from W8's readings and rulings (`W8-PLAN.md` §0.3, `W8-INTERFACES.md` §9), each named in §0.2. Its review is
`ISSUE-1-PLAN-REVIEW.md` (`8ce7426`); *Changes after the review* at the end lists every change against the review's
points, and where the two differ the revised text below wins. The user answered the plan's choices on 2026-11-16
(*Changes after the user's answers*, at the end): **all the stages approved, in order**; an app-owned value
the user changed stops Update, named (K11); **Build again… carries the user's components and remakes their mates**
(K5, a stage of its own, W9d); the hub is built by the app from a row (K8). Those now bind. A second review
(`ISSUE-1-PLAN-REVIEW-2.md`, `16e45dc`) and the coordinating session's rulings on its cost points followed
(*Changes after the second review*). GitHub issue #1 (`MoZ200701/SW-Gear-Generater`) is the
source of the four problems. The user's own words on problem 4 set the first requirement:

> "the thing about update cannot add a part is i have the assembly right then i made edits to some of its parts or
> added additional parts but then i straight up cannot use the build app anymore because it would overwrite all the
> things i did there"

**First requirement:** once the user has worked in the built assembly (edited app-built parts, added components of
their own, mated them, among themselves and to the app's gears), the app stays usable on it, and no app action
destroys that work or undoes the user's edit without their word. "Usable" means that the user's ordinary case — a
sprocket or coupling of theirs mated to an app gear — goes through Update, not that it is refused with a better
sentence. It is the first stage (W9a) because the code gives no reason to order otherwise: it needs no new geometry,
and it is what makes every later stage usable on a worked-in assembly.

**Where W8 stands.** W8's closing run finished overnight on SolidWorks 2026 34.1.1, every assembly section at 0 failed
(commits `c351b1f` to `fb85bcc`); the full window check there failed once, the built footer cut off by this device's
screen (`fb85bcc`), which K12 below takes up. So W9 starts from a closed W8 once that run's review is in.

Everything below was read at `c351b1f`, the revision checked against the review's citations at `8ce7426`, and the
window's fit at `fb85bcc`. Rules carried over unchanged (HANDOFF, *Rules carried over*): commits by explicit path, no
attribution lines, findings from committed `findings.py` only, the full build first, a probe ahead only for a call new
to the app that could hang, raise a dialog or damage a file or session, SolidWorks 2026 the working version with one
confirming build on 2024, each plan and result reviewed by a separate agent.

---

## 0. Summary

### 0.1 The name, and what it changes in the plan's statements

**W9**, in four stages W9a–W9d (renumbered after the second review: the sleeve checks and the bands and hub are one
stage, W9b; *Changes after the second review*). It is the next row of PLAN-WORKBOOK §6 because it changes the same import, record
and window W1–W8 built, and a W-number keeps the handoff, the boards and the results folder in one series. Two things
change with the name, both when W9a lands (not in this commit):

- *The tests' made-up W9* becomes **W99** (strings only): `tests/test_workbook_build.py:25-29`, `:538`, `:545`,
  `:797`, the fixture's import in `tests/test_workbook_window.py:30`, and the state shown in `design/UI-DESIGN.md:437`
  (*later · phase W9*).
- *"W8 is the last phase."* W9 adds **no refusal channel**: `LATER` stays empty and what this version does not build
  stays an error naming no phase. The sentence becomes *"W8 was the last phase of the import as planned on
  2026-11-11; W9 (issue #1) builds on it and leaves no row waiting for a phase"* in PLAN-WORKBOOK §3.4 (line 279) and
  §6 (lines 715-716), which also gains a W9 row; HANDOFF (lines 515-516); `design/UI-DESIGN.md:472`; and the comments
  and docstrings at `ui_text.py:1015`, `tests/test_ui_text.py:317`, `tests/test_workbook_build.py:797`,
  `workbook/build.py:37` and `workbook/geometry.py:228`.

### 0.2 Readings, and the user's answers

Each is argued in §2. **K1–K6 and K11 are the heart of problem 4.** Rows marked **(the user's, 2026-11-16)** are
the user's answers and bind; **(ruled)** is the coordinating session's ruling, for the user to overrule. K1, K3, K4,
K6 and K7 were never put to the user as questions and stand approved with the stages; K2, K9 and K10 are the plan's
readings still open in §6.

| # | Reading | Instead of | Overturns |
|---|---|---|---|
| K1 | **What is the app's own** is what the record lists: the gear, carrier and layout components (by `Name2`), the mates (by name), the configurations named as modes, and in each app part the globals and features its plan made. Everything else is the user's. A recorded component not found by its `Name2` is found by its part path when exactly one unclaimed instance of that part is in the assembly, and its new name recorded. | Guessing ownership from names; a renamed component sending the user to Build again…. | — |
| K2 | **A user lock on a gear Update must move does not stop Update** (amended after S0: *Changes after S0 and its review*). S0 (§4, `W9-S0.md`) measured the plan's two routes, **(a)** the put left to carry the user's component, nothing of the user's written, and **(b)** the user's mates suppressed around the put and turned back on, and both leave the component where the drive took it, the user's lock taking the new offset with no error. **Route (c1) is taken** (the coordinating session's ruling, accepted by the user 2026-11-16): every user component rigid to a gear this press puts, through user lock mates that are on in the mode being put, directly or through a chain of user locks (the chain read from each user lock's entities in that mode, M1's read), is put by that gear's own rigid motion in the same step, in the mode shown (its target G_target · G_before⁻¹ · U_before), after the app's bodies, each read back by `place_component`; the user's locks stay on. **Every other kind of user mate that ties a user's component to a gear Update would put back refuses before any write, named, until that kind is measured** (ruled, put to the user): a user gear mate above all (a put re-phases a gear mate silently, `MESH_PHASE_ROUTE`), a mate to a gear's own faces or planes, and a user lock whose flag differs between the mode being put and another mode. Beside both, only a **grounded tie** refuses: a train SolidWorks reads not free to turn (`constrained_status`, the read `_free_to_turn` makes) with the user's mates on, where the record says the app's own mates leave it free (the build's or last Update's post-check passed; nothing is suppressed to find out), the user's mates on **that train** named, the train as the mode read joins it (its couplings decide which bodies a tie holds). It is read in the mode showing before any change; when every user mate on the train has the same flag in every mode (readable without showing), that read decides whether a tie stands in every mode; only when they differ by mode is a mode read when shown, before its put, and a tie there stops the job part way. A user mate joining gears of two different trains (a lock from Sun to RangeSlv) reads free but no put can satisfy it: the inventory refuses it, named, before any change. SolidWorks' solver decides the tie, not a graph of mates: a sprocket concentric to the layout's axis and locked to Sun leaves Sun free and is not a tie. | Refusing every user mate on a moved gear (the plan before the review); routes (a) and (b), which S0 found leave a locked component behind; today's refusal of every user mate; a topological graph check (wrong for a concentric mate to a fixed axis). | W5 review M7, W8 J12's last sentence |
| K3 | **The user's features in an app part are kept.** Update changes only the app's globals; SolidWorks rebuilds the user's features after them; the job reads each user feature's error state afterwards and names any in error, as theirs. Nothing is saved (as today). | Refusing to change a part with user features. | — |
| K4 | **Told before anything is written.** Every job reads the user's work in the documents it opens and the finish records it, with the time read. The footer says before the press what Update will change, which of the user's components it will put with their gears (route c, K2), and what it leaves. Something the record did not hold that would refuse makes the press refuse before any change and is recorded, so the footer then says it; the next press refuses again unless the user has dealt with it. No new control. | A check-only job and a question before each Update. | — |
| K5 | **(the user's, 2026-11-16) Build again… carries the user's components and remakes their mates (W9d, §2.5).** Every top-level user component comes over where it stood relative to its app gear (or the layout), fixed or floating as it was, with its state in each mode; every mate of the user's whose entities are found is remade — by persistent reference on a file both revisions use, by name or tree order on the layout, carrier parts and the assembly's planes, by component for a lock or gear mate — and every other is named with why; a mate on a face of an app part made new is named, not re-found **(ruled: no finding by geometric role)**; the user's features in an app part made new are named with why the part is new, and how to keep them where K11's value is the reason. Carried items are left **unsaved**, and the user's open documents are never shown in another mode or saved. Until W9d, Build again… says what stays behind, as read at a stated time. | Saying only; bringing components over fixed and unmated (the plan's recommendation before the user's answer); finding faces by role on a new file. | — |
| K6 | **Update adds, removes and re-mates (W9c):** a new gear on an existing frame shaft along Z±, inserted and mated as the build mates it; a gear removed (not one that anchors other gears) with its app mates; a coupling or sliding mesh newly needed between components on record; a gear mate of a gearbox with modes made again (a tooth change); **Modes rows added or removed (ruled)**; each new or remade mate's and component's flag set and read back in every configuration. Bands are added to a built sleeve **in place** (§2.4). Replacing a part's file stays Build again… (deferred). | Every such edit structural; replacing the sleeve's component. | W8 J14 (in part), ruling 9.16 |
| K7 | **Reachability is a warning**, by the points the sleeve's shaft must reach (§2.2). | An error; the issue's narrower rule. | — |
| K8 | **(the user's, 2026-11-16) The hub is a workbook row**, kind `hub`, on the sleeve's own shaft, built by the app as a toothed ring like a dog with the row's Bore; the app never adds one by itself. A sleeve with no hub row is warned of. | A hub row checked but not built (a skeleton, as the carrier); the app adding one; leaving it to the user unchecked. | W8 J1 ("no hub") |
| K9 | **Minimum running clearance 0.5 × module a side, at least 0.5 mm**, a warning per mode. | A fixed mm figure; an error. | W8 J22 (extended) |
| K10 | **A sleeve declares two toothed bands** (two numeric columns, one at each end of its face); the span between is a relief bore of diameter m(z + 3), clearing a dog's tip by 0.5 m a side. One part. Engagement counts only toothed length. | One slider moving several rows. | W8 J4 (refined) |
| K11 | **(the user's, 2026-11-16) The user's edit to an app-owned value is never set back without their word.** A part's, the layout's or a carrier's global, a Face Z equation, a slide value in a configuration, or a recorded mate's flag in a configuration, found live different both from what the record says the file holds and from what the workbook now asks, and not explained by a lost or unsaved Update (the record's `unsaved` and `mismatched` marks), refuses the Update before any change, every such value named at once with both values and the cell to change. A gear's turn stays W5's (put back when Update must move a gear), since turning is motion, not an edit. | Setting it back (today); keeping the user's value and saying so. | W5's D10 for a mate the user suppressed |
| K12 | **(ruled) The Workbook window fits its screen (W9a, §2.6).** It never grows past the primary screen's work area less its frame; between a fixed header and a fixed footer, the two columns scroll as one page when the window is shorter than they ask; the footer has a ceiling (a third of the work area), above which its sentence scrolls in itself, and the body a least height, so the buttons are always whole. Drawn on the board first; the window check asserts on a 2560 × 1600 screen at 150 % that the frame's bottom is inside the work area, the footer whole and the body's last line reachable. | Growing without a cap (today, `workbook_gui.py:1160-1170`); scrolling the Checks panel alone; the whole window scrolling as the strip's page does. | UI-DESIGN §9 "grows taller … moves left or up" |

### 0.3 STOP and ask (implementers)

- **Anything that would write to, delete, move or rename a component, mate, feature, global or configuration that is
  not on record**, with two exceptions: route (c)'s move of a user's locked component with its gear
  (K2, added after S0): a user component rigid to a put gear through the user's locks on in the mode shown is moved
  by that gear's rigid motion, in that mode, and each one is read back by `place_component`; and W9d's writes into the
  **new** revision's assembly (the user's components inserted, their mates remade there, left unsaved), never into
  the old assembly or a user file. (Route (b)'s suppression of the user's mates around a put, an exception here
  before S0, is ruled out with route (b) itself: K2's *Instead of*; dropped at W9a package A's review, point 18.)
  The user's open documents are never saved by W9, and a configuration of theirs is never shown, unless S5 finds no
  unshown read of a component's state per mode: then, and only then, W9d shows the old assembly's modes and restores
  its active configuration, read back, with `GetSaveFlag` unchanged (a third exception, to be confirmed). The fake fails
  a test on any other such call, and on SolidWorks each demonstration compares every user item's flag, error code and
  entities before and after, in the old assembly as well after a Build again….
- W9d: a persistent reference that resolves to an entity of another kind than the one it was read from (a face where
  an edge was); a remade mate SolidWorks accepts with an error code it did not have in the old assembly but the app
  counts as remade; any file time of a user document changing during a Build again….
- A read W9 adds (a mate's entities, a part's feature tree, a feature's error, an external-references list) found
  marking a document modified (`GetSaveFlag`), or reading `None` for a component other than the assembly's own.
- A put with a user mate on its gear that SolidWorks accepts while leaving the gear off its frame without an error
  code; a user mate that route (b) cannot turn back on.
- Any dialog: from a rebuild that fails on a user feature (What's Wrong), from inserting or deleting a component.
- A new component or mate whose per-configuration state does not read back as set.
- A fixture answer (§3), including a W8 fixture's warnings, that disagrees with the code once written; a shape the
  interface commit pins changed.

---

## 1. What happens today, traced to code

### 1.1 How the app knows its own

The link record's `GearboxRecord` (`store.py:554-607`) lists the layout part and its component, each gear's
`ComponentEntry` (`store.py:494-510`: part, `Name2`, frame, per-configuration frames), every mate by name
(`MateEntry`), the carriers and the modes. Each part's `.gear.json` lists its globals and features. Nothing records
what the user added. Every gearbox built since W5 is a turning one (static only with a W5 finding missing), so
Update runs `swbuild._update_motion` (`swbuild.py:4453`), and with modes its W8 branch.

### 1.2 (a) The user adds features to an app-built part (a keyway, a fork groove)

- **Update with a value change on that part** (face, backlash, a tooth change on a gearbox without modes, since
  `GEAR_MATE_RATIO_ROUTE = "remake"`, `findings.py:670`; a dog-and-sleeve tooth change on one with modes, since
  couplings are not in `_wanted_teeth`, `swbuild.py:3816-3827`): the part is passed with its globals and no feature
  list (`workbook/update.py:165`); the check reads only that every app global is still there (`swbuild.py:2481-2493`);
  `update_variables` sets the globals that differ and rebuilds once (`swbuild.py:1365-1384`). **The user's features
  are left in the part** and SolidWorks rebuilds them; whether a keyway on the bore survives, only SolidWorks can
  tell. If the rebuild reports an error, the app records a failure (*"SolidWorks reported an error rebuilding …"*,
  `swbuild.py:3368-3369`) and stops before the remaining parts and the assembly (`:3580-3596`); whether a user
  feature's error makes it report one is unmeasured. A user mate or component already in error can likewise make the
  assembly's rebuild fail after values and flags were written, said as the app's (`swbuild.py:4173-4176`).
- **An app-owned value the user changed in SolidWorks** (Bore Diameter 10 → 12 to fit their shaft) is **set back**
  to the workbook's by the next Update (`planned_changes`, `swbuild.py:1323-1341`); so are the layout's globals, a
  Face Z equation, a slide value per configuration (`:4065-4072`), and a recorded mate's flag (D10, `:4182-4190`). It
  is unsaved, but undoing it means closing without saving, which also throws away the user's other unsaved work.
- **A tooth change of a meshed gear on a gearbox with modes** is refused in the check phase: *"The gear mate … would
  have to be made again, and making a gear mate of a gearbox with modes again is not in this version of Gear
  Generator, so nothing is changed; build the gearbox again."* (`swbuild.py:4695-4699`, ruling 9.16).
- **Build again…** reuses an unchanged part file as it is, the user's features with it (`workbook/gearbox.py:33-40`,
  `PartReuse.features`). A changed part, or one whose app global the user changed (`mismatched`, UI-DESIGN §9,
  *Build*, item 1), is made as a new file; the user's features stay in the old file only.

### 1.3 (b) The user adds components and mates among them (sprocket, chain, shaft, housing)

- **Components with no mates:** Update finds the app's components by `Name2` and never touches others. They enter
  the interference check, which runs on the whole assembly (`swcom.py:3356`), and a clash with a gear is reported
  under their names (`swbuild.py:2394-2413`). Nothing refuses.
- **Any mate among them refuses every Update.** The check phase walks the assembly's top-level mate group
  (`swcom.py:2380-2409`) and, without modes, raises at the **first** unsuppressed mate not on record, whatever it
  joins (`swbuild.py:4593-4602`): *"Mate12 is a mate in RangeBox.SLDASM that Gear Generator did not make, and it may
  hold the gears where Update SolidWorks would put them, so nothing is changed; suppress Mate12 in SolidWorks and
  press Update SolidWorks again."* With modes the same is judged in every mode and raises at the first mate on in any
  (`swbuild.py:4086-4100`). A user with six mates learns of them one press at a time. Something in the mate group that
  is neither a mate nor a folder refuses too (`:4582-4591`). A configuration of the user's is left alone and listed
  (`:4047`), but Update refuses while it is the active one (`:4040-4045`).

This is the code behind "I straight up cannot use the build app anymore": the refusal does not depend on whether the
user's mate touches anything of the app's.

### 1.4 (c) A mate between the user's component and an app-built gear

Refused exactly as in §1.3. If the user suppresses it as told, Update goes ahead and may put that gear. With modes,
any press that changes a value, a slide value or a Face Z sets `moved` (`swbuild.py:4213-4215`) and puts every train
in every mode (`needed = moved or …`, `:4346`); trains are joined over every mode's links, couplings included
(`workbook/update.py:1400-1402`, `:1416`), so in RangeBox the Sun, planets, carrier, both dogs and the sleeve are one
train. When the user turns their mate back on, SolidWorks moves their component or reports the mate in error. A user
mate that fully defines a gear makes the post-check say *"Sun cannot turn: SolidWorks reads it fully defined."*
(`_free_to_turn`, `swbuild.py:1068-1083`), blaming nothing of the user's.

### 1.5 (d) Then the workbook is edited and the user presses

| Edit | Update SolidWorks | Build again… |
|---|---|---|
| A value (face, backlash, bore), a slide offset, a dog-and-sleeve tooth change | Goes ahead (globals set; gears re-placed or put), **unless the user has any unsuppressed mate** (§1.3) | — |
| A tooth change of a meshed gear, no modes | Goes ahead, gear mate remade; same refusal for user mates | — |
| A tooth change of a meshed gear, with modes | Refused (ruling 9.16, §1.2) | Offered |
| A new gear (the hub) | Not run: *"Hub is new, and Update SolidWorks cannot add a part to what was built."* (`workbook/update.py:410`); also a new shaft (`:428`), a new mesh (`:450`) | Offered |
| A Modes pick between existing positions | Goes ahead (J14); same refusal for user mates | — |
| Modes rows added or removed, a new slider, a new coupling | Not run (`workbook/update.py:1292-1310`, `:1350-1359`) | Offered |

Classify's structural cases are decided on the Tk thread without reading SolidWorks, so they reach the *Build
again?* question without the user's work ever being seen. The question (`ui_text.py:2098-2184`) says what the new
revision makes and reuses and *"Nothing is overwritten, and RangeBox.SLDASM stays as it is on disk, but it shares the
reused parts …"* (`:2174-2183`); **it never says that the user's components, mates, or features in parts made new
stay behind.** After it, the record's current revision is the new one (`gearbox.py:17-31`), and every later Update
acts on it alone (`workbook/update.py:377`, `:386`).

### 1.6 Plainly

**Safer than feared:** no path deletes a user component, mate or feature, or rewrites a part file. Update never
deletes a document and never saves (PLAN-WORKBOOK §4.5 line 444; `swbuild.py:3415`); the only things it deletes are
its own equation in `detect_trig_units` and its own gear mate when it remakes one, by name. It refuses in a check phase
that writes nothing. Build again… never overwrites a file (`SAVE_AS_OVERWRITES` guard, `findings.py:57`).

**Where the fear is justified:** (1) Update sets back the user's edits to app-owned values (§1.2). (2) A later Update
of the new revision that changes a shared part changes the old assembly's geometry under the user's mates (said,
`ui_text.py:2177-2181`). (3) Build again… strands the work: the link moves to the new revision, and a part made new,
even only because the user changed one of its globals, leaves their features behind. (4) A renamed component or mate
forces Build again… (`swbuild.py:4713-4714`). (5) A user item in error may make the app's rebuild fail mid-change, said
as the app's.

**Where it is unusable:** one unsuppressed mate of the user's anywhere refuses every Update, one name per press, and
every structural edit sends the user to Build again…, which leaves their work behind without saying so.

### 1.7 Problems 1–3 in the code

- A sleeve is the strip's internal ring at the row's teeth, module and face, toothed over its whole face; a dog the
  spur plan (`gears/clutch.py:1-13`, J1: no fork groove, hub or chamfers). Its only bore is the teeth.
- Engagement: a sleeve engages a dog on another shaft when it covers the dog's whole face (`modes.py:178`); a sleeve
  covering a dog on its own shaft is a warning that it engages nothing (`modes.py:164-168`). Nothing checks how a
  sleeve is held on its shaft or whether its shaft can reach it.
- The bridging warning fires only when `length > gap` (`modes.py:342`): equal is silent, so a neutral flush against
  two dogs at 0 mm is not reported (§3).
- The Gears sheet has no column a band or relief could be written in (`schema.py:138-161`).

---

## 2. The behaviour proposed

### 2.1 Problem 4: keep the user's work, keep the app usable (W9a, then W9c)

**W9a — the user's work is theirs.**

1. *Ownership (K1),* including the renamed component found by its part path.
2. *Reads.* In the check phase each mate not on record is read for the components its entities are on
   (`IMate2.MateEntity(i).ReferenceComponent`, `None` for the assembly's own planes; verified on 2024 only in the
   macro database, `API-LEDGER.md:602`, so new on 2026) and for whether that component is fixed (`IsFixed`, read
   already). Each app part the job opens has its feature tree walked (a walk shown to mark nothing,
   `swbuild.py:2452-2455`); features its plan did not make are the user's. The error code of every user mate,
   component and feature is read before any change, so one already in error is named before the press and a later
   rebuild failure is not laid to the app.
3. *Mates on put gears (K2).* A user mate whose entities are all on the user's components, the layout component or
   the assembly is left alone and listed. One on a gear or carrier this press may put (without modes, from
   `train_check` and the placements; with modes, every gear of a mated train whenever the press changes anything,
   `swbuild.py:4213-4215`, `:4346`) goes through by **route (c1)**, the route S0 found to hold (amended after S0,
   K2): in the mode shown, after the app's locks, gear mates and couplings on there are suppressed and the assembly
   rebuilt, the app's bodies are put (carriers first), then each user component rigid to a put gear through user
   locks on in that mode, directly or through a chain of user locks (the chain read from each lock's entities in that
   mode, item 2's read), is put by its gear's rigid motion (G_target · G_before⁻¹ · U_before) and read back by
   `place_component`; then a rebuild and the app's mates back on, as `_put_train` turns back its own. The user's locks
   are left on and nothing else of the user's is written. Any other user mate on a gear this press puts that ties a
   user's component to it (a user gear mate, a mate to a gear's faces or planes, a user lock whose flag differs
   between the mode put and another) refuses before any change, named, until that kind is measured (K2). Beside
   this, the **grounded tie** — a train SolidWorks reads not free to turn with the user's mates on (K2) — refuses,
   naming every user mate on **that train** at once with its modes, the train as the mode read joins it (a tie on
   one gear makes the whole train read fully defined through its gear mates and that mode's couplings, so the gear
   that reads not free may carry no user mate at all; S0 read RangeSlv outside the tied set in N, where it is not
   coupled):
   *"Update SolidWorks must turn Sun's train back to its built place, and with your mates on SolidWorks reads it as
   unable to turn: Lock3 ties Sun to Housing-1, so nothing is changed; suppress Lock3 in H, N and L and press Update
   SolidWorks again."* "Where the app's own mates leave it free" comes from the record (the build's or last Update's
   post-check passed); nothing is suppressed to find it out. The read in the mode showing is made before any change.
   When every user mate on the train has the same flag in every mode (`mate_suppression`, read without showing), that
   read decides whether a tie stands in every mode, since a user mate that grounds a gear grounds it whatever the
   app's per-mode mates do (S0's C read H and L alike; which bodies it holds follows each mode's couplings).
   Only when a user mate's flags differ by mode is another mode read when shown (J25), before its put; a tie there
   stops the job before that mode's put, with what was already changed said and left unsaved, as any failure after the
   check phase is (W4 review B1). A user mate joining gears of two trains (a lock from Sun to RangeSlv) reads free but
   no put can satisfy it; the inventory finds it (both entities on app gears of different trains) and the press
   refuses before any change, naming it. The post-check's *"cannot turn"* sentence (`_free_to_turn`) names the user's
   mates on the train.
4. *Values (K11).* The check phase already reads every global, slide value and recorded flag live; a user's edit
   refuses before any change, all named: *"Bore Diameter in Gear_m1.25_N17 is 12 in SolidWorks and 10 in the
   workbook: type 12 in Gears!J5, or set it back in SolidWorks, and press Update SolidWorks again."*
5. *Features (K3).* After the rebuild each user feature's error state is read and any in error named as theirs
   (*"SolidWorks rebuilt your Keyway in Gear_m1.25_N17 after the new teeth, and it is in error."*). A rebuild error
   that comes only from the user's features does not stop the job, if M3 shows the rebuild reports it.
6. *Told before (K4).* The finish of every job, a refused one included, records what it read of the user's work (link
   record schema 7, §2.4: per part path the user's features, and the user's components and mates with what each
   touches, fixed or not, with the time read). The footer's Update line then says, before the press, what Update
   would change, which of the user's components it would put with their gears (route c, item 3) and what it leaves
   (*"Update SolidWorks changes RangeSlv's part, where your Keyway follows the app's features; it turns your
   Sprocket-1, which your Lock3 holds to Sun, back with Sun, and leaves Chain-1 and 6 mates of yours as they
   are."*). The
   worker reads again; what the record did not hold and would refuse refuses before any change and is recorded, so
   the footer says it; the next press refuses again unless the user has dealt with it.
7. *The window fits its screen (K12, §2.6),* since items 4 and 6 add words to the footer.
8. *Build again… until W9d (K5).* The question gains, from the record and with its time: *"As read at 14:02, your
   Sprocket-1, Chain-1 and 6 mates stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N17, which Sun's new
   part replaces; RangeBox_r2 has none of them."* The build job reads the old assembly's user items first (as it is
   in the session when open, never shown in another mode), and its result lists what stayed behind as found.

*What the user can do after W9a* (RangeBox with modes, a bore feature in a gear part; route (c) taken, the sprocket
held to its gear by the user's locks, K2):

| Press | Sprocket mated only to the layout or to the user's own shaft | Sprocket mated to Sun or RangeSlv, nothing of it grounded |
|---|---|---|
| A slide offset, a face, a dog-and-sleeve tooth change | Works; the bore feature kept, named if in error | Works; the sprocket found on its gear after |
| A tooth change of Sun, Planet or Ring | Build again… (9.16) until W9c | Build again… until W9c |
| Add the hub | Build again… until W9c | Build again… until W9c |
| An app value the user edited in SolidWorks | Refused, named, until the workbook or SolidWorks agrees | Same |
| A quiet press | Works | Works |

**W9c — Update adds, removes and re-mates (K6).** A new gear on an existing frame shaft along Z± is built as a part
(the build's part path), inserted into the open assembly (`AddComponent5`, used by the build), mated as the build
mates it (axis, along or lock, spline, mesh or coupling), and every new mate's and the new component's flag set and
read back in every configuration (the macro database: a mate made while a mode is active comes out suppressed in
some configurations, `API-LEDGER.md:220`; the J10 discipline). If it becomes its shaft's anchor (J9: the issue's hub
on Output, where the sleeve was a sliding anchor), the sleeve gains its spline mate. A gear that anchors no other gear
is removed with its app mates (a delete probed ahead, P1); a user mate on it, or a user part with in-context
references to it (an external-references read, new), refuses the removal before any change, named. A coupling or
sliding mesh newly needed between components on record is made as the build makes it, with its per-mode flags. A gear
mate of a gearbox with modes is made again by W5's remake route (delete, add, rename; `findings.MATE_DELETE_ROUTE`)
with its flags set and read back in every configuration, lifting ruling 9.16. Bands are added to a built sleeve in
place (§2.4). Inserting a component into a configured assembly and setting its state per mode (M5) is also what W9d
needs for the user's components.

**Modes rows added or removed, by Update (W9c; ruled by the coordinating session after the second review).** No call
here is new to the app: `AddConfiguration2` and `DeleteConfiguration2` are the build's own, verified on both versions
by W8's configurations probe (`API-LEDGER.md:138-139`, `:220`), and every flag and slide value per configuration is
set and read back as the build sets them (J10). What is new is the context — a saved, reopened assembly holding the
user's items — and that is what W9c's full build measures beside M5 and M6 (M10). A **mode added** is added as the build
adds one (a configuration copied from the active mode, so the user's components and mates there take the active
mode's state, said by name), handles fetched again after it (ruling 9.4), the top-only rebuild before any flag
(`API-LEDGER.md:333`), then every app mate's flag and slide value set in it and read back; a coupling or sliding
mesh it newly needs is made as above. A **mode removed** has its configuration deleted with nothing shown (deleting
a configuration other than the active one does not stale handles, `swcom.py:2950-2952`); removing the mode showing
refuses, naming it (*"show another mode and press again"*); removing the first mode makes the next one the mode the
record opens in, said. A mode **renamed** stays Build again…: the rename call (`IConfiguration.Name` put) is
unverified and J10 avoided it, and a delete-and-add would lose the user's own states in that configuration. Ruling
9.1 stands: a mode removed that leaves a coupling or sliding mesh on in no mode is Build again….

**Still Build again… after W9c** (from `workbook/update.py:404-453`, `_turning`, `_modes` `:1292-1368`; each said
in the question): a gear that anchors other gears removed; a shaft added or removed; a Modes row renamed, or one
removed that leaves a coupling or sliding mesh on in no mode (ruling 9.1); a gear starting or stopping to slide; a mated gear moved to another shaft; a Z± flip; a shaft starting or
ceasing to stand still; a shaft coordinate reaching, leaving or crossing its base plane (every RangeBox shaft is at
X = Y = 0, so moving one off the axis is structural); an anchor's face or a slide value reaching the Front plane; the
number of planet copies; a shared part splitting; a part whose file must change (Flank, Part name, a bevel's form); a
renamed app mate (`MateGone`). These are the edits that still reach Build again… once W9c lets Update add, remove and
re-mate in place, and the only ones W9d's carrying serves; that is why W9d can come last.

*Not taken:* a check-only job and a question before every Update (K4 says it in the footer); narrowing ruling 9.18 to
put only the trains whose frames change (it rests on s2's measurement that a mode not put can be left turned, and
would not cover the slider's train); replacing a part's component (delete and insert drops the user's features in the
old part from the assembly, M3 of the review; `ReplaceComponents2` keeps mates but is new to the app with a dialog
risk; both deferred, and with bands in place the issue's fix needs neither).

### 2.2 Problem 1: reachability, and the hub

**The rule (K7), by the points the shaft must reach.** A shaft is *present* at least over the closed interval between
the outer faces of its gears on that axis; a carrier's planets count as its gears and their faces as its presence (its
plate and pins sit there). A sleeve S on shaft O has a span along the axis in each position. O must reach under S in
every position (S is keyed to O there), so:

- from the Z− end, O must reach the point **p− = the largest start of S's spans** (with a hub row, the hub's start);
- from the Z+ end, the point **p+ = the smallest end of S's spans** (with a hub row, the hub's end).

**The Z− end is blocked** when another coaxial shaft P is present across p− (its interval holds p− with more than
`COVER_TOLERANCE` to spare on each side) and has a gear reaching more than `COVER_TOLERANCE` below p−; **the Z+ end**
likewise above p+. At p, P runs inside whatever keys S to O; at that gear O would have to run inside P; two tubes
cannot cross. **Warn when both ends are blocked**, at S's Gears cell. The rule uses only the least each shaft must span,
so a warning is certain. With bands and no hub row, the band that would ride a hub is unknown, so each band is tried
in place of the whole face and the warning is given only when every band is blocked both ways.

*The issue's box (§3).* Spans −34.5…−24.5, −29.5…−19.5, −24.5…−14.5: p− = p+ = −24.5. Input is present over
−34.5…15.5 (HighDog to Sun), across −24.5. Toward Z−, HighDog (−34.5…−29.5) reaches below; toward Z+, Sun (5.5…15.5)
reaches above. Both blocked: *"Gears row 7: Output cannot reach RangeSlv: Input runs through RangeSlv's travel (from
Sun at 10.5 to HighDog at −32), so Output would have to pass HighDog toward Z− or Sun toward Z+, each on Input."*
Carrier (present −19.5…15.5 with its planets) is not across −24.5.

*W8's fixtures* (§3 pins them). RangeSlv (At 60, face 8, −10/0/+10) spans 46…54, 56…64, 66…74: p− = 66, p+ = 54. In
TransferCase_Parallel, Lo is present over 25…73 (LoGear 25…35 below 66, LoDog 67…73 above 54): both blocked, a
warning. In E4, Carrier is present over 15…73 (planets 15…25 below, LoDog above): both blocked, a warning, which
toward Z− rests on counting the planets. ModeSlv (At 100, 0/+10; p− = 106, p+ = 104) is reached from either end in
both fixtures: no shaft is present across 106 or 104 (FrontDrv starts at 107). So both W8 fixtures, as built on
SolidWorks, have the issue's defect; §6 item 5 asks whether to correct them.

**The hub (K8).** The user decided on 2026-11-14 that a carrier is a skeleton because its plate and pins depend on
the gearbox at hand. A hub is mostly not that kind of thing: its working part is the sleeve's own teeth, which the
workbook already specifies, as J1 reasoned for the dog, and its place and width are numbers the checks need. What does
depend on the gearbox at hand is how it is fixed to its shaft (key, spline, press fit), and that stays the user's, as
it is for every gear's bore. So: a `hub` row (one new kind word) on the sleeve's shaft, built as a dog's toothed ring
with the row's Bore; a band of the sleeve must cover it whole (or it the band, the narrower covered) in every mode,
else an error at that mode's cell; it engages nothing and, as a non-sliding gear, becomes its shaft's anchor with the
sleeve splined to it (J9). The app never adds a hub by itself (Export writes named cells, never rows). This overturns
J1's "no hub", and says so. The user chose this on 2026-11-16 over a `hub` row checked but not built (a skeleton) and
over leaving it to them. A sleeve with no hub row is warned of: *"Gears row 7: nothing keys RangeSlv to Output: its whole
bore is teeth and no hub row is under it; add a hub on Output that a band of RangeSlv covers in every mode."*, adding
when none could fit *"; as laid out none can, since its 10 mm face slides 10 mm (H −5 to L +5) and its places share no
length."* It warns on both W8 fixtures (§3).

### 2.3 Problem 2: minimum running clearance (K9)

In every mode, for every dog or hub on another coaxial shaft that a toothed band of the sleeve does not engage there,
the axial gap between them must be at least **c = max(0.5 mm, 0.5 × module)** (0.625 mm at module 1.25). Scaled by
module because the chamfer and backlash a real dog needs scale with the tooth; floored so a fine module still gets
room. A gap from 0 up to c is a **warning** at that mode's Modes cell: *"Modes row 3: in N RangeSlv stands 0 mm from
HighDog and 0 mm from LowDog, which it does not engage there: leave at least 0.625 mm (0.5 × module) each side."* A
hub and a dog on different shafts are held to the same gap. The `length > gap` stroke warning stays for the travel
between positions. W8's fixtures are not newly warned: their least gap is 3 mm against c = 0.75 mm.

### 2.4 Problem 3: bands and the relief bore (K10), and the record

*Schema.* Two numeric Gears columns (working names **Start band** and **End band**, mm; the interface commit and the
board settle the words): the toothed length at the face's start (its end toward the shaft's Axis minus side) and at
its end. Blank both: toothed over the whole face, as today. Numeric cells avoid the Excel traps PLAN-WORKBOOK already
meets (`5-21` reads as a date, `-8` as a formula). Errors at the cell: bands on a row that is not a sleeve, a band not
positive, bands that leave no relief or exceed the face. More than two bands is not built (an error naming no phase).
The workbook stays at Format 1, as W8 added columns at Format 1: an older app reads a banded sleeve as toothed over
its whole face, which in `RangeBox_Fixed` jams L and is refused there, an acceptable failure.

*Engagement.* Each band is judged as a sleeve is today: a band covering a dog's whole face engages it; a band covering
part of one is an error. A dog under the relief is not engaged and must lie wholly within it (else the partial rule
catches it). Clearance (§2.3), the stroke warning, the hub rule and reach work per band.

*The part.* The strip's internal ring over the whole face, with the teeth removed over the relief to a diameter of
**m(z + 3)**: above the sleeve's root at either tooth depth the strip uses (m(z + 2.8) or m(z + 2.5)) and 0.5 m a side
over a dog's tip m(z + 2). A typed Rim must clear it (error). The op route is the interface commit's to choose from
proven ops; the herringbone groove's two blind extrudes and a plain ring between (`gears/helical.py:19-24`) are the
precedent; `Cut` has no blind depth today (`gears/base.py:254-258`). The bands are globals of the part, so a band
change on a banded sleeve is a value Update. *In place (W9c):* bands given to a sleeve built without them are added to
its part file — the band globals and the relief features, the same ops the build makes, run on the opened part — so
RangeSlv keeps its file, the user's groove and every mate; bands taken away suppress the app's relief features. This
is new (features added to an existing part) and is measured in W9c's full build (M8).

*The record.* W9a's link record is **schema 7** (the user-work inventory, K1's found names); W9b's is **schema 8**
(the bands in a sleeve's spec), so a W9a-era app refuses a W9b record as `store.py` refuses any newer one and leaves it
as it is; W9c adds nothing to the record's shape (its added components, mates and modes are entries of the kinds
schema 6 already has) and W9d's carried items make it **schema 9**. A part with bands writes its `.gear.json` at sidecar **schema 2** (`store.py:30` is 1 today), since
`GearSpec.from_dict` drops unknown keys (`spec.py:158-160`) and an older app would otherwise reuse a banded sleeve as an
unbanded one; a part without bands stays at 1.

*Not taken:* one slider moving several rows. It gets engagement right with no new geometry but builds the loose parts
the issue complains of, needs a rigid mate between them, and has no relief bore.

### 2.5 Build again… carries the user's work (K5, W9d)

The user answered (2026-11-16) that a new revision must carry their components **and** remake their mates, naming a
mate that cannot be remade. It is a stage of its own, **W9d, the last**: it needs W9a's reads (a mate's entities and
components, the inventory) and W9c's insertion and mate-making in a configured assembly with every flag read back (M5,
M6). Once W9c lets Update add, remove and re-mate in place and add or remove modes, only the edits listed at the end of
§2.1 still reach Build again….

**When it runs, and what it never does to the user's documents.** In the Build again… job, after the new revision's
assembly is built, checked and saved exactly as today (`SaveAs3` with option 1 saved no referenced document,
`swbuild.py:2898-2906`), so the app's own result never rests on the carried items. The job then reads the old
assembly's user items: as it is in the session when it is open there (never closed, never shown in another mode),
opened read-only when it is not (`OpenDoc6` with the read-only option, new, in S5). Component state per mode is read
without showing a mode if S5 finds a route, as `IsSuppressed2(3, names)` was for mates (`API-LEDGER.md:332`); if it
finds none, the old assembly's modes are shown and its active configuration restored and read back, `GetSaveFlag`
unchanged — the third exception of §0.3, stated there. Frames are read in the old assembly's active mode only. The
job then inserts and mates the carried items in the new assembly and checks them, and **leaves them unsaved**, as
Update leaves everything (PLAN-WORKBOOK §4.5): the result ends *"… RangeBox_r2 holds them unsaved: save it in
SolidWorks to keep them."* No `Save3`, a call the app has never made, whose effect on modified referenced documents
(the user's sprocket open with unsaved edits) is unmeasured. If carrying stops part way, what was carried is said, and
the saved new assembly and the old assembly are untouched on disk.

**What is carried.**

| Item | Carried | Not carried, and named |
|---|---|---|
| A top-level user component (a part, or a sub-assembly by its file) | Its file and referenced configuration; fixed or floating as it was; its suppressed or resolved state in each mode (by mode name; a mode new in this revision takes the first mode's state, said). Placed where it stood **relative to its app component** — new frame of that component · old frame⁻¹ · old frame of the user component — so a sprocket locked to a turned Sun goes in at the same angle to Sun; a cluster tied to no app component is placed by its world frame. Placed once, in the first mode: a floating component that stood differently per mode stands, in the new revision, where it stood in the old assembly's active mode, said. | A virtual component (no file to insert; saving it out would write a file of the user's); a flexible sub-assembly's flexibility (carried rigid, said); display states and appearances set in the assembly |
| A mate of the user's | Coincident, concentric, parallel, perpendicular, tangent, distance, angle (with limits), lock and gear, with alignment, flip, values and flag in each mode, whenever its entities are found | Width, path, slot, symmetric, profile-centre, cam, hinge, rack-and-pinion, screw, universal-joint and belt/chain: named as kinds this version does not remake; any mate whose entity is not found (below) |
| **A feature of the user's in an app part this revision makes new** | — | Named before the press (from the inventory, with its time) and in the result, with why the part is new and that the old file keeps it: *"your Keyway is in Gear_m1.25_N17, not in Gear_m1.25_N17_r2, which is new because Sun's Flank changed; RangeBox.SLDASM and that file keep it."* Every mate on its faces is named with it. Where the part is new only because the user typed an app value in SolidWorks (`MISMATCHED`, K11's case), the sentence says how to keep it: *"type 12 in Gears!J5 and Build again… reuses the part with your Keyway."*; where it is new only because an Update left it unsaved (`UNSAVED`): *"save it in SolidWorks first and Build again… reuses it with your Keyway."* |
| A user component pattern or mirror | Its seed component | Its instances (a pattern is an assembly feature the app does not make) |
| The user's assembly features, sketches and reference geometry | — | All; a mate on them is named |
| A user part's in-context reference to an old app component | — | Said: the user's file still refers to the old assembly |

**How each mate's entities are found in the new assembly.** Components map first: a user component to its new
instance; an app component by the record's gear id (planet copy *k* to copy *k*; a gear or copy that is gone means
not found); the layout and each carrier to the new revision's.

1. *On a file both revisions use* (every user component; an app part reused as the same file): its persistent
   reference, read in the part through the component (`GetPersistReference3` on the part-level entity), resolved in
   the new instance (`GetObjectByPersistReference3`, then the component's corresponding entity). Same file, same
   reference. User-to-user mates always come under this tier.
2. *On the layout part or a carrier part* (new files every revision, `<Name>_r<n>_Layout`, `<Name>_r<n>_<C>_Carrier`)
   *or the assembly itself*: by name for what the app names (`"Output Axis"`, a shaft's `"X Plane"`, a carrier's axes
   and planes, `layout.py:219`, `:512`), and **by tree order** for every base plane and origin, never by its English
   name (`swcom.py:1310`): on a non-English install "Front Plane" is not its name. A shaft gone means not found.
3. *A lock or gear mate* references whole components, so on an app part made new it is found through the component
   map, never "not found" for that reason.
4. *A face, edge or vertex of an app part made new* is **not** re-found **(ruled)**: its persistent reference belongs
   to the old file, and finding it by its geometric role would serve only the edits that change a part's file (a
   Flank or Part name change), which are rare. The mate is named with why: *"Concentric5 was on Sun's bore, and Sun's
   part is new because its Flank changed; it was not made again."*

**What is made, and the fallback.** Every mate whose entities are found is remade, and every other is named with
why; the user's components stay floating where they were placed (or fixed, as they were): SolidWorks leaves an
under-defined component where it stands, and dropping a mate cannot over-define anything. A remade mate that comes
back with the same error it had in the old assembly (W9a reads every user mate's error code) is carried as it was and
said, not counted against its cluster. A **cluster** (the user's components joined through their own mates) falls back
only in three cases: a remade mate comes back in an error it did not have before; the cluster over-defines; or it ties
a gear (the build's own post-check, now with the carried mates on). Then the mates it has to app parts, the layout,
the carriers and the assembly's planes are deleted again (the job's own, just made in the new assembly, by
`MATE_DELETE_ROUTE`), its user-to-user mates are **kept**, and its components are fixed where they were placed, each
deleted mate named with why: *"Sprocket-1 and Chain-1 are fixed where they stood in RangeBox_r2: with your Lock3 and
Concentric5 made again SolidWorks reads Sun unable to turn, so those two were not kept; Coincident7 between them was."*

**The record.** The carried items stay the user's: they go into the new revision's inventory, with which mates were
remade and which named — link record **schema 9** (§2.4).

### 2.6 The window on a short screen (K12, W9a, ruled)

*Today.* `WorkbookWindow._fit` (`workbook_gui.py:1160-1170`) asks for `max(winfo_reqheight, current)` with no cap,
and keeps the window on screen against `winfo_screenheight()`, the whole screen, by moving it up. On this device
(2560 × 1600 at 150 %) Windows holds the window to 1570 px inside, and in the closing run's window check the built E4
footer's label ended at 1657 (`w8-window-20261116-031412.log:283`; it is 281 px tall): its last lines are cut
(`W8-REVIEW-SW2024-CONFIRM.md` question 3; `fb85bcc`). By the same arithmetic a 1920 × 1080 screen at 100 % would cut
it too (that review's S6; inference, not measured). W9a adds words to the footer and to what the window says before a
press, so it cannot be shown on this device until the window fits.

*The change* — a constructor change, not a rebuild of the window at run time. Rows 1-5 of `body`
(`workbook_gui.py:390-452`) are built into a frame inside a canvas, and the header and footer stay outside it, as the
strip's page is built (`create_window` with a width, then `<Configure>` setting the scroll region, `gui.py:270-316`).
1. *The cap.* The window never grows past the **primary** screen's work area (`gui._work_area`, `gui.py:1836-1849`,
   reused) less the window's frame (title bar and borders, as the strip subtracts 40 px, `gui.py:1999`), and is placed
   inside it. A second monitor is not followed.
2. *The body page.* Between the fixed header and footer **the two columns scroll as one page** when the window is
   shorter than they ask. The body keeps a least height (enough for the Checks panel's first lines).
3. *The footer's ceiling.* The footer may take at most a third of the work area; above that its sentence scrolls in
   itself, so the buttons are always whole whatever W9a's inventory and K11's lists add. (The other way — the lists
   moving to Checks with a count in the footer — is left for the board to weigh.)
4. *The scroll bar's width* is reserved always beside the body, counted in the left column's width
   (`workbook_gui.py:931`), so a bar appearing never narrows the column, re-wraps it and hides the bar again.
5. *The mouse wheel.* The strip binds `<MouseWheel>` app-wide (`gui.py:285`) and its `_on_wheel` (`gui.py:318-326`)
   scrolls the strip's page wherever the pointer is but the flyout, the Workbook window included. Both handlers act
   only for their own toplevel.

*Why the body and not the Checks panel, and not the whole window.* The strip's rule — "when the screen is shorter
than the strip, the whole page scrolls" (UI-DESIGN §1) — would, applied to the whole Workbook window, scroll the
footer and its buttons out of sight, the one part that must stay whole. Scrolling the Checks panel alone cannot
promise a fit: the right column (the end view and Speeds, eleven lines and the chooser on E4) can be the taller one,
and Checks may hold few lines. The body page is the strip's rule kept, with the footer pinned.

*What it contradicts, rewritten in the same package:* `test_the_window_keeps_its_width_with_update_shown_and_a_long_sentence`
(`tests/test_workbook_window.py:751-768`), which pins `height == winfo_reqheight()`; UI-DESIGN §9's three places that
say the window "grows taller" (lines 397-399, 557, and 1128, which adds "(a test pins it)").

*Done when:* the board is drawn first (a new board of the built E4 at 1570 px, the body scrolled, the footer whole);
UI-DESIGN's three places and the test rewritten; a Tk test with a forced work area asserting the footer's bottom
inside the window, the footer at its ceiling scrolling in itself, and the body's last line reachable; and the window
check's W8 stage on this device, on SolidWorks 2026 only (K12 is Tk alone), passing `w8_footer_whole` and two new
assertions: the frame's bottom (`GetWindowRect`) inside the work area, and the body's last line scrolled into view.

---

## 3. The fixtures

**RangeBox (the issue's two-speed planetary).** Shafts, all frame and at the origin along Z+ unless said: Input
(input, 1500 rpm, 10 N·m), Carrier, Planet (on Carrier, X 26.25, 3 copies), Ring (fixed), Output (output). Gears
(module 1.25, Box 20°, 98 %): Sun 29 on Input at 10.5 face 10; Planet 13 at 10.5 face 10; Ring 55 internal at 10.5
face 10; HighDog 17 dog on Input at −32 face 5; LowDog 17 dog on Carrier at −17 face 5; RangeSlv 17 sleeve on Output
at −24.5 face 10, Slides `H=-5, N=0, L=+5`. Meshes Sun–Planet, Planet–Ring. Modes H, N, L. (Names follow the gear-name
rule, so "High dog" is `HighDog`.)

*Before W9 (run through `assess` at `c351b1f`):* builds; four warnings, none about the clutch (the planet's undercut
and thin tip, the sleeve's tips inside its base circle, the undercut planet meshing the sun). H engages HighDog, ratio
1.000; N engages nothing, neutral; L engages LowDog, ratio 2.896552 (1 + 55/29); Carrier 517.857 rpm, Planet
−1673.077 rpm about its own axis. The same box with the issue's one long sleeve (face 26 at −35, H −7.5 / N 0 / L
+7.5) is refused: *"Modes row 4: in L RangeSlv engages HighDog and LowDog at once, which joins Input to Carrier: as
written the box is jammed in this mode."*, with the stroke warning and *"H and N engage the same"*.

*After W9b (the same workbook):* three warnings more: no hub, and none can fit (§2.2); Output cannot reach RangeSlv
(§2.2); in N 0 mm from HighDog and LowDog (§2.3). Engagement and speeds unchanged.

**RangeBox_Fixed (after W9b):** RangeSlv face 26 at −35, Start band 5, End band 5 (relief 16, Ø 25.0), Slides
`H=-7.5, N=0, L=+7.5`; Hub 17 hub on Output at −45.5 face 20 (−55.5…−35.5). Hand-worked answers to pin (checked by the
review):

| Mode | End band (front) | Start band (rear) on Hub | Relief | Engaged | Least running gap |
|---|---|---|---|---|---|
| H | −34.5…−29.5 covers HighDog | −55.5…−50.5 | −50.5…−34.5 | HighDog; ratio 1.000 | LowDog 10 |
| N | −27…−22 | −48…−43 | −43…−27 holds HighDog | none; neutral | 2.5 each side |
| L | −19.5…−14.5 covers LowDog | −40.5…−35.5 | −35.5…−19.5 holds HighDog | LowDog; ratio 2.896552 | start band to HighDog 1.0 |

Hub to HighDog: 1.0 (≥ 0.625). Reach: p− = −55.5 (the hub's start), and no other shaft is present across it: reached.
No warning from W9b's checks, no stroke warning. In SolidWorks: Hub is Output's anchor (axis, along), `RangeSlv
splined to Hub`, `RangeSlv along Output` with H/N/L values, couplings on in H and L only.

**W8's fixtures after W9b** (no change to their rows): TransferCase_Parallel and E4 each gain three warnings — *Rear
cannot reach RangeSlv* (Lo, respectively Carrier, runs through its travel from LoGear at 30, respectively the planets
at 20, to LoDog at 70), and *nothing keys RangeSlv to Rear* and *nothing keys ModeSlv to Rear*, each with "as laid out
none can" (RangeSlv's 8 mm face slides 20 mm, ModeSlv's 8 mm face 10 mm). No clearance warning. Every pin of their
warning counts moves by three. The key is checked by an independent agent, as W8's was.

---

## 4. What must be measured on SolidWorks

Under the rule: a full build first; a probe ahead only for a call new to the app that could hang, raise a dialog or
damage a file or session.

| # | Unknown | How |
|---|---|---|
| S0 | **W9a's spike**, which decides K2's route (brief below) | **W9a's first step**, 2026 then 2024 |
| P0 | A rebuild that fails on a user feature, with SolidWorks' "show errors every rebuild" on: does What's Wrong open | **Probe ahead** (a dialog), a scratch part with a feature made to fail, **first** in S0's session, about 5 min per version |
| M1 | Reading a user mate's entities' components on coincident, concentric, distance, angle, width, limit, path, lock and gear mates, user–user, user–layout, user–gear; a mate to a component inside a user sub-assembly (`ReferenceComponent` gives the leaf, its `Name2` a path); a mate suppressed in the active configuration but on in another mode; and that none of it marks a document modified (new on 2026) | W9a full build |
| M2 | The feature walk telling the plan's features from the user's; each user feature's error code after a rebuild | W9a full build |
| M3 | Whether a part's rebuild, and the assembly's rebuild, report failure when only a user feature or a user mate is in error | W9a full build, one section |
| P1 | Deleting a component from an assembly with configurations (`Select2` then `EditDelete`, or `DeleteSelection2`): any "delete mates too?" confirmation | **Probe ahead** (a dialog), scratch assembly, at the start of W9c's sessions on 2026 and 2024, before W9c's packages |
| M4 | An external-references read on the user's parts (in-context references to an app component) | W9c full build |
| M5 | `AddComponent5` into a reopened assembly with mode configurations: its state in each configuration, set and read back | W9c full build |
| M6 | Mates made in that assembly (axis, along, spline, coupling) and a gear mate remade there: flags set and read back in every configuration | W9c full build |
| M7 | The banded sleeve's part (the relief op route) on both versions | W9b's build of `RangeBox_Fixed` from scratch |
| M8 | Band globals and relief features added to a built sleeve part in place, the user's groove in it kept | W9c full build |
| M10 | A Modes row added and one removed by Update in a saved, reopened assembly holding the user's items: the new configuration's flags and slide values, the user's items' state in it, a configuration deleted with nothing shown | W9c full build |
| S5 | **W9d's spike:** each standard mate kind's definition read (type, alignment, flip, values, limits; the macro database's *assemblies/06, read every mate* is the start) and remade by `AddMate5`; a mate entity's persistent reference read through its component (`GetPersistReference3` on the part-level entity, the route from the assembly-context entity unverified) and resolved in a new instance of the same file in another assembly, then selected through the component's corresponding entity; a mate to a layout axis re-selected by name and to the assembly's first base plane by tree order; the old assembly opened read-only (`OpenDoc6` with the read-only option, new) when not open; a component's suppressed or resolved state read per configuration **without showing** it (the route sought); every read checked for `GetSaveFlag` | **In W9c's sessions** on 2026 and 2024, after P1, about 40 min and 60 min |
| P2 | Inserting a user **sub-assembly** by its file (it must be opened first, `API-LEDGER.md:531`), one with a missing reference among its own files: a "find file" dialog | **Probe ahead** (a dialog), in S5's session, about 10 and 15 min |
| M9 | Carrying on a whole Build again…: two clusters (a sprocket and its "chain" on Sun, a housing mated to the layout), one mate on a bore of a part made new, a keyway in Sun, the new revision made by an edit that still needs Build again… (Sun's Flank changed, so its part is a new file; a shaft added) | W9d full build |

**S0, W9a's first step, precisely.** On SolidWorks 2026 (34.1.1) in a session the agent starts, then on 2024
(32.5.0) in a fresh session (a 2026 file does not open in 2024, so each version builds its own). In this order:

1. *P0 first,* so a dialog costs nothing of S0: a scratch part with a feature made to fail on rebuild, with
   SolidWorks' "show errors every rebuild" as found (read, and if off, turned on for the probe and restored, read
   back); whether What's Wrong opens.
2. *Build* the issue's RangeBox (§3) through the app's own Build into a fresh output folder named in the run. Its built
   folder is kept as **S0's master**, which W9a's demonstration starts from on that version, so RangeBox is built once
   per version.
3. *Add the user's work* to a copy of the master (J24's scheme): a "sprocket" (a strip-built spur, 20 teeth, module
   1.25, face 6, Bore 10) on the Input axis in front of Sun, a second on the Output axis behind RangeSlv's travel, and
   a "housing" (an app-built part standing in) inserted fixed. They go in by `AddComponent5` into the reopened assembly
   with configurations — the first use of that context, ahead of W9c's M5, said in the log — and are mated by their
   parts' **named axes and planes** through `GetCorresponding`, as the app mates gears (`API-LEDGER.md:552`), never by
   faces picked by coordinate. Each case's setup is saved by the app's `save_as` **under a new name** (the proven
   route; `Save3` is new and not used).
4. *Cases*, each on its own saved setup:
   - **A** — sprocket 1's axis on the layout's `Input Axis`, locked to Sun;
   - **B** — sprocket 2's axis on `Output Axis`, locked to RangeSlv (the sliding train);
   - **C** — A plus sprocket 1's plane coincident with the fixed housing's (the grounded tie);
   - **C′** — C with that coincident suppressed in H and on in L (a user mate whose flags differ by mode, K2).
5. *In each case, in H and then in L* (each shown in turn): the train is turned +37° by the drive W8's s7 used, then
   put back to its built frames by the put s7 made the app's way (`s7_put_job`, `probe/workbook_assembly_check.py:7481-
   7531`: the app's locks off in that configuration, `place_component` per gear, locks on). Today's Update cannot be
   used: it refuses the user's mate. A and B run twice, each from its own setup: **route (a)** with the user's mate on,
   **route (b)** with it suppressed in that configuration around the put and turned back on. C and C′ run route (a)
   only: what matters there is the tie's read, and the put shows what SolidWorks does against it.
6. *After the last put of each case,* every mode is shown, the assembly rebuilt, and every body read again (s7's
   discipline), so a put that holds only until the solver next runs does not read as success.

*Reads,* before and after each put: each gear's and sprocket's frame (`component_frame`); whether the sprocket turned
with its gear by the same angle; each put gear against its target to 1e-6; every mate's error code and flag in every
mode, the app's and the user's; each gear's and sprocket's `constrained_status`, and for C and C′, before any put,
whether Sun's train reads not free in H and in L; `GetSaveFlag` of every document before and after every read.
*Time:* about 40 min on 2026 and 70 min on 2024 (W8's s1 took 946 s to build E4 and s7 about 165 s a case).
*Output:* a log and JSON under `probe/results/` (2024's under `sw2024/`), the kept master's path, and proposed
findings — `USER_MATE_PUT_ROUTE` ("carried" or "suppress around"), `USER_TIE_READ` (the constrained status a tie
gives, and whether the showing mode's read decides C′), the What's Wrong reading — reviewed before W9a's packages
start. *STOP:* any dialog; a document marked modified by a read; a put that holds in neither route; a mode found
moved after the every-mode read.

Each demonstration works on a copy of one built folder (J24's scheme) into which the script puts the user's work: a
part of its own (a block "housing", a strip-built "sprocket"), mates among them, to the layout and to gears, a keyway
in a gear part and a groove in the sleeve part.

---

## 5. Stages, in order

The user is watching usage and approved the stages at about 30 to 35 agent runs. The order is below, each stage
closing before the next is planned in detail. **W9a gives the app back soonest**; W9d comes last because W9c first
shrinks what reaches Build again… to §2.1's list. The coordinating session's savings after the second review are
taken (each listed in *Changes after the second review*, for the user to overrule): the sleeve checks merged with the
bands and hub (W9b), K12 inside W9a's package B, S5 and P2 run in W9c's sessions, W9b's 2024 build run in W9c's 2024
session, the window check on 2026 only.

**W9a — the user's work is theirs.**
- *First:* S0 with P0 (§4) on 2026 and 2024; their result picks K2's route and is reviewed before the packages.
- *Packages:* A (worker: the reads, K2 by the chosen route with the train's grounded-tie refusal and the two-train
  refusal, K11's refusals, errors read before and after, all names at once, `_free_to_turn` naming the user's mates on
  the train, the component found by part path); B (planning, link record schema 7, the inventory in the finish, the
  Build again… clause and the build job's read of the old assembly, the footer line; K12 (§2.6), the board first, then
  `_fit` capped and the body page, its Tk test and the three UI-DESIGN places; the boards' footers redrawn; the W99
  rename and the "last phase" edits of §0.1).
- *Tests against the fake:* user–user and user–layout mates never refuse; a user lock on a put gear goes through by
  route (c1) (amended after S0, K2): each user component rigid to the put gear through user locks on in that mode,
  a chain included, put by the gear's rigid motion after the app's bodies and read back, the user's locks left on and
  their flags untouched; any other kind of user mate tying a user's component to a put gear (a gear mate, a mate to a
  gear's faces or planes, a user lock whose flag differs by mode) refuses before any write, named; a grounded tie
  refuses before any write, the train's user mates named; a mode-dependent tie (C′) is read in the right mode; a
  two-train user mate refuses; no call targets an item not on record but route (c)'s puts of those components, and
  the fake fails on any other move of a user component; a user's edit
  to each kind of K11 value refuses, named, and one a lost Update explains does not; user features survive a value
  Update and one in error is named; the inventory reaches the footer before the press; the Build again… question names
  what stays behind with its time; K12's Tk test.
- *Done when:* the suite is green; on SolidWorks 2026, on a copy of S0's master with the user's components, their mates
  among themselves and to the layout, a keyway in a gear part, and **a user lock from a free sprocket to Sun and to
  RangeSlv**, a value Update and a slide-offset Update go ahead, the sprocket is found on its gear afterwards, every
  user mate is on in the modes it was on in and in no error, and the keyway rebuilt; a lock to a fixed housing refuses
  naming it; a Bore Diameter typed in SolidWorks refuses naming the cell; M1–M3 answered; the window check's W8 stage
  passes on this device on 2026 with K12's assertions; 2024 confirms the assembly sections; reviewed.
- *Cost:* S0 about 40 min on 2026 and 70 min on 2024; the demonstration about 1.5 h on 2026 and 2 h 45 min on 2024
  (W8 measured 1.6-2.2× on 2024: a press that puts every mode took 238 s on 2026 and 515 s on 2024); the window check
  about 15 min on 2026 (W8's took 12); about 11 agent runs (S0's script and run, its review; two packages, their
  reviews; the demonstration script, its review; the two runs' reviews).

**W9b — sleeves: the checks, the bands and the hub (problems 1, 2 and 3).**
- *Packages:* A (pure: reach, hub-length and clearance checks in `modes.py` and `checks.py`, the W8 fixtures' pins
  moved by three each, §3); B (schema, model, engagement per band, the `hub` kind and its rules, the relief op, record
  schema 8 and sidecar schema 2; the board for the Gears sheet's two columns, no window control).
- *Tests:* §3's answers for RangeBox, RangeBox_Fixed and both W8 fixtures; the open intervals and tolerance; a nested
  input through a hollow carrier not warned; clearance at exactly c clean, below it warned; old workbooks and schema 6
  and 7 records read as before; the banded plan equals the internal ring's plus the relief; an older reader refuses
  schema 8.
- *Done when:* green; `RangeBox_Fixed` built from scratch on 2026 (M7) with every mode's engagement, slides and
  interference as §3; the same build on 2024 in W9c's 2024 session; reviewed.
- *STOP:* any warning on a fixture other than §3's; the relief op failing on either version; a mode reading other
  than §3.
- *Cost:* about 30 min on 2026 and 50 min on 2024 (in W9c's session); about 6 agent runs.

**W9c — Update adds, removes and re-mates, and adds and removes modes (problem 4's "cannot add a part").**
- *First, in the same sessions:* P1, then S5 and P2 for W9d (§4); reviewed before W9c's and W9d's packages
  respectively.
- *Packages:* A (worker: insert, mate, per-configuration flags, delete with app mates, remake with modes, bands in
  place, a configuration added or deleted with its flags and values); B (classify: what moves from structural to
  Update, the remaining list said in the question; the sentences; UI-DESIGN §9).
- *Tests:* adding a gear on an existing shaft and a hub that becomes an anchor; removing a non-anchor gear, refused
  when a user mate or in-context reference touches it; bands added in place keeping a user feature; a new coupling
  made with its per-mode flags; a tooth change on a gearbox with modes remade and read back; a mode added (the user's
  items taking the active mode's state, said) and one removed; removing the mode showing refused; ruling 9.1 kept.
- *Done when:* on a copy of the built RangeBox with the user's work (W9a's), the workbook edited to `RangeBox_Fixed`
  and one Update adds Hub, gives RangeSlv its bands in place and leaves every user item as it was, the groove in
  RangeSlv kept, each mode then engaging and turning as §3; then a mode added and one removed by Update (M10);
  confirmed on 2024; reviewed.
- *STOP:* §0.3; P1 showing a dialog (then removal stays Build again…, put to the user).
- *Cost:* P1 about 10 min on 2026 and 15 on 2024; S5 and P2 (W9d's) about 50 min and 75 min; the demonstration about
  2 h 20 min on 2026 and 3 h 35 min on 2024; about 10 agent runs (the probes' script and run, its review; two packages,
  their reviews; the demonstration script, its review; the two runs' reviews).

**W9d — Build again… carries the user's work (K5, §2.5; the user's answer).**
- *Packages:* A (worker: the old assembly read without showing or saving it, the user's components inserted where they
  stood relative to their app components with their state per mode, each mate's definition read and remade on
  entities found by reference, name, tree order or component, every other named, clusters judged and fixed only in
  §2.5's three cases with their user-to-user mates kept, the post-check with the carried mates on, the carried items
  left unsaved); B (planning: what the question says will be carried and what not, the user's features in parts made
  new and how to keep them, from the record's inventory with its time; the result's sentences; UI-DESIGN §9).
- *Tests against the fake:* each row of §2.5's table, carried or named; a mate whose entity is not found named, its
  component left floating where it stood and its other mates remade; a mate in error before carried as it was; a
  cluster that ties a gear loses only its mates to app parts, the layout and the assembly, and is fixed; a sprocket
  locked to a turned Sun placed at its angle to Sun; nothing written to the old assembly or a user file, nothing saved
  after the first save, no mode of the old assembly shown (or, on S5's fallback, shown and restored); a mode new in
  the revision takes the first mode's flags.
- *Done when:* M9 on 2026: after Sun's Flank change and a shaft added, Build again… makes RangeBox_r2 with both
  clusters carried and their mates remade and on in the modes they were, the bore mate on Sun named, the keyway in
  Sun named in the question and the result, every app gear free to turn in every mode, the carried items unsaved, the
  old assembly and every user file unchanged on disk; confirmed on 2024; reviewed.
- *STOP:* §0.3; a dialog in S5 or P2 (then sub-assemblies come over fixed and unmated, put to the user).
- *Cost:* the demonstration about 1 h 15 min on 2026 and 2 h 15 min on 2024; about 8 agent runs (two packages, their
  reviews; the demonstration script, its review; the two runs' reviews).

| Stage | SolidWorks 2026 | SolidWorks 2024 | Agent runs |
|---|---|---|---|
| W9a | ~2 h 25 min (S0 with P0, demonstration, window check) | ~3 h 55 min (S0 with P0, confirming build) | ~11 |
| W9b | ~30 min | ~50 min (run in W9c's 2024 session) | ~6 |
| W9c | ~3 h 20 min (P1, S5 and P2 for W9d, demonstration) | ~5 h 05 min (the same, confirming build) | ~10 |
| W9d | ~1 h 15 min (demonstration) | ~2 h 15 min (confirming build) | ~8 |
| **All** | **~7 h 30 min** | **~12 h 05 min** | **~35** |

2024 is the larger half because every press that puts every mode takes about twice as long there; the 2024 runs are
split into fresh sessions per section, as W8's were. W8 took 16 review notes beyond its plan; the run counts allow
for one fix round per stage, not more. **Deferrable** (each its own follow-up, on the user's word): replacing a part's
file by Update; Update adding or removing a shaft, renaming a mode, or removing an anchor gear; finding a face by its
role on an app part made new; carrying the mate kinds §2.5 names, component patterns, and the user's assembly
features.

**What still reaches Build again… after W9c, and so what W9d is for:** a shaft added or removed; a Modes row renamed,
or one removed that leaves a coupling or sliding mesh on in no mode; a gear starting or stopping to slide; a gear that
anchors others removed; a mated gear moved to another shaft; a Z± flip; a shaft starting or ceasing to stand still; a
shaft coordinate reaching, leaving or crossing its base plane (on RangeBox, moving any shaft off the axis); an
anchor's face or a slide value reaching the Front plane; the number of planet copies; a shared part splitting; a part
whose file must change (Flank, Part name, a bevel's form); a renamed app mate. Of these, the ones a user with work in
the assembly is likely to make are a shaft added or removed, the planet copies, and a Flank or Part name change; for
all but the last, every gear part is reused as the same file, so W9d remakes nearly every mate.

---

## 6. For the user

**Answered (2026-11-16), and binding:** all the stages, in order (now four, W9a–W9d, after the second review's
merge); an app-owned value you changed in
SolidWorks stops Update, named (K11); Build again… carries your components and remakes your mates, naming any it
cannot (K5, W9d); the hub is built by the app from a row you write (K8).

**Still open, each going on at the recommended reading unless you overrule it:**

1. **A mate of yours on a gear Update must move.** *Recommended:* Update goes ahead — either nothing of yours is
   touched because the put carries your component with the gear, or your mate is switched off around the put and
   back on after, read back and said — chosen by a measurement at the start of W9a; it stops, naming the mate, only
   when SolidWorks reads the gear unable to turn with your mate on. *Alternative:* it always stops and names your mate
   (you suppress and unsuppress it by hand). *After S0 (2026-11-16):* neither of the two ways held for a component
   you locked to a gear; a third, which puts your locked component with its gear, held, and you accepted it (K2). A
   mate of yours of any other kind on such a gear stops Update, named, until that kind is measured (ruled; *Changes
   after S0 and its review*).
2. **How a sleeve with a relief is written.** *Recommended:* two band lengths on the sleeve's row, one part (K10).
   *Alternative:* several rows that one slider moves together, several parts, no relief bore.
3. **The hub warning.** *Recommended:* a warning on every sleeve with no hub row. *Alternative:* only when no hub
   could fit.
4. **Running clearance.** *Recommended:* 0.5 × module a side, at least 0.5 mm, a warning. *Alternative:* a fixed
   figure (the issue suggests 0.5–1 mm), or an error.
5. **W8's fixtures have the issue's defect** (§2.2, §3). *Recommended:* leave them as W8 built them and pin the new
   warnings; RangeBox_Fixed is the corrected example. *Alternative:* correct both (a hub and longer sleeves), which
   reruns W8's demonstration sections on them.
6. **The window on a short screen** (K12, ruled by the coordinating session). *Recommended:* the window stops at the
   screen's work area and its two columns scroll between a fixed header and footer. *Alternatives:* only the Checks
   panel scrolls; the whole window scrolls as the strip's page does (the footer and buttons would scroll away).

**Ruled by the coordinating session after the second review, each for you to overrule:** the savings of §5 (the
sleeve checks merged with the bands and hub; K12 inside W9a's package B; W9d's spike run in W9c's sessions; W9b's
2024 build in W9c's 2024 session; the window check on 2026 only); a face of an app part made new not re-found by its
role, its mate named (K5); Modes rows added or removed by Update (W9c).

---

## 7. What reading could not settle

- Whether a put carries a free user component locked to its gear (S0), and so which route K2 takes; both are written
  to the same rule and test.
- Whether a user feature's or mate's error makes SolidWorks report the rebuild as failed (M3), and whether it opens
  What's Wrong (P0).
- How a component inserted into an assembly with configurations stands in the configurations not active (M5); W9c
  sets and reads every flag rather than relying on either version.
- Whether features can be added to a built part without disturbing the user's features after them (M8).
- Whether a 1920 × 1080 screen at 100 % cuts today's footer (by arithmetic it does; K12 makes it not matter).
- W9d: whether a persistent reference read through a component resolves in a new instance of the same file in
  another assembly, how faithfully each mate kind's definition reads back for a remake, and whether inserting a user
  sub-assembly can raise a dialog (S5, P2); the route from a mate's assembly-context entity to its part-level entity
  for `GetPersistReference3`, which is tier 1's crux; whether a component's state per configuration can be read
  without showing it (if not, §0.3's third exception applies); whether `GetConstrainedStatus` reads Sun free with a
  floating sprocket locked to it (S0, case A).

---

## Changes after the review

Against `ISSUE-1-PLAN-REVIEW.md` (`8ce7426`). Every must-fix and should-fix is taken; none is declined. Where the
plan took a point in a form other than the review's first suggestion, the line says so and why.

- **M1** (W9a still stopped the user's ordinary case). K2 rewritten: the spike S0 (§4), run first in W9a on both
  versions, picks route (a) — the put carries the free component, only a grounded tie refuses, nothing written — or
  route (b) — the user's mates on the put train suppressed around the put and restored with read-back, as `_put_train`
  does for the app's locks. §0.3's first STOP allows (b)'s write, with read-back, as the one exception. W9a's *Done
  when* now requires the sprocket locked to Sun and to RangeSlv to go through a value Update and a slide-offset
  Update. §6 Q1's recommendation reversed. §1.4 traces why every changing press with modes puts the one RangeBox train.
  Narrowing ruling 9.18 listed as not taken, for the review's reason.
- **M2** (app-owned values set back). K11 added: per kind — part, layout and carrier globals, Face Z, slide values
  and recorded mate flags — a user's edit refuses before any change, all named with both values and the cell; a value
  a lost or unsaved Update explains is not the user's; a gear's turn stays W5's. It overturns D10 for a mate the user
  suppressed, said in the table. K4's footer says it before the press.
- **M3** (W9d's replacement dropped the user's features). Replacement taken out of W9d and deferred; bands are added
  to the built sleeve **in place** (§2.4, M8), keeping the file, the user's groove and every mate. `ReplaceComponents2`
  weighed and not taken (new, dialog risk). The in-context references read is kept for W9d's gear removal (M4 of §4).
- **M4** (reachability undefined on W8's fixtures). §2.2 restated by p− and p+, with open intervals and
  `COVER_TOLERANCE`, a carrier's planets counted as its gears, the false general sentence dropped, and the band case
  defined. Answers pinned for RangeBox, RangeBox_Fixed and both W8 fixtures (§2.2, §3): both W8 fixtures warn on
  RangeSlv's reach and on both sleeves' hubs. W9b's STOP now fires on anything other than §3's pins. §6 Q6 asks
  whether to correct the fixtures.
- **M5** (incomplete structural list). The full list from the code is at the end of §2.1 and pointed to from §6 Q2.
  Gear removal (not an anchor) and new couplings and sliding meshes moved into W9d; the renamed component found by
  its part path moved into W9a (K1). The middle option — components brought over unmated — is now K5's recommended
  reading for W9d. A renamed app **mate** stays structural, listed.
- **S1** K4's last sentence says the next press refuses again unless the user has dealt with it.
- **S2** The Build again… clause carries the time it was read, and the build job reads the old assembly first and
  lists what stayed behind in its result.
- **S3** User items' error codes are read before any change and named before the press; M3 extended to the
  assembly's rebuild with a user mate in error.
- **S4** M1's list widened to every mate kind, sub-assembly leaves and mates on only in another mode; 2026's read
  marked new, the `GetSaveFlag` STOP kept.
- **S5** P0 added: a probe ahead for What's Wrong on a failing user feature.
- **S6** Link record schema 7 in W9a, 8 in W9c; sidecar schema 2 for a part with bands; the workbook's Format 1 kept,
  with what an older app does said.
- **S7** Costs redone with 2024 slower than 2026 (515 s against 238 s per changing press that puts every mode): about
  4.5 h on 2026 and 6 h 40 min on 2024, about 32 agent runs (30–35).
- **S8** §0.1 lists every place the W99 rename and the "last phase" sentence touch, and PLAN-WORKBOOK §6's W9 row.
- **S9** Taken in substance: with replacement deferred, no slider's component is deleted in W9d. The point is kept for
  the deferred replacement, which must remake the old component's slide mate (values per configuration, by
  `set_dimension_in`) and its couplings under their recorded names.
- **S10** `_free_to_turn`'s sentence names the user's mates on the gear (W9a package A).
- **S11** §6 Q4 offers the skeleton hub (checked, not built) beside K8; §2.2 says K8 overturns J1's "no hub".

---

## Changes after the user's answers

The user's answers of 2026-11-16, relayed by the coordinating session, and its ruling on the window.

- **Scope.** All stages approved, in order; W9 now has five, W9a–W9e (§0.1, §5). The head of the plan records that
  W8's closing run finished on SolidWorks 2026 34.1.1 with every assembly section at 0 failed (`c351b1f` to
  `fb85bcc`), so W9 starts from a closed W8 once that run's review is in.
- **K11 bound** (an app-owned value the user changed stops Update, named): marked the user's in §0.2 and §6.
- **K5 changed to the user's answer: Build again… carries the components and remakes the mates.** It is a new stage,
  **W9e**, placed last (§2.5): it needs W9a's reads and W9d's insertion and mate-making in a configured assembly, and
  once W9d is in, only §2.1's closing list still reaches Build again…. §2.5 says what is carried (components with
  their frame, fixed or floating state and state per mode; sub-assemblies by file; the standard mate kinds with their
  flags per mode), what is named and why (virtual components, the other mate kinds, pattern instances, the user's
  assembly features, sketches and reference geometry, in-context references), how each entity is found (persistent
  reference on a file both revisions use, name on the layout and the assembly's planes, geometric role on an app part
  made new), and the fallback (a cluster any of whose mates cannot be remade, or whose mates tie a gear, comes over
  fixed where it stood and unmated, every mate named). §4 adds S5 (W9e's spike), P2 (a sub-assembly insert, probed
  ahead for a dialog) and M9 (the full carry). §0.3 allows W9e's writes into the new assembly only. W9d no longer
  brings components over unmated. The cost table gains W9e: about 2 h 15 min on 2026, 3 h 40 min on 2024, 13 agent
  runs; the whole plan about 7 h 15 min and 10 h 50 min, about 47 runs.
- **K8 bound** (the hub built by the app from a row): marked the user's; the skeleton and leave-it options removed
  from §6, which keeps only the hub warning's scope open.
- **K12 added, the coordinating session's ruling** (§2.6, §6 item 6): the Workbook window stops at the screen's
  work area and its two columns scroll between a fixed header and footer, drawn on the board first, with the window
  check asserting the footer whole on this device. The body page, not the Checks panel alone (which cannot promise a
  fit when the right column is the taller) and not the whole window (whose footer and buttons would scroll away).
  Planned into W9a as package C, about 30 min of window check on each version and 2 agent runs.
- **K2 corrected while revising** (not asked of the user, still theirs to overrule): the grounded tie is now what
  SolidWorks reads — a gear not free to turn with the user's mates on — rather than a graph of what the user's mates
  touch. The graph rule of the first revision would have refused the ordinary sprocket concentric to the layout's
  axis and locked to Sun, which leaves Sun free. In a mode not showing, the tie can only be read when that mode is
  shown, so it stops the job there, with what was changed said and unsaved.
- **S0, W9a's first step, written out precisely** in §4: what it builds, its three cases in two modes and two routes,
  what it reads, its time on each version, its output and its STOPs.
- **§6 rewritten:** the answered points listed as binding; still open, at the recommended reading: a user mate on a
  gear Update must move, bands versus several rows, the hub warning's scope, the running clearance, W8's fixtures, and
  the window ruling.

---

## Changes after the second review

Against `ISSUE-1-PLAN-REVIEW-2.md` (`16e45dc`) and the coordinating session's rulings on its cost points. Every
must-fix and should-fix is taken; none is declined.

- **Stages renumbered.** The sleeve checks (old W9b) and the bands and hub (old W9c) are one stage, **W9b**; old W9d is
  **W9c**; old W9e is **W9d**. The body of the plan uses the new letters; the two change lists above keep the old ones.
- **M1** (the user's features in an app part made new). A row of §2.5's table names each such feature, before the
  press and in the result, with why the part is new and that the old file keeps it, and every mate on its faces with
  it; where the part is new only because of K11's case (`MISMATCHED`) or an unsaved Update (`UNSAVED`), the sentence
  says how to have it reused. In M9 and W9d's *Done when*.
- **M2** (the fallback dropped remakeable mates). Every mate whose entities are found is remade, every other named;
  components stay floating where they were placed. A cluster is fixed only when a remade mate comes back in a new
  error, it over-defines, or it ties a gear, and then only its mates to app parts, the layout, the carriers and the
  assembly are deleted; its user-to-user mates are kept. A lock or gear mate maps through the component map (tier 3).
  The example sentence reworded.
- **M3** (W9d acting on the user's documents). The carried items are left **unsaved**, as Update leaves everything; no
  `Save3`. The old assembly is read as it is in the session when open, opened read-only when not (in S5), frames in its
  active mode only, component state per mode by an unshown read if S5 finds one; if not, show-and-restore is §0.3's
  third exception, stated there and to be confirmed. A STOP on any user file's time changing.
- **S1** Components placed by their pose relative to their app component (new · old⁻¹ · old), once, in the first mode,
  from the old assembly's active mode, said.
- **S2** Base planes and origins by tree order, never by English name; carrier parts in tier 2; components mapped by
  gear id, copy *k* to copy *k*.
- **S3** A remade mate with the error it already had is carried as it was and said.
- **S4** The tie is the train's: the user's mates on the train named; "where the app's mates leave it free" comes from
  the record; the showing mode's read decides every mode unless a user mate's flags differ by mode (case C′ added to
  S0); a user mate joining two trains refuses from the inventory.
- **S5** S0 resized to about 40 and 70 min and reordered: P0 first; the sprocket and housing mated by named axes and
  planes through `GetCorresponding`; each setup saved under a new name by `save_as`; the first use of `AddComponent5`
  in a reopened configured assembly said; every mode read after the last put; S0's built master kept for W9a's
  demonstration.
- **S6** K12's five gaps closed in §2.6 (the footer's ceiling and the body's least height; the primary work area by
  `gui._work_area` less the frame; the window check's two new assertions; the scroll bar's width reserved; each wheel
  handler for its own toplevel); the test at `tests/test_workbook_window.py:751-768` and UI-DESIGN's three "grows
  taller" places named for rewriting; the 1657 figure cited as measured.
- **S7** W9d's record is schema 9; W9c adds none.
- **S8** 2024's confirming builds at 1.6-2.2× of 2026; the window check about 15 min, on 2026 only.
- **The coordinating session's rulings** (each for the user to overrule, listed in §6): (1) every saving of the
  review's question 6 taken — W9b merged, K12 in W9a's package B, S5 and P2 in W9c's sessions, W9b's 2024 build in W9c's
  2024 session, the window check on 2026 only; (2) no finding of an entity by geometric role on an app part made new:
  such a mate is named, its component still comes over where it stood; S5 loses its role item; (3) **Modes rows added
  or removed move into W9c's Update**: no call is new (`AddConfiguration2` and `DeleteConfiguration2` are the build's
  own, verified on both versions by W8's configurations probe), only the context (a saved, reopened assembly with the
  user's items), measured as M10 in W9c's full build. A renamed mode stays Build again… (the rename call is unverified,
  and delete-and-add would lose the user's own states in that configuration), and so does a mode removed that leaves a
  coupling on in no mode (ruling 9.1).
- **Costs, one last pass** (§5): about 7 h 30 min on 2026, 12 h 05 min on 2024, about 35 agent runs; the list of what
  still reaches Build again… after W9c stated beside the table.

---

## Changes after S0 and its review

2026-11-16. Against W9a's first measurement, S0 (`W9-S0.md`; runs on SolidWorks 2026 34.1.1 and 2024 32.5.0), its
review (`W9-S0-REVIEW.md`, `2ded80a`) and the coordinating session's rulings on it. The plan's text before this section
is amended only where it named routes (a) and (b) alone or forbade route (c)'s move; S0's brief in §4, §7 and the
change lists above keep what was planned before S0 ran.

- **Route (c1) is K2's route** (review M1). S0 found that routes (a) and (b) both leave a user's component locked to
  a put gear where the drive took it, the lock taking the put's offset with no error code, on both versions. The
  coordinating session ruled a third route, (c), and the user accepted it on 2026-11-16 (HANDOFF-WORKBOOK, *Where W9
  stands*): the app puts every user component rigid to a put gear through the user's locks on in the mode shown,
  chains included, by that gear's own rigid motion in the same step, each read back by `place_component`, the user's
  locks left on (c1). It held in every put of cases A, B and E on both versions. Amended: K2 (the route, and routes
  (a) and (b) moved to *Instead of*); K4 (the footer names the components it will put with their gears, not what it
  will suppress); §0.3's STOP (route (c)'s move named as an exception beside route (b)'s suppression and W9d's
  writes; the show-and-restore exception is now the fourth, and §2.5 and §7 say so); §2.1 item 3 (the put, step by
  step) and item 6 (the footer's sentence); the head of §2.1's table of what the user can do; §5's W9a tests against
  the fake (route (c1), and the fake failing on any other move of a user component); §6 item 1 (what S0 found and
  the user accepted).
- **Route (c1) covers user locks only; every other kind of user mate on a put gear refuses until measured** (review
  M2; the coordinating session's ruling, put to the user as HANDOFF-WORKBOOK's *Questions waiting for the user*, item
  9). S0 measured user components tied to an app gear by user locks on in the mode put, directly or through a chain
  of user locks, and one plane-coincident mate with no lock (case D). K2 now refuses, before any write and naming
  the mate, every other kind of user mate that ties a user's component to a gear Update would put back: a user gear
  mate (a `Transform2` put with a gear mate on re-phases it silently, `findings.MESH_PHASE_ROUTE`, as the lock's
  re-take sank routes (a) and (b)); a concentric, coincident, parallel or angle mate to a gear's own faces or planes;
  and a user lock whose flag differs between the mode being put and another mode (S0 carried a tied component in
  every mode whatever its lock's flag there). Measuring those kinds in W9a's demonstration would lift the refusal for
  each kind that holds, at the cost of SolidWorks time on both versions. Which components are tied comes from
  reading each user lock's entities in the mode shown (M1 of §4), not from a list, as S0's own cases had it.
- **What's Wrong is read for a part's rebuild only** (review M3). P0 rebuilt a part (`ForceRebuild3(False)`) with a
  user feature in error and "show errors every rebuild" on, on both versions: no window. Whether an assembly's
  rebuild with only a user mate or feature in error opens What's Wrong or reports failure stays §4's M3, answered in
  W9a's demonstration. No line of the plan changes; §0.3's STOP on any dialog stands for that rebuild.
- **The tie's read** (review M4 and S7). K2's test was already "not free to turn", the read `_free_to_turn` makes (any
  status but `COMPONENT_UNDER_DEFINED`), never "equal to fully defined", so it stands: SolidWorks itself said the
  assembly was over defined during case C's drive, and a tie whose geometry conflicts could read 4. K2 and §2.1 item 3
  now say that the showing mode's read, when every user mate's flags are the same in every mode, decides whether a tie
  stands in every mode, and that the train it names is the one the mode read joins: in S0's case C, H and L read the
  same tied set, and N, read only after the puts, left RangeSlv out, since it is not coupled there. Nothing in the app
  rests on the per-mode reading of case C2, which is still owed on SolidWorks 2024: a mode whose user flags differ is
  read when shown on every version.
- The review's S1 to S6 touch S0's script, the note, the handoff, PLAN-WORKBOOK and `findings.py`, not this plan.

## Changes after W9a's demonstration on SolidWorks 2026 and its review

2026-11-16. Against the demonstration's run on SolidWorks 2026 34.1.1 (`W9A-DEMONSTRATION.md`; logs
`probe/results/w9a-demo-sw2026-20261116-*.log`) and its review (`W9A-RUN-2026-REVIEW.md`, `6700505`). The text above
this section keeps what was planned before the run.

- **M3 is answered on 2026, and the answer changes the worker** (the coordinating session's ruling, on the review's
  conditions). With only a user's mate in error an assembly's rebuild returns True and the Update goes ahead. With a
  feature in error in a part, the user's own part or the user's feature in an app part, the rebuild returns False; no
  window opens in either case. So an Update whose rebuild returns False is not a failure when something of the
  user's is found in error and nothing of the app's own is (every app mate and every app-made feature read, an
  unread one counting as an error, an app component's error code that comes only from a user's feature in its part
  not counting): it goes ahead and names the user's items, those in error before told apart from those newly in
  error, which is what K3 asks. Gated per version by `findings.py`; where the findings are None (2024 until its
  confirming run) the Update stops as before. A press that would put, by route (c1), a user's component whose own
  part has a feature in error refuses before any write: that put is not measured.
- **M1 is answered in part, and the rest moves to S5 in W9c** (the coordinating session's ruling). Read on 2026 by the
  app's own reads: a user's coincident, distance, angle and lock mates, a gear mate between two of the user's
  components, and a mate suppressed in the active mode. Not read: concentric, width, limit and path mates, a user's
  gear mate on an app gear, and a leaf inside a user's sub-assembly (the app has no verified route to make the first
  four, and inserting a sub-assembly is P2's dialog-risk probe). S5 reads every standard mate kind's definition and
  takes these with it. Until then nothing rests on them: a user mate the app cannot read wholly refuses when anything
  is put, every mate of another kind on a gear Update would put refuses, and a user's sub-assembly locked to a put
  gear refuses as not measured. W9a's "M1–M3 answered" is read with this.
- **Route (c1) on a train with no carrier is measured on 2026** (the 12 : 1, no modes, gear mates left on during the
  put: locks to the driving and the driven gear and a chain, two presses): `USER_MATE_PUT_NO_CARRIER_ON_2026` True.
  The held-gear, fixed-gear and sub-assembly branches stay not measured and refuse.
- **Found on SolidWorks, for W9d:** with the SOLIDWORKS CAM add-in loaded, saving an assembly that has a lightweight
  component raises a modal Yes/No box and the save does not return. W9a's own paths make no such save. W9d, which
  will save an assembly holding the user's components, must resolve or refuse lightweight components before it
  saves.

## Changes after SolidWorks 2024's confirming runs and their review

2026-11-17. Against 2024's confirming set and the two measurements of its What's Wrong box
(`probe/results/sw2024/w9a-confirm-sw2024-20261117-*.log`, `w9a-box-sw2024-20261117-*.log`) and their review
(`W9A-CLOSE-2024-REVIEW.md`, `8e984e2`). This supersedes, for SolidWorks 2024, the sentence in the section above
that says the Update stops there as before.

- **SolidWorks 2024 shows What's Wrong during an Update when something of the user's is in error; the app leaves
  it alone** (the coordinating session's ruling, on the measurements, put to the user as the default they may
  change). With "show errors every rebuild" on, as found, the box came up in every such Update run on 2024 and in
  the steps where the script did what a person does (activating the assembly with a feature in error in a part);
  on 2026 none opens. Watched without being answered: a popup owned by SolidWorks' frame, the frame enabled, a read
  on a second connection answering with it up, the box gone by itself after 3 to 23 s, every job returning with its
  results as they should be. So the app does not suppress it, changes no SolidWorks setting and does not refuse for
  it; it says, before the press and after one that changed something, that the box may show and needs no answer.
  §0.3's STOP on any dialog stands for every other window, and for a What's Wrong that blocks: the gate reads
  `WHATS_WRONG_IN_UPDATE_BLOCKS_ON_<year>`, False on both versions, and a version where it is unmeasured keeps the
  failure.
- **M3 is answered on 2024 as on 2026**, and the worker's rule of the section above holds there: an Update goes
  ahead over the user's mates in error, over a feature in error in the user's own part, and over the user's
  feature in an app part rebuilt into error, naming them; a carried component in error refuses before any write.
- **Not measured on 2024, and so not relied on:** a person pressing FeatureXpert or the box's own checkbox while an
  Update runs; a box that outlives its job (never seen); a Build with the user's work in error; the mate case on a
  gearbox without modes; other kinds of mate error; a box longer than 23 s; "show errors every rebuild" off. The
  alternative ruling, the app turning that setting off for its job and setting it back, was not measured either and
  would need the user's word, since a session that ends mid-job would leave their setting changed.
- **Route (c1) on a train with no carrier is measured on 2024 too** (`USER_MATE_PUT_NO_CARRIER_ON_2024` True, the
  12 : 1 without modes).


## Changes after W9b, W9c's probes and the review of W9c's packages

Ruled by the coordinating session on 2026-11-17, each the user's to overrule. The detail is in
`W9B-INTERFACES.md` §7, `W9C-INTERFACES.md` §10 and §11, `W9C-PROBES-REVIEW.md` and `W9C-REVIEW.md`.

- **The record's schema.** §2.4 has W9c adding nothing to the record's shape and W9d's carried items making it
  schema 9. W9c's record now keeps what a stopped press left in SolidWorks (`GearboxRecord.left`: the app's globals
  and configurations, and a part built but not inserted), which decides whether a thing found there is the app's or
  the user's, and an older reader would drop it silently. So **W9c's link record is schema 9 and W9d's will be 10**.
- **Each new kind of write by Update is behind a per-version finding**, None until a full build on that SolidWorks
  reads it clean, and refuses before any write, by name, while None: a gear inserted with its mates; a gear mate
  made again on a gearbox with modes; bands given to a built sleeve; a mode added; a mode removed. Two more stay
  None after W9c's demonstration, because no legal edit of its gearboxes reaches them: **a coupling or sliding mesh
  newly made between gears already in the assembly**, and **bands taken away from, or given back to, a built
  sleeve** (the relief suppressed). They are measured when a gearbox that needs them is built, on the user's word.
- **M4 is not measured, and a removal refuses while any component of the user's is in the assembly.** Five reads of
  a part's external references answer and mark nothing on SolidWorks 2026, but no part with an in-context
  reference to an app gear could be made by proven calls, so none is shown to find one. Removal where the user has
  nothing in the assembly is measured (P1's route).
- **W9b's rulings**: a one-band sleeve is not built; a hub keys one sleeve; a banded and a plain sleeve of one size
  share a default file name and need a Part name on one; no thin-wall warning over the relief.
- **A part built by a press that then stopped is recorded and used by the next press**; the app never adopts a file
  on disk that no record holds.
- **Owed before W9d is designed** (§2.5), from S5: a face's persistent reference (only reference axes and planes
  were measured); **no route reads a component's state per configuration without marking the assembly**, and the
  fallback this plan names (show the old assembly's modes and restore) cannot leave its save flag as it was, since
  showing a configuration marks the assembly on both versions; whether opening a healthy user sub-assembly marks
  it. The mate kinds remade from their definitions are coincident, lock, distance and angle on axes, planes and
  whole components; concentric, limit, width, gear, faces and edges, flipped mates and a sub-assembly's leaf are
  not.
