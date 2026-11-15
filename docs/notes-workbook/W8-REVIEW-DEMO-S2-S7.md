# W8 review of the demonstration's rest, s2, s3, s4, s5, s7 and the window stage (independent, read-only)

**Verdict: the sections do what §5 and its rulings ask, with two gaps that should be closed before the closing run.
Neither is a script crash. Each would let the run close W8 while still carrying an open question about what SolidWorks
2026 does.**

1. **The run that closed s2 contradicts s7's summary, and nobody has noticed.** In s2's 0-failed run, a turn given in
   2H after an Update had put every mode was read in 4L. In the same press, the app's own judgement on showing then
   found 4H and N at the built turn. In the first press of that run, the same judgement found them turned. So either
   that turn did not reach 4H and N, or 2H's put did. The first breaks "a turn shows in every configuration in every
   state tried"; the second breaks "a put that moves a body stays in the configuration showing". The changed Update
   gives a second instance: FDrive's moving put in 2H was found in place in 4H and N, and s7 case 5 read the same put
   stay in 2H. The script never read 4H or N itself in that state (M1).
2. **s7 asserts nothing about what it measures** (M2). A closing s7 passes whatever SolidWorks does. §0.5's 2024
   triggers ("per-configuration slide values refused, or positions found shared…") are not STOP lines.

Everything else is right or nearly so:

- The expectations after every Update come from §2.3's key and the workbook edit, never from the app. `KEY` is reset
  per section and changed only by the section's own edits. `moved_frames` is applied to the frames copied from the
  master. The one exception is S1.
- Every mode's every body is held to those frames through fresh handles (`judge_mode_frames`, `frames_gap` over the
  wanted keys, a missing body infinite).
- Flags are read raw beside the app's own read after every changed Update.
- The five s7 FAILs are the script's, as claimed.
- The JSON matches the log on the ten values I compared.

**What was reviewed.** `probe/workbook_assembly_check.py` at HEAD (`48ab0aa`, line numbers below), the s2–s7 part whole
with its helpers. That covers the commits `97e2ed0`, `959732b`, `289b67f`, `08ed03a`, `a1f0ef0`, `1ecd115`, `42c393b`,
`be07ebd`, `074df2c` and `48ab0aa`. In the old part I read `run`, `DialogWatch`, `traced_call`, `TRACE`, `close_ours`,
`copy_built`, `keep_master`, `end_copy`, `check_quiet_update`, `update_marks`, `frames_gap`, `Desk.build`,
`Desk.update_solidworks` and `main`. I also read `probe/workbook_window_check.py`'s W8 stage, its runner, `callback_failed`,
`watchdog`, `finish` and `in_solidworks`, at `074df2c`, and swbuild's `TrainCheck`, `_modes_put` and the `baa1a56` diff.

**The evidence I read.** Every log the brief lists, through `iconv -f cp1252`: the stopped s2 runs at the lines cited,
and the others whole or by every FAIL/STOP/NOTE/DIALOG/fact/judge/table line. I parsed `w8-s7-20261115-135428.json`.

**How it was checked.** By reading, and by recomputing the JSON's fields against the log. I did not run the helpers in a
harness: every point below rests on logged readings, not on helper arithmetic. No SolidWorks, Excel or Windows program
was run.

---

## Must fix before the closing run

**M1. s2's 0-failed run reads 4H and N at the built turn where s7's two rules say they cannot be; the script never
reads them itself.** (must fix; script 6763–6770; `w8-workbook-assembly-20261115-151412-s2.log` lines 224–227, 356,
448–451, 569–572, 709)

*The first press in 4L* (app at `4871a85`), after the user's turn in 2H, which the script read in every mode. The app's
judgement on showing each mode, in the order 2H, 4H, N, 4L:
- 2H: turned True. 2H is put.
- 4H: `out of step [('ModeSlv', 'FrontDog')]`. This is a 37° turn there.
- N: turned True.
- 4L: was judged at the start.

So 2H's moving put did not reach 4H or N. That is s7's rule.

*The fresh turn.* All four modes had now been put (moving puts, back from 37°). The fresh turn in 2H was read by the
script in 4L only, at +37° on every rear body, LoDog across RangeSlv (line 356).

*The second press in 4L*, the same app, the same order (lines 448–451):
- 2H: turned True. 2H is put.
- 4H: `out of step [], off axis [], turned False`.
- N: `out of step [], off axis [], turned False`.

