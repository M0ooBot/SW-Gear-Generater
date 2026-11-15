# W7 spike: a gear mate whose axis rides a carrier

One question, asked before W7's packages are written around it (W7-PLAN §2.7, J5 and §2.9): how does SolidWorks
treat a gear mate when one of its two axes moves with a carrier?

The evidence is one run of probe `w7_planetary_spike` (`src/gear_generator/probe/p8_motion.py`) on SolidWorks 2026
(34.1.1), in a fresh session. It ran from a snapshot of the app as of 64f4620 with the probes as of 8cc1b79. The
result is `probe/results/w7-spike-20261114-192709.txt`, which opens with a summary, and its `.json`. Under the
testing rule of 2026-11-14 there was no 2024 run. No finding goes into `findings.py` yet: the plan commits the
finding after its demonstration.

## What was built

This is W7-PLAN §4.1's 4 : 1 planetary with the ring held: sun 18, three planets 18, ring 54 internal, module 1,
face 10, built as close to the plan's shape as is possible before W7 exists.

- **Parts.** The sun (bore 6), the planet (bore 8, one part inserted three times) and the ring were built by the
  app's own builder (`build_gearbox`, a static plan of a spec made to give exactly those three parts).
- **Layout.** A body-less layout part holds `S Axis`. The probe's layout parts take positive coordinates only, so
  the centre is at (100, 100), and every position below is shifted by that amount.
- **Carrier.** A body-less carrier part holds `C Axis` and `P1 Axis`–`P3 Axis` at the plan's copy positions:
  (18, 0), (−9, 15.588457268) and (−9, −15.588457268) from the centre. It is mated as §2.7 says: `C Axis`
  coincident with the layout's `S Axis`, and its Front plane coincident with the layout's, so it turns about the
  sun's axis. Its origin is the assembly origin rather than on its axis, which changes nothing for the mates.
- **Placement.** The sun is held on `S Axis`, with its origin 5 mm from the layout's Front. Each planet's Gear Axis
  is coincident with its carrier axis, and its origin is 5 mm from the layout's Front. The ring stays fixed.
- **Phases.** Sun 0, each planet 10°, ring 0, as §4.1 gives them. Nothing interfered as placed.
- **Drive and measurement.** A temporary angle mate on the sun, at 90° on a global, turned it +30° and back. Every
  turn below is read from the components' frames, about +Z in the fixed frame, and each planet's turn is also given
  relative to the carrier. The kinematics for +30° on the sun are: carrier +7.5°, each planet −15° (−22.5° relative
  to the carrier), ring 0.

## What each mate set did

| Gear mates (Flip as finally made) | Sun | Carrier | Each planet (relative to carrier) | Clashes driven | Verdict |
|---|---|---|---|---|---|
| **Plan (J5): sun–P1, sun–P2, sun–P3 (False); P1–ring (True after read-back)** | 30 | **7.5** | **−15 (−22.5)** | **0 on all six meshes** | **right** |
| Same, as made with Flip False everywhere (no read-back fix) | 30 | −15 | −60 (−45) | 5 on each planet–ring mesh | wrong |
| One planet: sun–P1, P1–ring (P2 and P3 left without a gear mate) | 30 | 7.5 | P1 −15 (−22.5); P2, P3 0 | P2, P3 clash | P1 right, the others free |
| §2.9 fallback: sun–carrier 18:72 (coaxial), sun–Pk 18:36, ring unmated | 30 | 7.5 | −3.75 (−11.25) | sun–Pk 2, Pk–ring 4 | **planets wrong** |
| A single sun–P1 (False): sun held by its drive, carrier driven +30, no ring mate | 0 | 30 | **P1 +60 (+30)**; P2, P3 free | — | the carrier's frame |

Every gear mate answered AddMate5 status 1, and no mate reported an error, as made, driven or set back. With the
plan's mates and the drive on, every component read fully defined. Without the drive (mounted only), the sun and
carrier read under-defined, as W5's check expects. Every frame came back to its start within 1.5e-12 mm after each
drive.

