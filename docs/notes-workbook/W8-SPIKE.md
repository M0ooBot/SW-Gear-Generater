# W8 spike: collinear gear mates, a slide under one, and configurations

The questions, asked before W8's packages are written around them: W8-PLAN §4.3 (the spline and coupling as 1 : 1
gear mates between collinear axes, a slide under the spline, configurations, a coupling turned on at an angle, save
and reopen), and the two calls §7 names as probed ahead: `ShowConfiguration2` on a mated assembly, and the save and
reopen of an assembly with several configurations, both under a dialog watcher.

The evidence is one passing run of probe `w8_modes_spike` (`src/gear_generator/probe/p8_motion.py`) on SolidWorks
2026 (34.1.1), in a fresh session. It ran from a snapshot of the app as of 64f4620 with the probes as of 000ea0c. The
result is `probe/results/w8-spike-20261114-204436.txt` and its `.json`; every number below is from them. Three
earlier attempts stopped on the probe's own use of component handles. Each taught something, and their logs are kept
beside it (see "The run's history"). Under the testing rule of 2026-11-14 there was no 2024 run. Nothing goes into
`findings.py`: the plan pins its findings against a result file when it is written.

## What was built

- **Parts.** The app's own builder (`build_gearbox`, a static plan) made the two parts: a spur gear (30 teeth,
  module 1.5, 20°, face 10, bore 8) and an internal spur ring (30 teeth, module 1.5, 20°, face 10). These are the
  strip's kinds, not yet a W8 sleeve or dog. The spur part is inserted twice, as the anchor **A** and the dog **D**;
  the ring is the sleeve **S**.
- **Layout.** A body-less layout part, fixed, holds `A Axis` and `D Axis` on one line along +Z. The probe's layout
  parts take positive coordinates only, so the line is at (60, 60).
- **Mounts.** A and D are held as W5 holds an anchor: AXIS coincident and ALONG, a distance from the origin to the
  layout's Front, at z = 10 for A and z = 40 for D. S has only its AXIS mate to `A Axis`, with its origin at z = 10
  and its phase at 6°, half a pitch. All three read `GetConstrainedStatus` 2 (under-defined) after mounting.
- **Drive.** As in W5: an angle mate from A's Top plane to the layout's Right, its D1 linked to a global `"Drive"`,
  moved 90 → 120 with a top-only rebuild, then set back and deleted. Turns are read about each component's own axis.
- **Mate calls.** Every gear mate was `AddMate5` type 10, CLOSEST, ratio 1 : 1, made under `CommandInProgress` and
  renamed at once. Its sense was read straight after: `IGearMateFeatureData.Reverse` and both
  `IMateEntity2.EntityParams`.

## 1. The spline between collinear axes, both Flips

| Flip | AddMate5 | moved on make | Reverse | entity directions | W5 rule says | H says | drive: A, S, D |
|---|---|---|---|---|---|---|---|
| False | 1 (no error) | 0 mm | True | (0,0,1), (0,0,1) | same way | same way (m = +1) | **+30, +30, 0** |
| True | 1 (no error) | 0 mm | False | (0,0,1), (0,0,1) | opposite | opposite (m = −1) | +30, −30, 0 |

- **AddMate5 accepts it.** Both entities read the same line, (60, 60) along +Z: one point at z = 9.4382 mm, the
  other at 9.4296 mm.
- **Nothing moves when it is made.** The worst frame change was 0. S still reads constrained status 2, free to slide.
  No mate is in error.
- **The drive works.** With Flip False, S turns +30° with A, the same way and 1 : 1. D does not turn, and nothing
  moves along the axis. Set back, every frame returns to within 1.4e-14 mm.
- **The Flips control works.** Exactly one Flip turns them together (False); the other turns S opposite. The
  read-back named the right one by both rules. W5's rule is `(Reverse == parallel) == same way`. W6's H, from tier 9,
  is `m = (+1 if Reverse else −1)·τA·τB`, with τ = (+1, +1) and entities paired by selection order on parallel axes.
- **Caveat.** Both entities pointed along their own +Z, so τ was never −1 here either, as in tier 9.

The Flip False spline was made again and kept: status 1, Reverse True, both rules say same way.

