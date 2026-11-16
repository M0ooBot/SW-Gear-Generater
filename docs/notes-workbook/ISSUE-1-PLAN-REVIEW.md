# Issue #1 plan review (independent, before any code)

**Verdict: approve with the listed changes.** The plan's account of today's code is true. The order is right: W9a
first, W9b nearly free, W9c and W9d on the user's word. The fixture numbers check. But W9a as written does not give
the user their app back in the case they will meet first. On a gearbox with modes, any mate of theirs on any turning
gear still stops every Update that changes anything, and W9a's own definition of done writes that refusal in. Five
things must change before code:

- W9a must get past a user's mate on a gear for an ordinary rigid attachment, not refuse it;
- Update still sets back the user's edits to app-owned values, and W9a leaves that alone;
- W9d's part replacement drops the user's features in the old part from the assembly without asking;
- the reachability rule is undefined on both W8 fixtures, and the plan does not predict what it says there;
- the list of edits that still need Build again… after W9d is incomplete, and two of them are cheap with W9d's own
  calls.

**How it was checked.** I read `ISSUE-1-PLAN.md` at `7c6af8a` against the code at that commit:
`swbuild._update_motion` (4453-4783), `_modes_check` / `_modes_unknown_mates` / `_modes_assembly` / `_modes_put`
(4022-4381), `update_variables` / `planned_changes` (1323-1384), `_read_live` (2440-2500), `update.classify`, `_part`,
`_modes` and `_turning`, `gearbox.py`'s revision and reuse rules, `swcom.mate_states`, `detect_trig_units`,
`_is_mate`, `ui_text`'s Build again… question, `tests/workbook_fixtures.py`, and the macro database's
`API-LEDGER.md` (lines 220 and 602). I worked the issue's box, `RangeBox_Fixed` and both W8 fixtures by hand. I did
not run SolidWorks.

---

## Must change before implementing

**M1. W9a still stops every changing Update on a gearbox with modes once a user's mate holds any turning gear, which
is the issue's own case (§2.1 item 2, §5 W9a *Done when*, §6 Q1).**

- *Why it stops.* With modes, `_modes_assembly` sets `moved` whenever any part or layout value, slide value or Face Z
  changed (`swbuild.py:4213-4215`). `_modes_put` then puts every train in every mode (`needed = moved or …`,
  `:4346`). The trains are joined over every mode's links, and the links include the couplings (`couple_links`,
  `update.py:1400-1402`, `:1416`). So in RangeBox, Sun, the planets, the carrier, HighDog, LowDog and RangeSlv are
  **one train**. A user mate on any of them counts as "on a gear this press may move", and only the fixed Ring is
  outside. The plan itself says the rule is exact, not merely cautious: "every gear of a mated train counts as put".
- *What that means for the user.* A coupling, a motor flange or a sprocket fixed to Sun or to RangeSlv is the most
  ordinary thing anyone adds. With one, every slide-offset, face, bore or backlash press refuses. The user then
  suppresses their mates in H, N and L, presses, and turns them back on by hand, every time. That is still "I
  straight up cannot use the build app", now with one sentence instead of six. W9a's definition of done writes this
  in: *"with a user lock added on a gear, a changed Update refuses before any write"*.
- *The answer to Q1 is the wrong way round for these words.* M4 (§4) already measures what decides it. Move that
  decision into W9a and ship one of these two, chosen by M4:
  - **(a) The put carries the component.** If a put with the user's lock on moves the user's free component with the
    gear and the put holds, narrow *in the way* to a user mate that joins a put gear to something that does not move
    with it. That means the layout component, the assembly's planes, a fixed component, a gear of another train, or
    any of the user's components joined through their own mates to one of those. It is a pure graph check on M1's
    entity read plus `IsFixed`, which the app already reads. No user item is written at all.
  - **(b) It does not.** Suppress the user's mates on that train's gears in the configuration being put, around the
    put, exactly as `_put_train` does for the app's own locks. Turn them back on whatever happens, read every flag
    back (`set_mate_suppressed_in` / `mate_suppression`, both proven per configuration), and name any that comes back
    in error. The fake test is the one that exists for M8's locks: every one is back on in every configuration,
    whatever raised.

  Keep the refusal for the grounded case: a user mate tying a put gear to the housing would stop it turning anyway
  (the `_free_to_turn` post-check, `swbuild.py:1068-1083`). Rewrite §0.3's first STOP to allow (b)'s
  suppress-and-restore, with read-back, as the one permitted write. Change W9a's *Done when* to: *"with a user lock
  from a free sprocket to Sun and to RangeSlv, a value Update and a slide-offset Update go ahead, the sprocket is
  found on its gear afterwards, and every user mate is on in the modes it was on in, in no error."*
