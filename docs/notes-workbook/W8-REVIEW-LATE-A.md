# Late review of package A: `5fcaa6a`, and the remade gear mate inside a planetary's put

*Independent, 2026-11-15, read only on code.* Under review: `5fcaa6a` ("Leave a per-mode gear mate off in a carrier
train's put"), on top of `9f21d99`, which made a planetary put work by suppressing the train's gear mates and locks
around the puts (`findings.PLANETARY_PUT_ROUTE`). Also the open point that `HANDOFF-WORKBOOK.md` lists under *To pick
W8 up*, item 4: a gear mate remade inside that suppression is not read again once it is turned back on. Line numbers
are at `fb8b90d`; `swbuild.py` has not changed since `5fcaa6a`.

**Verdict.** `5fcaa6a` does what it says, and the fault it fixes is real: on `9f21d99` an E4 Update would switch every
per-mode coupling on in every mode it put. Each mode's put suppresses and restores only the gear mates on in that mode,
in the configuration shown only, and every exit path restores them. A train with no carrier makes the same calls it
always made. Three things should change, none of them a must:

- the E4 case is the first place a per-mode mate goes through the this-configuration call, which no probe has measured
  on an assembly with several configurations, and the app's own checks would not catch it leaking (point 1);
- nothing in the suite runs the E4 case end to end (point 2);
- a failure sentence on a rare W7 path is wrong (point 3).

On item 4 my recommendation is **leave it as a caveat**. The reasons are under *Item 4* below.

---

## Points

**1. Should fix: on E4, a per-mode coupling is now suppressed and turned back on with `SetSuppression2(…,
THIS_CONFIGURATION, None)`, which no probe has run on an assembly with several configurations. A leak would go unseen
by the app.** `swbuild.py:4248`, `:4907`, `:4981`; `swcom.py:2432`; `swbuild.py:4164-4177`.

- *What the code does.* `_put_train` suppresses and restores through `Session.set_mate_suppressed`. That call is
  `SetSuppression2(action, findings.THIS_CONFIGURATION = 1, None)`, read back with `IsSuppressed2(1, …)`. In
  `_modes_put`, that call reached only lock mates before `9f21d99`, and lock mates are on in every mode. If such a call
  leaked into the other configurations, suppressing a lock and then restoring it would still leave it on everywhere,
  which is correct. `5fcaa6a` passes `on_here`, so a coupling that is on in the mode shown now goes through the same
  pair of calls. Examples: `RangeSlv engages InDog` in 2H and 4H, `RangeSlv engages LoDog` in 4L, `ModeSlv engages
  FrontDog` in 4H and 4L. If the pair of calls acted beyond the active configuration, the restore would switch that
  coupling on in modes that have it off. One example: 4L's put (the last mode when 4L is active) would leave
  `RangeSlv engages LoDog` on in 2H beside `RangeSlv engages InDog`, so both dogs would be engaged and the train jammed.
- *What has been measured.* Every per-configuration flag the W8 spike and its follow-up set used
  `SetSuppression2(…, 3, names)` (`W8-SPIKE.md`; `p8_motion.py:7066`). `swThisConfiguration` is documented as the
  active configuration only, and the fake models it that way (`FakeSolidWorks.set_mate_suppressed` changes
  `mate.suppressed` only, leaving `flags` alone). So the risk is low, but it has not been shown.
- *Why the app would not see it.* Each mode is post-checked straight after its own put (`swbuild.py:4174-4177`), and
  that check reads the flags of the configuration shown only (`mate_states`). A leak from a later mode's put into a mode
  already checked is never read. The next Update's check phase would find it and D10 would put it right, but the Update
  that caused it would report success.
- *Change (either one):*
  - (a) After the mode loop, read every recorded mate with modes in every configuration with
    `mate_suppression(handle, configurations)`: `IsSuppressed2(3, names)`, measured, and it marks nothing
    (`SUPPRESSION_READ_MARKS`). Compare each flag with `on_in(_on_set(motion, m), c)`. A disagreement is a failure
    *"In mode N, the mate … is on in SolidWorks, where this mode has it off."*
  - (b) In `_put_train`, turn a per-mode gear mate off and on with `set_mate_suppressed_in(handle, flag,
    [configuration])`, the measured route, which reads its flag back.

  Option (a) also catches a leak from the lock calls. Either option changes only the calls on W8's path: with
  `gear_mates` None (W7) nothing differs, so the pinned W7 log stands. If the SolidWorks run below shows that the call
  stays local, (a) can be dropped and this point closes as a caveat.

**2. Should fix: no test runs the E4 transfer case, the only fixture with both a carrier and modes, through a changed
Update on the fake.** `tests/test_swbuild.py:6721`, `:6734`.

- *What the new tests cover.* `test_a_gear_mate_off_in_the_mode_shown_stays_off_through_a_carrier_trains_put` calls
  `_put_train` directly on W7's `Planetary_4to1`, an assembly without configurations, with a mate suppressed by hand to
  stand in for a per-mode one. It is a real test of `_put_train`'s filter. Run against `9f21d99`'s `src`, it fails
  there, though only on the new keyword.
- `test_a_modes_put_hands_the_carrier_train_only_the_gear_mates_on_in_the_mode_shown` monkeypatches `_put_train` and
  asserts the list it is handed. The motion it builds has no carrier, so on the real path that list would never be
  consulted. That test checks the wiring by replaying the implementation.
- *What no test covers.* Neither test runs `_modes_assembly`: the shows, D10 per configuration, the per-mode puts, the
  post-checks.
- *A test that does.* I wrote the test below. It passes at HEAD and fails on `9f21d99`'s `src`. There, the post-check
  gives seven *"…is on in SolidWorks, where this mode has it off"* failures, and the flags of all three couplings come
  out on in every configuration. A second test refuses the third put part-way. Its flags all come back as recorded at
  HEAD, but not on `9f21d99`. Add both to `tests/test_workbook_modes.py`, next to the E4 tests:

```python
from gear_generator import swbuild
from gear_generator.workbook import update
from test_swbuild import mode_findings  # noqa: F401
from test_workbook_modes import build_on_fake, assessed, with_gear
from workbook_fixtures import e4_transfer_case


def flags_all(sw):
    out = {}
    for m in sw.mates:
        f = dict(m.flags)
        f[sw.config] = m.suppressed
        out[m.name] = {c: f.get(c) for c in sw.configs}
    return out


def moved_spec():                     # W8-PLAN §5 s2's edit: touches every mode
    spec = e4_transfer_case()
    for g in ("FDrive", "FIdler", "FOut"):
        spec = with_gear(spec, g, at="132")
    return spec


def press(sw, record, spec):
    up = update.classify(record, assessed(spec), exists=lambda p: True)
    assert up.refusal == "" and not up.needs_new_revision, (up.refusal, up.structural)
    return up, swbuild.update_gearbox(sw, **up.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)


def test_e4_changed_update_keeps_every_flag_in_every_configuration(mode_findings):
    sw, _, record = build_on_fake(e4_transfer_case())
    before = flags_all(sw)
    sun = next(c.name for c in record.gearbox.components if c.gear == "Sun")
    sw.drive(sun, 37.0)                     # the user's turn in 2H
    up, result = press(sw, record, moved_spec())
    assert result.failures == []
    assert result.placed[0] == "Carrier carrier"          # the carrier route ran
    assert flags_all(sw) == before
    assert set(result.put_in) == {"2H", "4H", "N", "4L"}


def test_e4_put_refused_part_way_leaves_flags_as_recorded(mode_findings):
    sw, _, record = build_on_fake(e4_transfer_case())
    before = flags_all(sw)
    orig, count = sw.place_component, [0]
    def flaky(handle, rotation, at, kind=None):
        count[0] += 1
        if count[0] == 3:
            raise swbuild.SolidWorksError("refused by the test")
        return orig(handle, rotation, at, kind=kind)
    sw.place_component = flaky
    up, result = press(sw, record, moved_spec())
    assert result.failures
    assert flags_all(sw) == before
```

- *Mutants run against the fake.* (i) `gear_mates` dropped, as on `9f21d99`: caught by the post-check and by the
  flags. (ii) One gear mate never turned back on: caught by the post-check in all four modes. So the fake and the
  post-check together catch a mate left suppressed or a per-mode flag turned on in the mode shown. They do not catch a
  leak into another configuration (point 1), because the fake does not model one.

**3. Should fix (small; from `9f21d99`, on W7's path only): when a remake inside a planetary's suppressed put loses its
mate after the delete, the failure tells the user the wrong thing.** `swbuild.py:4981-4991`.

- *What happens.* `_remake` deletes the mate. If the remake then stops, `_put_train` restores and tries to turn the
  deleted mate back on. `_kept_mate` raises `MateGone`, so the result carries two sentences:
  - *"The gear mate Sun meshes Planet copy 2 is left suppressed: SolidWorks would not turn it back on (The mate … is
    not in Planetary_4to1.SLDASM any more …); press Update SolidWorks again, which turns it back on."*
  - the remake's own *"… has lost the gear mate …: … close Planetary_4to1.SLDASM in SolidWorks without saving to bring
    it back"*.

  The first sentence's advice is wrong: pressed again, Update would find the mate gone and offer *Build again…*.
- *Reproduction.* I made the fake's second `set_gear_ratio` delete and then raise, and its `set_mate_suppressed` raise
  `MateGone` for a missing mate, as `swcom` does. Throwaway script:

```python
from gear_generator import swbuild, swcom
from gear_generator.workbook import update
from test_workbook_planetary import fake_build, edited, planetary_4to1, direct

def test_lost_remake_inside_the_route():
    sw, _, record = fake_build(planetary_4to1())
    spec = edited(planetary_4to1(), shafts={"P": dict(x="19.5")},
                  gears={"Sun": dict(teeth="21"), "Ring": dict(teeth="57")})
    real_ratio, real_supp, count = sw.set_gear_ratio, sw.set_mate_suppressed, [0]
    def lossy(handle, a, b, ratio):
        count[0] += 1
        if count[0] == 2:
            old = sw.mate(sw.mate_handles[handle]); sw.mates.remove(old)
            raise swbuild.SolidWorksError(f"The open Planetary_4to1.SLDASM has lost the gear mate {old.name}: ...")
        return real_ratio(handle, a, b, ratio)
    def supp(handle, suppressed):
        name = sw.mate_handles[handle]
        if sw.mate(name) is None:
            raise swcom.MateGone(f'The mate "{name}" is not in Planetary_4to1.SLDASM any more: ...')
        return real_supp(handle, suppressed)
    sw.set_gear_ratio, sw.set_mate_suppressed = lossy, supp
    up = update.classify(record, direct(spec), exists=lambda p: True)
    result = swbuild.update_gearbox(sw, **up.update_kwargs(), exists=lambda p: True, mtime=lambda p: 5.0)
    assert any("left suppressed" in f[1] for f in result.failures)     # passes: the wrong sentence is there
```

- *Change.* In the `gear_off` loop, skip a name that `states` was read without and does not list. The mate is gone,
  and the pending exception, raised just after, says so and how to get it back. Or catch `MateGone` there without
  adding a failure. W8 never remakes (`ratios` is `[]` at `swbuild.py:4249`, ruling 9.16), so this is W7's path only.

**4. Note: what the E4 case relies on that no probe has shown.** `planetary_put_back` measured W7's `Planetary_4to1`:
one configuration, offset parallel meshes and one lock. For E4, the route also rests on the following:

- `SetSuppression2(…, 1, None)` staying in the configuration shown on an assembly with four (point 1).
- Collinear 1 : 1 gear mates (the three couplings and the `ModeSlv splined to RangeSlv` spline) among the mates
  suppressed, and turned back on after the puts. Including them is right: a coupling or spline left on ties the carrier
  to RangeSlv, ModeSlv and the front chain, which is what made route A fail. `_planetary` in the fake grows its train
  over them too. But `GEAR_MATE_BACK_ON_KEEPS_SENSE_AND_RATIO` was measured on offset meshes only. On W8's path
  `settle` is None, so nothing in `_put_train` reads a sense afterwards. The post-check does read every gear mate on in
  the mode (`swbuild.py:4318-4334`, ruling 9.16a), so a coupling turned round would be a failure naming it, never a
  silent pass.
- The route run in a configuration other than the one the assembly opened in, after a show and a rebuild, with each
  sleeve's slide distance mate on during the puts. W8 without a carrier already puts sleeves that way.
- SolidWorks 2024: the route was probed on 2026 only, and on 2024 its only evidence is p3's first step.

---

## Item 4 of *To pick W8 up*: the remade gear mate not read again

**Recommendation: leave it as a caveat. Do not read again.**

- **What the read depends on.** `Session.gear_mate_sense` judges a gear mate from its definition: `Reverse`
  (`IGearMateFeatureData`) and the directions of its two entities (`EntityParams` 3..5). Neither is a frame, and
  suppression does not edit a definition.
- **The probe evidence, SolidWorks 2026.**
  - A suppressed mate reads the same as when it is on (`SUPPRESSED_GEAR_MATE_SENSE_READ`, read twice on a reopened
    copy, with a control left on).
  - A gear mate turned off and back on keeps its `Reverse` and ratio. Route C read this in all three of its cases.
- **Why a remade mate is no different.** It is made by the same `AddMate5` call (`_gear_mate`) as a built one.
  `GEAR_MATE_BACK_ON_KEEPS_SENSE_AND_RATIO` was measured on mates the build made. Nothing distinguishes them in the
  feature.
- **The axes do not change.** In a planetary every entity direction is ±Z, and the puts turn bodies about Z, so the
  directions the read uses do not change across the puts. A remade mate's sense could differ once unsuppressed only if
  SolidWorks rewrote `Reverse` on unsuppress. None of the four reads below saw that.
- **The exact case, on 2026.** p3's third step (`probe/results/w7-put-fix-20261115-014257-p3-p4.log`, on `9f21d99`) is
  that case:
  - all four gear mates remade inside the suppression, and `Planet copy 1 meshes Ring` turned round there;
  - every mate then read by the script after the Update, with the mates on and none suppressed: *"the app reads … turning
    right"* for all four, and rule H agreeing on the raw read;
  - driven at 3.714 : 1: Sun +30°, each copy −17.5°, off by 1e-13, and the carrier at the plan's +8.0769°;
  - the half-pitch controls clash with exactly the right neighbours.

  The closing run on `08fd712` did not rerun p3, but W7's put-back call log is the same at `9f21d99` and at HEAD (the
  pinned test passes on both).
