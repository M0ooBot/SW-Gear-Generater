# Review of stage F2 as built (packages A, B and C)

Read at `e449465` on `printed`: package A `b09a036`, package B `2d32c03`, package C `7d92748`, `8328263`, `19cff09`, against
PLAN-PRINTED §3.0 to §3.4 with *Changes before F2*, *Changes after F2's review* and the later sections,
`F2-INTERFACES.md`, `F2-0.md` with the coordinator's rulings, `F2-PROBES.md` and `F2-PROBES-REVIEW.md` (which landed while this
was written and is not repeated here except where a point bears on the packages). The packages' notes were read last
and held to the code. No code was changed. Line numbers are as of `e449465`.

**Verdict.** F2 as built does what §3.0 and §3.1 ask, against the fake, and is **fit for its SolidWorks demonstration
once the findings commit sets the six findings** (with `PART_WINDOW_READ` as the word `"Visible"`, F2-PROBES-REVIEW's must-fix).
The span maths is right: all ten of the plan's rows recompute to 1e-4 mm from the closed form alone, with the textbook
k. The export job cannot save, close or change anything of the user's in any path I could construct. Two sentences
are untrue in states the user can reach (M1, M2 below); neither writes anything, and both are small. Nothing machined
or pinned of W9 and F1 moved.

Suite, `PYTHONPATH=src` (the import path checked: `/home/m0obot/SW-Gear-Generater-printed/src/gear_generator/__init__.py`),
with the known Tk font test deselected: **5087 passed, 1 skipped, 1 deselected** in 147 s. The deselected one is
`test_workbook_window.py::test_a_second_workbooks_r2_parts_beside_long_ids_are_shortened_to_the_room_left`.

## 1. Against §3.0, §3.1 and Done when

Built and held by tests:

- §3.0: the span row after *Tooth at pitch* on a printed involute external spur, helical or herringbone gear (and a dog
  or hub, each a `SpurDerived`); none on a machined gear, a ring, a sleeve or a bevel gear; arcs, the narrow face and no
  contact each said under the rows; the Measured entry per gear, not saved; its line with the gear's own `cos α_n`, the
  floor and the line past `0.3 × module`; the span's card; the print list's span lines (machined *no span*, arcs *not one
  figure*).
- §3.1.3: Print files in the form's footer between Update values and Build and as the window's fifth button; the bar's
  line; every planning refusal of the window and the form; the job's reach table, reads, export, check and finally;
  the folder per press with its counter; `_r2` kept a part's revision; the list in UTF-8, headed *DO NOT PRINT THIS
  SET* after a stop.
- §3.1.4: the frame, the schema by prefix, solids counted as instances, the unit from the representation context (an
  inch file reads), and the size check, skipped as a fact where the plan and the rulings say.
- Done when: the interface reviewed (F2-0-REVIEW); the probe run on both versions and reviewed (F2-PROBES-REVIEW);
  Print files against the fake from both places with every refusal said, files checked, the list written and the open
  documents left as they were; the boards, UI-DESIGN and README updated.

**Not built** (each is a fact, not a fault of a package, unless said):

1. **The findings commit**: all six F2 findings are None, so every press is refused GATE_COPY. `printout.EXTENT_MEASURED`
   is False (`printout.py:116`), so the size check is skipped on every part until that commit sets it.
2. **`probe/f2_demonstration.py`** is not written, and nothing of F2 has run on SolidWorks but the probe.
3. **The user's step**: the coupons, Bambu Studio's opening of the files (U5), the measurements, and D3's number and F3's
   allowance from them.
4. **The lightweight read the interface describes** (§5.2, *How the job knows*): the job infers LIGHTWEIGHT for every
   part not found while any assembly is open, rather than reading the open assemblies' component states (B's choice 3).
5. **The boards' PNG renders** (Mac only, as since F1). The span's card borrows the Teeth diagram; it has no picture of
   its own.
6. `DOCUMENT_BY_PATH_ROUTE` stays the walk; `GetOpenDocumentByName` is built behind it, unused.
7. This review's should-fix round.

## 2. Package A: the span, by my own calculation