- *Not leaner:* narrowing ruling 9.18 (putting only the trains whose frames change). It rests on s2's measurement that
  a mode not put can be left turned and fail its post-check, and it would not cover the slider's train anyway.

**M2. Update still overwrites the user's edits to app-owned values, and W9a does nothing about it (§1.2 second
bullet, §1.6 "Where it does harm" (1); `swbuild.py:1323-1341`, `:1365-1384`; slide values `:4065-4072`; D10
`:4182-4190`).**

- §1.6 names this as the one real overwrite: Bore Diameter 10 → 12 in SolidWorks is set back to 10 on the next press.
  The first requirement is that no app action destroys the user's work. "Unsaved" does not save them: undoing it
  means closing without saving, which throws away everything else they did since their last save.
- The check phase already reads every global live (`_read_live` → `planned_changes`).
- *Change:* treat a value as the user's edit when its live text differs both from what the record says the file holds
  and from the workbook's new value. Tell it apart from a lost unsaved Update by the record's `unsaved` / `earlier`
  marks. For each such value, either refuse before any change, naming all of them at once with both values and the
  workbook cell (*"Bore Diameter in Gear_m1.25_N17 is 12 in SolidWorks and 10 in the workbook: type 12 in Gears!J7,
  or set it back in SolidWorks, and press Update SolidWorks again"*), or leave it and say so. Do the same for a
  slide value the user retyped and for an app mate they suppressed. Put each in K4's inventory, so the footer says
  it before the press. Choose one reading, list it in §0.2 and test it.

**M3. W9d's replacement drops the user's features in the replaced part from the assembly, and the issue's own fix
hits this (§2.1 W9d, §2.4 "giving bands to a sleeve built without them needs a new part", K6).**

- J1 leaves the fork groove to the user, so a user following the app's own advice cuts a groove into RangeSlv. The
  issue's fix then gives RangeSlv bands, and W9d replaces it: a new file goes in, the old component is deleted, and
  the groove stays only in a file the assembly no longer uses. The plan refuses the replacement for a user **mate**
  on the old component, but not for user **features** in its part, though K3's feature walk finds them.
- With a user mate on RangeSlv, the band fix is refused for good, and Build again… is the only way left.
- *Change:*
  - Refuse a replacement whose old part holds user features, naming them, as for mates. Do the same for user parts
    with in-context references to the old component, which deleting it breaks. That read is new (an external-
    references list), so measure it in M1's run.
  - For the bands, consider adding them **in place**: the band globals and the relief cut added to the built sleeve
    part. These are ops the build already makes, applied to an open part. RangeSlv then keeps its file, the user's
    groove and every mate, and W9c's "needs a new part" goes away for the one case the issue is about.
  - If replacement stays, weigh `ReplaceComponents2` with mates re-attached against delete-and-insert. It keeps the
    user's mates, but it is a call new to the app that can raise a dialog, so probe it beside P1.

**M4. The reachability rule is undefined on both W8 fixtures, and §3 does not say what it gives there (§2.2, §5 W9b
*STOP*).**

- *Undefined.* With no hub row, the hub zone is "the span its face shares in every position, which may be a single
  plane". In TransferCase_Parallel and E4, RangeSlv (At 60, face 8, ±10) spans 46…54, 56…64 and 66…74, which share
  nothing at all. ModeSlv (At 100, 0 / +10) spans 96…104 and 106…114, likewise. There is no plane to test.
- *What any sound reading gives: a true warning on both fixtures.* In Parallel, Lo is present over 25…73 (LoGear
  25…35, LoDog 67…73). It runs through the sleeve's travel, with a gear toward each end. In E4, Carrier is present
  over 15…73 (planets 15…25, LoDog 67…73). So both W8 fixtures, as built on SolidWorks, have issue #1's defect. W9b
  will warn on both, and §5's STOP ("a W8 fixture newly warned in a way §2.2–§2.3 do not predict") fires on the
  first run.
- *Change:*
  - State the rule by the points the shaft must reach. From the Z− end, O must reach at least the largest start of
    the sleeve's span over its positions (with a hub row, the hub's start). From the Z+ end, it must reach the
    smallest end. An end is blocked when another coaxial shaft P is present at that point and has a gear strictly
    between it and that end. Say whether the intervals are closed or open, and give the tolerance (`COVER_TOLERANCE`).
  - This reduces to §2.2's rule when the spans share length (the issue's −24.5), and stays certain.
  - Say whether a carrier's planets count as its gears for blocking. E4 depends on it toward Z−.
  - Pin "after W9b" answers for both W8 fixtures in §3 (reach and hub warnings), and ask the user whether W8's
    fixtures should be corrected.
  - Drop the general sentence "where a gear of shaft P sits, any other shaft present there runs inside P". It is
    false where a sleeve covers a dog, and at a sun inside its ring. The check needs only the blocking clause.