With nothing off its axis, `turned` is judged (the ruling of `W8-REVIEW-FIX-9-18-AND-WINDOW` voids it only while a body
is off its place). With ModeSlv at a 37° turn, 4H would read ModeSlv–FrontDog out of step, as it did in the first
press. So when shown, 4H and N stood at the built turn. Either:
- (a) the fresh turn reached 4L but not 4H or N; or
- (b) 2H's put reached 4H and N this time.

(a) contradicts "the drive's turn shows in every configuration in every state tried". (b) contradicts "a put that moves
a body stays in the configuration showing".

*The changed Update gives the same picture* (lines 569–572 and 709; also in `…-111951-s2-turn-carried-per-body.log`,
297–300):
- 2H found FDrive off its place (`off axis ['FDrive']`, which `TrainCheck` defines as "not at their place") and put it.
- 4H and N then found FDrive in place.
- 4L, shown last, did not.
- The check phase's own read of 4L (`motion: … off axis []`, line 560) judges against the record's old frames. So 4L's
  `['FDrive']` comes from its showing at the end, after the three other puts.

s7 case 5 put FDrive +2 mm in 2H by the same route and read it stay in 2H alone. W8-INTERFACES §9.18 recorded "2H's
put reached 4H and N" from the 111951 run; s7's summary does not account for it. Behaviour is unaffected, since every
mode is put and post-checked (§9.18). But the user-facing switch `TURN_PER_CONFIGURATION_ON_2026 = False` and the put
fact pinned to s7 both rest on the two rules.

*Change:*
- In s2, after the fresh turn, show and read 4H, N and 4L, not 4L only (`w8_shown_turned` on all three). Assert them per
  the finding, not as facts.
- Add an s7 case that reproduces the state on a copy, reading all four configurations through fresh handles after each
  step:
  1. drive +37° in 2H;
  2. the app's quiet Update in 4L, which puts every mode;
  3. drive +37° in 2H;
  4. a moving put by the app's route in 2H (FDrive +2 mm, or the train back from the turn).
- Until that has run, the s7 result should say its rules held "on a copy no Update had put", not "in every state
  tried".