- **What reading again would cost.**
  - It changes W7's call sequence: one `gear_mate_ratio` and one sense read for each remade mate after the last
    rebuild. `test_the_w7_put_back_calls_are_pinned_whole` (142 calls and a digest) would need re-pinning.
  - Under the handoff's rules p3 would need rerunning on 2026.
  - It would buy a fifth read of something four have shown. The reads themselves mark nothing
    (`GEAR_MATE_SENSE_READ_MARKS`).
- **Where the gap really is.** On 2024, where only p3's first step ran: no remake inside the route has run there. That
  belongs in the caveat for 2024's confirming run, not in code.
- **E4 is not affected.** W8 never remakes inside a put (ruling 9.16, `ratios` `[]`), and its post-check reads every
  gear mate on in each mode shown.
- **If it is read again all the same:** in `_put_train`'s last block (`swbuild.py:5002-5013`), drop the `continue` for
  names in `ratios`, so that every name in `gear_off` goes through `gear_mate_ratio` and `settle` after the restore's
  rebuild. `settle` reads again and, if the mate is wrong, remakes it with the other Flip while the train's mates are on,
  which is W5's ordinary remake context. Expect `result.turned_round` to list a mate twice if it turns round both
  times.

---

## For the SolidWorks run of the E4 transfer case (W8-PLAN §5)