**Source.** The base tangent length as KHK's *Gear Technical Reference* gives it (span measurement, Tables 5.10 and
5.11, with `A_Wk = A_sn cos α_n`), in its closed form, computed in a scratch script from each row's typed numbers alone
(m_n, z, α_n, β, x, j), not from the app:

    α_t = atan(tan α_n / cos β),  sin β_b = sin β cos α_n,  d = z m_n / cos β,  r_b = d cos α_t / 2
    W_n = m_n cos α_n [(k − 0.5) π + z inv α_t] + 2 x m_n sin α_n − j cos α_n,   W_t = W_n / cos β_b
    r_c = √(r_b² + (W_n cos β_b / 2)²);  k = the k in 1 … z−1 whose r_c is nearest r + x m_n
    textbook k: z/π (tan α_M / cos² β_b − inv α_t − 2 x tan α_n / z) + 0.5,  cos α_M = d_b / (d + 2 x m_n)

| Gear | j | k (textbook) | W_n mine | plan | Δ | W_t | r_c | face needed |
|---|---|---|---|---|---|---|---|---|
| spur m 1.5, z 20, printed | 0.3 | 3 (2.72) | 11.20875 | 11.2088 | −0.00005 | | 15.169 | |
| spur m 1.5, z 20, machined | 0.45 | 3 (2.72) | 11.06780 | 11.0678 | 0.00000 | | 15.143 | |
| spur m 1, z 12 | 0.3 | 2 (1.83) | 4.31436 | 4.3144 | −0.00004 | | 6.037 | |
| spur m 2, z 30 | 0.3 | 4 (3.83) | 21.22334 | 21.2233 | +0.00004 | | 30.122 | |
| spur m 1.5, z 15, x +0.3 | 0.3 | 3 (2.62) | 11.41153 | 11.4115 | +0.00003 | | 12.013 | |
| Sun m 1.25, z 29 | 0.3 | 4 (3.72) | 13.14137 | 13.1414 | −0.00003 | | 18.255 | |
| Planet m 1.25, z 13 | 0.3 | 2 (1.94) | 5.48093 | 5.4809 | +0.00003 | | 8.112 | |
| helical m_n 2, z 20, β 15° | 0.3 | 3 (2.94) | 15.09719 | 15.0972 | −0.00001 | 15.5645 | 20.713 | 6.672 (β_b 14.076°) |
| helical m_n 1.5, z 25, β 20° | 0.3 | **4** (3.80) | 15.84379 | 15.8438 | −0.00001 | 16.7315 | 20.062 | 8.092 (18.747°) |
| helical m_n 2, z 20, β 30° | 0.3 | 4 (3.79) | 21.22548 | 21.2255 | −0.00002 | 24.0448 | 23.260 | 12.973 (28.024°) |

Every row agrees with the plan within its rounding, and the nearest-contact k is the textbook k on every row (M1's β 20°
row included). The app's own `span()`, run on specs typed as the user would, gives the same ten (the machined row by
`span_over`; `span` is "none" for it as E1 asks), the β 30° gear "narrow_face" 12.973 at the default face 10 and k 4 at
face 14, a herringbone m 2, z 20, β 15° k 3 at face 14 (half 7 ≥ 6.672) and narrow at face 13 (half 6.5), recipe B
"arcs". The helical section carries `module = m_n` and `shift = x` (`helical.py:340-354`), so A's target `r + x·section.module` is
the plan's `r + x m_n`; the transverse thinning `j / cos β` makes the app's backlash normal, so `−j cos α_n` is the right term.

**The bounds.** `contact_bounds` is §3.0's (the involute's start, 0.2 mm under the tip); `choose` takes the nearest k among
those inside, which is the plan's "next k inward or outward". A's sweep finding is plausible: a z 6, m 1.5 pinion reads k 1
inside the bounds even at x −1, and at m 1 the tip margin makes it "no_contact", as A's test holds.