**M5. After W9d the plan leaves more edits structural than it lists, and two of them are cheap with W9d's own calls
(§2.1 W9d last sentence, §5 *Deferrable*, §6 Q2; `update.py:404-453`, `_turning`, `_modes` `:1292-1368`).**

- *Still Build again… after W9a and W9d, from the code:*
  - a gear removed;
  - a shaft added or removed;
  - Modes rows added, removed or renamed;
  - any edit that needs a coupling or sliding mesh not on record, for example a slide offset or a dog's At that now
    makes a sleeve engage a dog no mode engaged (`:1350-1359`);
  - a gear starting or stopping to slide;
  - a mated gear moved to another shaft;
  - a Z± flip;
  - a shaft starting or ceasing to stand still;
  - a shaft coordinate reaching, leaving or crossing its base plane. Every RangeBox shaft is at X = Y = 0, so moving
    any shaft off the axis is structural;
  - an anchor's face or a slide value reaching the Front plane;
  - the number of planet copies;
  - a shared part splitting;
  - a renamed app component or mate (`ComponentGone` / `MateGone` → `NotAsBuilt`, `swbuild.py:4713-4714`).
- Removing a gear uses P1's delete with app mates, and a new coupling or sliding mesh uses the mate-making with
  per-configuration flags that W9d writes anyway. Both belong in W9d.
- Finding a renamed component by its part path, when exactly one unclaimed instance carries it, is a read plus a
  pure rule. It is cheap enough for W9a. Renaming tree items is ordinary SolidWorks work.
- With those moved, "say, do not carry" (K5) is acceptable for the rest **only if** the user sees this list in §6 Q2
  and judges it.
- Offer Q2 a middle option as well: Build again… brings the user's components into the new revision at their
  last-read frames, fixed and unmated, and lists the mates to make again. That uses only `AddComponent5`, the put and
  `Fix`, which the build already calls. Re-pointing the mates stays deferred, as the plan says.

---

## Should change

**S1. K4's last sentence is ambiguous (§2.1 item 4).** *"something in the way that the record did not hold refuses
before any change, is recorded, and the next press goes ahead"* reads as if the next press goes past that mate.
Under K2 it would refuse again. Say what the next press does: it refuses again, with the footer having said so
beforehand.

**S2. Build again…'s clause comes from a record that may be stale (§2.1 item 5).** The question is decided on the Tk
thread (§1.5) from the last job's inventory, so anything the user added since that job is not named. Either have the
build job read the old assembly's user items before it builds (a read) and say them in its result, or word the clause
*"as read at 14:02"*.