## 2. The slide under the spline

S's slide was made with W5's ALONG route: a distance from S's origin to the layout's Front, at 10 mm, D1 linked to
the global `"S Face Z at P"`. The global was moved 10 → 20 with a top-only rebuild:

- S's origin moved **+10.0 mm** along the axis, and 0.0 mm off it.
- S's turn relative to A changed by **0.0°**, and every mate error code stayed 0.
- The spline still reads Reverse True, and both rules still say same way.
- Driven again: A +30, S +30, D 0. Nothing moved along the axis. Set back within 7e-15 mm.

## 3. The coupling

The coupling S–D was made at 1 : 1 with Flip False. It returned status 1 and read Reverse True, with both directions
(0,0,1); both rules said same way, so it was not remade. All three components still read status 2, with no mate
error. Driven: **A, S and D each +30°**.

## 4. Configurations

X and Y were added with `IConfigurationManager.AddConfiguration2(name, "", "", 0, "", "", True)`. Each returned an
`IConfiguration` and activated itself, read back by `ConfigurationManager.ActiveConfiguration.Name`, with no window.

**Component handles go stale on every configuration change.** This held in every run.

- After each `AddConfiguration2` and each `ShowConfiguration2`, every `IComponent2` held from before answers
  `Transform2` with **None**, and `IsFixed` with **False**, including the fixed layout's. That is a wrong answer,
  not an error.