**Back from a reading** (`span.measured`, `span.py:229-244`): `e = (reading − W_n)/2`, normal to the flank since W_n is
along the base-tangent normal; `j = 2 (e + 0.04)/cos α_n` is the closed form's `−j cos α_n` term solved for a flank keeping
0.04 mm. Checked: 11.291 on the coupon gives e 0.0411, j 0.1727 (the line's *0.173*; the interface's 0.172 is from e
0.041 rounded first); e 0.10 gives 0.298 (the plan's "0.3 stays"); the floor of 0.1 holds for every e under +0.0070 mm,
not only under the plan's −0.04 where the formula reaches 0, which is what "never proposes less than 0.1" means.

**The flag is where §3.0 and §3.2 part (M2).** `over_default` is `j > 0.3 × module` for this gear (`span.py:244`), as §3.0
words it. But §3.2 (and U4) put the user's decision at `j > 0.3 mm`: above that, every gear under module `j/0.3` would take
more than today's `0.3 × module`. On the m 1.5 coupon the line flags only past 0.45 mm (e > 0.171), so a printer adding
0.12 mm a flank proposes 0.34 mm, a case §3.2 says is the user's to decide, and the line says nothing. A's note says so
itself. The README's step 6 then tells the user *"If that backlash is more than 0.3 × module, the line says so, and you
decide"*, which is the wrong trigger for the coupons the README has them print (M2).

## 3. Package B: the export

**The planning refusals, in order** (`printout.py:314-437`): the gate (GATE_COPY first on every version, GATE with no
detail when none is connected, GATE by year and revision); on the form NOT_A_PART, NO_RECORD; in the window
FOREIGN_RECORD, WORKBOOK_ERROR (an error, a provisional read, fixes chosen), NO_PART (a row no part serves and no
in-place add, or a part not on disk), WORKBOOK_ERROR again (no Update plan, or one refused), UNSAVED_MARK, MISMATCHED_MARK
(the parts' marks only, never the layout's or the assembly's), CHANGES_ON_UPDATE (values, new part, an in-place add).
Each is true and the set is sufficient for "not matching the workbook" as the plan defines it; a layout- or
assembly-only change does not refuse (E3). One wording consequence is wrong (M1): a part that needs a new revision is
detailed "new part" like an in-place add, and C tells the user to press Update SolidWorks, which is never run then.

**The job's refusals, in order** (`swbuild.py:10393-10478`): the gate again, with the session against the plan's revision;
every part's way decided before anything is opened (COMPONENT_ONLY, LIGHTWEIGHT); then every part reached and read,
before any folder is made: MODIFIED (its own `GetSaveFlag` as the build document), GLOBALS_DIFFER (live against the
record's text, spaces aside, which is K11's first comparison), FEATURE_IN_ERROR (an error, not a warning); then the
folder, and each export and check, stopping at the first SOLIDWORKS_REFUSED or FILE_CHECK. Nothing is exported from a
part unsaved, in error or not its record's; a lightweight part, and any part not found while an assembly is open, is
refused, never opened beside. Each is true; the inference behind LIGHTWEIGHT errs safe (it also refuses a part simply
closed while an unrelated assembly is open), and C's *may be* makes the sentence true of both.

**The folder.** `<Output>\print\%Y-%m-%d %H.%M.%S` with " (2)" on, chosen at planning and taken again by the job if it has
come to exist; `export_step` refuses an existing path before SolidWorks is asked (`SaveAs` overwrites, q26:34);
`write_list` opens "x". Nothing can be overwritten. One gap: `_make_press_folder` uses `os.makedirs(dirname, exist_ok=True)`
(`swbuild.py:10313`), which would also make a missing Output folder; only C's checks before the press stop that (§5).

**The check.** Frame, schema by prefix (both AP203 names, AP214, AP242), instances counted by entity name (a name in a
quoted string or a comment is none), one MANIFOLD_SOLID_BREP and a CLOSED_SHELL, no OPEN_SHELL, no surface model, the
length unit through GLOBAL_UNIT_ASSIGNED_CONTEXT (so an inch file, which also carries its SI base, reads), Part 21 read as
latin-1 (any byte reads). The size check: largest vertex radius from Z against `d_a/2` and the vertices' axial extent
against the face, each to 0.01 mm, against 2026's measured 0.0012 mm over at z 20; skipped as a fact for a bevel, ring,
sleeve, dog, hub, a part holding the user's features (on record, or found live against the record's `made`), and
everything while `EXTENT_MEASURED` is False. **A herringbone is not skipped and not measured** (F2-PROBES-REVIEW): S3.

**The gate** is read at planning (`printout.gate`) and in the job before any document is touched, and refuses a session
that changed since the plan. The form plans for the snapshot's revision (`gui.py:151`), the window for the strip's.

**The active document** is read first and, in the finally, activated again by title if still open; `active_restored`
is read back and has no default (F2-0-REVIEW's S7). **Saves, closes, changes:** no save call exists in the path; only windows the job's
own `open_document` returned are closed (`r.opened` is set only after it returned, and `open_document` refuses a same-named
file open from another folder before `OpenDoc6`, so `CloseDoc` on a title can never reach a document of the user's);
assemblies are never opened or closed; every flag is read again and one turned on is said, never saved over. No
component state is ever set. I found no path that saves, closes or changes a document of the user's.

**Call for call.** With the findings as F2-PROBES-REVIEW sets them, the job's calls are the probe's but for three things
that review lists and I confirm: the reads (`equations`, `feature_states`) on a document not active or component-only, which no
probe step made and on which GLOBALS_DIFFER rests; the walk's handle rather than `GetOpenDocumentByName`'s for a
component's export; LIGHTWEIGHT inferred. W9's `use_open_document` reads cited by B (`read_old_assembly`, `swbuild.py:6925-6950`)
are of an assembly's mates and components, not a part's equations, so they do not cover the first. The demonstration
must (F2-PROBES-REVIEW §4 items 1 to 6).

**If the job stops halfway**, the user loses nothing of theirs: nothing is saved, the export is a copy, every window the
job opened is closed in the finally, and the active document is put back.

- A refusal in the reads makes no folder.
- A stop during the export leaves a new folder holding the files written so far, and its list headed *DO NOT PRINT THIS
  SET*.
- What is not covered: the app or SolidWorks dying mid-export, or *close anyway* in the window, leaves a folder of some
  files and **no list**, which looks like a set. The close-anyway question says so. A part window the job opened may then
  stay open, unmarked. This is the one way a user could print an incomplete set. A cheap guard is in §7.

## 4. Package C: what the user sees

Every refusal, result, list and span sentence is pinned on its exact string in `tests/test_ui_text.py` (REFUSALS) and the
two new Tk files; the coupon's whole list is pinned. Read state by state:

- **The span line and Measured**: plain and true; *adds / takes off / adds nothing*; the floor said as *the least
  proposed*; a reading not a number said. The flag's sentence names `0.3 × module (0.45 mm)` as *the most a gear of this
  module is given today*, true of the machined default, but see M2 for when it fires.
- **Print files' place**: form footer between Update values and Build (the strip keeps 460 px, the sentence wrapped in
  the room left); the window's fifth button after Export as… (1080 px, the sentence's 400). Matches §3.1 and E5.
- **LIGHTWEIGHT** (*with RangeBox open, Gear_… may be a lightweight component of it; resolve it there, or open the part
  itself, then print again*): true of both cases it stands for, and opening the part clears either.
- **CHANGES_ON_UPDATE**: untrue when Update cannot run (M1).
- **The result after a list that could not be written** (M2): *Print files wrote Coupon_A.step and its print list in … .
  Its print list could not be written …*, pinned in `tests/test_print_form.py:323`. The first sentence is composed by
  `print_result` before `write_list` runs (`gui.py:1983-1994`, `workbook_gui.py:1461-1471`).
- **NO_RECORD** says *has no .gear.json beside it* also when the file is there and does not read (`form_print` is handed
  None for both; `ui_text.py:6682`): S5.
- **COMPONENT_ONLY with no assembly named** (window read None, or two assemblies open) says *make it active, or close
  it*, impossible for a component-only part. Once `PART_WINDOW_READ` and `STEP_EXPORT_FROM_COMPONENT` are set, COMPONENT_ONLY
  no longer arises; a nit.
- **NOT_A_PART**'s variant naming the active assembly is unreachable on the form (the snapshot's path is blanked when the
  active document is not a part, `gui.py:1386`); harmless.
