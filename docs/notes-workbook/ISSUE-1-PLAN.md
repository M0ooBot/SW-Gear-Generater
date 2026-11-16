# W9 (issue #1: the user's work in a built assembly, and dog-clutch sleeves): the plan

**Authority and reading order.** `docs/PLAN-WORKBOOK.md` stays the authority. This plan says where W9 departs from it
and from W8's readings and rulings (`W8-PLAN.md` §0.3, `W8-INTERFACES.md` §9), each named in §0.2. Its review is
`ISSUE-1-PLAN-REVIEW.md` (`8ce7426`); *Changes after the review* at the end lists every change against the review's
points, and where the two differ the revised text below wins. The user answered the plan's choices on 2026-11-16
(*Changes after the user's answers*, at the end): **all five stages approved, in order W9a–W9e**; an app-owned value
the user changed stops Update, named (K11); **Build again… carries the user's components and remakes their mates**
(K5, a stage of its own, W9e); the hub is built by the app from a row (K8). Those now bind. GitHub issue #1 (`MoZ200701/SW-Gear-Generater`) is the
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

**W9**, in five stages W9a–W9e. It is the next row of PLAN-WORKBOOK §6 because it changes the same import, record
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
the user's answers and bind; **(ruled)** is the coordinating session's ruling; every other row is the plan's reading,
still for the user to overrule.

| # | Reading | Instead of | Overturns |
|---|---|---|---|
| K1 | **What is the app's own** is what the record lists: the gear, carrier and layout components (by `Name2`), the mates (by name), the configurations named as modes, and in each app part the globals and features its plan made. Everything else is the user's. A recorded component not found by its `Name2` is found by its part path when exactly one unclaimed instance of that part is in the assembly, and its new name recorded. | Guessing ownership from names; a renamed component sending the user to Build again…. | — |
| K2 | **A mate of the user's on a gear Update must move does not stop Update.** W9a's spike (§4, S0) decides between two routes, both shipped behind one rule: **(a)** the put carries a free user component with its gear, so nothing of the user's is written; or **(b)** it does not, so the user's mates on the train being put are suppressed in the configuration being put, around the put, as `_put_train` does for the app's locks, turned back on whatever happens, every flag read back, and any in error named. Under both, only a **grounded tie** refuses: a gear SolidWorks reads not free to turn (`constrained_status`, already read by the post-check) with the user's mates on, where the app's own mates leave it free — read in the mode showing before any change, and in each other mode when it is shown, before its put. SolidWorks' solver decides it, not a graph of mates: a sprocket concentric to the layout's axis and locked to Sun leaves Sun free and is not a tie. | Refusing every user mate on a moved gear (the plan before the review); today's refusal of every user mate; a topological graph check (wrong for a concentric mate to a fixed axis). | W5 review M7, W8 J12's last sentence |
| K3 | **The user's features in an app part are kept.** Update changes only the app's globals; SolidWorks rebuilds the user's features after them; the job reads each user feature's error state afterwards and names any in error, as theirs. Nothing is saved (as today). | Refusing to change a part with user features. | — |
| K4 | **Told before anything is written.** Every job reads the user's work in the documents it opens and the finish records it, with the time read. The footer says before the press what Update will change, what of the user's it will suppress around a put (route b), and what it leaves. Something the record did not hold that would refuse makes the press refuse before any change and is recorded, so the footer then says it; the next press refuses again unless the user has dealt with it. No new control. | A check-only job and a question before each Update. | — |
| K5 | **(the user's, 2026-11-16) Build again… carries the user's components and remakes their mates (W9e, §2.5).** Every top-level user component comes over at its frame, fixed or floating as it was, with its state in each mode; each mate of the user's is remade on the corresponding entities in the new revision, found by persistent reference on an unchanged file, by name on the layout and the assembly's planes, and by geometric role on an app part made new; a mate whose entity cannot be found, or that SolidWorks refuses, is named, and the user components joined through it come over fixed where they stood, unmated. Until W9e, Build again… says what stays behind, as read at a stated time, and the build job reads the old assembly first and lists it in its result. | Saying only; bringing components over fixed and unmated (the plan's recommendation before the user's answer). | — |
| K6 | **Update adds, removes and re-mates (W9d):** a new gear on an existing frame shaft along Z±, inserted and mated as the build mates it; a gear removed (not one that anchors other gears) with its app mates; a coupling or sliding mesh newly needed between components on record; a gear mate of a gearbox with modes made again (a tooth change); each new or remade mate's and component's flag set and read back in every configuration. Bands are added to a built sleeve **in place** (§2.4). Replacing a part's file stays Build again… (deferred). | Every such edit structural; replacing the sleeve's component. | W8 J14 (in part), ruling 9.16 |
| K7 | **Reachability is a warning**, by the points the sleeve's shaft must reach (§2.2). | An error; the issue's narrower rule. | — |
| K8 | **(the user's, 2026-11-16) The hub is a workbook row**, kind `hub`, on the sleeve's own shaft, built by the app as a toothed ring like a dog with the row's Bore; the app never adds one by itself. A sleeve with no hub row is warned of. | A hub row checked but not built (a skeleton, as the carrier); the app adding one; leaving it to the user unchecked. | W8 J1 ("no hub") |
| K9 | **Minimum running clearance 0.5 × module a side, at least 0.5 mm**, a warning per mode. | A fixed mm figure; an error. | W8 J22 (extended) |
| K10 | **A sleeve declares two toothed bands** (two numeric columns, one at each end of its face); the span between is a relief bore of diameter m(z + 3), clearing a dog's tip by 0.5 m a side. One part. Engagement counts only toothed length. | One slider moving several rows. | W8 J4 (refined) |
| K11 | **(the user's, 2026-11-16) The user's edit to an app-owned value is never set back without their word.** A part's, the layout's or a carrier's global, a Face Z equation, a slide value in a configuration, or a recorded mate's flag in a configuration, found live different both from what the record says the file holds and from what the workbook now asks, and not explained by a lost or unsaved Update (the record's `unsaved` and `mismatched` marks), refuses the Update before any change, every such value named at once with both values and the cell to change. A gear's turn stays W5's (put back when Update must move a gear), since turning is motion, not an edit. | Setting it back (today); keeping the user's value and saying so. | W5's D10 for a mate the user suppressed |
| K12 | **(ruled) The Workbook window fits its screen (W9a, §2.6).** It never grows past the screen's work area; between a fixed header and a fixed footer, the two columns scroll as one page when the window is shorter than they ask; the footer and its buttons are always whole. Drawn on the board first; the window check asserts the footer whole on a 2560 × 1600 screen at 150 %. | Growing without a cap (today, `workbook_gui.py:1160-1170`); scrolling the Checks panel alone; the whole window scrolling as the strip's page does. | UI-DESIGN §9 "grows taller … moves left or up" |

### 0.3 STOP and ask (implementers)

- **Anything that would write to, delete, move or rename a component, mate, feature, global or configuration that is
  not on record**, with two exceptions: route (b)'s suppression of the user's mates around a put, each turned back on
  and read back in every configuration it was on in; and W9e's writes into the **new** revision's assembly (the
  user's components inserted, their mates remade there), never into the old assembly or a user file. The fake fails
  a test on any other such call, and on SolidWorks each demonstration compares every user item's flag, error code and
  entities before and after, in the old assembly as well after a Build again….
- W9e: a persistent reference that resolves to an entity of another kind or another place than the one it was read
  from (a face where an edge was, a face off the role's position); a remade mate SolidWorks accepts with an error code
  but the app counts as remade.
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

### 2.1 Problem 4: keep the user's work, keep the app usable (W9a, then W9d)

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
   `swbuild.py:4213-4215`, `:4346`) goes through by the route the spike chose: (a) nothing written, or (b)
   suppressed in each configuration around the put there and turned back on, read back, as `_put_train` does with
   the app's own locks (`set_mate_suppressed_in`, `mate_suppression`, proven per configuration). Under both, the
   **grounded tie** — a gear SolidWorks reads not free to turn with the user's mates on (K2) — refuses, naming every
   user mate on that gear at once with its modes: *"Update SolidWorks must turn Sun back to its built place, and with
   your mate Lock3 on SolidWorks reads Sun as unable to turn (Lock3 ties it to Housing-1), so nothing is changed;
   suppress Lock3 in H, N and L and press Update SolidWorks again."* In the mode showing it is read before any change;
   in another mode it can be read only when that mode is shown (J25), so there it stops the job before that mode's put,
   with what was already changed said and left unsaved, as any failure after the check phase is (W4 review B1). The
   post-check's *"cannot turn"* sentence (`_free_to_turn`) names the user's mates on the gear.
4. *Values (K11).* The check phase already reads every global, slide value and recorded flag live; a user's edit
   refuses before any change, all named: *"Bore Diameter in Gear_m1.25_N17 is 12 in SolidWorks and 10 in the
   workbook: type 12 in Gears!J5, or set it back in SolidWorks, and press Update SolidWorks again."*
5. *Features (K3).* After the rebuild each user feature's error state is read and any in error named as theirs
   (*"SolidWorks rebuilt your Keyway in Gear_m1.25_N17 after the new teeth, and it is in error."*). A rebuild error
   that comes only from the user's features does not stop the job, if M3 shows the rebuild reports it.
6. *Told before (K4).* The finish of every job, a refused one included, records what it read of the user's work (link
   record schema 7, §2.4: per part path the user's features, and the user's components and mates with what each
   touches, fixed or not, with the time read). The footer's Update line then says, before the press, what Update
   would change, what of the user's it would suppress around a put (route b) and what it leaves (*"Update SolidWorks
   changes RangeSlv's part, where your Keyway follows the app's features; it leaves Sprocket-1, Chain-1 and 6 mates of
   yours as they are, and suppresses your Lock3 on Sun while it turns Sun back, then turns it on again."*). The
   worker reads again; what the record did not hold and would refuse refuses before any change and is recorded, so
   the footer says it; the next press refuses again unless the user has dealt with it.
7. *The window fits its screen (K12, §2.6),* since items 4 and 6 add words to the footer.
8. *Build again… until W9e (K5).* The question gains, from the record and with its time: *"As read at 14:02, your
   Sprocket-1, Chain-1 and 6 mates stay in RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N17, which RangeSlv's
   new part replaces; RangeBox_r2 has none of them."* The build job opens the old assembly first, reads its user items
   (a read), and its result lists what stayed behind as found.

*What the user can do after W9a* (RangeBox with modes, a bore feature in a gear part; route (a) or (b) taken):

| Press | Sprocket mated only to the layout or to the user's own shaft | Sprocket mated to Sun or RangeSlv, nothing of it grounded |
|---|---|---|
| A slide offset, a face, a dog-and-sleeve tooth change | Works; the bore feature kept, named if in error | Works; the sprocket found on its gear after |
| A tooth change of Sun, Planet or Ring | Build again… (9.16) until W9d | Build again… until W9d |
| Add the hub | Build again… until W9d | Build again… until W9d |
| An app value the user edited in SolidWorks | Refused, named, until the workbook or SolidWorks agrees | Same |
| A quiet press | Works | Works |

**W9d — Update adds, removes and re-mates (K6).** A new gear on an existing frame shaft along Z± is built as a part
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
place (§2.4). Inserting a component into a configured assembly and setting its state per mode (M5) is also what W9e
needs for the user's components.

**Still Build again… after W9d** (from `workbook/update.py:404-453`, `_turning`, `_modes` `:1292-1368`; each said
in the question): a gear that anchors other gears removed; a shaft added or removed; Modes rows added, removed or
renamed; a gear starting or stopping to slide; a mated gear moved to another shaft; a Z± flip; a shaft starting or
ceasing to stand still; a shaft coordinate reaching, leaving or crossing its base plane (every RangeBox shaft is at
X = Y = 0, so moving one off the axis is structural); an anchor's face or a slide value reaching the Front plane; the
number of planet copies; a shared part splitting; a part whose file must change (Flank, Part name, a bevel's form); a
renamed app mate (`MateGone`). These are the edits that still reach Build again… once W9d lets Update add, remove and
re-mate in place, and the only ones W9e's carrying serves; that is why W9e can come last.

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
change on a banded sleeve is a value Update. *In place (W9d):* bands given to a sleeve built without them are added to
its part file — the band globals and the relief features, the same ops the build makes, run on the opened part — so
RangeSlv keeps its file, the user's groove and every mate; bands taken away suppress the app's relief features. This
is new (features added to an existing part) and is measured in W9d's full build (M8).

*The record.* W9a's link record is **schema 7** (the user-work inventory, K1's found names); W9c's is **schema 8**
(the bands in a sleeve's spec), so a W9a-era app refuses a W9c record as `store.py` refuses any newer one and leaves it
as it is. A part with bands writes its `.gear.json` at sidecar **schema 2** (`store.py:30` is 1 today), since
`GearSpec.from_dict` drops unknown keys (`spec.py:158-160`) and an older app would otherwise reuse a banded sleeve as an
unbanded one; a part without bands stays at 1.

*Not taken:* one slider moving several rows. It gets engagement right with no new geometry but builds the loose parts
the issue complains of, needs a rigid mate between them, and has no relief bore.

### 2.5 Build again… carries the user's work (K5, W9e)

The user answered (2026-11-16) that a new revision must carry their components **and** remake their mates, naming a
mate that cannot be remade. It is a stage of its own, **W9e, the last**: it needs W9a's reads (a mate's entities and
components, the inventory), W9d's insertion and mate-making in a configured assembly with every flag read back (M5,
M6), and a selection problem neither has met, re-finding an entity on a part that may be a new file. And once W9d lets
Update add, remove and re-mate in place, only the edits listed at the end of §2.1 still reach Build again….

**When it runs.** In the Build again… job, after the new revision's assembly is built, checked and saved exactly as
today, so the app's own result never rests on the carried items. The job then opens the old assembly (it never writes
or saves it), reads the user's items, inserts and mates them in the new assembly, checks, and saves the new assembly
again. If carrying stops part way, what was carried is said, the new assembly stays as the app built it plus what was
carried and checked, and the old assembly is untouched.

**What is carried.**

| Item | Carried | Not carried, and named |
|---|---|---|
| A top-level user component (a part or a sub-assembly by its file) | Its file and referenced configuration, its frame, fixed or floating, and its suppressed or resolved state in each mode (by mode name; a mode new in this revision takes the first mode's state) | A virtual component (it has no file to insert; saving it out would write a file of the user's); a flexible sub-assembly's flexibility (carried rigid, said); display states and appearances set in the assembly |
| A mate among the user's components, or between one and an app gear, the layout, or the assembly's planes | Coincident, concentric, parallel, perpendicular, tangent, distance, angle (with their limits), lock and gear mates, with alignment, flip, values and their flag in each mode | Width, path, slot, symmetric, profile-centre, cam, hinge, rack-and-pinion, screw, universal-joint and belt/chain: named as kinds this version does not remake |
| A user component pattern or mirror | Its seed component | Its instances (a pattern is an assembly feature the app does not make) |
| The user's assembly features, sketches and reference geometry | — | All; a mate on them is not remade |
| A user part's in-context reference to an old app component | — | Said: the user's file still refers to the old assembly |

**How each mate's entities are found in the new assembly**, by where the entity was:

1. *On a file both revisions use* (every user component; an app part reused unchanged): its persistent reference,
   read in the part through the component (`GetPersistReference3` on the part-level entity), resolved in the new
   instance (`GetObjectByPersistReference3`, then the component's corresponding entity). Same file, same reference.
2. *On the layout part* (always a new file, `<Name>_r<n>_Layout`) *or the assembly's own planes*: by name. The app
   names every layout plane and axis (`"Output Axis"`), and the assembly's Front, Top and Right planes and Origin
   have theirs. A shaft gone means not found.
3. *On an app part made new* (a different file, whose persistent references are not expected to resolve — measured
   in S5): by role, from the plan. The part's named planes, axis and origin by name; a face by role only when exactly
   one face of the new part has it: the bore (a cylinder on the gear's axis at the Bore's radius), the two end faces
   (planes square to the axis at the face's two ends), and the circles where those meet. Anything else — a tooth
   flank or edge, a fillet, a face of a user feature in a part made new — is not found.

**Clusters, and the fallback.** The user's components joined through their own mates form clusters, with app
components, the layout and the assembly outside them. A cluster is carried whole when every mate touching it is
remade with no error code and SolidWorks still reads every app gear free to turn in every mode (the build's own
post-check, now with the carried mates on). Otherwise every mate the job made for that cluster is deleted again (its
own, just made, in the new assembly, by `MATE_DELETE_ROUTE`) and the cluster's components stay where they stood in
the old assembly, **fixed, unmated**, each of its mates named with why: *"Sprocket-1 is in RangeBox_r2 where it stood,
fixed and unmated: your Concentric5 was on a tooth face of Sun, whose part was made new, and that face cannot be found
in it; Lock3 and Coincident7 were therefore not made either."* Half a cluster mated and fixed would over-define or tie
a gear; half mated and floating would drift.

**The record.** The carried items stay the user's: they go into the new revision's inventory (schema 7), with which
mates were remade.

### 2.6 The window on a short screen (K12, W9a, ruled)

*Today.* `WorkbookWindow._fit` (`workbook_gui.py:1160-1170`) asks for `max(winfo_reqheight, current)` with no cap,
and keeps the window on screen against `winfo_screenheight()`, the whole screen, by moving it up. On this device
(2560 × 1600 at 150 %) Windows holds the window to 1570 px inside, and the built E4 window wants about 1690: the
footer's last lines are cut (`W8-REVIEW-SW2024-CONFIRM.md` question 3; the closing run's window check, `fb85bcc`). By
the same arithmetic a 1920 × 1080 screen at 100 % would cut it too (that review's S6; inference, not measured). W9a
adds words to the footer and to what the window says before a press, so it cannot be shown on this device until the
window fits.

*The change.* The window never grows past the screen's work area (on Windows the work area of the window's monitor,
`SystemParametersInfoW(SPI_GETWORKAREA)` through `ctypes`; elsewhere the screen less a margin), and is placed inside
it. The header and the footer, with its buttons, stay fixed and whole; between them **the two columns scroll as one
page** when the window is shorter than they ask, a scroll bar shown only then, the mouse wheel scrolling it.

*Why the body and not the Checks panel, and not the whole window.* The strip's rule — "when the screen is shorter
than the strip, the whole page scrolls" (UI-DESIGN §1) — would, applied to the whole Workbook window, scroll the
footer and its buttons out of sight, the one part that must stay whole. Scrolling the Checks panel alone cannot
promise a fit: the right column (the end view and Speeds, eleven lines and the chooser on E4) can be the taller one,
and Checks may hold few lines. The body page is the strip's rule kept, with the footer pinned.

*Done when:* the board is drawn first (a new board of the built E4 at 1570 px, the body scrolled, the footer whole),
UI-DESIGN §9's layout paragraph rewritten, a Tk test with a forced work area asserting the footer's bottom inside the
window and the body scrollable, and the window check's W8 stage passing `w8_footer_whole` on this device.

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

**RangeBox_Fixed (after W9c):** RangeSlv face 26 at −35, Start band 5, End band 5 (relief 16, Ø 25.0), Slides
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
| P0 | A rebuild that fails on a user feature, with SolidWorks' "show errors every rebuild" on: does What's Wrong open | **Probe ahead** (a dialog), a scratch part with a feature made to fail, in S0's session, about 5 min per version |
| M1 | Reading a user mate's entities' components on coincident, concentric, distance, angle, width, limit, path, lock and gear mates, user–user, user–layout, user–gear; a mate to a component inside a user sub-assembly (`ReferenceComponent` gives the leaf, its `Name2` a path); a mate suppressed in the active configuration but on in another mode; and that none of it marks a document modified (new on 2026) | W9a full build |
| M2 | The feature walk telling the plan's features from the user's; each user feature's error code after a rebuild | W9a full build |
| M3 | Whether a part's rebuild, and the assembly's rebuild, report failure when only a user feature or a user mate is in error | W9a full build, one section |
| P1 | Deleting a component from an assembly with configurations (`Select2` then `EditDelete`, or `DeleteSelection2`): any "delete mates too?" confirmation | **Probe ahead** (a dialog), scratch assembly, 2026 then 2024, before W9d's packages |
| M4 | An external-references read on the user's parts (in-context references to an app component) | W9d full build |
| M5 | `AddComponent5` into a reopened assembly with mode configurations: its state in each configuration, set and read back | W9d full build |
| M6 | Mates made in that assembly (axis, along, spline, coupling) and a gear mate remade there: flags set and read back in every configuration | W9d full build |
| M7 | The banded sleeve's part (the relief op route) on both versions | W9c's build of `RangeBox_Fixed` from scratch |
| M8 | Band globals and relief features added to a built sleeve part in place, the user's groove in it kept | W9d full build |
| S5 | **W9e's spike:** each standard mate kind's definition read (type, alignment, flip, values, limits; the macro database's *assemblies/06, read every mate* is the start) and remade by `AddMate5`; a mate entity's persistent reference read through its component (`GetPersistReference3`) and resolved in a new instance of the same file in another assembly, then selected for a mate through the component's corresponding entity; the same reference tried on a part rebuilt as a new file by the same plan (expected not to resolve); a bore and an end face found by role on that new file; a mate to a layout axis and to the assembly's Front plane re-selected by name; every read checked for `GetSaveFlag` | **W9e's first step**, scratch assemblies, 2026 then 2024, about 45 min and 70 min |
| P2 | Inserting a user **sub-assembly** by its file into the new assembly (it must be opened first, `API-LEDGER.md:531`), one with a missing reference among its own files: a "find file" dialog | **Probe ahead** (a dialog), in S5's session |
| M9 | Carrying on a whole Build again…: two clusters (a sprocket and its "chain" on Sun, a housing mated to the layout), one mate on a tooth face, the new revision made by an edit that still needs Build again… (Sun's Flank changed, so its part is a new file; a Modes row added) | W9e full build |

**S0, W9a's first step, precisely.** On SolidWorks 2026 (34.1.1) in a session the agent starts, then on 2024
(32.5.0) in a fresh session (a 2026 file does not open in 2024, so each version builds its own). *Builds:* the
issue's RangeBox (§3) through the app's own Build into a fresh output folder named in the run, then copies the built
folder (J24's scheme). Into the copy the script adds, through the API and saved only in the copy: a "sprocket" (a
strip-built spur, 20 teeth, module 1.25, face 6, Bore 10) on the Input axis in front of Sun and one on the Output
axis behind RangeSlv's travel, and a "housing" (any app-built part standing in, inserted fixed). *Cases*, each from a
fresh copy, each read in H and in L (shown in turn): **A** sprocket concentric to the layout's `Input Axis` and locked
to Sun; **B** the second sprocket concentric to `Output Axis` and locked to RangeSlv; **C** as A plus a coincident from
the sprocket's face to the fixed housing (the grounded tie). In each case the train is first turned +37° by the
drive W8's s7 used, then put back to its built frames by the put W8's s7 made the app's way (`s7_put_job` in
`probe/workbook_assembly_check.py`: the app's locks off in that configuration, `place_component` per gear, locks on) —
today's Update cannot be used, since it refuses the user's mate — first with the user's mate on (route a), then on a
fresh copy with it suppressed in that configuration around the put and turned back on (route b). *Reads*, before and
after each put: each gear's and each sprocket's frame (`component_frame`), whether the sprocket turned with its gear by
the same angle, each put gear against its target to 1e-6, every mate's error code and flag in every mode (app's and
user's), each gear's and sprocket's `constrained_status`, `GetSaveFlag` of every document before and after every
read, and for C whether Sun reads not free before any put. P0 runs in the same session. *Time:* about 20 min on 2026
and 35 min on 2024. *Output:* a log and JSON under `probe/results/` (2024's under `sw2024/`), proposed findings
(`USER_MATE_PUT_ROUTE` "carried" or "suppress around", `USER_TIE_READ` the constrained-status reading for C, the
What's Wrong reading), reviewed before W9a's packages start. *STOP:* any dialog; a document marked modified by a
read; a put that holds in neither route.

Each demonstration works on a copy of one built folder (J24's scheme) into which the script puts the user's work: a
part of its own (a block "housing", a strip-built "sprocket"), mates among them, to the layout and to gears, a keyway
in a gear part and a groove in the sleeve part.

---

## 5. Stages, in order

The user is watching usage: the leanest sound order is below, each stage closing before the next is planned in
detail. All five are approved (the user, 2026-11-16), in order W9a–W9e. **W9a gives the app back soonest**; W9b is
pure and can run beside it; W9e comes last because W9d first shrinks what reaches Build again… to §2.1's list.

**W9a — the user's work is theirs.**
- *First:* S0 and P0 on 2026 and 2024; their result picks K2's route and is reviewed before the packages.
- *Packages:* A (worker: the reads, K2 by the chosen route with the grounded-tie refusal, K11's refusals, errors read
  before and after, all names at once, `_free_to_turn` naming user mates, the component found by part path); B
  (planning, link record schema 7, the inventory in the finish, the Build again… clause and the build job's read of
  the old assembly, the footer line, UI-DESIGN §9 and the boards' footers redrawn; the W99 rename and the "last phase"
  edits of §0.1); C (K12, §2.6: the board first, then `_fit` capped at the work area and the body page, its Tk test).
- *Tests against the fake:* user–user and user–layout mates never refuse; a user lock on a put gear goes through by the
  chosen route (route b: every one back on in every configuration it was on in, whatever raised, as the test for M8's
  locks); a grounded tie refuses before any write, every one named; no call targets an item not on record but route
  (b)'s; a user's edit to each kind of K11 value refuses, named, and one a lost Update explains does not; user features
  survive a value Update and one in error is named; the inventory reaches the footer before the press; the Build
  again… question names what stays behind with its time.
- *Done when:* the suite is green; on SolidWorks 2026, on a copy of RangeBox with the user's components, their mates
  among themselves and to the layout, a keyway in a gear part, and **a user lock from a free sprocket to Sun and to
  RangeSlv**, a value Update and a slide-offset Update go ahead, the sprocket is found on its gear afterwards, every
  user mate is on in the modes it was on in and in no error, and the keyway rebuilt; a lock to a fixed housing refuses
  naming it; a Bore Diameter typed in SolidWorks refuses naming the cell; M1–M3 answered; the window check's W8 stage
  and W9a's window states pass on this device with the footer whole (K12); 2024 confirms; reviewed.
- *Cost:* the spike about 20 min on 2026 and 35 min on 2024; the demonstration about 1.5 h on 2026 and the
  confirming build about 2 h on 2024 (it puts every mode on each changing press: 238 s on 2026, 515 s on 2024 in W8);
  the window check about 30 min on each; about 13 agent runs.

**W9b — sleeve checks (problems 1 and 2).** Pure, Linux-tested, no SolidWorks.
- *Package:* one (`modes.py`, `checks.py`, sentences; W8 fixtures' warning pins moved by three each, §3).
- *Tests:* §3's answers for RangeBox, RangeBox_Fixed's checks and both W8 fixtures; the open intervals and tolerance;
  a nested input through a hollow carrier not warned; clearance at exactly c clean, below it warned.
- *Done when:* green and reviewed. *STOP:* any warning on a fixture other than §3's.
- *Cost:* no SolidWorks; about 3 agent runs.

**W9c — bands and the hub kind (problem 3, problem 1's hub).**
- *Package:* one for schema, model, engagement per band, the `hub` kind and its rules, the relief op, record schema 8
  and sidecar schema 2; the board for the Gears sheet's two columns (no window control changes).
- *Tests:* RangeBox_Fixed's table; old workbooks and schema 6 and 7 records read as before; the banded plan equals the
  internal ring's plus the relief; an older reader refuses schema 8.
- *Done when:* green; `RangeBox_Fixed` built from scratch on 2026 (M7) with every mode's engagement, slides and
  interference as §3, confirmed on 2024; reviewed.
- *STOP:* the relief op failing on either version; a mode reading other than §3.
- *Cost:* about 30 min on 2026 and 50 min on 2024; about 5 agent runs.

**W9d — Update adds, removes and re-mates (problem 4's "cannot add a part").**
- *First:* P1 on 2026 and 2024.
- *Packages:* A (worker: insert, mate, per-configuration flags, delete with app mates, remake with modes, bands in
  place); B (classify: what moves from structural to Update, the remaining list
  said in the question; the sentences; UI-DESIGN §9).
- *Tests:* adding a gear on an existing shaft and a hub that becomes an anchor; removing a non-anchor gear, refused
  when a user mate or in-context reference touches it; bands added in place keeping a user feature; a new coupling
  made with its per-mode flags; a tooth change on a gearbox with modes remade and read back.
- *Done when:* on a copy of the built RangeBox with the user's work (W9a's), the workbook edited to `RangeBox_Fixed`
  and one Update adds Hub, gives RangeSlv its bands in place and leaves every user item as it was, the groove in
  RangeSlv kept, each mode then engaging and turning as §3; confirmed on 2024; reviewed.
- *STOP:* §0.3; P1 showing a dialog (then removal stays Build again…, put to the user).
- *Cost:* P1 about 10 min on 2026 and 15 min on 2024; the demonstration about 2 h on 2026 and 3 h on 2024; about 13
  agent runs.

**W9e — Build again… carries the user's work (K5, §2.5; the user's answer).**
- *First:* S5 and P2 on 2026 and 2024, reviewed before the packages.
- *Packages:* A (worker: the old assembly read, the user's components inserted with their state per mode, each mate's
  definition read and remade on entities found by reference, name or role, clusters judged whole or brought over
  fixed and unmated, the post-check with the carried mates on); B (planning: what the question says will be carried
  and what not, from the record's inventory with its time; the result's sentences; UI-DESIGN §9).
- *Tests against the fake:* each row of §2.5's table, carried or named; a cluster with one mate not found comes over
  fixed and unmated, every mate named; a carried mate that ties a gear un-mates its cluster; nothing is written to
  the old assembly or a user file; a mode new in the revision takes the first mode's flags.
- *Done when:* M9 on 2026: after Sun's Flank change and a Modes row added, Build again… makes RangeBox_r2 with both
  clusters carried, their mates remade and on in the modes they were, every app gear free to turn in every mode, the
  tooth-face mate's cluster fixed and named, the old assembly unchanged; confirmed on 2024; reviewed.
- *STOP:* §0.3; a dialog in S5 or P2 (then sub-assemblies come over fixed and unmated, put to the user).
- *Cost:* the spike about 45 min on 2026 and 70 min on 2024; the demonstration about 1.5 h on 2026 and 2.5 h on
  2024; about 13 agent runs.

| Stage | SolidWorks 2026 | SolidWorks 2024 | Agent runs |
|---|---|---|---|
| W9a | ~2 h 20 min (spike, demonstration, window check) | ~3 h 05 min (spike, confirming build, window check) | ~13 |
| W9b | — | — | ~3 |
| W9c | ~30 min | ~50 min | ~5 |
| W9d | ~2 h 10 min (probe, demonstration) | ~3 h 15 min (probe, confirming build) | ~13 |
| W9e | ~2 h 15 min (spike, demonstration) | ~3 h 40 min (spike, confirming build) | ~13 |
| **All** | **~7 h 15 min** | **~10 h 50 min** | **~47 (42–52)** |

Carrying the mates (W9e) adds about 2 h 15 min on 2026, 3 h 40 min on 2024 and 13 agent runs to the plan as it
stood; the window's fit (K12) adds about 30 min on each version and 2 runs to W9a. W8 took 16 review notes beyond its
plan; the run counts allow for one fix round per stage, not more. **Deferrable** (each its own follow-up, on the
user's word): replacing a part's file by Update; Update adding or removing a shaft or Modes rows, or removing an
anchor gear; carrying the mate kinds §2.5 names, component patterns, and the user's assembly features.

---

## 6. For the user

**Answered (2026-11-16), and binding:** all five stages, in order W9a–W9e; an app-owned value you changed in
SolidWorks stops Update, named (K11); Build again… carries your components and remakes your mates, naming any it
cannot (K5, W9e); the hub is built by the app from a row you write (K8).

**Still open, each going on at the recommended reading unless you overrule it:**

1. **A mate of yours on a gear Update must move.** *Recommended:* Update goes ahead — either nothing of yours is
   touched because the put carries your component with the gear, or your mate is switched off around the put and
   back on after, read back and said — chosen by a measurement at the start of W9a; it stops, naming the mate, only
   when SolidWorks reads the gear unable to turn with your mate on. *Alternative:* it always stops and names your mate
   (you suppress and unsuppress it by hand).
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

---

## 7. What reading could not settle

- Whether a put carries a free user component locked to its gear (S0), and so which route K2 takes; both are written
  to the same rule and test.
- Whether a user feature's or mate's error makes SolidWorks report the rebuild as failed (M3), and whether it opens
  What's Wrong (P0).
- How a component inserted into an assembly with configurations stands in the configurations not active (M5); W9d
  sets and reads every flag rather than relying on either version.
- Whether features can be added to a built part without disturbing the user's features after them (M8).
- Whether a 1920 × 1080 screen at 100 % cuts today's footer (by arithmetic it does; K12 makes it not matter).
- W9e: whether a persistent reference read through a component resolves in a new instance of the same file in
  another assembly, how faithfully each mate kind's definition reads back for a remake, and whether inserting a user
  sub-assembly can raise a dialog (S5, P2).

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
