# F1 review: packages A, B and C as built

An independent review of stage F1's three packages on branch \`printed\`, \`git diff 792d026..4e4b9eb\` (F1-0 and its
follow-up were reviewed in \`F1-0-REVIEW.md\`). Held to \`docs/PLAN-PRINTED.md\` §1, §2 and §6 with its *Changes after*
sections, the three checks in \`docs/PLAN-PRINTED-REVIEW.md\`, and \`F1-INTERFACES.md\`; the hand-back notes were read
last and checked against the code. No SolidWorks, no Excel. No code was changed. Everything flipped or rebuilt ran in
scratch copies (\`git archive\`) under the session's scratchpad, since deleted.

**Verdict.** F1 is fit to close on Linux. Every figure the plan gives comes out of the code, and my own
calculation agrees with it. Twenty deliberate breaks (mutations) were each caught by the suite. A machined record is
still W9's byte for byte: I rebuilt RangeBox with W9's own code at \`f3c4873\` and with F1's code, and both give B's
fixture's text but for the schema number and a digest that changes on every run. There is no must-fix for closing on
Linux. Three things need a ruling before the stage is called done:

- §2.6's span over k teeth is not built;
- B changed what a machined planetary gearbox's *Build again…* says (a W9d fix, words only);
- the rule's own pins miss seven kinds of machined leak, which only the packages' own test files catch.

The SolidWorks part of *Done when* is not done (it was never Linux work).

**Suite** at \`4e4b9eb\`, with \`PYTHONPATH=src\` checked to import this worktree's \`src\`: **4669 passed, 1 skipped,
1 failed**. The failure is the known Tk font test
(\`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left\`).

## 1. The plan's §2 against what was built

| § | What the plan asks | Built | Where |
|---|---|---|---|
| 2.1 | the IIF in the five writers and four derives; the card's third state; K11's words | yes (the IIF is F1-0's; the card, Derived row and K11 are C's and B's) | \`ui_text._backlash_note\`, \`_gear_worked\`, \`swbuild._printed_default\` |
| 2.1 | the bevel's toe figure on the card | yes, in the worked line (*0.211 at the toe* for a 20 / 40 at module 1.5, face 10) | \`ui_text.py\` \`_gear_worked\` |
| 2.2 | tip after backlash under one nozzle line (spur, helical, ring, bevel toe), module under 2.5 nozzles, rim under 3 nozzles, helix over 45°, ring fillet, radial clearance per pair | yes, all, printed only | \`spur.py:991-1037\`, \`internal.py:592-603\`, \`helical.py:448\`, \`bevel.py:604-636\`, \`pair.py:1198-1267\`, \`checks.py:508-541\`, \`:678-714\` |
| 2.3 | the single gear's printed undercut sentence; no pair interference check; W7's sentence untouched | yes | \`spur.py:951-957\`; B tests RangeBox, planetary_4to1 and Risky_Placements carry the same gearbox warnings printed and machined |
| 2.4 | nothing new | nothing new | |
| 2.5 | printed tip and clearance in \`_shifted\`, \`shift_for_centre\` and \`fixes.shift_fix\`; Solve keywords, ranking, mark; no pointed row | yes | \`pair.py:440-458\` (\`_shift_refusal\`), \`:805-858\`, \`fixes.py:174-180\` |
| 2.6 | the **span over k teeth** on a printed spur or helical gear's Derived panel | **not built** | below |
| 2.7 | the pins hold at every commit | yes; one placeholder test deleted by ruling (§2 below) | \`tests/test_printed_rule.py\` |

**§2.8, *Done when*, item by item.**

- §2.7 holds: **yes.**
- A printed spur, helical, herringbone, ring, bevel gear, sleeve, dog and hub each derive, check and plan: **yes**
  (\`test_printed_gears.py::test_every_kind_derives_checks_and_plans_printed\`, eight kinds).
- A workbook built before this plan opens Machined and unchanged, and after Printed is typed Update carries it against
  the fake: **yes** (B; I checked the fixture's provenance myself, §4 below).
- The boards in \`design/\` show the Process row, the Workbook panel's Process line and one printed warning: **yes**,
  in the \`.dc.html\` boards. The PNG renders were not redone; they have been stale since W9a.
- UI-DESIGN, the README and the backlash hints say what Printed does: **yes.**
- **On SolidWorks 2026**: one printed spur gear, one printed pair, and Printed typed on a copy of W9a's
  \`setup.master\` with one Update. **Not done**; it is the coordinator's SolidWorks run.
- **The same three on 2024**: not done.
- This review.

**The tests F1 owes** (§2.8) are all present, with three gaps:

1. a reader of sidecar 2 refusing a printed \`.gear.json\` (F1-0's should-fix 4, still open, and in F1-0's file);
2. a printed *crossed* Solve has no test, though it runs and marks by each gear's tip;
3. no test holds a machined gearbox's or form's pair below module 0.75 in \`test_printed_rule\` (§2 below).

**§2.6, the span over k teeth.** It is the base tangent length: what calipers read across k teeth of a spur or
helical gear, for the gear as drawn with its backlash. For a spur gear it is

    W = m cos α [π (k − ½) + z inv α] + 2 x m sin α − j cos α,   k = round(z α / 180° + ½)

where the last term is the tooth thinned by the backlash j at the pitch circle. A helical gear uses the normal module
and α_n, with z inv α_t in the bracket and k from the virtual tooth count; calipers can then only read it if the face
is wider than W sin β_b.

- For a printed module 1.5 gear of 20 teeth: k = 3, W = 11.209 mm (11.491 without backlash). A print that measures
  11.409 adds 0.1 mm a flank.

To build it would take:

- a pure function in \`gears/spur.py\` and \`helical.py\` (A's files);
- a row in \`ui_text.derived_rows\` for a printed spur or helical gear (C's);
- a check that the caliper's contact diameter, √(d_b² + W²), lies on the drawn involute: above the flank start (§2.4's
  undrawn flank) and below the tip. Otherwise k is moved, or no span is given;
- for recipe B (arc flanks), either no span or one measured off the drawn outline, since the formula is the
  involute's;
- tests.

That is a small package, about one agent run.

F1 is complete without it in everything F1 itself uses. Nothing in F1 reads it, and no package list, *Done when* or
test list in §2.8 holds it. Its only consumer is §3.2 step 1, F2's *the user prints and measures*. **Recommendation:
move it to F2, as F2's first step, on Linux and before any gear is printed for measuring**, and add it to F2's *Done
when*. If it is not moved explicitly, it will be lost: no list now names it.

## 2. The rule: machined stays W9's

**\`tests/test_printed_rule.py\`.** Between \`792d026\` and \`4e4b9eb\` it changed in one commit (\`bbd08f2\`), which
deletes exactly the seven lines of
\`test_the_pair_stubs_answer_as_the_machined_maths_until_package_a_fills_them\` and nothing else. **No other test line
in \`tests/\` was deleted or changed** (the diff's 7 deletions are those seven); every other test edit is an addition.
Each package touched only its own files, in \`src\` and in \`tests\`; I checked every commit's file list.

**Records.** I rebuilt RangeBox with W9a's user work on the fake twice: with W9's code at \`f3c4873\`, and with F1's.
Each was serialised and compared with B's committed fixture. All three agree byte for byte except:

- the link schema number;
- the \`digest\`, which differs between any two runs, and between the two runs of the same code.

So B's fixture is what W9 wrote, and F1's machined record is W9's.

**Twenty mutations**, each in its own scratch copy, each run against the whole suite with \`-x\`, then against
\`test_printed_rule.py\` alone:

| Mutation | Suite | The rule's pins alone |
|---|---|---|
| M1 \`checks._printed\` always true (a machined gearbox judged as printed) | caught (\`test_printed_workbook\`) | **missed** |
| M2 \`mesh_warnings\` takes its printed branch for machined pairs | caught (\`test_printed_gears\`) | **missed** |
| M3 \`solve\` printed for a machined pair | caught | caught (Solve rows) |
| M4 the 45° helix check for machined gears | caught (\`test_printed_gears\`) | **missed** |
| M6 the strip's \`_gear_spec\` always machined | caught (\`test_printed_window\`) | not the rule's job |
| M7 / M8 the window's blank always printed / always machined | caught | M7 missed, M8 not the rule's job |
| M9 \`spec_values\` drops the Box's process | caught | caught |
| M10 \`_changed_columns\` reads a missing process as printed | caught (\`test_printed_workbook\`) | **missed** |
| M11 \`fixes.shift_fix\` tests every pair as printed | caught (\`test_printed_gears\`) | **missed** |
| M13 K11's printed words for any equation | caught | caught |
| M14 the printed undercut sentence for machined gears | caught | caught |
| M17 \`assess\` resolves a blank printed whatever the keyword | caught | caught |
| M18, M19, M20, M21, M22 (the form's load and start, the foreign record, \`template\`, \`_read_box\` resolving) | caught | not the rule's job |
| M23 the printed tip ignoring backlash | caught | not the rule's job |
| M24 Gleason's clearance said for machined bevel pairs in a workbook | caught (\`test_printed_workbook\`) | **missed** |

**Every mutation is caught by the suite.** But seven ways of telling a machined gear or gearbox something new are
held only in package A's and B's own test files: M1, M2, M4, M7, M10, M11 and M24. The rule's pins miss them for three
reasons:

- the W8 fixtures and pinned pairs sit at module 0.75 or above, where an unshifted clearance is already 0.3 mm;
- no pinned gear has a helix over 45°;
- no pinned gearbox has a bevel mesh under module 1.6, or a shift fix that the printed test would refuse.

This is the same gap F1-0's review raised for K11 and the card. F2 to F4 will edit these same files, so **before F2
opens \`pair.py\`, \`checks.py\`, \`helical.py\` or \`fixes.py\` again, add machined pins to \`test_printed_rule.py\`**:

- an outside, ring and bevel pair at module 0.5, on the form (\`mesh_warnings\`) and in a workbook (\`checks\`);
- a helical gear at 50°;
- a machined shift fix at a centre distance the printed test refuses (module 1, 20 / 40 at 30.2 mm);
- \`_changed_columns\` on a machined record against a machined spec.

(Should-fix S1.)

**A machined sentence that did move.** B's choice 9 changes \`update._why_part_new\` (\`update.py:3244-3250\`): a
planet copy made new now finds its row's job. So a **machined** planetary gearbox's *Build again…* now names a planet
copy's changed column (*its Face width changed*) where W9 said *its values changed*. The change is true and better,
and it is words only. But it is a change to what a machined gearbox is told, and no pin noticed it. The rule
(*"is told exactly what it is told today"*) needs the coordinator to rule it in as a W9d fix. **Recommend: keep it,
and land the same fix on \`w9d\`**, so the branches do not diverge on W9's own behaviour (ruling R-B9).

**Silent machined when the user asked for printed, or printed leaking into machined.** I found no path that builds
silently against the user's choice:

- **The strip.** The form starts Printed. \`_gear_spec\` passes the row into both gears, and Solve's \`apply\` keeps it.
  A loaded record sets the row, which shows it.
- **The workbook.** \`WorkbookWindow._assess\` is the only user-facing caller of \`assess\` (\`workbook_gui.py:831\`).
  Every build, Update and fix plan goes through its resolved spec. The raw read (\`self.reading.spec\`) feeds only
  the Process line, the drawing before the first assessment, and Export, which writes fix cells and never the Box.
- **A bad Process word or Nozzle** is an error that refuses Build. It is not built quietly as machined.

The leaks the other way are small:

- **Nozzle is checked even on a Machined Box** (B's choice 2, \`model.py:402-405\`). A machined gearbox with a stray
  \`0\` in Nozzle is refused Build, by a setting it does not use. The strip does not read a machined gear's Nozzle
  (F1-0's ruling 3).
- **A record that cannot be read, or is newer than this app**, leaves \`_blank_process\` with no record
  (\`workbook_gui.py:841-847\`). A machined gearbox with a blank Process then shows *Printed, 0.4 mm nozzle*, and every
  gear reads as changing. Nothing is built, since both buttons wait and the footer says why, but the Process line
  states something untrue there (S5).

## 3. Package A's maths, by my own calculation

I computed each figure independently, from the involute and internal-gear tooth-thickness formulas, and compared it
with the app's derive and with A's pair functions.

- **Backlash and flanks.** The printed blank is min(0.3, 0.3 m) a gear. It thins the tooth at the pitch circle by j
  and takes (j/2) cos α off each flank square to it: **0.141 mm** at 20° from module 1 up, and 0.141 × m below
  module 1. In a helical gear the transverse thinning is j / cos β (\`helical.py:354\`).
- **Spur tips after backlash** (s_a = d_a (s/d + inv α − inv α_a), s = πm/2 + 2xm tan α − j):

  | Module | Teeth | Tip (mm) |
  |---|---|---|
  | 1 | 12 / 20 / 25 / 26 / 40 | 0.271 / 0.365 / 0.396 / 0.401 / 0.446 |
  | 1.25 | 10 / 11 | 0.375 / 0.402 |
  | 1.5 | 6 / 7 / 8 / 12 / 20 | 0.305 / 0.379 / 0.437 / 0.581 / 0.712 |

  These are the plan's §2.2 figures exactly. \`spur.profile\` and \`pair.printed_tip_thickness\` agree to 1e-4.
  \`printed_tip_thickness\` = \`tip_thickness\` − (d_a/d) j / cos β is right: thinning at the pitch circle carries to
  the tip scaled by the radius.
- **Helical tips**, transverse section (20 teeth at 20°, module 1: 0.422; at 30°, module 1.5: 0.936): mine, the
  derive's and A's agree.
- **Ring tips** (s = d_a (s/d − inv α + inv α_a), d_a = d − 2m): module 0.5, 40 teeth 0.341; module 1, 54 teeth
  0.638; module 1.25, 55 teeth 0.867. All agree. At module 0.5, 20 teeth the ring's tip circle is inside its base
  circle, so there is no involute at the tip; the app's 0.438 is its drawn tip, and A's advice for a ring (*a larger
  module* only, since more teeth thin a ring's tip) holds.
- **Bevel toe.** For a 20 / 40 pair at module 1.5, face 10: R = 33.54, (R − b)/R = **0.702** (§2.1's 0.70). The heel
  tip is 0.529, so the toe is **0.371**, under 0.4, and it warns. The toe backlash is 0.211. Scaling the heel section
  by the toe scale is right: the build scales the whole heel section toward the apex.
- **Clearances.** \`tooth_depth\` is the user's IIF: 2.4 m up to module 1.25, 2.25 m above it. An unshifted outside
  pair's and a ring pair's tip-to-root gaps are both h − 2m:

  | Module | 0.5 | 0.75 | 1 | 1.25 | 1.3 | 1.5 | 2 |
  |---|---|---|---|---|---|---|---|
  | Gap (mm) | 0.2 | 0.3 | 0.4 | 0.5 | 0.325 | 0.375 | 0.5 |

  Module 0.75 computes as 0.2999999999999998 and passes within the tolerance. A bevel pair's is
  min(ded₁ − add₂, ded₂ − add₁) = 0.188 m (0.282 at module 1.5). It is under 0.3 mm below module 1.596.
- **Who is right on the ring gaps: A.** The plan's *each 0.4 × module unshifted* holds only up to module 1.25. Above
  it the depth is 2.25 m and each gap is 0.25 m, exactly as for an outside pair (0.375 mm at module 1.5). It changes
  no warning: 0.25 m is above 0.3 mm from module 1.2, so every module above 1.25 passes either way. The code follows
  the drawn depth, which is what the parts have. The plan's sentence should be corrected when §2.2 is next revised.
- **A shifted pinion in a ring.** \`ring_tip_clearance\` puts it at the working centre from the formula
  \`checks.internal_working_centre\` uses, inv α_w = inv α_t + 2 tan α_n (x₂ − x₁)/(z₂ − z₁). I checked the sign
  convention against that function. It is not checked against a drawn outline.
- **Solve, printed.**
  - Rows are marked *thin for a 0.4 nozzle* when the module is under 2.5 nozzle widths or a tip after backlash is
    under one line. A row whose tip is at or below 0 is dropped.
  - Marked rows rank after \`not standard\` and before \`undercut\`. \`Candidate.mark\` is \`repr=False\` and always \`""\`
    when machined, so a machined Solve's repr and order are unchanged; the pins hold them.
  - At 30 mm and ratio 2: the printed first row is module 1.25, 17 / 31, and the module 1 rows (20 / 40: tip 0.365)
    are marked and last. Machined, 20 / 40 at module 1 is first.
  - A printed crossed Solve runs and marks by each gear's tip, but nothing tests it (S6). It offers helix angles of
    50° to 61°, which the printed 45° check then warns of on the form; the plan's mark covers only module and tip.
  - Solve does not mark a printed bevel row under module 1.6, which the form then warns of (clearance 0.282 at
    module 1.5). That is consistent with §2.5's list; a caveat, not a fault.
- **\`shift_for_centre(printed=True)\`.**
  - Module 1, 20 / 40, moved to 30.2 mm: machined gives x = 0.102 each. Printed refuses, since the 20-tooth tip after
    backlash is already 0.365 unshifted.
  - At 29.8 mm both give −0.097 each. A negative shift thickens the tip at its smaller circle, to 0.4004, so printed
    accepts.
  - The clearance floor is max(0.1 m, 0.3 mm). \`fixes.shift_fix\` tests a pair as printed when either derived gear
    has a nozzle.
  - The refusal sentences never reach the user: \`shift_fix\` catches them.

## 4. Package B

**Process and Nozzle through read, check, write and template.**

- \`_read_box\` keeps a blank cell and a missing row both as \`""\`. It reads the word in any case and keeps it lower
  case. Any other word is *Box!B9: Process is Printed or Machined (got 'wood').*, kept as typed so the window shows
  it.
- Nozzle goes through the numeric check, then *Nozzle must be more than zero (got '0').*
- \`process_cell\` is \`at("process")\` only when the row exists. \`spec_values\` passes only checked values (ruling 3).
- \`to_sheets\` (F1-0's) writes the word as held.
- \`template\` writes \`printed\` and 0.4. *New workbook…*'s cell reads \`printed\` in lower case beside a note that says
  *Printed or Machined*, as the app's other words are written lower case: cosmetic.
- The \`float(text)\` at \`model.py:404\` cannot raise: it runs only when the numeric check added no diagnostic, and that
  check returns \`number_text\` of a value that parsed.

**Schemas and an older app.**

- Link 11 whatever the parts, and sidecar 3 only for a printed part (B's tests at 11 and 3, and at 1 or 2 for
  machined).
- A W9-era reader refuses 11 and leaves the file alone (F1-0's tests). A reader of sidecar 2 refusing 3 is still
  untested (F1-0's should-fix 4).
- A W9-era app reading an F1 workbook skips the two rows and builds machined: accepted by the plan.

**D11 (B) on a record W9 wrote: the test is real.** I regenerated the record with W9's code at \`f3c4873\`, and
separately with F1's code. Both equal the fixture's text but for the per-run digest and the schema number, so the
fixture is genuinely W9's output (fake paths only, \`C:\\Out\\\`, \`C:\\B\\\`; no personal data). On it:

- the blank reads Machined, Update and Build again… have nothing to do, W9d's columns find nothing, and the footer is
  W9's word for word;
- with Printed typed, each part changes in \`Backlash\` alone, in place, keeping its file.

*Nothing written* is shown only as a planning call can show it (B says so): the record is re-serialised and compared,
and no writer is called.

**What Update SolidWorks writes when Printed is typed on an existing gearbox.**

- One global a part: \`"Backlash"\`, from \`0.3 * "Module"\` to \`IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )\`.
- No structural change, no new revision, no put. Each file keeps its name, with no \`_P\` (D10).
- The record goes to 11, and each changed part's \`.gear.json\` to 3.

W9a's rules hold on the fake, end to end with W9a's user work: the Lock3 mate, two user components, the Keyway and
the Groove are kept; a second press finds nothing to do; and K11 then refuses a Backlash the user typed in SolidWorks,
in its printed words. A typed Backlash is not written.

**K11's wording.**

- The value: *0.3 (from its blank cell, the printed default: 0.3 mm, or 0.3 × Module below module 1)*.
- The set-back: *set it back to the equation IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )*.

Both are plain, and both are true at modules 1.5 and 0.5 (0.15). The printed default is recognised by comparing the
planned global's words, not SolidWorks', so how SolidWorks stores the IIF cannot change which words are chosen. The
machined K11 sentences are pinned and held (M13 was caught by the rule).

**What Build again… says and carries after Printed is typed.**

- Every part is made new as a \`_P\` part, and each body's reason is *its Process changed*.
- The user's components are carried onto the new parts. Features and face mates it cannot make again are named, as
  W9d names them.
- B found that a planet copy made new is handed no app feature names (\`update.carry_for\`). I traced it. A user's
  mate on a planet copy's Gear Axis or app feature is then **named** as gone (\`swbuild.py:7512-7520\`), not dropped
  silently, but it could have been carried.
- This is W9d's bug, and typing Printed on any planetary gearbox meets it for every planet. **It belongs on \`w9d\`.**

**What would first meet SolidWorks, and whether any of it is new.**

- An Update setting an existing global's text to an IIF.
- A printed part saved under a \`_P\` name.
- A printed part's IIF read back by K11's comparison.

None is a new kind of call:

- Update writes every global through the same value path.
- The IIF has the shape of the depth IIF (\`IIF ( "Module" <= 1.25 , … )\`, \`spur.py:845\`), which every build writes
  and K11 already compares on SolidWorks, and P1 probed \`<=\` in IIF.
- File names are the existing SaveAs.

The things to watch on the run:

- that the live text read back after the Update squashes equal to the planned, so K11 does not refuse the second
  press;
- that the 0.035 mm a flank moves re-solves the user's mates on tooth faces, as §6 expects.

## 5. Package C

**The form's rows.** Process (*Printed* · *Machined*) is under Make and starts Printed on every launch. Nozzle
(placeholder *0.4*, hint *the printer's line width*) shows only while Printed. Each gear's Backlash placeholder and
hint follow the row:

- machined: *0.3 × module*, *ISO: 0.02–0.05 × m*, as before;
- printed: *0.3 · printed*, *0.3 × m below m1*.

The rest of the readouts:

- **The Derived Backlash row** reads *0.3 · printed default* (*0.15 · printed default* at module 0.5).
- **The card's printed copy** is the machined first sentence, then *Printed, blank uses 0.3 mm, or 0.3 × module below
  module 1: room for walls printed a little fat, and a starting value until your own prints are measured. A slicer's
  X-Y compensation does the same job, so use one or the other, not both.* It is true in each state that shows it,
  including a typed Backlash on a printed gear, since it says what a blank uses.
- **Solve's mark** is in the error column and at the end of the chosen card.

**The Workbook window's Process line** (\`ui_text.workbook_process_line\`) is true in each of its six states:

| State | Line |
|---|---|
| Printed, typed or a blank resolved so | *Printed, 0.4 mm nozzle* |
| A blank resolved as built | *Machined, as built: type Printed beside Process on the Box sheet to print it* |
| The same with no Process row | that, then * (add a row labelled Process)* |
| Machined typed | *Machined, as the Box sheet says: type Printed beside Process to print it* |
| A word that is neither | *Process does not read: the Checks panel says why* |
| Printed with a bad Nozzle | *Printed; its Nozzle does not read: the Checks panel says why* |

There is one state where the line is untrue: a record that cannot be read or is newer, said in §2 (S5).

\`_blank_process\` reads the record without moving it, settles it as the window does, and drops another workbook's
record. Mutations M7, M8 and M20 were each caught by \`test_printed_window\`.

**The sentence after Update about file names keeping no _P** (\`ui_text._process_names_kept\`, \`ui_text.py:1959-1991\`).
It reads plainly, singular and plural, both ways. It is **not true in one state**. Its docstring says *when this
Update changed the Process*, but its test is \`spec.is_printed() != named\` (\`:1971\`), which compares the part's
Process now with its file name, not with what it was built as. So a part made printed by an earlier Update is told
again on every later Update that changes it. I ran it: a part at \`Gear_m1.5_N17\`, already printed, whose teeth go
to 18 is told *Gear_m1.5_N17, now printed, keeps its file name, without the _P …*, although this Update did not
change its Process. The fix is to compare with the record entry's process (S2).

**Pinned on exact strings.** Every new sentence of A, B and C appears verbatim in a test:

- the tip, ring, toe, module, rim, helix, fillet, undercut and clearance sentences, and Solve's mark, in
  \`test_printed_gears\`;
- the Box's word error, the Meshes clearance and K11, in \`test_printed_workbook\` and \`test_swbuild_user_work\`;
- the Process line's states, the card, the rows and the name sentence, in \`test_ui_text\` and \`test_printed_window\`.

\`test_workbook_window.py\` was not edited: no test there reads the whole Box panel, so no pinned text moved, against
the plan's expectation, which was harmless.

## 6. The seams

- **\`Candidate.mark\`** (A to C). It is \`field(default="", repr=False)\`. It is still part of \`==\`, which is harmless,
  since a machined row's is always \`""\`. C shows it in \`candidate_row\` and the chosen card. It is sound.
- **\`shift_for_centre\`'s \`nozzle\` keyword.** It was not in F1-INTERFACES (only \`printed=\` was), and A added it
  additively. Its only caller is \`fixes.shift_fix\`, which passes the derived gear's nozzle. It is sound.
  F1-INTERFACES §4 should name it.
- **\`Box.process_cell\`.** B sets it from \`rows\`, and C reads it off the raw read. It is outside \`==\` and never
  written. It is sound.
- **The clearance sentence.** Form and workbook both call \`pair.printed_clearance_sentence\` (\`d54d237\`), so the words
  cannot drift. The **bevel figure** comes from two sources: the form uses the derived gears'
  \`dedendum − addendum\`, the workbook \`(bevel.WHOLE_DEPTH − WORKING_DEPTH) × module\` (\`checks.py:681\`). They agree
  today (0.282 at module 1.5). One shared function in \`pair.py\` would keep them so (S4, low).
- **Crossed pairs.** The workbook judges a printed crossed pair as an unshifted outside pair (h − 2m_n). The form
  does not: \`mesh_warnings\` returns nothing for one (\`pair.py:1243\`), and the strip skips crossed pairs
  (\`gui.py:1354\`). The workbook's figure is right: at the common perpendicular each tip stands h − 2m_n from the other
  root, whatever the helix angles. The mismatch shows only where h − 2m_n < 0.3 mm, that is below module 0.75. At a
  0.4 mm nozzle the module floor (1.0) already warns there, so it is visible only with a nozzle under 0.3 mm.
  **Recommend: the form says it too** (A: a crossed branch in \`mesh_warnings\` giving the unshifted figure; C: drop
  \`not self._crossed()\` for a printed pair). Low priority; or accept and record it.
- **The form's \`mesh_warnings\` call** (\`gui.py:1354-1356\`). It is unchanged for machined pairs, so M2 caught only
  what A's function does. For printed pairs it is widened to rings and bevels. \`pair\` is not None only when both
  gears derive, so the \`None\` case cannot reach A's function.

## 7. Recommended rulings

**A's thirteen.**

| | Choice | Ruling |
|---|---|---|
| 1 | printed if either gear is | accept |
| 2 | mark after \`not standard\`, before \`undercut\` | accept |
| 3 | Solve uses the printed default, not a typed backlash | accept |
| 4 | bevel clearance at the heel | accept as the plan's figure; record that the toe's is 0.70 of it |
| 5 | bevel module check on the heel module | accept; the toe tip check covers the small end |
| 6 | \`nozzle\` unused in \`printed_tip_thickness\` | accept |
| 7 | one rim sentence; no nozzle rim check on a ring | accept |
| 8 | the tip advice per kind | accept; verified, a ring's tip thins with more teeth |
| 9 | *less profile shift* only when shifted | accept |
| 10 | the ring fillet sentence for sleeves and internal bevels | accept |
| 11 | no crossed clearance on the form | say it on the form (low); else accept and record |
| 12 | Solve's default bevel face | accept |
| 13 | pointed rows dropped only when printed | accept |

**B's ten** (the task said four; the note lists ten).

| | Choice | Ruling |
|---|---|---|
| 1 | a bad word goes into the gears as the spec's blank | accept |
| 2 | Nozzle checked whatever the Process | accept for F1; revisit if a user meets it |
| 3 | clearance advice split | accept |
| 4 | crossed pairs checked | accept (correct figure) |
| 5 | bevel figure from constants | accept, with S4 |
| 6 | clearance before the centre checks | accept |
| 7 | \`template\` writes 0.4 | accept |
| 8 | Process last in \`_SPEC_COLUMNS\` | accept |
| 9 | planet copy reason (R-B9) | keep, rule it in as the one machined change, and land it on \`w9d\` |
| 10 | the fixture committed | accept; verified W9's and clean |

Not fixed by B: the planet copies' feature names in \`carry_for\` go to \`w9d\`'s owners. C's name note is answered by
\`bc6ec8f\`, apart from S2.

**C's twelve.**

| | Choice | Ruling |
|---|---|---|
| 1 | typed-Machined and unread lines | accept |
| 2 | placeholder and hints | accept |
| 3 | *X-Y compensation* | accept |
| 4 | Derived row without mm | accept |
| 5 | bevel toe in the worked line | accept |
| 6 | Printed each launch; hidden nozzle kept | accept |
| 7 | no card for Process | accept |
| 8 | Solve's mark shown | accept |
| 9 | the name sentence | accept, with S2 |
| 10 | span over k teeth | move to F2's first step (§1) |
| 11 | readout without Process | accept |
| 12 | the crossed mismatch | as A11 |

## 8. Must-fix and should-fix

**Must-fix for closing F1 on Linux: none.** Before F1 is called done, the coordinator must:

- **R-2.6**: rule the span over k teeth (§1). The recommendation is to move it into F2's plan explicitly.
- **R-B9**: rule the machined *Build again…* wording change (\`workbook/update.py:3244-3250\`) in as a W9d fix, and have
  it landed on \`w9d\`.
- Run the SolidWorks part of *Done when*, on 2026 and then 2024.

**Should-fix:**

- **S1.** \`tests/test_printed_rule.py\`: pin machined behaviour that today only A's and B's own tests hold (M1, M2,
  M4, M10, M11, M24 in §2). Do it before F2 edits \`pair.py\`, \`checks.py\`, \`helical.py\` or \`fixes.py\`.
- **S2.** \`src/gear_generator/ui_text.py:1971\` (\`_process_names_kept\`): compare the part's Process with the one on
  record, not with its file name. Today the sentence repeats on every later Update of a part an earlier Update made
  printed.
- **S3.** \`docs/PLAN-PRINTED.md\` §2.2: correct the ring pair's gaps to *h − 2m: 0.4 × module up to module 1.25, 0.25
  above*. Name \`shift_for_centre\`'s \`nozzle\` keyword in \`F1-INTERFACES.md\` §4.
- **S4.** \`src/gear_generator/workbook/checks.py:681\`: take the bevel pair's clearance from one function shared with
  \`pair._printed_mesh_warnings\` (\`pair.py:1235-1238\`). Low.
- **S5.** \`src/gear_generator/workbook_gui.py:841-847\`: when the record cannot be read or is newer, the Process line
  should not say *Printed* for a gearbox it cannot judge. Say the record is unreadable, or resolve the line only once
  a record is read. Low; nothing is built in that state.
- **S6.** \`tests/test_printed_gears.py\`: a printed crossed Solve (marks by each gear's own helix).
- **S7.** \`src/gear_generator/gears/pair.py:825\`: a printed bevel row whose gear does not derive is returned unmarked
  and offered. Consider dropping it, as a pointed row is. Low; it builds no worse than machined.
- **S8.** A crossed pair's clearance on the form (A11 and C12), low.
- **Carried from F1-0's review:** \`tests/test_store.py\` still lacks a reader of sidecar 2 refusing a printed
  \`.gear.json\` (its should-fix 4).
- **Not F1's:** \`update.carry_for\` hands a planet copy made new no feature names (B's find; traced in §4), for
  \`w9d\`.