- **The README's *Calibrating your printer***: a person who never saw the plan can follow steps 1 to 5 and would send the
  right readings, grades and print details. Two faults: step 6's decision trigger (M2), and *"send the session that set
  this up"* (README.md:207), which means nothing to a reader of a public README (S6). The plan's table to fill (§3.2,
  *Measured*) is not in the README; the prose lists every number it holds, so that is optional.

## 5. The two places the interface was short

- **FOREIGN_RECORD.** The window makes no Update plan for another workbook's record (`self.record` None), so B's check
  of `update_plan.foreign_record` (`printout.py:377`) cannot fire from the window; C says it itself after B's gate
  (`workbook_gui.py:1429`). It is correct and tested (`test_a_copy_of_a_workbook_is_refused_as_another_workbooks_record`).
  **Recommend:** in the should-fix round add a keyword `foreign_record: str = ""` to `workbook_print` (B), checked where
  `update_plan.foreign_record` is now; the window passes its own verdict (the store's `foreign_workbook` of the settled
  record, as `_foreign_record` reads it) and drops its override. The order then lives in one place. Not needed before the
  demonstration.
- **An Output folder not on disk.** Both C's form (`gui.py:1974`) and window (`workbook_gui.py:1433`) refuse it after B's plan,
  while B's planners fall back to the part's folder (form, `printout.py:335`) and the assessment's or the workbook's
  (window, `printout.py:432`) for an empty one, fallbacks C's checks make dead, and B's job would make a missing Output
  folder (`swbuild.py:10313`). **Recommend:** a planning code `NO_FOLDER` in `printout` (detail: the folder), from both planners
  when the folder is empty or not a directory (by an `isdir` keyword like `exists`), B's fallbacks removed, C's two sentences
  kept as its words; and the job makes only `print` and the press's folder (`os.mkdir`), refusing if the Output folder has
  gone. S4.