**S3. User items already in error make the app's rebuild fail partway through a change (`swbuild.py:4173-4176`,
`:3368-3369`).** A user mate or component in error before the press may make `rebuild(kind=ASSEMBLY_TRAIN)` report
failure after values and flags were written, and that failure is said as the app's. The check phase already reads
every mate's error code (`mate_states`). Name the user's items in error before the press. Extend M3 from a part's
rebuild to the assembly's, with a user mate in error.

**S4. M1 should read more than four mate kinds.**
- Add distance, angle, width, limit, path and in-place mates (`_is_mate` passes anything starting "Mate").
- Add mates to a component inside a user sub-assembly: `ReferenceComponent` then gives the leaf, whose `Name2` has a
  path.
- Add mates suppressed in the active configuration but on in another mode. Whether their entities read at all is
  unknown, and K2 needs them.
- `ReferenceComponent` is verified on 2024 only (`API-LEDGER.md:602`), so 2026's read is new. Keep §0.3's
  `GetSaveFlag` STOP on it.

**S5. M3 (and S3) could raise SolidWorks' What's Wrong window.** With "show errors every rebuild" on, a rebuild that
fails on a user feature may open it. That is a dialog risk, so under the rule either probe it ahead on a scratch
part with a feature made to fail (about 5 minutes per version), or say why an API rebuild cannot raise it.

**S6. The schema steps collide and the sidecar is not versioned (§2.1 item 4, §2.4 *The record*).**
- W9a ships link record 7 with the inventory, and W9c adds band fields to the same 7. A W9a-era app would then read a
  W9c record without refusing it. Bump to 8 in W9c, or define both in W9a.
- The `.gear.json` stays at `SCHEMA_VERSION = 1` (`store.py:30`), and `GearSpec.from_dict` drops unknown keys
  silently (`spec.py:158-160`). An older app would reuse a banded sleeve as an unbanded one. Bump the sidecar schema
  for a part with bands.
- The workbook staying at Format 1 with two added columns follows W8's practice. An older app reads a banded
  `RangeBox_Fixed` as a fully toothed sleeve and refuses it on the jam, which is acceptable. Say so.

**S7. The SolidWorks estimates have 2024 faster than 2026, against what was measured (§5).** A quiet Update that put
every mode took 515 s on 2024 and 238 s on 2026 (HANDOFF line 680), and s2 took 43 minutes on 2024. W9a's "45 min on
2024", W9c's "15 min" and W9d's "1 h" should be about 1.5-2× their 2026 figures. 1 h on 2026 for W9a is believable
only if M1's demonstration (two more Updates that put every mode, about 4-9 min each) fits in it. W8 took 16 review
notes beyond its plan, so "about 23 agent runs" is more likely 30-35.

**S8. The W99 rename and "last phase" edits miss places (§0.1).**
- `design/UI-DESIGN.md:437` (*"later · phase W9"*) and `:472`.
- `ui_text.py:1015`.
- `tests/test_ui_text.py:317`.
- `tests/test_workbook_build.py:538`, `:545` and `:797`, besides `:25-29`.
- The comments at `build.py:37` and `geometry.py:228`.
- PLAN-WORKBOOK §6 needs a W9 row, not only the reworded sentence.

**S9. W9d's replacement must remake the old component's slide mate and couplings (§2.1 W9d).** Deleting RangeSlv
deletes `RangeSlv along Output` (a value per configuration) and both couplings (per-mode flags). The text only says
the *new gear* is "mated as the build mates it". Say that the replacement remakes each app mate of the old component
with its values set and read back per configuration (`set_dimension_in`), keeping the recorded names. Put it in M6.

**S10. The `_free_to_turn` post-check blames the app for the user's mate (`swbuild.py:1068-1083`).** A user mate that
fully defines a gear reads *"Sun cannot turn: SolidWorks reads it fully defined"*. Once M1's read knows the user's
mates on that gear, name them in the sentence.

