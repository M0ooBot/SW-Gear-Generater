# W9 (issue #1: the user's work in a built assembly, and dog-clutch sleeves): the plan

**Authority and reading order.** `docs/PLAN-WORKBOOK.md` stays the authority; this plan says where W9 departs from it
and from W8's readings and rulings (`W8-PLAN.md` §0.3, `W8-INTERFACES.md` §9), each named in §0.2. GitHub issue #1
(`MoZ200701/SW-Gear-Generater`) is the source of the four problems; the user's own words on problem 4 set the first
requirement:

> "the thing about update cannot add a part is i have the assembly right then i made edits to some of its parts or
> added additional parts but then i straight up cannot use the build app anymore because it would overwrite all the
> things i did there"

**First requirement:** once the user has worked in the built assembly (edited app-built parts, added components of
their own, mated them), the app stays usable on it, and no app action destroys that work. It is the first phase
(W9a) because the code gives no reason to order otherwise: it needs no new geometry and no new SolidWorks write, only
reads and narrower refusals (§1, §2.1), and it is what makes every later phase usable on a worked-in assembly.

Everything below was read at `c351b1f` (W8's closing run in progress). Rules carried over unchanged (HANDOFF, *Rules
carried over*): commits by explicit path, no attribution lines, findings from committed `findings.py` only, the full
build first, a probe ahead only for a call new to the app that could hang, raise a dialog or damage a file or
session, SolidWorks 2026 the working version with one confirming build on 2024, each plan and result reviewed by a
separate agent.

---

## 0. Summary

### 0.1 The name, and what it changes in the plan's statements

**W9**, in four stages W9a–W9d. It is the next row of PLAN-WORKBOOK §6 because it changes the same import, record
and window W1–W8 built, and a W-number keeps the handoff, the boards and the results folder in one series. Two things
must change with the name:

- *The tests' made-up W9.* `tests/test_workbook_build.py:25-29` (and the fixture's users there and in
  `tests/test_workbook_window.py:30`) make a dog ring "a later phase's, W9" to keep the refusal channel tested
  (`build.LATER` and `geometry.LATER_KINDS` are empty: `workbook/build.py:37`, `workbook/geometry.py:228`). Once W9 is
  real, a test saying "dog rings are built in phase W9" reads as a claim. W9a's first package renames the fake to
  **W99** (strings only; no behaviour changes).
- *"W8 is the last phase."* PLAN-WORKBOOK §3.4 (line 279), §6 (lines 715-716) and HANDOFF (lines 515-516) say W8 is
  the last phase and that what this version does not build is an error naming no phase. W9 adds **no refusal
  channel**: `LATER` stays empty and everything W9 does not build stays an error naming no phase. The sentence becomes
  *"W8 was the last phase of the import as planned on 2026-11-11; W9 (issue #1) builds on it and leaves no row waiting
  for a phase."* That edit is made when W9a lands, not in this commit.

### 0.2 Readings for the user to overrule

Each is argued in §2. **K1–K6 are the heart of problem 4.**