## 6. Nothing machined or pinned moved

`git diff 02b3ff1 HEAD -- tests` removes no line: every test change is an addition. `tests/test_printed_rule.py`, F1's tests,
W9's pins and `test_findings.py`'s existing pins are green. In `src`, outside the new F2 code, the only edits are: the snapshot
gains `revision`; three grid rows and two footer columns move one place (`gui.py`, `FOOTER_COLUMNS`); `workbook_footer` gains
`printing`, tested first and otherwise unchanged; *building* is now `job.kind == JOB_BUILD` where it was `not job.updating`
(the same for W9's two kinds); the swbuild Protocol gains two lines.

Tried to break it: a machined gear's Derived rows are `derived_rows` untouched (`_rows_with_span` returns them as they are
when the reading is not a span, and `span` is "none" for every machined gear, arcs included); no Measured entry or line
appears for one; the span's card is outside `EXPLAINER_FIELDS`; nothing new writes a record or a spec; the workbook's
Export and Export as… are unchanged but for a busy sentence while a print runs; no build, Update or Build again… path
calls anything new. What a machined user does see is new by design: the Print files button and the bar's line (E4).
I found nothing that moved.

## 7. The choices left to the coordinator: recommended rulings

**Package A**
1. Measured's arithmetic in `span.measured`: accept (C already words it with no sums; amend F2-INTERFACES §6).
2. k = 1 allowed: accept.
3. The nearest k inside the bounds, a tie to the smaller: accept.
4. The order none, arcs, no_contact, narrow_face, span: accept.
5. An unknown recipe reads none: accept.
6. Names beyond the interface: accept.
7. (A's own flag) `over_default` against `0.3 × module`: change, M2.

**Package B**
1. `active_restored` a required keyword: accept.
2. `PrintPart.variables` and `made`: accept; amend the interface.
3. LIGHTWEIGHT inferred for any part not found while an assembly is open: accept for F2. It is safer than the
   interface's read, which would open a lightweight part in a user's sub-assembly by the last row. Keep C's *may be*.
4. `document_by_path` by the walk: accept; the demonstration exports a component by it.
5. `use_document` and `window_read`: accept.
6. `EXTENT_MEASURED` as a `printout` constant: move it into `findings.py` in the findings commit, with its log lines and a pin
   (the house rule reads measured facts from `findings.py` only), and skip the herringbone until measured (S3).
7. The window's rules: accept, but tell a new revision from an in-place add (M1).
8. The job's order: accept.
9. A feature code SolidWorks will not give (UNREAD) neither refuses nor warns: accept.
10. The extra facts (close failed, flags unread): accept; C words both.
11. An empty Output folder's fallbacks: reject; NO_FOLDER instead (S4).
12. `printout`'s run-time imports: accept.

**Package C**
1. Measured per gear in a pair, A:/B: lines: accept.
2. A withheld span as a line under the rows: accept.
3. The Measured line's wording: accept, with M2's trigger.
4. The span's card borrowing the Teeth diagram, outside `EXPLAINER_FIELDS`: accept.
5. The buttons' places: accept (the plan's).
6. Print files enabled whenever no job runs: accept.
7. A print's finish as a standing note: accept.
8. WORKBOOK_ERROR reworded: accept.
9. COMPONENT_ONLY plural *close them*: accept.
10. The print list's layout: accept.
11. The README's numbers: accept, with M2 and S6.
12. The footer wrap following the buttons shown: accept.

**Also for the coordinator:** a guard against a list-less folder (§3). The press's folder could be made with the suffix
`" (writing)"` and renamed to its stamp once the list is written; a folder left so then says what it is. Optional.

## 8. Must-fix and should-fix

**Must-fix (before the stage closes; neither blocks the demonstration's runs, but M1 shows in one if a structural cell
is edited):**