- Fetched again with `IAssemblyDoc.GetComponentByName(name)`, every handle answers correctly. The layout reads
  `IsFixed` **True** in X and in Y, so **AddConfiguration2 carries the fixed state over** (the plan's S3 question).
- Held handles stay good across `DeleteConfiguration2` of a configuration that is not active.
- In the earlier attempts, a freshly fetched handle twice answered strangely once. In attempt 2, `GetModelDoc2`
  returned None. In attempt 3, `Name2` returned an empty string, so a selection string built from it named no
  component. The passing run, which records both on every fresh handle, saw neither. So selections after a change
  were made by `SelectByID2("<feature>@<component>@<assembly>")` with names read before any configuration existed.

**Setting flags.** Y was active.

- **The first two `SetSuppression2` calls, straight after `AddConfiguration2` with no rebuild between, misbehaved
  in all four runs.** `SetSuppression2(0, 3, ["Y"])` on the slide P **raised 0x80010105**, yet P did read suppressed
  in Y. The same call on the coupling **returned False** and did nothing.
- After a top-only rebuild and one more mate, all six later calls returned True and read back as meant. The calls
  were `SetSuppression2(0 or 1, 3, VARIANT(VT_ARRAY | VT_BSTR, names))`.
- **A mate made while Y was active** (the second slide Q, at P + 20) came out **suppressed in Default and on in X
  and Y**. That is neither "on everywhere" nor "only here". The plan sets every flag explicitly, so it does not
  matter, but no default may be assumed.
- **Q's D1 did not link.** The global `"S Face Z at Q"` went in by `IEquationMgr.Add2`. The link
  `"D1@S along A at Q" = "S Face Z at Q"` returned **−1** from the same `Add2`, which had linked P's D1 while only
  Default existed. The API help for `Add3` says it is the call for documents with several configurations. Which form
  links here was not tried; it needs a probe before the plan relies on it. Q held S at its made distance (30 mm)
  regardless.

**Flags read back** by `IsSuppressed2(3, ["Default", "X", "Y"])`. One flag per name, in that order; S means suppressed.

| Mate | unshown | after showing X | after showing Y | after X again | after deleting Default (X, Y) | reopened (X, Y) |
|---|---|---|---|---|---|---|
| S splined to A, the five mounts | `---` | `---` | `---` | `---` | `--` | `--` |
| S along A at P | `--S` | `--S` | `--S` | `--S` | `-S` | `-S` |
| S along A at Q | `SS-` | `SS-` | `SS-` | `SS-` | `S-` | `S-` |
| S engages D | `--S` | `--S` | `--S` | `--S` | `-S` | `-S` |

*Note, 2026-11-15.* The spike asked in the document's own configuration order (Default, X, Y, as they were made), so
the flags above are right, but "in that order" does not hold in general. `IsSuppressed2(3, names)` answers in the
document's configuration order (`GetConfigurationNames`), filtered to the names asked, whatever order they are passed
in; asked one name, it answers that configuration's flag. `GetSystemValue3(3, names)` answers in the order passed.
Evidence: `probe/results/w8-configuration-order-20261115-092100.txt` (SolidWorks 2026, read on the assembly W8 s0's
first run left open). The app has asked one configuration per call since `03a4e51`.

**ShowConfiguration2** went X → Y → X under the dialog watcher, each show followed by `ForceRebuild3(True)`:

| Shown | returned | dialog | active | S's origin z | mate errors | drive: A, S, D |
|---|---|---|---|---|---|---|
| X | True | none | X | 10.0 (P) | none | +30, +30, **+30** |
| Y | True | none | Y | 30.0 (Q) | none | +30, +30, **0** |
| X | True | none | X | 10.0 (P) | none | +30, +30, **+30** |

- The top-only rebuild after a show is enough: S stands at its configuration's slide and every turn is right.
- No dialog appeared on any show, add or delete.

**The app's existing reads in a configuration a mate is off in** (Y, where P and the coupling are off):

- **The mate-group walk** lists all nine mates in every configuration, suppressed ones included, in creation order.
- **`IsSuppressed2(1, …)`**, W5's this-configuration read, gives the active configuration's flags correctly in X and
  in Y.
- **Error codes:** no nonzero code on any mate in X or Y.
- **The sense read-back of the suppressed coupling** reads normally in Y: Reverse True, both entities, with S's point
  at its Y place (z = 29.44 mm). Both rules say same way. The read is usable on a suppressed mate.
- **GetSaveFlag after a switch** could not be told apart while the assembly was new, since it read modified
  throughout. On the reopened file it was: **`ShowConfiguration2` marks the assembly modified**, False → True before
  the rebuild, and **marks no part**. The `IsSuppressed2(3, …)` reads and the sense read-backs on open marked
  nothing (all four documents False).

**Deleting the template's configuration:** `DeleteConfiguration2("Default")`, with X active, returned True with no
window. The names read back `["X", "Y"]`, X stayed active, and the X/Y flags were unchanged.

## 5. A coupling turned on at an angle

Y was shown, and D was put +5° about its own axis (`Transform2` put, with the coupling off in Y). S's turn relative to
D went **−6.0° → −1.0°** in Y. Then X was shown and rebuilt:

- The relative turn read **−6.0°** again. **D was back at its angle from before the put** (0.0° from it), with no
  mate error and no window.
- The coupling still read Reverse True and same way. Driven in X: A, S and D each +30°.

So the coupling did **not** keep the 5° it found. D returned to where X had it. This run cannot tell which of two
causes did it: SolidWorks remembering D's place per configuration, or the gear mate restoring the relation it was
last solved at.

## 6. Save, close, reopen with several configurations

- **Save.** `SaveAs3`, silent, with X active: no window. The assembly reads unmodified after it.
- **Open.** `OpenDoc6`, twice, under the watcher.
  - **The active configuration on open is X**, the one active at the save.
  - The configuration names read back `["X", "Y"]`.
  - **Every document reads unmodified on open.**
  - The only window was SOLIDWORKS's load-progress box: no title, class #32770, text such as "Opened 4 Components /
    Updating Assembly / Elapsed time", and Close / Do not show again / Hide Details buttons. It stood 0.53 s and
    closed itself, so nothing was answered.
- **As saved.**
  - Every flag reads as saved.
  - S stands at 10 mm.
  - The spline and the coupling read Reverse True, and both rules say same way.
  - There are no mate errors.
- **Shows after reopening.**
  - `ShowConfiguration2("X")` while X was already active returned **False**, with the active name still X. The plan
    already says to judge by the name.
  - Y returned True and put S at 30 mm.
  - Driven in X: A, S and D each +30°. In Y: A and S +30°, D 0.
- **Close unsaved after a switch.** In the first reopening, showing Y marked the assembly. `ISldWorks.CloseDoc` then
  returned in 0.2 s with **no dialog**, and nothing of the spike stayed open. The second open came up in X, so the
  switch was discarded without a word, as W5's unsaved Update close is (UNSAVED_UPDATE_CLOSE).

## What it means for the plan

**What holds:**

- **J8 holds.** SolidWorks accepts a 1 : 1 gear mate between collinear axes. Nothing moves on the make, the sleeve
  stays free to slide, and the drive turns them together 1 : 1. Exactly one Flip is right, and the read-back names
  it: `COLLINEAR_GEAR_MATE_SENSE_READ_BACK` can be True from this file (steps 1–3 and 5 agree). W5's rule and W6's H
  agree, with τ never −1 here.
- **`COLLINEAR_GEAR_MATE_HOLDS_SLIDE` can be True:** the slide moves S 10 mm with the spline on, its relative turn
  unchanged, and the turn still 1 : 1.
- **Per-configuration distance mates solve here**, unlike assemblies/07's case: each configuration has exactly one
  SLIDE on, and no mate is in error in either.
- **These calls work as the plan writes them,** with the flags read back:
  - `AddConfiguration2(name, "", "", 0, "", "", True)`;
  - `ShowConfiguration2(name)` judged by the active name;
  - `SetSuppression2(0 or 1, 3, VT_ARRAY | VT_BSTR names)` and `IsSuppressed2(3, names)`;
  - `DeleteConfiguration2`;
  - a top-only rebuild after each show;
  - the save, and reopening in the configuration last active.
- **No call raised a dialog.**
- **The S3 question is answered:** `AddConfiguration2` carries a fixed component's fixed state over, as long as it is
  read through a fresh handle.

**What must change:**

1. **Fetch every component handle again after every `AddConfiguration2` and `ShowConfiguration2`.**
   - A held handle silently answers `Transform2` None and `IsFixed` False.
   - So §1.8's S3 step, "W5's `Fix`, which reads `IsFixed` first", would read False on a held handle and try to
     re-fix the layout.
   - Every frame read in the per-mode check, `place_component`, `_verify` and the interference pass must use handles
     fetched after the show.
   - Selections after a change should go by held names (`SelectByID2` on the full name), not by a fresh handle's
     `Name2` or `GetModelDoc2`. Each misbehaved once, in two of the four runs.
2. **Linking a SLIDE's D1 while several configurations exist failed with `Add2` (−1).** §1.8 step 3 makes each
   mode's SLIDEs, with their `LinkDimension`, after the configurations are added. As written, every SLIDE after the
   first configuration's would be left unlinked, so the slide globals would move nothing.
   - The likely route is `IEquationMgr.Add3` with an all-configurations option, which the API help names for this
     case. It is untested and needs a probe before the interface commit.
   - An alternative to probe is to make every SLIDE and its link while only the template configuration exists, then
     set flags. This would need each extra SLIDE suppressed at once, before the solver sees two.
3. **Rebuild between `AddConfiguration2` and the first `SetSuppression2`,** and never trust its return value:
   - straight after the add, the first call raised although it took effect, and the second returned False and did
     nothing;
   - the plan's order (add every configuration, then show and rebuild each before its mates) already puts a rebuild
     there, and keeping it is required;
   - the read-back the plan already makes is what catches it.
4. **§1.9 and the J11/J26 out-of-step path assume something this run contradicts.** They say a newly engaged
   coupling holds whatever relative angle it finds. Here, turning D in Y and showing X brought D back to X's angle,
   with no error and no tooth on tooth: `COUPLING_KEEPS_ANGLE_ON_SWITCH` reads False.
   - The out-of-step case may not arise this way, and a switch can turn a gear by itself (D moved 5°).
   - Whether SolidWorks keeps rotations per configuration or the gear mate restores its relation is not settled by
     this run. A follow-up with a free component beside the coupled one would tell them apart. Until then, §1.9
     should not lean on GOTCHAS §83 for rotations.
5. **A show marks the assembly modified, and no part.** A quiet Update that shows modes to check them leaves the
   assembly modified. Closing it unsaved discards without asking, the same as W5's unsaved Update.
6. **A mate made while a non-template configuration is active comes out suppressed in the template and on in the
   others.** The plan's explicit set-and-read-back covers it; record it as the reason, in place of assemblies/07's
   "inverse".

## The calls that worked, exactly

```python
cm = doc.ConfigurationManager
cm.AddConfiguration2(name, "", "", 0, "", "", True)          # adds and activates; returns IConfiguration
cm.ActiveConfiguration.Name                                   # the check, after every add or show
doc.ShowConfiguration2(name)                                  # True; False when already active; no dialog
doc.ForceRebuild3(True)                                       # after every show: enough to re-solve the slides
names = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_BSTR, configs)
mate_feature.SetSuppression2(0, 3, names)                     # 0 suppress / 1 unsuppress, 3 = the listed ones
mate_feature.IsSuppressed2(3, names)                          # one flag per name, in order; marks nothing
doc.DeleteConfiguration2(name)                                # True for a configuration not active
asm.GetComponentByName(name)                                  # again after every add or show
ext.SelectByID2(f"{feature}@{component}@{assembly}", "PLANE" | "EXTSKETCHPOINT", 0, 0, 0, append, 1, None, 0)
```

## The run's history

Four runs, each in a SolidWorks 2026 started fresh for it with no document of the user's open. Each SolidWorks was
exited by the probe agent after its run. The three that stopped are kept as `.txt` logs; the passing run as `.txt`
and `.json`.

1. `w8-spike-attempt-20261114-202111.txt` got through steps 1–5. It stopped at the first `ShowConfiguration2`: a
   held component answered `Transform2` with None. The same run read the layout's `IsFixed` False in X and Y through
   held handles; the later runs show that this was the stale handle.
2. `w8-spike-attempt-20261114-202929.txt` fetched handles again after each change and recorded the held ones. It
   stopped selecting S's origin, because a fresh handle's `GetModelDoc2` returned None.
3. `w8-spike-attempt-20261114-203634.txt` read the plane names and S's part beforehand. It stopped selecting S's
   origin again: the fresh handle's `Name2` was empty.
4. `w8-spike-20261114-204436` selects by held names everywhere after a change, and passed (34 pass, exit 0; the
   spike took 141 s).

Steps 1–5 read the same in every run that reached them. So did the stale held handles, and so did the first
`SetSuppression2` calls after `AddConfiguration2` (raised, then False).

## Follow-up, 2026-11-14: a slide per configuration, and what a configuration keeps of a turn

One more run, probe `w8_followup` (same file), on SolidWorks 2026 (34.1.1) in a fresh session. It used a snapshot of
64f4620 with the probes as of 00b03e5, and passed first time (34 pass, exit 0; the probe took 75 s). The result is
`probe/results/w8-followup-20261114-205913.{txt,json}`.

The assembly is the spike's, with one change and one addition:
- **The slide is changed.** S has a single slide: one distance mate from its origin to the layout's Front, typed at
  10 mm, linked to no global.
- **F is added.** A third component (the spur part again), on its own `F Axis`, AXIS and ALONG only, with no gear
  mate anywhere.
- **The coupling** S–D is on in Default and X and off in Y, as before.

The signatures came from sldworks.tlb and the enum values from swconst.tlb:
- `IDimension.SetSystemValue3(NewValue, WhichConfigurations, Config_names) -> int`;
- `IDimension.GetSystemValue3(WhichConfigurations, Config_names) -> VARIANT`;
- `swSetValue_InSpecificConfigurations` is 3, and `swSetValue_Successful` is 0;
- `swSpecifyConfiguration` is 3.

### A. One distance mate, its value per configuration: it works (option 1)

| Step | returned | GetSystemValue3(3, [Default, X, Y]) without activating | S's origin z |
|---|---|---|---|
| Before any per-configuration set (Y active) | | 0, 0, **10** | 10 |
| `SetSystemValue3(0.030, 3, ["Y"])`, Y active, then a top-only rebuild | **0** | 10, 10, **30** | 30 |
| Show X, rebuild | True | 10, 10, 30 | **10** |
| Show Y, rebuild | True | 10, 10, 30 | **30** |
| Show X, rebuild | True | 10, 10, 30 | **10** |
| `SetSystemValue3(0.035, 3, ["Y"])` **while X is active**, rebuild | **0** | 10, 10, **35** | 10 (X untouched) |
| Show Y, rebuild | True | 10, 10, 35 | **35** |
| Saved (`SaveAs3`, silent, X active), closed, reopened (`OpenDoc6`) | | 10, 10, 35 | X 10, Y 35, X 10 |

Every step read no mate error and raised no dialog.

- **The value reads back as typed in each configuration, without activating it.** It is a driving dimension; the
  set returns 0, not "driven".
- **An Update can change one configuration's value while another is active.** X's sleeve does not move, and the
  other configuration takes the new place when shown.
- **It survives save and reopen.** The file reopens in X, every document unmodified, and the reads mark nothing.
  The only window is the load-progress box, which closes itself.
- **Two cautions:**
  - Before a configuration has its own value, `GetSystemValue3` reads **0** for every configuration that is not
    active. Read it only after setting each configuration's value.
  - `IDimension.SystemValue` on the handle read **30** in X while S stood at 10. Use `GetSystemValue3` with the
    configuration name, never `SystemValue`.
- **What a set marks** could not be told, because the new assembly read modified throughout. The parts read
  modified too, as they did in the spike from the mounts on.

So options 2 (`Add3`) and 3 (two mates per slide) were not needed, and `Add3` was not tried.

**For the plan: one SLIDE per slider, not one per position.**
- Make it once, with its first mode's distance. After the configurations are added (and a rebuild), give each mode
  its value with `SetSystemValue3(z_front_m, 3, [mode])`.
- Read them all back with `GetSystemValue3(3, modes)`.
- There are no slide globals and no per-configuration suppression for slides. That removes item 2 above, and makes
  most of item 3 moot for slides, since SetSuppression2 remains only for couplings and sliding meshes.
- §1.7's `"<Gear> Face Z at <position>"` globals and §1.8's SLIDE-per-position build go. An Update that moves a
  position sets that configuration's value directly.
- The `"point"` coincident case for a position at the Front plane (z_front = 0) was not tried; a distance of 0 may
  need W5's rule.

### B. What a configuration keeps of a turn: each configuration keeps its own positions

Y was active (coupling off). F was put +20° about its own axis and D +5°, each by a `Transform2` put on handles
fetched after the last change, then a top-only rebuild. The table gives turns from the positions in Y before the
puts:

| Then | F (no gear mate) | D (coupling on in X only) | A, S |
|---|---|---|---|
| In Y after the puts | 20 | 5 | 0, 0 |
| X shown | **0** | **0** | 0, 0 |
| Y shown again | **20** | **5** | 0, 0 |
| X again, then F put +10° in X | 10 in X | 0 | 0, 0 |
| Y shown | **20** (the put in X did not reach Y) | 5 | 0, 0 |
| X shown | **10** | 0 | 0, 0 |
| Saved, reopened: X, Y, X | 10, 20, 10 | 0, 5, 0 | 0, 0 |

There were no errors and no windows throughout.

- **SolidWorks 2026 keeps a component's place per configuration**, including the turn of a free component with no
  gear mate, and keeps it through save and reopen.
- So the spike's §5 result, D back at X's angle, is this, not the gear mate restoring a relation. D behaves exactly
  like F.
- This contradicts GOTCHAS §83 and assemblies/07 ("component positions are not stored per configuration"), at least
  on 2026 for a freedom the mates leave open. Those were recorded on 2024 for a free mechanism; 2024 was not run here.

**What "the user's turn" means across modes.** A turn the user gives the train in one mode stays in that mode.
Every other mode keeps the positions it last had, and switching back finds each mode as it was left. A coupling
engaged in another mode therefore meets that mode's own last positions, not the turned ones. §1.9 must be rewritten
on this footing:
- No newly engaged coupling inherits an angle from another mode.
- No tooth-on-tooth from switching alone.
- Update's out-of-step repair (J11, J26) is needed only where a mode's own positions have gone out of step.

### C. A put's reach

Item B answers it: a `Transform2` put on a fresh handle holds **in the active configuration only**. F put +10° in X
left Y's F at its own 20°. So the app's per-mode placement (§1.8 step 3, `place_component` with the mode shown) is
per mode, as the plan needs. And restoring the built turn in every mode means a put in each mode, not one put.

## SolidWorks 2024, 2026-11-14: the spike and the follow-up again

Both probes were rerun on SolidWorks 2024 (32.5.0), each in a session started fresh for it, from the same snapshots
as on 2026 (64f4620 with the probes as of 00b03e5, and ed81031 for the follow-up's rerun). The results are
`probe/results/sw2024/w8-spike-20261114-232510.{txt,json}` and `probe/results/sw2024/w8-followup-20261114-233330.{txt,json}`.

**One difference, the collinear spline's Flip.**

| | 2026 | 2024 |
|---|---|---|
| Spline S–A, Flip False: Reverse; drive A, S, D | True; +30, +30, 0 | **False; +30, −30, 0** |
| Spline S–A, Flip True: Reverse; drive A, S, D | False; +30, −30, 0 | **True; +30, +30, 0** |
| The Flip that turns S with A | False | **True** |
| The read-back (W5's rule and H) names the right one | yes | yes |
| Coupling S–D: Flip False reads and drives right | yes | yes |

- On 2024 both entities read the same point, z = 9.4999 mm on each. On 2026 they read 9.4382 and 9.4296 mm.
- As with the toothed rings in W5, the two versions give the same collinear mate opposite senses, and only the
  read-back tells which.
- Nothing moved on make, S stayed under-defined, and every AddMate5 returned 1.
- For the plan: a SPLINE and a COUPLE must be settled by the read-back (W5's `_settle_sense`), as §1.7 already says.
  No static Flip is right on both versions.

**Everything else reads the same, number for number:**

- **The slide under the spline:** +10.0 mm, relative turn 0.0°, no error, and the drive 1 : 1.
- **The coupling's drive:** A, S and D each +30°.
- **Held handles go stale after `AddConfiguration2` and `ShowConfiguration2`.** They answer `Transform2` None and
  `IsFixed` False. Fresh `GetComponentByName` handles answer correctly: the layout's `IsFixed` reads True in X and
  Y, `GetModelDoc2` answers, and `Name2` reads right. Held handles stay good across `DeleteConfiguration2`.
- **`SetSuppression2` straight after `AddConfiguration2`:** the first call raised 0x80010105 yet took effect; the
  second returned False and did nothing. After a rebuild, every call returned True.
- **A mate made while Y was active** came out suppressed in Default and on in X and Y.
- **The second slide's D1 link by `IEquationMgr.Add2`** returned −1 with several configurations present.
- **The flags** read back the same in every configuration, unshown and shown, after the delete and after reopening.
- **`ShowConfiguration2` X → Y → X:** True each time, no dialog; S at 10, 30, 10; D turns with A in X and stands in
  Y. When already active it returns False.
- **The coupling turned on at an angle:** D put +5° in Y, and showing X found D back at its angle from before
  (relative −6.0°), with no error.
- **The template's configuration deleted:** True, names `["X", "Y"]`.
- **Save, reopen and close:** the file reopens in X with every document unmodified, and the reads mark nothing. A
  show marks the assembly and no part. Closing it unsaved after a switch asks nothing (CloseDoc, 0.18 s).

**The follow-up, on 2024:**

- **A: a slide's distance per configuration.** `SetSystemValue3(…, 3, ["Y"])` returned 0. `GetSystemValue3(3,
  [Default, X, Y])` read 10, 10, 30, and later 10, 10, 35 after Y was set from X. Before any per-configuration set
  it read 0 for the configurations not active, as on 2026. `SystemValue` read 30 in X here too.
- S stood at 10 / 30 / 10 on the shows, and at 35 in Y after the change made from X. After save and reopen it stood
  at 10, 35, 10, with no error and no dialog. The same as 2026.
- **B and C: positions per configuration.** The same as 2026:
  - F (no gear mate), put +20° in Y: 0 in X, 20 in Y again.
  - F put +10° in X: Y's F stayed 20, X's F read 10.
  - D, put +5° in Y with its coupling off there: 0 in X, 5 in Y again.
  - All of it held through save and reopen.
- **So on 2024 too, SolidWorks keeps each component's place per configuration, and a put holds in the active
  configuration only.** That contradicts GOTCHAS §83 and assemblies/07 for this case, a freedom the mates leave
  open, on both versions. The macro database's observation was of a free mechanism, whose positions may have been
  carried by a different solve; this run does not reproduce that case.