**M2. s7 asserts nothing about the findings it pins, so the closing s7 and the 2024 s7 cannot fail on a difference.**
(must fix; script 7556–7589, 7945–7948; W8-PLAN §0.5's 2024 trigger, §6 item 4)
- `s7_judge` logs which hypotheses fit and asserts nothing. That is right for a first measurement ("H broken is a
  result"). But §6 item 4 makes "s7 passes, 0 failed" a definition of done. Now that `TURN_PER_CONFIGURATION_ON_2026` and
  `POSITIONS_PER_CONFIGURATION_ON_2026` are pinned to s7's file, a closing run that read the opposite would still pass.
- Case 7's per-configuration value set and read-back is a `check`. On 2024 its failure is a §0.5 STOP ("per-configuration
  slide values refused").
- "Positions found shared … where §1.9 assumes the 2026 behaviour" has no STOP line at all.
- *Change:* where the running version's finding is a bool, `stop_check` it:
  - every "turn" judgement's `fits` includes "shared" when TURN… is False, or "per_configuration" when True;
  - every moving put's `fits` includes "per_configuration" when POSITIONS… is True.
- Make case 7's value check a `stop_check`. A None finding (2024 until settled) stays a logged measurement.
- The 2024 run in progress needs this to stop where §0.5 says it should.

## Should fix

**S1. After each press that puts, "every mode back at its built frames" is judged against the record the app just
rewrote.** (should fix; script 6683–6684)
- `w8_press_after_turn` ends with `w8_read_all(..., {m: mode_record_frames(desk, m) …})`, where `desk.record` is what
  `finish_update` wrote.
- If the app recorded the turned frames as "built" and left the train turned, this check would pass. The next steps
  (`w8_user_turn`'s "before the turn every body stands at its frame on record") inherit the same record.
- `built` (the copy's frames, held to the read in s1) is in scope.
- *Change:* pass `built` to `w8_read_all`, and check the record's frames equal `built` after a press that put.

**S2. s7 case 4 is not what its label says: the Update's puts moved no body that the following drive turns.**
(should fix; script 7816–7842; s7 log 644–698)
- The copy is untouched, so the changed Update's 52 puts are no-op puts for the input train. Only FDrive, FIdler and
  FOut move, by 2 mm.
- The drive in 2H then turns only the rear and input train. The front train is free in 2H and stays at 0 in the table.
- So "the drive's turn shows in every configuration … including after the app's own Update" rests, within s7, on puts
  that moved nothing it then turned. The real evidence for a turn after the app's moving puts is s2's fact line 356,
  logged and not asserted.
- *Change:* turn the train in 2H before the edit, so the Update's puts move it, or drive in 4H or 4L afterwards, so the
  moved front train turns. M1's new case covers the first.
- In s2, run the second press with `expect="finding"` and assert `SHARED_MAY` per the finding (line 6679 only logs it).
  Both were left as facts "until s7 settles it", and s7 has run.

**S3. s5 (ii) is a characterisation of what the build did, written after the run, and it is not §5's s5. The
status-5 path it was meant to show runs nowhere on SolidWorks.** (should fix; script 7232–7315; s5 log 909–925)
- §5 wanted SolidWorks to refuse the mate at the make in one mode: AddMate5 status 5, and the build's sentence "In mode N,
  the mate … over-defines the assembly." (`_status_sentence`, with step 6 never reached: `W8-REVIEW-TIER11` (3)).
- What ran:
  - (i) the app's own gate refusing a distance mate, which is honest and verbatim;
  - (ii) a 1 : 1 Sun–LoDog coupling that SolidWorks made with status 1 (line 912). The train locked, and step 6
    reported seven bodies fully defined, naming neither the mate nor the cause.
- `074df2c`'s expectations (status 1, step 6, exactly those seven bodies) were written from the 140811 run's FAIL
  (line 914). They hold what the app does, not what the plan asked, and they have not run.
- The downstream handling is shown and right: no assembly file, the document open and named, the parts on record, the
  footer refusing the same build, the close.
- The status-5-in-a-mode path is covered on the fake:
  `test_a_mode_whose_coupling_over_defines_stops_the_build_naming_the_mode_and_nothing_is_saved`.
- The path s5 (ii) does exercise has no fake test: a mode's step-6 "In mode N, X cannot turn: SolidWorks reads it fully
  defined." (`tests/test_swbuild.py` 3346 and 3712 are without modes).
- *Change:*
  - Add the fake test for the step-6 sentence in a mode.
  - Record as a ruling that §5's status-5 clause stays fake-only, or force it on SolidWorks. Tier 11's first run made a
    lock over-define with status 5, so a lock across an engaged coupled pair, made in N's step, would do.
  - Rerun s5 at the final source.

**S4. s3's "and says so" is not asserted, and s3 and s4 ran on an app before the last three Update commits.** (should
fix; script 7020, 7083, 6950–6975; s3 log 118, 727)
- s3 logs the D10 sentence and holds none of it. The logged sentence is right: "set RangeSlv's place in N back to 56 mm,
  where it had been changed in SolidWorks, turned the mate RangeSlv engages LoDog back on in 4L, suppressed the mate
  RangeSlv engages InDog again in 4L …".
- `listed_and_left` holds the mate's name but not the quiet sentence.
- s4 logs its §1.10 sentence pieces ("moved RangeSlv in 4L to 66.5 mm along Rear", "switched the mate ModeSlv engages
  FrontDog off in 4H") and holds none.
- s3 ran at `e670e7e` and s4 at `22ba33f`, both before `a87c1c5` and `baa1a56`, which changed `_modes_assembly`. s3's
  quiet footer still has the sentence ruling 18 replaced: "since nothing needed changing" (line 727).
- *Change:* assert the three D10 pieces, the quiet "It worked in 2H … since nothing in 2H needed changing.", and s4's
  pieces. The closing run reruns both sections anyway.

**S5. The quiet press in step does not hold "every sense and value read".** (should fix; script 6705–6709, 443)
- On 2026 the quiet path is reached only in `w8_press_in_step`. It does not assert `not result.senses_unread`, which is
  logged empty at 341. Nothing shows that the slide values were read in every mode: `GetSystemValue3` is not in
  `TRACED`.
- §5's quiet Update reads "every flag, value and sense".
- *Change:* add `GetSystemValue3` to `TRACED`, assert one read per slide per mode, and assert `senses_unread` is empty.

**S6. The window stage holds no number.** (should fix; window check 652–672)
- `w8_mode_check` asserts only that the chooser reads the mode and that the panel has lines. W6's stage held its lines
  exactly (`w6_read_check`).
- The logged lines are right, for example "4L: Rear 375 rpm · Front 375 rpm · 4.000 : 1" and "N: neutral — Rear,
  FrontDrv, Idler and Front turn freely.". A wrong speed would still pass.
- The built footer is held only for being drawn whole.
- *Change:* hold each mode's first Speeds line to §2.3, and the built footer's "mated to turn in each of its 4 modes"
  sentence.

**S7. The assembly check still has the window check's hole: its log is written only at exit.** (should fix; script
526–530, 8151, 8161, 8183)
- `run` waits 2400 s, then `queue.Empty` escapes with an empty message ("section s2 raised Empty: ").
- The section's `finally` queues `close_ours` behind the hung job and raises again after 600 s, out of the loop. Main's
  `finally` quits Excel, which is right, then waits another 600 s and raises again. The STOP list, the NOTE list and the
  `done` line are skipped.
- The log reaches disk only in `__main__`'s `finally`. A run stopped by hand during that hour, as the window check was
  today, loses the log unless stdout was redirected.
- There is no infinite wait, and SolidWorks is never quit (it is the user's).
- *Change:* append each `say` line to `LOG_PATH` as it goes. In `run`, turn `queue.Empty` into a named timeout. When the
  worker is hung, skip the `close_ours` calls and say so.

## Notes

**N1. The five s7 FAILs are the flag check after a put and nothing else.** Every "wrong" set in the log is exactly
§2.3's key: `RangeSlv engages LoDog` suppressed in 2H, 4H and N; `ModeSlv engages FrontDog` in 2H and N; `RangeSlv
engages InDog` in N and 4L. `be07ebd`'s check would pass on the same reads. Nothing else in those steps failed.

**N2. The JSON is faithful, but its per-body table is wrong in 15 rows.** Ten values compared with the log all agree:
- case 1's `as_built` (8.3e-10 at Pl copy 2; ModeSlv differs in 4H, RangeSlv in N, both in 4L);
- case 2's `fits` after the drive (["shared"]);
- case 3's drive +20 in 4L (Sun +57, FIdler −7.5, LoDog +14.25 in all four);
- case 4's `put_in` (4H, N, 4L, 2H);
- case 5's FIdler (N +20, 4H +10) and FDrive (2H +2.000 axial);
- case 7's 4L value 69 and back to 66, the held `Transform2` None, the held `IsFixed` False, and fresh `IsFixed` True
  everywhere;
- every `reopened_in` and `same_as_before_save`.

`put.held` and `per_body[].during` were written by the pre-`725566e` `s7_held`, which counted a coupling that is off in
the put's mode as holding. 15 of 68 rows name one; all are no-op-put rows (for example, case 2's InDog in 4L "held by
RangeSlv engages InDog", which was in fact wholly free). No judgement reads these fields, and case 5's moving-put rows
are right. Say so beside the findings' pin, or regenerate `per_body`.

**N3. The window check's guards are sound for what hung today. The watchdog cannot see a blocked Tk thread.**
- The runner pops only a step still at the head. `report_callback_exception` ends the run. The log is written line by
  line. `finish` is idempotent.
- `watchdog` runs on `root.after`, in the Tk thread. A "do" step that blocks, such as `close_ours` through
  `in_solidworks` with `t.join(600)`, holds it for up to 10 minutes. That is bounded.
- A hang inside Tk code itself would not be caught. A `threading.Timer` that logs and calls `os._exit` would be.
- The runner change covers every stage (W4–W7 included), but only `--only w8` has run since (`w8-window-20261115-150900`).

**N4. `DialogWatch` answers No to any SOLIDWORKS CAM "Save changes to …" box, whose document it is not told.** (line
661; pre-existing) The user's documents are open and changing during runs. If the user closes one during a run, their
changes are discarded unasked. Matching the box's text against this run's titles would close the gap.

**N5. Privacy.** No user document title, licence or name appears in the reviewed logs or the JSON. Every non-run title
is anonymised. The only personal datum is the Windows account name in paths (`C:\Users\…\GearGeneratorProbe\…`), in
every log and in `w8-followup-20261115-114828.*`. It is already in 109 committed result files.

**N6. The in-step note's advice understates what the press does.** "To put the gears back there, press Update
SolidWorks with that mode showing." Since ruling 18, that press puts every mode back, the one the user turned included.
The user is not told so. This is C's to word, and a candidate for the handoff's readings.

**N7. A Halt in s2, s3 or s4 ends the run before s5, s7 and anything after.** (`start_w8_copy` 6358, `main`'s Halt
`break`) s5 builds fresh and needs no master. For the closing run, put s5 before s2, or let a missing master skip only
the copy sections.

**N8. Smaller ones.**
- s7's drive "moved nothing" and the read's self-consistency are FAIL weight, but the case goes on reading a state the
  make disturbed. Make them `S7Stop`, before `48ab0aa`'s FrontDog drive first runs.
- That drive's 4H and 4L readings of FIdler are confounded by the coupling to ModeSlv there. 2H, where the front is free
  and FIdler at 0, is the clean comparison.
- `REVIEW-FIX-TIER11` asked that a changed Update be pressed with the user's mate suppressed in every mode. s3 presses
  only quiet ones then.
- Every W8 log ends with W5's Reducer person step (`person_step`, 8051), not s6's.

---

## §5 clause by clause

"Does" means a check at the weight shown. "Differently" says how it departs and which ruling covers it. "No" means no
check. "Log" says whether the log shows the reading or only "ok".

**s2**

| §5 clause | Script | Log |
|---|---|---|
| 2H: the user's turn simulated (37°, drive deleted) | does (STOP per body, against the key) | every body's turn |
| 4H, N, 4L shown; every frame read and logged against its record | does (`w8_shown_turned`) | per-body turns, interference |
| … every other mode as built, couplings in step, no interference | differently: ruling 18 (False), every body turned as 2H (STOP); 4L's LoDog–RangeSlv clash required (stage 2c) | yes, 531.913 mm³ |
| 2H shown again stands at the 37° turn | does (STOP) | gap |
| Update in 4L, nothing changed: quiet (nothing put or shown, flags, values, senses read, frames and save flags unchanged, sentence) | differently: ruling 18 puts every mode. The quiet path is held in 2H in step (`w8_press_in_step`); senses and values not asserted (S5) | frames, flags, sentence |
| Workbook change touching every mode (At 130 → 132) → every mode shown and put, 4L last | does | shows, puts per mode, carrier first |
| … 2H's 37° turn put back too | no: in the final run every mode is already at built before the changed Update. The put-back of a turned train is exercised by the two quiet presses, judged against the record (S1) | — |
| … every mode clean in the post-check, every frame at its new wanted frame | does: `measure_modes(expected=…)`, built + 2 mm, script-made, STOP, every body of every mode | gaps |
| … the assembly left in 4L; the sentence naming every mode shown | does (regex on the names) | the sentence |
| 2024 reading of §1.9 | n/a on 2026 | — |
| (added) raw flags straight after the changed Update | does (STOP, every mate) | raw, app, reversed |
| (added) the fresh turn, read in the other modes | 4L only, as a fact; 4H and N not read (M1) | 4L per body |

**s3**

| §5 clause | Script | Log |
|---|---|---|
| 4L flags and N's value changed by the script, 2H active | does | read back |
| Update in 2H puts all three right | does (exact lists) | result fields |
| … and says so | no (S4) | the sentence logged |
| … showing nothing in the check | does (sets before the first show) | indices |
| … then shows and checks every mode | does (visited; `measure_modes(expected=built)` with controls) | yes |
| Angle mate on in N only → refuses naming it and N | does (verbatim; also "in every mode") | verbatim |
| Suppressed → listed and left | does (name in lines, footer, extra mates; flags unchanged) | lines |
| Exploded added → listed and left | does | yes |
| Exploded active → refuses before changing anything | does (J13's text, no reads, nothing changed) | yes |
| 4H deleted → NotAsBuilt, Build again… offered | does | verbatim |

**s4**

| §5 clause | Script | Log |
|---|---|---|
| L=+10.5 → 4L's value 66 → 66.5 while 2H active, no other value changed, read back in all four | does (one `SetSystemValue3` naming 4L only, before any show; key-based reads, STOP) | yes |
| … 4L in the post-check, its frames and the drive there | does | yes |
| ModeSlv At 101, 4WD=+9 → 97 in 2H and N, 4H and 4L found right | does (slid exactly those two) | yes |
| 4H's ModeSlv 4WD → 2WD (J14): 97 in 4H, coupling suppressed in 4H, read in every configuration | does | yes |
| … 4H's frames and drive, no front | does (key row = 2H's) | yes |
| Modes row 4X → structural sentence, Build again… | does ("4X" in it) | yes |
| `_r2` built with five configurations, measured | does (`modes_built` with the key extended) | yes |
| Earlier files' sha256 and mtime unchanged | does | yes |
| (sentences) | logged, not held (S4) | yes |

**s5**

| §5 clause | Script | Log |
|---|---|---|
| Doctored second distance mate on in N → "In mode N, … over-defines the assembly." | differently: refused at the gate (`W8-REVIEW-TIER11` (3), ruling 3), verbatim, no SolidWorks call | verbatim |
| Parts and layout saved and on record, no assembly, document open and named | differently: shown for (ii)'s coupling, caught at step 6 (S3) | yes |
| Footer never offers the same build | does (ii) | yes |
| Closed as m4 closes it | does | yes |
| AddMate5 status 5 in a mode, and its sentence, on SolidWorks | no (fake only, S3) | — |

**s7**

| §5 clause | Script | Log |
|---|---|---|
| In N, FIdler put 20° on a fresh handle, rebuilt | does (case 5, plain, mates on) | table |
| 4H shown: read; N again: read; FIdler put 10° in 4H; N: read | does (every configuration after every step) | tables |
| Saved, reopened, read in each | does (from the reopened file; compared, `check`) | yes |
| RangeSlv's 4L value set while 2H active, read back without activating | does, as `check`; should be a STOP (M2) | values |
| Every handle held across a show read once | does (Transform2 None, IsFixed False) | yes |
| The layout's IsFixed through fresh handles in each configuration | does (and the Ring) | yes |
| The readings set the finding; a difference §1.9 does not cover is a STOP | no (M2) | judgements logged |
| (added) H against shared and per-configuration, no-op puts, the app's Update | measured, not asserted | yes |

**window**

| §5 clause | Script | Log |
|---|---|---|
| The Speeds panel, chooser on 4L | does, but no number held (S6) | lines |
| … on N | as above | lines |
| The built footer | drawn whole only (S6) | sentences |

**§5 clauses with no check:**
- s2: "2H's 37° turn put back too" by the changed Update (no mode is turned when it runs);
- s3: "and says so";
- s5: the status-5 refusal on SolidWorks;
- s7: the finding set from the readings, with a STOP on a difference.

The window's speed and footer contents, and s3's and s4's sentences, are logged without being held.

## Judgement on s7's evidence

**What the evidence supports, each with its limit:**
- *A no-op put changes nothing.* Shown in cases 2 and 3: every body put moved 0.0, nothing else moved, and every later
  drive read as before.
- *A turn by the drive shows in every configuration on a copy no Update had moved.* Shown in cases 1–4, including a turn
  given in 4L, and one given in N after a reopen.
- *A put that moves a body stays in the configuration showing.* Shown for a single body on a fresh copy: FIdler with its
  meshes on, in N and in 4H; FDrive wholly free in 2H by the app's route. The 132348 run's whole-train put in 4L agrees.
- *It survives a save and reopen.* Shown: every reopen was read from the file, in the configuration it was saved in,
  equal to 1e-14.
- *H is ruled out.* Only as "any put, a no-op included, splits a configuration off". Every put in cases 2–4 that the
  following drive could test was a no-op.

**What the evidence does not rule out.** The configuration's history matters: a turn or a moving put may reach other
configurations differently once every configuration has been put (moving) by an Update. The s2 readings in M1 fit that
and fit neither of s7's rules. Two further readings are also open:
- a mouse drag in SolidWorks may not behave like the angle-mate drive. Every "turn" in W8 is a drive whose mate is
  deleted before the read; ruling 18's "which is what a user's turn is" is assumed, and only s6's person step can test
  it;
- s7_read_job's own shows and rebuilds may carry state between configurations. Only the active configuration's
  self-consistency is checked.

**The most valuable case still unmeasured** is M1's: on a copy, a turn, then the app's Update putting every mode, then a
turn and a moving put, with every configuration read after each step. `48ab0aa` adds the next most valuable case: same
amount or same place, when the configurations already stand differently. It has not run.

## Judgement on s2's story

**Where the expectations came from.** The final s2 is a real test of the app. Its expectations moved twice:
- to the version's finding (`08ed03a`);
- to "a quiet Update with anything to put puts every mode" (`42c393b`).

Each move follows a written ruling (§9.18 as amended by `a90a2ee` and `81aa0bb`), not the app's output. Within the
run, everything is the script's own:
- the turns come from the key;
- the crossed couplings are worked by the script (`w8_crossed`) and must equal the app's `out_of_step` exactly;
- the frames after the changed Update are built + 2 mm;
- the flags are raw.

**The status sentences.** They are held as literals in the script, and they match ruling 18's verbatim texts:
- "re-placed … in every mode";
- each crossed pair once;
- "the gears of 4L are back …";
- "It worked in 4L … then showed and checked 2H, 4H and N …";
- the in-step "The gears stand where they were turned in SolidWorks." followed by `ui_text.TURN_SHOWN_ELSEWHERE`.

The last is taken from `ui_text` itself, but its text in the log equals ruling 18's. What a user is not told is N6.

**What no longer runs.** Two readings in the stopped logs are no longer exercised:
- 132348: the quiet path's put in 4L, made before any show, stayed in 4L while 2H and N stood turned. This is the
  "moving put stays" fact for a whole mated train made by the app. s7 covers only single bodies.
- 111951 and 151412: 2H's put found in place in 4H and N. M1.

Nothing else covers the second. The final run's own second press adds to it, unread by the script.

## Judgement on s5

**What each part tests.**
- Part (i) is an honest test of the gate on the plan's doctored mate.
- Part (ii) tests the build's refusal handling in one mode, reached through step 6. It is not "the refused mate". The
  mate is made without error, and the sentence names seven bodies, among them the internal ids "Carrier carrier" and
  "Pl copy 1".

**What is shown nowhere.** §5 wanted SolidWorks's own refusal at the make: AddMate5 status 5 while a mode is shown, the
"In mode N, the mate … over-defines the assembly." sentence, and whatever balloon comes with it. That path is covered
only on the fake. The path (ii) does take has no fake test (S3).

## What the closing run must contain

- **One run from the final source**, in a fresh SolidWorks session and a fresh output folder: `--only modes` (s0, s1,
  s2, s3, s4, s5, s7), 0 failed, no STOP, with M1's added reads and case and M2's assertions in.
  - s3, s4 and s5 have no 0-failed run on the current app: s3 and s4 ran before `a87c1c5` and `baa1a56`; s5 and s7 have
    not run since `074df2c` and `be07ebd` (s7 not since `48ab0aa` either).
  - With N7 unfixed, a Halt in s2–s4 would cost s5 and s7, so put s5 before s2 or accept a second run.
- **Order hazards.** None for a fresh folder:
  - every section's folder name is unique (s0, s1, s2, s3, s4, s5, s5b, s7-1 to s7-7), and `copy_built` exits only if
    one exists already;
  - `KEY` and `S7` are reset at each section's start;
  - s2–s4 and s7 need only `s1.master` from the same run.
- **Regression.**
  - Since W7's close (`fa4e508`), swbuild's changes are on the modes path (`motion.configurations`), with two exceptions,
    both after that close: `_put_train` gained a configuration branch (`c14e1b2`) and a MateGone restore (`c48b6ef`).
  - `mate_suppression` changed for every caller. No non-modes path calls it.
  - So rerun W7's close set: r1, r2, r3, m5, m8. Add p1 then p3, the planetary put-back that runs `_put_train`.
- **The full window check**, all stages, not `--only w8`. `074df2c` changed the step runner every stage shares.

## What I could not check

- Anything on SolidWorks, including M1's alternatives. Which of (a) or (b) happened needs the reads M1 asks for.
- The pure helpers (`s7_judge`, `w8_crossed`, `moved_frames`) on synthetic inputs. I traced them by hand against the
  logged readings, which they reproduce, and ran no harness.
- `48ab0aa`'s new readings: case 5's FrontDog drive (its base plane and θ = 0 frame for a body other than the input),
  and case 7's suppressed-sense read on the copy as opened.
- Whether the 2024 run in progress is at a commit with `be07ebd` and `48ab0aa`.
- `findings.py`'s comments on the two switches, which another agent is rewriting. I judged the evidence only.