**The answer.** A gear mate turns its two gears relative to the line joining their axes: in a planetary, relative to
the carrier. It does not turn them relative to the fixed frame. With the sun held and the carrier turned 30°, a
single 18 : 18 sun–planet mate turned the planet +60° in the fixed frame, which is Willis' answer
((ω_p − ω_c)·z_p = −(ω_s − ω_c)·z_s gives +60). A fixed-frame mate would have left it still. So the plan's
tooth-ratio gear mates are the right ones: they are exactly the mesh equation in the carrier's frame (§2.5).

## The read-back on a moving axis

The app's sense rule (`decide.read_back_says_right`: Reverse beside whether the two entities point the same way)
had only been shown on fixed axes. Here it matched the drive for both kinds of mate.

- **Sun–planet mates.** With Flip False they read right and turned right.
- **Planet–ring mate, as made with Flip False.** It read wrong. Driven that way the train was wrong: carrier −15°,
  planets −60°, and 5 clashes on every planet–ring mesh.
- **Planet–ring mate, remade with Flip True.** It read right and turned right, with no clash anywhere.

So `_settle_sense` works unchanged on a planetary. The ring mate needed Flip True here, on 2026, as every toothed
ring did in `ring_mate_sense`.

## One planet against three

- **Timing.** The top-only rebuild after mating and the drive's rebuild took 0.11 s each, whether one planet or all
  three were gear-mated to the sun.
- **Constraint.** Adding P2's and P3's sun mates over-defined nothing (status 1, no error code). With only P1 mated,
  P2 and P3 stayed free to spin (under-defined) and clashed when driven.
- **Unmated ring meshes.** With the plan's set, the two planet–ring meshes left without a gear mate stayed in mesh
  when driven, with no interference. Their phase is carried by the sun mates and the carrier, as §2.7 argues.

## Save, close, reopen

The plan's set (with P1–ring at Flip True) was saved, closed and reopened.

- **On open.** Every document read GetSaveFlag False: the assembly, layout, carrier and the three parts.
- **Driven again.** The same +30° drive gave carrier +7.5° and each planet −15° (−22.5° relative to the carrier).
  No mate was in error, and every frame came back to 1.6e-11 mm.
- **After the drive.** Only the assembly read modified.

## What it means for the plan

- **J5 stands as written.** That means one sun–planet gear mate per copy at the tooth ratio, one planet–ring gear
  mate, and the other ring meshes left unmated. It turns the planetary right, with no over-definition and no extra
  solve time.
- **The ring mate must go through the read-back.** Flip False was wrong for it on 2026. §2.7's "no Flip is assumed,
  the ring mate among them" is exactly what is needed.
- **§2.9's kinematic fallback must be removed, not kept in reserve.** Gear-mating every body to the input at its
  solved absolute speed ratio turns the planets wrong (−3.75° for −15°, with clashes), because a planet's mate is
  measured relative to the carrier. The coaxial sun–carrier gear mate itself is accepted and works (carrier +7.5°).
  But it is not needed: the carrier's freedom is taken by the ring mate, as §2.7 says.
- **`train_check`'s planetary form (§2.9) is the right model.** A planet's turn relative to its carrier, judged with
  the tooth ratio k, is exactly what SolidWorks enforces.
- **Not covered by this spike:**
  - a carrier on Z−, or planets facing the other way;
  - a held sun or a held carrier (§4.2);
  - a planet axis driven by carrier globals that Update changes;
  - a put of a component whose axis is mated to another free component (`_put_train`, §2.9);
  - copies that share one part being found by Name2. The spike's three planet copies, which shared one part file,
    were found and mated without trouble.

## The run's history

The spike reached its result on the third attempt:

1. The first attempt stopped because the parts' spec wrote its output folder with a doubled backslash, so the app's
   save check refused the first part (fixed in 738a3d4).
2. The second attempt passed.
3. A last attempt added the as-made case, so the ring mate's wrong read-back could be checked against a drive
   (8cc1b79). It is the run committed.

In all, SolidWorks was open about 25 minutes.