**S11. §6 Q4 is missing the option that matches the carrier decision.** Offer a `hub` row that is checked (its span,
reach, band cover) but not built, a skeleton as the user chose for the carrier on 2026-11-14, beside K8's built
toothed ring. K8's argument (the teeth are specified, the fixing is not) is consistent with how J1 ruled the dog. It
overturns J1's "no hub" and says so, which is right.

---

## Notes

- **§1's claims hold.**
  - Update never deletes or saves a file. The app never calls `close_document` (only probes do).
  - `detect_trig_units` deletes only the equation it added, by its own index (`swcom.py:1248-1260`).
  - The no-modes ratio remake deletes only the app's own gear mate, by name (`MATE_DELETE_ROUTE`).
  - Every build is guarded by an existence check (`build_many`, `swbuild.py:1213-1215`; revisions in `gearbox.py`).
  - The first-mate-only refusals are as quoted (`:4593-4602`, `:4086-4100`), and so are the configuration rules
    (`:4040-4047`).
  - A tooth change with modes refuses in the check phase (`:4695-4699`).
  - The Build again… question never mentions the user's work (`ui_text.py:2174-2183`).
  - User features survive a value Update, since `update_variables` sets globals only.
- **Where the user's fear is justified:**
  - values set back (M2);
  - Build again… stranding the work: the link moves, and a part made new leaves its user features behind,
    including a part made new only because the user changed one of its globals (`record.mismatched`, `gearbox.py`
    docstring);
  - a renamed component or mate forcing Build again… (M5);
  - in future, W9d's replacement (M3).

  No path found deletes a user component, mate or feature, or rewrites a part file.
- **A dog or sleeve tooth change needs no remake.** Couplings are not in `_wanted_teeth` (`swbuild.py:3816-3827`,
  meshes only), so changing the teeth of RangeSlv, HighDog and LowDog together is a value Update today, which M1 then
  governs. A tooth change of Sun, Planet or Ring remakes a gear mate and is refused under ruling 9.16 until W9d.
- **Q2 worked through the plan as written** (RangeBox with modes; the housing mated to the layout or to nothing of
  the app's; a bore feature in a gear part):

  | Press | Sprocket mated only to the layout's Output axis or to the user's own shaft | Sprocket mated to an app gear (Sun, RangeSlv, …) |
  |---|---|---|
  | (i) slide offset | **Works** (W9a). The bore feature is kept and named if it errors | **Stops** (K2: one train, put in every mode). Works only after the user suppresses in H, N and L, then turns back on |
  | (ii) tooth count, Sun/Planet/Ring | Stops: Build again… (9.16) until W9d, then works | Stops until W9d (9.16), then stops again on K2 |
  | (ii′) tooth count, dog + sleeve | Works (a value Update) | Stops (K2) |
  | (iii) add Hub | Stops: Build again… until W9d, then works. Bands at the same time also replace RangeSlv | Stops until W9d, then stops on K2. If the mate is on RangeSlv and bands are added, it is refused for good (M3) |
  | quiet press | Works | Works (nothing to put) |

- **K9 does not newly warn on the W8 fixtures.** Their least non-engaged gap is 3 mm (RangeSlv in N to InDog and
  LoDog, and ModeSlv in 2WD to FrontDog) against c = 0.75 mm at module 1.5. It warns on the issue's box (0 mm in N)
  as §3 says.
- **§3 is right.** `RangeBox_Fixed`'s bands, relief, engagements and least gaps (10, 2.5 / 2.5, 1.0; Hub to HighDog
  1.0) and its reach all check by hand.
- **The probe list is otherwise right under the rule.** P1 (a component delete, which can raise a dialog) is the one
  probe ahead. M5, M6 and M7 are rightly left to full builds. Only S5 (What's Wrong) and M3's `ReplaceComponents2`,
  if taken, are missing.
- **The order is right.** W9b is pure and could run beside W9a. Each *Done when* is testable once M1's is rewritten
  and M4's fixture answers are pinned.