- **M1. CHANGES_ON_UPDATE tells the user to press Update SolidWorks when Update cannot run.** A part classify says needs
  a new revision (its stem opening a sentence of `update_plan.structural`) is detailed "new part"
  (`printout.py:414`), like an in-place add (`:416`). C then says *press Update SolidWorks, then print* or *… and save*
  (`ui_text.py:6661-6662`). But `UpdatePlan.needs_new_revision` means Update is not run and the window offers Build again…
  (`workbook/update.py:102-104`, `:171-174`). The same is true of the values clause whenever the plan needs a new
  revision. Fix: B gives a third detail value (say `"new revision"`) for a part needing one, or a detail key when
  `update_plan.needs_new_revision`; C says *Build again… would make … new; build it again, then print* there. Tests: a
  new pin in `test_printout.py` and `test_ui_text.py`.
- **M2. The Measured line's flag does not fire where §3.2 puts the user's decision, and the README says it does.** `span.py:244` flags `j > 0.3 × module`; README.md:203-206 tells the user the line flags the decision. Fix (a
  ruling on §3.0's wording against §3.2's): flag when the proposed `j` exceeds this gear's printed default (0.3 mm from
  module 1 up, `0.3 × module` under it), and say which modules it would touch (*more than 0.3 mm: gears under module 1.13
  would get more than 0.3 × module; that is yours to decide, README step 6*). Reword README step 6 to that trigger.
  `tests/test_span.py`'s over_default pins and `tests/test_ui_text.py`'s line pins change, for this reason.

**Should-fix** (numbered from S2; the first draft's S1 became M2):

- **S2. The result claims a list it did not write.** `ui_text.py:6766` (and the plural) says *and its print list* before
  `write_list` runs; on its failure the status reads *wrote … and its print list … Its print list could not be written*
  (`gui.py:1983-1994`, `workbook_gui.py:1461-1471`). Compose the first sentence after the write, or drop *and its print
  list* when it failed. `tests/test_print_form.py:323` pins the contradiction and changes with it.
- **S3. Herringbone in `EXTENT_SKIPPED`** until a run shows its vertices (`printout.py:629-641`), before `EXTENT_MEASURED`
  is set True; F2-PROBES-REVIEW's caveat.
- **S4. NO_FOLDER, and the job not making the Output folder** (§5): `printout.py:335`, `:432`, `swbuild.py:10313`,
  `gui.py:1974`, `workbook_gui.py:1433`.
- **S5. NO_RECORD for a `.gear.json` that is there but does not read** (`ui_text.py:6682`; `gui.py` `_active_sidecar` hands
  None for both): *has no .gear.json beside it that Gear Generator can read*.
- **S6. README.md:207, *"send the session that set this up"***: say what to do with the numbers in words a reader of a
  public README understands (for instance, *keep them with the table below and send them to whoever set up your
  printed gears*), and consider copying §3.2's table.
- **S7. The fake reads any non-None `PART_WINDOW_READ` as measured** (`tests/test_swbuild.py:2063-2067`), and C's end-to-end
  tests patch it True (`tests/test_print_form.py:346`, `tests/test_print_window.py:257`). `swcom.window_read` answers None to
  True, so the tests pass on a value the app would treat as unset, the very slip F2-PROBES-REVIEW's must-fix is about.
  The fake should accept only `"Visible"` and `"ActiveView"`, and the tests patch `"Visible"`.
- **S8. FOREIGN_RECORD from B's planner** (§5): `printout.py:377`, `workbook_gui.py:1429`.

**Nits (say, or leave):** MODIFIED on a part the job opened itself and found marked on opening (a rebuild on open) tells
the user to save a document they never saw open. COMPONENT_ONLY's *make it active* for a component-only part
(`ui_text.py:6703-6716`). Two current parts with one stem from two folders would stop the set mid-export on
*already exists* rather than refuse before it. The bar's line stays stale for one poll after SolidWorks is lost (the
snapshot's error path does not derive, `gui.py:2093-2097`).

## 9. What the demonstration must add

F2-PROBES-REVIEW §4's six items stand: the window press with the parts component-only; GLOBALS_DIFFER read off a
component-only and a background part; a background part exported unactivated; a lightweight component refused and left
lightweight; the size check on every part of the 12 : 1 reducer on 2026; a part the job opens and closes itself. Add:

- M1's case, if the demonstration edits a Gears cell that is structural.
- One press after the Output folder is removed, once S4 is in.