- **Point 1: s2's changed Update.** FDrive, FIdler and FOut At 130 → 132, with 4L active, so the modes are put in the
  order 2H, 4H, N, then 4L. Straight after the Update, and before anything is shown, read `IsSuppressed2(3, [2H, 4H, N,
  4L])` for each coupling. This read is already in §5 *after every Update*, and here it must be logged. The record
  wants:
  - `RangeSlv engages InDog` on in 2H and 4H only;
  - `RangeSlv engages LoDog` on in 4L only;
  - `ModeSlv engages FrontDog` on in 4H and 4L only.

  A coupling on anywhere else is the leak. Watch `RangeSlv engages LoDog` and `ModeSlv engages FrontDog` in 2H and N
  (4L's put runs last) and `RangeSlv engages InDog` in N and 4L. Also log the result's `placed`, to show the carrier
  route ran: `Carrier carrier` first in each mode.
- **Point 4: s2's post-check and a drive.** Every gear mate on in each mode should read right in the app's `ModeCheck`
  (no *"turns its gears against the way they mesh"* failure), and every frame should be at its new wanted frame in
  every configuration to 1e-6. §5 also lists the half-pitch control after every Update. I would add §5's driven proof
  in 4L and 4H after s2's Update; at present it is listed per build only. In 4L, Rear and the front at +7.5° for +30° on
  the Sun. In 4H, ModeSlv with RangeSlv at +30°. That is the reading that shows the couplings and the spline turned back
  on with their sense after the route.
- **2024:** the same s2 readings in the confirming run, the first use of the planetary route on 2024 beyond p3 (1).

---

## What I checked and found sound

- **Which configurations are touched.** Suppression is in the configuration shown only, both ways: `set_mate_suppressed`
  is `THIS_CONFIGURATION`, and the restore reads `mate_states` (`IsSuppressed2(1, …)`). In each mode, `gear_off` holds
  exactly the train's gear mates on there. These follow the record's or J14's on-set (`_on_set`). D10 (`state.flags`)
  has made the live flags match that on-set before any put. A quiet Update has no flags to fix.
- **Every exit path restores.** I traced each place a failure can happen:
  - a lock's or a gear mate's suppression (the mate is listed before the call, so it is tried on the way out);
  - the rebuild after the suppression;
  - a put;
  - turning a mate back on (a failure naming it, `_LocksLeftOff`);
  - the last rebuild (kept as a failure when something else is on its way out).

  No path leaves a mate on the list suppressed or turns on one off in the mode. My test above refused the third put on
  E4: the flags came back as recorded in every configuration, with `2H` active again.
- **Stale handles.** No handle is held across a show. Suppress, put and restore all run inside one `_modes_put`, with
  no show between them. `swbuild` holds only string handles; `Session` fetches the COM objects again on a stale epoch.
  The show and its rebuild come before `_modes_put` reads `live`.
- **Which mates count as the train's.** Couplings and splines count (`GEAR_MATE_KINDS`). Splines are kept out of
  `lock_mates` (`_real_locks`), so none is suppressed twice. Point 4 says why including them is right.
- **No-carrier trains are unchanged.** I logged every `FakeSolidWorks` call list in the suite at `c29ea2e` (before
  `9f21d99`) and at HEAD, both with HEAD's tests:
  - 470 call sequences are identical;
  - the 11 that differ are all trains with a carrier;
  - one more exists at `c29ea2e` only (`test_a_turned_planetary_is_refused_before_anything_changes_while_the_put_route_is_unset`,
    refused before any call at HEAD).

  No committed test pins this. By reading, `gear_mates` is consulted only under `if carriers:`, and `gear_off` stays
  empty without a carrier.
- **The pinned W7 log.** `test_the_w7_put_back_calls_are_pinned_whole` passes against `9f21d99`'s `src`, so the
  commit's claim that W7's put-back log is identical holds. The two new tests fail there.
- **The fake.** It models only what was probed:
  - flags per configuration;
  - a put holding in the configuration shown;
  - the 6.2° pull-back while any gear mate of a train with a carrier is on.

  It does not model `THIS_CONFIGURATION` leaking (point 1).

## What I could not check

- Anything on SolidWorks. I ran no Windows program: another agent is driving SolidWorks on this host.
- Whether `SetSuppression2(…, 1, None)` stays in the active configuration on an assembly with several configurations
  (point 1).
- The route on 2024, and with collinear gear mates.
- The COM-level fake in `test_swcom.py`. I did not exercise the route through it; the stale-handle reasoning above is
  from reading.

## Tests run

- `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_swbuild_planetary.py tests/test_workbook_planetary.py
  tests/test_probe_planetary.py tests/test_swbuild_modes.py tests/test_workbook_modes.py`: `265 passed in 1.31s`.
- `… tests/test_swbuild.py -k "planetary or carrier or put_back or mode"`: `77 passed, 376 deselected in 0.54s`.
- `… tests/test_swbuild.py tests/test_workbook_update.py tests/test_workbook_turned.py`: `607 passed in 4.47s`.
- The whole suite: `2 failed, 3067 passed, 10 skipped in 42.11s`. Both failures are `ModuleNotFoundError: No module
  named 'tkinter'` in this WSL venv (`test_gears_clutch.py::test_the_strip_never_offers_them`,
  `test_ui_text.py::test_the_end_view_readout_always_fits_and_lists_up_to_four_heights`), not this code.
- HEAD's tests against `9f21d99`'s `src` (`git archive` into a scratch folder): `2 failed, 610 passed`. The failures
  are the two new tests of `5fcaa6a`; the pinned W7 log passes.
- The scratch tests above: the E4 pair `2 passed` at HEAD and `2 failed` on `9f21d99`; the two mutants caught; the
  lost-remake script reproduces point 3.
