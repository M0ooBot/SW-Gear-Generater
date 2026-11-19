# Review of F1's demonstration runs on SolidWorks 2026 and 2024

*Independent, 2026-11-18.*

**What I read.**
- \`5e2f386\`: the three logs, the two run sections of \`docs/notes-printed/F1-DEMONSTRATION.md\`, and the JSON where
  a log pointed to it.
- \`c1c9046\`: the script the runs were made from. It is \`353d09f\` plus the four should-fixes of
  \`F1-DEMONSTRATION-REVIEW.md\`.
- W9a's 2026 log (\`probe/results/w9a-final-sw2026-20261117.log\`), for its own value Update.
- \`git diff 12cf15d..workbook\`.

**How the logs are cited:**

| Cite | Log |
|---|---|
| "26:" | \`probe/results/f1-demo-sw2026-20261118-1-spur-pair-rangebox-clean.log\` |
| "24a:" | \`probe/results/sw2024/f1-demo-sw2024-20261118-1-rangebox-clean.log\` |
| "24b:" | \`probe/results/sw2024/f1-demo-sw2024-20261118-2-spur-pair-clean.log\` |

No SolidWorks or Excel was started, and nothing was changed but this file.

**One scratch check** (scratchpad, deleted after). I took a \`git archive\` of \`5e2f386\` and applied
\`12cf15d..workbook\`'s changes to \`src\`, \`tests\` and \`probe\`: that is the merge's incoming code, without its docs.
- The whole suite: **4747 passed, 1 skipped, 1 failed**, the known Tk font test.
- \`f1_demonstration.py --self-check\`: 0 failed.

## Verdict

**F1 is done by its own Done-when.** No must-fix.
- Every \`ok\` line the write-up relies on is in the logs, at the line it gives, and says what the write-up says.
- Each is a reading over the items it names, with S1's counts in place.
- Two statements in the write-up are not in the committed logs. Neither is a claim the Done-when rests on (§1.4).
- One sentence of the plan is contradicted by what was measured: §6 says "route (c1)'s puts are not met" for typing
  Printed. That is a correction to the plan's text, not a fault of the app (§3, should-fix S1).

## 1. Section by section

The counts in each log, by its own \`==\` sections, are the write-up's:

| Log | spur | pair | rangebox | Plus | done |
|---|---|---|---|---|---|
| 26 | 36 ok | 17 ok | 56 ok | the APPDATA check (26:3) | 0 failed, 0 noted, 0 STOP (26:1063) |
| 24a | — | — | 56 ok | the APPDATA check (24a:3) | (24a:221) |
| 24b | 36 ok | 17 ok | — | the APPDATA check (24b:3) | (24b:857) |

There is no FAIL, STOP or NOTE line anywhere.

### 1.1 \`spur\` (26:11-421; 24b:11-420)

For each of the four parts, on each version:

**The name.** The form's plan, with the file new (26:14, 116, 217, 318).

**The Backlash.** \`Session.equations\` read from SolidWorks, the text quoted in full:
- printed: \`"Backlash"= IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )\`, evaluated 0.3 at module 1.5 and 0.24 at
  0.8 (26:108, 310; 24b:107, 309);
- machined: \`"Backlash"= 0.3 * "Module"\`, evaluated **0.44999999999999996** at 1.5 (26:209; 24b:208) and 0.24 at
  0.8 (26:411; 24b:410).

The write-up's "0.45" is that value within the 1e-9 tolerance. The logs give the double.

**The tooth**, by small_pinion_check's own checks: no feature in error, one body, the volume within 0.1 %, and
exactly **100 tip corners for 25 teeth** on the outer radius with none just inside (26:110-112, 211-213, 312-314,
413-415; 24b:109-111 and so on). Those are real counts over the part's vertices.

**The \`.gear.json\`.** Sidecar 3 printed, sidecar 1 machined (26:113, 214, 315, 416; 24b:112, 213, 314, 415).

**The volumes, across the parts:**
- At module 1.5 each volume is its own outline's and not the other's (26:418-419; 24b:417-418).
- Printed less machined: +125.3602 mm³ on 2026 and +125.2969 on 2024, against the outlines' +125.2964 (26:420;
  24b:419).
- At module 0.8 the two are one solid: 2170.457157 mm³ on 2026, 2170.322686 on 2024 (26:421; 24b:420).

**Logged, not judged (as designed).** The form's diagnostics for the printed module 0.8 gear (26:216) are A's two
printed warnings: the 0.317 mm tip, under a 0.4 nozzle, and the module under 2.5 nozzle widths. They are the plan's
figures for module 0.8, 25 teeth: a printed warning of F1, seen live on the form.

### 1.2 \`pair\` (26:424-851; 24b:424-849)

For the printed pair, on each version:
- **The names:** both parts and the assembly with _P, new (26:425; 24b:424).
- **The build:** \`ok True, skipped ''\` (26:629; 24b:628).
- **The drive:**
  - Pinion −30.000000°, gear +15.000000°, interference \`(0, 0.0)\` at 10° and at 40° (fact 26:630; 24b:629).
  - The judgement: gear A 30°, B −0.5 of it, so +15° for a −30° drive is the right sense (26:631; 24b:630).
- **Each part:** its Backlash the IIF at 0.3, and its sidecar 3 (26:632-635; 24b:631-634).

The machined pair is the same without _P, with \`0.3 * "Module"\` at 0.44999999999999996 and sidecar 1 (26:842-849;
24b:841-847). The section's own judgement holds on both (26:851; 24b:849).

### 1.3 \`rangebox\` (26:855-1056; 24a:11-214)

**The master and the copy.**
- The master's own record was at **link 7, no part saying a process** (26:855; 24a:11).
- The copy is valid, owner ours, and the read's digest equals the record's (26:863; 24a:19).
- \`copy_built\` wrote the copy's record forward to 11 before the app opened it (26:868; 24a:25). The write-up says so.

**As built:**
- *the Process:* blank read machined, **5** jobs planned machined with no _P, nothing to do (26:880; 24a:37). S1's
  check holds the gears planned to the record's gears inside that judgement.
- *the wording:* the log says "5 gears" where it means the five parts' jobs. That is a slip in the script's message;
  the gear-id comparison is what judged.
- *the footer:* W9's footer, with nothing of Process in it (26:883; 24a:40).
- *the Process line:* the *(add a row labelled Process)* line (26:884-885; 24a:41-42).
- *the files:* nothing written by the open, by size, time and sha256 (26:886; 24a:43).

**The user's work, before:**
- the five components, from the copy (26:890; 24a:47);
- the eight mates by name (26:892; 24a:49);
- H, N and L each read in full: every app body at its record frame (6.6e-10), the three locked sprockets at 0.0 or
  7.1e-15, Sprocket-4 at −90.000000000 mm, the train free (26:893-895; 24a:50-52);
- every user mate on in the modes it was on in (26:896; 24a:53);
- the User Keyway at code 0 (26:898; 24a:55).

**Printed typed.** Excel set \`Box!A10 := 'Process'\` and \`Box!B10 := 'Printed'\` and saved (24a:58-60; 26:900).
Then:
- the Box reads \`printed\` at \`Box!B10\` (26:919; 24a:76);
- the line reads *Printed, 0.4 mm nozzle* (26:920-921; 24a:77-78);
- *Backlash alone* holds for the five parts (26:922; 24a:79);
- the footer's sentence names all five (26:928; 24a:85);
- nothing of the user's is foreseen stopping the press (26:929; 24a:86).

**The press:**
- *what it wrote:* each part logged \`set "Backlash"\` and \`rebuilt once\`; the layout and carrier "already hold the
  workbook's values" (26:944-962).
- *the judgements:* ok, \`changed == ['Backlash']\` in each of the five (26:1009; 24a:166). Nothing made new, every
  list read empty (26:1010; 24a:167).
- *the carry:* \`[('Sprocket-1','Sun'), ('Sprocket-2','RangeSlv'), ('Sprocket-3','Sun')]\`, said and done (26:1011;
  24a:168).
- *the puts:* app bodies and those three sprockets (26:1012; 24a:169).
- *the user's work:* nothing of the user's in error (26:1013; 24a:170).
- *the files:* no SolidWorks file saved (26:1014; 24a:171).
- *the sentence:* C's sentence once (26:1015; 24a:172).

**Read back:**
- the IIF at 0.3 in each part, and the count line naming all five (26:1017-1022; 24a:174-179);
- the record at link 11, the same five files, printed, sidecars at 3 (26:1023; 24a:180);
- all eight user mates read both times and joining the same (26:1025; 24a:182);
- H, N and L as before (26:1026-1028; 24a:183-185);
- the user mates on as set (26:1029; 24a:186);
- the Keyway at code 0 (26:1030; 24a:187);
- the components (26:1031; 24a:188).

**The second press:**
- the user saved the five parts and the assembly (26:1037; 24a:194), and everything was closed (26:1038; 24a:195);
- planned nothing (26:1039; 24a:196);
- the press loaded **all eight documents from disk** (26:1043; 24a:200), placed nothing (26:1049; 24a:206), and said
  \`SolidWorks already matches the workbook: nothing was changed.\` without the names sentence (26:1046, 1051;
  24a:203, 208);
- every gear stood where it was, at 0.0e+00 (26:1052; 24a:209);
- no document was marked before or after (26:1054; 24a:211);
- the record holds no unsaved or mismatched document (26:1055; 24a:212).

### 1.4 The write-up against the logs

**Every line number the two run sections give points at the line they describe.** I checked each one in the three
logs:
- the times (78, 113, 458 s; 711, 84, 92 s), the ok counts, the memory figures (peak private 1.67 GB on 2026, 6.95 GB
  on 2024; least free 9.12 and 9.34 GB) and the press times (162.7 and 109.2 s; 305.7 and 129.1 s);
- the calls by member, the same dict on both versions (26:937 = 24a:94; 26:1047 = 24a:204);
- the boxes:
  - *Calculating Interference Detection* (26:843) and *Opening* (26:889, 24a:21);
  - the untitled ticking boxes (26:1042; 24a:46 *Post load updating*, 24a:199 *Performance Evaluation*);
  - the watch's summaries, other windows 0 (26:1060; 24a:218; 24b:854).

**Not in the committed logs:**
- the sha256 of both masters' 34 files before, between and after the runs;
- WSL kept idle with a process check every 15 s;
- the sessions' start and exit by \`taskkill\` without \`/F\`.

These are the runner's own statements. They are plausible, and the masters' hashes matter only to the masters, not
to the Done-when. If they are to stand as evidence, the hash list should be committed beside the logs.

**"RangeBox.SLDASM reads marked … after read_every" (26:897; 24a:54) is borne out.** The script's own mode reads
left the assembly marked before the press, unmarked straight after the copy's open (26:865; 24a:22). So, as the
write-up says, the press's "nothing saved" rests on the files' sha256, not on save flags. That is the right ground.

## 2. F1's Done-when, its SolidWorks items

| Item (PLAN-PRINTED §2.8) | SolidWorks 2026 34.1.1 | SolidWorks 2024 32.5.0 |
|---|---|---|
| One printed spur gear built | Gear_m1.5_N25_P: 26:14, 107 (built, saved), 108 (IIF, 0.3), 110-112 (clean, +0.0016 %, 100 tips), 113 (sidecar 3); told from machined 26:418-419; m0.8 26:310, 421 | 24b:14, 106, 107, 109-111 (−0.0035 %), 112; 24b:417-418; 24b:309, 420 |
| One printed pair built | 26:425 (names), 629 (built), 630-631 (turns, no interference), 632-635 (IIF, sidecars), 851 | 24b:424, 628, 629-630, 631-634, 849 |
| Printed typed on a copy of setup.master | master at link 7 26:855; as built 26:880-886; typed 26:900, 919-922 | 24a:11; 24a:37-43; 24a:57-60, 76-79 |
| …one Update writes every part's Backlash in place | 26:944-958 (\`set "Backlash"\` ×5), 1009, 1010, 1017-1023 | 24a:166, 167, 174-180 |
| …touches none of the user's items | 26:1011-1014, 1025-1031 (as before 26:890-898) | 24a:168-171, 182-188 (as before 24a:47-55) |
| …reads back as W9a reads its own Update | W9a's \`go_judge\`, \`read_every\`, \`entities_of\`, keyway and components (26:1025-1031); the same puts as W9a's own value Update (w9a-final:95, 98) | 24a:182-188 |
| The quiet second press | 26:1039-1055 | 24a:196-212 |

**What each version handed back.** On both, every part's Backlash read
\`"Backlash"= IIF ( "Module" <= 1 , 0.3 * "Module" , 0.3 )\`:
- the app's text character for character, spaces included;
- no units, the quotes and \`<=\` as typed;
- after the first press, through \`Session.equations\` (26:1017-1021; 24a:174-178).

The second press opened every part **from disk** (26:1043; 24a:200), after the user's save and close. So K11 compared
the IIF as SolidWorks had saved and reloaded it, against the record's, and found nothing. The press went on to say
*already matches* with no refusal (26:1046; 24a:203). That is the measurement my review of the script (§1.4) said
would settle it, on both versions.

## 3. What differs between the versions

Every judgement reads the same on both: the same counts, calls, puts and carry. The differences, each a caveat:

**Memory on 2024.**
- The first press took SolidWorks 2024 from 3.14 to 6.20 GB private (24a:89-90), and the second to 6.95 GB (24a:200).
  On 2026 the peak was 1.67 GB.
- Free memory never fell under 9.34 GB, so neither 6 GB floor came near.
- It is in line with W9c's 3.3 to 4 GB. It is a reason the 2024 press wants a fresh session on a 24 GB laptop, not a
  fault.

**Time.** The 2024 presses took 1.9× and 1.2× the 2026 ones; the section took 711 s against 458 s.

**The solid's tolerances.**
- Volume against outline: +0.0010 to +0.0016 % on 2026, −0.0035 % on 2024 at module 1.5; −0.0054 % and −0.0116 % at
  module 0.8.
- The farthest tip vertex: 1.1e-3 and 6.2e-4 mm beyond the outer radius on 2026, about 1e-14 on 2024.
- All of these are an order of magnitude or more inside small_pinion_check's 0.1 % and 0.005 mm. They are how each
  kernel places a flank and tip intersection, not the backlash: the printed-less-machined difference agrees with the
  outlines to 0.064 mm³ on 2026 and 0.0005 mm³ on 2024.

**Progress boxes.** 2024 showed two untitled ticking boxes (*Post load updating*, *Performance Evaluation*) at an
assembly's open. The watch took them as progress boxes. No What's Wrong came, so the \`--close-outlived-whats-wrong\`
path in force on 2024 (24a:8, 24b:8) was never exercised: the write-up says so.

**Not a version difference, but a measured fact against the plan.** On both versions the press **re-placed the whole
train in every mode**:
- \`placed\` lists the carrier, Sun, the three planet copies, both dogs and RangeSlv, \`put_in ['N','L','H']\`, 33 puts
  (26:936-939; 24a:93-96);
- the locked sprockets were carried along, as the footer foresaw.

Nothing turned:
- post-check \`turned False\` in N, L and H (26:940-942);
- every app body at its record frame before and after (26:893-895, 1026-1028).

So the puts put the gears where they already were. W9a's own value Update of Sun's Backlash did exactly this on 2026
(\`w9a-final-sw2026-20261117.log\`:95, 98, 392-395), so it *is* reading back as W9a reads its own Update.

But PLAN-PRINTED §6 (\`docs/PLAN-PRINTED.md\`:926-928) says that, since no gear moves, "route (c1)'s puts and K2's
refusals are not met":
- *K2's refusals:* not met, as said (nothing refused).
- *The puts:* they *were* made, harmlessly.

A user's mate on an app gear's face is therefore re-solved by a put on this Update, as by any of W9a's value Updates.
setup.master has no such mate, so that was not seen. Not a fault. The plan's sentence should say what was measured
(S1).

## 4. The evidence and the merge of \`workbook\`

The incoming \`src\` changes (\`git diff 12cf15d..workbook -- src\`) are three:
- **\`findings.py\`:** the \`CARRY_*_ON_2024\` and \`REFERENCED_CONFIGURATION_READ_ON_2024\` values, set from W9d's
  2024 run, with comments.
- **\`ui_text.carry_sentence\`:** split into \`_carry_texts\`, plus \`_on_any_version\` for a record with no SolidWorks
  version on record.
- **\`update.carry_foresight\`:** \`as_year\` and \`per_year\` for that same case.

All three are read only on the path of a **carrying Build again…**: \`plan_carry\` and the worker, and the Build
again? question. **None of F1's SolidWorks evidence goes through that path:**
- spur and pair are the strip's builds;
- rangebox's presses are Updates.

The Build again… plan the Desk computes in planning feeds the footer's button, not its sentence. Every F1 line
quoted above is an Update's or a build's.

Also unaffected:
- the record's *written_by* is kept on every F1 write, so the "no version on record" branch is not met by an F1
  record;
- F1's machined pins (\`test_printed_rule\`) cover Build again…'s reuse and W9d's columns, not the carry question's
  words.

**The evidence stands for the merged head.** The merge's code passes the whole suite and the script's self-check
(scratch check above). Nothing needs running again on SolidWorks for F1.

## 5. Is F1 done?

**Yes, by its own Done-when (§2.8):**
- §2.7's pins hold (the suite);
- every kind derives, checks and plans printed against the fake;
- a workbook built before F1 opens Machined and unchanged, and Update carries Printed against the fake;
- the boards show the Process row, the Process line and a printed warning (the \`.dc.html\` boards);
- UI-DESIGN, the README and the hints say what Printed does;
- the three SolidWorks items on 2026, and the same on 2024 as the confirming build (§2 above);
- reviewed: \`F1-REVIEW.md\`, \`F1-DEMONSTRATION-REVIEW.md\` and this file.

**Still owed, none of it F1's Done-when:**
- **The design boards' PNG renders**, not redone since W9a, for want of the Mac's Chrome. The boards themselves are
  current.
- **The span over k teeth**, moved to F2 §3.0 by ruling 1. It is F2's first item and its Done-when's first line.
- **The user's word on the rulings made for them**, each recorded as theirs to overrule:
  - D11's answer (B), and D3's 0.3 mm (to be set from §3.2's prints);
  - D6, no pair interference check;
  - the review rulings recorded in PLAN-PRINTED's *Changes after F1's review*.
- **S1 below**, a sentence of the plan.

**F2's first steps, by the plan as it stands (§3):**
1. **§3.0, on Linux.** The span over k teeth in a printed spur or helical gear's Derived panel: pure code and the
   card's text, tested against the fake, with a machined gear's card held by \`test_printed_rule\`'s pins. My F1
   review §1 gives the formula and its two guards: the caliper's contact diameter on the drawn involute, and none
   for recipe B.
2. **§3.1, the probe first.** \`IModelDocExtension.SaveAs3\` to a \`.step\` name is a call the app has not made, and
   it writes a file. The probe uses a scratch part and checks:
   - no dialog;
   - the part's own path and modified mark unchanged;
   - on 2024, a part with a feature in error, where any box is the STOP until ruled.

   One short run on 2026, the same on 2024, and the findings committed.
3. **Then Export STEP**, on the form and in the Workbook window:
   - every distinct current part into \`print/\`, with its print list;
   - refused while the record marks a part unsaved or mismatched;
   - never overwriting (\`_r2\`);
   - the file checked by counting solids, without opening it in SolidWorks.
4. **§3.2, the user's step.** The user opens a STEP in Bambu Studio, prints the module 1.5, 20-tooth spur and the bore
   coupon, and measures. D3's figure and F3's allowance are set from those measurements.

## Summary

**Must-fix: none.**

**Should-fix (documents only):**
- **S1** \`docs/PLAN-PRINTED.md\`:926-928, §6: "route (c1)'s puts … are not met" was not what was measured. The Update
  re-placed the whole train in every mode on both versions, the gears staying at their record frames, as W9a's own
  value Update does (26:936-939, 24a:93-96, w9a-final:95, 98). Say so, and that a user's mate on a gear face is
  re-solved by those puts as by any W9a value Update.
- **S2** \`docs/notes-printed/F1-DEMONSTRATION.md\`: commit the masters' hash list it cites (34 files), or say it is the
  runner's statement, not in the logs.
- **S3** \`probe/f1_demonstration.py\`, the as-built line: say "parts" where it means the five jobs ("5 gears planned
  machined", 26:880). Wording only; the judgement compared gear ids.