| # | Reading | Instead of | Overturns |
|---|---|---|---|
| K1 | **What is the app's own** is what the record lists: the gear, carrier and layout components (by `Name2`), the mates (by name), the configurations named as modes, and in each app part the globals and features its plan made. Everything else in the assembly or a part is the user's. | Guessing ownership from names. | — |
| K2 | **A mate of the user's is left alone** unless it touches a component this press puts or re-places. Then Update refuses before changing anything, naming every such mate at once with the gear and the modes. A mate on the layout component, on the assembly's own planes, or between the user's own components never refuses. | Today: any unsuppressed mate not on record refuses, one per press (§1.3). The app suppressing the user's mate around its put (asked, §6 Q1). | W5 review M7, W8 J12's last sentence |
| K3 | **The user's features in an app part are kept.** Update changes only the app's globals; SolidWorks rebuilds the user's features after them; the job then reads each user feature's error state and names any in error. Nothing is saved (as today). | Refusing to change a part with user features; asking per part. | — |
| K4 | **Told before anything is written:** every job reads the user's work in the documents it opens and the finish records it (link record schema 7). The footer says, before the press, what Update will change and what of the user's it leaves. If the worker finds something of the user's in the way that the window did not show, it refuses before changing and records it; the next press goes ahead. No new control. | A check-only job and a question before each Update. | — |
| K5 | **Build again… says what stays behind** (the user's components, mates, and features in parts it makes new, all in the old files) and carries nothing over. | Re-inserting the user's components and re-pointing their mates in the new revision. | — |
| K6 | **Update adds and replaces parts (W9d):** a new gear on an existing frame shaft along Z±, inserted and mated as the build would mate it, every flag set and read back in every configuration; a part that needs a new file (bands, Flank, Part name) replaced by inserting the new part and deleting the old app component with its app mates, refused and named when a user mate touches the old component; and a gear mate of a gearbox with modes made again (a tooth change). | Every such edit structural (Build again…). | W8 J14 (in part), ruling 9.16 |
| K7 | **Reachability is a warning** under the nested-shafts rule of §2.2. | An error; the issue's narrower rule. | — |
| K8 | **The hub is a workbook row**, kind `hub`, on the sleeve's own shaft, built by the app as a toothed ring like a dog with the row's Bore; the app never adds one by itself. A sleeve with no hub row is warned of. | The app adding a hub; leaving the hub to the user, unchecked. | W8 J1 ("no hub") |
| K9 | **Minimum running clearance 0.5 × module per side, at least 0.5 mm**, a warning per mode. | A fixed mm figure; an error. | W8 J22 (extended) |
| K10 | **A sleeve declares two toothed bands** (two numeric columns, one at each end of its face); the span between is a relief bore of diameter m(z + 3), clearing a dog's tip by 0.5 m a side. One part. Engagement counts only toothed length. | One slider moving several rows. | W8 J4 (refined) |

### 0.3 STOP and ask (implementers)

- **Anything that would write to, suppress, delete, move or rename a component, mate, feature, global or
  configuration that is not on record.** This is the first requirement; the fake fails a test on any such call, and
  on SolidWorks the demonstration compares every user item's flag, error code and entities before and after.
- A read W9 adds (a mate's entities, a part's feature tree, a feature's error) found marking a document modified
  (`GetSaveFlag`), or reading `None` for a component other than the assembly's own.
- A put with a user mate on a gear (§4, M4) that SolidWorks accepts while leaving the gear off its frame without an
  error code.
- W9d: any dialog from inserting or deleting a component; a new component or mate whose per-configuration state does
  not read back as set.
- A fixture answer (§3) that disagrees with the code once written, or a shape the interface commit pins changed.

---

## 1. What happens today, traced to code

### 1.1 How the app knows its own

The link record's `GearboxRecord` (`store.py:554-607`) lists the layout part and its component, each gear's
`ComponentEntry` (`store.py:494-510`: part, `Name2`, frame, per-configuration frames), every mate by name
(`MateEntry`), the carriers and the modes. Each part's `.gear.json` lists its globals and features. Nothing records
what the user added. Every gearbox built since W5 is a turning one (a static build happens only with a W5 finding
missing), so Update runs `swbuild._update_motion` (`swbuild.py:4453`), and with modes its W8 branch.

### 1.2 (a) The user adds features to an app-built part (a keyway, a bore change)

- **Update with a value change on that part** (face width, backlash, and since `GEAR_MATE_RATIO_ROUTE = "remake"`
  (`findings.py:670`) a tooth change on a gearbox without modes): the part is passed with its globals and no feature
  list (`workbook/update.py:165`); the check reads only that every app global is still there (`swbuild.py:2481-2493`);
  `update_variables` sets the globals that differ and rebuilds once (`swbuild.py:1365-1384`). **The user's features
  are left in the part** and SolidWorks rebuilds them. Whether a keyway sketched on the bore or a face survives a
  teeth or face change, only SolidWorks can tell. If the rebuild reports an error, the app records a failure
  (*"SolidWorks reported an error rebuilding …"*, `swbuild.py:3368-3369`) and the job stops before the remaining
  parts and the assembly (`swbuild.py:3580-3596`); whether a user feature's error makes the rebuild report one is
  unmeasured.
- **An app global the user changed in SolidWorks** (say Bore Diameter 10 → 12 to fit their shaft) is **set back** to
  the workbook's value by the next Update (`planned_changes` compares text: `swbuild.py:1323-1341`). That is an
  overwrite, unsaved. The same holds for every other app-owned value: the layout's globals, a Face Z equation, a
  slide value per configuration, a recorded mate's suppression flag (D10), and the gears' positions.
- **A tooth change on a gearbox with modes** is refused in the worker's check phase before anything changes:
  *"The gear mate … would have to be made again, and making a gear mate of a gearbox with modes again is not in this
  version of Gear Generator, so nothing is changed; build the gearbox again."* (`swbuild.py:4695-4699`, ruling 9.16).
- **Build again…** reuses an unchanged part file as it is, the user's features with it: reuse checks the globals
  and only the features the `.gear.json` lists (`workbook/gearbox.py:33-40`, `PartReuse.features`). A changed part
  is made as a new file; the user's features stay in the old file only. If the user changed an app global, the live
  check finds the part not holding the record's values, nothing is built, and the next press makes it new (UI-DESIGN
  §9, *Build*, item 1).

### 1.3 (b) The user adds components and mates among them (sprocket, chain, shaft, housing)

- **Components with no mates:** Update finds the app's components by `Name2` and never touches others. They enter
  the interference check, which runs on the whole assembly (`swcom.py:3356`); a clash with a gear is reported
  under its components' names (`swbuild.py:2394-2413`). Nothing refuses.
- **Any mate among them refuses every Update.** The check phase walks the assembly's top-level mate group
  (`swcom.py:2380-2409`) and, without modes, raises at the **first** unsuppressed mate not on record, whatever it
  joins (`swbuild.py:4593-4602`): *"Mate12 is a mate in RangeBox.SLDASM that Gear Generator did not make, and it may
  hold the gears where Update SolidWorks would put them, so nothing is changed; suppress Mate12 in SolidWorks and
  press Update SolidWorks again."* With modes the same is judged in every mode and raises at the first mate on in any
  (`swbuild.py:4076-4100`): *"In modes H, N and L, Mate12 is a mate in RangeBox.SLDASM that Gear Generator did not
  make, … in SolidWorks, suppress Mate12 in H, N and L and press Update SolidWorks again."* A user with six mates
  learns of them one press at a time. Something in the mate group that is not a mate or a folder refuses too
  (`swbuild.py:4582-4591`). A configuration of the user's is left alone and listed (`swbuild.py:4047`), but Update
  refuses while it is the active one (`swbuild.py:4040-4045`).

This is the code behind "I straight up cannot use the build app anymore": the refusal does not depend on whether the
user's mate touches anything of the app's.

### 1.4 (c) A mate between the user's component and an app-built gear

Refused exactly as in §1.3, before anything changes. If the user suppresses it as told, Update goes ahead and may
put that gear (Update returns a turned train whenever it must move a gear, PLAN-WORKBOOK §4.5 W5 answer 2; with
modes, a press with anything to put puts every train in every mode, ruling 9.18); when the user turns the mate back
on, SolidWorks moves their component or reports the mate in error.

### 1.5 (d) Then the workbook is edited and the user presses

| Edit | Update SolidWorks | Build again… |
|---|---|---|
| A value (face, backlash, bore) | Goes ahead (a part's globals; gears re-placed or put), **unless the user has any unsuppressed mate** (§1.3) | — |
| A tooth change, no modes | Goes ahead, gear mate remade; same refusal for user mates | — |
| A tooth change, with modes | Refused (ruling 9.16, §1.2) | Offered |
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

**Safer than feared:** the app destroys none of the user's work in (a)–(d). Update never deletes anything and never
saves (PLAN-WORKBOOK §4.5, line 444; `swbuild.py:3415`), and it refuses in a check phase that writes nothing. Build
again… never overwrites a file (`SAVE_AS_OVERWRITES` guard, `findings.py:57`) and leaves the old assembly, with the
user's components and mates, on disk.

**Where it does harm:** (1) Update sets back app-owned values the user changed in SolidWorks (§1.2), unsaved. (2) A
later Update of the new revision that changes a shared part changes the old assembly's geometry under the user's
mates (said in the question, `ui_text.py:2177-2181`). (3) Build again… strands the work: the app's link moves to the
new revision and nothing of the app reaches the old assembly again. (4) A user feature that fails after Update's
rebuild may stop the job as the app's failure (inferred; unmeasured).

**Where it is unusable:** one unsuppressed mate of the user's anywhere, even between two of their own parts,
refuses every Update, one name per press (§1.3); and every edit of §1.5's structural rows sends the user to Build
again…, which leaves their work behind without saying so.

### 1.7 Problems 1–3 in the code

- A sleeve is the strip's internal ring at the row's teeth, module and face, toothed over its whole face; a dog the
  spur plan (`gears/clutch.py:1-13`, J1: no fork groove, hub or chamfers). Its only bore is the teeth.
- Engagement: a sleeve engages a dog on another shaft when it covers the dog's whole face (`modes.py:178`); a sleeve
  covering a dog on its own shaft is a warning that it engages nothing (`modes.py:164-168`). Nothing checks how a
  sleeve is held on its shaft or whether its shaft can reach it.
- The bridging warning fires only when `length > gap` (`modes.py:342`): equal is silent, so a neutral flush against
  two dogs at 0 mm is not reported (§3 shows it on the issue's box).
- The Gears sheet has no column a band or relief could be written in (`schema.py:138-161`).

---

## 2. The behaviour proposed

### 2.1 Problem 4: keep the user's work, keep the app usable (W9a, then W9d)

**W9a — the user's work is theirs** (no new SolidWorks write):

1. *Ownership (K1).* Whatever the record does not list is the user's.
2. *Mates (K2).* In the check phase each mate not on record is read for the components its entities are on
   (`IMate2.MateEntity(i).ReferenceComponent`, `None` for the assembly's own planes: verified on 2024 in the macro
   database, `API-LEDGER.md:602`, never used by the app). A mate whose entities are all on the user's components, the
   layout component or the assembly is left alone and listed. One that touches a gear or carrier component is *in the
   way* only when this press may put or re-place that component. That is decided before any change, conservatively:
   without modes, from `train_check` and the placements, as the put itself is; with modes, any press that will change
   something shows other modes and may put every train there (ruling 9.18, `baa1a56`), so every gear of a mated train
   counts as put, and only a quiet press with nothing to put goes past such a mate. Then the Update refuses before any
   change, naming every such mate, its gear and the modes it is on
   in, in one sentence: *"Update SolidWorks would turn HighDog back to its built place, and your mates Lock3 (on in H,
   N and L) and Concentric5 (on in H) hold it, so nothing is changed; suppress them in those modes and press Update
   SolidWorks again."* A press that puts nothing goes ahead past them. On a gearbox with modes this still stops most
   changed presses while a user mate holds a mated gear; §6 Q1 is the way past it.
3. *Features (K3).* For each app part it opens the job walks the feature tree (a walk already shown to mark nothing,
   `swbuild.py:2452-2455`); features the plan did not make are the user's. When Update changes that part's globals,
   it reads each user feature's error state after the rebuild and names any in error (*"SolidWorks rebuilt your
   Keyway in Gear_m1.25_N17 after the new teeth, and it is in error; nothing is saved, so close the part without
   saving to go back."*). A rebuild error that comes only from the user's features is said as theirs, and does not
   stop the job, if M3 (§4) shows the rebuild reports it.
4. *Told before (K4).* The finish of every job, a refused one included, records what it read of the user's work
   (link record schema 7, additive: per part path the user's features, and the user's components and mates with what
   each touches, with the time read). The footer's Update line then says, before the press, what Update would change
   and what of the user's it leaves (*"Update SolidWorks changes RangeSlv's part, where your Keyway follows the app's
   features; it leaves Sprocket-1, Chain-1 and 6 mates of yours as they are, and stops if it has to turn HighDog back
   while your Lock3 holds it."*). The worker reads again; something in the way that the record did not hold refuses
   before any change, is recorded, and the next press goes ahead.
5. *Build again… (K5).* The question gains, from the record: *"Your Sprocket-1, Chain-1 and 6 mates stay in
   RangeBox.SLDASM, and your Keyway stays in Gear_m1.25_N17, which RangeSlv's new part replaces; RangeBox_r2 has none
   of them."* Nothing is carried over: re-inserting the user's components and re-pointing mates at new components'
   faces is unprobed and could break the user's mates in ways no read catches.

*Not taken:* a check-only job and a question before every Update (two round trips on each press, for what K4 says
in the footer); the app suppressing the user's mates around its put (asked, §6 Q1); finding a renamed app component
by its part path (a later convenience).

**W9d — Update adds and replaces parts (K6).** A new gear on an existing frame shaft along Z± is built as a part
(the build's own part path), inserted into the open assembly (`AddComponent5`, used by the build), mated as the build
mates it (axis, along or lock, spline, mesh or coupling), and every new mate's and the new component's flag set and
read back in every configuration (the macro database: a mate made while a mode is active comes out suppressed in
some configurations, `API-LEDGER.md:220`; the J10 discipline). If it becomes its shaft's anchor (J9: the issue's hub
on Output, where the sleeve was a sliding anchor), the sleeve gains its spline mate. A part that needs a new file is
replaced: the new part inserted and mated, the old app component deleted with its app mates (a call probed ahead,
§4). A user mate on the old component refuses the replacement before any change, named. A gear mate of a gearbox with
modes is made again by W5's remake route (delete, add, rename; `findings.MATE_DELETE_ROUTE`) with its flags set and
read back in every configuration, lifting ruling 9.16. Still Build again… after W9d: a gear removed, a shaft added or
removed, Modes rows added or removed (each listed in §5 as deferrable).

### 2.2 Problem 1: reachability, and the hub

**The rule (K7), from what the workbook holds.** Shafts on one axis are nested tubes. A shaft is present at least
between its outermost gears on that axis (a carrier: its own gears and its planets' faces). Where a gear of shaft P
sits, any other shaft present there runs inside P. A sleeve's shaft O must be present over its **hub zone** (the hub
row's span, or with none the span its face shares in every position, which may be a single plane) and run from there
to one end of the axis. **O cannot reach the sleeve toward an end** when some other coaxial shaft P is present at the
hub zone and has a gear between the hub zone and that end: at the hub zone P must be inside O, at that gear O must be
inside P, and two tubes cannot cross. **Warn when both ends are blocked**, at the sleeve's Gears cell. The warning is
certain, not cautious: it uses only the least each shaft must span.

*The issue's box (§3).* With every shaft at the origin along Z+: Sun on Input at 10.5 (5.5…15.5), HighDog on Input
at −32 (−34.5…−29.5), LowDog on Carrier at −17 (−19.5…−14.5), RangeSlv on Output at −24.5 face 10, H −5 / N 0 /
L +5. Its spans are −34.5…−24.5, −29.5…−19.5 and −24.5…−14.5, which share only the plane z = −24.5: the hub zone.
Input is present over −34.5…15.5, which holds −24.5. Toward Z− HighDog (Input) lies between; toward Z+ Sun (Input)
does. Both ends blocked: *"Gears row 7: Output cannot reach RangeSlv: Input runs through RangeSlv's place (from Sun
at 10.5 to HighDog at −32), so Output would have to pass HighDog toward Z− or Sun toward Z+, each on Input."* Carrier
(present −19.5…15.5) does not hold −24.5 and blocks nothing by itself.

**The hub (K8).** The user decided on 2026-11-14 that a carrier is a skeleton because its plate and pins depend on
the gearbox at hand. A hub is mostly not that kind of thing: its working part is the sleeve's own teeth, which the
workbook already specifies, and its place and width are numbers the checks need (that a band rides it in every mode,
that its shaft reaches it). What does depend on the gearbox at hand is how it is fixed to its shaft (key, spline,
press fit), and that stays the user's, as it already is for every gear's bore. So: a `hub` row (one new kind word) on
the sleeve's shaft, built as a dog's toothed ring with the row's Bore; a band of the sleeve must cover it whole (or it
the band, the narrower covered) in every mode, else an error at that mode's cell; it engages nothing (no coupling)
and, as a non-sliding gear, becomes its shaft's anchor with the sleeve splined to it (J9, unchanged). The app never
adds a hub by itself (writing rows into the user's workbook is not something Export does). A sleeve with no hub row
is warned of: *"Gears row 7: nothing keys RangeSlv to Output: its whole bore is teeth and no hub row is under it; add
a hub on Output that a band of RangeSlv covers in every mode."*, adding when none could fit *"; as laid out none can,
since its 10 mm face slides 10 mm (H −5 to L +5) and its places share no length."* This warns every W8 workbook,
including W8's fixtures (their pins change); §6 Q4 asks whether to warn only when no hub could fit.

### 2.3 Problem 2: minimum running clearance (K9)

In every mode, for every dog or hub on another coaxial shaft that a toothed band of the sleeve does not engage there,
the axial gap between them must be at least **c = max(0.5 mm, 0.5 × module)** (0.625 mm at module 1.25). Scaled by
module because the chamfer and backlash a real dog needs scale with the tooth; floored so a fine module still gets
room. A gap from 0 up to c is a **warning** at that mode's Modes cell: *"Modes row 3: in N RangeSlv stands 0 mm from
HighDog and 0 mm from LowDog, which it does not engage there: leave at least 0.625 mm (0.5 × module) each side."* A
hub and a dog on different shafts are held to the same gap. The existing `length > gap` stroke warning stays for the
travel between positions.

### 2.4 Problem 3: bands and the relief bore (K10)

*Schema.* Two numeric Gears columns (working names **Start band** and **End band**, mm; the interface commit and the
board settle the words): the toothed length at the face's start (its end toward the shaft's Axis minus side) and at
its end. Blank both: toothed over the whole face, as today. Numeric cells avoid the Excel traps PLAN-WORKBOOK already
meets (`5-21` reads as a date, `-8` as a formula). Errors at the cell: bands on a row that is not a sleeve, a band
not positive, bands that leave no relief or exceed the face. More than two bands is not built (an error naming no
phase). Old workbooks have neither column and read as today; columns the app does not know are already kept.

*Engagement.* Each band is judged as a sleeve is today: a band covering a dog's whole face engages it; a band
covering part of one is an error. A dog under the relief is not engaged and must lie wholly within it (else the band
partial rule catches it). Clearance (§2.3), the stroke warning and the hub rule work per band.

*The part.* The strip's internal ring over the whole face, with the teeth removed over the relief to a diameter of
**m(z + 3)**: above the sleeve's root at either tooth depth the strip uses (m(z + 2.8) or m(z + 2.5)) and 0.5 m a side
over a dog's tip m(z + 2). A typed Rim must clear it (error). The op route is the interface commit's to choose from
proven ops; the herringbone groove's two blind extrudes and a plain ring between (`gears/helical.py:19-24`) are the
precedent; `Cut` has no blind depth today (`gears/base.py:254-258`). The bands are globals of the part, so a band
change on a banded sleeve is a value Update; giving bands to a sleeve built without them needs a new part (W9d
replaces it).

*The record.* The bands go into the sleeve's spec in its `.gear.json` and the link record; schema 6 records read
them as blank. The link record's schema 7 (§2.1) carries them; a schema 6 app refuses a schema 7 record and leaves it
as it is, as `store.py` already does for a newer record.

*Not taken:* one slider moving several rows. It gets engagement right with no new geometry but builds the loose parts
the issue complains of, needs a rigid mate between them, and has no relief bore.

---

## 3. The fixture: RangeBox (the issue's two-speed planetary)

Shafts, all frame and at the origin along Z+ unless said: Input (input, 1500 rpm, 10 N·m), Carrier, Planet (on
Carrier, X 26.25, 3 copies), Ring (fixed), Output (output). Gears (module 1.25, Box 20°, 98 %): Sun 29 on Input at
10.5 face 10; Planet 13 at 10.5 face 10; Ring 55 internal at 10.5 face 10; HighDog 17 dog on Input at −32 face 5;
LowDog 17 dog on Carrier at −17 face 5; RangeSlv 17 sleeve on Output at −24.5 face 10, Slides `H=-5, N=0, L=+5`.
Meshes Sun–Planet, Planet–Ring. Modes H, N, L. (Names follow the gear-name rule, so "High dog" is `HighDog`.)

**Before W9 (run through `assess` at `c351b1f`):** builds; four warnings, none about the clutch (the planet's
undercut and thin tip, the sleeve's tips inside its base circle, the undercut planet meshing the sun). H engages
HighDog, ratio 1.000; N engages nothing, neutral; L engages LowDog, ratio 2.896552 (1 + 55/29); Carrier 517.857 rpm,
Planet −1673.077 rpm about its own axis. The same box with the issue's one long sleeve (face 26 at −35, H −7.5 / N 0
/ L +7.5) is refused: *"Modes row 4: in L RangeSlv engages HighDog and LowDog at once, which joins Input to Carrier:
as written the box is jammed in this mode."*, with the stroke warning and *"H and N engage the same"*.

**After W9b (the same workbook):** three warnings more: no hub, and none can fit (§2.2); Output cannot reach
RangeSlv (§2.2); in N 0 mm from HighDog and LowDog (§2.3). Engagement and speeds unchanged.

**After W9c (the fix, `RangeBox_Fixed`):** RangeSlv face 26 at −35, Start band 5, End band 5 (relief 16, Ø 25.0),
Slides `H=-7.5, N=0, L=+7.5`; Hub 17 hub on Output at −45.5 face 20 (−55.5…−35.5). Hand-worked answers to pin:

| Mode | End band (front) | Start band (rear) on Hub | Relief | Engaged | Least running gap |
|---|---|---|---|---|---|
| H | −34.5…−29.5 covers HighDog | −55.5…−50.5 | −50.5…−34.5 | HighDog; ratio 1.000 | LowDog 10 |
| N | −27…−22 | −48…−43 | −43…−27 holds HighDog | none; neutral | 2.5 each side |
| L | −19.5…−14.5 covers LowDog | −40.5…−35.5 | −35.5…−19.5 holds HighDog | LowDog; ratio 2.896552 | start band to HighDog 1.0 |

Hub to HighDog: 1.0 (≥ 0.625). Reach: hub zone −55.5…−35.5, Input present −34.5…15.5, nothing toward Z−: reached.
No warning from W9b's checks, no stroke warning (a 5 mm band against a 10 mm gap). In SolidWorks: Hub is Output's
anchor (axis, along), `RangeSlv splined to Hub`, `RangeSlv along Output` with H/N/L values, couplings on in H and L
only. The key is checked by an independent agent, as W8's was.

---

## 4. What must be measured on SolidWorks

Under the rule: a full build first; a probe ahead only for a call new to the app that could hang, raise a dialog or
damage a file or session.

| # | Unknown | How |
|---|---|---|
| M1 | Reading a user mate's entities' components (`MateEntity(i).ReferenceComponent`) on concentric, coincident, lock and gear mates, user–user, user–layout, user–gear, and that it marks nothing | W9a full build (a read; verified on 2024 for gear mates' entities, `API-LEDGER.md:585`, `:602`) |
| M2 | The feature walk telling the plan's features from the user's, and each user feature's error code after a rebuild | W9a full build |
| M3 | Whether `update_variables`' rebuild reports failure when only a user feature fails (a keyway dimensioned to a tooth edge) | W9a full build, one section |
| M4 | A put of a gear whose user lock to a free user component is on: is the component carried, does the put hold, what error codes | W9a full build, one section; decides §6 Q1's follow-up |
| P1 | Deleting a component from an assembly with configurations (`Select2` then `EditDelete`, or `DeleteSelection2`): any "delete mates too?" confirmation | **Probe ahead** (a dialog), on a scratch assembly, 2026 then 2024, before W9d's packages rely on it |
| M5 | `AddComponent5` into a reopened assembly with mode configurations: the new component's state in each configuration (each configuration's own setting for new components), and setting and reading it | W9d full build (inserting is used by the build; a per-configuration read is not a dialog risk) |
| M6 | Mates made in that assembly (axis, along, spline, coupling) and a gear mate remade there: flags set and read back in every configuration | W9d full build |
| M7 | The banded sleeve's part (the relief op route) on both versions | W9c's build of `RangeBox_Fixed` from scratch |

The demonstration of each stage works on a copy of one built folder (J24's scheme) into which the script puts the
user's work: a part of its own (a block "housing", a strip-built "sprocket"), mates among them, to the layout and to a
gear, and a keyway cut in a gear part.

---

## 5. Phases, in order

The user is watching usage: the leanest sound order is below, each stage closing before the next is planned in
detail. **W9a gives the app back soonest**, and alone ends "cannot use the app" for every edit Update already
carries. W9b is nearly free. W9c and W9d can wait for the user's word.

**W9a — the user's work is theirs.**
- *Packages:* A (worker: the mate entities read, the feature walk, the in-the-way rule, the after-rebuild read, all
  user mates named at once); B (planning, record schema 7, the inventory in the finish, the Build again… clause, the
  footer line in `ui_text`, UI-DESIGN §9 and the boards' footers redrawn; the W99 rename).
- *Tests against the fake:* user–user and user–layout mates never refuse; a user mate on a gear refuses only when that
  gear is put or re-placed, every one named, before any write; no call ever targets an item not on record (a fake
  that fails on one); user features survive a value update and one in error is named; the inventory reaches the
  footer before the press; a mate found in the way that the record did not hold refuses and is then recorded; the
  Build again… question names what stays behind.
- *Done when:* the suite is green; on SolidWorks 2026 a copy of RangeBox with the user's components, their mates
  among themselves and to the layout, and a keyway in a gear part takes a value Update, a Modes-pick Update and a
  quiet Update with no refusal, every user item's flag, error code and entities unchanged and the keyway rebuilt;
  with a user lock added on a gear, a changed Update refuses before any write naming it and a quiet press with
  nothing to put goes past it; M1–M4 answered; 2024 confirms (the
  issue was seen on 2024, so run it straight after); reviewed.
- *STOP:* §0.3.
- *Cost:* SolidWorks about 1 h on 2026 and 45 min on 2024; about 8 agent runs (plan review, 2 packages, their
  review, the demonstration script and its review, the run's review, plus the orchestrator's own runs).

**W9b — sleeve checks (problems 1 and 2).** Pure, Linux-tested, no SolidWorks.
- *Package:* one (`modes.py`, `checks.py`, sentences; W8 fixtures' warning pins updated).
- *Tests:* §3's "after W9b" answers; the rule's certainty (a nested input through a hollow carrier is not warned);
  clearance at exactly c is clean, below it warned.
- *Done when:* green and reviewed. *STOP:* a W8 fixture newly warned in a way §2.2–§2.3 do not predict.
- *Cost:* 0 SolidWorks; 2 agent runs.

**W9c — bands and the hub kind (problem 3, problem 1's hub).**
- *Packages:* one for schema, model, engagement per band, the `hub` kind and its rules, the sleeve's relief op, the
  record fields; the board for the Gears sheet's two columns (no window control changes).
- *Tests:* §3's `RangeBox_Fixed` table; old workbooks and schema 6 records read as before; the banded plan equals the
  internal ring's plus the relief.
- *Done when:* green; `RangeBox_Fixed` built from scratch on 2026 (M7) with every mode's engagement, slides and
  interference as §3, confirmed on 2024; reviewed.
- *STOP:* the relief op failing on either version; a mode reading other than §3.
- *Cost:* about 20 min on 2026 and 15 min on 2024; about 4 agent runs.

**W9d — Update adds and replaces parts (problem 4's "cannot add a part").**
- *Packages:* P1 probe first; A (worker: insert, mate, per-configuration flags, delete with app mates, remake with
  modes); B (classify: what moves from structural to Update; the sentences; UI-DESIGN §9).
- *Tests:* adding a gear on an existing shaft and a hub that becomes an anchor; replacing the sleeve; a user mate on a
  replaced component refuses before any write; a tooth change on a gearbox with modes remakes and reads back.
- *Done when:* on a copy of the built RangeBox with the user's work, the workbook edited to `RangeBox_Fixed` and one
  Update adds Hub, replaces RangeSlv and leaves every user item as it was, each mode then engaging and turning as §3;
  confirmed on 2024; reviewed.
- *STOP:* §0.3; P1 showing a dialog (then the fallback is suppressing the old component in every configuration, put
  to the user).
- *Cost:* probe about 15 min per version; the demonstration about 1.5 h on 2026 and 1 h on 2024 (Updates that put
  every mode ran 4–9 min each in W8); about 9 agent runs.

**Deferrable** (each its own small follow-up, on the user's word): the app suppressing the user's mates around its
put (§6 Q1, after M4); Update removing a gear, adding or removing a shaft, adding or removing Modes rows; Build
again… carrying the user's work over; finding a renamed app component by its part path.

**Total if all four run:** about 4.5–5 h of SolidWorks and about 23 agent runs, W9a about a third of it.

---

## 6. Open questions for the user

Each has the reading the work goes on with if unanswered.

1. **A mate of yours holds a gear Update must turn back or move.** Recommended: Update stops before changing
   anything and names every such mate (K2). Alternative: the app suppresses those mates around its put, turns them
   back on and says so, as it does with its own locks; W9a's M4 measures whether that is sound first.
2. **Build again… and your work.** Recommended: it says exactly what stays behind in the old files and carries
   nothing over (K5); W9d makes Build again… needed far less. Alternative: it carries your components and mates into
   the new revision, a much larger and riskier job.
3. **How a sleeve with a relief is written.** Recommended: two band lengths on the sleeve's row, one part (K10).
   Alternative: several rows that one slider moves together, several parts.
4. **The hub.** Recommended: a row you write (kind `hub`), built by the app as a toothed ring with your Bore, and a
   warning on every sleeve with no hub row (K8). Alternatives: warn only when no hub could fit; or the app adding a
   hub by itself.
5. **Running clearance.** Recommended: 0.5 × module a side, at least 0.5 mm, a warning (K9). Alternative: a fixed
   figure (the issue suggests 0.5–1 mm).

---

## 7. What reading could not settle

- Whether a user feature's error makes SolidWorks report the part's rebuild as failed (M3), and so whether today's
  Update stops on it.
- Whether a put carries a user component locked to a gear (M4); K2 is written so that it does not matter.
- How SolidWorks 2024 and 2026 place a component inserted into an assembly with configurations in the configurations
  not active (M5); W9d sets and reads every flag rather than relying on either.
- How the window's footer fits one more line on a short screen: W8's 2024 run already found the built footer cut off
  at 150 % (HANDOFF, the ruling still open); W9a's line must be weighed with it.
